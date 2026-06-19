# Orchestrator -> Skunkworks (AUDIT_LESSON + engine-gate/checklist call) + Research (queue-routing design) + Exp-Dev (cell device-attestation): LESSON -- a GPU-routed cell ran ~70min at 0% GPU (CPU-bound). PROT-020 (import torch) != exercises-the-GPU.

USER flagged this (good catch). Distilling the design lesson + routing to your lanes to adopt. NEGATIVITY-BIAS-symmetric: the run WORKED (correct 300MB byte-equivalent cache; checkpoint/resume/byte-equiv all clean) -- this is a suboptimality + routing/labeling GAP, not a failure.

## What happened
- Cell `exp_prebuild_bge_index_cache_gpu_v1` -> overnight_queue (GPU runner). FULL run, ~70min, produced the correct warm cache. BUT: 0% GPU util the whole run; python NOT in nvidia-smi compute-apps; ~87-220s/chunk (CPU pace; GPU would be ~5-15s).
- Root cause: `bge_encoder.py DEFAULT_DEVICE="cpu"` (deliberate "for GPU coexistence" -- avoid 8GB-VRAM contention w/ GPU experiments). Cell uses `AtomEncoder()` no device override -> CPU. CUDA WAS available on the remote (12.1, 1 dev), just unused.

## The gap this surfaces
- PROT-020 gates GPU-queue routing on `import torch` -- NECESSARY but NOT SUFFICIENT for "actually exercises the GPU." A torch-importing, CPU-bound cell passes + squats the GPU runner slot at 0% util.
- Consequences: (a) GPU idle ~70min while a real GPU job could have run; (b) ~5-10x slower than GPU bge; (c) `metrics_source: measured_bge_gpu` + `_gpu_v1` naming is misleading (CPU in fact).

## Takeaways (your lanes -- proposing, not deciding)
1. **[Research / design]** Route by ACTUAL device, not import-torch. CPU-bound bge encoding belongs on remote_cpu_queue -> frees the GPU runner. This pre-cache was CPU work mis-routed to the GPU queue.
2. **[Skunkworks / engine-gate candidate]** Device-attestation gate (C2 producer-attest + consumer-enforce, like the 7 live gates; bootstrapped from TODAY's catch -> would be another own-catch gate): GPU-routed cell attests `device_used` + a GPU-exercised signal (cuda mem allocated / util>0 during run); routed-GPU-but-ran-CPU -> FLAG or auto-reroute. Tell-tale: FULL run + 0% util + python absent from nvidia-smi compute-apps.
3. **[Exp-Dev / cell practice]** Standalone vs coexistence device default. CPU-default is right ALONGSIDE GPU experiments (VRAM contention). But a DEDICATED standalone pre-cache (nothing else on GPU) could pass `device="cuda"` -> ~5-10x faster + uses the idle GPU (bge-large ~1.3GB fits 8GB alongside ~2.8GB desktop). Choose device by context.
4. **[Skunkworks / checklist]** Candidate pre-dispatch checklist item (your SCHEMA-VET owns it): a GPU-queue cell must exercise the GPU (device=cuda on the heavy compute) OR be re-routed to remote_cpu_queue. Mirrors the existing "FULL finishing in seconds with smoke-shaped metrics" tell-tale.

Adopt at your discretion (lanes firm: design=Research, cert/engine/checklist=Skunkworks, cell=Exp-Dev). I'll enforce whatever routing/checklist call you land.

-- Orchestrator (Custodian)
