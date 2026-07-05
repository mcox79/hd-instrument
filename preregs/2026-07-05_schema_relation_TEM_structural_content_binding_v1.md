# Pre-registration: schema_relation_TEM_structural_content_binding_v1

**Filed:** 2026-07-05 by exp_dev (cell author). **Basis:** drill note
`notes/research_frontier_drill_inductive_relational_transfer_unseen_entities_2026-07-05.md`;
parent cell `exp_schema_relation_transform_estimator_ablation_v1` (MIDDLE_BAND, vacuous SYNTH_CORR_HARD).
**Cell:** `experiments/exp_schema_relation_TEM_structural_content_binding_v1.py`.

## Scientific question
Does a brain-first (Tolman-Eichenbaum Machine) structural/content factorization give genuine
subject-conditional relational transfer to NOVEL (never-seen, inductive) entities on real
ConceptNet triples, where every prior AVERAGED/GLOBAL-transform substrate cell failed
(shuffle-invariant)? Load-bearing metric: REAL - SHUFFLED on INDUCTIVE eval (raw accuracy is a
relation-prior trap). Constructive build; ZERO generative-LLM calls; NOT vs-LLM.

## Mechanism axis (primary comparison)
- **GLOBAL** (reference baseline; the exhausted family, K=1 degenerate of TEM): single per-relation
  naive-mean transform. NOT a "win" arm -- the thing every prior cell already showed fails.
- **TEM_STRUCTURAL_BINDING** (PRIMARY, brain-first): cluster train subjects into K type-prototypes
  via bundle-centroid superposition (PP-254 mechanism); per-type transform M_k (reusable structural
  code); novel subject classified to nearest prototype (fast content-to-structure binding),
  type-transform applied, object resolved by argmax cleanup. K swept {5,10,20}.
- **ENTITY_FEATURE_SCORER** (SECONDARY, differentiable fallback): trained bilinear projected
  content scorer s(f_subj, f_obj); softmax-CE full-codebook negatives; inductive.

## Content encoding axis (the content slot)
- **bge_semantic**: BAAI/bge-small-en-v1.5 bounded cache -> centered unit feature + phasor.
- **gsbc**: program's TARGET encoder (GSBC_EXPAND2X: bge-large -> distilled sparse 8192-d
  global-WTA code). Self-contained precomputed cache (codes only; NO model/import at runtime).
  Cache-gated: absent -> per-unit GSBC_CACHE_MISSING; bge + mechanism axis stay valid.
- Both caches (`*_schema_TEM_entities_v1.npz`) cover ALL 4 relations (rebuilt to include CapableOf,
  which the prior ablation cache omitted).

## Relations
- Semantic (HP-eligible, >=3 per drill): **AtLocation, CausesDesire, CapableOf**.
- Surface negative-baseline (NOT HP-eligible): **DerivedFrom** (watch shuffle-climbs-to-real).

## Arms (PAIRED -- same split/seed/clustering; only manipulation differs)
REAL (true pairs, HP gates apply to mechanism arms) | SHUFFLED (object labels permuted; for TEM,
clustering on unchanged content, only per-type transform from shuffled pairs; must stay ~chance) |
MEAN_OBJECT (C-independent popular-object control). EVAL: inductive (novel-subject, PRIMARY) +
transductive (seen-subject held-out object; gap reported).

## Pre-registered bands (LOCKED)
gain(arm)=arm_acc-1/V_eff; primary = REAL, inductive, M_OP=200; best-of {TEM over K, SCORER} per
semantic relation x encoding.
- **HARD_PASS**: a TRUSTWORTHY mechanism family clears `real_gain(ind) >= 0.2075` (0.20 + 5%
  band-width, META_RULE_L) AND `real_minus_shuf(ind) >= 0.2075` AND `real_minus_meanobj(ind) >=
  0.05` on >=1 semantic relation. TEM win = headline (brain-aligned); SCORER-only win reported
  honestly as brain-first arm NOT winning.
