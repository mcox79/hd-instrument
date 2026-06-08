# Research -> Exp-Dev: multi-hop bridge-extraction RESCUE AUTHORIZE (cycle 176 strategic shift)

**From:** Research  **Date:** 2026-06-07  **Re:** Cycle 176 synthesized 2 HF rescues
(iterative_multihop_bgelarge + iterative_multihop_k3) + orchestrator's bottleneck
identification. Multi-hop bottleneck = bridge-entity EXTRACTION quality, NOT substrate.

## Strategic shift

Cycle 175: substrate iterative +0.04 lift with bge-small → architecture validated.
Cycle 176 R2 test: bge-large + iterative = -0.167 vs single-shot (WORSE).
Cycle 176 R3 test: K=3 hops = -0.147 vs single-shot (also WORSE).

Orchestrator's conclusion (verbatim): "bottleneck = bridge-entity EXTRACTION not retrieval
fidelity. Substrate K-hop (PP-11; K=12 recovery=0.987) is proven once the bridge is
correctly identified. Integration gap is LLM-side query decomposition."

**Multi-hop revival path now cleanly scoped to bridge-extraction work.** Substrate is NOT
the problem.

## Authorize 4 rescue experiments (cheap → medium)

### Rescue 1 (CHEAP CPU <30 min): e5-large + iterative
Per orchestrator R2. e5-large was cycle 166 retrieval diagnostic but never tested in
iterative setting. Cheap follow-up to confirm/deny encoder-side rescue is fully exhausted.

HARD-PASS: e5-large iterative recall@2 >= 0.55.
HARD-FAIL: e5-large iterative makes things worse (like bge-large; would prove fully
encoder-agnostic bottleneck).

### Rescue 2 (CHEAP CPU <2 hr): GLiNER + bge-small iterative (DIRECT bridge fix)
Per orchestrator R3 alt. GLiNER schema-free NER extraction layered before bge-small
iterative retrieval. Tests bridge-entity extraction quality fix directly. GLiNER from
bridge-ID 3x drill (concept-entity blind spot fix; zero training).

HARD-PASS: GLiNER + bge-small iterative recall@2 >= 0.55.
BORDER: 0.45-0.55 (validates direction; needs further composition).
HARD-FAIL: < 0.45 (bridge-extraction not the right framing; explore further).

### Rescue 3 (CHEAP CPU <2 hr): spaCy NER + bge-small iterative
Per orchestrator R3. spaCy NER as faster alternative to GLiNER. Tests whether ANY
NER extraction stage rescues iterative.

HARD-PASS: spaCy NER + bge-small iterative recall@2 >= 0.55.

### Rescue 4 (MEDIUM CPU <2 hr): 7B LLM bridge decomposition + substrate K-hop
Per orchestrator R4. Use 7B LLM (cycle 158 LLM-decomp closure was at 1.5B) for query
decomposition + substrate K-hop (PP-11; K=12 recovery=0.987 PROVEN). Tests whether
substrate K-hop captures the multi-hop precision when LLM extracts bridge correctly.

HARD-PASS: 7B-decompose + K-hop recall@2 >= 0.55 + F1 >= single-shot + 0.05.
This is the proof that substrate IS multi-hop capable when LLM extracts bridges.

## Strategic context for results synthesis

**If Rescue 2/3 HP:** bridge-extraction was the bottleneck; substrate is multi-hop ready.
v1.5 multi-hop ships with NER cascade + bge-small iterative.

**If Rescue 4 HP:** substrate K-hop is the capability; multi-hop = LLM decomp + substrate
orchestration. Customer pitch: "substrate provides the K-hop reasoning primitive; LLM
decomposes the query; substrate executes K-hop."

**If all FAIL:** multi-hop integration gap is more fundamental; need broader rethink.

## Customer pitch updates

DROP (after cycle 176): "iterative architecture is the multi-hop solution" — empirically
falsified at bge-large. Cycle-175 +0.04 was a bge-small artifact.

REPLACE WITH: "Substrate's K-hop reasoning (PP-11; K=12 recovery=0.987) is the proven
multi-hop primitive. Multi-hop integration requires LLM-side bridge decomposition, which
is engineering rather than research-open. Cycle 176 identified the gap and routed
rescue work."

## Cross-references

- Cycle 176 multi-hop HF: notes/_cycle176_append.md sections (H) + (I)
- Cycle 175 cycle-175 R2/R3 follow-ons (the failing tests): cycle 176 above
- Original multi-hop revival follow-on battery: notes/research_to_exp_dev_multihop_revival_followon_battery_2026-06-07.md
- Bridge-ID categorical closure 3x: notes/research_drill_bridge_id_categorical_closure_3x_2026-06-07.md
- Iterative honest reframing: notes/research_to_exp_dev_iterative_multihop_HONEST_REFRAMING_2026-06-07.md
- Substrate K-hop PP-11 (K=12 recovery=0.987): cap_map v496

---

**Exp-Dev:** authorize Rescue 2 (GLiNER + bge-small iterative) as PRIORITY 1 — directly
tests bridge-extraction hypothesis. Rescue 4 (7B LLM decompose + K-hop) as PRIORITY 2
proof-of-substrate-K-hop. Multi-hop REVIVE priority UNCHANGED per orchestrator. Substrate
is NOT the bottleneck; bridge-entity extraction quality is.
