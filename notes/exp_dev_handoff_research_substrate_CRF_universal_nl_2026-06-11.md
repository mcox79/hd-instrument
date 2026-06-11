# exp_dev hand-off -- research: substrate-CRF as UNIVERSAL discriminative structured prediction primitive

**Filed:** 2026-06-11 by research sub-agent (companion to `notes/research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md`).

**Trigger:** 2x DEEP research drill on the unification hypothesis (substrate-CRF subsumes 11+ NL structured prediction tasks under one library + per-task feature templates + per-task Tier-2 schemas). Lit-precedent unusually clean (IllinoisSL + Torch-Struct + Collins + Lafferty direct); substrate-novel synthesis is the bundle-as-CRF-feature integration + typed-relational features no classical or LLM-CRF stack can use. P_deflated=0.55. Cap_map consolidates 11 separate validated NL rows into ONE primitive row at tier-load-bearing if the pilots HARD-PASS.

**Pause state:** check `data/orchestrator_paused.flag` at pickup. If PAUSED, structural pilots (UNIFICATION-PILOT-1/-2/-3) STILL ALLOWED because they are substrate-classical CPU re-runs against already-validated tasks (no production-claim shift); ship-grade extension to 7 new tasks is GATED until resume.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor names, ETA, smoke profile, FULL profile. Research note specifies HARD-PASS / HARD-FAIL bands; exp_dev picks the concrete pre-reg fail bands per envelope-fail-bands.

---

## What this research drill closed

The substrate-CRF unification hypothesis was 2x-deep-drilled with parallel lit-scan (4 WebSearch breadths + targeted follow-ups). The unification holds at the lit level: MLR is the degenerate CRF (Sutton-McCallum 2012), arc-factored MST dep-parse is structured-perceptron on Eisner (McDonald 2005), BIO sequence labeling is linear-chain CRF (canonical), and the library design pattern is industrially validated (IllinoisSL Chang 2015 + Torch-Struct Rush 2020). The substrate-distinguishing feature is typed-relational substrate-bundle feature templates that classical CRFs cannot include without combinatorial feature engineering and LLM-CRF heads do not expose. P_deflated=0.55.

Three cheap CPU pilots gate the unification claim before v1 library ships.

---

## Top-N ANCHORS (rank-ordered; exp_dev picks at least the top 3)

### 1. UNIFICATION-PILOT-1 -- Substrate-CRF library reproduction of 4 anchor tasks

- **Anchor pointer:** Section (b) UNIFICATION-PILOT-1 of `notes/research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md`.
- **Substrate-product reading:** validates that ONE library API covers chain (POS) + flat (math op-class would-be flat extension; intent / sentiment / text-class as flat) + arc-factored-tree (dep-parse) + BIO (slot-filling) WITHOUT regressing any of the 4 already-validated baselines (POS 0.9499, dep-parse 0.787, slot-filling 0.871, math op-class published band). Threshold: reproduce all within +/- 0.01 absolute.
- **Tier hint:** Tier-2 (CPU) -- substrate-classical, no GPU, no LLM. ETA ~2-3 hr.
- **Why now:** highest-confidence pilot in the drill; direct lit-precedent on each individual task; only the library abstraction is novel. If HF1 fires (any task drops >0.02), the unification API has a per-task incompatibility and the library design needs re-thinking BEFORE the more speculative pilots run.

### 2. UNIFICATION-PILOT-2 -- Cross-task feature transfer ablation

- **Anchor pointer:** Section (b) UNIFICATION-PILOT-2 of the same research note.
- **Substrate-product reading:** identifies which feature templates are TASK-UNIVERSAL (lift >=0.01 on >=4 tasks) vs TASK-SPECIFIC. Validates the "shared infrastructure" claim operationally -- if zero templates are universal, the library savings are marginal and the unification reduces to "shared decoder only".
- **Tier hint:** Tier-2 (CPU). ETA ~1-2 hr. Ablation runs are short; multiple seeds for stability.
- **Why now:** the universal-template existence claim is the second load-bearing assumption of the unification (after library reproduction). If HF2 fires, the substrate-CRF library still works but per-task feature engineering remains expensive and the cross-task efficiency wedge collapses.

### 3. UNIFICATION-PILOT-3 -- Layer 1 attribution pre-ship gate

- **Anchor pointer:** Section (b) UNIFICATION-PILOT-3 of the same research note + cross-reference to `notes/research_drill_layer4_dialectic_methodology_2x_2026-06-11.md` (attribution self-check primitive).
- **Substrate-product reading:** validates that structured-perceptron weight magnitude predicts held-out lift (Spearman rho >= 0.60 per task). If yes, Layer 1 attribution becomes the pre-ship feature-template filter, making the extension to 7 more tasks tractable WITHOUT full ablation per task. If no, every new task needs N feature ablations to ship, killing the rapid-extension claim.
- **Tier hint:** Tier-3 (CPU, fast). ETA ~30 min once PILOT-1 ships with logged weights.
- **Why now:** PILOT-3 is the CHEAPEST of the three pilots and gates the operational viability of the library for new tasks. Run as the final closure check on the unification trilogy.

