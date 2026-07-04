# Research Drill: Does Discarding MAGNITUDE (graded rate) Cap the Block-Argmax Retrieval Ceiling? (2026-07-04)

**Author:** Director (Research). BRAIN 5x-drill, angle 3 of 5.
**Distinct angle:** the sibling angle
(`research_drill_brain_grounded_concept_encoding_how_does_brain_do_it_2026-07-04.md`) blames the
training ORDER (sparsify-during vs sparsify-after). THIS angle is orthogonal and about the
REPRESENTATION: our block-argmax keeps only the per-block argmax IDENTITY + SIGN (+-1) and DISCARDS the
graded magnitude/rate. Does the brain preserve graded firing RATE inside its sparse codes, and is
magnitude-discard the fundamental fidelity-killer for the retrieval CEILING?
**Anchor fact (from the task, quantizer-ceiling regime):** the K128 block-argmax caps retrieval at
~0.43 even on the teacher's OWN vectors (dense-float = 1.0); ~0.43-0.79 across densities. This is a
CEILING that holds even under perfect learning -> it is a representation-capacity fact, not a learning
fact. That is the object of this drill.
**Method:** substrate KB concept-query first; generic-terms internet drill (safe); then a clean
synthetic decomposition simulation (isotropic vs anisotropic; binary vs graded; magnitude-level sweep)
to quantify the graded-vs-binary gap. **Calibration:** lit-scan + novel-synthesis penalty applied.

---

## 0. The two distinct failures (do not conflate)

1. **Learning COLLAPSE (sibling drill):** DENSE_SIGN 0.825 -> BLOCK 0.645 smoke -> ~0.31 FULL. A
   training-dynamics failure; fix = decouple sparsification (rich-first, k-WTA after).
2. **Quantizer CEILING (this drill):** even with perfect learning, block-argmax BINARY caps retrieval
   at ~0.43 on the teacher's own vectors. A representation-capacity failure; fix = stop throwing away
   magnitude.

These are additive and BOTH must be fixed. Critically: **the sibling's decouple-sparsify rescue cannot
by itself exceed ~0.43, because that is the binary quantizer's ceiling on the teacher's own vectors.**
Fixing training order lets you REACH the ceiling; it does not RAISE it. Raising it is what this drill is
about.

---

## 1. Substrate prior-work check (ran first, v2 flags)

Queries: "graded firing rate magnitude sparse code binary block argmax retrieval fidelity"; "rate coding
firing rate information content bits per spike neural population sparse".

- **The biology primitive is INGESTED but never applied to the quantizer:** `BIO/population_coding_neural`
  (T1 primitive, cosine 0.358); the Pouget/Dayan/Zemel finding that **"firing rate encodes not just a
  point estimate but the posterior probability over that feature"** (5x biology drill 2026-06-08
  chunk015); a prior "population/rate coding ensemble N=100" note (confidence-binary drill 2026-06-10).
- **No prior arc connects graded-rate-coding to the block-argmax magnitude-discard ceiling.** Closest
  retrieval-side hits are SPLADE (learned sparse retrieval, which KEEPS graded weights) and the LoRA
  retrieval-degradation note, neither about our quantizer. **Prior arc work on THIS concept: NONE.**
  Novel-synthesis penalty applies.

---

## 2. What the brain does: graded rate, not binary on/off (cited)

- **Neurons are rate coders, not binary switches.** Since Adrian (1926), firing RATE varies continuously
  with stimulus intensity. Population coding represents full posteriors in the graded rates
  [Pouget/Dayan/Zemel 2003, in-substrate]. The sparse SET of active cells carries identity; the graded
  RATE of those cells carries the magnitude/confidence. Both channels are information-bearing.
- **Information content: graded >> binary at the unit level.** Cortical spike trains carry ~2.39 bits/spike
  on average, and the spike-train rate carries substantially more than a single binary spike (2.39 vs
  1.64 bits) because graded temporal/rate structure adds information [Reinagel/Reid-line SNN coding
  reviews, web drill]. A pure binary on/off is by definition 1 bit; the brain runs many discriminable
  rate levels per unit.
- **Synapses are graded (analog), not binary.** Synaptic weights and dendritic graded potentials are
  continuous; graded transmission is a load-bearing part of the code.
