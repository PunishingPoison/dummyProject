"use client";

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";

interface Props {
  dropoutProbabilities: number[];
}

const COLORS = ["#10b981", "#f59e0b", "#ef4444"];
const LABELS = ["Low (<30%)", "Medium (30-70%)", "High (>70%)"];

export default function RiskDistributionPie({ dropoutProbabilities }: Props) {
  const counts = [0, 0, 0];
  dropoutProbabilities.forEach((p) => {
    if (p < 30) counts[0]++;
    else if (p <= 70) counts[1]++;
    else counts[2]++;
  });

  const data = LABELS.map((name, i) => ({ name, value: counts[i] }));

  if (data.every((d) => d.value === 0)) {
    return (
      <div className="flex h-[300px] items-center justify-center rounded-xl border border-slate-200 bg-white text-sm text-slate-400">
        No data to display
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h3 className="mb-2 text-base font-semibold text-slate-800">Risk Level Distribution</h3>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie data={data} cx="50%" cy="50%" innerRadius={55} outerRadius={90} dataKey="value" strokeWidth={2}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ borderRadius: 10, border: "1px solid #e2e8f0", fontSize: 12 }}
            formatter={(val: number, name: string) => [`${val} students`, name]}
          />
          <Legend
            verticalAlign="bottom"
            iconType="circle"
            formatter={(val: string) => (
              <span style={{ color: "#475569", fontSize: 12 }}>{val}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
