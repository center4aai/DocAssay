import { useEffect, useRef, useState } from "react";
import { fetchFile, type FileLines } from "../api";
import { IconClose, IconFile } from "./icons";

interface Props {
  repoId: string;
  source: string;
  start: number | null;
  end: number | null;
  title: string;
  onClose: () => void;
}

export default function ProvenanceViewer({ repoId, source, start, end, title, onClose }: Props) {
  const [data, setData] = useState<FileLines | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const anchor = start ?? 1;
  // A small run of lines above the highlight is loaded up front so the window
  // can be scrolled upward; the modal auto-scrolls to the highlighted line so
  // it opens right on the claim. Both edges extend on demand.
  const [showStart, setShowStart] = useState<number>(Math.max(1, anchor - 40));
  const [showEnd, setShowEnd] = useState<number>(Math.max(end ?? anchor, anchor + 199));
  const bodyRef = useRef<HTMLDivElement>(null);
  const initialScrollDone = useRef(false);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const lo = Math.max(1, showStart);
    const hi = Math.max(showEnd, lo + 199);
    void fetchFile(repoId, source, lo, hi)
      .then((d) => setData(d))
      .catch((e) => setError(e instanceof Error ? e.message : String(e)))
      .finally(() => setLoading(false));
  }, [repoId, source, showStart, showEnd]);

  useEffect(() => {
    // On the first render only, bring the highlighted line to the top of the
    // modal. Later loads (earlier / show more) must not yank the view back.
    if (!data || initialScrollDone.current || !bodyRef.current) return;
    initialScrollDone.current = true;
    const hl = bodyRef.current.querySelector<HTMLElement>(".file-line.hl");
    if (!hl) return;
    const bodyRect = bodyRef.current.getBoundingClientRect();
    const hlRect = hl.getBoundingClientRect();
    bodyRef.current.scrollTop += hlRect.top - bodyRect.top - 8;
  }, [data]);

  const highlightLo = start ?? 1;
  const highlightHi = end ?? start ?? 1;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <strong>
            <IconFile size={15} />
            {title}
          </strong>
          <span className="muted small">{source}</span>
          <button className="close" onClick={onClose} aria-label="close">
            <IconClose size={18} />
          </button>
        </div>
        <div className="modal-body" ref={bodyRef}>
          {loading && (
            <div className="loading">
              <span className="spinner" /> Loading file…
            </div>
          )}
          {error && <div className="error">{error}</div>}
          {data && (
            <>
              <pre className="file-view">
                {data.lines.map((line) => {
                  const hl = line.n >= highlightLo && line.n <= highlightHi;
                  return (
                    <div key={line.n} className={hl ? "file-line hl" : "file-line"}>
                      <span className="line-no">{line.n}</span>
                      <span className="line-text">{line.text || " "}</span>
                    </div>
                  );
                })}
              </pre>
              <div className="modal-foot">
                <button
                  onClick={() => setShowStart((n) => Math.max(1, n - 200))}
                  className="ghost"
                  disabled={data.start <= 1}
                >
                  earlier
                </button>
                <span className="muted small">
                  lines {data.start}–{data.end}
                </span>
                <button
                  onClick={() => setShowEnd((n) => n + 200)}
                  className="ghost"
                >
                  show more
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}