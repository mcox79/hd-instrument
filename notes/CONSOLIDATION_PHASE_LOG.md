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
| E | ACT-R salience binder + GRADED softmax write | (pending) | (pending) | (pending) | ⬜ QUEUED |
| F | entity-augment of the situation model | (pending) | (pending) | (pending) | ⬜ QUEUED |
| C | incremental left-corner builder | (pending) | (pending) | (pending) | ⬜ QUEUED |
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
- Commit: see git log (strategy: land conceptual_meaning organ -- consolidation step 2).
