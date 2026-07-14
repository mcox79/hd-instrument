# Structure Discovery via Shared-Code Compositional Readout (Pre-Registration)

Date: 2026-07-14
Author: hdi_exp_dev (Director spawn: confirm/refute the inline shared-code structure-discovery finding, rigorously, at
scale, across multiple structure families).
Cell: `experiments/exp_structure_discovery_shared_code_readout_v1.py`
Anchor: `structure_discovery_shared_code_readout_v1`
Queue: `remote_cpu_queue` (CPU-only; small full-batch SGD; ~2 min wall at FULL).

Concept-query (mandatory pre-authoring): `bash tools/substrate_query.sh "discover compositional structure from data
shared code embedding homomorphism generalize novel combinations"`. Top hits (cosine): 0.4033
`preregs/2026-07-03_stage2_benchmark_reframe_vsa_native_task_suite.md` (VSA-native task SUITE; HAND-DESIGNS
bind/unbind over a fixed codebook -- does NOT test learning-the-algebra-from-data), 0.3535
`notes/wave14e_hierarchical_composition_research.md`, 0.3398 DECISION_130a semantic-rediscovery cautionary note.
Prior-work check: NONE at cosine>0.30 tests the specific mechanism here (a SHARED LEARNABLE code table whose algebra is
DISCOVERED by SGD/CE, not hand-built). This cell is genuinely novel; it is the direct sequel to the conjunction
CONSTRUCTION_PROOF (`exp_conjunction_native_bind_vs_homophily_cskg_v1`, which hand-designed the FPE algebra and never
tested whether it could be discovered from data). Skunkworks flagged exactly this open problem.

## 1. Question
Does the SHARED-CODE + compositional-similarity-readout architecture LEARN compositional structure from data (plain
cross-entropy, NO hand-designed algebra, NO homomorphism regularizer) and GENERALIZE to genuinely-novel (A,B)
combinations -- across MULTIPLE structure families, not just modular addition -- and FAIL (to chance) when the
composition is arbitrary?

Architecture (the DISCOVERY arm): one complex64 unit-phasor code E[v] = polar(1, theta[v]) per value v (SHARED across
A, B, and the ANSWER); readout `logits[r] = Re<bind(E[a],E[b]), E[r]>` using the REAL substrate FHRR bind
(`hdlab.binding.bind`, complex elementwise mul); train theta with plain CE over the answer vocabulary. Glass-box.

## 2. Structure families (the discriminating axis; PAIRED on the same held-out novel (A,B) pairs)
- F1 CYCLIC   R=(A+B) mod L            abelian Z_L                 -- DISCOVERABLE predicted
- F2 XOR      R=A xor B (L=2^k)        abelian (Z_2)^k, DISTINCT   -- DISCOVERABLE predicted (not-a-fluke-of-add)
- F3 ASYM     R=(c1*A+c2*B) mod L      c1!=c2, non-symmetric       -- CLAIM-BOUNDING (symmetric bind cannot represent)
- F4 ARBITRARY R=T[A,B] fixed random table                        -- MUST-FAIL control (novel unlearnable -> chance)
- F1_NOISY    F1 with eps=0.15 of TRAIN labels flipped            -- label-noise robustness of discovery

## 3. Arms (novel-pair top-1 acc; chance=1/L)
- DISCOVERY: shared learnable phasor codes + real-bind compositional readout (headline).
- MEMORIZE: SEPARATE learnable real tables Ea, Eb + concat -> MLP -> logits (no shared code, no bind). OVER-parameterized
  vs DISCOVERY (params_MEMORIZE >= params_DISCOVERY) so it cannot be dismissed as underpowered; it fits SEEN pairs
  (seen-acc ~1.0) but has no compositional prior -> should NOT generalize to novel combos.
- FPE: HAND-DESIGNED matched codes (F1 additive-FPE, F2 XOR-character code -- both EXACT homomorphisms under the bind).
  NOT trained. Construction-proof ceiling; DISCOVERY-minus-FPE = the optimization/coverage gap.
- FREQ_NULL: strongest non-learning null, score(r)=count(a'==a,r)+count(b'==b,r). Must fail on compositional novel.
- ORACLE: learner info-ceiling (deterministic rule -> 1.0 achievable; ARBITRARY held-out -> chance).

## 4. Fairness / weak-point-localization (first-class)
- Arbitrary MUST-FAIL control (F4): discovery must NOT generalize on a random table (proves genuine discovery, not leak).
- Novel-vs-seen: novel (A,B) combos never in train (disjoint index split; leak-count asserted == 0). Every value 0..L-1
  appears in TRAIN as A, as B, and as an answer (codes trainable); audited + reported.
- Info-ceiling: ORACLE per family; FPE hand-design proves the achievable ceiling (=1.0 on F1/F2).
- Metric-can-MOVE: arms differ (META_RULE_AF hash of novel predictions; >=3 distinct signatures required).
- Weak-point localizer: F3_ASYM directly BOUNDS the claim -- if discovery (and FPE) fail on the asymmetric linear form
  while succeeding on the symmetric abelian families, the bound is "discovers COMMUTATIVE (abelian) structure matched to
  the bind's own algebra," which is the honest, precise finding.

