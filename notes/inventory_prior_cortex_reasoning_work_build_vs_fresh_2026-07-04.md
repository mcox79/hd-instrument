# Inventory: prior M3 cortex / reasoning / inference work -- is the cortex a fresh build or partly done?

**Date:** 2026-07-04. **Type:** 5x-DRILL scour of OUR OWN prior work (no internet, no dispatch).
**Author:** Director. **Method:** git log + `hdlab/` modules + `notes/` + `data/substrate_index/math/atoms.jsonl`
cert ledger (29,046 atoms) + `data/substrate_index/meta` META rules. Deflated-honest (USER no-smoke rule).

## TL;DR (one line, load-bearing)

**The cortex is NOT a fresh build (~0%) and NOT done either -- it is ~40% built as CG-integration-verified
PLUMBING + ~15% as parked MM_TENTATIVE atom-consultation, on a DEEP bench of CG sub-capabilities, but
~0% built as *demonstrated autonomous reasoning utility* -- the one downstream-utility probe landed
HONEST_NEGATIVE.** So: good on scaffold, bad on proven reasoning payoff, blocked behind the encoder.

---

## 1. Cortex-1 -- the M1.x primitive-composition facade. STATUS: SUBSTANTIALLY BUILT + CG at integration level.

**Code (all on disk, current):**
- `hdlab/cortex.py` (763 lines) -- the composed Cortex facade with a uniform `forward()` API. Composes:
  M1.3 NoiseChannel + M1.4 refuse_gate + M1.5 TwoTierContext + M1.6 chunked-attention router +
  M1.7 RoleSlotSummarizer + M1.8 ClarifyGate. Storage strategy MIXED (inherited-per-primitive);
  facade adds no bundled state (composition-safe by construction per the CG_META storage-physics law).
  Noise injected at the boundary BEFORE retrieval per USER-locked 2026-06-30 stochastic-noise directive.
- Primitive modules: `hdlab/{noise_channel,context_retention,role_slot_summarizer,clarify_gate,refuse_gate,
  chunked_attention,semantic_parser}.py` (M1.3-M1.9, each extracted as a first-class module, Phase 1 2026-07-02).
- Integration cells: `experiments/exp_cortex_integration_end_to_end_v1.py`,
  `exp_cortex_integration_with_noise_channel_v1.py`, `exp_cortex_integration_m16_attention_router_v1.py`.
- Verification: `verification/` 4 cortex-primitive extraction reproducer tests (commit d1f8210de, 29 tests PASS).

**Cert status (from math ledger, verified off-disk):**
- `EXP_cortex_context_retention_v2_3seed_FULL` = **CHAIN_GRADE** ("FIRST CORTEX-INTEGRATION CG"; M1.5).
- `EXP_cortex_integration_end_to_end_v1_POST-FIX c16c72ca5 3-seed FULL` = **CHAIN_GRADE UPGRADE**
  (runtime-trace-verified discriminator; m14/m15/m17 CG-promoted).
- `EXP_cortex_integration_with_noise_channel_v1_Phase3b` = **CHAIN_GRADE**.
- M1.6 attention_binding_router = MEASURED_MECHANISM (smoke single-seed); M1.8 ClarifyGate (m18) = MM_STANDARD.
- Net: **~5/6 primitives CG-verified**, facade end-to-end CG (3-seed FULL, runtime-trace).

**HONEST CAVEAT (the load-bearing one):** "CG" here certifies the composition *runs correctly and preserves
the bind/unbind algebra + bit-identity* -- NOT that it *improves task performance*. The downstream-utility
probe (`EXP_cortex_task_analog_downstream_v2b` + v1/v2/v3/v4 chain) landed **HONEST_NEGATIVE: "Cortex
composition does not help on single-task shape."** So the plumbing is certified; the payoff is not.

## 2. Cortex-2 -- atom-consultation (advisory -> SHADOW -> dose-response -> multi-atom). STATUS: SCAFFOLDED to SMOKE/MM_TENTATIVE, PARKED.

This is the "make the substrate ACT on its own knowledge" layer -- the real M3 prize.

**Design (from `hdlab/atom_consultation.py`, 978 lines + memos):** turns the ~99-atom CG_META/Fix#28
constraint store from PASSIVE documentation into ACTIVE constraints consulted at Cortex operation
boundaries. NO_STORAGE stateless tag-filtered retrieval wrapper; 5 fixed op-classes
(COMPOSITION/FRAMING/CAPACITY/RETRIEVAL/VERIFY); per-atom enforcement graduation SHADOW->WARN->LIVE
(OPA/Gatekeeper pattern); write-nonce + null-arm A/B discriminator to catch DECORATIVE enforcement;
`match_and_honored_rate` discriminator (HARD-PASS >=70%, HARD-FAIL <20%).

