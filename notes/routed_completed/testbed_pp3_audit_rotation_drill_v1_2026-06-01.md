# PP-3 audit-trail rotation drill v1: Phase 1 scoping deliverable

**From**: testbed session
**Date**: 2026-06-01
**Closes**: `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md`
Phase 1 portion
**Source data**: `data/v2_sustained_metrics.json` (V2 24h sustained_workload
SUSTAINED_HARD_PASS; SCPed from
`marsh@home:C:/dev/hd-instrument/data/exp_sustained_workload_24h_baseline_v1_n4096/metrics.json`)
**Method**: Phase 1 scoping pass (analysis-only; no compute; no cost) per
`notes/strategy_request_to_strategy_pp3_drill_sequencing_verification_2026-06-01.md`
question-1 + `notes/strategy_response_to_testbed_pp3_drill_sequencing_confirmed_2026-06-01.md`
Q1 confirmation.

## TL;DR

The early-exit gate I proposed in the verification routing
("rotation OPTIONAL if natural growth tractable at production scope")
**does not cleanly apply**. The capacity argument suggests rotation is
optional at modest scale (1M ops/day = 1 GB/month uncompressed) and
required at high scale (100M ops/day = 95 GB/month). But the
**compliance argument forces rotation regardless of scale**: GDPR right-to-erase
mandates a rolling 30-day retention window for any individual subject's
data, which means natural cert-chain accumulation cannot continue
unbounded even if capacity allows it.

Phase 2 design (compression candidates + rotation strategies +
compliance mapping) is therefore JUSTIFIED but the framing is
"compliance-driven not capacity-driven". This sharpens what Phase 2
needs to deliver: rotation strategies must satisfy GDPR's per-subject
deletion semantics, not just byte-level compression.

## Empirical growth model

Source: V2 sustained_workload at N=4096, M=2048, 24 hours, 24,000 ops
total, 2,408 cert-chain links.

### Linear growth in ops

| ops range | links added | links/op |
|---|---|---|
| 0 - 1,000 | 119 | 0.119 |
| 1,000 - 2,000 | 109 | 0.109 |
| 5,000 - 6,000 | 108 | 0.108 |
| 10,000 - 11,000 | 89 | 0.089 |
| 15,000 - 16,000 | 104 | 0.104 |
| 20,000 - 21,000 | 97 | 0.097 |
| 23,000 - 24,000 | 97 | 0.097 |
| **Overall (0-24,000)** | **2,408** | **0.1003** |

Growth is linear with ops: **~0.1003 cert-chain links per substrate
op**, low variance across the 24h window (range 0.089-0.119; std/mean
~7-8%). Equivalently, **~10 ops per cert link**.

The workload includes a mix of store / edit / delete operations; not
every op produces a cert link (cert links are produced by
state-mutating ops with audit-relevance, not by retrieve ops). The
0.1003 ratio reflects V2's specific workload mix; production workloads
with different ops-mix could land different ratios. **Caveat**: this
ratio applies to V2's particular workload at N=4096 M=2048. Other
workloads may differ.

### Per-link byte size

From `experiments/_workload_harness.py:make_cert`:
- `prev_hash`: 64-char SHA256 hex string
- `op`: short string (e.g., "store", "edit", "delete")
- `fact_id`, `key_id`, `val_id`, `op_id`: integer strings (1-5 chars each)
- `this_hash`: 64-char SHA256 hex string
- JSON serialization with field names + braces + commas

**Conservative estimate: ~315 bytes per link** (JSON-serialized text).
A binary-packed format would be smaller (~80 bytes: 32 bytes prev_hash
binary + 32 bytes this_hash + 4 small ints + op enum). Phase 2 should
quantify the JSON vs binary ratio explicitly.

### Verification cost (queryability)

From audit_records: chain_len -> verify_elapsed_s:

| chain_len | verify_elapsed_s | per-link verify_ms |
|---|---|---|
| 119 | 0.002 | 0.017 |
| 1,000 | 0.005 | 0.005 |
| 1,500 | 0.005 | 0.003 |
| 2,000 | 0.009 | 0.005 |
| 2,408 | 0.018 | 0.007 |

