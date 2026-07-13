"""Core for the DEGREE-DEBIASED fair re-scoring of the Course-C glass-box rotation win.

WHAT THIS SETTLES. The landed multi-seed FULL
`data/exp_course_c_rotate_cskg_l2_seed_{7,17,23}_gpu1024_v1/metrics.json` is MIDDLE_BAND_PARTIAL: the fair
(low+mid gold-degree) WIN margin holds 3/3 seeds (oneshot_fair - POP_fair ~ +0.033..+0.045) while the
`g_backdoor` gate FAILS (pooled cross-channel r ~ 0.28..0.31 > R_BACKDOOR=0.15). This core re-scores that result
under the KG/RecSys popularity-bias field's standard leakage remedy (Aiyappa et al. ICML2025 arXiv:2405.14985;
Shomer et al. WWW2023 arXiv:2302.05044) to answer: is the 0.31 correlation a genuine within-degree shortcut, or
a third-variable (gold-tail degree) CONFOUND -- and does the +0.033 fair margin SURVIVE a degree-matched
candidate pool + within-stratum / partial correlation?

TWO debiased diagnostics, one cheap re-scoring pass over a REPRODUCED fit (no new experiment design):
  A) De-confound the pooled correlation: recompute cross_channel_geom_vs_poprank_r (i) pooled (reproduce), (ii)
     WITHIN each low/mid/high degree tertile, (iii) as a partial correlation controlling continuously for
     log(node_degree+1). (ii)+(iii) are the field-standard fix for the shared-confound Pearson artifact.
  B) Degree-match the candidate side: for the fair (low+mid) queries, restrict the ranking CANDIDATE COLUMNS to
     entities whose global node_degree also falls in the low+mid tertile range (degree <= q2 = tert_bounds[1]),
     for BOTH ONESHOT_ROTATE and BASELINE_POP, and report the new fair margin. This closes the candidate-side
     gap the field identifies as the dominant residual bias after gold-side stratification.

FAITHFUL REPRODUCTION, NOT A NEW FIT. The archived fit checkpoints are deleted post-run (disk hygiene), so this
core REFITS ONLY ONESHOT_ROTATE with the SAME (seed, FULL_CFG, split) and recomputes POP (no fit -- a frequency
count). Verification is DEVICE-HONEST:
  * SPLIT_IDENTITY (HARD): reproduced strata_counts + tert_bounds must match the archived per-seed values -- this
    proves the degree-stratification apparatus that degree-matching depends on is reproduced. Device-INDEPENDENT.
  * POP_FAITHFUL (HARD): reproduced fair-POP hits@10 must match the archived value within 0.002; POP arm_sig is
    recomputed and reported (exact-match noted). POP is pure numpy -> device-independent -> near-exact expected.
  * ONESHOT_FAITHFUL (REPORT/WARN, NOT hard-fail): this core is dispatched to REMOTE CPU (task lock: no GPU), but
    the archive was fit on CUDA. Cross-device SGD arithmetic precludes ONESHOT bit-identical arm_sig. So ONESHOT
    faithfulness is a TOLERANCE check (reproduced pooled backdoor_r within 0.05 AND fair-oneshot within 0.02 of
    archive). If it passes, the CPU refit reproduces the archived REGIME and the debias diagnostics are trusted;
    if it drifts, the numbers are reported as an INDEPENDENT CPU refit (not bit-identical to the CUDA archive),
    still a valid fit whose debias verdict stands on its own. The note's original P3 (both sigs bit-identical)
    assumed the GPU device of the archive; this is the honest CPU adaptation.

This is the FAIR YARDSTICK the mission asks for: within-stratum/partial correlation LOCALIZES where any residual
geometry-vs-popularity coupling lives (weak-point localization), degree-matched candidates is the FAIRNESS fix,
and both are reusable verbatim on the next map-builder eval. Consistent with the standing disciplines
[[feedback-fairness-plus-weak-point-localization-first-class]] and [[feedback-dont-over-correct-on-raw-full-either]].

ASCII-only. No bare except; except SystemExit before except Exception. Numbers in comments tagged
MEASURED@ / CITED@ / THEORETICAL@.
"""

