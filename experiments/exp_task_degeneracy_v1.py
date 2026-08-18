"""exp_task_degeneracy_v1 -- IS THE READ-OUT TASK DEGENERATE, OR WERE OUR FLOORS JUST TOO WEAK?

THE TRIGGER (2026-08-16, scratch/sparsify_right_object/decisive.json).
A CONSTANT ranking that uses ZERO information about the query -- cosine to the mean anchor
direction, the same answer to every question -- scored hit@1 0.1390 / 0.1518 on the open-vocabulary
read-out and beat the SPELLING floor by +0.0523 [+0.0391,+0.0658] / +0.0627 [+0.0475,+0.0778],
CI-separated. Every arm ever tested, our dense read-out, and the spelling floor itself therefore sit
below a baseline that knows nothing.

TWO READINGS. THEY DEMAND DIFFERENT RESPONSES AND MUST NOT BE COLLAPSED.
  READING 1  OUR FLOORS WERE TOO WEAK. `max(orthographic, frequency, scramble)` never contained a
             prototype/popularity-shaped member. Fix is mechanical: add the constant arm as a
             REQUIRED FOURTH FLOOR; the programme's direction is unchanged, the bar moves up.
  READING 2  THE TASK IS DEGENERATE. If a constant answer wins, hit@1 on this pool may be dominated
             by PROTOTYPICALITY rather than comprehension -- in which case the metric cannot show
             comprehension no matter what we build, and the read-out task needs redesigning.

HOW THEY ARE TOLD APART HERE.
  PART A  CHARACTERISE what the constant arm exploits: the gold-answer distribution's entropy, its
          top-k concentration, its correlation with corpus frequency and with the constant score,
          and the CEILING OF THE CONSTANT FAMILY (an ORACLE constant ranking fitted on the golds).
  PART B  BUILD A CONDITION THE CONSTANT ARM CANNOT WIN, and run the identical arms on it.
          Construction (tools/floor_battery.balanced_candidate_sets): each item's eligible pool
          becomes {its designated gold} + K distractors DRAWN FROM THE POPULATION OF OTHER ITEMS'
          GOLDS. Because distractors share the golds' marginal distribution over anchors, no
          anchor is more likely to be the RIGHT candidate than a WRONG one, so ANY item-independent
          ranking has expected hit@1 = 1/(K+1) = chance. Verified, not assumed: the fitted ORACLE
          constant is run on the balanced pool and must also sit at chance.
  PART C  A second de-biasing that KEEPS THE OPEN POOL: delete the top 1% of anchors by gold-degree
          from the pool and from every gold set. Tests whether the degeneracy is carried by a few
          hub words or is distributed.

DECISION RULE, PRE-REGISTERED HERE, BEFORE ANY NUMBER:
  * our read-out CI-separated ABOVE max(F1,F2,F3,F5) in the DE-BIASED condition but not in the
    ORIGINAL  ->  READING 2 supported; the task must be replaced.
  * our read-out fails to clear that floor set in BOTH  ->  READING 1 supported; the bar moves up.
  * anything else (regimes disagree, K values disagree, validity fails)  ->  NOT SETTLED, said
    plainly, rather than picked.

NEVER CARRY A NUMBER BETWEEN CONDITIONS. The original pool has ~5,500 candidates and the balanced
pool has K+1; their chance rates differ by two orders of magnitude. Only the MARGIN OVER THE FLOOR
SET MEASURED INSIDE THE SAME CONDITION may be compared, and every table below is grouped by
condition for that reason.

VALIDITY (read BEFORE any treatment number, per the standing rule):
  KA_QUERY_IS_GOLD_VECTOR   plants the answer -> must be near ceiling in every condition
  NULL_SCRAMBLED_ANCHORS    permutes anchor->vector -> must be near that condition's own chance
  They fail INDEPENDENTLY (one plants, one permutes) and both are reported per condition.
  SATURATION is checked: if the treatment arms do not spread, no gate is read.

TIE CONVENTIONS ARE REPORTED BOTH WAYS FOR EVERY ARM. The trigram channel carries ~15% tie mass and
our dense read-out carries 0.0%, which has already flipped one top-50 comparison. hit@1 optimistic =
a gold is among the top-scoring set; conservative = every top-scoring entry is a gold.

BOTH CUE REGIMES ARE REPORTED. EXACT_KEY (the query IS the stored profile) and PARTIAL_CUE (a
held-out sentence). The partial cue is the real operating regime.

INSTRUMENTATION, NOT A COMPONENT MEASUREMENT. This cell measures the MEASURING DEVICE. It makes no
brain-structure claim and none is fabricated for it; see the BRAIN_FIDELITY block in the report.

ASCII-only. No file under data/foundation, hdlab/ or any protected path is written or modified.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from typing import Dict, List, Sequence, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.floor_battery import (                                              # noqa: E402
    as_constant_matrix, balanced_candidate_sets, constant_prototype_floor, frequency_floor,
    hit_at_1_both_tie_conventions, l2n, margin, matched_candidate_sets, oracle_constant_scores,
    rank_of_best_gold, scramble_null,
)

ANCHOR_NAME = "exp_task_degeneracy_v1"
OUT_DIR = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
# PROVENANCE: the harness cache built by the 2026-08-16 cells from
# experiments/exp_grounding_readout_known_answer_v1 UNMODIFIED (same corpus, ConceptSpace, items,
# WordNet golds, eligible pool, MASTER_SEED). Reused so this cell scores the IDENTICAL pool the
# landed numbers were computed on. Rebuilt from C3 if absent.
CACHE = os.path.join(REPO_ROOT, "scratch", "sparse_code_real_task", "real_cache.npz")
AUX = os.path.join(REPO_ROOT, "scratch", "sparsify_right_object", "aux_v2.npz")

MASTER_SEED = 20260816
N_BOOT = 10000
K_LIST = (15, 49)          # balanced-pool sizes: chance 1/16 = 0.0625 and 1/50 = 0.0200
TOP_PCT_REMOVE = 0.01      # PART C: fraction of anchors (by gold degree) deleted from the pool
NORM_SEED = 7              # the lift cell's first seed; projection tag "proj:MEANING"
GRD_FRAC = 0.10            # the prior cell's best grounded k-cap point
KA_CEILING_MIN = 0.95      # known-answer gate; below this the condition is VOID and unread
SAT_MIN_SPREAD = 0.02      # treatment arms must spread by at least this or no gate is read


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(json.dumps(obj, indent=1).encode("utf-8"))
    os.replace(tmp, path)


def ruler_mode_gate() -> Dict:
    """HARD GATE, never inferred. exp_encoding_quality_instrument_v2 resolves RUN_MODE from argv/env
    AT IMPORT and exp_meaning_lift_population_code_v1 inherits V and CORPUS_BYTES from it, so the
    token '--smoke' anywhere in argv silently recomputes every lifted number on a 512-word
    vocabulary with no error and no warning. This cell's flags are --grid full|reduced for exactly
    that reason."""
    from experiments import exp_encoding_quality_instrument_v2 as INS
    g = {"RUN_MODE": INS.RUN_MODE, "V": int(INS.V), "CORPUS_BYTES": int(INS.CORPUS_BYTES),
         "argv": list(sys.argv)}
    g["PASS"] = bool(INS.RUN_MODE == "full" and int(INS.V) == 4096
                     and int(INS.CORPUS_BYTES) == 64_000_000)
    if not g["PASS"]:
        raise SystemExit("RULER MODE GATE FAILED: %r" % g)
    return g


def _unflatten(flat: np.ndarray, lens: np.ndarray) -> List[np.ndarray]:
    out, o = [], 0
    for n in lens:
        out.append(flat[o:o + int(n)])
        o += int(n)
    return out


def _lcp(a: str, b: str) -> int:
    k = 0
    for x, y in zip(a, b):
        if x != y:
            break
        k += 1
    return k


def build_cache_if_missing() -> Dict:
    """Rebuild the harness cache from exp_grounding_readout_known_answer_v1 UNMODIFIED."""
    if os.path.exists(CACHE):
        return {"source": "reused", "path": CACHE}
    import experiments.exp_grounding_readout_known_answer_v1 as C3
    from collections import defaultdict
    from hdlab.reading_grounding_loop import context_vector_masked, normalize_lemma
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    t0 = time.time()
    sents = C3.build_corpus("full")
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets, OUT_DIR)
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    items, diag = C3.build_items(space, buckets, counts, C3.MAX_ITEMS)
    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])
    mat_ok = np.linalg.norm(mat, axis=1) >= 1e-9
    Q_exact = np.zeros((len(items), mat.shape[1]), dtype=np.float32)
    Q_part = np.zeros((len(items), mat.shape[1]), dtype=np.float32)
    keep = np.zeros(len(items), dtype=bool)
    excl_l: List[np.ndarray] = []
    gold_l: List[np.ndarray] = []
    for i, it in enumerate(items):
        L = it["L"]
        q = space.bundle(L)
        cue = None
        if q is not None and float(np.linalg.norm(q)) >= 1e-9 and it["sent_idx"] is not None:
            cv = context_vector_masked(sents[it["sent_idx"]], L)
            if cv is not None and float(np.linalg.norm(cv)) >= 1e-9:
                cue = cv
        if cue is None:
            excl_l.append(np.zeros(0, dtype=np.int64))
            gold_l.append(np.zeros(0, dtype=np.int64))
            continue
        Q_exact[i], Q_part[i], keep[i] = q, cue, True
        excl_l.append(np.array(sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])), dtype=np.int64))
        gold_l.append(np.array(sorted(pos[g] for g in C3.gold_meaning_set(L) if g in pos),
                               dtype=np.int64))
    np.savez_compressed(
        CACHE, anchors=np.array(anchors), mat=mat.astype(np.float32), mat_ok=mat_ok,
        Q_exact=Q_exact, Q_part=Q_part, keep=keep,
        excl_flat=np.concatenate(excl_l), excl_len=np.array([len(x) for x in excl_l]),
        gold_flat=np.concatenate(gold_l), gold_len=np.array([len(x) for x in gold_l]),
        L_words=np.array([it["L"] for it in items]), diag=np.array([json.dumps(diag)]))
    print("[cache] rebuilt in %.0fs" % (time.time() - t0), flush=True)
    return {"source": "rebuilt", "path": CACHE, "elapsed_s": round(time.time() - t0, 1)}


def load_cache() -> Dict:
    z = np.load(CACHE, allow_pickle=False)
    anchors = [str(a) for a in z["anchors"]]
    return {"anchors": anchors, "mat": z["mat"].astype(np.float32), "mat_ok": z["mat_ok"],
            "Q_exact": z["Q_exact"].astype(np.float32), "Q_part": z["Q_part"].astype(np.float32),
            "keep": z["keep"], "excl": _unflatten(z["excl_flat"], z["excl_len"]),
            "goldi": _unflatten(z["gold_flat"], z["gold_len"]),
            "L_words": [str(w) for w in z["L_words"]],
            "pos": {a: i for i, a in enumerate(anchors)}}


def load_aux(C: Dict) -> Dict:
    """Spelling (trigram + prefix) and corpus-count channels on the identical pool."""
    if os.path.exists(AUX):
        z = np.load(AUX, allow_pickle=False)
        return {"Tq": z["Tq"], "t_mat": z["t_mat"], "Pq": z["Pq"], "fq": z["fq"],
                "source": "reused:" + AUX}
    import experiments.exp_grounding_readout_known_answer_v1 as C3
    import experiments.exp_meaning_supply_separation_v1 as MS
    anchors, L_words, keep, pos = C["anchors"], C["L_words"], C["keep"], C["pos"]
    t_mat, t_cov = MS.trigram_matrix(anchors)
    t_mat = np.asarray(t_mat, dtype=np.float32)
    Tq = np.zeros((len(L_words), t_mat.shape[1]), dtype=np.float32)
    Pq = np.zeros((len(L_words), len(anchors)), dtype=np.float32)
    alen = np.array([len(a) for a in anchors], dtype=np.float32)
    for i, L in enumerate(L_words):
        if not keep[i]:
            continue
        if L in pos and t_cov[pos[L]]:
            Tq[i] = t_mat[pos[L]]
        pre = np.array([_lcp(L, a) for a in anchors], dtype=np.float32)
        Pq[i] = pre / np.maximum(np.maximum(alen, float(len(L))), 1.0)
    sents = C3.build_corpus("full")
    _b, counts = C3.build_buckets(sents)
    fq = np.array([float(np.log1p(counts.get(a, 0))) for a in anchors], dtype=np.float32)
    os.makedirs(os.path.dirname(AUX), exist_ok=True)
    np.savez_compressed(AUX, Tq=Tq, t_mat=t_mat, Pq=Pq, fq=fq)
    return {"Tq": Tq, "t_mat": t_mat, "Pq": Pq, "fq": fq, "source": "rebuilt"}


def norms_for(words: Sequence[str], seed: int) -> Tuple[np.ndarray, np.ndarray]:
    """RAW 12-dim grounded norms with the lift cell's pre-registered OOV policy. Uses
    hdlab.grounded_similarity.grounded_vector -- NEVER grounded_similarity(), which is capped and
    saturates 76.18% of SimLex pairs onto two values."""
    from experiments import exp_encoding_quality_instrument_v2 as INS
    from hdlab.grounded_similarity import grounded_vector
    X = np.zeros((len(words), 12), dtype=np.float32)
    cov = np.zeros(len(words), dtype=bool)
    for i, w in enumerate(words):
        v = grounded_vector(w)
        if v is None:
            X[i] = np.random.default_rng(INS._hash_seed("oovnorm:" + w, seed)).standard_normal(12)
        else:
            X[i], cov[i] = np.asarray(v, dtype=np.float32), True
    return X, cov


def zcol(S: np.ndarray) -> np.ndarray:
    mu = S.mean(axis=0, keepdims=True)
    sd = S.std(axis=0, keepdims=True) + 1e-12
    return ((S - mu) / sd).astype(np.float32)


def _digest(v: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()[:16]


# =================================================================================================
# PART A -- what is the constant arm exploiting?
# =================================================================================================
def characterise(C: Dict, aux: Dict, f5: np.ndarray, GOLD: np.ndarray, E: np.ndarray,
                 keepm: np.ndarray) -> Dict:
    anchors = C["anchors"]
    n_anchors, n_items = GOLD.shape
    gold_deg = (GOLD & E).sum(axis=1).astype(np.float64)     # times an anchor is a correct answer
    tot = gold_deg.sum()
    p = gold_deg / max(tot, 1.0)
    nz = p[p > 0]
    H = float(-(nz * np.log2(nz)).sum())
    order = np.argsort(-gold_deg)
    n_scored = int(keepm.sum())
    fq = aux["fq"]

    def rho(a, b):
        m = np.isfinite(a) & np.isfinite(b)
        ra = np.argsort(np.argsort(a[m])).astype(np.float64)
        rb = np.argsort(np.argsort(b[m])).astype(np.float64)
        return round(float(np.corrcoef(ra, rb)[0, 1]), 4)

    # which single anchor does the CONSTANT floor actually answer with, and how often is it right?
    top_f5 = int(np.argmax(np.where(np.isfinite(f5), f5, -np.inf)))
    f5_order = np.argsort(-f5)
    gold_share_of_top_f5 = float(GOLD[top_f5][keepm].mean())
    return {
        "n_items_scored": n_scored, "n_anchors": int(n_anchors),
        "gold_set_size_mean": round(float((GOLD & E).sum(axis=0)[keepm].mean()), 3),
        "gold_set_size_median": float(np.median((GOLD & E).sum(axis=0)[keepm])),
        "ANSWER_DISTRIBUTION": {
            "note": "gold degree = number of items for which this anchor is a CORRECT answer. A "
                    "constant ranking wins exactly to the extent this distribution is concentrated.",
            "entropy_bits": round(H, 3),
            "max_entropy_bits": round(float(np.log2(max(int((gold_deg > 0).sum()), 1))), 3),
            "normalised_entropy": round(H / max(float(np.log2(max(int((gold_deg > 0).sum()), 1))),
                                                1e-9), 4),
            "n_anchors_ever_gold": int((gold_deg > 0).sum()),
            "top1_share_of_gold_mass": round(float(p[order[0]]), 4),
            "top10_share": round(float(p[order[:10]].sum()), 4),
            "top100_share": round(float(p[order[:100]].sum()), 4),
            "n_anchors_covering_50pct_of_gold_mass": int(
                np.searchsorted(np.cumsum(p[order]), 0.5) + 1),
            "top20_anchors_by_gold_degree": [
                [anchors[int(i)], int(gold_deg[int(i)]),
                 round(float(gold_deg[int(i)]) / max(n_scored, 1), 4)] for i in order[:20]],
            "frac_items_whose_gold_set_contains_a_top100_gold_degree_anchor": round(float(
                GOLD[order[:100]].any(axis=0)[keepm].mean()), 4)},
        "WHAT_THE_CONSTANT_CHANNEL_CORRELATES_WITH_spearman": {
            "gold_degree_vs_constant_prototype_score": rho(gold_deg, f5.astype(np.float64)),
            "gold_degree_vs_log_corpus_count": rho(gold_deg, fq.astype(np.float64)),
            "constant_prototype_score_vs_log_corpus_count": rho(f5.astype(np.float64),
                                                                fq.astype(np.float64)),
            "reading": "if gold degree tracks the constant score, the constant ranking is not a "
                       "trick -- it is reading the answer distribution off the pool."},
        "THE_CONSTANT_ARMS_ACTUAL_ANSWER": {
            "top_anchor_by_constant_score": anchors[top_f5],
            "fraction_of_items_for_which_that_ONE_WORD_is_a_correct_answer": round(
                gold_share_of_top_f5, 4),
            "top10_anchors_by_constant_score": [anchors[int(i)] for i in f5_order[:10]]},
    }


# =================================================================================================
# arms
# =================================================================================================
def col(v: np.ndarray) -> np.ndarray:
    """A CONSTANT floor as an [n_anchors, 1] column. Every scorer here broadcasts it, so the
    constant arms cost no memory and cannot silently acquire per-item variation."""
    return np.asarray(v, dtype=np.float32).reshape(-1, 1)


def static_arms(C: Dict, aux: Dict, f5: np.ndarray, grd: np.ndarray) -> Dict[str, np.ndarray]:
    """Arms that do NOT depend on the cue regime: the two orthographic floors, the two constant
    floors, and the grounded lexical channel (whose query is norms(L), not the cue). Their
    regime-independence is itself a tell and is stated in the report."""
    S_trig = (aux["t_mat"] @ aux["Tq"].T).astype(np.float32)
    S_pref = aux["Pq"].T.astype(np.float32)
    # aux["fq"] is already log1p(corpus count), i.e. exactly frequency_floor(counts).
    S_freq = col(frequency_floor(np.expm1(aux["fq"].astype(np.float64))))
    S_f5 = col(f5)
    Gn = l2n(grd)
    S_grd = (Gn @ Gn[C["qidx"]].T).astype(np.float32)
    return {"F1_TRIGRAM_ONLY_orthographic": S_trig, "F2_PREFIX_ONLY_orthographic": S_pref,
            "F3_FREQUENCY_ONLY_constant": S_freq,
            "F5_CONSTANT_PROTOTYPE_zero_query_information": S_f5,
            "G_GROUNDED_KCAP_f0.100_lexical": S_grd}


def build_arms(C: Dict, ST: Dict[str, np.ndarray], regime: str) -> Dict[str, np.ndarray]:
    mat = C["mat"]
    Q = C["Q_exact"] if regime == "EXACT_KEY" else C["Q_part"]
    Qn = l2n(Q)
    S_ctx = (l2n(mat) @ Qn.T).astype(np.float32)
    zc, zt, zg = zcol(S_ctx), zcol(ST["F1_TRIGRAM_ONLY_orthographic"]), zcol(
        ST["G_GROUNDED_KCAP_f0.100_lexical"])
    arms = dict(ST)
    arms["R0_CTX_DENSE_our_read_out"] = S_ctx
    arms["FUSE_ctx_SPELL"] = (0.5 * zc + 0.5 * zt).astype(np.float32)
    arms["FUSE_ctx_SPELL_GRD"] = ((zc + zt + zg) / 3.0).astype(np.float32)
    arms["NULL_SCRAMBLED_ANCHORS"] = (l2n(scramble_null(mat, MASTER_SEED)) @ Qn.T).astype(
        np.float32)
    del zc, zt, zg
    return arms


def known_answer_arm(C: Dict, designated: np.ndarray) -> np.ndarray:
    """The query IS the designated gold's stored vector. Must be near ceiling everywhere."""
    mat = C["mat"]
    Qka = np.zeros((len(C["L_words"]), mat.shape[1]), dtype=np.float32)
    ok = designated >= 0
    Qka[ok] = mat[designated[ok]]
    return (l2n(mat) @ l2n(Qka).T).astype(np.float32)


