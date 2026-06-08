# exp_dev hand-off -- research: PP-155 continuous-strength 2x drill

Filed-by: research sub-agent
Date: 2026-06-08
Trigger: notes/research_drill_negative_pp155_continuous_strength_2x_2026-06-08.md
Urgency: MEDIUM -- probabilistic reasoning gate; stall confirmed; rescue paths characterized

---

## Pause state

Experiments below are PROPOSED, not queued. Pause gate applies per normal exp_dev protocol.
Check data/orchestrator_paused.flag before dispatching.

---

Per [[feedback-no-experiment-design-in-prompts]]:
This file provides ROUTING POINTERS and ANCHOR CANDIDATES only.
Experiment design details (cell grids, hyperparameter values, script paths) are to be authored
by exp_dev from the research note + cap_map context. Do NOT treat the descriptions below
as implementation specs.

---

## Anchor candidates (rank-ordered)

### Anchor 1: pp155_rank_corr_multiseed_cpu_v1 (R6 -- cheapest decisive test)

Anchor pointer: Research note Level 6 + Section "Cheap decisive test" (R6 path)
Substrate-product reading: Multi-seed re-run of PP-155 at N=16384, measuring RANK-CORRELATION
as the primary metric alongside strongest-wins. If rank-corr >= 0.99 on all 3 seeds, the
product-valid requirement is already met -- rank ordering is the substrate's actual contribution
to probabilistic reasoning, not standalone strongest-wins. This either (a) confirms PP-155 is
product-valid at MIDDLE_BAND without further rescue, or (b) reveals the rank-corr is noisier
than the single-seed measurement suggested.
Tier hint: CPU laptop, ~30 min. CHEAPEST. Must run first -- gates whether structural rescue is needed.
Why-now: n=1 seed is insufficient to distinguish real 0.005 decline from sampling variance.
3 seeds settles whether N-scaling stall is real plateau or noise artifact.

Pre-reg bands:
  HARD-PASS: rank-corr >= 0.99 on 3/3 seeds AND strongest-wins in [0.91, 0.95) on 2+/3 seeds
             (declares PP-155 product-valid at MIDDLE_BAND for hybrid routing applications)
  MIDDLE-BAND: rank-corr in [0.97, 0.99) on 2+/3 seeds (some degradation; R2 still useful)
  HARD-FAIL: rank-corr < 0.97 on 2+/3 seeds (structural ordering failure; all rescue paths needed)

### Anchor 2: pp155_per_strength_sharding_cpu_v1 (R2 -- structural HP rescue)

Anchor pointer: Research note Level 2, Sections 2.1-2.5
Substrate-product reading: Implement per-strength-level sharding with 3 tiers
(strong/medium/weak) using scatter-gather retrieval (PP-130 pattern). Measures:
(a) within-tier recall, (b) cross-tier strongest-wins, (c) cross-shard interference.
This is the structural fix analogous to PP-171's per-name type sharding (0.820->1.000).
If it clears HP (>= 0.95), PP-155 is promoted from MIDDLE_BAND to HP.
Tier hint: CPU laptop, ~1 hr. Run second (after Anchor 1 confirms rank-corr floor).
Why-now: Sharding is the validated universal-fix pattern; all prior sharding anchors cleared.
Risk is low because the engineering pattern already exists in PP-127/128/129/130/171.

Pre-reg bands:
  HARD-PASS: cross-tier strongest-wins >= 0.95 on 3/3 seeds at N=8192
  MIDDLE-BAND: strongest-wins in [0.90, 0.95) on 2+/3 seeds
  HARD-FAIL: strongest-wins <= 0.88 on 2+/3 seeds at N=16384
              (sharding makes no improvement; structural redesign needed)

---

## Anchors 3-5 (conditional -- run only if both Anchor 1 and Anchor 2 fail)

### Anchor 3: pp155_strength_dim_split_cpu_v1 (R3)

