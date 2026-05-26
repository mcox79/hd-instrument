"""Multi-hop reasoning v3 — hop-depth sweep through 50 with per-hop retention.

Extends wave14e_multi_hop_v2 (which stopped at hop=5, single seed) to test
the substrate-theory prediction that 50-hop chains remain viable when
per-hop cleanup is applied. Theory (per v2 docstring): at N=4096, F=50
facts, per-hop detection margin sqrt(N/F) ≈ 9 sigma → per-hop error
< 1e-8 → 50 hops feasible.

Sweep depths {1, 5, 10, 25, 50}, 3 seeds, 50 trials per depth. For each
trial, build a fresh fact-base M containing HOP_DEPTH chain transitions
plus (NUM_FACTS - HOP_DEPTH) random-distractor transitions, then chain-
query end-to-end with per-hop cleanup against the entity codebook.

Reports: per-depth mean accuracy, per-hop retention rate, log-decay slope.

Pre-reg: preregs/2026-05-21_wave14r_multihop_K10.md
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


N_FULL = 16384  # R8 pre-armed rescue #4: Goldstone-mode noise ~ sqrt(K)/N
N_SMOKE = 512
NUM_ENTITIES_FULL = 200
NUM_ENTITIES_SMOKE = 50
NUM_RELATIONS_FULL = 10
NUM_RELATIONS_SMOKE = 5
NUM_FACTS_FULL = 100
NUM_FACTS_SMOKE = 20
HOP_DEPTHS_FULL = [1, 5, 10, 25, 50]
HOP_DEPTHS_SMOKE = [1, 5]
N_TRIALS_FULL = 50
N_TRIALS_SMOKE = 5
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]

PASS_ACC_1HOP = 0.98
PASS_ACC_50HOP = 0.10
PASS_RETENTION_STD = 0.05
KILL_ACC_5HOP_FLOOR = 0.50
KILL_ACC_50HOP = 0.02
KILL_RETENTION_FLOOR = 0.85
ACC_FLOOR = 1e-3  # below this, count as "no measurable accuracy"


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def _least_squares_slope(xs, ys) -> float:
    n = len(xs)
    if n < 2:
        return 0.0
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((xs[i] - mean_x) * (ys[i] - mean_y) for i in range(n))
    den = sum((xs[i] - mean_x) ** 2 for i in range(n))
    return num / den if abs(den) > 1e-12 else 0.0


def per_hop_retention_rate(per_depth_acc: dict) -> float:
    """Geometric-mean per-hop retention from the deepest depth with measurable acc.
    Uses a >= ACC_FLOOR so a seed that hits exactly the floor still contributes."""
    valid = [(k, a) for k, a in per_depth_acc.items() if a >= ACC_FLOOR and k >= 1]
    if not valid:
        return 0.0
    k_max, a_max = max(valid, key=lambda kv: kv[0])
    return a_max ** (1.0 / k_max)


def log_decay_slope(per_depth_acc: dict) -> float:
    """Slope of ln(accuracy) vs hop depth via least squares (acc floored at ACC_FLOOR)."""
    items = sorted(per_depth_acc.items())
    if len(items) < 2:
        return 0.0
    xs = [float(k) for k, _ in items]
    ys = [math.log(max(a, ACC_FLOOR)) for _, a in items]
    return _least_squares_slope(xs, ys)


def compute_verdict(summary: dict) -> tuple[str, str]:
    per_depth_mean = summary.get("per_depth_mean_acc")
    per_seed_acc = summary.get("per_seed_acc")  # dict[str(seed)] -> dict[str(depth)] -> acc
    if not per_depth_mean:
        return ("MULTIHOP_INCONCLUSIVE", "Missing per-depth accuracy data.")

    # Normalize keys (json roundtrip may stringify integer keys)
    pdm = {int(k): float(v) for k, v in per_depth_mean.items()}
    psa = None
    if per_seed_acc:
        psa = {seed: {int(d): float(a) for d, a in by_d.items()}
               for seed, by_d in per_seed_acc.items()}

    # Kill 1: v2 not replicated (any seed with acc_5hop < 0.5)
    if psa:
        bad_seeds = [seed for seed, by_d in psa.items()
                     if by_d.get(5, 1.0) < KILL_ACC_5HOP_FLOOR]
        if bad_seeds:
            seed_str = ",".join(str(s) for s in bad_seeds)
            return ("MULTIHOP_V2_NOT_REPLICATED",
                    f"acc_5hop < {KILL_ACC_5HOP_FLOOR} on seed(s) {seed_str}. v2 finding "
                    f"doesn't replicate; audit test setup before drawing depth conclusions.")

    acc_1 = pdm.get(1, 0.0)
    acc_5 = pdm.get(5, 0.0)
    acc_50 = pdm.get(50, 0.0)
    retention = per_hop_retention_rate(pdm)
    slope = log_decay_slope(pdm)

    # Per-seed retention std
    retention_std = 0.0
    if psa and len(psa) > 1:
        per_seed_ret = [per_hop_retention_rate(by_d) for by_d in psa.values()]
        if per_seed_ret:
            m = sum(per_seed_ret) / len(per_seed_ret)
            retention_std = math.sqrt(sum((r - m) ** 2 for r in per_seed_ret) /
                                      max(len(per_seed_ret) - 1, 1))

    # Kill 2: catastrophic decay
    if acc_50 <= KILL_ACC_50HOP and retention < KILL_RETENTION_FLOOR:
        # Find the first depth where acc fell below 0.10
        depths_sorted = sorted(pdm.keys())
        decay_at = None
        for d in depths_sorted:
            if pdm[d] < 0.10:
                decay_at = d
                break
        return ("MULTIHOP_CATASTROPHIC_DECAY",
                f"acc_50hop={acc_50:.3f} <= {KILL_ACC_50HOP} and per-hop retention="
                f"{retention:.3f} < {KILL_RETENTION_FLOOR}. Cleanup-budget insufficient "
                f"for deep chains; first decay below 0.10 at depth={decay_at}.")

    # PASS: 3 non-redundant criteria. retention >= 0.90 and slope >= -0.05
    # are mathematically implied by acc_50 > 0.10 (since 0.10^(1/50) = 0.955),
    # so they would add no signal here.
    pass_all = (
        acc_1 >= PASS_ACC_1HOP
        and acc_50 > PASS_ACC_50HOP
        and retention_std < PASS_RETENTION_STD
    )
    if pass_all:
        return ("MULTIHOP_50HOP_VALIDATED",
                f"50-hop multi-hop reasoning validated. acc_1hop={acc_1:.3f}, "
                f"acc_5hop={acc_5:.3f}, acc_50hop={acc_50:.3f}, per-hop retention="
                f"{retention:.4f} (per-seed std {retention_std:.4f}), log-decay slope="
                f"{slope:+.4f}/hop. Tier-2 KILLER probe passes.")

    # DECAY_AT_<D>: partial credit
    depths_sorted = sorted(pdm.keys())
    decay_at = None
    for d in depths_sorted:
        if pdm[d] < 0.10:
            decay_at = d
            break
    if decay_at is not None:
        return (f"MULTIHOP_DECAY_AT_{decay_at}",
                f"Multi-hop works through depth {max(d for d in depths_sorted if pdm[d] >= 0.10)}; "
                f"falls below 0.10 at depth={decay_at}. acc_1hop={acc_1:.3f}, retention="
                f"{retention:.3f}, slope={slope:+.4f}/hop. Capability bounded at intermediate "
                f"depth; not catastrophic but not 50-hop.")

    # All depths above 0.10 but PASS criteria not met → describe specifically
    fails = []
    if acc_1 < PASS_ACC_1HOP:
        fails.append(f"acc_1hop={acc_1:.3f}<{PASS_ACC_1HOP}")
    if acc_50 <= PASS_ACC_50HOP:
        fails.append(f"acc_50hop={acc_50:.3f}<={PASS_ACC_50HOP}")
    if retention_std >= PASS_RETENTION_STD:
        fails.append(f"ret_std={retention_std:.3f}>={PASS_RETENTION_STD}")
    return ("MULTIHOP_DECAY_AT_50",
            f"All tested depths achieve >0.10 mean accuracy but PASS criteria not all met: " +
            "; ".join(fails) + f". Soft pass on depth coverage; instability or boundary fail.")


def self_test_verdict() -> None:
    cases = [
        # 1. VALIDATED: high retention, gentle decay
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.95, 10: 0.90, 25: 0.78, 50: 0.60},
          "per_seed_acc": {"17": {1: 0.99, 5: 0.95, 10: 0.90, 25: 0.78, 50: 0.60},
                            "23": {1: 0.99, 5: 0.95, 10: 0.91, 25: 0.79, 50: 0.61},
                            "31": {1: 0.99, 5: 0.95, 10: 0.90, 25: 0.77, 50: 0.59}}},
         "MULTIHOP_50HOP_VALIDATED"),
        # 2. CATASTROPHIC: acc_50 = 0, retention low
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.50, 10: 0.20, 25: 0.01, 50: 0.0},
          "per_seed_acc": {"17": {1: 0.99, 5: 0.55, 10: 0.20, 25: 0.01, 50: 0.0}}},
         "MULTIHOP_CATASTROPHIC_DECAY"),
        # 3. V2 NOT REPLICATED: one seed shows acc_5hop too low
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.60, 10: 0.30, 25: 0.10, 50: 0.05},
          "per_seed_acc": {"17": {1: 0.99, 5: 0.40, 10: 0.30, 25: 0.10, 50: 0.05}}},
         "MULTIHOP_V2_NOT_REPLICATED"),
        # 4. DECAY_AT_25: works to 10, falls at 25
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.85, 10: 0.65, 25: 0.05, 50: 0.0},
          "per_seed_acc": {"17": {1: 0.99, 5: 0.85, 10: 0.65, 25: 0.05, 50: 0.0}}},
         "MULTIHOP_DECAY_AT_25"),
        # 5. INCONCLUSIVE: empty
        ({}, "MULTIHOP_INCONCLUSIVE"),
        # 6. Soft pass DECAY_AT_50: all depth means above 0.10 but per-seed
        # retentions are unstable. Seeds 17/23/31 have acc_50 {0.50, 0.05, 0.001}
        # -> retentions {0.986, 0.942, 0.871}, std ~= 0.058 > 0.05 threshold.
        # Mean acc_50 = 0.184 > 0.10 so depth coverage passes; only stability fails.
        ({"per_depth_mean_acc": {1: 0.99, 5: 0.85, 10: 0.65, 25: 0.30, 50: 0.184},
          "per_seed_acc": {"17": {1: 0.99, 5: 0.95, 10: 0.85, 25: 0.50, 50: 0.50},
                            "23": {1: 0.99, 5: 0.80, 10: 0.60, 25: 0.20, 50: 0.05},
                            "31": {1: 0.99, 5: 0.80, 10: 0.50, 25: 0.20, 50: 0.001}}},
         "MULTIHOP_DECAY_AT_50"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bsc_codebook(k: int, n: int, gen: torch.Generator,
                       device: torch.device) -> torch.Tensor:
    raw = torch.rand((k, n), generator=gen, device=device) > 0.5
    return 2.0 * raw.float() - 1.0


def sign_quantize(x):
    s = torch.sign(x)
    return torch.where(s == 0, torch.ones_like(s), s)


def cleanup_argmax(noisy: torch.Tensor, codebook: torch.Tensor) -> int:
    """Return index of closest codebook atom to noisy (by inner product)."""
    sims = codebook @ noisy
    return int(sims.argmax().item())


def build_factbase(chain_entities: list[int], chain_rels: list[int],
                    n_distractors: int, num_entities: int, num_relations: int,
                    entity_atoms: torch.Tensor, relation_atoms: torch.Tensor,
                    cpu_gen: torch.Generator, device: torch.device) -> torch.Tensor:
    """Construct M = sign(Σ chain_triples + Σ distractor_triples)."""
    triples = []
    for i in range(len(chain_rels)):
        subj = entity_atoms[chain_entities[i]]
        rel = relation_atoms[chain_rels[i]]
        obj = entity_atoms[chain_entities[i + 1]]
        triples.append(sign_quantize(subj * rel * obj))
    if n_distractors > 0:
        dist_subj_idx = torch.randint(0, num_entities, (n_distractors,), generator=cpu_gen)
        dist_rel_idx = torch.randint(0, num_relations, (n_distractors,), generator=cpu_gen)
        dist_obj_idx = torch.randint(0, num_entities, (n_distractors,), generator=cpu_gen)
        for j in range(n_distractors):
            subj = entity_atoms[int(dist_subj_idx[j])]
            rel = relation_atoms[int(dist_rel_idx[j])]
            obj = entity_atoms[int(dist_obj_idx[j])]
            triples.append(sign_quantize(subj * rel * obj))
    stacked = torch.stack(triples, dim=0)
    return sign_quantize(stacked.sum(dim=0))


def run_chain(M: torch.Tensor, start_idx: int, rel_idxs: list[int], target_idx: int,
               entity_atoms: torch.Tensor, relation_atoms: torch.Tensor) -> bool:
    """Walk the chain with per-hop cleanup. Return True iff final cleanup == target."""
    current_idx = start_idx
    for r_idx in rel_idxs:
        current = entity_atoms[current_idx]
        rel = relation_atoms[r_idx]
        probe = M * (current * rel)
        current_idx = cleanup_argmax(probe, entity_atoms)
    return current_idx == target_idx


def run_one_seed(seed: int, hop_depths: list[int], n_trials: int,
                  config: dict, device: torch.device) -> dict:
    N = config["N"]
    num_entities = config["num_entities"]
    num_relations = config["num_relations"]
    num_facts = config["num_facts"]

    gen = torch.Generator(device=device).manual_seed(seed)
    entity_atoms = make_bsc_codebook(num_entities, N, gen, device)
    relation_atoms = make_bsc_codebook(num_relations, N, gen, device)

    # Codebook orthogonality measurement (for oracle in smoke)
    ent_ips = (entity_atoms @ entity_atoms.T) / N
    mask = ~torch.eye(num_entities, dtype=torch.bool, device=device)
    max_pairwise = float(ent_ips[mask].abs().max())

    cpu_gen = torch.Generator().manual_seed(seed + 1009)

    by_depth = {}
    for depth in hop_depths:
        if depth > num_entities - 1:
            by_depth[depth] = 0.0
            continue
        if depth > num_facts:
            # Can't fit a chain of `depth` transitions inside NUM_FACTS facts
            by_depth[depth] = 0.0
            continue
        correct = 0
        for trial in range(n_trials):
            # Sample chain entities + relations
            perm = torch.randperm(num_entities, generator=cpu_gen)[:depth + 1]
            chain_entities = perm.tolist()
            chain_rels = [int(torch.randint(0, num_relations, (1,),
                                              generator=cpu_gen).item())
                          for _ in range(depth)]
            n_distractors = max(0, num_facts - depth)
            M = build_factbase(chain_entities, chain_rels, n_distractors,
                                num_entities, num_relations,
                                entity_atoms, relation_atoms, cpu_gen, device)
            ok = run_chain(M, chain_entities[0], chain_rels, chain_entities[-1],
                            entity_atoms, relation_atoms)
            if ok:
                correct += 1
        by_depth[depth] = correct / n_trials
    return {"seed": seed, "by_depth": by_depth, "max_pairwise_ip": max_pairwise}


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "num_entities": NUM_ENTITIES_SMOKE if smoke else NUM_ENTITIES_FULL,
        "num_relations": NUM_RELATIONS_SMOKE if smoke else NUM_RELATIONS_FULL,
        "num_facts": NUM_FACTS_SMOKE if smoke else NUM_FACTS_FULL,
        "hop_depths": HOP_DEPTHS_SMOKE if smoke else HOP_DEPTHS_FULL,
        "n_trials": N_TRIALS_SMOKE if smoke else N_TRIALS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    per_seed_results = []
    for seed in config["seeds"]:
        print(f"[seed={seed}] running...", flush=True)
        r = run_one_seed(seed, config["hop_depths"], config["n_trials"], config, device)
        per_seed_results.append(r)
        accs = " ".join(f"d{d}={r['by_depth'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed} max_ip={r['max_pairwise_ip']:.3f}  {accs}", flush=True)

    # Aggregate across seeds
    per_depth_mean = {}
    for d in config["hop_depths"]:
        vals = [r["by_depth"][d] for r in per_seed_results]
        per_depth_mean[d] = sum(vals) / len(vals)

    per_seed_acc = {str(r["seed"]): {str(d): r["by_depth"][d] for d in config["hop_depths"]}
                     for r in per_seed_results}

    retention = per_hop_retention_rate(per_depth_mean)
    slope = log_decay_slope(per_depth_mean)

    summary = {
        "per_depth_mean_acc": {str(d): per_depth_mean[d] for d in config["hop_depths"]},
        "per_seed_acc": per_seed_acc,
        "per_hop_retention_rate": retention,
        "log_decay_slope_per_hop": slope,
        "max_pairwise_ip_per_seed": {str(r["seed"]): r["max_pairwise_ip"]
                                       for r in per_seed_results},
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= AGGREGATE =========", flush=True)
    for d in config["hop_depths"]:
        print(f"  depth={d:3d}  mean_acc={per_depth_mean[d]:.3f}", flush=True)
    print(f"  per-hop retention rate = {retention:.4f}", flush=True)
    print(f"  log-decay slope = {slope:+.4f} per hop", flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14r_multihop_K10_smoke")
    log_event("experiment_started", name="wave14r_multihop_K10", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle 1: 1-hop must work even at smoke scale
    acc_1hop = summary["per_depth_mean_acc"].get("1", 0.0)
    if isinstance(acc_1hop, str):
        acc_1hop = float(acc_1hop)
    oracle.assert_baseline_high("acc_1hop_smoke", acc_1hop, 0.85)

    # Oracle 2: entity codebook pairwise IPs bounded
    max_ips = list(summary["max_pairwise_ip_per_seed"].values())
    max_ip = max(float(v) for v in max_ips)
    oracle.assert_in_range("entity_codebook_pairwise_max", max_ip, (0.0, 0.30))

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14r_multihop_K10",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14r_multihop_K10")
    log_event("experiment_started", name="wave14r_multihop_K10", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14r_multihop_K10",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
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
