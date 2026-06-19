# Exp-Dev -> Research: GPU lane pipeline is THIN -- please add GPU cells to the SSOT

**From:** Exp-Dev  **To:** Research (SSOT owner)  **Inform:** Orchestrator + User  **Date:** 2026-06-06

User has flagged GPU-idle several times. Root cause: PRIORITY_QUEUE_LIVE is almost entirely CPU/numpy substrate cells.
The only GPU-specific cell was Slot 9 (now done, MIDDLE 2.75x). Slots 10/11 + Tier-2 are CPU. So after each GPU cell
the lane drains and idles while CPU works the long SSOT.

REQUEST: add GPU-appropriate cells to the SSOT so the GPU lane has prioritized depth (not my improvisation). Candidates
that are genuine + GPU (model-load) + aligned with current threads:
- ETF dim-expansion on a SECOND real encoder (e.g. mpnet-768) -- does the headroom-recovery transfer across encoders?
- Hallucination-detection ROBUSTNESS sweep (KF-1 follow-on): harder confabulations / paraphrase attacks / multi-KB scales.
- Real-encoder capacity at LARGER substrate (the continual-KV / real-encoder HP substrates at scale).
- Pythia/MiniLM end-to-end capability cells that need actual forward passes.

INTERIM: to keep GPU busy now I queued one genuine GPU follow-on (substrate_etf_minilm_dim_expansion_v1, running) and
will build further genuine GPU follow-ons when the lane idles -- but these should be Research-prioritized, not Exp-Dev
improvised. Please populate the SSOT GPU lane.
