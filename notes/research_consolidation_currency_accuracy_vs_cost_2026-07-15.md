# Research: what does the brain's SELECTIVE consolidation actually optimize — accuracy, or metabolic-cost/capacity?

Filed by: research (Sonnet lit-scan fan-out, Opus synthesis) — 2026-07-15
Trigger: empirical finding that brain-faithful hold/consolidation (CLS hold-then-recover; STC tag-and-capture)
beats decide-at-arrival on accuracy (temporal integration helps, z=25) but adds ~nothing over flat accumulation
of the same accruing evidence. Question: is the elaborate structure an accuracy device that this test simply
doesn't need, or a cost/capacity device that an accuracy-only arena can never price?

**Status note on method:** 4 parallel Sonnet lit-scan sub-agents were dispatched (energy-budget/LTP-cost,
active-forgetting-as-capacity-economy, CLS/STC rationale, temporal-trajectory-coding). This note was first drafted
from established domain knowledge under an explicit "synthesize now" instruction, then REVISED below once all 4
sub-agents landed — their findings are folded in and, in one place, correct/sharpen the initial draft (STC's
founding rationale turns out to be specificity/accuracy-first with capacity-competition as a secondary,
empirically-discovered layer, not the founding motive as first drafted). The citations below are now the
sub-agents' actually-verified sources, not recalled-from-memory placeholders.

## HEADLINE

**Verified across 4 independent lit-scans: the brain's consolidation literature does NOT split cleanly into
"accuracy" vs "cost." Only ONE of the three mechanisms (CLS) has a clean, unmixed rationale — and it is
unambiguously an ACCURACY argument (interference-avoidance), with no capacity framing at all in its founding
papers. The other two (STC, active-forgetting/SHY) are explicitly BUNDLED — the literature does not treat
accuracy/generalization and capacity/cost as competing hypotheses to adjudicate; it presents them as two
faces of one mechanism, with accuracy/generalization getting primary billing and capacity arriving as a real
but secondary, often empirically-discovered-after-the-fact layer (e.g., PRP competition, Fonseca et al. 2004).**

Net read: the null (hold-structure ≈ flat accumulation on accuracy) is a **regime-scope finding, not a refutation
of brain-faithful consolidation generally** — and the regime-scope argument is now on FIRMER ground than in the
first draft, because CLS's benefit (the mechanism most clearly absent from the current test) turns out to have
literally no capacity dimension to it at all: it is 100% about protecting old memories from being overwritten by
new, competing/overlapping information. A single accruing evidence stream for one decision never presents that
competition, so CLS's home-field advantage was never in play. STC and active-forgetting are murkier — their own
literature doesn't cleanly separate accuracy from cost either, so "flat accumulation ties hold-structure on
accuracy" is a weaker refutation of THEM specifically than of CLS, precisely because their own field doesn't
agree the currencies are separable.

## The three mechanisms, disentangled

