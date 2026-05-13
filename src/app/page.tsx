"use client";

import Link from "next/link";
import { ArrowRight, Brain, Upload, BarChart3, Shield, Zap, TrendingUp } from "lucide-react";
import Navbar from "@/components/Navbar";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Predictions",
    desc: "Random Forest model with 88.43% accuracy trained on 3,300+ student records",
  },
  {
    icon: Zap,
    title: "SHAP Explainability",
    desc: "Understand exactly which factors drive each prediction with interactive visualizations",
  },
  {
    icon: Upload,
    title: "Batch Processing",
    desc: "Upload a CSV to analyze entire cohorts at once with detailed risk breakdowns",
  },
  {
    icon: BarChart3,
    title: "Analytics Dashboard",
    desc: "Explore model performance metrics and global feature importance rankings",
  },
  {
    icon: Shield,
    title: "Early Intervention",
    desc: "Identify at-risk students early with 70%+ probability threshold alerts",
  },
  {
    icon: TrendingUp,
    title: "Performance Trends",
    desc: "Track grade changes, approval rates, and efficiency between semesters",
  },
];

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        {/* Hero */}
        <section className="relative overflow-hidden border-b border-slate-200/80 bg-gradient-to-b from-indigo-50/60 via-white to-white">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(99,102,241,0.08),transparent_50%)]" />
          <div className="relative mx-auto max-w-5xl px-4 py-24 text-center">
            <div className="mb-4 inline-flex items-center gap-1.5 rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">
              <Shield className="h-3.5 w-3.5" /> v2.0 &middot; Production Ready
            </div>
            <h1 className="text-5xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-6xl">
              Predict Student
              <br />
              <span className="gradient-text">Dropout Risk</span>
            </h1>
            <p className="mx-auto mt-5 max-w-2xl text-lg text-slate-500">
              An AI-powered early warning system that identifies students at risk of dropping out
              with <strong className="text-slate-700">88.43% accuracy</strong>, powered by SHAP
              explainability and Random Forest classification.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Link
                href="/predict"
                className="flex items-center gap-2 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 transition-all hover:shadow-xl hover:shadow-indigo-500/30 hover:brightness-110"
              >
                Try Single Prediction <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/batch"
                className="flex items-center gap-2 rounded-xl border border-slate-300 bg-white px-6 py-3 text-sm font-semibold text-slate-700 shadow-sm transition-all hover:bg-slate-50 hover:shadow-md"
              >
                Batch Upload <Upload className="h-4 w-4" />
              </Link>
            </div>
          </div>
        </section>

        {/* Stats */}
        <section className="border-b border-slate-200/80 bg-white">
          <div className="mx-auto max-w-5xl px-4 py-12">
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
              {[
                { label: "Accuracy", value: "88.43%" },
                { label: "ROC-AUC", value: "93.43%" },
                { label: "Students Trained", value: "3,318" },
                { label: "Features", value: "15" },
              ].map((s) => (
                <div key={s.label} className="rounded-xl border border-slate-200 bg-slate-50/50 p-4 text-center">
                  <p className="text-2xl font-bold text-slate-900">{s.value}</p>
                  <p className="mt-0.5 text-xs font-medium uppercase tracking-wider text-slate-500">{s.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="mx-auto max-w-5xl px-4 py-20">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-slate-900">Everything you need to reduce dropout rates</h2>
            <p className="mt-3 text-slate-500">
              From individual assessments to cohort-wide analysis, make data-driven decisions.
            </p>
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => {
              const Icon = f.icon;
              return (
                <div
                  key={f.title}
                  className="group rounded-xl border border-slate-200 bg-white p-6 shadow-sm transition-all card-hover"
                >
                  <div className="mb-4 flex h-11 w-11 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 transition-colors group-hover:bg-indigo-100">
                    <Icon className="h-5.5 w-5.5" />
                  </div>
                  <h3 className="text-base font-semibold text-slate-900">{f.title}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-slate-500">{f.desc}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* How it works */}
        <section className="border-t border-slate-200/80 bg-slate-50/50">
          <div className="mx-auto max-w-5xl px-4 py-20">
            <div className="mb-12 text-center">
              <h2 className="text-3xl font-bold text-slate-900">How it works</h2>
              <p className="mt-3 text-slate-500">Three simple steps to get insights.</p>
            </div>
            <div className="grid gap-8 sm:grid-cols-3">
              {[
                { step: "01", title: "Enter Student Data", desc: "Input academic performance, demographics, and financial information manually or via CSV." },
                { step: "02", title: "AI Analyzes Risk", desc: "Our Random Forest model processes 15 features to compute dropout probability with 88.43% accuracy." },
                { step: "03", title: "Get Actionable Insights", desc: "Review the prediction, explore SHAP explanations, and download detailed reports." },
              ].map((s) => (
                <div key={s.step} className="text-center">
                  <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-700">
                    {s.step}
                  </div>
                  <h3 className="text-lg font-semibold text-slate-900">{s.title}</h3>
                  <p className="mt-1.5 text-sm text-slate-500">{s.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="border-t border-slate-200/80 bg-white py-8 text-center text-sm text-slate-400">
          <p>Student Dropout Predictor &middot; Powered by Random Forest &middot; v2.0</p>
        </footer>
      </main>
    </>
  );
}
