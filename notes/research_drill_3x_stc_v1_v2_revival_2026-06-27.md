# Research Drill 3x — STC tag-and-capture v1 + v2 HARD_FAIL revival

Date: 2026-06-27 ~17:50 PDT
Author: Research (Director)
Trigger: USER directive 2026-06-27 ~17:35 PDT after Wave 2H cell-author surfaced design flaw

## TL;DR

Both v1 and v2 fail because the discriminator is broken at the baseline level: Hebbian-additive W does not catastrophically forget. v2's `baseline_A_after=0.999` is not a bug in the cell — it is the substrate doing what HD vectors are designed to do (orthogonal additive coexistence). To revive STC we must either (a) force the baseline into a regime where additive storage genuinely degrades A, OR (b) change the discriminator from "preservation under overwrite" to one of STC's actual mechanistic strengths: late-LTP maintenance window, capacity@retrieval, or selective-recall. Both lit-scans confirm: classical Hopfield forgets only past critical capacity ("blackout catastrophe"); STC's biological discriminator is time-window survival of tagged vs untagged, not pattern interference.

---

## ANGLE A — PURE MATH: why substrate W does not catastrophically forget

Wave 2H is mathematically correct. Substrate Hebbian update is `W += x_i x_i.T` with no subtraction. In HD vectors of dimension N_DIM=8192, two random patterns have expected inner product ~N(0, 1/sqrt(N_DIM)) ≈ 0.011 — quasi-orthogonal. So `W·x_A` after storing both A and B reconstructs A with crosstalk on the order of M/N_DIM where M is item count. Forgetting only kicks in past the critical-capacity transition (Hopfield: M ≈ 0.138·N_DIM ≈ 1130 items; dense-associative variants higher). At M=2 the baseline correctly stays at 0.999. Lit-scan confirms: "blackout catastrophe" is a discontinuous transition above critical capacity — there is no smooth forgetting curve to demonstrate STC's preservation lift against.

**Three math-correct fixes to MAKE baseline forget:**

1. **Capacity-exceeded regime (M >> N_DIM/8)** — store 2000–8000 items into N_DIM=8192. Baseline collapses to noise; STC-tagged items should survive. This is the canonical Hopfield-forgetting regime.
2. **Bounded W with normalization** — after each write, `W /= max(1, ||W||_F / W_CAP)`. New writes now displace old structure proportionally. STC's preservation = tag exempts from displacement.
3. **Active decay between writes** — `W *= (1 - lambda_decay)` with `lambda_decay ≈ 0.01–0.05` per write step. Untagged items decay multiplicatively; tagged items skip the decay step. This is the most STC-faithful and the cleanest discriminator.

Fix #3 is the brain-correct version (see Angle B) and creates the cleanest falsifiable discriminator: A retention curve over t writes of B-distractors, with vs without tag on A.

---

## ANGLE B — BIOLOGY: how the brain achieves catastrophic forgetting

Brain does not catastrophically forget — it gradually forgets via several biologically distinct mechanisms, and STC is specifically about which subset of recent experiences survives the forgetting wave. The discriminator we have been testing (overwrite-interference) is not STC's actual job.

**Three brain-correct ways to instantiate a substrate forgetting baseline:**

1. **Time-decay of untagged synapses (E-LTP → null)** — early-LTP without PRP capture decays in ~1–3 hours. Substrate analog: every write decays all entries `W *= (1 - lambda)`; tagged entries are protected during a PRP-pulse window. This matches Frey-Morris STC exactly. Discriminator: after T decay steps, tagged items retain weight, untagged items decay below readout threshold.
2. **Slow synaptic homeostasis (renormalization)** — total synaptic weight is bounded; new strong potentiations force weakening of others. Substrate analog: total `||W||_F` bounded, new writes proportionally weaken old ones unless tagged.
3. **Neurogenesis / pattern-separator turnover** — sparse codes get rewritten by new patterns occupying same neurons. Substrate analog: bounded V_C with eviction policy; tagged codes pinned, untagged codes evicted under LRU.

Mechanism #1 (time-decay of untagged) is the most direct match to actual STC and the cleanest substrate translation. It is what the original Wave 2H cell intended but did not implement — v2 added STC tagging but did NOT add the untagged-decay step the tag is supposed to protect against. **That is the missing baseline mechanism.**

---

## ANGLE C — TEST DESIGN: maybe wrong discriminator entirely for STC

Wave 2H META-finding is right: STC is a CAPACITY mechanism (which subset of recent learning consolidates into long-term storage), not a CLASSIFICATION mechanism (does B overwrite A). Three alternative discriminators that play to STC's actual strengths:

1. **Time-window survival discriminator** — store N tagged + N untagged items, apply T steps of decay, measure retrieval@k for tagged vs untagged. Pass band: tagged retrieval > 0.8 AND untagged retrieval < 0.3 at t=T. This is the canonical biological STC assay translated.
2. **Capacity@retrieval discriminator** — store M items, fraction p tagged, measure retrieval accuracy as M grows from N_DIM/4 to 2·N_DIM. Pass band: tagged-item retrieval stays above 0.7 at M=2·N_DIM where untagged collapses below 0.3. Tests whether STC effectively raises capacity for the tagged subset.
3. **Selective-recall discriminator** — query for "any item tagged with context C" and measure precision/recall over the tagged subset. Tests whether tags provide an indexing/retrieval channel beyond raw similarity. Bonus: this is the version closest to actual Director-KB usage (tag the post-compaction docs, recall them selectively).

