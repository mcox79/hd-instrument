# exp_dev hand-off -- research: inference acceleration alternatives

**Filed:** 2026-06-07 by research sub-agent.
**Trigger:** Research note d:/AI/hd-instrument/notes/research_drill_inference_acceleration_alternatives_2x_2026-06-07.md
**Pause state:** Check data/orchestrator_paused.flag before dispatch. If paused, hold all GPU/remote anchors.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Orchestrator does NOT specify numerical parameters.

---

## Context

CELL-SPECDEC returned 0.48x speedup (HARD_FAIL). Research drill confirmed this is a workload mismatch: all draft-verify and parallel-decode accelerations require >= 32 token outputs to amortize overhead. HotpotQA bridge QA mean is ~6 tokens. The 2x drill evaluated 14 standard inference acceleration techniques; all are either already applied (int4 quantization), irrelevant at short outputs, or throughput-side-only.

The high-leverage path identified: substrate-native bypass of LLM generation for queries that are directly answerable from retrieval. This is not a standard inference acceleration; it is a fast-path architectural change.

v1 latency at 1.23 sec/query is NOT a demo blocker (enterprise break-even = 0.3 QPS sustained; one replica is sufficient). Latency becomes a concern at v1.1 production deployment (>= 5 QPS).

---

## Anchor candidates (rank-ordered)

### Anchor 1: Substrate-direct-answer fraction probe (LOCAL CPU, fast)
- Pointer: Research note Section 6 Pre-test 1, Section 5 Direction 1.
- Substrate-product reading: if >= 30% of HotpotQA queries are answerable with F1 >= 0.50 from top-1 substrate retrieval alone, a fast-path that bypasses LLM generation is worth implementing. Expected: 50ms vs 1.23 sec for routed queries (10-25x speedup on that fraction).
- Tier hint: LOCAL CPU. ~1 hr wall. No GPU needed. Run substrate retrieval on HotpotQA dev set, measure top-1 F1 vs gold answers.
- Why now: cheapest possible signal. If HARD-FAIL (< 15% answerable), the entire LLM-bypass direction closes. If HARD-PASS, opens a new architecture lane before v1.1 planning.
- HARD-PASS pre-reg: >= 30% of queries with top-1 F1 >= 0.50.
- HARD-FAIL pre-reg: < 15% of queries OR median top-1 F1 < 0.20 on "answerable" subset.

### Anchor 2: Query routing by retrieval similarity threshold (LOCAL CPU, 30 min)
- Pointer: Research note Section 6 Pre-test 5, Section 5 Direction 3.
- Substrate-product reading: a zero-training threshold router using retrieval similarity score could identify "substrate-answerable" queries with high precision. If precision >= 0.80 at threshold 0.90, this becomes the routing gate for the fast path (Anchor 1) in production.
- Tier hint: LOCAL CPU. ~30 min wall. Threshold sweep on retrieval similarity scores; no training required.
- Why now: costs almost nothing; needed to validate the router before any fast-path implementation.
- HARD-PASS pre-reg: precision >= 0.80 at some threshold.
- HARD-FAIL pre-reg: precision < 0.60 at all thresholds (no reliable routing signal; fast-path cannot be safely deployed).
- Dependency: run after Anchor 1 (needs retrieval output from same run).

### Anchor 3: Flash Attention + CUDA Graphs baseline verification (LOCAL, 30 min)
- Pointer: Research note Section 3 items K and L.
- Substrate-product reading: Flash Attention 2 and CUDA Graphs are both free-to-try hardware optimizations. Flash Attn gives 0-20% if not already active; CUDA Graphs gives 5-15% at 6-token decode (Python launch overhead is proportionally larger at short outputs). Combined could push 1.23 sec to 0.95-1.05 sec with no architectural change.
- Tier hint: LOCAL. ~30 min. Add attn_implementation check + torch.compile call; measure single-query latency delta.
- Why now: zero cost; eliminates question of whether baseline is hardware-saturated.
- HARD-PASS pre-reg: latency drops to <= 0.90 sec/query.
- HARD-FAIL pre-reg: no measurable change (already active; baseline is already saturated at hardware level).

