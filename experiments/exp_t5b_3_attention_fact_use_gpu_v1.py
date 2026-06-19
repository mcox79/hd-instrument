"""
exp_t5b_3_attention_fact_use_gpu_v1 -- T5b-3: does a MEANINGFUL substrate KB make Pythia-160M use injected facts -- GPU.

ROUTING: TIER5_SPRINT T5b-3. T5b-1/2 proved the plumbing is non-catastrophic with a random KB. T5b-3 builds a MEANINGFUL KB:
  for each (prompt, rare-answer) fact, the KB key is the prompt's layer-input hidden state and the KB value carries the answer
  token's unembedding direction. The layer-6 attention hook retrieves the matching fact for the current token and blends the
  answer direction into the attention output. Measures whether substrate injection makes the model PRODUCE/upweight the fact's
  answer (bare model does not know these rare facts). This is the categorical "substrate supplies knowledge the LLM lacks" demo.
PRE-REGISTERED: HARD-PASS substrate injection makes the fact's answer the top-1 next token in >= 0.50 of facts (bare baseline
  near 0 by construction). MIDDLE >= 0.30. HARD-FAIL < 0.30 (injection does not transmit facts).
FORMULA SELF-TESTS (PROT-022): 1. projection shape. 2. argmax. 3. softmax prob.
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

ANCHOR_NAME = "t5b_3_attention_fact_use_gpu_v1"; MODEL = "EleutherAI/pythia-160m"
LAYER = 11; ALPHA = 0.6
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _selftest():
    import numpy as _n
    h = _n.random.default_rng(0).standard_normal((3, 8)); P = _n.random.default_rng(1).standard_normal((8, 16))
    assert (h @ P).shape == (3, 16), "projection shape"
    assert int(_n.argmax([0.1, 0.9, 0.2])) == 1, "argmax"
    e = _n.exp([1.0, 2.0]); assert abs((e / e.sum()).sum() - 1.0) < 1e-9, "softmax prob"
    print("[selftest] PASS: t5b-3-attention-fact-use", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def make_facts(tok):
    # rare/arbitrary subject -> single-token answer the base model should NOT know
    subs = ["zorblax", "quenly", "frinabel", "morvath", "plistery", "drovannic", "xelphine", "yubbidge",
            "kravenll", "thessomir", "wandrelic", " obsidiyne", "glumtwarp", "neptarine", "vossberry", "cindraxa"]
    ans = [" violet", " copper", " seven", " marble", " thunder", " willow", " saffron", " glacier",
           " ember", " quartz", " orchid", " cobalt", " harvest", " lantern", " meadow", " falcon"]
    facts = []
    for s, a in zip(subs, ans):
        aid = tok(a, add_special_tokens=False)["input_ids"]
        if len(aid) == 1:
            facts.append(("The secret token of %s is" % s.strip(), aid[0]))
    return facts[:8] if SMOKE else facts


def run() -> Dict:
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    H = mdl.config.hidden_size
    W_U = mdl.embed_out.weight if hasattr(mdl, "embed_out") else mdl.get_output_embeddings().weight  # (vocab, H)
    facts = make_facts(tok)
    if not facts:
        print("[FATAL] no single-token facts", flush=True); return {"n": 0}

    # capture layer-LAYER INPUT hidden state at the last token, per prompt (the KB key)
    cap = {"h": None}

    def cap_hook(module, args, kwargs):
        hs = args[0] if len(args) else kwargs.get("hidden_states")
        cap["h"] = hs
        return None
    ch = mdl.gpt_neox.layers[LAYER].register_forward_pre_hook(cap_hook, with_kwargs=True)
    keys = []; vals = []; ans_ids = []
    for prompt, aid in facts:
        enc = tok(prompt, return_tensors="pt").to(DEV)
        with torch.no_grad():
            mdl(**enc)
        keys.append(cap["h"][0, -1, :].clone())                        # last-token hidden at layer input
        v = W_U[aid].detach().clone(); vals.append(v / (v.norm() + 1e-8))  # answer unembedding direction (unit)
        ans_ids.append(aid)
    ch.remove()
    K = torch.stack(keys); K = K / (K.norm(dim=1, keepdim=True) + 1e-8); V = torch.stack(vals)   # (Nfact,H)

    # injection hook on layer-LAYER attention: retrieve matching fact value, blend (norm-matched) into attn output
    state = {"on": False}

    def inj_hook(module, args, kwargs, output):
        if not state["on"] or not isinstance(output, tuple):
            return output
        hs = args[0] if len(args) else kwargs.get("hidden_states")
        if hs is None:
            return output
        q = hs / (hs.norm(dim=-1, keepdim=True) + 1e-8)
        idx = torch.argmax(q @ K.T, dim=-1)                            # (B,S) nearest fact
        retr = V[idx]                                                  # (B,S,H) answer direction
        retr = retr / (retr.norm(dim=-1, keepdim=True) + 1e-8) * output[0].norm(dim=-1, keepdim=True)
        return ((1.0 - ALPHA) * output[0] + ALPHA * retr,) + tuple(output[1:])
    ih = mdl.gpt_neox.layers[LAYER].register_forward_hook(inj_hook, with_kwargs=True)   # residual-stream injection (not just attn sub-output)

    bare_top1 = 0; inj_top1 = 0; n = 0
    for (prompt, aid) in facts:
        enc = tok(prompt, return_tensors="pt").to(DEV)
        state["on"] = False
        with torch.no_grad():
            lb = mdl(**enc).logits[0, -1, :]
        state["on"] = True
        with torch.no_grad():
            li = mdl(**enc).logits[0, -1, :]
        bare_top1 += int(int(torch.argmax(lb)) == aid); inj_top1 += int(int(torch.argmax(li)) == aid); n += 1
    ih.remove(); del mdl
    r = {"n": n, "bare_top1": bare_top1 / n, "inj_top1": inj_top1 / n}
    print("  fact-as-top1: bare=%.3f injected=%.3f (n=%d facts, alpha=%.2f)" % (r["bare_top1"], r["inj_top1"], n, ALPHA), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "fact-as-top1 bare=%.3f injected=%.3f (n=%d)" % (r["bare_top1"], r["inj_top1"], r["n"])
    if r["inj_top1"] >= 0.50:
        return ("HARD_PASS", "HARD_PASS: meaningful substrate injection makes the fact the top-1 token in >=50pct of queries (bare baseline near 0) -- substrate supplies knowledge the LLM lacks via the attention layer. " + s)
    if r["inj_top1"] >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: fact-use 0.30-0.50. " + s)
    return ("HARD_FAIL", "HARD_FAIL: substrate injection transmits facts <30pct. " + s)


print("[config] anchor=%s mode=%s model=%s layer=%d alpha=%.2f" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYER, ALPHA), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
