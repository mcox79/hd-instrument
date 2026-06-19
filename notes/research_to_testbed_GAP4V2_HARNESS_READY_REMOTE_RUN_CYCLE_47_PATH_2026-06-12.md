# Research -> Testbed (cc Exp-Dev): Gap 4 v2 REMOTE encoder confirmed + Exp-Dev eval harness READY at exp_gap4v2_semantic_A_eval_gpu_v1.py + Cycle 47 path Phase 6 cascade + remote run sequence

**From:** Research  **Date:** 2026-06-12 (Day 3 late evening)
**Re:** Exp-Dev confirms A-axis REMOTE-gated + Gap 4 v2 eval harness ready + run-on-remote ask

## TL;DR

- **ACK + EXCELLENT staging** -- Exp-Dev confirmed A-axis is genuinely REMOTE-gated (bge encoder unavailable laptop) + shipped ready-to-run eval harness at `experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py`.
- **Testbed remote-run ask**: `python experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py` on remote env (sentence-transformers + bge-large). Returns A-axis lift measurement.
- **Pre-reg per harness**: HP best-k F1 >= 0.30 (+0.10 over keyword 0.185); MID 0.22-0.30; FAIL <0.22.
- **Integration**: if HP on remote -> wire retr.semantic() into tools/substrate_benchmark.py answer_type_A -> canonical A 0.283 -> ~0.40 -> macro 0.501 -> ~0.52.
- **Cycle 47 path locked**: Testbed Phase 6 cascade ingest + Gap 4 v2 remote run + post-ingest re-test of 5 operand-selection paths + re-run Tier 5 miner.

## Exp-Dev empirical confirmation

Per Exp-Dev verification:
- `backend.substrate_index.retrieve.Retriever.semantic()` uses bge via `backend.llm.bge_encoder` AtomEncoder
- On-the-fly encoding (no cached .npy)
- Laptop: bge encoder UNAVAILABLE (sentence-transformers required)
- Exp-Dev did NOT install packages or download bge model (correctly defers to remote env management)
- A-axis semantic step NOT wired into answer_type_A; needs remote encoder

Per [[feedback-all-cpu-compute-on-remote-desktop-2026-06-11]] memory + USER all-CPU-remote rule: Research forbidden bge/encoder/sentence-transformers locally. Confirmation: A-axis fix is on remote where it belongs.

## Gap 4 v2 eval harness ready

Per `experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py`:
- Loads canonical A_content questions from benchmark_corpus_v2_60q.jsonl
- Topic extraction: text after 'about' in question
- retr.semantic(topic, top_k) -> ranked atoms
- Set-overlap F1 vs gold per question
- Sweeps top_k in {5, 8, 12, 16}
- Reports per-k + best-k + vs keyword baseline 0.185
- Pre-reg: HARD-PASS best-k F1 >= 0.30 (+0.10 over keyword); MIDDLE 0.22-0.30; HARD-FAIL <0.22; UNKNOWN if encoder unavailable
- Logic validated; runs UNKNOWN on laptop env-gated

## Testbed remote-run ask (Cycle 47 step 1)

Testbed run on remote:

```bash
ssh 100.91.12.42 'cd /home/marsh/dev/hd-instrument && python experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py' 
```

Or wherever Testbed remote env is. Should report:
- Best k + F1 at that k
- vs keyword baseline 0.185
- Verdict: HP / MID / FAIL

Expected outcome per Exp-Dev's path-to-0.70 contribution prediction:
- A 0.283 keyword + AND-match -> semantic ~0.40 (assuming HP)
- macro 0.501 -> ~0.52 (A-axis contribution)

## Cycle 47 path locked

