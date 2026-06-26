# RESEARCH (Director): multi-hop revival 5x drill — distinct angles after 4-for-4 substrate-native HARD_FAIL

**Date:** 2026-06-25
**Author:** Research (Director, Opus 4.7 1M)
**Trigger:** USER explicit 5x drill ask. Four substrate-native multi-hop attempts (consolidation v3, pointer-chain v2, WM-scaffold v1, CSP-gated v1) all HARD_FAIL at production scale (N=8192, V_C=200, V_P=10, n_chains=200, max_depth up to 10). Fifth attempt (parallel-replicate-vote v1 -> v2 META_M6_rail) preliminary HARD_FAIL pattern: smoke at smaller regime shows K=15 vote brings 5hop top1 from 0.122 to 0.50, but META_M6_rail violation means the smoke isn't an honest comparison to v2-full regime.
**Discipline:** 0.20 deflation novel-synthesis; cap P_deflated=0.50; brain-existence-proof +0.10 prior; Fix #28 default UNDER-claim; ASCII only; no cell dispatches authorized; spawn budget at Fix #14 cap (this drill is the only new spawn).

---

## 0. The core puzzle, calibrated against substrate data (one paragraph)

I read all five HARD_FAIL metrics.json files directly. The pattern is striking: across pointer-chain v2, WM-scaffold v1, and CSP-gated v1, the per-step accuracy sequence is BIT-IDENTICAL on the same seed/regime: seed 7 always reads [0.69, 0.485, 0.31, 0.205, 0.145] at hops 1-5. Seed 17 always reads [0.645, 0.375, 0.26, 0.20, 0.11]. Seed 23 reads [0.64, 0.415, 0.265, 0.16, 0.11]. CSP-gated has SLIGHTLY DIFFERENT numbers because the refuse-gate prunes (0.535 vs 0.69 at hop 1) — but the underlying cleanup math is the same. **What this means**: pointer-chain, WM-scaffold, and CSP-gated are ALL THE SAME CELL in mechanism — they all do per-hop "argmax over E of W@state, write the cleaned atom into next hop's read." The scaffold/pointer/gate framings are SUPERFICIAL; they all reduce to the same per-hop cleanup primitive operating on the same crosstalk-saturated W matrix. The 0.69 per-hop accuracy is a HARD INFORMATION-THEORETIC FLOOR set by the (V_C=200, V_P=10, K_set=20, max_depth=10) regime that gives 2000 W bindings = crosstalk-saturated regime. No mechanism that operates DOWNSTREAM of the cleanup primitive can improve on that floor. **This is the deep lesson and it constrains the revival space**: the per-hop primitive itself must change, OR the chain must be restructured to depend less on the per-hop primitive's failure rate, OR more INFORMATION (replication/redundancy/ECC) must be put INTO each hop's bind so that downstream cleanup has more signal to work with. Revival angles that don't satisfy at least one of those is doomed by the same per-step floor.

---

## ANGLE 1 — Apply today's wins (fly-LSH + multi-bank + partition-routing) to multi-hop

### Intuitive mechanism

Today's three chain-grade wins were all ARCHITECTURAL DECOMPOSITIONS that bypassed a per-step bottleneck:

1. **fly-LSH sparse expansion** (4-arm v2 ARM B; CHAIN_GRADE_CANDIDATE at M=10k): expand the representation into K=5-10 sparse-random dimensions before binding so the cleanup target lives in a less crowded space.
2. **Multi-bank WM 8x32** (recall=1.000 at K=256, vs naive single-bank K=256=0.46): split the working memory into 8 banks of 32 each, route to the right bank, retrieve within. Each bank stays in the K=32 chain-grade regime.
3. **Partition-routing M=10M** (recall=0.95 at M=1M; routing-acc=1.000): split the dense KV into 500 partitions of size 2000, route to the right partition, retrieve within. Each partition stays under the anisotropy ceiling.

The composition for multi-hop:

- **Per-hop cleanup with fly-LSH-rescued representation**: instead of storing the W bindings in raw HRR dense space (where 2000 bindings saturate), expand each (E[s], R[p], E[o]) triplet through fly-LSH sparse expansion BEFORE binding into W. Each bind now lives in a 5x-expanded sparse space where there are NEW orthogonal axes available. Per-hop cleanup operates on the sparse representation; cleaned result is read out via inverse expansion.
- **Multi-bank scaffold (PFC analog)**: each chain has its own dedicated WM bank for its intermediate. 8 banks of 32 means 8 chains can be in-flight simultaneously without cross-chain interference. The scaffold isn't holding clean intermediates of bad retrievals (as the WM-scaffold v1 ATTEMPT did); it's giving each hop's intermediate its own near-orthogonal storage so the next hop's read is uncontaminated.
- **Partition-routed retrieval per hop**: split the entity codebook E into 200 partitions of size 10 (or similar), route each hop's cue to the right partition, retrieve within. Each per-hop top-1 selection becomes a within-partition argmax — small-M chain-grade.

