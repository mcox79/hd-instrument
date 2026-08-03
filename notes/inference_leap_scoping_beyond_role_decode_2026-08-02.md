# Scoping the next leap: from role-decode to actual comprehension (causal-bridging inference)

**Date:** 2026-08-02. **Filed by:** Director (main thread, no dispatch). **Trigger:** USER-directed probe-to-aim
on the second big gap named in `notes/brain_fidelity_audit_and_path_to_fully_capable_comprehension_2026-08-02.md`
(commit bd0faab3c) — "causal-bridging inference triggered by event-boundary prediction-error" — following the
session's coreference win (match-or-allocate F1 0.843 vs recency-floor 0.462, HARD_PASS). KB-checked via
`tools/substrate_query.sh` before writing anything below (queries: "causal bridging inference event boundary
prediction error situation model" cosine=0.33 top hit; "event segmentation causal network comprehension question
answering" cosine=0.39 top hit — both return prior notes, not gold/experiments, confirming this capability has been
NAMED but never built or tested). No experiments dispatched; this is scoping only.

---

## 0. Where this sits in the standing decomposition (dedup check)

`notes/brain_foundational_stack_assessment_2026-07-30.md` (component #7, "Discourse-level / bridging inference")
already logged this as **ABSENT, UNTESTED** and explicitly deferred it pending two prerequisites: "#1's assembly
and #6's coreference are in place" (line 54). Both prerequisites are now DONE (per this session's CURRENT FOCUS):
clause-level role extraction is wired + VET'd (~0.60 end-to-end), the accumulate situation-model organ is wired
(`hdlab/situation_model_accumulate.py`), and competitive coreference just went from "genuinely untouched" to
HARD_PASS. **This capability is now unblocked, not newly discovered** — this note concretizes the "#7" line item
the July 30 assessment intentionally left vague, using the specific mechanism named in the Aug-2 brain-fidelity
audit (prediction-error-triggered event boundaries as the causal-inference trigger).

Prior-art citations already on file (not re-derived here): `notes/research_discourse_state_of_mind_situation_model_2026-07-17.md`
(A4 bridging/given-new automaticity debate, A5 event-segmentation-as-consolidation-trigger) and
`notes/research_drill_CI_comprehension_loop_situation_model_brain_mechanism_2026-07-21.md` (situation-model
integrator design, prediction-error/coherence-gate). No prior note or cell ever picked a SPECIFIC first inference
type or checked corpus affordance for it — that's this note's contribution.

---

## 1. Biology: which inference type is cheapest AND most brain-faithful to build first

Four candidate "next inference" types were on the table (causal-why, resultative-what-happened-next, temporal
ordering, generic bridging-the-gap). Grounding each against the literature already on file:

- **Temporal ordering** is largely already FREE in the current representation: `AccumulateRegister.add_event`
  keys events by `event_idx` in a fixed slot sequence, so "did event A happen before event B" is answerable by
  slot-index comparison with zero new machinery. McGuffey narrative prose is near-strictly chronological (no
  flashback/achrony sampled), so a temporal-order capability would mostly test string order, not genuine
  inference — low novelty, not a good first rung.
- **Causal ("why did X happen") and resultative ("what happened because of X")** are the SAME underlying relation
  queried from opposite ends (a CAUSE edge between two event-slots) — Trabasso & van den Broek's causal-network
  model of narrative comprehension (Trabasso & Sperry 1985, *JML* 24; Trabasso & van den Broek 1985, *JML* 24)
  represents a story as events connected by CAUSE edges, with recall/importance predicted by causal
  connectivity — and Zwaan & Radvansky's event-indexing model (already on file, A2) finds causal relatedness is
  one of the five monitored discontinuity dimensions with the most robust behavioral signature (Myers, Shinjo &
  Duffy 1987: causal relatedness facilitates reading time). So causal linkage is real, well-evidenced, and a
  SINGLE relation type covers both query directions — build once, serves two query framings.
- **Bridging inference generality**: Clark & Haviland's given-new / bridging framework (already on file, A4)
  distinguishes "authorized" bridges signaled by an explicit connective or discourse marker from unmarked
  implicit bridges that require the reader to invent an unstated link. The automaticity debate (McKoon-Ratcliff
  minimalist vs. Graesser-Singer-Trabasso constructionist, both cited A4) is UNRESOLVED specifically for
  implicit/unmarked bridges — but explicit-marker-cued bridges are the least contested case in that literature;
  nobody disputes that "because"/"so"/"in order to"/"thus" reliably route the reader to a causal link.

**Conclusion — minimal first capability: EXPLICIT-CONNECTIVE-TRIGGERED CAUSAL-LINK BINDING between adjacent
event-slots**, bidirectionally queryable (cause-of / effect-of). This is deliberately narrower than "bridging
inference" in general — it is the cue-driven subset the literature treats as least contested, leaving genuinely
implicit/unmarked bridging (the contested-automaticity case) for a follow-on rung once this one is proven. This
also gives the event-boundary trigger named in the Aug-2 audit a concrete job: an explicit causal connective is
itself a strong, cheap, already-detectable signal that the CURRENT clause continues the PRIOR event's causal
chain rather than opening a new one — i.e., it is a low-prediction-error case for Zacks' SEM boundary detector,
consistent with "prediction-error spike = new event" (A5) since connective-marked continuations are exactly the
LOW-surprise, expected-continuation case that should NOT trigger a boundary.

---

## 2. Corpus affordance (checked, not assumed)

Scanned all 247 passages across `data/eval_gold_mention_role_mcguffey_v1/gold_*.jsonl` (the existing role/coref
gold pool) for explicit causal/purpose/result connectives (`because`, `so that`, `as a result`, `therefore`,
`since`, `consequently`, `in order to`, `so he/she/they`, `thus`):

- **63/247 passages (25.5%)** contain at least one clause with an explicit causal/resultative/purpose connective.
- **73/1308 clauses (5.6%)** are themselves connective-triggered.
- Spot-checked 12 hits directly (e.g. `dodger_terrier`: "He is called Dodger because he jumps about so friskily";
  `charles_brown_feathers`: "So he lifted up the cover"; `rufus_wilson_bell`: "...asked him if he had rung the
  bell because he wanted anything"; `henry_bond_grammar`: "...wanted a grammar, in order to join a class...") —
  real, legible cause/effect pairs are present, almost all clause-adjacent (the cause is the immediately
  preceding or immediately following clause in the sample checked).
- **No gold causal-relation annotation exists anywhere in the repo currently** — the affordance is lexical
  (connectives are present in the raw text) but there is zero labeled `(cause_event, effect_event)` pair data.
  This mirrors the pronoun-coref situation before the density-scan-and-mine step, not the role-extraction
  situation (which had gold from day one).
- **Scale headroom is good, unlike the earlier "McGuffey too thin" finding for multi-entity density**: that
  finding was about DENSITY of entities per passage in a small extracted pool. Causal connectives are cheaply
  regex-minable straight from the raw graded-corpus text (`data/corpora/mcguffey_graded/{g1..g6}_*.txt`,
  168KB-840KB per grade, far larger than the 247-passage extracted gold pool), so a first annotation pass is not
  capacity-constrained — 63 hits is a floor from the SMALL existing pool, not the ceiling of what's minable.

**Verdict: affordance is real (explicit causal connectives are common, ~1 in 4 passages), but this is a
NEEDS-GOLD capability, not a build-on-existing-gold one.** A lightweight annotation pass (mine connective-cued
clause pairs from the raw grade text, hand/LLM-label the linked event pair, same pattern as the coref
density-scan-then-mine workflow that worked) is the correct first step, sized similarly to that prior effort —
not a from-scratch corpus-construction project.

---

## 3. Representation fit: does `AccumulateRegister` support this, and what's the minimal extension

Current representation (`hdlab/situation_model_accumulate.py`) is per-ENTITY: `add_event(entity, role, event_idx)`
binds `role_vec` to `idx_vecs[event_idx]` and bundles into that entity's register; `decode(entity, event_idx)`
unbinds by the event's `idx_vec` and cleanup-argmaxes over the role vocabulary. There is currently **no
cross-event relation binding at all** — every existing binding is (role, event) pairs scoped to one entity, never
(event, event) pairs.

**Minimal glass-box extension (reuses existing primitives, no new machinery class, no borrowed embeddings):**
add a PASSAGE-level (not per-entity) link register using the exact same `bind`/`unbind`/`bundle`/`cleanup_argmax`
primitives already validated:
- Two new atomic key vectors, `CAUSE_key` and `EFFECT_key` (same `unit_phase_vec` construction as role vecs),
  playing the same structural role as a "meta-role" — but instead of binding to a role string, they bind to the
  OTHER event's `idx_vec` (which already exists in `self.idx_vecs`, no new vocabulary needed).
- `add_causal_link(cause_idx, effect_idx)`: bind `CAUSE_key` to `idx_vecs[effect_idx]`, bundle into a
  passage-level `link_register` at slot `cause_idx` (i.e., "the event AT cause_idx has an effect, and here it
  is"); symmetric bind of `EFFECT_key` to `idx_vecs[cause_idx]`, bundled at slot `effect_idx`, gives the reverse
  query for free from the same write.
- `query_effect_of(event_idx)` / `query_cause_of(event_idx)`: unbind the passage's per-slot link contribution by
  `CAUSE_key`/`EFFECT_key`, cleanup-argmax over `idx_vecs` (already-existing vocab, size `max_event_slots`) to
  recover the linked event's index.
- This is structurally IDENTICAL to the already-VET'd role-decode organ (same bind/unbind/bundle/cleanup-argmax
  chain, atom 29609's ACCUMULATE mode already proves bundling multiple bindings into one register survives
  decode at this scale) — the only change is what gets bound to what. No new capability CLASS is being invented,
  which keeps this inside the "wire, don't island" / no-bolt-on discipline: it is an honest reuse, not a new
  black box.

---

## 4. First buildable cell sketch + can-fail

- **Gold construction (prerequisite, ~0.5-1 session):** mine connective-cued clause pairs from
  `data/corpora/mcguffey_graded/{g5,g6}_*.txt` (same regex used above, run against raw text not just the 247
  extracted passages) at a target of ~150-250 raw hits, hand/LLM-verify a subset for direction correctness (some
  connectives like "so" are ambiguous between causal and purely sequential/discourse use, and "so that" purpose
  clauses need checking they're not conflated with mere temporal sequence), landing on an estimated 80-150
  usable `(cause_event_idx, effect_event_idx, connective_type)` gold instances — comparable order of magnitude to
  the role-eval powered set (N=165) and larger than the coref eval's dense pool.
- **Cell:** wire clauses through the existing extraction pipeline into event slots (reuse the clause-segmentation
  + event-indexing already used to feed `AccumulateRegister`), call `add_causal_link` at connective-cued clause
  boundaries, then query `query_cause_of`/`query_effect_of` at held-out target event indices.
- **REAL floor (must be checked before calling this can-fail, per the recency-floor lesson from coref):** the
  spot-checked examples above are almost all clause-ADJACENT (cause = immediately preceding or following clause).
  A naive "always answer the immediately-adjacent clause" baseline is very likely to score high on this
  particular gold pool — this is the SAME shape of risk that made the initial pronoun-coref recency floor
  non-discriminating before the dense-gold mining fix. **Before treating this as a fair can-fail test, the gold
  mining step must explicitly count adjacency distance** (how many gold causal links skip >1 intervening clause)
  and, if the pool is recency-dominated, either (a) deliberately oversample non-adjacent causal links during
  mining (there are almost certainly some — the multi-clause LONG passages already sampled span longer chains),
  or (b) report the recency-floor score honestly alongside the organ's score rather than presupposing it fails.
- **Can-fail discriminator:** the extension organ should beat a recency-floor AND a majority-connective-type-
  direction floor (e.g. "so X" always means the PRIOR clause is the cause) by a real margin, on the
  adjacency-controlled subset specifically — mirroring the coref fair-test design (recency floor had to COLLAPSE
  below random for the test to be trusted).

---

## 5. Recommendation: BUILD-NOW, gated on a short gold-mining step first — not a big build yet

- Prerequisites (#1 role assembly, #6 coreference) are DONE — this is genuinely next, not premature.
- Representation extension is CHEAP and reuses proven primitives (no new mechanism class, no borrowed embedding,
  passes the no-bolt-on / wire-don't-island discipline) — a few hours of hdlab work, not a new research arc.
- Corpus affordance is REAL but currently ungolded — the honest recommendation is **NEEDS-GOLD, small (not
  richer-content-blocked like some other competencies this session found)**: mine ~150-250 raw connective-cued
  hits from the larger raw grade-text corpus (not just the 247-passage extracted pool), verify a subset,
  EXPLICITLY measure adjacency-distance distribution before trusting a recency floor, and only then build the
  extraction cell. This is a bounded, cheap first step (same shape as the coref density-scan that paid off),
  not a "needs richer/longer content" blocker like self-correction or cross-clause role-persistence turned out
  to be earlier this session.
- First rung deliberately EXCLUDES implicit/unmarked bridging inference (the automaticity-contested case per
  Clark/McKoon-Ratcliff/Graesser) — that is a legitimate follow-on once explicit-connective causal linking is
  proven, not folded into this first cell.

---

## Sources cited (already on file in the KB, re-cited here for this note's specific claims)

- Trabasso & Sperry (1985), *Journal of Memory and Language* 24; Trabasso & van den Broek (1985), *JML* 24 —
  causal-network models of narrative comprehension (causal connectivity predicts recall/importance).
- Zwaan, Langston & Graesser (1995), *Psychological Science* 6; Zwaan & Radvansky (1998), *Psychological
  Bulletin* 123 — event-indexing model, causation as a monitored discontinuity dimension; Myers, Shinjo & Duffy
  (1987) — causal relatedness facilitates reading time (already cited in
  `research_discourse_state_of_mind_situation_model_2026-07-17.md` A2).
- Haviland & Clark (1974), *JVLB* 13; Clark & Haviland (1977); Clark (1975) — given-new contract, "authorized"
  vs. unmarked bridging inferences (already cited, same note, A4).
- McKoon & Ratcliff (1992), *Psychological Review* 99 (minimalist hypothesis) vs. Graesser, Singer & Trabasso
  (1994), *Psychological Review* 101 (constructionist "search after meaning") — automaticity debate, unresolved
  for implicit bridges specifically (already cited, A4).
- Zacks & Tversky (2001), *Psychological Bulletin* 127; Zacks et al. (2007), *Psychological Bulletin* 133 —
  event-segmentation prediction-error boundaries (already cited, A5); reused here to motivate why an explicit
  connective is a LOW-prediction-error / expected-continuation signal.

No new web research was dispatched for this note — all citations above were already banked in the KB from prior
research drills (confirmed via the two `substrate_query.sh` calls at the top of this note); this scoping pass
is corpus-inspection + representation-analysis + literature-application, not new lit-scanning.