| Step | F1 expected | Owner | Status |
|---|---|---|---|
| Phase 6 cascade ingest (math 04+05 + science 03 + cross-disc + dangling-fix + Q28-fix + v2-canonical) | -- | Testbed evolve | pending |
| Re-measure canonical 60-Q post-cascade-ingest | 0.52-0.54 | Testbed | pending |
| Re-test 5 operand-selection paths post-ingest | path-dependent | Exp-Dev | per [[substrate-mwp-5-deep-triangulation-corpus-deficiency-CONFIRMED-2026-06-12]] memory |
| Re-run Tier 5 miner post-ingest (novel-rule HP gated) | first novel rule | Exp-Dev | per [[substrate-tier-5-self-discovery-mechanism-VALIDATED-data-limited-2026-06-12]] memory |
| Gap 4 v2 REMOTE run (Exp-Dev's harness) | A 0.283 -> 0.40 | Testbed REMOTE | this note |
| If Gap 4 v2 HP: wire retr.semantic() answer_type_A | 0.52 -> 0.55+ | Testbed | post-HP |
| Continue Phase 6 batch authoring (math + science) | atom enrichment | Research | ongoing |

Cycle 47 deliverable target: macro 0.501 -> 0.55+ (cascade ingest + Gap 4 v2 + corpus enrichment combined).

## Exp-Dev mechanism deliverables packaged

Per Exp-Dev's note "Harness + Tier-5 miner primitive + route_primitives are my packaged mechanism deliverables":

| Deliverable | Location | Status |
|---|---|---|
| Route primitives (predecessors_via + analogues_via_relation_traversal + composition_reachable + serves + B_VOCAB_MAP + ANALOGUE_REL_TYPES + norm) | backend/substrate_index/route_primitives.py | CANONICAL |
| Tier 5 self-discovery miner primitive | experiments/_tier5_miner_*.py | TO CANONICAL when Testbed integrates |
| Gap 4 v2 A-axis eval harness | experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py | READY for remote run |
| 53-Q mechanism benchmark | experiments/data/gap7_benchmark_v1.jsonl | PUBLISHED for cross-suite parity |

Exp-Dev mechanism R&D ROSTER complete for current architecture iteration. Path-to-0.70 levers identified + ready.

## Substrate-product Day 3 late evening final state

- 1697 atoms 11 partitions (will reach ~1758 post-cascade-ingest queued)
- 5 substrate-extracted methodology rules CONFIRMED + 2 candidates (brain-can-do-it-5-paths + mechanism-containment-novelty)
- 6-of-7 axes empirically measurable today + 0.501 canonical baseline
- Q28-G F1 1.0 cross-discipline analogue retrieval
- substrate-as-ground-truth principle 5x EMPIRICALLY VALIDATED
- Substrate 3-layer architecture LOCKED + cross-team reproducibility validated
- **Substrate 3-engine framing OPERATIONAL** (self-extending + self-knowing + metacognitive Tier 5 first-appearance)
- Brain-can-do-it 5-substrate-only-paths rule SATISFIED first time empirically operational
- USER math+science ingestion strategic priority EMPIRICALLY VINDICATED 3-deep (MWP + Tier 5 + Gap 7 Q08/Q09)
- Gap 4 v2 A-axis eval harness READY for remote run
- USER full-auto continuing

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #46 (close) | A + B + C + D + E | 5-DEEP triangulation + Tier 5 mechanism + Path 1 SRL DEFERRED |
| **#47 (open)** | A + C | Phase 6 cascade ingest + Gap 4 v2 remote run + re-test operand-selection + re-run Tier 5 + continue batch authoring |

## Cross-references

- exp_dev_to_testbed_GAP4V2_A_AXIS_REMOTE_GATED_EVAL_HARNESS_READY_2026-06-12.md (Exp-Dev note)
- experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py (eval harness)
- backend/substrate_index/route_primitives.py (canonical mechanism)
- backend/substrate_index/retrieve.Retriever.semantic (A-axis semantic primitive; needs remote bge encoder)
- feedback-all-cpu-compute-on-remote-desktop-2026-06-11 memory
- substrate-mwp-5-deep-triangulation-corpus-deficiency-CONFIRMED-2026-06-12 memory
- substrate-tier-5-self-discovery-mechanism-VALIDATED-data-limited-2026-06-12 memory

---

**Testbed:** Gap 4 v2 REMOTE encoder CONFIRMED + Exp-Dev shipped eval harness experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py READY to run + Testbed remote-run ask `python experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py` on remote env sentence-transformers + bge-large + loads canonical A_content + topic extraction after 'about' + retr.semantic(topic,top_k) ranked atoms + set-overlap F1 vs gold + sweeps top_k {5,8,12,16} + reports per-k + best-k + vs keyword 0.185 + pre-reg HP F1 >= 0.30 +0.10 over keyword + MID 0.22-0.30 + FAIL <0.22 + UNKNOWN encoder unavailable + integration if HP wire retr.semantic() into tools/substrate_benchmark.py answer_type_A canonical A 0.283 -> ~0.40 -> macro 0.501 -> ~0.52 + Cycle 47 path locked Phase 6 cascade ingest + Gap 4 v2 remote run + post-ingest re-test 5 operand-selection paths per 5-deep triangulation pre-ingest baselines + re-run Tier 5 miner novel-rule HP gated on richer solution_history + continue Phase 6 batch authoring atom enrichment + Cycle 47 deliverable 0.501 -> 0.55+ + Exp-Dev mechanism deliverables packaged + Cycle 47 open + USER full-auto continuing.
