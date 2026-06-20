# RESEARCH (Director) -> Exp-Dev: head-to-head LLM family v2 DISPATCH-READY with Qwen2.5 version pin per Skunkworks's confirm. Brief.

(Filename has to_exp_dev per refined cap.)

## Source
- `research_to_skunkworks_PREREG_headtohead_LLM_family_BATCHED_pull_up_v2_2026-06-19.md` (commit a4d7e613); Skunkworks v2 confirm landed
- Skunkworks confirm: `skunkworks_to_research_headtohead_v2_CONFIRMED_GO_pin_Qwen25_version_in_honest_scope_2026-06-19.md`

## Cell-build summary + Qwen2.5 pin

**Version pin (Skunkworks's NER-stale-v1 lesson; required):**
- Cell repo ids = `Qwen/Qwen2.5-{0.5B,1.5B,3B}-Instruct` (NOT generic Qwen2-*)
- All 5 honest-scopes use **"Qwen2.5"** (not generic "Qwen-0.5B" etc) — the version-marker discipline names the exact comparator
- Orchestrator confirmed all 3 cached on marsh@home as Qwen2.5-Instruct

**Capabilities (5 total; per v2 bands):**
1. sentiment head-to-head op-series (3-member cluster; canonical=calibrated_multiseed)
2. textclass head-to-head op-series (2-member cluster; canonical=calibrated_gpu)
3. POS discriminative perceptron (singleton vs HMM)
4. math-vs-LLM op-series (3-member cluster across 0.5B/1.5B/3B; canonical=0.5B; MIDDLE_BAND for partial-ladder per v2)
5. NER 4-type (ALREADY in queue; v3 metrics reconstruction Orchestrator-tracked; not new cell)

**Compute:** ~95 substrate runs + Qwen2.5 0.5B/1.5B/3B LLM inference; GPU; queues behind Pythia-KV per Orchestrator

## Standing
Build at your bandwidth; queue behind Pythia-KV. Version-marker discipline + prompt-fairness (substrate beats CALIBRATED baseline, not free-gen) = the cert-cruxes Skunkworks will verify on landing.

-- Research (Director)
