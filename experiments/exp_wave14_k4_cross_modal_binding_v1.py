"""K4 KILLER T2 — Cross-modal binding (text concepts bound with image embeddings).

K4 KILLER Tier-2 untested at substrate-product level. Hand-off v195
authorized this as one of the "untested KILLERs" to probe.

We use SYNTHETIC image embeddings (256-d random unit vectors, one per "image
concept") as a stand-in for a real image encoder. This is the operational
floor: if substrate can't even bind synthetic-image-embedding distributions to
text concepts, real image embeddings will fare worse. PASS at this floor
indicates the binding algebra survives cross-modal noise; FAIL kills K4 at
substrate level even before image-encoder choice is on the critical path.

Pipeline: for each (text_token, image_embedding) pair, project image_embedding
into substrate via a fixed random projection R: 256 -> N, bind text_atom *
proj(image) into bundle W. At query time, given text_atom alone, recover the
projected image; cosine vs. ground-truth proj. Compare to text-only baseline
(text bound to a random N-d vector — no cross-modal structure). Cross-modal
binding HARD-PASS iff cross-modal cosine > text-only baseline by at least
the pre-registered margin.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered.

Pre-reg:
    HARD-PASS: mean cross-modal recall cosine >= 0.50 AND lift over
               null-baseline >= +0.15 across >=4 of 5 seeds.
               -> K4 ✅ at synthetic floor; image-encoder choice is now the
               critical path.
    HARD-FAIL: mean cross-modal recall cosine < 0.20 OR lift over baseline
               < +0.05.
               -> K4 KILLER at substrate-binding level; no rescue from
               image-encoder choice.
    MIDDLE: any intermediate; report bands.

Pre-reg file: preregs/2026-05-24_wave14_k4_cross_modal_binding_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path
import numpy as np

try:
    import torch
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

REPO = Path(__file__).resolve().parent.parent

N_FULL = 4096
N_SMOKE = 512
N_IMG_DIM = 256                    # stand-in image encoder dim
M_PAIRS_FULL = 200
M_PAIRS_SMOKE = 40
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_MEAN_COS = 0.50
PASS_LIFT = 0.15
PASS_SEEDS = 4
FAIL_MEAN_COS = 0.20
FAIL_LIFT = 0.05


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing: raise ValueError(f"metrics missing required: {missing}")


def bind_circular(a, b):
    """Holographic binding via circular convolution (FFT)."""
    return torch.fft.irfft(torch.fft.rfft(a) * torch.fft.rfft(b), n=a.shape[-1])


def unbind_circular(c, a):
    """Holographic unbinding: c ⊛ a^-1 ≈ b."""
    A = torch.fft.rfft(a)
    A_inv = A.conj() / (A.abs() ** 2 + 1e-9)
    return torch.fft.irfft(torch.fft.rfft(c) * A_inv, n=c.shape[-1])


def cos(x, y):
    return float((x * y).sum() / (x.norm() * y.norm() + 1e-9))


def run_one_seed(seed, n, n_img, m_pairs, device="cpu"):
    g = torch.Generator(device=device).manual_seed(seed)
    text_atoms = torch.randn(m_pairs, n, generator=g, device=device) / math.sqrt(n)
    img_embeds = torch.randn(m_pairs, n_img, generator=g, device=device) / math.sqrt(n_img)
    # Fixed random projection R: n_img -> n
    R = torch.randn(n_img, n, generator=g, device=device) / math.sqrt(n_img)
    proj_imgs = img_embeds @ R  # m x n
    # Cross-modal bundle: sum_i text_i ⊛ proj_img_i
    bundle = torch.zeros(n, device=device)
    for i in range(m_pairs):
        bundle = bundle + bind_circular(text_atoms[i], proj_imgs[i])
    # Recover proj_img given text_atom
    cross_cos = []
    for i in range(m_pairs):
        rec = unbind_circular(bundle, text_atoms[i])
        cross_cos.append(cos(rec, proj_imgs[i]))
    # Null baseline: text bound to random N-d vectors (no cross-modal structure)
    null_vecs = torch.randn(m_pairs, n, generator=g, device=device) / math.sqrt(n)
    null_bundle = torch.zeros(n, device=device)
    for i in range(m_pairs):
        null_bundle = null_bundle + bind_circular(text_atoms[i], null_vecs[i])
    null_cos = []
    for i in range(m_pairs):
        rec = unbind_circular(null_bundle, text_atoms[i])
        null_cos.append(cos(rec, proj_imgs[i]))   # vs. proj_imgs[i] (this is the random recovery)
    mean_cross = sum(cross_cos) / len(cross_cos)
    mean_null = sum(null_cos) / len(null_cos)
    return {"mean_cross_cos": mean_cross, "mean_null_cos": mean_null,
            "lift": mean_cross - mean_null}


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("CROSS_MODAL_BIND_INCONCLUSIVE", "No seeds completed.")
    seeds_pass = 0
    means = []; lifts = []
    for s, d in per_seed.items():
        means.append(d["mean_cross_cos"]); lifts.append(d["lift"])
        if d["mean_cross_cos"] >= PASS_MEAN_COS and d["lift"] >= PASS_LIFT:
            seeds_pass += 1
    mean_cos_overall = sum(means)/len(means)
    mean_lift_overall = sum(lifts)/len(lifts)
    pts = ", ".join(f"s{s}:cos={d['mean_cross_cos']:.3f},lift={d['lift']:.3f}"
                    for s,d in per_seed.items())
    if seeds_pass >= PASS_SEEDS:
        return ("CROSS_MODAL_BIND_HARD_PASS",
                f"K4 cross-modal binding ACTIVE: {seeds_pass}/{len(per_seed)} seeds "
                f"pass cos>={PASS_MEAN_COS} AND lift>={PASS_LIFT}. mean_cos={mean_cos_overall:.3f} "
                f"mean_lift={mean_lift_overall:.3f}. {pts}.")
    if mean_cos_overall < FAIL_MEAN_COS or mean_lift_overall < FAIL_LIFT:
        return ("CROSS_MODAL_BIND_HARD_FAIL",
                f"K4 KILLER substrate-level: mean_cos={mean_cos_overall:.3f}<{FAIL_MEAN_COS} "
                f"OR mean_lift={mean_lift_overall:.3f}<{FAIL_LIFT}. {pts}.")
    return ("CROSS_MODAL_BIND_MIDDLE_BAND",
            f"Intermediate: seeds_pass={seeds_pass}/{len(per_seed)}, mean_cos={mean_cos_overall:.3f}, "
            f"mean_lift={mean_lift_overall:.3f}. {pts}.")


def self_test_verdict():
    def mk(seeds_data):
        ps = {}
        for i, (cos_v, lift_v) in enumerate(seeds_data):
            ps[str(i)] = {"mean_cross_cos": cos_v, "mean_null_cos": cos_v - lift_v, "lift": lift_v}
        return {"per_seed": ps}
    s_pass = mk([(0.65, 0.30)]*5)
    s_fail = mk([(0.10, 0.02)]*5)
    s_mid = mk([(0.55, 0.30), (0.55, 0.30), (0.35, 0.10), (0.35, 0.10), (0.35, 0.10)])
    s_inconc = {"per_seed": {}}
    cases = [(s_pass, "CROSS_MODAL_BIND_HARD_PASS"),
             (s_fail, "CROSS_MODAL_BIND_HARD_FAIL"),
             (s_mid, "CROSS_MODAL_BIND_MIDDLE_BAND"),
             (s_inconc, "CROSS_MODAL_BIND_INCONCLUSIVE")]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    n = N_SMOKE if smoke else N_FULL
    m_pairs = M_PAIRS_SMOKE if smoke else M_PAIRS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    device = "cuda" if (HAS_TORCH and torch.cuda.is_available()) else "cpu"
    config = {"mode": "smoke" if smoke else "full", "n": n, "n_img_dim": N_IMG_DIM,
              "m_pairs": m_pairs, "seeds": seeds, "device": device,
              "pass_mean_cos": PASS_MEAN_COS, "pass_lift": PASS_LIFT,
              "pass_seeds": PASS_SEEDS, "fail_mean_cos": FAIL_MEAN_COS,
              "fail_lift": FAIL_LIFT}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        r = run_one_seed(seed, n, N_IMG_DIM, m_pairs, device=device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: cos={r['mean_cross_cos']:.3f} null={r['mean_null_cos']:.3f} "
              f"lift={r['lift']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
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
    out_dir = get_output_dir("wave14_k4_cross_modal_binding_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_k4_cross_modal_binding_v1")
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


if __name__ == "__main__":
    sys.exit(main())
