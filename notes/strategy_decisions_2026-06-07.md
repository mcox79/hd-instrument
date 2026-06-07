# strategy_decisions_2026-06-07

## v473 -> v474 CYCLE 153 CAUSAL BATCH (2026-06-07)

Verdicts processed: causal_correlational_disambig_v1 (HP) + causal_intervention_isolation_v1 (HP) + causal_counterfactual_replay_v1 (HP)

### Step 0 honest re-read

- causal_correlational_disambig_v1: HONEST. 3-seed FULL remote. per_seed: prec=1.0/1.0/1.0 (mean=1.000); recall=0.94/1.0/0.98 (mean=0.973). BOTH >= HP threshold 0.85 on EVERY seed. Comparative claim ">=0.85" verified on all 3 per-seed cells. HARD_PASS label CORRECT. No LVH.
- causal_intervention_isolation_v1: HONEST. 3-seed FULL remote. per_seed: deg=0.0/0.0/0.0 (mean=0.000); non-target recall after=1.0/1.0/1.0. Threshold claim "<0.02 degradation; others >=0.95" verified on EVERY seed; deg=0.0000 and non-target recall=1.000 unanimous. HARD_PASS label CORRECT. No LVH.
- causal_counterfactual_replay_v1: HONEST. 3-seed FULL remote (N=1024). per_seed: acc=1.0/1.0/1.0 (mean=1.000); intervention_ms=4.148/3.738/3.740 (mean=3.876ms). Accuracy >=80% and latency <10ms verified on ALL seeds. EU AI Act Art. 12 product framing consistent with empirical numbers. HARD_PASS label CORRECT. No LVH.

HONEST: 1111 -> 1114 (+3). LVH: 250 UNCHANGED.

### Cap_map decisions

**(A) NEW TOP-LEVEL ROW PP-81: Substrate causal-graph role-vector disambiguation.**
causal_correlational_disambig_v1 GENUINE FULL HARD_PASS at N=4096 3-seed. Mechanism A (causal binding via role vectors): CAUSE_OF vs CORRELATED_WITH bindings algebraically separable with prec=1.000 recall=0.973 unanimous across seeds. Substrate-product implication: substrate stores and retrieves causal-vs-correlational relationship distinctions as native role bindings -- no separate causal inference engine needed; causal knowledge graph is first-class in the storage algebra. Cross-references: PP-35 graph retrieval (PP-81 extends to typed causal edges); PP-39 neural-symbolic bridge (PP-81 adds causal-binding to symbolic rule engine); PP-25 retrieval explainability (PP-81 enables causal-attribution readout). Filed at 0.60-0.75 EXPLORATORY (base 0.65-0.80 - 0.05 lit-scan calibration; N=4096 3-seed founding; production-N and heteroassoc-scale confirmation pending).

**(B) SUB-PROPERTY PP-81a: Causal intervention isolation (do() operator is LOCAL -- zero non-target degradation).**
causal_intervention_isolation_v1 GENUINE FULL HARD_PASS at N=4096 3-seed. Performing a do() hetero-assoc target swap on one binding does NOT degrade non-target bindings (deg=0.000 unanimous; non-target recall=1.000). Algebraic isolation is EXACT in this scope. Product implication: causal interventions are safe -- editing one causal fact does not corrupt other stored facts. PP-81a sub-property: EMPIRICAL VALIDATED (3-seed scope). Cross-references: PP-9 deletion-cert (causal isolation analogous to deletion-cert locality); PP-28 edit-impact-DAG (PP-81a provides zero-crosstalk intervention guarantee).

**(C) NEW TOP-LEVEL ROW PP-82: Substrate causal counterfactual replay (do() API, <4ms, EU AI Act Art. 12 audit-ready).**
causal_counterfactual_replay_v1 GENUINE FULL HARD_PASS at N=1024 3-seed. Counterfactual replay via hetero-assoc target swap: accuracy=1.000 (all seeds), mean_intervention=3.876ms. HP thresholds (>=80% accuracy, <10ms) passed with substantial margin on all seeds. Substrate-product implication: substrate exposes a native "what-if?" API -- swap a stored causal fact and instantly retrieve the modified conclusion at <4ms; first-class audit primitive for EU AI Act Article 12. No separate counterfactual engine needed; replay is algebraic. Cross-references: PP-49 hierarchical refusal counterfactual abduction (PP-82 is causal-graph what-if vs PP-49 refusal subtree what-if -- same algebra family, distinct product scopes); PP-25 retrieval explainability (PP-82 provides causal-counterfactual primitive); PP-46 GDPR non-repudiation (PP-82 enables "what-if this fact were deleted" query). Filed at 0.60-0.75 EXPLORATORY (base 0.65-0.80 - 0.05 lit-scan calibration; N=1024 founding only; production-N=4096+ needed for band-LIFT).

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**PP-81 causal disambiguation (HP founding -- rescues for scale confirmation):**
R1 (0-compute, ANNOTATION): N=4096 3-seed founding confirmed. Band UNCHANGED pending production-N cross-N.
R2 (CHEAP, CPU <30min): 3-seed at N=8192 to confirm prec/recall >= HP at production scale.
R3 (CHEAP, CPU <30min): M-sweep (M=50..200 bindings) to characterize disambiguation at larger KG sizes.
R4 (MEDIUM, CPU <2h): 3-class disambiguation (causal+correlational+confounded) to test multi-class causal structure.

**PP-81a causal isolation (HP sub-property -- rescues for capacity stress):**
R1 (0-compute, ANNOTATION): N=4096 3-seed zero-degradation confirmed. Band UNCHANGED pending M-capacity sweep.
R2 (CHEAP, CPU <30min): M-sweep (M=10..100) to characterize isolation at larger memory load.
R3 (CHEAP, CPU <30min): Adversarial isolation (M neighboring semantically similar bindings) to probe crosstalk at high density.