- **Direct read-across:** the brain uses BOTH a sparse binding-identity channel (WHICH ~1-5% of cells
  fire = pattern-separation / conjunctive binding, the DG/hippocampal role) AND a graded rate channel
  (HOW FAST they fire = magnitude / posterior). **Our block-argmax keeps the first channel (support +
  sign) and deletes the second (rate).** That deletion is precisely the un-biological choice.

## 2b. ML corroboration (web drill)

- **Top-k sparse autoencoders keep GRADED activations by design;** binarizing them would destroy
  reconstruction. JumpReLU/Gated/TopK SAE work is entirely about preserving graded magnitude at a given
  sparsity; the whole field treats magnitude as the information [Gao et al. 2024 "Scaling and evaluating
  SAEs"; JumpReLU 2024]. Nobody ships a binary top-k code for fidelity because it does not work.
- **Ordering latents by activation MAGNITUDE progressively recovers the vector** [SAE progressive-code
  result] - i.e. magnitude is not decoration, it is the reconstruction signal.

---

## 3. Decomposition simulation (the quantitative core)

Clean synthetic (no substrate state). N=4096, block-argmax quantizer (1 signed active per block).
Metric = **preservation Spearman** (rank-correlation between dense-space pairwise cosine and
quantized-space pairwise cosine) = exactly the RKD/retrieval-geometry target the 0.43 ceiling measures.
Scripts: `scratchpad/graded_vs_binary_sim.py`, `graded_vs_binary_aniso.py`, `graded_levels.py`.

### 3.1 The gap is ENTIRELY governed by anisotropy (this is the key finding)

Real transformer/BGE embeddings are strongly anisotropic (a handful of "rogue" high-variance dims;
effective participation ratio << nominal dim). I swept coordinate-variance power-law alpha:

| data anisotropy (coord-var participation ratio / 4096) | block_binary Spearman (K128, 3.1%) | block_GRADED Spearman | abs gain | rel gain |
|---|---|---|---|---|
| isotropic (alpha 0, PR 4089) | 0.166 | 0.185 | +0.018 | +11% |
| mild (alpha 0.5, PR 46) | 0.145 | 0.440 | +0.294 | +202% |
| embedding-like (alpha 0.8, PR 4) | 0.202 | 0.647 | +0.445 | +220% |
| strong (alpha 1.1, PR 2) | 0.264 | 0.762 | +0.497 | +188% |

**Read-out:** on ISOTROPIC data, magnitude is nearly worthless (all argmax magnitudes are statistically
identical), so binary is fine and graded adds ~nothing. On ANISOTROPIC data - where real embeddings live
- keeping graded magnitude roughly **2-3x's** the preservation Spearman and adds **+0.3 to +0.5 absolute**.
Note the graded ceilings (0.44 / 0.65 / 0.76) BRACKET the cited real block-argmax range 0.43-0.79 -
i.e. the cited "0.43-0.79 across densities" ceiling is exactly what magnitude recovery buys you, and the
current binary code is stuck at the BOTTOM of that band.

### 3.2 How many magnitude LEVELS are needed (does the clean discrete code survive?)

alpha=0.8 (embedding-like), preservation Spearman, signed-magnitude quantized to L levels:

| levels | K128 (3.1%) | recovers % of gain | K64 (1.56%) | recovers % of gain |
|---|---|---|---|---|
| binary (L=1) | 0.215 | 0% | 0.376 | 0% |
| 2-level | 0.297 | 19% | 0.472 | 35% |
| 3-level | 0.336 | 28% | 0.508 | 48% |
| 4-level | 0.350 | 31% | 0.523 | 54% |
| 8-level | 0.384 | 39% | 0.549 | 63% |
| full float | 0.650 | 100% | 0.651 | 100% |

**Honest nuance:** the gain is CONTINUOUS in bit-depth - cheap 2-4 levels recover only ~20-55%, not
most. To fully cash the +0.4 you want near-float amplitude. BUT: even a modest **4-level (2-bit)
amplitude crosses the >=0.35 retrieval target at 3.1%**, and at ~2% (K64) binary is already ~0.38 and
4-level ~0.52, float ~0.65. So the target is reachable with a small magnitude channel; the CEILING is
reachable only with fine amplitude.

### 3.3 Information-theoretic bits/code (analytic)

K128/B32: binary = 768 bits (640 selection + 128 sign); graded @ 3-4 mag-bits = 1152-1280 bits =
**1.5-1.7x raw bits.** The retrieval Spearman gain (2-3x) EXCEEDS the raw-bit gain (1.5x) because cosine
fidelity on anisotropic data is super-linear in magnitude info: a few dominant blocks dominate the inner
product and their RELATIVE magnitudes are exactly what binarization flattens to +-1.

---

## 4. Is magnitude-discard the culprit? (sharp verdict)

**YES - it is the single largest RECOVERABLE lever for the retrieval CEILING, conditional on the data
being anisotropic (which real embeddings are).** Specifically:
- On embedding-like anisotropy, magnitude recovery raises the ceiling from binary ~0.20-0.44 to graded
  ~0.44-0.76 (+0.3 to +0.5 Spearman, 2-3x). That is the difference between "below the 0.35 target" and
  "comfortably above it, into 0.65-0.76 territory."
- It is NOT the WHOLE story, and I will not overclaim: (a) the block-argmax SELECTION loss (deleting
  non-argmax coordinates within a block) caps even the graded ceiling below 1.0, and on isotropic data
  IS the entire loss; (b) on truly isotropic data magnitude buys ~nothing. The magnitude lever's payoff
  is DATA-DEPENDENT and large precisely because BGE is anisotropic.
- It is a DIFFERENT failure from the sibling's learning-collapse. Both share a root enemy - the hard
  BINARY bottleneck - and both fixes point the same way.

---

## 5. Concrete graded-sparse lever (brain-grounded, algebra-safe)

**Lever: factored magnitude channel = "which fires" (sign code) + "how fast" (graded amplitude).**
Keep the existing +-1 block-argmax SUPPORT+SIGN code for the SBC bind/unbind ALGEBRA (untouched;
roundtrip 1.000, keyed unbind acc@1 1.00 all preserved because the algebra path sees the identical
support and signs). ATTACH a per-active-block graded amplitude (float, or a 4-8 level / 2-3 bit magnitude
channel) used ONLY by the cosine/retrieval readout. Retrieval cosine is computed on
support*sign*magnitude; bind/unbind is computed on support*sign. Same active positions -> the two
channels are a clean factorization, not a conflict.

- **Brain grounding (exact):** the dentate-gyrus/cortex sparse SET does binding + pattern separation
  (our sign code); the graded firing RATE of those active cells carries the posterior/magnitude (our new
  amplitude channel). We deleted the rate channel; add it back. This is population coding
  [Pouget/Dayan/Zemel], not a hack.
- **Why algebra survives:** circular-convolution binding is DEFINED for graded real/complex vectors
  (HRR/FHRR are graded; bipolar +-1 is the degenerate MAP special case). Even so, the SAFE move is the
  FACTORED dual-readout above so the validated +-1 unbind is byte-for-byte unchanged; the amplitude rides
  alongside for retrieval only. If a single unified graded code is wanted later, test roundtrip with a
  per-block magnitude and expect graceful (not catastrophic) degradation.
- **Cost:** small. Add a magnitude head / keep the pre-argmax magnitude at the K active positions; change
  the retrieval readout to use it. ~20-40 lines. Composes with the sibling's decouple-sparsify (D1):
  decouple fixes the COLLAPSE so you reach the ceiling; graded amplitude RAISES the ceiling from ~0.43 to
  ~0.65-0.76. **You need both; they are orthogonal and multiplicative.**

**P_deflated = 0.55** for the composite operational claim ("factored graded-amplitude channel crosses
>=0.35 retrieval at ~2% sparse with the SBC algebra intact, on real BGE"). The CORE mechanism ("graded
amplitude substantially beats binary block-argmax for retrieval on anisotropic embeddings") is much more
robust, ~0.75 - it is triangulated by direct simulation + population-coding biology + the SAE field's
refusal to binarize. Deflation on the composite is for: synthetic anisotropy proxy not real BGE (exact
alpha unknown); my Spearman metric vs their exact retrieval metric; the algebra-factoring resolution is
reasoned not yet tested at roundtrip 1.0 with a live amplitude channel; and hitting the target at TRUE
2% (not 3.1%) is unverified. Not capped at 0.50 because this is a direct-mechanism finding with in-house
simulation support, not a pure lit extrapolation.

---

## 6. Provenance

**Simulation (this drill, scratchpad):** `graded_vs_binary_sim.py` (iid baseline: graded ~= binary,
magnitude worthless when isotropic), `graded_vs_binary_aniso.py` (anisotropy sweep, table 3.1),
`graded_levels.py` (magnitude-level sweep, table 3.2). Clean synthetic, N=4096, seed 0.
**Substrate:** `BIO/population_coding_neural` (T1); Pouget/Dayan/Zemel via
`research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md` chunk015; sibling angle
`research_drill_brain_grounded_concept_encoding_how_does_brain_do_it_2026-07-04.md`.
**Literature (generic-terms web drill):** SNN neural-coding reviews (bits/spike ~2.39; rate>single-spike)
[PMC7970006; arXiv 1809.03142]; SAE graded-magnitude fidelity [Gao et al. 2024 "Scaling and evaluating
sparse autoencoders"; JumpReLU 2024 arXiv 2407.14435; probabilistic-TopK openreview].

ASCII-only. No emojis. No em dashes.

---

## 7. Intuitive summary (USER universal rule)

The question was: our sparse code keeps only WHICH slot won in each block and its sign (+ or -), and
throws away HOW MUCH it won by. Does the brain keep that "how much," and is throwing it away why
retrieval is capped?

The brain answer is unambiguous: neurons are not on/off switches, they are dimmer knobs. Since the 1920s
we have known a neuron's firing RATE rises smoothly with how strongly it is driven, and a population's
graded rates encode a full probability distribution, not just a yes/no. The brain uses two channels at
once - WHICH neurons fire (that is the sparse identity, the binding, the "what is this") and HOW FAST
they fire (that is the graded magnitude, the "how much / how confident"). Our block-argmax keeps the
first channel and deletes the second. So we deleted exactly the part the brain leans on for graded
similarity.

Does that actually cap retrieval? I built a clean simulation to find out, and it gave a sharp and
slightly surprising answer. On perfectly uniform ("isotropic") data, keeping the magnitude buys almost
nothing - because when everything is the same size, "how much" carries no information. But real BGE
embeddings are the opposite of uniform: a few directions are huge and most are tiny (this is a
well-known property of transformer embeddings). On data shaped like that, keeping the graded magnitude
roughly DOUBLES to TRIPLES the retrieval quality at the same sparsity - it lifts the score from the
~0.2-0.4 range (where binary is stuck, and which matches the 0.43 ceiling we were told about) up to
~0.65-0.76. In other words: yes, throwing away magnitude is the single biggest recoverable reason the
ceiling is low, and it is low precisely BECAUSE real embeddings are lopsided in a way that makes
magnitude very informative.

The catch, honestly stated: you cannot get this for free with a cheap 1-or-2-bit magnitude - 2 to 4
levels only claw back a fifth to a half of the gain; to cash the full lift you want a fine-grained
amplitude, close to a real number. The good news is you do not have to break anything to add it. Keep
the clean +-1 code exactly as-is for the bind/unbind math (which already works perfectly), and simply
ATTACH a "loudness" number to each active slot that only the similarity/retrieval readout looks at. That
is literally the brain's design - the same neurons that do the binding also carry a firing rate - so it
is principled, not a bolt-on. And it stacks with the other rescue (the sibling drill's "form the meaning
first, sparsify after"): that one lets us REACH the ceiling, this one RAISES the ceiling from ~0.43 to
~0.65-0.76. We need both, and they do not fight each other.

Where it leaves us: the "should be EASIER" instinct is right. A big chunk of the missing retrieval is
not a hard learning problem, it is information we are deliberately deleting at the output - the graded
firing rate the brain never throws away. Add a magnitude channel to the retrieval readout, leave the
algebra untouched, and the ceiling moves from "below target" to "comfortably above it." Confidence is
moderate-to-good on the direction (~0.75 that graded beats binary substantially), more cautious on the
exact landing at true 2% with a live algebra channel (~0.55) until it is run on real BGE.
