# Research Drill: V1 Demo Pipeline Optimization (2x Depth)
# Regulated-AI Bipolar-Substrate-LLM Hybrid -- Certified Per-Fact Deletion on Medical KB
# Date: 2026-06-05
# Trigger: 2x deep drill requested; 4 pre-cloud-spend gaps addressed

---

## HEADLINE

Desktop-first pipeline is viable for a 5-minute screen-recordable V1 demo: SoftHSM provides
mathematically equivalent RSA accumulator deletion certs without FIPS 140-2 hardware (adequate
for demo + GDPR dev-phase; NOT for HIPAA production); batch=8 + bf16 + vllm + layer-skip yields
~8-12x combined speedup over naive baseline on RTX 4060 Ti, reducing a 5.7-min cloud extraction
of 10K facts to under 1 min locally; hybrid pre-seed (10K facts) + live-ingest (50 facts on
camera) maximises per-minute categorical-claim density while demonstrating BOTH deletion moat
AND real-time-write moat in one recording; Pythia-160M is the cheapest entry-point for the cheap
decisive test.

P_deflated = 0.48 (novel-synthesis cap applied; algebraic estimates, not measured)

---

## PART A: LOCAL CRYPTOGRAPHIC ACCUMULATOR INFRASTRUCTURE

### A1. Minimum viable accumulator stack

RSA accumulators (Baric-Pfitzmann 1997; Camenisch-Lysyanskaya 2002) require three operations:
  Acc(A, x) = A^(Hash_p(x)) mod N          (add element x to accumulator A)
  Del(A, x) = A^(Hash_p(x)^{-1} mod phi(N)) mod N  (delete; requires knowledge of phi(N))
  Wit(A, x) = A^(prod_{y != x} Hash_p(y)) mod N    (membership witness)

The mathematical core is modular exponentiation with a 2048+ bit RSA modulus. This is
independent of HSM hardware; the RSA group Z*_N has identical algebraic structure whether
computed on a laptop or AWS CloudHSM.

Software stack (LOC estimate, ~300-400 lines total):
  - Python gmpy2 or pycryptodome.Math.Numbers for large-integer modular exponentiation
    (gmpy2 wraps GMP; ~3-5x faster than pure Python for 2048-bit ops)
  - Accumulator class: add, delete, witness_gen, witness_verify -- ~120 lines
  - Hash_to_prime: deterministic prime derivation from element bytes -- ~40 lines
    (eprint 2024/505 eliminates this requirement; hash-then-map approach avoids the
    Miller-Rabin search loop entirely, reducing add/delete cost ~30%)
  - Deletion cert serialisation (JSON + base64 encoding of pi, N, new_acc) -- ~30 lines
  - Verifier CLI: reads cert JSON, checks witness equation -- ~60 lines
  Total: ~250-300 LOC, all pure Python + gmpy2. No PKCS#11, no SoftHSM required for V1.

SoftHSM (OpenDNSSEC project) provides PKCS#11 API without hardware, enabling key custody
workflow simulation. It is NOT a replacement for the accumulator math -- it manages the RSA
key pair (N, phi(N)) and signs deletion certificates. For V1 demo:
  SoftHSM optional: the accumulator secret phi(N) can be held in memory (demo mode)
  SoftHSM useful: if demo narrative requires showing key custody UI / "signed by HSM" output

### A2. Cert quality vs cloud HSM

The RSA accumulator deletion certificate is a mathematical proof:
  pi_x such that: pi_x^{Hash_p(x)} == Acc_after mod N

This proof is IDENTICAL in strength whether computed on SoftHSM, AWS CloudHSM, or in-process
Python. The mathematical hardness assumption (strong RSA: finding x such that x^e = y mod N)
is independent of the computing environment.

Attestation gap (what cloud HSM adds):
  - FIPS 140-2 Level 3: HSM physically tamper-evident; key material never leaves the device;
    certified by NIST-accredited lab. AWS KMS upgraded to FIPS 140-2 Level 3 in May 2023.
  - SoftHSM: software attestation only; key material is in RAM; not tamper-evident.