**PP-82 counterfactual replay (HP founding -- rescues for production-N):**
R1 (0-compute, ANNOTATION): N=1024 founding confirmed. Production-N required for band-LIFT.
R2 (CHEAP, CPU <30min): N=4096 3-seed replay to confirm accuracy >= 80% and latency < 10ms at production-N.
R3 (CHEAP, CPU <30min): Multi-step counterfactual (chain 2-3 do() ops) to characterize composability.
R4 (MEDIUM, CPU <2h): EU AI Act Art. 13 audit stress test -- 100+ concurrent counterfactual queries at N=4096 for throughput characterization.

### Portfolio: 32+80 -> 32+82 (+2 NEW ROWS: PP-81 causal-disambiguation + PP-82 counterfactual-replay; PP-81a isolation as sub-property of PP-81). 0 BAND-LIFTS. 0 closures.

### PROT compliance (v473 -> v474)

- PROT-004/006: No closures. 2 NEW TOP-LEVEL ROWS (PP-81 + PP-82). 1 NEW SUB-PROPERTY (PP-81a). Rescue sketches filed cheapest-first (R1 annotation always first; R2-R4 CPU/GPU in cost order).
- PROT-007: v474 history row appended to substrate_capability_map_history.md.
- PROT-008: 2 new top-level rows + 1 new sub-property. State-transition validator: PP-81 prec=1.0/recall=0.973 all-seed HP + PP-82 acc=1.0/ms=3.876 all-seed HP = FOUNDING CRITERIA MET. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 386th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 3 anchors. CLEAN.
- PROT-019: LVH 250 UNCHANGED. No new LVH catches.
- PROT-021: All 3 source=remote run_mode=full n_seeds=3. No smoke contamination. CLEAN.
- PROT-022: Causal anchors 1+2 at N=4096 3-seed; prec always 1.0; recall=0.94-1.0 seed variance acceptable at N=4096. Anchor 3 at N=1024 acc=1.0 all seeds; ms=3.74-4.15 timing variance acceptable. No HP-fragility concern.

Cap_map: v473 -> v474 CYCLE 153 (3 HP: causal_correlational_disambig-PREC1.0-RECALL0.973-CAUSE_VS_CORR-N4096-3SEED + causal_intervention_isolation-DEG0.000-NON_TARGET_RECALL1.000-ZERO_CROSSTALK + causal_counterfactual_replay-ACC1.0-3.876ms-DO_OPERATOR-EU_AIACT_ART12; 0 LVH; HONEST 1111->1114 +3; LVH 250 UNCHANGED; 2 NEW PP ROWS: PP-81 causal-disambiguation 0.60-0.75 EXPLORATORY + PP-82 counterfactual-replay 0.60-0.75 EXPLORATORY; 1 NEW SUB-PROPERTY PP-81a zero-crosstalk isolation; Portfolio 32+80 -> 32+82; 386th PROT-009 paired commit) (2026-06-07)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

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

## v475 -> v476 CYCLE 155 MORNING CONTINUATION BATCH (2026-06-07)

Verdicts processed (21 anchors): 4x GPU (llama_eigenspectrum_diagnostic_v1, w_4bit_quantization_gpu_v1, sparse_w_scale_validation_gpu_v1, modern_hopfield_gpu_scale_v1) + 17x CPU

### Step 0 honest re-read

HONEST COUNT INCOMING: +21 total; 3 LVH catches below.

**GPU ANCHORS:**

- llama_eigenspectrum_diagnostic_v1: HONEST=MIDDLE_BAND (correct). Remote n=1. Llama-L15 D=2048: PR_pre=PR_post=12.733 (IDENTICAL; SRHT zero effect); top10_pre=top10_post=0.854 (IDENTICAL). SRHT does NOT flatten Llama eigenspectrum; PRoverD=0.00622 (very low rank concentration vs MiniLM PR/D=0.225). Verdict_msg 'SRHT did not flatten the spectrum' confirmed by identical pre/post numerics. No LVH. +1 HONEST.

- w_4bit_quantization_gpu_v1: HONEST=HARD_PASS (correct). Remote n=1. N8192: fp32=0.0, q4bit=0.0, drop=0.0; N16384: fp32=0.0, q4bit=0.0, drop=0.0. Zero degradation from 4-bit quantization at both N. HP label valid (0.0 < 3pct threshold). elapsed=2s (short wall; n=1 seed caveat). No LVH. +1 HONEST.

- sparse_w_scale_validation_gpu_v1: HONEST=HARD_FAIL (correct). Remote n=1. sp0.5=1.0 (viable), sp0.75=0.0 (collapses), sp0.875=0.0, sp0.9375=0.0 -- at BOTH N=4096 and N=8192. Max viable sparsity=0.5 (2x reduction); 4x target requires sp=0.75 which collapses. HF label accurate. No LVH. +1 HONEST.

- modern_hopfield_gpu_scale_v1: HONEST=HARD_PASS (correct). Remote n=1. N8192_L0.30=1.0, N8192_L0.40=1.0, N16384_L0.30=1.0, N16384_L0.40=1.0 -- all unanimous 1.0 > 0.90. elapsed=1.3s. HP label valid. No LVH. +1 HONEST.

**CPU ANCHORS:**

- v1_corroboration_gate_v1: HONEST=MIDDLE_BAND (correct). Remote 3-seed N=4096. f=4/10 Q=3: false_accept=0.000 all seeds (safety PASS), recovery=0.553/0.574/0.543 (mean=0.557, liveness FAIL). Verdict_msg 'one criterion met' accurate. No LVH. +1 HONEST.

