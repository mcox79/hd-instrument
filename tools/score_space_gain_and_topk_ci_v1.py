"""score_space_gain_and_topk_ci_v1 -- TWO JOBS on one recompute of the identical C3 harness.
MEASURES ONLY. Wires nothing. Changes no hdlab default.

PRE-REG: preregs/2026-08-15_score_space_gain_and_topk_ci_v1.md, committed BEFORE this script ran.

JOB 1: does per-candidate excitability-style gain applied to the SCORE (after normalized-cosine
scoring, not to the stored anchor row) clear the orthographic floor on C3's open-vocabulary
read-out? `data/exp_per_row_gain_c3_vet_v1/metrics.json` proved gain applied to the VECTOR cancels
algebraically (cosine is invariant to a positive per-row rescale). This cell moves the identical
gain signal one stage later, to the SCORE, where that invariance does not hold.

JOB 2: paired-bootstrap CI on the "retrieval is tied, selection is not" diagnosis
(frac_gold_in_top50 and conditional-pick-given-in-top50, ours vs spelling-only), which
`notes/graded_path_does_not_clear_the_orthographic_floor_2026-08-14.md` reported as four bare
numbers with no interval and no persisted per-item array.

Reuses build_corpus / build_buckets / build_space / build_items / gold_meaning_set / MASTER_SEED /
MAX_ITEMS / _derangement / _is_variant from exp_grounding_readout_known_answer_v1, trigram_matrix /
paired_bootstrap / _z from exp_meaning_supply_separation_v1, and the real
hdlab.excitability gate functions -- never reimplemented. No new harness; same construction as
tools/per_row_gain_c3_vet_v1.py and tools/orthographic_floor_vet_v1.py.

Run:  .venv/Scripts/python.exe tools/score_space_gain_and_topk_ci_v1.py [--smoke]
Output: data/exp_score_space_gain_and_topk_ci_v1[_smoke]/metrics.json (atomic os.replace).
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
ANCHOR_NAME = "exp_score_space_gain_and_topk_ci_v1" + ("_smoke" if SMOKE else "")
OUT = os.path.join(_REPO, "data", ANCHOR_NAME)
os.makedirs(OUT, exist_ok=True)

# 2026-08-23: KNOWN INFLATED, DELIBERATELY UNCHANGED -- see the same note in
# tools/per_row_gain_c3_vet_v1.py. ~78% of this bar is morphological leakage in the WordNet gold
# (0.0867 -> 0.0193 on stem-stripped gold, overlapping its own info-free twin). NOT lowered here:
# a gate is not weakened by the session whose results it constrains. Owner decision open as Q117.
ORTHO_BAR = 0.0870
ORTHO_BAR_CI = (0.0783, 0.0960)
SELF_RETRIEVAL_FLOOR = 0.70
PROJDRAW_SD_CEILING = 0.0024  # measured, exp_graded_path_vs_orthographic_floor_v1 (on=0.0009, off=0.0024)


def build_excitability_E(anchors: List[str], counts, pos: Dict[str, int], cap: int = 50) -> np.ndarray:
    """Genuine EWMA excitability per anchor -- identical construction to per_row_gain_c3_vet_v1.py."""
    E = EXC.init_E(len(anchors))
    cfg = EXC.EConfig()
    for a in anchors:
        i = pos[a]
        EXC.seed_on_write(E, i, cfg)
        n_events = min(int(counts.get(a, 0)), cap)
        for _ in range(n_events):
            EXC.bump_on_retrieval(E, i, 1.0, cfg)
    return E


def _gain_vector_from_gate(gate_fn, n_anchors: int, **kwargs) -> np.ndarray:
    """Extract the per-row multiplier a real hdlab.excitability gate function would apply, by
    calling it (unmodified) on a 1-column all-ones proxy array and reading the result off.
    Reuses the actual module logic; does not reimplement the threshold/selection math."""
    proxy = np.ones((n_anchors, 1), dtype=np.float64)
    gate_fn(proxy, **kwargs)
    return proxy[:, 0].copy()


def _gain_vector_from_magnitude_gate(mat: np.ndarray, mat_nrm_base: np.ndarray, threshold_frac: float,
                                     scale: float) -> np.ndarray:
    """downscale_gate_by_magnitude thresholds on the row's OWN norm, so it cannot run on a
    uniform proxy -- run it on a real copy of the base matrix and read the multiplier off the
    norm ratio (after/before), which equals scale for masked rows and 1.0 elsewhere."""
    m = mat.copy()
    EXC.downscale_gate_by_magnitude(m, threshold_frac=threshold_frac, scale=scale)
    after = np.linalg.norm(m, axis=1)
    return after / np.maximum(mat_nrm_base, 1e-12)


def _paired_ratio_bootstrap(hit_a: np.ndarray, top50_a: np.ndarray, hit_b: np.ndarray,
                            top50_b: np.ndarray, n_boot: int, seed: int) -> dict:
    """Paired bootstrap on the RATIO statistic hit@1 / frac_gold_in_top50 (conditional pick rate
    given the gold is retrieved), for two arms simultaneously resampled with the SAME item indices
    per draw (paired design, same convention as MS.paired_bootstrap)."""
    n = len(hit_a)
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(n_boot, n))
    ha, ta = hit_a[idx].mean(axis=1), top50_a[idx].mean(axis=1)
    hb, tb = hit_b[idx].mean(axis=1), top50_b[idx].mean(axis=1)
    ra = np.where(ta > 1e-9, ha / np.where(ta > 1e-9, ta, 1.0), np.nan)
    rb = np.where(tb > 1e-9, hb / np.where(tb > 1e-9, tb, 1.0), np.nan)
    delta = ra - rb
    valid = ~(np.isnan(ra) | np.isnan(rb))
    pa = float(hit_a.mean() / max(float(top50_a.mean()), 1e-12))
    pb = float(hit_b.mean() / max(float(top50_b.mean()), 1e-12))
    lo_a, hi_a = float(np.percentile(ra[valid], 2.5)), float(np.percentile(ra[valid], 97.5))
    lo_b, hi_b = float(np.percentile(rb[valid], 2.5)), float(np.percentile(rb[valid], 97.5))
    lo_d, hi_d = float(np.percentile(delta[valid], 2.5)), float(np.percentile(delta[valid], 97.5))
    return {
        "n_boot": n_boot, "n_boot_valid": int(valid.sum()), "seed": seed,
        "arm_a_conditional_pick_rate": {"point": pa, "ci_lo": lo_a, "ci_hi": hi_a},
        "arm_b_conditional_pick_rate": {"point": pb, "ci_lo": lo_b, "ci_hi": hi_b},
        "delta_a_minus_b": {"point": pa - pb, "ci_lo": lo_d, "ci_hi": hi_d,
                            "ci_excludes_zero": bool(lo_d > 0 or hi_d < 0)},
    }


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

    mat_nrm = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm >= 1e-9
    t_mat, t_cov = MS.trigram_matrix(anchors)

    # ---- excitability signal + score-space gain vectors (per-anchor, item-independent)
    E = build_excitability_E(anchors, counts, pos)
    med_E = float(np.median(E))

    gain_e_thresh = _gain_vector_from_gate(EXC.downscale_gate_by_E, n_anchors, E=E, scale=0.4,
                                           threshold=med_E)
    n_hit_e_thresh = int(np.sum(gain_e_thresh < 1.0))
    frac_matched = min(max(max(1, n_hit_e_thresh) / max(1, n_anchors), 0.01), 0.99)

    gain_e_cont = (0.5 + 1.5 * E)
    gain_random = _gain_vector_from_gate(EXC.downscale_gate_random, n_anchors, frac=frac_matched,
                                         scale=0.4, rng=np.random.RandomState(7))
    gain_magnitude = _gain_vector_from_magnitude_gate(mat, mat_nrm, threshold_frac=frac_matched,
                                                       scale=0.4)
    gain_global = np.full(n_anchors, 1.7, dtype=np.float64)

    gains: Dict[str, np.ndarray] = {
        "SCORE_GAIN_E_THRESH": gain_e_thresh,
        "SCORE_GAIN_E_CONTINUOUS": gain_e_cont,
        "SCORE_GAIN_RANDOM": gain_random,
        "SCORE_GAIN_MAGNITUDE": gain_magnitude,
        "SCORE_GAIN_GLOBAL": gain_global,
    }
    gain_arms = tuple(gains.keys())

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])

    donors = C3._derangement(n, lambda i, j: len({items[j]["L"], items[j]["G"], items[j]["F"]}
                                                  & {items[i]["L"], items[i]["G"], items[i]["F"]}) > 0)

    fixed_arms = ("A1_BASE", "A6_TRIGRAM_ONLY", "F_FREQUENCY")
    all_hit_arms = fixed_arms + gain_arms
    hits = {a: np.zeros(n, dtype=bool) for a in all_hit_arms}
    top50 = {a: np.zeros(n, dtype=bool) for a in all_hit_arms}
    ranks = {a: np.zeros(n, dtype=np.int64) for a in all_hit_arms}
    picks = {a: [] for a in all_hit_arms}
    identical_to_base = {a: np.zeros(n, dtype=bool) for a in gain_arms}
    scramble_hit = np.zeros(n, dtype=bool)

    anchor_arr = np.array(anchors)

    def _score_and_record(arm: str, sc: np.ndarray, sel: np.ndarray, gsel: np.ndarray,
                          gold: frozenset, i: int) -> None:
        b = int(np.argmax(sc))
        p = anchor_arr[sel[b]]
        picks[arm].append(str(p))
        hits[arm][i] = str(p) in gold
        if gsel.size:
            best_gold = float(np.max(sc[gsel]))
            r = int(np.sum(sc > best_gold)) + 1
            ranks[arm][i] = r
            top50[arm][i] = r <= 50
        else:
            ranks[arm][i] = sel.size

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
        gsel = np.array([j for j, a in enumerate(sel) if anchors[a] in gold], dtype=np.int64)

        q = space.bundle(L)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        base = (mat[sel] @ q) / (mat_nrm[sel] * qn)
        _score_and_record("A1_BASE", base, sel, gsel, gold, i)
        base_pick = picks["A1_BASE"][-1]

        tq = t_mat[pos[L]] if t_cov[pos[L]] else None
        trig = t_mat[sel] @ tq if tq is not None else np.zeros(sel.size)
        _score_and_record("A6_TRIGRAM_ONLY", trig, sel, gsel, gold, i)

        cnts = np.array([counts[anchors[a]] for a in sel], dtype=np.float64)
        _score_and_record("F_FREQUENCY", cnts, sel, gsel, gold, i)

        qd = space.bundle(items[donors[i]]["L"])
        qdn = float(np.linalg.norm(qd))
        if qdn >= 1e-9:
            scr = (mat[sel] @ qd) / (mat_nrm[sel] * qdn)
            scramble_hit[i] = anchor_arr[sel[int(np.argmax(scr))]] in gold

        for arm in gain_arms:
            sc = base * gains[arm][sel]
            _score_and_record(arm, sc, sel, gsel, gold, i)
            # "identical outcome" in SCORE space means the ARGMAX (pick) matches base -- unlike
            # the vector-space cancellation case, a score-space arm's raw scores are NOT expected
            # to numerically equal base's (e.g. SCORE_GAIN_GLOBAL = 1.7*base by construction); the
            # invariance claim under test is about the ranking outcome, not score magnitude.
            identical_to_base[arm][i] = (picks[arm][-1] == base_pick)

        if (i + 1) % 500 == 0:
            print("[score] %d/%d elapsed=%.1fs" % (i + 1, n, time.time() - t0), flush=True)

    # ---- KNOWN_ANSWER positive control (verbatim reuse of C3 / per-row-gain construction)
    rng_sr = np.random.default_rng(C3.MASTER_SEED + 61)
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
        sc = (mat[cand] @ q) / (mat_nrm[cand] * qn)
        pick_L = sc[0] >= sc[1]
        sr_hits += int(pick_L)
        sr_n += 1
    self_retrieval = round(sr_hits / max(1, sr_n), 6)

    # ---- JOB 1 bootstrap: gain arms vs A1_BASE
    armv = {a: hits[a].astype(float) for a in all_hit_arms}
    armv["SCRAMBLE"] = scramble_hit.astype(float)
    deltas = [("d_%s_minus_BASE" % a, a, "A1_BASE") for a in gain_arms]
    bs = MS.paired_bootstrap(armv, deltas, 5000, C3.MASTER_SEED + 71)

    bar_lo = ORTHO_BAR_CI[1]
    clears_bar = {a: bool(bs["arm_acc_ci"][a]["ci_lo"] > bar_lo) for a in gain_arms}
    delta_excludes_zero = {a: bool(bs["deltas"]["d_%s_minus_BASE" % a]["ci_excludes_zero"])
                           for a in gain_arms}
    exceeds_projdraw_sd = {a: bool(abs(bs["deltas"]["d_%s_minus_BASE" % a]["delta"]) > PROJDRAW_SD_CEILING)
                           for a in gain_arms}
    hard_pass = {a: bool(clears_bar[a] and delta_excludes_zero[a] and exceeds_projdraw_sd[a])
                for a in gain_arms}
    bitwise_identical_frac = {a: float(identical_to_base[a].mean()) for a in gain_arms}
    any_gain_arm_visible = any(bitwise_identical_frac[a] < 1.0 for a in
                               ("SCORE_GAIN_E_THRESH", "SCORE_GAIN_E_CONTINUOUS",
                                "SCORE_GAIN_RANDOM", "SCORE_GAIN_MAGNITUDE"))
    global_still_null = bitwise_identical_frac["SCORE_GAIN_GLOBAL"] == 1.0

    # ---- JOB 2 bootstrap: top-50 CI (paired) + conditional-pick-rate CI (paired ratio)
    top50_bs = MS.paired_bootstrap(
        {"OURS_TOP50": top50["A1_BASE"].astype(float), "SPELL_TOP50": top50["A6_TRIGRAM_ONLY"].astype(float)},
        [("d_top50_OURS_minus_SPELL", "OURS_TOP50", "SPELL_TOP50")], 5000, C3.MASTER_SEED + 81)
    conditional_bs = _paired_ratio_bootstrap(
        hits["A1_BASE"].astype(float), top50["A1_BASE"].astype(float),
        hits["A6_TRIGRAM_ONLY"].astype(float), top50["A6_TRIGRAM_ONLY"].astype(float),
        5000, C3.MASTER_SEED + 91)

    a1_matches_headline = abs(bs["arm_acc_ci"]["A1_BASE"]["acc"] - 0.048) < 1e-9 if not SMOKE else None
    a6_matches_bar = abs(bs["arm_acc_ci"]["A6_TRIGRAM_ONLY"]["acc"] - ORTHO_BAR) < 1e-9 if not SMOKE else None
    void_plumbing = bool((not SMOKE) and (
        (a1_matches_headline is False) or (a6_matches_bar is False) or self_retrieval < SELF_RETRIEVAL_FLOOR))

    clears_bar_ci_separated_job1 = any(hard_pass.values())
    top50_rates_ci_separable = bool(top50_bs["deltas"]["d_top50_OURS_minus_SPELL"]["ci_excludes_zero"])

    rep = {
        "anchor_name": ANCHOR_NAME,
        "what": "PRE-REGISTERED VET, two jobs: (1) excitability-style gain applied in SCORE space "
                "(not vector space) on C3's open-vocab read-out; (2) paired-bootstrap CI on the "
                "top-50-retrieval-vs-conditional-pick diagnosis. Identical items/pool/gold/scorer "
                "as exp_grounding_readout_known_answer_v1 / exp_orthographic_floor_vet_v1.",
        "prereg": "preregs/2026-08-15_score_space_gain_and_topk_ci_v1.md",
        "bar": {"source": "exp_orthographic_floor_vet_v1 A6_TRIGRAM_ONLY", "acc": ORTHO_BAR,
                "ci": list(ORTHO_BAR_CI),
                "rule": "CI-separated: arm ci_lo must exceed bar ci_hi (%.4f)" % bar_lo},
        "projdraw_sd_ceiling_reused_from": "exp_graded_path_vs_orthographic_floor_v1 (on=0.0009, off=0.0024)",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "smoke": SMOKE,
        "n_items": n, "n_anchors": n_anchors, "item_construction": diag,
        "void_plumbing_gate": {
            "a1_base_reproduces_0480_to_1e-9": a1_matches_headline,
            "a6_trigram_reproduces_0870_to_1e-9": a6_matches_bar,
            "self_retrieval": {"acc": self_retrieval, "n": sr_n, "floor": SELF_RETRIEVAL_FLOOR,
                               "ok": self_retrieval >= SELF_RETRIEVAL_FLOOR},
            "void": void_plumbing,
        },
        "job1_score_space_gain": {
            "excitability_signal": {"median_E": med_E, "n_rows_downscaled_by_E_thresh": n_hit_e_thresh,
                                    "frac_matched_for_random_and_magnitude_controls": frac_matched},
            "bootstrap": bs,
            "clears_bar_CI_separated": clears_bar,
            "delta_vs_A1_BASE_excludes_zero": delta_excludes_zero,
            "delta_exceeds_projdraw_sd_ceiling": exceeds_projdraw_sd,
            "HARD_PASS_per_arm": hard_pass,
            "any_gain_arm_HARD_PASS": clears_bar_ci_separated_job1,
            "bitwise_identical_pick_fraction_vs_A1_BASE": bitwise_identical_frac,
            "prediction_1_at_least_one_variable_gain_arm_changes_picks": any_gain_arm_visible,
            "prediction_2_uniform_global_gain_stays_bit_identical": global_still_null,
            "per_arm": {a: {"hit_at_1": float(hits[a].mean()), "example_picks": picks[a][:10]}
                       for a in gain_arms},
        },
        "job2_topk_ci": {
            "ours_A1_BASE": {"hit_at_1": float(hits["A1_BASE"].mean()),
                             "frac_gold_in_top50": float(top50["A1_BASE"].mean()),
                             "median_rank": float(np.median(ranks["A1_BASE"]))},
            "spelling_A6_TRIGRAM_ONLY": {"hit_at_1": float(hits["A6_TRIGRAM_ONLY"].mean()),
                                         "frac_gold_in_top50": float(top50["A6_TRIGRAM_ONLY"].mean()),
                                         "median_rank": float(np.median(ranks["A6_TRIGRAM_ONLY"]))},
            "reference_uncontrolled_numbers_from_2026-08-14_note": {
                "ours_frac_gold_in_top50": 0.5565, "spelling_frac_gold_in_top50": 0.5455,
                "ours_conditional_pick": 0.0863, "spelling_conditional_pick": 0.1595},
            "top50_rate_paired_bootstrap": top50_bs,
            "top50_rates_CI_separable": top50_rates_ci_separable,
            "conditional_pick_rate_paired_ratio_bootstrap": conditional_bs,
            "conditional_pick_rates_CI_separable": conditional_bs["delta_a_minus_b"]["ci_excludes_zero"],
        },
        "floors": {"F_FREQUENCY": float(hits["F_FREQUENCY"].mean()), "SCRAMBLE": float(scramble_hit.mean())},
        "elapsed_s": round(time.time() - t0, 2),
    }
    p = os.path.join(OUT, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print("A1_BASE reproduces 0.0480:", a1_matches_headline)
    print("A6_TRIGRAM_ONLY reproduces 0.0870:", a6_matches_bar)
    print("SELF_RETRIEVAL:", self_retrieval, "(floor 0.70)")
    print("VOID_PLUMBING:", void_plumbing)
    print("bitwise identical to A1_BASE (gain arms):", bitwise_identical_frac)
    print("JOB1 HARD_PASS per arm:", hard_pass)
    print("JOB2 top50 delta:", top50_bs["deltas"]["d_top50_OURS_minus_SPELL"])
    print("JOB2 conditional pick delta:", conditional_bs["delta_a_minus_b"])
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
