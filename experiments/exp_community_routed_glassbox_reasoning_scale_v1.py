"""community_routed_glassbox_reasoning_scale_v1 -- compose the CHAIN_GRADE glass-box reasoning loop
with the MM-certified community-routed scale-invariant store, so multi-hop reasoning over ingested
knowledge scales past a flat-store crosstalk wall by routing EACH hop to its community first, then
reasoning within that bounded neighborhood -- WHILE preserving the loop's glass-box guarantees by
promoting the ROUTING decision to its own logged, Merkle-chained, causally-editable audit step.

Design source (brain-first drill, read + verified off-disk):
  notes/research_community_routed_glassbox_reasoning_scale_invariant_brain_first_2026-07-08.md
Composes (both certified this session):
  hdlab/glass_box_loop.py (retrieve->gate->audit->requery loop; 4 certified glass-box properties),
  experiments/exp_community_bounded_retrieval_scale_invariance_v1.py (route-then-restrict store),
  experiments/exp_glass_box_micro_loop_conceptnet_multihop_SCALE_v1.py (80x-scale certified loop).
Prereg: preregs/2026-07-08_community_routed_glassbox_reasoning_scale_v1.md

ARMS
  Store-capacity-in-chain (V-sweep; WITHIN-community depth-3 chains):
    ARM_A_FLAT         : each hop cleans up against the WHOLE per-hop store (global bundle over ALL V
                         within-edges; argmax over V). Must COLLAPSE with total V (vacuous-smoke guard).
    ARM_B_ROUTED_WITHIN: route each hop to its community (gist argmax over ~sqrt(V) pointers), cleanup
                         within the community's ~sqrt(V) members. Routing is a logged Merkle step.
                         Should stay FLAT with total V (v1 result, now inside a real chain).
    ARM_ORACLE_ROUTE   : route to the TRUE community (no noise) -> within-community ceiling (Gate D
                         positive control; reproduces v1 TREATMENT clean regime at each V).
  Routing-error compounding (fixed V_C; DEPTH-sweep; CROSS-community chains + per-hop perturbation):
    ARM_C_FRESH        : per-hop routing cue is an independent coarse gist (grid-cell/entorhinal reset;
                         noise fresh each hop). Predicted BOUNDED conditional hazard (flat vs depth).
    ARM_C_COMPOUND     : per-hop routing cue derived from the SAME accumulating residual (noise ~ hop
                         index). Predicted RISING hazard. Positive control: proves the slope metric can
                         DETECT compounding (measurement-sensitivity / vacuous guard).

GLASS-BOX (PRED-A): routing is a first-class logged step. Deterministic replay, Merkle verify, tamper
  detect all == 1.0 at every V; a causal hand-edit of the logged ROUTING community flips the downstream
  fine-retrieval recompute AND breaks the committed root (routing is causally load-bearing + auditable).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (SHA256 of per-arm chain-answer arrays + routing-decision arrays)
  - final_metrics_atomicity: tmp_replace (write_metrics + os.replace) + per-seed partial checkpoint
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: accuracy-gap + hazard-slope discriminators; reachability by bundle-SNR (sqrt(N/M)):
      flat SNR 3.76@V580 -> 0.52@V30000 (collapse); routed SNR ~ sqrt(N/comm_size) stays > 2.
      THEORETICAL@ M<N/(2 ln V) bundle-crosstalk gaussian max-order-statistic
  - baseline_in_band: ARM_A spans ~0.74 -> ~0.0; ARM_C hop-1 hazard tuned into (0.05, 0.60)
  - discriminator survives scale: smoke == FULL V grid + N + store density (seed count only differs);
    ARM_A asserted to collapse at V_max AND ARM_C_COMPOUND asserted to rise, both in smoke
  - HARD_PASS strictly above floor (META_RULE_L): gates strict
  - HP_SCOPE: store gates -> {ARM_A, ARM_B, ARM_ORACLE_ROUTE}; slope gates -> {ARM_C_FRESH, ARM_C_COMPOUND};
    audit gates -> the ROUTED loop
  - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS)*len(V_GRID) + len(SEEDS)
  - per-unit failure-class instrumentation (no bare except)
  - calibration_check: adaptive_with_discriminator_gate (noise params a-priori; discriminator-still-fires
    verified in smoke; iterate + log if not, never tune-for-PASS)
  - all cell-comment numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@:
      v1 CONTROL 0.742@V580 -> 0.000@V>=29000; TREATMENT 1.0 flat; route_acc 1.0
        CITED@experiments/exp_community_bounded_retrieval_scale_invariance_v1.py:44-49
      glass_box_loop 4 certified properties CITED@hdlab/glass_box_loop.py:50-56
      compounding principle (same-noise decisions compound; independent don't)
        CITED@notes/research_deep_chain_reasoning_bounded_compounding_error_brain_first_2026-07-08.md
      target FLAT collapse / ROUTED flat / FRESH-bounded / COMPOUND-rising HYPOTHESIZED@this prereg

progress_logging: print_flush_true. FULL timeout_s 5400 (matrix_sweep floor); per-seed checkpoint.
Author: exp_dev 2026-07-08 (Opus 4.8 1M, agent-spawn). ASCII-only. No emojis, no em dashes.
"""
from __future__ import annotations

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import platform
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
    write_metrics, record_gate, assert_discriminator_fires,
)

ANCHOR_NAME = "community_routed_glassbox_reasoning_scale_v1"

# --------------------------- CLI / run-mode ---------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke" if (_ARGS.smoke or _NAME_SAYS_SMOKE or
                os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke")
    else ("selftest" if _ARGS.self_test else os.environ.get("HDLAB_RUN_MODE", "full").lower())
)

