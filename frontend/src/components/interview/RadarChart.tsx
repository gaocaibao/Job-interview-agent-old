import type { RadarDimension } from "@/lib/types";

interface RadarChartProps {
  data: RadarDimension[];
  size?: number;
}

/** 纯 SVG 雷达图：无额外图表依赖，按维度数自适应。 */
export default function RadarChart({ data, size = 320 }: RadarChartProps) {
  if (data.length < 3) return null;

  const cx = size / 2;
  const cy = size / 2;
  const radius = size / 2 - 52;
  const count = data.length;

  const angleOf = (index: number) =>
    (Math.PI * 2 * index) / count - Math.PI / 2;
  const pointOf = (index: number, ratio: number) => {
    const angle = angleOf(index);
    return {
      x: cx + Math.cos(angle) * radius * ratio,
      y: cy + Math.sin(angle) * radius * ratio,
    };
  };
  const toPoints = (ratio: number) =>
    data
      .map((_, index) => {
        const { x, y } = pointOf(index, ratio);
        return `${x},${y}`;
      })
      .join(" ");

  const dataPoints = data
    .map((item, index) => {
      const { x, y } = pointOf(index, Math.max(0, Math.min(100, item.score)) / 100);
      return `${x},${y}`;
    })
    .join(" ");

  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      role="img"
      aria-label={`能力雷达图：${data.map((d) => `${d.dimension} ${d.score} 分`).join("，")}`}
      className="mx-auto w-full max-w-xs"
    >
      <defs>
        <radialGradient id="radar-fill" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#6366f1" stopOpacity="0.35" />
          <stop offset="100%" stopColor="#8b5cf6" stopOpacity="0.15" />
        </radialGradient>
      </defs>

      {[0.25, 0.5, 0.75, 1].map((ratio) => (
        <polygon
          key={ratio}
          points={toPoints(ratio)}
          className="fill-none stroke-slate-200"
          strokeWidth={1}
        />
      ))}

      {data.map((item, index) => {
        const { x, y } = pointOf(index, 1);
        return (
          <line
            key={item.dimension}
            x1={cx}
            y1={cy}
            x2={x}
            y2={y}
            className="stroke-slate-200"
            strokeWidth={1}
          />
        );
      })}

      <polygon
        points={dataPoints}
        fill="url(#radar-fill)"
        className="stroke-indigo-500"
        strokeWidth={2}
        strokeLinejoin="round"
      />

      {data.map((item, index) => {
        const { x, y } = pointOf(index, Math.max(0, Math.min(100, item.score)) / 100);
        return (
          <circle
            key={item.dimension}
            cx={x}
            cy={y}
            r={3}
            className="fill-indigo-500"
          />
        );
      })}

      {data.map((item, index) => {
        const { x, y } = pointOf(index, 1);
        const labelX = cx + (x - cx) * 1.22;
        const labelY = cy + (y - cy) * 1.22;
        const anchor =
          Math.abs(labelX - cx) < 8 ? "middle" : labelX > cx ? "start" : "end";
        return (
          <text
            key={item.dimension}
            x={labelX}
            y={labelY}
            textAnchor={anchor}
            dominantBaseline="middle"
            className="fill-slate-600 text-[11px] font-medium"
          >
            {item.dimension}
            <tspan x={labelX} dy="1.15em" className="fill-slate-400 text-[10px]">
              {item.score} 分
            </tspan>
          </text>
        );
      })}
    </svg>
  );
}
