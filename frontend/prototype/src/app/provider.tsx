import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";
import { useLiveQuery } from "dexie-react-hooks";
import { services } from "./services";
import type { Action, LearningState } from "../domain/model";
import { useI18n } from "../i18n/provider";
import { Button } from "../components/ui/button";
export type Message = { role: "user" | "assistant"; text: string };
const Context = createContext<{
  state: LearningState;
  act: (a: Action) => Promise<boolean>;
  pending: boolean;
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  notice: (s: string) => void;
  setError: (s: string) => void;
  sessions: Record<string, unknown>;
  setSessions: React.Dispatch<React.SetStateAction<Record<string, unknown>>>;
}>(null!);
export function download(raw: string, name: string) {
  const url = URL.createObjectURL(
    new Blob([raw], { type: "application/json" }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export function LearningProvider({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  const [ready, setReady] = useState(false),
    [error, setError] = useState(""),
    [pending, setPending] = useState(false),
    [note, notice] = useState(""),
    [messages, setMessages] = useState<Message[]>([]);
  const boot = () => {
    setError("");
    services.learning
      .initialize(() => localStorage.getItem("nikway-demo-v1"))
      .then(() => setReady(true))
      .catch(() =>
        setError(
          t(
            "خواندن داده ممکن نشد. دادهٔ اصلی حفظ شده است؛ فایل معتبر وارد کنید یا دوباره تلاش کنید.",
            "Unable to read data. Original data is preserved. Import a valid backup or retry.",
          ),
        ),
      );
  };
  useEffect(() => {
    boot();
  }, []);
  const [sessions, setSessions] = useState<Record<string, unknown>>({});
  const state = useLiveQuery(async () => {
    if (!ready) return null;
    try {
      return await services.learning.read();
    } catch {
      setError(
        t(
          "خواندن داده ممکن نشد. دوباره تلاش کنید.",
          "Unable to read data. Please retry.",
        ),
      );
      return null;
    }
  }, [ready]);
  useEffect(() => {
    if (!note) return;
    const id = setTimeout(() => notice(""), 3200);
    return () => clearTimeout(id);
  }, [note]);
  const act = async (a: Action) => {
    setPending(true);
    setError("");
    try {
      await services.learning.dispatch(a);
      if (a.type === "reset") {
        setMessages([]);
        setSessions({});
      }
      return true;
    } catch {
      setError(
        t(
          "ذخیره انجام نشد؛ دادهٔ قبلی حفظ شده است. دوباره تلاش کنید.",
          "Could not save. Previous data is preserved. Please retry.",
        ),
      );
      return false;
    } finally {
      setPending(false);
    }
  };
  if (!ready || !state)
    return (
      <div className="boot card">
        <h1>NIKWAY Learning OS</h1>
        {error ? (
          <>
            <p role="alert">{error}</p>
            <Button onClick={boot}>{t("تلاش دوباره", "Retry")}</Button>{" "}
            <Button
              variant="outline"
              onClick={() => {
                try {
                  download(
                    localStorage.getItem("nikway-demo-v1") ?? "null",
                    "nikway-original.json",
                  );
                } catch {
                  setError(
                    t(
                      "دسترسی به ذخیره‌سازی مرورگر مسدود است.",
                      "Browser storage access is blocked.",
                    ),
                  );
                }
              }}
            >
              {t("دریافت نسخهٔ اصلی", "Download original")}
            </Button>
            <label className="import-label">
              {t("ورود داده‌ها", "Import data")}
              <input
                aria-label={t("ورود داده‌ها", "Import data")}
                type="file"
                accept=".json"
                onChange={async (e) => {
                  try {
                    const f = e.target.files?.[0];
                    if (f) {
                      await services.learning.importBackup(await f.text());
                      setReady(true);
                      setError("");
                    }
                  } catch {
                    setError(
                      t(
                        "فایل نامعتبر است؛ دادهٔ اصلی حفظ شد.",
                        "Invalid file. Original data preserved.",
                      ),
                    );
                  }
                }}
              />
            </label>
          </>
        ) : (
          <p role="status">
            {t(
              "در حال آماده‌سازی فضای یادگیری…",
              "Preparing your learning space…",
            )}
          </p>
        )}
      </div>
    );
  return (
    <Context.Provider
      value={{
        state,
        act,
        pending,
        messages,
        setMessages,
        notice,
        setError,
        sessions,
        setSessions,
      }}
    >
      {error && (
        <div className="error-banner" role="alert">
          {error}
          <button
            onClick={() => setError("")}
            aria-label={t("بستن پیام", "Dismiss")}
          >
            ×
          </button>
        </div>
      )}
      {children}
      {note && (
        <div className="toast" role="status">
          {note}
        </div>
      )}
    </Context.Provider>
  );
}
export const useLearning = () => useContext(Context);
