"""
q_b1_ab_iterate_3arm_v1_n16384 -- Q-B1 IMPROVE-track A/B-iterate: does a better recall
mechanism EXTEND the heteroassoc chain-depth cliff past control's d287 collapse?

PRE-REG: research_to_skunkworks_qb1_AB_prereg_v3_CANDIDATE2_ADDED_2026-06-19.md
  (committed origin/main 2b9bf477; Skunkworks quick-confirm PASS). N=2 Bonferroni alpha=0.025.

THREE ARMS (iso-protocol: SAME chains, SAME seeds, SAME eval metric; only the recall op differs):
  CONTROL          standard linear heteroassoc: H += outer(b,a)/N ; recall r = sign(H @ r).
  CANDIDATE-C      tropical / min-plus morphological associative memory (Ritter-Sussner;
                   the canonical (min,+)-semiring associative memory the pre-reg's
                   "min-plus semiring; depth-aware noise mitigation" denotes):
                     store   W_ij = min_p (b_p_i - a_p_j)   over all stored pairs p
                     recall  v_i  = max_j (W_ij + q_j) ;  r = sign(v).
                   Hypothesis: max-plus picks the single dominant association per coordinate
                   instead of SUMMING crosstalk, so per-hop noise does not accumulate
                   additively -> deeper usable chain. (NOTE: candidate-C's exact tropical
                   formalization is gated on a Skunkworks/Research SCHEMA-VET confirm that
                   this Ritter-Sussner (min,+) memory matches the pre-reg intent, so a
                   HARD_FAIL is not misattributed to a wrong implementation. See routing note.)
  CANDIDATE-2      cleanup-between-hops (substrate-EVIDENCED; resonator seed
                   EXP_substrate_resonator_augmented_iterated_retrieval smoke HARD_PASS 6x):
                   same linear H, but snap each intermediate onto the nearest stored node
                   between hops: r = codebook[argmax(codebook @ (H @ r))]. Resets the noise
                   floor each hop. Track-B IMPROVE-track promote-path (smoke -> cert).

TEST DEPTHS (5; span shallow / working / cliff): d100 d276 d280 d287 d293.
  Cluster baseline (informational, NOT the control): PASS at d276; HARD_FAIL at d287+.

PER-DEPTH PASS (the cluster's multi-point cliff-profile bands, generalized across depth):
  HP thresholds  d5>=0.90 d20>=0.75 d50>=0.50 d100>=0.20 d200>=0.02 (each applied iff snap<=depth)
                 AND endpoint(d=depth) >= (0.20 if depth==100 else 0.005).
  HARD_FAIL floor d5<0.80 OR d20<0.50 OR endpoint<0.001.
  PASS = no floor breach AND all applicable HP thresholds met ; else MIDDLE (no breach) / FAIL.

PER-ARM VERDICT (pre-reg v3 bands; Bonferroni alpha=0.025; applied to EACH candidate vs its OWN bands):
  no-regression = PASS at d100 AND PASS at d276 (a cliff-extending swap that breaks the working
                  region is a BAD SWAP -- strict-improvement: EXTEND AND PRESERVE).
  HARD_PASS  = PASS at d>=287 AND no-regression.
  MIDDLE     = PASS at d in [280,287) AND no-regression (PASS d280, not d287).
  HARD_FAIL  = no extension (fail d280) OR REGRESSES (fail d100 or d276) OR worse-than-control at a cliff depth.
  Robustness: mean-profile clears the band AND >=4/5 seeds clear the HARD_FAIL floor at that depth.

FORMULA SELF-TESTS (PROT-022):
  1. morphological single-pair perfect recall: store a->b, max-plus recall(a) sign-matches b.
  2. cleanup snaps a noisy node to its nearest codebook node.
  3. control 2-hop heteroassoc non-NaN; self-cosine = 1.0; GPU mem > 0.

PROT-018: anchor has _n16384 -> N MUST = 16384 (full). PROT-021: checkpoints keyed depth+seed+run_mode+N.
QUEUE: overnight_queue / gpu (N=16384; H and W each ~1.07 GB float32; peak ~1.4 GB). run_mode=full.
TIMEOUT ESTIMATE: morphological W builds dominate (~15*depth+M pairs each an N x N min). ~40-60 min full;
  checkpoint/resume per (depth,seed) so a kill resumes. ceil -> 5400s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "q_b1_ab_iterate_3arm_v1_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

ARMS = ["control", "cand_c_tropical", "cand2_cleanup"]

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_ACTIVE = 1024
    SEEDS = [7, 17]
    N_CHAINS = 4
    M_BACKGROUND = 20
    DEPTHS = [30, 60]
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    N_CHAINS = 15
    M_BACKGROUND = 200
    DEPTHS = [100, 276, 280, 287, 293]

# Pre-registered per-depth cliff-profile thresholds (the cluster's bisect bands, generalized).
HP_THRESH = {5: 0.90, 20: 0.75, 50: 0.50, 100: 0.20, 200: 0.02}
ENDPOINT_HP = 0.005          # endpoint bar for depths beyond the HP_THRESH table (276/280/287/293)
HF_D5 = 0.80
HF_D20 = 0.50
HF_ENDPOINT = 0.001
MAXPLUS_CHUNK = 2048         # row-chunk for the N x N max-plus matvec (bounds temp memory)

BASE_SNAPS = [1, 3, 5, 10, 15, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100,
              120, 140, 160, 180, 200, 220, 240, 260, 276, 280, 287, 293]


def snaps_for(depth: int) -> List[int]:
    s = [d for d in BASE_SNAPS if d < depth]
    s.append(depth)
    return s


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    na = float(a.norm()); nb = float(b.norm())
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(torch.dot(a, b)) / (na * nb)


def maxplus_matvec(W: torch.Tensor, q: torch.Tensor, n_dim: int) -> torch.Tensor:
    """v_i = max_j (W_ij + q_j), computed in row-chunks to bound the N x N temp."""
    out = torch.empty(n_dim, device=DEVICE, dtype=torch.float32)
    qb = q.unsqueeze(0)
    for i0 in range(0, n_dim, MAXPLUS_CHUNK):
        block = W[i0:i0 + MAXPLUS_CHUNK] + qb            # (chunk, N)
        out[i0:i0 + block.shape[0]] = block.max(dim=1).values
    return out


def build_W_morphological(pairs_a: torch.Tensor, pairs_b: torch.Tensor, n_dim: int) -> torch.Tensor:
    """Ritter-Sussner (min,+) memory: W_ij = min_p (b_p_i - a_p_j). pairs_* are (P, n_dim)."""
    W = torch.full((n_dim, n_dim), float('inf'), device=DEVICE, dtype=torch.float32)
    P = pairs_a.shape[0]
    for p in range(P):
        diff = pairs_b[p].unsqueeze(1) - pairs_a[p].unsqueeze(0)   # (n_dim, n_dim), freed each iter
        torch.minimum(W, diff, out=W)
    return W


def _instrumentation_selftest():
    n_t = 128
    gen = torch.Generator(device=DEVICE); gen.manual_seed(0)

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    # 1. morphological single-pair perfect recall (low load -> exact)
    a = bsc(1, n_t).squeeze(0); b = bsc(1, n_t).squeeze(0)
    W = build_W_morphological(a.unsqueeze(0), b.unsqueeze(0), n_t)
    rec = torch.sign(maxplus_matvec(W, a, n_t)); rec[rec == 0] = 1.0
    assert cosine_sim_gpu(rec, b) > 0.999, "morphological single-pair recall failed"
    del W

    # 2. cleanup snaps a noisy node to its nearest codebook node
    cb = bsc(5, n_t)                                # 5 nodes
    noisy = cb[2] + 0.3 * torch.randn(n_t, generator=gen, device=DEVICE)
    assert int(torch.argmax(cb @ noisy)) == 2, "cleanup snap failed"

    # 3. control 2-hop non-NaN + self-cosine + gpu mem
    chain = [bsc(1, n_t).squeeze(0) for _ in range(3)]
    H = torch.zeros((n_t, n_t), device=DEVICE, dtype=torch.float32)
    for h in range(2):
        H += torch.outer(chain[h + 1], chain[h]) / n_t
    r = chain[0].clone()
    for _ in range(2):
        r = torch.sign(H @ r); r[r == 0] = 1.0
    c2 = cosine_sim_gpu(r, chain[2])
    assert not (c2 != c2), "control 2-hop NaN"
    assert abs(cosine_sim_gpu(chain[0], chain[0]) - 1.0) < 1e-5, "self-cosine != 1.0"
    assert torch.cuda.memory_allocated(0) > 0, "gpu mem not allocated"
    del H
    print(f"[selftest] PASS: morphological-recall, cleanup-snap, control-2hop "
          f"(gpu_mem={torch.cuda.memory_allocated(0)/1e6:.1f}MB)", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_unit(depth: int, seed: int, n_dim: int) -> Dict:
    """One (depth, seed): build chains once; run all 3 arms; return per-arm snapshot profiles."""
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time()
    snaps = snaps_for(depth)

    def bsc(m, n_d):
        return (torch.randint(0, 2, (m, n_d), generator=gen, device=DEVICE).float() * 2 - 1)

    chains = [[bsc(1, n_dim).squeeze(0) for _ in range(depth + 1)] for _ in range(N_CHAINS)]
    bg_keys = bsc(M_BACKGROUND, n_dim); bg_vals = bsc(M_BACKGROUND, n_dim)

    # all stored (a -> b) pairs: chain steps + background (identical set for H and W)
    pa_list, pb_list = [], []
    for ch in chains:
        for h in range(depth):
            pa_list.append(ch[h]); pb_list.append(ch[h + 1])
    for i in range(M_BACKGROUND):
        pa_list.append(bg_keys[i]); pb_list.append(bg_vals[i])
    pairs_a = torch.stack(pa_list); pairs_b = torch.stack(pb_list)
    codebook = torch.stack([ch[h] for ch in chains for h in range(depth + 1)])   # (K, n_dim)

    arms_profile: Dict[str, Dict[str, float]] = {a: {} for a in ARMS}

    # ---- linear H (shared by control + candidate-2) ----
    H = torch.zeros((n_dim, n_dim), device=DEVICE, dtype=torch.float32)
    for p in range(pairs_a.shape[0]):
        H += torch.outer(pairs_b[p], pairs_a[p]) / n_dim

    for arm in ("control", "cand2_cleanup"):
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
    del H
    torch.cuda.empty_cache()

    # ---- morphological W (candidate-C tropical) ----
    W = build_W_morphological(pairs_a, pairs_b, n_dim)
    sims = {d: [] for d in snaps}
    for ch in chains:
        r = ch[0].clone()
        for step in range(1, depth + 1):
            r = torch.sign(maxplus_matvec(W, r, n_dim)); r[r == 0] = 1.0
            if step in sims:
                sims[step].append(cosine_sim_gpu(r, ch[step]))
    for d in snaps:
        arms_profile["cand_c_tropical"][str(d)] = float(sum(sims[d]) / len(sims[d])) if sims[d] else 0.0
    del W
    peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
    torch.cuda.empty_cache()

    elapsed = time.time() - t0
    ep = {a: arms_profile[a].get(str(depth), 0.0) for a in ARMS}
    print(f"  [d{depth} seed={seed}] endpoint cos: "
          + " ".join(f"{a}={ep[a]:.4f}" for a in ARMS)
          + f" peak_gpu={peak_gb:.2f}GB elapsed={elapsed:.1f}s", flush=True)

    return {"depth": depth, "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
            "n_chains": N_CHAINS, "m_background": M_BACKGROUND,
            "arms": arms_profile, "peak_gpu_gb": float(peak_gb), "elapsed_s": elapsed}


def _depth_pass(profile: Dict[str, float], depth: int) -> str:
    """PASS / MIDDLE / FAIL for one arm at one depth from its mean snapshot profile."""
    def g(d):
        return profile.get(str(d), 0.0)
    endpoint = g(depth)
    # HARD_FAIL floor
    if g(5) < HF_D5 or g(20) < HF_D20 or endpoint < HF_ENDPOINT:
        return "FAIL"
    # all applicable HP thresholds
    ok = True
    for d, thr in HP_THRESH.items():
        if d <= depth and d != depth:
            ok = ok and (g(d) >= thr)
    endpoint_bar = HP_THRESH.get(depth, ENDPOINT_HP)
    ok = ok and (endpoint >= endpoint_bar)
    return "PASS" if ok else "MIDDLE"


def _seed_floor_frac(units: List[Dict], arm: str, depth: int) -> float:
    """Fraction of seeds whose per-seed profile clears the HARD_FAIL floor at this depth."""
    rel = [u for u in units if u["depth"] == depth]
    if not rel:
        return 0.0
    ok = 0
    for u in rel:
        p = u["arms"][arm]
        d5 = p.get("5", 0.0); d20 = p.get("20", 0.0); ep = p.get(str(depth), 0.0)
        if d5 >= HF_D5 and d20 >= HF_D20 and ep >= HF_ENDPOINT:
            ok += 1
    return ok / len(rel)


def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "No valid results.", {})

    # mean profile per (arm, depth)
    mean_prof: Dict[str, Dict[int, Dict[str, float]]] = {a: {} for a in ARMS}
    for depth in DEPTHS:
        rel = [u for u in units if u["depth"] == depth]
        for arm in ARMS:
            acc: Dict[str, List[float]] = {}
            for u in rel:
                for k, v in u["arms"][arm].items():
                    acc.setdefault(k, []).append(v)
            mean_prof[arm][depth] = {k: float(sum(v) / len(v)) for k, v in acc.items()}

    per_depth = {a: {} for a in ARMS}
    robust = {a: {} for a in ARMS}
    for arm in ARMS:
        for depth in DEPTHS:
            per_depth[arm][depth] = _depth_pass(mean_prof[arm][depth], depth)
            robust[arm][depth] = _seed_floor_frac(units, arm, depth)

    def passed(arm, depth):
        # robust PASS: mean clears band AND >=4/5 seeds (or >=1/2 in smoke) clear floor
        need = 0.8 if RUN_MODE == "full" else 0.5
        return per_depth[arm][depth] == "PASS" and robust[arm][depth] >= need

    arm_verdict = {}
    for arm in ARMS:
        no_regression = passed(arm, 100) and passed(arm, 276)
        ep293 = mean_prof[arm][293].get("293", 0.0) if 293 in DEPTHS else 0.0
        ep_ctrl293 = mean_prof["control"][293].get("293", 0.0) if 293 in DEPTHS else 0.0
        worse_than_control = (arm != "control") and any(
            mean_prof[arm][d].get(str(d), 0.0) + 1e-9 < mean_prof["control"][d].get(str(d), 0.0)
            for d in DEPTHS if d >= 287
        )
        if not no_regression:
            arm_verdict[arm] = "HARD_FAIL"            # regresses on working/shallow region
        elif worse_than_control:
            arm_verdict[arm] = "HARD_FAIL"            # not an improvement at the cliff
        elif any(passed(arm, d) for d in DEPTHS if d >= 287):
            arm_verdict[arm] = "HARD_PASS"            # extends past the cliff + preserves
        elif passed(arm, 280):
            arm_verdict[arm] = "MIDDLE_BAND"          # partial extension into [280,287)
        else:
            arm_verdict[arm] = "HARD_FAIL"            # no extension

    # overall = best CANDIDATE outcome (control is the reference, not a winner)
    cand = [a for a in ARMS if a != "control"]
    rank = {"HARD_PASS": 3, "MIDDLE_BAND": 2, "HARD_FAIL": 1}
    best = max(cand, key=lambda a: rank[arm_verdict[a]])
    overall = arm_verdict[best] if rank[arm_verdict[best]] > 1 else "HARD_FAIL"

    lines = []
    for arm in ARMS:
        pd = " ".join(f"d{d}:{per_depth[arm][d][0]}({robust[arm][d]:.1f})" for d in DEPTHS)
        ep = " ".join(f"d{d}={mean_prof[arm][d].get(str(d),0.0):.4f}" for d in DEPTHS)
        lines.append(f"{arm}={arm_verdict[arm]} | per-depth[{pd}] | endpoint[{ep}]")
    n_hp = sum(1 for a in cand if arm_verdict[a] == "HARD_PASS")
    swap = ("SWAP to " + best if n_hp >= 1 else "NO SWAP (current_best d276 stays)")
    msg = (f"{overall} (best candidate={best}; {n_hp} candidate HARD_PASS; {swap}; "
           f"Bonferroni alpha=0.025). " + " || ".join(lines))
    detail = {"arm_verdict": arm_verdict, "per_depth": per_depth, "robust_floor_frac": robust,
              "mean_profile": {a: {str(d): mean_prof[a][d] for d in DEPTHS} for a in ARMS},
              "best_candidate": best, "n_candidate_hard_pass": n_hp, "swap_decision": swap}
    return (overall, msg, detail)


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
                           f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} arms={ARMS} "
      f"depths={DEPTHS} seeds={SEEDS} n_chains={N_CHAINS} m_bg={M_BACKGROUND}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_ACTIVE if RUN_MODE == "smoke" else N, "run_mode": RUN_MODE}

# checkpoint/resume per (depth, seed) compound key
units_keys = [(d, s) for d in DEPTHS for s in SEEDS]
print(f"[ckpt] grid = {len(units_keys)} units ({len(DEPTHS)} depths x {len(SEEDS)} seeds)", flush=True)

t_sweep = time.time()
for depth, seed in units_keys:
    key = f"d{depth}_s{seed}"
    existing = aggregate_partials(out_dir, [key], run_config=run_config)
    if key in existing:
        print(f"[ckpt] {key} done; skip", flush=True)
        continue
    print(f"[unit={key}] {ANCHOR_NAME}...", flush=True)
    res = run_unit(depth, seed, N_ACTIVE if RUN_MODE == "smoke" else N)
    write_partial_key(out_dir, key, res)

all_partials = aggregate_partials(out_dir, [f"d{d}_s{s}" for d, s in units_keys], run_config=run_config)
units = list(all_partials.values())
verdict, verdict_msg, detail = compute_verdict(units)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU util check FAIL: peak_gpu={peak_mem_gb:.3f}GB (< 100MB)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE, "arms": ARMS, "depths": DEPTHS,
    "n_seeds": len(SEEDS), "n_chains": N_CHAINS, "m_background": M_BACKGROUND,
    "bonferroni_alpha": 0.025,
    "detail": detail,
    "per_unit": [{"depth": u["depth"], "seed": u["seed"], "arms": u["arms"],
                  "peak_gpu_gb": u.get("peak_gpu_gb"), "elapsed_s": u.get("elapsed_s")}
                 for u in units],
    "metrics_source": "measured_gpu_heteroassoc_chain_depth_3arm_ab",
    "peak_gpu_gb": float(peak_mem_gb),
}
write_metrics(out_dir, metrics, metrics.get("per_unit"))
print(f"[metrics] written to {out_dir / 'metrics.json'}", flush=True)
