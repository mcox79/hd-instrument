# Research drill — the modern comprehension board + the register-specificity of the Competition-Model role assigner (2026-09-06)

Solver: rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_19c_litbank_eval. Glass-box, NO external LLM.

## The opening move: which brain structure, and are we replicating or substituting?

This is a MEASUREMENT-fidelity rebuild — the reader is unchanged, only the corpus + golds change. But the brain
frame still sets the bar for each dimension, and the owner's directive ("every component, you AND upstream,
brain-foundational") makes the upstream organs the real subject. The reference standard is a competent adult
reader comprehending the register they actually read: MODERN language. Grading comprehension on 19c fiction is
the standing corpus-age confound — the analogue of testing a speaker of today's English on Early Modern text.

Two upstream organs feed the board's coref + who-did-what dimensions, and both are PINNED brain mechanisms:

| dimension | upstream organ | brain mechanism (PINNED) | status |
|---|---|---|---|
| coref (pronoun) | unified discourse referent | Heim(1982)/Kamp DRT file-change; ACT-R base-level activation (Anderson); Ariel(1990) accessibility hierarchy | owner-scope SOLVED (sibling), reused |
| who-did-what (agent) | Competition-Model role assigner | Bates & MacWhinney (1989) Competition Model; MacDonald(1994) constraint satisfaction; Lewis & Vasishth(2005) cue-based retrieval; Centering (Grosz-Joshi-Weinstein 1995) + DuBois(1987) Preferred Argument Structure for the candidate set | owner-DONE, landed |

## The key finding: cue validities are REGISTER-SPECIFIC (the Competition Model's own prediction)

The Competition Model is explicit that a cue's weight in the argmax is its **validity in the ambient language/
register** (cue availability × reliability, MacWhinney 1987). This predicts that an assigner tuned on one
register need not transfer to another — and that is exactly what the modern gold reveals:

- **On 19c narrative fiction** (character-driven, multi-clause, non-canonical structure), the load-bearing lever
  was the candidate-SET decouple: the AGENT competes over the TRACKED/GIVEN discourse entities (DuBois PAS: the
  transitive agent is the given/pronominal argument; 79.4% of reachable gold agents are tracked). The CM stack
  went 0.041 → 0.69.
- **On modern edited prose** (news / how-to / interview / academic — GUM; and web UD-EWT), two things change:
  1. **Sentences are canonical SVO**, so WORD-ORDER — itself a high-validity Competition-Model cue in English —
     already suffices: a plain positional agent (nearest preverbal nominal) scores **0.855** on UD-EWT and
     **0.704** on GUM. Gold agent = `nsubj` ≈ nearest-preverbal-nominal by construction in a fixed-word-order
     language, so position is a NEAR-CEILING cue on this register.
  2. **The tracked-set prior REVERSES sign on modern prose**: the DuBois-PAS candidate-set decouple — the
     load-bearing lever of the 19c win (cm_dense 0.082 << cm_tracked 0.252) — **flips** on modern discourse:
     on GUM (n=15738) cm_dense **0.719** > cm_tracked **0.634** (cm_tracked − cm_dense = −0.084 CI-sep). The
     tracked-set restriction HURTS: modern multi-genre agents are frequently new/one-off entities
     (organizations, "you", first-mention referents), so restricting to the given set forfeits them. Both
     remain far below the positional floor **0.829**. This sign-reversal of the 19c lever is the single
     cleanest demonstration that the assigner's winning configuration is register-specific.

So the 19c-tuned full competition **underperforms position on modern** (UD-EWT full_cm 0.758 vs positional 0.855;
a dev re-sweep only reaches 0.780). This is NOT a defect in the CM assigner — it is the Competition Model working
as specified: the optimal cue weighting and candidate set are register-dependent, and modern canonical prose is a
register where the word-order cue dominates.

## The brain-foundational way to at-least-match position on modern: the hybrid-override design

The same organ already solved this shape for the PATIENT: `hybrid_role_patient` keeps `resolve_patient`
byte-identical on canonical/confident inputs and invokes the graded competition ONLY where a MARKED override cue
fires. Ported to the AGENT (`hybrid_agent_pick`, prototyped here): keep the positional (word-order) default on
canonical clauses; override to the competition ONLY on (1) PASSIVE (voice flip to the by-phrase), (2) a
PP-GOVERNED positional pick (core-argument cue), (3) a NON-NOMINATIVE pronoun (case cue). This recovers most of
the gap (UD-EWT 0.758 → 0.832) and preserves the competition's win on the non-canonical slice (passives 0.062 →
0.125), though on modern sentence-level gold it still sits just under the near-ceiling positional floor
(-0.022 CI[-0.034,-0.011]) because modern edited sentences have too little non-canonical structure to exploit.

## Where the CM assigner DOES win on modern: the non-canonical slice + the cross-consumer

The assigner's brain-foundational value on modern text is concentrated where position is WRONG:
- **Passives** (UD-EWT n=16): position 0.062 → CM/hybrid 0.125 (position grabs the surface subject = patient).
- **The coref entity-KB hard-link** (a DIFFERENT consumer): brain-foundational (gold grammatical) roles beat
  the live POSITIONAL role proxy **+0.084 CI[+0.031,+0.130]** on GUM — so the SAME upstream role assigner that
  who-did-what needs ALSO lifts coreference (the owner's "revisit other consumers to use the newly-optimized
  upstream", measured on modern gold; matches the sibling's −0.084 positional cost).

## The methodological conclusion (the point of the 19c ban)

The impressive 19c who-did-what AGENT result (0.69) is a **register artifact**: on modern gold a dumb positional
floor already wins, and no faithful competition variant beats it CI-separated on canonical modern prose. This is
a decisive, located vindication of the 19c ban for this dimension — the ruler was measuring a capability the
modern register does not stress. The discriminating agent instrument lives in NON-CANONICAL structure (passives,
fronting, embedded clauses) and in discourse-level coref (the cross-consumer), which modern edited single-sentence
corpora under-represent — a named follow-on (a non-canonical modern who-did-what gold).

## PINNED vs OUR-INVENTION (labelled)

- PINNED: DRT file-change referent; ACT-R activation; Ariel accessibility; Competition Model additive cue
  integration = Bayesian posterior (McClelland 2013); Centering / DuBois PAS candidate set; word-order / animacy
  / voice / case cues.
- OUR-INVENTION-UNDER-TEST (swept, not adopted): the validity-seeded cue weights (AGENT_VALIDITIES) — SWEPT here
  on a modern dev split (does not generalize → register-specific, reported not adopted); the hybrid-override gate
  (mirrors the proven `hybrid_role_patient` design); the salience/first-mention floors.

## Citations
Bates & MacWhinney 1989 (Competition Model); MacWhinney 1987 (cue validity); MacDonald 1994; Lewis & Vasishth
2005; McClelland 2013; Grosz, Joshi & Weinstein 1995 (Centering); DuBois 1987 (Preferred Argument Structure);
Bornkessel-Schlesewsky & Schlesewsky 2006 (eADM actor-first); Heim 1982 / Kamp (DRT file-change); Ariel 1990
(accessibility hierarchy); Anderson (ACT-R base-level activation); Zwaan & Radvansky 1998 (situation model).
