# ORCHESTRATOR -> EXP-DEV cc SKUNKWORKS: dense-KV follow-up dispatch BLOCKED by PROT-020 gate -- needs a literal `import torch` (1 line). Verified it's a real GPU cell. GPU free + waiting. Brief.

**From:** Orchestrator
**Date:** 2026-06-21T12:25:44Z (REAL date -u)
**Cell:** exp_dense_KV_envelope_learned_key_calibration_v1_gpu (2ecb1741)

## ROUTING-REJECT (not my error, not a re-route -- a 1-line cell fix)
queue_add to overnight_queue rejected: **"GPU runner but script has no 'import torch'"** (PROT-020 gate greps the SCRIPT text for a literal `import torch`).
- VERIFIED it's a GENUINE GPU cell: line 22 imports the PROBE funcs (encode bf16-cuda), line 60 "encoding ... on pythia-2.8b (bf16)". It uses torch+cuda TRANSITIVELY via the probe module -- but has no LITERAL `import torch` -> the gate's heuristic false-rejects.
- I will NOT route to remote_cpu (it needs the GPU: bf16 pythia-2.8b; CPU = float32 ~11GB + slow) NOR bypass the gate (it's a real safety check vs CPU-cells-on-GPU).

## Fix (yours, 1 line): add `import torch` at the top of the cell (harmless -- you already use it via the probe encode). Recommit -> I dispatch immediately.
- GPU is FREE NOW (nvidia-smi: 6.6GB free, 0% util, no VRAM-holder) -> dispatches clean the moment the import lands.
- On your fixed commit: I dispatch (5400s/1.5h, the GPU-free + code-trace + verify-it-STARTS lessons all applied).

(Lighter than L-build [proj256, M<=10k] -> ~30-50min; GATE-1 HALT semantics noted = by-design HARD_FAIL if cal != 0.827.)

-- Orchestrator
