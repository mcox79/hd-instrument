# Brain analysis + design -- the_relcl_parser_is_too_weak_for_filler_gap_role_assignment

## How the brain does this (the opening move; UPDATED after a focused literature drill 2026-08-26)

Canonical (active SVO) role assignment runs on a fast VENTRAL/heuristic route (Bever's NVN "first-noun =
agent"; the two-line rule copies it -- PINNED). Reversible NON-CANONICAL constructions -- reversible
passives, object-relatives, object-clefts -- are where syntax is the ONLY cue.

**The mechanism (2020s consensus, adjudicated by the drill): graded, additive, CUE-BASED CONTENT-
ADDRESSABLE RETRIEVAL -- not a discrete rule and not "movement" per se.** At the verb/gap the parser
retrieves the argument that fills each slot by a PARALLEL, direct-access match of retrieval cues
(structural position, animacy, case, agreement, verb selectional restriction) against the held NPs
(McElree 2000, "Sentence Comprehension Is Mediated by Content-Addressable Memory Structures"; Lewis &
Vasishth 2005 ACT-R; Van Dyke & McElree 2011; reviewed Vasishth & Engelmann 2022). The activation of each
candidate is the SUM of weighted cue matches with a FAN/interference penalty (a cue shared by many items
gives weaker per-item activation) -- formalised in Dotlacil 2021, whose central result is that **the
ACTIVE FILLER STRATEGY is NOT a stipulated rule but EMERGES from cue-based retrieval + expectation**. So
our discrete active-filler resolver is a COMPETENCE-level approximation of this retrieval, exact only in
the clean single-filler regime.

**Neural substrate (CORRECTED):** the earlier "BA44 + arcuate = syntactic MOVEMENT operator" framing
(Grodzinsky & Santi 2008) is now a MINORITY view. Lesion evidence dissociates the two error types:
prefrontal/BA44 damage -> morphosyntactic/sequencing errors (voice-independent); **temporo-parietal damage
(posterior STG, angular/supramarginal) -> selective THEMATIC ROLE REVERSALS, worse on reversible
non-canonical order** (Beber, Capasso, Tettamanti & Miceli 2025; Matchin & Hickok 2020 place hierarchical
comprehension-side structure in pMTG). So reversible role BINDING localises to posterior-temporal/inferior-
parietal networks with frontal regions supporting WM/sequencing -- consistent with a memory-RETRIEVAL
operation, not a dedicated movement operator. Agrammatic chance-level performance (Caramazza & Zurif 1976)
is reinterpreted as noisy retrieval, not trace deletion.

The active-filler behaviour we copy -- posit a gap, and if the subject slot is filled move to the object --
falls OUT of this retrieval (Frazier 1987; Clifton & Frazier 1989 describe the behaviour; Dotlacil 2021
derives it). The subject-vs-object gap is signalled by whether an overt subject NOMINAL intervenes between
the relativizer and the verb -- a fast, reliable function-word cue that our discrete resolver reads
directly. Similarity/position INTERFERENCE (Gordon, Hendrick & Johnson 2001; Van Dyke & Lewis 2003 cue-
overload) and center-embedding collapse are the signatures that DISTINGUISH the graded retrieval from a
discrete rule -- the discrete rule structurally cannot produce them.

## PINNED vs OUR-INVENTION-UNDER-TEST

- **PINNED:** reversibility forces syntax (animacy/plausibility cannot disambiguate two animate arguments);
  the active-filler strategy + the empty-object-slot gap posit; cue-based retrieval at the gap.
- **PINNED (negative):** the brain does NOT run a general labelled dependency parse to do this -- the
  dorsal circuit is SPECIALISED for movement/filler-gap, fast and shallow, function-word-driven.
- **OUR-INVENTION-UNDER-TEST:** the exact surface realisation of the active-filler cue (nearest attached
  relativizer + intervening-subject + empty-object-slot over UPOS + closed-class words). We copy the
  OPERATION; the specific cue thresholds are ours and are swept/tested.

## Why the general arc parser is the WRONG tool (the thesis)

`arc_parser.py` is a greedy first-order (arc-factored) UNLABELED perceptron, UAS ~0.79. Two structural
reasons it fails exactly here, both confirmed on disk:
1. The single arc it must get right -- embedded-verb -> distant fronted antecedent, ACROSS an intervening
   subject NP -- is the longest-range, most garden-path-prone arc, and greedy first-order decoding
   mis-attaches it (measured: on "The doctor that the lawyer chased ..." it made *lawyer* the ROOT and
   attached *chased*->*lawyer*).
2. Being UNLABELED it cannot tell subject from object, so even a correct attachment does not yield the
   role. On subject relatives the `relcl_gap` rule fires on the AGENT and the prior arm reduces to
   "always pick the fronted antecedent" -- wrong on every subject extraction.

## Arms and the balanced-set trap

Gold PATIENT token per construction, both nouns animate (reversible). The set is BALANCED between
SUBJECT-extraction and OBJECT-extraction so the two dumb strategies are each capped at ~0.50:
- TWO_LINE_PRECISE (nearest nominal after the verb + participle voice) -- right on subject extractions,
  wrong on object extractions. The bar's named floor.
- PICK_FRONTED (always the fronted antecedent) -- right on object extractions, wrong on subject. Degeneracy
  control; the difference INC - FRONTED isolates the value of subject/object gap RESOLUTION.
- FILLERGAP_INCREMENTAL -- the active-filler resolver over UPOS + relativizers (no arc graph). Deliverable.
- FILLERGAP_ARCPARSER -- the prior arm over the real arc parse (shows the general parser is harmful).
- FILLERGAP_ORACLE -- construction-gold gap (the reachable ceiling).
- TWIN -- random covered nominal, 5 seeds (info-free-loses).

Only genuine subject/object gap resolution exceeds 0.50; the prior synthetic set (object-extractions only,
so fronted == answer always) let a degenerate "pick fronted" score 1.000 without resolving anything.

## Construction gate (the real-text lever)

Two active-filler conditions make the OBJECT-gap fire faithful and precise on natural text:
1. ATTACHED relativizer -- the relativizer's immediately preceding token is a NOMINAL antecedent (rules
   out the complementizer "that" after a verb, and interrogative "who").
2. EMPTY object slot -- the verb has NO overt nominal object in its own clause (scan stops at the next
   finite verb / relativizer / punctuation). The gap IS the empty position; posit it only where empty.
Otherwise (subject gap, filled object, complementizer, canonical) -> defer to two-line. On real QA-SRL this
gate fires on 0.75% of items and is net-safe (no leak on the 85% canonical majority).

## Falsifiers / how we would know it failed

- If the incremental resolver did NOT beat two-line CI-separated on the balanced fronted regime, or if
  PICK_FRONTED tied it -> it is not resolving the gap, just detecting fronting.
- If TWIN did not lose -> the scorer cannot tell signal from noise on this population.
- If the resolver leaked on canonical (INC < two-line there) -> the gate is unfaithful.
- If ORACLE did not reach ~1.0 -> the target is not reachable and "parser too weak" is wrong.

## Guards (written as code, in the witness)

- The incremental resolver's signature takes NO `heads` argument -> it structurally cannot use the arc
  graph (glass-box: the win is not laundered parser output).
- The arc arm's answer changes when heads are permuted; the incremental arm's does not.
- Info-free twin and the degenerate pick-fronted arm both scored and shown to LOSE.
- Gate no-leak asserted on canonical; depth-limit (outer-gap collapse) asserted with oracle reachable.
