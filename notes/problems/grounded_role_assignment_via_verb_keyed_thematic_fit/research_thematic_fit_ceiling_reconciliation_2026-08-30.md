# Research drill: RECONCILE "embeddings are a bad fit for thematic fit" (prior drill) with clean GloVe-0.65

Problem: grounded_role_assignment_via_verb_keyed_thematic_fit
Date: 2026-08-30
Type: ONLINE literature drill (NO experiments run). Resolves a discrepancy between two of our own artifacts.
Builds on / audits:
  - research_feature_based_role_generalization_2026-08-30.md  (claimed: features >> distributional;
    cited LREC-2020 + McRae norms; its empirical premise was "GloVe = 0.51 = chance")
  - research_thematic_fit_disambiguation_regime_2026-08-30.md  (established: fit is competition-gated,
    prototype-not-lookup; that stands and is NOT re-derived here)

THE DISCREPANCY (as handed to this drill):
  Prior drill: general bag-of-words distributional semantics CANNOT predict thematic role for a novel
    argument (GloVe ~0.51 = chance), so build a FEATURE/grounded fit vector.
  Fresh clean measurement (ours): a balanced logistic classifier, BALANCED accuracy, chance 0.50,
    held-out OOV nouns, modern role-balanced agent/patient gold ->
      GloVe-300 verb-conditioned (verb+noun+interaction) = ~0.65   (noun-only ~0.59)
      info-free twin                                        = ~0.48
      WordNet feature vec (animacy + IS-A concreteness + 15 supersenses) = ~0.51-0.57  (WORSE than GloVe)
      animacy-alone                                         = ~0.54
    The earlier "GloVe = 0.51 = chance" was a MEASUREMENT ARTIFACT: an UNBALANCED classifier predicting
    the majority class. So on OUR data distributional carries MODERATE generalising role signal and BEATS
    our coarse feature vector -- the OPPOSITE of the prior drill's strong claim.

Prior-work check (mandatory): experiment_index.py "thematic fit" -> 3 cells; "selectional preference"
  -> 11 cells (10 landed). Load-bearing priors: exp_pivot_selectional_knowledge_richness_2afc_v1 =
  HARD_PASS_KNOWLEDGE_POVERTY_WAS_THE_WALL (2026-07-23); the propara selectional-preference probes =
  HARD_FAIL_NO_GENERALIZATION (2026-08-11). Both are consistent with the verdict below (a coarse
  distributional signal exists but does not generalise far; richness/structure is the wall).

=====================================================================
RECONCILIATION VERDICT UP FRONT
=====================================================================
The two artifacts DO NOT genuinely contradict. The apparent conflict is (a) a TASK + METRIC confound and
(b) a PARTIAL MISCITATION of LREC-2020 in the prior drill, sitting on top of (c) a now-corrected
measurement artifact.

  GloVe-0.65 is CONSISTENT with the literature. The classic "embeddings are weak for thematic fit"
  result is measured on GRADED plausibility judgments (Spearman rank correlation of model score vs
  averaged human rating on verb-role-filler triples: Pado, McRae, Ferretti, DTFit). MY task is a COARSE
  BINARY agent-vs-patient decision (balanced accuracy). Those are different scales and different
  difficulties. The coarse binary task is DOMINATED BY ANIMACY, which embeddings encode well, so ~0.65
  balanced accuracy is the EXPECTED result, not an anomaly.

  The prior drill's strong claim -- "features >> distributional, so bag-of-words fits thematic fit
  WEAKLY" -- is OVERSTATED. LREC-2020's actual conclusion is that the determinant factor is reliable
  SYNTACTIC information (dependency-typed distributional space), NOT grounded features per se. The
  published wins over bag-of-words come from SYNTAX-TYPED STRUCTURE, by MODEST margins, and NO
  representation (embeddings, structured DM, or BERT) exceeds ~0.6-0.7 Spearman on these benchmarks. The
  "features beat 300-d embeddings on role generalisation" claim is a HYPOTHESIS, not a measured result.

  Net: distributional carries MODERATE role signal (true, ~0.65 coarse / ~0.4-0.6 graded); it is not
  "weak-to-zero" (the prior drill overstated) and it is not "strong/sufficient" (it plateaus well below
  human agreement, and most role info is STRUCTURAL not noun-intrinsic -- see SQ2). Both of our artifacts
  were partly right and each overstated in opposite directions.

