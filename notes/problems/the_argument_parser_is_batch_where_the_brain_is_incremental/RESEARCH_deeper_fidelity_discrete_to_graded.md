# Deeper fidelity drill (owner-requested 2nd pass, 2026-08-27): is the incremental builder brain-faithful, and what to optimise?

Read-only literature drill (routed to the `research` agent) + my own empirical tests. FOR THE STRATEGY SESSION:
this identifies a SUBSTRATE-WIDE fidelity direction (discrete -> graded) that is bigger than this one problem;
the recommendation at the bottom is to open it as its OWN problem, gated behind the p1 meaning-quality ceiling.

## The verdict: PARTIALLY brain-faithful; the one deep gap is DISCRETE vs GRADED

Faithful already: eager left-to-right commitment, verb-slot projection, Now-or-Never bounding, and the
structure-building / role-binding SEPARATION (Beber 2025). NOT faithful: the builder makes HARD binds where the
brain does graded, probabilistic, parallel constraint-satisfaction.

## Literature findings (tags: [PINNED]=copy, [UNPINNED]=sweep/invent)

**1. GRADED vs DISCRETE attachment [PINNED].** Human incremental parsing is a parallel, graded, probabilistic
competition, not discrete-serial-with-reanalysis. MacDonald/Pearlmutter/Seidenberg 1994 (constraint
satisfaction, continuously varying strength); Trueswell/Tanenhaus/Kello 1993 (subcat effect is "graded,
reflecting preferences"); Tanenhaus 1995 / Spivey-Knowlton normalized-recurrence (continuous fixation
proportions); Levy 2008 (comprehension = a probability distribution over continuations; surprisal = log
probability-mass shift). **Lewis & Vasishth 2005** is the mechanistic bridge: chunks carry continuously
fluctuating activation; retrieval is a stochastic competition that LOOKS discrete exactly when the activation
GAP is large (discrete = the noise->0 limit). **This is the SAME shape of answer as role assignment** -> "discrete
-> graded" is a unifying substrate-wide direction, with a worked collapse rule (activation-gap threshold).

**2. VERB VALENCY / SUBCATEGORIZATION [PINNED, most solid].** Valency is a GRADED probability distribution over
frames, NOT integer arity. Trueswell 1993; Garnsey/Pearlmutter/Myers/Lotocky 1997 (DO/SC bias continuous,
verb-specific, interacts with plausibility); MacDonald 1994; **Jurafsky 1996** (P(subcat frame | verb), Bayesian
update -- a ready spec); Gahl & Garnsey 2004/2006 (frame frequencies continuous enough to affect pronunciation
duration). Predicts my under-generation bug exactly: discretizing a continuous frame distribution rounds away
low-but-real optional slots.

**3. HIERARCHY -- does it matter for ARGUMENT ID? [PINNED, two-part].** (A) For canonical order, flat/shallow
suffices: Frank & Bod 2011 (sequential LMs predict RT as well as hierarchical); Ferreira good-enough. (B) A flat
builder SYSTEMATICALLY fails on passives/object-relatives/clefts, mirroring HUMAN errors: Ferreira 2003 (normal
readers misassign roles on ~10-20% of plausible passives via the NVN=agent-first heuristic); Grodzinsky Trace
Deletion Hypothesis (Broca's aphasics lose movement traces, fall back to the same agent-first default, at chance
on passives/object-relatives, normal on canonical). **Do NOT build a stack parser for argument ID; add a cheap
non-canonical detector.**

**4. MULTIPATH / BEAM [PINNED qualitatively; width UNPINNED].** Franzluebbers/Hale 2024 (fMRI, EN+ZH): a
multipath surprisal regressor fits bilateral STG better than single-path. Hale 2018 (RNNG + beam search fits
EEG). Width not pinnable from available access; compatible with a continuous-activation account discretized into
a beam. For argument ID, value concentrates at genuinely ambiguous attachment points -> a small beam (k=2-3) ONLY
at close-call points, after graded scores exist.

**5. NOW-OR-NEVER chunk contents [PINNED].** What persists is an abstracted/compressed code, not raw input
(Christiansen & Chater 2016 chunk-and-pass; Futrell/Gibson/Levy 2020 lossy-context surprisal, an independent line
reaching the same claim). Lowest priority for this per-clause job; store CLOSED constituents as role-tagged chunk
objects for cross-clause reference.

## My empirical tests (QA-SRL, full-gold candidate-identification F1; measured this session)

Generic INCREMENTAL builder F1 ~0.66 (dev) / 0.6201 (dev+test n=28,149). I conditioned it on learned per-verb
valency in three progressively-more-faithful forms; NONE beats the generic builder:

