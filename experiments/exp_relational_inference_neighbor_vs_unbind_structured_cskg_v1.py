"""RELATIONAL_INFERENCE_NEIGHBOR_VS_UNBIND_STRUCTURED: the DECISIVE zero-shot held-out-relation inference
experiment on REAL commonsense knowledge (CSKG). Corrects/decomposes agent a6bbdfd0's "inference flat at chance"
(MEASURED@data/real_kg_constraint_curve_metrics.json:taskB_infer_heldout_relation ~0.0000-0.0005 at every K) into
a clean 2x2 factorial: READOUT x CODES. a6bbdfd0 CONFLATED the readout with the code source; a toy prototype
(scratchpad/structured_codes_inference.py + graded_world_structured_codes.py) showed the chance result was
PRIMARILY the READOUT (self-unbind reads a cue with ZERO info on the held-out value), and that neighbor-retrieval
(CA3 pattern-completion) BEATS the marginal floor even with random codes, with STRUCTURED codes adding an
interpolative margin that is VISIBLE ONLY on the NOVEL-combination stratum under a GRADED value-distance metric
(discrete exact-match hides it). This cell decides it on REAL knowledge where generalization must cross value
boundaries.

THE 2x2 (all arms PAIRED on the SAME held-out (concept, relation, gold) query edges; filtered rank metrics + a
neutral graded value-similarity metric; stratified novel-vs-seen):
  READOUT axis:
    UNBIND  = bind the held-out relation onto the concept's OWN known-relation bundle, cleanup to nearest value
              (a6bbdfd0's op). RANDOM regime: est = sign(bundle_c) * RV[r*], score(t)=est.X_val[t] -- the cue has
              NO r* component => predicted DEGENERATE (<= marginal). STRUCTURED regime: est = bundle_c + D[r*],
              score(t)=-||est - X_t|| -- this is TransE inductive self-inference (may beat marginal; measured).
    NEIGHBOR= represent each TRAIN concept by its known-relation bundle; for a query concept retrieve top-m nearest
              TRAIN concepts by code similarity, transfer their value for the held-out relation by similarity-
              weighted vote (the brain's CA3 pattern-completion). THE HYPOTHESIZED mechanism.
  CODES axis:
    RANDOM     = random bipolar hypervectors (a6bbdfd0's regime); bundle_c = sign(sum_k RV[r_k]*X_val[t_k]).
    STRUCTURED = the additive-map's LEARNED entity/relation codes (AdditiveKGMap coord source = fit_kge_anchor1,
                 k=24 TransE); bundle_c = mean_k(X[t_k] - D[r_k]) (the additive map's native inductive concept
                 code). Carries cross-relation correlation by construction.

CRUX (pre-registered, decisive; keep bands STRICT -- expected effect is REAL-BUT-MODEST per the density de-risk):
  (i)   NEIGHBOR (structured) beats the honest MARGINAL floor (POP): STRUCT_NEIGHBOR_mrr - POP_mrr.
  (ii)  STRUCTURED adds over RANDOM under NEIGHBOR, concentrated on the NOVEL stratum under the GRADED metric:
        (struct_neighbor_valsim - random_neighbor_valsim) on NOVEL queries (the coordinator's 2026-07-14 finding:
        the advantage is LOWER value-distance-to-truth on unseen combinations, NOT higher exact hit@1).
  (iii) SHUFFLE (destroy cross-relation correlation by permuting concept profiles) collapses the neighbor lift to
        ~marginal (must-fail: if it does NOT collapse, the lift is an artifact / leak).
  (iv)  UNBIND(random) stays <= marginal (sanity; reproduces a6bbdfd0's chance = the READOUT, not a hard limit).
REFUTATION: if STRUCTURED does NOT beat RANDOM on the NOVEL stratum under the graded metric (with seed-consistent
sign), the "structured-codes-enable-inference" claim is REFUTED -- the most valuable outcome, reported plainly.

FAIRNESS FIRST-CLASS:
  - Honest floors: POP (rank tails by per-relation train frequency = "predict most-frequent value") + UNIFORM chance.
  - Info-ceiling per relation: ORACLE_NEIGHBOR (neighbor-vote with the held-out edges folded into the STORE/DATA,
    self-inclusion of the gold-bearing concept allowed) = the headroom the neighbor mechanism has given perfect
    reachability. Per-relation headroom (oracle - inductive) reported; the verdict does NOT celebrate sub-ceiling.
  - Novel-vs-seen stratification: a query is SEEN if some TRAIN concept sharing an EXACT known (r_k,v_k) edge with
    the query concept ALSO has (r*, gold) (=> exact-match retrieval can fire); NOVEL otherwise (only graded
    interpolation can help). Structured is expected to earn its keep on NOVEL.
  - Graded value-similarity: NEUTRAL, arm-agnostic train-graph neighbor-set Jaccard between predicted-top1 tail and
    gold (credits predicting a semantic neighbor of the true value). Purely-categorical relations with no usable
    value-similarity => tiny Jaccard for all arms; reported honestly (the experiment then only sees exact-match).
  - NO LEAKAGE: structured codes are fit on TRAIN edges ONLY (train-only refit; the specific held-out
    (concept, r*, gold) triples are NEVER in the fit). Verified: hold edges disjoint from train_int; asserted.

## Compute architecture
class (c) MIXED. The single STRUCTURED fit (train-only Xa/Da, k=24 epochs=500 n_neg=128) is minibatch-SGD ->
GPU-BATCHED (overnight_queue): matmul-heavy neg-scoring, the EXACT workload anchor_compose ran on gpu1024 (CPU
takes ~1-3h; GPU minutes). ONE fit per seed (the info-ceiling is a DATA-fold-in neighbor oracle = NO second fit,
compute-proportional). All bundling / neighbor similarity / vote / stratification / Jaccard / POP / filtered-rank
are CPU graph+matmul ops (cheap; nq~2.7k x n_concepts~2.7k x dim=1024 ~ 8e9 flops). Fits on cuda; readouts on cpu;
codes moved across the boundary once. Storage strategy: SHARDED (each concept its own bundle vector; neighbor
retrieval is per-concept, no global bundle) per the composition-depth storage law.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): the 4 2x2 cells + POP + ORACLE + SHUFFLE >= 5 distinct sigs.
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: decisive band (ii) is RELATIVE (>= REL_STRUCT_GAIN of the random-neighbor graded metric)
#   + seed-consistency, ROBUST to the unknown real value-similarity SCALE => discriminator_reachability OK by
#   construction; the info-ceiling (ORACLE_NEIGHBOR) bounds each arm and is reported per-relation.
# - baseline_in_band: POP is the honest floor (structurally low, not saturated); STRUCT_NEIGHBOR must clear it;
#   UNIFORM chance ~1/N; ORACLE_NEIGHBOR > inductive arms (headroom > 0). Verified at self-test on planted arena.
# - discriminator survives scale: the FULL runs at the a6bbdfd0 regime (dense CSKG core, n_dim=1024, k=24); the
#   self-test fires structured>random(novel,graded) + neighbor>unbind(random) + shuffle-collapse on a planted
#   latent-KIND arena that has BOTH concept-clustering (neighbor works) AND cross-relation correlation (structure
#   helps on novel). A MEMSMOKE (reduced core, 1 seed) confirms the discriminator on REAL data before FULL.
# - HARD bands strictly separated: INFER_MARGIN=0.02 (i); REL_STRUCT_GAIN=0.10 vs REFUTE_REL=0.02 (ii, 8% dead-band
#   + seed-sign); SHUFFLE_EPS=0.01 collapse vs 0.02 leak (iii); UNBIND_SANITY_EPS=0.005 (iv).
# - HP_SCOPE: (i) applies to STRUCT_NEIGHBOR vs POP; (ii) to STRUCT_NEIGHBOR vs RANDOM_NEIGHBOR on NOVEL; (iii) to
#   SHUFFLE_NEIGHBOR vs POP; (iv) to RANDOM_UNBIND vs POP. UNIFORM/ORACLE_NEIGHBOR = floor/ceiling references.
# - cardinality: EXPECTED_N_UNITS = n_seeds; each seed asserted to produce all arms + >=5 sigs + finite fit +
#   non-empty novel & seen strata.
# - per-unit failure-class instrumentation (no bare except; per-seed failure_class recorded).
# - calibration_check: default_ok_for_this_regime -- all bands pre-registered, NOT tuned on real data; the additive
#   fit config is COPIED VERBATIM from the confirmed anchor_compose FULL (k=24/epochs=500/n_neg=128).
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the docstring/prereg.
# - progress_logging: print_flush_true (line-buffered stdout + per-seed/per-phase flush prints + heartbeat; timeout>=1800).

ASCII-only. No bare except; except SystemExit before except Exception.
"""

