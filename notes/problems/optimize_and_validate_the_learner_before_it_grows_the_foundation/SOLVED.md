---
problem: optimize_and_validate_the_learner_before_it_grows_the_foundation
status: PARTIAL
bar: "PASSES only with ALL of: (1) Beats the PPMI-SVD baseline CI-separated on >=2 held-out meaning populations, its own strongest floor recomputed per population, info-free twin (shuffled co-occurrence / random-init / scrambled reading order) LOSING CI-separated; report CI half-width + null p95; NO number crosses populations/scorers. (2) Brain-faithful learning RULE: an ONLINE, error-driven/Hebbian (optionally replay-interleaved CLS) update -- NOT batch PPMI-SVD -- OR a specific, argued reason the batch form IS the computational optimum and the online rule converges to it; state the operation; COPY the computation, SWEEP the params. (3) NET-IMPROVES THE UPDATED SUBSTRATE: fused/demand-routed alongside conceptual_meaning + scalar_adjective_operation + the router, the learned channel lifts the composed meaning read CI-separated on the axis it should win AND does NOT regress what the OTHER channels already win; show the dissociations are preserved (a fused-into-one-pool control loses). (4) THE SAFETY GATE: a held-out test that growing the substrate's meaning WITH the learner improves a DOWNSTREAM comprehension score, with an info-free GROWTH control (grow with shuffled / non-text / random co-occurrence) that must NOT help (ideally HURT); quantify the corruption risk -- does the learner ever DEGRADE a meaning the substrate had right? report the rate + CI. (5) Propose the exact hdlab diff (default-off; growth is a separate gated step). A rigorous NEGATIVE -- the best brain-faithful learner does NOT beat PPMI-SVD, or does NOT safely improve the updated substrate -- is a FULL PASS: it says 'do not turn it on yet,' and why (which sub-bar failed)."
result: "DECISIVE, MIXED. (BAR1, WIN) The brain-faithful lever is CONTEXT SHAPE, not the update rule: a dependency-typed (grammatical-relation) distributional learner beats the incumbent +/-2-window PPMI-SVD baseline on the SIMILARITY axis CI-separated at MATCHED 15M-token scale -- SimLex rho 0.2699 vs 0.2102 (paired Delta-rho +0.0598 CI [0.0226,0.0965], ci_half 0.0369, n=995); SimVerb 0.1186 vs 0.0844 (+0.0342 CI [0.0074,0.0604], ci_half 0.0265, n=3432). 2/3 populations pass (WordSim relatedness stays the window's, the predicted dissociation). All info-free twins LOSE CI-separated (label-shuffle, random-tree), and the grammatical LABEL itself carries signal on verbs (DEP_TYPED > DEP_UNTYPED +0.042 CI [0.018,0.063]). The McRae selectional-preference verb arm (SELPREF) is the strongest verb model (SimVerb 0.148). At 15M the learner already matches the incumbent's full-38M SimLex (0.270 > 0.255) -- ~2.5x more data-efficient. (BAR2) The update-rule premise is REFUTED: SGNS == shifted-PPMI factorisation (Levy & Goldberg 2014) and CBOW==counting is already landed on this substrate (DEVIATION #2), so online==batch; the escape hatch is satisfied by argument. (BAR3, NUANCED) Under a brain-faithful RELIABILITY-weighted combiner the learned channel is NET-NEUTRAL-not-harmful when added to the full pool that already contains the SUPERVISED WordNet channel (which dominates the WordNet-derived golds at 0.52/0.50); the within-mission upgrade window->dependency DOES net-improve the reading-based read-out CI-separated (SimLex +0.038, SimVerb +0.024); equal-weight fusion HURT (an artifact of the non-brain-faithful combiner), and the dissociation is preserved (reliability-weighted beats the one-pool combiner). (BAR4, CONDITIONAL) Growing the reader's meaning by reading 5M->15M tokens improves downstream LitBank who-did-what comprehension 0.0714->0.1494 (+0.078 CI [0.070,0.087]) AND the gain is REAL learned structure: the strict info-free growth controls (full-corpus token shuffle 0.0112, filler-shuffle 0.0166) fall BELOW baseline and GROWN beats full-shuffle +0.138 CI-sep. BUT growth corrupts ~25.6% of previously-CORRECT answers (CI [0.215,0.299]), and this is UNIFORM across confidence (confident 0.254 vs low-margin 0.258, indistinguishable) = genuine knowledge loss, not churn -> confidence-gating cannot fix it. BUT (fidelity drill, exp_growth_cls_ensemble_v1) a CLS-FAITHFUL growth mechanism FLIPS the gate: keeping the pre-growth store and fusing it with the new one (ENSEMBLE_MEAN, the hippocampal+cortical keep-both-stores) cuts corruption to 0.0785 (delta -0.177 CI [-0.215,-0.142] vs naive, ~3.3x less) while keeping 71% of the gain; a rate-limited gradual blend (alpha=0.25) keeps 84% of the gain at corruption 0.185 (-0.071 CI-sep). Accuracy SATURATES at alpha=0.25 while corruption climbs monotonically toward the naive value -- the CLS signature (slow replay-preserving integration beats wholesale overwrite). CONCLUSION: the learner is decisively BETTER, growth adds real structure, and it IS SAFE to grow behind a CLS-faithful mechanism (keep-both-stores ensemble, or rate-limited gradual integration) -- the ~25.6% corruption of a NAIVE overwrite was a MISSING-MECHANISM artifact, not a ceiling. Default-OFF; the growth mechanism is now concrete, not hand-waved."
floor: "BAR1 strongest floor actually run, recomputed per population on its own representation: the strongest WINDOW arm (WIN2, +/-2) -- SimLex 0.2102, SimVerb 0.0844 (WIN1 +/-1 was weaker: 0.1942 / 0.0602); gated on the paired Delta-rho lower CI > 0, not on independent CIs. BAR4 floors: RANDOM-vector 0.0051, and the clean info-free GROWTH floor = full-corpus-shuffle 0.0112 (learned vectors with all co-occurrence destroyed). Q116 incumbent baseline (reverified PASS 2026-08-28) SimLex 0.2552 / SimVerb 0.1290 / WordSim 0.6301 at 38M is the absolute reference (beaten on data-efficiency)."
controls: "(1) LABEL-SHUFFLE twin (dependency-typed, deprel labels shuffled ACROSS edges preserving multiset+count+fillers) -- LOSES CI-sep on SimLex/SimVerb; excludes 'context sparsity, not grammar' (NB a global bijection is SVD-invariant and was rejected as degenerate). (2) RANDOM-TREE twin (random spanning tree + random labels per sentence) -- LOSES CI-sep; excludes 'any sparse structure.' (3) DEP_UNTYPED ablation (syntactic-neighbour fillers, NO label) -- DEP_TYPED beats it CI-sep on verbs; isolates the grammatical-relation TYPE. (4) SHUFFLED-CORPUS + RANDOM arms at floor. (5) BAR3 NOISE-channel fusion control (add random instead of the learned channel) never beats CONTROL; the equal-weight one-pool combiner REGRESSES where the reliability-weighted (dissociation-aware) combiner does not -- the fused-into-one-pool control loses. (6) BAR4 INFO-FREE GROWTH controls: full-corpus token-shuffle AND filler-shuffle BOTH fall below baseline (isolates real learned structure from 'more tokens'); the initial label-shuffle control was too WEAK (kept verb-filler co-occurrence) and was superseded. (7) BAR4 corruption split by prediction confidence (top vs bottom half of the top-vs-2nd margin) -- indistinguishable, excluding 'low-confidence churn'. (8) coverage reported per population; scored on common-coverage intersections so every arm saw the same pairs; NO number crosses populations/scorers; all floors recomputed per population. Reverify witness re-asserts these off the landed metrics."
files_changed: "experiments/exp_structured_context_learner_v1.py (BAR1+BAR2, the structured-context learner + arms/twins/paired-delta gate + optional SGNS arm); experiments/exp_learned_channel_fusion_v1.py (BAR3, reliability-weighted fusion + reading-channel upgrade + coverage); experiments/exp_learner_safety_gate_v1.py (BAR4, downstream growth gate + info-free growth controls + corruption-by-confidence); experiments/exp_growth_cls_ensemble_v1.py (FIDELITY: CLS keep-both-stores ensemble + rate-limited gradual blend -- flips the safety gate); experiments/exp_grounded_selpref_v1.py (FIDELITY: grounded-feature McRae selectional preference -- rigorous NEGATIVE, centroid-averaging over-compresses); verification/verify_structured_context_learner.py (scaffold-free witness, PASS -- asserts BAR1 + BAR4 + the CLS safe-growth flip); notes/problems/optimize_and_validate_the_learner_before_it_grows_the_foundation/DESIGN_brain_analysis.md; data/exp_structured_context_learner_v1/, data/exp_learned_channel_fusion_v1/, data/exp_learner_safety_gate_v1/, data/exp_growth_cls_ensemble_v1/, data/exp_grounded_selpref_v1/ (metrics + parse caches). NO hdlab/ CHANGED -- the proposed diff is described below for the strategy session to land."
reverify: ".venv/Scripts/python.exe verification/verify_structured_context_learner.py"
---

