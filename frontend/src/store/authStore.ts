import { create } from 'zustand';
import { UserOut } from '../types/auth';

interface AuthState {
  user: UserOut | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (user: UserOut, accessToken: string, refreshToken: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  accessToken: sessionStorage.getItem("accessToken"),
  refreshToken: sessionStorage.getItem("refreshToken"),
  login: (user, accessToken, refreshToken) => {
    sessionStorage.setItem("accessToken", accessToken);
    sessionStorage.setItem("refreshToken", refreshToken);
    set({ user, accessToken, refreshToken });
  },
  logout: () => {
    sessionStorage.removeItem("accessToken");
    sessionStorage.removeItem("refreshToken");
    set({ user: null, accessToken: null, refreshToken: null });
  },
}));
