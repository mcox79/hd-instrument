"""
exp_depparse_hashed_multiseed_cpu_v1.py -- discriminative dep-parser (feature hashing), MULTI-SEED firming -- CPU.

ROUTING: Research Direction 1 (multi-seed firming). Single-seed UAS 0.7868/0.7872 (seed1/seed2). Run n=5 seeds, report mean +/- SE.
  Arc-feature precompute is SEED-INDEPENDENT -> computed ONCE and reused across seeds (only the averaged-perceptron training rng
  varies per seed). Same hashing + features + 10-epoch averaged perceptron + greedy-decode-with-cycle-break as depparse_hashed_cpu_v1.
  Bundled UD-EWT (RESCUE). Substrate-only.
PRE-REGISTERED (firming; NO defeat): report UAS mean +/- SE over n=5. HARD-PASS mean-2SE >= 0.80 (Tier-A). MIDDLE mean 0.75-0.80
  (firmed MIDDLE; below 0.80 promotion bar). HARD-FAIL mean < 0.75. UNKNOWN if load fails.
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, zlib
from pathlib import Path
from typing import Dict, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu
ANCHOR_NAME = "depparse_hashed_multiseed_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIZE = 1 << 21


def _h(f): return zlib.crc32(f.encode("utf-8")) & (SIZE - 1)
def _dist(d):
    a = abs(d); return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))
def _suf(w): return w[-3:] if len(w) >= 3 else w


def _arc_ids(sent, i, h):
    n = len(sent); dw, dp = sent[i - 1][1].lower(), sent[i - 1][2]
    if h == 0: hw, hp = "<ROOT>", "ROOT"; d = 0; dr = "R"
    else: hw, hp = sent[h - 1][1].lower(), sent[h - 1][2]; d = h - i; dr = "L" if d < 0 else "R"
    db = _dist(d)
    F = ["b", "hp:" + hp, "dp:" + dp, "hp_dp:%s_%s" % (hp, dp), "hp_dp_dir:%s_%s_%s" % (hp, dp, dr),
         "hp_dp_dist:%s_%s_%s" % (hp, dp, db), "dw:" + dw, "hw:" + hw, "hw_dw:%s_%s" % (hw, dw),
         "hp_dw:%s_%s" % (hp, dw), "hw_dp:%s_%s" % (hw, dp), "dp_dir:%s_%s" % (dp, dr), "dp_dist:%s_%s" % (dp, db),
         "dsuf_hp:%s_%s" % (_suf(dw), hp), "hsuf_dp:%s_%s" % (_suf(hw), dp), "dsuf_dp_dir:%s_%s_%s" % (_suf(dw), dp, dr)]
    hp_l = sent[h - 2][2] if h >= 2 else "<S>"; dp_l = sent[i - 2][2] if i >= 2 else "<S>"
    dp_r = sent[i][2] if i < n else "<E>"; hp_r = sent[h][2] if 0 < h < n else "<E>"
    F += ["hpl_hp_dp:%s_%s_%s" % (hp_l, hp, dp), "dpl_dp_dir:%s_%s_%s" % (dp_l, dp, dr), "dpr_dp:%s_%s" % (dp_r, dp),
          "hpr_hp_dp:%s_%s_%s" % (hp_r, hp, dp)]
    if h != 0:
        lo, hi = min(i, h), max(i, h); between = [sent[k - 1][2] for k in range(lo + 1, hi)]
        if "VERB" in between: F.append("bV:%s_%s" % (hp, dp))
        if "PUNCT" in between: F.append("bP:%s_%s" % (hp, dp))
        F.append("dp_bn:%s_%s" % (dp, _dist(len(between))))
    return np.fromiter((_h(f) for f in F), dtype=np.int64, count=len(F))


def _selftest():
    assert _h("abc") == _h("abc")
    print("[selftest] PASS: depparse-hashed-multiseed", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _decode(arc, n, avg):
    S = {}; head = {}
    for i in range(1, n + 1):
        cand = []
        for h in range(0, n + 1):
            if h == i: continue
            cand.append((float(avg[arc[i][h]].sum()), h))
        cand.sort(reverse=True)
        head[i] = cand[0][1]; S[i] = {h: sc for sc, h in cand}
    for _ in range(n + 2):
        cyc = None
        for start in range(1, n + 1):
            seen = []; x = start
            while x != 0 and x not in seen:
                seen.append(x); x = head[x]
            if x != 0:
                j = seen.index(x); cyc = seen[j:]; break
        if cyc is None: break
        best_node = None; best_alt = None; best_loss = 1e18; cset = set(cyc)
        for node in cyc:
            cur = S[node][head[node]]; alt_h = -1; alt_s = -1e18
            for h, sc in S[node].items():
                if h not in cset and sc > alt_s: alt_s = sc; alt_h = h
            if alt_h >= 0 and (cur - alt_s) < best_loss:
                best_loss = cur - alt_s; best_node = node; best_alt = alt_h
        if best_node is None: break
        head[best_node] = best_alt
    return head


def _train_one_seed(train, tr_arc, seed):
    rng = np.random.default_rng(seed); W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    EP = 10 if not SMOKE else 3
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            s = train[si]; arc = tr_arc[si]; n = len(s)
            for i in range(1, n + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > n: continue
                best_h = -1; best_s = -1e18
                for h in range(0, n + 1):
                    if h == i: continue
                    sc = W[arc[i][h]].sum()
                    if sc > best_s: best_s = sc; best_h = h
                if best_h != gold_h:
                    gi = arc[i][gold_h]; pi = arc[i][best_h]
                    np.add.at(W, gi, 1.0); np.add.at(CW, gi, c)
                    np.add.at(W, pi, -1.0); np.add.at(CW, pi, -c)
                c += 1
    return W - CW / c


def run() -> Dict:
    try:
        train = load_conllu("train"); dev = load_conllu("dev")
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "uas": 0.0}
    MAXLEN = 50
    train = [s for s in train if 1 <= len(s) <= MAXLEN]; dev = [s for s in dev if 1 <= len(s) <= MAXLEN]
    if SMOKE: train = train[:300]; dev = dev[:150]

    def precompute(sents):
        out = []
        for s in sents:
            n = len(s); arc = [[None] * (n + 1) for _ in range(n + 1)]
            for i in range(1, n + 1):
                for h in range(0, n + 1):
                    if h == i: continue
                    arc[i][h] = _arc_ids(s, i, h)
            out.append(arc)
        return out
    t_pc = time.time(); tr_arc = precompute(train); dv_arc = precompute(dev)
    print("[precompute] arc features done %.1fs (train=%d dev=%d) -- shared across seeds" % (time.time() - t_pc, len(train), len(dev)), flush=True)
    SEEDS = [1, 2, 3] if SMOKE else [1, 2, 3, 4, 5]
    vals = []
    for sd in SEEDS:
        avg = _train_one_seed(train, tr_arc, sd)
        correct = tot = 0
        for si, s in enumerate(dev):
            head = _decode(dv_arc[si], len(s), avg)
            for i in range(1, len(s) + 1):
                gold_h = s[i - 1][3]
                if gold_h < 0 or gold_h > len(s): continue
                correct += int(head.get(i, -1) == gold_h); tot += 1
        uas = correct / tot if tot else 0.0; vals.append(round(uas, 4))
        print("  seed %d: UAS=%.4f" % (sd, uas), flush=True)
    mean = sum(vals) / len(vals); std = (sum((v - mean) ** 2 for v in vals) / len(vals)) ** 0.5
    se = std / (len(vals) ** 0.5)
    print("  DEPPARSE-HASHED MULTISEED n=%d: mean-UAS=%.4f std=%.4f SE=%.4f (mean-2SE=%.4f) vals=%s" % (
        len(vals), mean, std, se, mean - 2 * se, vals), flush=True)
    return {"uas": round(mean, 4), "accuracy": round(mean, 4), "std": round(std, 4), "se": round(se, 4),
            "mean_minus_2se": round(mean - 2 * se, 4), "vals": vals, "n_seeds": len(vals), "n_train": len(train)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    m = r["uas"]; m2 = r["mean_minus_2se"]
    s = "mean-UAS=%.4f std=%.4f SE=%.4f mean-2SE=%.4f (n=%d, vals=%s, train=%d)" % (m, r["std"], r["se"], m2, r["n_seeds"], r["vals"], r["n_train"])
    if m2 >= 0.80:
        return ("HARD_PASS", "HARD_PASS: dep-parser multiseed mean-2SE>=0.80 -- PROMOTE Tier-A. " + s)
    if m >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: dep-parser UAS firmed multi-seed at 0.75-0.80 (stable MIDDLE; below 0.80 promotion bar). " + s)
    return ("HARD_FAIL", "HARD_FAIL: dep-parser mean-UAS <0.75. " + s)


print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": r.get("n_seeds", 1), "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
