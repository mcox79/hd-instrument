# BRAIN-DRILL (5x): the COHERENCE / SCHEMA-FIT GATE — how the brain decides an interpretation coheres, and how to build the glass-box gate around it

**Date:** 2026-07-19. **Filed by:** research (3 parallel Sonnet lit-scans — N400/P600/predictive-coding;
Kintsch Construction-Integration; garden-path/good-enough/comprehension-monitoring — synthesized by
director). Trigger: direct 5-angle USER drill naming the COHERENCE GATE as a named component needed
before noisy reader extractions (~0.40-0.60 precision, per
`research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md`) enter the reasoning-map, and
noting the reader-coupled compgen cell will show whether extraction noise breaks the structure-content
factorization (in which case the gate is the confirmed fix).

**Load-bearing disk fact found during this drill (not previously flagged in this arc): a first-draft
coherence gate ALREADY EXISTS in code** — `experiments/exp_role_filler_factorization_reader_coupled_cg_v1.py`,
function `schema_fit_gate()` (lines 278-322), wired as the `real_reader_gated` condition. It scores each
(slot, filler) training membership by `cosine(GloVe[filler], centroid of the slot's OTHER trainable
fillers)`, drops the globally lowest `drop_frac` fraction (floored per-slot so no slot starves), and
feeds the survivors into the SAME structure-content-factorization mechanism as the ungated arm. **This
cell has not yet been run** (`data/exp_role_filler_factorization_reader_coupled_cg_v1*` does not exist on
disk as of this drill) — it is pre-registered and ready to dispatch, not a hypothetical. This drill's job
is to (a) find the brain mechanism that should inform whether this first-draft gate design is
brain-faithful and sufficient, or needs upgrading BEFORE/alongside that dispatch, and (b) hand the
upgrade spec directly to whoever authors v2.

Lit-scan calibration penalty applied throughout (deflate P 0.15-0.25 from raw literature-agreement;
novel-synthesis capped P<=0.50).

---

## HEADLINE

