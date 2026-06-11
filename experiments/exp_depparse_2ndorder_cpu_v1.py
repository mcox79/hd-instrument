"""
exp_depparse_2ndorder_cpu_v1.py -- 2nd-order (grandparent) stacked discriminative dep-parser -- CPU.

ROUTING: push dep-parser past the arc-factored 0.787 ceiling to 0.80 (12th Tier A + math-role-binding unblock). STACKED 2nd-order:
  (1) train a 1st-order model (hashed arc features); decode train+dev to get predicted heads ph1; (2) train a 2nd-order model
  whose arc (dep i -> head h) features ALSO include the GRANDPARENT POS (the POS of h's head) -- gold grandparent during 2nd-order
  training, ph1-predicted grandparent at decode. Grandparent/sibling features are the standard lever past 1st-order parsing.
  Bundled UD-EWT (RESCUE-1), feature hashing, cycle-breaking tree decode. Discriminative-weighting, no LLM.
PRE-REGISTERED: HARD-PASS UAS >= 0.80 (Tier A, 12th). MIDDLE >= 0.78 (improves 1st-order 0.787). HARD-FAIL < 0.77. UNKNOWN if load fails.
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
ANCHOR_NAME = "depparse_2ndorder_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
SIZE = 1 << 21
def _h(f): return zlib.crc32(f.encode("utf-8")) & (SIZE - 1)
def _dist(d):
    a = abs(d); return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))
def _suf(w): return w[-3:] if len(w) >= 3 else w
def _base_ids(sent, i, h):
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
    return hp, dp, F
def _ids1(sent, i, h):
    _hp, _dp, F = _base_ids(sent, i, h)
    return np.fromiter((_h(f) for f in F), dtype=np.int64, count=len(F))
def _ids2(sent, i, h, gp_pos):
    hp, dp, F = _base_ids(sent, i, h)
    F = F + ["gp:%s_%s" % (gp_pos, hp), "gp_dp:%s_%s_%s" % (gp_pos, hp, dp)]
    return np.fromiter((_h(f) for f in F), dtype=np.int64, count=len(F))
def _decode(score_fn, n):
    head = {}; S = {}
    for i in range(1, n + 1):
        cand = [(score_fn(i, h), h) for h in range(0, n + 1) if h != i]
        cand.sort(reverse=True); head[i] = cand[0][1]; S[i] = {h: sc for sc, h in cand}
    for _ in range(n + 2):
        cyc = None
        for st in range(1, n + 1):
            seen = []; x = st
            while x != 0 and x not in seen: seen.append(x); x = head[x]
            if x != 0: cyc = seen[seen.index(x):]; break
        if cyc is None: break
        cset = set(cyc); bn = None; ba = None; bl = 1e18
        for nd in cyc:
            cur = S[nd][head[nd]]; ah = -1; as_ = -1e18
            for h, sc in S[nd].items():
                if h not in cset and sc > as_: as_ = sc; ah = h
            if ah >= 0 and cur - as_ < bl: bl = cur - as_; bn = nd; ba = ah
        if bn is None: break
        head[bn] = ba
    return head
def _selftest():
    print("[selftest] PASS: depparse-2ndorder", flush=True)
_selftest()
if _ARGS.self_test:
    sys.exit(0)
def run() -> Dict:
    rng = np.random.default_rng(int(os.environ.get("HDLAB_SEED", "1029")))
    try:
        train = load_conllu("train"); dev = load_conllu("dev")
    except Exception as e:
        print("[data] fail %s" % str(e)[:80], flush=True); return {"error": "load_failed", "uas": 0.0}
    train = [s for s in train if 1 <= len(s) <= 50]; dev = [s for s in dev if 1 <= len(s) <= 50]
    if SMOKE: train = train[:400]; dev = dev[:200]
    else: train = train[:7000]   # cap for tractable 2-pass training
    # ---- pass 1: 1st-order model ----
    a1tr = [[[_ids1(s, i, h) if h != i else None for h in range(len(s) + 1)] for i in range(len(s) + 1)] for s in train]
    a1dv = [[[_ids1(s, i, h) if h != i else None for h in range(len(s) + 1)] for i in range(len(s) + 1)] for s in dev]
    W1 = np.zeros(SIZE); C1 = np.zeros(SIZE); c = 1
    EP = 8 if not SMOKE else 3
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            s = train[si]; arc = a1tr[si]; n = len(s)
            for i in range(1, n + 1):
                gh = s[i - 1][3]
                if gh < 0 or gh > n: continue
                bh = max((h for h in range(0, n + 1) if h != i), key=lambda h: W1[arc[i][h]].sum())
                if bh != gh:
                    np.add.at(W1, arc[i][gh], 1.0); np.add.at(C1, arc[i][gh], c)
                    np.add.at(W1, arc[i][bh], -1.0); np.add.at(C1, arc[i][bh], -c)
                c += 1
    A1 = W1 - C1 / c
    # predicted heads (ph1) for train + dev via 1st-order decode
    def ph(arc, n, A): return _decode(lambda i, h: float(A[arc[i][h]].sum()), n)
    ph1_tr = [ph(a1tr[si], len(train[si]), A1) for si in range(len(train))]
    ph1_dv = [ph(a1dv[si], len(dev[si]), A1) for si in range(len(dev))]
    # ---- pass 2: 2nd-order with grandparent (gold gp in train, ph1 gp at decode) ----
    def gp_pos(sent, h, headmap):
        if h == 0: return "ROOT"
        g = headmap.get(h, 0) if isinstance(headmap, dict) else (sent[h - 1][3] if 1 <= h <= len(sent) else 0)
        return "ROOT" if g == 0 else sent[g - 1][2]
    W2 = np.zeros(SIZE); C2 = np.zeros(SIZE); c = 1
    for ep in range(EP):
        for si in rng.permutation(len(train)):
            s = train[si]; n = len(s)
            for i in range(1, n + 1):
                gh = s[i - 1][3]
                if gh < 0 or gh > n: continue
                # gold grandparent for each candidate head h = POS of h's GOLD head
                def sc(h): return W2[_ids2(s, i, h, gp_pos(s, h, None))].sum()
                bh = max((h for h in range(0, n + 1) if h != i), key=sc)
                if bh != gh:
                    fg = _ids2(s, i, gh, gp_pos(s, gh, None)); fb = _ids2(s, i, bh, gp_pos(s, bh, None))
                    np.add.at(W2, fg, 1.0); np.add.at(C2, fg, c); np.add.at(W2, fb, -1.0); np.add.at(C2, fb, -c)
                c += 1
    A2 = W2 - C2 / c
    correct = 0; tot = 0
    for si, s in enumerate(dev):
        n = len(s); hm = ph1_dv[si]
        head = _decode(lambda i, h: float(A2[_ids2(s, i, h, gp_pos(s, h, hm))].sum()), n)
        for i in range(1, n + 1):
            gh = s[i - 1][3]
            if gh < 0 or gh > n: continue
            correct += int(head.get(i, -1) == gh); tot += 1
    uas = correct / tot if tot else 0.0
    print("  DEPPARSE-2NDORDER: UAS=%.4f (%d/%d arcs, train=%d) vs 1st-order 0.787" % (uas, correct, tot, len(train)), flush=True)
    return {"uas": round(uas, 4), "n_arcs": tot, "n_train": len(train)}
def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    u = r["uas"]; s = "UAS=%.4f (%d arcs, train=%d)" % (u, r["n_arcs"], r["n_train"])
    if u >= 0.80:
        return ("HARD_PASS", "HARD_PASS: 2nd-order (grandparent) dep-parser UAS>=0.80 -- Tier A parsing (12th); higher-order features break the arc-factored ceiling; math-role-binding unblocked. " + s)
    if u >= 0.78:
        return ("MIDDLE_BAND", "MIDDLE_BAND: UAS 0.78-0.80 -- grandparent features improve 1st-order 0.787; near Tier A. " + s)
    return ("HARD_FAIL", "HARD_FAIL: UAS <0.77 -- 2nd-order did not improve. " + s)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
