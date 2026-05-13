"use client";

interface Props {
  prediction: number;
  dropoutProb: number;
  graduateProb: number;
}

export default function RiskCard({ prediction, dropoutProb, graduateProb }: Props) {
  const isHigh = prediction === 1;
  const prob = isHigh ? dropoutProb : graduateProb;
  return (
    <div
      className={`animate-scale-in relative overflow-hidden rounded-2xl p-8 text-center shadow-xl ${
        isHigh
          ? "bg-gradient-to-br from-rose-500 to-pink-600"
          : "bg-gradient-to-br from-emerald-500 to-green-600"
      }`}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.15),transparent_60%)]" />
      <div className="relative">
        <p className="mb-1 text-lg font-semibold tracking-wide text-white/90">
          {isHigh ? "HIGH DROPOUT RISK" : "LOW DROPOUT RISK"}
        </p>
        <p className="text-6xl font-extrabold text-white drop-shadow-lg">
          {prob.toFixed(1)}%
        </p>
        <p className="mt-2 text-sm text-white/80">
          {isHigh
            ? "Immediate intervention and support recommended"
            : "Student is on track for successful graduation"}
        </p>
      </div>
    </div>
  );
}