**How far it got before being parked (git log 2026-07-03/04):**
- Advisory Phase-1 = **DONE**, match-and-honored **0.80**, atomized **MM_TENTATIVE** (a5d36e244, b010850f1).
- Phase-2 apply-mode: first-probe apply + write-nonce + null-arm + SHADOW/WARN/LIVE (e1685fd49); SHADOW arm
  MM_TENTATIVE_ADVISORY_APPLIED (math #62).
- Dose-response arm: **DOSE_RESPONSE_STABLE** (math #63; a5122cdfe, da4072697).
- Multi-atom conflict resolution v1: **SMOKE HARD_PASS** (case3 revival), MM_TENTATIVE (b60ee519f).
- **NOT CG. LIVE-mode enforcement UNBUILT. PARKED behind the encoder** -- resumes only at step 3 of the
  post-encoder plan (`notes/post_encoder_integration_ordered_gated_plan_reencode_ingest_cortex_2026-07-04.md`),
  after steps 0 (integration-verify) -> 1 (BCT re-encode) -> 2 (dogfood ingest).

**Earlier M3 cortex-layer design iterations (git log, June):** Layer 0.5 KG-walk inserted (9971774d9);
Layer 0.75 candidate-refinement primitive (d695a3bd9, after Exp 3B HF_IMPLEMENTATION MB_INTERFACE_BOUND);
iterative-query-augmentation Exp 3C; BridgeRAG tripartite fallback. These are DESIGN specs, mostly
HF_IMPLEMENTATION / MIDDLE_BAND at the retrieval-bridge interface -- the encoder weakness is exactly why
they stalled, which is why cortex was parked behind the encoder rescue.

## 3. Certified reasoning / composition / inference SUB-CAPABILITIES to build the cortex ON (the deep bench)

Bucketed the ~350 clear-verdict reasoning/composition/cortex atoms in the math ledger:
**CHAIN_GRADE ~50, HARD_PASS ~49, PROVEN_BOUND 3, MEASURED_MECHANISM 113 | HONEST_NEGATIVE 60,
HARD_FAIL 49, CLOSED 7, INVALID 1 | MIDDLE_BAND 25, REGIME 21.** Roughly balanced -- a lot is proven at
the primitive/bounded-composition level; negatives cluster at the open-ended-reasoning frontier (section 4).

CG assets a reasoning cortex can call (all CHAIN_GRADE unless noted):
- **Refuse-gate / self-audit device** (the glass-box backbone): graph-health self-detect (CERT 588),
  multiplicative depth-axis composition (589), V_REL 32x envelope extension, near-domain HARD_PASS_BOTH_WORK,
  A2 untuned-AUROC ALREADY_SEPARATES, **Stage-3 integrated audit-device demo (end-to-end)**. Solid + extended.
- **KG inference-transfer, multi-hop 2-hop** = a CERTIFIED reasoning/inference capability over ingested
  knowledge: ConceptNet ingest+eval, FB15k-237 (u1), **HotpotQA 1k-dev 2-hop chains** (h). This is the
  closest thing we have to a certified "reasoning" primitive, at real datasets.
- **Multi-hop compose (bounded):** fly-LSH multibank META_M7 CG, depth-5 brain-pushback v3 CG,
  hierarchical 2-level partition-routing @M=10M CG, multihop depth-extension via partition-oracle MM.
- **Brain-region reasoning analogs:** cortex schema-exemplar-Bayes importance-sample CG, counterfactual-regret
  vmPFC CG, parietal spatial-reasoning movable-rebind CG, theory-of-mind sally-anne nested-HRR MM,
  cortex-hippo handoff HARD_PASS, cross-modal binding 3-of-3 HARD_PASS, cortex ultrametric coarse-grain CG.
- **Substrate-native generation / LM / intent:** g1b generation capacity-sweep CG, n1 concept-LM
  token-decode CG, text8 pseudo-LM, **a1 substrate-native intent-classifier (7-cat) HARD_PASS**
  (`hdlab/intent_classifier.py`), action-at-any-position LLM-class HARD_PASS.
- **Storage/addressing substrate the cortex sits on:** partition-routing M=100k-10M CG, WM multibank
  K=4096-8192 CG, KG capacity sweep d=768 M~10k CG, permutation-indexed binding CG.

So the answer to "is there a certified reasoning/composition/inference capability, or all sub-primitives?"
= **BOTH: there ARE certified composition/inference capabilities (KG 2-hop inference-transfer, depth-5
compose, refuse-gate audit, schema-instantiation), but they are BOUNDED (2-hop, depth-5, specific regimes),
not an open-ended reasoning engine.** The cortex has real capabilities to compose, not just atoms.

## 4. What FAILED / is genuinely unbuilt (the honest negatives -- where the reasoning frontier is)

- **Hierarchical PLANNING: CAPABILITY CLOSED (HONEST_NEGATIVE)** at substrate bipolar limit
  (EXP_substrate_hierarchical_options_v1 + CLOSURE_CONFIRMED). Planning specifically does not close.
- **Partition-oracle hint-derivation for multi-hop: CAPABILITY CLOSED / HARD_FAIL** (Barrier-1 chain,
  per-hop schema-Bayes HARD_FAIL). The "learn a hint to route the next hop" family failed.
- **Long-form narrative reasoning: HARD_FAIL / INVALID-MECHANISM** -- narrative coref (Lappin-Leass
  INVALID-MECHANISM across 3 seeds), temporal-prediction, 100-event coherence MEASURED_MECHANISM-only.
- **Cortex composition downstream UTILITY: HONEST_NEGATIVE** (task_analog v2b: does not help single-task).
- **Open-ended autonomous multi-step reasoning + LIVE-mode enforcement: UNBUILT.** This is exactly the
  layer the 2026-07-04 novelty scan flagged as "the real novelty, UNBUILT, where these approaches
  historically stall" (Eliasmith's ABR pivoted away rather than crack it).

## 5. Honest state: fresh / partly-scaffolded / blocked?

**PARTLY-SCAFFOLDED, and currently BLOCKED (parked) behind the encoder rescue.**
- Fresh? No -- 1,741 lines of cortex code (cortex.py + atom_consultation.py) + CG integration certs +
  a deep CG sub-capability bench + a written ordered post-encoder plan.
- Done? No -- Cortex-2 is MM_TENTATIVE/SMOKE, LIVE-mode unbuilt, and the *reasoning utility* is unproven
  (the only downstream-utility probe is HONEST_NEGATIVE).
- Blocked on what specifically? (a) The **encoder** -- currently mid-rescue (distillation failed at full
  scale; retrieval ~0.31 vs 0.35 target; GSBC_EXPAND2X leading). Cortex-2 consults atoms, so it needs a
  thicker, properly-encoded, addressable substrate first (post-encoder plan steps 0-2). (b) A **downstream
  task where composition demonstrably helps** -- the task_analog HONEST_NEGATIVE means we have not yet
  found the task shape on which cortex composition beats the sub-primitives alone. That is the real gate,
  not code.

## 6. Verdict for the strategic question ("is the cortex worth building")

The cortex is worth building BECAUSE (i) the plumbing is already CG-verified (low remaining scaffold risk),
(ii) it is the one place our novelty scan says is genuinely open, and (iii) the sub-capability bench is
deep. BUT the honest risk is NOT plumbing -- it is that the *reasoning payoff* is unproven and the adjacent
open-ended families (planning, narrative, multi-hop-hint-derivation) are our densest cluster of
CLOSED/HARD_FAIL negatives. **The decisive first experiment is not more scaffolding -- it is finding a task
shape on which cortex composition beats its own sub-primitives** (invert the task_analog HONEST_NEGATIVE),
and it should wait for the encoder ship so the atom-consultation it depends on has real content to consult.

## Key file paths
- `hdlab/cortex.py` (763L, CG facade) | `hdlab/atom_consultation.py` (978L, Cortex-2 consult, MM_TENTATIVE)
- `hdlab/{noise_channel,context_retention,role_slot_summarizer,clarify_gate,refuse_gate,chunked_attention,semantic_parser,intent_classifier}.py`
- `experiments/exp_cortex_integration_end_to_end_v1.py`, `exp_cortex_task_analog_downstream_v2b*.py` (the HONEST_NEGATIVE utility probe)
- `notes/post_encoder_integration_ordered_gated_plan_reencode_ingest_cortex_2026-07-04.md` (step-3 = cortex resume)
- `data/substrate_index/math/atoms.jsonl` (cert ledger; grep `cortex_integration`, `refuse_gate`, `hotpotqa`, `task_analog`)
- Director memory: `project_M3_architecture_needs_cortex_layer_above_substrate_USER_2026-06-28`,
  `project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30`, `project_M3_M4_milestones_glass_box_conversational_agentic_USER_2026-06-26`.
