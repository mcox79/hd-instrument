"""Demo 1 Lane D 4-primitive composition under bit-flip noise — Cap 1 envelope expansion.

Cap 1 (Demo 1 Lane D capstone at N=65536) is ✅ FULL at clean observations
(composed_acc=1.000, cycles 130+139). Active-priorities lists as next envelope axis:
"N>=131072 push; 4-primitive composition under noise".

This experiment probes the noise axis at N=65536 (held fixed; GPU required):
inject bit-flip noise into the observation stream at p in {0.0, 0.05, 0.10, 0.20, 0.30}.
The 4-primitive pipeline is: Stage U (EMA working memory) + Stage S (VAMP-class
pattern completion) + Stage T (hypothesis tracking) + Stage X (skill program decode).
Same pipeline as exp_wave14_lane_D_end_to_end_N65536_vamp_v1.py but with noise sweep.

Cap-1 next-axis framing: does the Demo 1 capstone tolerate deployment-realistic
observation noise? Noise levels cover: clean baseline (0%), low (5%), moderate (10%),
high (20%), stress (30%).

Verdict thresholds (composed_acc = all 4 stages correct simultaneously):
  DEMO1_NOISE_ROBUST    -- composed_acc(p=0.10) >= 0.50 AND composed_acc(p=0.0) >= 0.50
  DEMO1_NOISE_BRITTLE   -- composed_acc(p=0.10) < 0.50 but composed_acc(p=0.0) >= 0.50
  DEMO1_NOISE_BROKEN    -- composed_acc(p=0.0) < 0.50 (regression from capstone FULL)
  DEMO1_NOISE_INCONCLUSIVE

Pre-reg: preregs/2026-05-23_wave14_demo1_noise_envelope_v1.md
Queue: overnight_queue (GPU; N=65536 requires CUDA)
Memory budget: N=65536 float32 codebook = 65536 x 200 x 4 = 52 MB per codebook;
  5 codebooks (entity, relation, hyp, position, skill) ~260 MB total; well under 8 GB.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, importlib.util, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_t = importlib.util.spec_from_file_location(
    "t", REPO / "experiments" / "exp_wave14t_multihop_v3.py")
t = importlib.util.module_from_spec(_t)
_t.loader.exec_module(t)

NOISE_LEVELS_FULL = [0.0, 0.05, 0.10, 0.20, 0.30]
NOISE_LEVELS_SMOKE = [0.0, 0.10]

# Hard thresholds
HARD_PASS_P10 = 0.50   # composed_acc at 10% flip for ROBUST verdict
HARD_PASS_CLEAN = 0.50 # clean composed_acc must hold (capstone regression guard)


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"metrics missing required keys: {set(d.keys())}")


def compute_verdict(summary):
    """Verdict logic based on composed_acc across noise levels."""
    if "acc_per_noise" not in summary:
        return ("DEMO1_NOISE_INCONCLUSIVE", "Missing acc_per_noise.")
    apn = summary["acc_per_noise"]
    clean = apn.get("0.00", apn.get("0.0", None))
    p10 = apn.get("0.10", None)
    if clean is None:
        return ("DEMO1_NOISE_INCONCLUSIVE", "Clean baseline missing from acc_per_noise.")
    if clean < HARD_PASS_CLEAN:
        return ("DEMO1_NOISE_BROKEN",
                f"Clean composed_acc={clean:.3f} < {HARD_PASS_CLEAN} (regression from "
                f"capstone FULL at 1.000). Pipeline broken. acc_per_noise={apn}.")
    if p10 is None:
        return ("DEMO1_NOISE_INCONCLUSIVE", "p=0.10 cell missing; check noise_levels config.")
    if p10 >= HARD_PASS_P10:
        return ("DEMO1_NOISE_ROBUST",
                f"Demo 1 noise-robust: composed_acc at p=0.10 = {p10:.3f} >= {HARD_PASS_P10}; "
                f"clean={clean:.3f}. Cap 1 envelope extends to moderate noise. "
                f"acc_per_noise={apn}.")
    return ("DEMO1_NOISE_BRITTLE",
            f"Demo 1 noise-brittle: composed_acc at p=0.10 = {p10:.3f} < {HARD_PASS_P10}; "
            f"clean={clean:.3f}. Cap 1 envelope does not extend to 10% bit-flip noise. "
            f"acc_per_noise={apn}.")


def self_test_verdict():
    cases = [
        ({"acc_per_noise": {"0.00": 1.0, "0.10": 0.65, "0.20": 0.30}}, "DEMO1_NOISE_ROBUST"),
        ({"acc_per_noise": {"0.00": 1.0, "0.10": 0.30, "0.20": 0.10}}, "DEMO1_NOISE_BRITTLE"),
        ({"acc_per_noise": {"0.00": 0.2, "0.10": 0.10}}, "DEMO1_NOISE_BROKEN"),
        ({}, "DEMO1_NOISE_INCONCLUSIVE"),
        ({"acc_per_noise": {"0.00": 0.9}}, "DEMO1_NOISE_INCONCLUSIVE"),  # p10 missing
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: compute_verdict({s}) = {got}, expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def flip_bits(vec, p_flip, gen):
    """Bipolar bit flip: each entry flipped with probability p_flip."""
    if p_flip == 0.0:
        return vec
    mask = (torch.rand(vec.shape, generator=gen, device=vec.device) < p_flip).float()
    flip = 1.0 - 2.0 * mask  # +1 (no flip) or -1 (flip)
    return vec * flip


def run_one_trial(seed, p_flip, config, device):
    """Run 4-primitive Demo 1 pipeline at N=65536 with observation noise at rate p_flip."""
    N = config["N"]
    K = config["K_hypotheses"]
    F = config["F_facts_per_hyp"]
    skill_len = config["skill_len"]
    skill_alphabet = config["skill_alphabet"]

    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)

    entity_atoms = t.make_bsc_codebook(200, N, gen, device)      # 200 entity HD vectors
    relation_atoms = t.make_bsc_codebook(20, N, gen, device)     # 20 relation HD vectors
    hyp_atoms = t.make_bsc_codebook(K, N, gen, device)           # K hypothesis bundles
    position_atoms = t.make_bsc_codebook(skill_len, N, gen, device)
    skill_atoms = t.make_bsc_codebook(skill_alphabet, N, gen, device)

    # Generate K hypothesis signatures and skill programs
    hyp_signatures = []
    hyp_skill_progs = []
    for k in range(K):
        sig_facts = [
            (int(torch.randint(0, 200, (1,), generator=cpu_gen)),
             int(torch.randint(0, 20, (1,), generator=cpu_gen)),
             int(torch.randint(0, 200, (1,), generator=cpu_gen)))
            for _ in range(F)
        ]
        hyp_signatures.append(sig_facts)
        skill_indices = torch.randint(0, skill_alphabet, (skill_len,),
                                      generator=cpu_gen).to(device)
        prog = t.sign_quantize(
            (skill_atoms[skill_indices] * position_atoms[:skill_len]).sum(dim=0))
        hyp_skill_progs.append((prog, skill_indices))

    true_k = int(torch.randint(0, K, (1,), generator=cpu_gen))

    # Stage U: EMA working-memory accumulator (decay=0.95)
    decay = 0.95
    B = torch.zeros(N, device=device)
    obs_stream = hyp_signatures[true_k] + [
        (int(torch.randint(0, 200, (1,), generator=cpu_gen)),
         int(torch.randint(0, 20, (1,), generator=cpu_gen)),
         int(torch.randint(0, 200, (1,), generator=cpu_gen)))
        for _ in range(5)
    ]
    for s, r, o in obs_stream:
        triple = (entity_atoms[s] * relation_atoms[r] * entity_atoms[o]).float()
        if p_flip > 0.0:
            triple = flip_bits(triple, p_flip, gen)   # noise injected into observation
        B = decay * B + triple
    B_q = t.sign_quantize(B)

    # Stage S: VAMP-class pattern completion from working memory
    probe_fact = hyp_signatures[true_k][-1]
    s_p, r_p, o_p = probe_fact
    s_probe = B_q * entity_atoms[s_p] * relation_atoms[r_p]
    sims = entity_atoms @ s_probe
    w = torch.softmax(sims, dim=0)
    soft_state = (w.unsqueeze(1) * entity_atoms).sum(dim=0)
    s_pred_o = int((entity_atoms @ t.sign_quantize(soft_state)).argmax().item())
    s_correct = int(s_pred_o == o_p)

    # Stage T: hypothesis tracking via bundle scoring against working memory
    M_T = t.sign_quantize(torch.stack([
        hyp_atoms[k] * t.sign_quantize(
            torch.stack([
                t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
                for s, r, o in facts
            ], dim=0).sum(dim=0))
        for k, facts in enumerate(hyp_signatures)
    ], dim=0).sum(dim=0))
    hyp_scores = [float((M_T * hyp_atoms[k] * B_q).sum()) for k in range(K)]
    pred_k = int(max(range(K), key=lambda k: hyp_scores[k]))
    t_correct = int(pred_k == true_k)

    # Stage X: skill program decode
    prog_pred, prog_true = hyp_skill_progs[pred_k]
    x_pred = [
        int((skill_atoms @ (prog_pred * position_atoms[i])).argmax().item())
        for i in range(skill_len)
    ]
    x_correct = int(all(x_pred[i] == int(prog_true[i]) for i in range(skill_len)))

    composed = int(s_correct and t_correct and x_correct)
    return {
        "composed": composed,
        "s_correct": s_correct,
        "t_correct": t_correct,
        "x_correct": x_correct,
    }


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    noise_levels = NOISE_LEVELS_SMOKE if smoke else NOISE_LEVELS_FULL
    config = {
        "mode": "smoke" if smoke else "full",
        "N": 8192 if smoke else 65536,
        "K_hypotheses": 3,
        "F_facts_per_hyp": 10,
        "skill_len": 4,
        "skill_alphabet": 5,
        "n_trials_per_noise_per_seed": 10 if smoke else 40,
        "noise_levels": noise_levels,
        "seeds": [17] if smoke else [17, 23, 31],
        "device": str(device),
        "note": "Cap 1 Demo 1 Lane D N=65536 noise envelope; 4-primitive composition",
    }

    print(f"Demo1 noise envelope: N={config['N']} device={device} "
          f"seeds={config['seeds']} noise={noise_levels}", flush=True)

    acc_per_noise = {}
    for p in noise_levels:
        results = []
        for seed in config["seeds"]:
            for trial in range(config["n_trials_per_noise_per_seed"]):
                r = run_one_trial(seed * 10000 + trial, p, config, device)
                results.append(r)
        n = len(results)
        c_acc = sum(r["composed"] for r in results) / n
        s_acc = sum(r["s_correct"] for r in results) / n
        t_acc = sum(r["t_correct"] for r in results) / n
        x_acc = sum(r["x_correct"] for r in results) / n
        key = f"{p:.2f}"
        acc_per_noise[key] = c_acc
        print(f"  p={p:.2f}: composed={c_acc:.3f} "
              f"(S={s_acc:.3f} T={t_acc:.3f} X={x_acc:.3f}) n={n}", flush=True)

    summary = {
        "acc_per_noise": acc_per_noise,
        "n_trials_per_cell": config["n_trials_per_noise_per_seed"] * len(config["seeds"]),
        "device": str(device),
        "N": config["N"],
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_demo1_noise_envelope_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Guard: clean baseline must be present
    clean = summary["acc_per_noise"].get("0.00", summary["acc_per_noise"].get("0.0", 0.0))
    oracle.assert_baseline_high("clean_composed_acc", clean, 0.10)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_demo1_noise_envelope_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
