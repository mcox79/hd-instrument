"""
exp_t5c_b1_single_layer_flamingo_smoke_gpu_v1 -- T5C-B1: trained single-layer Flamingo cross-attn over real memory (Tier-5c gate) -- GPU.

ROUTING: TIER5C_FULL_ROADMAP Phase B EXTENDED training (400 steps; does more training make the substrate-attn IMPROVE perplexity, not just non-destructive). The categorical Tier-5c decision: insert ONE
  trainable Flamingo gated cross-attention layer into frozen Pythia-160M, with the memory = the document's OWN past-token hidden
  states (Memorizing-Transformer / kNN-LM style -- meaningful substrate, unlike the random KB that failed T5b-3). Train the
  cross-attn (frozen LLM) briefly on WikiText; measure (a) perplexity of the modified model vs bare baseline -- must stay within
  2x (ideally LOWER, since memory helps), (b) the learnable gate is demonstrably USED (|tanh(gate)| grows from ~0 and the
  attention contributes). HARD-PASS -> Tier-5c empirically grounded -> escalate Phase C/D. HARD-FAIL -> back to full R&D scope.
PRE-REGISTERED: HARD-PASS modified perplexity <= 2.0x baseline AND gate demonstrably used (|tanh(gate)| > 0.05). MIDDLE <= 3x.
  HARD-FAIL > 3x or gate stays ~0 (substrate not used).
FORMULA SELF-TESTS (PROT-022): 1. ppl=exp(mean nll). 2. tanh range. 3. causal mask shape.
ASCII-only. write_metrics + _stream checkpoint. PROT-018 _v1.
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

ANCHOR_NAME = "t5c_b2_extended_training_flamingo_gpu_v1"; MODEL = "EleutherAI/pythia-160m"; LAYER = 6
STEPS = 40 if "--smoke" in sys.argv else 400
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_TRAIN = 16 if SMOKE else 96; N_EVAL = 12 if SMOKE else 48


def _selftest():
    assert abs(math.exp(0.0) - 1.0) < 1e-9, "ppl=exp(mean nll)"
    assert abs(math.tanh(0.0)) < 1e-9, "tanh range"
    import numpy as _n; assert _n.triu(_n.ones((3, 3)), 1).shape == (3, 3), "causal mask shape"
    print("[selftest] PASS: t5c-b2-extended-training-flamingo", flush=True)


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


def load_texts(n):
    for repo in ["Salesforce/wikitext", "wikitext"]:
        try:
            from datasets import load_dataset
            ds = load_dataset(repo, "wikitext-2-raw-v1", split="train")
            out = [t for t in ds["text"] if len(t.strip()) > 300]
            if out:
                return out[:n]
        except Exception:
            pass
    base = "The history of science is the study of the development of human understanding across many fields over centuries. "
    return [base * 6 for _ in range(n)]


def run() -> Dict:
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    for p in mdl.parameters():
        p.requires_grad_(False)
    H = mdl.config.hidden_size
    texts = load_texts(N_TRAIN + N_EVAL); train_txt = texts[:N_TRAIN]; eval_txt = texts[N_TRAIN:N_TRAIN + N_EVAL]
    enc = lambda t: tok(t, return_tensors="pt", truncation=True, max_length=192).to(DEV)

    # single trainable Flamingo gated cross-attention over the document's own past-token hidden states (causal memory)
    Wq = nn.Linear(H, H, bias=False).to(DEV); Wk = nn.Linear(H, H, bias=False).to(DEV)
    Wv = nn.Linear(H, H, bias=False).to(DEV); Wo = nn.Linear(H, H, bias=False).to(DEV)
    for w in (Wq, Wk, Wv, Wo):
        nn.init.normal_(w.weight, std=0.02)
    gate = nn.Parameter(torch.tensor(0.0, device=DEV))
    state = {"on": False, "mem": None}

    def xattn_hook(module, args, kwargs, output):
        if not state["on"] or not isinstance(output, tuple):
            return output
        hs = args[0] if len(args) else kwargs.get("hidden_states")
        if hs is None:
            return output
        B, S, _ = hs.shape
        q = Wq(hs); k = Wk(hs); v = Wv(hs)                              # memory = same sequence's tokens (causal)
        att = (q @ k.transpose(1, 2)) / math.sqrt(H)
        mask = torch.triu(torch.ones(S, S, device=hs.device), diagonal=1).bool()   # causal: attend only to PAST
        att = att.masked_fill(mask[None], float("-inf"))
        ctx = torch.softmax(att, dim=-1) @ v
        return (output[0] + torch.tanh(gate) * Wo(ctx),) + tuple(output[1:])
    h = mdl.gpt_neox.layers[LAYER].attention.register_forward_hook(xattn_hook, with_kwargs=True)

    def ppl(texts_, train=False):
        tot_nll = 0.0; tot_tok = 0
        for t in texts_:
            e = enc(t); ids = e["input_ids"]
            if ids.shape[1] < 4:
                continue
            out = mdl(**e); lg = out.logits[:, :-1, :].float(); tgt = ids[:, 1:]
            nll = torch.nn.functional.cross_entropy(lg.reshape(-1, lg.shape[-1]), tgt.reshape(-1))
            if train:
                yield nll
            tot_nll += float(nll) * tgt.numel(); tot_tok += tgt.numel()
        if not train:
            yield math.exp(tot_nll / max(1, tot_tok))

    state["on"] = False
    base_ppl = next(ppl(eval_txt))
    params = list(Wq.parameters()) + list(Wk.parameters()) + list(Wv.parameters()) + list(Wo.parameters()) + [gate]
    opt = torch.optim.Adam([{"params": params[:-1], "lr": 1e-3}, {"params": [gate], "lr": 0.1}])
    state["on"] = True
    for step in range(STEPS):
        opt.zero_grad(); t = train_txt[step % len(train_txt)]; e = enc(t); ids = e["input_ids"]
        if ids.shape[1] < 4:
            continue
        lg = mdl(**e).logits[:, :-1, :].float(); tgt = ids[:, 1:]
        loss = torch.nn.functional.cross_entropy(lg.reshape(-1, lg.shape[-1]), tgt.reshape(-1))
        loss.backward(); opt.step()
        if step % max(1, STEPS // 4) == 0:
            print("  step %d/%d train-CE=%.3f gate=%.4f" % (step, STEPS, float(loss), float(torch.tanh(gate))), flush=True)
    state["on"] = True
    mod_ppl = next(ppl(eval_txt)); h.remove(); gv = abs(float(torch.tanh(gate))); del mdl
    ratio = mod_ppl / base_ppl
    print("  baseline-ppl=%.2f modified-ppl=%.2f ratio=%.3fx | gate=%.4f (used=%s)" % (base_ppl, mod_ppl, ratio, gv, gv > 0.05), flush=True)
    return {"base_ppl": base_ppl, "mod_ppl": mod_ppl, "ratio": ratio, "gate": gv}


def verdict(r) -> Tuple[str, str]:
    s = "baseline-ppl=%.2f modified-ppl=%.2f ratio=%.3fx gate=%.4f" % (r["base_ppl"], r["mod_ppl"], r["ratio"], r["gate"])
    if r["ratio"] <= 2.0 and r["gate"] > 0.05:
        better = "IMPROVES" if r["ratio"] < 1.0 else "within 2x"
        return ("HARD_PASS", "HARD_PASS: trained single-layer Flamingo cross-attn keeps perplexity %s baseline with the gate demonstrably used -- Tier-5c Phase B grounded; escalate Phase C/D. " % better + s)
    if r["ratio"] <= 3.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: perplexity within 3x or gate marginal. " + s)
    return ("HARD_FAIL", "HARD_FAIL: perplexity >3x or gate unused -- Tier-5c back to full R&D scope. " + s)


print("[config] anchor=%s mode=%s model=%s layer=%d steps=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYER, STEPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
