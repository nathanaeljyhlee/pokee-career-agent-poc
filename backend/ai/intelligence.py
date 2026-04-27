"""
Provider-based intelligence layer.

Offline mode uses Ollama locally. Online mode is reserved for Babson Azure and
shares the same interface so the analysis/recommendation flow does not change.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any

import httpx

from config import (
    AI_ADVISOR_TIMEOUT,
    AI_EMBED_TIMEOUT,
    AI_EXTRACTION_TIMEOUT,
    AZURE_CLIENT_ID,
    AZURE_OPENAI_DEPLOYMENT,
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
    AZURE_OPENAI_ENDPOINT,
    AZURE_TENANT_ID,
    INTELLIGENCE_MODE,
    OFFLINE_LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
    OLLAMA_EMBED_MODEL,
)
from database.connection import execute, query_one


@dataclass
class ProviderHealth:
    status: str
    detail: str = ""


class IntelligenceProvider:
    mode = "offline"
    name = "deterministic"
    chat_model: str | None = None
    embedding_model: str | None = None

    def health(self) -> ProviderHealth:
        return ProviderHealth(status="unavailable", detail="No intelligence provider configured")

    def extract_profile_evidence(self, source: str, text: str) -> list[dict[str, Any]]:
        return []

    def embed(self, texts: list[str]) -> list[list[float]]:
        return []

    def advise(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        return None

    def metadata(self, fallback_used: bool = False) -> dict[str, Any]:
        health = self.health()
        provider = self.name if health.status == "ok" and not fallback_used else "deterministic"
        return {
            "mode": self.mode,
            "provider": provider,
            "model": self.chat_model if provider != "deterministic" else None,
            "embedding_model": self.embedding_model if provider != "deterministic" else None,
            "fallback_used": fallback_used or health.status != "ok",
            "health": health.status,
            "detail": health.detail,
        }


class OllamaIntelligenceProvider(IntelligenceProvider):
    mode = "offline"
    name = "ollama"

    def __init__(self):
        self.base_url = OLLAMA_BASE_URL.rstrip("/")
        self.chat_model = OLLAMA_CHAT_MODEL
        self.embedding_model = OLLAMA_EMBED_MODEL

    def health(self) -> ProviderHealth:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=3)
            response.raise_for_status()
            models = response.json().get("models", [])
            names = {m.get("name", "").split(":")[0] for m in models}
            if self.chat_model.split(":")[0] not in names:
                return ProviderHealth("degraded", f"Ollama is running, but chat model '{self.chat_model}' is not installed")
            return ProviderHealth("ok", "Ollama is available")
        except Exception as exc:
            return ProviderHealth("unavailable", f"Ollama unavailable: {exc}")

    def extract_profile_evidence(self, source: str, text: str) -> list[dict[str, Any]]:
        if not text.strip():
            return []

        prompt = f"""Extract career-relevant skill evidence from this {source} text.
Return ONLY valid JSON with this exact shape:
{{
  "skills": [
    {{
      "skill": "canonical or concise skill name",
      "evidence_text": "short exact phrase or sentence supporting the skill",
      "source": "{source}",
      "confidence": 0.0,
      "evidence_type": "explicit"
    }}
  ]
}}

Rules:
- Use confidence from 0 to 1.
- evidence_type must be one of explicit, inferred, course_mapped.
- Do not invent facts not present in the text.
- Prefer specific business, technical, leadership, entrepreneurship, and analytics skills.

Text:
{text[:7000]}"""
        data = self._generate_json(prompt, timeout=AI_EXTRACTION_TIMEOUT)
        skills = data.get("skills", []) if isinstance(data, dict) else []
        return [_normalize_evidence_item(item, source) for item in skills if isinstance(item, dict)]

    def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        for text in texts:
            response = httpx.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.embedding_model, "prompt": text},
                timeout=AI_EMBED_TIMEOUT,
            )
            response.raise_for_status()
            embeddings.append(response.json().get("embedding", []))
        return embeddings

    def advise(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        prompt = f"""You are a Babson MBA career advisor. Use only the JSON facts below.
Return ONLY valid JSON:
{{
  "summary": "2 sentence grounded profile summary",
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "development_areas": ["area 1", "area 2", "area 3"],
  "recommended_next_steps": ["step 1", "step 2", "step 3"],
  "explanation_sources": [
    {{"type": "skill", "label": "source label"}}
  ]
}}

Facts:
{json.dumps(payload, indent=2)[:9000]}"""
        data = self._generate_json(prompt, timeout=AI_ADVISOR_TIMEOUT)
        if not isinstance(data, dict):
            return None
        return {
            "summary": str(data.get("summary", ""))[:1200],
            "strengths": _string_list(data.get("strengths"), 3),
            "development_areas": _string_list(data.get("development_areas"), 3),
            "recommended_next_steps": _string_list(data.get("recommended_next_steps"), 3),
            "explanation_sources": _source_list(data.get("explanation_sources")),
        }

    def _generate_json(self, prompt: str, timeout: float) -> dict[str, Any]:
        response_text = self._generate(prompt, timeout)
        parsed = _extract_json(response_text)
        if parsed is not None:
            return parsed

        repair_prompt = f"""Repair this model output into valid JSON only. Do not add new facts.

