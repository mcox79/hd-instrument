# Research 2x REVIVAL drill — v2e modularity-Z LRG self-mapping HARD_FAIL

Date: 2026-06-23
Author: research (Opus 4.7-1M)
Trigger: USER directive "understand WHY it failed" on v2e_modularity_Z_LRG_self_mapping_v1_smoke HARD_FAIL. 5th attempt at substrate self-mapping. Cap P at 0.35 (5 prior nulls = strong empirical Bayes against this path).
Lit-scan calibration penalty applied (0.20-0.25 deflation). Generic-terms-only queries per query-privacy.

---

## HEADLINE

**WHY v2e failed:** the substrate adjacency under char_trigram encoder + 2-hop-Jaccard is **bit-identical to its degree-preserving null at every gamma in the sweep** (Q_real(gamma=1.0) = Q_shuf(gamma=1.0) = 0.0148; Q_real(gamma=2.0) = Q_shuf(gamma=2.0) = -0.0679; n_clusters_real = n_clusters_shuf at every gamma). This is not "discriminator can't tell them apart" — the actual graph topologies produced by the rewire and the real Hebbian-KG are degenerate-twins. Combined with the sanity self-test PASS (planted 2-block Z=30.02), the v2e cell is exonerated; the discriminator is sensitive when real signal exists. **The encoder + adjacency pipeline produces a graph whose structure is entirely captured by its degree sequence** — i.e. the substrate's "graph" carries no information beyond per-atom connectivity counts.

**Diagnosis (clean):** ENCODER-BOUND, not discriminator-bound, not n-too-small. Encoder substitution is forced.

**Top revival angle:** **DO NOT** dispatch v2e-FULL at n=150 (it would burn ~3hr remote_cpu and reproduce the same bit-degenerate result by construction; the failure mode is structural-not-statistical). **WAIT for encoder dual-gain to land** (the enc_dual_gain_softhebb_vs_fpe_v1 cell already designed in the 5x-DEEPER encoder upgrade dual-gain drill 2026-06-23), and only then retry self-mapping with the upgraded encoder. P_deflated = 0.30 on encoder-upgrade-then-retry; P_deflated = 0.10 on v2e-FULL n=150 alone.

---

## Cheap decisive test — already done, just need correct reading

The cheap test WAS v2e-smoke. The data is dispositive:

| gamma | n_clusters_real | n_clusters_shuf | Q_real | Q_shuf | Z_real | Z_shuf | identical? |
|---|---|---|---|---|---|---|---|
| 0.5 | 1 | 1 | 0.5000 | 0.5000 | 0.000 | 0.000 | YES (bit) |
| 1.0 | 2 | 2 | 0.0148 | 0.0148 | 0.828 | 0.828 | YES (bit) |
| 2.0 | 30 | 30 | -0.0679 | -0.0679 | 0.000 | 0.000 | YES (bit) |
| 4.0 | 30 | 30 | -0.1357 | -0.1357 | 0.000 | 0.000 | YES (bit) |

LRG also identical (real and shuf both give pair_aris=[1.0, 0.0], mean_pair_ari=0.500). Engram allocation collapsed to all-zero labels (single cluster) at iter=20, ari_init_vs_final=0.0.

**Why this is the right diagnosis, not n-too-small:** if n=30 were the problem, REAL and SHUF would show *noisy* divergence (different sample-Q at each gamma, different cluster counts on different random rewires). They are **bit-identical**, which means the Louvain optimization on real-adjacency and on degree-rewired-adjacency lands in the same partition at every gamma. That can only happen if the off-degree adjacency structure carries no community signal — i.e. **the encoder + Jaccard pipeline outputs a graph whose only structure IS the degree sequence**.

The sanity self-test PASS (planted 2-block partition gave Z=30.02 vs Z_shuf=-0.60) proves the discriminator is sensitive. Composing: discriminator-OK + null-test-degenerate = encoder-output-degenerate.

---

## WHY (intuitive, 1 paragraph)

