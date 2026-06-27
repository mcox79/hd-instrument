# Research drill — Substrate-vs-MD head-to-head proof gate design

**Date:** 2026-06-27
**Author:** research (Director)
**Status:** DESIGN — exp_dev to author cell when Wave 4 v2 tripwire lands chain-grade
**Anchor:** `exp_substrate_vs_md_head_to_head_post_compaction_recovery_v1`
**Routing target:** `hdi_exp_dev` (dispatch deferred per gating condition below)

---

## 1. USER directive (verbatim, 2026-06-27)

> "we need to first prove that it [substrate] will do better than a stale .md and that it's updated regularly before we switch"

Gates the MEMORY.md POST-COMPACTION RITUAL flip from "Read BACKUP file directly" to "Query substrate-KB FIRST".

## 2. Honest baseline (what we know today)

**v1 metadata-index KB (smoke 2026-06-26, HARD_PASS, smoke verdict 0.66s):**
- 30 known queries: ratio_resolved = 0.933, ratio_expected_hit = 0.967
- 8 unknown queries: ratio_refused = 1.0 (perfect refusal precision)
- Returns FILENAMES, NOT CONTENT. Caller still must Read the source file.
- Operational test 2026-06-26 ~21:50: substrate query for BACKUP file took 38s end-to-end (mostly KB load) vs ~1s direct Read of `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-26.md`. **v1 added 37s of overhead and returned a pointer, not content.** MD wins decisively.

**v2 content-chunk KB (smoke 2026-06-26, HARD_PASS, smoke verdict 14.03s):**
- 152 files / 1147 chunks / avg 7.55 chunks/file / coverage_ratio 1.0
- Reingest deterministic to within 1e-06 L2
- Skunkworks tiered MEASURED_MECHANISM infra (smoke proves it RUNS; tripwire unverified)
- Wave 4 v2 tripwire-surfaced cell currently in queue per CRITICAL_CONTEXT
- **Untested at scale: 1M+ atoms (notes + memory + WordNet + VerbNet + FrameNet + GO + KEGG + NeuroLex)**

**Scheduled task `hd_director_kb_continuous_ingest`:** Ready, next run 2026-06-26 23:52 (5-min cadence).

## 3. Drill objective — operationally answer four questions

| # | Question | Metric | USER ritual-flip threshold |
|---|----------|--------|----------------------------|
| 1 | Latency | substrate end-to-end seconds vs MD Read seconds | substrate <= 2x MD |
| 2 | Completeness | does substrate return the SAME content (precision/recall of returned chunks vs ground-truth BACKUP-section text) | substrate content-match >= 0.95 |
| 3 | Freshness | how far behind filesystem is the substrate? | substrate KB last-ingest-mtime <= 10 min behind FS file mtime |
| 4 | Robustness | does substrate degrade gracefully? | filesystem-fallback path returns content within 5s in 100% of partition-fault arms |

**ALL FOUR must pass for ritual flip.** Any FAIL keeps MD canonical.

## 4. Test corpus — 20 representative post-compaction-recovery queries

Drawn from actual USER question patterns + MEMORY.md "POST-COMPACTION RITUAL" usage:

**Bucket A: directive lookup (5)**
1. "what did USER directive D6 say about substrate as definitive source"
2. "what's the no-local experiment directive"
3. "what's the stage progression rule 1-2-3-4"
4. "what did USER say about discriminator must survive scale"
5. "what's the agent-spawn-only architecture per 2026-06-26"

**Bucket B: state queries (5)**
6. "what cells are in flight right now"
7. "what's the current substrate CERT count"
8. "what's the cortex E-tensor importance state"
9. "what HARD_PASS landings happened in last 6 hours"
10. "what is the active program for compositional understanding stage 3"

**Bucket C: mechanism / cell history (5)**
11. "what is TWO_TIER generational"
12. "what was the top-K composition refuse-gate result"
13. "what is the lock-in amplifier chain-grade evidence"
14. "what is the multi-hop depth-15 evidence"
15. "what's the n1_v3 substrate-vs-unigram result"