=====================================================================
SQ1 -- Reconcile LREC-2020 "embeddings weak" with GloVe-0.65. What is the real SOTA + ceiling?
VERDICT: task/metric confound + partial miscitation. PINNED with numbers.
=====================================================================
KEY: the benchmark task is GRADED, mine is BINARY-COARSE. Different metric (Spearman rho vs balanced acc),
different difficulty. Do not compare 0.51-rho to 0.65-acc as if they were the same axis.

Best embedding-based Spearman on the standard GRADED thematic-fit benchmarks (tuned GloVe; Wittenberg/
"Where's the Learning..." arXiv:2208.04749, Table 4 -- FIRMLY CITABLE, extracted from source):
    Pado                 0.5855
    McRae                0.4338
    GDS (Greenberg)      0.5467
    Ferretti-Locations   0.3410
    Ferretti-Instruments 0.3853
    Bicknell             0.6094
Interpretation: in ABSOLUTE terms these are MODERATE correlations (0.35-0.61), not "weak-to-zero." "Weak"
in the prior drill's sense is only relative to an ideal the field never reaches. Nobody clears ~0.6-0.7 on
these datasets -- structured DMs (SDM, Chersoni et al. 2019) and transformers (BERT, "Did the Cat Drink
the Coffee?", Pedinotti et al. 2021) cluster in the SAME 0.6-0.7 band as tuned embeddings on the easier
DTFit typical-vs-atypical contrast, and lower on Pado/McRae. So the ceiling is modest FOR EVERYONE, and a
0.65 balanced accuracy on the EASIER coarse binary task is fully consistent with this.

What LREC-2020 (Chersoni, Pannitto, Santus, Lenci, Huang 2020) ACTUALLY concluded (verified via ACL
abstract + code repo ellepannitto/tfe): the title is a rhetorical REBUTTAL. Its finding is "a determinant
factor for the performance seems to be the availability to the model of reliable SYNTACTIC information."
i.e. dependency-typed embeddings are competitive; the winning axis is SYNTAX/RELATIONAL structure. This is
a STRUCTURE story, NOT a grounded-FEATURES story. The prior drill used this paper to support "grounded
features >> distributional," which the paper does not establish -- it establishes "syntax-typed
distributional > bag-of-words distributional," by modest margins. FLAG THIS as an over-claim in the prior
drill's citation chain.

WHY the coarse binary task is easy for embeddings (so 0.65 is expected): coarse agent/patient ~ animacy.
Corpus base rates: ~89-90% of direct objects (patients) are inanimate; transitive subjects (agents) are
predominantly animate. Supervised linear probes extract animacy from embeddings at ~90% accuracy. So a
supervised classifier riding GloVe recovers the dominant (animacy + verb-selectional) component of the
coarse role decision as a matter of course.

STRONG CAVEAT (pulls toward "noun-side is near a modest ceiling"), arXiv:2208.04749's headline finding:
RANDOM embeddings perform AS WELL AS pretrained embeddings once the embedding is TUNED during training
(the gap closes almost completely on most of the six datasets). Read literally: the pretrained
distributional SEMANTICS contributes little BEYOND task structure once you supervise -- the signal a
supervised classifier rides is largely task-structural (animacy prior, verb-argument regularities of the
training verbs), not deep distributional world-knowledge. This is a direct warning that the NOUN-SIDE
representation is not where the leverage is, and that swapping GloVe for a richer noun vector may not move
the number much.

=====================================================================
SQ2 -- How much role info is in the ARGUMENT (noun) alone vs the VERB-CONSTRUCTION / structure?
VERDICT: MOST role info is STRUCTURAL, not noun-intrinsic. PINNED (converging psycholinguistics + our own numbers).
=====================================================================
Our own numbers already answer this on a ROLE-BALANCED gold (the key control): animacy-alone = 0.54
(near chance), GloVe verb-conditioned noun-side = 0.65. On a balanced set (where agents and patients are
NOT trivially separable by animacy), the noun-INTRINSIC role signal is WEAK and the noun-side tops out
around 0.65. That directly implies the bulk of role information lives in STRUCTURE (word order +
morphology/voice + the grammatical relation), not in the argument identity.

Converging evidence this is correct, not a quirk of our gold:
- Competition Model (Bates & MacWhinney; MacWhinney): English has the HIGHEST cue validity on WORD ORDER;
  animacy is a lower-validity cue in English (it dominates in e.g. Chinese, not English). So in English a
  noun-intrinsic (animacy) signal SHOULD be a weak standalone role cue -- exactly 0.54.
- Reversible-sentence literature (l-IPS rTMS, Reversible/irreversible comprehension; "the child the apple
  eats"): when both nouns are plausible agents (reversible), noun plausibility CANNOT assign the role and
  STRUCTURE must carry it; the l-IPS is specifically recruited to assign roles in reversible sentences.
  Role assignment is a structural computation that noun features only MODULATE.
- Prior disambiguation drill (this problem): thematic fit is COMPETITION-GATED -- decisive only where
  structure is ambiguous/conflicting; on clean structure it contributes ~0. So the noun-side fit signal's
  JOB is to break ties UNDER CONFLICT, not to carry role assignment in general.

STRATEGIC UPSHOT: the lever is the STRUCTURE/PARSE + the conflict/surprisal recruitment GATE (already the
problem's target), NOT a richer noun-side fit vector. This matches PROBLEM.md's own scoping note
("INVERSION stays hard even for fit, 0.21 -- it is a PARSE problem") and "conflict-validity is a GATE,
not a weight."

=====================================================================
SQ3 -- Do RICH grounded norms (Lancaster 40k x 11; Binder 65-dim) BEAT 300-d embeddings on
       thematic-fit / selectional-preference generalization? Is there MEASURED headroom?
VERDICT: THIN / UNPROVEN for this task. Some dimension-level headroom exists; a task-level win over embeddings is a HYPOTHESIS.
=====================================================================
Honest state of the evidence:
- Chersoni et al. 2021, "Decoding Word Embeddings with Brain-Based Semantic Features" (Computational
  Linguistics 47(3)): word2vec/GloVe encode SOME Binder dimensions well (concreteness, motion/action,
  size, spatial) and OTHERS less well (social / affective / animacy-sentience are reported harder to
  decode). This argues there IS dimension-level complementary information in brain-based norms on exactly
  the social/animate/affective axes role assignment cares about.
  >> CAVEAT / PARTIALLY-PINNED: this specific "animacy not robustly decodable" reading came from a
     fast-model summary of the PDF (the PDF did not machine-parse cleanly), and it is in TENSION with the
     ~90% supervised animacy-probe result in SQ1. The resolution is almost certainly the DIFFERENCE
     between (a) regressing the graded continuous Binder dimension (harder) and (b) a supervised binary
     linear probe (easy). Treat "embeddings miss animacy" as PARTIALLY-PINNED; do NOT lean on it as a
     strong claim. The safe claim: embeddings capture the coarse animacy/type split a binary role task
     needs; whether the fine graded social/affective residual helps role assignment is untested.
- Lancaster Sensorimotor Norms (Lynott et al. 2020): modality-specific norms OUTPERFORM concreteness and
  imageability on lexical-decision/naming. That is a real strength -- but it is NOT a demonstration that
  they beat 300-d embeddings on thematic fit or selectional preference. That specific comparison is, to
  this drill's search, UNTESTED.
- Our own datapoint is the most direct evidence available and it cuts AGAINST rich-features-win on THIS
  task: a coarse WordNet feature vector (animacy + concreteness + 15 supersenses) scored 0.51-0.57, WORSE
  than GloVe-0.65. This does NOT prove "features can't beat embeddings" -- it proves a WEAK, 17-dim
  DISCRETIZED feature vector loses to a tuned 300-d supervised space (the discretization throws away the
  continuous type-gradation and the verb x noun interaction that GloVe carries). A FAIR test of
  "rich features beat embeddings" (full Lancaster 11-dim continuous + Binder-projected + VerbNet-typed
  slot) has NOT been run. But the expected headroom is genuinely uncertain and could be FLAT, because the
  dimensions norms add (social/affective/animacy) overlap heavily with what embeddings + a supervised
  probe already extract for a COARSE role decision.

Bottom line for SQ3: dimension-level headroom for norms EXISTS (Chersoni 2021), but there is NO published
measurement that grounded norms beat 300-d embeddings on OOV thematic-fit / role generalization, and our
own coarse-feature result went the wrong way. Be honest: the "rich grounded vector will beat GloVe"
expectation is a hypothesis with THIN support on the coarse binary task.

=====================================================================
SQ4 -- Single most defensible brain-faithful (no external LLM) representation + expected ceiling
=====================================================================
MOST DEFENSIBLE REPRESENTATION (reconciling brain-faithfulness with the computational SOTA):
  A VERB-KEYED ROLE-FILLER PROTOTYPE (McRae, Ferretti & Amyote 1997) scored as SIMILARITY in a TYPED
  space. Two admissible instantiations, ranked by evidence:
    (1) The published SOTA form is a SYNTAX/DEPENDENCY-TYPED distributional prototype (Structured
        Distributional Model; the LREC-2020 "syntactic information is the determinant factor" result).
        This is the form that actually BEATS bag-of-words in the literature (by modest margins) and is
        compatible with FHRR binding (type the slot by dependency relation, not by lexical form).
    (2) The most BRAIN-FAITHFUL form is a grounded FEATURE prototype (ATL hub-and-spoke = feature
        integration; Binder brain-based dims). Higher fidelity story, but its task-level advantage over
        embeddings is UNPROVEN (SQ3).
  These are complementary, not exclusive: both discard topic-similarity for TYPED/ROLE-KEYED structure.
  Given "no external LLM at inference" and the thin headroom, the pragmatic recommendation is: KEEP the
  verb-conditioned GloVe fit signal (it is at/near the noun-side ceiling and adequate as a conflict
  tie-breaker), and treat a richer typed/grounded vector as an OPTIONAL upgrade with an EXPLICIT can-fail
  test, not a presumed win.

EXPECTED CEILING:
  - Graded thematic-fit benchmarks: best-of-everything ~0.6-0.7 Spearman (tuned embeddings, SDM, BERT all
    cluster here). This is the field ceiling; do not expect to beat it with a noun vector.
  - Coarse binary agent/patient OOV: ~0.65-0.75 balanced accuracy is a realistic NOUN-SIDE ceiling.
    GloVe-0.65 is already inside that band. Materially exceeding it almost certainly requires STRUCTURE
    (parse/word-order/voice + the conflict gate), not a better noun representation.
  - A FLAT / no-improvement result from a rich-feature fit vector over GloVe-0.65 is a LIVE and arguably
    LIKELY outcome. Per the problem's own rule, that flat result IS the real negative and must be reported
    as such (diagnose: coverage gap in the noun typing vs a genuine noun-side ceiling -- the SQ2/SQ1
    evidence says genuine ceiling is the more likely diagnosis).

=====================================================================
DOES THE PRIOR DRILL'S "features >> distributional" CLAIM HOLD? -- direct audit
=====================================================================
- PINNED and correct: the brain's GENERALISING thematic-fit substrate is feature/prototype-based, verb-
  keyed, and generalises to novel arguments via inferred type (McRae 1997; GEK McRae & Matsuki 2009;
  Elman 2009 words-as-cues; ATL hub-and-spoke). The MECHANISM claim stands.
- OVERSTATED as a QUANTITATIVE claim: "bag-of-words fits thematic fit weakly, therefore grounded features
  beat distributional." Three problems:
    (i)  Its empirical premise ("GloVe = 0.51 = chance") was a MEASUREMENT ARTIFACT (unbalanced classifier
         predicting the majority class). Corrected = 0.65 balanced. The foundation of the strong claim was
         wrong.
    (ii) LREC-2020 supports SYNTAX-TYPED structure > bag-of-words, NOT grounded-features > distributional.
         Miscited direction.
    (iii) No measured evidence that grounded norms beat 300-d embeddings on OOV role generalization; our
         own coarse-feature test went the wrong way.
- The disambiguation drill (sibling) is UNAFFECTED and correct: fit is competition-gated, prototype-not-
  lookup. That is orthogonal to the representation question and stands.

=====================================================================
TLDR (plain English)
=====================================================================
Our two write-ups looked like they disagreed; they do not. The older one said "plain word-similarity
vectors basically can't tell the do-er from the done-to" and recommended building a hand-made
properties-of-the-thing vector instead. The fresh, clean measurement shows the word-similarity vector
actually does moderately well -- about 65 in 100 on a coin-flip-baseline task -- once you score it fairly
(the old "chance" number was a bug where the scorer just guessed the more common answer). Reading the
actual research: the tough benchmark everyone cites is a HARDER task (rate how plausible each pairing is,
on a fine scale), and on THAT task nobody -- not word vectors, not fancy structured models, not big
transformers -- does better than a middling score; so "word vectors are weak" was only ever true compared
to an ideal no method reaches. Two honest corrections to the older write-up: (1) the paper it leaned on
actually says the thing that helps is GRAMMAR/relation information, not hand-made property lists; (2)
there is no published result showing property lists beat word vectors at this, and our own quick property
vector did WORSE than word vectors. The deeper finding is that most of "who did what to whom" is carried
by the SENTENCE STRUCTURE, not by the noun itself -- on a fair, balanced test the noun alone barely beats
a coin flip. So the smart move is NOT to pour effort into a richer property vector for the noun (its
ceiling is low and a no-improvement result is likely); it is to invest in the GRAMMAR/parse side and the
switch that decides WHEN to let plausibility overrule word order -- which is exactly what this problem is
already building. Keep the word-vector plausibility signal we have; it is good enough to break ties.

QUESTIONS: none.

NEXT STEPS
- Do NOT make the rich grounded-feature fit vector the primary lever. Keep verb-conditioned GloVe as the
  fit signal (near the noun-side ceiling, adequate as a conflict tie-breaker). If a richer typed/grounded
  vector is tried at all, gate it behind an EXPLICIT can-fail test vs GloVe-0.65 on held-out OOV; a flat
  result is the expected outcome and is a legitimate negative to report, not a coverage bug to chase.
- Put the build effort on the STRUCTURE side: the conflict/surprisal recruitment gate (the problem's sole
  un-built piece) + parse/voice quality on non-canonical order. SQ2 says that is where the role signal
  actually lives.
- If you want the strongest published representation upgrade, it is a SYNTAX/DEPENDENCY-TYPED distributional
  prototype (SDM-style), not a hand-built grounded vector -- modest margins, but it is the axis LREC-2020
  identifies as determinant. Frame any grounded-feature build as the brain-fidelity story with UNPROVEN
  task headroom, and say so.
- Over-claim guard, BOTH directions: (a) never state "distributional carries no/weak role structure" -- it
  carries moderate signal (~0.65 coarse; 0.4-0.6 graded); (b) never state "grounded features will beat
  embeddings on OOV role" -- unproven and likely flat on the coarse task.

=====================================================================
AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md, CAUSATION/role + thematic-fit entries)
=====================================================================
- The thematic-fit MECHANISM verdict (feature/prototype, verb-keyed, competition-gated) is PINNED and
  unchanged. What CHANGES: the REPRESENTATION recommendation. The prior drill's "grounded features >>
  distributional, build a rich feature fit vector" is downgraded from a recommendation to an UNPROVEN
  hypothesis with thin support; the computational SOTA favors SYNTAX-TYPED structure over bag-of-words by
  modest margins, and on a coarse binary role task verb-conditioned embeddings (~0.65 balanced) are at the
  noun-side ceiling. The load-bearing correction: most role information is STRUCTURAL, not noun-intrinsic
  (animacy-alone 0.54 on a balanced gold; English is word-order-dominant per Competition Model), so the
  fidelity lever is the parse + conflict gate, not the fit vector.

=====================================================================
CITATIONS (URLs used / verified in this drill)
=====================================================================
- Where's the Learning in Representation Learning ... Case of Thematic Fit (arXiv:2208.04749): https://arxiv.org/html/2208.04749 ; https://arxiv.org/pdf/2208.04749  [Table 4 numbers above extracted from this source]
- Are Word Embeddings Really a Bad Fit for the Estimation of Thematic Fit? (Chersoni, Pannitto, Santus, Lenci, Huang, LREC 2020): https://aclanthology.org/2020.lrec-1.700/ ; https://aclanthology.org/2020.lrec-1.700.pdf ; code: https://github.com/ellepannitto/tfe
- Structured Distributional Model of Sentence Meaning and Processing (Chersoni et al. 2019, arXiv:1906.07280): https://arxiv.org/pdf/1906.07280
- Did the Cat Drink the Coffee? Challenging Transformers with Generalized Event Knowledge (Pedinotti et al., *SEM 2021): https://aclanthology.org/2021.starsem-1.1.pdf ; https://arxiv.org/pdf/2107.10922
- Decoding Word Embeddings with Brain-Based Semantic Features (Chersoni et al., Computational Linguistics 2021): https://aclanthology.org/2021.cl-3.20.pdf   [PARTIALLY-PINNED: fast-model PDF summary; animacy-decodability reading is soft]
- Measuring Thematic Fit with Distributional Feature Overlap (Santus, Chersoni, Lenci, Blache, EMNLP 2017): https://aclanthology.org/D17-1068.pdf ; https://arxiv.org/pdf/1707.05967
- Lancaster Sensorimotor Norms (Lynott, Connell, Brysbaert, Brand & Carney 2020): https://link.springer.com/article/10.3758/s13428-019-01316-z ; https://pubmed.ncbi.nlm.nih.gov/31832879/
- psychNorms metabase (norms vs text vs brain; arXiv:2412.04936): https://arxiv.org/pdf/2412.04936   [PDF did not machine-parse; cited for completeness, not for a specific number]
- Competition Model / cue validity (Bates & MacWhinney; MacWhinney): word-order-dominant English -- framework reference.
- l-IPS in reversible/irreversible sentence comprehension (rTMS): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7544754/
- McRae, Ferretti & Amyote 1997 (Thematic roles as verb-specific concepts): https://www.tandfonline.com/doi/abs/10.1080/016909697386835