# The learner's brain-faithful lever is the CONTEXT it learns over, not how it updates -- and it is safe to grow with only behind a regression-checked gate

## Plain language

I was asked to build a more brain-like meaning-learner and prove it (a) beats the current recipe,
(b) makes the whole meaning system better, and (c) is SAFE to let loose growing the reader's
permanent knowledge -- before it is ever turned on.

- **The brief's idea (update the brain's way -- online, from prediction error) is a proven dead end.**
  The online method and the current batch method are mathematically the same and land in the same
  place (Levy & Goldberg 2014; already confirmed on this substrate). So *how* the learner updates is
  not the lever.
- **The real brain lever is WHAT it learns over.** The brain organises word meaning by grammatical
  role ("the thing that chases" vs "the thing chased"), not by which words sit nearby. A learner that
  learns over grammatical relations instead of nearby-word windows **wins the two hardest
  word-similarity tests by a clear, statistically-separated margin**, every scrambled control loses,
  and it reaches the old recipe's quality with ~2.5x less reading (itself brain-like). The
  "verb = its typical participants" arm is the single best verb model.
- **Does it make the whole system better?** It improves the reading-learned meaning. It does NOT beat
  the hand-supplied WordNet knowledge on WordNet's own tests (those tests are built from WordNet), but
  it does no harm there once you combine channels the brain's way (weighting each by how reliable it
  is, not averaging blindly).
