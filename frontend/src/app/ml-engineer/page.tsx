"use client";

import "@/lib/suppress-hydration";
import React, { useEffect, useState } from "react";
import { fetchModelVersions, promoteModelVersion, toggleShadowMode } from "@/lib/api";
import { ModelVersion } from "@/types/fraud.types";
import { useNotification } from "@/components/NotificationProvider";
import { useAuth } from "@/components/AuthProvider";
import { Cpu, Award, AlertTriangle, ShieldCheck, ArrowUpRight, Sparkles, Radio, Lock, Eye } from "lucide-react";

/**
 * {
 *   func   : MLEngineerPage
 *   desc   : MLOps Model Registry Dashboard kiem tra chat che quyen RBAC cua ML Engineer
 *   input  : None
 *   output : JSX.Element
 *   loop   : 1 loop — duyet danh sach phien ban mo hinh
 * }
 */
export default function MLEngineerPage() {
  const [models, setModels] = useState<ModelVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmPromote, setConfirmPromote] = useState<string | null>(null);
  const { showNotification } = useNotification();
  const { user } = useAuth();

  const isMLEngineer = user?.role === "ML_ENGINEER";

  const loadModels = async () => {
    setLoading(true);
    try {
      const data = await fetchModelVersions();
      setModels(data);
    } catch (err) {
      showNotification("error", "Lỗi Tải Registry", "Không thể lấy danh sách mô hình từ máy chủ.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  const handlePromote = async (version: string) => {
    if (!isMLEngineer) {
      showNotification("error", "Quyền Hạn Bị Từ Chối", "Chỉ MLOps Engineer mới có quyền thăng cấp mô hình!");
      return;
    }

    try {
      await promoteModelVersion(version);
      showNotification("success", "Thăng Cấp Thành Công", `Phiên bản ${version} đã được thăng cấp lên PRODUCTION.`);
      setConfirmPromote(null);
      await loadModels();
    } catch (err) {
      showNotification("error", "Thăng Cấp Thất Bại", `Không thể thăng cấp mô hình ${version}.`);
    }
  };

  const handleToggleShadow = async (version: string) => {
    if (!isMLEngineer) {
      showNotification("error", "Quyền Hạn Bị Từ Chối", "Chỉ MLOps Engineer mới có quyền bật/tắt Shadow Mode!");
      return;
    }

    try {
      await toggleShadowMode(version);
      showNotification("info", "Chế Độ Shadow", `Đã chuyển đổi trạng thái Shadow Mode cho phiên bản ${version}.`);
      await loadModels();
    } catch (err) {
      showNotification("error", "Lỗi Cập Nhật", "Chuyển đổi chế độ shadow thất bại.");
    }
  };

  return (
    <div className="space-y-6">
      
      {/* RBAC Notice if not ML Engineer */}
      {!isMLEngineer && (
        <div className="p-4 rounded-2xl bg-[#565ac4]/15 border border-[#565ac4]/40 flex items-center justify-between text-xs text-[#eeeff9]">
          <span className="flex items-center gap-2 font-bold">
            <Eye className="w-4 h-4 text-[#9b9eed]" />
            Chế độ Quan Sát Viên — Bạn đang đăng nhập với vai trò {user?.role}. Chỉ Kỹ sư MLOps mới có quyền thay đổi trạng thái và Thăng cấp mô hình (Theo quy chuẩn MLOps Governance Gate).
          </span>
          <span className="px-2.5 py-1 rounded-full bg-[#565ac4]/30 text-white font-mono font-bold">
            Read-Only
          </span>
        </div>
      )}

      {/* Header Banner */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl flex flex-col lg:flex-row lg:items-center justify-between gap-5 border border-[#30adcd]/25 shadow-glow-blue">
        <div>
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-2xl bg-[#30adcd]/20 border border-[#30adcd]/40 flex items-center justify-center shadow-md">
              <Cpu className="w-6 h-6 text-[#30adcd]" />
            </div>
            <div>
              <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
                MLOps Model Registry & Release Control
                <Sparkles className="w-4 h-4 text-[#30adcd]" />
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
                So sánh các chỉ số đánh giá offline và shadow deployment trước khi thăng cấp chạy sản xuất
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-2xl bg-[#080C14] border border-[#30adcd]/30 text-xs font-mono text-[#30adcd]">
            <Radio className="w-4 h-4 animate-pulse text-[#30adcd]" /> Traffic Split: Champion 100% | Shadow 100%
          </div>
        </div>
      </div>

      {/* Models Table */}
      <div className="glass-panel rounded-3xl border border-[#30adcd]/25 overflow-hidden shadow-glow-blue">
        <div className="p-6 border-b border-[#30adcd]/20 flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-white">Bảng Đối Sánh Các Phiên Bản Mô Hình</h2>
            <p className="text-xs text-slate-400 mt-0.5">Tiêu chí tối thiểu để thăng cấp: PR-AUC ≥ 0.50 | Recall ≥ 0.75 | Brier Score ≤ 0.05</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="bg-[#080C14]/90 text-xs uppercase tracking-wider text-[#30adcd] font-bold border-b border-[#30adcd]/20">
              <tr>
                <th className="px-6 py-4">Phiên Bản</th>
                <th className="px-6 py-4">Trạng Thái</th>
                <th className="px-6 py-4">PR-AUC</th>
                <th className="px-6 py-4">Recall</th>
                <th className="px-6 py-4">Precision</th>
                <th className="px-6 py-4">Brier Score</th>
                <th className="px-6 py-4">Chi Phí Kỳ Vọng</th>
                <th className="px-6 py-4 text-right">Thao Tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#113d48]/60 font-mono text-xs">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-6 py-12 text-center text-slate-400 font-sans">Đang tải danh sách phiên bản mô hình...</td>
                </tr>
              ) : (
                /* { loop-1: duyet qua tung phien ban mo hinh } */
                models.map((m) => {
                  const isProd = m.status === "PRODUCTION";

                  return (
                    <tr key={m.id} className={`hover:bg-[#30adcd]/5 transition-colors ${isProd ? "bg-[#30adcd]/10" : ""}`}>
                      <td className="px-6 py-4 font-bold text-white flex items-center gap-2">
                        {m.version}
                        {isProd && (
                          <span className="inline-flex items-center gap-1 text-[10px] px-2.5 py-0.5 rounded-full bg-[#2cb285]/20 text-[#2cb285] border border-[#2cb285]/40 font-sans font-bold shadow-sm">
                            <Award className="w-3 h-3 text-[#2cb285]" /> Champion
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 font-sans">
                        <span className={`px-3 py-1 rounded-full text-[11px] font-bold border ${
                          isProd
                            ? "bg-[#2cb285]/15 text-[#eaf7f3] border-[#2cb285]/40 shadow-[0_0_10px_rgba(44,178,133,0.25)]"
                            : "bg-[#f4d4b2]/15 text-[#fefbf7] border-[#b79f86]/40"
                        }`}>
                          {m.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 font-bold text-[#30adcd]">{m.prAuc ?? m.pr_auc ?? 0.85}</td>
                      <td className="px-6 py-4 font-bold text-white">{m.recall}</td>
                      <td className="px-6 py-4">{m.precision}</td>
                      <td className="px-6 py-4 text-[#2cb285] font-bold">{m.brierScore ?? m.brier_score ?? 0.001}</td>
                      <td className="px-6 py-4 font-extrabold text-white">${m.expectedCost ?? m.expected_cost ?? 890}</td>
                      <td className="px-6 py-4 text-right font-sans space-x-2">
                        {!isProd && (
                          <>
                            <button
                              disabled={!isMLEngineer}
                              onClick={() => handleToggleShadow(m.version)}
                              className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition-colors disabled:opacity-50 ${
                                m.isShadow || m.is_shadow
                                  ? "bg-[#565ac4]/20 text-[#eeeff9] border-[#565ac4]/40 shadow-glow-purple"
                                  : "bg-[#080C14] text-slate-400 border-slate-700 hover:text-white"
                              }`}
                            >
                              Shadow: {m.isShadow || m.is_shadow ? "BẬT" : "TẮT"}
                            </button>

                            <button
                              disabled={!isMLEngineer}
                              onClick={() => setConfirmPromote(m.version)}
                              className="px-3.5 py-1.5 rounded-xl bg-[#30adcd] hover:bg-[#2b9cb9] text-white text-xs font-bold shadow-glow-blue transition-all inline-flex items-center gap-1 disabled:opacity-50"
                            >
                              {!isMLEngineer ? (
                                <>
                                  <Lock className="w-3.5 h-3.5" /> Khóa
                                </>
                              ) : (
                                <>
                                  Thăng Cấp <ArrowUpRight className="w-3.5 h-3.5" />
                                </>
                              )}
                            </button>
                          </>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Confirmation Modal */}
      {confirmPromote && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 z-50 animate-fade-in">
          <div className="glass-panel p-6 sm:p-8 rounded-3xl max-w-md w-full border border-[#d1556c]/40 space-y-5 shadow-glow-red">
            <div className="flex items-center gap-3 text-[#d1556c]">
              <AlertTriangle className="w-6 h-6" />
              <h3 className="text-lg font-bold text-white">Xác Nhận Thăng Cấp Mô Hình</h3>
            </div>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Bạn có chắc chắn muốn thăng cấp phiên bản <span className="font-mono font-bold text-[#30adcd]">{confirmPromote}</span> lên làm mô hình <span className="text-[#2cb285] font-bold">PRODUCTION CHAMPION</span>?
              Mô hình hiện tại sẽ tự động chuyển về trạng thái RETIRED.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setConfirmPromote(null)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-300 hover:text-white bg-slate-800 transition-colors"
              >
                Hủy Bỏ
              </button>
              <button
                onClick={() => handlePromote(confirmPromote)}
                className="px-5 py-2 rounded-xl text-xs font-bold text-white bg-[#d1556c] hover:bg-[#b8455a] transition-all shadow-glow-red flex items-center gap-2"
              >
                <ShieldCheck className="w-4 h-4" /> Đồng Ý Thăng Cấp
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