## 5. PRE-REGISTERED BANDS (NOVEL stratum, top-1 acc; chance=1/L; NOT tuned)
HARD_PASS (architecture GENUINELY discovers compositional structure across families) -- require ALL:
- HP1 DISCOVERY novel-acc >= 0.30 on F1 AND F2  (0.30 = 19x chance at L=64; FPE ceiling=1.0 proves reachable)
- HP2 DISCOVERY - MEMORIZE novel-acc >= 0.25 on F1 AND F2  (architecture advantage)
- HP3 F4 ARBITRARY DISCOVERY novel-acc <= chance + 0.05  (must-fail: no generalization without structure)
- HP4 FREQ_NULL novel-acc <= 0.20 on F1 AND F2  (null genuinely fails on compositional novel)
HARD_FAIL / REFUTE (report STRAIGHT) -- ANY:
- RF1 DISCOVERY - MEMORIZE novel-acc <= 0.10 on F1  (no architecture advantage -> refuted)
- RF2 (INTEGRITY, dominates) F4 ARBITRARY DISCOVERY novel-acc >= chance + 0.15  (generalizes on a RANDOM table ->
  leak/cheat -> whole benchmark INVALID)
MIDDLE_BAND: else -- e.g. additive-only (F1 ok, F2 not) => claim bounded to modular-add; XOR-only; etc. F3_ASYM is a
DIAGNOSTIC, not a gate.

What refutes "the architecture discovers compositional structure": RF1 (discovery no better than the memorize
baseline) OR RF2 (arbitrary control also generalizes). Either fires -> the inline prototype finding is refuted.

## 6. Calibration evidence (MEASURED, from local self-test + calibration, NOT the FULL run)
- Self-test PASS (10.3s, real bind path): F1 DISC=0.696 MEMO=0.000 adv=0.696; F2_XOR DISC=0.804 MEMO=0.020;
  F4_ARB DISC=0.069 lift=0.006 (must-fail fires); FPE_F1=1.000; homomorphism_ok=True; validity_preflight_ok=True.
  MEASURED@data/exp_structure_discovery_shared_code_readout_v1/metrics.json:mechanism_selftest (self_test run_mode).
- FULL-scale 1-seed calibration (L=64 d=128 steps=800, 36.5s): F1 DISC=0.412 F2 DISC=0.412 (adv 0.41 vs MEMO ~0.00,
  FPE=1.0), F4_ARB DISC=0.017 (= chance 0.0156, lift 0.002), F3_ASYM DISC=0.030 (FPE also 0.016 -> bound is the bind's
  commutativity), F1_NOISY DISC=0.336. HYPOTHESIZED FULL 3-seed verdict = HARD_PASS
  (ARCHITECTURE_DISCOVERS_COMPOSITIONAL_STRUCTURE_ACROSS_ABELIAN_FAMILIES) with the honest bound that absolute acc at
  L=64 is ~0.41 (limited-coverage generalization gap, not an architecture wall) and F3_ASYM is the discovered limit.

## 7. Config / compute
- FULL: L=64, n_dim=128, coverage=0.30 (2867 novel pairs), steps=800, disc_lr=0.05, memo_h=96, seeds=[7,13,17],
  eps=0.15, (c1,c2)=(1,2). Est wall ~2 min (3x ~36s/seed) + one-time ~8s complex MKL warmup.
- Compute architecture: class (c) mixed / sequential-CPU JUSTIFIED -- small full-batch SGD, readout is one BATCHED
  (B,d) bind + one (B,d)@(d,L) matmul per step (batched tensors, not a python loop); matmuls tiny -> GPU launch overhead
  would dominate; CPU correct. Storage: no_storage (per-value SHARDED codes).
- final_metrics_atomicity: tmp_replace. progress_logging: print_flush_true (per-family flush prints + per-seed
  heartbeat). cell_chunked: false (per-seed try/except loop + partials + cardinality gate). cardinality_ok:
  EXPECTED_N_UNITS = n_seeds = 3.
- crlb_n/a: discrete argmax over L classes; chance=1/L is the only floor; HP1 (0.30) >> chance (0.0156) and << oracle
  (1.0, FPE-attained) so reachable.
- calibration_check: default_ok_for_this_regime (bands are absolute accuracy vs chance, not primitive-inherited).

## 8. Validity preflight (F.1-F.4, declared + ENFORCE)
real_code_path (self-test TRAINS the DISCOVERY arm through hdlab.binding.bind -- the EXACT FULL path; no external data,
so fully exercised locally); substrate_signature (hd_bind bound against live signature); positive_control;
metric_moves; negative_control_margin; full_gates_exercised. guard_baseline: n/a (MEMORIZE is a fair over-parameterized
contrast, not a control-beats-baseline break-guard).

## 9. Timeout
900 s (measured ~2 min at FULL; 900 s = generous headroom for slower remote CPU; < 1800 s so no 30-min heartbeat
mandate, but per-family/per-seed flush prints emitted regardless).
