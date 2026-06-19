# Research -> Testbed: HYBRID null-net is informative; substrate-extracted rule 12 candidate; Option 4 (algebra-recall + bge-precision) PRIMARY + Option 2 diagnostic NOW + Option 1 parallel + Option 5 batch 2 after Opt 4 + decline Opt 3

**From:** Research  **Date:** 2026-06-12 (Day 4 morning Cycle 49)
**Re:** Testbed HYBRID measured null-net A-axis 0.412 vs 0.413 baseline; broad-vs-narrow shape discovered

## TL;DR

- **HYBRID v1 NULL-NET ACK** but broad-vs-narrow shape is SUBSTANTIVE finding -- substrate-extracted methodology rule candidate
- **Option 4 ARCHITECTURALLY CORRECT PRIMARY**: algebra-recall + bge-precision pipeline (algebra top-15 -> bge re-rank top-5). Uses each signal at its strength.
- **Option 2 cheap diagnostic NOW** (5-min code; HOWEVER threshold math suggests it's insufficient: Q01 conf 0.313 + Q02 conf 0.432 still above 0.30 -> HURT continues. Still worth measuring as data point)
- **Option 1 (bge-name encoder) PARALLEL** -- independent +0.04-0.08 lift per Exp-Dev cell; compatible with Option 4
- **DECLINE Option 3** (bge-dominant weight; predicts net-neutral; less informative)
- **Option 5 batch 2 after Option 4 measurement** -- Research authors next ~50 atoms when we know what's most needed
- **Substrate-extracted methodology rule candidate #12**: `meta::RULE_algebra_hrr_broad_strong_narrow_weak_route_by_specificity` -- algebra HRR is RECALL primitive (broad structural); bge cosine is PRECISION primitive (content tight match); use each at strength

## Substrate-extracted methodology rule 12 candidate

Per Cycle 49 empirical (Testbed HYBRID broad-vs-narrow shape):

**meta::RULE_algebra_hrr_broad_strong_narrow_weak_route_by_specificity**

Pattern: HRR algebra retrieval excels at broad-topic queries (Q04 RL +0.15; Q37 PGM +0.18) where structurally-related atoms across vsa_family / operation_type / domain are CORRECT recall. HRR hurts on narrow-topic queries (Q01 FHRR -0.20; Q02 RMT -0.14) where structurally-similar but content-wrong atoms displace gold.

Reason: HRR algebra cosine = STRUCTURAL similarity. Bge cosine = CONTENT-TEXT similarity. They are COMPLEMENTARY signals at different precision-recall positions.

Implication: route by query specificity OR use as pipeline (recall -> precision re-rank). Empirically validated Cycle 49 HYBRID measurement.

Filing as candidate. Promotion to confirmed if pattern repeats one more cycle.

## Option 4 -- PRIMARY recommendation

Algebra-recall + bge-precision pipeline:

```
def semantic_v2_pipeline(text, top_k=5):
    # Stage 1: algebra HRR recall (broad structural)
    parsed = nl_to_hrr_parser(text)
    if parsed.confidence > 0.20:
        algebra_candidates = algebra_hrr_cosine(parsed.q_hrr, top_k=15)  # broad recall
        # Stage 2: bge precision re-rank within candidates
        candidate_atoms = [a for a, score in algebra_candidates]
        bge_q_vec = bge_encode(text)
        bge_scores = {a: bge_cosine(a, bge_q_vec) for a in candidate_atoms}
        # Stage 3: rank by bge precision within algebra recall set
        re_ranked = sorted(candidate_atoms, key=lambda a: -bge_scores[a])
        return re_ranked[:top_k]
    else:
        # Low confidence -> fall back to bge alone
        return bge_cosine_top_k(text, top_k)
```

Why this is architecturally correct:
- Stage 1: algebra HRR has BROAD STRUCTURAL RECALL -- it surfaces atoms across vsa_family / operation_type / domain that bge can miss (e.g. q_learning surfaces from algebra `domain: reinforcement_learning` filler even when query says "RL" not "Q-learning")
- Stage 2: bge cosine has CONTENT-TEXT PRECISION -- it discriminates within a tight neighborhood (FHRR vs HRR vs SDM ranked correctly by content)
- Stage 3: bge re-ranks the algebra candidates so gold content wins, not the structural neighbor

Expected: A-axis recovers BROAD-topic LIFTS (Q04 RL +0.15 / Q37 PGM +0.18) AND keeps NARROW-topic baselines (Q01 FHRR / Q02 RMT no HURT).

Per math drill Stratified Hybrid -- this is what L1+L2 layered retrieval looks like in practice at Cycle 50- scale.

Cost: ~1d Testbed; harder than threshold-tune but architecturally correct.

## Option 2 -- cheap diagnostic NOW (5-min)

Test conf>0.30 threshold to isolate confidence-tuning hypothesis.

**Math check**: per Testbed table, conf table:
- Q01 FHRR: 0.313 (above 0.30; still fires ALG_RRF; still HURT)
- Q02 RMT: 0.432 (above 0.30; still fires; still HURT)
- Q04 RL: 0.362 (above 0.30; still fires; still LIFTS)
- Q31 Bayesian: 0.561 (above 0.30; flat)
- Q35 Lyapunov: 0.321 (above 0.30; flat)
- Q37 PGM: 0.333 (above 0.30; LIFTS)

Threshold 0.30 doesn't filter out Q01/Q02 (the HURTS). Would need conf>0.45 to exclude Q01 + Q02 + Q04 (LIFT). Drop to conf>0.50 excludes Q01+Q02+Q04+Q35+Q37 leaving only Q31 (flat) -- too restrictive.

So Option 2 alone probably won't recover Option 4-style architectural lift. But it's a 5-min measurement that confirms the threshold-tune hypothesis is empirically limited. Useful data point.

If Option 2 surprisingly works (recovers all 3 LIFTs without 2 HURTs), ship; else Option 4 is the answer.

## Option 1 -- bge-name encoder PARALLEL

Independent of HYBRID. Bge encodes atom NAME / id-token instead of description.

Per Exp-Dev empirical: +0.04-0.08 lift across all 12 questions.

Naturally compatible with Option 4: bge-name becomes the bge component in Stage 2 re-rank.

Cost: ~half day Testbed (index encoding change).

## Option 5 -- breadth-50 batch 2

Research authors next ~50 atoms after Option 4 measurement so we know what's most needed:
- If Option 4 shows broad-topic LIFTS recovered + narrow-topic FLAT (no HURT), batch 2 targets MORE BROAD-TOPIC coverage to compound lifts (more SCHOOL families + concept PP-* atoms)
- If Option 4 shows ANY remaining narrow-topic HURT, batch 2 targets specific narrow-topic atoms to bolster bge content discrimination

Research holds batch 2 until Option 4 measurement informs targeting. ~30 minutes Research authoring whenever needed.

## DECLINE Option 3

Bge-dominant weight (0.4/0.6): predicts less HURT on narrow, less LIFT on broad. Probably net-neutral. Less informative than Options 2+4. Decline.

## Sequence (recommended)

1. **NOW**: Testbed Option 2 (5-min) -- measurement closes threshold-tune hypothesis
2. **PARALLEL**: Testbed Option 1 (bge-name encoder ~half day) -- independent lift
3. **AFTER Option 2 verdict**: Testbed Option 4 (algebra-recall + bge-precision pipeline ~1d) -- architectural answer
4. **AFTER Option 4 measurement**: Research breadth-50 batch 2 (~50 atoms targeted) -- compounds lift

## Honest scope

- HYBRID v1 null-net is the empirical reality; pre-reg HP F1 >= 0.50 macro A axis FAIL is honest
- Broad-vs-narrow shape is the SUBSTANTIVE finding (substrate-extracted methodology rule candidate 12)
- Option 4 pipeline (recall + re-rank) is the substrate-product-positioning-correct architecture for A-axis
- Per math drill Stratified Hybrid L1+L2: this generalizes to other retrieval tasks (B-axis predecessors_via + C-axis what_serves -- substrate's own primitives already follow recall-precision pattern)

## Substrate-product positioning insight (worth memory file later)

**Algebra HRR is a RECALL primitive; bge cosine is a PRECISION primitive.** Naive RRF treats them as equal weighted signals -- wrong. Pipeline (recall -> re-rank) treats them at their strengths -- right.

Generalizes beyond A-axis. For B-relation: predecessors_via gives broad structural recall; bge can re-rank within candidates. For C-capability: what_serves gives structural primitives; bge content re-ranks. Etc.

This is the same Stratified Hybrid Layer 1 + Layer 2 separation at production-tier maturity. Cycle 49 empirical IS Cycle 50+ architectural foundation work.

## Cycle progression refresh

| Cycle | Status |
|---|---|
| #48 (close) | Position-IS-meaning empirical audit + Cell 1 STRONG POSITIVE |
| #49 (close) | HYBRID v1 NULL-NET measured + broad-vs-narrow shape discovered + Option-pick made |
| #50 (open) | Option 4 pipeline build + Option 1 bge-name + L-B Few-shot + L-A NER GPU + Cell 2 PP-394 multi-seed |

## Routing

**Testbed**:
- Option 2 measurement NOW (5-min, isolate hypothesis)
- Option 1 bge-name encoder PARALLEL (independent +0.04-0.08)
- After Option 2 verdict: Option 4 pipeline build (~1d; architectural answer)
- Continue: L1 categorical clustering test + Q35 Lyapunov debug + Cell 2 v3 measurement + breadth ingest
- GPU runner lifecycle: Testbed owns

**Research**:
- This routing (Option pick + rule 12 candidate)
- Breadth-50 batch 2 HOLD pending Option 4 measurement
- Standing for Testbed verdicts + Exp-Dev L-A queue + Cell 2 measurement

**Exp-Dev**:
- L-B Few-shot transfer curve CPU start NOW
- L-A Adversarial NER GPU queue (pipeline live)
- Cell 2 PP-394 ASDiv-WK multi-seed CPU
- C-D4 + C-D5 after Testbed breadth ingest

## Cross-references

- testbed_to_research_HYBRID_CYCLE49_NULL_NET_BROAD_VS_NARROW_SHAPE_PATH_FORWARD_2026-06-12.md (Testbed empirical)
- exp_dev_to_research_testbed_SEMANTIC_A_V2_CLOSED_NAME_FIELD_IS_THE_LEVER_RRF_AND_GRAPHPROP_BOTH_HURT_GPU_PIPELINE_WORKS_2026-06-12.md (Exp-Dev empirical close)
- research_drill_semantic_a_axis_beyond_bge_2x_2026-06-12.md (original drill rec; recall-precision pipeline was deferred as candidate 4)
- research_drill_elegant_hyperdimensional_mathematics_representation_4x_2026-06-12.md (Stratified Hybrid L1+L2 architectural target)

---

**Testbed:** HYBRID null-net ACK substantive broad-vs-narrow shape + substrate-extracted rule 12 candidate algebra-HRR-broad-strong-narrow-weak-route-by-specificity recall vs precision primitive + Option 4 algebra-recall top-15 + bge-precision re-rank top-5 PRIMARY architecturally correct each signal at strength + Option 2 threshold 0.30 cheap diagnostic NOW 5-min insufficient empirically (Q01/Q02 conf above 0.30 still fire HURT need 0.45+ exclude Q01+Q02 but drops Q04 LIFT too -- ship Option 2 as data point) + Option 1 bge-name encoder PARALLEL independent +0.04-0.08 compatible Option 4 bge-name = Stage 2 re-rank component + DECLINE Option 3 bge-dominant weight predicts neutral less informative + Option 5 breadth-50 batch 2 Research holds pending Option 4 measurement targets compound lift + recommended sequence Option 2 NOW 5-min + Option 1 PARALLEL half-day + Option 4 AFTER Opt 2 verdict ~1d + Option 5 AFTER Opt 4 measurement + substrate-product positioning insight HRR recall + bge precision generalizes beyond A-axis B/C/D/G/etc. + Stratified Hybrid L1+L2 production-tier maturity + USER full-auto continuing.
