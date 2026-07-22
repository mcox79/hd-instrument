# PRE-REGISTRATION: compgen native-bind GEOMETRY ABLATION v1

**Filed:** exp_dev, 2026-07-22, BEFORE running full. LOCAL-ONLY (no push, no store mutation, no atom bank).
**Anchor:** `compgen_geometry_ablation_v1`
**Cell:** `experiments/exp_compgen_geometry_ablation_v1.py`
**Harness reuse:** imports `experiments/exp_compgen_native_bind_attested_real_text_v2.py` (NO new mechanism;
same NativeBind / FlatSharedReadout / attested real-text held-out split / PPMI-SVD corpus / train loop).

## QUESTION (resolves the HP2 conflation, drill 2026-07-22)
Atoms 29432/29433 (compgen) were ruled MEASURED_MECHANISM because HP2 (native beats the role-specific TIED
control at hard load) failed. The brain-drill found HP2 conflated (1) shared-vs-role-specific (mis-specified;
brain is role-specific + shared GEOMETRY, Frankland-Greene) and (2) LEARNED-vs-FIXED (the real free-algebra
concern, 29399, STILL UNRESOLVED). This ablation resolves (2): does native's held-out generalization come
from the LEARNED binding, or is it RIDING ON the free distributional filler-GEOMETRY (PPMI-SVD)?

## ONE VARIABLE: filler-geometry meaningful-vs-randomized
The "meaningful geometry" is entirely `corp["emb"]` (PPMI-SVD distributional embeddings), consumed identically
by every arm as the real-feature front-end `Rfeat`. The ablation replaces `emb` with **identity-preserving,
semantic-geometry-destroying** vectors:
- **WHAT IS RANDOMIZED:** each concept gets a FIXED distinct random Gaussian unit vector (same shape V x EMB_D,
  same unit-L2 norm as real emb, one fixed instance seed-independent like real emb).
- **PRESERVED:** concept IDENTITY (each concept -> a consistent distinct code every use) + dimensionality + norm.
- **DESTROYED:** inter-concept SEMANTIC/DISTRIBUTIONAL STRUCTURE (random Gaussian is near-orthogonal,
  off|cos| ~ 1/sqrt(EMB_D); no distributional neighbors, no polysemy, no frequency structure).
- Everything else identical between geom and random: SAME triples, SAME vidx/vocab, SAME attested held-out
  split, SAME subsample per seed. Only emb changes.

## ARMS (2x3 factorial; harness-reuse, SAME mechanism)
Trained arms x geometry variants:
- native_bind_shared  @ {geom, random}   (native-with-geometry = original; native-RANDOM = ABLATION)
- flat_shared_readout @ {geom, random}   (FAIR baseline; geom = the reference native must beat)
- native_bind_tied    @ {geom, random}   (role-specific control; the drill's original ablation target)
- native_bind_scramble @ {geom, random}  (decode-time random-role-key lesion; MUST-FAIL)
Named gate quantities (per task): native_geom_ho, native_random_ho, flat_geom_ho, tied_geom_ho, chance.

## MATCHED-HARD OPERATING POINTS
Difficulty swept by DATA-FRACTION. Compare held-out at MATCHED in-dist (removes the confound of comparing
held-out at different in-dist). Matched on native_RANDOM's in-dist (the arm under test):
- HARD band  = [0.75, 0.90] in-dist (target 0.825)
- HARDER band = [0.55, 0.68] in-dist (target 0.62)
For each target: native_random frac closest to target -> its in-dist; native_geom + flat_geom each matched to
that in-dist (frac with closest in-dist).

## PRE-REGISTERED GATE (bands fixed BEFORE running; reference = REAL-geometry v2/v3 on disk)
Reference facts (REAL geometry, MEASURED@data/exp_compgen_native_bind_matched_hard_v3/metrics.json):
native_geom_ho = 0.43 @ in-dist 0.83; 0.21 @ 0.62; flat_geom_ho ~ 0.0 all fracs; chance = 0.00203.

### MUST-FAIL SANITY (validity gate; MUST hold or ablation is INVALID)
- `native_random` IN-DIST @ full data >= 0.60. If < 0.40 -> ABLATION_INVALID (identity broken, not just
  geometry) -> do NOT interpret held-out. (Confirms the ablation destroyed geometry, not concept identity.)
- geometry actually destroyed: code_off_cos(random) <= 1.2 x random-floor AND code_off_cos(geom) >= 1.5 x floor.

### HARD-PASS-A (LEARNED-binding-does-it -> CG CANDIDATE ONLY; goes to FRESH adversarial VET + USER; NOT self-declared)
At the HARD matched point (native_random in-dist in [0.75,0.90]), ALL of:
- (A1) native_random_ho >= 20 x chance (= 0.041; strongly above chance)
- (A2) native_random_ho >= flat_geom_ho + 0.15 (beats the fair geometry-equipped baseline by >= 15pp)
- (A3) native_random_ho >= 0.50 x native_geom_ho (retains >= 50% of with-geometry held-out; geometry NOT dominant)
- (A4) native_random learning curve rises: init <= 0.10 AND rise >= 0.20 (NOT high-by-construction)
- (A5) scramble_random_ho <= 0.05 (binding lesion collapses)
- (A6) breaches == 0 (no novelty leak)
-> the generalization is LEARNED, not geometry-free -> CHAIN-GRADE CANDIDATE (pending fresh adversarial VET).

### HARD-FAIL (GEOMETRY-FREE -> MEASURED_MECHANISM confirmed, for the RIGHT reason)
At the HARD matched point, ANY of:
- native_random_ho <= flat_geom_ho + 0.05, OR
- native_random_ho <= 5 x chance (= 0.0102), OR
- native_random_ho <= 0.20 x native_geom_ho
-> native RODE ON the free distributional geometry -> MM confirmed (resolves HP2 conflation cleanly).

### MIDDLE (graded geometry contribution)
native_random_ho in (0.20, 0.50) x native_geom_ho AND above flat_geom+chance but below the A3 bar
-> bounded partial geometry-dependence; report as graded, neither clean CG-candidate nor clean collapse.

## HONESTY / CONFLICT-OF-INTEREST
Director WANTS the first CG. MOST-LIKELY outcome (per frequency-wall + HP2 showing geometry does the work at
hard load) is HARD-FAIL = MM confirmed = a FINE, definitive close of the CG question. HARD-PASS-A is reported
as a CG-CANDIDATE ONLY -> fresh adversarial VET + USER before any tier claim. No self-declared CG.

## COMPUTE ARCHITECTURE
Sequential-CPU justified: cell IS validating a substrate primitive (FHRR bind/unbind + learned encoder) at
tiny complex matmul scale (N=256, V=492); wall ~5-8 min foreground-LOCAL (v2 full=95s, v3=207s; this = 2x arms).
Storage: no_storage (per-triple encode+decode, no bundle store). final_metrics_atomicity: tmp_replace.
deterministic_seeding: fixed int seeds + np.random.default_rng(fixed) + sorted() splits; NO hash()-seeded RNG.
progress_logging: line-buffered prints (wall << 30min). crlb_n/a: classification-accuracy discriminator; bands
feasibility-checked vs chance=1/V and vs REAL-geometry reference numbers on disk.

## EXPECTED_N_UNITS (cardinality_ok)
= len(variants=2) x len(trained_arms=3) x len(fractions) x len(seeds) + scramble(2 x fractions x seeds).
Verdict counts per_unit; mismatch -> HARD_FAIL_CARDINALITY_BREACH.
