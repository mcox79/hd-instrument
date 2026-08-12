"""Post-landing cross-cell analysis for the 4-way brain-architecture composition ablation.

Designed to fire when the GPU composition cells land. Reads per-arm metrics across:
  - substrate_owned_predictive_coding_encoder_v1 (Path C: encoder direction)
  - substrate_brain_full_compose_LM_v1 (all 7 mechanisms; maximalist)
  - substrate_pc_hierarchy_text8_lm_v1 (multi-layer PC isolated)
  - substrate_sparse_competitive_readout_lm_v1 (Tonegawa K-WTA isolated)
  - fresh_W_bpc_per_encoder_v2 (5 encoder arms; baseline reference)

Produces a decision matrix:
  - Per-cell: pre-reg HP/HF verdict + per-arm BPC
  - Cross-cell: which mechanism is load-bearing (composition vs individual)
  - Substrate-as-LM gap: did ANY arm beat unigram 7.738?

Usage:
    python tools/composition_landings_analysis.py [--remote]

If --remote, SCPs metrics.json from marsh@home before analysis.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data"

CELLS = [
    ("fair_harness_substrate_as_lm_v1", "FAIR HARNESS (chain-grade): SPARSE_BIPOLAR +0.43 bits over unigram (ENVELOPE one-point)"),
    ("sparse_bipolar_substrate_lm_param_sweep_v1", "Param sweep (HARD_FAIL_SCALING): envelope cap measured; N_TRAIN=1M+N_DIM=16384 ALL FAIL"),
    ("path_c_substrate_owned_encoder_FAIR_HARNESS_v2", "Path C own-encoder (MIDDLE_BAND): +0.119 bits over unigram, loses to word2vec by 0.31"),
    ("brain_compose_fair_harness_debug_v2", "BRAIN_COMPOSE OOM-fix (HARD_PASS inherited): BRAIN_COMPOSE arm STILL inf/nan; 2nd failure mode"),
    ("fair_harness_sparse_bipolar_T_PINNED_witness_v1", "T-PINNED defense (MIDDLE_BAND): T=0.10 EXACT match grid-winner; cherry-pick critique refuted"),
    ("substrate_theta_gamma_nested_oscillation_LM_v1", "Theta-gamma v1 (HARD_FAIL): needs brain-compensation per research drill"),
    ("substrate_theta_gamma_nested_with_brain_compensation_N4096_v1", "Theta-gamma+brain-compose N=4096 (IN-FLIGHT remote CPU)"),
    ("substrate_neuromodulator_3axis_gated_compose_LM_v1", "3-axis neuromod (smoke HP, FULL RUNNING GPU): naive-multiplicative; ACh slot=0 in smoke; tests architectural-limit precedent"),
    ("substrate_dual_trace_sequential_neuromod_LM_v1", "Dual-trace sequential neuromod (IN-FLIGHT GPU): brain-correct alternative; 3-arm direct contrast vs NAIVE_MULT"),
    ("substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu", "Drosophila MB single-modulator (MIDDLE_BAND): lift HALVES from N=512 to N=2048 (same envelope pattern)"),
    ("substrate_owned_predictive_coding_encoder_v1", "Path C v1 (rigged-harness HARD_FAIL; METHODOLOGY-CONFOUND)"),
    ("substrate_brain_full_compose_LM_v1", "Maximalist v1 (rigged-harness HARD_FAIL; METHODOLOGY-CONFOUND)"),
    ("substrate_pc_hierarchy_text8_lm_v1", "Isolated: multi-layer PC (depth ablation)"),
    ("substrate_sparse_competitive_readout_lm_v1", "Isolated: Tonegawa K-WTA non-linear readout"),
    ("fresh_W_bpc_per_encoder_v2", "Encoder ref: 5 encoder arms (clean fresh-W)"),
]

UNIGRAM_FLOOR = 7.738


def scp_metrics(name: str) -> None:
    remote = f"marsh@home:C:/dev/hd-instrument/data/exp_{name}/metrics.json"
    local_dir = DATA / f"exp_{name}"
    local_dir.mkdir(exist_ok=True)
    local = local_dir / "metrics.json"
    try:
        _no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0
        # scp -O legacy mode (popup-fix per testbed 2026-06-28: prevents remote SFTP
        # subsystem fork that on OpenSSH-for-Windows servers spawns visible conhost).
        subprocess.run(["scp", "-O", remote, str(local)], check=False, capture_output=True, timeout=60,
                       creationflags=_no_window)
    except Exception:
        pass


def read_metrics(name: str) -> dict | None:
    path = DATA / f"exp_{name}" / "metrics.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def extract_per_arm_bpc(d: dict) -> dict:
    """Try multiple paths to per-arm BPC summary."""
    detail = d.get("detail", {})
    candidates = [
        detail.get("per_arm_bpc"),
        detail.get("by_arm_agg"),
        detail.get("mean_bpc_per_arm"),
        detail.get("bpc_per_arm"),
    ]
    for c in candidates:
        if c and isinstance(c, dict):
            return c
    # fallback: any dict keyed by ARM_*
    for k, v in detail.items():
        if isinstance(v, dict) and any(arm_k.startswith("ARM_") for arm_k in v.keys()):
            return v
    return {}


def extract_arm_bpc_scalar(val) -> float | None:
    """Pull a scalar BPC out of one arm's value (dict or scalar)."""
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, dict):
        # Common field names across cells
        for k in ("bpc_best_mean", "bpc_mean", "bpc_best", "bpc", "mean_bpc"):
            if k in val and isinstance(val[k], (int, float)):
                f = float(val[k])
                # filter inf/nan markers
                if f == f and f != float("inf") and f != float("-inf"):
                    return f
    return None


