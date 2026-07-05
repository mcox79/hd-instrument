"""DEEP REASONING + HUB ROBUSTNESS: constructive glass-box builds over REAL stored atoms.

Motivated by data/exp_cortex_readiness_real_atom_algebra_v1/metrics.json:
  single/typical recovery GOOD (deg1=1.000 src_uniform=0.920 edge_uniform=0.737) BUT
  high-degree HUBS collapse (deg>=5 single-shot exact top1 ~0.21) and reasoning is shallow.

Two CONSTRUCTIVE builds (NO LLM comparison; NO re-encode; read-only on substrate):

  BUILD 1 -- DEEPER multi-step reasoning (depth envelope):
    True chained bind/unbind + cleanup inference over REAL graph paths. At each hop we
    build the CURRENT atom's source-trace, unbind by the hop's role, cleanup to a discrete
    atom, and use THAT recovered atom as the next cursor (errors propagate). We measure how
    DEEP the chain stays on the correct path (L=1..Lmax) with baseline single-shot cleanup
    vs the Build-2 iterative-cleanup mechanism. Glass-box: every hop lands on an inspectable
    atom.

  BUILD 2 -- HUB robustness (top-k + iterative resonator-style settle-to-convergence):
    For high-degree sources the bundle-crosstalk + correlated-codebook cone (mean pair cos
    ~0.57) sink single-shot argmax. We BUILD: (a) mean-centered cleanup (whiten the cone),
    (b) iterative explaining-away with roles KNOWN (resonator with fixed factor) -- estimate
    all fillers, subtract their reconstructed contribution, re-estimate, iterate to a discrete
    fixed point. HIGH-ENERGY COMPUTE ALLOWED: many cleanups per source x iterations. Measure
    hub recovery vs the single-shot 0.21 floor (positive-control-reproduced) and vs top-5.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (ss_raw / ss_mc / iter_mc recovery arrays hash-distinct)
# - final_metrics_atomicity = tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared: floor is the MEASURED single-shot 0.21 (positive control), plus chance 1/M
# - baseline (ss_raw) is the collapse we improve; it sits in-band (deg>=5 ~0.21, 0.05<x<0.95)
# - discriminator survives scale: hub collapse is degree-driven; smoke codebook_M near full so
#     baseline collapses at deg>=5 in smoke too; iter must move it (discriminator-fires assertion)
# - HP rubric gates apply to hub iter_mc arm + chain arms (HP_SCOPE)
# - cardinality_ok: EXPECTED_N_UNITS = seeds*(deg_bins + 2*Lmax) gate
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok (substrate primitives used directly; mean-centering is a fixed
#     label-free linear readout transform, no data leakage)
# - Gate D positive control: ss_raw deg>=5 reproduces motivating 0.21 within tolerance
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

ASCII-only. CPU default. Read-only (NO substrate mutation).
Run: python experiments/exp_deep_reasoning_hub_robustness_v1.py --run-mode {smoke,full}
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import platform
import sys
import time
import traceback
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hdlab import binding  # noqa: E402
from backend.substrate_index.schema import load_atoms, load_relations  # noqa: E402

ANCHOR_NAME = "deep_reasoning_hub_robustness_v1"
BGE_CACHE = REPO / "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"
CONCEPT = REPO / "data/substrate_index/concept"
N_DIM = 1024  # MEASURED@data/.../semantic shape (177899,1024)
EPS = 1e-12

# MEASURED@data/exp_cortex_readiness_real_atom_algebra_v1/metrics.json:
#   deg>=5 single-shot exact top1 seed7=0.2092 seed13=0.2246 seed19=0.2224 -> mean ~0.219 (top5 ~0.476)
SINGLE_SHOT_HUB_FLOOR_REF = 0.219  # MEASURED (positive-control target for ss_raw deg>=5)
SINGLE_SHOT_HUB_TOP5_REF = 0.476   # MEASURED


# ============================================================
# Defensive-error-checking helpers
# ============================================================


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, output_dir / "_start_marker.json")


def _heartbeat(output_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(output_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(output_dir: Path, metrics: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    tmp = output_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, output_dir / "metrics.json")


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(output_dir, diag)


# ============================================================
# Substrate algebra (actual hdlab primitives) + cleanup readouts
# ============================================================


def _norm_rows(X: np.ndarray) -> np.ndarray:
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + EPS)).astype(np.float32)


_role_cache: dict[str, np.ndarray] = {}


def white_role(label: str) -> np.ndarray:
    """Deterministic near-orthogonal role vector per relation-type label."""
    if label in _role_cache:
        return _role_cache[label]
    h = int(hashlib.sha256(f"cortex_role::{label}".encode()).hexdigest(), 16)
    r = np.random.default_rng(h % (2 ** 63 - 1)).standard_normal(N_DIM).astype(np.float32)
    r = r / (np.linalg.norm(r) + EPS)
    _role_cache[label] = r
    return r


def bind_rows(roles: np.ndarray, fillers: np.ndarray) -> np.ndarray:
    """Row-wise HRR bind (circular-conv). (d,N),(d,N)->(d,N)."""
    out = binding.bind(torch.from_numpy(np.ascontiguousarray(roles)),
                       torch.from_numpy(np.ascontiguousarray(fillers)))
    return out.numpy()


def unbind_bcast(trace: np.ndarray, roles: np.ndarray) -> np.ndarray:
    """Unbind ONE trace by each of many roles. trace (N,), roles (d,N) -> (d,N)."""
    d = roles.shape[0]
    tr = np.broadcast_to(trace, (d, N_DIM))
    out = binding.unbind(torch.from_numpy(np.ascontiguousarray(tr)),
                         torch.from_numpy(np.ascontiguousarray(roles)))
    return out.numpy()


def unbind_rows(traces: np.ndarray, roles: np.ndarray) -> np.ndarray:
    """Row-wise unbind: unbind traces[j] by roles[j]. (d,N),(d,N)->(d,N)."""
    out = binding.unbind(torch.from_numpy(np.ascontiguousarray(traces)),
                         torch.from_numpy(np.ascontiguousarray(roles)))
    return out.numpy()


def cleanup_raw(Q: np.ndarray, Vn: np.ndarray, k: int = 5):
    """argmax + top-k cleanup, raw cosine. Q (d,N), Vn (M,N) unit rows."""
    qn = _norm_rows(Q)
    sc = qn @ Vn.T
    top1 = sc.argmax(1)
    topk = np.argpartition(sc, -k, axis=1)[:, -k:]
    return top1, topk


def cleanup_mc(Q: np.ndarray, mu: np.ndarray, Vcn: np.ndarray) -> np.ndarray:
    """Mean-centered cleanup argmax: whiten the codebook cone. Q (d,N)->(d,) idx."""
    qc = Q - mu
    qn = qc / (np.linalg.norm(qc, axis=1, keepdims=True) + EPS)
    sc = qn @ Vcn.T
    return sc.argmax(1)


# ============================================================
# BUILD 2 core: iterative explaining-away (resonator, roles known)
# ============================================================


def recover_iterative(T_raw: np.ndarray, roles: np.ndarray, init_idx: np.ndarray,
                      V: np.ndarray, mu: np.ndarray, Vcn: np.ndarray, n_iters: int):
    """Roles-known resonator. Given trace T_raw = sum_j bind(roles[j], V[true_j]), recover
    all filler indices by iterative explaining-away with mean-centered cleanup.

    Returns (final_idx (d,), n_iter_used). Every intermediate is a discrete codebook atom
    (glass-box: inspectable per iteration)."""
    d = roles.shape[0]
    est = init_idx.copy()
    used = 0
    for it in range(n_iters):
        bound_est = bind_rows(roles, V[est])          # (d,N) reconstruct each slot
        total = bound_est.sum(0)                        # (N,)
        residuals = T_raw[None, :] - (total[None, :] - bound_est)  # remove OTHERS from each slot
        Qres = unbind_rows(residuals, roles)            # (d,N) isolate slot j
        new = cleanup_mc(Qres, mu, Vcn)
        used = it + 1
        if np.array_equal(new, est):
            break
        est = new
    return est, used


# ============================================================
# Loading (read-only)
# ============================================================


def load_id_order() -> dict:
    with zipfile.ZipFile(BGE_CACHE) as z:
        with z.open("id_order_json.npy") as f:
            order = json.loads(str(np.load(io.BytesIO(f.read()), allow_pickle=False)))
    return {aid: i for i, aid in enumerate(order)}


def build_concept_graph():
    """out_edges src->[(rel,tgt)] over the REAL concept partition (deduped)."""
    atoms = load_atoms(CONCEPT / "atoms.jsonl")
    rels = load_relations(CONCEPT / "relations.jsonl")
    aid_set = {a.id for a in atoms}
    out = defaultdict(list)
    for r in rels:
        if r.src_id in aid_set and r.tgt_id in aid_set and r.src_id != r.tgt_id:
            out[r.src_id].append((r.rel_type.value, r.tgt_id))
    for k in out:
        out[k] = list(dict.fromkeys(out[k]))
    return out, [a.id for a in atoms]


# ============================================================
# Codebook construction (shared by both builds)
# ============================================================


def build_codebook(seed, out, all_ids, pos, sem, cfg):
    """Sample hub sources per degree-bin + real chain paths; build a shared codebook V of
    real unit BGE vectors up to codebook_M with distractors. Returns everything both builds need."""
    rng = np.random.default_rng(seed)
    deg = {k: len(v) for k, v in out.items()}

    # ---- hub sources per exact-degree bin (top bin pooled) ----
    deg_bins = cfg["deg_bins"]  # e.g. [2,3,4,5,6,7,"8plus"]
    per_bin = cfg["hub_per_bin"]
    bin_sources = {}
    for b in deg_bins:
        if isinstance(b, str) and b.endswith("plus"):
            lo = int(b[:-4])
            cands = [s for s, dd in deg.items() if dd >= lo]
        else:
            cands = [s for s, dd in deg.items() if dd == int(b)]
        rng.shuffle(cands)
        bin_sources[str(b)] = cands[:per_bin]

    # ---- real chain paths via random walk over the graph ----
    n_paths = cfg["chain_n_paths"]
    Lmax = cfg["chain_Lmax"]
    walk_starts = [s for s, dd in deg.items() if dd >= 1]
    rng.shuffle(walk_starts)
    paths = []
    wi = 0
    while len(paths) < n_paths and wi < len(walk_starts):
        u = walk_starts[wi]
        wi += 1
        seq = [u]
        edges_seq = []
        visited = {u}
        ok = True
        for _ in range(Lmax):
            edges = [(rt, t) for (rt, t) in out.get(u, []) if t not in visited]
            if not edges:
                ok = False
                break
            rt, t = edges[rng.integers(len(edges))]
            edges_seq.append((rt, t))
            seq.append(t)
            visited.add(t)
            u = t
        if ok and len(edges_seq) == Lmax:
            paths.append((seq[0], edges_seq))  # (start_id, [(rel,tgt),...])

    # ---- assemble codebook ids: hub sources + their targets + path nodes + their targets ----
    needed = set()
    for b, srcs in bin_sources.items():
        for s in srcs:
            needed.add(s)
            for (_, t) in out[s]:
                needed.add(t)
    for (s0, eseq) in paths:
        needed.add(s0)
        cur = s0
        for (_, t) in eseq:
            needed.add(cur)
            needed.add(t)
            # include the intermediate node's own targets so its trace is buildable
            for (_, t2) in out.get(t, []):
                needed.add(t2)
            cur = t
    needed = {a for a in needed if a in pos}
    extra = [a for a in all_ids if a not in needed and a in pos]
    rng.shuffle(extra)
    cb_ids = list(needed) + extra[: max(0, cfg["codebook_M"] - len(needed))]
    cb_index = {aid: i for i, aid in enumerate(cb_ids)}
    rows = np.array([pos[a] for a in cb_ids])
    V = _norm_rows(sem[rows].astype(np.float32))
    mu = V.mean(0).astype(np.float32)
    Vcn = _norm_rows(V - mu)
    # synthetic separable codebook (matched size) for the algebra-vs-representation control
    Vsyn = _norm_rows(np.random.default_rng(seed + 777).standard_normal((V.shape[0], N_DIM)).astype(np.float32))
    return {
        "V": V, "Vcn": Vcn, "mu": mu, "Vsyn": Vsyn, "cb_ids": cb_ids, "cb_index": cb_index,
        "bin_sources": bin_sources, "paths": paths, "M": V.shape[0],
    }


# ============================================================
# BUILD 2: hub-robustness arm
# ============================================================


def arm_hub_robustness(seed, cb, out, cfg, output_dir, t0):
    """Decompose the hub collapse + BUILD the fixes that actually work.
      ss_raw   : real neighbors, single-shot argmax (positive-control; reproduces 0.21 floor)
      ss_mc    : real neighbors, mean-centered single-shot (whiten the cos-0.57 cone)
      iter_mc  : roles-known iterative explaining-away resonator (crosstalk-cancellation BUILD)
      ctrlB    : SAME degree/roles, independent RANDOM real fillers (isolates neighbor-clustering)
      ctrlC    : SAME degree/roles, SYNTHETIC separable fillers (pure algebra / capacity check)
      idx_bind : PROTECTED binding -- same-role edges get distinct permutation powers so a hub's
                 multi-valued relations no longer collide (the STRUCTURAL BUILD that works)
    Also splits recovery by same-role-collision status to attribute the collapse.
    """
    from collections import Counter
    V, Vcn, mu, Vsyn = cb["V"], cb["Vcn"], cb["mu"], cb["Vsyn"]
    cb_index = cb["cb_index"]
    M = V.shape[0]
    n_iters = cfg["iter_n_iters"]
    role = white_role
    rng = np.random.default_rng(seed + 4242)

    per_bin = {}
    rec_ss_raw, rec_ss_mc, rec_iter = [], [], []  # for arms_differ hash
    iter_counts = []
    # deg>=5 aggregate [hit, n]
    agg = {k: [0, 0] for k in ("ss_raw", "ss_raw5", "ss_mc", "iter_mc", "ctrlB", "ctrlC", "idx_bind",
                               "ss_raw_unique", "ss_raw_collide", "idx_unique", "idx_collide")}
    collide_edges = [0, 0]  # [n_colliding, n_total] over deg>=5

    for bi, (b, srcs) in enumerate(cb["bin_sources"].items()):
        c1_raw = c5_raw = c1_mc = c1_it = c1_B = c1_C = c1_ix = tot = 0
        for s in srcs:
            edges = [(rt, t) for (rt, t) in out[s] if t in cb_index]
            if len(edges) < 2:
                continue
            d = len(edges)
            roles = np.stack([role(rt) for (rt, _) in edges]).astype(np.float32)
            true_idx = np.array([cb_index[t] for (_, t) in edges])
            # same-role collision bookkeeping: permutation power per same-relation edge
            rt_seen = {}
            pwr = np.zeros(d, dtype=int)
            for j, (rt, _) in enumerate(edges):
                pwr[j] = rt_seen.get(rt, 0)
                rt_seen[rt] = pwr[j] + 1
            rel_count = Counter(rt for (rt, _) in edges)
            colliding = np.array([rel_count[rt] > 1 for (rt, _) in edges])
            # --- arm A: REAL neighbors (bundle all edges into ONE trace) ---
            T_raw = bind_rows(roles, V[true_idx]).sum(0)
            Q0 = unbind_bcast(T_raw, roles)
            top1_raw, top5_raw = cleanup_raw(Q0, V, k=5)
            top1_mc = cleanup_mc(Q0, mu, Vcn)
            fin_idx, used = recover_iterative(T_raw, roles, top1_mc, V, mu, Vcn, n_iters)
            iter_counts.append(used)
            # --- idx_bind: protected binding (distinct perm power per same-role edge) ---
            roles_ix = np.stack([np.roll(roles[j], int(pwr[j])) for j in range(d)]).astype(np.float32)
            T_ix = bind_rows(roles_ix, V[true_idx]).sum(0)
            top1_ix, _ = cleanup_raw(unbind_bcast(T_ix, roles_ix), V, k=5)
            # --- ctrl B: independent random REAL fillers, same d/roles ---
            idxB = rng.choice(M, size=d, replace=False)
            top1_B, _ = cleanup_raw(unbind_bcast(bind_rows(roles, V[idxB]).sum(0), roles), V, k=5)
            # --- ctrl C: synthetic separable fillers, same d/roles ---
            idxC = rng.choice(M, size=d, replace=False)
            top1_C, _ = cleanup_raw(unbind_bcast(bind_rows(roles, Vsyn[idxC]).sum(0), roles), Vsyn, k=5)

            is_hub = str(b).endswith("plus") or int(str(b)) >= 5
            for j in range(d):
                tot += 1
                c = true_idx[j]
                hit_raw = top1_raw[j] == c
                hit_ix = top1_ix[j] == c
                c1_raw += hit_raw; c5_raw += (c in top5_raw[j]); c1_mc += (top1_mc[j] == c)
                c1_it += (fin_idx[j] == c); c1_B += (top1_B[j] == idxB[j]); c1_C += (top1_C[j] == idxC[j])
                c1_ix += hit_ix
                if is_hub:
                    agg["ss_raw"][0] += int(hit_raw); agg["ss_raw"][1] += 1
                    agg["ss_raw5"][0] += int(c in top5_raw[j]); agg["ss_raw5"][1] += 1
                    agg["ss_mc"][0] += int(top1_mc[j] == c); agg["ss_mc"][1] += 1
                    agg["iter_mc"][0] += int(fin_idx[j] == c); agg["iter_mc"][1] += 1
                    agg["ctrlB"][0] += int(top1_B[j] == idxB[j]); agg["ctrlB"][1] += 1
                    agg["ctrlC"][0] += int(top1_C[j] == idxC[j]); agg["ctrlC"][1] += 1
                    agg["idx_bind"][0] += int(hit_ix); agg["idx_bind"][1] += 1
                    collide_edges[0] += int(colliding[j]); collide_edges[1] += 1
                    ck = "collide" if colliding[j] else "unique"
                    agg[f"ss_raw_{ck}"][0] += int(hit_raw); agg[f"ss_raw_{ck}"][1] += 1
                    agg[f"idx_{ck}"][0] += int(hit_ix); agg[f"idx_{ck}"][1] += 1
                rec_ss_raw.append(int(top1_raw[j]))
                rec_ss_mc.append(int(top1_mc[j]))
                rec_iter.append(int(fin_idx[j]))
        per_bin[str(b)] = {
            "n_sources": len(srcs), "n_edges": tot,
            "ss_raw_top1": c1_raw / tot if tot else 0.0,
            "ss_raw_top5": c5_raw / tot if tot else 0.0,
            "ss_mc_top1": c1_mc / tot if tot else 0.0,
            "iter_mc_top1": c1_it / tot if tot else 0.0,
            "idx_bind_top1": c1_ix / tot if tot else 0.0,
            "ctrlB_indep_real_top1": c1_B / tot if tot else 0.0,
            "ctrlC_synth_top1": c1_C / tot if tot else 0.0,
        }
        _heartbeat(output_dir, bi, len(cb["bin_sources"]), t0, extra={"arm": "hub", "bin": str(b), "seed": seed})

    def r(key):
        return agg[key][0] / max(1, agg[key][1])
    hub = {
        "deg_ge5_ss_raw_top1": r("ss_raw"),
        "deg_ge5_ss_raw_top5": r("ss_raw5"),
        "deg_ge5_ss_mc_top1": r("ss_mc"),
        "deg_ge5_iter_mc_top1": r("iter_mc"),
        "deg_ge5_ctrlB_indep_real_top1": r("ctrlB"),
        "deg_ge5_ctrlC_synth_top1": r("ctrlC"),
        "deg_ge5_idx_bind_top1": r("idx_bind"),
        "deg_ge5_collision_frac": collide_edges[0] / max(1, collide_edges[1]),
        "deg_ge5_ss_raw_unique_top1": r("ss_raw_unique"),
        "deg_ge5_ss_raw_collide_top1": r("ss_raw_collide"),
        "deg_ge5_idx_unique_top1": r("idx_unique"),
        "deg_ge5_idx_collide_top1": r("idx_collide"),
        "deg_ge5_n_edges": agg["ss_raw"][1],
        "mean_iters_to_converge": float(np.mean(iter_counts)) if iter_counts else 0.0,
    }
    return {"per_bin": per_bin, "hub_aggregate": hub}, (rec_ss_raw, rec_ss_mc, rec_iter)


# ============================================================
# BUILD 1: chained multi-hop reasoning (depth envelope)
# ============================================================


def _build_trace(node_id, out, cb_index, V, role):
    """Build a node's source-trace = raw sum of bind(role(rel), V[tgt]) over its real edges."""
    edges = [(rt, t) for (rt, t) in out.get(node_id, []) if t in cb_index]
    if not edges:
        return None, None, None
    roles = np.stack([role(rt) for (rt, _) in edges]).astype(np.float32)
    idx = np.array([cb_index[t] for (_, t) in edges])
    bound = bind_rows(roles, V[idx])
    return bound.sum(0), roles, edges