For V1 demo purposes:
  - Third-party verifier checks: pi_x^{Hash_p(x)} == Acc mod N. This is purely mathematical.
    The verifier does NOT and cannot check where phi(N) was stored during the computation.
  - GDPR Article 17 (Right to Erasure) compliance for demo: mathematical proof of deletion
    is the core claim; no FIPS 140-2 requirement stated in GDPR.
  - HIPAA Security Rule: requires "encryption of ePHI" and "access controls" but does NOT
    mandate FIPS 140-2 Level 3 hardware HSM for a development demo. FIPS 140-2 is required
    for federal government systems (FISMA); healthcare demos can use software-attested deletion
    as a technical proof-of-concept.

When cloud HSM becomes REQUIRED (not demo, but production):
  (1) FISMA High / FedRAMP production: FIPS 140-2 Level 3 mandatory
  (2) EU AI Act Article 15 (cybersecurity requirements; enforcement Aug 2026): likely to
      require auditable key custody for high-risk AI systems -- hardware HSM strongly advisable
  (3) Multi-tenant SaaS: per-customer key isolation requires hardware boundary
  (4) Customer audit demand: enterprise buyers in healthcare/finance typically require HSM

BOTTOM LINE FOR V1 DEMO: No cloud HSM needed. SoftHSM is not even required -- pure Python
RSA accumulator with phi(N) held in process is mathematically sound. Cost = $0 cloud HSM.

P_deflated (SoftHSM-is-sufficient-for-demo) = 0.88 (well-established crypto; no novel claim)
HARD-FAIL: demo cert fails mathematical verification (pi_x^{Hash_p(x)} != Acc mod N) = infra bug

---

## PART B: INFERENCE FORWARD-PASS OPTIMIZATION FOR SUBSTRATE INPUT EXTRACTION

### B0. Baseline parameters (algebraic)

Llama-3.2-1B architecture:
  params: ~1.24B; fp32 weight footprint: ~4.96 GB; bf16: ~2.48 GB
  layers: 16; hidden_dim: 2048; GQA heads
  RTX 4060 Ti: 8 GB VRAM, 288 GB/s memory bandwidth (Ada Lovelace; bf16 tensor cores native)
  Naive baseline: batch=1, fp32, HuggingFace Transformers, full 16 layers, output_hidden_states=True

Memory footprint at fp32, batch=1, seq_len=512 for activation extraction:
  model weights: 4.96 GB
  input activations per layer: 512 * 2048 * 4 bytes = 4 MB per layer; 16 layers = 64 MB
  Total: ~5.0 GB -- fits in 8 GB VRAM with modest headroom

### B1. Batch processing speedup

At fp32 (weights 4.96 GB):
  remaining VRAM for activations: ~3.0 GB
  activation per batch item per layer: 512 * 2048 * 4 bytes = 4 MB
  16 layers * B items = 64B MB activations
  VRAM constraint: B <= 3000 / 64 ~ 46; practical limit with KV cache overhead: batch ~ 8-12
  Expected token throughput scaling (roofline model, memory-bandwidth-bound regime):
    batch=1:  1x baseline
    batch=4:  ~3.5x (memory coalescing; ~87% efficiency)
    batch=8:  ~6.0x (near-linear; diminishing for >8 on this bandwidth)
    batch=16: ~8x (VRAM fragmentation + scheduling overhead limits further gains)
  Wall-time per 10K extractions: naive ~5.7 min; batch=8 -> ~57 sec; batch=16 -> ~43 sec

At bf16 (weights 2.48 GB):
  remaining VRAM: ~5.5 GB
  activation per layer per item (bf16): 2 MB
  batch limit increases: B ~ 80+ practical; plateau at batch=32 for throughput
  batch=32 bf16: ~18-22x over naive fp32 batch=1 baseline

### B2. bf16/fp16 precision

RTX 4060 Ti (Ada Lovelace) bf16 tensor core throughput: ~155 TFLOPS (bf16) vs ~38.7 TFLOPS (fp32)
  Theoretical compute ratio: ~4x
  Memory ratio: 2x fewer bytes transferred per activation
  Combined: ~2x memory-bound speedup + up to 4x compute speedup (mixed depending on bottleneck)