| arm | what | F1 vs generic INCREMENTAL (n=28,149 dev+test) |
|---|---|---|
| VALENCY_INT | open round(learned pre/post arity) slots (discrete) | -0.0322 [-0.0351,-0.0293] BELOW (size 1.83) |
| VALENCY_GATE | drop objects only on strongly-intransitive verbs (P_post<0.3) | -0.0023 [-0.0028,-0.0018] BELOW (size 2.18) |
| VALENCY_GRADED | include object iff P_post(verb) x fit(noun, patient-centroid) > tau | -0.0628 [-0.0656,-0.0600] BELOW (size 1.50) |

Generic INCREMENTAL F1 0.6192 (size 2.20); mean gold 1.94; every valency arm CI-separated BELOW. Landed
reproducibly in `experiments/exp_incremental_valency_fidelity_v2.py` (self-test PASS + boot CIs; metrics in
`data/incremental_valency_fidelity_v2/`).

**Why the faithful (graded) fix loses here -- VERIFIED, not asserted (`exp_incremental_valency_wall_diagnostic_v2`,
per "decompose the wall, don't assert a ceiling"). The barrier is TWO-part, and my first "gated behind p1" note
was an OVER-SIMPLIFICATION:**
1. **SMALL task headroom (the binding limit).** A PERFECT object-inclusion decision (ORACLE_OBJ) beats the generic
   eager builder by only **+0.028 [+0.020, +0.036]** -- the generic "attach the nearest post-verbal nominal" is
   already near-ceiling on canonical English. Brain-foundational reason: English is a rigid word-order language,
   so word-order cue validity is highest and valency/semantic cues add little (Competition Model, Bates &
   MacWhinney) -- the SAME reason the front-end SOLVED found word order dominates. There is no big win here for ANY
   valency mechanism.
2. **WEAK fit signal (a real p1 symptom, but secondary).** cos(noun, patient-centroid) separates gold objects from
   non-gold post-verbal nominals at **AUC 0.59** only (frame-probability alone AUC 0.66). The coarse 12-dim space
   barely tells patient from non-patient, so even the small headroom cannot be captured by the semantic route
   (fit-only -0.11, frame-prob-only -0.04 vs the generic builder).

CORRECTED: NOT "graded would win big if p1 were fixed." On canonical English argument-ID the TASK is near-saturated
by eager word-order attachment (oracle +0.028), and the semantic signal is additionally weak (p1). The graded
direction's value is the non-canonical / freer-word-order / ambiguous tail, not canonical English argument-ID.

## Recommendation FOR THE STRATEGY SESSION

**Do NOT expand this solved problem to build graded attachment / beam now.** The reasons (verified):
1. On CANONICAL ENGLISH argument-ID the headroom is small: a PERFECT object decision beats the generic eager
   builder by only +0.028 (`exp_incremental_valency_wall_diagnostic_v2`). Word order already saturates the task
   (Competition Model). Graded attachment's value is the ambiguous / non-canonical tail, rare on QA-SRL.
2. The semantic-fit signal is weak (patient-centroid AUC 0.59; a p1 symptom) -- so even the small headroom can't be
   captured here. BUT this is SECONDARY: even a perfect fit gains only +0.028. So it is NOT "just fix p1 and graded
   wins big" -- the binding limit on canonical English is the TASK, not the representation.
3. "Discrete -> graded" is a SUBSTRATE-WIDE direction (parsing AND role assignment share it; Lewis-Vasishth is the
   shared collapse rule) -> it deserves its OWN problem, not solver scope-creep on this one.

**Proposed follow-up problem (strategy's call to open):** "the parser commits discretely where the brain competes
in graded activation" -- build graded-attachment (score-then-collapse on the best-vs-second activation gap,
Lewis-Vasishth) + a targeted k=2-3 beam at close-call points + graded frame-probability valency, and unify it with
the graded role-assignment finding (relcl) as one substrate-wide discrete->graded program. **TEST IT ON
NON-CANONICAL / FREER-WORD-ORDER / AMBIGUOUS populations** (passive, object-relative, garden-path; ideally a
case-marked / freer-order language where the Competition Model predicts valency/case cues carry real validity) --
NOT on canonical English argument-ID, where the verified oracle ceiling is only +0.028. A richer p1 representation
lifts the weak fit signal but is not the binding limit on canonical English. Ranked levers (highest first): graded
attachment -> graded valency/subcat -> targeted beam -> non-canonical detector (partly owned by relcl) ->
abstracted chunk buffer.
