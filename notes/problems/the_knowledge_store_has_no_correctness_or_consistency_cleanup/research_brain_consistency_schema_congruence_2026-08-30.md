# Research drill: the brain's computation for detecting + down-weighting a fact that contradicts the coherent majority

**Date:** 2026-08-30 · **For:** `the_knowledge_store_has_no_correctness_or_consistency_cleanup` · **Role:** hdi_research (Director)
**Scope:** literature scan + adversarial synthesis. **Calibration:** lit-scan penalty applied (P deflated 0.15-0.25; novel-synthesis P capped 0.50). The literature strongly supports the mechanism *class*; whether within-store consistency actually separates injected errors on THIS sparse real is-a store is the empirical question the build must answer (a rigorous negative is a full PASS, per the bar).

---

## BOTTOM LINE FIRST (the recommended computation)

**Implement an ENERGY / ATTRACTOR consistency score, computed on the graph by SUPPORT-PROPAGATION (spreading activation / message passing), and GATED by a PRECISION/COVERAGE weight.** The three candidate mechanisms are not rivals; they are the same computation at three levels of description, and the brain's own detection organ (ACC) and cleanup organ (cortical consolidation) both implement the energy form.

- **Most brain-faithful single computation for "down-weight the fact that contradicts the coherent majority" = ENERGY-MINIMISATION (a).** It is the brain's *literal* model on BOTH halves of this organ: (i) DETECTION - Botvinick's ACC conflict signal IS a Hopfield energy computed over co-active mutually-incompatible units; (ii) CLEANUP - systems consolidation relaxes a memory toward the low-energy schema attractor and over-writes inconsistent detail (CLS; trace-transformation; Bartlett gist-pull). One computation covers both; the other two do not.
- **Support-propagation (b) is the tractable GRAPH IMPLEMENTATION of (a), not a competitor.** Belief propagation / spreading activation is precisely the message-passing algorithm that finds low-energy configurations on a network. On an is-a graph it is the natural, directly-codeable form: a fact's consistency = net support from type-consistent neighbours minus contradiction from type-incompatible co-attestations, iterated to a fixpoint so support flows transitively.
- **Precision-weighted prediction-error (c) is the CONFIDENCE GATE.** Its unique load-bearing contribution is precision weighting, which *derives* the coverage bound: a concept with few related units has low precision, so even a large mismatch yields a down-weighted error → no reliable flag. Use it as the gate, not the core score.

**Generalisation verdict: DOMAIN-GENERAL.** The conflict/congruence machinery (ACC conflict monitoring; vmPFC/mPFC schema congruence) is engaged across knowledge types with a content-agnostic computation. A SINGLE relation-agnostic mechanism operating over relation-specific neighbourhoods is the faithful choice. Type-specificity lives in the CONTENT of each schema and in per-relation precision, not in a separate algorithm.

**Coverage-bound verdict: FAITHFUL - it is a real property of the brain's mechanism, not a defect.** All three accounts collapse to "no signal" in the isolated-fact limit (no attractor forms / no neighbours to propagate / zero precision). van Kesteren's model *requires* an activated schema for congruence to be computed at all; Tse shows congruence effects scale with schema strength. A single fact with no related knowledge is neither congruent nor incongruent. Report coverage as a first-class number and treat "insufficient support" as a THIRD verdict, distinct from "consistent."

> **In-house prior work that already confirms the coverage bound empirically:** `hdlab/predictive_coding.py` exists, and `exp_ingest_gate_strong_foundation_novelty_v2` (HARD_PASS, 2026-07-16) measured that **novelty/prediction-error detection collapses to chance on a weak foundation.** That is exactly the density-gating the literature below predicts. The solver should read that cell + `predictive_coding.py` before building - the confidence gate (c) may already be partly wired. (Per CLAUDE.md "two archives": run `tools/experiment_index.py query "novelty"` / `"surprise"` / `"schema"` first.)

---

## Q1. The core circuit + computation for detecting an INCONSISTENT fact

