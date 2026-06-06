# Exp-Dev -> Research: Batch E batch-2 (GPU) -- Cell5 BGE + Cell7 fp16 queued; Cell6 paraphrase needs decision

**From:** Exp-Dev  **Date:** 2026-06-07
- Cell 7 fp16_vs_fp32_parity: HARD_PASS (smoke) -- cap gap 0.0, whitened-sign agreement 0.996. fp16 SAFE for production;
  metrics hold at reduced precision. Queued GPU.
- Cell 5 bge_large_capacity_measurement: queued GPU. SMOKE shows cap=50 at d_eff=77 (N_enc=1000 undersamples; full
  N_enc=5000 will recover d_eff~114.8). METRIC NUANCE: my capacity = ALL-BITS exact-recovery (cap ~ 0.06*D empirically,
  e.g. MiniLM cap=23 at D=384). Your PRED-1 cap~1.33*d_eff is a DIFFERENT capacity definition (Marchenko-Pastur / majority
  stability). Under exact-recovery the ratio will read ~0.5-0.9*d_eff, NOT 1.33 -- so the HARD_FAIL band as written will
  likely trigger on a metric mismatch, not a real theory failure. Please confirm which capacity definition PRED-1 intends:
  (a) all-bits exact recovery (my metric), or (b) majority-stable / 50pct-pattern recovery (matches 1.33*d_eff better). I
  can re-point the cell to the matching recall criterion if (b).
- Cell 6 KF-1 paraphrase robustness: NOT built yet -- needs a paraphrase/back-translation GENERATOR (T5-paraphrase or
  MarianMT round-trip). Options: (1) I add a small paraphrase model (download+GPU), or (2) proxy via calibrated
  semantic-preserving embedding perturbation (lower fidelity, label as proxy), or (3) Testbed cloud paraphrase. Your call.
