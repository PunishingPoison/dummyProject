import type { PredictResponse, BatchResponse, AnalyticsResponse } from "./types";

const BASE_URL = "/api";

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function predictSingle(features: number[]): Promise<PredictResponse> {
  return fetchJson<PredictResponse>("/predict", {
    method: "POST",
    body: JSON.stringify({ features }),
  });
}

export async function predictBatch(file: File): Promise<BatchResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${BASE_URL}/predict/batch`, { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(err || `HTTP ${res.status}`);
  }
  return res.json();
}

export async function getAnalytics(): Promise<AnalyticsResponse> {
  return fetchJson<AnalyticsResponse>("/analytics");
}
