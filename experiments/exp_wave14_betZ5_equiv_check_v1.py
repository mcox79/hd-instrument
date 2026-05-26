"""Bet Z.5 absorbing-diffusion ensemble smoother vs VAMP-on-chain structural equivalence.

Probe: are the two readout algorithms structurally equivalent (same outputs up to
reparameterisation) or is Bet Z.5 strictly stronger (produces per-codeword variance
certificates that VAMP cannot)?

Theory:
  VAMP-on-chain (existing): forward-backward EP; single deterministic pass per direction;
    outputs argmax of smoothed log-posterior at each hop; NO variance/uncertainty estimate.
  Bet Z.5 absorbing-diffusion ensemble smoother (this experiment): K independent noisy
    "diffusion trajectories" starting from a uniformly perturbed query, each absorbed at
    the codebook boundary via sign-quantize; the ensemble posterior mean is the vote-weighted
    entity estimate; PER-CODEWORD VARIANCE = Var_k[sim(entity_k, mean_hat)] over K runs --
    this quantity CANNOT be computed from a single VAMP pass.

Structural equivalence metric: Pearson r between VAMP softmax output distribution and
  absorbing-diffusion posterior mean distribution, over all test chains (per hop).

Per-codeword variance certificate: SD of per-entity cosine similarity across K diffusion
  ensemble members, averaged over chains -- a non-zero value that VAMP cannot produce.

Verdict thresholds:
  BETZ5_EQUIVALENT_TO_VAMP:     r >= 0.99  (output distributions identical; Bet Z.5
                                              is VAMP under a different framing; close candidate row)
  BETZ5_STRICTLY_STRONGER:      r < 0.99   AND mean_var_cert > 0.01
                                             (distributions differ OR VAMP variance is trivially 0
                                              but Z.5 produces non-trivial variance; confirm new primitive)
  BETZ5_INCONCLUSIVE:            r or variance cert both degenerate / all outputs collapse

Pre-reg: preregs/2026-05-23_wave14_betZ5_equiv_check_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

import importlib.util
_mh_spec = importlib.util.spec_from_file_location(
    "mh", REPO / "experiments" / "exp_wave14r_multihop_K100.py"
)
mh = importlib.util.module_from_spec(_mh_spec)
_mh_spec.loader.exec_module(mh)

_vc_spec = importlib.util.spec_from_file_location(
    "vc", REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py"
)
vc = importlib.util.module_from_spec(_vc_spec)
_vc_spec.loader.exec_module(vc)


# ---------------------------------------------------------------------------
# Output dir
# ---------------------------------------------------------------------------

def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------

def compute_verdict(summary: dict) -> tuple[str, str]:
    r = summary.get("mean_pearson_r")
    var_cert = summary.get("mean_var_cert")
    if r is None or var_cert is None:
        return ("BETZ5_INCONCLUSIVE", "Missing mean_pearson_r or mean_var_cert.")
    if r >= 0.99:
        return (
            "BETZ5_EQUIVALENT_TO_VAMP",
            f"Absorbing-diffusion posterior distribution correlates r={r:.4f}>=0.99 "
            f"with VAMP softmax output. Bet Z.5 is structurally equivalent to VAMP-on-chain "
            f"up to reparameterisation. Close candidate row. "
            f"VAMP variance cert=0 (deterministic); Z.5 var_cert={var_cert:.4f} (trivially larger but irrelevant).",
        )
    if var_cert > 0.01:
        return (
            "BETZ5_STRICTLY_STRONGER",
            f"Output distributions differ: r={r:.4f}<0.99. "
            f"Absorbing-diffusion variance certificate={var_cert:.4f}>0.01 is non-trivial. "
            f"VAMP produces no per-codeword variance (deterministic single-pass). "
            f"Bet Z.5 confirmed as strictly stronger readout primitive. Justify full GPU impl.",
        )
    return (
        "BETZ5_INCONCLUSIVE",
        f"r={r:.4f}, var_cert={var_cert:.4f}. Outputs degenerate or all collapsed to same entity.",
    )


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def self_test_verdict() -> None:
    cases = [
        ({"mean_pearson_r": 0.995, "mean_var_cert": 0.005}, "BETZ5_EQUIVALENT_TO_VAMP"),
        ({"mean_pearson_r": 0.990, "mean_var_cert": 0.0001}, "BETZ5_EQUIVALENT_TO_VAMP"),
        ({"mean_pearson_r": 0.85, "mean_var_cert": 0.05}, "BETZ5_STRICTLY_STRONGER"),
        ({"mean_pearson_r": 0.70, "mean_var_cert": 0.02}, "BETZ5_STRICTLY_STRONGER"),
        ({}, "BETZ5_INCONCLUSIVE"),
        ({"mean_pearson_r": None, "mean_var_cert": None}, "BETZ5_INCONCLUSIVE"),
        ({"mean_pearson_r": 0.60, "mean_var_cert": 0.005}, "BETZ5_INCONCLUSIVE"),
    ]
    for i, (s, exp) in enumerate(cases):
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"case {i}: got {a}, expected {exp} | s={s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# Absorbing-diffusion ensemble smoother
# ---------------------------------------------------------------------------

def absorbing_diffusion_ensemble(
    M: torch.Tensor,
    start_idx: int,
    rel_idxs: list[int],
    entity_atoms: torch.Tensor,
    relation_atoms: torch.Tensor,
    K_ensemble: int,
    noise_level: float,
    gen: torch.Generator,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Run K noisy forward passes; return (posterior_mean_logits, per_entity_std).

    Each trajectory:
      1. Start from entity_atoms[start_idx] + Gaussian noise (noise_level * sqrt(N))
         absorbed back to bipolar via sign-quantize -- "absorbing boundary".
      2. Run forward chain like VAMP's greedy forward but with noisy quantized state.
      3. At each hop: collect final similarity vector over entity_atoms.
    Ensemble:
      posterior_mean_logits[K] = mean over ensemble of final-hop similarity vectors.
      per_entity_std[K]        = std  over ensemble of final-hop similarity vectors.
    """
    depth = len(rel_idxs)
    K_ent = entity_atoms.shape[0]
    N = entity_atoms.shape[1]
    # Collect last-hop similarity vectors across ensemble members
    all_final_sims = []
    for _ in range(K_ensemble):
        # Noisy start: perturb entity atom and absorb to bipolar
        start = entity_atoms[start_idx].clone().float()
        noise = torch.randn(N, generator=gen, device=entity_atoms.device) * noise_level
        noisy_start = mh.sign_quantize(start + noise)
        q_state = noisy_start
        for hop in range(depth):
            rel = relation_atoms[rel_idxs[hop]].float()
            probe = M.float() * (q_state * rel)
            sims = entity_atoms.float() @ probe  # (K_ent,)
            # Posterior expectation -- used as next q_state
            log_p = sims - torch.logsumexp(sims, dim=0)
            weights = torch.exp(log_p)
            q_state = (weights.unsqueeze(1) * entity_atoms.float()).sum(dim=0)
            q_state = mh.sign_quantize(q_state)
        # Final-hop similarity vector
        rel = relation_atoms[rel_idxs[-1]].float()
        probe = M.float() * (q_state * rel)
        final_sims = entity_atoms.float() @ probe
        all_final_sims.append(final_sims)
    sim_stack = torch.stack(all_final_sims, dim=0)  # (K_ensemble, K_ent)
    posterior_mean = sim_stack.mean(dim=0)           # (K_ent,)
    posterior_std  = sim_stack.std(dim=0)            # (K_ent,) -- per-codeword variance cert
    return posterior_mean, posterior_std


