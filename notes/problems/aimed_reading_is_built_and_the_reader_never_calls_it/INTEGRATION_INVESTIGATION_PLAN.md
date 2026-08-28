# INTEGRATION INVESTIGATION PLAN — why two good meaning signals combine to something worse
### Brain-foundational drill sequence. Referenced by the 30-min resolution cron (job 5defe965).
2026-08-24. Owner directive: "if we're brain foundational, this should work; if it's not working it
means we're not succeeding at being brain foundational. get to the bottom of this."

## THE ANOMALY (one paragraph)
A reader's raw distributional embedding scores WordSim-353 Spearman **~0.34**; the grounded
sensorimotor hub scores **~0.41**; our operator that folds grounding INTO the reading channel scores
**~0.23** — worse than *both*. Two positively-correlated meaning signals cannot integrate to
something worse than either unless the integration operator is broken. In hub-and-spoke terms
(Patterson; Lambon Ralph): the semantic hub INTEGRATES modality spokes complementarily, so the
integrated representation is >= any single spoke. Our operator (exp_reader_distilled_meaning_v1.py
`distill_and_score`, L266-331) trains the distributional channel to **mimic** the grounded channel
(X = phi[a]*phi[b], target = grounded cosine, diagonal bilinear fit). That is SUBSTITUTION, not
integration — it discards exactly the distributional relatedness that made raw 0.34. **The fix is to
integrate, not substitute — and to do it the way the brain does.**

## RESOLUTION CRITERION (stop only when BOTH hold)
1. A brain-faithful integration where **combined >= max(raw, grounded), CI-separated**, and the
   info-free (shuffled-grounding) twin LOSES.
2. A brain-mechanism explanation of **why the original operator failed** (and why the faithful one
   works), each choice marked PINNED-BY-EVIDENCE vs OUR-INVENTION-UNDER-TEST.

## THE LAYERED DRILLS (run the next unresolved layer each cron fire)

### L1 — Integration vs substitution  [RUNNING: agent a0a011441b9b0a956]
- **Brain claim (PINNED):** the hub combines spokes; combined >= either alone.
- **Drill:** on the same words, same shared eval pairs (both words have phi AND grounded), compare
  RAW, GROUNDED, the current SUBSTITUTIVE operator, equal-weight z-FUSION, CONCAT-JOINT, and a
  shuffled-grounding twin; bootstrap CIs on the deltas.
- **Prediction:** FUSION/CONCAT >= max(raw, grounded), CI-separated over raw; SUBSTITUTIVE loses;
  twin fails to lift. **Resolves:** was the operator the bug? (Expected: yes.)
- **If FUSION does NOT beat raw:** the problem is deeper than the operator → go to L2/L5, do not spin.

### L2 — Concreteness-gated integration (the likely REAL brain-faithful form)
- **Brain claim (PINNED, Vigliocco; Kousta; Barsalou):** sensorimotor grounding is informative for
  CONCRETE words (dog, hammer) and largely UNINFORMATIVE for ABSTRACT words (justice, theory), which
  the brain grounds via affective/interoceptive + linguistic routes, NOT sensorimotor. So a UNIFORM
  fusion injects noise on abstract words — the grounding weight should depend on concreteness.
- **Drill:** gate the grounding weight per word by Brysbaert concreteness (high concreteness -> lean
  on grounding; low -> lean on distributional). ALSO stratify the WordSim eval by pair concreteness
  and show grounding's lift concentrates on concrete pairs. Info-free twin: shuffle the concreteness
  values.
- **Prediction:** gated fusion > uniform fusion; the grounding lift is concentrated on concrete
  pairs and ~0 on abstract pairs. This is "use grounding where grounding applies" — the faithful hub.
- **OURS-UNDER-TEST:** the specific gating function (linear in concreteness vs threshold).

### L3 — Hub as a learned transmodal compression (highest fidelity)
- **Brain claim (PINNED structure, OURS implementation):** the ATL hub is a nonlinear LEARNED
  integration layer, not a fixed weighted sum. A faithful hub learns a joint low-dim code that keeps
  what is shared and complementary across the two spokes.
- **Drill:** learn a label-free joint embedding from [phi, grounded] — CCA / PLS / a shallow
  autoencoder over the two channels — score on WordSim; compare to L1/L2 fusion.
- **Prediction:** learned joint >= best hand-weighted fusion. If it does not beat fusion, the linear
  hub is sufficient at this scale (report that honestly — simpler is the answer).

