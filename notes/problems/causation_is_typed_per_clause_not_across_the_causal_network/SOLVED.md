---
problem: causation_is_typed_per_clause_not_across_the_causal_network
status: SOLVED
bar: "Types discourse-level causal links CI-separated over the connective/adjacency placeholder -- a discourse causal population (connective-linked clause pairs + multi-event chains); the placeholder (`_causal_network`'s untyped connective+adjacency link) recomputed on the same population = the floor; the info-free twin (shuffled edge types / shuffled network structure) LOSES CI-separated; report CI half-width + null p95; no number crosses populations. A POSITIVE control the metric can move. Isolates the network typing from single-clause typing (an ablation to per-clause typing without the network edges). A rigorous NEGATIVE is a FULL PASS."
result: "Discourse cross-event edge-typing 4-way accuracy (CAUSE/ENABLE/PREVENT/SEQUENTIAL) NET 1.000 [1.000,1.000] (bootstrap 5000, half-width 0.000; n=48 connective-neutral cross-SENTENCE passages, extraction given as structured events). Real-text bound (16 verbatim LitBank cross-event causal edges, FULL self-extraction): the physical force lexicon covers the cause verb in only 3/16 -- the other 13 are MENTAL/SOCIAL causation a physical-force system structurally cannot type. Built ACROSS it: an INTENTIONAL front-end feeding the SAME Wolff typer scores 1.000 [1.000,1.000] on constructed mental/social causation (n=30)."
floor: "the connective/adjacency PLACEHOLDER (type-blind -> majority CAUSE), recomputed on the same population = 0.271 [0.146,0.396]; AND the PERCLAUSE single-clause ablation (endstate read from the CAUSE clause, no cross-event edge) = 0.729 [0.604,0.854]. NET lower CI 1.000 > BOTH upper CIs (0.396 and 0.854). Intentional cell: PHYSICAL-only front-end (wrong system) 0.300 [0.133,0.467] and placeholder 0.333 [0.167,0.500], both beaten CI-separated."
controls: "(1) force-class-SHUFFLE info-free twin (destroys verb->force): p95 0.562, LOSES (NET lo 1.000). (2) edge-type-SHUFFLE twin (permute predicted types across items): p95 0.354, LOSES. (3) PERCLAUSE ablation (endstate from the CAUSE clause) = the single-clause-typing isolation: 0.729, beaten CI-sep -> the lift is the CROSS-EVENT effect-clause read (the PREVENT class: NET 1.0 / perclause 0.0 / placeholder 0.0). (4) PRECEDENCE positive control (flashback cause-ID): precedence finds the past-perfect cause 1.00 vs text-adjacency 0.00. (5) NECESSITY: NET abstains SEQUENTIAL on non-causal sequence 1.00 vs placeholder false-links 0.00. (6) intentional cell: intentional-class-shuffle twin p95 0.600 LOSES; PHYSICAL-only front-end (wrong brain system) abstains -> 0.300."
files_changed: "experiments/exp_causal_network_edge_typer_v1.py, experiments/exp_causal_network_realtext_v1.py, experiments/exp_causal_network_intentional_frontend_v1.py, verification/test_causal_network_edge_typer.py, notes/problems/causation_is_typed_per_clause_not_across_the_causal_network/research_causation_systems_brain_mechanism_2026-08-30.md"
reverify: ".venv/Scripts/python.exe verification/test_causal_network_edge_typer.py   # scaffold-free, 12/12 PASS, recomputes every headline from source"
---

# SOLVED -- a causal-network EDGE typer that types cross-event causal links, with the brain-faithful bound measured AND built across

## What I built (brain mechanism first)
The opening move was the brain's. The landed single-clause typer (`causation_has_no_force_dynamic_typing`,
owner-DONE) types ONE clause's verb; its measured applicability bound is that most narrative causation is a
CROSS-SENTENCE event->event link with no single causal verb ("The dam broke. The village flooded."). The brain
represents this as a **Trabasso causal network** (events are nodes; a causal edge exists where the earlier event
is "necessary in the circumstances" for the later; causally central events are read faster + recalled more), and
**Wolff/Talmy force dynamics LABELS each edge** CAUSE/ENABLE/PREVENT. I copied that COMPOSITION.

The edge typer (`experiments/exp_causal_network_edge_typer_v1.py`) types a cross-event edge by composing the
**landed** `force_dynamics_typer` over the two linked events:
- **DIRECTION** is gated by temporal PRECEDENCE (the integrated TIME register: a past-perfect "had Ved" event
  precedes narrative-now regardless of text order -- the flashback case). This blocks the post-hoc fallacy the
  brief names as non-brain-faithful.
