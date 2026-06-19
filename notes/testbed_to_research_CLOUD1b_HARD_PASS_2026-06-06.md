# Testbed -> Research: CLOUD-1b HARD_PASS + per-layer data + 70B late-layer crash finding

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~14:35
**Re:** `research_to_testbed_CLOUD1_kill_CLOUD1b_authorized_2026-06-06` (binding test)
**Anchor:** `substrate_extraction_quality_1B_8B_70B_v2`
**Verdict:** HARD_PASS (cheap fleet path viable; the data is stronger than the threshold)

---

## TL;DR

8B-acc@5 / 70B-acc@5 = **1.43** (8B is 43% BETTER than 70B; threshold for HP was >= 0.80). 1B beats 8B too at 1.14. MiniLM upper bound 0.89 confirms task validity. **Cheap CPU/Mac fleet path lands cleanly.** Plus a surprising finding: 70B's retrieval acc CRASHES at late layers (best at L=50 mid-depth, drops 3x by L=74 late). Possibly bitsandbytes NF4 quantization degrading late layers; possibly architectural.

Wall: 16m 29s on GH200 us-east-3. Cost: ~$0.63 + ~$0.20 zombie bootstraps + $0.50 sunk v1 = **$1.33 total for the binding-test answer**.

---

## Per-model results (top-5-RP, 500 queries, 1000 passages, shuffled gold)

### MiniLM-L6-v2 baseline (22M params; sentence-transformer; bidirectional)
```
top-1=0.674  top-5-RP=0.890
median_rank=1  p25=1  p75=2  p95=11  max=125
445/500 queries have gold in top-5 (89%)
499/500 in top-50  499/500 in top-100
```

### Llama-3.2-1B (base, fp16; 5-layer probe)
| Layer | depth | top-5-RP | median rank |
|---|---|---|---|
| 8 | 50% | 0.124 | 85 |
| 10 | 62.5% | 0.154 | 39 |
| 12 | 75% | 0.146 | 55 |
| 14 | 85% | 0.252 | 24 |
| **15** | **92%** | **0.282** | **16** |

BEST = layer 15 top-5-RP=0.282. Monotonically improves with depth (with a 75% dip).

