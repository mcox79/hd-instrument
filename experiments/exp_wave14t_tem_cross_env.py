"""TEM-style cross-environment transfer test for compositional schema.

Question: does our substrate encode role-presence in a way that transfers
across environments with disjoint filler atoms? If yes, real compositional
schema. If no, just env-specific representation.

Setup (Whittington 2020 TEM cognitive map):
  - Roles R = {r_1..r_m}: shared between env-A and env-B
  - Env-A fillers F_A: disjoint from env-B fillers F_B
  - "Scene" = bundle of (role, filler) bindings
  - Task: linear probe to decode which roles are present in the scene
  - Train probe on env-A scenes; test transfer to env-B scenes

Baselines (must run as part of the same test):
  - SUBSTRATE: use the bundle directly. Predict: positive transfer.
  - PCA: project env-A bundles to top-K PCs, train probe, test on env-B. Predict: ~chance.
  - RANDOM: shuffle probe labels. Predict: ~chance.

Pre-reg: preregs/2026-05-20_wave14t_tem_cross_env.md
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402


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


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Schema confirmed if substrate transfer > 1.5x PCA AND > 1.5x random baseline."""
    s = summary.get("by_method", {})
    sub = s.get("substrate", {})
    pca = s.get("pca", {})
    rnd = s.get("random", {})
    sub_acc = sub.get("transfer_acc")
    pca_acc = pca.get("transfer_acc", 0.5)
    rnd_acc = rnd.get("transfer_acc", 0.5)
    if sub_acc is None:
        return ("TEM_INCONCLUSIVE", "No substrate transfer accuracy.")
    if sub_acc >= max(pca_acc, rnd_acc) * 1.5 and sub_acc > 0.65:
        return ("TEM_SCHEMA_CONFIRMED",
                f"Substrate transfer acc={sub_acc:.2%} >> PCA ({pca_acc:.2%}) "
                f"and random ({rnd_acc:.2%}). Real compositional schema.")
    if sub_acc > max(pca_acc, rnd_acc) * 1.15:
        return ("TEM_SCHEMA_PARTIAL",
                f"Substrate acc={sub_acc:.2%} > PCA ({pca_acc:.2%}) and "
                f"random ({rnd_acc:.2%}), but margin smaller than 1.5x ratio. "
                f"Partial schema or weak signal.")
    return ("TEM_NO_SCHEMA",
            f"Substrate acc={sub_acc:.2%} not meaningfully above PCA ({pca_acc:.2%}) "
            f"or random ({rnd_acc:.2%}). No compositional transfer; binding "
            f"isn't producing transferable role representations.")


