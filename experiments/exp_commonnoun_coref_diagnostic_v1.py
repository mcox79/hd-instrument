"""exp_commonnoun_coref_diagnostic_v1 -- CAN a glass-box common-noun discourse-referent LINKER even
recover gold's common-noun clustering? ("ask whether the experiment could have succeeded first.")

THE PROBLEM (form_a_discourse_referent_for_every_entity...): the reader's coref is proper-name-centric;
83.5% of narrative emotion experiencers are entities named only by a COMMON NOUN ("the man", "the
child"). The affect signal-loss study localized 87% of the end-to-end loss to this. The research
mechanism-diff (research_brain_vs_our_coref_binding_mechanism_diff_2026-09-04) named the fix -- Poesio-
Vieira DIRECT (head-noun-match) anaphora + the Givenness hierarchy (definiteness) -- but ALSO flagged
the HARD-FAIL risk: gold's own common-noun clustering may NOT align with head-noun identity ("the girl"
in one place, "the child" in another with no shared word -> needs BRIDGING/world-knowledge).

This cell measures, on LitBank gold coref (100 docs), WHETHER the mechanism can succeed BEFORE building it:
  (1) POPULATION: pronoun / proper-name / common-noun mention split; character-cluster stats.
  (2) HEAD-MATCH RECALL: of common-noun mentions that HAVE a non-pronoun antecedent in their gold
      cluster, what fraction share the head lemma with the nearest prior same-cluster non-pronoun mention?
      (the fraction linkable by descriptive-content match vs the fraction needing bridging).
  (3) RECENCY+HEAD-MATCH PRECISION / OVER-MERGE: for each common-noun mention, link it to the MOST-RECENT
      prior same-head-lemma non-pronoun mention; is that the SAME gold entity? (the over-merge risk of
      "all same-head = one entity": multiple "man"s in a novel). Decompose the errors: does a MODIFIER or
      GENDER cue separate them (recoverable), or are they identical (needs deeper salience/bridging)?
  (4) THE COREF CHAIN-F1 INSTRUMENT + FLOORS: B3 / MUC / CEAFe / CoNLL-avg on gold NON-PRONOUN mentions
      for {singleton, name-only (no common-noun links), surface-head (current reader: all same-head
      merged), all-same-head}. Establishes the floor the linker must beat and the over-merge ceiling.

Glass-box, deterministic, NO LLM, hdlab READ-only. ASCII. own data dir. Fast (pure parsing; inline-safe).
Run: .venv/Scripts/python.exe experiments/exp_commonnoun_coref_diagnostic_v1.py --self-test
     .venv/Scripts/python.exe experiments/exp_commonnoun_coref_diagnostic_v1.py
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, glob, json, re, time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import parse_litbank_conll, build_merge_map, name_content_tokens, load_name_gender

CONLL_DIR = os.path.join(_REPO, "data/litbank/coref_conll")
OUT_DIR = os.path.join(_REPO, "data/exp_commonnoun_coref_diagnostic_v1")

# gendered personal pronouns -> a cluster containing one is a PERSON/character cluster (high precision).
PERS_PRON = {"he", "him", "his", "himself", "she", "her", "hers", "herself"}
ALL_PRON = PERS_PRON | {"they", "them", "their", "theirs", "themselves", "it", "its", "itself",
                        "i", "me", "my", "we", "us", "our", "you", "your", "this", "that", "these",
                        "those", "who", "whom", "whose", "which", "himself", "themself"}
DEF_DET = {"the", "this", "that", "these", "those", "his", "her", "my", "your", "our", "their", "its"}
INDEF_DET = {"a", "an", "some", "any", "another", "no", "each", "every", "one"}
_IRREG = {"men": "man", "women": "woman", "children": "child", "people": "person", "gentlemen": "gentleman",
          "gentlewomen": "gentlewoman", "wives": "wife", "ladies": "lady", "brothers": "brother",
          "sisters": "sister", "feet": "foot", "teeth": "tooth", "geese": "goose", "mice": "mouse"}


def head_lemma(head: str) -> str:
    """Light noun lemma: irregular map, then regular plural strip (ies->y, ses/xes/ches->s.., s)."""
    h = re.sub(r"[^a-z]+", "", str(head).lower())
    if not h:
        return ""
    if h in _IRREG:
        return _IRREG[h]
    if len(h) > 4 and h.endswith("ies"):
        return h[:-3] + "y"
    if len(h) > 4 and h.endswith(("ses", "xes", "zes", "ches", "shes")):
        return h[:-2]
    if len(h) > 3 and h.endswith("s") and not h.endswith("ss"):
        return h[:-1]
    return h


def is_name(m, gaz) -> bool:
    """A clean proper name (aliasable) -- reuse the coref organ's own name test on the raw span."""
    return bool(name_content_tokens(m.get("span_toks", [m["head"]])))