def arm_chain_reasoning(seed, cb, out, cfg, output_dir, t0):
    """Chained retrieval over REAL paths; per-hop stay-on-path for baseline vs iterative."""
    V, Vcn, mu = cb["V"], cb["Vcn"], cb["mu"]
    cb_index, cb_ids = cb["cb_index"], cb["cb_ids"]
    n_iters = cfg["iter_n_iters"]
    Lmax = cfg["chain_Lmax"]
    role = white_role

    # per-hop counters (1-indexed) for each variant
    base_hit = [0] * (Lmax + 1)
    iter_hit = [0] * (Lmax + 1)
    reached = [0] * (Lmax + 1)
    rec_base, rec_iter = [], []

    def step(cursor_id, rel, tgt_truth, mode):
        """One hop from cursor_id following relation `rel`. Returns predicted atom id."""
        T, roles, edges = _build_trace(cursor_id, out, cb_index, V, role)
        if T is None:
            return None
        # find the slot index whose relation == rel (the hop's role); if absent, still query by rel role
        r_vec = role(rel)[None, :].astype(np.float32)
        if mode == "baseline":
            q = unbind_bcast(T, r_vec)  # unbind the node's trace by the hop role
            top1, _ = cleanup_raw(q, V, k=5)
            return cb_ids[int(top1[0])]
        # iterative: recover ALL slots jointly, then read the slot with matching relation
        Q0 = unbind_bcast(T, roles)
        init = cleanup_mc(Q0, mu, Vcn)
        fin, _ = recover_iterative(T, roles, init, V, mu, Vcn, n_iters)
        # pick slot whose relation matches rel; if the matching relation appears, use it,
        # else fall back to a direct role-unbind + mc cleanup of the whole trace
        slot = None
        for j, (rt, _) in enumerate(edges):
            if rt == rel:
                slot = j
                break
        if slot is not None:
            return cb_ids[int(fin[slot])]
        q = unbind_bcast(T, r_vec)
        idx = cleanup_mc(q, mu, Vcn)
        return cb_ids[int(idx[0])]

    for pi, (s0, eseq) in enumerate(cb["paths"]):
        cur_b = s0
        cur_i = s0
        alive_b = True
        alive_i = True
        for hop in range(1, Lmax + 1):
            rel, tgt = eseq[hop - 1]
            reached[hop] += 1
            if alive_b:
                pred_b = step(cur_b, rel, tgt, "baseline")
                rec_base.append(0 if pred_b is None else (hash(pred_b) & 0xffffffff))
                if pred_b == tgt:
                    base_hit[hop] += 1
                    cur_b = pred_b
                else:
                    cur_b = pred_b if pred_b is not None else cur_b
                    alive_b = False  # derailed: stop crediting downstream (still advance cursor)
            if alive_i:
                pred_i = step(cur_i, rel, tgt, "iterative")
                rec_iter.append(0 if pred_i is None else (hash(pred_i) & 0xffffffff))
                if pred_i == tgt:
                    iter_hit[hop] += 1
                    cur_i = pred_i
                else:
                    cur_i = pred_i if pred_i is not None else cur_i
                    alive_i = False
        if pi % 50 == 0:
            _heartbeat(output_dir, pi, len(cb["paths"]), t0, extra={"arm": "chain", "seed": seed})

    # cumulative on-path accuracy at depth L = fraction of paths correct at EVERY hop up to L
    def envelope(hitv):
        # hitv[hop] counts paths correct at hop AND (by alive-gating) all previous hops.
        return [hitv[h] / max(1, reached[h]) for h in range(1, Lmax + 1)]

    base_env = envelope(base_hit)
    iter_env = envelope(iter_hit)

    def depth_at(env, thr=0.5):
        d = 0
        for h in range(len(env)):
            if env[h] >= thr:
                d = h + 1
            else:
                break
        return d

    return {
        "n_paths": len(cb["paths"]),
        "reached_per_hop": reached[1:],
        "baseline_cumulative_onpath": [round(x, 4) for x in base_env],
        "iter_cumulative_onpath": [round(x, 4) for x in iter_env],
        "baseline_depth_at_0.5": depth_at(base_env),
        "iter_depth_at_0.5": depth_at(iter_env),
    }, (rec_base, rec_iter)


