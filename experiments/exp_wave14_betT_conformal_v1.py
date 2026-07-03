"""Bet T Rescue #3: class-wise (Mondrian) conformal wrapper over hypothesis distribution.

Research rescue ranking (notes/research_betT_rescue_sketches_2026-05-23.md):
  Rank 1: per-hypothesis TEMPSCALE -> KILL (wave14_betT_per_hyp_tempscale_v1)
  Rank 2: conformal class-wise wrapper (this experiment), P_deflated=0.40

Premise: cycle 101 Bet T PARTIAL shows min_acc=0.689 across K_hyp=8 hypotheses.
TEMPSCALE KILL (BET_T_TEMPSCALE_KILL: best_min_acc=0.344 < 0.70) rules out
calibration as the issue. The conformal approach does not improve the argmax
accuracy but instead provides COVERAGE guarantees: for each hypothesis h, the
prediction set contains the true object with probability >= 1-alpha.

Class-wise (Mondrian) conformal:
  For each hypothesis h, build a conformal calibration set from seed-split.
  Compute nonconformity scores (1 - softmax_prob_of_true_label) on calibration.
  At test time: return prediction set = {labels with nonconf score <= quantile}.
  Coverage check: fraction of test points where true label in set >= 1-alpha.
  Informativeness check: mean prediction-set size <= K_hyp / 2 = 4.

HARD PASS (Research pre-reg, per research_betT_rescue_sketches_2026-05-23.md):
  - Per-hypothesis coverage in [0.85, 0.95] across ALL K_hyp hypotheses, 3 seeds.
  - Mean prediction-set size <= K_hyp / 2 = 4.0 (informativeness gate).

HARD FAIL:
  - ANY hypothesis has coverage outside [0.80, 0.99].
  - Mean prediction-set size > K_hyp / 2 (degenerated to uninformative sets).

Verdict labels:
  BET_T_CONFORMAL_PASS    -- HARD PASS criteria met
  BET_T_CONFORMAL_PARTIAL -- coverage in bounds but prediction sets too large
  BET_T_CONFORMAL_KILL    -- coverage out of bounds in any hypothesis
  BET_T_CONFORMAL_INCONCLUSIVE

Pure CPU. No GPU required. ~10 min at N=4096.
Memory budget: W not materialized explicitly; codebook N=4096 x 200 float32 = 3.2 MB.
  Peak: ~20 MB total (multiple codebooks). Well within any CPU budget.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# Pre-reg thresholds (Research sketch #3 hard pass/fail)
COV_LOW = 0.80    # absolute floor; coverage below this = KILL
COV_HIGH = 0.99   # absolute ceiling; over-coverage (trivial sets)
COV_TARGET_LOW = 0.85   # target range low
COV_TARGET_HIGH = 0.95  # target range high (tight calibration)
ALPHA = 0.10      # target error rate -> target coverage = 0.90
SET_SIZE_LIMIT_FACTOR = 0.5  # max mean set size = K_hyp * factor


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing metrics keys: {set(d.keys())}")


def compute_verdict(summary):
    if "per_hyp_coverage" not in summary:
        return ("BET_T_CONFORMAL_INCONCLUSIVE", "Missing per_hyp_coverage.")
    covs = summary["per_hyp_coverage"]
    mean_set_size = summary.get("mean_set_size", None)
    K_hyp = summary.get("K_hyp", 8)
    set_size_limit = K_hyp * SET_SIZE_LIMIT_FACTOR

    # Check per-hypothesis coverage bounds
    any_below_floor = any(c < COV_LOW for c in covs.values())
    any_above_ceil = any(c > COV_HIGH for c in covs.values())
    all_in_target = all(COV_TARGET_LOW <= c <= COV_TARGET_HIGH for c in covs.values())

    if any_below_floor or any_above_ceil:
        bad = {h: c for h, c in covs.items() if c < COV_LOW or c > COV_HIGH}
        return ("BET_T_CONFORMAL_KILL",
                f"HARD FAIL: coverage out of [{COV_LOW}, {COV_HIGH}] for "
                f"{len(bad)}/{len(covs)} hypotheses: {bad}. "
                f"Class-wise conformal does not cover Bet T. "
                f"mean_set_size={mean_set_size:.2f}.")

    if mean_set_size is not None and mean_set_size > set_size_limit:
        return ("BET_T_CONFORMAL_PARTIAL",
                f"Coverage in bounds but prediction sets too large: "
                f"mean_set_size={mean_set_size:.2f} > limit={set_size_limit:.1f} "
                f"(K_hyp={K_hyp}). Conformal covers but is uninformative. "
                f"per_hyp_coverage={covs}.")

    if not all_in_target:
        off = {h: c for h, c in covs.items()
               if not (COV_TARGET_LOW <= c <= COV_TARGET_HIGH)}
        return ("BET_T_CONFORMAL_PARTIAL",
                f"Coverage in hard bounds but outside target [{COV_TARGET_LOW}, "
                f"{COV_TARGET_HIGH}] for {len(off)}/{len(covs)} hypotheses: {off}. "
                f"mean_set_size={mean_set_size:.2f}.")

    return ("BET_T_CONFORMAL_PASS",
            f"HARD PASS: all {len(covs)} hypotheses have coverage in "
            f"[{COV_TARGET_LOW}, {COV_TARGET_HIGH}]; mean_set_size={mean_set_size:.2f} "
            f"<= {set_size_limit:.1f}. Class-wise conformal rescues Bet T coverage. "
            f"per_hyp_coverage={covs}.")


def self_test_verdict():
    cases = [
        # All in target, small sets -> PASS
        ({"per_hyp_coverage": {str(k): 0.90 for k in range(8)},
          "mean_set_size": 2.0, "K_hyp": 8},
         "BET_T_CONFORMAL_PASS"),
        # Coverage OK but sets too large -> PARTIAL
        ({"per_hyp_coverage": {str(k): 0.90 for k in range(8)},
          "mean_set_size": 5.0, "K_hyp": 8},
         "BET_T_CONFORMAL_PARTIAL"),
        # Some coverage below floor -> KILL
        ({"per_hyp_coverage": {"0": 0.75, "1": 0.90, "2": 0.90},
          "mean_set_size": 2.0, "K_hyp": 3},
         "BET_T_CONFORMAL_KILL"),
        # Missing per_hyp_coverage -> INCONCLUSIVE
        ({}, "BET_T_CONFORMAL_INCONCLUSIVE"),
        # Coverage in hard bounds but below target (0.82 < 0.85) -> PARTIAL
        ({"per_hyp_coverage": {"0": 0.82, "1": 0.90, "2": 0.90},
          "mean_set_size": 2.0, "K_hyp": 3},
         "BET_T_CONFORMAL_PARTIAL"),
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: compute_verdict -> {got}, expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def sign_q(x):
    s = torch.sign(x)
    s[s == 0] = 1.0
    return s


def make_bsc_codebook(n, N, gen, device):
    b = (torch.rand(n, N, generator=gen, device=device) > 0.5).float()
    return 2.0 * b - 1.0


def softmax_probs(scores, beta):
    """Softmax distribution over entity scores. Returns prob vector."""
    logits = beta * scores - (beta * scores).max()
    e = logits.exp()
    return e / e.sum()


def run_one_seed(seed, config, device):
    """Run Bet T conformal for one seed.

    Returns: dict with calibration_data and test_data per hypothesis.
    Each hypothesis has a list of (nonconf_score, true_label, pred_set_sizes) tuples.
    """
    N = config["N"]
    K_hyp = config["n_hypotheses"]
    n_facts = config["n_facts_per_hyp"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    beta = config["beta"]
    n_cal = config["n_cal_per_hyp"]  # calibration queries per hypothesis
    n_test = config["n_test_per_hyp"]  # test queries per hypothesis

    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = make_bsc_codebook(num_relations, N, gen, device)
    hyp_atoms = make_bsc_codebook(K_hyp, N, gen, device)

    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    hyp_facts = []
    for _ in range(K_hyp):
        facts = []
        for _ in range(n_facts):
            s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
            r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
            o = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
            facts.append((s, r, o))
        hyp_facts.append(facts)

    # Build joint memory matrix M
    triples_per_hyp = []
    for k, facts in enumerate(hyp_facts):
        triples = [sign_q(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
                   for s, r, o in facts]
        bundle_k = sign_q(torch.stack(triples, dim=0).sum(dim=0))
        triples_per_hyp.append(hyp_atoms[k] * bundle_k)
    M_joint = sign_q(torch.stack(triples_per_hyp, dim=0).sum(dim=0))

    # For each hypothesis, compute nonconformity scores (1 - prob_of_true)
    # on calibration split, then coverage on test split.
    cal_scores_per_hyp = {}   # hyp_k -> list of nonconf scores (for calibration)
    test_in_set_per_hyp = {}  # hyp_k -> list of (in_set, set_size)
    q_gen = torch.Generator().manual_seed(seed + 777)

    for k, facts in enumerate(hyp_facts):
        cal_scores = []
        for _ in range(n_cal):
            # Pick a random fact from this hypothesis as query
            fi = int(torch.randint(0, n_facts, (1,), generator=q_gen))
            s, r, o_true = facts[fi]
            probe = M_joint * hyp_atoms[k] * entity_atoms[s] * relation_atoms[r]
            scores = entity_atoms @ probe  # (num_entities,)
            probs = softmax_probs(scores, beta)
            nonconf = float(1.0 - probs[o_true].item())
            cal_scores.append(nonconf)
        cal_scores_per_hyp[k] = sorted(cal_scores)

    # Conformal quantile: (ceil((n_cal+1)*(1-alpha)) / n_cal) quantile
    n_cal_actual = len(cal_scores_per_hyp[0])
    alpha_level = ALPHA
    # Use (n_cal+1)*(1-alpha)/n_cal as the effective quantile index
    q_idx = min(int((n_cal_actual + 1) * (1.0 - alpha_level)), n_cal_actual - 1)

    test_results = {}
    set_sizes = []
    for k, facts in enumerate(hyp_facts):
        quantile = cal_scores_per_hyp[k][q_idx]
        in_set_count = 0
        for _ in range(n_test):
            fi = int(torch.randint(0, n_facts, (1,), generator=q_gen))
            s, r, o_true = facts[fi]
            probe = M_joint * hyp_atoms[k] * entity_atoms[s] * relation_atoms[r]
            scores = entity_atoms @ probe
            probs = softmax_probs(scores, beta)
            # Prediction set: all labels with nonconf score <= quantile
            nonconf_all = (1.0 - probs).tolist()
            pred_set = [i for i, nc in enumerate(nonconf_all) if nc <= quantile]
            set_sizes.append(len(pred_set))
            if o_true in pred_set:
                in_set_count += 1
        test_results[k] = {
            "coverage": in_set_count / n_test,
            "quantile": quantile,
        }

    return {
        "per_hyp_results": test_results,
        "mean_set_size": sum(set_sizes) / len(set_sizes),
    }


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # CPU-only
    config = {
        "N": 512 if smoke else 4096,
        "num_entities": 30 if smoke else 200,
        "num_relations": 4 if smoke else 20,
        "n_hypotheses": 3 if smoke else 8,
        "n_facts_per_hyp": 5 if smoke else 30,
        "n_cal_per_hyp": 10 if smoke else 80,   # calibration queries per hyp
        "n_test_per_hyp": 10 if smoke else 120,  # test queries per hyp
        "beta": 8,                               # beta=c/N=8 at N=4096 (optimal from betT research)
        "seeds": [17] if smoke else [17, 23, 31],
        "alpha": ALPHA,
        "device": "cpu",
        "note": "Bet T Rescue #3: class-wise Mondrian conformal; alpha=0.10; K_hyp=8",
    }
    K_hyp = config["n_hypotheses"]

    print(f"Bet T conformal: N={config['N']} K_hyp={K_hyp} "
          f"seeds={config['seeds']} alpha={ALPHA}", flush=True)

    all_coverages = {k: [] for k in range(K_hyp)}
    all_set_sizes = []

    for seed in config["seeds"]:
        result = run_one_seed(seed, config, device)
        seed_mean_size = result["mean_set_size"]
        all_set_sizes.append(seed_mean_size)
        for k, res in result["per_hyp_results"].items():
            all_coverages[k].append(res["coverage"])
        covs = {k: f"{v['coverage']:.3f}" for k, v in result["per_hyp_results"].items()}
        print(f"  seed={seed}: coverage={covs} mean_set_size={seed_mean_size:.2f}",
              flush=True)

    # Average across seeds
    mean_coverage_per_hyp = {
        str(k): sum(all_coverages[k]) / len(all_coverages[k])
        for k in range(K_hyp)
    }
    mean_set_size_overall = sum(all_set_sizes) / len(all_set_sizes)

    summary = {
        "per_hyp_coverage": mean_coverage_per_hyp,
        "mean_set_size": mean_set_size_overall,
        "K_hyp": K_hyp,
        "alpha": ALPHA,
        "target_coverage": 1.0 - ALPHA,
        "set_size_limit": K_hyp * SET_SIZE_LIMIT_FACTOR,
        "note": "Bet T Rescue #3: Mondrian conformal class-wise coverage check",
    }

    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\n  Mean coverage per hyp: {mean_coverage_per_hyp}", flush=True)
    print(f"  Mean set size: {mean_set_size_overall:.2f}", flush=True)
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
    out_dir = get_output_dir("wave14_betT_conformal_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Structural check: per_hyp_coverage must have K_hyp entries
    K_hyp = config["n_hypotheses"]
    assert len(summary["per_hyp_coverage"]) == K_hyp, (
        f"Expected {K_hyp} coverage entries, got {len(summary['per_hyp_coverage'])}")
    assert summary["mean_set_size"] > 0, "mean_set_size must be positive"
    oracle.assert_baseline_high("set_size_positive", summary["mean_set_size"], 0.5)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betT_conformal_v1")
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
