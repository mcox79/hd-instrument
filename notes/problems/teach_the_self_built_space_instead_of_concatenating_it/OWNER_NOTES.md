---
owner_verdict: DONE
---

PROBLEM: teach_the_self_built_space_instead_of_concatenating_it
STATUS: REFUTED (the brief's named mechanism) + a brain-foundational alternative whose MECHANISM is
        verified working, with the residual precisely localized. All three tracks witnessed.
LEDGER: python tools/problem_ledger.py --check  ->  malformed/incomplete: 0, awaiting integration.

WHAT WAS ASKED
We own two meaning sources: a narrow-but-accurate hand-rated table (grounded/sensorimotor) and a broad-
but-weak self-built reading map (distributional). A prior result concluded we must BUY a big supplied
map to recognise a word in a context it never co-occurred with -- but it had only ever GLUED the two
sources. The brief asked the untried thing: can the owned narrow source TEACH the built one? Then, at
owner direction, it grew into: what is the OPTIMAL brain-foundational way to give the reader this
capability, and where were we getting it wrong?

=================================================================================================
KEY REALIZATIONS THAT UNLOCKED THIS (read these first -- they are the point)
=================================================================================================
1. TEACHING vs COMBINING is TASK-DEPENDENT. Teaching (one source reshapes the other's geometry) WINS on
   SIMILARITY tasks (substitutability) and LOSES on PREDICTION tasks (slot-fill retrieval) -- because
   perceptual "how it feels" is the wrong AXIS for "which word fills this gap". More teaching = worse.
2. THE GAP IS A HUB PROBLEM, NOT A MAP PROBLEM. The two maps are settled (supplied clears the floor;
   the self-built map equals it on read material). The missing organ is the COMBINATION RULE.
3. THE ORACLE-HEADROOM DIAGNOSTIC is what separated "fundamental" from "fixable". A perfect per-item
   router beats the best fixed blend by +0.074 (0.383 vs 0.310); the two maps are COMPLEMENTARY (right
   on different items, correctness corr 0.23). So the idea was SOUND -- we were building it wrong.
4. THE INFO-FREE TWIN is the control that caught the artifact. Permuting the per-item reliability signal
   left the arbiter UNCHANGED -> the signals it used (cross-source agreement AUC 0.53, confidence 0.49)
   carried NO information. This forced the deeper look instead of accepting a plausible-looking hub.
5. THE UNLOCK -- RELIABILITY MUST BE INTRINSIC, NOT ESTIMATED. We were fusing two DENSE cortical maps
   and reading "which to trust" off their output statistics. In Complementary Learning Systems the tier
   that owns WHAT WAS READ is the HIPPOCAMPUS: a SPARSE, pattern-separated EPISODIC store that ABSTAINS
   on novel input. Its analog is the FIRST-ORDER co-occurrence TRACE itself -- reliability is BUILT IN
   (nonzero exactly where there is episodic evidence), not estimated post-hoc.
6. PATTERN SEPARATION == FREQUENCY CORRECTION. Raw co-occurrence fires for frequent-everything
   distractors (no clean abstention). PPMI-weighting is the computational stand-in for hippocampal
   pattern separation: it fires for genuine associations and goes EXACTLY ZERO on novel contexts.
7. THE RESIDUAL IS DATA SCARCITY, NOT MECHANISM. With a clean synthetic episodic trace the SAME fusion
   jumps 0.02 -> 0.89. On real data the episodic tier fires on only ~10% of items after ~8k sentences.
   The brain has a LIFETIME of episodes; we don't. Same corpus-scale ceiling that starves everything here.

=================================================================================================
THE ARC (three acts, each witnessed)
=================================================================================================
ACT 1 -- TEACHING REFUTED (clean, powered; the brief calls this a full PASS).
  On the unseen-co-occurrence retrieval task, 3 seeds, 267/269/279 unseen items, the grounded spoke
  teaching the self-built map in its THREE strongest forms all fail and all make retrieval WORSE:
  hit@10 (pess) DIAG 0.030/0.037/0.047, full-metric 0.019/0.007/0.025, retrofit 0.026/0.022/0.032 --
  vs CONC floor 0.161/0.164/0.172, vs raw self-built (LSA_FULL) 0.048-0.079, each BELOW its own oriented
  info-free twin. More grounded reshaping = monotonically worse. GLOVE (supplied) clears CI-separated at
  k>=25 -> the task is winnable, so the negative is real.
  Witness: verification/test_teaching_does_not_rescue_unseen_retrieval.py (5/5).

ACT 2 -- THE ARBITRATION HUB (drill's top pick) REFUTED BY ITS OWN CONTROL.
  An owner-authorized brain-foundational drill (notes/research/brain_foundational_unseen_context_
  recognition_2026-08-24.md) argued the fix is a per-item reliability-weighted FUSE-OR-DEFER hub
  (Ma2006/Ernst-Banks2002/Kording2007/Lee2014). Built it over the learned tier + supplied foundation on
  a MIXED seen+unseen population. It TIES the best fixed blend (replication UNSTABLE ~0) AND its
  permuted-reliability twin REPRODUCES it (max |ARB_FOD - ARB_PERM| = 0.016) -> per-item reliability
  signal inert. HARD-FAIL by the drill's own pre-registered controls.
  Witness: verification/test_reliability_arbitration_ties_fixed_blend.py (5/5).

ACT 3 -- THE DEEP-DIVE: where Act 2 went wrong, and the corrected mechanism WORKS.
  (a) exp_arbitration_failure_diagnosis_v1: oracle headroom +0.074 (idea sound); the used signals are
      coin-flips (agreement AUC 0.53, confidence 0.49); the EVIDENCE-based signal (first-order
      co-occurrence) carries information (AUC 0.81 seen / 0.615 learned-uniquely-right).
  (b) exp_reliability_arbitration_hub_v2_evidence_gate: gating a DENSE map by its evidence FIXES the
      inert-signal bug (beats its twin) but still TIES the fixed blend (replication INCONSISTENT_SIGN)
      -- a dense map's per-item reliability is too weak.
  (c) exp_cls_hippocampal_cortical_fusion_v1: the CLS-CORRECT build. Hippocampal tier = PPMI-weighted
      (pattern-separated) FIRST-ORDER co-occurrence, fused with the cortical prior (GLOVE). Result,
      3 seeds, 720 items (seen ~448 / unseen ~272):
        - the episodic trace ABSTAINS on novel contexts (HIPPO hit@10 on UNSEEN = 0.000);
        - the episodic signal now CARRIES VERIFIED INFORMATION: the gated fusion CI-beats its
          SHUFFLED-episodic twin on ALL 3 seeds (lo 0.237-0.246 > twin hi 0.204-0.225) -- in v1 the twin
          MATCHED; this is the fix, measured;
        - fusion beats cortical-alone every seed: +0.015-0.025 on the mixture, +0.03-0.05 on read
          material (FIXED_BEST SEEN 0.357-0.374 vs CORTICAL 0.306-0.336) -- but NOT CI-separated on the
          mixture (small);
        - HIPPO standalone ~0.10 (data-starved: fires on ~10% of items); oracle ceiling ~0.34;
        - synthetic positive control: a clean episodic trace takes the SAME fusion 0.02 -> 0.89.
  Witness: verification/test_cls_episodic_signal_carries_information.py (4/4).

CONTROLS THAT DID THE WORK
  - per-arm oriented INFO-FREE TWIN (teaching): every taught arm below its own; excludes orientation
    artifact. - COULD-IT-SUCCEED (GLOVE clears): excludes unwinnable population. - INFO-FREE TWIN
    (arbitration): permuted reliability reproduced v1 (caught the artifact) and FAILED for the corrected
    episodic signal (proved it real). - SHUFFLED-episodic twin CI-separated 3/3. - ORACLE per-item
    router: quantified the true headroom. - reliability-signal AUCs: which signals carry information.
  - SYNTHETIC positive control: the combiner registers an episodic win when a trace exists.
  - both tie conventions (rank_with_ties); 3-seed replication_gate throughout.

CAVEATS / WHAT IS NOT ESTABLISHED
  - The CLS fusion's gain over the cortical prior is REAL but SMALL and NOT CI-separated on the mixed
    population -- capped by episodic data scarcity, not the mechanism (the synthetic control isolates
    this). I would withdraw any "it beats the fixed blend" framing; the defensible claims are: (i) the
    corrected episodic signal carries verified information (CI-beats its shuffled twin 3/3), and (ii) the
    mechanism is sound (synthetic 0.02->0.89). - Everything is measured in live-faithful cells, not the
    literal live organ; the final live number is the strategy session's after wiring. - No hdlab/ change
    landed (board Q111).

PROPOSED hdlab DIRECTIONS (NOT landed; strategy/flagship owns integration)
  - For unseen-context retrieval: SUPPLY the distributional foundation (glass-box, offline, non-LLM);
    do NOT wire grounded->distributional teaching (refuted), and do NOT build a per-item reliability
    arbiter over two DENSE maps (v1 refuted).
  - DO wire the CLS pair: cortical prior (supplied distributional) + a SPARSE, PPMI/pattern-separated
    EPISODIC trace whose reliability is INTRINSIC (abstains on novel). It helps today and grows
    monotonically with reading. This is the flagship reader_meaning_channel's combination-rule territory.
  - The lever for a BIGGER gain is MORE READING (episodic coverage), not a new mechanism; there is no
    supplied episodic resource to buy.

REVERIFY (scaffold-free; each writes only its own dir)
  .venv/Scripts/python.exe verification/test_teaching_does_not_rescue_unseen_retrieval.py        # 5/5
  .venv/Scripts/python.exe verification/test_reliability_arbitration_ties_fixed_blend.py         # 5/5
  .venv/Scripts/python.exe verification/test_cls_episodic_signal_carries_information.py           # 4/4
  Full reruns: --mode full --seeds 3 on any of experiments/exp_taught_distributional_retrieval_v1.py,
  exp_reliability_arbitration_hub_v1.py, exp_cls_hippocampal_cortical_fusion_v1.py.

FILES
  experiments/: exp_taught_distributional_retrieval_v1.py, exp_selfbuilt_distributional_ceiling_probe_v1.py,
    exp_reliability_arbitration_hub_v1.py, exp_arbitration_failure_diagnosis_v1.py,
    exp_reliability_arbitration_hub_v2_evidence_gate.py, exp_cls_hippocampal_cortical_fusion_v1.py
  verification/: test_teaching_does_not_rescue_unseen_retrieval.py,
    test_reliability_arbitration_ties_fixed_blend.py, test_cls_episodic_signal_carries_information.py
  notes/research/brain_foundational_unseen_context_recognition_2026-08-24.md
  notes/problems/teach_the_self_built_space_instead_of_concatenating_it/SOLVED.md (the full arc)

FOR THE STRATEGY SESSION
  1. Re-verify the three witnesses. 2. Record the closures: teaching refuted; dense-map arbitration
  refuted-by-control; CLS episodic+cortical fusion mechanism VERIFIED (signal carries info) but gain
  data-capped. 3. Route the CLS pair (cortical prior + sparse PPMI/pattern-separated episodic trace)
  into reader_meaning_channel as the combination rule; keep B3' NEEDS_ADAPTER. 4. Frame the next lever
  as READING VOLUME (episodic coverage), not a new combiner. 5. Keep the grounded spoke labelled a
  SIMILARITY teacher, not a retrieval teacher.

PLAIN-LANGUAGE TLDR
  We asked whether our accurate-but-narrow meaning table could TEACH our broad-but-weak reading map to
  recognise a word in a brand-new sentence. It can't -- and it makes things worse, because "how a word
  feels" is the wrong clue for "which word fits here". So we tried the brain's actual trick: keep two
  memories -- a broad ready-made one and your own episodic memory of what you've read -- and trust
  whichever one actually has evidence about the word in front of you. Our first attempt failed, and the
  reason turned out to be that we built the "memory of what I've read" the wrong way (a blurry general
  map) and judged its trustworthiness by the wrong tell. When we rebuilt it the brain's way -- a sparse
  memory that only speaks up about things it genuinely saw, and stays silent otherwise -- the trust
  signal became real and the combination started helping. The only thing holding the gain down now is
  that we simply haven't read enough for that episodic memory to have much in it yet. The mechanism is
  right; it grows as the reader reads. Nothing here needs buying beyond the one broad ready-made map.
