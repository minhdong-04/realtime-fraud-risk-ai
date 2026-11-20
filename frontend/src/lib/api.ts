/**
 * {
 *   module : api.ts
 *   desc   : Client goi API tap trung giao tiep voi Backend FastAPI kem Bearer JWT & Cursor Pagination
 * }
 */

import { FraudCase, PaginatedFraudCases, ModelVersion, DashboardMetrics, AnalystDecision } from "@/types/fraud.types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function getAuthHeaders(): Record<string, string> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("sentinel_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }
  }
  return headers;
}

/**
 * {
 *   func   : fetchFraudCases
 *   desc   : Truy van phan trang ca gian lan dung Cursor-based Keyset toi uu O(1)
 *   input  : level (string | undefined), status (string | undefined), cursor (string | undefined), limit (number)
 *   output : Promise<PaginatedFraudCases>
 *   loop   : 0 loops
 * }
 */
export async function fetchFraudCases(
  level?: string,
  status?: string,
  cursor?: string | null,
  limit: number = 20
): Promise<PaginatedFraudCases> {
  try {
    const params = new URLSearchParams();
    if (level && level !== "ALL") params.append("level", level);
    if (status && status !== "ALL") params.append("status", status);
    if (cursor) params.append("cursor", cursor);
    params.append("limit", limit.toString());

    const res = await fetch(`${API_BASE_URL}/fraud-cases?${params.toString()}`, {
      headers: getAuthHeaders(),
      cache: "no-store",
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (Array.isArray(data)) {
      return { items: data, next_cursor: null, has_more: false, total_count: data.length };
    }
    return data as PaginatedFraudCases;
  } catch (err) {
    console.warn("API Backend chua khoi dong, dang dung du lieu gia lap dia phuong", err);
    const mock = getMockFraudCases();
    return { items: mock, next_cursor: null, has_more: false, total_count: mock.length };
  }
}

export async function fetchFraudCaseById(id: string): Promise<FraudCase> {
  try {
    const res = await fetch(`${API_BASE_URL}/fraud-cases/${id}`, {
      headers: getAuthHeaders(),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    const cases = getMockFraudCases();
    return cases.find(c => c.id === id) || cases[0];
  }
}

export async function submitAnalystReview(
  caseId: string,
  decision: AnalystDecision,
  reason: string
): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/fraud-cases/${caseId}/review`, {
    method: "POST",
    headers: getAuthHeaders(),
    body: JSON.stringify({ decision, reason }),
  });

  if (!res.ok) {
    const errText = await res.text();
    throw new Error(`Gui ket qua that bai: ${errText}`);
  }
}

export async function simulatePaySimTransactions(count: number = 5, fraudOnly: boolean = false): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/transactions/simulate-paysim?count=${count}&fraud_only=${fraudOnly}`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Mô phỏng giao dịch PaySim thất bại");
  return await res.json();
}

export async function fetchDashboardMetrics(): Promise<DashboardMetrics> {
  try {
    const res = await fetch(`${API_BASE_URL}/analytics/fraud`, {
      headers: getAuthHeaders(),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return {
      fraud_rate: 1.84,
      fp_rate: 6.2,
      cases_reviewed_today: 42,
      total_cases: 128,
      total_transactions: 14250,
      risk_distribution: [
        { level: "HIGH", count: 18, color: "#d1556c" },
        { level: "MEDIUM", count: 45, color: "#f4d4b2" },
        { level: "LOW", count: 110, color: "#2cb285" },
      ],
      trend: [
        { date: "2026-08-01", fraud_rate: 2.1, fp_rate: 7.5, volume: 110 },
        { date: "2026-08-05", fraud_rate: 1.9, fp_rate: 6.8, volume: 135 },
        { date: "2026-08-10", fraud_rate: 1.8, fp_rate: 6.2, volume: 150 },
      ],
    };
  }
}

export async function fetchModelVersions(): Promise<ModelVersion[]> {
  try {
    const res = await fetch(`${API_BASE_URL}/models`, {
      headers: getAuthHeaders(),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    return [
      {
        id: "m-1",
        name: "xgboost_hybrid",
        version: "v1.0.0",
        prAuc: 0.7548,
        recall: 0.89,
        precision: 0.82,
        f1Score: 0.85,
        brierScore: 0.0013,
        expectedCost: 1463.0,
        status: "PRODUCTION",
        isShadow: false,
        createdAt: "2026-08-01T10:00:00Z",
      },
    ];
  }
}

export async function promoteModelVersion(version: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/models/${version}/promote`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Thang cap phien ban mo hinh that bai");
}

export async function toggleShadowMode(version: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/models/${version}/shadow`, {
    method: "POST",
    headers: getAuthHeaders(),
  });
  if (!res.ok) throw new Error("Bat/Tat che do shadow that bai");
}

function getMockFraudCases(): FraudCase[] {
  return [
    {
      id: "case-001",
      transactionId: "PAYSIM-88912",
      riskLevel: "HIGH",
      riskScore: 92,
      status: "OPEN",
      assignedTo: null,
      createdAt: "2026-08-13T23:10:00Z",
      closedAt: null,
      transaction: {
        amount: 45000000,
        currency: "VND",
        channel: "TRANSFER",
        createdAt: "2026-08-13T23:10:00Z",
        accountId: "ACC-PAYSIM-102",
        merchantId: "MERCH-PAYSIM-VN",
      },
      shapValues: [
        { featureName: "new_device_flag", featureValue: 1, shapValue: 0.28, label: "Thiet bi moi chua tung ghi nhan" },
        { featureName: "txn_count_5m", featureValue: 7, shapValue: 0.24, label: "So luong giao dich trong 5 phut" },
        { featureName: "amount_ratio", featureValue: 8.5, shapValue: 0.19, label: "Ty le so tien so voi TB 30 ngay" },
      ],
    },
  ];
}