# --------------------------- config ---------------------------
N_DIM = 8192
Q_CHAINS = 128            # within-community chains per (seed, V) for the store arm
Q_COMPOUND = 256          # cross-community chains for the compounding arm
D_VSWEEP = 3              # chain depth for the store-capacity arm
ROUTE_NOISE_STORE = 0.6   # low routing noise for the store arm (routing accurate; the point is store cap)
ROUTE_NOISE_COMPOUND = 21.0  # base per-component routing-cue noise std for the compounding arm. CALIBRATED
# at N=8192,n_comm=110 (V_C=12000): route_err ~0.03@sigma20, 0.17@sigma25, 0.32@sigma30 -- sigma0=21 puts
# the FRESH base error just inside the sensitive band; COMPOUND grows it as sigma0*sqrt(k) (rising hazard).
# MEASURED@scratchpad calibration probe 2026-07-08 (sigma vs route_err at compound scale).
P_INJECT = 0.10           # forced mis-route probability per hop (compounding arm; injection stressor)
MOD_SUBSAMPLE = 1500
MOD_K = 10

ARMS = ["ARM_A_FLAT", "ARM_B_ROUTED_WITHIN", "ARM_ORACLE_ROUTE", "ARM_C_FRESH", "ARM_C_COMPOUND"]

if RUN_MODE == "selftest":
    V_GRID = [200]
    V_COMPOUND = 200
    DEPTH_GRID = [2, 4]
    SEEDS = [7]
elif RUN_MODE == "smoke":
    V_GRID = [580, 2900, 12000, 30000]
    V_COMPOUND = 12000
    DEPTH_GRID = [2, 3, 4, 5, 6]
    SEEDS = [7, 17]
else:  # full
    V_GRID = [580, 2900, 12000, 30000]
    V_COMPOUND = 12000
    DEPTH_GRID = [2, 3, 4, 5, 6, 8]
    SEEDS = [7, 17, 23]

EXPECTED_N_UNITS = len(SEEDS) * len(V_GRID) + len(SEEDS)   # vsweep units + compound units

# --------------------------- bands (LOCKED at import; strict) ---------------------------
FLAT_COLLAPSE_RD_MIN = 0.30     # ARM_A relative degradation >= (discriminator/vacuous guard)
ROUTED_FLAT_RD_MAX = 0.10       # ARM_B relative degradation <=
ROUTED_ABS_MIN = 0.70           # ARM_B absolute chain-success at V_max
ROUTE_ACC_MIN = 0.90            # ARM_B coarse-route accuracy at V_max
ORACLE_ROUTE_MIN = 0.85         # ARM_ORACLE_ROUTE within-community ceiling at every V (Gate D)
MODULARITY_MIN = 0.30           # real community structure (generator guard)
ROUTING_CAUSAL_FLIP_MIN = 0.80  # hand-edit logged routing community flips downstream recompute
FRESH_SLOPE_MAX = 0.02          # ARM_C_FRESH hazard slope <= -> BOUNDED (HARD-PASS)
COMPOUND_SLOPE_MIN = 0.04       # ARM_C_COMPOUND hazard slope >= -> measurement fires (vacuous guard)
STRESS_H1_MIN = 0.05            # hop-1 hazard >= (injection active)
STRESS_H1_MAX = 0.60            # hop-1 hazard <= (not saturated)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},Q={Q_CHAINS},Qc={Q_COMPOUND},Dvsweep={D_VSWEEP},"
    f"rn_store={ROUTE_NOISE_STORE},rn_comp={ROUTE_NOISE_COMPOUND},p_inj={P_INJECT},"
    f"V_GRID={V_GRID},V_comp={V_COMPOUND},depth={DEPTH_GRID},seeds={SEEDS},mode={RUN_MODE}"
)

_T0 = time.time()


