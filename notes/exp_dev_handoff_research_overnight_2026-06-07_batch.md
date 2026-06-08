# exp_dev hand-off -- research: OVERNIGHT BATCH 2026-06-07

**Filed:** 2026-06-07 ~21:45 by research (post-cycle-176 status drill + user "identify a lot of experiments overnight" mandate)
**Trigger:** Exp-Dev queue depth = 0 per user report; cycle 176 strategic shift identified bridge-entity extraction as multi-hop bottleneck; 15+ anchors with cheap CPU pre-tests pending across multiple paths
**Pause state:** data/cloud_paused_overnight.flag is SET; LOCAL CPU + small sonnet only, NO GPU/CLOUD overnight per existing rule
**Per [[feedback-no-experiment-design-in-prompts]]:** anchor pointers only; Exp-Dev designs N/M/K/seeds/bands/profile/anchor name

## CURRENT STATUS SYNTHESIS

### Today's empirical state (cycles 154-176; 12 cycles)
- HONEST 1297 (started morning at ~1180; +117 today)
- LVH 262 (+1 today; cycle-175 iterative direction-reversed)
- Portfolio 32+97 (+15 PP rows today including PP-86 through PP-97)
- 60 commits v438 -> v496

### Critical pending open threads
1. **Multi-hop bridge-extraction bottleneck (cycle 176 strategic shift):** orchestrator confirmed substrate K-hop PP-11 (K=12 recovery=0.987) is PROVEN; integration gap is LLM-side bridge decomposition; 7B LLM decompose path = forward
2. **Wikipedia substrate ingest GO/NO-GO:** CELL-2 v3 5.84M articles; ~7 hr; pre-trained substrate as v1 product (user-locked)
3. **Wish 2 multimodal:** MSCOCO pre-test required before commit
4. **Wish 3 preference bindings:** displaces $5K/customer LLM fine-tune; pre-test gate
5. **Multi-hop revival 5-experiment battery (pre-compaction filing):** 2 of 5 done in cycle 176 (bge-large HF, K=3 HF); 3 remain
6. **3-seed promotions:** 9 n=1 HPs from cycle 176 + earlier; strengthen empirical foundation
7. **DP field extensions:** 3 untested anchors (subsampling + GDP + N=1024 rehab)
8. **Modern Hopfield field extensions:** 2 untested anchors (continuous bridge + phase-transition characterization)
9. **VSA field FHRR speed:** Anchor 4 untested

## ANCHOR CANDIDATES (rank-ordered; rough priority groups)

### GROUP A: Multi-hop bridge-extraction RESCUES (PRIORITY 1 — strategic)

**A1. GLiNER + bge-small iterative (DIRECT bridge-extraction fix)**
- Pointer: notes/research_to_exp_dev_multihop_bridge_extraction_RESCUE_AUTHORIZE_2026-06-07.md Rescue 2
- Substrate-product reading: schema-free NER layered BEFORE iterative retrieval; directly tests "bridge-entity extraction quality is the bottleneck" hypothesis
- Tier: LOCAL CPU (~2 hr); HotpotQA distractor subset
- HARD-PASS: recall@2 >= 0.55

**A2. spaCy NER + bge-small iterative**
- Pointer: same RESCUE AUTHORIZE; Rescue 3
- Substrate-product reading: faster alternative to GLiNER; tests whether ANY NER extraction stage rescues iterative
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: recall@2 >= 0.55

**A3. e5-large + iterative (encoder-side completeness check)**
- Pointer: RESCUE AUTHORIZE Rescue 1
- Substrate-product reading: e5-large untested in iterative; confirms encoder side fully exhausted before pivoting LLM-side
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: recall@2 >= 0.55

