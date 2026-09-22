"use client";

import Link from "next/link";
import { useState } from "react";
import { api } from "@/lib/api";
import type {
  EducationLevel,
  IndustryType,
  InterviewMode,
  InterviewNextAction,
  InterviewReport,
  PositionType,
} from "@/lib/types";
import ErrorBanner from "@/components/ui/ErrorBanner";
import Panel from "@/components/ui/Panel";
import SubmitButton from "@/components/ui/SubmitButton";
import RadarChart from "@/components/interview/RadarChart";

const POSITION_OPTIONS: PositionType[] = [
  "技术类",
  "销售/市场类",
  "运营类",
  "服务类",
  "生产/工程类",
  "通用",
];

const INDUSTRY_OPTIONS: IndustryType[] = [
  "新能源",
  "葡萄酒",
  "枸杞/滩羊及特色农业",
  "算力与数据",
  "文旅",
  "通用",
];

const EDUCATION_OPTIONS: EducationLevel[] = [
  "初中及以下",
  "高中/中专",
  "大专",
  "本科",
  "硕士及以上",
];

const MODE_OPTIONS: { value: InterviewMode; label: string }[] = [
  { value: "standard", label: "常规模式" },
  { value: "pressure", label: "压力面试" },
  { value: "warmup", label: "热身模式" },
];

const SELECT_CLASS =
  "mt-1 w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2.5 text-sm text-slate-900 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 focus:outline-none";

const LABEL_CLASS = "block text-xs font-medium text-slate-500";

interface Turn {
  index: number;
  question: string;
  answer: string;
}

type Phase = "setup" | "interview" | "report";

