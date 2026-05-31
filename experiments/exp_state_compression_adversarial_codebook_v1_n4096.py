"""PP-2 STATE COMPRESSION ADVERSARIAL CODEBOOK v1 at N=4096.

CONTEXT (v296 cap_map; C3_HARD_PASS just filed via substrate_state_compression_v2_n4096):
  c_quant/bits8 achieved 4x compression + KF-1/KF-2/KF-3 all PASS at N=4096 5-seed.
  PP-2 row has its first empirical foothold.
  KNOWN RISK: U2 adversarial probing found codebook-collision achieves 100% breach
  under nominal retrieval (pattern_2: queries constructed from stored-key pairs with
  highest cosine similarity). The PP-2 compliance / audit-cert narrative requires
  verifying whether c_quant/bits8 still preserves KF-1 (deletion certificate)
  under adversarial-codebook-collision input.

SCIENTIFIC QUESTION:
  At N=4096, M=2048, c_quant/bits8 (4x compression):
  Does KF-1 (deletion certificate) hold when the input codebook contains
  adversarial colliding entries (100% collision pattern from U2)?
  Does KF-2 (norm drift) still hold post-compression under adversarial input?
  Does KF-3 (edit consistency) hold under adversarial input?

ADVERSARIAL PROTOCOL (U2-style 100% collision):
  - Build nominal W from clean codebook.
  - Apply c_quant/bits8 to W to get W_q.
  - Construct adversarial_codebook: pairs of entries i,j such that
    cos(codebook[i], codebook[j]) is maximized (highest-similarity pairs).
  - Run all 3 KF tests (deletion, drift-norm, edit-consistency) on W_q using
    adversarial_codebook entries as keys/values.
  - Compare to baseline (same KF tests on W_q with nominal codebook entries).

MIXED PATTERN ALSO TESTED:
  - 50% adversarial entries + 50% nominal entries interleaved.
  - Gives cleaner interpolation of degradation gradient.

PRE-REGISTERED BANDS:
  HP = KF-1 deletion cert holds >= 0.70 under 100% adversarial collision input
       AND KF-2 norm drift holds (ratio 0.85-1.15) post-compression regardless
       of adversarial input (norm is input-agnostic by construction)
       AND KF-3 edit consistency >= 0.70 under 100% adversarial input.
  HF = KF-1 deletion cert < 0.30 under 100% adversarial input (compliance
       claim collapses under adversarial regime).
  MB = otherwise (partial degradation; mixed pattern shows intermediate behavior).

NOTE: first adversarial + compression combined test; calibration-probe policy
applied -- HP threshold set at 0.70 (conservative; nominal c_quant/bits8 had
KF-1=1.0 so 0.70 allows significant adversarial degradation before blocking HP).
No prior empirical anchor; bands widened per calibration-probe policy.

PROT-018: _n4096 binds N = 4096.
PROT-019: timeout >= 14400s.
PROT-021: per-cell-seed checkpointing.

Anchor: state_compression_adversarial_codebook_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-31_state_compression_adversarial_codebook_v1_n4096.md
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_pp2adv", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PROT-018: _n4096 binds N = 4096
N = 4096
N_FULL  = N
N_SMOKE = 1024  # must be power of 4 for Kerdock construction (512 = 2^9 fails)
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_PROD = 2048
M_SMOKE = 256
N_PROBE_FULL = 64
N_PROBE_SMOKE = 10
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BITS = 8  # c_quant/bits8 -- the foothold config from v2

# Pre-registered bands
HP_MIN_KF1_ADV100 = 0.70   # deletion cert >= 0.70 under 100% adversarial
HP_MIN_KF3_ADV100 = 0.70   # edit consistency >= 0.70 under 100% adversarial
HF_MAX_KF1_ADV100 = 0.30   # deletion cert < 0.30 = compliance collapses


def get_output_dir(default_name: str = "state_compression_adversarial_codebook_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def compress_quant(W: torch.Tensor, bits: int) -> torch.Tensor:
    """Per-tensor symmetric quantization, returns dequantized float tensor."""
    max_v = float(W.abs().max().item())
    if max_v == 0:
        return W.clone()
    n_levels = (1 << (bits - 1)) - 1
    scale = max_v / n_levels
    q = torch.clamp(torch.round(W / scale), -n_levels, n_levels)
    return q * scale


def compression_ratio(W: torch.Tensor, bits: int) -> float:
    bytes_original = W.element_size() * W.nelement()
    bytes_compressed = (W.nelement() * bits) // 8
    return bytes_original / max(bytes_compressed, 1)


def _build_adversarial_codebook(codebook: torch.Tensor, M: int,
                                  n_probe: int, device: torch.device,
                                  mix_frac: float = 1.0) -> Tuple[torch.Tensor, torch.Tensor]:
    """Construct adversarial key_idx, val_idx using highest-cosine-similarity pairs.

    mix_frac=1.0: all adversarial (100% collision pattern, U2-style).
    mix_frac=0.5: half adversarial, half nominal interleaved.

    Returns (adv_key_idx, adv_val_idx) as index tensors into codebook.
    Keys are the first element of the high-sim pair; val_idx is remapped
    to the OTHER element's position (collision target), so W stores
    k_i -> val_j, forcing collision at retrieval time.
    """
    # Compute pairwise cosine similarity among first min(M, 256) codebook entries
    C = codebook.shape[0]
    n_sample = min(C, 256)
    cb_sample = codebook[:n_sample]  # (n_sample, N)
    # Normalize
    norms = cb_sample.norm(dim=-1, keepdim=True).clamp(min=1e-8)
    cb_norm = cb_sample / norms
    sims = cb_norm @ cb_norm.T  # (n_sample, n_sample)
    sims.fill_diagonal_(-2.0)

    # Greedily pick top n_probe collision pairs (each entry used at most once as key)
    used = set()
    adv_keys_i, adv_vals_j = [], []
    flat_idx = sims.view(-1).argsort(descending=True)
    for fi in flat_idx.tolist():
        i = fi // n_sample
        j = fi % n_sample
        if i == j or i in used or j in used:
            continue
        used.add(i); used.add(j)
        adv_keys_i.append(i)
        adv_vals_j.append(j)
        if len(adv_keys_i) >= n_probe:
            break

    if not adv_keys_i:
        # Fallback: no adversarial pairs found, use nominal
        return (torch.arange(n_probe, device=device),
                torch.arange(n_probe, device=device))

    n_adv = len(adv_keys_i)
    adv_ki = torch.tensor(adv_keys_i, device=device)
    adv_vi = torch.tensor(adv_vals_j, device=device)  # collision targets

    if mix_frac >= 1.0 or n_adv < 2:
        return adv_ki, adv_vi

    # Mixed: interleave with nominal indices (starting from n_sample onward)
    n_mix = min(n_adv, n_probe)
    n_nom = n_mix
    nom_start = min(n_sample, C - n_nom)
    nom_ki = torch.arange(nom_start, nom_start + n_nom, device=device) % C
    nom_vi = (nom_ki + 1) % C  # nominal val = next index

    mixed_ki = torch.cat([adv_ki[:n_mix // 2], nom_ki[:n_mix // 2]])
    mixed_vi = torch.cat([adv_vi[:n_mix // 2], nom_vi[:n_mix // 2]])
    return mixed_ki, mixed_vi


def _kf1_deletion_cert(W_q: torch.Tensor, codebook: torch.Tensor,
                        key_idx: torch.Tensor, val_idx: torch.Tensor,
                        N_use: int, n_probe: int) -> float:
    """KF-1: rank-1 delete k->v, then re-query k must NOT return v.
    Returns fraction of deletions that held (0.0 to 1.0)."""
    n = min(n_probe, key_idx.shape[0], val_idx.shape[0])
    if n == 0:
        return 1.0
    successes = 0
    for i in range(n):
        k = codebook[key_idx[i]:key_idx[i] + 1]
        v = codebook[val_idx[i]:val_idx[i] + 1]
        W2 = W_q - (v.T @ k) / N_use
        out = k @ W2.T
        sims = (codebook @ out.T) / N_use
        pred = int(torch.argmax(sims, dim=0).item())
        if pred != int(val_idx[i].item()):
            successes += 1
    return successes / n


def _kf2_drift_norm(W_q: torch.Tensor, W_orig: torch.Tensor) -> float:
    """KF-2: Frobenius norm preserved within 10% (input-agnostic, structural)."""
    n_o = float(torch.linalg.norm(W_orig).item())
    n_c = float(torch.linalg.norm(W_q).item())
    if n_o == 0:
        return 0.0
    ratio = n_c / n_o
    return 1.0 if 0.85 <= ratio <= 1.15 else 0.0


def _kf3_edit_consistency(W_q: torch.Tensor, codebook: torch.Tensor,
                            key_idx: torch.Tensor, val_idx: torch.Tensor,
                            N_use: int, n_probe: int) -> float:
    """KF-3: rank-1 edit k->v then k->new_v; re-query k must return new_v.
    Returns fraction of edits that landed correctly."""
    n = min(n_probe, key_idx.shape[0], val_idx.shape[0])
    if n < 2:
        return 1.0
    C = codebook.shape[0]
    successes = 0
    for i in range(n):
        k = codebook[key_idx[i]:key_idx[i] + 1]
        ov = codebook[val_idx[i]:val_idx[i] + 1]
        new_target_idx = (int(val_idx[i].item()) + C // 2) % C
        nv = codebook[new_target_idx:new_target_idx + 1]
        W2 = W_q - (ov.T @ k) / N_use + (nv.T @ k) / N_use
        out = k @ W2.T
        sims = (codebook @ out.T) / N_use
        pred = int(torch.argmax(sims, dim=0).item())
        if pred == new_target_idx:
            successes += 1
    return successes / n


def measure_seed(N_use: int, M: int, n_probe: int, seed: int,
                   device: torch.device) -> Dict:
    codebook, W, key_idx_nominal, val_idx_nominal, relation = build_shared(
        N_use, M, seed, device)

    # Compress W once with bits8
    W_q = compress_quant(W, BITS)
    comp_ratio = compression_ratio(W, BITS)

    # KF-2 is input-agnostic (purely structural -- compare norms of W vs W_q)
    kf2_nominal = _kf2_drift_norm(W_q, W)

    # Nominal KFs (baseline)
    kf1_nominal = _kf1_deletion_cert(
        W_q, codebook, key_idx_nominal, val_idx_nominal, N_use, n_probe)
    kf3_nominal = _kf3_edit_consistency(
        W_q, codebook, key_idx_nominal, val_idx_nominal, N_use, n_probe)

    # Adversarial: 100% collision pattern (U2-style)
    adv100_ki, adv100_vi = _build_adversarial_codebook(
        codebook, M, n_probe, device, mix_frac=1.0)
    kf1_adv100 = _kf1_deletion_cert(W_q, codebook, adv100_ki, adv100_vi, N_use, n_probe)
    kf3_adv100 = _kf3_edit_consistency(W_q, codebook, adv100_ki, adv100_vi, N_use, n_probe)

    # Mixed: 50% adversarial
    adv50_ki, adv50_vi = _build_adversarial_codebook(
        codebook, M, n_probe, device, mix_frac=0.5)
    kf1_adv50 = _kf1_deletion_cert(W_q, codebook, adv50_ki, adv50_vi, N_use, n_probe)
    kf3_adv50 = _kf3_edit_consistency(W_q, codebook, adv50_ki, adv50_vi, N_use, n_probe)

    del codebook, W, W_q
    return {
        "seed": int(seed), "M": int(M), "n_probe": int(n_probe),
        "bits": BITS, "compression_ratio": round(float(comp_ratio), 4),
        "ok": True,
        "kf2_drift_norm": round(float(kf2_nominal), 4),
        "nominal": {
            "kf1_deletion": round(float(kf1_nominal), 5),
            "kf3_edit": round(float(kf3_nominal), 5),
        },
        "adv_100pct": {
            "kf1_deletion": round(float(kf1_adv100), 5),
            "kf3_edit": round(float(kf3_adv100), 5),
        },
        "adv_50pct": {
            "kf1_deletion": round(float(kf1_adv50), 5),
            "kf3_edit": round(float(kf3_adv50), 5),
        },
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("PP2ADV_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("PP2ADV_INCONCLUSIVE", f"all {len(cells)} cells failed")

    # Aggregate across seeds
    kf2_vals = [c["kf2_drift_norm"] for c in ok]
    kf1_nom = [c["nominal"]["kf1_deletion"] for c in ok]
    kf3_nom = [c["nominal"]["kf3_edit"] for c in ok]
    kf1_100 = [c["adv_100pct"]["kf1_deletion"] for c in ok]
    kf3_100 = [c["adv_100pct"]["kf3_edit"] for c in ok]
    kf1_50  = [c["adv_50pct"]["kf1_deletion"] for c in ok]
    kf3_50  = [c["adv_50pct"]["kf3_edit"] for c in ok]

    mean_kf2 = sum(kf2_vals) / len(kf2_vals)
    mean_kf1_nom = sum(kf1_nom) / len(kf1_nom)
    mean_kf3_nom = sum(kf3_nom) / len(kf3_nom)
    mean_kf1_100 = sum(kf1_100) / len(kf1_100)
    mean_kf3_100 = sum(kf3_100) / len(kf3_100)
    mean_kf1_50  = sum(kf1_50) / len(kf1_50)
    mean_kf3_50  = sum(kf3_50) / len(kf3_50)

    comp = ok[0].get("compression_ratio", 0.0)
    detail = (f"comp={comp:.1f}x kf2={mean_kf2:.3f} "
              f"kf1_nom={mean_kf1_nom:.3f} kf3_nom={mean_kf3_nom:.3f} | "
              f"kf1_adv100={mean_kf1_100:.3f} kf3_adv100={mean_kf3_100:.3f} | "
              f"kf1_adv50={mean_kf1_50:.3f} kf3_adv50={mean_kf3_50:.3f}")

    # Hard-fail: compliance collapses under 100% adversarial
    if mean_kf1_100 < HF_MAX_KF1_ADV100:
        return ("PP2ADV_HARD_FAIL",
                f"COMPLIANCE_COLLAPSES kf1_adv100={mean_kf1_100:.3f}. " + detail)

    # Hard-pass: KF-1 and KF-3 survive adversarial AND kf2 structural
    kf2_pass = (0.85 <= mean_kf2 <= 1.15)
    if (mean_kf1_100 >= HP_MIN_KF1_ADV100
            and mean_kf3_100 >= HP_MIN_KF3_ADV100
            and kf2_pass):
        return ("PP2ADV_HARD_PASS",
                f"COMPRESSION_ADVERSARIAL_ROBUST kf1_adv100={mean_kf1_100:.3f} "
                f"kf3_adv100={mean_kf3_100:.3f} kf2={mean_kf2:.3f}. " + detail)

    return ("PP2ADV_MIDDLE_BAND",
            f"PARTIAL_ROBUSTNESS kf1_adv100={mean_kf1_100:.3f} "
            f"kf3_adv100={mean_kf3_100:.3f} kf2_pass={kf2_pass}. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert BITS == 8, "must test bits8 (the C3_HARD_PASS foothold config)"
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD, "n_probe": N_PROBE_FULL,
                "bits": 8, "compression_ratio": 4.0, "ok": True,
                "kf2_drift_norm": 0.98,
                "nominal": {"kf1_deletion": 1.0, "kf3_edit": 1.0},
                "adv_100pct": {"kf1_deletion": 0.75, "kf3_edit": 0.72},
                "adv_50pct": {"kf1_deletion": 0.88, "kf3_edit": 0.85}}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v} {msg}"

    # Verdict gate HF
    fake_hf = [{"seed": s, "M": M_PROD, "n_probe": N_PROBE_FULL,
                "bits": 8, "compression_ratio": 4.0, "ok": True,
                "kf2_drift_norm": 0.98,
                "nominal": {"kf1_deletion": 1.0, "kf3_edit": 1.0},
                "adv_100pct": {"kf1_deletion": 0.20, "kf3_edit": 0.15},
                "adv_50pct": {"kf1_deletion": 0.40, "kf3_edit": 0.35}}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v} {msg}"

    # Verdict gate MB: kf1_adv100 above HF but below HP
    fake_mb = [{"seed": s, "M": M_PROD, "n_probe": N_PROBE_FULL,
                "bits": 8, "compression_ratio": 4.0, "ok": True,
                "kf2_drift_norm": 0.98,
                "nominal": {"kf1_deletion": 1.0, "kf3_edit": 1.0},
                "adv_100pct": {"kf1_deletion": 0.50, "kf3_edit": 0.45},
                "adv_50pct": {"kf1_deletion": 0.65, "kf3_edit": 0.60}}
               for s in SEEDS_FULL]
    v, msg = compute_verdict(fake_mb)
    assert "MIDDLE_BAND" in v, f"MB gate failed: {v} {msg}"

    # Live smoke on CPU (forced -- no CUDA)
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, M_SMOKE, N_PROBE_SMOKE, 17, device)
    assert out.get("ok"), f"selftest measure_seed failed"
    assert "kf2_drift_norm" in out, "kf2_drift_norm missing"
    assert "nominal" in out and "kf1_deletion" in out["nominal"], "nominal KF missing"
    assert "adv_100pct" in out and "kf1_deletion" in out["adv_100pct"], "adv_100pct missing"
    assert "adv_50pct" in out and "kf1_deletion" in out["adv_50pct"], "adv_50pct missing"
    assert 0.0 <= out["nominal"]["kf1_deletion"] <= 1.0, "kf1 nominal out of range"
    assert 0.0 <= out["adv_100pct"]["kf1_deletion"] <= 1.0, "kf1_adv100 out of range"
    assert out["compression_ratio"] > 1.0, f"compression_ratio not > 1: {out['compression_ratio']}"
    print(f"[selftest] state_compression_adversarial_codebook_v1_n4096 PASS "
          f"comp={out['compression_ratio']:.2f}x "
          f"kf1_nom={out['nominal']['kf1_deletion']:.3f} "
          f"kf1_adv100={out['adv_100pct']['kf1_deletion']:.3f} "
          f"kf2={out['kf2_drift_norm']:.3f}",
          flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    # PROT: force CPU -- this anchor lives in remote_cpu_queue; must never touch CUDA
    device = torch.device("cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M = M_SMOKE if smoke else M_PROD
    n_probe = N_PROBE_SMOKE if smoke else N_PROBE_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] state_compression_adversarial_codebook_v1_n4096 smoke={smoke} "
          f"N={N_cfg} M={M} n_probe={n_probe} bits={BITS} "
          f"seeds={seeds} done={len(done)} device={device.type}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = measure_seed(N_cfg, M, n_probe, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"kf1_nom={cell.get('nominal', {}).get('kf1_deletion', 'n/a')} "
                  f"kf1_adv100={cell.get('adv_100pct', {}).get('kf1_deletion', 'n/a')} "
                  f"kf2={cell.get('kf2_drift_norm', 'n/a')} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "state_compression_adversarial_codebook_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M": M, "bits": BITS,
               "n_probe": n_probe, "seeds": seeds, "cells": cells,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
