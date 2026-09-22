import Link from "next/link";
import type { ReactNode } from "react";

interface ModuleCardProps {
  href: string;
  step: string;
  title: string;
  description: string;
  highlights: string[];
  accent: "indigo" | "emerald" | "rose";
  children?: ReactNode;
}

const ACCENT_STYLES: Record<
  ModuleCardProps["accent"],
  { chip: string; ring: string; dot: string }
> = {
  indigo: {
    chip: "bg-indigo-50 text-indigo-700",
    ring: "hover:border-indigo-300",
    dot: "bg-indigo-500",
  },
  emerald: {
    chip: "bg-emerald-50 text-emerald-700",
    ring: "hover:border-emerald-300",
    dot: "bg-emerald-500",
  },
  rose: {
    chip: "bg-rose-50 text-rose-700",
    ring: "hover:border-rose-300",
    dot: "bg-rose-500",
  },
};

export default function ModuleCard({
  href,
  step,
  title,
  description,
  highlights,
  accent,
}: ModuleCardProps) {
  const style = ACCENT_STYLES[accent];

  return (
    <Link
      href={href}
      className={`group flex flex-col rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all ${style.ring} hover:shadow-md`}
    >
      <div className="flex items-center justify-between">
        <span
          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${style.chip}`}
        >
          {step}
        </span>
        <span
          aria-hidden
          className="text-slate-300 transition-transform group-hover:translate-x-1 group-hover:text-slate-500"
        >
          →
        </span>
      </div>
      <h3 className="mt-4 text-lg font-bold text-slate-900">{title}</h3>
      <p className="mt-2 flex-1 text-sm leading-6 text-slate-600">
        {description}
      </p>
      <ul className="mt-4 space-y-1.5">
        {highlights.map((item) => (
          <li
            key={item}
            className="flex items-start gap-2 text-xs text-slate-500"
          >
            <span
              aria-hidden
              className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${style.dot}`}
            />
            {item}
          </li>
        ))}
      </ul>
    </Link>
  );
}
