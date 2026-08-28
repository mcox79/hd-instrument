# CONSOLIDATION PHASE -- RUNNING LOG (compaction-survival; append-only, newest step at the BOTTOM of each section)

**Purpose (owner 2026-08-27): keep a CLEAR running log so if this work extends beyond a compaction we keep all
the context.** This is the durable ledger of the consolidation phase: what has been landed/built/measured, with
commit hashes and verification, so a fresh session can resume mid-phase without re-deriving anything.

**READ THIS + `notes/CONSOLIDATION_PHASE_PLAN.md` (the ordered plan) + `notes/STATUS.md` (LATEST position) to resume.**

## ✅ RESUME STATE — UPDATED 2026-08-28 (the CONSOLIDATION PHASE IS COMPLETE; we are in the NEXT PHASE — read `notes/STATUS.md` for the LIVE authority, injected every session)
**The full-substrate consolidation is DONE.** `notes/STATUS.md` is the current authoritative recovery entry point (this block
is the durable consolidation-phase ledger tail). Do NOT re-derive; the disk + `git log` outrank the chat summary.

**CONSOLIDATION COMPLETE — everything landed + witnessed + registered (default-off islands):**
- **Reader organs:** `predictive_reader`, `semantic_control`, `graded_competition`, `conceptual_meaning`, `salience_binder`,
  `incremental_parser`, `relcl_resolver`, `graded_role_assigner`, `situation_register_setreturn` (decode_set).
- **Composition mechanisms VALIDATED:** the ENTITY×MEANING axes COMPOSE (STEP 18); the brain-faithful combination rule is
  CONVERGENT-CUE (log-Bayes product) not an independent AND → `hdlab/convergent_cue_reader.py` LANDED (beats the strongest
  floor 0.700→0.744 CI-sep, integrated p3).
- **The 3 parallel-solver trilogy + downstream ALL INTEGRATED (owner-DONE, EXCELLENT):** front-end non-canonical
  (`graded_role_assigner`), entity-store fan (ADDRESSING-collision, not blur → `decode_set` set-return LANDED; the factorized
  two-system store is a proven-ready follow-on), meaning-operation-routing, convergent-cue composition.

**NEWEST (2026-08-28) — stranded solutions integrated + p1 fully landed + NEXT PHASE framed (see STATUS for detail):**
- **THEORY OF MIND integrated (EXCELLENT):** `hdlab/belief_partition.py` LANDED (per-agent false-belief, 1.000 on real-English
  passages). Residual = the observation-cue front-end. Owner MUSED a dedicated re-eval solver (corpus-mined gold + the
  observation front-end) — package as a follow-on.
- **p1 SCALAR-MAGNITUDE RULER fully LANDED:** `hdlab/fractional_power_encoding.py` (log-Weber code) + `hdlab/scalar_adjective_operation.py`
  (the ruler) + `hdlab/meaning_operation_router.py` (word-class routing) — all witnessed + registered. → the learner's
  substrate-validation dependency is SATISFIED. Follow-on refinements (NOT blocking): `quality_relation` Ch.B linear→FPE-log
  (regrounding the lexicon) + wire dim-select to `semantic_control`.
- **NEXT PHASE = comprehension → REASONING** (p1's comparison is the first glass-box reasoning primitive; the meaning system
  is now multi-operation + demand-routed). **Learn-from-reading is PROVEN-worth-continuing but OFF** — being optimized +
  safety-validated as a solver problem BEFORE it grows the foundation (owner: validate hard first).

**IN FLIGHT (solvers; integrate ONLY on `owner_verdict: DONE`):** `optimize_and_validate_the_learner_before_it_grows_the_foundation`
(p2), `the_reader_cannot_choose_what_to_read_next` (p3 foraging), `dimensional_phase_diagram_audit_of_the_current_organs`
(p4, STILL RUNNING — has a SOLVED.md but the owner is iterating; leave alone).

**STRATEGY-OWNED REMAINING (mine, Q111):** the 2 p1 follow-on refinements; the factorized two-system store landing (heavy →
remote); the N400 PE event-segmentation wiring; the FULL 3-axis end-to-end measurement (heavy → remote); package the ToM
dedicated re-eval solver.

