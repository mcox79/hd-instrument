# RESEARCH (Director) -> Skunkworks (next session SCHEMA-VET): PRE-REG composition extensions = TIER-2 wave #1 per Skunkworks GREEN-LIGHT (commit handoff via skunkworks_to_all_GREENLIGHT_*). USER said "get all that going" → authored NOW; next Skunkworks session SCHEMA-VETs. 4-line template applied + gate-MECHANISM-not-cliff + can-fail-both-directions + dependent-set + op-series across N. Brief but complete.

(Filename has to_skunkworks per refined cap.)

## Context

- USER "get all that going" + Skunkworks GREEN-LIGHT (commit `skunkworks_to_all_GREENLIGHT_*`); next-Skunkworks-session SCHEMA-VETs the TIER-2 wave
- Order per RE-WEIGHTED enabling-ness ranking: **composition #1 → sparse-boundary → KG-fb15k237 → continual+drift → refuse-gate → capacity**
- Substrate-mining ground: `research_composition_extensions_SUBSTRATE_MINING_pre_stage_for_TIER2_pre_reg_authoring_2026-06-20.md` (Director-side working doc; 13 existing cert atoms catalogued + 3 gaps identified)

## PRE-REG: composition extensions at N>2048

### Title + cluster type
**Title:** Composition extensions: cleanup-mediated multi-hop + b2xb4xhier multiplicative scaling at N=4096 / N=8192.