**Bucket D: gotcha / known-pitfall (5)**
16. "what's the bigram-gap test problem"
17. "what's the band-floor results are MIDDLE_BAND rule"
18. "why is substrate-vs-MD a head-to-head test now"
19. "what's the Fix #28 violation pattern"
20. "what's the by-construction-saturation discipline"

For each query, ground truth = manually-extracted relevant section text from the source MD file (~2-5 paragraphs). Built once by exp_dev during cell-authoring, hashed, frozen as `ground_truth.jsonl`.

## 5. Cell design

### Name & location
- Cell file: `experiments/exp_substrate_vs_md_head_to_head_post_compaction_recovery_v1.py`
- Output dir: `data/exp_substrate_vs_md_head_to_head_post_compaction_recovery_v1/`
- Smoke variant: `..._v1_smoke.py` (5 queries, single arm; runs in <60s)
- Routing: `remote_cpu_queue` (USER NO LOCAL directive)

### Pre-registration (envelope-fail-bands)

```python
ENVELOPE = {
    # Latency (LOWER better)
    "hp_max_substrate_latency_ratio_vs_md": 2.0,     # substrate <= 2x MD median
    "hf_max_substrate_latency_ratio_vs_md": 5.0,     # substrate <= 5x = HARD_FAIL above

    # Completeness (HIGHER better)
    "hp_min_content_match_ratio": 0.95,              # avg-over-queries Jaccard chunk-vs-section
    "hf_min_content_match_ratio": 0.70,              # below 0.70 = HARD_FAIL

    # Freshness (LOWER lag better)
    "hp_max_freshness_lag_minutes": 10,              # substrate within 10 min of FS
    "hf_max_freshness_lag_minutes": 60,              # above 60 min = HARD_FAIL

    # Robustness (HIGHER fallback-success better)
    "hp_min_fallback_success_ratio": 1.0,            # 100% of induced-fault queries served
    "hf_min_fallback_success_ratio": 0.80,           # below 80% = HARD_FAIL
}
```

**Verdict gate:** `HARD_PASS` iff ALL 4 axes hit `hp_*` thresholds AND no axis hits `hf_*`. Otherwise `MIDDLE_BAND` if 3/4 axes pass, else `HARD_FAIL`. Anything other than HARD_PASS = ritual stays MD-first.

### Arms

**ARM 1: `ARM_LATENCY_HEAD_TO_HEAD`** (primary)
- For each of 20 queries, time wall-clock end-to-end for:
  - SUBSTRATE: `python tools/director_kb_query.py "<q>" --chunk-content --k 5` (subprocess)
  - MD: load FS index (one-time), grep across `notes/ memory/`, Read top file's relevant section
- Median + p95 ratios; per-query breakdown logged

**ARM 2: `ARM_CONTENT_COMPLETENESS`** (primary)
- For each query, extract returned content from BOTH arms
- Compute token-set Jaccard between substrate-returned-snippet UNION and ground-truth-section
- Compute precision (substrate-tokens ∈ ground-truth) and recall (ground-truth-tokens ∈ substrate)
- Per-query + macro-avg

**ARM 3: `ARM_FRESHNESS_SAMPLE`** (primary)
- Pick 5 currently-active filesystem files (e.g., recent BACKUP, MEMORY.md, fleet_waiting_on.md, director_plan.json, latest research_decisions)
- Read each file's mtime from FS
- Query substrate for each file's slug; compare KB entity's last-ingest-ts to FS mtime
- Lag = max(FS_mtime - KB_ingest_ts, 0); compute median + max across 5

**ARM 4: `ARM_ROBUSTNESS_PARTITION_FAULT`** (primary)
- Synthetic faults: rename `data/substrate_director_kb_chunk_v1/` to `_HIDDEN` for 5 queries; substrate query should refuse-gracefully OR fall back to MD path
- Verify each query still produces an answer (via filesystem fallback) within 5s
- Restore directory; verify normal operation resumes
- ALSO test partial-corruption: truncate one chunk file; verify substrate-side handles + flags