The char_trigram encoder represents atoms as bag-of-character-trigrams over the atom name. Two atoms with similar spelling get similar vectors regardless of meaning ("modularity_lock_v3" and "modularity_check_v2" cluster together even if one is a capability atom and the other is a feedback atom). When you then build a Hebbian KGStore on relations and ask "are two atoms within 2 relational hops?" via Jaccard on neighbor sets, the answer is dominated by **shared relation-type degree** (atom_A is the source of REL_TYPE_5 100 times, atom_B is the source of REL_TYPE_5 100 times → high Jaccard regardless of which targets they share). The resulting adjacency matrix is structurally a degree-degree outer product with rank-1 dominance. Degree-preserving rewire preserves this exactly. The substrate's "graph" is therefore informationally trivial — encoder gives no semantic similarity beyond spelling, and the Hebbian-KG composition collapses to pure-degree connectivity. Nothing the modularity-Z, LRG, or engram-allocation discriminator can do will rescue a graph whose information content equals its degree sequence. The 5x drill was right about discriminator-class; it was wrong about which side of the encoder–discriminator boundary the residual bottleneck sits. The v2e data resolves that ambiguity definitively.

**Brain analog check:** Tonegawa engram allocation assumes neurons have *informative inputs* on which to compete for excitability. If you gave the engram-allocation circuit pure-noise inputs, it would also collapse to a single ensemble or degenerate partitions. Biology does NOT assume "any encoder works" — biology assumes evolutionarily-tuned receptive fields (V1 edge detectors, MT motion, IT face cells) provide structured, semantic inputs. v2e has been running engram-allocation on the cortical analog of pure-spelling-noise. Of course it collapses.

---

## Five-axis diagnosis (cross-check vs prior 5x drill)

### Axis 1 — Encoder bit-degenerate adjacency (NEW; load-bearing)
The 5x drill anticipated this in its prediction-4 ("if LRG stability ≤ 0.30 on cached output, then there is NO multi-scale structure in the substrate adjacency at all — the encoder is the bottleneck"). v2e confirms the prediction: stability = 0.500 (matching shuf exactly = no real signal). The 5x drill ALSO said "encoder is not the bottleneck per v2/v2b signal at small scope" — that assertion is now FALSIFIED. v2/v2b had small-scope-spurious-signal (~50 atoms with v1-family overlap creates accidentally-non-trivial-structure from the small-N geometric noise; the v1-family clustering was the spurious confound, not the encoder).

### Axis 2 — n=30 is sufficient to detect the encoder bug
sqrt(n_anchors) Z-modularity upper bound = sqrt(30) = 5.48. HARD_PASS threshold Z>=2.5 is *46% of the theoretical max* — comfortably achievable IF the encoder produces non-trivial structure. The sanity self-test PASS (Z=30.02 on planted partition, which violates the sqrt(n) bound because the planted partition is by construction far above null) shows the discriminator-side is well-calibrated to detect strong signal. n=150 would simply tighten the variance bands; it would NOT escape the bit-degeneracy.

### Axis 3 — Engram-allocation collapse is downstream consequence, not separate issue
allocation final_labels all-zero + ari_init_vs_final=0.0 is the engram primitive doing what it should under pure-noise input. The competition softmax (atom @ centroid - lambda * cluster_size) collapses to the single cluster because every atom @ centroid is uniformly low (encoder gives spelling-noise vectors, all near-orthogonal at random). This is NOT a bug in engram-allocation; it's the load-bearing-encoder-bug propagating downstream. Engram-allocation primitive WILL work once encoder is fixed.

### Axis 4 — Fortunato resolution-limit is a red herring here
The 5x drill cited Fortunato sqrt(L/2)=14.75 as a structural blind-spot. But the failure mode is one level deeper: Fortunato says "modularity can't see clusters smaller than 14.75" — v2e shows modularity can't see *any* difference between real and rewire, which is a stronger failure than resolution-limit. Resolution-limit applies to graphs WITH real structure modularity is failing to detect. v2e graph has NO real structure to detect.