- dp_noise_injection_zkl_v1: [LVH #255] HARD_PASS 'DP injection is a viable privacy knob (SRHT alternative).' Per-cell: s0.00=0.037/recall1.0; s0.05=0.040/1.0; s0.10=0.050/1.0; s0.20=0.053/1.0; s0.40=0.033/1.0. Baseline s0.00=0.037 already << HIPAA 0.10 (attack-mismatch same as cycle-154 ZKL batch). DP noise at s0.05/0.10/0.20 ALL WORSE than baseline. s0.40 marginally better (0.033 vs 0.037). HP 'DP is a viable privacy knob' OVER-CLAIMS: (a) baseline already HIPAA-compliant on synthetic harness; (b) DP does not meaningfully improve ZKL on this harness. Honest: ATTACK_MISMATCH -- same synthetic-proxy harness as cycle-154; real Llama+MarianMT required. LVH #255. +1 HONEST, +1 LVH.

- sparse_key_coherent_distractors_v1: HONEST=HARD_FAIL (correct). Remote 3-seed N=4096. K8: dense=1.0/1.0/1.0, sparse=1.0/1.0/1.0; K12: dense=0.998/1.0/0.998, sparse=1.0/0.996/1.0. Both methods ~1.0; max delta=-0.004 at K12 seed17. Sparse-key provides zero advantage at B=10 coherent distractors. HF label 'sparse~dense at B=10' accurate. No LVH. +1 HONEST.

- sql_hybrid_aggregation_v1: HONEST=MIDDLE_BAND (correct). Remote 3-seed N=4096. s_recall=1.0 all seeds (SELECT native PASS); a_err=0.9998 all seeds (AVG 100% error -- DuckDB required); sa_err=0.000 all seeds (SUM native PASS). 2/3 query classes native confirmed. No LVH. +1 HONEST.

- bundle_relay_fault_tolerance_v1: HONEST=HARD_PASS (correct). Remote 3-seed N=4096. drop0.0=1.0, drop0.1=1.0, drop0.3=1.0 all seeds; drop0.5=1.0/0.999/1.0 (min=0.999). All >= 0.92 threshold. HP 'graceful degradation' accurate. No LVH. +1 HONEST.

- corroborate_gossip_damp_v1: HONEST=HARD_FAIL (correct). Remote 3-seed N=2048. adv_naive=0.0/0.0/0.0 (no DAMP baseline); adv_damp=0.523/0.580/0.600 (DAMP CREATES adversarial content); acc_naive=1.0/1.0/1.0; acc_damp=0.477/0.420/0.400. DAMP catastrophically inverts: adversarial fraction 0->0.55+, accuracy 1.0->0.43. HF label accurate and conservative. No LVH. +1 HONEST.

- crdt_quorum_bundle_v1: HONEST=HARD_PASS (correct). Remote 3-seed N=4096. order_independent=1.0/1.0/1.0. Exact commutativity+associativity confirmed unanimously. HP label valid. No LVH. +1 HONEST.

- n_reduction_storage_v1: HONEST=HARD_PASS (correct). Remote n=1 (278s). alpha_c: N1024=0.5, N2048=0.5, N4096=0.5, N8192=0.5 -- PERFECTLY FLAT (flatness=1.0 >> 0.8 threshold). HP 'alpha_c N-independent' accurate. No LVH. +1 HONEST.

- privacy_fixes_cone_rank_entropy_v1: [LVH #256] HARD_PASS 'F1_cone_center reaches ZKL<=0.14 -- HIPAA path reopens.' Per-cell: baseline=0.023/1.0; F1_cone_center=0.033/1.0 (WORSE than baseline); E1_entropy_rot=0.097/1.0; B1_rank_random=0.040/1.0 (WORSE than baseline). Baseline ZKL=0.023 already << 0.14 (attack-mismatch). cone_center and rank_random HURT ZKL vs baseline. HP 'HIPAA path reopens' OVER-CLAIMS on attack-mismatch harness. Honest: ATTACK_MISMATCH -- baseline compliant, none of the fixes improve over baseline, cone_center/rank_random both worse. LVH #256. +1 HONEST, +1 LVH.

- modern_hopfield_n_sweep_v1: HONEST=HARD_PASS (correct). Remote n=1 (24.7s). N4096_L0.20=1.0, N4096_L0.30=1.0, N8192_L0.20=1.0, N8192_L0.30=1.0. All 1.0. HP 'modern Hopfield >0.90 at N=4096 M/N=0.30' accurate. No LVH. +1 HONEST.

- membership_auroc_mapping_v1: HONEST=HARD_PASS (correct). Remote 3-seed. AUROC=1.0/1.0/1.0 unanimous. Perfect distinguishability on synthetic harness. HP 'AUROC=1.000' accurate (confirms attack power; also confirms real-attack need for meaningful privacy defense evaluation). No LVH. +1 HONEST.

- predicate_ratio_audit_v1: HONEST=MIDDLE_BAND (correct). Remote 3-seed N=4096. sel0.05 mean=0.915 (>0.90 PASS); sel0.10 mean=0.797 (<0.90 FAIL); sel0.25 mean=0.698; sel0.50 mean=0.742. Verdict_msg 'holds at low selectivity, degrades at high' confirmed. No LVH. +1 HONEST.

- sql_rolling_window_v1: HONEST=HARD_PASS (correct). Remote 3-seed N=4096. rel_error=0.011/0.015/0.018 (max=0.018 < 0.05). HP '<0.05 rel-error' confirmed. No LVH. +1 HONEST.

- confidence_weighted_bundling_v1: HONEST=HARD_FAIL (correct). Remote 3-seed N=4096. cw=1.0/1.0/1.0, naive=1.0/1.0/1.0, delta=0.0 all seeds. Null result -- ceiling effect at f=4/10 (both methods perfect). HF 'no better than naive' accurate. No LVH. +1 HONEST.

- bitemporal_sync_throughput_v1: HONEST=HARD_PASS (correct). Remote n=1 (n_writes=20000). per_write_ms=0.00136, throughput=737,730 writes/s. HP '<1ms/write' confirmed (0.00136ms is 736x below threshold). No LVH. +1 HONEST.

- chain3_sparse_key_integration_v1: HONEST=HARD_FAIL (correct). Remote 3-seed N=4096. B_eff=39.54/39.38/39.62 (mean=39.51). Identical to cycle-154 dense LSH B_eff=39.54. Sparse routing zero improvement. HF 'B_eff>=39 -- no improvement' accurate. No LVH. +1 HONEST.

- privacy_combined_fix_v1: [LVH #257] HARD_PASS 'cone_only reaches ZKL<=0.14 -- HIPAA path reopens.' Per-cell: baseline=0.023/1.0; cone_only=0.033/1.0 (WORSE than baseline); combined_cone_rot=0.097/1.0. Exact duplicate of LVH #256 pattern: baseline compliant, cone_only hurts. HP OVER-CLAIMS. LVH #257. +1 HONEST, +1 LVH.

**SUMMARY Step 0:**
HONEST: 1129 -> 1150 (+21)
LVH: 254 -> 257 (+3: #255 dp_noise_injection_zkl-DP_NO_BENEFIT_BASELINE_COMPLIANT + #256 privacy_fixes_cone_rank-CONE_HURTS_BASELINE_ATTACK_MISMATCH + #257 privacy_combined_fix-DUPLICATE_ATTACK_MISMATCH)

### Cap_map decisions (v475 -> v476)

**(A) Llama eigenspectrum diagnostic (MIDDLE_BAND -- SRHT mechanism DISPROVEN for Llama):**
llama_eigenspectrum_diagnostic_v1: PR_pre=PR_post=12.733; top10 unchanged=0.854. SRHT has ZERO effect on Llama-L15 D=2048 eigenspectrum. Mechanism hypothesis disproven. ZKL product-line annotation: 'Llama-L15 eigenspectrum: PR_pre=PR_post=12.733 (SRHT zero effect); top10 unchanged; SRHT spectrum-flattening mechanism DISPROVEN for Llama; PRoverD=0.0062 (Llama not anisotropic like MiniLM PR/D=0.225); ZKL-worsening root cause lies outside eigenspectrum; DP noise or structured projection needed.' Cycle 155.

**(B) 4-bit W quantization (HP -- 4x compression near-free):**
w_4bit_quantization_gpu_v1: drop=0.0 at N=8192 and N=16384. Storage/compression row annotation: '4-bit W quantization: 0.0% accuracy drop at N=8192-16384 (n=1 seed, 2s wall); 4x storage reduction near-free; recommended over sparse-W (which collapses at sp>=0.75).' 3-seed full recommended for cap_map band LIFT. Cycle 155.

**(C) Sparse-W (HF -- 4x compression axis CLOSED; 2x viable only):**
sparse_w_scale_validation_gpu_v1: sp=0.75 collapses recall 1.0->0.0 at both N. Storage/compression row annotation: 'sparse-W 4x compression CLOSED: sp>=0.75 recall=0.0 (N=4096 and N=8192 n=1); 2x (sp=0.5) viable; 4-bit quantization is superior compression path; sparse-W axis closed at this N regime.' Rescue sketches R1-R3 below. Cycle 155.

**(D) Modern Hopfield GPU scale (HP -- N=16384 confirmed):**
modern_hopfield_gpu_scale_v1: recall=1.0 all 4 cells at N=8192-16384 M/N=0.30-0.40. Modern Hopfield row annotation: 'GPU scale: N=16384 M/N=0.40 recall=1.0 (n=1); complements cycle-154 GPU result; N=8192-16384 operational range confirmed at M/N>=0.30.' 3-seed recommended for LIFT. Cycle 155.

**(E) v1 corroboration gate (MIDDLE_BAND -- safety OK, liveness insufficient at Q=3):**
v1_corroboration_gate_v1 MIDDLE_BAND: false_accept=0.000 (safety PASS), recovery=0.557 mean (liveness FAIL at f=4 Q=3). Byzantine-corroboration annotation: 'gate Q=3 f=4: safety=PASS (FA=0.0), liveness=FAIL (recovery=0.557); Q increase needed for liveness; Q-sweep R2 scheduled.' Rescue sketches R1-R3 below. Cycle 155.

**(F) DP noise ZKL (LVH #255 -- ATTACK_MISMATCH; no benefit on synthetic harness):**
dp_noise_injection_zkl_v1 ATTACK_MISMATCH / MIDDLE_BAND: baseline ZKL=0.037 already < HIPAA; DP noise does not improve baseline (s0.05/0.10/0.20 all WORSE). ZKL row annotation: 'LVH#255: dp_noise synthetic harness -- baseline already compliant; DP adds no benefit; s0.40 marginally better (0.033) but noise pattern non-monotone; Llama+MarianMT exact harness required for genuine DP evaluation. SRHT-CANCELLED extends to DP-on-synthetic-insufficient.' Cycle 155.

**(G) Sparse-KEY coherent distractors (HF -- sparse=dense at B=10; benefit limited to B=1):**
sparse_key_coherent_distractors_v1 HF: sparse=dense=~1.0 at B=10; max delta=0.004. PP-11 K-hop annotation: 'sparse-KEY at B=10 coherent: null result (dense~sparse); sparse benefit limited to B=1; confidence filter (cycle-154 T=0.5, K_max=22) is the viable coherent-distractor path at B>=10.' Cycle 155.

**(H) SQL hybrid aggregation (MIDDLE_BAND -- SELECT+SUM native; AVG needs DuckDB):**
sql_hybrid_aggregation_v1 MIDDLE_BAND 3-seed: SELECT recall=1.0 (native), SUM err=0.000 (native), AVG err~=1.0 (DuckDB required). SQL/HD row annotation: 'Hybrid SQL: 2/3 query classes native (SELECT+SUM); AVG 100% relative error natively; partition+DuckDB fallback for AVG required; 3-seed N=4096 confirmed.' Cycle 155.

**(I) Bundle relay fault tolerance (HP -- graceful degradation at 50% dropout confirmed):**
bundle_relay_fault_tolerance_v1 HP 3-seed: drop0.5 min recall=0.999 across all 3 seeds. Distributed-architecture row annotation: 'bundle relay: 50% node dropout recall=0.999 (3-seed N=4096); graceful degradation confirmed; relay-bundle multi-shard architecture fault-tolerant; no 2PC-abort needed.' Cycle 155.

**(J) Corroborate gossip DAMP (HF -- mechanism inverted; adversarial fraction INCREASES):**
corroborate_gossip_damp_v1 HF 3-seed: DAMP adv_frac=0.55+ vs naive=0.0; acc_damp=0.43 vs acc_naive=1.0. DAMP catastrophically counterproductive in gossip context. Annotation: 'DAMP gossip HF: adversarial fraction 0->0.55+; accuracy 1.0->0.43; DAMP inverted in gossip context; naive bundling strictly superior; alternative Byzantine suppression needed (rescue sketches R2-R4).' Cycle 155.

**(K) CRDT quorum bundle (HP -- commutative merge exactly confirmed):**
crdt_quorum_bundle_v1 HP 3-seed N=4096: order_independent=1.0 unanimous. Distributed-architecture annotation: 'CRDT superposition bundle: exact commutativity+associativity at N=4096 (3-seed); eventual consistency via CRDT bundle validated.' Cycle 155.

**(L) N reduction storage (HP -- alpha_c perfectly N-independent, flatness=1.0):**
n_reduction_storage_v1 HP: alpha_c=0.5 at all N (N1024-8192); flatness=1.0. Storage annotation: 'N-reduction: alpha_c=0.5 flat across N1024-8192 (flatness=1.0 >> 0.8 threshold); N reduction near-free storage savings; pick smallest N meeting quality threshold.' Cycle 155.

**(M) Privacy fixes cone/rank/entropy (LVH #256 -- ATTACK_MISMATCH; cone hurts baseline):**
privacy_fixes_cone_rank_entropy_v1 ATTACK_MISMATCH: baseline=0.023 already compliant; cone_center=0.033 > baseline (WORSE); rank_random=0.040 > baseline (WORSE); entropy_rot=0.097 (approaching limit but on compliant harness). ZKL privacy row annotation: 'LVH#256: all fixes WORSE than compliant baseline on synthetic harness; HIPAA path does not reopen via synthetic fixes; Llama+MarianMT harness required for genuine privacy-fix evaluation.' Cycle 155.

**(N) Modern Hopfield N sweep (HP -- N=4096 confirmed on CPU; bridges GPU coverage):**
modern_hopfield_n_sweep_v1 HP n=1 (24.7s): N4096/N8192 L0.20/L0.30 all=1.0. Modern Hopfield annotation: 'CPU N-sweep: N=4096-8192 M/N<=0.30 recall=1.0; bridges cycle-154 GPU (N=8192-16384) with N=4096 coverage; operational N range N=4096-16384 confirmed across both runners.' Cycle 155.

**(O) Membership AUROC mapping (HP -- ZKL->AUROC bridge; AUROC=1.0 on synthetic harness):**
membership_auroc_mapping_v1 HP 3-seed: AUROC=1.0 unanimous. Privacy row annotation: 'membership AUROC=1.000 (3-seed synthetic); ZKL->AUROC mapping established; AUROC=1.0 confirms perfect distinguishability on synthetic harness (consistent with attack-mismatch: real-attack AUROC may differ); reinforces Llama+MarianMT harness need.' Cycle 155.

**(P) Predicate ratio audit (MIDDLE_BAND -- native at sel<=0.05; DuckDB at sel>=0.10):**
predicate_ratio_audit_v1 MIDDLE_BAND 3-seed N=4096: sel0.05=0.915 (PASS); sel0.10=0.797 (FAIL); sel0.25=0.698; sel0.50=0.742. SQL/HD row annotation: 'Predicate selectivity: native HD viable at sel<=0.05 (recall~0.915); degrades at sel>=0.10 (recall<0.80); partition-or-DuckDB for high-selectivity predicates; production constraint: sel<=0.05 for native HD path.' Cycle 155.

**(Q) SQL rolling window (HP -- streaming COUNT/SUM no drift confirmed):**
sql_rolling_window_v1 HP 3-seed N=4096: rel_error max=0.018 < 0.05. SQL/HD annotation: 'rolling-window streaming: rel_error<0.05 all 3 seeds (max=0.018); native HD add/subtract no drift; streaming COUNT/SUM validated for production streaming aggregation.' Cycle 155.

**(R) Confidence weighted bundling (HF -- null result, ceiling effect at f=4/10):**
confidence_weighted_bundling_v1 HF 3-seed N=4096: cw=naive=1.0 all seeds. Null result (ceiling effect). Byzantine/corroboration annotation: 'confidence-weighted bundling HF: ceiling effect at f=4/10 (both=1.0); null result; stress test at higher f/N ratio or adversarial embedding required to evaluate confidence weighting signal.' Cycle 155.

**(S) Bitemporal sync throughput (HP -- 0.00136ms/write, 737K writes/s):**
bitemporal_sync_throughput_v1 HP n=20000-write sweep: 0.00136ms/write, 737,730 writes/s. Bitemporal product annotation: 'append-only bitemporal sync: 0.00136ms/write (736x below 1ms threshold), 737K writes/s; synchronous sync adequate for V1; no async queue needed.' Cycle 155.

**(T) Chain3 sparse-key integration (HF -- B_eff=39.51 = dense LSH; structural redesign needed):**
chain3_sparse_key_integration_v1 HF 3-seed N=4096: B_eff=39.51 (mean) vs dense LSH B_eff=39.54 (cycle-154). Zero improvement. PP-11/PP-12 routing annotation: 'sparse-key routing HF: B_eff=39.51=dense (null result, 3-seed); sparse-code overlay does not reduce branching; structural redesign (hierarchical routing or aggressive top-k cutoff) required to achieve B_eff<20.' Rescue sketches R2-R3 below. Cycle 155.

**(U) Privacy combined fix (LVH #257 -- ATTACK_MISMATCH duplicate of LVH #256):**
privacy_combined_fix_v1 ATTACK_MISMATCH: baseline=0.023; cone_only=0.033 (WORSE); combined_cone_rot=0.097. Same pattern as LVH#256. ZKL annotation: 'LVH#257: exact duplicate of #256 pattern -- cone_only hurts baseline; HP claim trivially true on compliant harness; Llama+MarianMT required.' Cycle 155.

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**Sparse-W compression (HF -- 4x axis closed; 2x viable only):**
R1 (0-compute, ANNOTATION): sp>=0.75 recall=0.0 confirmed at N=4096 and N=8192; 4x axis closed; 4-bit is superior path.
R2 (CHEAP, CPU <30min): sp=0.5 (2x) recall at N=16384 to confirm 2x boundary at larger N.
R3 (CHEAP, CPU <30min): Block-sparse (N/4 blocks) at sp=0.75 as structured-sparsity alternative.

**Corroborate gossip DAMP (HF -- mechanism inverted; alternative suppression):**
R1 (0-compute, ANNOTATION): DAMP inverted in gossip context; naive bundling strictly superior.
R2 (CHEAP, CPU <30min): Top-k similarity filter (weighted majority vote) as DAMP replacement.
R3 (CHEAP, CPU <30min): Byzantine-aware bundling with pairwise similarity thresholding.
R4 (MEDIUM, CPU <2h): Multi-round iterative consensus without DAMP for adversarial gossip.

**v1 corroboration gate (MIDDLE_BAND -- Q-sweep for liveness):**
R1 (0-compute, ANNOTATION): Q=3 safety confirmed (FA=0.0); Q increase needed for liveness at f=4.
R2 (CHEAP, CPU <30min): Q-sweep (Q=5,7,9) at fixed f=4 to locate liveness threshold.
R3 (CHEAP, CPU <30min): Confidence-weighted Q for liveness improvement at fixed Q=3.

**ZKL / privacy consolidated (LVH #255-257 -- real-attack harness path):**
R1 (0-compute, ANNOTATION): Llama-3.2-1B L15 + MarianMT = sole authoritative ZKL harness; all synthetic results are ATTACK_MISMATCH until reproduced on real harness.
R2 (MEDIUM, GPU <2h): Reproduce cycle-151 baseline ZKL~0.40 on exact harness.
R3 (MEDIUM, GPU <2h): DP noise re-run (dp_noise_injection_zkl) on Llama+MarianMT.
R4 (MEDIUM, GPU <2h): Privacy fixes (cone/rank/entropy + combined) re-run on Llama+MarianMT.

**Chain3 LSH branching (HF -- structural redesign to reduce B_eff):**
R1 (0-compute, ANNOTATION): Sparse-KEY null result confirms structural redesign needed.
R2 (CHEAP, CPU <30min): Hierarchical routing (2-level index) for B_eff reduction at S=100.
R3 (MEDIUM, CPU <2h): Approximate-NN with top-k=5 cutoff to achieve B_eff < 20.

### PROT compliance (v475 -> v476)

- PROT-004/006: No row closures. 3 LVH catches (#255-257) with rescue sketches R1-R4 cheapest-first. 2 compression/routing axis closures (sparse-W 4x + chain3-sparse-key null). DAMP mechanism inverted (functional closure of DAMP approach). Rescue sketches filed cheapest-first throughout.
- PROT-007: v476 history row appended to substrate_capability_map_history.md.
- PROT-008: HP founding: CRDT order_indep=1.0 (3-seed); n_reduction flatness=1.0; bundle_relay drop0.5=0.999 (3-seed); bitemporal 0.00136ms/write; sql_rolling max_err=0.018 (3-seed); modern_hopfield all-1.0 (GPU+CPU); membership AUROC=1.0 (3-seed); 4bit drop=0.0. State-transition validator PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 388th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 21 anchors. CLEAN.
- PROT-019: LVH 254->257 (+3: #255 dp_noise + #256 privacy_fixes_cone + #257 privacy_combined).
- PROT-021: All 21 source=remote. No smoke contamination. CLEAN.
- PROT-022: n=1 seed HP anchors (4-bit, GPU-scale, n_reduction, n-sweep, bitemporal): wall-time confirms deterministic or fast-converge; 3-seed anchors (relay, CRDT, corroborate, sparse-key, v1-gate, sql-hybrid, membership, predicate, sql-rolling, confidence-wt, chain3-sparse-key, privacy-fixes x2) confirm seed stability. No HP-fragility concern on multi-seed results.

Cap_map: v475 -> v476 CYCLE 155 (8 HP: w_4bit_quant-DROP0.0-N8192_16384 + modern_hopfield_gpu_scale-ALL1.0-N8192_16384 + bundle_relay-DROP0.5=0.999-3SEED + crdt_quorum-ORDER_INDEP1.0-3SEED + n_reduction-ALPHA_C_FLAT=0.5-ALLSIZE + membership_auroc-AUROC1.0-3SEED + bitemporal-0.00136ms-737Kwrites + sql_rolling-REL_ERR0.018-3SEED + modern_hopfield_n_sweep-N4096_ALL1.0; 3 MIDDLE_BAND: v1_corroboration_gate-FA0.0-RECOVERY0.557 + sql_hybrid-SELECT+SUM_NATIVE-AVG_DUCKDB + predicate_ratio_audit-SEL0.05_PASS-SEL0.10_FAIL; 5 HF: sparse_w_scale-SP0.75_COLLAPSES-4X_CLOSED + sparse_key_coherent-NULL_B10 + confidence_weighted-CEILING_NULL + corroborate_gossip_damp-INVERTED_CATASTROPHIC + chain3_sparse_key-B_EFF=39.51=DENSE; 1 MID_DIAGNOSTIC: llama_eigenspectrum-SRHT_ZERO_EFFECT-PR_PRE=POST; 3 LVH_ATTACK_MISMATCH: #255 dp_noise_injection-DP_NO_BENEFIT + #256 privacy_fixes_cone-CONE_HURTS_BASELINE + #257 privacy_combined_fix-DUPLICATE; HONEST 1129->1150 +21; LVH 254->257 +3; Portfolio 32+82 UNCHANGED; 388th PROT-009 paired commit) (2026-06-07)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.

## v476 -> v477 CYCLE 156 (2026-06-07)

Verdicts processed (8 anchors): crdt_gcounter_aggregate_v1 + predicate_partition_storage_v1 + hotpot_2hop_retrieval_pretest_v1 + hotpot_2hop_full_substrate_v1 + hotpot_2hop_khop_v1 + online_lora_infonce_proxy_v1 + lsh_fanout_norm_cone_llama_v1 + llama_encoder_config_hotpot_v1

### Step 0 honest re-read

All 8 metrics fetched source=remote (bridge stale; direct remote fetch).

- crdt_gcounter_aggregate_v1: HONEST=HARD_PASS (correct). fraction=1.0000; exact distributed COUNT order+duplicate independent. HP threshold verified. No LVH. +1 HONEST.
- predicate_partition_storage_v1: HONEST=HARD_FAIL (correct). flat=614 partitioned=612 ratio=1.00 < 1.1 threshold. No capacity gain confirmed. HF label accurate. No LVH. +1 HONEST.
- hotpot_2hop_retrieval_pretest_v1: HONEST=HARD_FAIL (correct). recall@2hop=0.147 < 0.50 threshold. Naive single-shot retrieval cannot support 2-hop at scale. HF label accurate. No LVH. +1 HONEST.
- hotpot_2hop_full_substrate_v1: HONEST=MIDDLE_BAND (correct). whitening lift=+0.053 >= 0.05 but recall=0.200 NOT >= 0.70 HP threshold. MIDDLE_BAND accurate. No LVH. +1 HONEST.
- hotpot_2hop_khop_v1: HONEST=MIDDLE_BAND (correct). khop lift=+0.053 >= 0.05 but recall=0.200 NOT >= 0.70. NOTABLE: khop achieves identical recall to whitening (0.200=0.200) -- no advantage of K-hop relay over whitening in this pretest scope. MIDDLE_BAND accurate. No LVH. +1 HONEST.
- online_lora_infonce_proxy_v1: HONEST=MIDDLE_BAND (correct). InfoNCE=0.314 > SFT=0.003 (beats SFT) but < base=0.476. MIDDLE_BAND accurate. No LVH. +1 HONEST.
- lsh_fanout_norm_cone_llama_v1: HONEST=MIDDLE_BAND (correct). cone=29.61 < 30 (partial) but NOT < 20 (HP). NOTABLE: raw LSH B_eff=6.80 and L2norm=6.87 both well below target -- L2 normalization alone is adequate; cone adds branching at S=100. MIDDLE_BAND label honest for cone mechanism. No LVH. +1 HONEST.
- llama_encoder_config_hotpot_v1: HONEST=HARD_FAIL (correct). All 6 Llama-1B configs < 0.05 recall@2hop (n=25). HF label accurate; confirms MiniLM mandate for retrieval encoder. No LVH. +1 HONEST.

HONEST: 1150 -> 1158 (+8). LVH: 257 UNCHANGED.

### Cap_map decisions (v476 -> v477)

**(A) CRDT G-counter aggregate (HP -- exact distributed COUNT without coordination):**
crdt_gcounter_aggregate_v1 HP: fraction=1.000 order+duplicate independent. CRDT distributed-architecture annotation (extends cycle-155 crdt_quorum_bundle HP): CRDT G-counter aggregate: exact distributed COUNT fraction=1.000; merge-order and duplicate independent; conflict-free COUNT aggregation native to substrate; CRDT distributed pair now covers commutativity (v476) + exact-COUNT (v477). Filed as annotation to existing distributed-architecture property row. Cycle 156.

**(B) Predicate partition storage (HF -- no capacity gain; partition axis closed for P=4):**
predicate_partition_storage_v1 HF: ratio=1.00 (flat=614, partitioned=612). Zero capacity benefit from predicate partitioning at P=4. Cap_map annotation to predicate/selectivity row: predicate partition storage HF: ratio=1.00 (partitioned=flat at P=4 N=4096); partition overhead erases any capacity gain; capacity improvement axis CLOSED for simple partition at P=4; alternative: P-sweep or composite-predicate indexing needed. Rescue sketches R1-R4 below. Cycle 156.

**(C) HotpotQA 2-hop retrieval pretest (HF -- naive single-shot recall=0.147; retrieval baseline established):**
hotpot_2hop_retrieval_pretest_v1 HF: recall@2hop=0.147 (n=300). Baseline established: naive single-shot retrieval floor for HotpotQA 2-hop is 0.147. Cap_map annotation (PP-35 graph retrieval / multi-hop row): HotpotQA 2-hop pretest: naive recall=0.147; substrate must lift to >=0.70 for HP; both whitening and K-hop achieve +0.053 lift (to 0.200) but remain far from 0.70; encoder upgrade is the key bottleneck. Cycle 156.

**(D) HotpotQA 2-hop full substrate + K-hop (dual MIDDLE_BAND -- whitening and K-hop identical lift):**
hotpot_2hop_full_substrate_v1 + hotpot_2hop_khop_v1: both MIDDLE_BAND, both recall=0.200, both lift=+0.053. Cap_map annotation (HotpotQA multi-hop row): substrate whitening and K-hop relay BOTH lift recall from 0.147 to 0.200 (identical lift=+0.053); K-hop provides zero advantage over whitening in this pretest scope; bottleneck is encoder quality (Llama-1B confirmed poor; MiniLM=0.147 baseline); production-encoder upgrade needed before re-testing K-hop advantage. Cycle 156.

**(E) Online LoRA InfoNCE proxy (MIDDLE_BAND -- InfoNCE beats SFT; both degrade from base):**
online_lora_infonce_proxy_v1 MIDDLE_BAND: InfoNCE=0.314 vs SFT=0.003 vs base=0.476. New annotation (LLM-integration / online-LoRA row): InfoNCE proxy beats SFT (0.314 vs 0.003); SFT catastrophically degrades base recall; InfoNCE retains 66% of base capability; InfoNCE is clearly superior proxy to SFT; retrieval-preserving fine-tuning path is InfoNCE not SFT. Temperature tuning and mixed-loss are the rescue paths. Cycle 156.

**(F) LSH fanout norm-cone Llama (MIDDLE_BAND -- L2norm alone B_eff=6.87; cone degrades at S=100):**
lsh_fanout_norm_cone_llama_v1 MIDDLE_BAND: raw=6.80 L2norm=6.87 cone=29.61 at S=100 (n=800 Llama embeddings). Cap_map annotation (PP-11 Chain3 LSH routing row): Llama LSH fan-out: L2-norm ALONE gives B_eff=6.87 (well below <20 target); cone adds branching at S=100 (cone=29.61, worse than norm-only); key finding: use L2-norm normalization without cone; cycle-154 B_eff=40 was unnormalized; L2-normalized Llama LSH achieves B_eff~7 -- major routing improvement; partially resolves cycle-154 Chain3 LSH branching concern. Cycle 156.

**(G) Llama encoder config hotpot (HF -- Llama-1B pooled embeddings not viable for retrieval):**
llama_encoder_config_hotpot_v1 HF (n=25): all 6 configs < 0.05 recall@2hop; MiniLM ref=0.16. Cap_map annotation (encoder/LLM-integration row): Llama-1B pooled embeddings: all configs (L8/L12/L15, last/mean) < 0.05 recall@2hop; far below MiniLM baseline 0.16; Llama-1B is NOT a viable retrieval encoder for 2-hop HotpotQA; MiniLM mandate confirmed; escalate to Llama-3.2-L15 MTP or dedicated retrieval model. Cycle 156.

### Rescue sketches (PROT-004/006; cheapest-first per [[feedback-rescue-sketch-first-sequencing]])

**Predicate partition storage (HF -- partition capacity closed for P=4):**
R1 (0-compute, ANNOTATION): P=4 ratio=1.00 at N=4096; simple partition overhead matches flat capacity.
R2 (CHEAP, CPU <30min): P-sweep (P=2,8,16) at same N to check if larger P groups help.
R3 (CHEAP, CPU <30min): Composite-predicate indexing (2-key partitions) as alternative to single-key.
R4 (MEDIUM, CPU <2h): Higher-N (N=8192-16384) partition to check if capacity gap opens at larger N.

**HotpotQA 2-hop (MIDDLE_BAND -- encoder upgrade path):**
R1 (0-compute, ANNOTATION): Both whitening and K-hop lift identical (recall=0.200); bottleneck is encoder not routing.
R2 (CHEAP, CPU <30min): Dedicated retrieval model (sentence-t5 or multilingual-E5) as encoder replacement.
R3 (CHEAP, CPU <30min): Multi-hop with document-level bundling (bundle bridge-hop candidates before final hop).
R4 (MEDIUM, GPU <2h): Llama-3.2 L15 MTP as retrieval encoder for HotpotQA 2-hop re-test.

**Online LoRA InfoNCE (MIDDLE_BAND -- base-recall gap):**
R1 (0-compute, ANNOTATION): InfoNCE >> SFT confirmed; SFT catastrophic.
R2 (CHEAP, CPU <30min): Temperature sweep for InfoNCE contrastive loss to tighten negatives.
R3 (CHEAP, CPU <30min): Mixed-loss (InfoNCE + retrieval replay) to preserve base recall.

**LSH fanout L2-norm finding (MIDDLE_BAND -- B_eff=6.87 already viable; confirm S-dependency):**
R1 (0-compute, ANNOTATION): L2-normalized B_eff=6.87 meets <20 target; cone adds branching. Use L2-norm without cone.
R2 (CHEAP, CPU <30min): Confirm L2-norm B_eff at S=50 and S=200 to establish S-dependency.
R3 (CHEAP, CPU <30min): Re-run cycle-154 chain3_lsh_fanout with L2-normalization to confirm B_eff drops from 40 to ~7.

### PROT compliance (v476 -> v477)

- PROT-004/006: No row closures. Predicate partition capacity axis closed for P=4 (4 cheapest-first rescues). HotpotQA retrieval axis MIDDLE_BAND with encoder-upgrade path (4 cheapest-first rescues). Rescue sketches R1 annotation-first throughout.
- PROT-007: v477 history row appended to substrate_capability_map_history.md.
- PROT-008: CRDT G-counter HP (fraction=1.000 exact, order+duplicate independent). Deterministic exact result = HP-founding criteria met. PASS.
- PROT-009: cap_map.md + substrate_capability_map_history.md + decisions log staged atomically; 389th PROT-009 paired commit.
- PROT-018: No _nN binding suffixes on any of 8 anchors. CLEAN.
- PROT-019: LVH 257 UNCHANGED. No new LVH catches.
- PROT-021: All 8 source=remote. No smoke contamination. CLEAN.
- PROT-022: HP anchor (crdt_gcounter) single deterministic result; no HP-fragility concern. All HF anchors unanimous at their thresholds. No HP-fragility concern.

Cap_map: v476 -> v477 CYCLE 156 (1 HP: crdt_gcounter_aggregate-FRACTION1.000-EXACT_COUNT-ORDER+DUP_INDEPENDENT; 4 MIDDLE_BAND: hotpot_2hop_full-WHITENING_RECALL0.200 + hotpot_2hop_khop-KHOP_RECALL0.200-IDENTICAL_TO_WHITENING + online_lora_infonce-INFONCE0.314-SFT0.003-BASE0.476 + lsh_fanout_norm_cone-L2NORM_B_EFF6.87-CONE29.61; 3 HF: predicate_partition_storage-RATIO1.00-NO_GAIN + hotpot_2hop_retrieval_pretest-RECALL0.147-BASELINE + llama_encoder_config-ALL_LT0.05; NOTABLE: L2-norm-only B_eff=6.87 resolves cycle-154 Chain3-LSH B_eff=40 concern; K-hop=whitening at recall=0.200 (bottleneck is encoder); Llama-1B invalid retrieval encoder; InfoNCE>>SFT; HONEST 1150->1158 +8; LVH 257 UNCHANGED; Portfolio 32+82 UNCHANGED; 389th PROT-009 paired commit) (2026-06-07)
Push BLOCKED from sub-agent context; orchestrator main thread executes git push origin main as 1-tool follow-up.
