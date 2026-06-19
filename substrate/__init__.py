"""
Substrate library — production port of the validated PP-* research primitives.

This is the production-grade reusable library extracted from the experiments/exp_*.py
research cells. Each module ports one PP-* primitive (validated cycle 154-188) into a
clean reusable API.

Modules:
    core            FHRR primitives (cphasor, cidx, bind, unbind, bundle); binary variant
    audit           Merkle hash chain + cryptographic proofs (shared utility)
    persistence     Disk-backed substrate state (numpy memmap + json metadata)
    shards          Sharding strategies (per-subject / per-relation / hierarchical / hybrid)
    khop            K-hop traversal (PP-119); 3-shard relay; confidence-weighted
    cascade         Cascade router (PP-123); native -> fuzzy fallback
    disambig        Two-stage entity disambiguation + K-hop (PP-125)
    confidence      Cleanup confidence threshold (PP-107); 'I do not know' rendering
    inverted        Mechanism B sleep-defrag inverted property index
    cross_shard     Mechanism C scatter-gather cross-shard chain extraction
    gdpr            PP-104 surgical exact erasure via pinv downdate + audit log
    bitemporal      As-of queries (PP-???) via searchsorted on sorted valid-time
    counterfactual  Pearl-style do() operator + DAG recompute + Merkle audit
    kv_memory       PP-135 Tier-5 substrate-KV with Pythia-1.4B (PATH A; deferred to W2)

All modules are pure Python (numpy + torch); no external service dependencies.
The FastAPI backend in `backend/` wires these into HTTP endpoints.

Validated benchmarks (cycle 188, public datasets):
    WebQSP K-hop:        97.6%
    CWQ K-hop:           92.6%
    FB15k-237 sharded:   r@5 = 1.000 (1-hop), 0.705 (2-hop); monolithic = 0.007 (140x gap)
    MuSiQue r@10:        0.784
    Wikipedia ingest:    155 art/sec; r@1 = 0.971; 5.84M proj 10-12hr
    Cascade router P95:  0.21 ms at 1M facts
    PP-107 abstention:   AUC = 1.0
    GDPR exact erase:    intact = 1.0; deleted-removed = 1.0; <1 ms/erase at 1M
    Bitemporal as-of:    1.000 correct; per-query 0.003 ms at 1M versions
"""

__version__ = "0.1.0"
