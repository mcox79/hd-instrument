"""Ingest-gate v3: LOCATE THE COLLAPSE KNEE + TEST AT REAL-CSKG STRENGTH.

The v2 VET (MEASURED@data/exp_ingest_gate_strong_foundation_novelty_v2/metrics.json) confirmed SURPRISE separates
NOVEL-vs-INFERABLE (deconfounded: both held-out -> KEY-AUC ~0.988 on a strong foundation) BUT the separation is
GENERALIZATION-GATED not strength-graded: it saturates at arena-weak MRR ~0.33 and collapses toward chance
(~0.605) at a DEAD non-generalizing foundation (MRR ~0.013). The OPEN QUESTION this cell answers: real CSKG caps at
MRR ~0.13 (VET'd held-out 0.1282), which sits BETWEEN dead (0.013) and arena-weak (0.33). The collapse KNEE is
somewhere in [0.013, 0.33] and 0.13 could be on EITHER side. Two-part test:

  PART 1 -- LOCATE THE KNEE (fine sweep on the SAME v2 synthetic arena, epochs-only strength dial):
    sweep a DENSE epochs grid so inferable-heldout MRR spans ~[0.01, 0.6]; at each point measure the deconfounded
    KEY-AUC (novel-heldout vs inferable-heldout, BOTH untrained). Find where KEY-AUC transitions from ~chance to
    saturated. Report the located knee MRR. Is real ~0.13 above or below it?

  PART 2 -- TEST ON REAL CSKG (the actual regime):
    on the REAL CSKG k-core foundation at its native ~0.13 MRR (v1 data path, exp_ingest_gate_consolidation_loop_
    pilot_v1), withhold a real relation r*, measure KEY-AUC separating r*'s NOVEL edges from INFERABLE-heldout edges
    (valid+test) of TRAINED relations -- both untrained, deconfounded exactly as v2. POSITIVE CONTROL: a
    synthetic-strong functional-TransE foundation at MATCHED entity scale (N ~= real N); if the pos-control KEY-AUC
    FIRES but the real KEY-AUC COLLAPSES, the real foundation is genuinely BELOW the knee (a scaling requirement),
    NOT a broken harness.

VERDICT (envelope-fail-bands):
  HARD_PASS  = real KEY-AUC materially ABOVE the located knee (real above knee) AND pos-control fires
               => the ingest-gate novelty criterion WORKS in the REAL regime (a genuine real-data step).
  MEASURED_BOUND = real KEY-AUC ~chance (near the sweep floor) WHILE pos-control fires (real BELOW knee)
               => the novelty-gate REQUIRES scaling the foundation stronger first (a concrete scaling requirement;
               BRAIN-CHECK: schema-strength-gated novelty/prediction-error, Lisman-Grace/Duszkiewicz/Tse).
  MIDDLE_BAND = real KEY-AUC straddles the knee (ambiguous).
  INCONCLUSIVE = pos-control does NOT fire (harness cannot distinguish real-collapse from a broken test).
The located knee MRR is reported EITHER way.

REUSE (extend, don't rebuild): ALL v2 arena machinery (gen_arena / fit_foundation / KEY-AUC) + ALL v1 real-data
machinery (load_core_triples / AdditiveKGMap fit / surprise readout / deconfounded held-out splits). Only new: the
dense epochs sweep + knee interpolation + the matched-scale synthetic pos-control + per-candidate array dump.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (sweep low/high-epoch surprise vectors hash-distinct; real vs pos-control distinct)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: KEY-AUC is a rank statistic over two measured surprise distributions; no closed-form noise floor.
#   The "chance" reference is self-calibrated from the sweep's own DEAD floor (not an assumed 0.5).
# - baseline_in_band: real inferable-heldout MRR 0.02<mrr<0.95 verified; pos-control strong MRR > 0.4
# - discriminator survives scale: PART-1 sweep IS the scale axis (MRR 0.01->0.6); knee located from measured curve
# - cardinality_ok: EXPECTED_N_UNITS = n_seeds*(n_epoch_points + 2) [+2 = real + pos-control per seed]
# - HARD_PASS strictly above knee-mid + 5% band-width (META_RULE_L)
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test constructs AdditiveKGMap + fit + score_all + compose_entity + insert_entity at N~16
#   AND exercises arena_key_auc (the load-bearing PART-1/pos-control primitive) at N~16
# - deterministic seeding: fixed int seeds + np.random.default_rng(seed); no hash()-seeded RNG, no list(set()) order
# - progress_logging = print_flush_true (every sweep point + seed logs, flush=True)

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
# REUSE v2 arena machinery (importing the module does NOT run main; guarded by __main__)
from experiments.exp_ingest_gate_strong_foundation_novelty_v2 import (  # noqa: E402
    gen_arena, fit_foundation, _to_int as _arena_to_int, _mean,
)
# REUSE v1 real-data + metric machinery
from experiments.exp_ingest_gate_consolidation_loop_pilot_v1 import (  # noqa: E402
    _auc, _recip_ranks, _surprise, _sha, load_core_triples, _index_universe, _to_int as _real_to_int,
)

ANCHOR_NAME = "ingest_gate_knee_locate_real_regime_v3"

# ---- pre-registered bands ----------------------------------------------------------------------------------------
# HYPOTHESIZED@this-file (design; measured at smoke/full):
#   sweep KEY-AUC floor ~0.60 (dead) -> ceil ~0.97 (strong), knee near MRR 0.10-0.20 (unknown; that is the question).
#   pos-control (matched-scale synthetic-strong) KEY-AUC >= 0.75 (harness-valid). real KEY-AUC = the open measurement.
HP_POSCTRL_KEY_AUC_MIN = 0.75    # harness-valid gate: matched-scale strong synthetic foundation MUST fire
HP_SWEEP_RISE_MIN = 0.20         # sweep must show a real dose-response (ceil-floor) so the knee is locatable
HP_REAL_ABS_KEY_AUC_MIN = 0.70   # absolute floor for HARD_PASS: real KEY-AUC materially above chance (~0.55-0.60)
HP_REAL_MRR_LO = 0.02            # baseline-in-band: real inferable-heldout MRR must be a real (non-degenerate) regime
HP_REAL_MRR_HI = 0.95
HP_POSCTRL_MRR_MIN = 0.40        # pos-control must actually GENERALIZE (else "strong" is vacuous)
KNEE_BAND_FRAC = 0.05            # META_RULE_L: HARD_PASS requires real KEY-AUC >= knee_mid + 5% of (ceil-floor)
BELOW_KNEE_FRAC = 0.20           # BELOW-knee (scaling-required) if real KEY-AUC <= floor + 20% of (ceil-floor)
HP_ARRAY_RECOMPUTE_TOL = 1e-6

EPS_BAND = 1e-9

# ---- arena config (rel_scale=4.0 EXACTLY matches v2's arena so the located knee is comparable to v2's dead/weak
#      points; epochs is the ONLY strength dial). Dense low-end epochs so MRR spans ~[0.01, 0.6]. ---------------
ARENA_BASE = dict(k_latent=16, k_fit=24, n_base_rel=12, gen_noise=0.10, rel_scale=4.0, frac_heldout=0.28)

FULL_CFG = dict(
    seeds=[7, 13, 17],
    # PART 1 sweep arena (v2-matched n_ent=600, edges_per_rel=420):
    sweep_n_ent=600, sweep_edges_per_rel=420,
    sweep_epochs=[2, 3, 4, 6, 8, 11, 15, 20, 28, 40, 60, 90, 140, 220, 350],
    # PART 2 real CSKG:
    real_k_core=10, real_max_nodes=3500, real_k=24, real_epochs=300, real_reach_k=2, real_reach_cap=300,
    real_min_rstar_edges=40,
    # PART 2 pos-control (matched-scale synthetic-strong; N capped for NN-memory feasibility, same ORDER as real N):
    posctrl_n_ent=1200, posctrl_edges_per_rel=420, posctrl_epochs=350,
)
SMOKE_CFG = dict(
    seeds=[7],
    sweep_n_ent=300, sweep_edges_per_rel=220,
    sweep_epochs=[3, 12, 40, 120, 300],
    real_k_core=8, real_max_nodes=1500, real_k=24, real_epochs=120, real_reach_k=2, real_reach_cap=150,
    real_min_rstar_edges=15,
    posctrl_n_ent=500, posctrl_edges_per_rel=220, posctrl_epochs=200,
)

B_INFER_ARENA, B_NOVEL_ARENA, B_INFER_REAL, B_NOVEL_REAL = 0, 1, 2, 3


# ---------------------------------------------------------------------------
# scaffolding (own copies; imported helpers bind their own ANCHOR_NAME)
# ---------------------------------------------------------------------------
def _log(msg):
    print("[ingest_gate_v3] %s" % msg, flush=True)


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
# LOAD-BEARING PRIMITIVE: deconfounded KEY-AUC on a synthetic functional-TransE arena at a given strength (epochs).
# Withhold one relation as NOVEL (info absent from foundation) + hold out a fraction of trained-rel edges as
# INFERABLE (foundation CAN predict if strong). BOTH held-out -> KEY-AUC deconfounded from train-membership.
# ---------------------------------------------------------------------------
def arena_key_auc(cfg, seed, epochs, device, want_arrays=False):
    """(epochs, mrr, key_auc, ...) for a synthetic arena at foundation-strength `epochs`. Reuses v2 gen_arena/fit."""
    Z, G, edges = gen_arena(cfg, seed)
    N = cfg["n_ent"]; nR = cfg["n_base_rel"]
    rng = np.random.default_rng(seed * 100003 + 71)
    rstar = nR - 1
    novel_edges = [e for e in edges if e[1] == rstar]
    trained_edges = [e for e in edges if e[1] != rstar]
    ne = len(trained_edges)
    perm = rng.permutation(ne)
    n_hold = int(round(cfg["frac_heldout"] * ne))
    hold_idx = set(perm[:n_hold].tolist())
    train = [trained_edges[i] for i in range(ne) if i not in hold_idx]        # FOUNDATION train
    inferable = [trained_edges[i] for i in range(ne) if i in hold_idx]        # held-out, inferable
    infer_int = _arena_to_int(inferable)
    novel_int = _arena_to_int(novel_edges)
    X, D, all_true = fit_foundation(cfg, seed, epochs, train, N, nR, device)
    surp_infer = _surprise(_recip_ranks(X, D, infer_int, all_true, device))
    surp_novel = _surprise(_recip_ranks(X, D, novel_int, all_true, device))
    mrr = float(np.mean(1.0 - surp_infer)) if surp_infer.size else float("nan")
    key_auc = _auc(surp_novel, surp_infer)
    out = dict(epochs=int(epochs), mrr=mrr, key_auc=key_auc, n_infer=int(infer_int.shape[0]),
               n_novel=int(novel_int.shape[0]), surp_infer_sha=_sha(surp_infer), surp_novel_sha=_sha(surp_novel))
    if want_arrays:
        out["_surp_infer"] = surp_infer
        out["_surp_novel"] = surp_novel
    return out


def _arena_cfg(base, n_ent, edges_per_rel):
    c = dict(base)
    c["n_ent"] = int(n_ent)
    c["edges_per_rel"] = int(edges_per_rel)
    return c


# ---------------------------------------------------------------------------
# PART 2: REAL CSKG deconfounded KEY-AUC (v1 data path). Withhold real relation r*; NOVEL = r* edges (never in fit),
# INFERABLE = valid+test edges of TRAINED relations (never in fit). Both untrained -> deconfounded.
# ---------------------------------------------------------------------------
def _pick_rstar(train, min_edges):
    """Deterministic median-frequency relation with >= min_edges (a relation the foundation must genuinely infer,
    not a trivially-dominant hub relation). No hash(); pure frequency-sorted selection."""
    rc = Counter(r for _, r, _ in train)
    cand = sorted([(r, n) for r, n in rc.items() if n >= min_edges], key=lambda x: (x[1], x[0]))
    if not cand:
        cand = sorted(rc.items(), key=lambda x: (x[1], x[0]))
    return cand[len(cand) // 2][0]


def real_regime(cfg, seed, device, cache_dir, want_arrays=False):
    real_cfg = dict(k_core=cfg["real_k_core"], max_nodes=cfg["real_max_nodes"], seeds=cfg["seeds"])
    train, valid, test, prov = load_core_triples(real_cfg, seed, cache_dir)
    allpool = train + valid + test
    ent2i, rel2i = _index_universe(allpool)
    N = len(ent2i)
    rstar = _pick_rstar(train, cfg["real_min_rstar_edges"])
    ristar = rel2i[rstar]

    found = [e for e in train if e[1] != rstar]                              # FOUNDATION = train minus r*
    rstar_edges = [e for e in train if e[1] == rstar]                        # NOVEL (withheld relation)
    entities_order = sorted(ent2i, key=lambda e: ent2i[e])
    relations_order = sorted(rel2i, key=lambda r: rel2i[r])

    kmap = AdditiveKGMap(device=device)
    kmap.fit(found, entities=entities_order, relations=relations_order, k=cfg["real_k"], epochs=cfg["real_epochs"],
             seed=seed)
    X = kmap.X; D = kmap.D
    assert ristar < int(D.shape[0]), "r* row must exist in D universe"

    all_true = defaultdict(set)
    for h, r, t in _real_to_int(found, ent2i, rel2i):
        all_true[(int(h), int(r))].add(int(t))

    # INFERABLE-heldout = valid+test edges of TRAINED (non-r*) relations (never in fit)
    heldout = [e for e in (valid + test) if e[1] != rstar and e[1] in rel2i]
    infer_int = _real_to_int(heldout, ent2i, rel2i) if heldout else np.zeros((0, 3), dtype=np.int64)
    novel_int = _real_to_int(rstar_edges, ent2i, rel2i) if rstar_edges else np.zeros((0, 3), dtype=np.int64)

    surp_infer = _surprise(_recip_ranks(X, D, infer_int, all_true, device)) if infer_int.shape[0] else np.zeros(0)
    surp_novel = _surprise(_recip_ranks(X, D, novel_int, all_true, device)) if novel_int.shape[0] else np.zeros(0)
    real_mrr = float(np.mean(1.0 - surp_infer)) if surp_infer.size else float("nan")
    real_key_auc = _auc(surp_novel, surp_infer)

    out = dict(seed=int(seed), rstar=str(rstar), N=int(N), n_found=len(found), n_rstar=int(novel_int.shape[0]),
               n_infer=int(infer_int.shape[0]), real_mrr=real_mrr, real_key_auc=real_key_auc,
               surp_infer_sha=_sha(surp_infer), surp_novel_sha=_sha(surp_novel), prov=prov)
    if want_arrays:
        out["_surp_infer"] = surp_infer
        out["_surp_novel"] = surp_novel
    return out


# ---------------------------------------------------------------------------
# knee location (self-calibrated: floor = dead/lowest-MRR KEY-AUC, ceil = strongest KEY-AUC)
# ---------------------------------------------------------------------------
def aggregate_sweep(sweep_per_seed):
    """Average KEY-AUC + MRR per epoch across seeds -> a monotone-in-epochs curve."""
    epochs = [p["epochs"] for p in sweep_per_seed[0]]
    curve = []
    for j, ep in enumerate(epochs):
        mrr = _mean([s[j]["mrr"] for s in sweep_per_seed])
        auc = _mean([s[j]["key_auc"] for s in sweep_per_seed])
        curve.append(dict(epochs=int(ep), mrr=mrr, key_auc=auc))
    return curve


def locate_knee(curve):
    """Knee = interpolated MRR where the epoch-averaged KEY-AUC first crosses the floor/ceil midpoint (rising)."""
    aucs = [c["key_auc"] for c in curve if c["key_auc"] == c["key_auc"]]
    mrrs = [c["mrr"] for c in curve if c["key_auc"] == c["key_auc"]]
    if len(aucs) < 2:
        return dict(floor=float("nan"), ceil=float("nan"), mid=float("nan"), knee_mrr=float("nan"))
    floor = float(min(aucs)); ceil = float(max(aucs))
    mid = 0.5 * (floor + ceil)
    knee_mrr = float("nan")
    for i in range(1, len(aucs)):
        a0, a1 = aucs[i - 1], aucs[i]
        lo, hi = (a0, a1) if a0 <= a1 else (a1, a0)
        if lo <= mid <= hi and a1 != a0:
            frac = (mid - a0) / (a1 - a0)
            knee_mrr = float(mrrs[i - 1] + frac * (mrrs[i] - mrrs[i - 1]))
            break
    return dict(floor=floor, ceil=ceil, mid=mid, knee_mrr=knee_mrr)


# ---------------------------------------------------------------------------
# per-candidate array dump + off-disk recompute (v2 discipline)
# ---------------------------------------------------------------------------
def dump_and_verify_arrays(output_dir, arena_arrays, real_arrays):
    """Dump all per-candidate surprise arrays (arena-strong + real) + recompute real KEY-AUC off-disk."""
    batches, surprise, seeds_a = [], [], []
    for seed, ai in arena_arrays:  # arena STRONG point per seed
        for lbl, arr in ((B_INFER_ARENA, ai["_surp_infer"]), (B_NOVEL_ARENA, ai["_surp_novel"])):
            batches.append(np.full(arr.shape[0], lbl, dtype=np.int64)); surprise.append(arr.astype(np.float64))
            seeds_a.append(np.full(arr.shape[0], seed, dtype=np.int64))
    for seed, ri in real_arrays:
        for lbl, arr in ((B_INFER_REAL, ri["_surp_infer"]), (B_NOVEL_REAL, ri["_surp_novel"])):
            batches.append(np.full(arr.shape[0], lbl, dtype=np.int64)); surprise.append(arr.astype(np.float64))
            seeds_a.append(np.full(arr.shape[0], seed, dtype=np.int64))
    flat = dict(batch=np.concatenate(batches), surprise=np.concatenate(surprise), seed=np.concatenate(seeds_a))
    path = os.path.join(str(output_dir), "per_candidate_arrays.npz")
    tmp = os.path.join(str(output_dir), "per_candidate_arrays_tmp.npz")
    np.savez(tmp, **flat)
    os.replace(tmp, path)
    inmem = _auc(flat["surprise"][flat["batch"] == B_NOVEL_REAL], flat["surprise"][flat["batch"] == B_INFER_REAL])
    z = np.load(path)
    offdisk = _auc(z["surprise"][z["batch"] == B_NOVEL_REAL], z["surprise"][z["batch"] == B_INFER_REAL])
    delta = abs(float(inmem) - float(offdisk)) if (inmem == inmem and offdisk == offdisk) else 0.0
    ok = delta <= HP_ARRAY_RECOMPUTE_TOL
    return ok, delta, path


# ---------------------------------------------------------------------------
# aggregate + verdict
# ---------------------------------------------------------------------------
def aggregate_and_verdict(curve, knee, real_per_seed, posctrl_per_seed, run_mode, array_ok, array_delta,
                          expected_units, observed_units):
    real_mrr = _mean([r["real_mrr"] for r in real_per_seed])
    real_key_auc = _mean([r["real_key_auc"] for r in real_per_seed])
    posctrl_mrr = _mean([p["mrr"] for p in posctrl_per_seed])
    posctrl_key_auc = _mean([p["key_auc"] for p in posctrl_per_seed])
    floor = knee["floor"]; ceil = knee["ceil"]; mid = knee["mid"]; knee_mrr = knee["knee_mrr"]
    band = (ceil - floor) if (ceil == ceil and floor == floor) else float("nan")

    g = {}
    g["cardinality_ok"] = (observed_units == expected_units)
    g["HP_POSCTRL_FIRES"] = posctrl_key_auc >= HP_POSCTRL_KEY_AUC_MIN
    g["HP_POSCTRL_GENERALIZES"] = posctrl_mrr >= HP_POSCTRL_MRR_MIN
    g["HP_SWEEP_RISES"] = (band == band) and (band >= HP_SWEEP_RISE_MIN)
    g["baseline_in_band"] = (HP_REAL_MRR_LO < real_mrr < HP_REAL_MRR_HI)

    harness_valid = g["HP_POSCTRL_FIRES"] and g["HP_POSCTRL_GENERALIZES"] and g["HP_SWEEP_RISES"] and g["cardinality_ok"]

    # real position relative to the self-calibrated knee
    above_thresh = mid + KNEE_BAND_FRAC * band if band == band else float("nan")
    below_thresh = floor + BELOW_KNEE_FRAC * band if band == band else float("nan")
    real_above_knee = (real_key_auc >= above_thresh) and (real_key_auc >= HP_REAL_ABS_KEY_AUC_MIN)
    real_below_knee = (real_key_auc <= below_thresh)
    knee_side = ("ABOVE" if real_above_knee else ("BELOW" if real_below_knee else "STRADDLE"))
    mrr_side = ("above" if (knee_mrr == knee_mrr and real_mrr > knee_mrr) else
                ("below" if knee_mrr == knee_mrr else "n/a"))

    if not harness_valid:
        verdict = "INCONCLUSIVE_harness"
        finding = "INCONCLUSIVE: pos-control/sweep did not validate the harness (cannot distinguish real-collapse " \
                  "from broken test)"
    elif real_above_knee:
        verdict = "HARD_PASS"
        finding = "REAL_ABOVE_KNEE: surprise-as-novelty SURVIVES at real-CSKG strength (real KEY-AUC %.3f above " \
                  "knee-mid %.3f + pos-control fires) => the ingest-gate novelty criterion works in the REAL regime" \
                  % (real_key_auc, mid)
    elif real_below_knee:
        verdict = "MEASURED_BOUND_real_below_knee"
        finding = "REAL_BELOW_KNEE: surprise-as-novelty COLLAPSES to ~chance at real strength (real KEY-AUC %.3f " \
                  "near sweep floor %.3f while pos-control fires %.3f) => the novelty-gate REQUIRES scaling the " \
                  "foundation stronger first (BRAIN-CHECK: schema-strength-gated novelty signal)" \
                  % (real_key_auc, floor, posctrl_key_auc)
    else:
        verdict = "MIDDLE_BAND_near_knee"
        finding = "REAL_STRADDLES_KNEE: real KEY-AUC %.3f sits between floor %.3f and knee-mid %.3f (ambiguous; " \
                  "real ~0.13 is right at the knee)" % (real_key_auc, floor, mid)

    msg = ("KNEE: floor=%.3f ceil=%.3f mid=%.3f knee_mrr=%.4f | REAL: mrr=%.4f key_auc=%.3f (%s knee; mrr %s knee_mrr) "
           "| POSCTRL: mrr=%.3f key_auc=%.3f | harness_valid=%s arrays_ok=%s(d=%.1e) card=%s -> %s" % (
               floor, ceil, mid, knee_mrr, real_mrr, real_key_auc, knee_side, mrr_side, posctrl_mrr,
               posctrl_key_auc, harness_valid, array_ok, array_delta, g["cardinality_ok"], verdict))
    summary = "%s: %s" % (verdict, finding)
    return dict(verdict=verdict, verdict_msg=msg, summary=summary, finding=finding, gates=g, run_mode=run_mode,
                knee=dict(floor=floor, ceil=ceil, mid=mid, knee_mrr=knee_mrr, band=band,
                          above_thresh=above_thresh, below_thresh=below_thresh),
                real=dict(mrr=real_mrr, key_auc=real_key_auc, knee_side=knee_side, mrr_side=mrr_side),
                posctrl=dict(mrr=posctrl_mrr, key_auc=posctrl_key_auc),
                agg=dict(real_mrr=real_mrr, real_key_auc=real_key_auc, posctrl_mrr=posctrl_mrr,
                         posctrl_key_auc=posctrl_key_auc, knee_mrr=knee_mrr, knee_floor=floor, knee_ceil=ceil,
                         knee_mid=mid, array_recompute_delta=array_delta),
                sweep_curve=curve)


# ---------------------------------------------------------------------------
# self-test (REAL substrate code path at N~16 + arena_key_auc primitive; validity preflight)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    from experiments._kge_anchor1_fit import fit_kge_anchor1
    _log("self_test: constructing REAL AdditiveKGMap + arena_key_auc at tiny scale")
    exercised = set()
    device = torch.device("cpu")

    # REAL substrate object path (matches FULL: AdditiveKGMap.fit is what real_regime + fit_foundation call)
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

    # arena_key_auc primitive: a STRONG arena must separate novel from inferable > a DEAD arena (dose-response)
    acfg = _arena_cfg(ARENA_BASE, n_ent=40, edges_per_rel=24)
    dead = arena_key_auc(acfg, 7, 2, device)
    strong = arena_key_auc(acfg, 7, 120, device)
    exercised.add("arena_key_auc")
    assert strong["mrr"] >= dead["mrr"] - 1e-6, "strong arena MRR must be >= dead (dose-response): %s vs %s" % (
        strong["mrr"], dead["mrr"])
    assert dead["surp_infer_sha"] != strong["surp_infer_sha"], "dead vs strong surprise vectors bit-identical (arm bug)"

    # knee location on a synthetic monotone curve
    curve = [dict(epochs=e, mrr=m, key_auc=a) for e, m, a in
             [(2, 0.01, 0.60), (8, 0.05, 0.62), (20, 0.13, 0.75), (60, 0.30, 0.95), (200, 0.60, 0.97)]]
    kn = locate_knee(curve)
    assert kn["floor"] == 0.60 and kn["ceil"] == 0.97, "knee floor/ceil wrong: %s" % kn
    assert 0.05 <= kn["knee_mrr"] <= 0.35, "knee_mrr out of expected band: %s" % kn["knee_mrr"]

    # AUC direction sanity: novel(high surprise) vs inferable(low) -> > 0.5
    assert _auc([0.9, 0.95], [0.1, 0.2]) == 1.0 and _auc([0.1, 0.2], [0.9, 0.95]) == 0.0

    # r* picker is deterministic median-frequency
    tr = [("a", "r1", "b")] * 2 + [("a", "r2", "c")] * 5 + [("a", "r3", "d")] * 9
    rstar = _pick_rstar(tr, 1)
    assert rstar == "r2", "r* median-frequency pick wrong: %s" % rstar

    # array dump + off-disk recompute round-trip
    import tempfile
    fake_arena = [(7, dict(_surp_infer=np.array([0.1, 0.2]), _surp_novel=np.array([0.9, 0.95])))]
    fake_real = [(7, dict(_surp_infer=np.array([0.1, 0.15, 0.2]), _surp_novel=np.array([0.8, 0.9, 0.95])))]
    with tempfile.TemporaryDirectory() as td:
        ok, delta, _p = dump_and_verify_arrays(td, fake_arena, fake_real)
        assert ok and delta <= HP_ARRAY_RECOMPUTE_TOL, "array recompute mismatch delta=%s" % delta

    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.fit", "AdditiveKGMap.score_all",
                                        "AdditiveKGMap.compose_entity", "AdditiveKGMap.insert_entity",
                                        "arena_key_auc"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": AdditiveKGMap, "callable_name": "AdditiveKGMap",
         "kwargs": {"device": "cpu"}},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": device, "seed": 7, "epochs": 1}},
        {"kind": "metric_moves", "metric_name": "key_auc", "before": 0.60, "after": 0.95, "min_delta": 1e-6},
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
    n_epoch_pts = len(cfg["sweep_epochs"])
    expected_units = len(seeds) * (n_epoch_pts + 2)   # sweep points + real + pos-control per seed
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()
    device = torch.device("cpu")   # CPU: small-N AdditiveKGMap fits; brute-force arena NN is numpy

    sweep_per_seed = []
    arena_strong_arrays = []
    posctrl_per_seed = []
    real_per_seed = []
    real_arrays = []
    observed_units = 0

    sweep_cfg = _arena_cfg(ARENA_BASE, cfg["sweep_n_ent"], cfg["sweep_edges_per_rel"])
    posctrl_cfg = _arena_cfg(ARENA_BASE, cfg["posctrl_n_ent"], cfg["posctrl_edges_per_rel"])

    for si, seed in enumerate(seeds):
        _log("seed %d/%d (seed=%d): PART 1 knee sweep over %d epoch points ..." % (
            si + 1, len(seeds), seed, n_epoch_pts))
        pts = []
        for ei, ep in enumerate(cfg["sweep_epochs"]):
            want = (ep == cfg["sweep_epochs"][-1])   # keep arrays for the strongest point (dump)
            p = arena_key_auc(sweep_cfg, seed, ep, device, want_arrays=want)
            pts.append({kk: p[kk] for kk in ("epochs", "mrr", "key_auc", "n_infer", "n_novel",
                                             "surp_infer_sha", "surp_novel_sha")})
            observed_units += 1
            if want:
                arena_strong_arrays.append((seed, p))
            _log("  [sweep] seed=%d ep=%d mrr=%.4f key_auc=%.3f (%.1fs)" % (
                seed, ep, p["mrr"], p["key_auc"], time.time() - t0))
        sweep_per_seed.append(pts)

        _log("seed=%d: PART 2 pos-control (matched-scale synthetic-strong N=%d, %d ep) ..." % (
            seed, cfg["posctrl_n_ent"], cfg["posctrl_epochs"]))
        pc = arena_key_auc(posctrl_cfg, seed, cfg["posctrl_epochs"], device)
        posctrl_per_seed.append({kk: pc[kk] for kk in ("epochs", "mrr", "key_auc", "n_infer", "n_novel")})
        observed_units += 1
        _log("  [posctrl] seed=%d mrr=%.4f key_auc=%.3f (%.1fs)" % (seed, pc["mrr"], pc["key_auc"], time.time() - t0))

        _log("seed=%d: PART 2 REAL CSKG foundation (k_core=%d max_nodes=%d ep=%d) ..." % (
            seed, cfg["real_k_core"], cfg["real_max_nodes"], cfg["real_epochs"]))
        rr = real_regime(cfg, seed, device, cache_dir, want_arrays=True)
        real_arrays.append((seed, rr))
        real_per_seed.append({kk: rr[kk] for kk in ("seed", "rstar", "N", "n_found", "n_rstar", "n_infer",
                                                    "real_mrr", "real_key_auc", "surp_infer_sha", "surp_novel_sha")})
        observed_units += 1
        _log("  [real] seed=%d rstar=%s N=%d mrr=%.4f key_auc=%.3f (%.1fs)" % (
            seed, rr["rstar"], rr["N"], rr["real_mrr"], rr["real_key_auc"], time.time() - t0))

    # ARMS-MUST-DIFFER: sweep dead vs strong surprise distinct; real vs pos-control distinct (META_RULE_AF)
    dead_sha = sweep_per_seed[0][0]["surp_infer_sha"]
    strong_sha = sweep_per_seed[0][-1]["surp_infer_sha"]
    real_sha = real_per_seed[0]["surp_novel_sha"]
    assert len({dead_sha, strong_sha, real_sha}) == 3, "surprise vectors bit-identical across arms (arm bug)"

    curve = aggregate_sweep(sweep_per_seed)
    knee = locate_knee(curve)
    array_ok, array_delta, array_path = dump_and_verify_arrays(output_dir, arena_strong_arrays, real_arrays)
    _log("per-candidate arrays -> %s (recompute_ok=%s delta=%.2e)" % (array_path, array_ok, array_delta))

    v = aggregate_and_verdict(curve, knee, real_per_seed, posctrl_per_seed, run_mode, array_ok, array_delta,
                              expected_units, observed_units)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(seeds),
                   config=dict(seeds=seeds, sweep_epochs=cfg["sweep_epochs"], sweep_n_ent=cfg["sweep_n_ent"],
                               real_k_core=cfg["real_k_core"], real_max_nodes=cfg["real_max_nodes"],
                               real_epochs=cfg["real_epochs"], posctrl_n_ent=cfg["posctrl_n_ent"],
                               posctrl_epochs=cfg["posctrl_epochs"], rel_scale=ARENA_BASE["rel_scale"]),
                   bands=dict(HP_POSCTRL_KEY_AUC_MIN=HP_POSCTRL_KEY_AUC_MIN, HP_SWEEP_RISE_MIN=HP_SWEEP_RISE_MIN,
                              HP_REAL_ABS_KEY_AUC_MIN=HP_REAL_ABS_KEY_AUC_MIN, HP_POSCTRL_MRR_MIN=HP_POSCTRL_MRR_MIN,
                              KNEE_BAND_FRAC=KNEE_BAND_FRAC, BELOW_KNEE_FRAC=BELOW_KNEE_FRAC),
                   expected_n_units=expected_units, observed_n_units=observed_units,
                   arms_differ_verified=True, final_metrics_atomicity="tmp_replace",
                   progress_logging="print_flush_true",
                   per_candidate_arrays=os.path.basename(array_path),
                   **v, sweep_per_seed=sweep_per_seed, real_per_seed=real_per_seed,
                   posctrl_per_seed=posctrl_per_seed)
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
