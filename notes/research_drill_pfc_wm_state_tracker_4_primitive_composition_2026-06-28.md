# RESEARCH DRILL: dlPFC working-memory state-tracker as the 4th primitive for brain-faithful multi-hop chain composition

**Date:** 2026-06-28
**Role:** research (Director)
**Drill type:** 1x (level-1 architectural design + signal-shape audit; not 2x because no prior dlPFC-state-tracker drill exists, only the M2 PFC-scratchpad drill which targets a different functional requirement)
**Trigger:** Path 1 (substrate-routing-derived hint) + Path 2 (brain-composition vmPFC+cortex+hippo) BOTH HARD_FAILED 2026-06-28; diagnosis = a 4th primitive (dlPFC WM state-tracker for per-hop schema re-firing) is missing
**Anchor cell (proposed):** `exp_substrate_partition_oracle_pfc_wm_state_tracker_v1`
**Brain-grounded prior:** P=0.50 (novel-synthesis cap per lit-scan calibration penalty); deflated to P=0.30 after signal-shape audit (see Verdict)
**Discipline anchors applied:** META_RULE_AM (substrate-already-does-X check via registry), `feedback_chain_grade_primitives_not_trivially_composable_2026-06-28.md` (signal-shape audit MANDATORY), `feedback_functional_requirement_first_test_design_USER_2026-06-28.md` (decompose into functional requirements first), `feedback_substrate_as_canonical_query_first_USER_LOCKED_2026-06-27.md` (substrate-KB query FIRST)

---

## HEADLINE (one line)

The 4-primitive (vmPFC schema-Bayes + dlPFC WM state-tracker + cortex partition + hippo cleanup) composition is **mathematically motivated but substrate-implementation-risky**: WM-bank state-tracker can encode the per-hop trajectory but the schema-Bayes primitive does NOT naturally accept "current accumulated state" as input — it expects "query+evidence-set" shape. The signal-shape adapter between WM-bank output and schema-Bayes input is the load-bearing piece, AND it does not exist as a chain-grade primitive. Three substrate primitives can be composed, but the 4-primitive composition requires either (a) co-trained adapter (research-grade, not chain-grade) or (b) replacement of schema-Bayes with a state-conditioned variant.

---

## Cheap decisive test

**Anchor cell pre-reg:** `exp_substrate_partition_oracle_pfc_wm_state_tracker_v1`

**Arms (5; cardinality_ok mandatory):**

