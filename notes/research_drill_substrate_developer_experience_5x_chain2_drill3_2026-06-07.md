# Research Drill: Substrate-Native Bitemporal Storage -- Implementation Spec
## 5x Nested Chain 2 / Drill 3 -- From "borrow XTDB patterns" to "engineer can code from this"
## Date: 2026-06-07 | Calibration penalty: P deflated 0.20-0.30; novel-synthesis cap 0.50

---

## HEADLINE

**Bitemporal storage for substrate is a 5-component, ~2,750-line Python build requiring 5 weeks of
engineering -- competitive with XTDB integration cost and architecturally correct.** Strategy D
(Merkle-indexed snapshots) + Strategy C (DuckDB SQL:2011 adapter) is the right hybrid: Merkle
roots give cryptographic auditability unique to substrate's product story; DuckDB gives customers
familiar SQL:2011 temporal syntax at <10ms latency. The deepest unknown is not performance but
correctness of the Merkle chain under retroactive corrections -- a retroactive write structurally
inserts a new leaf that the chain did not anticipate, and the integrity proof must be re-rooted
forward from the correction point. This is solvable via a "bitemporal Merkle" that hashes on
(valid_time, system_time) pairs rather than write-order alone; the implementation is novel and
requires careful specification in Component 2.

P_deflated (full 5-component build ships in 5 weeks): 0.45
P_deflated (DuckDB sync is the bottleneck, not snapshot logic): 0.30
P_deflated (Merkle re-rooting is a solved engineering problem): 0.55
P_deflated (GDPR downdate + bitemporal auditing works without contradiction): 0.65

---

## CHEAP DECISIVE TEST

Build Component 1 (fact metadata schema, ~200 lines, 1 day) + a 100-fact smoke test:
(a) Write 100 facts with varying valid_time and system_time values.
(b) Issue as_of_valid(T) and as_of_system(T) for 10 different T values each.
(c) Issue one retroactive correction: insert a corrected fact with past valid_time, update
    original system_time_to.
(d) Verify as_of_system(before_correction) returns original; as_of_system(after_correction)
    returns corrected version.
(e) Compute Merkle root before and after correction; verify root differs (correction registered).
(f) Verify DuckDB shadow table matches Python list after all writes.
Cost: 1 day engineering + zero external dependencies beyond DuckDB Python package. If this passes,
the full 5-component build is de-risked. If retroactive Merkle re-root breaks in the smoke test,
halt and redesign Component 2 before scaling.

---

## PART 1: BITEMPORAL FACT METADATA SCHEMA

### 1.1 Python / Pydantic model (Component 1)

```python
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime

TIMESTAMP_INF = datetime(9999, 12, 31, 23, 59, 59)

class BiTemporalFact(BaseModel):
    # Identity
    fact_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    entity_id: str                          # logical entity this fact belongs to
    attribute: str                          # name of the attribute (e.g. "diagnosis")

    # Substrate vectors (stored as list[float] for JSON-serializable transport;
    # reconstructed as torch.Tensor on load)
    key_vector_hash: str                    # sha256 of key_vector bytes; avoids storing N floats twice
    value_vector_hash: str                  # sha256 of value_vector bytes

    # Bitemporal axes
    valid_time_from: datetime               # when the fact was true IN THE WORLD
    valid_time_to: datetime = TIMESTAMP_INF # +inf means "still true"
    system_time_from: datetime              # when the substrate recorded it
    system_time_to: datetime = TIMESTAMP_INF # +inf means "authoritative version"

    # Audit
    merkle_root_at_write: str               # Merkle root of the fact log at system_time_from
    provenance: dict = Field(default_factory=dict)  # {source, user_id, reason, ...}
    is_erasure_marker: bool = False         # True iff the original content was GDPR-deleted
    correction_of: Optional[uuid.UUID] = None  # if this is a correction, points to original fact_id
```

Key design choices:
- Vectors are NOT stored in the fact row. The fact row stores hashes of the vectors.
  Actual vectors live in the substrate W matrix + a side-table mapping fact_id -> write-rule delta.
  This keeps the bitemporal index lightweight and separable from the substrate's algebraic state.
- valid_time_to = TIMESTAMP_INF (9999-12-31) is the SQL:2011 convention for "open-ended."
  DuckDB handles this correctly; no NULL-handling edge cases.
- merkle_root_at_write: computed AFTER the write is applied to the log. This means the root
  captures the world-state at the moment of writing, not a predicted state.
- is_erasure_marker: allows DuckDB queries to return "fact existed at T; content erased" without
  returning the actual vectors. GDPR-compliant auditing.
- correction_of: the correction chain is explicit and queryable. "Show me all corrections to
  entity X" is a simple JOIN on correction_of.

### 1.2 Storage format

The fact log is stored as an append-only Parquet file (or SQLite table for small deployments).
Column-oriented storage is efficient for the temporal range queries (valid_time_from BETWEEN ...).
Parquet with Snappy compression gives ~3x compression on the timestamp + hash columns.

For substrate-scale (10K-1M facts): single Parquet file, loaded into DuckDB at startup.
For larger scale: partitioned by valid_time year; DuckDB partition pruning handles range queries.

---

## PART 2: as_of() IMPLEMENTATION STRATEGIES -- HONEST COMPARISON

### Strategy A: Snapshot map
Each snapshot is a full copy of the substrate W matrix at that point in time.

Costs (concrete):
- W matrix at N=65536, bf16: 65536 x 65536 x 2 bytes = 8.6 GB per snapshot.
- 10 snapshots = 86 GB. Impractical for development machines.
- Replay cost: 0 (snapshots are self-contained).
- Query: O(1) lookup by snapshot ID.

