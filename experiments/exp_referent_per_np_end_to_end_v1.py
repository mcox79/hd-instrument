"""exp_referent_per_np_end_to_end_v1 -- the BAR experiment for
open_a_discourse_referent_for_every_np_not_just_coref_mentions.

The parent PROVED a candidate-COVERAGE gap: the live read() sources who-did-what candidates from the CoNLL COREF
column, so on 25 real LitBank docs the gold PATIENT is even a candidate only 0.8183 of the time; opening a referent
for every content-noun-head NP (Kamp 1981 DRT / Heim 1982 file-change semantics) lifts coverage to 0.9705 (+0.1521).
But coverage != end-to-end accuracy: MORE candidates recover the missed patient AND insert closer distractors that
can steal the positional pick. This cell measures the NET, end-to-end, through the ACTUAL LIVE reader.

DESIGN -- one variable (the mention SOURCE), everything else the live reader:
  We monkeypatch the ONE function read() sources mentions from (hdlab.situation_reader.parse_litbank_conll) so the
  full live SituationReader().read() runs unchanged except for which nouns become discourse referents. Events carry
  (sent_idx, pred_idx); we match them to the cleaned who-did-what gold (verb_idx == pred_idx) and score
  pick==gold_head with ABSTENTION COUNTED AS WRONG (effective end-to-end). Same reader config + same event set across
  arms -> the ONLY thing that moves the patient is the candidate source.

ARMS:
  coref  (FLOOR)  : the live coref-column mentions, exactly as deployed today.
  rnp    (FIX)    : referent-per-NP is THE source -- a referent for every content-noun head (head-positioned);
                    coref is DEMOTED to a downstream LINKING pass (clusters inherited from overlapping coref spans,
                    pronoun mentions preserved so pronoun resolution / who-has-what still runs). Brief's design.
  rnp_union       : conservative ADDITIVE variant -- coref mentions AS-IS + singleton referents only for content
                    nouns coref missed (keeps live coref positions; adds the gap-fillers).
  twin   (CONTROL): coref mentions + the SAME NUMBER of filler referents as `rnp` added, but at RANDOM non-head
                    token positions (info-free: matched candidate COUNT, wrong places). Must LOSE.

Glass-box, CPU, NO LLM/spaCy on the scored path. ASCII. own dir. hdlab is READ (monkeypatched at runtime, not edited).
"""
from __future__ import annotations
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse, glob, json, sys, time
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (_REPO, os.path.join(_REPO, "experiments")):
    if p not in sys.path:
        sys.path.insert(0, p)

import experiments.exp_verbrole_exemplar_which_arg_v1 as V1
import experiments.exp_19c_composed_cleaned_gold_v1 as CG        # is_clean_do: the parent's clean-19c DO filter
from hdlab.pos_tagger import PosTagger
from hdlab.scene_segment import parse_conll_sentences
import hdlab.situation_reader as SR
from hdlab.situation_reader import SituationReader

from experiments._seed_checkpoint import get_output_dir   # Q115: re-runnable output dir (added 2026-09-15 when first tracked)
OUT_DIR = get_output_dir("exp_referent_per_np_end_to_end_v1")
CORPUS = os.path.join(_REPO, "data/corpora/litbank_coref_conll")
POS_ASSET = os.path.join(_REPO, "data/frontend_assets/pos_tagger_ud_ewt_upos.json")
LB = os.path.join(_REPO, "data/predict_revise_recall_v1/_population_litbank.json")
NOMINAL = ("NOUN", "PROPN")
_ORIG_PARSE = SR.parse_litbank_conll        # the real coref-column parser (captured before patching)


def _norm(text_or_toks) -> str:
    if isinstance(text_or_toks, str):
        return " ".join(t.lower() for t in text_or_toks.split())
    return " ".join(t.lower() for t in text_or_toks)


def _content_head_positions(toks, up):
    """Referent-per-NP head set (Kamp/Heim): within-sentence token indices of every content-noun head.
    Same rule the parent prototype validated for coverage (NOUN/PROPN, non-stop, len>=3)."""
    return [i for i, u in enumerate(up) if u in NOMINAL and toks[i].lower() not in V1.STOP and len(toks[i]) >= 3]


def _mk_referent(head_low, sent_idx, wpos, cluster, midx):
    """A discourse-referent mention dict in the parse_litbank_conll schema (single-token, non-pronoun)."""
    return {"cluster": cluster, "gtok_start": -1, "gtok_end": -1, "sent_idx": sent_idx,
            "wtok_start": wpos, "head": head_low, "is_pronoun": False,
            "gender": None, "number": None, "name_gender": None, "span_toks": [head_low], "midx": midx}