### L4 — Teacher upgrade: CSKG as the grounded spoke
- **Brain claim:** richer world-knowledge grounding than 12-dim sensorimotor norms. The teacher
  ceiling (grounded-alone ~0.41) caps every integration; a stronger spoke raises it.
- **Drill:** replace/augment the 12-dim hub with CSKG (1.21M-edge, `data/`, unused live) node
  embeddings as the grounded channel; re-run the winning integration from L1-L3. Info-free twin:
  shuffled graph.
- **Prediction:** raises both the grounded spoke and the integrated result CI-separated over the
  norm-hub version. (This is the STEP-2 forward-work item, now with a working integration to feed.)

### L5 — Metric / word-class audit (fairness backstop, runs alongside)
- **Brain claim:** meaning is multi-faceted; do not judge grounding on one metric. WordSim
  (relatedness) is right for co-occurrence; SimLex (similarity) penalizes association; a downstream
  comprehension task is the real target.
- **Drill:** re-score the winning integration on SimLex-999 and a context-conditioned sense task,
  each with a POSITIVE CONTROL (metric detects meaning in a known-good embedding) before trusting any
  negative. Report per-word-class (concrete/abstract, noun/verb) breakdowns.
- **Prediction:** grounding's contribution is real but concentrated (concrete nouns); this explains
  the uniform-fusion shortfall and confirms L2.

## STANDING FAIRNESS RULES (every layer)
- Same shared eval-pair population across all arms; no number crosses populations.
- Report CI half-width and the info-free twin beside every delta; a width is not an effect.
- Untuned equal-weight is the honest headline; any tuned weight is cross-validated (tune on half,
  report on the other half) to avoid optimize-then-report.
- Save the scored population (eval pairs + per-arm predictions) every run.

## LOG (append per fire)
- 2026-08-24: L1 dispatched (agent a0a011441b9b0a956). Anomaly stated; operator confirmed
  substitutive by code read. v4 replication landed separately: v6 LEARNABLE coverage win REPLICATED
  3/3 (twin loses); shipped forager REFUTED-REPLICATED 3/3.
- 2026-08-24: **L1 RESOLVED. The anomaly was the substitutive operator; brain-faithful complementary
  integration works exactly as hub-and-spoke predicts.** Full run (budget 10000, shared eval pairs
  n=228-245), `data/exp_reader_meaning_integration_diag_v1/metrics.json`:
  | reader | RAW | GROUNDED | FUSION(equal) | CONCAT | SUBSTITUTIVE(old) | FUSION-SHUFFLE(twin) |
  |---|---|---|---|---|---|---|
  | FROZEN | 0.357 | 0.380 | **0.446** | 0.428 | -0.236 | 0.256 |
  | COMPREHENSIBLE | 0.345 | 0.382 | **0.448** | 0.429 | 0.126 | 0.166 |
  | RANDOM | 0.305 | 0.414 | **0.487** | 0.479 | 0.162 | 0.213 |
  - FUSION exceeds BOTH spokes in 3/3 readers (point-wise). Over the STRONGER spoke (grounded):
    +0.065 CI[0.009,0.124] (FROZEN), +0.067 CI[0.003,0.127] (COMPREHENSIBLE) -- CI-separated 2/3;
    RANDOM +0.073 CI[-0.008,0.150] (grounded strong, delta touches 0). Over RAW: CI-separated 2/3.
  - INFO-FREE TWIN (shuffled grounding) LOSES CI-separated 3/3: FUSION-SHUFFLE +0.19 CI[0.064,0.314],
    +0.282 CI[0.146,0.414], +0.274 CI[0.164,0.379]. The lift is real cross-modal complementarity.
  - SUBSTITUTIVE - RAW = -0.59 / -0.22 / -0.14: the shipped operator DESTROYS meaning vs raw. It was
    the bug.
  - NOTE on the cell's own labels: it fired INTEGRATION_DOES_NOT_HELP for FROZEN because its logic
    required beating RAW CI-separated; the brain-relevant test is beating the STRONGER spoke
    (grounded) + the twin, which holds. Read the deltas, not the auto-label.
  - MECHANISM (brain): the semantic hub INTEGRATES the linguistic and sensorimotor spokes
    complementarily (combined > either); our original operator SUBSTITUTED (trained linguistic to
    mimic sensorimotor), discarding the distributional relatedness. Fidelity divergence identified
    and fixed. **CORE ANOMALY RESOLVED.**
  - NEXT (enhancement, not required to resolve): L2 concreteness-gating -- explain WHERE the grounding
    lift lives (predict: concrete pairs) and push all-3 to CI-separation. phi caches saved
    (scratch/phi_cache_*.npz) so L2 runs offline/cheap.