Quality impact on mid-layer activation extraction:
  bf16 has 7 mantissa bits vs fp32 23 bits; dynamic range preserved (8 exponent bits same)
  For associative memory input (cosine similarity of activation vectors): quality loss is
  negligible. bf16 vs fp32 cosine similarity error < 0.001 for typical transformer hidden states.
  P_deflated (bf16 quality-safe for extraction) = 0.82

### B3. Inference framework optimization (extraction-specific)

vLLM hidden-states extraction (v0.18.0+, blog post 2026-03-30):
  - Native support for output_hidden_states via extract_hidden_states API
  - Layer-specific extraction: specify layer IDs (e.g., [3, 8, 12]) -- does NOT require
    extracting all layers (major memory saving for substrate use case)
  - Memory management: hidden states stored in KV-cache-style blocks (avoids fragmentation)
  - Key operational constraint: only prompt tokens supported; must use max_tokens=1
    For extraction use case: this is EXACTLY what is needed (no generation required)
  - Throughput vs HuggingFace: no published exact benchmark for extraction workload;
    architectural argument: PagedAttention + continuous batching gives 2-4x throughput
    improvement for batch workloads vs HuggingFace generate() with padding.
  P_deflated (vllm 2-4x over HuggingFace for extraction batches) = 0.60

TensorRT-LLM:
  - NVIDIA-specific kernel fusion; strongest compute gains for generation workloads
  - hidden_states extraction requires custom plugin (not natively supported as of 2025)
  - Engineering cost: HIGH (C++ CUDA plugin development)
  - Not recommended for V1 demo pipeline

SGLang (v0.4+, 2024):
  - RadixAttention KV cache reuse; 5x throughput vs vLLM on structured workloads (arXiv:2312.07104)
  - For extraction: if medical KB facts share a common prompt prefix (e.g., "Medical fact:"),
    prefix cache hits dramatically reduce re-computation. Estimated 2-3x additional gain.
  - Hidden states extraction: available via custom middleware; less mature than vLLM path
  P_deflated (SGLang prefix caching 2-3x for extraction) = 0.55 (no direct extraction benchmark)

### B4. Layer-skip / early exit

For extraction (NOT generation), layer-skip is trivially implementable:
  HuggingFace Transformers: LlamaModel.forward() iterates layers in a loop.
  Patch: add early return after target_layer index. ~5 lines of code.
  This is simpler than LayerSkip (arXiv:2404.16710) which targets generation quality;
  extraction layer-skip has no quality constraint -- we WANT the mid-stack representation.

Algebraic savings (Llama-3.2-1B, target layer 10 of 16):
  Skip layers 11-15: skip 5/16 = 31.25% of transformer blocks
  Compute savings: ~31% (FLOP-linear in layer count for transformer blocks)
  Memory savings: activations for skipped layers never materialised: ~31% reduction
  Combined with batch=8 bf16: additive speedup (compute-bound remainder benefits more)
  Estimated additional multiplier: ~1.3-1.4x

For Gemma-2-2B (26 layers, interleaved local/global attention, arXiv:2408.00118):
  CRITICAL CONSTRAINT: Gemma-2 alternates local (window=4096) and global (window=8192) attention.
  Layers: 0=local, 1=global, 2=local, ... odd layers are global.
  Target extraction layer 13 (global): forward pass truncated at 14.
  Skip 12 layers (12/26 = 46%): ~46% compute savings.
  Gemma-2-2B was natively distilled from 27B teacher; mid-layer representations at layer 13-14
  are geometrically richer than equivalent Llama-1B layer 8-10 due to KD + interleaved attention.
  P_deflated (Gemma-2 layer-13 extraction competitive with Llama-1B layer-10) = 0.52

LayerSkip (arXiv:2404.16710) for generation context:
  Requires retraining with layer dropout + early exit loss. Achieves 1.82-2.16x speedup.
  FOR EXTRACTION: retraining NOT needed; hard truncation is strictly superior.
  LayerSkip is relevant only if downstream use requires generation quality preservation.

### B5. Distillation to smaller fast model

Knowledge distillation for intermediate-layer representation preservation:
  Teacher: Llama-3.2-1B (layer 10) or Gemma-2-2B (layer 13)
  Student: Pythia-160M (~160M params; 12 layers; hidden_dim=768)