def _finalize(mentions):
    """Recompute midx + per-sentence grammatical-role rank (subjecthood proxy) over the union, exactly as
    parse_litbank_conll does, so _sentence_nominals / _pick_role_mentions behave identically."""
    mentions.sort(key=lambda m: (m["sent_idx"], m["wtok_start"], m.get("gtok_start", 0)))
    for i, m in enumerate(mentions):
        m["midx"] = i
    by_sent = {}
    for m in mentions:
        by_sent.setdefault(m["sent_idx"], []).append(m)
    for lst in by_sent.values():
        for rank, m in enumerate(sorted(lst, key=lambda mm: (mm["wtok_start"], mm["midx"]))):
            m["sent_role_rank"] = rank
            m["is_subject"] = (rank == 0)
    return mentions


def build_source(path, tagger, mode, name_gender_map=None, rng=None, supplied_by_sent=None):
    """Return (mentions, n_sents) for the given candidate-SOURCE mode. Reuses the REAL coref parse for clusters,
    pronouns and gender; adds/reshapes the non-pronoun candidate set per mode."""
    coref, n_sents = _ORIG_PARSE(path, name_gender_map=name_gender_map)
    if mode == "coref":
        return coref, n_sents
    sents = parse_conll_sentences(path)
    if mode == "supplied":
        # NO-REGRESSION arm: give the reader EXACTLY the noun-supplied eval candidate set (gold cand_idx/cand_heads),
        # coref pronouns preserved. rnp_vs_supplied through the LIVE reader = does self-built referent-per-NP regress
        # the accuracy the eval (which hands the nouns) gets? Uses the supplied_by_sent map (norm_sent -> [(idx,head)]).
        pron = [m for m in coref if m["is_pronoun"]]
        out = []
        cl = (max([m["cluster"] for m in coref], default=-1) + 1)
        for si, toks in enumerate(sents):
            if si >= n_sents:
                break
            supplied = (supplied_by_sent or {}).get(_norm(toks))
            if not supplied:
                continue
            for idx, head in supplied:
                if 0 <= idx < len(toks):
                    out.append(_mk_referent(str(head).lower(), si, idx, cl, -1)); cl += 1
        return _finalize(pron + out), n_sents
    # coref non-pronoun HEAD position per sentence (head = last span token) -> so we don't double-open a referent
    coref_head_wpos = {}    # (sent_idx, head_wpos) -> cluster
    pron_mentions = [m for m in coref if m["is_pronoun"]]
    nom_coref = [m for m in coref if not m["is_pronoun"]]
    for m in nom_coref:
        span = max(0, m["gtok_end"] - m["gtok_start"])
        hw = m["wtok_start"] + span
        coref_head_wpos[(m["sent_idx"], hw)] = m["cluster"]
    next_cluster = (max([m["cluster"] for m in coref], default=-1) + 1)

    out = []
    added = 0
    for si, toks in enumerate(sents):
        if si >= n_sents:
            break
        up = tagger.tag(list(toks))
        heads = _content_head_positions(toks, up)
        if mode in ("rnp", "rnp_union"):
            for hw in heads:
                cl = coref_head_wpos.get((si, hw))
                if mode == "rnp_union" and cl is not None:
                    continue   # union: keep the coref mention as-is, add only the MISSED nouns
                if cl is None:
                    cl = next_cluster; next_cluster += 1   # singleton referent (coref links it downstream)
                    added += 1
                out.append(_mk_referent(toks[hw].lower(), si, hw, cl, -1))
        elif mode == "twin":
            # match the COUNT rnp adds, but place fillers at RANDOM non-head token positions (info-free)
            missed = [hw for hw in heads if (si, hw) not in coref_head_wpos]
            nonhead = [j for j in range(len(toks)) if j not in set(heads)]
            k = min(len(missed), len(nonhead))
            if k and rng is not None:
                for j in rng.choice(nonhead, size=k, replace=False):
                    out.append(_mk_referent(toks[int(j)].lower(), si, int(j), next_cluster, -1))
                    next_cluster += 1; added += 1

    if mode == "rnp":
        mentions = pron_mentions + out                 # referent-per-NP is THE source; coref pronouns preserved
    else:  # rnp_union / twin: coref (all) + the extra referents
        mentions = list(coref) + out
    return _finalize(mentions), n_sents