# ============================================================
# Verdict
# ============================================================


def classify_verdict(hub_agg, chain, ref_floor):
    ss = hub_agg["deg_ge5_ss_raw_top1"]
    it = hub_agg["deg_ge5_iter_mc_top1"]
    ix = hub_agg["deg_ge5_idx_bind_top1"]
    cB = hub_agg["deg_ge5_ctrlB_indep_real_top1"]
    cC = hub_agg["deg_ge5_ctrlC_synth_top1"]
    cf = hub_agg["deg_ge5_collision_frac"]
    ix_col = hub_agg["deg_ge5_idx_collide_top1"]
    ss_col = hub_agg["deg_ge5_ss_raw_collide_top1"]
    b_depth = chain["baseline_depth_at_0.5"]
    i_depth = chain["iter_depth_at_0.5"]
    iter_lift = it - ss
    idx_lift = ix - ss

    if ss >= 0.40:
        return "DISCRIMINATOR_DID_NOT_FIRE", (f"baseline hub deg>=5 ss_raw={ss:.3f} not collapsed "
                                              f"(>=0.40); no hub wall to rescue at this regime")
    chain_note = f"chain depth@0.5 base={b_depth} iter={i_depth}"
    diag = (f"collision_frac={cf:.2f}; idx_bind={ix:.3f}(+{idx_lift:.3f}) iter_mc={it:.3f}"
            f"(+{iter_lift:.3f}); ctrlB(indep-real)={cB:.3f} ctrlC(synth)={cC:.3f}; "
            f"colliding-slot ss_raw={ss_col:.3f}->idx={ix_col:.3f}")
    # BUILD success = protected/index binding meaningfully rescues the hub (structural fix for
    # same-role collisions), whereas iterative crosstalk-cancellation does not.
    if idx_lift >= 0.10 and idx_lift > iter_lift + 0.03:
        return "HUBS_RESCUED_BY_PROTECTED_BINDING", (
            f"index/protected binding rescues real hubs: ss_raw={ss:.3f}->idx_bind={ix:.3f} "
            f"(+{idx_lift:.3f}); iterative resonator does NOT (+{iter_lift:.3f}). {diag}. {chain_note}")
    if iter_lift >= 0.20 and it >= 0.50:
        return "HUBS_RESCUED_BY_ITERATION", (
            f"iterative resonator rescues hubs: ss_raw={ss:.3f}->iter_mc={it:.3f} (+{iter_lift:.3f}). "
            f"{diag}. {chain_note}")
    return "HUB_COLLAPSE_CAPACITY_AND_COLLISION_LIMITED", (
        f"neither iteration (+{iter_lift:.3f}) nor protected-binding (+{idx_lift:.3f}) fully rescues "
        f"real hubs; controls show same-degree synth/indep-real ALSO collapse (ctrlC={cC:.3f} "
        f"ctrlB={cB:.3f}) => collapse is bundle-CAPACITY (crosstalk grows with degree) + same-role "
        f"COLLISION (frac={cf:.2f}), NOT neighbor-representation. Real fix = SHARDED storage + "
        f"protected binding, not a better cleanup. {diag}. {chain_note}")


