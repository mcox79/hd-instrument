"""Bet T Mondrian conformal stratified by anti-RM(1,16) coset (final close-or-rescue).

Strategy x Research shore-up matrix Weakness #2 (MEDIUM).
Premise: Bet T PARTIAL min_acc=0.689 at cycle 101 has stayed stale 67 cap_map
versions. The original conformal rescue used hypothesis-class as stratifier and
returned PARTIAL. Two rescues exhausted at FULL (TEMPSCALE per-hyp KILLED v158;
Mondrian-by-hypothesis queued but never ran). Per the v152 RM(1,16) refutation
the natural stratification basis is REFUTED; per meta-map Drill 3 the anti-coset
(complement of the Kerdock support in RM-subcode space) is the substrate-novel
stratifier never tested. P_deflated=0.40 per research field-coverage.

Construction:
  1. Same hypothesis-tracking pipeline as betT_conformal_v1: K_hyp=8 hypotheses,
     soft-bound triples in a joint memory; cleanup returns softmax probs.
  2. For each (hyp, query) pair compute an anti-RM coset signature: the codeword
     formed by binding the (subject, relation) probe is projected against the
     m+1=11 generators of RM(1,m=10) where N=1024, and the residual sign-pattern
     defines an anti-coset class in 2^{m+1}=2048 (we COARSEN to 4 cosets at the
     top order-1 Reed-Muller block to match the Kerdock 4-coset frame).
  3. Per-coset Mondrian conformal: independent calibration quantile for each of
     4 anti-coset classes; coverage check stratified by class.

HARD PASS:
  - Per-coset coverage in [0.85, 0.95] for all 4 anti-RM cosets at FULL config
    (N=1024 K_hyp=8 5 seeds).
  - Mean prediction-set size <= K_hyp / 2 = 4.

HARD FAIL:
  - Coverage outside [0.80, 0.99] for ANY of the 4 cosets, OR
  - mean_set_size > K_hyp = 8 (degenerated).
  Either outcome closes Bet T as Mondrian-rescue-exhausted.

Verdict labels:
  BETT_MONDRIAN_ANTI_RM_PASS       — HARD PASS criteria met
  BETT_MONDRIAN_ANTI_RM_PARTIAL    — coverage in hard bounds but outside target
  BETT_MONDRIAN_ANTI_RM_FAIL       — HARD FAIL; Bet T closes per PROT-004/006
  BETT_MONDRIAN_ANTI_RM_INCONCLUSIVE

Pure CPU. ~10 min at N=1024 K_hyp=8 5 seeds.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, math, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

COV_LOW = 0.80
COV_HIGH = 0.99
COV_TARGET_LOW = 0.85
COV_TARGET_HIGH = 0.95
ALPHA = 0.10
SET_SIZE_LIMIT_FACTOR = 0.5
N_COSETS = 4  # anti-RM coarsening at the order-1 block (matches Kerdock 4-coset frame)


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing metrics keys: {set(d.keys())}")


def compute_verdict(summary):
    if "per_coset_coverage" not in summary:
        return ("BETT_MONDRIAN_ANTI_RM_INCONCLUSIVE", "Missing per_coset_coverage.")
    covs = summary["per_coset_coverage"]
    mean_set_size = summary.get("mean_set_size", None)
    K_hyp = summary.get("K_hyp", 8)
    set_size_limit = K_hyp * SET_SIZE_LIMIT_FACTOR
    hard_size_limit = float(K_hyp)

    if not covs:
        return ("BETT_MONDRIAN_ANTI_RM_INCONCLUSIVE", "No cosets reported.")

    cov_vals = list(covs.values())
    any_below_floor = any(c < COV_LOW for c in cov_vals)
    any_above_ceil = any(c > COV_HIGH for c in cov_vals)

    if any_below_floor or any_above_ceil:
        bad = {k: c for k, c in covs.items() if c < COV_LOW or c > COV_HIGH}
        return ("BETT_MONDRIAN_ANTI_RM_FAIL",
                f"HARD FAIL: per-coset coverage out of [{COV_LOW}, {COV_HIGH}] for "
                f"{len(bad)}/{len(covs)} anti-RM cosets: {bad}. "
                f"Mondrian on anti-RM coset does NOT rescue Bet T. "
                f"Bet T closes per PROT-004/006 — Mondrian rescue exhausted.")

    if mean_set_size is not None and mean_set_size > hard_size_limit:
        return ("BETT_MONDRIAN_ANTI_RM_FAIL",
                f"HARD FAIL: mean_set_size={mean_set_size:.2f} > K_hyp={hard_size_limit:.1f} "
                f"(degenerate sets). Conformal degenerated; Mondrian rescue exhausted.")

    all_in_target = all(COV_TARGET_LOW <= c <= COV_TARGET_HIGH for c in cov_vals)
    if mean_set_size is not None and mean_set_size > set_size_limit:
        return ("BETT_MONDRIAN_ANTI_RM_PARTIAL",
                f"Coverage in [{COV_LOW}, {COV_HIGH}] but mean_set_size="
                f"{mean_set_size:.2f} > target limit {set_size_limit:.1f}. "
                f"Mondrian covers but is uninformative.")

    if not all_in_target:
        off = {k: c for k, c in covs.items()
               if not (COV_TARGET_LOW <= c <= COV_TARGET_HIGH)}
        return ("BETT_MONDRIAN_ANTI_RM_PARTIAL",
                f"Coverage in hard bounds but outside target [{COV_TARGET_LOW}, "
                f"{COV_TARGET_HIGH}] for {len(off)}/{len(covs)} cosets: {off}.")

    return ("BETT_MONDRIAN_ANTI_RM_PASS",
            f"HARD PASS: all {len(covs)} anti-RM cosets have coverage in "
            f"[{COV_TARGET_LOW}, {COV_TARGET_HIGH}]; mean_set_size="
            f"{mean_set_size:.2f} <= {set_size_limit:.1f}. "
            f"Anti-RM Mondrian conformal RESCUES Bet T. per_coset_coverage={covs}.")


def self_test_verdict():
    cases = [
        # All target, sets small -> PASS
        ({"per_coset_coverage": {str(k): 0.90 for k in range(4)},
          "mean_set_size": 2.0, "K_hyp": 8},
         "BETT_MONDRIAN_ANTI_RM_PASS"),
        # One coset below floor -> FAIL
        ({"per_coset_coverage": {"0": 0.70, "1": 0.90, "2": 0.90, "3": 0.90},
          "mean_set_size": 2.0, "K_hyp": 8},
         "BETT_MONDRIAN_ANTI_RM_FAIL"),
        # Sets too large -> PARTIAL
        ({"per_coset_coverage": {str(k): 0.90 for k in range(4)},
          "mean_set_size": 5.0, "K_hyp": 8},
         "BETT_MONDRIAN_ANTI_RM_PARTIAL"),
        # Sets way too large -> FAIL via hard size limit
        ({"per_coset_coverage": {str(k): 0.90 for k in range(4)},
          "mean_set_size": 8.5, "K_hyp": 8},
         "BETT_MONDRIAN_ANTI_RM_FAIL"),
        # Coverage in hard bounds but one below target -> PARTIAL
        ({"per_coset_coverage": {"0": 0.82, "1": 0.90, "2": 0.90, "3": 0.90},
          "mean_set_size": 2.0, "K_hyp": 8},
         "BETT_MONDRIAN_ANTI_RM_PARTIAL"),
        ({}, "BETT_MONDRIAN_ANTI_RM_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: got {got} expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# anti-RM(1, m) coset classification at the order-1 block
# ---------------------------------------------------------------------------

def sylvester_hadamard_rows(n_log2):
    """Return rows of Sylvester Hadamard H_{2^n_log2} as a (2^n, 2^n) numpy int8 tensor in {+1,-1}."""
    import numpy as np
    H = np.array([[1]], dtype=np.int8)
    for _ in range(n_log2):
        H = np.block([[H, H], [H, -H]])
    return H


def coset_signature(query_bipolar, hadamard_rows_2gen):
    """Project the query against the first 2 RM(1,m) generators to define an anti-coset class.

    RM(1, m) has 2*N codewords organised as Hadamard rows union their negations.
    The anti-coset structure at order 1 splits codewords into 4 classes by the
    SIGN PAIR (sign<query, h_1>, sign<query, h_2>) where h_1, h_2 are the
    second and third Hadamard rows (skipping the all-ones row which carries no
    coset info). The result is an integer in {0, 1, 2, 3} indexing the 4-coset
    coarsening — this matches the Kerdock 4-coset frame and is independent of
    the hypothesis-class index (per Drill 3, the anti-coset is exactly the
    stratifier the v158 attempt did NOT use).
    """
    import numpy as np
    s1 = int(np.sign(np.dot(query_bipolar, hadamard_rows_2gen[0])))
    s2 = int(np.sign(np.dot(query_bipolar, hadamard_rows_2gen[1])))
    s1 = 1 if s1 >= 0 else -1
    s2 = 1 if s2 >= 0 else -1
    # Pack (s1, s2) into {0,1,2,3}
    b1 = 0 if s1 > 0 else 1
    b2 = 0 if s2 > 0 else 1
    return b1 * 2 + b2


def sign_q(x):
    s = torch.sign(x)
    s[s == 0] = 1.0
    return s


def make_bsc_codebook(n, N, gen, device):
    b = (torch.rand(n, N, generator=gen, device=device) > 0.5).float()
    return 2.0 * b - 1.0


def softmax_probs(scores, beta):
    logits = beta * scores - (beta * scores).max()
    e = logits.exp()
    return e / e.sum()


def run_one_seed(seed, config, device):
    import numpy as np
    N = config["N"]
    K_hyp = config["n_hypotheses"]
    n_facts = config["n_facts_per_hyp"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    beta = config["beta"]
    n_cal = config["n_cal_per_hyp"]
    n_test = config["n_test_per_hyp"]

    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = make_bsc_codebook(num_relations, N, gen, device)
    hyp_atoms = make_bsc_codebook(K_hyp, N, gen, device)

    # Hadamard generators for anti-RM coset signature (N must be power of 2)
    n_log2 = int(round(math.log2(N)))
    H = sylvester_hadamard_rows(n_log2)
    # Use rows 1, 2 (the two lowest non-trivial generators)
    hadamard_2gen = H[1:3].astype(np.float32)

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

    triples_per_hyp = []
    for k, facts in enumerate(hyp_facts):
        triples = [sign_q(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
                   for s, r, o in facts]
        bundle_k = sign_q(torch.stack(triples, dim=0).sum(dim=0))
        triples_per_hyp.append(hyp_atoms[k] * bundle_k)
    M_joint = sign_q(torch.stack(triples_per_hyp, dim=0).sum(dim=0))

    # Mondrian calibration BY ANTI-RM COSET (not by hypothesis)
    cal_scores_per_coset = {c: [] for c in range(N_COSETS)}
    test_records = []
    q_gen = torch.Generator().manual_seed(seed + 777)

    # CALIBRATION
    for k, facts in enumerate(hyp_facts):
        for _ in range(n_cal):
            fi = int(torch.randint(0, n_facts, (1,), generator=q_gen))
            s, r, o_true = facts[fi]
            probe = M_joint * hyp_atoms[k] * entity_atoms[s] * relation_atoms[r]
            probe_np = probe.cpu().numpy().astype('float32')
            coset = coset_signature(probe_np, hadamard_2gen)
            scores = entity_atoms @ probe
            probs = softmax_probs(scores, beta)
            nonconf = float(1.0 - probs[o_true].item())
            cal_scores_per_coset[coset].append(nonconf)

    # Compute per-coset quantile
    per_coset_quantile = {}
    for c, lst in cal_scores_per_coset.items():
        if len(lst) == 0:
            per_coset_quantile[c] = 1.0  # all in set (no calibration in this coset)
            continue
        sorted_s = sorted(lst)
        n = len(sorted_s)
        q_idx = min(int((n + 1) * (1.0 - ALPHA)), n - 1)
        per_coset_quantile[c] = sorted_s[q_idx]

    # TEST
    cosets_test_in_set = {c: [0, 0] for c in range(N_COSETS)}  # [in_set, total]
    all_set_sizes = []
    for k, facts in enumerate(hyp_facts):
        for _ in range(n_test):
            fi = int(torch.randint(0, n_facts, (1,), generator=q_gen))
            s, r, o_true = facts[fi]
            probe = M_joint * hyp_atoms[k] * entity_atoms[s] * relation_atoms[r]
            probe_np = probe.cpu().numpy().astype('float32')
            coset = coset_signature(probe_np, hadamard_2gen)
            quantile = per_coset_quantile[coset]
            scores = entity_atoms @ probe
            probs = softmax_probs(scores, beta)
            nonconf_all = (1.0 - probs).tolist()
            pred_set = [i for i, nc in enumerate(nonconf_all) if nc <= quantile]
            all_set_sizes.append(len(pred_set))
            cosets_test_in_set[coset][1] += 1
            if o_true in pred_set:
                cosets_test_in_set[coset][0] += 1

    per_coset_coverage = {}
    per_coset_count = {}
    for c, (in_set, total) in cosets_test_in_set.items():
        per_coset_count[str(c)] = total
        per_coset_coverage[str(c)] = (in_set / total) if total > 0 else 1.0

    return {
        "per_coset_coverage": per_coset_coverage,
        "per_coset_count": per_coset_count,
        "mean_set_size": sum(all_set_sizes) / max(1, len(all_set_sizes)),
        "per_coset_quantile": {str(c): float(q) for c, q in per_coset_quantile.items()},
    }


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")
    config = {
        "N": 512 if smoke else 1024,
        "num_entities": 30 if smoke else 200,
        "num_relations": 4 if smoke else 20,
        "n_hypotheses": 3 if smoke else 8,
        "n_facts_per_hyp": 5 if smoke else 30,
        "n_cal_per_hyp": 10 if smoke else 80,
        "n_test_per_hyp": 10 if smoke else 120,
        "beta": 8,
        "seeds": [17] if smoke else [17, 23, 31, 37, 41],
        "alpha": ALPHA,
        "n_cosets": N_COSETS,
        "device": "cpu",
        "note": ("Bet T Mondrian conformal stratified by anti-RM(1,m) coset; final "
                 "close-or-rescue per Strategy x Research shore-up matrix Weakness #2."),
    }
    K_hyp = config["n_hypotheses"]
    print(f"Bet T anti-RM Mondrian: N={config['N']} K_hyp={K_hyp} "
          f"seeds={config['seeds']} alpha={ALPHA} n_cosets={N_COSETS}", flush=True)

    all_cov_per_coset = {c: [] for c in range(N_COSETS)}
    all_set_sizes = []
    seed_records = {}

    for seed in config["seeds"]:
        res = run_one_seed(seed, config, device)
        seed_records[str(seed)] = res
        all_set_sizes.append(res["mean_set_size"])
        for c in range(N_COSETS):
            all_cov_per_coset[c].append(res["per_coset_coverage"][str(c)])
        print(f"  seed={seed}: cov_per_coset="
              + ", ".join(f"c{c}={res['per_coset_coverage'][str(c)]:.3f}"
                          for c in range(N_COSETS))
              + f" mean_set_size={res['mean_set_size']:.2f}",
              flush=True)

    per_coset_coverage = {
        str(c): sum(all_cov_per_coset[c]) / len(all_cov_per_coset[c])
        for c in range(N_COSETS)
    }
    mean_set_size = sum(all_set_sizes) / len(all_set_sizes)

    summary = {
        "per_coset_coverage": per_coset_coverage,
        "mean_set_size": mean_set_size,
        "K_hyp": K_hyp,
        "alpha": ALPHA,
        "n_cosets": N_COSETS,
        "seed_records": seed_records,
        "note": "Mondrian conformal stratified by anti-RM(1,m) coset at order-1 block",
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nMean per-coset coverage: {per_coset_coverage}", flush=True)
    print(f"Mean set size: {mean_set_size:.2f}", flush=True)
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
    self_test_verdict()
    out_dir = get_output_dir("wave14_betT_mondrian_anti_RM_conformal_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    assert len(s["per_coset_coverage"]) == N_COSETS, (
        f"Expected {N_COSETS} cosets, got {len(s['per_coset_coverage'])}")
    assert s["mean_set_size"] > 0
    oracle.assert_baseline_high("coset_count", float(len(s["per_coset_coverage"])), 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    self_test_verdict()
    out_dir = get_output_dir("wave14_betT_mondrian_anti_RM_conformal_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


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
