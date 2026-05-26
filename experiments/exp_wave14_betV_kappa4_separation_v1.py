"""Bet V kappa_4 separation probe — final close-or-reject (substrate-novel higher-cumulant signature).

Strategy x Research shore-up matrix Weakness #3 (MEDIUM-LOW).
Premise: Bet V PARTIAL gap=0.424 at largeN cycle 103, stale 65 cap_map versions.
Original Bet V used SECOND-MOMENT cosine confidence (sim_max - sim_2nd). The v167
KAPPA_PROFILE_GROWS finding shows the substrate's higher cumulants carry
algebraic structure invisible to mean / variance metrics. Per the matrix, kappa_4
of the stored-vs-unstored confidence distribution may discriminate where the
gap (second moment) fails.

Per [[feedback-no-smoke]] this is honest closure-or-rescue: P(rescue) <= 0.25
because (i) Bet V framing is structurally inconsistent with a self-reflective
claim at gap=0.424, and (ii) kappa_4 is novel but unmotivated by prior Bet V
findings — the test is whether the substrate's higher-cumulant signal CARRIES
the self-reflective separation that the second-moment failed to surface.

Construction:
  1. Re-run the Bet V pipeline (stored/unstored confidence) at largeN N=4096.
  2. For each (stored, unstored) split, accumulate per-probe confidence samples
     across ALL probes (not just the mean): we now look at the FULL distribution.
  3. Compute classical kappa_4 (excess kurtosis k_4 = mu_4/sigma^4 - 3) of
     stored-probe confidences and unstored-probe confidences separately.
  4. Standard-deviation difference: kappa4_separation = (k4_stored - k4_unstored)
     / sqrt(var_k4_stored + var_k4_unstored) (jackknife SE estimate, 5 seeds).

HARD PASS:
  - |kappa4_separation| >= 2.0 SD (5-seed jackknife SE) AND
  - kappa4_stored consistent in sign across all 5 seeds.
  -> Bet V rescued via higher-cumulant signature.

HARD FAIL:
  - |kappa4_separation| < 1.0 SD.
  -> Bet V closes per PROT-004/006 (final rescue tried).
  -> Filed in summary: (a) re-axiomatize as downstream conformal calibration,
     (b) absorb into v166 codeword-overlap KS-test row, (c) deprecate.

Verdict labels:
  BETV_KAPPA4_RESCUE_PASS    — |sep| >= 2.0 SD + sign-consistent across seeds
  BETV_KAPPA4_RESCUE_PARTIAL — 1.0 <= |sep| < 2.0 SD
  BETV_KAPPA4_RESCUE_FAIL    — |sep| < 1.0 SD; Bet V closes
  BETV_KAPPA4_RESCUE_INCONCLUSIVE

Pure CPU. ~10 min at N=4096 5 seeds. Pattern 7 cross-family consistency check.
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
from verification import oracle  # noqa: E402

HARD_PASS_SEP_SD = 2.0
HARD_FAIL_SEP_SD = 1.0


def get_output_dir(name):
    n = os.environ.get("HDLAB_EXP_NAME", name)
    out = REPO / "data" / f"exp_{n}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing metrics keys: {set(d.keys())}")


def compute_verdict(summary):
    if "kappa4_separation_sd" not in summary:
        return ("BETV_KAPPA4_RESCUE_INCONCLUSIVE", "Missing kappa4_separation_sd.")
    sep_sd = abs(summary["kappa4_separation_sd"])
    sign_consistent = summary.get("sign_consistent_across_seeds", False)
    k4_stored_mean = summary.get("kappa4_stored_mean", 0.0)
    k4_unstored_mean = summary.get("kappa4_unstored_mean", 0.0)

    if sep_sd >= HARD_PASS_SEP_SD and sign_consistent:
        return ("BETV_KAPPA4_RESCUE_PASS",
                f"HARD PASS: |kappa4_sep|={sep_sd:.2f} SD >= {HARD_PASS_SEP_SD} and "
                f"sign-consistent across seeds. kappa4_stored={k4_stored_mean:.3f}, "
                f"kappa4_unstored={k4_unstored_mean:.3f}. Bet V RESCUED via higher-"
                f"cumulant signature; the second-moment gap was metric-deficient.")
    if sep_sd < HARD_FAIL_SEP_SD:
        return ("BETV_KAPPA4_RESCUE_FAIL",
                f"HARD FAIL: |kappa4_sep|={sep_sd:.2f} SD < {HARD_FAIL_SEP_SD}. "
                f"kappa4_stored={k4_stored_mean:.3f}, kappa4_unstored="
                f"{k4_unstored_mean:.3f}. Bet V closes per PROT-004/006 — final rescue "
                f"tried. Filed sketches: (a) downstream conformal, (b) absorb into "
                f"v166 codeword-overlap KS-test row, (c) deprecate.")
    return ("BETV_KAPPA4_RESCUE_PARTIAL",
            f"Partial: |kappa4_sep|={sep_sd:.2f} SD in [{HARD_FAIL_SEP_SD}, "
            f"{HARD_PASS_SEP_SD}); sign_consistent={sign_consistent}. "
            f"kappa4_stored={k4_stored_mean:.3f}, unstored={k4_unstored_mean:.3f}. "
            f"Signal present but not strong enough for portfolio rescue.")


def self_test_verdict():
    cases = [
        ({"kappa4_separation_sd": 2.5, "sign_consistent_across_seeds": True,
          "kappa4_stored_mean": 1.2, "kappa4_unstored_mean": -0.5},
         "BETV_KAPPA4_RESCUE_PASS"),
        ({"kappa4_separation_sd": 0.5, "sign_consistent_across_seeds": False,
          "kappa4_stored_mean": 0.1, "kappa4_unstored_mean": 0.05},
         "BETV_KAPPA4_RESCUE_FAIL"),
        ({"kappa4_separation_sd": 1.5, "sign_consistent_across_seeds": True,
          "kappa4_stored_mean": 0.8, "kappa4_unstored_mean": 0.1},
         "BETV_KAPPA4_RESCUE_PARTIAL"),
        ({"kappa4_separation_sd": 2.5, "sign_consistent_across_seeds": False,
          "kappa4_stored_mean": 0.8, "kappa4_unstored_mean": 0.1},
         "BETV_KAPPA4_RESCUE_PARTIAL"),
        ({}, "BETV_KAPPA4_RESCUE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: got {got} expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bsc_codebook(n, N, gen, device):
    b = (torch.rand(n, N, generator=gen, device=device) > 0.5).float()
    return 2.0 * b - 1.0


def sign_q(x):
    s = torch.sign(x)
    s[s == 0] = 1.0
    return s


def confidence(probe, codebook):
    sims = codebook @ probe
    top2 = sims.topk(2).values
    raw_gap = float(top2[0] - top2[1])
    norm = float(sims.abs().max())
    return raw_gap / max(norm, 1e-9)


def excess_kurtosis(samples):
    """Classical k_4 = mu_4 / sigma^4 - 3 (Pearson excess kurtosis)."""
    n = len(samples)
    if n < 4:
        return 0.0
    m = sum(samples) / n
    var = sum((x - m) ** 2 for x in samples) / n
    if var < 1e-12:
        return 0.0
    mu4 = sum((x - m) ** 4 for x in samples) / n
    return mu4 / (var * var) - 3.0


def jackknife_se_k4(samples):
    """Jackknife standard error estimate of k_4 (leave-one-out)."""
    n = len(samples)
    if n < 5:
        return 0.0
    k4_full = excess_kurtosis(samples)
    k4_jk = []
    # For efficiency, use block jackknife when n is large
    n_blocks = min(20, n)
    block_size = max(1, n // n_blocks)
    for b in range(n_blocks):
        start = b * block_size
        end = start + block_size
        held_out = samples[:start] + samples[end:]
        if len(held_out) < 4:
            continue
        k4_jk.append(excess_kurtosis(held_out))
    if len(k4_jk) < 2:
        return 0.0
    mean_jk = sum(k4_jk) / len(k4_jk)
    var_jk = (len(k4_jk) - 1) / len(k4_jk) * sum((k - mean_jk) ** 2 for k in k4_jk)
    return math.sqrt(max(0.0, var_jk))


def run_one_seed(seed, config, device):
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]
    n_probes = config["n_probes"]
    gen = torch.Generator(device=device).manual_seed(seed)
    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    entity_atoms = make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = make_bsc_codebook(num_relations, N, gen, device)

    facts = []
    triples = []
    for _ in range(num_facts):
        s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
        o = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        facts.append((s, r, o))
        triples.append(sign_q(entity_atoms[s] * relation_atoms[r] * entity_atoms[o]))
    M = sign_q(torch.stack(triples, dim=0).sum(dim=0))

    stored_confs = []
    for s, r, o in facts[:n_probes]:
        probe = M * entity_atoms[s] * relation_atoms[r]
        stored_confs.append(confidence(probe, entity_atoms))

    fact_set = {(s, r): o for s, r, o in facts}
    unstored_confs = []
    attempts = 0
    while len(unstored_confs) < n_probes and attempts < n_probes * 20:
        s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
        r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
        if (s, r) not in fact_set:
            probe = M * entity_atoms[s] * relation_atoms[r]
            unstored_confs.append(confidence(probe, entity_atoms))
        attempts += 1

    k4_stored = excess_kurtosis(stored_confs)
    k4_unstored = excess_kurtosis(unstored_confs)
    se_stored = jackknife_se_k4(stored_confs)
    se_unstored = jackknife_se_k4(unstored_confs)

    return {
        "k4_stored": k4_stored,
        "k4_unstored": k4_unstored,
        "se_stored": se_stored,
        "se_unstored": se_unstored,
        "stored_confs": stored_confs,
        "unstored_confs": unstored_confs,
        "mean_stored": sum(stored_confs) / max(1, len(stored_confs)),
        "mean_unstored": sum(unstored_confs) / max(1, len(unstored_confs)),
    }


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # explicit CPU per matrix spec
    config = {
        "mode": "smoke" if smoke else "full",
        "N": 1024 if smoke else 4096,
        "num_entities": 50 if smoke else 200,
        "num_relations": 5 if smoke else 20,
        "num_facts": 30 if smoke else 100,
        "n_probes": 30 if smoke else 200,  # ENLARGED vs original Bet V; need >= 50 for stable k_4
        "seeds": [17] if smoke else [17, 23, 31, 37, 41],
        "device": "cpu",
        "note": "Bet V kappa_4 separation: substrate-novel higher-cumulant rescue probe.",
    }
    print(f"Bet V kappa_4: N={config['N']} n_probes={config['n_probes']} "
          f"seeds={config['seeds']}", flush=True)

    per_seed = []
    for seed in config["seeds"]:
        res = run_one_seed(seed, config, device)
        per_seed.append(res)
        print(f"  seed={seed}: k4_stored={res['k4_stored']:+.3f}+-"
              f"{res['se_stored']:.3f} k4_unstored={res['k4_unstored']:+.3f}+-"
              f"{res['se_unstored']:.3f} mean_stored={res['mean_stored']:.3f} "
              f"mean_unstored={res['mean_unstored']:.3f}", flush=True)

    k4_stored_per_seed = [r["k4_stored"] for r in per_seed]
    k4_unstored_per_seed = [r["k4_unstored"] for r in per_seed]
    se_stored = [r["se_stored"] for r in per_seed]
    se_unstored = [r["se_unstored"] for r in per_seed]

    k4_stored_mean = sum(k4_stored_per_seed) / len(k4_stored_per_seed)
    k4_unstored_mean = sum(k4_unstored_per_seed) / len(k4_unstored_per_seed)

    # Across-seed pooled SE (combine within-seed jackknife SE with across-seed variance)
    n_s = len(k4_stored_per_seed)
    var_stored_seed = sum((k - k4_stored_mean) ** 2 for k in k4_stored_per_seed) / max(1, n_s - 1)
    var_unstored_seed = sum((k - k4_unstored_mean) ** 2 for k in k4_unstored_per_seed) / max(1, n_s - 1)
    var_stored_within = sum(s * s for s in se_stored) / max(1, n_s) / n_s
    var_unstored_within = sum(s * s for s in se_unstored) / max(1, n_s) / n_s
    pooled_var_stored = var_stored_seed / max(1, n_s) + var_stored_within
    pooled_var_unstored = var_unstored_seed / max(1, n_s) + var_unstored_within
    pooled_se = math.sqrt(max(0.0, pooled_var_stored + pooled_var_unstored))

    sep_raw = k4_stored_mean - k4_unstored_mean
    sep_sd = sep_raw / pooled_se if pooled_se > 1e-9 else 0.0

    # Sign consistency: ALL stored k4 same sign across seeds (positive OR negative)
    sign_stored = [1 if k > 0 else (-1 if k < 0 else 0) for k in k4_stored_per_seed]
    sign_consistent = (len(set(sign_stored)) == 1 and 0 not in sign_stored)

    summary = {
        "kappa4_stored_mean": k4_stored_mean,
        "kappa4_unstored_mean": k4_unstored_mean,
        "kappa4_separation_raw": sep_raw,
        "pooled_se": pooled_se,
        "kappa4_separation_sd": sep_sd,
        "sign_consistent_across_seeds": sign_consistent,
        "k4_stored_per_seed": k4_stored_per_seed,
        "k4_unstored_per_seed": k4_unstored_per_seed,
        "n_seeds": n_s,
        "note": "Excess kurtosis (classical k_4 = mu_4/sigma^4 - 3) of stored vs "
                "unstored confidence distribution; pooled jackknife + across-seed SE.",
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nkappa4_stored_mean={k4_stored_mean:+.3f} unstored_mean={k4_unstored_mean:+.3f} "
          f"sep_raw={sep_raw:+.3f} pooled_se={pooled_se:.3f} sep_sd={sep_sd:+.2f}",
          flush=True)
    print(f"sign_consistent={sign_consistent}", flush=True)
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
    out_dir = get_output_dir("wave14_betV_kappa4_separation_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    assert "kappa4_separation_sd" in s
    assert s["n_seeds"] >= 1
    oracle.assert_baseline_high("se_finite", float(s["pooled_se"] >= 0), 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    self_test_verdict()
    out_dir = get_output_dir("wave14_betV_kappa4_separation_v1")
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
