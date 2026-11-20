"use client";

import "@/lib/suppress-hydration";
import React from "react";
import Link from "next/link";
import {
  ShieldAlert, BarChart3, Cpu, Sparkles, ArrowRight, Zap, Database, Lock, Layers, CheckCircle2, Award
} from "lucide-react";

/**
 * {
 *   func   : HomePage
 *   desc   : Cong Kien Truc Tong Hanh Dinh (Landing & Architecture Overview Portal) cho buoi bao ve do an
 *   input  : None
 *   output : JSX.Element
 *   loop   : 2 loops — duyet qua 3 cong vai tro & 4 tang kien truc
 * }
 */
export default function HomePage() {
  const roleGateways = [
    {
      title: "Chuyên Viên Thẩm Định",
      role: "Fraud Analyst",
      href: "/analyst",
      icon: ShieldAlert,
      color: "border-[#30adcd]/40 hover:border-[#30adcd] shadow-glow-blue",
      btnBg: "bg-[#30adcd] hover:bg-[#2b9cb9] text-white",
      badge: "Tác Nghiệp Tuyến 1",
      desc: "Hàng đợi phân loại rủi ro Keyset Cursor O(1), phân tích hồ sơ giao dịch và đọc giải thích đặc trưng SHAP TreeExplainer.",
    },
    {
      title: "Giám Đốc Quản Trị Rủi Ro",
      role: "Risk Manager",
      href: "/manager",
      icon: BarChart3,
      color: "border-[#2cb285]/40 hover:border-[#2cb285] shadow-glow-green",
      btnBg: "bg-[#2cb285] hover:bg-[#259b73] text-white",
      badge: "Giám Sát Chiến Lược",
      desc: "Theo dõi KPI thời gian thực, kiểm soát Fraud Rate ≤ 2.0%, FP Rate ≤ 8.0% và xuất báo cáo kiểm toán CSV chỉ với 1-click.",
    },
    {
      title: "Kỹ Sư Học Máy MLOps",
      role: "MLOps Engineer",
      href: "/ml-engineer",
      icon: Cpu,
      color: "border-[#565ac4]/40 hover:border-[#565ac4] shadow-glow-purple",
      btnBg: "bg-[#565ac4] hover:bg-[#484cb3] text-white",
      badge: "Hạ Tầng Kỹ Thuật AI",
      desc: "Quản lý Model Registry, đối sánh Champion vs Candidate, kích hoạt Shadow Mode và thăng cấp an toàn Zero-Downtime.",
    },
  ];

  const architectureLayers = [
    {
      step: "01",
      title: "Data Streaming Ingestion",
      desc: "Apache Kafka tiếp nhận luồng giao dịch PaySim (2.77M dòng) với lưu lượng hàng nghìn TPS.",
      icon: Zap,
    },
    {
      step: "02",
      title: "Real-Time Feature Store",
      desc: "Trích xuất 8 nhóm đặc trưng (Velocity 5m/1h, Novelty thiết bị, Tỷ lệ chi tiêu) trong dưới 10ms.",
      icon: Database,
    },
    {
      step: "03",
      title: "Hybrid ML Risk Engine",
      desc: "XGBoost (Supervised) + Isolation Forest (Anomaly Detection) + Platt Scaling đạt Brier Score ≤ 0.05.",
      icon: Cpu,
    },
    {
      step: "04",
      title: "HITL & MLOps Governance",
      desc: "Hàng đợi thẩm định Human-in-the-Loop, giải thích SHAP XAI và quy trình thăng cấp mô hình 2 bước.",
      icon: Layers,
    },
  ];

  return (
    <div className="space-y-12 pb-8">
      
      {/* Hero Header */}
      <div className="text-center space-y-5 max-w-4xl mx-auto pt-4">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#30adcd]/15 border border-[#30adcd]/30 text-[#30adcd] text-xs font-bold shadow-glow-blue">
          <Sparkles className="w-4 h-4" /> SentinelRisk AI • Real-Time Fraud & Transaction Risk Detection Platform
        </div>
        
        <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
          Nền Tảng Phát Hiện Gian Lận <br className="hidden sm:inline" />
          <span className="bg-gradient-to-r from-[#30adcd] via-[#eaf7fa] to-[#565ac4] bg-clip-text text-transparent">
            Thời Gian Thực & MLOps v2.0
          </span>
        </h1>
        
        <p className="text-sm sm:text-base text-slate-300 max-w-2xl mx-auto leading-relaxed">
          Kiến trúc Hybrid Machine Learning kết hợp AI giải thích được (SHAP XAI), xử lý dòng Kafka với độ trễ P95 &lt; 100ms và phân quyền 3 tầng vai trò chuẩn ngân hàng.
        </p>

        <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
          <Link
            href="/analyst"
            className="px-6 py-3 rounded-2xl bg-[#30adcd] hover:bg-[#2b9cb9] text-white font-bold text-xs shadow-glow-blue transition-all flex items-center gap-2"
          >
            Vào Hàng Đợi Thẩm Định <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            href="/login"
            className="px-6 py-3 rounded-2xl bg-[#080C14] hover:bg-[#30adcd]/15 border border-[#30adcd]/30 text-white font-bold text-xs shadow-sm transition-all flex items-center gap-2"
          >
            <Lock className="w-4 h-4 text-[#30adcd]" /> Cổng Đăng Nhập JWT
          </Link>
        </div>
      </div>

      {/* 4 Stats Highlights Bar */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        <div className="glass-panel p-5 rounded-3xl border border-[#30adcd]/25 text-center space-y-1 shadow-glow-blue">
          <div className="text-2xl sm:text-3xl font-extrabold text-[#30adcd] font-mono">3.6M+</div>
          <div className="text-xs text-slate-400 font-medium">Bản Ghi Dữ Liệu Huấn Luyện</div>
        </div>
        <div className="glass-panel p-5 rounded-3xl border border-[#2cb285]/25 text-center space-y-1 shadow-glow-green">
          <div className="text-2xl sm:text-3xl font-extrabold text-[#2cb285] font-mono">&lt; 100ms</div>
          <div className="text-xs text-slate-400 font-medium">Độ Trễ Chấm Điểm P95</div>
        </div>
        <div className="glass-panel p-5 rounded-3xl border border-[#565ac4]/25 text-center space-y-1 shadow-glow-purple">
          <div className="text-2xl sm:text-3xl font-extrabold text-[#9b9eed] font-mono">0.9825</div>
          <div className="text-xs text-slate-400 font-medium">PR-AUC Dữ Liệu Mất Cân Bằng</div>
        </div>
        <div className="glass-panel p-5 rounded-3xl border border-[#d1556c]/25 text-center space-y-1 shadow-glow-red">
          <div className="text-2xl sm:text-3xl font-extrabold text-[#faeef0] font-mono">100%</div>
          <div className="text-xs text-slate-400 font-medium">Zero-Downtime MLOps Gate</div>
        </div>
      </div>

      {/* 3 Role Gateways Grid */}
      <div className="space-y-4">
        <div className="text-center space-y-1">
          <h2 className="text-xl sm:text-2xl font-extrabold text-white">3 Cổng Tác Nghiệp Phân Quyền (RBAC)</h2>
          <p className="text-xs sm:text-sm text-slate-400">Chọn vai trò phù hợp để trực tiếp trải nghiệm quy trình vận hành rủi ro</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
          {/* { loop-1: duyet qua 3 the cong vai tro } */}
          {roleGateways.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.role}
                className={`glass-panel p-6 sm:p-7 rounded-3xl border flex flex-col justify-between space-y-5 transition-all duration-300 ${item.color}`}
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="p-3 rounded-2xl bg-white/5 border border-white/10 shadow-sm">
                      <Icon className="w-6 h-6 text-white" />
                    </span>
                    <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-white/10 text-slate-200">
                      {item.badge}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-lg font-extrabold text-white">{item.title}</h3>
                    <span className="text-xs font-mono font-bold text-[#30adcd] block mt-0.5">{item.role}</span>
                  </div>
                  <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
                </div>

                <Link
                  href={item.href}
                  className={`w-full py-3 px-4 rounded-2xl text-xs font-bold transition-all flex items-center justify-center gap-2 shadow-md ${item.btnBg}`}
                >
                  Truy Cập Cổng Điều Hành <ArrowRight className="w-4 h-4" />
                </Link>
              </div>
            );
          })}
        </div>
      </div>

      {/* 4-Layer Architecture Pipeline Overview */}
      <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-[#30adcd]/25 space-y-6 shadow-glow-blue">
        <div className="border-b border-[#30adcd]/20 pb-4 flex items-center justify-between">
          <div>
            <h2 className="text-lg font-extrabold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-[#30adcd]" /> Kiến Trúc Xử Lý 4 Tầng (Clean Architecture)
            </h2>
            <p className="text-xs text-slate-400 mt-1">Từ dữ liệu dòng tốc độ cao đến phán quyết có trách nhiệm và giải thích AI</p>
          </div>
          <span className="hidden sm:inline-flex items-center gap-1.5 text-xs font-bold text-[#2cb285] bg-[#2cb285]/15 px-3 py-1 rounded-full border border-[#2cb285]/30">
            <CheckCircle2 className="w-3.5 h-3.5" /> Chuẩn MLOps Quốc Tế
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* { loop-2: duyet qua 4 tang kien truc } */}
          {architectureLayers.map((layer) => {
            const Icon = layer.icon;
            return (
              <div key={layer.step} className="p-5 rounded-2xl bg-[#080C14] border border-[#30adcd]/20 space-y-3 relative overflow-hidden group hover:border-[#30adcd]/50 transition-all">
                <span className="text-3xl font-black text-[#30adcd]/15 font-mono absolute top-2 right-3">
                  {layer.step}
                </span>
                <div className="w-8 h-8 rounded-xl bg-[#30adcd]/15 border border-[#30adcd]/30 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-[#30adcd]" />
                </div>
                <h3 className="text-sm font-bold text-white">{layer.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{layer.desc}</p>
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
