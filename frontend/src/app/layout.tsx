import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import SiteFooter from "@/components/layout/SiteFooter";
import SiteHeader from "@/components/layout/SiteHeader";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "面训 AI —— AI 面试实训智能体",
    template: "%s | 面训 AI",
  },
  description:
    "面向求职者的 AI 面试实训智能体：简历点评、题库训练、AI 视频面试，结合宁夏本地化产业知识库。",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="zh-CN"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col bg-slate-50 text-slate-900">
        <SiteHeader />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6 sm:py-10">
          {children}
        </main>
        <SiteFooter />
      </body>
    </html>
  );
}
