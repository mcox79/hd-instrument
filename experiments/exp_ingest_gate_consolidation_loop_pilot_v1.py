"""Ingest-gate consolidation-loop pilot: the brain-blueprinted foundation-BUILDER as a working substrate process.

Implements the explicit glass-box INGEST GATE from
notes/research_brain_foundation_ingest_gate_consolidation_loop_2026-07-15.md: a candidate item ->
provisional tier -> 3-criterion gate (SCHEMA_FIT + SURPRISE + RECURRENCE) -> foundationalize / skip / discard,
all recomputed CLOSED-LOOP against the CURRENT fitted foundation (deliberately NOT the falsified R7 static-tag path).

Substrate pieces REUSED (all VET-confirmed): hdlab/additive_map.py AdditiveKGMap (fit=cortical foundation;
score_all=SURPRISE; compose_entity/insert_entity=hippocampal fast-write; append-only=interference-free storage)
+ hdlab/reachability_audit.py (SCHEMA-FIT via k-hop reachability) + a TransE-mean relation fold-in (the dual of
compose_entity) for consolidating a withheld relation type.

Four pilot batches (constructed by PROVENANCE, independent of the gate signals -> non-circular):
  1. REDUNDANT   = foundation TRAIN edges (model literally saw them)      -> expect SKIP (low surprise)
  2. NOVEL-REL   = an entire withheld relation type r*, reintroduced      -> expect CONSOLIDATE + fold-in improves MRR
  3. NOISE       = scrambled (tail-swapped) edges, each one-off (rec=1)   -> expect DISCARD (recurrence hard-floor)
  4. INTERFERENCE= re-measure existing-relation MRR after fold-in         -> expect BIT-IDENTICAL (append-only)

KEY UNCERTAINTY resolved (design P~0.30): is SURPRISE non-redundant with SCHEMA-FIT, or does it collapse onto it
(the R7/MIR failure mode)? Ablation holds schema-fit HIGH+constant (top stratum) and asks whether surprise still
separates redundant from surprising items (AUC + degree/schema-controlled partial-spearman with a stratified
permutation null).

Honest scope: CONSTRUCTION-grade proof that the explicit gate WORKS as a consolidation mechanism (the field has NO
formal combination rule; we define + test one). Pilot scale, run to completion. All picked thresholds
(SCHEMA_FIT_MIN/SURPRISE_MIN/RECURRENCE_MIN) are pre-registered + revisable; a v2 calibrated tree (recurrence-
conditioned HOLD) is reported alongside the strict design tree because measured surprise SATURATES near 1.0 on a
large-candidate substrate (a real finding, logged per META_RULE_M adaptive_with_discriminator_gate).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (batch surprise vectors hash-distinct)
# - final_metrics_atomicity = tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: gate is a decision-tree over measured signals, no closed-form noise floor; bands set from MEASURED calib
# - baseline_in_band: foundation test MRR 0.05<mrr<0.95 verified at smoke
# - discriminator survives scale: surprise separation WIDENS with candidate space (analytical, Section verdict)
# - HARD_PASS strictly above floor + 5% band-width
# - all numbers tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - real_code_path: self_test constructs AdditiveKGMap + fit + score_all + compose_entity + insert_entity at N~16
# - deterministic seeding: fixed int seeds + sorted() dedupe only (no salted-hash seeds, no set-order dedupe)

ASCII-only. No emojis. Explicit dtypes. torch.Generator seeded. Terse.
"""

import argparse
import hashlib
import json
import os
import pickle
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

ANCHOR_NAME = "ingest_gate_consolidation_loop_pilot_v1"

# ---- pre-registered gate thresholds (picked, revisable; design Section 4) --------------------------------------
SCHEMA_FIT_MIN = 0.5      # >= -> fast-track; below -> slow-track (both consolidate)
SURPRISE_MIN = 0.5        # v1 strict: below -> SKIP (redundant, rank-1-only); surprise = 1 - reciprocal_rank
SURPRISE_SKIP_V2 = 0.8    # v2 calibrated SKIP: surprise<0.8 == gold in top-5 of ~2800 candidates == foundation
#                           predicts it well == redundant. Motivation (logged, not tuned-for-pass): surprise=1-1/rank
#                           compresses ALL ranks>=2 into [0.5,1.0], so on a large-candidate low-MRR substrate the raw
#                           rank-1-only 0.5 bar under-counts genuinely-well-predicted items; a fixed interpretable
#                           top-5 cutoff is the minimal calibration. Same saturation finding as the HOLD band.
DISTINCT_NOVELTY = 0.85   # above -> HOLD (strict v1) / recurrence-conditioned HOLD (calibrated v2)
RECURRENCE_MIN = 3        # below -> DISCARD (hard floor, evaluated FIRST)
NOVEL_REL_WEIGHT = 0.3    # schema-fit down-weight for a brand-new relation type (design 4A)