There are three published computational accounts of the incongruence signal. They are complementary, and the target organ can use all three at different roles.

### (b-answer) Conflict = simultaneous activation of mutually incompatible representations — ACC, Botvinick 2001
**Computation (implementable, exact):** conflict is operationalised as **Hopfield energy** over the competing units:

```
Conflict(E) = - Σ_i Σ_{j≠i} a_i · a_j · w_ij
```

where `a` is unit activity, `w_ij` is the (negative, inhibitory) weight between competing units `i,j`. Conflict is HIGH exactly when two units that inhibit each other are co-active. The ACC reads this high-energy state and engages control to lower it. (Botvinick, Braver, Barch, Carter, Cohen 2001, *Psych Review*; Botvinick, Cohen, Carter 2004 update.)

**Map to the store:** the injected `amygdala→molecule` co-activates with the coherent `amygdala→structure`; `molecule` and `structure` are mutually-incompatible genus assignments (different coherent clusters → a large negative `w_ij`). Their co-activation is a high-energy state = the flag. This is the cleanest, most directly-codeable detection primitive we have, and it is graded (continuous energy), not discrete.

### (a-answer) Match/mismatch between the incoming item and an activated schema — mPFC (van Kesteren SLIMM) + hippocampus (Kumaran & Maguire)
**mPFC congruence (van Kesteren, Ruiter, Fernández, Henson 2012, *TINS*, "SLIMM"):** the mPFC's function is to detect congruency of new information with existing neocortical knowledge, termed **resonance** (explicitly analogised to Adaptive Resonance Theory). Congruent info resonates with an activated schema and mPFC then INHIBITS the MTL (fast consolidation into cortex); incongruent info fails to resonate, "elicits a prediction error," and engages the MTL to build a new representation. Computationally: congruence = overlap/resonance between the input pattern and the schema attractor; the signal is graded and non-linear in congruency.

**Hippocampal match-mismatch (Kumaran & Maguire 2006/2007, *J Neurosci* 27:8517; CA1 as comparator):** CA3 recurrent collaterals retrieve a PREDICTION from partial cues; CA1 receives both the CA3 prediction and the direct entorhinal (actual) input and computes their **comparison**; a mismatch is an associative-novelty error signal that gates encoding. Computation: `mismatch = f(retrieved_prediction, current_input)` at CA1, i.e. an associative comparator.

### (c-answer) Prediction error under a generative schema model — free-energy / PRO model
**Predictive coding / free energy (Friston 2009/2010):** a schema is a generative model; a fact inconsistent with it produces a large prediction error. Free energy = a **precision-weighted sum of squared prediction errors**; precision (inverse variance) dynamically weights each error's influence. Low precision → the error barely moves belief.

**ACC as prediction error, not conflict (Alexander & Brown 2011, *Nat Neurosci*, PRO model):** the mPFC/ACC learns to predict outcomes and signals **surprise** (predicted-but-absent = negative surprise; unexpected = positive surprise), a unified account that reproduces phenomena previously attributed to conflict monitoring. This is the normative reframing of Botvinick's energy signal.

**Which is it?** All three are real and measured. For THIS organ the faithful synthesis is: **(b) conflict-energy is the detection primitive, (a) match-to-activated-schema defines WHAT competes, (c) prediction-error/precision supplies the confidence gate.** They agree in the limit and each contributes a distinct piece.

---

## Q2. Is congruence GRADED or discrete, and over WHAT support set?

**GRADED.** mPFC congruence is a parametric response to congruency ratings and memory is a *non-linear function of congruency* (van Kesteren 2012). ACC conflict is a continuous energy. Schema-strength effects scale continuously with prior knowledge (Tse 2007/2011). Implement a continuous consistency score, not a binary.

