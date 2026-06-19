"""K8 KILLER T3 — Hierarchical concepts (concepts-of-concepts) — local CPU quick scoping.

K8 KILLER Tier-3: untested at substrate level. Hand-off v195 authorized as
one of the "untested KILLERs" to probe. R3 (hierarchical) closed at K>=16 but
the structural test of CONCEPT-OF-CONCEPTS — i.e. a 2-level hierarchy where
the top-level concept is a BUNDLE of mid-level concepts which are themselves
bundles of atoms — has not been probed at substrate level.

This is a QUICK LOCAL CPU SCOPING probe (Tier C, <60s, sub-minute) to decide
whether a heavier GPU probe is warranted. If the floor at small N already
demonstrates 2-level hierarchical recovery >> chance, K8 deserves a bigger
GPU sweep. If the floor is at chance, K8 is structurally weak at substrate
level (consistent with R3 closure) and not worth GPU budget.

Method: 3 atoms (a,b,c), 2 mid-concepts (M1=a⊛b, M2=b⊛c), 1 top-concept
(T = M1 + M2). Query: recover M1 from T then recover a/b from M1 via two
hops. Compare 2-level recovery accuracy to chance.

Per [[feedback-no-experiment-design-in-prompts]]: parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered.
Per Tier-C local_cpu_queue rules: <60s, single-config, scoping probe.

Pre-reg:
    HARD-PASS: 2-level recall cosine >= 0.30 AND >= 3x chance baseline
               across 5 seeds.
               -> K8 substrate has hierarchical structure at small N; warrants
               GPU envelope-expansion probe.
    HARD-FAIL: 2-level recall cosine < 0.05 OR < 1.5x chance baseline.
               -> K8 KILLER at substrate level; align with R3 closure;
               structurally weak.
    MIDDLE: any intermediate; report bands; GPU probe call is conditional.

Pre-reg file: preregs/2026-05-24_wave14_k8_hierarchical_concepts_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path
import numpy as np

REPO = Path(__file__).resolve().parent.parent

N = 1024
N_ATOMS_PER_MID = 4
N_MIDS = 4
N_QUERIES = 30
SEEDS = [7, 17, 23, 31, 41]

PASS_COS = 0.30
PASS_CHANCE_MULT = 3.0
FAIL_COS = 0.05
FAIL_CHANCE_MULT = 1.5


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing: raise ValueError(f"metrics missing required: {missing}")


def bind(a, b):
    return np.real(np.fft.irfft(np.fft.rfft(a) * np.fft.rfft(b), n=a.shape[-1]))


def unbind(c, a):
    A = np.fft.rfft(a)
    A_inv = np.conj(A) / (np.abs(A) ** 2 + 1e-9)
    return np.real(np.fft.irfft(np.fft.rfft(c) * A_inv, n=c.shape[-1]))


def cos(x, y):
    return float((x * y).sum() / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9))


def run_one_seed(seed, n):
    rng = np.random.default_rng(seed)
    # Build hierarchical structure: vocab atoms, mid-concepts as bundles, top as bundle of mids
    # Each mid: bundle of N_ATOMS_PER_MID atoms; top: bundle of all mids
    two_level_cos = []
    chance_cos = []
    for q in range(N_QUERIES):
        # New atom pool per query
        atoms = rng.standard_normal((N_MIDS, N_ATOMS_PER_MID, n)).astype(np.float64)
        atoms = atoms / (np.linalg.norm(atoms, axis=-1, keepdims=True) + 1e-9)
        # Each mid is a bundle of its atoms (binding to a per-atom slot tag)
        slot_tags = rng.standard_normal((N_ATOMS_PER_MID, n)).astype(np.float64)
        slot_tags = slot_tags / (np.linalg.norm(slot_tags, axis=-1, keepdims=True) + 1e-9)
        mids = np.zeros((N_MIDS, n), dtype=np.float64)
        for mi in range(N_MIDS):
            for ai in range(N_ATOMS_PER_MID):
                mids[mi] = mids[mi] + bind(slot_tags[ai], atoms[mi, ai])
            mids[mi] = mids[mi] / (np.linalg.norm(mids[mi]) + 1e-9)
        # Top: bundle of mids via slot tags
        mid_slots = rng.standard_normal((N_MIDS, n)).astype(np.float64)
        mid_slots = mid_slots / (np.linalg.norm(mid_slots, axis=-1, keepdims=True) + 1e-9)
        top = np.zeros(n, dtype=np.float64)
        for mi in range(N_MIDS):
            top = top + bind(mid_slots[mi], mids[mi])
        top = top / (np.linalg.norm(top) + 1e-9)
        # 2-level recovery: pick a random target mid index + atom index
        ti = rng.integers(0, N_MIDS)
        ai = rng.integers(0, N_ATOMS_PER_MID)
        # Step 1: recover mid_ti from top using mid_slot_ti
        rec_mid = unbind(top, mid_slots[ti])
        # Step 2: recover atom from rec_mid using slot_tags[ai]
        rec_atom = unbind(rec_mid, slot_tags[ai])
        target_atom = atoms[ti, ai]
        two_level_cos.append(cos(rec_atom, target_atom))
        # Chance: random unit vector against target_atom
        rnd_v = rng.standard_normal(n)
        chance_cos.append(cos(rnd_v, target_atom))
    return {"mean_2level_cos": float(np.mean(two_level_cos)),
            "mean_chance_cos": float(np.mean(np.abs(chance_cos))),
            "ratio_to_chance": float(np.mean(two_level_cos) /
                                       (max(np.mean(np.abs(chance_cos)), 1e-9)))}


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed: return ("HIER_CONCEPTS_INCONCLUSIVE", "No seeds.")
    coss = [d["mean_2level_cos"] for d in per_seed.values()]
    ratios = [d["ratio_to_chance"] for d in per_seed.values()]
    mean_cos = sum(coss)/len(coss)
    mean_ratio = sum(ratios)/len(ratios)
    pts = ", ".join(f"s{s}:cos={d['mean_2level_cos']:.3f},ratio={d['ratio_to_chance']:.2f}"
                    for s,d in per_seed.items())
    if mean_cos >= PASS_COS and mean_ratio >= PASS_CHANCE_MULT:
        return ("HIER_CONCEPTS_HARD_PASS",
                f"K8 2-level concepts SUPPORTED: mean cos={mean_cos:.3f}>={PASS_COS} "
                f"AND ratio={mean_ratio:.2f}>={PASS_CHANCE_MULT}x chance. {pts}.")
    if mean_cos < FAIL_COS or mean_ratio < FAIL_CHANCE_MULT:
        return ("HIER_CONCEPTS_HARD_FAIL",
                f"K8 KILLER substrate-level: mean cos={mean_cos:.3f}<{FAIL_COS} "
                f"OR ratio={mean_ratio:.2f}<{FAIL_CHANCE_MULT}x chance. {pts}.")
    return ("HIER_CONCEPTS_MIDDLE_BAND",
            f"Intermediate: cos={mean_cos:.3f}, ratio={mean_ratio:.2f}. {pts}.")


def self_test_verdict():
    def mk(rows):
        ps = {}
        for i, (c, r) in enumerate(rows):
            ps[str(i)] = {"mean_2level_cos": c, "mean_chance_cos": 0.03, "ratio_to_chance": r}
        return {"per_seed": ps}
    s_pass = mk([(0.45, 5.0)]*5)
    s_fail = mk([(0.02, 1.1)]*5)
    s_mid = mk([(0.15, 2.5)]*5)
    s_inconc = {"per_seed": {}}
    cases = [(s_pass, "HIER_CONCEPTS_HARD_PASS"),
             (s_fail, "HIER_CONCEPTS_HARD_FAIL"),
             (s_mid, "HIER_CONCEPTS_MIDDLE_BAND"),
             (s_inconc, "HIER_CONCEPTS_INCONCLUSIVE")]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    # K8 is local CPU only — no smoke/full split needed at this scope.
    # If smoke flag, reduce seeds to 1.
    seeds = SEEDS if not smoke else [SEEDS[0]]
    config = {"mode": "smoke" if smoke else "full", "n": N,
              "n_atoms_per_mid": N_ATOMS_PER_MID, "n_mids": N_MIDS,
              "n_queries": N_QUERIES, "seeds": seeds,
              "pass_cos": PASS_COS, "pass_chance_mult": PASS_CHANCE_MULT,
              "fail_cos": FAIL_COS, "fail_chance_mult": FAIL_CHANCE_MULT}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        r = run_one_seed(seed, N)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: 2level_cos={r['mean_2level_cos']:.3f} "
              f"chance_cos={r['mean_chance_cos']:.3f} ratio={r['ratio_to_chance']:.2f}", flush=True)
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
    out_dir = get_output_dir("wave14_k8_hierarchical_concepts_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_k8_hierarchical_concepts_v1")
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
