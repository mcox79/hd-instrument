"""Source monitoring as a binding axis (Yonelinas dual-process / Johnson 1993).

Holy-grail research finding: bind source-key as an extra factor at storage:
  m = sum_{j,k} s_j ⊙ c_{jk} ⊙ v_{jk}
where s_j = source key, c_jk = cue, v_jk = content.

Prediction: source-monitoring accuracy (recover j given s_j ⊙ c probe)
remains above chance well beyond standard alpha_c, because source is a
separable factor. The Yonelinas dual-process dissociation should emerge
from the algebra.

Materials analog: staggered transition in multi-component spin glass -
source-order parameter relaxes slower than item-order parameter.

Pre-reg: preregs/2026-05-20_wave14source_monitoring.md
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
    rows = summary.get("per_alpha", [])
    if not rows:
        return ("SRCMON_INCONCLUSIVE", "No data.")
    # Find dissociation: load where item-recall drops but source-recall stays
    dissociation_seen = any(
        r["item_recall"] < 0.5 and r["source_recall"] > 0.7
        for r in rows
    )
    full_collapse = any(
        r["item_recall"] < 0.3 and r["source_recall"] < 0.4
        for r in rows
    )
    if dissociation_seen:
        # find the load
        d = next(r for r in rows
                 if r["item_recall"] < 0.5 and r["source_recall"] > 0.7)
        return ("SRCMON_DISSOCIATION_VALIDATED",
                f"At alpha={d['alpha']:.3f}: item_recall={d['item_recall']:.2%}, "
                f"source_recall={d['source_recall']:.2%}. Yonelinas dual-process "
                f"dissociation EMERGES from algebra. Source monitoring works at "
                f"loads where item recall has collapsed.")
    if all(r["source_recall"] > 0.5 for r in rows):
        return ("SRCMON_BOTH_PRESERVED",
                "Source recall stays above 50% across all tested loads; need higher load to see dissociation.")
    if full_collapse:
        return ("SRCMON_NO_DISSOCIATION",
                "Both item and source recall collapse together. Algebra doesn't separate them.")
    return ("SRCMON_PARTIAL",
            "Per-alpha: " + ", ".join(f"a={r['alpha']:.2f}: item={r['item_recall']:.2f}/src={r['source_recall']:.2f}" for r in rows[:5]))


def self_test_verdict() -> None:
    cases = [
        ({"per_alpha": [{"alpha": 0.3, "item_recall": 0.2, "source_recall": 0.85}]},
         "SRCMON_DISSOCIATION_VALIDATED"),
        ({"per_alpha": [{"alpha": 0.3, "item_recall": 0.2, "source_recall": 0.2}]},
         "SRCMON_NO_DISSOCIATION"),
        ({"per_alpha": [{"alpha": 0.05, "item_recall": 0.9, "source_recall": 0.9}]},
         "SRCMON_BOTH_PRESERVED"),
        ({"per_alpha": []}, "SRCMON_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bipolar(shape, gen):
    return 2.0 * (torch.rand(shape, generator=gen) > 0.5).float() - 1.0


def run_one_alpha(N, K_sources, L_items, seed, device, codebook_size=4096):
    gen = torch.Generator().manual_seed(seed)
    sources = make_bipolar((K_sources, N), gen).to(device)
    # For each source, L (cue, value) pairs
    cues = make_bipolar((K_sources, L_items, N), gen).to(device)
    values = make_bipolar((K_sources, L_items, N), gen).to(device)
    # Triple-bound bundle: sum over j,k of s_j ⊙ c_jk ⊙ v_jk
    triple_bound = sources.unsqueeze(1) * cues * values  # (K_sources, L_items, N)
    bundle = triple_bound.sum(dim=(0, 1))  # (N,)
    bundle_signed = torch.sign(bundle + 1e-9)

    # Build a content codebook (random distractors + true values flattened)
    distractor_count = max(codebook_size - K_sources * L_items, K_sources * L_items)
    distractors = make_bipolar((distractor_count, N), gen).to(device)
    true_values_flat = values.reshape(-1, N)
    content_codebook = torch.cat([true_values_flat, distractors], dim=0)

    # Test 1: Item recall (cross-source). Probe with c alone -> retrieve v
    # Strategy: pick a (j, k); probe = bundle ⊙ c_jk (unbinds c, leaves s_j ⊙ v_jk + cross-talk)
    # Then look for closest in content_codebook
    n_probes = min(50, K_sources * L_items)
    item_correct = 0
    src_correct = 0
    probe_gen = torch.Generator().manual_seed(seed * 7 + 1)
    for p in range(n_probes):
        j = int(torch.randint(0, K_sources, (1,), generator=probe_gen).item())
        k = int(torch.randint(0, L_items, (1,), generator=probe_gen).item())
        c_jk = cues[j, k]
        v_jk = values[j, k]
        s_j = sources[j]
        # Item retrieval: probe = bundle * c (no source key) -> should reveal v ⊙ s mixed
        # Better: probe = bundle * c * s (unbind both) -> should reveal v_jk
        probe_with_source = bundle_signed * c_jk * s_j
        sims = content_codebook @ probe_with_source / N
        true_v_idx = j * L_items + k  # location in true_values_flat
        if int(sims.argmax()) == true_v_idx:
            item_correct += 1
        # Source monitoring: given (c, v) what source did it come from?
        # Probe each source: project bundle * c_jk * v_jk * s_candidate
        # Best matching source = predicted source
        scores = torch.stack([(bundle_signed * c_jk * v_jk * sources[s_cand]).sum()
                              for s_cand in range(K_sources)])
        pred_src = int(scores.argmax())
        if pred_src == j:
            src_correct += 1
    return {"item_recall": item_correct / n_probes,
            "source_recall": src_correct / n_probes,
            "alpha": (K_sources * L_items) / N}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "K_sources": 4,
                  "L_items_list": [10, 30, 60], "seeds": [17]}
    else:
        # Vary L per source; total alpha = K*L/N
        config = {"mode": "full", "N": 4096, "K_sources": 8,
                  "L_items_list": [20, 50, 100, 150, 250, 400, 600],
                  "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14source_monitoring. mode={config['mode']} device={device}", flush=True)

    t0 = time.monotonic()
    per_alpha = []
    for L in config["L_items_list"]:
        rows = []
        for seed in config["seeds"]:
            r = run_one_alpha(config["N"], config["K_sources"], L, seed, device)
            rows.append(r)
        item_mean = sum(r["item_recall"] for r in rows) / len(rows)
        src_mean = sum(r["source_recall"] for r in rows) / len(rows)
        alpha = (config["K_sources"] * L) / config["N"]
        per_alpha.append({"L": L, "alpha": alpha,
                           "item_recall": item_mean, "source_recall": src_mean})
        print(f"  L={L:4d} (alpha={alpha:.3f})  item_recall={item_mean:.3f}  "
              f"source_recall={src_mean:.3f}", flush=True)
    elapsed = time.monotonic() - t0

    summary = {"per_alpha": per_alpha}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_alpha": per_alpha, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14source_monitoring")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