**ARM 5: `ARM_SCALE_PROBE`** (diagnostic, NOT in verdict gate)
- Repeat ARM 1 + ARM 2 with substrate query against FULL 1M+-atom KB (not smoke subset)
- This is what triggers the suspected scale-fail: char-trigram cosine at 1M atoms gets noisier
- If ARM 5 latency or completeness significantly degrade from smoke-scale, **flag in verdict_msg** even if main arms HARD_PASS — USER ritual-flip should be informed by scale behavior

### Self-tests (Fix #17 formula-selftests)
1. **Cardinality:** `len(arm1.per_query) == 20` for full (5 for smoke); `len(arm3.per_file) == 5`
2. **Verify-the-referent:** for each substrate-returned chunk, verify chunk-content actually exists in source file (cross-check via re-Read)
3. **Anti-rigging:** ground-truth sections were hashed at cell-author time; assert hash matches at run time (no post-hoc tweaking)
4. **No-silent-except:** any subprocess exception in ARM 1 substrate call HALTS the cell with verdict UNKNOWN, not silent skip
5. **Discriminator-survives-scale:** ARM 5 diagnostic flag MUST be surfaced in verdict_msg; if ARM 5 substrate fails AND ARMs 1-4 pass, ritual flip is BLOCKED pending ARM 5 root-cause

### Smoke variant
- 5 queries (1 per bucket A/B/C/D/extra), single ARM_LATENCY + single ARM_CONTENT
- HARD_PASS if substrate completes without error AND latency-ratio <= 5 AND content-match >= 0.5
- Purpose: prove cell RUNS end-to-end; full-N preview NOT possible (per Fix from 2026-06-26 — smoke at full-N substitute = ARM 5 SCALE_PROBE in main cell)

## 6. Bias-checklist application (USER 2026-06-24 master checklist)

Mapping to the 12+8 known biases:

- **BIAS-N (verify-referent-verdict-field):** primary defense via Self-test 2 — every substrate-returned chunk re-Read for ground truth
- **BIAS-O (basis-vs-use-case):** queries cover D buckets (directive, state, mechanism, gotcha) not just one regime
- **BIAS-Q (suspect 1.000 results):** ARM 4 `hp_min_fallback_success_ratio = 1.0` is suspect-pure; mitigated by tracking PARTIAL successes separately
- **BIAS-S (band-calibration regime checks):** ARM 5 SCALE_PROBE explicit — smoke-scale bands DO NOT transfer to 1M-atom-scale
- **BIAS-M (production-scale instrument calibration):** entire cell exists because v1 smoke HARD_PASS misled MEMORY.md ritual; production-scale recovery use is the calibration target
- **BIAS-13 (contamination):** ground-truth sections curated by exp_dev from CURRENT BACKUP file; potential leak — mitigated by using OLDER BACKUP (2026-06-26 frozen) so substrate cannot have learned from it post-hoc
- **BIAS-14 (regime mismatch):** USER's actual post-compaction queries may not match my 20 — flagged for USER review of query list before dispatch

## 7. Gating + dispatch sequence

**Gate (must hold before dispatch):**
1. Wave 4 v2 tripwire-surfaced cell has landed AND been tiered chain-grade by Skunkworks
2. Full 1M-atom content-chunk KB has been built (not just 152-file smoke); verify via `ls data/substrate_director_kb_chunk_v1/`
3. Scheduled task `hd_director_kb_continuous_ingest` has been ingesting for >=24h (cadence proven, not just one-shot smoke)

**Dispatch sequence:**
1. exp_dev authors cell from this design + ground-truth.jsonl (~1 cycle)
2. Cell-author smoke on remote_cpu_queue (~5min wall)
3. If smoke HARD_PASS: full dispatch on remote_cpu_queue (~30-60min wall expected; bounded by 20 queries x ~5s substrate + ~3s MD per arm)
4. Skunkworks cert-verdict on landing
5. **If HARD_PASS:** Director reports to USER + proposes MEMORY.md ritual edit; USER approves before flip
6. **If MIDDLE_BAND or HARD_FAIL:** Director files cap_map decision; MD ritual STAYS; identify failing axis; route follow-up cells

