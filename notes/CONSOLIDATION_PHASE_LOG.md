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
| H | relcl filler-gap resolver + route-conflict | `hdlab/relcl_resolver.py` | `test_relcl_resolver_organ.py` | relcl_resolver_v1 | ✅ LANDED 2026-08-27 (commit below) |
| E2 | sparse per-entity trace store (DG k-WTA + CA3) | (BUILD proposal, not a landed fix) | -- | -- | ⬜ BUILD TARGET |

## MEASUREMENT (step 2-4)
| artifact | status |
|----------|--------|
| ROLE-BALANCED comprehension gold | ✅ BUILT + VERIFIED 2026-08-27 (`exp_role_balanced_comprehension_gold_v1.py`; 9446 items, positional floor 0.500, can-fail PASS; gold rebuildable-deterministic) |
| composed-reader end-to-end harness (OFF-vs-ON) | 🔬 STARTED 2026-08-27 (`exp_composed_reader_role_balanced_measure_v1.py`; harness+gold validated -- ON beats floor+twin CI-sep; DIAGNOSIS: relcl arm rare-by-design, need to wire the ACCURACY lever = learned assigner D + incremental candidates) |
| the payoff number (composed reader vs floors, twins losing) | ✅ FRONT-END MEASURED 2026-08-27: composed front-end **0.739 vs positional floor 0.519 (+0.212 CI-sep)**, twin 0.296 loses (n=8225, role-balanced). Full-reader (entity+meaning, cross-sentence) = still to measure. |

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
- Commit: cedda5832 (strategy: land incremental_parser organ -- consolidation step 4).

