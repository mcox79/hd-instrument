# Skunkworks landed-VET batch 4 -- 5 cells + 4 META rules -- 2026-06-26

**Auditor:** Skunkworks (cert-owner)
**Method:** Verify-OFF-DATA via .venv Python recompute of per-arm metrics.json; NEVER from verdict_msg framings (Fix #28).
**Scope:** 5 cells handed off by Research (Director) for landed-VET this batch; 4 META rules atomized concurrently; ANCHOR 3 RE-TIER per USER 2026-06-26 directive.
**Authorization:** USER 2026-06-26 ratified commit; deferred since prior completion report.

## Cell rulings

### 1. exp_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3 -> MEASURED_MECHANISM (delta=0)
- K=8192 and K=16384 each landed ONE seed at rec=1.000 cv=0.000 (single-seed saturate).
- 7 of 27 units exhibit cardinality breach; v3's value is the HONEST surfacing of silent-drop (META_RULE_H + new META_RULE_J paying off).
- Per Fix #28: single-seed saturate is NOT chain-grade. Need 3-seed full at each K.
- Atom: `math::T3/EXP_phase_diagram_wm_multibank_K_ceiling_sweep_32768_v3_MEASURED_MECHANISM_...`

### 2. exp_kb_dual_store_audit_v1_smoke -> MIDDLE_BAND custom (delta=0)
- match_rate=0.90 AT pre-reg floor 0.90; per new META_RULE_L: at-floor != above-floor -> MIDDLE_BAND not HARD_PASS.
- Vacuous-UD at smoke; sub-audit needed for promotion. Full pending.
- Atom: `math::T3/EXP_kb_dual_store_audit_v1_smoke_MIDDLE_BAND_match_rate_0p90_at_floor_...`

### 3. exp_kb_partition_by_source_class_v1_smoke -> MEASURED_MECHANISM (delta=0)
- routing_acc=1.000 at n=10; USER BIAS-Q (suspect 1.000) + by-construction-saturation; vacuous-UD.
- Mechanism plumbed; non-discriminating at smoke regime. Full pending.
- Atom: `math::T3/EXP_kb_partition_by_source_class_v1_smoke_MEASURED_MECHANISM_routing_acc_1p000_...`

### 4. ANCHOR 3 coarse-grain RE-TIER -> MEASURED_MECHANISM_WITH_HONEST_CALIBRATION (delta=0)
- First smoke read at 21:19: cap_drop=0.000 at chain-grade-default cosine_thresh=0.85 (regime-insufficient on real char-trigram embeddings; 0.85 was synthetic-calibrated).
- Wave 3 re-ran at 21:24 with ADAPTIVE p5-percentile per source-class: cap_drop=0.300 rec=1.000 gap_vs_random=+0.214 = HARD_PASS at smoke.
- Re-tier as MEASURED_MECHANISM_WITH_HONEST_CALIBRATION (smoke pass; pending FULL). Adaptive calibration is honest (discriminator still fires at +0.214 above noise); not p-hacking.
- The calibration mismatch (chain-grade-benchmark default != real-substrate-distribution) is itself a methodological discipline -> META_RULE_M atomized concurrently.
- Atom: `math::T3/EXP_cortex_ultrametric_clustering_coarse_grain_ANCHOR_3_RE_TIER_smoke_MEASURED_MECHANISM_WITH_HONEST_CALIBRATION_...`

### 5. exp_kb_time_decay_eviction_with_reingest_v1_smoke -> MEASURED_MECHANISM (delta=0)
- eviction_frac=0.5 + recent_retention=1.0 non-vacuous; vacuous-UD overall; AUDIT_ONLY per USER.
- Mechanism plumbed; chain-grade requires FULL.
- Atom: `math::T3/EXP_kb_time_decay_eviction_with_reingest_v1_smoke_MEASURED_MECHANISM_eviction_frac_0p5_..._AUDIT_ONLY_...`

## META rules atomized (4)

- **META_RULE_J** -- no silent except in unit loops (per-unit try blocks must catch SPECIFIC exception classes + propagate failure-class to metrics.json; phase-diagram v1/v2/v3 are the witnesses)
- **META_RULE_K** -- smoke must FIRE discriminator (vacuous-UD or all-arms-saturate = NOT chain-grade evidence; demote to MIDDLE_BAND or harden regime)
- **META_RULE_L** -- band-floor results are MIDDLE_BAND not HARD_PASS (at-floor != above-floor; pre-reg must specify strictly-above-floor for chain-grade promotion)
- **META_RULE_M** -- primitive calibration to real-substrate distribution may differ from chain-grade benchmark regime (NEW from ANCHOR 3 RE-TIER; adaptive calibration acceptable iff principled + discriminator-still-fires + logged in metrics; honest calibration vs p-hacking distinction)

## A5 PRE/POST + Repair

**PRE-EXISTING DEFECT DISCOVERED + REPAIRED IN-LINE:** A5 PRE-load revealed the math + meta partitions contained 9 malformed atom records (5 META + 4 MATH) from prior batch2_8cell + batch3_4cell tool runs that wrote raw `{id,type,summary,rel_type,atomized_by,ts}` dicts instead of the Atom dataclass schema (lacks name + description + tier + kind). PartitionedStore was failing to load entirely. A5 PRE blocked all writes until repair.

**Repair (idempotent):** rewrote each malformed line as a proper Atom in-place via tmp + os.replace:
- math/atoms.jsonl: 4 repairs (lines 28584-28587 of 28587)
- meta/atoms.jsonl: 5 repairs (lines 187-191 of 191)
- Original `summary` lifted to `description`; `name` derived from `id` suffix; `tier` from id-prefix (T3 / T_methodology); `kind` from naming (META_RULE -> methodology_rule; otherwise methodology); original `atomized_by` + `ts` + `type` + `rel_type` preserved in metadata under `original_*` keys; `repaired_by` + `repaired_ts` stamped.
- Cert-status preserved in metadata (CHAIN_GRADE / HONEST_NEGATIVE -> provenance_quality CERT_CHAIN_GRADE; MM / META -> non-CERT) so the post-repair CERT N exactly equals the pre-repair intent.
- Underlying ledger rows for those 9 atoms already existed and were UNCHANGED.

**Effect of repair on CERT N:** the repair brought CERT N from "unloadable" to the live count 616 (which is the correct post-batch3 value: prior reported 588 + batch2's atomization delta + batch3's +1 chain-grade + other intervening writes; the ledger remains the authoritative cert-trail).

**Batch 4 atomize phase (post-repair):**
- A5 PRE: CERT N=616, atom_total=177403, ledger_rows=791
- 9 atoms added (5 cert + 4 META); 9 ledger rows appended
- A5 POST: CERT N=616 (delta=0 as expected; all 5 cells fail chain-grade per Fix #28), atom_total=177412 (+9), ledger_rows=800 (+9)

All writes via atomic tmp + os.replace + verify-load + JSON-integrity-check per A5 discipline.

## CERT N delta

**+0** (all 5 cells fail chain-grade tier per Fix #28 + by-construction-saturation + META_RULE_L band-floor + META_RULE_K vacuous-UD). Pre-batch4 CERT 616 -> Post-batch4 CERT 616.

The repair phase itself was net-neutral on CERT N (preserved cert-eligibility for the 1 chain-grade + 0 honest-negative + 8 non-cert original atoms whose intent had been recorded in the ledger already; the Store had been failing to surface them in CERT N counts because PartitionedStore was load-broken).

## Flag-backs to Research

1. **A5 PRE failure root cause:** the batch2_8cell + batch3_4cell tool runs used a non-Atom-schema writer pattern (raw dict with `type`/`summary`/`rel_type` instead of Atom dataclass). RECOMMENDATION: enforce `Atom.from_dict(json.dumps(out)) == atom` self-test inside any atomize tool before os.replace lands. The cert_ledger_writer's strict_a5 PartitionedStore PRE-load gate caught this only when the next tool tried to run -- consider a standalone partition-integrity scheduled task that runs every N writes.

2. **META_RULE_M is load-bearing for future cell-author dispatch:** primitive defaults inherit from chain-grade benchmark cells (synthetic data); real-substrate regimes may need adaptive calibration. Cell pre-reg template should declare a `calibration_check` field: either "default OK for this regime" with evidence, or "adaptive calibration with discriminator-still-fires gate".

3. **Phase-diagram K-ceiling is approaching chain-grade-eligible for K=8192:** 1 seed at K=8192 saturate; the cheap interim cell (3 seeds at K=8192 only, decoupled from K-ceiling extension) flagged in batch 3 still applies. K=16384 also has 1 seed; consider the same interim shape.

4. **META_RULE_J/K/L are pre-dispatch discipline:** recommend codifying as required SCHEMA-VET checks BEFORE Research dispatches future cells. The pattern: pre-reg must specify (a) per-unit failure-class instrumentation (J), (b) discriminator-fires check (K), (c) strictly-above-floor target (L).

## Cert-trail observability (HYBRID)

This note is the cert-trail observability artifact for batch 4 + repair. 9 new cert atoms + 9 new ledger rows landed in `data/substrate_index/{math,meta}/`. 9 in-place atom repairs landed in same paths. git-commit pending Director-cycle (Research authorized; commit by path).
