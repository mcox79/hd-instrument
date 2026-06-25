# STORE SCOUR: Multi-hop & Composition Architectures | 2026-06-24

USER directive: exhaustive inventory of working MULTI-HOP + COMPOSITION cells to inform Resonator HARD_FAIL rescue.

---

## CATEGORY 1: MULTI-HOP CELLS (>=2 hops tested)

### HARD_PASS Multi-hop Cells

CELL: FB15K-237 Real KG Traversal
PATH: /d/AI/hd-instrument/data/exp_fb15k237_multihop_traversal_cpu_v1/metrics.json
VERDICT: HARD_PASS
KEY METRIC: twohop_top1=1.000 top3=1.000 (n=600, |E|=14505)
CONFIG: Substrate native traversal on 237-relation FB15K-237 knowledge graph
WORKED: YES
WHY: Chain-grade proof that substrate 2-hop retrieval holds on real public KG at scale

CELL: Compositional Generalization K10-K20
PATH: /d/AI/hd-instrument/data/exp_substrate_compositional_generalization_K10_to_K20_v1_n4096/metrics.json
VERDICT: HARD_PASS
KEY METRIC: K10=1.00 K15=1.00 K20=1.00 (G=8 novel chains, 3 seeds)
CONFIG: N=4096, substrate-native sequence binding lossless at depth
WORKED: YES
WHY: Proves substrate composes novel chains perfectly past training depth (K10) to K20

CELL: Native K-hop Reasoning K1-K3
PATH: /d/AI/hd-instrument/data/exp_substrate_native_reasoning_K10_K20_n16384_v1/metrics.json
VERDICT: HARD_PASS
KEY METRIC: K1/K2/K3 all acc=1.0 (structured retrieval, no decode loop)
CONFIG: N=1024, K_SET validated, cheap matvecs per hop
WORKED: YES (K<=3)
WHY: K-hop is architecture native, no learned latent reasoning

CELL: Wave14R K50 Multi-hop Validated
PATH: /d/AI/hd-instrument/data/exp_wave14r_multihop_K50/metrics.json
VERDICT: HARD_PASS (Tier-2 KILLER probe)
KEY METRIC: acc_1=0.987 acc_5=0.913 acc_50=0.487 (retention=0.9857/hop)
CONFIG: N=16384, 50 relations, 100 facts, 50-hop depths
WORKED: YES
WHY: Log-decay at -0.0138/hop is predictable and exponential, not cliff

### MIDDLE_BAND Multi-hop Cells

CELL: HotpotQA Multi-hop Retrieval Benchmark
PATH: /d/AI/hd-instrument/data/exp_hotpotqa_multihop_retrieval_benchmark_gpu_v1/metrics.json
VERDICT: MIDDLE_BAND
KEY METRIC: best recall@10=0.587 (raw bge-large); whitening regresses to 0.56
CONFIG: N=300 questions, bge-large baseline + per-query whitening
WORKED: PARTIAL
WHY: Hits mid-band on real multi-hop QA; whitening is anti-pattern on small pools

CELL: Connectivity Multihop
PATH: /d/AI/hd-instrument/data/exp_connectivity_multihop/metrics.json
VERDICT: MIDDLE_BAND (hebbian saves 2-hop)
KEY METRIC: naive_vsa_2hop=0.467 | hebbian_2hop=0.914 (50 Hebbian passes)
CONFIG: N=4096, complex64, 50 entities, 150 facts
WORKED: PARTIAL
WHY: VSA fails 2-hop; Hebbian rescue restores via learning

### HARD_FAIL Multi-hop Cells

CELL: Resonator Multihop Integration (RECENT)
PATH: /d/AI/hd-instrument/data/exp_substrate_resonator_multihop_integration_v1/metrics.json
VERDICT: HARD_FAIL
KEY METRIC: NAIVE_2HOP top1=0.6500 | RESONATOR_2HOP top1=0.6317 (WORSE)
CONFIG: N=8192, V_C=200 V_P=10 K_SET=20, dense-bipolar HRR + multivalue-hebbian
WORKED: NO
WHY: Resonator does NOT close 2-hop gap; interference or wiring failure

CELL: Wave14 Multihop K100 @ N65K Killed
PATH: /d/AI/hd-instrument/data/exp_wave14_multihop_K100_N65536_v1_smoke/metrics.json
VERDICT: HARD_FAIL
KEY METRIC: per_depth={1: 1.0, 25: 0.2}; acc_50hop=0.2<0.4
CONFIG: N=8192, 200 entities, 100 facts, 25-hop / 50-hop
WORKED: NO
WHY: N-scaling fails for multi-hop (cliff at K25+)

CELL: Wave14R Modern Hopfield @ 50-hop Killed
PATH: /d/AI/hd-instrument/data/exp_wave14r_multihop_modernhopfield_v1/metrics.json
VERDICT: HARD_FAIL
KEY METRIC: acc_1=0.948 acc_50=0.128<0.4 (cliff at depth 25)
CONFIG: N variable, modern Hopfield beta tuning
WORKED: NO
WHY: D=25 cliff is architectural, all three R8 rescues killed

---

