"""exp_arceager_parser_operator_v1 -- the improved in-substrate parser as a PERSISTED, loadable parse()
OPERATOR: arc-eager transition + dynamic oracle + Zhang & Nivre 2011 RICH NON-LOCAL STRUCTURAL FEATURES
(leftmost/rightmost dependents, valency, head-of-stack -- a structured working-memory buffer, brain-plausible
Now-or-Never-with-structure). This is the FINER-DRILL winner: the ~0.81 arc-eager ceiling survived richer SEARCH
(global-beam HARD_FAIL) and richer LEXICAL features (GloVe clusters +0.0015), but the STRUCTURAL rich features
CROSS it -- UD-EWT test UAS 0.8184 -> 0.8421 (+0.024); vs the LIVE arc-factored richfeat 0.775 that is +0.067.

Emits per-attachment CONFIDENCE (softmax over legal actions at the attaching step + raw margin) -> the
graded_competition distribution / N7. Arc-eager + rich-structural features COPIED/extended from the verified
transition lab (exp_depparse_transition_arceager + exp_arceager_richfeat_transition). save/load; parse_with_conf;
UAS on UD-EWT test. CPU numpy only, NO torch/spaCy/LLM. ASCII. --smoke = tiny train gate.
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, json, sys, time, zlib
from pathlib import Path
from datetime import datetime, timezone
import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = Path(_REPO)
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
from experiments._seed_checkpoint import get_output_dir
OUT_DIR = get_output_dir("exp_arceager_parser_operator_v1")
ASSET_DIR = os.path.join(_REPO, "data/frontend_assets_exp")
MODEL_PATH = os.path.join(ASSET_DIR, "arceager_dynamic_ud_ewt.npz")
UD_DIR = REPO / "experiments" / "data" / "ud_english_ewt"

SIZE = 1 << 21; MASK = SIZE - 1
SHIFT, LARC, RARC, REDU = 0, 1, 2, 3
ACT_SALT = np.array([0x9E3779B1, 0x85EBCA77, 0xC2B2AE3D, 0x27D4EB2F], dtype=np.int64)
MAXLEN = 50
EPOCHS = int(os.environ.get("HDLAB_EPOCHS", "10"))
EXPLORE_AFTER = 2; EXPLORE_P = 0.9
RICH = True  # rich non-local structural features (the finer-drill winner)


def _h(f): return zlib.crc32(f.encode("utf-8")) & MASK
def _dist(d):
    a = abs(d); return "1" if a == 1 else ("2" if a == 2 else ("3-5" if a <= 5 else ("6-10" if a <= 10 else "11+")))
def _suf(w): return w[-3:] if len(w) >= 3 else w
def _szbucket(k): return "1" if k <= 1 else ("2" if k == 2 else ("3" if k == 3 else ("4-6" if k <= 6 else "7+")))
def _val(k): return "0" if k == 0 else ("1" if k == 1 else ("2" if k == 2 else "3+"))
_ROOT = ("<root>", "ROOT", "<root>"); _NONE = ("<none>", "<NONE>", "<none>")


def _pos(attr, k):
    return attr[k][1] if (k is not None and 0 <= k < len(attr)) else "<n>"


def _mk_attr(sent):
    a = [_ROOT]
    for tok in sent:
        w = tok[1]; p = tok[2]; wl = w.lower(); a.append((wl, p, _suf(wl)))
    return a


def _config_feats(stack, bptr, n, attr, heads, lc, rc, hd):
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
    if RICH:
        s0lc = lc.get(s0, []); s0rc = rc.get(s0, []); b0lc = lc.get(b0, [])
        s0lcp = _pos(attr, s0lc[0]) if s0lc else "<nc>"
        s0rcp = _pos(attr, s0rc[-1]) if s0rc else "<nc>"
        b0lcp = _pos(attr, b0lc[0]) if b0lc else "<nc>"
        s0hp = _pos(attr, hd.get(s0)) if s0 in hd else "<nh>"
        s0lclc = _pos(attr, lc.get(s0lc[0], [None])[0]) if s0lc and lc.get(s0lc[0]) else "<nc>"
        F += ["s0lcp:" + s0lcp, "s0rcp:" + s0rcp, "b0lcp:" + b0lcp, "s0hp:" + s0hp,
              "s0p_s0lcp:%s_%s" % (s0p, s0lcp), "s0p_s0rcp:%s_%s" % (s0p, s0rcp), "b0p_b0lcp:%s_%s" % (b0p, b0lcp),
              "s0p_b0p_s0rcp:%s_%s_%s" % (s0p, b0p, s0rcp), "s0p_b0p_b0lcp:%s_%s_%s" % (s0p, b0p, b0lcp),
              "s0p_s0hp:%s_%s" % (s0p, s0hp), "s0lclcp:" + s0lclc,
              "s0vall:%s_%s" % (_val(len(s0lc)), s0p), "s0valr:%s_%s" % (_val(len(s0rc)), s0p), "b0vall:%s_%s" % (_val(len(b0lc)), b0p)]
    return F


def _legal(stack, bptr, n, heads):
    moves = []; s0 = stack[-1]; buf = bptr <= n
    if buf: moves.append(SHIFT)
    if buf and s0 != 0 and s0 not in heads: moves.append(LARC)
    if buf: moves.append(RARC)
    if s0 != 0 and s0 in heads: moves.append(REDU)
    return moves


def _apply(stack, bptr, heads, lc, rc, hd, a):
    if a == SHIFT:
        stack.append(bptr); bptr += 1
    elif a == LARC:
        s0 = stack[-1]; heads[s0] = bptr; hd[s0] = bptr
        lc[bptr] = [s0] + lc.get(bptr, [])
        stack.pop()
    elif a == RARC:
        s0 = stack[-1]; heads[bptr] = s0; hd[bptr] = s0
        rc.setdefault(s0, []).append(bptr)
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


def _score_actions(base_ids, W, legal):
    return {a: float(W[(base_ids ^ ACT_SALT[a]) & MASK].sum()) for a in legal}


def _argmax_legal(scores):
    best_a = None; best = -1e18
    for a, s in scores.items():
        if s > best: best = s; best_a = a
    return best_a


def _perc_update(W, CW, base_ids, ag, ap, c):
    ig = (base_ids ^ ACT_SALT[ag]) & MASK; ip = (base_ids ^ ACT_SALT[ap]) & MASK
    np.add.at(W, ig, 1.0); np.add.at(CW, ig, c); np.add.at(W, ip, -1.0); np.add.at(CW, ip, -c)


def _train_transition(train, seed, dynamic=True):
    rng = np.random.default_rng(seed); W = np.zeros(SIZE); CW = np.zeros(SIZE); c = 1
    for ep in range(EPOCHS):
        explore = dynamic and ep >= EXPLORE_AFTER; te = time.time()
        for si in rng.permutation(len(train)):
            s = train[si]; n = len(s); attr = _mk_attr(s)
            gold = [0] * (n + 1)
            for tok in s: gold[tok[0]] = tok[3] if 0 <= tok[3] <= n else 0
            stack = [0]; bptr = 1; heads = {}; lc = {}; rc = {}; hd = {}; guard = 0
            while bptr <= n or len(stack) > 1:
                if bptr > n and len(stack) <= 1: break
                legal = _legal(stack, bptr, n, heads)
                if not legal: break
                base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, lc, rc, hd)), dtype=np.int64)
                scores = _score_actions(base_ids, W, legal); a_pred = _argmax_legal(scores)
                costs = _move_costs_live(stack, bptr, n, gold, heads)
                zero = [a for a in legal if costs.get(a, 1) == 0] or [min(costs, key=lambda k: costs[k])]
                a_orl = max(zero, key=lambda a: scores.get(a, -1e18))
                if a_pred != a_orl and costs.get(a_pred, 1) > 0:
                    _perc_update(W, CW, base_ids, a_orl, a_pred, c); c += 1
                a_next = a_pred if (explore and a_pred in legal and rng.random() < EXPLORE_P) else a_orl
                stack, bptr = _apply(stack, bptr, heads, lc, rc, hd, a_next); guard += 1
                if guard > 4 * (n + 2): break
        print("  [train] epoch %d/%d %.1fs (updates=%d)" % (ep + 1, EPOCHS, time.time() - te, c - 1), flush=True)
    return W - CW / c


def parse_with_conf(sent_tokens, pos_tags, W):
    """(heads, attach_conf, attach_margin). attach_conf[i]=softmax prob of the action that attached token i;
    attach_margin[i]=raw best-second action score. Unattached -> (0.0, 0.0)."""
    n = len(sent_tokens)
    sent = [(k + 1, sent_tokens[k], pos_tags[k], 0, "_", None) for k in range(n)]
    attr = _mk_attr(sent)
    stack = [0]; bptr = 1; heads = {}; lc = {}; rc = {}; hd = {}; conf = {}; marg = {}
    guard = 0
    while bptr <= n or len(stack) > 1:
        if bptr > n and len(stack) <= 1: break
        legal = _legal(stack, bptr, n, heads)
        if not legal: break
        base_ids = np.fromiter((_h(f) for f in _config_feats(stack, bptr, n, attr, heads, lc, rc, hd)), dtype=np.int64)
        scores = _score_actions(base_ids, W, legal); a = _argmax_legal(scores)
        sv = np.array([scores[x] for x in legal], dtype=np.float64)
        so = np.sort(sv)[::-1]; m = float(so[0] - so[1]) if len(so) > 1 else float(so[0])
        e = np.exp(sv - sv.max()); pa = float((e / e.sum())[legal.index(a)])
        s0 = stack[-1]
        if a == LARC: conf[s0] = pa; marg[s0] = m
        elif a == RARC: conf[bptr] = pa; marg[bptr] = m
        stack, bptr = _apply(stack, bptr, heads, lc, rc, hd, a); guard += 1
        if guard > 4 * (n + 2): break
    for i in range(1, n + 1):
        heads.setdefault(i, 0); conf.setdefault(i, 0.0); marg.setdefault(i, 0.0)
    return heads, conf, marg


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


def save_model(W, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp.npz"
    np.savez_compressed(tmp, avg=W.astype(np.float32)); os.replace(tmp, path)


def load_model(path):
    with np.load(path) as z:
        return z["avg"].astype(np.float64)


def uas_on(sents, W, tagger=None):
    hit = tot = 0
    for s in sents:
        toks = [t[1] for t in s]
        pos = [t[2] for t in s] if tagger is None else tagger.tag(toks)
        heads, _, _ = parse_with_conf(toks, pos, W)
        for tok in s:
            i, h = tok[0], tok[3]
            if h < 0 or h > len(s): continue
            hit += int(heads.get(i, -1) == h); tot += 1
    return hit / tot if tot else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true"); ap.add_argument("--epochs", type=int, default=None)
    ap.add_argument("--seed", type=int, default=1); ap.add_argument("--retrain", action="store_true")
    args = ap.parse_args()
    global EPOCHS
    if args.epochs is not None: EPOCHS = args.epochs
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    train = [s for s in _load_ud_feats("train") if 1 <= len(s) <= MAXLEN]
    dev = [s for s in _load_ud_feats("dev") if 1 <= len(s) <= MAXLEN]
    test = [s for s in _load_ud_feats("test") if 1 <= len(s) <= MAXLEN]
    if args.smoke:
        EPOCHS = min(EPOCHS, 3); train = train[:400]; dev = dev[:150]; test = test[:150]
    print("[data] train=%d dev=%d test=%d EPOCHS=%d RICH=%s" % (len(train), len(dev), len(test), EPOCHS, RICH), flush=True)

    if os.path.exists(MODEL_PATH) and not args.retrain and not args.smoke:
        print("[train] loading existing %s" % MODEL_PATH, flush=True); W = load_model(MODEL_PATH)
    else:
        tt = time.time(); W = _train_transition(train, args.seed, dynamic=True)
        print("[train] arc-eager rich-struct trained %.1fs" % (time.time() - tt), flush=True)
        if not args.smoke:
            save_model(W, MODEL_PATH); print("[train] saved -> %s" % MODEL_PATH, flush=True)

    uas_gold = round(uas_on(test, W), 4); print("[uas] arc-eager rich test gold-POS=%.4f" % uas_gold, flush=True)
    uas_pred = None
    try:
        from hdlab.pos_tagger import PosTagger
        tg = PosTagger.load(os.path.join(_REPO, "data", "frontend_assets", "pos_tagger_ud_ewt_upos.json"))
        uas_pred = round(uas_on(test, W, tagger=tg), 4); print("[uas] arc-eager rich test pred-POS=%.4f" % uas_pred, flush=True)
    except Exception as e:
        print("[uas] pred-POS skip: %s" % str(e)[:80], flush=True)
    ref = {}
    try:
        from hdlab.arc_parser import ArcParser
        FE = os.path.join(_REPO, "data", "frontend_assets")
        for nm, fn in (("richfeat", "arc_parser_richfeat_ud_ewt.npz"), ("hashed", "arc_parser_hashed_ud_ewt.npz")):
            pr = ArcParser.load(os.path.join(FE, fn))
            u, _, _ = pr.eval_uas([[(t[0], t[1], t[2], t[3], t[4]) for t in s] for s in test])
            ref[nm] = round(u, 4)
        print("[uas] arc-factored refs gold-POS: %s" % ref, flush=True)
    except Exception as e:
        print("[uas] ref skip: %s" % str(e)[:80], flush=True)

    conf_sample = []
    for s in dev[:300]:
        toks = [t[1] for t in s]; pos = [t[2] for t in s]
        _, cf, _mg = parse_with_conf(toks, pos, W); conf_sample.extend(cf.values())
    conf_mean = round(float(np.mean(conf_sample)), 4) if conf_sample else 0.0

    res = {"uas_test_goldpos": uas_gold, "uas_test_predpos": uas_pred, "arcfactored_refs_goldpos": ref,
           "uas_gain_goldpos_vs_richfeat": round(uas_gold - ref.get("richfeat", 0.0), 4) if ref else None,
           "attach_conf_mean": conf_mean, "n_train": len(train), "n_test": len(test),
           "epochs": EPOCHS, "rich_features": RICH, "model_path": MODEL_PATH if not args.smoke else None}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "arceager_parser_operator_v1", "results": res,
                   "elapsed_s": round(time.time() - t0, 1), "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    print("\n[SUMMARY] arc-eager RICH UAS gold=%.4f pred=%s vs richfeat %s gain=%s conf_mean=%.3f [%.0fs]" % (
        uas_gold, uas_pred, ref.get("richfeat"), res["uas_gain_goldpos_vs_richfeat"], conf_mean, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