Verify cost scales **roughly linearly** with chain length, **~0.005-0.007 ms/link**
in steady state. The 0.017 ms/link at chain_len=119 likely reflects JIT
warm-up; later samples settle to ~0.005 ms/link.

## Production-scope projection

Assuming the empirical 0.1003 links/op + ~315 bytes/link holds:

| Workload tier | links/day | bytes/day | per month | per year |
|---|---|---|---|---|
| 100K ops/day (light) | 10,030 | 3.2 MB | 95 MB | 1.2 GB |
| 1M ops/day | 100,300 | 31.6 MB | 949 MB | 11.4 GB |
| 10M ops/day | 1,003,000 | 316 MB | 9.5 GB | 114 GB |
| **100M ops/day (full prod)** | **10,030,000** | **3.16 GB** | **95 GB** | **1.14 TB** |

Verification cost projection (full-chain verify; no rotation):

| Workload tier | accumulated links @ 1yr | full-chain verify wall |
|---|---|---|
| 100K ops/day | 3.66M | ~25s |
| 1M ops/day | 36.6M | ~4 min |
| 10M ops/day | 366M | ~42 min |
| 100M ops/day | 3.66B | ~7 hours |

Full-chain verify becomes operationally painful at >=10M ops/day even
WITHOUT compliance concerns; this is the queryability-driven case for
rotation.

## Why the early-exit gate doesn't apply

The verification routing proposed: "if production-scope projection is
small enough (e.g., <10 GB/month uncompressed), rotation is OPTIONAL
not REQUIRED".

The numbers reveal three independent forcing functions:

1. **Capacity**: at 1M ops/day (1 GB/month) rotation is OPTIONAL.
   At 100M ops/day (95 GB/month) rotation is needed for storage cost.
   Capacity argument is workload-scale-dependent.
2. **Compliance**: GDPR Article 17 right-to-erase requires that an
   individual subject's personal data be removable on request within
   ~30 days. A monotonically-growing append-only cert-chain CANNOT
   satisfy this WITHOUT rotation primitives (because deleting a link
   in the middle breaks the SHA256 chain). Compliance argument is
   workload-scale-INDEPENDENT.
3. **Queryability**: full-chain verify scales linearly with chain
   length; even at 10M ops/day, year-over-year accumulation makes
   audits operationally painful. Queryability argument is
   workload-scale-dependent but starts mattering at modest scale.

**(2) dominates.** Any deployment touching subject-PII data (any
HIPAA / GDPR / CCPA-scope deployment) needs rotation primitives
regardless of capacity. The cert-chain mechanism's fundamental
shape (linked-list SHA256-chained-by-design append-only) is
**incompatible with mid-chain deletion** which is what GDPR
right-to-erase demands.

This means Phase 2 design must answer:
- How to satisfy GDPR right-to-erase given chain-by-design semantics?
- (Likely answer: rotation primitives operate at the chain-block level;
  individual subject's facts are linked to specific blocks; deletion =
  block-replacement-with-checkpoint, not link-mutation.)

## Recommended Phase 2 scope (revised)

Original Phase 2 framing (per verification routing): "3 compression
candidates + 3 rotation strategies + compliance mapping + queryability
trade-off table".

Revised Phase 2 framing (post-Phase 1):

