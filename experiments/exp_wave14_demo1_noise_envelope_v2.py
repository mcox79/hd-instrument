"""Demo 1 Lane D S->T->X capstone noise envelope expansion v2 — inter-stage W bit-flip.

Demo 1 Lane D (agent memory SDK 3-stage S->T->X pipeline) is v153 FULL at N=65536
composed_acc=1.000. This experiment characterizes the noise envelope by injecting
independent bit-flip noise at rate p into the working-memory vector W (B_q) BETWEEN
pipeline stages: after Stage U EMA accumulates B_q, each coordinate is flipped
independently at probability p before Stage S and again (fresh flip) before Stage T
and Stage X readouts. This is a DIFFERENT noise axis from v1 (which flipped observation
triples before accumulation); here noise models W read-out corruption / wire noise
in the memory bus between stages.

Noise levels: p in {0.0, 0.05, 0.10, 0.20, 0.30}
Multi-seed: seeds = [17, 23, 31]
N (FULL): 65536

Verdicts (composed_acc = all 3 stages S, T, X correct simultaneously):
  DEMO1_NOISE_ENVELOPE_PASS   -- composed_acc(p=0.00) >= 0.80 AND composed_acc(p=0.10) >= 0.40
  DEMO1_NOISE_ENVELOPE_NARROW -- composed_acc(p=0.00) >= 0.80 AND composed_acc(p=0.10) < 0.40
  DEMO1_NOISE_KILL            -- composed_acc(p=0.00) < 0.80 (regression from capstone 1.000)

Pre-reg: preregs/2026-05-23_wave14_demo1_noise_envelope_v2.md
Queue: overnight_queue (GPU required; N=65536 CUDA)
Memory budget: peak ~61 MB VRAM (5 codebooks float32 at N=65536); well under 8 GB.
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
HARD_PASS_CLEAN = 0.80    # composed_acc at p=0.0 must hold (regression guard vs 1.000 capstone)
HARD_PASS_P10   = 0.40    # composed_acc at p=0.10 for PASS verdict


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"metrics missing required keys: {set(d.keys())}")


def compute_verdict(summary):
    """Verdict logic: PASS / NARROW / KILL based on composed_acc across noise cells."""
    if "acc_per_noise" not in summary:
        return ("DEMO1_NOISE_ENVELOPE_KILL", "Missing acc_per_noise in summary.")
    apn = summary["acc_per_noise"]
    clean = apn.get("0.00", apn.get("0.0", None))
    p10   = apn.get("0.10", None)
    if clean is None:
        return ("DEMO1_NOISE_ENVELOPE_KILL", "Clean baseline (p=0.00) missing from acc_per_noise.")
    if clean < HARD_PASS_CLEAN:
        return ("DEMO1_NOISE_KILL",
                f"KILL: clean composed_acc={clean:.3f} < {HARD_PASS_CLEAN} -- "
                f"regression from capstone 1.000. acc_per_noise={apn}.")
    if p10 is None:
        return ("DEMO1_NOISE_ENVELOPE_NARROW",
                f"NARROW (p=0.10 cell missing -- cannot confirm PASS). "
                f"clean={clean:.3f}. acc_per_noise={apn}.")
    if p10 >= HARD_PASS_P10:
        return ("DEMO1_NOISE_ENVELOPE_PASS",
                f"PASS: composed_acc at p=0.10 = {p10:.3f} >= {HARD_PASS_P10}; "
                f"clean={clean:.3f}. Demo 1 Lane D S->T->X envelope extends to "
                f"moderate inter-stage W noise. acc_per_noise={apn}.")
    return ("DEMO1_NOISE_ENVELOPE_NARROW",
            f"NARROW: composed_acc at p=0.10 = {p10:.3f} < {HARD_PASS_P10}; "
            f"clean={clean:.3f}. Noise degrades the pipeline between p=0.0 and p=0.10. "
            f"acc_per_noise={apn}.")


def self_test_verdict():
    cases = [
        # PASS: clean >= 0.80 and p10 >= 0.40
        ({"acc_per_noise": {"0.00": 1.000, "0.10": 0.60, "0.20": 0.30}}, "DEMO1_NOISE_ENVELOPE_PASS"),
        # NARROW: clean >= 0.80 but p10 < 0.40
        ({"acc_per_noise": {"0.00": 0.90, "0.10": 0.25, "0.20": 0.10}}, "DEMO1_NOISE_ENVELOPE_NARROW"),
        # KILL: clean < 0.80
        ({"acc_per_noise": {"0.00": 0.50, "0.10": 0.20}}, "DEMO1_NOISE_KILL"),
        # KILL: missing acc_per_noise
        ({}, "DEMO1_NOISE_ENVELOPE_KILL"),
        # NARROW: p10 cell missing but clean passes
        ({"acc_per_noise": {"0.00": 0.95}}, "DEMO1_NOISE_ENVELOPE_NARROW"),
        # PASS at threshold boundary
        ({"acc_per_noise": {"0.00": 0.80, "0.10": 0.40}}, "DEMO1_NOISE_ENVELOPE_PASS"),
        # KILL at clean boundary
        ({"acc_per_noise": {"0.00": 0.79, "0.10": 0.50}}, "DEMO1_NOISE_KILL"),
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: compute_verdict({s}) = {got!r}, expected {exp!r}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def flip_bits_bipolar(vec, p_flip, gen):
    """Bipolar bit-flip: each entry multiplied by -1 independently at probability p_flip."""
    if p_flip == 0.0:
        return vec
    mask = torch.rand(vec.shape, generator=gen, device=vec.device) < p_flip
    signs = torch.where(mask, torch.tensor(-1.0, device=vec.device),
                        torch.tensor(1.0, device=vec.device))
    return vec * signs


def run_one_trial(seed, p_flip, config, device):
    """Run S->T->X Demo 1 pipeline at N with inter-stage W bit-flip noise at rate p_flip.

    Noise is applied to B_q BETWEEN stages:
      - B_q_S : W seen by Stage S (pattern completion from working memory)
      - B_q_T : W seen by Stage T (hypothesis bundle scoring)
    Each is an independent draw: fresh random mask per stage transition.
    Stage X uses the hypothesis prediction from Stage T (no direct W read in X).
    """
    N = config["N"]
    K = config["K_hypotheses"]
    F = config["F_facts_per_hyp"]
    skill_len  = config["skill_len"]
    skill_alpha = config["skill_alphabet"]

    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)

    entity_atoms   = t.make_bsc_codebook(200,        N, gen, device)
    relation_atoms = t.make_bsc_codebook(20,         N, gen, device)
    hyp_atoms      = t.make_bsc_codebook(K,          N, gen, device)
    position_atoms = t.make_bsc_codebook(skill_len,  N, gen, device)
    skill_atoms    = t.make_bsc_codebook(skill_alpha, N, gen, device)

    hyp_signatures  = []
    hyp_skill_progs = []
    for k in range(K):
        sig_facts = [
            (int(torch.randint(0, 200, (1,), generator=cpu_gen)),
             int(torch.randint(0, 20,  (1,), generator=cpu_gen)),
             int(torch.randint(0, 200, (1,), generator=cpu_gen)))
            for _ in range(F)
        ]
        hyp_signatures.append(sig_facts)
        skill_indices = torch.randint(0, skill_alpha, (skill_len,),
                                      generator=cpu_gen).to(device)
        prog = t.sign_quantize(
            (skill_atoms[skill_indices] * position_atoms[:skill_len]).sum(dim=0))
        hyp_skill_progs.append((prog, skill_indices))

    true_k = int(torch.randint(0, K, (1,), generator=cpu_gen))

    # Stage U: EMA working-memory accumulation (clean -- noise applied after)
    decay = 0.95
    B = torch.zeros(N, device=device)
    obs_stream = hyp_signatures[true_k] + [
        (int(torch.randint(0, 200, (1,), generator=cpu_gen)),
         int(torch.randint(0, 20,  (1,), generator=cpu_gen)),
         int(torch.randint(0, 200, (1,), generator=cpu_gen)))
        for _ in range(5)
    ]
    for s, r, o in obs_stream:
        triple = (entity_atoms[s] * relation_atoms[r] * entity_atoms[o]).float()
        B = decay * B + triple
    B_q = t.sign_quantize(B)   # clean W

    # Apply inter-stage noise to W before Stage S
    B_q_S = flip_bits_bipolar(B_q, p_flip, gen)

    # Stage S: VAMP-class pattern completion from noisy W
    probe_fact = hyp_signatures[true_k][-1]
    s_p, r_p, o_p = probe_fact
    s_probe = B_q_S * entity_atoms[s_p] * relation_atoms[r_p]
    sims = entity_atoms @ s_probe
    w = torch.softmax(sims, dim=0)
    soft_state = (w.unsqueeze(1) * entity_atoms).sum(dim=0)
    s_pred_o = int((entity_atoms @ t.sign_quantize(soft_state)).argmax().item())
    s_correct = int(s_pred_o == o_p)

    # Apply inter-stage noise to W before Stage T (independent draw)
    B_q_T = flip_bits_bipolar(B_q, p_flip, gen)

    # Stage T: hypothesis bundle scoring against noisy W
    M_T = t.sign_quantize(torch.stack([
        hyp_atoms[k] * t.sign_quantize(
            torch.stack([
                t.sign_quantize(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
                for s, r, o in facts
            ], dim=0).sum(dim=0))
        for k, facts in enumerate(hyp_signatures)
    ], dim=0).sum(dim=0))
    hyp_scores = [float((M_T * hyp_atoms[k] * B_q_T).sum()) for k in range(K)]
    pred_k = int(max(range(K), key=lambda k: hyp_scores[k]))
    t_correct = int(pred_k == true_k)

    # Stage X: skill program decode from predicted hypothesis (no W read; no extra noise)
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
        "noise_axis": "inter_stage_W_bitflip",
        "device": str(device),
        "note": "Demo 1 Lane D S->T->X N=65536 noise envelope v2; W noise between stages",
    }

    print(f"Demo1 noise envelope v2: N={config['N']} device={device} "
          f"seeds={config['seeds']} noise_levels={noise_levels}", flush=True)

    acc_per_noise = {}
    for p in noise_levels:
        results = []
        for seed in config["seeds"]:
            for trial in range(config["n_trials_per_noise_per_seed"]):
                r = run_one_trial(seed * 10000 + trial, p, config, device)
                results.append(r)
        n = len(results)
        c_acc = sum(r["composed"]  for r in results) / n
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
    out_dir = get_output_dir("wave14_demo1_noise_envelope_v2_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    clean = summary["acc_per_noise"].get("0.00", summary["acc_per_noise"].get("0.0", 0.0))
    oracle.assert_baseline_high("clean_composed_acc", clean, 0.10)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_demo1_noise_envelope_v2")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke",     action="store_true")
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
