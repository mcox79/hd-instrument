"""Phase A -- MEASURE spaCy's grammatical-SUBJECT identification, modern vs archaic literary prose, vs gold.

The whole reading stack's role cue is spaCy `nsubj`->SUBJECT (coref subjecthood term + incumbent Centering
tier read it off the reading corpus). Suspected confound (coref adjacency 6, SUSPECTED-UNMEASURED): the
corpus is 100-200yo literary prose and spaCy is trained on modern text, so the subject label degrades on
archaic long-sentence prose and every downstream organ inherits the error. This cell sizes it.

METRIC (matched to what the organ consumes -- the coref cue asks 'did this entity hold a SUBJECT role'):
  LENIENT (primary): does spaCy tag the GOLD subject head token as nsubj/nsubjpass at all? (robust to which
                     predicate/aux token spaCy attached it to; == the subjecthood cue the organ reads).
  STRICT (secondary): + that subject edge climbs to the gold clause's verb (attached to the RIGHT predicate).
Alignment is by CHARACTER SPAN (robust to gold-vs-spaCy tokenization differences).

ARMS:
  modern_ud_ewt   UD English-EWT test gold nsubj/nsubj:pass -- thousands of clauses, ZERO annotation bias.
                  Anchors spaCy's modern accuracy + the LENGTH curve (long modern sentences isolate
                  sentence-LENGTH difficulty from archaic REGISTER -- the brief's required control).
  archaic_hand    hand-annotated LitBank novel sentences (blind subject-head gold, length-stratified).
  modern_hand     hand-annotated modern textbook sentences, SAME annotation standard as archaic (the
                  apples-to-apples register comparison; UD anchor uses the UD standard, reported separately).
  minpair_*       archaic<->modernized minimal pairs (same subject, length-matched): within-item register.

spaCy en_core_web_sm runs LOCALLY only. Deterministic. ASCII-only.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

ANCHOR = "role_parse_accuracy_probe_v1"
SUBJ_DEPS_UD = {"nsubj", "nsubj:pass"}
SUBJ_DEPS_SPACY = {"nsubj", "nsubjpass"}
UD_EWT_TEST = os.path.join(_REPO, "data", "corpora", "ud_english_ewt", "en_ewt-ud-test.conllu")
HANDGOLD_DIR = os.path.join(_REPO, "notes", "problems",
                            "role_assignment_is_untested_on_archaic_literary_prose")


# ---------------------------------------------------------------------------- conllu (modern gold)
def conllu_sentences(path: str):
    def flush(rows):
        toks, text = [], ""
        for r in rows:
            r["start"] = len(text)
            text += r["form"]
            r["end"] = len(text)
            if "SpaceAfter=No" not in r["misc"]:
                text += " "
            toks.append(r)
        return {"text": text, "toks": toks}
    rows: List[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line:
                if rows:
                    yield flush(rows); rows = []
                continue
            if line.startswith("#"):
                continue
            c = line.split("\t")
            if len(c) < 10 or ("-" in c[0]) or ("." in c[0]):
                continue
            rows.append({"id": int(c[0]), "form": c[1], "upos": c[3],
                         "head": int(c[6]) if c[6].lstrip("-").isdigit() else 0,
                         "deprel": c[7], "misc": c[9]})
        if rows:
            yield flush(rows)


def ud_gold_items(path: str, max_sents: Optional[int] = None) -> List[dict]:
    """One item per gold nominal subject of a finite (VERB/AUX-headed) clause."""
    items = []
    for i, sent in enumerate(conllu_sentences(path)):
        if max_sents is not None and i >= max_sents:
            break
        by_id = {t["id"]: t for t in sent["toks"]}
        n_tok = len(sent["toks"])
        for t in sent["toks"]:
            if t["deprel"] in SUBJ_DEPS_UD:
                v = by_id.get(t["head"])
                if v is not None and v["upos"] in ("VERB", "AUX"):
                    items.append({"text": sent["text"], "subj_span": (t["start"], t["end"]),
                                  "verb_span": (v["start"], v["end"]), "n_tok": n_tok})
    return items


# ---------------------------------------------------------------------------- spaCy subject read-out
def _load_spacy():
    import spacy
    return spacy.load("en_core_web_sm", disable=["ner", "lemmatizer"])


def _tok_span(text: str, tok_idx: int) -> Tuple[int, int]:
    """Char span of the split()-token at tok_idx (measured in the ORIGINAL text, which may have >1 space)."""
    pos, toks = 0, text.split()
    # walk the raw text token by token to get true offsets (handles multiple spaces)
    idx = 0
    for j, tk in enumerate(toks):
        start = text.index(tk, idx)
        end = start + len(tk)
        idx = end
        if j == tok_idx:
            return (start, end)
    raise IndexError(tok_idx)


def _overlap(a, b) -> bool:
    return a[0] < b[1] and b[0] < a[1]


def spacy_subject_flags(doc, subj_span, verb_span) -> Tuple[int, int, int]:
    """(lenient, strict, spacy_labeled_any_subject_on_this_verb). subj token = spaCy token with max overlap
    of the gold subject-head span. lenient: that token is nsubj/nsubjpass. strict: + its head chain reaches
    the gold verb span."""
    best, best_ov = None, 0
    for t in doc:
        ov = min(t.idx + len(t.text), subj_span[1]) - max(t.idx, subj_span[0])
        if ov > best_ov:
            best, best_ov = t, ov
    if best is None:
        return (0, 0, 0)
    lenient = int(best.dep_ in SUBJ_DEPS_SPACY)
    strict = 0
    if lenient and verb_span is not None:
        h = best.head
        for _ in range(4):
            if _overlap((h.idx, h.idx + len(h.text)), verb_span):
                strict = 1; break
            if h.head is h:
                break
            h = h.head
    return (lenient, strict, lenient)


def score_items(nlp, items: List[dict]) -> List[dict]:
    """items: {text, subj_span|subj_tok, verb_span|verb_tok, n_tok?}. Returns rows with lenient/strict/n_tok."""
    rows = []
    for it in items:
        text = it["text"]
        subj_span = it.get("subj_span") or _tok_span(text, it["subj_tok"])
        verb_span = it.get("verb_span")
        if verb_span is None and it.get("verb_tok") is not None:
            verb_span = _tok_span(text, it["verb_tok"])
        doc = nlp(text)
        ln, st, _ = spacy_subject_flags(doc, subj_span, verb_span)
        rows.append({"lenient": ln, "strict": st,
                     "n_tok": it.get("n_tok", len(text.split())),
                     "subj": text[subj_span[0]:subj_span[1]]})
    return rows


# ---------------------------------------------------------------------------- stats
def boot_ci(vals, n_boot=5000, seed=0):
    a = np.asarray(vals, float)
    if len(a) == 0:
        return (0.0, 0.0, 0.0, 0.0)
    rng = np.random.default_rng(seed)
    means = a[rng.integers(0, len(a), size=(n_boot, len(a)))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(a.mean()), float(lo), float(hi), float((hi - lo) / 2.0)


def perm_null_gap(a, b, n_perm=5000, seed=0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    pool = np.concatenate([a, b]); na = len(a); rng = np.random.default_rng(seed)
    g = np.empty(n_perm)
    for i in range(n_perm):
        rng.shuffle(pool); g[i] = abs(pool[:na].mean() - pool[na:].mean())
    return float(np.percentile(g, 95))


def paired_ci(diffs, n_boot=5000, seed=0):
    d = np.asarray(diffs, float)
    rng = np.random.default_rng(seed)
    means = d[rng.integers(0, len(d), size=(n_boot, len(d)))].mean(axis=1)
    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(d.mean()), float(lo), float(hi)


def by_length(rows, bins=((0, 15), (15, 25), (25, 40), (40, 9999))):
    out = {}
    for lo, hi in bins:
        sub = [r["lenient"] for r in rows if lo <= r["n_tok"] < hi]
        if sub:
            m, clo, chi, hw = boot_ci(sub)
            out[f"{lo}-{hi if hi < 9999 else 'inf'}"] = {"n": len(sub), "acc": round(m, 4),
                                                          "ci": [round(clo, 4), round(chi, 4)]}
    return out


def summarize(name, rows):
    ln = [r["lenient"] for r in rows]; st = [r["strict"] for r in rows]
    m, lo, hi, hw = boot_ci(ln)
    ms, los, his, hws = boot_ci(st)
    return {"arm": name, "n": len(rows),
            "subject_acc_lenient": round(m, 4), "ci_lenient": [round(lo, 4), round(hi, 4)], "hw_lenient": round(hw, 4),
            "subject_acc_strict": round(ms, 4), "ci_strict": [round(los, 4), round(his, 4)],
            "by_length_lenient": by_length(rows)}


def _load_jsonl(fname):
    p = os.path.join(HANDGOLD_DIR, fname)
    if not os.path.exists(p):
        return []
    out = []
    with open(p, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("//"):
                out.append(json.loads(line))
    return out


# ---------------------------------------------------------------------------- io
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR); os.makedirs(d, exist_ok=True); return d


def _atomic_write(metrics):
    d = _out_dir(); tmp = os.path.join(d, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(d, "metrics.json"))


def main(max_modern=None):
    nlp = _load_spacy()
    t0 = time.perf_counter()
    arms, rows_by = {}, {}

    modern_ud = score_items(nlp, ud_gold_items(UD_EWT_TEST, max_sents=max_modern))
    arms["modern_ud_ewt"] = summarize("modern_ud_ewt", modern_ud); rows_by["modern_ud_ewt"] = modern_ud

    archaic = _load_jsonl("archaic_subject_gold_v1.jsonl")
    modern_h = _load_jsonl("modern_subject_gold_v1.jsonl")
    if archaic:
        r = score_items(nlp, archaic); arms["archaic_hand"] = summarize("archaic_hand", r); rows_by["archaic_hand"] = r
    if modern_h:
        r = score_items(nlp, modern_h); arms["modern_hand"] = summarize("modern_hand", r); rows_by["modern_hand"] = r

    # apples-to-apples register gap: hand archaic vs hand modern (SAME annotation standard), lenient
    gap = None
    if archaic and modern_h:
        a = [x["lenient"] for x in rows_by["archaic_hand"]]
        b = [x["lenient"] for x in rows_by["modern_hand"]]
        ma, la, ha, _ = boot_ci(a); mb, lb, hb, _ = boot_ci(b)
        gap = {"archaic_hand_acc": round(ma, 4), "archaic_ci": [round(la, 4), round(ha, 4)],
               "modern_hand_acc": round(mb, 4), "modern_ci": [round(lb, 4), round(hb, 4)],
               "gap_modern_minus_archaic": round(mb - ma, 4),
               "null_p95": round(perm_null_gap(a, b), 4),
               "ci_separated": bool(ha < lb)}

    # within-item minimal-pair register isolation (content + length controlled), paired lenient diff
    pairs = _load_jsonl("register_minimal_pairs_v1.jsonl")
    minpair = None
    if pairs:
        ra = score_items(nlp, [p["archaic"] for p in pairs])
        rm = score_items(nlp, [p["modern"] for p in pairs])
        arms["minpair_archaic"] = summarize("minpair_archaic", ra)
        arms["minpair_modernized"] = summarize("minpair_modernized", rm)
        diffs = [rm[i]["lenient"] - ra[i]["lenient"] for i in range(len(pairs))]
        md, ld, hd = paired_ci(diffs)
        flips = [{"pid": pairs[i]["pid"], "phen": pairs[i]["phenomenon"],
                  "archaic_ok": ra[i]["lenient"], "modern_ok": rm[i]["lenient"]}
                 for i in range(len(pairs)) if ra[i]["lenient"] != rm[i]["lenient"]]
        minpair = {"n_pairs": len(pairs),
                   "archaic_acc": arms["minpair_archaic"]["subject_acc_lenient"],
                   "modernized_acc": arms["minpair_modernized"]["subject_acc_lenient"],
                   "paired_gap_modern_minus_archaic": round(md, 4), "paired_ci": [round(ld, 4), round(hd, 4)],
                   "paired_ci_excludes_zero": bool(ld > 0 or hd < 0),
                   "disagreements": flips}

    metrics = {
        "verdict": "MEASURED", "anchor_name": ANCHOR,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "elapsed_s": round(time.perf_counter() - t0, 1),
        "metric": "spaCy subject-head labeled nsubj/nsubjpass vs gold (LENIENT primary), char-span aligned",
        "arms": arms,
        "register_gap_hand_same_standard": gap,
        "minimal_pair_register_isolation": minpair,
        "caveat": ("modern_ud_ewt uses the UD gold standard; hand arms use one consistent human standard, so "
                   "the register comparison is archaic_hand vs modern_hand (and the paired minimal pairs). "
                   "UD anchor is a large unbiased reference for spaCy's modern subject accuracy."),
    }
    _atomic_write(metrics)
    m = arms["modern_ud_ewt"]
    print(f"[modern UD-EWT] n={m['n']} lenient={m['subject_acc_lenient']} {m['ci_lenient']} "
          f"strict={m['subject_acc_strict']} by_len={m['by_length_lenient']}")
    if gap:
        print(f"[register gap, same standard] archaic_hand={gap['archaic_hand_acc']} {gap['archaic_ci']} vs "
              f"modern_hand={gap['modern_hand_acc']} {gap['modern_ci']} gap={gap['gap_modern_minus_archaic']} "
              f"null_p95={gap['null_p95']} CI-sep={gap['ci_separated']}")
    if minpair:
        print(f"[minimal pairs n={minpair['n_pairs']}] archaic={minpair['archaic_acc']} "
              f"modernized={minpair['modernized_acc']} paired_gap={minpair['paired_gap_modern_minus_archaic']} "
              f"ci={minpair['paired_ci']} excl0={minpair['paired_ci_excludes_zero']}")
    print(f"-> {os.path.join(_out_dir(), 'metrics.json')}  ({metrics['elapsed_s']}s)")
    return metrics


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="full")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        nlp = _load_spacy()
        # known subject: 'sailor' is nsubj of 'mended'
        it = [{"text": "The old sailor mended the torn sail.", "subj_tok": 2, "verb_tok": 3}]
        r = score_items(nlp, it)
        assert r[0]["subj"] == "sailor", r[0]["subj"]
        assert r[0]["lenient"] == 1 and r[0]["strict"] == 1, r
        # inversion: spaCy still ought to tag 'she' a subject in "Said she nothing."
        assert _tok_span("a bb ccc", 1) == (2, 4)
        assert boot_ci([1, 1, 0, 1])[0] == 0.75
        print("[self-test] PASS"); sys.exit(0)

    smoke = args.smoke or args.mode == "smoke"
    try:
        main(max_modern=(200 if smoke else None))
    except SystemExit:
        raise
    except Exception as e:
        import traceback
        _atomic_write({"verdict": "CELL_CRASHED", "error": f"{type(e).__name__}: {e}",
                       "traceback": traceback.format_exc()[:4000]})
        raise
