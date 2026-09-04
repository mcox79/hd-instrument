"""exp_parser_role_attachment_v1 -- prototype the IDEAL parser improvement that realizes the rest of the
who-did-what gain (structure-first patient 0.76 -> gold-parse ceiling 0.91).

The gap is ENTIRELY the parser's verb->argument attachment (structural_roles reads only the verb's dependents;
our-parse 0.76 vs gold-parse 0.91). The brain-faithful fix (Hagoort MUC; research this session): retrieve the
verb's ARGUMENT FRAME (valency/subcat) and BIND arguments into its slots by UNIFICATION -- so a verb that expects
an object gets one bound even when the raw transition-parser mis-attached it. This cell:
  (A) DECOMPOSES the structure-first misses: did the parse attach NO nominal on the needed side (recoverable by
      frame-binding) or attach the WRONG one?
  (B) prototypes FRAME_GUIDED binding (subcat-gated object/subject binding + PP-object skip + coordination share)
      and measures how much of the 0.76->0.91 gap it closes, vs the gold-parse ceiling, on clean UD-EWT (test+train).
Zero external LLM; the verb-frame is the on-disk subcat/valency signal. hdlab READ-only. ASCII. own dir.
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "3")
import argparse, json, time
from collections import Counter
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.pos_tagger import PosTagger
from hdlab.relcl_resolver import _cands
from hdlab.graded_role_assigner import robust_passive
from hdlab.thematic_role_labeler import lemma_verb, is_strictly_intransitive
from hdlab import verb_subcat as VS
import experiments.exp_whodidwhat_ud_structural_v1 as UD
from experiments.exp_structural_role_reader_v1 import structural_roles, _verb_nom_deps, _by_agent, _shared_object

POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
UD_TEST = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu")
UD_TRAIN = os.path.join(_REPO, "data/corpora/ud_english_ewt/en_ewt-ud-train.conllu")
OUT_DIR = os.path.join(_REPO, "data/exp_parser_role_attachment_v1")
NOMINAL = {"NOUN", "PROPN", "PRON"}


def _transitive(lem):
    """verb-frame valency: does the verb expect a direct object? (subcat signal, glass-box)."""
    return not is_strictly_intransitive(lem) and not VS.suppress_patient(lem, 0.5)


def _is_pp_object(pos, toks, v, c):
    """c is a PP-object (oblique), not the direct object, if a preposition governs it between v and c."""
    j = c - 1
    while j > v:
        if pos[j - 1] == "ADP" or toks[j - 1].lower() in ("of", "to", "in", "on", "at", "for", "with", "from", "by", "into", "over", "under", "about"):
            return True
        if pos[j - 1] in NOMINAL or pos[j - 1] == "VERB":
            break
        j -= 1
    return False


def frame_first_patient(toks, pos, heads, v, is_passive):
    """FRAME-FIRST binding: ignore the noisy raw attachment for the object; the verb's FRAME (valency) + grammatical
    position decide. Transitive active -> nearest post-verbal DIRECT (non-PP) object; passive -> nearest pre-verbal
    (non-PP) promoted subject; intransitive -> no object. Coordination share when no local object."""
    n = len(toks); lem = lemma_verb(toks[v - 1])
    if is_passive:
        for c in range(v - 1, 0, -1):
            if pos[c - 1] in NOMINAL and not _is_pp_object(pos, toks, 0, c):
                return c
        nom = _verb_nom_deps(pos, heads, v, n); post = [c for c in nom if c > v]
        return post[0] if post else None
    if _transitive(lem):
        for c in range(v + 1, n + 1):
            if pos[c - 1] in NOMINAL and not _is_pp_object(pos, toks, v, c):
                return c
        sh = _shared_object(toks, pos, heads, v, n)
        return sh
    return None


def frame_guided_patient(toks, pos, heads, v, is_passive):
    """MUC-style verb-frame binding: read the object off the parse where present; otherwise, if the verb's frame
    expects an object, BIND the nearest non-PP post-verbal nominal (the direct object the parser missed). Passive:
    bind the promoted (pre-verbal) subject, else the by-phrase/nearest pre-verbal nominal. Coordination share."""
    n = len(toks); lem = lemma_verb(toks[v - 1])
    nom = _verb_nom_deps(pos, heads, v, n)
    pre = [c for c in nom if c < v]; post = [c for c in nom if c > v]
    if is_passive:
        if pre:
            return pre[-1]
        # promoted subject the parse missed: nearest pre-verbal nominal not in a PP
        for c in range(v - 1, 0, -1):
            if pos[c - 1] in NOMINAL and not (c - 2 >= 0 and pos[c - 2] == "ADP"):
                return c
        return post[0] if post else None
    # active: the parse's object attachment carries real signal (frame-first that ignores it collapses to 0.58) ->
    # trust the nearest post-verbal dependent, then frame-bind only when the parse found no object.
    if post:
        return post[0]
    sh = _shared_object(toks, pos, heads, v, n)          # coordination/control sharing
    if sh is not None:
        return sh
    if _transitive(lem):                                 # frame expects an object the parser missed -> BIND it
        for c in range(v + 1, n + 1):
            if pos[c - 1] in NOMINAL and not (c - 2 >= 0 and pos[c - 2] == "ADP"):
                return c
    return None                                          # intransitive, no object -> genuinely no patient


def eval_split(path, tagger, W, parse, max_sents=None):
    sents = UD.load_ud(path)
    if max_sents:
        sents = sents[:max_sents]
    gpos = {tuple(t["form"] for t in s): [t["upos"] for t in s] for s in sents}
    gheads = {tuple(t["form"] for t in s): {t["id"]: t["head"] for t in s} for s in sents}
    R = {k: [] for k in ("STRUCT_ourparse", "FRAME_GUIDED", "FRAME_FIRST", "STRUCT_goldparse")}
    miss = Counter()
    for toks_l, v, pat, passive in UD.gold_items(sents):
        toks = tuple(toks_l); pos = tagger.tag(list(toks_l)); cands = _cands(pos)
        if not cands:
            continue
        try:
            oh = parse(list(toks_l), pos, W)[0]
        except Exception:
            oh = {}
        vpass = robust_passive(toks_l, pos, v)
        s_our = structural_roles(toks_l, pos, oh, v, vpass)["patient"]
        s_frame = frame_guided_patient(toks_l, pos, oh, v, vpass)
        s_ff = frame_first_patient(toks_l, pos, oh, v, vpass)
        s_gold = structural_roles(toks_l, gpos[toks], gheads[toks], v, passive)["patient"]
        R["STRUCT_ourparse"].append(1 if s_our == pat else 0)
        R["FRAME_GUIDED"].append(1 if s_frame == pat else 0)
        R["FRAME_FIRST"].append(1 if s_ff == pat else 0)
        R["STRUCT_goldparse"].append(1 if s_gold == pat else 0)
        # decompose the STRUCT_ourparse miss
        if s_our != pat:
            nom = _verb_nom_deps(pos, oh, v, len(toks_l))
            side = [c for c in nom if (c < v if vpass else c > v)]
            if not side:
                miss["parse_attached_NO_arg_on_side (frame-binding can recover)"] += 1
            elif pat not in nom:
                miss["gold_arg_NOT_a_verb_dependent (attachment error)"] += 1
            else:
                miss["wrong_dep_chosen_among_deps"] += 1
    m = lambda d: round(float(np.mean(d)), 4) if d else None
    base = m(R["STRUCT_ourparse"]); ceil = m(R["STRUCT_goldparse"])
    def gap(k):
        return round((m(R[k]) - base) / max(1e-9, ceil - base), 3) if ceil > base else None
    return {"n": len(R["STRUCT_ourparse"]),
            "acc": {k: m(R[k]) for k in R},
            "gap_closed_frac": {"FRAME_GUIDED": gap("FRAME_GUIDED"), "FRAME_FIRST": gap("FRAME_FIRST")},
            "miss_decomposition": dict(miss.most_common())}


def run(smoke=False):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    from hdlab.arceager_parser import load_model, parse_with_conf, MODEL_PATH
    W = load_model(MODEL_PATH)
    res = {"TEST": eval_split(UD_TEST, tagger, W, parse_with_conf, max_sents=(120 if smoke else None)),
           "TRAIN_sample": eval_split(UD_TRAIN, tagger, W, parse_with_conf, max_sents=(120 if smoke else 1500))}
    res["elapsed_s"] = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "parser_role_attachment_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    res = run(smoke=(a.self_test or a.smoke))
    for split in ("TEST", "TRAIN_sample"):
        s = res[split]
        print("\n=== %s (n=%d) patient accuracy ===" % (split, s["n"]), flush=True)
        print("  STRUCT_ourparse %s | FRAME_GUIDED %s | FRAME_FIRST %s | ceiling(goldparse) %s"
              % (s["acc"]["STRUCT_ourparse"], s["acc"]["FRAME_GUIDED"], s["acc"]["FRAME_FIRST"], s["acc"]["STRUCT_goldparse"]), flush=True)
        print("  gap closed: %s" % s["gap_closed_frac"], flush=True)
        print("  miss decomposition:", s["miss_decomposition"], flush=True)
    if a.self_test or a.smoke:
        assert res["TEST"]["n"] > 30
        print("\n[self-test] PASS", flush=True)


if __name__ == "__main__":
    main()
