"""Coverage of every candidate supervision source on (a) the 5,491 anchors and
(b) the 617 words of the licensed v1.7 matched-pair evaluation population.

Populations read off disk this session:
  scratch/anchors_5491_2026-08-18.json            <- scratch/sparse_code_real_task/real_cache.npz["anchors"]
  scratch/dsi_population_v17_full_2026-08-18.json <- data/exp_dissociation_score_instrument_v1/units.jsonl
                                                     unit_key "POPULATION|v1.7|full"

ASCII only. No LLM. Read-only over data/. data/foundation/ is NEVER touched.
"""
from __future__ import annotations

import csv
import glob
import gzip
import json
import os
import sys
from collections import Counter, defaultdict

REPO = "D:/AI/hd-instrument"
os.chdir(REPO)

ANCH = set(json.load(open("scratch/anchors_5491_2026-08-18.json")))
POP = json.load(open("scratch/dsi_population_v17_full_2026-08-18.json"))
EVAL = set(POP["all_words"])
P_PAIRS = [tuple(p[:2]) for p in POP["P"]]
S_PAIRS = [tuple(p[:2]) for p in POP["S"]]

print("anchors=%d  eval_words=%d  P_pairs=%d  S_pairs=%d" % (len(ANCH), len(EVAL), len(P_PAIRS), len(S_PAIRS)))
rows = []


def report(name, covered_words, pair_cov=None, note=""):
    a = len(covered_words & ANCH)
    e = len(covered_words & EVAL)
    rec = {"source": name, "anchors_covered": a, "anchors_pct": round(100.0 * a / len(ANCH), 1),
           "eval617_covered": e, "eval617_pct": round(100.0 * e / len(EVAL), 1), "note": note}
    if pair_cov is not None:
        rec.update(pair_cov)
    rows.append(rec)
    print("%-42s anchors %5d (%4.1f%%)   eval617 %4d (%4.1f%%)  %s" %
          (name, a, rec["anchors_pct"], e, rec["eval617_pct"], note))
    return rec


def load_col(path, wordcol, sep=None, enc="utf-8-sig", lower=True):
    out = set()
    with open(path, "r", encoding=enc, errors="replace", newline="") as fh:
        rd = csv.reader(fh, delimiter=sep) if sep else csv.reader(fh)
        hdr = next(rd, None)
        idx = wordcol if isinstance(wordcol, int) else hdr.index(wordcol)
        for r in rd:
            if len(r) <= idx:
                continue
            w = r[idx].strip()
            if lower:
                w = w.lower()
            if w:
                out.add(w)
    return out


# ------------------------------------------------------------------ human rating norms
report("Brysbaert concreteness (40k)",
       load_col("data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt", 0, sep="\t"),
       note="1 dim; human rating")
report("Warriner VAD (14k)",
       load_col("data/grounding_testbed/Ratings_Warriner_et_al.csv", 1),
       note="3 dims; human rating")
report("Kuperman AoA (51k)",
       load_col("data/grounding_testbed/AoA_51715_words.csv", 0),
       note="1 dim; human rating")
report("Lancaster sensorimotor (39,707)",
       load_col("data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv", 0),
       note="11 dims; human rating")
report("Binder (2016) ratings",
       load_col("data/corpora/binder/binder2016_ratings.csv", 1),
       note="65 dims; human rating")

# ------------------------------------------------------------------ CSKG
WN_RELS = {"/r/PartOf", "/r/MadeOf", "/r/MannerOf", "/r/Entails"}
cskg_all, cskg_clean, cskg_vg, cskg_at, cskg_fn, cskg_cn = set(), set(), set(), set(), set(), set()
deg_clean = Counter()
edges_total = edges_clean = 0
for f in sorted(glob.glob("data/cskg_foundation_v1/edges_shard_*.jsonl")):
    with open(f, encoding="utf-8") as fh:
        for line in fh:
            e = json.loads(line)
            s, o, rel, src = e["subject"], e["obj"], e["relation"], e["source"]
            edges_total += 1
            cskg_all.add(s); cskg_all.add(o)
            if src == "VG":
                cskg_vg.add(s); cskg_vg.add(o)
            elif src == "AT":
                cskg_at.add(s); cskg_at.add(o)
            elif src == "FN":
                cskg_fn.add(s); cskg_fn.add(o)
            elif src == "CN":
                cskg_cn.add(s); cskg_cn.add(o)
            if rel not in WN_RELS and "WN" not in src:
                edges_clean += 1
                cskg_clean.add(s); cskg_clean.add(o)
                deg_clean[s] += 1; deg_clean[o] += 1