def modifiers(m) -> set:
    """Non-determiner, non-head alphabetic modifier tokens of the span (lowercased)."""
    span = [w.lower() for w in m.get("span_toks", [m["head"]])]
    hl = head_lemma(m["head"])
    return {w for w in span[:-1] if w.isalpha() and w not in DEF_DET and w not in INDEF_DET
            and head_lemma(w) != hl}


def definiteness(m) -> str:
    span = [w.lower() for w in m.get("span_toks", [m["head"]])]
    if not span:
        return "bare"
    d = span[0]
    if d in INDEF_DET:
        return "indef"
    if d in DEF_DET:
        return "def"
    return "bare"


# ============================ CoNLL coref metrics (B3 / MUC / CEAFe) ==================================
def _clusters(labels):
    """label list -> list of index-sets (predicted/gold clusters)."""
    d = defaultdict(set)
    for i, l in enumerate(labels):
        d[l].add(i)
    return list(d.values())


def b3(pred, gold):
    """B-cubed P/R/F over mention-aligned label lists (verbatim contract of
    exp_extraction_quality_gate_neural_foundation_v1.b3_f1; cross-checked in self-test)."""
    n = len(pred)
    if n == 0:
        return 0.0, 0.0, 0.0
    gp = defaultdict(set); gg = defaultdict(set)
    for i in range(n):
        gp[pred[i]].add(i); gg[gold[i]].add(i)
    ps = rs = 0.0
    for i in range(n):
        pc = gp[pred[i]]; gc = gg[gold[i]]
        ov = len(pc & gc)
        ps += ov / len(pc); rs += ov / len(gc)
    p, r = ps / n, rs / n
    f = 2 * p * r / (p + r) if p + r > 0 else 0.0
    return p, r, f


def muc(pred, gold):
    """MUC link-based P/R/F. recall numerator = sum_G (|G| - #pred-partitions of G); denom = sum_G(|G|-1)."""
    def side(key, resp):
        kc = _clusters(key); num = den = 0
        resp_of = {}
        for ci, c in enumerate(_clusters(resp)):
            for i in c:
                resp_of[i] = ci
        for c in kc:
            if len(c) <= 1:
                continue
            parts = len({resp_of[i] for i in c})
            num += (len(c) - parts); den += (len(c) - 1)
        return num, den
    rn, rd = side(gold, pred)
    pn, pd = side(pred, gold)
    rec = rn / rd if rd else 0.0
    pre = pn / pd if pd else 0.0
    f = 2 * pre * rec / (pre + rec) if pre + rec > 0 else 0.0
    return pre, rec, f


def ceafe(pred, gold):
    """CEAFe (entity-based, phi4 = 2|R&G|/(|R|+|G|)); optimal 1-1 matching (scipy Hungarian, greedy fb)."""
    R = _clusters(pred); G = _clusters(gold)
    if not R or not G:
        return 0.0, 0.0, 0.0
    sim = np.zeros((len(R), len(G)))
    for i, r in enumerate(R):
        for j, g in enumerate(G):
            inter = len(r & g)
            if inter:
                sim[i, j] = 2.0 * inter / (len(r) + len(g))
    try:
        from scipy.optimize import linear_sum_assignment
        ri, gi = linear_sum_assignment(-sim)
        total = sim[ri, gi].sum()
    except Exception:
        total = 0.0; usedR = set(); usedG = set()
        order = sorted(((sim[i, j], i, j) for i in range(len(R)) for j in range(len(G))), reverse=True)
        for s, i, j in order:
            if s <= 0:
                break
            if i in usedR or j in usedG:
                continue
            usedR.add(i); usedG.add(j); total += s
    pre = total / len(R)
    rec = total / len(G)
    f = 2 * pre * rec / (pre + rec) if pre + rec > 0 else 0.0
    return pre, rec, f


