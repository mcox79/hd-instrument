# CONSOLIDATION PHASE -- RUNNING LOG (compaction-survival; append-only, newest step at the BOTTOM of each section)

**Purpose (owner 2026-08-27): keep a CLEAR running log so if this work extends beyond a compaction we keep all
the context.** This is the durable ledger of the consolidation phase: what has been landed/built/measured, with
commit hashes and verification, so a fresh session can resume mid-phase without re-deriving anything.

**READ THIS + `notes/CONSOLIDATION_PHASE_PLAN.md` (the ordered plan) + `notes/STATUS.md` (LATEST position) to resume.**

## THE GOAL (one paragraph)
All 3 in-flight problems integrated 2026-08-27 (the trilogy: graded parser/role; entity attribution-not-prediction;
conceptual meaning channel) -> the consolidation TRIGGER is met. The phase: (1) LAND every proven-but-islanded fix
into `hdlab/` in final form (default-off, witnessed, registered); (2) BUILD a ROLE-BALANCED comprehension gold (the
old McGuffey gold is agent-saturated so real wins are invisible on it); (3) WIRE the composition topology end-to-end
(§2 of the PLAN); (4) MEASURE the composed reader OFF-vs-ON on the role-balanced gold with recomputed floors +
info-free-twins-must-lose. DECISIVE either way: the modifications earn a live capability, or a rigorous negative
localises the residual binding constraint. **Discipline (owner 2026-08-27): do the RIGHT things not the easy ones;
if things aren't working like we expect, LIBERALLY run brain-foundationality research drills, finer resolution if needed.**

## LANDING LEDGER (queue rows from the PLAN; update status + commit hash as each lands)
| row | organ / fix | hdlab file | witness | registry id | status |
|-----|-------------|-----------|---------|-------------|--------|
| A | forward-prediction reader | `hdlab/predictive_reader.py` | `test_predictive_reader_organ.py` | predictive_reader_v1 | ✅ LANDED (pre-phase) |
| B | semantic-control gate | `hdlab/semantic_control.py` | `test_semantic_control_organ.py` | semantic_control_v1 | ✅ LANDED (pre-phase) |
| I | graded-competition organ + difficulty currency | `hdlab/graded_competition.py` | `test_graded_competition_organ.py` | graded_competition_v1 | ✅ LANDED 2026-08-27 (commit below) |
| J | ATL conceptual/definitional channel + operation-routing | `hdlab/conceptual_meaning.py` | `test_conceptual_meaning_organ.py` | conceptual_meaning_v1 | ✅ LANDED 2026-08-27 (commit below) |
| E | ACT-R salience binder + GRADED softmax write | `hdlab/salience_binder.py` | `test_salience_binder_organ.py` | salience_binder_v1 | ✅ LANDED 2026-08-27 (commit below) |
| F | entity-augment of the situation model | (pending) | (pending) | (pending) | ⬜ QUEUED |
| C | incremental left-corner builder | `hdlab/incremental_parser.py` | `test_incremental_parser_organ.py` | incremental_parser_v1 | ✅ LANDED 2026-08-27 (commit below) |
| D | front-end role-assignment fix | (pending) | (pending) | (pending) | ⬜ QUEUED |
| H | relcl filler-gap resolver + route-conflict | (pending) | (pending) | (pending) | ⬜ QUEUED |
| E2 | sparse per-entity trace store (DG k-WTA + CA3) | (BUILD proposal, not a landed fix) | -- | -- | ⬜ BUILD TARGET |

## MEASUREMENT (step 2-4)
| artifact | status |
|----------|--------|
| ROLE-BALANCED comprehension gold | ⬜ NOT STARTED |
| composed-reader end-to-end harness (OFF-vs-ON) | ⬜ NOT STARTED |
| the payoff number (composed reader vs floors, twins losing) | ⬜ NOT MEASURED |

---

## STEP-BY-STEP LOG (newest at the bottom)

### 2026-08-27 -- STEP 0: phase opened
Trigger met (all 3 in-flight integrated: commits 71af8bf26 entity, ce376e4cf discrete-graded, 0ecec1964 conceptual).
`CONSOLIDATION_PHASE_PLAN.md` flipped ARMED -> ACTIVE. Policy: NO new problem packaging (queue drained to zero by
design); one deliberate step per focused round.

