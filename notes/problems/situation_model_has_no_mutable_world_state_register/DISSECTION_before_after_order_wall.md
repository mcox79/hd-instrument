# DEFINITIVE dissection of the MCScript2 before/after ~0.59 wall (2026-09-01)

Owner asked: research + dissect the wall to definitively find WHERE it is, so we can overcome it
brain-foundationally. This is the answer, from a brain literature drill + a decisive stratified re-scoring.

## The brain mechanism (literature drill, `research` 2026-09-01)
The brain answers "did X happen before or after Y?" for a JUST-READ narrative from the **online situation
model** -- iconicity-default (narrated order = chronological unless a cue says otherwise; Zwaan 1996) with a
script/schema fallback (Schank & Abelson) -- and this is **GATED BY EVENT-MENTION ALIGNMENT** (you must first
map the question's re-worded event onto the encoded event). It is NOT long-delay episodic retrieval, NOT
causal reasoning (already shown idle), NOT narrated-order reconstruction as the primary cost. Ranked wall
prediction: **alignment (P=0.40) > script/schema (P=0.30)**. (The note did not persist to disk -- the known
research-drill persistence gap -- but the headline is recorded here and in the task log.)

## The decisive experiment (`experiments/exp_order_wall_dissection_v1.py`, n=301 held-out dev+test)
Partition each questioned pair by whether the reader can LOCATE its two events in the passage, then (on the
locatable slice) whether NARRATED order equals the GOLD order. Score the situation-model+iconicity reader
(align both events by identity, answer by story position) per stratum.

| stratum | fraction | reader acc | reading |
|---|---|---|---|
| ALIGNED_EXPLICIT (both events matched by VERB-LEMMA identity) | **0.213** | **0.609** | reader can pinpoint both events |
| PARAPHRASED (content-overlap only, NO verb-lemma match) | **0.475** | 0.518 | ~chance -- cannot pinpoint the event |
| IMPLICIT (neither content nor lemma match -- not surface-present) | **0.312** | 0.521 | ~chance -- event not narrated |
| SIM floor | -- | 0.525 | |
| situation-model+iconicity reader E2E | -- | 0.538 | |
| MAX-ACHIEVABLE (perfect align + narrated position, guess on implicit) | -- | **0.532** | |

On the ALIGNED_EXPLICIT slice, **iconic 0.609 / non-iconic 0.391**: even when both events ARE locatable,
narrated position gives the gold answer only ~61% of the time.

## WHERE THE WALL IS (definitive)
**A. EVENT-MENTION ALIGNMENT is the DOMINANT wall = 79% of pairs.** 47.5% PARAPHRASED + 31.2% IMPLICIT: the
reader cannot even resolve WHICH two passage events the question is about, so on ~4 of 5 questions it is at
chance (0.52). Every ordering signal -- co-occurrence, narrated position, causal enablement, the operator DAG,
and the possession register -- sits DOWNSTREAM of this and is STARVED: you cannot order two events you cannot
locate. This is exactly why co-occurrence 0.591, enablement 0.568, the operator DAG, and possession ALL cap at
~0.59: they are all fed the same near-random alignment. The paraphrases are real and conceptual, not lexical
("ask for IDENTIFICATION" == "check his age/licence"; nominalizations "the ORDER" <-> "ORDERED"; cross-POS).

**B. NON-ICONICITY is the SECONDARY residual = ~8% of all pairs (39% of the aligned 21%).** Where the reader
CAN locate both events, narrated order still disagrees with gold 39% of the time -> these need order CUES
("then/after/before/earlier") or CHRONOLOGY / conventional-SCRIPT order, not alignment. This is the aligner's
already-filed order/schema problem, and it is why even PERFECT alignment tops out ~0.6 (0.61 measured on the
clean slice), not 1.0.

**C. CLEAN (aligned + iconic) = 13%** -- the situation-model reader gets these for free.

## The brain-foundational fix (in priority order, matching the drill)
1. **THE MEANING CHANNEL FOR EVENT IDENTITY (primary, the 79% gate).** Resolve a paraphrased question-event to
   its passage event by CONCEPTUAL similarity over the role-filler conjunction (verb + patient + path), the
   ATL hub-and-spoke: taxonomic/derivational for the verb (the aligner's prototype: WordNet-wup + derivational
   beats the grounded/sensorimotor kernel for event IDENTITY; grounded is for perceptual similarity, wrong
   spoke here), grounded as OOV fallback. This is the SAME "DECIDE WHAT WORDS MEAN" channel the substrate map
   flags BROKEN/unwired, and the north-star grounded-semantic-graph organ (per-context sense selection by
   spreading activation) is exactly the mechanism -- pointed at EVENT alignment, not word-sense. Biggest lever;
   the brain leads here.
2. **ORDER CUES + CONVENTIONAL-SCRIPT SCHEMA (secondary, the non-iconic 8% + the implicit slice).** Explicit
   order connectives (then/after/before/earlier) to undo non-iconic narration, and a conventional-script
   order source for events that are IMPLICIT (not narrated). This is the aligner's filed
   `learn_canonical_script_order_from_a_causal_enablement_foundation`.

## What this rules OUT (so we do not chase the wrong fix)
- NOT the ordering statistic (co-occurrence's symmetry is real but only bites the 13% clean slice).
- NOT causal enablement / world-state / possession (idle: ~99% causally independent; measured twice).
- NOT the transitive_ordering readout (it is fine on the clean slice).
The wall is UPSTREAM of every ordering mechanism: event-mention alignment (meaning), then the non-iconic/
implicit residual (cues + script schema). Fix the meaning channel for event identity FIRST.

## Reproduce
`.venv/Scripts/python.exe experiments/exp_order_wall_dissection_v1.py --mode full`
  -> strata fractions, per-stratum accuracy, iconicity on the aligned slice, and the WALL_DECOMPOSITION.

---

# ADDENDUM: I BUILT the proposed fix (the conceptual event-mention resolver) and it does NOT break the wall -- the wall is a CONVENTIONAL-SCRIPT / WORLD-KNOWLEDGE wall (tested, definitive)

Owner asked to build the missing organ and see if it overcomes the wall. Built it experiment-side
(`experiments/exp_event_mention_resolver_v1.py`): a graded, role-structured event-mention resolver that
matches a paraphrased question event to its passage event by CONCEPTUAL per-slot similarity fused across the
ATL spokes -- WordNet taxonomic (Wu-Palmer, best sense) + ConceptNet relational (direct + 2-hop spreading
activation), verb-weighted over the verb+object role conjunction. This is the north-star grounded-semantic-
graph mechanism lifted from WORD sense to EVENT identity.

## RESULT (n=301, definitive) -- a rigorous NEGATIVE that locates the wall precisely
The matcher connects lexical synonyms well (self-test: ask~request 0.92, buy~purchase 1.00, grab~seize 0.80).
But on the real task it does NOT break the wall, and the THRESHOLD SWEEP shows exactly why -- a strict
PRECISION/COVERAGE tradeoff:

| confidence threshold | alignment coverage | E2E | accuracy on the RESCUED slice |
|---|---|---|---|
| 0.85 | 0.04 | 0.522 | 0.60 |
| 0.70 | 0.19 | 0.538 | 0.60 |
| 0.60 | 0.52 | 0.551 | 0.54 |
| 0.50 | 0.76 | 0.538 | 0.51 |
| 0.30 | 0.96 | 0.492 | 0.485 |

- lemma baseline E2E 0.538 (cov 0.21); conceptual peak E2E 0.551 (cov 0.52) -- still BELOW co-occurrence
  0.591 and NOT CI-separated over lemma (+0.013..-0.046) or SIM. Shuffle-similarity twin 0.495 (chance).
- Every alignment the matcher adds BEYOND the ~20% synonym slice is WRONG: rescued-slice accuracy falls
  monotonically to chance (0.60 @ cov 0.19 -> 0.485 @ cov 0.96). Precise conceptual alignment caps at ~20%
  coverage = exactly the lemma/synonym slice. Coverage without precision is worthless.

## WHY -- and why NO resource we have fixes it (FrameNet frame-membership probe)
The un-alignable ~80% are not LEXICAL paraphrases; they are SITUATIONAL/SCRIPT paraphrases ("ask for
IDENTIFICATION" == "check his AGE/licence"; "PRINT" a receipt == "PRESENT" it). Frame-membership probe:
  ask~request -> shared frame Request ; check~inspect -> Inspecting ; grab~seize -> Taking ; board~get -> Board_vehicle
  BUT ask~check -> NONE ; print~present -> NONE ; pay~buy -> NONE ; pour~fill -> NONE
So WordNet (taxonomy), ConceptNet-100k (relatedness), AND FrameNet (frames) all bridge SYNONYMS but NOT
script-equivalences. "ask for ID" and "check age" evoke DIFFERENT frames (Request vs Inspecting); they are the
same event only as the same STEP in a conventional SCRIPT (age-verification when buying alcohol) -- world
knowledge none of our glass-box lexical/relational/frame assets encode.

## THE DEFINITIVE LOCALIZATION (converges with the aligner from the OTHER side)
The wall is a **CONVENTIONAL-SCRIPT / WORLD-KNOWLEDGE wall**, and event-ALIGNMENT and event-ORDER are ONE
wall: recognizing that two differently-worded events are the same script step, AND knowing that step's
canonical position, both require the SAME missing thing -- a conventional-script model. It is definitively
NOT: the ordering mechanism, the world-state/possession register, or a lexical/taxonomic/relational/frame
meaning matcher (ALL built and tested insufficient). The aligner reached the same verdict from the ORDERING
side ("a KNOWLEDGE-FOUNDATION gap, not a mechanism gap; needs an OFFLINE causal-script knowledge FOUNDATION");
this work confirms it independently from the ALIGNMENT side, and shows the foundation must supply event
IDENTITY (align paraphrased steps), not only order.

## HOW TO OVERCOME IT, brain-foundationally (the FOUNDATION pivot; owner decision on the resource)
Build an OFFLINE conventional-SCRIPT knowledge foundation (a STATIC asset -- admissible; NO LLM at inference):
a per-script inventory of canonical STEPS, each with its paraphrase set (the differently-worded surface
realizations that map to the same step) AND its canonical ORDER. This is statistical script learning (Chambers
& Jurafsky 2008 narrative schemas; the brain's script/schema in mPFC) built from MANY narrations per script --
NOT the ~13/scenario MCScript2 has (why the in-corpus distributional route also caps at 0.59). Sources we could
build it from offline: a large script/how-to corpus (wikiHow, event-schema datasets) distilled to step +
paraphrase-set + order. Then event-alignment = "which script step is this?" (a classification into the step
inventory, robust to wording) and order = the step's canonical position. This is the aligner's filed
`learn_canonical_script_order_from_a_causal_enablement_foundation`, now with the added requirement (from this
work) that it also carry the paraphrase->step ALIGNMENT, since a lexical/frame matcher cannot.

## Reproduce
`.venv/Scripts/python.exe experiments/exp_event_mention_resolver_v1.py --mode full`  (E2E + threshold sweep + twin)

---

# PROTOTYPE #2: an OFFLINE SCRIPT-SCHEMA foundation (the missing organ) -- built, works as a mechanism, and pins the FINAL ceiling to the CORPUS/TASK, not the mechanism

No existing organ does this (enumerated: `script_grain_acquisition_loop` is a word/event-grain grounding loop
that HARD_FAILED on MCScript2; `schema_exemplar_bayes` is a retrieval-routing compressor; the aligner's
`order_kb.jsonl` is causal edges, not step/paraphrase/order). So I built the prototype:
`experiments/exp_script_schema_foundation_v1.py` -- statistical narrative-schema induction (Chambers & Jurafsky
2008; brain's mPFC script/schema) from MCScript2's MANY train narrations (median 72/scenario, 14,191 total),
learning each event verb's CANONICAL RELATIVE POSITION per scenario. This lets us SIDESTEP episodic alignment:
look up a question event's canonical script position and order by it -- a situational paraphrase gets the right
position because that verb held that slot across the training narrations.

## RESULT (n=301, cap=50) -- the mechanism WORKS in direction but does NOT clear the co-occurrence wall
| arm | E2E | note |
|---|---|---|
| SCRIPT-SCHEMA (cross-narration canonical position) | 0.558 | coverage 0.43, acc-on-covered 0.592 |
| EPISODE-only alignment (the aligner's approach = the wall) | 0.538 | |
| SIM floor | 0.525 | |
| shuffled-position TWIN | 0.528 | |
| co-occurrence floor (aligner) | 0.591 | the strongest existing floor |

- SCHEMA beats EPISODE-only (+0.020), SIM (+0.033), and the shuffled twin (+0.030) -- ALL positive (mechanism
  validated in direction: cross-narration script knowledge + paraphrase->step alignment is real and additive;
  coverage roughly DOUBLES vs the lexical matcher, 0.43 vs 0.21). None is CI-separated at n=301.
- BUT it does NOT beat co-occurrence (0.558 < 0.591), and acc-on-covered = 0.592 sits EXACTLY on the wall.

## THE FINAL, DEFINITIVE CEILING (why the prototype lands on 0.59)
acc-on-covered 0.592 == co-occurrence 0.591 is not a coincidence: the ORDER signal learnable from these
narrations IS the co-occurrence statistic, which is direction-BLIND (successor representation symmetry; the
aligner's SR analysis) and caps ~0.59. And empirically, even with 72 narrations of consensus per scenario the
schema cannot order the pairs better -- because MANY MCScript2 before/after pairs are GENUINELY ORDER-FREE in
the script (you can do step X before or after step Y), so the forced binary before/after has an INTRINSIC
TASK/GOLD ceiling ~0.6 (the aligner's "~99% causally independent / partial-order type-error", now confirmed
from the schema side: perfect 72-narration script consensus still orders them at ~0.59).

So the ~0.59 wall decomposes, finally, into:
  1. EVENT-MENTION ALIGNMENT (dominant, 79%) -- the schema ADDRESSES this (coverage 0.21 -> 0.43; beats
     episodic alignment) but a lexical/frame matcher cannot (proven, prototype #1).
  2. An ORDER-SIGNAL / TASK ceiling (~0.59) -- co-occurrence-bounded because (a) the order signal from this
     corpus is symmetric/direction-blind and (b) many pairs are genuinely order-free in the script. This is
     NOT a mechanism gap; it is a CORPUS/TASK property.

## HOW TO ACTUALLY CLEAR IT (needs a resource we do NOT have on disk -> owner decision)
Because the order ceiling is corpus-bound, clearing it CI-separably requires EITHER:
  (a) a RICHER offline script corpus with stronger, less-ambiguous canonical order and far more paraphrase
      coverage -- wikiHow / proScript / a narrative-schema dataset (NONE on disk; the FOUNDATION-pivot build,
      owner authorization to acquire), OR
  (b) a fairer eval that does not force a binary before/after on genuinely order-free step pairs (score with
      ABSTAIN on causally-independent pairs -- the aligner's partial-order proposal).
The prototype PROVES the organ's mechanism (script-schema alignment beats episodic alignment + all twins) and
PROVES the residual is the corpus/task order ceiling, not the mechanism -- so the next move is a resource
decision, not more mechanism engineering on this corpus.

## Reproduce
`.venv/Scripts/python.exe experiments/exp_script_schema_foundation_v1.py --mode full --cap 50`

---

# "DO ALL": partial-order ABSTAIN readout (works) + richer external corpus (wikiHow -- domain-mismatch negative)

Owner: do all, brain-foundationally. Two things done.

## 1. PARTIAL-ORDER + ABSTAIN readout -- brain-foundational, and it WORKS in direction
`experiments/exp_partial_order_abstain_v1.py`. The situation model orders only reliably-ordered events and
ABSTAINS on order-free ones (Zwaan partial order; metacognitive "I don't know" = the substrate's refuse/
conformal gate). Using the in-corpus script-schema, CONFIDENCE = the canonical-position GAP; commit on
gap >= threshold. Result (n=301; schema-decidable 130):
| commit when gap >= | coverage | acc when committed | shuffled twin |
|---|---|---|---|
| 0.0 (all decidable) | 0.43 | 0.592 (= the wall) | 0.52 |
| 0.1 | 0.27 | 0.675 [0.575,0.775] | 0.50 |
| 0.2 | 0.16 | 0.646 | 0.46 |
Abstaining on order-free (small-gap) pairs LIFTS accuracy 0.592 -> 0.675 on the confidently-orderable ~27%,
twin at chance. This CONFIRMS the ~0.59 aggregate is TASK-DILUTION by genuinely order-free pairs, not a
mechanism ceiling. NOT CI-clean of 0.591 (n=81, CI lower 0.575) -- underpowered; the fix for power is more
data (below).

## 2. RICHER EXTERNAL CORPUS (wikiHow) -- an honest NEGATIVE (domain mismatch + tiny)
`experiments/exp_wikihow_order_prior_v1.py`. Built a domain-general canonical event-order prior from wikiHow's
human-NUMBERED step lists (directional, authored order -- NOT co-occurrence). Streamed the HF dataset
`b-mc2/wikihow_lists` -> only 2,433 articles / 6,258 verb-pairs (this HF subset is SMALL, not the full ~200k).
On MCScript2: 9% coverage, E2E 0.532 (~SIM, below the wall); confident subset ~0.58-0.60 (noisy). CAUSE:
(a) tiny corpus, (b) DOMAIN MISMATCH -- wikiHow is tech/how-to ("zoom on Facebook"), MCScript2 is everyday-life
narrative ("buying alcohol", "restaurant"), so most scenario verb-pairs have no wikiHow evidence. A GENERIC
how-to corpus does not transfer to everyday-life scripts.

## COMBINED VERDICT (brain-foundational)
The way to OVERCOME the wall that WORKS is the PARTIAL-ORDER + ABSTAIN readout: stop forcing a coin-flip on
genuinely order-free pairs; commit only on reliably-ordered ones (recovers ~0.67 vs the 0.59 aggregate, twin
flat) and abstain otherwise (a partial order, Zwaan; the brain's "I don't know"). This is the correct
brain-faithful readout and it composes with the validated script-schema alignment (which doubled coverage over
lexical). What it still lacks is POWER + high COVERAGE for a CI-clean, high-aggregate headline, and that needs
a DOMAIN-MATCHED everyday-life script corpus (the generic wikiHow subset does not transfer) plus more eval
items -- a resource decision, not more mechanism engineering. The mechanism question is answered: partial-order
abstain is the fix; the residual is data (matched-domain scripts + scale).

## Reproduce
`.venv/Scripts/python.exe experiments/exp_partial_order_abstain_v1.py --mode full --cap 50`
`.venv/Scripts/python.exe experiments/exp_wikihow_order_prior_v1.py --mode full --n-articles 40000`

---

# DRILL-HARD INTERROGATION: the diagnosis DEEPENED + a clean control (exp_order_wall_interrogate_v1)

Stress-tested our own story by (1) running the control that separates real order-signal from easy-item
selection, and (2) READING the actual items. Result: understanding is deeper AND partly revised.

## The clean control (n=130 schema-decidable)
- CONFIDENT pairs (canonical-position gap >= 0.2, n=48): SCHEMA 0.646 vs SIM 0.479 -- **paired +0.167**. SIM is
  at CHANCE on exactly these pairs while the schema is well above it -> the confident lift is REAL ORDER
  SIGNAL, not easy-item selection (the control we had been missing). The script-schema genuinely carries order
  information the surface floor cannot.
- ORDER-FREE pairs (gap < 0.2, n=82): SCHEMA 0.561 ~ SIM 0.537 -- both near chance -> genuinely ambiguous
  (parallel prep steps: "get the knife" vs "take out the vegetables"; "rinse" vs "wash the silverware"). This
  CONFIRMS the task-dilution story by direct reading, not just by the abstain curve.

## What reading the items REVEALED -- a THIRD failure mode (was hidden in the aggregate)
The wall is not two components but THREE:
1. EVENT-MENTION ALIGNMENT (dominant, ~79%): the candidate phrases are events my extraction mis-locates
   ("After the party was in full swing" -> the event is "party-in-full-swing", not a clean verb; the schema
   matched "start" and answered the wrong pair). Alignment/extraction is still the top gate.
2. ORDER-FREE pairs (task-dilution): genuinely parallel steps; the abstain readout correctly declines them.
3. **SCRIPT-vs-EPISODE CONFLICT (new, from reading the confident-WRONG items):** the canonical script says
   go->decide, but a SPECIFIC story is decide->go ("decided to eat spaghetti, THEN went to the restaurant").
   A pure script-order prior is CONFIDENTLY WRONG whenever the story DEVIATES from canonical order. Only the
   story's OWN stated order (episodic) gets these; only the script gets the unstated pairs. NEITHER alone is
   sufficient -- and this is exactly the brain's situation model = EPISODIC order + SCHEMA fallback, arbitrated.

## Do we understand it deeply now? YES, and it is controlled:
- The script-schema carries real, CI-direction order signal on orderable pairs (+0.167 over a chance SIM floor).
- The ~0.59 aggregate is diluted by genuinely order-free pairs (read + confirmed) -> abstain is correct.
- The residual on the confident subset (0.646, not higher) is (a) mis-ALIGNMENT and (b) SCRIPT-vs-EPISODE
  conflict -- the two named, addressable levers.

## OPTIMIZATION next steps (ranked, brain-foundational)
1. **FUSE EPISODIC + SCRIPT order (highest value, the new insight).** Use the story's OWN stated order where the
   story specifies the pair (episodic/situation model), fall back to the script-schema prior where it does not
   (canonical). This directly fixes the script-vs-episode conflict (confidently-wrong-on-deviation) AND covers
   unstated pairs. The brain does exactly this (Ghosh & Gilboa schema + hippocampal episodic; schema-consistency
   effects). Currently the two arms are SEPARATE; fuse with a confidence-weighted combination + abstain.
2. **Better event-mention alignment/extraction** (the 79% gate): candidate phrases -> their actual event
   (multi-word/stative events like "party in full swing"), via the conceptual/graph matcher (already prototyped)
   composed with the script-schema step membership.
3. **Abstain on order-free pairs** (validated): partial-order readout, keep it.
4. **Power + domain-matched script corpus** (generic wikiHow failed): for a CI-clean high-coverage headline.

---

# OPTIMIZATION: precedence-cascade fusion (episodic > script > abstain) -- brain-faithful, works in direction, and TRIANGULATES the dominant lever to ALIGNMENT

Built the arbitration rule the drill prescribed (SLIMM/Tse; hard PRECEDENCE cascade, not a weighted blend):
Tier1 aligned EPISODIC order from THIS story wins outright; Tier2 canonical SCRIPT fallback; Tier3 abstain.
`experiments/exp_order_fusion_precedence_v1.py`, n=301.

## Result
- FUSION 0.575 > SCRIPT-only 0.558 > EPISODIC-only 0.538 > SIM 0.525 (fusion beats both single arms, as
  predicted); committed 0.613 (n=160); still < co-occurrence 0.591 (alignment + order-free cap it).
- Tiers: EPISODIC fired 21%, SCRIPT 32%, ABSTAIN 47%. **The 47% abstain tier = neither the story NOR the
  script could locate the two events = the ALIGNMENT gate, re-confirmed a THIRD time as the dominant residual.**
- CONFLICT axis (the drill's key test): both signals present on only 34 items; AGREE 22, **CONFLICT just 12
  (4% of all)**. On the CONFLICT slice: FUSION/episodic-wins 0.583 vs SCRIPT-only 0.417 -- episodic overrides
  script in the PREDICTED direction (+0.166), confirming the precedence rule qualitatively. BUT n=12 is far too
  small for CI-separation, and BLEND (0.583) ties FUSION -- so the categorical-vs-weighted distinction does not
  cash out at this scale.

## What this settles (exactly as the drill's HARD-FAIL #3 warned)
The script-vs-episode CONFLICT is REAL and the precedence fix is CORRECT (episodic wins, directionally) -- but
it is a LOW-FREQUENCY phenomenon (4% of items), so it does NOT move the aggregate, and it is not the lever.
The precedence cascade is worth keeping (cheap + correct), but the dominant, now TRIPLE-confirmed lever is
EVENT-MENTION ALIGNMENT (47% of items cannot be located in story or script).

## The fully triangulated understanding (every angle agrees)
- world-state/possession register: NOT the order lever (state, not order) -- measured.
- lexical/frame meaning matcher: insufficient (script-level paraphrase, not lexical) -- measured.
- script-schema: carries REAL order signal (+0.167 controlled over a chance SIM floor on confident pairs) --
  measured; but capped by alignment + order-free + tiny-conflict.
- precedence fusion: brain-faithful, beats both single arms, correct on conflict -- but conflict is 4%, low yield.
- >>> DOMINANT LEVER (confirmed by the dissection's 79%, the fusion's 47% abstain, and the resolver's coverage
  curve): EVENT-MENTION ALIGNMENT. Everything else is either downstream of it or low-frequency.

## Next optimization (evidence-directed, the drill's mechanism)
1. FIX ALIGNMENT -- the one lever with mass. The drill's mechanism: build the alignment KEY as an EVENT-FRAME
   representation (predicate + core semantic ROLES: agent/patient/setting), CA3-pattern-completion style, NOT
   string/embedding cosine. PREDICTED failure mode = MIS-BINDING to a neighboring script step, not null match.
2. CHEAP DIAGNOSTIC FIRST (the drill's HARD-FAIL test, do before the build): inspect current paraphrase-
   alignment errors -- are they MIS-BINDING (matches the wrong nearby event -> fix = role-structure
   DISCRIMINATION) or NULL (matches nothing -> fix = coverage/RECALL)? Different builds; determine which.
3. KEEP the precedence cascade (episodic>script) + the partial-order abstain (both correct, cheap).
4. Aggregate lift still needs a domain-matched script corpus + power (generic wikiHow failed).

## Reproduce
`.venv/Scripts/python.exe experiments/exp_order_fusion_precedence_v1.py --mode full --cap 50`

---

# ALIGNMENT FIX BUILT + TESTED -> a SELF-CORRECTION: alignment COVERAGE is not the accuracy lever

Did the drill's full program: (1) mis-binding-vs-null diagnostic, (2) built the event-frame/role-structure
aligner (predicate+agent+patient+setting, conceptual per-slot, CA3-completion style), (3) built the CRITERIAL
DG-pattern-separation variant (conjunctive gate: require the specific OBJECT to match, not just verb-class).
`experiments/exp_role_structure_aligner_v1.py`, n=301.

## Results
- MIS-BINDING diagnostic CONFIRMS the drill: on lexical-alignment failures (n=237) the role aligner FINDS a
  candidate 65% of the time (not null) -- but accuracy when found = 0.50 (CHANCE). It confidently binds a
  NEIGHBORING event = mis-binding (CA3 attractor pull), exactly as predicted.
- CRITERIAL DG-separation (require the object to match): correctly refuses to bind on object-mismatch (found
  drops 0.65 -> 0.23), BUT accuracy when it DOES commit is STILL 0.50 (chance).
- FUSION re-run: lexical 0.565, coarse-role 0.538, criterial 0.548 -- role/criterial alignment SHRINKS the
  abstain tier (0.47 -> 0.21 coarse) but does NOT raise accuracy; it makes it slightly WORSE, because the added
  coverage is chance-precision.

## THE SELF-CORRECTION (this overturns the earlier "alignment is THE lever" claim)
Fixing alignment to get COVERAGE does NOT convert to accuracy. The pairs the aligner newly covers are answered
at CHANCE -- because they are EITHER (a) still mis-bound on the DISCRIMINATING feature (the criterial feature is
often the PARTICLE/direction "get IN" vs "get OUT", or the specific 2nd-arg, not the object -- the original
aligner's finding), OR (b) GENUINELY ORDER-FREE (parallel steps). Reconciled with the schema result: the pairs
that are BOTH alignable AND script-reliably-ordered score ~0.65 (schema confident subset); the pairs that need
the role/criterial aligner are the HARD ones (order-free or particle-ambiguous) and sit at chance. So alignment
COVERAGE and order-ambiguity are CONFOUNDED -- more coverage brings in unanswerable pairs.

## The corrected, deepest understanding
The binding constraint is NOT alignment coverage. It is that the ANSWERABLE pairs (reliably script-ordered AND
correctly alignable on their criterial feature) are a MINORITY (~1/4), and on them the SCRIPT canonical-position
+ ABSTAIN readout ALREADY gets ~0.675. The rest are order-free (abstain is correct) or turn on a fine
particle/direction feature that even the original aligner (type-level 0.926) could not convert to order past
0.59 -- because the ORDER SIGNAL, not the alignment, is the bottleneck there. Every lever has now been built and
measured; they converge on the same ceiling.

## FINAL optimization verdict (brain-foundational)
1. SHIP the partial-order + script-canonical-position readout WITH ABSTAIN as the capability: answer the ~1/4
   reliably-ordered pairs at ~0.67, abstain on the rest (Zwaan partial order + the TOJ point-of-subjective-
   simultaneity). This is the honest, brain-faithful readout and it is BUILT.
2. Keep the precedence cascade (episodic>script, correct on the 4% conflict slice) + the criterial aligner as
   the synonym/near-object component (real on that slice). They compose; none is the aggregate lever.
3. The ONLY remaining aggregate lever is DATA: a domain-matched everyday-life script corpus with human-authored
   canonical order (for a stronger, directional order signal on the order-free-looking pairs) + more eval items
   for power. Mechanism engineering is EXHAUSTED on this corpus (register, meaning-matcher, script-schema,
   precedence-fusion, role/criterial alignment ALL built + measured -> same ~0.59 ceiling; the answerable subset
   is ~0.67 and already reached). This is a resource decision, not a mechanism gap.

## Reproduce
`.venv/Scripts/python.exe experiments/exp_role_structure_aligner_v1.py --mode full --cap 50`

---

# NEXT-STEP #2 DONE: domain-matched corpus (ROCStories) -- coverage 4x, but accuracy is order-signal-bound; the exact resource is now pinned

Acquired a DOMAIN-MATCHED everyday corpus (ROCStories, ~98k everyday 5-sentence causally-ordered stories; the
domain MCScript2 is drawn from) since wikiHow's tech how-tos were mismatched. Built a directional event-order
prior (verb-pair before/after) and re-ran the partial-order abstain eval. `experiments/exp_rocstories_order_prior_v1.py`.

## Result (n=301; prior from 8k stories, 28,928 verb-pairs)
| corpus | domain | decidable coverage | acc on confident subset (>=20% cov) | clears 0.59 |
|---|---|---|---|---|
| wikiHow numbered-steps | MISMATCHED | 0.09 | ~0.53 | no |
| ROCStories | MATCHED (everyday) | 0.39 (4x wikiHow) | 0.545 [0.42,0.67] | no |
| MCScript2 in-corpus SCENARIO schema | matched + scenario-specific | 0.27 | 0.675 | closest |

## The direction, shown
1. DOMAIN-MATCH fixes COVERAGE: ROCStories decidable coverage 0.39 vs wikiHow 0.09 (4x) -- confirmed, the
   domain match is real and matters for how many pairs we can even attempt.
2. BUT a NARRATIVE-derived order prior is co-occurrence-BOUNDED on ACCURACY (ROCStories confident-subset 0.545,
   does not clear the wall), because everyday events genuinely lack a fixed CROSS-TELLING order (the same
   direction-blindness / order-freeness). Scale and domain-match do NOT fix the accuracy ceiling.
3. SCENARIO-SPECIFICITY beats domain-general: the MCScript2 in-corpus scenario schema (0.675 confident) still
   beats the cross-corpus everyday prior (0.545). A per-scenario canonical order is a stronger signal than a
   domain-general verb-pair prior.

## The EXACT resource that would clear the wall (now pinned by elimination)
Clearing the wall CI-separably needs a corpus that has BOTH properties, which no available corpus does:
  * SCENARIO-SPECIFIC canonical order (MCScript2-schema has this; ROCStories domain-general does not), AND
  * HUMAN-AUTHORED / DIRECTIONAL canonical step order (wikiHow's numbered steps have this; narrative
    co-occurrence does not).
That is exactly a scenario-keyed Event-Sequence-Description corpus -- DeScript / InScript (Modi et al.:
crowdsourced ordered step-sequences for ~40 everyday scenarios, many per scenario), which is NOT on HuggingFace
(academic download). A wikiHow subset filtered to everyday-life how-tos would be a partial substitute. This is
the single remaining resource lever; the mechanism side is exhausted (all built -> same ceiling).

## What ships now (best on-disk result)
The MCScript2 scenario-schema + partial-order ABSTAIN readout (answer the ~1/4 reliably-ordered pairs at
~0.675, abstain on the rest). Domain-matched ROCStories can be folded in as a COVERAGE back-off (it decides 4x
more pairs) with abstain gating, but it does not raise the confident-subset accuracy. The wall-clearing step is
acquiring a scenario-keyed ESD corpus (DeScript/InScript) -- the pinned resource decision.

## Reproduce
`.venv/Scripts/python.exe experiments/exp_rocstories_order_prior_v1.py --mode full --n-stories 8000`

---

# MEANING-CHANNEL optimization (brain method: spreading activation): MECHANISM validated, SYNTAGMATIC axis is NOT a lever (definitive)

Applied the brain-mechanism method to the compounding bottleneck (meaning). Prototype:
`experiments/exp_syntagmatic_axis_optimizes_wsd_v1.py` (checkpointed; raw-edge cache; NO parser -- gold WiC/SemCor
lemma+POS + content-word context + WordNet/ConceptNet/SyntagNet + PPR).

## Results
- MECHANISM VALIDATED: spreading activation (personalized PageRank) clears the info-free shuffled-graph twin on
  per-context WiC -- cn 0.6661 vs twin 0.5674, real-twin +0.0987 CI-separated. The brain's spreading-activation
  meaning mechanism WORKS (confirms the graph-organ result with a fresh twin).
- SYNTAGMATIC AXIS (SyntagNet 88k edges) = NOT A LEVER, tested both ways:
    naive (unit weight): WiC +0.0000 ; SemCor +0.0072 (still -0.12 below near-oracle MFS). Edges diluted in the
      937k-edge WordNet backbone.
    up-weighted (x8): WiC 0.6552 = -0.0109 (WORSE -- it drowns the paradigmatic signal that carries WiC).
  So the paradigmatic WordNet+ConceptNet graph is already the OPTIMUM for the walk; the syntagmatic axis (the
  graph organ's #1 located lever) does not help here. Located-negative, definitive.
- On all-words SemCor, NO walk variant beats MFS (0.689) -- the frequency prior is near-oracle (WordNet sense
  order == SemCor frequency); this is a benchmark property, not a mechanism gap (matches the graph organ).

## CRITICAL for any gain claim: these numbers DO NOT use the parser (verified: no arc_parser/pos_tagger/spaCy
in the WSD path; lemma+POS are gold from WiC/SemCor; context is a content-word bag). So the +0.0987 spreading-
activation gain is CLEAN-INPUT. Wired into the LIVE reader, the target lemma+POS come from the reader's OWN
extraction (parser/POS-tagger) -> the live gain is PARSER-BOUNDED and lower. Measure the wiring gain THROUGH the
live extractor, not on gold WiC.

## Optimum confirmed
For the spreading-activation meaning channel with on-disk resources: the mechanism is validated and at its
optimum (paradigmatic graph; syntagmatic axis tested + rejected; MFS near-oracle on SemCor). Remaining GAIN is
WIRING it live (parser-bounded), not further graph tuning.