def conll_scores(pred, gold):
    _, _, fb = b3(pred, gold)
    _, _, fm = muc(pred, gold)
    _, _, fc = ceafe(pred, gold)
    return {"muc_f1": round(fm, 4), "b3_f1": round(fb, 4), "ceafe_f1": round(fc, 4),
            "conll_avg": round((fm + fb + fc) / 3.0, 4)}


# ============================ clustering floors over NON-PRONOUN mentions ============================
def cluster_labels(doc_mentions, gaz, mode):
    """Assign a predicted cluster label to each NON-PRONOUN mention (doc-namespaced). Modes:
      singleton     -- each its own entity (lower bound).
      name_only     -- names aliased (build_merge_map); every common noun a SINGLETON (proper-name-centric:
                       forms NO common-noun link -- the reader's affect-canonicalizer behavior).
      surface_head  -- names aliased; common nouns grouped by HEAD LEMMA (the reader's overlay: all
                       same-head merged -> max common-noun over-merge).
      all_same_head -- everything (names too) grouped by head lemma (extreme over-merge reference)."""
    midx_to_canon, _c2m, _s = build_merge_map(doc_mentions, use_gazetteer=True)
    labels = {}
    for m in doc_mentions:
        if m["is_pronoun"]:
            continue
        mi = m["midx"]; hl = head_lemma(m["head"])
        if mode == "singleton":
            labels[mi] = "S%d" % mi
        elif mode == "all_same_head":
            labels[mi] = "H:" + hl
        elif mode == "name_only":
            c = midx_to_canon.get(mi)
            labels[mi] = ("N:" + c) if c is not None else ("S%d" % mi)
        elif mode == "surface_head":
            c = midx_to_canon.get(mi)
            labels[mi] = ("N:" + c) if c is not None else ("H:" + hl)
        else:
            raise ValueError(mode)
    return labels


def score_nonpron(docs, gaz, mode):
    pred, gold = [], []
    for di, (doc, ms) in enumerate(docs):
        lab = cluster_labels(ms, gaz, mode)
        for m in ms:
            if m["is_pronoun"]:
                continue
            pred.append("d%d:%s" % (di, lab[m["midx"]]))
            gold.append("d%d:%d" % (di, m["cluster"]))
    return conll_scores(pred, gold), len(pred)


