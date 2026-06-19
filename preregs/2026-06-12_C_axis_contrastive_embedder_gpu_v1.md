# Pre-reg: C-axis contrastive functional-similarity embedder (GPU)
Date 2026-06-12. Cell exp_C_axis_contrastive_embedder_gpu_v1.py. Lane overnight_queue (GPU, remote-only training). NO generative LLM.
Research hand-off anchor #1. bge-frozen + projection head (1024->256->128), MNR + batch-hard-triplet (margin 0.2) on
(capability, serving-atom) pairs. HELD-OUT eval: 9 benchmark C-Q capabilities EXCLUDED from training (no leakage). Eval policies:
what_serves (baseline ~0.58), contrastive-top-k, contrastive-threshold, what_serves UNION contrastive. Report NONE-gold recovery.
HARD-PASS best contrastive policy C-F1 >= what_serves + 0.05 AND loss converges. MIDDLE +0.02..0.05. HARD-FAIL <+0.02 or no convergence.
Smoke note: CUDA only available via the GPU runner (direct-ssh python lacks CUDA); self-test passed + code-reviewed; runner is the validation path.