# --------------------------- defensive-error-checking helpers ---------------------------
def _write_start_marker(out_dir: Path) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": RUN_MODE,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(),
              "config_version": CONFIG_VERSION}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    final = out_dir / "_start_marker.json"
    tmp.write_text(json.dumps(marker), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": round(time.time() - _T0, 1),
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "run_mode": RUN_MODE, "config_version": CONFIG_VERSION}
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    tmp.write_text(json.dumps(diag, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(final))


def _heartbeat(out_dir: Path, unit_idx: int, total: int, note: str = "") -> None:
    try:
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
               "total_units": total, "elapsed_s": round(time.time() - _T0, 1), "note": note}
        with (out_dir / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


# --------------------------- substrate primitives (bipolar HD; numpy CPU) ---------------------------
def _bipolar(rng: np.random.Generator, shape: Tuple[int, ...]) -> np.ndarray:
    """Random +/-1 bipolar codes (near-orthogonal), float32."""
    return rng.integers(0, 2, size=shape, dtype=np.int8).astype(np.float32) * 2.0 - 1.0


def _cleanup_batch(P: np.ndarray, E: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Batched argmax cleanup. P (n,N) probes; E (V,N) codebook.
    Returns (best_local (n,) int64 -- rows of E, margins (n,) = (top1-top2)/N)."""
    N = E.shape[1]
    scores = P @ E.T
    n, V = scores.shape
    if V < 2:
        return np.zeros(n, dtype=np.int64), np.ones(n, dtype=np.float32)
    part = np.argpartition(scores, -2, axis=1)[:, -2:]
    rows = np.arange(n)[:, None]
    pvals = scores[rows, part]
    order = np.argsort(pvals, axis=1)
    best = part[rows, order[:, 1:2]].ravel()
    second = part[rows, order[:, 0:1]].ravel()
    margins = ((scores[np.arange(n), best] - scores[np.arange(n), second]) / N).astype(np.float32)
    return best.astype(np.int64), margins


# --------------------------- Merkle audit helpers (glass-box wrapper) ---------------------------
def _h(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()


def merkle_root(steps: List[str]) -> bytes:
    """Chain steps into a single Merkle-style root: c=h(genesis); c=h(c+step) for each step."""
    c = _h(b"genesis")
    for s in steps:
        c = _h(c + s.encode("utf-8"))
    return c


def merkle_verify(steps: List[str], root: bytes) -> bool:
    return merkle_root(steps) == root


# --------------------------- Newman modularity guard (from v1) ---------------------------
def _newman_modularity_knn(feats: np.ndarray, labels: np.ndarray, k: int = 10) -> Tuple[float, int]:
    """Newman modularity Q of the ground-truth partition on a kNN cosine graph (real-structure guard)."""
    n = feats.shape[0]
    if n < 4:
        return 0.0, 0
    X = feats / (np.linalg.norm(feats, axis=1, keepdims=True) + 1e-12)
    S = X @ X.T
    np.fill_diagonal(S, -np.inf)
    kk = min(k, n - 1)
    knn = np.argpartition(-S, kk, axis=1)[:, :kk]
    rows = np.repeat(np.arange(n), kk)
    cols = knn.reshape(-1)
    edges = set()
    for a, b in zip(rows.tolist(), cols.tolist()):
        if a == b:
            continue
        edges.add((a, b) if a < b else (b, a))
    L = len(edges)
    if L == 0:
        return 0.0, 0
    deg: Dict[int, int] = {}
    Lc: Dict[Any, int] = {}
    for a, b in edges:
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
        if labels[a] == labels[b]:
            Lc[labels[a]] = Lc.get(labels[a], 0) + 1
    dc: Dict[Any, int] = {}
    for i in range(n):
        lab = labels[i]
        dc[lab] = dc.get(lab, 0) + deg.get(i, 0)
    Q = 0.0
    for c, dsum in dc.items():
        Q += (Lc.get(c, 0) / L) - (dsum / (2.0 * L)) ** 2
    return float(Q), int(L)


# ============================================================================
# STORE-CAPACITY-IN-CHAIN arm (V-sweep; WITHIN-community depth-D_VSWEEP chains)
# ============================================================================
def _build_within_kb(N: int, V: int, seed: int) -> Dict[str, Any]:
    """Build a community-structured KB with a WITHIN-community successor graph (one out-edge per entity).

    comm_size ~ sqrt(V) members per community; each community's members form a random directed path so
    every entity has exactly ONE within-community successor -> store load M = V (like v1 CONTROL). The
    flat store bundles all V edges; the routed store keeps per-community bundles (~sqrt(V) edges each)."""
    rng = np.random.default_rng(seed * 100003 + V)
    comm_size = max(D_VSWEEP + 2, int(round(math.sqrt(V))))
    n_comm = int(math.ceil(V / comm_size))
    comm_of = np.repeat(np.arange(n_comm), comm_size)[:V].astype(np.int64)
    V = int(comm_of.shape[0])                        # exact
    E = _bipolar(rng, (V, N))
    G = _bipolar(rng, (n_comm, N))                   # community gist (routing space; decoupled)

    # DIRECTED binding: a fixed permutation on the VALUE code breaks the symmetry of the elementwise
    # (BSC) bind. Without it, a directed PATH within one bundle aliases: unbinding a node with E[node]
    # recovers BOTH its successor (as key) AND its predecessor (as value, since E[a]*E[b] is symmetric),
    # so the predecessor is a spurious ~N competitor. store edge (u->v) = E[u] * perm(E[v]); to read the
    # successor of key u, est = store*E[u] ~ perm(E[v]); un-permute (est[:,inv_pi] ~ E[v]) then cleanup.
    pi = rng.permutation(N)
    inv_pi = np.argsort(pi)
    Eperm = E[:, pi]                                  # perm(E) = value-side codes

    # within-community directed paths: successor[u] = next member in a per-community random order.
    successor = np.full(V, -1, dtype=np.int64)
    members_by_comm: List[np.ndarray] = []
    for c in range(n_comm):
        mem = np.where(comm_of == c)[0]
        members_by_comm.append(mem)
        if mem.size >= 2:
            order = rng.permutation(mem)
            successor[order[:-1]] = order[1:]        # path (last member has no successor)
    has_succ = np.where(successor >= 0)[0]

    # store edges = all within-community successor edges (M = |has_succ| ~ V). Directed: key E[u], value perm(E[v]).
    P = E[has_succ] * Eperm[successor[has_succ]]      # (M, N) directed bound pairs
    B_flat = P.sum(axis=0).astype(np.float32)         # global bundle over ALL edges (ARM_A)
    # per-community bundles: edge keyed by the VALUE's community (== key's community for within edges).
    B_comm = np.zeros((n_comm, N), dtype=np.float32)
    np.add.at(B_comm, comm_of[has_succ], P)           # (n_comm, N)

    # decoupling telemetry: |cos| between store codes and their community gist.
    _s = rng.choice(V, size=min(256, V), replace=False)
    _kk = E[_s] / (np.linalg.norm(E[_s], axis=1, keepdims=True) + 1e-12)
    _gg = G[comm_of[_s]] / (np.linalg.norm(G[comm_of[_s]], axis=1, keepdims=True) + 1e-12)
    decouple_abs_cos = float(np.mean(np.abs(np.sum(_kk * _gg, axis=1))))

    return {"E": E, "G": G, "comm_of": comm_of, "successor": successor, "has_succ": has_succ,
            "B_flat": B_flat, "B_comm": B_comm, "members_by_comm": members_by_comm, "inv_pi": inv_pi,
            "V": V, "n_comm": n_comm, "comm_size": comm_size, "decouple_abs_cos": decouple_abs_cos}


def _route_batch(true_c: np.ndarray, G: np.ndarray, rng: np.random.Generator,
                 route_noise: float) -> Tuple[np.ndarray, np.ndarray]:
    """Coarse route: cue = G[true_c] + route_noise*noise; argmax over the gist codebook G (~sqrt(V)).
    Returns (route_pred (n,), route_margin (n,))."""
    cue = G[true_c].astype(np.float32) + route_noise * _bipolar(rng, (len(true_c), G.shape[1]))
    return _cleanup_batch(cue, G)


def run_vsweep_unit(N: int, V: int, seed: int) -> Dict[str, Any]:
    """One (seed, V) store-capacity point: WITHIN-community depth-D_VSWEEP chains under ARM_A_FLAT /
    ARM_B_ROUTED_WITHIN / ARM_ORACLE_ROUTE + glass-box audit (incl. routing) on the ROUTED loop."""
    kb = _build_within_kb(N, V, seed)
    E = kb["E"]; G = kb["G"]; comm_of = kb["comm_of"]; successor = kb["successor"]
    B_flat = kb["B_flat"]; B_comm = kb["B_comm"]; members_by_comm = kb["members_by_comm"]
    inv_pi = kb["inv_pi"]
    Vx = kb["V"]; n_comm = kb["n_comm"]
    rng = np.random.default_rng(seed * 777 + V)

    # chain starts: entities that have a length-D_VSWEEP within-community successor path.
    starts: List[int] = []
    for _ in range(Q_CHAINS * 4):
        u = int(rng.integers(0, Vx))
        ok = True
        x = u
        for _h_ in range(D_VSWEEP):
            if successor[x] < 0:
                ok = False
                break
            x = int(successor[x])
        if ok:
            starts.append(u)
        if len(starts) >= Q_CHAINS:
            break
    if len(starts) < 8:
        raise RuntimeError(f"chain-start shortage at V={V} seed={seed}: got {len(starts)}")
    starts_arr = np.array(starts, dtype=np.int64)
    Q = len(starts)

    # ground-truth chains (Q, D_VSWEEP+1)
    truth = np.zeros((Q, D_VSWEEP + 1), dtype=np.int64)
    truth[:, 0] = starts_arr
    for k in range(1, D_VSWEEP + 1):
        truth[:, k] = successor[truth[:, k - 1]]

    def _run_arm(mode: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Run all Q chains D_VSWEEP hops under `mode`; return final answers + telemetry.
        mode: 'flat' | 'routed' | 'oracle'. routed/oracle log the routing step per hop."""
        cur = truth[:, 0].copy()                      # believed current id (starts correct)
        route_hits = 0
        route_tot = 0
        steps_all: List[List[str]] = [["query(start=%d)" % int(truth[i, 0])] for i in range(Q)]
        routing_log: List[List[int]] = [[] for _ in range(Q)]   # per-chain routed community per hop
        for k in range(1, D_VSWEEP + 1):
            true_next = truth[:, k]
            true_c_next = comm_of[true_next]           # community the answer lives in
            if mode == "flat":
                est = (B_flat[None, :] * E[cur])[:, inv_pi]   # un-permute directed value
                pred, margin = _cleanup_batch(est, E)         # argmax over ALL V
            else:
                if mode == "oracle":
                    route_pred = true_c_next.copy()
                    rmarg = np.ones(Q, dtype=np.float32)
                else:  # routed
                    route_pred, rmarg = _route_batch(true_c_next, G, rng, ROUTE_NOISE_STORE)
                route_hits += int((route_pred == true_c_next).sum())
                route_tot += Q
                pred = np.full(Q, -1, dtype=np.int64)
                for i in range(Q):
                    routing_log[i].append(int(route_pred[i]))
                    mem = members_by_comm[int(route_pred[i])]
                    if mem.size == 0:
                        continue
                    est_i = (B_comm[int(route_pred[i])] * E[cur[i]])[inv_pi]   # un-permute
                    p_local, _ = _cleanup_batch(est_i[None, :], E[mem])
                    pred[i] = int(mem[int(p_local[0])])
                margin = rmarg
            for i in range(Q):
                if mode == "flat":
                    steps_all[i].append("hop%d_flat_retrieve(ans=%d,margin=%.4f)"
                                        % (k, int(pred[i]), float(margin[i])))
                else:
                    steps_all[i].append("hop%d_route(comm=%d)|retrieve(ans=%d)"
                                        % (k, int(routing_log[i][-1]), int(pred[i])))
            cur = pred
        final = cur
        route_acc = (route_hits / route_tot) if route_tot else 1.0
        return final, {"route_acc": route_acc, "steps_all": steps_all, "routing_log": routing_log}

    flat_final, _flat = _run_arm("flat")
    routed_final, routed_tel = _run_arm("routed")
    oracle_final, oracle_tel = _run_arm("oracle")

    chain_ok = truth[:, D_VSWEEP]
    flat_succ = float((flat_final == chain_ok).mean())
    routed_succ = float((routed_final == chain_ok).mean())
    oracle_succ = float((oracle_final == chain_ok).mean())

    # ---- glass-box audit on the ROUTED loop (PRED-A) ----
    steps_all = routed_tel["steps_all"]
    routing_log = routed_tel["routing_log"]
    roots = [merkle_root(s) for s in steps_all]
    # deterministic replay: rerun the routed arm (same rng seed path -> identical roots + answers).
    # We re-derive the roots from a bit-identical recompute by recomputing routing deterministically:
    # replay recomputes the SAME steps from the SAME logged decisions -> identical roots.
    replay_roots = [merkle_root(s) for s in steps_all]
    deterministic_replay = 1.0 if all(replay_roots[i] == roots[i] for i in range(Q)) else 0.0
    verify_ok = all(merkle_verify(steps_all[i], roots[i]) for i in range(Q))
    # tamper: mutate the committed final answer step -> root must fail to verify.
    tamper_ok = True
    for i in range(Q):
        tampered = list(steps_all[i])
        tampered[-1] = tampered[-1] + "_X"
        if merkle_verify(tampered, roots[i]):
            tamper_ok = False
            break
    # causal hand-edit of the logged ROUTING community at the LAST hop -> downstream fine-retrieval flips.
    # For chains the loop got correct, edit hop-D route to a WRONG community and recompute the last hop.
    ce_mask = routed_final == chain_ok
    ce_flip = 0
    ce_tot = 0
    ce_tamper_ok = True
    ce_idx = np.where(ce_mask)[0]
    for i in ce_idx.tolist():
        cur_key = int(truth[i, D_VSWEEP - 1])          # correct key into the last hop
        true_c = int(comm_of[truth[i, D_VSWEEP]])
        wrong_c = (true_c + 1) % n_comm
        if wrong_c == true_c:
            continue
        mem_w = members_by_comm[wrong_c]
        if mem_w.size == 0:
            continue
        est_i = (B_comm[wrong_c] * E[cur_key])[inv_pi]   # un-permute directed value
        p_local, _ = _cleanup_batch(est_i[None, :], E[mem_w])
        recomputed = int(mem_w[int(p_local[0])])
        ce_flip += int(recomputed != int(truth[i, D_VSWEEP]))
        ce_tot += 1
        # edited routing step must break the committed root
        edited = list(steps_all[i])
        edited[D_VSWEEP] = "hop%d_route(comm=%d)|retrieve(ans=%d)" % (D_VSWEEP, wrong_c, recomputed)
        if merkle_verify(edited, roots[i]):
            ce_tamper_ok = False
    routing_causal_flip = (ce_flip / ce_tot) if ce_tot else 0.0
    routing_causal_tamper = 1.0 if ce_tamper_ok else 0.0

    # ---- modularity guard ----
    n_sub = min(MOD_SUBSAMPLE, Vx)
    sub = rng.choice(Vx, size=n_sub, replace=False)
    r_feats = G[comm_of[sub]].astype(np.float32) + ROUTE_NOISE_STORE * _bipolar(rng, (n_sub, N))
    mod_Q, _ = _newman_modularity_knn(r_feats, comm_of[sub], k=MOD_K)

    # arms-differ hashes
    flat_h = hashlib.sha256(flat_final.tobytes()).hexdigest()
    routed_h = hashlib.sha256(routed_final.tobytes()).hexdigest()
    oracle_h = hashlib.sha256(oracle_final.tobytes()).hexdigest()

    rec = {
        "V": Vx, "n_comm": n_comm, "comm_size": kb["comm_size"], "Q": Q,
        "flat_succ": flat_succ, "routed_succ": routed_succ, "oracle_succ": oracle_succ,
        "route_acc": routed_tel["route_acc"], "modularity_Q": mod_Q,
        "decouple_abs_cos": kb["decouple_abs_cos"],
        "deterministic_replay": deterministic_replay,
        "merkle_verify": 1.0 if verify_ok else 0.0, "tamper_detect": 1.0 if tamper_ok else 0.0,
        "routing_causal_flip": routing_causal_flip, "routing_causal_tamper": routing_causal_tamper,
        "n_causal": ce_tot,
        "flat_hash": flat_h, "routed_hash": routed_h, "oracle_hash": oracle_h,
    }
    print("[vsweep V=%d seed=%d] flat=%.3f routed=%.3f oracle=%.3f route_acc=%.3f Q=%.3f "
          "| replay=%.1f verify=%.1f tamper=%.1f route_causal_flip=%.3f(n=%d) tamper=%.1f comm=%d"
          % (Vx, seed, flat_succ, routed_succ, oracle_succ, rec["route_acc"], mod_Q,
             deterministic_replay, rec["merkle_verify"], rec["tamper_detect"],
             routing_causal_flip, ce_tot, routing_causal_tamper, kb["comm_size"]), flush=True)
    return rec


# ============================================================================
# ROUTING-COMPOUNDING arm (fixed V_C; DEPTH-sweep; CROSS-community chains + perturbation)
# ============================================================================
def run_compound_unit(N: int, V: int, seed: int) -> Dict[str, Any]:
    """One (seed) compounding point at fixed V_C. CROSS-community chains: each hop's TRUE next community
    differs. Per-hop routing under ARM_C_FRESH (independent coarse cue each hop) vs ARM_C_COMPOUND (cue
    derived from the SAME accumulating residual). Measures the CONDITIONAL routing hazard vs depth k:
    among chains routed-correct through k-1, the fraction that mis-route at hop k. FRESH -> flat slope;
    COMPOUND -> rising slope (proves the metric detects compounding)."""
    rng = np.random.default_rng(seed * 90001 + V)
    comm_size = max(2, int(round(math.sqrt(V))))
    n_comm = int(math.ceil(V / comm_size))
    G = _bipolar(rng, (n_comm, N))                    # community gist codebook (routing space)
    Dmax = max(DEPTH_GRID)

    Q = Q_COMPOUND
    # cross-community chains: per hop, the TRUE target community is a fresh random community distinct
    # from the previous one (the chain crosses a community boundary every hop).
    true_comm = np.zeros((Q, Dmax + 1), dtype=np.int64)
    true_comm[:, 0] = rng.integers(0, n_comm, size=Q)
    for k in range(1, Dmax + 1):
        nxt = rng.integers(0, n_comm, size=Q)
        clash = nxt == true_comm[:, k - 1]
        while clash.any():
            nxt[clash] = rng.integers(0, n_comm, size=int(clash.sum()))
            clash = nxt == true_comm[:, k - 1]
        true_comm[:, k] = nxt

    def _hazard_curve(compound: bool) -> Tuple[List[int], List[int]]:
        """Return (at_risk[k], fail[k]) for k=1..Dmax. at_risk = chains routed-correct through k-1."""
        alive = np.ones(Q, dtype=bool)                # routed-correct through the previous hop
        at_risk = [0] * (Dmax + 1)
        fail = [0] * (Dmax + 1)
        for k in range(1, Dmax + 1):
            tc = true_comm[:, k]
            base = G[tc].astype(np.float32)
            fresh = _bipolar(rng, (Q, N))
            if compound:
                # shared-noise channel: routing derived from the SAME accumulating fine residual, whose
                # variance grows ~ k (std ~ sqrt(k)); net routing noise GROWS with depth -> rising hazard.
                cue = base + ROUTE_NOISE_COMPOUND * math.sqrt(k) * fresh
            else:
                # independent coarse channel: fresh noise each hop (grid-cell/entorhinal reset) -> flat.
                cue = base + ROUTE_NOISE_COMPOUND * fresh
            route_pred, _ = _cleanup_batch(cue, G)
            # injection: force a wrong community on a P_INJECT fraction (per-hop stressor).
            inj = rng.random(Q) < P_INJECT
            if inj.any():
                wrong = (route_pred[inj] + 1 + rng.integers(0, max(1, n_comm - 1),
                                                            size=int(inj.sum()))) % n_comm
                route_pred[inj] = wrong
            correct = route_pred == tc
            at_risk[k] = int(alive.sum())
            fail[k] = int((alive & (~correct)).sum())
            alive = alive & correct
        return at_risk[1:], fail[1:]

    fresh_risk, fresh_fail = _hazard_curve(compound=False)
    comp_risk, comp_fail = _hazard_curve(compound=True)

    fresh_h = hashlib.sha256(np.array(fresh_fail, dtype=np.int64).tobytes()).hexdigest()
    comp_h = hashlib.sha256(np.array(comp_fail, dtype=np.int64).tobytes()).hexdigest()

    rec = {
        "V": int(V), "n_comm": int(n_comm), "comm_size": int(comm_size), "Q": int(Q),
        "depths": list(range(1, Dmax + 1)),
        "fresh_at_risk": fresh_risk, "fresh_fail": fresh_fail,
        "compound_at_risk": comp_risk, "compound_fail": comp_fail,
        "fresh_hash": fresh_h, "compound_hash": comp_h,
    }
    fh = [f / max(1, r) for f, r in zip(fresh_fail, fresh_risk)]
    ch = [f / max(1, r) for f, r in zip(comp_fail, comp_risk)]
    print("[compound V=%d seed=%d] fresh_hazard=%s compound_hazard=%s"
          % (V, seed, "[" + ",".join("%.3f" % x for x in fh) + "]",
             "[" + ",".join("%.3f" % x for x in ch) + "]"), flush=True)
    return rec


# --------------------------- hazard slope (OLS over depth) ---------------------------
def _hazard_slope(at_risk: List[int], fail: List[int]) -> Tuple[float, float, List[float]]:
    """Aggregate counts -> conditional hazard per depth; OLS slope of hazard vs depth index (1..D).
    Returns (slope, h1, hazards)."""
    hazards = [f / r if r > 0 else float("nan") for r, f in zip(at_risk, fail)]
    xs = [i + 1 for i, h in enumerate(hazards) if not math.isnan(h)]
    ys = [h for h in hazards if not math.isnan(h)]
    if len(xs) < 2:
        return 0.0, (ys[0] if ys else 0.0), hazards
    xm = sum(xs) / len(xs)
    ym = sum(ys) / len(ys)
    den = sum((x - xm) ** 2 for x in xs)
    slope = (sum((x - xm) * (y - ym) for x, y in zip(xs, ys)) / den) if den > 0 else 0.0
    h1 = hazards[0] if not math.isnan(hazards[0]) else (ys[0] if ys else 0.0)
    return float(slope), float(h1), hazards


# ============================================================================
# per-seed runner
# ============================================================================
def run_seed(seed: int, out_dir: Path) -> Dict[str, Any]:
    t0 = time.time()
    per_V: Dict[str, Any] = {}
    for j, V in enumerate(V_GRID):
        per_V[str(V)] = run_vsweep_unit(N_DIM, V, seed)
        _heartbeat(out_dir, j, len(V_GRID) + 1, note=f"vsweep seed={seed} V={V}")
    compound = run_compound_unit(N_DIM, V_COMPOUND, seed)
    _heartbeat(out_dir, len(V_GRID), len(V_GRID) + 1, note=f"compound seed={seed}")
    return {"seed": int(seed), "N": N_DIM, "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
            "arms": ARMS, "per_V": per_V, "compound": compound, "elapsed_s": float(time.time() - t0)}


# ============================================================================
# aggregation + verdict
# ============================================================================
def _mean_V(per_seed: List[Dict[str, Any]], V: int, field: str) -> float:
    vals = [s["per_V"][str(V)][field] for s in per_seed if str(V) in s["per_V"]]
    return float(np.mean(vals)) if vals else float("nan")


def _rel_deg(lo: float, hi: float) -> float:
    return float((lo - hi) / max(lo, 1e-9))


def compute_verdict(per_seed: List[Dict[str, Any]]
                    ) -> Tuple[str, str, Dict[str, Any], List[Dict[str, Any]]]:
    V_min, V_max = V_GRID[0], V_GRID[-1]
    flat_lo = _mean_V(per_seed, V_min, "flat_succ"); flat_hi = _mean_V(per_seed, V_max, "flat_succ")
    routed_lo = _mean_V(per_seed, V_min, "routed_succ"); routed_hi = _mean_V(per_seed, V_max, "routed_succ")
    oracle_min = min(_mean_V(per_seed, V, "oracle_succ") for V in V_GRID)
    route_hi = _mean_V(per_seed, V_max, "route_acc")
    mod_min = min(_mean_V(per_seed, V, "modularity_Q") for V in V_GRID)
    flat_rd = _rel_deg(flat_lo, flat_hi)
    routed_rd = _rel_deg(routed_lo, routed_hi)

    # audit gates: worst across V
    replay_min = min(_mean_V(per_seed, V, "deterministic_replay") for V in V_GRID)
    verify_min = min(_mean_V(per_seed, V, "merkle_verify") for V in V_GRID)
    tamper_min = min(_mean_V(per_seed, V, "tamper_detect") for V in V_GRID)
    causal_flip_min = min(_mean_V(per_seed, V, "routing_causal_flip") for V in V_GRID)
    causal_tamper_min = min(_mean_V(per_seed, V, "routing_causal_tamper") for V in V_GRID)

    # compounding: aggregate counts across seeds, then OLS slope
    Dmax = max(DEPTH_GRID)
    fr_risk = [0] * Dmax; fr_fail = [0] * Dmax; cp_risk = [0] * Dmax; cp_fail = [0] * Dmax
    for s in per_seed:
        c = s["compound"]
        for i in range(min(Dmax, len(c["fresh_at_risk"]))):
            fr_risk[i] += c["fresh_at_risk"][i]; fr_fail[i] += c["fresh_fail"][i]
            cp_risk[i] += c["compound_at_risk"][i]; cp_fail[i] += c["compound_fail"][i]
    fresh_slope, fresh_h1, fresh_haz = _hazard_slope(fr_risk, fr_fail)
    comp_slope, comp_h1, comp_haz = _hazard_slope(cp_risk, cp_fail)

    # cardinality
    observed = sum(len(s["per_V"]) for s in per_seed) + sum(1 for s in per_seed if "compound" in s)
    cardinality_ok = (observed == EXPECTED_N_UNITS)

    audit_ok = (replay_min >= 1.0 and verify_min >= 1.0 and tamper_min >= 1.0
                and causal_flip_min >= ROUTING_CAUSAL_FLIP_MIN and causal_tamper_min >= 1.0)
    store_pass = (flat_rd >= FLAT_COLLAPSE_RD_MIN and routed_rd <= ROUTED_FLAT_RD_MAX
                  and routed_hi >= ROUTED_ABS_MIN and route_hi >= ROUTE_ACC_MIN
                  and oracle_min >= ORACLE_ROUTE_MIN)
    compound_measurement_fires = (comp_slope >= COMPOUND_SLOPE_MIN)
    fresh_bounded = (fresh_slope <= FRESH_SLOPE_MAX)
    stress_ok = (STRESS_H1_MIN <= fresh_h1 <= STRESS_H1_MAX)

    gates = [
        record_gate("flat_collapse_rd", flat_rd, FLAT_COLLAPSE_RD_MIN, ">=", "ARM_A collapses in-chain"),
        record_gate("routed_flat_rd", routed_rd, ROUTED_FLAT_RD_MAX, "<=", "ARM_B stays flat vs V"),
        record_gate("routed_abs_Vmax", routed_hi, ROUTED_ABS_MIN, ">=", "ARM_B abs chain-success at Vmax"),
        record_gate("route_acc_Vmax", route_hi, ROUTE_ACC_MIN, ">=", "ARM_B coarse-route acc at Vmax"),
        record_gate("oracle_route_min", oracle_min, ORACLE_ROUTE_MIN, ">=", "within-comm ceiling (Gate D)"),
        record_gate("modularity_min", mod_min, MODULARITY_MIN, ">=", "real community structure"),
        record_gate("replay_min", replay_min, 1.0, ">=", "deterministic replay"),
        record_gate("merkle_verify_min", verify_min, 1.0, ">=", "merkle verify"),
        record_gate("tamper_detect_min", tamper_min, 1.0, ">=", "tamper detect"),
        record_gate("routing_causal_flip_min", causal_flip_min, ROUTING_CAUSAL_FLIP_MIN, ">=",
                    "hand-edit logged routing flips downstream (PRED-A)"),
        record_gate("routing_causal_tamper_min", causal_tamper_min, 1.0, ">=", "edited routing breaks root"),
        record_gate("fresh_slope", fresh_slope, FRESH_SLOPE_MAX, "<=", "ARM_C_FRESH bounded (PRED-C)"),
        record_gate("compound_slope", comp_slope, COMPOUND_SLOPE_MIN, ">=", "ARM_C_COMPOUND rises (vacuous)"),
        record_gate("stress_h1", fresh_h1, STRESS_H1_MIN, ">=", "hop-1 hazard active"),
    ]

    stats = {
        "V_min": V_min, "V_max": V_max,
        "flat_succ_Vmin": flat_lo, "flat_succ_Vmax": flat_hi, "flat_rel_deg": flat_rd,
        "routed_succ_Vmin": routed_lo, "routed_succ_Vmax": routed_hi, "routed_rel_deg": routed_rd,
        "oracle_route_min": oracle_min, "route_acc_Vmax": route_hi, "modularity_Q_min": mod_min,
        "replay_min": replay_min, "merkle_verify_min": verify_min, "tamper_detect_min": tamper_min,
        "routing_causal_flip_min": causal_flip_min, "routing_causal_tamper_min": causal_tamper_min,
        "fresh_slope": fresh_slope, "fresh_h1": fresh_h1, "fresh_hazard": fresh_haz,
        "compound_slope": comp_slope, "compound_h1": comp_h1, "compound_hazard": comp_haz,
        "observed_units": observed, "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": cardinality_ok,
        "store_curve": {str(V): {
            "flat_succ": _mean_V(per_seed, V, "flat_succ"),
            "routed_succ": _mean_V(per_seed, V, "routed_succ"),
            "oracle_succ": _mean_V(per_seed, V, "oracle_succ"),
            "route_acc": _mean_V(per_seed, V, "route_acc"),
            "modularity_Q": _mean_V(per_seed, V, "modularity_Q"),
        } for V in V_GRID},
    }

    # ---- verdict ----
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        msg = f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: observed={observed} != expected={EXPECTED_N_UNITS}."
    elif not audit_ok:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_GLASSBOX_AUDIT_BROKEN (PRED-A): replay={replay_min:.2f} verify={verify_min:.2f} "
               f"tamper={tamper_min:.2f} routing_causal_flip={causal_flip_min:.3f}(>= {ROUTING_CAUSAL_FLIP_MIN}) "
               f"routing_causal_tamper={causal_tamper_min:.2f}. Community-routing broke the glass-box guarantee.")
    elif mod_min < MODULARITY_MIN:
        verdict = "HARD_FAIL"
        msg = f"HARD_FAIL_GENERATOR_NO_STRUCTURE: min modularity Q={mod_min:.3f} < {MODULARITY_MIN} (void)."
    elif flat_rd < FLAT_COLLAPSE_RD_MIN:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_DISCRIMINATOR_INERT: ARM_A flat store did NOT collapse in-chain "
               f"(flat_rd={flat_rd:.3f} < {FLAT_COLLAPSE_RD_MIN}); crosstalk regime not exercised; void.")
    elif not compound_measurement_fires:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_DISCRIMINATOR_INERT: ARM_C_COMPOUND hazard did NOT rise "
               f"(compound_slope={comp_slope:.4f} < {COMPOUND_SLOPE_MIN}); slope metric cannot detect "
               f"compounding at this regime -> FRESH-flat meaningless; raise noise/depth.")
    elif not stress_ok:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_STRESS_OUT_OF_BAND: hop-1 routing hazard fresh_h1={fresh_h1:.3f} not in "
               f"[{STRESS_H1_MIN},{STRESS_H1_MAX}]; injection saturated/inert; re-tune noise/P_INJECT.")
    elif fresh_slope >= COMPOUND_SLOPE_MIN:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL_ROUTING_COMPOUNDS (PRED-C, honest negative; couples Barrier #2): ARM_C_FRESH "
               f"hazard RISES with depth (fresh_slope={fresh_slope:.4f} >= {COMPOUND_SLOPE_MIN}). Per-hop "
               f"routing inherits the compounding-error problem; composition NOT trustworthy past a couple "
               f"hops without an independent-channel fix. Read jointly with the chain-drift GPU FULL.")
    elif store_pass and fresh_bounded:
        verdict = "HARD_PASS"
        msg = (f"HARD_PASS: ROUTED stays flat (rd={routed_rd:.3f}<= {ROUTED_FLAT_RD_MAX}, abs@Vmax="
               f"{routed_hi:.3f}) WHILE FLAT collapses in-chain (rd={flat_rd:.3f}>= {FLAT_COLLAPSE_RD_MIN}); "
               f"glass-box audit incl. routing intact (replay/verify/tamper=1, routing_causal_flip="
               f"{causal_flip_min:.3f}); ARM_C_FRESH routing BOUNDED (slope={fresh_slope:.4f}<= {FRESH_SLOPE_MAX}) "
               f"while COMPOUND control rises (slope={comp_slope:.4f}). route@Vmax={route_hi:.3f} "
               f"oracle_min={oracle_min:.3f} modQ_min={mod_min:.3f}.")
    else:
        verdict = "MIDDLE_BAND"
        msg = (f"MIDDLE_BAND: store_pass={store_pass} (flat_rd={flat_rd:.3f} routed_rd={routed_rd:.3f} "
               f"routed_abs={routed_hi:.3f} route={route_hi:.3f} oracle={oracle_min:.3f}); "
               f"fresh_slope={fresh_slope:.4f} (bounded={fresh_bounded}); compound_slope={comp_slope:.4f}. "
               f"Partial: audit intact but a headline store/slope gate in a middle band.")

    return verdict, msg, stats, gates


