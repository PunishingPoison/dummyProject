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
  shapValues: number[];
  featureNames: string[];
}

export default function ShapWaterfall({ shapValues, featureNames }: Props) {
  const data = shapValues
    .map((v, i) => ({ feature: featureNames[i] ?? `F${i}`, shap: v }))
    .sort((a, b) => Math.abs(b.shap) - Math.abs(a.shap))
    .slice(0, 10)
    .reverse();

  const maxAbs = Math.max(...data.map((d) => Math.abs(d.shap)), 0.001);

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-4 text-base font-semibold text-slate-800">Top 10 Feature Impacts</h3>
      <ResponsiveContainer width="100%" height={380}>
        <BarChart data={data} layout="vertical" margin={{ left: 10, right: 30, top: 5, bottom: 5 }}>
          <XAxis type="number" domain={[-maxAbs * 1.2, maxAbs * 1.2]} tick={{ fontSize: 11, fill: "#94a3b8" }} />
          <YAxis type="category" dataKey="feature" width={160} tick={{ fontSize: 11, fill: "#475569" }} />
          <Tooltip
            contentStyle={{
              borderRadius: 10,
              border: "1px solid #e2e8f0",
              boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
              fontSize: 12,
            }}
            formatter={(val: number) => [`${val >= 0 ? "+" : ""}${val.toFixed(4)}`, "SHAP"]}
          />
          <Bar dataKey="shap" radius={[0, 4, 4, 0]}>
            {data.map((d, i) => (
              <Cell key={i} fill={d.shap >= 0 ? "#ef4444" : "#10b981"} fillOpacity={0.8} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      <div className="mt-2 flex items-center justify-center gap-6 text-xs text-slate-500">
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-sm bg-red-500/80" /> Increases risk
        </span>
        <span className="flex items-center gap-1.5">
          <span className="inline-block h-3 w-3 rounded-sm bg-emerald-500/80" /> Decreases risk
        </span>
      </div>
    </div>
  );
}
