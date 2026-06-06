# Testbed -> Research: Llama-3.2-1B weights re-downloaded to runner; G15/G16 unblocked

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~01:50
**Re:** research_to_testbed_Llama1B_weights_redownload_request_2026-06-07.md
**Subject:** Quick env action. Weights now present at `~/.cache/huggingface/hub/models--meta-llama--Llama-3.2-1B/snapshots/4e20de362430cd3b72f300e6b0f18e50e7166e08/`. CELL-2 cloud run continues independently.

---

## Done

Triggered `snapshot_download` with HF_TOKEN from `.hf_token`. Pre-existing cache had config + tokenizer only (per Exp-Dev's diagnosis). Re-download fetched the 5 missing files including `model.safetensors`.

### Cache state after download

```
config.json                  symlink (small)
generation_config.json       small
LICENSE.txt                  small
model.safetensors            2471.6 MB   <-- the missing weight file
special_tokens_map.json      small
tokenizer.json               9.1 MB
tokenizer_config.json        small
original/                    directory (additional artifacts)
```

Wall: ~20s download. Cost: $0.

### Verification

The 2471.6 MB matches the expected ~2.5 GB for a 1B-parameter fp16 model. Exp-Dev can now load via:

```python
from transformers import AutoModel  # or AutoModelForCausalLM
model = AutoModel.from_pretrained("meta-llama/Llama-3.2-1B")
```

No HF_TOKEN needed at load-time since weights are now in cache. Token only matters for the initial download.

## CELL-2 cloud parallel-progress

CELL-2 (Wikipedia layer-15 extraction) is currently provisioning on Lambda GH200 us-east-3 (cluster `cell2wiki-154355`). It uses ITS OWN cloud-side HF cache (downloaded fresh on the cluster's setup 6/7) so the runner-side weights aren't load-bearing for CELL-2. Both flows are independent and proceeding in parallel.

## What's next on Testbed lane

- Monitor CELL-2 dispatch through to verdict + manual rsync if needed
- Standing for user CELL-5 dispatch authorization (Together API key already in place + tested; CELL-5 prep starts when user says go)

---

**END.**

**Research:** Llama-3.2-1B weights now present at runner HF cache. G15/G16 unblocked. CELL-2 cloud run continues.

**Exp-Dev:** Weights at `~/.cache/huggingface/hub/models--meta-llama--Llama-3.2-1B/snapshots/.../model.safetensors`. Load via `AutoModel.from_pretrained("meta-llama/Llama-3.2-1B")`. No token needed at load-time. G15 + G16 can dispatch.

**User:** Quick local-runner env action while CELL-2 runs in parallel. $0 cost; 20s wall. G15/G16 (Exp-Dev local cells) unblocked.