# ============================ decisive: can descriptive-content match recover gold? ==================
def population_and_headmatch(docs, gaz):
    n_pron = n_name = n_common = 0
    n_char_cluster = n_cluster = 0
    common_in_char = 0
    # head-match recall: common-noun mentions WITH a prior same-cluster non-pronoun antecedent
    hm_opps = hm_headshare = 0
    # recency+head-match precision: link to most-recent prior same-head; correct = same gold cluster
    rh_cov = rh_correct = 0
    err_modifier_sep = err_gender_sep = err_identical = 0
    dist_correct = []   # sentence gap of CORRECT recency+head links
    dist_wrong = []     # sentence gap of OVER-MERGE (wrong) recency+head links
    for doc, ms in docs:
        by_cluster = defaultdict(list)
        for m in ms:
            by_cluster[m["cluster"]].append(m)
        n_cluster += len(by_cluster)
        for cid, cms in by_cluster.items():
            has_pers = any(mm["head"] in PERS_PRON for mm in cms) or \
                       any((mm.get("gender") in ("masc", "fem")) and not mm["is_pronoun"] for mm in cms)
            if has_pers:
                n_char_cluster += 1
        # ordered non-pronoun mentions (reading order = midx)
        noms = [m for m in ms if not m["is_pronoun"]]
        noms.sort(key=lambda m: m["midx"])
        prior_by_head = defaultdict(list)   # head_lemma -> list of (midx, cluster, mods, gender)
        prior_in_cluster = defaultdict(list)  # cluster -> list of prior non-pron mentions
        for m in ms:
            if m["is_pronoun"]:
                n_pron += 1; continue
            if is_name(m, gaz):
                n_name += 1
            else:
                n_common += 1
                if any((mm["head"] in PERS_PRON) for mm in by_cluster[m["cluster"]]):
                    common_in_char += 1
                # head-match RECALL: is there a prior same-cluster non-pronoun antecedent?
                pri_cl = prior_in_cluster.get(m["cluster"], [])
                if pri_cl:
                    hm_opps += 1
                    nearest = pri_cl[-1]
                    if head_lemma(nearest["head"]) == head_lemma(m["head"]):
                        hm_headshare += 1
                # recency+head PRECISION: most-recent prior same-head mention
                hl = head_lemma(m["head"])
                cand_list = prior_by_head.get(hl, [])
                if cand_list:
                    rh_cov += 1
                    cand = cand_list[-1]
                    gap = m["sent_idx"] - cand["sent_idx"]
                    if cand["cluster"] == m["cluster"]:
                        rh_correct += 1
                        dist_correct.append(gap)
                    else:
                        dist_wrong.append(gap)
                        cm = modifiers(cand); mm_ = modifiers(m)
                        cg = cand.get("gender"); mg = m.get("gender")
                        if cg in ("masc", "fem") and mg in ("masc", "fem") and cg != mg:
                            err_gender_sep += 1
                        elif cm and mm_ and cm.isdisjoint(mm_):
                            err_modifier_sep += 1
                        else:
                            err_identical += 1
            prior_in_cluster[m["cluster"]].append(m)
            prior_by_head[head_lemma(m["head"])].append(m)
    n_nonpron = n_name + n_common
    # window sweep: for a recency window W, keep a link iff gap<=W. correct_kept vs wrong_avoided(gap>W).
    dc = np.array(dist_correct); dw = np.array(dist_wrong)
    win_sweep = {}
    for W in (0, 1, 2, 3, 5, 8, 12, 20):
        kept_correct = int((dc <= W).sum()); split_correct = int((dc > W).sum())
        kept_wrong = int((dw <= W).sum()); split_wrong = int((dw > W).sum())
        # a link kept within W: precision among kept = kept_correct/(kept_correct+kept_wrong)
        kept = kept_correct + kept_wrong
        win_sweep[W] = {"kept_correct": kept_correct, "kept_wrong": kept_wrong,
                        "split_correct(lost)": split_correct, "split_wrong(avoided)": split_wrong,
                        "prec_kept": round(kept_correct / max(1, kept), 4)}
    return {
        "n_mentions": n_pron + n_nonpron, "n_pron": n_pron, "n_name": n_name, "n_common": n_common,
        "frac_nonpron_common": round(n_common / max(1, n_nonpron), 4),
        "n_cluster": n_cluster, "n_char_cluster": n_char_cluster,
        "common_in_char_cluster": common_in_char,
        "headmatch_recall": {
            "opportunities": hm_opps, "head_shared": hm_headshare,
            "frac": round(hm_headshare / max(1, hm_opps), 4),
            "note": "of common-noun mentions with a prior same-CLUSTER non-pron antecedent, frac where "
                    "the nearest such antecedent shares the head lemma (the rest need bridging/synonymy)"},
        "recency_head_precision": {
            "coverage": rh_cov, "correct": rh_correct,
            "acc": round(rh_correct / max(1, rh_cov), 4),
            "errors": {"gender_separable": err_gender_sep, "modifier_separable": err_modifier_sep,
                       "identical_ambiguous": err_identical},
            "note": "link each common-noun mention to the MOST-RECENT prior same-head non-pron mention; "
                    "acc = frac that are the SAME gold entity (over-merge = errors). Error decomposition: "
                    "how many over-merges a gender/modifier cue would separate vs genuinely identical."},
        "recency_window_sweep": win_sweep,
        "median_gap_correct": float(np.median(dc)) if len(dc) else None,
        "median_gap_wrong": float(np.median(dw)) if len(dw) else None,
    }


def load_docs(n=None):
    paths = sorted(glob.glob(os.path.join(CONLL_DIR, "*.conll")))
    if n:
        paths = paths[:n]
    gaz = load_name_gender()
    docs = []
    for p in paths:
        ms, _ns = parse_litbank_conll(p, name_gender_map=gaz)
        docs.append((os.path.basename(p), ms))
    return docs, gaz


