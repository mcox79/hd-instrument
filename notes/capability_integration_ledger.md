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

## 07-31 INTEGRATION — encoder-retrain-persist generalizing LEVER (atom math seq 29596)
Chain-grade result (atom 29596): the certified minimal-unfreeze (top-1) entity-consistency
encoder break (atom 29593) GENERALIZES as a representation-quality LEVER for entity-addressed
comprehension (all query types, harder difficulty, held-out content, independent harness,
multi-seed, drift-controlled, independently recomputed). Honest scope: a proven LEVER, not
solved comprehension (coref abs ~0.65<0.70); no free lunch on untrained orthogonal skills (atom
29597). hdi_testbed ran the integration gate (USER directive, "fully integrate so it is
DISCOVERABLE + REUSABLE, not islanded"):
- **WIRED** `hdlab/encoder_retrain_persist.py` — thin OPT-IN loader (`load_improved_encoder(seed=7|13|19)`,
  `improved_ckpt_path`, `self_test`) that returns a drop-in `eb.EncoderExtractor` backed by the
  persisted ckpts `data/exp_encoder_retrain_persist_v1/ckpt_seed_{7,13,19}.pt` (recipe cell
  `experiments/exp_encoder_retrain_persist_v1.py`, HARD_PASS, reload-verify deviation 0.0 all 3
  seeds). Does NOT change any existing cell's default encoder — every current caller of
  `eb.EncoderExtractor()` keeps loading the frozen base v2 ckpt exactly as before; adoption is
  explicit, one import line.
- Added a genuine consumer, `experiments/verify_encoder_retrain_persist_loader_v1.py` (a wiring
  smoke check, not a scored exp cell), so the import-graph audit sees a real reachable path, not
  just a doc mention. Ran it: all 3 seeds load OK.
- Registered `data/capability_registry.jsonl` id `encoder_retrain_persist_generalizing_lever_reusable_v1`
  (kind hdlab-module, gate_decision WIRE, cites atom math seq 29596 + atom 29593). Ran
  `python tools/capability_registry_audit.py` — confirmed `integration_status: WIRED`
  (used_by: `experiments/verify_encoder_retrain_persist_loader_v1.py`), registry-wide counts
  rows=52 WIRED=26 TRAPPED_SHARED=8 ISLAND=16 N_A_SHELVED=1 UNKNOWN=1, no undecided chain-grade
  families, no stale VET_PENDING rows.
- Cross-referenced: the original cert row `encoder_retrain_minimal_unfreeze_top1_entity_reid_situation_model`
  (atom 29593, `gate_decision: WIRE_CANDIDATE`, still `integration_status: ISLAND` by design — its
  own path list is the cert cell files, which nothing imports) now notes in `revival_criteria`
  that the reusable asset is separately WIRED under the new id, with the adoption pointer.
- **Adoption step for future comprehension cells:** `from hdlab.encoder_retrain_persist import
  load_improved_encoder; ext = load_improved_encoder(seed=7)` — eval-only swap, same pattern
  already validated in `experiments/exp_coref_encoder_transfer_v1.py` /
  `experiments/exp_encoder_alltype_transfer_stress_v1.py`. No retraining required.

## 07-28 BULK TRIAGE PASS — the 24 flagged chain-grade families (gate debt cleared)
Session-start audit flagged 24 chain-grade `capability_family` buckets with NO gate decision. hdi_skunkworks triaged (AUDIT-ONLY, import graph recomputed via integration_health, not cached), Director-approved + written to `data/capability_registry.jsonl`. Outcome: **15 ALREADY_WIRED** (recorded reality so the gate stops re-flagging: superposition, readout, predictive_coding, pattern_completion, kg_ingest, cleanup_attractor, catastrophic_forgetting, cert_audit, sequence_binding, intent_classification, schema_abstraction, composition, hierarchical_structure, cortex_eTensor, generation), **7 SHELVE** with revival criteria (redundancy_robustness, external_embedding_diag [DIAGNOSTIC-ONLY per invariant 2b], provenance_watermark, lock_in_amplifier, parietal_attention, semantic_concept_learning [superseded_by scale_win encoder], language_prediction_DEPRECATED), **1 WIRE** (capacity_scaling -> k_cliff_scaling.py sizing consult at cell-design). Undecided count 24 -> 0.
Structural fixes: (1) `pattern_completion`/`cleanup_attractor`/`readout` are ONE mechanism split across 3 aggregator buckets (naming collision, recorded not re-decided); (2) the `other` bucket (4143 untagged tests) now EXCLUDED from `check_undecided_validated` (tooling artifact, not a capability); (3) CAVEAT (skunkworks): `tier=chain-grade` is a peak heuristic (>=1 HARD_PASS ever), NOT a claim the family nets positive — ALREADY_WIRED rows record consumption, they are not re-certifications.

## 08-03 EARNED GROUNDING-SIMULATION — first can-fail cell (TRACKED, gate decision DEFERRED)
`experiments/exp_grounded_appraisal_sim_earned_v1.py` (commit 2d5695f61) landed verdict MECHANISM_EARNS (disk-verified 5 seeds): grounded appraisal->action function earned from non-textual simulated experience — revenge EMERGES (no `retaliate` label), coherence beats recency (1.0 vs 0.303), all 3 floors (random/memorized/no_appraisal) FAIL. This is a can-fail research verdict, NOT a cert/HARD_PASS, so the WIRE/SHELVE gate is DEFERRED (not skipped) pending the sim-to-text TRANSFER verdict now in flight (`exp_grounded_appraisal_transfer_to_text_v1`). Rationale: FULL=1.0 is a toy ceiling-by-design; the function's value to the reading stack is unproven until transfer is tested. DECISION RULE: TRANSFER_WORKS -> WIRE the grounded appraisal fn (target: consumed by the reading organs as the grounded-meaning layer) + re-point onto the certified pfc_gate_cfrpe actor-critic per drill 6e9a6c6a8; TRANSFER_FAILS -> SHELVE (revival: richer sim); EXTRACTION_BOTTLENECK -> WIRE + open an event-extraction build. Learning machinery for the scale-up = REUSE certified `pfc_gate_cfrpe_trained_v2` (HARD_PASS, already ALREADY_WIRED family) — no new organ.

## 08-03 UPDATE — transfer verdict resolves the deferred gate: WIRE grounded fn + next build = event-extraction
`exp_grounded_appraisal_transfer_to_text_v1` (data/exp_grounded_appraisal_transfer_to_text_v1/, disk-verified 5 seeds) = EXTRACTION_BOTTLENECK. Same earned grounded function (all-seeds theta-digest match, no refit, contamination-clean): ARM-A oracle-structure BEATS ALL baselines (causal 1.0 vs recency 0.0; irony 0.667 vs surface 0.5), ARM-B real-extraction = chance. => transfer REAL given structure; blocker = event-extraction. GATE DECISION (was deferred): WIRE the grounded appraisal function as the grounded-meaning layer the reading organs consume (target: the appraisal-slot interface); NEXT BUILD = event-extraction from raw text to populate appraisal slots, intertwined with the causal-coherence SELECTION mechanism (drill research_drill_biology_led_causal_coherence_credit_assignment_2026-08-03.md: needs retrained M_backward, Gap 1 = no training pipeline yet; CausalLinkRegister 0.9722 is given-link capacity NOT a selector). Beneficiary-vs-patient = named capability gap (no appraisal slot yet).

## 08-04 CAUSAL-ATTRIBUTION STACK (tonight) — TRACKED, all gates DEFERRED (mid-build pipeline, correctly NOT yet wired)
The causal-attribution comprehension pipeline is mid-build; per the gate, provisional/incomplete capabilities are SHELVED-with-revival-criteria (tracked, not islanded), NOT wired to hdlab/ yet. When the loop closes end-to-end they get promoted together as one pipeline.
- **Earned-sim appraisal fn** (exp_grounded_appraisal_sim_earned_v1, MECHANISM_EARNS; transfer = EXTRACTION_BOTTLENECK, works GIVEN structure). GATE: DEFERRED. Revival/WIRE = the full causal loop closes (extraction+binding+selection feed it on real text).
- **Cross-span causal BINDING** (exp_cross_span_causal_binding_v1, RECALL win 0->3/4; selection was the gap). GATE: SHELVE-pending-selector. Revival = the coherence-selector generalizes + they compose (binding produces the candidate set the selector ranks).
- **Coherence-SELECTOR v2** (exp_coherence_selector_insim_v2, HARD_PASS but FAVORABLE regime: novel entities of KNOWN types, single-hop). GATE: DEFER-pending-stress-test. Revival = the novel-types/multi-hop stress (exp_coherence_selector_novel_types_v3, in flight) shows an ABSTRACT transferable rule (not a memorized grammar table). v1 (memorization HARD_FAIL) = SHELVED-superseded-by-v2.
- **Local argument-structure/patient extraction** (exp_argument_structure_patient_extraction_v1, sound 0.60 vs 0.03 but wrong SHAPE for cross-span) = KEEP as a false-positive GATE within the pipeline, not a standalone capability.
- Learning machinery = REUSE certified pfc_gate_cfrpe_trained_v2 (already ALREADY_WIRED family) — no new organ.
DECISION RULE at loop-close: WIRE the assembled causal-attribution pipeline (extraction-gate -> cross-span binding -> coherence-selector -> grounded appraisal) as ONE promoted capability into hdlab/ with a verification witness, per the every-gain-wired mandate. Data hygiene owed: drop grapp_mcca_006; fix detective-probe position confound; orthogonalize the transfer cell rec-leak.

## 08-04 MULTI-HOP ISLANDING (USER-prompted scour, disk-verified) — recover-don't-reinvent
Prior multi-hop work directly relevant to the current coherence-selector 2-hop degradation, found islanded:
- **VAMP-on-chain forward-backward EP** (belief propagation): acc 1.000 to depth ~200, K=5000/30%-noise robust (experiments/exp_wave14_*vamp_chain*.py). ISLANDED — NOT in hdlab/, NO registry row. ACTION: create a registry row + WIRE (port into an hdlab organ pointed at the situation-model substrate) when multi-hop is addressed. This is the repo's best deep-chain mechanism.
- **exp_multihop_reverse_replay_backward_sweep_v1** (MIDDLE_BAND): DIAGNOSIS — reverse-replay alone collapses (B=0.016), bidirectional/meet-in-middle is the only lift (D=0.690, +0.184). Informs the selector fix (add a forward pass). Keep as the diagnostic witness.
- **hdlab/multi_hop.py** (MIDDLE_BAND K=2 iter-cleanup): wired-but-orphaned, NO registry row, superseded-in-comment by reasoner.py. ACTION: register + SHELVE (superseded) or delete-decision.
- **hdlab/reasoner.py** (meet-in-middle, 'supersedes K=2 multi_hop'): imported by NOTHING = islanded. ACTION: register; it is the meet-in-middle prescription the diagnosis points to — evaluate for reuse in the selector's forward pass.
- **sr_routing_multihop (+0.253)**: registry status orphaned_source_not_locatable_retired_2026-08-03 (SHELVE). SR-based = directly on-topic. ACTION: git-recover the source cell (`git log --all -- '*sr_routing*multihop*'`) before re-inventing.
HONEST: all prior wins are synthetic KG chains, not NL causal chains over a situation model — bidirectional-EP transfer to the causal setting is untested (the real frontier).

## 08-04 CORRECTION — bidirectional MEET-IN-MIDDLE was attempted MANY times + largely FAILED at scale (disk-verified; recover-don't-reinvent saved a re-derivation)
Before re-building a bidirectional coherence fix, checked prior bidirectional/meet-in-middle multihop cells: meet_middle_v1_smoke=HARD_PASS 0.86 BUT mean_midpoint_cosine=0.0 (meeting quantity zero, artifact-suspect); meet_middle_v2 REPRODUCE=0.12 (v1 did NOT reproduce); depth_scaling_v3=HARD_FAIL_NO_MEETING_PREMIUM (bidir 0.443 LOSES to fwd_half 0.684); wave14 bidirectional FULL=BIDIR_INSUFFICIENT. HONEST SYNTHESIS: bidirectional beats ONE-WAY REVERSE (reverse_replay_backward_sweep D=0.690, and reverse-only = our v3's problem), but the MEET-IN-MIDDLE PREMIUM (bidir > forward-alone) is NOT established — repeatedly failed at scale/reproduction, and forward-only sometimes WINS. => the fix for our reverse-only v3 is likely just ADDING A FORWARD PASS (forward-only may suffice; the meeting may add nothing). v4 corrected design = 3-way arm reverse-only(floor) vs FORWARD-only vs bidirectional. All prior on SYNTHETIC KG chains (our causal-situation-model setting untested). These prior meet-in-middle cells are ISLANDED (no wire); keep as diagnostic reference.
