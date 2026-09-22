import type { ReactNode } from "react";

interface PanelProps {
  title?: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}

export default function Panel({
  title,
  description,
  action,
  children,
  className = "",
}: PanelProps) {
  return (
    <section
      className={`rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 ${className}`}
    >
      {(title || action) && (
        <div className="mb-4 flex items-start justify-between gap-3">
          <div>
            {title && (
              <h2 className="text-base font-bold text-slate-900">{title}</h2>
            )}
            {description && (
              <p className="mt-1 text-xs text-slate-500">{description}</p>
            )}
          </div>
          {action}
        </div>
      )}
      {children}
    </section>
  );
}