**Why not auto-flip on HARD_PASS:** USER's directive says "prove" — proof requires USER review of the proof, not just a green verdict. Ritual flip is a USER decision.

## 8. Cell file structure (for exp_dev)

```
experiments/exp_substrate_vs_md_head_to_head_post_compaction_recovery_v1.py
    # imports: pathlib, time, json, subprocess, hashlib, re
    # imports: hdlab.director_kb_query (for direct in-process timing baseline)

    GROUND_TRUTH_PATH = "experiments/_ground_truth/substrate_vs_md_v1.jsonl"
    QUERIES = [...]  # 20 entries, schema: {id, bucket, q, expected_files, ground_truth_text, gt_hash}
    ENVELOPE = {...}  # per Section 5

    def arm_latency_head_to_head(queries) -> dict
    def arm_content_completeness(queries, ground_truth) -> dict
    def arm_freshness_sample(file_list) -> dict
    def arm_robustness_partition_fault(queries) -> dict
    def arm_scale_probe(queries, ground_truth) -> dict  # diagnostic

    def selftest_cardinality(arms) -> None
    def selftest_verify_referent(arm2) -> None
    def selftest_antirigging(queries) -> None  # gt_hash match check

    def verdict_compute(arms, envelope) -> tuple[str, str]
    def main():
        load ground truth, run 5 arms in sequence, run selftests, write metrics.json + verdict
```

```
experiments/_ground_truth/substrate_vs_md_v1.jsonl
    # 20 lines, one per query
    # {"id":1, "bucket":"A", "q":"...", "expected_files":["notes/..."],
    #  "ground_truth_text":"...full paragraph(s)...", "gt_hash":"sha256:..."}
```

```
experiments/exp_substrate_vs_md_head_to_head_post_compaction_recovery_v1_smoke.py
    # 5 queries, ARM_LATENCY + ARM_CONTENT only, <60s wall budget
    # HARD_PASS gates dispatch of full cell
```

## 9. Decision-tree on outcomes

| Verdict | Action |
|---------|--------|
| HARD_PASS (all 4 axes + ARM 5 OK) | Report to USER; propose MEMORY.md edit; await approval |
| HARD_PASS (all 4 axes) + ARM 5 FLAG | Report to USER; flag scale-degradation; ritual flip BLOCKED pending ARM 5 root-cause cell |
| MIDDLE_BAND (3/4 axes) | File cap_map decision; identify which axis failed; route remediation (e.g., if freshness failed, debug continuous-ingest cadence) |
| HARD_FAIL (any axis hf-tripped) | MD stays canonical; substrate-KB is not yet production-recovery-grade; defer ritual-flip indefinitely until v3 |

## 10. Open questions for USER (record, do NOT ask)

Per "never use AskUserQuestion" — I record these for USER awareness; will proceed with defaults unless USER overrides:

1. **20-query list approval:** USER may want different / additional queries that match actual post-compaction question patterns. Default: proceed with my 20 (4 buckets x 5).
2. **Ritual-flip is gated on USER review even after HARD_PASS:** my default — no auto-flip. USER may want auto-flip on HARD_PASS to reduce friction.
3. **ARM 5 SCALE_PROBE is diagnostic-only or also gates?** My default: diagnostic-only; flag scale issues in verdict_msg but don't block ritual-flip on ARM 5 alone (since substrate might HARD_PASS on smoke-scale queries that match real USER patterns even if 1M-atom-scale degrades on edge queries). USER may want it elevated to verdict-gate.

## 11. Status

- Design: DONE (this doc)
- Cell-author dispatch: GATED on Wave 4 v2 tripwire-surfaced cell landing chain-grade + 1M-atom content-chunk KB built + continuous-ingest 24h proven
- Estimated dispatch eligibility: 1-3 cycles from now (depends on Wave 4 v2 landing timing)
- Owner on dispatch: spawn `hdi_exp_dev` with pointer to this doc + ground-truth-build instructions in Section 8

---

**End of design.** exp_dev: when gating conditions hold, author cell per Sections 5+8, build ground-truth.jsonl per Section 4, dispatch smoke first, then full per Section 7.