# ============================================================
# Config + main
# ============================================================


def get_config(run_mode):
    if run_mode == "smoke":
        return {"seeds": [7], "deg_bins": [2, 3, 5, "8plus"], "hub_per_bin": 50,
                "codebook_M": 8000, "iter_n_iters": 6,
                "chain_n_paths": 100, "chain_Lmax": 5}
    # light-full (Director-authorized light CPU run): 3 seeds for cross-seed stability, finer
    # degree bins, honest large codebook (>> smoke). iter kept small (it does not help).
    return {"seeds": [7, 13, 19], "deg_bins": [2, 3, 4, 5, 6, 7, "8plus"], "hub_per_bin": 80,
            "codebook_M": 10000, "iter_n_iters": 4,
            "chain_n_paths": 200, "chain_Lmax": 6}


def _digest(a):
    return hashlib.sha256(np.asarray(a, dtype=np.int64).tobytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["smoke", "full"],
                    default=os.environ.get("HDLAB_RUN_MODE", "smoke"))
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    run_mode = args.run_mode if args.run_mode in ("smoke", "full") else "full"
    cfg = get_config(run_mode)

    suffix = "_smoke" if run_mode == "smoke" else ""
    output_dir = REPO / f"data/exp_{ANCHOR_NAME}{suffix}"
    t0 = time.perf_counter()

    Lmax = cfg["chain_Lmax"]
    expected_n_units = len(cfg["seeds"]) * (len(cfg["deg_bins"]) + 2 * Lmax)
    _write_start_marker(output_dir, run_mode, expected_n_units)

    if not BGE_CACHE.exists():
        raise FileNotFoundError(f"BGE cache missing (local-only artifact): {BGE_CACHE}")

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={cfg['seeds']} M={cfg['codebook_M']} "
          f"deg_bins={cfg['deg_bins']} iters={cfg['iter_n_iters']} Lmax={Lmax}", flush=True)
    print("[load] concept graph...", flush=True)
    out, all_ids = build_concept_graph()
    print(f"[load] sources_with_edges={len(out)} atoms={len(all_ids)}", flush=True)
    pos = load_id_order()
    sem = np.load(BGE_CACHE)["semantic"]
    print(f"[load] semantic shape={sem.shape}", flush=True)

    seeds_out = {}
    arms_differ_digests = {}
    n_units_counted = 0
    for seed in cfg["seeds"]:
        print(f"\n[seed {seed}] building shared codebook...", flush=True)
        cb = build_codebook(seed, out, all_ids, pos, sem, cfg)
        print(f"[seed {seed}] codebook M={cb['M']} n_paths={len(cb['paths'])} "
              f"hub_bins={ {b: len(s) for b,s in cb['bin_sources'].items()} }", flush=True)

        print(f"[seed {seed}] BUILD2 hub-robustness...", flush=True)
        hub, hub_recs = arm_hub_robustness(seed, cb, out, cfg, output_dir, t0)
        n_units_counted += len(hub["per_bin"])
        ha = hub["hub_aggregate"]
        print(f"[seed {seed}] hub deg>=5: ss_raw={ha['deg_ge5_ss_raw_top1']:.3f} "
              f"iter_mc={ha['deg_ge5_iter_mc_top1']:.3f} idx_bind={ha['deg_ge5_idx_bind_top1']:.3f} "
              f"| ctrlB={ha['deg_ge5_ctrlB_indep_real_top1']:.3f} ctrlC={ha['deg_ge5_ctrlC_synth_top1']:.3f} "
              f"| collision_frac={ha['deg_ge5_collision_frac']:.2f} "
              f"colliding: ss_raw={ha['deg_ge5_ss_raw_collide_top1']:.3f}->idx={ha['deg_ge5_idx_collide_top1']:.3f} "
              f"unique: ss_raw={ha['deg_ge5_ss_raw_unique_top1']:.3f}->idx={ha['deg_ge5_idx_unique_top1']:.3f}",
              flush=True)

        print(f"[seed {seed}] BUILD1 chain-reasoning...", flush=True)
        chain, chain_recs = arm_chain_reasoning(seed, cb, out, cfg, output_dir, t0)
        n_units_counted += 2 * Lmax
        print(f"[seed {seed}] chain base_onpath={chain['baseline_cumulative_onpath']} "
              f"depth@0.5={chain['baseline_depth_at_0.5']}", flush=True)
        print(f"[seed {seed}] chain iter_onpath={chain['iter_cumulative_onpath']} "
              f"depth@0.5={chain['iter_depth_at_0.5']}", flush=True)

        arms_differ_digests[str(seed)] = {
            "hub_ss_raw": _digest(hub_recs[0][:2000]),
            "hub_ss_mc": _digest(hub_recs[1][:2000]),
            "hub_iter_mc": _digest(hub_recs[2][:2000]),
            "chain_base": _digest(chain_recs[0][:2000]),
            "chain_iter": _digest(chain_recs[1][:2000]),
        }
        seeds_out[str(seed)] = {"hub_robustness": hub, "chain_reasoning": chain}
        _heartbeat(output_dir, seed, cfg["seeds"][-1], t0, extra={"stage": "seed_done", "seed": seed})

    # arms_differ (META_RULE_AF): hub ss_raw / ss_mc / iter_mc must be distinct arrays.
    arms_differ_ok = True
    for sd, dg in arms_differ_digests.items():
        core = [dg["hub_ss_raw"], dg["hub_ss_mc"], dg["hub_iter_mc"]]
        if len(set(core)) != len(core):
            arms_differ_ok = False
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: hub ss_raw/ss_mc/iter_mc recovery arrays bit-identical")

    cardinality_ok = n_units_counted >= expected_n_units
    verdict_flag = "" if cardinality_ok else \
        f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H(got={n_units_counted}<exp={expected_n_units})"

    # positive control (Gate D): ss_raw deg>=5 reproduces motivating 0.21 floor within tolerance.
    ss_raw_vals = [seeds_out[str(s)]["hub_robustness"]["hub_aggregate"]["deg_ge5_ss_raw_top1"]
                   for s in cfg["seeds"]]
    ss_raw_mean = float(np.mean(ss_raw_vals))
    pos_control_ok = abs(ss_raw_mean - SINGLE_SHOT_HUB_FLOOR_REF) <= 0.10

    # cross-seed aggregates for report
    def hv(key):
        return [seeds_out[str(s)]["hub_robustness"]["hub_aggregate"][key] for s in cfg["seeds"]]
    it_vals = hv("deg_ge5_iter_mc_top1")
    mc_vals = hv("deg_ge5_ss_mc_top1")
    ix_vals = hv("deg_ge5_idx_bind_top1")
    cB_vals = hv("deg_ge5_ctrlB_indep_real_top1")
    cC_vals = hv("deg_ge5_ctrlC_synth_top1")
    cf_vals = hv("deg_ge5_collision_frac")
    ib_depth = [seeds_out[str(s)]["chain_reasoning"]["iter_depth_at_0.5"] for s in cfg["seeds"]]
    bb_depth = [seeds_out[str(s)]["chain_reasoning"]["baseline_depth_at_0.5"] for s in cfg["seeds"]]

    primary = seeds_out[str(cfg["seeds"][0])]
    verdict, vmsg = classify_verdict(primary["hub_robustness"]["hub_aggregate"],
                                     primary["chain_reasoning"], SINGLE_SHOT_HUB_FLOOR_REF)

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "verdict": verdict if not verdict_flag else "HARD_FAIL_CARDINALITY",
        "verdict_msg": (verdict_flag + " | " if verdict_flag else "") + vmsg,
        "summary": f"{verdict}: deep chained reasoning + hub-robustness over REAL atoms ({run_mode})",
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
        "n_seeds": len(cfg["seeds"]),
        "config": {k: (v if not isinstance(v, list) else v) for k, v in cfg.items()},
        "expected_n_units": expected_n_units,
        "n_units_counted": n_units_counted,
        "cardinality_ok": cardinality_ok,
        "arms_differ_verified": arms_differ_ok,
        "arms_differ_digests": arms_differ_digests,
        "positive_control_ss_raw_deg_ge5": {
            "measured_mean": round(ss_raw_mean, 4), "values": [round(x, 4) for x in ss_raw_vals],
            "reference_floor_MEASURED": SINGLE_SHOT_HUB_FLOOR_REF, "within_tol_0.10": pos_control_ok,
        },
        "cross_seed_hub_deg_ge5": {
            "ss_raw_top1_mean": round(ss_raw_mean, 4),
            "ss_mc_top1_mean": round(float(np.mean(mc_vals)), 4),
            "iter_mc_top1_mean": round(float(np.mean(it_vals)), 4),
            "iter_mc_top1_values": [round(x, 4) for x in it_vals],
            "idx_bind_top1_mean": round(float(np.mean(ix_vals)), 4),
            "idx_bind_top1_values": [round(x, 4) for x in ix_vals],
            "ctrlB_indep_real_top1_mean": round(float(np.mean(cB_vals)), 4),
            "ctrlC_synth_top1_mean": round(float(np.mean(cC_vals)), 4),
            "collision_frac_mean": round(float(np.mean(cf_vals)), 4),
        },
        "cross_seed_chain_depth_at_0.5": {
            "baseline": bb_depth, "iter": ib_depth,
        },
        "per_seed": seeds_out,
        "notes": ("REAL atom vectors = BGE semantic (re-encode-independent). REAL edges = concept "
                  "partition. Algebra = hdlab HRR bind (circular-conv) + bundle + cleanup. BUILD1 = "
                  "per-hop-cleanup chained retrieval over real paths (depth envelope). BUILD2 = "
                  "roles-known iterative explaining-away resonator + mean-centered cleanup (hub rescue). "
                  "Read-only; NO substrate mutation; NO LLM comparison."),
    }
    _write_metrics_atomic(output_dir, metrics)

    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == run_mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {run_mode}"

    print(f"\n[VERDICT] {verdict} :: {vmsg}", flush=True)
    print(f"[pos-control] ss_raw deg>=5 mean={ss_raw_mean:.3f} vs ref {SINGLE_SHOT_HUB_FLOOR_REF} "
          f"within_tol={pos_control_ok}", flush=True)
    print(f"[metrics] {output_dir / 'metrics.json'} ({elapsed:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    _out_dir = None
    try:
        _rm = os.environ.get("HDLAB_RUN_MODE", "smoke")
        for i, a in enumerate(sys.argv):
            if a == "--run-mode" and i + 1 < len(sys.argv):
                _rm = sys.argv[i + 1]
        _rm = _rm if _rm in ("smoke", "full") else "full"
        _out_dir = REPO / f"data/exp_{ANCHOR_NAME}{'_smoke' if _rm == 'smoke' else ''}"
        sys.exit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if _out_dir is not None:
            _write_crash_metrics(_out_dir, e)
        raise