**STANDING DISCIPLINE:** integrate ONLY on `owner_verdict: DONE`; every landing default-off + witnessed + registered; commit
NO push; do the RIGHT thing not the easy one; heavy/long runs → the REMOTE GPU box; at a wall/surprise run brain-foundationality
drills BEFORE tuning; use problems for large builds.


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
| the payoff number (composed reader vs floors, twins losing) | ✅ FRONT-END MEASURED 2026-08-27: composed front-end **0.739 vs positional floor 0.519 (+0.212 CI-sep)**, twin 0.296 loses (n=8225, role-balanced). ✅ **+graded_role_assigner WIRED (STEP 17, held-out n=4078): 0.739->0.751 (+0.011 CI-sep), hard pre-verbal 0.576->0.600, canonical preserved.** Full-reader (entity+meaning, cross-sentence) = still to measure (action #3). |

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

### 2026-08-27 -- STEP 12: LANDING-VERIFICATION -- every landed organ reproduces its validated payoff ✅ (WIRE-DON'T-ISLAND)
While the 3 mechanism-gap solvers run in PARALLEL, strategy verified the ENTITY half of the composed reader composes
end-to-end: **`hdlab/salience_binder.actr_activation` == the harness `_actr_score` BYTE-FOR-BYTE** (ROLE_PROMINENCE ==
ROLE_W, decay 2.0) -> the entity-tracking integration's validated CROSS-SENTENCE payoff (ACT-R salience 0.174 vs
string-identity 0.059, +0.115 CI-sep, shuffled twin losing) TRANSFERS EXACTLY to the landed organ (stronger than a
re-run: the landed organ IS the validated binder). **Consolidated landing-verification (all 6 organs):**
  * FRONT-END (relcl_resolver + incremental_parser + voice): MEASURED end-to-end on the fair gold -- composed 0.739 vs
    positional floor 0.519 (+0.212 CI-sep), twin losing (STEP 9).
  * ENTITY (salience_binder): byte-reproduces the validated +0.115 cross-sentence payoff (this step).
  * graded_competition / conceptual_meaning / predictive_reader / semantic_control: each self-contained construction-
    proof witness PASS (STEPS 1-5 + pre-phase), reproducing the validated mechanism (entropy>binary-conflict; synonyms
    >>unrelated + twin loses; predictive surprisal>reactive; conflict-trigger AUC).
-> **THE LANDING PHASE IS VERIFIED-COMPOSING: all 6 organs are default-off islands that each reproduce their proven
result.** **THE ONE REMAINING DECISIVE TEST = the FULL composition end-to-end (front-end -> entity -> retrieval ->
meaning -> answer on a CROSS-SENTENCE gold), which the wire-and-measure showed was FRONT-END-gated.** With the front-end
now clearing the fair floor, re-running it is the payoff -- BUT the front-end solver (p1) is improving the front-end in
parallel, so this end-to-end test is best run either (a) as a BASELINE with the current landed front-end now, or (b) after
p1 lands (avoids a moving target). Leaning (b) to avoid double-measuring; meanwhile prep the full-composition harness.
- Commit: see git log (strategy: landing-verification -- all organs reproduce payoffs -- step 12).