### 4. UNIFICATION-EXTENSION-1 -- NER F1 rescue under substrate-CRF library

- **Anchor pointer:** cross-reference to `notes/research_drill_ner_substrate_paths_2x_2026-06-11.md` (BIO-constrained Viterbi + gazetteer + bigram + cascade-from-POS).
- **Substrate-product reading:** NER F1 0.58 -> 0.85+ rescue using substrate-CRF library: BIO-encoded labels in the schema, Wikipedia gazetteer feature template, bigram boundary template, cascade T_pos (POS output as feature) -- ALL feature-template additions on the same library. If PILOT-1/2/3 pass and EXTENSION-1 reaches F1 >= 0.80, the library extension claim is validated for the highest-value missing task.
- **Tier hint:** Tier-2 (CPU). ETA ~2 hr.
- **Why now:** NER is the lowest-confidence task in the 11-row list and the largest gap-to-baseline; if substrate-CRF library handles it cleanly, the unification framework is empirically validated at the boundary case.

### 5. UNIFICATION-EXTENSION-2 -- 2-op compositional math + code algopattern under k-best-tree decode

- **Anchor pointer:** cross-reference to `notes/research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md` (joint 1-op+2-op scoring) + Section (d) drill-8 of the substrate-CRF universal note.
- **Substrate-product reading:** validates that bounded-depth (height-2) tree CRF decode subsumes the compositional 2-op regime. Bounded operator alphabet (~10-20 math ops, ~10-15 code algopattern templates), k-best-tree decoder, structured perceptron training. If reaches the joint band [0.42, 0.50] for ASDiv (per the asdiv drill) and parity baseline for code algopattern, the COMPOSITIONAL subsumption holds; if not, the substrate-CRF library covers chain + flat + arc-factored-tree but NOT compositional outputs (still useful, just not universal at the user-vision level).
- **Tier hint:** Tier-2 (CPU). ETA ~3 hr (compositional training has slower structured-perceptron convergence per Collins 2002).
- **Why now:** user's compositional-engine insight is the most novel-synthesis component of the unification; empirical resolution is direct.

---

## Context pointers (paths, not summaries)

- Primary research note: `notes/research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md`
- 1x predecessor: `notes/research_drill_substrate_structured_prediction_2x_2026-06-11.md`
- Cross-thread drills (all 2026-06-11):
  - `notes/research_drill_dep_parse_0787_to_085_substrate_paths_2x_2026-06-11.md`
  - `notes/research_drill_ner_substrate_paths_2x_2026-06-11.md`
  - `notes/research_drill_asdiv_030_plateau_substrate_paths_2x_2026-06-11.md`
  - `notes/research_drill_gsm8k_substrate_boundary_2x_2026-06-11.md`
  - `notes/research_drill_layer4_dialectic_methodology_2x_2026-06-11.md`
  - `notes/research_drill_substrate_open_domain_creative_nl_2x_2026-06-11.md`
- Concrete proposed library layout: Section (d) drill-13 of the primary note (hdlab/structured/crf.py + decoders/ + feature_templates/ + schemas/ + layer1_attribution.py + registry/crf_tasks.yaml).
- Verdict cross-reference: PP-379 disc-POS 0.9499 + PP-381 hashed-depparse 0.787 (orchestrator status log 2026-06-11T16:02:48).

## Contract section

exp_dev picks: which of the 5 anchors to ship in this cycle, queue routing (likely all Tier-2 CPU), pre-reg fail bands per [[envelope-fail-bands]], smoke profile, FULL profile, multi-seed n, anchor naming. The HARD-PASS / HARD-FAIL bands in the primary note Section (c) are RESEARCH-PRE-REG; exp_dev may TIGHTEN them per envelope-fail-bands but should not loosen.

Output anchors are NOT pre-named; exp_dev names them per the naming convention. Expected naming pattern: `CRF-UNI-1`, `CRF-UNI-2`, `CRF-UNI-3`, `CRF-EXT-NER-1`, `CRF-EXT-COMPOSE-1`.

Sequencing: PILOT-1 ships FIRST (library reproduction); PILOT-2 + PILOT-3 in parallel after PILOT-1 returns; EXTENSION-1 + EXTENSION-2 after PILOT-3 closes Spearman gate.

## Autonomy declaration

exp_dev OWNS: all parameter choices (N, M, K, seeds), queue routing, anchor names, smoke vs FULL profile, ETA estimation, pre-reg threshold tightening, multi-seed stability protocols, dependencies between anchors, cycle-batching decisions. Research note specifies WHAT (the unification claim + the 5 pilot families + HP/HF bands) and WHY (lit-precedent + substrate-product implications + cap_map row consolidation). exp_dev specifies HOW (concrete cells) and WHEN (queue scheduling).