def run(n=None):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    docs, gaz = load_docs(n)
    pop = population_and_headmatch(docs, gaz)
    floors = {}
    for mode in ("singleton", "name_only", "surface_head", "all_same_head"):
        sc, npred = score_nonpron(docs, gaz, mode)
        floors[mode] = {**sc, "n": npred}
    res = {"n_docs": len(docs), "population": pop, "nonpron_chainF1_floors": floors,
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "commonnoun_coref_diagnostic_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def _print(res):
    p = res["population"]
    print("=" * 84)
    print("COMMON-NOUN COREF DIAGNOSTIC  (%d LitBank docs)" % res["n_docs"])
    print("-" * 84)
    print("POPULATION: mentions=%d  pron=%d  name=%d  common=%d  (common/non-pron=%.3f)"
          % (p["n_mentions"], p["n_pron"], p["n_name"], p["n_common"], p["frac_nonpron_common"]))
    print("  clusters=%d  character(person)-clusters=%d  common-noun mentions in char clusters=%d"
          % (p["n_cluster"], p["n_char_cluster"], p["common_in_char_cluster"]))
    hr = p["headmatch_recall"]
    print("HEAD-MATCH RECALL: %d/%d = %.3f of common-noun links share the head lemma "
          "(1-frac needs bridging)" % (hr["head_shared"], hr["opportunities"], hr["frac"]))
    rp = p["recency_head_precision"]
    print("RECENCY+HEAD PRECISION: %d/%d = %.3f link to the SAME gold entity (over-merge = 1-acc)"
          % (rp["correct"], rp["coverage"], rp["acc"]))
    e = rp["errors"]
    print("   over-merge errors: gender-separable=%d  modifier-separable=%d  identical/ambiguous=%d"
          % (e["gender_separable"], e["modifier_separable"], e["identical_ambiguous"]))
    print("   median sentence-gap: correct-link=%s  over-merge-link=%s"
          % (p["median_gap_correct"], p["median_gap_wrong"]))
    print("   RECENCY-WINDOW sweep (keep link iff gap<=W): W -> prec_among_kept (correct_kept/wrong_kept | correct_lost/wrong_avoided)")
    for W, s in p["recency_window_sweep"].items():
        print("     W=%-3d prec=%.3f  (%d/%d kept | %d/%d split)" % (
            W, s["prec_kept"], s["kept_correct"], s["kept_wrong"],
            s["split_correct(lost)"], s["split_wrong(avoided)"]))
    print("-" * 84)
    print("NON-PRONOUN COREF CHAIN-F1 FLOORS (MUC / B3 / CEAFe / CoNLL-avg):")
    for mode, sc in res["nonpron_chainF1_floors"].items():
        print("  %-14s MUC %.4f  B3 %.4f  CEAFe %.4f  CoNLL %.4f  (n=%d)"
              % (mode, sc["muc_f1"], sc["b3_f1"], sc["ceafe_f1"], sc["conll_avg"], sc["n"]))
    print("=" * 84)


def self_test():
    # metric sanity: correct-gold beats scrambled; B3 matches the reused contract
    pred_ok = ["A", "A", "B", "B"]; gold = ["A", "A", "B", "B"]; pred_bad = ["A", "B", "A", "B"]
    assert b3(pred_ok, gold)[2] > b3(pred_bad, gold)[2]
    assert muc(pred_ok, gold)[2] > muc(pred_bad, gold)[2]
    assert ceafe(pred_ok, gold)[2] > ceafe(pred_bad, gold)[2]
    # perfect prediction -> all F1 == 1
    for fn in (b3, muc, ceafe):
        assert abs(fn(gold, gold)[2] - 1.0) < 1e-9, fn.__name__
    # cross-check b3 against the reused foundation scorer on a toy
    try:
        import experiments.exp_extraction_quality_gate_neural_foundation_v1 as V1
        a = b3(["C0", "C0", "S2", "S2"], ["A", "A", "B", "B"])
        b = V1.b3_f1(["C0", "C0", "S2", "S2"], ["A", "A", "B", "B"])
        assert abs(a[2] - b[2]) < 1e-9, (a, b)
    except Exception as e:
        print("[self-test] (b3 cross-check skipped: %s)" % e)
    # head lemma
    assert head_lemma("men") == "man" and head_lemma("ladies") == "lady" and head_lemma("man") == "man"
    # small real run
    res = run(n=6)
    assert res["population"]["n_common"] > 0
    print("[self-test] PASS")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--n", type=int, default=None)
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    res = run(n=(6 if a.smoke else a.n))
    _print(res)


if __name__ == "__main__":
    main()
