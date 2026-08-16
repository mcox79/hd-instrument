"""RUNTIME probe of candidate TARGET SPACES for the bridged-grounding cell.

Answers, per candidate: dimensionality, vocabulary size, SimLex-999 coverage,
VERB coverage (via SimLex POS field), ours-vs-external.
Reports what is ACTUALLY in each file, not what its name claims.
"""
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import csv
import io
import json
import sys
from collections import Counter

REPO = "D:/AI/hd-instrument"
sys.path.insert(0, REPO)

out = {}


def head_cols(path, n=3, delim=None):
    with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        first = f.readline()
    if delim is None:
        delim = "\t" if first.count("\t") > first.count(",") else ","
    return delim, [c.strip() for c in first.rstrip("\r\n").split(delim)]


def load_table(path, key_col_candidates, delim=None):
    delim, cols = head_cols(path, delim=delim)
    key = None
    for c in key_col_candidates:
        if c in cols:
            key = c
            break
    if key is None:
        key = cols[0]
    rows = {}
    with io.open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
        rd = csv.DictReader(f, delimiter=delim)
        for r in rd:
            w = (r.get(key) or "").strip().lower()
            if w:
                rows[w] = r
    return cols, key, rows


# ---------------- SimLex gold + POS ----------------
simlex_path = None
for cand in [
    REPO + "/data/simlex999/SimLex-999.txt",
    REPO + "/data/grounding_testbed/SimLex-999.txt",
    REPO + "/data/SimLex-999.txt",
]:
    if os.path.exists(cand):
        simlex_path = cand
        break
if simlex_path is None:
    # search
    for root, dirs, files in os.walk(REPO + "/data"):
        for fn in files:
            if fn.lower().startswith("simlex") and fn.lower().endswith(".txt"):
                simlex_path = os.path.join(root, fn)
                break
        if simlex_path:
            break

simlex_words = set()
simlex_pos = {}
simlex_pairs = []
if simlex_path:
    with io.open(simlex_path, "r", encoding="utf-8", errors="replace") as f:
        rd = csv.DictReader(f, delimiter="\t")
        for r in rd:
            w1 = r["word1"].strip().lower()
            w2 = r["word2"].strip().lower()
            pos = r.get("POS", "").strip()
            simlex_words.add(w1)
            simlex_words.add(w2)
            simlex_pos[w1] = pos
            simlex_pos[w2] = pos
            simlex_pairs.append((w1, w2, pos))
out["simlex"] = {
    "path": simlex_path,
    "n_pairs": len(simlex_pairs),
    "n_words": len(simlex_words),
    "pos_word_counts": dict(Counter(simlex_pos.values())),
    "pos_pair_counts": dict(Counter(p for _, _, p in simlex_pairs)),
}


def cov(vocab):
    """coverage of SimLex words overall and per POS"""
    hit = simlex_words & vocab
    per = Counter()
    tot = Counter()
    for w in simlex_words:
        tot[simlex_pos[w]] += 1
        if w in vocab:
            per[simlex_pos[w]] += 1
    pairs_both = sum(1 for a, b, _ in simlex_pairs if a in vocab and b in vocab)
    return {
        "simlex_words_covered": len(hit),
        "simlex_words_total": len(simlex_words),
        "per_pos_covered": {k: [per[k], tot[k]] for k in tot},
        "simlex_pairs_both_endpoints": pairs_both,
    }


# ---------------- A. Lancaster sensorimotor ----------------
p = REPO + "/data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv"
cols, key, rows = load_table(p, ["Word"])
mean_cols = [c for c in cols if c.endswith(".mean")]
out["A_lancaster"] = {
    "path": p,
    "key_col": key,
    "n_rows": len(rows),
    "n_cols": len(cols),
    "mean_cols": mean_cols,
    "n_mean_cols": len(mean_cols),
    "all_cols_sample": cols[:30],
    "coverage": cov(set(rows)),
    "ours_or_external": "EXTERNAL (Lynott/Connell/Brysbaert 2020, published norms)",
}