- **HARD_FAIL**: BOTH mechanism families `real_minus_shuf(ind) <= 0.05` on ALL semantic
  relations x encodings WHILE BOTH synth discriminators fired -> honest inductive content-wall.
- **MIDDLE_BAND**: `0.05 < real_minus_shuf(ind) < 0.2075` from a trustworthy family; OR a synth
  discriminator did not fire (uninterpretable, cannot claim HARD_FAIL); OR transductive-only.

**Per-family discriminator gating (load-bearing repair of the vacuous-control failure mode):**
a mechanism family's real result is TRUSTWORTHY only if ITS OWN synth discriminator fired. A
marginal TEM control must NOT invalidate a robustly-firing SCORER result (or vice-versa).

## Repaired positive controls (Gate D; the prior SYNTH_CORR_HARD SATURATED naive=1.0 = vacuous)
- `SYNTH_ROT_CLEAN`: GLOBAL recovers clean rotation ~1.0 (algebra sanity). MEASURED@smoke:1.000.
- `SYNTH_TYPE_HARD` (TEM discriminator): K_true=20 type-conditional rotations + type signature.
  GLOBAL below ceiling; TEM must beat GLOBAL by >= TEM_ADV_MIN=0.04 (aggregate). CALIBRATED over
  full seeds 7,13,19: GLOBAL~0.66, TEM~0.78, tem_adv +0.114 (per-seed +0.085/+0.083/+0.175).
  MEASURED@smoke(seeds7,13): G=0.69 TEM=0.77 adv=+0.084 fires=True. NOTE: the TEM edge is
  genuinely MODEST because FHRR preserves object identity multiplicatively through any diagonal
  transform (a real property; discriminator threshold set accordingly).
- `SYNTH_CONTENT_MAP` (SCORER discriminator): object = linear-map(subject content) + codebook
  nearest. GLOBAL ~chance; SCORER must beat GLOBAL by >= SCORER_ADV_MIN=0.05.
  MEASURED@smoke: G=0.042 SC=0.203 adv=+0.160 fires=True.

## SCHEMA-VET mandatory fields
- `cardinality_ok`: EXPECTED_N_UNITS = 4 rel x 2 enc x (5 mech_slots x 2 arm x 2 eval + MEAN_OBJECT
  x 2 eval) x seeds = 352 (smoke, 2 seeds) / 528 (full, 3 seeds). Verdict emits CARDINALITY_BREACH
  if good_units < expected (gsbc-cache-missing tolerated). MEASURED@smoke: 352/352, 0 failed.
- `crlb_n/a`: argmax transfer has no closed-form CRLB noise floor. Chance = 1/V_eff = 0.01;
  reachability: (1/V)+0.2075 = 0.2175 < 0.95 saturation. Declared.
- `arms_differ_verified`: hash-test over {GLOBAL_REAL, TEM_REAL, MEAN_OBJECT, SCORER_REAL,
  SCORER_SHUF} predictions. MEASURED@smoke: True (5 distinct digests).
- `final_metrics_atomicity`: tmp_replace (os.replace on metrics.json.tmp).
- `baseline_in_band`: SYNTH_TYPE_HARD GLOBAL in (0.05,0.95); controls (SHUFFLED) ~chance.
  MEASURED@smoke: GLOBAL_synth=0.69 in-band; SHUFFLED synth ~0.03.
- `discriminator survives scale`: SMOKE runs at FULL N=8192; only seeds/test/steps shrink. Both
  discriminators fire at full N in smoke.
- `progress_logging`: print_flush_true (all progress + heartbeat lines flush=True;
  sys.stdout line_buffering). Per-seed timing printed. (timeout_s well under 1800 anyway.)
- `defensive_error_checking`: start-marker + crash-diagnostic (Exception -> CELL_CRASHED
  metrics.json + traceback); except SystemExit: raise BEFORE except Exception (no BaseException /
  bare except -- grep-verified clean).
