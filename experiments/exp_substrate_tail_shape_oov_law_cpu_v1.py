"""
exp_substrate_tail_shape_oov_law_cpu_v1.py -- quantify the cross-domain tail-shape SPECTRUM into a predictive OOV law -- CPU.

ROUTING: deepen the novel cross-domain tail-shape finding (4 anchors: NER 1.150 / POS 1.011 / topic 1.002 / sentiment 0.998 at
  ratio@100pct). Hypothesis: the high-data transfer TAIL magnitude is predicted by the OPEN-VOCABULARY GAP -- the fraction of
  target-test label-bearing tokens that the SOURCE supplies but the target's own training under-covers. Measure a concrete OOV
  proxy per task and correlate with the measured tail. If tail ~ OOV-gap (monotone), the qualitative spectrum becomes a
  QUANTITATIVE LAW -- new substrate-product knowledge. Substrate-quality-first; NO LLM.

  OOV proxy per task = fraction of TARGET-TEST content tokens NOT seen in SOURCE-train vocabulary (the knowledge the source can
  supply that is absent from the target domain's surface vocab). Tasks reuse the 4 transfer datasets.
  DATA: PTB + ag_news + ontonotes bundled; IMDB + conll2003 + 20NG via datasets/raw (env-gated).

PRE-REGISTERED: HARD-PASS Spearman rank-correlation(OOV, tail) >= 0.80 across the 4 tasks (monotone law) AND order matches
  (NER highest OOV+tail). MIDDLE rho 0.5-0.8 (qualitative monotone). HARD-FAIL rho < 0.5 (OOV does not predict the tail; the
  spectrum needs a different predictor). UNKNOWN if data unavailable.
ASCII-only. CPU. --self-test + --smoke + metrics.json. Route via remote_cpu_queue (desktop).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse, os, time, json, re, urllib.request
from pathlib import Path
from typing import Dict, Tuple, List
import numpy as np
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics
ANCHOR_NAME = "substrate_tail_shape_oov_law_cpu_v1"
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
SMOKE = RUN_MODE == "smoke"
_TOK = re.compile(r"[a-z']+")
# measured tail ratio@100pct from the 4 transfer cells (this session)
TAIL = {"NER": 1.150, "POS": 1.011, "topic": 1.002, "sentiment": 0.998}
_STOP = {"the", "a", "an", "of", "to", "and", "in", "is", "it", "for", "on", "this", "that", "i", "you", "was", "with", "as", "are", "at", "be"}


def _content(text):
    return [w for w in _TOK.findall(text.lower()) if w not in _STOP and len(w) > 2]


def _oov(src_texts, tgt_test_texts, cap=4000):
    """fraction of target-test content tokens NOT in source-train content vocab."""
    src_vocab = set()
    for t in src_texts[:cap]:
        src_vocab.update(_content(t))
    seen = miss = 0
    for t in tgt_test_texts[:cap]:
        for w in _content(t):
            if w in src_vocab: seen += 1
            else: miss += 1
    return miss / (seen + miss + 1e-9)


def _spearman(xs, ys):
    def rank(a):
        order = np.argsort(a); r = np.empty(len(a)); r[order] = np.arange(len(a)); return r
    rx, ry = rank(np.array(xs)), rank(np.array(ys))
    rx -= rx.mean(); ry -= ry.mean()
    d = (rx ** 2).sum() ** 0.5 * (ry ** 2).sum() ** 0.5
    return float((rx * ry).sum() / (d + 1e-9))


def _load_ner():
    # CoNLL-2003 (source, raw) vs OntoNotes (target, bundled) -- use raw text columns
    try:
        with urllib.request.urlopen("https://raw.githubusercontent.com/synalp/NER/master/corpus/CoNLL-2003/eng.train", timeout=40) as r:
            txt = r.read().decode("utf-8", "replace")
        src = [" ".join(ln.split()[0] for ln in blk.splitlines() if ln.split()) for blk in txt.split("\n\n")]
    except Exception:
        return None
    d = json.load(open(REPO / "experiments" / "data" / "ontonotes_ner.json", encoding="utf-8"))
    tgt = [" ".join(t) for t, _g in d["test"] if t]
    return [s for s in src if s], tgt


def _load_pos():
    d = json.load(open(REPO / "experiments" / "data" / "ptb_treebank_tagged.json", encoding="utf-8"))
    src = [" ".join(tok[0] for tok in s) for s in d if s]
    try:
        with urllib.request.urlopen("https://raw.githubusercontent.com/synalp/NER/master/corpus/CoNLL-2003/eng.train", timeout=40) as r:
            txt = r.read().decode("utf-8", "replace")
        tgt = [" ".join(ln.split()[0] for ln in blk.splitlines() if ln.split()) for blk in txt.split("\n\n")]
    except Exception:
        return None
    return src, [t for t in tgt if t]


def _load_topic():
    ag = json.load(open(REPO / "experiments" / "data" / "ag_news.json", encoding="utf-8"))
    src = [e["text"] for e in ag["train"]]
    try:
        from datasets import load_dataset
        ds = load_dataset("SetFit/20_newsgroups"); tgt = list(ds["test"]["text"])
    except Exception:
        return None
    return src, tgt


def _load_sentiment():
    sst = json.load(open(REPO / "experiments" / "data" / "sst2.json", encoding="utf-8"))
    src = [e["text"] for e in sst["train"]]
    try:
        from datasets import load_dataset
        ds = load_dataset("imdb"); tgt = list(ds["test"]["text"])
    except Exception:
        return None
    return src, tgt


def run() -> Dict:
    cap = 800 if SMOKE else 4000
    loaders = {"NER": _load_ner, "POS": _load_pos, "topic": _load_topic, "sentiment": _load_sentiment}
    rows = []
    for name, ld in loaders.items():
        d = ld()
        if d is None:
            print("  %s: data unavailable -- skipped" % name, flush=True); continue
        src, tgt = d
        oov = _oov(src, tgt, cap)
        rows.append({"task": name, "oov": round(oov, 4), "tail": TAIL[name]})
        print("  %-9s OOV=%.4f  tail(ratio@100pct)=%.4f" % (name, oov, TAIL[name]), flush=True)
    if len(rows) < 3:
        return {"error": "insufficient_tasks_env_gated", "rows": rows, "note": "needs >=3 task datasets (some via datasets/raw)"}
    oovs = [r["oov"] for r in rows]; tails = [r["tail"] for r in rows]
    rho = round(_spearman(oovs, tails), 4)
    print("  Spearman rho(OOV, tail) = %.4f  (n=%d tasks)" % (rho, len(rows)), flush=True)
    return {"rho": rho, "rows": rows, "n_tasks": len(rows)}


def verdict(r) -> Tuple[str, str]:
    if r.get("error", "").startswith("insufficient"):
        return ("UNKNOWN", "UNKNOWN: <3 task datasets available (env-gated). " + r.get("note", "") + " rows=%s" % r.get("rows"))
    if r.get("error"): return ("UNKNOWN", "UNKNOWN: " + r["error"])
    rho = r["rho"]
    s = "Spearman rho(OOV, tail)=%.4f over %d tasks; rows=%s" % (rho, r["n_tasks"], [(x["task"], x["oov"], x["tail"]) for x in r["rows"]])
    if rho >= 0.80:
        return ("HARD_PASS", "HARD_PASS: the cross-domain TAIL is predicted by the OOV gap (Spearman rho>=0.80) -- the qualitative tail-shape spectrum becomes a QUANTITATIVE law: high-data transfer tail magnitude ~ target-vs-source open-vocabulary gap. New substrate-product knowledge. " + s)
    if rho >= 0.50:
        return ("MIDDLE_BAND", "MIDDLE_BAND: rho 0.5-0.8 -- OOV qualitatively predicts the tail (monotone) but not strongly; the predictor is directionally right, magnitude noisy at n=4. " + s)
    return ("HARD_FAIL", "HARD_FAIL: rho<0.5 -- OOV does NOT predict the tail; the spectrum needs a different predictor (e.g. output-space openness, not surface OOV). " + s)


def _selftest():
    assert abs(_spearman([1, 2, 3], [1, 2, 3]) - 1.0) < 1e-6
    assert abs(_spearman([1, 2, 3], [3, 2, 1]) + 1.0) < 1e-6
    assert 0.0 < _oov(["the cat sat"], ["the dog ran fast"]) <= 1.0
    print("[selftest] PASS: tail-shape-oov-law", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)
print("[config] anchor=%s mode=%s" % (ANCHOR_NAME, RUN_MODE), flush=True)
out_dir = get_output_dir(ANCHOR_NAME); t0 = time.time(); r = run()
v, vmsg = verdict(r); print("\n[VERDICT] " + vmsg, flush=True)
metrics = {"anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg, "summary": vmsg, "run_mode": RUN_MODE, "n_seeds": 1, "per_seed": [r], "elapsed_s": time.time() - t0}
write_metrics(out_dir, metrics, [r]); print("[metrics] written", flush=True)