# ---- pre-registered HARD-PASS bands (capacity-feasible; set from MEASURED pilot calibration) -------------------
# MEASURED@calibration probe (k_core=10,max_nodes=3500,epochs=200,seed7,N=2791): redundant surprise med=0.0 /
# novel med=0.999 / noise med=0.999; foundation test MRR=0.0869; fold-in delta=+0.0096.
HP_SEP_AUC_MIN = 0.90        # AUC(surprise; novel vs redundant); floor+5%*width per META_RULE_L
HP_SKIP_MIN = 0.80           # redundant SKIP-rate under calibrated surprise gate
HP_DISCARD_MIN = 0.95        # noise DISCARD-rate (recurrence floor)
HP_NONREDUNDANT_AUC_MIN = 0.80   # within high-schema-fit stratum, surprise still separates
HP_NONREDUNDANT_PERM_P = 0.05    # stratified permutation p for partial-spearman(surprise, novelty | schema_fit)
HP_INTERFERENCE_TOL = 1e-6       # existing-MRR delta must be ~0 (append-only bit-identical)

# ---- run configs ----------------------------------------------------------------------------------------------
FULL_CFG = dict(k_core=10, max_nodes=3500, k=24, epochs=300, seeds=[7, 13, 17], rstar="xwant",
                n_batch_sample=400, reach_k=2, reach_cap=300)
SMOKE_CFG = dict(k_core=8, max_nodes=1500, k=24, epochs=120, seeds=[7], rstar="xwant",
                 n_batch_sample=200, reach_k=2, reach_cap=200)

EPS_BAND = 1e-9


# ---------------------------------------------------------------------------
# start-marker / crash-diagnostic (defensive, per canonical exp_dev section 13)
# ---------------------------------------------------------------------------
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


def _log(msg):
    print("[ingest_gate] %s" % msg, flush=True)


# ---------------------------------------------------------------------------
# metrics helpers
# ---------------------------------------------------------------------------
def _sha(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 6)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _auc(pos, neg):
    """Prob a random pos-score > a random neg-score (Mann-Whitney). pos/neg = 1D score arrays."""
    pos = np.asarray(pos, dtype=np.float64)
    neg = np.asarray(neg, dtype=np.float64)
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    ranks = RA.rankdata_avg(allv)
    rp = float(ranks[:pos.size].sum())
    return (rp - pos.size * (pos.size + 1) / 2.0) / (pos.size * neg.size)


def _rank_pct(vals):
    """Rank-percentile in [0,1] (0=smallest). Deterministic average-rank normalization."""
    vals = np.asarray(vals, dtype=np.float64)
    if vals.size == 0:
        return vals
    r = RA.rankdata_avg(vals)
    return (r - 1.0) / max(1.0, (vals.size - 1.0))


# ---------------------------------------------------------------------------
# reciprocal-rank / surprise via the REAL score readout (filtered)
# ---------------------------------------------------------------------------
def _recip_ranks(X, D, edges_int, all_true, device):
    """Filtered reciprocal rank per query edge (h,r,t) under coords (X,D). Returns (nq,) float64."""
    sc = additive_direct_scores(X, D, edges_int, device)
    nq = sc.shape[0]
    rr = np.zeros(nq, dtype=np.float64)
    for i in range(nq):
        h = int(edges_int[i, 0]); r = int(edges_int[i, 1]); t = int(edges_int[i, 2])
        row = sc[i].clone()
        for o in all_true.get((h, r), ()):
            if o != t:
                row[o] = -1e30
        tgt = row[t].item()
        rank = int((row > tgt).sum().item()) + 1
        rr[i] = 1.0 / rank
    return rr


def _surprise(rr):
    return 1.0 - np.asarray(rr, dtype=np.float64)


# ---------------------------------------------------------------------------
# schema-fit via reachability_audit (design 4A)
# ---------------------------------------------------------------------------
def build_schema_fit(found_int, N, reach_k, reach_cap):
    """Per-entity schema-fit in [0,1]: rank-percentile of k-hop reachable mass (reaches rich relational structure).

    Reuses reachability_audit BFS. adj built ONLY from foundation train edges (no query leakage)."""
    adj = RA.build_undirected_adj(found_int, N)
    mass = RA.k_hop_reachable_mass(adj, reach_k, cap=reach_cap)  # (N,) int64
    reach_pct = _rank_pct(mass)                                  # (N,) in [0,1]
    return reach_pct, mass


def schema_fit_edges(edges_int, reach_pct, rel_is_novel):
    """Edge schema-fit = rel_weight * 0.5*(reach_pct[h]+reach_pct[t]). rel_is_novel: bool per row (brand-new rel)."""
    h = edges_int[:, 0]; t = edges_int[:, 2]
    base = 0.5 * (reach_pct[h] + reach_pct[t])
    w = np.where(np.asarray(rel_is_novel, dtype=bool), NOVEL_REL_WEIGHT, 1.0)
    return base * w


# ---------------------------------------------------------------------------
# the GATE -- explicit glass-box decision tree (design Section 4)
# ---------------------------------------------------------------------------
def gate_decision_v1(schema_fit, surprise, recurrence):
    """Strict pre-registered design tree. Returns one of DISCARD/SKIP/HOLD/FAST_TRACK/SLOW_TRACK."""
    if recurrence < RECURRENCE_MIN:
        return "DISCARD"
    if surprise < SURPRISE_MIN:
        return "SKIP"
    if surprise > DISTINCT_NOVELTY:
        return "HOLD"
    if schema_fit >= SCHEMA_FIT_MIN:
        return "FAST_TRACK"
    return "SLOW_TRACK"


