"use client";

interface Props {
  label: string;
  value: string;
  sub?: string;
  color?: string;
}

export default function MetricCard({ label, value, sub, color = "text-slate-900" }: Props) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm card-hover">
      <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{label}</p>
      <p className={`mt-1 text-2xl font-bold ${color}`}>{value}</p>
      {sub && <p className="mt-0.5 text-xs text-slate-400">{sub}</p>}
    </div>
  );
}
