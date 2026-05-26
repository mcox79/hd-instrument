"""Lane D noise robustness — pipeline survival under Hamming-flipped observations.

Lane D end-to-end shipped composed_acc=1.000 on clean observations. This tests
robustness: inject bit-flips into the observation stream at rates
{0%, 5%, 10%, 20%, 30%} and measure how composed_acc degrades.

Substrate-product question: is the cognitive architecture pipeline robust
enough to claim deployment-grade or is it brittle?

Verdict thresholds:
  NOISE_ROBUST:    composed_acc(10% flip) >= 0.50
  NOISE_BRITTLE:   composed_acc(10% flip) < 0.50 but composed_acc(0%) >= 0.50
  NOISE_BROKEN:    composed_acc(0%) < 0.50 (regression)
  NOISE_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_lane_D_noise_robust_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_e2e = importlib.util.spec_from_file_location("e2e",
    REPO / "experiments" / "exp_wave14_lane_D_end_to_end_v1.py")
e2e = importlib.util.module_from_spec(_e2e); _e2e.loader.exec_module(e2e)
_t = importlib.util.spec_from_file_location("t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t); _t.loader.exec_module(t)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_per_noise" not in summary:
        return ("NOISE_INCONCLUSIVE", "Missing.")
    apn = summary["acc_per_noise"]
    clean = apn.get("0.0", 0.0)
    mid = apn.get("0.10", 0.0)
    if clean < 0.50:
        return ("NOISE_BROKEN",
                f"Clean composed_acc={clean:.3f} < 0.50 (regression from end-to-end PASS at 1.0). "
                f"acc_per_noise={apn}.")
    if mid >= 0.50:
        return ("NOISE_ROBUST",
                f"composed_acc at 10% bit-flip = {mid:.3f} (>=0.50); clean={clean:.3f}. "
                f"Lane D pipeline tolerates realistic observation noise. acc_per_noise={apn}.")
    return ("NOISE_BRITTLE",
            f"composed_acc at 10% bit-flip = {mid:.3f} (<0.50); clean={clean:.3f}. "
            f"Pipeline brittle to realistic noise. acc_per_noise={apn}.")


def self_test_verdict():
    cases = [
        ({"acc_per_noise": {"0.0": 1.0, "0.05": 0.95, "0.10": 0.80, "0.20": 0.40}}, "NOISE_ROBUST"),
        ({"acc_per_noise": {"0.0": 0.9, "0.05": 0.6, "0.10": 0.20, "0.20": 0.05}}, "NOISE_BRITTLE"),
        ({"acc_per_noise": {"0.0": 0.3, "0.05": 0.2}}, "NOISE_BROKEN"),
        ({}, "NOISE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def flip_bits(vec, p_flip, gen, device):
    """Bipolar bit flip at rate p_flip."""
    flips = (torch.rand(vec.shape, generator=gen, device=device) < p_flip).float() * (-2.0) + 1.0
    return vec * flips


def run_one_trial_with_noise(seed, p_flip, config, device):
    N = config["N"]
    K = config["K_hypotheses"]
    F = config["F_facts_per_hyp"]
    skill_len = config["skill_len"]
    skill_alphabet = config["skill_alphabet"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)

    entity_atoms = t.make_bsc_codebook(200, N, gen, device)
    relation_atoms = t.make_bsc_codebook(20, N, gen, device)
    hyp_atoms = t.make_bsc_codebook(K, N, gen, device)
    position_atoms = t.make_bsc_codebook(skill_len, N, gen, device)
    skill_atoms = t.make_bsc_codebook(skill_alphabet, N, gen, device)

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

    true_k = int(torch.randint(0, K, (1,), generator=cpu_gen))

    decay = 0.95
    B = torch.zeros(N, device=device)
    obs_stream = hyp_signatures[true_k] + \
                 [(int(torch.randint(0, 200, (1,), generator=cpu_gen)),
                   int(torch.randint(0, 20, (1,), generator=cpu_gen)),
                   int(torch.randint(0, 200, (1,), generator=cpu_gen))) for _ in range(5)]
    for s, r, o in obs_stream:
        triple = (entity_atoms[s] * relation_atoms[r] * entity_atoms[o]).float()
        if p_flip > 0:
            triple = flip_bits(triple, p_flip, gen, device)
        B = decay * B + triple
    B_q = t.sign_quantize(B)

    probe_fact = hyp_signatures[true_k][-1]
    s_p, r_p, o_p = probe_fact
    s_probe = B_q * entity_atoms[s_p] * relation_atoms[r_p]
    s_correct = (int((entity_atoms @ s_probe).argmax().item()) == o_p)

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
    return {"composed": int(composed), "s_correct": int(s_correct),
             "t_correct": int(t_correct), "x_correct": int(x_correct)}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "K_hypotheses": 3, "F_facts_per_hyp": 10,
              "skill_len": 4, "skill_alphabet": 5,
              "n_trials_per_seed": 20 if smoke else 80,
              "noise_levels": [0.0, 0.10] if smoke else [0.0, 0.05, 0.10, 0.20, 0.30],
              "seeds": [17] if smoke else [17, 23, 31]}
    acc_per_noise = {}
    for p in config["noise_levels"]:
        results = []
        for seed in config["seeds"]:
            for trial in range(config["n_trials_per_seed"]):
                r = run_one_trial_with_noise(seed * 1000 + trial, p, config, device)
                results.append(r)
        c_acc = sum(r["composed"] for r in results) / len(results)
        acc_per_noise[f"{p:.2f}".rstrip("0").rstrip(".") if p == 0.0 else f"{p:.2f}"] = c_acc
        # Normalize key: "0.0" for p=0, "0.05", "0.10"...
        print(f"  p_flip={p:.2f}: composed_acc={c_acc:.3f} ({sum(r['composed'] for r in results)}/{len(results)})", flush=True)
    # Renormalize keys for verdict lookup
    norm = {}
    for p in config["noise_levels"]:
        key = "0.0" if p == 0.0 else f"{p:.2f}"
        # Find original key
        for k in acc_per_noise:
            if abs(float(k) - p) < 1e-6:
                norm[key] = acc_per_noise[k]
                break
    summary = {"acc_per_noise": norm}
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
    out_dir = get_output_dir("wave14_lane_D_noise_robust_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("clean_acc", summary["acc_per_noise"].get("0.0", 0.0), 0.30)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_lane_D_noise_robust_v1")
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
