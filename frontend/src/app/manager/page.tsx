"use client";

import "@/lib/suppress-hydration";
import React, { useEffect, useState } from "react";
import { fetchDashboardMetrics, getAuthHeaders, API_BASE_URL } from "@/lib/api";
import { DashboardMetrics } from "@/types/fraud.types";
import { useNotification } from "@/components/NotificationProvider";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, PieChart, Pie, Cell
} from "recharts";
import { BarChart3, TrendingUp, AlertOctagon, CheckSquare, Download, Calendar, Activity, Sparkles } from "lucide-react";

/**
 * {
 *   func   : ManagerDashboardPage
 *   desc   : Dashboard Thong ke Manager kem thong bao Notification Toast va Tooltip ro net
 *   input  : None
 *   output : JSX.Element
 *   loop   : 1 loop — hien thi phan bo rui ro
 * }
 */
export default function ManagerDashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const { showNotification } = useNotification();

  useEffect(() => {
    fetchDashboardMetrics()
      .then(setMetrics)
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleExportCSV = async () => {
    try {
      showNotification("info", "Đang Xuất Báo Cáo", "Đang kết xuất dữ liệu thống kê tổng hợp sang định dạng CSV...");
      const res = await fetch(`${API_BASE_URL}/analytics/export`, { method: "POST", headers: getAuthHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "fraud_summary_report.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      showNotification("success", "Xuất File Thành Công", "Đã tải xuống tệp fraud_summary_report.csv.");
    } catch (err) {
      showNotification("error", "Lỗi Xuất File", "Không thể kết xuất dữ liệu báo cáo CSV.");
    }
  };

  if (loading || !metrics) {
    return <div className="p-12 text-center text-slate-400 font-sans">Đang tải dữ liệu KPI Manager Dashboard...</div>;
  }

  const donutColors: Record<string, string> = {
    HIGH: "#d1556c",
    MEDIUM: "#f4d4b2",
    LOW: "#2cb285",
  };

  return (
    <div className="space-y-6">
      
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-5 glass-panel p-6 sm:p-8 rounded-3xl border border-[#30adcd]/25 shadow-glow-blue">
        <div className="flex items-center gap-3.5">
          <div className="w-12 h-12 rounded-2xl bg-[#30adcd]/20 border border-[#30adcd]/40 flex items-center justify-center shadow-md">
            <BarChart3 className="w-6 h-6 text-[#30adcd]" />
          </div>
          <div>
            <h1 className="text-2xl font-extrabold text-white flex items-center gap-2">
              Risk Manager Analytics
              <Sparkles className="w-4 h-4 text-[#30adcd]" />
            </h1>
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
              Báo cáo thống kê tỷ lệ gian lận theo thời gian thực, hiệu suất kiểm duyệt và xu hướng 14 ngày
            </p>
          </div>
        </div>

        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-5 py-2.5 bg-[#30adcd] hover:bg-[#2b9cb9] text-white rounded-2xl text-xs font-bold shadow-glow-blue transition-all w-fit"
        >
          <Download className="w-4 h-4" /> Xuất Báo Cáo CSV
        </button>
      </div>

      {/* Top 3 KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        
        {/* Fraud Rate */}
        <div className="glass-panel p-6 rounded-3xl border border-[#d1556c]/30 space-y-2 shadow-glow-red">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Tỷ Lệ Gian Lận Tổng Thể</span>
            <AlertOctagon className="w-4 h-4 text-[#d1556c]" />
          </div>
          <div className="text-3xl font-extrabold text-[#faeef0] font-mono">
            {metrics.fraud_rate}%
          </div>
          <div className="text-xs text-[#2cb285] flex items-center gap-1.5 font-bold">
            <TrendingUp className="w-3.5 h-3.5 text-[#2cb285]" /> Đạt mục tiêu kiểm soát ≤ 2.0%
          </div>
        </div>

        {/* False Positive Rate */}
        <div className="glass-panel p-6 rounded-3xl border border-[#30adcd]/25 space-y-2 shadow-glow-blue">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Tỷ Lệ Cảnh Báo Sai (FPR)</span>
            <Activity className="w-4 h-4 text-[#30adcd]" />
          </div>
          <div className="text-3xl font-extrabold text-[#30adcd] font-mono">
            {metrics.fp_rate}%
          </div>
          <div className="text-xs text-slate-400 font-medium">
            Mục tiêu ngân hàng: ≤ 8.0%
          </div>
        </div>

        {/* Reviewed Today */}
        <div className="glass-panel p-6 rounded-3xl border border-[#2cb285]/30 space-y-2 shadow-glow-green">
          <div className="flex items-center justify-between text-slate-400 text-xs font-semibold">
            <span>Số Ca Đã Thẩm Định Hôm Nay</span>
            <CheckSquare className="w-4 h-4 text-[#2cb285]" />
          </div>
          <div className="text-3xl font-extrabold text-[#eaf7f3] font-mono">
            {metrics.cases_reviewed_today}
          </div>
          <div className="text-xs text-slate-400 font-medium">
            SLA xử lý trung bình: 3.4 phút / ca
          </div>
        </div>

      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Line Chart */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-3xl border border-[#30adcd]/25 space-y-4 shadow-glow-blue">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-[#30adcd]/20 pb-3">
            <Calendar className="w-4 h-4 text-[#30adcd]" /> Biểu Đồ Xu Hướng Fraud Rate & FPR 14 Ngày (%)
          </h3>
          <div className="h-64 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={metrics.trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#113d48" />
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} />
                <YAxis stroke="#94A3B8" fontSize={11} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#080C14",
                    borderColor: "#30adcd",
                    borderRadius: "16px",
                    boxShadow: "0 0 20px rgba(48,173,205,0.4)",
                    color: "#FFFFFF",
                  }}
                  itemStyle={{ color: "#FFFFFF", fontWeight: "bold", fontSize: "12px" }}
                  labelStyle={{ color: "#30adcd", fontWeight: "bold", fontSize: "12px" }}
                />
                <Line type="monotone" dataKey="fraud_rate" stroke="#d1556c" strokeWidth={3} dot={{ r: 4 }} name="Fraud Rate (%)" />
                <Line type="monotone" dataKey="fp_rate" stroke="#30adcd" strokeWidth={2.5} dot={{ r: 4 }} name="FP Rate (%)" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Donut Chart */}
        <div className="glass-panel p-6 rounded-3xl border border-[#30adcd]/25 space-y-4 shadow-glow-blue">
          <h3 className="text-sm font-bold text-white border-b border-[#30adcd]/20 pb-3">
            Phân Bố Mức Độ Rủi Ro
          </h3>
          <div className="h-48 w-full flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={metrics.risk_distribution}
                  dataKey="count"
                  nameKey="level"
                  cx="50%"
                  cy="50%"
                  innerRadius={48}
                  outerRadius={72}
                  paddingAngle={6}
                >
                  {metrics.risk_distribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={donutColors[entry.level] || entry.color} stroke="#080C14" strokeWidth={2} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "#080C14",
                    borderColor: "#30adcd",
                    borderRadius: "16px",
                    boxShadow: "0 0 20px rgba(48,173,205,0.4)",
                    color: "#FFFFFF",
                  }}
                  itemStyle={{ color: "#FFFFFF", fontWeight: "bold", fontSize: "12px" }}
                  labelStyle={{ color: "#30adcd", fontWeight: "bold", fontSize: "12px" }}
                  formatter={(val: any, name: any) => [`${val} ca`, `Mức ${name}`]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          
          <div className="space-y-2 text-xs">
            {/* { loop-1: hien thi phan bo tung muc do } */}
            {metrics.risk_distribution.map((item, idx) => {
              const itemColor = donutColors[item.level] || item.color;
              return (
                <div key={idx} className="flex items-center justify-between p-2 rounded-xl bg-[#080C14]/70 border border-[#30adcd]/15">
                  <span className="flex items-center gap-2 text-slate-200 font-semibold">
                    <span className="w-2.5 h-2.5 rounded-full shadow-sm" style={{ backgroundColor: itemColor }} />
                    Mức {item.level}
                  </span>
                  <span className="font-mono font-bold text-[#30adcd]">{item.count} ca</span>
                </div>
              );
            })}
          </div>
        </div>

      </div>

    </div>
  );
}
