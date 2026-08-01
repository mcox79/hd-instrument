# Prereg: grammar-learner FILLER-generalization -- known structure + brand-new entity filler
# (never bound at learn time) -- structure-content factorization axis, complement of the
# sibling novel-STRUCTURE-combo cell

Filed alongside `experiments/exp_grammar_learner_filler_generalization_v1.py`. CHEAP/CPU,
LOCAL-ONLY, foreground-to-completion. CONFIRMATORY-TIER, not exploratory -- see prior-work section.

## What this build tests

The sibling cell (`exp_grammar_learner_encounter_rule_uncover_generalize_v1.py`, commit
76f9e6249, MIDDLE_BAND 2026-08-01) proved the accumulate-encounters loop generalizes to NOVEL
STRUCTURE COMBOS. It did not test the USER's other named axis: known STRUCTURE + a BRAND-NEW
FILLER (entity identity never bound at learn time) -- the entorhinal/Tolman-Eichenbaum-Machine
structure-content factorization claim. This cell isolates that ONE VARIABLE (filler-factored vs
filler-keyed-lookup), holding structure fully known (all 16 combos trainable).

## MANDATORY prior-work disclosure (substrate_query.sh, run before authoring, 2026-08-01)

`bash tools/substrate_query.sh "structure content factored binding novel filler entity
generalization FHRR unbind"` returned, at **cosine=0.3545** (top hit, cert_ledger/atoms):
`experiments/exp_role_filler_factorization_compgen_v1.py` (prereg
`preregs/2026-07-18_role_filler_factorization_compgen_v1.md`, metrics
`data/exp_role_filler_factorization_compgen_v1/metrics.json`) -- **HARD_PASS, 5 seeds,
2026-07-19**: FACTORED held-out accuracy=1.000, FLAT (memorization) held-out=0.003, gap=0.997,
must-fail control fired, positive learning-curve-vs-diversity (gcos 0.43->0.998). This is the
SAME core scientific claim (native FHRR bind/unbind structure-content factorization generalizes
to a held-out filler where a memorization baseline fails), already measured at HIGHER rigor
(LEARNED content-blind structural code g_hat via TEM-Hebbian averaging, not a hand-fixed
codebook; diversity sweep; m-capacity probe; 5 seeds) than this cell. A family of follow-on
cells already exists (`exp_role_filler_factorization_{realcontent,conceptnet,reader_coupled,
assembled_reading_axis,learning_curve}_cg_v1.py`).

**Novelty verdict: REDISCOVERY of the core mechanism claim.** This cell is authored anyway,
scoped down, for the one genuinely missing thing: does the SAME proven mechanism generalize to a
held-out filler when wired through THIS session's specific grammar-learner accumulate-loop
apparatus (proginduction legibility readout + estimation-plugin can-fail floor + checkpointed
learning curve) -- an integration confirmation inside the current arc's own tooling, not a fresh
capability discovery. Bands below are calibrated accordingly (confirmatory, not exploratory).

## Reused machinery

- `hdlab/atoms.py` (`make_atom_fhrr`, `similarity`) + `hdlab/bundling.py` (`bundle`) -- same FHRR
  structure codebook convention as the sibling cell, PLUS a new filler codebook (48 fixed unit
  vectors, one per entity identity).
- `hdlab/learner/plugins/estimation_plugin.py` `generic_mdl` mode, keyed on `filler_id` (not atom
  combo this time) -- can-fail floor.
- `hdlab/learner/plugins/proginduction_plugin.py` -- legibility readout, filler-blind by
  construction (never given the filler feature).

## Planted rule (identical to the sibling cell, for direct comparability)

4 boolean atoms: `precedes_verb, is_definite, is_proper_noun, follows_comma`.
`label = AGENT if XOR(precedes_verb, is_definite) or (is_proper_noun and not follows_comma) else
PATIENT`. Full 16-combo truth table is **10 AGENT / 6 PATIENT** (MEASURED, not the naively
assumed 8/8 -- corrected during smoke).

## Filler axis (new)

`N_FILLER_POOL=48` fixed FHRR unit "entity identity" vectors, generated once (a priori
addressable codebook -- the entorhinal-grid framing: the slot exists structurally before any
content is bound to it). Deterministic split: filler ids 0..35 = TRAIN (36), ids 36..47 =
HELD_OUT (12). HELD_OUT fillers are never bound into any encounter in the learn stream --
asserted (leakage guard) at self-test and full.

## Encounter stream