### Anchor 4 (CRAZY): Extractive span head on encoder representations (LOCAL CPU, ~2 hr)
- Pointer: Research note Section 6 Pre-test 4, Section 5 Direction 2.
- Substrate-product reading: train a 2-layer MLP span head on Llama-1B encoder embeddings to predict answer start/end span on HotpotQA gold contexts. If F1 >= 0.55 on single-hop subset, this is an LLM-free answer path (10-50ms vs 1.23 sec). Directly relevant to north star (functional system beats LLMs): substrate + 50M extraction model > 7B chat model on factoid QA.
- Tier hint: LOCAL CPU. ~2 hr wall (training + eval on dev set). No GPU needed for MLP head training.
- Why now: if it works, this is a major architectural finding. If it fails (F1 < 0.35), it closes the "encoder as extractor" direction cleanly.
- HARD-PASS pre-reg: extractive F1 >= 0.55 on single-hop HotpotQA subset.
- HARD-FAIL pre-reg: F1 < 0.35.
- CRAZY rating: HIGH. Non-standard architecture but theoretically grounded (SQuAD-era BERT extractive baseline as precedent).

### Anchor 5 (THROUGHPUT): vLLM continuous batching QPS measurement (REMOTE GPU, ~2 hr)
- Pointer: Research note Section 3 items E and F, Section 6 Pre-test 2.
- Substrate-product reading: measures actual production serving capability. At batch=10, if QPS >= 8, a single GPU handles 700K queries/day -- which covers the v1 break-even load with margin. If QPS < 4, the production serving architecture needs multi-GPU before v1.1.
- Tier hint: REMOTE GPU (needs real GPU to measure serving throughput accurately). ~2 hr. Use vLLM serve with HotpotQA query batch at sizes 5, 10, 20.
- Why now: v1.1 production deployment planning needs this number. It is not blocking v1 demo but IS blocking v1.1 architecture decisions.
- HARD-PASS pre-reg: QPS >= 8 at batch=10 on single GPU.
- HARD-FAIL pre-reg: QPS < 4 at batch=10 (forces multi-GPU deployment even at v1 scale).
- Note: single-query latency increase under batching is expected and acceptable; the metric here is throughput (queries/sec), not per-query latency.

---

## Context pointers

- Research note: d:/AI/hd-instrument/notes/research_drill_inference_acceleration_alternatives_2x_2026-06-07.md
- CELL-SPECDEC verdict: see recent verdicts / testbed results (0.48x speedup HARD_FAIL)
- North star: d:/AI/hd-instrument/memory/north_star_functional_system_beats_LLMs.md
- Production architecture (locked 2026-06-07): d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md
- Encoder distillation priority (v1.1): see MEMORY.md entry "Distilled 50M encoder stays as v1.1 priority"
- Post-compaction brief (afternoon): d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

## Contract section

exp_dev picks queue routing (LOCAL / REMOTE_CPU / REMOTE_GPU), designs anchor names, sets pre-reg bands, decides order. The ordering above is suggested by research (cheapest-first), but exp_dev overrides based on current queue depths and runner state. Anchors 1-3 are all LOCAL CPU / LOCAL and should not compete with GPU runners.

Anchors 4-5 are optional / CRAZY / throughput-planning respectively. Dispatch at exp_dev's discretion based on queue headroom.

## Autonomy declaration

exp_dev has full authority to:
- Reorder anchors based on queue state
- Skip Anchor 5 if remote GPU queue is full
- Combine Anchors 1+2 into a single script (they share the same retrieval run)
- Add a smoke gate to Anchor 4 (train on 100 examples first; full only if smoke F1 >= 0.40)
- Defer Anchor 5 to next cycle if v1 demo timeline is imminent
