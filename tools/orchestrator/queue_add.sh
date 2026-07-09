#!/usr/bin/env bash
# tools/orchestrator/queue_add.sh
#
# Multi-queue dispatcher.  Routes an experiment to the correct runner queue.
#
# Usage:
#   bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout_s> [extra_flags...]
#
# Args (positional; first 5 required):
#   queue       overnight_queue | remote_cpu_queue | local_cpu_queue
#   name        queue entry name (also HDLAB_EXP_NAME on the runner)
#   script      script path relative to repo root (e.g. experiments/exp_X.py)
#   prereg      prereg path relative to repo root (e.g. preregs/2026-05-23_X.md)
#   timeout_s   per-run timeout in seconds. REQUIRED; compute from smoke:
#               ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))
#               scaling_exp=1.0 linear, 1.5 vector sweeps, 2.0 matrix ops. Cap at 14400 or justify.
#
# Optional extra flags (passed through verbatim to queue_add.py):
#   --rerun-as <new_name>   Queue clone under new_name; original entry untouched.
#   --allow-duplicate       Reset a terminal (done/failed/completed/canceled/killed) entry to pending.
#   --skip-smoke            Skip the smoke run.
#
# Queue routing:
#   overnight_queue   -> SCP + SSH to marsh@home; runs queue_add.py there targeting overnight_queue
#   remote_cpu_queue  -> SCP + SSH to marsh@home; runs queue_add.py there targeting remote_cpu_queue
#   local_cpu_queue   -> direct local queue_add.py call (no SCP; script already in local repo)
#
# Exits 0 on success, non-zero on failure.  All output goes to stdout/stderr.

set -euo pipefail

