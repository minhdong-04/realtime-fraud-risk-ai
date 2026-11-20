"use client";

import React, { useState } from "react";

interface PromotionDialogProps {
  version: string;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (reason: string) => void;
}

export function PromotionDialog({ version, isOpen, onClose, onConfirm }: PromotionDialogProps) {
  const [reason, setReason] = useState("");

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-xl max-w-md w-full p-6 shadow-2xl space-y-4">
        <h3 className="text-xl font-bold text-slate-100">Xác Nhận Promote Mô Hình {version}</h3>
        <p className="text-sm text-slate-300">
          Cảnh báo: Việc Promote mô hình này sẽ cập nhật Champion Scorer trên toàn bộ hệ thống real-time scoring.
        </p>

        <div>
          <label className="block text-xs font-medium text-slate-400 mb-1">
            Lý do Promote (Bắt buộc):
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2 text-sm text-slate-100 focus:outline-none focus:border-indigo-500"
            rows={3}
            placeholder="Nhập lý do kiểm định hiệu năng mô hình..."
          />
        </div>

        <div className="flex justify-end gap-2 pt-2">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 transition"
          >
            Hủy Bỏ
          </button>
          <button
            disabled={!reason.trim()}
            onClick={() => {
              onConfirm(reason);
              onClose();
            }}
            className="px-4 py-2 text-sm bg-indigo-600 text-white font-medium rounded-lg hover:bg-indigo-500 disabled:opacity-50 transition"
          >
            Xác Nhận Promote
          </button>
        </div>
      </div>
    </div>
  );
}
