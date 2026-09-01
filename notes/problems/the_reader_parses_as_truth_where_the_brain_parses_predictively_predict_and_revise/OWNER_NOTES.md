---
owner_verdict: DONE
---

NEXT PRIORITY PROBLEM — build the generative valence parser (the reader's EXACT mechanism)

slug: the_reader_assigns_roles_by_a_linear_cue_sum_where_the_brain_does_joint_generative_inference
priority: HIGH — this is the identified ceiling for who-did-what, and it caps SPACE, causation,
belief, and the situation model the learner grows on. Glass-box, NO external LLM at inference (the
invariant). A dedicated FOUNDATION build (a probabilistic generative parser).

THE PROBLEM (plain): our reader assigns "who did what to whom" with a bottom-up pipeline — POS-tag,
then find the verb, then combine cues (word order + animacy + selectional fit + constructions) as a
weighted SUM. The brain does something different in kind: JOINT GENERATIVE inference — it infers the
whole clause (word category + structure + roles) TOGETHER as the single most probable message given
the input, under a generative model. Our cue-sum is a known crude LINEAR APPROXIMATION of that joint
posterior, which is mathematically why it plateaus and why our tagger mis-reads verb/noun homographs.

WHAT IS ALREADY ESTABLISHED (inherit; do NOT re-derive — all measured this session, CI-separated,
reusing validated organs, both modern QA-SRL v2 and 19c LitBank):
- who-did-what recall gap to human (~0.95) decomposes: correct 0.481 / WRONG-BIND 0.309 / DROPPED
  0.114 / EXTRACTION-MISS 0.096; every error is recoverable in principle (gold present, oracle 1.0).
- DROP-FILL (recover the argument the parse left empty) is robust + era-general: reusing the
  validated hdlab.relcl_resolver lifts recall to ~0.55 modern / ~0.30 on 19c. RE-SELECTING committed
  picks does NOT generalize (era-fragile). Recover-the-missing generalizes; second-guess-the-commit
  does not.
- The validated Competition-Model organ hdlab.graded_role_assigner (routed cue-integration) reaches
  0.6076 modern (best), beating a hand-rolled flat integrator (routing > flat replacement).
- The plateau is NOT cue quality: a billion-token role-separated distributional selectional model
  (GloVe) only TIES a coarse 12-d grounded one on modern and is WORSE on 19c. Fit quality is not the
  lever; WORD-ORDER DOMINANCE + PARSE + combination-architecture are.
- EXTRACTION-MISS is 71% verb/noun homographs mis-tagged NOUN ("clay FORMS mud") because we commit
  POS before structure; a structure-aware predicate slot recovers ~+0.023.
- DECISIVE MECHANISM TEST: holding cues fixed and swapping ONLY the combination rule (linear sum ->
  reliability-weighted joint posterior) made it WORSE (-0.016 modern / -0.033 on 19c) — because a
  valid posterior needs CALIBRATED generative likelihoods; miscalibrated heuristics multiplied let a
  wrong cue VETO the right answer. => the generative model CANNOT be shortcut by reweighting cues.

THE EXACT MECHANISM (research drill, 17 papers; the build to replicate, glass-box, no LLM):
- COMPUTATIONAL: infer argmax over (category, structure, roles) of P(structure)·P(fillers|role,verb)
  ·P(observed string | intended, noise) — a valence/structural PRIOR (Jurafsky 1996; Levy 2008) x a
  selectional LIKELIHOOD (McRae 1998) x a NOISE model (Gibson/Bergen/Piantadosi 2013).
- ALGORITHMIC: incremental left-corner / PLTAG-style parser (Demberg & Keller) maintaining a BEAM of
  joint (category, structure, role) hypotheses scored by joint log-probability, word-by-word
  (analysis-by-synthesis; Hale 2001 surprisal = belief-mass shift). Resource-bounded -> "good-enough"
  errors emerge naturally (Ferreira 2003), not a different computation.
- IMPLEMENTATIONAL: explicit role-filler BINDING (agent/patient distinct, position-independent;
  Frankland & Greene 2015) = tensor-product/VSA binding (Smolensky) — the substrate ALREADY has FHRR.
- THE BUILD: a lexicalized generative grammar with valence/argument slots, trained on a role-labeled
  treebank (PropBank/OntoNotes) — inspectable counts, no LLM; decode by the incremental beam parser;
  repurpose the existing selectional-fit model as the LIKELIHOOD term INSIDE the posterior (NOT an
  independent cue); add a noisy-channel correction layer. Category/attachment/role fall out of ONE
  MAP derivation — never committed independently (so "forms" is never a noun in the predicate slot).

THE BAR: PASS = the joint-generative parser recovers who-did-what CI-separated over the strongest
real floor actually run (the validated graded_role_assigner routed Competition-Model organ, 0.6076
modern) on held-out + MODERN + 19c prose, AND (a) definitionally eliminates the predicate-slot
homograph mis-tag class, AND (b) its residual errors pattern-match HUMAN errors (garden-path-shaped,
plausibility-driven, lingering-misassignment — Ferreira/Christianson), not the discriminative model's
error shape. Report CI half-width + null beside every margin; info-free twins LOSE (shuffled grammar
/ shuffled likelihood). A rigorous NEGATIVE is a full PASS if located: build it at the SAME
information content as the cue-sum and if it STILL plateaus at ~0.61 with the SAME error distribution,
the ceiling is DATA/information, not the generative-vs-discriminative architecture — which itself
resolves the open question.

SCOPE: may write experiments/, verification/, notes/problems/<slug>/. May NOT write hdlab/ (Q111 —
strategy lands; state the proposed default-off wire in SOLVED.md), preregs/**, arm_key*.
data/foundation/ read-only. Reuse where organs exist: FHRR role-filler binding, graded_role_assigner,
graded_competition, predictive_reader, relcl_resolver, the pos_tagger/arc_parser assets. THE DISK
OUTRANKS THE BRIEF.

WHY NOW: every cheaper lever is exhausted and measured — drop-fill (done), construction fixes
(era-fragile), richer selectional cues (tie/lose), combination-rule swap (worse). The blowout from
0.61 to ~0.95 is gated on this ONE mechanism, and the cheap-shortcut negative proves it must be
built, not approximated. This is the exact, brain-faithful answer to the reader's parse-as-truth
thesis: hold a distribution over structures and infer the intended one — generatively.