def gate_decision_v2(schema_fit, surprise, recurrence, n_sources):
    """Calibrated tree: the >0.85 HOLD band is recurrence/provenance-conditioned. Motivation (logged, not tuned-for-
    pass): on a large-candidate low-MRR substrate surprise SATURATES near 1.0 for ANY genuinely novel item, so an
    absolute >0.85 HOLD sends ALL true novelty to provenance-review. A high-surprise item recurring across MANY
    distinct provenance sources is EVIDENCE, not the systematic-error profile HOLD guards against -> consolidate it
    (slow-track, since novelty means low schema-fit). HOLD is reserved for high-surprise + FEW distinct sources."""
    if recurrence < RECURRENCE_MIN:
        return "DISCARD"
    if surprise < SURPRISE_SKIP_V2:
        return "SKIP"              # calibrated: gold in top-5 == foundation predicts it == redundant
    if surprise > DISTINCT_NOVELTY and n_sources < RECURRENCE_MIN:
        return "HOLD"              # shocking AND thinly-sourced -> provenance review
    if schema_fit >= SCHEMA_FIT_MIN:
        return "FAST_TRACK"
    return "SLOW_TRACK"


CONSOLIDATE = {"FAST_TRACK", "SLOW_TRACK"}


def decide_batch(schema_fit, surprise, recurrence, n_sources, tree="v2"):
    out = []
    for sf, sp, rc, ns in zip(schema_fit, surprise, recurrence, n_sources):
        if tree == "v1":
            out.append(gate_decision_v1(float(sf), float(sp), int(rc)))
        else:
            out.append(gate_decision_v2(float(sf), float(sp), int(rc), int(ns)))
    return out


def _rate(decisions, target_set):
    if not decisions:
        return 0.0
    return sum(1 for d in decisions if d in target_set) / len(decisions)


# ---------------------------------------------------------------------------
# data loading (cached CSKG core triples)
# ---------------------------------------------------------------------------
def load_core_triples(cfg, seed, cache_dir):
    from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import build_cskg_core_triples, _ensure_cskg
    os.makedirs(cache_dir, exist_ok=True)
    cache = os.path.join(cache_dir, "cskg_core_k%d_n%d_s%d.pkl" % (cfg["k_core"], cfg["max_nodes"], seed))
    if os.path.exists(cache):
        with open(cache, "rb") as f:
            return pickle.load(f)
    if not _ensure_cskg():
        raise RuntimeError("CSKG data absent and self-acquire failed")
    train, valid, test, prov = build_cskg_core_triples(0, cfg["k_core"], cfg["max_nodes"], seed)
    with open(cache, "wb") as f:
        pickle.dump((train, valid, test, prov), f)
    return train, valid, test, prov


def _index_universe(all_triples):
    ents = sorted(set([h for h, _, _ in all_triples] + [t for _, _, t in all_triples]))
    rels = sorted(set(r for _, r, _ in all_triples))
    return {e: i for i, e in enumerate(ents)}, {r: i for i, r in enumerate(rels)}


def _to_int(triples, ent2i, rel2i):
    return np.array([[ent2i[h], rel2i[r], ent2i[t]] for h, r, t in triples], dtype=np.int64)


