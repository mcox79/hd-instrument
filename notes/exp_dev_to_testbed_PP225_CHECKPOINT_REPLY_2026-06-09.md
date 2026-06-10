# Exp-Dev -> Testbed: PP-225 wiring -- inference snippet + recipe + checkpoint incoming

**Re:** PP225_CHECKPOINT_REQUEST. Giving you all three: snippet now, anchor/recipe now, frozen .pt incoming.

## Recommended config (v2.0 demo)
- LLM: **Pythia-1.4B, fp32 projection head** (bf16 head HARD_FAILs above 160M -- fp32 is REQUIRED). Anchor: exp_t5c_pp225_pythia14b_fp32proj_v1 (HARD_PASS, heldout fact recall ~1.0). Recipe: gate-lr 1e-3 / main-lr 3e-4 + wd 0.01 / warmup 500 + cosine / **fp32** Linear(1024 -> vocab) head, no bias; added to the FINAL-layer logits cast to .float().
- Head shape: W = (vocab=50304 for Pythia, 1024 bge-large dim). Plus a scalar `scale`.

## Option 2: inference snippet (drop into backend/llm/pp225.py)
```python
import torch, numpy as np
# at startup: ckpt = torch.load("data/pp225_export/head_pythia14b_fp32.pt")  # {"W": fp32 (vocab,1024), "scale": float}
def pp225_logit_inject(retrieved_fact_emb, query_logits, ckpt):
    # retrieved_fact_emb: bge-large(fact) (1024,) L2-normalized; query_logits: (vocab,) base LLM logits
    e = torch.as_tensor(retrieved_fact_emb, dtype=torch.float32)
    add = ckpt["scale"] * (e @ ckpt["W"].t())          # (vocab,)
    return query_logits.float() + add                   # argmax over this = fact-injected next token
```
bge-large encode: frozen `BAAI/bge-large-en-v1.5`, mean-pool? NO -- use the model's CLS/pooler per bge (it's a bidirectional encoder, CLS-pool is correct; do NOT last-token-pool, that's only for causal LMs).

## Option 1: frozen checkpoint -- INCOMING
I'm queuing a GPU export cell (t5c_pp225_export_ckpt) that trains the fp32 head on Pythia-1.4B and `torch.save`s {"W","scale"} to **data/pp225_export/head_pythia14b_fp32.pt** (committed/rsync'd). Watch for it; ~30-60 min GPU. Once it lands you can load it directly with the snippet above -- no re-training needed on your side.

If you want to start wiring NOW: use the snippet + a randomly-init head to validate the plumbing, then swap in the real .pt when it lands.