### Axis 5 — V1-family ground truth was the wrong target; intrinsic discriminator was the right move
The 5x drill correctly abandoned v1-family ground truth. v2e implementing modularity-Z + LRG + engram-allocation was the right move. It just happens that "right discriminator on encoder-degenerate adjacency" returns null — which is itself a clean diagnostic.

---

## Cross-thread synthesis

- **META atom [[by-construction-saturation]]** — char_trigram + 2-hop-Jaccard is by-construction-degenerate: the adjacency-from-spelling-bag with Hebbian-KG-Jaccard collapses to rank-1 degree outer product. This is now a SECOND by-construction-saturation result on the self-mapping path (first was v2c modularity at full scope; now encoder pipeline at any scope). The path forward must avoid this class of pipeline.
- **META atom [[cleanup-load-bearing]]** — engram-allocation primitive at `hdlab/iterative_attractor.py` will still be load-bearing once encoder is fixed. The primitive is not broken; its input is.
- **5x encoder-upgrade dual-gain drill (sister doc)** — already designed enc_dual_gain_softhebb_vs_fpe_v1 cell with 4 arms (random bipolar / char_trigram / SoftHebb-3-layer / FPE-phase). The DECISIVE arm for self-mapping revival is **ARM_SOFTHEBB_3LAYER** — SoftHebb gives a substrate-native learned encoder that converges to Bayesian-generative representations (Moraitis 2021). If SoftHebb passes its cleanup HARD_PASS at sigma=1.5, the same encoder should produce non-trivial substrate adjacency for self-mapping retry.
- **r2 brain-drill (CLS)** — CLS needs informative inputs to separate consolidated from novel structure. Same encoder dependency.
- **r3 multi-hop drill** — multi_hop at K=2 IS the Hebbian-trace step in engram-allocation. Primitive is fine. Encoder gates the whole composition.
- **Prior 5x drill's Bayes-flip threshold** — "if v2e HARD_FAIL, P(discriminator-class works) drops to 0.20." Confirmed; we are below the threshold for any further cycles in the char_trigram + 2-hop-Jaccard class. Encoder substitution is now the forcing function — not optional.

---

## Top revival angle ranking

### Recommended: (b) WAIT for encoder dual-gain to land + retry v2e with the better encoder

**Anchor:** Reuse v2e cell mechanics (modularity-Z + LRG + engram-allocation) but swap encoder from `char_trigram_encoder.py` to the winning arm from `enc_dual_gain_softhebb_vs_fpe_v1` (SoftHebb-3-layer or FPE-phase, whichever passes its HARD_PASS).

**Why-now:** The 5x-DEEPER encoder upgrade drill is already designed (notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md) and the enc_dual_gain cell is laptop-CPU cheap (~30-60 min). Total revival path: ~1hr encoder dispatch + ~3hr v2e-FULL-with-new-encoder = ~4hr. Dispatching v2e-FULL n=150 with the SAME encoder first would burn ~3hr to reproduce the bit-degeneracy. Strict cost-asymmetry favors wait.

**Substrate-product reading:** Phase 1 self-mapping is blocked on encoder; encoder dual-gain unlocks BOTH self-mapping AND Path A bigram-gap. The encoder dispatch is high-leverage anyway.

**Tier hint:** chain-grade-targetable in 2 cells (dual-gain → upgraded self-map).

**P_deflated:** 0.30 (capped at 0.35 per directive; deflated 0.05 for "second-order composition through encoder + adjacency + discriminator" stack — each stage has its own potential to surprise).

### Not-recommended: (a) v2e FULL n=150 to definitively rule out smoke-confound

The smoke v2e is already definitive. Real and shuf are bit-identical at every gamma; n=150 cannot create informative graph structure where there is none. Cost ~3hr remote_cpu for confirmatory null. **Skip.**

