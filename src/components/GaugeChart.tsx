"use client";

interface Props {
  value: number;
  size?: number;
}

export default function GaugeChart({ value, size = 240 }: Props) {
  const radius = 90;
  const circumference = 2 * Math.PI * radius;
  const clamped = Math.min(100, Math.max(0, value));
  const offset = circumference * (1 - clamped / 100);

  const color = clamped > 70 ? "#ef4444" : clamped > 30 ? "#f59e0b" : "#10b981";

  return (
    <div className="flex flex-col items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#e2e8f0"
          strokeWidth={16}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={16}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          className="transition-all duration-700 ease-out"
        />
        <text
          x={size / 2}
          y={size / 2 - 8}
          textAnchor="middle"
          fill="#1e293b"
          fontSize={32}
          fontWeight={800}
          fontFamily="Inter, sans-serif"
        >
          {clamped.toFixed(0)}%
        </text>
        <text
          x={size / 2}
          y={size / 2 + 20}
          textAnchor="middle"
          fill="#94a3b8"
          fontSize={13}
          fontFamily="Inter, sans-serif"
        >
          Dropout Probability
        </text>
      </svg>
      <div className="mt-2 flex w-full max-w-[200px] justify-between text-xs font-medium text-slate-400">
        <span className="text-emerald-500">Safe</span>
        <span className="text-amber-500">Moderate</span>
        <span className="text-red-500">High</span>
      </div>
    </div>
  );
}