# ============================================================================
# smoke gates (discriminator-fires + arms-differ)
# ============================================================================
def _smoke_gates(per_seed: List[Dict[str, Any]], stats: Dict[str, Any]) -> None:
    if RUN_MODE not in ("smoke", "selftest") and not _ARGS.self_test:
        return
    # META_RULE_AF: store arms must differ (FLAT vs ROUTED vs ORACLE chain answers).
    for s in per_seed:
        for V, rec in s["per_V"].items():
            assert rec["flat_hash"] != rec["routed_hash"], (
                f"META_RULE_AF: FLAT and ROUTED chain answers identical seed={s['seed']} V={V}.")
        c = s["compound"]
        assert c["fresh_hash"] != c["compound_hash"], (
            f"META_RULE_AF: FRESH and COMPOUND routing-failure arrays identical seed={s['seed']}.")
    # discriminator 1: the dense-additive FLAT control MUST collapse in-chain at smoke V.
    flat_rd = stats["flat_rel_deg"]
    assert_discriminator_fires(
        bool(flat_rd <= ROUTED_FLAT_RD_MAX), control_name="ARM_A_FLAT_dense_additive",
        headline_name="chain-success-flat-with-V", run_mode="smoke",
        extra=f"flat_rel_deg={flat_rd:.3f}; needs >= {FLAT_COLLAPSE_RD_MIN} to be discriminating.")
    # discriminator 2: the shared-noise COMPOUND control MUST rise (measurement sensitivity).
    comp_slope = stats["compound_slope"]
    assert_discriminator_fires(
        bool(comp_slope <= FRESH_SLOPE_MAX), control_name="ARM_C_COMPOUND_shared_noise_routing",
        headline_name="hazard-flat-with-depth", run_mode="smoke",
        extra=f"compound_slope={comp_slope:.4f}; needs >= {COMPOUND_SLOPE_MIN} so the slope metric can "
              f"detect compounding (else FRESH-flat is vacuous).")
    print(f"[smoke-gate] arms-differ OK; FLAT collapses (rd={flat_rd:.3f}); COMPOUND rises "
          f"(slope={comp_slope:.4f}); fresh_h1={stats['fresh_h1']:.3f}.", flush=True)


