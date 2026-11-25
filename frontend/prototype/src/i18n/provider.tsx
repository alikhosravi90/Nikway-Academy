import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from "react";
export type Locale = "fa" | "en";
const Context = createContext<{
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (fa: string, en: string) => string;
  num: (n: number) => string;
}>(null!);
export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, set] = useState<Locale>(() => {
    try {
      return localStorage.getItem("nikway-locale") === "en" ? "en" : "fa";
    } catch {
      return "fa";
    }
  });
  useEffect(() => {
    document.documentElement.lang = locale;
    document.documentElement.dir = locale === "fa" ? "rtl" : "ltr";
    try {
      localStorage.setItem("nikway-locale", locale);
    } catch {}
  }, [locale]);
  return (
    <Context.Provider
      value={{
        locale,
        setLocale: set,
        t: (fa, en) => (locale === "fa" ? fa : en),
        num: (n) => n.toLocaleString(locale === "fa" ? "fa-IR" : "en-US"),
      }}
    >
      {children}
    </Context.Provider>
  );
}
export const useI18n = () => useContext(Context);
