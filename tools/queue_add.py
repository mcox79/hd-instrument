"""Queue-entry gate: verify a script is queueable before adding it.

Usage:
    python tools/queue_add.py <queue_name> <entry_name> <script_path> \\
        --prereg preregs/<file>.md --timeout <seconds>

NOTE: --timeout is REQUIRED (no silent default). exp_dev must estimate per-anchor:
    timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)**scaling_exp * (FULL_seeds/smoke_seeds))
    scaling_exp: 1.0-1.5 most sweeps, 2.0 matrix ops. Estimates >14400 (4h) need prereq justification.

Required checks (script must pass ALL):
    1. Script file exists.
    1b. PROT-018: anchor _n<N> suffix binds to script production N (exit 6).
    1c. PROT-019: anchor _n>=4096 requires --timeout >= 3600s (exit 7).
    2. Script supports `--self-test` and exits 0.
    3. Script supports `--smoke` and exits 0, producing metrics.json at
       data/exp_{HDLAB_EXP_NAME}/metrics.json with required fields.
    4. Prereg markdown file exists.

Prevents the silent-failure mode from 2026-05-20 where scripts wrote to
hardcoded names while the queue renamed them, producing zero metrics.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from safe_queue import QueueLock  # noqa: E402

PYTHON = sys.executable
REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")
SMOKE_TIMEOUT_S = 180  # 3 min cap on smoke


def fail(msg: str) -> "None":
    print(f"GATE_FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def check_script_exists(script: str) -> Path:
    path = REPO / script
    if not path.exists():
        fail(f"script not found: {path}")
    return path


def run_with_flag(script: Path, flag: str, env_extra: dict) -> tuple[int, str]:
    """Run script with single flag. Return (exit_code, tail_of_log).

    Uses a temp log file (matches the actual runner's approach) instead of
    capture_output, which has pipe-buffering issues with CUDA-heavy scripts.

    Smoke timeout (per Skunkworks 2026-06-18 ratify): per-dispatch override via
    HDLAB_SMOKE_TIMEOUT_S env var; default SMOKE_TIMEOUT_S=180 UNCHANGED for all
    other cells (a global raise would weaken hang-catch for genuinely-hung cells
    -- the historical 4hr-CPU-on-GPU incident is exactly why the cap exists).
    Override is LOGGED so a long smoke timeout is visible (a 4hr hang can't hide
    behind a silently-raised timeout). Use only for cells with verified fixed-
    setup costs that exceed 180s (e.g. bge AtomEncoder + 41k-atom index rebuild).
    """
    env = {**os.environ, **env_extra}
    timeout_s = SMOKE_TIMEOUT_S
    # CEILING (Skunkworks 2026-06-18 hardening reco; mirrors PROT-019/021 timeout-FLOOR
    # guards): cap the smoke override so a typo'd HDLAB_SMOKE_TIMEOUT_S can't run a
    # 10hr "smoke." 3600s = 1 hour, well above any legitimate heavy-fixed-setup
    # (bge+41k ~ 3-10 min), well below an abusive value.
    SMOKE_TIMEOUT_CEILING_S = 3600
    override_raw = os.environ.get("HDLAB_SMOKE_TIMEOUT_S")
    if override_raw:
        try:
            requested = int(override_raw)
            if requested > SMOKE_TIMEOUT_CEILING_S:
                print(
                    f"[gate] WARN: HDLAB_SMOKE_TIMEOUT_S={requested}s exceeds ceiling "
                    f"{SMOKE_TIMEOUT_CEILING_S}s; capping at ceiling",
                    file=sys.stderr,
                )
                timeout_s = SMOKE_TIMEOUT_CEILING_S
            else:
                timeout_s = requested
            print(
                f"[gate] SMOKE_TIMEOUT_S override via HDLAB_SMOKE_TIMEOUT_S: "
                f"using {timeout_s}s (default {SMOKE_TIMEOUT_S}s, ceiling "
                f"{SMOKE_TIMEOUT_CEILING_S}s)",
                file=sys.stderr,
            )
        except ValueError:
            print(
                f"[gate] WARN: HDLAB_SMOKE_TIMEOUT_S={override_raw!r} not an int; "
                f"using default {SMOKE_TIMEOUT_S}s",
                file=sys.stderr,
            )
    log_path = REPO / "data" / f"gate_log_{script.stem}_{flag.lstrip('-')}.txt"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    _no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0
    try:
        with log_path.open("w", encoding="utf-8") as logf:
            result = subprocess.run(
                [PYTHON, "-u", str(script), flag],
                cwd=str(REPO),
                env=env,
                stdout=logf,
                stderr=subprocess.STDOUT,
                timeout=timeout_s,
                creationflags=_no_window,
            )
    except subprocess.TimeoutExpired:
        return 124, f"TIMEOUT after {timeout_s}s (log: {log_path})"
    try:
        lines = log_path.read_text(encoding="utf-8").splitlines()
        tail = "\n".join(lines[-15:])
    except OSError:
        tail = f"(log unreadable at {log_path})"
    return result.returncode, tail


def validate_metrics(path: Path) -> str | None:
    if not path.exists():
        return f"missing at {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return f"invalid_json: {e}"
    if not isinstance(data, dict):
        return "not_an_object"
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return f"missing_fields: {missing}"
    if not data.get("verdict"):
        return "empty_verdict"
    if not data.get("verdict_msg"):
        return "empty_verdict_msg"
    return None


# PROT-019: large-N anchors require a generous timeout floor.
# Triggered after tcft_n8192_v5 hit the (then-)default 1800s and lost seed=41
# mid-run. Tiered floors (raised 2026-05-28) reflect actual observed FULL
# runtimes: 14400s for _n4096 multi-seed FULL, 21600s for _n>=8192 multi-seed
# FULL. A separate purpose-keyword warning catches multi-M-point batteries.
PROT019_LARGE_N_RE = re.compile(r'_n(\d+)(?:_|$)')
PROT019_LARGE_N_MIN = 4096
# Tiered floors: (min_N_inclusive, floor_s). Sorted descending by N.
PROT019_TIMEOUT_FLOOR_TIERS = [
    (8192, 21600),  # _n>=8192 -> >= 6h
    (4096, 14400),  # _n>=4096 -> >= 4h
]
# Multi-M-point / battery / sweep anchors should budget for multiple-GPU-day
# runtime; we WARN (not block) if purpose hints at this scope and timeout is
# below 86400s (24h). The c1_kf_battery_phase_v1_n4096 case (predicted 2-3
# GPU-days, shipped at 14400s = would have timed out at 4h) drove this rule.
PROT019_BATTERY_KEYWORDS = ("battery", "gpu-day", "gpu day", "sweep", "boundary curve")
PROT019_BATTERY_FLOOR_S = 86400


def _prot019_floor_for(entry_name: str) -> tuple[int | None, int | None]:
    """Return (suffix_n, required_floor_s) for this anchor, or (None, None).

    No-op return (None, None) when the anchor has no _n<N> suffix or N<min.
    """
    m = PROT019_LARGE_N_RE.search(entry_name)
    if not m:
        return None, None
    suffix_n = int(m.group(1))
    for tier_min, tier_floor in PROT019_TIMEOUT_FLOOR_TIERS:
        if suffix_n >= tier_min:
            return suffix_n, tier_floor
    return suffix_n, None


def check_timeout_floor(entry_name: str, timeout_s: int, purpose: str = "") -> None:
    """PROT-019: enforce tiered minimum timeout for large-N anchors.

    Tiers (raised 2026-05-28 after c1_kf_battery / c3_tcft_phase incidents):
      _n>=8192 multi-seed FULL -> --timeout >= 21600 (6h)
      _n>=4096 multi-seed FULL -> --timeout >= 14400 (4h)

    Also warns (does NOT block) when purpose contains battery/sweep keywords
    suggesting multi-M-point or GPU-day-scope work below an 86400s budget.

    Exits with code 7 on tier violation. Prints warning on purpose-mismatch.
    """
    suffix_n, floor_s = _prot019_floor_for(entry_name)
    if floor_s is None:
        if suffix_n is not None and suffix_n >= PROT019_LARGE_N_MIN:
            print(f"[gate] PROT-019 OK: _n{suffix_n} no tier (below 4096)")
        return
    if timeout_s < floor_s:
        print(
            f"\n[gate] PROT-019 REJECT: anchor '{entry_name}' contains _n{suffix_n} "
            f"(>= {PROT019_LARGE_N_MIN})\n"
            f"  but --timeout={timeout_s}s is below the PROT-019 tier floor "
            f"of {floor_s}s ({floor_s // 3600}h).\n"
            f"\n"
            f"  Background: tcft_n8192_v5 (2026-05-27) hit a 1800s timeout and\n"
            f"  lost seed=41 mid-run -- recorded metrics were a 4-of-5 partial,\n"
            f"  not the 5-seed HARD_PASS the anchor name promised. Tiers were\n"
            f"  raised 2026-05-28 after c1_kf_battery_phase_v1_n4096 (predicted\n"
            f"  2-3 GPU-days) was shipped at only 14400s (4h).\n"
            f"\n"
            f"  Fix options:\n"
            f"    1. Re-estimate timeout from smoke wall-clock:\n"
            f"         timeout_s = ceil(1.5 * smoke_wall_s\n"
            f"                          * (FULL_N/smoke_N)**scaling_exp\n"
            f"                          * (FULL_seeds/smoke_seeds))\n"
            f"       scaling_exp: 1.0-1.5 most sweeps, 2.0 matrix ops.\n"
            f"    2. If the script is genuinely fast, pass --timeout {floor_s}\n"
            f"       (the floor) explicitly.\n"
            f"\n"
            f"  Tiers (PROT-019 2026-05-28 raise):\n"
            f"    _n>=8192 -> --timeout >= 21600s\n"
            f"    _n>=4096 -> --timeout >= 14400s\n",
            file=sys.stderr,
        )
        sys.exit(7)
    print(
        f"[gate] PROT-019 OK: large-N anchor _n{suffix_n} with "
        f"timeout={timeout_s}s >= tier-floor {floor_s}s"
    )
    purpose_lc = (purpose or "").lower()
    battery_hit = next((kw for kw in PROT019_BATTERY_KEYWORDS if kw in purpose_lc), None)
    if battery_hit and timeout_s < PROT019_BATTERY_FLOOR_S:
        print(
            f"[gate] PROT-019 WARNING: purpose contains '{battery_hit}' suggesting "
            f"multi-M-point / GPU-day scope; --timeout={timeout_s}s is below the "
            f"recommended battery-floor of {PROT019_BATTERY_FLOOR_S}s (24h). Not "
            f"blocking -- but consider raising if the run is genuinely a battery.",
            file=sys.stderr,
        )


CHECKPOINT_IMPORT_RE = re.compile(
    # Recognize both bare (`from _seed_checkpoint import`) AND package-qualified
    # (`from experiments._seed_checkpoint import`) forms -- the canonical repo-root
    # import is `from experiments._seed_checkpoint import (...)`, which the old
    # bare-only pattern false-rejected (PROT-021 false-positive on a genuinely
    # checkpointed cell, 2026-06-19 q_b1). Optional `(?:[\w.]+\.)?` package prefix;
    # still rejects cells that truly do not import the helper. Strengthens detection,
    # does not weaken the safety floor.
    r'^\s*(?:from\s+(?:[\w.]+\.)?_seed_checkpoint\b|import\s+(?:[\w.]+\.)?_seed_checkpoint\b)',
    re.MULTILINE,
)
PROT021_TIMEOUT_THRESHOLD_S = 14400  # 4h — anchors at/above this floor must checkpoint


def check_long_timeout_has_checkpoint(
    entry_name: str,
    script_path: Path,
    timeout_s: int,
    allow_override: bool,
) -> None:
    """PROT-021: anchors with timeout >= 14400s must import _seed_checkpoint.

    Rationale: a script that takes 4+ hours and writes output only at the end
    discards 100% of compute on any kill / timeout / OOM. The _seed_checkpoint
    helper (experiments/_seed_checkpoint.py) is in-repo and supports any
    hashable key (per-seed, per-cell-seed, etc) via write_partial_key /
    list_completed_keys. The 2026-05-29 tcft_erase_robustness_n8192_v1
    incident wasted 4h of GPU runner time because the script had no checkpoint;
    after PROT-021, that ship is blocked at gate-time.

    Exits with code 9 if a long-timeout script doesn't import _seed_checkpoint.
    Override with --allow-no-checkpoint (rare; only for single-shot probes that
    genuinely can't be cell-decomposed).

    No-op for short-timeout anchors (< 14400s).
    """
    if timeout_s < PROT021_TIMEOUT_THRESHOLD_S:
        return
    try:
        source = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"[gate] PROT-021 WARN: could not read script for checkpoint-check: {e}",
              file=sys.stderr)
        return
    if CHECKPOINT_IMPORT_RE.search(source):
        print(f"[gate] PROT-021 OK: long-timeout anchor imports _seed_checkpoint")
        return
    if allow_override:
        print(f"[gate] PROT-021 WARN: long-timeout anchor lacks checkpoint "
              f"(override flag set)")
        return
    print(
        f"\n[gate] PROT-021 REJECT: anchor '{entry_name}' has --timeout={timeout_s}s\n"
        f"  (>= {PROT021_TIMEOUT_THRESHOLD_S}s = 4h) but script '{script_path.name}'\n"
        f"  does not import _seed_checkpoint.\n"
        f"\n"
        f"  A script that runs 4+ hours and writes output only at the end discards\n"
        f"  100% of compute on any kill / timeout / OOM. Real incident:\n"
        f"  tcft_erase_robustness_n8192_v1 wasted 4h on the GPU runner on\n"
        f"  2026-05-29 before being killed -- zero recoverable output.\n"
        f"\n"
        f"  Fix options:\n"
        f"    1. Wire the in-repo helper experiments/_seed_checkpoint.py into\n"
        f"       the script. Public API: resumable_seeds / write_partial /\n"
        f"       write_partial_key / aggregate_partials. See the helper's\n"
        f"       docstring for the adoption template. tcft_m_sweep_v3 and\n"
        f"       saad_solla_v15 are working examples.\n"
        f"    2. Pass --allow-no-checkpoint for single-shot probes that\n"
        f"       genuinely cannot be cell-decomposed (rare).\n",
        file=sys.stderr,
    )
    sys.exit(9)


def check_gpu_queue_uses_torch(queue_name: str, script_path: Path, allow_override: bool) -> None:
    """PROT-020: scripts queued to GPU queue (overnight_queue) must import torch.

    Rationale: the GPU runner slot is a finite resource. NumPy-only scripts
    occupy that slot but execute entirely on CPU, leaving the GPU idle for
    hours while genuinely GPU-accelerated work waits. Two real incidents:
      - tcft_m_sweep_v3_n8192_5seed (NumPy-only, ran on GPU runner 2026-05-28)
      - tcft_erase_robustness_n8192_v1 (NumPy-only, ran 4h on GPU runner
        2026-05-29 before user noticed near-zero GPU utilization)

    Exits with code 8 if a NumPy-only script targets overnight_queue.
    Override with --allow-numpy-on-gpu (rare; only when the script is
    explicitly using GPU-host-CPU for a reason that won't fit remote_cpu_queue).

    No-op for non-GPU queues (remote_cpu_queue, local_cpu_queue).
    """
    if queue_name != "overnight_queue":
        return
    try:
        source = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"[gate] PROT-020 WARN: could not read script for torch-check: {e}", file=sys.stderr)
        return
    uses_torch = bool(re.search(r'^\s*(?:import\s+torch\b|from\s+torch\b)', source, re.MULTILINE))
    if uses_torch:
        print("[gate] PROT-020 OK: script imports torch (GPU queue routing justified)")
        return
    if allow_override:
        print("[gate] PROT-020 WARN: NumPy-only script on GPU queue (override flag set)")
        return
    print(
        f"\n[gate] PROT-020 REJECT: queue='overnight_queue' but script '{script_path.name}'\n"
        f"  does not import torch — it is NumPy-only and cannot use the GPU.\n"
        f"\n"
        f"  Occupying the GPU runner slot with a CPU-bound script wastes hours of\n"
        f"  GPU access while torch+cuda anchors wait in the queue. Two prior\n"
        f"  incidents: tcft_m_sweep_v3_n8192_5seed and tcft_erase_robustness_n8192_v1\n"
        f"  (the latter ran 4h before the user noticed near-zero GPU utilization).\n"
        f"\n"
        f"  Fix options:\n"
        f"    1. Re-target the CPU queue:\n"
        f"         bash tools/orchestrator/queue_add.sh remote_cpu_queue ...\n"
        f"    2. Port the script to torch+cuda (preferred for matmul-heavy work).\n"
        f"    3. Pass --allow-numpy-on-gpu if you genuinely need the GPU host's\n"
        f"       CPU for a reason that doesn't fit remote_cpu_queue.\n",
        file=sys.stderr,
    )
    sys.exit(8)


PROT022_DECLARED_REFERENTS_RE = re.compile(
    r'^\s*#\s*KB_REFERENT\s*:\s*(\S+)\s*$',
    re.MULTILINE,
)
PROT022_REMOTE_HOST = "marsh@home"
PROT022_REMOTE_REPO = "C:/dev/hd-instrument"
PROT022_REMOTE_QUEUES = {"overnight_queue", "remote_cpu_queue"}


def check_declared_referents(
    script_path: Path,
    queue_name: str,
    allow_override: bool,
) -> None:
    """PROT-022: scripts must declare their data referents; gate verifies
    each declared path either (a) exists on the dispatch host, or (b) is
    overridden via --allow-missing-referent for cells whose first arm
    BUILDS the referent before use.

    Mechanism: a script that needs a specific data file declares a top-of-
    file comment:

        # KB_REFERENT: data/substrate_director_kb_v1/manifest.json
        # KB_REFERENT: data/exp_substrate_director_kb_ingest_v1/_arm_full/kb/manifest.json

    For LOCAL queues (local_cpu_queue), each referent must exist on the
    local filesystem.
    For REMOTE queues (overnight_queue, remote_cpu_queue), the gate runs
    `ssh marsh@home test -f <path>` for each referent and rejects on
    missing.

    Override: --allow-missing-referent (rare; only for cells whose first
    arm BUILDS the referent before use, such as the Tier-1
    substrate_director_kb_remote_provision cell).

    Exits with code 10 on violation.

    Rationale: three cells on 2026-06-27 wasted compute hitting
    KB_REFERENT_MISSING (anchor_1_v2 partition, anchor_5_dual_store,
    anchor_3_coarse_grain_v2). A 1-second SSH existence check at gate time
    catches the entire class. See
    notes/research_drill_kb_referent_missing_systemic_3x_2026-06-27.md
    Section "Concrete artifact 2".

    No-op for scripts without any KB_REFERENT declarations (gate is opt-in
    via declaration; existing cells without declarations are unaffected).
    """
    try:
        source = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"[gate] PROT-022 WARN: could not read script for referent-check: {e}",
              file=sys.stderr)
        return

    referents = PROT022_DECLARED_REFERENTS_RE.findall(source)
    if not referents:
        return  # opt-in: cells without declarations skip the gate

    print(f"[gate] PROT-022: script declares {len(referents)} KB referent(s)")

    is_remote = queue_name in PROT022_REMOTE_QUEUES
    missing: list[str] = []

    for ref in referents:
        if is_remote:
            remote_path = f"{PROT022_REMOTE_REPO}/{ref}"
            try:
                _no_window = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000) if sys.platform == "win32" else 0
                # ssh -T disables pseudo-tty (popup-fix per testbed 2026-06-28).
                rc = subprocess.run(
                    ["ssh", "-T", "-o", "ConnectTimeout=10", "-o", "BatchMode=yes",
                     PROT022_REMOTE_HOST, f"test -f \"{remote_path}\""],
                    timeout=15, capture_output=True,
                    creationflags=_no_window,
                ).returncode
                exists = (rc == 0)
            except subprocess.TimeoutExpired:
                print(f"[gate] PROT-022 WARN: ssh TIMEOUT checking {ref}; "
                      f"treating as MISSING", file=sys.stderr)
                exists = False
            except OSError as e:
                print(f"[gate] PROT-022 WARN: ssh error checking {ref}: {e}; "
                      f"treating as MISSING", file=sys.stderr)
                exists = False
        else:
            exists = (REPO / ref).exists()

        status = "OK" if exists else "MISSING"
        print(f"  PROT-022 {status} ({queue_name}): {ref}")
        if not exists:
            missing.append(ref)

    if not missing:
        print(f"[gate] PROT-022 OK: all {len(referents)} referent(s) resolved "
              f"on {'remote' if is_remote else 'local'} host")
        return

    if allow_override:
        print(f"[gate] PROT-022 WARN: {len(missing)} declared referent(s) "
              f"missing but --allow-missing-referent set; proceeding")
        return

    print(
        f"\n[gate] PROT-022 REJECT: {len(missing)} declared KB referent(s) "
        f"missing on {'remote' if is_remote else 'local'} host:\n"
        + "\n".join(f"    {m}" for m in missing) +
        f"\n\n  Three cells on 2026-06-27 (anchor_1_v2_partition, "
        f"anchor_5_dual_store, anchor_3_coarse_grain_v2) wasted GPU/CPU "
        f"compute hitting this exact failure mode. PROT-022 catches it at "
        f"the gate.\n"
        f"\n  Fix options:\n"
        f"    1. Build the referent on the target host (e.g. run "
        f"tools/sync_canonical_kb_to_remote.sh for the canonical KB).\n"
        f"    2. Make the cell self-contained (build its own KB IN-CELL like "
        f"exp_kb_partition_by_source_class_v3_self_contained does via "
        f"hdlab.director_kb_chunk_ingest.run_chunk_ingest).\n"
        f"    3. Pass --allow-missing-referent if the cell's first arm "
        f"BUILDS the referent before use.\n",
        file=sys.stderr,
    )
    sys.exit(10)


def check_n_suffix_binding(entry_name: str, script_path: Path) -> None:
    """PROT-018: if anchor name has _n<NUMBER>, the script's production N must match.

    Exits with code 6 on mismatch (anchor-name N mismatch).
    No-op if the anchor name contains no _n<NUMBER> suffix.
    """
    # Match the LAST _n<digits> token in the anchor name (e.g. wave14_foo_n4096 -> 4096).
    # Require word-boundary on the right (end-of-string or underscore) to avoid matching
    # _n inside words like 'next', 'noise', 'norm'.
    m = re.search(r'_n(\d+)(?:_|$)', entry_name)
    if not m:
        return  # no _n<N> suffix — rule does not apply

    suffix_n = int(m.group(1))
    print(f"[gate] PROT-018: anchor name contains _n{suffix_n}; verifying script production N...")

    try:
        source = script_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        print(f"[gate] PROT-018 WARN: could not read script for N-check: {e}", file=sys.stderr)
        return  # can't read script; let later checks catch it

    # Search for lines that assign the suffix-N to a variable whose name contains N or n.
    # Patterns matched:
    #   N = 4096
    #   N=4096
    #   n = 4096
    #   n=4096
    #   DIM_N = 4096      (any ALLCAPS word ending in N)
    #   default=4096      (argparse default)
    # We require the value to appear as an integer literal equal to suffix_n.
    # Version suffixes like _v3 don't contain _n<N>, so this pattern is safe.
    pattern = re.compile(
        r'(?:'
        r'\bN\s*=\s*' + str(suffix_n) + r'\b'
        r'|'
        r'\bn\s*=\s*' + str(suffix_n) + r'\b'
        r'|'
        r'\b[A-Z_]*N\s*=\s*' + str(suffix_n) + r'\b'
        r'|'
        r'default\s*=\s*' + str(suffix_n) + r'\b'
        r')'
    )
    match = pattern.search(source)
    if match:
        # Found a matching production-N assignment.
        # Make sure it is not ONLY inside a smoke/small-N guard block.
        # Heuristic: if the match line also contains "smoke" or "SMOKE", it is
        # the smoke config — that is not sufficient; we need it outside the guard.
        line_start = source.rfind('\n', 0, match.start()) + 1
        line_end = source.find('\n', match.end())
        matched_line = source[line_start:line_end].strip()
        # Accept if the matched line is NOT exclusively inside a comment or smoke block.
        # Simple check: the line must not be a pure comment line.
        if matched_line.lstrip().startswith('#'):
            # Match is commented out — keep searching.
            # Fall through to the REJECT path below.
            pass
        else:
            print(f"[gate] PROT-018 OK: found N={suffix_n} in script (line: {matched_line[:80]!r})")
            return

    # No match found (or only commented).
    print(
        f"\n[gate] PROT-018 REJECT: anchor name '{entry_name}' contains _n{suffix_n} suffix\n"
        f"  but script '{script_path}' has no production N={suffix_n} assignment.\n"
        f"\n"
        f"  Smoke running at a smaller N is expected — but the FULL queued config must\n"
        f"  set N = {suffix_n} (or n = {suffix_n}, argparse default={suffix_n}, etc.).\n"
        f"\n"
        f"  Fix options:\n"
        f"    1. Add/update the production config in the script:  N = {suffix_n}\n"
        f"    2. Rename the anchor to match the actual production N (e.g., drop the _n{suffix_n} suffix\n"
        f"       or change it to _n<actual_N>).\n"
        f"\n"
        f"  Per PROT-018 (2026-05-27): anchor-name _n<N> is a binding contract, not a label.\n",
        file=sys.stderr,
    )
    sys.exit(6)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("queue_name", help="Queue dir under data/ (e.g. overnight_queue)")
    ap.add_argument("entry_name", help="Name for the queue entry (also HDLAB_EXP_NAME)")
    ap.add_argument("script", help="Script path relative to repo root")
    ap.add_argument("--prereg", required=True, help="Path to prereg markdown (relative to repo)")
    ap.add_argument(
        "--timeout",
        type=int,
        required=True,
        help=(
            "Per-run timeout seconds. REQUIRED — no silent default. "
            "exp_dev must estimate this from smoke: "
            "timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N / smoke_N)**scaling_exp * (FULL_seeds / smoke_seeds)). "
            "Typical scaling_exp: 1.0-1.5 (most sweeps), 2.0 (matrix ops). "
            "If estimate > 14400 (4 h), exp_dev must justify in the prereq."
        ),
    )
    ap.add_argument("--purpose", default="", help="One-line purpose string for the queue entry")
    ap.add_argument("--skip-smoke", action="store_true",
                    help="Skip smoke run (use only when previously smoke-tested)")
    ap.add_argument(
        "--rerun-as",
        metavar="NEW_NAME",
        default=None,
        help=(
            "Clone the entry under NEW_NAME (inherits script+prereg) and queue it as pending. "
            "Bypasses dedup: the original entry is untouched. "
            "Use when Strategy explicitly wants to re-run a previously-queued experiment. "
            "If NEW_NAME is the same as entry_name, a date suffix is appended automatically."
        ),
    )
    ap.add_argument(
        "--allow-duplicate",
        action="store_true",
        help=(
            "If entry_name already exists with status in {done, failed, completed, canceled, killed}, "
            "reset it to pending in-place (clears started_at, increments run_index). "
            "Refuses if status is 'running' or 'pending' (use --rerun-as for those)."
        ),
    )
    ap.add_argument(
        "--allow-numpy-on-gpu",
        action="store_true",
        help=(
            "Override PROT-020: allow a NumPy-only script on overnight_queue (the GPU queue). "
            "Rare; only when the script genuinely needs the GPU host's CPU for a reason that "
            "doesn't fit remote_cpu_queue."
        ),
    )
    ap.add_argument(
        "--allow-no-checkpoint",
        action="store_true",
        help=(
            "Override PROT-021: allow a long-timeout (>=14400s) script without "
            "_seed_checkpoint. Rare; only for single-shot probes that genuinely "
            "cannot be cell-decomposed."
        ),
    )
    ap.add_argument(
        "--allow-missing-referent",
        action="store_true",
        help=(
            "Override PROT-022: allow declared `# KB_REFERENT:` paths that do "
            "not exist on the dispatch host. Rare; only for cells whose first "
            "arm BUILDS the referent before use (e.g. provisioning cells)."
        ),
    )
    args = ap.parse_args()

    # ── Host guard ──────────────────────────────────────────────────────────────
    # Remote queues (overnight_queue, remote_cpu_queue) are owned by the remote
    # runner on marsh@home. Writing to their queue.json from the local Windows
    # box only mutates the LOCAL data/<queue>/queue.json — the remote runner
    # never sees the entry. This caused 5 anchors to silently fail to ship on
    # 2026-05-24.
    #
    # Structural fix: refuse remote-queue invocations unless the env marker
    # HDLAB_QUEUE_ADD_ON_REMOTE=1 is set. queue_add.sh sets this when SSH'ing
    # into the remote host before invoking queue_add.py, so the legitimate
    # remote-side call still works. Direct local invocation now fails loud.
    REMOTE_QUEUES = {"overnight_queue", "remote_cpu_queue"}
    if args.queue_name in REMOTE_QUEUES and os.environ.get("HDLAB_QUEUE_ADD_ON_REMOTE") != "1":
        fail(
            f"queue '{args.queue_name}' is a REMOTE queue and must be added via "
            f"`bash tools/orchestrator/queue_add.sh {args.queue_name} ...` (which "
            f"SCPs the script and SSHs into marsh@home). Direct local invocation "
            f"of queue_add.py only writes the LOCAL data/{args.queue_name}/queue.json "
            f"and the remote runner never sees the entry. If you ARE running this on "
            f"the remote host, set HDLAB_QUEUE_ADD_ON_REMOTE=1."
        )

    print(f"[gate] entry_name={args.entry_name}")
    print(f"[gate] script={args.script}")
    print(f"[gate] prereg={args.prereg}")

    # 1. Script exists
    script_path = check_script_exists(args.script)
    print(f"[gate] OK: script exists at {script_path}")

    # 1b. PROT-018: anchor-name N-suffix binding check (exit 6 on mismatch)
    check_n_suffix_binding(args.entry_name, script_path)

    # 1c. PROT-019: timeout floor for large-N anchors (exit 7 on violation).
    # Pass purpose so the battery/sweep WARNING can fire on multi-M-point work.
    check_timeout_floor(args.entry_name, args.timeout, getattr(args, "purpose", "") or "")

    # 1d. PROT-020: GPU-queue routing audit — NumPy-only scripts cannot use the
    # GPU and waste the runner slot. Exit 8 on violation; --allow-numpy-on-gpu
    # overrides.
    check_gpu_queue_uses_torch(args.queue_name, script_path, args.allow_numpy_on_gpu)

    # 1e. PROT-021: long-timeout anchors must import _seed_checkpoint so a kill
    # / timeout / OOM doesn't discard hours of compute. Exit 9 on violation;
    # --allow-no-checkpoint overrides.
    check_long_timeout_has_checkpoint(
        args.entry_name, script_path, args.timeout, args.allow_no_checkpoint
    )

    # 1f. PROT-022: declared `# KB_REFERENT:` paths must resolve on the dispatch
    # host. Exit 10 on violation; --allow-missing-referent overrides for cells
    # whose first arm BUILDS the referent. Opt-in via in-script declaration.
    check_declared_referents(
        script_path, args.queue_name, args.allow_missing_referent
    )

    # 2. Prereg exists
    prereg_path = REPO / args.prereg
    if not prereg_path.exists():
        fail(f"prereg not found: {prereg_path}")
    print(f"[gate] OK: prereg exists at {prereg_path}")

    # 3. Self-test passes
    # 2026-06-30 fix: selftest HDLAB_EXP_NAME must include _selftest suffix to isolate
    # output dir from FULL run path. Without this, selftest writes metrics.json to the
    # SAME path FULL would use (data/exp_<entry_name>/metrics.json), polluting the FULL
    # output dir with run_mode=smoke + _phase=selftest_done. Caught 6+ phantom-FULL
    # recurrences this session (META_RULE_AV signature). Mirrors smoke pattern at line
    # below where smoke_name = f"{args.entry_name}_smoke". META_RULE_BB candidate.
    selftest_name = f"{args.entry_name}_selftest"
    print(f"[gate] running --self-test under HDLAB_EXP_NAME={selftest_name}...")
    t0 = time.monotonic()
    rc, tail = run_with_flag(script_path, "--self-test",
                             env_extra={"HDLAB_EXP_NAME": selftest_name})
    if rc != 0:
        print(tail, file=sys.stderr)
        fail(f"--self-test exit={rc} (after {time.monotonic()-t0:.1f}s)")
    print(f"[gate] OK: --self-test passed in {time.monotonic()-t0:.1f}s")

    # 4. Smoke passes + valid metrics
    if not args.skip_smoke:
        print(f"[gate] running --smoke under HDLAB_EXP_NAME={args.entry_name}_smoke...")
        smoke_name = f"{args.entry_name}_smoke"
        t0 = time.monotonic()
        rc, tail = run_with_flag(script_path, "--smoke",
                                 env_extra={"HDLAB_EXP_NAME": smoke_name})
        if rc != 0:
            print(tail, file=sys.stderr)
            fail(f"--smoke exit={rc} (after {time.monotonic()-t0:.1f}s)")
        smoke_metrics = REPO / "data" / f"exp_{smoke_name}" / "metrics.json"
        err = validate_metrics(smoke_metrics)
        if err:
            fail(f"smoke metrics invalid: {err}")
        print(f"[gate] OK: --smoke produced valid metrics in {time.monotonic()-t0:.1f}s")

    # Validate flag combinations
    if args.rerun_as and args.allow_duplicate:
        fail("--rerun-as and --allow-duplicate are mutually exclusive; pick one")

    # 5. Add to queue
    queue_dir = REPO / "data" / args.queue_name
    queue_dir.mkdir(parents=True, exist_ok=True)
    queue_file = queue_dir / "queue.json"

    # Resolve the actual name that will be registered in the queue.
    # For --rerun-as: the new name is the target; for all other cases it's entry_name.
    if args.rerun_as:
        register_name = args.rerun_as
        # If caller passed the same name as entry_name, auto-suffix with today's date.
        if register_name == args.entry_name:
            register_name = f"{args.entry_name}_rerun_{time.strftime('%Y-%m-%d')}"
            print(f"[gate] --rerun-as same as entry_name; auto-suffixed to {register_name}")
    else:
        register_name = args.entry_name

    entry = {
        "name": register_name,
        "script": args.script,
        "status": "pending",
        "purpose": args.purpose or f"See {args.prereg}",
        "prereg": args.prereg,
        "timeout_s": args.timeout,
        "gated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    # Terminal statuses that --allow-duplicate can reset.
    _TERMINAL = {"done", "failed", "completed", "canceled", "killed"}

    with QueueLock(queue_file, max_wait_s=10.0) as lock:
        if queue_file.exists():
            q = lock.read()
        else:
            q = {"experiments": []}

        existing_map = {e["name"]: e for e in q["experiments"]}

        if args.allow_duplicate:
            # --allow-duplicate: reset an existing terminal entry in-place.
            if args.entry_name in existing_map:
                ex = existing_map[args.entry_name]
                cur_status = ex.get("status", "")
                if cur_status in ("running", "pending"):
                    fail(
                        f"--allow-duplicate refused: {args.entry_name} is currently "
                        f"'{cur_status}'. Use --rerun-as to queue a parallel copy."
                    )
                if cur_status not in _TERMINAL:
                    fail(
                        f"--allow-duplicate refused: {args.entry_name} has unrecognised "
                        f"status '{cur_status}'. Inspect queue.json manually."
                    )
                run_index = ex.get("run_index", 1) + 1
                ex.update({
                    "status": "pending",
                    "purpose": args.purpose or ex.get("purpose", f"See {args.prereg}"),
                    "prereg": args.prereg,
                    "timeout_s": args.timeout,
                    "gated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "run_index": run_index,
                    # Clear previous-run timestamps.
                    "started_at": None,
                    "finished_at": None,
                    "claimed_by": None,
                })
                lock.write(q)
                print(f"[gate] OK: reset {args.entry_name} to pending (run_index={run_index})")
            else:
                # Name not in queue yet; just add fresh (--allow-duplicate is harmless here).
                q["experiments"].append(entry)
                lock.write(q)
                print(f"[gate] OK: queued {register_name} (new entry; --allow-duplicate was no-op)")

        elif args.rerun_as:
            # --rerun-as: always append under register_name (already de-collided above).
            if register_name in existing_map:
                fail(
                    f"--rerun-as target '{register_name}' already exists in queue. "
                    f"Choose a different name or use --allow-duplicate on that name."
                )
            q["experiments"].append(entry)
            lock.write(q)
            print(f"[gate] OK: queued clone '{register_name}' (original '{args.entry_name}' untouched)")

        else:
            # Default: dedup by name (original behaviour).
            if args.entry_name in existing_map:
                print(
                    f"[gate] WARN: {args.entry_name} already in queue; not adding duplicate. "
                    f"Use --rerun-as <new_name> or --allow-duplicate to override."
                )
            else:
                q["experiments"].append(entry)
                lock.write(q)
                print(f"[gate] OK: queued {register_name}")

        pending = [e["name"] for e in q["experiments"] if e["status"] == "pending"]
    print(f"[gate] queue pending now ({len(pending)}): {pending}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
