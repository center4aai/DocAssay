import { IconSearch } from "./icons";

export interface Filters {
  predicate: string;
  verdict: string;
  domain: string;
  search: string;
}

export const DEFAULT_FILTERS: Filters = {
  predicate: "",
  verdict: "",
  domain: "",
  search: "",
};

interface Props {
  predicates: string[];
  domains: string[];
  filters: Filters;
  onChange: (next: Filters) => void;
}

export default function FilterBar({ predicates, domains, filters, onChange }: Props) {
  const set = (patch: Partial<Filters>) => onChange({ ...filters, ...patch });
  return (
    <div className="filter-bar">
      <select
        value={filters.predicate}
        onChange={(e) => set({ predicate: e.target.value })}
        aria-label="predicate"
      >
        <option value="">all predicates</option>
        {predicates.map((p) => (
          <option key={p} value={p}>
            {p}
          </option>
        ))}
      </select>
      <select
        value={filters.domain}
        onChange={(e) => set({ domain: e.target.value })}
        aria-label="domain"
      >
        <option value="">all domains</option>
        {domains.map((d) => (
          <option key={d} value={d}>
            {d === "" ? "root" : d}
          </option>
        ))}
      </select>
      <select value={filters.verdict} onChange={(e) => set({ verdict: e.target.value })} aria-label="verdict">
        <option value="">all verdicts</option>
        <option value="SUPPORTED">SUPPORTED</option>
        <option value="REFUTED">REFUTED</option>
        <option value="NEI">NEI</option>
      </select>
      <div className="search-wrap">
        <IconSearch size={15} />
        <input
          type="search"
          placeholder="search object…"
          value={filters.search}
          onChange={(e) => set({ search: e.target.value })}
        />
      </div>
    </div>
  );
}