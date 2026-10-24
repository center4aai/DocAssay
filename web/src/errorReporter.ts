import { sessionToken } from "./session";

function report(data: { message: string; stack?: string }) {
  try {
    const headers = new Headers({ "Content-Type": "application/json" });
    if (sessionToken) headers.set("X-Session-Token", sessionToken);
    fetch("/api/client-error", {
      method: "POST",
      headers,
      body: JSON.stringify({ page: window.location.href, ...data }),
      keepalive: true,
    });
  } catch {
    /* best effort; never crash on reporting */
  }
}

export function installErrorReporter() {
  window.addEventListener("error", (event) => {
    const err = event.error;
    report({
      message: event.message,
      stack: err instanceof Error ? err.stack : undefined,
    });
  });
  window.addEventListener("unhandledrejection", (event) => {
    const err = event.reason;
    report({
      message: err instanceof Error ? err.message : String(err),
      stack: err instanceof Error ? err.stack : undefined,
    });
  });
}