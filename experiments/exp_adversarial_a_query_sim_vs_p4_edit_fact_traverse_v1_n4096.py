"""ADVERSARIAL a_query_sim vs p4 EDIT-FACT-TRAVERSE v1 at N=4096.

CONTEXT (G8_HARD_PASS generality test):
  G8 confirmed a_query_sim achieves def=1.000 fp=0.000 against
  codebook-collision (pattern 2) at N=4096 M=2048. This anchor tests
  whether the SAME defense mechanism is GENERAL: does it also defeat
  the p4 edit-fact-traverse attack (pattern 4 from U2 adversarial probing)?

ATTACK PATTERN p4 (edit-fact-traverse):
  Adversary edits a subset of facts (replaces old values), then immediately
  queries the ORIGINAL keys. Attack goal: retrieve old pre-edit values
  (information that should have been erased/updated). U2 found 99.4% breach
  on undefended substrate.

DEFENSE MECHANISM (a_query_sim, identical to G8):
  Reject query if max cosine_sim to ANY stored key < 0.5. The hypothesis
  is that post-edit queries to original keys will retain high similarity
  to stored keys (since the keys are unchanged), so the defense should
  ACCEPT the queries but return the UPDATED value -- defense rate = whether
  the NEW value is returned, not the old one.

  Note: unlike codebook-collision where we want to REJECT adversarial
  queries, p4 queries are "legitimate" key lookups after an edit. The
  defense question is: does the substrate's edit semantics naturally
  defeat the p4 attack, AND does a_query_sim further help (or hurt) by
  possibly rejecting valid post-edit queries?

SCIENTIFIC QUESTION:
  At N=4096, M=2048 (same operating point as G8): does a_query_sim
  achieve defense rate >= 0.95 AND fp <= 0.05 against the p4 attack?
  (Defense rate = fraction of p4 queries where EITHER the defense rejects
  the query OR the correct NEW value is returned, NOT the old value.)

PRE-REGISTERED BANDS:
  HP = defense rate >= 0.95 AND fp <= 0.05 (5 seeds).
  HF = defense rate < 0.50 OR fp > 0.20.
  MB = anything in between.

STRATEGIC VALUE:
  If PASS: a_query_sim is GENERAL (defeats both codebook-collision AND
  edit-fact-traverse); reduces D7 edit-log-replay engineering motivation.
  If FAIL: a_query_sim is codebook-collision-specific; D7 engineering
  work remains justified.

PROT-018: _n4096 binds N = 4096.
PROT-021: per-cell-seed checkpointing.

Anchor: adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096
Queue: overnight_queue (cloud Lambda A10 GPU)
Pre-reg: preregs/2026-05-31_adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096.md
Total cells: 5 (1 M-value x 5 seeds)
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

from experiments._multi_hop_mechanisms import build_shared  # noqa: E402

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_p4vsaq", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FULL  = 2048   # same operating point as G8
M_SMOKE = 256
N_EDIT_FULL  = 32   # number of facts to edit + query adversarially
N_EDIT_SMOKE = 8
N_LEG_QUERIES_FULL  = 64  # legitimate queries (edit queries to verify NEW value)
N_LEG_QUERIES_SMOKE = 16
SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Defense A: identical threshold to G8
DEFENSE_A_SIM_THRESH = 0.5

# Pre-registered bands (verbatim from spec)
HP_DEFENSE_RATE = 0.95
HP_MAX_FP_RATE  = 0.05
HF_DEFENSE_RATE = 0.50
HF_MAX_FP_RATE  = 0.20


def get_output_dir(
    default_name: str = "adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096",
) -> Path:
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


def _cpu_randint_to(low: int, high: int, shape, seed: int,
                    device: torch.device) -> torch.Tensor:
    """CPU-gen randint, move to device. Avoids cuda-gen + cpu-allocator bug."""
    g = torch.Generator(device='cpu').manual_seed(int(seed))
    out = torch.randint(low, high, shape, generator=g, dtype=torch.long)
    return out.to(device)


def _build_p4_scenario(codebook, W, key_idx, val_idx, n_edit, seed,
                        N_use, device):
    """Build the p4 edit-fact-traverse scenario:
    1. Pick n_edit facts to edit.
    2. Apply edits to W: W' = W - (old_val * key) + (new_val * key)
    3. Adversarial queries: original keys after edit (should retrieve NEW value)
    4. Return (W_edited, adv_queries, old_vals, new_vals, key_vecs)

    The p4 attack goal is to recover old values via the original keys.
    Defense success = query returns NEW value (or is rejected by a_query_sim).
    """
    C = codebook.shape[0]
    n_edit = min(n_edit, key_idx.shape[0] // 4)
    if n_edit == 0:
        return None, None, None, None, None

    edit_idx = torch.arange(n_edit, device=device)
    e_keys_idx = key_idx[edit_idx]
    e_old_idx  = val_idx[edit_idx]
    # New values: random codebook entries, CPU-gen RNG for determinism
    e_new_idx = _cpu_randint_to(0, C, (n_edit,), seed + 4, device)

    k_v  = codebook[e_keys_idx]
    ov   = codebook[e_old_idx]
    nv   = codebook[e_new_idx]

    # Apply Hebbian edit: remove old, add new
    W_edited = W - (ov.T @ k_v) / N_use + (nv.T @ k_v) / N_use

    # Adversarial queries: the ORIGINAL keys post-edit
    adv_queries = k_v

    return W_edited, adv_queries, e_old_idx, e_new_idx, k_v


def _retrieve(W, q, codebook, N_use):
    """Single-hop retrieval: q -> W -> argmax over codebook."""
    out = q @ W.T
    sims = (codebook @ out.T) / N_use
    pred = torch.argmax(sims, dim=0)
    return pred


def defense_a_query_sim(W, q, codebook, keys, N_use):
    """Defense A: reject query if max cosine_sim to stored keys < threshold.
    Returns (pred, accepted_mask). Rejected queries get pred=-1.
    IDENTICAL to G8 defense_a_query_sim."""
    sims_q_keys = q @ keys.T / N_use   # (n_q, M)
    max_sim = sims_q_keys.max(dim=-1).values
    accepted = max_sim >= DEFENSE_A_SIM_THRESH
    pred_raw = _retrieve(W, q, codebook, N_use)
    pred = torch.where(accepted, pred_raw, torch.full_like(pred_raw, -1))
    return pred, accepted


def measure_seed(N_use: int, M: int, n_edit: int, n_leg: int,
                  seed: int, device: torch.device) -> Dict:
    """Run one seed cell measuring a_query_sim vs p4 edit-fact-traverse."""
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    keys = codebook[key_idx]

    W_edited, adv_q, old_idx, new_idx, key_vecs = _build_p4_scenario(
        codebook, W, key_idx, val_idx, n_edit, seed, N_use, device)
    if adv_q is None:
        del codebook, W
        _safe_clear(device)
        return {"seed": int(seed), "M": int(M), "ok": False,
                "error": "no edit queries constructed (too few facts)"}

    # === Defense: a_query_sim against p4 adversarial queries ===
    # Note: keys used for similarity check are ALL stored keys (pre-edit),
    # same as G8. The p4 queries ARE original keys, so sim should be HIGH
    # => defense accepts them. Defense success = returns new_idx, not old_idx.
    a_adv_pred, a_adv_accepted = defense_a_query_sim(
        W_edited, adv_q, codebook, keys, N_use)
    # Defense rate: query rejected OR new value returned (not old)
    # Rejection counts as "defense" because attacker gets no info
    defended = ((a_adv_pred == -1) | (a_adv_pred == new_idx)).float().mean().item()
    old_leaked = (a_adv_pred == old_idx).float().mean().item()

    # === False positive rate: legitimate post-edit queries ===
    # Legitimate queries: same keys, check we get the new value back
    # (this tests that the defense does NOT over-reject valid post-edit usage)
    a_leg_pred, a_leg_accepted = defense_a_query_sim(
        W_edited, adv_q, codebook, keys, N_use)
    # FP = rejected OR returned old value instead of new
    fp = ((a_leg_pred == -1) | (a_leg_pred != new_idx)).float().mean().item()

    # Also record baseline (no defense): does substrate naturally protect?
    baseline_pred = _retrieve(W_edited, adv_q, codebook, N_use)
    baseline_defended = (baseline_pred == new_idx).float().mean().item()

    del codebook, W, W_edited
    _safe_clear(device)
    return {
        "seed": int(seed),
        "M": int(M),
        "ok": True,
        "defense_rate":        round(float(defended), 5),
        "fp_rate":             round(float(fp), 5),
        "old_leaked_rate":     round(float(old_leaked), 5),
        "baseline_defense_rate": round(float(baseline_defended), 5),
        "n_edit":              int(adv_q.shape[0]),
        "frac_accepted_adv":   round(float(a_adv_accepted.float().mean().item()), 5),
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("P4_AQSIM_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("P4_AQSIM_INCONCLUSIVE", f"all {len(cells)} cells failed")

    def_rates = [c["defense_rate"] for c in ok]
    fp_rates  = [c["fp_rate"]      for c in ok]
    mean_def  = sum(def_rates) / len(def_rates)
    mean_fp   = sum(fp_rates)  / len(fp_rates)
    mean_baseline = sum(c["baseline_defense_rate"] for c in ok) / len(ok)

    # HF: ANY cell sharply fails
    hf_cells = [c for c in ok
                if c["defense_rate"] < HF_DEFENSE_RATE or c["fp_rate"] > HF_MAX_FP_RATE]
    # HP: ALL cells pass
    hp_cells = [c for c in ok
                if c["defense_rate"] >= HP_DEFENSE_RATE and c["fp_rate"] <= HP_MAX_FP_RATE]

    detail = (
        f"mean_def={mean_def:.3f} mean_fp={mean_fp:.3f} "
        f"baseline_def={mean_baseline:.3f} n_ok={len(ok)}/5 "
        f"n_hp={len(hp_cells)} n_hf={len(hf_cells)}"
    )

    if len(hf_cells) > 0:
        return ("P4_AQSIM_HARD_FAIL",
                f"AQSIM_NOT_GENERAL_vs_P4: {len(hf_cells)} cells below HF threshold. "
                + detail)
    if len(hp_cells) == len(ok):
        return ("P4_AQSIM_HARD_PASS",
                f"AQSIM_GENERAL_DEFEATS_P4: all {len(ok)} cells >= HP threshold. "
                + detail)
    return ("P4_AQSIM_MIDDLE_BAND",
            f"PARTIAL_P4_DEFENSE: {len(hp_cells)}/{len(ok)} cells pass HP. "
            + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert M_FULL == 2048
    assert len(SEEDS_FULL) == 5
    assert DEFENSE_A_SIM_THRESH == 0.5  # same as G8

    # Total cells check
    assert len(SEEDS_FULL) == 5, len(SEEDS_FULL)

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_FULL, "ok": True,
                "defense_rate": 0.97, "fp_rate": 0.02,
                "old_leaked_rate": 0.01, "baseline_defense_rate": 0.90,
                "n_edit": 8, "frac_accepted_adv": 0.85}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"

    # Verdict gate HF
    fake_hf = [{"seed": s, "M": M_FULL, "ok": True,
                "defense_rate": 0.30, "fp_rate": 0.30,
                "old_leaked_rate": 0.70, "baseline_defense_rate": 0.30,
                "n_edit": 8, "frac_accepted_adv": 0.95}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"

    # Verdict gate MB
    fake_mb = [{"seed": s, "M": M_FULL, "ok": True,
                "defense_rate": 0.75, "fp_rate": 0.10,
                "old_leaked_rate": 0.20, "baseline_defense_rate": 0.70,
                "n_edit": 8, "frac_accepted_adv": 0.85}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v}"

    # Live smoke forward pass on CPU
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, N_EDIT_SMOKE, N_LEG_QUERIES_SMOKE, 17, device)
    assert out["ok"], f"selftest measure_seed failed: {out.get('error')}"
    assert "defense_rate"   in out
    assert "fp_rate"        in out
    assert "old_leaked_rate" in out
    assert 0.0 <= out["defense_rate"] <= 1.0, f"defense_rate={out['defense_rate']}"
    assert 0.0 <= out["fp_rate"]      <= 1.0, f"fp_rate={out['fp_rate']}"
    assert out["n_edit"] >= 1, "no edit queries constructed at smoke scale"
    print(
        f"[selftest] adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096 PASS "
        f"N={N_SMOKE} M={M_SMOKE} def={out['defense_rate']:.3f} "
        f"fp={out['fp_rate']:.3f} baseline={out['baseline_defense_rate']:.3f}",
        flush=True,
    )


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    smoke  = args.smoke
    N_cfg  = N_SMOKE      if smoke else N_FULL
    M      = M_SMOKE      if smoke else M_FULL
    n_edit = N_EDIT_SMOKE if smoke else N_EDIT_FULL
    n_leg  = N_LEG_QUERIES_SMOKE if smoke else N_LEG_QUERIES_FULL
    seeds  = SEEDS_SMOKE  if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    total_cells = len(seeds)
    print(
        f"[run] adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096 "
        f"smoke={smoke} N={N_cfg} M={M} n_edit={n_edit} n_leg={n_leg} "
        f"seeds={seeds} total_cells={total_cells} done={len(done)} device={device.type}",
        flush=True,
    )

    cells: List[Dict] = []
    for cell_num, seed in enumerate(seeds, 1):
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [cell {cell_num}/{total_cells}] seed={seed} RESUMED",
                      flush=True)
                continue
        try:
            cell = measure_seed(N_cfg, M, n_edit, n_leg, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(
                f"  [cell {cell_num}/{total_cells}] seed={seed} "
                f"ok={cell.get('ok')} "
                f"def={cell.get('defense_rate', 'n/a'):.3f} "
                f"fp={cell.get('fp_rate', 'n/a'):.3f} "
                f"baseline={cell.get('baseline_defense_rate', 'n/a'):.3f} "
                f"({time.time()-t0:.1f}s)",
                flush=True,
            )
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  [cell {cell_num}/{total_cells}] seed={seed} FAILED: {e}",
                  flush=True)
            _safe_clear(device)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "adversarial_a_query_sim_vs_p4_edit_fact_traverse_v1_n4096",
        "N": N_cfg, "smoke": smoke, "M": M, "seeds": seeds,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