def format_cell_report(name: str, label: str, d: dict | None) -> str:
    lines = [f"\n## {label}", f"   anchor: `{name}`"]
    if d is None:
        lines.append("   STATUS: not landed yet (metrics.json missing)")
        return "\n".join(lines)
    verdict = d.get("verdict", "?")
    msg = d.get("verdict_msg", "")
    elapsed = d.get("elapsed_s", 0)
    n_seeds = d.get("n_seeds", "?")
    lines.append(f"   verdict: **{verdict}**  elapsed: {elapsed:.0f}s  n_seeds: {n_seeds}")
    lines.append(f"   verdict_msg: {msg[:300]}")

    arms = extract_per_arm_bpc(d)
    if arms:
        lines.append("   per-arm:")
        for arm, val in arms.items():
            if isinstance(val, (int, float)):
                rel = "BEATS_UNIGRAM" if val < UNIGRAM_FLOOR else f"+{val-UNIGRAM_FLOOR:.3f} above unigram"
                lines.append(f"     {arm:50s} BPC={val:.4f}  [{rel}]")
            elif isinstance(val, dict):
                # try to pull bpc key
                bpc = val.get("bpc") or val.get("bpc_best") or val.get("mean_bpc")
                if bpc is not None and isinstance(bpc, (int, float)):
                    rel = "BEATS_UNIGRAM" if bpc < UNIGRAM_FLOOR else f"+{bpc-UNIGRAM_FLOOR:.3f}"
                    lines.append(f"     {arm:50s} BPC={bpc:.4f}  [{rel}]")
                else:
                    lines.append(f"     {arm:50s} (no scalar bpc)")
    return "\n".join(lines)


