# Adversarial brain-fidelity architecture audit -- grounded self-growing narrative comprehension (2026-08-09)

**Filed by:** research (Opus), director-assigned ADVERSARIAL SHAPE+POSITION+METRIC audit ahead of a
multi-month capstone commit. **Charge:** actively hunt for places the assembled architecture calls a
computational CONVENIENCE "brain-foundational," or diverges from the brain's actual mechanism SHAPE, and
name them honestly. Not a rubber-stamp. **Method:** read the ACTUAL CODE of every named owned organ
(`grounding_acquisition_loop.py`, `predictive_coding.py`, `event_bundle.py`, `schema_exemplar_bayes.py`,
`learner/core.py`, `situation_model_accumulate.py`) rather than the notes' descriptions of them, so every
SHAPE verdict below is checked against the function signatures and gate logic on disk; plus 2 parallel Sonnet
lit-scan lanes on three of the four genuinely-contested brain-fidelity questions (MDL-as-commit-criterion;
convolution-binding-plausibility + sleep-timing-shape), primary-source verified and integrated. The fourth
(CRP-as-event-clustering, row 6) was finalized from Opus domain knowledge in the foreground per explicit
coordinator direction not to block delivery on a third lane -- flagged and separately calibrated in row 6,
not presented as sub-agent-verified. A coordinator precision-check on row 7 (real-valued HRR vs
FHRR-unitary vs VTB) caught and corrected an evidentiary overreach in the first draft; the correction is
folded into row 7 below, not hidden.

---

## HEADLINE

