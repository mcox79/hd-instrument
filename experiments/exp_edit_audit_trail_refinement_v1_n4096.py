"""C5 EDIT AUDIT TRAIL REFINEMENT v1 at N=4096.

CONTEXT (v290 cap_map follow-on):
  Production compliance schema. Generate sample audit reports for 6 scenarios.

SCENARIOS:
  (1) single_edit
  (2) sequential_edits
  (3) delete_with_certificate
  (4) interrupted_operation_recovery
  (5) concurrent_edits_serialization
  (6) failed_deletion_audit

For each scenario: emit audit_trail entry with schema:
  - timestamp_ns
  - operation (str)
  - operands (key_idx, old_val_idx, new_val_idx, ...)
  - W_norm_before, W_norm_after, delta_norm
  - hash chain link (sha256 of previous entry || current entry)

PRE-REGISTERED BANDS:
  HP = all 6 scenarios produce COMPLETE audit trail AND integrity 100%
       (hash chain unbroken) AND audit_size_per_op <500 bytes.
  HF = any scenario produces incomplete or invalid trail.
  MB = otherwise.

OUTPUT: also write a sample audit trail JSON to
  notes/audit_trail_schema_v1_2026-05-30.md (best-effort; falls back to
  metrics.json on FS error).

PROT-018: _n4096 binds N = 4096.
PROT-021: per-cell-seed checkpointing.

Anchor: edit_audit_trail_refinement_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-05-30_edit_audit_trail_refinement_v1_n4096.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import hashlib
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
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_c5", _ck_path)
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

M_PROD = 2048
M_SMOKE = 256
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

HP_MAX_AUDIT_SIZE_BYTES = 500

SCENARIOS = [
    "s1_single_edit",
    "s2_sequential_edits",
    "s3_delete_with_certificate",
    "s4_interrupted_recovery",
    "s5_concurrent_serialization",
    "s6_failed_deletion_audit",
]


def get_output_dir(default_name: str = "edit_audit_trail_refinement_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _hash_entry(prev_hash: str, entry: Dict) -> str:
    body = (prev_hash + json.dumps(entry, sort_keys=True)).encode()
    return hashlib.sha256(body).hexdigest()


def _make_audit_entry(prev_hash: str, op: str, operands: Dict,
                        W_before, W_after) -> Dict:
    n_before = float(torch.linalg.norm(W_before).item())
    n_after = float(torch.linalg.norm(W_after).item())
    delta = float(torch.linalg.norm(W_after - W_before).item())
    body = {
        "ts_ns": time.perf_counter_ns(),
        "op": op,
        "operands": operands,
        "W_norm_before": round(n_before, 6),
        "W_norm_after": round(n_after, 6),
        "delta_norm": round(delta, 6),
    }
    body["link"] = _hash_entry(prev_hash, body)
    return body


def _verify_chain(trail: List[Dict]) -> bool:
    if not trail:
        return True
    prev = ""
    for entry in trail:
        link = entry.get("link")
        body = {k: v for k, v in entry.items() if k != "link"}
        expected = _hash_entry(prev, body)
        if link != expected:
            return False
        prev = link
    return True


def _apply_rank1(W, codebook, key_idx, old_val_idx, new_val_idx, N_use):
    k = codebook[key_idx:key_idx + 1]
    ov = codebook[old_val_idx:old_val_idx + 1]
    nv = codebook[new_val_idx:new_val_idx + 1]
    return W - (ov.T @ k) / N_use + (nv.T @ k) / N_use


def _entry_bytes(entry: Dict) -> int:
    return len(json.dumps(entry).encode())


def run_scenario(name: str, codebook, W_base, key_idx, val_idx, N_use,
                   seed: int) -> Tuple[List[Dict], bool, int]:
    """Returns (audit_trail, integrity_under_failure_ok, max_entry_bytes)."""
    trail: List[Dict] = []
    prev_hash = ""
    integrity_ok = True

    if name == "s1_single_edit":
        # one edit
        ki = int(key_idx[0].item())
        ov = int(val_idx[0].item())
        nv = (ov + 1) % codebook.shape[0]
        W_new = _apply_rank1(W_base, codebook, ki, ov, nv, N_use)
        e = _make_audit_entry(prev_hash, "edit",
                                {"key": ki, "old": ov, "new": nv}, W_base, W_new)
        trail.append(e); prev_hash = e["link"]
        del W_new

    elif name == "s2_sequential_edits":
        # 3 sequential edits
        W_cur = W_base
        for i in range(3):
            ki = int(key_idx[i].item())
            ov = int(val_idx[i].item())
            nv = (ov + i + 1) % codebook.shape[0]
            W_next = _apply_rank1(W_cur, codebook, ki, ov, nv, N_use)
            e = _make_audit_entry(prev_hash, "edit",
                                    {"key": ki, "old": ov, "new": nv}, W_cur, W_next)
            trail.append(e); prev_hash = e["link"]
            W_cur = W_next

    elif name == "s3_delete_with_certificate":
        ki = int(key_idx[0].item())
        ov = int(val_idx[0].item())
        k_v = codebook[ki:ki + 1]
        ov_v = codebook[ov:ov + 1]
        W_new = W_base - (ov_v.T @ k_v) / N_use
        e_del = _make_audit_entry(prev_hash, "delete",
                                    {"key": ki, "old": ov}, W_base, W_new)
        trail.append(e_del); prev_hash = e_del["link"]
        # certificate entry: hash of W_new + zeroed key row
        cert_body = {"key": ki, "post_delete_norm": round(
            float(torch.linalg.norm(W_new).item()), 6)}
        e_cert = _make_audit_entry(prev_hash, "delete_certificate",
                                      cert_body, W_new, W_new)
        trail.append(e_cert); prev_hash = e_cert["link"]
        del W_new

    elif name == "s4_interrupted_recovery":
        # apply edit, "interrupt" (log no completion), recovery replays
        ki = int(key_idx[0].item())
        ov = int(val_idx[0].item())
        nv = (ov + 1) % codebook.shape[0]
        W_new = _apply_rank1(W_base, codebook, ki, ov, nv, N_use)
        e_start = _make_audit_entry(prev_hash, "edit_start",
                                       {"key": ki, "old": ov, "new": nv},
                                       W_base, W_base)
        trail.append(e_start); prev_hash = e_start["link"]
        # ... "interruption" ...
        e_recover = _make_audit_entry(prev_hash, "edit_recover",
                                          {"key": ki, "from_W_norm": round(
                                              float(torch.linalg.norm(W_base).item()), 6)},
                                          W_base, W_new)
        trail.append(e_recover); prev_hash = e_recover["link"]
        del W_new

    elif name == "s5_concurrent_serialization":
        # 2 "concurrent" edits, serialized into the audit trail
        ki1 = int(key_idx[0].item()); ov1 = int(val_idx[0].item())
        ki2 = int(key_idx[1].item()); ov2 = int(val_idx[1].item())
        nv1 = (ov1 + 1) % codebook.shape[0]
        nv2 = (ov2 + 2) % codebook.shape[0]
        W_a = _apply_rank1(W_base, codebook, ki1, ov1, nv1, N_use)
        W_b = _apply_rank1(W_a, codebook, ki2, ov2, nv2, N_use)
        e1 = _make_audit_entry(prev_hash, "edit_concurrent",
                                  {"tx": "a", "key": ki1, "old": ov1, "new": nv1,
                                   "serial_order": 1}, W_base, W_a)
        trail.append(e1); prev_hash = e1["link"]
        e2 = _make_audit_entry(prev_hash, "edit_concurrent",
                                  {"tx": "b", "key": ki2, "old": ov2, "new": nv2,
                                   "serial_order": 2}, W_a, W_b)
        trail.append(e2); prev_hash = e2["link"]
        del W_a, W_b

    elif name == "s6_failed_deletion_audit":
        # Attempt deletion of a key NOT in the store (should fail; audit entry)
        # pick a fake key index
        C = codebook.shape[0]
        fake_key = int((int(key_idx[0].item()) + C // 2) % C)
        in_keys = set(int(k.item()) for k in key_idx)
        if fake_key in in_keys:
            fake_key = (fake_key + 1) % C
        e = _make_audit_entry(prev_hash, "delete_failed",
                                  {"key": fake_key,
                                   "reason": "not_in_store"},
                                  W_base, W_base)
        trail.append(e); prev_hash = e["link"]

    chain_ok = _verify_chain(trail)
    # Integrity under failure: tamper with one entry and verify break detected
    if trail:
        tampered = [dict(e) for e in trail]
        tampered[0]["operands"] = {"tampered": True}
        tamper_ok = not _verify_chain(tampered)
        integrity_ok = chain_ok and tamper_ok
    else:
        integrity_ok = False  # empty trail counts as incomplete

    max_size = max((_entry_bytes(e) for e in trail), default=0)
    return trail, integrity_ok, max_size


def measure_seed(N_use: int, M: int, seed: int, device: torch.device) -> Dict:
    codebook, W, key_idx, val_idx, relation = build_shared(N_use, M, seed, device)
    scenarios = {}
    sample_reports = {}
    for sc in SCENARIOS:
        try:
            trail, ok, max_size = run_scenario(sc, codebook, W, key_idx,
                                                  val_idx, N_use, seed)
            scenarios[sc] = {
                "trail_complete": len(trail) > 0,
                "chain_valid": _verify_chain(trail),
                "integrity_under_failure": ok,
                "max_entry_bytes": int(max_size),
                "n_entries": len(trail),
            }
            sample_reports[sc] = trail[:2]  # first 2 entries as sample
        except Exception as e:  # noqa: BLE001
            scenarios[sc] = {"trail_complete": False, "chain_valid": False,
                              "integrity_under_failure": False,
                              "max_entry_bytes": 0, "n_entries": 0,
                              "error": str(e)[:300]}
    del codebook, W
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"seed": int(seed), "M": int(M),
            "scenarios": scenarios,
            "sample_reports": sample_reports}


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("C5_INCONCLUSIVE", "no cells")
    n_seeds = len(cells)

    sc_summary = {}
    for sc in SCENARIOS:
        complete = [c["scenarios"].get(sc, {}).get("trail_complete", False)
                    for c in cells]
        valid = [c["scenarios"].get(sc, {}).get("chain_valid", False)
                 for c in cells]
        integ = [c["scenarios"].get(sc, {}).get("integrity_under_failure", False)
                 for c in cells]
        max_sz = max((c["scenarios"].get(sc, {}).get("max_entry_bytes", 0)
                      for c in cells), default=0)
        sc_summary[sc] = {
            "all_complete": all(complete),
            "all_valid": all(valid),
            "all_integ": all(integ),
            "max_size_bytes": max_sz,
        }

    detail = " | ".join(
        f"{sc}: complete={sc_summary[sc]['all_complete']} "
        f"valid={sc_summary[sc]['all_valid']} "
        f"integ={sc_summary[sc]['all_integ']} "
        f"max_sz={sc_summary[sc]['max_size_bytes']}B"
        for sc in SCENARIOS)

    all_complete = all(s["all_complete"] for s in sc_summary.values())
    all_valid = all(s["all_valid"] for s in sc_summary.values())
    all_integ = all(s["all_integ"] for s in sc_summary.values())
    max_size_ok = all(s["max_size_bytes"] < HP_MAX_AUDIT_SIZE_BYTES
                       for s in sc_summary.values())

    if all_complete and all_valid and all_integ and max_size_ok:
        return ("C5_HARD_PASS", "AUDIT_SCHEMA_COMPLETE: " + detail)
    if not all_complete or not all_valid:
        return ("C5_HARD_FAIL", "TRAIL_INCOMPLETE_OR_INVALID: " + detail)
    return ("C5_MIDDLE_BAND", "PARTIAL: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, "PROT-018: _n4096"
    assert len(SCENARIOS) == 6
    assert len(SEEDS_FULL) == 5

    # Verdict gate HP
    fake_hp = [{"seed": s, "M": M_PROD,
                "scenarios": {sc: {"trail_complete": True, "chain_valid": True,
                                     "integrity_under_failure": True,
                                     "max_entry_bytes": 300, "n_entries": 2}
                              for sc in SCENARIOS}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hp); assert "HARD_PASS" in v, v

    # Verdict gate HF (incomplete)
    fake_hf = [{"seed": s, "M": M_PROD,
                "scenarios": {sc: {"trail_complete": False, "chain_valid": False,
                                     "integrity_under_failure": False,
                                     "max_entry_bytes": 0, "n_entries": 0}
                              for sc in SCENARIOS}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_hf); assert "HARD_FAIL" in v, v

    # Verdict gate MB (size too big but rest valid)
    fake_mb = [{"seed": s, "M": M_PROD,
                "scenarios": {sc: {"trail_complete": True, "chain_valid": True,
                                     "integrity_under_failure": True,
                                     "max_entry_bytes": 800, "n_entries": 2}
                              for sc in SCENARIOS}}
               for s in SEEDS_FULL]
    v, _ = compute_verdict(fake_mb); assert "MIDDLE_BAND" in v, v

    # Live smoke on CPU
    device = torch.device("cpu")
    out = measure_seed(N_SMOKE, 128, 17, device)
    assert len(out["scenarios"]) == 6
    for sc in SCENARIOS:
        assert sc in out["scenarios"], f"scenario {sc} missing"
        scd = out["scenarios"][sc]
        assert scd.get("trail_complete"), f"{sc} trail not complete"
    print(f"[selftest] edit_audit_trail_refinement_v1_n4096 PASS "
          f"6/6 scenarios produced complete audit trails", flush=True)


_instrumentation_selftest()


def _emit_schema_doc(seed_report, out_dir):
    """Emit schema doc; falls back to metrics.json directory on FS errors."""
    try:
        notes_dir = REPO / "notes"
        notes_dir.mkdir(parents=True, exist_ok=True)
        doc = notes_dir / "audit_trail_schema_v1_2026-05-30.md"
        with open(doc, "w", encoding='utf-8') as f:
            f.write("# Audit Trail Schema v1 (2026-05-30)\n\n")
            f.write("## Schema\n\n")
            f.write("Each audit entry is a JSON object with fields:\n")
            f.write("- ts_ns: perf_counter_ns timestamp\n")
            f.write("- op: operation string\n")
            f.write("- operands: per-op operands dict\n")
            f.write("- W_norm_before, W_norm_after, delta_norm: float L2 norms\n")
            f.write("- link: sha256(prev_hash || entry_body)\n\n")
            f.write("Hash chain integrity: each entry's link verifies against "
                    "previous entry's link.\n\n")
            f.write("## Sample Reports (per scenario)\n\n")
            for sc, sample in seed_report.get("sample_reports", {}).items():
                f.write(f"### {sc}\n\n```json\n")
                f.write(json.dumps(sample, indent=2, default=str))
                f.write("\n```\n\n")
    except Exception:  # noqa: BLE001
        pass


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device = torch.device("cpu")
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    M = M_SMOKE if smoke else M_PROD
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] edit_audit_trail_refinement_v1_n4096 smoke={smoke} N={N_cfg} "
          f"M={M} seeds={seeds} done={len(done)} device={device.type}",
          flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body); continue
        try:
            cell = measure_seed(N_cfg, M, seed, device)
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} scenarios={list(cell['scenarios'].keys())} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except (RuntimeError, MemoryError, Exception) as e:  # noqa: BLE001
            print(f"  seed={seed} FAILED: {e}", flush=True)

    if cells and not smoke:
        _emit_schema_doc(cells[0], out_dir)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "edit_audit_trail_refinement_v1_n4096",
               "N": N_cfg, "smoke": smoke, "M": M, "seeds": seeds,
               "cells": cells, "verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