### 2026-08-27 -- STEP 13: FULL-COMPOSITION harness built + IN-PIPELINE integration test PASS ✅ (character-tracking half)
Built `experiments/exp_composed_reader_litbank_full_v1.py` -- runs the LANDED `hdlab/salience_binder` INSIDE the
end-to-end reader (front-end mention stream -> entity binding -> the REAL situation-model register decode) on LitBank,
not just as a unit. This is the full-composition harness; the `annotate`/mention-stream step is the PLUGGABLE FRONT-END
SEAM the improved front-end (solver p1) slots into (one-line swap, no rebuild). **IN-PIPELINE RESULT (60 docs, 5469
pronoun queries):** ACT-R salience (landed organ) **0.1836 [0.154,0.213]** vs STRING_IDENTITY 0.0578 (**+0.1258 CI-sep**)
vs SHUFFLED_TWIN 0.1015 (ACT-R **+0.0821 CI-sep**). Reproduces the integration's cross-sentence payoff (0.174 vs 0.059
+0.115; twin +0.073) IN-PIPELINE -> **the character-tracking half of the full reader COMPOSES end-to-end with the landed
organ.** **STATE:** front-end payoff MEASURED (0.739 vs 0.519, STEP 9); entity/character-tracking payoff MEASURED
in-pipeline (this step); the two halves are validated. **REMAINING for the FULL end-to-end (front-end -> entity ->
retrieval -> meaning on ONE cross-sentence gold): swap p1's improved front-end into the SEAM + add the meaning channel;
best run when p1 lands (avoids the moving target). The harness is READY.**
- Commit: see git log (strategy: full-composition harness + in-pipeline integration test -- step 13).