# ---------------- B. Brysbaert concreteness ----------------
p = REPO + "/data/grounding_testbed/Concreteness_ratings_Brysbaert_et_al_BRM.txt"
cols, key, rows = load_table(p, ["Word"])
out["B_concreteness"] = {
    "path": p,
    "key_col": key,
    "n_rows": len(rows),
    "cols": cols,
    "coverage": cov(set(rows)),
    "ours_or_external": "EXTERNAL (Brysbaert et al. 2014)",
}

# ---------------- C. Warriner VAD ----------------
p = REPO + "/data/grounding_testbed/Ratings_Warriner_et_al.csv"
cols, key, rows = load_table(p, ["Word"])
vad = [c for c in cols if c.endswith(".Mean.Sum")]
out["C_warriner_vad"] = {
    "path": p,
    "key_col": key,
    "n_rows": len(rows),
    "n_cols": len(cols),
    "vad_mean_cols": vad,
    "cols_sample": cols[:20],
    "coverage": cov(set(rows)),
    "ours_or_external": "EXTERNAL (Warriner, Kuperman & Brysbaert 2013)",
}

# ---------------- D. AoA ----------------
p = REPO + "/data/grounding_testbed/AoA_51715_words.csv"
cols, key, rows = load_table(p, ["Word"])
out["D_aoa"] = {
    "path": p,
    "key_col": key,
    "n_rows": len(rows),
    "cols": cols[:15],
    "coverage": cov(set(rows)),
    "ours_or_external": "EXTERNAL (Kuperman et al. 2012). NOT a meaning space - one developmental scalar.",
}

# ---------------- E. our live grounded space (runtime import) ----------------
try:
    import importlib
    gs = importlib.import_module("hdlab.grounded_similarity")
    info = {}
    for name in ["SENSORIMOTOR_COLS", "CONCRETENESS_COL", "GROUNDED_CAP"]:
        if hasattr(gs, name):
            info[name] = getattr(gs, name)
    if hasattr(gs, "coverage_stats"):
        info["coverage_stats"] = gs.coverage_stats()
    tbl = None
    if hasattr(gs, "_table"):
        tbl = gs._table()
        try:
            info["_table_n_words"] = len(tbl)
            k0 = next(iter(tbl))
            info["_table_example_key"] = k0
            info["_table_example_len"] = len(tbl[k0])
        except Exception as e:
            info["_table_probe_err"] = repr(e)
        vocabE = set(tbl)
        info["coverage"] = cov(vocabE)
    out["E_live_grounded_space"] = info
except Exception as e:
    out["E_live_grounded_space"] = {"ERROR": repr(e)}

# ---------------- F. relation assets (not vector spaces) ----------------
rel = {}
tp = REPO + "/data/thematic_relations_v1/thematic_edges_v1.pkl"
rel["thematic_edges_v1_exists"] = os.path.exists(tp)
if os.path.exists(tp):
    rel["thematic_edges_v1_bytes"] = os.path.getsize(tp)
rp = REPO + "/data/thematic_relations_v1/extraction_report_v1.json"
if os.path.exists(rp):
    try:
        rel["extraction_report"] = json.load(io.open(rp, "r", encoding="utf-8"))
    except Exception as e:
        rel["extraction_report_err"] = repr(e)
for name in ["cskg.tsv.gz"]:
    q = REPO + "/data/grounding_testbed/" + name
    if os.path.exists(q):
        rel[name] = os.path.getsize(q)
ak = REPO + "/data/atomic_kb"
if os.path.isdir(ak):
    rel["atomic_kb_files"] = sorted(
        (f, os.path.getsize(os.path.join(ak, f))) for f in os.listdir(ak)
    )
out["F_relation_assets"] = rel

print(json.dumps(out, indent=2, default=str))
