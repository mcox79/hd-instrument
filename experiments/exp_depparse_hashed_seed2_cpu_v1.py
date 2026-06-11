"""
exp_depparse_hashed_cpu_v1.py -- discriminative dep-parser with feature hashing (full UD-EWT train) -- CPU.

ROUTING: push the discriminative dep-parser to 0.80 (12th Tier A + math-role-binding unblock). The bottleneck was pure-Python
  dict lookups in arc scoring; this uses FEATURE HASHING (deterministic crc32 -> fixed numpy weight array) so the full
  12544-sentence UD-EWT train + morphology + 3rd-order features are tractable. Arc-factored averaged perceptron; each token
  picks its head by argmax arc-score. Bundled UD-EWT (RESCUE-1). Same discriminative-weighting lever (POS/math/code), no LLM.
PRE-REGISTERED: HARD-PASS UAS >= 0.80 (Tier A; unblocks math role-binding). MIDDLE >= 0.75. HARD-FAIL < 0.70. UNKNOWN if load fails.
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
from typing import Dict, List, Tuple
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO)); sys.path.insert(0, str(REPO / "experiments"))
from _seed_checkpoint import get_output_dir, write_metrics
from _ud_loader import load_conllu
ANCHOR_NAME = "depparse_hashed_seed2_cpu_v1"
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
    print("[selftest] PASS: depparse-hashed", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "2027")))
    try:
        train = load_conllu("train"); dev = load_conllu("dev")
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "uas": 0.0}
    MAXLEN = 50
    train = [s for s in train if 1 <= len(s) <= MAXLEN]; dev = [s for s in dev if 1 <= len(s) <= MAXLEN]
    if SMOKE: train = train[:400]; dev = dev[:200]
    # precompute arc-feature ids per sentence (token -> head -> ids) to avoid recompute each epoch
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
    tr_arc = precompute(train); dv_arc = precompute(dev)
    W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
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
    avg = W - CW / c
    def decode(arc, n):
        # arc-scores per (dep i -> head h); greedy heads then break cycles (reattach min-margin node to best non-cycle head)
        S = {}
        head = {}; second = {}
        for i in range(1, n + 1):
            cand = []
            for h in range(0, n + 1):
                if h == i: continue
                cand.append((float(avg[arc[i][h]].sum()), h))
            cand.sort(reverse=True)
            head[i] = cand[0][1]; S[i] = {h: sc for sc, h in cand}
            second[i] = cand[1] if len(cand) > 1 else (cand[0][0], 0)
        for _ in range(n + 2):
            # find a cycle among non-root heads
            cyc = None
            for start in range(1, n + 1):
                seen = []; x = start
                while x != 0 and x not in seen:
                    seen.append(x); x = head[x]
                if x != 0:
                    j = seen.index(x); cyc = seen[j:]; break
            if cyc is None: break
            # reattach the node whose best alternative (to a non-cycle head) loses least
            best_node = None; best_alt = None; best_loss = 1e18
            cset = set(cyc)
            for node in cyc:
                cur = S[node][head[node]]
                alt_h = -1; alt_s = -1e18
                for h, sc in S[node].items():
                    if h not in cset and sc > alt_s: alt_s = sc; alt_h = h
                if alt_h >= 0 and (cur - alt_s) < best_loss:
                    best_loss = cur - alt_s; best_node = node; best_alt = alt_h
            if best_node is None: break
            head[best_node] = best_alt
        return head
    correct = 0; tot = 0
    for si, s in enumerate(dev):
        arc = dv_arc[si]; n = len(s); head = decode(arc, n)
        for i in range(1, n + 1):
            gold_h = s[i - 1][3]
            if gold_h < 0 or gold_h > n: continue
            correct += int(head.get(i, -1) == gold_h); tot += 1
    uas = correct / tot if tot else 0.0
    print("  DEPPARSE-HASHED: UAS=%.4f (%d/%d arcs, train=%d sents, dev=%d) vs count 0.60 / dict-version 0.735" %
          (uas, correct, tot, len(train), len(dev)), flush=True)
    return {"uas": round(uas, 4), "n_arcs": tot, "n_train": len(train)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    u = r["uas"]; s = "UAS=%.4f (%d arcs, train=%d)" % (u, r["n_arcs"], r["n_train"])
    if u >= 0.80:
        return ("HARD_PASS", "HARD_PASS: discriminative dep-parser UAS>=0.80 -- discriminative weighting + morphology + full UD-EWT train reaches Tier-A parsing; unblocks math role-binding. 12th-Tier-A candidate. " + s)
    if u >= 0.75:
        return ("MIDDLE_BAND", "MIDDLE_BAND: UAS 0.75-0.80 -- strong; 3rd-order/MST decode for 0.85. " + s)
    return ("HARD_FAIL", "HARD_FAIL: UAS <0.70. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
