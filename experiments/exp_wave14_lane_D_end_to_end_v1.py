"""Lane D end-to-end cognitive architecture demo — chained substrate flow.

Per cap_map v79 Phase 4: Lane D end-to-end demo composes 4 primitives in a
PIPELINE (not just side-by-side). Output of stage N feeds stage N+1.

Pipeline (medical-triage analog):
  Stage 1 (Bet U working memory): stream of observation triples accumulates in
    EMA buffer B with decay 0.95.
  Stage 2 (Bet S pattern completion): query B for missing fact -> entity.
  Stage 3 (Bet T hypothesis tracking): predict which of K=3 hypothesis bundles
    is consistent with the observation stream by scoring evidence overlap.
  Stage 4 (Bet X skill composition): given chosen hypothesis, decode the
    associated 4-step skill program.

Verdict thresholds:
  END_TO_END_PASS: composed_acc >= 0.50 (chained failures multiply)
  END_TO_END_PARTIAL: 0.25 <= composed_acc < 0.50 (some stages drop)
  END_TO_END_BROKEN: composed_acc < 0.25 (pipeline collapses)

Pre-reg: preregs/2026-05-22_wave14_lane_D_end_to_end_v1.md
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
    if "composed_acc" not in summary:
        return ("LANE_D_E2E_INCONCLUSIVE", "Missing.")
    c = summary["composed_acc"]
    s1 = summary["stage_s_acc"]; s2 = summary["stage_t_acc"]; s3 = summary["stage_x_acc"]
    if c >= 0.50:
        return ("LANE_D_E2E_PASS",
                f"End-to-end Lane D pipeline composes: composed_acc={c:.3f} (>=0.50). "
                f"Stages: S={s1:.3f} -> T={s2:.3f} -> X={s3:.3f}. Substrate-product "
                f"chained cognitive architecture viable.")
    if c < 0.25:
        return ("LANE_D_E2E_BROKEN",
                f"End-to-end Lane D pipeline collapses: composed_acc={c:.3f} (<0.25). "
                f"Stages: S={s1:.3f} -> T={s2:.3f} -> X={s3:.3f}. Stage errors compound.")
    return ("LANE_D_E2E_PARTIAL",
            f"End-to-end Lane D pipeline partial: composed_acc={c:.3f} "
            f"(0.25 <= acc < 0.50). Stages: S={s1:.3f} -> T={s2:.3f} -> X={s3:.3f}. "
            f"Identify weakest link.")


def self_test_verdict():
    cases = [
        ({"composed_acc": 0.65, "stage_s_acc": 0.9, "stage_t_acc": 0.85, "stage_x_acc": 0.85}, "LANE_D_E2E_PASS"),
        ({"composed_acc": 0.35, "stage_s_acc": 0.7, "stage_t_acc": 0.7, "stage_x_acc": 0.7}, "LANE_D_E2E_PARTIAL"),
        ({"composed_acc": 0.10, "stage_s_acc": 0.5, "stage_t_acc": 0.4, "stage_x_acc": 0.5}, "LANE_D_E2E_BROKEN"),
        ({}, "LANE_D_E2E_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_trial(seed, config, device):
    """One end-to-end trial: stream observations, completes to skill program."""
    N = config["N"]
    K = config["K_hypotheses"]
    F = config["F_facts_per_hyp"]
    skill_len = config["skill_len"]
    skill_alphabet = config["skill_alphabet"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)

    # Shared substrate codebooks
    entity_atoms = t.make_bsc_codebook(200, N, gen, device)
    relation_atoms = t.make_bsc_codebook(20, N, gen, device)
    hyp_atoms = t.make_bsc_codebook(K, N, gen, device)
    position_atoms = t.make_bsc_codebook(skill_len, N, gen, device)
    skill_atoms = t.make_bsc_codebook(skill_alphabet, N, gen, device)

    # Build K hypotheses, each with a signature fact-set and a recovery skill program
    hyp_signatures = []
    hyp_skill_progs = []
    for k in range(K):
        sig_facts = [(int(torch.randint(0, 200, (1,), generator=cpu_gen)),
                      int(torch.randint(0, 20, (1,), generator=cpu_gen)),
                      int(torch.randint(0, 200, (1,), generator=cpu_gen))) for _ in range(F)]
        hyp_signatures.append(sig_facts)
        skill_indices = torch.randint(0, skill_alphabet, (skill_len,), generator=cpu_gen).to(device)
        prog = t.sign_quantize((skill_atoms[skill_indices] * position_atoms[:skill_len]).sum(dim=0))
        hyp_skill_progs.append((prog, skill_indices))

    # Pick the ground-truth hypothesis for this trial
    true_k = int(torch.randint(0, K, (1,), generator=cpu_gen))

    # === Stage 1 (Bet U): stream observations into EMA buffer B ===
    # Observations = true hyp's signature facts in temporal order with mild noise
    decay = 0.95
    B = torch.zeros(N, device=device)
    obs_stream = hyp_signatures[true_k] + \
                 [(int(torch.randint(0, 200, (1,), generator=cpu_gen)),
                   int(torch.randint(0, 20, (1,), generator=cpu_gen)),
                   int(torch.randint(0, 200, (1,), generator=cpu_gen))) for _ in range(5)]
    for s, r, o in obs_stream:
        triple = (entity_atoms[s] * relation_atoms[r] * entity_atoms[o]).float()
        B = decay * B + triple
    B_q = t.sign_quantize(B)

    # === Stage 2 (Bet S): pattern-complete a recent fact ===
    # Pick a fact from the true hypothesis and ask the substrate to fill in 'o'
    probe_fact = hyp_signatures[true_k][-1]
    s_p, r_p, o_p = probe_fact
    s_probe = B_q * entity_atoms[s_p] * relation_atoms[r_p]
    s_pred_o = int((entity_atoms @ s_probe).argmax().item())
    s_correct = (s_pred_o == o_p)

    # === Stage 3 (Bet T): identify hypothesis by evidence overlap ===
    # Build M_T from all K hypothesis bundles; ask which h_k best explains B
    M_T = t.sign_quantize(torch.stack([
        hyp_atoms[k] * t.sign_quantize(torch.stack([
            t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
            for s, r, o in facts], dim=0).sum(dim=0))
        for k, facts in enumerate(hyp_signatures)], dim=0).sum(dim=0))
    # Score each hypothesis by similarity of its unbound projection to B_q
    hyp_scores = []
    for k in range(K):
        unbound = M_T * hyp_atoms[k]  # peek what M_T thinks hypothesis k contains
        # Compare to B_q: cosine-ish via dot product
        score = float((unbound * B_q).sum())
        hyp_scores.append(score)
    pred_k = int(max(range(K), key=lambda k: hyp_scores[k]))
    t_correct = (pred_k == true_k)

    # === Stage 4 (Bet X): given predicted hypothesis, decode its skill program ===
    prog_pred, prog_true = hyp_skill_progs[pred_k]
    x_pred = []
    for i in range(skill_len):
        probe = prog_pred * position_atoms[i]
        x_pred.append(int((skill_atoms @ probe).argmax().item()))
    x_correct = all(x_pred[i] == int(prog_true[i]) for i in range(skill_len))

    # End-to-end success requires ALL stages right
    composed = s_correct and t_correct and x_correct

    return {"s_correct": int(s_correct), "t_correct": int(t_correct),
            "x_correct": int(x_correct), "composed": int(composed)}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "K_hypotheses": 3,
              "F_facts_per_hyp": 5 if smoke else 10,
              "skill_len": 4,
              "skill_alphabet": 5,
              "n_trials": 20 if smoke else 100,
              "seeds": [17] if smoke else [17, 23, 31]}
    all_results = []
    for seed in config["seeds"]:
        for trial in range(config["n_trials"]):
            r = run_one_trial(seed * 1000 + trial, config, device)
            all_results.append(r)
        n = len(all_results)
        s_acc = sum(r["s_correct"] for r in all_results) / n
        t_acc = sum(r["t_correct"] for r in all_results) / n
        x_acc = sum(r["x_correct"] for r in all_results) / n
        c_acc = sum(r["composed"] for r in all_results) / n
        print(f"  seed={seed} cum: S={s_acc:.3f} T={t_acc:.3f} X={x_acc:.3f} composed={c_acc:.3f}", flush=True)
    n = len(all_results)
    summary = {"stage_s_acc": sum(r["s_correct"] for r in all_results) / n,
               "stage_t_acc": sum(r["t_correct"] for r in all_results) / n,
               "stage_x_acc": sum(r["x_correct"] for r in all_results) / n,
               "composed_acc": sum(r["composed"] for r in all_results) / n,
               "n_trials_total": n}
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
    out_dir = get_output_dir("wave14_lane_D_end_to_end_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("any_stage", max(summary["stage_s_acc"], summary["stage_t_acc"], summary["stage_x_acc"]), 0.20)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_lane_D_end_to_end_v1")
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
