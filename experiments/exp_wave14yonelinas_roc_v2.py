"""Honest test of Yonelinas dual-process - equal codebook sizes + ROC analysis.

wave14source_monitoring claimed Yonelinas dual-process VALIDATED based on
asymmetric codebook (8 sources vs 4096 contents). User correctly pushed back:
the apparent dissociation is largely a codebook-size artifact.

This v2 fixes it: EQUAL codebook sizes for sources AND items + Yonelinas-style
signal-detection ROC. Real dual-process predicts a SPECIFIC asymmetry in the
ROC curve (DPSD model, Yonelinas 1994/1999): high-confidence "yes" responses
come from threshold recollection, lower-confidence from continuous familiarity.

Also adds session_log.log_event() calls so the dashboard Tests tab populates.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Dashboard wiring: log events for the dashboard Tests tab
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not all(k in d for k in required):
        raise ValueError("missing")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty")


def compute_verdict(summary: dict) -> tuple[str, str]:
    """Real Yonelinas DPSD: dual-process predicts ROC asymmetry (z-ROC slope < 1).
    Pure familiarity (signal detection) predicts symmetric ROC (z-ROC slope = 1).
    """
    s = summary
    z_slope = s.get("z_roc_slope")
    rec_recall = s.get("recollection_accuracy")
    fam_d_prime = s.get("familiarity_d_prime")
    if z_slope is None:
        return ("YONELINAS_INCONCLUSIVE", "No ROC data.")
    if z_slope < 0.85 and rec_recall and rec_recall > 0.3:
        return ("YONELINAS_DUAL_PROCESS_VALIDATED",
                f"z-ROC slope = {z_slope:.2f} (< 0.85 indicates dual-process per DPSD model). "
                f"Recollection accuracy = {rec_recall:.2%}, familiarity d' = {fam_d_prime:.2f}. "
                f"The Yonelinas dissociation holds under PROPER test (equal codebooks + ROC).")
    if z_slope >= 0.85 and z_slope <= 1.15:
        return ("YONELINAS_PURE_FAMILIARITY",
                f"z-ROC slope = {z_slope:.2f} ~ 1.0 (symmetric ROC = single signal-detection process). "
                f"This is FAMILIARITY ONLY, not dual-process. Earlier 'dissociation' was "
                f"asymmetric-codebook artifact.")
    return ("YONELINAS_ANOMALOUS",
            f"z-ROC slope = {z_slope:.2f} outside [0.85, 1.15] dual-process or [0.85+, 1.15-] "
            f"single-process bands. Inspect data.")


def self_test_verdict() -> None:
    cases = [
        ({"z_roc_slope": 0.70, "recollection_accuracy": 0.5, "familiarity_d_prime": 1.2},
         "YONELINAS_DUAL_PROCESS_VALIDATED"),
        ({"z_roc_slope": 0.95, "recollection_accuracy": 0.1, "familiarity_d_prime": 1.5},
         "YONELINAS_PURE_FAMILIARITY"),
        ({"z_roc_slope": 1.50, "recollection_accuracy": 0.1, "familiarity_d_prime": 0.5},
         "YONELINAS_ANOMALOUS"),
        ({}, "YONELINAS_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: {actual} != {expected} for {s}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_bipolar(shape, gen):
    return 2.0 * (torch.rand(shape, generator=gen) > 0.5).float() - 1.0


def standard_normal_inv_cdf(p: float) -> float:
    """Approximate inverse normal CDF (probit) via Acklam's algorithm."""
    if p <= 0 or p >= 1:
        return float('inf') if p >= 1 else float('-inf')
    if p < 0.5:
        return -standard_normal_inv_cdf(1 - p)
    t = (-2 * math.log(1 - p)) ** 0.5
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1*t + c2*t*t) / (1 + d1*t + d2*t*t + d3*t*t*t)


def linear_fit(xs, ys):
    n = len(xs)
    xm = sum(xs) / n
    ym = sum(ys) / n
    num = sum((x - xm) * (y - ym) for x, y in zip(xs, ys))
    den = sum((x - xm) ** 2 for x in xs)
    slope = num / den if den > 0 else 1.0
    intercept = ym - slope * xm
    return slope, intercept


