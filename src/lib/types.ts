export interface PredictResponse {
  prediction: number;
  dropout_probability: number;
  graduate_probability: number;
  shap_values: number[];
  feature_names: string[];
  feature_display_names: string[];
}

export interface BatchResult {
  prediction: number;
  dropout_probability: number;
  graduate_probability: number;
}

export interface BatchResponse {
  total: number;
  dropout_count: number;
  high_risk_count: number;
  avg_dropout_probability: number;
  results: BatchResult[];
}

export interface AnalyticsResponse {
  metrics: {
    accuracy: number;
    precision: number;
    recall: number;
    f1_score: number;
    roc_auc: number;
  };
  feature_importance: {
    features: string[];
    display_names: string[];
    values: number[];
  };
  config: {
    algorithm: string;
    trees: number;
    max_depth: number;
    class_weight: string;
    random_state: number;
    total_samples: number;
    training_samples: number;
    test_samples: number;
    features_count: number;
    scaling: string;
  };
}

export const FEATURE_NAMES = [
  "Curricular_units_1st_sem_grade",
  "Curricular_units_1st_sem_approved",
  "Curricular_units_2nd_sem_grade",
  "Curricular_units_2nd_sem_approved",
  "grade_delta",
  "approved_delta",
  "efficiency_change",
  "absenteeism_trend",
  "financial_stress_index",
  "age_group",
  "Admission_grade",
  "Unemployment_rate",
  "Previous_qualification",
  "Course",
  "Daytime_per_evening_attendance",
];

export const DEFAULT_FEATURES = [
  12.5, 5, 11.8, 4, -0.7, -1, -0.167, 0.25, 0.35, 1, 125.0, 10.5, 1, 9238, 1,
];

export function calculateDeltas(
  s1g: number, s1a: number, s1e: number,
  s2g: number, s2a: number, s2e: number
) {
  const gradeDelta = s2g - s1g;
  const approvedDelta = s2a - s1a;
  let efficiencyChange = 0;
  if (s1e > 0 && s2e > 0) {
    efficiencyChange = (s2a / s2e) - (s1a / s1e);
  }
  return { gradeDelta, approvedDelta, efficiencyChange };
}

export function calculateFinancialStress(
  isDebtor: number,
  tuitionUpToDate: number,
  hasScholarship: number
) {
  return (isDebtor * 0.4) + ((1 - tuitionUpToDate) * 0.4) + ((1 - hasScholarship) * 0.2);
}

export function ageToGroup(age: number): number {
  if (age <= 20) return 0;
  if (age <= 25) return 1;
  return 2;
}