`N_STREAM=256`, same Zipf-like weighting as the sibling cell (`weight[i]=1/(i+1)` over sorted
16-combo order -- ALL 16 combos eligible, unlike the sibling's 12/16 split) x filler drawn
uniformly at random from TRAIN fillers only, via `random.Random(20260801)` (PROT-023). 2 decoy
booleans per encounter, unused by any arm.

## Probes (deterministic, not random)

Two full cycles of the 16-combo enumeration paired with held-out / train fillers respectively:
`NOVEL_FILLER_PROBES = [(combos[i%16], HELD_OUT_FILLERS[i%12]) for i in range(32)]`,
`SEEN_FILLER_PROBES = [(combos[i%16], TRAIN_FILLERS[i%36]) for i in range(32)]` -- IDENTICAL
class-mix (20 AGENT/12 PATIENT each), so the seen-vs-novel comparison is apples-to-apples.
SEEN_FILLER_PROBES accuracy of the FACTORED mechanism = the POSITIVE CONTROL.

## Learning curve

CHECKPOINTS = [4, 8, 16, 32, 64, 128, 256], same as the sibling cell. FACTORED mechanism: CLS-style
dedup-by-distinct-atom-combo (matching the sibling cell's pattern) before bundling recovered
structure vectors into per-class prototypes -- well-founded here because `recovered_structure`
for a given combo is IDENTICAL regardless of which filler bound it (exact FHRR unbind algebra,
confirmed at self-test: bind-then-unbind cosine > 0.999 for ANY filler, seen or unseen). A
first no-dedup version (raw per-instance bundling, intended as a harder superposition-capacity
stress) was tried and MEASURED to plateau at 0.625 on BOTH seen and novel identically -- a
bundling-capacity confound from Zipf-skewed combo frequencies overwhelming minority combos within
their own class bucket, UNRELATED to the filler axis. Dedup removes that confound so the
one-variable comparison (filler-factored vs filler-lookup) is isolated cleanly.

## Pre-registered bands (calibrated at SMOKE time, before the final full run's verdict was read)

Calibrated against this cell's OWN measured structure-bundling ceiling: dedup-by-combo CLS
consolidation with all 16 combos covered plateaus at **seen=novel=0.875 at N=256** (MEASURED at
smoke, not hypothesized) -- a genuine structure-bundling capacity ceiling (10 AGENT + 6 PATIENT
near-orthogonal FHRR vectors bundled into 2 prototypes), orthogonal to the filler axis.

- `POS_CONTROL_SEEN_FILLER_MIN = 0.75` (mechanism acc on SEEN_FILLER_PROBES at N=256; MUST pass.
  Calibrated to the sibling cell's own measured ceiling of 0.75 at 12/16 combos; this cell covers
  all 16 so should clear it -- not an arbitrary 0.90.)
- `FLOOR_MUST_FAIL_MAX = 0.65` (floor acc on NOVEL_FILLER_PROBES, any checkpoint)
- `MECHANISM_NOVEL_HARD_PASS_MIN = 0.80` (mechanism acc on NOVEL_FILLER_PROBES at N=256)
- `MECHANISM_NOVEL_MIDDLE_MIN = 0.65`
- `PARITY_GAP_MAX = 0.05` (|seen_acc - novel_acc| at N=256 -- the PRIMARY, load-bearing
  discriminator: near-exact parity is the actual filler-factorization signature, since FHRR
  bind/unbind cancels the filler factor algebraically whether or not it was ever seen at learn
  time. The absolute-accuracy bands are secondary and capped by the unrelated structure-bundling
  ceiling shared identically by both probe sets.)

HARD_FAIL if: positive control < 0.65 (pipeline lifts nothing, can't trust any novel-filler
null), OR floor exceeds 0.65 on novel probes at any checkpoint (can-fail floor did not fail, test
broken), OR a held-out filler leaks into the learn stream, OR mechanism and floor produce
identical predictions at every checkpoint (META_RULE_AF).

## Compute architecture

Class (b) sequential-CPU. Same order of magnitude as the sibling cell (7 checkpoints x 2 primary
arms + 1 legibility readout, all sub-second). MEASURED full-run wall time = 9.73s (local .venv,
2026-08-01). LOCAL-ONLY, foreground-to-completion, NO queue, NO push, NO remote-persist, NO atom
bank (Skunkworks VETs separately). Deterministic: OMP/MKL/OPENBLAS_NUM_THREADS=1, fixed int seed
20260801, no hash()-derived RNG/ordering (PROT-023).

## Cell-template mandates (applicable subset)

- `arms_differ_verified` at full (hash test, mechanism vs floor predicted-class tuples on the
  NOVEL probe set, across all checkpoints).
- `final_metrics_atomicity: tmp_replace` (`os.replace`).
- `except SystemExit`/`KeyboardInterrupt`: raise BEFORE `except Exception` (no `BaseException`).
- `crlb_n/a`: accuracy/generalization measurement, not a capacity/CRLB-bound cell.
- `baseline_in_band: n/a` (filler-keyed lookup IS the discriminating must-fail floor under test).
- `discriminator survives scale: n/a` (fixed small synthetic domain).
- `cardinality_ok`: `EXPECTED_N_UNITS = len(CHECKPOINTS) * 2 primary arms = 14`.
- `calibration_check: default_ok_for_this_regime` (bands calibrated at smoke time against this
  cell's own measured structure-bundling ceiling, principled + logged, not post-hoc p-hacked --
  the full run's verdict was not read before the bands were fixed).
- `deterministic_seeding: true`.
- Multi-unit checkpoint/resume via `tools/exp_checkpoint.py` (unit = checkpoint_n), per CLAUDE.md
  mandate, wired even though wall time is seconds.
- All numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@ in the cell docstring.
