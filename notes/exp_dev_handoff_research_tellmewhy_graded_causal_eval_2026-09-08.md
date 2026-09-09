# exp_dev hand-off -- research: TellMeWhy graded/clean causal-selection eval (LEVER B)

**Filed-by**: research sub-agent, 2026-09-08
**Trigger**: notes/research_tellmewhy_graded_causal_eval_2026-09-08.md -- separates mechanism quality from the TellMeWhy single-gold eval ceiling for the causal-selection lineage (`chain_multi_step_plans_and_scripts_for_the_generative_world_model`, 11th triangulation, all 3 formal mechanisms tie base on TellMeWhy non-adjacent single-gold argmax).

**Pause state**: check data/orchestrator_paused.flag before dispatching. Do not ship if flag present.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands TASK + WHY + CONTRACT + AUTONOMY. exp_dev decides anchor names, sweep parameters, threshold formulas, queue routing, and pre-reg bands.

---

## Anchor candidates (rank-ordered)

### 1. 2-candidate TellMeWhy re-slicing disambiguator (HIGHEST PRIORITY -- CPU, cheapest, zero new data)

**What**: for each TellMeWhy non-adjacent question with >2 candidate story sentences, construct a reduced-candidate version keeping only the (single) gold sentence + the single highest-scoring distractor (by whichever existing mechanism's own confidence ranking), collapsing the item to a COPA-shaped 2-way choice. Re-run the already-built sufficiency/necessity/causal-network mechanisms (exp_multistep_forward_transition_v1.py, exp_multistep_necessity_v1.py, exp_multistep_causal_network_v1.py) on this reduced population, same base/twin-control discipline as their original runs.

**Why**: disambiguates the two readings a future COPA/BCOPA win would otherwise conflate. If mechanisms CI-separate at 2-candidate reduction, the eval-ceiling reading is supported (candidate COUNT/noise was the wall, not eval leakiness per se -- COPA would then meaningfully test the SAME wall). If mechanisms still tie even at 2 candidates, the wall is candidate CONTENT/CLEANLINESS, not count -- a COPA win would then be measuring something COPA's clean construction adds, not resolving whether the ORIGINAL TellMeWhy tie was an eval artifact. This is a re-slicing of already-on-disk data (TellMeWhy full non-adjacent population, n=256+935 depending on which cycle's population is reused) -- no new annotation, no new organ. P_deflated=0.30 for CI-separation at 2-candidate (deflated per research's own calibration; MIDDLE_BAND -- ties even at 2 candidates -- is the honest expected outcome given the substrate's own prior 11-way triangulation already located the wall at edge-correctness, which a candidate-count reduction alone does not fix).

**Tier hint**: CPU local, reuses existing mechanism code + existing TellMeWhy loader, ~few minutes wall. Laptop queue.

**Pre-reg bands (for exp_dev to formalize)**: per research note's Falsifiable-prediction-1 (notes/research_tellmewhy_graded_causal_eval_2026-09-08.md, section "Falsifiable predictions"): HARD-PASS-eval-ceiling-reading = CI-separation at 2-candidate comparable to or exceeding the full-population non-separation; HARD-PASS-difficulty-reading = still ties at 2-candidate (equally informative, opposite conclusion); HARD-FAIL-for-the-COPA-program = ties at 2-candidate, meaning a subsequent COPA run (anchor 2 below) would not be interpretable as resolving the eval-vs-mechanism question (though still useful as an absolute-ceiling measurement).

**Cap_map pointer**: informs whether the causal-selection cap_map row's closure (11th triangulation, edge-correctness) should be annotated as "closed independent of eval cleanliness" (if this control also ties) vs. "eval-format-contingent, retest on cleaner benchmarks" (if this control separates).

---

### 2. BCOPA + raw-COPA acquisition and run, with mandatory Kavumba alternatives-only ablation twin (CPU, cheap, static datasets)