**The DIRECTION is brain-foundational at the systems level -- but the "brain-foundational" label is
attached most confidently to the ASPIRATIONAL design, while the WIRED code is largely a set of statistical
and engineering CONVENIENCES, and two load-bearing mechanisms (the MDL commit gate, the CRP library key)
are Marr COMPUTATIONAL-level rational analyses being counted as if they were algorithmic/implementational
brain mechanisms.** This is not dishonesty -- the drill notes flag most individual deviations openly -- but
the composite picture the USER needs is: committing to the capstone means committing to BUILD several
brain-faithful mechanisms that the substrate does not yet own, not shipping a substrate that already
implements them. Three pillars are genuinely brain-grounded and should be the load-bearing story: (1) the
CLS engine TOPOLOGY (fast pattern-separated episodic capture that is never overwritten + a slow offline
extraction pass -- McClelland/McNaughton/O'Reilly 1995, Kumaran/Hassabis/McClelland 2016); (2) the GRAIN
(scripts/schemas -- Baldassano/Hasson/Norman 2018 is DIRECT neural evidence for story-independent schema
representations, the single strongest citation in the program); (3) the FLAG SIGNAL PRINCIPLE (relative
self-referential prediction error -- Reynolds/Zacks/Braver 2007, doubly cross-validated by the statistical-
learning literature). The weak points, ranked: the GUARD's wired signal computes a DIFFERENT thing
(split-half test-retest RELIABILITY) than the brain structure it is mapped to (vmPFC congruency); the CRP
library key is a convenient nonparametric prior when the brain-foundational shape is the owned DG/CA3
pattern-separation/completion circuit; the FHRR/bipolar binding OPERATOR is an engineering convenience
(and the wired event codec is in a DIFFERENT algebra family, BSC, than the FHRR scripts it must compose
with -- an internal inconsistency, not just a fidelity gap); and offline consolidation is a UNIFORM batch
sweep when the brain replays a PRIORITIZED subset (the substrate owns `surprise_order` for exactly this but
leaves it diagnostic-only, ungated).

**Overall verdict: brain-COMPATIBLE at the systems level, with named computational-level-vs-
implementational-level gaps. Recommendation: GO-WITH-CORRECTIONS.** Six SHAPE corrections below, five of
which are cheap (relabelings + wiring an already-owned organ), one of which is a genuine build. The
direction does not need to be abandoned or re-founded; it needs its brain-fidelity claims tagged to the
right Marr level and its highest-risk novel piece (match-or-spawn) re-grounded on the owned CA3/DG organ
instead of a borrowed statistical prior.

**P_deflated (the claim "the architecture AS CURRENTLY WIRED is brain-foundational in the strict
SHAPE+POSITION+METRIC sense"): 0.33** -- deflated below the 0.50 novel-synthesis cap because of the
wired-vs-aspirational gap and the two Marr-level category slips. **P_deflated (the claim "the architecture
WITH the six corrections is a defensible brain-COMPATIBLE design"): ~0.55** (reported for contrast; the
corrections are mostly honesty relabelings + wiring an owned organ, low execution risk).

---

## The per-component verdict table (SHAPE + POSITION + METRIC)

Legend: **FOUNDATIONAL** = directly an observed brain mechanism; **COMPATIBLE** = a published
computational-neuroscience model of that exact process; **DEVIATION** = convenience or divergence.
"Wired" = what the code on disk actually does today; "Planned" = the drill-note design not yet built.

| # | Component | Brain structure claimed | SHAPE | POSITION | METRIC | Verdict |
|---|---|---|---|---|---|---|
| 1 | ENGINE (FLAG->library->CONSOLIDATE->GUARD->BANK->GROW) | CLS: hippocampal fast capture + neocortical schema extraction + offline replay | Match: traces kept separate (never folded at intake) = pattern-separated episodic store; offline pass = neocortical extraction; committed items = semantic | Right: offline consolidation separated from online flag/read | Right: extract cross-episode structure while protecting episodic detail from interference | **COMPATIBLE** (strong; faithful CLS instantiation) |
| 2 | FLAG = EST relative prediction error | Event Segmentation Theory (Reynolds/Zacks/Braver 2007); statistical event-structure learning (Baldwin 2008) | PRINCIPLE match (relative self-referential PE). **WIRED code does NOT implement it** -- flags on isolated verb-lemma MET/UNMET polarity; `threshold_gate` is ABSOLUTE | Wired signal fires per-episode teacher label, not continuously at boundaries | Wired classifies lemma outcome polarity, not PE against a maintained event model | **PRINCIPLE FOUNDATIONAL; WIRED DEVIATION** |
| 3 | GRAIN = scripts/schemas | Ghosh-Gilboa 2014; **Baldassano/Hasson/Norman 2018** (story-independent schema patterns in PMC/mPFC); Schank-Abelson | Match: recurring typed-role event-types = the story-independent schema patterns Baldassano decodes | n/a (representational grain) | Match: generalize across narratives, not memorize surface | **FOUNDATIONAL** (grain choice); binding operator caveat -> row 7 |
| 4 | GUARD = escalate-don't-force-commit | Warren 2014 (vmPFC same circuit for true+false learning); van Kesteren SLIMM 2012 (vmPFC congruency) | PRINCIPLE match (conjunction of independent signals, never force-commit). **Wired signal = split-half cosine of an item's OWN traces = test-retest RELIABILITY, NOT congruency-with-an-existing-schema** | Right: fires at consolidation | Wired optimizes internal trace consistency; SLIMM optimizes input-vs-schema match -- different objectives | **PRINCIPLE COMPATIBLE; WIRED SIGNAL DEVIATION + mislabeled brain structure** |
| 5 | COMMIT gate = MDL `per_cluster_gate`/`KEEP_EPISODIC` | Perfors-Tenenbaum 2009 two-part code; mapped to Ghosh-Gilboa/Preston-Eichenbaum | Marr COMPUTATIONAL-level equivalence ("compress past null" ~ "structure out-predicts noise"), not a shape identity. Induces a SYMBOLIC conjunction rule -- more symbolic than the distributed schema elsewhere | Right position (consolidation) | MDL optimizes description-length in bits; brain optimizes predictive utility/interference -- Occam-related, not identical | **COMPATIBLE (computational-level rational proxy), NOT FOUNDATIONAL** |
| 6 | KEYING = sticky-CRP soft-match-or-spawn | Franklin/Norman/Gershman 2020 SEM; latent-cause inference (Gershman/Niv) | FUNCTION (reuse-vs-spawn) is real; CRP-stickiness MATH is a nonparametric convenience. Brain shape = DG pattern-separation (spawn) / CA3 completion (reuse). **WIRED code keys by EXACT LEMMA STRING** -- CRP entirely aspirational | Right position (intake/library) | CRP concentration parameter vs neural novelty threshold -- no established bridge | **FUNCTION FOUNDATIONAL (DG/CA3); CRP formalism CONVENIENCE; WIRED = DEVIATION placeholder** |
| 7 | REPRESENTATION = FHRR/VSA + EventBundleCodec role-filler binding | Eliasmith NEF/Spaun; TEM (Whittington 2020) conjunctive binding; binding-problem literature | Structure/content FACTORIZATION = FOUNDATIONAL (TEM, Baldassano). Binding OPERATOR = circular-convolution/complex-multiply = COMPRESSED; brain evidence (TEM) is OUTER-PRODUCT/conjunctive = EXPANDED. **Wired event codec is BIPOLAR (BSC), not FHRR** -- can't bind to FHRR script roles without a port | n/a | FHRR preserves separable retrieval approximately (capacity-bounded) vs dedicated conjunctive cells | **FACTORIZATION FOUNDATIONAL; OPERATOR DEVIATION (honestly labeled) + internal dtype inconsistency** |
| 8 | CHAINING = multi-step situation-model inference | Mattar & Daw 2018 (replay chains one-step backups); Trabasso G-A-O recursion; Spaun decode-reinject | decode-cleanup-feedforward = SPA-faithful shape. **DEVIATION: pure-vector chaining compounds error MULTIPLICATIVELY; brain re-grounds via replay of ACTUAL episodes, not lossy vector iteration** | Right (inference/retrieval) | Mattar-Daw prioritizes by expected value of backup; design chains by content-similarity | **COMPATIBLE (shape) with a real error-control DEVIATION (honestly flagged)** |
| 9 | CONTROL FLOW timing (offline sleep passes) | Wake-encode/sleep-consolidate; Dumay-Gaskell 2007 (sleep-not-time); prioritized replay | Offline-separate + intervening-pass rule = faithful. **DEVIATION: `consolidation_pass` sweeps the WHOLE library UNIFORMLY; brain replays a PRIORITIZED subset. `surprise_order` exists but is diagnostic-only, never gates** | Coarse position right (offline) | Brain selectively strengthens surprising/relevant; code strengthens all eligible uniformly | **PARTIALLY COMPATIBLE; uniform-batch = DEVIATION (fixable with owned organ)** |

---

## Component-by-component detail (the adversarial read)

### 1. ENGINE topology -- COMPATIBLE (strongest architectural pillar)

The loop's division of labor is a genuinely faithful instantiation of Complementary Learning Systems.
`grounding_acquisition_loop.Trace` is kept SEPARATE per episode and never folded/averaged at intake
(disk-verified: `Library.flag` appends a `Trace`; nothing averages) -- this is exactly the hippocampal
pattern-separated store, and it means a schema commit never destroys the individuating detail (the
Preston-Eichenbaum "stored separately, not overwritten" property). `consolidation_pass` is the offline
neocortical extraction pass. `GROUNDED_*` items are the semanticized output. The one honest caveat: CLS is
a systems-level THEORY/framework, not a single observed mechanism, so this is COMPATIBLE (faithful
implementation of a well-supported framework), not FOUNDATIONAL (a directly observed circuit). The
sub-mechanisms hanging off this topology are where the fidelity gaps live (rows 2, 4, 5, 6, 9).

### 2. FLAG signal -- PRINCIPLE FOUNDATIONAL, WIRED DEVIATION (the aspirational-vs-wired gap, exhibit A)

This is the clearest case of the headline pattern. The DESIGNED signal -- relative self-referential
prediction error, `residual(t)/running_avg(residual) > threshold` against a situation-model register -- is
FOUNDATIONAL-grade: EST is field consensus and the statistical-learning literature (Baldwin 2008, Stahl
2014) independently converges on relative-not-absolute from a different paradigm. But the CODE ON DISK does
not do this. The wired FLAG is `consequence_learning_loop.teacher_verdict(signal_mode="signal_a_only")` --
an isolated verb-lemma MET/UNMET polarity classification -- and `predictive_coding.threshold_gate` uses an
ABSOLUTE `residual_mag >= threshold` test (disk-verified, lines 102-125). The research note's own
"wrong-grain" diagnosis is correct and honest. The point for the USER: the brain-foundational FLAG is a
BUILD TARGET (handoff anchor 2, `relative_threshold_gate`), not an owned capability. **Fix:** build anchor
2 AND compute the relative signal against an `AccumulateRegister` situation-model register (not a lemma) --
both are in the plan; the honest framing is "we will build the brain-faithful flag," not "we have it."

### 3. GRAIN -- FOUNDATIONAL (correct choice)

Scripts/schemas as recurring typed-role event-types is the right grain and the best-evidenced pillar.
Baldassano/Hasson/Norman 2018 found story-INDEPENDENT schema patterns (a "restaurant" pattern recognizable
across unrelated narratives) in posterior medial cortex/mPFC/superior frontal gyrus -- direct neural
evidence, in narrative comprehension specifically, for exactly this grain. This should be the PRIMARY
brain-grounding citation, with TEM as the mechanistic complement. No divergence at the grain level; the
only question is whether the REPRESENTATION of the grain matches the brain (row 7).

### 4. GUARD -- PRINCIPLE COMPATIBLE, WIRED SIGNAL DEVIATION with a mislabeled brain structure (weak point)

The guard's JUSTIFICATION is sound: Warren 2014 shows the same vmPFC circuit that fast-tracks true schema
learning also manufactures false memories, so a single fooled signal must not force a commit -- hence a
conjunction of independent signals. That principle is COMPATIBLE. But the WIRED signal
`schema_consistency_split_half` (disk-verified, lines 156-180) computes the cosine between two disjoint
HALVES of an item's OWN accumulated context vectors. That is a test-retest RELIABILITY metric
(psychometrics) -- "are my repeated observations of this item mutually consistent" -- which is closer to
Ghosh-Gilboa criteria 2+3 (multiple episodes, shared abstracted structure) than to the vmPFC CONGRUENCY
signal it is mapped to in the notes. Congruency (SLIMM) is a match between INCOMING input and an EXISTING
schema template; split-half is internal self-consistency. These are different computations with different
failure modes. The prereg is honest ("standing in for a full FHRR/hippocampal-encoder CA3-complete
wiring"), but the brain-structure NAME is a loose mapping. **Fix (cheap):** relabel split-half honestly as
a cross-episode reliability/regularity check (Ghosh-Gilboa criterion), OR build a genuine congruency signal
= cosine(incoming trace, existing schema prototype). Do not call the current signal "vmPFC congruency."

### 5. COMMIT gate (MDL) -- COMPATIBLE at computational level, NOT FOUNDATIONAL (adjudication requested)

**Adjudication (Lane-1 verified): MDL/two-part-code is COMPATIBLE at Marr's COMPUTATIONAL level; a
DEVIATION if asserted as the algorithmic/implementational commit mechanism.** The brain does not compute
description-length in bits as the consolidation trigger. Lane-1's primary-source scan is decisive on both
directions:
- **No study exists** that measures a code-length/bits quantity gating the episodic->schema transition. The
  literature that actually studies the MECHANISM uses a DIFFERENT vocabulary entirely: congruency/prediction-
  error (van Kesteren SLIMM 2012 -- note this is the LIKELIHOOD/fit term of a Bayesian objective, NOT the
  complexity-penalty term MDL contributes), immediate-early-gene cascade thresholds contingent on a
  pre-existing scaffold (Tse et al. 2007/2011 *Science* -- the most mechanistic entry), replay/reactivation
  dialogue count (Preston-Eichenbaum 2013), and gradual interleaving (McClelland/McNaughton/O'Reilly 1995;
  McClelland 2013, which itself revises toward CONGRUENCY-gated fast cortical learning, not compression).
- The compression-in-bits result that IS neurally real (Al Roumi/Planton/Dehaene 2023 *eLife*; Al Roumi et
  al. 2021 *Neuron* -- dlPFC tracks minimal-description-length of a sequence) measures ~16-item WORKING-MEMORY
  sequence compression over SECONDS, not the hippocampal->neocortical schema commit over days. Citing it for
  the commit question would be a category substitution.
- Perfors-Tenenbaum 2009 and Kemp-Tenenbaum 2008 are, by their own lineage's explicit framing (Griffiths/
  Chater/Kemp/Perfors/Tenenbaum 2010 *TiCS*; Griffiths 2015; Perfors 2012), Marr COMPUTATIONAL-level ("ideal
  learner") models -- Chater's own PNAS companion to Kemp-Tenenbaum 2008 is titled "Induction as model
  selection." A very recent preprint on consolidation (Fountas et al. 2026, "Why the Brain Consolidates")
  explicitly states its framework "operates at Marr's computational level, specifying what consolidation
  achieves" -- the cleanest self-aware confirmation of exactly the slip this audit probes.

Two adversarial sharpenings from the CODE: (a) `learner.core.per_cluster_gate` (disk-verified) is correct as
a rational gate, but the plugin it fits (`ruleind_plugin`) induces a SYMBOLIC conjunction rule -- MORE
symbolic than the distributed FHRR schema the rest of the architecture uses, so committing via MDL injects a
representational discontinuity; (b) the gate optimizes bits, the brain optimizes predictive utility /
interference minimization. **Honest label/calibration (Lane-1):** P(bits is literally the schema-commit
decision variable) ~0.10-0.15; P(compression/MDL is a valid citable computational-level redescription of
what consolidation ACHIEVES) ~0.75-0.80. The one rigorous implementational BRIDGE is the free-energy /
Hinton-van Camp 1993 MDL<->variational-free-energy equivalence (accuracy + a complexity code-length term) --
but it is assembled across separately-published pieces, never demonstrated as one measured neural mechanism;
rate it plausible, not established. **Directive:** keep MDL as a GATE; keep the schema representation
distributed; report it as computational-level, NOT as the brain's commit criterion.

### 6. KEYING (sticky-CRP) -- FUNCTION FOUNDATIONAL, CRP a CONVENIENCE, WIRED a placeholder (highest-risk novel piece; finalized)

**Adjudication (finalized from primary-literature domain knowledge -- this row's dedicated lit-scan lane did
not return before the foreground deadline; citations below are Opus knowledge, not sub-agent WebFetch-
verified this session, and are deflated accordingly, though DG/CA3 pattern-separation/completion is
textbook-consensus systems neuroscience with a large converging evidence base, not a fringe claim): the
reuse-vs-spawn FUNCTION is brain-foundational; the CRP-stickiness FORMALISM is a Marr computational-level
nonparametric-Bayes convenience -- the SAME category slip as row 5's MDL; the brain-foundational SHAPE for
match-or-spawn is the owned DG/CA3 pattern-separation/completion circuit, not a CRP sampler.**
- **CRP/latent-cause clustering is COMPATIBLE-at-computational-level, not FOUNDATIONAL.** SEM (Franklin,
  Norman, Ranganath, Zacks & Gershman 2020, *Psychol Rev*) sits in the rational-analysis lineage (Anderson
  1991 rational model of categorization; Sanborn, Griffiths & Navarro 2010 rational process models; Gershman,
  Blei & Niv 2010 *Psychol Rev*, "Context, learning, and extinction," which first applied CRP/latent-cause
  inference to associative learning). These specify WHAT an ideal learner should infer about latent
  structure, not a claim that neurons run Gibbs sampling over a Chinese-Restaurant-Process. No neurophysiology
  anywhere reports a CRP-stickiness/concentration-parameter-like quantity as a measured circuit variable.
- **The implementational-level mechanism for familiar-vs-novel is dentate-gyrus pattern SEPARATION vs CA3
  pattern COMPLETION/attractor dynamics -- extensively validated, not merely hypothesized.** Computational
  proposal: Marr 1971; O'Reilly & McClelland 1994 (DG sparse expansion recoding orthogonalizes similar inputs;
  CA3 recurrent collaterals form an auto-associative attractor that completes a partial/noisy cue to a stored
  pattern). Empirical: Leutgeb, Leutgeb, Moser & Moser 2007 (*Science*, rate remapping in CA3 vs global
  remapping in DG -- a graded separation-completion continuum in vivo); Bakker, Kirwan, Miller & Stark 2008
  (fMRI pattern-separation signature in human DG/CA3); Yassa & Stark 2011 (*Trends Neurosci*, review); most
  decisively, causal evidence from Guzman, Sychiv, Sirenko et al. 2016 (*Nat Neurosci*) and McHugh et al. 2007
  (*Science*, NMDAR CA3 knockout specifically impairs pattern completion) -- optogenetic/genetic, not just
  correlational decoding.
- **The bridge from mechanism to CRP-like BEHAVIOR is published, and it is not a CRP**: Kumaran & McClelland
  2012 (*Psychol Rev*, REMERGE model) shows a recurrent hippocampal network built from pattern-
  completion/attractor dynamics reproduces context-sensitive generalization and clustering behavior
  functionally similar to a rational nonparametric-clustering model's predictions -- without computing a
  Dirichlet process anywhere. CRP is a valid computational-level REDESCRIPTION of the attractor circuit's
  emergent behavior, not a description of the circuit's actual operation -- exactly the row-5 MDL pattern.
- **Novelty gating** (the threshold half of match-or-spawn) has its own implementational literature: Lisman &
  Grace 2005 (hippocampal-VTA loop gating dopamine release on novelty); Vinogradova 2001 (hippocampal
  comparator function) -- the concrete circuit-level analog of what a CRP's concentration parameter only
  redescribes abstractly.
- **On the code:** the WIRED library has no soft-matching at all -- `Library.flag` keys by EXACT LEMMA STRING
  (disk-verified, lines 141-153) -- so the CRP is entirely aspirational, correctly flagged in the design note
  as untested with no owned precedent. The substrate already OWNS the right primitive for the brain-faithful
  fix: `cleanup_family.iterative_attractor`, whose own docstring says "Brain-canonical via CA3 / DG attractor
  dynamics (Treves-Rolls)" (disk-verified).
**Calibration:** P(CRP-stickiness is literally what hippocampal circuitry computes) ~0.05-0.10; P(DG/CA3
pattern-separation/completion is the correct implementational-level shape for match-or-spawn) ~0.80 (high;
large converging causal+correlational base; deflate 0.10-0.15 from a fully fresh-verified figure since this
row's citations are expertise-drawn this session, not freshly WebFetch-checked). **Independent confirmation,
landed after this row was drafted:** a dedicated lit-scan lane completed and self-filed
`notes/research_sem_crp_brain_fidelity_audit_2026-08-09.md` (+ its own exp_dev hand-off) with the SAME
verdict, sub-agent WebFetch-verified: sticky-CRP is a self-disclosed Marr computational-level model (not
validated as a brain mechanism even by SEM's own authors, zero bridge to any neuromodulator even in SEM's
own "Neural Correlates" section) while DG/CA3 pattern-separation/completion is a causally-tested,
continuous-similarity-graded circuit that is the materially better-motivated brain SHAPE for match-or-spawn
-- P_deflated=0.60 on the literature characterization, capped 0.50 on the novel-synthesis replacement
proposal, with its own pre-registered `exp_dg_ca3_vs_crp_match_or_spawn_ablation_v1` cheap decisive test.
Two independently-produced adjudications converging is a strong signal for row 6's verdict; read that note
for the fully sub-agent-verified citation trail in place of relying solely on this row's foreground-drafted
expertise pass. **Fix:** build match-or-spawn
on the owned CA3/DG-labeled attractor primitive plus a novelty threshold (Lisman-Grace-style gate), and
describe CRP ONLY as the rational-level account of what that circuit's aggregate behavior approximates --
never as the mechanism itself. This turns the program's highest-risk novel piece from "a borrowed,
unimplemented statistical prior" into "a wiring of an owned, already-labeled brain-foundational organ" --
strictly better on both engineering risk (no new module) and fidelity (implementational-level, not
computational-level-only).

### 7. REPRESENTATION (FHRR binding) -- FACTORIZATION FOUNDATIONAL, OPERATOR DEVIATION + internal inconsistency (adjudication requested)

**Adjudication (Lane-3 verified): the structure/content FACTORIZATION property is brain-foundational (TEM,
Baldassano); the BINDING OPERATOR -- circular convolution / elementwise complex multiply -- is an
engineering convenience that diverges from the brain's best-evidenced binding shape. DEVIATION.** The
precise divergence: compressed/dimension-PRESERVING convolutional (or complex-multiplicative) binding vs the
brain's dimension-EXPANDING conjunctive/outer-product binding. Lane-3 evidence:
- TEM (Whittington 2020, confirmed via the reproducing formalism arXiv:2112.04035): hippocampal
  representation `p = flatten(x^T g)` -- an explicit OUTER PRODUCT of content code x and structural code g,
  the literal opposite shape from convolution. Bicanski & Burgess's successor likewise uses conjunctive place
  cells. No convolution-based hippocampal-formation model exists.
- Direct physiology converges on conjunctive coding: item-place conjunctive cells (Komorowski/Manns/
  Eichenbaum 2009), ubiquitous cortical/PFC mixed-selectivity (dimension-expanding). Temporal-synchrony
  binding (Singer/Engel) is contested-not-superseded; the binding problem is described as unresolved as of
  2023 (Yu, "Binding Problem 2.0").
- **Circular convolution/HRR has NO direct neurophysiological evidence anywhere.** Plate frames it as a
  connectionist engineering scheme. The strongest "neurally implemented" claim (Eliasmith NEF/SPA/Spaun) is
  an existence proof, not a discovery -- NEF can implement almost any computable operator in spiking
  populations by construction.
- **Precision correction (coordinator-flagged, load-bearing -- my initial draft conflated two distinct
  binding schemes and I retract that conflation here):** `Gosmann & Eliasmith 2019` (*Neural Computation*,
  "Vector-Derived Transformation Binding") replaced circular convolution with VTB specifically because
  REAL-VALUED circular convolution, when realized as a bilinear operation over POPULATION-CODED real vectors
  in a spiking NEF circuit (the SPA/Spaun implementation), needs a disproportionate number of neurons to
  represent the intermediate product terms at low noise. **That is a SPIKING-IMPLEMENTATION-COST critique of
  REAL-VALUED convolution, not a general algebraic indictment of complex-multiplicative binding, and it does
  NOT directly transfer to our substrate.** Our substrate's actual primitive (`situation_model_accumulate.
  unit_phase_vec` -- disk-verified: `torch.polar(ones, theta)`, unit-MAGNITUDE complex phasors) is
  Frady & Sommer's FHRR-unitary formalization, not Plate's real-valued HRR/SPA scheme: binding is exact
  elementwise complex multiplication computed on classical hardware (no population-coded spiking bilinear
  circuit to pay a neuron-cost tax on), and unbind-by-conjugate is EXACT in the noise-free case (confirmed
  by `RelationRegister`'s own docstring proof, `unbind(bind(v,r),r) = v*r*conj(r) = v`, disk-verified). So
  citing Gosmann & Eliasmith's abandonment of convolution as if it settled a brain-fidelity question about
  OUR complex-unitary FHRR was an overreach; I withdraw that specific inferential step.
- **What DOES survive, on separate and still-valid grounds, is a narrower, ENGINEERING/CAPACITY caveat, not
  a brain-fidelity one**: the same Schlegel/Neubert/Protzel benchmark already read in full for the sibling
  VSA note (arXiv:2001.11797) tests FHRR as its OWN distinct VSA family (separately from real-valued HRR and
  MAP-C), and even FHRR sits in the "moderate" (~0.6 similarity retained), not best-case VTB (~0.8+), band
  under DEEP repeated/chained binding (depth-40). This is a property of algebraic noise-accumulation under
  REPEATED composition -- unrelated to spiking-implementation cost -- and it is already the exact concern
  row 8/Prediction 4 flags for the program's recursive multi-hop chaining design. It is a real risk to
  MANAGE (shallow chain depth, abstain-band, per-hop re-grounding -- row 8's own fix), not evidence that
  FHRR is neurally unfaithful.
- The complex-FHRR variant's best BIOLOGICAL-PLAUSIBILITY story (as opposed to the capacity story above) is
  Frady & Sommer 2019 (*PNAS*): a theoretical isomorphism between complex-phasor multiplication and
  spike-timing/phase coding -- elegant and constructive, but not an in-vivo observation, and it inherits
  synchrony binding's contested (Singer/Engel vs. unresolved, per Yu 2023 "Binding Problem 2.0") status.
**Corrected verdict, same DEVIATION conclusion, right grounds this time**: neither real-valued HRR, nor
FHRR-unitary, nor VTB has ANY direct neurophysiological evidence for the binding OPERATOR itself -- NEF's
ability to implement whichever operator a team picks in spiking neurons is an existence-proof that applies
equally to all three, so choice among them is an ENGINEERING decision, not a fidelity one. The
best-evidenced actual brain binding mechanism (TEM outer-product/conjunctive coding) is a structurally
DIFFERENT (dimension-EXPANDING) algebraic family than any convolution-family operator (real HRR, FHRR, VTB
alike, all dimension-PRESERVING/compressive) -- this axis of the DEVIATION is independent of which
convolution-family variant is chosen. Calibration: P(any convolution-family operator, FHRR included, is
neurally faithful as the binding SHAPE) ~0.15; P(conjunctive/outer-product is the better-supported binding
shape) ~0.75. **Practical implication: VTB is NOT a brain-fidelity upgrade over FHRR** (neither has neural
support) **and should be evaluated, if at all, purely as an engineering fix for row 8's deep-chaining
capacity risk -- label any such swap as capacity-motivated, never as closing the fidelity gap.** The design
notes' existing honesty ("never report as 'the brain uses FHRR' or 'circular convolution'") is correct and
this audit's contribution is sharpening WHY (dimension-expanding vs -preserving), not just flagging that a
caveat is needed.
**A second, code-level finding the notes flag but the USER should weigh:** `event_bundle.EventBundleCodec`
is BIPOLAR (BSC -- elementwise sign multiply, disk-verified: it reuses `role_slot_summarizer._bipolar_bind`),
NOT FHRR complex64. BSC binding is even further from any brain mechanism (it is Boolean), and -- more
practically -- a bipolar event vector cannot bind to an FHRR script-role vector without an explicit port.
So the "representation pillar" currently spans TWO algebra families that do not compose. **Fix:** (a) label
the binding operator as a compressed engineering convenience, claim only the factorization property as
brain-foundational; (b) resolve the internal inconsistency by porting `EventBundleCodec`'s proven pattern to
FHRR (VSA-note resolution (i)) before building the event->script hierarchy, so the whole stack is one family.

### 8. CHAINING -- COMPATIBLE shape, real error-control DEVIATION (honestly flagged)

The "decode a role filler, clean it up, re-inject as the next query" shape is genuinely how Spaun chains
(Eliasmith), and the recursive Goal->Attempt->Outcome->new-Goal unit is discourse-psych-grounded (Trabasso).
So the SHAPE is COMPATIBLE. The DEVIATION, which the VSA note flags honestly (Prediction 4), is that pure
vector chaining compounds unbinding error MULTIPLICATIVELY per hop, whereas the brain does NOT chain purely
through decoded vectors -- Mattar & Daw 2018 show it re-grounds by REPLAYING actual stored one-step
experiences and stitching them, which avoids compounding lossy decodes. **Fix (already the note's own):**
per-hop re-grounding against the actual stored `Trace`s (the substrate keeps them all), not pure vector
iteration; budget shallow depth (single digits) with a hard abstain-band on cleanup confidence.

### 9. CONTROL-FLOW timing -- PARTIALLY COMPATIBLE; uniform-batch is a DEVIATION with an owned fix (adjudication requested)

**Adjudication (Lane-3B verified): offline-separated-from-online + the mandatory-intervening-pass rule are
faithful; the uniform-whole-library batch sweep is a DEVIATION on BOTH axes (uniform-vs-prioritized AND
single-pass-vs-gradual) -- about as clean a deviation as the literature allows.** Lane-3B evidence:
- Prioritization is the mechanism's CENTRAL feature, not incidental: Mattar & Daw 2018 (replay ordered by
  utility, explicitly against uniform access); *Nat Commun* 2023 (PMC10710481) -- sleep-replay priority is
  set by cumulative AWAKE replay (novelty-driven), and if sleep does not occur within 24h the saliency bias
  is PERMANENTLY LOST -- a late uniform sweep cannot recover it.
- Selectivity survives to within-episode granularity: Payne & Kensinger -- sleep BOOSTS emotionally salient
  objects WHILE DEGRADING neutral content from the SAME scene; a uniform sweep cannot produce this
  dissociation. Molecular backing: synaptic tagging-and-capture (Frey & Morris 1997; Redondo & Morris 2011)
  -- only tagged synapses capture consolidation resources.
- No consolidation theory is single-pass: standard model (weeks-years), MTT/TTT (Nadel & Moscovitch;
  Winocur & Moscovitch) go further -- ongoing, interactive, some episodic detail NEVER fully transfers.
- Dumay & Gaskell 2007 (mandatory intervening SLEEP, not elapsed time) VERIFIED but domain-scoped to
  lexical/declarative; Tamminen spindle-dose follow-ups show it scales with reactivation DOSE, not a boolean
  one-pass checkbox. (P that the intervening-pass rule generalizes beyond lexical memory ~0.35.)
The code's `consolidation_pass` (disk-verified, lines 208-270) iterates over ALL items uniformly each pass.
The substrate OWNS the right mechanism -- `surprise_order` (Tamminen/Rasch selective-replay ordering) -- but
it is DIAGNOSTIC ONLY and gates nothing (disk-verified: docstring says "does not itself gate anything"). The
intervening-pass rule IS implemented faithfully. The "frozen after commit" choice (`GROUNDED_*` terminal;
`Library.flag` no-ops on non-PENDING) is a real DEVIATION from Ghosh-Gilboa criterion 4 (schemas stay
adaptable) AND from MTT/TTT (some memories never terminally consolidate) -- honestly flagged as a
false-memory-safety tradeoff. Lane-3B: P(uniform-batch-sweep is brain-faithful) ~0.08. **Fix (cheap, owned
organ):** wire `surprise_order` to prioritize/subsample which items get a consolidation attempt (or their
replay budget), add a lightweight encoding-time "tag" decoupling was-touched from was-consolidated, and
distribute replay across many cycles with strength compounding over selection frequency; keep the
intervening-pass rule; consider a guarded re-opening path for committed schemas.

---

## The two systematic findings (the adversarial synthesis)

**Finding A -- the aspirational-vs-wired gap.** Across rows 2, 4, 6, 7, the "brain-foundational" version is
the PLANNED design and the WIRED code is a convenience: FLAG (wired = lemma polarity vote; planned = relative
PE), GUARD (wired = split-half reliability; planned/claimed = vmPFC congruency), KEYING (wired = exact lemma
string; planned = CRP soft-match), event REPRESENTATION (wired = bipolar BSC; planned = FHRR). The capstone
commit is therefore a commit to BUILD brain-faithful mechanisms, not to a substrate that has them. That is a
legitimate program -- but it should be stated that way to the USER, because the honest current state is
"CLS-shaped scaffold with placeholder sub-mechanisms," not "a brain-faithful comprehender."

**Finding B -- the Marr-level category slip.** Two load-bearing "brain-foundational" claims (MDL commit,
CRP keying) are Marr COMPUTATIONAL-level rational analyses. The project's own discipline (SHAPE+POSITION+
METRIC) is an ALGORITHMIC/IMPLEMENTATIONAL-level fidelity standard. Counting computational-level equivalence
as SHAPE fidelity is a category error. The fix is a discipline addition, not a redesign: tag every mechanism
with its Marr level, and require an implementational-level bridge (DG/CA3 for match-or-spawn; replay-budget/
metabolic cost for MDL-Occam) before any mechanism is called FOUNDATIONAL rather than COMPATIBLE.

---

## Cheap decisive test (brain-fidelity discriminators, not new capability claims)

These are the cheapest experiments that would VERIFY (or falsify) the contested brain-fidelity claims BEFORE
the multi-month build leans on them. All reuse owned organs; CPU-only.

1. **Does split-half behave like congruency or like reliability? (row 4)** Construct (a) a coherent-repeat
   trace set, (b) a set where each incoming trace is individually schema-CONGRUENT with a fixed prototype but
   the traces are mutually INDEPENDENT in content. A genuine congruency signal fires HIGH on (b); a
   reliability signal fires LOW on (b). Run `schema_consistency_split_half` on both. This decides empirically
   whether the current signal is what the notes call it. (Prediction: it behaves as reliability, not
   congruency -- i.e. the brain-structure label is wrong and should be corrected.)
2. **Does the owned CA3/DG attractor beat CRP-stickiness on match-or-spawn? (row 6)** On a toy set with
   known event-type membership + genuine novel items, compare (a) `cleanup_family.iterative_attractor` +
   novelty threshold vs (b) a cosine-CRP-stickiness rule, on spawn-precision / reuse-recall. If the owned
   attractor is at least as good, the fix (re-ground on CA3/DG) is free and strictly more brain-foundational.
3. **Does wiring `surprise_order` to gate replay change what consolidates? (row 9)** A/B: uniform batch pass
   vs surprise-prioritized subsampled pass, on commit-correctness + false-consolidation resistance. If
   prioritized replay is at least as safe and no worse on growth, selective replay becomes functional at
   near-zero cost.
4. **Is the wired FLAG actually worse-grain than EST? (row 2)** The handoff's anchor-2 paired comparison
   (relative_threshold_gate vs signal_a_only on the same corpus) already tests this; run it before anchor 3.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**P1 -- the split-half-is-not-congruency claim (row 4).** P = 0.70 (high; this is a code-behavior claim, not
a novel synthesis).
- HARD-PASS: `schema_consistency_split_half` scores the mutually-independent-but-each-congruent set (test 1b)
  LOW (< 0.35, near its own scrambled-noise floor), confirming it measures internal reliability, not
  input-vs-schema congruency -> the vmPFC-congruency label must be corrected to a Ghosh-Gilboa reliability
  label.
- HARD-FAIL: it scores 1b HIGH (> 0.7, near the coherent-repeat ceiling), which would mean split-half DOES
  capture congruency and the label is defensible -- I would withdraw the row-4 correction.

**P2 -- CA3/DG is at least as good as CRP for match-or-spawn (row 6).** P = 0.45 (deflated; owned-attractor
transfer to this task is plausible but untested).
- HARD-PASS: `iterative_attractor` + novelty threshold matches or beats cosine-CRP-stickiness on
  spawn-precision AND reuse-recall on the toy set (within 0.05), licensing the brain-foundational re-grounding
  at no accuracy cost.
- HARD-FAIL: the attractor is worse by > 0.15 on either metric -> CRP-stickiness earns its place as a
  necessary convenience, and it must be labeled a computational-level prior (not brain-foundational),
  carried explicitly as the program's one deliberate non-foundational event-clustering choice.

**P3 -- the Marr-level relabelings do not weaken the program's product claim.** P = 0.60.
- HARD-PASS: after tagging MDL/CRP as computational-level and correcting the guard label, the program's
  DEFENSIBLE claim (glass-box, self-growing, improves-with-exposure at script grain, auditable trace) is
  unchanged -- the corrections cost only overclaim, not capability.
- HARD-FAIL: a corrected claim collapses to "a rational-model pipeline with a CLS-shaped wrapper" with no
  distinct brain-foundational content -> the program's brain-foundational thesis was resting on the
  mislabels, a NO-GO signal. (I do not expect this: rows 1, 3, and the relative-PE principle survive
  correction intact.)

**HARD-FAIL for the WHOLE audit's GO recommendation (pre-registered):** if the capstone build proceeds while
(a) continuing to call MDL/CRP the brain's commit/clustering criterion, (b) leaving the guard mislabeled as
vmPFC congruency, and (c) building match-or-spawn on CRP without evaluating the owned CA3/DG organ -- then the
program is optimizing "sounds brain-foundational" over "is brain-foundational," which is exactly the failure
mode this audit exists to catch. The GO is conditional on the six corrections being at least LOGGED as
required, not silently dropped.

---

## GO / GO-WITH-CORRECTIONS / NO-GO

**GO-WITH-CORRECTIONS.** The direction is brain-foundational at the systems level and the divergences are
mostly honestly-labeled conveniences with clear brain-faithful fixes, not fatal flaws. Make these SHAPE
corrections before/during the capstone (five cheap, one build):

1. **[Honesty, zero cost] Tag every mechanism's Marr level.** Stop calling MDL (row 5) and CRP (row 6) "the
   brain's commit/clustering criterion." Label them computational-level rational proxies. This is the single
   most important correction and it costs nothing but discipline.
2. **[Relabel or build, cheap] Fix the guard's brain-structure claim (row 4).** Split-half is a cross-episode
   RELIABILITY check (Ghosh-Gilboa), not vmPFC congruency. Relabel, or build a genuine congruency signal.
   Run cheap-test 1 to decide empirically.
3. **[Re-ground on owned organ, cheap] Build match-or-spawn on the owned CA3/DG attractor**
   (`cleanup_family.iterative_attractor`) + novelty threshold, with CRP as the rational-level description
   only (row 6). Run cheap-test 2 first. This de-risks the program's highest-risk novel piece.
4. **[Port, mechanical] Resolve the representation dtype inconsistency (row 7):** port `EventBundleCodec`
   bipolar->FHRR before building the event->script hierarchy, and label the binding operator (whichever
   convolution-family variant is used -- FHRR-unitary by default) a compressed engineering convenience,
   claiming only the structure/content factorization as foundational. **Do NOT swap to VTB as a "fidelity
   fix"** -- neither operator has neural support, so that choice is capacity-motivated only (row 8's deep-
   chaining risk, Prediction 4), never fidelity-motivated; if VTB is adopted, label it that way explicitly.
5. **[Wire owned organ, cheap] Make `surprise_order` gate/prioritize replay (row 9)** instead of leaving it
   diagnostic-only, so selective replay is functional. Run cheap-test 3.
6. **[Build, sequenced] Build the relative-PE FLAG against a situation-model register (row 2)** as handoff
   anchor 2 already specifies -- and frame it honestly as building the brain-faithful flag, not as owning it.

Keep the plan's existing good disciplines: strict anchor sequencing (1->2->3, don't compound unvalidated
primitives); pairscramble + adversarial-item guard invariants as hard gates; the intervening-pass rule; the
never-overwrite-episodic-detail property. One sequencing caution: handoff anchor 1 wires the MDL gate on the
CURRENT lemma-keyed (wrong-grain) library -- fine as a cheap non-redundancy check, but a PASS there does NOT
validate the brain-foundational commit criterion; the real fidelity test is anchor 3.

**Why not NO-GO:** rows 1, 3, and the relative-PE principle are genuinely brain-grounded and survive every
correction; the corrections remove overclaim, they do not remove capability. **Why not clean GO:**
committing while the two Marr-level slips and the guard mislabel stand would let "sounds brain-foundational"
substitute for "is," against the USER's explicit charge.

---

## Cross-thread synthesis

- **Audits, does not duplicate,** the three same-day drills (`research_brain_script_acquisition_
  consolidation_2026-08-09.md`, `research_vsa_script_representation_chaining_2026-08-09.md`,
  `research_narrative_benchmark_scout_2026-08-09.md`) and the handoff. Those notes DESIGN the architecture and
  are individually honest about most deviations; this note's contribution is the COMPOSITE adversarial read
  they cannot give themselves -- the two systematic patterns (aspirational-vs-wired gap; Marr-level slip) are
  only visible across the whole assembly, and the guard-mislabel (row 4) and the CA3/DG-beats-CRP fix (row 6)
  are corrections the design notes did not make.
- **Converges with** the same-day `director_brain_fidelity_audit_shape_position_metric_2026-08-09.md`, which
  audits the COMPLEMENTARY goal-achievement pipeline and finds its core SHAPE gap is feed-forward-extract-
  then-compare vs the brain's RECURRENT goal-conditioned / predictive-coding interpretation. That is the SAME
  top-down/predictive-error SHAPE this audit's row 2 (FLAG = relative PE) identifies in the acquisition loop
  -- two independent audits landing on "the brain is predictive/top-down where we are feed-forward/absolute"
  is a strong convergent signal that the relative-PE / goal-conditioned direction is the right SHAPE lever.
- **Consistent with** the arc's standing conclusion that AUDITABILITY, not accuracy-parity, is the defensible
  product edge (`project_glassbox_comprehension_reckoning...`, `research_desiredb_hard_residual...`). None of
  the six corrections touch that edge; correction 1 (Marr-level honesty) strengthens it, because an auditable
  glass-box trace that is ALSO honest about which steps are rational-proxy vs brain-mechanism is more
  defensible than one that overclaims.
- **Reinforces** the USER-locked disciplines `feedback_for_every_mechanism_ask_which_brain_structure_and_does
  _it_share_existing_processes` (row 6's CA3/DG re-grounding is exactly "reuse the existing organ, don't build
  a parallel one") and `feedback_select_by_brain_foundational_right_not_by_cheap` (the audit's whole thrust:
  do not let cheap conveniences masquerade as the foundational choice).

## Substrate-product implications

- The capstone remains worth doing; its value is the brain-faithful glass-box SELF-GROWING architecture, and
  that thesis survives the audit intact for the systems topology + grain + flag-principle.
- The product claim must be tagged to the right Marr level in any write-up or demo: "self-growing script
  grounding with a CLS-shaped acquisition loop, an EST-relative surprise flag, and a glass-box auditable
  commit trace" is defensible; "the brain's MDL commit criterion and CRP event clustering" is not, and would
  not survive an expert challenge.
- The cheapest brain-fidelity ROI is corrections 1-3 and 5 (four relabelings/wirings of owned organs); do
  those before sinking multi-month effort into anchor 3, so the build stands on brain-foundational
  sub-mechanisms rather than placeholders.

## Citations (verified count -- finalized; row 6 completed from domain knowledge in the foreground, not a 4th lit-scan lane)

Primary sources this audit rests on. Rows 1-2, 5, 7, 9 verified via 2 completed parallel Sonnet lit-scan
lanes (WebSearch/WebFetch primary-source checked this session) + the three same-day design drills' own
citation sets; row 6 (CRP/DG-CA3) finalized from Opus domain knowledge per the coordinator's explicit
foreground-completion instruction (dedicated lane not dispatched/awaited) -- flagged and deflated in-line,
though the core DG/CA3 claims are textbook-consensus systems neuroscience, not contested or novel:

McClelland/McNaughton/O'Reilly 1995 (CLS); Kumaran/Hassabis/McClelland 2016; Baldassano/Hasson/Norman 2018
(*J Neurosci*, story-independent schema patterns -- the load-bearing grain citation); Reynolds/Zacks/Braver
2007 (*Cogn Sci*, EST relative-PE); Zacks et al. 2007 (*Psychol Bull*); Baldwin et al. 2008; Stahl et al.
2014; Ghosh & Gilboa 2014 (*Neuropsychologia*); Gilboa & Marlatte 2017 (*TiCS*); van Kesteren et al. 2012
(SLIMM); Preston & Eichenbaum 2013 (*Curr Biol*); Warren et al. 2014 (*J Neurosci*, vmPFC false-memory); Tse
et al. 2007/2011 (*Science*); McClelland 2013 (*JEP:Gen*); Perfors & Tenenbaum 2009; Kemp & Tenenbaum 2008;
Griffiths/Chater/Kemp/Perfors/Tenenbaum 2010 (*TiCS*); Fountas et al. 2026 (consolidation-as-computational-
level preprint); Al Roumi/Planton/Dehaene 2023 (*eLife*) + Al Roumi et al. 2021 (*Neuron*, WM
sequence-compression, category-distinguished from the schema-commit question); Hinton & van Camp 1993
(MDL<->free-energy). **Row 6:** Franklin/Norman/Ranganath/Zacks/Gershman 2020 (*Psychol Rev*, SEM/sticky-
CRP); Gershman/Blei/Niv 2010 (*Psychol Rev*, latent-cause/CRP); Anderson 1991; Sanborn/Griffiths/Navarro
2010; Marr 1971; O'Reilly & McClelland 1994; Leutgeb/Leutgeb/Moser/Moser 2007 (*Science*); Bakker/Kirwan/
Miller/Stark 2008; Yassa & Stark 2011 (*Trends Neurosci*); Guzman et al. 2016 (*Nat Neurosci*); McHugh et al.
2007 (*Science*); Kumaran & McClelland 2012 (*Psychol Rev*, REMERGE); Lisman & Grace 2005; Vinogradova 2001.
**Row 7:** Whittington et al. 2020 (*Cell*, TEM outer-product binding, arXiv:2112.04035 reproducing
formalism); Komorowski/Manns/Eichenbaum 2009 (conjunctive item-place cells); Yu 2023 ("Binding Problem 2.0");
Plate 1995 (HRR); Gosmann & Eliasmith 2019 (*Neural Computation*, VTB -- precisely scoped to real-valued
NEF-spiking convolution cost, per the coordinator-flagged correction above); Frady & Sommer 2019 (*PNAS*,
complex-phasor/phase-coding isomorphism); Schlegel/Neubert/Protzel arXiv:2001.11797 (FHRR-vs-VTB deep-chain
capacity, already in-KB from the sibling VSA note); Eliasmith et al. 2012 (*Science*, Spaun). **Row 9:**
Mattar & Daw 2018 (*Nat Neurosci*, prioritized replay); Dumay & Gaskell 2007 (*Psych Sci*); Tamminen et al.
2010 (*J Neurosci*); PMC10710481 (*Nat Commun* 2023, sleep-replay priority set by awake novelty, 24h decay);
Payne & Kensinger (emotional-salience-selective sleep consolidation); Frey & Morris 1997 + Redondo & Morris
2011 (synaptic tagging-and-capture); Nadel & Moscovitch + Winocur & Moscovitch (MTT/TTT).
