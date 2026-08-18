"""exp_bridged_grounding_from_core_v1 -- does a word grounded ONLY by bridging from an
already-grounded core carry real meaning?

PRE-REG: preregs/2026-08-16_bridged_grounding_from_core_v1.md (all thresholds fixed BEFORE any run;
this file never edits them). DESIGN BASIS: notes/drill_brain_word_meaning_acquisition_from_grounded_
core_bridging_2026-08-16.md PART D, with SEVEN deviations, each measured and each recorded in the
pre-reg section 3 and re-stated in metrics under "deviations_from_design".

THE THESIS: hide the hand-rated 12-dim Lancaster+Brysbaert norms for a held-out set of words;
rebuild each held-out word's code ONLY by an ADDITIVE d=1 bridge from words that still have norms;
score on the Phase-1 rho instrument against max(orthographic, hardened-frequency, scramble)
RECOMPUTED ON THE IDENTICAL STRATUM.

WHAT IS PINNED AND WHAT IS OURS (the brain-fidelity gate):
  PINNED   meaning lives in modality spokes bound by an anterior-temporal hub (lesion dissociation)
  PINNED   the angular gyrus computes meaning from the relational combination of known meanings,
           and ATL-AG coupling scales with combinatorial demand (Price et al. 2015 J Neurosci 35:3276)
  PINNED   that combination is approximately ADDITIVE (Baron & Osherson 2011 NeuroImage)
  PINNED   the early grounded core is order 10^3 early-acquired concrete words
  OURS     the specific additive form (unweighted mean / PMI-weighted mean) -- INVENTION UNDER TEST
  OURS     AoA <= 6.0 as the core cut (pinned to a developmental regularity by an INDEPENDENT asset)

TRAPS GUARDED, both re-verified by runtime in selftest(), not inherited:
  hdlab.grounded_similarity.grounded_similarity() SATURATES 76.18% of SimLex pairs onto two values
  (654 at 0.45, 107 at 0.0). It is NEVER the scorer here. The scorer is the raw 12-dim vector,
  L2-normalised, plain cosine -- what the Phase-1 ASSET_NORMS12 arm used.
  hdlab.gap_detector / hdlab.gap_driven_reader compute NO distance (0 occurrences of distance /
  frontier / hop / bridge in either source). The distance-to-frontier notion is BUILT here.

NO EXTERNAL LANGUAGE MODEL ANYWHERE IN THE RUNTIME PATH. No pretrained embedding table in any arm.
The CSKG arms are CEILING REFERENCE ONLY, on exactly the same footing as GloVe, and a pass on them
is never a wiring recommendation.

ASCII-only. CPU. No network. data/foundation/** is opened READ-ONLY and never written.
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import collections
import csv
import gzip
import json
import pickle
import re
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
for _p in (str(REPO), str(REPO / "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import exp_encoding_quality_instrument_v2 as INS          # THE INSTRUMENT, IMPORTED, NEVER EDITED
import exp_meaning_asset_fair_test_v1 as FT               # the Phase-1 verdict machinery, unchanged
from experiments._seed_checkpoint import get_output_dir, write_metrics
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units

ANCHOR_NAME = "bridged_grounding_from_core_v1"
CODE_VERSION = "v1.0"
PREREG = "preregs/2026-08-16_bridged_grounding_from_core_v1.md"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()
SMOKE = bool(_ARGS.smoke) or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
RUN_MODE = "smoke" if SMOKE else "full"

# ------------------------------------------------------------------------------------------
# PRE-REGISTERED CONSTANTS -- prereg section 6. NOT EDITED AFTER A RUN.
# ------------------------------------------------------------------------------------------
AOA_CORE_MAX = 6.0
T_MARGIN_MIN = FT.T_MARGIN_MIN                 # 0.05, inherited from the Phase-1 fair-test prereg
N_BOOT = 2000 if SMOKE else 10000
N_PERM = 400 if SMOKE else 2000
NULL_SEEDS = (7, 13, 17, 23, 29)
MORPH_PREFIX_MIN = 4
MORPH_TRIGRAM_COS_MAX = 0.40
HUB_INDEGREE_MAX = 10
POS_MIN_N = 25
BOOT_SEED = 20260816
ORTHO_DIMS = (12, 64, 256, 1024)
MIDDLE_BAND_FRAC = 0.05

SIMLEX = REPO / "data" / "encoder_eval_benchmarks" / "simlex999.txt"
AOA_CSV = REPO / "data" / "grounding_testbed" / "AoA_51715_words.csv"
CSKG_CACHE = REPO / "data" / "_cache_cskg_simlex_canonical_v1.pkl"
FACT_FILES = (
    "data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl",
    "data/foundation/reading_grounding_v3_definitional/definitional_facts.jsonl",
    "data/foundation/reading_grounding_v4_parsefix/definitional_facts_v4.jsonl",
)
# copied VERBATIM from experiments/exp_distinctiveness_weighted_composition_v1.py, which
# established it: a synonym/similarity dictionary would supply the answer SimLex is asking for.
LEXREL_DROP = frozenset({
    "/r/Synonym", "/r/Antonym", "/r/SimilarTo", "/r/RelatedTo", "/r/DistinctFrom",
    "/r/DerivedFrom", "/r/EtymologicallyRelatedTo", "/r/EtymologicallyDerivedFrom", "/r/FormOf",
})
_CANON_NODE = re.compile(r"^/c/en/([a-z]+)$")


# ------------------------------------------------------------------------------------------
# assets
# ------------------------------------------------------------------------------------------
def load_simlex_pos() -> List[Tuple[str, str, str, float]]:
    """(word1, word2, POS, gold). POS is SimLex's own A/N/V column."""
    out = []
    with open(SIMLEX, encoding="utf-8") as fh:
        rd = csv.reader(fh, delimiter="\t")
        next(rd)
        for r in rd:
            if len(r) >= 4:
                out.append((r[0].strip().lower(), r[1].strip().lower(), r[2].strip(), float(r[3])))
    return out


def load_aoa() -> Dict[str, float]:
    out = {}
    with open(AOA_CSV, encoding="utf-8", errors="replace") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        ic = head.index("AoA_Kup_lem")
        for r in rd:
            if len(r) > ic:
                try:
                    out[r[0].strip().lower()] = float(r[ic])
                except ValueError:
                    continue
    return out


def load_def_graph() -> Tuple[Dict[str, Dict[str, float]], Dict[str, int], int]:
    """Undirected definitional graph over head lemmas. Value = max PMI seen on that edge.
    Also returns the relation-pattern census (prereg deviation 4) and the row count."""
    from hdlab.reading_grounding_loop import normalize_lemma
    g: Dict[str, Dict[str, float]] = collections.defaultdict(dict)
    pat = collections.Counter()
    rows = 0
    for fp in FACT_FILES:
        p = REPO / fp
        if not p.exists():
            raise SystemExit(f"[fatal] missing fact file {fp}")
        with open(p, encoding="utf-8", errors="replace") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                rows += 1
                pat[(r.get("pattern") or "UNK").upper()] += 1
                subj = r.get("subject_head_lemma") or r.get("subject") or ""
                obj = r.get("object") or r.get("canonical_obj") or ""
                if not subj or not obj:
                    continue
                s = normalize_lemma(str(subj).split()[-1].lower())
                o = normalize_lemma(str(obj).split()[-1].lower())
                if not s or not o or s == o:
                    continue
                try:
                    pmi = float(r.get("pmi") or 0.0)
                except (TypeError, ValueError):
                    pmi = 0.0
                g[s][o] = max(g[s].get(o, -1e9), pmi)
                g[o][s] = max(g[o].get(s, -1e9), pmi)
    return dict(g), dict(pat), rows