Output:
{response_text[:6000]}"""
        repaired = self._generate(repair_prompt, timeout)
        parsed = _extract_json(repaired)
        if parsed is None:
            raise ValueError("Ollama returned malformed JSON")
        return parsed

    def _generate(self, prompt: str, timeout: float) -> str:
        response = httpx.post(
            f"{self.base_url}/api/generate",
            json={"model": self.chat_model, "prompt": prompt, "stream": False, "format": "json"},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json().get("response", "")


class AzureIntelligenceProvider(IntelligenceProvider):
    mode = "online"
    name = "azure"

    def __init__(self):
        self.chat_model = AZURE_OPENAI_DEPLOYMENT or None
        self.embedding_model = AZURE_OPENAI_EMBEDDING_DEPLOYMENT or None

    def health(self) -> ProviderHealth:
        missing = [
            name
            for name, value in {
                "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
                "AZURE_OPENAI_DEPLOYMENT": AZURE_OPENAI_DEPLOYMENT,
                "AZURE_OPENAI_EMBEDDING_DEPLOYMENT": AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                "AZURE_TENANT_ID": AZURE_TENANT_ID,
                "AZURE_CLIENT_ID": AZURE_CLIENT_ID,
            }.items()
            if not value
        ]
        if missing:
            return ProviderHealth("unavailable", f"Azure provider not configured yet. Missing: {', '.join(missing)}")
        return ProviderHealth("degraded", "Azure provider stub is configured but not implemented yet")

    def extract_profile_evidence(self, source: str, text: str) -> list[dict[str, Any]]:
        raise RuntimeError("Azure provider not configured yet")

    def embed(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("Azure provider not configured yet")

    def advise(self, payload: dict[str, Any]) -> dict[str, Any] | None:
        raise RuntimeError("Azure provider not configured yet")


class DeterministicIntelligenceProvider(IntelligenceProvider):
    mode = "offline"
    name = "deterministic"

    def health(self) -> ProviderHealth:
        return ProviderHealth("ok", "Deterministic fallback is available")


def get_intelligence_provider() -> IntelligenceProvider:
    if INTELLIGENCE_MODE == "online":
        return AzureIntelligenceProvider()
    if INTELLIGENCE_MODE != "offline":
        return DeterministicIntelligenceProvider()
    if OFFLINE_LLM_PROVIDER == "ollama":
        return OllamaIntelligenceProvider()
    return DeterministicIntelligenceProvider()


def cache_embedding(entity_type: str, entity_id: str, provider: IntelligenceProvider, text: str, embedding: list[float]) -> None:
    model = provider.embedding_model or "none"
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    execute(
        """INSERT OR IGNORE INTO ai_embeddings
        (entity_type, entity_id, provider, model, embedding_json, content_hash)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (entity_type, entity_id, provider.name, model, json.dumps(embedding), content_hash),
    )


def get_cached_embedding(entity_type: str, entity_id: str, provider: IntelligenceProvider, text: str) -> list[float] | None:
    model = provider.embedding_model or "none"
    content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    row = query_one(
        """SELECT embedding_json FROM ai_embeddings
        WHERE entity_type = ? AND entity_id = ? AND provider = ? AND model = ? AND content_hash = ?""",
        (entity_type, entity_id, provider.name, model, content_hash),
    )
    if not row:
        return None
    return json.loads(row["embedding_json"])


def _extract_json(text: str) -> dict[str, Any] | None:
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        parsed = json.loads(match.group())
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def _normalize_evidence_item(item: dict[str, Any], source: str) -> dict[str, Any]:
    confidence = item.get("confidence", 0.5)
    try:
        confidence = max(0.0, min(1.0, float(confidence)))
    except (TypeError, ValueError):
        confidence = 0.5
    evidence_type = item.get("evidence_type") if item.get("evidence_type") in {"explicit", "inferred", "course_mapped"} else "inferred"
    return {
        "skill": str(item.get("skill", "")).strip()[:120],
        "evidence_text": str(item.get("evidence_text", "")).strip()[:500],
        "source": item.get("source") if item.get("source") in {"resume", "linkedin", "transcript"} else source,
        "confidence": confidence,
        "evidence_type": evidence_type,
    }


def _string_list(value: Any, limit: int) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item)[:300] for item in value if isinstance(item, str) and item.strip()][:limit]


def _source_list(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    sources = []
    for item in value[:8]:
        if not isinstance(item, dict):
            continue
        source_type = item.get("type")
        if source_type not in {"skill", "course", "project", "job", "transcript"}:
            source_type = "skill"
        label = str(item.get("label", "")).strip()
        if label:
            sources.append({"type": source_type, "label": label[:160]})
    return sources