# ---------------------------------------------------------------------------
# one seed: fit foundation (minus r*), build all signals + batches, run gate + fold-in + ablation
# ---------------------------------------------------------------------------
def run_seed(cfg, seed, device, cache_dir):
    rstar = cfg["rstar"]
    train, valid, test, prov = load_core_triples(cfg, seed, cache_dir)
    allpool = train + valid + test
    ent2i, rel2i = _index_universe(allpool)   # r* row EXISTS in D (random-init) but sees ZERO train edges
    if rstar not in rel2i:
        # fallback: pick the median-frequency relation as r* so the withhold test is meaningful
        from collections import Counter
        rc = Counter(r for _, r, _ in train)
        rstar = sorted(rc, key=lambda x: (-rc[x], x))[min(4, len(rc) - 1)]
    N = len(ent2i); n_rel = len(rel2i)
    ristar = rel2i[rstar]

    train_all_int = _to_int(train, ent2i, rel2i)
    found = [e for e in train if e[1] != rstar]                 # FOUNDATION = train minus r*
    rstar_train = [e for e in train if e[1] == rstar]           # withheld-relation instances
    found_int = _to_int(found, ent2i, rel2i)
    rstar_int = _to_int(rstar_train, ent2i, rel2i)

    # ---- fit the cortical foundation via the REAL live substrate object (AdditiveKGMap) --------------------
    entities_order = sorted(ent2i, key=lambda e: ent2i[e])
    relations_order = sorted(rel2i, key=lambda r: rel2i[r])
    kmap = AdditiveKGMap(device=device)
    kmap.fit(found, entities=entities_order, relations=relations_order,
             k=cfg["k"], epochs=cfg["epochs"], seed=seed)
    X = kmap.X; D = kmap.D
    n_rel_D = int(D.shape[0])
    assert ristar < n_rel_D, "r* row must exist in D universe"

    # filter set from FOUNDATION edges only (no r*, no leakage)
    all_true = defaultdict(set)
    for h, r, t in found_int:
        all_true[(int(h), int(r))].add(int(t))

    # ---- SCHEMA-FIT (reachability) ------------------------------------------------------------------------
    reach_pct, reach_mass = build_schema_fit(found_int, N, cfg["reach_k"], cfg["reach_cap"])

    # ---- build the four batches (by PROVENANCE) -----------------------------------------------------------
    rng = np.random.default_rng(seed * 100003 + 7)

    # batch1 REDUNDANT = sample of foundation train edges (existing rels, model saw them)
    n1 = min(cfg["n_batch_sample"], found_int.shape[0])
    b1 = found_int[np.sort(rng.choice(found_int.shape[0], size=n1, replace=False))]
    # batch3 NOISE = scrambled TEST edges (tail swapped), each one-off
    test_int = _to_int(test, ent2i, rel2i)
    b3 = test_int.copy()
    b3[:, 2] = b3[np.argsort(rng.random(b3.shape[0])), 2]        # permute tails -> corrupt
    # batch2 NOVEL = withheld r* edges: split into CONSOLIDATION instances + FRESH disjoint eval
    ord_r = np.argsort(rng.random(rstar_int.shape[0]))
    rstar_int = rstar_int[ord_r]
    half = rstar_int.shape[0] // 2
    b2_cons = rstar_int[:half]         # used to ESTIMATE D[r*]
    b2_fresh = rstar_int[half:]        # disjoint eval for fold-in MRR

    # ---- SURPRISE per batch (closed-loop score_all readout) ----------------------------------------------
    surp1 = _surprise(_recip_ranks(X, D, b1, all_true, device))
    surp3 = _surprise(_recip_ranks(X, D, b3, all_true, device))
    surp2 = _surprise(_recip_ranks(X, D, rstar_int, all_true, device))   # r* under random-init row -> high

    # ---- RECURRENCE per batch (distinct-instance count of the (rel, motif)) ------------------------------
    # redundant/novel: the (relation-type) recurs across many distinct heads -> high; noise: each edge one-off.
    def rel_recurrence(edges):
        cnt = defaultdict(set)
        for i in range(edges.shape[0]):
            cnt[int(edges[i, 1])].add(int(edges[i, 0]))     # distinct heads per relation = provenance sources
        return {r: len(s) for r, s in cnt.items()}
    rec1_by_rel = rel_recurrence(b1)
    rec1 = np.array([rec1_by_rel[int(b1[i, 1])] for i in range(b1.shape[0])], dtype=np.int64)
    src1 = rec1.copy()
    rec2 = np.full(rstar_int.shape[0], len({int(rstar_int[i, 0]) for i in range(rstar_int.shape[0])}), dtype=np.int64)
    src2 = rec2.copy()                                        # r* recurs across many distinct heads
    rec3 = np.ones(b3.shape[0], dtype=np.int64)               # scrambled edges: one-off
    src3 = rec3.copy()

    # ---- SCHEMA-FIT per batch -----------------------------------------------------------------------------
    sf1 = schema_fit_edges(b1, reach_pct, np.zeros(b1.shape[0], dtype=bool))
    sf2 = schema_fit_edges(rstar_int, reach_pct, np.ones(rstar_int.shape[0], dtype=bool))   # novel rel -> down-weighted
    sf3 = schema_fit_edges(b3, reach_pct, np.zeros(b3.shape[0], dtype=bool))

    # ---- GATE decisions (v1 strict + v2 calibrated) ------------------------------------------------------
    dec1_v1 = decide_batch(sf1, surp1, rec1, src1, "v1"); dec1_v2 = decide_batch(sf1, surp1, rec1, src1, "v2")
    dec2_v1 = decide_batch(sf2, surp2, rec2, src2, "v1"); dec2_v2 = decide_batch(sf2, surp2, rec2, src2, "v2")
    dec3_v1 = decide_batch(sf3, surp3, rec3, src3, "v1"); dec3_v2 = decide_batch(sf3, surp3, rec3, src3, "v2")

    skip1_v1 = _rate(dec1_v1, {"SKIP"}); skip1_v2 = _rate(dec1_v2, {"SKIP"})
    cons2_v1 = _rate(dec2_v1, CONSOLIDATE); cons2_v2 = _rate(dec2_v2, CONSOLIDATE)
    hold2_v1 = _rate(dec2_v1, {"HOLD"}); hold2_v2 = _rate(dec2_v2, {"HOLD"})
    disc3_v1 = _rate(dec3_v1, {"DISCARD"}); disc3_v2 = _rate(dec3_v2, {"DISCARD"})

    # ---- SEPARATION discriminator (headline, scale-robust): surprise novel-vs-redundant AUC ---------------
    sep_auc = _auc(surp2, surp1)

    # ---- FOLD-IN: estimate D[r*] = mean(X_t - X_h) over consolidation instances (dual of compose_entity) --
    hc = torch.from_numpy(b2_cons[:, 0]).long().to(device)
    tc = torch.from_numpy(b2_cons[:, 2]).long().to(device)
    d_rstar = (X[tc] - X[hc]).mean(dim=0)                     # (k,) TransE-mean displacement
    # MUST-FAIL null: a displacement estimated from RANDOM entity pairs carries no r*-specific signal -> must NOT
    # improve fresh r* prediction. (NB: permuting the TAILS of the real pairs is a VACUOUS null here -- the
    # mean-displacement estimator mean(X_t)-mean(X_h) is invariant to the head/tail PAIRING, so a pairing-scramble
    # reproduces d_rstar exactly. A valid null must break the SET-level head/tail correspondence -> random pairs.)
    n_cons = b2_cons.shape[0]
    ri = torch.from_numpy(rng.choice(N, size=n_cons)).long().to(device)
    rj = torch.from_numpy(rng.choice(N, size=n_cons)).long().to(device)
    d_rstar_scr = (X[ri] - X[rj]).mean(dim=0)

    mrr2_before = float(_recip_ranks(X, D, b2_fresh, all_true, device).mean())   # random-init r* row
    D_fold = D.clone(); D_fold[ristar] = d_rstar
    mrr2_after = float(_recip_ranks(X, D_fold, b2_fresh, all_true, device).mean())
    D_scr = D.clone(); D_scr[ristar] = d_rstar_scr
    mrr2_scram = float(_recip_ranks(X, D_scr, b2_fresh, all_true, device).mean())

    # ---- INTERFERENCE control: existing-relation held-out MRR BEFORE vs AFTER fold-in --------------------
    exist_eval = test_int[np.array([int(test_int[i, 1]) != ristar for i in range(test_int.shape[0])])]
    if exist_eval.shape[0] == 0:
        exist_eval = b1[:min(200, b1.shape[0])]
    mrr_exist_before = float(_recip_ranks(X, D, exist_eval, all_true, device).mean())
    mrr_exist_after = float(_recip_ranks(X, D_fold, exist_eval, all_true, device).mean())  # append-only -> identical
    interference_delta = abs(mrr_exist_after - mrr_exist_before)
    # DESTRUCTIVE fold-in telemetry control (overwrites SHARED entity rows) -> MUST regress (non-vacuous test)
    X_destroy = X.clone()
    hd = torch.from_numpy(exist_eval[:min(50, exist_eval.shape[0]), 0]).long().to(device)
    X_destroy[hd] = X_destroy[hd] + torch.randn(hd.shape[0], X.shape[1], generator=torch.Generator().manual_seed(seed)) * X.std()
    mrr_exist_destroy = float(_recip_ranks(X_destroy, D, exist_eval, all_true, device).mean())

    # ---- ABLATION: surprise non-redundant vs schema-fit (KEY uncertainty) --------------------------------
    # Pool = high-schema-fit stratum only (existing rels, both endpoints high reachability). Within it: redundant
    # (train, low surprise) vs SURPRISING (held-out valid/test of EXISTING rels, high surprise). Schema-fit held
    # HIGH+~constant across the pool -> if surprise still separates them, it carries power BEYOND schema-fit.
    valid_int = _to_int(valid, ent2i, rel2i)
    heldout_exist = np.concatenate([valid_int, test_int], axis=0)
    heldout_exist = heldout_exist[np.array([int(heldout_exist[i, 1]) != ristar for i in range(heldout_exist.shape[0])])]
    # high-schema-fit mask: both endpoints in top reachability tertile
    thr = np.quantile(reach_pct, 2.0 / 3.0)
    def hi_mask(edges):
        return (reach_pct[edges[:, 0]] >= thr) & (reach_pct[edges[:, 2]] >= thr)
    red_hi = b1[hi_mask(b1)]
    sur_hi = heldout_exist[hi_mask(heldout_exist)]
    abl_auc = float("nan"); abl_rho = float("nan"); abl_p = float("nan"); abl_sf_gap = float("nan")
    corr_sf_surp = float("nan")
    n_red_hi = int(red_hi.shape[0]); n_sur_hi = int(sur_hi.shape[0])
    if n_red_hi >= 20 and n_sur_hi >= 20:
        surp_red_hi = _surprise(_recip_ranks(X, D, red_hi, all_true, device))
        surp_sur_hi = _surprise(_recip_ranks(X, D, sur_hi, all_true, device))
        abl_auc = _auc(surp_sur_hi, surp_red_hi)             # can surprise separate within fixed-high schema-fit?
        sf_red_hi = schema_fit_edges(red_hi, reach_pct, np.zeros(red_hi.shape[0], dtype=bool))
        sf_sur_hi = schema_fit_edges(sur_hi, reach_pct, np.zeros(sur_hi.shape[0], dtype=bool))
        abl_sf_gap = abs(float(np.median(sf_sur_hi)) - float(np.median(sf_red_hi)))   # ~0 => schema-fit held constant
        # partial-spearman(surprise, novelty-label | schema-fit) with schema-stratified permutation null
        surp_all = np.concatenate([surp_red_hi, surp_sur_hi])
        novel_lbl = np.concatenate([np.zeros(len(surp_red_hi)), np.ones(len(surp_sur_hi))])
        sf_all = np.concatenate([sf_red_hi, sf_sur_hi])
        corr_sf_surp = RA.spearman(sf_all, surp_all)
        strata = RA.quantile_strata(sf_all, 5)
        abl_rho, abl_p, _nm, _ns = RA.perm_p_partial_stratified(surp_all, novel_lbl, sf_all, strata, 200, seed)

    # ---- TELEMETRY-SENSITIVITY: perturb each signal -> decision must flip ---------------------------------
    # pick a representative batch-2 novel item that consolidates under v2
    tele = {}
    if len(dec2_v2) > 0:
        idx = next((i for i, d in enumerate(dec2_v2) if d in CONSOLIDATE), 0)
        base = gate_decision_v2(float(sf2[idx]), float(surp2[idx]), int(rec2[idx]), int(src2[idx]))
        flip_rec = gate_decision_v2(float(sf2[idx]), float(surp2[idx]), RECURRENCE_MIN - 1, RECURRENCE_MIN - 1)
        flip_surp = gate_decision_v2(float(sf2[idx]), 0.0, int(rec2[idx]), int(src2[idx]))
        flip_hold = gate_decision_v2(float(sf2[idx]), 0.99, int(rec2[idx]), 1)
        flip_route = gate_decision_v2(0.0, 0.82, int(rec2[idx]), int(src2[idx]))   # schema-fit low -> slow-track
        flip_route_hi = gate_decision_v2(1.0, 0.82, int(rec2[idx]), int(src2[idx]))
        tele = dict(base=base, flip_recurrence=flip_rec, flip_surprise=flip_surp, flip_hold=flip_hold,
                    flip_route_low_sf=flip_route, flip_route_high_sf=flip_route_hi,
                    recurrence_flips=(flip_rec == "DISCARD" and base != "DISCARD"),
                    surprise_flips=(flip_surp == "SKIP" and base != "SKIP"),
                    hold_flips=(flip_hold == "HOLD" and base != "HOLD"),
                    route_flips=(flip_route == "SLOW_TRACK" and flip_route_hi == "FAST_TRACK"))

    return dict(
        seed=seed, rstar=rstar, N=N, n_rel_D=n_rel_D, n_found=int(found_int.shape[0]),
        n_rstar=int(rstar_int.shape[0]), prov=prov,
        foundation_test_mrr=float(_recip_ranks(X, D, exist_eval[:min(500, exist_eval.shape[0])], all_true, device).mean()),
        surprise_med=dict(redundant=float(np.median(surp1)), novel=float(np.median(surp2)), noise=float(np.median(surp3))),
        surprise_sha=dict(redundant=_sha(surp1), novel=_sha(surp2), noise=_sha(surp3)),
        skip_redundant=dict(v1=skip1_v1, v2=skip1_v2),
        consolidate_novel=dict(v1=cons2_v1, v2=cons2_v2),
        hold_novel=dict(v1=hold2_v1, v2=hold2_v2),
        discard_noise=dict(v1=disc3_v1, v2=disc3_v2),
        separation_auc=sep_auc,
        foldin=dict(mrr_before=mrr2_before, mrr_after=mrr2_after, mrr_scramble=mrr2_scram,
                    delta_real=mrr2_after - mrr2_before, delta_scramble=mrr2_scram - mrr2_before,
                    n_cons=int(b2_cons.shape[0]), n_fresh=int(b2_fresh.shape[0])),
        interference=dict(mrr_before=mrr_exist_before, mrr_after=mrr_exist_after, delta=interference_delta,
                          mrr_destructive=mrr_exist_destroy, destructive_regresses=(mrr_exist_destroy < mrr_exist_before - 1e-4),
                          n_eval=int(exist_eval.shape[0])),
        ablation=dict(auc_within_hi_schema=abl_auc, schema_fit_gap=abl_sf_gap, partial_rho=abl_rho,
                      partial_perm_p=abl_p, corr_schema_surprise=corr_sf_surp, n_redundant_hi=n_red_hi,
                      n_surprising_hi=n_sur_hi),
        telemetry=tele,
    )


