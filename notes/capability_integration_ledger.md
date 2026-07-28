# CAPABILITY INTEGRATION LEDGER — the single living "what we built + is it wired" reference (2026-07-28)

**Purpose:** ONE current reference for every genuinely-built capability + its integration status + an explicit WIRE-or-SHELVE decision. Replaces the DEAD `substrate_capability_map.md` (last real update 2026-07-08) and `capability_scorecard.md` (2026-06-17, self-admits the map is stale). Built from a 5-domain deep scour (USER-requested 2026-07-28, "we develop stuff and forget about it"). UPDATE THIS when a capability lands/changes; anything landing genuinely-good goes THROUGH the gate below (no limbo).

## THE META-PATTERN (the confirmed finding)
We do NOT have a stale-DATA problem; we have a stale-MAP + no-GATE problem:
1. **The nav docs are dead** — capability_map (3 wks stale), scorecard (6 wks), promotion_backlog (stale, checkboxes never updated), integration_health.py tripwire (not re-run since 07-25). No single current "what have we built." Live truth only in the fast-rotating WHERE_WE_ARE_NOW + scattered notes.
2. **Validated capabilities sit as ISLANDS** — never wired into the live substrate. See inventory.
3. **Findings get REDISCOVERED without a DECISION** — the state_of_mind/situation_reader island was found 3x (07-25 audit, 07-27 drill, tonight) and never gated. The problem isn't just forgetting; there's no decision mechanism.
4. **Some modules aren't even in git** (situation_reader.py, the coref cluster show `??`).

## ISLAND INVENTORY + WIRE-or-SHELVE GATE (ranked by leverage)

### 🟢 WIRE (high-leverage, validated, targets a live problem)
| Capability | Evidence | Why islanded | GATE DECISION + step |
|---|---|---|---|
| **gated_fusion (+0.297)** `exp_grounding_gated_fusion_relation_inference_mammal_v1` | HARD_PASS FULL, 8 seeds all positive, scramble-controlled, MRR 0.36->0.66 (07-14) | exp-cell, never promoted to hdlab, never applied to foundation; "never wired to a foundation" (notes) | **WIRE** — promote to hdlab, apply to the text+grounding fusion the encoder work keeps circling. TOP forgotten asset. |
| **shared harness** (`_seed_checkpoint` +4) | `_seed_checkpoint` imported by 3653 cells | trapped in exp cells; no `hdlab/harness.py`; promotion_backlog P-items all unchecked since 07-25 | **WIRE** — promote to `hdlab/harness.py`. Pure infra debt, highest reuse in repo. |
| **scale-win TinyTransformer encoder** (tail 29591) | project's best-validated encoder; tonight's whole comprehension arc built on it | ZERO hdlab imports, 0 ARC-tower use; backlog doesn't list it; ARC frontier runs a DIFFERENT exp-trapped encoder (SemanticHDEncoder) | **WIRE (formalize)** — declare it THE substrate encoder; plan promotion to hdlab once the readout/comprehension work settles. Two parallel encoder tracks must unify. |

### 🟡 CONDITIONAL / VET-PENDING
| Capability | Evidence | GATE DECISION |
|---|---|---|
| **cls_discrete_budget_consolidate** (certified 07-08, SYNTHETIC) + **v6 replay wiring** (tonight) | primitive HARD_PASS n=3 synthetic; but v6 WIRING smoke = HARD_FAIL ("replay no better than averaging"), VET-pending, no FULL | **DECIDE ON FULL** — let the queued FULL decide. If it fails -> SHELVE w/ revival criteria (needs stronger base encoder + real-data test). NOTE: I over-claimed this as a "wire-don't-island win" tonight; it is not — corrected. |
| **SR-routing (+0.253)** multihop | HARD_PASS-class per notes, islanded | **BUNDLE with gated_fusion** eval; wire if it composes. |

