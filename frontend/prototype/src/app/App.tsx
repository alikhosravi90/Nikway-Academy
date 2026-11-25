import { Component, type ReactNode } from "react";
import { HashRouter, Routes, Route, Navigate } from "react-router-dom";
import { I18nProvider } from "../i18n/provider";
import { LearningProvider } from "./provider";
import { Shell } from "./Shell";
import { modules } from "./registry";
class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    return this.state.failed ? (
      <div className="boot card" role="alert">
        <h1>NIKWAY</h1>
        <p>نمایش صفحه با خطا روبه‌رو شد. داده‌های ذخیره‌شده حذف نشده‌اند.</p>
        <button className="btn" onClick={() => location.reload()}>
          بارگذاری دوباره / Reload
        </button>
      </div>
    ) : (
      this.props.children
    );
  }
}
export function App() {
  return (
    <ErrorBoundary>
      <I18nProvider>
        <LearningProvider>
          <HashRouter>
            <Routes>
              <Route element={<Shell />}>
                {modules.map(({ id, Component: Page }) => (
                  <Route key={id} path={id} element={<Page />} />
                ))}
                <Route
                  path="*"
                  element={<Navigate to="/dashboard" replace />}
                />
              </Route>
            </Routes>
          </HashRouter>
        </LearningProvider>
      </I18nProvider>
    </ErrorBoundary>
  );
}
