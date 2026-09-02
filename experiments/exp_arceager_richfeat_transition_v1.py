"""exp_arceager_richfeat_transition_v1 -- the FINER wall drill. The 0.81 arc-eager UAS ceiling survived richer
SEARCH (global-beam, HARD_FAIL) and richer LEXICAL features (GloVe clusters, +0.0015). The one remaining
high-yield, glass-box, brain-plausible lever is richer STRUCTURAL context: Zhang & Nivre 2011 rich non-local
features -- the leftmost/rightmost already-attached DEPENDENTS of the stack-top and buffer-front, their POS,
the head of the stack-top, and VALENCY counts. These are the features that historically took glass-box
transition parsers from ~0.90 to ~0.925 (WSJ). Brain-plausible: a structured working-memory buffer (Now-or-
Never with structure, not just a token window). ONE variable = +rich structural features; retrain arc-eager,
remeasure UAS on UD-EWT test vs the base (0.8184 gold-POS). A gain CROSSES the wall; a null completes the
three-lever characterization (search/lexical/structural all refuted -> a genuine architecture gap).

CPU numpy only. NO torch/spaCy/LLM. ASCII. --smoke = tiny. own dir.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time, zlib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UD_DIR = Path(_REPO) / "experiments" / "data" / "ud_english_ewt"
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_arceager_richfeat_transition_v1")
SIZE = 1 << 21; MASK = SIZE - 1
SHIFT, LARC, RARC, REDU = 0, 1, 2, 3
ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)
MAXLEN = 50
EPOCHS = int(os.environ.get("HDLAB_EPOCHS", "10"))
EXPLORE_AFTER = 2; EXPLORE_P = 0.9


def _h(f): return zlib.crc32(f.encode("utf-8")) & MASK
def _dist(d):
    a = abs(d); return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))
def _suf(w): return w[-3:] if len(w) >= 3 else w
def _szbucket(k): return "1" if k <= 1 else ("2" if k == 2 else ("3" if k == 3 else ("4-6" if k <= 6 else "7+")))
def _val(k): return "0" if k == 0 else ("1" if k == 1 else ("2" if k == 2 else "3+"))
_ROOT = ("<root>", "ROOT", "<root>"); _NONE = ("<none>", "<NONE>", "<none>")


def _num_of(feats):
    for kv in feats.split("|"):
        if kv.startswith("Number="):
            v = kv.split("=", 1)[1]; return v if v in ("Sing", "Plur") else None
    return None


def _load_ud_feats(split):
    fp = UD_DIR / ("en_ewt-ud-%s.conllu" % split); sents = []; cur = []
    with open(fp, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if cur: sents.append(cur); cur = []
                continue
            if line.startswith("#"): continue
            c = line.split("\t")
            if len(c) < 8 or "-" in c[0] or "." in c[0]: continue
            try: idx = int(c[0]); head = int(c[6])
            except Exception: continue
            cur.append((idx, c[1], c[3], head, c[7], _num_of(c[5])))
    if cur: sents.append(cur)
    return sents


def _mk_attr(sent):
    a = [_ROOT]
    for (i, w, p, h, dl, num) in sent:
        wl = w.lower(); a.append((wl, p, _suf(wl)))
    return a


def _pos(attr, k):
    return attr[k][1] if (k is not None and 0 <= k < len(attr)) else "<n>"


def _word(attr, k):
    return attr[k][0] if (k is not None and 0 <= k < len(attr)) else "<n>"


def _config_feats(stack, bptr, n, attr, heads, lc, rc, hd, rich):
    s0 = stack[-1]; s1 = stack[-2] if len(stack) >= 2 else None
    b0 = bptr if bptr <= n else None; b1 = (bptr + 1) if (bptr + 1) <= n else None; b2 = (bptr + 2) if (bptr + 2) <= n else None
    s0w, s0p, s0s = attr[s0]
    s1w, s1p, s1s = attr[s1] if s1 is not None else _NONE
    b0w, b0p, b0s = attr[b0] if b0 is not None else _NONE
    b1w, b1p, b1s = attr[b1] if b1 is not None else _NONE
    b2w, b2p, b2s = attr[b2] if b2 is not None else _NONE
    dd = _dist(b0 - s0) if (b0 is not None and s0 > 0) else "0"
    s0hh = "1" if s0 in heads else "0"
    F = ["bias", "s0p:" + s0p, "s0w:" + s0w, "s1p:" + s1p, "b0p:" + b0p, "b0w:" + b0w, "b1p:" + b1p, "b2p:" + b2p,
         "s0p_b0p:%s_%s" % (s0p, b0p), "s0w_b0w:%s_%s" % (s0w, b0w), "s0p_b0w:%s_%s" % (s0p, b0w), "s0w_b0p:%s_%s" % (s0w, b0p),
         "s0p_b0p_b1p:%s_%s_%s" % (s0p, b0p, b1p), "s1p_s0p_b0p:%s_%s_%s" % (s1p, s0p, b0p),
         "s0s:" + s0s, "b0s:" + b0s, "s0s_b0p:%s_%s" % (s0s, b0p), "b0s_s0p:%s_%s" % (b0s, s0p),
         "dist:%s_%s_%s" % (dd, s0p, b0p), "s0hh_p:%s_%s" % (s0hh, s0p), "s0hh_b0p:%s_%s" % (s0hh, b0p),
         "stksz:" + _szbucket(len(stack))]
    if rich:
        # leftmost/rightmost dependents of s0 and b0 (already-attached children), head of s0, valency
        s0lc = lc.get(s0, []); s0rc = rc.get(s0, []); b0lc = lc.get(b0, [])
        s0lcp = _pos(attr, s0lc[0]) if s0lc else "<nc>"
        s0rcp = _pos(attr, s0rc[-1]) if s0rc else "<nc>"
        b0lcp = _pos(attr, b0lc[0]) if b0lc else "<nc>"
        s0hp = _pos(attr, hd.get(s0)) if s0 in hd else "<nh>"
        # grandchild (2nd order): leftmost-child-of-leftmost-child of s0
        s0lclc = _pos(attr, lc.get(s0lc[0], [None])[0]) if s0lc and lc.get(s0lc[0]) else "<nc>"
        F += [
            "s0lcp:" + s0lcp, "s0rcp:" + s0rcp, "b0lcp:" + b0lcp, "s0hp:" + s0hp,
            "s0p_s0lcp:%s_%s" % (s0p, s0lcp), "s0p_s0rcp:%s_%s" % (s0p, s0rcp), "b0p_b0lcp:%s_%s" % (b0p, b0lcp),
            "s0p_b0p_s0rcp:%s_%s_%s" % (s0p, b0p, s0rcp), "s0p_b0p_b0lcp:%s_%s_%s" % (s0p, b0p, b0lcp),
            "s0p_s0hp:%s_%s" % (s0p, s0hp), "s0lclcp:" + s0lclc,
            "s0vall:%s_%s" % (_val(len(s0lc)), s0p), "s0valr:%s_%s" % (_val(len(s0rc)), s0p), "b0vall:%s_%s" % (_val(len(b0lc)), b0p),
        ]
    return F


def _legal(stack, bptr, n, heads):
    moves = []; s0 = stack[-1]; buf = bptr <= n
    if buf: moves.append(SHIFT)
    if buf and s0 != 0 and s0 not in heads: moves.append(LARC)
    if buf: moves.append(RARC)
    if s0 != 0 and s0 in heads: moves.append(REDU)
    return moves


def _apply(stack, bptr, heads, lc, rc, hd, a):
    """apply action, maintaining children (lc/rc) and head (hd) maps for rich features."""
    if a == SHIFT:
        stack.append(bptr); bptr += 1
    elif a == LARC:
        s0 = stack[-1]; heads[s0] = bptr; hd[s0] = bptr
        lc.setdefault(bptr, []); lc[bptr] = [s0] + lc[bptr]  # s0 is a LEFT child of b0 (leftmost so far)
        stack.pop()
    elif a == RARC:
        s0 = stack[-1]; heads[bptr] = s0; hd[bptr] = s0
        rc.setdefault(s0, []).append(bptr)                  # b0 is a RIGHT child of s0 (rightmost)
        stack.append(bptr); bptr += 1
    elif a == REDU:
        stack.pop()
    return stack, bptr


def _move_costs_live(stack, bptr, n, gold, heads):
    costs = {}; s0 = stack[-1]; b0 = bptr if bptr <= n else None; ss = set(stack)
    for a in _legal(stack, bptr, n, heads):
        if a == SHIFT:
            c = sum(1 for k in stack if gold[k] == b0)
            if 0 <= gold[b0] and gold[b0] in ss: c += 1
            costs[a] = c
        elif a == LARC:
            c = 0; gh = gold[s0]
            if gh != b0 and (bptr + 1) <= gh <= n: c += 1
            c += sum(1 for k in range(bptr, n + 1) if gold[k] == s0); costs[a] = c
        elif a == RARC:
            c = 0; gh = gold[b0]
            if gh != s0 and (gh in ss or (bptr + 1) <= gh <= n): c += 1
            c += sum(1 for k in stack if gold[k] == b0); costs[a] = c
        elif a == REDU:
            costs[a] = sum(1 for k in range(bptr, n + 1) if gold[k] == s0)
    return costs


def _score(base_ids, W, legal):
    return {a: float(W[(base_ids ^ ACT_SALT[a]) & MASK].sum()) for a in legal}


def _amax(scores):
    ba = None; b = -1e18
    for a, s in scores.items():
        if s > b: b = s; ba = a
    return ba


def _upd(W, CW, base_ids, ag, ap, c):
    ig = (base_ids ^ ACT_SALT[ag]) & MASK; ip = (base_ids ^ ACT_SALT[ap]) & MASK
    np.add.at(W, ig, 1.0); np.add.at(CW, ig, c); np.add.at(W, ip, -1.0); np.add.at(CW, ip, -c)


def _train(train, seed, rich):
    rng = np.random.default_rng(seed); W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    for ep in range(EPOCHS):
        explore = ep >= EXPLORE_AFTER; te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]; n = len(s); attr = _mk_attr(s)
            gold = [0] * (n + 1)
            for (i, w, p, h, dl, num) in s: gold[i] = h if 0 <= h <= n else 0
            stack = [0]; bptr = 1; heads = {}; lc = {}; rc = {}; hd = {}; guard = 0
            while bptr <= n or len(stack) > 1:
                if bptr > n and len(stack) <= 1: break
                legal = _legal(stack, bptr, n, heads)
                if not legal: break
                base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, lc, rc, hd, rich)), dtype=np.int64)
                scores = _score(base_ids, W, legal); ap = _amax(scores)
                costs = _move_costs_live(stack, bptr, n, gold, heads)
                zero = [a for a in legal if costs.get(a, 1) == 0] or [min(costs, key=lambda k: costs[k])]
                aorl = max(zero, key=lambda a: scores.get(a, -1e18))
                if ap != aorl and costs.get(ap, 1) > 0: _upd(W, CW, base_ids, aorl, ap, c); c += 1
                anext = ap if (explore and ap in legal and rng.random() < EXPLORE_P) else aorl
                stack, bptr = _apply(stack, bptr, heads, lc, rc, hd, anext); guard += 1
                if guard > 4 * (n + 2): break
        print("  [train rich=%s] epoch %d/%d %.1fs" % (rich, ep + 1, EPOCHS, time.time() - te), flush=True)
    return W - CW / c


def _decode(sent, W, rich):
    n = len(sent); attr = _mk_attr(sent); stack = [0]; bptr = 1; heads = {}; lc = {}; rc = {}; hd = {}; guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1: break
        legal = _legal(stack, bptr, n, heads)
        if not legal: break
        base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, lc, rc, hd, rich)), dtype=np.int64)
        a = _amax(_score(base_ids, W, legal)); stack, bptr = _apply(stack, bptr, heads, lc, rc, hd, a); guard += 1
        if guard > 4 * (n + 2): break
    for i in range(1, n + 1): heads.setdefault(i, 0)
    return heads


def uas(sents, W, rich):
    hit = tot = 0
    for s in sents:
        heads = _decode(s, W, rich)
        for (i, w, p, h, d, num) in s:
            if h < 0 or h > len(s): continue
            hit += int(heads.get(i, -1) == h); tot += 1
    return hit / tot if tot else 0.0


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--smoke", action="store_true"); ap.add_argument("--epochs", type=int, default=None)
    ap.add_argument("--seed", type=int, default=1)
    args = ap.parse_args()
    global EPOCHS
    if args.epochs is not None: EPOCHS = args.epochs
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    train = [s for s in _load_ud_feats("train") if 1 <= len(s) <= MAXLEN]
    test = [s for s in _load_ud_feats("test") if 1 <= len(s) <= MAXLEN]
    if args.smoke:
        EPOCHS = min(EPOCHS, 3); train = train[:400]; test = test[:150]
    print("[data] train=%d test=%d EPOCHS=%d seed=%d" % (len(train), len(test), EPOCHS, args.seed), flush=True)
    res = {"seed": args.seed}
    for rich in (False, True):
        tt = time.time(); W = _train(train, args.seed, rich); u = round(uas(test, W, rich), 4)
        res["rich" if rich else "base"] = u
        print("[uas] seed=%d rich=%s test gold-POS UAS=%.4f (%.0fs)" % (args.seed, rich, u, time.time() - tt), flush=True)
    res["rich_gain"] = round(res["rich"] - res["base"], 4); res["base_arceager_cited"] = 0.8184
    # append to a multi-seed log so the control accumulates across seeds without overwriting
    logp = os.path.join(OUT_DIR, "seed_runs.jsonl")
    with open(logp, "a", encoding="ascii") as fh:
        fh.write(json.dumps({"seed": args.seed, "base": res["base"], "rich": res["rich"], "gain": res["rich_gain"]}) + "\n")
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "arceager_richfeat_transition_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[SUMMARY] seed=%d base=%.4f +richstruct=%.4f gain=%+.4f (base cited 0.8184) [%.0fs]" % (
        args.seed, res["base"], res["rich"], res["rich_gain"], time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
