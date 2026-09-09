# CATALOG — live non-brain-foundational stand-ins in the reader

**Slug:** `audit_the_live_substrate_for_non_brain_faithful_stand_ins_and_name_replacements` · **solver session, 2026-09-08.**
**Denominator (the absence claim requires an enumeration, not a search):** every organ `hdlab/situation_reader.py`
consumes at `read()` time, taken from its full import set (module-level + lazy-in-method) reconciled against the ACTUAL
`__init__` flag defaults at `situation_reader.py:851-923` (NOT the inline comments — several say "default OFF" but the
signature is `True`; this stale-comment trap is itself catalogued as C-STALE). ~45 organs consumed; each checked.
**Witness:** `verification/test_audit_live_standins.py` (30/30) reproduces every LIVE/DORMANT/remediated claim below on
the current bytes. **Method note:** four cluster sub-audits (front-end / coref-entity / affect-belief-goal /
state-space-causal-memory) each returned file:line evidence; every load-bearing claim was then re-verified first-hand.

**Legend.** BF = brain-foundational. LIVE = consumed by `situation_reader.read()` under default flags. DORMANT = built
but no read()-time consumer (landed ≠ live). PINNED = the brain's computation is fixed by evidence; OUR-INVENTION = a
placeholder we chose. Each entry carries the five required fields **(a)** brain structure+computation, **(b)** why the
code is not it (file:line), **(c)** BF replacement, **(d)** blast radius / live-vs-dormant with the proving grep,
**(e)** LOCAL-FIX vs RE-ARCHITECTURE.

---

## TOP-K (ranked by blast × severity)

| # | stand-in | live? | blast | fix class |
|---|----------|-------|-------|-----------|
| **1** | C1 gold-coref-inheritance leak (`_apply_commonnoun_gate`) | LIVE | CRITICAL — masks C3 experiencer + every coref/name-bridge/meaning gain | RE-ARCH (pri-6, filed) + a strip-the-peek LOCAL-FIX |
| **2** | C3 arc-eager surface-feature attachment scorer | LIVE | HIGH — sole head source for who-did-what/theme/obl | RE-ARCH (converges on pri-1) |
| **3** | C2 `commonnoun_binder.situation_predict` string-identity binder | LIVE | HIGH — sets `sm.entities` clustering; trails the naive floor | RE-ARCH (typed_coref binding) |
| **4** | C4 `experiments/*` imported AT INFERENCE (self-containment) | LIVE | MEDIUM — reproducibility gate-violation, ≥5 live sites | LOCAL-FIX (promote cells) |
| **5** | C7 `cleanup_family`/`iterative_attractor` sign()+attractor-as-ranker | LIVE (other path) | MEDIUM — active harm in the grounding-acquisition pipeline | RE-ARCH (graded read) |
| 6 | C5 `parse_confidence` fitted logistic + PURE-DEFER | LIVE-computed, inert | LOW today — a fitted stand-in for a globally-normalized posterior | LOCAL-FIX |
| 7 | C6 `context_grounded_valence` cert-fit governor perceptron | LIVE-computed, decision-dead | LOW — wasted compute, output discarded | LOCAL-FIX |
| 8 | C8 `hd_fact_store` 66% tautology/junk facts | LIVE (other path) | FLEET — foundation subsystem, not the reader | LOCAL-FIX (gate) |
| — | C9 `coref` "name-Jaccard" | DORMANT/misattributed | correction to CONT-28 | n/a |
| — | C10 `scene_segment` fixed-window | LIVE but dead-code | cleanup | LOCAL-FIX |
| — | C11 `polarity_operator` surface-scan vs parsed | LIVE, located-negative | low — parsed arm measured worse today | RE-ARCH (parser-gated) |

Entries C9–C11 are **located negatives / corrections** (flagged, then shown BF-defensible or dormant on deeper reading
— the bar credits these when the deeper reading is shown). C1–C8 are the eight LIVE stand-ins the bar requires.

---