### 2026-08-27 -- STEP 1: landed the GRADED-COMPETITION organ (queue row I) ✅
- **`hdlab/graded_competition.py`** created -- additive Lewis-Vasishth activation -> softmax maintained distribution
  with readouts {win, p, entropy, margin, cycles}; `map_pick` (the discrete resolver's argmax collapse), `difficulty`
  (the shared gold-free entropy currency). Ported the validated `net_activation`/`softmax`/`normalized_recurrence`/
  `graded_pick` VERBATIM from the integrated cell. DEFAULT-SAFE (new module; nothing imports it yet -> no behaviour
  change; `map_pick` reproduces the discrete resolver exactly).
- **Witness `verification/test_graded_competition_organ.py`** -- self-contained construction proof, run FIRST-HAND,
  PASS: entropy(error)-entropy(correct) +0.043 CI[+0.035,+0.052] (CI-separated); info-free random-settling twin
  -0.010 CI[-0.027,+0.006] (loses); noise->0 collapse (graded argmax == map_pick == argmax(net); high-gain one-hot);
  glass-box (no gold in signature; normalized entropy candidate-count-robust; decisive item -> ~0 entropy).
- **Registered** `graded_competition_v1` (kind=organ, status=BUILT, gate=WIRE_CANDIDATE, integration=ISLAND).
- NOT YET WIRED into any consumer (the entropy-as-shared-difficulty-currency wiring into N400/write-gating/
  route-conflict/predictive-reader is the composition step §2 of the PLAN). Keep attachment + role binding SEPARATE.
- Commit: 5ced07b69 (strategy: land graded_competition organ -- consolidation step 1).

### 2026-08-27 -- STEP 2: landed the ATL CONCEPTUAL/DEFINITIONAL meaning channel (queue row J) ✅
- **`hdlab/conceptual_meaning.py`** created -- the reader's missing SECOND meaning system (meaning-IDENTITY /
  what-a-word-IS), a glass-box STATIC asset: `ConceptualChannel.similarity(w1,pos1,w2,pos2)` = IDF-weighted
  WordNet gloss+genus definitional-feature cosine. Ported `_def_bag`/`build_global_idf`/`ConceptualChannel`/
  `_sparse_cos` VERBATIM with the headline cfg {gloss,lemmas,hyper,hyper_levels:2}. The global IDF (distinctive-
  feature weighting over ALL ~117k synsets) is an offline-built, DISK-CACHED static asset
  (`data/hdlab_conceptual_idf/global_idf.json`, 2.8 MB). **CORRECTION: the cache is gitignored (derived-data
  policy) so it is NOT committed -- the organ REBUILDS + re-caches it on first use (~30-60s, one pass over all
  synsets); rebuildable, not a committed artifact.** DEFAULT-SAFE (new module, nothing imports it yet).
