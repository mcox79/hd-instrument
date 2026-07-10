# Pillar-2 Design: A Native (Not Oracle-Free) Geometric Router — 2026-07-10

**Author:** Director synthesis of 4 brain-grounding lit-scans (SR/routing, grid-cell geometry, hippocampal attractor/pattern-separation, honest-scaffolding). Consolidated in main thread after the sub-drill deadlocked on child re-reports; all 4 child findings captured below with citations.

**HEADLINE:** The scour's "oracle router prop" wall should NOT be attacked by chasing a purely oracle-free router — the brain doesn't have one. The biologically-honest target is a **native-LOCAL geometric router that DRIFTS, corrected by periodic EXTERNAL-REFERENT recalibration + top-down goal bias.** Two named architectures already build exactly this on algebra we run (FHRR): **Vector-HaSH** (grid-code address scaffold + attractor cleanup on the address, avoids the memory cliff) and **Spatial Semantic Pointers** (grid-like codes from fractional FHRR binding). The candidate anti-load-collapse mechanism — SR as a low-rank spectral basis (grid cells = its eigenvectors) — is a PLAUSIBLE BUT UNTESTED cross-literature inference; proving it survives load in OUR substrate where the dense router collapsed is itself the novel contribution.

---

## 1. THE REFRAME (honest-scaffolding scan) — the brain router is NOT oracle-free

The scour framed the wall as "our traversal rides on a partition-ORACLE; every oracle-free router failed." The biology says an oracle-free router is the wrong goal, because the brain's own navigation is externally anchored:

- **Grid cells DRIFT without external correction.** Grid-cell error accumulates with time/distance since last landmark/boundary contact; border-cell interactions reset it (Hardcastle, Ganguli & Giocomo, *Neuron* 2015). Continuous-attractor theory: aperiodic grid attractors rotate/drift over minutes absent external input — "a spatial input is required to oppose drift" (Burak & Fiete, *PLoS Comp Biol* 2009).
- **Wehner's reversal (the key intuition):** path-integration is the SCAFFOLD, landmarks are what STABILIZE long-run accuracy — "Path Integration Provides a Scaffold for Landmark Learning" (Wehner, *Curr Biol* 2010). Self-generated routing is primary; the external referent corrects its drift.
- **PFC supplies top-down GOAL BIAS to hippocampus** — actively-maintained goal representations that "guide the flow of activity along neural pathways" the target circuit would not establish itself (Miller & Cohen, *Annu Rev Neurosci* 2001); mechanistically instantiated by long-range PFC→hippocampus GABAergic gating that disinhibits specific microcircuits (bioRxiv 2021.03.01.433441).
- **Thalamus gates routing via DESCENDING cortical feedback** (Crick searchlight 1984; Sherman & Guillery gatekeeper) — the channel-selector is informed by top-down, not bottom-up, signals.

**Design consequence:** the router target is **native-local routing + periodic external-referent recalibration + top-down goal bias**, not oracle-elimination. The external anchor IS the exogenous referent — **this ties Pillar-2 directly into GROUNDING** (the 2nd real wall). The "oracle" we should remove is the *god's-eye partition-label oracle*; the "oracle" we should KEEP (and make honest) is a *biologically-faithful external recalibration signal* drawn from the ingested data itself.

## 2. THE BLUEPRINT — two architectures on FHRR algebra we already run

- **Vector-HaSH** (Chandra, Sharma, Chaudhuri & Fiete, *Nature* 2024): separates an **ADDRESS SPACE** (grid-cell-driven CA3 scaffold of attractor states, fixed random EC→CA3 projections + learned return weights) from **CONTENT** (bound onto scaffold locations). Attractor dynamics do error-correction on the **address/routing state itself** = exactly address-cleanup / routing-resolution, and it **avoids the classic memory cliff**, showing graceful capacity/detail tradeoff instead. → This is the router blueprint: a grid-code address scaffold with attractor cleanup on the address.
- **Our regenerative hard-snap cleanup is already CG** and is the RIGHT KIND of cleanup: CA3 completion is a discrete hard-snap to an attractor basin (Amit 1989; Rolls 2007), not a linear filter — matches our certified `digital_repeater_regenerative_hard_snap_cleanup`. We may already own the router's cleanup stage.
- **Spatial Semantic Pointers** (Komer/Dumont/Eliasmith, CogSci 2019 / IJCNN): grid-like codes from **fractional FHRR binding** (phase exponentiation by a continuous amount). FHRR unbind = elementwise conjugate multiply = **phase subtraction = the grid-cell goal-vector operation** (Bush, Barry, Manson & Burgess, *Neuron* 2015; formal equivalence). → The geometric code is a CONTINUOUS regime of our OWN algebra, not a foreign import. Discrete binding (integer exponent) = memorize; fractional binding (continuous exponent) = interpolate/navigate. This is the candidate concrete knob from the memorizing regime (alpha->1) to the generalizing regime (alpha->0).
- **Tolman-Eichenbaum Machine** (Whittington et al., *Cell* 2020): factorized structural/transition codes that generalize across relational GRAPHS — the bridge from grid-code-for-space to grid-code-for-arbitrary-relational-structure. The reference architecture for applying this to our knowledge graph.

