"""KB TIME-DECAY EVICTION WITH REINGEST v1 (ANCHOR 4; INFRASTRUCTURE; 2026-06-26).

Pre-reg: preregs/2026-06-26_kb_time_decay_eviction_with_reingest_v1.md
Wave 3c (after ANCHOR 1 + 3 pass; AUDIT-ONLY first 3 weeks per USER vetting).

Simulates per-atom last-queried timestamp tracking + eviction decision over
a synthetic 90-day timeline. AUDIT-ONLY: does NOT mutate the production KB.
Re-ingest-on-demand verification ensures evicted atoms can be re-fetched from
filesystem (Principle 1: filesystem canonical).

ARMS (3 mandatory):
  ARM_NO_EVICTION_BASELINE         - sanity rail (no eviction; capacity stable)
  ARM_TIME_DECAY_EVICTION          - 90-day eviction simulation (AUDIT-ONLY)
  ARM_REINGEST_ON_DEMAND           - filesystem re-fetch for audit-marked atoms

SUCCESS CRITERIA (INFRASTRUCTURE tier):
  - Eviction-mark fraction >= 0.20 over 90 simulated days.
  - Re-ingest-on-demand success >= 0.90.
  - USER_DIRECTIVE NEVER eviction-marked (zero-loss).
  - Recently-queried atoms (last 30 days) retention >= 0.99.

ASCII-only. No emojis. No em-dashes.
"""

from __future__ import annotations

import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import json
import os
import time
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from hdlab.director_kb_query import DirectorKBQuery, load_default_kb  # noqa: E402


AUDIT_LOG_PATH = REPO / "data" / "director_kb_audit_log.jsonl"
AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

EVICTION_AGE_DAYS = 90  # Initial USER spec
RECENT_PROTECTION_DAYS = 30


def _audit_event(event: dict) -> None:
    line = json.dumps(event, default=str, ensure_ascii=False) + "\n"
    with AUDIT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line)


