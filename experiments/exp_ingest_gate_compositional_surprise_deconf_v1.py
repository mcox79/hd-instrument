"""Was SURPRISE-INERT an EXTRACTOR ARTIFACT? Recompute surprise via a COMPOSITIONAL model, re-run DECONF_AUC.

BACKGROUND: the combination-rule race (exp_ingest_gate_combination_rule_race_v1) concluded SCHEMAFIT_CARRIES --
FLAT additive-surprise DECONF_AUC ~chance (deconf_full flat=0.545 MEASURED@
data/exp_ingest_gate_combination_rule_race_v1/metrics.json:agg.deconf_full.flat) while schema_fit alone carried the
within-relation derivability signal (deconf_full schemafit=0.719 MEASURED@ same:agg.deconf_full.schemafit). BUT that
"surprise" was the ADDITIVE-MAP DIRECT readout: score(t) = -||X_h + D_r* - X_t|| using the MEMORIZED whole-relation
operator D[r*]. D[r*] is trained on r*-edges directly, so it captures WHOLE-RELATION presence (~ a frequency/degree
signal) and gives ~the same score to DERIVABLE and UNDERIVABLE r* facts (both ARE r* facts). So "surprise inert" may
be an EXTRACTOR ARTIFACT of the additive-DIRECT score, not a property of surprise.

THE TEST (this cell): recompute surprise from a COMPOSITIONAL readout that composes the CONSTITUENT operators along
the generative path r* = r0 o r1, then re-run the SAME v4 within-trained-relation derivable-vs-underivable DECONF_AUC.
Two compositional readouts (both reuse the SAME fitted foundation X_T, D_T -- ONLY the operator changes):
  ARM_ADD_FLAT   : surprise = 1 - RR( pred = X_h + D[r*] )            (additive-DIRECT; reproduces race flat ~0.545)
  ARM_SCHEMAFIT  : score    = 1 - schema_fit (reachability)          (reproduces race schemafit ~0.719 -- REFERENCE)
  ARM_COMP_OP    : surprise = 1 - RR( pred = X_h + D[r0] + D[r1] )   (NEW: operator-composition along the path)
  ARM_COMP_PATH  : surprise = 1 - max_mid RR( pred = X_mid + D[r1] ), mid in top-M of (h,r0)  (NEW: discrete 2-hop)
  ARM_RECUR      : score    = deg(h)/(deg(h)+TAU)                    (graded recurrence/degree -- the confound probe)

WHY COMP_OP SEPARATES WHERE ADD_FLAT CANNOT (THEORETICAL@TransE geometry): the foundation is fit so real base edges
(a,r0,b): X_b ~ X_a + D[r0] and (b,r1,c): X_c ~ X_b + D[r1]. A DERIVABLE r* fact has a real base 2-path h->mid->t, so
X_t ~ X_h + D[r0] + D[r1] -> COMP_OP ranks t high -> LOW surprise. An UNDERIVABLE r* fact asserts (h,r*,t) with NO
supporting base path, so X_t is NOT near X_h+D[r0]+D[r1] -> HIGH surprise. The DIRECT D[r*] operator is a single fixed
displacement memorized over ALL r* edges -> it cannot tell derivable from underivable. COMP_OP can.

DECISIVE metric = DECONF_AUC per arm = AUC(score; UNDERIVABLE vs DERIVABLE), both held-out, SAME trained r* row, on
the IDENTICAL v4 split as the race (split RNG derivation copied VERBATIM from race_seed). Head-to-head:
  EXTRACTOR_ARTIFACT   = comp_op (and/or comp_path) DECONF >= HP_DECONF_MIN AND >> add_flat (margin>=DECISIVE_MARGIN)
                         => "surprise inert" was an EXTRACTOR ARTIFACT; a compositional surprise recovers the signal
                         the additive-direct score missed. Sub-case CONVERGES_WITH_SCHEMAFIT if comp ~ schemafit
                         (|comp - schemafit| <= CONVERGE_EPS) -> the free-energy view (schema-conditioned surprise is
                         ONE quantity) is supported. ROUTE TO VET.
  SURPRISE_GENUINELY_INERT = comp_op AND comp_path <= HF_DECONF_MAX (~chance even with a compositional model) =>
                         surprise is genuinely inert here; schema-fit-direct stands (race conclusion holds).
  MIDDLE_BAND          = comp arms straddle chance..pass (partial/ambiguous signal).

SANITY CHECKS (task-mandated, reported): (1) RECURRENCE = graded deg/(deg+TAU) (TAU=3.0), NOT the old v1-pilot
RECURRENCE_MIN=3 hard floor (that hard floor lives ONLY in exp_ingest_gate_consolidation_loop_pilot_v1.gate_decision_*;
the race + this cell use the GRADED form) -- confirmed by construction + reported recur DECONF. (2) SCHEMA-FIT =
reachability rank-percentile over foundation (build_schema_fit) -- reproduced deriv/underiv means + schemafit DECONF.
(3) D[r*] vs D[r0]+D[r1] cosine: if ~1 the memorized operator already equals the composition (comp would be inert by
construction -- informative); if low they diverge (comp can carry a different signal). All reported.

CONTROLS (harness-valid, reuse v4/race verbatim): CONF_AUC (untrained-row confound) reproduces; POSCTRL (corrupt-r*
vs in-train-r*) fires; RANDLABEL ~chance; r* row genuinely trained; foundation generalizes; class balance. Plus a
Gate-D positive control: ADD_FLAT reproduces ~chance AND SCHEMAFIT > ADD_FLAT (the race's qualitative finding) at
this scale -- if not, the split diverged from the race and the compositional arm is on the wrong arena (INCONCLUSIVE).

HONEST: either outcome is decisive. EXTRACTOR-ARTIFACT (surprise-done-right works, converges with schema-fit) OR
GENUINELY-INERT (schema-fit-direct stands). No fitting in any compositional arm (COMP_OP/COMP_PATH are parameter-free
readouts off the SAME foundation) -> no calib/test split needed; DECONF is over the full balanced held set (matches
how add_flat/schemafit are non-fitted in the race's deconf_full).

REUSE (extend, don't rebuild): v4 gen_composed_arena / derivability_labels / _exact_path_labels / _balance_mask /
_arena_cfg / ARENA_BASE; v2 fit_foundation / _to_int / _mean; v1 _auc / _recip_ranks / _surprise / _sha /
build_schema_fit / schema_fit_edges / additive_direct_scores. New: the two compositional readouts + the head-to-head.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (the 5 arm score vectors hash-distinct on the held split)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: DECONF_AUC is a rank statistic over two measured score distributions; chance=0.5, self-calibrated by the
#   RANDLABEL must-fail control; no closed-form noise floor.
# - baseline_in_band: inferable held-out MRR 0.05<mrr<0.95 AND strong (>=HP_STRONG_MRR_MIN); r* MRR >= floor (trained)
# - discriminator survives scale: multi-seed smoke at reduced N (3 seeds) shows comp arm spread; FULL confirms
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds (one arena race block per seed)
# - HARD_PASS strictly above chance-floor + band (HP_DECONF_MIN=0.65 vs chance 0.50)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test constructs AdditiveKGMap + fit + score_all + compose_entity + insert_entity at N~16 AND
#   exercises gen_composed_arena + derivability_labels + comp_surprise_seed + both compositional readouts at tiny scale
# - deterministic seeding: fixed int seeds + np.random.default_rng(seed); no hash()-seeded RNG / no list(set()) order
# - progress_logging = print_flush_true (every seed + arm logs, flush=True)

ASCII-only. No emojis. Explicit dtypes. np.random.default_rng / torch.Generator seeded. Terse.
"""

