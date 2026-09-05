"""exp_commonnoun_scene_presence_ceiling_v1 -- ATTACK THE REAL CAPABILITY: does a SITUATION MODEL (scene
co-presence) make the ambiguous multi-person common-noun links uniquely recoverable, or does even a PERFECT
presence oracle leave them ambiguous (=> genuine world knowledge / the Phase-1 wall)?

The drill localized the gap: 82% of person common-noun links have 2-3 competing gender-compatible active
referents; the correct one is the SCENE-FOREGROUNDED entity. This cell measures the CEILING of the brain's
situation-model cue BEFORE building it -- using GOLD clusters as referents (so we measure the presence
SIGNAL, not our clustering errors) and the landed `hdlab.scene_segment.detect_scene_boundaries` to define
"who is present in the current scene." For every ambiguous person common-noun link (>1 compatible active
person cluster), measure whether restricting to SCENE-PRESENT clusters:
  - RECALL: is the gold antecedent even mentioned in the current scene? (if not, scene-restriction hurts)
  - UNIQUE: does scene-presence leave exactly ONE compatible cluster, and is it the gold antecedent?
  - SCENE+RECENCY: among scene-present compatibles, is the most-recent the gold antecedent?
vs the recency-only baseline (most-recent compatible active == gold antecedent). Decomposed by link type
(kinship_role / residual / name_antecedent / head_identical) so we know WHICH slice a presence model can
cross and which needs relational/world knowledge.

Glass-box, NO LLM. Reuses scene_segment (landed). hdlab READ-only. ASCII. own dir.
Run: .venv/Scripts/python.exe experiments/exp_commonnoun_scene_presence_ceiling_v1.py --self-test
"""
from __future__ import annotations
import os, sys
for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse, json, time
from collections import defaultdict
from datetime import datetime, timezone

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.coref import parse_litbank_conll, load_name_gender
from hdlab.scene_segment import parse_conll_sentences, detect_scene_boundaries
import experiments.exp_commonnoun_coref_diagnostic_v1 as DIAG
import experiments.exp_commonnoun_referent_linker_v1 as LK
import experiments.exp_commonnoun_linktype_decomposition_v1 as DEC

CONLL_DIR = os.path.join(_REPO, "data/litbank/coref_conll")
OUT_DIR = os.path.join(_REPO, "data/exp_commonnoun_scene_presence_ceiling_v1")
head_lemma = DIAG.head_lemma
is_name = DIAG.is_name


def _categorize(m, ante, gaz):
    hl = head_lemma(m["head"]); ahl = head_lemma(ante["head"])
    if ahl == hl:
        return "head_identical"
    if is_name(ante, gaz):
        return "name_antecedent"
    if DEC.wn_bridge(hl, ahl):
        return "wordnet_bridge"
    if hl in DEC.KINSHIP_ROLE or ahl in DEC.KINSHIP_ROLE:
        return "kinship_role"
    return "residual"