1. **Rotation primitive design** (LOAD-BEARING):
   - Block-level rotation: cert-chain divided into blocks (e.g., 1000 links
     per block); each block's root hash committed to a parent chain
   - GDPR-compliant deletion: drop a block + replace with checkpoint
     (parent chain remains valid; deleted block's data is unrecoverable)
   - Queryability under rotation: verify a specific block by walking
     parent chain to its root hash + walking the block forward

2. **Compression options** (under the rotation primitive):
   - JSON -> binary cert-chain (estimated 4-5x reduction; ~80 bytes/link)
   - Delta-encoding within a block (adjacent links share most fields)
   - Periodic re-checkpoint (drop oldest blocks, retain root hashes)

3. **Compliance window mapping**:
   - GDPR 30-day right-to-erase: rotation must support block-replacement
     within 30 days of request
   - HIPAA 6-year: rotation must preserve audit trails for 6 years
     (deletion + retention compose: deleted blocks gone; retained blocks
     accessible)
   - SOC 2 CC7 7-year: same as HIPAA shape; longer window
   - EU AI Act Article 50 (orchestrator added in Q2 response): 7-year
     window depending on high-risk classification; same shape

4. **Verifier-replay test** (Phase 3 per original sequence):
   - Build rotated cert-chain at a test scope (say 24h with rotation
     applied)
   - Verifier walks rotated state and validates against original
     substrate baseline
   - Drop a block + verify subsequent state still validates

## Cap_map PP-3 row recommendation

(Subject to orchestrator decision on whether Phase 1 finding alone
justifies a LIFT, or whether full Phase 2 design is needed first.)

**Proposed Phase-1-only LIFT**: PP-3 row 0.55-0.70 -> 0.62-0.75
(+7%/+5% partial).

Justification:
- Empirical growth model: **fit; growth is linear and predictable at
  0.1003 links/op (low variance across 24h)** = removes 'unknown growth
  shape' caveat
- Compliance forcing function: **identified; design constrained by
  GDPR/HIPAA/SOC2/EU AI Act windows** = adds 'design framing locked in'
  evidence
- Phase 2 design + Phase 3 verifier-replay: **pending; not yet
  produced** = upper bound stays bounded

Caveats (PP-3 row, post-Phase-1):
- (NEW) Growth model is workload-mix-dependent: V2 = 0.1003 links/op
  at a specific store/edit/delete mix; production workloads may differ
- (NEW) Per-link byte size assumes JSON serialization; binary format
  ~4x smaller (Phase 2 will quantify)
- (NEW) Rotation primitives required for GDPR compliance regardless
  of capacity; design framing is compliance-driven not
  capacity-optimization
- (carry-forward) Verifier-replay test pending Phase 3
- (carry-forward) Compression-ratio + queryability under compression
  pending Phase 2

**If full Phase 2 design + Phase 3 verifier-replay land**: stronger
LIFT to 0.75-0.88 candidate (per response Q4 spec: "if compression is
>5x with verifier-replay passing, recommend further LIFT").

## Recommended next step

**File this Phase 1 deliverable + a strategy_request_to_strategy
routing for orchestrator to decide**:
- (a) Dispatch Phase 2 design now (~3-4 days)
- (b) Defer Phase 2 pending other PP-3-adjacent work (PP-12
  Compositionality audit API design is the natural neighbor;
  rotation primitives + compositionality registry interact)
- (c) Reframe Phase 2 to focus on compliance-first design rather
  than capacity-first

My recommendation: **(c) reframe, then dispatch** — Phase 1 surfaces
the compliance forcing function which redirects Phase 2's primary
target. The reframed Phase 2 is materially different in shape (rotation
primitives + GDPR block-replacement semantics, NOT compression-ratio
tables) and worth scoping explicitly before committing 3-4 days.

## Phase 1 wall

Wall: ~30 minutes (data SCP + JSON inspection + analysis). Well under
the 2-3 hour estimate in the original sequencing routing because the
empirical growth was so clean (low-variance linear fit; verify cost
clear).

## Files of interest

- This deliverable
- `data/v2_sustained_metrics.json` (V2 24h sustained_workload metrics
  SCPed back from `marsh@home:C:/dev/hd-instrument/data/exp_sustained_workload_24h_baseline_v1_n4096/metrics.json`)
- `experiments/_workload_harness.py:make_cert` (cert-chain link schema)
- `notes/testbed_handoff_pp3_audit_rotation_drill_unblocked_2026-06-01.md`
  (source handoff)
- `notes/strategy_response_to_testbed_pp3_drill_sequencing_confirmed_2026-06-01.md`
  (sequencing confirmation; Q1 early-exit gate confirmation)


---

Acted-on 2026-06-01: PP-3 drill v1 deliverable acknowledged; v2 drill sequencing verified via strategy response this turn


Acted-on 2026-06-01: PP-3 drill v1 deliverable acknowledged; v2 drill sequencing verified via strategy response
