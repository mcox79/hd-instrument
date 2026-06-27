#!/usr/bin/env bash
# sync_canonical_kb_to_remote.sh -- mirror canonical substrate-Director-KB to
# remote_cpu_queue runner via temp-dir-then-mv (atomic-swap; matches local
# continuous-ingest atomic-swap from commit 5de28ea1).
#
# Source: d:/AI/hd-instrument/data/substrate_director_kb_v1/
# Target: marsh@home:C:/dev/hd-instrument/data/substrate_director_kb_v1/
#
# Why atomic-swap: a reader (any cell on remote calling load_default_kb()) must
# see EITHER the old complete KB OR the new complete KB; never a partial mid-
# SCP state where manifest.json claims n_entities=577k but W.pt is half-written.
# Local continuous-ingest is atomic-swap safe; the remote mirror must match.
#
# Flow:
#   1. Verify local canonical exists + manifest parseable.
#   2. SCP all files into REMOTE/data/substrate_director_kb_v1_inflight/
#   3. Remove REMOTE/data/substrate_director_kb_v1/ (if exists)
#   4. Rename _inflight/ -> substrate_director_kb_v1/
#   5. Post-swap remote sanity check (manifest readable + entity count match).
#
# Idempotent: re-running with no local change is fine; final mv is fast.
#
# Usage:
#   bash tools/sync_canonical_kb_to_remote.sh
#   bash tools/sync_canonical_kb_to_remote.sh --dry-run
#
# Exit codes:
#   0 = sync OK
#   1 = local KB missing/unparseable
#   2 = remote SSH/SCP failure
#   3 = post-swap verification failure
#
# Audit log: appends one JSON line per run to
#   data/kb_remote_provision_audit_log.jsonl
#
# ASCII-only. No emojis.

set -u

REPO="d:/AI/hd-instrument"
LOCAL_KB="${REPO}/data/substrate_director_kb_v1"
REMOTE_HOST="marsh@home"
REMOTE_REPO="C:/dev/hd-instrument"
REMOTE_KB="${REMOTE_REPO}/data/substrate_director_kb_v1"
REMOTE_INFLIGHT="${REMOTE_REPO}/data/substrate_director_kb_v1_inflight"
AUDIT_LOG="${REPO}/data/kb_remote_provision_audit_log.jsonl"

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
    DRY_RUN=1
fi

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
t0=$(date +%s)

log() { printf '[sync] %s\n' "$*" >&2; }

audit() {
    # $1 = JSON line (no trailing newline)
    mkdir -p "$(dirname "${AUDIT_LOG}")"
    printf '%s\n' "$1" >> "${AUDIT_LOG}"
}

# ---------- Phase 0: local sanity ----------
if [ ! -d "${LOCAL_KB}" ]; then
    log "ERROR: local canonical KB not found at ${LOCAL_KB}"
    audit "{\"ts\":\"${TS}\",\"phase\":\"local_check\",\"ok\":false,\"err\":\"local_kb_missing\",\"path\":\"${LOCAL_KB}\"}"
    exit 1
fi
if [ ! -f "${LOCAL_KB}/manifest.json" ]; then
    log "ERROR: local manifest missing at ${LOCAL_KB}/manifest.json"
    audit "{\"ts\":\"${TS}\",\"phase\":\"local_check\",\"ok\":false,\"err\":\"manifest_missing\"}"
    exit 1
fi

LOCAL_N_ENT=$(python -c "import json,sys;m=json.load(open(r'${LOCAL_KB}/manifest.json'));print(m.get('n_entities',0))" 2>/dev/null || echo 0)
LOCAL_KB_VER=$(python -c "import json,sys;m=json.load(open(r'${LOCAL_KB}/manifest.json'));print(m.get('kb_version','unknown'))" 2>/dev/null || echo unknown)
LOCAL_BYTES=$(du -sb "${LOCAL_KB}" 2>/dev/null | awk '{print $1}')

log "local OK: n_entities=${LOCAL_N_ENT} kb_version=${LOCAL_KB_VER} bytes=${LOCAL_BYTES}"

if [ "${LOCAL_N_ENT}" -lt 500000 ]; then
    log "ERROR: local n_entities=${LOCAL_N_ENT} < 500000 (HARD_FAIL band per Tier-1 prereg)"
    audit "{\"ts\":\"${TS}\",\"phase\":\"local_check\",\"ok\":false,\"err\":\"too_few_entities\",\"n_entities\":${LOCAL_N_ENT}}"
    exit 1
fi

if [ "${DRY_RUN}" = "1" ]; then
    log "DRY-RUN: would SCP ${LOCAL_KB}/* -> ${REMOTE_HOST}:${REMOTE_INFLIGHT}/"
    log "DRY-RUN: would atomic-swap inflight -> ${REMOTE_KB}"
    audit "{\"ts\":\"${TS}\",\"phase\":\"dry_run\",\"ok\":true,\"n_entities\":${LOCAL_N_ENT},\"bytes\":${LOCAL_BYTES}}"
    exit 0
fi