- **EXISTENCE** is gated by NECESSITY: an edge is licensed only on force-dynamic / connective / bridge evidence,
  NOT bare adjacency. On a non-causal sequence the typer ABSTAINS; the placeholder always links.
- **TYPE**: the AFFECTOR force class comes from the CAUSE event's verb (Wolff), and the endstate polarity is read
  from the EFFECT event's clause -- a DIFFERENT Trabasso node. `force_dynamic_type(cause_verb, effect_endstate)`.

The network<->force-dynamics COMPOSITION is OUR-SYNTHESIS (Trabasso gives the network, Wolff gives edge labels;
their combination is not one published result -- LABELLED). The edge-construction necessity rule and the
clause-pair->force mapping are OUR-INVENTION-UNDER-TEST. The Wolff truth-table is PINNED and REUSED unchanged.

## What I measured
**The typer clears the bar** (`exp_causal_network_edge_typer_v1`, witness W2-W7): pooled 4-way edge-type accuracy
**1.000 [1.000,1.000]** vs the connective/adjacency PLACEHOLDER **0.271** (type-blind -> majority) and vs the
PERCLAUSE single-clause ablation **0.729**, both beaten CI-separated. Force-class-shuffle twin 0.474 (p95 0.562,
LOSES); edge-type-shuffle twin 0.252 (p95 0.354, LOSES). The three sharpest results, each a genuine discourse-level
(not clause-level) contribution:
- **The isolation (bar sec.3): PREVENT is the measured cross-event lift.** NET 1.0 / perclause 0.0 / placeholder
  0.0 on the PREVENT subset. A prevention's SUCCESS ("...the town stayed dry") is stated only in the EFFECT clause;
  the single-clause typer, reading the cause clause, cannot tell a succeeded from a failed prevention. CAUSE, ENABLE
  and SEQUENTIAL do NOT separate NET from the per-clause ablation -- PREVENT does. This is the cross-event signal,
  and it is exactly the brain-faithful place typing matters (only force dynamics represents a never-realised
  endstate; Wolff; Kaup negation-as-simulation).
- **Precedence gates direction (flashback).** On flashback passages ("The village flooded. The old dam had broken.")
  the precedence gate finds the past-perfect cause 1.00 of the time; text-adjacency finds it 0.00 (there is no prior
  event in text). Typing without precedence would type the wrong event.
- **Necessity abstains on non-causal sequence.** The typer emits SEQUENTIAL 1.00 on "She poured the coffee. He
  yawned."; the placeholder asserts a (false) positive causal link 1.00 of the time.

**The measured brain-faithful BOUND** (`exp_causal_network_realtext_v1`, witness W8-W9) -- the real research content,
answering the owner's "if you hit a wall, understand WHY". On **16 verbatim LitBank cross-event causal edges** (reused
from the integrated `exp_read_causal_chain` cell, FULL self-extraction with NLTK + WordNet):
- **The physical force lexicon covers the cause verb in only 3/16.** The other 13 are MENTAL / SOCIAL / INTENTIONAL
  causation: "she frowned because she **remembered**", "the servants wailed because she had **died**", "he held his
  tongue because he **promised**", "I came because I **felt** strange". A physical-force verb lexicon STRUCTURALLY
  cannot type these -- the cause verb carries no physical force.
- **This is NOT a coverage bug.** A brain-mechanism research drill (5 literatures, `research_causation_systems_brain_
  mechanism_2026-08-30.md`) returned the decisive verdict: the physical/mental split is a **principled bound on the
  force-SOURCE system**. The brain reads physical forces with the intuitive-physics/ToBY system (frontoparietal/
  premotor; Fischer, Mikhael, Tenenbaum & Kanwisher 2016 PNAS) and intentional/social forces with the mentalizing/
  ToMM system (mPFC/rTPJ; Saxe & Kanwisher 2003; Leslie 1994) -- two dissociable systems from infancy.
- **But the CAUSE/ENABLE/PREVENT TYPOLOGY is one unified engine.** Talmy (1988) built force dynamics to span
  physical, intra-psychological and social causation; Wolff (2007) defined the three types via ABSTRACT dimensions
  (patient tendency, concordance, endstate) -- none physical; Wolff & Barbey (2015) treat force theory as general.
  Corroborated by Trabasso's own narrative taxonomy (physical/motivational/psychological/enablement -- Warren,
  Nicholas & Trabasso 1979). **So the wall factorizes: ONE typology, TWO force-source front-ends.**
