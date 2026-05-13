"use client";

import { useState, useEffect } from "react";
import Navbar from "@/components/Navbar";
import MetricCard from "@/components/MetricCard";
import FeatureImportance from "@/components/FeatureImportance";
import { getAnalytics } from "@/lib/api";
import type { AnalyticsResponse } from "@/lib/types";
import {
  BarChart as BarChartIcon,
  Info,
  Settings,
  Database,
  TrendingUp,
  Target,
  Activity,
} from "lucide-react";

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getAnalytics()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <>
        <Navbar />
        <main className="mx-auto max-w-5xl px-4 py-20 text-center">
          <svg className="mx-auto h-8 w-8 animate-spin text-indigo-600" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="mt-4 text-sm text-slate-500">Loading analytics...</p>
        </main>
      </>
    );
  }

  if (error) {
    return (
      <>
        <Navbar />
        <main className="mx-auto max-w-5xl px-4 py-20 text-center">
          <p className="text-red-600">{error}</p>
        </main>
      </>
    );
  }

  if (!data) return null;

  const metrics = [
    { label: "Accuracy", value: `${data.metrics.accuracy}%`, icon: Target, color: "text-emerald-600" },
    { label: "Precision", value: `${data.metrics.precision}%`, icon: TrendingUp, color: "text-blue-600" },
    { label: "Recall", value: `${data.metrics.recall}%`, icon: Activity, color: "text-purple-600" },
    { label: "F1 Score", value: `${data.metrics.f1_score}%`, icon: BarChartIcon, color: "text-pink-600" },
    { label: "ROC-AUC", value: `${data.metrics.roc_auc}%`, icon: Target, color: "text-amber-600" },
  ];

  const cfgRows: [string, string][] = [
    ["Algorithm", data.config.algorithm],
    ["Trees", data.config.trees.toString()],
    ["Max Depth", data.config.max_depth.toString()],
    ["Class Weight", data.config.class_weight],
    ["Total Samples", data.config.total_samples.toLocaleString()],
    ["Training Set", data.config.training_samples.toLocaleString()],
    ["Test Set", data.config.test_samples.toLocaleString()],
    ["Features", data.config.features_count.toString()],
    ["Scaling", data.config.scaling],
  ];

  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Model Performance Dashboard</h1>
          <p className="mt-1 text-slate-500">
            Random Forest classifier achieving <strong className="text-slate-700">{data.metrics.accuracy}% accuracy</strong> on {data.config.training_samples.toLocaleString()} training samples.
          </p>
        </div>

        {/* Performance Metrics */}
        <div className="mb-8">
          <div className="mb-4 flex items-center gap-2">
            <BarChartIcon className="h-5 w-5 text-indigo-600" />
            <h2 className="text-lg font-semibold text-slate-800">Performance Metrics</h2>
          </div>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {metrics.map((m) => {
              const Icon = m.icon;
              return (
                <div key={m.label} className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm card-hover">
                  <div className="mb-3 flex items-center justify-between">
                    <p className="text-xs font-semibold uppercase tracking-wider text-slate-500">{m.label}</p>
                    <Icon className={`h-4 w-4 ${m.color}`} />
                  </div>
                  <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
                </div>
              );
            })}
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Feature Importance */}
          <div className="lg:col-span-2">
            <FeatureImportance
              features={data.feature_importance.features}
              values={data.feature_importance.values}
              displayNames={data.feature_importance.display_names}
            />
          </div>

          {/* Model Config */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Settings className="h-5 w-5 text-indigo-600" />
              <h2 className="text-base font-semibold text-slate-800">Model Configuration</h2>
            </div>
            <div className="space-y-2">
              {cfgRows.map(([k, v]) => (
                <div key={k} className="flex justify-between rounded-lg bg-slate-50/50 px-3 py-2 text-sm">
                  <span className="text-slate-500">{k}</span>
                  <span className="font-medium text-slate-800">{v}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Training Dataset */}
          <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-4 flex items-center gap-2">
              <Database className="h-5 w-5 text-indigo-600" />
              <h2 className="text-base font-semibold text-slate-800">Data & Preprocessing</h2>
            </div>
            <div className="space-y-4">
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Preprocessing Steps</h3>
                <ul className="space-y-1.5 text-sm text-slate-600">
                  <li className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Data leakage prevention</li>
                  <li className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Feature engineering (deltas)</li>
                  <li className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> Categorical encoding</li>
                  <li className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> StandardScaler normalization</li>
                  <li className="flex items-center gap-2"><span className="h-1.5 w-1.5 rounded-full bg-emerald-500" /> 75/25 stratified split</li>
                </ul>
              </div>
              <div>
                <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">Engineered Features</h3>
                <ul className="space-y-1.5 text-sm text-slate-600">
                  <li><strong>grade_delta:</strong> Performance trend (sem2 - sem1)</li>
                  <li><strong>approved_delta:</strong> Course completion trend</li>
                  <li><strong>efficiency_change:</strong> Approval rate dynamics</li>
                  <li><strong>financial_stress_index:</strong> Composite financial risk</li>
                  <li><strong>age_group:</strong> Categorical age buckets</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </>
  );
}
