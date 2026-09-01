# FORWARD PROBLEM PROPOSAL (draft for the strategy session to formalize into a PROBLEM.md)

**Proposed slug:** `learn_canonical_script_order_from_a_causal_enablement_foundation`
**Proposed by:** the SOLVER on `the_reader_conflates_similar_events_needs_a_soft_and_conjunctive_grounded_aligner`,
2026-09-01. This is the located, drilled-to-bedrock residual of that problem: the aligner is validated, and the
before/after ceiling (~0.59) is now a KNOWLEDGE-FOUNDATION gap, not a mechanism gap.
**NOTE (scope):** a solver cannot create another problem's folder; this is a proposal. The mechanism is already
prototyped in `experiments/exp_conceptnet_causal_order_foundation_v1.py` (result folded into this problem's SOLVED.md).

## 1. THE PROBLEM IN PLAIN LANGUAGE
Our reader can now tell similar events apart, but it still can't reliably say which of two steps in a routine comes
first. We proved WHY: it learns order by noticing which steps tend to appear before others across a handful of
stories, and that "co-occurrence" signal is direction-blind by nature -- it tells you steps belong together, not
which is first. Humans get these right 97% of the time because they KNOW the cause-and-effect of everyday routines
(you must get the mug before you can pour). That knowledge isn't in a dozen short stories; it's world knowledge. The
task: give the reader that knowledge as a pre-built, offline "what-enables-what" reference (no live outside AI), and
use it to order the steps.

## 2. WHY THIS ONE
Reasoning over the story is the North Star's remaining half. The sibling problem proved the reasoning machine and the
event-aligner are built and brain-faithful, and localized the ONE remaining lever to the canonical-order signal --
and then proved that NO in-text signal breaks the ~0.59 ceiling (co-occurrence, positional, hierarchical, in-text
enablement, discourse connectives, episodic, fusion all <= 0.591). This is the single build that can convert the
rigorous near-positive into a clean positive, and the causal-order asset it builds is reusable everywhere the reader
must know "what comes before what" (planning, prediction, goal tracking, the learner's script acquisition).

## 3. HOW THE BRAIN DOES THIS (PINNED)
Canonical script order is fixed by CAUSAL/GOAL ENABLEMENT -- each action's effect establishes the next's precondition
(Schank & Abelson 1977; ProPara dependency graphs). The brain acquires this from rich, repeated, embodied experience
and stores it as event schemas whose order is conferred by mPFC/PMC (Baldassano/Hasson/Norman 2018) and reused via
ONE cognitive-map / relational-integration operation (Behrens 2018; Whittington TEM 2020). Co-occurrence/successor-
representation statistics are a GENERALIZATION device (symmetric, direction-weak; Dayan 1993; Gershman & Moore 2012)
-- which is exactly why the in-text co-occurrence signal caps. See
`research_canonical_script_order_mechanism_2026-09-01.md` (in the sibling folder).

## 3b. SHARPENED MECHANISM (drill-confirmed -- research_model_based_simulation_of_script_order_2026-09-01.md)
The brain recovers order by MODEL-BASED SIMULATION of a GENERATIVE, STATE-CONDITIONED forward model, not by a static
order lookup (event models generate the next event -- Zacks/Reynolds 2007; SEM is RUN not indexed -- Franklin 2020;
consolidation trains a generative SEQUENCE model -- Spens & Burgess 2024; forward-replay during temporal-order
judgment -- eLife 2020). Order is a BY-PRODUCT of a rollout over a MUTABLE WORLD STATE (each event's EFFECT
establishes the next's PRECONDITION), and it is a PARTIAL order. IMPLICATIONS FOR THE BUILD (all drill-pinned):
- **Keep `transitive_ordering` as the integrator (it IS the brain's stored ordinal line); simulation SUPPLIES the
  directed premises.** The genuinely-new organ is a WORLD-STATE register + operator model, NOT a new read-out.
- **The fix for the flat-KB coverage failure (1/301): SEED OPERATORS, don't query flat order.** Each event type = a
  STRIPS/PDDL operator (preconditions + add/delete effects) over a coarse predicate state (existence/location/toggle;
  ProPara grid). ConceptNet `HasPrerequisite`->precondition, `Causes`->effect; ATOMIC `xNeed`->precondition,
  `xEffect`->effect (seed OFFLINE, freeze a static library -- NaRuto does this but with an LM at generation; we do it
  offline). Join operators on shared STATE PREDICATES (have(X)/at(L)) -- predicates are shared across many events, so
  they cover densely where event-PAIR edges did not. Operators are learnable glass-box (LOCM, ARMS, ProPara).
- **Order = topological sort / forward-sim of the operator graph; feed the line only causally-DEPENDENT edges and
  ABSTAIN on independent (parallel) pairs** (fixes the total-vs-partial-order type-error).
- **HONEST calibration (do not over-build):** on short everyday-script narratives full mutable-state SIMULATION is
  likely measurably IDLE over the cheaper topo-sort (few re-toggles/consumed resources) -- LEAD WITH THE TOPO-SORT;
  build the rollout simulator only if a non-trivial re-toggle/consumption/branching subset is enumerable (can-fail
  test c'). "Simulation faithful-but-idle" is a full located PASS. Drill P: framing-right ~0.60; KB-seeded topo-sort
  beats 0.591 CI-sep ~0.30-0.40 (coverage risk); mutable-state sim beats static topo-sort ~0.15-0.25.

## 4. PINNED vs OUR-INVENTION
- **PINNED (copy):** causal-enablement precondition/effect chains fix order; the reused `transitive_ordering`
  cognitive-map read-out integrates directed premises into one ordering; event identity is the conjunctive role-filler
  (validated by the sibling problem).
- **OUR-INVENTION-UNDER-TEST (sweep):** the offline knowledge SOURCE (ConceptNet 5.7 HasPrerequisite/Causes/
  HasFirst-/HasLastSubevent -- a static, non-LLM asset already on disk; ATOMIC also on disk); how to MAP the reader's
  conjunctive event types to KB concepts (verb / verb+object phrase granularity); the premise-confidence weighting;
  whether to FUSE the world-knowledge order with the in-text co-occurrence order.

## 5. THE BAR (can-fail; CI-separated over the strongest REAL floor)
PASS = an OFFLINE causal-order foundation (static, NO LLM at inference), mapped to the reader's conjunctive event
types and ordered via the reused `transitive_ordering`, lifts end-to-end before/after CI-SEPARATED over BOTH floors
(similarity 0.525, text-position 0.518) AND over the IN-TEXT co-occurrence ceiling (0.591), with the shuffled-order
twin LOSING. A rigorous LOCATED negative is a PASS: if the foundation as-built does NOT clear it, report the KB
COVERAGE (scenario/pair hit rate) and localize whether the gap is KB coverage, event->concept mapping, or a genuine
irreducible (causally-independent) residual -- and name the STRONGER foundation (richer relations / ATOMIC / a
consolidated multi-source KB) before any "route exhausted".

## 6. FLOORS + CONTROLS
- **Floors:** similarity, text-position, AND the in-text co-occurrence order (0.591 -- the key floor: the foundation
  must beat what the text alone already gives).
- **Twin:** shuffled-order derangement of the KB-ordered nodes (must LOSE) -- excludes "any premise structure helps".
- **KB-coverage report:** fraction of scenarios / questioned pairs the KB actually orders (a low hit rate bounds the
  claim and names the next build).
- **Leakage:** the KB is scenario-general world knowledge, not fit to MCScript2 gold; report that it never sees the
  eval answers.

## 7. FILES AND ENTRY POINTS
Prototype: `experiments/exp_conceptnet_causal_order_foundation_v1.py` (offline `--build` streams
`data/conceptnet/conceptnet-assertions-5.7.0.csv.gz` -> `order_kb.jsonl`; the scorer maps conjunctive event types ->
directed premises -> `transitive_ordering`; arms CONCEPTNET / COOCCUR / HYBRID / floors / twin). Reuse the sibling
problem's conjunctive aligner + `transitive_ordering` read-out UNCHANGED. If it clears the bar, strategy lands the
wire (Q111): the offline causal-order KB as a static asset + the KB->premise builder, default-off, witnessed.

## PROTOTYPE RESULT (already run -- a LOCATED NEGATIVE that de-risks the real build)
`exp_conceptnet_causal_order_foundation_v1.py`, n=301 held-out. The foundation is BUILDABLE and glass-box: an
offline stream of the full ConceptNet 5.7 CSV yields 70,970 script-order edges (22,710 HasPrerequisite, 16,801
Causes, +6,221 first/last-subevent) in 62s, NO LLM. The mechanism is sound (edges -> `transitive_ordering`). BUT:
CONCEPTNET 0.545 < in-text COOCCUR 0.591; HYBRID 0.551. **Root cause, pinned:** a KB<->reader COVERAGE/GRANULARITY
mismatch -- at phrase precision, only **1 of 301** questioned event-pairs has a ConceptNet BEFORE-edge between the
two aligned events (direct pair-hit ~0). ConceptNet's generic concepts ("take a shower", "get clean") do not match
the reader's specific extracted events ("get out of the shower", "dry off with a towel"). So the foundation does not
FAIL for a mechanism reason; it fails because THIS source, naively phrase-matched, does not cover the specific
event-pairs the benchmark asks about. **The formalized problem's first job is therefore the KB<->event MAPPING +
COVERAGE:** (a) grounded/paraphrase-matched KB lookup (match a reader event phrase to the nearest KB concept, not
exact-string), and/or (b) a higher-coverage / finer-grained source -- ATOMIC (on disk, if-then event knowledge at a
finer grain) or a consolidated multi-source script KB. Report the pair-hit rate as the headline coverage number.

## 8. DO NOT QUOTE / DO NOT REDO
- Do NOT re-run the IN-TEXT order signals expecting a different result: co-occurrence (all aggregators), positional,
  hierarchical, in-text enablement, discourse connectives, episodic, fusion ALL cap <= 0.591 (measured in the sibling
  problem). The lever is EXTERNAL world knowledge, not a cleverer in-text statistic.
- Do NOT use an LLM to supply the causal order (the invariant). The foundation must be a static, offline, non-LLM
  asset (ConceptNet/ATOMIC are admissible; an LLM-distilled KB at inference is not).
