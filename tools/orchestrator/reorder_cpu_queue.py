"""
Reorder remote_cpu_queue: move TARGET_NAME to TARGET_PENDING_POSITION (0-indexed among pending).
Uses local Python + SCP + remote atomic rename per feedback-powershell-queue-json-bom.

Usage: python reorder_cpu_queue.py
"""
import sys
import json
import subprocess
import tempfile
import os

REMOTE_HOST = "marsh@home"
REMOTE_QUEUE_PATH = "C:/dev/hd-instrument/data/remote_cpu_queue/queue.json"
REMOTE_TMP_PATH = "C:/dev/hd-instrument/data/remote_cpu_queue/queue.json.tmp"
TARGET_NAME = "pp58_bbp_discrete_fallback_v1_n16384"
# Position 2 = 0-indexed pending slot 2 = after pp49_discriminator(0) + pp33_mfpt(1)
TARGET_PENDING_POSITION = 2


def ssh_read_queue_raw():
    result = subprocess.run(
        ["ssh", REMOTE_HOST,
         f'powershell -Command "Get-Content {REMOTE_QUEUE_PATH} -Raw"'],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"[error] SSH read failed: {result.stderr}", flush=True)
        sys.exit(1)
    return result.stdout


def clean_ssh_output(raw):
    """Remove SSH warning lines and BOM."""
    lines = raw.split('\n')
    json_lines = [l for l in lines if not l.startswith('**') and not l.startswith('* ')]
    return '\n'.join(json_lines).lstrip('﻿')


def main():
    print("[reorder] Reading remote CPU queue...", flush=True)
    raw = ssh_read_queue_raw()
    clean = clean_ssh_output(raw)
    queue = json.loads(clean)
    experiments = queue["experiments"]
    print(f"[reorder] Total entries: {len(experiments)}", flush=True)

    # Identify pending/running entries in order
    pending = [(i, e) for i, e in enumerate(experiments)
               if e.get("status") in ("pending", "running")]
    print(f"[reorder] Pending/running entries ({len(pending)}):", flush=True)
    for pi, (gi, e) in enumerate(pending):
        marker = "  <-- TARGET" if e["name"] == TARGET_NAME else ""
        print(f"  pending[{pi}] global[{gi}] {e['name']} ({e['status']}){marker}", flush=True)

    # Find target
    target_pi = None
    target_gi = None
    for pi, (gi, e) in enumerate(pending):
        if e["name"] == TARGET_NAME:
            target_pi = pi
            target_gi = gi
            break

    if target_pi is None:
        print(f"[error] {TARGET_NAME} not found in pending entries", flush=True)
        sys.exit(1)

    if target_pi == TARGET_PENDING_POSITION:
        print(f"[reorder] {TARGET_NAME} already at pending position {TARGET_PENDING_POSITION}. No change.", flush=True)
        return

    # Remove target from experiments list
    target_entry = experiments.pop(target_gi)

    # Rebuild pending list after removal (global indices shifted)
    pending_after = [(i, e) for i, e in enumerate(experiments)
                     if e.get("status") in ("pending", "running")]

    if TARGET_PENDING_POSITION == 0:
        # Insert before first pending entry
        insert_before_gi = pending_after[0][0]
        experiments.insert(insert_before_gi, target_entry)
    else:
        # Insert after pending[TARGET_PENDING_POSITION - 1]
        after_pending_idx = TARGET_PENDING_POSITION - 1
        if after_pending_idx >= len(pending_after):
            print(f"[error] Not enough pending entries to insert at position {TARGET_PENDING_POSITION}", flush=True)
            sys.exit(1)
        after_gi = pending_after[after_pending_idx][0]
        experiments.insert(after_gi + 1, target_entry)

    queue["experiments"] = experiments

    # Verify result
    pending_final = [(i, e) for i, e in enumerate(experiments)
                     if e.get("status") in ("pending", "running")]
    print(f"[reorder] New pending order:", flush=True)
    found_at = None
    for pi, (gi, e) in enumerate(pending_final):
        marker = "  <-- MOVED" if e["name"] == TARGET_NAME else ""
        print(f"  pending[{pi}] global[{gi}] {e['name']}{marker}", flush=True)
        if e["name"] == TARGET_NAME:
            found_at = pi

    if found_at != TARGET_PENDING_POSITION:
        print(f"[error] Target ended at position {found_at}, expected {TARGET_PENDING_POSITION}", flush=True)
        sys.exit(1)

    # Write to local temp file (UTF-8, no BOM, LF line endings)
    new_json = json.dumps(queue, indent=2, ensure_ascii=False)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False,
                                     encoding='utf-8', newline='\n') as f:
        f.write(new_json)
        tmp_local = f.name
    print(f"[reorder] Local temp: {tmp_local} ({len(new_json)} chars)", flush=True)

    # SCP to remote .tmp path
    scp_result = subprocess.run(
        ["scp", tmp_local, f"{REMOTE_HOST}:{REMOTE_TMP_PATH}"],
        capture_output=True, text=True, timeout=30
    )
    os.unlink(tmp_local)
    if scp_result.returncode != 0:
        print(f"[error] SCP failed: {scp_result.stderr}", flush=True)
        sys.exit(1)
    print(f"[reorder] SCP OK: .tmp written to remote", flush=True)

    # Atomic rename on remote (Move-Item -Force)
    rename_result = subprocess.run(
        ["ssh", REMOTE_HOST,
         'powershell -Command "Move-Item -Force '
         '\'C:/dev/hd-instrument/data/remote_cpu_queue/queue.json.tmp\' '
         '\'C:/dev/hd-instrument/data/remote_cpu_queue/queue.json\'; Write-Output OK"'],
        capture_output=True, text=True, timeout=30
    )
    out = rename_result.stdout.strip()
    err = rename_result.stderr.strip()
    if rename_result.returncode != 0 or 'OK' not in out:
        print(f"[error] Remote rename failed rc={rename_result.returncode}: {err}", flush=True)
        sys.exit(1)
    print(f"[reorder] Remote atomic rename OK", flush=True)

    # Verify final remote state
    verify_raw = ssh_read_queue_raw()
    verify_clean = clean_ssh_output(verify_raw)
    verify_q = json.loads(verify_clean)
    verify_pending = [e for e in verify_q["experiments"]
                      if e.get("status") in ("pending", "running")]
    for pi, e in enumerate(verify_pending):
        if e["name"] == TARGET_NAME:
            print(f"[reorder] REMOTE VERIFY: {TARGET_NAME} at pending position {pi}", flush=True)
            if pi == TARGET_PENDING_POSITION:
                print(f"[reorder] DONE: queue reorder confirmed on remote.", flush=True)
            else:
                print(f"[error] Remote verify: position {pi} != expected {TARGET_PENDING_POSITION}", flush=True)
                sys.exit(1)
            return

    print(f"[error] Remote verify: {TARGET_NAME} not found in pending after write!", flush=True)
    sys.exit(1)


if __name__ == "__main__":
    main()
