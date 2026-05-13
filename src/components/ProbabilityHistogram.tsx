"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";

interface Props {
  dropoutProbabilities: number[];
}

export default function ProbabilityHistogram({ dropoutProbabilities }: Props) {
  const bins = 20;
  const binWidth = 100 / bins;
  const binned = Array.from({ length: bins }, (_, i) => ({
    range: `${(i * binWidth).toFixed(0)}-${((i + 1) * binWidth).toFixed(0)}`,
    low: i * binWidth,
    high: (i + 1) * binWidth,
    count: 0,
  }));
  dropoutProbabilities.forEach((p) => {
    const idx = Math.min(Math.floor(p / binWidth), bins - 1);
    binned[idx].count++;
  });

  if (dropoutProbabilities.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center rounded-xl border border-slate-200 bg-white text-sm text-slate-400">
        No data to display
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-2 text-base font-semibold text-slate-800">Dropout Probability Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={binned} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
          <XAxis
            dataKey="range"
            tick={{ fontSize: 10, fill: "#94a3b8" }}
            interval={3}
          />
          <YAxis tick={{ fontSize: 11, fill: "#94a3b8" }} allowDecimals={false} />
          <Tooltip
            contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0", fontSize: 12 }}
            formatter={(val: number) => [`${val} students`, "Count"]}
          />
          <ReferenceLine x="30-35" stroke="#10b981" strokeDasharray="4 4" strokeWidth={2} label={{ value: "Low", position: "insideTopLeft", fontSize: 11, fill: "#10b981" }} />
          <ReferenceLine x="70-75" stroke="#ef4444" strokeDasharray="4 4" strokeWidth={2} label={{ value: "High", position: "insideTopRight", fontSize: 11, fill: "#ef4444" }} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]} fill="#818cf8" fillOpacity={0.8} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
