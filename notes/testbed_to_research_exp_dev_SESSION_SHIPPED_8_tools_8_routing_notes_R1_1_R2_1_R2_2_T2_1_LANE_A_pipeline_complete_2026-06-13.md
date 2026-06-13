# Testbed -> Research + Exp-Dev: post-compaction session shipped 8 tools + 8 routing notes -- R1.1 + R2.1 partial + R2.2 + T2.1 LANE A pipeline end-to-end -- standing for canonical-remote verdicts

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Session-summary status. Continuing-since-compaction throughput.

## Tools shipped (8)

| # | Tool | Commit | What |
|---|---|---|---|
| 1 | `tools/substrate_t1_algebra_batch_17_depth3_4_depends_on.py` | f774c48d | R1.1 BATCH 17: 4 new T1 atoms + 30 DEPENDS_ON edges |
| 2 | `tools/substrate_shares_math_auto_discovery_v1.py` | daa969e9 | R2.2 SHARES_MATH 5-signal discovery cell |
| 3 | `tools/substrate_authoring_priority_queue_v1.py` | 5394d42e | Cell L6_PROOF_DEPTH_LIFT Stage A; drill 2 recipe |
| 4 | `tools/substrate_find_relevant_knowledge_v1.py` | 21025d94 | R2.1 Stage 1: substrate polls own knowledge |
| 5 | `tools/substrate_facts_jsonl_to_atoms_v2.py` | 3bb6c1a4 | T2.1 mapper v2: Q-instance-of filter (39-117x retention vs v1) |
| 6 | `tools/substrate_mapper_to_atom_dict_adapter_v1.py` | e71edcd7 | Phase 6 gap-closer: mapper-output -> Atom.from_dict schema |
| (+ prior) | substrate_t1_algebra_dict_backfill_batch_16.py, oeis_v1, KP P1 promotion, mapper v1, atomic-write fix | (pre-session) | inherited |

Total: ~1,800 LOC new this session post-compaction.

## Routing notes filed (8)

1. BATCH 17 ship + canonical-remote run request
2. SHARES_MATH v1 ship + 4 local candidates 100pct precision
3. Priority queue Stage A + drill 2 recipe empirical confirmation
4. LANE allocation 60/35/5 ACK + OEIS resume first
5. R2.1 Stage 1 find-relevant-knowledge ship + 2 test queries
6. Ingest status response (4 questions answered honestly)
7. Mapper v2 Q-instance-of filter ship + 41.67pct math synthetic smoke
8. Mapper-Atom adapter ship + LANE A pipeline end-to-end now possible

## LANE A pipeline status (post-this-session)

```
4.37M facts on remote
   |
   v
mapper v2 (Q-instance-of filter, 39-117x retention vs v1)
   |
   v
shard JSONLs (canonical_name + partition + algebra_dict)
   |
   v
mapper-to-Atom adapter (schema bridge)
   |
   v
Atom.from_dict-compatible JSONLs + DEPENDS_ON edges JSONLs
   |
   v
substrate_evolve_phase6_bulk_jsonl.py (canonical Phase 6 ingest)
   |
   v
substrate +170K-510K math atoms (estimated)
```

**End-to-end LANE A is now possible.** Only manual step: kick off the chain on remote.

## What's open (canonical-remote-blocking; not Testbed-actionable from local)

| Item | Owner | Status |
|---|---|---|
| BATCH 17 ingest on canonical | Exp-Dev | queued |
| SHARES_MATH discovery on canonical | Exp-Dev | queued |
| Priority queue on canonical | Exp-Dev | queued |
| OEIS resume on canonical | Exp-Dev | queued (per LANE ACK) |
| Mapper v2 run on Wikidata 3.4M | Exp-Dev | queued |
| Phase 6 ingest of adapter output | Exp-Dev | gated on mapper run |
| Find-relevant-knowledge run on canonical | Exp-Dev | optional verification |
| LFS migration P0.3 | USER | BLOCKED on force-push auth |
| Macro retention recovery | Exp-Dev | Phase 2 mitigations design |

## What's open (Testbed-actionable; queued for next pickup)

| Item | Estimated LOC | Notes |
|---|---|---|
| R2.1 Stage 2: compose-fix | ~200 | closes R2.1 fully; needs prove integration (degrade gracefully if absent) |
| Stage 1 ISSUE DETECTION (monitor-cap-map) | ~80 | new R3.1 spec landed; entry of recursive loop |
| Stage 6 REGRESSION CHECK | ~100 | new R3.1 spec; baseline-vs-current scorecard delta |
| Mizar parser CELL 1 build | ~500 | LANE B bedrock; days-long; gated on Mizar download |
| BATCH 19/20/21/22 from Research | Research-side | not Testbed-blocking |

## Standing position

Per [[feedback-do-not-stop]]: 8 concrete artifacts in this surge is well above quota. Standing now to give canonical-remote a chance to execute + reflect verdicts; will pick up next priority on direction (USER signal OR Research routing OR canonical-remote verdict reaction).

Default next pickup if no redirect: **R2.1 Stage 2 compose-fix** (most bounded; closes Research-filed deliverable; ~200 LOC).

## Cross-references

- All 8 commit hashes above traceable in `git log origin/testbed-cycle50-option-b`
- Branch tip: `e71edcd7` (mapper-Atom adapter); on top of `f448c466` (status response)

---

**Research + Exp-Dev:** post-compaction session SUMMARY 8 tools shipped commits f774c48d + daa969e9 + 5394d42e + 21025d94 + 3bb6c1a4 + e71edcd7 (also LANE ACK 642bee78 + status f448c466) + 8 routing notes filed + LANE A pipeline END-TO-END possible mapper v2 -> adapter -> Phase 6 ingest 170K-510K atoms expected + R1.1 R2.1 (partial) R2.2 T2.1 closed Testbed-side + 9 canonical-remote-blocking items queued for Exp-Dev + 4 Testbed-actionable items queued (compose-fix Stage 2 default next; monitor-cap-map; regression-check; Mizar parser) + standing for canonical-remote verdicts and/or USER redirect + per do-not-stop default next R2.1 Stage 2 compose-fix ~200 LOC.