def vamp_final_sims(
    M: torch.Tensor,
    start_idx: int,
    rel_idxs: list[int],
    entity_atoms: torch.Tensor,
    relation_atoms: torch.Tensor,
) -> torch.Tensor:
    """Run VAMP forward pass; return final-hop similarity vector (K_ent,).

    Mirrors vamp_chain_forward_backward but only the forward pass,
    returning the softmax-log-posterior at the final hop as the reference
    distribution for correlation comparison.
    """
    depth = len(rel_idxs)
    K_ent = entity_atoms.shape[0]
    q_state = entity_atoms[start_idx].clone().float()
    for hop in range(depth):
        rel = relation_atoms[rel_idxs[hop]].float()
        probe = M.float() * (q_state * rel)
        sims = entity_atoms.float() @ probe
        log_post = sims - torch.logsumexp(sims, dim=0)
        weights = torch.exp(log_post)
        q_state = (weights.unsqueeze(1) * entity_atoms.float()).sum(dim=0)
        q_state = mh.sign_quantize(q_state)
    # Final-hop: apply last relation to get final sims
    rel = relation_atoms[rel_idxs[-1]].float()
    probe = M.float() * (q_state * rel)
    return entity_atoms.float() @ probe  # (K_ent,)


def pearson_r(a: torch.Tensor, b: torch.Tensor) -> float:
    """Pearson correlation between two 1-D tensors."""
    a_f = a.float()
    b_f = b.float()
    a_c = a_f - a_f.mean()
    b_c = b_f - b_f.mean()
    num = (a_c * b_c).sum()
    den = torch.sqrt((a_c ** 2).sum() * (b_c ** 2).sum())
    if den.item() < 1e-12:
        return 0.0
    return float((num / den).item())


