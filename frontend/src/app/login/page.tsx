"use client";

import "@/lib/suppress-hydration";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth, DEMO_MODE } from "@/components/AuthProvider";
import { useNotification } from "@/components/NotificationProvider";
import { UserRole } from "@/types/fraud.types";
import { ShieldCheck, Lock, Mail, ArrowRight, UserCheck, BarChart3, Cpu, Sparkles } from "lucide-react";

/**
 * {
 *   func   : LoginPage
 *   desc   : Trang Dang nhap Xac thuc JWT Token va Chuyen doi Vai tro 1-cham (RBAC)
 *   input  : None
 *   output : JSX.Element
 *   loop   : 1 loop — hien thi 3 nut quick login theo vai tro
 * }
 */
export default function LoginPage() {
  const router = useRouter();
  const { login, quickLogin } = useAuth();
  const { showNotification } = useNotification();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const handleManualLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setLoading(true);
    const success = await login(email, password);
    setLoading(false);

    if (success) {
      showNotification("success", "Đăng Nhập Thành Công", `Chào mừng bạn trở lại, ${email}! Mã JWT Token đã được cấp.`);
      if (email.includes("manager")) router.push("/manager");
      else if (email.includes("ml")) router.push("/ml-engineer");
      else router.push("/analyst");
    } else {
      showNotification("error", "Đăng Nhập Thất Bại", "Email hoặc mật khẩu không chính xác.");
    }
  };

  const handleQuickRoleSelect = async (role: UserRole, targetRoute: string, roleName: string) => {
    setLoading(true);
    const success = await quickLogin(role);
    setLoading(false);

    if (success) {
      showNotification("success", `Kích Hoạt Vai Trò: ${roleName}`, "Đã tạo phiên làm việc JWT hợp lệ và cấp quyền RBAC tương ứng.");
      router.push(targetRoute);
    } else {
      showNotification("error", "Lỗi Cấp Quyền", "Không thể tạo phiên làm việc JWT cho vai trò này.");
    }
  };

  const demoRoles = [
    {
      role: "ANALYST" as UserRole,
      title: "Fraud Analyst",
      email: "analyst@fraud-platform.com",
      route: "/analyst",
      icon: UserCheck,
      color: "border-[#30adcd]/40 hover:border-[#30adcd] shadow-glow-blue",
      btnBg: "bg-[#30adcd]/20 text-[#30adcd] hover:bg-[#30adcd] hover:text-white",
      desc: "Kiểm tra hàng đợi, thẩm định ca rủi ro và xem giải thích SHAP",
    },
    {
      role: "MANAGER" as UserRole,
      title: "Risk Manager",
      email: "manager@fraud-platform.com",
      route: "/manager",
      icon: BarChart3,
      color: "border-[#2cb285]/40 hover:border-[#2cb285] shadow-glow-green",
      btnBg: "bg-[#2cb285]/20 text-[#2cb285] hover:bg-[#2cb285] hover:text-white",
      desc: "Theo dõi KPI thời gian thực, Fraud Rate, FPR và xuất báo cáo CSV",
    },
    {
      role: "ML_ENGINEER" as UserRole,
      title: "MLOps Engineer",
      email: "mlengineer@fraud-platform.com",
      route: "/ml-engineer",
      icon: Cpu,
      color: "border-[#565ac4]/40 hover:border-[#565ac4] shadow-glow-purple",
      btnBg: "bg-[#565ac4]/20 text-[#9b9eed] hover:bg-[#565ac4] hover:text-white",
      desc: "Quản lý Model Registry, đối sánh Champion vs Candidate và Promote",
    },
  ];

  return (
    <div className="min-h-[80vh] flex flex-col items-center justify-center p-4">
      
      <div className="w-full max-w-4xl space-y-8">
        
        {/* Header Title */}
        <div className="text-center space-y-3">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[#30adcd]/15 border border-[#30adcd]/30 text-[#30adcd] text-xs font-bold shadow-glow-blue">
            <Sparkles className="w-3.5 h-3.5" /> SentinelRisk AI • Hệ Thống Xác Thực & Phân Quyền RBAC
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Đăng Nhập Cổng Điều Hành Rủi Ro
          </h1>
          <p className="text-sm text-slate-400 max-w-lg mx-auto">
            Hệ thống bảo mật ngân hàng sử dụng chuẩn mã hóa JWT Token (HS256) và phân quyền 3 tầng vai trò độc lập
          </p>
        </div>

        {/* 3 Quick Role Switchers */}
        {DEMO_MODE && <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {/* { loop-1: render 3 the chon vai tro demo 1-cham } */}
          {demoRoles.map((item) => {
            const Icon = item.icon;
            return (
              <div
                key={item.role}
                className={`glass-panel p-5 rounded-3xl border transition-all duration-300 flex flex-col justify-between space-y-4 ${item.color}`}
              >
                <div className="space-y-2.5">
                  <div className="flex items-center justify-between">
                    <span className="p-2.5 rounded-2xl bg-white/5 border border-white/10">
                      <Icon className="w-5 h-5 text-white" />
                    </span>
                    <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded-full bg-white/10 text-slate-300 font-bold">
                      {item.role}
                    </span>
                  </div>
                  <h3 className="text-base font-extrabold text-white">{item.title}</h3>
                  <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
                </div>

                <button
                  disabled={loading}
                  onClick={() => handleQuickRoleSelect(item.role, item.route, item.title)}
                  className={`w-full py-2.5 px-4 rounded-2xl text-xs font-bold transition-all flex items-center justify-center gap-2 ${item.btnBg}`}
                >
                  Đăng Nhập 1-Chạm <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })}
        </div>}

        {/* Manual Login Form */}
        <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-[#30adcd]/25 max-w-md mx-auto shadow-glow-blue space-y-5">
          <div className="border-b border-[#30adcd]/20 pb-3 flex items-center gap-2 text-sm font-bold text-white">
            <Lock className="w-4 h-4 text-[#30adcd]" /> Đăng Nhập Thủ Công Bằng Tài Khoản
          </div>

          <form onSubmit={handleManualLogin} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Địa chỉ Email</label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="analyst@fraud-platform.com"
                  className="w-full bg-[#080C14] border border-[#30adcd]/30 rounded-2xl py-2.5 pl-10 pr-4 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#30adcd] transition-all"
                  required
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs text-slate-300 font-medium">Mật khẩu xác thực</label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  required
                  className="w-full bg-[#080C14] border border-[#30adcd]/30 rounded-2xl py-2.5 pl-10 pr-4 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-[#30adcd] transition-all"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-[#30adcd] hover:bg-[#2b9cb9] text-white rounded-2xl text-xs font-extrabold shadow-glow-blue transition-all flex items-center justify-center gap-2"
            >
              {loading ? "Đang xác thực JWT..." : "Cấp Quyền & Vào Dashboard"} <ArrowRight className="w-4 h-4" />
            </button>
          </form>
        </div>

      </div>

    </div>
  );
}
