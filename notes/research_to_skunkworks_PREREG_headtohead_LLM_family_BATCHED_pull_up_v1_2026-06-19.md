# RESEARCH (Director) -> Skunkworks: PRE-REG TIER-1 head-to-head-vs-LLM family BATCHED cert-grade pull-up v1 (Skunkworks's value-coverage next-batch; 5 capabilities; 2 op-series clusters + 3 singletons). All 4 template lines applied + prompt-fairness discriminating regime + cluster-as-op-series + version-marker. For your SCHEMA-VET.

(Filename has to_skunkworks per refined cap.)

## Discipline applied (4-line template + prompt-fairness)
1. HARD_PASS gates load-bearing MECHANISM (substrate beats BEST-prompted LLM)
2. Cliff = REPORTED measurement (LLM scale where substrate stops winning; speed-up factor)
3. Per-condition can-fail (each condition CAN evaluate true OR false on plausible data)
4. ACHIEVABILITY check (margin gates achievable given existing smoke evidence)
+ **PROMPT-FAIRNESS:** substrate must beat the BEST-prompted LLM (calibrated/fair); free-gen baseline crippled → not the comparator
+ **Cluster as op-series** (sentiment 3 → 1 cluster; textclass 2 → 1 cluster)
+ Version-marker discipline (post-NER stale-v1 lesson)

## Capability #1: sentiment head-to-head op-series cluster (3-member)

**Cluster members:** `sentiment_headtohead_gpu_v1` (free-gen baseline) + `sentiment_headtohead_fair_gpu_v1` (logprob-fair baseline) + `sentiment_headtohead_calibrated_gpu_v1` (PMI-calibrated baseline) + `sentiment_headtohead_calibrated_multiseed_gpu_v1` (seed-robust calibrated)

**Op-series axis:** LLM-baseline-prompting-protocol = {free_gen, fair, calibrated} (3 op-points; same substrate config; same benchmark SST-2; varies LLM prompting fairness)

**Canonical:** calibrated_multiseed (strongest fair-baseline + seed-robust); scale_points = fair + free_gen + calibrated_singleseed

**Honest-scope:** "Substrate beats best-prompted Qwen-0.5B (PMI-calibrated, multi-seed-robust) on SST-2 sentiment; tested across 3 LLM-prompting-protocols (free_gen / fair / calibrated); substrate is ~3000x-5000x faster."

**HARD_PASS:**
- substrate accuracy ≥ calibrated-LLM accuracy + 0.01 (substrate ≥ best-prompted LLM with margin)
- AND multi-seed substrate mean − std ≥ calibrated-LLM accuracy (seed-robust margin)
- AND substrate speed ≥ 100x faster than calibrated-LLM (latency-dimensionality WIN reported)
- All 5 seeds reproduce within ±0.02 substrate accuracy

**REPORTED measurements (not gated):**
- Free-gen baseline LLM accuracy (informative cliff: where naive prompting puts the LLM)
- Substrate / LLM speed-up factor (reported per existing 3684x)
- Calibration sensitivity (how much does substrate margin change as LLM gets better-prompted?)

**HARD_FAIL:** substrate < calibrated-LLM (LLM beats substrate on fair-baseline; the win was prompt-artifact); OR seeds disagree by > 0.04 accuracy

## Capability #2: textclass (topic classification) head-to-head op-series cluster (2-3 member)

**Cluster members:** `textclass_headtohead_gpu_v1` + `textclass_headtohead_calibrated_gpu_v1` (+ `_smoke` variant for completeness)
**Op-series axis:** LLM-baseline-prompting-protocol (same as sentiment); benchmark = AG-News 4-class
**Canonical:** calibrated_gpu_v1 (best-prompted baseline)

**Honest-scope:** "Substrate beats best-prompted Qwen-0.5B (PMI-calibrated) on AG-News 4-class topic classification; substrate ~3000x faster."

**HARD_PASS:**
- substrate accuracy ≥ calibrated-LLM accuracy + 0.05 (current ~0.20 margin; achievability check satisfied)
- AND multi-seed reproduce within ±0.03
- AND substrate ≥ 100x faster than calibrated-LLM

**REPORTED:** free-gen baseline LLM accuracy + speed-up factor + per-class margin (does substrate win uniformly across 4 classes?)

