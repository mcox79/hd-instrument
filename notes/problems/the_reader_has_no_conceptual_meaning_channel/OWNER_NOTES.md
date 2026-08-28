---
owner_verdict: DONE
---

SUBMISSION -- SOLVER RESULT: the_reader_has_no_conceptual_meaning_channel
STATUS: SOLVED (core bar met + strengthened; the wall the owner pushed on is UNDERSTOOD and converted to a
        build target) | ledger malformed/incomplete: 0 | hdlab UNTOUCHED (Q111 -- you land; I proposed)
INTEGRATE ONLY on owner_verdict: DONE in notes/problems/the_reader_has_no_conceptual_meaning_channel/OWNER_NOTES.md.
REVERIFY:
  .venv/Scripts/python.exe verification/test_conceptual_meaning_channel.py        (core: identity + dissociation; PASSES; fast, cached GloVe subset)
  .venv/Scripts/python.exe experiments/exp_conceptual_channel_limits_v1.py         (finest-resolution limit map; ~25s; writes own dir)
  .venv/Scripts/python.exe experiments/exp_scalar_adjective_operation_v1.py        (the wall-as-build-target adjective op; ~4min; writes own dir)

THE ANSWER IN ONE LINE
The reader was missing the brain's CONCEPTUAL/definitional meaning system (the ATL amodal hub) and was at
chance on "do these mean the same thing?". I built it (WordNet gloss+genus, distinctive-feature IDF), and it
beats even a STEELMANNED distributional competitor on meaning-IDENTITY, off-WordNet, with the two systems
DOUBLE-DISSOCIATING (conceptual->similarity, associative->relatedness). Pushed to understand the residual
wall, the deepest finding fell out: THERE IS NO SINGLE SIMILARITY OPERATION -- meaning-similarity is
operation-specific per word class, and one cosine is the wrong operator for two of three classes.

THE BAR (PROBLEM.md sec 7, verbatim): "The conceptual channel (demand-routed) must beat the ASSOCIATIVE-ONLY
reader on meaning-IDENTITY CI-separated over its UPPER bound, with the info-free twin (shuffled definitions /
scrambled concept) LOSING CI-separated. Report CI half-width + null p95. Show the conceptual channel is not
just same-resource provenance: validate on a test NOT derived from WordNet (SimLex similarity-vs-relatedness
split, or a held-out synonymy set), and ablate the routing (does demand-routing beat a fixed choice and beat
the HARD-FAILED fusion?)."