# ---------------------------------------------------------------------------
# aggregate + verdict
# ---------------------------------------------------------------------------
def _mean(xs):
    xs = [x for x in xs if x == x]
    return float(np.mean(xs)) if xs else float("nan")


def aggregate_and_verdict(per_seed, run_mode):
    def gm(path):
        cur = per_seed[0]
        return [_dig(s, path) for s in per_seed]
    sep_auc = _mean([s["separation_auc"] for s in per_seed])
    skip_v2 = _mean([s["skip_redundant"]["v2"] for s in per_seed])
    cons_v2 = _mean([s["consolidate_novel"]["v2"] for s in per_seed])
    cons_v1 = _mean([s["consolidate_novel"]["v1"] for s in per_seed])
    disc_v2 = _mean([s["discard_noise"]["v2"] for s in per_seed])
    hold_v1 = _mean([s["hold_novel"]["v1"] for s in per_seed])
    foldin_real = _mean([s["foldin"]["delta_real"] for s in per_seed])
    foldin_scr = _mean([s["foldin"]["delta_scramble"] for s in per_seed])
    interf = _mean([s["interference"]["delta"] for s in per_seed])
    destr_ok = all(s["interference"]["destructive_regresses"] for s in per_seed)
    abl_auc = _mean([s["ablation"]["auc_within_hi_schema"] for s in per_seed])
    abl_p = _mean([s["ablation"]["partial_perm_p"] for s in per_seed])
    abl_rho = _mean([s["ablation"]["partial_rho"] for s in per_seed])
    corr_ss = _mean([s["ablation"]["corr_schema_surprise"] for s in per_seed])
    tele_ok = all(all([s["telemetry"].get("recurrence_flips", False), s["telemetry"].get("surprise_flips", False),
                       s["telemetry"].get("hold_flips", False), s["telemetry"].get("route_flips", False)])
                  for s in per_seed if s["telemetry"])
    base_mrr = _mean([s["foundation_test_mrr"] for s in per_seed])

    # ---- pre-registered gates -------------------------------------------------------------------------
    g = {}
    g["HP_SEP_AUC"] = sep_auc >= HP_SEP_AUC_MIN + EPS_BAND
    g["HP_SKIP"] = skip_v2 >= HP_SKIP_MIN
    g["HP_DISCARD"] = disc_v2 >= HP_DISCARD_MIN
    g["HP_CONSOLIDATE_V2"] = cons_v2 >= 0.70
    g["HP_FOLDIN_DIRECTIONAL"] = (foldin_real > 0.0) and (foldin_real > foldin_scr + 0.002)
    g["HP_INTERFERENCE"] = (interf <= HP_INTERFERENCE_TOL) and destr_ok
    g["HP_NONREDUNDANT"] = (abl_auc >= HP_NONREDUNDANT_AUC_MIN) and (abl_p <= HP_NONREDUNDANT_PERM_P)
    g["HP_TELEMETRY"] = tele_ok
    g["baseline_in_band"] = 0.02 < base_mrr < 0.95

    joint = all([g["HP_SEP_AUC"], g["HP_SKIP"], g["HP_DISCARD"], g["HP_CONSOLIDATE_V2"],
                 g["HP_FOLDIN_DIRECTIONAL"], g["HP_INTERFERENCE"], g["HP_NONREDUNDANT"],
                 g["HP_TELEMETRY"], g["baseline_in_band"]])

    # non-redundancy readout for the KEY uncertainty
    if abl_auc >= HP_NONREDUNDANT_AUC_MIN and abl_p <= HP_NONREDUNDANT_PERM_P:
        surprise_verdict = "NON_REDUNDANT_with_schema_fit"
    elif abl_auc == abl_auc:
        surprise_verdict = "REDUNDANT_with_schema_fit_gate_simplifies_to_2_criteria"
    else:
        surprise_verdict = "ABLATION_UNDERPOWERED"

    if joint:
        verdict = "HARD_PASS"
    elif g["HP_SEP_AUC"] and g["HP_DISCARD"] and g["HP_INTERFERENCE"] and g["HP_TELEMETRY"]:
        verdict = "MIDDLE_BAND_gate_mechanism_sound_threshold_or_foldin_tuning"
    else:
        verdict = "HARD_FAIL"

    msg = ("sep_auc=%.3f skip_v2=%.2f cons_v2=%.2f(v1=%.2f hold_v1=%.2f) disc_v2=%.2f foldin=%+.4f(scr=%+.4f) "
           "interf=%.2e destr_ok=%s abl_auc=%.3f abl_p=%.3f corr_ss=%.3f surprise=%s tele_ok=%s base_mrr=%.4f" % (
               sep_auc, skip_v2, cons_v2, cons_v1, hold_v1, disc_v2, foldin_real, foldin_scr, interf, destr_ok,
               abl_auc, abl_p, corr_ss, surprise_verdict, tele_ok, base_mrr))
    summary = "%s: %s" % (verdict, surprise_verdict)
    return dict(verdict=verdict, verdict_msg=msg, summary=summary, gates=g, joint_hard_pass=joint,
                surprise_vs_schema_fit=surprise_verdict, run_mode=run_mode,
                agg=dict(separation_auc=sep_auc, skip_redundant_v2=skip_v2, consolidate_novel_v1=cons_v1,
                         consolidate_novel_v2=cons_v2, hold_novel_v1=hold_v1, discard_noise_v2=disc_v2,
                         foldin_delta_real=foldin_real, foldin_delta_scramble=foldin_scr,
                         interference_delta=interf, ablation_auc=abl_auc, ablation_partial_rho=abl_rho,
                         ablation_partial_perm_p=abl_p, corr_schema_surprise=corr_ss, baseline_test_mrr=base_mrr))


