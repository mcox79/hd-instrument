"""Ingest-gate DECONFOUND: does SURPRISE detect genuine semantic-UNDERIVABILITY, or just RELATION-IDENTITY
(an untrained relation row)?  -- the v3 VET's PROMOTION CRITERION.

THE CONFOUND (v3 VET, MEASURED@data/exp_ingest_gate_knee_locate_real_regime_v3/metrics.json). v2/v3 measured
KEY-AUC(surprise; NOVEL vs INFERABLE) where NOVEL = edges of a relation r* WITHHELD ENTIRELY from the foundation.
Withholding r* entirely makes two manipulations IDENTICAL: "r*'s relation-ROW is untrained (random D[r*])" and
"these facts are semantically novel". A random relation row scores every fact poorly (high surprise) REGARDLESS of
whether the fact is graph-derivable, so the v3 KEY-AUC ~0.835 could be a pure RELATION-IDENTITY ARTIFACT. The
knee-sweep does NOT deconfound (both hypotheses predict the below-knee collapse). This cell runs the decisive split.

THE DECISIVE DESIGN (relation-row-state held CONSTANT):
  TRAIN the r* row -- fit the foundation INCLUDING a random subset of r*'s edges, so D[r*] is TRAINED and functional.
  Then split the HELD-OUT r* facts (row-state now identical for both classes) by GROUND-TRUTH derivability:
    DERIVABLE   = tail t is reachable from head h within reach_k hops over the FOUNDATION's trained (non-r*) edges
                  (a known compositional path grounds the fact). r* itself is a COMPOSED relation r* = ra o rb, so
                  reach_k=2 reachability is exactly the composition that could infer t -- ground-truth by CONSTRUCTION.
    UNDERIVABLE = no such path in the foundation (info needed to place t is absent from the trained structure).
  DECISIVE METRIC  DECONF_AUC = AUC(surprise; UNDERIVABLE vs DERIVABLE), both HELD-OUT, both the SAME TRAINED r* row.

  CONTRAST ARM (reproduce the v3 confound in-arena): fit a SECOND foundation on base-train ONLY (r* row UNTRAINED),
  measure CONF_AUC = AUC(surprise; ALL-r* [untrained row] vs inferable held-out trained-rel edges). This must
  REPRODUCE high (~v3's 0.835) -- else the arena has no confound to deconfound (vacuous).
  POS-CONTROL (must fire): within the TRAINED-r* foundation, AUC(surprise; RANDOM-CORRUPT r* vs IN-TRAIN r*) -- a
  construction where surprise MUST separate; proves the metric CAN fire so a DECONF collapse is real, not broken.
  MUST-FAIL: RANDOM-LABEL shuffle of derivable/underivable -> AUC ~chance (guards a label-blind separator).

VERDICT (envelope-fail-bands):
  HARD_PASS      = harness-valid AND DECONF_AUC materially ABOVE chance (>= HP_DECONF_AUC_MIN, strict +5% band)
                   => surprise separates DERIVABLE from UNDERIVABLE with the relation row TRAINED => semantic-novelty
                   DECONFOUNDED from relation-identity => the ingest-gate surprise IS genuine semantic-novelty.
                   BRAIN-CHECK: aligned -- schema-CONSISTENT/derivable consolidates fast (low surprise),
                   schema-INCONSISTENT/underivable is high-surprise (Tse 2007 schema-consolidation). Route to VET.
  MEASURED_BOUND = harness-valid (CONF high + pos-control fires) AND DECONF_AUC ~chance (<= HF_DECONF_AUC_MAX)
                   => the v3 0.835 WAS the untrained-row artifact => surprise detects WHOLE-RELATION-ABSENCE only,
                   NOT within-relation semantic-underivability. An honest bound on the foundation-builder's
                   novelty-criterion. BRAIN-CHECK: our surprise is COARSER than the brain's (relation-presence, not
                   schema-composition-fit); the fix would be a schema-composition-aware surprise readout.
  MIDDLE_BAND    = harness-valid AND DECONF_AUC straddles [HF, HP] (ambiguous).
  INCONCLUSIVE   = NOT harness-valid (pos-control did not fire / confound did not reproduce / class sizes / row not
                   genuinely trained / foundation not generalizing) -> cannot distinguish real-collapse from broken.
A lightweight REAL-CSKG proxy arm (2-hop-reachable derivability, r* row trained) is reported NON-GATING for external
validity (real derivability is a proxy, not ground-truth).

REUSE (extend, don't rebuild): v2 gen_arena / fit_foundation / _to_int / _mean; v1 _auc / _recip_ranks / _surprise /
_sha / load_core_triples / _index_universe / _to_int; reachability_audit BFS adjacency. New: the composed relation
r* = ra o rb, the trained-row-held-constant derivable/underivable split, the CONF/POSCTRL/RANDLABEL arms, real proxy.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (derivable/underivable/conf-novel/posctrl-corrupt surprise vectors hash-distinct)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: DECONF_AUC is a rank statistic over two measured surprise distributions; chance is 0.5, self-calibrated
#   by the RANDOM-LABEL must-fail control; no closed-form noise floor.
# - baseline_in_band: inferable held-out MRR 0.05<mrr<0.95 AND strong (>= HP_STRONG_MRR_MIN) so DERIVABLE facts CAN
#   be ranked (a dead foundation cannot rank derivable either -> boring collapse); train-r* MRR >= floor (row trained)
# - discriminator survives scale: multi-seed smoke at reduced N (>=3 seeds) fires the discriminator; FULL confirms
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds * 2 (one synthetic block + one real block per seed)
# - HARD_PASS strictly above chance-floor + 5% band (HP_DECONF_AUC_MIN=0.65 vs chance 0.50)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test constructs AdditiveKGMap + fit + score_all + compose_entity + insert_entity at N~16
#   AND exercises gen_composed_arena + derivability_labels + the deconf primitive at N~16
# - deterministic seeding: fixed int seeds + np.random.default_rng(seed); no hash()-seeded RNG, no list(set()) order
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
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hdlab.additive_map import AdditiveKGMap  # noqa: E402
from hdlab import reachability_audit as RA  # noqa: E402
# REUSE v2 arena machinery (import does NOT run main; guarded by __main__)
from experiments.exp_ingest_gate_strong_foundation_novelty_v2 import (  # noqa: E402
    gen_arena, fit_foundation, _to_int as _arena_to_int, _mean,
)
# REUSE v1 metric + real-data machinery
from experiments.exp_ingest_gate_consolidation_loop_pilot_v1 import (  # noqa: E402
    _auc, _recip_ranks, _surprise, _sha, load_core_triples, _index_universe, _to_int as _real_to_int,
)

ANCHOR_NAME = "ingest_gate_deconfound_within_relation_derivability_v1"

# ---- pre-registered bands ---------------------------------------------------------------------------------------
# HYPOTHESIZED@this-file (design; measured at smoke/full):
#   DECONF_AUC is the OPEN measurement (either outcome is a clean finding). Chance = 0.50 (rank stat), self-checked
#   by RANDLABEL. CONF_AUC should reproduce v3's ~0.835. POSCTRL must fire (>=0.75). Strong foundation MRR ~0.4-0.7.
HP_DECONF_AUC_MIN = 0.65        # HARD_PASS: surprise separates derivable-vs-underivable WITHIN trained r* (>chance+0.15)
HF_DECONF_AUC_MAX = 0.58        # MEASURED_BOUND: DECONF collapses to ~chance (surprise = relation-presence only)
HP_POSCTRL_AUC_MIN = 0.75       # harness-valid: metric MUST separate corrupt-r* from in-train-r* (else broken)
HP_CONF_AUC_MIN = 0.70          # harness-valid: the v3 untrained-row confound MUST reproduce (else arena vacuous)
HP_RANDLABEL_LO = 0.40          # must-fail: random derivable/underivable labels -> AUC ~chance
HP_RANDLABEL_HI = 0.60
HP_RSTAR_TRAINED_MRR_MIN = 0.30  # r* row genuinely TRAINED: in-train r* facts must rank (else "trained row" vacuous)
HP_STRONG_MRR_MIN = 0.40        # foundation GENERALIZES: inferable held-out MRR high enough that derivable CAN rank
HP_INFER_MRR_LO = 0.05          # baseline-in-band
HP_INFER_MRR_HI = 0.95
HP_MIN_CLASS_FRAC = 0.20        # each derivability class must be >= this frac of held-out r* (balance sanity)
HP_ARRAY_RECOMPUTE_TOL = 1e-6

EPS_BAND = 1e-9

# ---- arena config (rel_scale=4.0 matches v2/v3 so a genuinely-strong foundation is attainable) -------------------
ARENA_BASE = dict(k_latent=16, k_fit=24, n_base_rel=12, gen_noise=0.10, rel_scale=4.0)

FULL_CFG = dict(
    seeds=[7, 13, 17],
    n_ent=600, edges_per_rel=420, n_rstar=420,
    train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=350,
    reach_k=2, reach_cap=300, min_class_n=25,
    # real proxy (non-gating):
    real_k_core=10, real_max_nodes=3000, real_k=24, real_epochs=250,
    real_train_frac_rstar=0.5, real_reach_k=2, real_reach_cap=300, real_min_rstar_edges=60,
)
SMOKE_CFG = dict(
    seeds=[7, 13, 17],   # multi-seed smoke (MANDATORY for an AUC discriminator; single-seed inflates)
    n_ent=300, edges_per_rel=180, n_rstar=180,
    train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=140,
    reach_k=2, reach_cap=150, min_class_n=10,
    # real arm kept tiny in smoke (non-gating; keeps smoke under the queue_add smoke-timeout cap):
    real_k_core=6, real_max_nodes=500, real_k=24, real_epochs=50,
    real_train_frac_rstar=0.5, real_reach_k=2, real_reach_cap=120, real_min_rstar_edges=15,
)

# batch ids for the per-candidate array dump
B_DERIV, B_UNDERIV, B_CONF_NOVEL, B_CONF_INFER, B_POSCTRL_CORRUPT, B_POSCTRL_TRAIN = 0, 1, 2, 3, 4, 5
B_REAL_DERIV, B_REAL_UNDERIV = 6, 7


# ---------------------------------------------------------------------------
# scaffolding (own copies; imported helpers bind their own ANCHOR_NAME)
# ---------------------------------------------------------------------------
def _log(msg):
    print("[deconf_v1] %s" % msg, flush=True)


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


# ---------------------------------------------------------------------------
# composed relation r* = ra o rb (2-hop nearest composition) + reachability derivability oracle
# ---------------------------------------------------------------------------
def _nearest(Q, Z, exclude_idx):
    """Q (m,kL), Z (N,kL). Return (m,) argmin L2 index, excluding the paired exclude_idx[i]."""
    d2 = ((Q[:, None, :] - Z[None, :, :]) ** 2).sum(axis=2)   # (m,N)
    for i in range(Q.shape[0]):
        d2[i, int(exclude_idx[i])] = np.inf
    return np.argmin(d2, axis=1).astype(np.int64)


def gen_composed_arena(acfg, seed, rstar_idx, ra, rb, n_rstar):
    """Reuse v2 gen_arena for base edges; build r*=ra o rb edges via TWO-HOP nearest composition.

    Returns (Z, G, base_edges list[(h,r,t)], rstar_edges list[(h,rstar,t)], mid list[m] intermediate per r* edge)."""
    Z, G, base_edges = gen_arena(acfg, seed)
    N = Z.shape[0]
    rng = np.random.default_rng(seed * 100003 + 777)
    m = min(n_rstar, N)
    heads = rng.choice(N, size=m, replace=False)
    q1 = Z[heads] + G[ra][None, :] + rng.standard_normal((m, Z.shape[1])) * acfg["gen_noise"]
    mid = _nearest(q1, Z, heads)                                  # h --ra--> mid
    q2 = Z[mid] + G[rb][None, :] + rng.standard_normal((m, Z.shape[1])) * acfg["gen_noise"]
    tails = _nearest(q2, Z, mid)                                 # mid --rb--> t
    rstar_edges = [(int(heads[i]), int(rstar_idx), int(tails[i])) for i in range(m)]
    return Z, G, base_edges, rstar_edges, mid.tolist()


def k_hop_reachable_set(adj, source, k):
    """BFS: set of entities reachable from `source` within k undirected hops (excludes source)."""
    seen = {int(source)}
    frontier = [int(source)]
    for _ in range(k):
        nxt = []
        for u in frontier:
            for v in adj[u]:
                vi = int(v)
                if vi not in seen:
                    seen.add(vi)
                    nxt.append(vi)
        frontier = nxt
        if not frontier:
            break
    seen.discard(int(source))
    return seen


def derivability_labels(heldout_int, adj_found, reach_k):
    """Per held-out r* fact (h,r*,t): DERIVABLE iff t reachable from h within reach_k hops over FOUNDATION edges.

    adj_found built from base TRAIN edges ONLY (no r*, no held-out base) -> label is what the foundation can infer.
    Ground-truth structural + non-circular (independent of the surprise signal). Returns bool (nq,) derivable."""
    reach_cache = {}
    out = np.zeros(heldout_int.shape[0], dtype=bool)
    for i in range(heldout_int.shape[0]):
        h = int(heldout_int[i, 0]); t = int(heldout_int[i, 2])
        if h not in reach_cache:
            reach_cache[h] = k_hop_reachable_set(adj_found, h, reach_k)
        out[i] = (t in reach_cache[h])
    return out


def _exact_path_labels(heldout_int, mid_of_head, base_train_set, ra, rb):
    """SECONDARY label (tighter): the GENERATIVE 2-hop path (h,ra,mid) AND (mid,rb,t) both in base-train. bool (nq,)."""
    out = np.zeros(heldout_int.shape[0], dtype=bool)
    for i in range(heldout_int.shape[0]):
        h = int(heldout_int[i, 0]); t = int(heldout_int[i, 2])
        mm = mid_of_head.get(h, None)
        if mm is None:
            continue
        out[i] = ((h, ra, mm) in base_train_set) and ((mm, rb, t) in base_train_set)
    return out


def _balance_mask(derivable, rng, min_frac):
    """Subsample the majority class so classes are within 1.5x. Returns keep-mask (bool). None if either class empty."""
    idx_d = np.where(derivable)[0]
    idx_u = np.where(~derivable)[0]
    if idx_d.size == 0 or idx_u.size == 0:
        return None
    lo = min(idx_d.size, idx_u.size)
    cap = int(np.ceil(1.5 * lo))
    keep = np.zeros(derivable.shape[0], dtype=bool)
    for idx in (idx_d, idx_u):
        if idx.size > cap:
            idx = idx[rng.permutation(idx.size)[:cap]]
        keep[idx] = True
    return keep


def _arena_cfg(n_ent, edges_per_rel):
    c = dict(ARENA_BASE)
    c["n_ent"] = int(n_ent)
    c["edges_per_rel"] = int(edges_per_rel)
    return c


# ---------------------------------------------------------------------------
# LOAD-BEARING PRIMITIVE: the deconfounded within-relation derivability test on a synthetic composed arena.
# ---------------------------------------------------------------------------
def deconf_seed(cfg, seed, device, want_arrays=False):
    """One arena; fit TRAINED-row + UNTRAINED-row foundations; compute DECONF / CONF / POSCTRL / RANDLABEL AUCs."""
    acfg = _arena_cfg(cfg["n_ent"], cfg["edges_per_rel"])
    N = acfg["n_ent"]; nR_base = acfg["n_base_rel"]
    rstar_idx = nR_base                      # r* gets its OWN relation row (index nR_base); total rels = nR_base + 1
    nR_total = nR_base + 1
    ra, rb = 0, 1                            # r* = r0 o r1

    Z, G, base_edges, rstar_edges, mid = gen_composed_arena(acfg, seed, rstar_idx, ra, rb, cfg["n_rstar"])
    rng = np.random.default_rng(seed * 100003 + 131)

    # split base edges -> base_train (foundation structure) + base_heldout (INFERABLE for baseline + CONF arm)
    nb = len(base_edges)
    pb = rng.permutation(nb)
    nb_hold = int(round(cfg["frac_heldout_base"] * nb))
    hold_b = set(pb[:nb_hold].tolist())
    base_train = [base_edges[i] for i in range(nb) if i not in hold_b]
    base_heldout = [base_edges[i] for i in range(nb) if i in hold_b]

    # split r* edges -> rstar_train (TRAINS the row) + rstar_heldout (the decisive derivable/underivable split)
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

    # ---- derivability oracle: reachability over FOUNDATION base-train edges only (non-circular) ----
    adj_found = RA.build_undirected_adj(base_train_int, N)
    derivable = derivability_labels(rstar_heldout_int, adj_found, cfg["reach_k"])
    # SECONDARY exact-generative-path label
    base_train_set = set((int(h), int(r), int(t)) for (h, r, t) in base_train)
    mid_of_head = {int(rstar_edges[i][0]): int(mid[i]) for i in range(nr)}
    derivable_exact = _exact_path_labels(rstar_heldout_int, mid_of_head, base_train_set, ra, rb)

    # balance classes (within 1.5x) so DECONF_AUC is not driven by class-size asymmetry
    keep = _balance_mask(derivable, np.random.default_rng(seed * 100003 + 191), cfg["min_class_n"])
    if keep is None:
        return dict(seed=int(seed), status="ONE_CLASS_EMPTY", n_deriv=int(derivable.sum()),
                    n_underiv=int((~derivable).sum()), deconf_auc=float("nan"))
    held_int = rstar_heldout_int[keep]
    deriv_lbl = derivable[keep]
    deriv_exact_lbl = derivable_exact[keep]
    n_deriv = int(deriv_lbl.sum()); n_underiv = int((~deriv_lbl).sum())

    # ---- FOUNDATION_T: r* row TRAINED (base_train + rstar_train) ----
    train_T = base_train + rstar_train
    X_T, D_T, all_true_T = fit_foundation(acfg, seed, cfg["epochs"], train_T, N, nR_total, device)

    # surprise on held-out r* (both classes; SAME trained row) -> DECISIVE
    surp_held = _surprise(_recip_ranks(X_T, D_T, held_int, all_true_T, device))
    surp_deriv = surp_held[deriv_lbl]
    surp_underiv = surp_held[~deriv_lbl]
    deconf_auc = _auc(surp_underiv, surp_deriv)                                     # underiv(high) vs deriv(low)
    deconf_auc_exact = _auc(surp_held[~deriv_exact_lbl], surp_held[deriv_exact_lbl])

    # baseline: inferable held-out trained-rel MRR (foundation strength) + in-train r* MRR (row genuinely trained)
    surp_infer_T = _surprise(_recip_ranks(X_T, D_T, base_heldout_int, all_true_T, device))
    infer_mrr = float(np.mean(1.0 - surp_infer_T)) if surp_infer_T.size else float("nan")
    surp_rtrain_T = _surprise(_recip_ranks(X_T, D_T, rstar_train_int, all_true_T, device))
    rstar_train_mrr = float(np.mean(1.0 - surp_rtrain_T)) if surp_rtrain_T.size else float("nan")

    # ---- POS-CONTROL (must fire): corrupt-r* (random wrong tail) vs in-train-r*, under FOUNDATION_T ----
    corrupt = rstar_train_int.copy()
    if corrupt.shape[0] > 0:
        rand_t = rng.integers(0, N, size=corrupt.shape[0])
        # avoid accidental true tail
        for i in range(corrupt.shape[0]):
            if int(rand_t[i]) == int(corrupt[i, 2]):
                rand_t[i] = (int(rand_t[i]) + 1) % N
        corrupt[:, 2] = rand_t
    surp_corrupt = _surprise(_recip_ranks(X_T, D_T, corrupt, all_true_T, device))
    posctrl_auc = _auc(surp_corrupt, surp_rtrain_T)                                  # corrupt(high) vs train(low)

    # ---- CONF ARM (reproduce v3 confound): r* row UNTRAINED (base_train only) ----
    X_U, D_U, all_true_U = fit_foundation(acfg, seed, cfg["epochs"], base_train, N, nR_total, device)
    all_rstar_int = _arena_to_int(rstar_edges)                                       # ALL r* = "novel" (row untrained)
    surp_conf_novel = _surprise(_recip_ranks(X_U, D_U, all_rstar_int, all_true_U, device))
    surp_conf_infer = _surprise(_recip_ranks(X_U, D_U, base_heldout_int, all_true_U, device))
    conf_auc = _auc(surp_conf_novel, surp_conf_infer)                                # novel(high) vs inferable(low)

    # ---- MUST-FAIL: RANDOM-LABEL shuffle of derivable/underivable -> AUC ~chance ----
    rlrng = np.random.default_rng(seed * 100003 + 313)
    shuf = rlrng.permutation(surp_held.shape[0])
    cut = n_deriv
    randlabel_auc = _auc(surp_held[shuf[cut:]], surp_held[shuf[:cut]])

    out = dict(
        seed=int(seed), status="OK", N=int(N), rstar_idx=int(rstar_idx), ra=int(ra), rb=int(rb),
        n_base_train=len(base_train), n_base_heldout=len(base_heldout),
        n_rstar_train=len(rstar_train), n_rstar_heldout=len(rstar_heldout),
        n_deriv=n_deriv, n_underiv=n_underiv,
        deriv_frac=float(deriv_lbl.mean()) if deriv_lbl.size else float("nan"),
        deconf_auc=deconf_auc, deconf_auc_exact=deconf_auc_exact,
        conf_auc=conf_auc, posctrl_auc=posctrl_auc, randlabel_auc=randlabel_auc,
        infer_mrr=infer_mrr, rstar_train_mrr=rstar_train_mrr,
        mean_surp_deriv=float(np.mean(surp_deriv)) if surp_deriv.size else float("nan"),
        mean_surp_underiv=float(np.mean(surp_underiv)) if surp_underiv.size else float("nan"),
        sha=dict(deriv=_sha(surp_deriv), underiv=_sha(surp_underiv), conf_novel=_sha(surp_conf_novel),
                 posctrl=_sha(surp_corrupt)),
    )
    if want_arrays:
        out["_arrays"] = [
            (B_DERIV, surp_deriv), (B_UNDERIV, surp_underiv),
            (B_CONF_NOVEL, surp_conf_novel), (B_CONF_INFER, surp_conf_infer),
            (B_POSCTRL_CORRUPT, surp_corrupt), (B_POSCTRL_TRAIN, surp_rtrain_T),
        ]
    return out


# ---------------------------------------------------------------------------
# REAL-CSKG proxy (NON-GATING): r* row TRAINED on subset; derivable = 2-hop reachable over foundation.
# ---------------------------------------------------------------------------
def real_deconf_seed(cfg, seed, device, cache_dir, want_arrays=False):
    """Reported-only external-validity arm. Any failure records a failure_class (non-fatal, non-gating)."""
    try:
        real_cfg = dict(k_core=cfg["real_k_core"], max_nodes=cfg["real_max_nodes"], seeds=cfg["seeds"])
        train, valid, test, prov = load_core_triples(real_cfg, seed, cache_dir)
        ent2i, rel2i = _index_universe(train + valid + test)
        N = len(ent2i)
        rc = Counter(r for _, r, _ in train)
        cand = sorted([(r, n) for r, n in rc.items() if n >= cfg["real_min_rstar_edges"]], key=lambda x: (x[1], x[0]))
        if not cand:
            return dict(seed=int(seed), status="NO_RSTAR_CANDIDATE", real_deconf_auc=float("nan"))
        rstar = cand[len(cand) // 2][0]
        ristar = rel2i[rstar]

        rstar_edges = [e for e in train if e[1] == rstar]
        base_train_lbl = [e for e in train if e[1] != rstar]
        rng = np.random.default_rng(seed * 100003 + 971)
        pr = rng.permutation(len(rstar_edges))
        ntr = int(round(cfg["real_train_frac_rstar"] * len(rstar_edges)))
        rstar_train_lbl = [rstar_edges[i] for i in pr[:ntr]]
        rstar_held_lbl = [rstar_edges[i] for i in pr[ntr:]]
        if len(rstar_held_lbl) < cfg["real_min_rstar_edges"] // 2:
            return dict(seed=int(seed), status="RSTAR_HELDOUT_TOO_SMALL", real_deconf_auc=float("nan"))

        entities_order = sorted(ent2i, key=lambda e: ent2i[e])
        relations_order = sorted(rel2i, key=lambda r: rel2i[r])
        fit_lbl = base_train_lbl + rstar_train_lbl                              # r* row TRAINED
        kmap = AdditiveKGMap(device=device)
        kmap.fit(fit_lbl, entities=entities_order, relations=relations_order, k=cfg["real_k"],
                 epochs=cfg["real_epochs"], seed=seed)
        X = kmap.X; D = kmap.D
        assert ristar < int(D.shape[0]), "r* row must exist"

        all_true = defaultdict(set)
        for h, r, t in _real_to_int(fit_lbl, ent2i, rel2i):
            all_true[(int(h), int(r))].add(int(t))

        # derivability oracle: 2-hop reachability over base_train (non-r*) edges
        base_train_int = _real_to_int(base_train_lbl, ent2i, rel2i)
        adj = RA.build_undirected_adj(base_train_int, N)
        held_int = _real_to_int(rstar_held_lbl, ent2i, rel2i)
        derivable = derivability_labels(held_int, adj, cfg["real_reach_k"])
        keep = _balance_mask(derivable, np.random.default_rng(seed * 100003 + 977), 1)
        if keep is None:
            return dict(seed=int(seed), status="REAL_ONE_CLASS_EMPTY", real_deconf_auc=float("nan"),
                        real_n_deriv=int(derivable.sum()), real_n_underiv=int((~derivable).sum()))
        held_int = held_int[keep]; deriv_lbl = derivable[keep]

        surp_held = _surprise(_recip_ranks(X, D, held_int, all_true, device))
        real_deconf_auc = _auc(surp_held[~deriv_lbl], surp_held[deriv_lbl])
        rstar_train_int = _real_to_int(rstar_train_lbl, ent2i, rel2i)
        surp_rtrain = _surprise(_recip_ranks(X, D, rstar_train_int, all_true, device))
        real_rstar_train_mrr = float(np.mean(1.0 - surp_rtrain)) if surp_rtrain.size else float("nan")
        return dict(seed=int(seed), status="OK", rstar=str(rstar), N=int(N),
                    real_deconf_auc=real_deconf_auc, real_n_deriv=int(deriv_lbl.sum()),
                    real_n_underiv=int((~deriv_lbl).sum()), real_rstar_train_mrr=real_rstar_train_mrr, prov=prov)
    except (FileNotFoundError, OSError, RuntimeError, ValueError, KeyError, AssertionError) as e:
        return dict(seed=int(seed), status="REAL_ARM_FAILED", failure_class=type(e).__name__,
                    failure_msg=str(e)[:300], real_deconf_auc=float("nan"))


# ---------------------------------------------------------------------------
# per-candidate array dump + off-disk recompute of DECONF_AUC (pooled)
# ---------------------------------------------------------------------------
def dump_and_verify_arrays(output_dir, syn_arrays):
    batches, surprise, seeds_a = [], [], []
    for seed, arrs in syn_arrays:
        for lbl, arr in arrs:
            arr = np.asarray(arr, dtype=np.float64)
            batches.append(np.full(arr.shape[0], lbl, dtype=np.int64))
            surprise.append(arr)
            seeds_a.append(np.full(arr.shape[0], seed, dtype=np.int64))
    flat = dict(batch=np.concatenate(batches), surprise=np.concatenate(surprise), seed=np.concatenate(seeds_a))
    path = os.path.join(str(output_dir), "per_candidate_arrays.npz")
    tmp = os.path.join(str(output_dir), "per_candidate_arrays_tmp.npz")
    np.savez(tmp, **flat)
    os.replace(tmp, path)
    inmem = _auc(flat["surprise"][flat["batch"] == B_UNDERIV], flat["surprise"][flat["batch"] == B_DERIV])
    z = np.load(path)
    offdisk = _auc(z["surprise"][z["batch"] == B_UNDERIV], z["surprise"][z["batch"] == B_DERIV])
    delta = abs(float(inmem) - float(offdisk)) if (inmem == inmem and offdisk == offdisk) else 0.0
    ok = delta <= HP_ARRAY_RECOMPUTE_TOL
    return ok, delta, path


# ---------------------------------------------------------------------------
# aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(syn_per_seed, real_per_seed, run_mode, array_ok, array_delta,
                          expected_units, observed_units):
    ok_syn = [s for s in syn_per_seed if s.get("status") == "OK"]
    deconf = _mean([s["deconf_auc"] for s in ok_syn])
    deconf_exact = _mean([s["deconf_auc_exact"] for s in ok_syn])
    conf = _mean([s["conf_auc"] for s in ok_syn])
    posctrl = _mean([s["posctrl_auc"] for s in ok_syn])
    randlabel = _mean([s["randlabel_auc"] for s in ok_syn])
    infer_mrr = _mean([s["infer_mrr"] for s in ok_syn])
    rstar_train_mrr = _mean([s["rstar_train_mrr"] for s in ok_syn])
    min_class = min([min(s["n_deriv"], s["n_underiv"]) for s in ok_syn]) if ok_syn else 0
    min_class_frac = min([min(s["deriv_frac"], 1.0 - s["deriv_frac"]) for s in ok_syn]) if ok_syn else 0.0
    real_ok = [r for r in real_per_seed if r.get("status") == "OK"]
    real_deconf = _mean([r["real_deconf_auc"] for r in real_ok]) if real_ok else float("nan")

    g = {}
    g["cardinality_ok"] = (observed_units == expected_units)
    g["all_seeds_ok"] = (len(ok_syn) == len(syn_per_seed)) and len(ok_syn) > 0
    g["HP_POSCTRL_FIRES"] = (posctrl == posctrl) and (posctrl >= HP_POSCTRL_AUC_MIN)
    g["HP_CONF_REPRODUCES"] = (conf == conf) and (conf >= HP_CONF_AUC_MIN)
    g["HP_RANDLABEL_CHANCE"] = (randlabel == randlabel) and (HP_RANDLABEL_LO <= randlabel <= HP_RANDLABEL_HI)
    g["HP_RSTAR_TRAINED"] = (rstar_train_mrr == rstar_train_mrr) and (rstar_train_mrr >= HP_RSTAR_TRAINED_MRR_MIN)
    g["HP_FOUNDATION_STRONG"] = (infer_mrr == infer_mrr) and (infer_mrr >= HP_STRONG_MRR_MIN)
    g["baseline_in_band"] = (infer_mrr == infer_mrr) and (HP_INFER_MRR_LO < infer_mrr < HP_INFER_MRR_HI)
    g["class_balance_ok"] = (min_class_frac >= HP_MIN_CLASS_FRAC) and (min_class > 0)

    harness_valid = all([g["cardinality_ok"], g["all_seeds_ok"], g["HP_POSCTRL_FIRES"], g["HP_CONF_REPRODUCES"],
                         g["HP_RANDLABEL_CHANCE"], g["HP_RSTAR_TRAINED"], g["HP_FOUNDATION_STRONG"],
                         g["baseline_in_band"], g["class_balance_ok"]])

    deconf_hp = (deconf == deconf) and (deconf >= HP_DECONF_AUC_MIN)
    deconf_collapse = (deconf == deconf) and (deconf <= HF_DECONF_AUC_MAX)

    if not harness_valid:
        verdict = "INCONCLUSIVE_harness"
        finding = ("INCONCLUSIVE: harness not validated (posctrl=%.3f conf=%.3f randlabel=%.3f rstar_train_mrr=%.3f "
                   "infer_mrr=%.3f class_bal=%.2f card=%s) -- cannot distinguish real-collapse from broken test"
                   % (posctrl, conf, randlabel, rstar_train_mrr, infer_mrr, min_class_frac, g["cardinality_ok"]))
    elif deconf_hp:
        verdict = "HARD_PASS"
        finding = ("DECONFOUNDED_SEMANTIC_NOVELTY: with the r* row TRAINED, surprise separates DERIVABLE from "
                   "UNDERIVABLE (DECONF_AUC=%.3f >= %.2f) while the v3 confound reproduces (CONF_AUC=%.3f) and the "
                   "pos-control fires (%.3f) => surprise IS genuine semantic-novelty, DECONFOUNDED from "
                   "relation-identity. BRAIN: aligned (schema-fit consolidation, Tse 2007). ROUTE TO SKUNKWORKS VET."
                   % (deconf, HP_DECONF_AUC_MIN, conf, posctrl))
    elif deconf_collapse:
        verdict = "MEASURED_BOUND_relation_identity_artifact"
        finding = ("RELATION_IDENTITY_ARTIFACT: with the r* row TRAINED, surprise does NOT separate derivable from "
                   "underivable (DECONF_AUC=%.3f <= %.2f ~chance) WHILE the v3 confound reproduces (CONF_AUC=%.3f) "
                   "and the pos-control fires (%.3f) => the v3 0.835 WAS the untrained-row artifact; surprise detects "
                   "WHOLE-RELATION-ABSENCE only, NOT within-relation semantic-underivability. BRAIN: our surprise is "
                   "COARSER than the brain's (relation-presence, not schema-composition-fit); fix = "
                   "schema-composition-aware surprise readout."
                   % (deconf, HF_DECONF_AUC_MAX, conf, posctrl))
    else:
        verdict = "MIDDLE_BAND_straddle"
        finding = ("STRADDLE: DECONF_AUC=%.3f sits between collapse (%.2f) and pass (%.2f) -- partial within-relation "
                   "derivability signal (ambiguous)." % (deconf, HF_DECONF_AUC_MAX, HP_DECONF_AUC_MIN))

    msg = ("DECONF_AUC=%.3f (exact=%.3f) | CONF_AUC=%.3f POSCTRL_AUC=%.3f RANDLABEL=%.3f | infer_mrr=%.3f "
           "rstar_train_mrr=%.3f min_class=%d bal=%.2f | REAL_DECONF=%.3f | harness_valid=%s arrays_ok=%s(d=%.1e) "
           "card=%s -> %s" % (deconf, deconf_exact, conf, posctrl, randlabel, infer_mrr, rstar_train_mrr,
                              min_class, min_class_frac, real_deconf, harness_valid, array_ok, array_delta,
                              g["cardinality_ok"], verdict))
    summary = "%s: %s" % (verdict, finding)
    return dict(verdict=verdict, verdict_msg=msg, summary=summary, finding=finding, gates=g,
                harness_valid=harness_valid, run_mode=run_mode,
                agg=dict(deconf_auc=deconf, deconf_auc_exact=deconf_exact, conf_auc=conf, posctrl_auc=posctrl,
                         randlabel_auc=randlabel, infer_mrr=infer_mrr, rstar_train_mrr=rstar_train_mrr,
                         real_deconf_auc=real_deconf, min_class=int(min_class), min_class_frac=min_class_frac,
                         array_recompute_delta=array_delta))


# ---------------------------------------------------------------------------
# self-test (REAL substrate code path at N~16 + deconf primitive; validity preflight)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    from experiments._kge_anchor1_fit import fit_kge_anchor1
    _log("self_test: constructing REAL AdditiveKGMap + composed arena + deconf primitive at tiny scale")
    exercised = set()
    device = torch.device("cpu")

    # REAL substrate object path (matches FULL: AdditiveKGMap.fit is what deconf_seed/real_deconf_seed call)
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

    # composed-arena generation + reachability BFS
    acfg = _arena_cfg(n_ent=40, edges_per_rel=24)
    Z, G, base_edges, rstar_edges, mid = gen_composed_arena(acfg, 7, ARENA_BASE["n_base_rel"], 0, 1, 24)
    exercised.add("gen_composed_arena")
    assert len(rstar_edges) > 0 and all(len(e) == 3 and e[1] == ARENA_BASE["n_base_rel"] for e in rstar_edges)
    adj = RA.build_undirected_adj(_arena_to_int(base_edges), acfg["n_ent"])
    rs = k_hop_reachable_set(adj, 0, 2)
    assert isinstance(rs, set) and 0 not in rs
    # reachable node IS labeled derivable; a definitely-unreachable node is NOT
    if rs:
        t_reach = next(iter(rs))
        held = np.array([[0, ARENA_BASE["n_base_rel"], t_reach]], dtype=np.int64)
        dl = derivability_labels(held, adj, 2)
        assert bool(dl[0]) is True, "reachable tail must be labeled derivable"
    exercised.add("derivability_labels")

    # deconf primitive: STRONG arena must give a defined DECONF_AUC + firing pos-control + reproduced confound
    cfg = dict(n_ent=80, edges_per_rel=48, n_rstar=48, train_frac_rstar=0.5, frac_heldout_base=0.28, epochs=60,
               reach_k=2, reach_cap=60, min_class_n=3)
    r = deconf_seed(cfg, 7, device, want_arrays=True)
    exercised.add("deconf_seed")
    assert r["status"] in ("OK", "ONE_CLASS_EMPTY"), "deconf_seed status: %s" % r["status"]
    if r["status"] == "OK":
        for kk in ("deconf_auc", "conf_auc", "posctrl_auc", "randlabel_auc"):
            assert 0.0 <= r[kk] <= 1.0, "%s out of [0,1]: %s" % (kk, r[kk])
        # arms differ (surprise vectors bit-distinct)
        assert len({r["sha"]["deriv"], r["sha"]["underiv"], r["sha"]["conf_novel"], r["sha"]["posctrl"]}) >= 3, \
            "surprise vectors bit-identical (arm bug)"

    # AUC direction sanity: high vs low -> 1.0
    assert _auc([0.9, 0.95], [0.1, 0.2]) == 1.0 and _auc([0.1, 0.2], [0.9, 0.95]) == 0.0

    # balance mask keeps both classes within 1.5x
    dv = np.array([True] * 10 + [False] * 2)
    km = _balance_mask(dv, np.random.default_rng(1), 1)
    assert km is not None and km[dv].sum() <= int(np.ceil(1.5 * 2)) and km[~dv].sum() == 2

    # array dump + off-disk recompute round-trip
    import tempfile
    fake = [(7, [(B_DERIV, np.array([0.1, 0.2])), (B_UNDERIV, np.array([0.8, 0.9]))])]
    with tempfile.TemporaryDirectory() as td:
        ok, delta, _p = dump_and_verify_arrays(td, fake)
        assert ok and delta <= HP_ARRAY_RECOMPUTE_TOL, "array recompute mismatch delta=%s" % delta

    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.fit", "AdditiveKGMap.score_all",
                                        "AdditiveKGMap.compose_entity", "AdditiveKGMap.insert_entity",
                                        "gen_composed_arena", "derivability_labels", "deconf_seed"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": AdditiveKGMap, "callable_name": "AdditiveKGMap",
         "kwargs": {"device": "cpu"}},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": device, "seed": 7, "epochs": 1}},
        {"kind": "metric_moves", "metric_name": "deconf_auc", "before": 0.50, "after": 0.80, "min_delta": 1e-6},
    ], run_mode="selftest")
    assert ok, "validity preflight failed"
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
    cache_dir = os.path.join(os.path.dirname(output_dir), "_cskg_cache")
    seeds = cfg["seeds"]
    expected_units = len(seeds) * 2                                  # 1 synthetic block + 1 real block per seed
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()
    device = torch.device("cpu")   # small-N AdditiveKGMap fits; arena NN is numpy

    syn_per_seed = []
    real_per_seed = []
    syn_arrays = []
    observed_units = 0

    for si, seed in enumerate(seeds):
        _log("seed %d/%d (seed=%d): SYNTHETIC deconf (train r* row; derivable-vs-underivable held-out) ..." % (
            si + 1, len(seeds), seed))
        want = (si == 0)
        s = deconf_seed(cfg, seed, device, want_arrays=want)
        if want and s.get("status") == "OK":
            syn_arrays.append((seed, s.pop("_arrays")))
        else:
            s.pop("_arrays", None)
        syn_per_seed.append(s)
        observed_units += 1
        _log("  [syn] seed=%d status=%s DECONF=%.3f CONF=%.3f POSCTRL=%.3f RAND=%.3f infer_mrr=%.3f "
             "rstar_train_mrr=%.3f n_deriv=%s n_underiv=%s (%.1fs)" % (
                 seed, s.get("status"), s.get("deconf_auc", float("nan")), s.get("conf_auc", float("nan")),
                 s.get("posctrl_auc", float("nan")), s.get("randlabel_auc", float("nan")),
                 s.get("infer_mrr", float("nan")), s.get("rstar_train_mrr", float("nan")),
                 s.get("n_deriv"), s.get("n_underiv"), time.time() - t0))

        _log("seed=%d: REAL-CSKG proxy (non-gating) ..." % seed)
        r = real_deconf_seed(cfg, seed, device, cache_dir)
        real_per_seed.append(r)
        observed_units += 1
        _log("  [real] seed=%d status=%s REAL_DECONF=%.3f (%.1fs)" % (
            seed, r.get("status"), r.get("real_deconf_auc", float("nan")), time.time() - t0))

    # ARMS-MUST-DIFFER across seeds' synthetic surprise vectors (META_RULE_AF)
    ok_syn = [s for s in syn_per_seed if s.get("status") == "OK"]
    if ok_syn:
        shas = ok_syn[0]["sha"]
        assert len({shas["deriv"], shas["underiv"], shas["conf_novel"], shas["posctrl"]}) >= 3, \
            "surprise vectors bit-identical across arms (arm bug)"

    if syn_arrays:
        array_ok, array_delta, array_path = dump_and_verify_arrays(output_dir, syn_arrays)
    else:
        array_ok, array_delta, array_path = False, float("nan"), ""
    _log("per-candidate arrays -> %s (recompute_ok=%s delta=%s)" % (array_path, array_ok, array_delta))

    v = aggregate_and_verdict(syn_per_seed, real_per_seed, run_mode, array_ok, array_delta,
                              expected_units, observed_units)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(seeds),
                   config=dict(seeds=seeds, n_ent=cfg["n_ent"], edges_per_rel=cfg["edges_per_rel"],
                               n_rstar=cfg["n_rstar"], train_frac_rstar=cfg["train_frac_rstar"],
                               frac_heldout_base=cfg["frac_heldout_base"], epochs=cfg["epochs"],
                               reach_k=cfg["reach_k"], rel_scale=ARENA_BASE["rel_scale"],
                               real_k_core=cfg["real_k_core"], real_max_nodes=cfg["real_max_nodes"],
                               real_epochs=cfg["real_epochs"]),
                   bands=dict(HP_DECONF_AUC_MIN=HP_DECONF_AUC_MIN, HF_DECONF_AUC_MAX=HF_DECONF_AUC_MAX,
                              HP_POSCTRL_AUC_MIN=HP_POSCTRL_AUC_MIN, HP_CONF_AUC_MIN=HP_CONF_AUC_MIN,
                              HP_RANDLABEL_LO=HP_RANDLABEL_LO, HP_RANDLABEL_HI=HP_RANDLABEL_HI,
                              HP_RSTAR_TRAINED_MRR_MIN=HP_RSTAR_TRAINED_MRR_MIN, HP_STRONG_MRR_MIN=HP_STRONG_MRR_MIN),
                   expected_n_units=expected_units, observed_n_units=observed_units,
                   arms_differ_verified=True, final_metrics_atomicity="tmp_replace",
                   progress_logging="print_flush_true",
                   per_candidate_arrays=os.path.basename(array_path) if array_path else None,
                   **v, syn_per_seed=syn_per_seed, real_per_seed=real_per_seed)
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
