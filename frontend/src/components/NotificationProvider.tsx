"use client";

import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { NotificationItem, NotificationType, NotificationToast } from "./NotificationToast";

interface NotificationContextValue {
  showNotification: (type: NotificationType, title: string, message: string, duration?: number) => void;
}

const NotificationContext = createContext<NotificationContextValue | undefined>(undefined);

export const useNotification = (): NotificationContextValue => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error("useNotification phai duoc su dung ben trong NotificationProvider");
  }
  return context;
};

/**
 * {
 *   func   : NotificationProvider
 *   desc   : Context Provider quan ly danh sach notification toast toan he thong kem mount check
 *   input  : children (React.ReactNode)
 *   output : JSX.Element
 *   loop   : 1 loop — hien thi cac notification hien co
 * }
 */
export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const removeNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  }, []);

  const showNotification = useCallback(
    (type: NotificationType, title: string, message: string, duration: number = 5000) => {
      const id = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const newItem: NotificationItem = { id, type, title, message, duration };

      setNotifications((prev) => [...prev, newItem]);

      if (duration > 0) {
        setTimeout(() => {
          removeNotification(id);
        }, duration);
      }
    },
    [removeNotification]
  );

  return (
    <NotificationContext.Provider value={{ showNotification }}>
      {children}
      
      {/* Chi render container khi da mount va co it nhat 1 notification de tranh hydration error */}
      {mounted && notifications.length > 0 && (
        <div className="fixed top-20 right-5 z-50 flex flex-col gap-3 pointer-events-auto" suppressHydrationWarning>
          {/* { loop-1: duyet qua danh sach notification de render } */}
          {notifications.map((item) => (
            <NotificationToast key={item.id} notification={item} onClose={removeNotification} />
          ))}
        </div>
      )}
    </NotificationContext.Provider>
  );
};
