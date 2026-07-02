#!/bin/bash
# Wrapper for substrate-KB concept-content search — MERGED across BOTH KBs.
#
# 2026-07-02: routes to tools/substrate_query_merged.py which fans out to
# primary v1 KB (filename-index; INCLUDES atoms class) AND chunk KB
# (--chunk-content; text chunks only, excludes atoms BY DESIGN per
# build_substrate_director_kb_chunk_v1.py primitive) in parallel, then merges
# by cosine desc / dedupes by entity / tags each hit with [v1] / [chunk] /
# [v1+chunk] KB origin.
#
# Fixes recurring bug 2026-07-02: prior wrapper hardcoded --chunk-content, so
# every USER-locked pre-dispatch concept-query check had been architecturally
# blind to atoms for weeks (including today's Stage 1 SCALE_FREE / TOPOLOGY_FREE
# physics-law CG_META atoms).
#
# Usage:
#   bash tools/substrate_query.sh "int8 precision at N=8192"
#   bash tools/substrate_query.sh --k 10 "cortex-side dense-Hopfield attention"
#   bash tools/substrate_query.sh --tau 0.10 "self-explanation richness ceiling"
#   bash tools/substrate_query.sh --json "..."   # merged JSON payload
#
# Prints STALENESS WARNING at top if either KB manifest.json is >24h old.
# All director_kb_query.py flags forward through to both child invocations.

set -e

cd "$(dirname "$0")/.."

# Defaults preserved from the prior single-KB wrapper (--schema-version v2 tau 0.15 k 5),
# forwarded to both child director_kb_query.py invocations. The merger adds --chunk-content
# to one child automatically.
python tools/substrate_query_merged.py \
    --schema-version v2 \
    --tau 0.15 \
    --k 5 \
    "$@"