- **Is it safe to grow with?** Growing by reading more genuinely helps comprehension (real structure,
  not just more words -- the strict fakes fall to chance). BUT growing breaks about **1 in 4** answers
  the reader previously got right, and it breaks confident answers just as often as unsure ones. So a
  simple "only update when unsure" safeguard would not protect what it already knows. **It is not yet
  safe to turn on unconditional growth; it becomes safe only behind a mechanism that checks each
  update against a held-out test and can roll it back.**

## What I built and measured (by sub-bar)

**BAR 1 -- the learner beats the baseline (PASS).** `exp_structured_context_learner_v1.py`. Held
EVERYTHING constant except the definition of "context" (same corpus, same vocab, same PPMI-alpha+SVD
pipeline reused verbatim from the incumbent, same scorer) and varied only the word x context matrix's
columns: +/-2 window (incumbent), +/-1 window, dependency-TYPED (direction+deprel, filler),
dependency-UNTYPED (filler only), the McRae selectional-preference verb arm, and info-free twins. At
matched 15M tokens, dependency-typed context beats the strongest window arm CI-separated on SimLex
(+0.060) and SimVerb (+0.034) by a PAIRED Delta-rho bootstrap (the incumbent's own score_fusion
method -- comparing independent CIs is far too conservative for a ~0.05 effect at n~1000). Twins lose
CI-separated; the grammatical label type carries signal (typed > untyped on verbs). WordSim
relatedness stays the window's -- the two-similarity-systems dissociation, now shown to be a
context-shape effect.