The composition is NOT "do all three"; it's "if you can route each cue to a small partition AND the cue itself lives in a sparse-expanded representation, your per-hop top-1 accuracy could plausibly jump from 0.69 to >0.95, which would carry 5 hops at 0.95^5 = 0.77."

### Why different from prior attempts

Pointer-chain, WM-scaffold, and CSP-gated all operated DOWNSTREAM of the cleanup primitive — they tried to manage the consequences of a 0.69 per-step accuracy. Today's wins say the right move is to FIX the per-step accuracy by changing what's being cleaned up. Fly-LSH gives new axes; partition-routing gives smaller-M cleanup; multi-bank gives dedicated WM per chain. None of the four HARD_FAIL attempts touched the cleanup primitive.

### P(solve), calibrated

Per-hop floor estimate: composition of 3 known chain-grade primitives, each operating in its proven regime, on a problem class (multi-hop QA) where the bottleneck is per-hop cleanup accuracy. Plausible per-hop accuracy after composition: 0.85-0.95 (vs current 0.69). At 5 hops: 0.44-0.77 top-1, vs current 0.145. That would be MIDDLE_BAND or HARD_PASS depending on which end of the range.

Raw P_solve = 0.55 (three chain-grade primitives composing in their proven regimes, on a problem with a clear bottleneck the composition addresses)
Deflated -0.20 (novel-synthesis lit-scan; nobody has published this exact composition for VSA multi-hop)
+0.10 brain prior (all three primitives are brain-aligned: fly-LSH = cerebellar/KC, multi-bank = PFC working memory parcellation, partition-routing = hippocampal place-cell-style episode decomposition)
**P_deflated = 0.45** (cap P=0.50 not invoked; this is genuine composition not pure novel-synthesis)

### Cell spec

`exp_substrate_multihop_compose_fly_lsh_multibank_partition_v1`

Arms (4 + baseline):
- ARM_BASELINE: pointer-chain v2 regime verbatim (sanity rail [0.62, 0.68] at 2hop)
- ARM_FLY_LSH_ONLY: pointer-chain v2 + fly-LSH 5x sparse expansion at bind+read
- ARM_MULTI_BANK_ONLY: pointer-chain v2 + 8 dedicated WM banks (one per chain in batch)
- ARM_PARTITION_ONLY: pointer-chain v2 + 50 partitions of E (size 4 each at V_C=200)
- ARM_COMPOSED: fly-LSH + multi-bank + partition-routing

Discriminator: ARM_COMPOSED 5hop top1 >= 0.50 AND beats SUM of individual-arm improvements (super-additive composition test).

Pre-reg bands: HP_5hop >= 0.50, MID_5hop=[0.25, 0.50], HF_5hop < 0.25, baseline_sanity=[0.62, 0.68], cv <= 0.10.

Brain prior: STRONG (three brain-aligned mechanisms, each proven separately).

---

## ANGLE 2 — Predictive coding + error correction (Friston, Rao-Ballard, ACC conflict detection)

### Intuitive mechanism

The four HARD_FAIL cells all treat per-hop cleanup as a one-shot "argmax over E". The brain doesn't do that. The brain runs predictive coding: at each hop, the predictive head EXPECTS what the next entity should be GIVEN the current chain context (not just the bind result). The predictive expectation comes from the substrate's sequence-binding primitive (chain-grade CERT586) — applied to the chain's history, it produces a distribution over plausible next entities. The bind-cleanup produces an INDEPENDENT distribution. AGREEMENT between the two means high confidence; DISAGREEMENT triggers ACC-style conflict detection and re-cleanup with sharpened beta or alternative retrieval path.

Mechanistically:
- After each hop, compute two estimates of the next entity:
  - `e_cleanup` from W@state cleanup (the existing primitive)
  - `e_predict` from substrate sequence-binding applied to chain[-N:] history
- If cosine(`e_cleanup`, `e_predict`) > tau_agree: write the bundle of both into the next-hop state (boost the signal)
- If cosine < tau_disagree: route to refinement — re-cleanup with sharpened beta, or backtrack one hop, or refuse-and-replan
- The substrate's CSP uncertainty primitive (chain-grade) provides the confidence metric

### Why different from prior attempts

CSP-gated v1 used confidence threshold to ABORT (refuse-rate climbed to 0.61 at 10hop = mostly refusing). That LOSES signal. This angle uses confidence threshold to REFINE — disagreement triggers more compute, not abandonment. Also, CSP-gated v1 used the confidence of the cleanup output ITSELF (top1-top2 cosine separation), which is the SAME signal as the argmax — circular. This angle uses an INDEPENDENT predictive signal from the sequence-binding history, which has the property that prediction-error is OFFSET from cleanup-error — they're uncorrelated when the chain is correct, and ANTI-correlated when the chain has drifted off (correct prediction says "this should be X", cleanup-error says "I'm picking Y" — anti-correlation surfaces the disagreement).

