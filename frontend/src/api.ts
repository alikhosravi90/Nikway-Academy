import Keycloak from "keycloak-js";
export const auth = new Keycloak({
  url: import.meta.env.VITE_OIDC_URL || "http://localhost:18480",
  realm: "academy",
  clientId: "academy-web",
});
export async function api<T>(path: string, body?: unknown): Promise<T> {
  await auth.updateToken(30);
  const r = await fetch("/api" + path, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      Authorization: `Bearer ${auth.token}`,
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  if (!r.ok) {
    let detail = "";
    try {
      const e = await r.json();
      detail =
        typeof e.detail === "string" ? e.detail : e.message || "Request failed";
    } catch {}
    throw new Error(`${r.status}: ${detail || "درخواست انجام نشد"}`);
  }
  return r.status === 204 ? (undefined as T) : r.json();
}