# =================================================================================================
# scoring one condition
# =================================================================================================
def score_condition(name: str, E: np.ndarray, GOLD: np.ndarray, keepm: np.ndarray,
                    arms: Dict[str, np.ndarray], chance: float, do_rank: bool,
                    floors: Sequence[str]) -> Dict:
    per: Dict[str, Dict] = {}
    scored_all = None
    for k, S in arms.items():
        h = hit_at_1_both_tie_conventions(S, E, GOLD)
        sc = h["scored"] & keepm
        per[k] = {"hit_exp": h["hit_exp"], "hit_opt": h["hit_opt"], "hit_cons": h["hit_cons"],
                  "tie": h["tie_mass"], "scored": sc}
        if do_rank:
            per[k].update(rank_of_best_gold(S, E, GOLD))
        scored_all = sc.copy() if scored_all is None else (scored_all & sc)
    common = scored_all
    nc = int(common.sum())
    idx = np.flatnonzero(common)
    rng = np.random.default_rng(MASTER_SEED + 101)
    IDX = rng.integers(0, nc, size=(N_BOOT, nc))
    boot = {c: {k: per[k][c][idx][IDX].mean(axis=1) for k in arms}
            for c in ("hit_exp", "hit_opt", "hit_cons")}
    acc = {c: {k: round(float(per[k][c][idx].mean()), 4) for k in arms}
           for c in ("hit_exp", "hit_opt", "hit_cons")}
    ci = {k: [round(float(np.percentile(boot["hit_exp"][k], 2.5)), 4),
              round(float(np.percentile(boot["hit_exp"][k], 97.5)), 4)] for k in arms}
    tie = {k: round(float(per[k]["tie"][idx].mean()), 4) for k in arms}

    A = acc["hit_exp"]                       # PRIMARY: tie-corrected expectation
    treat = [k for k in arms if not k.startswith(("KA_", "NULL_", "ORACLE"))]
    spread = round(float(max(A[k] for k in treat) - min(A[k] for k in treat)), 4)
    ka = A.get("KA_QUERY_IS_GOLD_VECTOR", float("nan"))
    nul = A.get("NULL_SCRAMBLED_ANCHORS", float("nan"))
    valid = bool(ka >= KA_CEILING_MIN and spread >= SAT_MIN_SPREAD)

    present = [f for f in floors if f in A]
    binding = max(present, key=lambda f: A[f]) if present else None
    out = {
        "n_common_scored": nc, "chance_for_THIS_condition": round(float(chance), 6),
        "PRIMARY_METRIC": "hit_at_1_TIE_CORRECTED (expected hit under a random tie-break)",
        "VALIDITY": {
            "KNOWN_ANSWER_hit_at_1": ka, "gate": KA_CEILING_MIN,
            "KA_PASSES": bool(ka >= KA_CEILING_MIN),
            "NULL_hit_at_1": nul, "chance": round(float(chance), 6),
            "null_near_chance": bool(abs(nul - chance) < max(0.02, 0.5 * chance)),
            "treatment_spread": spread, "saturation_tripped": bool(spread < SAT_MIN_SPREAD),
            "CONDITION_READABLE": valid,
            "independence": "KA plants the answer; NULL permutes the anchor->vector map. Different "
                            "mechanisms, so they can and do fail separately."},
        "hit_at_1_TIE_CORRECTED_primary": A,
        "hit_at_1_OPTIMISTIC_tie": acc["hit_opt"],
        "hit_at_1_CONSERVATIVE_tie": acc["hit_cons"],
        "ci95_tie_corrected": ci, "mean_tie_mass_of_eligible_pool": tie,
        "arm_digests": {k: _digest(per[k]["hit_exp"][idx]) for k in arms},
        "BINDING_FLOOR": binding,
        "MARGIN_vs_binding_floor_TIE_CORRECTED": (
            {k: margin(boot["hit_exp"], k, binding) for k in arms if k != binding}
            if binding else {}),
        "MARGIN_vs_binding_floor_CONSERVATIVE": (
            {k: margin(boot["hit_cons"], k, binding) for k in arms if k != binding}
            if binding else {}),
        "MARGIN_vs_binding_floor_OPTIMISTIC": (
            {k: margin(boot["hit_opt"], k, binding) for k in arms if k != binding}
            if binding else {}),
    }
    orc = "ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"
    if orc in arms:
        # THE CEILING OF THE CONSTANT FAMILY. If our read-out cannot beat the BEST POSSIBLE
        # constant answer, no amount of floor bookkeeping helps.
        out["MARGIN_vs_ORACLE_CONSTANT_tie_corrected"] = {
            k: margin(boot["hit_exp"], k, orc) for k in arms if k != orc}
    # every arm against EVERY floor separately, so a reader can judge without trusting the
    # binding-floor selection (which is itself a choice).
    out["ARM_BY_ARM_vs_EACH_FLOOR_tie_corrected"] = {
        k: {f: margin(boot["hit_exp"], k, f) for f in present if f != k}
        for k in arms if k not in present}
    if binding:
        out["BINDING_FLOOR_VALUE_tie_corrected"] = A[binding]
        out["MARGIN_vs_CHANCE_tie_corrected"] = {
            k: {"point": round(A[k] - float(chance), 4),
                "ci95_of_arm": ci[k],
                "band": ("ABOVE" if ci[k][0] > chance else
                         ("BELOW" if ci[k][1] < chance else "NOT_SEPARATED"))} for k in arms}
    if do_rank:
        out["top50_recall_OPTIMISTIC"] = {
            k: round(float((per[k]["rank_opt"][idx] <= 50).mean()), 4) for k in arms}
        out["top50_recall_CONSERVATIVE"] = {
            k: round(float((per[k]["rank_cons"][idx] <= 50).mean()), 4) for k in arms}
        out["median_rank_OPTIMISTIC"] = {
            k: float(np.median(per[k]["rank_opt"][idx])) for k in arms}
    print("[%s] n=%d KA=%.4f NULL=%.4f chance=%.4f binding=%s  " % (
        name, nc, ka, nul, chance, binding)
        + " ".join("%s=%.4f" % (k[:18], v) for k, v in A.items()), flush=True)
    return out