import argparse
import gc
import hashlib
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

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, write_metrics, write_partial, assert_discriminator_fires,
)
from experiments._validity_preflight import run_validity_preflight  # noqa: E402
from experiments.exp_gt_induction_fb15k237_dense_v1 import Graph, build_ids  # noqa: E402
from experiments.exp_cskg_dense_core_headroom_acceptance_v1 import (  # noqa: E402
    build_cskg_core_triples, _ensure_cskg,
)
from experiments.exp_course_c_map_builder_cskg_l2_genuine_v1 import (  # noqa: E402
    _to_int_edges, build_true_by_hr_int, filtered_hits_from_scores, pop_hits,
)
from experiments._kge_anchor1_fit import fit_kge_anchor1, A1_LR  # noqa: E402
from experiments._fit_checkpoint import FitCheckpoint  # noqa: E402

ANCHOR_NAME = "relational_inference_neighbor_vs_unbind_structured_cskg_v1"

# ---- arm names (all scored PAIRED on the SAME held-out QUERY edges) ----
RU = "RANDOM_UNBIND"           # random codes  x self-unbind  (a6bbdfd0 op; predicted <= marginal)
SU = "STRUCT_UNBIND"           # structured codes x self-unbind (TransE self-inference; measured)
RN = "RANDOM_NEIGHBOR"         # random codes  x neighbor-vote (CA3; exact-match regime)
SN = "STRUCT_NEIGHBOR"         # structured codes x neighbor-vote (THE headline mechanism)
SHUF = "SHUFFLE_NEIGHBOR"      # must-fail: structured neighbor on profile-shuffled concepts (correlation destroyed)
POP = "BASELINE_POP"           # honest marginal floor (rank tails by per-relation train freq)
UNIF = "UNIFORM_CHANCE"        # ~1/N reference
ORC = "ORACLE_NEIGHBOR"        # info-ceiling: neighbor-vote with held-out edges folded into the store (headroom ref)

INDUCTIVE = [RU, SU, RN, SN]
ALL_ARMS = [RU, SU, RN, SN, SHUF, POP, UNIF, ORC]
EVAL_KS = (1, 3, 10, 100)
CEIL_METRIC = "mrr"

# ---- CITED reference (the a6bbdfd0 result this corrects) ----
CITED_A6_TASKB_MAX = 0.0005   # MEASURED@data/real_kg_constraint_curve_metrics.json:taskB_infer_heldout_relation (max over K)
CITED_AA_ORACLE = 0.137       # MEASURED@data/exp_anchor_compose_inductive_entity_cskg_v1/metrics.json:gates.heldout_mrr.ORACLE_ADDITIVE (structured-code ceiling scale)

# ---- PRE-REGISTERED bands (NOT tuned on real data) ----
INFER_MARGIN = 0.02           # (i) STRUCT_NEIGHBOR_mrr - POP_mrr >= this => INFERS (HARD-PASS)
INFER_FLOOR = 0.005           # (i) <= this => NO_INFERENCE
REL_STRUCT_GAIN = 0.10        # (ii) (SN_valsim - RN_valsim)/max(RN_valsim,eps) on NOVEL >= this => STRUCTURE_ADDS (HARD-PASS)
REFUTE_REL = 0.02             # (ii) <= this => REFUTED (structured adds nothing on the novel stratum)
SEED_SIGN_FRAC = 0.66         # (ii) sign consistent in >= this frac of seeds
SHUFFLE_EPS = 0.01            # (iii) |SHUF_mrr - POP_mrr| <= this => collapse (must-fail fires)
SHUFFLE_LEAK = 0.02           # (iii) SHUF_mrr - POP_mrr > this => BROKEN (leak/artifact)
UNBIND_SANITY_EPS = 0.005     # (iv) RU_mrr - POP_mrr <= this => degenerate (sanity)
VALSIM_EPS = 1e-4             # denominator floor for the relative graded gain

# ---- self-test planted thresholds (calibrated on synthetic, NOT real data) ----
ST_SN_BEATS_POP = 0.02        # planted kind-arena: STRUCT_NEIGHBOR mrr - POP mrr >= this
ST_NEIGHBOR_BEATS_UNBIND = 0.03  # random codes: RANDOM_NEIGHBOR mrr - RANDOM_UNBIND mrr >= this
ST_SHUFFLE_COLLAPSE = 0.01    # SHUFFLE_NEIGHBOR - POP <= this on the planted arena (one-sided; below-marginal is OK)
ST_STRUCT_NOVEL_GAIN = 0.02   # planted: SN_valsim - RN_valsim on NOVEL >= this (structure adds on novel, graded;
                              #          on the planted arena RANDOM sits at value_sim=0.0 so 0.02 needs genuine structure)

SCORE_CHUNK = 512

# Config profiles. SELFTEST/MEMSMOKE/FULL exercise the SAME split->fit->bundle->readout->stratify->verdict path.
SELFTEST_CFG = dict(mode="synthetic", n_dim=256, k=8, epochs=120, n_neg=32, batch=2048, neg_chunk=16,
                    m_nn=15, k_min_rel=3, match_min=2, seeds=[7])
MEMSMOKE_CFG = dict(mode="cskg", n_dim=512, k=16, epochs=200, n_neg=64, batch=4096, neg_chunk=16, ckpt_every=25,
                    m_nn=15, k_min_rel=4, match_min=2, cskg_max_lines=150000, k_core=6, cskg_max_nodes=800,
                    n_query_cap=1500, min_query=40, seeds=[7])
FULL_CFG = dict(mode="cskg", n_dim=1024, k=24, epochs=500, n_neg=128, batch=8192, neg_chunk=16, ckpt_every=20,
                m_nn=25, k_min_rel=4, match_min=2, cskg_max_lines=0, k_core=12, cskg_max_nodes=0,
                n_query_cap=3000, min_query=100, seeds=[7, 13, 17])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.4f" % x) if (x == x) else "nan"


