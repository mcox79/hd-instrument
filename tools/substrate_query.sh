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

# ==================== MEASURED 2026-08-18. READ BEFORE TRUSTING THIS TOOL. ====================
# **THE PRIMARY DEFECT IS NOT SLOWNESS: THIS QUERY RETURNS NOTHING AND REPORTS SUCCESS.**
#
# Measured directly, both interpreters, twice:
#   bash tools/substrate_query.sh "<any query>"          -> rc=0, ~38 s, **0 BYTES of output**
#   .venv/Scripts/python.exe tools/director_kb_query.py  -> rc=0, ~51 s, **no result lines**
# Bare `python` resolves correctly here (3.12.10, `--version` in 1 s), so this is NOT the
# bare-python-vs-venv trap and NOT a hang. The tool runs, takes ~40-50 s, prints nothing, exits 0.
#
# **CONSEQUENCE: THE MANDATORY PRIOR-WORK CHECK HAS BEEN NON-FUNCTIONAL.** Every agent running it
# gets an empty answer and reports "timed out" or "no prior work found". At least FIVE did so on
# 2026-08-17/18 alone; one held a research lane until the Director killed its query by hand.
# **AN EMPTY RESULT FROM THIS TOOL IS NOT EVIDENCE OF ABSENCE.** The backing index
# (`hd_director_kb_continuous_ingest`) is separately documented as LIVELOCKED -- it self-terminates
# at its own 45-minute limit while Task Scheduler reports it healthy.
#
# **DO THIS INSTEAD, and say in your report which you did:**
#   ls notes/ | grep -i <topic>          # then READ the hits
#   os.walk over data/ for metrics.json  # then reconcile to the registry, never the reverse
# An absence claim requires an ENUMERATION, never a search that returned nothing.
#
# **HONEST STATUS OF THE TIMEOUT BELOW: ITS FIRING WAS NOT DEMONSTRATED.** It was added to bound
# the cost, but the wrapper still took ~38 s against a 25 s guard while returning rc=0, and that was
# not explained. Standalone `timeout 5 python -c "sleep(30)"` DOES return rc=124 correctly in this
# shell, so the mechanism works in isolation. **Treat the guard as UNPROVEN**; the reliable
# instruction is the enumeration above, not this wrapper's exit code.
# ==============================================================================================
_SQ_TIMEOUT="${HD_SUBSTRATE_QUERY_TIMEOUT:-25}"

if ! timeout "${_SQ_TIMEOUT}" python tools/director_kb_query.py \
        --schema-version v2 \
        --tau 0.15 \
        --k 5 \
        "$@"; then
    _rc=$?
    if [ "${_rc}" -eq 124 ]; then
        echo "" >&2
        echo "SUBSTRATE_QUERY_TIMEOUT after ${_SQ_TIMEOUT}s -- THE KB DID NOT ANSWER." >&2
        echo "This is the documented director_kb livelock, NOT evidence that no prior work exists." >&2
        echo "DO NOT report this as 'no prior work found'. Enumerate from disk instead:" >&2
        echo "  ls notes/ | grep -i <topic>      # and read the hits" >&2
        echo "  os.walk over data/ for metrics.json, then reconcile to the registry" >&2
        echo "State in your report HOW you enumerated -- an absence claim needs an enumeration," >&2
        echo "never a search that timed out." >&2
        exit 0
    fi
    exit "${_rc}"
fi
