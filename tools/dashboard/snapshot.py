"""Phase 1 smoke test: pull one full dashboard snapshot from marsh@home.

Runs the four read families the dashboard needs (nvidia-smi, python procs,
per-queue heartbeat + queue.json + queue.log tail), prints each result
truncated, and reports total elapsed wall time. No UI, no server, no writes.
"""

from __future__ import annotations

import time

from ssh_client import ReadOnlySSH


QUEUE_DIRS: dict[str, str] = {
    "gpu": r"C:\dev\hd-instrument\data\overnight_queue",
    "cpu": r"C:\dev\hd-instrument\data\remote_cpu_queue",
}


def pull_snapshot(ssh: ReadOnlySSH) -> dict[str, str]:
    out: dict[str, str] = {}

    out["nvidia_smi"] = ssh.run(
        "nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total,"
        "temperature.gpu --format=csv,noheader,nounits"
    )
    out["python_procs"] = ssh.run('tasklist /FI "IMAGENAME eq python.exe"')

    for label, qdir in QUEUE_DIRS.items():
        out[f"{label}_heartbeat"] = ssh.run(f"type {qdir}\\heartbeat.json")
        out[f"{label}_queue"] = ssh.run(f"type {qdir}\\queue.json")
        out[f"{label}_log_tail"] = ssh.run(
            f'powershell -Command "Get-Content {qdir}\\queue.log -Tail 50"'
        )

    return out


def main() -> None:
    t_total = time.perf_counter()
    with ReadOnlySSH() as ssh:
        t_connect = time.perf_counter() - t_total
        t0 = time.perf_counter()
        snap = pull_snapshot(ssh)
        t_pull = time.perf_counter() - t0

    print(f"--- timings ---")
    print(f"connect:   {t_connect*1000:7.1f} ms")
    print(f"pull all:  {t_pull*1000:7.1f} ms")
    print(f"total:     {(time.perf_counter()-t_total)*1000:7.1f} ms")
    print()

    for k, v in snap.items():
        body = v if len(v) <= 600 else v[:600] + f"\n... [{len(v)-600} more chars]"
        print(f"=== {k} ({len(v)} chars) ===")
        print(body)
        print()


if __name__ == "__main__":
    main()