export default function InterviewWorkspace() {
  const [position, setPosition] = useState<PositionType>("技术类");
  const [industry, setIndustry] = useState<IndustryType>("新能源");
  const [educationLevel, setEducationLevel] =
    useState<EducationLevel>("本科");
  const [mode, setMode] = useState<InterviewMode>("standard");
  const [questionCount, setQuestionCount] = useState(5);

  const [phase, setPhase] = useState<Phase>("setup");
  const [sessionId, setSessionId] = useState("");
  const [current, setCurrent] = useState<InterviewNextAction | null>(null);
  const [history, setHistory] = useState<Turn[]>([]);
  const [answer, setAnswer] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [report, setReport] = useState<InterviewReport | null>(null);

  async function handleStart() {
    setBusy(true);
    setError("");
    setReport(null);
    setHistory([]);
    try {
      const session = await api.createInterviewSession({
        position,
        industry,
        education_level: educationLevel,
        mode,
        question_count: questionCount,
      });
      const action = await api.startInterview(session.session_id);
      setSessionId(session.session_id);
      setCurrent(action);
      setAnswer("");
      setPhase("interview");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "面试启动失败，请稍后重试",
      );
    } finally {
      setBusy(false);
    }
  }

  async function handleSubmit() {
    if (!current || answer.trim().length === 0) return;
    setBusy(true);
    setError("");
    try {
      const action = await api.submitAnswer(sessionId, answer.trim());
      setHistory((prev) => [
        ...prev,
        {
          index: current.turn_index,
          question: current.question,
          answer: answer.trim(),
        },
      ]);
      setAnswer("");
      if (action.action === "finish") {
        const result = await api.finishInterview(sessionId);
        setReport(result);
        setCurrent(null);
        setPhase("report");
      } else {
        setCurrent(action);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "提交失败，请稍后重试");
    } finally {
      setBusy(false);
    }
  }

  function handleRestart() {
    setPhase("setup");
    setSessionId("");
    setCurrent(null);
    setHistory([]);
    setReport(null);
    setAnswer("");
    setError("");
  }

  return (
    <div className="space-y-6">
      {error && <ErrorBanner message={error} />}

      {phase === "setup" && (
        <Panel
          title="面试设置"
          description="按目标岗位与产业定制问答，未配置大模型时使用种子题库兜底，同样可以完整体验流程"
        >
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <label>
              <span className={LABEL_CLASS}>目标岗位</span>
              <select
                value={position}
                onChange={(event) =>
                  setPosition(event.target.value as PositionType)
                }
                className={SELECT_CLASS}
              >
                {POSITION_OPTIONS.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span className={LABEL_CLASS}>目标产业</span>
              <select
                value={industry}
                onChange={(event) =>
                  setIndustry(event.target.value as IndustryType)
                }
                className={SELECT_CLASS}
              >
                {INDUSTRY_OPTIONS.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span className={LABEL_CLASS}>学历</span>
              <select
                value={educationLevel}
                onChange={(event) =>
                  setEducationLevel(event.target.value as EducationLevel)
                }
                className={SELECT_CLASS}
              >
                {EDUCATION_OPTIONS.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span className={LABEL_CLASS}>面试模式</span>
              <select
                value={mode}
                onChange={(event) =>
                  setMode(event.target.value as InterviewMode)
                }
                className={SELECT_CLASS}
              >
                {MODE_OPTIONS.map((item) => (
                  <option key={item.value} value={item.value}>
                    {item.label}
                  </option>
                ))}
              </select>
            </label>
            <label>
              <span className={LABEL_CLASS}>主问题数量</span>
              <select
                value={questionCount}
                onChange={(event) => setQuestionCount(Number(event.target.value))}
                className={SELECT_CLASS}
              >
                {[3, 5, 8, 10].map((count) => (
                  <option key={count} value={count}>
                    {count} 题
                  </option>
                ))}
              </select>
            </label>
          </div>
          <div className="mt-5">
            <SubmitButton onClick={handleStart} loading={busy}>
              {busy ? "面试官上线中…" : "开始面试"}
            </SubmitButton>
          </div>
        </Panel>
      )}

      {phase === "interview" && current && (
        <>
          <Panel
            title="面试进行中"
            description={`第 ${current.turn_index} 轮对话 · 主问题进度 ${Math.min(history.length + 1, questionCount)} / ${questionCount}`}
          >
            <div className="rounded-xl bg-indigo-50/70 p-4">
              <div className="flex items-center gap-2">
                <span
                  aria-hidden
                  className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-600 text-xs font-bold text-white"
                >
                  官
                </span>
                <span className="text-xs font-semibold text-indigo-700">
                  {current.action === "follow_up" ? "面试官追问" : "面试官提问"}
                </span>
              </div>
              <p className="mt-2 text-sm leading-6 font-medium text-slate-900">
                {current.question}
              </p>
            </div>

            <div className="mt-4">
              <textarea
                value={answer}
                onChange={(event) => setAnswer(event.target.value)}
                rows={5}
                placeholder="像真实面试一样回答，建议用 STAR 结构：情境-任务-行动-结果…"
                className="w-full rounded-xl border border-slate-300 px-3.5 py-2.5 text-sm leading-6 text-slate-900 placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 focus:outline-none"
              />
              <div className="mt-3 flex items-center gap-3">
                <SubmitButton
                  onClick={handleSubmit}
                  loading={busy}
                  disabled={answer.trim().length === 0}
                >
                  {busy ? "面试官评估中…" : "提交回答"}
                </SubmitButton>
                <span className="text-xs text-slate-400">
                  回答将实时评估，可能触发追问
                </span>
              </div>
            </div>
          </Panel>

          {history.length > 0 && (
            <Panel title="问答记录" description="本次面试已完成的问答回合">
              <ol className="space-y-4">
                {history.map((turn) => (
                  <li
                    key={turn.index}
                    className="rounded-xl border border-slate-200 p-4"
                  >
                    <p className="text-sm font-medium text-slate-900">
                      第 {turn.index} 轮 · {turn.question}
                    </p>
                    <p className="mt-1.5 text-xs leading-6 whitespace-pre-wrap text-slate-600">
                      {turn.answer}
                    </p>
                  </li>
                ))}
              </ol>
            </Panel>
          )}
        </>
      )}

      {phase === "report" && report && (
        <>
          <Panel
            title="面试评价报告"
            description={`会话 ${report.session_id.slice(0, 8)}… · 五维能力评估`}
            action={
              <SubmitButton variant="secondary" onClick={handleRestart}>
                再面一场
              </SubmitButton>
            }
          >
            <div className="grid gap-6 sm:grid-cols-2">
              <div className="flex flex-col items-center justify-center">
                <p className="text-5xl font-bold text-indigo-600">
                  {report.overall_score}
                </p>
                <p className="mt-1 text-xs text-slate-500">综合得分 / 100</p>
              </div>
              <RadarChart data={report.radar} />
            </div>
          </Panel>

          <div className="grid gap-6 sm:grid-cols-2">
            <Panel title="表现亮点">
              {report.highlights.length > 0 ? (
                <ul className="space-y-2">
                  {report.highlights.map((item) => (
                    <li
                      key={item}
                      className="rounded-xl bg-emerald-50/60 px-3.5 py-2.5 text-sm text-slate-700"
                    >
                      {item}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-400">暂无达标回合，继续加油</p>
              )}
            </Panel>
            <Panel title="薄弱环节">
              {report.weak_points.length > 0 ? (
                <ul className="space-y-2">
                  {report.weak_points.map((item) => (
                    <li
                      key={item}
                      className="rounded-xl bg-rose-50/60 px-3.5 py-2.5 text-sm text-slate-700"
                    >
                      {item}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-400">无明显薄弱回合</p>
              )}
            </Panel>
          </div>

          <Panel title="改进建议">
            <ul className="space-y-2">
              {report.suggestions.map((item) => (
                <li
                  key={item}
                  className="rounded-xl border border-slate-200 px-3.5 py-2.5 text-sm leading-6 text-slate-700"
                >
                  · {item}
                </li>
              ))}
            </ul>
            {report.retrain_links.length > 0 && (
              <div className="mt-4 border-t border-slate-100 pt-4">
                <Link
                  href="/quiz"
                  className="inline-flex items-center gap-1.5 text-sm font-semibold text-indigo-600 hover:text-indigo-500"
                >
                  前往题库模块针对性训练 →
                </Link>
              </div>
            )}
          </Panel>
        </>
      )}
    </div>
  );
}
