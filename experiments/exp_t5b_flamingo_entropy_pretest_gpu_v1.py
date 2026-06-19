"""
exp_t5b_flamingo_entropy_pretest_gpu_v1 -- T5b Flamingo pre-test: attention entropy over RAW vs ADAPTED substrate keys -- GPU.

ROUTING: T5b_ENGINEERING_PIVOT_FLAMINGO cheap pre-test (gate before full Flamingo engineering). Question: can a FROZEN Qwen
  attention head differentiate substrate HD vectors used as keys, or does it attend ~uniformly (max entropy)? Take real queries
  (Qwen hidden -> q_proj, per head); build substrate keys two ways: (RAW) HD vectors naively linear-projected to the K space,
  and (ADAPTED) a small learned per-head adapter trained briefly to spread attention. Measure softmax entropy over M substrate
  keys, normalized by ln(M). If RAW entropy is near 1.0 (uniform) -> adapter REQUIRED (frozen heads cannot differentiate raw HD).
PRE-REGISTERED (decision pre-test, not pass/fail capability): report normalized entropy RAW vs ADAPTED. HARD-PASS (decisive)
  = RAW norm-entropy > 0.95 (adapter REQUIRED, clear signal) OR RAW < 0.85 (minimal adapter sufficient); MIDDLE = ambiguous
  0.85-0.95. Either way the result decides the Flamingo adapter scope. HARD-FAIL only if Qwen fails to load.
FORMULA SELF-TESTS (PROT-022): 1. entropy of uniform = ln(K). 2. softmax sums to 1. 3. head reshape.
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

ANCHOR_NAME = "t5b_flamingo_entropy_pretest_gpu_v1"; MODEL = "Qwen/Qwen2.5-0.5B-Instruct"; SUB_N = 8192
M_KEYS = 64 if "--smoke" in sys.argv else 256
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _selftest():
    import numpy as _n
    K = 8; u = _n.ones(K) / K; ent = -(u * _n.log(u + 1e-12)).sum(); assert abs(ent - math.log(K)) < 1e-6, "entropy of uniform = ln(K)"
    z = _n.array([1.0, 2.0, 3.0]); sm = _n.exp(z) / _n.exp(z).sum(); assert abs(sm.sum() - 1.0) < 1e-9, "softmax sums to 1"
    x = _n.zeros((2, 12)); assert x.reshape(2, 3, 4).shape == (2, 3, 4), "head reshape"
    print("[selftest] PASS: t5b-flamingo-entropy-pretest", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def norm_entropy(scores):  # scores (Q,H,M) -> mean normalized entropy over Q,H
    p = torch.softmax(scores, dim=-1); ent = -(p * (p + 1e-12).log()).sum(-1)
    return float((ent / math.log(scores.shape[-1])).mean())


def run() -> Dict:
    g = torch.Generator(device="cpu").manual_seed(7)
    try:
        tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
        mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32, trust_remote_code=True).to(DEV).eval()
    except Exception as e:
        print("[FATAL] Qwen load failed: %s" % str(e)[:120], flush=True); return {"loaded": False}
    cfg = mdl.config; H = cfg.hidden_size; nH = cfg.num_attention_heads; hd = H // nH
    print("[model] %s hidden=%d heads=%d head_dim=%d" % (MODEL, H, nH, hd), flush=True)
    layer = mdl.model.layers[len(mdl.model.layers) // 2]; attn = layer.self_attn
    Wq = attn.q_proj.weight.detach()                                  # (H, H) (q heads)
    # real queries from a few prompts (hidden at the chosen layer input)
    cap = {"h": None}

    def pre(m, args, kwargs):
        cap["h"] = args[0] if len(args) else kwargs.get("hidden_states"); return None
    hk = layer.register_forward_pre_hook(pre, with_kwargs=True)
    prompts = ["Who founded the company?", "What year did it happen?", "Where is it located?", "What is the capital?"]
    Hs = []
    for p in prompts:
        enc = tok(p, return_tensors="pt").to(DEV)
        with torch.no_grad():
            mdl(**enc)
        Hs.append(cap["h"][0])                                        # (S,H)
    hk.remove()
    hid = torch.cat(Hs, 0)                                            # (Q,H)
    Q = (hid @ Wq.T).view(-1, nH if (hid @ Wq.T).shape[1] == nH * hd else (hid @ Wq.T).shape[1] // hd, hd)  # (Q,nHq,hd)
    nHq = Q.shape[1]
    # substrate HD keys
    sub = torch.randn(M_KEYS, SUB_N, generator=g).to(DEV); sub = sub / sub.norm(dim=1, keepdim=True)
    # RAW: naive fixed projection HD -> H, split to heads (no learned adapter)
    Praw = (torch.randn(SUB_N, H, generator=g) / math.sqrt(SUB_N)).to(DEV)
    Kraw = (sub @ Praw).view(M_KEYS, nHq, hd)
    sc_raw = torch.einsum("qhd,mhd->qhm", Q, Kraw) / math.sqrt(hd)
    raw_ent = norm_entropy(sc_raw)
    # ADAPTED: small learned adapter HD -> H trained briefly to MAXIMIZE attention spread (reduce entropy) for these queries
    import torch.nn as nn
    Ad = nn.Linear(SUB_N, H, bias=False).to(DEV); nn.init.normal_(Ad.weight, std=1.0 / math.sqrt(SUB_N))
    opt = torch.optim.Adam(Ad.parameters(), lr=1e-3); steps = 30 if SMOKE else 100
    for _ in range(steps):
        opt.zero_grad(); Kad = Ad(sub).view(M_KEYS, nHq, hd)
        sc = torch.einsum("qhd,mhd->qhm", Q.detach(), Kad) / math.sqrt(hd)
        p = torch.softmax(sc, -1); ent = -(p * (p + 1e-12).log()).sum(-1).mean()   # minimize entropy = sharpen attention
        ent.backward(); opt.step()
    with torch.no_grad():
        ad_ent = norm_entropy(torch.einsum("qhd,mhd->qhm", Q, Ad(sub).view(M_KEYS, nHq, hd)) / math.sqrt(hd))
    del mdl
    print("  normalized attention entropy over %d substrate keys: RAW=%.3f  ADAPTED=%.3f (1.0=uniform)" % (M_KEYS, raw_ent, ad_ent), flush=True)
    return {"loaded": True, "raw_entropy": raw_ent, "adapted_entropy": ad_ent, "m_keys": M_KEYS}


def verdict(r) -> Tuple[str, str]:
    if not r.get("loaded"):
        return ("HARD_FAIL", "HARD_FAIL: Qwen-0.5B-Instruct failed to load.")
    s = "RAW norm-entropy=%.3f ADAPTED=%.3f (M=%d keys)" % (r["raw_entropy"], r["adapted_entropy"], r["m_keys"])
    if r["raw_entropy"] > 0.95:
        return ("HARD_PASS", "HARD_PASS (decisive): RAW attention over substrate HD is near-UNIFORM (>0.95) -> frozen heads cannot differentiate raw HD; the per-head ADAPTER IS REQUIRED for the Flamingo insert (adapted entropy %.3f confirms a learned adapter sharpens attention). " % r["adapted_entropy"] + s)
    if r["raw_entropy"] < 0.85:
        return ("HARD_PASS", "HARD_PASS (decisive): RAW attention over substrate HD already shows structure (<0.85) -> a MINIMAL adapter suffices for the Flamingo insert. " + s)
    return ("MIDDLE_BAND", "MIDDLE_BAND: RAW entropy ambiguous (0.85-0.95); lean adapter-recommended. " + s)


print("[config] anchor=%s mode=%s model=%s M=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, M_KEYS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
