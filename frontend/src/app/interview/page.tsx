import type { Metadata } from "next";
import InterviewWorkspace from "@/components/interview/InterviewWorkspace";

export const metadata: Metadata = {
  title: "AI 视频面试",
  description: "模拟真实面试流程：智能提问、实时追问、五维雷达评价报告。",
};

export default function InterviewPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          AI 视频面试
        </h1>
        <p className="mt-1.5 text-sm text-slate-500">
          按目标岗位与产业开启一场模拟面试：面试官逐题提问，回答后实时评估并可能追问，
          结束后生成五维能力雷达图与改进建议。
        </p>
      </div>
      <InterviewWorkspace />
    </div>
  );
}