**What**: acquire BCOPA (github.com/Balanced-COPA/Balanced-COPA, static XML, 1000 dev items; or HF `datasets` mirror `pkavumba/balanced-copa`) and raw COPA (HF SuperGLUE `copa` config, or original 500 dev/500 test release). Run the SAME already-built glass-box causal-selection mechanisms (no retraining, no fine-tuning -- pure zero-shot scoring, per the research note's confirmed-legitimate offline-eval-instrument reasoning) on both, reporting side by side. REQUIRED: also run an alternatives-only ablation (strip the premise, mechanism sees only the 2 candidate sentences) on RAW COPA as the info-free-style twin -- this certifies any COPA win is not itself surface-cue exploitation (Kavumba et al. 2019 found token-frequency cues alone reach 59.6%+/-2.3% vs 50% chance with the premise stripped).

**Why**: BCOPA is the correct primary clean instrument (kappa=0.965 filtered construction, specifically closes the one documented, quantified artifact class). Raw COPA is the required denominator so any raw-vs-balanced gap is directly attributable, not hidden (same "report both, grade the harder number" discipline already used for the 19th-century-corpus question). Do NOT run only BCOPA or only raw COPA -- the pairing plus the ablation twin is what makes the result interpretable per the research note's Section D artifact-guard requirement.

**Tier hint**: CPU local, static 500-1000 item datasets, trivial to load (BCOPA via static XML parse or HF `datasets.load_dataset("pkavumba/balanced-copa")`; COPA via `datasets.load_dataset("super_glue", "copa")`). No GPU needed. Laptop queue.

**Pre-reg bands (for exp_dev to formalize)**: per research note's Falsifiable-prediction-2: HARD-PASS = mechanisms CI-separate from chance on BCOPA AND the alternatives-only ablation scores at/near 50% chance (no cue-exploitation). MIDDLE_BAND = mechanisms beat chance on raw COPA but not BCOPA, AND the ablation beats chance meaningfully on raw COPA (the "our result was cue-exploitation" finding -- valuable, report it, do not re-file as a fix). HARD-FAIL = mechanisms tie chance on BOTH raw COPA and BCOPA -- strengthens the "wall is edge-correctness regardless of eval" reading from the build-queue's prior 11th-triangulation work.

**Cap_map pointer**: a HARD-PASS here (mechanism discriminates on clean 2-way data) opens a new cap_map row candidate distinct from the closed TellMeWhy-full-population row -- "causal-selection mechanisms work on clean/disambiguated 2-way choices; TellMeWhy's tie is [eval-ceiling|edge-count-noise] per anchor 1's finding." A HARD-FAIL closes the causal-selection mechanism question generally, independent of which eval is used, which is the strongest possible confirmation of the build-queue's own prior conclusion.

**Substrate-product reading**: if HARD-PASS, the practical payoff is a validated glass-box "does A plausibly cause B" 2-way discriminator usable wherever a system needs to choose between exactly two candidate explanations (a narrower but immediately deployable capability than full open-narrative cause-selection) -- directly useful for structured decision-support use cases (e.g., "which of these two prior events explains this outcome") even if the harder open-narrative version remains capped.

---

### 3. Track A graded/frequency reformulation over existing TellMeWhy annotations (CPU, zero new labeling)

**What**: compute per-sentence gold weight = (count of the 3 TellMeWhy annotators who independently flagged that sentence in `helpful_sentences`) / 3, directly from already-released TellMeWhy annotation files (github.com/StonyBrookNLP/tellmewhy) -- no new human labor. Score the EXISTING mechanisms two ways: (i) top-1 frequency credit = the gold weight of whichever sentence the mechanism's argmax lands on; (ii) rank correlation = Spearman's rho between the mechanism's full candidate ranking and the graded weight distribution. Stratify BOTH by annotator-agreement tier (all-3-agree / 2-of-3 / all-diverge / none-flagged, computed from the same data) rather than reporting one pooled number.

**Why**: (i) is expected to be a near-null CONFIRMATION, not a new finding -- the research note proves mathematically that frequency credit is a strict tightening of the union-lenient credit already measured as a located negative (-0.055 CI-sep below base), so it cannot show a materially larger gain; running it is cheap and closes the question formally rather than leaving it as an inference. (ii) is the genuinely untested reformulation -- not mechanically bounded by the union result, but gated by n=3 statistical power (only 4 distinguishable gold values per sentence) and a 43.3% empty-flag-set rate in the underlying data (many questions have zero annotators flagging any sentence). P_deflated=0.10 for (i) showing a material gain (near-impossible by construction, run mainly to formally close it); P_deflated=0.25 (capped, novel-synthesis) for (ii) showing full-population CI-separation; MIDDLE_BAND (real signal on the ~14.6% high-agreement stratum only) is the calibrated-expected honest outcome for (ii).

**Tier hint**: CPU local, pure re-aggregation of already-on-disk annotation files + existing mechanism outputs, ~minutes wall. Laptop queue.

**Pre-reg bands (for exp_dev to formalize)**: per research note's Falsifiable-prediction-3: HARD-PASS = Spearman rho CI-separates from a shuffled-ranking null on the high-agreement (>=2-of-3) stratum. MIDDLE_BAND = separates on high-agreement stratum only, ties on full population. HARD-FAIL = ties the shuffled-ranking null even on the high-agreement stratum -- closes this reformulation without needing the costlier Track B new-annotation pass to be attempted.

**Cap_map pointer**: informs whether a graded-eval reformulation should be adopted as the STANDARD TellMeWhy scoring going forward for this lineage, or whether single-gold argmax (despite its known leakiness) remains adequate because the graded version adds no discriminating power even where annotators agree.

---

## Context pointers

- Research note (full synthesis): notes/research_tellmewhy_graded_causal_eval_2026-09-08.md
- Build-queue state (why this lever matters now): notes/problems/chain_multi_step_plans_and_scripts_for_the_generative_world_model/CONTEXT_HANDOFF_POST_COMPACTION_2026-09-08.md
- 11th-triangulation located negative (all 3 mechanisms tie, structure=shuffle): notes/problems/chain_multi_step_plans_and_scripts_for_the_generative_world_model/CAUSAL_NETWORK_RESULT_2026-09-08.md
- Prior located negatives (do not re-run, reuse the twin-control pattern): notes/problems/chain_multi_step_plans_and_scripts_for_the_generative_world_model/NECESSITY_RESULT_2026-09-08.md, FORWARD_TRANSITION_RESULT_2026-09-08.md
- Why TellMeWhy gold measures best-explanation/relevance, not strict necessity (explains WHY the tie happens, complements this note's eval-fix): notes/research_resolution_wall_and_gold_semantics_2026-09-08.md
- Existing mechanism cells to reuse (do NOT rebuild): experiments/exp_multistep_forward_transition_v1.py (sufficiency), experiments/exp_multistep_necessity_v1.py (necessity), experiments/exp_multistep_causal_network_v1.py (structure), experiments/exp_multistep_meansend_chain_v1.py (goal engine + ladder pattern for stratified reporting).
- TellMeWhy gold + annotation loader: data/corpora/tellmewhy/ (TMW.load_items) -- confirm `helpful_sentences` field is accessible per-annotator (not pre-collapsed) before building anchor 3.
- BCOPA: github.com/Balanced-COPA/Balanced-COPA or HF `datasets` id `pkavumba/balanced-copa`. Raw COPA: HF `datasets` id `super_glue` config `copa`.

---

## Contract section

exp_dev owns: anchor names, sweep parameter choices, exact threshold formulas, queue routing (CPU vs GPU -- all 3 anchors are CPU-cheap, no GPU expected needed), pre-reg band specification, script implementation, and confirming e-CARE's standard-loader status before treating it as equally turnkey (not verified this cycle per the research note).

Research has provided: the eval-methodology derivation (why frequency credit is mechanically bounded by the union result), the benchmark-selection reasoning (BCOPA over raw COPA or e-CARE as primary instrument, with citations), the disambiguation-control design (2-candidate re-slicing), P_deflated estimates, pre-reg threshold GUIDANCE (not specification), queue tier hints, and product framing.

---

## Autonomy declaration

exp_dev has full autonomy over experiment implementation details. The three anchor candidates above are RANKED RECOMMENDATIONS, not mandatory sequencing, though the research note's own reasoning is that anchor 1 (2-candidate control) should run BEFORE anchor 2 (BCOPA acquisition) because it decides whether a COPA/BCOPA result would even be interpretable for the specific eval-ceiling-vs-mechanism-cap question this lever was dispatched to answer -- BCOPA acquisition itself is free/instant regardless, so exp_dev may parallelize acquisition with anchor 1's run if that is cheaper in practice. Anchor 3's sub-item (i) (top-1 frequency credit) is expected to be a fast, near-certain-null confirmation and should not be treated as requiring the same scrutiny as (ii) (rank correlation) or anchors 1-2. Do NOT build the Track B new-human-annotation pass (a small rating panel, described in the research note's Section A) until anchors 1-3 have run and the eval-vs-mechanism question remains genuinely open -- it is the costliest lever in the note and is explicitly sequenced last.