# =================================================================================================
# self-test
# =================================================================================================
def self_test() -> dict:
    res: dict = {}
    from tools import floor_battery
    res["floor_battery_selftest"] = floor_battery.self_test()

    # T1 -- zcol is a per-column standardisation and does not reorder a column.
    rng = np.random.default_rng(2)
    S = rng.standard_normal((50, 7)).astype(np.float32)
    Z = zcol(S)
    assert np.allclose(np.argsort(S, axis=0), np.argsort(Z, axis=0)), "zcol reordered a column"
    assert abs(float(Z[:, 3].mean())) < 1e-5 and abs(float(Z[:, 3].std()) - 1.0) < 1e-4
    res["T1_zcol_ok"] = True

    # T2 -- the CONSTANT floor is bit-identical across items when materialised.
    v = rng.standard_normal(50).astype(np.float32)
    M = as_constant_matrix(v, 7)
    assert all(np.array_equal(M[:, 0], M[:, j]) for j in range(7))
    res["T2_constant_is_constant"] = True

    # T3 -- score_condition end to end on a synthetic pool where the ANSWER IS KNOWN:
    # a planted arm must reach 1.0, a null must sit at chance, and a constant prototype arm must
    # beat chance on a prototype-skewed open pool. If any of these fails the harness is broken.
    n_a, n_i = 120, 900
    GOLD = np.zeros((n_a, n_i), dtype=bool)
    proto = np.linspace(1, 0, n_a).astype(np.float32)
    p = proto ** 6; p = p / p.sum()
    g = rng.choice(n_a, size=n_i, p=p)
    GOLD[g, np.arange(n_i)] = True
    E = np.ones((n_a, n_i), dtype=bool)
    keepm = np.ones(n_i, dtype=bool)
    Splant = np.zeros((n_a, n_i), dtype=np.float32); Splant[g, np.arange(n_i)] = 1.0
    arms = {"R0_CTX_DENSE_our_read_out": rng.standard_normal((n_a, n_i)).astype(np.float32),
            "F5_CONSTANT_PROTOTYPE_zero_query_information": as_constant_matrix(proto, n_i),
            "KA_QUERY_IS_GOLD_VECTOR": Splant,
            "NULL_SCRAMBLED_ANCHORS": rng.standard_normal((n_a, n_i)).astype(np.float32)}
    r = score_condition("T3", E, GOLD, keepm, arms, 1.0 / n_a, False,
                        ["F5_CONSTANT_PROTOTYPE_zero_query_information"])
    assert r["VALIDITY"]["KA_PASSES"], "planted-answer arm did not reach ceiling: %r" % r["VALIDITY"]
    assert r["hit_at_1_OPTIMISTIC_tie"]["NULL_SCRAMBLED_ANCHORS"] < 0.05, "null arm is not null"
    assert r["hit_at_1_OPTIMISTIC_tie"][
        "F5_CONSTANT_PROTOTYPE_zero_query_information"] > 5.0 / n_a, "constant arm did not fire"
    assert r["BINDING_FLOOR"] == "F5_CONSTANT_PROTOTYPE_zero_query_information"
    res["T3_harness_end_to_end"] = {
        "KA": r["VALIDITY"]["KNOWN_ANSWER_hit_at_1"], "NULL": r["VALIDITY"]["NULL_hit_at_1"],
        "constant": r["hit_at_1_OPTIMISTIC_tie"]["F5_CONSTANT_PROTOTYPE_zero_query_information"]}

    # T4 -- VALIDITY ARMS FAIL INDEPENDENTLY (demonstrated, not asserted): break KA only.
    arms_bad = dict(arms); arms_bad["KA_QUERY_IS_GOLD_VECTOR"] = arms["NULL_SCRAMBLED_ANCHORS"]
    r2 = score_condition("T4", E, GOLD, keepm, arms_bad, 1.0 / n_a, False,
                         ["F5_CONSTANT_PROTOTYPE_zero_query_information"])
    assert not r2["VALIDITY"]["KA_PASSES"] and r2["VALIDITY"]["NULL_hit_at_1"] < 0.05
    res["T4_validity_arms_fail_independently"] = True

    # T5 -- the SATURATION guard actually trips when every arm is identical.
    same = rng.standard_normal((n_a, n_i)).astype(np.float32)
    arms_sat = {"R0_CTX_DENSE_our_read_out": same, "F1_TRIGRAM_ONLY_orthographic": same,
                "KA_QUERY_IS_GOLD_VECTOR": Splant, "NULL_SCRAMBLED_ANCHORS": same}
    r3 = score_condition("T5", E, GOLD, keepm, arms_sat, 1.0 / n_a, False,
                         ["F1_TRIGRAM_ONLY_orthographic"])
    assert r3["VALIDITY"]["saturation_tripped"] and not r3["VALIDITY"]["CONDITION_READABLE"]
    res["T5_saturation_guard_trips"] = True

    print("[selftest] PASS " + json.dumps(res)[:1200], flush=True)
    return res


