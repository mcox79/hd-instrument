# Research: combiner robustness to IMPERFECT (incomplete/noisy) retrieved facts -- biology synthesis + can-fail cell design

Date: 2026-07-24. Trigger: VET'd finding that bind+settle CI combination scores 0.690 on ARC-Challenge given GOLD facts
but only 0.341 on the best real retrieved+selected pool (task-supplied, referenced as "29541 VET" -- **flagged: I did
not independently re-locate this exact atom/number on disk this session; grep for "29541" and "0.341" across
notes/ and data/substrate_index/ returned no hits from this session's cwd. Treat the 0.690/0.341 figures as
Director-supplied, not disk-re-verified by me, per the caveat-interpretation discipline.** Retrieval recall is
independently documented as capped (~0.38-0.50 miss rate) in `notes/research_arc_retrieval_biology_and_design_2026-07-24.md`
(29537/af29a98ef), so the premise that retrieval will never reach gold-completeness is well-grounded even without
re-verifying the exact 29541 number.

Method: KB-check first (7 same-day 07-24 notes read end-to-end: brain_qa_architecture_completeness, bindsettle_ci_settle_dynamics,
contradiction_representation_and_settle_dynamics, multihop_reasoning_layer_biology_and_design_sketch, arc_retrieval_biology_and_design,
plus the 07-21 metacognitive-calibration drill) + 3 parallel Sonnet lit-scans (axis 1: PCS/CI robustness to incomplete evidence +
metacognitive escalation; axis 2: schema/frame gap-filling; axis 3: hippocampal on-the-fly bridging + Gentner structure-mapping).
Lit-scan calibration penalty applied throughout (deflate 0.15-0.25; novel-synthesis capped <=0.50).

**Explicitly NOT this drill's territory (already answered, build-on not re-derive):** CI's signed-matrix settle mechanics,
epsilon/iteration-budget, Cowan-4 buffer-carryover, choice-choice mutual inhibition (`research_bindsettle_ci_settle_dynamics...`);
how contradiction/polarity edges get their SIGN (`research_contradiction_representation_and_settle_dynamics...`); multi-hop
task-SHAPE classification and khop.py's production validation on FB15K/WebQSP/CWQ (`research_multihop_reasoning_layer_biology...`);
retrieval-mechanism redesign itself, PPR/spreading-activation (`research_arc_retrieval_biology_and_design...`). This drill's
territory is narrower and different: **given retrieval will structurally never reach gold-completeness, how must the
COMBINER stage reason robustly around that fact** -- gap-filling, bridging, and confidence-gated escalation as three
candidate robustness mechanisms, evaluated against what the literature actually supports (and does NOT support).

---

## HEADLINE

**Three converging, independently-sourced findings reframe the 0.690->0.341 gap as a MISSING ROBUSTNESS LAYER, not a
combiner-mechanism defect -- but the literature is equally clear that the two most obvious fixes (schema gap-filling,
on-the-fly bridging) are NOT free wins; each has a specific, well-documented failure mode that must be engineered
around, not assumed away.**

1. **Coherence/PCS-style settling (Kintsch CI, Thagard ECHO) degrades BRITTLY, not gracefully, near a competing-hypothesis
   threshold** -- the best available evidence (Hopfield basin-of-attraction theory as the formal analog, Thagard &amp;
   Verbeurgt's own NP-hardness/approximation caveat, one contested coherence-filtering preprint showing a noise-vs-prior
   crossover) points to a snap-to-wrong-attractor failure mode once supporting evidence drops below a critical mass,
   not a smooth accuracy decline proportional to missingness. This is an INFERENCE from adjacent literature (flagged,
   not a dedicated missing-evidence sweep on CI/ECHO itself) but it is the most coherent read across three independent
   angles. **Practical reading: our observed 0.690->0.341 collapse (49-point drop, not a modest few points) is exactly
   the SHAPE this literature predicts for evidence dropping below basin-boundary, not evidence of a broken settle.**

2. **Schema/frame gap-filling (Bartlett 1932 -> Rumelhart 1980/Minsky 1975 -> Schank &amp; Abelson 1977 scripts -> PDP
   settling networks, Rumelhart/Smolensky/McClelland/Hinton 1986) is a strongly validated, cross-paradigm-replicated
   mechanism for substituting a plausible value for a missing fact -- but the literature is unambiguous that classical
   gap-filling does NOT come with a native confidence discount.** Bower, Black &amp; Turner (1979): subjects falsely
   "recognize" unstated-but-script-typical events with HIGH confidence, indistinguishable from true memory. DRM
   paradigm: false recall of the unpresented associate carries "remember," not "know," judgments. Minsky's own frames:
   once a default is instantiated it "is taken to be the slot filler" identically to an explicit value -- nothing in
   the base mechanism marks it as less certain. **This is the single most load-bearing finding for our design: naive
   gap-filling would make the combiner MORE confidently wrong, not more robust, unless we explicitly engineer a
   confidence discount that the biology itself does not supply for free** (the literature's own fix for this,
   non-monotonic/default logic's defeasibility marking and truth-maintenance-system provenance tracking, is a
   BOLT-ON layer, not intrinsic to schema completion).

3. **On-the-fly bridging of two independently-retrieved, never-before-combined facts IS a genuine, multiply-replicated
   hippocampal mechanism (REMERGE-family models; RT/accuracy signatures: near-chance-then-rising accuracy across
   repeated test trials, monotonically increasing RT from direct to inferred judgments, BC-source-memory at chance
   while AC-inference succeeds) -- this directly validates that `substrate/khop.py`'s bridging capability is
   biologically well-grounded as a recovery mechanism for a missing single fact, not a hopeful engineering analogy.**
   But it is NOT free: every study demonstrating it also shows a real cost (chance-level accuracy until practiced,
   large RT penalty), and critically, **the literature only demonstrates bridging over two INTACT, cleanly-retrieved
   premises** -- there is no evidence it works, or even any documented attempt to test whether it works, when one of
   the two bridging premises is itself noisy/degraded. Gentner-style structure-mapping (SME) is well-established to
   prefer relational-structure matches over surface-feature lures and is CONSTRUCTED to operate on whatever partial
   relational structure is supplied (graceful-by-design), but no quantitative robustness curve exists for how much
   structure can be missing before it fails -- this specific claim is a reasonable extrapolation from the theory's
   architecture, not a cited empirical result.

**Net design verdict: the fix is a confidence-gated, bounded ITERATIVE escalation loop wrapped around the existing
(unchanged) CI settle -- not a smarter single-shot combiner and not unlimited iteration.** The trigger/gating half of
this (Nelson &amp; Narens monitor-control, Koriat feeling-of-knowing-gated search, Shenhav/Botvinick/Cohen Expected
Value of Control, SAM/REM bounded-search stopping rules) is the MOST strongly evidenced piece of the whole synthesis
-- strong, multiply-converging, real brain mechanism, not a plausible-but-undocumented engineering idea. This is
exactly the trustworthy-reader gate (29465) and khop.py's job, both already built and both currently UNWIRED to any
downstream action.

P_deflated: **0.32** (see Calibration; this is the most novel-synthesis-heavy of the four 07-24 combiner-adjacent
drills, because it proposes wiring THREE previously-separate, previously-unwired pieces -- confidence gate, schema
gap-fill-with-discount, khop bridging -- into one loop that has not been tested even piecewise on real ARC data).

---

## Biology synthesis (per sub-question, cross-checked across 3 lit-scans)

### Q1. CI/PCS robustness under incomplete evidence -- BRITTLE, not graceful (inferred, flagged)

Thagard's ECHO (1989 *BBS*; Thagard &amp; Verbeurgt 1998 *Cognitive Science*, "Coherence as Constraint Satisfaction")
settles a signed evidence/hypothesis network via connectionist relaxation, formally shown to be an NP-hard
optimization approximated by the settle dynamics -- meaning near-tied competing hypotheses are exactly where the
approximate relaxation is least guaranteed to find the true coherence optimum, and small perturbations (missing
support, noise) can flip which attractor wins. A single (unreplicated, preprint) coherence-filtering paper
("Coherence as a Constraint on Scientific Inquiry," philsci-archive) reports a noise-vs-prior CROSSOVER: coherence
filtering helps when noise is high/priors good, hurts when noise is low/priors poor -- i.e., the response to
missing/noisy evidence is CONDITIONAL, not uniformly graceful. Classical Hopfield associative-memory theory (the
best-characterized formal analog, same iterative signed-relaxation family) shows retrieval accuracy from a partial
cue is near-perfect WITHIN a stored pattern's basin of attraction, then discontinuously snaps to a DIFFERENT
attractor once the missing/corrupted fraction crosses a critical Hamming-distance radius -- graceful-then-brittle,
with the brittle transition being the operative failure mode near the boundary. Kintsch's own CI literature
emphasizes robustness to NOISE (over-generate propositions, prune via settling) but does not address MISSING
propositions directly -- this is a genuine literature gap, not a resolved question, and should be reported as such.

### Q2. Metacognitive control of continued search -- strong, well-established, directly on-point

Nelson &amp; Narens (1990) formalize the monitor (feeling-of-knowing/accessibility) -> control (continue/redirect/stop)
loop as dissociable stages. Koriat's accessibility hypothesis (1993, 2008) adds a two-stage gate: cheap familiarity
check first, effortful accessibility search only if familiarity clears a threshold. Shenhav, Botvinick &amp; Cohen
(2013, *Neuron*, Expected Value of Control) formalize a cost/benefit computation over further deliberation/retrieval
as the normative basis for continuing vs. stopping. SAM (Raaijmakers &amp; Shiffrin 1980/81) and REM (Shiffrin &amp;
Steyvers 1997) formalize free recall as repeated probabilistic sampling that TERMINATES after a run of consecutive
retrieval failures -- an explicit, well-established bounded-search stopping rule. **This is the strongest, least
speculative leg of the whole synthesis: an iterative, confidence/cost-gated retrieve-evaluate-continue-or-stop
architecture is real and multiply evidenced, not a single-shot combine-whatever-was-retrieved architecture.**

### Q3. Schema/frame gap-filling -- validated mechanism, NO native confidence discount (the load-bearing finding)

Bartlett (1932): "effort after meaning" substitutes schema-typical content for unfamiliar/missing material (canoes
became boats in "The War of the Ghosts"); the empirical signature distinguishing genuine gap-fill from accurate
retrieval is systematic INTRUSION of schema-typical-but-never-presented detail, well-replicated across decades.
Rumelhart (1980) and Minsky (1975): schemas/frames have slots with default values, substituted "in the absence of
explicit information to the contrary" -- a pure presence/absence rule, no probabilistic/confidence gradient in the
base formalism. Schank &amp; Abelson (1977) scripts, tested directly by Bower, Black &amp; Turner (1979, *Cognitive
Psychology*): subjects falsely recognize unstated-but-script-typical sub-events at rates far above chance, WITH HIGH
CONFIDENCE ratings indistinguishable from true recognition -- and the effect scales with how strongly the schema is
activated, consistent with an automatic/activation-driven mechanism, not purely deliberate strategy. DRM false-memory
paradigm (Roediger &amp; McDermott 1995) gives the same signature at the lexical-associate level: false recall of an
unpresented but semantically-implied item carries "remember" (not merely "know") judgments. Rumelhart, Smolensky,
McClelland &amp; Hinton (1986, PDP Vol. 2 Ch. 14) show schema completion emerging from pure constraint-satisfaction
settling (their room-schema simulation: clamp a few units, network settles to a full filled-in interpretation) --
the connectionist-level version of the SAME finding: once settled, filled and given units share the SAME activation
currency, with no intrinsic tag distinguishing "clamped/retrieved" from "inferred/defaulted." **Where a confidence
discount DOES exist in this literature, it is bolted on afterward by a separate mechanism** (Reiter's default logic
defeasibility marking, truth-maintenance-system provenance tracking) -- never intrinsic to the completion mechanism
itself. This is the single most decisive, least equivocal finding across all three lit-scans.

### Q4/Q3(task). Hippocampal bridging + Gentner structure-mapping -- on-the-fly bridging is real but costly and premise-intact-only

Two co-existing, both well-replicated hippocampal mechanisms exist: (A) encoding-time integration (Zeithamova,
Dominick &amp; Preston 2012; Preston &amp; Eichenbaum 2013) -- overlapping pairs get fused into one engram DURING learning,
so by test time the "inference" is really a lookup of a pre-built representation; (B) retrieval-time recombination
(Kumaran &amp; McClelland's REMERGE model; a 2023 acquired-equivalence study explicitly framed as "retrieval-based
inference," frontiersin.org 10.3389/fcogn.2023.1326191) -- associations stay SEPARATE (pattern-separated), and
inference is computed on-demand via "recursive retrieval of individual trained associations," recombined for the
first time at query time. Evidence FOR (B) being genuinely on-the-fly, not just theoretical: accuracy starts near
chance on the first inferred (AC) test trial and rises only across repeated testing (inconsistent with a
pre-existing cached answer); RT scales up monotonically from direct to inferred judgments (2.80s -> 3.55s -> 4.70s
in one dataset); BC-source memory can sit at chance even while AC-inference succeeds (the bridge is built
transiently, not stored). **HONEST caveat, load-bearing for our design**: every demonstration of on-the-fly bridging
uses two CLEANLY, INTACTLY retrieved premises -- no study was found testing (or even attempting) bridging when one
premise itself is noisy or degraded. This maps onto our task fairly precisely (combine two facts that WERE
retrieved) but does NOT license assuming bridging rescues a case where retrieval itself was poor quality on the
premises it did return. What triggers an ATTEMPT at bridging (vs. giving up) is the thinnest-evidenced part of the
whole synthesis -- one low-confidence finding (unconscious/automatic relational inference, J. Neurosci. 32:6138,
index-only, not independently verified) actually cuts AGAINST a metacognitively-gated trigger, suggesting some
inference may be obligatory/automatic rather than effort-gated; treat any claim that gap-detection specifically
triggers bridging-search as a design choice, not an established finding, per this drill's honest read.

Gentner's structure-mapping (1983; Falkenhainer, Forbus &amp; Gentner 1989, SME; Clement &amp; Gentner 1991 systematicity)
is well-established and, critically, CONSTRUCTED to operate on whatever relational predicates are supplied -- it
computes the best structurally-consistent mapping over available structure and ranks by a systematicity score,
rather than requiring a complete relational description before producing an answer. This is graceful-degradation-by-
architecture, and behavioral studies confirm partial-but-structurally-aligned matches beat larger surface-feature-
overlap matches. No quantitative noise/incompleteness-tolerance curve for SME itself was found -- treat the
"degrades gracefully" claim as a reasonable extrapolation from the algorithm's design, not a cited empirical result.
**No direct literature link exists between the hippocampal-bridging literature and Gentner's structure-mapping
literature** -- the closest genuine convergence is the Tolman-Eichenbaum Machine (Whittington et al. 2020, *Cell*)
reframing hippocampal generalization as structural abstraction over a relational code, using Gentner-adjacent
vocabulary without citing Gentner directly. Flagged explicitly: any claim that these are "the same computation at
different scales" is this drill's own synthesis-level inference, not a documented finding in either literature.

---

## Cheap decisive test (can-fail cell design -- NOT dispatched, per task instruction)

**Candidate anchor name:** `arc_combiner_confidence_gated_escalation_v1`

Hold the existing CI settle (bind+settle, already VET'd) COMPLETELY FIXED. The one variable is what happens BEFORE
and AROUND it: a bounded escalation loop wrapping the same settle call. Run on the SAME real (non-oracle) retrieved
pools already used to measure the 0.341 baseline (per the task-supplied number; re-locate and re-verify this exact
condition/harness before building, since I could not confirm it on disk this session).

**Arms (one loop-design variable each; settle mechanics unchanged across all arms):**
- A. `baseline_single_shot` -- current behavior: retrieve once, settle once, answer (no gating, no bridge, no gap-fill). This IS the 0.341 condition, re-run for a same-seed baseline.
- B. `confidence_gate_abstain_only` -- run the settle once; if choice-vs-choice margin is below a pre-registered threshold tau, ABSTAIN instead of answering (no bridging, no gap-fill). Isolates the pure VALUE of knowing-when-not-to-guess (Nelson-Narens/Koriat/EVC leg alone).
- C. `bridge_on_gap` -- on a low-margin trigger, attempt ONE khop.py bridging pass: if two retrieved (already-in-pool, not re-retrieved) facts can be composed via a typed relation into a new fact relevant to a currently-unsupported choice, add it and re-settle ONCE (bounded, not iterated further). Requires BOTH bridging premises to already be in the retrieved pool (per Q4's honest caveat -- do not test bridging over a re-retrieved, potentially-noisy premise in this first cell).
- D. `gap_fill_discounted` -- on a low-margin trigger, identify an empty schema slot implied by the question's relation-type (reuse the WorldTree IFTHEN/COUPLEDRELATIONSHIP typing already surfaced in `research_contradiction_representation_and_settle_dynamics...`), fill it with a schema-typical default, but inject it into the settle graph with an EXPLICIT, LOWER initial activation weight than a retrieved fact (the confidence discount the literature says the base mechanism does NOT supply for free -- must be engineered in).
- E. `gap_fill_undiscounted` (must-fail control) -- identical to D but the filled slot gets the SAME initial activation as a retrieved fact (mimics the naive/classical schema-completion failure mode the literature warns about). **Prediction: E should show MORE confident-wrong errors than D** -- this is the single cleanest test of whether the "discount matters" claim (this drill's most load-bearing finding) is actually load-bearing for this task, not assumed.
- F. `bridge_random_pair` (must-fail control) -- same as C but composes a RANDOM pair of in-pool facts instead of a khop-typed-relation pair. Must NOT beat baseline A -- validates that any lift from C comes from genuine relational bridging, not just "adding a second fact to the pool helps regardless of relation."
- G. `combined_gate_bridge_gapfill` -- the full loop: gate first (B), attempt bridge if premises available (C), else discounted gap-fill (D), else abstain. Bounded to ONE escalation attempt total (per SAM/REM bounded-search precedent -- do not iterate unboundedly).

**Primary metrics (per arm):** accuracy-when-answered (excludes abstentions), coverage (fraction answered vs. abstained),
and a joint "risk-adjusted" score (accuracy-when-answered x coverage, penalizing a gate that abstains its way to a
trivially high accuracy on a tiny n). Report Easy and Challenge separately.

**Secondary metric:** confident-wrong-error RATE specifically (answered-and-wrong instances where the settle's own
margin was ABOVE the confidence threshold) -- this is the metric that directly tests the schema-gap-fill risk this
drill's biology flags as the central danger.

## Falsifiable predictions

**HARD-PASS (all must hold, pre-registered before results):**
1. Arm G (combined loop) beats arm A (baseline_single_shot) on the risk-adjusted score by a pre-registered margin
   (>=5 points) on BOTH Easy and Challenge, replicated across >=2 seeds.
2. Arm D (discounted gap-fill) shows a LOWER confident-wrong-error rate than arm E (undiscounted gap-fill) by a
   non-trivial margin -- directly confirms the literature's single most load-bearing finding (defaults need an
   explicit confidence discount the base mechanism does not supply) is actually load-bearing for THIS task.
3. Arm C (khop-typed bridging) beats arm F (random-pair bridging) by a non-trivial margin -- confirms genuine
   relational structure, not mere pool-size increase, drives any bridging lift.
4. Arm B (abstain-only) shows accuracy-when-answered meaningfully ABOVE the 0.341 baseline (i.e., the margin
   threshold correctly identifies genuinely-low-confidence cases that would otherwise be wrong) while coverage
   does not collapse to a vacuously small n (report the actual coverage number, do not hide behind a tiny-n high
   accuracy).

**HARD-FAIL (any one sufficient to refute the corresponding piece of the design, though other pieces may still stand):**
1. Arm G does not beat arm A -- the whole escalation-loop framing adds nothing measurable; report honestly, the
   0.690->0.341 gap is not addressable by this class of mechanism at all (would redirect all future effort to
   retrieval-quality improvement alone, per `research_arc_retrieval_biology_and_design...`'s own recommendation).
2. Arm D does not beat arm E (confidence-discount ablation) -- the discount claim, despite being this drill's most
   confident biological reading, does not transfer to this task; report as a genuine, informative negative (the
   base undiscounted mechanism may simply not fire often enough for the discount to matter, a coverage problem
   distinct from a mechanism refutation -- check fire-rate before concluding refutation).
3. Arm C does not beat arm F -- bridging lift (if any) is not coming from genuine relational structure; treat
   khop.py as not load-bearing for THIS specific gap, independent of its already-proven production validation
   elsewhere (FB15K/WebQSP/CWQ), since this cell tests a DIFFERENT regime (bridging two already-retrieved facts,
   not directed multi-hop traversal over a large graph).
4. Arm B's coverage collapses below a pre-registered floor (e.g. <30% of items answered) while accuracy-when-
   answered looks good -- a real risk given Q1's brittle-threshold-degradation prediction (many real-pool items
   may sit close to the boundary, triggering abstention on a large fraction) -- report honestly as "correctly
   conservative but not yet useful," not as a pass.

**P estimates (calibration-penalty applied, deflated 0.15-0.25, novel-synthesis capped at 0.50):**
- P(arm G beats arm A on risk-adjusted score, HARD-PASS 1) = **0.30** (deflated from a naive ~0.50-0.55; this wires
  THREE previously-unwired pieces together for the first time on real data, and Q1's own brittle-threshold finding
  means a meaningful fraction of real-pool items may simply be past the point of recovery regardless of loop design).
- P(discount ablation D>E confirms, HARD-PASS 2) = **0.35** (the biological finding itself is high-confidence, ~0.85
  raw, but whether it's MEASURABLE on ARC's specific fact/slot structure at achievable fire-rates is novel synthesis).
- P(bridging C>F confirms, HARD-PASS 3) = **0.40** (khop.py itself is already production-validated elsewhere, lower
  novel-synthesis risk for the mechanism per se; risk here is mainly whether qualifying bridgeable pairs are common
  enough in the real retrieved pools to matter at all).
- P(HARD-FAIL 1, whole framing adds nothing) = 0.30.
- P(MIDDLE-BAND: some arms pass, some fail, most likely outcome per calibration discipline) = 0.40.

## Cross-thread synthesis

- **Directly reframes the diagnosis in `notes/research_arc_retrieval_biology_and_design_2026-07-24.md`.** That note
  correctly identified retrieval as the dominant wall (~47-50% of misses) and proposed a retrieval-quality fix
  (multi-cue PPR/spreading activation). This drill's contribution is orthogonal and complementary, not competing:
  EVEN IF retrieval improves per that design, recall will structurally never reach 1.0 (no retrieval mechanism is
  perfect), so the combiner-robustness question this drill answers remains load-bearing regardless of how far
  retrieval improves -- the two workstreams should proceed in parallel, not sequentially gated on each other.
- **Directly builds on `notes/research_bindsettle_ci_settle_dynamics_multifact_aggregation_2026-07-24.md`** (settle
  mechanics, held fixed here as the one-variable discipline requires) and
  `notes/research_contradiction_representation_and_settle_dynamics_2026-07-24.md` (WorldTree relation-typing as the
  schema-slot source for arm D/E's gap-fill trigger, reused not re-derived).
- **Directly activates two previously-unwired built primitives**: `substrate/khop.py` (validated per
  `notes/research_multihop_reasoning_layer_biology_and_design_sketch_2026-07-24.md` on FB15K/WebQSP/CWQ, but never
  wired to the ARC aggregation pipeline) and the trustworthy-reader confidence/conflict gate, 29465 (referenced by
  the task; **flagged, per the contradiction-representation note's own honest caveat, that this atom was not
  independently re-located on disk this session either -- re-locate and confirm its actual signal/API before
  building arm B/G, do not assume its interface from description alone**).
- **Extends `notes/research_drill_metacognitive_calibration_escalation_trigger_2026-07-21.md`'s bifurcated
  monitoring design** (ACC-conflict-flag + parietal signal-strength/margin, both needed, neither sufficient alone)
  from the READER's oracle-escalation context to the COMBINER's bridge/gap-fill/abstain decision -- same underlying
  brain mechanism (Nelson-Narens monitor-control), new application site.
- **New finding not in any prior 07-24 note**: the specific, decisive risk that naive schema/gap-filling produces
  CONFIDENTLY WRONG answers (not merely unhelpful ones) unless explicitly discounted -- this is a genuinely new
  caution this codebase's prior combiner-design notes (bindsettle, contradiction-representation) did not surface,
  because those notes focused on facts that WERE present (contradiction-aware weighting of retrieved evidence), not
  on facts that are ABSENT entirely and might be synthetically supplied.

## Substrate-product implications

If the HARD-PASS predictions clear (even partially, e.g. arms B+D+ pass while C is inconclusive), the product claim
sharpens meaningfully beyond "we retrieve and combine facts": **"the substrate knows when its evidence is
insufficient and either fills the gap with an explicitly-flagged, lower-confidence inference (never silently, never
at full confidence) or honestly declines to answer rather than confidently guessing wrong -- a materially different,
auditable failure mode than a black-box system that always outputs an answer with no visibility into whether it was
confident or coerced."** This is a genuine glass-box differentiator: every abstention, every gap-fill, every bridge
step is inspectable (khop.py's Merkle audit chain, already built, directly reusable for this purpose) -- competitors
using opaque retrieval-augmented generation cannot cheaply retrofit "I made this part up and flagged it as such" as
an auditable property. If HARD-FAIL 1 lands (whole framing adds nothing), the honest, still-valuable product
takeaway is that retrieval quality is the ENTIRE lever and combiner-side robustness work should stop here --
directing 100% of future investment to `research_arc_retrieval_biology_and_design`'s retrieval redesign instead.

## Citations (verified count: approximately 35 distinct external sources across 3 lit-scans, cross-checked for
primary-vs-secondary/flagged status; 6 internal cross-thread notes)

**PCS/CI robustness + metacognitive escalation:** Thagard (1989, *Behavioral and Brain Sciences*, "Explanatory
Coherence"); Thagard &amp; Verbeurgt (1998, *Cognitive Science*, "Coherence as Constraint Satisfaction"); "Coherence
as a Constraint on Scientific Inquiry" (philsci-archive preprint, flagged unreplicated/contested); Kintsch (1988,
*Psychological Review*, CI, already primary-source-verified in a prior 07-24 drill); Hopfield (1982) and standard
basin-of-attraction treatments (flagged as background analog, not a CI/ECHO-specific study); Nelson &amp; Narens (1990,
metamemory monitor-control framework); Koriat (1993 *Psych Review*, 2008 accessibility/cue-familiarity); Shenhav,
Botvinick &amp; Cohen (2013, *Neuron*, Expected Value of Control); Raaijmakers &amp; Shiffrin (1980/81, SAM); Shiffrin &amp;
Steyvers (1997, REM); Harbison, Dougherty et al. (2010, *Cognition*, memory-search termination, secondary-sourced).

**Schema/frame gap-filling:** Bartlett (1932, *Remembering*); Rumelhart (1980, "Schemata: The Building Blocks of
Cognition"); Minsky (1975, "A Framework for Representing Knowledge"); Reiter (default logic, defeasibility, via
standard reference); Bower, Black &amp; Turner (1979, *Cognitive Psychology*, script false-recognition, primary PDF
verified); Roediger &amp; McDermott (1995, DRM paradigm); Rumelhart, Smolensky, McClelland &amp; Hinton (1986, PDP Vol. 2
Ch. 14, room-schema settling simulation, primary PDF verified).

**Hippocampal bridging + structure-mapping:** Zeithamova, Dominick &amp; Preston (2012, *Frontiers in Human
Neuroscience*, encoding-time integration); Preston &amp; Eichenbaum (2013, *Current Biology*, review); Kumaran &amp;
McClelland (REMERGE, cited via 2023 acquired-equivalence follow-up, frontiersin.org 10.3389/fcogn.2023.1326191,
primary-adjacent); a 2013-era retrieval-based-inference RT/accuracy study (PMC4980665); "unconscious relational
inference" (*J. Neurosci.* 32:6138, flagged index-only/low-confidence, not independently full-text-verified);
Gentner (1983, structure-mapping); Falkenhainer, Forbus &amp; Gentner (1989, *Artificial Intelligence*, SME, primary
PDF verified); Clement &amp; Gentner (1991, *Cognitive Science*, systematicity-as-selection-constraint); Whittington,
Muller, Barry, Behrens et al. (2020, *Cell*, Tolman-Eichenbaum Machine, cited as a convergence point, not a direct
bridge between the two literatures -- flagged as this drill's own synthesis).

**Internal cross-thread:** `notes/research_brain_qa_architecture_completeness_2026-07-24.md`;
`notes/research_bindsettle_ci_settle_dynamics_multifact_aggregation_2026-07-24.md`;
`notes/research_contradiction_representation_and_settle_dynamics_2026-07-24.md`;
`notes/research_multihop_reasoning_layer_biology_and_design_sketch_2026-07-24.md`;
`notes/research_arc_retrieval_biology_and_design_2026-07-24.md`;
`notes/research_drill_metacognitive_calibration_escalation_trigger_2026-07-21.md`.

## Calibration reasoning (P_deflated = 0.32)

Raw confidence in the CORE BIOLOGY, per leg: Q2 (metacognitive escalation architecture) is high, ~0.85 -- multiply-
converging, well-established, textbook-consensus. Q3 (schema gap-fill lacks native confidence discount) is also high,
~0.85 -- cross-paradigm-replicated (Bartlett, script false-recognition, DRM, PDP settling all converge on the same
signature). Q1 (brittle vs graceful CI degradation) and Q4 (on-the-fly bridging, structure-mapping robustness) are
more moderate, ~0.55-0.65, because both rest partly on INFERENCE from adjacent literature (Hopfield basin theory
standing in for a CI-specific study; SME's graceful-degradation read from architecture rather than a direct
robustness benchmark) rather than a direct primary-source measurement. Standard lit-scan deflation (-0.15 to -0.25)
brings the biology average to roughly 0.55-0.65. The SUBSTRATE-APPLICATION step -- wiring THREE previously-separate,
previously-unwired primitives (confidence gate 29465, khop.py bridging, a NEW discounted-gap-fill mechanism that
does not exist yet in any form) into one bounded escalation loop, and expecting it to move the needle on the
specific 0.341 real-pool condition -- is genuine novel synthesis, capped at 0.50, further discounted to 0.32
because: (i) none of this has been smoked -- it is a design, not a measurement; (ii) the 0.690/0.341 baseline
numbers themselves were not independently re-verified on disk this session (Director-supplied, flagged above);
(iii) the confidence-gate atom (29465) and its exact interface were likewise not re-located this session and must
be confirmed before building; (iv) Q1's own brittle-threshold prediction means a meaningful fraction of real-pool
items may be genuinely unrecoverable by ANY combiner-side mechanism, capping the ceiling of what this whole design
can achieve even if every individual piece works as hypothesized.

## Next-drill candidate

Per the field-advisor read at cycle start (110 drills, 22 fields -- this topic is orthogonal to the substrate-physics
taxonomy the advisor tracks, cognitive-architecture/biology feeding the ARC/ingestion program). The natural next-
drill candidate, gated on this cell's build/smoke result: if arm D vs E (discount ablation) is INCONCLUSIVE or
HARD-FAIL, a focused 2x-depth drill on non-monotonic/default-logic defeasibility formalisms (Reiter default logic,
truth-maintenance systems, Bayesian/plausibility extensions to default reasoning) to sharpen HOW MUCH discount and
under what conditions it should apply, since this drill's biology establishes THAT a discount is needed but not a
principled magnitude. If arm C vs F (bridging) is INCONCLUSIVE, the network-science-graph-theory field (already
flagged as a Tier-1b next-drill candidate in `research_multihop_reasoning_layer_biology_and_design_sketch`) would
help characterize how often qualifying two-fact bridge pairs actually co-occur in a real, sparse elementary-science
KB, independent of whether the bridging mechanism itself works.
