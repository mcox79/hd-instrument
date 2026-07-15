# Pre-reg: interference_avoidance_conjunctive_vs_additive_v1

**Date:** 2026-07-14
**Cell:** `experiments/exp_interference_avoidance_conjunctive_vs_additive_v1.py`
**Anchor:** `interference_avoidance_conjunctive_vs_additive_v1`
**Trigger:** Drill 2 (`notes/drill_realworld_conjunctive_determination_prevalence_and_targets_2026-07-14.md`)
part-(a) reason-2 (pattern-separation / interference-avoidance) + part-(c) hedge +
Prediction 3. De-risks the conjunction thrust: if genuine no-dominant-driver
conjunctions are a minority regime, "structured codes beat frequency" cannot rest
only on attribute-selection. The hedge: conjunctive/orthogonal STORAGE avoids
catastrophic interference in a multi-fact shared-feature-pool store EVEN for a
single-driver-dominated attribute (a STORAGE win, independent of attribute
interactivity). Brain grounding: hippocampal DG/CA3 pattern separation; 2025
hippocampus split (perceptual cells linear, memory/storage cells conjunctive).

## Question
Does conjunctive/orthogonal (pattern-separated) coding give retrieval-WITHOUT-
interference in a multi-fact store whose concepts SHARE an overlapping feature
pool -- beating additive/overlapping codes AND a frequency baseline -- EVEN when
the stored held-out attribute is DELIBERATELY single-driver-dominated? Glass-box
HD; NO LLM.

## World model (single-driver-dominated by construction)
- Shared feature pool: `P_POOL=48` bipolar HD vectors (dim `N=4096`).
- Attribute cardinality `V_ATTR=8`; each attribute value = random bipolar codeword.
- Each feature f has canonical attribute `mu_f` (random in 0..7).
- Fact i draws `k=8` features from the shared pool; `driver_i = feats[0]`.
  `a_i = mu_{driver_i}` w.p. `p_drv=0.60`, else uniform random.
  => single-factor dominance ~0.60 (cf. metabolic-rate 1.11/1.88 = 0.59); distractor
  features carry ~0 MI about a_i. This is the HARD case for the hedge.

## Arms (compute architecture)
Self-contained numpy HD (CPU). Storage = hetero-associative Hebbian outer-product,
readout `pred_i = Gram @ Cmat`, argmax over V codewords.
- **ORTH** (conjunctive/pattern-separated): `k_i = normalize(prod_{f in S_i} phi_f)` --
  elementwise conjunctive bind; distinct feature-sets => near-orthogonal codes.
- **ADD** (additive/overlapping): `k_i = normalize(sum_{f in S_i} phi_f)` -- linear
  superposition; shared pool => high pairwise correlation => crosstalk.
- **FREQ_ORACLE** (dominant-factor baseline, ORACLE upper bound): predict `mu_{driver_i}`.
  STRONGEST possible single-driver/frequency predictor; beating it is conservative/fair.
- **FREQ_MARGINAL** (population floor): global modal attribute over the stored set.

`## Compute architecture`: class **(b) sequential-CPU with justification** -- numpy
matmul (Gram, readout) is BLAS-batched already; the only Python loop is over the M/regime
sweep (independent phase points). Total wall < 5 min at N=4096 across 3 seeds x 16 units.
No GPU speedup needed at this scale (largest op M=1024 Gram ~ a few seconds). **Storage
strategy: sharded** (each fact stored as its own key/value pair in the hetero-associative
matrix; the cell IS the sharded-vs-overlapping-code comparison).

## Capacity curve (measured @ prototype before authoring; re-measured at FULL)
N=4096 P=48 k=8 V=8 p_drv=0.6, seeds 7/13/19:
- M=8:   orth=1.000 add=1.000 freq_oracle~0.67  (no interference yet; ADD==ORTH)
- M=64:  orth=1.000 add~0.59  freq_oracle~0.67  (ADD crosses BELOW freq -- crossover)
- M=256: orth=1.000 add~0.35  freq_oracle~0.65  (ADD deeply collapsed; ORTH holds)
- rho_add ~ 0.167 (shared-pool key correlation); rho_conj ~ 0 (pattern-separated)
- CONTROL disjoint M=256/768: orth~1.000 add~1.000 gap~0.000 (must-fail control clean)
All MEASURED@scratch prototype; re-measured at FULL by the cell.

## Bands (Prediction 3; aggregate seed-mean at reference load M_HI=256, shared regime)
**HARD_PASS** (interference-avoidance benefit measurable EVEN for single-driver attr):
- `orth_acc_hi >= 0.90` (ORTH holds -- retrieval-without-interference), AND
- `gap_orth_add_hi >= 0.30` (structured beats additive; interference avoided), AND
- `gap_orth_freq_hi >= 0.15` (structured beats FREQ oracle; recovers residual), AND
- `add_acc_hi < freq_oracle_hi` (ADD collapses BELOW the no-storage baseline), AND
- `gap_control_hi <= 0.10` (must-fail control: no spurious lift w/ disjoint features), AND
- `>= 2 of 3` seeds individually satisfy the four shared-regime conditions (stability).

**HARD_FAIL** (hedge fails; bet must rest on attribute-selection alone):
- `max_over_M gap_orth_add < 0.10` (ORTH never beats ADD -- no interference-avoidance), OR
- `max_over_M gap_orth_freq < 0.05` (structured storage never beats frequency), OR
- `gap_control_hi > 0.25` (benefit appears WITHOUT a shared pool => confound).

**MIDDLE_BAND**: benefit exists but a HP condition unmet (e.g. ADD does not fall below
FREQ; or control shows moderate 0.10-0.25 lift; or only 1 seed satisfies all4).

