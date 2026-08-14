# Pre-registration -- exp_meaning_supply_separation_v1

**Filed:** 2026-08-14, BEFORE the run. **Cell:** `experiments/exp_meaning_supply_separation_v1.py`
**Question:** the handoff's #1 open question (`notes/HANDOFF_full_project_report_for_new_team_2026-08-14.md`
5.3 MEH #1, 7, 10 Q1): does supplying RICHER PER-WORD MEANING CONTENT to the live C3
open-vocabulary grounding read-out improve **within-neighbourhood separation** -- or is meaning
supply not the constraint?

---

## 0. GROUND TRUTH ESTABLISHED FIRST (measured, `data/exp_meaning_asset_coverage_probe_v1/metrics.json`, commit 8931ab5f6)

The handoff's framing rests on three premises that the coverage probe **corrects on disk**. They
are recorded here because they change the arms, and because a cell must not silently test a
different claim than the one it cites.

1. **The hand lexicon is NOT on the C3 read-out path at all.** `hdlab/reading_grounding_loop.py`
   -- the module the C3 cell imports its entire meaning path from -- does **not** import
   `hdlab.lexical_similarity` (measured: `rgl_imports_lexical_similarity=false`); it imports only
   `hdlab.closed_class_lexicon`, a function-word stoplist. The C3 decision variable is cosine
   between `context_vector_masked` bags of nearby content-word lemmas (d=256 hashed bipolar,
   `GRADED_COMPARATOR` ON), compared in `ConceptSpace` via `canonicalize_fast`. So "meaning in the
   live path is a ~380-word hand lexicon" is **false for this gate**: the lexicon is neither the
   bottleneck nor a component of it.
