"use client";

import React from "react";
import { ShapFeature } from "@/types/fraud.types";
import { Info, TrendingUp, TrendingDown, Sparkles } from "lucide-react";

interface ShapChartProps {
  features: ShapFeature[];
}

/**
 * {
 *   func   : ShapChart
 *   desc   : Bieu do SHAP su dung bang ma mau Blue #30adcd va Red #d1556c chuan thiet ke
 *   input  : features (ShapFeature[])
 *   output : JSX.Element
 *   loop   : 1 loop — anh xa cac dac trung thanh thanh bieu do
 * }
 */
export const ShapChart: React.FC<ShapChartProps> = ({ features }) => {
  if (!features || features.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400 text-sm glass-card rounded-2xl border border-[#30adcd]/20">
        <Info className="w-6 h-6 text-[#30adcd] mx-auto mb-2 opacity-60" />
        Chưa có dữ liệu giải thích đặc trưng SHAP cho giao dịch này.
      </div>
    );
  }

  const sorted = [...features].sort((a, b) => Math.abs(b.shapValue) - Math.abs(a.shapValue)).slice(0, 10);
  const maxAbsShap = Math.max(...sorted.map((f) => Math.abs(f.shapValue)), 0.01);

  return (
    <div className="glass-panel rounded-2xl p-6 border border-[#30adcd]/25 space-y-5 shadow-glow-blue">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-[#30adcd]/20 pb-4 gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-[#30adcd]/20 border border-[#30adcd]/40 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-[#30adcd]" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white">
              Top 10 Đặc Trưng SHAP Đóng Góp Lớn Nhất
            </h3>
            <p className="text-[11px] text-slate-400">TreeExplainer Model Interpretability</p>
          </div>
        </div>
        
        <div className="flex items-center gap-3 text-xs">
          <span className="flex items-center gap-1.5 text-[#d1556c] font-semibold bg-[#d1556c]/15 px-2.5 py-1 rounded-lg border border-[#d1556c]/30">
            <TrendingUp className="w-3.5 h-3.5" /> Tăng rủi ro (+SHAP)
          </span>
          <span className="flex items-center gap-1.5 text-[#30adcd] font-semibold bg-[#30adcd]/15 px-2.5 py-1 rounded-lg border border-[#30adcd]/30">
            <TrendingDown className="w-3.5 h-3.5" /> Giảm rủi ro (-SHAP)
          </span>
        </div>
      </div>

      <div className="space-y-3.5">
        {/* { loop-1: hien thi tung thanh do thi luc SHAP } */}
        {sorted.map((item, idx) => {
          const isIncrease = item.shapValue >= 0;
          const barWidthPercent = Math.min(100, Math.round((Math.abs(item.shapValue) / maxAbsShap) * 100));

          return (
            <div key={idx} className="group relative flex flex-col gap-1.5 text-xs">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-200 group-hover:text-[#30adcd] transition-colors flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#30adcd]" />
                  {item.label || item.featureName}
                  <span className="text-slate-400 font-mono text-[11px]">({item.featureName} = <strong className="text-[#30adcd]">{item.featureValue}</strong>)</span>
                </span>
                <span className={`font-mono font-bold text-xs ${isIncrease ? "text-[#d1556c]" : "text-[#30adcd]"}`}>
                  {isIncrease ? "+" : ""}{item.shapValue.toFixed(4)}
                </span>
              </div>

              {/* Thanh tien trinh phat sang theo bang ma mau */}
              <div className="w-full bg-[#080C14] h-3 rounded-full overflow-hidden border border-[#113d48] p-0.5">
                <div
                  className={`h-full transition-all duration-500 rounded-full ${
                    isIncrease
                      ? "bg-gradient-to-r from-[#9d4051] to-[#d1556c] shadow-[0_0_12px_rgba(209,85,108,0.5)]"
                      : "bg-gradient-to-r from-[#24829a] to-[#30adcd] shadow-[0_0_12px_rgba(48,173,205,0.5)]"
                  }`}
                  style={{ width: `${Math.max(6, barWidthPercent)}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