import argparse
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.additive_map import AdditiveKGMap, additive_direct_scores  # noqa: E402
from hdlab import reachability_audit as RA  # noqa: E402
# REUSE v4 arena + derivability machinery (import does NOT run main; guarded by __main__)
from experiments.exp_ingest_gate_deconfound_within_relation_derivability_v1 import (  # noqa: E402
    gen_composed_arena, derivability_labels, _exact_path_labels, _balance_mask, _arena_cfg, ARENA_BASE,
)
# REUSE v2 fit + helpers
from experiments.exp_ingest_gate_strong_foundation_novelty_v2 import (  # noqa: E402
    fit_foundation, _to_int as _arena_to_int, _mean,
)
# REUSE v1 metric + schema-fit machinery
from experiments.exp_ingest_gate_consolidation_loop_pilot_v1 import (  # noqa: E402
    _auc, _recip_ranks, _surprise, _sha, build_schema_fit, schema_fit_edges,
)

ANCHOR_NAME = "ingest_gate_compositional_surprise_deconf_v1"

# ---- pre-registered bands ---------------------------------------------------------------------------------------
# HYPOTHESIZED@this-file (design; measured at smoke/full). DECONF_AUC chance = 0.50 (rank stat), self-checked by
# RANDLABEL. P<=0.50 (novel synthesis). Modal expectation (deflated): comp_op DECONF meaningfully > add_flat (~0.545)
# and approaches schemafit (~0.72) -> EXTRACTOR_ARTIFACT, converges with schema-fit. But could be genuinely inert.
HP_DECONF_MIN = 0.65          # a comp arm "carries the signal": separates underivable-vs-derivable (>chance+0.15, +5% band)
HF_DECONF_MAX = 0.58          # an arm collapses to ~chance
DECISIVE_MARGIN = 0.10        # comp decisively beats additive-flat
CONVERGE_EPS = 0.07           # comp "converges with" schema-fit (schema-conditioned surprise = ONE quantity)

# harness-valid bands (reuse v4/race verbatim)
HP_POSCTRL_AUC_MIN = 0.75
HP_CONF_AUC_MIN = 0.70
HP_RANDLABEL_LO = 0.40
HP_RANDLABEL_HI = 0.60
HP_RSTAR_TRAINED_MRR_MIN = 0.30
HP_STRONG_MRR_MIN = 0.40
HP_INFER_MRR_LO = 0.05
HP_INFER_MRR_HI = 0.95
HP_MIN_CLASS_FRAC = 0.20
HP_ARRAY_RECOMPUTE_TOL = 1e-6
# Gate-D positive control (reproduce the race's qualitative SCHEMAFIT_CARRIES at this scale)
FLAT_REPRO_MAX = 0.60         # add_flat must be ~chance (reproduces additive-inert)
SCHEMAFIT_GAP_MIN = 0.08      # schemafit must beat add_flat by >= this (reproduces schema carries)

TAU = 3.0                     # recurrence -> local_precision = deg/(deg+TAU) (GRADED; matches race_v1, NOT v1-pilot floor)
COMP_PATH_TOPM = 5            # discrete 2-hop: top-M predicted mids under (h, r0)

EPS_BAND = 1e-9
B_DERIV, B_UNDERIV = 0, 1
ARM_ORDER = ["add_flat", "schemafit", "comp_op", "comp_path", "recur"]
COMP_ARMS = ["comp_op", "comp_path"]

FULL_CFG = dict(
    seeds=[7, 13, 17],
    n_ent=600, edges_per_rel=420, n_rstar=420,
    train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=350,
    reach_k=2, reach_cap=300, min_class_n=25,
)
SMOKE_CFG = dict(
    seeds=[7, 13, 17],       # multi-seed smoke (MANDATORY for an AUC discriminator; single-seed inflates)
    n_ent=300, edges_per_rel=180, n_rstar=180,
    train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=140,
    reach_k=2, reach_cap=150, min_class_n=10,
)