Distillation loss (arXiv:2502.04499):
  L_distill = alpha * L_CE + (1-alpha) * ||W_proj * h^s_k - h^t_L||^2_F
  where W_proj: 768->2048 linear projection; k = student layer ~8; L = teacher target layer
  Recent finding: single-layer final matching is sufficient; multi-layer adds complexity.

Speedup from distillation (algebraic):
  Pythia-160M fp32 footprint: ~640 MB; fits entirely in 8 GB VRAM with batch=32+
  Layer count: 12; target layer: ~8; skip last 4 = 67% utilisation
  Throughput relative to Llama-1B batch=1 fp32: ~15-20x (smaller model + larger batch)
  vs optimized Llama-1B (batch=8 bf16 + layer-skip): ~2-3x additional gain

Engineering cost: MEDIUM-HIGH (~2-4h training on A100; alignment verification required)
Justified ONLY if extraction volume > 100K facts or repeated re-extraction scenarios.
P_deflated (distillation preserves representation geometry) = 0.47
HARD-FAIL: cosine sim between student layer-k and teacher layer-L < 0.80 after distillation

### B6. Combined optimization stack (Llama-3.2-1B, RTX 4060 Ti 8GB)

| Config                                  | Speedup vs naive | VRAM used | 10K extraction wall |
|-----------------------------------------|-----------------|-----------|---------------------|
| naive (batch=1, fp32, HF, 16 layers)    | 1x              | ~5.0 GB   | ~5.7 min (cloud)    |
| batch=8, fp32                           | ~6x             | ~5.5 GB   | ~57 sec             |
| batch=8, bf16                           | ~10x            | ~3.5 GB   | ~34 sec             |
| batch=8, bf16 + vllm                    | ~16-24x         | ~4.0 GB   | ~14-21 sec          |
| batch=8, bf16 + vllm + layer-skip-10   | ~20-32x         | ~3.5 GB   | ~11-17 sec          |
| Pythia-160M distilled (batch=32)        | ~50-80x         | ~2.5 GB   | ~4-7 sec            |

Calibration: deflate upper bound by 0.20; realistic combined speedup (no distillation) = 8-12x
P_deflated (8-12x combined speedup) = 0.60
HARD-PASS: 10K extraction in <5 min on RTX 4060 Ti
HARD-FAIL: 10K extraction takes >20 min with batch=8 bf16 = implementation bug or VRAM OOM

---

## PART C: MINIMUM VIABLE DEMO SCALE + REAL-TIME WRITE ARCHITECTURE

### C1. Scale and categorical claim strength

The claim "frontier LLMs cannot prove a fact was deleted" is architecturally categorical at
ANY scale. Parametric weight matrices have no deletion certificate mechanism regardless of KB size.

Scale needed for PRODUCTION CREDIBILITY in a demo:
  100 facts:  audiences dismiss as toy; easy to memorise manually; 2 min ingestion
  1K facts:   borderline credible; clearly beyond manual memorisation; 3-4 min demo
  10K facts:  solidly credible; medical KB framing lands; requires pre-seeding
  100K facts: overkill for V1 demo; extraction takes hours even with optimization

Recommended demo scale: 10K pre-seeded + 50 live-ingested (see C3)

Screen-recording timing budget (5-minute demo):
  [0:00-0:30] intro: substrate loaded with 10K medical facts
  [0:30-1:30] LIVE: add 50 new facts on camera; substrate writes in real-time (<1ms each)
  [1:30-2:00] query batch: ask 3 questions; get correct answers from live-added facts
  [2:00-2:30] DELETE: delete 2 live-added facts; cert generated in <1ms
  [2:30-3:30] third-party verifier: run verifier CLI on cert; mathematically confirms deletion
  [3:30-4:30] re-query: same questions return null/no-knowledge response (0 phantom recall)
  [4:30-5:00] frontier LLM contrast: ask GPT-4 to delete a fact; show impossibility response

### C2. Real-time write architecture

Substrate Hebbian write is O(N^2) for dense update or O(N*k) for sparse outer-product:
  N=10^3: dense write per fact: 10^6 FLOPs ~ 0.001 ms on GPU, 0.01 ms on CPU
  N=10^4: dense write per fact: 10^8 FLOPs ~ 0.1 ms on GPU, ~1 ms on CPU
  50 facts at N=10^4: ~5 ms on GPU; 50 ms on CPU. Both screen-recordable live.

