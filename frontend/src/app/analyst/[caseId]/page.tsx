"use client";

import "@/lib/suppress-hydration";
import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { fetchFraudCaseById, submitAnalystReview } from "@/lib/api";
import { FraudCase, AnalystDecision } from "@/types/fraud.types";
import { RiskBadge } from "@/components/RiskBadge";
import { ShapChart } from "@/components/ShapChart";
import { useNotification } from "@/components/NotificationProvider";
import { useAuth } from "@/components/AuthProvider";
import {
  ArrowLeft, ShieldCheck, AlertTriangle, CheckCircle2, HelpCircle, Send, User, CreditCard, Clock, Lock, Eye
} from "lucide-react";

/**
 * {
 *   func   : CaseDetailPage
 *   desc   : Chi tiet ca rui ro kem Waterfall SHAP va form tham dinh kiem tra quyen RBAC
 *   input  : None
 *   output : JSX.Element
 *   loop   : 0 loops
 * }
 */
export default function CaseDetailPage() {
  const params = useParams();
  const router = useRouter();
  const caseId = params.caseId as string;
  const { showNotification } = useNotification();
  const { user } = useAuth();

  const [fraudCase, setFraudCase] = useState<FraudCase | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [decision, setDecision] = useState<AnalystDecision>("CONFIRMED_FRAUD");
  const [reason, setReason] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  const isAnalyst = user?.role === "ANALYST";

  useEffect(() => {
    fetchFraudCaseById(caseId)
      .then(setFraudCase)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, [caseId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isAnalyst) {
      showNotification("error", "Quyền Hạn Bị Từ Chối (RBAC)", "Chỉ Chuyên viên Fraud Analyst mới có quyền thẩm định ca rủi ro!");
      return;
    }

    if (reason.trim().length < 10) {
      setErrorMsg("Vui lòng nhập lý do giải trình thẩm định chi tiết (Tối thiểu 10 ký tự).");
      return;
    }

    setSubmitting(true);
    setErrorMsg("");

    try {
      await submitAnalystReview(caseId, decision, reason);
      showNotification("success", "Thẩm Định Thành Công", `Đã ghi nhận kết quả ${decision} vào hồ sơ kiểm toán.`);
      router.push("/analyst");
    } catch (err: any) {
      setErrorMsg(err.message || "Gửi kết quả thẩm định thất bại.");
      showNotification("error", "Lỗi Thao Tác", err.message || "Không thể lưu kết quả thẩm định.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="p-12 text-center text-slate-400 font-sans">Đang tải hồ sơ điều tra ca rủi ro...</div>;
  }

  if (!fraudCase) {
    return <div className="p-12 text-center text-[#d1556c] font-sans">Không tìm thấy ca rủi ro tương ứng.</div>;
  }

  const txn = fraudCase.transaction;
  const txnId = fraudCase.transactionId || fraudCase.transaction_id || "TXN-AUTO";
  const rLevel = fraudCase.riskLevel || fraudCase.risk_level || "HIGH";
  const rScore = fraudCase.riskScore ?? fraudCase.risk_score ?? 85;
  const createdStr = fraudCase.createdAt || fraudCase.created_at;
  const validTime = createdStr && !isNaN(new Date(createdStr).getTime()) ? new Date(createdStr).toLocaleString() : "Vừa xong";
  const amount = Number(txn?.amount ?? 0);
  const currency = txn?.currency || "VND";
  const channel = txn?.channel || "MOBILE";

  return (
    <div className="space-y-6" suppressHydrationWarning>
      
      {/* RBAC Notice if not Analyst */}
      {!isAnalyst && (
        <div className="p-4 rounded-2xl bg-[#565ac4]/15 border border-[#565ac4]/40 flex items-center justify-between text-xs text-[#eeeff9]">
          <span className="flex items-center gap-2 font-bold">
            <Eye className="w-4 h-4 text-[#9b9eed]" />
            Chế độ Quan Sát Viên — Bạn đang đăng nhập với vai trò {user?.role}. Chỉ Chuyên viên Fraud Analyst mới có quyền thẩm định ca này.
          </span>
          <span className="px-2.5 py-1 rounded-full bg-[#565ac4]/30 text-white font-mono font-bold">
            Read-Only
          </span>
        </div>
      )}

      {/* Header Bar */}
      <div className="flex items-center justify-between glass-panel p-6 rounded-3xl border border-[#30adcd]/25 shadow-glow-blue">
        <div className="flex items-center gap-4">
          <Link
            href="/analyst"
            className="p-2.5 rounded-2xl bg-[#080C14] hover:bg-[#30adcd]/15 border border-[#30adcd]/30 text-slate-300 hover:text-white transition-all shadow-sm"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-xl font-extrabold text-white flex items-center gap-3">
              Hồ Sơ Ca Gian Lận: {txnId}
              <RiskBadge level={rLevel} score={rScore} />
            </h1>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-3" suppressHydrationWarning>
              <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-[#30adcd]" /> {validTime}</span>
              <span className="text-slate-600">•</span>
              <span className="flex items-center gap-1"><CreditCard className="w-3.5 h-3.5 text-[#30adcd]" /> Kênh: {channel}</span>
            </p>
          </div>
        </div>
      </div>

      {/* Grid: 2 Columns */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Transaction Details & SHAP */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Card Info */}
          <div className="glass-panel p-6 rounded-3xl border border-[#30adcd]/25 space-y-4 shadow-glow-blue">
            <h2 className="text-sm font-bold text-white border-b border-[#30adcd]/20 pb-3 flex items-center gap-2">
              <User className="w-4 h-4 text-[#30adcd]" /> Chi Tiết Giao Dịch
            </h2>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-slate-400 block mb-1">Số Tiền</span>
                <span className="font-extrabold text-[#30adcd] font-mono text-sm" suppressHydrationWarning>
                  {amount.toLocaleString("vi-VN")} {currency}
                </span>
              </div>
              <div>
                <span className="text-slate-400 block mb-1">Tài Khoản Gửi</span>
                <span className="font-mono text-white font-bold">{txn?.accountId || "ACC-89104"}</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-1">Mã Đơn Vị (Merchant)</span>
                <span className="font-mono text-white font-bold">{txn?.merchantId || "MERCH-VN-92"}</span>
              </div>
              <div>
                <span className="text-slate-400 block mb-1">Trạng Thái Ca</span>
                <span className="font-mono px-2.5 py-0.5 rounded-full bg-[#30adcd]/15 text-[#30adcd] border border-[#30adcd]/30 font-bold">
                  {fraudCase.status}
                </span>
              </div>
            </div>
          </div>

          {/* SHAP Chart */}
          <ShapChart features={fraudCase.shapValues || fraudCase.shap_values || []} />

        </div>

        {/* Right Column: Review Submission Form */}
        <div className="glass-panel p-6 rounded-3xl border border-[#30adcd]/25 h-fit space-y-5 shadow-glow-blue">
          <div className="flex items-center gap-2 border-b border-[#30adcd]/20 pb-3">
            <ShieldCheck className="w-5 h-5 text-[#30adcd]" />
            <h2 className="text-base font-bold text-white">
              Quyết Định Thẩm Định
            </h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            
            <div className="space-y-2">
              <label className="text-xs font-bold uppercase tracking-wider text-[#30adcd] block">
                Chọn Kết Quả Phê Duyệt
              </label>
              <div className="space-y-2.5">
                <button
                  type="button"
                  disabled={!isAnalyst}
                  onClick={() => setDecision("CONFIRMED_FRAUD")}
                  className={`w-full flex items-center gap-3 p-3.5 rounded-2xl border text-xs font-bold transition-all disabled:opacity-50 ${
                    decision === "CONFIRMED_FRAUD"
                      ? "bg-[#d1556c]/20 border-[#d1556c] text-[#faeef0] shadow-glow-red"
                      : "bg-[#080C14] border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  <AlertTriangle className="w-4 h-4 text-[#d1556c]" />
                  Xác Nhận Gian Lận (Confirmed Fraud)
                </button>

                <button
                  type="button"
                  disabled={!isAnalyst}
                  onClick={() => setDecision("LEGITIMATE")}
                  className={`w-full flex items-center gap-3 p-3.5 rounded-2xl border text-xs font-bold transition-all disabled:opacity-50 ${
                    decision === "LEGITIMATE"
                      ? "bg-[#2cb285]/20 border-[#2cb285] text-[#eaf7f3] shadow-glow-green"
                      : "bg-[#080C14] border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  <CheckCircle2 className="w-4 h-4 text-[#2cb285]" />
                  Giao Dịch Hợp Lệ (Legitimate)
                </button>

                <button
                  type="button"
                  disabled={!isAnalyst}
                  onClick={() => setDecision("NEED_MORE_INFO")}
                  className={`w-full flex items-center gap-3 p-3.5 rounded-2xl border text-xs font-bold transition-all disabled:opacity-50 ${
                    decision === "NEED_MORE_INFO"
                      ? "bg-[#f4d4b2]/20 border-[#b79f86] text-[#fefbf7]"
                      : "bg-[#080C14] border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  <HelpCircle className="w-4 h-4 text-[#f4d4b2]" />
                  Cần Thêm Thông Tin / Escalate
                </button>
              </div>
            </div>

            {/* Textarea Reason */}
            <div className="space-y-1.5">
              <label className="text-xs font-bold uppercase tracking-wider text-[#30adcd] block">
                Lý Do Giải Trình (Audit Trail) <span className="text-[#d1556c]">*</span>
              </label>
              <textarea
                rows={4}
                disabled={!isAnalyst}
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Nhập căn cứ phân tích dựa trên sự đóng góp đặc trưng SHAP..."
                className="w-full p-3.5 rounded-2xl bg-[#080C14] border border-[#30adcd]/25 text-white text-xs focus:outline-none focus:border-[#30adcd] shadow-inner disabled:opacity-50"
              />
              <span className="text-[11px] text-slate-400 block text-right font-mono">Tối thiểu 10 ký tự</span>
            </div>

            {errorMsg && (
              <div className="p-3 rounded-xl bg-[#d1556c]/15 border border-[#d1556c]/40 text-[#faeef0] text-xs font-bold">
                {errorMsg}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting || !isAnalyst}
              className="w-full flex items-center justify-center gap-2 py-3.5 rounded-2xl bg-[#30adcd] hover:bg-[#2b9cb9] text-white font-bold text-xs shadow-glow-blue transition-all disabled:opacity-50 cursor-pointer disabled:cursor-not-allowed"
            >
              {!isAnalyst ? (
                <>
                  <Lock className="w-4 h-4" /> Chỉ Analyst Mới Có Quyền Phê Duyệt
                </>
              ) : submitting ? (
                "Đang Gửi..."
              ) : (
                <>
                  <Send className="w-4 h-4" /> Xác Nhận & Ghi Nhật Ký
                </>
              )}
            </button>

          </form>

        </div>

      </div>

    </div>
  );
}