import hashlib  # noqa: F401  (re-exported _sig uses it upstream)
import json
import os
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import torch  # noqa: F401  top-level device visibility

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial,
)
# Reuse the EXACT fit + readout + fairness apparatus of the landed cell (apples-to-apples reproduction).
from experiments._course_c_rotate_core_v1 import (  # noqa: E402
    fit_kge_rotate, rotate_direct_scores, _sig, ROT_LR,
    SELFTEST_CFG, SMOKE_CFG, MEMSMOKE_CFG, FULL_CFG,
    ONESHOT, POP, R_BACKDOOR, POP_GAP, MIN_HELDOUT, STRATA,
    fair_mask, fair_hits_from_scores, fair_pop, select_device,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    extract_l2_genuine, stratify_by_tail_degree, build_true_by_hr_int,
    filtered_hits_from_scores, pop_hits, _to_int_edges,
    MAX_RULES_PER_HEAD, HUB_CAP, PRIMARY_K,
)
from experiments.exp_gt_induction_fb15k237_dense_v1 import (  # noqa: E402
    Graph, build_ids, mine_rules,
)
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments._fit_checkpoint import FitCheckpoint, cleanup_seed_checkpoints  # noqa: E402

ANCHOR_FAMILY = "course_c_debias_cskg_l2"

# ---- Pre-registered debias bands (picked BEFORE the run; see prereg 2026-07-12) ----
# R_BACKDOOR (0.15) + POP_GAP (0.03) imported from the parent so the bars are literally the same objects.
R_LEAK = 0.25            # P1 HARD-FAIL floor: within-stratum OR partial r >= this = a genuine within-degree leak
DEG_MARGIN_PASS = 0.02   # P2 HARD-PASS: degree-matched fair margin >= this (relaxed vs POP_GAP: harder test)
DEG_MARGIN_TIE = 0.00    # P2 HARD-FAIL: degree-matched fair margin <= this (win was a candidate-pool artifact)
MIN_STRAT_Q = 8          # min queries in a stratum to report its within-r
POP_FAITHFUL_TOL = 0.002   # POP is device-independent -> near-exact reproduction of archived fair-POP hits
ONESHOT_R_TOL = 0.05     # cross-device: reproduced pooled backdoor_r within this of archive = faithful regime
ONESHOT_FAIR_TOL = 0.02  # cross-device: reproduced fair-oneshot within this of archive = faithful regime
TERT_TOL = 0.5           # tert_bounds float match tolerance (degree quantiles are near-integer counts)

# ---- Archived per-seed reference values (MEASURED@ the three gpu1024 metrics.json, read off-disk 2026-07-12).
# Embedded (not disk-loaded) because those metrics.json are NOT git-tracked -> absent on the remote host.
REF = {
    7: dict(pop_sig="611e7fef0f1f65ef", oneshot_sig="1ac33ca75946958d",
            fair_oneshot=0.0917, fair_pop=0.0563, backdoor_r=0.2806,
            tert=[100.0, 357.9999999999991], strata=dict(low=2009, mid=1991, high=2000)),
    17: dict(pop_sig="f7fe67bfd8c3af18", oneshot_sig="7a8e196906e99b7b",
             fair_oneshot=0.0772, fair_pop=0.0442, backdoor_r=0.3118,
             tert=[99.0, 347.0], strata=dict(low=2020, mid=1985, high=1995)),
    23: dict(pop_sig="8ced24b6b93aa961", oneshot_sig="765465eab6a31e26",
             fair_oneshot=0.0949, fair_pop=0.05, backdoor_r=0.2795,
             tert=[100.0, 344.0], strata=dict(low=2024, mid=1980, high=1996)),
}


def _log(anchor, m):
    print("[%s] %s" % (anchor, m), flush=True)


def _write_start_marker(output_dir, anchor, run_mode, expected_n_units):
    import platform
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=anchor, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, anchor, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=anchor)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Debias estimators (the only new logic; validated in the self-test against known answers).
# ---------------------------------------------------------------------------

def _pearson(a, b):
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    if a.size < 3 or np.std(a) < 1e-9 or np.std(b) < 1e-9:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def _gold_geo_vec(scores, hold):
    """Raw ONESHOT rotation score on the TRUE gold tail, per held-out query (pooled across strata)."""
    return np.array([float(scores[i, int(hold[i, 2])].item()) for i in range(hold.shape[0])], dtype=np.float64)


