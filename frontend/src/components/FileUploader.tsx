"use client";

import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";

interface Props {
  label: string;
  description: string;
  onUpload: (file: File) => Promise<void>;
  accept?: Record<string, string[]>;
  icon: React.ReactNode;
}

export function FileUploader({ label, description, onUpload, icon }: Props) {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback(
    async (accepted: File[]) => {
      if (accepted.length === 0) return;
      setUploading(true);
      setError(null);
      setResult(null);
      try {
        await onUpload(accepted[0]);
        setResult(`Uploaded ${accepted[0].name}`);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Upload failed");
      } finally {
        setUploading(false);
      }
    },
    [onUpload],
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  });

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 rounded-lg bg-[#006747]/10 flex items-center justify-center text-[#006747]">
          {icon}
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">{label}</h3>
          <p className="text-sm text-gray-500">{description}</p>
        </div>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-[#006747] bg-[#006747]/5"
            : "border-gray-300 hover:border-[#006747]/50 hover:bg-gray-50"
        }`}
      >
        <input {...getInputProps()} />
        {uploading ? (
          <div className="flex flex-col items-center gap-2">
            <div className="w-8 h-8 border-2 border-[#006747] border-t-transparent rounded-full animate-spin" />
            <p className="text-sm text-gray-600">Processing...</p>
          </div>
        ) : isDragActive ? (
          <p className="text-[#006747] font-medium">Drop the PDF here</p>
        ) : (
          <div>
            <p className="text-gray-600 mb-1">Drag & drop a PDF here, or click to browse</p>
            <p className="text-xs text-gray-400">PDF only, up to 10 MB</p>
          </div>
        )}
      </div>

      {result && (
        <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-700 flex items-center gap-2">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          {result}
        </div>
      )}
      {error && (
        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
          {error}
        </div>
      )}
    </div>
  );
}
