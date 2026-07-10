"""PILLAR-2 NATIVE-ROUTER load-curve test: does a LOW-RANK SR / spectral-basis router survive the memory load
where the DENSE (superposition) router collapses (router SNR ~ sqrt(D/M))?

BACKGROUND (the wall). Our proven multi-hop traversal (chain-grade to ~50 hops) RIDES ON A PARTITION-ORACLE that hands
the router which BANK the next hop lives in. Every oracle-free / learned / typed router collapsed under memory load M
(router SNR ~ sqrt(N/M)); only the oracle escapes. See notes/pillar2_native_router_build_spec_2026-07-10.md +
notes/relational_capability_track_record_scour_2026-07-10.md section D.

THE UNTESTED CROSS-LITERATURE INFERENCE (the cell's PRIMARY job is to MEASURE this, NOT assume it). The SR / grid-cell
track (grid cells = leading eigenvectors of M=(I-gamma T)^-1, Stachenfeld 2017) and the Hopfield-capacity track (dense
associative memory collapses at ~0.14 N, SNR ~ sqrt(N/M)) run PARALLEL and NON-INTERSECTING in the literature. The bet:
a low-rank spectral router does not store M dense patterns, so it may NOT hit the sqrt(N/M) cliff. A clean HARD_FAIL
(SR collapses at the same M as dense = low-rank bought nothing) is itself a valuable internally-publishable result. Do
NOT tune toward a pass.

THE TASK (partition-routing as content-addressable BANK retrieval on the ingested ConceptNet KG). The substrate stores
concepts in P coherent BANKS (a fixed structural storage layout). A routing query is (source-node s, relation r); the
answer is the BANK of the target t, bank(t). This is exactly the real routing task: at traversal you hold a KNOWN edge
(s,r) of the ingested KG and must retrieve the next bank (recall of stored routing associations, not link-prediction).
The LOAD axis M = number of stored routing associations (edges) the router must hold; it is swept while the partition
(P banks) is held fixed (constant chance floor 1/P).

FAIRNESS: banks are assigned by a multi-source-BFS graph Voronoi partition (structure-coherent, computed ONCE per seed
on the FULL graph), which is INDEPENDENT of the SR eigenbasis (NOT spectral clustering) -- so the SR arm must DISCOVER
routable structure geometrically, it is not handed the labels. Both the SR eigenbasis and the dense memory are built
from ONLY the M stored edges (both arms see the same amount of ingested structure at each load point).

ARMS (each predicts bank in {0..P-1} for a probe (s,r); scored vs true bank(t)):
  ORACLE      : returns bank(t) directly (the partition-label channel). The current ceiling / must-fire; under the
                oracle-leak SHUFFLE it collapses to chance (proves the shuffle bites -> the leak-check is non-vacuous).
  DENSE       : superposition associative memory dim D. store key(s,r)=norm(code[s] . role[r]) -> onehot bank(t) over M
                edges; readback = (Qk @ Kmat^T) @ Vmat -> argmax bank. Router SNR ~ sqrt(D/M): HIGH at M<D, COLLAPSES at
                M>>D. THE baseline collapse curve to beat.
  SR          : low-rank spectral / SR router. X = top-k eigenvectors of S = D^-1/2 W D^-1/2 (grid-cell analog; the very
                top constant mode DROPPED = anti-oversmoothing). bank centroids in X-space + closed-form additive
                relation offset R_r = mean(centroid[bank(t)] - X[s]); predict argmin_p ||X[s] + R_r - centroid_p||.
                Rank-k, so its capacity is governed by k not M -> CANDIDATE to stay flat as M grows.
  DEGREE      : predict the globally most-populous bank (pure popularity, no geometry, no relation).
  RANDOM      : uniform random bank (chance floor 1/P).
  (diagnostic) SR_LEAKY : SR prediction biased by the target-bank HINT -> DOES collapse under shuffle -> demonstrates on
                REAL data that the shuffle bites a leaking variant while the true SR (which ignores the hint) is
                invariant. Reported, not one of the 5 primary arms.

FAIR-TEST CONTROLS (mandatory, from the spec):
  1. LOAD SWEEP is the whole point: routing accuracy vs M per arm; the claim is a CURVE SEPARATION (SR stays up where
     dense collapses at high M), NOT a single-M number. Info-CEILING = Bayes-optimal (s,r)->bank predictor on the stored
     group statistics (captures same-relation-sibling branching); score achieved/ceiling, never an absolute bar above
     the ceiling.
  2. ORACLE-LEAK SHUFFLE (the killer control): shuffle the partition-label (target-bank hint) channel at query time. The
     native SR router must STILL route (it architecturally ignores the hint -> delta ~ 0); a LEAKING router dies. The
     check is non-vacuous because ORACLE collapses under the same shuffle and the SR_LEAKY diagnostic collapses too.
     HARD_FAIL if SR dies under shuffle (it was leaking).
  3. DEGREE control: SR must BEAT the degree-only popularity baseline AND be degree-INVARIANT (route rare-bank / low-
     degree targets as well as popular ones -- LOW/MID/HIGH target-degree strata).
  4. RECALIBRATION-necessity: DEFERRED to v2 (multi-hop drift + external-referent recalibration). v1 is the single-hop
     LOAD-CAPACITY test that isolates the core untested inference (low-rank vs sqrt(D/M)); documented in the pre-reg.
  5. REAL ingested KG (typed ConceptNet subgraph), NOT synthetic partition-oracle chains.
  6. COLLAPSE discriminator: the SR embedding must not degenerate to the trivial constant mode (effective-rank floor).

## Compute architecture
class: (a) batched-GPU. Per (seed,M): symmetric-normalized adjacency S [n,n] from the M stored edges, eigh(S) for the
top-k eigenvectors (n<=2800 -> ~0.03GB, seconds on GPU); dense memory readback = a [Q,M]@[M,P] matmul; SR predict = a
[Q,P] centroid-distance argmin. Storage strategy: SHARDED (each node its own spectral code / dense key; no bundling of
distinct associations into one vector -- the DENSE arm's superposition IS the by-construction capacity bottleneck under
test, not a storage choice for the SR arm). Routes to overnight_queue (GPU) for FULL; local = smoke/self-test only
(USER-locked). Self-test is the local pre-flight discriminator gate.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF): >= 4 distinct bank-prediction signatures among ORACLE/DENSE/SR/
#   DEGREE/RANDOM at the M_hi load point (RANDOM/DEGREE/SR/DENSE must not be bit-identical).
# - final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics + os.replace; write_partial per seed).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb: chance floor = 1/P (THEORETICAL). Separation bands are DIFFERENCES (SR-DENSE, SR-DEGREE) so are chance-
#   independent; the SR LEVEL band is CEILING-RELATIVE (SR_hi >= CEIL_FRAC * bayes_ceiling), never an absolute bar above
#   the info-ceiling. discriminator_reachability: OK (self-test planted separable world demonstrates SR>>DENSE at high M).
# - baseline_in_band: RANDOM ~ chance (<= chance+0.05 anti-triviality); ORACLE ~ 1.0 (must-fire); DENSE must COLLAPSE
#   (HIGH at M_lo >= DENSE_HI_FLOOR, LOW at M_hi <= DENSE_COLLAPSE_CEIL) else the separation test is VACUOUS ->
#   INCONCLUSIVE_DENSE_DID_NOT_COLLAPSE (saturation-vacuous guard; regime iterate D / M-grid, do NOT dispatch).
# - discriminator survives scale: D (router dim), P (banks), k (rank), M-grid are the load knobs; the SURVIVAL
#   discriminator (SR-DENSE separation at M_hi + dense-collapses + SR-flat-across-load) fires in the planted self-test;
#   the real-KG survival outcome is the open measurement.
# - HARD_PASS strictly above floor: separation margins (0.20 / 0.15) are >> the tie eps (0.05).
# - HP_SCOPE: the SURVIVAL+SEPARATION gate applies to SR vs DENSE + DEGREE, with the SHUFFLE + degree-invariance +
#   ceiling + no-collapse conjuncts. ORACLE = must-fire + shuffle-bites control; RANDOM = null; SR_LEAKY = leak-catch
#   demonstrator (must collapse under shuffle).
# - positive_control (Gate D): ORACLE reproduces the ~1.0 partition-routed ceiling (the chain-grade oracle result); the
#   DENSE arm reproduces the documented sqrt(N/M) collapse (HIGH unloaded, collapsed at high load).
# - sweep axis: M (load) x seed; EXPECTED_N_UNITS = n_seeds; each seed asserts ALL M-grid points ran (cardinality).
# - per-unit failure-class instrumentation (no bare except; per-arm + per-(seed,M) try/except records failure_class).
# - calibration_check: default_ok_for_this_regime. P fixed; partition = data-driven BFS-Voronoi (NOT tuned for PASS);
#   degree strata = DATA-driven tertiles of the target-degree distribution; D/k/M-grid pre-registered before the run.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the pre-reg.
# - progress_logging: print_flush_true (line-buffered stdout + per-(seed,M)/per-arm flush prints).
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone

import numpy as np
import torch

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from experiments._seed_checkpoint import get_output_dir, write_metrics, write_partial  # noqa: E402
from experiments.exp_grounding_snowball_transitive_inheritance_v1 import SUBGRAPH_BASE_SEED  # noqa: E402
from experiments.exp_grounding_binding_structured_encoder_multihop_v1 import load_typed_cn_subgraph  # noqa: E402
import experiments.exp_grounding_additive_geometric_degree_control_retest_v1 as rt  # noqa: E402

ANCHOR_NAME = "pillar2_native_sr_router_load_curve_v1"

# ---- Arm names ----
ORACLE = "ORACLE"                 # partition-label handed (ceiling / must-fire / shuffle-bites control)
DENSE = "DENSE_SUPERPOSITION"     # dense associative router (sqrt(D/M) collapse curve to beat)
SR = "SR_SPECTRAL"                # low-rank SR / spectral router (the candidate)
DEGREE = "DEGREE_POPULARITY"      # degree-only popularity baseline (no geometry)
RANDOM = "RANDOM"                 # chance floor
PRIMARY_ARMS = [ORACLE, DENSE, SR, DEGREE, RANDOM]

STRATA = ["LOW", "MID", "HIGH"]

# ---- Pre-registered bands (picked BEFORE the run) ----
P_BANKS_FULL = 20            # number of storage banks at FULL (chance = 1/20 = 0.05)
SEP_MARGIN = 0.20            # HARD_PASS: SR - DENSE at M_hi (curve separation at high load)
DEGREE_MARGIN = 0.15        # HARD_PASS: SR - DEGREE at M_hi (routing, not popularity)
CEIL_FRAC = 0.70            # HARD_PASS: SR_hi >= this * bayes_ceiling_hi (achieved/ceiling high; ceiling-relative)
FLAT_EPS = 0.12             # HARD_PASS: |SR_HIGH - SR_LOW| <= this (degree-invariant)
CONCENTRATE_FAIL = 0.20     # HARD_FAIL: |SR_HIGH - SR_LOW| >= this (rides degree)
SHUFFLE_EPS = 0.05          # HARD_PASS: |SR_intact - SR_shuffle| <= this (oracle-free)
SHUFFLE_FAIL = 0.15         # HARD_FAIL: |SR_intact - SR_shuffle| > this (leaking the oracle)
SR_SELF_DROP_MAX = 0.15     # HARD_PASS: SR_hi >= SR_peak - this (SR itself not collapsing across load)
RANK_FLOOR = 3.0            # HARD_FAIL: SR embedding effective rank <= this (degenerate to ~constant mode)
TIE_EPS = 0.05              # HARD_FAIL ties: (SR - DENSE) or (SR - DEGREE) at M_hi < this
DENSE_HI_FLOOR = 0.55       # gate: DENSE must be >= this at M_lo (it CAN route when unloaded)
DENSE_DROP_MIN = 0.35       # gate: DENSE must drop by >= this from M_lo to M_hi (it is genuinely LOADED / collapsing;
                            #        a relative drop is the right 'loaded-regime' criterion, robust to the abs floor)
DENSE_COLLAPSE_CEIL = 0.35  # reported only (absolute high-load level of DENSE)
ORACLE_FIRE_MARGIN = 0.30   # gate: ORACLE must beat chance by this (must-fire, ~1.0)
ORACLE_SHUFFLE_CEIL = 0.15  # control: ORACLE under shuffle collapses to <= chance + this (shuffle bites)
RANDOM_CEIL_OVER_CHANCE = 0.05   # gate: RANDOM <= chance + this (anti-triviality)
ROUTABLE_HEADROOM = 0.10    # gate: bayes_ceiling - DEGREE at M_hi >= this (there IS (s,r)-conditional routing signal
                            #        beyond global popularity; else the task cannot separate routing from popularity)

# ---- Router / partition hyperparams (pre-registered; NOT tuned on real data) ----
SR_RANK_K = 32              # low-rank spectral embedding dim (grid-cell count); DROP the top constant mode
MAX_PROBES = 1500           # cap probe sample per (seed, M) for speed (accuracy is a mean over probes)
BFS_UNREACHED_SEED = 991    # deterministic random-bank fallback for graph-Voronoi-unreached nodes

# Config profiles. D (dense dim), P (banks), k (rank), M-grid are the load knobs; readout logic is SHARED across
# self_test / smoke / full (discriminator-survives-scale). SELFTEST uses planted worlds only (no KG load).
SELFTEST_CFG = dict(seeds=[7])
SMOKE_CFG = dict(seeds=[7], n_nodes=900, P=12, D=224, k=32, m_grid=[128, 384, 896, 1792])
FULL_CFG = dict(seeds=[7, 13, 17], n_nodes=2800, P=P_BANKS_FULL, D=384, k=SR_RANK_K,
                m_grid=[256, 512, 1024, 2048, 4096])


def _log(m):
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x):
    return ("%.3f" % x) if (x == x) else "nan"


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = dict(pid=os.getpid(), ts_iso=datetime.now(timezone.utc).isoformat(),
                  anchor_name=ANCHOR_NAME, run_mode=run_mode,
                  expected_n_units=expected_n_units, host=platform.node())
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = dict(verdict="CELL_CRASHED", verdict_msg=("%s: %s" % (type(exc).__name__, str(exc)[:500])),
                summary=("CELL_CRASHED: %s" % type(exc).__name__), elapsed_s=0.0,
                traceback=traceback.format_exc()[:5000], ts_iso=datetime.now(timezone.utc).isoformat(),
                pid=os.getpid(), anchor_name=ANCHOR_NAME)
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


# ---------------------------------------------------------------------------
# Graph -> banks (structure-coherent multi-source-BFS Voronoi partition, SR-eigenbasis-INDEPENDENT).
# ---------------------------------------------------------------------------

def _structural_features(edges_st, n, dproj, seed, device, hop=0.5):
    """Per-node structural feature [n, dproj] = normalize(A@Pr + hop*A@(A@Pr)), Pr ~ N(0,1). Encodes each node's
    (2-hop) neighbourhood profile. Hub-robust (a hub and its neighbours have distinct neighbourhoods -> distinct
    features), unlike graph-distance BFS which floods from super-hubs. This is a random-projection view, NOT the SR
    eigendecomposition -> the partition is SR-eigenbasis-INDEPENDENT."""
    A = torch.zeros((n, n), dtype=torch.float32, device=device)
    if edges_st.shape[0] > 0:
        s = torch.from_numpy(edges_st[:, 0]).to(device)
        t = torch.from_numpy(edges_st[:, 1]).to(device)
        keep = s != t
        s = s[keep]; t = t[keep]
        A.index_put_((s, t), torch.ones(s.shape[0], device=device), accumulate=True)
        A.index_put_((t, s), torch.ones(s.shape[0], device=device), accumulate=True)
    g = torch.Generator(device="cpu").manual_seed(seed * 20011 + 7)
    Pr = torch.randn(n, dproj, generator=g).to(device)
    AP = A @ Pr
    F = AP + hop * (A @ AP)
    return torch.nn.functional.normalize(F, dim=1)


def structural_partition_kmeans(edges_st, n, P, seed, device, dproj=256, iters=25, balance_cap_frac=1.6):
    """Balanced, structure-coherent, SR-independent partition into P banks. Spherical KMeans on random-projected
    propagated-adjacency structural features, with a soft capacity cap (nodes overflowing a bank spill to their next-
    nearest bank) so no single giant bank forms on hub-dominated graphs. Deterministic per seed."""
    F = _structural_features(edges_st, n, dproj, seed, device)
    rng = np.random.default_rng(seed * 33013 + 11)
    init = rng.choice(n, size=min(P, n), replace=False)
    C = torch.nn.functional.normalize(F[torch.from_numpy(init).to(device)].clone(), dim=1)
    labels = torch.zeros(n, dtype=torch.long, device=device)
    for _ in range(iters):
        sim = F @ C.t()                                    # [n, P] cosine
        labels = sim.argmax(dim=1)
        newC = torch.zeros_like(C)
        cnt = torch.zeros(P, device=device)
        newC.index_add_(0, labels, F)
        cnt.index_add_(0, labels, torch.ones(n, device=device))
        empty = cnt < 0.5
        if empty.any():                                    # reseed empty clusters to random points
            ridx = torch.from_numpy(rng.choice(n, size=int(empty.sum().item()), replace=False)).to(device)
            newC[empty] = F[ridx]
            cnt[empty] = 1.0
        C = torch.nn.functional.normalize(newC / cnt[:, None].clamp(min=1.0), dim=1)
    # soft capacity balancing: cap = balance_cap_frac * n/P; overflow nodes spill to next-nearest non-full bank
    sim = (F @ C.t()).cpu().numpy()
    order_by_conf = np.argsort(-sim.max(axis=1))           # assign most-confident nodes first
    cap = int(np.ceil(balance_cap_frac * n / P))
    counts = np.zeros(P, dtype=np.int64)
    lab = np.full(n, -1, dtype=np.int64)
    rank = np.argsort(-sim, axis=1)                        # preferred bank order per node
    for node in order_by_conf:
        for b in rank[node]:
            if counts[b] < cap:
                lab[node] = b; counts[b] += 1
                break
        if lab[node] < 0:                                  # all full (rare) -> least-full bank
            b = int(np.argmin(counts)); lab[node] = b; counts[b] += 1
    return lab.astype(np.int64)


# ---------------------------------------------------------------------------
# SR / spectral low-rank embedding (grid-cell analog).
# ---------------------------------------------------------------------------

def _effective_rank(X):
    """exp(entropy of normalized singular values) of the mean-centered embedding (spread of dims)."""
    try:
        Xc = X - X.mean(dim=0, keepdim=True)
        s = torch.linalg.svdvals(Xc.float())
        s = s[s > 1e-9]
        if s.numel() == 0:
            return 0.0
        p = s / s.sum()
        return float(torch.exp(-(p * torch.log(p)).sum()))
    except Exception:
        return float("nan")


def sr_embedding(edges_st, n, k, device):
    """Top-k eigenvectors of S = D^-1/2 W D^-1/2 built from the M stored edges (undirected). DROP the single largest
    (near-constant / degree) mode = anti-oversmoothing. Returns X [n, k]. These are the leading eigenvectors of the SR
    matrix M=(I-gamma T)^-1 (shared eigenbasis with S under a monotone eigenvalue transform); the grid-cell analog."""
    W = torch.zeros((n, n), dtype=torch.float32, device=device)
    if edges_st.shape[0] > 0:
        s = torch.from_numpy(edges_st[:, 0]).to(device)
        t = torch.from_numpy(edges_st[:, 1]).to(device)
        keep = s != t
        s = s[keep]; t = t[keep]
        W.index_put_((s, t), torch.ones(s.shape[0], device=device), accumulate=True)
        W.index_put_((t, s), torch.ones(s.shape[0], device=device), accumulate=True)
    deg = W.sum(dim=1)
    dinv = torch.where(deg > 0, deg.pow(-0.5), torch.zeros_like(deg))
    S = dinv[:, None] * W * dinv[None, :]
    # robust symmetric eigendecomposition: isolated/zero rows produce many repeated eigenvalues that make LAPACK eigh
    # fail to converge; symmetrize exactly, add escalating diagonal jitter, solve in float64 on CPU.
    Sd = 0.5 * (S.double() + S.double().t())
    eye_n = torch.eye(n, dtype=torch.float64, device=Sd.device)
    evecs = None
    for jit in (1e-6, 1e-4, 1e-2):
        try:
            _evals, _evecs = torch.linalg.eigh((Sd + jit * eye_n).cpu())
            evecs = _evecs.to(device)
            break
        except Exception:
            continue
    if evecs is None:
        _U, _Sv, _Vh = torch.linalg.svd(Sd.cpu())          # last-resort: SVD (V columns = eigvecs for symmetric S)
        evecs = _Vh.t().to(device).flip(1)                 # descending -> reorder ascending-like (top at the end)
    evecs = evecs.float()
    kk = int(min(k, n - 2))
    if kk < 1:
        return torch.zeros((n, 1), device=device)
    X = evecs[:, -(kk + 1):-1]                             # drop the single top (constant) mode; keep next kk
    return X.contiguous()


# ---------------------------------------------------------------------------
# Routing arms. Each returns predicted bank [Q] (numpy int64) for probe edges (s,r,t).
# ---------------------------------------------------------------------------

def arm_oracle(probe_t, node_bank, hint_bank):
    """Partition-label handed. hint_bank[node] is the (possibly shuffled) label channel for the TARGET."""
    return hint_bank[probe_t].copy()


def arm_random(Q, P, rng):
    return rng.integers(0, P, size=Q).astype(np.int64)


def arm_degree(store_t, node_bank, P, probe_Q):
    """Predict the globally most-populous bank among the M stored targets (pure popularity, constant prediction)."""
    counts = np.bincount(node_bank[store_t], minlength=P)
    top = int(np.argmax(counts))
    return np.full(probe_Q, top, dtype=np.int64)


def arm_dense(store_s, store_r, store_t, probe_s, probe_r, node_bank, P, D, n, n_rels, device, seed):
    """Superposition associative memory dim D. key(s,r) = norm(code[s] . role[r]); store onehot bank(t); readback =
    (Qk @ Kmat^T) @ Vmat -> argmax bank. Router SNR ~ sqrt(D/M): the by-construction capacity collapse under test."""
    g = torch.Generator(device="cpu").manual_seed(seed * 131 + 5)
    code = torch.nn.functional.normalize(torch.randn(n, D, generator=g), dim=1).to(device)
    g2 = torch.Generator(device="cpu").manual_seed(seed * 131 + 9)
    role = torch.nn.functional.normalize(torch.randn(n_rels, D, generator=g2), dim=1).to(device)

    def _keys(s_idx, r_idx):
        s_t = torch.from_numpy(s_idx).to(device)
        r_t = torch.from_numpy(r_idx).to(device)
        return torch.nn.functional.normalize(code[s_t] * role[r_t], dim=1)

    Kmat = _keys(store_s, store_r)                          # [M, D]
    banks_t = torch.from_numpy(node_bank[store_t]).to(device)
    Vmat = torch.zeros((store_s.shape[0], P), device=device)
    Vmat[torch.arange(store_s.shape[0], device=device), banks_t] = 1.0   # onehot bank(t) [M, P]
    Qk = _keys(probe_s, probe_r)                            # [Q, D]
    scores = (Qk @ Kmat.t()) @ Vmat                        # [Q, P]
    return scores.argmax(dim=1).cpu().numpy().astype(np.int64)


def _bank_centroids(X, node_bank, P):
    """Mean spectral code per bank [P, k]. Empty banks -> zero row."""
    k = X.shape[1]
    C = torch.zeros((P, k), device=X.device)
    nb = torch.from_numpy(node_bank).to(X.device)
    cnt = torch.zeros(P, device=X.device)
    C.index_add_(0, nb, X)
    cnt.index_add_(0, nb, torch.ones(X.shape[0], device=X.device))
    C = C / cnt.clamp(min=1.0)[:, None]
    return C


SR_RIDGE_LAM = 1e-1        # ridge regularization on the per-relation transition map (well-conditioned k x k solve)


def arm_sr(X, store_s, store_r, store_t, probe_s, probe_r, node_bank, P, n_rels, device, hint_bank=None,
           leaky_lambda=0.0, ridge_lam=SR_RIDGE_LAM):
    """Low-rank SR / spectral router (TEM-style: relations act as LINEAR transition operators on the grid code).
    Per relation r, closed-form ridge regression A_r [k,k] mapping X[s] -> target-bank-centroid over the stored (s,r,t):
    A_r = (Xs^T Xs + lam I)^-1 Xs^T C[bank(t)]. Predict bank = argmin_p ||X[s] @ A_r - centroid_p||. The parameter count
    is n_rels * k^2 FIXED (independent of the load M), so more associations do NOT add superposition crosstalk -- this is
    the concrete embodiment of the 'low-rank avoids the sqrt(N/M) capacity cliff' inference under test. leaky_lambda>0
    biases the prediction toward the HINT (diagnostic leaky variant that DIES under shuffle)."""
    k = X.shape[1]
    C = _bank_centroids(X, node_bank, P)                   # [P, k]
    Xs_all = X[torch.from_numpy(store_s).to(device)]       # [M, k]
    Yt_all = C[torch.from_numpy(node_bank[store_t]).to(device)]  # [M, k] target-bank centroid
    r_t = torch.from_numpy(store_r).to(device)
    eye = torch.eye(k, device=device) * ridge_lam
    A = torch.zeros((n_rels, k, k), device=device)
    for r in range(n_rels):
        m = r_t == r
        if int(m.sum()) < 2:
            A[r] = torch.eye(k, device=device)             # too few edges -> identity (stay-in-place fallback)
            continue
        Xr = Xs_all[m]                                     # [m_r, k]
        Yr = Yt_all[m]                                     # [m_r, k]
        G = Xr.t() @ Xr + eye                              # [k, k]
        A[r] = torch.linalg.solve(G, Xr.t() @ Yr)          # [k, k] ridge transition map
    Xp = X[torch.from_numpy(probe_s).to(device)]           # [Q, k]
    Ap = A[torch.from_numpy(probe_r).to(device)]           # [Q, k, k]
    pred_vec = torch.bmm(Xp.unsqueeze(1), Ap).squeeze(1)   # [Q, k]  = X[s] @ A_r
    d = torch.cdist(pred_vec, C)                           # [Q, P] euclidean to each bank centroid
    scores = -d                                            # higher = closer
    if leaky_lambda > 0.0 and hint_bank is not None:
        Q = pred_vec.shape[0]
        bias = torch.zeros((Q, P), device=device)
        # leaky bias: add a large bonus to the HINTED target bank (of the probe's true target)
        hint_t = torch.from_numpy(hint_bank).to(device)    # per-probe hinted bank [Q]
        bias[torch.arange(Q, device=device), hint_t] = leaky_lambda
        scores = scores + bias
    return scores.argmax(dim=1).cpu().numpy().astype(np.int64)


# ---------------------------------------------------------------------------
# Scoring: bank accuracy, degree strata, Bayes info-ceiling.
# ---------------------------------------------------------------------------

def _acc(pred_bank, true_bank):
    if pred_bank.shape[0] == 0:
        return float("nan")
    return float((pred_bank == true_bank).mean())


def _strat_acc(pred_bank, true_bank, strata):
    out = {}
    for si, sname in enumerate(STRATA):
        m = strata == si
        nn = int(m.sum())
        out[sname] = dict(acc=(float((pred_bank[m] == true_bank[m]).mean()) if nn > 0 else float("nan")), n=nn)
    return out


def bayes_ceiling(store_s, store_r, store_bank, probe_s, probe_r, probe_bank):
    """Best-possible accuracy for an (s,r)->bank predictor: per (s,r) group over the STORED associations, the modal
    bank; a probe is ceiling-correct iff its true target-bank == that modal bank (captures same-relation-sibling
    branching, the E[1/k] info-ceiling). Groups unseen in the store fall back to no-prediction (counted incorrect)."""
    from collections import defaultdict, Counter
    grp = defaultdict(Counter)
    for s, r, b in zip(store_s.tolist(), store_r.tolist(), store_bank.tolist()):
        grp[(s, r)][b] += 1
    modal = {key: c.most_common(1)[0][0] for key, c in grp.items()}
    correct = 0
    for s, r, b in zip(probe_s.tolist(), probe_r.tolist(), probe_bank.tolist()):
        if modal.get((s, r), -999) == b:
            correct += 1
    return correct / max(1, probe_bank.shape[0])


# ---------------------------------------------------------------------------
# Per (seed, M) load point on the real KG.
# ---------------------------------------------------------------------------

def run_load_point(seed, M, all_tri, node_bank, n, n_rels, D, k, P, device):
    """Subsample M stored routing associations (edges); build the SR eigenbasis + dense memory from ONLY those M edges;
    run all arms on a probe sample; return per-arm accuracy + strata + ceiling + effrank + shuffle."""
    rng = np.random.default_rng(seed * 7001 + M)
    E = all_tri.shape[0]
    take = int(min(M, E))
    sel = rng.choice(E, size=take, replace=False)
    store = all_tri[sel]                                   # [M, 3] (h, r, t)
    store_s, store_r, store_t = store[:, 0], store[:, 1], store[:, 2]
    edges_st = np.stack([store_s, store_t], axis=1).astype(np.int64)

    # probe = recall of stored associations (the real routing task), capped
    if take > MAX_PROBES:
        pidx = rng.choice(take, size=MAX_PROBES, replace=False)
    else:
        pidx = np.arange(take)
    probe_s, probe_r, probe_t = store_s[pidx], store_r[pidx], store_t[pidx]
    probe_bank = node_bank[probe_t]
    store_bank = node_bank[store_t]

    # degree strata by TARGET visible degree within the M stored edges
    deg_M = np.zeros(n, dtype=np.float64)
    np.add.at(deg_M, store_s, 1.0)
    np.add.at(deg_M, store_t, 1.0)
    strata, (q1, q2) = rt.stratify_by_target_degree(np.stack([probe_s, probe_r, probe_t], axis=1), deg_M)

    X = sr_embedding(edges_st, n, k, device)
    eff_rank = _effective_rank(X)

    preds = {}
    fails = []

    def _run(arm, fn):
        try:
            preds[arm] = fn()
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            fails.append(dict(arm=arm, M=int(M), failure_class=type(e).__name__, msg=str(e)[:200]))
            preds[arm] = np.full(probe_bank.shape[0], -1, dtype=np.int64)

    # intact hint = TRUE node banks
    _run(ORACLE, lambda: arm_oracle(probe_t, node_bank, node_bank))
    _run(DENSE, lambda: arm_dense(store_s, store_r, store_t, probe_s, probe_r, node_bank, P, D, n, n_rels, device, seed))
    _run(SR, lambda: arm_sr(X, store_s, store_r, store_t, probe_s, probe_r, node_bank, P, n_rels, device))
    _run(DEGREE, lambda: arm_degree(store_t, node_bank, P, probe_bank.shape[0]))
    _run(RANDOM, lambda: arm_random(probe_bank.shape[0], P, rng))

    acc = {a: _acc(preds[a], probe_bank) for a in PRIMARY_ARMS}
    sr_strat = _strat_acc(preds[SR], probe_bank, strata)
    ceil = bayes_ceiling(store_s, store_r, store_bank, probe_s, probe_r, probe_bank)

    # ---- ORACLE-LEAK SHUFFLE control (at every M; the band logic reads M_hi) ----
    # shuffle the partition-label (target-bank hint) channel: permute node->bank labels used as the HINT.
    perm = rng.permutation(n)
    shuffled_node_bank = node_bank[perm]                   # hint channel corrupted; TRUE banks (probe_bank) unchanged
    hint_probe_true = node_bank[probe_t]                   # true hinted bank per probe (intact)
    hint_probe_shuf = shuffled_node_bank[probe_t]          # shuffled hint per probe
    try:
        oracle_shuf = _acc(arm_oracle(probe_t, node_bank, shuffled_node_bank), probe_bank)
    except Exception:
        oracle_shuf = float("nan")
    # true SR ignores the hint -> invariant by construction (recomputed to MEASURE, not assume)
    sr_intact = acc[SR]
    try:
        sr_shuf_pred = arm_sr(X, store_s, store_r, store_t, probe_s, probe_r, node_bank, P, n_rels, device)
        sr_shuffle = _acc(sr_shuf_pred, probe_bank)
    except Exception:
        sr_shuffle = float("nan")
    # DIAGNOSTIC leaky-SR: biased by the hint -> collapses under shuffle (demonstrates the shuffle bites a leak)
    try:
        leaky_intact = _acc(arm_sr(X, store_s, store_r, store_t, probe_s, probe_r, node_bank, P, n_rels, device,
                                   hint_bank=hint_probe_true, leaky_lambda=10.0), probe_bank)
        leaky_shuffle = _acc(arm_sr(X, store_s, store_r, store_t, probe_s, probe_r, node_bank, P, n_rels, device,
                                    hint_bank=hint_probe_shuf, leaky_lambda=10.0), probe_bank)
    except Exception:
        leaky_intact = float("nan"); leaky_shuffle = float("nan")

    sigs = {}
    for a in PRIMARY_ARMS:
        sigs[a] = hashlib.sha256(preds[a][:128].astype(np.int64).tobytes()).hexdigest()

    _log("  seed=%d M=%d(store=%d probes=%d) | ORACLE=%s DENSE=%s SR=%s DEG=%s RAND=%s | ceil=%s SR/ceil=%s | "
         "SR_strat LOW=%s[%d] MID=%s[%d] HIGH=%s[%d] | effrank=%.1f/%d | shuf: ORACLE %s->%s SR %s->%s leaky %s->%s"
         % (seed, M, take, probe_bank.shape[0], _fmt(acc[ORACLE]), _fmt(acc[DENSE]), _fmt(acc[SR]),
            _fmt(acc[DEGREE]), _fmt(acc[RANDOM]), _fmt(ceil),
            _fmt(acc[SR] / ceil) if ceil > 1e-9 else "nan",
            _fmt(sr_strat["LOW"]["acc"]), sr_strat["LOW"]["n"], _fmt(sr_strat["MID"]["acc"]), sr_strat["MID"]["n"],
            _fmt(sr_strat["HIGH"]["acc"]), sr_strat["HIGH"]["n"], eff_rank, k,
            _fmt(acc[ORACLE]), _fmt(oracle_shuf), _fmt(sr_intact), _fmt(sr_shuffle),
            _fmt(leaky_intact), _fmt(leaky_shuffle)))

    return dict(seed=int(seed), M=int(M), store=int(take), probes=int(probe_bank.shape[0]),
                acc=acc, sr_strat=sr_strat, ceiling=float(ceil), eff_rank=float(eff_rank),
                oracle_shuffle=float(oracle_shuf), sr_intact=float(sr_intact), sr_shuffle=float(sr_shuffle),
                leaky_intact=float(leaky_intact), leaky_shuffle=float(leaky_shuffle),
                deg_tertiles=[float(q1), float(q2)], sigs=sigs, failures=fails, P=int(P))


def run_seed(seed, all_tri, n, n_rels, cfg, device):
    node_bank = structural_partition_kmeans(np.stack([all_tri[:, 0], all_tri[:, 2]], axis=1).astype(np.int64),
                                            n, cfg["P"], seed, device)
    bank_sizes = np.bincount(node_bank, minlength=cfg["P"])
    _log("  seed=%d partition: P=%d bank_sizes min/med/max=%d/%d/%d n_edges=%d"
         % (seed, cfg["P"], int(bank_sizes.min()), int(np.median(bank_sizes)), int(bank_sizes.max()),
            all_tri.shape[0]))
    points = []
    for M in cfg["m_grid"]:
        pt = run_load_point(seed, M, all_tri, node_bank, n, n_rels, cfg["D"], cfg["k"], cfg["P"], device)
        points.append(pt)
    return dict(seed=int(seed), points=points, bank_sizes=[int(x) for x in bank_sizes])


# ---------------------------------------------------------------------------
# Aggregate + verdict (the pre-registered core).
# ---------------------------------------------------------------------------

def _mean(vals):
    a = np.array([v for v in vals if v == v], dtype=np.float64)
    return float(a.mean()) if a.shape[0] > 0 else float("nan")


def aggregate_and_verdict(per_seed, cfg):
    m_grid = cfg["m_grid"]
    P = cfg["P"]
    chance = 1.0 / P
    m_lo, m_hi = m_grid[0], m_grid[-1]

    def at(M, key_path):
        vals = []
        for s in per_seed:
            for pt in s["points"]:
                if pt["M"] == M:
                    v = pt
                    for kk in key_path:
                        v = v[kk]
                    vals.append(v)
        return _mean(vals)

    # per-arm curve (mean over seeds) at each M
    curve = {a: [at(M, ["acc", a]) for M in m_grid] for a in PRIMARY_ARMS}
    ceil_curve = [at(M, ["ceiling"]) for M in m_grid]

    sr_hi = at(m_hi, ["acc", SR]); dense_hi = at(m_hi, ["acc", DENSE]); deg_hi = at(m_hi, ["acc", DEGREE])
    rand_hi = at(m_hi, ["acc", RANDOM]); oracle_hi = at(m_hi, ["acc", ORACLE])
    dense_lo = at(m_lo, ["acc", DENSE])
    ceil_hi = ceil_curve[-1]
    sr_peak = max([v for v in curve[SR] if v == v], default=float("nan"))
    eff_rank_hi = at(m_hi, ["eff_rank"])
    sr_low = at(m_hi, ["sr_strat", "LOW", "acc"]); sr_high = at(m_hi, ["sr_strat", "HIGH", "acc"])
    sr_flatness = abs(sr_high - sr_low) if (sr_high == sr_high and sr_low == sr_low) else float("nan")
    oracle_shuf_hi = at(m_hi, ["oracle_shuffle"])
    sr_intact_hi = at(m_hi, ["sr_intact"]); sr_shuffle_hi = at(m_hi, ["sr_shuffle"])
    sr_shuffle_delta = abs(sr_intact_hi - sr_shuffle_hi) if (sr_intact_hi == sr_intact_hi
                                                             and sr_shuffle_hi == sr_shuffle_hi) else float("nan")
    leaky_intact_hi = at(m_hi, ["leaky_intact"]); leaky_shuffle_hi = at(m_hi, ["leaky_shuffle"])

    # ---- precondition gates ----
    enough = all(at(M, ["probes"]) >= 40 for M in m_grid)
    random_valid = bool(rand_hi == rand_hi and rand_hi <= chance + RANDOM_CEIL_OVER_CHANCE)
    oracle_fires = bool(oracle_hi == oracle_hi and oracle_hi >= chance + ORACLE_FIRE_MARGIN)
    shuffle_bites = bool(oracle_shuf_hi == oracle_shuf_hi and oracle_shuf_hi <= chance + ORACLE_SHUFFLE_CEIL)
    dense_collapses = bool(dense_lo == dense_lo and dense_hi == dense_hi
                           and dense_lo >= DENSE_HI_FLOOR and (dense_lo - dense_hi) >= DENSE_DROP_MIN)
    routable = bool(ceil_hi == ceil_hi and deg_hi == deg_hi and (ceil_hi - deg_hi) >= ROUTABLE_HEADROOM)

    # ---- HARD_PASS / HARD_FAIL conjuncts ----
    sep_ok = bool(sr_hi == sr_hi and dense_hi == dense_hi and (sr_hi - dense_hi) >= SEP_MARGIN)
    degree_ok = bool(sr_hi == sr_hi and deg_hi == deg_hi and (sr_hi - deg_hi) >= DEGREE_MARGIN)
    ceil_ok = bool(sr_hi == sr_hi and ceil_hi == ceil_hi and ceil_hi > 1e-9 and sr_hi >= CEIL_FRAC * ceil_hi)
    flat_ok = bool(sr_flatness == sr_flatness and sr_flatness <= FLAT_EPS)
    sr_self_ok = bool(sr_hi == sr_hi and sr_peak == sr_peak and sr_hi >= sr_peak - SR_SELF_DROP_MAX)
    shuffle_ok = bool(sr_shuffle_delta == sr_shuffle_delta and sr_shuffle_delta <= SHUFFLE_EPS and shuffle_bites)
    rank_ok = bool(eff_rank_hi == eff_rank_hi and eff_rank_hi > RANK_FLOOR)

    sr_ties_dense = bool(sr_hi == sr_hi and dense_hi == dense_hi and (sr_hi - dense_hi) < TIE_EPS)
    sr_ties_degree = bool(sr_hi == sr_hi and deg_hi == deg_hi and (sr_hi - deg_hi) < TIE_EPS)
    sr_leaks = bool(sr_shuffle_delta == sr_shuffle_delta and sr_shuffle_delta > SHUFFLE_FAIL)
    sr_concentrates = bool(sr_flatness == sr_flatness and sr_flatness >= CONCENTRATE_FAIL)
    sr_degenerate = bool(eff_rank_hi == eff_rank_hi and eff_rank_hi <= RANK_FLOOR)

    hard_pass = bool(sep_ok and degree_ok and ceil_ok and flat_ok and sr_self_ok and shuffle_ok and rank_ok)

    if not enough:
        verdict = "INCONCLUSIVE_TOO_FEW_PROBES"
    elif not random_valid:
        verdict = "INCONCLUSIVE_RANDOM_NOT_AT_CHANCE"
    elif not oracle_fires:
        verdict = "INCONCLUSIVE_ORACLE_DID_NOT_FIRE"
    elif not routable:
        verdict = "INCONCLUSIVE_NO_ROUTABLE_STRUCTURE_BEYOND_POPULARITY"
    elif not dense_collapses:
        verdict = "INCONCLUSIVE_DENSE_DID_NOT_COLLAPSE"
    elif sr_degenerate:
        verdict = "HARD_FAIL_SR_DEGENERATE_COLLAPSE"
    elif sr_leaks:
        verdict = "HARD_FAIL_ORACLE_LEAK_SR_DIES_UNDER_SHUFFLE"
    elif sr_ties_dense:
        verdict = "HARD_FAIL_SR_COLLAPSES_LIKE_DENSE_LOWRANK_BOUGHT_NOTHING"
    elif sr_ties_degree:
        verdict = "HARD_FAIL_POPULARITY_SHORTCUT_SR_TIES_DEGREE"
    elif sr_concentrates:
        verdict = "HARD_FAIL_DEGREE_DEPENDENT_SR_CONCENTRATES"
    elif hard_pass:
        verdict = "HARD_PASS_NATIVE_SR_ROUTER_SURVIVES_LOAD"
    else:
        verdict = "MIDDLE_BAND_PARTIAL_ROUTING_AMBIGUOUS"

    verdict_msg = (
        "%s || CURVE acc-vs-M (M=%s): ORACLE=%s DENSE=%s SR=%s DEGREE=%s RANDOM=%s CEIL=%s || "
        "M_hi=%d: SR=%.3f DENSE=%.3f DEGREE=%.3f RANDOM=%.3f ORACLE=%.3f CEIL=%.3f chance=%.3f | "
        "sep(SR-DENSE)=%s deg(SR-DEG)=%s SR/ceil=%s SR_flat|hi-lo|=%s (LOW=%s HIGH=%s) SR_peak=%s effrank=%s || "
        "SHUFFLE M_hi: ORACLE %.3f->%.3f (bites=%s) SR %.3f->%.3f (delta=%s) leaky %.3f->%.3f || "
        "DENSE collapse: M_lo=%.3f -> M_hi=%.3f (collapses=%s) || "
        "GATES enough=%s rand_valid=%s oracle_fires=%s routable(ceil-deg>=%.2f)=%s dense_collapses=%s || "
        "HP conj: sep=%s degree=%s ceil=%s flat=%s sr_self=%s shuffle=%s rank=%s || seeds=%d P=%d run=%s" % (
            verdict, ",".join(str(m) for m in m_grid),
            ",".join(_fmt(v) for v in curve[ORACLE]), ",".join(_fmt(v) for v in curve[DENSE]),
            ",".join(_fmt(v) for v in curve[SR]), ",".join(_fmt(v) for v in curve[DEGREE]),
            ",".join(_fmt(v) for v in curve[RANDOM]), ",".join(_fmt(v) for v in ceil_curve),
            m_hi, sr_hi, dense_hi, deg_hi, rand_hi, oracle_hi, ceil_hi, chance,
            _fmt(sr_hi - dense_hi), _fmt(sr_hi - deg_hi), _fmt(sr_hi / ceil_hi) if ceil_hi > 1e-9 else "nan",
            _fmt(sr_flatness), _fmt(sr_low), _fmt(sr_high), _fmt(sr_peak), _fmt(eff_rank_hi),
            oracle_hi, oracle_shuf_hi, shuffle_bites, sr_intact_hi, sr_shuffle_hi, _fmt(sr_shuffle_delta),
            leaky_intact_hi, leaky_shuffle_hi,
            dense_lo, dense_hi, dense_collapses,
            enough, random_valid, oracle_fires, ROUTABLE_HEADROOM, routable, dense_collapses,
            sep_ok, degree_ok, ceil_ok, flat_ok, sr_self_ok, shuffle_ok, rank_ok,
            len(per_seed), P, "full" if len(per_seed) >= 3 else "smoke"))

    gates = dict(
        verdict=verdict,
        curve=dict(m_grid=list(m_grid), **{a: curve[a] for a in PRIMARY_ARMS}, CEILING=ceil_curve),
        m_hi=dict(M=m_hi, SR=sr_hi, DENSE=dense_hi, DEGREE=deg_hi, RANDOM=rand_hi, ORACLE=oracle_hi,
                  ceiling=ceil_hi, chance=chance, sep_sr_dense=(sr_hi - dense_hi),
                  deg_sr_degree=(sr_hi - deg_hi),
                  sr_over_ceil=(sr_hi / ceil_hi) if ceil_hi > 1e-9 else float("nan"),
                  sr_flatness=sr_flatness, sr_low=sr_low, sr_high=sr_high, sr_peak=sr_peak, eff_rank=eff_rank_hi),
        shuffle=dict(oracle_intact=oracle_hi, oracle_shuffle=oracle_shuf_hi, shuffle_bites=shuffle_bites,
                     sr_intact=sr_intact_hi, sr_shuffle=sr_shuffle_hi, sr_shuffle_delta=sr_shuffle_delta,
                     leaky_intact=leaky_intact_hi, leaky_shuffle=leaky_shuffle_hi),
        dense_collapse=dict(dense_lo=dense_lo, dense_hi=dense_hi, collapses=dense_collapses),
        preconditions=dict(enough=enough, random_valid=random_valid, oracle_fires=oracle_fires,
                           routable=routable, dense_collapses=dense_collapses),
        hard_pass_conjuncts=dict(sep_ok=sep_ok, degree_ok=degree_ok, ceil_ok=ceil_ok, flat_ok=flat_ok,
                                 sr_self_ok=sr_self_ok, shuffle_ok=shuffle_ok, rank_ok=rank_ok),
        bands=dict(SEP_MARGIN=SEP_MARGIN, DEGREE_MARGIN=DEGREE_MARGIN, CEIL_FRAC=CEIL_FRAC, FLAT_EPS=FLAT_EPS,
                   CONCENTRATE_FAIL=CONCENTRATE_FAIL, SHUFFLE_EPS=SHUFFLE_EPS, SHUFFLE_FAIL=SHUFFLE_FAIL,
                   SR_SELF_DROP_MAX=SR_SELF_DROP_MAX, RANK_FLOOR=RANK_FLOOR, TIE_EPS=TIE_EPS,
                   DENSE_HI_FLOOR=DENSE_HI_FLOOR, DENSE_DROP_MIN=DENSE_DROP_MIN,
                   DENSE_COLLAPSE_CEIL=DENSE_COLLAPSE_CEIL,
                   ORACLE_FIRE_MARGIN=ORACLE_FIRE_MARGIN, ORACLE_SHUFFLE_CEIL=ORACLE_SHUFFLE_CEIL,
                   ROUTABLE_HEADROOM=ROUTABLE_HEADROOM, P=P, chance=chance, D=cfg["D"], k=cfg["k"]),
    )
    return verdict, verdict_msg, gates


# ---------------------------------------------------------------------------
# Mechanism self-test. Planted worlds prove the routing discriminators FIRE:
#   (a) planted routable structure (block-model banks separable in low-rank space) is FOUND by SR (SR >> chance);
#   (b) a label-shuffled hint kills a LEAKING router (leaky collapses; native SR invariant);
#   (c) a load-saturated world collapses the DENSE arm (M >> D) while SR survives.
# Saturation-vacuous guard: (b) leaky-collapses + (c) dense-collapses FAIL at self-test scale by construction, so a
# green self-test cannot rubber-stamp a degenerate FULL.
# ---------------------------------------------------------------------------

def _block_model_world(P, per_bank, n_rels, p_in, p_cross, seed):
    """Planted routable world: P banks, each with per_bank nodes; edges dense WITHIN a bank + a relation-consistent
    cross-bank translation (bank i --rel r--> bank (i + r + 1) mod P). bank(t) is a low-rank-separable function of node
    geometry -> SR should route; DENSE memorizes until crosstalk."""
    rng = np.random.default_rng(seed)
    n = P * per_bank
    node_bank = np.repeat(np.arange(P), per_bank).astype(np.int64)
    members = [np.where(node_bank == p)[0] for p in range(P)]
    tri = []
    # within-bank relation r=0 (local), and cross-bank translations r=1..n_rels-1
    for p in range(P):
        for s in members[p]:
            # local edges (same bank)
            for t in rng.choice(members[p], size=max(1, int(p_in * per_bank)), replace=True):
                if t != s:
                    tri.append((int(s), 0, int(t)))
            # translation edges
            for r in range(1, n_rels):
                tp = (p + r) % P
                for t in rng.choice(members[tp], size=max(1, int(p_cross * per_bank)), replace=True):
                    tri.append((int(s), r, int(t)))
    tri = np.asarray(tri, dtype=np.int64)
    return n, node_bank, tri


def _selftest(device):
    P = 8; per_bank = 30; n_rels = 4
    n, node_bank, tri = _block_model_world(P, per_bank, n_rels, p_in=0.20, p_cross=0.12, seed=0)
    chance = 1.0 / P
    D_small = 48                       # small dense dim -> collapses at feasible M
    k = 16

    def _point(M, seed):
        return run_load_point(seed, M, tri, node_bank, n, n_rels, D_small, k, P, device)

    # (c) load sweep: low M (< D) vs high M (>> D)
    lo = _point(32, 7)                 # M=32 < D_small=48 -> DENSE should recall well
    hi = _point(1200, 7)               # M=1200 >> D_small -> DENSE should collapse

    sr_hi = hi["acc"][SR]; dense_hi = hi["acc"][DENSE]; dense_lo = lo["acc"][DENSE]
    rand_hi = hi["acc"][RANDOM]; oracle_hi = hi["acc"][ORACLE]

    a_sr_finds_structure = bool(sr_hi == sr_hi and sr_hi >= chance + 0.25)      # (a) SR routes the planted structure
    c_dense_collapses = bool(dense_lo == dense_lo and dense_hi == dense_hi
                             and dense_lo >= 0.50 and dense_hi <= dense_lo - 0.20)  # (c) dense HIGH->LOW with load
    c_sr_survives_load = bool(sr_hi == sr_hi and dense_hi == dense_hi and (sr_hi - dense_hi) >= 0.20)
    # (b) leak: shuffle bites a leaking router; native SR invariant
    b_leaky_dies = bool(hi["leaky_intact"] == hi["leaky_intact"] and hi["leaky_shuffle"] == hi["leaky_shuffle"]
                        and (hi["leaky_intact"] - hi["leaky_shuffle"]) >= 0.25)
    b_native_invariant = bool(hi["sr_intact"] == hi["sr_intact"] and hi["sr_shuffle"] == hi["sr_shuffle"]
                              and abs(hi["sr_intact"] - hi["sr_shuffle"]) <= 0.02)
    b_oracle_bites = bool(hi["oracle_shuffle"] == hi["oracle_shuffle"] and hi["oracle_shuffle"] <= chance + 0.15)
    rank_ok = bool(hi["eff_rank"] > 3.0)
    # arms differ (not bit-identical)
    arms_differ = bool(len(set(hi["sigs"][a] for a in PRIMARY_ARMS)) >= 4)

    res = dict(
        chance=round(chance, 4), D_small=D_small,
        lo_M=32, hi_M=1200,
        sr_hi=round(sr_hi, 4), dense_lo=round(dense_lo, 4), dense_hi=round(dense_hi, 4),
        oracle_hi=round(oracle_hi, 4), rand_hi=round(rand_hi, 4), eff_rank_hi=round(hi["eff_rank"], 2),
        leaky_intact=round(hi["leaky_intact"], 4), leaky_shuffle=round(hi["leaky_shuffle"], 4),
        sr_intact=round(hi["sr_intact"], 4), sr_shuffle=round(hi["sr_shuffle"], 4),
        oracle_shuffle=round(hi["oracle_shuffle"], 4),
        a_sr_finds_structure=a_sr_finds_structure, c_dense_collapses=c_dense_collapses,
        c_sr_survives_load=c_sr_survives_load, b_leaky_dies=b_leaky_dies, b_native_invariant=b_native_invariant,
        b_oracle_bites=b_oracle_bites, rank_ok=rank_ok, arms_differ=arms_differ)
    ok = bool(a_sr_finds_structure and c_dense_collapses and c_sr_survives_load and b_leaky_dies
              and b_native_invariant and b_oracle_bites and rank_ok and arms_differ)
    return ok, res


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["self_test", "smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--device", choices=["auto", "cpu", "cuda"], default="auto")
    args, _unknown = ap.parse_known_args()
    run_mode = "self_test" if args.self_test else ("smoke" if args.smoke else args.run_mode)
    device = torch.device("cpu") if args.device == "cpu" else torch.device(
        "cuda" if ((args.device in ("auto", "cuda")) and torch.cuda.is_available()) else "cpu")

    output_dir = get_output_dir(ANCHOR_NAME)               # Path (write_metrics / write_partial require a Path)
    cfg = {"self_test": SELFTEST_CFG, "smoke": SMOKE_CFG, "full": FULL_CFG}[run_mode]
    expected_n_units = len(cfg["seeds"])
    _write_start_marker(str(output_dir), run_mode, expected_n_units)
    t_start = time.perf_counter()
    _log("device=%s cuda=%s run_mode=%s" % (device, torch.cuda.is_available(), run_mode))

    st_ok, st_res = _selftest(device)
    _log("mechanism_selftest ok=%s %s" % (st_ok, st_res))
    if not st_ok:
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL", run_mode=run_mode,
            verdict_msg="MECHANISM_SELFTEST_FAILED (routing discriminators did not fire): %s" % st_res,
            summary="mechanism selftest failed", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        raise SystemExit(1)

    if run_mode == "self_test":
        write_metrics(output_dir, dict(
            verdict="SELFTEST_PASS", run_mode="self_test",
            verdict_msg="SELFTEST_PASS native-SR-router: (a) SR finds planted routable structure; (b) shuffle kills a "
                        "leaking router while native SR is invariant + ORACLE collapses; (c) load saturation collapses "
                        "DENSE while SR survives; arms differ; no rank collapse",
            summary="SELFTEST_PASS", elapsed_s=time.perf_counter() - t_start, mechanism_selftest=st_res))
        _log("SELFTEST_PASS (%.1fs)" % (time.perf_counter() - t_start))
        return

    _log("loading typed ConceptNet subgraph (target n_nodes=%d)..." % cfg["n_nodes"])
    node_ids, node_words, edges, degrees, rels, T, types, meta = load_typed_cn_subgraph(
        cfg["n_nodes"], SUBGRAPH_BASE_SEED)
    edges = np.asarray(edges, dtype=np.int64)
    rels = np.asarray(rels, dtype=np.int64)
    n = len(node_ids)
    n_rels = int(T)
    # build directed triples (h, r, t) from edges + rels
    all_tri = np.stack([edges[:, 0], rels, edges[:, 1]], axis=1).astype(np.int64)
    _log("subgraph: n_nodes=%d n_edges=%d rel_types=%d median_degree=%s | M-grid=%s D=%d k=%d P=%d"
         % (n, all_tri.shape[0], n_rels, meta.get("median_degree"), cfg["m_grid"], cfg["D"], cfg["k"], cfg["P"]))
    # cardinality guard: the largest M must be reachable (enough edges) or the collapse-curve high-load point is fake
    if all_tri.shape[0] < cfg["m_grid"][-1]:
        write_metrics(output_dir, dict(
            verdict="INCONCLUSIVE_TOO_FEW_EDGES_FOR_M_GRID", run_mode=run_mode,
            verdict_msg="subgraph has %d edges < M_hi=%d; cannot reach the high-load point"
                        % (all_tri.shape[0], cfg["m_grid"][-1]),
            summary="too few edges", elapsed_s=time.perf_counter() - t_start, subgraph_meta=meta))
        raise SystemExit(1)

    per_seed = []; seed_failures = []
    for seed in cfg["seeds"]:
        try:
            sm = run_seed(seed, all_tri, n, n_rels, cfg, device)
            if len(sm["points"]) != len(cfg["m_grid"]):
                raise RuntimeError("CARDINALITY seed=%d ran %d/%d M-points"
                                   % (seed, len(sm["points"]), len(cfg["m_grid"])))
            per_seed.append(sm)
            write_partial(output_dir, seed, dict(seed=seed, metrics=sm))
        except (KeyboardInterrupt, SystemExit):
            raise
        except Exception as e:
            seed_failures.append(dict(seed=int(seed), failure_class=type(e).__name__, msg=str(e)[:300]))
            _log("SEED_FAILED seed=%d class=%s: %s" % (seed, type(e).__name__, str(e)[:200]))

    if len(per_seed) < expected_n_units:
        write_metrics(output_dir, dict(
            verdict="HARD_FAIL_CARDINALITY_BREACH_META_RULE_H", run_mode=run_mode,
            verdict_msg="expected %d seeds, got %d (failures=%s)" % (expected_n_units, len(per_seed), seed_failures),
            summary="cardinality breach", elapsed_s=time.perf_counter() - t_start,
            seed_failures=seed_failures, subgraph_meta=meta))
        raise SystemExit(1)

    verdict, verdict_msg, gates = aggregate_and_verdict(per_seed, cfg)
    metrics = dict(verdict=verdict, verdict_msg=verdict_msg, summary=verdict_msg[:200], run_mode=run_mode,
                   elapsed_s=time.perf_counter() - t_start, anchor_name=ANCHOR_NAME,
                   ts_iso=datetime.now(timezone.utc).isoformat(), device=str(device), n_seeds=len(per_seed),
                   seeds=cfg["seeds"], config=dict(seeds=cfg["seeds"], n_nodes=cfg["n_nodes"], P=cfg["P"],
                                                   D=cfg["D"], k=cfg["k"], m_grid=cfg["m_grid"]),
                   subgraph_meta=meta, gates=gates, mechanism_selftest=st_res,
                   seed_failures=seed_failures, per_seed=per_seed)
    write_metrics(output_dir, metrics, results=[{"elapsed_s": metrics["elapsed_s"]}])
    _log("VERDICT: %s" % verdict_msg)
    _log("done (%.1fs)" % (time.perf_counter() - t_start))


if __name__ == "__main__":
    _od = str(get_output_dir(ANCHOR_NAME))
    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_crash_metrics(_od, e)
        raise