**Cluster type:** **dependent-set** (b2 × b4 × hier inherits cert evidence from existing singletons cert-PASS) **+ operating-point-SERIES across N** (per Skunkworks's adopted op-series cluster type; individual N values are scale-points within one capability).

### Honest-scope
"Substrate's multiplicative-composition (b2 × b4 × hier) reproduces at N=4096 / N=8192 + cleanup-mediated multi-hop depth K_observed ≥ classical-floor scaled per N; comparator class = substrate-internal cert atoms at N=2048 (own-cert iso-protocol extension), NOT vs-LLM."

### Discriminating regime (the load-bearing axis)
**N × K joint sweep:** N ∈ {2048 [cert baseline; reproduces], 4096, 8192}; K ∈ {12 [SQ2 baseline], 24, 36, 48}; 5 seeds per (N, K).

At each (N, K) measure:
- `recall` (b2xb4xhier multiplicative-composition recall at the predicted pattern-count)
- `pattern_count_observed` (vs multiplicative-principle prediction = `M_dense × sparse_factor × K × D`)
- `cleanup_augmentation_ratio` (cleanup-mediated K_observed / plain-iter K_observed; baseline at N=2048 is 6×)
- `K_observed_at_recall_0.9` (the depth at which recall drops to 0.9; the depth-cliff)

### 4-line template applied

**(1) HARD_PASS gates load-bearing MECHANISM (NOT the cliff; the cliff is REPORTED).** Mechanism = multiplicative-composition reproducibility + cleanup-augmentation maintenance:
- At N=4096: recall ≥ 0.95 × N=2048-recall (the multiplicative cert reproduces under N-extension)
- At N=4096: pattern_count_observed ≥ 0.9 × multiplicative-principle-prediction (the principle holds; allows 10% headroom for finite-N noise)
- At N=4096 + K=24: cleanup_augmentation_ratio ≥ 2× (cleanup augmentation maintains at least one-third of the N=2048 6× baseline; mechanism survives N-extension)
- At N=8192: ALL three conditions hold (the principle scales to 4× the baseline N)

ALL conditions must hold for HARD_PASS. MIDDLE_BAND if N=4096 passes but N=8192 fails on the cleanup-augmentation (the extension partially scales; cliff is at N between 4096-8192).

**(2) CLIFF = REPORTED measurement, not gated above HARD_PASS.** Report K at which `cleanup_augmentation_ratio` drops below 2× at each N (this IS the empirical depth-cliff at scale). Report pattern_count_observed vs prediction divergence as N grows. Report `K_observed_at_recall_0.9` per (N, K) — this populates Phase 0d q_b composition op section.

**(3) Per-condition CAN-fail (BOTH directions, data-dry-run check):**
- DOWN-direction can-fail: recall < 0.95 × baseline at N=4096 (multiplicative principle breaks); pattern_count_observed < 0.9 × prediction (sparsity benefit shrinks at N); cleanup_augmentation drops below 2× at K=24 N=4096 (cleanup augmentation fails to scale)
- UP-direction can-fail: recall reproduces TOO well (>1.05× baseline — would suggest measurement bug or unintended easier task at higher N); pattern_count_observed > 1.1 × prediction (suggests overcounting — verify-the-referent on the metric)
- Data-dry-run: existing N=2048 cert atoms confirm 600K patterns + recall=1.00 + 6× cleanup augmentation → at N=4096 a 0.95× recall = 0.95 (clearly achievable per the algebra); at N=8192 a 0.95× recall = 0.95 with predicted pattern_count = 1.2M (multiplicative scaling)
- The UP-direction cliff (measurement-bug) is the verify-the-referent guard per recent disciplines

**(4) Achievability check on plausible data.** N=2048 cert atoms (the substrate-mining catalogue): b2xb4xhier_v1_n2048 HP at 600K patterns recall=1.00; cleanup-augmented depth 6× boost at N=2048; SQ2 K=12 HP at N=2048; SQ2 × hierarchical 24-hop HP at N=2048. The N>2048 extension is plausible per the multiplicative-principle algebra (M scales linearly with N at fixed alpha; cleanup augmentation depends on local-SNR which scales with N). Prior n4096/n8192 GPU runs had NO LOGS (infra failure 2026-06-05; not the science) — so the actual extension HASN'T failed, just was never measured. Achievability HIGH per existing N=2048 evidence + linear-scaling algebra.

### Pre-reqs (BLOCKING for dispatch)
- **GPU infra fix:** the n4096/n8192 no-log GPU failure from 2026-06-05 must be RCA'd. Symptoms: passed --self-test + smoke; GPU produced no logs/metrics. Likely a runner-config or memory-pressure issue at higher N. Coordinate with Orchestrator + Exp-Dev before dispatch.
- **Cell-build:** Exp-Dev builds the N × K joint sweep cell after GPU infra fix; estimated 40 runs (2 N × 4 K × 5 seeds); medium GPU
- **Version-marker:** add `metrics_source` version-marker per the NER stale-v1 lesson; pin substrate version + cleanup-config version

### What this pre-reg DOES NOT do (out-of-scope; future-drill)
- K_max formula NESS correction (the scorecard 2026-06-05 01:20 observation that K_max is pessimistic) — theoretical follow-up; this empirical pre-reg FEEDS the correction work
- N>8192 scaling (out-of-scope; this pre-reg covers 2× and 4× the cert baseline; further extension is a future op-series scale-point if HARD_PASS lands)
- Composition with NON-cleanup substrate operations (e.g. resonator-augmented at scale; logged for follow-up)

### Composes downstream
- Phase 0d framework q_b composition op section populated (validated regions extended to N=8192; cliff REPORTED)
- KG fb15k237 pre-reg (#3 in wave) builds on this — KG traversal IS composition at scale; KG cert at N=8192 needs composition cert at N=8192
- Glass-box-LLM Phase 3 multi-hop scale-up uses this as the load-bearing capacity envelope per USER-LOCKED substrate-quality-first

## Standing
- **Skunkworks (next session):** SCHEMA-VET this pre-reg per the encoded disciplines (gate-mechanism / cliff-REPORTED / can-fail-both / achievability). RESUME-ANCHOR captures the disciplines; this pre-reg applies them explicitly
- **Orchestrator + Exp-Dev:** RCA the n4096/n8192 GPU infra failure (2026-06-05 no-log issue); blocks cell-build dispatch but NOT pre-reg SCHEMA-VET. Pre-reg can SCHEMA-VET in parallel with infra fix
- **Me (Director):** authoring next TIER-2 wave pre-reg (sparse-boundary #2) in parallel; continuing Phase 0c probe results reactivity + Phase 0d framework population as data arrives

Next Director artifacts in flight: sparse-boundary pre-reg (TIER-2 #2) + KG fb15k237 pre-reg (TIER-2 #3).

-- Research (Director)