Strict-above-floor (META_RULE_L): HP `gap_orth_add >= 0.30` vs HF floor 0.10 (band width
0.20; HP is floor + 1.0x width above -- strictly above). Prototype gap ~0.65 >> 0.30.

## SCHEMA-VET checklist
- `cardinality_ok`: EXPECTED_N_UNITS = (len(shared_M)+len(control_M)) * n_seeds =
  (13+3)*3 = 48 (FULL); (3+1)*2 = 8 (SMOKE). Verdict HARD_FAILs on breach (META_RULE_H).
- `arms_differ_verified`: ORTH vs ADD prediction sha256 asserted distinct per unit
  (ceiling-tie exempt only when both acc==1.0) (META_RULE_AF).
- `final_metrics_atomicity`: **tmp_replace** (META_RULE_AH).
- `except SystemExit: raise` before `except Exception`; no bare/BaseException (grep-clean).
- `crlb_n/a`: argmax over V=8 codewords; ORTH clean recall 1.0 measured; gap ~0.65 >> HP 0.30.
  `discriminator_reachability: True`.
- `baseline_in_band`: ADD at M_HI ~0.35 (0.05 < x < 0.95); ORTH ~1.0 (ceiling BY DESIGN --
  ORTH is the mechanism arm expected to hold, not a baseline that must sit mid-band). FREQ
  oracle ~0.65 mid-band. Discriminator is the GAP + crossover + control, not a single-arm
  mid-band value. (AG applies to baselines; ADD baseline is in band.)
- `discriminator_survives_scale`: SMOKE uses N=N_FULL=4096 and includes M_HI=256 + crossover
  M=64 + control -- fires the discriminator at full scale (option A).
- `calibration_check`: default_ok_for_this_regime.
- `cell_chunked`: false. Justification: single-cell multi-seed with per-seed
  `write_partial`+`resumable_seeds` checkpointing; total wall <5min at N=4096 numpy; runner
  death resumes from last completed seed; chunking a <5min cell into 3 files triples dispatch
  overhead for no reliability gain. `defensive_error_checking`: start-marker + heartbeat +
  crash-diagnostic + per-seed checkpoint all present.
- `progress_logging`: **print_flush_true** + `line_buffering=True` on stdout. (timeout 1800s.)

### §15 gates
- **A effective-vs-nominal**: swept axis = M (N_facts) and regime; each primitive experiences
  the same M it is swept over (no partition routing). `sweep_alignment_verdict: ALIGNED`.
- **B discriminating band**: capacity curve spans ADD=1.0 (M<=16) -> crossover (M~64) ->
  collapse 0.35 (M>=256); >= 8 of 13 shared M-points land in a discriminating regime for ADD.
  `discriminating_fraction ~ 0.85 >= 0.30`.
- **C shape-compat**: no primitive->primitive composition (single hetero-assoc store per arm).
  `composition_edges: []` (n/a).
- **D positive-control-reproduce**: no cited external chain-grade primitive composed; the
  cell's own store+readout is the primitive and is reproduced in self-test. n/a beyond self-test.
- **E functional-requirements**: (1) store many facts sharing features -> hetero-assoc Hebbian
  matrix; (2) retrieve exact stored attribute per fact -> argmax readout; (3) resist interference
  -> pattern-separated (conjunctive) code; (4) fair non-storage baseline -> FREQ oracle+marginal.
- **F.1-F.4 real_code_path / substrate_signature / guard_baseline**: **n/a** -- self-contained
  numpy HD, NO KGStore / fit-module / substrate object is constructed (no version-drift surface).
  The "real store+readout path" for THIS cell is `build_facts`+`hetero_recall`, which the
  self-tests call directly at N in {512,1024} (orth-holds, add-collapses, disjoint-control,
  freq-in-band, arms-differ). No guard-vs-arena-floor mis-fire risk (no POP/RANDOM held-out arena).

## Self-tests (exercise the REAL store+readout path)
1. orth recall >= 0.90 at M=300 N=1024 (retrieval-without-interference holds).
2. gap_orth_add >= 0.30 at M=300 N=1024 shared pool (interference collapse present).
3. disjoint control gap <= 0.10 (must-fail: no lift without shared pool).
4. freq_oracle within 0.10 of `p_drv + (1-p_drv)/V` AND in beatable band (0.30,0.90).
5. arms-differ: ORTH vs ADD prediction sha256 distinct.
6. verdict HP fires on synthetic HP units.
7. verdict HF fires on synthetic control-confound units.
8. verdict HF fires on synthetic no-benefit (orth~add) units.

## Dispatch
- SMOKE (local, gate-clear): `--smoke`, seeds [7,13], N=4096, shared M [8,64,256] + control [256].
- FULL: `remote_cpu_queue`, seeds [7,13,19], N=4096, shared M (13 pts) + control (3 pts). numpy
  (no torch) -- correct for remote_cpu (routing gate WARNs only at N>=16384; N=4096 fine).
- Timeout: **1800s** (measured smoke wall x safety; genuinely <5min, 1800 is generous headroom).

## Prior-work check
substrate-KB concept-query 2026-07-14: top hit cosine=0.3057 = 'proactive interference'
(wordnet concept, NOT prior arc). Prior arc substrate work (cortex_hippo M8192 capacity 0.277;
correlation-hurts-capacity 0.270) all < cosine 0.30. This cell OPERATIONALIZES the
correlation-hurts-capacity finding as an interference-avoidance value-prop for a single-driver
attribute + a 3-way frequency comparison -- genuine NEW test, not a rediscovery.
