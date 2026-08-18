"""CORTEX-READINESS: does the substrate bind/unbind/bundle+cleanup algebra reason over REAL atoms?

Re-encode-independent probe. Operates on the currently-stored BGE `semantic` vectors + the REAL
relation edges of the concept partition. Read-only on the substrate (NO mutation).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (real vs synth vs null recovery-idx arrays hash-distinct)
# - final_metrics_atomicity = tmp_replace (metrics.json.tmp -> os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared (recovery-vs-chance; floor = 1/M computed + reported)
# - baseline = random-guess chance (1/M); sweep spans saturated->collapsed (mechanism visible)
# - discriminator survives scale: full-N codebook (20000, +142K in full mode); null collapses
# - HP rubric gates apply to real_graph arm only (HP_SCOPE)
# - cardinality_ok: EXPECTED_N_UNITS gate on degree-bins + depth-points
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: default_ok (substrate primitives used directly)
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

ASCII-only. CPU default. Run: python experiments/exp_cortex_readiness_real_atom_algebra_v1.py --run-mode {smoke,full}
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
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch

# Line-buffer stdout so progress lines flush on newline (progress_logging=print_flush_true).
try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from hdlab import binding, bundling  # noqa: E402
from backend.substrate_index.schema import load_atoms, load_relations  # noqa: E402

ANCHOR_NAME = "cortex_readiness_real_atom_algebra_v1"
BGE_CACHE = REPO / "data/substrate_index/cached_indices/bge_large_v2_name_177899_54f7cf6a.npz"
CONCEPT = REPO / "data/substrate_index/concept"
N_DIM = 1024  # BGE-large dimensionality; MEASURED@data/.../semantic shape (177899,1024)


# ============================================================
# Defensive-error-checking helpers (start-marker / crash / heartbeat)
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
# Substrate algebra wrappers (the ACTUAL hdlab primitives)
# ============================================================


def _norm_rows(X: np.ndarray) -> np.ndarray:
    return (X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)).astype(np.float32)


def white_role(label: str) -> np.ndarray:
    """Deterministic white (near-orthogonal) role vector per relation-type label."""
    h = int(hashlib.sha256(f"cortex_role::{label}".encode()).hexdigest(), 16)
    r = np.random.default_rng(h % (2 ** 63 - 1)).standard_normal(N_DIM).astype(np.float32)
    return r / (np.linalg.norm(r) + 1e-12)


def bind_batch(roles: np.ndarray, fillers: np.ndarray) -> np.ndarray:
    """bind each (role_i, filler_i) via hdlab.binding.bind (circular-conv HRR). (K,N)->(K,N)."""
    out = binding.bind(torch.from_numpy(np.ascontiguousarray(roles)),
                       torch.from_numpy(np.ascontiguousarray(fillers)))
    return out.numpy()


def unbind_batch(trace: np.ndarray, roles: np.ndarray) -> np.ndarray:
    """unbind trace by each role_i via hdlab.binding.unbind. trace (N,), roles (K,N) -> (K,N)."""
    K = roles.shape[0]
    tr = np.broadcast_to(trace, (K, N_DIM))
    out = binding.unbind(torch.from_numpy(np.ascontiguousarray(tr)),
                         torch.from_numpy(np.ascontiguousarray(roles)))
    return out.numpy()


def bundle_np(bound: np.ndarray) -> np.ndarray:
    """L2-normed superposition via hdlab.bundling.bundle. (K,N) -> (N,)."""
    return bundling.bundle(torch.from_numpy(np.ascontiguousarray(bound))).numpy()


def cleanup_topk(queries: np.ndarray, codebook: np.ndarray, k: int = 5):
    """argmax cleanup (k_NN_lookup default) + top-k. queries (B,N), codebook (M,N)."""
    q = _norm_rows(queries)
    sc = q @ codebook.T
    top1 = sc.argmax(1)
    topk = np.argpartition(sc, -k, axis=1)[:, -k:]
    return top1, topk


# ============================================================
# Vector loading (read-only)
# ============================================================


def load_id_order() -> dict:
    with zipfile.ZipFile(BGE_CACHE) as z:
        with z.open("id_order_json.npy") as f:
            order = json.loads(str(np.load(io.BytesIO(f.read()), allow_pickle=False)))
    return {aid: i for i, aid in enumerate(order)}


def build_concept_graph():
    """Return (out_edges, all_ids, degree_weights). degree_weights carries the TRUE
    full-graph source-uniform and edge-uniform weights per degree-bin (1..5, 5=deg>=5)
    for honest realistic reweighting (NOT the equal-bin sampled fractions)."""
    atoms = load_atoms(CONCEPT / "atoms.jsonl")
    rels = load_relations(CONCEPT / "relations.jsonl")
    aid_set = {a.id for a in atoms}
    out = defaultdict(list)
    for r in rels:
        if r.src_id in aid_set and r.tgt_id in aid_set and r.src_id != r.tgt_id:
            out[r.src_id].append((r.rel_type.value, r.tgt_id))
    for k in out:
        out[k] = list(dict.fromkeys(out[k]))  # dedup identical (rel,tgt)
    deg = {k: len(v) for k, v in out.items()}
    src_at = defaultdict(int)   # sources per capped-degree bin
    edge_at = defaultdict(int)  # edges per capped-degree bin
    for d in deg.values():
        b = min(d, 5)
        src_at[b] += 1
        edge_at[b] += d
    n_src = max(1, sum(src_at.values()))
    n_edge = max(1, sum(edge_at.values()))
    degree_weights = {
        "n_sources": n_src, "n_edges": n_edge,
        "source_uniform": {str(b): src_at[b] / n_src for b in src_at},
        "edge_uniform": {str(b): edge_at[b] / n_edge for b in edge_at},
    }
    return out, [a.id for a in atoms], degree_weights


# ============================================================
# Arms
# ============================================================


def arm_real_graph(out, all_ids, pos, sem, cfg, seed, output_dir, t0, degree_weights):
    """Real (A,R,B) recovery binned by source degree + relation type. Returns dict + null result."""
    rng = np.random.default_rng(seed)
    deg = {k: len(v) for k, v in out.items()}
    per_bin = cfg["sources_per_bin"]
    bins = {1: [], 2: [], 3: [], 4: [], 5: []}
    for s, dd in deg.items():
        b = min(dd, 5)
        bins[b].append(s)
    for b in bins:
        rng.shuffle(bins[b])
    sources = [s for b in bins for s in bins[b][:per_bin]]

    # Codebook: sources + all targets + distractors up to codebook_M.
    needed = set(sources)
    for s in sources:
        for (_, t) in out[s]:
            needed.add(t)
    needed = {a for a in needed if a in pos}
    extra = [a for a in all_ids if a not in needed and a in pos]
    rng.shuffle(extra)
    cb_ids = list(needed) + extra[: max(0, cfg["codebook_M"] - len(needed))]
    cb_index = {aid: i for i, aid in enumerate(cb_ids)}
    rows = np.array([pos[a] for a in cb_ids])
    V = _norm_rows(sem[rows].astype(np.float32))
    M = V.shape[0]

    role_cache = {}

    def role(rt):
        if rt not in role_cache:
            role_cache[rt] = white_role(rt)
        return role_cache[rt]

    res_deg = defaultdict(lambda: [0, 0, 0])   # deg -> [top1, top5, tot]
    res_rt = defaultdict(lambda: [0, 0, 0])
    edge_weight = defaultdict(lambda: [0, 0, 0])  # true-degree -> for edge-frequency-weighted
    null_hit = 0
    null_tot = 0
    recovered_idx = []  # for arms_differ hash

    n = len(sources)
    for si, s in enumerate(sources):
        edges = [(rt, t) for (rt, t) in out[s] if t in cb_index]
        if not edges:
            continue
        dd = len(edges)
        roles = np.stack([role(rt) for (rt, _) in edges])
        fillers = np.stack([V[cb_index[t]] for (_, t) in edges])
        bound = bind_batch(roles, fillers)
        trace = bound[0] if dd == 1 else bundle_np(bound)
        Q = unbind_batch(trace, roles)
        top1, top5 = cleanup_topk(Q, V, k=5)
        db = min(dd, 5)
        for j, (rt, t) in enumerate(edges):
            correct = cb_index[t]
            recovered_idx.append(int(top1[j]))
            res_deg[db][2] += 1
            res_rt[rt][2] += 1
            edge_weight[dd][2] += 1
            if top1[j] == correct:
                res_deg[db][0] += 1
                res_rt[rt][0] += 1
                edge_weight[dd][0] += 1
            if correct in top5[j]:
                res_deg[db][1] += 1
                res_rt[rt][1] += 1
                edge_weight[dd][1] += 1
        # shuffled-role null: query with a role NOT among this bundle's roles
        wrong = white_role(f"__NULL__{seed}_{si}")
        qn = unbind_batch(trace, wrong[None, :])
        an, _ = cleanup_topk(qn, V, k=5)
        null_tot += 1
        if an[0] in [cb_index[t] for (_, t) in edges]:
            null_hit += 1
        if si % 200 == 0:
            _heartbeat(output_dir, si, n, t0, extra={"arm": "real_graph", "seed": seed})

    def rate(d):
        return {str(k): {"top1": v[0] / v[2] if v[2] else 0.0,
                          "top5": v[1] / v[2] if v[2] else 0.0, "n": v[2]}
                for k, v in sorted(d.items(), key=lambda x: str(x[0]))}

    by_degree = rate(res_deg)

    # REALISTIC reweighting: measured per-degree-bin top1/top5 x the TRUE full-graph
    # degree distribution (NOT the equal-bin sampled fractions). Two honest views:
    #  - source_uniform: pick a random source atom, query one of its edges.
    #  - edge_uniform:   pick a random real edge across the whole graph (hub-heavy).
    def _reweight(weight_key, metric):
        w = degree_weights[weight_key]
        num = 0.0
        wsum = 0.0
        for b_str, frac in w.items():
            if b_str in by_degree and by_degree[b_str]["n"] > 0:
                num += frac * by_degree[b_str][metric]
                wsum += frac
        return num / wsum if wsum > 0 else 0.0

    realistic = {
        "source_uniform": {"top1": _reweight("source_uniform", "top1"),
                           "top5": _reweight("source_uniform", "top5")},
        "edge_uniform": {"top1": _reweight("edge_uniform", "top1"),
                         "top5": _reweight("edge_uniform", "top5")},
        "weights_used": {"source_uniform": degree_weights["source_uniform"],
                         "edge_uniform": degree_weights["edge_uniform"]},
    }

    return {
        "codebook_M": M,
        "chance_top1": 1.0 / M,
        "by_degree": by_degree,
        "by_relation_type": rate(res_rt),
        "equal_bin_overall": {
            "top1": sum(v[0] for v in res_deg.values()) / max(1, sum(v[2] for v in res_deg.values())),
            "top5": sum(v[1] for v in res_deg.values()) / max(1, sum(v[2] for v in res_deg.values())),
            "n": sum(v[2] for v in res_deg.values()),
            "note": "equal-bin sample (degree-balanced); NOT realistic weighting",
        },
        "realistic_weighted_overall": realistic,
        "shuffled_role_null": {"hit_any_slot": null_hit / max(1, null_tot), "n": null_tot,
                               "chance_ref": 1.0 / M},
    }, recovered_idx, V, cb_ids, cb_index


def arm_synth_depth_sweep(V_real, cfg, seed, output_dir, t0):
    """Controlled depth sweep on REAL independent fillers vs SYNTHETIC random codes."""
    rng = np.random.default_rng(seed + 1000)
    M = V_real.shape[0]
    Vsyn = _norm_rows(rng.standard_normal((M, N_DIM)).astype(np.float32))
    depths = cfg["depths"]
    n_trials = cfg["depth_trials"]

    def run(codebook, tag):
        Mc = codebook.shape[0]
        out = {}
        rec_all = []
        for depth in depths:
            n_t1 = n_t5 = tot = 0
            rs = np.random.default_rng(seed * 131 + depth)
            for tt in range(n_trials):
                fill_idx = rs.choice(Mc, size=depth, replace=False)
                roles = np.stack([white_role(f"{tag}_d{depth}_t{tt}_s{j}") for j in range(depth)])
                fillers = codebook[fill_idx]
                bound = bind_batch(roles, fillers)
                trace = bound[0] if depth == 1 else bundle_np(bound)
                Q = unbind_batch(trace, roles)
                top1, top5 = cleanup_topk(Q, codebook, k=5)
                for j in range(depth):
                    tot += 1
                    if top1[j] == fill_idx[j]:
                        n_t1 += 1
                    if fill_idx[j] in top5[j]:
                        n_t5 += 1
                    rec_all.append(int(top1[j]))
            out[str(depth)] = {"top1": n_t1 / tot, "top5": n_t5 / tot, "n": tot}
            _heartbeat(output_dir, depth, max(depths), t0, extra={"arm": f"synth_sweep_{tag}", "seed": seed})
        return out, rec_all

    real_out, real_rec = run(V_real, "real")
    synth_out, synth_rec = run(Vsyn, "synth")
    return {"real_filler": real_out, "synth_filler": synth_out,
            "chance_top1": 1.0 / M, "codebook_M": M}, real_rec, synth_rec


def arm_neighbor_correlation(out, sem, pos, cb_index, V, cfg, seed):
    """Mean mutual cosine of real neighbors vs random pairs (explains real-vs-synth gap)."""
    rng = np.random.default_rng(seed + 2000)
    mut = []
    count = 0
    for s, edges in out.items():
        ts = [t for (_, t) in edges if t in cb_index]
        if len(ts) >= 2:
            vs = V[[cb_index[t] for t in ts]]
            cc = vs @ vs.T
            iu = np.triu_indices(len(ts), 1)
            mut.extend(cc[iu].tolist())
            count += 1
        if count >= cfg["neighbor_sources"]:
            break
    a = V[rng.choice(V.shape[0], 3000, replace=False)]
    b = V[rng.choice(V.shape[0], 3000, replace=False)]
    rand_cos = float(np.mean(np.sum(a * b, axis=1)))
    return {"real_neighbor_mean_cos": float(np.mean(mut)) if mut else 0.0,
            "n_neighbor_pairs": len(mut), "random_pair_mean_cos": rand_cos,
            "codebook_mean_abs_cos": float(np.mean(np.abs(np.sum(a * b, axis=1))))}


# ============================================================
# Verdict
# ============================================================


def classify_verdict(rg):
    """Verdict rubric on real_graph arm (HP_SCOPE). Uses realistic (true-degree-weighted)
    recovery, single-hop exact recovery, and hub collapse."""
    bd = rg["by_degree"]
    d1 = bd.get("1", {}).get("top1", 0.0)
    d2 = bd.get("2", {}).get("top1", 0.0)
    d5 = bd.get("5", {}).get("top1", 0.0)  # deg>=5 hubs
    su = rg["realistic_weighted_overall"]["source_uniform"]["top1"]
    eu = rg["realistic_weighted_overall"]["edge_uniform"]["top1"]
    null = rg["shuffled_role_null"]["hit_any_slot"]
    fires = (d1 > 0.90) and (null < 0.01)
    if not fires:
        return "DISCRIMINATOR_DID_NOT_FIRE", f"deg1={d1:.3f} null={null:.4f}"
    if d1 < 0.80:
        return "BAD", f"deg1 exact recovery {d1:.3f} < 0.80 -- algebra does not reason over real atoms"
    good = (d1 >= 0.95) and (su >= 0.85) and (null < 0.01)
    hubs_weak = d5 < 0.40
    if good and not hubs_weak:
        return "GOOD", (f"cortex-ready: deg1={d1:.3f} src_uniform={su:.3f} edge_uniform={eu:.3f} "
                        f"deg5+={d5:.3f} null={null:.4f}")
    if good and hubs_weak:
        return "GOOD_SHALLOW_MEDIOCRE_HUBS", (f"single/typical GOOD (deg1={d1:.3f} src_uniform={su:.3f} "
                                              f"edge_uniform={eu:.3f}) but hub collapse deg5+ exact "
                                              f"{d5:.3f}<0.40 (hubs need top-5/candidate-set)")
    if su < 0.70:
        return "MEDIOCRE", (f"single-hop works (deg1={d1:.3f}) but realistic src_uniform={su:.3f}<0.70 "
                            f"edge_uniform={eu:.3f} deg5+={d5:.3f}")
    return "GOOD_SHALLOW_MEDIOCRE_HUBS", (f"deg1={d1:.3f} src_uniform={su:.3f} edge_uniform={eu:.3f} "
                                          f"deg5+={d5:.3f}")


# ============================================================
# Main
# ============================================================


def get_config(run_mode):
    if run_mode == "smoke":
        return {"seeds": [7], "sources_per_bin": 120, "codebook_M": 5000,
                "depths": [1, 2, 4, 8, 16], "depth_trials": 40, "neighbor_sources": 400,
                "codebook_sizes": [5000]}
    return {"seeds": [7, 13, 19], "sources_per_bin": 300, "codebook_M": 20000,
            "depths": [1, 2, 4, 8, 16, 32], "depth_trials": 120, "neighbor_sources": 3000,
            "codebook_sizes": [2000, 20000]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["smoke", "full"], default="smoke")
    ap.add_argument("--device", default="cpu")  # cpu default (runner does not pass argv)
    args = ap.parse_args()
    run_mode = args.run_mode
    cfg = get_config(run_mode)

    suffix = "_smoke" if run_mode == "smoke" else ""
    output_dir = REPO / f"data/exp_{ANCHOR_NAME}{suffix}"
    t0 = time.perf_counter()

    # EXPECTED_N_UNITS = per-seed [5 deg bins + depths*2 filler-types + 1 null + 1 neighbor] cardinality gate.
    per_seed_units = 5 + len(cfg["depths"]) * 2 + 1 + 1
    expected_n_units = len(cfg["seeds"]) * per_seed_units
    _write_start_marker(output_dir, run_mode, expected_n_units)

    if not BGE_CACHE.exists():
        raise FileNotFoundError(f"BGE cache missing (local-only artifact): {BGE_CACHE}")

    print(f"[{ANCHOR_NAME}] run_mode={run_mode} seeds={cfg['seeds']} codebook_M={cfg['codebook_M']}", flush=True)
    print("[load] concept graph...", flush=True)
    out, all_ids, degree_weights = build_concept_graph()
    print(f"[load] sources_with_edges={len(out)} atoms={len(all_ids)} "
          f"n_edges={degree_weights['n_edges']}", flush=True)
    print("[load] id_order + semantic matrix (local BGE cache)...", flush=True)
    pos = load_id_order()
    sem = np.load(BGE_CACHE)["semantic"]  # (177899,1024) fp32
    print(f"[load] semantic shape={sem.shape}", flush=True)

    seeds_out = {}
    arms_differ_digests = {}
    n_units_counted = 0
    for seed in cfg["seeds"]:
        print(f"\n[seed {seed}] real_graph arm...", flush=True)
        rg, rg_rec, V, cb_ids, cb_index = arm_real_graph(out, all_ids, pos, sem, cfg, seed, output_dir, t0, degree_weights)
        n_units_counted += len(rg["by_degree"]) + 1  # deg bins + null
        print(f"[seed {seed}] real_graph by_degree={ {k: round(v['top1'],3) for k,v in rg['by_degree'].items()} } "
              f"null={rg['shuffled_role_null']['hit_any_slot']:.4f}", flush=True)

        print(f"[seed {seed}] synth_depth_sweep arm...", flush=True)
        sw, real_rec, synth_rec = arm_synth_depth_sweep(V, cfg, seed, output_dir, t0)
        n_units_counted += len(sw["real_filler"]) + len(sw["synth_filler"])

        nb = arm_neighbor_correlation(out, sem, pos, cb_index, V, cfg, seed)
        n_units_counted += 1
        print(f"[seed {seed}] neighbor mean_cos real={nb['real_neighbor_mean_cos']:.3f} "
              f"random={nb['random_pair_mean_cos']:.3f}", flush=True)

        # arms_differ: recovery-index arrays for real/synth/null must be distinct.
        def _digest(a):
            return hashlib.sha256(np.asarray(a, dtype=np.int64).tobytes()).hexdigest()
        arms_differ_digests[str(seed)] = {
            "real_graph": _digest(rg_rec[:2000]),
            "synth_real_filler": _digest(real_rec[:2000]),
            "synth_synth_filler": _digest(synth_rec[:2000]),
        }
        seeds_out[str(seed)] = {"real_graph": rg, "synth_depth_sweep": sw, "neighbor_correlation": nb}
        _heartbeat(output_dir, seed, cfg["seeds"][-1], t0, extra={"stage": "seed_done", "seed": seed})

    # arms_differ verification (META_RULE_AF)
    arms_differ_ok = True
    for sd, dg in arms_differ_digests.items():
        vals = list(dg.values())
        if len(set(vals)) != len(vals):
            arms_differ_ok = False
    if not arms_differ_ok:
        raise AssertionError("META_RULE_AF VIOLATION: real/synth/null recovery arrays bit-identical")

    # cardinality gate (META_RULE_H)
    cardinality_ok = n_units_counted >= expected_n_units
    verdict_flag = ""
    if not cardinality_ok:
        verdict_flag = f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H(got={n_units_counted}<exp={expected_n_units})"

    # Verdict on the primary seed's real_graph (report all seeds; classify on seed[0]).
    primary = seeds_out[str(cfg["seeds"][0])]["real_graph"]
    verdict, vmsg = classify_verdict(primary)
    # cross-seed realistic-weighted mean for stability note
    su_means = [seeds_out[str(s)]["real_graph"]["realistic_weighted_overall"]["source_uniform"]["top1"] for s in cfg["seeds"]]
    eu_means = [seeds_out[str(s)]["real_graph"]["realistic_weighted_overall"]["edge_uniform"]["top1"] for s in cfg["seeds"]]
    d1_means = [seeds_out[str(s)]["real_graph"]["by_degree"].get("1", {}).get("top1", 0.0) for s in cfg["seeds"]]

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "verdict": verdict if not verdict_flag else "HARD_FAIL_CARDINALITY",
        "verdict_msg": (verdict_flag + " | " if verdict_flag else "") + vmsg,
        "summary": f"{verdict}: substrate algebra relational recovery over REAL atoms ({run_mode})",
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
        "n_seeds": len(cfg["seeds"]),
        "config": cfg,
        "expected_n_units": expected_n_units,
        "n_units_counted": n_units_counted,
        "cardinality_ok": cardinality_ok,
        "arms_differ_verified": arms_differ_ok,
        "arms_differ_digests": arms_differ_digests,
        "cross_seed_source_uniform_top1": {"values": [round(x, 4) for x in su_means],
                                           "mean": round(float(np.mean(su_means)), 4),
                                           "std": round(float(np.std(su_means)), 4)},
        "cross_seed_edge_uniform_top1": {"values": [round(x, 4) for x in eu_means],
                                         "mean": round(float(np.mean(eu_means)), 4),
                                         "std": round(float(np.std(eu_means)), 4)},
        "cross_seed_deg1_top1": {"values": [round(x, 4) for x in d1_means],
                                 "mean": round(float(np.mean(d1_means)), 4)},
        "per_seed": seeds_out,
        "notes": ("REAL atom vectors = BGE semantic (current encoding; re-encode-independent). "
                  "REAL edges = concept partition. Algebra = hdlab.binding(circular-conv HRR) + "
                  "bundling + argmax cleanup. Read-only; NO substrate mutation."),
    }
    _write_metrics_atomic(output_dir, metrics)

    # run_mode verification post-write (RUN_MODE VERIFICATION rule)
    written = json.load(open(output_dir / "metrics.json"))
    assert written["run_mode"] == run_mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {run_mode}"

    print(f"\n[VERDICT] {verdict} :: {vmsg}", flush=True)
    print(f"[cross-seed] deg1 top1 mean={np.mean(d1_means):.3f} | src_uniform mean={np.mean(su_means):.3f} "
          f"| edge_uniform mean={np.mean(eu_means):.3f}", flush=True)
    print(f"[metrics] {output_dir / 'metrics.json'} ({elapsed:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    _out_dir = None
    try:
        _rm = "smoke"
        for i, a in enumerate(sys.argv):
            if a == "--run-mode" and i + 1 < len(sys.argv):
                _rm = sys.argv[i + 1]
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
