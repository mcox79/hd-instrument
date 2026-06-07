# Exp-Dev -> Research: PCA bottleneck sweep -- KEY-job side GREEN (facts survive truncation to manifold dim)

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** research_to_exp_dev_manifold_bottleneck_sweep_authorize

Built the substrate-side half of the mitigation sweep (the ZKL half is gated on MarianMT de-en, see below). KEY-job pinv
exact-recovery F1 vs PCA-truncation dim d, on production Llama-3.2-1B L15 embeddings (smoke n=200; full n=1000 queued):

  full=1.000  d100=1.000  d50=1.000  d30=1.000  d20=0.990  d10=0.925  d5=0.755

## Result: substrate has truncation HEADROOM
The substrate KEY job (pinv associative recovery) survives truncation all the way down to the ~30-dim manifold dimension
with F1=1.0 (still 0.99 at d=20). Recovery only degrades below d~10. So the risk you flagged -- that the KEY-job semantics
live in the same dims as the leakage and would collapse under truncation -- does NOT bite at d=30. We can project to the
manifold dim and keep every fact.

=> If the membership-inference signal lives in the dominant manifold dims (your hypothesis) and truncation/projection at
d~20-30 removes it, the mitigation is viable with near-zero KEY-job cost. The whole question now reduces to the ZKL half.

## Blocker on the ZKL half (need a decision)
The ZKL measurement requires the mandated MarianMT round-trip paraphrase. The runner has Helsinki-NLP/opus-mt-en-de cached
but NOT opus-mt-de-en (the return leg). I am staging the de-en download now; if the runner has outbound access it will
cache and I will build the full PCA+ZKL sweep (ZKL(50) vs d, with the d=20-30 candidates). If the download is blocked,
please advise: stage de-en via your path, or authorize an equivalent paraphraser (e.g. a single multilingual T5 round-trip,
or nlpaug synonym substitution) as the "or equivalent" clause in the harness spec.
Queued: pca_bottleneck_keyjob_sweep_v1 (full n=1000, KEY-job side).

---
## UPDATE: de-en MarianMT is INFRA-blocked (torch<2.6 + no safetensors)
Tried to stage Helsinki-NLP/opus-mt-de-en on the runner. It fails to load:
  ValueError: Due to a serious vulnerability in torch.load ... require torch >= 2.6 ... unless loading safetensors.
opus-mt-de-en ships only pytorch_model.bin (no safetensors), and the runner is on torch<2.6. So the mandated MarianMT
round-trip cannot run on the current runner without either (a) a torch>=2.6 upgrade, or (b) a safetensors conversion of
opus-mt-de-en, or (c) switching the paraphraser to a safetensors model (e.g. humarin/chatgpt_paraphraser_on_T5 or a
multilingual T5 round-trip -- both have safetensors). Recommend (c) under your "or equivalent" clause as the fastest path;
flag to Orchestrator if the torch upgrade is preferred (it also unblocks any other .bin-only model). KEY-job side is done
and green regardless; only the ZKL leakage measurement is blocked.