## 3. THE ANTI-COLLAPSE MECHANISM — and its honest status

Our routers die because router SNR ~ sqrt(N/M) collapses under memory load M. Candidate fix from the SR scan:

- **SR is a LOW-RANK spectral basis, not a dense associative lookup.** M = (I - gamma*T)^-1; grid cells encode the **leading eigenvectors** of M (Stachenfeld, Botvinick & Gershman, *Nat Neurosci* 2017). A low-rank/compressed spectral router does not store N patterns densely, so it may not hit the 0.14N Hopfield capacity cliff.
- **Sparse coding independently raises the ceiling:** sparse associative capacity ~ N^2/(k^2 log N) >> dense 0.14N (Amit & Fusi; Tsodyks & Feigel'man). DG expansion + sparsity decorrelates before storage.
- **HONEST FLAG (load-bearing):** "low-rank/reused SR AVOIDS Hopfield capacity collapse" is a **cross-literature INFERENCE — the SR track and the Hopfield-capacity track run parallel and non-intersecting; no paper tests it.** So this is NOT an established result to lean on; it is a hypothesis our experiment must MEASURE (does a low-rank spectral / sparse router survive the exact load where our dense router collapsed?). If it does, that is a genuine novel contribution, not a port.
- **SR's honest limits to carry:** SF/GPI transfer requires reward ~ LINEAR in features (nonlinear breaks clean reuse; Barreto 2018); SR is INSENSITIVE to reward change (good) but HIGHLY SENSITIVE to TRANSITION/STRUCTURE change — new edges force relearning the SR matrix (Russek 2017; Momennejad 2017); SF-from-raw is prone to representation collapse.

## 4. THE UNIFYING BET — one geometric code for both walls?

Pillar-1 (inductive inference) and Pillar-2 (routing) may be the SAME build: in the brain the grid/SR geometric code does BOTH — vector-subtraction inference AND native navigation — and all three architectures (Vector-HaSH, SSP, TEM) use one grid-code scaffold for both address and content generalization.

**HONEST CAVEAT (grid-cell scan, do not overclaim):** the literal "king-man+woman=queen" ANALOGICAL inference is NOT demonstrated in neural data — that result is from NLP (word2vec) + VSA theory; the neural evidence supports grid code for NAVIGATION and for CONCEPTUAL-SPACE FORMAT (hexagonal modulation in conceptual/social 2D spaces; Constantinescu 2016, Bao 2019, Park 2021), NOT for discrete relational/analogical inference over a knowledge graph. So "one code cracks both walls" is a well-motivated HYPOTHESIS with architectural precedent, not a fact. Whether our substrate's geometric code performs discrete relational inference (vs only continuous conceptual navigation) is exactly what Pillar-1's retest + build must show.

## 5. FALSIFIABLE-PREDICTION SKELETON (fair controls; exp_dev designs the cell)

**Claim to test:** a native geometric router (low-rank SR / SSP address scaffold + hard-snap attractor cleanup + external-referent recalibration) routes multi-hop lookups WITHOUT the partition-label oracle, and SURVIVES the memory load where the dense/learned router collapsed.

Mandatory controls (apply the fairness + degree-control + info-ceiling lessons):
- **The sqrt(N/M) load-collapse baseline** the router must beat: reproduce our dense/learned router's collapse curve vs M, then show the geometric router's curve stays above it at the same M (the whole point — if it collapses at the same M, low-rank bought nothing).
- **Degree/popularity baseline** (same as the inference test): a router that picks the highest-degree/most-frequent next-partition with NO geometry — the geometric router must beat it (else it's the popularity shortcut, not routing).
- **Oracle-leak check (critical):** prove the router is NOT peeking at partition labels — ablate/shuffle the partition-label channel and confirm the geometric router still routes (if routing dies when labels are shuffled, it was leaking the oracle). This is the analog of `codes_necessary`.
- **Recalibration-necessity:** show the drift-correction (external-referent recalibration) is load-bearing — without it the router drifts and degrades over hops (matches grid-drift biology); with it, accuracy holds. This is what distinguishes "native+recalibrated" from "secretly still oracle'd."
- **Real ingested knowledge, not synthetic chains** (scour constraint): must be tested on the ingested KG, since our synthetic-chain CG results don't transfer.
- **HARD-PASS:** geometric router beats both the dense-collapse curve AND the degree baseline at high M, survives label-shuffle (oracle-free), recalibration is necessary, on real KG. **HARD-FAIL:** collapses at the same M as dense (low-rank bought nothing) OR dies under label-shuffle (was leaking) OR ties the degree baseline (popularity, not routing).

## 6. NEXT STEP

Gate on the Pillar-1 retest first (shared geometric-code question). If the additive/geometric code survives degree control for INFERENCE, the same code family is the natural router substrate → hand this skeleton to exp_dev for a native-router cell. If it fails for inference, Pillar-2 may still be independently buildable (routing needs geometric ADDRESSING, not necessarily inductive inference) — but expect the low-rank-avoids-collapse claim to be the real crux either way. Grounding (external-referent recalibration) is now a SHARED dependency of both pillars, not a separate front.
