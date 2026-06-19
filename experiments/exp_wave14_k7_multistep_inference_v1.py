"""K7 KILLER T2 — Multi-step inference (deduction over chained retrievals).

K7 KILLER Tier-2: substrate does multi-hop retrieval through pre-stored chains
(Cap 8 VAMP-on-chain ✅) but the harder claim is DEDUCTION — given facts
A→B, B→C, query A→? should yield C without an explicit A→C edge stored.

Test harness:
  - Store M facts of form (subject_i, relation, object_i) as bundles
    bundle_i = subject_i ⊛ relation ⊛ object_i.
  - For deduction, given subject_A and relation chain (R1, R2, ..., R_d), follow
    the chain step by step: at each step, unbind to recover next object;
    treat that object as next subject for the next relation. Repeat d steps.
  - Measure accuracy at depth d in {1, 2, 3, 4, 5}.

If accuracy decays slower than the geometric-exponential law per existing-data
analysis (Finding 1: r=0.97 per-hop), substrate has DEDUCTION beyond chained
retrieval. If it tracks pure-retrieval decay, K7 is just multi-hop retrieval
relabeled.

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev autonomy.
Per [[feedback-no-smoke]]: HARD-PASS/HARD-FAIL bands pre-registered.

Pre-reg:
    HARD-PASS: accuracy at depth=5 >= 0.50 AND per-step decay rate r >= 0.85
               (substrate maintains coherent deduction over 5 hops).
               -> K7 row promoted; substrate has deduction capability beyond
               pure retrieval.
    HARD-FAIL: accuracy at depth=5 < 0.10 OR per-step r < 0.65
               (deduction collapses; substrate behaves as additive-noise chain).
               -> K7 KILLER at this envelope; multi-step inference REJECTED.
    MIDDLE: any intermediate; report bands.

Pre-reg file: preregs/2026-05-24_wave14_k7_multistep_inference_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path

try:
    import torch
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

REPO = Path(__file__).resolve().parent.parent

N_FULL = 8192
N_SMOKE = 1024
N_ENTITIES_FULL = 100
N_ENTITIES_SMOKE = 30
DEPTHS_FULL = [1, 2, 3, 4, 5]
DEPTHS_SMOKE = [1, 2, 3]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_QUERIES_FULL = 50
N_QUERIES_SMOKE = 10

PASS_ACC_AT_5 = 0.50
PASS_R_PER_STEP = 0.85
FAIL_ACC_AT_5 = 0.10
FAIL_R_PER_STEP = 0.65


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
    return torch.fft.irfft(torch.fft.rfft(a) * torch.fft.rfft(b), n=a.shape[-1])


def unbind(c, a):
    A = torch.fft.rfft(a)
    A_inv = A.conj() / (A.abs() ** 2 + 1e-9)
    return torch.fft.irfft(torch.fft.rfft(c) * A_inv, n=c.shape[-1])


def cleanup_to_entity(vec, entities):
    """Pick the closest entity by cosine."""
    sims = entities @ vec / (entities.norm(dim=1) * vec.norm() + 1e-9)
    return int(sims.argmax())


def run_one_seed(seed, n, n_ents, depths, n_queries, device="cpu"):
    g = torch.Generator(device=device).manual_seed(seed)
    entities = torch.randn(n_ents, n, generator=g, device=device) / math.sqrt(n)
    relation = torch.randn(n, generator=g, device=device) / math.sqrt(n)
    # Random successor: chain a chain of length max(depths)
    max_d = max(depths)
    # Generate a deterministic chain: 0 -> 1 -> 2 -> ... -> max_d
    # (we'll do n_queries different starting points by shifting)
    bundle = torch.zeros(n, device=device)
    chains = []
    for q in range(n_queries):
        # Build a chain of unique entities for this query
        perm = torch.randperm(n_ents, generator=g, device=device)[:max_d + 1]
        chains.append(perm.tolist())
        for i in range(max_d):
            subj = entities[perm[i]]
            obj = entities[perm[i + 1]]
            bundle = bundle + bind(bind(subj, relation), obj)
    # Decode chains
    depth_correct = {d: 0 for d in depths}
    for chain in chains:
        cur_vec = entities[chain[0]]
        for step in range(max_d):
            # Recover obj from bundle: bundle contains subj ⊛ rel ⊛ obj
            # query: bundle ⊛ (subj ⊛ rel)^-1
            key = bind(cur_vec, relation)
            rec = unbind(bundle, key)
            cur_idx = cleanup_to_entity(rec, entities)
            cur_vec = entities[cur_idx]
            if (step + 1) in depths:
                if cur_idx == chain[step + 1]:
                    depth_correct[step + 1] += 1
    per_depth_acc = {d: depth_correct[d] / n_queries for d in depths}
    # Per-step decay: fit r where acc(d) = acc(1) * r^(d-1)
    if 1 in per_depth_acc and per_depth_acc[1] > 0:
        # Take last depth for which acc > 0 to fit
        log_vals = []
        for d in depths:
            if per_depth_acc[d] > 0:
                log_vals.append((d, math.log(per_depth_acc[d])))
        if len(log_vals) >= 2:
            xs = [v[0] for v in log_vals]; ys = [v[1] for v in log_vals]
            mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
            num = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
            den = sum((x-mx)**2 for x in xs)
            slope = num/den if den else 0.0
            r_per_step = math.exp(slope)
        else:
            r_per_step = 0.0
    else:
        r_per_step = 0.0
    return {"per_depth_acc": per_depth_acc, "r_per_step": r_per_step}


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("MULTISTEP_INFER_INCONCLUSIVE", "No seeds completed.")
    acc_at_5s = []; rs = []
    pts_list = []
    for s, d in per_seed.items():
        pda = d["per_depth_acc"]
        a5 = pda.get(5)
        if a5 is None: a5 = pda.get("5")
        if a5 is None:
            # smoke depths max < 5; use max-depth as proxy
            keys_int = [int(k) for k in pda]
            mx = max(keys_int)
            a5 = pda.get(mx)
            if a5 is None: a5 = pda.get(str(mx))
        if a5 is None: a5 = 0.0
        acc_at_5s.append(a5)
        rs.append(d["r_per_step"])
        pts_list.append(f"s{s}:acc_d5={a5:.3f},r={d['r_per_step']:.3f}")
    mean_a5 = sum(acc_at_5s)/len(acc_at_5s)
    mean_r = sum(rs)/len(rs)
    pts = ", ".join(pts_list)
    if mean_a5 >= PASS_ACC_AT_5 and mean_r >= PASS_R_PER_STEP:
        return ("MULTISTEP_INFER_HARD_PASS",
                f"K7 multi-step deduction ACTIVE: acc@d5={mean_a5:.3f}>={PASS_ACC_AT_5} "
                f"AND r_per_step={mean_r:.3f}>={PASS_R_PER_STEP}. {pts}.")
    if mean_a5 < FAIL_ACC_AT_5 or mean_r < FAIL_R_PER_STEP:
        return ("MULTISTEP_INFER_HARD_FAIL",
                f"K7 deduction REJECTED: acc@d5={mean_a5:.3f}<{FAIL_ACC_AT_5} "
                f"OR r_per_step={mean_r:.3f}<{FAIL_R_PER_STEP}. {pts}.")
    return ("MULTISTEP_INFER_MIDDLE_BAND",
            f"Intermediate: acc@d5={mean_a5:.3f}, r_per_step={mean_r:.3f}. {pts}.")


def self_test_verdict():
    def mk(rows):
        ps = {}
        for i, (acc_dict, r) in enumerate(rows):
            ps[str(i)] = {"per_depth_acc": acc_dict, "r_per_step": r}
        return {"per_seed": ps}
    s_pass = mk([({1: 0.95, 2: 0.85, 3: 0.78, 4: 0.66, 5: 0.55}, 0.88)]*5)
    s_fail = mk([({1: 0.40, 2: 0.10, 3: 0.02, 4: 0.0, 5: 0.0}, 0.30)]*5)
    s_mid = mk([({1: 0.80, 2: 0.55, 3: 0.40, 4: 0.30, 5: 0.20}, 0.75)]*5)
    s_inconc = {"per_seed": {}}
    cases = [(s_pass, "MULTISTEP_INFER_HARD_PASS"),
             (s_fail, "MULTISTEP_INFER_HARD_FAIL"),
             (s_mid, "MULTISTEP_INFER_MIDDLE_BAND"),
             (s_inconc, "MULTISTEP_INFER_INCONCLUSIVE")]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    n = N_SMOKE if smoke else N_FULL
    n_ents = N_ENTITIES_SMOKE if smoke else N_ENTITIES_FULL
    depths = DEPTHS_SMOKE if smoke else DEPTHS_FULL
    n_q = N_QUERIES_SMOKE if smoke else N_QUERIES_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    device = "cuda" if (HAS_TORCH and torch.cuda.is_available()) else "cpu"
    config = {"mode": "smoke" if smoke else "full", "n": n, "n_entities": n_ents,
              "depths": depths, "n_queries": n_q, "seeds": seeds, "device": device,
              "pass_acc_at_5": PASS_ACC_AT_5, "pass_r_per_step": PASS_R_PER_STEP,
              "fail_acc_at_5": FAIL_ACC_AT_5, "fail_r_per_step": FAIL_R_PER_STEP}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        r = run_one_seed(seed, n, n_ents, depths, n_q, device=device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: acc={r['per_depth_acc']} r={r['r_per_step']:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14_k7_multistep_inference_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_k7_multistep_inference_v1")
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
