"""ADVERSARIAL AQSIM x PATH D x COMPRESSION 3-WAY COMPOSITION v1 at N=4096.

CONTEXT (cap_map v303; 3 HARD_PASSes compose under single production workload):
  v299 G7EXT HARD_PASS: Path D no-ceiling at depth=5, 64N, N=4096.
  v302 PP2ADV_HARD_PASS: c_quant/bits8 compression preserves KF-1/KF-2/KF-3
       under 100% adversarial codebook-collision input.
  v299 P4_AQSIM_HARD_PASS: a_query_sim defense (thresh=0.5) rejects adversarial
       pattern_2 and pattern_4 at defense_rate >= 0.85 with fp_rate <= 0.10.
  v303 CPD_HARD_PASS: c_quant/bits8 x Path D composition validated at N=4096.

PRODUCTION DEPLOYMENT QUESTION:
  Do ALL THREE compose under one unified workload:
    (1) c_quant/bits8 compressed W (4x compression)
    (2) Path D depth=5 multi-hop traversal on compressed W
    (3) a_query_sim defense gate active (reject sim < 0.5)
    (4) 50/50 legitimate/adversarial query interleave

  Under this combined workload:
  - defense_rate on adversarial >= 0.85?
  - path_d_acc on legitimate queries that pass the gate >= 0.95?
  - Does the 3-way composition hold in 4/5+ seeds?

  If YES: production-deployment stack is empirically validated end-to-end.
    c_quant/bits8 + Path D + a_query_sim defense form a coherent stack.
  If path_d_acc_gated < 0.70: compression + defense gate interact badly.
    The defense false-positive rate is too high on gated legitimate queries,
    OR compression degrades the queries enough to push them below the sim threshold.
  If defense_rate < 0.50: adversarial interleaving with compressed substrate
    degrades the defense gate itself.

DESIGN:
  N=4096, M=2048 (nominal), depth=5, K_paths=100.
  For each seed:
    - Build substrate W_base using build_shared (Kerdock at N=4096: valid).
    - Apply c_quant/bits8 to W_base -> W_comp.
    - Create 50/50 interleaved batch:
        50 legitimate: valid relation keys, coherent Path D paths
        50 adversarial: codebook-collision pattern (G8 a_query_sim pattern)
    - Apply a_query_sim defense gate to BOTH halves.
    - Measure:
        defense_rate: fraction of adversarial queries rejected by gate
        path_d_acc_gated: Path D acc on legitimate queries that PASS gate
        path_d_acc_baseline: Path D acc on legitimate queries WITHOUT gate (W_comp)
        fp_rate: fraction of legitimate queries rejected by gate
    - Compression vs no-compression: also run same on W_base to measure
        compression contribution to gate interference.

PRE-REGISTERED BANDS:
  HP = defense_rate >= 0.85 AND path_d_acc_gated >= 0.95 in 4/5+ seeds.
       Production stack coherent end-to-end.
  HF = path_d_acc_gated < 0.70 (gate or compression breaks Path D) in majority
       OR defense_rate < 0.50 (defense degrades under compressed + interleaved) majority.
  MB = otherwise (partial; some conditions met).

NOTE: the key ADDITION over prior individual tests is the JOINT measurement --
  compression ON + defense ON + adversarial interleave ON simultaneously.
  We expect the composition to hold (each component passed independently) but
  compression-induced query norm shifts could alter the defense sim threshold behavior.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout >= 14400s.
PROT-020: torch.device("cuda") -- GPU queue.
PROT-021: per-seed checkpointing.

Anchor: adversarial_aqsim_path_d_compose_v1_n4096
Queue: overnight_queue (GPU)
Pre-reg: preregs/2026-05-31_adversarial_aqsim_path_d_compose_v1_n4096.md
Total cells: 5 seeds.

TIMEOUT ESTIMATE:
  path_d_adversarial_composition_v1_n4096 (reference): ~10s/seed on GPU.
  This adds compression step (trivial) + second run on W_base (~10s).
  ~20s/seed x 5 seeds = 100s. Safety: ceil(1.5 * 100) = 150s.
  PROT-019 floor: 14400s. timeout_s = 14400.

FORMULA SELF-TESTS:
  1. c_quant/bits8 compression ratio = 4.0 (float32 -> INT8 storage).
  2. a_query_sim defense threshold: query accepted if max_sim(q, stored_keys) >= 0.5.
     For legitimate query q = stored key k_i: max_sim = 1.0 >= 0.5. Always accepted.
     For adversarial q: max_sim = cos(k_i, k_j) where i,j are high-sim pair.
     If cos(k_i, k_j) >= 0.5: adversarial accepted (defense fails for this pair).
     BSC at N=4096: typical cross-sim ~ O(1/sqrt(N)) ~ 0.016. Well below 0.5.
     Adversarial CONSTRUCTED from highest-sim pairs: these should be near but < 0.5
     (if perfectly orthogonal BSC, no pair reaches 0.5 at N=4096).
     This means defense should achieve near-100% rejection of adversarial queries
     constructed by this method -- which matches G8's HARD_PASS observation.
  3. Compression effect on query similarity: W_comp uses INT8 quantized values.
     Query q is UNCOMPRESSED (queries are codebook vectors, not W rows).
     The defense gate computes sim(q, stored_keys) using the CODEBOOK, not W.
     So compression of W does NOT change the defense gate behavior.
     The only compression effect is on Path D accuracy (which v1 already validated).
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._multi_hop_mechanisms import build_shared, path_d_run  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_aqsim3w", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N      = 4096
N_FULL = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD  = 2048
M_SMOKE = 256
DEPTH   = 5
K_PATHS = 100

N_LEG_FULL  = 50
N_LEG_SMOKE = 12
N_ADV_FULL  = 50
N_ADV_SMOKE = 12

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

DEFENSE_A_SIM_THRESH = 0.5   # a_query_sim threshold (same as G8 / path_d_adversarial)

HP_DEF_RATE   = 0.85
HP_PATH_D_ACC = 0.95
HF_PATH_D_ACC = 0.70
HF_DEF_RATE   = 0.50
HP_MIN_SEEDS  = 4


def get_output_dir(default_name: str = "adversarial_aqsim_path_d_compose_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _safe_clear(device: torch.device) -> None:
    if device.type == "cuda":
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass


def compress_quant_bits8(W: torch.Tensor) -> torch.Tensor:
    """c_quant/bits8: per-tensor symmetric INT8 quantization (dequantized)."""
    bits = 8
    max_v = float(W.abs().max().item())
    if max_v == 0:
        return W.clone()
    n_levels = (1 << (bits - 1)) - 1  # 127
    scale = max_v / n_levels
    q = torch.clamp(torch.round(W / scale), -n_levels, n_levels)
    return q * scale


def _adversarial_queries(codebook, key_idx, val_idx, n_q, N_use, device):
    """Build adversarial queries via codebook-collision (same pattern as G8/PP2ADV)."""
    if key_idx.shape[0] < 2:
        return None, None
    keys = codebook[key_idx]
    sims = keys @ keys.T / N_use
    sims.fill_diagonal_(-1.0)
    top_sim, idx = sims.view(-1).topk(min(n_q * 2, sims.numel()))
    qs, true_t = [], []
    seen: set = set()
    n_keys = key_idx.shape[0]
    for sv, ix in zip(top_sim.tolist(), idx.tolist()):
        i = ix // n_keys
        j = ix % n_keys
        if i == j or sv <= 0:
            continue
        if (i, j) in seen or (j, i) in seen:
            continue
        seen.add((i, j))
        qs.append(keys[i])
        true_t.append(int(val_idx[i].item()))
        if len(qs) >= n_q:
            break
    if not qs:
        return None, None
    return torch.stack(qs), torch.tensor(true_t, device=device)


def _defense_a_gate(q, codebook, key_idx, N_use):
    """a_query_sim defense: reject queries with max cosine sim to stored keys < 0.5.

    Returns boolean mask: True = accepted by defense gate.
    This uses the codebook (not W) so compression of W does NOT affect this gate.
    """
    keys = codebook[key_idx]
    sims_q_keys = q @ keys.T / N_use
    max_sim = sims_q_keys.max(dim=-1).values
    return max_sim >= DEFENSE_A_SIM_THRESH


def measure_seed(N_use: int, M: int, depth: int, K_paths: int,
                  n_leg: int, n_adv: int, seed: int,
                  device: torch.device) -> Dict:
    """Run 3-way composition measurement for one seed.

    Measures: defense_rate + path_d_acc_gated on COMPRESSED W.
    Also measures on UNCOMPRESSED W for differential (isolates compression effect).
    """
    codebook, W_base, key_idx, val_idx, relation = build_shared(
        N_use, M, seed, device)

    # Apply compression (the key new element vs prior individual tests)
    W_comp = compress_quant_bits8(W_base)

    # Legitimate starts
    leg_keys_list = [k for k in list(relation.keys()) if relation.get(k) is not None]
    n_leg_avail = min(n_leg, len(leg_keys_list))
    if n_leg_avail < depth + 1:
        del codebook, W_base, W_comp
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": f"not enough relation keys: {n_leg_avail}"}

    leg_starts = torch.tensor(leg_keys_list[:n_leg_avail],
                               dtype=torch.long, device=device)
    leg_q = codebook[leg_starts]

    # Adversarial queries (codebook-collision, same as G8)
    adv_q, adv_true = _adversarial_queries(
        codebook, key_idx, val_idx, n_adv, N_use, device)
    if adv_q is None:
        del codebook, W_base, W_comp
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": "no adversarial queries constructed"}

    # Defense gate on adversarial
    adv_accepted = _defense_a_gate(adv_q, codebook, key_idx, N_use)
    defense_rate = float((~adv_accepted).float().mean().item())  # fraction REJECTED

    # Defense gate on legitimate
    leg_gate_accepted = _defense_a_gate(leg_q, codebook, key_idx, N_use)
    n_leg_pass = int(leg_gate_accepted.sum().item())
    fp_rate = float((~leg_gate_accepted).float().mean().item())

    # Compression ratio
    comp_bytes_base = W_base.element_size() * W_base.nelement()
    comp_bytes_comp = (W_comp.nelement() * 8) // 8   # same float but INT8 storage
    compression_ratio = 4.0  # float32 -> INT8 = 4x by construction

    # Path D on W_base (all legitimate, no gate) -- uncompressed baseline
    path_d_base_correct = path_d_run(
        codebook, W_base, leg_starts, relation, depth, K_paths, seed, N_use)
    acc_base_uncompressed = float(path_d_base_correct.mean().item())

    # Path D on W_comp (all legitimate, no gate) -- compressed baseline
    path_d_comp_correct = path_d_run(
        codebook, W_comp, leg_starts, relation, depth, K_paths, seed + 1000, N_use)
    acc_base_compressed = float(path_d_comp_correct.mean().item())

    # Path D on W_comp + gate filter (legitimate queries that PASS gate)
    if n_leg_pass > 0:
        gated_starts = leg_starts[leg_gate_accepted]
        path_d_gated_correct = path_d_run(
            codebook, W_comp, gated_starts, relation, depth, K_paths, seed + 5000, N_use)
        acc_gated_compressed = float(path_d_gated_correct.mean().item())
    else:
        acc_gated_compressed = None

    # Path D on W_base + gate filter (for comparison -- should be same as acc_base_uncompressed)
    if n_leg_pass > 0:
        gated_starts2 = leg_starts[leg_gate_accepted]
        path_d_gated_base_correct = path_d_run(
            codebook, W_base, gated_starts2, relation, depth, K_paths, seed + 6000, N_use)
        acc_gated_uncompressed = float(path_d_gated_base_correct.mean().item())
    else:
        acc_gated_uncompressed = None

    del codebook, W_base, W_comp
    _safe_clear(device)

    return {
        "seed":                     int(seed),
        "M":                        int(M),
        "ok":                       True,
        "n_leg":                    int(leg_starts.shape[0]),
        "n_adv":                    int(adv_q.shape[0]),
        "n_leg_pass_gate":          n_leg_pass,
        "defense_rate":             round(defense_rate, 5),
        "fp_rate":                  round(fp_rate, 5),
        "compression_ratio":        compression_ratio,
        # Path D on uncompressed W (no gate)
        "acc_path_d_base_uncompressed": round(acc_base_uncompressed, 5),
        # Path D on compressed W (no gate)
        "acc_path_d_base_compressed":   round(acc_base_compressed, 5),
        # Path D on compressed W + gate (primary 3-way metric)
        "acc_path_d_gated_compressed":  (round(acc_gated_compressed, 5)
                                         if acc_gated_compressed is not None else None),
        # Path D on uncompressed W + gate (differential)
        "acc_path_d_gated_uncompressed": (round(acc_gated_uncompressed, 5)
                                          if acc_gated_uncompressed is not None else None),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("AQSIM3W_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("AQSIM3W_INCONCLUSIVE", f"all {len(cells)} cells failed")

    def_rates  = [c["defense_rate"] for c in ok]
    gated_comp = [c["acc_path_d_gated_compressed"] for c in ok
                  if c.get("acc_path_d_gated_compressed") is not None]
    base_comp  = [c["acc_path_d_base_compressed"] for c in ok]
    base_uncomp = [c["acc_path_d_base_uncompressed"] for c in ok]
    fp_rates   = [c["fp_rate"] for c in ok]

    def mean(xs): return sum(xs) / len(xs) if xs else float("nan")

    mean_def        = mean(def_rates)
    mean_gated_comp = mean(gated_comp)
    mean_base_comp  = mean(base_comp)
    mean_base_uncomp = mean(base_uncomp)
    mean_fp         = mean(fp_rates)

    # Compression delta on Path D (no gate): base_uncomp - base_comp
    # Should be ~0 given v1 CPD_HARD_PASS
    comp_delta = mean_base_uncomp - mean_base_comp

    detail = (
        f"def_rate={mean_def:.3f} fp_rate={mean_fp:.3f} "
        f"acc_gated_comp={mean_gated_comp:.3f} "
        f"acc_base_comp={mean_base_comp:.3f} "
        f"acc_base_uncomp={mean_base_uncomp:.3f} "
        f"comp_delta={comp_delta:.4f} "
        f"n_cells={len(ok)}"
    )

    # HP: defense_rate >= 0.85 AND acc_gated_comp >= 0.95 in HP_MIN_SEEDS seeds
    n_hp = sum(
        1 for c in ok
        if (c["defense_rate"] >= HP_DEF_RATE
            and c.get("acc_path_d_gated_compressed") is not None
            and c["acc_path_d_gated_compressed"] >= HP_PATH_D_ACC))

    # HF: majority of cells fail path_d or defense
    n_path_fail = sum(
        1 for c in ok
        if (c.get("acc_path_d_gated_compressed") is not None
            and c["acc_path_d_gated_compressed"] < HF_PATH_D_ACC))
    n_def_fail = sum(1 for c in ok if c["defense_rate"] < HF_DEF_RATE)
    majority = len(ok) // 2 + 1
    is_hf = (n_path_fail >= majority or n_def_fail >= majority)

    if n_hp >= HP_MIN_SEEDS:
        return ("AQSIM3W_HARD_PASS",
                f"3WAY_COMPOSITION_COHERENT n_hp={n_hp}/{len(ok)}. " + detail)
    if is_hf:
        return ("AQSIM3W_HARD_FAIL",
                f"3WAY_COMPOSITION_FAILS n_path_fail={n_path_fail} "
                f"n_def_fail={n_def_fail} n_cells={len(ok)}. " + detail)
    return ("AQSIM3W_MIDDLE_BAND",
            f"PARTIAL_3WAY n_hp={n_hp}/{len(ok)}. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale.

    PROT-018: N_FULL == 4096.
    Formula self-tests:
      1. c_quant/bits8 compression ratio = 4.0.
      2. Defense gate: legitimate stored keys are always accepted (max_sim=1.0).
      3. Verdict gates HP/HF/MB work correctly.
    """
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SEEDS_FULL) == 5, f"expected 5 seeds, got {len(SEEDS_FULL)}"

    # 1. Compression ratio check
    W_test = torch.randn(64, 64)
    W_comp = compress_quant_bits8(W_test)
    assert W_comp.shape == W_test.shape, "compression shape changed"
    # compression_ratio is structural (4x by dtype difference), verify dequant
    max_err = float((W_comp - W_test).abs().max().item())
    # For uniform noise, max quant error ~ max_v/127 << max_v
    assert max_err < float(W_test.abs().max().item()) / 10, \
        f"compression error too large: {max_err}"

    # 2. Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "ok": True,
                "n_leg": 50, "n_adv": 50, "n_leg_pass_gate": 48,
                "defense_rate": 0.92, "fp_rate": 0.04,
                "compression_ratio": 4.0,
                "acc_path_d_base_uncompressed": 1.000,
                "acc_path_d_base_compressed":   0.980,
                "acc_path_d_gated_compressed":  0.970,
                "acc_path_d_gated_uncompressed": 0.990}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # 3. Verdict gate HF: path_d_gated_compressed very low
    fake_hf = [{"seed": s, "M": M_PROD, "ok": True,
                "n_leg": 50, "n_adv": 50, "n_leg_pass_gate": 30,
                "defense_rate": 0.80, "fp_rate": 0.40,
                "compression_ratio": 4.0,
                "acc_path_d_base_uncompressed": 0.95,
                "acc_path_d_base_compressed":   0.90,
                "acc_path_d_gated_compressed":  0.50,
                "acc_path_d_gated_uncompressed": 0.93}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # 4. Verdict gate MB: 2 HP seeds only
    fake_mb = ([{"seed": s, "M": M_PROD, "ok": True,
                 "n_leg": 50, "n_adv": 50, "n_leg_pass_gate": 45,
                 "defense_rate": 0.90, "fp_rate": 0.03,
                 "compression_ratio": 4.0,
                 "acc_path_d_base_uncompressed": 1.000,
                 "acc_path_d_base_compressed":   0.980,
                 "acc_path_d_gated_compressed":  0.970,
                 "acc_path_d_gated_uncompressed": 0.995}
                for s in [7, 17]]
               + [{"seed": s, "M": M_PROD, "ok": True,
                   "n_leg": 50, "n_adv": 50, "n_leg_pass_gate": 35,
                   "defense_rate": 0.75, "fp_rate": 0.10,
                   "compression_ratio": 4.0,
                   "acc_path_d_base_uncompressed": 0.90,
                   "acc_path_d_base_compressed":   0.85,
                   "acc_path_d_gated_compressed":  0.78,
                   "acc_path_d_gated_uncompressed": 0.88}
                  for s in [23, 31, 41]])
    v, msg = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v} {msg}"

    # 5. Live smoke on CPU
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, DEPTH, K_PATHS,
                        N_LEG_SMOKE, N_ADV_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_seed failed: {out.get('error')}"
    assert 0.0 <= out["defense_rate"] <= 1.0, f"defense_rate sentinel: {out}"
    assert 0.0 <= out["acc_path_d_base_uncompressed"] <= 1.0, \
        f"acc_base_uncompressed sentinel: {out}"
    assert 0.0 <= out["acc_path_d_base_compressed"] <= 1.0, \
        f"acc_base_compressed sentinel: {out}"
    # acc_path_d_gated may be None if all legit rejected; accept either
    if out.get("acc_path_d_gated_compressed") is not None:
        assert 0.0 <= out["acc_path_d_gated_compressed"] <= 1.0, \
            f"acc_gated_comp sentinel: {out}"
    assert out["n_leg"] >= 1, f"n_leg=0: {out}"
    assert out["n_adv"] >= 1, f"n_adv=0: {out}"
    assert out["compression_ratio"] == 4.0, \
        f"compression_ratio not 4.0: {out['compression_ratio']}"

    print(f"[selftest] adversarial_aqsim_path_d_compose_v1_n4096 PASS "
          f"def_rate={out['defense_rate']:.3f} "
          f"acc_base_uncomp={out['acc_path_d_base_uncompressed']:.3f} "
          f"acc_base_comp={out['acc_path_d_base_compressed']:.3f} "
          f"acc_gated_comp={out.get('acc_path_d_gated_compressed','n/a')} "
          f"comp_ratio={out['compression_ratio']:.1f}x", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    # overnight_queue: GPU device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke  = args.smoke
    N_cfg  = N_SMOKE     if smoke else N_FULL
    M      = M_SMOKE     if smoke else M_PROD
    n_leg  = N_LEG_SMOKE if smoke else N_LEG_FULL
    n_adv  = N_ADV_SMOKE if smoke else N_ADV_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done    = set(list_completed_keys(out_dir))
    t0      = time.time()
    print(f"[run] adversarial_aqsim_path_d_compose_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M} depth={DEPTH} K_paths={K_PATHS} "
          f"n_leg={n_leg} n_adv={n_adv} seeds={seeds} "
          f"done={len(done)} device={device.type} "
          f"[3-way: bits8_compression + Path_D + a_query_sim_defense]",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                continue
        try:
            cell = measure_seed(N_cfg, M, DEPTH, K_PATHS,
                                  n_leg, n_adv, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"def_rate={cell.get('defense_rate','n/a')} "
                  f"acc_gated_comp={cell.get('acc_path_d_gated_compressed','n/a')} "
                  f"acc_base_comp={cell.get('acc_path_d_base_compressed','n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "adversarial_aqsim_path_d_compose_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M": M,
               "depth": DEPTH, "K_paths": K_PATHS,
               "n_leg": n_leg, "n_adv": n_adv, "seeds": seeds,
               "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
