import BackendStatus from "@/components/ui/BackendStatus";
import ModuleCard from "@/components/ui/ModuleCard";

const FEATURES = [
  {
    title: "多模型路由降级",
    detail: "DeepSeek / StepFun / 豆包等公有大模型 API 统一封装，按降级链自动切换，未配置 Key 时启发式兜底，保证随时可演示。",
  },
  {
    title: "工作流编排",
    detail: "面试对话核心流程由自研轻量状态机驱动：开场→提问⇄倾听→评估→追问/转场→报告，全程白名单流转。",
  },
  {
    title: "RAG 知识库",
    detail: "宁夏本地化产业知识网络（新能源、葡萄酒、枸杞/滩羊、算力），评分引用可溯源，LLM-as-Judge 三级量表。",
  },
];

export default function Home() {
  return (
    <div className="space-y-10">
      <section className="rounded-3xl bg-gradient-to-br from-slate-900 via-indigo-950 to-violet-950 px-6 py-14 text-white sm:px-12">
        <p className="text-xs font-semibold tracking-widest text-indigo-300 uppercase">
          AI AGENT 大赛参赛项目 · 宁夏本地化
        </p>
        <h1 className="mt-4 text-3xl font-bold leading-tight tracking-tight sm:text-4xl">
          用 AI 把每一次面试，
          <br className="hidden sm:block" />
          变成一次有反馈的实训
        </h1>
        <p className="mt-5 max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
          面训 AI 面向求职者（含低学历、转行、应届群体），提供「简历点评 →
          题库训练 → AI 视频面试」全链路实训。公有大模型 API 驱动，
          Serverless 云托管，打开浏览器即可开始。
        </p>
        <div className="mt-7">
          <BackendStatus />
        </div>
      </section>

      <section aria-labelledby="modules-heading">
        <h2
          id="modules-heading"
          className="text-lg font-bold text-slate-900"
        >
          三大实训模块
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          建议按顺序完成，形成「改简历 → 补知识 → 练面试」的闭环。
        </p>
        <div className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          <ModuleCard
            href="/resume"
            step="第一步"
            title="简历实训"
            description="粘贴简历原文，自动解析结构化画像，AI 逐条点评亮点与不足，并生成结合本人经历的定制面试题。"
            highlights={[
              "正则 + 规则解析联系方式/学历/技能",
              "LLM 点评：亮点、不足、关键词建议",
              "定制面试题附带考察意图与参考要点",
            ]}
            accent="indigo"
          />
          <ModuleCard
            href="/quiz"
            step="第二步"
            title="题库训练"
            description="按宁夏重点产业题库专项刷题，LLM-as-Judge 三级评分（正确/半对/错误）并给出依据，自动汇总知识点掌握度。"
            highlights={[
              "新能源 / 葡萄酒 / 特色农业 / 算力题库",
              "分学历差异化题目难度",
              "掌握度汇总，薄弱点一键回流面试训练",
            ]}
            accent="emerald"
          />
          <ModuleCard
            href="/interview"
            step="第三步"
            title="AI 视频面试"
            description="数字人面试官多轮提问，支持追问与转场，结束后生成五维雷达图评价报告与改进建议。视频不可用时自动降级语音/文字。"
            highlights={[
              "压力/常规/热身三种面试模式",
              "面试流程状态机驱动",
              "五维雷达报告 + 专项训练回流链接",
            ]}
            accent="rose"
          />
        </div>
      </section>

      <section aria-labelledby="tech-heading">
        <h2 id="tech-heading" className="text-lg font-bold text-slate-900">
          技术特色
        </h2>
        <div className="mt-5 grid gap-5 sm:grid-cols-3">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="rounded-2xl border border-slate-200 bg-white p-5"
            >
              <h3 className="text-sm font-bold text-slate-900">
                {feature.title}
              </h3>
              <p className="mt-2 text-xs leading-6 text-slate-600">
                {feature.detail}
              </p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