def run_one_alpha(N, n_codebook, K_stored, n_probes, seed, device):
    """Build triple-bound bundle with K_stored items. Equal codebook for source/cue/value.
    Compute ROC: at each confidence threshold, measure (hit_rate, false_alarm_rate).
    """
    gen = torch.Generator().manual_seed(seed)
    # Equal-sized codebook for sources, cues, contents
    sources = make_bipolar((n_codebook, N), gen).to(device)
    cues = make_bipolar((n_codebook, N), gen).to(device)
    contents = make_bipolar((n_codebook, N), gen).to(device)
    # Store K_stored random triples
    triple_idx = torch.randperm(n_codebook, generator=gen)[:K_stored].tolist()
    # Each stored item: bind (s_i, c_i, v_i) where i is from triple_idx
    bound = sources[triple_idx] * cues[triple_idx] * contents[triple_idx]
    bundle = torch.sign(bound.sum(dim=0) + 1e-9)

    stored_set = set(triple_idx)
    # OLD-NEW recognition test:
    # OLD probes: (s_i, c_i, v_i) for i in stored. Measure "old" confidence.
    # NEW probes: random (s, c, v) triples NOT in stored. Measure "old" confidence.
    # Confidence = strength of evidence that triple is in bundle = bundle · (s*c*v) / N
    n_old = min(n_probes // 2, K_stored)
    n_new = n_probes - n_old
    old_idx_sample = list(stored_set)[:n_old]
    # Generate n_new random NEW probes
    probe_gen = torch.Generator().manual_seed(seed * 31 + 7)
    new_triples = []
    while len(new_triples) < n_new:
        s = int(torch.randint(0, n_codebook, (1,), generator=probe_gen).item())
        c = int(torch.randint(0, n_codebook, (1,), generator=probe_gen).item())
        v = int(torch.randint(0, n_codebook, (1,), generator=probe_gen).item())
        # New = not all three indices match a stored triple
        # Since stored is identity-tied (s_i=c_i=v_i=i for i in triple_idx), we just need
        # to ensure the triple isn't a stored one
        if not (s == c == v and s in stored_set):
            new_triples.append((s, c, v))

    old_scores = []
    for i in old_idx_sample:
        probe = sources[i] * cues[i] * contents[i]
        score = float((bundle * probe).sum() / N)
        old_scores.append(score)
    new_scores = []
    for (s, c, v) in new_triples:
        probe = sources[s] * cues[c] * contents[v]
        score = float((bundle * probe).sum() / N)
        new_scores.append(score)

    # ROC: sweep threshold, compute (hit_rate, false_alarm_rate)
    all_scores = sorted(set(old_scores + new_scores))
    roc_points = []
    for t in all_scores:
        hits = sum(1 for s in old_scores if s >= t)
        fas = sum(1 for s in new_scores if s >= t)
        hit_rate = hits / max(1, len(old_scores))
        false_alarm = fas / max(1, len(new_scores))
        if 0 < hit_rate < 1 and 0 < false_alarm < 1:
            roc_points.append((false_alarm, hit_rate))
    # z-ROC slope (DPSD analysis)
    if len(roc_points) < 3:
        z_slope = None
        d_prime = None
    else:
        z_fa = [standard_normal_inv_cdf(fa) for fa, _ in roc_points]
        z_hit = [standard_normal_inv_cdf(hr) for _, hr in roc_points]
        z_slope, z_intercept = linear_fit(z_fa, z_hit)
        d_prime = z_intercept  # at fa=0 (z=0), hit z-score
    # Recollection accuracy: at low false-alarm (high threshold), is hit-rate intercept > 0?
    # DPSD: recollection contribution = hit_rate at false_alarm=0
    high_threshold_hits = [hr for fa, hr in roc_points if fa < 0.05]
    recollection_acc = max(high_threshold_hits) if high_threshold_hits else 0.0
    return {"K_stored": K_stored, "n_codebook": n_codebook,
            "z_roc_slope": z_slope,
            "familiarity_d_prime": d_prime,
            "recollection_accuracy": recollection_acc,
            "n_roc_points": len(roc_points)}


def main(smoke: bool = False) -> None:
    self_test_verdict()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if smoke:
        config = {"mode": "smoke", "N": 512, "n_codebook": 128, "K_stored": 30,
                  "n_probes": 100, "seeds": [17]}
    else:
        config = {"mode": "full", "N": 4096, "n_codebook": 4096, "K_stored": 200,
                  "n_probes": 1000, "seeds": [17, 23, 31, 41, 53]}
    print(f"wave14yonelinas_roc_v2. mode={config['mode']} device={device}", flush=True)
    log_event("experiment_started", name="wave14yonelinas_roc_v2",
              mode=config["mode"], queue="overnight_queue")

    t0 = time.monotonic()
    rows = []
    for seed in config["seeds"]:
        r = run_one_alpha(config["N"], config["n_codebook"], config["K_stored"],
                          config["n_probes"], seed, device)
        rows.append(r)
        print(f"  seed={seed}  z-ROC slope={r['z_roc_slope']}  d'={r['familiarity_d_prime']}  "
              f"rec_acc={r['recollection_accuracy']}", flush=True)
    elapsed = time.monotonic() - t0

    z_slopes = [r["z_roc_slope"] for r in rows if r["z_roc_slope"] is not None]
    if z_slopes:
        z_slope_mean = sum(z_slopes) / len(z_slopes)
    else:
        z_slope_mean = None
    rec_accs = [r["recollection_accuracy"] for r in rows]
    d_primes = [r["familiarity_d_prime"] for r in rows if r["familiarity_d_prime"] is not None]
    summary = {"z_roc_slope": z_slope_mean,
               "recollection_accuracy": sum(rec_accs) / len(rec_accs) if rec_accs else None,
               "familiarity_d_prime": sum(d_primes) / len(d_primes) if d_primes else None}
    verdict, msg = compute_verdict(summary)
    print(f"\n=== {verdict} ===\n{msg}", flush=True)
    log_event("experiment_outcome", name="wave14yonelinas_roc_v2",
              verdict=verdict, verdict_msg=msg, elapsed_s=elapsed,
              z_roc_slope=z_slope_mean)
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "config": config, "device": str(device),
               "per_seed": rows, "summary": summary}
    validate_metrics(metrics)
    out_dir = get_output_dir("wave14yonelinas_roc_v2")
    tmp = (out_dir / "metrics.json").with_suffix(".tmp")
    tmp.write_text(json.dumps(metrics, indent=2))
    os.replace(tmp, out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test_verdict()
        sys.exit(0)
    main(smoke="--smoke" in sys.argv)