def load_cskg_graphs(vocab: Set[str]) -> Tuple[Dict[str, Dict[str, float]],
                                               Dict[str, Dict[str, float]]]:
    """(all-relations, lexical-relations-dropped) neighbour maps for the SimLex vocabulary,
    read from the cache built by exp_distinctiveness_weighted_composition_v1."""
    if not CSKG_CACHE.exists():
        raise SystemExit(f"[fatal] missing CSKG cache {CSKG_CACHE}")
    with open(CSKG_CACHE, "rb") as f:
        cache = pickle.load(f)
    wf = cache["word_feats"]
    missing = sorted(w for w in vocab if w not in wf)
    if missing:
        raise SystemExit(f"[fatal] CSKG cache misses {len(missing)} SimLex words, e.g. {missing[:5]}")
    ga: Dict[str, Dict[str, float]] = collections.defaultdict(dict)
    gn: Dict[str, Dict[str, float]] = collections.defaultdict(dict)
    for w, feats in wf.items():
        for ft in feats:
            rel, node = ft.split("|", 1)
            m = _CANON_NODE.match(node)
            if not m:
                continue
            o = m.group(1)
            if o == w:
                continue
            ga[w][o] = 1.0
            if rel not in LEXREL_DROP:
                gn[w][o] = 1.0
    return dict(ga), dict(gn)


def corpus_counts() -> Dict[str, int]:
    """Frequency over the SAME corpus and byte budget the Phase-1 instrument used."""
    with open(INS.CORPUS, "rb") as f:
        raw = f.read(INS.CORPUS_BYTES)
    cut = raw.rfind(b"\n")
    if cut > 0:
        raw = raw[:cut]
    return collections.Counter(re.findall(r"[a-z]+", raw.decode("utf-8", errors="ignore").lower()))


# ------------------------------------------------------------------------------------------
# morphology blocking -- prereg control 1, THE DECISIVE ONE
# ------------------------------------------------------------------------------------------
def _tri(w: str) -> Set[str]:
    t = " " + w + " "
    return {t[i:i + 3] for i in range(len(t) - 2)} if len(t) >= 3 else {t}