- **Witness `verification/test_conceptual_meaning_organ.py`** -- self-contained construction proof over WordNet
  directly (no external gold), run FIRST-HAND, PASS: synonyms 0.834 vs unrelated 0.010 (margin +0.824);
  info-free twin (real word vs a RANDOM other word's definition) 0.011 LOSES; glass-box (no gold in signature;
  OOV -> None; cosine in [0,1]); distinctive-feature IDF op active (generic 'large' idf 3.97 < median 10.98;
  weighted != unweighted). [The off-WordNet human-gold win vs steelmanned GloVe + the double dissociation is the
  solver's test_conceptual_meaning_channel.py, re-verified at integration.]
- **Registered** `conceptual_meaning_v1` (kind=organ, status=BUILT, gate=WIRE_CANDIDATE, integration=ISLAND).
- NOT YET WIRED. Composition step: DEMAND-ROUTE (identity->conceptual, relatedness->associative; FUSE for graded
  rating; conflict-gated SELECTION -> semantic_control) + OPERATION-ROUTE by word class. Do NOT wire the
  tested-negatives (SVD distillation; task-switch gate; grounded-sensorimotor for adjectives; GPU hub over 1 spoke).
- Commit: d4bb6f76d (+ bfcc8ad13 log correction) (strategy: land conceptual_meaning organ -- consolidation step 2).

### 2026-08-27 -- STEP 3: landed the SALIENCE BINDER (ACT-R + Centering prominence; graded write) (queue row E) ✅
- **`hdlab/salience_binder.py`** created -- the pronoun-BIND half of entity tracking. `actr_activation(history,
  now)` = B = ln sum_k w(role_k)*dt_k^-decay (ACT-R base-level, Anderson & Schooler); prominence weights =
  Centering Cf-ranking (SUBJECT 4 > POSSESSIVE 2.5 > OBJECT 2 > OTHER 1). `bind` = hard argmax (the default);
  `graded_write` = Nref-faithful softmax(activation/temp), temp~2.0. **BRAIN-FOUNDATIONAL COHERENCE: `graded_write`
  REUSES `hdlab.graded_competition.softmax` (gain=1/temp) -- the SAME divisive-normalization op as the parser's
  role competition (Lewis-Vasishth cue-based retrieval IS an ACT-R model); verified byte-equal in the witness.**
  Ported `_actr_score`/`ROLE_W`/`_dt` + the graded write VERBATIM. DEFAULT-SAFE (new module, nothing imports it).
- **Witness `verification/test_salience_binder_organ.py`** -- self-contained construction proof, run FIRST-HAND,
  PASS: [1] grammatical PROMINENCE overrides RECENCY (subject-x2-older beats other-recent; the binder picks the
  prominent entity, a recency baseline picks the wrong recent one) -- the load-bearing brain claim; [2] ACT-R
  monotonicity; [3] graded_write == graded_competition.softmax (winner mass 0.551, interior optimum); [4]
  glass-box + info-free twin loses (shuffled-activation hits the prominent entity 0.273 ~ 1/4 chance; a uniform
  write carries no winner -> the ACTIVATION weighting binds, not mere hedging).
- **Registered** `salience_binder_v1` (kind=organ, status=BUILT, gate=WIRE_CANDIDATE, integration=ISLAND).
- NOT YET WIRED. Dissociation to honor at composition: BIND by salience (this organ), PREDICT by content-addressable
  retrieval (a different channel); wire the composed readout for RETRIEVAL, not as a predictive prior.
- Commit: c6726d9bf (strategy: land salience_binder organ -- consolidation step 3).

### 2026-08-27 -- STEP 4: landed the INCREMENTAL LEFT-CORNER ARGUMENT BUILDER (queue row C) ✅
- **`hdlab/incremental_parser.py`** created -- the parser's STRUCTURAL front-end done the brain's way:
  `incremental_build(toks, pos[, predictor])` reads LEFT-TO-RIGHT under a bounded Now-or-Never buffer, eager
  left-corner subject bind + eager patient fill; prediction ON (reuses predictive_reader), revision OFF (default,
  per the integration). Ports `incremental_build`/`_g`/`_cos`/`_lemma` VERBATIM. DEFAULT-SAFE (new module; with
  predictor=None the structural core runs). Keep structure-BUILDING and role-BINDING SEPARATE (Beber 2025).
- **Witness `verification/test_incremental_parser_organ.py`** -- self-contained construction proof, run FIRST-HAND,
  PASS: canonical SVO recovered {subj,obj}; LEFT-CORNER nearest-nominal subject bind (not a distant one); genuinely
  INCREMENTAL (every prefix parse's bindings subset the full parse -- no retraction, the Now-or-Never property);
  BOUNDED good-enough (<=3 args/verb, does NOT over-generate -- the precision mechanism that beats the batch parser
  +0.0352 F1); glass-box.
- **Registered** `incremental_parser_v1` (kind=organ, status=BUILT, gate=WIRE_CANDIDATE, integration=ISLAND).
- NOT YET WIRED. Composition: wire as the CANDIDATE SOURCE feeding the role assigner; route reversibles to relcl.
- Commit: see git log (strategy: land incremental_parser organ -- consolidation step 4).

## 🧠 IS THE *WIRING* BRAIN-FOUNDATIONAL, TOO? (owner check 2026-08-27 -- tracked here, enforced at the composition step)
Landing brain-faithful organs is necessary but NOT sufficient -- the COMPOSITION must be brain-faithful too. The
composition step (§2 of the PLAN) is held to these architecture principles, each PINNED, and will be VALIDATED (not
just asserted) when organs are wired:
1. **LATE ALGEBRAIC MERGE, not a feedforward cascade** (Norris/McQueen/Cutler 2000 "Merge"): parallel forward-computed
   streams merged late + bounded revision -- established by the wire-and-measure integration (NOT a cascade, NOT
   recurrence). The §2 arrows are DATA DEPENDENCIES, not a strict pipeline.
2. **TOP-DOWN prediction meets BOTTOM-UP evidence** (predictive coding; Friston): the predictive reader's expectation
   meets the incremental stream; surprisal = prediction error. Not pure feed-forward.
3. **ONE shared graded currency, reused -- not re-implemented** (already enforced): the divisive-normalization softmax
   is ONE op used by graded_competition AND salience_binder (verified byte-equal); the maintained-distribution
   ENTROPY = predictive_reader surprisal = N400 confidence is ONE difficulty signal feeding all consumers.
4. **SEPARATE POOLS stay separate -- never fuse** (the dissociations we measured): attachment vs role-binding (Beber);
   associative vs conceptual meaning (route/fuse-for-rating, do NOT fuse for identity); bind-by-salience vs
   predict-by-content (entity tracking). Fusing any of these is a fidelity regression, gated against.
5. **Discrete organs are the noise->0 argmax COLLAPSE of the graded competition** -- the discrete front-end is the
   task-triggered readout of one graded distribution, not a separate mechanism.
**Owner discipline in force: if the composed measurement surprises us, run brain-foundationality drills at finer
resolution before tuning.** The wiring's brain-foundationality is a GATE on the composition step, logged here.
