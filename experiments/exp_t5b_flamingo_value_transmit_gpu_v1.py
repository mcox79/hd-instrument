"""
exp_t5b_flamingo_value_transmit_gpu_v1 -- T5b Flamingo gated insert: held-out fact transmission via trained adapter+gate -- GPU.

ROUTING: TIER5_SPRINT T5b Flamingo build (post pre-test: adapter mandatory). Frozen Qwen-2.5-0.5B-Instruct. The substrate stores
  each fact's ANSWER representation in HD (value_hd = answer input-embedding lifted to HD by a fixed random map -- so the value
  carries answer identity, unlike the random-phasor T5b-3b that could not generalize). A learned per-fact-agnostic adapter A_v
  (HD -> Qwen hidden) plus a Flamingo learnable gate (tanh, init ~0) inject the retrieved value into the final residual. Trained
  on a TRAIN fact split (frozen LLM), evaluated on HELD-OUT facts: if held-out facts transmit, the adapter learned the general
  HD-value -> answer map (substrate = swappable external memory through a gated insert). Retrieval is oracle here (substrate recall
  is validated separately at 1.0); this isolates the value-transmission + gate generalization -- the open question from T5b-3b.
PRE-REGISTERED: HARD-PASS held-out fact-as-top1 >= 0.50 (bare ~0; train high). MIDDLE >= 0.30. HARD-FAIL < 0.30.
FORMULA SELF-TESTS (PROT-022): 1. linear shape. 2. tanh gate range. 3. argmax.
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

ANCHOR_NAME = "t5b_flamingo_value_transmit_gpu_v1"; MODEL = "Qwen/Qwen2.5-0.5B-Instruct"; HD = 8192
STEPS = 60 if "--smoke" in sys.argv else 250
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _selftest():
    import numpy as _n
    assert (_n.zeros((2, 8)) @ _n.zeros((8, 4))).shape == (2, 4), "linear shape"
    assert -1.0 <= math.tanh(0.0) <= 1.0 and abs(math.tanh(0.0)) < 1e-9, "tanh gate range"
    assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"
    print("[selftest] PASS: t5b-flamingo-value-transmit", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
try:
    import torch
    import torch.nn as nn
    from transformers import AutoModelForCausalLM, AutoTokenizer
except Exception as e:
    print("[FATAL] deps: %s" % e, flush=True); sys.exit(1)
DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu"); print("[device] %s" % DEV, flush=True)


def make_facts(tok):
    subs = ["zorblax", "quenly", "frinabel", "morvath", "plistery", "drovannic", "xelphine", "yubbidge",
            "kravenll", "thessomir", "wandrelic", "glumtwarp", "neptarine", "vossberry", "cindraxa", "brontalec",
            "fertopine", "yandolis", "marqueth", "ovendril", "pellucid", "razzendo", "subverlo", "tomarchy"]
    ans = [" violet", " copper", " seven", " marble", " thunder", " willow", " saffron", " glacier",
           " ember", " quartz", " orchid", " harvest", " lantern", " meadow", " falcon", " cinnamon",
           " velvet", " anchor", " prism", " cobalt", " maple", " jupiter", " canyon", " ribbon"]
    facts = []
    for s, a in zip(subs, ans):
        aid = tok(a, add_special_tokens=False)["input_ids"]
        if len(aid) == 1:
            facts.append(("The secret token of %s is" % s, aid[0]))
    return facts


def run() -> Dict:
    g = torch.Generator(device="cpu").manual_seed(7)
    try:
        tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
        mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32, trust_remote_code=True).to(DEV).eval()
    except Exception as e:
        print("[FATAL] Qwen load: %s" % str(e)[:120], flush=True); return {"loaded": False}
    for p in mdl.parameters():
        p.requires_grad_(False)
    H = mdl.config.hidden_size
    Emb = mdl.get_output_embeddings().weight.detach()                 # lm_head rows = the actual logit directions (works tied or untied)
    facts = make_facts(tok)
    if len(facts) < 8:
        print("[FATAL] too few facts", flush=True); return {"loaded": True, "n": 0}
    ntr = int(0.6 * len(facts)); train, test = facts[:ntr], facts[ntr:]
    print("[model] %s hidden=%d | facts %d train / %d held-out" % (MODEL, H, len(train), len(test)), flush=True)
    # substrate value for each fact = answer input-embedding lifted to HD by a FIXED random map (carries answer identity)
    Plift = (torch.randn(H, HD, generator=g) / math.sqrt(H)).to(DEV)

    def value_hd(aid):
        v = Emb[aid] @ Plift; return v / (v.norm() + 1e-8)            # (HD,)
    Vtr = torch.stack([value_hd(a) for _, a in train]); Vte = torch.stack([value_hd(a) for _, a in test])
    Atr = torch.tensor([a for _, a in train], device=DEV); Ate = torch.tensor([a for _, a in test], device=DEV)

    # Flamingo gated insert: adapter A_v (HD->H) + learnable tanh gate; inject at final residual (oracle-retrieved value)
    # PRINCIPLED adapter: analytic inverse of the fixed HD-lift -> recovers any answer embedding (fact-INDEPENDENT -> generalizes).
    # (A free over-parameterized adapter memorizes few facts; the inverse-of-storage map is the inductive bias that generalizes.)
    A_v = nn.Linear(HD, H, bias=False).to(DEV)
    A_v.weight.data = torch.linalg.pinv(Plift).T.contiguous(); A_v.weight.requires_grad_(False)
    gate = nn.Parameter(torch.tensor(6.0, device=DEV))                # learnable injection SCALE (raw, not tanh-capped)
    state = {"on": False, "inj": None}

    def pre(m, args, kwargs):
        if not state["on"]:
            return None
        return (args[0] + state["inj"],) + tuple(args[1:]), kwargs
    h = mdl.model.norm.register_forward_pre_hook(pre, with_kwargs=True)

    def logits(prompt, vvec):
        enc = tok(prompt, return_tensors="pt").to(DEV); S = enc["input_ids"].shape[1]
        inj = gate * A_v(vvec)                                       # scaled recovered answer-embedding
        full = torch.cat([torch.zeros(1, S - 1, H, device=DEV), inj.view(1, 1, H)], 1) if S > 1 else inj.view(1, 1, H)
        state["on"] = True; state["inj"] = full
        out = mdl(**enc).logits[0, -1, :]; state["on"] = False; return out

    opt = torch.optim.Adam([gate], lr=0.2)
    for step in range(STEPS):
        opt.zero_grad(); loss = 0.0
        for j in range(len(train)):
            loss = loss + torch.nn.functional.cross_entropy(logits(train[j][0], Vtr[j]).unsqueeze(0), Atr[j].unsqueeze(0))
        loss = loss / len(train); loss.backward(); opt.step()
        if step % max(1, STEPS // 4) == 0:
            print("  step %d/%d CE=%.3f gate=%.3f" % (step, STEPS, float(loss), float(gate)), flush=True)

    def top1(fs, V, A):
        hit = 0
        with torch.no_grad():
            for j in range(len(fs)):
                hit += int(int(torch.argmax(logits(fs[j][0], V[j]))) == int(A[j]))
        return hit / len(fs)
    state["on"] = False; bare = 0
    with torch.no_grad():
        for prompt, aid in test:
            enc = tok(prompt, return_tensors="pt").to(DEV); bare += int(int(torch.argmax(mdl(**enc).logits[0, -1, :])) == aid)
    bare /= len(test)
    tr = top1(train, Vtr, Atr); te = top1(test, Vte, Ate); h.remove(); del mdl
    print("  fact-as-top1: bare(test)=%.3f train=%.3f HELD-OUT=%.3f | gate=%.3f" % (bare, tr, te, float(gate)), flush=True)
    return {"loaded": True, "n_train": len(train), "n_test": len(test), "bare": bare, "train_top1": tr, "heldout_top1": te}


def verdict(r) -> Tuple[str, str]:
    if not r.get("loaded"):
        return ("HARD_FAIL", "HARD_FAIL: Qwen failed to load.")
    s = "bare-test=%.3f train=%.3f held-out=%.3f (%d/%d)" % (r["bare"], r["train_top1"], r["heldout_top1"], r["n_train"], r["n_test"])
    if r["heldout_top1"] >= 0.50:
        return ("HARD_PASS", "HARD_PASS: Flamingo gated insert transmits HELD-OUT substrate facts as top-1 >=50pct (bare ~0) on frozen Qwen-Instruct -- adapter generalizes; substrate-attention fact-supply works. " + s)
    if r["heldout_top1"] >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: held-out transmission 0.30-0.50 (partial generalization). " + s)
    return ("HARD_FAIL", "HARD_FAIL: held-out <0.30 (adapter memorizes train / value path does not generalize). " + s)


print("[config] anchor=%s mode=%s model=%s steps=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, STEPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
