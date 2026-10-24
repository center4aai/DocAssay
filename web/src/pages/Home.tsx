import { useCallback, useEffect, useMemo, useState } from "react";
import {
  analyzePathStream,
  clearCache,
  cloneRepoStream,
  deleteRepo,
  fetchRepos,
  pruneSources,
  uploadZipStream,
  type ProgressEvent,
} from "../api";
import type { RepoInfo } from "../types";
import UploadZone from "../components/UploadZone";
import { monogram, phaseLabel, type PhaseTiming } from "../components/ui";
import { IconGlobe, IconFolder, IconTrash, IconRefresh, IconUpload, IconShield } from "../components/icons";
import AnalyzingLog, { type LogLine } from "../components/AnalyzingLog";

function toLogLine(evt: ProgressEvent): LogLine {
  return { kind: (evt.kind as LogLine["kind"]) || "info", message: evt.message };
}

// Mirrors the server's `_normalize_repo_url`: a trailing slash and `.git` do
// not distinguish two clones of the same remote.
function normalizeRepoUrl(url: string): string {
  return url.trim().replace(/\.git$/i, "").replace(/\/+$/, "").toLowerCase();
}

export default function Home() {
  const [repos, setRepos] = useState<RepoInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [path, setPath] = useState("");
  const [url, setUrl] = useState("");
  const [busy, setBusy] = useState<string | null>(null);
  const [logEvents, setLogEvents] = useState<LogLine[]>([]);
  const [progress, setProgress] = useState<number | null>(null);
  const [phases, setPhases] = useState<PhaseTiming[]>([]);
  const [runId, setRunId] = useState(0);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setRepos(await fetchRepos());
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  // Remotes already downloaded: cloning one of these refreshes the existing
  // checkout instead of adding a second copy.
  const downloadedUrls = useMemo(
    () =>
      new Set(
        repos
          .filter((r) => r.kind === "clone" && r.url)
          .map((r) => normalizeRepoUrl(r.url as string)),
      ),
    [repos],
  );
  const willReuse = url.trim() !== "" && downloadedUrls.has(normalizeRepoUrl(url));

  const { claims, refuted } = useMemo(() => {
    let claims = 0;
    let refuted = 0;
    for (const repo of repos) {
      if (!repo.analyzed || !repo.meta) continue;
      claims += repo.meta.claims;
      refuted += repo.meta.verdicts.REFUTED ?? 0;
    }
    return { claims, refuted };
  }, [repos]);

  const onProgress = useCallback((evt: ProgressEvent) => {
    // Phase timing frames (clone / extract / analyze) are not terminal lines:
    // they feed the phase summary instead of the scrolling log.
    if (evt.kind === "timing" && typeof evt.duration_ms === "number") {
      setPhases((prev) => [...prev, { label: phaseLabel(evt.message), ms: evt.duration_ms as number }]);
      return;
    }
    setLogEvents((prev) => [...prev, toLogLine(evt)]);
    if (typeof evt.percent === "number") setProgress(evt.percent);
  }, []);

  const startRun = useCallback(() => {
    setLogEvents([]);
    setProgress(null);
    setPhases([]);
    setRunId((r) => r + 1);
  }, []);

  const onAnalyzePath = async () => {
    if (!path.trim()) return;
    setBusy("analyzing");
    setError(null);
    startRun();
    try {
      const repo = await analyzePathStream(path.trim(), onProgress);
      setPath("");
      await refresh();
      window.location.hash = `#/repo/${encodeURIComponent(repo.id)}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  };

  const onUpload = async (file: File) => {
    setBusy("uploading");
    setError(null);
    startRun();
    try {
      const repo = await uploadZipStream(file, onProgress);
      await refresh();
      window.location.hash = `#/repo/${encodeURIComponent(repo.id)}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  };

  const onClone = async () => {
    if (!url.trim()) return;
    setBusy("cloning");
    setError(null);
    startRun();
    try {
      const repo = await cloneRepoStream(url.trim(), onProgress);
      setUrl("");
      await refresh();
      window.location.hash = `#/repo/${encodeURIComponent(repo.id)}`;
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  };

  const open = (id: string) => {
    window.location.hash = `#/repo/${encodeURIComponent(id)}`;
  };

  const onDelete = async (repo: RepoInfo) => {
    const kindNote =
      repo.kind === "upload" || repo.kind === "clone"
        ? "\nThe downloaded source copy will be removed from the server."
        : "\nThe source tree on disk is kept; only the analysis is removed.";
    if (!window.confirm(`Delete analysis of "${repo.name}"?${kindNote}`)) return;
    setBusy("deleting");
    setError(null);
    try {
      await deleteRepo(repo.id);
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  };

  const onClearCache = async () => {
    if (
      !window.confirm(
        "Clear cached analyses?\nRepositories stay listed but are re-analyzed on the next open (bundles + AST symbol caches are removed).",
      )
    )
      return;
    setBusy("clearing");
    setError(null);
    try {
      const res = await clearCache();
      await refresh();
      setError(`Cache cleared: ${res.cleared_bundles} bundle(s), ${res.cleared_symbol_caches} symbol cache(s).`);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  };

  const onPruneSources = async () => {
    setBusy("pruning");
    setError(null);
    try {
      const res = await pruneSources();
      await refresh();
      const mb = (res.freed_bytes / (1024 * 1024)).toFixed(1);
      setError(
        `Pruned orphan sources: ${res.removed_dirs} dir(s), ${res.removed_bundles} bundle(s), ${res.removed_logs} log(s) — ${mb} MB freed.`,
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="page">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">
            <IconShield size={22} />
          </span>
          <span className="brand-text">
            <h1>DocAssay</h1>
            <span className="sub">documentation ↔ code verification</span>
          </span>
        </div>
      </header>

      <section className="intro">
        <div>
          <h2>Documentation verified against code.</h2>
          <p className="intro-lede">
            Add a repository to audit its claims — verdicts, evidence and source
            provenance in one pass.
          </p>
        </div>
        {repos.length > 0 && (
          <div className="intro-stats">
            <div>
              <span>repositories</span>
              <strong>{repos.length}</strong>
            </div>
            <div>
              <span>claims</span>
              <strong>{claims}</strong>
            </div>
            <div>
              <span>refuted</span>
              <strong className="stat-ref">{refuted}</strong>
            </div>
          </div>
        )}
      </section>

      <section className="actions">
        <div className="action-block">
          <div className="action-title">
            <IconUpload size={17} />
            Upload
          </div>
          <div className="action-desc">Analyze a repository from a zip archive</div>
          <UploadZone onUpload={onUpload} disabled={busy !== null} />
        </div>

        <div className="action-block">
          <div className="action-title">
            <IconGlobe size={17} />
            Clone
          </div>
          <div className="action-desc">Clone a remote repository and analyze it</div>
          <div className="path-form">
            <input
              type="text"
              placeholder="https://github.com/org/repo"
              value={url}
              disabled={busy !== null}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void onClone();
              }}
            />
            <button
              className="primary"
              onClick={() => void onClone()}
              disabled={busy !== null || !url.trim()}
            >
              {busy === "cloning"
                ? "Cloning…"
                : willReuse
                  ? "Refresh & analyze"
                  : "Clone & analyze"}
            </button>
          </div>
          {willReuse && (
            <div className="action-hint">
              Already downloaded — the existing checkout will be refreshed, not cloned again.
            </div>
          )}
        </div>

        <div className="action-block">
          <div className="action-title">
            <IconFolder size={17} />
            Local path
          </div>
          <div className="action-desc">Analyze a directory on this machine</div>
          <div className="path-form">
            <input
              type="text"
              placeholder="/path/to/a/repository"
              value={path}
              disabled={busy !== null}
              onChange={(e) => setPath(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") void onAnalyzePath();
              }}
            />
            <button
              className="primary"
              onClick={() => void onAnalyzePath()}
              disabled={busy !== null || !path.trim()}
            >
              {busy === "analyzing" ? "Analyzing…" : "Analyze path"}
            </button>
          </div>
        </div>
      </section>

      {(busy === "uploading" || busy === "cloning" || busy === "analyzing") && (
        <AnalyzingLog
          key={runId}
          title={
            busy === "uploading"
              ? "Extracting & analyzing"
              : busy === "cloning"
                ? "Cloning & analyzing"
                : "Analyzing"
          }
          events={logEvents}
          pending
          percent={progress}
          phases={phases}
        />
      )}

      {error && <div className="error">{error}</div>}

      <div className="section-head">
        <h2>
          <IconShield size={15} />
          Repositories
        </h2>
        <div className="section-actions">
          <button
            className="ghost icon-btn"
            onClick={() => void onPruneSources()}
            disabled={busy !== null}
            title="Delete downloaded source trees that no longer have an analysis"
          >
            <IconTrash size={14} />
            Prune sources
          </button>
          <button
            className="ghost icon-btn"
            onClick={() => void onClearCache()}
            disabled={busy !== null}
          >
            <IconRefresh size={14} />
            Clear cache
          </button>
        </div>
      </div>

      <section className="repo-grid">
        {loading ? (
          <div className="loading">
            <span className="spinner" /> Loading repositories…
          </div>
        ) : repos.length === 0 ? (
          <div className="empty-state">
            <IconUpload size={34} />
            <div>
              No repositories yet — clone a URL, upload a zip, or analyze a path.
            </div>
          </div>
        ) : (
          repos.map((repo) => (
            <div key={repo.id} className="repo-card-wrap">
              <button className="repo-card" onClick={() => open(repo.id)}>
                <div className="repo-card-head">
                  <span className="repo-card-title">
                    <span className="repo-monogram">{monogram(repo.name)}</span>
                    <strong>{repo.name}</strong>
                  </span>
                </div>
                {repo.analyzed && repo.meta ? (
                  <div className="repo-card-meta">
                    <div>
                      <span className="count sup">{repo.meta.verdicts.SUPPORTED ?? 0}</span>
                      <span className="count ref">{repo.meta.verdicts.REFUTED ?? 0}</span>
                      <span className="count nei">{repo.meta.verdicts.NEI ?? 0}</span>
                    </div>
                    <div className="muted small">
                      {repo.meta.claims} claims · {repo.meta.evidence} evidence · coverage{" "}
                      {repo.meta.coverage.toFixed(2)}
                    </div>
                  </div>
                ) : (
                  <div className="muted small">available — open to analyze</div>
                )}
                <div className="repo-card-foot">
                  <span className={`badge kind-${repo.kind}`}>{repo.kind}</span>
                  <span className="muted tiny" style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {repo.url ?? repo.source}
                  </span>
                </div>
              </button>
              <button
                className="ghost repo-delete"
                title="Delete this analysis"
                aria-label={`Delete ${repo.name}`}
                disabled={busy !== null}
                onClick={() => void onDelete(repo)}
              >
                <IconTrash size={16} />
              </button>
            </div>
          ))
        )}
      </section>
    </div>
  );
}