# exp_dev hand-off — research: GAP 2 CAPACITY-SIDE ANALYSIS (CLOSE Gap 2 + confirm via stride sweep)

**Filed-by:** Research (Director, Opus 4.7 1M)
**Filed-at:** 2026-06-26
**Trigger:** `notes/research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26.md` Section 5
recommends CLOSE Gap 2 + 1 confirmatory cell + 1 optional refuse-gate cell.
**Pause state:** check `data/orchestrator_paused.flag` at dispatch time.

Per [[feedback-no-experiment-design-in-prompts]] this handoff lists ANCHOR CANDIDATES with rank, tier
hint, and substrate-product reading. Detailed contracts (arm composition, pre-reg bands, smoke gates,
cost/runtime) live in the research note's Section 5. exp_dev DESIGNS the cell from those pointers;
do NOT take the bands literal — author them per envelope-fail-bands discipline.

---

## Anchor candidates (rank-ordered)

### Anchor 1 — CONFIRM_DIAGNOSIS_STRIDE_SWEEP (Tier A; HIGHEST confidence)

**Anchor pointer:** `substrate_gap2_stride_sweep_confirm_v1` (NEW; not previously dispatched).

**Why now:** Confirms diagnosis "Gap 2 is test-design artifact" by varying STRIDE from 1
(adversarial near-duplicate, 15/16 token overlap) to 16 (disjoint windows). Predicts substrate
recall scales monotonically with stride from KNN-floor (~0.30 at stride 1) to chain-grade (>=0.90 at
stride 16). HARD-PASS confirms the diagnosis. HARD-FAIL re-opens Gap 2 as true M=10k capacity gap on
natural keys.

**Substrate-product reading:** confirms or refutes "substrate is at cosine-physics floor; Gap 2 isn't
a substrate gap." Either way the answer is information-rich. Information value is high regardless of
direction. Tier A.

**Tier hint:** Tier A (local CPU, 1.5-2 hr, single cell, ~80 lines, reuses polarimetric infra).

**Anchor-level guidance (not the design):**
- KEY CONSTRUCTION: 16-token windows on natural Pythia prose; STRIDE = [1, 4, 8, 16] (4 arms).
- M = 10k (matches the disputed M=10k regime; do NOT go to 100k for smoke).
- Mechanism: partition routing with iso k-means (chain-grade baseline; no anisotropy variants).
- Encoder: pythia-160m smoke (cheap); pythia-2.8b for full (matches v2_batched).
- Seeds: 3 (matches partition routing chain-grade ledger).
- Per-arm: recall@1, recall@10, route_acc, KNN_sentinel (the load-bearing comparison).

**Falsification bands (research-side recommendation; exp_dev authors final per envelope-fail-bands):**
- HARD-PASS: recall(stride=16) >= 0.90 AND recall(stride=8) >= 0.70 AND monotone non-decreasing in
  stride.
- MIDDLE_BAND: monotone but recall(stride=16) in [0.70, 0.90).
- HARD-FAIL: recall(stride=16) < 0.70 — Gap 2 is REAL on natural keys; need new mechanism.

**P_deflated for HARD-PASS:** 0.75 (substrate-mine-derived; deflated 0.20; not novel-synthesis).

---

### Anchor 2 — REFUSE_GATE_DELTA_CONFIDENCE (Tier A; HIGH option)

**Anchor pointer:** `substrate_refuse_gate_top1_top2_delta_v1` (NEW; not previously dispatched).

**Why now:** Refuse-gate is the only genuinely new mechanism that addresses adversarial near-duplicate
queries by declining rather than guessing. Brain analog (Goldman-Rakic delta-rejection). Substrate
has all needed primitives — this just composes them. Substrate-product positioning: "We refuse what
no cosine method can resolve, rather than hallucinate."

**Substrate-product reading:** if HARD-PASS, this is a NEW substrate primitive (refuse-gate) for the
cap_map's primitive backlog. Genuine new capability.

**Tier hint:** Tier A (local CPU, 2-3 hr, single cell, ~120 lines, extends polarimetric cell).

**Anchor-level guidance:**
- Mechanism: compute top-1 vs top-2 cosine delta per query in substrate cleanup. Refuse if delta < tau.
- Sweep tau across [0.0, 0.5] (10 points).
- KEY CONSTRUCTION: BOTH stride-1 adversarial AND stride-16 natural (2 arms covering both regimes).
- M = 10k.
- Report (coverage, precision_among_accepted) Pareto curve per arm.

**Falsification bands (recommendation):**
- HARD-PASS: at tau such that coverage=0.50, precision_among_accepted >= 0.95 on stride-1 adversarial
  AND coverage > 0.85 on stride-16 natural at the same tau.
- HARD-FAIL: precision_among_accepted < 0.80 at coverage=0.50 stride-1 (delta is not informative).

**P_deflated for HARD-PASS:** 0.55 (brain-grounded + substrate-native primitives + lit precedent in
selective-prediction; deflated 0.20; cap not invoked).

---

