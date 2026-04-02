import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
}

interface UIStore {
  darkMode: boolean;
  sidebarOpen: boolean;
  notifications: Notification[];
  toggleDarkMode: () => void;
  toggleSidebar: () => void;
  setSidebarOpen: (open: boolean) => void;
  addNotification: (n: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
  markAllRead: () => void;
  clearNotifications: () => void;
  unreadCount: () => number;
}

export const useUIStore = create<UIStore>()(
  persist(
    (set, get) => ({
      darkMode:       false,
      sidebarOpen:    true,
      notifications:  [],

      toggleDarkMode:  () => set((s) => ({ darkMode: !s.darkMode })),
      toggleSidebar:   () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSidebarOpen:  (open) => set({ sidebarOpen: open }),

      addNotification: (n) =>
        set((s) => ({
          notifications: [
            {
              ...n,
              id:        crypto.randomUUID(),
              timestamp: new Date().toISOString(),
              read:      false,
            },
            ...s.notifications.slice(0, 99),  // keep last 100
          ],
        })),

      markAllRead: () =>
        set((s) => ({ notifications: s.notifications.map((n) => ({ ...n, read: true })) })),

      clearNotifications: () => set({ notifications: [] }),

      unreadCount: () => get().notifications.filter((n) => !n.read).length,
    }),
    {
      name: 'spoorthy-ui',
      partialize: (state) => ({ darkMode: state.darkMode, sidebarOpen: state.sidebarOpen }),
    }
  )
);
