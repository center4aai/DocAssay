import { MISSING_TOKEN_HINT, sessionToken } from "./session";
import type { Bundle, RepoInfo } from "./types";

function withToken(init?: RequestInit): RequestInit {
  if (!sessionToken) return init ?? {};
  const headers = new Headers(init?.headers);
  headers.set("X-Session-Token", sessionToken);
  return { ...init, headers };
}

async function asJson<T>(res: Response): Promise<T> {
  if (res.status === 401) {
    throw new Error(`401: ${MISSING_TOKEN_HINT}`);
  }
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status}: ${detail.slice(0, 300)}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchRepos(): Promise<RepoInfo[]> {
  const data = await asJson<{ repos: RepoInfo[] }>(await fetch("/api/repos", withToken()));
  return data.repos;
}

// The persisted progress log of a completed run (empty for legacy bundles).
export async function fetchLog(id: string): Promise<ProgressEvent[]> {
  const data = await asJson<{ lines: ProgressEvent[] }>(
    await fetch(`/api/repos/${encodeURIComponent(id)}/log`, withToken()),
  );
  return data.lines;
}

export async function deleteRepo(id: string): Promise<void> {
  const res = await fetch(
    `/api/repos/${encodeURIComponent(id)}`,
    withToken({ method: "DELETE" }),
  );
  await asJson<{ ok: boolean }>(res);
}

export async function clearCache(): Promise<{ cleared_bundles: number; cleared_symbol_caches: number }> {
  return asJson<{ cleared_bundles: number; cleared_symbol_caches: number }>(
    await fetch("/api/repos/clear-cache", withToken({ method: "POST" })),
  );
}

export interface PruneReport {
  removed_dirs: number;
  removed_bundles: number;
  removed_logs: number;
  freed_bytes: number;
}

export async function pruneSources(): Promise<PruneReport> {
  return asJson<PruneReport>(
    await fetch("/api/repos/prune-sources", withToken({ method: "POST" })),
  );
}

export interface FileLines {
  path: string;
  start: number;
  end: number;
  lines: { n: number; text: string }[];
}

export async function fetchFile(
  id: string,
  path: string,
  start: number,
  end: number,
): Promise<FileLines> {
  const qs = new URLSearchParams({ path, start: String(start), end: String(end) });
  return asJson<FileLines>(
    await fetch(`/api/repos/${encodeURIComponent(id)}/file?${qs}`, withToken()),
  );
}

// ---- Streaming (SSE) analysis ---------------------------------------------

export interface ProgressEvent {
  kind: string;
  message: string;
  percent?: number;
  duration_ms?: number;
}

interface DoneEvent {
  event: "done";
  repo?: RepoInfo;
  bundle?: Bundle;
}

function parseSSE(text: string): Array<Record<string, unknown>> {
  const out: Array<Record<string, unknown>> = [];
  for (const block of text.split("\n\n")) {
    for (const line of block.split("\n")) {
      if (!line.startsWith("data: ")) continue;
      try {
        out.push(JSON.parse(line.slice(6)));
      } catch {
        /* skip malformed frames */
      }
    }
  }
  return out;
}

async function readEventStream(
  res: Response,
  onProgress: (evt: ProgressEvent) => void,
): Promise<DoneEvent> {
  if (res.status === 401) {
    throw new Error(`401: ${MISSING_TOKEN_HINT}`);
  }
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status}: ${detail.slice(0, 300)}`);
  }
  if (!res.body) throw new Error("response body unavailable");
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  let done: DoneEvent | null = null;
  let error: string | null = null;

  const drain = (): boolean => {
    let idx: number;
    while ((idx = buf.indexOf("\n\n")) >= 0) {
      const block = buf.slice(0, idx);
      buf = buf.slice(idx + 2);
      for (const evt of parseSSE(block)) {
        if (evt.event === "error") {
          error = String(evt.error ?? "analysis failed");
        } else if (evt.event === "done") {
          done = evt as unknown as DoneEvent;
        } else if (typeof evt.kind === "string") {
          onProgress({
            kind: evt.kind,
            message: String(evt.message ?? ""),
            percent: typeof evt.percent === "number" ? evt.percent : undefined,
            duration_ms:
              typeof evt.duration_ms === "number" ? evt.duration_ms : undefined,
          });
        }
      }
    }
    return done !== null || error !== null;
  };

  for (;;) {
    const { value, done: streamDone } = await reader.read();
    if (value) {
      buf += decoder.decode(value, { stream: true });
      if (drain()) break;
    }
    if (streamDone) break;
  }
  if (error) throw new Error(error);
  if (!done) throw new Error("stream ended without a result");
  return done;
}

export async function analyzePathStream(
  path: string,
  onProgress: (evt: ProgressEvent) => void,
): Promise<RepoInfo> {
  const res = await fetch(
    "/api/repos/analyze?stream=true",
    withToken({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path }),
    }),
  );
  const done = await readEventStream(res, onProgress);
  if (!done.repo) throw new Error("analysis returned no repository");
  return done.repo;
}

export async function uploadZipStream(
  file: File,
  onProgress: (evt: ProgressEvent) => void,
): Promise<RepoInfo> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(
    "/api/repos/upload?stream=true",
    withToken({ method: "POST", body: form }),
  );
  const done = await readEventStream(res, onProgress);
  if (!done.repo) throw new Error("upload returned no repository");
  return done.repo;
}

export async function cloneRepoStream(
  url: string,
  onProgress: (evt: ProgressEvent) => void,
): Promise<RepoInfo> {
  const res = await fetch(
    "/api/repos/clone?stream=true",
    withToken({
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    }),
  );
  const done = await readEventStream(res, onProgress);
  if (!done.repo) throw new Error("clone returned no repository");
  return done.repo;
}

export async function fetchBundleStream(
  id: string,
  onProgress: (evt: ProgressEvent) => void,
): Promise<Bundle> {
  const res = await fetch(
    `/api/repos/${encodeURIComponent(id)}/bundle/stream`,
    withToken(),
  );
  const done = await readEventStream(res, onProgress);
  if (!done.bundle) throw new Error("bundle stream returned no data");
  return done.bundle;
}