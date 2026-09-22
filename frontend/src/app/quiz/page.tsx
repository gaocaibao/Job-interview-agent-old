import type { Metadata } from "next";
import QuizWorkspace from "@/components/quiz/QuizWorkspace";

export const metadata: Metadata = {
  title: "题库训练",
  description: "宁夏重点产业题库专项训练，LLM-as-Judge 三级评分与掌握度汇总。",
};

export default function QuizPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900">
          题库训练
        </h1>
        <p className="mt-1.5 text-sm text-slate-500">
          选择宁夏重点产业题库开始练习，每题提交后由 LLM-as-Judge
          给出三级评分与依据，练习结束后自动汇总知识点掌握度。
        </p>
      </div>
      <QuizWorkspace />
    </div>
  );
}