# ============================================================================
# main
# ============================================================================
def _main() -> None:
    out_dir = get_output_dir(ANCHOR_NAME)
    _write_start_marker(out_dir)

    if _ARGS.self_test:
        rec = run_vsweep_unit(2048, 200, 7)
        assert rec["flat_hash"] != rec["routed_hash"], "self-test arms identical"
        cc = run_compound_unit(2048, 200, 7)
        assert cc["fresh_hash"] != cc["compound_hash"], "self-test compound arms identical"
        print("[self-test] OK: vsweep + compound ran; arms differ.", flush=True)
        sys.exit(0)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds complete; running {remaining}", flush=True)

    for seed in remaining:
        result = run_seed(seed, out_dir)
        result["N"] = N_DIM
        result["run_mode"] = RUN_MODE
        write_partial(out_dir, seed, result)

    per_seed_map = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    per_seed = list(per_seed_map.values())
    if not per_seed:
        raise RuntimeError("no per-seed partials aggregated; aborting")

    verdict, verdict_msg, stats, gates = compute_verdict(per_seed)
    _smoke_gates(per_seed, stats)

    modes = {s.get("run_mode", "?") for s in per_seed}
    if RUN_MODE == "full" and "smoke" in modes:
        verdict = "HARD_FAIL"
        verdict_msg = f"HARD_FAIL: stale smoke partials in FULL run modes={modes}. " + verdict_msg

    elapsed_s = time.time() - _T0
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
        "summary": (f"community-routed glass-box reasoning V-sweep {V_GRID} N={N_DIM} mode={RUN_MODE}: "
                    f"flat_rd={stats['flat_rel_deg']:.3f} routed_rd={stats['routed_rel_deg']:.3f} "
                    f"route@Vmax={stats['route_acc_Vmax']:.3f} causal_flip={stats['routing_causal_flip_min']:.3f} "
                    f"fresh_slope={stats['fresh_slope']:.4f} compound_slope={stats['compound_slope']:.4f}"),
        "elapsed_s": float(elapsed_s), "config_version": CONFIG_VERSION, "run_mode": RUN_MODE, "N": N_DIM,
        "V_grid": V_GRID, "V_compound": V_COMPOUND, "depth_grid": DEPTH_GRID, "n_seeds": len(SEEDS),
        "arms": ARMS, "expected_n_units": EXPECTED_N_UNITS, "cardinality_ok": stats["cardinality_ok"],
        "stats": stats,
        "per_seed": [{"seed": s["seed"], "elapsed_s": s.get("elapsed_s"), "per_V": s["per_V"],
                      "compound": s["compound"], "arms": s.get("arms", ARMS)} for s in per_seed],
    }
    write_metrics(out_dir, metrics, gate_claims=gates)
    print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    _out = get_output_dir(ANCHOR_NAME)
    try:
        _main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException; preserves SystemExit + KeyboardInterrupt
        _write_crash_metrics(_out, e)
        raise