## C1 — GOLD-COREF-INHERITANCE LEAK in `_apply_commonnoun_gate` — the #1 blast, already filed pri-6
**(a) Brain structure+computation.** PINNED: online, incremental discourse-referent formation with **no external answer
key** — Kamp/Heim DRT file-cards; antecedent retrieval by cue-based content-addressable matching (Lewis & Vasishth 2005)
+ Centering salience (Grosz-Joshi-Weinstein). The reader must CLUSTER mentions from the text alone.
**(b) Why the code is not it (file:line).** `situation_reader.py:4079` stashes the raw human-annotated CoNLL coref
column (`coref_mentions`, parsed at `coref.py:169` `coref = cols[-1].strip()` — the literal answer key). `:3844`
`anchored = {m["cluster"] for m in (self._coref_mentions or []) if not m["is_pronoun"]}` reads those gold IDs; `:3854-3855`
`gold = [m["cluster"] for m in ms if m["cluster"] in anchored]; lab_to_cluster[lab] = Counter(gold).most_common(1)[0][0]`
majority-votes the gold ID over each heuristic group; `:3856-3861` overwrites every member's `m["cluster"]`; `:4090`
`sm.entities = _build_entities(role_mentions)` builds the live entity set from the gold-overwritten clusters. The
docstring admits it (`:3825-3826` "each merged group INHERITS a real gold coref cluster id") — and its "Default OFF ->
never called" (`:3830`) is STALE: `commonnoun_situation_gate: bool = True` (`:914`), called at `:4086-4089`.
**(c) BF replacement.** Online cue-based clustering with zero gold read — the filed OPEN problem
`replace_the_entity_gate_gold_coref_inheritance_with_online_cue_based_clustering` (pri-6). Candidate organ: the pinned
`typed_coref` content-addressed type-license binding (already beats string-identity when honestly floored).
**(d) Blast / live.** LIVE (`commonnoun_situation_gate=True`; `verification/test_crosstype_live_wire.py` W4 independently
reproduces the leak — the native path keeps ≥80% gold IDs). Masks board dims **C3 experiencer-attribution** (honest
0.1548 vs leaked ~0.80-0.86), **C1 entity clustering** (honest 0.6947), **C2 name hard-link** (honest 0.0239). Every
entity/experiencer/goal-owner board number through the live gate is currently a peek.
**(e) BOTH.** Deleting `:3844`+`:3854-3855`+`:3856-3861` is a one-function LOCAL-FIX, but it silently drops the
pronoun→named-entity linkage the leak illegitimately supplies, so the correct scope is RE-ARCHITECTURE (swap the whole
binding to online cue-based clustering), which is exactly what pri-6 scopes.

