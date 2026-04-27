"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { connectWorkday, listMockStudents } from "@/lib/api";
import { getSessionId } from "@/lib/session";

interface MockStudent {
  student_id: string;
  name: string;
  program: string;
}

export default function TranscriptPage() {
  const router = useRouter();
  const [students, setStudents] = useState<MockStudent[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const [result, setResult] = useState<{ name: string; gpa: number; courses: number; credits: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listMockStudents().then((res) => setStudents(res.students)).catch(() => {});
  }, []);

  const handleConnect = async () => {
    const sid = getSessionId();
    if (!sid) {
      setError("No session found. Please upload documents first.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await connectWorkday(sid, selected || undefined);
      setConnected(true);
      setResult({
        name: res.student.name,
        gpa: res.student.gpa,
        courses: res.student.courses_count,
        credits: res.student.credits_completed,
      });
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Connection failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Connect Transcript</h1>
        <p className="text-gray-500">
          Connect your Workday student portal to import your academic transcript automatically.
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Workday Student</h3>
            <p className="text-sm text-gray-500">Demo mode — select a mock student profile</p>
          </div>
          <span className="ml-auto px-2 py-1 bg-amber-100 text-amber-700 text-xs font-medium rounded-full">Mock</span>
        </div>

        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">Select Student Profile</label>
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-[#006747] focus:border-[#006747] text-gray-900"
          >
            <option value="">Default (Alex Chen)</option>
            {students.map((s) => (
              <option key={s.student_id} value={s.student_id}>
                {s.name} — {s.program} ({s.student_id})
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleConnect}
          disabled={loading || connected}
          className="w-full px-6 py-3 bg-[#006747] text-white font-medium rounded-lg hover:bg-[#004d35] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              Connecting...
            </span>
          ) : connected ? (
            "Connected"
          ) : (
            "Connect Workday"
          )}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">{error}</div>
        )}

        {result && (
          <div className="mt-4 bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-medium text-green-800 mb-2">Transcript Connected</h4>
            <div className="grid grid-cols-2 gap-3 text-sm text-green-700">
              <div><span className="font-medium">Student:</span> {result.name}</div>
              <div><span className="font-medium">GPA:</span> {result.gpa}</div>
              <div><span className="font-medium">Courses:</span> {result.courses}</div>
              <div><span className="font-medium">Credits:</span> {result.credits}</div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 flex justify-between">
        <button
          onClick={() => router.push("/upload")}
          className="px-6 py-2.5 text-gray-600 hover:text-gray-900 transition-colors"
        >
          Back
        </button>
        <button
          onClick={() => router.push("/dashboard")}
          className="px-6 py-2.5 bg-[#006747] text-white font-medium rounded-lg hover:bg-[#004d35] transition-colors"
        >
          Go to Dashboard
        </button>
      </div>
    </div>
  );
}