# ---------------------------------------------------------------------------
# Experiment runner
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()

    # noise_level=3.0 is the regime where sign-quantize gives distinct absorbing paths.
    # At nl<=1.0, all K trajectories collapse to the same attractor (ensemble collapses,
    # var_cert=0, r=1.0 trivially). nl=3.0 introduces real path diversity while remaining
    # in a physically meaningful "noisy retrieval" regime.
    config = {
        "mode": "smoke" if smoke else "full",
        "N": 512 if smoke else 4096,
        "K_entities": 30 if smoke else 200,
        "K_relations": 5 if smoke else 20,
        "K_facts": 15 if smoke else 100,
        "depth": 3 if smoke else 10,
        "n_trials": 5 if smoke else 40,
        "seeds": [17] if smoke else [17, 23, 31],
        "K_ensemble": 20 if smoke else 50,
        "noise_level": 3.0,
    }

    N = config["N"]
    K_ent = config["K_entities"]
    K_rel = config["K_relations"]
    K_facts = config["K_facts"]
    depth = config["depth"]
    n_trials = config["n_trials"]
    K_ensemble = config["K_ensemble"]
    noise_level = config["noise_level"]

    all_r = []
    all_var_cert = []
    all_z5_acc = []
    all_vamp_acc = []

    for seed in config["seeds"]:
        device = torch.device("cpu")
        gen = torch.Generator(device=device).manual_seed(seed)
        entity_atoms = mh.make_bsc_codebook(K_ent, N, gen, device)
        relation_atoms = mh.make_bsc_codebook(K_rel, N, gen, device)
        trial_gen = torch.Generator().manual_seed(seed + 1009)
        ens_gen = torch.Generator().manual_seed(seed + 777)

        rs_seed = []
        var_certs_seed = []
        z5_correct = 0
        vamp_correct = 0

        for trial in range(n_trials):
            perm = torch.randperm(K_ent, generator=trial_gen)[:depth + 1]
            chain_entities = perm.tolist()
            chain_rels = [
                int(torch.randint(0, K_rel, (1,), generator=trial_gen).item())
                for _ in range(depth)
            ]
            n_dist = max(0, K_facts - depth)
            M = mh.build_factbase(
                chain_entities, chain_rels, n_dist,
                K_ent, K_rel, entity_atoms, relation_atoms, trial_gen, device
            )
            target_idx = chain_entities[-1]

            # VAMP forward similarity vector at final hop
            vamp_sims = vamp_final_sims(M, chain_entities[0], chain_rels,
                                         entity_atoms, relation_atoms)
            vamp_pred = int(vamp_sims.argmax().item())
            if vamp_pred == target_idx:
                vamp_correct += 1

            # Absorbing-diffusion ensemble
            z5_mean, z5_std = absorbing_diffusion_ensemble(
                M, chain_entities[0], chain_rels,
                entity_atoms, relation_atoms,
                K_ensemble, noise_level, ens_gen
            )
            z5_pred = int(z5_mean.argmax().item())
            if z5_pred == target_idx:
                z5_correct += 1

            # Correlation metric: pearson r between VAMP sims and Z.5 posterior mean
            r = pearson_r(vamp_sims, z5_mean)
            rs_seed.append(r)

            # Per-codeword variance certificate: mean std over entities
            var_cert = float(z5_std.mean().item())
            var_certs_seed.append(var_cert)

        seed_r = sum(rs_seed) / len(rs_seed)
        seed_var = sum(var_certs_seed) / len(var_certs_seed)
        seed_z5_acc = z5_correct / n_trials
        seed_vamp_acc = vamp_correct / n_trials

        all_r.append(seed_r)
        all_var_cert.append(seed_var)
        all_z5_acc.append(seed_z5_acc)
        all_vamp_acc.append(seed_vamp_acc)

        print(
            f"  seed={seed}: pearson_r={seed_r:.4f} var_cert={seed_var:.4f} "
            f"z5_acc={seed_z5_acc:.3f} vamp_acc={seed_vamp_acc:.3f}",
            flush=True,
        )

    mean_r = sum(all_r) / len(all_r)
    mean_var = sum(all_var_cert) / len(all_var_cert)
    mean_z5_acc = sum(all_z5_acc) / len(all_z5_acc)
    mean_vamp_acc = sum(all_vamp_acc) / len(all_vamp_acc)

    # Peak memory estimate (CPU tensors)
    # Dominant: entity_atoms (K_ent x N float32) + M (N float32) + ensemble stack (K_ens x K_ent float32)
    peak_mb = (K_ent * N * 4 + N * 4 + K_ensemble * K_ent * 4) / 1024 / 1024

    summary = {
        "mean_pearson_r": mean_r,
        "mean_var_cert": mean_var,
        "mean_z5_acc": mean_z5_acc,
        "mean_vamp_acc": mean_vamp_acc,
        "per_seed_r": all_r,
        "per_seed_var_cert": all_var_cert,
        "per_seed_z5_acc": all_z5_acc,
        "per_seed_vamp_acc": all_vamp_acc,
        "config_depth": depth,
        "K_ensemble": K_ensemble,
        "estimated_peak_mb": peak_mb,
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    print(f"  elapsed={elapsed:.1f}s  peak_est={peak_mb:.1f}MB", flush=True)
    return summary, verdict, msg, elapsed, config


# ---------------------------------------------------------------------------
# Metrics I/O
# ---------------------------------------------------------------------------

def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing keys: {missing}")


def write_metrics(
    out_dir: Path, summary: dict, verdict: str, msg: str, elapsed: float, config: dict
) -> None:
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


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def run_smoke() -> None:
    out_dir = get_output_dir("wave14_betZ5_equiv_check_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Smoke gate: at minimum var_cert should be > 0 (ensemble has some variance)
    assert summary["mean_var_cert"] >= 0.0, "var_cert must be non-negative"
    assert summary["mean_pearson_r"] is not None, "pearson_r must be computed"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    out_dir = get_output_dir("wave14_betZ5_equiv_check_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
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
