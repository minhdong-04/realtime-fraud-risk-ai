import React from "react";
import { RiskLevel } from "@/types/fraud.types";
import { ShieldAlert, AlertTriangle, ShieldCheck } from "lucide-react";

interface RiskBadgeProps {
  level: RiskLevel;
  score?: number;
  showScore?: boolean;
}

/**
 * {
 *   func   : RiskBadge
 *   desc   : Hien thi badge muc do rui ro su dung ma mau Red #d1556c, Orange #f4d4b2, Green #2cb285
 *   input  : level (RiskLevel), score (number | undefined), showScore (boolean)
 *   output : JSX.Element
 *   loop   : 0 loops
 * }
 */
export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, score, showScore = true }) => {
  const styles: Record<RiskLevel, { bg: string; text: string; border: string; glow: string; icon: React.ReactNode }> = {
    HIGH: {
      bg: "bg-[#d1556c]/15",
      text: "text-[#faeef0]",
      border: "border-[#d1556c]/50",
      glow: "shadow-[0_0_15px_rgba(209,85,108,0.35)]",
      icon: <ShieldAlert className="w-3.5 h-3.5 text-[#d1556c]" />,
    },
    MEDIUM: {
      bg: "bg-[#f4d4b2]/15",
      text: "text-[#fefbf7]",
      border: "border-[#b79f86]/50",
      glow: "shadow-[0_0_15px_rgba(244,212,178,0.3)]",
      icon: <AlertTriangle className="w-3.5 h-3.5 text-[#f4d4b2]" />,
    },
    LOW: {
      bg: "bg-[#2cb285]/15",
      text: "text-[#eaf7f3]",
      border: "border-[#2cb285]/50",
      glow: "shadow-[0_0_15px_rgba(44,178,133,0.35)]",
      icon: <ShieldCheck className="w-3.5 h-3.5 text-[#2cb285]" />,
    },
  };

  const style = styles[level] || styles.LOW;

  return (
    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border ${style.bg} ${style.text} ${style.border} ${style.glow} backdrop-blur-md`}>
      {style.icon}
      <span>{level}</span>
      {showScore && score !== undefined && (
        <span className="font-mono font-extrabold border-l border-white/20 pl-1.5 ml-0.5 text-white">
          {score}
        </span>
      )}
    </span>
  );
};