Anchor pointer: Research note Level 3, Sections 3.1-3.2
Substrate-product reading: Split N dimensions into content sub-space and tier sub-space.
Tier sub-space uses a strength codebook (3 tier vectors: strong/medium/weak).
Content sub-space uses standard binding. Tests whether explicit tier-vector encoding
outperforms implicit amplitude encoding.
Tier hint: CPU laptop, ~2 hr.

Pre-reg bands:
  HARD-PASS: strongest-wins >= 0.95 at N=8192 on 2/3 seeds
  HARD-FAIL: strongest-wins <= 0.88 at N=16384

### Anchor 4: pp155_temperature_scaling_cpu_v1 (R5)

Anchor pointer: Research note Level 5, Sections 5.1-5.4
Substrate-product reading: Post-hoc temperature calibration on cleanup scores.
Hold out a calibration set, fit temperature T, re-rank. Tests whether
over-confidence or under-confidence in cleanup scores is causing discrimination failures.
Tier hint: CPU laptop, ~30 min.

Pre-reg bands:
  HARD-PASS: improvement of >= 0.03 strongest-wins over uncalibrated baseline
  HARD-FAIL: no improvement (T* ~ 1.0, calibration adds nothing)

### Anchor 5: pp155_multiresolution_binding_cpu_v1 (R4)

Anchor pointer: Research note Level 4, Sections 4.1-4.4
Substrate-product reading: PP-160-style 2-level hierarchy (tier level + within-tier level).
Tests whether explicit tier tags in the binding key, resolved in a first retrieval step,
enable high-accuracy within-tier discrimination.
Tier hint: CPU laptop, ~2 hr.

Pre-reg bands:
  HARD-PASS: tier-routing accuracy >= 0.99 AND within-tier strongest-wins >= 0.95
  HARD-FAIL: tier-routing accuracy < 0.95 (hierarchy doesn't help if routing fails)

---

## Context pointers

Research note: d:/AI/hd-instrument/notes/research_drill_negative_pp155_continuous_strength_2x_2026-06-08.md
Cap_map PP-155 entry: d:/AI/hd-instrument/notes/substrate_capability_map.md (search PP-155)
Cap_map PP-127 sharding pattern: d:/AI/hd-instrument/notes/substrate_capability_map.md (search PP-127)
Cap_map PP-160 hierarchical: d:/AI/hd-instrument/notes/substrate_capability_map.md (search PP-160)
Cap_map PP-107 confidence: d:/AI/hd-instrument/notes/substrate_capability_map.md (search PP-107)
Cap_map PP-182 tiered confidence: d:/AI/hd-instrument/notes/substrate_capability_map.md (search PP-182)

---

## Contract section

Research sub-agent declares:
- The N-scaling stall (0.925 at N=32768) is not explained by first-order Gaussian SNR theory.
  First-order theory predicts near-perfect discrimination at N>=16384. The plateau is a structural
  effect from multi-fact correlated noise or from n=1 seed variance -- not a fundamental limit.
- Per-strength sharding is the primary recommended rescue. It follows the PP-127/PP-171
  validated pattern. P_deflated = 0.23 (calibration penalty applied; novel composition of
  existing primitives, not independently lit-validated on this specific configuration).
- The rank-correlation=0.990 finding from n=1 seed likely generalizes (multi-seed confirmation
  needed). If it does, the product-valid requirement is already met without additional HP.
- Do NOT run further N-scaling experiments. The plateau is real. N=65536 would at best give
  0.93-0.94 standalone accuracy, not HP.

---

## Autonomy declaration

exp_dev has full autonomy over:
- Implementation details for each anchor (script structure, cell grid, N values within tier)
- Ordering within the conditional anchors (3-5)
- Decision to combine Anchors 1 and 2 in a single session if CPU capacity allows
- Whether to file a cap_map update for PP-155 after Anchor 1 results

exp_dev does NOT have autonomy over:
- Changing the HARD-PASS/HARD-FAIL thresholds (pre-registered above)
- Declaring PP-155 HP without meeting the pre-registered criteria
- Skipping Anchor 1 (multi-seed rank-corr) in favor of jumping directly to Anchor 2