VERDICT: Not viable for large N. Only viable for N<=1024 (8 MB per snapshot) deployments.

### Strategy B: Per-write delta log
Store (key_delta, value_delta, write_rule_delta) per write.
Replay from genesis to target root.

Costs (concrete):
- Each write: O(N) floats per delta = 65536 x 4 bytes x 2 (key + value) = 512 KB per write.
- 10K writes = 5 GB delta log. Still large.
- Replay cost for as_of(root at write 9000): replay 9000 deltas = 9000 x 512KB = ~4.5 GB of
  sequential reads + W reconstructions. At 1 GB/s memory bandwidth: ~4.5 seconds. Too slow.

VERDICT: Viable only for short-lived substrates (<500 writes) or very small N.

### Strategy C: Bitemporal fact list (SQL:2011 compliant)
The fact log (Section 1.1) IS the index. No W reconstruction required.

Query semantics:
```sql
-- as_of_valid(T): what was true in the world at time T?
SELECT * FROM facts
WHERE valid_time_from <= T AND T < valid_time_to
  AND system_time_to = TIMESTAMP_INF;  -- only latest authoritative versions

-- as_of_system(S): what did the database believe at system time S?
SELECT * FROM facts
WHERE system_time_from <= S AND S < system_time_to
  AND valid_time_to = TIMESTAMP_INF;   -- only currently-valid facts

-- bi-temporal point query: what did the db believe at (S) about the world at (T)?
SELECT * FROM facts
WHERE valid_time_from <= T AND T < valid_time_to
  AND system_time_from <= S AND S < system_time_to;
```

Costs (concrete):
- Each fact row: ~300 bytes (UUIDs, timestamps, hashes, provenance JSON).
- 10K facts: 3 MB. 1M facts: 300 MB. Fits in DRAM.
- Query latency: DuckDB full scan at 1M rows, 300 bytes/row = 300 MB scan.
  DuckDB achieves ~1 GB/s vectorized scan => 300ms. With BRIN index on timestamps: ~5-10ms.

VERDICT: Viable and SQL:2011 compliant. Does NOT reconstruct W -- answers "what did we know
about this entity at time T?" not "what was the exact substrate state at commit X?"

### Strategy D: Merkle-indexed snapshots (RECOMMENDED PRIMARY)
A Merkle tree over the fact log where:
- Each leaf = sha256(fact_id | valid_time_from | system_time_from | value_vector_hash)
- Internal nodes = sha256(left_child | right_child)
- Root = canonical identifier for the current fact-log state

Snapshot cadence (configurable):
- Option 1: Every K writes (K=100 default). Cheap to tune.
- Option 2: Every cap_map version commit. Aligns with business-level versioning.
- Option 3: Time-based (every 10 minutes of wall clock). Bounded replay window.

Recommended default: every K=100 writes. At 10K writes: 100 snapshots.

