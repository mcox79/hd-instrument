# Skunkworks audit: exp_dev instruction files — 2026-06-27

## Scope
Per USER directive 2026-06-27, audit `.claude/agents/exp_dev.md` + `.claude/agents/hdi_exp_dev.md` for completeness against 7 discipline lessons surfaced TODAY by Research, then implement the update.

## Files audited
- `d:/AI/hd-instrument/.claude/agents/exp_dev.md` (162 lines, mtime 2026-06-27 03:59 — CANONICAL, actively maintained)
- `C:/Users/marsh/.claude/agents/hdi_exp_dev.md` (75 lines, mtime 2026-06-21 — home-dir legacy stub)
- `C:/Users/marsh/.claude/agents/exp_dev.md` (69 lines, mtime 2026-05-27 — very stale; references role contract file)
- `d:/AI/hd-instrument/tools/orchestrator/agents/exp_dev.md` (374 lines — role-contract reference, NOT the spawn-loaded file under Agent Teams architecture)

The canonical file under Agent Teams is the repo-local `d:/AI/hd-instrument/.claude/agents/exp_dev.md`.

## 7-lesson gap analysis (PRE-audit)
1. **META_RULE_AF arms-must-differ** — MISSING (only ad-hoc + optional in some cells)
2. **META_RULE_AH atomic-final-metrics-write** — MISSING (no path-discipline rule)
3. **`except SystemExit: raise` BEFORE `BaseException`** — PARTIAL (Section "NO SILENT except: BLOCKS" exists but does not address BaseException-vs-SystemExit ordering specifically)
4. **CRLB formula validation** — MISSING (calibration-probe band-width section mentions ±50% bands but no analytical floor / reachability validation)
5. **META_RULE_AG substrate-too-robust-for-default-regime** — PARTIAL (DISCRIMINATOR-MUST-SURVIVE-SCALE is adjacent but doesn't enforce baseline_in_band 0.05<x<0.95)
6. **HYPOTHESIZED vs MEASURED marking (META_RULE_AC)** — MISSING (cited-number discipline not in cell-template)
7. **Discriminator-must-survive-scale** — PRESENT (full section lines 68-92; already MANDATORY)

## Edits implemented (in `d:/AI/hd-instrument/.claude/agents/exp_dev.md`)

Added section "ADDITIONAL CELL-TEMPLATE MANDATES (2026-06-27 — codification of META_RULE_AC/AF/AG/AH + 3 related)" after the existing SCHEMA-VET PRE-DISPATCH CHECKLIST. Numbered 6 through 12:

- **§6 ARMS-MUST-DIFFER self-test (META_RULE_AF)** — paste-ready Python helper using SHA-256 of tobytes(); MANDATORY at smoke gate; pre-reg field `arms_differ_verified`; explicit exemption mechanism for legitimately-shared outputs (`arms_differ_exempted` list with rationale per pair)
- **§7 ATOMIC-FINAL-METRICS-WRITE (META_RULE_AH)** — three acceptable solutions (per-iter distinct paths / tmp+os.replace / `tuning_iteration_count` field); pre-reg field `final_metrics_atomicity` REQUIRED; default-reject if missing
- **§8 `except SystemExit: raise` ordering** — mandatory outer try/except ordering (SystemExit / KeyboardInterrupt / Exception — never BaseException); pre-flight grep gate `grep -nE "except\s+BaseException"` BLOCKS dispatch; same for bare `except:`
- **§9 CRLB / capacity-feasibility validation** — pre-reg fields `crlb_floor_computed`, `crlb_formula_reference`, `discriminator_reachability`; explicit `crlb_n/a` opt-out if formula doesn't apply (silent omission = REJECT)
- **§10 Substrate-too-robust-for-default-regime (META_RULE_AG)** — smoke-gate check `0.05 < baseline_score < 0.95` per baseline arm; ITERATE_REGIME flag if out of band; pre-reg field `baseline_in_band`; relation to SCALE rule clarified (both required, neither suffices)
- **§11 HYPOTHESIZED vs MEASURED (META_RULE_AC)** — 4 explicit tags (MEASURED@path / HYPOTHESIZED@prereg / THEORETICAL@formula / CITED@source); untagged numbers in spawn-prompts REJECT; in verdict reports auto-MIDDLE_BAND pending re-source
- **§12 Cell-template summary block** — paste-at-top-of-every-cell comment block listing all 11+ mandatory checks; `BLOCK_DISPATCH_META_RULE_<X>` sentinel for any smoke-gate fail

Two stub files updated with pointers to the canonical instruction file:
- `C:/Users/marsh/.claude/agents/hdi_exp_dev.md` — added "CANONICAL INSTRUCTION FILE" pointer section listing the four MANDATORY sections in the repo-local file
- `C:/Users/marsh/.claude/agents/exp_dev.md` — added "ALSO REQUIRED" note directing to repo-local file (in addition to existing role-contract pointer)

No git commit yet (per Skunkworks discipline: do not auto-commit; surface for review). Edits are on-disk and immediately effective for any new exp_dev spawn loaded against the repo-local agent file.

## Additional gaps surfaced beyond the 7 lessons
- **Stale stub files** — `hdi_exp_dev.md` (Jun 21) and home-dir `exp_dev.md` (May 27) drift out of sync with canonical repo file. Mitigation in place: pointer sections; long-term fix should be a periodic three-way diff cadence (META rule candidate below).
- **No explicit "exp_dev spawn-discovery" checklist** — agents must discover the 12 mandates from the file text; format is prose interleaved with templates. A top-of-file "MANDATORY CHECKLIST" 12-line summary would speed scanning. (Partially mitigated by §12 cell-template summary block; consider also a file-top mirror.)
- **No `hd-instrument`-local cell-author smoke-gate script** that automates §§6-11 mechanically. Today's rules require self-discipline; a tool like `tools/smoke_gate_meta_rules.py` could enforce mechanically. Out of scope for this audit; recommend filing as exp_dev / Director cycle.
- **HP_SCOPE per-arm scope (§5b, already added 2026-06-27)** mentions Skunkworks batch-7 flag-back but doesn't cross-reference the bare-baseline failure-mode atom in Store (`meta` corpus). META-RULE atom for HP_SCOPE should be filed.

## META rule candidates from this audit (CERT-neutral; for atomization)
1. **META_RULE_AI agent-instruction-files-need-periodic-discipline-audit-cadence** — agent .md files drift between the canonical (repo-local) and stub (home-dir) copies; without a fortnightly diff-cadence, spawns loading the wrong file silently regress. Recommended cadence: Skunkworks runs three-way diff at every major META rule addition + monthly proactive.
2. **META_RULE_AJ cell-template-summary-block-mirrored-at-cell-top** — agent-instruction files should mirror their cell-template mandate block at the TOP of every cell script (not just in the agent .md). Mechanical enforcement via cell-skeleton generator.
3. **META_RULE_AK rejection-default-on-missing-pre-reg-field** — every MANDATORY pre-reg field added to exp_dev instructions should default to REJECT-on-missing (not "silent omission accepted"). Today's audit added 4 new mandatory fields (`arms_differ_verified`, `final_metrics_atomicity`, `crlb_floor_computed`, `baseline_in_band`); all spec REJECT semantics.
4. **META_RULE_AL spawn-prompt-number-tagging-discipline (direct codification of META_RULE_AC into spawn-prompt template)** — extend MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ tagging to the agent spawn prompt itself (not just cell-design notes). Research's spawn prompts have been the source of 3+ phantom-vet batches today.

## Net result
- 7-of-7 USER-flagged lessons now locked in canonical exp_dev.md (4 new sections, 1 promoted from optional to mandatory, 2 had partial coverage extended)
- 2 stale stub files pointed to canonical
- 4 META rule candidates surfaced for Director / atomization cycle
- No git push (edits surfaced for review per Skunkworks discipline)

File path: `d:/AI/hd-instrument/notes/skunkworks_exp_dev_md_audit_2026-06-27.md`
