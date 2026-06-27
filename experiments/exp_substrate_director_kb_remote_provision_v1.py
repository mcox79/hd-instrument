"""SUBSTRATE DIRECTOR KB REMOTE PROVISION v1 (Tier-1 from drill 2026-06-27).

Pre-reg: preregs/2026-06-27_substrate_director_kb_remote_provision_v1.md

Tier-1 deliverable from `notes/research_drill_kb_referent_missing_systemic_3x_2026-06-27.md`.

Provisions the canonical substrate-Director-KB onto the remote_cpu_queue
runner so cells that legitimately need 577k-entity canonical scale (e.g.
ANCHOR 5 dual-store audit) can load_default_kb() without HARD_FAILing on
KB_REFERENT_MISSING.

ARMS (3 mandatory):
  ARM_LOCAL_INGEST_FRESHNESS_CHECK  - verify local canonical fresh + populated
  ARM_REMOTE_SYNC                   - invoke tools/sync_canonical_kb_to_remote.sh
  ARM_REMOTE_VERIFY                 - SSH-load remote KB; compare n_entities
                                       + canary-query top-1 atom string

HARD_PASS BANDS:
  - local n_entities >= 500_000 AND coverage_ratio >= 0.99
  - remote_post_sync n_entities EXACTLY equals local
  - remote_post_sync load_default_kb() opens without exception
  - canary-query top-1 atom matches exactly between local and remote

ASCII-only. No emojis. No em-dashes.

KB_REFERENT note: this cell's ARM_LOCAL_FRESHNESS reads the local canonical,
and ARM_REMOTE_SYNC BUILDS the remote canonical. Declared referent is the
local canonical (cell crashes early if local KB itself is absent). The
PROT-022 gate uses --allow-missing-referent if remote check is requested.

# KB_REFERENT: data/substrate_director_kb_v1/manifest.json
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

LOCAL_KB_PATH = REPO / "data" / "substrate_director_kb_v1"
LOCAL_MANIFEST = LOCAL_KB_PATH / "manifest.json"

REMOTE_HOST = "marsh@home"
REMOTE_REPO = "C:/dev/hd-instrument"
REMOTE_KB_PATH = f"{REMOTE_REPO}/data/substrate_director_kb_v1"

SYNC_SCRIPT = REPO / "tools" / "sync_canonical_kb_to_remote.sh"
AUDIT_LOG = REPO / "data" / "kb_remote_provision_audit_log.jsonl"

# Pre-reg bands
HP_MIN_LOCAL_N_ENTITIES = 500_000
HP_MIN_LOCAL_COVERAGE = 0.99
HP_MAX_LOCAL_MANIFEST_AGE_S = 86_400  # 24h
MB_REMOTE_RATIO_FLOOR = 0.95

EXPECTED_N_ARMS = 3

# Canary query (stable; testable across canonical-KB rotations because it
# always resolves to the kb_ingest cell prereg which is committed git history)
CANARY_QUERY = "substrate director kb ingest"
CANARY_K = 3


def _ssh(remote_cmd: str, timeout: int = 30) -> tuple[int, str, str]:
    """Run a command on REMOTE_HOST via ssh; return (rc, stdout, stderr).
    Filters out OpenSSH PQ warning lines from stderr."""
    cmd = ["ssh", "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
           REMOTE_HOST, remote_cmd]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, "", f"TIMEOUT after {timeout}s"
    stderr_clean = "\n".join(
        ln for ln in r.stderr.splitlines()
        if not any(s in ln for s in ("WARNING:", "store now", "server may", "This session"))
    )
    return r.returncode, r.stdout, stderr_clean


def _arm_local_freshness() -> dict:
    """ARM 1: verify local canonical KB exists, populated, recently rotated."""
    t0 = time.perf_counter()
    arm = {"arm": "ARM_LOCAL_INGEST_FRESHNESS_CHECK"}
    try:
        if not LOCAL_MANIFEST.exists():
            arm.update({"ok": False, "error": f"local manifest missing at {LOCAL_MANIFEST}"})
            arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
            return arm
        manifest = json.loads(LOCAL_MANIFEST.read_text(encoding="utf-8"))
        n_ent = manifest.get("n_entities", 0)
        coverage = manifest.get("coverage_ratio", 0.0)
        kb_ver = manifest.get("kb_version", "unknown")
        n_dim = manifest.get("n_dim", 0)
        encoder = manifest.get("encoder", "unknown")
        n_triples = manifest.get("n_triples", 0)
        mtime = LOCAL_MANIFEST.stat().st_mtime
        age_s = time.time() - mtime
        ok = (
            n_ent >= HP_MIN_LOCAL_N_ENTITIES
            and coverage >= HP_MIN_LOCAL_COVERAGE
            and age_s <= HP_MAX_LOCAL_MANIFEST_AGE_S
        )
        arm.update({
            "ok": bool(ok),
            "n_entities": n_ent,
            "coverage_ratio": coverage,
            "kb_version": kb_ver,
            "encoder": encoder,
            "n_dim": n_dim,
            "n_triples": n_triples,
            "manifest_age_s": round(age_s, 1),
            "manifest_path": str(LOCAL_MANIFEST),
        })
    except Exception as e:  # noqa: BLE001
        arm.update({"ok": False, "error": f"{type(e).__name__}: {e}"})
    arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
    return arm


def _arm_remote_sync() -> dict:
    """ARM 2: invoke the sync script; capture wall + audit-log final line."""
    t0 = time.perf_counter()
    arm: dict[str, Any] = {"arm": "ARM_REMOTE_SYNC"}
    if not SYNC_SCRIPT.exists():
        arm.update({"ok": False, "error": f"sync script not found at {SYNC_SCRIPT}"})
        arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
        return arm
    try:
        r = subprocess.run(
            ["bash", str(SYNC_SCRIPT)],
            capture_output=True, text=True, timeout=3600,
        )
        arm["sync_exit_code"] = r.returncode
        # Tail of stderr (log lines from sync script)
        stderr_tail = "\n".join(r.stderr.splitlines()[-20:])
        arm["sync_stderr_tail"] = stderr_tail
        # Audit log: read the last 'complete' line
        if AUDIT_LOG.exists():
            audit_lines = AUDIT_LOG.read_text(encoding="utf-8").splitlines()
            for ln in reversed(audit_lines):
                try:
                    rec = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                if rec.get("phase") == "complete":
                    arm["audit_complete_record"] = rec
                    arm["sync_wall_s"] = rec.get("wall_s")
                    arm["scp_s"] = rec.get("scp_s")
                    arm["bytes_transferred"] = rec.get("bytes")
                    arm["remote_n_entities_per_audit"] = rec.get("n_entities")
                    break
            else:
                arm["audit_complete_record"] = None
        arm["ok"] = bool(r.returncode == 0 and arm.get("audit_complete_record"))
    except subprocess.TimeoutExpired:
        arm.update({"ok": False, "error": "sync script TIMEOUT after 3600s"})
    except Exception as e:  # noqa: BLE001
        arm.update({"ok": False, "error": f"{type(e).__name__}: {e}"})
    arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
    return arm


def _arm_remote_verify(local_arm: dict) -> dict:
    """ARM 3: SSH-load remote KB; compare against local."""
    t0 = time.perf_counter()
    arm: dict[str, Any] = {"arm": "ARM_REMOTE_VERIFY"}

    # Remote manifest read
    rc, out, err = _ssh(
        f"python -c \"import json;m=json.load(open(r'{REMOTE_KB_PATH}/manifest.json'));"
        f"import sys;sys.stdout.write(json.dumps(m))\"",
        timeout=30,
    )
    if rc != 0:
        arm.update({"ok": False, "error": f"remote manifest read failed rc={rc} err={err}"})
        arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
        return arm
    try:
        remote_manifest = json.loads(out.strip())
    except json.JSONDecodeError as e:
        arm.update({"ok": False, "error": f"remote manifest unparseable: {e}; raw={out[:200]}"})
        arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
        return arm

    remote_n_ent = remote_manifest.get("n_entities", 0)
    remote_kb_ver = remote_manifest.get("kb_version", "unknown")
    remote_encoder = remote_manifest.get("encoder", "unknown")
    local_n_ent = local_arm.get("n_entities", -1)
    local_kb_ver = local_arm.get("kb_version", "unknown_local")
    local_encoder = local_arm.get("encoder", "unknown_local")
    arm["remote_n_entities"] = remote_n_ent
    arm["remote_kb_version"] = remote_kb_ver
    arm["remote_encoder"] = remote_encoder
    arm["local_n_entities"] = local_n_ent
    arm["local_kb_version"] = local_kb_ver
    arm["local_encoder"] = local_encoder
    arm["n_entities_match"] = bool(remote_n_ent == local_n_ent)
    arm["kb_version_match"] = bool(remote_kb_ver == local_kb_ver)
    arm["encoder_match"] = bool(remote_encoder == local_encoder)

    # Remote load_default_kb sanity (does it actually open?)
    rc, out, err = _ssh(
        f"cd {REMOTE_REPO} && python -c \"import sys;sys.path.insert(0,'.');"
        f"from hdlab.director_kb_query import load_default_kb;"
        f"kb=load_default_kb();print(len(kb.entity_names));print(kb.kb_version)\"",
        timeout=180,
    )
    if rc != 0:
        arm.update({"ok": False, "error": f"remote load_default_kb failed rc={rc} err={err}"})
        arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
        return arm
    out_lines = out.strip().splitlines()
    if len(out_lines) < 2:
        arm.update({"ok": False, "error": f"remote KB load output malformed: {out[:200]}"})
        arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
        return arm
    try:
        remote_loaded_n_ent = int(out_lines[0].strip())
    except ValueError:
        arm.update({"ok": False, "error": f"remote n_entities not int: {out_lines[0]!r}"})
        arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
        return arm
    arm["remote_loaded_n_entities"] = remote_loaded_n_ent

    # Canary query: top-1 atom string match
    canary_remote_cmd = (
        f"cd {REMOTE_REPO} && python -c \"import sys,json;sys.path.insert(0,'.');"
        f"from hdlab.director_kb_query import load_default_kb;"
        f"kb=load_default_kb();"
        f"r=kb.query('{CANARY_QUERY}', k={CANARY_K}, confidence_floor=0.0);"
        f"top=r['top_k_atoms'][0] if r['top_k_atoms'] else None;"
        f"print(json.dumps({{'top_atom':top,'refused':r.get('refused')}}))\""
    )
    rc, out, err = _ssh(canary_remote_cmd, timeout=180)
    if rc != 0:
        arm.update({"ok": False, "error": f"remote canary query failed rc={rc} err={err}"})
        arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
        return arm
    try:
        remote_canary = json.loads(out.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError) as e:
        arm.update({"ok": False, "error": f"remote canary output unparseable: {e}"})
        arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
        return arm
    remote_top_atom = remote_canary.get("top_atom")
    arm["remote_canary_top_atom"] = remote_top_atom
    arm["remote_canary_refused"] = remote_canary.get("refused")

    # Local canary query for comparison
    try:
        from hdlab.director_kb_query import load_default_kb
        local_kb = load_default_kb(REPO)
        local_r = local_kb.query(CANARY_QUERY, k=CANARY_K, confidence_floor=0.0)
        local_top = local_r["top_k_atoms"][0] if local_r["top_k_atoms"] else None
        arm["local_canary_top_atom"] = local_top
        # Compare on stable fields: subj/rel/obj triple identity (avoid timestamps)
        if remote_top_atom and local_top:
            r_sig = (remote_top_atom.get("subject"),
                     remote_top_atom.get("relation"),
                     remote_top_atom.get("object"))
            l_sig = (local_top.get("subject"),
                     local_top.get("relation"),
                     local_top.get("object"))
            arm["canary_top1_match"] = bool(r_sig == l_sig)
            arm["canary_remote_sig"] = list(r_sig)
            arm["canary_local_sig"] = list(l_sig)
        else:
            arm["canary_top1_match"] = bool(remote_top_atom == local_top)
    except Exception as e:  # noqa: BLE001
        arm["canary_local_load_error"] = f"{type(e).__name__}: {e}"
        arm["canary_top1_match"] = False

    ok = bool(
        arm["n_entities_match"]
        and arm["kb_version_match"]
        and arm["encoder_match"]
        and arm.get("canary_top1_match", False)
    )
    arm["ok"] = ok
    arm["elapsed_s"] = round(time.perf_counter() - t0, 3)
    return arm


def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    # D4 cardinality
    if len(arms) != EXPECTED_N_ARMS:
        return "HARD_FAIL", (
            f"d4_cardinality_breach: expected {EXPECTED_N_ARMS} arms, got {len(arms)}"
        )
    by = {a["arm"]: a for a in arms}
    local = by.get("ARM_LOCAL_INGEST_FRESHNESS_CHECK", {})
    sync = by.get("ARM_REMOTE_SYNC", {})
    verify = by.get("ARM_REMOTE_VERIFY", {})

    # D3: any arm error/exception => HARD_FAIL
    for a in arms:
        if a.get("error"):
            return "HARD_FAIL", f"arm_exception {a['arm']}: {a['error']}"

    # Local must be OK first; otherwise cannot interpret remote
    if not local.get("ok"):
        return "HARD_FAIL", (
            f"local_freshness_failed: n_ent={local.get('n_entities')}, "
            f"coverage={local.get('coverage_ratio')}, age_s={local.get('manifest_age_s')}"
        )

    if not sync.get("ok"):
        return "HARD_FAIL", (
            f"remote_sync_failed: exit={sync.get('sync_exit_code')}; "
            f"tail={sync.get('sync_stderr_tail', '')[:200]}"
        )

    local_n = local.get("n_entities", 0)
    remote_n = verify.get("remote_n_entities", 0)
    n_match = verify.get("n_entities_match", False)
    kb_ver_match = verify.get("kb_version_match", False)
    enc_match = verify.get("encoder_match", False)
    canary_match = verify.get("canary_top1_match", False)

    if n_match and kb_ver_match and enc_match and canary_match:
        return "HARD_PASS", (
            f"PROVISIONED: local n_ent={local_n} == remote n_ent={remote_n}; "
            f"kb_version match; encoder match; canary top-1 match; "
            f"sync_wall_s={sync.get('sync_wall_s')}; "
            f"bytes={sync.get('bytes_transferred')}"
        )

    # MIDDLE_BAND: partial sync (remote in [0.95, 1.0) * local)
    if local_n > 0:
        ratio = remote_n / local_n if local_n else 0.0
        if MB_REMOTE_RATIO_FLOOR <= ratio < 1.0 and kb_ver_match and enc_match:
            return "MIDDLE_BAND", (
                f"partial_sync_operational: remote/local={ratio:.4f} in "
                f"[{MB_REMOTE_RATIO_FLOOR}, 1.0); kb_version/encoder match; "
                f"canary_match={canary_match}; suspect network truncation"
            )

    return "HARD_FAIL", (
        f"provision_failed: n_match={n_match}, kb_ver_match={kb_ver_match}, "
        f"encoder_match={enc_match}, canary_match={canary_match}; "
        f"local_n={local_n}, remote_n={remote_n}"
    )


def _instrumentation_selftest() -> None:
    """Formula self-tests on synthetic arm dicts."""
    base_local = {"arm": "ARM_LOCAL_INGEST_FRESHNESS_CHECK", "ok": True,
                  "n_entities": 577842, "coverage_ratio": 0.9989,
                  "kb_version": "v1", "encoder": "char_trigram_v1",
                  "manifest_age_s": 100.0}
    base_sync = {"arm": "ARM_REMOTE_SYNC", "ok": True, "sync_exit_code": 0,
                 "sync_wall_s": 900, "bytes_transferred": 5_000_000_000,
                 "audit_complete_record": {"ok": True}}

    # HARD_PASS
    v, _ = _verdict_from_arms([
        base_local, base_sync,
        {"arm": "ARM_REMOTE_VERIFY", "ok": True,
         "remote_n_entities": 577842, "n_entities_match": True,
         "kb_version_match": True, "encoder_match": True,
         "canary_top1_match": True},
    ])
    assert v == "HARD_PASS", f"selftest HP: {v}"

    # HARD_FAIL: D4 cardinality
    v, _ = _verdict_from_arms([base_local, base_sync])
    assert v == "HARD_FAIL", f"selftest HF cardinality: {v}"

    # HARD_FAIL: arm exception
    v, _ = _verdict_from_arms([
        base_local, base_sync,
        {"arm": "ARM_REMOTE_VERIFY", "ok": False, "error": "synthetic test exception"},
    ])
    assert v == "HARD_FAIL", f"selftest HF exception: {v}"

    # HARD_FAIL: local freshness fails
    v, _ = _verdict_from_arms([
        {"arm": "ARM_LOCAL_INGEST_FRESHNESS_CHECK", "ok": False,
         "n_entities": 100, "coverage_ratio": 0.5, "manifest_age_s": 999_999},
        base_sync,
        {"arm": "ARM_REMOTE_VERIFY", "ok": True,
         "remote_n_entities": 0, "n_entities_match": False,
         "kb_version_match": False, "encoder_match": False,
         "canary_top1_match": False},
    ])
    assert v == "HARD_FAIL", f"selftest HF local fresh: {v}"

    # MIDDLE_BAND: 97% sync
    v, _ = _verdict_from_arms([
        base_local, base_sync,
        {"arm": "ARM_REMOTE_VERIFY", "ok": False,
         "remote_n_entities": 560000, "n_entities_match": False,
         "kb_version_match": True, "encoder_match": True,
         "canary_top1_match": True},
    ])
    assert v == "MIDDLE_BAND", f"selftest MB partial: {v}"

    # HARD_FAIL: canary mismatch
    v, _ = _verdict_from_arms([
        base_local, base_sync,
        {"arm": "ARM_REMOTE_VERIFY", "ok": False,
         "remote_n_entities": 577842, "n_entities_match": True,
         "kb_version_match": True, "encoder_match": True,
         "canary_top1_match": False},
    ])
    assert v == "HARD_FAIL", f"selftest HF canary: {v}"

    print("[selftest] substrate_director_kb_remote_provision_v1 formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get(
        "HDLAB_EXP_NAME", "substrate_director_kb_remote_provision_v1"
    )


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true",
                   help="No-op for this cell: provisioning is binary (full or nothing)")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--skip-sync", action="store_true",
                   help="Verify-only mode: skip ARM_REMOTE_SYNC (assume prior sync landed)")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = _exp_dir()
    t0 = time.time()
    print(f"[run] {_exp_name()} smoke={args.smoke} skip_sync={args.skip_sync}", flush=True)

    arms: list[dict] = []

    # ARM 1
    print("[arm] ARM_LOCAL_INGEST_FRESHNESS_CHECK", flush=True)
    local_arm = _arm_local_freshness()
    arms.append(local_arm)
    print(f"  ok={local_arm.get('ok')} n_ent={local_arm.get('n_entities')} "
          f"coverage={local_arm.get('coverage_ratio')} "
          f"age_s={local_arm.get('manifest_age_s')}", flush=True)

    # ARM 2
    if args.skip_sync:
        print("[arm] ARM_REMOTE_SYNC SKIPPED (--skip-sync)", flush=True)
        arms.append({
            "arm": "ARM_REMOTE_SYNC", "ok": True,
            "skipped": True, "elapsed_s": 0.0,
            "note": "skip_sync flag: assume prior sync landed; verify-only run",
            "audit_complete_record": {"ok": True, "skipped": True},
            "sync_exit_code": 0,
        })
    else:
        print("[arm] ARM_REMOTE_SYNC (this is the slow phase; up to 30min for 4.9GB)",
              flush=True)
        sync_arm = _arm_remote_sync()
        arms.append(sync_arm)
        print(f"  ok={sync_arm.get('ok')} exit={sync_arm.get('sync_exit_code')} "
              f"wall_s={sync_arm.get('sync_wall_s')} "
              f"bytes={sync_arm.get('bytes_transferred')}", flush=True)

    # ARM 3
    print("[arm] ARM_REMOTE_VERIFY", flush=True)
    verify_arm = _arm_remote_verify(local_arm)
    arms.append(verify_arm)
    print(f"  ok={verify_arm.get('ok')} remote_n_ent={verify_arm.get('remote_n_entities')} "
          f"n_match={verify_arm.get('n_entities_match')} "
          f"canary_match={verify_arm.get('canary_top1_match')}", flush=True)

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)

    payload: dict[str, Any] = {
        "anchor": _exp_name(),
        "smoke": bool(args.smoke),
        "skip_sync": bool(args.skip_sync),
        "arms": arms,
        "local_n_entities": local_arm.get("n_entities"),
        "remote_n_entities": verify_arm.get("remote_n_entities"),
        "local_kb_version": local_arm.get("kb_version"),
        "remote_kb_version": verify_arm.get("remote_kb_version"),
        "canary_query_top1_match": verify_arm.get("canary_top1_match"),
        "sync_wall_s": arms[1].get("sync_wall_s") if len(arms) > 1 else None,
        "bytes_transferred": arms[1].get("bytes_transferred") if len(arms) > 1 else None,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
    }

    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "verdict_msg": vm,
                   "elapsed_s": elapsed, "summary": payload},
                  f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
