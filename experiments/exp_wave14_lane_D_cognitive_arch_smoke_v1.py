"""Lane D Cognitive Architecture integration smoke — composes Bet S + T + U + X.

Per cap_map v79 Phase 3: Lane D = cognitive architecture (TAM $30-50B+).
Substrate-product demo composing validated primitives:
  - Bet S Pattern completion: bidirectional triple recall
  - Bet T Hypothesis tracking: K competing hypothesis bundles
  - Bet U Working memory + decay: recency gradient
  - Bet X Skill composition: position-indexed program

Demo: an agent has a short-term working memory of recent observations
(Bet U), maintains 3 candidate hypotheses about what's happening (Bet T),
can pattern-complete missing slots (Bet S), and executes multi-step skills
(Bet X). Smoke verifies all 4 primitives still work when composed in one
substrate.

Pre-reg: preregs/2026-05-22_wave14_lane_D_cognitive_arch_smoke_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_t = importlib.util.spec_from_file_location("t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "S_acc" not in summary:
        return ("LANE_D_INCONCLUSIVE", "Missing.")
    s_acc = summary["S_acc"]; t_acc = summary["T_acc"]
    u_recent = summary["U_recent"]; x_acc = summary["X_acc"]
    failures = []
    if s_acc < 0.70: failures.append(f"S={s_acc:.3f}")
    if t_acc < 0.70: failures.append(f"T={t_acc:.3f}")
    if u_recent < 0.70: failures.append(f"U_recent={u_recent:.3f}")
    if x_acc < 0.70: failures.append(f"X={x_acc:.3f}")
    if not failures:
        return ("LANE_D_COMPOSE",
                f"All 4 Lane D primitives compose: S={s_acc:.3f}, T={t_acc:.3f}, "
                f"U_recent={u_recent:.3f}, X={x_acc:.3f}. Cognitive architecture "
                f"substrate-demo viable.")
    if len(failures) >= 3:
        return ("LANE_D_INCOMPATIBLE",
                f"Primitive composition fails on {len(failures)}/4 primitives: {failures}.")
    return ("LANE_D_PARTIAL",
            f"Partial composition: {len(failures)} primitive(s) below 0.70: {failures}.")


def self_test_verdict():
    cases = [
        ({"S_acc": 0.85, "T_acc": 0.80, "U_recent": 0.90, "X_acc": 0.85}, "LANE_D_COMPOSE"),
        ({"S_acc": 0.85, "T_acc": 0.50, "U_recent": 0.90, "X_acc": 0.85}, "LANE_D_PARTIAL"),
        ({"S_acc": 0.40, "T_acc": 0.50, "U_recent": 0.40, "X_acc": 0.50}, "LANE_D_INCOMPATIBLE"),
        ({}, "LANE_D_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_seed(seed, config, device):
    """Build a single substrate that hosts all 4 primitives; measure each."""
    N = config["N"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    # Shared codebooks (single substrate, multiple roles)
    entity_atoms = t.make_bsc_codebook(100, N, gen, device)
    relation_atoms = t.make_bsc_codebook(20, N, gen, device)
    hyp_atoms = t.make_bsc_codebook(3, N, gen, device)
    position_atoms = t.make_bsc_codebook(8, N, gen, device)
    skill_atoms = t.make_bsc_codebook(5, N, gen, device)

    # === Bet S: pattern completion ===
    s_facts = [(int(torch.randint(0, 100, (1,), generator=cpu_gen)),
                 int(torch.randint(0, 20, (1,), generator=cpu_gen)),
                 int(torch.randint(0, 100, (1,), generator=cpu_gen))) for _ in range(50)]
    M_S = t.sign_quantize(torch.stack([t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
                                                for s, r, o in s_facts], dim=0).sum(dim=0))
    s_correct = 0
    for s, r, o in s_facts[:20]:
        probe = M_S * entity_atoms[s] * relation_atoms[r]
        if int((entity_atoms @ probe).argmax()) == o: s_correct += 1
    s_acc = s_correct / 20

    # === Bet T: 3 hypothesis tracking ===
    hyp_facts = []
    for k in range(3):
        h_facts = [(int(torch.randint(0, 100, (1,), generator=cpu_gen)),
                    int(torch.randint(0, 20, (1,), generator=cpu_gen)),
                    int(torch.randint(0, 100, (1,), generator=cpu_gen))) for _ in range(10)]
        hyp_facts.append(h_facts)
    M_T = t.sign_quantize(torch.stack([
        hyp_atoms[k] * t.sign_quantize(torch.stack([
            t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
            for s, r, o in facts], dim=0).sum(dim=0))
        for k, facts in enumerate(hyp_facts)], dim=0).sum(dim=0))
    t_correct = 0; t_total = 0
    for k, facts in enumerate(hyp_facts):
        for s, r, o in facts:
            probe = M_T * hyp_atoms[k] * entity_atoms[s] * relation_atoms[r]
            if int((entity_atoms @ probe).argmax()) == o: t_correct += 1
            t_total += 1
    t_acc = t_correct / t_total

    # === Bet U: working memory decay ===
    B = torch.zeros(N, device=device)
    u_facts = [(int(torch.randint(0, 100, (1,), generator=cpu_gen)),
                 int(torch.randint(0, 20, (1,), generator=cpu_gen)),
                 int(torch.randint(0, 100, (1,), generator=cpu_gen))) for _ in range(40)]
    decay = 0.95
    for s, r, o in u_facts:
        triple = (entity_atoms[s] * relation_atoms[r] * entity_atoms[o]).float()
        B = decay * B + triple
    B_q = t.sign_quantize(B)
    u_recent_correct = 0
    for s, r, o in u_facts[-5:]:
        probe = B_q * entity_atoms[s] * relation_atoms[r]
        if int((entity_atoms @ probe).argmax()) == o: u_recent_correct += 1
    u_recent = u_recent_correct / 5

    # === Bet X: skill composition (position-indexed) ===
    x_correct = 0; x_total = 0
    for _ in range(10):
        skill_indices = torch.randint(0, 5, (4,), generator=cpu_gen).to(device)
        prog = t.sign_quantize((skill_atoms[skill_indices] * position_atoms[:4]).sum(dim=0))
        for i in range(4):
            probe = prog * position_atoms[i]
            if int((skill_atoms @ probe).argmax()) == int(skill_indices[i]): x_correct += 1
            x_total += 1
    x_acc = x_correct / x_total

    return {"S_acc": s_acc, "T_acc": t_acc, "U_recent": u_recent, "X_acc": x_acc}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "seeds": [17] if smoke else [17, 23, 31]}
    per_seed = []
    for s in config["seeds"]:
        r = run_one_seed(s, config, device)
        per_seed.append(r)
        print(f"  seed={s}: S={r['S_acc']:.3f} T={r['T_acc']:.3f} U={r['U_recent']:.3f} X={r['X_acc']:.3f}", flush=True)
    summary = {k: sum(p[k] for p in per_seed) / len(per_seed)
                for k in ["S_acc", "T_acc", "U_recent", "X_acc"]}
    summary["per_seed"] = per_seed
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_lane_D_cognitive_arch_smoke_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_primitive_works", max(summary["S_acc"], summary["T_acc"], summary["U_recent"], summary["X_acc"]), 0.30)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_lane_D_cognitive_arch_smoke_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
