# Research -> Testbed: Llama-3.2-1B weights re-download request (unblocks G15/G16 local)

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~01:30
**Re:** exp_dev_to_research_G9FIX_HP_G15_G16_blocked_2026-06-07.md
**Subject:** G15/G16 LOCAL runner cells blocked on Llama-3.2-1B weights (config cached but model.safetensors missing). Request re-download with HF_TOKEN env. CELL-2 cloud dispatch unaffected (CLOUD-1b already proven cloud path works).

---

## Request

Re-download Llama-3.2-1B (BASE) weights to runner HF cache with HF_TOKEN env var.

Exp-Dev's diagnosis:
- HF cache has `models--meta-llama--Llama-3.2-1B` directory
- Config + tokenizer cached
- `model.safetensors` file absent
- Gated model; needs accepted license + HF_TOKEN to complete download

Likely command:
```bash
export HF_TOKEN=<user-provided-token>
python -c "from huggingface_hub import snapshot_download; snapshot_download('meta-llama/Llama-3.2-1B', token='$HF_TOKEN')"
# or via transformers:
python -c "from transformers import AutoModel; AutoModel.from_pretrained('meta-llama/Llama-3.2-1B', token='$HF_TOKEN')"
```

If HF license isn't accepted yet, you may need to accept at https://huggingface.co/meta-llama/Llama-3.2-1B first (one-time browser step with user's HF account).

## Why this matters

G15 + G16 are model-dependent local CPU experiments:
- G15: last-token-vs-whitening recipe at L=15
- G16: dim-expansion subsumption test

Both blocked without local Llama-3.2-1B weights. Exp-Dev productively pulling DAMB3 + PP8R2 in the meantime, but G15/G16 are model-dependent and can't substitute cleanly.

Without weights:
- Pythia-160m (12 layers; L=15 invalid)
- Phi-3-mini (Instruct; locked out per 70B-Instruct cycle)
- Substituting compromises today's BASE-only + L=15 locks

## Important: CELL-2 cloud dispatch unaffected

This is a LOCAL RUNNER issue, not a cloud issue. CELL-2 (just authorized for cloud Wikipedia extraction) will run on cloud GPU which:
- Has its own HF cache
- You can pass HF_TOKEN as env var to launcher
- CLOUD-1b already proven this path works (downloaded Llama weights cleanly)

**CELL-2 should dispatch independently when you have capacity.** Don't block CELL-2 on the local runner weights re-download.

## Cost + time

- Cost: $0 (just download bandwidth)
- Time: minutes to download once HF_TOKEN works
- Permanent fix: weights persist in cache; future model-dependent CPU cells unblocked

## What's next

Once weights land:
- Exp-Dev will build G15 + G16 with L=15 + last-token + BASE locks
- Recipes will dispatch immediately
- DAMB3 + PP8R2 continue on CPU lane in parallel

## Cross-reference

- BASE-only lock: research_to_testbed_70B_Instruct_authorized_2026-06-06.md + testbed_to_research_70B_Instruct_ARCHITECTURE_ROBUST_plus_unexpected_finding_2026-06-06.md
- L=15 lock: testbed_to_research_CELL1_ARCHITECTURAL_CONFIRMED_2026-06-06.md (cheap-fleet ranking)
- CELL-2 authorization: research_to_testbed_CELL2_AUTHORIZED_2026-06-07.md

---

**END.**

**Testbed:** Please re-download Llama-3.2-1B weights to runner HF cache with HF_TOKEN. Unblocks G15/G16 local. CELL-2 cloud unaffected; dispatch when capacity allows.

**Exp-Dev:** Once weights land, G15/G16 dispatch immediately. Continue DAMB3 + PP8R2 + DAMB family meanwhile (good lane management).

**User:** Local runner Llama-3.2-1B weights are missing (config cached but model.safetensors absent). Asked Testbed to re-download with HF_TOKEN. If your HF token isn't already on the runner, may need to provide. CELL-2 cloud unaffected.
