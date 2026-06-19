"""SubstrateMemory smoke test.

Gate definition (Workstream D):
  N=512, C=512, M=64, BSC codebook. Tests:
    1. store M items, retrieve each, recall_at_1 >= 0.9
    2. edit 1 item, max_isolation < 0.10
    3. delete 1 item, var_ratio < 0.20, post-retrieve returns different key
    4. audit() populates all 3 KF metrics (non-None)
    5. save + load round-trip preserves retrieval results

Must complete in <30s on CPU. Exits 0 on pass, nonzero on fail.
"""

from __future__ import annotations

import sys
import tempfile
import time
from pathlib import Path

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from testbed.substrate_memory import SubstrateMemory  # noqa: E402


def _query_for(mem: SubstrateMemory, key_id: str) -> np.ndarray:
    row = mem._atom_for_key_id(key_id)
    return mem.codebook[row].detach().cpu().numpy()


def main() -> int:
    t0 = time.time()
    print("[smoke] starting SubstrateMemory smoke test N=512 C=512 M=64 bsc")

    N = 512
    M = 64
    mem = SubstrateMemory(
        N=N,
        codebook_kind="bsc",
        codebook_scale=1,  # C = 1 * N = 512
        beta=32.0,
        seed=17,
    )

    # 1) Store M items, retrieve, assert recall_at_1 >= 0.9
    ids = [f"k_{i:03d}" for i in range(M)]
    values = [f"v_{i:03d}" for i in range(M)]
    for kid, val in zip(ids, values):
        kvec = _query_for(mem, kid)
        mem.store(kid, kvec, val)

    hits = 0
    confs: list[float] = []
    for kid, val in zip(ids, values):
        r = mem.retrieve(_query_for(mem, kid))
        confs.append(r.confidence)
        if r.key_id == kid and r.value == val:
            hits += 1
    recall = hits / M
    print(f"[smoke] recall_at_1 = {recall:.3f} (hits {hits}/{M}, "
          f"mean_conf {sum(confs)/len(confs):.4f})")
    assert recall >= 0.9, f"recall_at_1 {recall:.3f} < 0.9"

    # 2) Edit 1 item, max_isolation < 0.10
    # Snapshot non-edited acc, edit, recompute non-edited acc, compute delta.
    target = ids[0]
    non_edit = ids[1:]
    base_hits = [
        mem.retrieve(_query_for(mem, k)).key_id == k for k in non_edit
    ]
    mem.edit(target, "v_000_EDITED")
    edited_r = mem.retrieve(_query_for(mem, target))
    assert edited_r.value == "v_000_EDITED", (
        f"edit did not stick: got {edited_r.value!r}"
    )
    post_hits = [
        mem.retrieve(_query_for(mem, k)).key_id == k for k in non_edit
    ]
    delta = sum(abs(int(a) - int(b)) for a, b in zip(base_hits, post_hits)) / len(non_edit)
    print(f"[smoke] edit max_isolation (acc-delta on non-edited) = {delta:.4f}")
    assert delta < 0.10, f"edit isolation {delta:.4f} >= 0.10"

    # 3) Delete 1 item, var_ratio < 0.20, post-retrieve returns different key
    victim = ids[1]
    cert = mem.delete(victim)
    print(
        f"[smoke] delete var_ratio = {cert.var_ratio:.4f}  "
        f"erased = {cert.erased}"
    )
    assert cert.var_ratio is not None and cert.var_ratio < 0.20, (
        f"var_ratio {cert.var_ratio} not < 0.20"
    )
    assert cert.erased, "post-delete retrieve still returns the deleted key"

    # 4) audit() populates all 3 KF metrics
    report = mem.audit()
    print(
        f"[smoke] audit kf1_above={report.kf1_above_thresh_frac}  "
        f"kf2_max_iso={report.kf2_max_isolation}  "
        f"tcft_mean_vr={report.tcft_mean_var_ratio}  "
        f"n_items={report.n_items}"
    )
    assert report.kf1_above_thresh_frac is not None, "kf1 not populated"
    assert report.kf2_max_isolation is not None, "kf2 not populated"
    assert report.tcft_mean_var_ratio is not None, "tcft not populated"
    assert report.n_items == M - 1, f"n_items {report.n_items} != {M-1}"

    # 5) save + load round-trip
    import gc
    import shutil
    state_dir = Path(tempfile.mkdtemp()) / "substrate_state_smoke"
    try:
        mem.save(state_dir)
        # Sample expected retrievals from the live store.
        sample_ids = [ids[2], ids[5], ids[10]]
        live_results = []
        for k in sample_ids:
            r = mem.retrieve(_query_for(mem, k))
            live_results.append((r.key_id, r.value, r.confidence))

        # Fresh instance, load state.
        mem2 = SubstrateMemory(
            N=N, codebook_kind="bsc", codebook_scale=1, beta=32.0, seed=17
        )
        mem2.load(state_dir)
        for (exp_kid, exp_val, exp_conf), kid in zip(live_results, sample_ids):
            r2 = mem2.retrieve(_query_for(mem2, kid))
            assert r2.key_id == exp_kid, (
                f"load drift key_id: {r2.key_id!r} vs {exp_kid!r}"
            )
            assert r2.value == exp_val, (
                f"load drift value: {r2.value!r} vs {exp_val!r}"
            )
            assert abs(r2.confidence - exp_conf) < 1e-4, (
                f"load drift confidence: {r2.confidence} vs {exp_conf}"
            )
        print(
            f"[smoke] save+load round-trip OK ({len(sample_ids)} samples identical)"
        )
        # Release any memmap references before Windows cleanup.
        del mem2
        gc.collect()
    finally:
        shutil.rmtree(state_dir.parent, ignore_errors=True)

    elapsed = time.time() - t0
    print(f"[smoke] PASS elapsed={elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except AssertionError as e:
        print(f"[smoke] FAIL assertion: {e}", file=sys.stderr)
        rc = 2
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[smoke] FAIL exception: {e}", file=sys.stderr)
        rc = 3
    sys.exit(rc)