def read_doc_patients(reader, path, tagger, mode, name_gender_map, rng, supplied_by_sent=None):
    """Run the LIVE reader with the mention source swapped; return {(norm_sent, pred_idx): patient_low} and the
    set of (norm_sent, pred_idx) the reader emitted an event for (for abstention accounting)."""
    def _patched(p, name_gender_map=None, **_kw):   # 2026-09-15: the reader passes tagger= since pri 109; accept and ignore
        return build_source(p, tagger, mode, name_gender_map=name_gender_map, rng=rng,
                            supplied_by_sent=supplied_by_sent)
    SR.parse_litbank_conll = _patched
    try:
        sm = reader.read(path)
    finally:
        SR.parse_litbank_conll = _ORIG_PARSE
    sents = parse_conll_sentences(path)
    sent_norm = {si: _norm(toks) for si, toks in enumerate(sents)}
    picks = {}
    for e in sm.events:
        if e.pred_idx is None:
            continue
        key = (sent_norm.get(e.sent_idx), e.pred_idx)
        if key[0] is None:
            continue
        picks[key] = (e.patient or "?").lower()
    return picks


def score(rows, picks):
    """effective end-to-end: pick==gold_head, ABSTENTION (no event / patient '?') = WRONG. Returns per-item 0/1."""
    hits = []
    for r in rows:
        key = (_norm(r["sent"]), r["verb_idx"])
        pk = picks.get(key, "?")
        hits.append(1 if (pk not in ("?", "", None) and pk == r["gold_head"]) else 0)
    return np.array(hits, dtype=np.float64)


def _supplied_pick(r):
    """NO-REGRESSION reference: the reader's positional rule (nearest post-verbal NP-head) over the FULL supplied
    candidate set the noun-supplied eval hands it (r['cand_heads'] at r['cand_idx']). This is the eval-setting
    ceiling referent-per-NP must not regress -- rnp reconstructs ~this set from POS, so rnp ~= supplied."""
    vi = r["verb_idx"]
    post = [(ci, h) for h, ci in zip(r["cand_heads"], r["cand_idx"])
            if ci > vi and h not in V1.STOP and len(h) >= 3]
    if not post:
        return "?"
    post.sort()
    return post[0][1]


def _boot_delta(a, b, n_boot, seed):
    """paired bootstrap of mean(a)-mean(b); returns (delta, lo, hi, half, null_p95)."""
    rng = np.random.default_rng(seed)
    d = a - b
    n = len(d)
    idx = rng.integers(0, n, size=(n_boot, n))
    boot = d[idx].mean(axis=1)
    lo, hi = np.percentile(boot, [2.5, 97.5])
    # null: sign-flip permutation of the paired differences
    signs = rng.choice([-1.0, 1.0], size=(n_boot, n))
    nullb = (d[None, :] * signs).mean(axis=1)
    return float(d.mean()), float(lo), float(hi), float((hi - lo) / 2), float(np.percentile(np.abs(nullb), 95))