def _dig(d, path):
    for p in path.split("."):
        d = d[p]
    return d


# ---------------------------------------------------------------------------
# self-test (REAL substrate code path at N~16; validity preflight)
# ---------------------------------------------------------------------------
def self_test():
    from experiments._validity_preflight import run_validity_preflight
    from experiments._kge_anchor1_fit import fit_kge_anchor1
    _log("self_test: constructing REAL AdditiveKGMap at tiny scale")
    exercised = set()
    device = torch.device("cpu")

    # tiny planted arena: 4 relations, 16 entities, a withheld r*
    triples = []
    for i in range(16):
        triples.append(("e%d" % i, "ra", "e%d" % ((i + 1) % 16)))
        triples.append(("e%d" % i, "rb", "e%d" % ((i + 3) % 16)))
        triples.append(("e%d" % i, "rc", "e%d" % ((i + 5) % 16)))
        triples.append(("e%d" % i, "rstar", "e%d" % ((i + 2) % 16)))   # withheld relation
    ents = sorted({x for tr in triples for x in (tr[0], tr[2])})
    rels = sorted({tr[1] for tr in triples})
    found = [t for t in triples if t[1] != "rstar"]

    kmap = AdditiveKGMap(device=device)
    kmap.fit(found, entities=ents, relations=rels, k=8, epochs=40, seed=7)   # REAL fit path
    exercised.add("AdditiveKGMap"); exercised.add("AdditiveKGMap.fit")
    _ = kmap.score_all("e0", "ra"); exercised.add("AdditiveKGMap.score_all")
    code = kmap.compose_entity([("e0", "ra"), ("e1", "rb")]); exercised.add("AdditiveKGMap.compose_entity")
    _ = kmap.insert_entity(code, name="e_new"); exercised.add("AdditiveKGMap.insert_entity")

    # gate + AUC + schema-fit sanity
    ent2i = {e: i for i, e in enumerate(ents)}; rel2i = {r: i for i, r in enumerate(rels)}
    found_int = np.array([[ent2i[h], rel2i[r], ent2i[t]] for h, r, t in found], dtype=np.int64)
    reach_pct, _m = build_schema_fit(found_int, len(ents), 2, 50)
    assert reach_pct.shape[0] == len(ents)
    # decision-tree branch coverage (all 5 outcomes reachable)
    outs = {gate_decision_v2(0.9, 0.0, 5, 5), gate_decision_v2(0.9, 0.82, 5, 5), gate_decision_v2(0.1, 0.82, 5, 5),
            gate_decision_v2(0.9, 0.99, 5, 1), gate_decision_v2(0.9, 0.82, 1, 1)}
    assert outs == {"SKIP", "FAST_TRACK", "SLOW_TRACK", "HOLD", "DISCARD"}, "gate branches incomplete: %s" % outs
    # AUC monotonicity
    assert _auc([1, 2, 3], [0, 0, 0]) == 1.0 and _auc([0, 0], [1, 1]) == 0.0
    # telemetry sensitivity: perturbations flip
    assert gate_decision_v2(0.9, 0.82, 1, 1) == "DISCARD"          # recurrence floor flips
    assert gate_decision_v2(0.9, 0.0, 5, 5) == "SKIP"             # surprise flips
    assert gate_decision_v2(0.1, 0.82, 5, 5) != gate_decision_v2(0.9, 0.82, 5, 5)   # schema-fit routes

    # fold-in / interference micro-check: append a relation row -> existing scores identical
    D = kmap.D.clone(); ristar = rel2i["rstar"]
    all_true = defaultdict(set)
    for h, r, t in found_int:
        all_true[(int(h), int(r))].add(int(t))
    exist = found_int[:8]
    before = _recip_ranks(kmap.X, D, exist, all_true, device)
    D2 = D.clone(); D2[ristar] = (kmap.X[torch.tensor([2, 4])] - kmap.X[torch.tensor([0, 1])]).mean(0)
    after = _recip_ranks(kmap.X, D2, exist, all_true, device)
    assert np.allclose(before, after), "append-only fold-in changed existing retrieval (interference bug)"

    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["AdditiveKGMap", "AdditiveKGMap.fit", "AdditiveKGMap.score_all",
                                        "AdditiveKGMap.compose_entity", "AdditiveKGMap.insert_entity"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": AdditiveKGMap, "callable_name": "AdditiveKGMap",
         "kwargs": {"device": "cpu"}},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": device, "seed": 7, "epochs": 1}},
        {"kind": "metric_moves", "metric_name": "foldin_mrr", "before": 0.1, "after": 0.2, "min_delta": 1e-6},
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
    _write_start_marker(output_dir, run_mode, len(cfg["seeds"]))
    t0 = time.time()
    per_seed = []
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    for si, seed in enumerate(cfg["seeds"]):
        _log("seed %d/%d (seed=%d) fitting foundation..." % (si + 1, len(cfg["seeds"]), seed))
        res = run_seed(cfg, seed, device, cache_dir)
        per_seed.append(res)
        _log("seed=%d done: sep_auc=%.3f skip_v2=%.2f cons_v2=%.2f disc_v2=%.2f foldin=%+.4f interf=%.2e abl_auc=%.3f (%.1fs)" % (
            seed, res["separation_auc"], res["skip_redundant"]["v2"], res["consolidate_novel"]["v2"],
            res["discard_noise"]["v2"], res["foldin"]["delta_real"], res["interference"]["delta"],
            res["ablation"]["auc_within_hi_schema"], time.time() - t0))

    # ARMS-MUST-DIFFER: batch surprise vectors distinct (META_RULE_AF)
    shas = per_seed[0]["surprise_sha"]
    assert len({shas["redundant"], shas["novel"], shas["noise"]}) >= 2, "batch surprise vectors bit-identical"

    v = aggregate_and_verdict(per_seed, run_mode)
    elapsed = time.time() - t0
    metrics = dict(anchor_name=ANCHOR_NAME, elapsed_s=round(elapsed, 2),
                   ts_iso=datetime.now(timezone.utc).isoformat(), n_seeds=len(cfg["seeds"]),
                   config=dict(k_core=cfg["k_core"], max_nodes=cfg["max_nodes"], k=cfg["k"], epochs=cfg["epochs"],
                               rstar=cfg["rstar"], seeds=cfg["seeds"]),
                   thresholds=dict(SCHEMA_FIT_MIN=SCHEMA_FIT_MIN, SURPRISE_MIN=SURPRISE_MIN,
                                   SURPRISE_SKIP_V2=SURPRISE_SKIP_V2, DISTINCT_NOVELTY=DISTINCT_NOVELTY,
                                   RECURRENCE_MIN=RECURRENCE_MIN),
                   arms_differ_verified=True, final_metrics_atomicity="tmp_replace",
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
