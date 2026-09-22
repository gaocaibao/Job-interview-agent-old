import type { Metadata } from "next";
import ResumeWorkspace from "@/components/resume/ResumeWorkspace";

export const metadata: Metadata = {
  title: "简历实训",
  description: "粘贴简历原文，AI 解析结构化画像并逐条点评，生成定制面试题。",
};

export default function ResumePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          简历实训
        </h1>
        <p className="mt-1.5 text-sm text-slate-500">
          粘贴简历原文（至少 20 字），先解析为结构化画像，再由 AI
          逐条点评并生成结合本人经历的定制面试题。
        </p>
      </div>
      <ResumeWorkspace />
    </div>
  );
}
