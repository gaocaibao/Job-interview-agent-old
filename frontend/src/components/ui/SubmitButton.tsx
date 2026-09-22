import type { ButtonHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost";

interface SubmitButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  loading?: boolean;
  children: ReactNode;
}

const VARIANT_STYLES: Record<Variant, string> = {
  primary:
    "bg-indigo-600 text-white hover:bg-indigo-500 disabled:bg-indigo-300",
  secondary:
    "border border-slate-300 bg-white text-slate-700 hover:bg-slate-50 disabled:text-slate-400",
  ghost: "text-indigo-600 hover:bg-indigo-50 disabled:text-indigo-300",
};

export default function SubmitButton({
  variant = "primary",
  loading = false,
  children,
  disabled,
  ...rest
}: SubmitButtonProps) {
  return (
    <button
      {...rest}
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-colors disabled:cursor-not-allowed ${VARIANT_STYLES[variant]}`}
    >
      {loading && (
        <span
          aria-hidden
          className="h-3.5 w-3.5 animate-spin rounded-full border-2 border-current border-t-transparent"
        />
      )}
      {children}
    </button>
  );
}