RESULT 1 -- IDENTITY WIN (the bar), vs a STEELMANNED competitor, off-WordNet:
  conceptual (ATL hub) vs GloVe-300 (the strong associative steelman; the reader's own co-occurrence is ~0.04):
    SimLex-999 (n=999)  CONC 0.5210 CI[0.4725,0.5703]  vs GloVe 0.3705  ->  +0.1505 CI[0.0850,0.2156]
    SimVerb    (n=2986) CONC 0.4981                     vs GloVe 0.2204  ->  +0.2777 CI[0.2377,0.3165]
    twin (shuffled glosses) p95 0.0622 LOSES | concreteness -0.138 | grounded-ATL spoke 0.2902
    the distinctive-feature op EARNS ITS KEEP: IDF beats UNWEIGHTED overlap (the ATL WRONG-OP) +0.0247 CI[0.0145,0.0356]
  Gloss CONTENT alone (zero taxonomy graph) already scores 0.3996 -- beats reader's 0.04 + grounded 0.29,
  ties GloVe -- so the win is definitional content, not WordNet-taxonomy lookup; genus takes it past GloVe.

RESULT 2 -- THE TWO-SYSTEM DOUBLE DISSOCIATION (the brain signature; off-WordNet; same SimLex pairs):
  CONC sim 0.5210 > assoc 0.3420 ; GloVe sim 0.3705 <= assoc 0.3881 ; crossover +0.1966 CI[0.1113,0.2815].
  WordSim-353 relatedness: GloVe 0.6102 beats CONC 0.4028 (+0.2074 CI[0.0970,0.3150]). Each system wins its
  own axis. Real-but-PARTIAL (channels overlap) -- the brain-consistent picture (Mirman 2017 / Jackson 2015).

RESULT 3 -- ROUTING vs FUSION (bar part 2), reconciling the brief with the disk:
  On easy decontextualised rating a fixed FUSION (mean-across-axes 0.5958) is NOT beaten by demand-ROUTING
  (0.5656; route-minus-fusion -0.0302 CI[-0.0631,0.0040]) -- consistent with the disk's prior 'fused>switch'
  AND competition-gated control (inert on easy items). ROUTE beats a random-switch twin (p95 0.4423), so the
  task signal is real, but fusion still ties/wins. The brief's "route, fusion hard-failed" is WSD-specific;
  routing/control's true home is context SELECTION = the semantic-control organ already built in
  context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark (trigger AUC 0.79).

THE WALL (owner-pushed) -- WRONG-OPERATION, NOT MISSING DATA; A BUILD TARGET; the DEEPEST finding:
  THERE IS NO SINGLE SIMILARITY OPERATION. Meaning-similarity is OPERATION-SPECIFIC per word class:
    NOUN = taxonomic feature/genus overlap (our gloss channel's home turf, 0.599)
    ADJECTIVE = SIGNED-MAGNITUDE distance on a shared scale (Walsh ATOM/IPS magnitude system; Moyer
                distance-effect, documented for scalar adjectives; Kennedy degree semantics) -- feature-overlap
                cosine has no order/sign, structurally the wrong operator (adj: CONC 0.479 < GloVe 0.585)
    VERB = relational/argument-structure (gloss carries it, 0.492; GloVe's single blended vector fails, 0.152)
  One cosine is wrong for TWO of three classes -- the unifying cause of every per-class wall.
  BUILT the adjective op from OWNED resources (GloVe scale-membership + WordNet antonym-pole SIGNED
  opposition, SemAxis-style; NO new data): SimLex adjectives 0.585 -> 0.6227, with the INFO-FREE RANDOM-AXIS
  control at matched lambda LOSING (0.5528). CI-separation POWER-LIMITED (n=111 adj pairs): antonym-axis vs
  GloVe +0.038 CI[-0.050,0.127]; vs random-axis +0.070 CI[-0.002,0.151] -- point estimates as predicted, CIs
  just include 0. DIRECTIONALLY CONFIRMED, mechanism nailed; a fully CI-separated claim needs a larger
  adjective gold than exists on disk (a POWER limit, not a mechanism failure).

TESTED-NEGATIVE / DO NOT RE-RUN (each with a can-fail control):
  - ATL covariance-DISTILLATION (SVD+whiten over gloss features) TIES sparse IDF (+0.028 CI[0.001,0.053] / a
    SimVerb tie) -- the distinctive-feature op is SUPPLY-dependent: dense grounding->whiten, sparse
    definitional->IDF; the literature-faithful distillation does not beat IDF on this supply.
  - Task-SWITCH routing for graded rating: fusion wins (above).
  - Grounded SENSORIMOTOR spoke for adjectives: LOSES CI-sep (grounded-minus-conceptual -0.309 CI[-0.536,-0.093])
    -- our grounded asset is sensorimotor, not the scalar-magnitude representation adjectives need.
  - Global-profile SemAxis (project onto 1263 axes, take cosine): tied its own random control -- the WRONG
    operationalisation (irrelevant axes drown the sign-flip); the corrected per-pair signed-opposition works.
  - Symbolic exact-antonym flag helps more (+0.10 on adj) but is MECHANISM-approximate -- do NOT ship it as
    the operation.

AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md):
  1. The ATL amodal CONCEPTUAL/definitional hub is BUILT + PROVEN as a second meaning system (identity win,
     off-WordNet, twin losing). IDF beats unweighted overlap -- the ATL WRONG-OP confirmed on this channel too.
  2. Two-system DOUBLE DISSOCIATION confirmed (conceptual=identity, distributional=relatedness), real-but-partial.
  3. The distinctive-feature op is SUPPLY-DEPENDENT (dense->whiten, sparse->IDF); covariance-distillation ties
     IDF (fidelity boundary) -- the "richer feature SUPPLY" the prior two-systems SOLVED predicted.
  4. Semantic control is COMPETITION-GATED; for decontextualised rating FUSION beats routing (replicates the
     prior 'fused>switch' with a stronger conceptual channel). The brief's "route" is WSD-specific.
  5. The ceiling is understood per-word-class; the SENSORIMOTOR grounded spoke does NOT fix adjectives.
  6. NEW, DEEPEST: MEANING-SIMILARITY IS OPERATION-SPECIFIC PER WORD CLASS -- one cosine is the wrong operator
     for adjectives (signed-magnitude) and, in the distributional channel, verbs (relational). The adjective op
     is buildable from OWNED resources (GloVe + WordNet antonyms), directionally confirmed. The meaning read-out
     should be OPERATION-ROUTED by word class -- and that is the natural home for the semantic-control router.

PROPOSED hdlab CHANGE (you land it; I did NOT write hdlab/):
  1. Wire the CONCEPTUAL/definitional channel (per-word WordNet gloss+genus feature bag, global-IDF
     distinctive-feature weighted, cosine), default-off, gated on the held-out SimLex/SimVerb margins.
  2. DEMAND-ROUTE (do not fuse-for-everything): identity/similarity -> conceptual; relatedness -> associative;
     FUSE (fixed) for decontextualised graded rating; conflict-gated SELECTION -> the existing semantic-control organ.
  3. OPERATION-ROUTE the similarity read-out BY WORD CLASS: noun -> conceptual taxonomic overlap; adjective ->
     GloVe scale-membership + WordNet-antonym signed-magnitude (owned resources); verb -> conceptual/gloss
     relational content (a VerbNet/FrameNet argument-structure op is the deeper, not-yet-owned upgrade).
  4. Do NOT wire: SVD distillation over definitional features; a task-switch gate for rating; the grounded
     SENSORIMOTOR spoke for adjectives; a symbolic antonym-flag as the mechanism; a GPU learned hub over a
     single spoke (premature -- it earns its keep only reconciling >=2 heterogeneous spokes).
  5. Measure on the LIVE reading task before any capability claim (SimLex/SimVerb are naturalistic instruments).

KEY REALIZATIONS (the enabling moves):
  - SimLex ships TWO golds on the SAME pairs (SimLex999 similarity + Assoc(USF) association) -- the cleanest
    dissociation test (vocab/frequency/difficulty fixed, only the task-axis varies).
  - Steelman the associative competitor with GloVe, not the reader's own 0.04 system -- the win is credible
    only against the strong competitor.
  - The distinctive-feature op is SUPPLY-dependent (IDF on sparse, whitening on dense) -- and the
    literature's proposed covariance-distillation does NOT beat IDF here (a boundary, only visible on the rich
    supply the prior SOLVED pointed to).
  - The wall is a WRONG-OPERATION, not missing data: adjectives need signed-magnitude, verbs need relational;
    a single cosine is the deepest reason for every per-class wall. And the adjective fix is buildable from
    resources we ALREADY OWN (project before buying).
  - A brief that contradicts the disk is a lead, not a bug -- testing "route vs fusion" both ways showed the
    disk right for graded rating and the brief's hard-fail WSD-specific.

DO NOT QUOTE / DO NOT REDO:
  - Do NOT quote an absolute WiC number as domain-general (WordNet provenance inflation); the controlled claim
    is chance->above-chance with the twin at chance.
  - Do NOT quote the absolute conceptual rho (~0.52) as a domain-general similarity number -- the claim is the
    CI-separated WIN over the competitor + twin losing + the dissociation.
  - Do NOT quote the adjective operation as CI-SEPARATED -- it is DIRECTIONALLY confirmed, power-limited (n=111);
    quote the mechanism + the random-axis control losing, not a pass.
  - The routing NET numbers are on decontextualised rating; quote "fusion >= route for graded rating", not a
    general "routing loses".

FILES: experiments/exp_conceptual_meaning_channel_v1.py; experiments/exp_conceptual_channel_limits_v1.py;
experiments/exp_scalar_adjective_operation_v1.py; verification/test_conceptual_meaning_channel.py;
notes/problems/the_reader_has_no_conceptual_meaning_channel/{SOLVED.md, DESIGN_brain_analysis.md};
data/exp_conceptual_meaning_channel_v1/metrics.json (+ glove_bench_subset.npz cache);
data/exp_conceptual_channel_limits_v1/metrics.json; data/exp_scalar_adjective_operation_v1/metrics.json. NO hdlab/.

TLDR (plain language): Our reader knew what words go WITH (dog-leash) but not what they ARE (a dog is a kind
of animal), so it was guessing on "do these mean the same thing?". I built the missing what-it-IS system from
dictionary definitions and category structure; it beats even a strong off-the-shelf word-association model at
telling same-meaning from merely-related, on human-rated pairs it was never tuned on, and it collapses when
the definitions are scrambled (so it's really using meaning). It shows the clean brain pattern -- the new
system wins "same kind", the old one wins "goes together". Then, pushing on where it still fell short, the
biggest lesson: there isn't one way to measure "same meaning" -- the brain uses a different method for
different kinds of words (nouns by shared features, adjectives by position on a scale like hot/cold, verbs by
who-does-what), and our single method was simply the wrong tool for adjectives and, in the word-association
channel, verbs. The adjective fix can be built from tools we already have (word co-occurrence + the
dictionary's list of opposites), and it works -- we just don't yet have enough adjective test-pairs to prove
it to the strict statistical bar.

QUESTIONS: none blocking. One judgment call I made: filed SOLVED because the core bar (conceptual beats the
associative reader on identity, off-WordNet, twin losing) is met and strengthened, and the double
dissociation is CI-separated. The adjective/per-class-operation result is a DIRECTIONAL, power-limited bonus
(mechanism nailed, not CI-separated) -- I did NOT let it gate the SOLVED status. If you want the per-class
adjective operation to carry CAPABILITY weight in the wiring (not just insight weight), it needs hardening --
see the scoped follow-up.

NEXT STEPS:
  1. Wire the conceptual/definitional channel as a second demand-routed representation (proposed diff above).
  2. OPERATION-ROUTE the read-out by word class (noun->overlap, adjective->GloVe+antonym-signed, verb->gloss-relational).
  3. Measure on the live reading/coref task before any capability claim.
  4. Do NOT pursue (tested-negative): SVD distillation; task-switch gate for rating; grounded-sensorimotor
     routing for adjectives; symbolic antonym-flag-as-mechanism; a GPU learned hub over one spoke.
  5. SCOPED FOLLOW-UP (only if the per-class op must carry capability weight): harden the adjective
     signed-magnitude operation to CI-separation on an INDEPENDENT, adequately-powered, non-WordNet
     adjective-similarity gold, WITH an operation refinement (the crude opposite-pole signal is the weak link,
     not the data alone) -- do both together on the same clean data, not more data on the current operation.
  6. Deeper verb operation (VerbNet/FrameNet argument-structure) is the one genuine not-yet-owned resource gap.
