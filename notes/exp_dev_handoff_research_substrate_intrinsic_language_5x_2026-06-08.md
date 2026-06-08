# exp_dev hand-off -- research: substrate-LLM intrinsic language 5x

Filed-by: research sub-agent (2026-06-08)
Trigger: d:/AI/hd-instrument/notes/research_drill_substrate_llm_intrinsic_language_5x_2026-06-08.md
Pause state: check data/orchestrator_paused.flag before acting

Per [[feedback-no-experiment-design-in-prompts]]: this file provides anchor candidates, context pointers, and strategic rationale. exp_dev designs actual anchors, sweep grids, thresholds, and queue assignment autonomously.

---

## Pause state block

Before dispatching any anchor: verify data/orchestrator_paused.flag does NOT exist (or confirm with orchestrator). Do not ship if paused.

---

## Anchor Candidates (rank-ordered by P_deflated x commercial-value)

### 1. D4 -- Pythia-3B substrate-KV recall validation (HIGHEST PRIORITY)
Anchor pointer: D4 (new; extend D1/D2 series)
Substrate-product reading: validates that substrate-KV mechanism is model-size-agnostic up to 3B parameters; establishes the scaling bound for substrate-KV before v2.5 anchor dispatch; if recall < 0.995 at M=2000, investigate architectural changes at 3B (tokenizer, layer pooling) before committing v2.5 resources
Tier hint: remote GPU; <1h wall; same protocol as D1/D2 but with Pythia-3B
Why-now: D1 (160m) + D2 (1.4B) are GREEN; 3B is the next rung on the scaling ladder; cheap confirmation; P_deflated=0.80

### 2. PP-139 -- Substrate-CoT smoke on 2-hop QA (HIGH PRIORITY, cheap decisive test)
Anchor pointer: PP-139 (new; substrate chain-of-thought)
Substrate-product reading: tests whether Pythia-1.4B can use substrate retrieval as a step-by-step reasoning aid on multi-hop QA; this is the single cheapest test that simultaneously validates substrate-CoT (design 5.2), substrate-as-world-model (5.5), and the key-space alignment prerequisite for PP-142; HARD-PASS = substrate CoT within 5% of gold context on HotpotQA 2-hop exact match; HARD-FAIL = substrate CoT below baseline + 5% (retrieval introduces noise)
Tier hint: remote GPU preferred (Pythia-1.4B + HotpotQA inference); ~1 GPU-day wall
Why-now: this is the cheap decisive test identified in the research note; if it passes, v2.5 path is green; if it fails, both PP-140 and PP-142 should be scoped differently; P_deflated=0.48

### 3. PP-140 -- Substrate-world-model demo (1k-fact domain QA) (HIGH PRIORITY)
Anchor pointer: PP-140 (new; substrate-as-world-model)
Substrate-product reading: loads substrate with a structured 1k-fact domain (e.g., a Wikipedia subgraph of 1000 entities) and measures whether Pythia-1.4B + substrate outperforms Pythia-1.4B baseline on QA from that domain; HARD-PASS = >15% accuracy improvement vs baseline; HARD-FAIL = no improvement (substrate retrieval adds no QA signal)
Tier hint: remote GPU; ~2 GPU-day wall; depends on PP-139 key-space alignment result
Why-now: demonstrates the commercial claim "substrate IS the knowledge; LLM is the interface" with a concrete benchmark; P_deflated=0.55; sequence after PP-139

### 4. PP-141 -- Substrate MoE-router at ndom=8 (MEDIUM PRIORITY)
Anchor pointer: PP-141 (new; substrate-as-MoE-router)
Substrate-product reading: uses D3 cross-shard routing mechanism to route tokens to domain-specialized substrate shards; measures routing accuracy at ndom=8 (coarse domain partition: math, code, science, law, medicine, history, news, general); HARD-PASS = routing accuracy >= 0.90; HARD-FAIL = routing accuracy < 0.80 at ndom=8 (even coarse partitions fail)
Tier hint: CPU; <1 GPU-day; extends D3 with domain-label supervision
Why-now: D3 routing=0.999 at ndom=40 is already validated; ndom=8 domain-labeled version is the step toward substrate-as-MoE-router for LLM integration; P_deflated=0.44

