"""One-shot: move importance_ceiling_v7B from remote_cpu_queue to overnight_queue with --device cuda."""
import json
import os
import shutil
import time

CPU_Q = "C:/dev/hd-instrument/data/remote_cpu_queue/queue.json"
GPU_Q = "C:/dev/hd-instrument/data/overnight_queue/queue.json"
TARGET_NAME = "importance_ceiling_v7B_n_seeds_scale"


def backup(p):
    bak = p + f".bak.{int(time.time())}"
    shutil.copyfile(p, bak)
    return bak


def main():
    # Load
    with open(CPU_Q, "r", encoding="utf-8") as f:
        cpu = json.load(f)
    with open(GPU_Q, "r", encoding="utf-8") as f:
        gpu = json.load(f)

    # Find target in CPU pending
    target_idx = None
    for i, e in enumerate(cpu["experiments"]):
        if e.get("name") == TARGET_NAME and e.get("status") == "pending":
            target_idx = i
            break

    if target_idx is None:
        print(f"ERROR: {TARGET_NAME} not found as pending in CPU queue")
        return

    target = cpu["experiments"][target_idx]
    print(f"Found target at CPU index {target_idx}:")
    print(json.dumps(target, indent=2))

    # Build GPU entry with --device cuda
    gpu_entry = dict(target)
    existing_args = gpu_entry.get("args", [])
    if isinstance(existing_args, str):
        existing_args = existing_args.split()
    elif existing_args is None:
        existing_args = []
    # Append --device cuda if not already present
    if "--device" not in existing_args:
        existing_args = list(existing_args) + ["--device", "cuda"]
    gpu_entry["args"] = existing_args
    gpu_entry["timeout_s"] = 1800
    gpu_entry["routed_from"] = "remote_cpu_queue"
    gpu_entry["routed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    gpu_entry["routed_reason"] = "Fix #24 GPU dispatch must use GPU — v7B has torch.cuda paths confirmed by cell-author a7f42f93"

    # Backup both
    cpu_bak = backup(CPU_Q)
    gpu_bak = backup(GPU_Q)
    print(f"Backups: {cpu_bak} / {gpu_bak}")

    # Remove from CPU, append to GPU
    cpu["experiments"].pop(target_idx)
    gpu["experiments"].append(gpu_entry)

    # Write back
    with open(CPU_Q, "w", encoding="utf-8") as f:
        json.dump(cpu, f, indent=2)
    with open(GPU_Q, "w", encoding="utf-8") as f:
        json.dump(gpu, f, indent=2)

    # Verify
    with open(GPU_Q, "r", encoding="utf-8") as f:
        gpu2 = json.load(f)
    gpu_pending = [e for e in gpu2["experiments"] if e.get("status") == "pending"]
    with open(CPU_Q, "r", encoding="utf-8") as f:
        cpu2 = json.load(f)
    cpu_pending = [e for e in cpu2["experiments"] if e.get("status") == "pending"]
    print(f"\nAfter move:")
    print(f"  CPU pending: {len(cpu_pending)}")
    print(f"  GPU pending: {len(gpu_pending)}")
    gpu_target = [e for e in gpu_pending if e["name"] == TARGET_NAME]
    if gpu_target:
        print(f"  v7B in GPU at position {gpu_pending.index(gpu_target[0])} of {len(gpu_pending)} pending")
        print(f"  args: {gpu_target[0].get('args')}")
        print(f"  timeout_s: {gpu_target[0].get('timeout_s')}")
    cpu_target = [e for e in cpu_pending if e["name"] == TARGET_NAME]
    if cpu_target:
        print(f"  WARNING: v7B still in CPU pending!")
    else:
        print(f"  v7B removed from CPU pending: OK")


if __name__ == "__main__":
    main()