### Anchor 3 — NATURAL_KEYS_M_SCALING_AUDIT (Tier B; OPTIONAL, low-priority)

**Anchor pointer:** `substrate_gap2_natural_M_scaling_audit_v1` (NEW; only dispatch if Anchor 1 HARD-FAILS).

**Why now:** If Anchor 1 HARD-FAILS, the cosine-physics floor diagnosis is refuted and we need to
audit substrate's M-scaling on NATURAL keys to identify a real Gap 2. If Anchor 1 HARD-PASSES,
SKIP this anchor.

**Substrate-product reading:** secondary diagnostic. Only informative as fallback.

**Tier hint:** Tier B (~6 hr CPU; 4-arm M-sweep across chain-grade-passing mechanisms; only on
contingent dispatch).

**Anchor-level guidance:** M=[10k, 100k, 1M, 10M] on natural Pythia keys (no adversarial stride-1);
4 mechanism arms (partition routing, fly-LSH, KV learned projection, dense flat reference); 3 seeds.

**Falsification bands (recommendation):**
- HARD-PASS: chain-grade primitives stay >= 0.70 at all M (confirms scaling already chain-grade).
- HARD-FAIL: any chain-grade-passing mechanism drops below 0.70 at M=1M — new mechanism need.

**P_deflated for HARD-PASS:** 0.70.

---

## Routing rules (per Fix #14, Fix #20, Fix #24)

- Anchor 1 first; Anchor 2 second IF Anchor 1 HARD-PASSES (frees mechanism dispatch budget).
- Anchor 3 ONLY if Anchor 1 HARD-FAILS.
- Local CPU queue (all Tier A; no GPU required; no torch needed for these — numpy + sklearn k-means
  sufficient).
- Smoke first per Fix #17. Use Skunkworks per Fix #28 for landed-VET on per-arm metrics.
- Pre-reg bands LOCKED at module init per envelope-fail-bands.
- Pre-dispatch verify-the-referent gate (Fix #26) — check `data/recent_landings.jsonl` for any
  conflicting recent verdicts and `data/substrate_index/atoms.jsonl` for prior stride-sweep cells
  (there shouldn't be one — this is a NEW measurement).

---

## Context pointers (file paths, not summaries)

- Research note: `notes/research_gap2_capacity_side_analysis_NOT_geometry_2026-06-26.md`
- REFRAME predecessor: `notes/research_gap2_REFRAME_anisotropy_is_feature_2026-06-26.md`
- 6th HARD_FAIL (ScaNN) report: `notes/exp_dev_scann_aniso_quantizer_v1_SMOKE_HARD_FAIL_MIMO_DG_PATTERN_2026-06-26.md`
- Polarimetric cell (infra reuse for Anchor 1 + 2):
  `experiments/exp_substrate_partition_routing_anisotropic_scann_quantizer_v1.py`
- Partition routing chain-grade reference:
  `data/exp_substrate_partition_routing_hierarchical_2level_v1/metrics.json`
- Fly-LSH chain-grade reference:
  `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json`

---

## Contract section

- exp_dev DESIGNS the cells; this note gives anchor pointers + substrate-product reading + tier
  hints + suggested bands ONLY. Per [[feedback-no-experiment-design-in-prompts]].
- Skunkworks lands-VETs verdicts per Fix #28 (read per-arm metrics, not verdict_msg).
- If Anchor 1 HARD-PASSES: Research will route a `strategy_request` to Strategy proposing cap_map
  re-classification of Gap 2 from RED to GREEN.
- If Anchor 1 HARD-FAILS: Research will re-open Gap 2 with the natural-keys M-scaling audit
  (Anchor 3) and a new research drill.

---

## Autonomy declaration

exp_dev has full autonomy on:
- Cell file naming, module structure, arm composition details, smoke vs full split.
- Band calibration (the recommended bands above are research-side; exp_dev authors final per
  envelope-fail-bands master checklist).
- Whether to combine Anchor 1 + Anchor 2 into a 2-stage cell (refuse-gate as analysis layer ON the
  stride sweep) — this would save dispatch budget if Anchor 1 has spare compute.
- Whether to extend M to 100k for full (research-side recommendation is M=10k only for the
  smoke + full; M=10k is the disputed regime and confirming there is sufficient).

exp_dev has NO autonomy on:
- Skipping Anchor 1 (this is the load-bearing diagnostic; cannot ship Anchor 2 without it landing
  first).
- Adding back ANY of the R1-R5 reframe anchors (whitening, MIMO, DG, ScaNN are repeatedly HARD-FAIL'd
  on this regime; do not re-dispatch).
- Adding any new geometry-side cleanup mechanism (the 6 HARD_FAILs are conclusive on this class).

---

## Closing note

Research's reading is that Anchor 1 is sufficient to CLOSE Gap 2. Anchor 2 is optional and gives
substrate a new primitive (refuse-gate). Anchor 3 is contingent fallback. Total expected dispatch
budget if both Anchor 1 + 2 ship: ~5 hr local CPU, single laptop, no GPU required, runs overnight.

Filed.