def _sig(arr):
    a = np.round(np.asarray(arr, dtype=np.float64), 4)
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "_start_marker.json.tmp")
    final = os.path.join(str(output_dir), "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(str(output_dir), exist_ok=True)
    tmp = os.path.join(str(output_dir), "metrics.json.tmp")
    final = os.path.join(str(output_dir), "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Held-out-RELATION split: among concepts with >= k_min_rel distinct relations, hold out ONE edge each as a query.
# The remaining edges stay in train (concept is SEEN via its other edges; the (c, r*, gold) triple is unseen).
# ---------------------------------------------------------------------------

def build_heldout_relation_split(pool_lbl, k_min_rel, seed, n_query_cap=0):
    """pool_lbl: list of (h, r, t) label triples. For each dense head (>= k_min_rel distinct relations), hold out
    ONE of its edges (deterministic per seed). Returns (train_lbl, query_lbl, prov). No (c, r*, gold) query triple
    is in train (verified downstream). query_lbl each element = (h, r, gold)."""
    rng = np.random.default_rng(seed * 100003 + 11)
    out_by_head = defaultdict(list)          # h -> list of (r, t)
    rels_by_head = defaultdict(set)
    for (h, r, t) in pool_lbl:
        out_by_head[h].append((r, t))
        rels_by_head[h].add(r)
    dense = sorted([h for h in out_by_head if len(rels_by_head[h]) >= k_min_rel])
    query = []
    held_key = set()                          # (h, r, t) held out -> excluded from train
    for h in dense:
        edges = out_by_head[h]
        j = int(rng.integers(len(edges)))
        r, t = edges[j]
        query.append((h, r, t))
        held_key.add((h, r, t))
    if n_query_cap and len(query) > n_query_cap:
        idx = sorted(rng.choice(len(query), size=n_query_cap, replace=False).tolist())
        # queries NOT selected: their held edge goes BACK to train (keep only capped queries held out)
        sel = set(idx)
        keep_query = []
        for qi, q in enumerate(query):
            if qi in sel:
                keep_query.append(q)
            else:
                held_key.discard(q)
        query = keep_query
    train = [(h, r, t) for (h, r, t) in pool_lbl if (h, r, t) not in held_key]
    prov = dict(n_pool=len(pool_lbl), n_dense_concepts=len(dense), n_query=len(query),
                n_train=len(train), k_min_rel=k_min_rel)
    return train, query, prov


# ---------------------------------------------------------------------------
# Code sources. RANDOM: bipolar X_val (N,n_dim) + RV (n_rel,n_dim). STRUCTURED: learned X (N,k) + D (n_rel,k).
# ---------------------------------------------------------------------------

def make_random_codes(N, n_rel, n_dim, seed):
    g = torch.Generator(device="cpu").manual_seed(seed * 100000 + n_dim + 3)
    X_val = (torch.randint(0, 2, (N, n_dim), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32)
    RV = (torch.randint(0, 2, (n_rel, n_dim), generator=g, dtype=torch.int8) * 2 - 1).to(torch.float32)
    return X_val, RV


def fit_structured_codes(train_int, N, n_rel, cfg, device, seed, ckpt_dir=None):
    """Train-only additive-map fit (AdditiveKGMap's LearnedSGD coord source). Returns (X [N,k], D [n_rel,k]).
    NO held-out edge is in train_int => zero leakage (asserted by caller)."""
    ckpt = None
    if ckpt_dir is not None and cfg.get("ckpt_every"):
        ckpt = FitCheckpoint(ckpt_dir, "struct_seed%d" % seed, cfg["ckpt_every"])
    X, D = fit_kge_anchor1(train_int, N, n_rel, cfg["k"], device, seed, cfg["epochs"], reciprocal=True, lr=A1_LR,
                           n_neg=cfg["n_neg"], batch_size=cfg["batch"], neg_chunk=cfg.get("neg_chunk"), ckpt=ckpt)
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return X.detach().to("cpu"), D.detach().to("cpu")


# ---------------------------------------------------------------------------
# Concept bundles (per head entity) from its KNOWN (train) edges. SHARDED: one bundle vector per concept.
# ---------------------------------------------------------------------------

def build_random_bundles(train_int, N, X_val, RV):
    """B[e] = sign(sum over e's train head-edges (r,t) of RV[r]*X_val[t]); rows with no head-edge stay 0. (N,n_dim)."""
    n_dim = X_val.shape[1]
    acc = torch.zeros(N, n_dim, dtype=torch.float32)
    for i in range(train_int.shape[0]):
        h = int(train_int[i, 0]); r = int(train_int[i, 1]); t = int(train_int[i, 2])
        acc[h] += RV[r] * X_val[t]
    B = torch.sign(acc)
    B[B == 0] = 0.0
    return B


def build_struct_bundles(train_int, N, X, D):
    """B[e] = mean over e's train head-edges (r,t) of (X[t] - D[r]) (additive-map inductive concept code). (N,k)."""
    k = X.shape[1]
    acc = torch.zeros(N, k, dtype=torch.float32)
    cnt = torch.zeros(N, dtype=torch.float32)
    for i in range(train_int.shape[0]):
        h = int(train_int[i, 0]); r = int(train_int[i, 1]); t = int(train_int[i, 2])
        acc[h] += (X[t] - D[r])
        cnt[h] += 1.0
    mask = cnt > 0
    acc[mask] = acc[mask] / cnt[mask].unsqueeze(1)
    return acc


def _l2norm_rows(B):
    n = torch.linalg.norm(B, dim=1, keepdim=True)
    n = torch.clamp(n, min=1e-9)
    return B / n


# ---------------------------------------------------------------------------
# READOUTS -> (nq, N) score tensors (higher=better), scored by filtered_hits_from_scores.
# ---------------------------------------------------------------------------

def unbind_random_scores(query_int, bundles_rand, X_val, RV, device):
    """est_i = sign(bundle[c_i]) * RV[r*_i]; score(t) = est_i . X_val[t]. Cue has NO r* term => degenerate."""
    nq = query_int.shape[0]; N = X_val.shape[0]
    est = torch.empty(nq, X_val.shape[1], dtype=torch.float32)
    for i in range(nq):
        c = int(query_int[i, 0]); r = int(query_int[i, 1])
        est[i] = torch.sign(bundles_rand[c]) * RV[r]
    est = est.to(device); Xv = X_val.to(device)
    out = torch.empty(nq, N, dtype=torch.float32)
    for s in range(0, nq, SCORE_CHUNK):
        e = min(s + SCORE_CHUNK, nq)
        out[s:e] = (est[s:e] @ Xv.T).detach().to("cpu")
    del est, Xv
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return out


def unbind_struct_scores(query_int, bundles_struct, X, D, device):
    """est_i = bundle_struct[c_i] + D[r*_i]; score(t) = -||est_i - X[t]||. TransE inductive self-inference."""
    nq = query_int.shape[0]; N = X.shape[0]; k = X.shape[1]
    pred = torch.empty(nq, k, dtype=torch.float32)
    for i in range(nq):
        c = int(query_int[i, 0]); r = int(query_int[i, 1])
        pred[i] = bundles_struct[c] + D[r]
    pred = pred.to(device); Xd = X.to(device)
    Xsq = (Xd * Xd).sum(dim=1)
    out = torch.empty(nq, N, dtype=torch.float32)
    XT = Xd.T
    for s in range(0, nq, SCORE_CHUNK):
        e = min(s + SCORE_CHUNK, nq)
        pc = pred[s:e]
        d2 = (pc * pc).sum(dim=1, keepdim=True) + Xsq.unsqueeze(0) - 2.0 * (pc @ XT)
        out[s:e] = (-torch.sqrt(torch.clamp(d2, min=0.0))).detach().to("cpu")
    del pred, Xd, XT
    if getattr(device, "type", "") == "cuda":
        torch.cuda.empty_cache()
    return out


def neighbor_scores(query_int, bundles, store_heads, out_by_head, m_nn, N, allow_self=False, weight_pos=True):
    """Neighbor-vote (CA3): for each query c, top-m nearest store concepts by bundle cosine; those with an (r*, t)
    train edge vote their tail t with weight max(sim,0). Returns (nq, N). store_heads: list of head-entity ids in
    the store. out_by_head: dict head -> list of (r, t) train edges. allow_self: include the query concept itself
    (ORACLE fold-in uses True with gold-bearing store)."""
    nq = query_int.shape[0]
    Bn = _l2norm_rows(bundles)                                   # (N, dim)
    Bstore = Bn[store_heads]                                     # (n_store, dim)
    head_pos = {int(h): j for j, h in enumerate(store_heads)}
    scores = torch.zeros(nq, N, dtype=torch.float32)
    for s in range(0, nq, SCORE_CHUNK):
        e = min(s + SCORE_CHUNK, nq)
        qids = [int(query_int[i, 0]) for i in range(s, e)]
        Q = Bn[qids]                                             # (b, dim)
        S = Q @ Bstore.T                                         # (b, n_store) cosine
        for bi, ci in enumerate(range(s, e)):
            rstar = int(query_int[ci, 1])
            row = S[bi].clone()
            if not allow_self and ci_head_in_store(qids[bi], head_pos):
                row[head_pos[qids[bi]]] = -1e30                  # exclude self
            mm = min(m_nn, row.shape[0])
            top = torch.topk(row, mm).indices.tolist()
            for j in top:
                sim = float(S[bi, j].item())
                w = max(sim, 0.0) if weight_pos else sim
                if w <= 0.0:
                    continue
                nb_head = int(store_heads[j])
                for (rr, tt) in out_by_head.get(nb_head, ()):    # neighbor's train edges
                    if rr == rstar:
                        scores[ci, tt] += w
    return scores


def ci_head_in_store(head, head_pos):
    return head in head_pos


# ---------------------------------------------------------------------------
# Neutral graded value-similarity: train-graph neighbor-set Jaccard between two tails.
# ---------------------------------------------------------------------------

def build_neighbor_sets(train_int, N):
    """nbr[e] = set of entities e connects to via ANY train edge (both directions). For value-similarity Jaccard."""
    nbr = [set() for _ in range(N)]
    for i in range(train_int.shape[0]):
        h = int(train_int[i, 0]); t = int(train_int[i, 2])
        nbr[h].add(t); nbr[t].add(h)
    return nbr


def value_sim(a, b, nbr):
    if a == b:
        return 1.0
    Na = nbr[a]; Nb = nbr[b]
    if not Na or not Nb:
        return 0.0
    inter = len(Na & Nb)
    if inter == 0:
        return 0.0
    return inter / float(len(Na | Nb))


def graded_metric(scores, query_int, nbr):
    """Per query: value_sim(argmax_t score, gold). Returns array (nq,) of graded similarities in [0,1]."""
    nq = scores.shape[0]
    vals = np.zeros(nq, dtype=np.float64)
    top1 = torch.argmax(scores, dim=1).tolist()
    for i in range(nq):
        gold = int(query_int[i, 2])
        vals[i] = value_sim(int(top1[i]), gold, nbr)
    return vals


# ---------------------------------------------------------------------------
# Novel-vs-seen stratification (exact-match reachability).
# ---------------------------------------------------------------------------

def compute_novel_mask(query_int, train_int, N, match_min=2):
    """SEEN if some TRAIN concept sharing >= match_min EXACT known (r_k,v_k) edges with the query concept ALSO has
    (r*, gold) => exact-match retrieval from a genuinely similar concept can deliver gold. NOVEL otherwise (only
    graded interpolation across weaker/holistic similarity could find it). match_min=2 avoids counting a coincidental
    single-edge overlap as reachable. Returns boolean array (nq,) True=NOVEL."""
    from collections import Counter as _Counter
    edge2heads = defaultdict(set)                # (r, t) -> set of heads with that exact edge
    hr2tails = defaultdict(set)                  # (h, r) -> set of tails
    out_by_head = defaultdict(list)
    for i in range(train_int.shape[0]):
        h = int(train_int[i, 0]); r = int(train_int[i, 1]); t = int(train_int[i, 2])
        edge2heads[(r, t)].add(h)
        hr2tails[(h, r)].add(t)
        out_by_head[h].append((r, t))
    nq = query_int.shape[0]
    novel = np.ones(nq, dtype=bool)
    for i in range(nq):
        c = int(query_int[i, 0]); rstar = int(query_int[i, 1]); gold = int(query_int[i, 2])
        overlap = _Counter()
        for (rk, vk) in out_by_head.get(c, ()):
            if rk == rstar:
                continue
            for h2 in edge2heads.get((rk, vk), ()):
                if h2 != c:
                    overlap[h2] += 1
        seen = any(ov >= match_min and gold in hr2tails.get((h2, rstar), ())
                   for h2, ov in overlap.items())
        novel[i] = not seen
    return novel


# ---------------------------------------------------------------------------
# Score every arm PAIRED. Returns arm_scores + graded + novel mask + diagnostics.
# ---------------------------------------------------------------------------

def score_all_arms(prep, cfg, device, seed, ckpt_dir=None):
    N = prep["N"]; n_rel = prep["n_rel"]; n_dim = cfg["n_dim"]
    train_int = prep["train_int"]; query_int = prep["query_int"]; all_true = prep["all_true"]
    out_by_head = prep["out_by_head"]; store_heads = prep["store_heads"]; nbr = prep["nbr"]
    m_nn = cfg["m_nn"]

    # ---- codes ----
    X_val, RV = make_random_codes(N, n_rel, n_dim, seed)
    X, D = fit_structured_codes(train_int, N, n_rel, cfg, device, seed, ckpt_dir=ckpt_dir)
    fits_finite = bool(torch.isfinite(X).all().item() and torch.isfinite(D).all().item())

    # ---- bundles ----
    B_rand = build_random_bundles(train_int, N, X_val, RV)
    B_struct = build_struct_bundles(train_int, N, X, D)

    # ---- SHUFFLE control: permute concept profiles (destroy which concept has which known bundle) ----
    rngp = np.random.default_rng(seed * 4441 + 19)
    perm = rngp.permutation(len(store_heads))
    B_struct_shuf = B_struct.clone()
    src = [int(store_heads[p]) for p in perm]
    for j, h in enumerate(store_heads):
        B_struct_shuf[int(h)] = B_struct[src[j]]

    arm_scores = {}
    arm_scores[RU] = unbind_random_scores(query_int, B_rand, X_val, RV, device)
    arm_scores[SU] = unbind_struct_scores(query_int, B_struct, X, D, device)
    arm_scores[RN] = neighbor_scores(query_int, B_rand, store_heads, out_by_head, m_nn, N)
    arm_scores[SN] = neighbor_scores(query_int, B_struct, store_heads, out_by_head, m_nn, N)
    arm_scores[SHUF] = neighbor_scores(query_int, B_struct_shuf, store_heads, out_by_head, m_nn, N)
    # ---- ORACLE (info-ceiling = reachability ceiling): perfect ranking of gold WHEN the struct-neighbor voted set
    #      already contains it (SN can do no better than rank a reachable gold first). Headroom = ORACLE - SN = the
    #      pure ranking loss; ORACLE ~ POP => even a perfect ranker cannot reach gold in the retrieved neighborhood
    #      (LOW info-ceiling for that relation) => do NOT celebrate a sub-ORACLE arm. Cheap: derived from SN scores,
    #      no refit / no self-cheat vote. Strictly >= SN by construction. ----
    orc_scores = arm_scores[SN].clone()
    for i in range(query_int.shape[0]):
        gold = int(query_int[i, 2])
        if float(orc_scores[i, gold].item()) > 0.0:
            orc_scores[i, gold] = float(arm_scores[SN][i].max().item()) + 1.0
    arm_scores[ORC] = orc_scores
    # UNIFORM chance scores: deterministic tiny noise (rank-random)
    gnu = torch.Generator(device="cpu").manual_seed(seed * 999 + 5)
    arm_scores[UNIF] = torch.rand(query_int.shape[0], N, generator=gnu, dtype=torch.float32)

    # ---- graded metric + novel mask ----
    novel = compute_novel_mask(query_int, train_int, N, match_min=cfg.get("match_min", 2))
    graded = {a: graded_metric(arm_scores[a], query_int, nbr) for a in [RU, SU, RN, SN, SHUF, ORC]}

    # ---- filtered rank metrics per arm (overall + per stratum) ----
    def _rank(sc):
        return filtered_hits_from_scores(sc, query_int, all_true, ks=EVAL_KS)

    arm_metric = {}
    arm_metric_novel = {}
    arm_metric_seen = {}
    q_novel = query_int[novel] if novel.any() else query_int[:0]
    q_seen = query_int[~novel] if (~novel).any() else query_int[:0]
    for a in [RU, SU, RN, SN, SHUF, ORC, UNIF]:
        sc = arm_scores[a]
        arm_metric[a] = _rank(sc)
        if novel.any():
            arm_metric_novel[a] = filtered_hits_from_scores(sc[novel], q_novel, all_true, ks=EVAL_KS)
        if (~novel).any():
            arm_metric_seen[a] = filtered_hits_from_scores(sc[~novel], q_seen, all_true, ks=EVAL_KS)
    pop_m, pop_rank = pop_hits(prep["gd"].rel_tail_freq, query_int, all_true, N, ks=EVAL_KS)
    arm_metric[POP] = pop_m

    # ---- signatures (arms-must-differ) ----
    arm_sig = {a: _sig(arm_scores[a].numpy()[:min(64, arm_scores[a].shape[0])].ravel())
               for a in [RU, SU, RN, SN, SHUF, ORC, UNIF]}
    arm_sig[POP] = _sig(pop_rank.astype(np.float64))

    # ---- per-relation info-ceiling headroom (ORACLE vs SN) ----
    per_rel = {}
    rel_ids = sorted(set(int(query_int[i, 1]) for i in range(query_int.shape[0])))
    for r in rel_ids:
        mask = np.array([int(query_int[i, 1]) == r for i in range(query_int.shape[0])])
        if mask.sum() < 3:
            continue
        qr = query_int[mask]
        sn_r = filtered_hits_from_scores(arm_scores[SN][mask], qr, all_true, ks=EVAL_KS)[CEIL_METRIC]
        orc_r = filtered_hits_from_scores(arm_scores[ORC][mask], qr, all_true, ks=EVAL_KS)[CEIL_METRIC]
        pop_r, _ = pop_hits(prep["gd"].rel_tail_freq, qr, all_true, N, ks=EVAL_KS)
        per_rel[str(r)] = dict(n=int(mask.sum()), sn_mrr=round(sn_r, 5), oracle_mrr=round(orc_r, 5),
                               pop_mrr=round(pop_r[CEIL_METRIC], 5), headroom=round(orc_r - sn_r, 5))

    # graded means per stratum
    def _gmean(a, msk):
        v = graded[a][msk]
        return float(v.mean()) if v.shape[0] > 0 else float("nan")

    graded_summary = {}
    for a in [RU, SU, RN, SN, SHUF, ORC]:
        graded_summary[a] = dict(all=_gmean(a, np.ones(len(novel), dtype=bool)),
                                 novel=_gmean(a, novel), seen=_gmean(a, ~novel))

    diag = dict(fits_finite=fits_finite, n_novel=int(novel.sum()), n_seen=int((~novel).sum()),
                n_query=int(query_int.shape[0]), n_store=len(store_heads),
                X_norm=round(float(torch.linalg.norm(X).item()), 4))

    # free big tensors
    for a in list(arm_scores.keys()):
        del arm_scores[a]
    gc.collect()

    return dict(arm_metric=arm_metric, arm_metric_novel=arm_metric_novel, arm_metric_seen=arm_metric_seen,
                arm_sig=arm_sig, graded_summary=graded_summary, per_rel=per_rel, diag=diag,
                pop_mrr=pop_m[CEIL_METRIC])


# ---------------------------------------------------------------------------
# Prepare a seed-deterministic held-out-RELATION corpus.
# ---------------------------------------------------------------------------

def prepare_corpus(pool_lbl, cfg, seed):
    train_lbl, query_lbl, prov = build_heldout_relation_split(
        pool_lbl, cfg["k_min_rel"], seed, n_query_cap=cfg.get("n_query_cap", 0))
    ent2i, rel2i = build_ids(pool_lbl, [], [])
    N = len(ent2i); n_rel = len(rel2i)
    train_int = _to_int_edges(train_lbl, ent2i, rel2i)
    query_int = _to_int_edges(query_lbl, ent2i, rel2i)
    # LEAKAGE GUARD: no query triple may be in train_int
    train_set = set((int(train_int[i, 0]), int(train_int[i, 1]), int(train_int[i, 2]))
                    for i in range(train_int.shape[0]))
    leak = sum(1 for i in range(query_int.shape[0])
               if (int(query_int[i, 0]), int(query_int[i, 1]), int(query_int[i, 2])) in train_set)
    out_by_head = defaultdict(list)
    for i in range(train_int.shape[0]):
        out_by_head[int(train_int[i, 0])].append((int(train_int[i, 1]), int(train_int[i, 2])))
    store_heads = sorted(out_by_head.keys())
    gd = Graph(train_lbl, ent2i, rel2i)
    all_true = build_true_by_hr_int(train_int, query_int)
    nbr = build_neighbor_sets(train_int, N)
    return dict(ent2i=ent2i, rel2i=rel2i, N=N, n_rel=n_rel, train_int=train_int, query_int=query_int,
                out_by_head=out_by_head, store_heads=store_heads, gd=gd, all_true=all_true, nbr=nbr,
                prov=prov, leak=int(leak))


def run_corpus(pool_lbl, cfg, device, seed, corpus_name, ckpt_dir=None):
    prep = prepare_corpus(pool_lbl, cfg, seed)
    result = dict(corpus=corpus_name, seed=seed, N=int(prep["N"]), n_rel=int(prep["n_rel"]),
                  n_train=int(prep["train_int"].shape[0]), n_query=int(prep["query_int"].shape[0]),
                  n_store=len(prep["store_heads"]), leak=prep["leak"], prov=prep["prov"],
                  n_dim=int(cfg["n_dim"]), k=int(cfg["k"]))
    if prep["query_int"].shape[0] < 1 or prep["leak"] > 0:
        result["invalid"] = "empty_query" if prep["query_int"].shape[0] < 1 else "LEAK_%d" % prep["leak"]
        return result, None
    fs = score_all_arms(prep, cfg, device, seed, ckpt_dir=ckpt_dir)
    result.update(
        arm_mrr={a: round(fs["arm_metric"][a][CEIL_METRIC], 6) for a in ALL_ARMS},
        arm_hits={a: {kk: round(vv, 6) for kk, vv in fs["arm_metric"][a].items() if kk != "n"} for a in ALL_ARMS},
        arm_mrr_novel={a: round(fs["arm_metric_novel"].get(a, {}).get(CEIL_METRIC, float("nan")), 6)
                       for a in [RU, SU, RN, SN, SHUF, ORC, UNIF]},
        arm_mrr_seen={a: round(fs["arm_metric_seen"].get(a, {}).get(CEIL_METRIC, float("nan")), 6)
                      for a in [RU, SU, RN, SN, SHUF, ORC, UNIF]},
        graded=fs["graded_summary"], per_rel_ceiling=fs["per_rel"], arm_sigs=fs["arm_sig"], diag=fs["diag"],
    )
    return result, fs


# ---------------------------------------------------------------------------
# Decisive verdict over per-seed results.
# ---------------------------------------------------------------------------

def _nm(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def decisive_verdict(per_seed):
    def agg_mrr(arm):
        return _nm([ps["arm_mrr"].get(arm, float("nan")) for ps in per_seed])

    def agg_graded(arm, stratum):
        return _nm([ps["graded"].get(arm, {}).get(stratum, float("nan")) for ps in per_seed])

    mrr = {a: agg_mrr(a) for a in ALL_ARMS}
    sn = mrr[SN]; rn = mrr[RN]; ru = mrr[RU]; su = mrr[SU]; shuf = mrr[SHUF]; pop = mrr[POP]
    unif = mrr[UNIF]; orc = mrr[ORC]

    # (i) INFERS: STRUCT_NEIGHBOR beats marginal
    infer_gap = sn - pop
    infers = bool(infer_gap == infer_gap and infer_gap >= INFER_MARGIN)
    no_infer = bool(infer_gap == infer_gap and infer_gap <= INFER_FLOOR)

    # (ii) STRUCTURE_ADDS on NOVEL under graded metric (relative gain + seed-sign consistency)
    sn_nov = agg_graded(SN, "novel"); rn_nov = agg_graded(RN, "novel")
    rel_gain = ((sn_nov - rn_nov) / max(rn_nov, VALSIM_EPS)) if (sn_nov == sn_nov and rn_nov == rn_nov) else float("nan")
    per_seed_signs = []
    for ps in per_seed:
        a = ps["graded"].get(SN, {}).get("novel", float("nan"))
        b = ps["graded"].get(RN, {}).get("novel", float("nan"))
        if a == a and b == b:
            per_seed_signs.append(1 if (a - b) > 0 else 0)
    sign_frac = (sum(per_seed_signs) / len(per_seed_signs)) if per_seed_signs else 0.0
    structure_adds = bool(rel_gain == rel_gain and rel_gain >= REL_STRUCT_GAIN and sign_frac >= SEED_SIGN_FRAC)
    refuted_struct = bool(rel_gain == rel_gain and rel_gain <= REFUTE_REL)

    # (iii) SHUFFLE collapse (must-fail)
    shuf_gap = shuf - pop
    shuffle_collapses = bool(shuf_gap == shuf_gap and shuf_gap <= SHUFFLE_EPS)
    shuffle_leaks = bool(shuf_gap == shuf_gap and shuf_gap > SHUFFLE_LEAK)

    # (iv) UNBIND(random) sanity
    unbind_gap = ru - pop
    unbind_sane = bool(unbind_gap == unbind_gap and unbind_gap <= UNBIND_SANITY_EPS)

    # ceiling sanity
    ceiling_ok = bool(orc == orc and sn == sn and orc >= sn - 1e-6)

    pos_controls_ok = bool(not shuffle_leaks and ceiling_ok
                           and all(ps.get("diag", {}).get("fits_finite", False) for ps in per_seed)
                           and all(ps.get("leak", 1) == 0 for ps in per_seed))

    if not pos_controls_ok:
        verdict = "INCONCLUSIVE_CONTROL_OR_LEAK_FAILED"
    elif infers and structure_adds and shuffle_collapses:
        verdict = "STRUCTURED_CODES_ENABLE_INFERENCE"
    elif infers and shuffle_collapses and refuted_struct:
        verdict = "NEIGHBOR_INFERS_BUT_STRUCTURE_ADDS_NOTHING_REFUTED"
    elif infers and shuffle_collapses:
        verdict = "NEIGHBOR_INFERS_STRUCTURE_MIDDLE_BAND"
    elif no_infer:
        verdict = "NO_INFERENCE_EVEN_WITH_NEIGHBOR"
    else:
        verdict = "MIDDLE_BAND_INCONCLUSIVE"

    msg = ("%s || MRR: SN(struct-nbr)=%s RN(rand-nbr)=%s SU(struct-unbind)=%s RU(rand-unbind)=%s POP=%s UNIF=%s "
           "ORACLE=%s || (i)INFER SN-POP=%s(>=%.3f=%s) (ii)STRUCT novel-graded SN=%s RN=%s relgain=%s(>=%.2f & sign>=%.2f=%s; "
           "refute<=%.2f=%s) (iii)SHUF-POP=%s(collapse|.|<=%.3f=%s; leak>%.3f=%s) (iv)RU-POP=%s(sane<=%.3f=%s) | "
           "ceiling_ok=%s pos_controls=%s"
           % (verdict, _fmt(sn), _fmt(rn), _fmt(su), _fmt(ru), _fmt(pop), _fmt(unif), _fmt(orc),
              _fmt(infer_gap), INFER_MARGIN, infers, _fmt(sn_nov), _fmt(rn_nov), _fmt(rel_gain), REL_STRUCT_GAIN,
              SEED_SIGN_FRAC, structure_adds, REFUTE_REL, refuted_struct, _fmt(shuf_gap), SHUFFLE_EPS,
              shuffle_collapses, SHUFFLE_LEAK, shuffle_leaks, _fmt(unbind_gap), UNBIND_SANITY_EPS, unbind_sane,
              ceiling_ok, pos_controls_ok))

    def _r(x, nd=6):
        return round(x, nd) if (x == x and x != float("inf")) else (None if x != x else "inf")

    gates = dict(
        verdict=verdict,
        mrr=dict(SN=_r(sn), RN=_r(rn), SU=_r(su), RU=_r(ru), POP=_r(pop), UNIF=_r(unif), ORACLE=_r(orc)),
        infer_gap_SN_POP=_r(infer_gap), infers=infers, no_infer=no_infer,
        novel_graded=dict(SN=_r(sn_nov), RN=_r(rn_nov), rel_gain=_r(rel_gain), sign_frac=_r(sign_frac, 3)),
        structure_adds=structure_adds, refuted_struct=refuted_struct,
        shuffle_gap_SHUF_POP=_r(shuf_gap), shuffle_collapses=shuffle_collapses, shuffle_leaks=shuffle_leaks,
        unbind_gap_RU_POP=_r(unbind_gap), unbind_sane=unbind_sane, ceiling_ok=ceiling_ok,
        pos_controls_ok=pos_controls_ok,
        bands=dict(INFER_MARGIN=INFER_MARGIN, INFER_FLOOR=INFER_FLOOR, REL_STRUCT_GAIN=REL_STRUCT_GAIN,
                   REFUTE_REL=REFUTE_REL, SEED_SIGN_FRAC=SEED_SIGN_FRAC, SHUFFLE_EPS=SHUFFLE_EPS,
                   SHUFFLE_LEAK=SHUFFLE_LEAK, UNBIND_SANITY_EPS=UNBIND_SANITY_EPS),
    )
    return verdict, msg, gates


# ---------------------------------------------------------------------------
# Planted latent-KIND arena for the self-test (concept clustering + cross-relation correlation).
# ---------------------------------------------------------------------------

def build_planted_kind_arena(seed, n_concept=500, n_kind=8, n_rel=6, vals_per_rel=16, peak=1.3):
    """Latent-KIND world -> (h,r,t) label triples. Each kind induces a per-relation PEAKED tail categorical; concepts
    of the same kind share tails (clustering => neighbor + exact-match fire) and correlated across relations
    (structure helps on novel combos). Tails are relation-specific value tokens. Deterministic per seed."""
    rng = np.random.default_rng(seed * 100019 + 7)
    kind_dist = {}
    for kd in range(n_kind):
        kind_dist[kd] = {}
        for r in range(n_rel):
            w = rng.random(vals_per_rel) ** peak
            kind_dist[kd][r] = w / w.sum()
    edges = []
    for c in range(n_concept):
        kd = int(rng.integers(n_kind))
        for r in range(n_rel):
            vi = int(rng.choice(vals_per_rel, p=kind_dist[kd][r]))
            edges.append(("c%d" % c, "r%d" % r, "r%dv%d" % (r, vi)))
    return list(dict.fromkeys(edges))


# ---------------------------------------------------------------------------
# Self-test: apparatus validity on the planted KIND arena (real code path) + validity-preflight.
# ---------------------------------------------------------------------------

def mechanism_selftest(device):
    _prev = torch.get_num_threads()
    torch.set_num_threads(1)
    try:
        return _mechanism_selftest_body(device)
    finally:
        torch.set_num_threads(_prev)


def _mechanism_selftest_body(device):
    cfg = dict(SELFTEST_CFG)
    out = {}
    pool = build_planted_kind_arena(7)
    prep = prepare_corpus(pool, cfg, 7)
    if prep["query_int"].shape[0] < 20:
        return False, {"fail": "planted arena produced too few queries (%d)" % prep["query_int"].shape[0]}
    if prep["leak"] > 0:
        return False, {"fail": "LEAK in self-test split (%d)" % prep["leak"]}
    res, fs = run_corpus(pool, cfg, device, 7, "PLANTED_KIND")
    if fs is None:
        return False, {"fail": "run_corpus invalid: %s" % res.get("invalid")}

    m = res["arm_mrr"]; g = res["graded"]
    n_sigs = len(set(res["arm_sigs"].values()))
    sn_beats_pop = bool(m[SN] - m[POP] >= ST_SN_BEATS_POP)
    neighbor_beats_unbind = bool(m[RN] - m[RU] >= ST_NEIGHBOR_BEATS_UNBIND)
    shuffle_collapses = bool((m[SHUF] - m[POP]) <= ST_SHUFFLE_COLLAPSE)
    struct_novel_gain = bool((g[SN]["novel"] - g[RN]["novel"]) >= ST_STRUCT_NOVEL_GAIN)
    ceiling_ok = bool(m[ORC] >= m[SN] - 1e-6)
    arms_differ = bool(n_sigs >= 5)
    fits_finite = bool(res["diag"]["fits_finite"])
    novel_pop = bool(res["diag"]["n_novel"] >= 3 and res["diag"]["n_seen"] >= 3)

    # VACUOUS-SMOKE guard: neighbor MUST separate from unbind on the planted arena (else arena not answerable)
    nbr_frozen = bool(neighbor_beats_unbind is False)
    assert_discriminator_fires(nbr_frozen, control_name=RU,
                               headline_name="neighbor_beats_unbind_random_synth", run_mode="self_test",
                               extra="on the planted KIND arena random-code NEIGHBOR did NOT beat self-UNBIND -> arena "
                                     "not answerable / apparatus frozen (the a6bbdfd0 readout confound is not testable)")

    v_verdict, _vm, _vg = decisive_verdict([res])

    vp_ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["fit_kge_anchor1", "neighbor_scores", "build_struct_bundles",
                                        "compute_novel_mask"],
         "exercised_entrypoints": ["fit_kge_anchor1", "neighbor_scores", "build_struct_bundles",
                                   "compute_novel_mask"],
         "extra": "self-test fits the REAL additive-map coord source (fit_kge_anchor1) at k=8 on planted (h,r,t) "
                  "triples and runs the REAL neighbor/unbind/stratify/graded pipeline; build_cskg_core_triples is "
                  "the FULL-only CSKG data source (exercised remote via _ensure_cskg), intentionally not in self-test"},
        {"kind": "substrate_signature", "callable_obj": fit_kge_anchor1, "callable_name": "fit_kge_anchor1",
         "kwargs": {"train_edges": None, "N": 1, "n_rel": 1, "k": 8, "device": None, "seed": 7, "epochs": 1,
                    "reciprocal": True, "lr": A1_LR, "n_neg": 32, "batch_size": 2048, "neg_chunk": 16}},
        {"kind": "positive_control",
         "positive_control_passed_headline_gate": bool(sn_beats_pop and neighbor_beats_unbind and struct_novel_gain),
         "control_name": "PLANTED_KIND_MECHANISMS", "headline_name": "neighbor_infers_and_structure_adds_on_novel",
         "extra": "planted KIND arena: STRUCT_NEIGHBOR beats POP, RANDOM_NEIGHBOR beats RANDOM_UNBIND (readout is the "
                  "confound), and STRUCTURED adds over RANDOM on the NOVEL stratum under the graded value metric"},
        {"kind": "metric_moves", "metric_name": "arm_mrr",
         "values": [m[SN], m[RN], m[SU], m[RU], m[POP]],
         "extra": "the arms MOVE on synthetic: SN=%.3f RN=%.3f SU=%.3f RU=%.3f POP=%.3f"
                  % (m[SN], m[RN], m[SU], m[RU], m[POP])},
        {"kind": "negative_control_margin",
         "control_scores": [m[POP], m[RU], m[SHUF]],
         "headline_threshold": m[SN], "higher_is_pass": True, "margin": ST_SN_BEATS_POP, "n_repeats_min": 3,
         "control_name": "POP_RU_SHUF_below_struct_neighbor", "extra":
         "POP (marginal) + RANDOM_UNBIND (a6bbdfd0 op) + SHUFFLE (correlation destroyed) sit below STRUCT_NEIGHBOR "
         "by the MRR margin -> the inference needs the neighbor readout + intact cross-relation correlation"},
        {"kind": "full_gates_exercised",
         "full_fail_closed_gates": ["sn_beats_pop", "neighbor_beats_unbind", "shuffle_collapses",
                                    "struct_novel_gain", "ceiling_ok", "arms_differ", "decisive_verdict"],
         "exercised_gates": ["sn_beats_pop", "neighbor_beats_unbind", "shuffle_collapses", "struct_novel_gain",
                             "ceiling_ok", "arms_differ", "decisive_verdict"],
         "extra": "decisive_verdict=%s at self-test scale" % v_verdict},
    ], run_mode="self_test")

    out.update(
        planted_mrr={a: round(m[a], 5) for a in ALL_ARMS},
        planted_graded_novel={a: round(g[a]["novel"], 5) for a in [RN, SN]},
        n_distinct_sigs=n_sigs, n_novel=res["diag"]["n_novel"], n_seen=res["diag"]["n_seen"],
        sn_beats_pop=sn_beats_pop, neighbor_beats_unbind=neighbor_beats_unbind,
        shuffle_collapses=shuffle_collapses, struct_novel_gain=struct_novel_gain, ceiling_ok=ceiling_ok,
        arms_differ=arms_differ, fits_finite=fits_finite, novel_and_seen_present=novel_pop,
        decisive_selftest_verdict=v_verdict, validity_preflight_ok=bool(vp_ok),
        validity_preflight_declared=["real_code_path", "substrate_signature", "positive_control", "metric_moves",
                                     "negative_control_margin", "full_gates_exercised"],
    )
    ok = bool(sn_beats_pop and neighbor_beats_unbind and shuffle_collapses and struct_novel_gain
              and ceiling_ok and arms_differ and fits_finite and novel_pop)
    return ok, out


# ---------------------------------------------------------------------------
# Core entry.
# ---------------------------------------------------------------------------

def _pick_device(arg):
    if arg == "cpu":
        return torch.device("cpu")
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def core_main(run_mode, device):
    out_dir = get_output_dir(ANCHOR_NAME)
    cfg = dict({"self_test": SELFTEST_CFG, "memsmoke": MEMSMOKE_CFG, "full": FULL_CFG}[run_mode])
    seeds = cfg["seeds"]
    expected_n_units = len(seeds)
    _write_start_marker(out_dir, run_mode, expected_n_units)
    t_start = time.perf_counter()
    hb_path = os.path.join(str(out_dir), "_heartbeat.jsonl")
    ckpt_dir = os.path.join(str(out_dir), "_fit_ckpts")

    def _hb(tag, i):
        with open(hb_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts_iso": datetime.now(timezone.utc).isoformat(),
                                "unit": tag, "idx": i, "elapsed_s": time.perf_counter() - t_start}) + "\n")

    _log("device=%s run_mode=%s seeds=%s n_dim=%s k=%s epochs=%s m_nn=%s"
         % (device, run_mode, seeds, cfg["n_dim"], cfg["k"], cfg.get("epochs"), cfg["m_nn"]))

    st_ok, st_res = mechanism_selftest(device)
    _log("mechanism_selftest ok=%s | planted_mrr=%s neighbor_beats_unbind=%s struct_novel_gain=%s shuffle_collapses=%s vp_ok=%s"
         % (st_ok, st_res.get("planted_mrr"), st_res.get("neighbor_beats_unbind"), st_res.get("struct_novel_gain"),
            st_res.get("shuffle_collapses"), st_res.get("validity_preflight_ok")))
    _hb("selftest", 0)
    if not st_ok:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED: %s"
                        % {kk: st_res.get(kk) for kk in ("sn_beats_pop", "neighbor_beats_unbind",
                           "shuffle_collapses", "struct_novel_gain", "ceiling_ok", "arms_differ", "fits_finite")},
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(out_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS RELATIONAL_INFERENCE_NEIGHBOR_VS_UNBIND: on the planted KIND arena the NEIGHBOR "
                        "readout beats self-UNBIND (random codes) -> a6bbdfd0's chance was the readout; STRUCT_NEIGHBOR "
                        "beats the marginal floor; STRUCTURED adds over RANDOM on the NOVEL stratum under the graded "
                        "value metric; the SHUFFLE control collapses to marginal; 6 validity-preflight checks declared",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    if not _ensure_cskg():
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="CSKG data absent and self-acquire failed", summary="cskg missing",
            elapsed_s=time.perf_counter() - t_start))
        raise SystemExit(1)

    per_seed = []
    unit_failures = []
    for si, seed in enumerate(seeds):
        try:
            ts = time.time()
            train_lbl, valid_lbl, test_lbl, prov = build_cskg_core_triples(
                cfg["cskg_max_lines"], cfg["k_core"], cfg["cskg_max_nodes"], seed)
            pool = list(train_lbl) + list(valid_lbl) + list(test_lbl)
            _log("cskg seed=%d core_nodes=%d core_edges=%d rels=%d pool_edges=%d"
                 % (seed, prov["n_core_nodes"], prov["n_core_edges"], prov["n_rel_tokens"], len(pool)))
            res, fs = run_corpus(pool, cfg, device, seed, "CSKG_CORE_HELDOUT_RELATION", ckpt_dir=ckpt_dir)
            if res.get("invalid"):
                raise RuntimeError("invalid corpus: %s" % res["invalid"])
            if int(res["n_query"]) < cfg.get("min_query", 40):
                raise RuntimeError("held-out query edges too few (%d)" % int(res["n_query"]))
            if res["leak"] > 0:
                raise RuntimeError("LEAKAGE seed=%d leak=%d" % (seed, res["leak"]))
            if len(set(res["arm_sigs"].values())) < 5:
                raise RuntimeError("ARMS_MUST_DIFFER_META_RULE_AF seed=%d" % seed)
            if not res["diag"]["fits_finite"]:
                raise RuntimeError("additive fit non-finite seed=%d" % seed)
            if res["diag"]["n_novel"] < 3 or res["diag"]["n_seen"] < 3:
                raise RuntimeError("stratum too small seed=%d novel=%d seen=%d"
                                   % (seed, res["diag"]["n_novel"], res["diag"]["n_seen"]))
            res["cskg_provenance"] = prov
            per_seed.append(res)
            write_partial(out_dir, seed, dict(seed=seed, metrics=res, run_mode=run_mode))
            _log("seed=%d nq=%d novel=%d seen=%d | SN=%s RN=%s SU=%s RU=%s POP=%s ORACLE=%s | novelgraded SN=%s RN=%s | (%.1fs)"
                 % (seed, res["n_query"], res["diag"]["n_novel"], res["diag"]["n_seen"],
                    _fmt(res["arm_mrr"][SN]), _fmt(res["arm_mrr"][RN]), _fmt(res["arm_mrr"][SU]),
                    _fmt(res["arm_mrr"][RU]), _fmt(res["arm_mrr"][POP]), _fmt(res["arm_mrr"][ORC]),
                    _fmt(res["graded"][SN]["novel"]), _fmt(res["graded"][RN]["novel"]), time.time() - ts))
            _hb("cskg", si + 1)
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fc = type(e).__name__
            unit_failures.append(dict(seed=seed, failure_class=fc, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, fc, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(out_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), unit_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            unit_failures=unit_failures, mechanism_selftest=st_res))
        raise SystemExit(1)

    verdict, verdict_msg, gates = decisive_verdict(per_seed)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(seeds), seeds=seeds,
                   config=cfg, gates=gates, mechanism_selftest=st_res, unit_failures=unit_failures,
                   per_seed=per_seed)
    write_metrics(out_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "memsmoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else args.run_mode
    if not args.self_test and args.run_mode == "full":
        _env_mode = os.environ.get("HDLAB_RUN_MODE", "").strip().lower()
        if _env_mode in ("self_test", "memsmoke", "full"):
            run_mode = _env_mode
        # The prod runner forces HDLAB_RUN_MODE=full; a MEMSMOKE is triggered by naming the queue entry with
        # 'memsmoke' (runner sets HDLAB_EXP_NAME=<entry name>, which also isolates the output dir). Runner-compatible.
        if "memsmoke" in os.environ.get("HDLAB_EXP_NAME", "").lower():
            run_mode = "memsmoke"
    device = _pick_device(args.device)
    out_dir = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except (AttributeError, ValueError):
        pass
    try:
        core_main(run_mode, device)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(out_dir, e)
        raise


if __name__ == "__main__":
    main()