### 2026-08-27 -- STEP 14: MEANING axis earns its keep in comprehension (recognise-not-recite) ✅
Built `experiments/exp_meaning_channel_paraphrase_comprehension_v1.py`: answer a PARAPHRASED who-did-what question
("what did X PURSUE?" when the story said "chased") on LitBank, retrieving the event among the doc's ~100 candidate
verbs. **Result (n=5939 paraphrase items):** OFF exact-match **0.0000** (structurally fails on paraphrase, by
construction) | ON conceptual_meaning **0.7500 [0.739,0.762]** | TWIN random **0.0101**. ON - OFF +0.75 CI-sep;
ON - TWIN +0.74 CI-sep. **-> the landed conceptual channel RECOVERS who-did-what under paraphrase (recognise-not-recite)
where exact word-matching cannot; the info-free twin loses.** **HONEST CAVEAT: the paraphrases are WordNet synonyms and
the channel is WordNet-based -> mild in-domain circularity (the channel recognising its own source's synonymy). A fully
independent test needs NON-WordNet paraphrases (PPDB / a human paraphrase set) -- the meaning-op-routing solver (p3) +
a follow-on cover this; here it is a legitimate demonstration of the channel's paraphrase-recovery FUNCTION, so caveated.**
**CONSOLIDATION STATE -- ALL THREE ORGAN AXES individually earn their keep in comprehension:** FRONT-END 0.739 vs 0.519
(STEP 9); ENTITY/character-tracking 0.184 vs 0.058 in-pipeline (STEP 13); MEANING 0.750 vs 0.010 paraphrase (this step);
each with its info-free twin LOSING. The FULL end-to-end (all three composed on ONE cross-sentence gold + p1's improved
front-end) is the remaining decisive test, ready to fire when p1 lands (harness STEP 13; seam + meaning channel wired).
- Commit: see git log (strategy: meaning axis earns its keep in comprehension -- step 14).

### 2026-08-27 -- STEP 15: INTEGRATED p1 (front-end non-canonical fix, owner-DONE, EXCELLENT) ✅
Re-verified FIRST-HAND (`test_noncanonical_role_assigner.py` 6/6 PASS, held-out n=4078). A HYBRID graded cue-competition
assigner (Competition Model over the landed `graded_competition`) beats the front-end on the non-canonical slice
**0.6000 vs 0.5758 (+0.0242 CI-sep)**, net-positive overall (+0.0113 CI-sep), canonical preserved, twin losing, seed-robust.
FLAT-integrator net-negative -> the faithful method ROUTES (word-order dominant, override only on marked cues). Deep drills:
verb-subcat SUPPLY bound broken with WordNet frames; the residual is ARCHITECTURE (incremental parsing + reanalysis)
bottlenecked by meaning-rep quality + coref + parser -> routes to EXISTING lines, not more cues. Solver withdrew its own
7pt coref overclaim (anti-gaming twin). review EXCELLENT + SOLVER REVIEW; priority cleared; AUDIT UPDATE folded (§2b);
STATUS updated. **NO hdlab landed; EARNED proven-ready: `graded_role_assigner` HYBRID route (default-off).**
**NEXT: (a) land `graded_role_assigner` as a focused build; (b) swap it into the full-reader harness SEAM
(`exp_composed_reader_litbank_full_v1.py`) + run the FULL whole-reader measurement with the improved front-end -- the
consolidation payoff.** p2 (entity store) + p3 (meaning op-routing) submitted, await owner_verdict: DONE.
- Commit: see git log (strategy: integrate p1 front-end non-canonical fix -- step 15).

### 2026-08-27 -- STEP 16: LANDED graded_role_assigner (the p1 earned front-end wiring) ✅
`hdlab/graded_role_assigner.py` -- the Competition-Model non-canonical patient route. `hybrid_role_patient` keeps
resolve_patient BYTE-IDENTICAL on canonical/confident routes; invokes a graded cue competition (learned validities over
`graded_competition`) ONLY on the marked non-canonical fall-through (strong passive / relativizer-less object gap /
unaccusative). Ported voice_cues/gap_config/cue_supports/competition_pick/hybrid_pick VERBATIM; the offline-fit validities
baked as DEFAULT_VALIDITIES (fit by logistic on the role-balanced train split, seed 20260827; passive_weak -2.99 = the -ed
garden-path distrusted). Witness `test_graded_role_assigner_organ.py` PASS first-hand: reduced object-relatives 4/4 vs
resolve_patient 0/4; canonical byte-identical (routing not replacement); shuffled-validity twin 1/4 loses; passive_weak<0.
Registered `graded_role_assigner_v1` (BUILT/ISLAND, default-safe). NOT yet wired into resolve_patient (a flagged wiring +
live measure is the composition step). NEXT: land `scalar_adjective_operation` (the p3 earned organ).
- Commit: see git log (strategy: land graded_role_assigner organ -- step 16).

### 2026-08-27 -- STEP 17: WIRED graded_role_assigner into the composed front-end + measured OFF-vs-ON (leak-free) ✅
The composition-step confirmation for the p1 earned organ (IMMEDIATE-NEXT-ACTION #2). Built
`experiments/exp_wire_graded_assigner_measure_v1.py` -- drives the LANDED organ's baked `DEFAULT_VALIDITIES` (the static
asset, not the solver's fresh fit) over the composed front-end's candidate set, on the ROLE-BALANCED gold's HELD-OUT test
split (sentence-level, rng(20260827), first half = test -- the validities were fit on the COMPLEMENT, so LEAK-FREE).
ONE variable OFF->ON = `resolve_patient` (discrete voice+relcl) vs `hybrid_role_patient` (+graded Competition-Model route
on the non-canonical fall-through). **RESULT (held-out n=4078):**
  * PRE-verbal hard/reversible slice (n=1980): OFF 0.5758 -> **ON 0.6000 (+0.0242 CI-sep, paired [+0.0146,+0.0333])**
  * OVERALL (n=4078):                            OFF 0.7393 -> **ON 0.7506 (+0.0113 CI-sep, paired [+0.0066,+0.0157])**
  * POST-verbal canonical (n=2098):              OFF 0.8937 -> ON 0.8928 (-0.0010 NOT_SEP -- **canonical PRESERVED**)
  * info-free shuffled-validity TWIN loses on the PRE slice (+0.0121 CI-sep) -> the LEARNED validities carry it.
**-> the LANDED graded_role_assigner reproduces the solver's held-out lift EXACTLY (0.6000 vs 0.5758 pre; +0.0113 overall)
when wired in a strategy-owned harness -- the baked static organ delivers, not just the in-test fit.** HONEST: the
magnitude is MODEST (+0.011 overall) as the solver flagged; the value is the hard non-canonical slice + canonical
untouched (routing not replacement), not a large aggregate swing. This is a landing-VERIFICATION (reproduces an
already-validated result in-pipeline), not a new discovery. **NEXT (action #3, the consolidation HEADLINE): the FULL
whole-reader end-to-end (front-end -> entity -> meaning on ONE cross-sentence gold) with this improved front-end swapped
into the `exp_composed_reader_litbank_full_v1.py` SEAM + the meaning channel added.** The front-end moving-target gate
(p1 landed) is now cleared, so the decisive test is unblocked.
- Commit: see git log (strategy: wire graded_role_assigner + measure OFF-vs-ON -- step 17).

### 2026-08-27 -- STEP 18: THE ENTITY x MEANING axes COMPOSE end-to-end (headline part 1) ✅
Built `experiments/exp_composed_reader_entity_meaning_paraphrase_v1.py` -- the first measurement that COMPOSES two
landed organs on ONE cross-sentence task instead of validating each on its own gold. Task: answer a PARAPHRASED
who-did-what about a PRONOUN-LINKED entity on LitBank -- correct requires BOTH the entity binding (landed
`salience_binder`) AND the meaning match (landed `conceptual_meaning`): `ok = (pred_verb==v) AND (argmax_c sim(q,c)==v)`.
**RESULT (60 docs, n=3681 pronoun queries):**
  * single-axis context: meaning-solo 0.6998, entity-solo(ACT-R) 0.1668
  * FULL (entity + meaning)                : **0.1190 [0.0976,0.1424]**
  * ENTITY_OFF (string-identity + meaning) : 0.0337  -> the ENTITY axis is worth **+0.0853 CI-sep**
  * MEANING_OFF (entity + exact decode)    : 0.0000  -> the MEANING axis is worth **+0.1190 CI-sep** (exact fails on paraphrase)
  * TWIN (shuffled binding + meaning)      : 0.0660  -> FULL beats it **+0.0530 CI-sep** (info-free binding loses)
**-> BOTH organs are LOAD-BEARING in the SAME reader; neither is inert.** `FULL 0.119 ~= meaning-solo 0.700 x
entity-solo 0.167 (=0.117)` -> the two axes compose ~INDEPENDENTLY (each a necessary factor; a strict conjunction).
This is genuinely NEW (STEP-13 = entity only/exact-match; STEP-14 = meaning only/not-entity-tracked; this = both composed).
**HONEST DEFLATIONS (reported against self):** (1) the ABSOLUTE FULL (0.119) is LOW -- expected for a strict conjunction
of two moderate independent capabilities on the HARDEST (pronoun-contributed, paraphrased) subset; the point is
axis-necessity, not the absolute. (2) entity-solo 0.167 is the STEP-13 register-decode ceiling -- the SAME dense
entity store `p2` (sparse DG+CA3) is refining, so entity-solo (and FULL) has KNOWN headroom p2 targets; this is a
BASELINE, one-swap when p2 lands. (3) meaning-solo 0.700 keeps STEP-14's mild WordNet-circularity caveat (WordNet
paraphrases scored by a WordNet channel) -- a non-WordNet paraphrase set is the clean follow-on. **CONSOLIDATION STATE:
front-end axis DONE (landed+wired, STEP 17); entity+meaning now shown to COMPOSE (this step). The FULL 3-axis end-to-end
(add the front-end role assigner to a gold that ALSO has non-canonical structure) + the p2/scalar-refined re-run remain.**
- Commit: see git log (strategy: entity x meaning compose end-to-end -- consolidation step 18).

### 2026-08-27 -- STEP 19: BRAIN-FOUNDATIONALITY DRILL on the COMPOSITION (owner check "ensure brain foundational") 🧠
Ran the finer-resolution fidelity drill the owner asks for on the STEP-18 WIRING itself (not the organs -- those are
each landed brain-faithful: salience_binder = ACT-R base-level + Centering; conceptual_meaning = ATL amodal hub).
**THREE fidelity levels, checked as a neuroscientist:**
1. **Are the two SYSTEMS separate in the brain? YES -- PINNED by a canonical DOUBLE DISSOCIATION.** Semantic dementia
   (bilateral ATL atrophy) degrades conceptual identity (cannot recognise pursue==chase) but SPARES episodic/relational
   binding; hippocampal amnesia spares semantics but destroys relational who-did-what binding. -> keeping entity and
   meaning as SEPARATE POOLS (wiring rule 4) is EVIDENCE-PINNED, not our invention. **The STEP-18 composition RESPECTS
   this** (two separate readouts; MEANING_OFF and ENTITY_OFF each degrade independently) -> FAITHFUL. ✅
2. **Is the COMBINATION RULE (my strict independent AND) brain-faithful? PARTIALLY -- and this is the fidelity GAP.**
   The AND is defensible as a LATE MERGE of two parallel streams at the DECISION (Norris/McQueen/Cutler "Merge", wiring
   rule 1). BUT for the RETRIEVAL step specifically it is NOT the deepest-fidelity mechanism: episodic retrieval is
   CONVERGENT-CUE PATTERN COMPLETION (CLS / hippocampal) -- the meaning cue ("pursue") and the entity cue (X) should
   JOINTLY address the content-addressable situation register, with meaning providing TOP-DOWN SUPPORT to the
   hippocampal read (predictive-coding facilitation). My AND treats the two retrievals as INDEPENDENT and combines them
   post-hoc -> it FORBIDS the top-down semantic facilitation the brain uses, so it likely UNDER-estimates the composed
   capability. This is exactly the "content-addressable retrieval convergence" the entity-tracking integration flagged 4x.
3. **Do the organs stay faithful IN the composition? YES** -- used unchanged; no fidelity regression introduced by wiring.
**DRILL VERDICT:** the STEP-18 composition is a VALID DISSOCIATION and late-merge-consistent (faithful for the DECISION),
but the brain-faithful RETRIEVAL mechanism is CONVERGENT-CUE (meaning ⊗ entity jointly addressing the store, top-down
support), NOT an independent AND. **Testable brain-foundational prediction: convergent-cue retrieval BEATS the STEP-18
independent-AND baseline (0.119) -- recovering entity-solo MISSES via semantic facilitation -- WHILE preserving the double
dissociation (a fused-into-one-pool control must LOSE the dissociation and is refuted as a fidelity regression).**
**-> This is a SIGNIFICANT NEW MECHANISM (how two dissociable systems COMBINE at read), measurement-surfaced, with a
baseline to beat -> HANDED OFF as a solver problem (owner 08-27: "handoff significant problems to the solvers"):
`compose_the_reader_by_convergent_cue_not_independent_conjunction` (priority 3). AUDIT UPDATE folded (§2b).** STEP-18's
result STANDS (both axes load-bearing); this drill defines the next fidelity step, it does not retract anything.
- Commit: see git log (strategy: brain-foundationality drill + package convergent-cue handoff -- step 19).

### 2026-08-28 -- STEP 20: DESIGN GATE for the FULL 3-AXIS END-TO-END (the comprehension baseline; heavy → remote) 🔵
The consolidation's remaining HEADLINE + the baseline the REASONING phase builds on. All axes are now landed (front-end
graded_role_assigner + incremental_parser + relcl_resolver; entity salience_binder + set-return decode; meaning
conceptual_meaning + scalar_adjective_operation + meaning_operation_router + convergent_cue_reader). This step SPECIFIES
the decisive measurement before the heavy build (DESIGN GATE before FULL). **It re-runs the original 2026-08-26
wire-and-measure question — "does the composed reader work end-to-end, or does the front-end swamp it?" — now that the
front-end is FIXED.** Robust to the in-flight solvers (learner/foraging/ToM/phase-diagram change NONE of the 3 axes).

**GOLD:** LitBank paraphrased pronoun who-did-what (the STEP-18 / convergent-cue task already exercises ENTITY+MEANING;
this ADDS the front-end axis). Question form: "what did [pronoun-linked entity E] [paraphrase q of the true verb v]?".

**THE THREE AXES + how they compose (the probe surfaced the key design point):**
  1. FRONT-END = correct AGENT/PATIENT attribution of each verb to entities. The LitBank stream currently attributes via
     spaCy dep (gov_verb + role_class) — the ORACLE-ish parse. The landed front-end REFINES non-canonical attribution
     (graded_role_assigner over the marked fall-through). ONE-VARIABLE OFF→ON on this axis = spaCy attribution vs
     landed-front-end-refined attribution. (Design note: the convergent-cue harness reads `m["gov_verb"]` directly; add a
     front-end SEAM there so the event's entity-attribution can be swapped oracle vs landed.)
  2. ENTITY = bind pronouns to entities (salience_binder) + register decode (set-return); vs string-identity floor.
  3. MEANING = match the paraphrase (convergent_cue_reader: conceptual + the routed ruler); vs exact-match floor.

**MEASUREMENT:** all-organs-OFF (string-identity binding + exact-match meaning + spaCy attribution) vs all-ON (landed
front-end + salience binding + convergent-cue meaning). FLOORS recomputed per arm; INFO-FREE TWINS (shuffled binding +
shuffled meaning cue) MUST LOSE. CAN-FAIL: the composed reader must beat the floors CI-separated with twins losing;
DECISIVE either way (a rigorous negative localising the residual binding constraint is a PASS, per the original
wire-and-measure).

**BUILD PLAN:** extend `experiments/exp_convergent_cue_composed_reader_v1.py` (entity+meaning) with the front-end SEAM +
an all-OFF-vs-all-ON arm. SMOKE inline (few docs) to validate the harness; the FULL LitBank run (FHRR register + front-end
+ meaning over ~100 docs) is HEAVY → the REMOTE GPU box (queue-compliant `--self-test`/`--smoke`/`metrics.json` + prereg).

**HONEST OPEN RISK:** the composition may be dominated by one axis (the original finding was front-end-swamped); with the
front-end now fixed the test is whether the full reader clears the floor, or a residual constraint (coref quality, the
observation/attribution front-end) still binds. Either outcome is decisive + informative. **STATUS: DESIGNED, not built —
the build is the next dedicated step (smoke inline, full remote).**
- Commit: see git log (strategy: design gate for the full 3-axis end-to-end -- consolidation step 20).

### 2026-08-28 -- STEP 20 REFINEMENT (worked the design harder before building -- RE-SCOPED, do the right thing not the mechanical thing) ⚠️
Drilling the composition before building surfaced a load-bearing asymmetry: **the three axes are NOT equally broad.**
The FRONT-END fix (`graded_role_assigner`) only changes NON-CANONICAL role assignment (passives, reduced relatives),
which fire on ~1% of natural narrative (STEP 10: relcl fires on ~1% of QA-SRL; the landed lift is +0.011 overall,
+0.024 on the rare pre-verbal slice). ENTITY (pronoun linking) and MEANING (paraphrase) are BROAD (every query).
**CONSEQUENCE: a "full 3-axis on ONE natural gold" is DOMINATED by entity+meaning -- which STEP 18 ALREADY measured
(both load-bearing) -- with the front-end a tiny rare-case sliver.** So the full-3-axis is a COMPLETENESS CHECK, not the
decisive headline STEP 20 framed; and the corpus-mismatch (front-end on sentence-level QA-SRL vs entity/meaning on
cross-sentence LitBank) makes forcing all three onto one gold partly artificial. **RE-SCOPE:** (a) the COMPREHENSION
BASELINE is essentially ESTABLISHED -- each axis earns its keep on its OWN fair gold (front-end 0.739 vs 0.519 STEP 9;
entity 0.184 vs 0.058 STEP 13; meaning 0.750 vs 0.010 STEP 14; p1 comparison 0.758 vs 0.552) AND entity+meaning COMPOSE
(STEP 18) -- so comprehension is validated axis-by-axis + on the one non-rare-dominated composition. (b) DEMOTE the
full-3-axis to a LOW-PRIORITY remote completeness check (it will mostly reproduce STEP 18). (c) The genuinely HIGHER-LEVERAGE
next measurement is the reader's NEW capability -- p1's COMPARISON in a COMPREHENSION context ("which was bigger, X or Y?"
from a passage) -- the first REASONING-phase measurement, distinct from re-running the broad axes. **The neuroscientist-
strategist call: don't build a mechanically-impressive mega-measurement that mostly re-derives STEP 18; measure the new
capability the phase actually needs.** STEP 20's harness/seam plan still holds IF the full-3-axis is later wanted; it is
just no longer the headline.
- Commit: see git log (strategy: STEP 20 refinement -- re-scope the full 3-axis, redirect to comparison-in-comprehension).
