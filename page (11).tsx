import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Navbar } from "@/components/Navbar";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "Babson Career Intelligence | MBA Career Platform",
  description:
    "AI-powered career guidance for Babson MBA students. Upload your resume, analyze your skills, and get personalized course, project, and job recommendations.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} font-sans antialiased bg-gray-50 text-gray-900`}>
        <Navbar />
        <main className="min-h-screen">{children}</main>
      </body>
    </html>
  );
}