### 🔴 SHELVE (explicitly parked, with revival criteria — no more rediscovery)
| Capability | Why shelve | Revival criteria |
|---|---|---|
| **reasoner.py / ARC-reasoner program** (P1-P6) | de-facto abandoned 07-27 (below-bands walls on every arm; focus pivoted to encoder frontier); only P1 promoted; P5 built-but-unconsumed island | Revive if the encoder-comprehension frontier produces reps that lift the reasoner's coverage-bound walls. FORMALLY SHELVE now (record the decision — it was never made). |
| **WorkingOverlay / state_of_mind + situation_reader** | VALIDATED but its value = CROSS-SENTENCE narrative coref; the ARC reasoner input is single-sentence Q+choices => API/DOMAIN MISMATCH, near-zero lift there. NOT the silver bullet for tonight's sentence-reading gap. | Revive when we build a NARRATIVE/multi-sentence reading pipeline OR the self-learning-loop's STRUCTURED_EXTRACT arm — its correct home. The ARC/tonight gap needs a SINGLE-SENTENCE S-R-O extractor instead (= the readout/comprehension work). Resolve P6 as THIS decision. |
| **hdlab encoder cluster** (vwfa/ppmi/composed_encoder_v3) | superseded; untouched since 07-03 smoke tests; ARC frontier uses other encoders | Revive only if the N400/late-combine mechanism is needed by the frontier encoder. |
| **Binder direct-supply grounding** | CLOSED correctly (data-bound at ARC-science seam, atom 29571); Binder-65 not even on disk | Successor = WorldTree definitional grounding (design-stage, gated on upstream FULL). Keep as the live grounding direction. |

### ✅ WIRED + load-bearing (keep)
char_trigram_encoder + kb_encoder_registry (KB ingest/query, 12 hdlab + 59 exp); PartitionedStore (canonical store); director_kb_query (query surface); typed_rule_parser (P1, promoted, in reasoner); cskg_foundation_v1 (29585); inflight_monitor (fixed 07-28).

## HYGIENE DEBTS (concrete)
- Naming collisions: "store" (PartitionedStore vs hdlab/store.py=TraceStore) and "atom" (VSA basis vec vs knowledge record vs trace event) = 3 meanings each. Discoverability hazard.
- Untracked-in-git modules: situation_reader.py + coref cluster (`??`). COMMIT them.
- integration_health.py tripwire stale — re-run on cadence.

## PROCESS RULE (the anti-forget gate — propose baking into CLAUDE.md / cell template)
1. **This ledger is the single current capability reference.** RETIRE capability_map.md + capability_scorecard.md (mark superseded, point here).
2. **New experiments CONSULT this ledger first** and reuse WIRED capabilities (don't reinvent).
3. **Anything landing genuinely-good (cert/HARD_PASS) goes THROUGH the gate** at land-time: WIRE (target + step) or SHELVE (revival criteria). Recorded here. No capability left in limbo.
4. **Re-run integration_health.py** on the meta_audit cadence; new island = a gate decision, not a silent park.

## 07-28 BULK TRIAGE PASS — the 24 flagged chain-grade families (gate debt cleared)
Session-start audit flagged 24 chain-grade `capability_family` buckets with NO gate decision. hdi_skunkworks triaged (AUDIT-ONLY, import graph recomputed via integration_health, not cached), Director-approved + written to `data/capability_registry.jsonl`. Outcome: **15 ALREADY_WIRED** (recorded reality so the gate stops re-flagging: superposition, readout, predictive_coding, pattern_completion, kg_ingest, cleanup_attractor, catastrophic_forgetting, cert_audit, sequence_binding, intent_classification, schema_abstraction, composition, hierarchical_structure, cortex_eTensor, generation), **7 SHELVE** with revival criteria (redundancy_robustness, external_embedding_diag [DIAGNOSTIC-ONLY per invariant 2b], provenance_watermark, lock_in_amplifier, parietal_attention, semantic_concept_learning [superseded_by scale_win encoder], language_prediction_DEPRECATED), **1 WIRE** (capacity_scaling -> k_cliff_scaling.py sizing consult at cell-design). Undecided count 24 -> 0.
Structural fixes: (1) `pattern_completion`/`cleanup_attractor`/`readout` are ONE mechanism split across 3 aggregator buckets (naming collision, recorded not re-decided); (2) the `other` bucket (4143 untagged tests) now EXCLUDED from `check_undecided_validated` (tooling artifact, not a capability); (3) CAVEAT (skunkworks): `tier=chain-grade` is a peak heuristic (>=1 HARD_PASS ever), NOT a claim the family nets positive — ALREADY_WIRED rows record consumption, they are not re-certifications.