def run(n_docs=None, n_boot=1000, seed=20260903):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    tagger = PosTagger.load(POS_ASSET)
    gaz = {}
    try:
        import experiments.exp_situation_qa_v1 as SITQA
        gaz = SITQA.load_given_gazetteer()
    except Exception:
        gaz = {}
    reader = SituationReader(gaz=gaz)            # the LIVE default reader (all net-positive flags ON)
    docs = sorted(glob.glob(os.path.join(CORPUS, "*.conll")))
    if n_docs:
        docs = docs[:n_docs]

    # gold rows that MATCH a doc sentence (deployment population -- same match the coverage prototype used)
    rows_all = V1.load_pop(LB)
    doc_sents = set()
    for d in docs:
        for toks in parse_conll_sentences(d):
            doc_sents.add(_norm(toks))
    rows = [r for r in rows_all if r.get("gold_head") and _norm(r["sent"]) in doc_sents]
    # regime split: FULL (all matched) + CLEAN_DO (parent's parser-free clean-19c direct-object gold, the honest instrument)
    clean_flags = np.array([CG.is_clean_do(r, tagger.tag(r["sent"].split()))[0] for r in rows], dtype=bool)
    # supplied-candidate map (norm_sent -> [(idx, head)]) = the exact noun-supplied eval candidate set per sentence
    supplied_by_sent = {}
    for r in rows:
        supplied_by_sent.setdefault(_norm(r["sent"]),
                                    list(zip([int(i) for i in r["cand_idx"]], [str(h) for h in r["cand_heads"]])))

    modes = ["coref", "rnp", "rnp_union", "twin", "supplied"]
    picks = {m: {} for m in modes}
    for d in docs:
        for m in modes:
            rng = np.random.default_rng(seed + hash(os.path.basename(d)) % 100000) if m == "twin" else None
            picks[m].update(read_doc_patients(reader, d, tagger, m, gaz, rng, supplied_by_sent=supplied_by_sent))

    hits_full = {m: score(rows, picks[m]) for m in modes}
    naive_supplied = np.array([1 if (_supplied_pick(r) == r["gold_head"]) else 0 for r in rows], dtype=np.float64)

    res = {"n_docs": len(docs), "n_clauses_full": len(rows), "n_clauses_clean_do": int(clean_flags.sum())}
    for regime, mask in [("FULL", np.ones(len(rows), dtype=bool)), ("CLEAN_DO", clean_flags)]:
        hits = {m: hits_full[m][mask] for m in modes}
        acc = {m: float(hits[m].mean()) for m in modes}
        acc["naive_supplied_positional"] = float(naive_supplied[mask].mean())
        block = {"n": int(mask.sum()), "effective_end_to_end": {m: round(acc[m], 4) for m in modes},
                 "naive_supplied_positional": round(acc["naive_supplied_positional"], 4)}
        for name, a, b in [("rnp_vs_coref", "rnp", "coref"),
                           ("rnp_union_vs_coref", "rnp_union", "coref"),
                           ("rnp_vs_twin", "rnp", "twin"),
                           ("twin_vs_coref", "twin", "coref"),
                           ("rnp_vs_supplied_noregress", "rnp", "supplied")]:
            dlt, lo, hi, half, p95 = _boot_delta(hits[a], hits[b], n_boot, seed)
            block[name] = {"delta": round(dlt, 4), "ci_lo": round(lo, 4), "ci_hi": round(hi, 4),
                           "ci_half": round(half, 4), "null_p95": round(p95, 4),
                           "ci_separated": bool(lo > 0), "over_null": bool(dlt > p95)}
        res[regime] = block
    el = round(time.time() - t0, 1)
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor_name": "referent_per_np_end_to_end_v1", "results": res,
                   "elapsed_s": el, "ts_iso": datetime.now(timezone.utc).isoformat()},
                  fh, indent=2)
    res["_elapsed"] = "%.1fs" % el
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--docs", type=int, default=None)
    ap.add_argument("--nboot", type=int, default=1000)
    args = ap.parse_args()
    nd = 3 if (args.self_test or args.smoke) else args.docs
    res = run(n_docs=nd, n_boot=(200 if (args.self_test or args.smoke) else args.nboot))
    print("\n===== REFERENT-PER-NP end-to-end who-did-what (LIVE reader; abstain=wrong) docs=%d ====="
          % res["n_docs"], flush=True)
    for regime in ("FULL", "CLEAN_DO"):
        b = res[regime]; e = b["effective_end_to_end"]
        print("\n-- %s regime (n=%d) --" % (regime, b["n"]), flush=True)
        print("  FLOOR coref %.4f | FIX referent-per-NP %.4f (union %.4f) | TWIN %.4f | SUPPLIED(live) %.4f | naive-pos %.4f"
              % (e["coref"], e["rnp"], e["rnp_union"], e["twin"], e["supplied"], b["naive_supplied_positional"]), flush=True)
        for k in ("rnp_vs_coref", "rnp_vs_twin", "twin_vs_coref", "rnp_vs_supplied_noregress"):
            d = b[k]
            tag = ("CI-SEP" if d.get("ci_separated") else "n.s.") if "ci_separated" in d else ""
            print("    %-26s d=%+.4f CI[%+.4f,%+.4f] half=%.4f %s"
                  % (k, d["delta"], d["ci_lo"], d["ci_hi"], d["ci_half"], tag), flush=True)
    if args.self_test or args.smoke:
        assert res["n_clauses_full"] >= 20, "too few matched clauses"
        assert res["FULL"]["effective_end_to_end"]["rnp"] >= res["FULL"]["effective_end_to_end"]["coref"], \
            "fix should not trail the coref floor on the smoke set"
        print("\n[self-test] PASS", flush=True)
    print("\n[done] %s" % res.get("_elapsed", ""), flush=True)


if __name__ == "__main__":
    main()