# ---------- Phase 1: prep remote inflight dir ----------
# Use SSH to clear any half-written prior inflight + create fresh empty dir.
log "preparing remote inflight dir ${REMOTE_INFLIGHT}..."
ssh -o ConnectTimeout=15 -o BatchMode=yes "${REMOTE_HOST}" \
    "if exist \"${REMOTE_INFLIGHT}\" rmdir /s /q \"${REMOTE_INFLIGHT}\" & mkdir \"${REMOTE_INFLIGHT}\"" \
    2>&1 | grep -v "WARNING\|store now\|server may\|This session" >&2 || true

# Verify creation
RC=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "${REMOTE_HOST}" \
    "if exist \"${REMOTE_INFLIGHT}\" (echo EXISTS) else (echo MISSING)" \
    2>&1 | grep -v "WARNING\|store now\|server may\|This session" | tr -d '\r\n ')
if [ "${RC}" != "EXISTS" ]; then
    log "ERROR: failed to create remote inflight dir; rc=${RC}"
    audit "{\"ts\":\"${TS}\",\"phase\":\"prep_inflight\",\"ok\":false,\"err\":\"mkdir_failed\"}"
    exit 2
fi

# ---------- Phase 2: SCP all files into inflight ----------
log "SCP all canonical files (this is the slow phase; ~4.9GB; expect 5-30min over LAN)..."
t_scp_0=$(date +%s)
for f in manifest.json reject_log.jsonl relations.jsonl entities.jsonl W.pt R.pt atoms.jsonl E.pt; do
    src="${LOCAL_KB}/${f}"
    if [ ! -f "${src}" ]; then
        log "  skip ${f} (not present locally)"
        continue
    fi
    sz=$(stat -c %s "${src}" 2>/dev/null || stat -f %z "${src}" 2>/dev/null || echo 0)
    log "  scp ${f} (${sz} bytes)..."
    if ! scp -o ConnectTimeout=15 -o BatchMode=yes -q "${src}" "${REMOTE_HOST}:${REMOTE_INFLIGHT}/${f}" 2>&1 | grep -v "WARNING\|store now\|server may\|This session" >&2; then
        log "ERROR: scp ${f} failed"
        audit "{\"ts\":\"${TS}\",\"phase\":\"scp\",\"ok\":false,\"err\":\"scp_failed\",\"file\":\"${f}\"}"
        exit 2
    fi
done
t_scp_1=$(date +%s)
SCP_S=$((t_scp_1 - t_scp_0))
log "scp phase done in ${SCP_S}s"

# ---------- Phase 3: atomic swap inflight -> canonical ----------
log "atomic-swap on remote: remove old + rename inflight -> canonical..."
ssh -o ConnectTimeout=15 -o BatchMode=yes "${REMOTE_HOST}" \
    "if exist \"${REMOTE_KB}\" rmdir /s /q \"${REMOTE_KB}\" & move \"${REMOTE_INFLIGHT}\" \"${REMOTE_KB}\"" \
    2>&1 | grep -v "WARNING\|store now\|server may\|This session" >&2 || true

# Verify final canonical exists
RC=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "${REMOTE_HOST}" \
    "if exist \"${REMOTE_KB}\\manifest.json\" (echo OK) else (echo MISSING)" \
    2>&1 | grep -v "WARNING\|store now\|server may\|This session" | tr -d '\r\n ')
if [ "${RC}" != "OK" ]; then
    log "ERROR: post-swap remote canonical manifest missing; rc=${RC}"
    audit "{\"ts\":\"${TS}\",\"phase\":\"swap\",\"ok\":false,\"err\":\"swap_failed\"}"
    exit 3
fi

# ---------- Phase 4: post-swap verification ----------
log "verifying remote manifest n_entities..."
REMOTE_N_ENT=$(ssh -o ConnectTimeout=10 -o BatchMode=yes "${REMOTE_HOST}" \
    "python -c \"import json;m=json.load(open(r'${REMOTE_KB}/manifest.json'));print(m.get('n_entities',0))\"" \
    2>&1 | grep -v "WARNING\|store now\|server may\|This session" | tr -d '\r\n ')

if [ "${REMOTE_N_ENT}" != "${LOCAL_N_ENT}" ]; then
    log "ERROR: remote n_entities=${REMOTE_N_ENT} != local ${LOCAL_N_ENT}"
    audit "{\"ts\":\"${TS}\",\"phase\":\"verify\",\"ok\":false,\"err\":\"entity_count_mismatch\",\"local\":${LOCAL_N_ENT},\"remote\":\"${REMOTE_N_ENT}\"}"
    exit 3
fi

t1=$(date +%s)
WALL_S=$((t1 - t0))
log "SUCCESS: local=${LOCAL_N_ENT} == remote=${REMOTE_N_ENT}; wall=${WALL_S}s scp=${SCP_S}s bytes=${LOCAL_BYTES}"
audit "{\"ts\":\"${TS}\",\"phase\":\"complete\",\"ok\":true,\"n_entities\":${LOCAL_N_ENT},\"kb_version\":\"${LOCAL_KB_VER}\",\"bytes\":${LOCAL_BYTES},\"wall_s\":${WALL_S},\"scp_s\":${SCP_S}}"

exit 0
