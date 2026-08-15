"""AUDITOR RECOMPUTE (not a pre-registered cell; wires nothing; changes no hdlab default).

Adds the ORTHOGRAPHIC/STRING-FORM floor the ledger-validity audit (2026-08-15,
tools/ledger_validity_audit.py) found missing from the leak-proof relational-inference family:
exp_leakproof_relational_inference_heldout_v1 (C6), exp_leakproof_relinfer_context_sweep_v1 (B45),
exp_leakproof_relinfer_twonew_v1 (B82). All three carry a FREQ/ARM floor (POPULARITY, degree-matched
-> ~0.50) and a must-fail control (COLLAPSE_SHUFFLE) but never an orthographic one, which is why the
ledger-validity audit scores them SOFT rather than HARD.

CONSTRUCTION (reused, not invented): the trigram-hash construction is copied verbatim from
experiments/exp_meaning_supply_separation_v1.trigram_matrix (character-trigram cosine profile per
surface string, hashed into a fixed-width bag, zero substrate/meaning signal) -- the same primitive
tools/orthographic_floor_vet_v1.py promoted for the C3 family. Here the "anchors" being profiled are
concept SURFACE STRINGS (nodes.jsonl "surface", e.g. "repair_shop" -> "repair shop") rather than
lexicon words, but the construction (hash trigrams into a fixed-width bag, L2-normalize, cosine) is
identical.

SCORER REUSE (zero reimplementation): each target module's OWN eval_relational_inference() computes
`sc = Zg[sel] @ score_matrix[h]` for any [K,d] score_matrix -- i.e. it is ALREADY a generic
"cosine-style scorer over any embedding," and the ORTHO arm plugs in by substituting the trigram
matrix for the learned/raw embedding matrix. No AUC math, negative-sampling, degree-matching, or
leak-exclusion logic is reimplemented here; this script imports and calls the module's own
_query_positives_negatives and _auc_from_scores, only adding a thin per-query capture (the module's
own eval_relational_inference collapses to a mean; the paired bootstrap below needs the per-query
array) that mirrors the module's loop 1:1.

PAIRING: build_leakproof_split / build_eval_context are DETERMINISTIC (sha256 salts, no seed
argument), so the held-out query set, its positives and its degree-matched negatives are IDENTICAL
across every arm and every seed (EVAL_SEED is fixed and consumed in the same iteration order). This
licenses a per-query PAIRED bootstrap between ORTHO (seed-independent, computed once) and LEARNED
(averaged per query across the module's own seeds).

Run:  .venv/Scripts/python.exe tools/orthographic_floor_relinfer_v1.py --cell C6
      .venv/Scripts/python.exe tools/orthographic_floor_relinfer_v1.py --cell B45
      .venv/Scripts/python.exe tools/orthographic_floor_relinfer_v1.py --cell B82
      .venv/Scripts/python.exe tools/orthographic_floor_relinfer_v1.py --cell ALL
Output: data/exp_orthographic_floor_relinfer_<cell>_v1/metrics.json (atomic os.replace, ts_iso).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import importlib
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

TRIGRAM_DIM = 512  # matches exp_meaning_supply_separation_v1.TRIGRAM_DIM (the C3-family floor width)

MODULES = {
    "C6": "experiments.exp_leakproof_relational_inference_heldout_v1",
    "B45": "experiments.exp_leakproof_relinfer_context_sweep_v1",
    "B82": "experiments.exp_leakproof_relinfer_twonew_v1",
}
LANDED_LEARNED = {  # from data/<dir>/metrics.json, verbatim, for a reproduction sanity check only
    "C6": 0.6534,
    "B45": 0.6614,  # ALL-context arm of the sweep (matches the base cell's config/number)
    "B82": 0.6719,
}


def trigram_surface_matrix(surfaces: List[str], dim: int = TRIGRAM_DIM) -> np.ndarray:
    """Row-L2-normalized character-trigram profile per SURFACE STRING. Copied construction from
    exp_meaning_supply_separation_v1.trigram_matrix; only the input (concept surfaces, may be
    multi-word, e.g. "repair shop") differs from that function's single-word anchors."""
    mat = np.zeros((len(surfaces), dim), dtype=np.float64)
    for i, s in enumerate(surfaces):
        ss = "^" + str(s).lower().replace("_", " ") + "$"
        for k in range(len(ss) - 2):
            j = int.from_bytes(hashlib.sha256(ss[k:k + 3].encode("utf-8")).digest()[:4], "big") % dim
            mat[i, j] += 1.0
        nrm = float(np.linalg.norm(mat[i]))
        if nrm >= 1e-9:
            mat[i] /= nrm
    return mat.astype(np.float32)


