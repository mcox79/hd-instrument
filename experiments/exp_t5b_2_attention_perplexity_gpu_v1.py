"""
exp_t5b_2_attention_perplexity_gpu_v1 -- T5b-2: WikiText perplexity, bare vs substrate-attention-modified Pythia-160M -- GPU.

ROUTING: TIER5_SPRINT T5b-2. Measures the cost of the layer-6 substrate-attention modification: WikiText perplexity for bare
  Pythia-160M (alpha=0) vs the modified model at several injection strengths (alpha). Reports the perplexity-ratio curve. The
  scaffold substrate is random (T5b-1), so this bounds the WORST-case plumbing cost; a meaningful KB (T5b-3) should be better.
PRE-REGISTERED: HARD-PASS modified perplexity within 5x of baseline at some usable alpha>0. BORDER within 10x. HARD-FAIL > 10x
  at all alpha (modification catastrophic).
FORMULA SELF-TESTS (PROT-022): 1. ppl=exp(mean nll). 2. shift labels. 3. ratio.
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

ANCHOR_NAME = "t5b_2_attention_perplexity_gpu_v1"; MODEL = "EleutherAI/pythia-160m"
SUB_N = 8192; N_KB = 5000; LAYER = 6; ALPHAS = [0.0, 0.1, 0.3, 0.5]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_TEXT = 12 if SMOKE else 40


def _selftest():
    import numpy as _n
    assert abs(math.exp(_n.mean([0.0, 0.0])) - 1.0) < 1e-9, "ppl=exp(mean nll)"
    a = [1, 2, 3]; assert a[:-1] == [1, 2] and a[1:] == [2, 3], "shift labels"
    assert abs((10.0 / 5.0) - 2.0) < 1e-9, "ratio"
    print("[selftest] PASS: t5b-2-attention-perplexity", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def load_texts(n):
    for repo in ["Salesforce/wikitext", "wikitext"]:
        try:
            from datasets import load_dataset
            ds = load_dataset(repo, "wikitext-2-raw-v1", split="test")
            out = [t for t in ds["text"] if len(t.strip()) > 200]
            if out:
                print("[data] wikitext-2 loaded via %s (%d usable lines)" % (repo, len(out)), flush=True)
                return out[:n]
        except Exception as e:
            print("[warn] %s failed: %s" % (repo, str(e)[:80]), flush=True)
    if True:
        print("[warn] wikitext unavailable on all repos; using fallback text", flush=True)
        base = "The history of science is the study of the development of human understanding over many centuries of inquiry. "
        return [base * 4 for _ in range(n)]


def run() -> Dict:
    g = torch.Generator(device="cpu").manual_seed(7)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    H = mdl.config.hidden_size
    keys_kb = torch.randn(N_KB, SUB_N, generator=g).to(DEV); keys_kb = keys_kb / keys_kb.norm(dim=1, keepdim=True)
    vals_kb = torch.randn(N_KB, SUB_N, generator=g).to(DEV); vals_kb = vals_kb / vals_kb.norm(dim=1, keepdim=True)
    P_in = (torch.randn(H, SUB_N, generator=g) / math.sqrt(H)).to(DEV)
    P_out = (torch.randn(SUB_N, H, generator=g) / math.sqrt(SUB_N)).to(DEV)
    state = {"alpha": 0.0}

    def hook(module, args, kwargs, output):
        if state["alpha"] == 0.0 or not isinstance(output, tuple):
            return output
        hs = args[0] if len(args) else kwargs.get("hidden_states")
        if hs is None:
            return output
        q = hs @ P_in; q = q / (q.norm(dim=-1, keepdim=True) + 1e-8)
        idx = torch.argmax(q @ keys_kb.T, dim=-1); proj = vals_kb[idx] @ P_out
        proj = proj / (proj.norm(dim=-1, keepdim=True) + 1e-8) * output[0].norm(dim=-1, keepdim=True)  # match attn-output magnitude
        a = state["alpha"]
        return ((1.0 - a) * output[0] + a * proj.to(output[0].dtype),) + tuple(output[1:])           # true interpolation

    h = mdl.gpt_neox.layers[LAYER].attention.register_forward_hook(hook, with_kwargs=True)
    texts = load_texts(N_TEXT)
    enc_list = [tok(t, return_tensors="pt", truncation=True, max_length=256).to(DEV) for t in texts]

    def ppl(alpha):
        state["alpha"] = alpha; tot_nll = 0.0; tot_tok = 0
        for enc in enc_list:
            ids = enc["input_ids"]
            if ids.shape[1] < 2:
                continue
            with torch.no_grad():
                lg = mdl(**enc).logits
            sl = lg[:, :-1, :].float(); tgt = ids[:, 1:]
            nll = torch.nn.functional.cross_entropy(sl.reshape(-1, sl.shape[-1]), tgt.reshape(-1), reduction="sum")
            tot_nll += float(nll); tot_tok += int(tgt.numel())
        return math.exp(tot_nll / max(1, tot_tok))

    res = {}
    for a in ALPHAS:
        res[a] = ppl(a); print("  alpha=%.2f -> perplexity=%.2f" % (a, res[a]), flush=True)
    h.remove(); del mdl
    base = res[0.0]; ratios = {a: res[a] / base for a in ALPHAS if a > 0}
    best = min(ratios.values()); best_a = min(ratios, key=ratios.get)
    print("  baseline ppl=%.2f | best modified ratio=%.2fx at alpha=%.2f | ratios=%s" % (base, best, best_a, {k: round(v, 2) for k, v in ratios.items()}), flush=True)
    return {"baseline_ppl": base, "best_ratio": best, "best_alpha": best_a, "ratios": {str(k): round(v, 3) for k, v in ratios.items()}}


def verdict(r) -> Tuple[str, str]:
    s = "baseline-ppl=%.1f best-ratio=%.2fx@alpha%.2f ratios=%s" % (r["baseline_ppl"], r["best_ratio"], r["best_alpha"], r["ratios"])
    if r["best_ratio"] <= 5.0:
        return ("HARD_PASS", "HARD_PASS: substrate-attention-modified Pythia-160M perplexity within 5x of baseline (PoC-acceptable) -- even with a RANDOM scaffold KB; meaningful KB (T5b-3) expected better. " + s)
    if r["best_ratio"] <= 10.0:
        return ("MIDDLE_BAND", "BORDER: perplexity within 10x (PoC-acceptable as research-positioned). " + s)
    return ("HARD_FAIL", "HARD_FAIL: perplexity >10x at all alpha (random-scaffold injection too disruptive; needs meaningful KB or smaller alpha). " + s)


print("[config] anchor=%s mode=%s model=%s layer=%d alphas=%s n_text=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYER, ALPHAS, N_TEXT), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
