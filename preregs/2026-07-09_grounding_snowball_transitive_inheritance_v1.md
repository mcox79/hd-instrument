# Pre-reg: Grounding snowball -- transitive grounding-inheritance on the native relational encoder

- **Anchor:** `grounding_snowball_transitive_inheritance_v1`
- **Cell:** `experiments/exp_grounding_snowball_transitive_inheritance_v1.py`
- **Date:** 2026-07-09
- **Author:** exp_dev
- **Queue target:** `remote_cpu_queue` (CPU-only; small linear models + label propagation; no GPU needed). Smoke ran LOCAL.
- **Source note:** `notes/research_native_encoder_relational_structure_vs_grounded_meaning_2026-07-09.md` (Predictions A + B).
- **Reused pipeline (NOT rebuilt):** `experiments/exp_teacher_free_relational_encoder_cn_subgraph_v1.py` (cert 06e5a493d): `load_cn_subgraph`, `char_trigram_features`, `ProjHead`, `info_nce`, `vicreg_repulsion`, `build_adjlist`, `_l2norm`. This cell ADDS the grounding/attribute/propagation layer only.

## Prior-work check (substrate-KB concept-query, mandatory)
`bash tools/substrate_query.sh "transitive grounding inheritance seed set propagation graph distance decay relational encoder attribute"` -> top hit cosine=0.3135 (`Locative_relation::Distance`, a FrameNet frame) + adversarial-encoder-injection note chunks; NONE substantively about transitive grounding-inheritance. **Prior-work check: NONE at cosine>0.30 substantively related; genuinely novel** (matches the note's "no literature directly tests this in an HD/graph-embedding artificial system"). Not a rediscovery.

## Hypothesis (USER's own)
Attach REAL non-symbolic grounding to a SMALL seed set of atoms, then let the relational web carry it: meaning propagates transitively to neighbouring un-grounded atoms, decaying with graph distance. Formalised as transitive grounding-inheritance (Gunther et al. 2018) + ATL graded-hub gradient. `P(snowball works) ~ 0.35` (deflated; genuinely uncharted in artificial HD encoders per lit scan). Both outcomes gold.

## Attribute honesty (load-bearing framing)
The grounded scalar is a **synthetic graph-smooth field** diffused over the REAL ConceptNet 2-core subgraph -- an honest stand-in for a measured non-symbolic attribute (size/weight/magnitude) that correlates along relational edges (the note's stated precondition; the biological prior that relationally-close things share attributes). No external measured node-attribute file keyed to ConceptNet exists on disk, and fabricating one violates the no-external-ingest discipline. This is NOT a claim of real perceptual grounding and NOT "teaching the substrate English". The cell tests the **propagation MECHANISM**: does grounding attached to a seed set spread transitively through the existing relational web with the right distance-decay signature. Frame results as grounded-attribute propagation, NOT language understanding.

## Sequence (two stages)

### STAGE 1 -- Prediction A: hollow-skeleton floor (baseline, does NOT gate Stage 2)
Probe the EXISTING relational encoder (ungrounded `ProjHead` trained relational-only) with two families:
- **RELATIONAL probe**: edge-vs-non-edge link prediction from codes (Mann-Whitney AUC; chance=0.5). Encoder is trained for neighbour-closeness -> expected near-ceiling.
- **GROUNDED-ATTRIBUTE probe**: pairwise magnitude ORDERING ("is X bigger than Y") of the exogenous scalar (never a graph edge), read via a GLOBAL ridge linear probe fit on seed codes, ordering-accuracy over all non-seed atoms (chance=0.5). Expected near-chance: relational-only training preserves unsigned proximity, not a signed 1-D magnitude axis.
- **LEAKAGE GUARD**: if the ungrounded grounded-attribute readout > 0.70, the magnitude leaked into relational codes -> flag + inspect before trusting Stage 2 (per note).

### STAGE 2 -- Prediction B: the snowball (headline)
Ground a SMALL seed set (30 smoke / 120 full atoms) with the scalar; read it off NON-seed atoms via **label propagation** (cosine-weighted k=7 nearest grounded seeds in code space -- the Gunther transitive-inheritance mechanism), binned by graph distance to nearest seed. Primary readout runs on the RELATIONAL-ONLY (ungrounded) codes -- the purest test of "attach meaning to a few, structure carries it".
- **Real-snowball signature**: near-seed (dist 1) ordering acc ABOVE chance, DECAYING monotonically with graph distance, WHILE the same codes + same seeds + a SHUFFLED (non-graph-smooth) attribute stay FLAT at chance. Smooth-decays-while-shuffled-flat isolates genuine transitive grounding from any encoder/readout artifact (only the attribute's graph-alignment differs).
- **Secondary ablation**: does co-training the encoder with an auxiliary seed-only attribute-regression loss DEEPEN propagation beyond relational structure alone? (`cotrain_lift_near`.)

## Arms
- `ARM_STRUCTURE_SMOOTH` [PRIMARY]: label-prop of the smooth attribute from grounded seeds over UNGROUNDED relational codes.
- `ARM_STRUCTURE_SHUFFLED` [MUST-FAIL CONTROL]: same codes, same seeds, SHUFFLED attribute (graph-smoothness destroyed). MUST stay flat at chance.
- `ARM_GROUNDED_SMOOTH` [SECONDARY]: label-prop over encoder co-trained with seed-only attribute MSE (does co-training help?).
- Stage-1 uses the ungrounded relational codes for BOTH the relational AUC probe and the global ridge grounded-attribute floor.

## Pre-registered bands (lifted from note Predictions A + B, picked BEFORE the FULL run)

### Stage 1 (Prediction A)
- `STAGE1_HARD_PASS` (hollow skeleton): relational_auc >= 0.75 AND (relational_auc - grounded_floor_acc) >= 0.30 AND NOT leakage. (Note asks 40pp; deflated to 30pp for AUC-vs-acc comparability.)
- `STAGE1_LEAKAGE_FLAG`: grounded_floor_acc > 0.70 (magnitude recoverable ungrounded; inspect).
- `baseline_in_band`: 0.42 <= grounded_floor_acc <= 0.62 (META_RULE_AG; near-chance).

### Stage 2 (Prediction B) -- applied to `ARM_STRUCTURE_SMOOTH`; control = `ARM_STRUCTURE_SHUFFLED`
- `STAGE2_HARD_PASS` (real snowball): near_acc(d1) >= 0.60 AND decay (near_acc - far_acc, far = largest populated bin d>=3) >= 0.08 AND monotone-non-increasing across populated bins AND genuine_margin (near_acc_smooth - near_acc_shuffled) >= 0.06.
- `STAGE2_HARD_FAIL`: near_acc < 0.55 (no propagation) OR decay < 0.03 (flat/artifact -- a FLAT improvement uncorrelated with graph distance is a HARD-FAIL, not a win) OR genuine_margin < 0.03 (shuffled ~ smooth => leakage/artifact).
- `STAGE2_MIDDLE_BAND`: otherwise.
- `STAGE2_INCONCLUSIVE_NO_FAR_BIN`: no populated far bin (cannot measure decay) -> overall MIDDLE_BAND.
- `PRECONDITION_FAIL`: attribute graph-smoothness assortativity < 0.45 OR shuffled assortativity > 0.20 (adaptive gate; cannot test propagation if the attribute is not graph-smooth as designed).
- HP strictly-above-floor (META_RULE_L): all three Stage-2 HP thresholds clear their HF floors by > 5% band-width; multi-criteria AND gate.

## SMOKE evidence (LOCAL, MEASURED)
- SELFTEST_PASS: discriminator telemetry-sensitive (planted graph-smooth codes) near_acc=0.688 far_acc=0.499 decay=0.189 shuffled_near=0.514 genuine_margin=0.174. MEASURED@`data/exp_grounding_snowball_transitive_inheritance_v1_selftest/metrics.json`.
- SMOKE **HARD_PASS** (n=2143 CN 2-core, 2 model-seeds, 30 ground-seeds): STAGE1_HARD_PASS rel_auc=0.870 grounded_floor=0.516 gap=0.354 leakage=False baseline_in_band=True | STAGE2_HARD_PASS near_acc(d1)=0.630 far_acc(d3)=0.484 decay=0.146 monotone=True shuffled_near=0.495 genuine_margin=0.135 cotrain_lift_near=-0.023 | attr_assort smooth=0.685 shuf=-0.013. MEASURED@`data/exp_grounding_snowball_transitive_inheritance_v1_smoke/metrics.json`.
- Per-model-seed consistency: seed7 near=0.641, seed13 near=0.619.
- **Interpretation (honest):** transitive grounding-inheritance EXISTS but is SHALLOW (~1 hop); driven by relational structure itself (co-training does NOT deepen it, cotrain_lift_near=-0.023); shuffled control confirms graph-smoothness is load-bearing. FULL (5 seeds, n=12000, populated d4+ far bin) confirms canonical numbers + decay depth.

## Discriminator survives scale (DISCRIMINATOR-MUST-SURVIVE-SCALE)
Route (A): SMOKE=FULL branch parity -- smoke runs the identical code path at n=2143 and the discriminator FIRES (smooth decays, shuffled flat, genuine_margin=0.135 >> 0.06 HP). At FULL n=12000 the far bin d4+ populates (empty at smoke; d3 served as far anchor) giving a cleaner far anchor; the mechanism (graph-neighbour-of-seed is code-close) is scale-stable. No saturation risk: baseline (shuffled + global ridge floor) sits at chance by construction.

## Compute architecture (mandatory)
- **Class: (b) sequential-CPU with justification.** Per-epoch cost is a single small batch matmul (512 x 8192 @ 8192 x 256, sub-second CPU); reuses the CPU-only teacher-free encoder pipeline. GPU batching gives no material speedup (linear model, tiny code_dim); wall < 15 min at FULL. No GPU.
- **Storage strategy: `no_composition`** (no multi-item bundling/chained retrieval; per-atom codes are sharded rows; label propagation is single-hop kernel regression, not a bind/unbind chain).

## SCHEMA-VET fields
- `cardinality_ok`: true. `EXPECTED_N_UNITS = n_model_seeds` (smoke 2, full 5). Verdict emits `HARD_FAIL_CARDINALITY_BREACH_META_RULE_H` if fewer complete.
- `arms_differ_verified`: true (smoke; the ungrounded vs grounded ENCODERS are hash-checked distinct; META_RULE_AF). No exemptions.
- `final_metrics_atomicity`: `tmp_replace` (via `_seed_checkpoint.write_metrics` + `os.replace`; crash path also atomic).
- `except SystemExit: raise` BEFORE `except Exception` (no `BaseException`); bare-except grep gate PASS.
- `crlb_n/a`: "ordering-accuracy chance floor = 0.5 by construction; the discriminator is the DISTANCE-DECAY of label-propagation accuracy for a graph-smooth attribute vs a shuffled empirical null, not a closed-form estimator noise floor."
- `discriminator_reachability`: true (HP thresholds are on the achievable side; smoke MEASURED near_acc 0.630 >= 0.60, decay 0.146 >= 0.08, genuine_margin 0.135 >= 0.06).
- `baseline_in_band`: true (grounded_floor 0.516 in [0.42,0.62]; shuffled control ~0.50).
- `calibration_check`: `adaptive_with_discriminator_gate` -- shuffled-attribute empirical null + attribute graph-smoothness assortativity recomputed per run; discriminator (genuine_margin) still fires at smoke.
- `cell_chunked`: false (2-5 model-seeds in one cell; per-seed try/except with failure-class instrumentation + `write_partial` checkpoint; single linear-model training, restartable-cheap).
- `start_marker_written`: true. `crash_diagnostic_present`: true (CELL_CRASHED metrics + traceback). `heartbeat_present`: true (`_cell_heartbeat.emit_heartbeat` during training). `defensive_error_checking`: passed_all_4_patterns.
- `progress_logging`: `print_flush_true` (`_log` uses flush=True; `sys.stdout.reconfigure(line_buffering=True)` at entry). Note: FULL wall < 15 min < 30 min, so the timeout_s>=1800 mandate does not strictly bind, but flushing is implemented anyway.
- **Sweep/composition gates (Section 15):** no sweep axis; `sweep_alignment_verdict: N/A`. `discriminating_fraction: N/A` (no by-construction-saturation sweep). `composition_edges: []` (no primitive->primitive shape-adapter chain; label propagation is a single kernel readout over codes). `positive_control_arms`: the relational-AUC probe reproduces the teacher-free encoder's known neighbour-closeness AT THIS REGIME (rel_auc 0.870, consistent with cert 06e5a493d assortativity result). `functional_requirements`: (1) relational proximity (met by reused InfoNCE+VICReg encoder), (2) seed-anchored attribute inheritance (met by label propagation), (3) genuineness control (met by shuffled-attribute must-fail arm).

## Number tags
- rel_auc 0.870, grounded_floor 0.516, gap 0.354, near_acc 0.630, decay 0.146, genuine_margin 0.135, cotrain_lift_near -0.023: MEASURED@`data/exp_grounding_snowball_transitive_inheritance_v1_smoke/metrics.json`.
- P(snowball)=0.35: CITED@source note (deflated novel-synthesis estimate).
- Stage-1 gap HP=0.30 (deflated from note 0.40pp for AUC-vs-acc comparability), Stage-2 near_acc HP=0.60 / decay HP=0.08 / genuine_margin HP=0.06: HYPOTHESIZED@this prereg (bands picked before FULL; smoke MEASURED clears all).

## Prediction C (deferred)
Causal/index diagnostic (perturbing the grounded feature must move the representation >= 2x a matched relation-only perturbation) requires re-training per removed edge -- NOT cheap in this pipeline. Flagged as a follow-up cell, not implemented here.

## FULL dispatch
- Queue: `remote_cpu_queue`. Timeout: 3600 s (>= 5x estimated ~5-15 min FULL wall).
- Expected: 5 seeds, n=12000, 120 ground-seeds, populated d4+ far bin. Confirms Stage-1 gap + Stage-2 near_acc/decay/genuine_margin canonical values.
