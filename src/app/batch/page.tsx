"use client";

import { useState, useRef } from "react";
import Navbar from "@/components/Navbar";
import MetricCard from "@/components/MetricCard";
import RiskDistributionPie from "@/components/RiskDistributionPie";
import ProbabilityHistogram from "@/components/ProbabilityHistogram";
import EmptyState from "@/components/EmptyState";
import { predictBatch } from "@/lib/api";
import { FEATURE_NAMES, type BatchResponse, type BatchResult } from "@/lib/types";
import { Upload, Download, AlertTriangle, FileText, ClipboardPaste } from "lucide-react";

type InputMethod = "upload" | "paste";

export default function BatchPage() {
  const [method, setMethod] = useState<InputMethod>("upload");
  const [file, setFile] = useState<File | null>(null);
  const [pasteData, setPasteData] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<BatchResponse | null>(null);
  const [error, setError] = useState("");
  const [filterRisk, setFilterRisk] = useState<string[]>(["Low", "Medium", "High"]);
  const fileRef = useRef<HTMLInputElement>(null);

  const handlePredict = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      let f: File;
      if (method === "upload") {
        if (!file) throw new Error("Please select a CSV file");
        f = file;
      } else {
        if (!pasteData.trim()) throw new Error("Please paste CSV data");
        f = new File([pasteData], "pasted.csv", { type: "text/csv" });
      }
      const res = await predictBatch(f);
      setResult(res);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Batch prediction failed");
    } finally {
      setLoading(false);
    }
  };

  const downloadCSV = (data: BatchResult[], label: string) => {
    const header = "prediction,dropout_probability,graduate_probability";
    const rows = data.map((r) => `${r.prediction},${r.dropout_probability},${r.graduate_probability}`);
    const csv = [header, ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${label}_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const filteredResults = result
    ? result.results.filter((r) => {
        const level = r.dropout_probability > 70 ? "High" : r.dropout_probability > 30 ? "Medium" : "Low";
        return filterRisk.includes(level);
      })
    : [];

  const highRisk = result?.results.filter((r) => r.dropout_probability > 70) ?? [];

  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-5xl px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-900">Batch Risk Assessment</h1>
          <p className="mt-1 text-slate-500">Process multiple students at once with cohort analysis.</p>
        </div>

        {/* Method Toggle */}
        <div className="mb-6 flex gap-2 rounded-xl border border-slate-200 bg-white p-1.5 shadow-sm">
          {(["upload", "paste"] as const).map((m) => (
            <button
              key={m}
              onClick={() => { setMethod(m); setResult(null); }}
              className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-medium transition-all ${
                method === m
                  ? "bg-indigo-600 text-white shadow-sm"
                  : "text-slate-600 hover:bg-slate-100"
              }`}
            >
              {m === "upload" ? "Upload CSV" : "Paste Data"}
            </button>
          ))}
        </div>

        <div className="grid gap-6 lg:grid-cols-[1fr_400px]">
          {/* Left: Input */}
          <div className="space-y-5">
            {/* Input Area */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              {method === "upload" ? (
                <div
                  onClick={() => fileRef.current?.click()}
                  className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50/50 p-10 text-center transition-all hover:border-indigo-400 hover:bg-indigo-50/30"
                >
                  <Upload className="mb-3 h-8 w-8 text-slate-400" />
                  <p className="text-sm font-medium text-slate-600">
                    {file ? file.name : "Drop CSV file or click to browse"}
                  </p>
                  {file && <p className="mt-1 text-xs text-slate-400">{(file.size / 1024).toFixed(1)} KB</p>}
                  <input
                    ref={fileRef}
                    type="file"
                    accept=".csv"
                    className="hidden"
                    onChange={(e) => {
                      setFile(e.target.files?.[0] ?? null);
                      setResult(null);
                    }}
                  />
                </div>
              ) : (
                <div>
                  <p className="mb-2 text-xs font-medium text-slate-500">Paste CSV data (one student per line):</p>
                  <textarea
                    value={pasteData}
                    onChange={(e) => { setPasteData(e.target.value); setResult(null); }}
                    placeholder="12.5,5,11.8,4,-0.7,-1,-0.167,0.25,0.35,1,125.0,10.5,1,9238,1"
                    rows={6}
                    className="w-full rounded-lg border border-slate-300 px-3 py-2.5 text-sm font-mono focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none"
                  />
                </div>
              )}

              <div className="mt-4 flex items-center gap-3">
                <button
                  onClick={handlePredict}
                  disabled={loading || (method === "upload" && !file) || (method === "paste" && !pasteData.trim())}
                  className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-xl disabled:cursor-not-allowed disabled:opacity-60"
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Processing...
                    </span>
                  ) : (
                    <><FileText className="h-4 w-4" /> Run Predictions</>
                  )}
                </button>
                <a
                  href="/sample_data.csv"
                  download
                  className="text-xs font-medium text-indigo-600 hover:text-indigo-800 hover:underline"
                >
                  Download template
                </a>
              </div>
            </div>

            {error && (
              <div className="rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
            )}

            {/* Results Table */}
            {result && (
              <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                <div className="flex items-center justify-between border-b border-slate-200 px-5 py-3">
                  <h3 className="text-sm font-semibold text-slate-800">Detailed Results</h3>
                  <div className="flex items-center gap-2">
                    <select
                      multiple
                      value={filterRisk}
                      onChange={(e) => setFilterRisk(Array.from(e.target.selectedOptions, (o) => o.value))}
                      className="rounded-lg border border-slate-300 px-2 py-1 text-xs outline-none"
                    >
                      {["Low", "Medium", "High"].map((l) => (
                        <option key={l} value={l}>{l}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="max-h-80 overflow-auto">
                  <table className="w-full text-left text-xs">
                    <thead className="bg-slate-50 text-slate-500 sticky top-0">
                      <tr>
                        <th className="px-4 py-2 font-semibold">#</th>
                        <th className="px-4 py-2 font-semibold">Prediction</th>
                        <th className="px-4 py-2 font-semibold">Dropout %</th>
                        <th className="px-4 py-2 font-semibold">Graduate %</th>
                        <th className="px-4 py-2 font-semibold">Risk</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredResults.map((r, i) => (
                        <tr key={i} className="hover:bg-slate-50">
                          <td className="px-4 py-2 text-slate-400">{i + 1}</td>
                          <td className="px-4 py-2">
                            <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium ${
                              r.prediction === 1 ? "bg-red-100 text-red-700" : "bg-emerald-100 text-emerald-700"
                            }`}>
                              {r.prediction === 1 ? "Dropout" : "Graduate"}
                            </span>
                          </td>
                          <td className="px-4 py-2 font-medium">{r.dropout_probability.toFixed(1)}%</td>
                          <td className="px-4 py-2">{r.graduate_probability.toFixed(1)}%</td>
                          <td className="px-4 py-2">
                            <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                              r.dropout_probability > 70
                                ? "bg-red-100 text-red-700"
                                : r.dropout_probability > 30
                                ? "bg-amber-100 text-amber-700"
                                : "bg-emerald-100 text-emerald-700"
                            }`}>
                              {r.dropout_probability > 70 ? "High" : r.dropout_probability > 30 ? "Medium" : "Low"}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3">
                  <p className="text-xs text-slate-400">{filteredResults.length} of {result.results.length} shown</p>
                  <div className="flex gap-2">
                    <button onClick={() => downloadCSV(result.results, "all_predictions")}
                      className="flex items-center gap-1 rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-all">
                      <Download className="h-3 w-3" /> All
                    </button>
                    {highRisk.length > 0 && (
                      <button onClick={() => downloadCSV(highRisk, "high_risk")}
                        className="flex items-center gap-1 rounded-lg border border-red-300 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-50 transition-all">
                        <AlertTriangle className="h-3 w-3" /> High Risk
                      </button>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right: Summary */}
          <div className="space-y-5">
            {!result && !loading && (
              <EmptyState
                icon={<Upload className="h-12 w-12" />}
                title="No data yet"
                description="Upload a CSV file or paste data to analyze a cohort."
              />
            )}
            {loading && (
              <div className="flex items-center justify-center rounded-xl border border-slate-200 bg-white p-12 text-center">
                <div>
                  <svg className="mx-auto h-8 w-8 animate-spin text-indigo-600" viewBox="0 0 24 24" fill="none">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                  </svg>
                  <p className="mt-3 text-sm text-slate-500">Processing batch...</p>
                </div>
              </div>
            )}
            {result && (
              <div className="space-y-4 animate-fade-in">
                <div className="grid grid-cols-2 gap-3">
                  <MetricCard label="Total Students" value={result.total.toString()} />
                  <MetricCard label="Dropouts" value={result.dropout_count.toString()} sub={`${(result.dropout_count / result.total * 100).toFixed(1)}%`} color="text-red-500" />
                  <MetricCard label="High Risk" value={result.high_risk_count.toString()} sub={`${(result.high_risk_count / result.total * 100).toFixed(1)}%`} color="text-red-500" />
                  <MetricCard label="Avg Probability" value={`${result.avg_dropout_probability.toFixed(1)}%`} />
                </div>

                <RiskDistributionPie dropoutProbabilities={result.results.map((r) => r.dropout_probability)} />
                <ProbabilityHistogram dropoutProbabilities={result.results.map((r) => r.dropout_probability)} />

                {highRisk.length > 0 && (
                  <div className="rounded-xl border border-red-200 bg-red-50 p-4">
                    <div className="flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-red-600" />
                      <p className="text-sm font-semibold text-red-800">
                        {highRisk.length} high-risk student{highRisk.length > 1 ? "s" : ""} requiring attention
                      </p>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