def cross_cell_decision_matrix(landings: dict[str, dict]) -> str:
    """Honest cross-cell read: which mechanism is load-bearing?"""
    lines = ["\n## CROSS-CELL DECISION MATRIX\n"]

    beat_unigram = []
    no_beat = []
    not_landed = []
    for name, label in CELLS:
        d = landings.get(name)
        if d is None:
            not_landed.append(name)
            continue
        arms = extract_per_arm_bpc(d)
        any_beat = False
        best_bpc = None
        best_arm = None
        for arm, val in arms.items():
            v = extract_arm_bpc_scalar(val)
            if v is not None:
                if best_bpc is None or v < best_bpc:
                    best_bpc = v
                    best_arm = arm
                if v < UNIGRAM_FLOOR:
                    any_beat = True
        if any_beat:
            beat_unigram.append((name, best_arm, best_bpc))
        else:
            no_beat.append((name, best_arm, best_bpc))

    lines.append(f"### Cells where AT LEAST ONE ARM BEAT UNIGRAM ({UNIGRAM_FLOOR}):")
    if beat_unigram:
        for name, arm, bpc in beat_unigram:
            lines.append(f"  - {name}  best_arm={arm}  BPC={bpc:.4f}  lift={UNIGRAM_FLOOR-bpc:.3f} bits")
    else:
        lines.append("  NONE (substrate-as-LM gap remains; brain-architecture composition did not close)")

    lines.append("\n### Cells where ALL ARMS FAILED to beat unigram:")
    for name, arm, bpc in no_beat:
        lines.append(f"  - {name}  best_arm={arm}  BPC={(bpc if bpc is not None else 'n/a')}")

    if not_landed:
        lines.append("\n### NOT LANDED:")
        for name in not_landed:
            lines.append(f"  - {name}")

    lines.append("\n### LOAD-BEARING MECHANISM ATTRIBUTION (per pre-reg ablation design):")
    has_pc = "substrate_pc_hierarchy_text8_lm_v1" in [n for n, _, _ in beat_unigram]
    has_kwta = "substrate_sparse_competitive_readout_lm_v1" in [n for n, _, _ in beat_unigram]
    has_full = "substrate_brain_full_compose_LM_v1" in [n for n, _, _ in beat_unigram]
    has_pathc = "substrate_owned_predictive_coding_encoder_v1" in [n for n, _, _ in beat_unigram]

    if has_pc and has_kwta and has_full:
        lines.append("  - Multiple mechanisms work; composition likely additive. Best path = brain_full_compose.")
    elif has_full and not has_pc and not has_kwta:
        lines.append("  - ONLY brain_full_compose passes; ISOLATED mechanisms insufficient.")
        lines.append("  - INTERPRETATION: composition is essential; brain-architecture composes")
    elif has_pc and not has_kwta:
        lines.append("  - PC hierarchy alone passes; sparse-competitive ablation didn't.")
        lines.append("  - INTERPRETATION: multi-layer hierarchy is the load-bearing brain mechanism")
    elif has_kwta and not has_pc:
        lines.append("  - Sparse-competitive alone passes; PC hierarchy ablation didn't.")
        lines.append("  - INTERPRETATION: non-linear readout is the load-bearing brain mechanism")
    elif has_pathc and not (has_pc or has_kwta or has_full):
        lines.append("  - ONLY Path C (substrate-owned encoder) passes.")
        lines.append("  - INTERPRETATION: encoder direction is the substrate-product answer")
    elif not (has_pc or has_kwta or has_full or has_pathc):
        lines.append("  - NO arm beat unigram in any cell.")
        lines.append("  - INTERPRETATION: current composition design insufficient.")
        lines.append("  - NEXT: iterate composition design (see notes/next_iteration_composition_spec.md)")
    return "\n".join(lines)


def main():
    do_remote = "--remote" in sys.argv
    landings = {}
    for name, _label in CELLS:
        if do_remote:
            scp_metrics(name)
        landings[name] = read_metrics(name)

    print("# Composition Landings Cross-Cell Analysis")
    print(f"# Generated by tools/composition_landings_analysis.py")
    print(f"# Unigram BPC floor: {UNIGRAM_FLOOR}")

    for name, label in CELLS:
        print(format_cell_report(name, label, landings[name]))

    print(cross_cell_decision_matrix(landings))


if __name__ == "__main__":
    main()
