"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { UserProfile, UserRole, AuthTokenResponse } from "@/types/fraud.types";

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, pass: string) => Promise<boolean>;
  quickLogin: (role: UserRole) => Promise<boolean>;
  logout: () => void;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Chế độ demo (mặc định TẮT): bật nút đăng nhập 1-chạm bằng mật khẩu demo từ env.
export const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
const DEMO_PASSWORD = process.env.NEXT_PUBLIC_DEMO_PASSWORD || "";

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const ROLE_EMAILS: Record<UserRole, { email: string; name: string }> = {
  ANALYST: { email: "analyst@fraud-platform.com", name: "Chuyên Viên Thẩm Định Gian Lận" },
  MANAGER: { email: "manager@fraud-platform.com", name: "Giám Đốc Quản Trị Rủi Ro" },
  ML_ENGINEER: { email: "mlengineer@fraud-platform.com", name: "Kỹ Sư Học Máy MLOps" },
};

/**
 * {
 *   func   : AuthProvider
 *   desc   : Context Provider quan ly trang thai xac thuc JWT Token va phan quyen RBAC
 *   input  : children (React.ReactNode)
 *   output : JSX.Element
 *   loop   : 0 loops
 * }
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  // Khoi tao phien dang nhap tu localStorage khi load trang
  useEffect(() => {
    try {
      const savedToken = localStorage.getItem("sentinel_token");
      const savedUser = localStorage.getItem("sentinel_user");

      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      } else if (pathname !== "/login") {
        router.replace("/login");
      }
    } catch (e) {
      console.error("Loi khoi tao phien Auth:", e);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, pass: string): Promise<boolean> => {
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password: pass }),
      });

      if (!res.ok) return false;

      const data: AuthTokenResponse = await res.json();
      const profile: UserProfile = {
        email: data.email,
        role: data.role,
        name: ROLE_EMAILS[data.role]?.name || "Nguoi dung he thong",
      };

      setToken(data.access_token);
      setUser(profile);
      localStorage.setItem("sentinel_token", data.access_token);
      localStorage.setItem("sentinel_user", JSON.stringify(profile));
      return true;
    } catch (err) {
      console.error("Loi dang nhap:", err);
      return false;
    }
  };

  const quickLogin = async (role: UserRole): Promise<boolean> => {
    if (!DEMO_MODE) return false;
    return login(ROLE_EMAILS[role].email, DEMO_PASSWORD);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("sentinel_token");
    localStorage.removeItem("sentinel_user");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        quickLogin,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth phai duoc su dung ben trong AuthProvider");
  }
  return context;
}