def _tri_cos(a: str, b: str) -> float:
    sa, sb = _tri(a), _tri(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / ((len(sa) ** 0.5) * (len(sb) ** 0.5))


def morph_related(a: str, b: str) -> bool:
    """True if the pair could carry a SPELLING channel: shared long prefix, containment, or high
    character-trigram similarity. A bridge edge that fires this is DELETED in the blocked arms."""
    if a == b:
        return True
    if a in b or b in a:
        return True
    n = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        n += 1
    if n >= MORPH_PREFIX_MIN:
        return True
    return _tri_cos(a, b) >= MORPH_TRIGRAM_COS_MAX


# ------------------------------------------------------------------------------------------
# bridging
# ------------------------------------------------------------------------------------------
class Bridger:
    """Owns the hidden-norms table and every eligibility rule. The held-out rows are DELETED from
    the table this object reads, so a self-leak is a KeyError, not a silent pass (prereg G2)."""

    def __init__(self, raw: Dict[str, np.ndarray], held_out: Set[str],
                 partners: Dict[str, Set[str]]):
        self.hidden = {w: v for w, v in raw.items() if w not in held_out}
        self.held_out = set(held_out)
        self.partners = partners
        leak = sorted(w for w in held_out if w in self.hidden)
        if leak:
            raise SystemExit(f"[fatal] G2 self-leak: {len(leak)} held-out rows still in table")

    def eligible(self, w: str, n: str, sources: Set[str], morph_block: bool) -> bool:
        if n == w or n in self.held_out or n not in sources or n not in self.hidden:
            return False
        if n in self.partners.get(w, ()):          # never bridge to your own SimLex partner
            return False
        if morph_block and morph_related(w, n):
            return False
        return True

    def neighbours(self, w: str, graph: Dict[str, Dict[str, float]], sources: Set[str],
                   morph_block: bool, indeg: Optional[Dict[str, int]] = None
                   ) -> List[Tuple[str, float]]:
        nb = graph.get(w) or {}
        out = []
        for n, wt in nb.items():
            if not self.eligible(w, n, sources, morph_block):
                continue
            if indeg is not None and indeg.get(n, 0) >= HUB_INDEGREE_MAX:
                continue
            out.append((n, wt))
        return sorted(out)

    def mean_code(self, nbrs: Sequence[Tuple[str, float]], weighted: bool) -> np.ndarray:
        M = np.stack([self.hidden[n] for n, _ in nbrs]).astype(np.float64)
        if not weighted:
            return M.mean(axis=0)
        w = np.array([max(wt, 0.0) for _, wt in nbrs], dtype=np.float64)
        if w.sum() <= 0:
            return M.mean(axis=0)
        return (M * w[:, None]).sum(axis=0) / w.sum()


# ------------------------------------------------------------------------------------------
# scoring
# ------------------------------------------------------------------------------------------
def code_matrix(vocab: List[str], raw: Dict[str, np.ndarray],
                bridged: Dict[str, np.ndarray]) -> np.ndarray:
    X = np.zeros((len(vocab), 12), dtype=np.float32)
    for i, w in enumerate(vocab):
        X[i] = bridged[w] if w in bridged else raw[w]
    return INS._l2n(X)


def pair_cos(X: np.ndarray, ia: np.ndarray, ib: np.ndarray) -> np.ndarray:
    return np.einsum("ij,ij->i", X[ia], X[ib]).astype(np.float64)


def scramble_floor(X: np.ndarray, ia: np.ndarray, ib: np.ndarray, gold: np.ndarray,
                   seed: int) -> Dict:
    """PERMUTATION-CALIBRATED scramble floor: p95 of the null obtained by permuting the CODE TABLE's
    ROWS. Explicitly NOT a max of observed draws -- a prior scramble floor was a single draw sitting
    at the 98.6th percentile of its own null. The gold-permutation null is computed too and the
    HIGHER p95 is taken, which can only raise the bar."""
    n = X.shape[0]
    rhos = np.empty(N_PERM)
    for i in range(N_PERM):
        p = np.random.default_rng(seed + i).permutation(n)
        rhos[i] = INS._spearman(pair_cos(X[p], ia, ib), gold)
    rhos = rhos[np.isfinite(rhos)]
    p95_row = float(np.percentile(rhos, 95))
    obs = pair_cos(X, ia, ib)
    g_rng = np.random.default_rng(seed ^ 0xBEEF)
    gn = np.array([INS._spearman(obs, gold[g_rng.permutation(len(gold))]) for _ in range(N_PERM)])
    gn = gn[np.isfinite(gn)]
    p95_gold = float(np.percentile(gn, 95))
    p95 = max(p95_row, p95_gold)
    near_i = int(np.argmin(np.abs(rhos - p95)))
    near = pair_cos(X[np.random.default_rng(seed + near_i).permutation(n)], ia, ib)
    return {"p95": p95, "p95_row_permutation": p95_row, "p95_gold_permutation": p95_gold,
            "row_null_mean": float(rhos.mean()), "row_null_sd": float(rhos.std(ddof=1)),
            "n_perm": int(len(rhos)),
            "permutation_p_value": float((np.sum(rhos >= INS._spearman(obs, gold)) + 1)
                                         / (len(rhos) + 1)),
            "_partner": near}


def build_floors(vocab: List[str], ia: np.ndarray, ib: np.ndarray, gold: np.ndarray,
                 counts: Dict[str, int]) -> Dict[str, Dict]:
    """F_ORTHO (max over d) and F_FREQ (max over the four hardened channels), on THIS stratum."""
    out = {}
    best = None
    per_d = {}
    for d in ORTHO_DIMS:
        Xo = INS._l2n(INS.enc_orthographic(vocab, d, 7))
        c = pair_cos(Xo, ia, ib)
        r = INS._spearman(c, gold)
        per_d[f"d{d}"] = float(r)
        if best is None or r > best[0]:
            best = (r, c, d)
    out["F_ORTHO"] = {"rho": float(best[0]), "per_dim": per_d, "argmax_d": int(best[2]),
                      "_partner": best[1]}

    lf = np.array([np.log(counts.get(w, 0) + 1.0) for w in vocab], dtype=np.float64)
    la, lb = lf[ia], lf[ib]
    ch = {"FREQ_NEG_ABS_DIFF": -np.abs(la - lb), "FREQ_SUM": la + lb,
          "FREQ_MIN": np.minimum(la, lb),
          "FREQ_MIN_OVER_MAX": np.minimum(la, lb) / np.maximum(np.maximum(la, lb), 1e-12)}
    rh = {k: float(INS._spearman(v, gold)) for k, v in ch.items()}
    bk = max(rh, key=lambda k: rh[k])
    out["F_FREQ"] = {"rho": rh[bk], "per_channel": rh, "argmax_channel": bk, "_partner": ch[bk]}
    return out


def score_arm(name: str, X: np.ndarray, ia: np.ndarray, ib: np.ndarray, gold: np.ndarray,
              floors: Dict[str, Dict], seed: int) -> Dict:
    obs = pair_cos(X, ia, ib)
    sc = scramble_floor(X, ia, ib, gold, seed)
    cands = {"F_ORTHO": (floors["F_ORTHO"]["rho"], floors["F_ORTHO"]["_partner"]),
             "F_FREQ": (floors["F_FREQ"]["rho"], floors["F_FREQ"]["_partner"]),
             "F_SCRAMBLE": (sc["p95"], sc["_partner"])}
    bf = max(cands, key=lambda k: cands[k][0])
    diff = FT.boot_rho_diff(obs, cands[bf][1], gold, n_boot=N_BOOT, seed=BOOT_SEED)
    b = FT.band(diff["ci95"])
    per_floor = {}
    for k, (r, p) in cands.items():
        dd = FT.boot_rho_diff(obs, p, gold, n_boot=N_BOOT, seed=BOOT_SEED)
        per_floor[k] = {"floor_rho": float(r), "margin": dd, "band": FT.band(dd["ci95"])}
    clears = bool(b == "ABOVE" and diff["point"] >= T_MARGIN_MIN)
    middle = bool(clears and (diff["point"] - T_MARGIN_MIN)
                  < MIDDLE_BAND_FRAC * max(abs(diff["ci95"][1] - diff["ci95"][0]), 1e-12))
    return {"arm": name, "rho": FT.boot_rho(obs, gold, n_boot=N_BOOT, seed=BOOT_SEED),
            "strongest_floor": bf, "floor_rho_by_arm": {k: round(v[0], 4) for k, v in cands.items()},
            "margin_over_strongest_floor": diff, "band": b, "clears_floor": clears,
            "middle_band": middle,
            "scramble_null": {k: v for k, v in sc.items() if not k.startswith("_")},
            "DECOMPOSED_per_floor": per_floor, "_cos": obs}


def identity_axis(bridged: Dict[str, np.ndarray]) -> Dict:
    """IDENTITY axis. REPORTED SEPARATELY FROM STRUCTURE AND NEVER AVERAGED WITH IT. If bridging
    collapses many words onto one hub code, identity dies even when structure survives."""
    if not bridged:
        return {"n_bridged": 0, "status": "NOT_CONSTRUCTIBLE"}
    ws = sorted(bridged)
    M = INS._l2n(np.stack([bridged[w] for w in ws]).astype(np.float32))
    n = len(ws)
    distinct = len({tuple(np.round(M[i], 6)) for i in range(n)})
    out = {"n_bridged": n, "n_distinct_codes": distinct,
           "distinct_fraction": round(distinct / n, 4)}
    if n >= 2:
        S = M @ M.T
        iu = np.triu_indices(n, 1)
        out["mean_pairwise_cosine"] = float(S[iu].mean())
        out["frac_pairs_cosine_above_0.99"] = float((S[iu] > 0.99).mean())
    if n >= 8:
        out["recoverability_sigma1"] = float(INS.recoverability(M, min(n, 64), 1.0, 7))
        out["recoverability_sigma8"] = float(INS.recoverability(M, min(n, 64), 8.0, 7))
    return out


# ------------------------------------------------------------------------------------------
# self-tests -- run BEFORE anything else, every run
# ------------------------------------------------------------------------------------------
def selftest() -> Dict:
    print("[selftest] start", flush=True)
    ev = {}
    from hdlab import grounded_similarity as GS

    # 1. the norms asset is the one on disk
    tab = GS._table()
    assert len(tab) == 36810, f"norms table {len(tab)} != 36810"
    assert len(next(iter(tab.values()))) == 12, "norms are not 12-dim"
    ev["norms_table"] = {"n_words": len(tab), "n_dim": 12}

    # 2. TRAP 1 RE-VERIFIED BY RUNTIME, not inherited: grounded_similarity() is SATURATED.
    pairs = load_simlex_pos()
    vals = [GS.grounded_similarity(a, b) for a, b, _, _ in pairs]
    c = collections.Counter(round(v, 6) for v in vals if v is not None)
    frac2 = sum(n for _, n in c.most_common(2)) / len(vals)
    assert frac2 > 0.70, f"expected grounded_similarity saturated; top-2 mass {frac2:.4f}"
    ev["TRAP1_grounded_similarity_saturation"] = {
        "n_pairs": len(vals), "n_distinct": len(c), "top2": c.most_common(2),
        "fraction_on_two_values": round(frac2, 4),
        "consequence": "NEVER used as a scorer here; the scorer is raw 12-dim + plain cosine"}

    # 3. the scorer reproduces an INDEPENDENT recompute of the norms rho on the full 999
    vocab = sorted({w for p in pairs for w in p[:2]})
    raw = {w: np.asarray(tab[w], dtype=np.float64) for w in vocab}
    idx = {w: i for i, w in enumerate(vocab)}
    ia = np.array([idx[p[0]] for p in pairs]); ib = np.array([idx[p[1]] for p in pairs])
    gold = np.array([p[3] for p in pairs], dtype=np.float64)
    X = code_matrix(vocab, raw, {})
    rho_fast = INS._spearman(pair_cos(X, ia, ib), gold)
    ref = []
    for a, b, _, _ in pairs:
        va = np.asarray(tab[a], np.float64); vb = np.asarray(tab[b], np.float64)
        ref.append(float(va @ vb / (np.linalg.norm(va) * np.linalg.norm(vb))))
    rho_ref = INS._spearman(np.array(ref), gold)
    assert abs(rho_fast - rho_ref) < 1e-6, f"scorer {rho_fast} != independent recompute {rho_ref}"
    ev["G1_norms_rho_simlex999"] = {"vectorised": round(float(rho_fast), 6),
                                    "independent_recompute": round(float(rho_ref), 6)}

    # 4. bridge arithmetic is the additive mean it claims to be
    br = Bridger({"a": np.ones(12), "b": np.full(12, 3.0), "x": np.full(12, 99.0)},
                 {"x"}, {"x": {"a"}})
    assert "x" not in br.hidden, "held-out row survived into the hidden table"
    nb = br.neighbours("x", {"x": {"a": 1.0, "b": 1.0}}, {"a", "b"}, False)
    assert [n for n, _ in nb] == ["b"], f"SimLex-partner exclusion failed: {nb}"
    nb2 = br.neighbours("x", {"x": {"a": 1.0, "b": 1.0}}, {"a", "b"}, False)
    assert np.allclose(br.mean_code(nb2, False), 3.0), "unweighted mean wrong"
    nb3 = [("a", 1.0), ("b", 3.0)]
    assert np.allclose(br.mean_code(nb3, True), (1 * 1 + 3 * 3) / 4.0), "PMI-weighted mean wrong"

    # 5. the morphology blocker fires on the cases the design names, and not on unrelated words
    for a, b in (("biology", "biological"), ("reproduction", "production"),
                 ("photosynthesis", "synthesis"), ("cell", "cells")):
        assert morph_related(a, b), f"morphology blocker missed {a}/{b}"
    for a, b in (("dog", "cat"), ("tissue", "organ"), ("heart", "pump")):
        assert not morph_related(a, b), f"morphology blocker over-fired on {a}/{b}"
    ev["morphology_blocker"] = {"prefix_min": MORPH_PREFIX_MIN,
                                "trigram_cos_max": MORPH_TRIGRAM_COS_MAX,
                                "checked_fires": ["biology/biological", "reproduction/production",
                                                  "photosynthesis/synthesis", "cell/cells"],
                                "checked_does_not_fire": ["dog/cat", "tissue/organ", "heart/pump"]}

    # 6. the orthographic floor is a function of SPELLING ONLY and is not degenerate
    ws = [f"word{i}" for i in range(64)]
    O1 = INS.enc_orthographic(ws, 64, 7)
    O2 = INS.enc_orthographic(ws, 64, 999)
    assert np.allclose(O1, O2), "orthographic encoder depends on the seed, not only the string"
    assert len({tuple(np.round(r, 6)) for r in INS._l2n(O1)}) == 64, "orthographic floor degenerate"

    # 7. the bootstrap can fail and can fire
    g = np.random.default_rng(1)
    gg = g.random(200)
    good = gg + 0.05 * g.standard_normal(200)
    noise = g.standard_normal(200)
    assert FT.band(FT.boot_rho_diff(good, good.copy(), gg, n_boot=400)["ci95"]) == "NOT_SEPARATED"
    assert FT.band(FT.boot_rho_diff(good, noise, gg, n_boot=400)["ci95"]) == "ABOVE"

    # 8. the scramble floor's p95 sits ABOVE its own null centre
    sc = scramble_floor(X[:len(vocab)], ia[:200], ib[:200], gold[:200], 7)
    assert sc["p95"] > sc["row_null_mean"], "calibrated scramble floor below its null centre"
    ev["scramble_floor_selftest"] = {k: round(v, 4) for k, v in sc.items()
                                     if isinstance(v, float)}

    # 9. gap_detector / gap_driven_reader compute NO distance (runtime, not grep of a doc)
    import inspect
    tok = {}
    for mod in ("hdlab.gap_detector", "hdlab.gap_driven_reader"):
        src = inspect.getsource(__import__(mod, fromlist=["x"])).lower()
        tok[mod] = {t: src.count(t) for t in ("distance", "frontier", "hop", "bridge")}
        assert tok[mod]["distance"] == 0, f"{mod} unexpectedly mentions distance -- re-check reuse"
    ev["distance_metric_had_to_be_built"] = tok

    print("[selftest] ALL PASS", flush=True)
    return ev


# ------------------------------------------------------------------------------------------
# one configuration
# ------------------------------------------------------------------------------------------
def run_config(cfg_name: str, graph: Optional[Dict[str, Dict[str, float]]], sources: Set[str],
               morph_block: bool, hub_censor: bool, ctx: Dict) -> Dict:
    """Build every arm's code table for one (graph, source-set, control) configuration, define the
    stratum it induces, recompute all three floors ON THAT STRATUM, and score."""
    t0 = time.time()
    vocab, raw, pairs = ctx["vocab"], ctx["raw"], ctx["pairs"]
    idx, held_out, core = ctx["idx"], ctx["held_out"], ctx["core"]
    partners, counts, aoa = ctx["partners"], ctx["counts"], ctx["aoa"]
    br = Bridger(raw, held_out, partners)

    indeg = None
    if hub_censor and graph is not None:
        c = collections.Counter()
        for w in held_out:
            for n in (graph.get(w) or {}):
                if n in sources:
                    c[n] += 1
        indeg = dict(c)

    # ---- who is bridgeable, and the edges that make them so
    nbrs: Dict[str, List[Tuple[str, float]]] = {}
    edges_before = edges_after = 0
    if graph is not None:
        for w in sorted(held_out):
            allnb = [(n, wt) for n, wt in (graph.get(w) or {}).items()
                     if br.eligible(w, n, sources, False)]
            edges_before += len(allnb)
            keep = br.neighbours(w, graph, sources, morph_block, indeg)
            edges_after += len(keep)
            if keep:
                nbrs[w] = keep
    else:                                   # ORACLE config: every held-out word is bridgeable
        for w in sorted(held_out):
            nbrs[w] = []
    bridged_words = sorted(nbrs)

    # ---- the stratum this configuration induces: EXACTLY ONE endpoint bridged
    S = set(bridged_words)
    strat = [p for p in pairs if (p[0] in S) != (p[1] in S)]
    n = len(strat)
    res = {"config": cfg_name, "n_stratum": n, "n_bridged_words": len(bridged_words),
           "morph_block": morph_block, "hub_censor": hub_censor,
           "edges_before_control": edges_before, "edges_after_control": edges_after,
           "pos_counts": dict(collections.Counter(p[2] for p in strat)),
           "spearman_ci_halfwidth_approx": (round(1.96 / max(n - 3, 1) ** 0.5, 4) if n > 3 else None),
           "elapsed_s": None}
    if graph is not None and bridged_words:
        deg = [len(nbrs[w]) for w in bridged_words]
        tg = collections.Counter(nn for w in bridged_words for nn, _ in nbrs[w])
        res["bridge_degree"] = {"mean": round(float(np.mean(deg)), 3),
                                "median": int(np.median(deg)), "max": int(max(deg)),
                                "frac_degree_1": round(float(np.mean(np.array(deg) == 1)), 4)}
        res["distinct_bridge_targets"] = len(tg)
        res["top_bridge_targets"] = tg.most_common(8)
        if res["bridge_degree"]["median"] <= 1:
            res["ADDITIVITY_NOT_EXERCISED"] = (
                "median in-source degree <= 1: the 'mean over d=1 neighbours' is a SINGLE-NEIGHBOUR "
                "SUBSTITUTION here, so Baron & Osherson additivity is essentially untested by this "
                "configuration")
    if n < 10:
        res["status"] = "STRATUM_TOO_SMALL_TO_SCORE"
        res["elapsed_s"] = round(time.time() - t0, 1)
        return res

    ia = np.array([idx[p[0]] for p in strat]); ib = np.array([idx[p[1]] for p in strat])
    gold = np.array([p[3] for p in strat], dtype=np.float64)
    floors = build_floors(vocab, ia, ib, gold, counts)
    res["floors"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                     for k, v in floors.items()}

    # ---- ORACLE neighbour choice: nearest CORE word in the TRUE (hidden) norm space.
    # USES THE HELD-OUT WORD'S OWN HIDDEN NORMS. A ceiling on NEIGHBOUR CHOICE, never a mechanism.
    core_src = sorted(w for w in sources if w in raw and w not in held_out)
    CM = INS._l2n(np.stack([raw[w] for w in core_src]).astype(np.float32))

    def oracle_nbrs(w: str, k: int) -> List[Tuple[str, float]]:
        v = INS._l2n(raw[w][None, :].astype(np.float32))[0]
        s = CM @ v
        order = np.argsort(-s)
        out = []
        for j in order:
            cw = core_src[j]
            if cw == w or cw in partners.get(w, ()):
                continue
            out.append((cw, float(s[j])))
            if len(out) >= k:
                break
        return out

    # ---- arms
    arms: Dict[str, Dict[str, np.ndarray]] = {}
    arms["K1_OWN_NORMS"] = {}                                   # held-out words keep real norms
    arms["K2_ORACLE_BRIDGE"] = {w: br.mean_code(oracle_nbrs(w, 1), False) for w in bridged_words}
    arms["K2b_ORACLE_BRIDGE_MEAN3"] = {w: br.mean_code(oracle_nbrs(w, 3), False)
                                       for w in bridged_words}
    if graph is not None:
        arms["B_BRIDGE_MEAN"] = {w: br.mean_code(nbrs[w], False) for w in bridged_words}
        arms["B_BRIDGE_PMIW"] = {w: br.mean_code(nbrs[w], True) for w in bridged_words}

        # NULL 1: edges permuted WITHIN log-frequency deciles -> degree preserved, target
        # frequency band matched. NULL 2: uniformly random source-set targets, same degree.
        pool = core_src
        lf = np.array([np.log(counts.get(w, 0) + 1.0) for w in pool])
        dec = np.digitize(lf, np.percentile(lf, np.arange(10, 100, 10)))
        by_dec: Dict[int, List[str]] = collections.defaultdict(list)
        for w, dd in zip(pool, dec):
            by_dec[int(dd)].append(w)
        dec_of = {w: int(dd) for w, dd in zip(pool, dec)}
        for tag, seeds in (("N1_SHUFFLE_DEGREE_FREQ", NULL_SEEDS), ("N2_RANDOM_TARGET", NULL_SEEDS)):
            for s in seeds:
                rng = np.random.default_rng(s ^ 0x51F7)
                tbl = {}
                for w in bridged_words:
                    picks = []
                    for nn, _ in nbrs[w]:
                        cand = by_dec[dec_of.get(nn, 0)] if tag.startswith("N1") else pool
                        for _ in range(64):
                            c2 = cand[int(rng.integers(len(cand)))]
                            if br.eligible(w, c2, sources, False):
                                picks.append((c2, 1.0))
                                break
                    if picks:
                        tbl[w] = br.mean_code(picks, False)
                arms[f"{tag}|s{s}"] = tbl
    else:
        arms["N2_RANDOM_TARGET|s7"] = {}
        rng = np.random.default_rng(7 ^ 0x51F7)
        for w in bridged_words:
            for _ in range(64):
                c2 = core_src[int(rng.integers(len(core_src)))]
                if br.eligible(w, c2, sources, False):
                    arms["N2_RANDOM_TARGET|s7"][w] = br.mean_code([(c2, 1.0)], False)
                    break

    # ---- G3 arms-must-differ
    k1 = code_matrix(vocab, raw, {})
    gate_g3 = []
    for a in sorted(arms):
        if a == "K1_OWN_NORMS":
            continue
        if not arms[a]:
            continue
        Xa = code_matrix(vocab, raw, arms[a])
        gate_g3.append({"arm": a, "differs_from_K1": bool(not np.allclose(Xa, k1))})
    res["G3_arms_must_differ"] = gate_g3
    res["G3_passed"] = all(g["differs_from_K1"] for g in gate_g3) if gate_g3 else False

    # ---- score
    rows = {}
    cos_by_arm = {}
    for a in sorted(arms):
        if a != "K1_OWN_NORMS" and not arms[a]:
            rows[a] = {"arm": a, "status": "NO_BRIDGE_PRODUCED"}
            continue
        Xa = code_matrix(vocab, raw, arms[a])
        r = score_arm(a, Xa, ia, ib, gold, floors, seed=int(abs(hash(cfg_name + a)) % 100000) + 11)
        cos_by_arm[a] = r.pop("_cos")
        r["IDENTITY"] = identity_axis(arms[a]) if arms[a] else identity_axis(
            {w: raw[w] for w in bridged_words})
        rows[a] = r

    # ---- null floors: the MAX draw, never the mean
    for tag in ("N1_SHUFFLE_DEGREE_FREQ", "N2_RANDOM_TARGET"):
        ks = [k for k in rows if k.startswith(tag + "|") and "rho" in rows[k]]
        if not ks:
            continue
        best = max(ks, key=lambda k: rows[k]["rho"]["point"])
        res.setdefault("null_floors", {})[tag] = {
            "n_draws": len(ks), "max_draw_arm": best,
            "rho_max": rows[best]["rho"]["point"],
            "rho_mean": float(np.mean([rows[k]["rho"]["point"] for k in ks])),
            "policy": "the NULL FLOOR IS THE MAX DRAW, never the mean"}
        for a in list(rows):
            if a.startswith(("K", "B")) and "rho" in rows[a]:
                dd = FT.boot_rho_diff(cos_by_arm[a], cos_by_arm[best], gold,
                                      n_boot=N_BOOT, seed=BOOT_SEED)
                rows[a].setdefault("vs_nulls", {})[tag] = {"margin": dd, "band": FT.band(dd["ci95"])}

    # ---- retention fraction + POS strata, for every bridge/known-answer arm
    k1c = cos_by_arm.get("K1_OWN_NORMS")
    rho_k1 = rows["K1_OWN_NORMS"]["rho"]["point"] if "K1_OWN_NORMS" in rows else float("nan")
    pos_of = np.array([p[2] for p in strat])
    for a in list(rows):
        if "rho" not in rows[a] or a == "K1_OWN_NORMS":
            continue
        dd = FT.boot_rho_diff(cos_by_arm[a], k1c, gold, n_boot=N_BOOT, seed=BOOT_SEED)
        rows[a]["RETENTION_vs_K1"] = {
            "rho_arm": rows[a]["rho"]["point"], "rho_K1": rho_k1,
            "retention_fraction": (rows[a]["rho"]["point"] / rho_k1
                                   if rho_k1 not in (0.0,) and rho_k1 == rho_k1 else None),
            "paired_difference": dd, "band": FT.band(dd["ci95"])}
    for a in list(rows):
        if "rho" not in rows[a]:
            continue
        ps = {}
        for tag in ("N", "V", "A"):
            m = pos_of == tag
            k = int(m.sum())
            if k < POS_MIN_N:
                ps[tag] = {"n": k, "status": "NOT_CONSTRUCTIBLE"}
                continue
            ps[tag] = {"n": k, "rho": FT.boot_rho(cos_by_arm[a][m], gold[m],
                                                  n_boot=N_BOOT, seed=BOOT_SEED)}
        rows[a]["POS_STRATA"] = ps

    # ---- G0 POWER GATE: can the known-answer arm see meaning at this n at all?
    k1row = rows.get("K1_OWN_NORMS", {})
    res["G0_power_gate"] = {
        "K1_clears_floor": bool(k1row.get("clears_floor")),
        "K1_rho": k1row.get("rho", {}).get("point"),
        "K1_margin": k1row.get("margin_over_strongest_floor", {}).get("point"),
        "K1_band": k1row.get("band"),
        "rule": ("if the KNOWN-ANSWER arm does not clear this stratum's floor, the instrument "
                 "cannot resolve meaning at this n and every bridge arm here is POWER_INSUFFICIENT, "
                 "never FAIL")}
    if not res["G0_power_gate"]["K1_clears_floor"]:
        for a in rows:
            if a.startswith(("B", "K2")) and "rho" in rows[a]:
                rows[a]["verdict_for_this_arm"] = "POWER_INSUFFICIENT"
    else:
        for a in rows:
            if a.startswith(("B", "K2")) and "rho" in rows[a]:
                rows[a]["verdict_for_this_arm"] = (
                    "MIDDLE_BAND" if rows[a].get("middle_band")
                    else ("CLEARS_FLOOR" if rows[a]["clears_floor"] else "DOES_NOT_CLEAR_FLOOR"))

    res["arms"] = rows
    res["elapsed_s"] = round(time.time() - t0, 1)
    print(f"[cfg] {cfg_name:<34} n={n:<4} bridged={len(bridged_words):<4} "
          f"G0={'PASS' if res['G0_power_gate']['K1_clears_floor'] else 'FAIL'} "
          f"({res['elapsed_s']}s)", flush=True)
    return res


# ------------------------------------------------------------------------------------------
# order-effects arms (A5: nearest-frontier ordering)
# ------------------------------------------------------------------------------------------
def run_order_effects(graph: Dict[str, Dict[str, float]], sources: Set[str], ctx: Dict,
                      tag: str) -> Dict:
    """O1 frozen core one pass | O2 iterative nearest-frontier, AoA earliest-first | O3 identical
    iteration, randomised order. All three are scored on the SAME stratum -- the words O1 can
    reach -- so the only variable is the ORDER in which codes become available as sources."""
    vocab, raw, pairs = ctx["vocab"], ctx["raw"], ctx["pairs"]
    idx, held_out, counts = ctx["idx"], ctx["held_out"], ctx["counts"]
    partners, aoa = ctx["partners"], ctx["aoa"]
    br = Bridger(raw, held_out, partners)

    d1 = sorted(w for w in held_out if br.neighbours(w, graph, sources, False))
    # BFS closure: how far does iteration actually reach on this graph?
    frontier = set(sources) | set(d1)
    rounds = [len(d1)]
    admitted = list(d1)
    for _ in range(6):
        new = sorted(w for w in held_out
                     if w not in frontier and any(
                         n in frontier and br.eligible(w, n, frontier, False)
                         for n in (graph.get(w) or {})))
        if not new:
            break
        rounds.append(len(new))
        frontier |= set(new)
        admitted.extend(new)

    def bridge_ordered(order: Sequence[str]) -> Dict[str, np.ndarray]:
        avail = set(sources)
        codes: Dict[str, np.ndarray] = {}
        live = dict(br.hidden)
        b2 = Bridger(raw, held_out, partners)
        b2.hidden = live
        for w in order:
            nb = [(n, wt) for n, wt in (graph.get(w) or {}).items()
                  if n in avail and n in live and n != w and n not in partners.get(w, ())]
            if not nb:
                continue
            codes[w] = b2.mean_code(sorted(nb), False)
            live[w] = codes[w]          # ADMIT to the frontier -- this is the whole point of O2
            avail.add(w)
        return codes

    o1 = {w: br.mean_code(br.neighbours(w, graph, sources, False), False) for w in d1}
    aoa_order = sorted(d1, key=lambda w: (aoa.get(w, 99.0), w))
    o2 = bridge_ordered(aoa_order)
    o3s = {}
    for s in NULL_SEEDS:
        rng = np.random.default_rng(s ^ 0x1234)
        perm = list(d1)
        rng.shuffle(perm)
        o3s[s] = bridge_ordered(perm)

    common = sorted(set(o1) & set(o2) & set.intersection(*[set(v) for v in o3s.values()]))
    S = set(common)
    strat = [p for p in pairs if (p[0] in S) != (p[1] in S)]
    out = {"graph": tag, "d1_count": len(d1), "admissions_per_round": rounds,
           "closure_size": len(admitted), "n_common_words": len(common),
           "n_stratum": len(strat),
           "note": ("O1 and O2 differ ONLY where a d1 word can bridge from an EARLIER-admitted d1 "
                    "word; if the graph has no such edge the arms are identical by construction")}
    if len(strat) < 10:
        out["status"] = "STRATUM_TOO_SMALL_TO_SCORE"
        return out
    ia = np.array([idx[p[0]] for p in strat]); ib = np.array([idx[p[1]] for p in strat])
    gold = np.array([p[3] for p in strat], dtype=np.float64)
    floors = build_floors(vocab, ia, ib, gold, counts)
    tables = {"O1_ONESHOT_D1": {w: o1[w] for w in common},
              "O2_ITER_NEAREST": {w: o2[w] for w in common}}
    for s, t in o3s.items():
        tables[f"O3_ITER_ARBITRARY|s{s}"] = {w: t[w] for w in common}
    rows, cs = {}, {}
    for a, tb in sorted(tables.items()):
        X = code_matrix(vocab, raw, tb)
        r = score_arm(a, X, ia, ib, gold, floors, seed=int(abs(hash(tag + a)) % 100000) + 3)
        cs[a] = r.pop("_cos")
        r["IDENTITY"] = identity_axis(tb)
        rows[a] = r
    o3k = [k for k in rows if k.startswith("O3_")]
    best3 = max(o3k, key=lambda k: rows[k]["rho"]["point"])
    for a in ("O2_ITER_NEAREST", "O1_ONESHOT_D1"):
        dd = FT.boot_rho_diff(cs[a], cs[best3], gold, n_boot=N_BOOT, seed=BOOT_SEED)
        rows[a]["vs_O3_max_draw"] = {"vs": best3, "margin": dd, "band": FT.band(dd["ci95"])}
    d21 = FT.boot_rho_diff(cs["O2_ITER_NEAREST"], cs["O1_ONESHOT_D1"], gold,
                           n_boot=N_BOOT, seed=BOOT_SEED)
    out["O2_vs_O1"] = {"margin": d21, "band": FT.band(d21["ci95"])}
    out["O1_equals_O2_bitwise"] = bool(all(
        np.allclose(tables["O1_ONESHOT_D1"][w], tables["O2_ITER_NEAREST"][w]) for w in common))
    out["arms"] = rows
    out["floors"] = {k: {kk: vv for kk, vv in v.items() if not kk.startswith("_")}
                     for k, v in floors.items()}
    return out


# ------------------------------------------------------------------------------------------
def main() -> int:
    t_start = time.time()
    ev = selftest()
    if _ARGS.self_test:
        print("SELFTEST_ONLY_OK")
        return 0

    out_dir = get_output_dir(ANCHOR_NAME + ("_smoke" if SMOKE else ""))
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[cfg] mode={RUN_MODE} N_BOOT={N_BOOT} N_PERM={N_PERM} out={out_dir}", flush=True)

    from hdlab import grounded_similarity as GS
    tab = GS._table()
    pairs = load_simlex_pos()
    vocab = sorted({w for p in pairs for w in p[:2]})
    for w in vocab:
        if w not in tab:
            raise SystemExit(f"[fatal] SimLex word {w} has no norms")
    # the WHOLE norms table is the potential source pool, so DEF_ANYNORM is not silently
    # narrowed to the SimLex vocabulary
    raw = {w: np.asarray(v, dtype=np.float64) for w, v in tab.items()}
    idx = {w: i for i, w in enumerate(vocab)}
    partners: Dict[str, Set[str]] = collections.defaultdict(set)
    for a, b, _, _ in pairs:
        partners[a].add(b)
        partners[b].add(a)

    aoa = load_aoa()
    core = {w for w, v in aoa.items() if v <= AOA_CORE_MAX and w in tab}
    held_out = {w for w in vocab if w not in core}

    def_graph, pat_census, def_rows = load_def_graph()
    cskg_all, cskg_nolex = load_cskg_graphs(set(vocab))
    counts = corpus_counts()
    print(f"[assets] core={len(core)} held_out={len(held_out)} def_nodes={len(def_graph)} "
          f"def_rows={def_rows} cskg_nolex_nodes={len(cskg_nolex)}", flush=True)

    ctx = {"vocab": vocab, "raw": raw, "pairs": pairs, "idx": idx, "held_out": held_out,
           "core": core, "partners": partners, "counts": counts, "aoa": aoa}

    norms_only = {w for w in tab if w not in held_out}
    CONFIGS = [
        # name, graph, sources, morph_block, hub_censor
        ("PRIMARY_DEF_CORE", def_graph, core, False, False),
        ("PRIMARY_DEF_CORE_MORPHBLOCK", def_graph, core, True, False),
        ("PRIMARY_DEF_CORE_HUBCENSOR", def_graph, core, False, True),
        ("DEF_ANYNORM", def_graph, norms_only, False, False),
        ("DEF_ANYNORM_MORPHBLOCK", def_graph, norms_only, True, False),
        ("CEILING_CSKG_NOLEXREL_CORE", cskg_nolex, core, False, False),
        ("CEILING_CSKG_NOLEXREL_CORE_MORPHBLOCK", cskg_nolex, core, True, False),
        ("CEILING_CSKG_ALL_CORE_CONTAMINATED", cskg_all, core, False, False),
        ("ORACLE_ALL_HELDOUT", None, core, False, False),
    ]

    done = completed_units(str(out_dir))
    units = load_units(str(out_dir))
    results = {}
    for name, g, src, mb, hc in CONFIGS:
        key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, name)
        if key in done and key in units:
            results[name] = units[key]
            print(f"[cfg] {name} RESUMED", flush=True)
            continue
        r = run_config(name, g, set(src), mb, hc, ctx)
        record_unit(str(out_dir), key, r)
        results[name] = r

    order = {}
    for tag, g, src in (("DEF_CORE", def_graph, core),
                        ("CSKG_NOLEXREL_CORE", cskg_nolex, core)):
        key = unit_key(ANCHOR_NAME, CODE_VERSION, RUN_MODE, "ORDER_" + tag)
        if key in done and key in units:
            order[tag] = units[key]
            continue
        o = run_order_effects(g, set(src), ctx, tag)
        record_unit(str(out_dir), key, o)
        order[tag] = o
        print(f"[order] {tag} rounds={o.get('admissions_per_round')} n={o.get('n_stratum')} "
              f"O1==O2 {o.get('O1_equals_O2_bitwise')}", flush=True)

    # ---------------- verdict ----------------
    P = results["PRIMARY_DEF_CORE"]
    parm = P.get("arms", {}).get("B_BRIDGE_MEAN", {})
    pmb = results["PRIMARY_DEF_CORE_MORPHBLOCK"].get("arms", {}).get("B_BRIDGE_MEAN", {})
    g0 = bool(P.get("G0_power_gate", {}).get("K1_clears_floor"))
    g3 = bool(P.get("G3_passed"))
    if not g3:
        verdict = "INVALID_VALIDITY_GATE_FAILED"
    elif not g0:
        verdict = "POWER_INSUFFICIENT_ON_THE_PRIMARY_STRATUM"
    elif parm.get("clears_floor") and pmb.get("clears_floor") and not parm.get("middle_band"):
        verdict = "BRIDGED_CODES_CARRY_MEANING_CLEARS_THE_FLOOR"
    elif parm.get("clears_floor"):
        verdict = "MIDDLE_BAND_CLEARS_UNBLOCKED_ONLY"
    else:
        verdict = "BRIDGED_CODES_DO_NOT_CLEAR_THE_FLOOR_ON_OUR_GRAPH"

    ceil = results["CEILING_CSKG_NOLEXREL_CORE"].get("arms", {}).get("B_BRIDGE_MEAN", {})
    orc = results["ORACLE_ALL_HELDOUT"].get("arms", {}).get("K2_ORACLE_BRIDGE", {})
    dissociation = {
        "our_graph_B_BRIDGE_MEAN": parm.get("verdict_for_this_arm"),
        "ceiling_cskg_nolexrel": ceil.get("verdict_for_this_arm"),
        "oracle_neighbour_choice": orc.get("verdict_for_this_arm"),
        "reading": None}
    if orc.get("clears_floor") and not parm.get("clears_floor"):
        dissociation["reading"] = ("OUR RELATIONS ARE THE LIMITER, NOT THE BRIDGING IDEA. Next step "
                                   "is extraction yield and a thematic relation channel, not a "
                                   "different operator.")
    elif not orc.get("clears_floor") and not parm.get("clears_floor"):
        dissociation["reading"] = ("additive single-hop bridging does not carry meaning in the "
                                   "12-dim CONCRETE-SPOKE space even with a perfect neighbour. Next "
                                   "step is the TARGET SPACE (add the Warriner emotion/interoception "
                                   "spoke) or the operator, NOT the graph.")
    elif parm.get("clears_floor"):
        dissociation["reading"] = "bridged codes clear the floor on our own graph; see PASS band."

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE, "code_version": CODE_VERSION,
        "prereg": PREREG, "verdict": verdict,
        "verdict_msg": ("Does a word grounded ONLY by bridging from an already-grounded core carry "
                        "measurable meaning on the rho instrument, against floors recomputed on the "
                        "identical stratum? -> " + verdict),
        "summary": verdict,
        "HOW_TO_READ_A_NULL": (
            "The brain does this, so the capability is DEMONSTRATED. A null here is a fact about "
            "OUR IMPLEMENTATION, never about the capability. See prereg section 8 and "
            "named_divergences_from_the_biology below."),
        "config": {"AOA_CORE_MAX": AOA_CORE_MAX, "T_MARGIN_MIN": T_MARGIN_MIN, "N_BOOT": N_BOOT,
                   "N_PERM": N_PERM, "NULL_SEEDS": list(NULL_SEEDS),
                   "MORPH_PREFIX_MIN": MORPH_PREFIX_MIN,
                   "MORPH_TRIGRAM_COS_MAX": MORPH_TRIGRAM_COS_MAX,
                   "HUB_INDEGREE_MAX": HUB_INDEGREE_MAX, "POS_MIN_N": POS_MIN_N,
                   "ORTHO_DIMS": list(ORTHO_DIMS), "BOOT_SEED": BOOT_SEED},
        "assets": {"simlex": "data/encoder_eval_benchmarks/simlex999.txt",
                   "norms": "hdlab/grounded_similarity.py (36,810 words x 12 dims)",
                   "aoa": "data/grounding_testbed/AoA_51715_words.csv (AoA_Kup_lem)",
                   "definitional_graph": list(FACT_FILES),
                   "cskg_cache": "data/_cache_cskg_simlex_canonical_v1.pkl (CEILING REFERENCE)",
                   "corpus_for_frequency": str(INS.CORPUS.relative_to(REPO)).replace("\\", "/"),
                   "corpus_bytes": INS.CORPUS_BYTES},
        "population": {"n_simlex_pairs": len(pairs), "n_distinct_words": len(vocab),
                       "n_core_AoA_le_6": len(core), "n_core_in_simlex": len(vocab) - len(held_out),
                       "n_held_out_simlex": len(held_out),
                       "definitional_graph_nodes": len(def_graph),
                       "definitional_graph_rows": def_rows,
                       "relation_pattern_census": pat_census},
        "selftest_evidence": ev,
        "deviations_from_design": {
            "1_PRIMARY_STRATUM_IS_47_NOT_392": (
                "the design's n=392 counted SimLex pairs with >=1 endpoint having ANY normed "
                "definitional neighbour -- a coverage statistic over ALL SimLex words, not a "
                "held-out stratum, and not restricted to the AoA<=6.0 core the design specifies. "
                "Re-measured under the actual experiment: 37 held-out words bridgeable, n=47. The "
                "design's n=66 both-endpoints stratum is n=4. Spearman CI half-width ~0.30 at n=47."),
            "2_POWERED_COMPANION_STRATA_ADDED": (
                "DEF_ANYNORM (n~124), CEILING_CSKG_NOLEXREL (n~247), CEILING_CSKG_ALL (n~414, "
                "CONTAMINATED), ORACLE (n~410) so the cell is informative regardless of the primary"),
            "3_ORACLE_CANNOT_USE_THE_GOLD": (
                "the design's 'CORE word with the highest GOLD similarity' is, for a held-out word, "
                "essentially its own SimLex partner -- the other endpoint of the pair being scored. "
                "Using it manufactures the result and violates leakage control C5. The oracle is "
                "taken over the TARGET SPACE instead and USES THE HELD-OUT WORD'S OWN HIDDEN NORMS. "
                "It is a ceiling on NEIGHBOUR CHOICE, never a mechanism, and can never be wired."),
            "4_ATL_VS_AG_TAXONOMIC_THEMATIC_NOT_CONSTRUCTIBLE": (
                "all five extracted relation patterns are taxonomic-definitional (COPULA 2006, "
                "APPOSITIVE 1521, CALLED 1303, GLOSSARY_COLON 944, REFERS_TO 25). There is no "
                "thematic family, so the pinned ATL/AG dissociation cannot be tested here. B2 is "
                "retained as an honestly-relabelled PMI-weighted additive bridge."),
            "5_VERB_STRATUM_NOT_CONSTRUCTIBLE_ON_THE_PRIMARY_GRAPH": (
                "the primary stratum is A 6 / N 41 / V 0 -- the foundation is noun-only and that "
                "propagates straight into the stratum. THE HILLS 2009 NOUN-SPECIFIC FALSIFIER "
                "CANNOT BE RUN ON THE PRIMARY ARM AT ALL. It is runnable on ORACLE (N 247 / V 111) "
                "and weakly on CSKG_NOLEXREL (N 226 / V 17). A real limitation of this test."),
            "6_HIT_AT_1_INSTRUMENT_NOT_RUN": (
                "it carries no verdict weight by design and Phase 1 already showed a 12-dim norm "
                "code does not drive that read-out (A2_NORMS 0.07125 < the 0.0870 spelling floor). "
                "The 8.70%-vs-4.80% spelling result belongs to the hit@1 instrument and is NOT the "
                "bar for any arm here; quoting it as such would be a cross-run conflation."),
            "7_ADDITIVITY_BARELY_EXERCISED_ON_OUR_GRAPH": (
                "mean in-core bridge degree is ~1.2 on the primary graph, so 'mean over d=1 "
                "neighbours' is a SINGLE-NEIGHBOUR SUBSTITUTION there. Baron & Osherson's pinned "
                "additivity is exercised only on the CSKG configurations."),
        },
        "named_divergences_from_the_biology": [
            "TARGET SPACE: the 12-dim code is a CONCRETE-SPOKE code. The brain grounds abstract "
            "words in emotion / interoception / social spokes. Ratings_Warriner_et_al.csv is on "
            "disk and unused. Widening the target space is the first revival move.",
            "RELATION SUPPLY: one-hop-thin and taxonomic-only. The angular gyrus's thematic channel "
            "has no counterpart in our extraction at all.",
            "NO INFORMATIVE-ENCOUNTER SELECTOR: ~90% of natural exposures are uninformative "
            "(Medina et al. 2011), so a selector is an upstream COMPONENT of the mechanism, not an "
            "optimisation bolted beside it.",
            "NO CONSOLIDATION: a bridged code is treated as immediately durable. Lexical "
            "integration requires an interval containing sleep (Dumay & Gaskell 2007). Phase 5.",
        ],
        "dissociation": dissociation,
        "results": results,
        "order_effects": order,
        "elapsed_s": round(time.time() - t_start, 1),
    }
    write_metrics(out_dir, metrics)

    print("\n===== PRIMARY (our definitional graph, core = AoA<=6.0)")
    for cfg in ("PRIMARY_DEF_CORE", "PRIMARY_DEF_CORE_MORPHBLOCK", "DEF_ANYNORM",
                "CEILING_CSKG_NOLEXREL_CORE", "CEILING_CSKG_ALL_CONTAMINATED",
                "CEILING_CSKG_ALL_CORE_CONTAMINATED", "ORACLE_ALL_HELDOUT"):
        r = results.get(cfg)
        if not r or "arms" not in r:
            continue
        print(f"\n--- {cfg}  n={r['n_stratum']}  POS={r['pos_counts']}  "
              f"G0={'PASS' if r['G0_power_gate']['K1_clears_floor'] else 'FAIL'}")
        for a, v in sorted(r["arms"].items()):
            if "rho" not in v:
                continue
            m = v["margin_over_strongest_floor"]
            print(f"  {a:<28} rho={v['rho']['point']:+.4f} "
                  f"[{v['rho']['ci95'][0]:+.4f},{v['rho']['ci95'][1]:+.4f}]  "
                  f"floor={v['strongest_floor']:<12}"
                  f"({v['floor_rho_by_arm'][v['strongest_floor']]:+.4f})  "
                  f"margin={m['point']:+.4f} [{m['ci95'][0]:+.4f},{m['ci95'][1]:+.4f}] "
                  f"{v['band']:<14} {v.get('verdict_for_this_arm', '')}")
    print("\nVERDICT:", verdict)
    print("DISSOCIATION:", json.dumps(dissociation, indent=1))
    print(f"[done] {out_dir}/metrics.json ({metrics['elapsed_s']}s)", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:                                     # noqa: BLE001 -- printed, never hidden
        import traceback
        traceback.print_exc()
        sys.exit(2)
