#!/bin/bash
# Canonical wrapper for substrate-KB concept-content search — UNIFIED KB.
#
# 2026-07-02: UNIFIED architecture. Prior wrapper juggled two KBs (primary v1
# filename-index + separate chunk KB); chunk KB kept going stale (last built
# 2026-06-27) while primary stayed fresh via continuous-ingest. The chunk
# emission is now FOLDED INTO the primary KB (hdlab/director_kb.py::run_ingest,
# UNIFIED-KB commit). One KB, all content types:
#   - notes/memories/preregs/director_plan/fleet_state: filename entities +
#     CHUNK_CONTENT entities (content-encoded for semantic cosine retrieval)
#   - atoms/cert_ledger: JSONL row-per-line entities (concept text = entity name)
#   - wordnet/verbnet/framenet/gene_ontology/kegg_pathway/neurolex: API entities
#   - metrics: filename entities (JSON is not narrative, not chunked)
#
# The wrapper drops the --chunk-content flag it prior forced; primary now
# serves both filename-index queries and content-semantic chunk queries.
#
# Usage:
#   bash tools/substrate_query.sh "int8 precision at N=8192"
#   bash tools/substrate_query.sh --k 10 "cortex-side dense-Hopfield attention"
#   bash tools/substrate_query.sh --tau 0.10 "self-explanation richness ceiling"
#   bash tools/substrate_query.sh --json "..."
#
# All director_kb_query.py flags forward through.

set -e

cd "$(dirname "$0")/.."

python tools/director_kb_query.py \
    --schema-version v2 \
    --tau 0.15 \
    --k 5 \
    "$@"