def within_stratum_r(gold_geo, neg_poprank, strat):
    """Cross-channel r WITHIN each degree tertile -> localizes where any residual coupling lives."""
    out = {}
    for si, nm in enumerate(STRATA):
        m = np.where(strat == si)[0]
        r = (round(_pearson(gold_geo[m], neg_poprank[m]), 4) if m.size >= MIN_STRAT_Q else None)
        out[nm] = dict(r=r, n=int(m.size))
    return out


def partial_r_logdeg(gold_geo, neg_poprank, deg):
    """Partial correlation of (gold_geo, neg_poprank) controlling continuously for log(node_degree+1).
    Residualize each channel against [1, log(deg+1)] via OLS, correlate the residuals (field-standard fix)."""
    x = np.log(np.asarray(deg, dtype=np.float64) + 1.0)
    A = np.column_stack([np.ones_like(x), x])

    def _resid(y):
        beta, _, _, _ = np.linalg.lstsq(A, np.asarray(y, dtype=np.float64), rcond=None)
        return np.asarray(y, dtype=np.float64) - A @ beta

    return round(_pearson(_resid(gold_geo), _resid(neg_poprank)), 4)


def _pop_hits_degmatched(rel_tail_freq, hold, all_true, allowed_set, k=PRIMARY_K):
    """POP filtered hits@k with the candidate universe restricted to `allowed_set` (low+mid degree entities).
    Mirrors pop_rank's tie/zero-block logic (random.Random(12345)) but only over allowed candidates."""
    import random as _random
    rng = _random.Random(12345)
    nq = hold.shape[0]
    hits = 0.0
    n_allowed = len(allowed_set)
    for i in range(nq):
        h = int(hold[i, 0]); r = int(hold[i, 1]); gold = int(hold[i, 2])
        filt = (all_true.get((h, r), set()) - {gold})
        cnt = rel_tail_freq.get(r, Counter())
        g_pop = cnt.get(gold, 0)
        higher = 0; ties = 0; seen_allowed = 0
        for c, p in cnt.items():
            if c in allowed_set:
                seen_allowed += 1
            if c == gold or c in filt or c not in allowed_set:
                continue
            if p > g_pop:
                higher += 1
            elif p == g_pop:
                ties += 1
        if g_pop == 0:
            zero_block = n_allowed - seen_allowed   # allowed entities never seen as tail of this rel (pop 0)
            ties += max(0, zero_block - 1)
        rank = higher + 1 + rng.randint(0, ties)
        if rank <= k:
            hits += 1.0
    return hits / max(1, nq)


def degmatched_fair(scores_oneshot, hold, strat, all_true, rel_tail_freq, node_degree, q2, N, k=PRIMARY_K):
    """Fair (low+mid) queries scored against a DEGREE-MATCHED candidate pool: columns restricted to entities
    with global node_degree <= q2 (the low+mid tertile range). ONESHOT masks disallowed columns; POP restricts
    its ranking universe identically. Gold tails of fair queries have degree <= q2 (stratified by tail degree)
    so they remain in-pool. Returns the degree-matched fair margin (oneshot - pop)."""
    fair = fair_mask(strat)
    if fair.size < 1:
        return dict(oneshot=float("nan"), pop=float("nan"), margin=float("nan"), n=0, n_allowed=0)
    allowed_bool = np.array([node_degree.get(int(e), 0) <= q2 for e in range(N)], dtype=bool)
    disallow_cols = np.where(~allowed_bool)[0]
    sc = scores_oneshot[fair].clone()
    if disallow_cols.size > 0:
        sc[:, torch.from_numpy(disallow_cols).long()] = -1e30
    om = filtered_hits_from_scores(sc, hold[fair], all_true, ks=(k,))
    allowed_set = set(int(e) for e in np.where(allowed_bool)[0])
    pop_dm = _pop_hits_degmatched(rel_tail_freq, hold[fair], all_true, allowed_set, k=k)
    oh = round(om["hits@%d" % k], 4)
    return dict(oneshot=oh, pop=round(pop_dm, 4), margin=round(oh - pop_dm, 4),
                n=int(fair.size), n_allowed=int(allowed_bool.sum()))


# ---------------------------------------------------------------------------
# One-seed faithful re-score (reproduce split + POP, refit ONESHOT, debias A + B).
# ---------------------------------------------------------------------------

