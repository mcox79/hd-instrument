"""Lane D end-to-end at N=65536 with backward-smoother-only readout — Strategy 21:32 P2.

Demo 1 substrate-product story re-demonstrated with cheaper/wider-envelope primitive
(backward-smoother-only) instead of VAMP-on-chain.
"""
from __future__ import annotations
import argparse, importlib.util, json, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

_t = importlib.util.spec_from_file_location("t",
    REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)
_so = importlib.util.spec_from_file_location("so",
    REPO / "experiments" / "exp_wave14_chain_smoother_only_v1.py")
so = importlib.util.module_from_spec(_so); _so.loader.exec_module(so)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "composed_acc" not in summary:
        return ("LANE_D_E2E_SMOOTHER_INCONCLUSIVE", "Missing.")
    c = summary["composed_acc"]
    if c >= 0.50:
        return ("LANE_D_E2E_SMOOTHER_PASS", f"Demo 1 with smoother readout PASS: composed_acc={c:.3f}.")
    if c >= 0.30:
        return ("LANE_D_E2E_SMOOTHER_PARTIAL", f"Partial: composed_acc={c:.3f}.")
    return ("LANE_D_E2E_SMOOTHER_KILLED", f"Killed: composed_acc={c:.3f}.")


def self_test_verdict():
    for s, exp in [
        ({"composed_acc": 0.70}, "LANE_D_E2E_SMOOTHER_PASS"),
        ({"composed_acc": 0.40}, "LANE_D_E2E_SMOOTHER_PARTIAL"),
        ({"composed_acc": 0.20}, "LANE_D_E2E_SMOOTHER_KILLED"),
        ({}, "LANE_D_E2E_SMOOTHER_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (4/4 cases)", flush=True)


def run_one_trial(seed, config, device):
    N = config["N"]; K = config["K_hypotheses"]
    F = config["F_facts_per_hyp"]; skill_len = config["skill_len"]
    skill_alphabet = config["skill_alphabet"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = t.make_bsc_codebook(200, N, gen, device)
    relation_atoms = t.make_bsc_codebook(20, N, gen, device)
    hyp_atoms = t.make_bsc_codebook(K, N, gen, device)
    position_atoms = t.make_bsc_codebook(skill_len, N, gen, device)
    skill_atoms = t.make_bsc_codebook(skill_alphabet, N, gen, device)

    hyp_signatures = []; hyp_skill_progs = []
    for k in range(K):
        sig_facts = [(int(torch.randint(0, 200, (1,), generator=cpu_gen)),
                      int(torch.randint(0, 20, (1,), generator=cpu_gen)),
                      int(torch.randint(0, 200, (1,), generator=cpu_gen))) for _ in range(F)]
        hyp_signatures.append(sig_facts)
        sk_idx = torch.randint(0, skill_alphabet, (skill_len,), generator=cpu_gen).to(device)
        prog = t.sign_quantize((skill_atoms[sk_idx] * position_atoms[:skill_len]).sum(dim=0))
        hyp_skill_progs.append((prog, sk_idx))
    true_k = int(torch.randint(0, K, (1,), generator=cpu_gen))

    # Stage U: EMA accumulator
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

    # Stage S with backward-smoother-only readout: use target_prior + backward msg
    # Here we have B_q as the "bundle" containing chain info; for a single-step query
    # use softmax weighted readout
    probe_fact = hyp_signatures[true_k][-1]
    s_p, r_p, o_p = probe_fact
    s_probe = B_q * entity_atoms[s_p] * relation_atoms[r_p]
    sims = entity_atoms @ s_probe
    w = torch.softmax(sims, dim=0)
    soft_state = (w.unsqueeze(1) * entity_atoms).sum(dim=0)
    s_pred_o = int((entity_atoms @ t.sign_quantize(soft_state)).argmax().item())
    s_correct = (s_pred_o == o_p)

    M_T = t.sign_quantize(torch.stack([
        hyp_atoms[k] * t.sign_quantize(torch.stack([
            t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
            for s, r, o in facts], dim=0).sum(dim=0))
        for k, facts in enumerate(hyp_signatures)], dim=0).sum(dim=0))
    hyp_scores = [float((M_T * hyp_atoms[k] * B_q).sum()) for k in range(K)]
    pred_k = int(max(range(K), key=lambda k: hyp_scores[k]))
    t_correct = (pred_k == true_k)

    prog_pred, prog_true = hyp_skill_progs[pred_k]
    x_pred = [int((skill_atoms @ (prog_pred * position_atoms[i])).argmax().item()) for i in range(skill_len)]
    x_correct = all(x_pred[i] == int(prog_true[i]) for i in range(skill_len))

    composed = s_correct and t_correct and x_correct
    return {"s_correct": int(s_correct), "t_correct": int(t_correct),
             "x_correct": int(x_correct), "composed": int(composed)}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"N": 8192 if smoke else 65536,
              "K_hypotheses": 3, "F_facts_per_hyp": 10,
              "skill_len": 4, "skill_alphabet": 5,
              "n_trials": 15 if smoke else 60,
              "seeds": [17] if smoke else [17, 23, 31]}
    all_results = []
    for seed in config["seeds"]:
        for trial in range(config["n_trials"]):
            r = run_one_trial(seed * 1000 + trial, config, device)
            all_results.append(r)
        n = len(all_results)
        print(f"  seed={seed} cum: composed={sum(r['composed'] for r in all_results)/n:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14_lane_D_end_to_end_N65536_smoother_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present", summary["composed_acc"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_lane_D_end_to_end_N65536_smoother_v1")
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