def per_query_auc(score_matrix: np.ndarray, split: dict, ev_ctx: dict, mod) -> Dict[int, float]:
    """Thin per-query capture mirroring module.eval_relational_inference's cosine-arm branch 1:1
    (same gallery construction, same _query_positives_negatives, same _auc_from_scores) but
    returning the per-query AUC dict instead of collapsing to a mean -- needed for a paired
    bootstrap. Zero reimplementation of the scorer itself."""
    gallery_idx = ev_ctx["train_idx"] if "train_idx" in ev_ctx else ev_ctx["held_idx"]
    Zg = score_matrix[gallery_idx]
    rng = np.random.default_rng(mod.EVAL_SEED)
    out: Dict[int, float] = {}
    for h in split["held_idx"].tolist():
        qpn = mod._query_positives_negatives(h, split, ev_ctx, rng)
        if qpn is None:
            continue
        pos_arr, neg_arr = qpn[0], qpn[1]
        sel = np.concatenate([pos_arr, neg_arr])
        sc = Zg[sel] @ score_matrix[h]
        pm = np.zeros(sel.shape[0], dtype=bool)
        pm[:pos_arr.shape[0]] = True
        a = mod._auc_from_scores(sc, pm)
        if a is not None:
            out[h] = a
    return out


def paired_bootstrap_delta(a: Dict[int, float], b: Dict[int, float], n_boot: int, seed: int) -> dict:
    """Resample over the SHARED query-id set (a - b), percentile CI."""
    common = sorted(set(a.keys()) & set(b.keys()))
    va = np.array([a[h] for h in common], dtype=np.float64)
    vb = np.array([b[h] for h in common], dtype=np.float64)
    n = va.shape[0]
    rng = np.random.default_rng(seed)
    deltas = np.empty(n_boot, dtype=np.float64)
    for r in range(n_boot):
        idx = rng.integers(0, n, size=n)
        deltas[r] = va[idx].mean() - vb[idx].mean()
    point = float(va.mean() - vb.mean())
    lo, hi = np.percentile(deltas, [2.5, 97.5])
    return {
        "n_query": n, "a_mean": float(va.mean()), "b_mean": float(vb.mean()),
        "delta_a_minus_b": point, "ci_lo": float(lo), "ci_hi": float(hi),
        "sd": float(deltas.std()), "ci_excludes_zero": bool(lo > 0.0 or hi < 0.0),
    }


