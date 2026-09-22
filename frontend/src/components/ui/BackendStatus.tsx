"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";

type Status = "loading" | "online" | "offline";

export default function BackendStatus() {
  const [status, setStatus] = useState<Status>("loading");
  const [providers, setProviders] = useState<string[]>([]);

  useEffect(() => {
    let cancelled = false;
    api
      .llmHealth()
      .then((data) => {
        if (cancelled) return;
        setProviders(data.available_providers);
        setStatus("online");
      })
      .catch(() => {
        if (!cancelled) setStatus("offline");
      });
    return () => {
      cancelled = true;
    };
  }, []);

  if (status === "loading") {
    return (
      <p className="text-xs text-slate-400" role="status">
        正在检测后端服务状态…
      </p>
    );
  }

  if (status === "offline") {
    return (
      <p className="text-xs text-rose-600" role="status">
        后端服务未连接：请确认 API 服务已启动（本地开发默认
        localhost:8000），或配置 NEXT_PUBLIC_API_BASE_URL。
      </p>
    );
  }

  return (
    <p className="text-xs text-emerald-700" role="status">
      后端服务正常
      {providers.length > 0
        ? ` · 已接入模型：${providers.join("、")}`
        : " · 未配置模型 Key，当前使用内置种子题库与启发式评估（可演示）"}
    </p>
  );
}