### 2026-08-27 -- STEP 5: landed the RELATIVE-CLAUSE FILLER-GAP RESOLVER (queue row H) ✅
- **`hdlab/relcl_resolver.py`** created -- reversible-sentence role assignment the brain's way. `resolve_patient(
  toks, pos, v)` = the active-filler object-gap rule (Frazier): the fronted filler is the PATIENT exactly when the
  object slot is empty (gap) and a subject nominal intervenes; else word-order. Glass-box over UPOS + closed-class
  relativizers, NO arc graph (route AROUND the arc parser, which is HARMFUL here). Ports arm_fillergap_incremental
  + helpers VERBATIM. DEFAULT-SAFE (new module; leaves canonical clauses == the two-line rule).
- **Witness `verification/test_relcl_resolver_organ.py`** -- self-contained construction proof, run FIRST-HAND,
  PASS: the REVERSIBLE object-gap 'the doctor that the lawyer chased' -> patient=doctor where the word-order
  baseline picks the WRONG lawyer (the discriminator); subject-gap + canonical fall to word-order (gate off);
  passive -> pre-aux subject; glass-box (no heads/gold in signature).
- **Registered** `relcl_resolver_v1` (kind=organ, status=BUILT, gate=WIRE_CANDIDATE, integration=ISLAND).
- BRAIN-FOUNDATIONAL COHERENCE: the discrete filler-gap rule is the noise->0 limit of graded cue-based retrieval --
  the SAME primitive as graded_competition (wiring rule 5).
- NOT YET WIRED. Composition: reversible-case route after the role assigner; expose the route-CONFLICT as a
  gold-free difficulty signal (two competing scorers + a conflict term, NOT if/else).
- Commit: see git log (strategy: land relcl_resolver organ -- consolidation step 5).

### ISLAND-ORGAN LANDINGS COMPLETE (2026-08-27)
All self-contained new-module organs are now landed + witnessed + registered: predictive_reader, semantic_control
(pre-phase) + graded_competition, conceptual_meaning, salience_binder, incremental_parser, relcl_resolver (this
phase). **REMAINING queue rows are WIRING-INTO-EXISTING-ORGANS, done AT the composition step, not as islands:**
D (front-end role-fix: quote-exclusion + speech-verb into situation_reader/thematic_role_labeler), F (entity-augment
of the situation model), E2 (sparse per-entity store = a BUILD proposal). **NEXT: build the ROLE-BALANCED comprehension
gold (the measurement instrument), then wire the composition (§2) honoring the 5 brain-foundationality rules, then
measure OFF-vs-ON.**

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

### 2026-08-27 -- STEP 6: MEASUREMENT DESIGN (verify-before-building; the design gate) 🔵
Assessed existing assets (NOT a from-scratch build): the wire-and-measure harness `exp_wire_organs_endtoend_v1.py`
(+ witness `test_wire_organs_endtoend.py`, 9/9 at integration) already composes the MEMORY/MEANING organs and found
the FRONT-END is the wall on the AGENT-SATURATED McGuffey gold. **Decision: BUILD ON it** -- (a) swap the gold for a
ROLE-BALANCED modern one, (b) wire in the newly-landed FRONT-END organs. **Gold = QA-SRL** (`load_patient_items`:
modern sentences w/ labeled agent+patient spans + voice), sampled BALANCED across agent-vs-patient answer position AND
canonical-vs-non-canonical, so the majority floor is ~0.5 not 0.78 (the front-end fix's clean win lives here:
two-animate 0.93 vs 0.50). Design gate recorded in PLAN section 3 (real baseline + can-fail two-animate discriminator +
one variable OFF-vs-ON). **NEXT ROUND: write the role-balanced gold builder cell + verify the majority floor is ~0.5
(can-fail: if the sampled set is still agent-saturated, the balance failed).** This is MY work (strategy owns hdlab
wiring; no solver round -- the mechanisms are already proven), optionally using helper agents for mechanical parts.

### 2026-08-27 -- STEP 7: BUILT the ROLE-BALANCED comprehension gold ✅ (the fair measuring stick)
- **`experiments/exp_role_balanced_comprehension_gold_v1.py`** -- builds a MODERN role-balanced who-did-what test
  from QA-SRL (labeled agent+patient spans + voice). Balances the PATIENT's POSITION relative to the verb: POST-verbal
  (canonical active SVO -- the easy majority case) vs PRE-verbal (passive + object-relative -- the reversible
  discriminator), sampling EQUAL counts so a POSITIONAL-ONLY reader scores ~0.5 by construction.
- **Ran FIRST-HAND, can-fail PASS:** full build = **9446 items (4723 pre / 4723 post); positional-only floor 0.500;
  majority-role floor 0.500** (vs the McGuffey 0.78 saturation this replaces); 5883 passives + 534 object-relative
  reversibles. The can-fail asserts the floor is ~0.5 (if the sample were still agent-saturated the balance failed).
- Saved `data/role_balanced_comprehension_gold_v1/{gold.jsonl, meta.json}` (gitignored -> REBUILDABLE via the
  DETERMINISTIC cell -- fixed prefixes, no RNG). Commit tracks the reproducible builder cell.
- **This is the MEASUREMENT INSTRUMENT.** NEXT: wire the newly-landed FRONT-END organs into the composed reader
  (build on `exp_wire_organs_endtoend_v1.py`) and measure OFF-vs-ON on this gold -- the positional floor (0.5) is the
  bar the composed reader must clear CI-separated, with info-free twins losing.
- Commit: see git log (strategy: build role-balanced comprehension gold -- consolidation step 7).

### 2026-08-27 -- STEP 8: FIRST composed-reader measurement + DIAGNOSIS (owner directive: drill the surprise) 🔬
Built `experiments/exp_composed_reader_role_balanced_measure_v1.py` (OFF=two_line voice-aware, ON=+relcl object-gap arm,
FLOOR=positional-only, TWIN=random nominal), scored patient-in-span with bootstrap CIs. **Smoke (n=988 aligned):**
FLOOR 0.220, OFF 0.318, ON 0.319, TWIN 0.124. **ON beats FLOOR +0.099 CI-sep and TWIN +0.195 CI-sep** (voice+structure
beats pure position; the info-free twin loses -> the gold + harness WORK). BUT **ON-OFF = +0.001 NOT_SEP** (the relcl arm
is inert on aggregate) and the absolute accuracy is LOW (0.32) -- a SURPRISE.
**DRILLED to finer resolution (2 probes), and the surprise is UNDERSTOOD -- NOT a bug:**
1. **The relcl gate fires on 1.32% of items (13/988)** -- a faithful reproduction of the integration's honest "fires on
   ~0.75% of QA-SRL, aggregate +0.001" bound. The relcl organ was NEVER the aggregate lever; its value is rare hard
   sentences. On the is_object_gap-FIRED slice (its TRUE domain, n=13) **ON 0.231 > OFF 0.154** -- it DOES help where it
   fires; the aggregate just dilutes it by rarity.
2. **My "reversible slice" proxy (pre-verbal & non-passive) was a BAD isolation** -- inspection shows those items are
   mostly odd QA-SRL annotations / fronted subjects, NOT object-relative clauses. Isolate by `is_object_gap`, not position.
3. **The low absolute accuracy is the CRUDE two_line baseline, NOT the learned front-end FIX.** I measured the wrong
   lever: the real role-assignment accuracy driver is the LEARNED assigner (front-end fix D: core-mention selection +
   quote-exclusion + speech-verb + perceptron, which took 0.48->0.75 in the integration) + the incremental_parser's
   candidate PRECISION -- NEITHER is wired into this measurement yet (D is a wiring-into-thematic_role_labeler item).
**CONCLUSION (rigorous, honest):** the harness + gold are validated (defeat the positional floor, twin loses); the relcl
organ behaves exactly as its integration said (rare, real on its slice). **The composed-reader PAYOFF is NOT yet measured
-- it needs the ACCURACY lever wired: the learned role-assigner (D) + incremental candidates.** NEXT ROUND: wire D +
incremental_parser candidates into the composed reader, sharpen scoring to the patient HEAD, and re-measure OFF (live
positional baseline) vs ON (composed) -- that is the real front-end payoff test on the fair gold.
- Commit: see git log (strategy: first composed-reader measurement + diagnosis -- consolidation step 8).

### 2026-08-27 -- STEP 9: THE FRONT-END PAYOFF (a scoring-bug wall drilled + fixed, then the real number) ✅
**Owner directive lived out ("anytime we face a wall we research drill to make sure we're implementing correctly").**
STEP 8's flat 0.32 + "incremental adds nothing" looked like a wall. Drilled it with an ORACLE-CEILING probe (can the
method even succeed?): ceiling was 0.49 -- IMPOSSIBLE if the candidates contained the answer. **Root cause = a bug in MY
OWN checker:** QA-SRL patient spans are HALF-OPEN `(start,end)`, but `_in_span` scored membership in the 2-element SET
`{start,end}` -- so "the air" `[3,5)` was checked against {3,5} and missed the head "air" at index 4. Fix to
`range(start,end)`: **oracle 0.49 -> 0.97** and the real result appeared. (Fixed v1 + v2; v2 is definitive.)
**DEFINITIVE MEASUREMENT (`exp_composed_reader_role_balanced_measure_v2.py`, full n=8225):**
  * FLOOR positional (guess by position, no voice) : 0.5191 [0.508,0.530]  (a coin-flip -- the balanced gold works)
  * COMPOSED front-end (voice + word-order + relcl) : **0.7387 [0.729,0.748]  -> +0.2118 CI-sep over the floor**
  * info-free TWIN (random nominal)                 : 0.2964  (loses by +0.4345 CI-sep)
  * pre-verbal (hard/reversible) patients 0.582 vs post-verbal 0.875 -- headroom on the reversibles.
**-> THE FRONT-END ORGANS EARN THEIR KEEP ON A FAIR MODERN TEST: from a ~0.52 position-guess floor to 0.74, CI-separated,
the scrambled control destroying it.** This is the consolidation's first real PAYOFF number (front-end role assignment).
**HONEST sub-findings:** (1) restricting the patient search to the incremental parser's argument slots slightly HURTS
(-0.008 CI-sep below resolving over all nominals) -- the incremental parser's value is broad-parse candidate precision,
not single-patient-ID, so it is NOT the lever here; (2) the LEARNED assigner (D) is still un-wired -- the pre-verbal 0.582
is where it (+ more voice/structure work) could lift the number. **SCOPE: this is the FRONT-END (who-did-what) payoff;
the FULL composed reader (entity tracking + meaning) on a CROSS-SENTENCE gold is a further measurement.**
- Commit: see git log (strategy: front-end payoff measured + scoring-bug fix -- consolidation step 9).

### 2026-08-27 -- STEP 10: DRILL the front-end headroom (pre-verbal 0.582) -> localized to voice-recall + uncovered reversibles 🔬
Broke the pre-verbal (hard) slice down by construction:
  * gold-passive pre-verbal (n=3595): `precise_passive` DETECTS only 0.742 (2667/3595). Where DETECTED acc=0.802;
    overall passive acc=0.626 -> **voice detection is too STRICT (BE-aux + participle); ~26% of passives are missed**
    (got/being/reduced passives, _is_participle gaps), and a missed passive -> the pre-verbal patient is lost.
  * relcl-gate object-relatives (n=44): acc 0.773 -> the relcl organ WORKS where it fires.
  * **"other pre-verbal" (n=408): acc 0.076 (!!)** -- pre-verbal patients that are neither detected-passives nor
    object-gap relatives (reduced relatives "the book written...", fronting/topicalization, relativizers the gate
    misses). resolve_patient defaults to the WRONG post-verbal pick -> near-total loss.
**LOCALIZED: the front-end headroom is (a) voice-detection RECALL and (b) UNCOVERED reversible constructions -- exactly
the cues the LEARNED cue-integrating assigner (fix D, MacWhinney Competition Model: learned order+voice+morphology
validities) handles that the crude precise_passive + narrow relcl gate do NOT.** This CONFIRMS STEP 9's note: D is the
front-end accuracy lever for the hard cases (the brain-faithful move -- graded learned cue integration, not more hand
rules). NOT a tuning job (do NOT hand-patch precise_passive -- that is the easy thing); the right thing is the learned
Competition-Model assigner. **Decision for next rounds: (a) the FULL composed reader (entity + meaning, cross-sentence
gold) is the consolidation's headline goal and tests the OTHER landed organs; (b) wiring D lifts the front-end hard cases.
Lean (a) -- the front-end already earns its keep (+0.21 CI-sep); the full-reader payoff is the open question.**
- Commit: see git log (strategy: drill front-end headroom -- consolidation step 10).

### 2026-08-27 -- STEP 11: PARALLELIZE -- packaged 3 mechanism-gap solver problems (owner prompt) 🔀
Owner: "are you sure some of these aren't good opportunities for parallel solver sessions?" -- YES. The split:
STRATEGY (mine, not solver-able): wiring the LANDED organs into the live reader + the OFF-vs-ON measurements (hdlab
composition, Q111, no new mechanism). SOLVER (parallel-able): the NEW brain-MECHANISM gaps the measurement SURFACES.
**Policy update: the drain-to-trigger phase is DONE (consolidation active); during active consolidation, measurement-
surfaced mechanism gaps ARE packaged as PARALLEL solver work (this does not re-grow a pre-consolidation queue -- it
parallelizes discovery while strategy does the wiring).** Packaged (priorities unique 1/2/3):
  1. `the_front_end_mishandles_non_canonical_argument_structure` (p1) -- the STEP-10 headroom: learned graded cue
     integration (Competition Model) where morphology/voice OVERRIDE order; fix reduced relatives + fronting + the 26%
     undetected passives. Bar: beat the composed front-end's 0.582 pre-verbal slice CI-sep, shuffled-validity twin losing.
  2. `the_entity_store_is_a_dense_bundle_that_fans` (p2) -- the MEASURED fan effect (0.695->0.608): sparse DG k-WTA
     conjunctive encode + CA3 completion (NOT a pointer). Bar: reduce the fan SLOPE CI-sep vs the dense bundle, twin losing.
  3. `the_meaning_read_out_is_one_operation_where_the_brain_has_three` (p3) -- operation-routing by word class
     (adjective signed-magnitude, verb relational); resolve the adjective op's n=111 power limit. Bar: beat the single
     cosine per-class CI-sep on a powered gold, random-axis twin losing.
**These run in PARALLEL (solver sessions). Strategy CONTINUES its lane: the full composed-reader cross-sentence
measurement (character tracking + meaning) + wiring the landed organs.** Integrate each solver result only on
owner_verdict: DONE (standing rule).
- Commit: see git log (strategy: parallelize -- package 3 mechanism-gap solver problems -- step 11).