# =================================================================================================
# main
# =================================================================================================
def run(grid: str) -> Dict:
    t0 = time.time()
    rep: Dict = {"anchor_name": ANCHOR_NAME, "grid": grid,
                 "ts_iso": datetime.now(timezone.utc).isoformat(), "host": platform.node(),
                 "RULER_MODE_GATE": ruler_mode_gate(), "cache": build_cache_if_missing()}
    C = load_cache()
    aux = load_aux(C)
    rep["aux_source"] = aux.get("source", "?")
    anchors, mat, mat_ok, keep = C["anchors"], C["mat"], C["mat_ok"], C["keep"]
    n_anchors, n_items = len(anchors), len(C["L_words"])
    C["qidx"] = np.array([C["pos"].get(w, 0) for w in C["L_words"]], dtype=np.int64)
    print("[load] n_anchors=%d n_items=%d keep=%d %.0fs"
          % (n_anchors, n_items, int(keep.sum()), time.time() - t0), flush=True)

    # ---- gold + eligibility matrices (the ORIGINAL condition) --------------------------------
    GOLD = np.zeros((n_anchors, n_items), dtype=bool)
    E_A = np.zeros((n_anchors, n_items), dtype=bool)
    for i in range(n_items):
        if not keep[i]:
            continue
        E_A[:, i] = mat_ok
        if len(C["excl"][i]):
            E_A[C["excl"][i], i] = False
        gi = C["goldi"][i]
        if len(gi):
            GOLD[gi, i] = True
    GOLD &= E_A
    keep_A = keep & GOLD.any(axis=0)
    print("[pool] items with an eligible gold: %d" % int(keep_A.sum()), flush=True)

    # ---- the FOURTH FLOOR ---------------------------------------------------------------------
    f5 = constant_prototype_floor(mat, mat_ok)
    rep["PART_A_CHARACTERISATION"] = characterise(C, aux, f5, GOLD, E_A, keep_A)

    # ---- designated gold: UNIFORM among each item's eligible golds (a frequency-weighted pick
    # would smuggle the very bias under test into the gold marginal). Computed PER CONDITION,
    # because a condition that deletes anchors can delete a designated gold and silently drag its
    # own known-answer arm below ceiling (observed on the smoke gate at 0.9374). -------------
    def designate(G: np.ndarray, km: np.ndarray, seed: int) -> np.ndarray:
        r = np.random.default_rng(seed)
        d = np.full(n_items, -1, dtype=np.int64)
        for i in np.flatnonzero(km):
            gi = np.flatnonzero(G[:, i])
            if gi.size:
                d[i] = int(gi[r.integers(0, gi.size)])
        return d

    designated = designate(GOLD, keep_A, MASTER_SEED + 5)

    # ---- the grounded lexical channel (the prior cell's one surviving positive) ---------------
    from experiments import exp_meaning_lift_population_code_v1 as LIFT
    X, cov = norms_for(anchors, NORM_SEED)
    grd = LIFT.lift_kcap(X, 1024, NORM_SEED, GRD_FRAC, True, True).astype(np.float32)
    rep["grounded_channel"] = {"coverage_of_pool": round(float(cov.mean()), 4),
                               "operator": "exp_meaning_lift_population_code_v1.lift_kcap",
                               "d": 1024, "active_fraction": GRD_FRAC, "seed": NORM_SEED}

    ST = static_arms(C, aux, f5, grd)
    S_trig_for_matching = ST["F1_TRIGRAM_ONLY_orthographic"]

    # ---- CONDITIONS ---------------------------------------------------------------------------
    conditions: Dict[str, Dict] = {}
    gold_lists = [np.flatnonzero(GOLD[:, i]) for i in range(n_items)]
    n_elig_A = E_A.sum(axis=0)
    chance_A = float(np.mean(GOLD[:, keep_A].sum(axis=0) / np.maximum(n_elig_A[keep_A], 1)))
    conditions["A_ORIGINAL_open_pool"] = {
        "E": E_A, "keep": keep_A, "chance": chance_A, "rank": True, "designated": designated,
        "what": "the task exactly as landed: open pool of every eligible anchor, ANY member of the "
                "WordNet gold set counts. Reproduces the landed numbers as a regression gate."}

    def _elig_from_cand(cand: np.ndarray, ok: np.ndarray, K: int) -> np.ndarray:
        E = np.zeros((n_anchors, n_items), dtype=bool)
        rows = cand[ok]
        cols = np.repeat(np.flatnonzero(ok)[:, None], K + 1, axis=1)
        E[rows.ravel(), cols.ravel()] = True
        return E

    ks = K_LIST if grid == "full" else K_LIST[:1]
    for K in ks:
        cand, _gc = balanced_candidate_sets(designated, gold_lists, C["excl"], keep_A, K,
                                            MASTER_SEED + 17 + K)
        ok = cand[:, 0] >= 0
        E_B = _elig_from_cand(cand, ok, K)
        leak = int((E_B & GOLD).sum(axis=0)[ok].max())
        assert leak == 1, "balanced candidate set contains more than one correct answer"
        conditions["B_BALANCED_K%d" % K] = {
            "E": E_B, "keep": ok, "chance": 1.0 / (K + 1), "rank": False, "K": K,
            "designated": designated, "n_golds_per_candidate_set_max": leak,
            "what": "DE-BIASED, THE DECISIVE CONDITION. Per-item pool = designated gold + %d "
                    "distractors drawn from the population of OTHER items' golds, so the distractor "
                    "marginal equals the gold marginal and NO item-independent (constant) ranking "
                    "can beat chance %.4f. Verified by the ORACLE_CONSTANT arm, not assumed."
                    % (K, 1.0 / (K + 1))}

    # PART D -- the same balanced pool, ADDITIONALLY matched on orthographic similarity to the
    # query word, so neither a constant NOR a speller can win. Secondary control: sub-selecting
    # donors perturbs the role symmetry, so its constant arms are re-read, never inherited.
    K_D = ks[0]
    cand_d, _gcd, dmatch = matched_candidate_sets(designated, gold_lists, C["excl"], keep_A, K_D,
                                                 MASTER_SEED + 31, S_trig_for_matching)
    okd = cand_d[:, 0] >= 0
    E_D = _elig_from_cand(cand_d, okd, K_D)
    assert int((E_D & GOLD).sum(axis=0)[okd].max()) == 1, "matched pool has 2 correct answers"
    conditions["D_BALANCED_K%d_SPELLING_MATCHED" % K_D] = {
        "E": E_D, "keep": okd, "chance": 1.0 / (K_D + 1), "rank": False, "K": K_D,
        "designated": designated, "match_diagnostics": dmatch,
        "what": "SECONDARY, STRICTER. As B, plus every distractor matched to the gold on trigram "
                "similarity to the query word, so the ORTHOGRAPHIC channel is neutralised too. A "
                "task on which neither a constant nor a speller can win."}

    # PART C -- keep the open pool, delete the top 1% of anchors BY GOLD DEGREE
    gold_deg = (GOLD & E_A).sum(axis=1)
    n_rm = max(1, int(round(TOP_PCT_REMOVE * n_anchors)))
    rm = np.argsort(-gold_deg)[:n_rm]
    E_C = E_A.copy()
    E_C[rm, :] = False
    GOLD_C = GOLD.copy()
    GOLD_C[rm, :] = False
    keep_C = keep_A & GOLD_C.any(axis=0)
    conditions["C_OPEN_POOL_top1pct_gold_hubs_deleted"] = {
        "E": E_C, "keep": keep_C, "GOLD": GOLD_C, "rank": True,
        "designated": designate(GOLD_C, keep_C, MASTER_SEED + 9),
        "chance": float(np.mean(GOLD_C[:, keep_C].sum(axis=0)
                                / np.maximum(E_C.sum(axis=0)[keep_C], 1))),
        "what": "OPEN POOL retained; the %d anchors that are correct answers most often are "
                "deleted from the pool AND from every gold set. Tests whether the degeneracy is "
                "carried by a few hub words or is distributed. NOTE this does not neutralise every "
                "constant ranking -- the ORACLE arm measures what is left." % n_rm,
        "n_anchors_removed": n_rm,
        "removed_anchors": [anchors[int(i)] for i in rm[:25]],
        "items_lost": int(keep_A.sum() - keep_C.sum())}

    FLOORS = ("F1_TRIGRAM_ONLY_orthographic", "F2_PREFIX_ONLY_orthographic",
              "F3_FREQUENCY_ONLY_constant", "F5_CONSTANT_PROTOTYPE_zero_query_information")

    ORACLE: Dict[str, np.ndarray] = {}
    KAS: Dict[str, np.ndarray] = {}
    for cname, cfg in conditions.items():
        G = cfg.get("GOLD", GOLD)
        kk = np.flatnonzero(cfg["keep"])
        restricted = cname.startswith(("B_", "D_"))
        ORACLE[cname] = col(oracle_constant_scores(
            n_anchors, [np.flatnonzero(G[:, i]) for i in kk],
            ([np.flatnonzero(cfg["E"][:, i]) for i in kk] if restricted else None)))
        KAS[cname] = known_answer_arm(C, cfg["designated"])

    results: Dict[str, Dict] = {}
    for regime in ("EXACT_KEY", "PARTIAL_CUE"):
        arms = build_arms(C, ST, regime)
        for cname, cfg in conditions.items():
            G = cfg.get("GOLD", GOLD)
            arms["KA_QUERY_IS_GOLD_VECTOR"] = KAS[cname]
            a2 = dict(arms)
            a2["ORACLE_CONSTANT_FITTED_ON_GOLDS_not_a_floor"] = ORACLE[cname]
            key = "%s|%s" % (cname, regime)
            results[key] = score_condition(key, cfg["E"], G, cfg["keep"], a2, cfg["chance"],
                                           bool(cfg["rank"]), FLOORS)
            results[key]["condition_note"] = cfg["what"]
        del arms
    rep["CONDITIONS"] = {
        k: dict({kk: vv for kk, vv in v.items()
                 if kk not in ("E", "keep", "GOLD", "designated")},
                n_items_in_condition=int(np.asarray(v["keep"]).sum()))
        for k, v in conditions.items()}
    rep["RESULTS"] = results
    rep["elapsed_s"] = round(time.time() - t0, 1)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--grid", choices=["full", "reduced"], default="full")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    os.makedirs(OUT_DIR, exist_ok=True)
    if a.self_test:
        self_test()
        print("ALL SELF-TESTS PASSED", flush=True)
        return 0
    with open(os.path.join(OUT_DIR, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))
    try:
        rep = run(a.grid)
        _atomic_json(os.path.join(OUT_DIR, "metrics.json"), rep)
        print("WROTE " + os.path.join(OUT_DIR, "metrics.json"), flush=True)
    except SystemExit:
        raise
    except Exception as exc:
        _atomic_json(os.path.join(OUT_DIR, "_crash_diagnostic.json"),
                     {"error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
