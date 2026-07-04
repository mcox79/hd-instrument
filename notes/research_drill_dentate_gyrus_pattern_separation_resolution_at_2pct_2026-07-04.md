# Research drill: dentate-gyrus pattern separation -- why 2% sparse is NOT resolution-limited

Date: 2026-07-04
Drill: BRAIN 5x-DRILL angle 1/5 (hippocampal DG angle)
Problem: distilled K-block bipolar sparse code hits ret_agree10 = 0.21(K128,3.1%) / 0.29(K256) / 0.41(K512,12.5%). Target >= 0.35 at ~2%. K128 code CEILING (teacher-through-argmax) = 0.43; trained reaches 0.20 = 47% of ceiling. Block-argmax discards magnitude.

---

## SHARP ANSWER (the DG resolution law)

The dentate gyrus does NOT get discrimination resolution from its 2% sparsity fraction. It gets **separation** from the low fraction and **resolution from the ABSOLUTE active count**, which it keeps high by **massive expansion** (EC ~200k -> DG ~1M+ granule cells, a 5-10x fan-out). At 2% of ~1M granule cells, ~20,000 units are active -- a huge absolute code even though the fraction is tiny. Resolution scales with active-count and ambient dimension; separation scales with fraction. **2% is inherently resolution-limited ONLY when the ambient dimension is small.** hd-instrument is small-dim-trapped: total_dim = 4096 forces K (active count = resolution) and the fraction to trade off against each other. That is exactly why the config that already clears the target (K512 -> 0.41 > 0.35) can only reach it by paying 12.5% sparsity -- there is no room at 4096 to put 512 active units at a 2% fraction.

This is not a soft analogy. It is the **expand-and-sparsify / FlyHash** law: the fruit-fly mushroom body expands 50 projection neurons -> 2000 Kenyon cells (40x) then WTA-sparsifies to ~5%, and the resulting sparse tags preserve NEAREST-NEIGHBOR structure BETTER than dense LSH -- "most prominently for short hash lengths" (Dasgupta, Stevens & Navlakha, Science 2017). Sparse-NN retrieval on an expanded code is a solved, winning regime. hd-instrument is doing the sparsify without the expand.

Two DG mechanisms we are additionally throwing away, both empirically shown to matter:

1. **Rigid per-block argmax is the wrong sparsifier.** The expand-and-sparsify literature (Dasgupta, "Expressivity of expand-and-sparsify representations", 2020) finds that for manifold-structured data, **per-unit adaptive thresholds beat a winner-take-all mechanism**. Biology agrees: DG sparseness is set by feedback/feedforward inhibition tuning **adaptive spike thresholds per cell** (mossy-cell sparse coding via adaptive-threshold dynamics, bioRxiv 2022), not a hard "exactly one winner per fixed partition." Block-argmax forces exactly-one-per-block regardless of whether that block's evidence is strong or noise -- it spends code capacity on blocks with no signal and caps blocks with lots of signal at one bit.

2. **The winner's magnitude/rank is discarded.** WTA-hashing works because **rank order preserves the shape of the input vector**; the retrieval-quality gain of the whole WTA family comes from keeping ordinal/rank information. hd-instrument records only winner-index + sign per block and drops the graded activation -- so cross-block "which winners were confident" (the rank shape) is gone. This is precisely why the *code ceiling itself* is only 0.43: magnitude is destroyed before retrieval even starts.

---

## MECHANISM MAP (biology -> concrete implementation)

| DG mechanism | What it buys | hd-instrument today | Concrete port |
|---|---|---|---|
| Expansion (5-10x granule cells) | high absolute active-count at low fraction | total_dim=4096 fixed; K and fraction coupled | expand total_dim; decouple from block count |
| Adaptive per-cell threshold + inhibition | sparsity adapts to input evidence | rigid per-block argmax | global/adaptive top-k over expanded dim, or per-block soft-threshold |
| Graded firing rate of winners | rank/shape preserved for downstream discrim | pure +-1, magnitude dropped | dual readout: ternary/graded code for retrieval, +-1 for algebra |
| CA3 handoff (separate completer) | retrieval done by dense attractor, not the sparse code | cosine-NN directly on sparse code | (bigger change; note only) |

---

## CONCRETE UNTRIED LEVERS

