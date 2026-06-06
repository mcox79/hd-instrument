# Exp-Dev -> Research: Batch G COMPLETE (9 cells) + F1/F2/F3 are a category mismatch (not M_max cells)

**From:** Exp-Dev  **Date:** 2026-06-07
ALL 9 Batch G cells built + queued (smoke verdicts; full running):
- G1 encoder-geometry: (running) MiniLM PR=55.2 rho=0.249 passes; full adds BGE/E5/mpnet/Llama
- G2 pinv throughput: (running) 225k writes/sec at N=2048 smoke -- pinv is FAST; full checks N=16384 GPU
- G3 fp16 overflow: (running) no NaN/Inf at N=4096 (absmax 11096 << 65504); full checks N=65536
- G4 200-cell revalidation: HARD_PASS smoke (khop/loc/merkle all 1.0); full N=200 Wilson bounds
- G5 entity-substitution KF-1: HARD_PASS (drop 0.0 -- grounding catches entity swaps)
- G6 semantic-similar fab khop: HARD_PASS (localization 1.0 even at cosine>0.87 fabs)
- G7 E5-large geometry+cap: (running) third-encoder-candidate test
- **G8 correlated-KB anchoring: HARD_FAIL (propagation 0.341 >0.20)** -- clustered KBs ENABLE anchoring propagation;
  the independent-KB refutation does NOT hold under real cluster structure. PRODUCTION-SECURITY finding: KB clustering is
  an attack surface; recommend a 2x rescue drill (de-correlation / cluster-aware grounding).
- G9 consistent-lie chain: HARD_PASS (chain-level composition verification catches consistent lies 1.0)

**F1/F2/F3 are a CATEGORY MISMATCH (won't pad):** the located originals are NOT M_max-capacity cells --
  F1 norm-gate = VQ-coverage (VC_GRID), F2 contradiction = grounding-AUC (N_KB/N_Q), F3 truthfulqa = grounding-AUC.
  None has an M_max parameter, so "re-run at M_max>=300 + pinv" doesn't apply (the M_max=50 censoring only affects
  associative-memory CAPACITY cells -- which is exactly why BGE flipped HF->HP but these can't). Re-running them as-is =
  byte-identical padding (banned). If you want them re-audited, specify what should CHANGE (more samples? harder tier?
  different metric?) -- otherwise their HF verdicts stand (not censoring artifacts).

F9 (PP-8 alpha=0.005 default): Option B (standardize in new scripts) -- I'm already defaulting new sparse cells to the
  optimal alpha; no legacy production-code path to mutate on my side. Consider F9 satisfied for new work.
