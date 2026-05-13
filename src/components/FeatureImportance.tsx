"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";

interface Props {
  features: string[];
  values: number[];
  displayNames?: string[];
}

export default function FeatureImportance({ features, values, displayNames }: Props) {
  const data = features
    .map((f, i) => ({ feature: displayNames?.[i] ?? f, importance: values[i] }))
    .sort((a, b) => b.importance - a.importance);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-4 text-base font-semibold text-slate-800">Feature Importance Rankings</h3>
      <ResponsiveContainer width="100%" height={500}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 30, top: 5, bottom: 5 }}>
          <XAxis type="number" tick={{ fontSize: 11, fill: "#94a3b8" }} />
          <YAxis type="category" dataKey="feature" width={170} tick={{ fontSize: 11, fill: "#475569" }} />
          <Tooltip
            contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0", fontSize: 12 }}
            formatter={(val: number) => [(val * 100).toFixed(2) + "%", "Importance"]}
          />
          <Bar dataKey="importance" radius={[0, 4, 4, 0]}>
            {data.map((_, i) => (
              <Cell
                key={i}
                fill={`hsl(${260 - i * 18}, 70%, ${60 - i * 2}%)`}
                fillOpacity={0.85}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
