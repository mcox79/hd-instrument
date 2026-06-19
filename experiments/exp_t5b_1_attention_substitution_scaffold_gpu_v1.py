"""
exp_t5b_1_attention_substitution_scaffold_gpu_v1 -- T5b-1: Pythia-160M layer-6 attention substitution scaffold -- GPU.

ROUTING: TIER5_SPRINT T5b-1. Substrate-as-attention PoC, step 1 (the plumbing). Hook Pythia-160M layer-6 attention; per token,
  use the layer's input hidden state to QUERY a substrate KB (project 768->N), retrieve the top binding, project back (N->768),
  and blend it into the attention output. Confirm the modified model produces NON-NaN logits on simple prompts and that substrate
  retrievals are logged per token. This is the scaffold/plumbing proof; perplexity (T5b-2) and generation (T5b-3) measure quality.
PRE-REGISTERED: HARD-PASS modified Pythia-160M produces finite (non-NaN/non-Inf) logits on all probe prompts AND substrate
  retrievals logged per token (>0). HARD-FAIL NaN/Inf logits or shape mismatch / no retrievals.
FORMULA SELF-TESTS (PROT-022): 1. projection shapes. 2. argmax retrieve. 3. blend finite.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "t5b_1_attention_substitution_scaffold_gpu_v1"; MODEL = "EleutherAI/pythia-160m"
SUB_N = 8192; N_KB = 5000; LAYER = 6; ALPHA = 0.5
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _selftest():
    rng = np.random.default_rng(0)
    Pin = rng.standard_normal((8, 16)).astype(np.float32); hs = rng.standard_normal((3, 8)).astype(np.float32)
    assert (hs @ Pin).shape == (3, 16), "projection shapes"
    kb = rng.standard_normal((5, 16)).astype(np.float32); q = (hs @ Pin); idx = np.argmax(q @ kb.T, axis=1)
    assert idx.shape == (3,), "argmax retrieve"
    assert np.isfinite((hs + 0.5 * rng.standard_normal((3, 8))).sum()), "blend finite"
    print("[selftest] PASS: t5b-1-attention-substitution-scaffold", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)
RETR_LOG = {"tokens": 0, "calls": 0}


def run() -> Dict:
    g = torch.Generator(device="cpu").manual_seed(7)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    H = mdl.config.hidden_size
    # fixed random substrate KB + projections (scaffold uses real-valued substrate; quality comes in T5b-2/3)
    keys_kb = torch.randn(N_KB, SUB_N, generator=g).to(DEV); keys_kb = keys_kb / keys_kb.norm(dim=1, keepdim=True)
    vals_kb = torch.randn(N_KB, SUB_N, generator=g).to(DEV); vals_kb = vals_kb / vals_kb.norm(dim=1, keepdim=True)
    P_in = (torch.randn(H, SUB_N, generator=g) / math.sqrt(H)).to(DEV)
    P_out = (torch.randn(SUB_N, H, generator=g) / math.sqrt(SUB_N)).to(DEV)

    def hook(module, args, kwargs, output):
        hs = args[0] if len(args) else kwargs.get("hidden_states")
        if hs is None or not isinstance(output, tuple):
            return output
        q = hs @ P_in; q = q / (q.norm(dim=-1, keepdim=True) + 1e-8)            # (B,S,SUB_N) substrate query
        idx = torch.argmax(q @ keys_kb.T, dim=-1)                              # (B,S) nearest binding
        retr = vals_kb[idx]                                                    # (B,S,SUB_N)
        proj = retr @ P_out                                                    # (B,S,H) back to hidden
        proj = proj / (proj.norm(dim=-1, keepdim=True) + 1e-8) * output[0].norm(dim=-1, keepdim=True)  # match attn-output magnitude
        ao = (1.0 - ALPHA) * output[0] + ALPHA * proj.to(output[0].dtype)      # true interpolation (alpha=1 = full substitution)
        RETR_LOG["tokens"] += int(idx.numel()); RETR_LOG["calls"] += 1
        return (ao,) + tuple(output[1:])

    h = mdl.gpt_neox.layers[LAYER].attention.register_forward_hook(hook, with_kwargs=True)
    prompts = ["The capital of France is", "Water is made of hydrogen and", "The opposite of hot is",
               "In 1969 humans first walked on the", "A triangle has three"]
    if SMOKE:
        prompts = prompts[:3]
    all_finite = True; logit_stats = []
    for p in prompts:
        enc = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            out = mdl(**enc)
        lg = out.logits; fin = bool(torch.isfinite(lg).all()); all_finite = all_finite and fin
        logit_stats.append((p[:24], fin, float(lg.abs().max())))
        print("  prompt=%-26s finite=%s max|logit|=%.2f" % (p[:24], fin, float(lg.abs().max())), flush=True)
    h.remove()
    print("  substrate retrievals: %d tokens over %d hooked attention calls" % (RETR_LOG["tokens"], RETR_LOG["calls"]), flush=True)
    del mdl
    return {"all_finite": all_finite, "retr_tokens": RETR_LOG["tokens"], "calls": RETR_LOG["calls"], "n_prompts": len(prompts)}


def verdict(r) -> Tuple[str, str]:
    s = "all_finite=%s retr_tokens=%d hooked_calls=%d prompts=%d" % (r["all_finite"], r["retr_tokens"], r["calls"], r["n_prompts"])
    if r["all_finite"] and r["retr_tokens"] > 0 and r["calls"] > 0:
        return ("HARD_PASS", "HARD_PASS: layer-6 attention substitution scaffold runs -- modified Pythia-160M produces finite logits with substrate retrievals injected per token; plumbing proven for T5b-2/3 quality eval. " + s)
    return ("HARD_FAIL", "HARD_FAIL: NaN/Inf logits or no retrievals (scaffold broken). " + s)


print("[config] anchor=%s mode=%s model=%s layer=%d SUB_N=%d N_KB=%d alpha=%.2f" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYER, SUB_N, N_KB, ALPHA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
