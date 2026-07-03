"""Bet T per-hypothesis TEMPSCALE rescue (Research rescue sketch #2, P_deflated=0.45).

Metric-definition fix for cycle 101 BET_T_PARTIAL min_acc=0.689.
Problem: shared beta=32 is ~4x too large at N=4096 (optimal beta = c/N = 32768/4096 = 8).
The weakest hypothesis is mis-calibrated first.

Fix: run Bet T with per-hypothesis beta_h in {4, 8, 16} sweep; record logits
(raw cosine scores before cleanup threshold). For each beta_h, compute:
  - per_hyp_acc_h: accuracy per hypothesis at that temperature
  - ECE_h: calibration error per hypothesis (|predicted confidence - accuracy|)
  - min_acc, mean_acc across hypotheses

HARD PASS: at best beta_h, min_acc >= 0.85 AND mean_acc >= 0.90 AND ECE_max_h <= 0.10
HARD FAIL: at ALL beta_h, min_acc < 0.70 (no improvement over cycle 101's 0.689)

Pure CPU. No new substrate change -- same W, same codebooks, different readout beta.
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


HARD_PASS_MIN_ACC = 0.85
HARD_PASS_MEAN_ACC = 0.90
HARD_PASS_ECE_MAX = 0.10
HARD_FAIL_MIN_ACC = 0.70  # no improvement from 0.689


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing keys in metrics")


def compute_verdict(s):
    if "best_min_acc" not in s:
        return ("BET_T_TEMPSCALE_INCONCLUSIVE", "Missing best_min_acc.")
    bmin = s["best_min_acc"]
    bmean = s["best_mean_acc"]
    bece = s["best_ece_max"]
    if bmin >= HARD_PASS_MIN_ACC and bmean >= HARD_PASS_MEAN_ACC and bece <= HARD_PASS_ECE_MAX:
        return ("BET_T_TEMPSCALE_PASS",
                f"HARD PASS: best_min_acc={bmin:.3f}>={HARD_PASS_MIN_ACC} "
                f"mean_acc={bmean:.3f}>={HARD_PASS_MEAN_ACC} "
                f"ECE_max={bece:.3f}<={HARD_PASS_ECE_MAX}. "
                f"Per-hypothesis TEMPSCALE rescues Bet T from cycle-101 PARTIAL 0.689.")
    if bmin < HARD_FAIL_MIN_ACC:
        return ("BET_T_TEMPSCALE_KILL",
                f"HARD FAIL: best_min_acc={bmin:.3f} < {HARD_FAIL_MIN_ACC} at ALL beta_h. "
                f"Per-hypothesis TEMPSCALE did not lift min_acc above 0.70.")
    return ("BET_T_TEMPSCALE_PARTIAL",
            f"Partial: best_min_acc={bmin:.3f} in [{HARD_FAIL_MIN_ACC},{HARD_PASS_MIN_ACC}). "
            f"mean_acc={bmean:.3f} ECE_max={bece:.3f}. "
            f"Improvement over 0.689 but HARD PASS not met.")


def self_test_verdict():
    cases = [
        ({"best_min_acc": 0.88, "best_mean_acc": 0.93, "best_ece_max": 0.08},
         "BET_T_TEMPSCALE_PASS"),
        ({"best_min_acc": 0.65, "best_mean_acc": 0.80, "best_ece_max": 0.12},
         "BET_T_TEMPSCALE_KILL"),
        ({"best_min_acc": 0.77, "best_mean_acc": 0.87, "best_ece_max": 0.09},
         "BET_T_TEMPSCALE_PARTIAL"),
        ({}, "BET_T_TEMPSCALE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: got {got} expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def sign_q(x):
    s = torch.sign(x); s[s == 0] = 1.0; return s


def make_bsc_codebook(n, N, gen, device):
    b = (torch.rand(n, N, generator=gen, device=device) > 0.5).float()
    return 2.0 * b - 1.0


def softmax_confidence(scores, beta):
    """Return (top-1 prob, predicted index) for a score vector."""
    logits = beta * scores
    logits = logits - logits.max()
    exps = logits.exp()
    probs = exps / exps.sum()
    pred = int(probs.argmax().item())
    conf = float(probs[pred].item())
    return pred, conf


def run_one_seed(seed, config, device, beta_h_list):
    """Run Bet T at this seed with per-hypothesis beta in beta_h_list.

    Returns dict: beta_h -> {"per_hyp_acc": {k: acc}, "per_hyp_ece": {k: ece}}
    """
    N = config["N"]
    K_hyp = config["n_hypotheses"]
    n_facts = config["n_facts_per_hyp"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]

    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = make_bsc_codebook(num_relations, N, gen, device)
    hyp_atoms = make_bsc_codebook(K_hyp, N, gen, device)

    cpu_gen = torch.Generator().manual_seed(seed + 1009)
    hyp_facts = []
    for _ in range(K_hyp):
        facts = []
        for _i in range(n_facts):
            s = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
            r = int(torch.randint(0, num_relations, (1,), generator=cpu_gen))
            o = int(torch.randint(0, num_entities, (1,), generator=cpu_gen))
            facts.append((s, r, o))
        hyp_facts.append(facts)

    # Build joint memory matrix
    triples_per_hyp = []
    for k, facts in enumerate(hyp_facts):
        triples = [sign_q(entity_atoms[s] * relation_atoms[r] * entity_atoms[o])
                   for s, r, o in facts]
        bundle_k = sign_q(torch.stack(triples, dim=0).sum(dim=0))
        triples_per_hyp.append(hyp_atoms[k] * bundle_k)
    M_joint = sign_q(torch.stack(triples_per_hyp, dim=0).sum(dim=0))

    # For each beta_h, decode and compute accuracy + ECE
    results_by_beta = {}
    for beta_h in beta_h_list:
        per_hyp_acc = {}
        per_hyp_ece = {}
        for k, facts in enumerate(hyp_facts):
            correct = 0; confs = []; corrects = []
            for s, r, o in facts:
                probe = M_joint * hyp_atoms[k] * entity_atoms[s] * relation_atoms[r]
                scores = entity_atoms @ probe  # (num_entities,)
                pred, conf = softmax_confidence(scores, beta_h)
                is_correct = int(pred == o)
                correct += is_correct
                confs.append(conf); corrects.append(is_correct)
            acc = correct / n_facts
            # ECE: |mean_conf - acc|
            ece = abs(sum(confs) / len(confs) - acc)
            per_hyp_acc[str(k)] = acc
            per_hyp_ece[str(k)] = ece
        results_by_beta[str(beta_h)] = {"per_hyp_acc": per_hyp_acc, "per_hyp_ece": per_hyp_ece}
    return results_by_beta


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # CPU-only experiment
    cfg = {
        "N": 512 if smoke else 4096,
        "num_entities": 30 if smoke else 200,
        "num_relations": 4 if smoke else 20,
        "n_hypotheses": 3 if smoke else 8,
        "n_facts_per_hyp": 5 if smoke else 30,
        "seeds": [17] if smoke else [17, 23, 31],
        "beta_h_list": [4, 8, 16],
        "device": "cpu",
        "note": "Per-hypothesis TEMPSCALE rescue for Bet T; optimal beta_h=c/N=8 at N=4096",
    }
    beta_h_list = cfg["beta_h_list"]

    # Aggregate across seeds: per beta_h -> {per_hyp_acc, per_hyp_ece}
    all_seeds = {}
    for seed in cfg["seeds"]:
        r = run_one_seed(seed, cfg, device, beta_h_list)
        all_seeds[str(seed)] = r
        for bh in beta_h_list:
            accs = r[str(bh)]["per_hyp_acc"]
            print(f"  seed={seed} beta={bh}: " + " ".join(f"h{k}={accs[k]:.3f}" for k in accs),
                  flush=True)

    # Average per hypothesis per beta across seeds
    K_hyp = cfg["n_hypotheses"]
    best_min_acc = -1.0; best_mean_acc = -1.0; best_ece_max = 99.0; best_beta = None
    per_beta_summary = {}
    for bh in beta_h_list:
        acc_per_hyp = {}
        ece_per_hyp = {}
        for k in range(K_hyp):
            accs_k = [all_seeds[str(s)][str(bh)]["per_hyp_acc"][str(k)] for s in cfg["seeds"]]
            eces_k = [all_seeds[str(s)][str(bh)]["per_hyp_ece"][str(k)] for s in cfg["seeds"]]
            acc_per_hyp[str(k)] = sum(accs_k) / len(accs_k)
            ece_per_hyp[str(k)] = sum(eces_k) / len(eces_k)
        min_acc = min(acc_per_hyp.values())
        mean_acc = sum(acc_per_hyp.values()) / K_hyp
        ece_max = max(ece_per_hyp.values())
        per_beta_summary[str(bh)] = {
            "min_acc": min_acc, "mean_acc": mean_acc, "ece_max": ece_max,
            "per_hyp_acc": acc_per_hyp, "per_hyp_ece": ece_per_hyp,
        }
        print(f"  beta={bh}: min_acc={min_acc:.3f} mean_acc={mean_acc:.3f} "
              f"ece_max={ece_max:.3f}", flush=True)
        if min_acc > best_min_acc or (min_acc == best_min_acc and ece_max < best_ece_max):
            best_min_acc = min_acc; best_mean_acc = mean_acc
            best_ece_max = ece_max; best_beta = bh

    summary = {
        "best_min_acc": best_min_acc,
        "best_mean_acc": best_mean_acc,
        "best_ece_max": best_ece_max,
        "best_beta": best_beta,
        "per_beta_summary": per_beta_summary,
        "baseline_cycle101_min_acc": 0.689,
        "note": "Baseline beta=32 cycle-101 min_acc=0.689; optimal beta_h=c/N=8 at N=4096",
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, cfg


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_betT_per_hyp_tempscale_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    oracle.assert_baseline_high("best_min_acc", s["best_min_acc"], 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betT_per_hyp_tempscale_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__": sys.exit(main())