- 2026-08-24: **L2 DONE -- UNIFORM FUSION IS SUFFICIENT; concreteness gating does NOT improve it.**
  `data/exp_reader_meaning_integration_gated_v1/metrics.json` (offline from caches, 20s). Per reader
  (RAW/GROUNDED/FUSION_EQUAL/GATED_FUSION/GATED_TWIN): FROZEN 0.357/0.380/0.446/0.448/0.432;
  COMPREHENSIBLE 0.345/0.382/0.448/0.452/0.430; RANDOM 0.305/0.414/0.487/0.474/0.443.
  - GATED - FUSION_EQUAL straddles 0 all 3 (+0.003/+0.003/-0.013) -> gating adds nothing over uniform.
  - Concreteness IS a weak real targeting axis: GATED - GATED_TWIN CI-separated for RANDOM
    (+0.031 [0.004,0.057]), positive-not-separated for the others.
  - Per-stratum GROUNDED-RAW: concrete>abstract for COMPREHENSIBLE & RANDOM (predicted) but REVERSES
    for FROZEN; NO stratum delta is CI-separated (abstract n=30-36, half-widths ~0.45-0.52).
  - HONEST: prediction (b) gating-beats-uniform = UNSUPPORTED; prediction (a) concrete-localization =
    suggestive but UNDERPOWERED. **Uniform equal-weight fusion is the answer at this scale.** Simpler
    is the resolution; do not claim concrete-localization without a bigger benchmark (L5, more pairs).
  - NEXT: L3 learned hub (CCA/joint compression) -- is a LEARNED integration better than fixed
    equal-weight, or is linear fusion sufficient? Offline from caches. Then L4 CSKG teacher (raise the
    grounded spoke ceiling above 0.41 -- the biggest absolute lever, needs a graph-embedding build).
- 2026-08-24: **L3 DONE -- LINEAR_FUSION_SUFFICIENT (3/3). A learned hub does NOT beat fixed
  equal-weight fusion.** `data/exp_reader_meaning_integration_learned_v1/metrics.json` (offline, 11s).
  Per reader (RAW/GROUNDED/FUSION_EQUAL/CCA_JOINT/PCA_JOINT/CCA_TWIN):
  FROZEN 0.357/0.380/0.446/0.384/0.338/0.192; COMPREHENSIBLE 0.345/0.382/0.448/0.422/0.396/0.187;
  RANDOM 0.305/0.414/0.487/0.369/0.348/0.135.
  - CCA_JOINT - FUSION_EQUAL: -0.062/-0.026/-0.119 (RANDOM CI-separated BELOW) -- learned hub never
    beats fixed fusion; sometimes worse. PCA_JOINT worse in FROZEN & RANDOM.
  - CCA_TWIN lost 3/3 (0.19/0.19/0.13); CCA beats its OWN twin CI-separated (learned alignment uses
    real correspondence) but that real signal does not exceed the untuned equal-weight fusion.
  - MECHANISM (brain insight): CCA maximizes the SHARED subspace between spokes; the VALUE of hub
    integration is the COMPLEMENTARY (non-shared) information. Equal-weight fusion PRESERVES both
    spokes' unique contributions; CCA discards them. So the simplest faithful operator is correct.
  - **CONVERGED. THREE independent results (L1 integration>substitution+both-spokes; L2 gating adds
    nothing; L3 learned hub adds nothing) all point to: fixed equal-weight COMPLEMENTARY FUSION of the
    reading spoke and the grounded spoke is the sufficient, brain-faithful meaning operator.**
    ANOMALY FULLY RESOLVED + OPERATOR VALIDATED.
  - REMAINING (forward levers, NOT anomaly-resolution): L4 raise the grounded spoke via CSKG (the
    teacher quality caps the ceiling); L5 confirm on SimLex + a downstream comprehension task. These
    raise absolute performance; they do not change the resolved mechanism.