def self_test_verdict() -> None:
    cases = [
        ({"by_method": {"substrate": {"transfer_acc": 0.85},
                        "pca": {"transfer_acc": 0.50},
                        "random": {"transfer_acc": 0.50}}}, "TEM_SCHEMA_CONFIRMED"),
        ({"by_method": {"substrate": {"transfer_acc": 0.60},
                        "pca": {"transfer_acc": 0.50},
                        "random": {"transfer_acc": 0.50}}}, "TEM_SCHEMA_PARTIAL"),
        ({"by_method": {"substrate": {"transfer_acc": 0.51},
                        "pca": {"transfer_acc": 0.50},
                        "random": {"transfer_acc": 0.50}}}, "TEM_NO_SCHEMA"),
        ({"by_method": {}}, "TEM_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {s} -> {actual} expected {expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bipolar(shape, gen, device):
    # If generator is on CPU but device is CUDA, generate on CPU then move
    if gen.device.type == "cpu" and device.type == "cuda":
        x = 2.0 * (torch.rand(shape, generator=gen) > 0.5).float() - 1.0
        return x.to(device)
    return 2.0 * (torch.rand(shape, generator=gen, device=device) > 0.5).float() - 1.0


def make_bipolar_cpu_to_device(shape, gen, device):
    """Convenience: CPU generator, then move to device."""
    x = 2.0 * (torch.rand(shape, generator=gen) > 0.5).float() - 1.0
    return x.to(device)


def build_scenes(roles, fillers, n_scenes, roles_per_scene, gen, device):
    """Each scene: sum of (r_i * f_j) for randomly selected (role, filler) pairs.
    Returns (scenes, role_labels) where scenes is (n_scenes, N) and role_labels
    is (n_scenes, n_roles) boolean.
    """
    n_roles = roles.size(0)
    n_fillers = fillers.size(0)
    N = roles.size(-1)
    scenes = torch.zeros((n_scenes, N), device=device)
    labels = torch.zeros((n_scenes, n_roles), device=device)
    for s in range(n_scenes):
        # random subset of roles for this scene
        role_perm = torch.randperm(n_roles, generator=gen)[:roles_per_scene]
        for r_idx in role_perm.tolist():
            f_idx = int(torch.randint(0, n_fillers, (1,), generator=gen).item())
            scenes[s] += roles[r_idx] * fillers[f_idx]  # Hadamard bind
            labels[s, r_idx] = 1.0
    return scenes, labels


def linear_probe_train(X, y, lambda_reg=1.0):
    """Ridge regression: W = (X^T X + lambda I)^-1 X^T y. Returns weights (N, n_out)."""
    N = X.size(-1)
    XtX = X.T @ X + lambda_reg * torch.eye(N, device=X.device)
    XtY = X.T @ y
    return torch.linalg.solve(XtX, XtY)


def evaluate_probe(W_probe, X, y) -> float:
    """Multi-label accuracy: predict y>0.5 from W_probe @ x; fraction of correct labels."""
    pred = (X @ W_probe > 0.5).float()
    return ((pred == y).float().mean()).item()


def run_one(N, n_roles, n_fillers_per_env, n_scenes_train, n_scenes_test,
            roles_per_scene, seed, device):
    # Use CPU generator (works for both CPU and GPU operations via cuda fallback)
    gen = torch.Generator().manual_seed(seed)
    # Shared roles - generate on CPU then move to device
    roles = make_bipolar_cpu_to_device((n_roles, N), gen, device)
    # Disjoint filler sets
    fillers_A = make_bipolar((n_fillers_per_env, N), gen, device)
    fillers_B = make_bipolar((n_fillers_per_env, N), gen, device)

    # Build env-A scenes (train + test_A) and env-B scenes (test_B)
    train_A_X, train_A_y = build_scenes(roles, fillers_A, n_scenes_train, roles_per_scene,
                                          gen, device)
    test_A_X, test_A_y = build_scenes(roles, fillers_A, n_scenes_test, roles_per_scene,
                                       gen, device)
    test_B_X, test_B_y = build_scenes(roles, fillers_B, n_scenes_test, roles_per_scene,
                                       gen, device)

    results = {}

    # METHOD 1: SUBSTRATE - use bundles directly
    W_probe = linear_probe_train(train_A_X, train_A_y)
    sub_test_A = evaluate_probe(W_probe, test_A_X, test_A_y)
    sub_test_B = evaluate_probe(W_probe, test_B_X, test_B_y)
    results["substrate"] = {"in_env_acc": sub_test_A, "transfer_acc": sub_test_B}

    # METHOD 2: PCA - project bundles to top-K PCs first
    k_pc = n_roles  # match dimensionality to role count
    train_centered = train_A_X - train_A_X.mean(dim=0)
    cov = train_centered.T @ train_centered / train_centered.size(0)
    _, _, Vt = torch.linalg.svd(cov)
    P = Vt[:k_pc].T  # (N, k_pc) projector
    train_A_P = train_A_X @ P
    test_A_P = test_A_X @ P
    test_B_P = test_B_X @ P
    W_pca = linear_probe_train(train_A_P, train_A_y, lambda_reg=0.1)
    pca_test_A = evaluate_probe(W_pca, test_A_P, test_A_y)
    pca_test_B = evaluate_probe(W_pca, test_B_P, test_B_y)
    results["pca"] = {"in_env_acc": pca_test_A, "transfer_acc": pca_test_B}

    # METHOD 3: RANDOM - shuffled labels
    perm = torch.randperm(train_A_y.size(0), generator=gen)
    W_rnd = linear_probe_train(train_A_X, train_A_y[perm])
    rnd_test_A = evaluate_probe(W_rnd, test_A_X, test_A_y)
    rnd_test_B = evaluate_probe(W_rnd, test_B_X, test_B_y)
    results["random"] = {"in_env_acc": rnd_test_A, "transfer_acc": rnd_test_B}

    return {"seed": seed, "methods": results}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "n_roles": 4, "n_fillers_per_env": 8,
                  "n_scenes_train": 200, "n_scenes_test": 50, "roles_per_scene": 2,
                  "seeds": [17]}
    else:
        # Substantial config: multiple seeds, larger env
        config = {"mode": "full", "N": 4096, "n_roles": 8, "n_fillers_per_env": 30,
                  "n_scenes_train": 2000, "n_scenes_test": 500, "roles_per_scene": 3,
                  "seeds": [17, 23, 31, 41, 53, 67, 79]}
    print(f"wave14t_tem_cross_env. mode={config['mode']} device={device}", flush=True)
    print(f"  N={config['N']} n_roles={config['n_roles']} "
          f"n_fillers/env={config['n_fillers_per_env']} "
          f"roles/scene={config['roles_per_scene']}", flush=True)
    print(f"  seeds={config['seeds']}", flush=True)

    t0 = time.monotonic()
    all_runs = []
    for seed in config["seeds"]:
        r = run_one(config["N"], config["n_roles"], config["n_fillers_per_env"],
                    config["n_scenes_train"], config["n_scenes_test"],
                    config["roles_per_scene"], seed, device)
        all_runs.append(r)
        print(f"  seed={seed}  substrate={r['methods']['substrate']['transfer_acc']:.3f}  "
              f"pca={r['methods']['pca']['transfer_acc']:.3f}  "
              f"random={r['methods']['random']['transfer_acc']:.3f}", flush=True)
    elapsed = time.monotonic() - t0

    def avg(method_key, metric_key):
        return sum(r["methods"][method_key][metric_key] for r in all_runs) / len(all_runs)
    by_method = {
        "substrate": {"in_env_acc": avg("substrate", "in_env_acc"),
                      "transfer_acc": avg("substrate", "transfer_acc")},
        "pca": {"in_env_acc": avg("pca", "in_env_acc"),
                "transfer_acc": avg("pca", "transfer_acc")},
        "random": {"in_env_acc": avg("random", "in_env_acc"),
                   "transfer_acc": avg("random", "transfer_acc")},
    }

    # Oracle: substrate in-env accuracy should be HIGH (substrate works);
    # if not, the test setup is broken.
    oracle.assert_baseline_high("substrate in-env acc",
                                  by_method["substrate"]["in_env_acc"], 0.85)
    # PCA should NOT transfer (it overfits env-A)
    if by_method["pca"]["transfer_acc"] > 0.75:
        raise AssertionError(
            f"SANITY FAIL: PCA transfer={by_method['pca']['transfer_acc']:.2%} is "
            f"too high (>75%). Either test is easy or PCA accidentally finds the schema.")

    summary = {"by_method": by_method}
    verdict, msg = compute_verdict(summary)
    print(f"\nORACLE CHECKS PASSED.")
    print(f"=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "by_method": by_method, "per_seed": all_runs, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14t_tem_cross_env")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
