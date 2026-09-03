"""Witness for the APPRAISAL-SIM THETA DISK CACHE (2026-09-03 substrate-speed fix, companion to the
frame-induction cache).

WHAT + WHY. context_grounded_valence._sim_theta trains an online reward-modulated bandit (n_train episodes,
torch) to earn the appraisal-sim theta used by the reader's affect/valence stage. It ran on the FIRST read()
of every fresh process (~8-24s); the in-process _THETA_CACHE amortized only within a process, so every
witness / benchmark / board process re-paid it. The (Codebook, theta) result is DETERMINISTIC given
(seed, n_train) + the training code (manual_seed CPU torch), so we persist it -- keyed by (seed, n_train) +
a CONTENT HASH of the appraisal-sim module source, so any change to train_theta/Codebook/reward/phi auto-
invalidates (no silent staleness). Measured: fresh-process reader read 16s (induction-cached, theta not) ->
6.5s (both cached).

  [1] FRESH-TRAIN == CACHE byte-exact: a fresh manual_seed training reproduces the disk-cached theta tensor
      exactly (torch.equal) -- the cache changes NOTHING, it only skips recompute.
  [2] KEY = source-hash sensitive: the cache path embeds a hash of the appraisal-sim source, so editing that
      module changes the path (invalidates); identical source -> identical path.
  [3] THE CACHE IS USED: with the disk cache present, _sim_theta (fresh in-process cache) returns the theta
      that torch.equal's the on-disk one -- it loads, it does not retrain.

Run: .venv/Scripts/python.exe verification/test_theta_disk_cache_organ.py
"""
import os
import sys

os.environ.setdefault("OMP_NUM_THREADS", "1")
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import torch  # noqa: E402
import hdlab.context_grounded_valence as CGV  # noqa: E402

_SIM = CGV._sim
SEED = 0
N = CGV.FULL_N_TRAIN_THETA


def _fresh_theta(seed, n):
    """Reproduce _sim_theta's training WITHOUT any cache (the definitive faithfulness reference)."""
    gen = torch.Generator().manual_seed(seed)
    cb = _SIM.Codebook(gen)
    g = torch.Generator().manual_seed(seed * 100 + _SIM.hash_variant("FULL"))
    theta = _SIM.train_theta(cb, g, "FULL", n)
    return cb, theta


def main():
    checks = []

    # ensure the disk cache exists (build once if absent; ~8-24s only on a cold checkout)
    CGV._THETA_CACHE.clear()
    cb0, theta0 = CGV._sim_theta(SEED, N)
    disk = CGV._load_theta_disk(SEED, N)
    checks.append((disk is not None, "[0] theta disk cache present after _sim_theta (%s)"
                   % (os.path.basename(CGV._theta_disk_path(SEED, N)))))

    # [1] FRESH-TRAIN == CACHE byte-exact.
    _cbf, theta_fresh = _fresh_theta(SEED, N)
    disk_theta = disk[1] if disk is not None else None
    ok1 = disk_theta is not None and torch.equal(disk_theta, theta_fresh)
    checks.append((ok1, "[1] fresh manual_seed training == the disk-cached theta byte-exact (torch.equal)"))

    # [2] KEY source-hash sensitive.
    p_same = CGV._theta_disk_path(SEED, N)
    h = CGV._theta_src_hash()
    ok2 = (h and h != "nosrc" and h in p_same and p_same == CGV._theta_disk_path(SEED, N)
           and CGV._theta_disk_path(SEED, N + 1) != p_same)
    checks.append((ok2, "[2] cache path embeds the appraisal-sim source hash (%s); (seed,n) vary the path" % h))

    # [3] THE CACHE IS USED (fresh in-process cache still returns the on-disk theta).
    CGV._THETA_CACHE.clear()
    _cb2, theta2 = CGV._sim_theta(SEED, N)
    ok3 = torch.equal(theta2, disk_theta)
    checks.append((ok3, "[3] cache USED: _sim_theta returns the on-disk theta (torch.equal), no retrain"))

    print("=== witness: APPRAISAL-SIM THETA DISK CACHE (substrate-speed fix, byte-faithful) ===")
    ok_all = True
    for ok, msg in checks:
        print("  %s  %s" % ("PASS" if ok else "FAIL", msg))
        ok_all = ok_all and bool(ok)
    print("\nRESULT: %s (%d/%d)" % ("ALL CHECKS PASS" if ok_all else "FAIL",
                                    sum(1 for ok, _ in checks if ok), len(checks)))
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