if [[ $# -lt 5 ]]; then
  echo "usage: $0 <queue> <name> <script_rel_path> <prereg_rel_path> <timeout_s> [extra_flags...]" >&2
  exit 2
fi

QUEUE="$1"
NAME="$2"
SCRIPT_REL="$3"
PREREG_REL="$4"
TIMEOUT_S="$5"
shift 5
# Any remaining args are passed through to queue_add.py (e.g. --rerun-as, --allow-duplicate).
EXTRA_FLAGS=("$@")

REPO_LOCAL="$(cd "$(dirname "$0")/../.." && pwd)"
REPO_REMOTE="C:/dev/hd-instrument"
SSH_TARGET="marsh@home"

echo "[queue-add] queue=${QUEUE} name=${NAME}"

# Ship-attempt sentinel (audit rec #2 / Condition 2). Heartbeat watchdog reads
# this to detect ships that "succeeded locally" but never landed in remote
# queue.json (silent SSH/SCP failures). Written ON SUCCESSFUL EXIT below.
SHIP_SENTINEL="${REPO_LOCAL}/data/recent_ship_attempts.jsonl"
record_ship_attempt() {
  local now
  now="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  mkdir -p "$(dirname "${SHIP_SENTINEL}")"
  # JSONL line; single-line, no embedded newlines. Atomic append is fine on
  # local FS; torn writes are tolerated by the watchdog parser.
  printf '{"ts":"%s","queue":"%s","name":"%s","attempted_at":"%s"}\n' \
    "${now}" "${QUEUE}" "${NAME}" "${now}" >> "${SHIP_SENTINEL}"
}

if [[ "${QUEUE}" == "local_cpu_queue" ]]; then
  # ── Local CPU path ──────────────────────────────────────────────────────────
  # Script and prereg are already in the local repo; no SCP needed.
  SCRIPT_LOCAL="${REPO_LOCAL}/${SCRIPT_REL}"
  PREREG_LOCAL="${REPO_LOCAL}/${PREREG_REL}"

  if [[ ! -f "${SCRIPT_LOCAL}" ]]; then
    echo "FAIL: script not found at ${SCRIPT_LOCAL}" >&2
    exit 3
  fi
  if [[ ! -f "${PREREG_LOCAL}" ]]; then
    echo "FAIL: prereg not found at ${PREREG_LOCAL}" >&2
    exit 3
  fi

  echo "[queue-add] local path: ${SCRIPT_LOCAL}"
  echo "[queue-add] running local queue_add.py for local_cpu_queue"
  QUEUE_ADD_OUTPUT=$(python "${REPO_LOCAL}/tools/queue_add.py" \
    local_cpu_queue \
    "${NAME}" \
    "${SCRIPT_REL}" \
    --prereg "${PREREG_REL}" \
    --timeout "${TIMEOUT_S}" \
    --skip-smoke \
    "${EXTRA_FLAGS[@]}" 2>&1)
  echo "${QUEUE_ADD_OUTPUT}"

  # Only record ship attempt if queue_add.py actually added the entry (not a dedup reject).
  # A dedup-rejected ship prints "WARN: ... already in queue" and exits 0 but does NOT
  # add the entry. Recording it as a ship_attempt would cause watchdog ship_unconfirmed
  # false positives (the entry is "completed" in queue.json, not newly pending).
  if echo "${QUEUE_ADD_OUTPUT}" | grep -qF "already in queue"; then
    echo "[queue-add] SKIP ship_attempt sentinel: duplicate rejected by queue_add.py"
  else
    record_ship_attempt
  fi
  echo "[queue-add] OK: ${NAME} queued to local_cpu_queue"

elif [[ "${QUEUE}" == "overnight_queue" || "${QUEUE}" == "remote_cpu_queue" ]]; then
  # ── Remote path (GPU or remote-CPU runner on marsh@home) ────────────────────
  SCRIPT_LOCAL="${REPO_LOCAL}/${SCRIPT_REL}"
  PREREG_LOCAL="${REPO_LOCAL}/${PREREG_REL}"

  if [[ ! -f "${SCRIPT_LOCAL}" ]]; then
    echo "FAIL: script not found at ${SCRIPT_LOCAL}" >&2
    exit 3
  fi
  if [[ ! -f "${PREREG_LOCAL}" ]]; then
    echo "FAIL: prereg not found at ${PREREG_LOCAL}" >&2
    exit 3
  fi

  # ── ROUTING-SANITY GATE (anti-mis-route; added 2026-06-04 after q_f5 + mini_lm incidents) ──
  # (a) numpy/no-torch script on the GPU runner idles the GPU + blocks real GPU jobs (q_f5 incident) -> REJECT.
  # (b) numpy + large-N (>=16384) on CPU risks intractable per-element Python-loop runs (mini_lm v1) -> WARN.
  if grep -qE '^[[:space:]]*(import torch|from torch)' "${SCRIPT_LOCAL}"; then HAS_TORCH=1; else HAS_TORCH=0; fi
  # large-N only when the literal is INSIDE a grid list bracket (N_GRID = [...16384...]) or a bare N_DIM
  # assignment -- excludes docstring prose AND trailing comments like "# 16384 dropped" after the bracket.
  if grep -qE '(N_GRID|N_grid)[[:space:]]*=[[:space:]]*\[[^]]*(16384|32768|65536|131072)|(N_DIM|N_dim)[[:space:]]*=[[:space:]]*(16384|32768|65536|131072)' "${SCRIPT_LOCAL}"; then HAS_LARGE_N=1; else HAS_LARGE_N=0; fi
  if [[ "${QUEUE}" == "overnight_queue" && "${HAS_TORCH}" == "0" ]]; then
    echo "[gate] ROUTING-REJECT: overnight_queue (GPU runner) but script has no 'import torch' -- a numpy/CPU" >&2
    echo "       script on the GPU runner idles the GPU and blocks real GPU jobs (q_f5 incident, 2026-06-04)." >&2
    echo "       Fix: route to remote_cpu_queue, OR make it torch+cuda. Refusing to queue." >&2
    exit 7
  fi
  if [[ "${QUEUE}" == "remote_cpu_queue" && "${HAS_TORCH}" == "0" && "${HAS_LARGE_N}" == "1" ]]; then
    echo "[gate] ROUTING-WARN: remote_cpu_queue + numpy (no torch) + large-N literal (>=16384) -- risk of an" >&2
    echo "       intractable per-element Python-loop run (mini_lm v1 incident: killed after ~2h, nothing saved)." >&2
    echo "       VERIFY: realistic wall estimate + PER-CELL checkpointing before relying on this. Proceeding." >&2
  fi

  SCRIPT_REMOTE_DIR="${REPO_REMOTE}/$(dirname "${SCRIPT_REL}")"
  PREREG_REMOTE_DIR="${REPO_REMOTE}/$(dirname "${PREREG_REL}")"

  echo "[queue-add] SCP script -> ${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
  scp -o ConnectTimeout=10 "${SCRIPT_LOCAL}" "${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
  echo "[queue-add] SCP prereg -> ${SSH_TARGET}:${PREREG_REMOTE_DIR}/"
  scp -o ConnectTimeout=10 "${PREREG_LOCAL}" "${SSH_TARGET}:${PREREG_REMOTE_DIR}/"

  # Auto-detect + SCP sibling helpers (4th recurrence fix; 2026-06-30).
  # Cell convention: exp_<base>_seed_<N>.py wrappers exec exp_<base>.py core +
  # may use _<base>_core.py / _<base>_base.py helpers in same experiments/ dir.
  # SCP'ing only the wrapper without sibling helpers = remote ImportError / exec
  # FileNotFoundError. Caught 4x this session (Schema v4 / multihop v5 / WM enc /
  # Lock-in v4 + TOM v5). Fix: detect convention + auto-SCP siblings if present.
  # 2026-07-03: broadened suffix regex to also match newer _s<N> convention
  # (e.g. _s11/_s17/_s23 M-sweep cells). Prior regex matched only _seed_<N>,
  # so _s<N> wrappers were treated as non-seed cells and shared cores were not
  # auto-SCPed -> remote ModuleNotFoundError (orchestrator workaround 2026-07-03).
  SCRIPT_BASE=$(basename "${SCRIPT_LOCAL}" .py)
  SCRIPT_DIR_LOCAL=$(dirname "${SCRIPT_LOCAL}")
  # Tracks basenames (no .py) already SCP'ed by Patterns 1-5 so Pattern 6's
  # generic import-parse pass below doesn't re-announce/re-scp the same file.
  SHIPPED_SIBLINGS=()
  if [[ "${SCRIPT_BASE}" =~ (_seed_[0-9]+|_s[0-9]+)$ ]]; then
    CORE_BASE=$(echo "${SCRIPT_BASE}" | sed -E 's/(_seed_[0-9]+|_s[0-9]+)$//')
    # Pattern 1: exp_<base>.py (core file with same prefix as wrappers; ships with v4/v5 cells)
    CORE_LOCAL="${SCRIPT_DIR_LOCAL}/${CORE_BASE}.py"
    if [[ -f "${CORE_LOCAL}" ]]; then
      echo "[queue-add] AUTO-SCP core sibling -> ${CORE_LOCAL}"
      scp -o ConnectTimeout=10 "${CORE_LOCAL}" "${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
      SHIPPED_SIBLINGS+=("${CORE_BASE}")
    fi
    # Pattern 2: _<base>_core.py (helper module convention; older cells)
    CORE_HELPER="${SCRIPT_DIR_LOCAL}/_${CORE_BASE}_core.py"
    if [[ -f "${CORE_HELPER}" ]]; then
      echo "[queue-add] AUTO-SCP _core helper -> ${CORE_HELPER}"
      scp -o ConnectTimeout=10 "${CORE_HELPER}" "${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
      SHIPPED_SIBLINGS+=("_${CORE_BASE}_core")
    fi
    # Pattern 3: _<base>_base.py (alternative helper convention)
    BASE_HELPER="${SCRIPT_DIR_LOCAL}/_${CORE_BASE}_base.py"
    if [[ -f "${BASE_HELPER}" ]]; then
      echo "[queue-add] AUTO-SCP _base helper -> ${BASE_HELPER}"
      scp -o ConnectTimeout=10 "${BASE_HELPER}" "${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
      SHIPPED_SIBLINGS+=("_${CORE_BASE}_base")
    fi
    # Pattern 4: strip leading exp_ from base when looking up helpers (5th recurrence fix; 2026-06-30).
    # Convention seen in cleanup_family_wm_kcliff_v1: wrapper exp_substrate_X_seed_N.py imports
    # _substrate_X_core (no exp_ prefix on helper). Try the stripped-exp_ variant of patterns 2+3.
    if [[ "${CORE_BASE}" =~ ^exp_(.+)$ ]]; then
      STRIPPED_BASE="${BASH_REMATCH[1]}"
      CORE_HELPER_STRIPPED="${SCRIPT_DIR_LOCAL}/_${STRIPPED_BASE}_core.py"
      if [[ -f "${CORE_HELPER_STRIPPED}" ]]; then
        echo "[queue-add] AUTO-SCP _core helper (exp_-stripped) -> ${CORE_HELPER_STRIPPED}"
        scp -o ConnectTimeout=10 "${CORE_HELPER_STRIPPED}" "${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
        SHIPPED_SIBLINGS+=("_${STRIPPED_BASE}_core")
      fi
      BASE_HELPER_STRIPPED="${SCRIPT_DIR_LOCAL}/_${STRIPPED_BASE}_base.py"
      if [[ -f "${BASE_HELPER_STRIPPED}" ]]; then
        echo "[queue-add] AUTO-SCP _base helper (exp_-stripped) -> ${BASE_HELPER_STRIPPED}"
        scp -o ConnectTimeout=10 "${BASE_HELPER_STRIPPED}" "${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
        SHIPPED_SIBLINGS+=("_${STRIPPED_BASE}_base")
      fi
    fi
  fi

  # Pattern 5: shared framework modules that ANY cell may import (SH-2 fix; 2026-07-01).
  # Cells commonly import cross-cutting helpers like `from experiments._cell_heartbeat`,
  # `from experiments._seed_checkpoint`, `from experiments._multi_hop_mechanisms`, etc.
  # Patterns 1-4 only match sibling wrappers/helpers by name convention; they miss
  # these shared modules. Fix: hardcoded allow-list of shared framework modules; if
  # the local script imports any of them, scp explicitly. Surfaced 2026-07-01 03:00 UTC
  # when seqbind N-scaling silently failed on remote (import worked locally but the
  # module was never SCPed).
  #
  # NOTE: kept intentionally SHORT — only true cross-cell shared framework modules
  # that CI/dispatch has repeatedly missed. Cell-specific `_core`/`_base` are handled
  # by patterns 1-4. Do NOT expand into a general-purpose transitive dep resolver
  # (that's a rabbit hole; stick to the known-recurrence set).
  SHARED_FRAMEWORK_MODULES=(
    "_cell_heartbeat"
    "_seed_checkpoint"
    "_multi_hop_mechanisms"
    "_metric_battery"
    "_relation_graph"
    "_gpu_cap"
    "_stream"
    "_cell_provenance"
    "_bit_precision"
    "_atomic_write"
    "_common_gates"
  )
  for MODULE in "${SHARED_FRAMEWORK_MODULES[@]}"; do
    # grep for either `from experiments._MODULE ` or `import experiments._MODULE` in the local script
    if grep -qE "(from experiments\.${MODULE}[[:space:]]|import experiments\.${MODULE})" "${SCRIPT_LOCAL}"; then
      SHARED_LOCAL="${REPO_LOCAL}/experiments/${MODULE}.py"
      if [[ -f "${SHARED_LOCAL}" ]]; then
        # Ship shared framework modules to REPO_REMOTE/experiments/ (the actual import
        # target), NOT SCRIPT_REMOTE_DIR (which is the wrapper's own dir). If they're
        # the same dir (script is in experiments/), this is idempotent; if the script
        # lives elsewhere, this places the module where python's import resolves it.
        SHARED_REMOTE_DIR="${REPO_REMOTE}/experiments"
        echo "[queue-add] AUTO-SCP shared framework module (Pattern 5) -> ${SHARED_LOCAL} -> ${SHARED_REMOTE_DIR}/"
        scp -o ConnectTimeout=10 "${SHARED_LOCAL}" "${SSH_TARGET}:${SHARED_REMOTE_DIR}/"
        SHIPPED_SIBLINGS+=("${MODULE}")
      else
        echo "[queue-add] WARN: script imports experiments.${MODULE} but ${SHARED_LOCAL} not found locally" >&2
      fi
    fi
  done

  # Pattern 5b: shared framework modules in the hdlab/ PACKAGE (added 2026-07-08).
  # Pattern 5 only matches `from experiments.<mod>`; it misses `from hdlab.<mod>`
  # package imports. The remote runner repo (C:/dev/hd-instrument) is not kept in
  # lock-step with origin (known repo drift), so an hdlab/ module that gained a new
  # symbol locally (e.g. hdlab.cleanup_family.peel_sic_readout) is stale on remote
  # and the self-test crashes with ImportError. Surfaced 2026-07-08 when
  # community_bounded_retrieval_scale_invariance_v1 self-test HARD_FAILed on
  # `cannot import name 'peel_sic_readout' from 'hdlab.cleanup_family'`.
  # Fix: hardcoded allow-list of shared hdlab package modules; if the local script
  # imports one, scp it to REPO_REMOTE/hdlab/. Kept SHORT (same discipline as
  # Pattern 5): only true cross-cell shared hdlab modules, not a general dep resolver.
  HDLAB_SHARED_MODULES=(
    "cleanup_family"
  )
  for HMODULE in "${HDLAB_SHARED_MODULES[@]}"; do
    if grep -qE "(from hdlab\.${HMODULE}[[:space:]]|import hdlab\.${HMODULE})" "${SCRIPT_LOCAL}"; then
      HDLAB_LOCAL="${REPO_LOCAL}/hdlab/${HMODULE}.py"
      if [[ -f "${HDLAB_LOCAL}" ]]; then
        HDLAB_REMOTE_DIR="${REPO_REMOTE}/hdlab"
        echo "[queue-add] AUTO-SCP shared hdlab module (Pattern 5b) -> ${HDLAB_LOCAL} -> ${HDLAB_REMOTE_DIR}/"
        scp -o ConnectTimeout=10 "${HDLAB_LOCAL}" "${SSH_TARGET}:${HDLAB_REMOTE_DIR}/"
      else
        echo "[queue-add] WARN: script imports hdlab.${HMODULE} but ${HDLAB_LOCAL} not found locally" >&2
      fi
    fi
  done

  # Pattern 6: generic import-parse fallback (6th recurrence fix; 2026-07-04).
  # Patterns 1-5 all match siblings by NAME CONVENTION (suffix-strip + fixed
  # filename shapes, or a hardcoded allow-list). That still misses cells like
  # exp_encoder_v3e_decline_vs_plateau_v1_seed_7.py -> its core is
  # exp_encoder_v3e_decline_vs_plateau_v1_core.py (no leading underscore --
  # Pattern 1 wants "{CORE_BASE}.py" with no _core suffix, Pattern 2 wants a
  # LEADING-underscore "_{CORE_BASE}_core.py") and
  # exp_encoder_migration_step1b_v3c_paired_rkd_only_seed_13.py, whose core is
  # exp_encoder_migration_step1b_v3c_full_paired_rkd_only_dense_recovery_v1_core.py
  # -- a name that does not derive from the wrapper name by ANY suffix rule.
  # Both were manually scp'd this session (exp_dev flagged the gap).
  #
  # Fix: actually parse the wrapper's `from experiments import <mod>` / `import
  # experiments.<mod>` statements via Python `ast` (tools/orchestrator/
  # extract_sibling_imports.py) and auto-SCP whatever local experiments/*.py
  # sibling it names, regardless of naming convention. This generalizes past
  # Patterns 1-5's fixed shapes and closes the class, not just this instance.
  # Best-effort: helper never blocks the ship (parse errors -> empty output).
  SIBLING_IMPORT_HELPER="${REPO_LOCAL}/tools/orchestrator/extract_sibling_imports.py"
  if [[ -f "${SIBLING_IMPORT_HELPER}" ]]; then
    already_shipped() {
      local needle="$1" hay
      for hay in "${SHIPPED_SIBLINGS[@]:-}"; do
        [[ "${hay}" == "${needle}" ]] && return 0
      done
      return 1
    }
    while IFS= read -r SIB_BASE; do
      # Strip a trailing CR: native Windows python.exe emits CRLF line endings
      # even when invoked from git-bash, and bare `read -r` only strips \n --
      # left in, the \r corrupts both the -f existence check below and the
      # already_shipped string compare (caught via dry-run harness before commit).
      SIB_BASE="${SIB_BASE%$'\r'}"
      [[ -z "${SIB_BASE}" ]] && continue
      if already_shipped "${SIB_BASE}"; then
        continue
      fi
      SIB_LOCAL="${SCRIPT_DIR_LOCAL}/${SIB_BASE}.py"
      if [[ -f "${SIB_LOCAL}" ]]; then
        echo "[queue-add] AUTO-SCP import-parsed sibling (Pattern 6) -> ${SIB_LOCAL}"
        scp -o ConnectTimeout=10 "${SIB_LOCAL}" "${SSH_TARGET}:${SCRIPT_REMOTE_DIR}/"
        SHIPPED_SIBLINGS+=("${SIB_BASE}")
      fi
    done < <(python "${SIBLING_IMPORT_HELPER}" "${SCRIPT_LOCAL}" 2>/dev/null || true)
  fi

  # SSH+PowerShell payload. Single-quote bash outer per [[feedback-ssh-powershell-quoting]].
  # Extra flags (e.g. --rerun-as, --allow-duplicate) are appended verbatim.
  # HDLAB_QUEUE_ADD_ON_REMOTE=1 satisfies the host-guard in queue_add.py that
  # refuses direct local writes to remote-queue queue.json files.
  EXTRA_FLAGS_STR="${EXTRA_FLAGS[*]:-}"
  PS_PAYLOAD="cd ${REPO_REMOTE}; \$env:HDLAB_QUEUE_ADD_ON_REMOTE='1'; .\\.venv\\Scripts\\python.exe tools/queue_add.py ${QUEUE} ${NAME} ${SCRIPT_REL} --prereg ${PREREG_REL} --timeout ${TIMEOUT_S} --skip-smoke ${EXTRA_FLAGS_STR}"

  echo "[queue-add] SSH queue_add -> ${SSH_TARGET} (${QUEUE})"
  echo "[queue-add] payload: ${PS_PAYLOAD}"
  ssh -o ConnectTimeout=10 "${SSH_TARGET}" "powershell -Command \"${PS_PAYLOAD}\""

  # Post-ship verification: confirm entry actually landed in REMOTE queue.json.
  # Catches scp/ssh silent failures and proves the entry is reachable by the runner.
  VERIFY_PS="Get-Content ${REPO_REMOTE}/data/${QUEUE}/queue.json | ConvertFrom-Json | Select-Object -ExpandProperty experiments | Where-Object { \$_.name -eq '${NAME}' } | Select-Object -ExpandProperty name"
  REMOTE_HIT=$(ssh -o ConnectTimeout=10 "${SSH_TARGET}" "powershell -Command \"${VERIFY_PS}\"" 2>/dev/null | tr -d '\r' | grep -F "${NAME}" || true)
  if [[ -z "${REMOTE_HIT}" ]]; then
    echo "FAIL: post-ship verification — ${NAME} NOT found in remote ${QUEUE}/queue.json" >&2
    exit 5
  fi

  # Status-field grep-back (Fix #28-adjacent; 2026-07-01). Presence alone is insufficient:
  # the entry may be present but in a terminal state (completed / failed / canceled / killed)
  # from a prior run, making "VERIFIED present" a stale-claim (USER caught 2026-07-01 02:30 UTC).
  # Emit both status AND run_index so downstream watchers/USER can spot terminal-state ships.
  STATUS_PS="\$q = Get-Content ${REPO_REMOTE}/data/${QUEUE}/queue.json | ConvertFrom-Json; \$e = \$q.experiments | Where-Object { \$_.name -eq '${NAME}' }; if (\$e) { \"status=\" + \$e.status + \" run_index=\" + \$e.run_index }"
  STATUS_LINE=$(ssh -o ConnectTimeout=10 "${SSH_TARGET}" "powershell -Command \"${STATUS_PS}\"" 2>/dev/null | tr -d '\r' | head -1 || true)
  if [[ -z "${STATUS_LINE}" ]]; then
    # Fallback: entry present per REMOTE_HIT but status field unreadable (schema drift?).
    # Don't fail here — the presence-verify already passed. Just flag.
    echo "[queue-add] VERIFIED: ${NAME} present in remote ${QUEUE}/queue.json (status field unreadable)"
  else
    # Parse status; warn if terminal.
    ENTRY_STATUS=$(echo "${STATUS_LINE}" | grep -oE "status=[a-z_]+" | cut -d= -f2 || true)
    case "${ENTRY_STATUS}" in
      pending|running|"")
        echo "[queue-add] VERIFIED: ${NAME} present in remote ${QUEUE}/queue.json (${STATUS_LINE})"
        ;;
      done|completed|failed|canceled|killed)
        echo "[queue-add] WARN: ${NAME} present in remote queue.json BUT status is terminal (${STATUS_LINE})" >&2
        echo "[queue-add] WARN: this ship is a NO-OP for the runner unless --allow-duplicate reset the entry to pending" >&2
        echo "[queue-add] WARN: check queue_add.py output above — did it emit 'already in queue' or 'reset to pending'?" >&2
        # Still record + return success; the DIRECTOR needs to see this warn and act.
        # Exit-fail here would break --allow-duplicate flows that legitimately land on terminal entries.
        echo "[queue-add] VERIFIED: ${NAME} present in remote ${QUEUE}/queue.json (${STATUS_LINE})"
        ;;
      *)
        echo "[queue-add] VERIFIED: ${NAME} present in remote ${QUEUE}/queue.json (${STATUS_LINE}; unknown status)"
        ;;
    esac
  fi

  record_ship_attempt
  echo "[queue-add] OK: ${NAME} queued to ${QUEUE}"

else
  echo "FAIL: unknown queue '${QUEUE}'. Must be one of: overnight_queue, remote_cpu_queue, local_cpu_queue" >&2
  exit 4
fi