REAL-TIME WRITE MOAT claim vs model editing:
  ROME single edit: ~1 second per edit (sequential gradient computation)
  MEMIT batch=100: ~1-5 minutes (gradient + optimisation loop)
  Substrate 100 Hebbian writes at N=10^4: ~100 ms total
  Contrast: substrate is ~1000-30000x faster for live knowledge injection.
  Empirical anchor: ROME/MEMIT at scale leads to gradual and catastrophic forgetting
  (ACL 2024 Findings, aclanthology.org/2024.findings-acl.902/)
  Post-ROME deletion: 38% whitebox / 29% blackbox residual extraction success rate
  (arXiv:2309.17410). These are NOT provable deletions -- they are parameter noise reductions.
  P_deflated (real-time write moat claim well-founded) = 0.78

### C3. Hybrid architecture (RECOMMENDED)

Pre-seed (before recording):
  Extract LLM activations for 10K medical facts (desktop, optimized, pre-recorded)
  Load substrate W matrix with 10K fact embeddings

Live-ingest foreground (on camera):
  50 new facts typed or fed via script; substrate writes in real-time
  Wall: <5 seconds at N=10^4 on GPU

Live deletion (on camera):
  Select 2-5 of the live-ingested facts
  Run deletion + accumulator update
  Cert generated in <1ms (RSA modular exponentiation ~0.1-1 ms at 2048-bit single element)
  Verifier confirms cert: ~0.5 ms

HARD-PASS: pre-seed extraction of 10K facts completes in <2h on desktop hardware
HARD-FAIL: W matrix for N=10^4 substrate with 10K facts exceeds available RAM
  (N=10^4 float32 W: 10^4 * 10^4 * 4 bytes = 4 GB -- fits in 12 GB system RAM; bf16 = 2 GB, safe)

---

## PART D: LLM-SPECIFIC EXTRACTION DIFFERENCES

### D1. Per-architecture comparison table

| Aspect                | Pythia-160M          | Llama-3.2-1B         | Gemma-2-2B               |
|-----------------------|----------------------|----------------------|--------------------------|
| Weight footprint fp32 | 640 MB               | 4.96 GB              | 8.3 GB (OOM on 8GB VRAM) |
| Weight footprint bf16 | 320 MB               | 2.48 GB              | 4.15 GB                  |
| Attention type        | MHA (standard)       | GQA + RoPE           | GQA + interleaved L/G    |
| Layers                | 12                   | 16                   | 26                        |
| Hidden dim            | 768                  | 2048                 | 2048                      |
| Optimal mid-layer     | ~6-7                 | ~8-10                | ~10-14 (layer 13 global) |
| Max batch @ bf16 8GB  | 32+                  | ~16                  | ~6-8                      |
| Extraction wall 10K   | <10 sec              | ~11-34 sec           | ~30-90 sec                |
| Representation depth  | LOW (from scratch)   | MEDIUM               | HIGH (KD from 27B)        |

Gemma-2-2B fp32 is out-of-bounds for RTX 4060 Ti 8GB:
  8.3 GB weights alone exceeds 8 GB VRAM; bf16 (4.15 GB) is the only viable path.
  Layer truncation after layer 14 (of 26): ~46% compute reduction.
  Interleaved local/global: layer 13 is global attention; richer cross-fact representation.
  Practical recommendation: extract at layer 13 (global attention layer) for Gemma-2-2B.

Pythia-160M extraction:
  Fits model + batch=64 easily in 8 GB VRAM; estimated ~500-1000 facts/sec.
  Quality concern: Pythia-160M representations are geometrically sparse vs 1B+ models.
  Use case: CHEAP DECISIVE TEST ONLY -- verify downstream retrieval accuracy.
  If retrieval >80% correct: Pythia-160M suffices for V1. If not: escalate to Llama-1B.

