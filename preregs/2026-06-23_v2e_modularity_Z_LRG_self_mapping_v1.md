# Pre-registration: v2e_modularity_Z_LRG_self_mapping_v1

**Date:** 2026-06-23
**Anchor:** v2e_modularity_Z_LRG_self_mapping_v1
**Queue:** local_cpu_queue (smoke); production target = remote_cpu_queue (FULL)
**N:** 4096, **Seeds:** [1] (smoke), [7,17,23] (full), **n_anchors:** 30 (smoke) / 150 (full)

## Scientific question

Does the substrate exhibit genuine multi-scale community structure when probed with intrinsic discriminators (modularity-Z vs degree-preserving null + Laplacian Renormalization Group stability across diffusion timescales), abandoning the structurally degenerate external lexical ground truth that v1 family maps provided?

## Background (why intrinsic discriminators)

Prior 4-attempt arc on substrate-native self-mapping all hit different walls:

| Attempt | Verdict | Diagnosis |
|---|---|---|
| v2 | MIDDLE_BAND | encoder + 2-hop signal exists at small scope |
| v2b | MIDDLE_BAND (96 rel) | mechanism works at restricted scope |
| v2c | HARD_FAIL (cluster_gap=-3) | discriminator misspecified at 200k-rel scope |
| v2d | HARD_FAIL (smoke ARI=0) | v1 lexical families are degenerate (~2/20 anchors match) |

The 5x-deeper drill in `notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md` concluded: **abandon external ground truth + abandon single-resolution clustering**. Modularity-Z vs degree-preserving null is by-construction immune to the by-construction-saturation META atom (random graphs cannot beat their own degree-preserved null in expectation). LRG-tau-sweep reads multi-scale structure without needing labels.

## Pre-registered bands

**HARD-PASS:**
- `mod_Z(REAL) >= 3.0` at any gamma in the sweep
- `LRG_stability >= 0.5` across at least 2 tau-pair values (mean pair-ARI >= 0.5 for >= 2 adjacent tau pairs)
- `mod_Z(REAL) / mod_Z(SHUF) >= 2.0` (intrinsic over degree-preserved null)
- `atom_retrieval_recall >= 0.95`
- `n_llm_calls == 0` (substrate-only-decode)

**MIDDLE:** `mod_Z(REAL) in [1.5, 3.0)` at best gamma; partial signal characterization.

**HARD-FAIL:** `mod_Z(REAL) < 1.5` at EVERY gamma in the sweep, OR `mod_Z(REAL) / mod_Z(SHUF) < 1.1`. This forces **encoder substitution** (not another discriminator attempt) per the 5x drill: char_trigram + 2-hop-Jaccard pipeline is structurally insufficient regardless of discriminator choice.

## Calibration rationale

Director task spec defines simpler bands than the full v2e drill (which sweeps 5 gammas with consensus-entropy tertiary). These thresholds are deflated from the typical "Z >= 2 sigma" community-detection rule of thumb to Z >= 3 (HARD_PASS) to give 3-sigma cleaner separation, and ratio >= 2.0 ensures the degree-preserved null is a genuine baseline (not just slightly above). LRG threshold 0.5 across 2 tau pairs is a standard scale-stability heuristic (Villegas 2023). Recall floor 0.95 carries forward from v2c (codebook identity is non-negotiable). Smoke uses 1 seed; full uses 3 with cv check absorbed into ratio.

## Sanity self-test (endpoint)

`--self-test` builds a planted 2-block adjacency (50 atoms, p_intra=0.7 / p_inter=0.05); requires `mod_Z(REAL) >= 2.0` AND `mod_Z(REAL) > mod_Z(SHUF)` AND zero LLM calls. Also exercises LRG + allocation primitives on the planted graph; sys.exit(0) on pass.

## Mechanism upgrades vs v2c/v2d

1. **Modularity-Z gamma sweep** (gamma in {0.5, 1.0, 2.0, 4.0}) — by-construction-immune to by-construction-saturation; best gamma chosen by argmax Z.
2. **Degree-preserving rewire null** (50 rewires in smoke / 100 in full) via networkx double_edge_swap — preserves per-atom degree; null Q distribution is structurally well-defined.
3. **Laplacian Renormalization Group sweep** (tau in {0.1, 1.0, 10.0}) — heat-kernel exp(-tau * L_norm) smooths the adjacency at multiple diffusion timescales; ARI between adjacent-tau partitions measures scale stability.
4. **Sparse-ensemble allocation diagnostic** (Tonegawa engram-cell analog; 20 iterations softmax reallocation with cluster-size decay) — composes existing iterative_attractor primitive with the Louvain partition; included as observable, not gate.

## Smoke vs full delta

| Param | Smoke | Full |
|---|---|---|
| seeds | 1 | 3 |
| n_anchors | 30 | 150 |
| max_ingest_triples | 5000 | None |
| n_null_rewires | 50 | 100 |
| jaccard_tau | 0.05 | 0.10 |
| expected wall | ~15-20 min local_cpu | ~3h remote_cpu |

## N-suffix section
Anchor anchored at N=4096 across smoke and full (per Director spec; the encoder is not the bottleneck).

## Timeout estimate
Smoke ~ 1200s wall at N=4096 / 30 anchors / 50 null rewires / 1 seed on local_cpu_queue.
formula: 1.5 * 1200 = 1800s (smoke margin)
timeout_s = 1800
