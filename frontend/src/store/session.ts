import { create } from 'zustand';
import { UserSession } from '@/types';

interface SessionState {
  session: UserSession | null;
  setSession: (session: UserSession | null) => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  session: null,
  setSession: (session) => set({ session }),
}));
