# Curated triaged exemplars — real-incident harvest

This source tops up the thin `identifier-drift` class. Every row is a real
public commit whose **parent tree already carried the renamed identifier**, while
the cited document line still used the old name. The commit repairs that line;
`scripts/fetch_exemplar_evidence.py` extracts the before/after diff into
`../evidence/`. Nothing here comes from the `readu_raw` LLM-hypothesis pool, and
nothing is rendered from the controls pool.

## Bank effect

| class | triaged |
|---|---:|
| `path-location-drift` | 12 |
| `external-dependency-drift` | 11 |
| `removed-referent-drift` | 9 |
| `identifier-drift` | 8 |
| **total triaged** | **40** |

The `raw` pool stays at **713** and the `controls` pool at **81**; both remain
separate and are never merged into `triaged`.

## Added curated incidents

- `ident-nseindia-list-sme` — identifier-drift — BennyThadikaran/NseIndiaApi — https://github.com/BennyThadikaran/NseIndiaApi/commit/0e0a77bb98eac005fdabcaca51b6e14f8da59e79
  - location: `src/nse/NSE.py:993`
  - quote: Documentation references `listSme`, but the identifier was renamed to `list_sme`.
  - triage: Parent tree already defines list_sme() and list_equity_stocks_by_index(); the docstrings still used the pre-rename camelCase names. The commit updates the docstring references (one :ref: anchor remains stale). Manually verified against the parent tree before adding.
- `ident-immosquare-my-ip` — identifier-drift — immosquare/immosquare-constants — https://github.com/immosquare/immosquare-constants/commit/92ab4acea6a497ddcbd53641fcbbcb655379eff5
  - location: `CLAUDE.md:23`
  - quote: Documentation references `get_my_ip_from_aws`, but the identifier was renamed to `my_ip_from_aws`.
  - triage: Parent tree defines my_ip_from_aws() and keeps get_my_ip_from_aws() only as a deprecated alias; the project guide still named the deprecated method. Manually verified against the parent tree before adding.
- `ident-casehub-incident-summary` — identifier-drift — casehubio/soc — https://github.com/casehubio/soc/commit/a38e2e1ad72ede05fa819efd9f8f6c4bde8f05d4
  - location: `docs/specs/issue-32-incident-summary-createdat/2026-08-18-incident-summary-createdat-design.md:8`
  - quote: Documentation references `IncidentSummaryDto`, but the identifier was renamed to `IncidentSummaryResponse`.
  - triage: Parent tree has IncidentSummaryResponse (IncidentSummaryDto is absent); the design spec still pointed at the old DTO name. The fix updates line 8 and the resource; the title line remains stale. Manually verified against the parent tree before adding.
- `ident-silo-refresh-devices` — identifier-drift — amontlabs/silo — https://github.com/amontlabs/silo/commit/d70ae0855e53f10ad0d754d9511a8264bc54472e
  - location: `docs/SiloUI-CHECKPOINTS-PLAN.md:181`
  - quote: Documentation references `refreshComputers`, but the identifier was renamed to `refreshDevices`.
  - triage: Parent tree defines refreshDevices() and no refreshComputers(); the plan document still cited the old function name. Manually verified against the parent tree before adding.

## Reclassified READU incidents (ruleset 2026-10-20)

- `triaged:alert-4a2f8a3f229f0f7f` — `unclassified` → `identifier-drift` —
  `https://github.com/Significant-Gravitas/AutoGPT/commit/cf6e724e99ef288f743e63aa3b092576a6940911`
  — `FORM_CREATOR.md` still destructures `id`, code renames it to `id: fieldId`.
- `triaged:alert-4e6ffd8b9ad6347e` — `path-location-drift` → `identifier-drift` —
  same commit — `FORM_CREATOR.md` uses `fieldKey`, code renamed it to `arrayFieldHandleId`.

## Ruleset change

`exemplars/rules.json` was bumped from `2026-10-13` to `2026-10-20`. The path
rule gained a `none_of` guard for `code renamed it to ...`, and the identifier
rule gained a present-tense `renames it to` pattern. Rationale: the path rule
claimed to guard against symbol renames but did not, so a field rename that
mentioned `FORM_CREATOR.md` was assigned to `path-location-drift`. The change
moves exactly the two real READU field-rename incidents above; it does not move
any `raw` hypothesis, and the two moved rows are still real human-triaged TPs.

## Verification

For identifier-drift rows the parent tree defines the new symbol (the old one is
absent or a deprecated alias) and the document line names the old symbol.
Evidence files are deterministic:
`{status, commit_sha, patch_sha256, locations, files[...]}` with no timestamps.