def analyze(docs_paths, gaz, windows=(1, 2, 3, 5, 8, 15)):
    """FAIR presence-ceiling: for every PERSON common-noun link (m, gold antecedent), sweep a tight
    PRESENCE WINDOW Wp (= 'on stage in the last Wp sentences'). At each Wp, candidates = compatible active
    person clusters mentioned within Wp. Report, over all links: recall (ante within Wp), unique-resolution
    (Wp leaves exactly 1 compatible AND it is ante), presence+recency (most-recent-in-Wp == ante), and mean
    candidate count. This measures whether a locality/presence model can UNIQUELY fix the referent."""
    cats = ["ALL", "head_identical", "name_antecedent", "wordnet_bridge", "kinship_role", "residual"]
    B = {W: {c: defaultdict(int) for c in cats} for W in windows}
    links = []   # (cat, ante_cluster, {W: (candidate_clusters_within_W)}, sent) collected per link
    for path in docs_paths:
        ms, n_sents = parse_litbank_conll(path, name_gender_map=gaz)
        by_cluster = defaultdict(list)
        for m in ms:
            by_cluster[m["cluster"]].append(m)
        cl_g = {}; cl_num = {}; cl_person = {}
        for c, cms in by_cluster.items():
            cl_g[c] = next((mm.get("gender") or mm.get("name_gender") for mm in cms
                            if (mm.get("gender") or mm.get("name_gender")) in ("masc", "fem")), None)
            cl_num[c] = "plur" if any(LK._num_of(mm) == "plur" for mm in cms if not mm["is_pronoun"]) else "sing"
            cl_person[c] = any((not mm["is_pronoun"]) and (LK.person_synset(head_lemma(mm["head"])) is not None
                                                           or is_name(mm, gaz)) for mm in cms) or \
                any(mm["head"] in DIAG.PERS_PRON for mm in cms)
        noms = sorted([m for m in ms if not m["is_pronoun"]], key=lambda m: m["midx"])
        prior_in_cluster = defaultdict(list)
        cl_last_sent = {}
        for m in noms:
            hl = head_lemma(m["head"]); g = m.get("gender") or m.get("name_gender"); num = LK._num_of(m)
            si = m["sent_idx"]
            person = LK.person_synset(hl) is not None or is_name(m, gaz)
            pri = prior_in_cluster.get(m["cluster"], [])
            if (not is_name(m, gaz)) and person and pri:
                ante_c = pri[-1]["cluster"]; cat = _categorize(m, pri[-1], gaz)
                for W in windows:
                    cand = [c for c, ls in cl_last_sent.items()
                            if cl_person.get(c) and (si - ls) <= W
                            and LK._gender_ok(g, cl_g.get(c)) and LK._number_ok(num, cl_num.get(c))]
                    ante_in = any(c == ante_c for c in cand)
                    uniq = len(cand) == 1
                    rec_pick = max(cand, key=lambda c: cl_last_sent[c]) if cand else None
                    for cc in ("ALL", cat):
                        b = B[W][cc]
                        b["n"] += 1
                        b["ante_in_window"] += int(ante_in)
                        b["unique"] += int(uniq)
                        b["unique_correct"] += int(uniq and cand[0] == ante_c)
                        b["presence_recency_correct"] += int(rec_pick == ante_c)
                        b["mean_cand_sum"] += len(cand)
            prior_in_cluster[m["cluster"]].append(m)
            if person:
                cl_last_sent[m["cluster"]] = si
    out = {}
    for W in windows:
        out[W] = {}
        for c in cats:
            b = B[W][c]; n = b["n"]
            if n == 0:
                continue
            out[W][c] = {"n": n, "recall_ante_in_window": round(b["ante_in_window"] / n, 4),
                         "presence_unique": round(b["unique"] / n, 4),
                         "presence_unique_correct": round(b["unique_correct"] / n, 4),
                         "presence_recency_correct": round(b["presence_recency_correct"] / n, 4),
                         "mean_candidates": round(b["mean_cand_sum"] / n, 2)}
    return out


def run(n=None):
    t0 = time.time(); os.makedirs(OUT_DIR, exist_ok=True)
    import glob
    paths = sorted(glob.glob(os.path.join(CONLL_DIR, "*.conll")))
    if n:
        paths = paths[:n]
    gaz = load_name_gender()
    res = {"n_docs": len(paths), "by_window": analyze(paths, gaz),
           "elapsed_s": round(time.time() - t0, 1)}
    with open(os.path.join(OUT_DIR, "metrics.json"), "w", encoding="ascii") as fh:
        json.dump({"anchor": "commonnoun_scene_presence_ceiling_v1", "results": res,
                   "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
    return res


def _print(res):
    print("=" * 100)
    print("PRESENCE-WINDOW CEILING on person common-noun links (%d docs) -- CAN a locality/presence model"
          % res["n_docs"])
    print("  UNIQUELY fix the referent? (GOLD referents; Wp = 'on stage in last Wp sentences')")
    print("  ALL links, sweeping the presence window Wp:")
    print("  %-4s %6s %14s %10s %14s %16s %12s" % ("Wp", "n", "recall(in-win)", "uniq", "uniq&correct",
                                                   "presence+recency", "mean_cand"))
    for W in sorted(res["by_window"]):
        s = res["by_window"][W].get("ALL")
        if not s:
            continue
        print("  %-4d %6d %14.3f %10.3f %14.3f %16.3f %12.2f"
              % (W, s["n"], s["recall_ante_in_window"], s["presence_unique"], s["presence_unique_correct"],
                 s["presence_recency_correct"], s["mean_candidates"]))
    # per-category at a mid window
    Wmid = 5 if 5 in res["by_window"] else sorted(res["by_window"])[len(res["by_window"]) // 2]
    print("  " + "-" * 96)
    print("  by category at Wp=%d (presence+recency correct | mean candidates):" % Wmid)
    for c in ("head_identical", "name_antecedent", "wordnet_bridge", "kinship_role", "residual"):
        s = res["by_window"][Wmid].get(c)
        if s:
            print("    %-16s n=%-5d presence+recency %.3f  mean_cand %.2f"
                  % (c, s["n"], s["presence_recency_correct"], s["mean_candidates"]))
    print("=" * 100)


def self_test():
    res = run(n=8)
    assert res["by_window"].get(5, {}).get("ALL", {}).get("n", 0) > 0
    print("[self-test] PASS (%d links at Wp=5 over 8 docs)" % res["by_window"][5]["ALL"]["n"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", dest="self_test")
    ap.add_argument("--n", type=int, default=None)
    a = ap.parse_args()
    if a.self_test:
        self_test(); return
    _print(run(n=a.n))


if __name__ == "__main__":
    main()
