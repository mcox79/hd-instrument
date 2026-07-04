"""_autorefill_watcher_smoke.py -- offline smoke harness for autorefill_watcher.py.

Two layers:
  1. Direct calls into autorefill_watcher.decide() (pure function, no IO) with
     synthetic world/pool/fallback/state fixtures -- covers every branch: pool-fill,
     pool-empty->fallback-fill, fallback cap (2 consecutive) + alert + quiet,
     fallback exhaustion + alert + quiet, cap-reset-on-pool-refill, zombie/missing
     runner skip, not-idle skip, double-queue (stale pool dup) skip.
  2. One end-to-end CLI invocation of `python tools/autorefill_watcher.py
     --test-state ... --pool ... --fallback ... --state ... --paused-flag ...
     --enabled-flag ... --dry-run` against SCRATCH files only, proving the argv/
     JSON-loading/dispatch-command-construction path works without any SSH call
     and without touching data/autorefill_pool.json, data/autorefill_fallback_
     cell.json, data/orchestrator_paused.flag, or data/autorefill_enabled.flag,
     and WITHOUT ever invoking queue_add.sh for real (--dry-run short-circuits
     before the subprocess call). No real runner or queue is touched by this file.

Run: python d:/AI/hd-instrument/tools/_autorefill_watcher_smoke.py
Exits 0 if all checks pass, 1 otherwise (prints FAIL lines).
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import autorefill_watcher as arw  # noqa: E402

FAILS: list[str] = []


def check(name: str, cond: bool, detail: str = "") -> None:
    if cond:
        print(f"PASS: {name}")
    else:
        msg = f"FAIL: {name}" + (f" -- {detail}" if detail else "")
        print(msg)
        FAILS.append(msg)


def idle_world(gpu_idle=True, cpu_idle=False, gpu_entries=None, cpu_entries=None):
    return {
        "overnight_queue": {
            "runner_verdict": "ALIVE", "idle": gpu_idle, "status": "idle" if gpu_idle else "running_cell",
            "pending": 0 if gpu_idle else 0, "running": 0 if gpu_idle else 1,
            "queue_entries": gpu_entries or ([] if gpu_idle else [{"name": "busy_cell", "status": "running"}]),
        },
        "remote_cpu_queue": {
            "runner_verdict": "ALIVE", "idle": cpu_idle, "status": "idle" if cpu_idle else "running_cell",
            "pending": 0 if cpu_idle else 0, "running": 0 if cpu_idle else 1,
            "queue_entries": cpu_entries or ([] if cpu_idle else [{"name": "busy_cell2", "status": "running"}]),
        },
    }


# --- Scenario A: pool has an entry for the idle GPU queue -> pool-fill -------
def scenario_a():
    world = idle_world(gpu_idle=True, cpu_idle=False)
    pool = {"pool": [{"id": "p1", "queue": "overnight_queue", "name": "test_cell_1",
                       "script": "experiments/exp_test.py", "prereg": "preregs/test.md", "timeout_s": 600}]}
    actions, new_state, logs, remove_ids = arw.decide(world, pool, {}, {})
    check("A: exactly one action", len(actions) == 1, str(actions))
    if actions:
        check("A: action is pool-kind for overnight_queue", actions[0]["kind"] == "pool" and actions[0]["queue"] == "overnight_queue")
        check("A: dispatched entry id is p1", actions[0]["entry"]["id"] == "p1")
    check("A: p1 marked for pool removal", remove_ids == {"p1"}, str(remove_ids))
    check("A: POOL-FILL logged", any("POOL-FILL" in l for l in logs), str(logs))
    check("A: cpu queue got NOT-IDLE (busy, untouched)", any("NOT-IDLE" in l and "cpu_runner_0" in l for l in logs))
    check("A: gpu consecutive_fallback stays 0", new_state["gpu_runner_0"]["consecutive_fallback"] == 0)


# --- Scenario B: pool empty, fallback has one candidate -> fallback-fill -----
def scenario_b():
    world = idle_world(gpu_idle=True, cpu_idle=False)
    pool = {"pool": []}
    fallback = {"overnight_queue": {
        "active": True, "cell_id": "encoder_test", "prereg": "preregs/test.md", "timeout_s": 600,
        "candidate_seeds": [{"name": "encoder_test_seed_1", "script": "experiments/exp_test_seed1.py", "dispatched": False}],
    }}
    actions, new_state, logs, remove_ids = arw.decide(world, pool, fallback, {})
    check("B: exactly one action", len(actions) == 1, str(actions))
    if actions:
        check("B: action is fallback-kind", actions[0]["kind"] == "fallback")
        check("B: candidate name matches", actions[0]["candidate"]["name"] == "encoder_test_seed_1")
    check("B: FALLBACK-FILL logged (pool was empty)", any("FALLBACK-FILL" in l for l in logs), str(logs))
    check("B: POOL-EMPTY logged before fallback", any("POOL-EMPTY" in l for l in logs))
    check("B: consecutive_fallback now 1", new_state["gpu_runner_0"]["consecutive_fallback"] == 1)


# --- Scenario C: fallback cap (2 consecutive) -> alert -> quiet -> reset -----
def scenario_c():
    fallback = {"overnight_queue": {
        "active": True, "cell_id": "encoder_test", "prereg": "preregs/test.md", "timeout_s": 600,
        "candidate_seeds": [
            {"name": "seed_1", "script": "experiments/exp_seed1.py", "dispatched": False},
            {"name": "seed_2", "script": "experiments/exp_seed2.py", "dispatched": False},
            {"name": "seed_3", "script": "experiments/exp_seed3.py", "dispatched": False},
        ],
    }}
    world = idle_world(gpu_idle=True, cpu_idle=False)
    state = {}

    # call 1 -> dispatch seed_1, consecutive=1
    actions, state, logs, _ = arw.decide(world, {"pool": []}, fallback, state)
    check("C1: dispatches seed_1", len(actions) == 1 and actions[0]["candidate"]["name"] == "seed_1")
    check("C1: consecutive=1", state["gpu_runner_0"]["consecutive_fallback"] == 1)
    fallback["overnight_queue"]["candidate_seeds"][0]["dispatched"] = True  # simulate main() persisting it

    # call 2 -> dispatch seed_2, consecutive=2 (allowed: check is BEFORE increment, 1 < cap 2)
    actions, state, logs, _ = arw.decide(world, {"pool": []}, fallback, state)
    check("C2: dispatches seed_2", len(actions) == 1 and actions[0]["candidate"]["name"] == "seed_2")
    check("C2: consecutive=2", state["gpu_runner_0"]["consecutive_fallback"] == 2)
    fallback["overnight_queue"]["candidate_seeds"][1]["dispatched"] = True

    # call 3 -> cap reached (2 >= 2): BLOCKED even though seed_3 is available
    actions, state, logs, _ = arw.decide(world, {"pool": []}, fallback, state)
    check("C3: cap blocks dispatch of seed_3", len(actions) == 0, str(actions))
    check("C3: FALLBACK-CAP-ALERT logged", any("FALLBACK-CAP-ALERT" in l for l in logs), str(logs))
    check("C3: alerted flag set", state["gpu_runner_0"]["alerted"] is True)
    check("C3: consecutive stays at 2 (not incremented further)", state["gpu_runner_0"]["consecutive_fallback"] == 2)

    # call 4 -> still capped, already alerted -> quiet variant, still no dispatch (no spam re-alert)
    actions, state, logs, _ = arw.decide(world, {"pool": []}, fallback, state)
    check("C4: still blocked", len(actions) == 0)
    check("C4: FALLBACK-CAP-QUIET logged (not re-ALERT)", any("FALLBACK-CAP-QUIET" in l for l in logs), str(logs))
    check("C4: no duplicate ALERT spam", not any("FALLBACK-CAP-ALERT" in l for l in logs))

    # call 5 -> pool refills for overnight_queue -> cap resets, pool takes priority
    pool = {"pool": [{"id": "p9", "queue": "overnight_queue", "name": "real_cell",
                       "script": "experiments/exp_real.py", "prereg": "preregs/real.md", "timeout_s": 600}]}
    actions, state, logs, remove_ids = arw.decide(world, pool, fallback, state)
    check("C5: pool entry dispatched once pool refills", len(actions) == 1 and actions[0]["kind"] == "pool")
    check("C5: consecutive_fallback reset to 0", state["gpu_runner_0"]["consecutive_fallback"] == 0)
    check("C5: alerted reset to False", state["gpu_runner_0"]["alerted"] is False)


# --- Scenario D: fallback candidates all exhausted (dispatched already) -----
def scenario_d():
    world = idle_world(gpu_idle=True, cpu_idle=False)
    fallback = {"overnight_queue": {
        "active": True, "cell_id": "encoder_test", "prereg": "preregs/test.md", "timeout_s": 600,
        "candidate_seeds": [{"name": "seed_1", "script": "experiments/exp_seed1.py", "dispatched": True}],
    }}
    actions, state, logs, _ = arw.decide(world, {"pool": []}, fallback, {})
    check("D1: no action (exhausted)", len(actions) == 0)
    check("D1: FALLBACK-EXHAUSTED-ALERT logged", any("FALLBACK-EXHAUSTED-ALERT" in l for l in logs), str(logs))
    actions, state, logs, _ = arw.decide(world, {"pool": []}, fallback, state)
    check("D2: quiet on second exhausted cycle", any("FALLBACK-EXHAUSTED-QUIET" in l for l in logs), str(logs))


# --- Scenario E: zombie / missing runner -> never autofilled ----------------
def scenario_e():
    world = {
        "overnight_queue": {"runner_verdict": "ZOMBIE", "idle": False, "status": "idle", "pending": 0, "running": 0, "queue_entries": []},
        "remote_cpu_queue": {"runner_verdict": "MISSING", "idle": False, "status": None, "pending": 0, "running": 0, "queue_entries": []},
    }
    pool = {"pool": [
        {"id": "p1", "queue": "overnight_queue", "name": "x", "script": "s", "prereg": "p", "timeout_s": 1},
        {"id": "p2", "queue": "remote_cpu_queue", "name": "y", "script": "s", "prereg": "p", "timeout_s": 1},
    ]}
    actions, state, logs, remove_ids = arw.decide(world, pool, {}, {})
    check("E: no actions for zombie/missing runners", len(actions) == 0, str(actions))
    check("E: ZOMBIE-SKIP logged for gpu", any("ZOMBIE-SKIP" in l and "gpu_runner_0" in l for l in logs))
    check("E: NO-HEARTBEAT logged for cpu", any("NO-HEARTBEAT" in l and "cpu_runner_0" in l for l in logs))
    check("E: nothing removed from pool (never got to dispatch)", remove_ids == set())


# --- Scenario F: double-queue guard (stale pool dup skipped, next one taken) -
def scenario_f():
    world = idle_world(gpu_idle=True, cpu_idle=False,
                        gpu_entries=[{"name": "already_running_dup", "status": "pending"}])
    pool = {"pool": [
        {"id": "dup1", "queue": "overnight_queue", "name": "already_running_dup",
         "script": "s", "prereg": "p", "timeout_s": 1},
        {"id": "clean1", "queue": "overnight_queue", "name": "clean_entry",
         "script": "s2", "prereg": "p2", "timeout_s": 2},
    ]}
    actions, state, logs, remove_ids = arw.decide(world, pool, {}, {})
    check("F: dup skipped, clean one dispatched", len(actions) == 1 and actions[0]["entry"]["id"] == "clean1", str(actions))
    check("F: both dup and dispatched id marked for pool removal", remove_ids == {"dup1", "clean1"}, str(remove_ids))
    check("F: SKIP-DUP logged", any("SKIP-DUP" in l for l in logs), str(logs))


# --- End-to-end CLI dry-run against scratch files only ----------------------
def scenario_cli_end_to_end():
    with tempfile.TemporaryDirectory() as td:
        tdp = Path(td)
        test_state = tdp / "world.json"
        pool_path = tdp / "pool.json"
        fallback_path = tdp / "fallback.json"
        state_path = tdp / "state.json"
        enabled_flag = tdp / "enabled.flag"
        paused_flag = tdp / "paused.flag"  # deliberately NOT created -> not paused

        test_state.write_text(json.dumps(idle_world(gpu_idle=True, cpu_idle=False)), encoding="utf-8")
        pool_path.write_text(json.dumps({"pool": [
            {"id": "e2e1", "queue": "overnight_queue", "name": "e2e_cell",
             "script": "experiments/exp_e2e.py", "prereg": "preregs/e2e.md", "timeout_s": 42},
        ]}), encoding="utf-8")
        fallback_path.write_text(json.dumps({}), encoding="utf-8")
        state_path.write_text(json.dumps({}), encoding="utf-8")
        enabled_flag.write_text("", encoding="utf-8")

        cmd = [
            sys.executable, str(REPO / "tools" / "autorefill_watcher.py"),
            "--dry-run",
            "--test-state", str(test_state),
            "--pool", str(pool_path),
            "--fallback", str(fallback_path),
            "--state", str(state_path),
            "--enabled-flag", str(enabled_flag),
            "--paused-flag", str(paused_flag),
        ]
        result = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=60)
        out = result.stdout + result.stderr
        check("CLI: exit code 0", result.returncode == 0, out[-800:])
        check("CLI: POOL-FILL fired", "POOL-FILL" in out, out[-800:])
        check("CLI: DRY-RUN would-run line printed", "DRY-RUN] would run:" in out, out[-800:])
        check("CLI: dry-run references queue_add.sh", "queue_add.sh" in out, out[-800:])
        check("CLI: dry-run references e2e_cell", "e2e_cell" in out, out[-800:])
        # Dry-run must not mutate the pool file it read from.
        pool_after = json.loads(pool_path.read_text(encoding="utf-8"))
        check("CLI: dry-run left pool.json untouched", pool_after["pool"][0]["id"] == "e2e1", str(pool_after))

        # Second CLI check: disabled (no enabled flag) -> must no-op cleanly.
        enabled_flag.unlink()
        result2 = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=60)
        out2 = result2.stdout + result2.stderr
        check("CLI-disabled: exit 0", result2.returncode == 0)
        check("CLI-disabled: DISABLED tag logged", "DISABLED" in out2, out2[-500:])
        check("CLI-disabled: no dispatch attempted", "DRY-RUN] would run" not in out2, out2[-500:])

        # Third CLI check: paused flag present -> must no-op even though enabled.
        enabled_flag.write_text("", encoding="utf-8")
        paused_flag.write_text("", encoding="utf-8")
        result3 = subprocess.run(cmd, cwd=str(REPO), capture_output=True, text=True, timeout=60)
        out3 = result3.stdout + result3.stderr
        check("CLI-paused: exit 0", result3.returncode == 0)
        check("CLI-paused: PAUSED tag logged", "PAUSED" in out3, out3[-500:])
        check("CLI-paused: no dispatch attempted", "DRY-RUN] would run" not in out3, out3[-500:])


def main() -> int:
    scenario_a()
    scenario_b()
    scenario_c()
    scenario_d()
    scenario_e()
    scenario_f()
    scenario_cli_end_to_end()

    print()
    if FAILS:
        print(f"{len(FAILS)} FAILURE(S):")
        for f in FAILS:
            print(" ", f)
        return 1
    print("ALL SMOKE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
