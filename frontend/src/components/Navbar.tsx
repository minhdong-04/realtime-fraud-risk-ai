"use client";

import React, { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useAuth, DEMO_MODE } from "@/components/AuthProvider";
import { useNotification } from "@/components/NotificationProvider";
import { PaySimSimulatorModal } from "@/components/PaySimSimulatorModal";
import { UserRole } from "@/types/fraud.types";
import {
  ShieldAlert, BarChart3, Cpu, UserCheck, Sparkles, Activity, LogOut, ChevronDown, Key, Shield, Zap
} from "lucide-react";

/**
 * {
 *   func   : Navbar
 *   desc   : Thanh dieu huong tich hop Auth Context, Nut Ban PaySim va Switcher JWT dac ro net
 *   input  : None
 *   output : JSX.Element
 *   loop   : 2 loops — duyet cac muc dieu huong & danh sach vai tro
 * }
 */
export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const router = useRouter();
  const { user, quickLogin, logout } = useAuth();
  const { showNotification } = useNotification();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [simulatorOpen, setSimulatorOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Dong dropdown khi bam ra ngoai
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const navItems = [
    { label: "Analyst Queue", href: "/analyst", icon: ShieldAlert },
    { label: "Manager Dashboard", href: "/manager", icon: BarChart3 },
    { label: "ML Engine & MLOps", href: "/ml-engineer", icon: Cpu },
  ];

  const roleOptions: Array<{ role: UserRole; label: string; href: string; color: string; bgBadge: string }> = [
    { role: "ANALYST", label: "Fraud Analyst", href: "/analyst", color: "text-[#30adcd]", bgBadge: "bg-[#30adcd]/20" },
    { role: "MANAGER", label: "Risk Manager", href: "/manager", color: "text-[#2cb285]", bgBadge: "bg-[#2cb285]/20" },
    { role: "ML_ENGINEER", label: "MLOps Engineer", href: "/ml-engineer", color: "text-[#9b9eed]", bgBadge: "bg-[#565ac4]/20" },
  ];

  const handleRoleSwitch = async (role: UserRole, targetHref: string, label: string) => {
    setDropdownOpen(false);
    const success = await quickLogin(role);
    if (success) {
      showNotification("success", `Chuyển Quyền: ${label}`, "Đã cấp mới mã Token JWT tương ứng với đầy đủ quyền RBAC.");
      router.push(targetHref);
    }
  };

  const handleLogout = () => {
    setDropdownOpen(false);
    logout();
    showNotification("info", "Đã Đăng Xuất", "Mã Token JWT đã được thu hồi.");
    router.push("/login");
  };

  const currentRole = roleOptions.find((r) => r.role === user?.role) || roleOptions[0];

  return (
    <>
      <header className="sticky top-0 z-40 border-b border-[#30adcd]/30 bg-[#080C14] shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            
            {/* Logo & Thuong Hieu */}
            <Link href="/" className="flex items-center gap-3 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-[#30adcd] via-[#565ac4] to-[#2cb285] p-0.5 flex items-center justify-center shadow-lg shadow-[#30adcd]/25 group-hover:shadow-[#30adcd]/50 transition-all duration-300">
                <div className="w-full h-full bg-[#080C14] rounded-[10px] flex items-center justify-center">
                  <ShieldAlert className="w-5 h-5 text-[#30adcd] group-hover:scale-110 transition-transform" />
                </div>
              </div>
              <div>
                <div className="flex items-center gap-1.5">
                  <span className="text-base sm:text-lg font-bold tracking-tight bg-gradient-to-r from-white via-[#eaf7fa] to-[#30adcd] bg-clip-text text-transparent font-sans">
                    SentinelRisk AI
                  </span>
                  <Sparkles className="w-3.5 h-3.5 text-[#30adcd]" />
                </div>
                <span className="hidden sm:inline-block text-[10px] font-semibold uppercase tracking-wider text-[#30adcd] bg-[#30adcd]/15 px-2 py-0.2 rounded-full border border-[#30adcd]/30">
                  JWT Auth • PaySim 2.77M
                </span>
              </div>
            </Link>

            {/* Cac lien ket dieu huong */}
            <nav className="flex items-center space-x-1 sm:space-x-2">
              {/* { loop-1: duyet qua cac duong dan dieu huong } */}
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname.startsWith(item.href);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all duration-200 ${
                      isActive
                        ? "bg-[#30adcd]/20 text-[#eaf7fa] border border-[#30adcd]/60 shadow-glow-blue font-bold"
                        : "text-slate-400 hover:text-[#30adcd] hover:bg-[#30adcd]/10 border border-transparent"
                    }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? "text-[#30adcd]" : "text-slate-400"}`} />
                    <span className="hidden md:inline">{item.label}</span>
                  </Link>
                );
              })}
            </nav>

            {/* Simulator Trigger & Role Switcher */}
            <div className="flex items-center gap-2 sm:gap-3 relative" ref={dropdownRef}>
              
              {/* Nut Ban PaySim truc tiep */}
              <button
                onClick={() => setSimulatorOpen(true)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-gradient-to-r from-[#30adcd] to-[#2cb285] hover:opacity-90 text-white text-xs font-bold shadow-glow-blue transition-all cursor-pointer"
              >
                <Zap className="w-3.5 h-3.5 fill-white" />
                <span className="hidden sm:inline">Bắn PaySim</span>
              </button>

              {/* Nut Role Switcher */}
              <div className="relative">
                <button
                  onClick={() => setDropdownOpen(!dropdownOpen)}
                  className="flex items-center gap-2 bg-[#0c1626] border-2 border-[#30adcd] hover:bg-[#112038] px-3.5 py-1.5 rounded-xl text-xs font-bold text-white shadow-[0_0_15px_rgba(48,173,205,0.4)] transition-all cursor-pointer"
                >
                  <Key className="w-3.5 h-3.5 text-[#30adcd]" />
                  <span className={currentRole.color}>{currentRole.label}</span>
                  <ChevronDown className="w-3.5 h-3.5 text-slate-300" />
                </button>

                {/* Menu Dropdown hoan toan dac */}
                {dropdownOpen && (
                  <div className="absolute right-0 mt-2 w-64 bg-[#0c1626] border-2 border-[#30adcd] rounded-2xl p-2.5 shadow-[0_20px_50px_rgba(0,0,0,0.95)] z-[9999] space-y-1.5">
                    <div className="px-3 py-2 text-[11px] uppercase font-extrabold text-[#30adcd] border-b border-slate-700/80 flex items-center justify-between">
                      <span>Chuyển Quyền JWT Nhanh</span>
                      <Shield className="w-3.5 h-3.5 text-[#30adcd]" />
                    </div>

                    {/* { loop-2: danh sach cac vai tro (chi o che do demo) } */}
                    {DEMO_MODE && roleOptions.map((opt) => (
                      <button
                        key={opt.role}
                        onClick={() => handleRoleSwitch(opt.role, opt.href, opt.label)}
                        className={`w-full text-left px-3 py-2.5 rounded-xl text-xs font-bold flex items-center justify-between transition-all ${
                          user?.role === opt.role
                            ? "bg-[#30adcd]/25 text-white border border-[#30adcd]"
                            : "text-slate-200 hover:bg-[#16253d] hover:text-white"
                        }`}
                      >
                        <span className={`flex items-center gap-2 ${opt.color}`}>
                          <span className={`w-2 h-2 rounded-full ${opt.bgBadge}`} />
                          {opt.label}
                        </span>
                        {user?.role === opt.role && <UserCheck className="w-4 h-4 text-[#30adcd]" />}
                      </button>
                    ))}

                    <div className="border-t border-slate-700/80 pt-1 mt-1">
                      <button
                        onClick={handleLogout}
                        className="w-full text-left px-3 py-2 rounded-xl text-xs font-bold text-[#d1556c] hover:bg-[#d1556c]/20 flex items-center gap-2 transition-colors"
                      >
                        <LogOut className="w-3.5 h-3.5 text-[#d1556c]" /> Đăng Xuất & Về Login
                      </button>
                    </div>
                  </div>
                )}
              </div>

            </div>

          </div>
        </div>
      </header>

      {/* Modal PaySim Simulator */}
      <PaySimSimulatorModal
        isOpen={simulatorOpen}
        onClose={() => setSimulatorOpen(false)}
        onSuccess={() => {
          if (pathname === "/analyst" || pathname === "/manager") {
            window.location.reload();
          }
        }}
      />
    </>
  );
};