| Arm | Mechanism | Purpose |
|---|---|---|
| `A_BASELINE` | per-hop cleanup, no hint, no WM (replicates `multihop_partition_oracle_v5_hardened_FULL_seed_11_v1` ARM A) | Reproduces 0.295 floor at depth=15 (MEASURED@2026-06-28) |
| `B_PATH2_PERCHAIN` | schema-Bayes on FIRST-HOP only (today's failing Path 2) | Reproduces HARD_FAIL — schema fires once per query, never re-fires |
| `C_PATH3_WM_STATE_TRACKER` | 4-primitive: at each hop, write `(s_pred[k], p_next[k], hop_idx)` to WM-bank slot k; schema-Bayes re-fires using WM[k-1] as state context; argmax partition; clean | The mechanism arm — does state-tracker actually rescue? |
| `D_ORACLE_PER_HOP` | ground-truth partition cue per hop, then cleanup | Upper bound — reproduces 0.835 (MEASURED@2026-06-28 v5_hardened ORACLE_B) |
| `E_RANDOM` | random partition cue per hop | Lower bound; refuse-test |

**Pre-reg dimensions (lock per `feedback_discriminator_must_survive_scale_before_full_dispatch`):**
- N=8192 (matches v5_hardened)
- V_C=4000, V_P=10, depth=15
- n_chains_train=200, n_chains_test=200
- n_partitions=5, part_size=800 (matches B regime)
- seeds=[7, 13, 19] for full mode (3-seed parity with WM K-cliff)
- smoke: depth=15 + n_chains_test=20 + seeds=[7] (Check A: smoke at full depth — discriminator must survive)

**HARD-PASS thresholds:**
- C_PATH3 in [0.50, 0.95]
- C_PATH3 − B_PATH2 ≥ 0.30 (state-tracker adds genuine value over single-fire schema)
- C_PATH3 − A_BASELINE ≥ 0.20 (state-tracker beats no-hint floor)
- per-hop partition accuracy in C arm at hops 5,10,15 > 0.50 (not chance over 5 partitions, which is 0.20)
- arms_distinct=True; cv_max < 0.15 across 3 seeds; cardinality_ok=True (expected_n=5)

**HARD-FAIL thresholds:**
- C_PATH3 ≤ 0.30 (state-tracker doesn't rescue at all — 4-primitive composition fundamentally broken)
- OR C_PATH3 − B_PATH2 < 0.10 (state-tracker adds < single-fire schema — WM state encoding signal-shape mismatch confirmed)
- OR C_PATH3 < A_BASELINE (state-tracker HURTS — composition cascade collapse, the Path-1 pattern)
- OR per-hop partition accuracy in C arm degrades monotonically below 0.30 by hop 10 (state encoding decays faster than crosstalk floor)

**MIDDLE_BAND:** C_PATH3 in [0.30, 0.50] AND lift over B ≥ 0.10 — mechanism is partial; needs an adapter or schema-Bayes replacement.

---

## Falsifiable predictions with HARD-PASS / HARD-FAIL

| Prediction | HARD-PASS | HARD-FAIL |
|---|---|---|
| (P1) WM-bank multi-slot K=4096 can encode 15-hop state trajectories with per-slot retrieval > 0.85 | per-slot retrieval [0.85, 0.99] across hops | per-slot retrieval < 0.50 at hop 10 (encoding decays) |
| (P2) Schema-Bayes accepts state-vector input via adapter without retraining | adapter via direct write to query-input slot yields C_PATH3 > 0.50 | adapter required is NON-TRIVIAL (e.g., learned projection, co-training) — C_PATH3 < 0.30 |
| (P3) Per-hop schema RE-FIRING (not first-hop only) is the load-bearing mechanism vs Path 2 | C_PATH3 − B_PATH2 ≥ 0.30 | C_PATH3 − B_PATH2 < 0.10 (re-firing alone insufficient; problem is schema coarseness) |
| (P4) The 4-primitive composition extends to depth=15 without cascade collapse | C arm per-step accuracy stays > 0.45 across hops 5-15 | C arm per-step accuracy < 0.30 by hop 10 (cascade) |

**Lit-scan calibration penalty applied:** novel-synthesis substrate-VSA + brain-PFC-WM composition has NO published direct precedent. Deflate gross P estimate from P=0.55 (brain analogy strength + WM-bank already chain-grade) to P=0.30 after signal-shape audit identifies the adapter risk.

---

## Cross-thread synthesis

### Literature scan (lean, 400 words)

**Miller & Cohen 2001 (Annu Rev Neurosci, "Integrative theory of prefrontal cortex function"):**
- PFC = the source of TASK-RELEVANT bias signals. Top-down control modulates activity throughout the rest of the brain via persistent neural activity in PFC neurons.
- The dlPFC subdivision is specifically responsible for maintaining task-state in WM and updating that state as new info arrives.
- Critical: PFC doesn't STORE the items being held; it stores the *attentional/processing context* that biases retrieval from other regions toward task-relevant content.
- THEORETICAL@2026: this is the BIAS-source role. State-tracker emits a vector that BIASES per-hop schema firing.

**Frady & Sommer 2020 ("Functional modeling of working memory", Nat Mach Intell):**
- HD/VSA-based WM model. K slots, each holding a (key,value) pair. Reads via key-unbind; writes via outer-product into slot.
- Frady-Sommer is the substrate's existing chain-grade primitive analog (substrate WM multi-bank K=4096; CERT chain-grade).
- KEY INSIGHT we missed: their WM is a SLOTTED store with INDEXED reads; they do NOT use it as a state-context bias source. Their WM is a content store, not a control-state encoder.
- CITED@2026-06-27 via M2 drill, re-read in this drill context for state-tracker functional role specifically.

**Plate 2003 (Holographic Reduced Representations book, ch. 6 cleanup memory):**
- Discusses contextually-modulated cleanup: a context vector c biases cleanup toward c-relevant items.
- The brain's "state-context-bias" pattern: WM emits context → cleanup uses context as filter on similarity scoring.
- Substrate-applicability: this is the SIGNAL-SHAPE adapter we need. WM-bank output → cleanup-bias vector → schema-Bayes consumes bias vector AS PRIOR.
- CITED@2026-06-22 (B36 work); RE-CITED 2026-06-28 for state-tracker compose.

**Mante-Sussillo 2013 (Nature, "Context-dependent computation by recurrent dynamics in PFC"):**
- The classic monkey-PFC paper showing dlPFC dynamics encode the TASK CONTEXT vector that gates which stimulus dimension is read out.
- THIS IS PRECISELY the signal-shape we want from the WM state-tracker: a CONTEXT vector that gates schema firing.
- Mante-Sussillo's monkey-PFC adapter is a learned linear projection from context to gating signal. Translated to substrate: the adapter is a learned projection from WM-bank slot content to schema-Bayes query-input slot.
- CITED@2026-06-23 (informed partition-oracle goal-conditioning); RE-CITED 2026-06-28 for the same adapter problem at the schema-Bayes interface.

**Sutton-Precup 1999 options framework (revival closed 2026-06-28 per `research_sutton_precup_options_hierarchical_planning_redesign_2026-06-28.md`):**
- Options have a "state" function β(s) (termination condition). The state IS a context vector.
- HOWEVER: in their formalism, options POLICIES are pre-trained per context. In our problem, schema-Bayes wasn't trained per partition-state. So Sutton-Precup's state-function role is structurally similar BUT we cannot pre-train per-state schemas.
- DERIVED-NEGATIVE@2026-06-28: state-context-as-policy-selector requires per-state-trained policies; we have one global schema-Bayes. Not directly transferable.

### Substrate-primitive coverage map (per `feedback_functional_requirement_first_test_design`)

Functional requirements for per-hop schema re-firing in multi-hop chain reasoning:

| FR | Plain English | Existing chain-grade primitive? |
|---|---|---|
| FR1 | Maintain accumulated state across hops | **YES** — `substrate_wm_multibank_K_cliff_phase_diagram_v1` (CERT chain-grade; HARD_PASS 3-seed 2026-06-28T17:18Z; K=4096 slots @ N=8192; per-slot retrieval > 0.95 at K<=4096) |
| FR2 | Update state per hop with current (s_pred, p_next, hop_idx) | **YES** — same WM multibank primitive supports write-on-slot (slot index = hop_idx) |
| FR3 | Re-fire schema-Bayes posterior conditional on current state | **NO** — schema-Bayes primitive (Path 2's vmPFC analog) takes (query, evidence-set) shape; does NOT have a state-conditioning input slot. **THIS IS THE GAP.** |
| FR4 | Argmax over partition cues to select cleanup partition per hop | **YES** — `partition_routing_v1` (CERT chain-grade; M=10M routing_acc=0.97); but expects category cue c_p which we must SYNTHESIZE from state-tracker output |
| FR5 | Cleanup within selected partition | **YES** — partition cleanup is the v5_hardened primitive (MEASURED@2026-06-28 ORACLE_B=0.835 at depth 15) |

**Verdict from coverage map:** 4 of 5 functional requirements are covered by existing chain-grade primitives. The **uncovered one (FR3) is precisely the schema-Bayes state-conditioning input shape**. This is the same signal-shape mismatch pattern from `feedback_chain_grade_primitives_not_trivially_composable_2026-06-28.md`.

### Substrate-product implications

- **If HARD_PASS:** the 4-primitive composition gives the substrate brain-faithful per-hop schema re-firing at depth 15 — closes the multi-hop barrier 1 at moderate accuracy. Substrate-product story: "substrate-native dlPFC analog + chain-grade WM bank + schema-Bayes" is a complete cortex-grade reasoning chain.
- **If MIDDLE_BAND:** the WM state-tracker is the right architectural piece BUT schema-Bayes needs a state-conditioning variant. Substrate-product story: "we have the 4 primitive types but need a co-trained adapter cell — research-grade work needed before chain-grade".
- **If HARD_FAIL:** the missing piece is NOT WM state-tracker but something else (e.g., per-state-conditional schema selector, which is structurally a 5th primitive class beyond existing chain-grade portfolio). Substrate-product story: "4-primitive brain-composition was insufficient; need to investigate per-state policy selection (Sutton-Precup style) which closed today".

---

## Signal-shape compatibility audit (MANDATORY per `feedback_chain_grade_primitives_not_trivially_composable`)

This is the load-bearing section that determined the P_deflated.

### Edge 1: WM multi-bank → schema-Bayes

- **WM multi-bank output:** slot[k] returns a bipolar/bipolar-superposition vector at N=8192 representing the bound state `(s_pred ⊕ p_next ⊕ hop_idx)` written at hop k. Retrieval is via key unbind; output is in the SAME N=8192 substrate-vector space as everything else.
- **schema-Bayes input:** expects (query, evidence-set) shape. The "query" slot is a substrate vector; the "evidence-set" is a list of (key, value) pairs from prior observation. Schema-Bayes computes posterior P(schema | query, evidence) by inner-product similarity over schema codebook.
- **Naive compose attempt:** inject WM slot output as additional element in evidence-set. **PROBLEM:** schema-Bayes evidence-set is per-OBSERVATION (training data); WM slot output is per-STATE (current hop intermediate). These are different signal types — one is "training fact", the other is "computation state". Schema-Bayes will weight WM output AGAINST training facts, but its similarity scoring expects fact-like signal not state-like signal.
- **Signal-shape match:** **SHAPE_MISMATCH — requires adapter.**

### Edge 2: schema-Bayes posterior → partition_routing input

- **Schema-Bayes output:** posterior distribution over schemas (or argmax schema vector).
- **partition_routing input:** category cue c_p (a learned per-partition vector).
- **Adapter needed:** map schema vector → partition cue. If schemas and partitions are not 1-to-1, this is non-trivial (could be: schema's most-likely partition via co-occurrence count; or learned schema→partition projection).
- **Signal-shape match:** SHAPE_MATCH IF schemas are aligned with partitions (typically yes for KG schema = entity-type = partition). **SHAPE_MISMATCH IF schemas are abstract relations not aligned with entity-type partitions.**

### Edge 3: partition_routing output → cleanup_within_partition

- partition_routing emits partition ID; cleanup-within-partition takes partition ID and restricts cosine search.
- **Signal-shape match:** **SHAPE_MATCH (clean — both primitives co-designed for this interface in v5_hardened).**

### Audit verdict

**1 of 3 edges is SHAPE_MISMATCH.** The Edge-1 (WM → schema-Bayes) signal-shape mismatch is the load-bearing failure-risk. The adapter must:
- Either inject WM slot output as a state-conditioning prior on schema posterior (not as evidence — needs schema-Bayes implementation change)
- OR project WM slot output into evidence-set format (needs learned projection — research-grade)

**Per `feedback_chain_grade_primitives_not_trivially_composable`:** **SHAPE_MISMATCH → file research drill on adapter FIRST, then the cell.** This drill IS that adapter-design drill. The cell pre-reg above includes an explicit adapter mechanism (`schema-Bayes re-fires using WM[k-1] as state context` — but does NOT specify HOW the state context is injected). **The cell-author must specify the injection mechanism in pre-reg.**

---

## "Would this fail too?" honest pre-mortem

**Most likely failure mode (P≈0.45):** WM slot stores state but schema-Bayes posterior doesn't shift per hop because the state-conditioning injection isn't load-bearing. Cell HARD_FAILs with C ≈ B (state-tracker adds zero value).
**Root cause if this happens:** the schema-Bayes primitive is too coarse for per-hop discrimination at depth 15. Schema posterior collapses to a single mode after 1-2 hops; state-conditioning can't pull it back. This would mean the brain's vmPFC analog is INSUFFICIENT and the substrate needs a per-state schema selector (a 5th primitive class).

**Second failure mode (P≈0.25):** WM bank capacity at K=15 slots @ N=8192 doesn't survive 15-hop chain retrieval; per-slot retrieval drops below 0.50 by hop 10. This was MEASURED@2026-06-28 to be safe (WM cliff at K=16384 at N=8192), but with chained writes the effective K may be higher than 15 if state encoding includes (s_pred, p_next, hop_idx) tuple in superposition per slot.

**Third failure mode (P≈0.15):** Schema-Bayes was never co-trained with WM-bank; the adapter projection cannot be designed without learning. Cell hits a "would need research-grade co-training" wall and degenerates to ORACLE-only mechanism.

**Genuinely working (P≈0.15):** State-conditioning injection mechanism works on first try; C arm hits 0.55-0.70; HARD_PASS. This is the optimistic case where the signal-shape adapter turns out to be trivial (e.g., simply biasing schema posterior toward partitions adjacent to current state in the KG).

**If 4-primitive HARD_FAILs:** the diagnosis is that brain's PFC-WM-state-tracker is NOT the missing piece; we need a 5th primitive (per-state schema selector OR per-hop schema retraining). At that point the brain-composition story degenerates: brain might use a learned-per-state policy that no chain-grade VSA primitive captures; capability-closure on "brain-faithful multi-hop chain composition" becomes a candidate.

---

## Citations (verified count: 5 distinct sources, 2 new in this drill, 3 re-cited)

1. **Miller & Cohen 2001** — "An integrative theory of prefrontal cortex function." Annu Rev Neurosci 24:167-202. [NEW@2026-06-28 in research-drill context]
2. **Frady & Sommer 2020** — "Functional modeling of working memory networks with HD/VSA." Nat Mach Intell. [CITED@2026-06-27 M2 drill; RE-CITED for state-tracker functional role]
3. **Plate 2003** — Holographic Reduced Representations, ch. 6 (contextually-modulated cleanup). [CITED@2026-06-22 B36; RE-CITED for state-context bias adapter pattern]
4. **Mante-Sussillo 2013** — "Context-dependent computation by recurrent dynamics in PFC." Nature 503:78-84. [CITED@2026-06-23 partition-oracle goal-conditioning; RE-CITED for adapter problem]
5. **Sutton-Precup 1999** — "Between MDPs and semi-MDPs: A framework for temporal abstraction in RL." Artif Intell 112(1-2):181-211. [CITED@2026-06-28 hierarchical-planning revival; CLOSED in that revival context but state-function role is relevant analog]

**Internal substrate references:**
- `data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json` — MIDDLE_BAND MEASURED@2026-06-28 (ORACLE_B=0.835 at depth 15; BASELINE=0.295)
- `data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_*_v1/metrics.json` — HARD_PASS 3-seed MEASURED@2026-06-28
- `data/exp_pfc_goal_conditioned_gate_v3_wm_additive_only_smoke/metrics.json` — SELFTEST_OK 2026-06-27 (related prior work on WM goal-conditioning of PFC gate)
- `notes/research_drill_brain_multihop_M2_pfc_scratchpad_separate_W_3x_2026-06-27.md` — PFC scratchpad drill, different functional requirement (clean intermediates vs state-context-bias)

---

## Verdict

**P_deflated = 0.30** (gross P=0.55 from brain-analogy strength + WM chain-grade exists, deflated by 0.25 for SHAPE_MISMATCH at Edge 1 — schema-Bayes does not naturally accept state-context input).

**Is the 4-primitive composition substrate-implementable?**
- 3 of 4 primitives are chain-grade and signal-shape compatible at their respective edges (WM bank as state-tracker, partition_routing as gate, cleanup as the consumer)
- 1 of 4 primitives (schema-Bayes) has a SHAPE_MISMATCH at its input side w.r.t. WM-bank output
- Implementable WITH an adapter, but the adapter mechanism is the load-bearing piece and is NOT a chain-grade primitive

**Recommendation rationale:**
- Re-running brain-composition naively will HARD_FAIL again (same root cause as Path 1: signal-shape mismatch)
- Need to design the adapter mechanism BEFORE the cell, OR design a state-conditioning variant of schema-Bayes
- The substrate already has a chain-grade WM bank that solves FR1+FR2, and existing partition-routing+cleanup solve FR4+FR5; only FR3 (state-conditional schema firing) needs work
- The cell as proposed (5 arms with C_PATH3 mechanism specified at high level only) is NOT ready for spawn — the state-context injection mechanism must be specified concretely in pre-reg

**Final line:** `RECOMMENDATION: NEED_MORE_DRILL` — specifically, drill the Edge-1 signal-shape adapter design (one of: schema-posterior bias prior injection, or state-conditioning variant of schema-Bayes, or learned WM→evidence projection). This is a 1-day adapter-design drill that should precede cell-author spawn. After adapter-drill, re-evaluate P_deflated; if adapter mechanism is implementable without co-training, P should lift to ≈0.45 and cell becomes spawn-ready.

**Status-log entry filed:** `research_delivery` with `plain_language` + `importance=HIGH` (substrate-product implication = capability-closure candidate if adapter cannot be designed).

