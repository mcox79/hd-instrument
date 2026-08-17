"""Verify the SimVerb-3500 ruler: integrity, usable n, CI width, IAA, SimLex overlap.

Scaffold-free witness for the 2026-08-17 ruler acquisition. Answers, from disk only:
  1. INTEGRITY  -- sha256 of each placed file matches the upstream Cambridge release.
  2. USABLE N   -- pairs whose BOTH members have a 12-dim grounded-norms row in our vocabulary.
  3. CI WIDTH   -- Spearman CI half-width at that n, and the projected MARGIN half-width,
                   compared against the +0.1452 effect from exp_verb_target_space_n222_v1.
  4. IAA        -- inter-annotator agreement RECOMPUTED from the released per-annotator matrix,
                   both the way that reproduces the paper's 84.0 and the way that gives 61.2.
  5. OVERLAP    -- unordered-pair overlap with SimLex-999's 222 verb pairs.

Run: .venv/Scripts/python.exe verification/verify_simverb_ruler_fitness.py
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import csv
import hashlib
import json
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)

BENCH = os.path.join(REPO, "data", "encoder_eval_benchmarks")
SIMVERB = os.path.join(BENCH, "simverb3500.txt")
SIMLEX = os.path.join(BENCH, "simlex999.txt")
ANNOT = os.path.join(BENCH, "simverb3520_annotator_ratings.csv")

# sha256 recorded at acquisition (2026-08-17) from the upstream zip, before placement.
EXPECTED_SHA256 = {
    "simverb3500.txt": "b58f68454cf9354b94ecd8bfd778ff2cc784a25fc7dca02bc695319ad2b4157e",
    "simverb3500_dev500.txt": "33f8998ac40478ab1e271cf10d2097c2e5de4d9780c6644ff054a601d892d791",
    "simverb3500_test3000.txt": "4e689048a940833239733e91a313715a49e9ecb958cd6c98069bbd103f1a066f",
}

# Measured facts from data/exp_verb_target_space_n222_v1/metrics.json (the licensing cell).
# NOT floors and NOT imported as a result -- used only to project POWER at a new n.
N222_N = 222
N222_MARGIN = 0.1452
N222_MARGIN_HALFWIDTH = (0.3379 - (-0.0496)) / 2.0  # paired-bootstrap CI on the MARGIN
N222_RHO_HALFWIDTH = (0.3841 - 0.1282) / 2.0        # bootstrap CI on the single rho


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rankdata_avg(a):
    """Average-rank transform (ties matter: annotator ratings are integers 0-6)."""
    a = np.asarray(a, dtype=np.float64)
    order = np.argsort(a, kind="mergesort")
    ranks = np.empty(len(a), dtype=np.float64)
    sa = a[order]
    i = 0
    while i < len(a):
        j = i
        while j + 1 < len(a) and sa[j + 1] == sa[i]:
            j += 1
        ranks[order[i:j + 1]] = 0.5 * (i + j) + 1.0
        i = j + 1
    return ranks


def spearman(x, y):
    rx, ry = rankdata_avg(x), rankdata_avg(y)
    rx = rx - rx.mean()
    ry = ry - ry.mean()
    d = np.sqrt((rx * rx).sum() * (ry * ry).sum())
    if d == 0:
        return float("nan")
    return float((rx * ry).sum() / d)


def load_simverb(path):
    """word1, word2, POS, score, relation -- tab separated, NO header line."""
    out = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            p = line.split("\t")
            out.append((p[0], p[1], p[2], float(p[3]), p[4]))
    return out


def load_simlex_verbs(path):
    """SimLex-999 HAS a header line. Return only the POS=='V' rows."""
    out = []
    with open(path, "r", encoding="utf-8") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    hdr = rows[0]
    i1, i2, ip, isc = (hdr.index("word1"), hdr.index("word2"),
                       hdr.index("POS"), hdr.index("SimLex999"))
    for r in rows[1:]:
        if not r:
            continue
        if r[ip] == "V":
            out.append((r[i1], r[i2], float(r[isc])))
    return out


def main():
    rep = {}

    # ---- 1. INTEGRITY ----------------------------------------------------------------
    integ = {}
    for fn, exp in EXPECTED_SHA256.items():
        p = os.path.join(BENCH, fn)
        got = sha256(p)
        integ[fn] = {"sha256": got, "matches_release": got == exp,
                     "bytes": os.path.getsize(p)}
        assert got == exp, f"CHECKSUM MISMATCH for {fn}: {got} != {exp}"
    rep["integrity"] = integ

    # ---- 2. PAIR COUNT + USABLE N ----------------------------------------------------
    sv = load_simverb(SIMVERB)
    pos = sorted(set(r[2] for r in sv))
    rep["simverb"] = {
        "pair_count": len(sv),
        "distinct_pos_tags": pos,
        "distinct_verbs": len(set([r[0] for r in sv] + [r[1] for r in sv])),
        "score_min": min(r[3] for r in sv),
        "score_max": max(r[3] for r in sv),
        "relations": {k: sum(1 for r in sv if r[4] == k)
                      for k in sorted(set(r[4] for r in sv))},
    }

    from hdlab import grounded_similarity as GS
    tab = GS._table()
    vocab = set(tab.keys())
    rep["our_vocabulary"] = {
        "source": "hdlab.grounded_similarity._table() -- the 12-dim Lancaster11+Brysbaert-Conc.M "
                  "table that exp_verb_target_space_n222_v1 uses as K1_OWN_NORMS",
        "size": len(vocab),
    }

    def usable(pairs):
        keep, drop_words = [], set()
        for r in pairs:
            a, b = r[0].lower(), r[1].lower()
            if a in vocab and b in vocab:
                keep.append(r)
            else:
                if a not in vocab:
                    drop_words.add(a)
                if b not in vocab:
                    drop_words.add(b)
        return keep, drop_words

    sv_use, sv_missing = usable(sv)
    n_usable = len(sv_use)
    rep["usable_n"] = {
        "headline_pairs": len(sv),
        "usable_pairs_both_members_in_our_vocab": n_usable,
        "retention_frac": round(n_usable / len(sv), 4),
        "distinct_verbs_missing_from_our_vocab": len(sv_missing),
        "example_missing": sorted(sv_missing)[:15],
    }

    # ---- 3. CI HALF-WIDTH AT THE USABLE N --------------------------------------------
    def rho_hw(n):
        return 1.96 / np.sqrt(n - 3)  # the convention the licensing cell reported

    # Empirical inflation from single-rho CI to MARGIN CI, measured on the n=222 run.
    infl_boot = N222_MARGIN_HALFWIDTH / N222_RHO_HALFWIDTH
    infl_analytic = N222_MARGIN_HALFWIDTH / float(rho_hw(N222_N))
    # Margin half-width scales as 1/sqrt(n-3): project from the measured n=222 value.
    proj_margin_hw = N222_MARGIN_HALFWIDTH * np.sqrt(N222_N - 3) / np.sqrt(n_usable - 3)

    rep["power"] = {
        "effect_to_resolve": N222_MARGIN,
        "n222_margin_ci_halfwidth_measured": round(N222_MARGIN_HALFWIDTH, 4),
        "n222_rho_ci_halfwidth_measured": round(N222_RHO_HALFWIDTH, 4),
        "margin_over_rho_inflation_vs_bootstrap": round(float(infl_boot), 4),
        "margin_over_rho_inflation_vs_analytic": round(float(infl_analytic), 4),
        "usable_n": n_usable,
        "single_rho_ci_halfwidth_at_usable_n": round(float(rho_hw(n_usable)), 4),
        "projected_margin_ci_halfwidth_at_usable_n": round(float(proj_margin_hw), 4),
        "margin_halfwidth_narrower_than_effect": bool(proj_margin_hw < N222_MARGIN),
        "power_gain_factor_vs_n222": round(float(np.sqrt((n_usable - 3) / (N222_N - 3))), 3),
        "min_n_for_margin_hw_below_effect": int(np.ceil(
            (N222_MARGIN_HALFWIDTH ** 2) * (N222_N - 3) / (N222_MARGIN ** 2) + 3)),
    }

    # ---- 4. IAA, RECOMPUTED FROM THE RELEASED PER-ANNOTATOR MATRIX -------------------
    rows, mat = [], []
    with open(ANNOT, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n").rstrip("\r")
            if not line:
                continue
            p = line.split(",")
            rows.append((p[0], p[1]))
            mat.append([int(v) for v in p[2:]])
    M = np.array(mat, dtype=np.float64)          # (pairs, annotators); -1 == not rated
    rated = M >= 0
    n_pairs_m, n_annot = M.shape

    # The consistency set: pairs rated by EVERY annotator (README: 20 such pairs).
    per_pair = rated.sum(axis=1)
    consistency_idx = np.where(per_pair == n_annot)[0]

    # (a) APIAA over the consistency set only -- every annotator pair fully overlaps here.
    def apiaa(idx, min_overlap):
        vals = []
        sub = M[idx, :]
        subr = rated[idx, :]
        for i in range(n_annot):
            for j in range(i + 1, n_annot):
                both = subr[:, i] & subr[:, j]
                if both.sum() < min_overlap:
                    continue
                r = spearman(sub[both, i], sub[both, j])
                if not np.isnan(r):
                    vals.append(r)
        return (float(np.mean(vals)) if vals else float("nan")), len(vals)

    apiaa_cons, npairs_cons = apiaa(consistency_idx, min_overlap=10)
    apiaa_all, npairs_all = apiaa(np.arange(n_pairs_m), min_overlap=10)

    # (b) AIAA: each annotator vs the MEAN of all OTHER annotators, over items they rated.
    aiaa_vals = []
    Msum = np.where(rated, M, 0.0).sum(axis=1)
    Mcnt = rated.sum(axis=1)
    for i in range(n_annot):
        sel = rated[:, i]
        if sel.sum() < 10:
            continue
        oth_sum = Msum[sel] - M[sel, i]
        oth_cnt = Mcnt[sel] - 1
        ok = oth_cnt > 0
        if ok.sum() < 10:
            continue
        r = spearman(M[sel, i][ok], oth_sum[ok] / oth_cnt[ok])
        if not np.isnan(r):
            aiaa_vals.append(r)

    rep["iaa"] = {
        "matrix_shape": [int(n_pairs_m), int(n_annot)],
        "consistency_set_size": int(len(consistency_idx)),
        "ratings_per_pair_median": float(np.median(per_pair)),
        "APIAA_consistency_set_only": round(apiaa_cons, 4),
        "APIAA_consistency_set_n_annotator_pairs": npairs_cons,
        "APIAA_all_pairs_min_overlap_10": round(apiaa_all, 4),
        "APIAA_all_pairs_n_annotator_pairs": npairs_all,
        "AIAA_vs_mean_of_others": round(float(np.mean(aiaa_vals)), 4),
        "AIAA_n_annotators": len(aiaa_vals),
    }

    # ---- 5. OVERLAP WITH SIMLEX'S 222 VERB PAIRS -------------------------------------
    slv = load_simlex_verbs(SIMLEX)
    sl_keys = set(frozenset((a.lower(), b.lower())) for a, b, _ in slv)
    sv_keys = set(frozenset((a.lower(), b.lower())) for a, b, _, _, _ in sv)
    inter = sl_keys & sv_keys

    sl_words = set(w.lower() for a, b, _ in slv for w in (a, b))
    sv_words = set(w.lower() for r in sv for w in (r[0], r[1]))

    # Do the two datasets agree on the pairs they share? (scale-free: Spearman)
    sl_map = {frozenset((a.lower(), b.lower())): s for a, b, s in slv}
    sv_map = {frozenset((r[0].lower(), r[1].lower())): r[3] for r in sv}
    shared = sorted(inter, key=lambda k: sorted(k))
    agree = (spearman([sl_map[k] for k in shared], [sv_map[k] for k in shared])
             if len(shared) >= 10 else None)

    rep["simlex_overlap"] = {
        "simlex_verb_pairs": len(slv),
        "simverb_pairs": len(sv),
        "shared_unordered_pairs": len(inter),
        "frac_of_simlex222_also_in_simverb": round(len(inter) / max(1, len(sl_keys)), 4),
        "frac_of_simverb3500_also_in_simlex": round(len(inter) / max(1, len(sv_keys)), 4),
        "simlex_verb_vocab": len(sl_words),
        "simverb_vocab": len(sv_words),
        "shared_vocab_words": len(sl_words & sv_words),
        "gold_score_spearman_on_shared_pairs": (round(agree, 4)
                                                if agree is not None else None),
        "example_shared": [sorted(k) for k in shared[:10]],
    }

    # Usable n for SimLex-V under the identical vocabulary filter, for a like-for-like read.
    slv_use = [r for r in slv if r[0].lower() in vocab and r[1].lower() in vocab]
    rep["simlex_overlap"]["simlex_verb_pairs_usable_in_our_vocab"] = len(slv_use)

    # SimVerb pairs that are usable AND disjoint from SimLex-V: the independent stratum.
    sv_use_disjoint = [r for r in sv_use
                       if frozenset((r[0].lower(), r[1].lower())) not in sl_keys]
    rep["usable_n"]["usable_pairs_disjoint_from_simlex_verbs"] = len(sv_use_disjoint)

    # ---- 6. STRATA: half-width on the SimLex-disjoint (independent) stratum -----------
    n_disj = len(sv_use_disjoint)
    rep["strata"] = {
        "PRIMARY_simverb_usable": {
            "n": n_usable,
            "projected_margin_ci_halfwidth": round(float(proj_margin_hw), 4)},
        "INDEPENDENT_simverb_usable_minus_simlex": {
            "n": n_disj,
            "projected_margin_ci_halfwidth": round(float(
                N222_MARGIN_HALFWIDTH * np.sqrt(N222_N - 3) / np.sqrt(n_disj - 3)), 4),
            "note": "SimLex-V pairs removed; safe to read alongside a SimLex-V replication "
                    "without double-counting the same 170 pairs."},
        "REPLICATION_simlex_verbs": {
            "n": len(slv_use),
            "projected_margin_ci_halfwidth": round(float(
                N222_MARGIN_HALFWIDTH * np.sqrt(N222_N - 3) / np.sqrt(len(slv_use) - 3)), 4),
            "note": "NEVER POOLED with SimVerb. Scored separately."},
    }

    # ---- 7. NORMS ON DISK FOR THESE ITEMS (the C1_PARTIAL feasibility question) -------
    def wordset_tsv(path, col=0, skip_header=True, sep="\t"):
        s = set()
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f):
                if skip_header and i == 0:
                    continue
                p = line.rstrip("\n").split(sep)
                if len(p) > col and p[col].strip():
                    s.add(p[col].strip().lower())
        return s

    def wordset_csv(path, colname, enc="utf-8", require_col=None):
        s = set()
        with open(path, "r", encoding=enc, errors="replace") as f:
            r = csv.reader(f)
            hdr = next(r)
            ci = hdr.index(colname)
            ri = hdr.index(require_col) if require_col else None
            for row in r:
                if len(row) > ci and row[ci].strip():
                    if ri is not None and (len(row) <= ri or not row[ri].strip()):
                        continue
                    s.add(row[ci].strip().lower())
        return s

    GT = os.path.join(REPO, "data", "grounding_testbed")
    sources = {
        "concreteness_brysbaert_Conc.M": wordset_tsv(
            os.path.join(GT, "Concreteness_ratings_Brysbaert_et_al_BRM.txt")),
        "aoa_kuperman_AoA_Kup": wordset_csv(
            os.path.join(GT, "AoA_51715_words.csv"), "Word"),
        "warriner_VAD": wordset_csv(
            os.path.join(GT, "Ratings_Warriner_et_al.csv"), "Word"),
        "binder535_IMG_imageability": wordset_csv(
            os.path.join(REPO, "data", "corpora", "binder", "binder2016_ratings.csv"),
            "Word", enc="utf-8-sig", require_col="IMG"),
        "simverb_own_BNCFREQ": set(
            l.split()[1].lower()
            for i, l in enumerate(open(os.path.join(BENCH, "simverb3500_stats.txt"),
                                       encoding="utf-8"))
            if i > 0 and len(l.split()) > 3),
    }
    norms = {}
    for nm, ws in sources.items():
        both = sum(1 for r in sv_use
                   if r[0].lower() in ws and r[1].lower() in ws)
        norms[nm] = {
            "source_words": len(ws),
            "simverb_pairs_both_members_covered": both,
            "frac_of_usable_stratum": round(both / max(1, n_usable), 4),
        }
    rep["norms_on_disk_for_these_items"] = norms
    rep["c1_partial_feasibility"] = {
        "concreteness_partial_runnable_now": norms[
            "concreteness_brysbaert_Conc.M"]["simverb_pairs_both_members_covered"] >= 3000,
        "log_frequency_partial_runnable_now": norms[
            "simverb_own_BNCFREQ"]["simverb_pairs_both_members_covered"] >= 3000,
        "imageability_partial_runnable_now": norms[
            "binder535_IMG_imageability"]["simverb_pairs_both_members_covered"] >= 3000,
        "imageability_blocker": "Binder-535 IMG is the ONLY imageability column on disk and it "
                                "covers a negligible number of SimVerb pairs. An imageability "
                                "partial requires acquiring the English Verbs Semantic Norms "
                                "Database (3,512 verbs, Behav Res Methods 2025). NOT on disk.",
    }

    print(json.dumps(rep, indent=2))
    out = os.path.join(REPO, "data", "simverb_ruler_fitness.json")
    with open(out, "w", encoding="utf-8", newline="") as f:
        json.dump(rep, f, indent=2)
    print("\n[written] " + out, file=sys.stderr)


if __name__ == "__main__":
    main()
