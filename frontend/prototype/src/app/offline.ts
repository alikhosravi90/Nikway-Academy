import { useEffect, useState } from "react";
import { registerSW } from "virtual:pwa-register";
export function useOffline() {
  const [ready, setReady] = useState(false),
    [failed, setFailed] = useState(false),
    [update, setUpdate] = useState<null | (() => void)>(null);
  useEffect(() => {
    if (!import.meta.env.PROD) return;
    const updateSW = registerSW({
      immediate: true,
      onOfflineReady: () => setReady(true),
      onNeedRefresh: () => setUpdate(() => () => void updateSW(true)),
      onRegisterError: () => setFailed(true),
      onRegisteredSW: () => {
        navigator.serviceWorker.ready
          .then(() => setReady(true))
          .catch(() => setFailed(true));
      },
    });
  }, []);
  return { ready, failed, update };
}