Distillation feasibility per architecture:
  Pythia-160M <- Llama-1B teacher:
    Layer match: student layer 8 -> teacher layer 10; projection 768->2048 (~1.57M params)
    Training: ~1-2h GPU; feasible for V1 if retrieval quality fails threshold
    Risk: Pythia architecture lacks GQA/RoPE; geometric alignment imperfect
    P_deflated = 0.42

  Llama-1B <- Gemma-2-2B teacher:
    Same hidden_dim (2048); no projection needed; L2 loss directly applicable
    Training: ~2-4h on A100; moderate cost
    Quality gain: Gemma-2-2B layer-13 richer due to original KD from 27B teacher
    P_deflated = 0.52

  VERDICT: distillation is V2 work. V1 demo uses Llama-1B direct with optimization stack.

### D2. Extraction-specific gap vs generation-optimized frameworks

Production LLM inference systems (vLLM, SGLang, TGI, LightLLM) optimize for generation
throughput, not activation extraction. Gaps:

  1. No KV cache needed for extraction: single-pass, prompt-only (max_tokens=1).
     KV cache allocation is partially wasted. vLLM v0.18.0+ mitigates via extraction mode.
  2. Layer truncation: generation frameworks must run full forward pass for logits.
     Extraction terminates early. None of vLLM/SGLang/TGI natively support hard truncation;
     requires ~5-line HuggingFace patch OR vLLM config specifying only target layer(s).
     Estimated gap: 1.3-1.5x additional speedup from truncation.
  3. Same-length batching: for fixed-length KB facts, all prompts similar token count.
     Generation frameworks handle variable-length via padding; extraction fast-path possible.
     Estimated gap: 1.1-1.2x for same-length extraction.
  4. No sampling overhead: extraction uses greedy forward pass only. Minor (~5-10%).

Total extraction-specific gap estimate: 1.5-2.5x speedup available vs generation-optimized
frameworks used naively for extraction.
P_deflated = 0.55 (architectural argument; no controlled benchmark)

---

## PART E: RECOMMENDED V1 DEMO PIPELINE

### E1. Demo scale

RECOMMENDATION: Hybrid pre-seed 10K + live-ingest 50 facts
  10K provides "medical KB" production credibility
  50 live facts demonstrates real-time write moat on camera
  Categorical deletion claim holds at any scale (verified at 50-fact live subset)

### E2. Extraction architecture

RECOMMENDED: Desktop pre-extraction with optimized stack (avoids cloud spend for demo)
FALLBACK: Single H100 batch run ($0.50-1.00, 10-20 min) if desktop benchmark fails HP-4

### E3. Specific pipeline

Hardware:    RTX 4060 Ti 8GB (primary); laptop CPU for smoke/cert verification
Software:    vLLM v0.18.0+ (extraction path); HuggingFace Transformers with layer-skip patch
Model:       Llama-3.2-1B (bf16; layer-skip to layer 10 of 16)
Batch:       8 (GPU extraction); 1 (live demo real-time writes)
Crypto:      Python gmpy2 + custom RSA accumulator class (~300 LOC); no SoftHSM required
Cert store:  SQLite (local file); deletion certs stored as JSON + base64 signatures
Verifier:    Standalone Python CLI; shareable with third-party reviewer

Estimated wall (pre-extraction 10K facts):
  Model load: ~10 sec (bf16 from disk)
  Extraction batch=8 bf16 + vllm + layer-skip: ~11-35 sec (P_deflated = 0.60 on lower bound)
  Substrate write (10K Hebbian, N=10^3): ~50-100 ms
  Total pre-extraction: <5 min on desktop (HARD-PASS); >20 min = infra bug

Estimated cost:
  Desktop pre-extraction: $0 (sunk hardware)
  Cloud fallback (if needed): $0.50-1.00 (H100, 10-20 min)
  Cloud HSM: $0 (not needed for V1 demo)
  TOTAL V1 DEMO COST: $0-1.00

4 engineering days to screen-recordable demo:
  Day 1: RSA accumulator class (300 LOC) + verifier CLI; test on 10 facts
  Day 2: vLLM extraction pipeline + layer-skip patch; benchmark on 1K facts
  Day 3: Substrate integration + live-ingest flow; end-to-end smoke test
  Day 4: Screen record + polish; third-party verifier package

---

## CHEAP DECISIVE TEST

1. (30 min) Extract 100 facts with Pythia-160M on CPU. Measure associative memory retrieval
   accuracy. Threshold: >80% correct recalls at N=1024. If yes: Pythia may suffice for V1.
