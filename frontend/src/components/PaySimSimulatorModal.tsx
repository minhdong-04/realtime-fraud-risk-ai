"use client";

import "@/lib/suppress-hydration";
import React, { useState } from "react";
import { simulatePaySimTransactions } from "@/lib/api";
import { useNotification } from "@/components/NotificationProvider";
import {
  Zap, X, Play, RefreshCw, CheckCircle2, AlertTriangle, ShieldCheck, Cpu
} from "lucide-react";

interface PaySimSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

/**
 * {
 *   func   : PaySimSimulatorModal
 *   desc   : Modal ban dong giao dich PaySim, cham diem AI va kiem thu do chinh xac so voi nhan thuc te (Ground Truth)
 *   input  : isOpen (boolean), onClose (function), onSuccess (function)
 *   output : JSX.Element
 *   loop   : 1 loop — duyet danh sach ket qua giao dich vua ban
 * }
 */
export function PaySimSimulatorModal({ isOpen, onClose, onSuccess }: PaySimSimulatorModalProps) {
  const [count, setCount] = useState<number>(5);
  const [fraudOnly, setFraudOnly] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [results, setResults] = useState<any[]>([]);
  const [accuracy, setAccuracy] = useState<number | null>(null);
  const [correctCount, setCorrectCount] = useState<number>(0);

  const { showNotification } = useNotification();

  if (!isOpen) return null;

  const handleSimulate = async () => {
    setLoading(true);
    setResults([]);
    setAccuracy(null);
    try {
      const data = await simulatePaySimTransactions(count, fraudOnly);
      setResults(data.transactions || []);
      setAccuracy(data.accuracy_percentage ?? 100);
      setCorrectCount(data.correct_count ?? data.transactions?.length ?? 0);

      showNotification(
        "success",
        "Kiểm Thử Mô Hình PaySim",
        `Đã nạp ${data.processed_count} giao dịch. Độ chính xác mô hình: ${data.accuracy_percentage}%!`
      );
      if (onSuccess) onSuccess();
    } catch (err: any) {
      showNotification("error", "Lỗi Mô Phỏng", err.message || "Không thể nạp dữ liệu PaySim");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in" suppressHydrationWarning>
      <div className="relative w-full max-w-2xl bg-[#080C14] border-2 border-[#30adcd]/40 rounded-3xl p-6 sm:p-8 shadow-glow-blue space-y-6 overflow-hidden max-h-[90vh] flex flex-col">
        
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#30adcd]/20 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-[#30adcd]/20 border border-[#30adcd]/40 flex items-center justify-center shadow-md">
              <Zap className="w-5 h-5 text-[#30adcd]" />
            </div>
            <div>
              <h2 className="text-lg sm:text-xl font-black text-white flex items-center gap-2">
                PaySim Test & AI Evaluation Engine
              </h2>
              <p className="text-xs text-slate-400">Bắn dòng giao dịch từ tập PaySim (2.77M dòng) và đối chiếu nhãn thực tế</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-all cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Controls */}
        <div className="space-y-4 text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            
            {/* Count Selector */}
            <div className="space-y-2">
              <label className="font-bold text-slate-300">Số lượng giao dịch bắn vào:</label>
              <div className="flex gap-2">
                {[1, 5, 10, 20].map((num) => (
                  <button
                    key={num}
                    onClick={() => setCount(num)}
                    className={`flex-1 py-2 rounded-xl font-bold border transition-all cursor-pointer ${
                      count === num
                        ? "bg-[#30adcd] border-[#30adcd] text-white shadow-glow-blue"
                        : "bg-[#0c1626] border-slate-800 text-slate-400 hover:text-white"
                    }`}
                  >
                    {num} Txns
                  </button>
                ))}
              </div>
            </div>

            {/* Mode Selector */}
            <div className="space-y-2">
              <label className="font-bold text-slate-300">Chế độ mẫu dữ liệu PaySim:</label>
              <div className="flex gap-2">
                <button
                  onClick={() => setFraudOnly(false)}
                  className={`flex-1 py-2 rounded-xl font-bold border transition-all cursor-pointer ${
                    !fraudOnly
                      ? "bg-[#565ac4] border-[#565ac4] text-white shadow-glow-purple"
                      : "bg-[#0c1626] border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  Ngẫu Nhiên (Mixed)
                </button>
                <button
                  onClick={() => setFraudOnly(true)}
                  className={`flex-1 py-2 rounded-xl font-bold border transition-all cursor-pointer ${
                    fraudOnly
                      ? "bg-[#d1556c] border-[#d1556c] text-white shadow-glow-red"
                      : "bg-[#0c1626] border-slate-800 text-slate-400 hover:text-white"
                  }`}
                >
                  🚨 Chỉ Gian Lận (Fraud)
                </button>
              </div>
            </div>

          </div>

          {/* Trigger Button */}
          <button
            onClick={handleSimulate}
            disabled={loading}
            className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-[#30adcd] via-[#2cb285] to-[#565ac4] hover:opacity-95 text-white font-extrabold text-xs shadow-glow-blue transition-all flex items-center justify-center gap-2 disabled:opacity-50 cursor-pointer"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" /> Đang truyền dữ liệu PaySim & Kiểm thử AI...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" /> Bắn & Kiểm Thử {count} Giao Dịch PaySim
              </>
            )}
          </button>
        </div>

        {/* Results Stream Area */}
        {results.length > 0 && (
          <div className="space-y-3 overflow-y-auto flex-1 pr-1">
            
            {/* Accuracy Banner */}
            <div className="p-3.5 rounded-2xl bg-gradient-to-r from-[#2cb285]/20 to-[#30adcd]/20 border border-[#2cb285]/40 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-[#2cb285]" />
                <div>
                  <div className="text-xs font-bold text-white">Độ Chính Xác Mô Hình Trong Đợt Test Này:</div>
                  <div className="text-[11px] text-slate-300 font-sans">
                    Dự đoán đúng <strong className="text-[#2cb285]">{correctCount}/{results.length}</strong> giao dịch PaySim
                  </div>
                </div>
              </div>
              <div className="text-lg font-black text-[#2cb285] font-mono">
                {accuracy}%
              </div>
            </div>

            <div className="space-y-2">
              {/* { loop-1: duyet danh sach ket qua } */}
              {results.map((item, idx) => (
                <div
                  key={idx}
                  className="p-3.5 rounded-2xl bg-[#0c1626] border border-[#30adcd]/20 space-y-2 text-xs font-mono"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <strong className="text-white">{item.transaction_id}</strong>
                      <span className="px-2 py-0.5 rounded-md bg-white/5 text-[10px] text-slate-300 font-sans">
                        {item.channel}
                      </span>
                    </div>
                    <span className="text-[#30adcd] font-bold">
                      {(item.amount || 0).toLocaleString("vi-VN")} VND
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-white/5">
                    {/* Ground truth label */}
                    <div className="flex items-center gap-1 text-[11px] font-sans">
                      <span className="text-slate-400">Nhãn gốc:</span>
                      <strong className={item.is_fraud_label === 1 ? "text-[#d1556c]" : "text-[#2cb285]"}>
                        {item.ground_truth}
                      </strong>
                    </div>

                    {/* AI Score */}
                    <div className="flex items-center gap-1.5 font-sans">
                      <span className="text-slate-400 text-[11px]">AI Dự đoán:</span>
                      <span className={`px-2 py-0.5 rounded-full text-[11px] font-bold ${
                        item.risk_level === "HIGH"
                          ? "bg-[#d1556c]/20 text-[#faeef0] border border-[#d1556c]"
                          : item.risk_level === "MEDIUM"
                          ? "bg-[#f4d4b2]/20 text-[#fefbf7] border border-[#b79f86]"
                          : "bg-[#2cb285]/20 text-[#eaf7f3] border border-[#2cb285]"
                      }`}>
                        {item.risk_score}/100 ({item.risk_level})
                      </span>
                    </div>

                    {/* Status match */}
                    <div className="text-[11px] font-sans">
                      {item.is_correct ? (
                        <span className="text-[#2cb285] font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Đúng
                        </span>
                      ) : (
                        <span className="text-[#d1556c] font-bold flex items-center gap-1">
                          <AlertTriangle className="w-3.5 h-3.5" /> Lệch
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

          </div>
        )}

      </div>
    </div>
  );
}
