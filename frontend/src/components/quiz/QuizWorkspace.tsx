"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type {
  MasterySummary,
  QuestionBankInfo,
  QuizGradeResult,
  QuizQuestion,
} from "@/lib/types";
import ErrorBanner from "@/components/ui/ErrorBanner";
import Panel from "@/components/ui/Panel";
import SubmitButton from "@/components/ui/SubmitButton";

const LEVEL_LABEL: Record<string, { text: string; className: string }> = {
  correct: { text: "正确", className: "bg-emerald-100 text-emerald-700" },
  half_correct: {
    text: "半对",
    className: "bg-amber-100 text-amber-700",
  },
  wrong: { text: "错误", className: "bg-rose-100 text-rose-700" },
};

interface Draft {
  answer: string;
  grading: boolean;
  result: QuizGradeResult | null;
}

export default function QuizWorkspace() {
  const [banks, setBanks] = useState<QuestionBankInfo[]>([]);
  const [banksLoading, setBanksLoading] = useState(true);
  const [banksError, setBanksError] = useState("");

  const [selectedBank, setSelectedBank] = useState("");
  const [questionCount, setQuestionCount] = useState(5);
  const [questions, setQuestions] = useState<QuizQuestion[]>([]);
  const [drafts, setDrafts] = useState<Record<string, Draft>>({});
  const [summary, setSummary] = useState<MasterySummary[] | null>(null);
  const [actionError, setActionError] = useState("");

  const loadBanks = useCallback(
    () =>
      api
        .listBanks()
        .then((data) => {
          setBanks(data);
          if (data.length > 0) setSelectedBank(data[0].id);
          setBanksLoading(false);
        })
        .catch((err: unknown) => {
          setBanksError(
            err instanceof Error
              ? err.message
              : "题库加载失败，请检查后端服务",
          );
          setBanksLoading(false);
        }),
    [],
  );

  useEffect(() => {
    void loadBanks();
  }, [loadBanks]);

  function handleRetryLoadBanks() {
    setBanksLoading(true);
    setBanksError("");
    void loadBanks();
  }

  async function handleStart() {
    if (!selectedBank) return;
    setActionError("");
    setSummary(null);
    try {
      const data = await api.drawQuestions(selectedBank, questionCount);
      setQuestions(data);
      setDrafts(
        Object.fromEntries(
          data.map((question) => [
            question.id,
            { answer: "", grading: false, result: null },
          ]),
        ),
      );
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "抽题失败，请稍后重试",
      );
    }
  }

  async function handleGrade(question: QuizQuestion) {
    const draft = drafts[question.id];
    if (!draft || draft.answer.trim().length === 0) return;
    setDrafts((prev) => ({
      ...prev,
      [question.id]: { ...prev[question.id], grading: true },
    }));
    setActionError("");
    try {
      const result = await api.gradeAnswer(question.id, draft.answer.trim());
      setDrafts((prev) => ({
        ...prev,
        [question.id]: { ...prev[question.id], grading: false, result },
      }));
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "评分失败，请稍后重试",
      );
      setDrafts((prev) => ({
        ...prev,
        [question.id]: { ...prev[question.id], grading: false },
      }));
    }
  }

  async function handleSummarize() {
    const results = Object.values(drafts)
      .map((draft) => draft.result)
      .filter((result): result is QuizGradeResult => result !== null);
    if (results.length === 0) return;
    setActionError("");
    try {
      setSummary(await api.summarize(results));
    } catch (err) {
      setActionError(
        err instanceof Error ? err.message : "汇总失败，请稍后重试",
      );
    }
  }

  const gradedCount = Object.values(drafts).filter((d) => d.result).length;

  return (
    <div className="space-y-6">
      <Panel title="选择题库" description="题库内容来自宁夏本地化产业知识库">
        {banksLoading ? (
          <p className="text-sm text-slate-400">题库加载中…</p>
        ) : banksError ? (
          <ErrorBanner
            message={banksError}
            onRetry={handleRetryLoadBanks}
          />
        ) : (
          <div className="flex flex-wrap items-end gap-4">
            <label className="flex-1 min-w-56">
              <span className="block text-xs font-medium text-slate-500">
                题库
              </span>
              <select
                value={selectedBank}
                onChange={(event) => setSelectedBank(event.target.value)}
                className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 focus:outline-none"
              >
                {banks.map((bank) => (
                  <option key={bank.id} value={bank.id}>
                    {bank.title}（{bank.question_count} 题）
                  </option>
                ))}
              </select>
            </label>
            <label className="w-32">
              <span className="block text-xs font-medium text-slate-500">
                题目数量
              </span>
              <select
                value={questionCount}
                onChange={(event) => setQuestionCount(Number(event.target.value))}
                className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 focus:outline-none"
              >
                {[3, 5, 8].map((count) => (
                  <option key={count} value={count}>
                    {count} 题
                  </option>
                ))}
              </select>
            </label>
            <SubmitButton onClick={handleStart} disabled={!selectedBank}>
              开始练习
            </SubmitButton>
          </div>
        )}
      </Panel>

      {actionError && <ErrorBanner message={actionError} />}

      {questions.length > 0 && (
        <Panel
          title="练习中"
          description={`共 ${questions.length} 题 · 已评分 ${gradedCount} 题`}
          action={
            <SubmitButton
              variant="secondary"
              onClick={() => void handleSummarize()}
              disabled={gradedCount === 0}
            >
              生成掌握度汇总
            </SubmitButton>
          }
        >
          <ol className="space-y-5">
            {questions.map((question, index) => {
              const draft = drafts[question.id];
              const level = draft?.result
                ? LEVEL_LABEL[draft.result.level]
                : null;
              return (
                <li
                  key={question.id}
                  className="rounded-xl border border-slate-200 p-4"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-sm font-medium leading-6 text-slate-900">
                      {index + 1}. {question.content}
                    </p>
                    <span className="shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-[10px] text-slate-500">
                      {question.knowledge_point} · 难度 {"★".repeat(question.difficulty)}
                    </span>
                  </div>

                  {draft?.result ? (
                    <div className="mt-3 space-y-2">
                      <div className="flex items-center gap-2">
                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${level?.className ?? ""}`}
                        >
                          {level?.text ?? draft.result.level}
                        </span>
                        <span className="text-xs text-slate-500">
                          得分 {draft.result.score}
                        </span>
                      </div>
                      <p className="text-xs leading-6 text-slate-600">
                        {draft.result.reason}
                      </p>
                      {draft.result.evidence.length > 0 && (
                        <ul className="space-y-0.5">
                          {draft.result.evidence.map((item) => (
                            <li
                              key={item}
                              className="text-xs leading-5 text-slate-500"
                            >
                              · {item}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  ) : (
                    <div className="mt-3 space-y-2">
                      <textarea
                        value={draft?.answer ?? ""}
                        onChange={(event) =>
                          setDrafts((prev) => ({
                            ...prev,
                            [question.id]: {
                              ...prev[question.id],
                              answer: event.target.value,
                            },
                          }))
                        }
                        rows={3}
                        placeholder="输入你的回答…"
                        className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm leading-6 text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 focus:outline-none"
                      />
                      <SubmitButton
                        variant="secondary"
                        loading={draft?.grading}
                        disabled={!draft || draft.answer.trim().length === 0}
                        onClick={() => void handleGrade(question)}
                      >
                        {draft?.grading ? "评分中…" : "提交评分"}
                      </SubmitButton>
                    </div>
                  )}
                </li>
              );
            })}
          </ol>
        </Panel>
      )}

      {summary && (
        <Panel title="掌握度汇总" description="按知识点统计正确 / 半对 / 错误">
          <div className="space-y-3">
            {summary.map((item) => (
              <div key={item.knowledge_point}>
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-700">
                    {item.knowledge_point}
                  </span>
                  <span className="text-slate-500">
                    掌握度 {Math.round(item.mastery * 100)}% · 对 {item.correct} /
                    半对 {item.half_correct} / 错 {item.wrong}
                  </span>
                </div>
                <div
                  role="progressbar"
                  aria-valuenow={Math.round(item.mastery * 100)}
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-label={`${item.knowledge_point} 掌握度`}
                  className="mt-1.5 h-2 overflow-hidden rounded-full bg-slate-100"
                >
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-indigo-500 to-violet-500"
                    style={{ width: `${Math.round(item.mastery * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Panel>
      )}
    </div>
  );
}
