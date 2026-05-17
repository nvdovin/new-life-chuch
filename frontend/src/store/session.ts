import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { UserSession } from '@/types';

interface SessionState {
  session: UserSession | null;
  setSession: (session: UserSession | null) => void;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set) => ({
      session: null,
      setSession: (session) => set({ session }),
      clearSession: () => set({ session: null }),
    }),
    {
      name: 'nlc-session',
    },
  ),
);