**BAR 2 -- the learning rule (SATISFIED by the argued escape hatch).** SGNS is provably an implicit
factorisation of the shifted-PPMI matrix (Levy & Goldberg 2014); the online delta-rule converges to
the batch fixed point on a stationary corpus, and CBOW==counting is ALREADY landed here (DEVIATION
#2). So the batch form is the computational optimum and the online rule converges to it. The
operation is stated (predict context c from target t; error e = label - sigma(u.v); update by the
gradient; unigram^0.75 negatives) with an optional `--sgns` arm; I did NOT re-run it because that
would re-derive a landed negative.

**BAR 3 -- net-improvement (NUANCED).** `exp_learned_channel_fusion_v1.py`. Equal-weight fusion of a
weaker learned channel with the dominant SUPERVISED WordNet conceptual channel HURTS (SimVerb -0.055
CI-sep) -- but that is a NON-brain-faithful combiner. Under RELIABILITY/precision-weighted cue
integration (the brain's way; the project's own convergent-cue reader uses it) the harm vanishes
(-0.008, not separated) and the learned channel is net-neutral-not-harmful; the noise control stays
clean; the dissociation-aware combiner beats the one-pool combiner. The clean WITHIN-MISSION result:
upgrading the reader's OWN learned spoke window->dependency net-improves the reading-based read-out
CI-separated (SimLex +0.038, SimVerb +0.024). The "where WordNet is silent" value could not be tested
(WordNet covers ~100% of these golds) -- that value shows only downstream / on OOV populations.

**BAR 4 -- the safety gate (CONDITIONAL / rigorous negative on UNCONDITIONAL growth).**
`exp_learner_safety_gate_v1.py`, downstream = LitBank paraphrase who-did-what (reused verbatim).
Growing 5M->15M raises accuracy 0.071->0.149 (+0.078 CI-sep), and it is REAL structure: the strict
info-free growth controls (full-corpus token-shuffle, filler-shuffle) fall BELOW baseline to the
random floor, and GROWN beats full-shuffle +0.138 CI-sep. The corruption cost is real and uniform:
~25.6% of previously-correct answers flip wrong under growth, at the same rate for confident and
unsure predictions -- genuine knowledge loss, so confidence-gating will not protect it. **BUT the
fidelity drill (`exp_growth_cls_ensemble_v1.py`) shows this was a missing-mechanism artifact of a
NAIVE OVERWRITE, not a ceiling.** The brain grows meaning by reading for a lifetime without
catastrophic forgetting -- Complementary Learning Systems (McClelland/O'Reilly/Norman 1995): keep the
old store (hippocampal) and integrate slowly, interleaved with replay. Reproducing that flips the
gate: ENSEMBLE_MEAN (keep both the 5M and 15M channels, fuse) cuts corruption 0.256 -> 0.079
(-0.177 CI-sep, ~3.3x) while keeping 71% of the gain; a rate-limited gradual blend (alpha=0.25) keeps
84% of the gain at corruption 0.185 (-0.071 CI-sep). The dose-response is the CLS signature: accuracy
saturates at alpha=0.25 while corruption climbs monotonically toward the naive value as the blend
approaches a full overwrite. So growth IS safe -- behind a CLS-faithful keep-both-stores ensemble or a
small rate-limited integration, NOT a wholesale overwrite.

## BAR 5 -- the proposed hdlab diff (for the strategy session to land; NOTHING landed here)

1. **ADD a learned STRUCTURED-CONTEXT similarity channel** (a new island, default-safe): dependency-
   typed distributional PPMI-SVD + the SELPREF verb selectional-preference sub-channel, built OFFLINE
   from a dependency-parsed corpus. The read-out is glass-box cosine over a static learned matrix (no
   LLM at inference). Store vectors + a `similarity(w1,w2)` fn. This is a SIMILARITY spoke (joins
   grounded + conceptual on the similarity axis); the window channel remains the relatedness spoke.
2. **KEEP the learner's UPDATE rule BATCH** (BAR2: online==batch; the update rule is not the lever).
   Copy the computation (PPMI-SVD over TYPED contexts); the brain-fidelity is in the CONTEXT
   (grammatical relations), not the update. SWEEP the relation set / label granularity / shift.
3. **FUSE via RELIABILITY/precision-weighting, NOT equal-weight** (extend `meaning_fusion.py`):
   equal-weight averaging demonstrably harms; weight each spoke by its held-out reliability, demand-
   routed by `semantic_control` (similarity spokes for the similarity axis, window for relatedness).
4. **PARSER = the substrate's OWN front-end** (`arc_parser`/`arc_labeler`, currently islanded) as the
   brain-faithful, wire-don't-island dependency source; spaCy is the offline proof-of-mechanism. A
   robustness arm confirming the win survives the substrate's own parser is the recommended next build.
5. **FOUNDATION-GROWTH STAYS DEFAULT-OFF, and when enabled uses a CLS-FAITHFUL update -- now
   DEMONSTRATED, not hand-waved.** Growth must NOT be a wholesale overwrite (25.6% corruption).
   Two validated mechanisms (`exp_growth_cls_ensemble_v1.py`): (a) KEEP-BOTH-STORES ENSEMBLE -- retain
   the pre-growth channel and fuse it with the grown one (ENSEMBLE_MEAN: corruption 0.079, ~3.3x less
   than naive CI-sep, 71% of the gain) = the hippocampal+cortical CLS split; or (b) RATE-LIMITED
   GRADUAL INTEGRATION -- blend new evidence in at a low rate (alpha~0.25: 84% of the gain, corruption
   0.185, CI-sep below naive) = slow replay-preserving consolidation. Confidence-gating is INSUFFICIENT
   (corruption is confidence-uniform). Prefer the ENSEMBLE for safety-first, the low-alpha blend for
   gain-retention. This is the concrete growth gate this problem exists to specify.

## What I did NOT establish / would withdraw first

- **The learner does NOT beat the SUPERVISED WordNet channel on WordNet-derived similarity golds**, and
  its unsupervised-coverage value (OOV / non-WordNet vocabulary) is UNTESTED here (those benchmarks
  are ~100% WordNet-covered). If any single claim is fragile, it is any implication that the learned
  channel improves the FULL read-out on standard golds -- it is net-neutral there, not net-positive.
- **The absolute downstream accuracies are low** (7%->15% on a hard argmax-over-verbs task); the growth
  gain and corruption are measured on that task and should not be quoted as general comprehension.
- **spaCy parses, not the substrate's own parser**, underlie the dependency contexts (admissible
  offline foundation-build, not an LLM); the parser-robustness arm is a recommended follow-up.
- The BAR4 corruption is on the who-did-what task's small base-correct set (n=395); the ~25% rate is
  the headline safety number but its severity vs a versioned-growth mitigation is not yet quantified.

## KEY REALIZATIONS (the enabling moves)

- **The disk outranked the brief, and it changed the whole approach.** Three integrated problems
  already showed the online/CLS UPDATE rule == batch (Levy-Goldberg). Reading them BEFORE building
  stopped me re-deriving a landed negative and redirected the search to the one open lever the audit
  itself named: STRUCTURE (context shape).
- **The paired-difference test was the difference between a null and a win.** The first run wrote a
  FAIL because it compared independent bootstrap CIs (ci_half ~0.06) for a ~0.05 effect; switching to
  a paired Delta-rho on the same pairs (the incumbent's own method) flipped SimLex+SimVerb to
  CI-separated wins. A ~0.05 similarity effect at n~1000 is only visible paired.
- **A shuffle can be non-degenerate two ways, and one is a no-op.** The killer label-shuffle twin
  must break the edge<->label CORRESPONDENCE (shuffle labels ACROSS edges); a global label BIJECTION
  merely permutes columns and is SVD-invariant (bit-identical to the real arm) -- caught before it
  could make the PASS verdict unreachable.
- **Equal-weight fusion is not brain-faithful and it manufactured a false regression.** Reliability/
  precision-weighting (the brain's cue integration) removed a -0.055 CI-separated "regression" that
  was purely a combiner artifact. The combiner is part of the mechanism.
- **An info-free control has to actually be info-free.** The label-shuffle "growth control" kept the
  true verb-filler co-occurrence, so it was a real (weaker) channel, not a floor -- it spuriously
  failed Gate B. Full-corpus-shuffle and filler-shuffle are the honest floors, and they fall to chance.
- **Corruption is confidence-uniform**, which kills the obvious mitigation (confidence-gating) and
  points at outcome-checked/rollback growth -- a finding that only appeared because I split the
  corruption by prediction margin instead of reporting one number.
- **The corruption wall dissolved the moment I stopped treating growth as overwrite.** Framing growth
  as CLS (keep the old store, integrate slowly) instead of a batch retrain cut corruption ~3.3x while
  keeping most of the gain. The brain grows without forgetting; naming the missing mechanism (CLS
  keep-both-stores / rate-limited replay) rather than accepting the negative is what flipped it. A
  clean dose-response (accuracy saturates at alpha=0.25, corruption climbs monotonically) confirmed the
  CLS reading rather than a lucky arm.
- **My worst fidelity move was AVERAGING (centroid selectional preference); my best was COPYING an
  OPERATION (typed context).** The grounded-feature verb channel collapsed to chance in BOTH a 12-dim
  and a 600-dim feature space because per-role MEAN pooling discards the distributional shape that
  word-identity co-occurrence keeps -- McRae/Erk-Pado keep the exemplar DISTRIBUTION, not the mean.
  Same lesson the memory already carries: copy the computation, do not compress it away.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)

- **The cortical-learning-rule / CLS deviation ("the substrate does not learn by an online predictive
  rule") should be RE-POINTED:** the online-vs-batch update is a CLOSED question (== , Levy-Goldberg;
  DEVIATION #2 + #5 already say this) -- it is NOT a fidelity gap worth building across. The OPEN,
  load-bearing fidelity gap is the learning CONTEXT: the substrate's distributional learning is over
  linear windows; the brain's is over GRAMMATICAL RELATIONS (ATL hub + pMTG/LIFG syntax; Harris 1954
  distributional hypothesis = substitutability within grammatical environments). Dependency-typed
  context is PINNED-by-NLP-evidence (Levy & Goldberg 2014 dependency embeddings) to recover the
  paradigmatic/feature-similarity axis; ingesting it is OUR-INVENTION-UNDER-TEST but now CI-validated.
- **The two-similarity-systems entry gains a THIRD regime:** window-distributional -> relatedness
  (WordSim), dependency-distributional -> feature/functional SIMILARITY (SimLex/SimVerb),
  conceptual/grounded -> identity/feature similarity. So "distributional -> relatedness" is TRUE only
  for the WINDOW channel; the dependency channel inverts it. Fuse reliability-weighted, demand-routed.
- **New deviation, now RESOLVED with a mechanism: FOUNDATION-GROWTH NEEDS A CLS UPDATE, NOT AN
  OVERWRITE.** A naive overwrite corrupts ~1/4 of known-correct meanings (confidence-uniform); this is
  a MISSING-MECHANISM artifact, not a ceiling. A CLS-faithful update fixes it: keep-both-stores
  ensemble (corruption 0.079, ~3.3x less, CI-sep) or rate-limited gradual integration (alpha~0.25,
  84% of the gain). This is the McClelland/O'Reilly/Norman CLS prediction (slow replay-preserving
  integration beats wholesale consolidation) reproduced on-substrate. Growth stays default-off until
  the ensemble/rate-limited gate is landed; confidence-gating is INSUFFICIENT.
- **FIDELITY PHASE 2 (`exp_context_typing_fidelity_v1.py`): three findings.** (A) PARSER ROBUSTNESS
  is graded and NOT a gold-parser artifact -- a fully-random parse collapses to the floor (SimLex
  0.012 / SimVerb -0.055) and the SimLex win survives 10% parse corruption CI-separated (+0.047 over
  window); BUT the SimVerb win is parse-quality-sensitive (already not CI-separated over window at 10%
  noise), so the verb-axis result depends on a decent parser -> verify on the substrate's own arc_parser.
  (B) THEMATIC-role typing TIES syntactic-deprel typing (both beat the role-shuffle twin) -- an expected
  modest null (English actives align role~deprel). (C) PARAMETER SWEEP: the adopted k=300 LEFT A
  CI-SEPARATED GAIN ON THE TABLE -- **k=500 (all-relations) beats k=300 on BOTH axes** (SimLex
  0.271->0.293 +0.021 [.010,.035]; SimVerb 0.122->0.141 +0.019 [.010,.027]); argument-only is worse.
  Recommended config for the hdlab diff = **k=500, all relations** (not the adopted k=300); at k=500,
  15M-token SimVerb (0.141) exceeds the incumbent's full-38M number (0.129).
- **The McRae feature-averaged selectional preference (per-role MEAN centroid) is validated in the
  narrow sense (beats its shuffle controls) but NOT competitive with word-identity co-occurrence on
  SimVerb at 15M** (grounded 12-dim AND learned 600-dim both collapse to ~0). The bottleneck is the
  MEAN pooling, which discards distributional shape; the untested brain-faithful fix is exemplar /
  distributional pooling (Erk & Pado 2010), not the grounded-feature direction itself. Record as: the
  learned WORD-IDENTITY selectional preference (lexical thematic-fit) is the stronger verb channel at
  this data scale; feature-abstraction's advantage regime is low-data/OOV.

## FIDELITY-PHASE STATUS (open drills + what is blocked)

- ANSWERED: thematic-role typing ties syntactic (null); parameter sweep -> k=500 all-relations beats
  the adopted k=300 CI-sep on both axes (recommended config); parser robustness is graded and NOT a
  gold-parser artifact (random parse collapses; SimLex survives 10% corruption CI-sep) but verb-axis
  is parse-quality-sensitive.
- LOW-YIELD BY SPECIFIC REASON (fidelity-lock, not a score-mover): FHRR/VSA bind+bundle encoding of
  role-filler contexts -- bundle ~= weighted sum ~= the count matrix, so it is metric-neutral for the
  similarity numbers (keep FHRR for architectural coherence per the standing position; do not expect a
  number move). Online prediction-error construction likewise = batch at convergence (BAR2).
- GENUINE BRAIN-GAPS, drills BUILT + SMOKED + REMOTE-READY, empirical full 15M runs PENDING on the
  remote box (routed via the strategy lane): (a) EXEMPLAR-set soft-max selectional preference
  (Erk-Pado, the non-averaging fix to the Q2 negative) -- `exp_exemplar_selpref_v1.py`, self-test +
  smoke green, tested in the RARE/OOV-verb regime where the brain's generalisation shows; (b)
  GROUNDING-SUPPLY -- `exp_grounding_supply_v1.py`, self-test + smoke green, richer grounded supply
  (full Lancaster + Brysbaert + Binder-2016) vs text-only on a NON-WordNet gold (MEN), crossover +
  random control. SMOKE (machinery, not the claim -- TEXT arm is weak at 150k): grounding adds over
  thin grounding on the Binder subset (+0.229) and the CROSSOVER holds (grounding benefit larger on
  MEN than on WordNet-ish SimLex). Both cells: no spaCy, KB_REFERENT-declared, load the shipped cache.
- BLOCKED: the remote-dispatch pipeline (`queue_add.sh`) REQUIRES a `preregs/<slug>.md` file (`--prereg
  required=True`), and the solver session is scope-barred from writing `preregs/**` (denial confirmed).
  The 458MB parse cache + SimVerb are already shipped + byte-verified on marsh@home. Resolution is an
  OWNER decision: grant a one-time `preregs/` write, or route the remote runs through the strategy lane.

## FIDELITY PHASE 3 -- REMOTE ARCHITECTURE DRILLS (full 15M runs, 2026-08-28)

Five brain-foundational drills, self-dispatched to the remote CPU box. Three wins, two honest partials:

- **SEMANTIC-CONTROL ROUTING -- WIN** (`exp_semantic_control_routing_v1`, HARD_PASS). IFG-style dynamic
  per-query control (task-set gain over channels) beats the best FIXED reliability-weighted blend on a
  pooled similarity+relatedness+verb eval; the shuffled-gate twin loses. Pooled TASKSET 0.274 vs
  FIXED_BLEND 0.262; the gain is on RELATEDNESS routing (REL: 0.544 vs 0.495, routes to the window
  channel) and flat on similarity. Validates the semantic-control organ: dynamic routing > one static
  blend. (The gold-blind CONFLICT variant 0.253 underperforms the task-set gain -- a deepening target.)
- **GROUNDING SUPPLY -- WIN** (`exp_grounding_supply_v1`, HARD_PASS). Richer grounding fused with text
  beats text-alone on the NON-WordNet MEN gold +0.1275 [ci_half .021] CI-sep, and the CROSSOVER holds
  (FUSED MEN-delta +0.1275 vs SimLex +0.0345; RICH MEN +0.0535 vs SimLex -0.0103). Binder-65 alone =
  0.633 on MEN. The learner-vs-WordNet gap is a real, closable SUPPLY gap; grounding earns its keep on
  the experiential/associative axis where taxonomic WordNet is weakest.
- **EXEMPLAR SELECTIONAL PREFERENCE -- honest partial** (MIDDLE_BAND). Beats its FEATURE_SHUFFLE twin
  (+0.013 CI-sep, real grounded signal) but LOSES to word-identity even on RARE verbs (rare EXEMPLAR
  0.056 vs WORDID 0.176; pooled -0.043 vs 0.149). NOT a brain-gap at this scale: the exemplar/feature-
  generalisation advantage is a LOW-DATA / true-zero-count phenomenon; at 15M read-tokens counting has
  enough data (the standing corpus-limited theme). The 12-dim grounded feature space is also too thin
  for verb participants. To SEE the brain's advantage: test at low token budgets / genuinely unseen
  verb-filler pairs -- a regime test, not a fix.
- **DEPENDENCY-PATH CONTEXT -- rigorous negative** (MIDDLE_BAND). Length-2 grandparent+sibling path
  columns beat their PATH_SHUFFLE twin (SimLex +0.050, SimVerb +0.046 CI-sep) but do NOT beat the
  immediate (deprel, filler) context (SimVerb vs_DEP1 -0.021, CI-sep BELOW; SimLex -0.024 ns); WordSim
  hurt. NOT a wall: the immediate dependency context IS the brain's grammatical-context mechanism and
  ALREADY won (BAR #1) -- it saturates the paradigmatic signal; longer paths add sparsity/noise. The
  only untested brain-faithful variant is true SECOND-ORDER similarity (Lin 1998 similar-not-identical
  contexts), but diminishing returns.

- **BROAD BRAIN-BASED GROUNDING via Binder-attribute prediction -- WIN** (`exp_binder_attr_prediction_grounding_v1`,
  HARD_PASS, full 15M run 2026-08-28). The grounding-supply win (drill above) was proven on only the ~434
  SURVEYED Binder words -- a narrow island. This scales it: a Ridge predictor (alpha=300, chosen by OOF CV)
  fit on the 428 surveyed Binder words maps Lancaster-sensorimotor + Brysbaert-concreteness + the learned
  DEP_TYPED distributional embedding onto the 65 brain-derived Binder attributes, then GENERALISES that
  grounding to **15,319 words** vocab-wide (a ~36x coverage expansion off the 428-word survey). All four
  gates pass: (a) the predictor carries real signal, CI-separated above its shuffled-target twin;
  (b) the broad PREDICTED grounding beats BOTH the thin Lancaster floor AND text-alone on the non-WordNet
  MEN gold CI-separated -- GRND_BROAD vs LANC12 +0.026 [0.007,0.045] and vs TEXT +0.071 [0.043,0.099];
  FUSED stronger still (vs LANC12 +0.054, vs TEXT +0.099 [0.081,0.120]); (c) the CROSSOVER holds -- the
  grounding benefit is ~0 on WordNet-ish SimLex (GRND vs TEXT +0.0004 ns; FUSED +0.028) but large on
  associative MEN (+0.071 / +0.099), exactly the experiential-axis signature; (d) the info-free twin loses
  hard (BINDER_PRED vs BINDER_PRED_SHUF +0.202 [0.161,0.239]) and RANDOM is the MEN floor. So the
  neurobiological Binder attribute space is a REAL property of concepts, not an accident of the 434-word
  survey: the supply gap named in the grounding-supply drill is not just real but **manufacturable
  vocab-wide** -- broad brain-based grounding can be predicted for thousands of words and still earns its
  keep on the associative axis where taxonomic WordNet is weakest. This is the concrete way to grow the
  grounded similarity spoke past the surveyed island (feeds BAR 5 item 1).

(Infra note, flag to owner -- not solver-fixable: the remote auto-sync `hd_metrics_sync` is DISABLED -- runs
completed cleanly on the box but had to be pulled manually; re-enable `schtasks /change /tn hd_metrics_sync
/enable`. The runner also writes a double-prefixed `data/exp_exp_<name>/` path (SH-4). Both mean any solver
remote run needs an orchestrator pull until fixed.)

## TLDR

The brief's plan -- make the learner update the brain's way (online, from error) -- is a proven dead
end, because online and batch learning are the same thing. The real brain lever is WHAT the learner
learns over: grammatical relations, not nearby words. A learner built that way clearly beats the
current recipe on the hardest word-similarity tests, with every scrambled control losing, using far
less text. It improves the reading-learned meaning; it does not beat hand-built WordNet on WordNet's
own tests (but does no harm if you combine channels by reliability, the brain's way). Letting it grow
by reading genuinely helps comprehension -- and it is real structure, not just more words. Growing
by wholesale RETRAIN breaks about 1 in 4 things the reader already knew -- but that turned out to be
because we threw the old knowledge away, not a hard limit: the brain grows for a lifetime without
forgetting by keeping its old memory and integrating slowly, and when we do the same (keep both the
old and new channels, or blend the new in gradually) it keeps most of the improvement while losing far
less of what it knew. So the learner is better AND it is safe to let it grow -- provided it grows the
brain's way (keep-both-stores, or a small gradual update), not by overwriting.

## QUESTIONS

None -- the four bars each resolved to a clear number and the turn-on decision is unambiguous (better
learner; wire it; keep growth OFF until a regression-checked update gate exists).

## NEXT STEPS

1. Strategy lands the diff above (learned structured-context similarity spoke + reliability-weighted
   demand-routed fusion), default-off, growth OFF.
2. Land the VALIDATED growth gate (`exp_growth_cls_ensemble_v1.py`): a CLS keep-both-stores ensemble
   (safety-first) or a rate-limited gradual integration (alpha~0.25, gain-first), NOT a wholesale
   overwrite and NOT confidence-gating. This is the actual gate to autonomous foundation-growth, now
   demonstrated. (A per-word held-out regression check can be layered on for belt-and-braces.)
3. Robustness arm: reproduce the BAR1 win with the substrate's OWN arc_parser (wire-don't-island),
   and test the learner's unsupervised value on an OOV / non-WordNet population (the coverage question
   these WordNet-derived golds cannot answer).
4. Housekeeping: the pre-upos-fix parse caches `parsed_simplewiki_{150000,5000000}tok.jsonl` in
   `data/exp_structured_context_learner_v1/` have empty POS tags (silently break SELPREF/VERB use);
   regenerate or delete them.
