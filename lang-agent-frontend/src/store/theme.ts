import { create } from "zustand";

const theme_color: Record<string, string> = {
  dark: "black",
  light: "white",
};

type ThemeState = {
  dark: boolean;
  color: string;
  toggleDark: () => void;
};

export const useThemeStore = create<ThemeState>((set) => ({
  dark: false,
  color: "white",
  toggleDark: () =>
    set((state) => ({
      dark: !state.dark,
      color: theme_color[state.dark ? "light" : "dark"],
    })),
}));