print("CSKG edges total=%d  WordNet-free-at-origin=%d (%.2f%%)" %
      (edges_total, edges_clean, 100.0 * edges_clean / edges_total))
report("CSKG all nodes", cskg_all, note="%d edges" % edges_total)
report("CSKG WordNet-FREE-at-origin nodes", cskg_clean,
       note="%d edges; drops PartOf/MadeOf/MannerOf/Entails + any WN-labelled" % edges_clean)
report("CSKG Visual-Genome subset (CROSS-MODAL)", cskg_vg, note="image-derived object relations")
report("CSKG ATOMIC subset", cskg_at, note="social/event inference")
report("CSKG FrameNet subset", cskg_fn, note="frame-element relations")
report("CSKG ConceptNet subset", cskg_cn, note="crowd assertions")

# degree of eval words in the clean subgraph -- a 1-edge node supervises nothing
ev_deg = [deg_clean.get(w, 0) for w in sorted(EVAL)]
an_deg = [deg_clean.get(w, 0) for w in sorted(ANCH)]


def band(ds):
    return {"deg0": sum(1 for d in ds if d == 0), "deg1_4": sum(1 for d in ds if 1 <= d <= 4),
            "deg5_19": sum(1 for d in ds if 5 <= d <= 19), "deg20plus": sum(1 for d in ds if d >= 20),
            "median": sorted(ds)[len(ds) // 2]}


print("\nCSKG clean-subgraph DEGREE, eval 617:", band(ev_deg))
print("CSKG clean-subgraph DEGREE, anchors 5491:", band(an_deg))

# both members of a pair present AND both with degree>=5 (usable for a pairwise signal)
def pair_usable(pairs, mindeg):
    return sum(1 for a, b in pairs if deg_clean.get(a, 0) >= mindeg_ok(mindeg) and deg_clean.get(b, 0) >= mindeg)


def mindeg_ok(m):
    return m


print("SET_P pairs with BOTH members deg>=1 / >=5 in clean CSKG: %d / %d  (of %d)" %
      (pair_usable(P_PAIRS, 1), pair_usable(P_PAIRS, 5), len(P_PAIRS)))
print("SET_S pairs with BOTH members deg>=1 / >=5 in clean CSKG: %d / %d  (of %d)" %
      (pair_usable(S_PAIRS, 1), pair_usable(S_PAIRS, 5), len(S_PAIRS)))

# ------------------------------------------------------------------ eval benchmarks (validators)
def simlex_words():
    out = set()
    with open("data/encoder_eval_benchmarks/simlex999.txt", encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            p = line.split("\t")
            if len(p) >= 2:
                out.add(p[0].strip().lower()); out.add(p[1].strip().lower())
    return out


report("SimLex-999 vocabulary", simlex_words(), note="INDEPENDENT VALIDATOR, not supervision")

# ------------------------------------------------------------------ UD English EWT
ud_forms = Counter()
ud_sents = 0
for p in ["data/corpora/ud_english_ewt/en_ewt-ud-train.conllu",
          "data/corpora/ud_english_ewt/en_ewt-ud-test.conllu"]:
    with open(p, encoding="utf-8") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            if not line.strip():
                ud_sents += 1
                continue
            c = line.split("\t")
            if len(c) > 3 and "-" not in c[0]:
                ud_forms[c[2].lower() if c[2] != "_" else c[1].lower()] += 1
print("\nUD EWT: %d sentences, %d distinct lemmas, %d tokens" %
      (ud_sents, len(ud_forms), sum(ud_forms.values())))
report("UD EWT lemma vocabulary (parser TRAIN data)", set(ud_forms),
       note="supplies the PARSER, not per-anchor contexts")

json.dump(rows, open("scratch/supervision_coverage_2026-08-18.json", "w"), indent=1)
print("\nwrote scratch/supervision_coverage_2026-08-18.json")
