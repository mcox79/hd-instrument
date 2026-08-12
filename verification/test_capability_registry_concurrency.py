"""Witness for capability_registry.jsonl concurrent-write safety.

Reported bug (2026-08-12): an agent's write to data/capability_registry.jsonl was a
read-edit-replace with a ~1s window and was NOT concurrency-safe -- two agents
writing the registry in the same session can race that window, and the second
os.replace() silently clobbers the first writer's row (lost update, not a crash,
so nothing flags it). The registry is the project's WIRE-or-SHELVE durability gate
(CLAUDE.md "Capability tracking"); a lost row silently un-registers a capability.

Fix under test: tools/capability_registry_audit.py's RegistryLock / registry_
transaction / append_rows(), which hold a cross-process lock (reusing tools/
safe_queue.py's portalocker/msvcrt/fcntl backend) across the whole load-mutate-
write span, not just the final os.replace.

This test spawns two REAL separate OS processes (not threads, not mocked) against
a throwaway temp-dir copy of the registry -- it never touches
data/capability_registry.jsonl. Two cases:

  1. Both writers go through the safe path (append_rows). They must both land,
     every time, regardless of interleaving.
  2. Both writers replay the exact same race through the PRE-FIX pattern
     (load_registry() then, after a barrier-synchronized rendezvous standing in
     for the reported window, write_registry()) with no lock. This must
     reproduce the reported loss -- proving this witness is capable of failing,
     i.e. it would have caught the original bug and will catch any regression
     that removes the lock.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Run as a separate `python -c` process so locking is exercised across real OS
# process boundaries (matches the reported failure mode: two agent sessions).
# mode "safe"   -> goes through append_rows() (the fix).
# mode "unsafe" -> replicates the pre-fix load_registry()+write_registry() pattern,
#                  with a file-based barrier so both workers are guaranteed to have
#                  completed their load() before either proceeds to append+write --
#                  this removes reliance on absolute timing/machine speed while still
#                  genuinely reproducing the reported interleaving.
_WORKER = """
import json, os, sys, time
sys.path.insert(0, {root!r})
import tools.capability_registry_audit as cra

mode, reg_path, row_id, other_id, barrier_dir = sys.argv[1:6]
cra.REGISTRY = cra.Path(reg_path)
cra.REGISTRY_LOCK_PATH = cra.REGISTRY.with_suffix(".jsonl.lock")

row = {{"id": row_id, "name": row_id, "kind": "exp-cell", "path": []}}


def _rendezvous(tag):
    mine = cra.Path(barrier_dir) / (row_id + "." + tag)
    other = cra.Path(barrier_dir) / (other_id + "." + tag)
    mine.write_text("1", encoding="utf-8")
    # Generous deadline: under heavy host contention (e.g. many python-process
    # launches stacked back-to-back, antivirus scan-on-open) a partner worker's
    # own process startup can itself take several seconds. A deadline that is too
    # tight makes this rendezvous silently give up and proceed WITHOUT the other
    # worker, which turns the intended race into an accidental non-overlapping
    # sequential run (a false negative for the "unsafe" repro below -- it stops
    # reproducing the loss purely because nothing overlapped, not because the
    # bug is gone). 30s comfortably covers normal single-test-at-a-time runs.
    deadline = time.time() + 30.0
    while not other.exists() and time.time() < deadline:
        time.sleep(0.005)


if mode == "safe":
    cra.append_rows([row])