Discriminators #1 and #2 are mechanism-clean. Discriminator #3 is product-aligned (matches Director-KB use case).

---

## SYNTHESIS — TOP-2 REVIVAL CELLS

### Cell 1 (PRIMARY): `stc_tag_decay_window_v3`

Combines Angle A fix #3 + Angle B mechanism #1 + Angle C discriminator #1. The minimal-change revival that fixes the missing baseline mechanism.

- **Forgetting baseline:** `W *= (1 - lambda_decay)` every write step. `lambda_decay = 0.02`.
- **STC mechanism:** Tagged entries skip the decay step during a PRP-pulse window of T_PRP=50 write-steps after tagging. Outside the window, decay applies normally.
- **Setup:** Store M=200 items at N_DIM=8192. Tag 100 of them at write-time. Apply T=200 subsequent write-steps of unrelated B-items.
- **Readout:** Retrieval@1 for tagged vs untagged subset after T=200.
- **Falsifiable bands:** PASS: tagged@1 ≥ 0.80 AND untagged@1 ≤ 0.30 AND tag_fraction in [0.40, 0.55]. HARD_FAIL: tagged@1 < 0.50 OR untagged@1 > 0.50 (baseline does not forget) OR tag_fraction outside [0.30, 0.65].
- **Smoke gate:** N_DIM=512, M=50, T=50, lambda_decay=0.05. Must show untagged_smoke@1 < 0.40 BEFORE full dispatch (Fix #28: discriminator must survive scale).
- **Discriminator-survives-scale check:** at smoke N=512 with lambda_decay scaled to 0.05, untagged decay should reach ~e^(-2.5)·noise ≈ 0.08; tagged in-window ≈ 1.0. Confirms separation present at smoke scale before full N.
- **Why this revives:** It is the v2 design WITH the missing untagged-decay step. Without that step, tag has nothing to protect against. With it, the discriminator becomes the classical Frey-Morris assay.

### Cell 2 (BACKUP): `stc_capacity_lift_v3`

Combines Angle A fix #1 + Angle C discriminator #2. The capacity-mechanism reframing per Wave 2H META.

- **Forgetting baseline:** Capacity-exceeded regime, no explicit decay. Store M items at N_DIM=8192, sweep M ∈ {1000, 2000, 4000, 8000, 16000}.
- **STC mechanism:** At each write, tag with probability p=0.25. Tagged items go to a protected "scaffold" sub-matrix W_tagged of bounded size. Untagged items go to W_main which fills toward capacity collapse.
- **Readout:** Retrieval@1 for tagged subset vs untagged subset at each M.
- **Falsifiable bands:** PASS: at M=2·N_DIM, tagged@1 ≥ 0.70 AND untagged@1 ≤ 0.30. HARD_FAIL: bands not separated by 0.30 absolute at any M ≥ N_DIM. SATURATION: both arms at 1.0 at M=8000 (baseline didn't fill; scale M up further).
- **Smoke gate:** N_DIM=512, M ∈ {200, 1000}, p=0.25. Must show untagged@1 collapse from M=200 (≥0.8) to M=1000 (≤0.3) BEFORE full dispatch.
- **Why this revives:** It abandons the overwrite-interference framing entirely and tests STC as a capacity-protection mechanism, which is what STC actually does biologically. Closer to the heteroassociation-scaffold approach in arxiv:2202.00159.

## Recommendation

Dispatch **Cell 1** first via hdi_orchestrator (smoke local at N_DIM=512, then full N_DIM=8192 on remote_cpu). Cell 1 is the minimal-change repair of v2 and the closest faithful translation of biological STC. If Cell 1 PASSes, Cell 2 becomes optional capacity-confirmation. If Cell 1 HARD_FAILs with `untagged@1 > 0.50` despite decay (meaning HD orthogonality survives even strong decay), pivot immediately to Cell 2 which tests the orthogonal hypothesis (STC as capacity-lift not interference-protection).

Both cells preserve STC's biological core (tag + protected-window + decay-of-untagged) while abandoning the bad baseline assumption (B overwrites A in additive Hebbian).

---

## Sources

- [Memory consolidation and improvement by synaptic tagging and capture in recurrent neural networks (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7977149/)
- [State Based Model of Long-Term Potentiation and Synaptic Tagging and Capture (PLOS Comp Bio)](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1000259)
- [Beyond boundaries: extended temporal flexibility in synaptic tagging and capture (Nature Comm Bio 2025)](https://www.nature.com/articles/s42003-025-07998-w)
- [Content Addressable Memory Without Catastrophic Forgetting by Heteroassociation with a Fixed Scaffold (arxiv 2202.00159)](https://arxiv.org/pdf/2202.00159)
- [Beyond catastrophic forgetting in associative networks with self-interactions (arxiv 2504.04560)](https://arxiv.org/pdf/2504.04560)
- [The Hopfield-type memory without catastrophic forgetting (arxiv 1205.0908)](https://arxiv.org/pdf/1205.0908)
- [Transient dynamics of associative memory models (arxiv 2506.05303)](https://arxiv.org/html/2506.05303v1)
- [Tag-Trigger-Consolidation: A Model of Early and Late LTP and Depression (PLOS Comp Bio)](https://journals.plos.org/ploscompbiol/article?id=10.1371%2Fjournal.pcbi.1000248)