- **The wrong-SIGN value.** On 4 verbatim McGuffey PREVENT sentences the typer types PREVENT 4/4 while the placeholder
  asserts a positive CAUSE link 0/4 -- the one place typing flips a real answer's sign (the outcome was AVERTED, so
  there is no positive causal edge to assert). This is the concrete real-prose value of typing over the placeholder.
- **Honest negative on the CAUSE-only gold.** Real cause-ID gold is all CAUSE (none ENABLE/PREVENT -- a base-rate
  fact), so a majority-CAUSE placeholder scores 16/16 and the typer does NOT beat it on this population. The typing
  VALUE is the non-CAUSE minority + the wrong-sign cases, not a raw accuracy win on cause-ID prose.

## PUSH -- BUILDING ACROSS THE WALL (owner: "if the brain can do it, we can once we understand")
The drill said the 13/16 miss is a BUILDABLE fidelity gap. I built the second front-end
(`exp_causal_network_intentional_frontend_v1`, witness W10): an **INTENTIONAL force-source lexicon** derived from
FrameNet mental/social frames (affective/cognitive/desire/memory/awareness -> CAUSE; prohibition + a closed
commitment-to-refrain set -> PREVENT; permission -> ENABLE), feeding the **SAME** `force_dynamic_type` engine
UNCHANGED. On constructed connective-neutral MENTAL/SOCIAL cross-sentence causation (n=30): intentional front-end
**1.000 [1.000,1.000]** vs the PHYSICAL-only front-end (the wrong brain system, abstains) **0.300** and the
placeholder **0.333**, both beaten CI-separated; the intentional-class-shuffle twin loses (p95 0.600). On the real
LitBank edges, COMBINED (physical OR intentional) coverage is **6/16 -- double** the physical-alone 3/16 (the
intentional lexicon adds remember/know/promise). "He held his tongue because he promised" now types PREVENT (the
promise is the antagonist force opposing the urge to speak) via the same engine. This is a MECHANISM DEMONSTRATION
that the typology transfers across the two force systems; it is NOT yet a real-text accuracy at scale.

