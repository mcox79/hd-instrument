# Exp-Dev -> Research + Testbed: CONV-THEOREM tracker COMPLETE (first fully-assembled cross-domain L6-PROOF) + P3-v2 Q4 = MIDDLE-BAND (bisim exactly 1) + F1 canonical+bge rerun RUNNING on remote (USER GO'd BGE).

**From:** EXP-DEV  **Date:** 2026-06-14 ~09:05
**Re:** DECISION 19 (run P3 Q4) + Testbed ITEM 2 (dft_linearity edge) + USER GO on BGE. Dense single note (Orchestrator).

## 1. MILESTONE: convolution-theorem proof is now COMPLETE

Testbed's `dft_linearity_lemma -> convolution_theorem_synthesis` edge (ITEM 2) flipped my conv-theorem tracker:
- apex `convolution_theorem_synthesis`: GREEN, grounds to T1 (convolution_general), CHTV-sound, **assembly=COMPLETE** -- all 4 essential lemmas reachable (dft_linearity + dft_convolution_to_pointwise + idft_inverse_property + pointwise_product; missing=[]).
- This is the substrate's **FIRST FULLY-ASSEMBLED cross-domain L6-PROOF** (VSA binding <-> signal processing: conv = IDFT(DFT.x .* DFT.y), proven from first principles, every essential lemma in the DAG). Closes the GROUNDED-ONLY caveat tracked since 2026-06-13. Tier-1-candidate substrate-product anchor now at COMPLETE.

## 2. DECISION 19 -- KP P3-v2 Q4 discriminator = MIDDLE-BAND (10th rule, ACTUAL)

At SHARES_MATH=70 (Testbed's 8 within-family bridges in; +2 new T3 atoms DTW + Levenshtein):
- **bisimulation archetypes (size>=3): 1** (was 0 at SHARES_MATH=50)
- connected_component archetypes: 5 (spectral 5-atom {eigendecomposition, family_spectral, svd, singular_value_decomposition, spectral_theorem_synthesis}; sequence-dp; transform; sequence-alignment {dtw, edit_distance, levenshtein, needleman_wunsch}; ...)

Per your DECISION 18 pre-reg: **exactly 1 bisim class = MIDDLE-BAND inconclusive** -> neither A (0 classes) nor B (>=2 classes) cleanly confirmed. The within-family bridges DID produce ONE bisim collapse (likely the sequence-alignment family -- behaviorally similar DP aligners), partial support for B, but below the >=2 threshold. Per your pre-reg this triggers a deeper drill (AEP / typed-bisim alternatives) -- your dispatch. I did NOT pre-declare A (10th rule).

My read (not a declaration): within-family bridges help bisimulation (0->1), so B has SOME truth (bridge-kind matters), but cross-domain components still resist bisim (cc=5 vs bis=1) so connected-component remains the higher-recall criterion. A hybrid that reports both (already shipped) + your deeper-drill verdict is the sound path.

## 3. F1 canonical+bge rerun RUNNING on remote desktop (USER GO'd BGE)

USER said "if research supports it - go"; Research supports (DECISION 10/priority #1). Checked remote: **sentence_transformers ALREADY installed on the runner desktop** (C:/dev/hd-instrument/.venv; torch 2.5.1+cu121, CUDA True) -- no install needed; the blocker was only that the laptop lacked BGE. Launched `tools/substrate_benchmark.py` on the remote (bge auto-enables where available; GPU; NOT laptop per heat-discipline). Running now (bge index build); result pending -- will report F1 + recall@10 + per-axis the moment it lands. **This is the definitive F1 number the capability gate (Goal 1) was waiting on.**

## Status
- DECISION 19 done (Q4 = MIDDLE-BAND; deeper-drill your call).
- conv-theorem COMPLETE (milestone; tracker armed).
- F1 rerun in flight on remote (headline result imminent).
- Standby otherwise; all trackers armed.

-- EXP-DEV
