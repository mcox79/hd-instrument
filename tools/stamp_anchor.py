"""stamp_anchor.py -- Generate anchor scripts from templates by parameter substitution.

Reduces 200-400 lines of hand-typed Python per new anchor (in a known family)
to a single CLI call. Templates live in experiments/_templates/<family>.py.template
with {{TOKEN}} placeholders. Family-specific logic for derived tokens
(snapshot depths, HP/HF thresholds, calibration narrative) lives in this file.

Currently supported families:
    q_b1_chain_depth   — Q-B1 heteroassoc chain at depth-K, N=N
    (PP-48 NKT and Q-A3 cross-layer pending; see TODO at bottom)

Usage:
    python tools/stamp_anchor.py q_b1_chain_depth \\
        --depth 90 --N 8192 --prior-depth 80 \\
        --out experiments/exp_q_b1_chain_depth_90_v1_n8192.py

The output script is production-ready (no further edits expected). Caller
should still run smoke verification before queue_add per discipline.
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = REPO / "experiments" / "_templates"


# ---------------------------------------------------------------------------
# Q-B1 family: heteroassoc chain depth ceiling-chase
# ---------------------------------------------------------------------------

def stamp_q_b1_chain_depth(depth: int, N: int, prior_depth: int) -> dict:
    """Return token-value mapping for Q-B1 template."""
    anchor_name = f"q_b1_chain_depth_{depth}_v1_n{N}"

    # H matrix memory: N*N*4 bytes / 1e6 MB
    h_mem_mb = int(N * N * 4 / 1e6)
    if h_mem_mb < 1000:
        gpu_safety = "Safe on 8 GB GPU"
    elif h_mem_mb < 4000:
        gpu_safety = "Fits in 8 GB GPU with margin"
    else:
        gpu_safety = "Tight on 8 GB GPU; verify capacity before ship"

    # Snapshot depths: standard pattern + every 5 up to DEPTH, plus DEPTH itself
    base = [1, 3, 5, 10, 15, 20, 25, 30, 35, 40, 45]
    snapshots = sorted(set(base + list(range(50, depth + 1, 5))))
    if depth not in snapshots:
        snapshots.append(depth)
    snapshots = sorted(snapshots)
    snapshots_repr = "[" + ", ".join(str(s) for s in snapshots) + "]"

    # HP/HF thresholds: empirical calibration from historical Q-B1 ships
    # Anchor table from existing scripts (verdict-handler-confirmed):
    #   d5=0.95 d10=0.88 d20=0.70 d30=0.55 d45=0.40 d55=0.25 d60=0.20 d70=0.15 d80=0.10
    # Decay is super-exponential (lambda varies from 0.015 at low d to 0.04 at deep d).
    # Beyond d=80 we extrapolate conservatively with lambda=0.030.
    HP_d5 = 0.95
    HP_d10 = 0.88
    HP_d20 = 0.70
    HP_d30 = 0.55
    HP_d45 = 0.40
    # Anchor table for d >= 45 — extends if depth is in table; else extrapolates
    anchor_table = {45: 0.40, 50: 0.32, 55: 0.25, 60: 0.20, 65: 0.17, 70: 0.15, 75: 0.12, 80: 0.10}
    if depth in anchor_table:
        apex_hp = anchor_table[depth]
    elif depth < 45:
        # Earlier depths: shouldn't be templated this way, but compute via linear interp on rough HP_d-table
        # Defensive: just floor at HP_d45
        apex_hp = HP_d45
    else:
        # depth > 80: extrapolate from d=80=0.10 with conservative lambda=0.030
        apex_hp = round(0.10 * math.exp(-(depth - 80) * 0.030), 3)
    # HARD-FAIL: ~40% of HP (3-sigma below HP center, conservative); floor 0.05
    apex_hf = max(round(apex_hp * 0.40, 3), 0.05)

    HF_d5 = 0.80
    HF_d10 = 0.65
    HF_d20 = 0.40

    hp_constants_lines = [
        f"HP_D5 = {HP_d5}",
        f"HP_D10 = {HP_d10}",
        f"HP_D20 = {HP_d20}",
        f"HP_D30 = {HP_d30}",
        f"HP_D45 = {HP_d45}",
        f"HP_D{depth} = {apex_hp}",
        f"HF_D5 = {HF_d5}",
        f"HF_D10 = {HF_d10}",
        f"HF_D20 = {HF_d20}",
        f"HF_D{depth} = {apex_hf}",
    ]
    hp_hf_constants = "\n".join(hp_constants_lines)

    hp_human = (
        f"depth-5 >= {HP_d5} AND depth-10 >= {HP_d10} AND depth-20 >= {HP_d20} "
        f"AND depth-30 >= {HP_d30} AND depth-45 >= {HP_d45} AND depth-{depth} >= {apex_hp}"
    )
    hf_human = (
        f"depth-5 < {HF_d5} OR depth-10 < {HF_d10} OR depth-20 < {HF_d20} "
        f"OR depth-{depth} < {apex_hf}"
    )
    mid_human = (
        f"depth-{depth} in [{apex_hf:.2f}, {apex_hp:.2f}) while earlier depths meet HP"
    )

    calibration = (
        f"Ceiling chase: depth-{prior_depth} HARD_PASS recent cycle. "
        f"Push to depth-{depth} to map degradation slope."
    )
    calibration_detail = (
        f"depth-{prior_depth} HP set per prior cycle; depth-{depth} bands derived "
        f"from empirical Q-B1 decay table (super-exponential, lambda 0.015 at low d "
        f"rising to 0.040 at deep d). For d>80 extrapolated with lambda=0.030. "
        f"HP={apex_hp}; HF={apex_hf} (~2.5x below HP)."
    )

    verdict_body_lines = [
        '    d5 = mean_key("mean_cos_d5")',
        '    d10 = mean_key("mean_cos_d10")',
        '    d20 = mean_key("mean_cos_d20")',
        '    d30 = mean_key("mean_cos_d30")',
        '    d45 = mean_key("mean_cos_d45")',
        f'    dapex = mean_key("mean_cos_d{depth}")',
        "",
        '    summary = (f"d5={d5:.4f}(HP>={HP_D5} HF<{HF_D5}) "',
        '               f"d10={d10:.4f}(HP>={HP_D10} HF<{HF_D10}) "',
        '               f"d20={d20:.4f}(HP>={HP_D20} HF<{HF_D20}) "',
        '               f"d30={d30:.4f}(HP>={HP_D30}) "',
        '               f"d45={d45:.4f}(HP>={HP_D45}) "',
        f'               f"d{depth}={{dapex:.4f}}(HP>={{HP_D{depth}}} HF<{{HF_D{depth}}}) "',
        '               f"n_seeds={len(results)}")',
        "",
        f"    if d5 < HF_D5 or d10 < HF_D10 or d20 < HF_D20 or dapex < HF_D{depth}:",
        '        return ("HARD_FAIL", f"HARD_FAIL: {summary}")',
        "",
        "    hp5 = d5 >= HP_D5",
        "    hp10 = d10 >= HP_D10",
        "    hp20 = d20 >= HP_D20",
        "    hp30 = d30 >= HP_D30",
        "    hp45 = d45 >= HP_D45",
        f"    hpapex = dapex >= HP_D{depth}",
        "",
        "    if hp5 and hp10 and hp20 and hp30 and hp45 and hpapex:",
        f'        return ("HARD_PASS", f"HARD_PASS: all depth thresholds met at N={N} depth-{depth}. {{summary}}")',
        "    n_hp = sum([hp5, hp10, hp20, hp30, hp45, hpapex])",
        '    return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/6 depth HP. {summary}")',
    ]
    verdict_body = "\n".join(verdict_body_lines)

    return {
        "ANCHOR_NAME": anchor_name,
        "N": str(N),
        "DEPTH": str(depth),
        "H_MEM_MB": str(h_mem_mb),
        "GPU_SAFETY_NOTE": gpu_safety,
        "SNAPSHOT_DEPTHS_REPR": snapshots_repr,
        "SNAPSHOT_DEPTHS_LIST": snapshots_repr,
        "CALIBRATION_PARAGRAPH": calibration,
        "CALIBRATION_DETAIL": calibration_detail,
        "HP_BANDS_HUMAN": hp_human,
        "HF_BANDS_HUMAN": hf_human,
        "MID_BAND_HUMAN": mid_human,
        "HP_HF_CONSTANTS": hp_hf_constants,
        "VERDICT_BODY": verdict_body,
    }


# ---------------------------------------------------------------------------
# Substitution engine
# ---------------------------------------------------------------------------

def substitute(template_text: str, tokens: dict[str, str]) -> str:
    """Replace {{TOKEN}} placeholders with values. Errors on unsubstituted tokens."""
    out = template_text
    for k, v in tokens.items():
        out = out.replace("{{" + k + "}}", v)
    # Catch any remaining unsubstituted tokens
    import re
    leftovers = re.findall(r"\{\{[A-Z_][A-Z0-9_]*\}\}", out)
    if leftovers:
        print(f"GATE_FAIL: unsubstituted tokens remain: {sorted(set(leftovers))}",
              file=sys.stderr)
        sys.exit(2)
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Stamp anchor script from template")
    p.add_argument("family", choices=["q_b1_chain_depth"],
                   help="Anchor family (template name)")
    p.add_argument("--out", required=True,
                   help="Output script path (relative to repo root)")
    p.add_argument("--depth", type=int, help="Apex depth (Q-B1)")
    p.add_argument("--N", type=int, help="Production N")
    p.add_argument("--prior-depth", type=int,
                   help="Prior-cycle apex depth (for calibration narrative)")
    args = p.parse_args()

    template_path = TEMPLATES_DIR / f"{args.family}.py.template"
    if not template_path.exists():
        print(f"GATE_FAIL: template not found: {template_path}", file=sys.stderr)
        sys.exit(1)

    template_text = template_path.read_text(encoding="utf-8")

    if args.family == "q_b1_chain_depth":
        if args.depth is None or args.N is None or args.prior_depth is None:
            print("GATE_FAIL: q_b1_chain_depth requires --depth, --N, --prior-depth",
                  file=sys.stderr)
            sys.exit(1)
        tokens = stamp_q_b1_chain_depth(args.depth, args.N, args.prior_depth)
    else:
        print(f"GATE_FAIL: unknown family '{args.family}'", file=sys.stderr)
        sys.exit(1)

    out_text = substitute(template_text, tokens)

    out_path = REPO / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(out_text, encoding="utf-8")
    print(f"STAMPED: {out_path} (family={args.family})")
    print(f"  anchor_name={tokens['ANCHOR_NAME']}")
    try:
        rel = out_path.relative_to(REPO)
        print(f"  Verify by running: python {rel} --self-test")
    except ValueError:
        print(f"  Verify by running: python {out_path} --self-test")


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# TODO: additional templates to add as those families ship
# ---------------------------------------------------------------------------
# - pp48_nkt_depth.py.template       (PP-48 NKT ceiling chase; only NKT_DEPTH +
#                                     total-tree node count differ)
# - pp48_nkt_cross_n.py.template     (PP-48 NKT cross-N envelope; same logic, different N)
# - q_a3_cross_layer.py.template     (Q-A3 cross-layer L=N; requires refactor of
#                                     per-level M_MID constants to a single
#                                     parametric M_MIDS list before templating)
# - pp52_exact_rollback.py.template  (PP-52 Hebbian exact rollback at varying N)
# - pp52_one_shot_addition.py.template (PP-52 one-shot at varying N)
