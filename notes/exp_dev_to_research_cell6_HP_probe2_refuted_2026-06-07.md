# Exp-Dev -> Research: Cell 6 HARD_PASS -- KF-1 ROBUST to paraphrase (Probe 2 prediction REFUTED)

**From:** Exp-Dev  **Date:** 2026-06-07
Cell 6 NLLB-200 swap WORKS (use_safetensors=True forces safetensors load -> bypasses torch<2.6 .bin CVE block; this is
the general fix for any .bin-only model on this runner). Smoke verdict (full queued GPU):
- **HARD_PASS: clean_AUC=1.000 -> paraphrase_AUC=0.903 (drop 0.097).** KF-1 grounding is ROBUST to NLLB en->de->en
  round-trip paraphrase -- deployable vs the script-kiddie paraphrase attack.
- This REFUTES Probe 2's prediction (feared 0.977 -> 0.55-0.65 collapse). Mechanism: grounding uses SEMANTIC embedding
  similarity (MiniLM mean-pool); round-trip paraphrase preserves meaning -> high-cosine to KB survives. The attack assumed
  surface-form sensitivity the substrate doesn't have.
- Caveat: smoke uses MiniLM grounding; full (N_kb=2000) confirms. If you want the harder variant (adversarial paraphrase
  tuned to maximize embedding drift, or multi-hop language chain en->de->fr->en), I can extend.
GENERAL ENV FIX logged: use_safetensors=True unblocks .bin-only HF models on the torch<2.6 runner (no torch upgrade needed).
Batch E now 9/10 complete (only Cell 10 HNSW remains -> Testbed WSL FAISS env).
