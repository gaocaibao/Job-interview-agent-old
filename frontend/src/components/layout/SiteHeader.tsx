"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "首页" },
  { href: "/resume", label: "简历实训" },
  { href: "/quiz", label: "题库训练" },
  { href: "/interview", label: "AI 视频面试" },
];

export default function SiteHeader() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-4 sm:px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <span
            aria-hidden
            className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 text-base font-bold text-white shadow-sm"
          >
            面
          </span>
          <span className="text-lg font-bold tracking-tight text-slate-900">
            面训 AI
          </span>
        </Link>

        <nav aria-label="主导航" className="hidden items-center gap-1 sm:flex">
          {NAV_ITEMS.map((item) => {
            const active =
              item.href === "/"
                ? pathname === "/"
                : pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`rounded-lg px-3.5 py-2 text-sm font-medium transition-colors ${
                  active
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>

        <a
          href="https://bf.bifrostv.com/competition"
          target="_blank"
          rel="noopener noreferrer"
          className="rounded-full border border-slate-200 px-3.5 py-1.5 text-xs font-medium text-slate-500 transition-colors hover:border-indigo-200 hover:text-indigo-600"
        >
          AI Agent 大赛
        </a>
      </div>

      <nav
        aria-label="主导航（移动端）"
        className="flex gap-1 overflow-x-auto border-t border-slate-100 px-4 pb-2 pt-2 sm:hidden"
      >
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-current={active ? "page" : undefined}
              className={`shrink-0 rounded-lg px-3 py-1.5 text-sm font-medium ${
                active
                  ? "bg-indigo-50 text-indigo-700"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </header>
  );
}
