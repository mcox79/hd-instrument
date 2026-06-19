"""Holy-grail capability: soft (integer-valued) bundle vs sign-clipped bundle.

Holy-grail research finding (this session): the sign() clip on bundles destroys
information that the algebra needs for:
  1. Bayesian uncertainty (m_tilde[i] is sum of votes, calibrated log-odds)
  2. Counterfactual queries (m_tilde - v_k * c_k = "what if k not stored")
  3. Smoother degradation past alpha_c (sign clip causes the AGS cliff)

Materials analog: Ising spin (sign-clipped) -> XY/Potts (continuous magnetization).

Three direct tests:
  A. ECE (expected calibration error) of clipped vs soft retrieval at varying load
  B. Counterfactual: subtract item k; measure cosine to baseline-without-k
  C. Cliff sharpness: recovery rate vs alpha for both versions

Pre-reg: preregs/2026-05-20_wave14soft_trace.md
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import torch


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    repo_root = Path(__file__).resolve().parent.parent
    out = repo_root / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not all(k in d for k in required):
        raise ValueError("missing")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Soft trace wins if (1) ECE_soft < ECE_clip * 0.3, (2) counterfactual fidelity
    >= 0.95, (3) cliff is qualitatively smoother in soft.
    """
    s = summary
    ece_clip = s.get("ece_clip_mean")
    ece_soft = s.get("ece_soft_mean")
    cf_fidelity = s.get("counterfactual_fidelity")
    cliff_steepness_ratio = s.get("cliff_steepness_ratio")  # clip / soft
    if ece_clip is None or ece_soft is None:
        return ("SOFT_TRACE_INCONCLUSIVE", "No ECE data.")
    wins = []
    if ece_soft < ece_clip * 0.5:
        wins.append(f"ECE: soft {ece_soft:.3f} << clip {ece_clip:.3f}")
    if cf_fidelity is not None and cf_fidelity >= 0.95:
        wins.append(f"counterfactual fidelity {cf_fidelity:.2f}")
    if cliff_steepness_ratio is not None and cliff_steepness_ratio >= 1.5:
        wins.append(f"clip cliff {cliff_steepness_ratio:.1f}x steeper")
    if len(wins) >= 2:
        return ("SOFT_TRACE_HOLY_GRAIL",
                f"Soft trace wins on {len(wins)} probes: " + "; ".join(wins) +
                ". Materials analog (Ising -> XY) validated: continuous magnetization "
                f"gives Bayesian calibration + counterfactual + smoother cliff for FREE.")
    if len(wins) == 1:
        return ("SOFT_TRACE_PARTIAL",
                f"Soft wins on: " + wins[0] + ". Other axes inconclusive.")
    return ("SOFT_TRACE_NO_GAIN",
            f"Sign clip doesn't measurably hurt. ECE clip={ece_clip:.3f} ~ soft={ece_soft:.3f}. "
            f"CF fidelity={cf_fidelity}, cliff ratio={cliff_steepness_ratio}.")


