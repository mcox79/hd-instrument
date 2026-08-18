"""per_row_gain_c3_vet_v1 -- does hdlab/excitability.py's per-row multiplicative gain improve the
C3 open-vocabulary final pick? MEASURES ONLY. Wires nothing. Changes no hdlab default.

PRE-REG: preregs/2026-08-15_per_row_gain_c3_readout_v1.md, committed BEFORE this script ran.

Reuses build_corpus / build_buckets / build_space / build_items / gold_meaning_set / MASTER_SEED /
MAX_ITEMS from exp_grounding_readout_known_answer_v1 (never reimplemented) -- same construction
tools/orthographic_floor_vet_v1.py used to reproduce the C3 headline bit-for-bit. Reuses
hdlab.excitability's actual gate functions (downscale_gate_by_E, downscale_gate_random,
downscale_gate_by_magnitude) for the module-function arms; the CONTINUOUS arm is disclosed as a
generalization, not a call into the module (see pre-reg).

Run:  .venv/Scripts/python.exe tools/per_row_gain_c3_vet_v1.py [--smoke]
Output: data/exp_per_row_gain_c3_vet_v1[_smoke]/metrics.json (atomic os.replace, ts_iso stamped).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

from hdlab.reading_grounding_loop import context_vector_masked, normalize_lemma  # noqa: E402
import hdlab.excitability as EXC  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402

SMOKE = "--smoke" in sys.argv
ANCHOR_NAME = "exp_per_row_gain_c3_vet_v1" + ("_smoke" if SMOKE else "")
OUT = os.path.join(_REPO, "data", ANCHOR_NAME)
os.makedirs(OUT, exist_ok=True)

ORTHO_BAR = 0.0870
ORTHO_BAR_CI = (0.0783, 0.0960)
SELF_RETRIEVAL_FLOOR = 0.70


def build_excitability_E(anchors: List[str], counts, pos: Dict[str, int], cap: int = 50) -> np.ndarray:
    """Genuine EWMA excitability per anchor: seed_on_write once, then bump_on_retrieval(1.0) once
    per corpus occurrence (capped at `cap`; eta=0.1 saturates well before 50 events). Calls the
    real hdlab.excitability functions, not a reimplementation of their math."""
    E = EXC.init_E(len(anchors))
    cfg = EXC.EConfig()
    for a in anchors:
        i = pos[a]
        EXC.seed_on_write(E, i, cfg)
        n_events = min(int(counts.get(a, 0)), cap)
        for _ in range(n_events):
            EXC.bump_on_retrieval(E, i, 1.0, cfg)
    return E


def main() -> int:
    t0 = time.time()
    sents = C3.build_corpus("smoke" if SMOKE else "full")
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets, OUT)
    anchors, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    max_items = 200 if SMOKE else C3.MAX_ITEMS
    items, diag = C3.build_items(space, buckets, counts, max_items)
    n = len(items)
    print("[recompute] n_items=%d n_anchors=%d elapsed=%.1fs" % (n, n_anchors, time.time() - t0),
          flush=True)

    mat_nrm_base = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm_base >= 1e-9

    # ---- build the real excitability signal (module functions, real corpus frequency)
    E = build_excitability_E(anchors, counts, pos)
    med_E = float(np.median(E))
    rng = np.random.default_rng(C3.MASTER_SEED + 31)

    # ---- precompute all gained anchor matrices ONCE (gain is per-anchor-row, item-independent)
    mats: Dict[str, np.ndarray] = {"A1_BASE": mat}

    m = mat.copy()
    n_hit = EXC.downscale_gate_by_E(m, E, scale=0.4, threshold=med_E)
    mats["PER_ROW_GAIN_E_THRESH"] = m
    n_hit_e_thresh = n_hit

    m = mat.copy()
    m *= (0.5 + 1.5 * E)[:, None]
    mats["PER_ROW_GAIN_E_CONTINUOUS"] = m

    m = mat.copy()
    frac_matched = max(1, n_hit_e_thresh) / max(1, n_anchors)
    frac_matched = min(max(frac_matched, 0.01), 0.99)
    n_hit_rand = EXC.downscale_gate_random(m, frac=frac_matched, scale=0.4, rng=np.random.RandomState(7))
    mats["PER_ROW_GAIN_RANDOM"] = m

    m = mat.copy()
    n_hit_mag = EXC.downscale_gate_by_magnitude(m, threshold_frac=frac_matched, scale=0.4)
    mats["PER_ROW_GAIN_MAGNITUDE"] = m

    m = mat.copy()
    m *= 1.7
    mats["GLOBAL_SCALAR"] = m

    col_std = np.std(mat, axis=0)
    gain_dim = 1.0 / np.maximum(col_std, 1e-9)
    gain_dim = gain_dim / float(np.mean(gain_dim))
    m = mat.copy()
    m *= gain_dim[None, :]
    mats["PER_RAW_DIM_INV_STD"] = m

    gain_dim_shuf = gain_dim.copy()
    rng.shuffle(gain_dim_shuf)
    m = mat.copy()
    m *= gain_dim_shuf[None, :]
    mats["PER_RAW_DIM_RANDOM"] = m

    norms: Dict[str, np.ndarray] = {k: np.linalg.norm(v, axis=1) for k, v in mats.items()}
    gain_arms = tuple(k for k in mats if k != "A1_BASE")
    all_score_arms = ("A1_BASE",) + gain_arms + ("SCRAMBLE",)

    hits = {a: np.zeros(n, dtype=bool) for a in all_score_arms}
    picks = {a: [] for a in all_score_arms}
    identical_to_base = {a: np.zeros(n, dtype=bool) for a in gain_arms}

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])

    donors = C3._derangement(n, lambda i, j: len({items[j]["L"], items[j]["G"], items[j]["F"]}
                                                  & {items[i]["L"], items[i]["G"], items[i]["F"]}) > 0)

    anchor_arr = np.array(anchors)

    for i, it in enumerate(items):
        L = it["L"]
        elig = np.ones(n_anchors, dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])):
            elig[k] = False
        elig &= mat_ok
        sel = np.flatnonzero(elig)
        if sel.size == 0:
            continue
        gold = C3.gold_meaning_set(L)

        qL = space.bundle(L)
        qLn = float(np.linalg.norm(qL))
        qD = space.bundle(items[donors[i]]["L"])
        qDn = float(np.linalg.norm(qD))

        base_scores = None
        for a in all_score_arms:
            if a == "SCRAMBLE":
                if qDn < 1e-9:
                    continue
                sc = (mats["A1_BASE"][sel] @ qD) / (norms["A1_BASE"][sel] * qDn)
            else:
                if qLn < 1e-9:
                    continue
                sc = (mats[a][sel] @ qL) / (norms[a][sel] * qLn)
            b = int(np.argmax(sc))
            p = anchor_arr[sel[b]]
            picks[a].append(str(p))
            hits[a][i] = str(p) in gold
            if a == "A1_BASE":
                base_scores = sc
                base_pick = p
            elif a != "SCRAMBLE":
                identical_to_base[a][i] = (str(p) == str(base_pick)) and bool(
                    np.allclose(sc, base_scores, atol=1e-6, rtol=1e-6))
        if (i + 1) % 500 == 0:
            print("[score] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    # ---- KNOWN_ANSWER positive control: reuse C3's own self-retrieval construction verbatim
    rng_sr = np.random.default_rng(C3.MASTER_SEED + 41)
    sr_hits, sr_n = 0, 0
    for it in items[:min(300, n)]:
        L = it["L"]
        if it["sent_idx"] is None:
            continue
        other = anchors[int(rng_sr.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (other == L or C3._is_variant(other, L)):
            other = anchors[int(rng_sr.integers(len(anchors)))]
            tries += 1
        if other == L:
            continue
        q = context_vector_masked(sents[it["sent_idx"]], L)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        cand = [pos[L], pos[other]]
        sc = (mat[cand] @ q) / (mat_nrm_base[cand] * qn)
        pick_L = sc[0] >= sc[1]
        sr_hits += int(pick_L)
        sr_n += 1
    self_retrieval = round(sr_hits / max(1, sr_n), 6)

    armv = {a: hits[a].astype(float) for a in all_score_arms}
    deltas = [("d_%s_minus_BASE" % a, a, "A1_BASE") for a in gain_arms] + \
             [("d_SCRAMBLE_minus_BASE", "SCRAMBLE", "A1_BASE")]
    bs = MS.paired_bootstrap(armv, deltas, 5000, C3.MASTER_SEED + 51)

    a1_matches_c3_headline = abs(bs["arm_acc_ci"]["A1_BASE"]["acc"] - 0.048) < 1e-9 if not SMOKE else None
    bar_lo = ORTHO_BAR_CI[1]  # CI-separated margin requires beating the UPPER bound of the floor's CI

    clears_bar = {a: bool(bs["arm_acc_ci"][a]["ci_lo"] > bar_lo) for a in gain_arms}
    struct_null = {a: bool(not bs["deltas"]["d_%s_minus_BASE" % a]["ci_excludes_zero"]) for a in gain_arms}
    bitwise_identical_frac = {a: float(identical_to_base[a].mean()) for a in gain_arms}

    rep = {
        "anchor_name": ANCHOR_NAME,
        "what": "PRE-REGISTERED VET: hdlab/excitability.py per-row multiplicative gain on the C3 "
                "open-vocabulary final pick, one variable, identical items/pool/gold/scorer as "
                "exp_grounding_readout_known_answer_v1 / exp_orthographic_floor_vet_v1",
        "prereg": "preregs/2026-08-15_per_row_gain_c3_readout_v1.md",
        "compares_against": {"cell": "exp_grounding_readout_known_answer_v1", "arm": "B5_OPEN_REAL",
                             "hit_at_1": 0.048},
        "bar": {"source": "exp_orthographic_floor_vet_v1 A6_TRIGRAM_ONLY", "acc": ORTHO_BAR,
                "ci": list(ORTHO_BAR_CI),
                "rule": "CI-separated: arm's ci_lo must exceed the bar's ci_hi (%.4f)" % bar_lo},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "smoke": SMOKE,
        "n_items": n, "n_anchors": n_anchors, "item_construction": diag,
        "a1_base_reproduces_c3_headline_exactly": a1_matches_c3_headline,
        "self_retrieval": {"acc": self_retrieval, "n": sr_n, "floor": SELF_RETRIEVAL_FLOOR,
                           "ok": self_retrieval >= SELF_RETRIEVAL_FLOOR},
        "excitability_signal": {"median_E": med_E, "n_rows_downscaled_by_E_thresh": n_hit_e_thresh,
                                "frac_matched_for_random_and_magnitude_controls": frac_matched},
        "bootstrap": bs,
        "clears_bar_CI_separated": clears_bar,
        "structural_null_vs_A1_BASE": struct_null,
        "bitwise_identical_pick_fraction_vs_A1_BASE": bitwise_identical_frac,
        "per_arm": {a: {"hit_at_1": float(hits[a].mean()), "example_picks": picks[a][:10]}
                    for a in all_score_arms},
        "elapsed_s": round(time.time() - t0, 2),
    }
    p = os.path.join(OUT, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print(json.dumps(rep["per_arm"], indent=1))
    print(json.dumps(bs["deltas"], indent=1))
    print("A1_BASE reproduces C3 headline 0.0480 exactly:", a1_matches_c3_headline)
    print("SELF_RETRIEVAL:", self_retrieval, "(floor 0.70)")
    print("bitwise identical to A1_BASE:", bitwise_identical_frac)
    print("clears bar CI-separated:", clears_bar)
    print("WROTE", p)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        _crash = os.path.join(OUT, "_crash_diagnostic.json")
        with open(_crash + ".tmp", "w", encoding="utf-8") as fh:
            json.dump({"anchor_name": ANCHOR_NAME,
                       "error": "%s: %s" % (type(exc).__name__, exc),
                       "traceback": traceback.format_exc(),
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        os.replace(_crash + ".tmp", _crash)
        raise
