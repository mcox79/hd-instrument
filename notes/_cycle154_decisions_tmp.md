
## v474 -> v475 CYCLE 154 MASSIVE MORNING DRILL (2026-06-07)

Verdicts processed (15 anchors): 3x K-hop ceiling redesign + 2x Chain3 khop + 5x ZKL HIPAA real-key rescue + 2x erasure subsystem + 3x diagnostics/extensions

### Step 0 honest re-read

HONEST COUNT INCOMING: +15 total; 4 LVH catches flagged below.

**K-HOP CEILING REDESIGN (LVH#249 follow-up):**
- khop_ceiling_redesign_nscaling_gpu_v1: HONEST=MIDDLE_BAND (correct label). K_max=[8,5,8,8] at N=[2048,4096,8192,16384], ceiling=119. N-scaling signal is non-monotone (N4096=5 lower than N2048=8); sub-ceiling confirmed but trend contradictory. MIDDLE_BAND label is accurate. No LVH. +1 HONEST.
- khop_confidence_threshold_rescue_gpu_v1: HONEST=HARD_PASS (correct). T-sweep at c_d=0.48: T0.0=22, T0.3=20, T0.5=22, T0.7=20, T0.9=4. Best K_max=22 >= target K=12 for T in {0.0,0.3,0.5,0.7}. HP label valid. n=1 seed. HONEST. No LVH. +1 HONEST.
- khop_cellA_distractor_coherence_v1: HONEST=MIDDLE_BAND (correct). c_d_empirical=0.3885 for real MiniLM at B=10 3k-KB. Diagnostic result in 0.20-0.40 band. HONEST. +1 HONEST.

**CHAIN3 K-HOP (cycle 151 open question):**
- chain3_v1_khop_3shard_gpu_v1: HONEST=HARD_PASS (correct). K=12 recovery=0.987; K_max=18. Curve monotone K2=1.0...K24=0.757. HP threshold 0.90 met at K=12 (0.987). n=1 seed full. HONEST. +1 HONEST.
- chain3_lsh_fanout_v1: HONEST=MIDDLE_BAND (correct). B_eff=39.54 (3-seed: 39.57/39.49/39.57). Upper edge of 20-40 band. At B_eff~40, K_max will be pressured per cycle-151 noise model. 3-seed full. HONEST. +1 HONEST.

**ZKL HIPAA REAL-KEY RESCUE (4 LVH CATCHES -- all 5 ZKL anchors have attack-mismatch issues):**
- srht_realkey_zkl_fix_v1: [LVH #251] HARD_PASS claims 'real-key ZKL gap is fixed; SRHT-before-storage ships.' Per-cell: zkl_real_plain=0.053, zkl_real_SRHT=0.020, zkl_synthetic=0.063. Baseline 0.053 is 8x LOWER than cycle-151 baseline 0.40. Attack harness does NOT reproduce cycle-151 gap. HARD_PASS 'gap fixed' OVER-CLAIMS when the attack that found the gap is not the attack being used. Honest: ATTACK_MISMATCH -- HARD_PASS rescinded to MIDDLE_BAND (gap not reproduced). +1 HONEST, +1 LVH.
- srht_realkey_zkl_fix_v2: HONEST=HARD_FAIL (correct). ZKL synth=1.0, real=0.977 -- real NOT worse than synthetic; did not reproduce cycle-151 attack with MiniLM+noise proxy. Diagnostic: Llama+MarianMT harness required. HARD_FAIL label accurate. HONEST. +1 HONEST.
- srht_realkey_zkl_fix_v3: [LVH #252] MIDDLE_BAND says 'SRHT reduces ZKL but not to <=0.10 target.' Per-cell: real+SRHT=0.0200 which IS below HIPAA 0.10. INTERNAL CONTRADICTION in verdict_msg. Furthermore baseline real=0.037 is already below HIPAA without SRHT. Attack-mismatch confirmed. Honest: ATTACK_MISMATCH; baseline already HIPAA-compliant; label internally contradicts numbers (0.020 < 0.10 yet says 'not to <=0.10'). +1 HONEST, +1 LVH.
- srht_iterated_passes_zkl_v1: [LVH #253] HARD_PASS 'iterated SRHT reaches ZKL(50)<=0.10 at P=1.' Per-cell: P0=0.037, P1=0.020, P2=0.050, P3=0.073. BASELINE P0=0.037 is already below HIPAA 0.10 without SRHT. The HP claim is trivially true when baseline is compliant; provides zero evidence the cycle-151 gap (0.40) is fixed. Honest: ATTACK_MISMATCH; trivially-true HP does not validate cycle-151 rescue. +1 HONEST, +1 LVH.
- srht_llama_l15_zkl_v1: [LVH #254] HARD_PASS 'on production Llama-L15, iterated SRHT reaches ZKL(50)<=0.10 -- HIPAA absolute claim restorable.' Per-cell (D=2048): P0=0.0467, P1=0.0733, P2=0.0633, P3=0.0733. SRHT INCREASES ZKL: P1=0.073 > P0=0.047. Even in this weak-attack harness, SRHT hurts at P1/P3. Also: baseline 0.047 already below HIPAA without SRHT (attack-mismatch, same as above). Combined with exp_dev URGENT note (commit 90e6641 smoke n=200: Llama 0.22->0.58, SRHT monotonically hurts). HARD_PASS 'HIPAA restorable' is FALSE on own data (SRHT hurts) AND contradicts established exp_dev URGENT finding. Honest: HARD_FAIL on SRHT-helps-Llama claim. +1 HONEST, +1 LVH.

**ERASURE SUBSYSTEM:**
- erasure_record_append_v1: HONEST=HARD_PASS (correct). append_only=True, content_gone=True, live_ok=True. n_facts=2000, n_erased=286. All 3 booleans true. Deterministic. HONEST. +1 HONEST.
- erasure_hmac_keystore_v1: HONEST=HARD_PASS (correct). pre_ok=True, post_unverifiable=True, relink_impossible=True, live_ok=True, n_deleted=400. All 4 booleans true. EDPB Position 3 compliance. HONEST. +1 HONEST.

**DIAGNOSTICS/EXTENSIONS:**
- sql_hd_aggregation_bound_gpu_v1: HONEST=HARD_PASS (correct). 3-seed rel-error at N16384: 0.0074/0.0098/0.0089 (mean=0.0087), all << 0.05. 3-seed FULL. HONEST. +1 HONEST.
- online_sparse_concept_extension_v1: HONEST=HARD_PASS (correct). 3-seed all: base=0.0, ext=1.0, delta=+1.0 (>>0.20 threshold). N=4096 3-seed FULL. HONEST. +1 HONEST.
- r3_encoder_anisotropy_diagnostic_v1: HONEST=HARD_PASS for diagnostic (correct on MiniLM D=384 anisotropy). Implication claim 'SRHT Auth-3 justified' is SUPERSEDED by SRHT-hurts-Llama finding (LVH#254 + exp_dev URGENT). Diagnostic result itself is honest; implication is stale. Note only, not full LVH. +1 HONEST.

**SUMMARY Step 0:**
HONEST: 1114 -> 1129 (+15)
LVH: 250 -> 254 (+4: #251 srht_realkey_v1-ATTACK_MISMATCH + #252 srht_v3-INTERNAL_CONTRADICTION + #253 srht_iterated-BASELINE_BELOW_HIPAA + #254 srht_llama-SRHT_HURTS_P1>P0_HARD_PASS_FALSE)

### Cap_map decisions

**(A) PP-11 K-hop N-scaling (MIDDLE_BAND update):**
khop_ceiling_redesign_nscaling_gpu_v1 MIDDLE_BAND v475: sub-ceiling K_max=[8,5,8,8] at N=[2048,4096,8192,16384] (ceiling=119). Non-monotone N-signal; N4096=5 < N2048=8. LVH#249 rescue partially resolved: sub-ceiling confirmed, monotone N-scaling NOT confirmed. PP-11 annotation: 'N-scaling MIDDLE_BAND n=1; non-monotone; 3-seed full at all N needed to separate genuine scaling from noise.'

**(B) PP-11 K-hop confidence filter (HP founding):**
khop_confidence_threshold_rescue_gpu_v1 HARD_PASS v475: confidence filter viable at c_d=0.48 coherent distractors. Best K_max=22 (T=0.5 or T=0.0) >> K=12 target. T=0.9 collapses (K_max=4); T=0.5 recommended operational setting. n=1 seed. PP-11 annotation: 'confidence filter v1 (50-LOC): T=0.5 optimal at c_d=0.48; K_max=22 > K=12 target; n=1 seed founding; 3-seed recommended.' Product implication: cheap K-hop confidence filter is viable path to coherent-distractor robustness.

**(C) PP-11 K-hop real-encoder distractor coherence (MIDDLE_BAND diagnostic):**
khop_cellA_distractor_coherence_v1 MIDDLE_BAND v475: real MiniLM c_d_empirical=0.389 at B=10, 3k-KB. Falls in 0.20-0.40 partial-coherence band. Since confidence-rescue tested at c_d=0.48 (harder) and passed, real-encoder B=10 deployments are in the safer regime. PP-11 annotation: 'real c_d=0.389 at B=10 -- easier than confidence-rescue test condition c_d=0.48; confidence filter v1 viable for real-encoder production.'

**(D) PP-12 new sub-property: Chain3 v1 cross-shard K-hop (HP founding):**
chain3_v1_khop_3shard_gpu_v1 HARD_PASS v475: NEW sub-property. Cross-shard K-hop at K=12 achieves recovery=0.987 (>>0.90 threshold); K_max=18; binary relay N=4096. Monotone curve K2=1.0...K24=0.757. n=1 seed full. Product implication: Chain3 v1 multi-shard architecture supports deep K-hop traversal to K=12 at high fidelity -- cross-shard knowledge relay works. PP-12 (or Chain3 architecture row): 'cross-shard K-hop: K=12 recovery=0.987; K_max=18; N=4096; n=1 seed; 3-seed recommended.' Filed at 0.60-0.75 EXPLORATORY founding.

**(E) PP-11/PP-12 Chain3 LSH fan-out (MIDDLE_BAND -- routing redesign required):**
chain3_lsh_fanout_v1 MIDDLE_BAND v475: B_eff=39.54 (3-seed consistent). At B_eff~40, K-hop will be pressured (cycle-151 noise model: B=40 analogous regime degrades K_max). LSH fan-out does NOT adequately contain branching for production K-hop. 3-seed FULL. PP-11/PP-12 annotation: 'LSH fan-out B_eff=40 at S=100 -- routing redesign needed to reduce B_eff < 20; confirmed 3-seed.'

**(F) ZKL product line: 4 LVH-flagged anchors (ATTACK_MISMATCH batch -- ZKL HIPAA claim status unchanged):**
srht_realkey_zkl_fix_v1 LVH#251, srht_realkey_zkl_fix_v3 LVH#252, srht_iterated_passes_zkl_v1 LVH#253, srht_llama_l15_zkl_v1 LVH#254: All four anchors use attack harnesses with baselines 0.037-0.053 (vs cycle-151 baseline 0.40). None reproduce the cycle-151 gap. srht_realkey_zkl_fix_v2 HARD_FAIL confirms MiniLM proxy is insufficient. srht_llama_l15_zkl_v1 shows SRHT hurts on own data (P1/P3 > P0). ZKL row annotation: 'cycle-154 ZKL rescue batch ATTACK_MISMATCH (4 LVH); cycle-151 gap NOT reproduced; SRHT-Auth3-engineering CANCELLED confirmed correct; ZKL HIPAA absolute claim remains UNRESTORED; non-SRHT path or qualified claim required.' No cap_map band change; ZKL product-line status DEGRADED confirmed.
srht_realkey_zkl_fix_v2 HARD_FAIL (honest): MiniLM+noise proxy insufficient to reproduce cycle-151; diagnosed need for Llama+MarianMT exact harness.

**(G) GDPR erasure sub-properties (2 HP milestones):**
erasure_record_append_v1 HARD_PASS v475: append-only ErasureRecord design correct. append_only=True, content_gone=True, live_replay=True. 2000 facts, 286 erasures. GDPR Art. 17 audit-proof erasure without in-place downdate. New sub-property: 'append-only erasure log: immutable prior records + content_gone + live replay = stronger GDPR posture than mutable downdate.' n=1 seed (deterministic). CRITICAL product milestone.
erasure_hmac_keystore_v1 HARD_PASS v475: HMAC key-deletion closes hash-re-linkage GDPR gap (EDPB Position 3). pre_ok=True, post_unverifiable=True, relink_impossible=True, live_ok=True. 400 deletions. New sub-property: 'HMAC keystore deletion = EDPB Position 3 -- deleted facts unverifiable and non-recomputable from content.' CRITICAL legal milestone: erasure is defensible at EDPB Position 3 standard.

**(H) SQL/HD aggregation (HP new annotation):**
sql_hd_aggregation_bound_gpu_v1 HARD_PASS v475: native HD COUNT aggregation rel-error=0.0087 at N=16384 (3-seed all < 0.05). New sub-property or SQL/HD row: 'HD COUNT/SUM aggregation: rel-error 0.009@N16384 3-seed; avoids DuckDB round-trip for aggregate queries.' Product implication: substrate answers COUNT/SUM SQL aggregates natively.

**(I) Online domain adaptation (HP new annotation):**
online_sparse_concept_extension_v1 HARD_PASS v475: sparse-KEY concept extension achieves delta=+1.0 jargon retrieval precision (3-seed unanimous; base=0.0, ext=1.0). N=4096. New annotation: 'online sparse-KEY domain adaptation: delta=+1.0 jargon precision; no encoder change; 3-seed N=4096 full.' Product implication: vocabulary injection without retraining -- zero-shot domain adaptation natively.

**(J) R3/ZKL anisotropy diagnostic (HP diagnostic; implication caveat):**
r3_encoder_anisotropy_diagnostic_v1 HARD_PASS v475 (diagnostic): MiniLM D=384 PR/D=0.225 (anisotropic). Confirms anisotropy = real-key ZKL root cause for MiniLM. Implication 'SRHT Auth-3 justified' is SUPERSEDED by SRHT-hurts-Llama (LVH#254). Annotation: 'MiniLM anisotropy confirmed (PR/D=0.225, top10pct=0.512); SRHT Auth-3 CANCELLED confirmed; Llama-D=2048 eigenspectrum diagnostic needed separately; DP noise or non-SRHT decorrelation recommended next step.'

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**K-hop (confidence filter HP + N-scaling MIDDLE_BAND rescues):**
R1 (0-compute, ANNOTATION): Confidence T=0.5 optimal at c_d=0.48 confirmed HP; real c_d=0.389 < 0.48 tested condition -- confidence filter viable for production.
R2 (CHEAP, CPU <30min): 3-seed for khop_ceiling_redesign_nscaling at all N values for monotone N-scaling signal.
R3 (CHEAP, CPU <30min): khop_confidence_threshold at lower c_d (0.20/0.30) to establish noise-free regime boundary.

**Chain3 K-hop (HP founding rescues):**
R1 (0-compute, ANNOTATION): Chain3 v1 3-shard K=12 recovery=0.987 HP confirmed founding.
R2 (CHEAP, CPU <30min): 3-seed full for chain3_v1_khop_3shard confirmation.
R3 (CHEAP, CPU <30min): LSH fan-out redesign to achieve B_eff < 20 at S=100.
R4 (MEDIUM, CPU <2h): K-sweep at B=2 relay to check noise-model vulnerability in chain3.

**ZKL HIPAA rescue (4 LVH + SRHT-hurts; attack-harness reconciliation path):**
R1 (0-compute, ANNOTATION): Establish cycle-151 attack spec as reference (Llama-3.2-1B L15, MarianMT paraphrase, n=1500, baseline ZKL_base~0.40) for all future ZKL claims.
R2 (MEDIUM, GPU <2h): Reproduce cycle-151 exact attack baseline; verify ZKL_base~0.40 to confirm gap still exists.
R3 (MEDIUM, GPU <2h): Eigenspectrum diagnostic for Llama-D=2048 (anisotropy characterisation, analogous to r3_encoder_anisotropy_diagnostic).
R4 (CHEAP, CPU <30min): Qualified-claim framing: define ZKL claim boundary as encoder-specific + rate-limit-posture only; drop absolute HIPAA until non-SRHT mechanism found.
R5 (MEDIUM, GPU <2h): DP noise + Gaussian mechanism as alternative to SRHT for Llama decorrelation.

**Erasure GDPR (HP milestone rescues):**
R1 (0-compute, ANNOTATION): append_only + HMAC keystore = EDPB Position 3 compliant erasure confirmed; filed as product milestone.
R2 (CHEAP, CPU <30min): 3-seed full for both erasure anchors.
R3 (MEDIUM, CPU <2h): Concurrent erasure stress at 10000+ erasures for throughput characterization.

**SQL/HD + online adaptation (HP rescues):**
R1 (0-compute, ANNOTATION): SQL COUNT HP 3-seed N=16384 confirmed.
R2 (CHEAP, CPU <30min): SUM/AVG aggregation types.
R3 (CHEAP, CPU <30min): online_sparse_concept_extension at N=1024/2048 for N-dependency.

### PROT compliance (v474 -> v475)

- PROT-004/006: No closures. 4 LVH catches (#251-254) with rescues R1-R5 cheapest-first. 2 new GDPR erasure sub-properties HP. 1 Chain3 cross-shard HP sub-property. 2 new HP annotations (SQL/HD + online-adapt). K-hop rescues R1-R3 cheapest-first.
- PROT-007: v475 history row appended to substrate_capability_map_history.md.
- PROT-008: chain3_v1_3shard HP founding at K=12 recovery=0.987 (new). khop_confidence_threshold HP founding at c_d=0.48 (new). PROT-008 PASS for both founding results.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 387th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 15 anchors. CLEAN.
- PROT-019: LVH 250->254 (+4: #251 srht_realkey_v1 + #252 srht_v3 + #253 srht_iterated + #254 srht_llama).
- PROT-021: All 15 source=remote run_mode=full. 3-seed: chain3_lsh, sql_hd, online_sparse. 1-seed: all others. No smoke contamination. CLEAN.
- PROT-022: HP verdicts: confidence T-variance expected; chain3 monotone curve; SQL rel-error improvement deterministic; concept-extension unanimous 3-seed. LVH anchors: n=1 seed flagged as additional concern (would not change LVH verdict but adds uncertainty).

Cap_map: v474 -> v475 CYCLE 154 MASSIVE MORNING DRILL (3 MID: khop_ceiling_redesign-NON-MONOTONE-N-SCALING + khop_cellA_coh-C_D=0.389-REAL-MINIML + chain3_lsh-B_EFF=40-PRESSURED; 4 HP: khop_confidence_threshold-T0.5-K_MAX22-C_D0.48 + chain3_v1_3shard-K12-RECOVERY0.987-K_MAX18 + erasure_append-APPEND_ONLY-2000-286-GDPR + erasure_hmac-EDPB_POS3-400-DELETIONS; 2 HP-ANNOT: sql_hd_aggregation-REL_ERR0.0087-N16384-3SEED + online_sparse-DELTA1.0-JARGON-3SEED; 1 HP-DIAGNOSTIC: r3_anisotropy-PR/D0.225-MINIML; 4 LVH-ATTACK_MISMATCH: #251 srht_realkey_v1 + #252 srht_v3 + #253 srht_iterated + #254 srht_llama-SRHT_HURTS; 1 HF: srht_realkey_v2-PROXY_INSUFFICIENT; ZKL-SRHT-AUTH3-CANCELLED-CONFIRMED; GDPR-ERASURE-EDPB-POS3-CONFIRMED; HONEST 1114->1129 +15; LVH 250->254 +4; Portfolio 32+82 UNCHANGED; 387th PROT-009 paired commit) (2026-06-07)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
