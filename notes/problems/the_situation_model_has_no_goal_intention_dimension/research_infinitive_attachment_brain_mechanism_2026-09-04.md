# Brain-mechanism research drill: infinitive attachment (purpose-adjunct vs complement) — the UPSTREAM parser component (2026-09-04)

Grounds the UPSTREAM fix for the goal dimension's parse-gated wall (bare-purpose extraction precision
0.33 vs a spaCy oracle): distinguishing a PURPOSE ADJUNCT ("she went [to buy bread]") from a
COMPLEMENT/raising/EXTRAPOSED infinitive ("began [to rain]", "wonderful [to meet]"), and attaching the
purpose clause + binding its implicit agent. Multi-lane scan; PINNED-BY-EVIDENCE vs OUR-INVENTION per
finding. Depth caveat: several primary PDFs were abstract/secondary-only (flagged); the strongest sources
were read in full (marked). Cited by `SOLVED.md` §8 (the upstream deepening).

## Lane 1 — LEXICALIST CONSTRAINT-BASED PARSING: the verb's subcategorization frame decides complement vs adjunct
- **MacDonald, Pearlmutter & Seidenberg 1994 (*Psychological Review* 101:676)** — lexical and syntactic
  ambiguity resolution derive from ONE lexical mechanism: the parser integrates probabilistic constraints,
  chief among them verb-specific ARGUMENT-STRUCTURE (subcategorization) frequencies, via competitive
  constraint-satisfaction. **Trueswell, Tanenhaus & Kello 1993 (*JEP:LMC* 19:528); Trueswell 1996 (*JML*)** —
  verb-specific subcat-frequency bias has IMMEDIATE, GRADED (not categorical) effects on attachment; subcat
  information is used "at the earliest point possible." **Garnsey, Pearlmutter, Myers & Lotocky 1997 (*JML*).**
- **VERDICT (PINNED, ~0.80):** the lexical knowledge the brain uses to decide whether a following "to VP" is
  a COMPLEMENT (want/begin/try/seem — the verb's frame has an open infinitival slot) or forces an ADJUNCT
  reading (go/come/stand — no such slot) is the verb's stored, frequency-weighted SUBCATEGORIZATION FRAME.
  A corpus-derived per-verb P(infinitive-complement) frame IS a faithful model of this knowledge.
- **NUANCE (from the neural-unification lane):** for the CLEAR case (verb categorically lacks the complement
  frame), the brain-faithful account is CONSTRAINT-SATISFACTION / FILTERING (the complement candidate is
  never licensed → the adjunct reading wins by exclusion), NOT a dynamical inhibitory race; true competitive
  inhibition (Vosse & Kempen 2000) is reserved for genuine residual ambiguity. **Our filter (skip a bare
  "to VP" whose governing verb is a complement-taker) is exactly this faithful filtering.** The graded frame
  frequency (we keep `p_complement`, threshold at 0.5) matches the graded-frequency evidence.
- **OUR-INVENTION (extrapolation):** no study tested the infinitival complement-vs-PURPOSE-ADJUNCT case
  specifically (the nearest, NP-vs-S-complement bias, is well-established). Applying the PINNED architecture
  to this exact construction is a defensible extrapolation, labelled as such (not a validated result).

## Lane 3 — NEURAL substrate for frame retrieval + unification
- **Vosse & Kempen 2000 (*Cognition* 75:105)** — lexical frames retrieved from the lexicon unify into a parse
  by competitive inhibition; incompatible links (grammatical/treehood violations) suppress each other.
  **Hagoort MUC (2013, *Front. Psychol.* 4:416)** — frame STORAGE in posterior temporal cortex, UNIFICATION
  in left inferior frontal cortex; **Snijders et al. 2009 (fMRI)** confirmed the predicted posterior-LIFC
  pattern for lexical-frame ambiguity. **Matchin & Hickok 2020 (*Cereb. Cortex* 30:1481)** — pMTG builds
  hierarchical lexical-syntactic structure. **VERDICT (PINNED as architecture):** lexically-retrieved frames
  are combined/selected in a named cortical circuit; our json-lookup frame is the computational-level model.

## Lane 4 — ATTACHMENT + control: where a purpose clause attaches, and who its implicit subject is
- **Frazier & Clifton 1996 Construal** (secondary): adjuncts (non-primary relations) are NOT attached by
  Late Closure/recency; they associate into the "current thematic processing domain (the extended maximal
  projection of the last theta-assigner)" — i.e. HIGH, at the matrix event level, resolved by thematic/
  pragmatic info. **"Rationale clauses are TP adjuncts, not VP adjuncts" (A'ingae, *J. Semantics*, read in
  full)** — HIGH attachment (propositional, not event-internal). Convergent: the scope-based control paper
  ("a rationale clause is a VP-EXTERNAL adjunct"). **VERDICT (PINNED):** a purpose/rationale "to VP" attaches
  HIGH to the matrix clause/event, not to the nearest embedded verb.
