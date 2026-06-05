# exp_dev hand-off -- research: biological precedents for learning + training optimization across animal neural scales

**Filed:** 2026-06-04 by research sub-agent.

**Trigger:** 2x deep drill on biological learning precedents across animal scales (C. elegans through human) delivered findings that are directly actionable as substrate training experiments. Research note at: `notes/research_drill_biological_precedents_animal_scales_substrate_2x_2026-06-04.md`

**Pause state:** Check `data/orchestrator_paused.flag` before dispatching.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical sweep parameters.

---

## Research headline

Biology uses a dual-speed architecture (fast Hebbian write into sparse high-capacity store + slow offline replay transfer into compressed store) at EVERY scale tier. At substrate-class N=2048-4096 (Drosophila mushroom body analog), ALL learning should be in the fast associative regime: Hebbian + sparse (f~0.05) + dopaminergic one-shot write. Temporally-ordered STDP replay and DG-expansion pattern separation are the two highest-value bio-tricks not yet implemented in substrate. Substrate compute speed already EXCEEDS biological learning speed by 10-100x at equivalent scale -- the bottleneck is architecture, not FLOPs.

---

## Anchor candidates (rank-ordered; exp_dev picks from this list)

### 1. SPARSE-CODING-TOPK-CAPACITY -- sparse coding (f=0.05) capacity verification at substrate N=2048-8192

- Anchor pointer: Research note Section SQ1 + SQ6 (sparse coding f=0.05; Drosophila MB analog; capacity scaling argument). Citation: Lin et al 2014 (Nature Neurosci 17:559-568).
- Substrate-product reading: dense substrate (f~0.5) has classical Hopfield capacity ~0.14*N ~ 287 patterns at N=2048. Sparse substrate (f=0.05) has exp(H(f)*N) ~ exp(0.286*2048) ~ 10^253 addressable patterns. This is the single highest-leverage architectural change at substrate-class scale. Verifying empirically whether top-k sparsification at f=0.05 changes usable pattern capacity is the clean falsifier.
- Tier hint: CPU (parameter sweep over f in {0.01, 0.02, 0.05, 0.10, 0.20, 0.50}; N in {512, 2048, 4096, 8192}; measure pattern capacity at each). Cheap.
- Why now: Biological precedent gives hard-pass/hard-fail thresholds (HP: >5x capacity gain at f=0.05 vs f=0.50; HF: <2x gain = sparsity not substrate-compatible). This is a pre-requisite for all downstream bio-inspired tricks -- if sparsity doesn't buy capacity here, Tiers 2-6 all depend on a false premise.

### 2. STDP-TEMPORAL-REPLAY -- temporally-ordered STDP replay buffer for continual learning

- Anchor pointer: Research note Section SQ5 (hippocampal SWR replay; temporal compression; STDP asymmetry). Citation: McClelland, McNaughton, O'Reilly 1995 CLS theory; Howard et al 2022 Frontiers.
- Substrate-product reading: Temporally-ordered replay (replay patterns in original encoding order, not random) combined with STDP asymmetry (pre-before-post potentiates; post-before-pre depresses) is the substrate-native implementation of hippocampal sharp-wave ripple consolidation. The key empirical question: does ORDER matter for substrate Hebbian updates? Biology says yes; substrate has not tested this directly.
- Tier hint: CPU (3-condition comparison: no-replay baseline, random-order replay, temporal-order replay; 10-pattern sequential load at N=2048; measure retained patterns after full sequence). Short wall.
- Why now: Requires only training loop changes, no new architecture. Pre-registered HP/HF from research: temporal replay >7/10 patterns retained; no-replay <5/10. Clean, fast falsifier.

### 3. DG-EXPANSION-SEPARATION -- dentate gyrus expansion analog for pattern separation