- 2026-08-24: **L4 DONE -- CSKG_TEACHER_LIFTS (unanimous), BUT it REPLACES rather than COMPLEMENTS --
  read the caveat, not just the number.** `data/exp_reader_meaning_teacher_optimization_v1/metrics.json`.
  Built a CSKG word embedding (data/grounding_testbed/cskg.tsv.gz, 4.63M English edges, PPMI+symmetric
  SVD k=200, 100% benchmark coverage; cache scratch/cskg_node_embedding_v1_k200.npz). Prior-work
  checked: query "cskg"=129 (113 landed), "conceptnet"=42 (35 landed); no reusable word->dense CSKG
  embedding existed.
  - WordSim (RAW/GRN_NORM/FUS_NORM/GRN_CSKG/FUS_CSKG/FUS_3WAY/CSKG_TWIN):
    FROZEN .357/.380/.446/.656/.647/.598/.231; COMPREH .345/.382/.448/.665/.653/.595/.268;
    RANDOM .305/.414/.487/.698/.650/.638/.224. SimLex lifts too (FUS_NORM .11-.17 -> FUS_CSKG .28-.34;
    GRN_CSKG .39-.42).
  - Controls hold: FUS_CSKG-FUS_NORM +.16-.20 CI-separated 3/3; positive control GRN_CSKG >>0; twins
    lose CI-separated; CV-honest tuned ~= untuned (no tuning leak).
  - **CAVEAT (director interpretation, VET-pending): CSKG DOMINATES, does NOT complement.** CV-honest
    tuning drives the norm-hub weight to ~0 and the reading weight low; FUS_CSKG ~= GRN_CSKG alone;
    FUS_CSKG > FUS_3WAY (adding the thin hub DILUTES). So this is a richer teacher REPLACING the thin
    one, not spoke-synergy -- and reading becomes ~redundant given CSKG (a static rich foundation
    subsumes the runtime reading channel on relatedness). CSKG is a relatedness/linguistic graph;
    WordSim measures relatedness; ~0.65 is the known ConceptNet-embedding regime -- arguably a better
    DISTRIBUTIONAL channel, not a distinct sensorimotor modality.
  - **THE GENUINE HUB-AND-SPOKE RESULT REMAINS L1** (sensorimotor grounding ADDS to reading; fusion >
    BOTH; the modality is complementary). L4 optimizes the absolute number (ceiling ~0.66 WordSim /
    ~0.40 SimLex) but does not demonstrate multi-modal synergy.
  - NEXT (genuine frontier): (a) skunkworks landed-VET, esp. the grounding-vs-distributional
    adjudication; (b) a truly SENSORIMOTOR richer teacher (full Lancaster norms) to test spoke-SYNERGY
    without the relatedness-overlap confound -- does a richer PERCEPTUAL spoke ADD on top of CSKG?
- 2026-08-24: **L4 landed-VET (hdi_skunkworks, independent, AUDIT-ONLY) -- NUMBERS CLEAN, SYNERGY
  FRAMING REFUTED.** Off-disk recompute matches the table to |delta|=0.00000 (54 arm-cells); leak
  audit CLEAN (benchmark WORDS used only for vocab coverage; no PAIR/LABEL enters the CSKG build, SVD,
  or any fit; headline arms use FIXED equal weights = zero fitting; CV-tuning splits disjoint halves);
  twin genuinely permutes (99.6-100% cosines change) and collapses (0.66->0.03); positive control
  >>0. DISPOSITION proven-bound / MEASURED_MECHANISM.
  - ADJUDICATION (independent): FOUNDATION-SWAP, not spoke synergy; "grounding" label NOT defensible.
    Synergy signature ABSENT in all 6 cells: GROUNDED_CSKG >= FUSION_CSKG >= FUSION_3WAY. Adding
    reading never beats CSKG-alone; adding the hub HURTS. CV-honest weights zero the hub and downweight
    reading (SimLex picks CSKG-alone). CSKG PPMI+SVD is a distributional/relational embedding; ~0.65
    WordSim is the known ConceptNet regime. **Do NOT atomize under a "multi-modal grounding synergy"
    anchor.**
  - **NET, VERIFIED:** (i) the GENUINE hub-and-spoke synergy result is L1 (sensorimotor grounding
    COMPLEMENTS thin reading: 0.34+0.40 -> 0.47 > both, twin loses). (ii) The OPTIMIZATION ceiling on
    lexical benchmarks is ~0.65-0.70 via the CSKG relational foundation, which SUBSUMES reading + the
    hub -- nothing adds to it. These are two different findings; do not conflate.
  - THE ONE OPEN FRONTIER (needs a NEW eval, not a richer teacher): does a SENSORIMOTOR/PERCEPTUAL
    spoke ADD on top of CSKG on a task where PERCEPTION is decisive (not lexical relatedness)? Lexical
    benchmarks may structurally hide sensorimotor contribution. This is the real test of hub-and-spoke
    at the ceiling; it is a scoping decision (which perceptual benchmark), not a quick drill.