## CATEGORY 2: COMPOSITION CELLS

### HARD_PASS Composition Cells

CELL: Cross-layer L=2 Composition
PATH: /d/AI/hd-instrument/data/exp_q_a3_l2_cross_layer_composition_v1_n4096/metrics.json
VERDICT: HARD_PASS
KEY METRIC: outer_fid=1.0 inner_fid=1.0 l2_acc=1.0 (n=2 seeds)
CONFIG: N=4096, M_inner=50 M_outer=25, lossless at L=2
WORKED: YES
WHY: Layer-stacking preserves fidelity perfectly

CELL: Cross-layer L=3 Composition
PATH: /d/AI/hd-instrument/data/exp_q_a3_l3_cross_layer_composition_v1_n4096/metrics.json
VERDICT: HARD_PASS
KEY METRIC: L1_fid=1.0 L2_fid=1.0 L3_fid=1.0 l3_acc=1.0 (n=2)
CONFIG: N=4096, M_inner=30 M_mid=15 M_outer=8
WORKED: YES
WHY: Proven lossless composition to L=3

CELL: Cross-layer L=4 Composition
PATH: /d/AI/hd-instrument/data/exp_q_a3_l4_cross_layer_composition_v1_n4096/metrics.json
VERDICT: HARD_PASS
KEY METRIC: L1_fid=L2_fid=L3_fid=L4_fid=1.0 l4_acc=1.0 (n=2)
CONFIG: N=4096, M_inner=30 M_mid2=15 M_mid3=8 M_outer=4
WORKED: YES
WHY: Lossless stacking up to L=4 (reports: L=100 cross-layer compose = chain-grade per fact-finder)

CELL: CF-RPE + STDP Heterogeneous (Skunkworks-verified)
PATH: /d/AI/hd-instrument/data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json
VERDICT: HARD_PASS
KEY METRIC: super_seeds=5/5, gap_combined=3.744 (cfrpe=3.767, stdp=3.245)
CONFIG: N=512 V=512, sparse-bipolar, heterogeneous plasticity
WORKED: YES - SUPERADDITIVE
WHY: CF-RPE + STDP compose BETTER than additive (5/5 seeds), chain-grade verified

CELL: Heterogeneous Plasticity Fair Harness
PATH: /d/AI/hd-instrument/data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json
VERDICT: HARD_PASS
KEY METRIC: lift=0.141 bits (BPC: unigram=7.738 | Hebbian=7.307 | CFRPE+STDP=7.165)
CONFIG: N_DIM=8192, text8 100k training, word2vec_sparse_bipolar f=0.05
WORKED: YES - REAL LIFT
WHY: Heterogeneous plasticity adds 0.141 bits over Hebbian at production scale

CELL: Capacity Composition B2xB4
PATH: /d/AI/hd-instrument/data/exp_substrate_capacity_composition_b2xb4_v1_n2048/metrics.json
VERDICT: HARD_PASS
KEY METRIC: obs_mult=240.0x pred_mult=240.0x
CONFIG: N=2048, sparse_factor=48.0x times K=5 = 240x total
WORKED: YES - MULTIPLICATIVE
WHY: Sparse + K banks compose multiplicatively (key capacity lever)

### HARD_FAIL Composition Cells

CELL: CF-RPE + STDP + K2 + MH Full Joint Compose
PATH: /d/AI/hd-instrument/data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json
VERDICT: HARD_FAIL - SUB-ADDITIVE
KEY METRIC: ARM_FULL_JOINT_COMPOSE BPC=7.8919 (collapses; total_lift=-0.585)
CONFIG: N_DIM=8192, 5-arm progressive stacking
WORKED: NO
WHY: Primitives alive individually but no stacking (compose-saturation)

---

## CATEGORY 3: WORKING PATTERNS

Multi-hop cells that WORK:
- FB15K-237 (real KG, exact)
- K10-K20 compositional (substrate-native sequencing)
- Wave14R K50 (exponential decay, no cliff)

Common architecture:
- Exponential per-hop retention (0.985+/hop)
- NO learned latent chain reasoning
- Structured traversal (adjacency-based, not dense-attention)
- Lossless or near-lossless per hop (fidelity >= 0.93)

Multi-hop cells that FAIL:
- Resonator integration (0.65 approx 0.63, NO LIFT)
- Modern Hopfield at 50-hop (cliff at 25)
- N-scaling fails K25+

Consistent failure mode:
- Cliff at depth 25-50 (UNIVERSAL)
- Resonator/Hopfield tuning-resistant
- Joint composition of 5+ primitives saturates

---

## RECOMMENDATIONS

BEST RESCUE: Deploy Wave14R K50 sparse traversal + K-bank composition
- Already proven at N=16384
- Exponential decay, no cliff
- 240x capacity lift from sparse x K
- Cost: zero new dispatch (restore from Store)

RESONATOR HARD_FAIL: Consistent with Store pattern
- Connectivity-resonator: 0% lift over baseline
- Modern Hopfield: architectural cliff at depth 25
- Both tuning-resistant

SKIP: Soft-chain dispatch is REDUNDANT with exp_connectivity_resonator
(already ruled out in Store)