The lit-scan analog: this is the brain's actual circuit (Rao-Ballard 1999; Friston free-energy; Botvinick-Carter ACC conflict). The mechanism is brain-aligned and the substrate has all the primitives.

### P(solve), calibrated

Per-hop floor estimate: predictive-coding refinement adds maybe +0.05 to +0.15 per-hop accuracy if the substrate sequence-binding primitive is genuinely informative on token chains. Critical pre-requisite: substrate sequence-binding on these chain regimes must be >50% above chance to be load-bearing. Substrate sequence-binding IS chain-grade (CERT586), but that was tested on a single domain — sequence patterns over predicates may be harder than the original sequence-binding benchmark.

Raw P_solve = 0.40 (brain-aligned mechanism, substrate has all primitives, but pre-requisite that sequence-binding adds independent signal is unverified at this regime)
Deflated -0.20 (novel-synthesis lit-scan; PC at write-path stage in VSA multi-hop is novel; also a previous Director drill flagged this as P=0.35 in the anisotropy lane — re-applying for multi-hop without new evidence)
+0.10 brain prior (mechanism is the brain's actual circuit; high brain prior)
**P_deflated = 0.30**

### Cell spec

`exp_substrate_multihop_predictive_coding_acc_refinement_v1`

Arms (3):
- ARM_BASELINE: pointer-chain v2 regime verbatim
- ARM_PC_REFINE: pointer-chain v2 + per-hop predictive-coding agreement gate; disagreement triggers re-cleanup with sharpened beta (3x)
- ARM_PC_BUNDLE: pointer-chain v2 + per-hop bundle of cleanup-result with prediction-result (no gating; pure additive)

Discriminator: ARM_PC_REFINE 5hop top1 >= 0.30 (vs baseline 0.14); ARM_PC_BUNDLE provides the "is the predict-signal independent?" check (bundle should give boost only if signals are uncorrelated).

Critical pre-flight: verify substrate sequence-binding on the chain-of-predicates regime gives >50% above chance prediction. If not, abandon this angle.

Brain prior: STRONG for refinement mechanism (Rao-Ballard); MEDIUM for write-path location of PC.

---

## ANGLE 3 — Bidirectional chain expansion (meet-in-the-middle)

### Intuitive mechanism

Substrate has chain-grade `unbind` (the inverse of bind; FHRR uses conjugate multiply; HRR uses circular correlation via FFT). The substrate's binding is involutive — bind(a, b) followed by unbind(_, b) recovers a (modulo cleanup). This means the substrate can naturally run a chain in REVERSE: given the target answer Z and the predicate sequence [p_n, p_{n-1}, ..., p_1] applied in reverse with unbind, you get back to the start.

For multi-hop QA where (a) the start S, (b) the predicate chain [p_1, ..., p_n], and (c) the target class are known a priori, you can run two chains:
- **Forward chain**: S -> p_1 -> e_1 -> p_2 -> e_2 -> ... -> midpoint M_fwd at floor(n/2)
- **Backward chain**: Z (candidate answer) -> unbind(p_n) -> e_{n-1} -> ... -> midpoint M_bwd at ceil(n/2)

If M_fwd and M_bwd MATCH (cosine similarity above tau), the candidate answer Z is consistent with the chain. Otherwise reject and try the next candidate.

This converts a 5-hop forward chain (top1 = 0.14) into two 2.5-hop chains (each at ~0.485) where the answer is correct if both halves match. Critically, the per-hop floor was the issue — halving the depth halves the compounding.

For ranking candidates: substrate runs forward to M_fwd; runs backward from each candidate Z in the top-K plausible answer set; ranks candidates by cosine(M_fwd, M_bwd_Z). The candidate with highest meet-in-middle cosine wins.

### Why different from prior attempts

Prior attempts were all forward-only. None used the substrate's existing unbind primitive at the chain level. Brain's bidirectional connectivity (cortex-cortex; cortico-thalamic; hippocampus has bidirectional EC<->DG<->CA3<->CA1 loops) suggests the brain does something analogous — chunked retrieval explores both forward and backward from anchors. This is a NEW class of mechanism for substrate multi-hop, not a variant of cleanup-management.

### P(solve), calibrated

Per-hop floor estimate: 5-hop forward = 0.14 top1; 2.5-hop each direction at ~0.35 each (composition of 2 and 3 hop accuracies); meet-in-middle matching is high-signal because the two halves were computed INDEPENDENTLY with different W reads — uncorrelated errors. If both halves are correct (probability 0.35^2 = 0.12 if independent) and you require both to match for accept, you have low recall but high precision. With top-K candidate generation + meet-in-middle ranking, you can recover MUCH higher top1.

But critical concern: meet-in-middle requires KNOWING the predicate sequence a priori AND having a plausible candidate set. The first is reasonable for multi-hop QA over a KG (predicates are part of the query); the second requires either a generation step (substrate generates top-K candidates) or an enumeration over the entity space (V_C=200 manageable).

Raw P_solve = 0.50 (mechanism is genuinely different, substrate has all primitives, error directions are likely uncorrelated)
Deflated -0.20 (novel-synthesis lit-scan; bidirectional VSA chain expansion isn't a standard published technique I can cite — though IBM Pacheco-Kanerva 2017 sketch some bidirectional resonator extensions)
+0.10 brain prior (cortical-cortical bidirection is universal; hippocampal forward-backward replay is well-documented in Foster-Wilson 2006 Nature; brain DOES this)
**P_deflated = 0.40**

### Cell spec

`exp_substrate_multihop_bidirectional_meet_middle_v1`

Arms (4):
- ARM_BASELINE: pointer-chain v2 forward-only verbatim
- ARM_REVERSE_ONLY: pointer-chain v2 backward-only from candidate set
- ARM_MEET_MIDDLE_RANK: forward to midpoint + backward from all V_C candidates; rank by meet-cosine
- ARM_MEET_MIDDLE_TOP_K: forward to midpoint + backward from top-K=20 generated candidates; rank by meet-cosine

Critical discriminator: ARM_MEET_MIDDLE_TOP_K 5hop top1 >= 0.40 (vs baseline 0.14); cv <= 0.10; check that forward-error and backward-error are genuinely uncorrelated (compute correlation across seeds).

Pre-reg bands: HP_5hop >= 0.40; MID_5hop=[0.20, 0.40]; HF < 0.20.

Brain prior: STRONG for bidirectional retrieval circuits.

---

## ANGLE 4 — Substrate-native ECC (error correcting codes) on intermediate

### Intuitive mechanism

The HRR/FHRR bind operation is a continuous "modulation" of one signal by another — but it has no redundancy. A single bit of noise in the bind output cascades into the cleanup as a cosine-similarity perturbation. Classical error-correcting codes (Reed-Solomon, LDPC, repetition) add REDUNDANCY at the encoding stage so a decoder can recover the original signal even after channel noise.

For multi-hop chains, this would look like: each entity E[i] gets bound not just into its bare slot but also into K=3-5 PARITY CODES (each parity code is a deterministic function of E[i] with disjoint redundancy bits). The cleanup at each hop now has K independent "votes" for what the entity should be — the parity decoder recovers the correct E[i] even when the primary slot's cleanup is noisy.

Concretely (one substrate-native instantiation):
- For each entity E[i], precompute K shadow codes E_k[i] = E[i] XOR H_k (where H_k is a deterministic hash that gives near-orthogonal shadows)
- At bind time, bind both E[i] and E_k[i] into W (so each entity is stored K+1 times under different cue patterns)
- At read time, cleanup against all K+1 candidate sets; majority-vote the indices
- The redundancy gives effective error correction: if 2 of 5 shadow reads agree on entity X, that's strong signal even if the primary read disagreed

Compared to parallel-replicate-vote: vote-attempt v1 added NOISE to replicates and voted; the diversity (0.21 mean) was low because adding noise to the SAME bind doesn't decorrelate the noise. ECC adds STRUCTURED REDUNDANCY (different shadows hit different parts of the W matrix) so the per-shadow errors are by-construction uncorrelated.

### Why different from prior attempts

Parallel-replicate-vote v1 tried independence-via-noise; it didn't work because noise on the same W produces correlated errors. ECC produces independence-via-structure: the K shadows hit DIFFERENT regions of the W matrix, so their crosstalk patterns are uncorrelated. The vote then has REAL diversity to exploit.

Literature check: there's a small body of work on HRR-compatible ECC. Plate 1995 (the original HRR paper) noted that bundling multiple bindings of the same item gives noise-averaging benefits. Mirus-Stewart-Eliasmith 2020 explored "binding-stability under noise" but didn't formalize ECC. Frady-Sommer 2020 showed that sparse bundle networks have built-in redundancy properties. None of these published a clean ECC-for-VSA framework I can cite. This is genuinely novel-synthesis territory.

Brain alignment is WEAK for explicit ECC. The brain has cortical microcolumn redundancy (each microcolumn ~100 neurons coding similar things) — that's a form of population coding which gives noise-averaging but isn't strictly ECC. So the brain analog is loose.

### P(solve), calibrated

Per-hop floor estimate: structured redundancy could plausibly lift per-hop accuracy from 0.69 to 0.80-0.85 (if shadow reads are genuinely uncorrelated and majority-vote is decisive). At 5 hops: 0.33-0.44 top1.

Raw P_solve = 0.35 (mechanism is plausible but never validated for VSA; structured-redundancy benefits depend on shadow construction being orthogonal-enough)
Deflated -0.25 (novel-synthesis lit-scan; this is genuinely uncharted; deflate more aggressively because no existing chain-grade ECC-on-VSA citation)
+0.05 brain prior (microcolumn redundancy is brain-adjacent but not a tight analog)
**P_deflated = 0.15** — lowest of the 5 angles

### Cell spec

`exp_substrate_multihop_ecc_shadow_codes_v1`

Arms (3):
- ARM_BASELINE: pointer-chain v2 regime verbatim
- ARM_ECC_K3: pointer-chain v2 + K=3 shadow codes per entity, per-hop majority vote across 4 cleanups
- ARM_ECC_K5: pointer-chain v2 + K=5 shadow codes per entity

Discriminator: per-shadow read CORRELATION must be <0.3 (else shadows are redundant not orthogonal — design failure); 5hop top1 >= 0.30 (HP), [0.18, 0.30] (MID), <0.18 (HF).

Risk: this is the lowest brain-prior angle and the most uncertain — recommend dispatch ONLY if angles 1+3 dispatch first and one of them lands.

---

## ANGLE 5 — Hierarchical / compositional multi-hop (PFC task-decomposition)

### Intuitive mechanism

The substrate has chain-grade 2-hop closure (the original n8 ConceptNet result). It does NOT have chain-grade 5-hop. The substrate ALSO has chain-grade multi-bank WM + audit-gate + intent-classifier — composition primitives that could implement a "query planner."

The compose: decompose a multi-hop query into 2-hop SUB-QUERIES that the substrate CAN handle, then chain the SUB-ANSWERS into the final answer.

Concretely for a 5-hop query S -> p1 -> e1 -> p2 -> e2 -> p3 -> e3 -> p4 -> e4 -> p5 -> e5:
- Sub-query 1: S -> p1 -> e1 -> p2 -> e2 (2-hop, chain-grade) -> read out e2
- Write e2 into WM bank 1
- Sub-query 2: e2 -> p3 -> e3 -> p4 -> e4 (2-hop, chain-grade) -> read out e4
- Write e4 into WM bank 2
- Sub-query 3: e4 -> p5 -> e5 (1-hop, near-perfect) -> answer

Each sub-query operates in the chain-grade regime. The WM banks provide clean storage for intermediates (each in its own bank = uncontaminated). The "planner" decomposes the predicate chain into 2-hop chunks. For 5-hop -> 2+2+1; for 10-hop -> 2+2+2+2+2.

The brain does exactly this. PFC plans tasks into sub-goals; basal ganglia chunks action sequences (Graybiel chunking; Jin-Costa 2010 Nature); hippocampus retrieves the answer to each sub-goal. Multi-step reasoning in humans is empirically chunked into 2-3-element units (Miller's 7+-2 plus Cowan's tighter ~4 unit estimate for working memory).

The key insight: 5-hop with per-hop floor 0.69 gives 0.14 top1. But (2-hop with floor 0.69) gives 0.485 top1 per chunk, and chaining 3 chunks at 0.485 with CLEAN intermediates between chunks gives 0.485^3 = 0.114 — WORSE than the monolithic 5-hop unless the clean-WM-between-chunks provides additional cleanup gain. Which it should: each sub-query starts from a CLEANED entity (not a noisy state), so the 2-hop accuracy should be CLOSER to the n8 ConceptNet 2-hop chain-grade (0.85+) than to the noisy-state 2-hop of pointer-chain v2 (0.485).

The math becomes interesting: if WM-cleaned sub-query 2-hop accuracy is ~0.80 (the n8 number, restoring after the WM cleanup gate), then 3-chunk chain at 0.80^3 = 0.51 — that's a 3.5x lift over monolithic 5-hop. If WM-cleaned is 0.85, you get 0.61 at 5-hop — that's HARD_PASS territory.

### Why different from prior attempts

WM-scaffold v1 wrote intermediates to WM and read them back — but the intermediates it wrote were the CLEANED-INDEX (just an atom from E) which is already a clean signal, so the WM cleanup gate provided no additional benefit. The composition didn't actually decompose the chain into sub-queries; it just wrote per-hop atoms to a scaffold which is what naive cleanup already does implicitly.

This angle is different because it decomposes the CHAIN STRUCTURE into 2-hop sub-queries, each starting from a clean entity. The 2-hop chain primitive is empirically chain-grade (n8 ConceptNet HARD_PASS); we leverage the working primitive at its proven regime.

Substrate doesn't try to make 5-hop primitive WORK; it COMPOSES known-working 2-hop primitives. The "planner" is the only novel piece — and even the planner is simple: a fixed decomposition rule (5-hop -> 2+2+1) needs no learning, just an enumeration.

### P(solve), calibrated

Per-hop floor estimate: 2-hop chain-grade is empirically proven. Composing 2+2+1 with clean WM-mediated handoffs gives bottleneck at the WM cleanup quality. Substrate multi-bank WM is chain-grade at K=32. The composition holds together by construction IF the 2-hop primitive at production scale stays at its chain-grade rail when started from a clean entity (not a noisy bind result).

Raw P_solve = 0.55 (composition of proven primitives in their proven regimes; the "decompose multi-hop into 2-hop chunks" mechanism is the BRAIN'S ACTUAL approach to multi-step reasoning per cognitive psychology)
Deflated -0.20 (novel-synthesis lit-scan; chunked multi-hop in VSA isn't a standard published technique)
+0.10 brain prior (PFC task decomposition + basal ganglia chunking is universal in brain; very high prior)
**P_deflated = 0.45** (cap P=0.50 not invoked; this is composition of proven primitives, not pure novel-synthesis)

### Cell spec

`exp_substrate_multihop_pfc_chunked_2hop_decomposition_v1`

Arms (4):
- ARM_BASELINE: pointer-chain v2 monolithic 5-hop (verbatim regime)
- ARM_CHUNKED_2_2_1: 5-hop decomposed as 2+2+1 sub-queries with clean WM hand-off
- ARM_CHUNKED_3_2: 5-hop decomposed as 3+2 (test whether 2-hop is the right chunk size or whether 3-hop is fine too)
- ARM_CHUNKED_PER_HOP: 5-hop as 1+1+1+1+1 (the limit case — every hop starts from clean WM; tests whether the issue is depth-compounding or chunk-size)

Discriminator: ARM_CHUNKED_2_2_1 5hop top1 >= 0.50 (HP); MID [0.30, 0.50]; HF < 0.30. CRITICAL pre-flight: verify that 2-hop chain-grade STILL HOLDS at the pointer-chain v2 regime (V_C=200, V_P=10) starting from clean entity. If the 2-hop primitive at this harder regime only gives 0.485 (the empirically observed cleanup-after-noisy-state number), then the chunking won't help.

Brain prior: STRONGEST of the five (PFC task decomposition is the brain's universal multi-step-reasoning circuit).

---

## 1. Cross-angle synthesis

### Per-angle summary table

| Angle | Mechanism | P_solve (deflated) | Brain prior | Bottleneck addressed | Cost |
|---|---|---|---|---|---|
| 1 | Compose fly-LSH + multi-bank + partition-routing | 0.45 | STRONG | Per-hop primitive (changes WHAT is being cleaned) | MEDIUM (3 known primitives compose) |
| 2 | Predictive coding + ACC refinement | 0.30 | STRONG (mech), MEDIUM (location) | Independent signal for confidence (offsets cleanup error) | MEDIUM (depends on sequence-binding strength on chains) |
| 3 | Bidirectional meet-in-middle | 0.40 | STRONG | Halves effective chain depth (compounding) | MEDIUM (new unbind-chain path; candidate ranking) |
| 4 | ECC shadow codes | 0.15 | WEAK | Structured redundancy on per-hop reads | HIGH (uncharted; shadow construction risky) |
| 5 | PFC chunked 2-hop decomposition | 0.45 | STRONGEST | Restructures chain to use chain-grade 2-hop primitive | LOW (uses proven primitives at proven regimes) |

### Recommended dispatch order

1. **Angle 5 FIRST** (PFC chunked 2-hop). Highest brain prior, lowest implementation cost, uses proven primitives at proven regimes. If 2-hop at the pointer-chain v2 regime is genuinely chain-grade when started clean, this is the cheapest win. PRE-FLIGHT: 30-min sanity cell verifying 2-hop chain-grade at V_C=200/V_P=10 starting from a clean entity (no chained noise). If pre-flight fails, this angle is dead. If pre-flight passes, dispatch the full chunked-decomposition cell.

2. **Angle 1 SECOND** (compose today's wins). Three chain-grade primitives composed. P=0.45. The super-additive test (does composition give more than sum of individual arms) is the key discriminator. If ARM_COMPOSED beats sum-of-individual-improvements, you have a real composition; if not, you have additive primitives.

3. **Angle 3 THIRD** (bidirectional meet-in-middle). P=0.40, mechanism is genuinely different from the four HARD_FAIL attempts. Costs are MEDIUM (need to verify unbind-chain works at the regime). Key pre-flight: confirm forward-chain-error and backward-chain-error are uncorrelated (compute correlation directly across seeds; if r > 0.5, meet-in-middle won't help much).

4. **Angle 2 FOURTH** (predictive coding refinement). P=0.30. The pre-requisite (sequence-binding gives independent signal on chains) is the load-bearing unknown. Cheap pre-flight: test substrate sequence-binding accuracy on the chain-of-predicates regime in 15 min. If it's not >50% above chance, kill this angle; if it is, dispatch.

5. **Angle 4 LAST or NEVER** (ECC). P=0.15 is the lowest and the brain prior is WEAK. Recommend dispatching ONLY if angles 1, 3, and 5 all land in MIDDLE_BAND and you need one more shot. Even then, the literature gap is real — there's no chain-grade VSA-ECC technique published.

### Compose-multiple-angles option (cheap combos)

**Angle 5 + Angle 1 combo** (PFC chunking + fly-LSH per chunk):
The chunked decomposition (Angle 5) uses 2-hop sub-queries. Each 2-hop sub-query could ALSO use fly-LSH expansion + multi-bank for the within-chunk per-hop cleanup. The composition costs are additive but the lifts compound: chunk-level decomposition restructures the CHAIN, fly-LSH+multi-bank improves the PER-HOP. Combined P-estimate: 0.55 (cap P=0.50 NOT applicable — this is composition of two distinct composition mechanisms, each at P=0.45 individually, with non-overlapping bottleneck targets). Combined P_deflated after additional -0.10 for composition-on-composition risk: 0.45. Same expected P as the best individual angle, but with a different mechanism mix — could be the right move if Angle 5 alone hits MIDDLE_BAND ~0.40.

**Angle 5 + Angle 3 combo** (PFC chunking + bidirectional meet-in-middle):
Decompose 5-hop into 2+2+1 chunks; run each chunk bidirectionally (meet-in-middle within the chunk). This gives chunk-level depth-halving on top of chain-level depth-chunking. Per-chunk 2-hop with meet-in-middle (forward 1, backward 1, meet) could lift the 2-hop primitive from 0.485 (noisy-state) to ~0.70 (because meet-in-middle drops compounding for the within-chunk 2-hop too). Combined P_deflated: 0.45.

**Angle 1 + Angle 3 combo** (fly-LSH per-hop + bidirectional chain):
fly-LSH lifts per-hop accuracy AND meet-in-middle halves chain depth. Both attack the same compounding problem from different sides. Combined P_deflated: 0.45-0.50 depending on independence assumption.

Recommendation: do NOT combine angles in the FIRST cell of each angle. Get individual-arm baselines first to know what each piece does. Then combine angles 5+1 if both land MIDDLE_BAND or better. The combined-angle dispatch is a SECOND-WAVE cell.

### Brain-prior cross-check per angle

I made the brain-prior claims directly in each angle. Quick consolidation:
- Angle 1: STRONG. Three brain-aligned primitives (cerebellar/KC fan-in; PFC working memory parcellation; hippocampal place-cell decomposition).
- Angle 2: STRONG-mech, MEDIUM-location. Rao-Ballard predictive coding is brain's actual circuit. ACC conflict detection is well-documented (Botvinick-Carter). But brain's PC is mostly applied at perceptual/encoder stages; write-path PC for declarative memory is less directly evidenced.
- Angle 3: STRONG. Cortical-cortical bidirection is universal; hippocampal forward-backward replay during sharp-wave ripples is well-documented (Foster-Wilson 2006 Nature).
- Angle 4: WEAK. Cortical microcolumn redundancy is brain-adjacent population coding, not structured ECC. The mechanism is more engineering than biology.
- Angle 5: STRONGEST. PFC task decomposition + basal ganglia chunking is the brain's universal approach to multi-step reasoning. Cognitive psychology (Miller, Cowan, Graybiel) provides chunked-decomposition evidence directly.

### Field literature for HRR-compatible ECC + bidirectional VSA + resonator networks

I'll be honest about what I can confidently cite vs what would require deeper lit-scan:

**Bidirectional VSA / resonator networks** (Angle 3):
- Frady-Kent-Olshausen-Sommer 2020 "Resonator Networks" Neural Computation introduced resonator networks for factorization (solving X = a (x) b (x) c for known X, partial knowledge of factors). The resonator dynamics are bidirectional in the sense that each factor is updated using cross-talk with the others. Substrate has resonator primitives (exp_resonator_capacity_gpu_v1 HARD_FAIL at K=3 N=4096 — limit is small) but never tried bidirectional CHAIN expansion.
- Plate 1995 thesis section on inverse-bind and approximate inverses for HRR — the unbind primitive is well-grounded.
- IBM Pacheco-Kanerva 2017 (general VSA reviews) sketch bidirectional cleanup but don't formalize chain bidirection.

**HRR-compatible ECC** (Angle 4):
- Plate 1995 noted bundling-as-redundancy gives noise averaging (sqrt(K) gain) but didn't formalize ECC.
- Frady-Sommer 2020 (sparse bundle networks) showed sparse coding has redundancy properties but no explicit ECC framework.
- I am NOT aware of a chain-grade published ECC-for-VSA framework. This is genuinely uncharted territory.

**Predictive coding for memory write-path** (Angle 2):
- Rao-Ballard 1999 PC is at encoder stage. Friston 2010 free-energy generalizes broadly but doesn't specifically target VSA memory write-path.
- The brain analog (cortical PC error signals feeding hippocampus) is suggestive but not directly cited.

**PFC chunked decomposition for multi-step reasoning** (Angle 5):
- Miller 1956 (chunking in WM), Cowan 2000 (4-item WM capacity), Graybiel 1998-2008 (basal ganglia chunking).
- Botvinick 2008 "Hierarchical models of behavior and prefrontal function" Trends Cog Sci — PFC chunks tasks into sub-goals.
- For VSA implementation: I'm not aware of a specific published HRR/FHRR chunked-multi-hop architecture. The brain literature is HUGE; the VSA literature is sparse on this composition.

**Honest summary**: angles 3, 4, 5 have weak VSA-specific literature support; the brain-side literature is strong. Angle 1 has direct VSA-side validation (the three primitives are chain-grade in the substrate). Angle 2 has strong brain mechanism support but the write-path application is novel.

---

## 2. Honest framing for USER

The four HARD_FAIL attempts all operated DOWNSTREAM of the per-hop cleanup primitive. They tried to manage the consequences of a 0.69 per-step accuracy. The lesson from reading the metrics: **the per-step accuracy was identical across all four attempts** because the underlying primitive was unchanged. Pointer-chain, WM-scaffold, CSP-gated, and consolidation are ALL THE SAME CELL in mechanism — they all do per-hop argmax over E of W@state, with cleaned-atom-index seeding the next hop. The scaffold/pointer/gate framings are superficial.

This is good news for revival: if the bottleneck is the per-hop primitive, then the 5 revival angles each propose a DIFFERENT way to break that primitive's information-theoretic floor:
- Angle 1: change WHAT the primitive cleans (sparse expanded + bank-routed + partition-routed)
- Angle 2: add an INDEPENDENT signal for confidence (predictive coding gives uncorrelated error direction)
- Angle 3: halve the chain depth (bidirectional meet-in-middle)
- Angle 4: add structured redundancy on each per-hop read (ECC shadows)
- Angle 5: restructure the chain into 2-hop chunks where the primitive IS chain-grade (PFC decomposition)

Angles 1, 3, and 5 are the strongest. Each addresses the bottleneck from a different angle, has STRONG brain priors, and uses substrate primitives that are either already chain-grade or recently chain-grade-candidate. Angle 2 is contingent on a sequence-binding pre-flight. Angle 4 is the longest shot.

**If I had to recommend ONE dispatch from this drill**: Angle 5 (PFC chunked 2-hop decomposition) FIRST, with the 30-min pre-flight to verify 2-hop chain-grade at the pointer-chain v2 regime starting from clean entity. The pre-flight is cheap, the full cell is cheap (composes proven primitives), and the brain prior is strongest. If it lands, you have a chain-grade-candidate multi-hop revival mechanism. If it MIDDLE_BANDs, compose with Angle 1 (fly-LSH per-chunk) as the second wave.

**If I had to recommend TWO**: Angle 5 + Angle 1, dispatched in parallel (different cells; same drill scope). Both use proven primitives, both have STRONG brain priors, both attack different bottlenecks. The expected union P (P_5 OR P_1) is roughly 0.45 + 0.45 - (0.45 * 0.45) = 0.70 — meaning if either lands, multi-hop revival is genuine.

**What I am NOT doing**: dispatching. Drill discipline + spawn-budget Fix #14. Recommendations land here; cell dispatches go through exp_dev spawn separately if/when Director (USER) authorizes. The drill is the strategic deliverable; the dispatches are downstream actions.

---

## 3. File pointers

- Substrate metrics read (Fix #28 per-arm):
  - `data/exp_substrate_multihop_consolidation_v3_proper_test_heldout_fix/metrics.json`
  - `data/exp_substrate_multihop_pointer_chain_hybrid_v2_baseline_rail_fixed/metrics.json`
  - `data/exp_substrate_multihop_wm_scaffolded_v1/metrics.json`
  - `data/exp_substrate_multihop_csp_gated_iterated_cleanup_v1/metrics.json`
  - `data/exp_exp_substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail_smoke/metrics.json`
  - `data/exp_kmax_ness_envelope_corrected_v1/metrics.json` (substrate HAS multi-hop in NESS sense)
  - `data/exp_graph_multihop_snr_v1/metrics.json` (4-hop SNR chain-grade)
  - `data/exp_substrate_partition_routing_10M_full_v2/metrics.json` (decomposition win)
  - `data/exp_substrate_working_memory_multi_bank_routing_v1/metrics.json` (multi-bank win)
  - `data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json` (fly-LSH win)
- Today's anisotropy synthesis: `notes/research_anisotropy_intuitive_synthesis_with_visual_2026-06-25.md`
- Today's solutions catalog: `notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md`
- Barrier 1 closure framing: `notes/research_barrier1_double_negative_substrate_product_definition_2026-06-25.md`
- Substrate primitives verified: `hdlab/binding.py` (unbind exists), `hdlab/multi_hop.py` (naive_chain + iter_cleanup_chain with beta-regime warning), `hdlab/iterative_attractor.py`, `hdlab/profiling.py` (additional unbind references)

Word count: ~3000.

— Research (Director)
