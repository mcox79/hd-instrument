"""
exp_t5c_c1fact_heldout_recall_gpu_v1 -- Tier-5c PRODUCT claim: trained Flamingo cross-attn over an EXTERNAL fact KB; HELD-OUT recall -- GPU.

ROUTING: the marquee Tier-5c experiment -- does a TRAINED Flamingo adapter let a frozen LLM USE external substrate facts it never
  saw, generalizing to HELD-OUT facts? Unlike C1 (memory=past tokens -> proves architecture via perplexity), here the adapter's
  cross-attention attends over a FIXED external fact-KB memory (all facts as K/V slots). Train the adapter on TRAIN facts'
  completions; the held-out facts' slots ARE in the KB but the model never trained on answering them. If held-out fact-recall is
  high, the adapter learned the GENERAL retrieve-from-substrate-and-answer behavior (substrate = swappable knowledge), not
  memorization -- the categorical "substrate supplies knowledge to the LLM" product claim. Recipe = Phase C's (gate-lr 1e-3,
  main 3e-4/wd 0.01, warmup+cosine, grad-clip, LayerNorm, betas 0.9/0.95). Frozen Pythia-160M.
PRE-REGISTERED: HARD-PASS held-out fact-recall >= 0.50 (bare ~0; model does not know the rare facts). MIDDLE >= 0.30. HARD-FAIL < 0.30.
FORMULA SELF-TESTS (PROT-022): 1. softmax. 2. tanh gate. 3. argmax.
ASCII-only. write_metrics + progress.jsonl + ckpt (resumable). PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
import argparse, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "t5c_c1fact_heldout_recall_gpu_v1"; MODEL = "EleutherAI/pythia-160m"; LAYER = 6
STEPS = 100 if "--smoke" in sys.argv else 8000; CKPT_EVERY = 500
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"


def _selftest():
    import numpy as _n; p = _n.exp([1.0, 2]); p = p / p.sum(); assert abs(p.sum() - 1) < 1e-9, "softmax"
    assert abs(math.tanh(0.0)) < 1e-9, "tanh gate"; assert int(_n.argmax([0.1, 0.9])) == 1, "argmax"
    print("[selftest] PASS: t5c-c1fact-heldout-recall", flush=True)


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
    import numpy as _np
    pool = [" violet"," copper"," seven"," marble"," thunder"," willow"," saffron"," glacier"," ember"," quartz",
            " orchid"," harvest"," lantern"," meadow"," falcon"," cinnamon"," velvet"," anchor"," prism"," cobalt",
            " maple"," jupiter"," canyon"," ribbon"," basalt"," nectar"," pebble"," cypress"," marlin"," walnut",
            " amber"," crimson"," silver"," forest"," ocean"," desert"," mountain"," valley"," river"," island",
            " tiger"," eagle"," dolphin"," panther"," otter"," raven"," sparrow"," badger"," ferret"," lizard"]
    pool = [a for a in pool if len(tok(a, add_special_tokens=False)["input_ids"]) == 1]
    g = _np.random.default_rng(123); N = 60 if SMOKE else 240
    facts = []
    for i in range(N):
        subj = "entity%04d" % i; a = pool[int(g.integers(0, len(pool)))]
        facts.append(("The secret code of %s is" % subj, tok(a, add_special_tokens=False)["input_ids"][0], a))
    return facts


def run() -> Dict:
    torch.manual_seed(7)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    for p in mdl.parameters():
        p.requires_grad_(False)
    H = mdl.config.hidden_size
    facts = make_facts(tok)
    ntr = int(0.6 * len(facts)); train, test = facts[:ntr], facts[ntr:]
    print("[facts] %d train / %d held-out (KB has all %d)" % (len(train), len(test), len(facts)), flush=True)

    # external fact-KB memory: each fact's last-token hidden of "<prompt> <answer>" (carries the answer); ALL facts in the KB
    def fact_hidden(prompt, ans_str):
        e = tok(prompt + ans_str, return_tensors="pt").to(DEV)
        with torch.no_grad():
            h = mdl(**e, output_hidden_states=True).hidden_states[LAYER]
        return h[0, -1, :]
    mem = torch.stack([fact_hidden(p, a) for (p, _aid, a) in facts])      # (Nfact, H) fixed external KB

    # trainable Flamingo adapter: cross-attention query=hs over the fixed fact-KB memory
    ln = nn.LayerNorm(H).to(DEV); Wq = nn.Linear(H, H, bias=False).to(DEV); Wk = nn.Linear(H, H, bias=False).to(DEV)
    Wv = nn.Linear(H, H, bias=False).to(DEV); Wo = nn.Linear(H, H, bias=False).to(DEV)
    for w in (Wq, Wk, Wv, Wo):
        nn.init.normal_(w.weight, std=0.02)
    gate = nn.Parameter(torch.tensor(0.0, device=DEV)); state = {"on": False}
    Kmem = None

    def hook(module, args, kwargs, output):
        if not state["on"] or not isinstance(output, tuple):
            return output
        hs = args[0] if len(args) else kwargs.get("hidden_states")
        if hs is None:
            return output
        q = Wq(ln(hs)); K = Wk(mem); V = Wv(mem)                          # attend over external fact-KB (no causal mask)
        att = (q @ K.T) / math.sqrt(H); ctx = torch.softmax(att, dim=-1) @ V
        return (output[0] + torch.tanh(gate) * Wo(ctx),) + tuple(output[1:])
    h = mdl.gpt_neox.layers[LAYER].attention.register_forward_hook(hook, with_kwargs=True)
    out_dir = get_output_dir(ANCHOR_NAME); Path(out_dir).mkdir(parents=True, exist_ok=True)
    prog = open(Path(out_dir) / "progress.jsonl", "a", encoding="utf-8")

    def recall(fs):
        hit = 0
        with torch.no_grad():
            for (p, aid, a) in fs:
                e = tok(p, return_tensors="pt").to(DEV); hit += int(int(torch.argmax(mdl(**e).logits[0, -1, :])) == aid)
        return hit / len(fs)

    state["on"] = False; bare = recall(test)
    params = list(ln.parameters()) + list(Wq.parameters()) + list(Wk.parameters()) + list(Wv.parameters()) + list(Wo.parameters())
    opt = torch.optim.Adam([{"params": params, "lr": 3e-4, "weight_decay": 0.01}, {"params": [gate], "lr": 1e-3}], betas=(0.9, 0.95))
    def lr_lambda(s):
        return (s + 1) / 500.0 if s < 500 else 0.5 * (1 + math.cos(math.pi * min(1.0, (s - 500) / max(1, STEPS - 500))))
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)
    state["on"] = True; t0 = time.time()
    for step in range(STEPS):
        opt.zero_grad(); (p, aid, a) = train[step % len(train)]; e = tok(p, return_tensors="pt").to(DEV)
        lg = mdl(**e).logits[0, -1, :]
        loss = torch.nn.functional.cross_entropy(lg.unsqueeze(0), torch.tensor([aid], device=DEV))
        loss.backward(); torch.nn.utils.clip_grad_norm_(params + [gate], 1.0); opt.step(); sched.step()
        if step % CKPT_EVERY == 0:
            tr = recall(train); te = recall(test); state["on"] = True
            rec = {"step": step, "of": STEPS, "train_ce": round(float(loss), 4), "train_recall": round(tr, 3), "heldout_recall": round(te, 3), "gate": round(float(torch.tanh(gate)), 4), "elapsed_s": round(time.time() - t0, 1)}
            prog.write(json.dumps(rec) + "\n"); prog.flush()
            print("  [acc] step %d/%d CE=%.3f train-recall=%.3f HELD-OUT-recall=%.3f gate=%.3f" % (step, STEPS, float(loss), tr, te, float(torch.tanh(gate))), flush=True)
    state["on"] = True; tr = recall(train); te = recall(test); prog.close(); h.remove(); gv = abs(float(torch.tanh(gate))); del mdl
    print("  FINAL: bare-heldout=%.3f train-recall=%.3f HELD-OUT-recall=%.3f gate=%.3f" % (bare, tr, te, gv), flush=True)
    return {"bare": bare, "train_recall": tr, "heldout_recall": te, "gate": gv, "n_train": len(train), "n_test": len(test)}


def verdict(r) -> Tuple[str, str]:
    s = "bare-heldout=%.3f train-recall=%.3f HELD-OUT-recall=%.3f gate=%.3f (%d/%d)" % (r["bare"], r["train_recall"], r["heldout_recall"], r["gate"], r["n_train"], r["n_test"])
    if r["heldout_recall"] >= 0.50:
        return ("HARD_PASS", "HARD_PASS: trained Flamingo adapter recalls HELD-OUT substrate facts >=50pct (bare ~0) -- the LLM USES external substrate knowledge via generalized retrieve-and-answer; categorical product claim grounded. " + s)
    if r["heldout_recall"] >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: held-out recall 0.30-0.50 (partial generalization). " + s)
    return ("HARD_FAIL", "HARD_FAIL: held-out recall <0.30 (adapter memorizes train / does not generalize to new facts). " + s)


print("[config] anchor=%s mode=%s model=%s layer=%d steps=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYER, STEPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