**Support set = the concept's FULL ACTIVATED ASSOCIATIVE NETWORK — not a bare pairwise comparison, and not the superordinate type alone.** Ghosh & Gilboa (2014, *Neuropsychologia*, "What is a memory schema?") define a schema by four necessary features: (1) an **associative network structure**, (2) formed over **multiple episodes**, (3) **lacking unit detail**, (4) **adaptable**. van Kesteren's resonance is over the *activated schema representation*, i.e. the related knowledge the concepts bring online. So the faithful neighbourhood is the whole activated associative network.

**Operational neighbourhood for the is-a graph:**
```
schema(subject s) = { s's own attested genera }
                  ∪ { sibling terms sharing a genus with s }
                  ∪ { transitive is-a ancestors/descendants of s }
                  ∪ { terms in the same coherent genus cluster }
```
activated by spreading activation, each edge weighted by strength (attestation count / cluster coherence). **The superordinate TYPE is the single most diagnostic dimension for is-a specifically** (it is what `molecule` vs `structure` disagree on), but the faithful support set is the whole activated neighbourhood, of which the type is the strongest feature. Do NOT reduce to pairwise `(s, o)` comparison - that discards the network structure the brain's mechanism depends on.

---

## Q3. The DOWN-WEIGHTING / cleanup operation, and what each mechanism predicts