## What I did NOT establish (and would withdraw first if wrong)
- **Real-text end-to-end 3-way ACCURACY at scale, with automatic extraction.** The 1.000 headline is on CONSTRUCTED
  connective-neutral cross-sentence passages with extraction GIVEN as structured events (exactly as the landed
  single-clause typer's gold gives agent/verb/patient). The real-text cell shows the self-extraction pipeline is
  NOISY (on the physical slice it scores 1/5 -- a distractor force verb hijacks cause selection, a "not strong
  enough" negation mis-scopes the endstate, and catch/slip/trip are not force-classed). **Withdraw the constructed
  1.000 as a real-text claim first** -- it is a mechanism proof, and the honest real-text number is the coverage
  bound + the wrong-sign value, not an accuracy at scale.
- **The intentional front-end at real-text scale.** Its 1.000 is constructed; the real coverage lift is a verb-count
  (3 -> 6/16), not an accuracy (real cause-ID gold is all CAUSE). The commitment-to-ACT vs commitment-to-REFRAIN
  ambiguity is the intentional analogue of the physical CAUSE-vs-ENABLE tendency wall (world-knowledge; the parent's
  measured bound), so I claim intentional PREVENT only on prohibition + commitment-to-refrain phrasings.
- **The full mental slice.** The intentional lexicon covers emotion/cognition/desire/memory/commitment/permission,
  but communication (say), event (die) and perception (seem) causation still abstain -- named follow-on front-ends.

## KEY REALIZATIONS (the enabling moves)
1. **The cross-event lift IS the effect-clause polarity, and PREVENT is where it lives.** The single-clause typer
   reads endstate from its own clause; a discourse prevention states the block only in the EFFECT clause. Making the
   per-clause ablation read the CAUSE clause (one variable changed) isolates the cross-event contribution cleanly:
   CAUSE/ENABLE/SEQUENTIAL don't separate the two, PREVENT does. The isolation wrote itself once I saw that
   "succeeded vs failed prevention" is only decidable across the sentence boundary.
2. **A leak taught the real design.** My first PREVENT gold used cause verbs (block/stop/prevent) whose PAST-TENSE
   SURFACE ("blocked") is itself in the negation detector's cue set -- so the per-clause ablation read not-reached
   FROM THE CAUSE CLAUSE and got PREVENT "for free", defeating the isolation. The fix named the genuine cross-event
   case: opposing-ACTION verbs (hold/shield/deter/restrain/save) whose success is stated only downstream.
3. **The real-text miss is a DIFFERENT BRAIN SYSTEM, not a lexicon gap.** 3/16 physical coverage looked like a
   failure until the drill showed mental causation is read by mentalizing (ToMM), a system dissociable from
   intuitive-physics (ToBY). "Understand WHY the brain succeeds where our mechanism fails" turned a coverage number
   into an architecture: one typology, two front-ends -- and a buildable next front-end, not a ceiling.
4. **FrameNet's Cause_to_make_noise over-licenses the necessity heuristic.** "the bell rang", "a door creaked" are
   Cause_* frame members, so "nearest force verb = cause" mis-selects an ambient noise event over the true cause.
   A real, named limitation of the necessity proxy (motivates patient-matching), caught by the CHAIN subset.
5. **Derive both lexicons from an EXTERNAL resource, then write the gold.** The physical lexicon is the landed
   FrameNet one; the intentional lexicon is derived from FrameNet mental/social frames BEFORE the gold verbs were
   chosen -- so a high score is generalisation of the frame->class map, not memorisation (the construction-proof trap
   the parent named). The twin losing + the physical-only-abstains control confirm it is the verb semantics.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **The CAUSATION dimension's measured APPLICABILITY BOUND is now BUILT.** The 2026-08-29 audit entry says "most
  narrative causation is connective-linked clause pairs (the Trabasso NETWORK level) that force dynamics LABELS but a
  verb lexicon doesn't type." That NETWORK level now has an EDGE typer: compose the landed `force_dynamics_typer` over
  the Trabasso event network (precedence gates direction, necessity gates existence, force dynamics types), CI-separated
  1.000 vs the placeholder 0.271 and vs single-clause typing 0.729, twins lose. Composition is OUR-SYNTHESIS; PINNED
  computation reused unchanged.
- **NEW deviation, now measured and understood: force dynamics types the PHYSICAL slice of discourse causation; the
  BULK of narrative causation is MENTAL/SOCIAL (13/16 real edges) and belongs to a DIFFERENT brain system
  (mentalizing/ToMM vs intuitive-physics/ToBY).** The CAUSE/ENABLE/PREVENT typology is PINNED domain-general (Talmy
  1988; Wolff 2007; Wolff & Barbey 2015); the force-SOURCE extraction is domain-specific. Fidelity target: TWO force-
  source front-ends into ONE typer. An intentional front-end is BUILT (doubles real-text coverage); communication /
  event / perception front-ends remain.
- **New citations (PINNED):** Fischer, Mikhael, Tenenbaum & Kanwisher 2016 PNAS (intuitive-physics engine);
  Saxe & Kanwisher 2003; Leslie 1994 (ToBY/ToMM); Talmy 1988; Wolff & Barbey 2015; Warren, Nicholas & Trabasso 1979;
  Kuperberg, Paczynski & Ditman 2010 (graded online causal-strength during reading).

## Adjacent components -- capability / limitation / opportunity / brain-foundational status (owner push #2)
Evaluated for BOTH brain-foundational fidelity AND optimization potential, to seed next problems.
1. **The MENTALIZING / intentional-causation front-end (HIGH leverage -- the bulk of narrative causation).**
   *Capability now:* the intentional front-end BUILT here types emotion/cognition/desire/memory/commitment/permission
   causation via the same typer (constructed 1.000; real coverage 3->6/16). *Limitation:* communication (say), event
   (die), perception (seem) causation still abstain; commit-to-act vs commit-to-refrain is a tendency ambiguity.
   *Brain status:* PINNED that intentional causation is a distinct system (ToMM, mPFC/rTPJ); the force-configuration
   READ-OUT from a mental state is OUR-INVENTION (the specific online cue is an open empirical question). *Opportunity:*
   a fuller intentional extractor (goal/desire as agonist force; obligation/prohibition as antagonist; FrameNet
   Communication + Death + Perception frames), and couple to the ToM/belief organs (belief_partition) already landed.
2. **Cross-clause AFFECTOR/PATIENT extraction (the real-text bottleneck).** *Capability:* self-extraction (NLTK+WordNet)
   finds events; the necessity heuristic picks the nearest force verb. *Limitation:* a distractor force verb hijacks
   cause selection, and negation mis-scopes the endstate (measured: physical real-text 1/5). *Brain status:* the reader
   binds the affector to the patient via role assignment (PINNED); our proxy is positional. *Opportunity:* patient-
   matching (does the cause verb's patient undergo the outcome?) would fix both the noise-causative confound (#4 below)
   and the distractor hijack -- the single highest-yield real-text lift.
3. **The counterfactual-NECESSITY check (currently a force-verb proxy).** *Capability:* an edge is licensed on
   force/connective/bridge evidence, not adjacency (abstains on sequence 1.0 vs placeholder 0.0). *Limitation:* it is a
   PRESENCE proxy, not a true counterfactual ("would B have happened without A?"). *Brain status:* Trabasso's edge weight
   IS counterfactual necessity (PINNED); do-calculus HARD_FAILED here. *Opportunity:* a graded necessity from the force
   configuration (a PREVENT edge asserts B would have happened; a CAUSE edge asserts it would not) -- necessity falls
   out of the type, a tighter loop than a separate check.
4. **The noise-causative confound (Cause_to_make_noise).** *Capability:* the FrameNet lexicon has high force-verb recall.
   *Limitation:* ambient noise verbs (ring/creak) are Cause_* members and over-license the necessity heuristic.
   *Brain status:* a bell ringing is not a causal-network parent of a later event -- the reader knows this from the
   patient. *Opportunity:* subsumed by #2 (patient-matching), or a frame-level exclusion of sound-emission from the
   causal-network necessity set.
5. **TIME precedence register (integrated, EXCELLENT) -- the direction gate this typer relies on.** Healthy; consumed
   as the flashback direction gate (1.00 vs 0.00), no change needed. Confirms the composition strategy.

## What strategy would change in hdlab/ (Q111 -- I propose, do not land)
Promote the causal-network edge typer as the DISCOURSE layer of the CAUSATION dimension: replace
`situation_reader._read_causation`'s untyped network (connective + most-recent adjacency) with a TYPED edge builder
that (a) constructs the Trabasso network with precedence-gated direction (reuse the TIME register) and force/connective/
bridge NECESSITY (abstain, don't adjacency-link), and (b) types each edge via the landed `force_dynamics_typer` over
(cause verb force class, effect-clause endstate). Wire TWO force-source front-ends into the one typer: the landed
physical `_force_dynamics_lexicon` and the new intentional one (promote `build_intentional_lexicon`). Emit
`TypedCausalEdge(cause, effect, force_type in {CAUSE,ENABLE,PREVENT}, endstate_reached, source in {PHYS,INTENTIONAL})`.
Do NOT land it as a coverage-complete real-text organ -- land the mechanism + the measured two-system bound, wired for
the downstream consumers (why-questions, event segmentation, ToM/blame), and file the mentalizing front-end (adjacent
#1) + patient-matching (adjacent #2) as the lifts. NO do-calculus, NO external LLM.

## TLDR
Our reader could judge cause-and-effect inside a single sentence, but not across sentences -- "The dam broke. The
village flooded." is two separate events with no single cause-word. I built the reader's map of how a story's events
cause each other, and labelled each link with the kind of causation: did the first event CAUSE the second, merely LET
it happen, or PREVENT it? On clean test passages it labels the links perfectly where the old placeholder (which just
guesses "cause" for everything and links by nearness) gets about a quarter right, and every fairness check passes. The
sharpest case is prevention -- "the sandbags held; the town stayed dry" -- where nothing bad happened at all: the old
placeholder wrongly asserts a cause, and only this method sees the prevented, never-happened outcome (which needs
reading the SECOND sentence). Then the honest limit: on real novels, most "because" links are MENTAL -- "she frowned
because she remembered", "he held his tongue because he promised" -- and a physical-force method can't read those.
That is not a bug: the brain uses a SEPARATE system for reading people's minds than for reading physical forces, but
it uses the SAME three labels (cause/let/prevent) for both. So I built a second reader for mental causation that feeds
the same labeller, and it doubles how much real-story causation we can read. The next step is to read the rest --
speech, death, perception -- the same way.

## QUESTIONS
None. (The mechanism is built and clears the bar CI-separated with the isolation and twins; the real-text bound is a
measured, brain-explained two-system fact, and I built across it with the second front-end. The remaining items are
scale + more front-ends, named as follow-ons.)

## NEXT STEPS
1. **Build the fuller MENTALIZING front-end** (adjacent #1): Communication + Death + Perception FrameNet frames into the
   same typer, and couple to the landed ToM/belief organs -- the bulk of narrative causation lives here.
2. **Patient-matching cross-clause extraction** (adjacent #2): fixes both the distractor-hijack and the noise-causative
   confound; the highest-yield real-text lift. Then a larger auto-extracted real-narrative sample with a 2nd adjudicator.
3. **Necessity from the type** (adjacent #3): derive counterfactual necessity from the force configuration rather than a
   separate presence check.
4. Strategy: land the discourse edge typer in hdlab (proposal above), reusing the TIME precedence gate + BOTH force-source
   front-ends; fold the two-system AUDIT UPDATE into BRAIN_FOUNDATIONAL_AUDIT.md.
