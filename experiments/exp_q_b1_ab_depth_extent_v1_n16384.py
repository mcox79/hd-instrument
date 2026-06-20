"""
q_b1_ab_depth_extent_v1_n16384 -- q_b1 A/B FOLLOW-UP: characterize the NEW cliff of candidate-2
(resonator cleanup-between-hops) beyond d293.

PRE-REG-TRIGGERED: the q_b1 A/B (CERT 588) showed cand2_cleanup HARD_PASS at d293 (cos=1.0; the cliff is
BEYOND d293, not absent). Pre-reg v4 bonus add-back: "if a candidate HARD_PASSes at d293 -> a follow-up
depth-extent run (d300/d350/d400/d500) characterizes the NEW cliff." This is that run. CHARACTERIZATION
(find where cand2's per-hop snap starts failing), not a new HARD_PASS/FAIL cert -- honest-scope: extends
the measured-bound of the cleanup mechanism.

ARMS = control (standard sign-cleanup; reference, collapsed past its d287 cliff) + cand2_cleanup
(snap-to-nearest-stored-node each hop). Same iso-protocol harness as the A/B (N=16384, n_seeds=5,
N_CHAINS=15, M_BACKGROUND=200). DEPTHS = [300, 350, 400, 500].

VERDICT (descriptive): cand2's cliff = the smallest tested depth where cand2 is NOT PASS (cliff-profile
bands, same as the A/B). If cand2 PASS through d500 -> "CLIFF_BEYOND_d500" (extends further still).
FORMULA SELF-TESTS: control 2-hop non-NaN; cleanup snaps noisy node to nearest. PROT-018 _n16384.
QUEUE: overnight_queue (GPU; longer chains -> heavier than the A/B). checkpoint/resume per (depth,seed). ASCII.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "q_b1_ab_depth_extent_v1_n16384"
_N_SUFFIX = 16384; N = 16384
assert N == _N_SUFFIX
ARMS = ["control", "cand2_cleanup"]
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_ACTIVE = 1024; SEEDS = [7, 17]; N_CHAINS = 4; M_BACKGROUND = 20; DEPTHS = [60, 90]
else:
    N_ACTIVE = N; SEEDS = [7, 17, 23, 31, 41]; N_CHAINS = 15; M_BACKGROUND = 200; DEPTHS = [300, 350, 400, 500]

HP_THRESH = {5: 0.90, 20: 0.75, 50: 0.50, 100: 0.20, 200: 0.02}
ENDPOINT_HP = 0.005; HF_D5 = 0.80; HF_D20 = 0.50; HF_ENDPOINT = 0.001
BASE_SNAPS = [1, 3, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 120, 140, 160, 180, 200,
              220, 240, 260, 280, 300, 325, 350, 375, 400, 450, 500]


def snaps_for(depth):
    s = [d for d in BASE_SNAPS if d < depth]; s.append(depth); return s


def cosine_sim_gpu(a, b):
    na = float(a.norm()); nb = float(b.norm())
    return 0.0 if (na < 1e-12 or nb < 1e-12) else float(torch.dot(a, b)) / (na * nb)


def _selftest():
    n_t = 128; g = torch.Generator(device=DEVICE); g.manual_seed(0)
    def bsc(m, n_d): return (torch.randint(0, 2, (m, n_d), generator=g, device=DEVICE).float() * 2 - 1)
    chain = [bsc(1, n_t).squeeze(0) for _ in range(3)]
    H = torch.zeros((n_t, n_t), device=DEVICE, dtype=torch.float32)
    for h in range(2):
        H += torch.outer(chain[h + 1], chain[h]) / n_t
    r = chain[0].clone()
    for _ in range(2):
        r = torch.sign(H @ r); r[r == 0] = 1.0
    assert not (cosine_sim_gpu(r, chain[2]) != cosine_sim_gpu(r, chain[2])), "2-hop NaN"
    cb = bsc(5, n_t); noisy = cb[2] + 0.3 * torch.randn(n_t, generator=g, device=DEVICE)
    assert int(torch.argmax(cb @ noisy)) == 2, "cleanup snap"
    assert torch.cuda.memory_allocated(0) > 0
    print("[selftest] PASS: control-2hop + cleanup-snap", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_unit(depth, seed, n_dim):
    g = torch.Generator(device=DEVICE); g.manual_seed(seed); t0 = time.time(); snaps = snaps_for(depth)
    def bsc(m, n_d): return (torch.randint(0, 2, (m, n_d), generator=g, device=DEVICE).float() * 2 - 1)
    chains = [[bsc(1, n_dim).squeeze(0) for _ in range(depth + 1)] for _ in range(N_CHAINS)]
    bg_k = bsc(M_BACKGROUND, n_dim); bg_v = bsc(M_BACKGROUND, n_dim)
    pa, pb = [], []
    for ch in chains:
        for h in range(depth):
            pa.append(ch[h]); pb.append(ch[h + 1])
    for i in range(M_BACKGROUND):
        pa.append(bg_k[i]); pb.append(bg_v[i])
    pairs_a = torch.stack(pa); pairs_b = torch.stack(pb)
    codebook = torch.stack([ch[h] for ch in chains for h in range(depth + 1)])
    arms_profile = {a: {} for a in ARMS}
    H = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32)
    for p in range(pairs_a.shape[0]):
        H += torch.outer(pairs_b[p], pairs_a[p]) / n_dim
    for arm in ARMS:
        sims = {d: [] for d in snaps}
        for ch in chains:
            r = ch[0].clone()
            for step in range(1, depth + 1):
                v = H @ r
                if arm == "cand2_cleanup":
                    r = codebook[int(torch.argmax(codebook @ v))]
                else:
                    r = torch.sign(v); r[r == 0] = 1.0
                if step in sims:
                    sims[step].append(cosine_sim_gpu(r, ch[step]))
        for d in snaps:
            arms_profile[arm][str(d)] = float(sum(sims[d]) / len(sims[d])) if sims[d] else 0.0
    del H; peak = torch.cuda.max_memory_allocated(0) / 1e9; torch.cuda.empty_cache()
    elapsed = time.time() - t0
    print(f"  [d{depth} seed={seed}] endpoint: " + " ".join(f"{a}={arms_profile[a].get(str(depth),0):.4f}" for a in ARMS)
          + f" peak={peak:.2f}GB {elapsed:.0f}s", flush=True)
    return {"depth": depth, "seed": seed, "N": n_dim, "run_mode": RUN_MODE, "arms": arms_profile,
            "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def _depth_pass(profile, depth):
    def gg(d): return profile.get(str(d), 0.0)
    ep = gg(depth)
    if gg(5) < HF_D5 or gg(20) < HF_D20 or ep < HF_ENDPOINT:
        return "FAIL"
    ok = all(gg(d) >= thr for d, thr in HP_THRESH.items() if d < depth)
    ok = ok and (ep >= HP_THRESH.get(depth, ENDPOINT_HP))
    return "PASS" if ok else "MIDDLE"


def compute_verdict(units) -> Tuple[str, str, Dict]:
    if not units:
        return ("UNKNOWN", "no results", {})
    mean = {a: {} for a in ARMS}
    for depth in DEPTHS:
        rel = [u for u in units if u["depth"] == depth]
        for arm in ARMS:
            acc = {}
            for u in rel:
                for k, v in u["arms"][arm].items():
                    acc.setdefault(k, []).append(v)
            mean[arm][depth] = {k: sum(v) / len(v) for k, v in acc.items()}
    cand_pd = {d: _depth_pass(mean["cand2_cleanup"][d], d) for d in DEPTHS}
    ctrl_pd = {d: _depth_pass(mean["control"][d], d) for d in DEPTHS}
    cliff = next((d for d in DEPTHS if cand_pd[d] != "PASS"), None)
    if cliff is None:
        verdict = "CLIFF_BEYOND_d%d" % max(DEPTHS)
        scope = ("cand2 cleanup-between-hops PASS through ALL tested depths (%s) -- the new cliff is BEYOND d%d "
                 "(even deeper than this follow-up tested)." % (DEPTHS, max(DEPTHS)))
    else:
        verdict = "CLIFF_AT_d%d" % cliff
        scope = ("cand2 cleanup cliff onset at d=%d (%s); PASS below it. The per-hop exact-snap mechanism "
                 "holds until d=%d at N=16384/%d-chain load." % (cliff, cand_pd[cliff], cliff, N_CHAINS))
    eps = {a: {d: round(mean[a][d].get(str(d), 0.0), 4) for d in DEPTHS} for a in ARMS}
    msg = ("%s: %s | cand2 per-depth=%s | control per-depth=%s (reference; collapsed past its d287 cliff) | "
           "endpoints cand2=%s control=%s" % (verdict, scope, cand_pd, ctrl_pd, eps["cand2_cleanup"], eps["control"]))
    detail = {"cand2_cliff_depth": cliff, "cand2_per_depth": cand_pd, "control_per_depth": ctrl_pd,
              "endpoints": eps, "honest_scope": scope}
    return (verdict, msg, detail)


def _prot018(n):
    if RUN_MODE != "smoke" and n != _N_SUFFIX:
        raise RuntimeError("PROT-018 N mismatch")


print(f"[config] {ANCHOR_NAME} mode={RUN_MODE} arms={ARMS} depths={DEPTHS} seeds={SEEDS}", flush=True)
_prot018(N_ACTIVE if RUN_MODE == "smoke" else N)
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE if RUN_MODE == "smoke" else N, "run_mode": RUN_MODE}
t_sweep = time.time()
for depth, seed in [(d, s) for d in DEPTHS for s in SEEDS]:
    key = f"d{depth}_s{seed}"
    if key in aggregate_partials(out_dir, [key], run_config=run_config):
        print(f"[ckpt] {key} done; skip", flush=True); continue
    print(f"[unit={key}]", flush=True)
    write_partial_key(out_dir, key, run_unit(depth, seed, N_ACTIVE if RUN_MODE == "smoke" else N))
units = list(aggregate_partials(out_dir, [f"d{d}_s{s}" for d in DEPTHS for s in SEEDS], run_config=run_config).values())
verdict, msg, detail = compute_verdict(units)
print("\n[VERDICT] " + msg, flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9
assert peak > 0.01
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": msg, "N": N, "run_mode": RUN_MODE,
           "arms": ARMS, "depths": DEPTHS, "n_seeds": len(SEEDS), "detail": detail,
           "metrics_source": "measured_gpu_heteroassoc_chain_depth_extent_cand2", "per_unit": units,
           "elapsed_s": time.time() - t_sweep, "peak_gpu_gb": float(peak)}
write_metrics(out_dir, metrics, units)
print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)