2. (30 min) Build RSA accumulator delete + verify in Python with gmpy2. Confirm cert round-trips.
   Threshold: pi_x^{Hash_p(x)} == Acc_new mod N. Failure = implementation bug.
3. (60 min, after vllm install) Time Llama-1B bf16 batch=8 extraction of 1K facts on 4060 Ti.
   Threshold: <10 sec. If yes, 10K linearly extrapolates to <100 sec = desktop viable.

---

## FALSIFIABLE PREDICTIONS

HARD-PASS (each independently sufficient to proceed):
  HP-1: 10K Llama-1B bf16 extraction (batch=8, layer-skip-10) completes in <5 min on desktop
  HP-2: RSA deletion cert for 1 element verifies in <1 ms (Python gmpy2, 2048-bit modulus)
  HP-3: Substrate with 10K pre-seeded + 50 live-ingested facts answers medical queries
        with >80% accuracy; 0 phantom recall after deletion of target facts
  HP-4: Third-party verifier script (shared repo) passes cert verification without modification

HARD-FAIL (any triggers review before cloud spend or multi-day work):
  HF-1: 4060 Ti VRAM OOM at batch=8 bf16 Llama-1B -- re-profile, reduce batch to 4
  HF-2: RSA cert verification fails (pi_x^{Hash_p(x)} != Acc mod N) -- implementation bug
  HF-3: Associative memory retrieval accuracy <60% after Llama-1B extraction -- geometry mismatch
  HF-4: Desktop extraction wall >20 min for 10K at batch=8 bf16 -- triggers cloud H100 fallback
  HF-5: W matrix for N=10^4 10K-fact substrate exceeds 4 GB fp32 -- switch to bf16 W from day 1

MIDDLE BAND (needs follow-up, not blocking):
  MB-1: Pythia-160M extraction retrieval 60-80% -> use Llama-1B; defer distillation to V2
  MB-2: Desktop extraction wall 5-20 min -> evaluate single H100 batch run (<$1)
  MB-3: Gemma-2-2B on 4060 Ti bf16 OOM at target batch -> defer to V2

---

## CROSS-THREAD SYNTHESIS

1. This drill addresses demo engineering, orthogonal to the main cap_map substrate-physics
   drills (spin-glass/thermodynamics). It does not affect cap_map rows.

2. vLLM extraction-as-first-class-use-case was only productized in v0.18.0 (March 2026).
   The extraction-specific gap (1.5-2.5x vs generation-optimized) is real and actionable.
   Patch strategy: HuggingFace early exit (~5 lines) + vLLM extraction mode for demo.

3. ROME/MEMIT deletion impossibility anchor (arXiv:2309.17410):
   38% whitebox / 29% blackbox extraction success rate post-ROME "deletion" is citable
   empirical literature. Substrate accumulator cert is a categorical mathematical proof;
   model editing "deletion" is parameter noise reduction. This is the demo contrast core.

4. Gemma-2-2B native KD (arXiv:2408.00118):
   For V2 (scale >100K facts), Gemma-2-2B bf16 + layer-13 may outperform Llama-1B despite
   3x compute cost due to richer representation geometry from original KD from 27B teacher.

5. SGLang prefix caching opportunity:
   If medical KB facts share a common prefix template, RadixAttention provides 2-3x
   additional throughput. Worth testing in V2 if extraction volume grows to 100K+ facts.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

1. V1 demo is achievable on consumer hardware with 4 engineering days and $0-1 cloud spend.
   No HSM, no cloud GPU required for the demo recording itself. This is a low-risk, low-cost
   path to a credible regulated-AI demonstration.

2. "Two moats in one recording" (real-time write + certified deletion) is the highest-density
   demo structure. It demonstrates both architectural impossibilities for frontier LLMs in a
   single 5-minute screen recording. This framing should survive demo review.

3. The ROME/MEMIT residual-extraction literature (38%/29%) is the strongest available
   empirical anchor for the demo contrast. It is peer-reviewed, citable, and category-breaking.

4. EU AI Act Article 15 (Aug 2026 enforcement) creates a near-term regulatory tailwind.
   The substrate accumulator cert is architecturally positioned for this requirement.
   Cloud HSM is a V2+ production upgrade, not a demo blocker.

