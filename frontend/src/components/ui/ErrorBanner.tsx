interface ErrorBannerProps {
  message: string;
  onRetry?: () => void;
}

export default function ErrorBanner({ message, onRetry }: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className="flex flex-col gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700 sm:flex-row sm:items-center sm:justify-between"
    >
      <span>{message}</span>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="shrink-0 self-start rounded-lg border border-rose-300 px-3 py-1 text-xs font-medium text-rose-700 transition-colors hover:bg-rose-100 sm:self-auto"
        >
          重试
        </button>
      )}
    </div>
  );
}