**A4. 7B LLM decompose + substrate K-hop (proof of orchestrator's hypothesis)**
- Pointer: RESCUE AUTHORIZE Rescue 4; orchestrator endorsed
- Substrate-product reading: PROOF that substrate IS the K-hop primitive once LLM extracts bridge correctly; Qwen-7B or Mistral-7B for decomposition, substrate Pattern B K=8 for K-hop, LLM for answer
- Tier: LOCAL CPU MEDIUM (~3-4 hr; 7B inference is heavy on CPU)
- HARD-PASS: recall@2 >= 0.55 AND F1 >= single-shot + 0.05
- STRATEGIC: this is the orchestrator-endorsed forward path

### GROUP B: Substrate K-hop production-N validation (proof primitive at scale)

**B1. substrate K-hop at production N=4096, K=8, real-bridge inputs**
- Pointer: cycle 176 cap_map "substrate K-hop PP-11 K=12 recovery=0.987 PROVEN"; confirm at production N=4096 not just N=1024
- Substrate-product reading: validates the K-hop capability at production substrate size; if HP at K=8 N=4096 then substrate K-hop is empirically anchored as primitive
- Tier: LOCAL CPU (~1-2 hr)
- HARD-PASS: K=8 recovery >= 0.95 at N=4096

### GROUP C: Wikipedia substrate ingest GO/NO-GO (v1 product gate)

**C1. Wikipedia substrate ingest dry-run (10K articles smoke)**
- Pointer: CELL-2 v3 was prior cell; the 5.84M-article full ingest is ~7 hr
- Substrate-product reading: PRE-trained Wikipedia substrate is locked v1 product requirement ("we're not sending this thing out a virgin"); 10K dry-run validates pipeline + timing extrapolation before committing 7 hr
- Tier: LOCAL CPU (~30-60 min smoke)
- HARD-PASS: 10K ingest completes; timing extrapolation to 5.84M < 12 hr

### GROUP D: Wish 2 + Wish 3 pre-tests (wish-we-had drill follow-ons)

**D1. Wish 2 MSCOCO binary-CLIP pre-test (multimodal gate)**
- Pointer: notes/research_to_exp_dev_composition_plus_wish_we_had_pretests_AUTHORIZE_2026-06-07.md Wish 2 anchor
- Substrate-product reading: binary-CLIP at N=512 on MSCOCO; if recall@10 >= 90% of full-precision CLIP, multimodal v2.0 path opens
- Tier: LOCAL CPU (~3-4 hr) or GPU if available
- HARD-PASS: bipolar CLIP N=512 retains >= 90% MSCOCO r@10 vs full precision

**D2. Wish 3 preference bindings pre-test (customer intuitions)**
- Pointer: same routing; Wish 3 anchor
- Substrate-product reading: synthetic customer feedback on 100 queries → substrate accumulates bindings → sleep defrag aggregates; predicts 50 held-out queries
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: substrate preference prediction matches human-validated >= 75% on held-out

### GROUP E: 3-seed promotions for cycle-176 n=1 HPs (strengthen foundation)

3-seed any subset of these 9 cycle-176 n=1 HPs to confirm variance bounds:
- E1. streaming_count_min_sketch_v1 3-seed (n=3 across different seeds + stream lengths)
- E2. streaming_hyperloglog_v1 3-seed
- E3. streaming_reservoir_sampling_v1 3-seed
- E4. streaming_bloom_dedup_v1 3-seed
- E5. vsa_map_permute_sequences_v1 3-seed at V=100k (production vocab scale)
- E6. dp_rdp_accountant_v1 T-sweep (T=10,50,100,200,500) for consortium sizing curve
- E7. hopfield_phase_map_v1 at N=4096 (production scale of N=256 cycle-176 result)
- E8. sparse_hopfield_v1 with K-sparsity sweep at N=4096
- E9. hopfield_beta_sweep_v1 at production N=4096

Tier: LOCAL CPU (~30 min each); pick top 4-5 for overnight batch

### GROUP F: DP field extensions (untested anchors from DP 5x drill)

**F1. dp_subsampling_amplification_v1**
- Pointer: notes/research_to_exp_dev_field_DP_5x_AUTHORIZE_2026-06-07.md Anchor 3
- Substrate-product reading: substrate per-customer query sampling at 1% → equivalent to 100x lower ε; tests free privacy via subsampling
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: 1% subsampling = 100x lower ε equivalent

**F2. dp_gdp_tradeoff_v1**
- Pointer: same DP AUTHORIZE Anchor 4
- Substrate-product reading: arXiv 2503.10945 (2025) Gaussian DP tighter bounds; tests if substrate DP guarantees can be tightened via GDP-based analysis
- Tier: LOCAL CPU (~2-3 hr)
- HARD-PASS: GDP bound 1.5x+ tighter than current RDP at T=20

**F3. dp_n1024_rehab_v1**
- Pointer: same DP AUTHORIZE Anchor 5
- Substrate-product reading: smaller substrate at N=1024 vs production N=4096 viable under subsampling + per-instance-DP combination; cost-efficient edge deployment
- Tier: LOCAL CPU (~3-4 hr)
- HARD-PASS: N=1024 + subsampling + per-instance-DP achieves equivalent recall + privacy as N=4096 unsampled

### GROUP G: Modern Hopfield + VSA field untested anchors

**G1. modern_hopfield_continuous_bridge_v1 (Tier-4.5 prep)**
- Pointer: notes/research_to_exp_dev_field_5x_drills_3_AUTHORIZE_2026-06-07.md Modern Hopfield Anchor 3
- Substrate-product reading: substrate continuous-valued bindings for fine-grained queries; bridge to attention layer; Tier 5 enabler
- Tier: LOCAL CPU (~4-6 hr)
- HARD-PASS: continuous Hopfield retains >= 95% retrieval at lower bit count

**G2. modern_hopfield_phase_transition_v1**
- Pointer: same Modern Hopfield Anchor 4
- Substrate-product reading: map substrate's operating point on capacity-noise phase diagram; customer pitch "substrate operates at <1% of theoretical capacity"
- Tier: LOCAL CPU analysis (~1-2 hr; pure data analysis from existing results)

**G3. vsa_fhrr_speed_pretest_v1**
- Pointer: notes/research_to_exp_dev_field_5x_drills_3_AUTHORIZE_2026-06-07.md VSA Anchor 4
- Substrate-product reading: FFT-domain convolution at N=4096 vs direct convolution; if FHRR >= 2x speedup at recall parity, production speed enhancement
- Tier: LOCAL CPU (~3-4 hr)
- HARD-PASS: FHRR >= 2x speedup at recall parity

## RECOMMENDED OVERNIGHT BATCH SHAPE

Cheap priority anchors (each <2 hr CPU; can stack 8-12 overnight):
- A1 GLiNER iterative (PRIORITY 1)
- A2 spaCy NER iterative
- A3 e5-large iterative
- B1 substrate K-hop production-N
- C1 Wikipedia ingest dry-run smoke
- D2 Wish 3 preference bindings
- E1-E5 streaming/VSA 3-seed promotions (pick 4)
- F1 DP subsampling
- G3 VSA FHRR speed

Medium priority anchors (each 3-4+ hr CPU; queue if cheap batch completes):
- A4 7B LLM decompose + K-hop (STRATEGIC; orchestrator-endorsed forward path)
- D1 Wish 2 MSCOCO multimodal
- F3 DP N=1024 rehab
- G1 continuous Hopfield bridge

## Cross-references

- Cycle 176 verdict summary: notes/orchestrator_to_research_results_summary_2026-06-07_cycle176.md
- Multi-hop RESCUE AUTHORIZE: notes/research_to_exp_dev_multihop_bridge_extraction_RESCUE_AUTHORIZE_2026-06-07.md
- Multi-hop revival follow-on battery (pre-compaction): notes/research_to_exp_dev_multihop_revival_followon_battery_2026-06-07.md
- Field 5x AUTHORIZE: notes/research_to_exp_dev_field_5x_drills_3_AUTHORIZE_2026-06-07.md
- DP 5x AUTHORIZE: notes/research_to_exp_dev_field_DP_5x_AUTHORIZE_2026-06-07.md
- Wish-we-had + composition: notes/research_to_exp_dev_composition_plus_wish_we_had_pretests_AUTHORIZE_2026-06-07.md
- 5 natural analog pre-tests: notes/research_to_exp_dev_natural_analog_5_pretests_AUTHORIZE_2026-06-07.md
- Evening post-compaction brief: notes/research_POST_COMPACTION_BRIEF_2026-06-07_evening.md

---

**Exp-Dev:** queue is empty per user 2026-06-07 ~21:45. Authorize the 8-12 cheap anchors
in recommended overnight shape above. A1 (GLiNER iterative) is highest strategic priority
per cycle 176 bottleneck identification. A4 (7B LLM decompose + K-hop) is orchestrator-endorsed
forward path but medium-cost; queue after cheap batch. NO CLOUD/GPU overnight.