## C2 — `commonnoun_binder.situation_predict` — a string-identity binder that trails the naive floor
**(a) Brain structure+computation.** PINNED (same DRT / content-addressed-retrieval target as C1): a definite NP resolves
by TYPE/content match (Ariel accessibility), not surface head form.
**(b) Why not it (file:line).** `commonnoun_binder.py:203-330` `situation_predict()` links a definite common noun to an
antecedent by **head-lemma string match** (`hl not in r.hls` gate, `:287`) + a modifier-disjointness veto, with an HD
event-centrality tie-break only when ≥2 head-matched candidates compete. It never asks whether the description is
TYPE-compatible with a different-headed referent — the operation the brain needs. Its own measured per-mention
resolution is **0.4904, BELOW plain string-identity 0.5412**. `window=16` (`situation_reader.py:3842`) was swept on the
very LitBank-gold corpus it is scored on (`commonnoun_binder.py:16-19`) — an eval-set-fit parameter.
**(c) BF replacement.** `hdlab.typed_coref` binding (content-addressed type-cue retrieval + non-writing
hold-under-uncertainty bridge), measured +0.0252 CI-sep over string-identity — but wired today only as a parallel
resolution-only field, not as the clustering consumer.
**(d) Blast / live.** LIVE — `entity_kb_resolver=False` (`:913`) so the `else` at `:3841-3843` runs `situation_predict`
on every read; it sets `sm.entities` clustering for every mention not overwritten by C1 (fully exposed on the
`CN:`-namespaced non-gold-covered singletons). Blast = the entity/who-has-what dimension.
**(e) RE-ARCHITECTURE** — swap the clustering consumer to the `typed_coref` binding (de-restrict its person-gate for the
clustering path, per the project's own upgrade list). *Note: a SECOND live path, `_resolve_commonnouns`
(`situation_reader.py:3915-4042`, `resolve_commonnouns=True`), is an honest gold-FREE typed-coref-style re-implementation
writing only to the additive `sm.commonnoun_resolution` field — it does NOT feed `sm.entities`, so it neither carries the
C1 leak nor supersedes C2. Both run live on different fields.*

## C3 — arc-eager SURFACE-FEATURE attachment scorer — the parser-cluster head (see the replacement DESIGN below)
**(a) Brain structure+computation.** PINNED: incremental, left-to-right, working-memory-BOUNDED structure building —
left-corner projection with a lossy bounded buffer (Now-or-Never bottleneck, Christiansen & Chater 2016; good-enough
bounded attachment, Ferreira/Frazier), and — the deeper property — parsing by **constraint-satisfaction with TOP-DOWN
feedback** (MacDonald-Pearlmutter-Seidenberg 1994; interactive activation, McClelland-Rumelhart 1981), NOT a one-way
bottom-up scorer.
**(b) Why not it (file:line).** `arceager_parser.py:56-84` (`_config_feats`) scores each shift/reduce/arc action from
surface n-grams — word identity (`s0w`,`b0w`), POS bi/trigrams, 3-letter suffix, stack/valency/distance buckets —
combined by a linear averaged perceptron trained to maximise UD-EWT UAS (`:1-18`,`:112-125`). This is Zhang-Nivre 2011
transition parsing (an accuracy paper), not a derivation of any sentence-processing mechanism. `arc_parser.py:50-81` and
`arc_labeler.py:51-82` are the identical architecture for arcs/labels.
**(c) BF replacement.** Already built and DORMANT: `incremental_parser.incremental_build` (`:78-150`), which its own
docstring reports BEATS the batch parser at candidate-argument ID (F1 0.6201 vs 0.5849, +0.0352 CI-sep, prefix-consistency
0.985 vs 0.941). The FULL replacement is the RE-ARCHITECTURE design below (globally-normalized posterior + graded-competition
joint settle + top-down loop = pri-1).
**(d) Blast / live.** LIVE — `parser_arceager=True` (`:894`); `parse_with_conf` is the sole head source for the default
`role_route="wired"` path (`:2031-2051`), i.e. every who-did-what / theme / oblique decision. HIGH blast.
`incremental_build` is DORMANT (`"incremental_build" not in situation_reader.py`; only the narrow `incremental_subject_before`
cue is live). `graded_parser` marginals are DORMANT (`"graded_parser" not in situation_reader.py`).
**(e) RE-ARCHITECTURE.** Downstream consumers need a full labeled `heads` map; `incremental_build` returns
`{verb:{args}}` — swapping the candidate source is a load-bearing pipeline change, and the full fix closes the recurrent
loop (pri-1).

## C4 — SELF-CONTAINMENT: `experiments/*` scratch cells imported AT INFERENCE on the live path
**(a) Brain structure+computation.** N/A (a hygiene/reproducibility property, not a computation). The rule: `hdlab/` must
be reproducible from a clean checkout (the typed_coref/world_state promotion standard = ZERO `experiments/` imports; many
organs deliberately byte-copy to honour it — e.g. `goal_owner_select.py:59` "hdlab/ must not import from experiments/").
**(b) Why not it (file:line).** LIVE read()-path `experiments/*` imports (a scratch cell can change under a live organ):
`context_grounded_valence.py:61-64` (module-level `import experiments.exp_bridge1_* / exp_grounded_appraisal_sim_*`, pulled
in whenever `situation_reader` imports the module at its own `:131`); `situation_reader.py:2335` `_temporal_order_register`,
`:2351` `_space_reader`, `:2378` `_belief_reader` (→ which imports `_space_reader`), `:2436/:2440` `_forward_prediction_live`
— all lazy but on the default-ON paths (`timeline_register`/`track_space`/`track_belief`/`predict_surprisal` all True);
`temporal_reasoner.py:54-55` (module-level `from experiments import _temporal_ordering_multiframe / _temporal_order_register`,
live via `track_temporal_reasoning=True`).
**(c) BF replacement.** Promote the load-bearing functions of those cells into `hdlab/` (the established VERBATIM-promotion
pattern), then drop the `experiments/` import. For `context_grounded_valence` that is `combine_biased_competition` + the
animacy-lookup helpers; for the belief/space/temporal paths, `_space_reader`/`_belief_reader`/`_temporal_order_register`.
**(d) Blast / live.** LIVE (unconditional or default-on). Not a board-number defect — a reproducibility gate-violation
(a clean checkout of `hdlab/` alone would fail to import the reader). Compounded by the stale docstring at
`situation_reader.py:2367` ("default-off") contradicting the signature (`track_belief=True`, `:869`).
**(e) LOCAL-FIX** (mechanical promotion; no computation changes).

## C5 — `parse_confidence`: a fitted logistic calibrator + PURE-DEFER that never fires
**(a) Brain structure+computation.** PINNED: Friston active-inference precision-weighting / Ernst-Banks 2002 cue
reliability, whose correct computational-level form is a **globally-normalized posterior** (an exact edge marginal), not a
locally-fit classifier; and the brain **integrates and commits**, it does not abstain (the obl_spatial work established
defer→commit as the BF move, +0.0144 CI-sep).
**(b) Why not it (file:line).** `parse_confidence.py:70-101` freezes a logistic (`_PATIENT_FULL_W`/`_OBL_W`, fit offline)
over features that are mostly the bottom-up parser's own greedy outputs, plus a permanently-inert `a2_marg` — the live
call hardcodes it away (`situation_reader.py:2251` comment "a2 dropped"; the raw single-root marginal AUC 0.782 beats the
whole obl calibrator's 0.736, per the module's own later docstring). The DEFER is dead: `precision_weight_tau=None`
(`:923`) and the defer is gated `if p_conf is not None and tau is not None:` (`:2256`), so `patient_defer`/`agent_defer`
stay `None`; repo-wide grep finds no consumer of the `.patient_conf`/`.patient_defer` fields it writes.
**(c) BF replacement.** `hdlab/graded_parser.py` exact single-root Matrix-Tree edge marginals (Koo 2007) — a genuine
globally-normalized posterior — already plumbed as `ArcParser.parse(..., want_marginals=True)` and
`structural_patient_pick(..., marginals=...)` but never requested by the reader. Drop the logistic (use the raw marginal),
COMMIT on the posterior (don't defer).
**(d) Blast / live.** LIVE-computed every event (`precision_weight_roles=True`, `:922`), but currently ZERO behavioural
effect (defer dead). LOW blast today; a genuine wiring debt + a fitted stand-in for a posterior.
**(e) LOCAL-FIX** (the module lists the wire points as additive). Part of the parser-cluster design below.

## C6 — `context_grounded_valence` cert-fit governor perceptron — live-computed, decision-dead
**(a) Brain structure+computation.** No brain structure — a hand-fitted classifier stage whose PINNED successor is Talmy
1988 / Wolff 2007 force-dynamics. (The `FORCE_CLASS_HARM_REAL` hand-list flagged in CONT-28 is already RETIRED, replaced
by `hdlab/force_dynamics_valence.py` — confirmed self-contained.)
**(b) Why not it (file:line).** `context_grounded_valence.py:127-136` `_governor_pred_fn` trains
`train_perceptron(_gov.TRAIN_ITEMS)` on 134 HAND-BUILT items (`experiments/exp_bridge1_governor_grounding_v1.py:172-191`)
— a cert-set-fit classifier — called at `:201-203`.
**(c) BF replacement.** The force-dynamics stage already present (`:211-212` `_fdv.force_dynamics_event_type`); drop or
lazy-load the perceptron.
**(d) Blast / live.** LIVE-computed but DECISION-DEAD: the reader's `_assign_affect` discards every non-event stage
(`situation_reader.py:840-841` `if result["stage"] != "event": return None`), and the perceptron only surfaces on the
governor stage — so its output never reaches `sm.events[i].affect`. Wasted compute, zero live observable. LOW.
**(e) LOCAL-FIX** (efficiency; correctness already handled by the force-dynamics stage + the reader gate).

## C7 — `cleanup_family`/`iterative_attractor` sign()+attractor-as-RANKER — DORMANT wrt the reader, LIVE in the grounding loop
**(a) Brain structure+computation.** PINNED: attractor dynamics are for pattern-completion / RECOGNITION (Hopfield;
Marr 1971 CA3), not for producing a graded similarity RANKING; ranking wants a graded population read.
**(b) Why not it.** `cleanup_family.py` uses `sign()` + an iterative attractor as a ranker, which re-promotes
high-degree concept-hubs and hurts semantic ranking (CONT-28 #3).
**(c) BF replacement.** Graded population read for ranking; reserve the attractor for the recognition/recall step.
**(d) Blast / live.** **CORRECTION to CONT-28 ("live via gap_detector"):** DORMANT wrt `situation_reader.read()` —
`cleanup_family`, `gap_detector`, `hd_fact_store` are ALL absent from the reader's import closure (witness W7). They ARE
live in a SEPARATE live pipeline — the FOUNDATION/grounding-acquisition subsystem (`hdlab/reading_grounding_loop.py`,
`hdlab/substrate.py`, `gap_driven_reader.py`), which consumes `gap_detector`→`cleanup_family`. So the defect is real but
its blast is the grounding loop's ranking, not any `situation_reader` board dim.
**(e) RE-ARCHITECTURE** (swap the ranker; keep the attractor for recognition).

## C8 — `hd_fact_store` — 66% tautology/junk facts — DORMANT wrt the reader, LIVE in the foundation subsystem
**(a) Brain structure+computation.** PINNED: semantic memory stores VETTED propositions (a consolidation/quality gate,
CLS McClelland-McNaughton-O'Reilly 1995), not tautologies.
**(b) Why not it.** ~66% of stored facts are tautology/junk (FLEET-flagged).
**(c) BF replacement.** A consolidation-gate quality filter on admission (`hdlab/consolidation_gate.py` exists).
**(d) Blast / live.** DORMANT wrt `situation_reader.read()` (witness W7); LIVE only in the grounding/foundation subsystem
(`foundation_persistence.py`, `grounding_acquisition_loop.py`, `three_tier_loop.py`). FLEET, foundation-side.
**(e) LOCAL-FIX** (gate admission).

## C9 — `coref` "name-Jaccard" — MISATTRIBUTED (correction to CONT-28)
`hdlab/coref.py`'s `EntityAliaser` does **exact** given/surname/token-set matching with gender gating + ambiguity
abstention (`:428-474`), NOT a Jaccard ratio. The normalized-token Jaccard matcher (`ov = len(toks & e.tokens)/len(union)`)
lives in `hdlab/coreference_resolver.py:214`, which is **DORMANT wrt the reader** (`"coreference_resolver" not in
situation_reader.py`; its own docstring calls it "the durable promotion target for a future refactor pass, not a
replacement in place"). So CONT-28's low-blast "coref name-Jaccard" is dormant/misattributed — not a live defect. If it
IS ever wired, Jaccard-over-tokens is not a semantic comparator (ORGAN_MAP already notes this) → replace with a
type/embedding comparator. **Located negative.**

## C10 — `scene_segment` fixed-window (`LOCAL_WINDOW=5`) — live but numerically DEAD (correction to CONT-28)
`event_centrality_coref.py` builds `sid_fixed = [i//LOCAL_WINDOW]` scene IDs on every read, but `EventCentralityReader`
is constructed with `graded_pick=True` (`situation_reader.py:1718`), and the graded ACT-R pick
(`graded_coref_pick`) NEVER reads the scene IDs (`event_centrality_coref.py:487-492`; `query_memory` also forced False).
So the fixed window is vestigial dead code, not a live proxy shaping output. The real cue-driven segmenter
(`scene_segment.detect_scene_boundaries` = the PE/N400 boundary detector, Zacks event-segmentation) is DORMANT (witness
W9). **(a)** PINNED brain mechanism = prediction-error event segmentation (Zacks-Speer-Reynolds 2007). **(e)** LOCAL-FIX
(delete the dead threading, or wire the cue detector if per-scene scoping is revived). **Located negative / cleanup.**

## C11 — `polarity_operator` surface-scan vs the parse-aware resolver — LIVE, but the BF version measured WORSE today
**(a)** PINNED: negation scope = the operator's clause-local **c-command** domain (a structural computation).
**(b)** `situation_reader.py:2597/2605` imports+calls only `event_polarity` (a backward token-scan), never the
parse-aware `event_polarity_parsed` (`polarity_operator.py:338-416`) — the module's own "principled successor".
**(c)** `event_polarity_parsed` over the reader's cached heads/deprels. **(d)** LIVE (`read_polarity=True`); the parsed
resolver is DORMANT. **(e)** RE-ARCHITECTURE, but PARSER-GATED: the disk measurement
(`data/exp_polarity_operator_parsed_ewt_v1/metrics.json`, n=132) is `surface 0.9318 > parsed 0.9091` ("PARSED_WORSE") —
the structural version loses on upstream arc-attachment noise. **Located negative:** the BF target is right in principle
but is bottlenecked by C3 (the parser); it becomes a win only once C3's attachment improves. A valid catalog entry whose
deeper reading shows the surface scan is the better-measured arm *today*.

---

## THE PARSER-SCORER CLUSTER — one concrete brain-faithful REPLACEMENT DESIGN (references pri-1; does not rebuild it)

**The cluster.** C3 (bottom-up n-gram arc-eager attachment scorer) + C5 (offline-fitted logistic calibrator + PURE-DEFER)
+ the family of bottom-up CUE PROXIES the prior obl-spatial solver flagged (ConceptNet-count / Lancaster-norm /
gold-coref-count cues — surface/frequency proxies used *in place of* a computed constraint). All share one architectural
error: **a feed-forward, hard-committing, bottom-up scorer where the brain uses a graded, globally-normalized,
constraint-satisfaction parse with TOP-DOWN feedback.** A better bottom-up scorer is not the fix; the *architecture* is
the stand-in.

**The replacement (four moves; the first three are landable LOCAL steps, the fourth is the pri-1 RE-ARCHITECTURE):**
1. **Posterior, not a locally-fit score.** Replace the arc-eager greedy score + the frozen logistic with the exact
   single-root **Matrix-Tree edge marginals** (`hdlab/graded_parser.py`, Koo 2007) — a genuine globally-normalized
   posterior over parses. Drop the `_OBL_W`/`_PATIENT_FULL_W` logistic (the raw marginal AUC 0.782 already beats it).
2. **COMMIT, don't DEFER.** Precision-weighting (Friston) *sharpens* the posterior; the brain integrates and commits. Take
   the argmax of the marginal over candidate heads (the obl-spatial result: commit +0.0144 CI-sep over greedy, 0/351
   no-regress). PURE-DEFER is retired.
3. **Joint settle, not a one-way handoff.** Fuse the attachment marginal with the `graded_competition` additive cue
   activation (Lewis-Vasishth) and let the lexical-category and syntactic levels settle TOGETHER via normalized recurrence
   (interactive activation; "syntactic ambiguity IS lexical ambiguity"). Run it on the working-memory-bounded
   `incremental_parser` substrate (built, measured superior, dormant).
4. **Close the recurrent predictive-coding loop = pri-1 (reference, do not rebuild).** The residual C3 cannot solve
   bottom-up is the **two-valid attachment** (~67% of wrong patient picks) — resolvable only by a TOP-DOWN expectation of
   *which argument the situation so far predicts*. That expectation is exactly the output of the posted pri-1
   **`build_the_generative_result_state_world_model`**: a content-sensitive generative rollout produces the expected
   patient / result-state, which biases the attachment+role competition (Rao-Ballard 1999 predictive coding; N400 as
   forward prediction-error, Rabovsky 2018). So the parser-cluster fix is **convergent with pri-1, not a separate build**:
   land moves 1-3 to get a graded committing posterior on a bounded incremental substrate; then feed pri-1's top-down
   expectation into that posterior's competition to close the loop. The arc-eager SOLVED, the front-end audit, and the
   pri-1 brief independently name this same loop as the completing lever.

**Why this is the BF answer and not a convenient one.** Every piece is PINNED or already-built-and-measured: the posterior
(Koo/Matrix-Tree, built), the commit (obl-spatial, measured), the joint settle (graded_competition, live), the bounded
substrate (incremental_parser, built+superior), the top-down loop (pri-1, posted with two generative prototypes already
beating retrieval). No external LLM at any step (the invariant).

---

## ADMISSIBLE — checked and deliberately NOT flagged (the do-not-over-fire discipline; a false positive is a failure)
- **Static offline FOUNDATION assets supplying knowledge the brain has** (not decisions): `affect_lexicon`,
  `psych_verb_frames`, `goal_register` desire/intend/try verb classes, `occ_appraisal`, `force_dynamics_lexicon`,
  `structured_matcher` (WordNet/FrameNet/ConceptNet signed-relation store), the FrameNet/WordNet/VerbNet `nltk.corpus`
  LOOKUPS in `predicate_argument_frontend`/`predicate_detector`. Each feeds a separately-stated PINNED decision rule.
- **Already-remediated (disk outranks the brief — do NOT re-flag):** spaCy purged everywhere in `hdlab/` (witness W10 —
  `perceptual_access_ledger._nlp = None`, `causation_typing` parses in-substrate); `FORCE_CLASS_HARM_REAL` retired
  (→ `force_dynamics_valence`); `state_register.incompatible()` WordNet-antonymy fallback LANDED (W12a);
  `location_register` region-taxonomy WordNet fallback LANDED (W12b).
- **DORMANT by flag (not live defects):** `causation_typing` typed links (`causation_typed=False`), `coherence_reader`
  (`track_coherence=False`), `structured_matcher` affect route (`affect_structured_matcher=False`),
  `entity_world_model_resolver` (`entity_kb_resolver=False`), `agent_hybrid`/`unified_referent` (False).
- **Genuinely BF, verified clean:** `causal_reasoner` (Pearl do-calculus + Halpern-Pearl actual cause),
  `spatial_relational_model` (Franklin-Tversky), `temporal_reasoner` (Reichenbach + Allen), `graded_role_assigner`
  (Competition Model additive cues), `event_centrality_coref` (forced to graded ACT-R via `graded_pick=True`),
  `salience_binder` (ACT-R base-level activation), `referent_per_np` (DRT), `predicate_detector` (noisy-channel logistic
  over interpretable cues, additive-only), `relcl_resolver`/`np_head_reduce` (deterministic linguistic rules).

## COMPLETENESS SCAN — the consumed organs the four clusters did not explicitly name (scanned, all clean)
The residual read()-consumed organs were scanned for stand-in signatures (fitted-at-inference weights, surface-only
decisions, hand-lexicon-as-decision, external tool): `event_bundle` (FHRR sign+argmax cleanup = the accepted/owner-locked
binding algebra, UNPINNED-OK), `situation_focus` (clean), `frame_induction` (the OFFLINE induction that explicitly
REPLACED a shelved flat perceptron — a fix, not a stand-in; frames are supply), `verb_subcat_frames` (FrameNet/VerbNet
valency supply; the `verb_subcat_thr=0.35` gate is OUR-INVENTION-swept), `bridging_inference` (cosine-argmax over the
grounded hub + WordNet lookup — SOLVED, brain-faithful), `typed_spokes` (WordNet/DBpedia type supply), `predictive_reader`
(OUR-INVENTION-swept role-centroid + temp, honestly labelled, graded not sign-quantised). **No new decision-standing
stand-in.** So the eight LIVE entries (C1-C8) + three corrections (C9-C11) are the full set on the `situation_reader`
read() path.

## POSITIVE CONTROL (the enumeration recovers every CONT-28-named item — witness W11)
Every component named in `BRAIN_FOUNDATIONAL_AUDIT.md` §2b CONT-28 is accounted for above: gold-coref leak (C1),
`situation_predict` (C2), arc-eager scorer (C3), `context_grounded_valence` (C6), `perceptual_access_ledger`+`causation_typing`
spaCy (remediated, W10), `cleanup_family`/`hd_fact_store` (C7/C8 — corrected to dormant-wrt-reader), `state_register`/
`location_register` (remediated, W12), `coref` name-Jaccard (C9 — corrected to misattributed/dormant), `scene_segment`
(C10), similarity organs (dormant per brief §4). No named item silently dropped. New this pass: C4 (self-containment) and
the C7/C8/C9/C10/C11 live-vs-dormant corrections.