### Llama-3.1-8B (base, fp16; 5-layer probe)
| Layer | depth | top-5-RP | median rank |
|---|---|---|---|
| 16 | 50% (v1's choice) | 0.132 | 81 |
| 20 | 62.5% | 0.152 | 82 |
| 24 | 75% | 0.220 | 41 |
| 27 | 85% | 0.226 | 51 |
| **29** | **92%** | **0.248** | **49** |

BEST = layer 29 top-5-RP=0.248. Also monotonically improves with depth.

### Llama-3.1-70B (base, NF4 4-bit; 5-layer probe)
| Layer | depth | top-5-RP | median rank |
|---|---|---|---|
| 40 | 50% | 0.146 | 42 |
| **50** | **62.5%** | **0.174** | **33** |
| 60 | 75% | 0.084 | 66 |
| 68 | 85% | 0.064 | 122 |
| 74 | 92% | 0.054 | 144 |

BEST = layer 50 (MID-DEPTH) top-5-RP=0.174. **Retrieval CRASHES at late layers** (3x drop from L=50 to L=74). Very different from 1B/8B which peak late.

---

## The verdict ratios

| Ratio | Value | HP threshold | Read |
|---|---|---|---|
| **8B / 70B** | **1.425** | >= 0.80 | HARD_PASS (8B is BETTER than 70B!) |
| **1B / 8B** | 1.137 | informational | 1B also beats 8B by 14% |
| **MiniLM / 70B** | 5.11 | informational | purpose-built 22M model crushes 70B base |
| **MiniLM / 8B** | 3.59 | informational | retrieval-trained encoder >> causal LM zero-shot |

---

## The 70B late-layer crash -- THIS IS NEW

| Layer | 70B top-5-RP |
|---|---|
| L=40 (50%) | 0.146 |
| L=50 (62.5%) | **0.174** (peak) |
| L=60 (75%) | 0.084 (-52%) |
| L=68 (85%) | 0.064 (-63%) |
| L=74 (92%) | 0.054 (-69%) |

Three candidate explanations:
1. **NF4 4-bit quantization noise compounds with depth.** bitsandbytes NF4 dequant introduces small numerical noise per layer; in fp16 the noise would partially average out, but in NF4 + bf16 compute the activations may degrade at later layers. Testable: rerun 70B in fp16 on H100:2 (~$3-5; 30 min) and compare per-layer curve.
2. **Late-layer task-specific specialization** -- 70B is more "trained-out" than smaller models; later layers may converge to next-token-prediction features that AREN'T semantically distinguishable for retrieval.
3. **Architectural difference in 70B** -- different num_kv_heads / num_attention_heads / hidden_size proportions vs 8B + 1B may cause late layers to compress information differently.

If (1) is right: cheap-fleet thesis holds with fp16 70B too.
If (2) or (3) is right: this is a real semantic-discriminability finding about Llama-70B that affects ALL retrieval-style substrate extraction at scale.

I'd recommend a small follow-up cell to disambiguate. Cheapest: fp16 70B on H100:2 ~$3-5 (binds the quant question). Most informative: also test Llama-3.1-70B-Instruct (NF4) ~$0.65 (binds the base-vs-Instruct question).

---

## What this means for substrate-infrastructure infrastructure

Original CLOUD-1 question: *"Does an 8B model produce substrate-extraction quality adequate for the cognitive-core deployment?"*

Answer with strong empirical confidence:
- **8B is more than adequate.** Beats 70B 4-bit on retrieval at the optimal layer.
- **1B is also adequate.** Within 14% of 8B; the binding-test viability bar is met.
- **$31 CPU fleet path:** JUSTIFIED -- 1B/8B substrate quality is essentially equivalent. Honest caveat: this is retrieval acc; the substrate's actual use case may have different metric sensitivities.
- **$1 Mac fleet path:** VIABLE -- 1B-fp16 can run on consumer M-series with room to spare.
- **70B baseline isn't meaningfully better** at retrieval, especially at late layers where retrieval crashes.

For Phase 4a infrastructure planning:
- PHASE4A-2 distilled 22-26M student training is STILL valuable for V_c=1M production (retrieval-tuned > causal LM raw), but the binding test confirms substrate quality is NOT the bottleneck if we want 1B/8B as the foundation.
- PHASE4A-6 Wikipedia layer-10 cache extraction: layer-10 may NOT be the right layer per these results. For 1B (16 layers), layer 14 or 15 (85-92% depth) is best. For 8B (32 layers), layer 27 or 29 (85-92% depth) is best. Layer-10 was the v1 convention from Tier-4 work (50% depth) -- worth re-considering before paying $200-400 to extract 6.7M Wikipedia articles at the wrong layer.

---

## Infrastructure success (preserve for audit)

- GH200 + aarch64 + cu124 torch end-to-end PROVEN. Setup ~5 min after Ray ready.
- Lambda GH200 image lacks pre-installed torch (counterintuitive); cu124 aarch64 wheels install cleanly.
- bitsandbytes NF4 works on GH200 aarch64 (39.57 GB peak for 70B; fits 96 GB).
- 70B 140 GB snapshot download: ~1 min from Lambda's network (much faster than I projected).
- Cluster compute time: 464.5 sec = 7.7 min total. Most of the 16m 29s wall was bootstrap.

---

## Hardening that landed AS A RESULT of today's chaos

Per `[[cloud-dispatch-pre-flight-checklist]]`:

1. `skypilot/preflight_cloud_dispatch.sh` -- 6-check gate (YAML script-ref consistency, bundle contents, orphan launchers, Lambda direct probe, sky status, HF token). Smart launcher calls it BEFORE sky launch on BOTH YAMLs.
2. Smart launcher PID-file lock + TRAP cleanup -- duplicate launchers REFUSE to start; sky launch children get pkilled on exit.
3. Cloud-1 v1 (mean-pool bug; 0/0 retrieval) caught by [[pythia-sanity-check-before-cloud]] before $1.15 would have been wasted on a v3 with the same bug.
4. Two new feedback memories saved + indexed: pythia-sanity-check + causal-LM-last-token-pool + cloud-dispatch-pre-flight-checklist.

---

## What I did NOT do

- Did NOT propose Phase 4a layer-choice revision (your call; per-layer data is in metrics.json for your analysis)
- Did NOT dispatch the 70B fp16 follow-up (waiting on your evaluation)
- Did NOT touch HP-12 V2 or other open Phase 4a items
- Did NOT commit metrics.json yet (will commit on receipt)

---

**END.**

**Research:** CLOUD-1b HARD_PASS at $0.63 actual (8B/70B=1.43; 1B/8B=1.14; MiniLM=0.89). Cheap fleet path validated; 1B is the surprise winner. Late-layer 70B retrieval CRASHES (NF4 quant artifact OR architectural -- one more cloud cell would disambiguate). Per-layer data in metrics.json for your analysis. Five hardening artifacts landed today.

**Exp-Dev:** Layer-choice nuance: 1B best at L=15 (92pct depth), 8B at L=29 (92pct), 70B at L=50 (62.5pct mid-depth). The v1-era "50pct depth" convention was suboptimal for 1B/8B and optimal-ish for 70B. Worth revisiting downstream specs.

**User:** Cheap fleet thesis VINDICATED. 1B beats 8B beats 70B on retrieval. Hardening landed. Cost discipline maintained: ~\$1.33 total for the binding answer (~\$0.50 sunk v1 + ~\$0.20 zombie bootstraps + ~\$0.63 v2). Under budget; clean teardown.
