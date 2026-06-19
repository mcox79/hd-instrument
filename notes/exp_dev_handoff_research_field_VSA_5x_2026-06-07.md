# exp_dev hand-off -- research: VSA algebraic foundation 5x drill

**Filed:** 2026-06-07 by research sub-agent (5x fan-out VSA field drill).
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md
**Pause state:** Check data/orchestrator_paused.flag before queueing any GPU anchors.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names anchors and pointers only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, full profile. Orchestrator and research do NOT specify numerical parameters.

---

## Anchor candidates (rank-ordered)

### 1. MAP permutation sequence encoding -- pre-test smoke (HIGHEST PRIORITY)

- Anchor pointer: research note Section "Path 1: MAP permutation for sequence encoding"
- Substrate-product reading: substrate has no native ordered-sequence representation; permutation-based binding is the VSA-standard solution (MAP Permute operation); directly enables bitemporal temporal-sequence product capability; 5-line code change
- Tier hint: LOCAL CPU smoke (30 min); no GPU required for pre-test at K=5 positions N=4096
- Why now: highest P_deflated (0.50) of all four extension paths; lowest implementation risk; directly unblocks a validated product gap (bitemporal temporal reasoning); pre-test is near-zero cost

### 2. Resonator capacity theory vs empirical cliff match -- analysis anchor

- Anchor pointer: research note Section "Path 2: Resonator network capacity analysis" + Section "Cross-thread synthesis -- K/N=0.56 cliff"
- Substrate-product reading: Frady Resonator-2 capacity formula predicts convergence drop near codebook size limit; substrate's empirical K=2944 dip in acf_K_dependent_extended is consistent; applying the formula to empirical data gives a theoretical grounding for the K/N=0.56 cliff OR reveals a substrate-specific finite-N deviation worth investigating
- Tier hint: LOCAL CPU analysis (2 hours); no model training; pure data analysis comparing formula to existing results in data/exp_acf_K_dependent_extended/
- Why now: zero engineering cost; either confirms theoretical grounding (cap_map annotation) or opens a new research direction (finite-N correction)

### 3. HDC classifier readout as alternative retrieval primitive -- smoke

- Anchor pointer: research note Section "Path 5: VSA classifier as a substrate readout primitive"
- Substrate-product reading: HDC classifiers bundle per-class training examples into class hypervectors then classify by nearest-class lookup; as a substrate readout this enables category-retrieval without per-fact Hopfield lookup; may be faster for classification-style queries at scale
- Tier hint: REMOTE CPU smoke (2 hours); no GPU required at K=4 N=4096 scale
- Why now: P_deflated 0.40; cleanly separable from Pattern B production stack (can be validated as a parallel retrieval path without modifying existing stack)

### 4. Compressed sensing phase transition analogy -- analysis

- Anchor pointer: research note Section "(5.2) VSA compressed sensing analogy"
- Substrate-product reading: bipolar Bernoulli random matrices have a published CS phase transition threshold; if this matches K/N=0.56 it provides a second independent theoretical derivation of the capacity cliff; if it does not match it indicates the Hopfield cleanup step is providing capacity beyond what linear CS theory predicts (which is itself a capability claim worth documenting)
- Tier hint: LOCAL analysis; look up bipolar Bernoulli CS threshold in compressed sensing literature (Donoho-Tanner phase transition); compare to K/N=0.56 empirical value
- Why now: zero cost analysis; either confirms existing result or reveals a new "substrate exceeds CS theory prediction" capability claim

---

## Context pointers

- Research note (primary): d:/AI/hd-instrument/notes/research_drill_field_VSA_algebraic_foundation_5x_2026-06-07.md
- Substrate capability map: d:/AI/hd-instrument/notes/substrate_capability_map.md (Pattern B, ACF resonator, cap rows)
- Resonator empirical data: data/exp_acf_K_dependent_extended/metrics.json (K=2944 dip)
- Pattern B production evidence: cap_map rows for decomposition, pool retrieval, resonator ACF (all validated)
- Frady Resonator-2 paper: arxiv 1906.11684 / Neural Computation 32(12) 2020 (capacity formula in Section 4)

---

## Contract

exp_dev: when you pick up this hand-off file, treat Anchor 1 (MAP permutation smoke) as the highest-priority local CPU item if the local queue has capacity. Anchor 2 (resonator theory match) is pure analysis with no queue submission needed -- it is a read + compute + annotation task. Anchors 3 and 4 are secondary; queue when local CPU has space.

Do NOT submit any of these anchors to the GPU queue. All four paths are CPU-tractable or analysis-only at the pre-test stage.

## Autonomy declaration

exp_dev owns: anchor naming, N/K/M parameter choices, seed counts, threshold bands, queue routing, smoke vs full profile decision, timing. Research has pre-registered P_deflated estimates and HARD-PASS/HARD-FAIL bands in the research note; these are starting priors, not constraints on exp_dev's pre-registration choices.
