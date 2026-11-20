"use client";

import "@/lib/suppress-hydration";
import React, { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { fetchFraudCases } from "@/lib/api";
import { FraudCase, RiskLevel } from "@/types/fraud.types";
import { RiskBadge } from "@/components/RiskBadge";
import { useNotification } from "@/components/NotificationProvider";
import { PaySimSimulatorModal } from "@/components/PaySimSimulatorModal";
import { RefreshCw, ChevronRight, ChevronLeft, ShieldAlert, Clock, Filter, CreditCard, Zap } from "lucide-react";

/**
 * {
 *   func   : AnalystQueuePage
 *   desc   : Hang doi Review gian lan Keyset Pagination O(1) tich hop PaySim Stream Simulator
 *   input  : None
 *   output : JSX.Element
 *   loop   : 1 loop — duyet danh sach ca rui ro trong trang
 * }
 */
export default function AnalystQueuePage() {
  const [cases, setCases] = useState<FraudCase[]>([]);
  const [loading, setLoading] = useState(true);
  const [levelFilter, setLevelFilter] = useState<string>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("OPEN");
  
  const [currentCursor, setCurrentCursor] = useState<string | null>(null);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [cursorHistory, setCursorHistory] = useState<(string | null)[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [simulatorOpen, setSimulatorOpen] = useState(false);

  const { showNotification } = useNotification();

  const loadData = useCallback(async (cursor: string | null = null, isManual = false) => {
    setLoading(true);
    try {
      const res = await fetchFraudCases(levelFilter, statusFilter, cursor, 15);
      setCases(res.items);
      setNextCursor(res.next_cursor);
      setHasMore(res.has_more);
      setTotalCount(res.total_count || res.items.length);
      setCurrentCursor(cursor);

      if (isManual) {
        showNotification("info", "Đồng Bộ Hàng Đợi", `Đã tải lại ${res.items.length} ca rủi ro qua Cursor Keyset.`);
      }
    } catch (err) {
      showNotification("error", "Lỗi Đồng Bộ", "Không thể kết nối đến máy chủ API.");
    } finally {
      setLoading(false);
    }
  }, [levelFilter, statusFilter, showNotification]);

  useEffect(() => {
    setCursorHistory([]);
    loadData(null, false);
  }, [levelFilter, statusFilter, loadData]);

  const handleNextPage = () => {
    if (!nextCursor || !hasMore) return;
    setCursorHistory((prev) => [...prev, currentCursor]);
    loadData(nextCursor, false);
  };

  const handlePrevPage = () => {
    if (cursorHistory.length === 0) return;
    const prevCursor = cursorHistory[cursorHistory.length - 1];
    setCursorHistory((prev) => prev.slice(0, prev.length - 1));
    loadData(prevCursor, false);
  };

  const handleResetCursor = () => {
    setCursorHistory([]);
    loadData(null, true);
  };

  return (
    <div className="space-y-6" suppressHydrationWarning>
      
      {/* Header Bar */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-5 glass-panel p-6 sm:p-8 rounded-3xl border border-[#30adcd]/25 shadow-glow-blue">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-[#30adcd]/20 border border-[#30adcd]/40 flex items-center justify-center shadow-md">
              <ShieldAlert className="w-5 h-5 text-[#30adcd]" />
            </div>
            <div>
              <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
                Fraud Review Queue
                <span className="w-2 h-2 rounded-full bg-[#30adcd] animate-pulse" />
              </h1>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[11px] font-mono font-bold text-[#2cb285] bg-[#2cb285]/15 px-2.5 py-0.5 rounded-full border border-[#2cb285]/30 flex items-center gap-1">
                  <Zap className="w-3 h-3" /> Cursor Keyset: O(1) Index Seek
                </span>
                <span className="text-xs text-slate-400">Tổng số: {totalCount} ca trong CSDL</span>
              </div>
            </div>
          </div>
        </div>

        {/* Filter Toolbar & PaySim Trigger */}
        <div className="flex flex-wrap items-center gap-3">
          
          {/* Level Filter */}
          <div className="flex items-center bg-[#080C14] p-1.5 rounded-2xl border border-[#30adcd]/25">
            <Filter className="w-3.5 h-3.5 text-[#30adcd] ml-2 mr-1" />
            {["ALL", "HIGH", "MEDIUM", "LOW"].map((lvl) => (
              <button
                key={lvl}
                onClick={() => setLevelFilter(lvl)}
                className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
                  levelFilter === lvl
                    ? "bg-[#30adcd] text-white shadow-glow-blue"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {lvl}
              </button>
            ))}
          </div>

          {/* Status Filter */}
          <div className="flex items-center bg-[#080C14] p-1.5 rounded-2xl border border-[#30adcd]/25">
            {["OPEN", "CLOSED", "ALL"].map((st) => (
              <button
                key={st}
                onClick={() => setStatusFilter(st)}
                className={`px-3 py-1 rounded-xl text-xs font-bold transition-all ${
                  statusFilter === st
                    ? "bg-[#565ac4] text-white shadow-glow-purple"
                    : "text-slate-400 hover:text-white"
                }`}
              >
                {st}
              </button>
            ))}
          </div>

          {/* PaySim Simulator Trigger Button */}
          <button
            onClick={() => setSimulatorOpen(true)}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-gradient-to-r from-[#30adcd] to-[#2cb285] text-white rounded-2xl text-xs font-bold transition-all shadow-glow-blue cursor-pointer"
          >
            <Zap className="w-3.5 h-3.5 fill-white" />
            Bắn PaySim
          </button>

          {/* Refresh Button */}
          <button
            onClick={handleResetCursor}
            disabled={loading}
            className="flex items-center gap-2 px-3.5 py-2 bg-[#080C14] hover:bg-[#30adcd]/15 text-[#30adcd] border border-[#30adcd]/30 rounded-2xl text-xs font-bold transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} />
            Làm Mới
          </button>

        </div>
      </div>

      {/* Cases Table */}
      <div className="glass-panel rounded-3xl overflow-hidden border border-[#30adcd]/25 shadow-glow-blue">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-[#080C14]/90 text-xs uppercase tracking-wider text-[#30adcd] font-bold border-b border-[#30adcd]/20 font-sans">
              <tr>
                <th className="px-6 py-4">Mã Giao Dịch</th>
                <th className="px-6 py-4">Mức Rủi Ro</th>
                <th className="px-6 py-4">Số Tiền (VND)</th>
                <th className="px-6 py-4">Kênh</th>
                <th className="px-6 py-4">Trạng Thái</th>
                <th className="px-6 py-4">Thời Gian</th>
                <th className="px-6 py-4 text-right">Thao Tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#113d48]/60 font-mono text-xs" suppressHydrationWarning>
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-14 text-center text-slate-400 font-sans">
                    <div className="flex items-center justify-center gap-2">
                      <RefreshCw className="w-4 h-4 animate-spin text-[#30adcd]" />
                      Đang truy vấn hàng đợi rủi ro qua Keyset Cursor...
                    </div>
                  </td>
                </tr>
              ) : cases.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-14 text-center text-slate-400 font-sans">
                    Không có ca rủi ro nào phù hợp với bộ lọc hiện tại.
                  </td>
                </tr>
              ) : (
                /* { loop-1: hien thi tung hang trong bang } */
                cases.map((c) => {
                  const txnId = c.transactionId || c.transaction_id || `TXN-${c.id.slice(0, 8)}`;
                  const rLevel = (c.riskLevel || c.risk_level || "HIGH") as RiskLevel;
                  const rScore = c.riskScore ?? c.risk_score ?? 85;
                  const createdStr = c.createdAt || c.created_at || c.transaction?.createdAt || c.transaction?.created_at;
                  const validTime = createdStr && !isNaN(new Date(createdStr).getTime())
                    ? new Date(createdStr).toLocaleTimeString()
                    : "Vừa xong";
                  const amount = Number(c.transaction?.amount ?? 0);
                  const currency = c.transaction?.currency || "VND";
                  const channel = c.transaction?.channel || "MOBILE";

                  return (
                    <tr key={c.id} className="hover:bg-[#30adcd]/5 transition-colors group">
                      <td className="px-6 py-4 font-bold text-white flex items-center gap-2">
                        <CreditCard className="w-3.5 h-3.5 text-[#30adcd]" />
                        {txnId}
                      </td>
                      <td className="px-6 py-4 font-sans">
                        <RiskBadge level={rLevel} score={rScore} />
                      </td>
                      <td className="px-6 py-4 font-bold text-[#30adcd] text-sm" suppressHydrationWarning>
                        {amount.toLocaleString("vi-VN")} {currency}
                      </td>
                      <td className="px-6 py-4 text-slate-300 font-sans">
                        <span className="px-2.5 py-1 rounded-lg bg-[#080C14] border border-[#30adcd]/20 text-[11px] font-semibold text-slate-300">
                          {channel}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-sans">
                        <span className={`px-2.5 py-1 rounded-full text-[11px] font-bold border ${
                          c.status === "OPEN"
                            ? "bg-[#f4d4b2]/15 text-[#fefbf7] border-[#b79f86]/40"
                            : "bg-slate-800 text-slate-400 border-slate-700"
                        }`}>
                          {c.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-slate-400 font-sans flex items-center gap-1.5" suppressHydrationWarning>
                        <Clock className="w-3.5 h-3.5 text-[#30adcd]/70" />
                        {validTime}
                      </td>
                      <td className="px-6 py-4 text-right font-sans">
                        <Link
                          href={`/analyst/${c.id}`}
                          className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-[#30adcd]/20 text-[#eaf7fa] border border-[#30adcd]/40 hover:bg-[#30adcd] hover:text-white transition-all text-xs font-bold shadow-sm"
                        >
                          Kiểm Tra Ca
                          <ChevronRight className="w-3.5 h-3.5" />
                        </Link>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Cursor Keyset Pagination Bar */}
        <div className="p-4 sm:p-5 bg-[#080C14]/90 border-t border-[#30adcd]/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="text-xs text-slate-400 flex items-center gap-2 font-mono">
            <span>Trang hiện tại: <strong className="text-white">#{cursorHistory.length + 1}</strong></span>
            <span>•</span>
            <span>Hiển thị: <strong className="text-[#30adcd]">{cases.length} ca</strong></span>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={handlePrevPage}
              disabled={cursorHistory.length === 0 || loading}
              className="flex items-center gap-1.5 px-4 py-2 bg-[#080C14] hover:bg-[#30adcd]/15 text-slate-300 hover:text-white border border-[#30adcd]/30 rounded-xl text-xs font-bold transition-all disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              <ChevronLeft className="w-3.5 h-3.5" /> Trang Trước
            </button>

            <button
              onClick={handleNextPage}
              disabled={!hasMore || loading}
              className="flex items-center gap-1.5 px-4 py-2 bg-[#30adcd] hover:bg-[#2b9cb9] text-white border border-[#30adcd] rounded-xl text-xs font-bold transition-all shadow-glow-blue disabled:opacity-40 disabled:cursor-not-allowed cursor-pointer"
            >
              Trang Kế Tiếp <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

      </div>

      {/* PaySim Simulator Modal */}
      <PaySimSimulatorModal
        isOpen={simulatorOpen}
        onClose={() => setSimulatorOpen(false)}
        onSuccess={() => handleResetCursor()}
      />

    </div>
  );
}
