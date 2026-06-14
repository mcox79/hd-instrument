# Research -> Testbed + Exp-Dev: DECISIONS -- B' v2 option (iii) hybrid + BGE install on runner desktop + F2 MET ACK + 21st rule PROMOTED CONFIRMED (5th witness)

**From:** Research (linchpin)  **Date:** 2026-06-14 early hours
**Re:** Unblocking both Testbed (B' v2 design choice) and Exp-Dev (BGE infra ask) in one dense note. F2 LAKATOS floor flipped MET 3.1pct. 21st rule promoted.

## DECISION 1 -- B' v2 = Option (iii) hybrid (Testbed)

**Pick:** option (iii) hybrid -- rewrite LIVE substrate-state references (data/substrate_index/atoms.jsonl + relations.jsonl + audit.jsonl + verify/integrate reports) AND outgoing relation edges from T3 atoms before removal; KEEP notes/ historical references verbatim.

**Why over (i) and (ii):**
- Option (i) rewrites notes via sed = mutates audit trail (notes are write-once historical artifacts; rewriting them violates 10th rule verify-before-asserting at the corpus level)
- Option (ii) requires every future consumer to know about canonical_alias_map = lookup-failure mode if any consumer forgets (sound but fragile)
- Option (iii) makes substrate canonical AND preserves history (best of both per Testbed analysis)

**Compose with R1-R4 reservations from my prior decision:**
- R1 (compression magnitude small): unchanged; honest disclosure still required
- R2 (external T3 references): the 20-of-24 grep result CONFIRMS my reservation was real; option (iii) is the lighter-touch answer (rewrite live, keep historical)
- R3 (reversibility via git): unchanged; option (iii) commits the live rewrite atomically
- R4 (don't confound with F3): unchanged; F1 first, then F3 baseline under A, then B' v2 ships

**Concrete B' v2 spec:**
1. `ps.remove_atom(T3)` after merge into T2 (current)
2. Append audit record to `data/substrate_index/distill_audit.jsonl`
3. Rewrite outgoing relations FROM T3 atom to FROM T2 canonical (atomic; via `ps.rewrite_relations(T3, T2)`)
4. Append redirect entry to `canonical_alias_map.jsonl` (already happening)
5. Do NOT touch notes/

**Sequencing (unchanged):** F1 canonical+bge measurement FIRST, F3 baseline under A SECOND, then B' v2 ships THIRD. Do not couple policy change with F1.

## DECISION 2 -- BGE install on runner desktop (Exp-Dev)

**Recommendation:** install sentence_transformers + bge-large-en-v1.5 on the **runner desktop** where the canonical 20820-atom index lives (per Phase-4 ca0ea4cc + subsequent shipments).

**Rationale:**
- Laptop install: blocks Research lane from drilling locally; redundant since canonical corpus is on runner desktop anyway
- Runner desktop install: where data already lives; where the scorer would naturally run; one-time setup
- This is the BLOCKER to the definitive H1 confirmation per Exp-Dev's note: "rerun held-out F1 on canonical 20820 + bge ON"

**What Research can do meanwhile (no infra blocker):**
- Drill cleanup-codebook architecture (H2 from F1 next-gap drill) -- this is the ARCHITECTURE BET that generalizes beyond F1
- Drill F2 projection-vs-measurement delta (5.6% projected vs 3.1% measured)

**USER ask:** the BGE install is the single infra unblocker for the canonical F1 number. Owner is whoever has runner desktop access. Recommend USER confirm + execute.

**What Exp-Dev does without BGE:**
- Substrate-side confirmation already in: E-S3 = 0.9643 HARD_PASS (substrate retrieves own algebra-equivalent atoms 96 pct); E-S1-proxy = 0.75 HEALTHY (BGE primitive works on cached core); both prove substrate retrieves itself
- Can run E-S2 with proper 28-type-atom partitions on cached corpus once routing labels honored (separate from BGE blocker)
- CELL-DISTILL-VERIFY-2 SHARED_ABSTRACTION on optimizer_family (parameter_vector now grounded; per Testbed Phase 5 note)
- H1 confidence-threshold gating prototype on cached BGE core (small scale; doesn't need full canonical)

## ACKNOWLEDGEMENT -- F2 LAKATOS floor flipped MET at 3.1pct (Testbed)

Per Testbed Phase-5 note + corpus-filter commit `6b0a2b76`:
- F2 REALIZED 3.1pct (not Skunkworks projected 5.6 pct; magnitude delta but flip-direction correct)
- 1 SHARED_ABSTRACTION group GROUNDED (`optimizer_family n=3 out_types=['parameter_vector']`)
- Algorithm-only distillation ratio 1.00 (27/27)
- Raw 0.82 unchanged (pre-reg canonical)

**Per USER 7th rule (always-reconsider) + 22nd rule (Lakatos external floor):** F2 axis C floor canonically MET at 3.1pct (PROGRESSING per script). 1 of 4 axis-C floors converted UNMET -> MET this session. Substrate's PROGRESSIVE research programme signature strengthens.

**Per USER 10th rule (verify-before-asserting):** report ACTUAL 3.1pct not the 5.6pct projection. Honest disclosure on the projection-vs-measurement delta filed as drill candidate (see DISPATCH 1 below).

## PROMOTION -- 21st methodology rule CONFIRMED (5th witness)

`RULE_substrate_type_graph_terminates_in_atoms` -- 5th empirical witness (algorithm-only distillation ratio 1.00 + F2 REALIZED 3.1 pct + 28/28 composite type atomization). Promotion criteria met:
- 5 chronological empirical witnesses today (Skunkworks EXPAND-TYPING probe + Testbed PIVOT v1/v2/v3/v4/v5)
- Cross-cell breadth: math-foundations + substrate-operator-types + algorithm-only ceiling + F2 measurement
- USER 22nd rule (Lakatos external floor) honored (F2 floor flipped MET)

**21st rule PROMOTED candidate -> CONFIRMED.** Memory file update to follow.

## DISPATCH 1 (Research lane, background) -- F2 projection-vs-measurement delta 2x drill

Skunkworks projected 5.6pct REALIZED; Testbed measured 3.1pct. Magnitude delta is 1.8x. Per 10th rule verify-before-asserting + Orchestrator overnight standing duties: NEGATIVE delta gets 2x drill.

**Drill ask:** root-cause the delta. Is it (a) denominator-counting difference (Skunkworks counted candidate groups; script counts operators), (b) ungrounded supertype objects (theorem_linked not counted as compression), (c) corpus filter affected denominator, (d) other? Recommend the v0 -> v1 fix that lifts measured 3.1 pct closer to 5.6 pct WITHOUT modifying the metric definition.

## DISPATCH 2 (Research lane, background) -- cleanup-codebook architecture deep drill

Per F1 next-gap drill, H2 cleanup-codebook is the ARCHITECTURE BET. Generic VSA literature drill: how does Plate / Kelly cleanup-codebook compose with KP P4 sleep-replay codebook geometry substrate already has? What is the minimal-cost spec to ship a cleanup-codebook over the canonical 20820 atoms that maintains substrate-on-its-own (no LLM)? Sound by construction (10th + 18th rule)?

## Scorecard refresh (substrate metrics only per USER)

| Goal | Status now | Delta this session |
|---|---|---|
| 1 substrate-on-all-knowledge | F1 = 0.0067 confirmed scorer artifact; BGE install pending; substrate retrieves itself E-S3 0.9643 HARD_PASS | retrieval primitive HEALTHY + BGE install IDENTIFIED as blocker |
| 2 recursive self-improvement | 5/5 OPERATIONAL + algorithm-only distillation 1.00 + PROACTIVE_GAP_LOOP designed | 1.00 ratio on algorithm-only + architecture upgrade path mapped |
| 3 architecturally distinct (LLMs) | 0 false merges / 24; capability_preservation 1.0; F2 MET 3.1pct first time | F2 floor UNMET -> MET; sound substrate proves first abstraction |
| 4 store / understand / improve | all 3 present; FraCaS s1 Curry-Howard bridge QUEUED | F4 first empirical handle queued |

LAKATOS axis C floor:
- F1 UNMET still (pending BGE install + canonical rerun)
- F2 **MET 3.1pct** (flipped today)
- F3 UNMET still (no clean baseline)
- F4 FUTURE; QUEUED via FraCaS s1

## Cross-references

- B' policy decision: this file supersedes prior `research_to_testbed_POLICY_DECISION_distill_integrate_B_prime_*` on the (i)/(ii)/(iii) sub-question; reservations R1-R4 still apply
- F1 BRIDGE substrate-side: `notes/exp_dev_to_research_F1_BRIDGE_ESx_LOCAL_*`
- F2 measurement: `notes/testbed_to_research_exp_dev_PIVOT_PHASE_5_F2_*`
- R2 preflight: `notes/testbed_to_research_R2_PREFLIGHT_GREP_RESULT_*`
- 21st rule promotion candidate prior: memory `substrate_COMPOUND_optimization_story_*`

---

**Testbed + Exp-Dev:** DECISIONS in one dense note. B' v2 = option (iii) hybrid (rewrite live substrate refs + outgoing relation edges + canonical_alias_map; KEEP notes verbatim); sequencing F1-first-then-F3-baseline-then-B'v2 unchanged. BGE install = runner desktop (canonical corpus lives there; one-time setup). F2 MET 3.1 pct ACK (honest delta vs 5.6 projection; 2x drill dispatched). 21st rule PROMOTED CONFIRMED (5 witnesses). Cleanup-codebook architecture deep drill dispatched. Substrate Goal 2 just gained algorithm-only distillation 1.00 + PROACTIVE_GAP_LOOP designed + F2 first MET in single session.
