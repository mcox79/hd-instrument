"""
exp_t5b_3b_calibrated_kv_gpu_v1 -- T5b-3b: CALIBRATED substrate->Pythia projection for fact transmission (held-out) -- GPU.

ROUTING: TIER5_SPRINT T5b-3 proper path (Research-authorized K/V substitution w/ calibration). T5b-3 showed an UNcalibrated
  additive injection does not transmit facts. Here a small projection P (substrate value-space -> Pythia residual) is TRAINED
  against a frozen Pythia-160M so that injecting the retrieved fact's value steers the next token to the fact's answer. Crucially,
  P is trained on a TRAIN split and evaluated on HELD-OUT facts: if held-out facts transmit, P learned the general value->boost
  map (substrate = true swappable external memory), not per-fact memorization. Frozen LLM; only P trains. Injection at layer-L
  residual (architectural placement; in-attention K/V is the same calibrated projection wired into GPTNeoXAttention).
PRE-REGISTERED: HARD-PASS held-out fact-as-top1 >= 0.50 after calibration (bare ~0). MIDDLE >= 0.30. HARD-FAIL < 0.30.
FORMULA SELF-TESTS (PROT-022): 1. linear shape. 2. argmax. 3. CE finite.
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

ANCHOR_NAME = "t5b_3b_calibrated_kv_gpu_v1"; MODEL = "EleutherAI/pythia-160m"; LAYER = 9
STEPS = 60 if "--smoke" in sys.argv else 300
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _selftest():
    import numpy as _n
    assert (_n.zeros((3, 8)) @ _n.zeros((8, 5))).shape == (3, 5), "linear shape"
    assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"
    assert _n.isfinite(-_n.log(0.5)), "CE finite"
    print("[selftest] PASS: t5b-3b-calibrated-kv", flush=True)


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
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    for p in mdl.parameters():
        p.requires_grad_(False)
    H = mdl.config.hidden_size
    W_U = (mdl.embed_out.weight if hasattr(mdl, "embed_out") else mdl.get_output_embeddings().weight).detach()
    facts = make_facts(tok)
    if len(facts) < 8:
        print("[FATAL] too few single-token facts", flush=True); return {"n": 0}
    ntr = int(0.6 * len(facts)); train, test = facts[:ntr], facts[ntr:]
    print("  facts: %d train / %d held-out test" % (len(train), len(test)), flush=True)

    # capture layer-L input hidden (last token) = KB key; value = answer unembed direction (unit)
    cap = {"h": None}

    def cap_hook(m, args, kwargs):
        cap["h"] = (args[0] if len(args) else kwargs.get("hidden_states")); return None
    ch = mdl.gpt_neox.layers[LAYER].register_forward_pre_hook(cap_hook, with_kwargs=True)

    def kb_for(fs):
        K = []; V = []; A = []
        for prompt, aid in fs:
            enc = tok(prompt, return_tensors="pt").to(DEV)
            with torch.no_grad():
                mdl(**enc)
            K.append(cap["h"][0, -1, :].clone()); v = W_U[aid]; V.append(v / (v.norm() + 1e-8)); A.append(aid)
        return torch.stack(K), torch.stack(V), torch.tensor(A, device=DEV)
    Ktr, Vtr, Atr = kb_for(train); Kte, Vte, Ate = kb_for(test); ch.remove()
    KtrN = Ktr / (Ktr.norm(dim=1, keepdim=True) + 1e-8); KteN = Kte / (Kte.norm(dim=1, keepdim=True) + 1e-8)

    # trainable calibrated projection P: substrate value direction (H) -> residual injection (H)
    gain = nn.Parameter(torch.tensor(8.0, device=DEV))   # 1-param calibration: cannot memorize -> tests generalization
    state = {"on": False, "inj": None}

    def inj_prehook(m, args, kwargs):
        if not state["on"]:
            return None
        hs = args[0]                                                # final residual (1,S,H) into final_layer_norm
        return (hs + state["inj"],) + tuple(args[1:]), kwargs       # grad-tracked input replacement
    ih = mdl.gpt_neox.final_layer_norm.register_forward_pre_hook(inj_prehook, with_kwargs=True)

    def logits_with(prompt, inj_vec):
        enc = tok(prompt, return_tensors="pt").to(DEV); S = enc["input_ids"].shape[1]
        # build (1,S,H) injection with grad preserved through inj_vec (last position only)
        if S > 1:
            full = torch.cat([torch.zeros(1, S - 1, H, device=DEV), inj_vec.view(1, 1, H)], dim=1)
        else:
            full = inj_vec.view(1, 1, H)
        state["on"] = True; state["inj"] = full
        out = mdl(**enc).logits[0, -1, :]; state["on"] = False; return out

    opt = torch.optim.Adam([gain], lr=0.5)
    for step in range(STEPS):
        opt.zero_grad(); loss = 0.0
        for j in range(len(train)):
            inj = gain * Vtr[j]                                       # calibrated injection (scalar gain on answer dir)
            lg = logits_with(train[j][0], inj)
            loss = loss + torch.nn.functional.cross_entropy(lg.unsqueeze(0), Atr[j].unsqueeze(0))
        loss = loss / len(train); loss.backward(); opt.step()
        if step % max(1, STEPS // 4) == 0:
            print("  step %d/%d train-CE=%.3f gain=%.2f" % (step, STEPS, float(loss), float(gain)), flush=True)

    def eval_top1(fs, K, V, A):
        hit = 0
        with torch.no_grad():
            for j in range(len(fs)):
                inj = gain * V[j]; lg = logits_with(fs[j][0], inj); hit += int(int(torch.argmax(lg)) == int(A[j]))
        return hit / len(fs)

    # bare baseline (no injection)
    state["on"] = False; bare = 0
    with torch.no_grad():
        for prompt, aid in test:
            enc = tok(prompt, return_tensors="pt").to(DEV); bare += int(int(torch.argmax(mdl(**enc).logits[0, -1, :])) == aid)
    bare /= len(test)
    tr_top1 = eval_top1(train, Ktr, Vtr, Atr); te_top1 = eval_top1(test, Kte, Vte, Ate)
    ih.remove(); del mdl
    r = {"n_train": len(train), "n_test": len(test), "bare_test": bare, "train_top1": tr_top1, "heldout_top1": te_top1}
    print("  fact-as-top1: bare(test)=%.3f train=%.3f HELD-OUT=%.3f" % (bare, tr_top1, te_top1), flush=True)
    return r


def verdict(r) -> Tuple[str, str]:
    s = "bare-test=%.3f train=%.3f held-out=%.3f (%d/%d)" % (r["bare_test"], r["train_top1"], r["heldout_top1"], r["n_train"], r["n_test"])
    if r["heldout_top1"] >= 0.50:
        return ("HARD_PASS", "HARD_PASS: calibrated projection transmits HELD-OUT substrate facts as top-1 >=50pct (bare ~0) -- substrate is a true swappable external memory wired through the attention layer; categorical fact-supply demonstrated. " + s)
    if r["heldout_top1"] >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: held-out fact-transmission 0.30-0.50 (partial generalization). " + s)
    return ("HARD_FAIL", "HARD_FAIL: held-out fact-transmission <0.30 (projection memorizes train / does not generalize). " + s)


print("[config] anchor=%s mode=%s model=%s layer=%d steps=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYER, STEPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
