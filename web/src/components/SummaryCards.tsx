import type { Meta } from "../types";
import { IconCheck, IconX, IconFile, IconShield, IconUpload, IconGlobe, IconSearch } from "./icons";

interface Props {
  meta: Meta;
}

export default function SummaryCards({ meta }: Props) {
  const cards: { label: string; value: string; cls?: string; icon?: React.ReactNode }[] = [
    { label: "SUPPORTED", value: String(meta.verdicts.SUPPORTED ?? 0), cls: "sup", icon: <IconCheck size={15} /> },
    { label: "REFUTED", value: String(meta.verdicts.REFUTED ?? 0), cls: "ref", icon: <IconX size={15} /> },
    { label: "NEI", value: String(meta.verdicts.NEI ?? 0), cls: "nei", icon: <IconFile size={15} /> },
    { label: "coverage", value: meta.coverage.toFixed(2), icon: <IconShield size={15} /> },
    { label: "claims", value: String(meta.claims), icon: <IconUpload size={15} /> },
    { label: "referents", value: String(meta.referents), icon: <IconGlobe size={15} /> },
    { label: "evidence", value: String(meta.evidence), icon: <IconSearch size={15} /> },
  ];
  return (
    <div className="summary-grid">
      {cards.map((c) => (
        <div key={c.label} className={`summary-card${c.cls ? ` sc-${c.cls}` : ""}`}>
          <div className="summary-label" style={{ display: "flex", alignItems: "center", gap: 6 }}>
            {c.icon}
            {c.label}
          </div>
          <div className="summary-value">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