| Mechanism | Literature | What it optimizes | Currency |
|---|---|---|---|
| **CLS (hippocampal fast-encode → slow interleaved cortical replay)** | McClelland, McNaughton & O'Reilly 1995 *Psychol Rev* "Why there are complementary learning systems"; McClelland 2013 *Psychol Rev* (schema-consistent fast learning); McCloskey & Cohen 1989 (formal catastrophic-interference demonstration) | **Pure accuracy — CONFIRMED, no capacity framing found anywhere in this literature.** The stated reason hippocampus does fast pattern-separated learning while cortex learns slowly/interleaved is that direct fast writes into a shared, overlapping cortical network cause catastrophic interference. Nothing in the founding argument turns on scarce synapses or a metabolic budget — it turns entirely on what happens to superimposed weight changes in overlapping representations. 2013 update reinforces: cortex CAN learn fast when new info is schema-consistent (non-interfering) — interference is the whole deciding variable. | Correctness of OLD memories when NEW, competing/overlapping patterns arrive. Requires ≥2 distinguishable, potentially-interfering items — **absent from the single-stream test**. |
| **STC (synaptic tagging-and-capture)** | Frey & Morris 1997 *Nature*; Redondo & Morris 2011 *Nat Rev Neurosci* "Making memories last"; Fonseca et al. 2004 *Neuron* "Competing for memory" | **Specificity/accuracy is the FOUNDING rationale; capacity-competition is real but secondary/downstream.** Cell-wide PRP synthesis is not synapse-specific, yet LTP is input-specific — the tag exists to route PRPs to the *correct* synapses (an accuracy/assignment argument that would exist even with unlimited protein). Fonseca et al. 2004 later showed synapses genuinely COMPETE for a limited PRP pool under heavy simultaneous demand — a real capacity finding, but discovered as a consequence of tagging, not the reason tagging was proposed. No quantitative "protein available vs needed" ceiling found in the literature (qualitative competition only). | Primarily specificity/correct-assignment (accuracy); capacity-competition emerges only under high simultaneous demand — an empirically real but secondary currency. |
| **Active forgetting / SHY-style downscaling / "good forgetting"** | Richards & Frankland 2017 *Neuron* "The Persistence and Transience of Memory"; Tononi & Cirelli synaptic homeostasis hypothesis (*Sleep Med Rev* 2006, *Neuron* 2014 "Sleep and the Price of Plasticity"); Ronald Davis Drosophila active forgetting (dopamine→Rac1/Cofilin; *Neuron* 2017 "The Biology of Forgetting") | **Generalization/decision-optimization gets primary billing; capacity is explicitly bundled, not separated, by the field itself.** Richards & Frankland state outright: *"the goal of memory is not the transmission of information through time, per se... the goal of memory is to optimize decision-making"* — transience prevents overfitting to episodic detail and supports flexible, generalizable behavior. This is a bias-variance/generalization argument, NOT a resource-scarcity argument in their framing. SHY is the one strand that explicitly bundles BOTH currencies as jointly evidenced consequences of one renormalization process (quote: costs include *"energy, space, supplies, decreased S/N, saturation"* — listed together, not adjudicated). Davis's Drosophila work frames erasure as protecting against interference/decision-blocking, closer to the accuracy side. | Generalization/decision-quality (accuracy at a different level) — primary in the theory literature. Capacity (SHY) is real but explicitly fused with signal-to-noise, not isolated as a separate rival currency. |