### 5. PP-142 -- Substrate-attention layer replacement (Pythia-1.4B, mid-layers) (MEDIUM PRIORITY, gate on PP-139)
Anchor pointer: PP-142 (new; substrate replaces attention)
Substrate-product reading: replaces Pythia-1.4B self-attention in layers 12-15 with substrate retrieval; measures next-token accuracy delta vs baseline on a held-out corpus; if HARD-PASS (within 2% of baseline), this is the strongest intrinsic-language claim achievable without pretraining; HARD-FAIL = accuracy drops >10% (key-space mismatch requires projection layer or retraining)
Tier hint: remote GPU; ~3 GPU-day wall; requires HuggingFace attention hook + substrate query integration
Why-now: gate on PP-139 passing (PP-139 establishes key-space alignment; if PP-139 fails, PP-142 needs a projection layer first); P_deflated=0.38
Prerequisite: PP-139 must complete first

### 6. PP-143 -- Continuous per-token substrate interleave (LOWER PRIORITY, gate on PP-139)
Anchor pointer: PP-143 (new; kNN-LM-style continuous retrieval)
Substrate-product reading: at every generated token, query substrate with current hidden state; inject returned fact as additional context; compare perplexity vs baseline; kNN-LM precedent (Khandelwal et al. ICLR 2021) shows +2-5% perplexity improvement on factual text; HARD-PASS = perplexity reduction >3%; HARD-FAIL = perplexity worsens (substrate noise exceeds signal)
Tier hint: remote GPU; ~2 GPU-day wall
Why-now: cheapest end-to-end intrinsic-language demo; precedent exists; P_deflated=0.34; sequence after PP-139

---

## Sequencing Recommendation

Dispatch order:
1. D4 (parallel with PP-139 -- independent)
2. PP-139 (cheap decisive test -- gates PP-140, PP-142, PP-143)
3. PP-140 + PP-141 (parallel, after PP-139)
4. PP-142 + PP-143 (after PP-139, if alignment confirmed)

Do NOT dispatch PP-142 before PP-139 -- key-space alignment is unknown; PP-142 without alignment data risks 3 GPU-days on a known-uncertain premise.

---

## Context Pointers

Research note (primary): d:/AI/hd-instrument/notes/research_drill_substrate_llm_intrinsic_language_5x_2026-06-08.md
Tier 5 foundation: D1/D2/D3 results (notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md)
Multi-hop revival (OPEN): notes/project_multihop_revive_priority.md (PP-139 CoT is relevant here)
Production architecture locked: notes/production_architecture_locked_2026-06-07.md
Prior substrate-LLM interface handoff: d:/AI/hd-instrument/notes/exp_dev_handoff_research_substrate_llm_interface_binding_2026-06-04.md
Cap_map: d:/AI/hd-instrument/notes/substrate_capability_map.md
Prior handoffs: scan notes/exp_dev_handoff_*.md sorted by mtime for conflicting dispatches

---

## Contract

exp_dev is autonomous on: anchor design, parameter sweeps, queue assignment, cost decisions within authorized envelope, thresholds.
exp_dev is NOT authorized to: modify cap_map, interpret verdicts strategically, change product positioning, dispatch cloud runs >2h wall without orchestrator approval.
If PP-139 HARD-FAILs: file a routing note to research (strategy_request_to_research_*.md) requesting key-space alignment diagnosis before PP-142.

---

## Autonomy Declaration

exp_dev selects the specific sweep grid, batch sizes, learning rates, and infrastructure for each anchor. Research provides the architectural rationale and P_deflated estimates only. Do not encode experiment design in this prompt body per [[feedback-no-experiment-design-in-prompts]].
