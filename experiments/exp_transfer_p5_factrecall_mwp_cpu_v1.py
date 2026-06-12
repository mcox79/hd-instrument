"""
exp_transfer_p5_factrecall_mwp_cpu_v1.py -- E5 / Transfer-P5: PP-225 FHRR fact-recall -> KB-fact-from-MWP-text -- CPU.

ROUTING: Research APPROVED (research_to_exp_dev_NER_NORTH_STAR_WIN_E5_E1_PRIORITY) -- E5 framework DISCRIMINATOR. Drill 2 P5
  predicts HARD-FAIL (P_deflated transfer = 0.012; C1 homology 0.20 -- FHRR unbind != text sequence labeling; structural mismatch).
  TEST: can the PP-225 recall mechanism [value = cleanup(unbind(memory, bind(subject,relation)))] EXTRACT (entity,object,value) facts
  from MWP-style text WITHOUT a parser? The mechanism has no text-structure model; a text-derived FHRR memory lacks the clean
  subject(x)relation(x)value triple structure recall needs -> predicted to fail vs a heuristic regex baseline.
DESIGN (fair, not strawman): genuine FHRR -- unit phasors dim=1024, bind=complex mult, unbind=mult by conjugate, bundle=sum+phase-norm,
  cleanup=nearest by cosine over a NUMBER codebook. Memory = bundle over content-word pairs (w_a x w_b) (unsupervised relational
  binding; no gold roles -- the honest no-parser condition). Recall: for each (entity,object) present, value=cleanup(unbind(memory,
  bind(entity,object))). Baseline = regex heuristic (number -> nearest object-noun + nearest name). Span-style fact-F1 on both.
PRE-REGISTERED (Drill 2): HARD-PASS extraction-F1 >= 0.50. MIDDLE 0.30-0.50. HARD-FAIL < 0.30 (framework validated -- structural mismatch
  dominates; substrate < regex). UNKNOWN if build fails. (A surprise PASS would REFUTE the framework -- report as discovery.)
ASCII-only. write_metrics. PROT-018 _v1.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "transfer_p5_factrecall_mwp_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
DIM = 256 if SMOKE else 1024

NAMES = ["Tom", "Mary", "Sara", "John", "Lucy", "Ben", "Anna", "Mike", "Kate", "Sam", "Emma", "Jack"]
OBJECTS = ["apples", "books", "pens", "marbles", "coins", "cards", "candies", "stamps", "balls", "flowers", "cookies", "stickers"]
NUMWORDS = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "twelve": 12}
W2N = dict(NUMWORDS)
N2W = {v: k for k, v in NUMWORDS.items()}


def _gen_dataset(n, seed):
    rng = np.random.default_rng(seed); data = []
    templates = [
        lambda nm, ob, v: ("%s has %s %s ." % (nm, v, ob), [(nm, ob, v)]),
        lambda nm, ob, v: ("%s bought %s %s yesterday ." % (nm, v, ob), [(nm, ob, v)]),
        lambda nm, ob, v: ("There are %s %s in %s 's box ." % (v, ob, nm), [(nm, ob, v)]),
        lambda nm, ob, v: ("%s gave away %s %s ." % (nm, v, ob), [(nm, ob, v)]),
    ]
    for _ in range(n):
        if rng.random() < 0.4:  # two-fact sentence (distractor number present)
            nm1, nm2 = rng.choice(NAMES, 2, replace=False)
            ob1, ob2 = rng.choice(OBJECTS, 2, replace=False)
            v1 = int(rng.integers(2, 13)); v2 = int(rng.integers(2, 13))
            w1 = N2W.get(v1, str(v1)); w2 = N2W.get(v2, str(v2))
            s = "%s has %s %s and %s has %s %s ." % (nm1, w1, ob1, nm2, w2, ob2)
            data.append((s.split(), [(nm1, ob1, v1), (nm2, ob2, v2)]))
        else:
            nm = str(rng.choice(NAMES)); ob = str(rng.choice(OBJECTS)); v = int(rng.integers(2, 13))
            w = N2W.get(v, str(v)); t = templates[int(rng.integers(0, len(templates)))]
            s, facts = t(nm, ob, w)
            data.append((s.split(), facts))
    return data


# ---------- genuine FHRR ----------
def _codebook(tokens, seed):
    rng = np.random.default_rng(seed)
    return {t: np.exp(1j * rng.uniform(-np.pi, np.pi, DIM)) for t in tokens}


def _bind(a, b): return a * b
def _unbind(c, b): return c * np.conj(b)
def _bundle(vs):
    s = np.sum(vs, axis=0); mag = np.abs(s); mag[mag < 1e-9] = 1e-9
    return s / mag  # phase-only normalize (FHRR)
def _cos(a, b): return float(np.real(np.vdot(a, b)) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def _cleanup_number(vec, num_cb):
    best = None; bs = -1e18
    for n, cv in num_cb.items():
        sc = _cos(vec, cv)
        if sc > bs: bs = sc; best = n
    return best, bs


def _fhrr_extract(words, cb, num_cb):
    """PP-225 recall transfer: memory = bundle of content-word pairs; recall value via unbind(memory, bind(entity,object))."""
    toks = [w for w in words]
    content = [w for w in toks if w in cb]
    if len(content) < 2: return set()
    # unsupervised relational memory: bind adjacent content-word pairs (no gold roles)
    pairs = [_bind(cb[content[i]], cb[content[i + 1]]) for i in range(len(content) - 1)]
    memory = _bundle(pairs)
    names = [w for w in toks if w in NAMES]; objs = [w for w in toks if w in OBJECTS]
    out = set()
    for nm in names:
        for ob in objs:
            key = _bind(cb[nm], cb[ob])
            recalled = _unbind(memory, key)
            num, score = _cleanup_number(recalled, num_cb)
            if score > 0.18:  # acceptance threshold (above chance cleanup)
                out.add((nm, ob, num))
    return out


def _fhrr_extract_cartesian(words, cb, num_cb):
    """Best-shot: give FHRR category knowledge (names/objects/numbers) but NOT the association -- bind all
    cartesian (name x object x value) triples present, bundle, then recall value via unbind(bind(name,object)).
    Tests whether FHRR recall can recover the entity-object-value ASSOCIATION without a parser."""
    names = [w for w in words if w in NAMES]; objs = [w for w in words if w in OBJECTS]
    nums = sorted({W2N[w] for w in words if w in W2N} | {int(w) for w in words if w.isdigit()})
    if not (names and objs and nums): return set()
    num_vec = {n: num_cb.get(n) for n in nums if num_cb.get(n) is not None}
    triples = [_bind(_bind(cb[nm], cb[ob]), num_vec[n]) for nm in names for ob in objs for n in nums if n in num_vec]
    if not triples: return set()
    memory = _bundle(triples)
    local_numcb = {n: num_vec[n] for n in nums if n in num_vec}
    out = set()
    for nm in names:
        for ob in objs:
            recalled = _unbind(memory, _bind(cb[nm], cb[ob]))
            num, score = _cleanup_number(recalled, local_numcb)
            if num is not None and score > 0.18:
                out.add((nm, ob, num))
    return out


def _regex_extract(words):
    """Heuristic baseline: each number -> nearest object-noun + nearest name."""
    idx_num = [(i, (W2N[w] if w in W2N else (int(w) if w.isdigit() else None))) for i, w in enumerate(words)]
    idx_num = [(i, v) for i, v in idx_num if v is not None]
    out = set()
    for i, v in idx_num:
        ob = min(((j, w) for j, w in enumerate(words) if w in OBJECTS), key=lambda jw: abs(jw[0] - i), default=None)
        nm = min(((j, w) for j, w in enumerate(words) if w in NAMES), key=lambda jw: abs(jw[0] - i), default=None)
        if ob and nm: out.add((nm[1], ob[1], v))
    return out


def _prf(golds: List[set], preds: List[set]):
    tp = fp = fn = 0
    for g, p in zip(golds, preds):
        tp += len(g & p); fp += len(p - g); fn += len(g - p)
    prec = tp / (tp + fp + 1e-9); rec = tp / (tp + fn + 1e-9)
    return 2 * prec * rec / (prec + rec + 1e-9), prec, rec


def _selftest():
    assert _regex_extract("Tom has five apples .".split()) == {("Tom", "apples", 5)}
    cb = _codebook(["a", "b", "c"], 0)
    assert abs(_cos(cb["a"], cb["a"]) - 1.0) < 1e-6
    x = _unbind(_bind(cb["a"], cb["b"]), cb["b"]); assert _cos(x, cb["a"]) > 0.99  # unbind recovers
    print("[selftest] PASS: transfer-p5-factrecall-mwp", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run() -> Dict:
    data = _gen_dataset(60 if SMOKE else 400, seed=11)
    golds = [set(f) for _w, f in data]
    vocab = set(NAMES) | set(OBJECTS) | set(NUMWORDS) | {"has", "bought", "gave", "away", "there", "are", "in", "and", "yesterday", "'s", "box", ".", "the"}
    cb = _codebook(sorted(vocab), seed=7)
    num_cb = {v: cb[N2W[v]] if N2W.get(v) in cb else _codebook([str(v)], v)[str(v)] for v in range(2, 13)}
    # ensure number codebook uses the numword vectors actually in cb
    num_cb = {v: cb.get(N2W.get(v, ""), num_cb[v]) for v in range(2, 13)}
    t0 = time.time()
    adj_preds = [_fhrr_extract(w, cb, num_cb) for w, _f in data]
    car_preds = [_fhrr_extract_cartesian(w, cb, num_cb) for w, _f in data]
    regex_preds = [_regex_extract(w) for w, _f in data]
    a_f1, a_p, a_r = _prf(golds, adj_preds)
    c_f1, c_p, c_r = _prf(golds, car_preds)
    r_f1, r_p, r_r = _prf(golds, regex_preds)
    f_f1 = max(a_f1, c_f1)  # headline = FHRR best-shot
    print("  FHRR adjacent-pair recall:   F1=%.4f (P=%.3f R=%.3f)" % (a_f1, a_p, a_r), flush=True)
    print("  FHRR cartesian best-shot:    F1=%.4f (P=%.3f R=%.3f)" % (c_f1, c_p, c_r), flush=True)
    print("  regex heuristic baseline:    F1=%.4f (P=%.3f R=%.3f)" % (r_f1, r_p, r_r), flush=True)
    print("  FHRR best-shot vs regex gap = %+.4f (predicted FHRR << regex; structural mismatch)" % (f_f1 - r_f1), flush=True)
    return {"f1": round(f_f1, 4), "fhrr_f1": round(f_f1, 4), "fhrr_adjacent_f1": round(a_f1, 4),
            "fhrr_cartesian_f1": round(c_f1, 4), "regex_f1": round(r_f1, 4), "gap": round(f_f1 - r_f1, 4),
            "cartesian_prec": round(c_p, 3), "cartesian_rec": round(c_r, 3), "n": len(data)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    f = r["fhrr_f1"]; s = "FHRR-extract-F1=%.4f vs regex %.4f (gap %+.4f, n=%d)" % (f, r["regex_f1"], r["gap"], r["n"])
    if f >= 0.50:
        return ("HARD_PASS", "HARD_PASS: FHRR fact-recall transfers to MWP-KB extraction F1>=0.50 -- REFUTES Drill 2 P5 HARD-FAIL prediction (framework discriminator surprise; report as discovery per literature-is-not-oracle). " + s)
    if f >= 0.30:
        return ("MIDDLE_BAND", "MIDDLE_BAND: FHRR extraction 0.30-0.50 -- partial transfer; framework P5 prediction partially off. " + s)
    return ("HARD_FAIL", "HARD_FAIL: FHRR fact-recall extraction <0.30 -- Drill 2 P5 HARD-FAIL prediction CONFIRMED; transfer-conditions framework validated discriminatively (FHRR unbind structurally mismatched to text fact-extraction; substrate < regex). " + s)


print("[config] anchor=%s mode=%s DIM=%d" % (ANCHOR_NAME, RUN_MODE, DIM), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