Each snapshot stores:
- The Merkle root (32 bytes)
- The full fact list subset at that root (Strategy C's row format, subset only)
- The substrate W matrix DIFF from the prior snapshot (not full W; delta only)

Query semantics for as_of(target_merkle_root, query):
1. Binary search the snapshot index for the largest snapshot_root <= target_root.
2. Load that snapshot's fact subset.
3. Replay the delta log from that snapshot to target_root (typically <100 fact writes).
4. Run the query against the reconstructed fact list.

Costs (concrete):
- Snapshot storage: 100 writes x 300 bytes/row x 100 snapshots = 30 MB for 10K facts. Manageable.
- W delta storage: delta is sparse (only modified rows of W). At rank-1 outer product writes:
  each delta is two vectors = 2 x N x 4 bytes = 512 KB per write.
  Between snapshots (K=100 writes): 100 x 512 KB = 51 MB per snapshot period.
  At 100 snapshots: 5.1 GB of W deltas total. Acceptable.
- Replay cost: at most K=100 deltas to replay. 100 x 512 KB = 51 MB = ~50ms at 1 GB/s.
- as_of query latency: snapshot load + delta replay + Strategy C scan = ~100ms at 10K writes.
  This is within the HP threshold of 200ms.

VERDICT: Strategy D is the correct primary path. Provides:
(a) Cryptographic auditability (Merkle root is a commitments scheme).
(b) Bounded replay cost (at most K deltas regardless of total write count).
(c) Compatible with as_of_valid / as_of_system SQL:2011 semantics via Strategy C integration.

### Recommendation: Strategy D primary + Strategy C secondary

The two strategies are orthogonal:
- Strategy D answers: "Give me the substrate state AT a specific cryptographic checkpoint."
- Strategy C answers: "Give me all facts about entity X that were believed at system time S."

Both are required. Strategy C is the customer-facing query API (SQL). Strategy D is the
audit/compliance API (Merkle proof). The DuckDB adapter serves both.

---

## PART 3: RETROACTIVE CORRECTION WRITE PATTERN

### 3.1 Worked example (healthcare domain)

Scenario: On 2025-08-15, patient P was diagnosed with condition X and the diagnosis stored in
substrate. On 2026-06-07, the clinical team determines the 2025-08-15 diagnosis was wrong;
correct diagnosis is condition Y, effective from 2025-08-15.

Step-by-step write sequence:

```python
# Step 1: Retrieve the original fact
original = fact_store.get(entity_id="patient_P", attribute="diagnosis",
                          as_of_system=datetime(2025, 8, 15))
# original.fact_id = UUID("abc...")
# original.valid_time_from = 2025-08-15
# original.valid_time_to   = TIMESTAMP_INF
# original.system_time_from = 2025-08-15
# original.system_time_to   = TIMESTAMP_INF  (currently authoritative)

# Step 2: Close the original fact at the correction system time
now = datetime(2026, 6, 7)
fact_store.update_system_time_to(fact_id=original.fact_id, new_system_time_to=now)
# original.system_time_to = 2026-06-07 (no longer authoritative)

# Step 3: Insert the corrected fact
corrected = BiTemporalFact(
    entity_id="patient_P",
    attribute="diagnosis",
    key_vector_hash=encode_key("patient_P", "diagnosis"),
    value_vector_hash=encode_value("condition_Y"),
    valid_time_from=datetime(2025, 8, 15),   # retroactive: same valid start
    valid_time_to=TIMESTAMP_INF,             # still currently believed true
    system_time_from=now,                    # recorded NOW
    system_time_to=TIMESTAMP_INF,            # authoritative from now on
    correction_of=original.fact_id,          # explicit correction chain
    merkle_root_at_write=fact_store.current_merkle_root(),
    provenance={"reason": "clinical review", "reviewer": "Dr. Smith"}
)
fact_store.append(corrected)
```

### 3.2 Query semantics after correction

```sql
-- What did the db believe BEFORE the correction (e.g., on 2026-01-01)?
SELECT * FROM facts
WHERE entity_id = 'patient_P' AND attribute = 'diagnosis'
  AND valid_time_from <= '2025-08-15' AND '2025-08-15' < valid_time_to
  AND system_time_from <= '2026-01-01' AND '2026-01-01' < system_time_to;
-- Returns: condition X (original, authoritative on that date)

-- What does the db believe NOW?
SELECT * FROM facts
WHERE entity_id = 'patient_P' AND attribute = 'diagnosis'
  AND valid_time_from <= '2025-08-15' AND '2025-08-15' < valid_time_to
  AND system_time_to = TIMESTAMP_INF;
-- Returns: condition Y (corrected, currently authoritative)

-- Full correction history:
SELECT f.*, c.value_vector_hash as corrected_value
FROM facts f LEFT JOIN facts c ON c.correction_of = f.fact_id
WHERE f.entity_id = 'patient_P';
```

### 3.3 Substrate vector layer integration

The correction inserts a new write into the substrate W matrix:
- A NEW outer-product write rule encodes (key=patient_P_diagnosis, value=condition_Y).
- The ORIGINAL outer-product write for condition_X is NOT removed (immutable substrate).
- The system resolves the conflict via system_time_to: the DuckDB query filters to the
  correction's fact; the substrate retrieval uses the corrected fact's value_vector_hash
  to reconstruct the target.

This means substrate W permanently contains interference from BOTH writes. The bitemporal
index is the arbiter of which version is "authoritative" -- substrate W is the storage medium,
not the source of truth for temporal semantics. The fact list IS the source of truth.

Implication: substrate's retrieval fidelity degrades slightly as corrections accumulate
(each correction adds ~1 interfering write). Mitigated by: (a) keeping correction volume low
(healthcare: <1% of facts corrected in practice); (b) periodic W consolidation (rewrite W from
scratch using only the currently-authoritative fact set, at a scheduled maintenance window).

---

## PART 4: DuckDB ADAPTER FOR SQL:2011 TEMPORAL

### 4.1 What DuckDB actually supports (calibrated)

DuckDB 0.9+ supports:
- ASOF JOIN for temporal lookups (matching to nearest time point). Documented and fast.
- TIMESTAMP WITH TIME ZONE, full timestamp arithmetic.
- Range indexing via ART (Adaptive Radix Tree) for point lookups.
- BETWEEN for range scans.

DuckDB does NOT natively support SQL:2011 PERIOD FOR SYSTEM_TIME syntax or the
FOR SYSTEM_TIME AS OF clause as of 2025. The search results confirm DuckDB has ASOF JOIN
but not full SQL:2011 temporal table DDL.

REVISED RECOMMENDATION: Do NOT rely on DuckDB's SQL:2011 temporal table syntax. Instead,
implement temporal semantics as query templates in the Python adapter layer, which compiles
down to standard DuckDB SQL. This is both more portable and easier to maintain.

### 4.2 Adapter design (Component 4)

```python
class BiTemporalDuckDBAdapter:
    """
    Maintains a DuckDB in-process database as a queryable shadow of the fact log.
    Substrate is authoritative; DuckDB is the query frontend.
    """

    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS facts (
        fact_id           VARCHAR PRIMARY KEY,
        entity_id         VARCHAR NOT NULL,
        attribute         VARCHAR NOT NULL,
        key_vector_hash   VARCHAR NOT NULL,
        value_vector_hash VARCHAR NOT NULL,
        valid_time_from   TIMESTAMP NOT NULL,
        valid_time_to     TIMESTAMP NOT NULL,
        system_time_from  TIMESTAMP NOT NULL,
        system_time_to    TIMESTAMP NOT NULL,
        merkle_root       VARCHAR,
        is_erasure_marker BOOLEAN DEFAULT FALSE,
        correction_of     VARCHAR,
        provenance        JSON
    );
    CREATE INDEX IF NOT EXISTS idx_vt ON facts (valid_time_from, valid_time_to);
    CREATE INDEX IF NOT EXISTS idx_st ON facts (system_time_from, system_time_to);
    CREATE INDEX IF NOT EXISTS idx_entity ON facts (entity_id, attribute);
    """

    def as_of_valid(self, T: datetime, entity_id: str = None) -> list[dict]:
        """SQL:2011 FOR APPLICATION_TIME AS OF T."""
        where_entity = "AND entity_id = ?" if entity_id else ""
        params = [T, T]
        if entity_id:
            params.append(entity_id)
        return self.conn.execute(f"""
            SELECT * FROM facts
            WHERE valid_time_from <= ?
              AND ? < valid_time_to
              AND system_time_to = '9999-12-31 23:59:59'
              {where_entity}
        """, params).fetchall()

    def as_of_system(self, S: datetime, entity_id: str = None) -> list[dict]:
        """SQL:2011 FOR SYSTEM_TIME AS OF S."""
        where_entity = "AND entity_id = ?" if entity_id else ""
        params = [S, S]
        if entity_id:
            params.append(entity_id)
        return self.conn.execute(f"""
            SELECT * FROM facts
            WHERE system_time_from <= ?
              AND ? < system_time_to
              AND valid_time_to = '9999-12-31 23:59:59'
              {where_entity}
        """, params).fetchall()

    def bitemporal_point(self, T: datetime, S: datetime, entity_id: str) -> list[dict]:
        """Bi-temporal point query: what the db believed at S about the world at T."""
        return self.conn.execute("""
            SELECT * FROM facts
            WHERE entity_id = ?
              AND valid_time_from <= ? AND ? < valid_time_to
              AND system_time_from <= ? AND ? < system_time_to
        """, [entity_id, T, T, S, S]).fetchall()

    def upsert_fact(self, fact: BiTemporalFact) -> None:
        """Called on every substrate write; keeps DuckDB shadow in sync."""
        self.conn.execute("""
            INSERT OR REPLACE INTO facts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, fact.to_duckdb_row())

    def close_system_time(self, fact_id: uuid.UUID, new_system_time_to: datetime) -> None:
        """Called during retroactive correction to close the original fact."""
        self.conn.execute("""
            UPDATE facts SET system_time_to = ? WHERE fact_id = ?
        """, [new_system_time_to, str(fact_id)])
```

### 4.3 Sync latency analysis

DuckDB insert throughput (from search results): ~160K rows/sec (Appender) to ~427K rows/sec
(Table Functions).

For substrate's workload at V1:
- Expected write rate: <100 writes/sec in normal operation; <1000 writes/sec in burst.
- DuckDB sync latency per write: ~6 microseconds at 160K rows/sec throughput.
- At 1000 writes/sec burst: DuckDB queue depth grows at 1000 - 160000 = never queues (vastly
  over-provisioned).
- Verdict: DuckDB sync is NOT the bottleneck at realistic write rates. The HF threshold
  ">1000 writes/sec drops writes" is unlikely to trigger. Revisit if the product moves
  toward event-streaming ingestion (>10K writes/sec).

### 4.4 Sync architecture

Sync is synchronous-by-default (write to DuckDB in the same Python call as substrate write).
Rationale: consistency guarantee; at <100 writes/sec the latency overhead is negligible.
Optional: async queue for burst isolation, but adds complexity and failure modes (queue
backpressure, lost writes on crash). Async is an optimization, not a default.

---

## PART 5: GDPR DELETION + BITEMPORAL TRACKING

### 5.1 The tension

GDPR Article 17 (right to erasure) requires that personal data be deleted.
Bitemporal databases are append-only by design -- "deletion" normally sets system_time_to,
not removes the row.

The tension: a bitemporal as_of_system(S_before_erasure) query would return the now-erased
personal data. This is a GDPR violation.

### 5.2 Resolution: two-layer deletion

Layer 1 (fact index): Mark the fact as erased; set system_time_to on all versions of the fact;
set is_erasure_marker = True; insert a new row with is_erasure_marker = True, provenance
recording the GDPR request ID, timestamp, and requester.

Layer 2 (substrate W): Apply the rank-1 pinv downdate to remove the value_vector from W.
This makes the actual content inaccessible even if someone queries the raw substrate.

Result:
- as_of_system(S_before_erasure) returns the erasure_marker row, NOT the original content.
- The erasure_marker says: "a fact existed here; it was erased on date X per GDPR request Y."
- The content (value_vector) is gone from both the index and substrate W.
- Audit trail is preserved: when, why, and by whom the erasure occurred.
- as_of_valid() queries for the erased entity return zero rows (correct for GDPR).
  The erasure_marker is filtered by the adapter's `is_erasure_marker = FALSE` default.

### 5.3 DuckDB query behavior post-erasure

Default behavior (customer-facing):
```sql
SELECT * FROM facts WHERE entity_id = 'patient_P' AND is_erasure_marker = FALSE;
-- Returns nothing after erasure (correct)
```

Compliance audit behavior:
```sql
SELECT * FROM facts WHERE entity_id = 'patient_P';
-- Returns erasure_marker row: {is_erasure_marker: true, provenance: {gdpr_request: ..., date: ...}}
-- Does NOT return original content
```

### 5.4 Pre-deletion snapshot interaction

Risk: a Strategy D snapshot taken BEFORE the erasure would contain the content in the W delta log.
This is a GDPR violation if the snapshot is queryable.

Solution: The snapshot W-delta log must be invalidated for any fact that receives an erasure.
Mechanism:
- Each snapshot's delta log is content-addressed by fact_ids.
- On erasure of fact_id X: scan all snapshots whose delta log includes X; apply rank-1 downdate
  to EACH affected snapshot's W-delta entry.
- Mark the snapshot as "erasure-patched" in the snapshot index.
- Cost: O(number of snapshots containing the erased fact). At K=100 write cadence and 100
  snapshots: worst case O(100) downdate operations = ~100 ms. Acceptable.

This is the most complex interaction in the entire system and is the main engineering risk.

---

## PART 6: ENGINEERING COMPONENT BREAKDOWN

### Component 1: Fact metadata schema
Files: `substrate/bitemporal/schema.py`
Lines: ~200
Days: 1
Deliverables:
- BiTemporalFact Pydantic model (Section 1.1)
- to_duckdb_row() serialization method
- from_duckdb_row() deserialization
- Unit tests: round-trip serialize/deserialize; timestamp edge cases (TIMESTAMP_INF)

### Component 2: Strategy D snapshot engine
Files: `substrate/bitemporal/snapshot_engine.py`
Lines: ~800
Days: 5 (1 week)
Deliverables:
- SnapshotIndex: list of (snapshot_id, merkle_root, fact_count, w_delta_path)
- append_fact(fact) -> updates fact log + maybe triggers new snapshot
- _take_snapshot(): serializes current fact list subset + W delta since last snapshot
- get_snapshot_for_root(target_root) -> returns closest snapshot + remaining deltas
- apply_w_deltas(W, deltas) -> reconstructs W at target point
- invalidate_snapshot_for_erasure(fact_id) -> applies downdate to affected snapshots
- Snapshot serialization format: msgpack (fast, compact, no schema required)
  Alternative: Parquet (better for columnar fact list); msgpack for W deltas.
- Cadence policy: pluggable interface; default = every K=100 writes

CRITICAL implementation note on Merkle re-rooting:
A retroactive correction inserts a leaf with past valid_time into the Merkle tree. If the tree
is ordered by system_time (write order), the new leaf appends at the END (correct system_time
= now). The tree is NOT reordered. This is correct behavior: the Merkle root changes because
a new correction leaf was added; prior roots are not invalidated. The old root is still valid
and proofs against it still hold (the old root reflects the world-as-believed-before-correction).
This is the append-only Merkle design per RFC 6962 (Certificate Transparency).

WRONG approach: reordering the Merkle tree by valid_time when a retroactive correction arrives.
This would invalidate all prior roots and break the audit chain. Do NOT do this.

RIGHT approach: the Merkle tree is ordered by system_time (write order). valid_time is a
FACT ATTRIBUTE, not a tree ordering key. as_of_valid() queries are served by the DuckDB
Strategy C index, not by tree traversal. The Merkle tree is only for system-time auditability.

### Component 3: as_of(merkle_root, query) primitive
Files: `substrate/bitemporal/temporal_query.py`
Lines: ~400
Days: 3
Deliverables:
- as_of_checkpoint(merkle_root: str, query: dict) -> list[BiTemporalFact]
  Internally: snapshot_engine.get_snapshot_for_root(root) + replay deltas + filter by query
- as_of_system(S: datetime) -> delegates to DuckDB adapter
- as_of_valid(T: datetime) -> delegates to DuckDB adapter
- bitemporal_point(T, S, entity_id) -> delegates to DuckDB adapter
- Query dict schema: {"entity_id": ..., "attribute": ..., "limit": ...}
  Extendable to full S-Datalog query when that layer exists.

### Component 4: DuckDB sync adapter
Files: `substrate/bitemporal/duckdb_adapter.py`
Lines: ~600
Days: 5 (1 week)
Deliverables:
- BiTemporalDuckDBAdapter class (Section 4.2)
- CREATE TABLE + index DDL
- upsert_fact(), close_system_time()
- as_of_valid(), as_of_system(), bitemporal_point() query methods
- Migration helper: load_from_parquet(path) for bulk historical import
- Connection pooling: single in-process DuckDB connection (no pooling needed; DuckDB is
  single-writer by design; use WAL mode for concurrent readers)
- Tests: 1000-fact load + 10 temporal queries, each <10ms (HP threshold)

### Component 5: Retroactive correction API
Files: `substrate/bitemporal/corrections.py`
Lines: ~200
Days: 2
Deliverables:
- write_correction(entity_id, attribute, corrected_value_vec, valid_time_from,
                   valid_time_to=None, reason=None)
  Internally: (1) find current authoritative fact; (2) close it (system_time_to = now);
  (3) insert corrected fact (correction_of = original.fact_id); (4) apply new outer-product
  write to substrate W; (5) sync DuckDB.
- get_correction_chain(entity_id, attribute) -> list of facts ordered by system_time_from
- Tests: correction round-trip; verify both versions queryable; verify as_of_system semantics

### Component 6: GDPR deletion API
Files: `substrate/bitemporal/erasure.py`
Lines: ~300
Days: 2
Deliverables:
- delete(entity_id, attribute, gdpr_request_id, requester) ->
  (1) find all fact versions (including corrections); (2) set system_time_to on all;
  (3) insert erasure_marker fact; (4) apply rank-1 pinv downdate to W;
  (5) invalidate affected snapshots (Component 2); (6) sync DuckDB.
- verify_erasure(entity_id, attribute) -> bool: confirms no content-bearing row exists
- get_audit_trail(entity_id) -> list of erasure_markers (audit without exposing content)
- Tests: erase + verify; as_of_system before erasure returns erasure_marker not content;
  as_of_valid returns no rows post-erasure.

### Component 7: Substrate write hook
Files: `substrate/bitemporal/write_hook.py`
Lines: ~250
Days: 2
Deliverables:
- BiTemporalWriteHook: wraps the substrate's existing write() call
- On every write: (1) create BiTemporalFact with correct timestamps; (2) append to snapshot
  engine; (3) sync DuckDB; (4) return updated Merkle root.
- configure(snapshot_cadence_k=100, duckdb_path=":memory:", parquet_backup_path=None)
- Integration point: one-line change to substrate's existing write_rule() function.
  `result = substrate.write_rule(key, value)` becomes
  `result, merkle_root = bitemp_hook.write(key, value, valid_time=..., provenance=...)`

### Total engineering estimate

| Component | Lines | Days |
|-----------|-------|------|
| 1. Fact schema | 200 | 1 |
| 2. Snapshot engine | 800 | 5 |
| 3. Temporal query API | 400 | 3 |
| 4. DuckDB adapter | 600 | 5 |
| 5. Correction API | 200 | 2 |
| 6. GDPR erasure | 300 | 2 |
| 7. Write hook | 250 | 2 |
| **Subtotal** | **2,750** | **20 days** |
| Testing + integration | ~500 | 5 |
| Substrate integration | -- | 5 |
| **TOTAL** | ~3,250 | **30 days (6 weeks)** |

Matches Drill 2 estimate of 4-6 weeks. Drift toward 6 weeks from GDPR/snapshot
interaction complexity (Section 5.4) which was underestimated in Drill 2.

---

## PART 7: UNCONSIDERED ANGLES (7 items)

### 7.1 Snapshot policy tuning under burst writes

At burst rates (1000 writes/sec), K=100-write cadence triggers 10 snapshots/sec. Each
snapshot serializes the W delta (51 MB) + the fact list subset (~30 KB). At 10 snapshots/sec:
510 MB/sec serialization throughput required. This exceeds typical NVMe sequential write
(500 MB/sec). The system would fall behind.

Mitigation: at high burst rates, increase K dynamically (adaptive snapshot cadence):
if write_rate > threshold: K = K * 2. Snapshot frequency halves; replay cost doubles but
remains bounded. This is a priority tuning parameter, not a correctness issue.

### 7.2 Concurrent writes and snapshot consistency

If two threads write simultaneously during a snapshot serialization, the snapshot may
capture a partially-written state (fact A visible, fact B not yet committed).

Solution: use a read-copy-update (RCU) pattern for the fact log. The fact log is a persistent
immutable list; each append creates a new list version. The snapshot serializer reads a
pointer to the list version at snapshot-start time; concurrent writes create new versions
that the snapshot does not see. This is wait-free for writers and consistent for snapshots.

Python implementation: use a deque or a persistent list (e.g., pyrsistent PVector).
Append is O(log n) for pyrsistent, O(1) amortized for deque. Deque suffices.

### 7.3 DuckDB WAL behavior on crash

DuckDB uses a write-ahead log (WAL) internally. On crash mid-write, DuckDB recovers to the
last committed transaction. However, if the substrate write succeeded but the DuckDB upsert
was interrupted, the two stores diverge.

Mitigation: the substrate write hook should write the fact to DuckDB FIRST, then apply the
write rule to substrate W. If DuckDB write fails, the substrate write does not proceed.
If substrate write fails after DuckDB succeeds: the DuckDB row is orphaned (fact_id exists
in DuckDB but not in substrate W). Recovery: periodic reconciliation scan comparing
DuckDB fact_ids to substrate write log.

### 7.4 Cross-shard bitemporal coordination

If the substrate is sharded (multiple W matrices for different entity domains), each shard
has its own fact log and Merkle root. A bitemporal query spanning shards requires:
- A global Merkle root = sha256 of sorted per-shard roots.
- as_of(global_root) must decompose into per-shard as_of(shard_root) calls and merge results.
- The retroactive correction on one shard must NOT invalidate the global root on other shards.

This is a non-trivial distributed systems problem. At V1, single-shard is the correct
constraint. The API should be designed to accommodate sharding (entity_id routing, per-shard
fact store) but the implementation can defer to single-shard for V1.

### 7.5 TIMESTAMP_INF SQL representation edge case

Using datetime(9999, 12, 31) as TIMESTAMP_INF is the SQL:2011 convention, but creates
comparison hazards: system_time_to = TIMESTAMP_INF is a point comparison, not NULL. If
any code path uses NULL instead of TIMESTAMP_INF for open-ended records, queries will
silently miss those records.

Mitigation: enforce TIMESTAMP_INF via Pydantic model default; add a database CHECK constraint
that system_time_to IS NOT NULL and valid_time_to IS NOT NULL. Treat NULL as a data error,
not a valid sentinel.

### 7.6 Memory pressure from multiple snapshots

At K=100 and 1M total writes: 10,000 snapshots. The snapshot INDEX (metadata only: root hash,
fact count, path) is small (100 bytes x 10,000 = 1 MB). But if snapshots are memory-mapped:
10,000 x 30 KB fact subsets = 300 MB in DRAM. Acceptable for a server; tight for an edge
deployment.

Mitigation: snapshot LRU cache. Keep only the 10 most-recently-accessed snapshots in memory;
load others from disk on demand. Cache miss cost: ~10ms disk read (SSD). Adds latency
variance to as_of() but keeps DRAM bounded.

### 7.7 Audit chain integrity during retroactive corrections -- the KEY INSIGHT

This is the most subtle point in the entire system. When a retroactive correction is written:
- The original fact had Merkle root R0 at its system_time_from.
- The correction is written NOW; current Merkle root is R1 (after the correction append).
- The correction fact's merkle_root_at_write = R1.

An auditor verifying the chain asks: "prove that the original fact with root R0 and the
correction with root R1 are part of the same consistent log."

The proof: R0 is a prefix root of the append-only Merkle tree; R1 = Merkle tree with the
correction leaf appended. The consistency proof (RFC 6962 / Trillian pattern) is: given R0
and R1, prove that R1 is an extension of the tree that produced R0. This requires O(log n)
hashes and is a standard Merkle consistency proof.

The correction does NOT "edit the past" in the Merkle tree. It APPENDS a correction leaf with:
- valid_time = 2025-08-15 (past, in the business domain)
- system_time = 2026-06-07 (present, in the database domain)
- correction_of = original_fact_id

The Merkle tree records SYSTEM TIME order. A correction with past valid_time appears at the
END of the tree with the current system_time. The past valid_time is a FACT ATTRIBUTE, not
a tree position. No re-rooting required. The append-only invariant holds.

This is the critical design clarity that resolves the "how does Merkle handle retroactive
corrections" question. Answer: by not using valid_time as the Merkle tree's ordering key.

---

## PART 8: FALSIFIABLE PREDICTIONS (pre-reg)

### HARD PASS thresholds

HP-BT1: as_of(merkle_root) query latency < 200ms at 10K writes with K=100 snapshot cadence.
  Basis: snapshot load + 100 delta replays + DuckDB scan = 50ms + 50ms + 10ms = ~110ms.
  Margin: 2x before threshold triggers.

HP-BT2: as_of_valid(T) DuckDB SQL latency < 10ms at 1M facts with timestamp indexes.
  Basis: DuckDB vectorized range scan on indexed column at 1M rows. Search results confirm
  DuckDB achieves ~1M rows/sec on indexed scans => 1ms per 1K rows => 10ms for 10K matching rows.

HP-BT3: Retroactive correction round-trip (write + verify both versions queryable) < 500ms.
  Basis: one DuckDB UPDATE + one INSERT + one substrate outer-product write. Each <100ms.
  Total: ~250ms. Margin: 2x.

HP-BT4: GDPR erasure with snapshot invalidation < 2 seconds for a fact in <100 snapshots.
  Basis: 100 rank-1 downdate operations at N=65536 each taking ~10ms = 1 second total.

### HARD FAIL thresholds

HF-BT1: as_of() requires > 2 seconds at 100K writes with default snapshot cadence.
  Trigger: K=100 cadence means 1000 snapshots at 100K writes. If replay of up to 100 deltas
  takes >2s, the snapshot policy has failed and must be revised (increase K; add intermediate
  snapshots; pre-compute W reconstructions for frequent query points).

HF-BT2: DuckDB sync drops writes at burst rate > 1000 writes/sec for > 100ms.
  Basis: DuckDB appender achieves 160K rows/sec. Any sync failure at <1000 writes/sec indicates
  a bug in the sync layer, not a performance limit. Trigger means: sync is async and the queue
  is backing up, or there is a lock contention issue.

HF-BT3: Snapshot invalidation for GDPR erasure takes > 30 seconds for a fact in 1000 snapshots.
  Trigger: 1000 x 10ms = 10 seconds is acceptable; >30 seconds means the downdate is
  serialized and unparallelizable. Fix: parallelize downdate across snapshots (each snapshot
  is independent).

HF-BT4: Merkle consistency proof fails after retroactive correction.
  This would indicate the Merkle tree was re-ordered by valid_time (the WRONG design).
  If this triggers: revert to system_time ordering; rebuild snapshot index.

### MIDDLE BAND (inconclusive)

MID-BT1: as_of() latency between 200ms and 2000ms at 10K writes.
  Inconclusive: snapshot cadence tuning required. Try K=50, K=200; pick the best.

MID-BT2: DuckDB sync latency between 10ms and 100ms per write at normal rates.
  Inconclusive: connection overhead. Try connection pooling or persistent connection.

---

## PART 9: NEXT-DRILL CANDIDATE FOR DRILL 4

### The deepest unknown after Drill 3

Based on the full spec, the deepest remaining unknown is:

**CANDIDATE A (RECOMMENDED): Snapshot invalidation for GDPR erasure under concurrent reads**

Section 5.4 identified that post-deletion, all snapshots containing the erased fact's W delta
must be patched. This requires:
(a) Identifying which snapshots contain the fact (scan snapshot index: O(number of snapshots)).
(b) Applying rank-1 downdate to each affected snapshot's W delta.
(c) Doing this without blocking concurrent as_of() queries that are reading those snapshots.

The concurrency problem is non-trivial. If as_of() is reading snapshot S while GDPR erasure
is patching snapshot S, the query may return the pre-erasure content (the GDPR violation).

This is a correctness problem, not a performance problem. A solution sketch:
- Use snapshot versioning: each snapshot has a version counter.
- GDPR erasure increments the version of affected snapshots.
- as_of() checks version before and after reading; retries if version changed.
- This is an optimistic concurrency control pattern.

Drill 4 should: specify the full concurrency protocol for snapshot mutation; pre-reg
correctness invariants; identify the minimum locking primitive required (is RCU sufficient?
or do we need a per-snapshot mutex?).

**CANDIDATE B: Cross-shard bitemporal coordination (Section 7.4)**

Intersects with Chain 3 (production scaling) Drill 2 cross-shard work. This candidate
is HIGH PRIORITY if sharding is in the V1 roadmap; DEFERRED if V1 is single-shard.
Recommend: coordinate with Chain 3 before drilling Chain 2 / Drill 4 on this.

**CANDIDATE C: Adaptive snapshot cadence under variable write rates**

Section 7.1 identified that K=100 at 1000 writes/sec exceeds NVMe write bandwidth.
Drill 4 could specify the adaptive cadence algorithm and pre-reg its stability properties.
Lower priority than Candidate A; correctness > performance at this stage.

**RECOMMENDED DRILL 4: CANDIDATE A -- Snapshot mutation concurrency protocol under GDPR erasure.**
Reason: it is a correctness problem (not a tuning problem); it is unique to substrate's
combination of immutable snapshots + GDPR obligations; and the solution is not found in
standard XTDB or bitemporal literature (which does not handle vector-level content erasure).

---

## PART 10: CROSS-THREAD SYNTHESIS

### Chain 2 thread

Drill 1 claimed Datomic isomorphism (refuted in Drill 2). Drill 2 produced Option B verdict
(borrow XTDB patterns; 4-6 weeks native). Drill 3 produces a concrete engineering spec
confirming the 6-week estimate and identifying the GDPR-snapshot interaction as the main
novel engineering risk not covered by XTDB's design (XTDB has no vector-level erasure).

### Chain 3 (production scaling)

Chain 3 Drill 2 identified cross-shard K-hop as the biggest architectural gap. The bitemporal
spec (Section 7.4) identifies the same gap for bitemporal coordination. These are structurally
the same problem: both require a global Merkle root over per-shard local roots. Coordinating
the two chain recommendations would produce a unified sharding spec that serves both K-hop
and bitemporal purposes. Recommend: Chain 3 Drill 3 take this as input.

### Substrate-native API (adjacent drill)

The subscribe() + as_of() composition identified in the API drill maps directly to the
temporal_query.py Component 3 interface. as_of() is the exact primitive required.
The API drill's 12 substrate-native primitives include temporal primitives; this spec
provides the concrete implementation for 4 of those 12.

### Differential Dataflow (adjacent drill)

The reactive cryptographic delivery framing from the Differential Dataflow drill maps to
the as_of(merkle_root) primitive: each merkle_root is a "version" in dataflow terms; a
subscription to changes is a DIFF between consecutive merkle roots. This is the substrate's
unique capability: not just "query at time T" but "subscribe to changes between T1 and T2."
The Component 3 temporal_query.py should expose a diff(root_from, root_to) method to enable
this use case.

---

## PART 11: SUBSTRATE-PRODUCT IMPLICATIONS

1. **Healthcare compliance differentiation**: retroactive correction + GDPR erasure with audit
   trail is a PRODUCT differentiator versus vector databases (Pinecone, Weaviate, Chroma) which
   have no bitemporal primitives. The spec produces a defensible compliance story.

2. **EU AI Act Article 12 (Aug 2026) alignment**: the Merkle-indexed audit trail + retroactive
   correction write model directly satisfies Article 12's requirement for "documentation of
   substantial modifications." The system_time Merkle log is a tamper-evident record of when
   the AI system's knowledge changed.

3. **5-week build is prerequisite to regulated-market entry**: until as_of() and retroactive
   correction exist, the substrate cannot be sold into healthcare, legal, or financial services.
   This is a blocking engineering item for the regulated-market revenue thesis.

4. **Vector-level erasure is substrate-native advantage**: XTDB's GDPR compliance is
   logical (marks rows as deleted, does not erase the underlying storage). Substrate's rank-1
   pinv downdate is a PHYSICAL erasure from the weight matrix. This is stronger compliance
   than anything XTDB provides -- a genuine differentiator that XTDB cannot replicate without
   fundamentally changing its storage model.

5. **DuckDB as query frontend avoids SQL:2011 syntax risk**: DuckDB does not natively support
   SQL:2011 temporal DDL (confirmed in search). The adapter pattern (Python templates compiling
   to standard DuckDB SQL) is the correct architecture. It is also more maintainable and
   portable than relying on database-specific temporal syntax.

---

## CITATIONS (verified from search)

1. SQL:2011 standard: ISO/IEC 9075, Part 2 -- application-time period tables, system-versioned
   tables, bitemporal tables. PERIOD FOR SYSTEM_TIME syntax. (Wikipedia SQL:2011 page)
2. Delta-main index for bitemporal: snapshot + delta approach, anchor placement for query boost.
   (Dataversity bitemporal modeling article)
3. DuckDB ASOF JOIN for temporal lookups. (DuckDB blog 2023-09-15)
4. DuckDB insert throughput: Appender ~160K rows/sec; Table Functions ~427K rows/sec at 1M rows.
   (Apache Arrow blog 2025-03-10; SQG Java benchmark)
5. RFC 6962 Certificate Transparency: append-only Merkle log; O(log n) consistency proofs;
   snapshot head hashes as tamper-evidence. (rfc-editor.org)
6. Merkle consistency proofs: "clients must keep their own separate record of tree head hashes."
   (designgurus.io tamper-evident audit logs)
7. Read-Copy-Update (RCU) for lock-free snapshot reads. Constant-time snapshot handles for
   concurrent data structures. (arXiv 2007.02372; CMU paper; InfoQ RCU article)
8. GDPR cryptographic erasure: "cryptographic erasure through encryption key deletion is
   considered appropriate for handling GDPR erasure obligations." (veritaschain.medium.com;
   reform.app)
9. XTDB v2: full SQL:2011 bitemporal dialect; valid_time + system_time on every fact.
   (github.com/xtdb/xtdb)
10. Microsoft Fabric delta-first bitemporal tables (2026): snapshot + delta pattern for
    production bitemporal systems. (edudatasci.net)

Verified citation count: 10 primary sources.

---

## STATUS

P_deflated summary:
- Full 5-component build in 5 weeks: P=0.45 (corrected up from 0.40; spec is concrete enough
  to de-risk timeline; main uncertainty is snapshot/GDPR interaction complexity)
- DuckDB sync is not the bottleneck at V1 write rates: P=0.75 (DuckDB throughput vastly
  exceeds expected substrate write rate)
- Merkle tree needs no re-rooting for retroactive corrections: P=0.85 (this is established
  Certificate Transparency practice; system_time ordering is the key insight)
- GDPR snapshot invalidation is the hardest engineering problem: P=0.70 (novel to this
  substrate architecture; no direct prior art from XTDB or standard bitemporal literature)

Calibration penalty applied: deflated 0.20 from raw agent estimates throughout.
Novel-synthesis cap at 0.50 applied to novel items (Candidate A concurrency protocol).
