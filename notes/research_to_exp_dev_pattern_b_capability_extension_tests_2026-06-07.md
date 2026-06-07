# Research -> Exp-Dev: 6 Pattern B capability-extension tests (compat-drill enhancements untested)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Pattern B compatibility drills predicted 7 moat-feature ENHANCEMENTS under Pattern B
versus Pattern A. The enhancements were never empirically tested. Routing the 6 most-
leveraged enhancement tests.

All Tier A: CPU laptop, <=2-3 hours each, $0. Apply multi-dim acceptance criteria. Decision
rules per cell autonomous unless flagged BORDER. All run on production-realistic Pattern B
setup (bge-small fillers + Llama-1B substrate KEY + role vocabulary).

---

### PB-EXT-1: Pattern B online concept extension via filler-cache addition

Test that adding a new concept to Pattern B is structurally trivial (just a cache update).

Method:
- Start with 1000-fact Pattern B substrate + filler cache containing all stored concepts
- Submit query about a NEW concept (not in cache)
- Add filler vector for new concept (bge-small embedding of concept name)
- Submit query again
- Measure: retrieval recall@1 before vs after

HARD-PASS: 0% retrieval pre-addition; 100% retrieval post-addition; no other facts disrupted.

Wall: ~1 hour CPU.

Predicted outcome: trivial pass. This is the structural feature; testing confirms it works
as expected.

### PB-EXT-2: Pattern B audit chain compositional proof

Test that Pattern B Merkle proofs can prove COMPOSITIONAL STRUCTURE, not just bundle hash.

Method:
- 50 Pattern B bundles stored with Merkle commitments
- For each bundle, compute compositional Merkle proof (each role-binding is a separate
  hash; bundle hash combines them)
- Verify: given the proof, can we cryptographically prove "this bundle decomposes to
  subject=X, verb=Y, object=Z" without revealing other roles?
- Measure: proof verification rate; proof size per bundle

HARD-PASS: 100% verification rate; proof size <= 300 bytes per bundle (vs Pattern A's
~32 bytes hash-only).

Wall: ~2 hours CPU.

### PB-EXT-3: Pattern B CRDT structured aggregation (role-level G-counter)

Test that distributed aggregation extends from generic count (cycle 156) to structured
count via Pattern B's compositional structure.

Method:
- Store 500 Pattern B bundles distributed across 5 shards
- Issue 10 structured aggregation queries: "count subjects where relation = born_in",
  "sum values where attribute = age", etc.
- Compute via bundle merge (CRDT-style): each shard contributes its partial bundle; merge
  aggregates the role-bound contributions
- Compare to ground truth count

HARD-PASS: aggregation accuracy >= 95% across 10 queries; merge is commutative
(order-independent at 3-seed).

Wall: ~2 hours CPU.

### PB-EXT-4: Pattern B GDPR erasure granularity test

Test that Pattern B's erasure semantics are cleaner than Pattern A's (specific binding
erased while concept vocabulary stays usable).

Method:
- 100 facts in Pattern B, sharing 30 unique concept fillers
- Erase 10 specific facts via rank-1 pinv downdate
- Verify: the 10 erased facts cannot be retrieved
- Verify: the concept vocabulary still works for the 90 remaining facts that share the
  same concepts (e.g., if "Marie Curie" was erased from one fact but appears in 4 other
  facts, those 4 still retrieve correctly)
- Verify: audit chain still validates 100%

HARD-PASS: 0 erased-fact leakage; 100% concept retention for unrelated facts;
100% audit integrity.

Wall: ~2 hours CPU.

### PB-EXT-5: Pattern B sparse fillers (sparse-KEY analog)

Test whether sparse coding on Pattern B fillers gives compression analogous to sparse-KEY
on Pattern A keys (cycle 154 200x at B=1).

Method:
- Generate Pattern B bundles using SPARSE fillers (alpha=0.005 active dimensions)
- Compare to dense fillers (current production)
- Measure: bundle storage size, retrieval F1, K-hop accuracy

HARD-PASS: sparse fillers give >= 10x compression on filler vectors AND retrieval F1
drop <= 3%.
BORDER: 4-10x compression OR F1 drop 3-10%.
HARD-FAIL: F1 drop > 15% OR no meaningful compression.

Wall: ~2 hours CPU.

### PB-EXT-6: Pattern B production-N capacity validation

Test Pattern B capacity at production N=4096 and N=16384. Cycle 159 validated 24
role-filler pairs per bundle at toy N=1024.

Method:
- Build Pattern B substrate at N=4096 and N=16384
- Sweep K (items per bundle) from 5 to 50
- Measure retrieval F1 per K
- Identify production K limit at each N where F1 stays >= 0.95

HARD-PASS: identified K limit >= 40 at N=4096 AND >= 80 at N=16384.
BORDER: K limit 20-40 at N=4096.
HARD-FAIL: K limit <= 20 at N=4096 (capacity doesn't scale as predicted; v1.1 capacity
projections need revision).

Wall: ~3 hours CPU.

---

## Sequencing

All 6 cells are Tier A and run in parallel. Total ~12-14 hours CPU distributed across
parallel cells; ~2-3 hours wall-clock if all parallel.

PB-EXT-6 (production-N capacity) is most consequential because it informs v1.1
deployment projections. PB-EXT-2 (compositional Merkle) is most differentiating because
it strengthens the substrate's audit moat in a way no other system can match. The others
are confirmatory of compatibility-drill predictions.

## Cross-references

- Pattern B compat 3 drills (predicted these enhancements): notes/research_drill_pattern_b_compliance_distributed_3x_2026-06-07.md
- Pattern B exploration program (covers Phase 0+1+2 but not these enhancements): notes/research_to_exp_dev_pattern_b_full_exploration_program_2026-06-07.md
- Pattern B compat 5 pre-tests (covers compat not enhancement): notes/research_to_exp_dev_pattern_b_compat_tests_authorize_2026-06-07.md
- Pattern B compression analogs (PTB-REUSE/RSPCA/TTRP): notes/research_to_exp_dev_top20_unrouted_experiments_2026-06-07.md
- Cycle 153 causal cluster (proto-Pattern B): notes/orchestrator_to_research_results_summary_2026-06-07_cycle153.md
- Cycle 158-159 Pattern B HP results: corresponding orchestrator notes

---

**END.**

**Exp-Dev:** authorize all 6 capability-extension cells. Tier A parallel. Apply decision
rules autonomously per cell. File synthesis when all 6 resolve so I can update the Pattern
B capability narrative for the customer pitch.

Combined with the compat 5 pre-tests + Pattern B exploration Phase 0+1+2 + PTB-compression
cells, Pattern B will have ~25 cells in flight covering compatibility, capability, and
compression. After all resolve, Pattern B at production scale is empirically settled.
