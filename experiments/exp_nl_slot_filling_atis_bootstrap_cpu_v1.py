"""
exp_nl_slot_filling_atis_bootstrap_cpu_v1.py -- ATIS slot-filling with BOOTSTRAP error bars -- CPU.

ROUTING: Research Direction 1 (multi-seed/firmed Tier-B->Tier-A promotion). The slot-filler is count-DETERMINISTIC (no training
  seed variance), so seed-resampling is moot; instead BOOTSTRAP-resample the test sentences (B=1000) to get a sampling-error CI on
  micro slot-F1 + intent accuracy. Same substrate mechanism as nl_slot_filling_atis_cpu_v1 (emission word->slot + slot-bigram
  transition + Viterbi; intent = bag-of-words count-NB). Point slot-F1 was 0.871. Promote to Tier-A only if the bootstrap LOWER
  bound clears the 0.85 bar (sampling-robust). ATIS cached offline (HF_*_OFFLINE forced; no network on runner). Substrate-only.
PRE-REGISTERED: HARD-PASS slot-F1 2.5th-percentile >= 0.85 AND intent-acc point >= 0.80 (Tier-A: sampling-robust frame-role binding).
  MIDDLE point slot-F1 0.65-0.85 or lower-CI < 0.85. HARD-FAIL point slot-F1 < 0.50. UNKNOWN if dataset load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import os
os.environ["HF_HUB_OFFLINE"] = "1"; os.environ["HF_DATASETS_OFFLINE"] = "1"
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, time, math
from pathlib import Path
from typing import Dict, Tuple
from collections import defaultdict, Counter
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "nl_slot_filling_atis_bootstrap_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
B_BOOT = 200 if SMOKE else 1000


def _feats(w):
    wl = w.lower(); fs = []
    if any(c.isdigit() for c in w): fs.append("F:DIGIT")
    if w[:1].isupper(): fs.append("F:CAP")
    for k in (2, 3, 4):
        if len(wl) >= k: fs.append("S%d:%s" % (k, wl[-k:]))
    return fs


def _spans(labels):
    sp = set(); i = 0; n = len(labels)
    while i < n:
        l = labels[i]
        if l.startswith("B-"):
            t = l[2:]; j = i + 1
            while j < n and labels[j] == "I-" + t: j += 1
            sp.add((i, j, t)); i = j
        else: i += 1
    return sp


def _selftest():
    assert _spans(["B-a", "I-a", "O", "B-b"]) == {(0, 2, "a"), (3, 4, "b")}
    # bootstrap of a trivial all-correct set must give F1=1 with zero variance
    tp = np.array([2, 1]); fp = np.array([0, 0]); fn = np.array([0, 0])
    rng = np.random.default_rng(0); idx = rng.integers(0, 2, size=(5, 2))
    f1s = []
    for r in idx:
        T = tp[r].sum(); F = fp[r].sum(); N = fn[r].sum()
        p = T / (T + F + 1e-9); rc = T / (T + N + 1e-9); f1s.append(2 * p * rc / (p + rc + 1e-9))
    assert min(f1s) > 0.999
    print("[selftest] PASS: nl-slot-filling-atis-bootstrap", flush=True)


def _load():
    try:
        from datasets import load_dataset
        ds = load_dataset("tuetschek/atis")
        def conv(split):
            out = []
            for ex in ds[split]:
                toks = ex["text"].split(); slots = ex["slots"].split()
                if len(toks) == len(slots) and toks:
                    out.append((toks, slots, ex["intent"]))
            return out
        return conv("train"), conv("test")
    except Exception as e:
        print("[data] fail %s" % str(e)[:120], flush=True); return None, None


def run() -> Dict:
    train, test = _load()
    if not train:
        return {"error": "load_failed", "slot_f1": 0.0}
    if SMOKE: train = train[:400]; test = test[:120]
    labels = sorted({s for _t, ss, _i in train for s in ss}); T = len(labels)
    intents = sorted({i for _t, _s, i in train})
    K = 0.1
    emit = defaultdict(Counter); trans = defaultdict(Counter); feat_emit = defaultdict(Counter)
    lab_count = Counter(); prev_count = Counter(); vocab = set()
    intent_w = defaultdict(Counter); intent_tot = Counter()
    for toks, slots, intent in train:
        prev = "<S>"
        for w, s in zip(toks, slots):
            wl = w.lower(); emit[s][wl] += 1; lab_count[s] += 1; vocab.add(wl)
            for f in _feats(w): feat_emit[s][f] += 1
            trans[prev][s] += 1; prev_count[prev] += 1; prev = s
        intent_tot[intent] += 1
        for w in set(t.lower() for t in toks): intent_w[intent][w] += 1
    Vsz = len(vocab)

    def log_emit(w, s):
        wl = w.lower()
        if wl in vocab: return math.log((emit[s][wl] + K) / (lab_count[s] + K * Vsz))
        sc = math.log((lab_count[s] + K) / (sum(lab_count.values()) + K * T))
        for f in _feats(w): sc += math.log((feat_emit[s][f] + K) / (lab_count[s] + K * 200))
        return sc
    TM = np.array([[math.log((trans[labels[p]][labels[c]] + K) / (prev_count[labels[p]] + K * T)) for c in range(T)] for p in range(T)])
    sv = np.array([math.log((trans["<S>"][labels[c]] + K) / (prev_count["<S>"] + K * T)) for c in range(T)])

    def viterbi(toks):
        em0 = np.array([log_emit(toks[0], labels[c]) for c in range(T)]); V = sv + em0; bp = []
        for i in range(1, len(toks)):
            ei = np.array([log_emit(toks[i], labels[c]) for c in range(T)])
            cand = V[:, None] + TM; back = np.argmax(cand, axis=0); V = cand[back, np.arange(T)] + ei; bp.append(back)
        seq = [int(np.argmax(V))]
        for b in reversed(bp): seq.append(int(b[seq[-1]]))
        seq.reverse(); return [labels[j] for j in seq]

    def pred_intent(toks):
        ws = set(t.lower() for t in toks); best = intents[0]; bs = -1e18
        for it in intents:
            sc = math.log((intent_tot[it] + K) / (sum(intent_tot.values()) + K * len(intents)))
            for w in ws: sc += math.log((intent_w[it][w] + K) / (intent_tot[it] + K * Vsz))
            if sc > bs: bs = sc; best = it
        return best

    # per-sentence tp/fp/fn + intent-hit (for bootstrap)
    stp = []; sfp = []; sfn = []; sih = []
    for toks, gold, intent in test:
        pred = viterbi(toks); gs = _spans(gold); ps = _spans(pred)
        stp.append(len(gs & ps)); sfp.append(len(ps - gs)); sfn.append(len(gs - ps))
        sih.append(int(pred_intent(toks) == intent))
    stp = np.array(stp); sfp = np.array(sfp); sfn = np.array(sfn); sih = np.array(sih)
    TP = int(stp.sum()); FP = int(sfp.sum()); FN = int(sfn.sum())
    prec = TP / (TP + FP + 1e-9); rec = TP / (TP + FN + 1e-9); f1 = 2 * prec * rec / (prec + rec + 1e-9)
    intent_acc = float(sih.mean()) if len(sih) else 0.0
    # bootstrap over sentences
    n = len(test); rng = np.random.default_rng(12345); f1s = np.empty(B_BOOT); ias = np.empty(B_BOOT)
    for b in range(B_BOOT):
        idx = rng.integers(0, n, size=n)
        tp = stp[idx].sum(); fp = sfp[idx].sum(); fn = sfn[idx].sum()
        p = tp / (tp + fp + 1e-9); r = tp / (tp + fn + 1e-9); f1s[b] = 2 * p * r / (p + r + 1e-9)
        ias[b] = sih[idx].mean()
    f1_lo, f1_hi = float(np.percentile(f1s, 2.5)), float(np.percentile(f1s, 97.5))
    f1_se = float(f1s.std(ddof=1)); ia_lo = float(np.percentile(ias, 2.5))
    print("  ATIS-SLOT-FILLING bootstrap (B=%d): slot-F1=%.4f [95%% CI %.4f-%.4f, SE=%.4f] | intent-acc=%.4f [lo %.4f] | %d labels, test=%d" % (
        B_BOOT, f1, f1_lo, f1_hi, f1_se, intent_acc, ia_lo, T, n), flush=True)
    return {"slot_f1": round(f1, 4), "slot_f1_lo": round(f1_lo, 4), "slot_f1_hi": round(f1_hi, 4), "slot_f1_se": round(f1_se, 4),
            "intent_acc": round(intent_acc, 4), "intent_acc_lo": round(ia_lo, 4), "slot_prec": round(prec, 3),
            "slot_rec": round(rec, 3), "n_boot": B_BOOT, "n_test": n}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    f1 = r["slot_f1"]; lo = r["slot_f1_lo"]; ia = r["intent_acc"]
    s = "slot-F1=%.4f [95%%CI %.4f-%.4f SE=%.4f] intent-acc=%.4f (P=%.3f R=%.3f, B=%d, test=%d)" % (
        f1, lo, r["slot_f1_hi"], r["slot_f1_se"], ia, r["slot_prec"], r["slot_rec"], r["n_boot"], r["n_test"])
    if lo >= 0.85 and ia >= 0.80:
        return ("HARD_PASS", "HARD_PASS: ATIS slot-filling bootstrap LOWER bound >=0.85 AND intent>=0.80 -- Tier-A (sampling-robust substrate frame-role binding). " + s)
    if f1 >= 0.65:
        return ("MIDDLE_BAND", "MIDDLE_BAND: slot-F1 point 0.65-0.85 or lower-CI<0.85 -- strong; firmed with bootstrap error bars but below sampling-robust 0.85 bar. " + s)
    return ("HARD_FAIL", "HARD_FAIL: slot-F1 <0.50. " + s)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