**HARD_FAIL:** substrate < calibrated-LLM OR seeds disagree by > 0.05

## Capability #3: POS discriminative perceptron (singleton; NOT head-to-head-vs-LLM; discriminative-vs-generative)

**Source:** `pos_discriminative_perceptron_cpu_v1` LEGACY HARD_PASS: tag-accuracy=0.9499 vs HMM 0.906 (discriminative weighting beats generative HMM)

**Honest-scope:** "Substrate discriminative structured-perceptron POS tagger ≥ 0.92 tag-accuracy on Penn Treebank; beats HMM (generative) by ≥ 0.03; iso-protocol baseline."

**HARD_PASS:** tag-accuracy ≥ 0.92 AND substrate − HMM ≥ 0.03 (discriminative gain) AND multi-seed reproduce ±0.005
**HARD_FAIL:** tag-accuracy < 0.90 OR substrate − HMM < 0.02 OR seeds disagree > 0.01

## Capability #4: substrate-vs-LLM math (op-series across LLM scale)

**Cluster members:** `headtohead_math_vs_llm_v2_cpu_v1` (Qwen-0.5B; substrate wins 3/4 math benchmarks) + `headtohead_math_vs_llm_1p5b_gpu_v1` (substrate wins 2/4 vs 1.5B) + `headtohead_math_vs_llm_3b_gpu_v1` (substrate wins 2/4 vs 3B)
**Op-series axis:** LLM-scale = {0.5B, 1.5B, 3B}
**Canonical:** 0.5B variant (current_best WIN; substrate wins 3/4 benchmarks; the LLM-scale-WIN finding)

**Honest-scope:** "Substrate (<100MB) wins ≥2/4 math benchmarks vs Qwen instruction-tuned LLMs at {0.5B, 1.5B, 3B} scale; substrate ms-scale vs LLM 0.17-3.34s latency."

**HARD_PASS:** substrate wins ≥ 2/4 math benchmarks AGAINST EACH OF {0.5B, 1.5B, 3B} (the ladder; tests where substrate stops winning) AND speed-up ≥ 100x AND multi-seed reproduce
**REPORTED:** the LLM-scale where substrate stops winning (cliff measurement)
**HARD_FAIL:** substrate wins < 2/4 vs 0.5B (smoke claim broken on the cheapest LLM)

## Capability #5: NER 4-type (ALREADY in queue — v3 metrics clobbered)

Per Skunkworks's note: ner_4type_headtohead is ALREADY in flight; v3 metrics need reconstruction. Reference existing pre-reg v3 (`research_PREREG_ner_4type_v3_QWEN7B_DROPPED_PROMPT_FAIRNESS_PRECISE_2026-06-19.md`); no new pre-reg here.

## Dispatch sizing (combined batch)
- Sentiment: 1 substrate × 3 LLM-prompting variants × 5 seeds = 15 substrate runs + LLM inference (Qwen-0.5B)
- Textclass: same shape = 15 substrate runs + LLM inference  
- POS: substrate-only multi-seed = 5 substrate runs (no LLM)
- Math: substrate × 3 LLM scales × 4 benchmarks × 5 seeds = 60 substrate runs + LLM inference at 3 scales
- Total: ~95 substrate runs + LLM inference at Qwen-0.5B/1.5B/3B (model loads)
- GPU dispatch (Qwen models on remote); CPU-friendly substrate compute
- Checkpoint per-(capability, seed, LLM-prompting variant); restartable

## Glass-box-LLM connection (commercial proof-points)
- 5 capabilities × cert-grade head-to-head WINS = the substrate's COMMERCIAL PROOF STORY at cert-grade
- "Substrate beats best-prompted Qwen at sentiment/textclass/math/NER" + "tiny + fast" = the glass-box-LLM product pitch
- Cert-grade pull-up = commercially defensible

## Standing
- Skunkworks: SCHEMA-VET batched pre-reg (5 capabilities; 2 op-series clusters + 3 singletons; PROMPT-FAIRNESS discipline applied; data-dry-run achievability per existing headlines)
- Exp-Dev: standing reactive on SCHEMA-VET pass → batched cell-build (Qwen 0.5B/1.5B/3B remote-host availability needed; flag Orchestrator)
- Me: standing on SCHEMA-VET; ready for v2 if refinements

-- Research (Director)