**The brain does NOT have one coherence-monitoring mechanism — it has (at least) two, doing different
jobs, and the existing first-draft gate implements only a weak version of the WRONG one for a fix that
also needs the SECOND.** (1) A graded, continuous prediction-error signal (N400-family, formalized by
Rabovsky/Hansen/McClelland's Sentence-Gestalt model as "magnitude of update to a running situation-model")
that scores routine plausibility — the current gate's cosine-to-slot-centroid score is a crude, static
analog of this, but scores against a FIXED per-slot centroid rather than the CURRENT, growing situation-
model/discourse state, and uses a flat global-percentile threshold rather than a graded/precision-weighted
score. (2) A separate, discrete "flag for reanalysis" trigger (P600-family, contested but real) that fires
specifically when role/structural combination can't be reconciled, escalating to active repair — the
current gate has NO analog of this at all; it only accepts or silently drops, never flags-for-revision.
**And the brain's OWN baseline for "does the gate actually stop bad interpretations from being
consolidated" is worse than one might assume**: the good-enough-processing and Moses-illusion literature
(Ferreira & Patson 2007; Barton & Sanford 1993) shows the human default is to accept a locally-plausible,
GLOBALLY-wrong reading roughly 40-50% of the time in controlled paradigms, and demonstrably lets it persist
into durable memory (Bottoms & Eslick) — meaning an engineered gate that ALWAYS runs a global-consistency
check (rather than the brain's effort-gated, only-check-when-forced default) has a real, literature-backed
opportunity to structurally beat the brain baseline here, not just match it. Kintsch's Construction-
Integration model supplies the best formal existence-proof for HOW multiple candidate interpretations get
narrowed to one via mutual constraint satisfaction (a settling spreading-activation network, analytically
characterized for convergence by a dedicated *Journal of Mathematical Psychology* paper) — but even CI's
own descendants (garden-path/constraint-based-parsing literature) document that the settling process CAN
confidently converge on a wrong interpretation, so "let it settle" alone is not a safe filter; it needs the
graded-score-plus-flag structure from angles 1+3, not a bare accept/reject.

**Ranked brain mechanism to build around: a two-signal gate — (a) graded prediction-error-to-situation-model
score for the routine accept/downweight decision (N400/Sentence-Gestalt-inspired), PLUS (b) a discrete
structural-incoherence flag that escalates ambiguous/contradictory cases to a settle-then-decide step
(CI-integration-inspired) instead of a silent drop — with the entire design held to the honest bar that
"accept-uncorrected" is a documented, common, ~40-50%-rate human failure mode, so an always-on (not
effort-gated) check is where the engineered version can plausibly do better than biology, not just imitate
it.** Deflated P = 0.50 (capped, novel-synthesis) that this two-signal architecture is the right build;
individual cited mechanisms sit higher (P~=0.55-0.70, established literature per section below).

---

## (1) Neuroscience of coherence monitoring — N400 / P600 / ATL

*Lit-scan 1, generic-terms-only queries, live-search-verified unless flagged.*

- **Kutas & Federmeier (2011), *Annual Review of Psychology*** (verified) — N400 amplitude indexes ease
  of semantic access/integration, scaled by contextual predictability; field consensus has moved toward a
  prediction/pre-activation framing rather than passive post-hoc integration difficulty. **Implies: the
  routine coherence signal is GRADED and continuous, not binary** — a real-valued mismatch score, not a
  yes/no flag.
- **Rabovsky, Hansen & McClelland (2018), *Nature Human Behaviour*** (verified) — the Sentence Gestalt
  connectionist model reproduces a wide range of N400 modulations from ONE mechanism: N400 amplitude tracks
  the MAGNITUDE OF UPDATE forced onto a running probabilistic "sentence meaning" (situation-model)
  representation by the incoming word — i.e., semantic prediction error against the CURRENT discourse
  state, not against a fixed prior template. **Implies: the gate's reference point should be the CURRENT,
  growing situation-model, not a static per-slot centroid** — directly diagnostic of a gap in the existing
  first-draft gate (see verdict below).
- **Kim & Osterhout (2005); van Herten et al. (2005/2006), the "semantic P600" literature** (verified,
  and explicitly contested — Chow & Phillips 2013 and a Mandarin replication dispute whether this is a
  genuine separate "semantic illusion" detector vs. continued combinatorial reanalysis) — grammatical-but-
  implausible thematic-role-reversal sentences ("the hearty meal was devouring the kids") elicit P600, NOT
  N400, breaking a clean semantic->N400 / syntactic->P600 double dissociation. **Implies: there is a
  SEPARATE signal that fires specifically when role/argument-structure can't be reconciled, distinct from
  plain lexical-semantic mismatch** — this is the flag/escalation signal, not the graded score.
- **Patterson, Nestor & Rogers (2007), *Nature Reviews Neuroscience*** (verified) — anterior temporal lobe
  (ATL) as an amodal semantic "hub" integrating modality-specific spokes (evidence: semantic-dementia
  deficit pattern). **Baron & Osherson (2011), *NeuroImage*** (verified) — LATL representations of
  composed concepts ("young man") are approximately ADDITIVE over their constituents. **Implies: a
  compositional-coherence check exists biologically at the hub level** — test whether a candidate relation's
  combined representation is a well-formed point in the same additive/compositional space as its parts, a
  cheap analog our substrate's additive_map compositional-readout already computes as a byproduct.
- **Kuperberg (predictive-coding accounts of language comprehension, incl. 2024 Cognition paper)** (verified
  via search hits, primary text not fully read — moderate confidence) and **Friston-style precision-weighted
  predictive coding (Millidge et al. 2021 review, general theory, verified)** — prediction error is
  PRECISION-WEIGHTED: an attention/gain term decides whether a given error signal is even ALLOWED to drive
  belief-update (low precision -> error suppressed/ignored; high precision -> error drives revision).
  **Implies: the gate needs a per-relation "how much should this error matter" weighting, not a flat
  threshold applied identically everywhere** — directly parallel to the already-landed schema-fit/surprise
  consolidation-cost finding in `research_compounding_learning_missing_structure_schema_gated_consolidation_2026-07-18.md`
  (variable cost, not flat rehearsal), now reinforced from an independent (comprehension-monitoring, not
  memory-consolidation) angle.

**Deflated confidence: P~=0.60** that coherence-monitoring is split into (a) a graded continuous
prediction-error signal and (b) a separate discrete structural-incoherence-escalation signal — established
core findings on both sides, but the field itself is split on whether these are truly two mechanisms or one
graded process interpreted two ways (flag honestly, not suppressed).

---

## (2) Kintsch Construction-Integration — is settling literally the gate?

*Lit-scan 2, generic-terms-only queries, live-search-verified unless flagged.*

- **Kintsch (1988), *Psychological Review*; Kintsch (1998) book** (verified via secondary
  summaries/ACM overview; the exact original matrix-update equation could not be pulled from a live
  full-text hit today — flagged as recalled/folklore, not freshly re-verified) — CONSTRUCTION phase spreads
  activation loosely and INDISCRIMINATELY (including irrelevant/wrong candidate propositions on purpose);
  INTEGRATION phase is constraint satisfaction implemented as iterative spreading activation over a
  proposition-connectivity matrix built from argument overlap/context fit: propositions that mutually
  cohere reinforce each other's activation, propositions that don't fit are inhibited toward zero, over a
  small fixed number of cycles (not run to a formal energy minimum in the original papers).
- **"Convergence of the Integration Dynamics of the Construction-Integration Model," *Journal of
  Mathematical Psychology*** (verified, live-search-confirmed listing) — treats CI's integration step as a
  nonlinear dynamical system on the connectivity matrix and analytically characterizes its equilibrium/
  fixed-point behavior. **This is the closest formal proof that "settle a constraint network, keep what
  survives" has well-defined convergence properties** — not framed as Hopfield energy-minimization
  specifically (no energy function asserted), but a characterized nonlinear iterative map.
- **van den Broek, Young, Zheng & Linderholm; Yeari & van den Broek (2011), the Landscape Model**
  (verified) — extends CI with activation fluctuation across reading cycles PLUS two reinstatement
  mechanisms: passive cohort activation (simple associative spread) and active COHERENCE-BASED RETRIEVAL —
  when a coherence-break is detected against a reader's coherence STANDARD, the model actively searches
  back through prior text/background knowledge to re-establish a connection. **This is a citable, named
  "detect coherence-break -> trigger repair-search" mechanism, distinct from and richer than "just let it
  settle."**
- **Garden-path / constraint-based-parsing literature (CI-adjacent, not identical to Kintsch 1988 proper —
  flagged honestly as a related-but-distinct mechanism family)** (verified) — documents that the settling/
  constraint-satisfaction process CAN confidently commit to and RETAIN a wrong interpretation even after
  disambiguating information arrives (the "lingering misinterpretation" effect, directly reinforced by
  lit-scan 3's Christianson et al. 2001 finding below). **This is the critical caveat: settling is not
  automatically a SAFE filter — an incoherent candidate can win the settling process outright.**

**Implementation recipe this literature supports (synthesis, not a direct quote):** represent each
candidate relation/interpretation as a node with bottom-up-seeded initial activation; build a
pairwise fit matrix W (positive = mutually consistent/context-fitting, negative/zero = contradictory or
irrelevant, including a self-term for fit-to-the-running-situation-model); iterate A(t+1) =
normalize(A(t)*W) for a small bounded number of cycles (bounded per the JMP convergence
characterization); apply a THRESHOLD at convergence — high final activation = accept, near-zero = reject,
and (the piece CI itself does not specify, and the garden-path caveat says is NECESSARY) nodes that
oscillate or land in a middle band = FLAG for external disambiguation rather than silently resolving.

**Deflated confidence: P~=0.55** that CI-style multi-candidate settling is the right mechanism for
resolving MUTUAL coherence among several candidate relations at once (established core mechanism,
formally characterized convergence), but capped because the specific original matrix-update formula
could not be freshly verified today and no source confirms CI itself includes a safe "flag the ambiguous
middle" step — that addition is this drill's own synthesis, informed by the garden-path caveat.

---

## (3) Predictive coding — folded into angle 1 above (Rabovsky/Kuperberg/Friston); see there for citations
and the precision-weighting implication. Restated for completeness: coherence = low prediction-error
against the running situation-model; incoherence = high prediction-error, and whether that error triggers
revision depends on a PRECISION weighting, not the raw error magnitude alone — directly informs the
"graded score, precision-weighted, not a flat threshold" design element below.

---

## (4) Error recovery / avoiding knowledge-poisoning — garden-path reanalysis, good-enough processing, comprehension-monitoring failures

*Lit-scan 3, generic-terms-only queries, live-search-verified unless flagged.*

- **Christianson, Hollingworth, Halliwell & Ferreira (2001), *Cognitive Psychology* 42:368-407**
  (verified) — "Thematic Roles Assigned along the Garden Path Linger." After garden-path sentences (e.g.
  "While Anna dressed the baby played in the crib"), readers frequently still answer "yes" to "Did Anna
  dress the baby?" even after correctly parsing the disambiguating continuation — the WRONG initial
  thematic assignment persists ALONGSIDE, not replaced by, the correct final parse. Reanalysis is
  partial/incomplete, not all-or-nothing.
- **Frazier & Rayner (1982), garden-path/Selective Reanalysis Hypothesis** (verified) — reanalysis is a
  distinct repair mechanism triggered when the initial parse fails a later structural check; NOT guaranteed
  to succeed or be complete, consistent with Christianson et al.'s lingering-misparse finding.
- **Ferreira & Patson (2007), *Language and Linguistics Compass* 1:71-83**, "The 'Good Enough' Approach to
  Language Comprehension" (verified) — comprehenders often build shallow, heuristic, non-fully-compositional
  representations sufficient for the immediate task, and TOLERATE perceived oddities left unresolved; full
  reanalysis/verification triggers only when a sufficiently strong signal forces it (e.g., a direct
  comprehension question) — otherwise the shallow, possibly-wrong representation stands, uncorrected.
- **Barton & Sanford (1993), *Memory & Cognition* 21:477-487** (verified) — ~40% of subjects failed to
  notice a semantic anomaly despite otherwise fluent reading; the classic **Moses illusion** (Erickson &
  Mattson 1981 lineage) shows the same pattern at scale — a wrong-but-locally-plausible referent (Moses vs.
  Noah) goes undetected because comprehension checks new information against BACKGROUND/GIVEN material only
  shallowly, not by fully re-verifying it against stored world-knowledge.
- **Bottoms & Eslick et al., "Memory and the Moses illusion: Failures to detect contradictions with stored
  knowledge yield negative memorial consequences"** (verified) — the undetected error is not just a
  momentary lapse; it propagates into LATER memory/judgment — the direct biological analog of "a bad
  extracted relation silently enters durable knowledge."
- **Comprehension-monitoring literature (Oakhill/Cain tradition, "Process and Product of Coherence
  Monitoring")** (verified, explicitly contested in the source material itself) — mixed evidence on WHERE
  monitoring fails: some studies find the coherence-break is never even flagged online; others find longer
  gaze duration AT the break (meaning it WAS detected transiently) but the detection never gets encoded or
  reported afterward — i.e., detection and repair-commitment are dissociable failure points, not one
  failure.

**Implication (the sharpest, most actionable finding of this whole drill): "good-enough, uncorrected,
plausible-but-wrong" is a real, common, well-documented human failure mode — not an edge case — showing up
at both the syntactic level (garden-path lingering, Christianson et al.) and the semantic/world-knowledge
level (Moses illusion, ~40-50% miss rates), and it demonstrably propagates into durable memory (Bottoms &
Eslick). The brain's default is a cost-sensitive heuristic monitor that only escalates to expensive full
verification when forced by task demands. An ENGINEERED gate does not face that attention-economy
constraint — it can run the equivalent of "always ask the comprehension question" (always fully verify a
candidate relation against the stored global model, not just the locally plausible surface cue) on every
extraction, for free relative to a biological system. This is the one place in this drill where the honest
verdict is NOT "match the brain" but "the brain sets a genuinely low bar here, and an always-on check can
structurally clear it" — while still respecting the dissociation caveat: if the real bottleneck is
encoding-after-detection rather than detection itself, the gate's job is less "notice the anomaly" (which a
cheap always-on check plausibly already achieves) and more "force the consequence of that notice to
actually block the write" — arguably the EASIER of the two engineering targets, and the one the existing
code-level gate (a silent drop, no separate "detected but not yet resolved" state) does not yet implement.**

**Deflated confidence: P~=0.65** that accept-uncorrected-plausible-but-wrong is a genuine, common,
well-replicated human failure mode (established, multiply-replicated across syntactic and semantic
paradigms) — high confidence on the EXISTENCE of the failure mode; lower confidence (folded into the
overall P=0.50 design verdict) on exactly how much headroom an always-on engineered check captures on OUR
specific reader's noise profile, which is untested.

---

## (5) THE DESIGN VERDICT — ranked brain mechanism + concrete glass-box gate

**Ranked brain mechanism (name it): a TWO-SIGNAL coherence gate — (a) a graded, situation-model-conditioned
prediction-error score (N400/Sentence-Gestalt-inspired, precision-weighted per Friston/Kuperberg) for the
routine accept/downweight decision, composed with (b) a discrete structural-incoherence FLAG (P600-family-
inspired) that escalates role/argument-structure conflicts to a CI-style multi-candidate settling step
rather than a silent drop, all held to the honest bar that "always-on verification" is where an engineered
system can beat, not merely match, the brain's effort-gated default.** This is not one textbook-named
mechanism but a synthesis across four independently-converging literatures (ERP, predictive coding, CI/
Landscape, comprehension-monitoring) — held at the calibration cap, P<=0.50, as a design proposal.

### Concrete glass-box VSA coherence-gate design

**Inputs available today, reused not reinvented:** (i) the reader's per-relation extraction (verb-slot,
filler, sentence context); (ii) the running discourse/situation-model overlay
(`exp_read_discourse_state_hd_vs_symbolic_coherence_scalar_score_v1` — an HD-bundle scalar coherence score
already built and tested, aggregate AUCd2 in the 0.55-0.81 range depending on bundle load, HARD_FAIL as an
end-to-end capacity claim but the SCALAR COHERENCE SCORE PRIMITIVE itself is functional and reusable here);
(iii) the existing schema-fit gate's cosine-to-centroid machinery
(`exp_role_filler_factorization_reader_coupled_cg_v1.py::schema_fit_gate`); (iv) the additive_map
compositional-readout (ATL-additivity analog, angle 1); (v) the KL/Bayesian-surprise primitive already
built for the memory-ingest gate (already flagged as the same math object at a different grain per
`research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md`).

**Score 1 — graded prediction-error-to-situation-model (replaces/upgrades the current gate's fixed
per-slot centroid):** for each candidate relation, compute cosine-similarity (or KL-divergence, reusing the
existing surprise primitive) between the candidate's bound FHRR representation and the CURRENT discourse-
state overlay vector, NOT a static training-set centroid. This directly fixes the gap angle 1 diagnoses in
the existing code: `schema_fit_gate()` scores against "centroid of the slot's OTHER trainable fillers" —
a fixed, corpus-wide, backward-looking reference — rather than the CURRENT, incrementally-growing
situation-model the N400 literature says is the actual reference point. Precision-weight this score by a
term that scales with how much local context is available (Friston precision-weighting) — early in a
document, downweight the error term (little context yet, wide precision → don't punish); later, upweight it.

**Score 2 — discrete structural-incoherence flag (the piece the existing gate has zero analog of):**
separately check whether the candidate relation's ROLE/ARGUMENT structure is internally consistent with
already-known relations for the same predicate/argument (a taxonomic/is-a-hierarchy consistency check per
the task's candidate (c) — e.g. reject "dog is-a plant" against an established is-a hierarchy, independent
of the graded cosine score, which could be fooled by surface lexical similarity). This is a discrete
accept/flag/reject decision, not a threshold on the same continuous score as (1) — mirroring the P600 vs
N400 dissociation.

**Settling step (only for the FLAGGED middle band, reusing Kintsch CI, not applied to every extraction —
keeps cost bounded):** when a relation is flagged, build a small local constraint network of the flagged
candidate plus its neighboring already-accepted relations (same sentence/paragraph); run the bounded
iterative update A(t+1)=normalize(A(t)*W) for a small fixed number of cycles (analytic convergence bound
per the JMP paper, angle 2); if the flagged node's activation converges HIGH, accept; if it converges LOW,
reject; if it still oscillates/lands in a genuine middle band after the cycle budget, route to a THIRD
state — **DEFERRED, not silently dropped and not silently accepted** — held out of the foundation until
either more context resolves it or an explicit re-extraction pass revisits it. This DEFERRED state is the
single most important addition this drill proposes over the existing code: the current `schema_fit_gate`
has exactly two outcomes (keep/drop); the comprehension-monitoring literature's dissociation finding
(detection vs. encoding-consequence) says the THIRD state — detected-as-ambiguous-but-not-yet-resolved —
is the state the brain's own failure mode analysis says matters most to make explicit, not implicit.

**Why this stays flexible / compounds (the Matthew property the task asks for):** Score 1 is conditioned
on the CURRENT situation-model, which grows every document — so the same candidate relation gets judged
against a richer reference as the knowledge base grows, meaning coherence-judgment quality is not fixed at
gate-design-time but improves automatically as ingestion proceeds (directly the property the
`research_compounding_learning_missing_structure_schema_gated_consolidation_2026-07-18.md` note already
established should hold for the sibling consolidation-cost problem — this is the same structural
requirement, applied to comprehension instead of memory-write). The taxonomic consistency check (Score 2)
also strengthens automatically as more of the is-a hierarchy gets populated. The settling step's neighbor
pool (already-accepted relations to constrain against) is also larger and denser as the foundation grows,
making DEFERRED cases resolvable on LATER passes even if they could not be resolved on first read — this
is the direct glass-box analog of reconsolidation (angle 2/4 convergence with the separately-landed
compounding-learning note's Rank-1b reactivation-triggered-reconsolidation finding): a DEFERRED relation is
exactly a candidate for later re-scoring against a grown situation-model, not a permanently lost read.

---

## Cheap decisive test

**Zero new build required for step 1 — the cell already exists and has not been run.** Dispatch
`exp_role_filler_factorization_reader_coupled_cg_v1.py` (smoke then full) AS-IS first. Its three conditions
(`control_synthetic`, `real_reader`, `real_reader_gated`) already isolate exactly the question this drill
was asked to inform: does the FIRST-DRAFT gate (flat global-percentile cosine-to-centroid, no situation-
model conditioning, no flag/defer state) recover any of the gap between `real_reader` and
`control_synthetic`? This is the existing pre-registered HARD_FAIL_READER_NOISE_BREAKS /
HARD_PASS_READING_AXIS_FIRST_CG verdict logic already written into the cell (lines 92-104) — reuse it
verbatim, do not re-design. If `real_reader_gated` shows measurable but incomplete recovery (a MIDDLE_BAND
outcome), that is the clean trigger to build the Score-1/Score-2/settling/DEFERRED upgrade this drill
specifies, with the FIRST-DRAFT gate's own dropped-examples log
(`gate_stats["dropped_examples"]`) as a free diagnostic corpus of what the crude centroid-cosine version
gets wrong — useful for calibrating whether situation-model-conditioning specifically (Score 1) or
taxonomic consistency specifically (Score 2) would have saved the dropped-but-actually-valid cases.

## Falsifiable predictions — HARD-PASS / HARD-FAIL

**Prediction A (existing first-draft gate, as-is, is not sufficient — the cheapest, already-coded test).**
P=0.45 (deflated). HARD-PASS (first-draft gate already sufficient, no upgrade needed): `real_reader_gated`
FACTORED held-out accuracy at headline N recovers to within 0.05 absolute of `control_synthetic` AND the
cell's own pre-registered HARD_PASS_READING_AXIS_FIRST_CG bands fire. HARD-FAIL (first-draft gate
insufficient, upgrade needed as designed above): `real_reader_gated` shows <=30% relative recovery of the
`real_reader` vs `control_synthetic` gap, or drops so many true relations that it falls into the cell's own
VOID/MIDDLE_BAND bands — this is the expected, not surprising, outcome given the fixed-centroid /
no-situation-model-conditioning gap this drill diagnoses; a MIDDLE_BAND result (partial recovery) is the
most likely real outcome and is itself the trigger for the v2 build, not a failure of this drill.

**Prediction B (situation-model-conditioned Score 1 beats fixed-centroid Score, on the SAME dropped-vs-kept
cases from the first-draft gate's log).** P=0.40 (deflated, novel-synthesis, not yet tested against real
data). HARD-PASS: re-scoring the first-draft gate's own `dropped_examples` against the CURRENT discourse-
state overlay (rather than the static slot centroid) reclassifies >=25% of dropped-but-actually-valid
relations (validated against an external/held-out gold check, not the same generator) as coherent, with
<10% of the correctly-dropped noise reclassified as coherent (precision-recall tradeoff must improve on
BOTH sides, not trade one for the other). HARD-FAIL: reclassification rate <10% on either side, or improves
recall only by also flooding back in genuine noise (net precision does not improve) — would mean the
situation-model-conditioning refinement is not the load-bearing lever, and the flat/global gate is closer
to a real ceiling than this drill's mechanism-story suggests.

**Prediction C (the DEFERRED/flag state captures cases neither pure accept nor pure reject correctly
resolves, and later re-scoring against a grown foundation resolves a real fraction of them).** P=0.35
(deflated further — the reconsolidation-for-declarative-facts extrapolation flagged in the sibling
compounding-learning note applies here too). HARD-PASS: on a held-out set of genuinely ambiguous
extractions (neither confidently coherent nor confidently incoherent under Score 1+2 at first pass),
re-scoring after the foundation has grown (more accepted relations, richer situation-model) correctly
resolves >=40% of them (external gold check) with a false-resolution rate (confidently resolved WRONG)
below 15%. HARD-FAIL: resolution rate <15% even with a grown foundation, OR false-resolution rate exceeds
correct-resolution rate — meaning deferral buys no compounding benefit and a flat accept/reject-only gate
is the honest ceiling.

---

## FAIR can-fail test (full specification)

**Real baseline:** the CURRENT reader extraction pipeline UN-gated (`real_reader` condition, already coded,
not a strawman — it is the arm the existing cell was built to compare against).

**Can-fail (both directions, not just one):** the gate genuinely can hurt — real narrative slots have
legitimately diverse fillers (already flagged in the cell's own brain-check section, line 80), so an
over-aggressive gate can drop TRUE relations and reduce recall/coverage, not just noise. Symmetrically, an
under-aggressive gate (too permissive Score 1/2 thresholds) can pass through the SAME plausible-but-wrong
relations the good-enough/Moses-illusion literature says slip past a biological monitor — the gate must be
shown to beat, not just re-create, that failure mode.

**One variable per arm:**
- Arm 1 isolates the EXISTING first-draft gate design (fixed centroid, global percentile, binary
  keep/drop) vs ungated — this is Prediction A, already fully specified in the existing cell, zero new code.
- Arm 2 isolates situation-model-conditioning specifically: same drop mechanism, but Score computed against
  current discourse state instead of static centroid — Prediction B.
- Arm 3 isolates the DEFERRED/settling addition specifically: same Score 1+2, but adds the third
  (defer-then-resettle) state vs a forced binary accept/reject at first pass — Prediction C.

**Precision-recall tradeoff, measured explicitly (not just accuracy):** report BOTH the fraction of true
relations preserved and the fraction of noise removed for every arm — a gate that "improves accuracy" by
dropping half the true relations along with the noise is not a win; the existing cell's `gate_stats`
(`n_dropped`, `n_total`, `drop_frac_effective`) already logs the raw counts needed for this, extend to a
precision/recall pair against an external gold check per arm.

**Independent gold, not self-graded:** all three predictions require validation against an EXTERNAL
held-out gold-annotated slice, never the same reader/generator that produced the candidate relations being
gated — this guards against the construction-determined-outcome trap already flagged in
`research_drill_relation_comprehension_reader_thematic_roles_glassbox_2026-07-18.md` and reiterated as a
standing discipline in this arc.

---

## Brain-check (outcome not pre-assumed, per standing discipline)

**Coherence-gating IS a real, existence-proven brain capability** — N400/predictive-coding gives a graded
continuous version, P600/semantic-P600 debate gives a (contested) discrete structural-escalation version,
CI/Landscape gives a formally-characterized multi-candidate settling mechanism. This is NOT a case where
the brain lacks the capability; the brain clearly does something in this space, continuously, online, per
word.

**Where the brain-check reveals a REAL structural bound (same-limit, accept):** the settling mechanism
itself (CI/constraint-satisfaction) can confidently converge on and RETAIN a wrong interpretation — this is
not a brain bug fixable by "trying harder," it is a property of any bounded-iteration constraint-
satisfaction settling process (the garden-path lingering-misinterpretation literature shows this happens in
biological wetware too). **Implication for the substrate: the settling step alone cannot be trusted as a
complete safety net — the DEFERRED/flag state is required precisely because settling-to-convergence is not
guaranteed to converge to the CORRECT answer**, only to A stable answer. This is a genuine, brain-shared
limit, not a substrate-specific weakness — accept it and design around it (the DEFERRED state IS the
design-around, not a workaround for a brain-absent capability).

**Where the brain-check reveals the brain fails the SAME way, meaning the fix is substrate-NATIVE not
brain-imitative (per the 07-17 refinement anchor):** the good-enough/Moses-illusion literature shows the
brain's DEFAULT coherence-monitoring is effort-gated and frequently skipped — roughly 40-50% miss rates on
controlled semantic-anomaly paradigms, and the miss demonstrably propagates into durable memory. Imitating
this default (an effort-gated, sometimes-skipped check) would be imitating a well-documented brain FAILURE
MODE, not its capability. **The substrate-native fix is to make the check ALWAYS-ON rather than effort-
gated** — the brain has no analog for "always fully verify," because biological attention is a genuinely
scarce resource in a way compute cycles for a bounded per-relation check are not. This is the one place in
this whole drill where the honest engineering target is explicitly ABOVE the brain baseline, stated
plainly rather than smoothed over.

---

## Cross-thread synthesis

This drill fills a real, previously-undrilled gap in the arc: five prior notes
(`research_missing_structure_learned_comprehension_5x_drill_2026-07-18.md`,
`research_compounding_learning_missing_structure_schema_gated_consolidation_2026-07-18.md`,
`research_schema_fit_derivability_signal_upgrade_2026-07-16.md`,
`research_consolidation_gate_signal_mechanism_and_integration_2026-07-16.md`,
`research_consolidation_function_inventory_schema_reorg_2026-07-16.md`) established schema-fit/surprise as
load-bearing signals for MEMORY-CONSOLIDATION cost and eligibility, but none had yet drilled the specific,
narrower, upstream question this task poses: how does the brain gate COMPREHENSION/EXTRACTION coherence,
before a candidate relation is even a consolidation candidate? The answer converges cleanly with the prior
memory-consolidation thread's own structure (graded, situation-conditioned score + a revisable/deferred
state, not a flat one-shot gate) — the SAME architectural shape (variable-cost, reactivation-capable
gating) recurs at the comprehension layer as at the memory-consolidation layer, independently re-derived
here from four different literatures (ERP, predictive coding, CI, comprehension-monitoring) rather than
copied from the consolidation note. This is a genuine, not merely coincidental, convergence: both problems
are instances of the SAME general principle (Friston precision-weighting / McClelland 2013 schema-gated
bypass / EWC Fisher-weighting / N400 prediction-error, per the two notes combined) — "how much should a new
piece of information change what's already believed" — applied at two different grains (word-by-word
comprehension vs. document-by-document consolidation).

The most concrete, load-bearing NEW fact this drill surfaces (not previously flagged): the first-draft
coherence gate is not hypothetical — it is ALREADY WRITTEN CODE (`schema_fit_gate()` in
`exp_role_filler_factorization_reader_coupled_cg_v1.py`), pre-registered with its own HARD-PASS/HARD-FAIL
bands, and simply has not been dispatched yet. The highest-leverage next action is not a new design
document but literally running the cell that already exists, using its own results (particularly the
`dropped_examples` diagnostic log) to decide whether the upgrades this drill specifies (situation-model
conditioning, taxonomic consistency check, DEFERRED state) are needed, and how urgently.

## Substrate-product implications

Not a publication angle — a build-priority and reliability angle. If the existing first-draft gate
(zero new code, already written) shows even partial recovery, that is immediate, cheap evidence that
gating noisy extractions before they enter the foundation is a viable, buildable capability — directly
relevant to any "trustworthy ingestion pipeline" product claim (a system that can quantify and bound its
own extraction-error rate, rather than silently accumulating it, is a real differentiator against
competitors that do one-shot LLM-extraction with no downstream verification layer). If the DEFERRED-state
addition (Prediction C) holds, the product gets a genuine, auditable "I don't know yet, revisit me later"
state for ambiguous extractions — an honesty property most competing pipelines (forced-choice extraction,
no deferral) structurally lack, and one that compounds: the same deferred item gets cheaper to resolve
correctly as the knowledge base grows, which is a direct instance of the already-identified Matthew-effect/
compounding-learning product story. If Predictions B/C HARD-FAIL, the honest fallback is that the
existing flat cosine-centroid gate (Prediction A's target) is close to the achievable ceiling for this
specific mechanism, and further investment should redirect to the OTHER ranked gap already identified in
this arc (the construction-induction/disambiguation-scorer build, per the 07-18 missing-structure note's
Rank 2) rather than continuing to refine the gate itself.

## Citations (verified count)

**~20 distinct primary/named sources freshly verified via live search this session** across the three
lit-scans: Kutas & Federmeier 2011; Rabovsky, Hansen & McClelland 2018; Kim & Osterhout 2005; van Herten
et al. 2005/2006; Chow & Phillips 2013; Patterson, Nestor & Rogers 2007; Baron & Osherson 2011; Kuperberg
(2024 Cognition, moderate confidence); Millidge et al. 2021 (general predictive-coding review); Kintsch
1988/1998 (secondary-verified, primary matrix formula recalled not fresh); the *Journal of Mathematical
Psychology* CI-convergence paper; van den Broek/Yeari Landscape Model 2011; Christianson, Hollingworth,
Halliwell & Ferreira 2001; Frazier & Rayner 1982; Ferreira & Patson 2007; Barton & Sanford 1993; Erickson &
Mattson 1981 (Moses illusion lineage); Bottoms & Eslick et al.; Oakhill/Cain comprehension-monitoring
tradition. Plus 5 prior-arc notes cited and cross-checked against, not re-derived (listed in Cross-thread
synthesis). All claims flagged live-verified vs. recalled-from-training/secondary-sourced are marked
inline per sub-agent report; excluded from load-bearing predictions where flagged as recalled-only.

## Calibration

Per [[feedback-lit-scan-calibration-penalty]]: all P estimates deflated 0.15-0.25 from raw
literature-agreement reads. The overall design verdict (two-signal gate + DEFERRED state) is
novel-synthesis, capped at **P<=0.50**. Individual established literature claims (N400 prediction-error
framing, CI settling mechanism, garden-path lingering-misinterpretation, Moses-illusion miss rates) sit at
the higher P~=0.55-0.65 band reported per-section above. HYPOTHESIS-generating throughout; VET-pending; no
claim here should be treated as settled until the cheap decisive test (dispatch the already-existing cell)
returns.
