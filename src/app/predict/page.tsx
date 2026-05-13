"use client";

import { useState, useMemo, useCallback } from "react";
import Navbar from "@/components/Navbar";
import RiskCard from "@/components/RiskCard";
import MetricCard from "@/components/MetricCard";
import GaugeChart from "@/components/GaugeChart";
import ShapWaterfall from "@/components/ShapWaterfall";
import { predictSingle } from "@/lib/api";
import {
  calculateDeltas,
  calculateFinancialStress,
  ageToGroup,
  FEATURE_NAMES,
  DEFAULT_FEATURES,
  type PredictResponse,
} from "@/lib/types";
import {
  Brain,
  ArrowRight,
  BookOpen,
  User,
  DollarSign,
  AlertTriangle,
  Gauge,
  Sparkles,
  Info,
  TrendingDown,
  TrendingUp,
} from "lucide-react";

type InputMode = "smart" | "manual";
type Tab = "gauge" | "shap" | "factors";

const STEPS = [
  { icon: BookOpen, label: "Academic", desc: "Semester grades & courses" },
  { icon: User, label: "Demographics", desc: "Age, background, course" },
  { icon: DollarSign, label: "Financial", desc: "Debt, tuition, scholarship" },
  { icon: AlertTriangle, label: "Risk Factors", desc: "Absenteeism & predict" },
];

function HelpText({ children }: { children: React.ReactNode }) {
  return (
    <p className="mt-0.5 flex items-start gap-1 text-[11px] leading-tight text-slate-400">
      <Info className="mt-px h-3 w-3 shrink-0" />
      <span>{children}</span>
    </p>
  );
}

function DeltaBadge({ label, value, suffix = "", decimals = 2 }: { label: string; value: number; suffix?: string; decimals?: number }) {
  const isGood = value >= 0;
  return (
    <div className="rounded-lg border border-slate-100 bg-white p-2.5 text-center shadow-xs">
      <p className="text-[10px] font-semibold uppercase tracking-wider text-slate-400">{label}</p>
      <p className={`mt-0.5 text-sm font-bold ${isGood ? "text-emerald-600" : "text-red-500"}`}>
        {value >= 0 ? "+" : ""}{value.toFixed(decimals)}{suffix}
      </p>
      <p className="text-[10px] text-slate-400">{isGood ? "Improving" : "Declining"}</p>
    </div>
  );
}

