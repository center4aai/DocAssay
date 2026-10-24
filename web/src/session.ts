// The server prints its start address as `/?token=...`. On first load the token
// moves from the address bar into session storage (and out of the visible URL
// and history); every API request then sends it as `X-Session-Token`.
const STORAGE_KEY = "docassay-session-token";

function readSessionToken(): string {
  try {
    const url = new URL(window.location.href);
    const fromUrl = url.searchParams.get("token");
    if (fromUrl) {
      sessionStorage.setItem(STORAGE_KEY, fromUrl);
      url.searchParams.delete("token");
      window.history.replaceState(window.history.state, "", url.pathname + url.search + url.hash);
      return fromUrl;
    }
    return sessionStorage.getItem(STORAGE_KEY) ?? "";
  } catch {
    return "";
  }
}

export const sessionToken = readSessionToken();

export const MISSING_TOKEN_HINT =
  "Open the address printed by `docassay web` (it carries the session token).";
