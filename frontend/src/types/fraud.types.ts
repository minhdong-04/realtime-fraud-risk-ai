/**
 * {
 *   module : fraud.types.ts
 *   desc   : Dinh nghia tap hop cac kieu du lieu TypeScript ho tro JWT Auth va RBAC
 * }
 */

export type UserRole = "ANALYST" | "MANAGER" | "ML_ENGINEER";

export interface UserProfile {
  readonly email: string;
  readonly role: UserRole;
  readonly name?: string;
}

export interface AuthTokenResponse {
  readonly access_token: string;
  readonly token_type: string;
  readonly role: UserRole;
  readonly email: string;
}

export type RiskLevel = "LOW" | "MEDIUM" | "HIGH";

export type CaseStatus = "OPEN" | "ASSIGNED" | "UNDER_REVIEW" | "ESCALATED" | "CLOSED";

export type AnalystDecision = "LEGITIMATE" | "CONFIRMED_FRAUD" | "NEED_MORE_INFO";

export interface ShapFeature {
  readonly featureName: string;
  readonly featureValue: number;
  readonly shapValue: number;
  readonly label?: string;
}

export interface FraudCase {
  readonly id: string;
  readonly transactionId?: string;
  readonly transaction_id?: string;
  readonly riskLevel?: RiskLevel;
  readonly risk_level?: RiskLevel;
  readonly riskScore?: number;
  readonly risk_score?: number;
  readonly status: CaseStatus;
  readonly assignedTo?: string | null;
  readonly assigned_to?: string | null;
  readonly createdAt?: string;
  readonly created_at?: string;
  readonly closedAt?: string | null;
  readonly closed_at?: string | null;
  readonly transaction?: {
    amount: number;
    currency: string;
    channel: string;
    createdAt?: string;
    created_at?: string;
    accountId?: string;
    account_id?: string;
    merchantId?: string;
    merchant_id?: string;
  };
  readonly shapValues?: ShapFeature[];
  readonly shap_values?: ShapFeature[];
  readonly history?: Array<{
    id: string;
    amount: number;
    currency: string;
    channel: string;
    status: string;
    createdAt?: string;
    created_at?: string;
  }>;
}

export interface PaginatedFraudCases {
  readonly items: FraudCase[];
  readonly next_cursor: string | null;
  readonly has_more: boolean;
  readonly total_count: number;
}

export interface ModelVersion {
  readonly id: string;
  readonly name: string;
  readonly version: string;
  readonly prAuc?: number;
  readonly pr_auc?: number;
  readonly recall: number;
  readonly precision: number;
  readonly f1Score?: number;
  readonly f1_score?: number;
  readonly brierScore?: number;
  readonly brier_score?: number;
  readonly expectedCost?: number;
  readonly expected_cost?: number;
  readonly status: "CANDIDATE" | "PRODUCTION" | "RETIRED";
  readonly isShadow?: boolean;
  readonly is_shadow?: boolean;
  readonly createdAt?: string;
  readonly created_at?: string;
}

export interface DashboardMetrics {
  readonly fraud_rate: number;
  readonly fp_rate: number;
  readonly cases_reviewed_today: number;
  readonly total_cases: number;
  readonly total_transactions: number;
  readonly risk_distribution: Array<{
    level: string;
    count: number;
    color: string;
  }>;
  readonly trend: Array<{
    date: string;
    fraud_rate: number;
    fp_rate: number;
    volume: number;
  }>;
}