- `cell_chunked`: false (single-cell 3-seed via _seed_checkpoint resumable partials; each seed a
  distinct partial file; fast enough that chunking is unnecessary at ~30s/seed).

### §15 composition/sweep gates
- **Gate A (effective vs nominal)**: swept param K (TEM types). effective_K per (rel,enc,seed) =
  min(K, n_train_subjects). At M_OP=200 train pairs, K in {5,10,20} all << 200 -> ALIGNED (no
  MISALIGNMENT; every K distinct). `sweep_alignment_verdict: ALIGNED`.
- **Gate B (discriminating band)**: the discriminating metric is real_minus_shuf (not raw acc).
  Predicted/MEASURED@smoke real_minus_shuf lands in the discriminating (nonzero, sub-HP) band on
  AtLocation/CausesDesire for both mechanisms x both encoders (>= 6 of 12 semantic cells in
  (0.05, 0.2075)); CapableOf near floor. `discriminating_fraction >= 0.30` satisfied.
- **Gate C (shape compatibility)**: composition edges: content phasor -> bundle-centroid cluster
  (SHAPE_MATCH: unit phasors); cluster proto -> per-type naive-mean transform (SHAPE_MATCH); novel
  content -> nearest-proto classify (SHAPE_MATCH); transform -> argmax cleanup (SHAPE_MATCH). For
  SCORER: content feature -> fixed projection -> bilinear (SHAPE_MATCH). No SHAPE_MISMATCH_no_adapter.
- **Gate D (positive control reproduce at test regime)**: SYNTH_ROT_CLEAN (GLOBAL >= 0.90) +
  SYNTH_TYPE_HARD (TEM > GLOBAL) + SYNTH_CONTENT_MAP (SCORER > GLOBAL) all AT N=8192 (the test N).
  PP-254 bundle-centroid clustering reproduced via kmeans_phasor selftest (purity >= 0.85).
- **Gate E (functional requirements)**: (1) classify novel entity by content -> PP-254 bundle-
  centroid (kmeans_phasor). (2) reusable per-relation structure -> per-type naive-mean transform
  (structural code). (3) resolve specific object -> argmax cleanup / bilinear scorer. (4) trained
  component (satisfies PROVEN CONSTRAINT that untrained codebook scores 0.0) -> type-clustering +
  per-type transforms + scorer W are all fit-from-data.

## Compute architecture
Class **(b) sequential-CPU with justification**: all mechanisms are small-matrix numpy at V=100,
M=200, N=8192 -- per (rel,enc,seed) wall < 10s; full grid ~3-5 min total. GPU gives NO meaningful
speedup at V=100 (tiny matmuls; launch overhead dominates). The ENTITY_FEATURE_SCORER is
implemented as a numpy analytic-gradient bilinear (NOT torch) so the whole cell is self-contained,
import-safe on the remote, and needs NO GPU. Storage strategy: no_storage (no substrate write; in-
memory codebook algebra only). MEASURED smoke wall: ~29s/seed at reduced config -> GPU unwarranted.

## Dispatch
`remote_cpu_queue` (numpy CPU; no torch/GPU). Runner injects HDLAB_RUN_MODE=full -> RUN_MODE=full.
GSBC + BGE caches (`*_schema_TEM_entities_v1.npz`) + conceptnet dataset must be present on the
remote (explicit SCP -- NOT auto-shipped). timeout: 1800s (ample; measured ~3-5 min).

## HYPOTHESIZED priors (per drill; calibration-penalized)
- P(TEM clears HARD_PASS on >=1 semantic relation, inductive | control valid) = 0.28
  HYPOTHESIZED@drill.
- P(SCORER clears HARD_PASS) = 0.24 HYPOTHESIZED@drill.
- P(MIDDLE_BAND partial signal) = 0.35 HYPOTHESIZED@drill.
- Smoke MEASURED: MIDDLE_BAND (nonzero inductive real_minus_shuf on AtLocation/CausesDesire, both
  mechanisms x both encoders; below HARD_PASS) -- consistent with the ~0.35 MIDDLE_BAND prior.
