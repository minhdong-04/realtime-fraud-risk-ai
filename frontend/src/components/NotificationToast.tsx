"use client";

import React from "react";
import { Info, CheckCircle2, AlertTriangle, AlertOctagon, X } from "lucide-react";

export type NotificationType = "info" | "success" | "warning" | "error";

export interface NotificationItem {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  duration?: number;
}

interface NotificationToastProps {
  notification: NotificationItem;
  onClose: (id: string) => void;
}

/**
 * {
 *   func   : NotificationToast
 *   desc   : Component the thong bao Notification Card theo dung chuan bang ma mau thiet ke
 *   input  : notification (NotificationItem), onClose (func)
 *   output : JSX.Element
 *   loop   : 0 loops
 * }
 */
export const NotificationToast: React.FC<NotificationToastProps> = ({ notification, onClose }) => {
  const { id, type, title, message } = notification;

  // Bang ma mau chuan cho ca 4 loai Notification (Dark Mode & Light Accent)
  const styles: Record<
    NotificationType,
    {
      cardBg: string;
      border: string;
      glow: string;
      titleColor: string;
      textColor: string;
      iconColor: string;
      closeBtnBg: string;
      icon: React.ReactNode;
    }
  > = {
    info: {
      cardBg: "bg-[#113d48]/90",
      border: "border-[#30adcd]/50",
      glow: "shadow-[0_8px_30px_rgba(48,173,205,0.35)]",
      titleColor: "text-[#eaf7fa]",
      textColor: "text-[#bfe6f0]",
      iconColor: "text-[#30adcd]",
      closeBtnBg: "hover:bg-[#30adcd]/20 text-[#30adcd]",
      icon: <Info className="w-4 h-4 text-[#30adcd] shrink-0" />,
    },
    success: {
      cardBg: "bg-[#0f3e2f]/90",
      border: "border-[#2cb285]/50",
      glow: "shadow-[0_8px_30px_rgba(44,178,133,0.35)]",
      titleColor: "text-[#eaf7f3]",
      textColor: "text-[#bee7d9]",
      iconColor: "text-[#2cb285]",
      closeBtnBg: "hover:bg-[#2cb285]/20 text-[#2cb285]",
      icon: <CheckCircle2 className="w-4 h-4 text-[#2cb285] shrink-0" />,
    },
    warning: {
      cardBg: "bg-[#554a3e]/90",
      border: "border-[#b79f86]/50",
      glow: "shadow-[0_8px_30px_rgba(244,212,178,0.3)]",
      titleColor: "text-[#fefbf7]",
      textColor: "text-[#fcf2e7]",
      iconColor: "text-[#f4d4b2]",
      closeBtnBg: "hover:bg-[#f4d4b2]/20 text-[#f4d4b2]",
      icon: <AlertTriangle className="w-4 h-4 text-[#f4d4b2] shrink-0" />,
    },
    error: {
      cardBg: "bg-[#491e26]/90",
      border: "border-[#d1556c]/50",
      glow: "shadow-[0_8px_30px_rgba(209,85,108,0.35)]",
      titleColor: "text-[#faeef0]",
      textColor: "text-[#f1cad1]",
      iconColor: "text-[#d1556c]",
      closeBtnBg: "hover:bg-[#d1556c]/20 text-[#d1556c]",
      icon: <AlertOctagon className="w-4 h-4 text-[#d1556c] shrink-0" />,
    },
  };

  const style = styles[type] || styles.info;

  return (
    <div
      className={`relative w-full max-w-sm rounded-2xl p-4 border ${style.border} ${style.cardBg} ${style.glow} backdrop-blur-xl transition-all duration-300 transform animate-in slide-in-from-top-3 fade-in font-sans`}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-2.5">
          {style.icon}
          <h4 className={`text-xs font-bold ${style.titleColor}`}>
            {title}
          </h4>
        </div>
        <button
          onClick={() => onClose(id)}
          className={`rounded-full p-1 transition-colors ${style.closeBtnBg}`}
          aria-label="Close"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <p className={`mt-2 text-[11px] leading-relaxed ${style.textColor}`}>
        {message}
      </p>
    </div>
  );
};
