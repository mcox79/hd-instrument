"""Lock-safe queue operations for multi-runner setups.

Provides atomic claim-and-mark-running and outcome-update operations on a
shared queue.json, using cross-process file locking.

Lock backend selection (auto):
  1. portalocker (if installed)  — uses LockFileEx on Windows; FIFO-fair
  2. msvcrt.locking (Windows fallback)  — not fair; OK for <=3 concurrent runners
  3. fcntl.flock (POSIX)  — fair on Linux/macOS

The lock file is queue.json.lock — a sentinel file we open and lock. The
actual queue.json is read and written while holding the lock.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# ---------- Lock backend selection ----------

_LOCK_BACKEND = "unknown"
try:
    import portalocker  # type: ignore
    _LOCK_BACKEND = "portalocker"
except ImportError:
    portalocker = None
    if sys.platform == "win32":
        import msvcrt
        _LOCK_BACKEND = "msvcrt"
    else:
        import fcntl
        _LOCK_BACKEND = "fcntl"


def _acquire(fd: int, blocking: bool = True, max_wait_s: float = 30.0) -> bool:
    """Acquire exclusive lock on fd. Returns True on success, False on timeout."""
    if _LOCK_BACKEND == "portalocker":
        flags = portalocker.LOCK_EX
        if not blocking:
            flags |= portalocker.LOCK_NB
        deadline = time.monotonic() + max_wait_s
        while True:
            try:
                portalocker.lock(fd, flags)
                return True
            except portalocker.exceptions.LockException:
                if not blocking or time.monotonic() > deadline:
                    return False
                time.sleep(0.05)
    elif _LOCK_BACKEND == "msvcrt":
        mode = msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK
        deadline = time.monotonic() + max_wait_s
        while True:
            try:
                msvcrt.locking(fd, mode, 1)
                return True
            except OSError:
                if not blocking or time.monotonic() > deadline:
                    return False
                time.sleep(0.05)
    else:  # fcntl
        flags = fcntl.LOCK_EX | (fcntl.LOCK_NB if not blocking else 0)
        deadline = time.monotonic() + max_wait_s
        while True:
            try:
                fcntl.flock(fd, flags)
                return True
            except OSError:
                if not blocking or time.monotonic() > deadline:
                    return False
                time.sleep(0.05)


def _release(fd: int) -> None:
    try:
        if _LOCK_BACKEND == "portalocker":
            portalocker.unlock(fd)
        elif _LOCK_BACKEND == "msvcrt":
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        else:
            fcntl.flock(fd, fcntl.LOCK_UN)
    except OSError:
        pass


def lock_backend_name() -> str:
    """Return name of the active lock backend (for diagnostics)."""
    return _LOCK_BACKEND


# ---------- QueueLock context manager ----------

class QueueLock:
    """Context manager: hold the queue lock for read+write."""

    def __init__(self, queue_path: Path, max_wait_s: float = 30.0):
        self.queue_path = Path(queue_path)
        self.lock_path = Path(str(queue_path) + ".lock")
        self.max_wait_s = max_wait_s
        self._fd: int | None = None

    def __enter__(self):
        # O_CREAT lets multiple processes share the same sentinel file.
        # portalocker on Windows requires binary-mode FD via os.open.
        self._fd = os.open(str(self.lock_path), os.O_RDWR | os.O_CREAT, 0o644)
        ok = _acquire(self._fd, blocking=True, max_wait_s=self.max_wait_s)
        if not ok:
            os.close(self._fd)
            self._fd = None
            raise TimeoutError(
                f"Could not acquire queue lock within {self.max_wait_s}s "
                f"(backend={_LOCK_BACKEND})"
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._fd is not None:
            _release(self._fd)
            os.close(self._fd)
            self._fd = None

    def read(self) -> dict:
        # Retry on PermissionError: a concurrent reader (e.g. dashboard state-emitter)
        # can briefly hold queue.json with an exclusive open on Windows, raising
        # PermissionError. The lock is transient, so retry-with-backoff (mirrors write()'s
        # os.replace retry). Without this, a single collision crashed the runner (2026-06-11).
        last_err: Exception | None = None
        for _ in range(60):
            try:
                with open(self.queue_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except PermissionError as e:
                last_err = e
                time.sleep(0.05)
        raise last_err if last_err is not None else RuntimeError("queue read failed")

    def write(self, queue: dict) -> None:
        # Per-PID tmp file + os.replace (retried on Windows handle delay).
        tmp_path = Path(f"{self.queue_path}.tmp.{os.getpid()}")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(queue, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        last_err: Exception | None = None
        for _ in range(20):
            try:
                os.replace(tmp_path, self.queue_path)
                return
            except PermissionError as e:
                last_err = e
                time.sleep(0.02)
        # Final fallback: direct truncate-write (we hold the lock, so safe).
        try:
            with open(self.queue_path, "w", encoding="utf-8") as f:
                json.dump(queue, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
        except Exception:
            if last_err is not None:
                raise last_err
            raise


# ---------- Public claim/outcome ops ----------

def claim_next_pending(queue_path: Path, runner_id: str, now_iso: str) -> dict | None:
    """Atomically find the first pending entry, mark it running, return it.
    Returns None if queue has no pending work.
    """
    with QueueLock(queue_path) as lock:
        queue = lock.read()
        for entry in queue["experiments"]:
            if entry.get("status") == "pending":
                entry["status"] = "running"
                entry["claimed_by"] = runner_id
                entry["started_at"] = now_iso
                lock.write(queue)
                return entry
        return None


def mark_outcome(queue_path: Path, name: str, status: str, **extra) -> bool:
    """Atomically update a running entry to a terminal status.
    Only updates entries currently in 'running'. Returns True if updated.
    """
    with QueueLock(queue_path) as lock:
        queue = lock.read()
        for entry in queue["experiments"]:
            if entry.get("name") == name and entry.get("status") == "running":
                entry["status"] = status
                entry.update(extra)
                lock.write(queue)
                return True
        return False


def force_status(queue_path: Path, name: str, status: str, **extra) -> bool:
    """Atomically update an entry regardless of current status. For healer use."""
    with QueueLock(queue_path) as lock:
        queue = lock.read()
        for entry in queue["experiments"]:
            if entry.get("name") == name:
                entry["status"] = status
                entry.update(extra)
                lock.write(queue)
                return True
        return False