2. **True asset sizes differ from the cited ones.** `CONCEPT_FEATURES` = **359** words (not ~380);
   the joined Lancaster+Brysbaert grounded vocabulary = **36,810** words (not 39,707 -- the 39,707
   is Lancaster's raw row count before the multi-token/intersection cleaning the module applies).
3. **The norms island is ALREADY WIRED**, since 2026-08-11, as an OOV fallback inside
   `lexical_similarity.concept_similarity(use_grounded_fallback=True)`, capped at
   `GROUNDED_CAP=0.45`. It is not an untouched island. It is, however, wired into a module the C3
   path never calls -- so it is unreachable *from this gate*, which is the real defect.
4. **`load_improved_encoder` and the `encoder=` plug point are DIFFERENT, INCOMPATIBLE interfaces.**
   `process_sentence(encoder=...)` expects a `StructuralEncoder` (UD dependency-role-bound bipolar
   vector, `structural_vector_masked`, landed 2026-08-13). `hdlab/encoder_retrain_persist.load_improved_encoder`
   returns an `eb.EncoderExtractor` (`V2Transformer`, d_model=512) whose public API is
   `decode_dataset_slots` / `cue_vec` / `oracle` and whose cue set is the SYNTHETIC slot harness
   (`{'ENT': 'what was the entity ?', 'MARK': 'what was tagged ?', 'S': 'what was set to ?',
   'P': 'what was placed to ?'}`). It has **no word- or sentence-embedding API**
   (`has_word_embedding_api=false`). It loads and runs (48.7s, 3 certified seeds).

**Coverage of the C3 anchor vocabulary** (measured on the 10,502-lemma superset the C3 filter
admits; the cell below re-measures on the exact `space.anchors()` set it builds):
hand lexicon **2.79%** (293), grounded norms **69.02%** (7,249), live fallback path (either)
**69.10%**, encoder tokenizer whole-word **43.86%** (4,606 / 16,000-token vocab).

**Consequence for the design.** Arm 2 is still meaningful and is the faithful version of "wire the
norms": route the norms into *this* gate's comparison, where they have 69% coverage and are
currently unreachable. Arm 3 must be honest that no encoder word-embedding API exists, so the
cell constructs one (mean-pooled `tok_emb+pos_emb+enc+norm` hidden states) and reports the result
as **OUT-OF-DISTRIBUTION** use of an encoder trained on a synthetic templated grammar. That is the
fair test of "wire the encoder"; it is not a claim that the encoder was built for this.

---

## 1. Design

**Reuse, not reimplementation.** The cell imports `build_corpus`, `build_buckets`, `build_space`,
`build_items`, `gold_meaning_set` from `experiments/exp_grounding_readout_known_answer_v1.py`, so
the corpus, the anchor construction, the item construction and the gold set are the SAME OBJECTS
as the 4.80% baseline, not lookalikes. A self-test asserts the BASE arm reproduces that cell's
argmax exactly on a shared subset.

**Scoring.** Per item, over the eligible anchor pool (the lemma's own anchors masked out, exactly
as B5 does), the base score is `canonicalize_fast`'s cosine, recomputed as the identical matvec so
that full RANKS are available. Auxiliary meaning signals are blended **after per-item z-scoring of
both signals across the candidate pool** (scale-free, so the blend weight has one meaning):

    score_arm = z(base_cos) + w * z(aux_sim)

- **A1_BASE** -- live path, unchanged (w=0).
- **A2_NORMS** -- `aux = cos(grounded_vector(L), grounded_vector(anchor))`, the 12-dim
  Lancaster sensorimotor + Brysbaert concreteness profile. Anchors OOV of the norms get
  `aux = 0` (z-scored within the covered subset; the uncovered keep base ranking).
- **A3_ENCODER** -- `aux = cos(enc(L), enc(anchor))`, mean-pooled `V2Transformer` hidden states.
- **A4_BOTH** -- both aux terms, each at w.
- **w grid (PRE-REGISTERED, fixed):** `w in {0.25, 0.50, 1.00}`. **The HEADLINE arm is w=0.50.**
  The full grid is reported as sensitivity; **the max over w is an OPTIMISTIC UPPER BOUND and is
  labelled as such in the metrics, never quoted as a shipped number.**

**Floors (ARMS, not assertions).**
- **F_SCRAMBLE** -- donor-lemma query (the B6 construction), per arm.
- **F_FREQUENCY** -- pick the most frequent eligible anchor.
- **F_PROJDRAW** -- BASE re-run over `R=3` independent salted draws of the random projection
  (salted reimplementation of `context_vector`, with a self-test asserting salt=`""` reproduces
  the live function BYTE-IDENTICALLY). Reported as an **sd**: a hit@1 delta smaller than this sd
  is noise, whatever its bootstrap CI says.

**Metrics, per arm (the separation-specific ones are the point).**
- `hit@1` (primary; baseline **0.0480**, scramble floor **0.0080**).
- **`median_rank`** of the best gold anchor, and **`frac_gold_in_top50`** -- the diagnostic pair:
  they say whether meaning got *better*, not whether argmax got lucky.
- **`sister_error_conversions`** -- items BASE got wrong that the arm gets right, and the reverse
  (net). The rank-1 common-mode cell converted exactly ZERO; that is the number to beat.
- **`crowding`** -- median nearest-neighbour score among a sample of anchors **under that arm's own
  metric**, against a random-permutation null of the aux signal. Live baseline **0.4637 vs 0.2264**.
- Paired bootstrap (n=5000) CIs on every arm-minus-BASE delta and every arm-minus-floor delta.

**Secondary:** near-neighbour 2AFC is NOT re-run in this cell (separate harness); its live
baseline is **0.698** at d=256 graded-ON. Never quote 0.7495 (unshipped d=1024) or 0.69975
(unshipped divisive-norm arm).

**Settings declared:** `GRADED_COMPARATOR` **ON** (default at HEAD), d=CTX_D=**256**,
`readout=None`, `MASTER_SEED` inherited from the C3 cell. Stated because arms must be comparable
to the 4.80% baseline, which ran under the same settings.

---

## 2. Bands (CAN-FAIL, declared before the run)

Let `d = hit@1(arm, w=0.50) - hit@1(A1_BASE)`, paired-bootstrap CI, and `sd_proj` = F_PROJDRAW sd.

- **PASS_GATE_CLEARED** -- some arm reaches **hit@1 >= 0.10** (the C3 revival gate) with CI
  excluding the base. Would mean: wiring meaning supply closes the gate.
- **MIDDLE_BAND_REAL_BUT_SHORT** -- some arm has `d >= +0.020`, CI excludes 0, `d > 2*sd_proj`,
  **and** median rank falls **and** crowding falls -- but hit@1 < 0.10. Real separation gain,
  gate still open.
- **MIDDLE_BAND_ARGMAX_ONLY** -- `d >= +0.020` with CI excluding 0 but median rank and crowding
  do NOT improve. Explicitly flagged as **SUSPECT**: an argmax gain without a rank/crowding gain
  is not a separation gain.
- **HARD_FAIL_NO_EFFECT** -- no arm has a `d` whose CI excludes 0 at `+0.020`, AND no arm reduces
  median rank by >=10%, AND no arm reduces crowding. **This is a RESULT**: it closes the
  handoff's #1 hypothesis and says meaning SUPPLY is not the binding constraint on C3.
- **HARD_FAIL_HURTS** -- some/all arms significantly BELOW base (the composed-chain outcome).

**Discriminator-fires check (must hold at smoke):** the smoke run must show the arms producing
DIFFERENT hit@1 / median-rank values from BASE (arms-must-differ), and F_SCRAMBLE must sit far
below BASE. If every arm is bit-identical to BASE at smoke, the blend is not wired and the cell is
VACUOUS -- abort rather than scale.

---

## 3. The four pre-declared outcome interpretations (what distinguishes them)

1. **"The norms help"** -- A2 clears MIDDLE_BAND_REAL_BUT_SHORT or better AND A3 does not.
   Interpretation: perceptual/sensorimotor content is the missing meaning; wire the norms into the
   read-out comparison (a real, cheap default change).
2. **"The encoder helps"** -- A3 clears and A2 does not. Interpretation: learned distributional
   identity content is the lever, even OOD; the case for a properly-trained in-domain concept
   encoder becomes the program's next build.
3. **"Both needed"** -- only A4 clears, with both single-arm deltas' CIs including 0 or below half
   of A4's. Interpretation: the two supply complementary content; neither alone is sufficient.
4. **"Neither -- meaning supply is not the constraint"** -- HARD_FAIL_NO_EFFECT.
   Interpretation, and the one the pre-existing evidence most supports: the defect is not the
   AMOUNT of per-word meaning content but the **comparison geometry** (a bag-of-co-occurring-words
   vector cannot separate paradigmatic neighbours that occur in near-identical contexts, which is
   exactly what sympathetic/parasympathetic, radial/bilateral, innate/adaptive are). This would
   redirect the program away from wire-what-exists and toward the contrastive/structural
   objective -- and it retires the handoff's stated #1 move.

**EXPECTED FAILURE MODE, PRE-DECLARED.** `hdlab/grounded_similarity.py`'s own docstring records a
MEASURED ceiling: sensorimotor profiles **cannot separate synonyms from siblings** (sofa/couch
raw 0.968 vs apple/orange raw 0.952, fully overlapping distributions), which is *why* the 0.45 cap
exists. So A2 is expected to raise COVERAGE while leaving SEPARATION untouched, and A3 is the more
likely lever. If A2 nonetheless moves hit@1 **without** moving crowding or median rank, that is
the MIDDLE_BAND_ARGMAX_ONLY / SUSPECT case and must not be reported as a meaning win.
"More coverage" is already a REFUTED route (2.9% -> 35.0% coverage, still at chance); this cell
therefore judges on SEPARATION, not coverage.

---

## 4. Engineering / discipline

Threads pinned before numpy import; fresh output dir; smoke to a SEPARATE dir
(`_smoke` suffix); `metrics.json` written once via tmp + `os.replace`; `sorted(set())` throughout;
per-unit checkpoint via `tools/exp_checkpoint.py`; progress printed with `flush=True`
(`progress_logging: yes`, required at `timeout_s >= 1800`); no silent `except`; long run DETACHED
with separate stdout/stderr and PID recorded. **This cell WIRES NOTHING by default** --
`wire_status: EXPERIMENT_LOCAL_NOT_WIRED`; it reads `hdlab` and blends in its own scoring
function. No `hdlab/` default is changed by it.