- **Controller = the matrix AGENT** (Whelpton 2002 "the intention is assigned to a phrase in the matrix,
  usually the subject"; Jones 1991 IOC default = matrix subject). CRITICAL refinement — **McCourt, Green, Lau
  & Williams 2015 (*Front. Psychol.* 6:1629, read in full):** "the ship was sunk to collect the insurance" →
  PRO = an implicit AGENT (the owner/saboteur), NOT the grammatical subject "ship" (a patient). So the
  default is AGENT (= subject in canonical actives), and a rule keyed to the SURFACE SUBJECT MISFIRES ON
  PASSIVES. Control resolution is rapid/lexical (Demestre 2024; Green 2018). An OBJECT-CONTROL override class
  exists ("bring/send NP along to VP", Faraci 1974/Jones 1991).
- **VERDICT:** PINNED = attach HIGH, bind PRO to the matrix AGENT (subject in actives). **OUR-INVENTION /
  known-residual:** our current agent-binding uses the nearest preceding nominal subject (correct for
  canonical actives, the dominant case), which is the AGENT there; the passive-agent and object-control
  overrides are named refinements (a quantified residual, not yet built).

## Lane 5 — EXTRAPOSITION / expletive-it
- "It would be wonderful [to meet X]", "it is hard [to say]", "a way [to go]", "time [to leave]" — the
  infinitive is an extraposed SUBJECT/complement of a predicate adjective/noun, not a purpose adjunct of a
  preceding verb. **VERDICT (PINNED surface cue):** expletive "it" + copula + an extraposition predicate
  (ADJ/NOUN that hosts an infinitival subject), OR the token governing "to" being such a predicate, reliably
  flags extraposition. Our extraposition-predicate set is DERIVED from UD-EWT (ADJ/NOUN lemmas heading an
  infinitival csubj/subject) — a corpus-grounded model of this cue, not a hand-list.

## Bottom line
1. A corpus-derived per-verb infinitive-complement SUBCATEGORIZATION FRAME is a brain-foundational (PINNED,
   ~0.80) model of the lexical knowledge the brain uses to decide complement-vs-adjunct; the FILTERING
   implementation (skip a bare "to VP" governed by a complement-taker) is the brain-faithful mechanism for
   the clear case, and the graded frame frequency matches the evidence. The specific infinitival-purpose
   application is a labelled extrapolation.
2. Incremental surprisal/prediction (Hale 2001; Levy 2008) is the SAME lexical-frame signal expressed
   dynamically (an infinitive is low-surprisal after a complement-taker, high after an action verb) — it
   ADDS a processing-time account but does not substitute for the frame; the frame is the knowledge source.
   (The reader already has a `predict_surprisal` organ — a natural composition point, not built here.)
3. Extraposition surface cue: expletive-it + copula + extraposition predicate (corpus-derived set).
4. A purpose adjunct attaches HIGH to the matrix event and binds PRO to the matrix AGENT (= subject in
   canonical actives; the implicit agent in passives — the named residual for a surface-subject rule).
