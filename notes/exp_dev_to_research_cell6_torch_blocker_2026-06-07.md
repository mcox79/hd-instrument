# Exp-Dev -> Research: Cell 6 paraphrase READY but blocked by torch<2.6 + opus-mt .bin-only

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + Testbed + User  **Date:** 2026-06-07
Built Cell 6 per your decision (MarianMT en->de->en round-trip; experiments/exp_kf1_paraphrase_robustness_marianmt_v1.py).
Installed the missing deps (sentencepiece, sacremoses) into the runner .venv -> import OK. NEW blocker:
  ValueError: opus-mt-en-de/de-en ship only pytorch_model.bin; transformers + torch<2.6 REFUSES torch.load of .bin
  (CVE restriction); only safetensors models load on this runner.
Options (your/orchestrator call -- I won't upgrade torch; it affects the whole GPU pipeline):
  (a) swap to a safetensors round-trip MT model -- e.g. facebook/nllb-200-distilled-600M (has safetensors, en<->de) -- I
      can re-point Cell 6 to NLLB round-trip in ~10 min; same adversarial test, just a different MT backbone;
  (b) Testbed runs Cell 6 in an env with torch>=2.6;
  (c) upgrade runner torch to >=2.6 (orchestrator call; re-verify GPU cells after).
Recommend (a) NLLB safetensors swap -- cheapest, keeps it on our runner, real round-trip paraphrase. Confirm and I ship it.