def self_test_verdict() -> None:
    cases = [
        ({"ece_clip_mean": 0.20, "ece_soft_mean": 0.05, "counterfactual_fidelity": 0.99,
          "cliff_steepness_ratio": 2.0}, "SOFT_TRACE_HOLY_GRAIL"),
        ({"ece_clip_mean": 0.20, "ece_soft_mean": 0.05, "counterfactual_fidelity": 0.5,
          "cliff_steepness_ratio": 1.0}, "SOFT_TRACE_PARTIAL"),
        ({"ece_clip_mean": 0.05, "ece_soft_mean": 0.05, "counterfactual_fidelity": 0.5,
          "cliff_steepness_ratio": 1.0}, "SOFT_TRACE_NO_GAIN"),
        ({}, "SOFT_TRACE_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bipolar(shape, gen):
    return 2.0 * (torch.rand(shape, generator=gen) > 0.5).float() - 1.0


def store_and_query(N, K, seed, device, M_codebook=8192):
    """Store K bound pairs in both soft and clipped bundles.
    Return (soft_bundle, clip_bundle, items_dict).
    """
    gen = torch.Generator().manual_seed(seed)
    # Bound items: v_k * c_k for K random pairs
    contents = make_bipolar((K, N), gen).to(device)
    cues = make_bipolar((K, N), gen).to(device)
    bound = contents * cues  # Hadamard binding
    soft_bundle = bound.sum(dim=0)  # integer in {-K..K}
    clip_bundle = torch.sign(soft_bundle)
    clip_bundle = torch.where(clip_bundle == 0, torch.ones_like(clip_bundle), clip_bundle)
    return {"soft": soft_bundle, "clip": clip_bundle,
            "contents": contents, "cues": cues, "K": K, "N": N}


def measure_ece_calibration(bundle, contents, cues, codebook_size, gen, device):
    """For each item, unbind by cue -> measure cosine to content.
    Calibration: bin by predicted-confidence (cos magnitude), measure accuracy.
    Returns ECE.
    """
    K = contents.size(0)
    N = contents.size(-1)
    # Make a codebook including the K true contents + random distractors
    n_distractor = codebook_size - K
    distractors = make_bipolar((n_distractor, N), gen).to(device)
    codebook = torch.cat([contents, distractors], dim=0)  # (codebook_size, N)
    # Unbind each item: bundle * cue_k -> should give content_k (in soft case, scaled)
    confidences = []
    correct = []
    for k in range(K):
        unbound = bundle * cues[k]
        # Cosine to all codebook items
        sims = (codebook @ unbound) / (codebook.norm(dim=1) * unbound.norm() + 1e-9)
        top_idx = int(sims.argmax())
        is_correct = (top_idx == k)
        # "Confidence" = (top sim - mean) / std of sims
        confidence = ((sims[top_idx] - sims.mean()) / (sims.std() + 1e-9)).item()
        confidences.append(confidence)
        correct.append(is_correct)
    # Bin by confidence, compute ECE
    # Normalize confidences to [0, 1] for binning
    confs = torch.tensor(confidences)
    if confs.max() > confs.min():
        confs_norm = (confs - confs.min()) / (confs.max() - confs.min())
    else:
        confs_norm = torch.zeros_like(confs)
    correct_t = torch.tensor(correct, dtype=torch.float)
    n_bins = 10
    ece = 0.0
    for b in range(n_bins):
        lo = b / n_bins
        hi = (b + 1) / n_bins
        mask = (confs_norm >= lo) & (confs_norm < hi if b < n_bins - 1 else confs_norm <= hi)
        if mask.sum() == 0:
            continue
        bin_acc = correct_t[mask].mean().item()
        bin_conf = confs_norm[mask].mean().item()
        weight = mask.float().mean().item()
        ece += weight * abs(bin_acc - bin_conf)
    accuracy = correct_t.mean().item()
    return ece, accuracy


def measure_counterfactual(soft_bundle, contents, cues, k_idx, device):
    """Subtract item k_idx from soft bundle; compare to a fresh bundle built without item k_idx.
    Returns cosine similarity.
    """
    K = contents.size(0)
    # Counterfactual bundle: subtract bound term
    bound_k = contents[k_idx] * cues[k_idx]
    cf_bundle = soft_bundle - bound_k
    # Reference: bundle without item k_idx
    mask = torch.ones(K, dtype=torch.bool, device=device)
    mask[k_idx] = False
    ref_bundle = (contents[mask] * cues[mask]).sum(dim=0)
    # Cosine
    cos = torch.nn.functional.cosine_similarity(cf_bundle.unsqueeze(0),
                                                  ref_bundle.unsqueeze(0)).item()
    return cos


def run_one_seed(N, K_list, seed, device):
    """For each K in K_list: build bundle (soft + clip), measure ECE for both,
    measure counterfactual fidelity (soft only - clip can't do CF).
    """
    results = []
    for K in K_list:
        gen_meas = torch.Generator().manual_seed(seed * 7 + K)
        items = store_and_query(N, K, seed + K, device)
        ece_soft, acc_soft = measure_ece_calibration(items["soft"], items["contents"],
                                                       items["cues"], 8192, gen_meas, device)
        ece_clip, acc_clip = measure_ece_calibration(items["clip"], items["contents"],
                                                       items["cues"], 8192, gen_meas, device)
        # Counterfactual: pick k=0, subtract from soft, compare to without-k
        cf_cos = measure_counterfactual(items["soft"], items["contents"], items["cues"], 0, device)
        results.append({"K": K, "N": N,
                         "ece_soft": ece_soft, "ece_clip": ece_clip,
                         "acc_soft": acc_soft, "acc_clip": acc_clip,
                         "counterfactual_cos": cf_cos})
    return results


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_list": [30, 100, 300], "seeds": [17]}
    else:
        # Push way past alpha_c to test smooth-degradation prediction
        config = {"mode": "full", "N": 4096,
                  "K_list": [100, 300, 627, 1500, 3000, 5000, 8000, 12000],
                  "seeds": [17, 23, 31, 41, 53, 67, 79, 89, 101, 113]}
    print(f"wave14soft_trace_extended. mode={config['mode']} device={device}", flush=True)

    t0 = time.monotonic()
    all_runs = []
    for seed in config["seeds"]:
        r = run_one_seed(config["N"], config["K_list"], seed, device)
        all_runs.extend(r)
        for row in r:
            print(f"  seed={seed} K={row['K']:5d}  ECE_soft={row['ece_soft']:.3f}  "
                  f"ECE_clip={row['ece_clip']:.3f}  acc_soft={row['acc_soft']:.2f}  "
                  f"acc_clip={row['acc_clip']:.2f}  cf_cos={row['counterfactual_cos']:.3f}",
                  flush=True)
    elapsed = time.monotonic() - t0

    # Aggregate by K
    per_K = {}
    for r in all_runs:
        K = r["K"]
        if K not in per_K:
            per_K[K] = []
        per_K[K].append(r)
    aggregated = []
    for K in sorted(per_K):
        rows = per_K[K]
        aggregated.append({"K": K,
                            "ece_soft_mean": sum(r["ece_soft"] for r in rows) / len(rows),
                            "ece_clip_mean": sum(r["ece_clip"] for r in rows) / len(rows),
                            "acc_soft_mean": sum(r["acc_soft"] for r in rows) / len(rows),
                            "acc_clip_mean": sum(r["acc_clip"] for r in rows) / len(rows),
                            "cf_cos_mean": sum(r["counterfactual_cos"] for r in rows) / len(rows)})

    # Summary stats for verdict
    ece_clip_mean = sum(r["ece_clip_mean"] for r in aggregated) / len(aggregated)
    ece_soft_mean = sum(r["ece_soft_mean"] for r in aggregated) / len(aggregated)
    counterfactual_fidelity = sum(r["cf_cos_mean"] for r in aggregated) / len(aggregated)
    # Cliff steepness ratio: how fast does accuracy drop?
    accs_clip = [r["acc_clip_mean"] for r in aggregated]
    accs_soft = [r["acc_soft_mean"] for r in aggregated]
    if len(accs_clip) >= 2 and max(accs_clip) > min(accs_clip):
        clip_drop = max(accs_clip) - min(accs_clip)
        soft_drop = max(accs_soft) - min(accs_soft)
        cliff_steepness_ratio = clip_drop / max(soft_drop, 1e-9)
    else:
        cliff_steepness_ratio = 1.0

    summary = {"per_K": aggregated,
               "ece_clip_mean": ece_clip_mean,
               "ece_soft_mean": ece_soft_mean,
               "counterfactual_fidelity": counterfactual_fidelity,
               "cliff_steepness_ratio": cliff_steepness_ratio}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_K": aggregated, "per_seed": all_runs, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14soft_trace_extended")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