The brain's cleanup is **systems consolidation that over-writes toward the gist/schema and discards inconsistent detail:**
- **CLS (McClelland, McNaughton, O'Reilly 1995):** neocortex slowly extracts shared statistical structure via **interleaved** reactivation; a detail that overlaps little with the extracted structure is not reinforced and is forgotten while the gist is retained. Inconsistent detail = poorly-supported by overlapping structure → decays.
- **Trace Transformation Theory (Winocur & Moscovitch 2011, *JINS*):** a detailed trace transforms into a gist/schematic residue; representation shifts posterior-HPC (details) → anterior-HPC (gist) → mPFC (schema). Peripheral/inconsistent detail is lost; central structure survives.
- **Schema distortion (Bartlett 1932; Alba & Hasher 1983):** reconstructive recall is PULLED TOWARD the schema (selection, abstraction, integration); schema-inconsistent detail is systematically dropped or normalised.

**Which faithful mechanism, and what each predicts about caught-vs-missed:**

| mechanism | cleanup operation | wrong fact CAUGHT when… | wrong fact MISSED when… |
|---|---|---|---|
| **(a) attractor / Hopfield energy-min** | relax to the nearest low-energy coherent state; inconsistent detail sits at high energy and is over-written toward the schema basin | it raises the energy of a **deep** attractor (concept has a strong dominant coherent genus) AND the wrong genus is strongly incompatible (large negative `w_ij`) | the basin is **shallow** (few coherent neighbours) OR the wrong genus is CLOSE to the true one (small incompatibility - e.g. `region` vs `structure` barely conflict) |
| **(b) support-propagation / spreading activation** | fact strength = Σ support from consistent neighbours − Σ contradiction, iterated to fixpoint (belief propagation) | contradicted by **many high-support** neighbours; detection ∝ node degree × neighbour coherence | **isolated** (nothing propagates) OR the contradictor itself accreted spurious support (many co-attestations of the wrong fact) |
| **(c) precision-weighted prediction-error suppression** | error signal, scaled by schema precision, suppresses the low-precision/deviant trace | schema precision is **high** (well-sampled concept) AND mismatch is large | precision is **low** even if mismatch is large (uncertain schema down-weights its own error) → the coverage bound falls out directly |

**Recommendation:** use **(a) as the score** (it is what consolidation literally does), **(b) as the algorithm** that computes it on the graph, and **(c) as the gate** that decides whether the score is trustworthy enough to act on. The three predictions above are also the **discriminating ablations** to run: they disagree about isolated-but-locally-plausible facts vs well-connected-but-wrong facts, so measuring which errors are caught tells you which mechanism your store actually rewards.

---

## Q4. The DENSITY / COVERAGE constraint — is "you cannot judge an isolated fact" brain-faithful?

**YES — the coverage bound is a faithful property of the brain's mechanism, converging from all three accounts:**

- **van Kesteren SLIMM (2012):** congruence/resonance is only computed *when a schema is activated*. With no relevant prior knowledge, the item is not "incongruent" - it is routed to the MTL as **novel** and encoded as a fresh instance. No schema → no congruence signal, by construction.
- **Schema strength gates the effect (Tse et al. 2007 *Science*; Tse et al. 2011):** rapid schema-consistent consolidation requires a **pre-existing associative structure** built from multiple paired associates; the effect *scales with* schema strength. A thin/absent schema yields no congruence acceleration. Ghosh & Gilboa's feature (2) "formed over multiple episodes" is the same requirement: below a minimum number of related units there is no schema, hence nothing to be congruent or incongruent with.
- **Precision weighting (Friston; predictive coding):** precision = inverse variance of the schema's predictions. Few related units → low precision → `precision × prediction_error ≈ 0`, so even a large raw mismatch produces no reliable signal. This makes the coverage bound a *quantitative* prediction, not just a qualitative one.

**Convergence:** in the isolated-fact limit, (a) has no attractor, (b) has no neighbours, (c) has zero precision - all three say "no signal." So the store's "only facts embedded in enough related knowledge get a consistency score" is replicating a genuine gating property of the brain, NOT papering over a defect. **Design consequence:** make coverage a first-class output; emit "insufficient support to judge" as a THIRD verdict alongside "consistent" / "inconsistent"; report the fraction of the store that has a real signal as an honest bound. Given the store is ~half singletons, expect coverage to be the dominant limiting factor - and per the bar, a rigorous "the store is too sparse for a within-store signal on most facts" is a full PASS that re-points to the upstream density/coverage work (p1).

---

## Q5. GENERALISATION — domain-general or type-specific?

**DOMAIN-GENERAL computation over domain-specific content.** A single relation-agnostic mechanism is the faithful choice:
- **ACC conflict monitoring is content-agnostic** - the energy computation ranges over whatever units compete, regardless of what they represent (Botvinick 2001).
- **vmPFC/mPFC is a common schema-congruence hub across knowledge domains** (van Kesteren 2012; Gilboa & Marlatte 2017, *TICS*, "Neurobiology of Schemas and Schema-Mediated Memory"). Ghosh & Gilboa define "schema" as a domain-general structural concept, not a per-domain object.
- **Predictive coding is a general cortical algorithm** (Friston), the same message-passing at every level and domain.

**Caveat (deflated):** the CONTENT of each schema is domain/type-specific (different genus clusters have different internal structure), and per-relation *precision* may differ. So the faithful design is ONE relation-agnostic algorithm operating over relation-specific neighbourhoods, with optional per-relation/per-cluster precision tuning as a refinement - never a separate mechanism per relation.

---

## Recommended build (algorithm sketch, for the solver)

1. **Build the activated schema per concept** = its associative neighbourhood on the is-a graph (own genera + siblings-by-genus + transitive is-a chain + same-cluster terms), edge-weighted by attestation/coherence. (Ghosh & Gilboa; van Kesteren resonance.)
2. **Conflict-energy term (a/Botvinick):** for fact `f=(s, is-a, g)`, `E(f) = Σ_{i,j} a_i a_j w_ij` over the co-active genus-assignments in `s`'s neighbourhood, with `w_ij < 0` between incompatible genera. High `E` = the concept's neighbourhood strongly supports a *different, incompatible* genus.
3. **Support-propagation (b):** `consistency(f) = Σ_consistent-neighbours support − Σ_contradicting-neighbours contradiction`, iterated to a fixpoint (spreading activation / loopy belief propagation) so support flows transitively along is-a chains.
4. **Precision/coverage gate (c):** weight the verdict by schema strength (count + coherence of activated related units); below `k` related units emit **"insufficient support"** (the coverage bound), not "consistent."
5. **Down-weight/flag:** facts with high conflict-energy AND sufficient precision are flagged/down-weighted - the ACC→control analog and the consolidation "over-write toward gist, discard inconsistent detail" operation.
6. **Discriminating controls (the three predictions in Q3):** score isolated-but-plausible vs well-connected-but-wrong injected errors separately; the pattern of caught-vs-missed identifies which mechanism the real store rewards, and is itself the fidelity evidence.

**AUDIT UPDATE candidate (for `BRAIN_FOUNDATIONAL_AUDIT.md` §2b):** the consistency-cleanup computation is PINNED at the level of (energy-minimisation detection = Botvinick ACC; schema-congruence = van Kesteren mPFC; consolidation gist-pull = CLS/Winocur-Moscovitch). The coverage bound is PINNED (a real gating property, not OUR-INVENTION). OUR-INVENTION = the specific graph energy/support functional, edge weights, `w_ij` incompatibility metric, precision estimator, and thresholds. Note the in-house tie: `predictive_coding.py` + `exp_ingest_gate_strong_foundation_novelty_v2` HARD_PASS already demonstrated PE-detection collapses on a weak foundation - empirical confirmation of the coverage bound.

---

## Sources
- Botvinick, Braver, Barch, Carter, Cohen (2001) Conflict monitoring and cognitive control, *Psych Review*. Hopfield energy = conflict: https://princetonuniversity.github.io/PsyNeuLink/BotvinickConflictMonitoringModel.html · update: https://pubmed.ncbi.nlm.nih.gov/15556023/
- van Kesteren, Ruiter, Fernández, Henson (2012) How schema and novelty augment memory formation, *TINS* (SLIMM): https://pubmed.ncbi.nlm.nih.gov/22398180/ · PDF: https://www.mrc-cbu.cam.ac.uk/personal/rik.henson/personal/VanKesterenEtAl_12_TINS_schema_novelty_memory.pdf
- Kumaran & Maguire (2007) Match–mismatch processes underlie hippocampal responses to associative novelty, *J Neurosci* 27:8517: https://www.jneurosci.org/content/27/32/8517 · CA1 as match/mismatch detector: https://pmc.ncbi.nlm.nih.gov/articles/PMC3529001/
- Ghosh & Gilboa (2014) What is a memory schema? *Neuropsychologia*: https://pubmed.ncbi.nlm.nih.gov/24280650/
- Gilboa & Marlatte (2017) Neurobiology of Schemas and Schema-Mediated Memory, *TICS*: https://www.sciencedirect.com/science/article/abs/pii/S1364661317300864
- Alexander & Brown (2011) Medial prefrontal cortex as an action-outcome predictor (PRO model), *Nat Neurosci*: https://pmc.ncbi.nlm.nih.gov/articles/PMC4077597/ · review: https://onlinelibrary.wiley.com/doi/full/10.1111/tops.12307
- Friston (2009) Predictive coding under the free-energy principle: https://pubmed.ncbi.nlm.nih.gov/19528002/ · precision weighting / attention & free-energy: https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2010.00215/full
- McClelland, McNaughton, O'Reilly (1995) Why there are complementary learning systems: https://www.researchgate.net/publication/15575602
- Winocur & Moscovitch (2011) Memory transformation and systems consolidation, *JINS* (Trace Transformation Theory): https://www.semanticscholar.org/paper/c1f6c35717ae3999b3d68d82fbd357b816078de1 · No consolidation without representation: https://www.cell.com/neuron/pdf/S0896-6273(21)00291-9.pdf
- Tse et al. (2007) Schemas and memory consolidation, *Science*: https://pubmed.ncbi.nlm.nih.gov/17412951/ · Tse et al. (2011) Schema-dependent gene activation, *Science*: https://pubmed.ncbi.nlm.nih.gov/21737703/
- Bartlett (1932) *Remembering*; Alba & Hasher (1983) Is memory schematic? *Psych Bulletin* (via Winocur & Moscovitch, above).
- Hopfield attractor energy minimisation (content-addressable memory, pattern completion to nearest low-energy attractor): https://pmc.ncbi.nlm.nih.gov/articles/PMC7498056/
