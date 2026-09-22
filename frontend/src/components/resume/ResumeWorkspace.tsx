"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type {
  ResumeProfile,
  ResumeReviewResponse,
} from "@/lib/types";
import ErrorBanner from "@/components/ui/ErrorBanner";
import Panel from "@/components/ui/Panel";
import SubmitButton from "@/components/ui/SubmitButton";

const SEVERITY_LABEL: Record<string, string> = {
  high: "重要",
  medium: "建议",
  low: "参考",
};

export default function ResumeWorkspace() {
  const [rawText, setRawText] = useState("");
  const [profile, setProfile] = useState<ResumeProfile | null>(null);
  const [review, setReview] = useState<ResumeReviewResponse | null>(null);
  const [parsing, setParsing] = useState(false);
  const [reviewing, setReviewing] = useState(false);
  const [error, setError] = useState("");

  async function handleParse() {
    setParsing(true);
    setError("");
    try {
      const result = await api.parseResume(rawText);
      setProfile(result);
      setReview(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "解析失败，请稍后重试");
    } finally {
      setParsing(false);
    }
  }

  async function handleReview() {
    if (!profile) return;
    setReviewing(true);
    setError("");
    try {
      const result = await api.reviewResume(profile, rawText);
      setReview(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "点评失败，请稍后重试");
    } finally {
      setReviewing(false);
    }
  }

  return (
    <div className="space-y-6">
      <Panel
        title="简历原文"
        description="支持直接粘贴文本；文件上传解析将在后续版本提供"
      >
        <textarea
          value={rawText}
          onChange={(event) => setRawText(event.target.value)}
          rows={10}
          placeholder="例如：张明，电话 13812345678，本科学历，3 年光伏电站运维经验，熟悉 PLC 与电气巡检……"
          className="w-full rounded-xl border border-slate-300 px-3.5 py-3 text-sm leading-6 text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 focus:outline-none"
        />
        <div className="mt-3 flex items-center gap-3">
          <SubmitButton
            onClick={handleParse}
            loading={parsing}
            disabled={rawText.trim().length < 20}
          >
            {parsing ? "解析中…" : "解析简历"}
          </SubmitButton>
          <span className="text-xs text-slate-400">
            已输入 {rawText.trim().length} 字（至少 20 字）
          </span>
        </div>
      </Panel>

      {error && <ErrorBanner message={error} />}

      {profile && (
        <Panel title="结构化画像" description="由规则引擎解析，供点评与面试定制使用">
          <dl className="grid gap-3 text-sm sm:grid-cols-2">
            <div>
              <dt className="text-xs text-slate-400">联系方式</dt>
              <dd className="mt-0.5 text-slate-800">
                {profile.phone || "未识别"} / {profile.email || "未识别"}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-400">学历</dt>
              <dd className="mt-0.5 text-slate-800">
                {profile.education_level}
              </dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-xs text-slate-400">识别到的技能关键词</dt>
              <dd className="mt-1.5 flex flex-wrap gap-1.5">
                {profile.skills.length > 0 ? (
                  profile.skills.map((skill) => (
                    <span
                      key={skill}
                      className="rounded-full bg-slate-100 px-2.5 py-1 text-xs text-slate-700"
                    >
                      {skill}
                    </span>
                  ))
                ) : (
                  <span className="text-xs text-slate-400">暂未识别到</span>
                )}
              </dd>
            </div>
          </dl>
          <div className="mt-4 border-t border-slate-100 pt-4">
            <SubmitButton
              onClick={handleReview}
              loading={reviewing}
              disabled={reviewing}
            >
              {reviewing ? "AI 点评生成中…" : "生成 AI 点评与定制面试题"}
            </SubmitButton>
          </div>
        </Panel>
      )}

      {review && (
        <>
          <Panel
            title="AI 点评"
            description={`综合得分 ${review.review.overall_score} / 100${review.provider_used ? ` · 模型：${review.provider_used}` : ""}`}
          >
            <div className="grid gap-5 sm:grid-cols-2">
              <div>
                <h3 className="text-sm font-semibold text-emerald-700">
                  亮点
                </h3>
                <ul className="mt-2 space-y-2">
                  {review.review.highlights.map((item) => (
                    <li
                      key={item.title}
                      className="rounded-xl bg-emerald-50/60 px-3.5 py-2.5"
                    >
                      <p className="text-sm font-medium text-slate-800">
                        {item.title}
                      </p>
                      <p className="mt-0.5 text-xs leading-5 text-slate-600">
                        {item.detail}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="text-sm font-semibold text-rose-700">不足</h3>
                <ul className="mt-2 space-y-2">
                  {review.review.weaknesses.map((item) => (
                    <li
                      key={item.title}
                      className="rounded-xl bg-rose-50/60 px-3.5 py-2.5"
                    >
                      <p className="text-sm font-medium text-slate-800">
                        {item.title}
                        <span className="ml-2 rounded bg-white px-1.5 py-0.5 text-[10px] font-normal text-slate-500">
                          {SEVERITY_LABEL[item.severity] ?? item.severity}
                        </span>
                      </p>
                      <p className="mt-0.5 text-xs leading-5 text-slate-600">
                        {item.detail}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            <div className="mt-5 border-t border-slate-100 pt-4">
              <h3 className="text-sm font-semibold text-slate-800">
                建议补充的关键词
              </h3>
              <div className="mt-2 flex flex-wrap gap-1.5">
                {review.review.keyword_suggestions.map((keyword) => (
                  <span
                    key={keyword}
                    className="rounded-full bg-indigo-50 px-2.5 py-1 text-xs text-indigo-700"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
              <p className="mt-4 text-xs leading-6 text-slate-600">
                <span className="font-semibold text-slate-700">模板策略：</span>
                {review.review.template_recommendation}
              </p>
            </div>
          </Panel>

          <Panel
            title="定制面试题"
            description="结合简历中的具体经历生成，可直接用于 AI 视频面试预热"
          >
            <ol className="space-y-3">
              {review.custom_questions.map((item, index) => (
                <li
                  key={item.question}
                  className="rounded-xl border border-slate-200 px-4 py-3"
                >
                  <p className="text-sm font-medium text-slate-900">
                    {index + 1}. {item.question}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">
                    考察意图：{item.intent}
                  </p>
                  <ul className="mt-1.5 space-y-0.5">
                    {item.reference_answer_points.map((point) => (
                      <li
                        key={point}
                        className="text-xs leading-5 text-slate-600"
                      >
                        · {point}
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ol>
          </Panel>
        </>
      )}
    </div>
  );
}
