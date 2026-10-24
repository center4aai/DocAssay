# Stage C — LLM annotation arm (supplementary)

**LLM annotation arm (supplementary confirmation).** Three LLM annotators label
the blind sheet; the report is provisional.

- annotators: claude-haiku-5-5, glm-5.3-flash, qwen3.8-flash
- rows: 132
- coverage: {'claude-haiku-5-5': 132, 'glm-5.3-flash': 132, 'qwen3.8-flash': 132}

| field | Fleiss κ | % agreement | pairwise Cohen | majority |
|---|---:|---:|---|---|
| claim_type | 1.0 | 1.0 | claude-haiku-5-5 vs glm-5.3-flash: 1.0; claude-haiku-5-5 vs qwen3.8-flash: 1.0; glm-5.3-flash vs qwen3.8-flash: 1.0 | {'current_claim': 129, 'illustrative': 3} |
| claim_form | 0.9867 | 0.9848 | claude-haiku-5-5 vs glm-5.3-flash: 1.0; claude-haiku-5-5 vs qwen3.8-flash: 0.98; glm-5.3-flash vs qwen3.8-flash: 0.98 | {'bare': 15, 'bare_call': 4, 'dependency': 26, 'not_a_claim': 3, 'path': 41, 'qualified': 4, 'section_qualified': 39} |
| context_source | 0.9049 | 0.9318 | claude-haiku-5-5 vs glm-5.3-flash: 1.0; claude-haiku-5-5 vs qwen3.8-flash: 0.858; glm-5.3-flash vs qwen3.8-flash: 0.858 | {'heading': 19, 'list': 7, 'none': 93, 'path_prose': 1, 'prose': 5, 'table': 7} |
| defect_is_real | 1.0 | 1.0 | claude-haiku-5-5 vs glm-5.3-flash: 1.0; claude-haiku-5-5 vs qwen3.8-flash: 1.0; glm-5.3-flash vs qwen3.8-flash: 1.0 | {'n/a': 27, 'yes': 105} |
| nei_reason_applies | 0.4887 | 0.6742 | claude-haiku-5-5 vs glm-5.3-flash: 0.4206; claude-haiku-5-5 vs qwen3.8-flash: 0.3858; glm-5.3-flash vs qwen3.8-flash: 0.9447 | {'n/a': 3, 'no': 110, 'yes': 19} |
| none_claim_not_extracted | 1.0 | 1.0 | claude-haiku-5-5 vs glm-5.3-flash: 1.0; claude-haiku-5-5 vs qwen3.8-flash: 1.0; glm-5.3-flash vs qwen3.8-flash: 1.0 | {'no': 129, 'yes': 3} |
| control_false_positive | 1.0 | 1.0 | claude-haiku-5-5 vs glm-5.3-flash: 1.0; claude-haiku-5-5 vs qwen3.8-flash: 1.0; glm-5.3-flash vs qwen3.8-flash: 1.0 | {'n/a': 108, 'yes': 24} |
| same_artifact | None | 1.0 | claude-haiku-5-5 vs glm-5.3-flash: None; claude-haiku-5-5 vs qwen3.8-flash: None; glm-5.3-flash vs qwen3.8-flash: None | {'n/a': 132} |

## KPI checks (majority label)

| check | count |
|---|---:|
| injection_defect_real_yes | 105 |
| injection_defect_real_no | 0 |
| injection_defect_real_na | 3 |
| control_true_yes | 24 |
| control_false_positive_no | 0 |
| nei_legitimate_yes | 8 |
| nei_legitimate_no | 7 |
| none_is_miss_no | 4 |
| none_is_miss_yes | 0 |

## Sensitivity: NEI legitimacy

- operator KPI (REFUTED + every NEI): 65/69
- LLM-validated (REFUTED + legitimate NEI): 58/69 = 0.8406
- NEI legitimate: 8; not legitimate: 7

A κ near 0 means the LLM annotators do not reproduce each other; it is
reported, not hidden. This arm is supplementary confirmation only.