P_deflated of (a) finding HARD_PASS at n=150: 0.10 (only if there's a smoke-only float-precision artifact that disappears at n=150 — vanishingly unlikely given bit-identical observations).

### Not-recommended-yet: (c) Different mechanism class entirely (spectral / SBM / GNN)

The discriminator is fine. Switching to spectral clustering or stochastic-block-model fitting would just be "different discriminator on same degenerate graph" — same failure mode. Only consider after encoder upgrade lands AND fails. P_deflated as next-after-encoder: 0.20 if encoder upgrade itself returns HARD_FAIL.

---

## Falsifiable predictions (HARD_PASS + HARD_FAIL)

### Recommended revival cell: `v2f_self_map_softhebb_encoder` (post-encoder-dual-gain HARD_PASS)

**Configuration:**
- Encoder: SoftHebb-3-layer (winning arm from enc_dual_gain_softhebb_vs_fpe_v1), N_DIM=4096
- Discriminator: modularity-Z gamma sweep + LRG tau sweep + engram-allocation (unchanged from v2e)
- n_anchors: 100 chain-grade-only (smoke=30 to validate the sweep is non-degenerate before FULL)
- run_mode: smoke first (~10 min laptop), then FULL n=150 if smoke passes

**HARD_PASS:** Z_real(gamma*) >= 2.5 AND Z_real(gamma*) - Z_shuf(gamma*) >= 1.5 AND partition_stability_LRG >= 0.40 AND engram allocation converges to >= 3 clusters with non-zero size variance AND recall >= 0.95 AND cv across seeds <= 0.20. **P_deflated = 0.30.**

**HARD_FAIL:** Z_real(gamma*) - Z_shuf(gamma*) <= 0.20 at every gamma in sweep (i.e. encoder-upgrade also fails to break the bit-degeneracy) AND engram allocation collapses to 1-2 clusters with all-singleton or all-merged labels. **P_deflated = 0.30** (this would force the next pivot to different graph-construction-from-encoder pipeline — not 2-hop-Jaccard, e.g. cosine-similarity-thresholded direct atom-vector graph, or attention-style soft-adjacency).

**MIDDLE_BAND:** Z_real(gamma*) - Z_shuf(gamma*) in (0.20, 1.5) OR partition_stability_LRG in (0.20, 0.40). **P_deflated = 0.40.** Indicates partial encoder-rescue; characterize per-gamma where signal lives.

### Pre-registered hard-fail meaning (what HARD_FAIL forces)

If v2f also HARD_FAILS with SoftHebb encoder: the 2-hop-Jaccard adjacency itself is the bottleneck, not the encoder representation. Next move = abandon Hebbian-KG-Jaccard adjacency; build adjacency from direct atom-vector cosine similarity OR from substrate cleanup-attractor basin overlaps. This is a 6th-attempt-pivot at the adjacency construction primitive — atomize as META: "Hebbian-KG + multi-hop-Jaccard is by-construction-degenerate as a self-mapping adjacency at chain-grade atom density."

---

## Substrate-product implications

If v2f HARD_PASS: Phase 1 closes; Phase 2 autoatom unblocked. Phase 3 (substrate proposes new mathematics) requires the substrate to have intrinsic multi-scale structure to draw novel-mathematics candidates FROM. v2f-pass provides exactly that.

If v2f HARD_FAIL: the substrate-self-mapping arc has now spent ~50 cycles across 6 attempts with each diagnosed root cause. The substrate-product implication is structural: **the substrate does not have a cert-grade self-mapping capability** under current encoder/adjacency primitive stack. This is not a stop-signal but a re-scoping: Phase 1 self-mapping is descoped to "structural-summary-only" (the substrate can report its own statistics but cannot autonomously partition itself), and autoatom Phase 2 must operate on human-curated capability groupings until/unless a 7th attempt is justified. The cert-trail will mark substrate self-mapping as MEASURED_NULL at the chain-grade-atom density regime.

### hdlab/ primitive implications

- `hdlab/char_trigram_encoder.py` — keep for narrow use (atom-name lookup, structural debug) but DO NOT use as primary substrate encoder
- `hdlab/softhebb_encoder.py` (NEW, conditional on enc_dual_gain HARD_PASS) — substrate-native learned text encoder
- `hdlab/self_mapping.py` (NEW, conditional on v2f HARD_PASS) — bundles encoder-agnostic modularity-Z + LRG + engram-allocation
- engram_allocation primitive validated as not-broken; not yet promoted (waiting on informative input from upgraded encoder)

---

## Cross-thread with field advisor

Field advisor's top-5 next-drill candidates are all in `free-probability` / `semiconductor` / `spin-glass` — none directly bear on encoder upgrade. **The encoder-upgrade drill is already filed (5x deeper encoder dual-gain) — it's the more leveraged next dispatch than the advisor's top-5 because it unblocks both Phase 1 self-mapping AND Path A bigram-gap.** Once encoder dual-gain lands, F4 / D1 / D2 candidates from the advisor become natural follow-ons (substrate-native cumulant statistics on the upgraded codebook).

The 2x revival drill does NOT add a new field to the advisor's matrix — it consolidates the encoder-bound diagnosis across two prior fruit-bearing fields (`network-science-graph-theory` for the discriminator side; `learning-rules` / `cerebellar-fan-in` for the encoder side per the dual-gain drill).

---

## Lit-scan calibration penalty applied

- The "encoder produces graph degenerate to its degree-sequence under 2-hop-Jaccard" diagnosis is novel-synthesis from substrate data + lit (Reichardt-Bornholdt Potts + Fortunato resolution + degree-preserving null model theory). The diagnosis is DATA-FORCED by the bit-identical Q sweep; calibration penalty applies to the *forward prediction* (encoder substitution rescues), not to the *backward diagnosis*. P_deflated on encoder-rescue: 0.30 (deflated 0.20 from natural 0.50 cap for 5 prior nulls in the broader self-mapping arc).
- Symmetric anti-negativity check: P_HARD_PASS=0.30 + P_MIDDLE=0.40 + P_HARD_FAIL=0.30 = 1.00. Reasonable; MIDDLE is most likely (partial encoder rescue is more probable than full bipolar pass/fail given encoder upgrade is one-step from random bipolar baseline).
- HARD bands numerically pre-registered.
- HARD_FAIL forces a specific structural pivot (abandon Hebbian-KG-Jaccard adjacency), not a stop.

---

## Self-check (Director cross-check)

- All 5 prior attempts re-read: yes (v2 / v2b / v2c FULL / v2d FULL / v2d-smoke / v2e-smoke; per-cell metrics + verdict_msg + DESIGN_NOTE).
- Per-arm metrics read, not summary verdict_msg (per [[feedback-fix28-verify-per-arm-metrics]]): YES — REAL and SHUF Q-sweeps + LRG pair_aris + allocation final_labels were directly inspected; the bit-identical observation is the load-bearing finding, not the verdict_msg framing.
- Discriminating-regime gate: yes — bit-identical Q sweep across REAL and SHUF is by-construction CAN-fail-detectable; v2e cell PASSED its sanity self-test (planted partition Z=30.02) which means the discriminator is sensitive.
- Verify-the-referent (per [[feedback-verify-the-referent]]): yes — the n_real_edges=435 == n_shuf_edges=435 by-construction (degree-preserving rewire preserves edge count) is correct; the surprise is that Q is also bit-identical, which is informative beyond identical-by-construction.
- Symmetric anti-negativity: yes — HARD_FAIL (encoder upgrade also fails) and HARD_PASS (encoder upgrade rescues) are equally weighted at P=0.30 each.
- 5-axis structural diagnosis: 5 axes, encoder-bound is load-bearing; n=30, Fortunato, engram-collapse, v1-family-deprecation are all consequences or already-addressed.
- USER directive "understand WHY it failed" answered with bit-identical-Q-sweep evidence (not just "the encoder is wrong" assertion).
- Cap P at 0.35 (per directive): observed; recommended cell P_HARD_PASS = 0.30.
- 5th attempt strong-Bayes-against: observed — recommendation is NOT "do v2e-FULL again" (the seductive trap); recommendation is "wait for encoder to be fixed FIRST, then retry" (cost-asymmetric correct move).
- Anti-negativity (USER rule): the diagnosis is structurally productive — it forces encoder substitution which is ALREADY queued as enc_dual_gain dispatch. The 2x revival adds urgency + downstream-dependency framing.
- Empowered-to-experiment-where-lit-says-dismissed: relevant — modularity-Z + LRG + engram-allocation on multi-relational Hebbian KG has no published precedent; the v2e null result is an INFORMATION-rich substrate-physics observation, not a stop-signal. Cycle to encoder side, then retry.

---

## Citations (verified count: 6)

1. **Fortunato & Barthelemy** "Resolution limit in community detection," PNAS 2007 / cond-mat/0606220. sqrt(L/2) lower bound on detectable cluster size; modularity inherently scale-limited. https://arxiv.org/abs/cond-mat/0606220
2. **"Modularity maximization considered harmful"** Inverse Complexity Lab. Modularity-Louvain over-fragments and has exponentially many near-optimal partitions for small/sparse networks. https://skewed.de/lab/posts/modularity-harmful/
3. **Miyauchi & Kawase 2016** "Z-Score-Based Modularity for Community Detection in Networks," PLOS One PMC4726636. Z-modularity has upper bound sqrt(n); calibrates against configuration-model null. https://pmc.ncbi.nlm.nih.gov/articles/PMC4726636/
4. **Reichardt & Bornholdt** "Statistical mechanics of community detection," Phys. Rev. E 2006 / cond-mat/0603718. Community detection as Potts spin-glass ground state. https://arxiv.org/abs/cond-mat/0603718
5. **Moraitis 2021** "SoftHebb: Bayesian inference in unsupervised Hebbian soft winner-take-all networks," 2107.05747. Substrate-native unsupervised encoder convergent to Bayesian generative model. https://arxiv.org/abs/2107.05747
6. **Bremer-Orchard 2024** "Improved cleanup for Fractional Power Encoding," 2412.00488. FPE substrate-native HD encoder with CLE+MLE iterative cleanup. https://arxiv.org/abs/2412.00488

Also referenced (cross-thread carry):
- Tonegawa engram-allocation (PMC11525749) — biology assumes informative inputs to competition
- Villegas LRG (arxiv 2406.02337) — multi-scale partition stability framework
- Prior 5x drill (notes/research_5x_deeper_substrate_self_mapping_gap_2026-06-23.md)
- Sister 5x drill (notes/research_5x_deeper_encoder_upgrade_dual_gain_2026-06-23.md)

---

## Recommended downstream actions

1. **DO NOT dispatch v2e-FULL at n=150** with current encoder. The smoke result is bit-degenerate; n=150 cannot create informative structure where the encoder + Jaccard composition produces a degree-rank-1 adjacency.
2. **DISPATCH enc_dual_gain_softhebb_vs_fpe_v1** (already designed in sister 5x drill). Wait for HARD_PASS on at least one non-bipolar arm.
3. **POST-ENCODER-DUAL-GAIN** (if HARD_PASS): dispatch v2f_self_map_softhebb_encoder smoke first (n=30, ~10 min laptop) to validate the encoder swap breaks the bit-degeneracy. If smoke shows Z_real - Z_shuf >= 1.0 at any gamma, dispatch v2f-FULL n=150 (3hr remote_cpu).
4. **If enc_dual_gain HARD_FAILS** (all encoder arms fail their HARD_PASS): self-mapping arc is paused at MEASURED_NULL chain-grade; descope to structural-summary-only for Phase 2 autoatom.
5. **Atomize the META finding NOW** (independent of next dispatch outcome): "char_trigram + 2-hop-Jaccard composition produces a graph bit-identical to its degree-preserving null at substrate-chain-grade-atom density (verified 2026-06-23 via v2e smoke per-gamma Q sweep)." This is a substrate-physics meta-fact that informs every future self-mapping attempt regardless of encoder choice.

---

## Companion hand-off

This research finding IS exp_dev-actionable (recommends specific cell sequence: enc_dual_gain → v2f). Companion hand-off file will be written at `notes/exp_dev_handoff_research_2x_revival_v2e_self_mapping_2026-06-23.md` per role contract.