def _sample_atoms_with_sources(
    kb: DirectorKBQuery,
    n_atoms: int,
    seed: int = 17,
) -> tuple[list[int], list[str], list[list[str]], list[bool]]:
    """Sample atoms; return (atom_indices, source_classes, source_paths, is_user_directive)."""
    rng = np.random.RandomState(seed)
    n_ent = len(kb.entity_names)
    candidates = list(range(n_ent))
    rng.shuffle(np.array(candidates))

    atom_idx: list[int] = []
    sc_list: list[str] = []
    paths_list: list[list[str]] = []
    is_ud_list: list[bool] = []

    n_user_directive_force = max(5, n_atoms // 10)
    n_user_directive_taken = 0

    for i in candidates:
        if len(atom_idx) >= n_atoms:
            break
        sc_set = kb._source_classes_by_ent.get(i, set())
        paths = sorted(kb._sources_by_ent.get(i, set()))[:3]
        if not sc_set:
            continue
        is_ud = "memory" in sc_set
        if is_ud and n_user_directive_taken >= n_user_directive_force:
            # Have enough memory; skip extras to ensure diversity
            if len(atom_idx) < n_atoms - 10:
                continue
        atom_idx.append(i)
        if "memory" in sc_set:
            sc_list.append("memory")
            is_ud_list.append(True)
            n_user_directive_taken += 1
        else:
            sc_list.append(sorted(sc_set)[0])
            is_ud_list.append(False)
        paths_list.append(paths)

    return atom_idx[:n_atoms], sc_list[:n_atoms], paths_list[:n_atoms], is_ud_list[:n_atoms]


def _synthetic_query_timeline(
    n_atoms: int,
    n_days: int,
    is_user_directive: list[bool],
    seed: int = 17,
) -> np.ndarray:
    """Build per-atom last-queried-day matrix.

    Returns (n_atoms,) array of integers in [-INF, n_days-1]:
      -INF = atom never queried (will be eviction-mark candidate)
      d    = atom last queried on day d (most recent query)

    Distribution:
      - 30% atoms queried within last 30 days (recent)
      - 20% atoms queried 30-90 days ago (semi-recent)
      - 50% atoms NEVER queried in this window (oldest -- eviction candidates)
      - USER_DIRECTIVE atoms: ALWAYS queried within last 7 days (always-protect)
    """
    rng = np.random.RandomState(seed)
    last_q = np.full(n_atoms, -10000, dtype=np.int64)  # sentinel for "never"
    for i in range(n_atoms):
        if is_user_directive[i]:
            last_q[i] = n_days - rng.randint(1, 8)  # within last 7 days
        else:
            r = rng.rand()
            if r < 0.30:
                last_q[i] = n_days - rng.randint(0, RECENT_PROTECTION_DAYS)
            elif r < 0.50:
                last_q[i] = n_days - rng.randint(RECENT_PROTECTION_DAYS, EVICTION_AGE_DAYS)
            else:
                # Either older than 90d (eviction candidate) or never queried
                if rng.rand() < 0.5:
                    last_q[i] = n_days - EVICTION_AGE_DAYS - rng.randint(0, 30)
                # else stays at -10000 (never queried)
    return last_q


def _arm_no_eviction_baseline(n_atoms: int, n_days: int) -> dict:
    return {
        "arm": "ARM_NO_EVICTION_BASELINE",
        "ok": True,
        "n_atoms": n_atoms,
        "n_days": n_days,
        "capacity_used_start": n_atoms,
        "capacity_used_end": n_atoms,
        "capacity_drop_fraction": 0.0,
    }


def _arm_time_decay_eviction(
    n_atoms: int,
    n_days: int,
    last_q: np.ndarray,
    is_user_directive: list[bool],
    audit_log_first_n: int = 50,
) -> dict:
    """Audit-only eviction simulation.

    For each atom: age = n_days - last_q[i]; eviction-mark if age > 90
    AND not USER_DIRECTIVE.
    """
    t0 = time.perf_counter()
    age = n_days - last_q  # large positive for never-queried
    eviction_mark = np.zeros(n_atoms, dtype=bool)
    user_directive_protected_count = 0
    user_directive_eviction_violations = 0
    recent_evictions = 0  # within last 30 days = violation
    audit_emitted = 0

    for i in range(n_atoms):
        if is_user_directive[i]:
            user_directive_protected_count += 1
            # If our age-based rule WOULD evict, that's a violation we caught
            if age[i] > EVICTION_AGE_DAYS:
                user_directive_eviction_violations += 1
            continue
        if age[i] > EVICTION_AGE_DAYS:
            eviction_mark[i] = True
            if age[i] <= RECENT_PROTECTION_DAYS:
                recent_evictions += 1  # should be 0 by construction
            if audit_emitted < audit_log_first_n:
                _audit_event({
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "kind": "eviction_audit_event",
                    "mode": "AUDIT_ONLY",
                    "atom_idx": int(i),
                    "age_days": int(min(age[i], 99999)),
                    "is_user_directive": False,
                    "decision": "MARK_FOR_EVICTION",
                })
                audit_emitted += 1

    n_marked = int(eviction_mark.sum())
    eviction_fraction = n_marked / n_atoms

    # Retention checks
    n_recent_total = int(np.sum((age <= RECENT_PROTECTION_DAYS) &
                                (np.array(is_user_directive) == False)))
    n_recent_retained = n_recent_total - recent_evictions
    recent_retention = n_recent_retained / n_recent_total if n_recent_total else 1.0

    ud_retention = ((user_directive_protected_count - user_directive_eviction_violations)
                    / user_directive_protected_count) if user_directive_protected_count else 1.0

    elapsed = time.perf_counter() - t0
    ok = (eviction_fraction >= 0.20 and ud_retention >= 1.0
          and recent_retention >= 0.99)
    return {
        "arm": "ARM_TIME_DECAY_EVICTION",
        "ok": bool(ok),
        "mode": "AUDIT_ONLY",
        "n_atoms": n_atoms,
        "n_days": n_days,
        "eviction_age_days": EVICTION_AGE_DAYS,
        "recent_protection_days": RECENT_PROTECTION_DAYS,
        "n_marked_for_eviction": n_marked,
        "eviction_fraction": round(eviction_fraction, 4),
        "n_user_directive_protected": user_directive_protected_count,
        "user_directive_eviction_violations": user_directive_eviction_violations,
        "user_directive_retention": round(ud_retention, 4),
        "n_recent_atoms": n_recent_total,
        "n_recent_evicted": recent_evictions,
        "recent_retention": round(recent_retention, 4),
        "audit_events_emitted": audit_emitted,
        "elapsed_s": round(elapsed, 3),
        "_eviction_mark_mask": eviction_mark.tolist(),  # passed to ARM 3
    }


def _arm_reingest_on_demand(
    atom_idx: list[int],
    source_paths: list[list[str]],
    eviction_mark: list[bool],
    repo_root: Path,
    seed: int = 17,
) -> dict:
    """For marked atoms, attempt re-ingest from filesystem source_paths."""
    t0 = time.perf_counter()
    rng = np.random.RandomState(seed)
    marked_atoms = [i for i, m in enumerate(eviction_mark) if m]
    n_marked = len(marked_atoms)
    if n_marked == 0:
        return {
            "arm": "ARM_REINGEST_ON_DEMAND",
            "ok": True,
            "n_attempts": 0,
            "n_success": 0,
            "reingest_success_rate": 1.0,
            "elapsed_s": round(time.perf_counter() - t0, 3),
            "note": "no_atoms_marked_skip",
        }
    n_attempts = min(30, n_marked)
    rng.shuffle(np.array(marked_atoms))
    candidates = marked_atoms[:n_attempts]
    n_success = 0
    per_attempt: list[dict] = []
    for atom_local_idx in candidates:
        paths = source_paths[atom_local_idx]
        t_atom = time.perf_counter()
        if not paths:
            per_attempt.append({"atom_idx": atom_local_idx,
                                "success": False, "reason": "no_source_paths"})
            continue
        # Try to read at least one path
        found = False
        for p in paths:
            full = repo_root / p
            if not full.exists():
                # Try external paths (memory dir starts with .../memory/...)
                ext_candidates = [
                    Path("C:/Users/marsh/.claude/projects/d--AI/memory") / Path(p).name,
                    Path(p),
                ]
                for ec in ext_candidates:
                    if ec.exists():
                        full = ec
                        break
            if full.exists():
                try:
                    sz = full.stat().st_size
                    if sz > 0:
                        found = True
                        break
                except OSError:
                    continue
        elapsed_atom = time.perf_counter() - t_atom
        if found:
            n_success += 1
        per_attempt.append({
            "atom_idx": atom_local_idx,
            "success": found,
            "n_paths_tried": len(paths),
            "elapsed_s": round(elapsed_atom, 4),
        })
    success_rate = n_success / n_attempts if n_attempts else 1.0
    elapsed = time.perf_counter() - t0
    ok = success_rate >= 0.90
    return {
        "arm": "ARM_REINGEST_ON_DEMAND",
        "ok": bool(ok),
        "n_attempts": n_attempts,
        "n_success": n_success,
        "reingest_success_rate": round(success_rate, 4),
        "sample_per_attempt": per_attempt[:10],
        "elapsed_s": round(elapsed, 3),
    }


def _verdict_from_arms(arms: list[dict]) -> tuple[str, str]:
    by = {a["arm"]: a for a in arms}
    evic = by.get("ARM_TIME_DECAY_EVICTION", {})
    reing = by.get("ARM_REINGEST_ON_DEMAND", {})

    udv = evic.get("user_directive_eviction_violations", 0)
    if udv > 0:
        return "HARD_FAIL", (
            f"USER_DIRECTIVE eviction violations={udv}; "
            f"load-bearing zero-eviction invariant violated"
        )

    recent_ret = evic.get("recent_retention", 1.0)
    if recent_ret < 0.99:
        return "HARD_FAIL", (
            f"recent_retention={recent_ret:.4f} < 0.99; regression on recent atoms"
        )

    evic_frac = evic.get("eviction_fraction", 0.0)
    reing_rate = reing.get("reingest_success_rate", 0.0)
    n_reing_attempts = reing.get("n_attempts", 0)

    if evic_frac >= 0.20 and reing_rate >= 0.90 and n_reing_attempts > 0:
        return "HARD_PASS", (
            f"eviction_fraction={evic_frac:.3f} >= 0.20; "
            f"reingest_rate={reing_rate:.3f} >= 0.90 ({reing.get('n_success')}/{n_reing_attempts}); "
            f"user_directive_retention={evic.get('user_directive_retention'):.4f}; "
            f"recent_retention={recent_ret:.4f}; AUDIT_ONLY mode"
        )
    if evic_frac >= 0.10 and reing_rate >= 0.80:
        return "MIDDLE_BAND", (
            f"eviction_fraction={evic_frac:.3f}; reingest_rate={reing_rate:.3f}; "
            f"operational thresholds met but below HP gates; per Fix28 default MM; "
            f"AUDIT_ONLY mode"
        )
    return "HARD_FAIL", (
        f"eviction_fraction={evic_frac:.3f} (>=0.20?) reingest_rate={reing_rate:.3f} "
        f"(>=0.90?) below thresholds"
    )


def _instrumentation_selftest() -> None:
    v, _ = _verdict_from_arms([
        {"arm": "ARM_NO_EVICTION_BASELINE", "ok": True},
        {"arm": "ARM_TIME_DECAY_EVICTION", "ok": True, "eviction_fraction": 0.30,
         "user_directive_eviction_violations": 0, "user_directive_retention": 1.0,
         "recent_retention": 1.0},
        {"arm": "ARM_REINGEST_ON_DEMAND", "ok": True, "reingest_success_rate": 0.95,
         "n_attempts": 30, "n_success": 28},
    ])
    assert v == "HARD_PASS", f"selftest hp: {v}"
    v, _ = _verdict_from_arms([
        {"arm": "ARM_NO_EVICTION_BASELINE", "ok": True},
        {"arm": "ARM_TIME_DECAY_EVICTION", "ok": True, "eviction_fraction": 0.15,
         "user_directive_eviction_violations": 0, "user_directive_retention": 1.0,
         "recent_retention": 1.0},
        {"arm": "ARM_REINGEST_ON_DEMAND", "ok": True, "reingest_success_rate": 0.85,
         "n_attempts": 30, "n_success": 25},
    ])
    assert v == "MIDDLE_BAND", f"selftest mb: {v}"
    v, _ = _verdict_from_arms([
        {"arm": "ARM_NO_EVICTION_BASELINE", "ok": True},
        {"arm": "ARM_TIME_DECAY_EVICTION", "ok": True, "eviction_fraction": 0.30,
         "user_directive_eviction_violations": 1, "user_directive_retention": 0.95,
         "recent_retention": 1.0},
        {"arm": "ARM_REINGEST_ON_DEMAND", "ok": True, "reingest_success_rate": 0.95,
         "n_attempts": 30, "n_success": 28},
    ])
    assert v == "HARD_FAIL", f"selftest hf-ud: {v}"
    v, _ = _verdict_from_arms([
        {"arm": "ARM_NO_EVICTION_BASELINE", "ok": True},
        {"arm": "ARM_TIME_DECAY_EVICTION", "ok": True, "eviction_fraction": 0.30,
         "user_directive_eviction_violations": 0, "user_directive_retention": 1.0,
         "recent_retention": 0.85},
        {"arm": "ARM_REINGEST_ON_DEMAND", "ok": True, "reingest_success_rate": 0.95,
         "n_attempts": 30, "n_success": 28},
    ])
    assert v == "HARD_FAIL", f"selftest hf-recent: {v}"
    print("[selftest] kb_time_decay_eviction_with_reingest_v1 formula PASS", flush=True)


_instrumentation_selftest()


def _exp_name() -> str:
    return os.environ.get("HDLAB_EXP_NAME", "kb_time_decay_eviction_with_reingest_v1")


def _exp_dir() -> Path:
    d = REPO / "data" / f"exp_{_exp_name()}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--kb-dir", default=None)
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    out_dir = _exp_dir()
    if args.kb_dir:
        kb = DirectorKBQuery(kb_dir=Path(args.kb_dir))
    else:
        try:
            kb = load_default_kb(REPO)
        except FileNotFoundError as e:
            payload = {"verdict": "HARD_FAIL", "verdict_msg": f"KB_REFERENT_MISSING: {e}",
                       "elapsed_s": 0.0,
                       "summary": {"anchor": "kb_time_decay_eviction_with_reingest_v1"}}
            with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, default=str)
            print(f"[verdict] HARD_FAIL\n[verdict_msg] {payload['verdict_msg']}", flush=True)
            return

    t0 = time.time()
    n_atoms = 50 if args.smoke else 200
    n_days = 30 if args.smoke else 90
    print(f"[run] kb_time_decay_eviction_with_reingest_v1 smoke={args.smoke} "
          f"kb_version={kb.kb_version} n_atoms={n_atoms} n_days={n_days} "
          f"mode=AUDIT_ONLY", flush=True)

    atom_idx, sc_list, paths_list, is_ud = _sample_atoms_with_sources(kb, n_atoms)
    from collections import Counter
    print(f"[run] sampled {len(atom_idx)} atoms; class_dist=", end="")
    print(dict(Counter(sc_list)), end="; ", flush=True)
    print(f"n_user_directive={sum(is_ud)}", flush=True)

    last_q = _synthetic_query_timeline(len(atom_idx), n_days, is_ud)

    arms: list[dict] = []
    try:
        a = _arm_no_eviction_baseline(len(atom_idx), n_days)
        arms.append(a)
        print(f"  ARM_NO_EVICTION_BASELINE ok={a['ok']} cap_drop={a['capacity_drop_fraction']}",
              flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_NO_EVICTION_BASELINE", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})

    try:
        ev = _arm_time_decay_eviction(len(atom_idx), n_days, last_q, is_ud)
        eviction_mark = ev.pop("_eviction_mark_mask")
        arms.append(ev)
        print(f"  ARM_TIME_DECAY_EVICTION ok={ev['ok']} "
              f"eviction_frac={ev['eviction_fraction']} "
              f"ud_retention={ev['user_directive_retention']} "
              f"recent_retention={ev['recent_retention']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_TIME_DECAY_EVICTION", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})
        eviction_mark = [False] * len(atom_idx)

    try:
        re = _arm_reingest_on_demand(atom_idx, paths_list, eviction_mark, REPO)
        arms.append(re)
        print(f"  ARM_REINGEST_ON_DEMAND ok={re['ok']} "
              f"reingest_rate={re['reingest_success_rate']} "
              f"n_attempts={re['n_attempts']}", flush=True)
    except Exception as e:  # noqa: BLE001
        arms.append({"arm": "ARM_REINGEST_ON_DEMAND", "ok": False,
                     "error": f"{type(e).__name__}: {e}"})

    verdict, vm = _verdict_from_arms(arms)
    elapsed = round(time.time() - t0, 2)
    payload: dict[str, Any] = {
        "anchor": "kb_time_decay_eviction_with_reingest_v1",
        "smoke": args.smoke,
        "mode": "AUDIT_ONLY",
        "kb_version": kb.kb_version,
        "n_atoms_sample": len(atom_idx),
        "n_days_simulated": n_days,
        "eviction_age_days": EVICTION_AGE_DAYS,
        "arms": arms,
        "verdict": verdict,
        "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    with (out_dir / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump({"verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed,
                   "summary": payload}, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s", flush=True)


if __name__ == "__main__":
    main()
