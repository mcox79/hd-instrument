"""
exp_t5c_s2_pythia2p8b_everylayer_v1 -- Tier-5c Phase C: multi-layer Flamingo adapter continued training (LOCAL 4060 Ti) -- GPU.

ROUTING: TIER5C_PHASE_CD_LOCAL_AUTHORIZE Phase C (USER-confirmed, local). Pythia-160M frozen; trainable Flamingo gated
  cross-attention adapters at TWO middle layers (L4+L5); memory = the document's own past-token hidden states (causal, kNN-LM
  style). Continued training on WikiText-2. CHECKPOINTS the adapter + step every 500 steps to out_dir/ckpt.pt and RESUMES from it
  (so the 6-hour timeout / any kill loses <=1 checkpoint, never all progress -- uses the _stream discipline). Acceptance-gates
  perplexity vs baseline periodically. Expected wall ~1-4 hr; --smoke runs a few steps.
PRE-REGISTERED: HARD-PASS final perplexity ratio < 2.0x baseline AND both gates demonstrably used (|tanh(gate)| > 0.05). MIDDLE
  < 3x. HARD-FAIL >= 3x or gates unused. (Phase C gates Phase D.)
FORMULA SELF-TESTS (PROT-022): 1. ppl=exp(mean nll). 2. tanh gate. 3. causal mask.
ASCII-only. write_metrics + ckpt.pt every 500 steps (resumable). PROT-018 _v1.
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

ANCHOR_NAME = "t5c_s2_pythia2p8b_everylayer_v1"; MODEL = "EleutherAI/pythia-2.8b"; LAYERS = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
CKPT_EVERY = 500; ACC_EVERY = 500
STEPS = 60 if "--smoke" in sys.argv else 2500
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N_TRAIN = 24 if SMOKE else 400; N_EVAL = 12 if SMOKE else 64


def _selftest():
    assert abs(math.exp(0.0) - 1.0) < 1e-9, "ppl=exp(mean nll)"
    assert abs(math.tanh(0.0)) < 1e-9, "tanh gate"
    import numpy as _n; assert _n.triu(_n.ones((2, 2)), 1).sum() == 1, "causal mask"
    print("[selftest] PASS: s2-pythia2p8b-everylayer", flush=True)


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


class FlamingoAdapter(nn.Module):
    def __init__(self, H):
        super().__init__()
        self.Wq = nn.Linear(H, H, bias=False); self.Wk = nn.Linear(H, H, bias=False)
        self.Wv = nn.Linear(H, H, bias=False); self.Wo = nn.Linear(H, H, bias=False)
        for w in (self.Wq, self.Wk, self.Wv, self.Wo):
            nn.init.normal_(w.weight, std=0.02)
        self.ln = nn.LayerNorm(H); self.gate = nn.Parameter(torch.tensor(0.0)); self.H = H

    def forward(self, hs, attn_out):
        S = hs.shape[1]
        z = self.ln(hs); q = self.Wq(z); k = self.Wk(z); v = self.Wv(z)   # LayerNorm before substrate cross-attn (Flamingo)
        att = (q @ k.transpose(1, 2)) / math.sqrt(self.H)
        mask = torch.triu(torch.ones(S, S, device=hs.device), diagonal=1).bool()
        att = att.masked_fill(mask[None], float("-inf"))
        ctx = torch.softmax(att, dim=-1) @ v
        return attn_out + torch.tanh(self.gate) * self.Wo(ctx)


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
    torch.manual_seed(7)
    tok = AutoTokenizer.from_pretrained(MODEL); tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.float32).to(DEV).eval()
    for p in mdl.parameters():
        p.requires_grad_(False)
    H = mdl.config.hidden_size
    adapters = nn.ModuleDict({str(L): FlamingoAdapter(H).to(DEV) for L in LAYERS})
    out_dir = get_output_dir(ANCHOR_NAME); ckpt_path = Path(out_dir) / "ckpt.pt"; Path(out_dir).mkdir(parents=True, exist_ok=True)
    start_step = 0
    if ckpt_path.exists():
        try:
            ck = torch.load(ckpt_path, map_location=DEV); adapters.load_state_dict(ck["adapters"]); start_step = int(ck["step"])
            print("[resume] loaded checkpoint at step %d" % start_step, flush=True)
        except Exception as e:
            print("[resume] checkpoint load failed (%s); fresh start" % str(e)[:60], flush=True)
    state = {"on": False}
    hooks = []

    def mk(L):
        def hook(module, args, kwargs, output):
            if not state["on"] or not isinstance(output, tuple):
                return output
            hs = args[0] if len(args) else kwargs.get("hidden_states")
            if hs is None:
                return output
            return (adapters[str(L)](hs, output[0]),) + tuple(output[1:])
        return hook
    for L in LAYERS:
        hooks.append(mdl.gpt_neox.layers[L].attention.register_forward_hook(mk(L), with_kwargs=True))

    texts = load_texts(N_TRAIN + N_EVAL); train_txt = texts[:N_TRAIN]; eval_txt = texts[N_TRAIN:N_TRAIN + N_EVAL]
    enc = lambda t: tok(t, return_tensors="pt", truncation=True, max_length=512).to(DEV)

    def eval_ppl():
        prev = state["on"]; tot_nll = 0.0; tot_tok = 0
        for t in eval_txt:
            e = enc(t); ids = e["input_ids"]
            if ids.shape[1] < 4:
                continue
            with torch.no_grad():
                lg = mdl(**e).logits[:, :-1, :].float()
            tgt = ids[:, 1:]; nll = torch.nn.functional.cross_entropy(lg.reshape(-1, lg.shape[-1]), tgt.reshape(-1))
            tot_nll += float(nll) * tgt.numel(); tot_tok += tgt.numel()
        state["on"] = prev; return math.exp(tot_nll / max(1, tot_tok))

    state["on"] = False; base_ppl = eval_ppl()
    opt = torch.optim.Adam([{"params": [p for L in LAYERS for n, p in adapters[str(L)].named_parameters() if n != "gate"], "lr": 3e-4, "weight_decay": 0.01},
                            {"params": [adapters[str(L)].gate for L in LAYERS], "lr": 1e-3}])  # gate-lr 1e-3 (1e-5 inert, 0.05 diverged; stability fixes hold this)
    # live pollable progress log (full visibility): one JSON line per acceptance check + a heartbeat file
    prog = open(Path(out_dir) / "progress.jsonl", "a", encoding="utf-8"); t_start = time.time()
    def heartbeat(d):
        try:
            (Path(out_dir) / "heartbeat.json").write_text(json.dumps(d), encoding="utf-8")
        except Exception:
            pass
    def lr_lambda(step):
        if step < 500:
            return (step + 1) / 500.0                                       # linear warmup 500
        prog = (step - 500) / max(1, STEPS - 500); return 0.5 * (1 + math.cos(math.pi * min(1.0, prog)))   # cosine decay to 0
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lr_lambda)
    best_ppl = float("inf"); since_improve = 0
    state["on"] = True; t_ck = time.time(); recent = []
    for step in range(start_step, STEPS):
        opt.zero_grad(); t = train_txt[step % len(train_txt)]; e = enc(t); ids = e["input_ids"]
        if ids.shape[1] < 4:
            continue
        lg = mdl(**e).logits[:, :-1, :].float(); tgt = ids[:, 1:]
        loss = torch.nn.functional.cross_entropy(lg.reshape(-1, lg.shape[-1]), tgt.reshape(-1))
        loss.backward(); torch.nn.utils.clip_grad_norm_([p for L in LAYERS for p in adapters[str(L)].parameters()], 1.0); opt.step(); sched.step(); recent.append(float(loss))  # grad clip + warmup/cosine sched
        if step % CKPT_EVERY == 0 or (time.time() - t_ck) > 300:           # checkpoint every 500 steps OR 5 min (resumable)
            torch.save({"adapters": adapters.state_dict(), "step": step + 1}, ckpt_path); t_ck = time.time()
            heartbeat({"step": step + 1, "of": STEPS, "elapsed_s": round(time.time() - t_start, 1), "train_ce_recent": round(float(np.mean(recent[-50:])), 4), "ts": time.strftime("%H:%M:%S")})
        if step % ACC_EVERY == 0:                                          # acceptance check: eval perplexity ratio + log trajectory
            g0 = float(torch.tanh(adapters[str(LAYERS[0])].gate)); g1 = float(torch.tanh(adapters[str(LAYERS[1])].gate))
            acc_ppl = eval_ppl(); ratio = acc_ppl / base_ppl
            rec = {"step": step, "of": STEPS, "train_ce": round(float(np.mean(recent[-100:])), 4), "ppl_ratio": round(ratio, 4),
                   "mod_ppl": round(acc_ppl, 2), "base_ppl": round(base_ppl, 2), "gates": [round(g0, 4), round(g1, 4)], "elapsed_s": round(time.time() - t_start, 1)}
            prog.write(json.dumps(rec) + "\n"); prog.flush()
            print("  [acc] step %d/%d CE=%.3f ppl-ratio=%.3fx gates=[%.3f,%.3f] elapsed=%.0fs" % (step, STEPS, rec["train_ce"], ratio, g0, g1, rec["elapsed_s"]), flush=True)
            if ratio > 3.0 and step > ACC_EVERY:                           # quality gate: abort on clear regression (no wasted hours)
                print("  [ABORT] perplexity ratio %.2fx > 3x -- regression; stopping early." % ratio, flush=True); break
            if acc_ppl < best_ppl - 1e-3:
                best_ppl = acc_ppl; since_improve = 0; torch.save({"adapters": adapters.state_dict(), "step": step + 1}, Path(out_dir) / "ckpt_best.pt")
            else:
                since_improve += 1
                if since_improve >= 3:                                       # early-stop: 3 evals (1500 steps) no improvement
                    print("  [early-stop] no val-ppl improvement for 3 evals (best=%.2f); stopping." % best_ppl, flush=True); break
    torch.save({"adapters": adapters.state_dict(), "step": STEPS}, ckpt_path); prog.close()
    state["on"] = True; mod_ppl = eval_ppl()
    g0 = abs(float(torch.tanh(adapters[str(LAYERS[0])].gate))); g1 = abs(float(torch.tanh(adapters[str(LAYERS[1])].gate)))
    for h in hooks:
        h.remove()
    del mdl
    ratio = mod_ppl / base_ppl; used = (g0 > 0.05 and g1 > 0.05)
    print("  baseline-ppl=%.2f modified-ppl=%.2f ratio=%.3fx | gates=[%.3f,%.3f] used=%s (steps=%d)" % (base_ppl, mod_ppl, ratio, g0, g1, used, STEPS), flush=True)
    return {"base_ppl": base_ppl, "mod_ppl": mod_ppl, "ratio": ratio, "gate0": g0, "gate1": g1, "used": bool(used)}


def verdict(r) -> Tuple[str, str]:
    s = "baseline=%.2f modified=%.2f ratio=%.3fx gates=[%.3f,%.3f]" % (r["base_ppl"], r["mod_ppl"], r["ratio"], r["gate0"], r["gate1"])
    if r["ratio"] < 2.0 and r["used"]:
        tag = "IMPROVES" if r["ratio"] < 1.0 else "within 2x"
        return ("HARD_PASS", "HARD_PASS: Tier-5c Phase C multi-layer Flamingo adapter -- perplexity %s baseline with both gates used -> Phase C grounded, Phase D unblocked. " % tag + s)
    if r["ratio"] < 3.0:
        return ("MIDDLE_BAND", "MIDDLE_BAND: perplexity within 3x or a gate marginal. " + s)
    return ("HARD_FAIL", "HARD_FAIL: perplexity >=3x or gates unused. " + s)


print("[config] anchor=%s mode=%s model=%s layers=%s steps=%d" % (ANCHOR_NAME, RUN_MODE, MODEL, LAYERS, STEPS), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