Energy-budget grounding (verified): Attwell & Laughlin 2001 (updated by Harris & Attwell 2012 for mammalian,
not squid, AP costs) puts the ~20 W grey-matter budget at roughly AP firing ~47%, postsynaptic glutamate-receptor
effects ~34%, resting potential ~13%, presynaptic release/recycling ~3%. Plasticity/LTP itself is a comparatively
modest slice of the fast-excitatory budget (~4–11%, per a 2019/2020 *J Neurophysiol* "Metabolic constraints on
synaptic learning and memory" analysis), though a cross-species estimate puts long-term-memory formation at
roughly **~10 mJ/bit** (arXiv 2301.09565), with real fitness costs documented in *Drosophila* (LTM consolidation
measurably shortens lifespan under food scarcity) — that paper's own honest caveat: *"biological memory storage is
expensive, but the reason behind it is not known."* Separately, a hard **wiring/volumetric capacity ceiling** is
well supported independent of any accuracy argument: PMC6256250 derives synapse-count-vs-energy-ratio constraints,
and the Chklovskii/Stevens conservation-of-wiring literature shows wiring and spine/glia volume fractions are
near-constant and brain-size-independent. So: a real capacity ceiling exists (moderate-strong support) and
consolidation is genuinely costly (moderate-strong support), but **direct evidence that researchers frame
SELECTIVITY itself as a metabolic-economy decision (rather than a salience/relevance decision) is mixed-to-weak**
— novelty/salience-gating literature (locus coeruleus, dopaminergic gating) leans almost entirely on
behavioral-relevance language, rarely invoking metabolic cost explicitly.

## Cheap decisive test

Run the SAME hold-vs-flat-accumulation comparison, but change what's being asked, along two axes that separate
the three mechanisms above:

1. **Interference axis (tests CLS's actual claim):** present TWO OR MORE competing/overlapping evidence streams
   in sequence (item B's evidence partially overwrites/interferes with item A's stored representation), then ask
   for accurate recall of BOTH A and B, not just a running decision on one accruing stream. Hold-then-consolidate
   should show an accuracy advantage here that flat accumulation cannot, because flat accumulation has no
   mechanism to protect A from being overwritten while B is being integrated. If hold-structure ties flat
   accumulation even here, THAT would be the genuine refutation of CLS's value for this substrate.
2. **Capacity-priced axis (tests STC/SHY's actual claim):** impose an explicit finite-capacity or finite-write-budget
   constraint (a proxy currency — e.g., cap the number of "consolidation writes" or the storage footprint allowed)
   and measure accuracy-per-unit-capacity-spent, not raw accuracy. Hold-then-selectively-capture should show a
   Pareto advantage (same or slightly lower peak accuracy at much lower committed capacity) over flat accumulation,
   which by construction commits capacity indiscriminately.

## Falsifiable predictions

**HARD-PASS (supports "cost/capacity is the real currency, test-design mismatch explains the null"):**
- Axis 1 (interference): hold-structure beats flat accumulation by a comparable effect size to the original z=25
  finding on recall accuracy of the EARLIER item after a later, competing item is integrated.
- Axis 2 (capacity-priced): hold-structure achieves ≥80% of flat-accumulation's peak accuracy at ≤50% of the
  committed-capacity/write budget.
- Either result independently would show the elaborate machinery earns its keep once the right currency is on
  the table — consistent with "accuracy-only, unlimited-capacity, single-stream" being the wrong arena for this
  mechanism, not the mechanism being spurious.

**HARD-FAIL (refutes the cost/capacity defense; supports "genuinely no benefit anywhere, drop it"):**
- Axis 1: hold-structure ties or loses to flat accumulation on recall of the earlier item even under direct
  interference from a later competing stream (i.e., CLS's own home-field advantage doesn't materialize).
- Axis 2: hold-structure's accuracy-per-capacity curve is dominated by flat accumulation everywhere (no
  crossover), i.e., flat accumulation is simply better AND cheaper — no economy to defend.
- If BOTH fail, the honest read is that the brain-faithful structure is not earning anything on this substrate
  in any tested currency, and Frontier-2 (skip the elaborate hold, keep temporal integration only) should be
  adopted without reservation, independent of a capacity-pricing story.

## Trajectory / temporal-order angle (question 3) — verified, stronger than initially drafted

This is a real regime with **rigorous, proof-shaped support**, not just qualitative fading-memory language:
- **Reservoir computing / echo-state / liquid-state machines** — Maass, Natschläger & Markram 2002 (*Neural
  Computation*, "Real-time computing without stable states") define fading memory + the **separation property**:
  a nonlinear reservoir's high-dimensional trajectory separates distinct input histories into linearly-readable
  classes that a simple leaky integrator cannot. White, Lee & Sompolinsky 2004 (*PRL*) and Jaeger's echo-state
  work establish a formal **linear memory-capacity bound** (Σ MC_k ≤ N): a linear/leaky accumulator can only
  reconstruct linear projections of the past and is *provably* unable to compute nonlinear, order-dependent
  functions of multiple time-lags (e.g. an XOR-type function of inputs at t-1 and t-3). Dambre, Verstraeten,
  Schrauwen & Massar 2012 (*Sci Rep*, "Information Processing Capacity of Dynamical Systems") formalize the
  **memory–nonlinearity trade-off**: nonlinear dynamics necessarily trades away some pure linear memory to open
  capacity for history-order-dependent functions no linear accumulator can reach. Butcher et al. 2013 (*Sci Rep*)
  show mixed linear+nonlinear reservoirs beat either pure regime — direct evidence nonlinear trajectory shape
  carries information a flat sum structurally lacks.
- **Short-term synaptic plasticity** — Tsodyks & Markram 1997 (*PNAS*); Abbott & Regehr 2004 (*Nature*, "Synaptic
  computation"); Buonomano & Maass 2009 (*Nat Rev Neurosci*, "State-dependent computations") frame
  facilitation-then-depression as a history-dependent nonlinear filter: the same average spike rate delivered in
  different temporal orders produces different postsynaptic trajectories, explicitly used by cortex for temporal
  pattern/sequence discrimination.
- **Non-monotonic memory-strength curves** — Ritvo et al. 2019 (*Trends Cogn Sci*, "Nonmonotonic Plasticity: How
  Memory Retrieval Drives Learning", the NMPH): a U-shaped plasticity curve where the *same* total activation
  produces opposite outcomes (weakening/differentiation vs. strengthening/integration) depending on WHERE the
  trajectory sits on the curve — shape, not integrated magnitude, determines later retrievability.
- **Delay-embedding / Takens framing** — a 2024 arXiv paper ("Delay Embedding Theory of Neural Sequence Models")
  shows trajectory/delay-embedding preserves the dimensionality needed to reconstruct temporal order; a scalar
  linear accumulator is rank-1 and structurally cannot meet the embedding-dimension requirement needed to
  disambiguate distinct temporal orders that map to the same integral.

**Implication (now higher-confidence):** the memory-capacity theorems (White/Lee/Sompolinsky; Dambre et al.) are
not just suggestive — they are structural proofs that a flat linear accumulator is blind to certain
order-dependent information by construction, regardless of tuning. The original test (a single accruing signal
collapsing to one decision) is not an order/sequence-discrimination task, so it could not have exercised this
advantage even though the advantage demonstrably exists elsewhere. If the substrate's downstream requirement
(relational/compositional reasoning over multiple events, per the standing program spine) ever needs "did A
happen before B" or sequence reconstruction, trajectory coding is a live, well-supported candidate again — this
is NOT the same claim as "hold-structure helps single-stream accuracy," which the current finding correctly
refutes.

## Cross-thread synthesis

- Aligns with and sharpens the standing efficiency premise (brain = near-optimal EFFICIENCY, not near-optimal
  accuracy-in-a-vacuum): efficiency claims are meaningless without a cost axis, and this drill shows the brain
  literature itself keeps cost and accuracy as separate, only-sometimes-overlapping ledgers. An accuracy-only
  arena is structurally the wrong instrument for validating an efficiency claim — this generalizes beyond
  consolidation to any other "brain-faithful mechanism produces no accuracy delta" result the program hits.
- Connects to the SCALE REFRAME thread (07-15, fair-test refute): that thread asked whether reasoning is
  gated on grounded-data scale; this drill adds a parallel caution — some negatives may be **currency-scope**
  mismatches (wrong thing being priced) rather than **scale** mismatches (not enough data). Both are "test design
  didn't match the mechanism's actual claim," which is becoming a recurring diagnostic pattern this program should
  name explicitly: before accepting a brain-faithful-mechanism-adds-nothing result, ask (a) does this test present
  the interference/competition regime the mechanism defends against, and (b) does this test price the resource
  the mechanism economizes.
- Direct precedent for the "brain-check every negative" standing discipline (07-15): this IS that check, applied
  to the hold-vs-flat-accumulation finding, and the answer is "the brain solves a related-but-different problem
  with this mechanism (interference across items / resource rationing), not the problem the test posed
  (accuracy of temporal integration within one item)."

## Substrate-product implications

1. **Frontier-2 is justified AS SCOPED, not as a general verdict on brain-faithful consolidation.** For
   single-stream temporal-evidence-integration tasks, adopt flat accumulation + temporal integration and drop the
   elaborate hold — the accuracy win is fully explained by "using the time axis," and the extra structure has
   shown zero payoff in the only currency (accuracy) this test measured, honestly.
2. **Do not generalize this to "CLS/STC-style machinery is dead weight for this substrate."** The interference
   axis (multiple competing items/tasks) and the capacity-priced axis (finite storage/write budget) are both
   untested and both have strong literature reasons to expect a real payoff there. If/when the foundation-builder
   needs multi-item continual learning (which the standing program spine says it will — relational reasoning over
   many stored facts, ingest-gate work, catastrophic-forgetting concerns already logged elsewhere), CLS-style
   hold-then-consolidate is the load-bearing candidate, and should be re-tested THERE, not re-litigated on the
   single-stream task.
3. **If the foundation-builder's evaluation harness is ever used to justify a capacity/efficiency claim (not just
   an accuracy claim), it needs an explicit capacity/write-budget currency as a first-class metric** — accuracy-
   per-unit-capacity-committed, not accuracy alone. Absent that axis, any future "brain-faithful mechanism doesn't
   help" result involving a resource-economizing mechanism (STC-like selectivity, SHY-like downscaling, sparse
   ingest-gating) will be similarly unfalsifiable in the wrong direction — it will look like a negative when it
   may just be an unpriced positive.
4. **Concretely for the next experiment cycle (not a design, just an anchor candidate):** re-run the existing
   hold-vs-flat-accumulate comparison unchanged except for (a) two sequential competing evidence streams instead
   of one (interference axis) and (b) a capped consolidation-write budget with accuracy-per-write reported
   (capacity axis). This reuses the existing harness with two orthogonal, cheap modifications rather than a new
   build.

## Citations (verified by 4 live Sonnet lit-scan sub-agents, 2026-07-15/16)

- Attwell D & Laughlin SB (2001). *An energy budget for signaling in the grey matter of the brain.* J Cereb
  Blood Flow Metab. (AP ~47%, postsynaptic ~34%, resting ~13%, presynaptic ~3% of budget.)
- Harris JJ & Attwell D (2012). *Synaptic Energy Use and Supply.* Neuron. (mammalian-AP-cost update.)
- Engl E & Attwell D (2015). *Non-signalling energy use in the brain.* J Physiol.
- *Metabolic constraints on synaptic learning and memory* (2019/2020, J Neurophysiol) — plasticity ~4-11% of fast
  excitatory budget.
- arXiv 2301.09565 — *Estimating the energy requirements for long-term memory formation* (~10 mJ/bit cross-species
  estimate; Drosophila lifespan-cost data; explicit caveat that the "why" of the cost is not established).
- PMC6256250 — metabolic-energy constraint on synapse count (derives a hard connectivity ceiling).
- Chklovskii DB & Stevens CF — cortical wiring-optimization / conservation-of-wiring literature.
- McClelland JL, McNaughton BL, O'Reilly RC (1995). *Why there are complementary learning systems in the
  hippocampus and neocortex.* Psychol Rev. McClelland (2013), Psychol Rev, schema-consistent fast cortical
  learning update.
- McCloskey M & Cohen NJ (1989). *Catastrophic interference in connectionist networks.* Psychology of Learning
  and Motivation.
- Frey U & Morris RGM (1997). *Synaptic tagging and long-term potentiation.* Nature.
- Redondo RL & Morris RGM (2011). *Making memories last: the synaptic tagging and capture hypothesis.* Nat Rev
  Neurosci.
- Fonseca R et al. (2004). *Competing for memory: hippocampal LTP under regimes of reduced protein synthesis.*
  Neuron. (PRP competition — the capacity-competition finding, secondary to STC's founding specificity rationale.)
- Richards BA & Frankland PW (2017). *The Persistence and Transience of Memory.* Neuron. (Direct quote used above:
  "the goal of memory is to optimize decision-making," not raw information transmission.)
- Tononi G & Cirelli C — synaptic homeostasis hypothesis, *Sleep Med Rev* 2006; *Neuron* 2014 "Sleep and the
  Price of Plasticity."
- Ronald Davis lab — Drosophila active forgetting, dopamine→Rac1/Cofilin; *Neuron* 2017 "The Biology of
  Forgetting"; PNAS 2022 dopamine-circuit follow-up.
- Mattar MG & Daw ND (2018). Nat Neurosci — prioritized replay as reward/utility-maximizing (RL-replay analogy).
- Tsodyks MV & Markram H (1997). PNAS — facilitation-depression synaptic model.
- Abbott LF & Regehr WG (2004). *Synaptic computation.* Nature.
- Buonomano DV & Maass W (2009). *State-dependent computations: spatiotemporal processing in cortical networks.*
  Nat Rev Neurosci.
- Maass W, Natschläger T, Markram H (2002). *Real-time computing without stable states.* Neural Computation.
- White OL, Lee DD, Sompolinsky H (2004). PRL — linear memory-capacity bound for recurrent networks.
- Dambre J, Verstraeten D, Schrauwen B, Massar S (2012). *Information Processing Capacity of Dynamical Systems.*
  Sci Rep.
- Butcher JB et al. (2013). *Reservoir Computing Beyond Memory-Nonlinearity Trade-off.* Sci Rep.
- Ritvo VJH et al. (2019). *Nonmonotonic Plasticity: How Memory Retrieval Drives Learning.* Trends Cogn Sci.
- arXiv 2406.11993 — *Delay Embedding Theory of Neural Sequence Models* (2024).

Verified count: **~24 sources, independently confirmed live by 4 parallel Sonnet lit-scan sub-agents** (as
opposed to the first-draft version of this note, which relied on unverified recall). All four sub-agents returned
qualitative confidence of moderate-to-high on their respective sub-questions; no sub-agent reported an inability
to find supporting literature. One correction from verification: the initial draft characterized STC's capture
selectivity as founded on a resource-scarcity argument — verification shows the founding rationale is
specificity/accuracy (correct synapse-to-event assignment), with resource competition (Fonseca et al. 2004) a
real but secondary, later-discovered layer. This has been corrected above.

## Deflated P

Per lit-scan calibration penalty ([[feedback-lit-scan-calibration-penalty]]): with live verification now landed
across all four angles, confidence in the underlying literature claims themselves is high (~0.80) — CLS's
pure-accuracy rationale and the reservoir-computing memory-capacity theorems are both about as rigorously
supported as this kind of cross-domain claim gets. The residual uncertainty is entirely in the SYNTHESIS — mapping
these three disentangled mechanisms onto this specific substrate finding, and specifically the claim that the
single-stream test structurally cannot exercise CLS's or STC's home-field advantage. That mapping is plausible and
now well-grounded, but untested against the proposed cheap decisive test (interference axis / capacity-priced
axis) above. Deflating 0.20-0.25 for calibration and applying the hard novel-synthesis cap:

**P_deflated = 0.50** (hard novel-synthesis cap; the literature-grounding itself would support higher, but the cap
applies regardless per [[feedback-lit-scan-calibration-penalty]] until the proposed decisive test is actually
run).