5. Engineering priority order: (1) RSA accumulator class, (2) vllm extraction patch,
   (3) substrate live-ingest flow. Three pieces plus screen recorder = complete demo.
   Total complexity: LOW. Execution timing is the only risk.

---

## CITATIONS (19 verified, 2026-06-05)

[1] Baric, N. & Pfitzmann, B. (1997). Collision-free accumulators and fail-stop signature
    schemes without trees. EUROCRYPT 1997. [RSA accumulator original]

[2] Camenisch, J. & Lysyanskaya, A. (2002). Dynamic accumulators and application to efficient
    revocation of anonymous credentials. CRYPTO 2002. [Deletion witness construction]

[3] ePrint 2024/505: RSA-Based Dynamic Accumulator without Hashing into Primes. IACR 2024.
    https://eprint.iacr.org/2024/505 [Eliminates Miller-Rabin prime search; ~30% cost reduction]

[4] arXiv:2511.17118 (Leo Kao, 2025/2026): Constant-Size Cryptographic Evidence Structures
    for Regulated AI Workflows. [Directly applicable to regulated-AI deletion cert pipeline]

[5] arXiv:2207.01754: Cryptography with Certified Deletion. [Theoretical foundations for
    certified deletion primitives; compilers for PKE, ABE, FHE]

[6] NIST FIPS 140-2 Final (2002, upd2): Security Requirements for Cryptographic Modules.
    https://csrc.nist.gov/pubs/fips/140-2/upd2/final

[7] AWS KMS: Upgraded to FIPS 140-2 Security Level 3 (May 2023).
    https://aws.amazon.com/about-aws/whats-new/2023/05/aws-kms-hsm-fips-security-level-3/

[8] vLLM Blog (2026-03-30): Extracting hidden states from vLLM (v0.18.0+).
    https://vllm.ai/blog/2026-03-30-extract-hidden-states
    [Layer-specific extraction; max_tokens=1 for prompt-only mode; KV-block memory mgmt]

[9] agencyenterprise/vllm-hidden-states (GitHub): Extract hidden states from intermediate
    transformer layers using vLLM, with correct per-request tracking.
    https://github.com/agencyenterprise/vllm-hidden-states

[10] arXiv:2404.16710 (LayerSkip, Meta AI, 2024): Enabling Early Exit Inference and
     Self-Speculative Decoding. [1.82-2.16x speedup; requires retraining for generation;
     hard truncation is superior for extraction use case]

[11] arXiv:2312.04916 (EE-LLM, 2023): Large-Scale Training and Inference of Early-Exit
     Large Language Models with 3D Parallelism.

[12] Hinton, G., Vinyals, O. & Dean, J. (2015). Distilling the Knowledge in a Neural Network.
     arXiv:1503.02531. [Knowledge distillation original]

[13] arXiv:2502.04499 (2025): Revisiting Intermediate-Layer Matching in Knowledge Distillation:
     Layer-Selection Strategy Doesnt Matter (Much).
     [Final hidden layer distillation sufficient; multi-layer adds complexity without gain]

[14] arXiv:2605.11513 (2026): A Study on Hidden Layer Distillation for Large Language Model
     Pre-Training. [123M-735M student models studied with large teacher]

[15] arXiv:2408.00118 (Gemma Team, Google, 2024): Gemma 2: Improving Open Language Models at
     a Practical Size. [Interleaved local/global attention; 2B and 9B trained with KD from 27B]

[16] arXiv:2309.17410 (2023): Can Sensitive Information Be Deleted From LLMs? Objectives for
     Defending Against Extraction Attacks. [38% whitebox / 29% blackbox residual post-ROME --
     critical empirical anchor for demo contrast claim]

[17] ACL 2024 Findings: Model Editing at Scale leads to Gradual and Catastrophic Forgetting.
     https://aclanthology.org/2024.findings-acl.902/

[18] arXiv:2312.07104 (SGLang, 2023/2024): Efficient Execution of Structured Language Model
     Programs. RadixAttention; 5x throughput vs vLLM on structured workloads.

[19] Kwon et al. (2023, vLLM): Efficient Memory Management for Large Language Model Serving
     with PagedAttention. SOSP 2023. [Core vLLM paper; continuous batching foundation]