def run_one(cell: str, out_dir: str) -> dict:
    t0 = time.time()
    mod = importlib.import_module(MODULES[cell])
    cfg = mod.FULL_CFG
    print("[%s] loading grounded subgraph (min_deg=%d cap=%d top_rel=%d)..."
          % (cell, cfg["min_deg"], cfg["cap_nodes"], cfg["top_rel"]), flush=True)
    data = mod.load_grounded_subgraph(cfg)

    if cell == "B45":
        split = mod.build_leakproof_split(data, cfg, max_context=mod.ALL_CONTEXT)
        base_feats, landmarks, target_geo, ev_ctx = mod.build_level_context(split, cfg)
    else:
        split = mod.build_leakproof_split(data, cfg)
        own = split["own_feat"]
        ctx = mod._pooled_ctx_block(split, own, mod.GROUND_DIM)
        base_feats = dict(own=own.astype(np.float32), ctx=ctx.astype(np.float32))
        landmarks = mod.select_landmarks(split, cfg)
        A = mod.build_train_adjacency(split)
        own_norm = mod._l2_np(own.astype(np.float64)).astype(np.float32)
        target_geo = mod.compute_target_geometry(own_norm, A, landmarks)
        ev_ctx = mod.build_eval_context(split, cfg["n_deg_bins"])

    print("[%s] split: %s" % (cell, split["split_meta"]), flush=True)

    surfaces = data["surfaces"]
    trigram_mat = trigram_surface_matrix(surfaces)
    ortho_pq = per_query_auc(trigram_mat, split, ev_ctx, mod)
    ortho_auc = float(np.mean(list(ortho_pq.values()))) if ortho_pq else float("nan")
    print("[%s] ORTHO_ARM (trigram-surface-only) rel_infer_auc=%.4f n_query=%d"
          % (cell, ortho_auc, len(ortho_pq)), flush=True)

    learned_pq_by_seed = {}
    for seed in cfg["seeds"]:
        enc = mod.train_fusion(base_feats, target_geo, landmarks, split, cfg, seed,
                                use_ctx=True, w_rel=cfg["w_rel"], w_ema=cfg["w_ema"], do_train=True)
        codes = mod.encode_all(enc, base_feats)
        pq = per_query_auc(codes, split, ev_ctx, mod)
        learned_pq_by_seed[seed] = pq
        print("[%s] seed=%d LEARNED rel_infer_auc=%.4f n_query=%d (elapsed=%.1fs)"
              % (cell, seed, float(np.mean(list(pq.values()))) if pq else float("nan"),
                 len(pq), time.time() - t0), flush=True)

    common_q = sorted(set.intersection(*[set(pq.keys()) for pq in learned_pq_by_seed.values()]))
    learned_seedavg = {h: float(np.mean([learned_pq_by_seed[s][h] for s in cfg["seeds"]]))
                        for h in common_q}
    learned_auc_recomputed = float(np.mean(list(learned_seedavg.values()))) if learned_seedavg else float("nan")

    bs = paired_bootstrap_delta(learned_seedavg, ortho_pq, 5000, 20260815)

    landed = LANDED_LEARNED[cell]
    reproduction_ok = bool(abs(learned_auc_recomputed - landed) < 0.02)

    rep = {
        "anchor_name": "orthographic_floor_relinfer_%s_v1" % cell,
        "what": "AUDITOR RECOMPUTE: trigram-surface-only ORTHO_ARM plugged into the module's own "
                "eval_relational_inference, paired-bootstrapped against re-trained LEARNED",
        "target_cell": MODULES[cell], "target_cell_short": cell,
        "compares_against": {"landed_metrics": "data/%s/metrics.json"
                              % MODULES[cell].split(".")[-1],
                              "landed_learned_rel_infer_auc": landed},
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "reproduction_check": {
            "recomputed_learned_auc_seed_mean": learned_auc_recomputed,
            "landed_learned_auc": landed,
            "abs_diff": abs(learned_auc_recomputed - landed),
            "within_0.02_tolerance": reproduction_ok,
        },
        "ortho_arm": {"rel_infer_auc": ortho_auc, "n_query": len(ortho_pq),
                      "trigram_dim": TRIGRAM_DIM, "construction": "surface-string char-trigram "
                      "cosine, ZERO substrate/embedding signal, same eval_relational_inference "
                      "scorer as LEARNED/RAW/POPULARITY/COLLAPSE"},
        "learned_arm_recomputed": {"rel_infer_auc_seed_mean": learned_auc_recomputed,
                                   "n_query_common_across_seeds": len(common_q), "seeds": cfg["seeds"]},
        "paired_bootstrap_learned_minus_ortho": bs,
        "clears_ortho_floor_ci_separated": bool(bs["ci_excludes_zero"] and bs["delta_a_minus_b"] > 0.0),
        "split_meta": split["split_meta"], "data_meta": data["meta"],
        "elapsed_s": round(time.time() - t0, 2),
    }
    os.makedirs(out_dir, exist_ok=True)
    p = os.path.join(out_dir, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print("[%s] WROTE %s" % (cell, p), flush=True)
    print("[%s] LEARNED=%.4f ORTHO=%.4f delta=%.4f CI=[%.4f,%.4f] clears=%s"
          % (cell, learned_auc_recomputed, ortho_auc, bs["delta_a_minus_b"], bs["ci_lo"], bs["ci_hi"],
             rep["clears_ortho_floor_ci_separated"]), flush=True)
    return rep


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cell", choices=["C6", "B45", "B82", "ALL"], default="ALL")
    args = ap.parse_args()
    cells = list(MODULES.keys()) if args.cell == "ALL" else [args.cell]
    results = {}
    for cell in cells:
        out_dir = os.path.join(_REPO, "data", "exp_orthographic_floor_relinfer_%s_v1" % cell)
        try:
            results[cell] = run_one(cell, out_dir)
        except Exception as exc:
            crash = {"anchor_name": "orthographic_floor_relinfer_%s_v1" % cell,
                      "error": "%s: %s" % (type(exc).__name__, exc),
                      "traceback": traceback.format_exc(),
                      "ts_iso": datetime.now(timezone.utc).isoformat()}
            os.makedirs(out_dir, exist_ok=True)
            p = os.path.join(out_dir, "_crash_diagnostic.json")
            with open(p + ".tmp", "w", encoding="utf-8") as fh:
                json.dump(crash, fh, indent=2)
            os.replace(p + ".tmp", p)
            print("[%s] CRASHED: %s" % (cell, exc), flush=True)
            raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
