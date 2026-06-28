# Skunkworks ruling: hierarchical planning capability CLOSED (third-failure-gate)

**Date:** 2026-06-28
**Auditor:** skunkworks (cert-owner)
**Scope:** ONE closure (narrow USER scope; 80-finding broader audit deferred)

## Verdict

**RULED:** HONEST_NEGATIVE | capability_closed_three_mechanism_failures (delta=0 to CERT N)
**CERT trajectory:** 628 -> 628 (honest-negative; no chain-grade increment)
**Closure atoms landed:** 2

## SCHEMA-VET (pre-reg vs smoke output)

Pre-reg at `d:/AI/hd-instrument/preregs/2026-06-28_substrate_hierarchical_options_v1.md` validates:
- THIRD-FAILURE GATE clause present at line 54 with explicit closure action
- arms_distinct via SHA-256 per-arm seq trace (line 47)
- cardinality_ok at line 71-73 (EXPECTED=120, observed=120)
- META_RULE_AG un-saturated band [0.30, 0.95] (line 44)
- META_RULE_AF arms-must-differ; META_RULE_AH atomic-write
- META_RULE_AL 3-channel encoding pi/beta/I BEFORE readout (line 107)
- No silent except blocks (line 111)
- Discriminator-must-survive-scale at full N=8192 + composite-depth=6 (line 112)

PASS -- pre-reg validates against smoke output cleanly.

## LANDED-VET (independent recompute off disk)

Read `d:/AI/hd-instrument/data/exp_substrate_hierarchical_options_v1_smoke/metrics.json` directly:
- verdict = HARD_FAIL: VERIFIED
- summary verbatim matches USER context: VERIFIED
- _third_failure_gate_triggered=True: VERIFIED
- chance_random_floor = 2.143347050754458e-05; independent recompute 6^-6 = 2.143347050754458e-05: VERIFIED (exact)
- arms_distinct=True with 6 distinct SHA-256 hashes: VERIFIED
- cardinality_ok=True (120/120): VERIFIED
- Per-arm: OPTS=0.000 POLICY=0.000 INIT=0.050 TERM=0.000 CF=0.100 RAND=0.000: VERIFIED via direct read
- run_mode=smoke, elapsed_s=7.8 (well under 2400s timeout): VERIFIED

PASS -- no claim depends on verdict-msg framing; all numbers independently recomputed.

## Atoms landed

1. **Capability-closed result:** `math::T3/EXP_substrate_hierarchical_options_v1_HONEST_NEGATIVE_CAPABILITY_CLOSED_three_mechanism_class_failures_...`
   - kind=experiment_record, tier=T3, pq=HONEST_NEGATIVE, cert_status=honest_negative
   - cert_class=capability_closed_three_mechanism_failures
   - metadata includes all 3 prior cell anchors + arm SHA-256 hashes + root_diagnosis + M3/M4 implications
2. **META_RULE_AO:** `meta::T_methodology/META_RULE_AO_capability_closure_after_3_mechanism_class_HF_...`
   - Genuinely new (not duplicate of AA-AN): operates at MULTI-CELL aggregate layer, not per-cell smoke-discipline layer; first such rule
   - Codifies: 3 distinct mechanism-class HFs on same capability + convergent encoding-root diagnosis => close box; no 4th iter without USER+research consensus

## A5 gate (PRE/POST verified)

- PRE CERT_N=628; POST CERT_N=628; delta=0 == expected (honest_negative)
- Fresh-Store round-trip survival: a1+a2 both Atom.from_dict clean
- Cert-ledger row appended (hash=11833ee27291ea79)

## Why this is genuinely a new META rule (not duplicate of AA-AN)

Reviewed AA-AN in `d:/AI/hd-instrument/data/substrate_index/meta/audit.jsonl`:
- AA fairness-before-tier: per-cell discipline (regime fires discriminator)
- AC HYPOTHESIZED-vs-MEASURED: per-claim discipline (drill numbers tagged)
- AF arms-must-differ: per-cell SHA hash discipline
- AG un-saturated band: per-cell band discipline
- AH cell-template SystemExit/BaseException order: per-cell discipline
- AL substrate-already-does-X: per-mechanism additive-lift discipline
- AM extends AL at process layer (single-cell new-mechanism gate)
- AN cone-collapse extrapolation: per-formula scale discipline

NONE of these operate at the multi-cell capability-aggregate layer. AO fills that gap: "3 distinct mechanism classes HF + convergent encoding-root diagnosis => capability closure." This is the FIRST multi-cell aggregate rule.

## No expansion

Did NOT scan the 80-finding broader audit (USER deferred). Did NOT VET other recent landings. Did NOT propose Phase-2/3 cert-trail migration changes.

## Pointers (absolute)

- Cell: `d:/AI/hd-instrument/experiments/exp_substrate_hierarchical_options_v1.py`
- Pre-reg: `d:/AI/hd-instrument/preregs/2026-06-28_substrate_hierarchical_options_v1.md`
- Metrics: `d:/AI/hd-instrument/data/exp_substrate_hierarchical_options_v1_smoke/metrics.json`
- Closure note: `d:/AI/hd-instrument/notes/exp_dev_capability_closed_hierarchical_planning_2026-06-28.md`
- Atomize tool: `d:/AI/hd-instrument/tools/atomize_hierarchical_planning_capability_closed_2026-06-28.py`
- Math partition: `d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl` (a1 appended)
- Meta partition: `d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl` (a2 appended)
- Meta audit log: `d:/AI/hd-instrument/data/substrate_index/meta/audit.jsonl` (a1+a2 audit entries)
- Cert ledger: `d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl` (row hash 11833ee27291ea79)