### LEVER 1 (primary, highest-confidence): decouple total_dim from block count -- EXPAND
The config that ALREADY clears the target is K512 -> 0.41. It only fails the sparsity spec because 512/4096 = 12.5%. **Expand total_dim to 16384-32768 so K512 sits at 1.5-3.1% sparse.** Each block gets larger (more log2(blocksize) bits/winner -> ceiling rises above the current 0.43), active-count stays at the resolution-adequate 512, and the fraction drops into spec. This is the DG/FlyHash expansion applied to the RETRIEVAL head. Cost: memory ~4-8x on the code; algebra (bind/unbind) is unaffected or improved by higher dim.
- Falsifier: run K512 at total_dim in {8192, 16384, 32768}; PASS-band ret_agree10 >= 0.35 at sparsity <= 0.03 with algebra fidelity still >= 0.99 and hi80_cos >= 0.80. FAIL-band: ret_agree10 < 0.30 at 2% (means resolution does NOT survive re-parameterization -> expansion is not the missing piece).

### LEVER 2 (attacks both the 0.43 ceiling AND the 47% training gap): drop rigid block-argmax
Replace exactly-one-per-block with **(a) global adaptive top-k over the expanded dim** (k = target active-count; threshold set by k-th value, DG-inhibition analog) so active units go where the evidence is, not one-per-partition; and **(b) retain the winner's graded magnitude as a ternary/rank-weighted RETRIEVAL readout while keeping the +-1 projection for algebra** (dual readout -- algebra never touches the graded channel). Rank-order retention is the documented source of WTA-hash retrieval quality; recovering it should lift the code ceiling above 0.43 and give training a smoother target (the 47%-of-ceiling gap is partly an argmax-hardness/gradient artifact -- a soft/graded top-k is far more trainable than a hard per-block argmax).
- Falsifier: at fixed sparsity 2%, compare {block-argmax} vs {global adaptive top-k} vs {top-k + graded-magnitude retrieval readout}. PASS: graded readout raises code ceiling >= 0.50 AND trained ret_agree10 >= 0.35. Diagnostic: if the code CEILING rises but trained stays ~47% of it, the gap is optimization not representation (route to a training-objective drill).

---

## PRIOR-WORK CHECK (substrate KB)
Concept-query hit: `notes/exp_dev_handoff_research_biological_precedents_animal_scales_2026-06-04.md` anchor **"3. DG-EXPANSION-SEPARATION"** ALREADY proposed a fixed random expansion E: R^N -> R^(kN), k=4-8, top-2% sparsify. BUT it was aimed at **store-side interference reduction** (orthogonalize similar patterns before binding), NOT at the retrieval-distillation head. The lever exists in our own KB and was never pointed at this gap. Also: `research_drill_multi_channel_substrate_lm_training_2026-06-03.md::chunk029` (DG separation vs CA3 completion, ACh switch) and `research_drill_continual_full_cls_5x_2026-06-10.md` (B2 sparse coding). None applied expansion to ret_agree10. This drill re-targets the existing anchor + adds the adaptive-threshold and graded-readout levers (both new to our KB).

---

## HONEST P
P_deflated (this angle cracks retrieval-at-2% to >= 0.35): **0.42**
Reasoning: unusually high for a lit-scan drill because our OWN data already brackets the target -- K512 achieves 0.41 > 0.35; the whole problem reduces to "run the winning active-count at a lower fraction," which expansion mechanically enables (not speculative). Raw estimate ~0.60. Deflated ~0.18 for two honest downside risks: (i) the trained-vs-ceiling 47% gap is an ORTHOGONAL optimization problem that expansion alone may not fix (Lever 2 targets it but is less certain); (ii) untested whether the 0.41 quality survives re-parameterization to expanded-dim-at-fixed-K. Capped at the 0.50 novel-synthesis ceiling. Symmetric note: I am NOT deflating below 0.42 despite the lit-scan penalty because suppressing our own bracketing data would be dishonest downward bias.

## SOURCES
- Dasgupta, Stevens, Navlakha, "A neural algorithm for a fundamental computing problem," Science 2017 (FlyHash; expand+WTA beats dense LSH at short hash lengths).
- Dasgupta et al., "Expressivity of expand-and-sparsify representations," arXiv 2006.03741 (per-unit adaptive threshold > WTA for manifold data).
- bioRxiv 2022.03.07.483263 (DG mossy-cell sparse coding via adaptive spike-threshold dynamics).
- "A combinatorial model for dentate gyrus sparse coding," PubMed 27764589 (highly-redundant sparse decorrelated output; expansion parameters).
- Ahmad & Scheinkman, "How Can We Be So Dense? The Benefits of Highly Sparse Representations," arXiv 1903.11257.
- WTA-hashing rank-order preservation: arXiv 1908.09799; Rank Subspace / ordinal hashing arXiv 1503.05951.
