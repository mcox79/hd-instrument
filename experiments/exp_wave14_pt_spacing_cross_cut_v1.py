"""PT C3: Spacing-concentration x Depth 2x2 cross-cut.

Tests whether cascade replay improvement comes from DEPTH (number of timescale
levels) or from SPACING PROFILE (how samples are distributed across levels).
PT literature (Katzgraber 2006): geometric spacing fails near phase transitions;
densified spacing at the critical zone improves performance.

2x2 design:
  depth in {2, 4}  x  spacing in {geometric, densified}

Spacing modes:
  geometric: uniform chunk_fraction across all pool levels (existing behavior)
  densified: middle pool level(s) get 2x thinning-fraction (more samples retained);
             outer levels get 0.5x (more aggressively thinned). Concentrates
             replay at medium timescale -- the substrate's analog of densifying
             replicas near the phase-transition temperature.

Also instruments adjacent-buffer KL divergence (partial C4 diagnostic).

Per [[feedback-no-experiment-design-in-prompts]]: all parameters exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS / HARD-FAIL bands pre-registered.
Per [[feedback-envelope-expansion-fail-bands]]: bands committed before ship.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.
Per [[feedback-strategy-spec-formula-selftests]]: self-test cells before smoke.
Per [[feedback-composition-classification]]: SCORE-level composition.

Pre-reg: prereqs/2026-05-24_wave14_pt_spacing_cross_cut_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, importlib.util, json, math, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from verification import oracle  # noqa: E402

# Load M1 hierreplay for cascade infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)

base = m1.base
v1 = m1.v1
pa = m1.pa

# ---- design parameters (exp_dev autonomy) ----
N_FULL = 2048
N_SMOKE = 512
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 150_000
BYTES_SMOKE = 4_000
SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

DEPTHS_TO_TEST = [2, 4]
SPACINGS_TO_TEST = ["geometric", "densified"]

# Geometric baseline chunk fraction
BASE_CHUNK_FRACTION = 0.5
# Densified: middle levels get 2x, outer levels get 0.5x
DENSIFIED_MID_FACTOR = 2.0
DENSIFIED_OUTER_FACTOR = 0.5

# Pre-registered verdict bands
EFFECT_THRESHOLD = 0.05  # minimum effect size to attribute to a lever
NULL_THRESHOLD = 0.03    # max effect for H_null verdict


def get_output_dir(name=None):
    n = name or os.environ.get("HDLAB_EXP_NAME", "wave14_pt_spacing_cross_cut_v1")
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def get_chunk_fractions(depth, spacing):
    """Return list of per-level chunk fractions for a given depth and spacing mode.
    Level 0 = most recent (smallest timescale); level depth-1 = oldest (largest).
    """
    if spacing == "geometric":
        return [BASE_CHUNK_FRACTION] * depth
    elif spacing == "densified":
        # Middle level(s) densified; outer levels thinned
        fracs = []
        mid = (depth - 1) / 2.0
        for i in range(depth):
            dist = abs(i - mid) / max(mid, 1e-6)
            if dist <= 0.5:  # within 50% of center
                f = min(BASE_CHUNK_FRACTION * DENSIFIED_MID_FACTOR, 1.0)
            else:
                f = max(BASE_CHUNK_FRACTION * DENSIFIED_OUTER_FACTOR, 0.05)
            fracs.append(f)
        return fracs
    else:
        raise ValueError(f"unknown spacing: {spacing}")


def thin_pool_with_fraction(pool_v, pool_l, pool_u, chunk_fraction, device):
    """Thin pool to chunk_fraction of entries (wraps m1.thin_pool_to_chunks behavior)."""
    return m1.thin_pool_to_chunks(pool_v, pool_l, pool_u,
                                   chunk_fraction=chunk_fraction, device=device)


def buffer_kl_divergence(pool_a_v, pool_a_u, pool_b_v, pool_b_u, n_samples=200):
    """Approximate KL divergence between two pool distributions via cosine-similarity proxy.
    KL(A||B) approximated by mean pairwise cosine distance.
    Returns float or None if insufficient samples.
    """
    if pool_a_u < 5 or pool_b_u < 5:
        return None
    n_a = min(n_samples, pool_a_u)
    n_b = min(n_samples, pool_b_u)
    A = pool_a_v[:n_a].float()
    B = pool_b_v[:n_b].float()
    A_norm = A / (A.norm(dim=1, keepdim=True).clamp(min=1e-9))
    B_norm = B / (B.norm(dim=1, keepdim=True).clamp(min=1e-9))
    # Mean cosine distance between A samples and B samples (cross-matrix mean)
    cos_sim = (A_norm @ B_norm.T)  # n_a x n_b
    mean_cos = float(cos_sim.mean().item())
    cos_dist = 1.0 - mean_cos  # 0 = identical distributions, 2 = opposite
    return cos_dist


def run_one_cell(depth, spacing, seed, config, device):
    """Run a depth-stage chain with given spacing profile. Returns retention_A."""
    N = config["N"]
    batch_size = config["batch_size"]
    n_epochs = config["epochs"]
    phase_a_epochs = config["phase_a_epochs"]
    n_bytes = config["bytes_per_corpus"]
    smoke = (config["mode"] == "smoke")

    chunk_fracs = get_chunk_fractions(depth, spacing)

    # Build corpora
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a_full = pa.load_corpus_a()
    corpus_a = corpus_a_full[:n_bytes] if n_bytes < len(corpus_a_full) else corpus_a_full
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d_full = v1.load_corpus_D(smoke=smoke)
    corpus_d = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full
    corpus_e = pa.shuffle_bytes(corpus_b, seed=seed + 5)

    all_corpora = [corpus_a, corpus_b, corpus_c, corpus_d, corpus_e][:depth]

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    train_sets, test_a_idx_ref, test_a_tgt_ref = [], None, None
    for i, corp in enumerate(all_corpora):
        tr, te = split80(corp)
        tr_idx, tr_tgt = base.bytes_to_idx_tensors(tr, device)
        te_idx, te_tgt = base.bytes_to_idx_tensors(te, device)
        train_sets.append((tr_idx, tr_tgt))
        if i == 0:
            test_a_idx_ref = te_idx
            test_a_tgt_ref = te_tgt

    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    thin_pools = []
    bpc_A_baseline = None
    pool_final_v = pool_final_l = None
    pool_final_u = 0
    adj_kl_values = []

    for stage_idx in range(depth):
        tr_idx, tr_tgt = train_sets[stage_idx]
        n_ep = phase_a_epochs if stage_idx == 0 else n_epochs

        # Build combined replay from all prior thinned pools
        if thin_pools:
            all_v = torch.cat([p[0][:p[2]] for p in thin_pools], dim=0)
            all_l = torch.cat([p[1][:p[2]] for p in thin_pools], dim=0)
            all_u = all_v.shape[0]
        else:
            all_v = all_l = None
            all_u = 0

        W_new, pool_v, pool_l, pool_u = base.train_w_with_replay(
            W, None, None, 0, byte_atoms, pos_atoms,
            tr_idx, tr_tgt, all_v, all_l, all_u,
            n_ep, batch_size, device)
        W = W_new

        if stage_idx == 0:
            bpc_A_baseline = base.evaluate_bpc(
                W, pool_v, pool_l, pool_u,
                byte_atoms, pos_atoms,
                test_a_idx_ref, test_a_tgt_ref, batch_size, device)

        # Thin with stage-specific fraction (spacing profile)
        frac = chunk_fracs[stage_idx]
        thin_v, thin_l, thin_u = thin_pool_with_fraction(
            pool_v, pool_l, pool_u, frac, device)

        # Adjacent-buffer KL divergence diagnostic (C4 partial)
        if thin_pools:
            prev_v, prev_l, prev_u = thin_pools[-1]
            kl = buffer_kl_divergence(prev_v, prev_u, thin_v, thin_u)
            if kl is not None:
                adj_kl_values.append(kl)

        thin_pools.append((thin_v, thin_l, thin_u))
        pool_final_v = pool_v
        pool_final_l = pool_l
        pool_final_u = pool_u

    bpc_A_after = base.evaluate_bpc(
        W, pool_final_v, pool_final_l, pool_final_u,
        byte_atoms, pos_atoms, test_a_idx_ref, test_a_tgt_ref, batch_size, device)
    ret_A = min(bpc_A_baseline / max(bpc_A_after, 1e-6), 1.0) if bpc_A_baseline else 0.0

    mean_adj_kl = sum(adj_kl_values) / len(adj_kl_values) if adj_kl_values else None
    return ret_A, bpc_A_baseline, bpc_A_after, mean_adj_kl, chunk_fracs


def compute_verdict(summary):
    cells = summary.get("cells", {})
    if not cells:
        return ("SPACING_INCONCLUSIVE", "No cell data.")

    # Extract per-cell mean retA
    means = {}
    for cell_key, cell_data in cells.items():
        per_seed = cell_data.get("per_seed", {})
        if not per_seed:
            continue
        mean_r = sum(v["retA"] for v in per_seed.values()) / len(per_seed)
        means[cell_key] = mean_r

    required_cells = [(str(d), sp) for d in [2, 4] for sp in ["geometric", "densified"]]
    cell_keys = [f"d{d}_{sp}" for d, sp in [(2, "geometric"), (2, "densified"),
                                               (4, "geometric"), (4, "densified")]]
    if not all(k in means for k in cell_keys):
        available = list(means.keys())
        return ("SPACING_INCONCLUSIVE",
                f"Missing cells; have {available}, need {cell_keys}.")

    # Spacing effect: average improvement from densified over geometric
    spacing_effect_d2 = means["d2_densified"] - means["d2_geometric"]
    spacing_effect_d4 = means["d4_densified"] - means["d4_geometric"]
    spacing_effect = (spacing_effect_d2 + spacing_effect_d4) / 2.0

    # Depth effect: average improvement from d=4 over d=2
    depth_effect_geo = means["d4_geometric"] - means["d2_geometric"]
    depth_effect_den = means["d4_densified"] - means["d2_densified"]
    depth_effect = (depth_effect_geo + depth_effect_den) / 2.0

    cell_str = ", ".join(f"{k}:{means[k]:.3f}" for k in cell_keys)
    detail = (f"spacing_effect={spacing_effect:.3f} depth_effect={depth_effect:.3f}. "
              f"Cells: {cell_str}.")

    max_effect = max(abs(spacing_effect), abs(depth_effect))
    if max_effect < NULL_THRESHOLD:
        return ("SPACING_NULL",
                f"H_null: neither lever active. max_effect={max_effect:.3f}<{NULL_THRESHOLD}. {detail}")

    if abs(spacing_effect) >= EFFECT_THRESHOLD and abs(spacing_effect) >= abs(depth_effect):
        direction = "densified wins" if spacing_effect > 0 else "geometric wins"
        return ("SPACING_DOMINANT",
                f"H_spacing CONFIRMED: spacing_effect={spacing_effect:.3f}>={EFFECT_THRESHOLD} "
                f"dominates depth_effect={depth_effect:.3f}. {direction}. "
                f"PT framing supported: spacing profile is the primary lever. {detail}")

    if abs(depth_effect) >= EFFECT_THRESHOLD and abs(depth_effect) >= abs(spacing_effect):
        direction = "deeper wins" if depth_effect > 0 else "shallower wins"
        return ("DEPTH_DOMINANT",
                f"H_depth CONFIRMED: depth_effect={depth_effect:.3f}>={EFFECT_THRESHOLD} "
                f"dominates spacing_effect={spacing_effect:.3f}. {direction}. "
                f"SWR/1-RSB framing supported: depth is the primary lever. {detail}")

    return ("SPACING_MIDDLE",
            f"Mixed signals: spacing_effect={spacing_effect:.3f} depth_effect={depth_effect:.3f}. "
            f"No clear dominant lever. {detail}")


def self_test_verdict():
    """Self-test: (input -> expected verdict) pairs per formula in prereq."""
    def mk(d2g, d2d, d4g, d4d):
        def cell(r):
            return {"per_seed": {"17": {"retA": r, "bpc_baseline": 1.0, "bpc_after": 1.0}}}
        return {"cells": {
            "d2_geometric": cell(d2g), "d2_densified": cell(d2d),
            "d4_geometric": cell(d4g), "d4_densified": cell(d4d)}}

    cases = [
        # H_spacing: spacing_effect=0.09 > depth_effect=0.01
        (mk(0.80, 0.88, 0.79, 0.89), "SPACING_DOMINANT"),
        # H_depth: depth_effect=0.10 > spacing_effect=0.01
        (mk(0.80, 0.81, 0.90, 0.91), "DEPTH_DOMINANT"),
        # H_null: all same
        (mk(0.85, 0.85, 0.85, 0.85), "SPACING_NULL"),
        # MIDDLE: both effects present but < threshold
        (mk(0.82, 0.84, 0.86, 0.89), "SPACING_MIDDLE"),
        # Inconclusive: no data
        ({}, "SPACING_INCONCLUSIVE"),
    ]
    for summary, expected in cases:
        actual, msg = compute_verdict(summary)
        if actual != expected:
            raise AssertionError(
                f"self_test FAIL: got {actual!r} expected {expected!r}; msg={msg!r}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run(smoke=False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    t0 = time.monotonic()
    print(f"[pt-spacing-cross-cut] device={device} smoke={smoke}", flush=True)

    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    depths = [2] if smoke else DEPTHS_TO_TEST  # smoke: just depth=2 to verify both spacings
    spacings = SPACINGS_TO_TEST

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": seeds,
        "depths": depths,
        "spacings": spacings,
        "base_chunk_fraction": BASE_CHUNK_FRACTION,
        "densified_mid_factor": DENSIFIED_MID_FACTOR,
        "effect_threshold": EFFECT_THRESHOLD,
        "null_threshold": NULL_THRESHOLD,
    }
    print(f"[config] {config}", flush=True)

    cells = {}
    for depth in depths:
        for spacing in spacings:
            cell_key = f"d{depth}_{spacing}"
            per_seed = {}
            kl_vals = []
            for seed in seeds:
                ret_A, bpc_base, bpc_after, mean_kl, fracs = run_one_cell(
                    depth, spacing, seed, config, device)
                per_seed[str(seed)] = {
                    "retA": ret_A, "bpc_baseline": bpc_base, "bpc_after": bpc_after,
                    "mean_adj_kl": mean_kl, "chunk_fracs": fracs}
                kl_str = f"{mean_kl:.4f}" if mean_kl is not None else "N/A"
                print(f"  depth={depth} spacing={spacing} seed={seed}: "
                      f"retA={ret_A:.3f} bpc_base={bpc_base:.4f} bpc_after={bpc_after:.4f} "
                      f"mean_adj_kl={kl_str}", flush=True)
                if mean_kl is not None:
                    kl_vals.append(mean_kl)
            mean_ret = sum(v["retA"] for v in per_seed.values()) / len(per_seed)
            mean_kl_cell = sum(kl_vals) / len(kl_vals) if kl_vals else None
            cells[cell_key] = {"per_seed": per_seed, "mean_retA": mean_ret,
                                "mean_adj_kl": mean_kl_cell}
            kl_str = f"{mean_kl_cell:.4f}" if mean_kl_cell is not None else "N/A"
            print(f"  cell={cell_key} MEAN retA={mean_ret:.3f} mean_adj_kl={kl_str}", flush=True)

    summary = {"cells": cells}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()

    if args.self_test:
        self_test_verdict()
        return

    name = os.environ.get(
        "HDLAB_EXP_NAME",
        "wave14_pt_spacing_cross_cut_v1_smoke" if args.smoke
        else "wave14_pt_spacing_cross_cut_v1")
    out_dir = get_output_dir(name)

    summary, verdict, msg, elapsed, config = run(smoke=args.smoke)

    if args.smoke:
        n_cells = len(summary.get("cells", {}))
        oracle.assert_baseline_high("spacing_cross_cut_n_cells", float(n_cells), 1.5)

    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "elapsed_s": elapsed, "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"[done] elapsed={elapsed:.1f}s verdict={verdict}", flush=True)


if __name__ == "__main__":
    main()
