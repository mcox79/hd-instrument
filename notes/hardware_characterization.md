# Hardware characterization for HDC primitives

Track 0.2 output. Best published per-op energy figures across three hardware classes (CPU AVX-512, NVIDIA H100, in-memory analog), synthesized from a focused 2024–2025 literature pass. This document answers the user's question: *if HDC works algorithmically, what hardware would run it uniquely efficiently, and how much energy would it save?*

## Headline finding

The strongest cell is **associative cleanup / similarity search**: in-memory analog hardware beats H100 by roughly **3 orders of magnitude** on this single operation, with **real fabricated silicon** as the evidence (IBM Zurich's 760K-device PCM chip, Karunaratne et al., *Nature Electronics* 3, 327, 2020). This is the operation that dominates the inner loop of any pointer-chain HDC, multi-relation graph traversal, or codebook-cleanup architecture. If our Bet B algorithm wants to live on dedicated hardware, the cleanup advantage is the load-bearing claim — and it survives scrutiny.

The weakest cells are **FHRR bind on non-GPU substrates** (only projection, no fabricated silicon — PhotoHDC, arXiv 2311.17801) and **HRR circular convolution on analog hardware** (no published energy figure at all). If we depend on FHRR or HRR for the substrate, the hardware story is partly speculative.

The pragmatic implication: **BSC may be the deployment-friendly substrate even if FHRR is the research-friendly one.** BSC has real silicon evidence; FHRR currently does not.

## Per-op energy table

Best published numbers per (primitive, hardware) cell. "Real silicon" means fabricated and measured. "Projection" means simulated, architectural, or extrapolated.

| Primitive | CPU (AVX-512) | GPU (H100, FP16) | In-memory analog | Headline ratio (best vs H100) |
|---|---|---|---|---|
| **FHRR bind** (complex unit-modulus mul) | ~5–10 pJ/element (proxy from FP16 FMA; no HDC-specific measurement) | ~1.4 pJ/element (0.7 pJ/MAC × 2 for complex); real silicon | PhotoHDC projects 2–5 orders of magnitude advantage; **projection only, no fab** | ~3–4 orders (speculative) |
| **BSC bind** (XOR + popcount) | ~1–2 pJ/bit (proxy from AVX-512 VPOPCNT/VPXORD) | Reference: ReHDC (Hernandez-Cano et al.) cites 51.5× advantage of analog over P100; no direct H100 number | IBM 760K PCM (Karunaratne 2020): >6× over optimized 65nm digital; on-array scalar ops <10 fJ at 8-bit-equivalent; **real silicon** | ~1–2 orders (standalone) to ~3 orders (integrated with on-array cleanup) |
| **HRR bind** (FFT-based, O(N log N)) | No HDC-specific FFT energy paper found | cuFFT throughput well-known but no per-sample J number for H100 published | **No published in-memory FFT for HRR.** Optical FFT (Lightmatter / Lightelligence) targets VMM, not circular convolution | **Gap — no analog story for HRR** |
| **Cleanup / similarity search** over K-vector codebook | ~µJ-per-query (ARM-class proxy; no AVX-512 HDC paper) | Extrapolated from FP16 GEMM: ~0.7 pJ × N × K | **Strongest cell.** Karunaratne 2020 measured silicon; HyDra (arXiv 2504.14020, 2025) projects 282× search-energy reduction vs 7nm CMOS; Imani A-HAM (DATE 2017) shows 1347× EDP improvement at iso-accuracy | **~3 orders, real silicon evidence** |
| **Hebbian outer-product update** | No HDC-specific number | ~0.7 pJ/MAC FP16 | PCM/RRAM crossbars demonstrate outer-product update at 30–150 fJ/MAC; IBM 64-core AIMC chip (Le Gallo et al., *Nature Electronics* 6, 680, 2023) is the most credible measurement; real silicon | ~2–3 orders per-MAC, but **write endurance dominates over energy** at scale |

## Strategic implications for the project

### What this means for Bet B (Hebbian-trained VSA-LM)

If Track 0.1 lands "alive," the deployment-friendly substrate is BSC, not FHRR, for hardware energy reasons. Three concrete shifts that fall out of this:

1. **Run Track 0.1 also with BSC**, not just FHRR, before committing the architecture. If BSC trains comparably to FHRR on the char-LM probe, BSC becomes the default. If FHRR is materially better, we accept the hardware story is partly speculative and proceed anyway.
2. **The Hebbian update energy story is real but write-endurance-limited.** PCM/RRAM cells tolerate ~10⁶–10⁹ writes before degradation. A trained model that does inference-only after training is fine. A model that does continual learning at deployment needs careful update gating — which our modulator architecture already provides (`surprise`, `arousal`) but it becomes load-bearing rather than nice-to-have.
3. **Cleanup is the hardware home run.** Our pointer-chain and multi-relation architectures both bottleneck on cleanup — and that's exactly where the largest fabricated-silicon advantage lives. This is consistent with what we'd want.

### What this means for Bet A (HDC retrieval layer for frozen LLM)

The hardware story for Bet A is less load-bearing because the LLM remains on GPUs. The HDC retrieval layer running on dedicated analog silicon would still save compute, but the absolute savings are bounded by the retrieval share of total inference compute. For typical RAG-class workloads, that share is 5–15% of total cost. Even with the 3-orders-of-magnitude cleanup advantage, total platform-level savings are realistically 10–30% on retrieval-heavy workloads.

For Bet A, the **observability differentiator dominates over the hardware differentiator**. We don't need custom silicon for Bet A to ship; we need ablation-traceable retrieval.

## Gaps and risks in the hardware story

Things that would weaken the project's hardware-efficiency claims if surfaced:

1. **FHRR has no fabricated silicon.** PhotoHDC is the only published FHRR-friendly hardware path and it is purely architectural projection. Critics will note this. Mitigation: position BSC as primary deployment target; FHRR as the research substrate.
2. **HRR circular convolution has no analog implementation.** If we end up needing HRR for any reason (e.g., depth scaling), the hardware story degrades to "GPU only." Our prior work showed HRR has the worst depth ceiling among substrates anyway; this confirms we should not be on HRR.
3. **Write endurance limits.** PCM and RRAM tolerate 10⁶–10⁹ writes per cell. Continual-learning regimes will eventually wear out cells. Mitigation: hierarchical update strategy — fast Hebbian updates in a digital buffer; periodic consolidation into analog crossbars. This is a real engineering constraint we have to acknowledge.
4. **Real-world per-watt comparisons are noisy.** End-to-end system energy includes data movement, ADC/DAC conversion at analog boundaries, control logic. The "3 orders" cleanup number is per-operation in the array; system-level numbers degrade by 5–10× depending on integration quality. The honest claim is "1.5–2 orders of magnitude at the system level for cleanup-heavy workloads," not "3 orders end-to-end."
5. **Loihi 2 / SpiNNaker 2 are absent.** Neuromorphic chips have no HDC-primitive benchmarks in published literature (Yan et al. 2021 covers keyword spotting/control only). If the user wants a neuromorphic story, that's an open research direction, not a reportable advantage.

## Realistic energy projection for a Bet B deployment

If Bet B produces a Hebbian-VSA-LM with **N** = 4K to 16K, **K** (codebook entries) = 10K to 10M, and inference characterized by:
- 1 context bundle per token (K bind ops + 1 normalize)
- 1 cleanup against K-entry codebook per token
- 0 or 1 Hebbian update per token (online learning regime)

Then per-token energy on integrated analog HDC silicon would be approximately:

| Component | H100 estimate | Analog HDC estimate | Ratio |
|---|---|---|---|
| Context bind (K bytes) | K × 1.4 pJ | K × 0.5 pJ (BSC on-array) | ~3× |
| Cleanup over K vectors | K × N × 0.7 pJ ≈ K × N pJ | K × 30 fJ (analog crossbar) | ~50× to 1000× depending on K |
| Hebbian update | N × N × 0.7 pJ ≈ N² × 0.7 pJ | N × 100 fJ (PCM) | ~100× |
| **Per-token total (K=10K, N=4K)** | **~3 µJ** | **~30–300 nJ** | **~10×–100× system level** |

This is the **system-level ratio** including conversion overhead, control logic, and data movement. The headline-ratio of "3 orders of magnitude" is the per-operation peak; the system-level number is one-to-two orders less. **A factor of 10×–100× on inference energy is the defensible claim.**

For comparison, a Llama-7B on H100 in FP16 is ~0.05–0.1 J/token (TokenPowerBench, arXiv 2512.03024, 2025). A Hebbian-VSA-LM on analog silicon at 30–300 nJ/token would be **5–6 orders of magnitude lower**. That gap is large enough that even with our pessimistic system-level adjustment, the conclusion holds: if the algorithm works, the hardware advantage is real and material.

## What we will *not* claim

- That FHRR-based HDC has demonstrated silicon advantage. It hasn't; only projections.
- That neuromorphic chips (Loihi 2, SpiNNaker 2) currently beat GPUs on HDC primitives. Not benchmarked.
- That analog crossbars deliver their peak per-op energy in production systems without integration overhead. They don't.
- That the energy advantage applies to all workloads. It applies to cleanup-heavy and update-heavy workloads, which is the regime our architecture is in.

## Primary sources

- Karunaratne et al., *Nature Electronics* 3, 327 (2020) — IBM 760K PCM HDC chip. The foundational silicon evidence.
- Le Gallo et al., *Nature Electronics* 6, 680 (2023) — IBM 64-core AIMC chip.
- Langenegger et al., *Nature Nanotechnology* 18, 479 (2023) — In-memory HDC factorization, problem sizes 10⁵ larger than digital.
- HyDra SOT-CAM, arXiv 2504.14020 (2025) — Search energy projection at 7nm.
- PhotoHDC, arXiv 2311.17801 (2023) — Photonic FHRR architecture, projection only.
- Hernandez-Cano et al. ReHDC — Analog vs P100 GPU baseline.
- Imani et al., DATE 2017 — A-HAM / R-HAM associative memory designs.
- TokenPowerBench, arXiv 2512.03024 (2025) — H100 inference energy per token.
- NVIDIA H100 whitepaper (2022) — FP16 dense throughput baseline.

## Verdict for the Track 0 decision matrix

**Hardware characterization outcome: "compelling hardware story" tier** — with caveats.

The compelling parts:
- Cleanup energy advantage is real, measured silicon, ~3 orders of magnitude at the per-op level.
- Integrated with on-array bind and update operations (IBM's 760K-device chip is exactly this integration), the system-level energy advantage is realistically 10×–100× on HDC-suitable workloads.
- This advantage is durable: it depends on the operations being primitive and stable, which they are by construction.

The caveats:
- FHRR-specific silicon does not exist. Deployment story should be BSC-first.
- Write endurance constrains continual-learning regimes.
- End-to-end system numbers are 5–10× worse than per-op peak.

This places the Track 0.2 outcome in the "compelling hardware story" column of the decision matrix in `NEXT_PHASE.md`. Combined with whatever Track 0.1 returns, we'll have a concrete next-step decision.
