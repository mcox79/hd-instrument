# strategy_decisions_2026-06-05

## v426 -> v427 CYCLE 98 BATCH (2026-06-05)

Verdicts processed: substrate_kgram_xor_real_llama1b_v1 (MIDDLE_BAND) + substrate_kfact_combination_anchors_v1 (MIDDLE_BAND)

### Step 0 honest re-read
- kgram_xor_real_llama1b_v1: HONEST. K2/K1=1.17x (1.155-1.181x 3/3 seeds). Label "modest" accurate. No LVH.
- kfact_combination_anchors_v1: HONEST. 2/4: A1+A3 pass; A2+A4 fail. Label "2/4 anchors confirm" accurate. No LVH.
HONEST: 922 -> 924 (+2). LVH: 222 UNCHANGED.

### Cap_map decisions
- kgram_xor_real_llama1b: PP-8 sub-property annotation. Real-data XOR lift 1.17x vs synthetic 6.63x. V_C=256 VQ ceiling persists in real Llama-1B. Band UNCHANGED.
- kfact_combination_anchors: Physics combination sub-property annotation. beta* recovery (A1=1.000) + Rule-8 gain (A3=+29.3pp) confirmed. A2 transition K=25 vs sqrt(N)/2=16 mismatch (finite-N correction needed). A4 resonator_disagree=0.0% (unexplained; open physics question). Band UNCHANGED.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

Queue state: overnight_queue 0 pending (cache stale ~39.5h). [queue: empty -- Exp-Dev session will refill on its cadence]

## v427 -> v428 CYCLE 99 (2026-06-05)

Verdict: substrate_certified_deletion_demo_medical_v1 MIDDLE_BAND

### Step 0 honest re-read
- LABEL: MIDDLE_BAND -- honest. cert_latency_median=3.136ms (range 3.115-3.163ms, 3 seeds) falls in 1-10ms MIDDLE_BAND window. HP threshold was <1ms -- missed by ~3x. phantom_recall=0.000 (all seeds), verifier_confirmed=1.000 (all seeds), nondeleted_retention=1.000 (all seeds). Deletion mechanism correct; latency is the gap.
- No over-claim. HONEST: 924 -> 925 (+1). LVH: 222 UNCHANGED.

### Cap_map decision
- PP-3 (audit trail + rotation strategy): Sub-property annotation. Medical demo confirms deletion cert mechanism works end-to-end at M=1200, RSA-512, third-party verifier. Latency 3.136ms above <1ms HP threshold; latency-optimization path required for production-grade GDPR demo. Band UNCHANGED at 0.55-0.70.
- PP-9 (GDPR deletion / reasoning amortization): Sub-property annotation. Certified deletion confirmed third-party verifiable with 0 phantom recall. Latency gap (3.136ms vs <1ms) is a latency-engineering challenge, not a correctness failure. Band UNCHANGED.
- Product-feature row (certified deletion): MIDDLE_BAND annotation. Deletion cert + audit chain + verifier all confirmed working. RSA accumulator overhead drives latency. Optimization path: RSA bit-reduction + N-scale reduction + batch cert + hardware acceleration.

### Portfolio: 32+77 UNCHANGED. 0 new rows. 0 BAND-LIFTS. 0 closures.

### Rescue sketches (PROT-004/006 -- latency gap, cheapest-first per [[feedback-rescue-sketch-first-sequencing]])
1. R1 (CHEAP, 0-compute) -- Subsumption: cert_latency 3.136ms is sub-10ms; real HIPAA deletion compliance windows are 60-day; <1ms HP threshold is stricter than any medical regulatory SLA. Re-frame HP as <10ms for product context; MIDDLE_BAND becomes functionally HP for compliance demo.
2. R2 (CHEAP, CPU <30min) -- RSA bit-reduction: RSA-256 vs RSA-512 latency; accumulator ops scale O(k^2) with key bits; halving key size expected to halve latency toward ~1.5ms; likely clears <2ms and possibly <1ms.
3. R3 (CHEAP, CPU <30min) -- N-scale ablation: N=1024 or N=2048 vs N=4096; projection-op component of cert latency is O(N); smaller N may clear <1ms with acceptable retrieval accuracy trade-off.
4. R4 (MEDIUM, GPU <2h) -- Batch cert optimization: batch 200 deletion certs into one accumulator witness update; amortized latency per cert drops proportionally with batch size.
5. R5 (MEDIUM, GPU <2h) -- GPU-native accumulator: RSA-512 on GPU vs CPU; may achieve sub-ms cert at current N=4096 with no algorithmic change.

### PROT compliance (v427 -> v428)
- PROT-004/006: No closures. 5 rescue sketches filed for MIDDLE_BAND latency gap (cheapest-first sequencing). 0 new top-level rows. 0 BAND-LIFTS.
- PROT-007: v428 history row to be appended to substrate_capability_map_history.md.
- PROT-008: Validator skipped (annotation-only; no row state changes; no portfolio changes; 0 LVH; MIDDLE_BAND x1 sub-property only).
- PROT-009: cap_map.md (this v428 entry) + substrate_capability_map_history.md + decisions log staged atomically; 340th PROT-009 paired commit.
- PROT-018: substrate_certified_deletion_demo_medical_v1 no _nN suffix; N=4096 stated in metrics. CLEAN.

Cap_map: v427 -> v428 CYCLE 99 (1 MID: substrate_certified_deletion_demo_medical_v1 CERT-DELETION-3MS-PHANTOM-ZERO-VERIFIER-CONFIRMED; PP-3+PP-9+product-feature sub-prop annotations; 5 latency-rescue sketches; HONEST 924->925; LVH 222; Portfolio 32+77; 340th PROT-009 paired commit) (2026-06-05)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