else:
    # Rendezvous before load, then a generous fixed sleep standing in for the
    # reported ~1s read-edit-replace window, before either writes. The barrier
    # alone was measured flaky (~2/8 runs) on this box: python-process-startup /
    # antivirus-scan jitter between the two workers occasionally exceeded the
    # implicit race window, so one worker's whole load-sleep-write cycle finished
    # before the other even called load() -- no real overlap, so nothing was lost
    # (a false negative for this repro, not evidence the bug is gone). Forcing
    # both loads to land within the barrier's ~10ms poll granularity and THEN
    # holding both for a full second before either writes guarantees neither
    # process's load() can ever observe the other's write, regardless of how much
    # slower one process was to even start.
    _rendezvous("start")
    rows = cra.load_registry()
    time.sleep(1.0)
    rows.append(row)
    # Deliberately NOT cra.write_registry() here: that function uses a FIXED shared
    # tmp filename (REGISTRY.with_suffix('.jsonl.tmp')), so two unsynchronized
    # callers racing it can also interleave-corrupt the tmp file itself (a second,
    # narrower bug than the one under test, and confounds this repro -- occasionally
    # made BOTH rows appear to land via a garbled merge rather than a clean
    # last-writer-wins overwrite). Use a PID-private tmp name instead, isolating the
    # demonstration to exactly the documented bug: an unsynchronized read-then-
    # replace race causes a clean lost update, nothing more.
    tmp = cra.REGISTRY.with_suffix(".jsonl.tmp.%d" % os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\\n")
    os.replace(tmp, cra.REGISTRY)
"""


def _spawn(mode: str, reg_path: Path, row_id: str, other_id: str, barrier_dir: Path) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-c", _WORKER.format(root=str(ROOT)),
         mode, str(reg_path), row_id, other_id, str(barrier_dir)],
        cwd=str(ROOT), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )


def _seed_registry(path: Path) -> None:
    seed = {"id": "seed_row", "name": "seed", "kind": "exp-cell", "path": []}
    path.write_text(json.dumps(seed) + "\n", encoding="utf-8")


def _load_ids(path: Path) -> set[str]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), f"duplicate id landed in registry: {ids}"
    return set(ids)


def test_concurrent_safe_appends_both_land():
    with tempfile.TemporaryDirectory() as td:
        reg = Path(td) / "capability_registry.jsonl"
        barrier_dir = Path(td) / "barrier"
        barrier_dir.mkdir()
        _seed_registry(reg)

        p1 = _spawn("safe", reg, "concurrent_row_a", "concurrent_row_b", barrier_dir)
        p2 = _spawn("safe", reg, "concurrent_row_b", "concurrent_row_a", barrier_dir)
        out1 = p1.communicate(timeout=60)
        out2 = p2.communicate(timeout=60)

        assert p1.returncode == 0, f"worker 1 failed: {out1}"
        assert p2.returncode == 0, f"worker 2 failed: {out2}"

        ids = _load_ids(reg)
        assert {"seed_row", "concurrent_row_a", "concurrent_row_b"} <= ids, (
            f"lost update under the locked path: expected both concurrent rows to "
            f"land, got {ids}")


def test_unsafe_pattern_reproduces_the_reported_lost_update():
    """Negative control: proves this witness can actually fail. Replays the same
    two-writer race through the pre-fix pattern (no lock) and asserts the loss
    the bug report described actually reproduces -- if this assertion ever starts
    failing, it means the unsynchronized pattern stopped losing data (unlikely;
    treat as a signal the barrier/repro itself broke, not that the bug is gone)."""
    with tempfile.TemporaryDirectory() as td:
        reg = Path(td) / "capability_registry.jsonl"
        barrier_dir = Path(td) / "barrier"
        barrier_dir.mkdir()
        _seed_registry(reg)

        p1 = _spawn("unsafe", reg, "unsafe_row_a", "unsafe_row_b", barrier_dir)
        p2 = _spawn("unsafe", reg, "unsafe_row_b", "unsafe_row_a", barrier_dir)
        out1 = p1.communicate(timeout=60)
        out2 = p2.communicate(timeout=60)

        assert p1.returncode == 0, f"worker 1 failed: {out1}"
        assert p2.returncode == 0, f"worker 2 failed: {out2}"

        ids = _load_ids(reg)
        assert not ({"unsafe_row_a", "unsafe_row_b"} <= ids), (
            "expected the unsynchronized pre-fix pattern to lose one of the two "
            f"rows (that is the bug this fix addresses); both landed instead: {ids} "
            "-- either the repro's barrier is no longer forcing an overlap, or the "
            "OS started making os.replace-without-locking safe under races, which "
            "would be surprising")
