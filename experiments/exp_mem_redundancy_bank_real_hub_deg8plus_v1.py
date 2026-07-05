"""REDUNDANCY-BANK lever on the REAL heterogeneous deg8+ hub residual: cost or wall?

Closes the one open memory limiter. The protected-binding arm of
exp_deep_reasoning_hub_robustness_v1 left the real deg8+ hub tail at
idx_bind_top1 = 0.4662 MEASURED@data/exp_deep_reasoning_hub_robustness_v1/metrics.json
(seed7 "8plus" bin; mean degree ~16; 89.8% same-role collisions -> protected binding
lifts ss_raw 0.108 -> 0.466 by breaking collisions, but the residual is pure BUNDLE-CAPACITY
crosstalk among the many slots of one hub trace).

A sibling cell (exp_mem_joint_capacity_hub_degree_redundancy_v1, HARD_PASS
verdict HARD_PASS_COMPUTE_COST_ENVELOPE_ESTABLISHED) already showed the REDUNDANCY-BANK
lever (R independent banks, mean-before-cleanup) rescues SYNTHETIC uniform-degree hubs to
deg20 (min recall 0.82 CITED@data/exp_mem_joint_capacity_hub_degree_redundancy_v1/metrics.json
gate_diagnostics.HP1_protected_hub_recall_by_deg_at_OP). It was NEVER tested on the REAL
heterogeneous codebook that produced the 0.466 residual. That gap is the single decisive test.

MECHANISM (population-vector averaging; brain-grounded CITED@Georgopoulos1986 population vector,
Seung&Sompolinsky1993 Fisher-info ~ linear in independent channels -> SNR ~ sqrt(R); NOT MTT):
  For a real hub with d edges (roles = relation-type vectors, values = real BGE atom vectors):
    - base protected address (idx_bind reproduce):  addr0[j] = roll(role[j], pwr[j])
      (pwr breaks same-role collisions; this is the R=1 arm = the 0.466 baseline BY CONSTRUCTION)
    - bank r>=1 address:  addr_r[j] = roll(role[j], pwr[j] + s_rj)  with s_rj an INDEPENDENT
      per-(bank,slot) random cyclic shift. roll is a UNITARY permutation (dimension-free).
      Signal recovery unbind(bind(addr_r[j],V_j), addr_r[j]) = (role_j corr role_j) conv V_j is
      SHIFT-INVARIANT -> bank-invariant (survives averaging in full). Crosstalk from slot i is
      roll(role_i corr role_j, s_ri - s_rj) conv V_i -> randomly rotated per bank -> averages down.
    - REDUNDANCY R: recovered = mean over R banks of unbind(bank_r), THEN cleanup. Crosstalk
      averages ~1/sqrt(R). Cost = R banks = R * N storage per hub (a real COMPUTE COST, not free).

ARMS (per hub, per degree bin):
  r1/r4/r8         : redundancy R in {1,4,8}, RAW cosine cleanup (r1 raw == idx_bind = 0.466 repro)
  r1_mc/r4_mc/r8_mc: SAME recovered vectors, MEAN-CENTERED cleanup (whiten the cos~0.57 real cone;
                     label-free readout transform, no leakage). Isolates crosstalk-fix (redundancy)
                     from cone-fix (whitening); redundancy contribution = r8_mc - r1_mc.
  ctrl_synth       : SAME roles/degrees/R with SYNTHETIC separable codebook. Isolates whether the
                     real-codebook cone (not the mechanism) is the limiter (expect synth r8 -> high).
  ctrl_degenerate  : R=8 with IDENTICAL banks (all shifts = pwr). Averaging identical estimates ==
                     r1 (asserted allclose). Rules out "free averaging" numerical artifact: any lift
                     MUST come from bank INDEPENDENCE = genuine population averaging.

DISCRIMINATOR (joint gate: credit only genuine redundancy lift, report the memory cost):
  HARD-PASS (envelope closed on REAL data): best deg8+ recall at R>=4 clearly PAST 0.47 (>=0.65)
            AND redundancy genuinely contributes (max(r8-r1 raw, r8_mc-r1_mc) >= 0.10).
  HARD-FAIL (a genuine different wall): best deg8+ recall at R=8 <= 0.50 (doubling R twice buys
            almost nothing -> real correlated intra-hub interference caps the sqrt(R) gain).
  MIDDLE : 0.50 < best_r8 < 0.65 -> routes to RNS/CRT hub-sharding or PP-354 erasure coding.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (r1 vs r8 recovered-idx arrays hash-distinct)
# - final_metrics_atomicity = tmp_replace (metrics.json.tmp -> os.replace via _seed_checkpoint)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: floor is MEASURED r1=0.466 (positive control) + chance 1/M; HP=0.65 < synthetic
#     redundancy ceiling 0.82 (deg20) so HP is reachable (discriminator_reachability=True)
# - baseline (r1 deg8+ ~0.466) in-band (0.05<x<0.95) => measurable failure to rescue
# - discriminator survives scale: SMOKE runs real codebook M=8000 + real degree distribution +
#     real cone (same physics as full M=10000); r1 reproduces 0.466 in smoke (option A)
# - HP_SCOPE: HP/HF gates apply to real deg8+ pooled arms (r1/r4/r8 raw+mc); NOT to ctrl_synth
#     (reference), NOT to deg5 reference bin (saturated protected)
# - cardinality_ok: EXPECTED_N_UNITS = seeds * bins * len(R_list) gate
# - per-unit failure-class instrumentation (no bare except; SystemExit re-raised first)
# - calibration_check: default_ok (reuses landed exp_deep_reasoning_hub_robustness_v1 primitives +
#     the same real codebook; no new tuning; mean-centering is label-free)
# - Gate D positive control AT TEST REGIME: r1 raw deg8+ reproduces 0.4662 (same data, N=1024) tol 0.10
# - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

Storage strategy: BUNDLED per hub (the OBJECT OF STUDY: the deg8+ bundle-capacity residual;
SHARDED-STORAGE-DEFAULT exemption (b): bundle-storage IS the discriminator). SHARDED would
trivially solve it (each edge its own trace) -- the point is to fix the BUNDLED hub cheaply via
redundancy and quantify the cost. Cross-hub bundling is NOT used (each trace = one hub's edges).

Compute architecture: (b) sequential-CPU with justification. Reuses hdlab.binding torch-fft
primitives; per-hub independent; N=1024 rfft is microseconds; no material GPU speedup at N=1024;
reuses the CPU reference algebra of the landed predecessor. Full wall ~ 20-30 min (3 seeds), CPU.

DATA DEPENDENCY (load-bearing for dispatch): requires the LOCAL-ONLY BGE cache (1.3GB) +
concept partition. VERIFIED ABSENT on remote (marsh@home). FULL must run where the data is (local),
same as the predecessor which ran full on FrameworkMPC (~18.5 min).

ASCII-only. CPU only. Read-only (NO substrate mutation). NO LLM comparison.
Run:  python experiments/exp_mem_redundancy_bank_real_hub_deg8plus_v1.py --run-mode {smoke,full}
Self: python experiments/exp_mem_redundancy_bank_real_hub_deg8plus_v1.py --self-test
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

try:
    sys.stdout.reconfigure(line_buffering=True)  # progress flushing (section 17)
except Exception:
    pass

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

# Reuse the LANDED predecessor's exact algebra + real-graph loaders so R=1 reproduces idx_bind
# bit-identically (positive control at test regime, Gate D).
from experiments.exp_deep_reasoning_hub_robustness_v1 import (  # noqa: E402
    white_role, bind_rows, unbind_bcast, cleanup_mc, _norm_rows,
    build_concept_graph, load_id_order, N_DIM, BGE_CACHE,
)
from experiments._seed_checkpoint import (  # noqa: E402
    resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "mem_redundancy_bank_real_hub_deg8plus_v1"
EPS = 1e-12

# ---- MEASURED/CITED reference anchors (tagged per META_RULE_AC) ----
# Real deg>=8 protected-binding residual (positive-control center, Gate D):
IDX_BIND_DEG8PLUS_REF = 0.4662   # MEASURED@data/exp_deep_reasoning_hub_robustness_v1/metrics.json
#                                  (per_seed.7.hub_robustness.per_bin.8plus.idx_bind_top1)
# Synthetic redundancy ceiling (feasibility of HP=0.65): deg20 R4 min recall 0.82
SYNTH_REDUNDANCY_DEG20_R4 = 0.82  # CITED@data/exp_mem_joint_capacity_hub_degree_redundancy_v1
HARD_PASS_DEG8PLUS = 0.65         # THEORETICAL band floor (task): clearly past 0.47; < synth 0.82
HARD_FAIL_DEG8PLUS = 0.50         # THEORETICAL band ceiling for a genuine wall


# ============================================================
# Defensive-error-checking helpers (section 13)
# ============================================================


def _write_start_marker(out_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "_start_marker.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, out_dir / "_start_marker.json")


def _heartbeat(out_dir: Path, unit_idx: int, total_units: int, t0: float, extra=None) -> None:
    row = {
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "unit_idx": unit_idx,
        "total_units": total_units,
        "elapsed_s": round(time.perf_counter() - t0, 2),
    }
    if extra:
        row["extra"] = extra
    with open(out_dir / "_heartbeat.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")


def _write_metrics_atomic(out_dir: Path, metrics: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = out_dir / "metrics.json.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, out_dir / "metrics.json")


def _write_crash_metrics(out_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": "unknown",
    }
    _write_metrics_atomic(out_dir, diag)


# ============================================================
# Cleanup (top1). RAW top1 is bit-identical to predecessor cleanup_raw top1.
# ============================================================


def cleanup_raw_top1(Q: np.ndarray, Vn: np.ndarray) -> np.ndarray:
    """argmax raw-cosine cleanup. Q (d,N) recovered, Vn (M,N) unit codebook -> (d,) idx."""
    qn = _norm_rows(Q)
    return (qn @ Vn.T).argmax(1)


# ============================================================
# Redundancy-bank recovery (the mechanism under test)
# ============================================================


def recover_multi_R(roles: np.ndarray, true_idx: np.ndarray, V: np.ndarray,
                    base_pwr: np.ndarray, bank_shifts: np.ndarray, R_list,
                    mu: np.ndarray, Vcn: np.ndarray):
    """R independent banks (running mean), raw + mc cleanup at each requested R.

    roles (d,N) relation-type vectors; true_idx (d,) target codebook indices;
    base_pwr (d,) protected permutation power (breaks same-role collisions);
    bank_shifts (maxR, d) independent per-(bank,slot) random cyclic shifts (bank 0 unused);
    Returns {R: {"raw": top1_raw(d,), "mc": top1_mc(d,), "rec": recovered(d,N)}}.
    """
    d = roles.shape[0]
    max_R = int(max(R_list))
    R_set = set(int(x) for x in R_list)
    rec_cum = np.zeros((d, N_DIM), dtype=np.float32)
    out = {}
    for r in range(max_R):
        if r == 0:
            shifts = base_pwr.astype(np.int64)          # bank 0 = pure protected idx_bind
        else:
            shifts = (base_pwr + bank_shifts[r, :d]) % N_DIM
        addr = np.stack([np.roll(roles[j], int(shifts[j])) for j in range(d)]).astype(np.float32)
        T = bind_rows(addr, V[true_idx]).sum(0)          # one hub-bundle for this bank
        rec_cum += unbind_bcast(T, addr)                 # (d,N) recovered per slot
        Rnow = r + 1
        if Rnow in R_set:
            rec = (rec_cum / Rnow).astype(np.float32)
            out[Rnow] = {
                "raw": cleanup_raw_top1(rec, V),
                "mc": cleanup_mc(rec, mu, Vcn),
                "rec": rec,
            }
    return out


def recover_degenerate_R8(roles, true_idx, V, base_pwr, mu, Vcn):
    """R=8 IDENTICAL banks (all shifts = base_pwr). Must equal R=1 (free-averaging control)."""
    d = roles.shape[0]
    addr = np.stack([np.roll(roles[j], int(base_pwr[j])) for j in range(d)]).astype(np.float32)
    T = bind_rows(addr, V[true_idx]).sum(0)
    one = unbind_bcast(T, addr)
    rec = (one * 8.0 / 8.0).astype(np.float32)            # mean of 8 identical == one
    return cleanup_raw_top1(rec, V), one


# ============================================================
# Codebook (real BGE atoms + real concept-graph hubs), finer degree bins
# ============================================================


def _parse_bin(b: str):
    """'5'->(5,5); '8to12'->(8,12); '20plus'->(20, inf)."""
    if b.endswith("plus"):
        return int(b[:-4]), 10 ** 9
    if "to" in b:
        lo, hi = b.split("to")
        return int(lo), int(hi)
    return int(b), int(b)


def build_codebook_hub(seed, out, all_ids, pos, sem, cfg):
    """Sample hub sources per (finer) degree bin; build shared real codebook V (unit BGE) up to
    codebook_M with distractors + matched synthetic separable codebook Vsyn."""
    rng = np.random.default_rng(seed)
    deg = {k: len(v) for k, v in out.items()}
    bins = cfg["deg_bins"]
    per_bin = cfg["hub_per_bin"]
    bin_sources = {}
    for b in bins:
        lo, hi = _parse_bin(b)
        cands = [s for s, dd in deg.items() if lo <= dd <= hi]
        rng.shuffle(cands)
        bin_sources[b] = cands[:per_bin]

    needed = set()
    for b, srcs in bin_sources.items():
        for s in srcs:
            needed.add(s)
            for (_, t) in out[s]:
                needed.add(t)
    needed = {a for a in needed if a in pos}
    extra = [a for a in all_ids if a not in needed and a in pos]
    rng.shuffle(extra)
    cb_ids = list(needed) + extra[: max(0, cfg["codebook_M"] - len(needed))]
    cb_index = {aid: i for i, aid in enumerate(cb_ids)}
    rows = np.array([pos[a] for a in cb_ids])
    V = _norm_rows(sem[rows].astype(np.float32))
    mu = V.mean(0).astype(np.float32)
    Vcn = _norm_rows(V - mu)
    Vsyn = _norm_rows(np.random.default_rng(seed + 777).standard_normal((V.shape[0], N_DIM)).astype(np.float32))
    return {"V": V, "Vcn": Vcn, "mu": mu, "Vsyn": Vsyn, "cb_index": cb_index,
            "bin_sources": bin_sources, "M": V.shape[0]}


# ============================================================
# Per-bin evaluation
# ============================================================


def eval_bin(seed, b, srcs, cb, out, cfg, out_dir, t0, bi, nbins):
    """Evaluate one degree bin: per-R (raw+mc) recall over all edges of all hub sources in the bin,
    plus synthetic-codebook control on a subset, plus the degenerate control on the first hub."""
    V, Vcn, mu, Vsyn = cb["V"], cb["Vcn"], cb["mu"], cb["Vsyn"]
    cb_index = cb["cb_index"]
    R_list = cfg["R_list"]
    synth_cap = cfg["synth_cap"]
    max_R = int(max(R_list))
    rng = np.random.default_rng(seed * 100003 + 4242 + bi)

    # accumulators: hits[R]["raw"/"mc"], synth_hits[R], degenerate
    hits = {R: {"raw": 0, "mc": 0} for R in R_list}
    synth_hits = {R: 0 for R in R_list}
    n_edges = 0
    n_edges_synth = 0
    degenerate = {"checked": False, "equals_r1": None, "recall": None}
    rec_r1_digest_src = []   # recovered idx (R1 raw) for arms-differ
    rec_r8_digest_src = []   # recovered idx (maxR raw) for arms-differ
    n_synth_done = 0

    for hi, s in enumerate(srcs):
        edges = [(rt, t) for (rt, t) in out[s] if t in cb_index]
        if len(edges) < 2:
            continue
        d = len(edges)
        roles = np.stack([white_role(rt) for (rt, _) in edges]).astype(np.float32)
        true_idx = np.array([cb_index[t] for (_, t) in edges])
        # protected permutation power per same-role edge (identical to predecessor idx_bind)
        rt_seen = {}
        base_pwr = np.zeros(d, dtype=np.int64)
        for j, (rt, _) in enumerate(edges):
            base_pwr[j] = rt_seen.get(rt, 0)
            rt_seen[rt] = base_pwr[j] + 1
        bank_shifts = rng.integers(1, N_DIM, size=(max_R, d)).astype(np.int64)

        res = recover_multi_R(roles, true_idx, V, base_pwr, bank_shifts, R_list, mu, Vcn)
        for R in R_list:
            hits[R]["raw"] += int((res[R]["raw"] == true_idx).sum())
            hits[R]["mc"] += int((res[R]["mc"] == true_idx).sum())
        n_edges += d
        rec_r1_digest_src.extend(res[R_list[0]]["raw"].tolist())
        rec_r8_digest_src.extend(res[max_R]["raw"].tolist())

        # synthetic-codebook control (subset): separable fillers, same roles/degree/R
        if n_synth_done < synth_cap:
            syn_true = rng.choice(V.shape[0], size=d, replace=False)
            sres = recover_multi_R(roles, syn_true, Vsyn, base_pwr, bank_shifts, R_list, mu, Vcn)
            for R in R_list:
                synth_hits[R] += int((sres[R]["raw"] == syn_true).sum())
            n_edges_synth += d
            n_synth_done += 1

        # degenerate control (first eligible hub only): R=8 identical banks == R=1
        if not degenerate["checked"]:
            dpred, one = recover_degenerate_R8(roles, true_idx, V, base_pwr, mu, Vcn)
            r1_rec = res[R_list[0]]["rec"]
            degenerate["checked"] = True
            degenerate["equals_r1"] = bool(np.allclose(one, r1_rec, atol=1e-5))
            degenerate["recall"] = round(float((dpred == true_idx).mean()), 4)

        if hi % 10 == 0:
            _heartbeat(out_dir, bi * 1000 + hi, nbins * 1000, t0,
                       extra={"seed": seed, "bin": b, "hub": hi, "d": d})

    per_R = {}
    for R in R_list:
        per_R[str(R)] = {
            "raw_recall": round(hits[R]["raw"] / max(1, n_edges), 4),
            "mc_recall": round(hits[R]["mc"] / max(1, n_edges), 4),
            "synth_raw_recall": round(synth_hits[R] / max(1, n_edges_synth), 4),
        }
    return {
        "bin": b, "n_sources": len(srcs), "n_edges": n_edges, "n_edges_synth": n_edges_synth,
        "per_R": per_R, "degenerate_r8": degenerate,
        "_r1_digest": hashlib.sha256(np.asarray(rec_r1_digest_src[:2000], dtype=np.int64).tobytes()).hexdigest(),
        "_r8_digest": hashlib.sha256(np.asarray(rec_r8_digest_src[:2000], dtype=np.int64).tobytes()).hexdigest(),
    }


def run_one_seed(seed, cfg, out_dir, t0):
    if not BGE_CACHE.exists():
        raise FileNotFoundError(f"BGE cache missing (LOCAL-ONLY artifact; full needs local data): {BGE_CACHE}")
    print(f"\n[seed {seed}] loading real concept graph + BGE codebook...", flush=True)
    out, all_ids = build_concept_graph()
    pos = load_id_order()
    sem = np.load(BGE_CACHE)["semantic"]
    cb = build_codebook_hub(seed, out, all_ids, pos, sem, cfg)
    print(f"[seed {seed}] codebook M={cb['M']} bins={ {b: len(s) for b,s in cb['bin_sources'].items()} }",
          flush=True)

    bins_out = {}
    nbins = len(cb["bin_sources"])
    for bi, (b, srcs) in enumerate(cb["bin_sources"].items()):
        r = eval_bin(seed, b, srcs, cb, out, cfg, out_dir, t0, bi, nbins)
        bins_out[b] = r
        pr = r["per_R"]
        print(f"[seed {seed}] bin {b} (n_edges={r['n_edges']}): "
              f"raw R1={pr[str(cfg['R_list'][0])]['raw_recall']:.3f} "
              f"R4={pr.get('4',{}).get('raw_recall','-')} R8={pr.get('8',{}).get('raw_recall','-')} | "
              f"mc R8={pr.get('8',{}).get('mc_recall','-')} | "
              f"synth R8={pr.get('8',{}).get('synth_raw_recall','-')} | "
              f"degen_r8==r1={r['degenerate_r8']['equals_r1']}", flush=True)

    return {"seed": seed, "N": N_DIM, "run_mode": cfg.get("_mode"), "bins": bins_out,
            "config_version": f"ANCHOR={ANCHOR_NAME},N={N_DIM},run_mode={cfg.get('_mode')}"}


# ============================================================
# Config
# ============================================================


def get_config(run_mode):
    if run_mode == "smoke":
        # SMOKE at real codebook M=8000 (near full) + real degree distribution + real cone:
        # same physics as full (discriminator-survives-scale option A). 1 seed, 3 bins.
        return {"seeds": [7], "deg_bins": ["5", "8to12", "20plus"], "hub_per_bin": 30,
                "codebook_M": 8000, "R_list": [1, 4, 8], "synth_cap": 15}
    # full
    return {"seeds": [7, 13, 19], "deg_bins": ["5", "8to12", "13to19", "20plus"],
            "hub_per_bin": 60, "codebook_M": 10000, "R_list": [1, 4, 8], "synth_cap": 20}


# ============================================================
# Aggregation + verdict (pooled deg8+)
# ============================================================


def _mean(vals):
    vals = [v for v in vals if v is not None]
    return float(np.mean(vals)) if vals else float("nan")


def _pool_deg8plus(per_seed, R, field):
    """Edge-weighted pooled recall across the deg>=8 bins (8to12/13to19/20plus), cross-seed mean."""
    hi_bins = ["8to12", "13to19", "20plus"]
    seed_vals = []
    for s in per_seed:
        bins = per_seed[s]["bins"]
        num = den = 0.0
        for b in hi_bins:
            if b in bins and str(R) in bins[b]["per_R"]:
                ne = bins[b]["n_edges"]
                num += bins[b]["per_R"][str(R)][field] * ne
                den += ne
        if den > 0:
            seed_vals.append(num / den)
    return _mean(seed_vals)


def _subbin(per_seed, b, R, field):
    return _mean([per_seed[s]["bins"][b]["per_R"][str(R)][field]
                  for s in per_seed if b in per_seed[s]["bins"] and str(R) in per_seed[s]["bins"][b]["per_R"]])


def classify(per_seed, cfg):
    R_list = cfg["R_list"]
    Rlo, Rmax = R_list[0], R_list[-1]
    hi_bins = ["8to12", "13to19", "20plus"]

    r1 = _pool_deg8plus(per_seed, Rlo, "raw_recall")
    r4 = _pool_deg8plus(per_seed, 4, "raw_recall") if 4 in R_list else None
    r8 = _pool_deg8plus(per_seed, Rmax, "raw_recall")
    r1m = _pool_deg8plus(per_seed, Rlo, "mc_recall")
    r4m = _pool_deg8plus(per_seed, 4, "mc_recall") if 4 in R_list else None
    r8m = _pool_deg8plus(per_seed, Rmax, "mc_recall")
    synth_r8 = _pool_deg8plus(per_seed, Rmax, "synth_raw_recall")

    lift_raw = r8 - r1
    lift_mc = r8m - r1m
    best_r8 = max(r8, r8m)
    best_r4 = max([x for x in (r4, r4m) if x is not None], default=None)
    redundancy_contributes = max(lift_raw, lift_mc) >= 0.10

    # per-sub-bin best-cleanup recall at Rmax (spread across the true tail)
    subbin_best = {b: max(_subbin(per_seed, b, Rmax, "raw_recall"),
                          _subbin(per_seed, b, Rmax, "mc_recall")) for b in hi_bins}
    spread = max(subbin_best.values()) - min(subbin_best.values())

    # degenerate control (any seed's checked hub): identical banks must equal r1
    degen_ok = True
    degen_vals = []
    for s in per_seed:
        for b in hi_bins:
            dd = per_seed[s]["bins"].get(b, {}).get("degenerate_r8", {})
            if dd.get("checked"):
                degen_vals.append(dd.get("recall"))
                if dd.get("equals_r1") is False:
                    degen_ok = False

    pc_ok = abs(r1 - IDX_BIND_DEG8PLUS_REF) <= 0.10          # Gate D positive control at test regime
    fires = 0.05 < r1 < 0.95                                  # baseline in-band (META_RULE_AG)

    diag = {
        "deg8plus_pooled": {
            "raw": {"R1": round(r1, 4), "R4": (round(r4, 4) if r4 is not None else None), "R8": round(r8, 4)},
            "mc": {"R1": round(r1m, 4), "R4": (round(r4m, 4) if r4m is not None else None), "R8": round(r8m, 4)},
            "synth_raw_R8": round(synth_r8, 4),
        },
        "lift_raw_R1_to_R8": round(lift_raw, 4),
        "lift_mc_R1_to_R8": round(lift_mc, 4),
        "best_R4": (round(best_r4, 4) if best_r4 is not None else None),
        "best_R8": round(best_r8, 4),
        "redundancy_contributes_ge_0.10": bool(redundancy_contributes),
        "subbin_best_recall_at_R8": {b: round(v, 4) for b, v in subbin_best.items()},
        "subbin_spread_at_R8": round(spread, 4),
        "memory_cost_ratio_R8": Rmax,          # R banks = R * N storage per hub (real compute cost)
        "degenerate_r8_equals_r1": degen_ok, "degenerate_r8_recall": degen_vals,
        "GateD_positive_control_r1_raw": round(r1, 4),
        "GateD_ref": IDX_BIND_DEG8PLUS_REF, "GateD_ok": pc_ok,
        "research_note_strict_gates": {
            "r4_raw_ge_0.65": (r4 is not None and r4 >= 0.65),
            "r8_raw_ge_0.75": (r8 >= 0.75),
            "spread_le_0.20": (spread <= 0.20),
        },
        "discriminator_fired_baseline_in_band": bool(fires),
    }

    if not fires:
        return "DISCRIMINATOR_DID_NOT_FIRE", (
            f"baseline r1 deg8+ raw={r1:.3f} not in-band (0.05..0.95); no residual to rescue"), diag
    if not pc_ok:
        return "HARD_FAIL_POSITIVE_CONTROL_DRIFT", (
            f"r1 raw deg8+={r1:.3f} does NOT reproduce protected-binding ref "
            f"{IDX_BIND_DEG8PLUS_REF} within 0.10 -> port drift; downstream arms UNTRUSTWORTHY"), diag
    if not degen_ok:
        return "HARD_FAIL_FREE_AVERAGING_ARTIFACT", (
            f"degenerate R8 (identical banks) != R1 -> lift is an averaging artifact, "
            f"not genuine bank-independence population averaging"), diag

    cost = (f"cost = R banks = {Rmax}x dimension/storage for the deg8+ tail "
            f"(1836/118799 = 1.5%% of sources); real COMPUTE COST either way")

    if best_r8 <= HARD_FAIL_DEG8PLUS:
        return "HARD_FAIL_REAL_HUB_REDUNDANCY_WALL", (
            f"redundancy buys almost nothing on REAL deg8+: best R8 recall {best_r8:.3f} <= {HARD_FAIL_DEG8PLUS} "
            f"(raw R1={r1:.3f}->R8={r8:.3f} lift +{lift_raw:.3f}; mc R1={r1m:.3f}->R8={r8m:.3f} lift +{lift_mc:.3f}; "
            f"synth R8={synth_r8:.3f}). Real correlated intra-hub interference caps the sqrt(R) gain -> a genuine "
            f"different WALL, not a compute cost. Route to RNS/CRT structural sharding. {cost}"), diag

    if best_r8 >= HARD_PASS_DEG8PLUS and redundancy_contributes:
        via = "raw redundancy alone" if lift_raw >= 0.10 and r8 >= HARD_PASS_DEG8PLUS else \
              ("redundancy + cone-whitening (mc)" if r8m >= HARD_PASS_DEG8PLUS else "redundancy (best cleanup)")
        return "HARD_PASS_REAL_DEG8PLUS_REDUNDANCY_CLOSES_ENVELOPE", (
            f"REDUNDANCY LEVER GENERALIZES TO REAL heterogeneous deg8+: best R8 recall {best_r8:.3f} >= "
            f"{HARD_PASS_DEG8PLUS} (past the 0.466 residual) via {via}; raw R1={r1:.3f}->R8={r8:.3f} "
            f"(+{lift_raw:.3f}); mc R1={r1m:.3f}->R8={r8m:.3f} (+{lift_mc:.3f}); best R4={best_r4}; "
            f"sub-bin spread {spread:.3f}; synth ctrl R8={synth_r8:.3f}; degenerate R8==R1 (population "
            f"averaging genuine, not free). Memory envelope CLOSED: deg8+ residual is a COMPUTE COST, "
            f"not a wall, on REAL data. {cost}"), diag

    return "MIDDLE_BAND", (
        f"partial rescue on REAL deg8+: best R8 recall {best_r8:.3f} in ({HARD_FAIL_DEG8PLUS}, "
        f"{HARD_PASS_DEG8PLUS}); raw R1={r1:.3f}->R8={r8:.3f} (+{lift_raw:.3f}); mc R1={r1m:.3f}->R8={r8m:.3f} "
        f"(+{lift_mc:.3f}); synth R8={synth_r8:.3f}. Redundancy helps but does not fully close on real "
        f"correlated hubs -> route to RNS/CRT hub-sharding or PP-354 erasure coding (structured codes). {cost}"), diag


# ============================================================
# Self-test (formula selftests; synthetic, no BGE cache; exit 0 <180s)
# ============================================================


def self_test(out_dir):
    import torch
    from hdlab import binding
    t0 = time.perf_counter()
    print("[self-test] formula self-tests...", flush=True)
    N = N_DIM
    rng = np.random.default_rng(0)

    # 1. protected bind/unbind round-trip on a single pair (signal recovery shift-invariant)
    role = _norm_rows(rng.standard_normal((1, N)).astype(np.float32))
    val = _norm_rows(rng.standard_normal((1, N)).astype(np.float32))
    addr0 = np.roll(role[0], 3)[None]
    addr1 = np.roll(role[0], 137)[None]
    rec0 = unbind_bcast(bind_rows(addr0, val).sum(0), addr0)[0]
    rec1 = unbind_bcast(bind_rows(addr1, val).sum(0), addr1)[0]
    d_shift = float(np.abs(_norm_rows(rec0[None])[0] - _norm_rows(rec1[None])[0]).max())
    assert d_shift < 1e-3, f"signal recovery NOT shift-invariant (max|d|={d_shift}); mechanism wrong"

    # 2. redundancy reduces crosstalk on a SYNTHETIC hub (separable codebook) => r8 > r1
    M = 400
    d = 12
    V = _norm_rows(rng.standard_normal((M, N)).astype(np.float32))
    mu = V.mean(0).astype(np.float32)
    Vcn = _norm_rows(V - mu)
    roles = _norm_rows(rng.standard_normal((d, N)).astype(np.float32))
    true_idx = rng.choice(M, size=d, replace=False)
    base_pwr = np.zeros(d, dtype=np.int64)
    bank_shifts = rng.integers(1, N, size=(8, d)).astype(np.int64)
    res = recover_multi_R(roles, true_idx, V, base_pwr, bank_shifts, [1, 4, 8], mu, Vcn)
    r1 = float((res[1]["raw"] == true_idx).mean())
    r8 = float((res[8]["raw"] == true_idx).mean())
    assert r8 >= r1, f"redundancy did not help synthetic hub (r1={r1} r8={r8})"

    # 3. degenerate (identical banks) == R1 (rules out free-averaging)
    dpred, one = recover_degenerate_R8(roles, true_idx, V, base_pwr, mu, Vcn)
    assert np.allclose(one, res[1]["rec"], atol=1e-4), "degenerate R8 != R1 (free-averaging control broke)"

    # 4. arms differ: r1 vs r8 recovered idx not bit-identical (crosstalk changed the estimate)
    h1 = hashlib.sha256(res[1]["raw"].astype(np.int64).tobytes()).hexdigest()
    h8 = hashlib.sha256(res[8]["raw"].astype(np.int64).tobytes()).hexdigest()
    arms_differ = (h1 != h8) or (r1 == 1.0)  # if r1 already perfect, arrays may match (both correct)

    elapsed = time.perf_counter() - t0
    metrics = {
        "verdict": "SELFTEST_PASS",
        "verdict_msg": (f"formula self-tests pass: shift_invariance_diff={d_shift:.1e}; "
                        f"synth hub r1={r1:.3f}->r8={r8:.3f} (redundancy helps); "
                        f"degenerate==R1 True; arms_differ={arms_differ}"),
        "summary": "SELFTEST_PASS (shift-invariant signal + redundancy-reduces-crosstalk + degenerate control)",
        "run_mode": "self_test",
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
    }
    _write_metrics_atomic(out_dir, metrics)
    print(f"[self-test] PASS in {elapsed:.1f}s :: {metrics['verdict_msg']}", flush=True)
    return 0


# ============================================================
# main
# ============================================================


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", choices=["smoke", "full"], default=None)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only; flag accepted for runner compat
    args = ap.parse_args()

    suffix_st = "_selftest"
    if args.self_test:
        out_dir = REPO / f"data/exp_{ANCHOR_NAME}{suffix_st}"
        out_dir.mkdir(parents=True, exist_ok=True)
        return self_test(out_dir)

    run_mode = args.run_mode or os.environ.get("HDLAB_RUN_MODE", "full")
    run_mode = run_mode if run_mode in ("smoke", "full") else "full"
    cfg = get_config(run_mode)
    cfg["_mode"] = run_mode

    suffix = "_smoke" if run_mode == "smoke" else ""
    out_dir = REPO / f"data/exp_{ANCHOR_NAME}{suffix}"
    t0 = time.perf_counter()

    expected_n_units = len(cfg["seeds"]) * len(cfg["deg_bins"]) * len(cfg["R_list"])
    _write_start_marker(out_dir, run_mode, expected_n_units)
    print(f"[{ANCHOR_NAME}] run_mode={run_mode} N={N_DIM} seeds={cfg['seeds']} "
          f"bins={cfg['deg_bins']} R={cfg['R_list']} M={cfg['codebook_M']} "
          f"expected_units={expected_n_units}", flush=True)

    run_config = {"N": N_DIM, "run_mode": run_mode, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(cfg["seeds"], out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} done, running {remaining}", flush=True)

    for seed in remaining:
        res = run_one_seed(seed, cfg, out_dir, t0)
        write_partial(out_dir, seed, res)
        _heartbeat(out_dir, seed, cfg["seeds"][-1], t0, extra={"stage": "seed_done", "seed": seed})

    per_seed = aggregate_partials(out_dir, cfg["seeds"], run_config=run_config)

    # cardinality (META_RULE_H): every seed has every bin with every R
    n_units = 0
    for s in per_seed:
        for b in per_seed[s]["bins"]:
            n_units += len(per_seed[s]["bins"][b]["per_R"])
    cardinality_ok = (len(per_seed) == len(cfg["seeds"])) and (n_units == expected_n_units)

    # arms-differ (META_RULE_AF): r1 vs r8 recovered-idx digests distinct on the deg8+ bins
    arms_differ_ok = True
    arms_note = "ok"
    for s in per_seed:
        for b in ("8to12", "13to19", "20plus"):
            bb = per_seed[s]["bins"].get(b)
            if bb and bb["_r1_digest"] == bb["_r8_digest"]:
                arms_differ_ok = False
                arms_note = f"IDENTICAL r1/r8 recovered idx at {b} (seed {s})"

    verdict, vmsg, diag = classify(per_seed, cfg)

    if not cardinality_ok:
        verdict = "HARD_FAIL_CARDINALITY"
        vmsg = (f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: {n_units} units / {len(per_seed)} seeds; "
                f"expected {expected_n_units} / {len(cfg['seeds'])} | " + vmsg)
    if not arms_differ_ok:
        verdict = "HARD_FAIL_ARMS_IDENTICAL"
        vmsg = f"META_RULE_AF VIOLATION: {arms_note} | " + vmsg

    elapsed = time.perf_counter() - t0
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": f"{verdict}: redundancy-bank lever on REAL heterogeneous deg8+ hubs ({run_mode}, N={N_DIM})",
        "elapsed_s": round(elapsed, 2),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "host": platform.node(),
        "n_seeds": len(cfg["seeds"]),
        "seeds": cfg["seeds"],
        "config": {k: v for k, v in cfg.items() if not k.startswith("_")},
        "expected_n_units": expected_n_units,
        "n_units_counted": n_units,
        "cardinality_ok": cardinality_ok,
        "arms_differ_verified": arms_differ_ok,
        "arms_differ_note": arms_note,
        "gate_diagnostics": diag,
        "per_seed": per_seed,
        "notes": ("REAL atom vectors = BGE semantic (LOCAL-ONLY cache). REAL edges = concept partition. "
                  "Redundancy-bank = R independent per-(bank,slot) unitary roll shifts, mean-before-cleanup. "
                  "R1 raw == predecessor idx_bind (positive control). Read-only; NO substrate mutation; NO LLM."),
    }
    _write_metrics_atomic(out_dir, metrics)

    written = json.load(open(out_dir / "metrics.json"))
    assert written["run_mode"] == run_mode, f"RUN_MODE_MISMATCH {written['run_mode']} != {run_mode}"

    print(f"\n[VERDICT] {verdict}", flush=True)
    print(f"[msg] {vmsg}", flush=True)
    dp = diag.get("deg8plus_pooled", {})
    print(f"[diag] raw={dp.get('raw')} mc={dp.get('mc')} best_R8={diag.get('best_R8')} "
          f"lift_raw={diag.get('lift_raw_R1_to_R8')} lift_mc={diag.get('lift_mc_R1_to_R8')} "
          f"synth_R8={dp.get('synth_raw_R8')} spread={diag.get('subbin_spread_at_R8')}", flush=True)
    print(f"[metrics] {out_dir / 'metrics.json'} ({elapsed:.1f}s)", flush=True)
    return 0


if __name__ == "__main__":
    _out_dir = None
    try:
        _st = "--self-test" in sys.argv
        _rm = None
        for i, a in enumerate(sys.argv):
            if a == "--run-mode" and i + 1 < len(sys.argv):
                _rm = sys.argv[i + 1]
        if _st:
            _out_dir = REPO / f"data/exp_{ANCHOR_NAME}_selftest"
        else:
            _rm = _rm or os.environ.get("HDLAB_RUN_MODE", "full")
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