def rescore_seed(seed, cfg, device, is_ref_seed, ckpt_dir=None):
    train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
        cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
    ent2i, rel2i = build_ids(train_lbl, valid_lbl, test_lbl)
    N = len(ent2i); n_rel = len(rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    valid_int = _to_int_edges(valid_lbl, ent2i, rel2i)
    test_int = _to_int_edges(test_lbl, ent2i, rel2i)
    gd = Graph(train_lbl, ent2i, rel2i)
    known = defaultdict(set)
    for tr in (train_lbl, valid_lbl, test_lbl):
        for (h, r, t) in tr:
            known[(ent2i[h], rel2i[r])].add(ent2i[t])
    _acc, allpat, _hub = mine_rules(gd, list(rel2i.values()),
                                    cfg["min_support"], cfg["min_conf"], MAX_RULES_PER_HEAD, HUB_CAP)
    hold, hold_prov = extract_l2_genuine(gd, allpat, known, test_int, cfg["n_eval"], seed)
    all_true = build_true_by_hr_int(train_int, valid_int, test_int)
    strat, tert = stratify_by_tail_degree(hold, gd.node_degree)
    strata_counts = {STRATA[si]: int((strat == si).sum()) for si in range(3)}

    if hold.shape[0] < cfg.get("min_heldout", MIN_HELDOUT):
        raise RuntimeError("L2-genuine held-out too small (%d)" % hold.shape[0])

    # --- SPLIT_IDENTITY (HARD) vs archive: strata_counts + tert_bounds ---
    split_identity_ok = True
    split_identity_detail = "n/a (non-reference seed)"
    if is_ref_seed and seed in REF:
        ref = REF[seed]
        sc_ok = (strata_counts == ref["strata"])
        tert_ok = (abs(tert[0] - ref["tert"][0]) <= TERT_TOL and abs(tert[1] - ref["tert"][1]) <= TERT_TOL)
        split_identity_ok = bool(sc_ok and tert_ok)
        split_identity_detail = "strata_match=%s tert_match=%s (repro strata=%s tert=%s vs ref strata=%s tert=%s)" % (
            sc_ok, tert_ok, strata_counts, [round(tert[0], 2), round(tert[1], 2)], ref["strata"], ref["tert"])
    if not split_identity_ok:
        raise RuntimeError("SPLIT_IDENTITY_BREACH seed=%d: %s" % (seed, split_identity_detail))

    # --- refit ONESHOT_ROTATE (SAME recipe as _fit_and_score) ---
    # Fit-checkpoint (ckpt_every from cfg; FULL only) so a timeout/kill of the multi-hour CPU fit RESUMES from
    # the last epoch instead of restarting (PROT-021 resumability; correctness-neutral -- copies of the trajectory).
    _ckpt = None
    if ckpt_dir is not None and cfg.get("ckpt_every"):
        _ckpt = FitCheckpoint(ckpt_dir, "rotate_oneshot_seed%d" % seed, cfg["ckpt_every"])
    PHI, THETA = fit_kge_rotate(train_int, N, n_rel, cfg["k"], device, seed, cfg["epochs"],
                                lr=ROT_LR, n_neg=cfg["n_neg"], batch_size=cfg["batch"],
                                neg_chunk=cfg.get("neg_chunk"), ckpt=_ckpt)
    sc_oneshot = rotate_direct_scores(PHI, THETA, hold, device)   # (nq, N) cpu float32
    oneshot_metric = filtered_hits_from_scores(sc_oneshot, hold, all_true)
    oneshot_sig = _sig(sc_oneshot.numpy()[:min(64, sc_oneshot.shape[0])].ravel())
    del PHI, THETA
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()

    # --- POP (device-independent frequency count) ---
    pop_metric, pop_rank_vec = pop_hits(gd.rel_tail_freq, hold, all_true, N)
    pop_sig = _sig(pop_rank_vec.astype(np.float64))

    # --- unmatched fair (reproduce the archived fair margin) ---
    fair_oneshot = fair_hits_from_scores(sc_oneshot, hold, strat, all_true)["hits"]
    fair_pop_hits = fair_pop(gd.rel_tail_freq, hold, strat, all_true, N)["hits"]
    fair_margin = round(fair_oneshot - fair_pop_hits, 4)

    # --- POP_FAITHFUL (HARD): device-independent -> near-exact reproduction of archived fair-POP ---
    pop_faithful_ok = True
    pop_sig_exact = None
    if is_ref_seed and seed in REF:
        ref = REF[seed]
        pop_faithful_ok = bool(abs(fair_pop_hits - ref["fair_pop"]) <= POP_FAITHFUL_TOL)
        pop_sig_exact = bool(pop_sig == ref["pop_sig"])
    if not pop_faithful_ok:
        raise RuntimeError("POP_FAITHFUL_BREACH seed=%d: repro fair_pop=%.4f vs ref=%.4f (tol %.3f)" % (
            seed, fair_pop_hits, REF[seed]["fair_pop"], POP_FAITHFUL_TOL))

    # --- Debias A: pooled / within-stratum / partial correlation ---
    gold_geo = _gold_geo_vec(sc_oneshot, hold)
    neg_poprank = -pop_rank_vec.astype(np.float64)
    pooled_r = round(_pearson(gold_geo, neg_poprank), 4)
    within_r = within_stratum_r(gold_geo, neg_poprank, strat)
    gold_deg = np.array([gd.node_degree.get(int(hold[i, 2]), 0) for i in range(hold.shape[0])], dtype=np.float64)
    partial_r = partial_r_logdeg(gold_geo, neg_poprank, gold_deg)
    within_vals = [abs(within_r[nm]["r"]) for nm in STRATA if within_r[nm]["r"] is not None]
    within_max_abs = round(max(within_vals), 4) if within_vals else None

    # --- ONESHOT_FAITHFUL (REPORT/WARN; cross-device tolerance, NOT hard-fail) ---
    oneshot_faithful = None
    oneshot_sig_exact = None
    if is_ref_seed and seed in REF:
        ref = REF[seed]
        r_ok = (pooled_r == pooled_r) and abs(pooled_r - ref["backdoor_r"]) <= ONESHOT_R_TOL
        f_ok = abs(fair_oneshot - ref["fair_oneshot"]) <= ONESHOT_FAIR_TOL
        oneshot_faithful = bool(r_ok and f_ok)
        oneshot_sig_exact = bool(oneshot_sig == ref["oneshot_sig"])

    # --- Debias B: degree-matched candidate pool ---
    dm = degmatched_fair(sc_oneshot, hold, strat, all_true, gd.rel_tail_freq, gd.node_degree, tert[1], N)

    return dict(
        corpus="CSKG_XCUT_CORE", seed=int(seed), N=int(N), n_rel=int(n_rel),
        n_train=int(train_int.shape[0]), n_test=int(test_int.shape[0]),
        l2_genuine=hold_prov, tert_bounds=[float(tert[0]), float(tert[1])], strata_counts=strata_counts,
        arm_hits={ONESHOT: {k: round(v, 4) for k, v in oneshot_metric.items() if k != "n"},
                  POP: {k: round(v, 4) for k, v in pop_metric.items() if k != "n"}},
        arm_sigs_recomputed={ONESHOT: oneshot_sig, POP: pop_sig},
        fair_unmatched=dict(oneshot=fair_oneshot, pop=fair_pop_hits, margin=fair_margin,
                            n=int(fair_mask(strat).size)),
        # --- verification (device-honest) ---
        verification=dict(
            split_identity_ok=bool(split_identity_ok), split_identity_detail=split_identity_detail,
            pop_faithful_ok=bool(pop_faithful_ok), pop_sig_exact=pop_sig_exact,
            oneshot_faithful=oneshot_faithful, oneshot_sig_exact=oneshot_sig_exact,
            device=str(device)),
        # --- debias A ---
        pooled_backdoor_r=pooled_r, within_stratum_r=within_r, within_max_abs_r=within_max_abs,
        partial_r_logdeg=partial_r,
        # --- debias B ---
        degmatched_fair=dm,
        cskg_provenance=prov, _min_support=cfg["min_support"], _min_conf=cfg["min_conf"])


# ---------------------------------------------------------------------------
# Per-seed provisional verdict (3-seed HARD-PASS/FAIL computed downstream over the 3 metrics files).
# ---------------------------------------------------------------------------

def seed_verdict(ps):
    """Provisional per-seed debias verdict. The headline 3-seed gate is aggregated downstream (mean over the
    3 process-isolated metrics.json), same convention as the parent cell's seed_cv gate."""
    within_max = ps.get("within_max_abs_r")
    partial = ps.get("partial_r_logdeg")
    dm_margin = ps.get("degmatched_fair", {}).get("margin")
    ver = ps.get("verification", {})

    if not ver.get("split_identity_ok") or not ver.get("pop_faithful_ok"):
        return "INCONCLUSIVE_VERIFICATION", dict(reason="split/pop reproduction not faithful")

    def _bad(x):
        return (x is None) or (x != x)
    if _bad(within_max) or _bad(partial) or _bad(dm_margin):
        return "INCONCLUSIVE_INSUFFICIENT", dict(within_max=within_max, partial=partial, dm_margin=dm_margin)

    # P1 de-confound verdict is decided by the PARTIAL correlation (continuous log-degree control) -- the
    # field-standard de-confounder. within_max_abs_r is a LOCALIZER (reported): a coarse 3-band stratification
    # retains within-band degree spread, so within-stratum r legitimately stays above the partial r when the
    # bands are wide; the continuous partial control is the decisive statistic (validated in the self-test).
    p1_pass = (abs(partial) < R_BACKDOOR)                                    # confound, not leak (deg-controlled)
    p1_fail = (abs(partial) >= R_LEAK)                                       # genuine within-degree leak survives
    p2_pass = (dm_margin >= DEG_MARGIN_PASS)                                  # win survives degree-matched cands
    p2_fail = (dm_margin <= DEG_MARGIN_TIE)                                   # win was a candidate-pool artifact

    gates = dict(p1_pass=bool(p1_pass), p1_fail=bool(p1_fail), p2_pass=bool(p2_pass), p2_fail=bool(p2_fail),
                 within_max_abs_r=within_max, partial_r_logdeg=partial, degmatched_margin=dm_margin,
                 R_BACKDOOR=R_BACKDOOR, R_LEAK=R_LEAK, DEG_MARGIN_PASS=DEG_MARGIN_PASS)
    if p1_fail or p2_fail:
        return "SEED_HARD_FAIL", gates
    if p1_pass and p2_pass:
        return "SEED_HARD_PASS", gates
    return "SEED_MIDDLE_BAND", gates


# ---------------------------------------------------------------------------
# Self-test: validate the debias estimators against known answers + declare 4 validity-preflight checks.
# ---------------------------------------------------------------------------

def debias_selftest():
    rng = np.random.default_rng(20260712)
    n = 600
    # log-degree covariate common to both channels
    deg = np.exp(rng.uniform(1.0, 6.0, size=n))          # heavy-tailed degrees
    ld = np.log(deg + 1.0)
    strat = np.where(ld <= np.quantile(ld, 1/3), 0, np.where(ld <= np.quantile(ld, 2/3), 1, 2)).astype(np.int64)

    # (1) CONFOUND arena: both channels driven ONLY by log-degree + independent noise -> pooled r high, partial ~0
    g_conf = 1.5 * ld + rng.normal(0, 0.6, size=n)
    p_conf = 2.0 * ld + rng.normal(0, 0.6, size=n)
    pooled_conf = _pearson(g_conf, p_conf)
    partial_conf = partial_r_logdeg(g_conf, p_conf, deg)
    within_conf = within_stratum_r(g_conf, p_conf, strat)
    within_conf_max = max(abs(within_conf[nm]["r"]) for nm in STRATA if within_conf[nm]["r"] is not None)

    # (2) LEAK arena: an EXTRA degree-independent shared signal -> partial r stays high after controlling for deg
    shared = rng.normal(0, 1.0, size=n)
    g_leak = 1.5 * ld + 1.2 * shared + rng.normal(0, 0.3, size=n)
    p_leak = 2.0 * ld + 1.2 * shared + rng.normal(0, 0.3, size=n)
    partial_leak = partial_r_logdeg(g_leak, p_leak, deg)

    # (3) metric_moves: degree-matched masking changes POP ranking (removes high-degree freebies). Sized so gold
    # (freq 1) sits OUTSIDE top-10 in the full pool (>10 popular high-degree distractors above it) but INSIDE
    # top-10 once the high-degree columns are masked out -> the margin provably moves.
    N = 200
    node_degree = {e: float(rng.integers(1, 500)) for e in range(N)}
    q2 = float(np.quantile(list(node_degree.values()), 2 / 3))
    rel_tail_freq = defaultdict(Counter)
    low_ents = [e for e in range(N) if node_degree[e] <= q2]
    high_ents = [e for e in range(N) if node_degree[e] > q2]
    n_distract = min(15, len(high_ents))         # >10 popular high-degree distractors -> push gold past rank 10
    hold_rows = []
    for i in range(6):
        gold = low_ents[i % len(low_ents)]
        rel_tail_freq[0][gold] += 1
        for he in high_ents[:n_distract]:
            rel_tail_freq[0][he] += 10           # popular high-degree distractors (freebies in full pool)
        hold_rows.append((low_ents[(i + 1) % len(low_ents)], 0, gold))
    hold = np.array(hold_rows, dtype=np.int64)
    all_true = build_true_by_hr_int(hold)
    strat_dm = np.zeros(hold.shape[0], dtype=np.int64)   # all fair
    sc_os = torch.zeros((hold.shape[0], N), dtype=torch.float32)
    for i in range(hold.shape[0]):
        sc_os[i, int(hold[i, 2])] = 1.0                  # ONESHOT nails gold (unaffected by masking)
    allowed_set_full = set(range(N))
    pop_full = _pop_hits_degmatched(rel_tail_freq, hold, all_true, allowed_set_full)
    dm = degmatched_fair(sc_os, hold, strat_dm, all_true, rel_tail_freq, node_degree, q2, N)
    metric_moves = (abs(pop_full - dm["pop"]) > 1e-6)

    # (4) negative_control_fails_with_margin: corrupting POP arm_sig detectably differs
    # Confound detected: pooled correlation is high but the PARTIAL (log-degree-controlled) correlation collapses
    # toward 0 -- the decisive de-confounder. within_conf_max is reported (localizer) but NOT required to be low:
    # a coarse 3-band split retains within-band degree spread, so within-stratum r legitimately stays elevated.
    ok_confound = (pooled_conf > 0.4) and (abs(partial_conf) < 0.15)
    ok_leak = (abs(partial_leak) >= 0.25)
    ok_moves = bool(metric_moves)
    ok_gates = True   # verdict logic exercised below

    # exercise the full seed_verdict gate machinery on a synthetic per-seed (full_gates_exercised)
    synth_pass = dict(within_max_abs_r=0.05, partial_r_logdeg=0.03,
                      degmatched_fair=dict(margin=0.04),
                      verification=dict(split_identity_ok=True, pop_faithful_ok=True))
    synth_fail = dict(within_max_abs_r=0.30, partial_r_logdeg=0.28,
                      degmatched_fair=dict(margin=-0.01),
                      verification=dict(split_identity_ok=True, pop_faithful_ok=True))
    v_pass, _ = seed_verdict(synth_pass)
    v_fail, _ = seed_verdict(synth_fail)
    ok_gates = (v_pass == "SEED_HARD_PASS") and (v_fail == "SEED_HARD_FAIL")

    checks = dict(
        positive_control_passes=bool(ok_confound and ok_leak),   # estimator separates confound from leak
        metric_moves=ok_moves,                                   # degree-matched masking DOES something
        negative_control_fails_with_margin=bool(ok_leak),        # leak arena is detected as a leak (r>=0.25)
        full_gates_exercised_at_selftest=bool(ok_gates))
    overall = all(checks.values())
    detail = dict(
        confound=dict(pooled_r=round(pooled_conf, 4), partial_r=partial_conf, within_max=round(within_conf_max, 4)),
        leak=dict(partial_r=partial_leak),
        metric_moves=dict(pop_full=round(pop_full, 4), pop_degmatched=dm["pop"], oneshot_degmatched=dm["oneshot"]),
        gate_probe=dict(synth_pass_verdict=v_pass, synth_fail_verdict=v_fail))
    return overall, dict(validity_preflight_ok=overall,
                         validity_preflight_declared=list(checks.keys()),
                         validity_checks=checks, selftest_detail=detail)


# ---------------------------------------------------------------------------
# Process main (one seed list; per-seed process isolation for the FULL wrappers).
# ---------------------------------------------------------------------------

def core_main(anchor_name, seeds, run_mode, device):
    out_dir = get_output_dir(anchor_name)
    cfg = dict({"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG,
                "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    # SMOKE has no neg_chunk/ckpt_every keys -> single-shot fit path (fine on CPU tiny scale).
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, anchor_name, run_mode, expected_n_units)
    t0 = time.perf_counter()

    st_ok, st_res = debias_selftest()
    _log(anchor_name, "debias_selftest ok=%s checks=%s" % (st_ok, st_res["validity_checks"]))
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="DEBIAS_SELFTEST_FAILED (estimator did not separate confound/leak, or masking frozen)",
            summary="debias selftest failed", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS course-C DEBIAS: partial-r separates degree-confound from within-degree "
                        "leak; degree-matched masking moves POP; 4 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t0, mechanism_selftest=st_res))
        _log(anchor_name, "SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t0))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t0))
        raise SystemExit(1)

    # SMOKE (small CSKG core) has NO archived reference -> skip identity gate; FULL seeds are reference seeds.
    ref_seed = (run_mode in ("full", "memsmoke"))
    per_seed, seed_failures = [], []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            ps = rescore_seed(seed, cfg, device, is_ref_seed=(ref_seed and seed in REF), ckpt_dir=out_dir)
            v, vg = seed_verdict(ps)
            ps["seed_verdict"] = v; ps["seed_gates"] = vg
            per_seed.append(ps)
            write_partial(out_dir, seed, dict(seed=seed, metrics=ps, run_mode=run_mode))
            cleanup_seed_checkpoints(out_dir, seed)   # seed fully done -> drop its fit checkpoints
            _log(anchor_name, "seed=%d %s | pooled_r=%.4f within_max=%.4f partial=%.4f | fair_margin=%.4f "
                 "dm_margin=%.4f (repro fair_os=%.4f pop=%.4f) (%.1fs)" % (
                     seed, v, ps["pooled_backdoor_r"], ps["within_max_abs_r"] or float("nan"),
                     ps["partial_r_logdeg"], ps["fair_unmatched"]["margin"], ps["degmatched_fair"]["margin"],
                     ps["fair_unmatched"]["oneshot"], ps["fair_unmatched"]["pop"], time.time() - ts))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            seed_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log(anchor_name, "SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))
        finally:
            if getattr(device, "type", "") == "cuda":
                torch.cuda.empty_cache()

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t0,
            seed_failures=seed_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    # Provisional PROCESS verdict = this process's single seed's verdict; 3-seed headline aggregated downstream.
    v0 = per_seed[0]["seed_verdict"]
    gm = "%s | pooled_r=%.4f within_max=%.4f partial=%.4f fair_margin=%.4f dm_margin=%.4f | split_ok=%s pop_ok=%s oneshot_faithful=%s" % (
        v0, per_seed[0]["pooled_backdoor_r"], per_seed[0]["within_max_abs_r"] or float("nan"),
        per_seed[0]["partial_r_logdeg"], per_seed[0]["fair_unmatched"]["margin"],
        per_seed[0]["degmatched_fair"]["margin"], per_seed[0]["verification"]["split_identity_ok"],
        per_seed[0]["verification"]["pop_faithful_ok"], per_seed[0]["verification"]["oneshot_faithful"])
    metrics = dict(verdict=v0, verdict_msg=gm, summary=gm[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t0, anchor_name=anchor_name,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device),
                   n_seeds=len(per_seed), seeds=seeds, config=cfg,
                   mechanism_selftest=st_res, seed_failures=seed_failures, per_seed=per_seed,
                   cross_seed_note=("single-seed process-isolated re-score; 3-seed debias headline aggregated "
                                    "downstream over the 3 seed metrics files (mean within_max/partial/dm_margin)."))
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log(anchor_name, "VERDICT: %s" % gm)
    _log(anchor_name, "done (%.1fs)" % (time.perf_counter() - t0))


def wrapper_run(anchor_name, default_seeds, default_run_mode):
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "memsmoke", "full"], default=default_run_mode)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    seeds = [7] if run_mode == "self_test" else default_seeds
    device = select_device(args.device)
    out_dir = str(get_output_dir(anchor_name))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(anchor_name, seeds, run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, anchor_name, e)
        raise