export default function PredictPage() {
  const [mode, setMode] = useState<InputMode>("smart");
  const [step, setStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<Tab>("gauge");

  // Smart input fields
  const [s1g, setS1g] = useState(12.5);
  const [s1a, setS1a] = useState(5);
  const [s1e, setS1e] = useState(6);
  const [s2g, setS2g] = useState(11.8);
  const [s2a, setS2a] = useState(4);
  const [s2e, setS2e] = useState(6);
  const [absent, setAbsent] = useState(0.25);
  const [age, setAge] = useState(20);
  const [admission, setAdmission] = useState(125);
  const [unemployment, setUnemployment] = useState(10.5);
  const [prevQual, setPrevQual] = useState(1);
  const [course, setCourse] = useState(9238);
  const [attendance, setAttendance] = useState(1);
  const [isDebtor, setIsDebtor] = useState(0);
  const [tuitionUpToDate, setTuitionUpToDate] = useState(1);
  const [hasScholarship, setHasScholarship] = useState(0);

  const [manualVals, setManualVals] = useState<number[]>([...DEFAULT_FEATURES]);

  const handleManualChange = useCallback((i: number, val: number) => {
    setManualVals((prev) => {
      const next = [...prev];
      next[i] = val;
      return next;
    });
  }, []);

  const deltas = useMemo(
    () => calculateDeltas(s1g, s1a, s1e, s2g, s2a, s2e),
    [s1g, s1a, s1e, s2g, s2a, s2e]
  );
  const financialStress = useMemo(
    () => calculateFinancialStress(isDebtor, tuitionUpToDate, hasScholarship),
    [isDebtor, tuitionUpToDate, hasScholarship]
  );
  const ageGroup = useMemo(() => ageToGroup(age), [age]);

  const buildFeatures = useCallback((): number[] => {
    return [s1g, s1a, s2g, s2a, deltas.gradeDelta, deltas.approvedDelta, deltas.efficiencyChange, absent, financialStress, ageGroup, admission, unemployment, prevQual, course, attendance];
  }, [s1g, s1a, s2g, s2a, deltas, absent, financialStress, ageGroup, admission, unemployment, prevQual, course, attendance]);

  const handlePredict = useCallback(async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const features = mode === "smart" ? buildFeatures() : manualVals;
      const res = await predictSingle(features);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Prediction failed");
    } finally {
      setLoading(false);
    }
  }, [mode, buildFeatures, manualVals]);

  const { gradeDelta, approvedDelta, efficiencyChange } = deltas;
  const AGE_LABELS = ["17\u201320", "21\u201325", "26+"];

  const absentMeta = useMemo(() => {
    const label = absent <= 0.15 ? "Excellent" : absent <= 0.35 ? "Good" : absent <= 0.55 ? "Moderate" : absent <= 0.75 ? "Concerning" : "Severe";
    const color = absent <= 0.15 ? "text-emerald-600" : absent <= 0.35 ? "text-blue-600" : absent <= 0.55 ? "text-amber-500" : absent <= 0.75 ? "text-orange-500" : "text-red-500";
    return { label, color };
  }, [absent]);
  const absentLabel = absentMeta.label;
  const absentColor = absentMeta.color;

  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Individual Risk Assessment</h1>
          <p className="mt-1 text-slate-500">Enter student details below and get an instant AI-powered dropout risk prediction with explanations.</p>
        </div>

        {/* Mode Toggle */}
        <div className="mb-6 flex gap-2 rounded-xl border border-slate-200 bg-white p-1.5 shadow-sm">
          {(["smart", "manual"] as const).map((m) => (
            <button
              key={m}
              onClick={() => { setMode(m); setResult(null); }}
              className={`flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                mode === m ? "bg-indigo-600 text-white shadow-sm" : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {m === "smart" ? (
                <><TrendingUp className="h-4 w-4" /> Smart Input — auto-calculated trends</>
              ) : (
                <><Gauge className="h-4 w-4" /> Manual Input — enter all 15 features directly</>
              )}
            </button>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-[1.3fr_1fr]">
          {/* Left: Form */}
          <div className="space-y-5">
            {mode === "smart" ? (
              <div className="rounded-xl border border-slate-200 bg-white shadow-sm">
                {/* Step Indicator */}
                <div className="border-b border-slate-100 px-5 pt-4 pb-3">
                  <div className="flex items-center justify-between">
                    {STEPS.map((s, i) => {
                      const Icon = s.icon;
                      const isActive = step === i;
                      const isDone = i < step;
                      return (
                        <button
                          key={i}
                          onClick={() => setStep(i)}
                          className={`flex flex-col items-center gap-1 transition-all ${
                            isActive ? "opacity-100" : "opacity-50 hover:opacity-80"
                          }`}
                        >
                          <div className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold transition-all ${
                            isActive
                              ? "bg-indigo-600 text-white shadow-sm shadow-indigo-300 scale-110"
                              : isDone
                              ? "bg-emerald-100 text-emerald-700"
                              : "bg-slate-100 text-slate-400"
                          }`}>
                            {isDone ? "✓" : i + 1}
                          </div>
                          <span className={`text-[10px] font-semibold uppercase tracking-wider ${
                            isActive ? "text-indigo-700" : "text-slate-400"
                          }`}>{s.label}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Slider */}
                <div className="overflow-hidden">
                  <div
                    className="flex transition-transform duration-150 ease-out"
                    style={{ transform: `translateX(-${step * 100}%)` }}
                  >
                    {/* Slide 0: Academic */}
                    <div className="w-full shrink-0 p-5">
                      <div className="mb-4 flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                          <BookOpen className="h-4 w-4" />
                        </div>
                        <div>
                          <h2 className="text-base font-semibold text-slate-800">Academic Performance</h2>
                          <p className="text-xs text-slate-400">Enter grades and course counts for both semesters. Deltas are auto-calculated.</p>
                        </div>
                      </div>

                      <div className="grid gap-6 sm:grid-cols-2">
                        <div className="rounded-lg border border-sky-100 bg-sky-50/40 p-4">
                          <p className="mb-3 text-xs font-bold uppercase tracking-wider text-sky-700">First Semester</p>
                          <div className="space-y-3">
                            <div>
                              <label className="block text-xs font-semibold text-slate-700">Average Grade</label>
                              <input type="number" value={s1g} onChange={(e) => setS1g(+e.target.value)} step={0.1} min={0} max={20}
                                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                              <HelpText>Typical passing grade is ~10/20. Higher = better.</HelpText>
                            </div>
                            <div>
                              <label className="block text-xs font-semibold text-slate-700">Courses Approved</label>
                              <input type="number" value={s1a} onChange={(e) => setS1a(+e.target.value)} min={0} max={30}
                                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                              <HelpText>Number of courses the student passed. Must be ≤ enrolled.</HelpText>
                            </div>
                            <div>
                              <label className="block text-xs font-semibold text-slate-700">Courses Enrolled</label>
                              <input type="number" value={s1e} onChange={(e) => setS1e(+e.target.value)} min={0} max={30}
                                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                              <HelpText>Total courses the student registered for.</HelpText>
                            </div>
                          </div>
                        </div>

                        <div className="rounded-lg border border-emerald-100 bg-emerald-50/40 p-4">
                          <p className="mb-3 text-xs font-bold uppercase tracking-wider text-emerald-700">Second Semester</p>
                          <div className="space-y-3">
                            <div>
                              <label className="block text-xs font-semibold text-slate-700">Average Grade</label>
                              <input type="number" value={s2g} onChange={(e) => setS2g(+e.target.value)} step={0.1} min={0} max={20}
                                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                              <HelpText>Compare to semester 1 — improving or declining?</HelpText>
                            </div>
                            <div>
                              <label className="block text-xs font-semibold text-slate-700">Courses Approved</label>
                              <input type="number" value={s2a} onChange={(e) => setS2a(+e.target.value)} min={0} max={30}
                                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                              <HelpText>Number of courses passed in semester 2.</HelpText>
                            </div>
                            <div>
                              <label className="block text-xs font-semibold text-slate-700">Courses Enrolled</label>
                              <input type="number" value={s2e} onChange={(e) => setS2e(+e.target.value)} min={0} max={30}
                                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                              <HelpText>Total courses enrolled in semester 2.</HelpText>
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="mt-4">
                        <p className="mb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Auto-Calculated Performance Trends</p>
                        <div className="grid grid-cols-3 gap-3">
                          <DeltaBadge label="Grade Delta" value={gradeDelta} />
                          <DeltaBadge label="Approved Delta" value={approvedDelta} decimals={0} />
                          <DeltaBadge label="Efficiency Delta" value={efficiencyChange} decimals={3} />
                        </div>
                        <p className="mt-1.5 text-[11px] text-slate-400">Automatically computed from your entries. Positive = improving, negative = declining.</p>
                      </div>
                    </div>

                    {/* Slide 1: Demographics */}
                    <div className="w-full shrink-0 p-5">
                      <div className="mb-4 flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                          <User className="h-4 w-4" />
                        </div>
                        <div>
                          <h2 className="text-base font-semibold text-slate-800">Demographics &amp; Background</h2>
                          <p className="text-xs text-slate-400">Personal and academic background factors that influence risk.</p>
                        </div>
                      </div>

                      <div className="grid gap-4 sm:grid-cols-2">
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Age</label>
                          <input type="number" value={age} onChange={(e) => setAge(+e.target.value)} min={17} max={70}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                          <div className="mt-1 flex items-center gap-2">
                            <span className="inline-block rounded bg-indigo-100 px-2 py-0.5 text-[11px] font-medium text-indigo-700">Age group: {AGE_LABELS[ageGroup]}</span>
                            <span className="text-[11px] text-slate-400">Mature students may face higher risk.</span>
                          </div>
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Admission Grade</label>
                          <input type="number" value={admission} onChange={(e) => setAdmission(+e.target.value)} min={0} max={200} step={1}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                          <HelpText>Score on university entry exam (0–200). Higher = stronger foundation.</HelpText>
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Regional Unemployment Rate (%)</label>
                          <input type="number" value={unemployment} onChange={(e) => setUnemployment(+e.target.value)} min={0} max={30} step={0.5}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                          <HelpText>Unemployment rate in the student&apos;s region. Higher economic stress can increase dropout risk.</HelpText>
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Previous Qualification</label>
                          <input type="number" value={prevQual} onChange={(e) => setPrevQual(+e.target.value)} min={0} max={20}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                          <HelpText>Code representing the type of prior education completed (e.g., high school track).</HelpText>
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Course Code</label>
                          <input type="number" value={course} onChange={(e) => setCourse(+e.target.value)} min={0} max={10000}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                          <HelpText>Identifier for the enrolled program. Some courses have higher dropout rates.</HelpText>
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Attendance Schedule</label>
                          <select value={attendance} onChange={(e) => setAttendance(+e.target.value)}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-white">
                            <option value={1}>Daytime Classes</option>
                            <option value={0}>Evening Classes</option>
                          </select>
                          <HelpText>Evening students often balance work and study, which can increase risk.</HelpText>
                        </div>
                      </div>
                    </div>

                    {/* Slide 2: Financial */}
                    <div className="w-full shrink-0 p-5">
                      <div className="mb-4 flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                          <DollarSign className="h-4 w-4" />
                        </div>
                        <div>
                          <h2 className="text-base font-semibold text-slate-800">Financial Information</h2>
                          <p className="text-xs text-slate-400">Financial stress is a known contributor to dropout risk.</p>
                        </div>
                      </div>

                      <div className="grid gap-4 sm:grid-cols-3">
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Outstanding Debt</label>
                          <select value={isDebtor} onChange={(e) => setIsDebtor(+e.target.value)}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-white">
                            <option value={0}>No</option>
                            <option value={1}>Yes</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Tuition Payment Status</label>
                          <select value={tuitionUpToDate} onChange={(e) => setTuitionUpToDate(+e.target.value)}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-white">
                            <option value={1}>Up to Date</option>
                            <option value={0}>Overdue</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-xs font-semibold text-slate-700">Scholarship</label>
                          <select value={hasScholarship} onChange={(e) => setHasScholarship(+e.target.value)}
                            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 bg-white">
                            <option value={0}>None</option>
                            <option value={1}>Active</option>
                          </select>
                        </div>
                      </div>

                      <div className={`mt-4 rounded-lg border p-3 ${
                        financialStress > 0.6 ? "border-red-200 bg-red-50" : financialStress > 0.3 ? "border-amber-200 bg-amber-50" : "border-emerald-200 bg-emerald-50"
                      }`}>
                        <div className="flex items-center justify-between">
                          <div>
                            <span className="text-xs font-semibold text-slate-600">Financial Stress Index</span>
                            <p className="text-[11px] text-slate-400">Weighted score: debt(40%) + overdue tuition(40%) + no scholarship(20%)</p>
                          </div>
                          <span className={`text-lg font-bold ${financialStress > 0.6 ? "text-red-600" : financialStress > 0.3 ? "text-amber-600" : "text-emerald-600"}`}>{financialStress.toFixed(3)}</span>
                        </div>
                        <div className="mt-1.5 flex gap-2">
                          <span className={`rounded px-2 py-0.5 text-[11px] font-medium ${financialStress <= 0.3 ? "bg-emerald-200 text-emerald-800" : "bg-slate-100 text-slate-400"}`}>Low</span>
                          <span className={`rounded px-2 py-0.5 text-[11px] font-medium ${financialStress > 0.3 && financialStress <= 0.6 ? "bg-amber-200 text-amber-800" : "bg-slate-100 text-slate-400"}`}>Moderate</span>
                          <span className={`rounded px-2 py-0.5 text-[11px] font-medium ${financialStress > 0.6 ? "bg-red-200 text-red-800" : "bg-slate-100 text-slate-400"}`}>High</span>
                        </div>
                      </div>
                    </div>

                    {/* Slide 3: Risk Factors */}
                    <div className="w-full shrink-0 p-5">
                      <div className="mb-4 flex items-center gap-2">
                        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                          <AlertTriangle className="h-4 w-4" />
                        </div>
                        <div>
                          <h2 className="text-base font-semibold text-slate-800">Additional Risk Factors</h2>
                          <p className="text-xs text-slate-400">Attendance behavior is a strong predictor of dropout risk.</p>
                        </div>
                      </div>

                      <div>
                        <div className="flex items-center justify-between">
                          <label className="text-xs font-semibold text-slate-700">Absenteeism Trend</label>
                          <span className={`text-xs font-bold ${absentColor}`}>{absentLabel}</span>
                        </div>
                        <input type="range" value={absent} onChange={(e) => setAbsent(+e.target.value)} min={0} max={1} step={0.05}
                          className="mt-2 w-full accent-indigo-600" />
                        <div className="mt-1 flex justify-between text-[11px] text-slate-400">
                          <span>0<br/>Perfect</span>
                          <span>0.25<br/>Slight</span>
                          <span>0.5<br/>Moderate</span>
                          <span>0.75<br/>High</span>
                          <span>1<br/>Severe</span>
                        </div>
                        <p className="mt-2 text-[11px] text-slate-400">How often the student misses classes. Drag to the right if absenteeism is increasing over time.</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Prev / Next Navigation */}
                <div className="flex items-center justify-between border-t border-slate-100 px-5 py-3">
                  <button
                    onClick={() => setStep(Math.max(0, step - 1))}
                    disabled={step === 0}
                    className="rounded-lg border border-slate-300 px-4 py-2 text-xs font-semibold text-slate-600 transition-all hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-30"
                  >
                    ← Previous
                  </button>
                  <span className="text-xs text-slate-400">Step {step + 1} of 4</span>
                  {step < 3 ? (
                    <button
                      onClick={() => setStep(Math.min(3, step + 1))}
                      className="rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-indigo-700"
                    >
                      Next →
                    </button>
                  ) : (
                    <span className="text-xs font-medium text-emerald-600">All set!</span>
                  )}
                </div>
              </div>
            ) : (
              /* ===== MANUAL INPUT ===== */
              <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="mb-4 flex items-center gap-2">
                  <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-100 text-indigo-700">
                    <Gauge className="h-4 w-4" />
                  </div>
                  <div>
                    <h2 className="text-base font-semibold text-slate-800">Manual Feature Entry</h2>
                    <p className="text-xs text-slate-400">For advanced users with pre-calculated values. Enter all 15 feature values directly.</p>
                  </div>
                </div>
                <div className="grid gap-4 sm:grid-cols-2">
                  {[
                    { i: 0, label: "1st Semester Grade", desc: "Average grade (0–20)" },
                    { i: 1, label: "1st Semester Approved", desc: "Courses passed" },
                    { i: 2, label: "2nd Semester Grade", desc: "Average grade (0–20)" },
                    { i: 3, label: "2nd Semester Approved", desc: "Courses passed" },
                    { i: 4, label: "Grade Delta", desc: "S2 grade − S1 grade" },
                    { i: 5, label: "Approved Delta", desc: "S2 approved − S1 approved" },
                    { i: 6, label: "Efficiency Change", desc: "Approval rate change" },
                    { i: 7, label: "Absenteeism Trend", desc: "0 (perfect) → 1 (severe)" },
                    { i: 8, label: "Financial Stress Index", desc: "0 (low) → 1 (high)" },
                    { i: 9, label: "Age Group", desc: "0=17–20, 1=21–25, 2=26+" },
                    { i: 10, label: "Admission Grade", desc: "Entry exam score (0–200)" },
                    { i: 11, label: "Unemployment Rate", desc: "Regional %" },
                    { i: 12, label: "Previous Qualification", desc: "Education code" },
                    { i: 13, label: "Course Code", desc: "Program identifier" },
                    { i: 14, label: "Attendance", desc: "1=Daytime, 0=Evening" },
                  ].map(({ i, label, desc }) => (
                    <div key={i}>
                      <label className="block text-xs font-semibold text-slate-700">{label}</label>
                      <input type="number" value={manualVals[i]} onChange={(e) => handleManualChange(i, +e.target.value)}
                        step={typeof DEFAULT_FEATURES[i] === "number" && DEFAULT_FEATURES[i] % 1 !== 0 ? 0.1 : 1}
                        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm outline-none transition-colors focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200" />
                      <p className="mt-0.5 text-[11px] text-slate-400">{desc}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Predict Button */}
            <button
              onClick={handlePredict}
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-xl hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  Running ML Model...
                </span>
              ) : (
                <><Brain className="h-4 w-4" /> Generate Prediction <ArrowRight className="h-4 w-4" /></>
              )}
            </button>

            {error && <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>}
          </div>

          {/* Right: Results Panel */}
          <div className="space-y-5">
            {!result && !loading && (
              <div className="flex h-full min-h-[400px] items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-white p-12 text-center">
                <div>
                  <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50">
                    <Brain className="h-8 w-8 text-indigo-400" />
                  </div>
                  <p className="text-sm font-medium text-slate-500">Waiting for input...</p>
                  <p className="mt-1 max-w-xs text-xs text-slate-400">Fill in the student details on the left and click &quot;Generate Prediction&quot; to see the AI-powered risk analysis here.</p>
                </div>
              </div>
            )}
            {loading && (
              <div className="flex items-center justify-center rounded-xl border border-slate-200 bg-white p-12 text-center">
                <div>
                  <svg className="mx-auto h-8 w-8 animate-spin text-indigo-600" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <p className="mt-3 text-sm text-slate-500">Analyzing student data with Random Forest model...</p>
                </div>
              </div>
            )}
            {result && (
              <div className="space-y-4 animate-fade-in">
                <RiskCard prediction={result.prediction} dropoutProb={result.dropout_probability} graduateProb={result.graduate_probability} />

                <div className="grid grid-cols-2 gap-3">
                  <MetricCard label="Dropout Probability" value={`${result.dropout_probability.toFixed(1)}%`} color={result.prediction === 1 ? "text-red-500" : "text-emerald-600"} />
                  <MetricCard label="Graduate Probability" value={`${result.graduate_probability.toFixed(1)}%`} color={result.prediction === 0 ? "text-emerald-600" : "text-slate-900"} />
                </div>

                {/* Visualization Tabs */}
                <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                  <div className="flex border-b border-slate-200">
                    {(["gauge", "shap", "factors"] as const).map((tab) => (
                      <button
                        key={tab}
                        onClick={() => setActiveTab(tab)}
                        className={`flex-1 px-4 py-2.5 text-xs font-semibold uppercase tracking-wider transition-all ${
                          activeTab === tab
                            ? "border-b-2 border-indigo-600 text-indigo-700 bg-indigo-50/50"
                            : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                        }`}
                      >
                        {tab === "gauge" ? "Probability Gauge" : tab === "shap" ? "SHAP Analysis" : "Top Factors"}
                      </button>
                    ))}
                  </div>
                  <div className="p-5">
                    {activeTab === "gauge" && (
                      <div className="flex flex-col items-center">
                        <GaugeChart value={result.dropout_probability} />
                        <p className="mt-3 text-xs text-slate-400 text-center max-w-xs">
                          The gauge shows the model&apos;s confidence. Green = low risk, Yellow = moderate, Red = high risk (&gt;70%).
                        </p>
                      </div>
                    )}
                    {activeTab === "shap" && (
                      <div>
                        <ShapWaterfall shapValues={result.shap_values} featureNames={result.feature_display_names} />
                        <p className="mt-2 text-xs text-slate-400 text-center">
                          Red bars push toward dropout, green bars push toward graduation. Wider bar = stronger influence.
                        </p>
                      </div>
                    )}
                    {activeTab === "factors" && (
                      <div className="space-y-3">
                        <p className="text-xs font-medium text-slate-500">Top factors driving this prediction:</p>
                        {result.shap_values
                          .map((v, i) => ({ feature: result.feature_display_names[i] ?? result.feature_names[i], shap: v }))
                          .sort((a, b) => Math.abs(b.shap) - Math.abs(a.shap))
                          .slice(0, 5)
                          .map((f, i) => (
                            <div key={i} className="flex items-center justify-between rounded-lg border border-slate-100 bg-slate-50/50 p-3">
                              <div className="flex items-center gap-2">
                                <span className={`inline-block h-2 w-2 rounded-full ${f.shap >= 0 ? "bg-red-500" : "bg-emerald-500"}`} />
                                <span className="text-sm font-medium text-slate-700">{f.feature}</span>
                              </div>
                              <div className="flex items-center gap-1.5">
                                {f.shap >= 0 ? <TrendingUp className="h-3 w-3 text-red-500" /> : <TrendingDown className="h-3 w-3 text-emerald-500" />}
                                <span className={`text-xs font-bold ${f.shap >= 0 ? "text-red-500" : "text-emerald-600"}`}>
                                  {f.shap >= 0 ? "+" : ""}{f.shap.toFixed(4)}
                                </span>
                              </div>
                            </div>
                          ))}
                        <p className="text-xs text-slate-400 flex items-center gap-1">
                          <Sparkles className="h-3 w-3" />
                          Green = decreases risk &middot; Red = increases risk &middot; Larger numbers = stronger effect
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