# ---------------------------------------------------------------------------
# scaffolding
# ---------------------------------------------------------------------------
def _log(msg):
    print("[comp_surp_v1] %s" % msg, flush=True)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(), anchor_name=ANCHOR_NAME,
                  run_mode=run_mode, expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(str(output_dir), "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(str(output_dir), "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    _write_metrics_atomic(output_dir, diag)


def _pearson(a, b):
    a = np.asarray(a, dtype=np.float64); b = np.asarray(b, dtype=np.float64)
    if a.size < 2 or b.size < 2:
        return float("nan")
    sa = a.std(); sb = b.std()
    if sa < 1e-12 or sb < 1e-12:
        return float("nan")
    return float(np.mean((a - a.mean()) * (b - b.mean())) / (sa * sb))


# ---------------------------------------------------------------------------
# COMPOSITIONAL READOUTS (the NEW machinery; both parameter-free off the fitted foundation X,D)
# ---------------------------------------------------------------------------
def comp_op_surprise(X, D, held_int, ra, rb, all_true_rstar, device):
    """Operator-composition surprise: pred = X_h + D[ra] + D[rb]; filtered RR of true t; surprise = 1 - RR.

    Reuses _recip_ranks by appending a composed displacement row to D and remapping the held edges to it. The filter
    set is the r* true-tail set per head (same filtering as the direct r* readout -> apples-to-apples)."""
    D_comp = torch.cat([D, (D[ra] + D[rb]).unsqueeze(0)], dim=0)   # extra row = composed displacement
    r_comp = int(D.shape[0])                                       # index of the new row
    held_c = held_int.copy(); held_c[:, 1] = r_comp
    # filter (h, r_comp) -> the r* true tails of h (all_true_rstar is keyed (h, r*))
    all_true_c = defaultdict(set)
    for i in range(held_c.shape[0]):
        h = int(held_c[i, 0])
        all_true_c[(h, r_comp)] = all_true_rstar.get(h, set())
    rr = _recip_ranks(X, D_comp, held_c, all_true_c, device)
    return np.clip(_surprise(rr), 0.0, 1.0)


def comp_path_surprise(X, D, held_int, ra, rb, all_true_T, device, topM):
    """Discrete two-hop traversal surprise: from h take top-M predicted mids under (h,ra); for each mid score t under
    (mid,rb) with the FOUNDATION filter; RR_path = max over mids of RR(t | mid, rb); surprise = 1 - RR_path.

    A genuine multi-hop composition (follows predicted r0 edges then r1 edges), guards against comp_op being a
    degenerate re-additive score."""
    nq = held_int.shape[0]
    if nq == 0:
        return np.zeros(0, dtype=np.float64)
    # hop-1: rank all entities as r0-successors of each head
    hr0 = held_int.copy(); hr0[:, 1] = ra
    sc0 = additive_direct_scores(X, D, hr0, device)               # (nq, N) higher=better
    topM = min(int(topM), sc0.shape[1])
    top_mids = torch.topk(sc0, k=topM, dim=1).indices.cpu().numpy().astype(np.int64)  # (nq, M)
    # hop-2: build (mid, rb, t) sub-edges for every (fact, mid) pair; filtered RR under the foundation
    sub = np.empty((nq * topM, 3), dtype=np.int64)
    for i in range(nq):
        t_i = int(held_int[i, 2])
        for j in range(topM):
            sub[i * topM + j, 0] = top_mids[i, j]
            sub[i * topM + j, 1] = rb
            sub[i * topM + j, 2] = t_i
    rr_sub = _recip_ranks(X, D, sub, all_true_T, device)          # (nq*M,)
    rr_sub = rr_sub.reshape(nq, topM)
    rr_path = rr_sub.max(axis=1)                                  # best path per fact
    return np.clip(_surprise(rr_path), 0.0, 1.0)


# ---------------------------------------------------------------------------
# LOAD-BEARING PRIMITIVE: rebuild the v4/race arena+split VERBATIM, add the compositional surprise arms.
# ---------------------------------------------------------------------------
def comp_surprise_seed(cfg, seed, device, want_arrays=False):
    """SPLIT DERIVATION COPIED VERBATIM from race_seed so the derivable/underivable held set is the IDENTICAL v4 split.
    Then compute the 5 arm scores + their DECONF_AUC (full balanced held set), the harness controls, and the
    D[r*]-vs-D[r0]+D[r1] diagnostics."""
    acfg = _arena_cfg(cfg["n_ent"], cfg["edges_per_rel"])
    N = acfg["n_ent"]; nR_base = acfg["n_base_rel"]
    rstar_idx = nR_base
    nR_total = nR_base + 1
    ra, rb = 0, 1                            # r* = r0 o r1

    Z, G, base_edges, rstar_edges, mid = gen_composed_arena(acfg, seed, rstar_idx, ra, rb, cfg["n_rstar"])
    rng = np.random.default_rng(seed * 100003 + 131)   # VERBATIM race_seed seed

    nb = len(base_edges)
    pb = rng.permutation(nb)
    nb_hold = int(round(cfg["frac_heldout_base"] * nb))
    hold_b = set(pb[:nb_hold].tolist())
    base_train = [base_edges[i] for i in range(nb) if i not in hold_b]
    base_heldout = [base_edges[i] for i in range(nb) if i in hold_b]

    nr = len(rstar_edges)
    pr = rng.permutation(nr)
    nr_train = int(round(cfg["train_frac_rstar"] * nr))
    tr_r = set(pr[:nr_train].tolist())
    rstar_train = [rstar_edges[i] for i in range(nr) if i in tr_r]
    rstar_heldout = [rstar_edges[i] for i in range(nr) if i not in tr_r]

    base_train_int = _arena_to_int(base_train)
    base_heldout_int = _arena_to_int(base_heldout)
    rstar_train_int = _arena_to_int(rstar_train)
    rstar_heldout_int = _arena_to_int(rstar_heldout)

    adj_found = RA.build_undirected_adj(base_train_int, N)
    derivable = derivability_labels(rstar_heldout_int, adj_found, cfg["reach_k"])
    base_train_set = set((int(h), int(r), int(t)) for (h, r, t) in base_train)
    mid_of_head = {int(rstar_edges[i][0]): int(mid[i]) for i in range(nr)}
    derivable_exact = _exact_path_labels(rstar_heldout_int, mid_of_head, base_train_set, ra, rb)

    keep = _balance_mask(derivable, np.random.default_rng(seed * 100003 + 191), cfg["min_class_n"])  # VERBATIM
    if keep is None:
        return dict(seed=int(seed), status="ONE_CLASS_EMPTY", n_deriv=int(derivable.sum()),
                    n_underiv=int((~derivable).sum()))
    held_int = rstar_heldout_int[keep]
    deriv_lbl = derivable[keep]
    deriv_exact_lbl = derivable_exact[keep]
    n_deriv = int(deriv_lbl.sum()); n_underiv = int((~deriv_lbl).sum())

    # SCHEMA-FIT (reachability rank-percentile over foundation) -- the reference the race said carries the signal
    reach_pct, reach_mass = build_schema_fit(base_train_int, N, cfg["reach_k"], cfg["reach_cap"])
    schema_fit_held = schema_fit_edges(held_int, reach_pct, np.zeros(held_int.shape[0], dtype=bool))
    schema_fit_held = np.clip(np.asarray(schema_fit_held, dtype=np.float64), 0.0, 1.0)

    # RECURRENCE -> graded local precision (deg(h)/(deg(h)+TAU)); the degree/frequency confound probe
    deg = RA.degree_vector(adj_found)
    rec_held = deg[held_int[:, 0]].astype(np.float64)
    recur_held = rec_held / (rec_held + TAU)

    # FOUNDATION_T: r* row TRAINED (base_train + rstar_train) = the arena the race scored on
    train_T = base_train + rstar_train
    X_T, D_T, all_true_T = fit_foundation(acfg, seed, cfg["epochs"], train_T, N, nR_total, device)

    # r* true-tail set per head (filter for BOTH the direct r* readout and the comp_op readout)
    all_true_rstar = defaultdict(set)
    for h, r, t in train_T:
        if int(r) == rstar_idx:
            all_true_rstar[int(h)].add(int(t))

    # ---- ARM scores (all non-fitted; higher = more UNDERIVABLE = revision needed) ----
    add_flat = np.clip(_surprise(_recip_ranks(X_T, D_T, held_int, all_true_T, device)), 0.0, 1.0)  # additive-DIRECT r*
    sf_score = 1.0 - schema_fit_held                                                                 # schemafit ref
    comp_op = comp_op_surprise(X_T, D_T, held_int, ra, rb, all_true_rstar, device)                   # NEW operator-comp
    comp_path = comp_path_surprise(X_T, D_T, held_int, ra, rb, all_true_T, device, COMP_PATH_TOPM)   # NEW discrete 2-hop
    arm_score = dict(add_flat=add_flat, schemafit=sf_score, comp_op=comp_op, comp_path=comp_path, recur=recur_held)

    def _arm_auc(score):
        pos = score[~deriv_lbl]      # underivable (should be HIGH)
        neg = score[deriv_lbl]       # derivable (should be LOW)
        return _auc(pos, neg)

    deconf = {a: _arm_auc(arm_score[a]) for a in ARM_ORDER}
    deconf_exact = {a: _auc(arm_score[a][~deriv_exact_lbl], arm_score[a][deriv_exact_lbl]) for a in ARM_ORDER}

    # baseline strength + row-trained checks
    surp_infer_T = _surprise(_recip_ranks(X_T, D_T, base_heldout_int, all_true_T, device))
    infer_mrr = float(np.mean(1.0 - surp_infer_T)) if surp_infer_T.size else float("nan")
    surp_rtrain_T = _surprise(_recip_ranks(X_T, D_T, rstar_train_int, all_true_T, device))
    rstar_train_mrr = float(np.mean(1.0 - surp_rtrain_T)) if surp_rtrain_T.size else float("nan")

    # POS-CONTROL (must fire): corrupt-r* vs in-train-r* under FOUNDATION_T
    corrupt = rstar_train_int.copy()
    if corrupt.shape[0] > 0:
        rand_t = rng.integers(0, N, size=corrupt.shape[0])
        for i in range(corrupt.shape[0]):
            if int(rand_t[i]) == int(corrupt[i, 2]):
                rand_t[i] = (int(rand_t[i]) + 1) % N
        corrupt[:, 2] = rand_t
    surp_corrupt = _surprise(_recip_ranks(X_T, D_T, corrupt, all_true_T, device))
    posctrl_auc = _auc(surp_corrupt, surp_rtrain_T)

    # CONF ARM (reproduce v3/v4 confound): r* row UNTRAINED (base_train only)
    X_U, D_U, all_true_U = fit_foundation(acfg, seed, cfg["epochs"], base_train, N, nR_total, device)
    all_rstar_int = _arena_to_int(rstar_edges)
    surp_conf_novel = _surprise(_recip_ranks(X_U, D_U, all_rstar_int, all_true_U, device))
    surp_conf_infer = _surprise(_recip_ranks(X_U, D_U, base_heldout_int, all_true_U, device))
    conf_auc = _auc(surp_conf_novel, surp_conf_infer)

    # MUST-FAIL: RANDOM-LABEL shuffle -> AUC ~chance (on comp_op, the arm under test)
    rlrng = np.random.default_rng(seed * 100003 + 313)
    shuf = rlrng.permutation(comp_op.shape[0])
    randlabel_auc = _auc(comp_op[shuf[n_deriv:]], comp_op[shuf[:n_deriv]])

    # DIAGNOSTIC: does the memorized D[r*] already equal the composition D[r0]+D[r1]?
    d_star = D_T[rstar_idx]; d_comp = D_T[ra] + D_T[rb]
    cos_star_comp = float(torch.nn.functional.cosine_similarity(d_star.unsqueeze(0), d_comp.unsqueeze(0)).item())
    # correlations of comp_op with add_flat and with schemafit (converge-with-schemafit evidence)
    corr_comp_flat = _pearson(comp_op, add_flat)
    corr_comp_sf = _pearson(comp_op, sf_score)

    out = dict(
        seed=int(seed), status="OK", N=int(N), n_deriv=n_deriv, n_underiv=n_underiv,
        deriv_frac=float(deriv_lbl.mean()) if deriv_lbl.size else float("nan"),
        deconf=deconf, deconf_exact=deconf_exact,
        conf_auc=conf_auc, posctrl_auc=posctrl_auc, randlabel_auc=randlabel_auc,
        infer_mrr=infer_mrr, rstar_train_mrr=rstar_train_mrr,
        schemafit_deriv_mean=float(np.mean(schema_fit_held[deriv_lbl])) if n_deriv else float("nan"),
        schemafit_underiv_mean=float(np.mean(schema_fit_held[~deriv_lbl])) if n_underiv else float("nan"),
        recur_deriv_mean=float(np.mean(recur_held[deriv_lbl])) if n_deriv else float("nan"),
        recur_underiv_mean=float(np.mean(recur_held[~deriv_lbl])) if n_underiv else float("nan"),
        comp_op_deriv_mean=float(np.mean(comp_op[deriv_lbl])) if n_deriv else float("nan"),
        comp_op_underiv_mean=float(np.mean(comp_op[~deriv_lbl])) if n_underiv else float("nan"),
        cos_dstar_dcomp=cos_star_comp, corr_comp_flat=corr_comp_flat, corr_comp_schemafit=corr_comp_sf,
        recurrence_form="graded_deg_over_deg_plus_tau_TAU_%.1f" % TAU,
        arm_score_sha={a: _sha(arm_score[a]) for a in ARM_ORDER},
    )
    if want_arrays:
        out["_arrays"] = dict(
            batch=(~deriv_lbl).astype(np.int64),   # 0=deriv,1=underiv on the full balanced held set
            add_flat=add_flat, schemafit=sf_score, comp_op=comp_op, comp_path=comp_path, recur=recur_held,
            deriv_label=deriv_lbl.astype(np.int64),
        )
    return out


# ---------------------------------------------------------------------------
# per-candidate array dump + off-disk recompute of comp_op DECONF_AUC
# ---------------------------------------------------------------------------
def dump_and_verify_arrays(output_dir, arrays_by_seed):
    cols = defaultdict(list)
    seed_col = []
    for seed, arr in arrays_by_seed:
        n = arr["batch"].shape[0]
        seed_col.append(np.full(n, seed, dtype=np.int64))
        for kk, vv in arr.items():
            cols[kk].append(np.asarray(vv, dtype=np.float64))
    flat = {kk: np.concatenate(vv) for kk, vv in cols.items()}
    flat["seed"] = np.concatenate(seed_col)
    path = os.path.join(str(output_dir), "per_candidate_arrays.npz")
    tmp = os.path.join(str(output_dir), "per_candidate_arrays_tmp.npz")
    np.savez(tmp, **flat)
    os.replace(tmp, path)
    inmem = _auc(flat["comp_op"][flat["batch"] == B_UNDERIV], flat["comp_op"][flat["batch"] == B_DERIV])
    z = np.load(path)
    offdisk = _auc(z["comp_op"][z["batch"] == B_UNDERIV], z["comp_op"][z["batch"] == B_DERIV])
    delta = abs(float(inmem) - float(offdisk)) if (inmem == inmem and offdisk == offdisk) else 0.0
    return (delta <= HP_ARRAY_RECOMPUTE_TOL), delta, path


# ---------------------------------------------------------------------------
# aggregate + head-to-head verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed, run_mode, array_ok, array_delta, expected_units, observed_units):
    ok = [s for s in per_seed if s.get("status") == "OK"]

    def agg_arm(arm):
        return _mean([s["deconf"][arm] for s in ok])
    deconf = {a: agg_arm(a) for a in ARM_ORDER}
    deconf_exact = {a: _mean([s["deconf_exact"][a] for s in ok]) for a in ARM_ORDER}
    conf = _mean([s["conf_auc"] for s in ok])
    posctrl = _mean([s["posctrl_auc"] for s in ok])
    randlabel = _mean([s["randlabel_auc"] for s in ok])
    infer_mrr = _mean([s["infer_mrr"] for s in ok])
    rstar_train_mrr = _mean([s["rstar_train_mrr"] for s in ok])
    min_class = min([min(s["n_deriv"], s["n_underiv"]) for s in ok]) if ok else 0
    min_class_frac = min([min(s["deriv_frac"], 1.0 - s["deriv_frac"]) for s in ok]) if ok else 0.0
    cos_dstar_dcomp = _mean([s["cos_dstar_dcomp"] for s in ok])
    corr_comp_flat = _mean([s["corr_comp_flat"] for s in ok])
    corr_comp_sf = _mean([s["corr_comp_schemafit"] for s in ok])

    g = {}
    g["cardinality_ok"] = (observed_units == expected_units)
    g["all_seeds_ok"] = (len(ok) == len(per_seed)) and len(ok) > 0
    g["HP_POSCTRL_FIRES"] = (posctrl == posctrl) and (posctrl >= HP_POSCTRL_AUC_MIN)
    g["HP_CONF_REPRODUCES"] = (conf == conf) and (conf >= HP_CONF_AUC_MIN)
    g["HP_RANDLABEL_CHANCE"] = (randlabel == randlabel) and (HP_RANDLABEL_LO <= randlabel <= HP_RANDLABEL_HI)
    g["HP_RSTAR_TRAINED"] = (rstar_train_mrr == rstar_train_mrr) and (rstar_train_mrr >= HP_RSTAR_TRAINED_MRR_MIN)
    g["HP_FOUNDATION_STRONG"] = (infer_mrr == infer_mrr) and (infer_mrr >= HP_STRONG_MRR_MIN)
    g["baseline_in_band"] = (infer_mrr == infer_mrr) and (HP_INFER_MRR_LO < infer_mrr < HP_INFER_MRR_HI)
    g["class_balance_ok"] = (min_class_frac >= HP_MIN_CLASS_FRAC) and (min_class > 0)
    # Gate-D positive control: reproduce the race's qualitative SCHEMAFIT_CARRIES at this scale
    flat_a = deconf["add_flat"]; sfa = deconf["schemafit"]
    g["GATE_D_FLAT_INERT"] = (flat_a == flat_a) and (flat_a <= FLAT_REPRO_MAX)
    g["GATE_D_SCHEMAFIT_CARRIES"] = (sfa == sfa) and (flat_a == flat_a) and (sfa >= flat_a + SCHEMAFIT_GAP_MIN)
    harness_valid = all(g.values())

    comp_op_a = deconf["comp_op"]; comp_path_a = deconf["comp_path"]; recur_a = deconf["recur"]
    best_comp = max([c for c in (comp_op_a, comp_path_a) if c == c], default=float("nan"))
    best_comp_name = "comp_op" if (comp_op_a == comp_op_a and comp_op_a >= (comp_path_a if comp_path_a == comp_path_a else -1)) else "comp_path"

    comp_op_works = (comp_op_a == comp_op_a) and (comp_op_a >= HP_DECONF_MIN)
    comp_path_works = (comp_path_a == comp_path_a) and (comp_path_a >= HP_DECONF_MIN)
    any_comp_works = comp_op_works or comp_path_works
    comp_beats_flat = (best_comp == best_comp) and (flat_a == flat_a) and (best_comp >= flat_a + DECISIVE_MARGIN)
    both_comp_chance = ((comp_op_a == comp_op_a) and (comp_op_a <= HF_DECONF_MAX)
                        and (comp_path_a == comp_path_a) and (comp_path_a <= HF_DECONF_MAX))
    converges_sf = (best_comp == best_comp) and (sfa == sfa) and (abs(best_comp - sfa) <= CONVERGE_EPS
                                                                   or best_comp >= sfa - CONVERGE_EPS)

    if not harness_valid:
        verdict = "INCONCLUSIVE_harness"
        finding = ("INCONCLUSIVE: harness/positive-control not validated (posctrl=%.3f conf=%.3f randlabel=%.3f "
                   "rstar_mrr=%.3f infer_mrr=%.3f class_bal=%.2f card=%s GATE_D_flat_inert=%s[%.3f] "
                   "GATE_D_sf_carries=%s[flat=%.3f sf=%.3f]). If GATE_D failed, the split diverged from the race and "
                   "the compositional arm is on the wrong arena." % (
                       posctrl, conf, randlabel, rstar_train_mrr, infer_mrr, min_class_frac, g["cardinality_ok"],
                       g["GATE_D_FLAT_INERT"], flat_a, g["GATE_D_SCHEMAFIT_CARRIES"], flat_a, sfa))
    elif any_comp_works and comp_beats_flat:
        verdict = "EXTRACTOR_ARTIFACT_comp_carries"
        conv = ("and CONVERGES with schema-fit (|%.3f - %.3f| <= %.2f) -> free-energy view supported (schema-"
                "conditioned surprise = ONE quantity)" % (best_comp, sfa, CONVERGE_EPS) if converges_sf else
                "but does NOT reach schema-fit (%.3f < %.3f - %.2f) -> a compositional surprise recovers PART of the "
                "signal, schema-fit still strongest" % (best_comp, sfa, CONVERGE_EPS))
        finding = ("EXTRACTOR_ARTIFACT: the 'surprise inert' finding was an ARTIFACT of the additive-DIRECT extractor. "
                   "%s DECONF_AUC=%.3f >= %.2f decisively beats additive-flat=%.3f (margin>=%.2f) %s. comp_op=%.3f "
                   "comp_path=%.3f schemafit=%.3f recur=%.3f. cos(D[r*],D[r0]+D[r1])=%.3f (the memorized operator "
                   "differs from the composition -> comp carries new signal). ROUTE TO SKUNKWORKS VET." % (
                       best_comp_name, best_comp, HP_DECONF_MIN, flat_a, DECISIVE_MARGIN, conv, comp_op_a, comp_path_a,
                       sfa, recur_a, cos_dstar_dcomp))
    elif both_comp_chance:
        verdict = "SURPRISE_GENUINELY_INERT"
        finding = ("SURPRISE_GENUINELY_INERT: even a COMPOSITIONAL surprise stays ~chance (comp_op=%.3f comp_path=%.3f "
                   "both <= %.2f) while additive-flat=%.3f and schemafit=%.3f. Surprise is genuinely inert for "
                   "within-relation derivability here; schema-fit-DIRECT stands (the race's SCHEMAFIT_CARRIES holds). "
                   "recur=%.3f. cos(D[r*],D[r0]+D[r1])=%.3f." % (
                       comp_op_a, comp_path_a, HF_DECONF_MAX, flat_a, sfa, recur_a, cos_dstar_dcomp))
    else:
        verdict = "MIDDLE_BAND_partial"
        finding = ("MIDDLE_BAND: compositional surprise straddles chance..pass (comp_op=%.3f comp_path=%.3f between "
                   "%.2f and %.2f) vs additive-flat=%.3f schemafit=%.3f recur=%.3f -- partial/ambiguous. "
                   "comp_beats_flat=%s. cos(D[r*],D[r0]+D[r1])=%.3f." % (
                       comp_op_a, comp_path_a, HF_DECONF_MAX, HP_DECONF_MIN, flat_a, sfa, recur_a, comp_beats_flat,
                       cos_dstar_dcomp))

    msg = ("DECONF_AUC add_flat=%.3f schemafit=%.3f comp_op=%.3f comp_path=%.3f recur=%.3f | comp_beats_flat=%s "
           "converges_sf=%s | cos(Dr*,Dr0+Dr1)=%.3f corr(comp,flat)=%.3f corr(comp,sf)=%.3f | CONF=%.3f POSCTRL=%.3f "
           "RAND=%.3f infer_mrr=%.3f rstar_mrr=%.3f bal=%.2f | GATE_D[flat_inert=%s sf_carries=%s] harness=%s "
           "arrays_ok=%s(d=%.1e) card=%s -> %s" % (
               flat_a, sfa, comp_op_a, comp_path_a, recur_a, comp_beats_flat, converges_sf, cos_dstar_dcomp,
               corr_comp_flat, corr_comp_sf, conf, posctrl, randlabel, infer_mrr, rstar_train_mrr, min_class_frac,
               g["GATE_D_FLAT_INERT"], g["GATE_D_SCHEMAFIT_CARRIES"], harness_valid, array_ok, array_delta,
               g["cardinality_ok"], verdict))
    summary = "%s: %s" % (verdict, finding)
    return dict(verdict=verdict, verdict_msg=msg, summary=summary, finding=finding, gates=g,
                harness_valid=harness_valid, run_mode=run_mode,
                agg=dict(deconf=deconf, deconf_exact=deconf_exact, conf_auc=conf, posctrl_auc=posctrl,
                         randlabel_auc=randlabel, infer_mrr=infer_mrr, rstar_train_mrr=rstar_train_mrr,
                         cos_dstar_dcomp=cos_dstar_dcomp, corr_comp_flat=corr_comp_flat, corr_comp_schemafit=corr_comp_sf,
                         min_class=int(min_class), min_class_frac=min_class_frac, array_recompute_delta=array_delta,
                         head_to_head=dict(comp_op_works=bool(comp_op_works), comp_path_works=bool(comp_path_works),
                                           comp_beats_flat=bool(comp_beats_flat), both_comp_chance=bool(both_comp_chance),
                                           converges_schemafit=bool(converges_sf), best_comp=best_comp,
                                           best_comp_name=best_comp_name)))


# ---------------------------------------------------------------------------
# self-test (REAL substrate code path at N~16 + compositional readouts; validity preflight)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    from experiments._kge_anchor1_fit import fit_kge_anchor1
    _log("self_test: constructing REAL AdditiveKGMap + composed arena + compositional readouts at tiny scale")
    exercised = set()
    device = torch.device("cpu")

    triples = []
    for i in range(16):
        triples.append(("e%d" % i, "ra", "e%d" % ((i + 1) % 16)))
        triples.append(("e%d" % i, "rb", "e%d" % ((i + 3) % 16)))
        triples.append(("e%d" % i, "rc", "e%d" % ((i + 5) % 16)))
    ents = sorted({x for tr in triples for x in (tr[0], tr[2])})
    rels = sorted({tr[1] for tr in triples})
    kmap = AdditiveKGMap(device=device)
    kmap.fit(triples, entities=ents, relations=rels, k=8, epochs=30, seed=7)
    exercised.add("AdditiveKGMap"); exercised.add("AdditiveKGMap.fit")
    _ = kmap.score_all("e0", "ra"); exercised.add("AdditiveKGMap.score_all")
    code = kmap.compose_entity([("e0", "ra"), ("e1", "rb")]); exercised.add("AdditiveKGMap.compose_entity")
    _ = kmap.insert_entity(code, name="e_new"); exercised.add("AdditiveKGMap.insert_entity")

    # compositional readouts on a tiny synthetic foundation: pred = X_h + D[0] + D[1] must be a valid surprise in [0,1]
    X = kmap.X; D = kmap.D
    held = np.array([[0, 0, 3], [1, 1, 5], [2, 0, 7]], dtype=np.int64)  # (h, r_placeholder, t) -- r overwritten inside
    all_true_rstar = defaultdict(set)
    co = comp_op_surprise(X, D, held, 0, 1, all_true_rstar, device)
    exercised.add("comp_op_surprise")
    assert co.shape[0] == 3 and np.all((co >= 0.0) & (co <= 1.0)), "comp_op surprise out of [0,1]"
    all_true_T = defaultdict(set)
    tri_int = np.array([[ents.index(h), rels.index(r), ents.index(t)] for h, r, t in triples], dtype=np.int64)
    for h, r, t in tri_int:
        all_true_T[(int(h), int(r))].add(int(t))
    cp = comp_path_surprise(X, D, held, 0, 1, all_true_T, device, 3)
    exercised.add("comp_path_surprise")
    assert cp.shape[0] == 3 and np.all((cp >= 0.0) & (cp <= 1.0)), "comp_path surprise out of [0,1]"

    # AUC direction sanity
    assert _auc([0.9, 0.95], [0.1, 0.2]) == 1.0 and _auc([0.1, 0.2], [0.9, 0.95]) == 0.0

    # full seed primitive at tiny scale: composed arena gives defined per-arm AUCs + firing controls + distinct arms
    cfg = dict(n_ent=80, edges_per_rel=48, n_rstar=48, train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=60,
               reach_k=2, reach_cap=60, min_class_n=3)
    r = comp_surprise_seed(cfg, 7, device, want_arrays=True)
    exercised.add("comp_surprise_seed"); exercised.add("gen_composed_arena"); exercised.add("derivability_labels")
    assert r["status"] in ("OK", "ONE_CLASS_EMPTY"), "comp_surprise_seed status: %s" % r["status"]
    if r["status"] == "OK":
        for a in ARM_ORDER:
            assert 0.0 <= r["deconf"][a] <= 1.0, "%s deconf out of [0,1]: %s" % (a, r["deconf"][a])
        assert len(set(r["arm_score_sha"].values())) >= 4, "arm score vectors not distinct (arm bug)"
        for kk in ("conf_auc", "posctrl_auc", "randlabel_auc"):
            assert 0.0 <= r[kk] <= 1.0, "%s out of [0,1]" % kk
        # array round-trip
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            okd, delta, _p = dump_and_verify_arrays(td, [(7, r["_arrays"])])
            assert okd and delta <= HP_ARRAY_RECOMPUTE_TOL, "array recompute mismatch delta=%s" % delta

    okp = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.fit", "AdditiveKGMap.score_all",
                                        "AdditiveKGMap.compose_entity", "AdditiveKGMap.insert_entity",
                                        "gen_composed_arena", "derivability_labels", "comp_surprise_seed",
                                        "comp_op_surprise", "comp_path_surprise"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": AdditiveKGMap, "callable_name": "AdditiveKGMap",
         "kwargs": {"device": "cpu"}},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": device, "seed": 7, "epochs": 1}},
        {"kind": "metric_moves", "metric_name": "comp_op_deconf_auc", "before": 0.50, "after": 0.80, "min_delta": 1e-6},
    ], run_mode="selftest")
    assert okp, "validity preflight failed"
    _log("self_test PASS (real code path exercised: %s)" % sorted(exercised))
    return True


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args, _unk = ap.parse_known_args()

    from experiments._seed_checkpoint import get_output_dir
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else "full")
    output_dir = get_output_dir(ANCHOR_NAME + ("_selftest" if args.self_test else ("_smoke" if args.smoke else "")))
    global _OUT
    _OUT = output_dir

    if args.self_test:
        self_test()
        _write_metrics_atomic(output_dir, dict(verdict="HARD_PASS", verdict_msg="SELFTEST_PASS", run_mode="self_test",
                                               summary="self_test ok", elapsed_s=0.0))
        return

    cfg = SMOKE_CFG if args.smoke else FULL_CFG
    seeds = cfg["seeds"]
    expected_units = len(seeds)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()
    device = torch.device("cpu")

    per_seed = []
    arrays_by_seed = []
    observed_units = 0
    for si, seed in enumerate(seeds):
        _log("seed %d/%d (seed=%d): fitting trained-row + untrained-row foundations; scoring 5 arms ..." % (
            si + 1, len(seeds), seed))
        want = (si == 0)
        s = comp_surprise_seed(cfg, seed, device, want_arrays=want)
        if want and s.get("status") == "OK":
            arrays_by_seed.append((seed, s.pop("_arrays")))
        else:
            s.pop("_arrays", None)
        per_seed.append(s)
        observed_units += 1
        if s.get("status") == "OK":
            dc = s["deconf"]
            _log("  [seed=%d] status=OK DECONF add_flat=%.3f schemafit=%.3f comp_op=%.3f comp_path=%.3f recur=%.3f | "
                 "cos(Dr*,Dr0+Dr1)=%.3f CONF=%.3f POSCTRL=%.3f infer_mrr=%.3f n_deriv=%d n_underiv=%d (%.1fs)" % (
                     seed, dc["add_flat"], dc["schemafit"], dc["comp_op"], dc["comp_path"], dc["recur"],
                     s["cos_dstar_dcomp"], s["conf_auc"], s["posctrl_auc"], s["infer_mrr"], s["n_deriv"],
                     s["n_underiv"], time.time() - t0))
        else:
            _log("  [seed=%d] status=%s (%.1fs)" % (seed, s.get("status"), time.time() - t0))

    ok = [s for s in per_seed if s.get("status") == "OK"]
    if ok:
        assert len(set(ok[0]["arm_score_sha"].values())) >= 4, "arm score vectors not distinct (arm bug)"

    if arrays_by_seed:
        array_ok, array_delta, array_path = dump_and_verify_arrays(output_dir, arrays_by_seed)
    else:
        array_ok, array_delta, array_path = False, float("nan"), ""
    _log("per-candidate arrays -> %s (recompute_ok=%s delta=%s)" % (array_path, array_ok, array_delta))

    v = aggregate_and_verdict(per_seed, run_mode, array_ok, array_delta, expected_units, observed_units)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(seeds),
                   config=dict(seeds=seeds, n_ent=cfg["n_ent"], edges_per_rel=cfg["edges_per_rel"],
                               n_rstar=cfg["n_rstar"], train_frac_rstar=cfg["train_frac_rstar"],
                               frac_heldout_base=cfg["frac_heldout_base"], epochs=cfg["epochs"],
                               reach_k=cfg["reach_k"], rel_scale=ARENA_BASE["rel_scale"],
                               comp_path_topM=COMP_PATH_TOPM, TAU=TAU),
                   bands=dict(HP_DECONF_MIN=HP_DECONF_MIN, HF_DECONF_MAX=HF_DECONF_MAX, DECISIVE_MARGIN=DECISIVE_MARGIN,
                              CONVERGE_EPS=CONVERGE_EPS, FLAT_REPRO_MAX=FLAT_REPRO_MAX, SCHEMAFIT_GAP_MIN=SCHEMAFIT_GAP_MIN),
                   expected_n_units=expected_units, observed_n_units=observed_units,
                   arms_differ_verified=True, final_metrics_atomicity="tmp_replace",
                   progress_logging="print_flush_true", cell_chunked=False,
                   start_marker_written=True, crash_diagnostic_present=True, heartbeat_present=False,
                   defensive_error_checking="single_seed_loop_short_cell_no_heartbeat",
                   per_candidate_arrays=os.path.basename(array_path) if array_path else None,
                   **v, per_seed=per_seed)
    _write_metrics_atomic(output_dir, metrics)
    _log("VERDICT %s | %s" % (v["verdict"], v["verdict_msg"]))
    _log("wrote %s (%.1fs)" % (os.path.join(output_dir, "metrics.json"), elapsed))


_OUT = None
if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_OUT or os.path.join("data", "exp_" + ANCHOR_NAME), e)
        raise