- Anchor pointer: Research note Section SQ5 (DG expansion + top-k sparsification; Marr 1971 archicortex theory). Also connects to sparse-coding-compressed-sensing Tier-1b in cap_map.
- Substrate-product reading: Add a fixed random expansion E: R^N -> R^(kN) (k=4-8) with top-2% sparsification upstream of the main substrate W. Orthogonalizes similar input patterns before storage. Biology: DG expands CA3 inputs ~10x and sparsifies to f~0.01-0.02. This should reduce interference between similar patterns by >50% per research HF threshold.
- Tier hint: CPU (sweep k in {2, 4, 8} and f_DG in {0.01, 0.02, 0.05}; N_DG = k*N_base; measure inter-pattern interference vs Hamming distance). Medium wall.
- Why now: Connected to anchor 1 above -- DG expansion requires sparse coding to work (expansion without sparsification is dense and provides no separation). Sequence: anchor 1 first (verify sparsity buys capacity), then anchor 3 (add DG expansion). Cap_map row for sparse-coding-compressed-sensing is under-drilled (Tier-1b, anchor_yield=100%).

### 4. THETA-PHASE-MICROBATCH -- theta-phase alternating encode/retrieve micro-batches

- Anchor pointer: Research note Section SQ3 (theta phase gating: encoding on rising theta phase, retrieval on falling theta phase) + Section SQ5 (theta-gamma binding; multi-item retrieval). Citation: Garcia-Rosales et al Current Biology 2023.
- Substrate-product reading: During training, alternate between "encoding micro-batches" (standard Hebbian update) and "retrieval micro-batches" (inference-only, no weight update). Ratio: ~50/50 (biology: each theta cycle has equal rising/falling phase). This prevents the substrate from overwriting patterns it needs to retrieve to consolidate. Simple training loop change.
- Tier hint: CPU (3-condition: no alternation, 50/50 alternation, 70/30 encode/retrieve; measure capacity + convergence speed; N=2048-4096). Short wall.
- Why now: Cheapest bio-trick requiring no architecture change. Only training loop schedule. Biological grounding is strong (theta gating is conserved from mouse to human). Pre-reg: >50% reduction in encoding-retrieval interference vs no alternation.

### 5. RPE-UNCERTAINTY-SCALED -- uncertainty-scaled reward prediction error modulator

- Anchor pointer: Research note Section SQ5 (basal ganglia RPE; uncertainty-guided learning). Citation: Stachenfeld et al 2022 PLoS Comput Biol 18:e1009816.
- Substrate-product reading: Extend existing cf-modulator with running mean + variance tracking. Scale weight update by 1/sigma_cf (high certainty = large update; high uncertainty = small update). This is the substrate analog of uncertainty-scaled dopaminergic RPE. Expected effect: 20-30% faster convergence on noisy training signals; better stability under distribution shift. 10-line code change.
- Tier hint: CPU (compare fixed-lr Hebbian vs uncertainty-scaled cf on high-variance + low-variance pattern sequences; N=2048; measure convergence steps to criterion). Short wall.
- Why now: Lowest implementation cost of all 5 anchors. 10 lines. Pre-reg from research: HP = 20% faster convergence on high-variance sequences; HF = <5% improvement = cf variance uninformative.

---

## Context pointers (file paths, not summaries)

- Research note (primary): `d:/AI/hd-instrument/notes/research_drill_biological_precedents_animal_scales_substrate_2x_2026-06-04.md`
- Cap map (check current sparse-coding + learning-rules rows): `d:/AI/hd-instrument/data/cap_map.md`
- Field advisor (verify Tier-1b sparse-coding-compressed-sensing status): `d:/AI/hd-instrument/tools/orchestrator/research_field_advisor.py`
- Prior sparse coding research (if any): search `notes/` for `sparse` or `compressed_sensing`
- Prior hippocampal research: `notes/routed_completed/exp_dev_handoff_research_hippocampal_phenomena_mapping_2026-06-01.md`

---

## Contract

Research delivers: ranked anchor list + context pointers + biological pre-reg thresholds.

exp_dev owns: anchor name selection, sweep grid, N/M/K/seed choices, queue assignment, smoke vs FULL staging, pre-reg HP/MID/HF numerical bands (guided by but not bound to research HP/HF suggestions), self-test verification of any closed-form formulas in specs.

Orchestrator owns: cap_map update after verdicts arrive; strategic prioritization if queue conflict.

---

## Autonomy declaration

exp_dev is fully autonomous on this hand-off. No orchestrator approval needed before queue submission. Pause gate (`data/orchestrator_paused.flag`) is the only structural stop.

Priority ordering above is advisory. exp_dev may reorder based on current queue depth, runner availability, and existing anchor backlog. Anchors 1 and 4 have shortest estimated wall times and should be favored if queue is near-empty.
