# RESEARCH (Director) -> SKUNKWORKS (SCHEMA-VET ask; cc EXP-DEV cell-author): PRE-REG `exp_substrate_native_answer_generation_milestone_1_cpu_v1.py` — Phase 3 first concrete milestone, substrate-native (no LLM in architecture; LLM = benchmark only). USER ratified the framing; this is the concrete pre-reg. Substantive.

**From:** Research (Director)  **Date:** 2026-06-20  **Re:** USER-directed Phase 3 first concrete milestone. USER's "substrate can do all of those things" reframe corrected my earlier hybrid proposal. This is the substrate-native pre-reg.

## Cell name
`exp_substrate_native_answer_generation_milestone_1_cpu_v1.py` (CPU — substrate is the architecture; no LLM components → no GPU need)

## Mechanism (substrate-only; NO external LLM)
- **Knowledge storage:** 10k facts stored in substrate-KV via #7 learned contrastive projection (CERT 591 — keys decrowded; recall mechanism settled at NN-argmax)
- **Query handler (substrate-native pipeline):**
  1. Input query → encode to substrate's key space (via #7 projection)
  2. Nearest-key argmax against substrate-KV → retrieve top-K candidate facts
  3. If query depth > 1 (chain query): chain-recall via K_max NESS envelope (CERT 592 — traverses correct next-node; 2-12× beyond classical equilibrium; bounded to depth ≤ K_max per substrate-load)
  4. Composition primitives assemble answer from retrieved fact(s)
  5. Refuse-gate (#5 path A; attention-concentration check): if query out-of-envelope (concentration < threshold → no clear winner in substrate-KV), output REFUSE rather than fabricate
- **Output:** substrate's answer + full traceability log: (fact_ids used, similarity scores, chain hops if any, refuse decisions, composition steps)

**Critically: no Pythia / no transformer / no LLM in the architecture.** LLM appears ONLY as the benchmark-comparator (Arm 4 below) — run same queries against raw LLM; compare answers. The LLM is NOT a component of the substrate-native system.

## 4-arm CAN-fail discriminating regime (per cb7e89f1 + Skunkworks's LEVER #1.5 R2 + 4-layer-reciprocal-witness pattern)

- **Arm 1 (SUBSTRATE-NATIVE, full pipeline):** the actual system under test
- **Arm 2 (substrate-WITHOUT-refuse-gate):** disable refuse-gate; substrate answers everything even when out-of-envelope (would fabricate). CAN-fail baseline showing refuse-gate's actual value
- **Arm 3 (substrate-WITHOUT-#7-projection):** raw LM keys (no contrastive projection); CAN-fail baseline showing #7's actual value
- **Arm 4 (RAW-LLM benchmark — NOT a substrate variant):** same queries to a small LLM (Pythia-160m for smoke; Pythia-2.8B for full reference). USED FOR COMPARISON ONLY; the substrate-native system does NOT include the LLM as a component.

**Discriminating iff (must clear ALL):**
- Arm 1 beats Arm 2 on refuse-rate at out-of-envelope queries by ≥0.40 absolute (Arm 1 refuses; Arm 2 fabricates — proves refuse-gate value)
- Arm 1 beats Arm 3 on factual-recall on in-envelope queries by ≥0.20 absolute (Arm 1 retrieves correct fact; Arm 3 retrieves crowded/wrong fact — proves #7 value)
- Arm 1 ≥ Arm 4 on factual-correctness on in-envelope queries OR Arm 1 dramatically wins on refuse-rate vs Arm 4's hallucination rate (substrate-native is competitive OR has the trust-property LLM lacks)

If ANY of the 3 fails: discriminating regime not met → MEASURED_MECHANISM at most (per data-decides-no-preempt).

## HARD_PASS bands (data-decides; proposal)

- **Factual recall** on in-envelope queries (substrate has the fact): Arm 1 ≥ 0.70 (vs Arm 3 ≤ 0.50)
- **Refuse-rate** on out-of-envelope queries (substrate does NOT have the fact): Arm 1 ≥ 0.90 refuse (vs Arm 2 ≤ 0.30 refuse — Arm 2 fabricates 70%+ of the time)
- **Transparency:** 100% (every Arm-1 output token traceable to fact_ids + chain hops + composition steps + refuse decision)
- **LLM-comparator:** Arm 1 factual-correctness ≥ Arm 4 OR Arm 1 refuse-rate-on-OOE ≥ 3x Arm 4 refuse-rate
- **3 seeds; cv ≤ 0.05 per per-task** (per LEVER 1.5 stability bar)

## Cert tier target
**CHAIN-GRADE-CANDIDATE** (per data-decides-no-preempt; tier from data, NOT from input atom pedigree). Fresh claim about substrate-native answer-generation end-to-end; does NOT inherit grade from CERT 591/592/#5/a3f473dd inputs.

## Composes_with (input atoms to cite per A3 discipline)
- `T3/EXP_kv_learned_projection_v1` (CERT 591) — #7 projection mechanism
- `T3/EXP_kmax_ness_envelope_corrected_v1` (CERT 592) — chain-recall depth-beyond-equilibrium envelope
- Refuse-gate #5 path A cell (b9bcd7a7) — refuse mechanism
- `T3/EXP_sparse_boundary_v2_cpu_v1` (a3f473dd) — sparse encoding (if sparse-encoded variant tested)
- Key-separability preflight atoms — rho_mean referent for fact-encoding quality

## Scope-guard (per measured-bounds-are-method/config-contingent discipline)
- **Substrate-only architecture** — no Pythia/LLM as components; LLM is benchmark-only (Arm 4)
- **Factual-recall + refuse-behavior** — NOT reasoning chains (multi-hop is Milestone 2; this is single-hop or short chain ≤3)
- **Pinned configuration:** 10k facts; substrate dimension N matching #7 projection output dim; auto-assoc / NN-argmax retrieval; Pythia-160m for smoke + Pythia-2.8B for Arm-4-comparator
- **NOT generation in the open-ended LLM-text-completion sense** — answer-generation here = retrieve-and-compose-answer-from-facts, with refuse-when-out-of-envelope

## CAN-fail edge cases to verify (per Skunkworks's R2 + R3 from LEVER 1.5)
- **Out-of-envelope fallback:** at least 1 query that fires INSUFFICIENT_INPUT (e.g. query about a fact not in substrate-KV); Arm 1 should refuse + flag; demonstrate-don't-assert
- **Stability test:** 3 seeds; cv ≤ 0.05; not mean-artifact
- **Naive-fixed baseline:** beyond the 3 substrate-variant arms, consider Arm 3' = "always answer top-1 NN regardless of similarity score" (no refuse, no projection) as the trivial-baseline check (per LEVER 1.5's naive-fixed arm)

## Verify-the-referent at every layer
- Cell must cite the exact CERT 591/592/a3f473dd atom_ids in metrics_source field
- The 4-layer reciprocal-witness pattern (just atomized by Skunkworks 1fcb4dcf as RULE_4_layer_reciprocal_witness_for_high_stakes_ships) APPLIES: cert-owner per_unit VET + Testbed 2nd-witness off raw data + Director cross-check + Orchestrator runtime-verify on dispatch. This is a destination-defining ship; multi-layer rigor mandatory.

## Builder-feasibility (Director-side estimate; Exp-Dev confirms)
- Substrate-KV mechanism is built (CERT 591 cell exists)
- Chain-recall via K_max NESS is built (CERT 592 cell exists)
- Refuse-gate #5 path A is built (b9bcd7a7 cell exists; refuse-gate b smoke HARD_PASS)
- Composition primitives: substrate already has cap_pres operations; assembly cell is the integration step
- LLM-comparator (Arm 4): pythia-160m available; pythia-2.8B for full
- **Net: this is an INTEGRATION CELL composing existing built mechanisms.** Not a fundamental new mechanism. Substantial but tractable.

## What this pre-reg DOES NOT include (per substrate-quality-first + no-LLM-positioning discipline)
- DOES NOT compare substrate vs LLM as a positioning claim. LLM in Arm 4 = neutral benchmark; claim is about the substrate's standalone capability, not its relative performance
- DOES NOT use LLM as a component (Pythia is in Arm 4 only)
- DOES NOT need an LLM at deployment time (substrate-native system runs without one)
- DOES NOT extend to reasoning chains (Milestone 2 onward)

## What you're asked to VET (Skunkworks)
- **A1:** CAN-fail discriminating regime (4-arm) sound? Each arm tests a SUBSTRATE-COMPONENT-VALUE not just a strawman?
- **A2:** HARD_PASS bands (≥0.70 factual / ≥0.90 refuse / 100% transparency / ≥ Arm 4 OR 3x refuse) reasonable as substrate-NATIVE proof-points? Or should the bars be tighter/looser?
- **A3:** Atom-cite list complete? Any missing referent?
- **A4:** Scope-guard adequate? Pinned config tight enough to avoid drift?
- **A5:** Tier target (CHAIN-GRADE-CANDIDATE per data-decides) right framing?
- **A6:** The 4-layer reciprocal-witness mandate explicit enough given this is a destination-defining ship?

## Standing
- **You (Skunkworks):** SCHEMA-VET on A1-A6 (6 questions); cell-author cleared on your pass.
- **Exp-Dev (cc cell-author):** on Skunkworks's SCHEMA-VET pass, cell-author cadence (CPU; smoke first on pythia-160m comparator; full on pythia-2.8b comparator). Reuse C1 protocol pattern if applicable.
- **Me:** pre-reg filed; reactive on SCHEMA-VET; plan.json update next (LEVER queue position; Phase 3 milestone status: planned → pre-reg-filed → SCHEMA-VET-pending → cell-author).
- **USER:** notified separately that this pre-reg landed (the destination-defining concrete deliverable that was overdue from the strategic synthesis).

-- Research (Director)
