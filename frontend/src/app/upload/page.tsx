"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileUploader } from "@/components/FileUploader";
import { uploadResume, uploadLinkedIn } from "@/lib/api";
import { getSessionId, setSessionId } from "@/lib/session";

export default function UploadPage() {
  const router = useRouter();
  const [resumeReady, setResumeReady] = useState(false);
  const [linkedinReady, setLinkedinReady] = useState(false);
  const [resumeInfo, setResumeInfo] = useState<{ name: string; skills: number; experience: number } | null>(null);
  const [linkedinInfo, setLinkedinInfo] = useState<{ name: string; headline: string; skills: number } | null>(null);

  const handleResume = async (file: File) => {
    const sid = getSessionId() || undefined;
    const res = await uploadResume(file, sid);
    setSessionId(res.session_id);
    setResumeReady(true);
    setResumeInfo({
      name: res.parsed.name,
      skills: res.parsed.skills_count,
      experience: res.parsed.experience_count,
    });
  };

  const handleLinkedIn = async (file: File) => {
    const sid = getSessionId() || undefined;
    const res = await uploadLinkedIn(file, sid);
    setSessionId(res.session_id);
    setLinkedinReady(true);
    setLinkedinInfo({
      name: res.parsed.name,
      headline: res.parsed.headline,
      skills: res.parsed.skills_count,
    });
  };

  const canProceed = resumeReady || linkedinReady;

  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <div className="text-center mb-10">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Upload Your Documents</h1>
        <p className="text-gray-500">
          Upload your resume and/or LinkedIn profile PDF to get started. At least one is required.
        </p>
      </div>

      <div className="space-y-6">
        <FileUploader
          label="Resume"
          description="Upload your resume in PDF format"
          onUpload={handleResume}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          }
        />

        {resumeInfo && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-medium text-green-800">Resume Parsed Successfully</h4>
            <div className="mt-2 grid grid-cols-3 gap-4 text-sm text-green-700">
              <div><span className="font-medium">Name:</span> {resumeInfo.name}</div>
              <div><span className="font-medium">Skills:</span> {resumeInfo.skills} found</div>
              <div><span className="font-medium">Experience:</span> {resumeInfo.experience} roles</div>
            </div>
          </div>
        )}

        <FileUploader
          label="LinkedIn Profile"
          description="Export your LinkedIn profile as PDF and upload it"
          onUpload={handleLinkedIn}
          icon={
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          }
        />

        {linkedinInfo && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <h4 className="font-medium text-green-800">LinkedIn Profile Parsed</h4>
            <div className="mt-2 grid grid-cols-3 gap-4 text-sm text-green-700">
              <div><span className="font-medium">Name:</span> {linkedinInfo.name}</div>
              <div><span className="font-medium">Headline:</span> {linkedinInfo.headline}</div>
              <div><span className="font-medium">Skills:</span> {linkedinInfo.skills} found</div>
            </div>
          </div>
        )}
      </div>

      <div className="mt-8 flex justify-between items-center">
        <p className="text-sm text-gray-400">
          {canProceed ? "Ready to proceed!" : "Upload at least one document to continue"}
        </p>
        <div className="flex gap-3">
          <button
            onClick={() => router.push("/transcript")}
            disabled={!canProceed}
            className="px-6 py-2.5 bg-white border border-[#006747] text-[#006747] font-medium rounded-lg hover:bg-[#006747]/5 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Add Transcript
          </button>
          <button
            onClick={() => router.push("/dashboard")}
            disabled={!canProceed}
            className="px-6 py-2.5 bg-[#006747] text-white font-medium rounded-lg hover:bg-[#004d35] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Analyze Profile
          </button>
        </div>
      </div>
    </div>
  );
}
