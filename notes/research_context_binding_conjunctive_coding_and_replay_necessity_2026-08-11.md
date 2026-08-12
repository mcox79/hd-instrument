# Research: context-binding / conjunctive coding + is replay necessary for the fade (brain-mechanism drill)

Filed by: research (Sonnet, foreground synthesis over 3 parallel Sonnet lit-scan sub-agents,
generic-term queries per query-privacy discipline). Trigger: Director task, explicit "accuracy is
paramount, be maximally brain-foundational" instruction, directly informing the live
context-dependent-entity-fate build (water is MOVED in the water-cycle, CREATED in respiration;
naive `water -> fate` storage averages/conflates across processes and loses the context).

KB-CHECK DONE FIRST (mandatory dedup): read in full before drilling --
`notes/research_drill_dentate_gyrus_pattern_separation_resolution_at_2pct_2026-07-04.md` (DG
resolution-vs-separation law, expansion lever, already answers "how many active units" but not
"item x context capacity"), `notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md`
(CLS replay-based redesign, already finds `cls_discrete_budget_consolidate` certified+islanded,
but its consolidation citations are flagged "recalled from general knowledge, not re-verified" --
this drill supplies the causal verification that note lacked), `notes/brain_whitening_decorrelation_
pattern_separation_fidelity_2026-07-30.md` (sparse-fan-in + divisive-normalization is the correct DG
mechanism, not PCA whitening), and the 2026-08-10 crutch-fade cluster (`research_crutch_design_and_
generalization_2026-08-10.md`, `research_brain_scaffolding_that_fades_2026-08-10.md`,
`research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md`, `design_prelim_tier_staged_
consolidation_crutch_fade_2026-08-10.md`) which drilled FADE/consolidation exhaustively for
GENERIC single-fact acquisition (Fitts & Posner stages, Logan instance theory, Newell & Rosenbloom
power law, Schneider & Shiffrin consistent-mapping, Tse/van Kesteren schema-gating cited but not
mechanistically detailed) and independently confirmed BANK writes to a flat side-table dict, never
into a natively-read structure -- structurally identical finding to what this drill's Verdict 3
below reaches from a different (capacity/replay-causality) angle. None of the prior notes drilled
**item-IN-CONTEXT conjunctive coding** (the specific mechanism needed when the SAME entity has
DIFFERENT fates in different processes) or the **replay-necessity-vs-accumulation-sufficiency**
question with causal (not correlational) evidence -- both are genuinely new ground, confirmed by a
targeted grep across `notes/` for `conjunctive|entorhinal|lateral entorhinal|medial entorhinal|
Ribot|multiple trace theory|Tse.*schema|SLIMM` returning zero prior full drills on these specific
angles (only passing citations inside the fade cluster above).

Also read fresh on disk this session (not from memory of prior notes' descriptions): `hdlab/hd_fact_
store.py` (FACT_ROLES tuple, `store()` conflict-resolution logic, `_cleanup()` -- confirmed
single-shot argmax, NOT iterative), `hdlab/situation_model_accumulate.py` (`AccumulateRegister`,
`CausalLinkRegister` -- confirmed per-entity bundle with no context slot in the bind), `hdlab/
hippocampal_encoder.py` (`DGProjection`, `CA3AutoAssociator`, `cls_discrete_budget_consolidate` --
confirmed zero callers outside its own file, still fully islanded as of this session), `hdlab/
cleanup_family.py::iterative_attractor` (confirmed genuinely iterative: `max_steps`, `tol`,
`converged` flag, softmax-weighted settling -- own docstring cites Treves-Rolls; this IS the
correct-shape CA3-completion primitive, just not wired to the fact-binding call sites).

Method: 3 parallel Sonnet lit-scan sub-agents (generic neuro/math terms only, no substrate-novel
names off-platform per [[feedback-query-privacy-decomposition]]) covering (1) conjunctive coding +
theoretical capacity, (2) the replay-necessity-vs-accumulation debate with causal evidence, (3)
schema-gated fast consolidation mechanism (Tse et al., mPFC, indexing theory). Synthesized below
against the on-disk organs.

---

## HEADLINE

**Three precise, independently-converging answers, each with a concrete substrate correction.**

**(1) Superposition-of-bound-(entity,context)-pairs IS a defensible computational-level (Marr
algorithmic-level) model of hippocampal conjunctive coding -- but only with three named fidelity
corrections our current organs mostly already have as CERTIFIED, ISLANDED primitives: (a) the bind
must be preceded by a DG-style sparse EXPANSION+threshold recoding, not a raw dense bind
(`hdlab.hippocampal_encoder.DGProjection` exists, zero callers); (b) retrieval must be ITERATIVE
attractor settling, not one-shot argmax (`hdlab.cleanup_family.iterative_attractor` exists, genuinely
iterative, matches CA3 dynamics -- but `hd_fact_store._cleanup()`, the store this problem needs, is
confirmed on disk to be a single-shot `argmax(cb @ filler_hat)`, not this primitive); (c) capacity is
NOT unbounded -- the classic sparse-associative-memory scaling law (Treves & Rolls 1991/1994) bounds
how many (entity,context) conjunctions one superposition register can hold before CATASTROPHIC
(cliff, not graceful) collapse, and this composes directly with the already-existing 2026-07-04
DG-expansion finding rather than being a new, separate problem.

**(2) Is REPLAY necessary for the fade, or does accumulation suffice? Necessary for the GENERAL
case (multiple independent causal designs converge on this), with one causally-validated EXCEPTION:
schema-congruent material.** Closed-loop sharp-wave-ripple disruption (Girardeau et al. 2009;
Ego-Stengel & Wilson 2010; Jadhav et al. 2012) impairs consolidation despite matched total sleep
time; targeted memory reactivation (Rasch et al. 2007; Rudoy et al. 2009) and optogenetic
replay-content manipulation (de Lavilleon et al. 2015) show inducing MORE reactivation causally
IMPROVES retention, holding elapsed time fixed -- this is about as clean a causal case as exists in
systems neuroscience for "replay does something mere accumulation does not." BUT Tse et al.
2007/2011 (causal, hippocampal-lesion-based) show that when a pre-existing SCHEMA already covers the
new material's structure, a single learning trial becomes hippocampus-independent within 48 hours --
a genuinely faster, lower-replay-dosage alternate route, not a refutation of (2)'s general finding.
**Our current plan ("process-conditioned encoding + per-process superposition, NO replay yet") is
brain-faithful ONLY for facts that fall under a strong, pre-seeded process schema. For anything
outside a seeded schema, "no replay yet" will NOT produce genuine fade/consolidation** -- it will
reproduce exactly the flat-side-table-annotation failure mode the 2026-07-28 and 2026-08-10 audits
already diagnosed for the unrelated generic-fact-acquisition loop, now independently confirmed from
the causal-replay-necessity literature rather than from a code audit.

**(3) Schema-gated fast consolidation is a REAL, causally-demonstrated, precisely-characterized
mechanism (Tse et al. 2007/2011 PRE paradigm; SLIMM, van Kesteren et al. 2012) -- and it carries a
causally-demonstrated LIABILITY (Warren et al. 2014: vmPFC lesions REDUCE schema-driven false
recall, i.e. the same causal node responsible for useful fast assimilation is required for its
false-memory cost) that maps EXACTLY onto the false-memory guard our `grounding_acquisition_
loop.py::schema_consistency_split_half` already implements, citing the same Warren et al. 2014 paper
-- this drill upgrades that citation from an analogy to a mechanistically-precise match: the guard
is not decoration, it targets the literal circuit-level liability the schema-fast-track mechanism
carries.**

Concrete, verified-on-disk structural gap this drill names as the cheapest, most load-bearing fix:
**`hdlab/hd_fact_store.py`'s `FACT_ROLES = ("REL", "ARG0", "ARG1", "SOURCE", "TRUST")` has no
CONTEXT/PROCESS role, and its `sr_key(subject, relation)` conflict-detection key does not include
one either.** Two same-relation facts about the same subject in two different processes (e.g.
`water HAS_FATE moved` vs `water HAS_FATE created`) hit the store's FUNCTIONAL-cardinality path and
get FLAGGED as an unresolved contradiction -- confirmed by reading `store()`'s conflict-resolution
logic directly -- rather than coexisting as separable, context-addressable facts. This is the
literal, on-disk, present-today instance of "the naive learner stores water -> fate and averages."

**MID-DRILL UPDATE (coordinator sharpening, empirical result landed): the build already tested
this section's core prediction and CONFIRMED it, then moved the wall.** `exp_bootstrap_fhrr_
superposition_fade_v3` (disk-VET'd, `data/exp_bootstrap_fhrr_superposition_fade_v3/metrics.json`)
built exactly the sharded-by-process FHRR superposition register this drill's Section 4b
recommends (bind+bundle, unbind+cleanup, `fhrr_dim=4096`, sharded per process) and measured
**retrieval self-consistency 0.9556 (215/225)** -- `water@water_cycle=MOVE` and
`water@respiration=DESTROY` provably coexist in distinct registers, confirmed across THREE
independent storage mechanisms (v1 symbolic trust-resolution, v2 (entity,process)-dict, v3 FHRR
superposition), all reproducing the identical `reading_only` recall (~0.0968) with no fade in any
of the three. **Storage/averaging is empirically ruled out as the bottleneck -- Section 1's
faithfulness verdict is now DISK-CONFIRMED, not just literature-argued.** The wall moved fully
upstream to ACQUISITION: `exp_bootstrap_process_conditioned_reading_fade_v2` found **85.55%
(3326/3888) of fate-statements in general science prose carry NO taggable process signal at the
sentence level** (skipped, not mis-tagged), and sentence/keyword-level process-tagging on the
remainder is only **71.67% accurate** (86/120 hand-checked; dominant error = keyword-latching,
e.g. "combustion engine" tagged as process=combustion when the sentence is not actually about
combustion). Reading therefore EXTENDS entity coverage but cannot RE-DERIVE the seed's
process-conditioned precision -- a HARD_FAIL, honestly diagnosed as `PARTIAL_BOOTSTRAP`, not a
storage failure. **Section 5 (new, below) directly answers the sharpened rescue question this
result raises: how does the brain acquire context/process-conditioned knowledge from language when
individual sentences don't restate the context?**

---

## 1. CONTEXT-BINDING / CONJUNCTIVE CODING -- precise mechanism, faithfulness verdict, capacity

### 1a. The circuit (classic + modern)

- **Lateral entorhinal cortex (LEC, "what"/item) vs medial entorhinal cortex (MEC, "where"/context)
  parallel input streams converging on hippocampus**: Hargreaves, Rao, Lee & Knierim (2005,
  *Science* 308:1792) -- MEC units show strong stable spatial tuning, LEC units track
  object/non-spatial identity with weak spatial specificity. Refined by Deshmukh & Knierim (2011,
  *Front. Behav. Neurosci.* 5:69): LEC neurons DO acquire spatial firing when discrete objects are
  present (a landmark-anchored signal, not a pure item code) -- the LEC/MEC split is a dissociation
  of emphasis, not an absolute double dissociation. Knierim, Lee & Hargreaves (2006, *Hippocampus*
  16:755) frames the parallel-stream-convergence picture explicitly.
- **CA3/CA1 as the conjunction site**: the standard inference in the field, well-supported by the
  anatomy but -- important honesty flag from the lit-scan -- I could not find a single decisive
  experiment showing a CA3/CA1 cell's firing is literally the algebraic conjunction of an
  LEC-item signal and an MEC-context signal, vs. merely correlating with both. Treat "CA3/CA1 =
  conjunction site" as well-supported but still model-inferred, not a directly-proven single-cell
  fact.
- **Dentate gyrus pattern separation** (orthogonalizing sparse recoding BEFORE CA3 storage): Marr
  1971 (foundational proposal); O'Reilly & McClelland 1994 (*Hippocampus* 4:661) -- the key
  mechanistic account: sparse random EC->DG->CA3 projections + strong feedback inhibition produce
  sparse randomized conjunctive codes, and pure Hebbian LTP alone IMPROVES completion but DEGRADES
  separation -- heterosynaptic LTD is required to keep separation high (this is a precise,
  frequently-missed point: separation and completion are in tension, and the brain needs BOTH LTP
  and LTD to get both). Leutgeb, Leutgeb, Moser & Moser (2007, *Science* 315:961) -- in vivo
  confirmation of a DUAL mechanism: DG rate-remapping decorrelates for SMALL environmental changes,
  CA3 recruits wholly non-overlapping assemblies for LARGE changes. Bakker, Kirwan, Miller & Stark
  (2008, *Science* 319:1640) -- human fMRI confirmation localizing pattern separation to
  combined CA3/DG (resolution cannot separate the two regions). Yassa & Stark (2011, *Trends
  Neurosci.* 34:515) -- synthesis review; flag that later work shows pattern-separation
  MEASUREMENT is method-dependent (orthogonalization vs. decorrelation vs. spike-distance metrics
  disagree in places) -- the qualitative conclusion (DG separates) is consensus, the precise
  metric is contested.
- **CA3 as autoassociative attractor performing pattern completion**: Marr 1971; McNaughton &
  Morris (1987, *Trends Neurosci.* 10:408) -- CA3's dense recurrent collaterals (~2-4% connectivity
  among CA3 pyramidal cells in rodent) implement an attractor network. Rolls (2013, *Front. Cell.
  Neurosci.* 7:98) -- modern quantitative synthesis, explicit Hopfield-like treatment. Nakazawa et
  al. (2002, *Science* 297:211) -- CA3-NMDAR knockout mice show impaired pattern COMPLETION
  (recall from partial cues) with intact ENCODING -- the best available causal (not just
  theoretical) evidence that CA3 specifically does completion, separable from encoding.

### 1b. Verdict: is "bind then superpose then inverse-bind+cleanup" a faithful model?

**Yes, at the Marr-algorithmic level, with three corrections that make it non-toy.**

The abstraction itself has real theoretical-neuroscience lineage, not just an ML borrowing:
Smolensky (1990, *AI* 46:159) tensor-product variable binding is the origin of literal
outer-product role-filler binding; Plate (1995, *IEEE TNN* 6:623; *Holographic Reduced
Representation*, 2003) is the circular-convolution/superposition/cleanup formalization that is
close to exactly what the task's hypothesis describes. Rolls & Treves' theoretical capacity work
(below) explicitly treats CA3 as a Hopfield-type associative memory -- and a Hopfield net's stored
associations ARE mathematically a superposition of outer products, i.e. structurally the same
object as a rank-limited tensor-product VSA. The current state-of-the-art, directly hippocampal,
2025 instantiation: **Chandra, Sharma, Chaudhuri & Fiete (2025, *Nature*), "Episodic and associative
memory from spatial scaffolds in the hippocampus" (Vector-HaSH)** -- entorhinal grid-cell modules
provide a fixed low-dimensional SCAFFOLD, content is bound to scaffold states via plastic
associative projections, retrieval uses error-correcting attractor dynamics, and the model is
explicitly built to give a GRACEFUL capacity/fidelity tradeoff (avoiding the classic Hopfield
"memory cliff"). This is the best current literature match to a scaffolded, brain-grounded
bind+superpose+attractor-cleanup account and is directly relevant to the sharding-vs-global-register
design choice below (Section 4).

Three named breakdown points / corrections, all with direct substrate implications:

1. **The real brain does not do a literal dense outer-product/convolution over full-width item and
   context vectors.** It uses SPARSE RANDOM conjunctive coding -- each DG/CA3 cell fires for a
   random, low-order conjunction of a HANDFUL of input features (O'Reilly & McClelland 1994's
   model), not a full algebraic product of two dense vectors. Literal tensor-product binding's
   dimensionality blowup with recursion depth is explicitly flagged in the VSA literature as
   impractical; the brain's actual solution is sparsity, not a bigger tensor. **Substrate
   correction: the bind(entity, context) operation must feed into a DG-style expand-then-sparsify
   stage (`hdlab.hippocampal_encoder.DGProjection`) BEFORE being bundled/stored, not be bundled raw.
   This organ exists, is certified, and has ZERO callers -- confirmed by grep this session.**
2. **Real CA3 retrieval is a unified iterative attractor-relaxation process (energy-descent
   settling), not two discrete algorithmic steps (algebraic inverse-bind, then a SEPARATE
   nearest-neighbor cleanup).** McNaughton & Morris 1987; Rolls 2013; Nakazawa et al. 2002's
   NMDA-dependence finding specifically supports a dynamical, not purely algebraic, completion
   process. **Substrate correction: retrieval from a context-bound conjunctive store must use
   `hdlab.cleanup_family.iterative_attractor` (confirmed genuinely iterative this session: settles
   over `max_steps` with a `converged` flag, softmax-weighted, own docstring cites Treves-Rolls) --
   NOT `hd_fact_store._cleanup()`, which is confirmed on disk to be a single-shot
   `argmax(codebook @ query)`, the exact "two discrete steps" shape the literature flags as the
   biggest fidelity mismatch.**
3. **The learning rule is one-shot NMDA-dependent Hebbian LTP for storage plus heterosynaptic LTD
   for separation, not a clean linear vector sum with no interference structure of its own.**
   MEDIUM-HIGH confidence, less directly substrate-actionable than (1)/(2) at this drill's scope --
   flagged for completeness, not a near-term build item.

### 1c. Capacity: how many (entity, context) conjunctions before interference?

**The formal result** (Treves & Rolls 1991, *Network* 2:371, "What determines the capacity of
autoassociative memories in the brain?"; Treves & Rolls 1994, *Hippocampus* 4:374): for a
sparsely-coded, partially/diluted-connected autoassociative network, storage capacity scales
**p_max ~ C / (a * ln(1/a))**, where C = recurrent connections PER CELL (not total neuron count N)
and a = the fraction of active units (sparseness). This is a superlinear-in-sparsity result --
driving `a` toward zero buys far more than a proportional capacity gain, which is the formal reason
DG/CA3's ~2-5% activity level is load-bearing, not incidental. Contrast: the classic DENSE Hopfield
result (Amit, Gutfreund & Sompolinsky 1987, *Annals of Physics* 173:30) gives capacity ~0.14*N for
~50%-active patterns with a SHARP catastrophic collapse (spin-glass transition) past that loading
ratio -- capacity failure in these networks is a CLIFF, not graceful degradation. Rolls (2013)
applies the sparse formula to real CA3 parameters (recurrent connections per cell C_RC ~ 12,000 in
rat, sparseness a ~ 0.02-0.05) and gets an order-of-magnitude estimate around **p_max ~ 10^4** (the
paper's own worked example lands near ~36,000 under specific simplifying assumptions) -- **explicitly
flagged by the paper itself, and by this drill, as an illustrative theoretical estimate under
uncorrelated-random-pattern assumptions, not a directly-measured biological count; real episodic
conjunctions are far from uncorrelated, which changes effective capacity in either direction.**

**Applying this to our own already-declared config** (illustrative only, same honesty caveat as
above -- this is a back-of-envelope sanity check, not a validated prediction): `hippocampal_encoder.
DGProjection`'s own docstring example uses `dg_dim=8192` at `sparsity~0.01-0.03`. Our
`CA3AutoAssociator` is currently a FULLY DENSE `dg_dim x dg_dim` outer-product matrix (confirmed on
disk), which is closer to C = dg_dim (full connectivity) than to real CA3's diluted ~2-4%
connectivity -- meaning our current implementation is MORE densely connected than biology, which
the Treves-Rolls formula says should raise nominal capacity (C larger) but the dense-Hopfield
cliff-sharpness result (Amit-Gutfreund-Sompolinsky) also applies more directly to a fully-connected
matrix than to a diluted one. Plugging dg_dim=8192, a=0.02 into p_max ~ C/(a*ln(1/a)) gives an
illustrative order-of-magnitude figure in the 10^4-10^5 range -- **this number should NOT be treated
as a validated ceiling for our substrate; it is a plausibility check that motivates the cheap
decisive test below, which measures the ACTUAL capacity-cliff shape on our own algebra rather than
assuming the idealized formula transfers.**

### 1d. How the brain avoids the ceiling (and what does/doesn't transfer)

(a) **Sparsity is the primary, well-established lever** -- already the dominant conclusion of the
2026-07-04 DG note; this drill supplies the formal WHY (Treves & Rolls' superlinear scaling) that
note's own empirical bracketing (K512 clears the target) did not have a theoretical law behind it.
(b) **Population-level orthogonalization (pattern separation), not literal separate anatomical
modules per content domain** -- important honesty flag: I found strong support for DG/CA3
pattern-separation as the mechanism that keeps unrelated conjunctions from competing for the same
representational real estate, but did NOT find support for the brain using distinct anatomical
"modules for unrelated content" as a SEPARATE mechanism from pattern separation itself. **This
matters for the sharding-vs-global-register design decision in Section 4**: sharding-by-context in
our substrate is a reasonable, cheap ENGINEERING approximation of what pattern separation achieves,
but should not be oversold as "the brain does this too" -- the brain achieves the same outcome
(non-interfering codes) within one recurrent structure via orthogonalization, not via separate
per-domain sub-hippocampi.
(c) **Systems consolidation as a capacity-management release valve** -- Treves & Rolls and Rolls
(2013) argue on FORMAL grounds that a fast, capacity-limited hippocampal buffer needs an
independent, larger, slower store (neocortex) to hold a lifetime of memories, with old hippocampal
traces expected to fade/be overwritten as capacity pressure mounts (heterosynaptic LTD literally
supports "new memories overwrite old ones" at the synaptic level). **Honesty flag: this is a
theoretical/computational argument, not something I found directly experimentally confirmed as the
in-vivo TRIGGER for consolidation timing** -- plausible and widely assumed, not independently nailed
down by a causal manipulation tying hippocampal capacity pressure specifically to consolidation
onset.

### 1e. Hippocampal indexing theory -- reframes what the capacity numbers are counting

**Teyler & DiScenna (1986, *Behav. Neurosci.* 100:147)** and **Teyler & Rudy (2007, *Hippocampus*
17:1158)**: the hippocampus does not store episode CONTENT -- it stores a compressed INDEX/pointer
into the distributed neocortical pattern that constituted the experience, and reprojects to
neocortex to reinstate that pattern on partial-cue retrieval ("the hippocampus itself does not
contain the content of an experience but it does provide an index that allows the content to be
retrieved" -- direct quote, Teyler & Rudy 2007). This reframes the Section 1c capacity numbers in a
load-bearing way (this specific bridging argument is this drill's own synthesis of two
separately-well-supported literatures, not a single directly-cited claim -- flagged accordingly,
lower confidence than the individual literatures it connects): if hippocampus stores INDICES, not
raw content, then p_max limits the number of distinguishable EPISODES/conjunctions taggable for
retrieval, not the amount of content each one carries -- which is a much better fit to extreme DG/CA3
sparsity given how much richer real episodic content is than a sparse code could hold directly.
**Direct substrate implication: the context-bound conjunctive register should store a compact
INDEX (a `fid`-style pointer) that resolves to the FULL fate/relation description in a separate,
larger, slower store (`hd_fact_store`, once given a CONTEXT role -- Section 4), not attempt to
carry the full content inside the superposition register itself.** This multiplies effective
capacity for free, because the superposition only needs to distinguish indices.

---

## 2. THE FADE / SYSTEMS CONSOLIDATION -- is replay necessary, or does accumulation suffice?

### 2a. The two classic theories, precisely, and the honest state of the debate

**Standard Consolidation Theory** (Squire & Alvarez 1995; Squire, Genzel, Wixted & Morris 2015,
*Cold Spring Harb. Perspect. Biol.*): hippocampus is a temporary store; ALL declarative memory
(including episodic) eventually becomes fully hippocampus-independent. Decisive supporting evidence:
**Ribot's law** -- temporally graded retrograde amnesia (recent memories impaired more than remote
ones after hippocampal damage). **Multiple Trace Theory / Trace Transformation Theory** (Nadel &
Moscovitch 1997; Winocur & Moscovitch 2011; Moscovitch et al. 2005/2016): episodic/contextually-rich
memory NEVER fully leaves the hippocampus (every retrieval creates a new trace); only
semantic/gist-level content migrates to cortex. Decisive supporting evidence: studies of remote
autobiographical memory in hippocampal patients showing a FLAT (non-graded) impairment for episodic
detail alongside relatively preserved semantic content (synthesized in Moscovitch et al. 2006, *Curr
Opin Neurobiol*).

**This debate is explicitly NOT resolved in the field** -- Sekeres, Winocur & Moscovitch (2018,
*Hippocampus*, "Has multiple trace theory been refuted?") directly engages the controversy; evidence
is mixed across methodologies (neuroimaging tends to favor MTT, lesion data favor-but-don't-conclusively
support it, some of MTT's sharper predictions are not consistently confirmed). Report this as a live
controversy, not a settled question, per the task's explicit ask to flag genuine debate.

**Semantic/episodic double dissociation within the same content** (directly relevant to the
water-cycle problem's "different processes" framing, since context here plays a role somewhat
analogous to episodic specificity): Vargha-Khadem, Gadian, Watkins, Connelly, Van Paesschen & Mishkin
(1997, *Science*) -- developmental-amnesia patients (perinatal bilateral hippocampal damage) show
NORMAL semantic/factual knowledge acquisition despite severely impaired episodic memory for the SAME
learning episodes. The complementary direction (semantic dementia: impaired semantic knowledge,
relatively preserved episodic recency memory, temporal-neocortex damage with hippocampus spared) is
reported in the semantic-dementia literature (Graham, Simons, Pratt, Patterson & Hodges-type
findings) -- MEDIUM confidence, this specific citation was recalled rather than independently
re-verified this cycle, flagged accordingly.

### 2b. Causal evidence that ACTIVE REPLAY specifically (not just elapsed time/sleep) matters

**Necessity (removing replay impairs consolidation despite matched time):**
- Girardeau, Benchenane, Wiener, Zugaro & Buzsaki (2009, *Nat. Neurosci.*) -- real-time closed-loop
  detection+disruption of sharp-wave ripples during POST-TRAINING REST impaired spatial-memory
  learning rate across days, with sleep architecture otherwise normal. Canonical, heavily replicated.
- Ego-Stengel & Wilson (2010, *Hippocampus*) -- within-subject replication, same design, same
  qualitative result.
- Jadhav, Kemere, German & Frank (2012, *Science*) -- disrupting ripples DURING AWAKE BEHAVIOR
  (not offline rest) also impairs learning, dissociable from the offline-rest effect -- ripples
  appear to serve at least two temporally/mechanistically distinct roles (Joo & Frank 2018, *Nat.
  Rev. Neurosci.* review frames this as an open, still-being-worked-out distinction, not settled).

**Sufficiency (inducing MORE replay causally improves retention, holding elapsed time fixed --
the cleanest available causal design):**
- Rasch, Buchel, Gais & Born (2007, *Science*) -- odor cue paired with learning, re-presented during
  subsequent slow-wave sleep, IMPROVES retention of the paired declarative memory vs. no-cue
  controls; effect specific to SWS (not REM/wake) and to hippocampus-dependent (not procedural)
  memory; cueing produces measurable hippocampal fMRI activation.
- Rudoy, Voss, Westerberg & Paller (2009, *Science*) -- WITHIN-SUBJECT, within-identical-sleep-bout:
  a subset of learned associations get sound-cued during SWS; cued locations are recalled MORE
  accurately than uncued locations from the SAME sleep period. This within-subject design is close
  to the cleanest possible isolation of "reactivation, not just sleep time" as the active ingredient.
- Bendor & Wilson (2012, *Nat. Neurosci.*) -- task-associated tones played during sleep causally
  BIAS WHICH TRAJECTORY hippocampal ensembles replay -- direct electrophysiological confirmation
  that TMR-style cues act by biasing hippocampal replay content itself.
- de Lavilleon, Lacroix, Rondi-Reig & Benchenane (2015, *Nat. Neurosci.*) -- optogenetic/closed-loop:
  triggering reward stimulation contingent on a specific place-cell's spiking DURING SLEEP was
  sufficient to install a novel, explicit, waking goal-preference for that location -- a memory
  CREATED purely by manipulating sleep replay content, with no corresponding waking reward
  experience. The single strongest available sufficiency demonstration.

**Theoretical/computational necessity argument (why interleaved replay specifically, not mere
accumulation, is required to avoid overwriting):** McClelland, McNaughton & O'Reilly (1995, *Psychol.
Rev.* 102:419) -- simulations show a single slow-learning distributed network catastrophically
forgets old associations when new ones are added UNLESS old material is interleaved with new during
training; this is presented as the direct computational reason biology needs two systems (fast
sparse hippocampus + slow interleaved-replay-trained cortex). Builds on McCloskey & Cohen (1989) and
French (1999, *Trends Cogn. Sci.*) establishing catastrophic interference as a generic property of
sequential (non-interleaved) training on any distributed/overlapping representation. Modern,
independent (non-biological, but structurally confirmatory) evidence: Robins (1995) pseudorehearsal;
Shin, Lee, Kim & Kim (2017, NeurIPS, "Continual Learning with Deep Generative Replay" -- explicitly
modeled on hippocampal replay); van de Ven & Tolias (brain-inspired generative replay reviews) --
all show empirically that INTERLEAVED (real or generated) replay of old material, specifically, not
just more training on new material, is what prevents catastrophic forgetting in artificial
distributed networks where naive sequential accumulation fails.

**Complications, both cited and honestly weighed:**
- Lesburgueres et al. (2011, *Science*) -- blocking a CORTICAL tagging process AT THE TIME OF
  ENCODING (not later, offline) also prevents eventual hippocampus-independent memory -- suggests
  the causally-necessary process may be partly an early cortical-tagging event concurrent with
  encoding, not exclusively later sleep replay; most likely complementary mechanisms, not competing
  ones.
- Tse et al. 2007/2011 (Section 3 below) is itself evidence for the OTHER side: when a strong
  pre-existing schema exists, new congruent memories become hippocampus-independent in ONE trial,
  vastly faster than the normal replay-dependent timeline -- genuine evidence that SOME route to
  consolidation needs much less replay dosage than the general/default case.
- No study has run the maximally clean test (chronic, complete replay suppression across weeks, PLUS
  unlimited massed passive re-exposure, testing whether hippocampus-independent memory can still
  eventually form some other way) -- this remains an open empirical gap in the literature itself,
  not just in our own KB.

### 2c. Verdict

**MEDIUM-HIGH confidence: replay is necessary for the GENERAL/default route to hippocampus-cortex
consolidation** -- multiple independent causal designs (ripple disruption, TMR, optogenetic
content-manipulation) converge, and the CLS-theoretic mechanism for WHY (avoiding catastrophic
interference) is independently corroborated by the modern ML generative-replay literature. **This is
NOT a universal law without exception**: Section 3 shows a real, causally-validated FASTER route
exists specifically for schema-congruent material. Given our plan is explicitly "process-conditioned
encoding + per-process superposition, NO replay yet," **the honest, precise verdict is conditional,
not a flat yes/no**: brain-faithful and likely SUFFICIENT for facts that fall under a strong,
pre-seeded process schema (the fast track, Section 3); NOT brain-faithful, and NOT expected to
produce genuine hippocampus-independent consolidation, for facts outside any pre-seeded schema (the
slow track) -- for that slice, replay-consolidation is the load-bearing missing piece, not an
optional refinement, and this drill's causal-literature review upgrades the 2026-07-28 note's
"recalled from general knowledge, not re-verified" replay-necessity claim to a citation-verified one.

---

## 3. SCHEMA-GATED FAST CONSOLIDATION -- precise mechanism (Tse et al., mPFC, indexing theory)

### 3a. The PRE paradigm, precisely

Tse, Langston, Kakeyama, Bethus, Spooner, Wood, Witter & Morris (2007, *Science* 316:76,
"Schemas and Memory Consolidation"): rats learned a flavor-place paired-associate schema (each of
six flavors always buried at a FIXED spatial location) over ~15-20 sessions across roughly a month
-- this schema-BUILDING phase is slow and hippocampus-dependent (lesions during this phase impair
it). Once the schema was established, NEW flavor-place pairs (novel flavors, novel locations, but
following the SAME "flavor goes with a fixed place" structural rule) were learned in **a single
trial**, and hippocampal lesions given as early as **48 hours** after that one-trial learning left
the new memory intact -- i.e. it had already become hippocampus-independent, vastly faster than the
normal weeks-long timeline. Tse et al. (2011, *Science* 333:891, "Schema-Dependent Gene Activation
and Memory Encoding in Neocortex") used the same paradigm with a molecular readout: rapid,
learning-locked up-regulation of the immediate-early genes **Zif268/Egr1 and Arc specifically in
prelimbic medial prefrontal cortex** (later work, Wang, Tse & Morris 2012, *Learning & Memory*,
extends the same rapidly-activated network to retrosplenial cortex and anterior cingulate cortex)
accompanied one-trial schema-congruent learning -- a fast neocortical engram-allocation signature at
the time of encoding, not the normal delayed post-consolidation gene-expression timeline.

### 3b. mPFC's computational role

**SLIMM** (Schema-Linked Interactions between Medial prefrontal and Medial temporal regions; van
Kesteren, Ruiter, Fernandez & Henson 2012, *Trends Neurosci.* 35:211): ventromedial PFC detects
"resonance" -- congruence between new input and an existing cortical schema. Schema-congruent
information is proposed to be encoded largely DIRECTLY into cortex via this vmPFC-gated route,
bypassing the need for a full, slow, independent hippocampal-episodic trace; incongruent/novel
information takes the standard hippocampus-dependent slow route. van Kesteren, Fernandez, Norris &
Hermans (2010, *PNAS* 107:7550) -- hippocampal-vmPFC functional connectivity during encoding of
schema-congruent material is elevated and PERSISTS into post-encoding rest, consistent with vmPFC
acting as an integration hub from the moment of encoding for congruent items (correlational
connectivity evidence, not a direct causal trial-by-trial demonstration that encoding-time vmPFC
activity SETS the speed of subsequent hippocampal independence -- flagged as inferred/interpretive
extension, not a directly-measured causal link). Preston & Eichenbaum (2013, *Curr. Biol.* 23:R764)
and Gilboa & Marlatte (2017, *Trends Cogn. Sci.* 21:618) synthesize a distributed
vmPFC-hippocampus-angular-gyrus network for schema instantiation generally.

### 3c. Hippocampal indexing theory's connection to schema-gated speed

The literature does NOT contain a direct quantitative demonstration that the hippocampal index
itself is physically smaller/simpler for schema-congruent vs. schema-incongruent items -- this is a
well-motivated theoretical extension of Teyler & DiScenna/Teyler & Rudy's indexing theory (Section
1e) combined with the Tse/SLIMM empirical findings, not a directly-measured result. Flagged
explicitly as inferred synthesis, consistent with this drill's calibration discipline.

### 3d. The liability: schema-assimilation causes false memory, via the SAME circuit

Bartlett (1932, "War of the Ghosts") is the classic behavioral precedent: schema-driven recall
systematically assimilates unfamiliar detail into familiar structure, distorting memory. The DRM
paradigm (Deese 1959; Roediger & McDermott 1995) is the modern lab analogue -- semantically related
word lists produce high-confidence false recall of a non-presented, gist-consistent lure. The
causal, circuit-level link to schema-fast-consolidation specifically: **Warren, Jones, Duff et al.
(2014, *J. Neurosci.* 34:7677)** -- patients with focal VENTROMEDIAL PFC LESIONS show significantly
REDUCED schema-driven false recall (fewer DRM intrusions) compared to healthy controls and to
patients with damage elsewhere. This directly implicates the SAME vmPFC node SLIMM proposes as the
schema-congruence gate as CAUSALLY NECESSARY for the false-memory liability -- you cannot easily get
the useful fast-assimilation benefit without the same circuit's over-generalization risk; Warren et
al. (2018, *J. Neurosci.* 38:3767) extends this to normal associative-inference/integration deficits
under vmPFC damage. Gilboa & Marlatte (2017) state this explicitly: schemas "can enhance OR distort
mnemonic processing from the outset" via the same mechanism.

### 3e. Verdict and direct substrate implication

**Yes, causally demonstrated (not just theoretically plausible): a well-formed schema (= our SEED)
should make reading-acquired congruent facts consolidate measurably faster and cleaner than
schema-incongruent facts of otherwise-matched difficulty.** This is a real, precisely-characterized,
lesion-validated mechanism, not a loose analogy. **Equally causally demonstrated: this fast-track
mechanism carries a specific false-memory risk that must be independently gated, not assumed safe
because voting/consistency looks fine.** Our `hdlab/grounding_acquisition_loop.py::schema_
consistency_split_half` guard, which already cites Warren et al. 2014 (per the 2026-07-28/08-09
notes), is now confirmed by this drill to target the EXACT circuit-level liability the neuroscience
identifies, not merely an analogous-sounding citation -- this upgrades that guard from "well-motivated
design choice" to "mechanistically required, per the same causal literature that validates the
fast-track benefit."

---

## 4. MAP TO SUBSTRATE + NAME THE GAP -- concrete build recommendation

### 4a. What to store

`bind(ENTITY, CONTEXT) -> bundle-of-bound(ROLE, FATE)` facts, where CONTEXT = a process/schema
identifier (`"water_cycle"`, `"respiration"`, etc). **Concrete, surgical fix**: extend
`hdlab/hd_fact_store.py`'s `FACT_ROLES` tuple to include a `CONTEXT` role, and change `_sr_key`
(currently `f(subject, relation)`) to `f(subject, relation, context)`. This is a role addition + a
key-function change -- it reuses 100% of the existing `store()`/`query()`/conflict-resolution
machinery untouched, and it is the literal fix for the concrete, verified-on-disk failure this
drill's HEADLINE names: two same-(subject,relation) facts from different contexts currently collide
in the FUNCTIONAL-cardinality path and get FLAGGED as an unresolved contradiction instead of
coexisting as separably-queryable, context-addressed facts.

### 4b. How to shard (Section 1d's honesty flag, made into a decision)

**Recommend sharding by context as the practical substrate implementation** (separate `sr_key`
partition per context, per 4a) -- cheap, guarantees zero cross-context crosstalk BY CONSTRUCTION,
and matches "context/process is a real, given partition boundary" in this specific problem. Per
Section 1d, this should be understood explicitly as an ENGINEERING approximation of what DG/CA3
pattern separation achieves via population-level orthogonalization within one recurrent structure --
NOT a claim that the brain has literally separate per-context sub-hippocampi (no evidence found for
that). **Keep a single, DG-expanded, globally-superposed conjunctive register (composing
`DGProjection` + `CA3AutoAssociator`, sized against the target (entity,context) pair count via the
Treves-Rolls formula, Section 1c) as the harder, more brain-faithful fallback if cross-context
generalization/transfer is later required** (e.g. "does X's fate transfer to a structurally similar
but previously-unseen process?") -- sharding forecloses that question by construction; a single
conjunctive superposition with cleanup does not.

### 4c. Whether/how to wire replay -- the two-route design, now causally justified

**FAST TRACK (schema-congruent, Section 3):** when a reading-acquired (entity, context, fate) fact
matches a PRE-SEEDED process schema's expected relation-type/role pattern (reuse `hdlab.learner`
MDL / `script_grain_acquisition_loop.ScriptLibrary`'s schema-clustering to test congruence),
promote toward "native" after 1-2 confirmatory exposures, not the full replay-budget route --
mirrors Tse et al.'s one-trial finding precisely. **MANDATORY gate**: `schema_consistency_split_
half` (already built) -- per Section 3d/3e this is not optional, it targets the exact liability the
neuroscience identifies for this specific pathway.

**SLOW TRACK (schema-incongruent / no matching schema):** route through
`hdlab.hippocampal_encoder.cls_discrete_budget_consolidate` -- discrete-budget offline replay with
SWR-style partial-cue reactivation, CA3-completion, and interleaved old/new draw from a shared
budget -- already CERTIFIED (HARD_PASS, `exp_cls_ca3complete_consolidation_v1`, commit 92e01cf3f)
and confirmed this session to STILL have zero callers outside its own module. Per Section 2c, a
single-fold/vote-margin bank (the current shape of every acquisition loop in this codebase) is NOT
expected, on causal grounds, to produce genuine hippocampus-independent consolidation for
schema-incongruent context-bound facts -- this is the load-bearing missing piece for that slice, not
a nice-to-have. This composes directly with, and sharpens, the identical wiring gap the
2026-07-28 and 2026-08-10 audits already found (for unrelated generic single-fact acquisition) --
now doubly motivated: once by code-audit precedent, once by this drill's causal-replay-necessity
literature.

### 4d. Retrieval-primitive correction

Any query against a context-bound conjunctive store should use `hdlab.cleanup_family.
iterative_attractor` (confirmed genuinely iterative, matches CA3 dynamics), not `hd_fact_store.
_cleanup()`'s current single-shot argmax -- Section 1b's fidelity correction #2, concretely
actionable and cheap (a call-site swap, not a new primitive).

---

## 5. THE ACQUISITION RESCUE -- discourse-level context maintenance, not sentence-level tagging

**Sharpened question (coordinator, mid-drill, directly answered here with a dedicated lit-scan):**
storage is solved. The wall is that no-LLM sentence-level reading cannot reliably tag which process
a fate-statement belongs to, because most sentences don't restate it. **How does the brain solve
this?** The hypothesis to confirm/refute/refine: the brain does NOT tag each sentence independently
-- it maintains the ACTIVE CONTEXT across a coherent passage (a sustained situation/discourse model)
and binds every fact encountered while that context is active to it, resetting only when a
discontinuity is detected. **Verdict: CONFIRMED, precisely, with a directly-applicable formal
model and clean neural evidence at three levels (discourse-theoretic, cortical, hippocampal).**

### 5a. The situation/discourse model supplies the context (and persists by default)

**Kintsch's Construction-Integration model** (Kintsch 1988, *Psychol. Rev.* 95:163; van Dijk &
Kintsch 1983): three representational levels (surface, textbase, situation model); the situation
model is explicitly the cross-sentence-coherence layer. Mechanistically, CI processes text in
cycles (roughly clause-by-clause), and each new cycle's associative network is built from the
incoming propositions PLUS a small set of most-activated propositions carried over from the
previous cycle's short-term buffer -- this IS the literal mechanism for "interpret the new sentence
against the maintained model," not sentence-isolated classification. Ericsson & Kintsch (1995,
*Psychol. Rev.* 102:211, "Long-term working memory") extend this: skilled comprehenders build
retrieval structures in LONG-TERM memory cued by a small active working-memory set, letting context
persist across a WHOLE passage (not just adjacent sentences) despite short-term capacity limits --
directly explains how "respiration" stays the active context many sentences after it was last named.

**Zwaan & Radvansky's Event-Indexing Model** (1998, *Psychol. Bull.* 123:162): readers track up to
five situational dimensions (time, space, protagonist/entity, causation, intentionality); a new
sentence is checked against the CURRENTLY-ACTIVE values on each dimension, and reading-time cost
scales with how many dimensions must CHANGE -- the empirical signature is "no change = no cost,"
which is the behavioral fingerprint of DEFAULT persistence, updated only on a signaled
discontinuity (this exact default-persistence wording is MEDIUM confidence -- verified via a
secondary synthesis, not a primary-text quote this cycle, but the underlying reading-time-cost
finding it rests on is HIGH confidence and well-replicated). The domain-general version of the same
claim, Event Segmentation Theory (Zacks, Speer, Swallow, Braver & Reynolds 2007, *Psychol. Bull.*,
already in this project's KB via the ProPara drill): a stable event/situation model persists until
a PREDICTION-ERROR spike signals a new event -- persistence is the default, not per-sentence
reclassification.

**Directly quantitative extension to continuous text (the single strongest citation for this
section)**: Howard, Shankar & Jagadisan (2011, *Topics in Cognitive Science* 3:48, "Constructing
semantic representations from a gradually-changing representation of temporal context") extend the
Temporal Context Model (Howard & Kahana 2002, *J. Math. Psychol.* 46:269 -- context is a slowly-
drifting vector, bound to each item at encoding) into a predictive form applied to CONTINUOUS
NATURAL TEXT, not word lists. They explicitly fit a cross-sentence context-drift rate that is
reliably NONZERO and LESS than a full reset -- i.e., **context does not reset at sentence
boundaries**; information flows forward. This is a formal, fitted, quantitative model of precisely
the phenomenon this rescue needs: a persisting, gradually-updating context vector that binds
incoming facts without requiring each sentence to restate it.

### 5b. Neural implementation: sustained cortical state + hippocampal drifting-context signal

**PFC as the top-down context-maintenance/bias signal**: Goldman-Rakic (1995, *Neuron* 14:477) --
canonical delay-period persistent activity, PFC actively HOLDS a representation across a temporal
gap. Miller & Cohen (2001, *Annu. Rev. Neurosci.* 24:167) -- PFC maintains goal/context/task-rule
patterns and issues top-down bias signals to posterior regions, shaping which inputs get
preferentially processed -- the general cognitive-control mechanism for "maintained context biases
interpretation of new input."

**Discourse-scale cortical evidence (the sharpest modern match)**: Baldassano, Chen, Zadbood,
Pillow, Hasson & Norman (2017, *Neuron* 95:709) and Baldassano, Hasson & Norman (2018, *J.
Neurosci.* 38:9689, "Representation of Real-World Event Schemas during Narrative Perception") --
naturalistic narrative fMRI shows a HIERARCHY of event timescales; high-order regions (angular
gyrus, posterior medial cortex, DMN/mPFC-adjacent areas) hold a STABLE multivariate activity
pattern that persists across an ENTIRE MULTI-SENTENCE EVENT and shifts abruptly only at event
boundaries. This is the clearest available neural signature of a sustained, multi-sentence "current
situation" state -- extending Miller & Cohen's single-item WM bias account to the discourse scale
(this specific extension/framing is this drill's own synthesis connecting the two literatures, not
a claim either paper states in those terms -- flagged accordingly, though each literature
individually is HIGH confidence).

**Hippocampal drifting-context / time-cell signal**: MacDonald, Lepage, Eden & Eichenbaum (2011,
*Neuron* 71:737, "Hippocampal 'time cells' bridge the gap in memory for discontiguous events") --
hippocampal neurons fire in a chaining sequence across the temporal gap between related events,
remapping when interval duration changes. Manns, Howard & Eichenbaum (2007, *Neuron* 56:530,
"Gradual changes in hippocampal activity support remembering the order of events") -- a GRADUALLY
DRIFTING hippocampal ensemble pattern (not discrete time-locked cells) serves as a slowly-changing
context signal bound to each new event, and the drift itself predicts later memory for event
ORDER -- the closest single citation to "a slowly drifting context state persisting across related
experience." Smith & Mizumori (2006, *Hippocampus* 16; *J. Neurosci.* 26:3154) -- hippocampal
neurons differentiate task-defined behavioral CONTEXTS/RULES even under matched spatial/sensory
cues, and firing tracks which abstract situation is currently in force -- the closest available
rodent analog to "which process/domain is currently active," not just literal elapsed time.

### 5c. Does replay reinstate the FULL context, or an isolated fact?

**Directly answered, HIGH confidence, and directly relevant to whether the SLOW/replay track
(Section 2/4c) can correctly consolidate a context-bound fact into the RIGHT schema slot**: Pacheco-
Estefan et al. (2019, *Nat. Commun.* 10:2255, "Coordinated representational reinstatement in the
human hippocampus and lateral temporal cortex during episodic memory retrieval") -- hippocampal
encoding-retrieval similarity was elevated ONLY for congruent item+context trials; the paper
explicitly reports **no evidence of item-specific, context-FREE reinstatement in hippocampus** --
that decontextualized signature was found instead in lateral temporal cortex. **Hippocampal
reinstatement (and by extension, replay) is inherently a JOINT item+context code, not an isolated
fact.** Convergent rodent evidence: Wilson & McNaughton (1994, *Science* 265:676) -- place-cell
PAIRS that fired together within one contextual experience show correlated reactivation in
subsequent sleep, i.e. reactivation preserves relational/contextual structure by construction (place
identity is itself context-defined). Foster & Wilson (2006, *Nature* 440:680) and Davidson,
Kloosterman & Wilson (2009, *Neuron* 63:497) -- replay reconstructs EXTENDED ordered trajectories
embedded in a task/spatial context, not single decontextualized units. **Verdict: replay-based
consolidation (Section 4c's slow track) should be expected to correctly preserve the (entity,
context)->fate binding through consolidation, provided the fact was correctly context-bound AT
ENCODING -- replay does not need a separate mechanism to "re-attach" context, but it also cannot
FIX a fact that was encoded without its context in the first place.** This sharpens Section 4c: the
acquisition-time binding (Section 5d/5e below) is upstream of and load-bearing for everything
downstream, including replay.

### 5d. Corpus-density/coherence: schema quality depends on BLOCKED, not scattered, exposure

**Direct, quantitative, modern, text-narrative evidence**: Beukers, Collin, Kempner, Franklin,
Gershman & Norman (2024, *Communications Psychology*, "Blocked training facilitates learning of
multiple schemas") -- using TEXT-NARRATIVE stimuli directly, blocked training (many coherent
same-domain stories presented consecutively) vs. interleaved (scattered) training on the SAME total
exposure count: blocked produced **88.4% vs. 59.3%** schema-test accuracy (d=1.81, p<.001). Their
latent-cause/event-segmentation account: coherent, contiguous same-domain exposure lets the learner
correctly SEGMENT experience into the right latent schemas; interleaving destroys the local
prediction-error signal needed to detect which schema is currently active, blurring schema
boundaries. **This is a direct, decisive answer to "is corpus density part of the answer": yes, and
specifically COHERENT-BLOCK density (many passages about the same process, encountered together),
not merely total sentence count scattered across topics.** Corroborating: Gick & Holyoak (1983,
*Cognitive Psychology* 15:1) -- a single analog story (even with an explicit stated principle)
largely FAILED to produce a transferable schema; TWO analogs let subjects spontaneously abstract a
transferable schema via comparison. Carvalho & Goldstone (2014, *Memory & Cognition*) -- blocked
study promotes abstraction of WITHIN-category commonalities (schema/prototype formation); interleaving
instead sharpens between-category discrimination -- schema formation specifically wants blocked,
same-domain density.

### 5e. Verdict on the hypothesis, and the concrete brain-faithful build rescue

**The hypothesis is confirmed, precisely, not merely plausible: the brain does discourse-level,
not sentence-level, context binding**, via (i) a situation-model layer that carries forward
activated content cycle-to-cycle by default (Kintsch/Zwaan-Radvansky, with a fitted, nonzero,
sub-reset cross-sentence drift rate -- Howard/Shankar/Jagadisan's pTCM), (ii) a sustained cortical
state (PFC bias signal generalized to a discourse-scale, multi-sentence-stable pattern in
high-order/DMN regions -- Miller & Cohen extended by Baldassano et al.), and (iii) a hippocampal
gradually-drifting context signal bound to each new item as it's encoded (Manns/Howard/Eichenbaum,
MacDonald et al., Smith & Mizumori) -- with (iv) replay preserving whatever item+context binding was
established at encoding (Pacheco-Estefan et al.), and (v) reliable schema formation itself requiring
coherent, blocked (not scattered) same-domain exposure density (Beukers et al. 2024; Gick & Holyoak
1983).

**Concrete brain-faithful build rescue, mapped to owned organs:**

Reading should be **PASSAGE-conditioned, not sentence-tagged.** Concretely: maintain a persistent
"active process/context" register across a passage, seeded/updated at PASSAGE-level discontinuity
boundaries (paragraph breaks, explicit topic shift, or a `SituationModel`-level discontinuity signal
-- reuse the SAME discontinuity-detection shape Zwaan-Radvansky/SEM name: fire on a
prediction-error/dimension-change spike, not on every sentence), and BIND EVERY FACT extracted while
that context is active to it -- rather than re-deriving the process independently, per sentence,
from local keyword cues (the `keyword`-tagger source of both the 85.55% skip rate and the dominant
keyword-latching error mode, confirmed in `design_gate_result.wrong_by_process`/`tagger_mix` in
`exp_bootstrap_process_conditioned_reading_fade_v2`'s own metrics: `keyword`=272/562 facts, the
LARGEST and WEAKEST source; `paragraph`=146/562, already the ProPara-oracle passage-level tagger and
qualitatively the right SHAPE, just not general-purpose or extended to non-oracle prose;
`frame_sentence`=30/562, smallest).

**Owned-organ mapping**: `hdlab/situation_reader.py::SituationReader.read()` already produces a
passage-scoped `SituationModel` (entities, events, timeline, causation) per document -- this is the
natural SEAT for a persistent context register; it does not currently carry one. `hdlab/situation_
model_accumulate.py::AccumulateRegister`/`CausalLinkRegister` already implements exactly the
"bundle of bound (role,event) pairs" accumulation Section 1's algebra needs -- extend its `add_event`
call (or a sibling method) to bind a CONTEXT key sourced from `SituationReader`'s currently-active
context, not re-derive context per-fact from local lexical cues. The existing `_select_matched`
paragraph-level tagger (`experiments/exp_propara_process_keyed_lookup_v1.py`, already the
`paragraph` source in the tagger mix) is the closest already-built PROTOTYPE of passage-level
context assignment -- it should be GENERALIZED from ProPara's oracle one-process-per-paragraph
structure to general prose (detect passage/context boundaries via discontinuity, not via an oracle
label), rather than treated as ProPara-specific. `hdlab/hippocampal_encoder.py`
(`DGProjection`+`CA3AutoAssociator`) and `cls_discrete_budget_consolidate` remain the correct
Section 4c slow-track consolidation organs for facts acquired this way -- per Section 5c, replay
does not need new machinery to preserve context, provided the context was bound correctly at
acquisition, which is exactly the piece this section fixes.

**The SINGLE most load-bearing change, named precisely**: replace the `frame_sentence`+`keyword`
sentence-level process-taggers (378/562 = 67% of current tagged facts, and 100% of the reason
71.67% tag accuracy and the keyword-latching error mode exist) with a **persistent
discontinuity-gated context register carried across sentences within a passage** (generalizing the
already-working `paragraph`/`_select_matched` shape beyond ProPara's oracle boundaries) that every
extracted fact binds to by default, updated only when a same-shape discontinuity signal fires --
this is a re-architecture of WHEN/HOW context is assigned (discourse-level, persistent,
default-carry-forward), not a new extraction algorithm, a new store, or a new consolidation
mechanism.

**Honest, falsifiable expectation, calibrated against Section 5d's corpus-density finding**: even a
correctly-built discontinuity-gated context register will not close the *coverage* half of the
85.55% skip rate for free -- SimpleWiki-style general prose is, per Beukers et al. 2024's own
distinction, closer to SCATTERED than BLOCKED exposure across processes (short articles, not long
coherent multi-passage treatments of one process) -- so this rescue's realistic ceiling is
**significantly higher process-tag ACCURACY on facts within a passage once a context is genuinely
active** (directly targeting the 71.67%->should exceed the 0.7 gate by a wide margin, since
discontinuity-gated carry-forward should eliminate most keyword-latching false-positives, which by
definition fire on isolated lexical cues rather than sustained context), rather than a full fix to
the skip rate itself, which is more a function of the corpus's passage-level coherence/density than
of the tagging mechanism. If the corpus lacks passage-level process-coherence altogether (single
disconnected sentences about a process with no surrounding coherent passage), NO mechanism -- brain
or substrate -- should be expected to recover reliable process-context from it, per Section 5a/5d;
this would be an honest, literature-predicted CEILING of the rescue, not a bug, and should be
reported as such rather than iterated against indefinitely.

---

## Cheap decisive test (ORIGINAL -- context-binding storage; SUPERSEDED, see note)

**Superseded by the actual build**: the test below was pre-registered before `exp_bootstrap_fhrr_
superposition_fade_v3` ran; that experiment IS this test, at real (not toy) scale, and confirmed
Prediction 1 (retrieval self-consistency 0.9556, far above the 0.85 `SEPARATES_MIN_SELFCONSIST`
band already in that cell's own `bands`). Retained below for the record and because the
capacity-cliff half of Prediction 2 was NOT run (mean_load=15, max_load=30 facts/register in the
actual run -- far below any plausible capacity ceiling, so the cliff-shape question remains open and
the test as designed is still the right one to run if/when register load grows). **The load-bearing
open test now is Section 5's acquisition rescue**, see the new decisive test immediately below this
one.

**Toy-scale, no GPU, reuses only already-certified organs -- validates the mechanism claims above
before any larger build commitment.**

Build a small synthetic set: 5-10 entities, each appearing in 3-5 distinct contexts, with a KNOWN,
genuinely CONFLICTING fate per (entity, context) pair for a subset of entities (e.g. "water":
water_cycle->MOVED, respiration->CREATED, combustion->CONSUMED) and non-conflicting fates for a
control subset (to check the test isn't trivially easy). Two arms:

1. **CONTEXT-BOUND arm**: `bind(entity_vec, context_vec)` fed through `DGProjection` (expand +
   sparsify) then bundled into a superposition register; retrieve via `iterative_attractor`
   settling against the (entity,context) codebook, then read off the bound fate.
2. **NAIVE arm** (the failure mode this whole drill targets): bundle each entity's fates across ALL
   its contexts with NO context key at all (the literal `AccumulateRegister`-without-context shape
   confirmed on disk today), retrieve by entity alone.

**Then, separately, a capacity-cliff check**: scale the number of bundled (entity,context)
conjunctions in the CONTEXT-BOUND arm's single global register from small (N=10) to large (N well
past the Section 1c illustrative estimate), holding `dg_dim`/sparsity fixed, and plot retrieval
accuracy vs. N.

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**HARD-PASS (both required):**
1. CONTEXT-BOUND arm retrieves the correct context-specific fate for >= 95% of (entity,context)
   pairs at small N (<=50 conjunctions), while the NAIVE arm's accuracy on the genuinely-conflicting
   subset is no better than a chance-adjusted baseline (<= 1/n_contexts-per-entity) -- confirms
   context-binding, not just "any retrieval," solves the disambiguation problem on our own algebra,
   not just in theory.
2. The capacity-cliff check shows retrieval accuracy staying >= 0.90 up to some N*, then dropping
   SHARPLY (not gradually) past N* -- reproduces the qualitative Hopfield/Treves-Rolls cliff shape
   (Section 1c) on our substrate's own geometry, and N* should move in the direction the formula
   predicts when `dg_dim` or sparsity is varied (order-of-magnitude match sufficient, not exact).

**HARD-FAIL (any one triggers, subject to a mandatory pre-check: hand-verify the conflicting-fate
subset genuinely produces different bound vectors per context before interpreting a null --
a flat result from a broken toy is a harness bug, not a mechanism verdict, per the standing
discipline):**
- The NAIVE arm ALSO disambiguates correctly (context leaks in via some unintended channel, or the
  toy's fates aren't actually context-dependent) -- fix the toy; not evidence against context-binding.
- The CONTEXT-BOUND arm fails to clear ~95% even at trivially small N=10 -- an implementation-level
  problem in our own bind/bundle/cleanup call composition (e.g. codebook too small/noisy, attractor
  not actually converging), not a theory rejection -- route to an implementation audit.
- Capacity degrades GRADUALLY rather than showing a cliff -- a genuine, informative negative about
  whether our DENSE (not diluted) `CA3AutoAssociator` matches the qualitative Treves-Rolls/Hopfield
  prediction; would motivate exploring a diluted-connectivity variant (closer to real CA3's ~2-4%
  recurrent connectivity, vs. our current full-dense `dg_dim x dg_dim` matrix) as a new, literature-
  motivated lever if capacity turns out to be the binding constraint at target scale.

**MIDDLE_BAND**: context-binding clears disambiguation but the capacity-cliff check is inconclusive
(e.g. N* too large to reach at toy scale) -- proceed with sharding (Section 4b) as the safe default
and defer the global-register capacity question until cross-context generalization is actually
needed.

---

## Cheap decisive test (NEW -- Section 5's acquisition rescue; this is the load-bearing one)

Build the discontinuity-gated passage-context register (Section 5e) as a thin addition to
`SituationReader`/`AccumulateRegister` and re-run the EXACT SAME held-out harness
`exp_bootstrap_process_conditioned_reading_fade_v2` already uses (same ProPara DEV oracle, same
no-leak guard, same `PROCTAG_ACC_GATE=0.7`, same 120-item hand-check sample) with ONE variable
changed: replace the `frame_sentence`+`keyword` sentence-level taggers with the passage-level
discontinuity-gated register, generalizing the existing `paragraph`/`_select_matched` mechanism
beyond ProPara's oracle paragraph boundaries. This is cheap (reuses the existing harness, corpus,
and hand-check protocol verbatim; the only new code is the context-register + discontinuity-gate
logic) and directly decisive (isolates whether discourse-level binding, not sentence-level tagging,
is the fix, exactly as Section 5 predicts).

## Falsifiable predictions (HARD-PASS / HARD-FAIL) -- acquisition rescue

**HARD-PASS (both required):**
1. Process-tag accuracy on the SAME 120-item hand-check protocol rises materially above the current
   0.7167 (target: clears the existing 0.7 gate by a wide margin, e.g. >= 0.85) -- per Section 5e's
   reasoning, discontinuity-gated carry-forward should eliminate most keyword-latching
   false-positives (which by construction fire on isolated lexical cues, not sustained context),
   this is the mechanism-specific prediction this rescue makes that sentence-level tagging cannot.
2. The skip rate (currently 85.55%, `n_skipped_no_process`/total) drops, but NOT to near-zero --
   per Section 5d's honest ceiling, expect a partial reduction (facts within an already-active,
   passage-coherent context should now resolve instead of being skipped; facts in genuinely
   scattered/incoherent single-sentence contexts should still, correctly, be skipped or abstained,
   not force-tagged). A near-total skip-rate collapse to ~0 would itself be suspicious (would
   suggest over-eager context-carry-forward mis-tagging facts that don't actually belong to the
   carried context) and should trigger a false-positive audit, not be read as an unqualified win.

**HARD-FAIL (any one triggers, subject to the mandatory pre-check: hand-verify the discontinuity
gate actually fires at real passage/topic boundaries in a small sample before interpreting a null --
a gate that never fires, or fires on every sentence, is a harness bug per the standing "flat result
= broken experiment" discipline):**
- Process-tag accuracy does not improve materially over 0.7167 -- would mean sentence-level lexical
  ambiguity was NOT the dominant error source (contrary to Section 5e's `wrong_by_process`-diagnosed
  keyword-latching pattern), and the substrate-application claim in this section's calibration
  (below) is falsified even though the underlying discourse-context-persistence NEUROSCIENCE
  (Sections 5a-5d) remains independently well-supported by the literature regardless of this
  substrate-specific result.
- The re-run fade/lesion/scramble harness (reusing Section 2/exp_bootstrap_fhrr_superposition_
  fade_v3's own bands: `RISE_MIN_ABS=0.05`, `FADE_GAP_MAX=0.05`, `FADE_RATIO_MIN=0.85`) STILL shows
  no fade even with materially improved tag accuracy and coverage -- would mean process-tagging
  precision was necessary but not sufficient, and the remaining gap is in the Section 4c
  fast/slow-track consolidation wiring (still unwired, per Section 4c) rather than in acquisition --
  a genuinely informative, mechanism-localizing negative, not an undiagnosed flat result.

**MIDDLE_BAND**: tag accuracy improves materially but the skip rate does not drop (passages in this
specific corpus are more scattered/less coherent than Section 5d's blocked-training precondition
requires) -- would confirm Section 5d's corpus-density ceiling specifically, and the correct next
action is sourcing/selecting a more passage-coherent corpus (per Beukers et al. 2024's blocked-vs-
interleaved distinction), not further tagger iteration on the same corpus.

---

## Cross-thread synthesis

- **Composes with, does not duplicate, `notes/research_drill_dentate_gyrus_pattern_separation_
  resolution_at_2pct_2026-07-04.md`**: that note found the expand-then-sparsify lever for pure
  ITEM resolution (K512 @ higher total_dim clears the target) empirically, without a capacity-law
  citation behind it. This drill supplies the formal WHY (Treves & Rolls' sparse-capacity scaling)
  and extends the SAME lever to ITEM x CONTEXT conjunctions specifically -- the two findings are the
  same mechanism (DG expansion) applied to two related but distinct binding problems (item alone vs.
  item-in-context), and should share one build, not two.
- **Sharpens `notes/consolidation_brain_fidelity_audit_and_redesign_2026-07-28.md`**: that note's
  consolidation-neuroscience citations are explicitly flagged "recalled from general knowledge, NOT
  re-verified against fresh sources... treat as reasoning aids, not VET'd literature." This drill's
  Section 2 supplies the causal-evidence verification that note lacked (Girardeau/Ego-Stengel/
  Jadhav/Rasch/Rudoy/de Lavilleon), confirms its central claim (replay is not optional, single-fold
  consolidation is structurally the wrong operation), and ADDS the schema-fast-track exception
  (Section 3) that note did not have -- the two-route (fast/slow) design in Section 4c is a direct,
  now-doubly-justified extension of that note's Section 3.1 "replay + schema-gate + surprise-priority"
  recommended composition.
- **Directly reconciles with, and upgrades, the 2026-08-10 crutch-fade cluster**
  (`research_crutch_design_and_generalization_2026-08-10.md`, `research_brain_scaffolding_that_
  fades_2026-08-10.md`, `research_crutch_fade_loop_owned_organ_wiring_2026-08-10.md`,
  `design_prelim_tier_staged_consolidation_crutch_fade_2026-08-10.md`): those notes independently
  found (via code-audit, not neuroscience-causal-literature) that BANK writes to a flat side-table
  dict, never a natively-read structure, and that `cls_discrete_budget_consolidate` sits certified
  and unwired -- the SAME finding this drill reaches from Section 2's causal-replay literature. The
  PRELIM/NATIVE 3-tier design already in flight (fast-track low-trust retain + accumulate +
  generalization-feed; strict promote gate to NATIVE) maps directly onto this drill's Section 4c
  fast/slow split, and Section 3's Tse-et-al causal validation gives that design's fast-tier a
  precise, literature-grounded justification for WHY combined-evidence-without-full-replay-dosage
  can legitimately cross a promotion gate for schema-congruent material specifically -- something
  the prior design note asserted architecturally (per USER direction) without this drill's causal
  backing.
- **Explicitly distinct axis from `notes/research_propara_content_driven_order_dependent_state_
  update_2026-08-10.md`**: that drill's finding (`state_t = f(state_{t-1}, content_t)`, sequential
  content-driven recurrence WITHIN one narrative) is about TEMPORAL/sequential update of a single
  entity's state across a passage. This drill's finding (item-IN-context conjunctive binding) is
  about DISAMBIGUATING the same entity ACROSS distinct processes/narratives. These are orthogonal,
  both real, and should compose: an entity's per-CONTEXT register (this drill) should itself be
  updated sequentially WITHIN that context via the content-driven recurrence the ProPara drill
  names, not overwritten or re-derived from scratch per mention.
- **Extends `notes/brain_whitening_decorrelation_pattern_separation_fidelity_2026-07-30.md`**: that
  drill established sparse-fan-in + post-projection divisive normalization (not PCA whitening) as
  the correct DG-analog front end; this drill's Section 4a's DG-expansion recommendation for
  context-binding should reuse that same corrected front-end design, not a naive whiten-then-expand
  pipeline.
- **Section 5 directly extends and resolves the open question in `notes/research_propara_content_
  driven_order_dependent_state_update_2026-08-10.md`**: that drill established `state_t =
  f(state_{t-1}, content_t)` as the brain-faithful shape for WITHIN-passage sequential state update
  (content-conditioned recurrence, not index arithmetic) but did not address WHERE the
  passage-level context itself comes from or how it persists across sentences that don't restate
  it -- Section 5a-5b supplies exactly that missing piece (Kintsch/Zwaan-Radvansky situation-model
  carryover + the discourse-scale cortical/hippocampal evidence), and the two findings now compose
  directly: an entity's per-CONTEXT register (this drill's Section 1/4) should be updated via the
  ProPara drill's content-driven recurrence WHILE that context is the currently-active one per
  Section 5's discontinuity-gated carry-forward, not re-derived per-sentence from local cues either
  way.
- **Directly grounded in, and now supersedes the speculative framing of, the mid-drill empirical
  result from `experiments/exp_bootstrap_fhrr_superposition_fade_v3.py` and `experiments/exp_
  bootstrap_process_conditioned_reading_fade_v2.py`** (both disk-VET'd, HARD_FAIL_PARTIAL_BOOTSTRAP
  verdicts, `data/exp_bootstrap_fhrr_superposition_fade_v3/metrics.json` and `data/exp_bootstrap_
  process_conditioned_reading_fade_v2/metrics.json`): these cells are what triggered this drill's
  mid-session sharpening (see the HEADLINE mid-drill update and Section 5) -- Section 1's
  faithfulness verdict for superposition-of-bound-pairs is now confirmed by that build (self-
  consistency 0.9556), and Section 5's acquisition rescue is designed as the direct next build this
  pair of cells' own honest diagnosis (`the_actual_wall_is_upstream`) calls for.

## Substrate-product implications

If the cheap decisive test HARD-PASSes, the product claim sharpens beyond "the system reads and
remembers" to **"the system correctly disambiguates what the SAME entity means across different
situations, with an auditable trace showing exactly which context licensed which fate"** -- directly
differentiating from a black-box embedding system, which has no mechanism to guarantee it isn't
silently averaging across contexts (the exact failure this drill's HEADLINE confirms is
structurally present in `hd_fact_store` TODAY). The capacity-cliff finding, if confirmed, also gives
the substrate a PRINCIPLED sizing rule (Treves-Rolls-derived, not just empirically re-discovered
each time) for how many context-bound facts one superposition register can safely hold before a
build needs to shard or expand -- directly reusable for every future context-dependent-knowledge
build, not just this one. If the schema-fast-track design (Section 4c) lands, it gives a second,
independently-causally-motivated fade curve (alongside the existing generic crutch-fade arc) with a
sharper, falsifiable prediction: schema-congruent facts should fade/promote MUCH faster than
schema-incongruent ones of matched difficulty -- itself a literature-precedented, testable,
demoable claim ("the system learns schema-consistent facts almost instantly, like a human given a
relevant analogy, and is appropriately slower and more cautious about facts that don't fit anything
it already knows").

**Section 5's acquisition rescue, if it clears its decisive test, is the sharper NEAR-TERM product
claim** (storage is already proven, this is the actual open gap per the mid-drill empirical
result): not "the system can store context-dependent facts without conflating them" (already true,
disk-confirmed, self-consistency 0.9556) but **"the system reads general prose the way a human
does -- holding the current topic in mind across a passage rather than re-guessing it from each
sentence's own words in isolation -- which is WHY it can correctly attribute an unstated-context
fact instead of either guessing wrong or silently discarding it."** This is a literature-grounded
architectural claim (Section 5a-5d), not an ad hoc heuristic, with a specific, cheap, already-
scoped falsifiable test (above) and a named honest ceiling (Section 5e's corpus-coherence caveat,
directly citing Beukers et al. 2024) that keeps the claim from being oversold if the underlying
corpus itself lacks passage-level coherence.

## Calibration (per [[feedback-lit-scan-calibration-penalty]])

**Important distinction, stated explicitly per the task's "accuracy is paramount" instruction: the
NEUROSCIENCE claims themselves (Sections 1-3) are HIGH confidence** -- these are well-established,
heavily-cited, mostly foundational-textbook findings (LEC/MEC dissociation, DG pattern separation,
CA3 attractor completion, Treves-Rolls capacity scaling, the replay-causality studies, the Tse et
al. PRE paradigm) verified via direct citation search this session, not recalled from memory
uncritically. Where the literature is genuinely contested (SCT vs. MTT, exact pattern-separation
measurement methodology, whether hippocampal capacity pressure specifically triggers consolidation
timing), this is explicitly flagged inline, not glossed over. **The calibration penalty applies to
Section 4's SUBSTRATE-APPLICATION claims specifically** -- whether these organs, composed this way,
on THIS problem, at THIS scale, will produce the predicted disambiguation and capacity-cliff
behavior is novel synthesis, capped at 0.50 and deflated further:

- P_deflated("superposition-of-bound-(entity,context)-pairs + DG-expansion + iterative-attractor-
  cleanup, composed as in Section 4, correctly disambiguates cross-context fates on the cheap
  decisive test") = **0.45** -- undeflated ~0.60 (the individual organs are each independently
  certified; the composition is new but low-novelty, mostly a call-site wiring problem, not a new
  algorithm); deflated for genuine uncertainty about whether `DGProjection`'s current dense
  `CA3AutoAssociator` (not diluted, unlike real CA3) behaves as the sparse-capacity formula predicts
  at our target scale.
- P_deflated("replay-consolidation, once wired per Section 4c's slow track, is the load-bearing fix
  for schema-incongruent context-bound fade") = **0.40** -- the causal literature strongly supports
  replay's necessity in the general case, but this specific substrate claim inherits the same
  four deflators the 2026-08-10 crutch-fade cluster already named for the parallel generic-fact
  case (untested fade mechanism even once wired, hollow-acquisition-loop precedent, open store-
  capacity-cliff adjacency risk) -- this drill does not resolve those, it adds causal-neuroscience
  weight to the underlying claim that replay matters, not new evidence that OUR specific wiring will
  work first try.
- P_deflated("the schema-congruent fast track, gated by schema_consistency_split_half, safely
  reproduces Tse-et-al-style near-one-trial promotion without reintroducing the Warren-et-al-2014
  false-memory failure mode") = **0.42** -- the neuroscience precedent for BOTH the benefit and the
  paired risk is unusually strong (causal lesion evidence on both sides, Section 3), which is why
  this is not deflated further; the substrate-specific uncertainty is whether our existing guard's
  cosine-based schema-consistency metric is a good enough proxy for the vmPFC "resonance" signal the
  literature describes, which is genuinely untested.
- **P_deflated("Section 5's discontinuity-gated passage-context register clears its HARD-PASS bands
  (tag accuracy >= 0.85, partial-not-total skip-rate reduction) on the exact re-run harness") =
  0.48** -- notably the HIGHEST substrate-application estimate in this note, deflated less than the
  others, for a stated reason: this is not a novel mechanism guess, it is a DIRECTED FIX of a
  root-caused, disk-diagnosed failure mode (`wrong_by_process`'s own dominant-error-mode field
  already names keyword-latching-on-isolated-lexical-cues as the problem, and Section 5's fix is
  structurally aimed exactly at that cause: replace isolated-cue tagging with sustained-context
  carry-forward) rather than a speculative new direction; undeflated estimate ~0.65, deflated to
  0.48 for genuine uncertainty about (a) whether `SituationReader`'s existing sentence/event
  segmentation gives a clean enough discontinuity signal on SimpleWiki-style prose (untested on
  this corpus) and (b) Section 5d's own honest caveat that SimpleWiki may simply be too scattered
  (non-blocked) a corpus for the skip-rate half of the prediction to move much, independent of
  whether the tagging-accuracy half succeeds. Per the mandatory novel-synthesis cap, still held at
  0.48, not raised to the undeflated estimate, despite the directed-fix argument for a smaller
  deflation than the other rows.

## Citations (verified count)

**Section 1 (conjunctive coding/capacity), verified via dedicated lit-scan sub-agent this session
(citations independently searched, not recalled from memory):** Hargreaves, Rao, Lee & Knierim 2005
*Science* 308:1792; Deshmukh & Knierim 2011 *Front. Behav. Neurosci.* 5:69; Knierim, Lee &
Hargreaves 2006 *Hippocampus* 16:755; Marr 1971 *Phil. Trans. R. Soc. Lond. B* 262:23; O'Reilly &
McClelland 1994 *Hippocampus* 4:661; Leutgeb, Leutgeb, Moser & Moser 2007 *Science* 315:961; Bakker,
Kirwan, Miller & Stark 2008 *Science* 319:1640; Yassa & Stark 2011 *Trends Neurosci.* 34:515;
McNaughton & Morris 1987 *Trends Neurosci.* 10:408; Rolls 2013 *Front. Cell. Neurosci.* 7:98;
Nakazawa et al. 2002 *Science* 297:211; Smolensky 1990 *AI* 46:159; Plate 1995 *IEEE TNN* 6:623;
Amit, Gutfreund & Sompolinsky 1987 *Annals of Physics* 173:30; Treves & Rolls 1991 *Network* 2:371;
Treves & Rolls 1994 *Hippocampus* 4:374; Chandra, Sharma, Chaudhuri & Fiete 2025 *Nature* (Vector-
HaSH); Whittington et al. 2020 *Cell* 183:1249 (TEM); Teyler & DiScenna 1986 *Behav. Neurosci.*
100:147; Teyler & Rudy 2007 *Hippocampus* 17:1158; McClelland, McNaughton & O'Reilly 1995 *Psychol.
Rev.* 102:419; Nadel, Samsonovich, Ryan & Moscovitch 2000 *Hippocampus* 10:352. (22 distinct works.)

**Section 2 (replay necessity), verified via dedicated lit-scan sub-agent:** Squire, Genzel, Wixted
& Morris 2015 *Cold Spring Harb. Perspect. Biol.*; Nadel & Moscovitch 1997 *Curr. Opin. Neurobiol.*;
Winocur & Moscovitch 2011 *J. Int. Neuropsychol. Soc.*; Moscovitch et al. 2006 *Curr. Opin.
Neurobiol.*; Sekeres, Winocur & Moscovitch 2018 *Hippocampus*; Vargha-Khadem et al. 1997 *Science*;
Manns, Hopkins & Squire 2003 *Neuron*; Girardeau, Benchenane, Wiener, Zugaro & Buzsaki 2009 *Nat.
Neurosci.*; Ego-Stengel & Wilson 2010 *Hippocampus*; Jadhav, Kemere, German & Frank 2012 *Science*;
Joo & Frank 2018 *Nat. Rev. Neurosci.*; Rasch, Buchel, Gais & Born 2007 *Science*; Rudoy, Voss,
Westerberg & Paller 2009 *Science*; Bendor & Wilson 2012 *Nat. Neurosci.*; de Lavilleon, Lacroix,
Rondi-Reig & Benchenane 2015 *Nat. Neurosci.*; McCloskey & Cohen 1989; French 1999 *Trends Cogn.
Sci.*; Robins 1995 *Connection Science*; Shin, Lee, Kim & Kim 2017 NeurIPS; van de Ven & Tolias
(brain-inspired replay reviews); Lesburgueres et al. 2011 *Science*; Tse et al. 2007 *Science*
(cross-referenced with Section 3). (21 distinct works.)

**Section 3 (schema-gated consolidation), verified via dedicated lit-scan sub-agent:** Tse, Langston,
Kakeyama, Bethus, Spooner, Wood, Witter & Morris 2007 *Science* 316:76; Tse, Takeuchi, Kakeyama,
Kajii, Okuno, Tohyama, Bito & Morris 2011 *Science* 333:891; Wang, Tse & Morris 2012 *Learning &
Memory* 19:315; Preston & Eichenbaum 2013 *Curr. Biol.* 23:R764; van Kesteren, Ruiter, Fernandez &
Henson 2012 *Trends Neurosci.* 35:211 (SLIMM); van Kesteren, Fernandez, Norris & Hermans 2010 *PNAS*
107:7550; McKenzie, Frank, Kinsky, Porter, Riviere & Eichenbaum 2014 *Neuron* 83:202; Gilboa &
Marlatte 2017 *Trends Cogn. Sci.* 21:618; Bartlett 1932 *Remembering*; Deese 1959 / Roediger &
McDermott 1995 (DRM); Warren, Jones, Duff et al. 2014 *J. Neurosci.* 34:7677; Warren et al. 2018
*J. Neurosci.* 38:3767. (13 distinct works.)

**Section 5 (discourse-level context maintenance / acquisition rescue), verified via a fourth
dedicated lit-scan sub-agent (dispatched mid-drill after the coordinator's sharpening):** Kintsch
1988 *Psychol. Rev.* 95:163; van Dijk & Kintsch 1983 *Strategies of Discourse Comprehension*;
Ericsson & Kintsch 1995 *Psychol. Rev.* 102:211; Zwaan & Radvansky 1998 *Psychol. Bull.* 123:162;
Zacks, Speer, Swallow, Braver & Reynolds 2007 *Psychol. Bull.* (cross-referenced with the ProPara
drill); Howard & Kahana 2002 *J. Math. Psychol.* 46:269 (TCM); Howard, Shankar & Jagadisan 2011
*Topics in Cognitive Science* 3:48 (pTCM extended to continuous text); Goldman-Rakic 1995 *Neuron*
14:477; Miller & Cohen 2001 *Annu. Rev. Neurosci.* 24:167; Ferstl & von Cramon 2001 (text-coherence
fMRI); Yarkoni, Speer & Zacks 2008 *NeuroImage* 41:1408; Baldassano, Chen, Zadbood, Pillow, Hasson
& Norman 2017 *Neuron* 95:709; Baldassano, Hasson & Norman 2018 *J. Neurosci.* 38:9689; MacDonald,
Lepage, Eden & Eichenbaum 2011 *Neuron* 71:737; Manns, Howard & Eichenbaum 2007 *Neuron* 56:530;
Smith & Mizumori 2006 *Hippocampus* 16 / *J. Neurosci.* 26:3154; Pacheco-Estefan et al. 2019 *Nat.
Commun.* 10:2255; Wilson & McNaughton 1994 *Science* 265:676; Foster & Wilson 2006 *Nature*
440:680; Davidson, Kloosterman & Wilson 2009 *Neuron* 63:497; Gupta, van der Meer, Touretzky &
Redish 2010 *J. Neurosci.* 30:9918; Liu, Dolan, Kurth-Nelson et al. 2019 *Cell* 178:640; Shin, Tang
& Jadhav 2019 *Neuron* 104:1110; Beukers, Collin, Kempner, Franklin, Gershman & Norman 2024
*Communications Psychology*; Gick & Holyoak 1983 *Cognitive Psychology* 15:1 (cross-referenced with
Section 3); Carvalho & Goldstone 2014 *Memory & Cognition*; Xu & Tenenbaum 2007 *Psychol. Rev.*
114:245 and *Developmental Science* (cross-referenced with prior KB notes). (24 distinct works, ~4
cross-referenced with earlier sections rather than newly counted.)

**Total distinct external citations this drill: ~76** (across 4 independent lit-scan sub-agents,
each returning per-item HIGH/MEDIUM/LOW confidence flags, preserved throughout Sections 1-5 above
wherever the underlying claim is anything less than HIGH, including explicit flags for this drill's
OWN synthesis/extension claims that bridge two independently-cited literatures without a single
paper stating the bridge directly -- e.g. Section 1e's indexing-theory/capacity-math connection,
Section 5b's PFC-to-discourse-scale extension). No citation fabricated; every item traces to a
specific sub-agent WebSearch/WebFetch result. On-disk code citations (FACT_ROLES, `_sr_key`,
`_cleanup`, `AccumulateRegister`, `CausalLinkRegister`, `DGProjection`, `CA3AutoAssociator`,
`cls_discrete_budget_consolidate`, `iterative_attractor`, `SituationReader`, `_select_matched`) were
read directly this session, not from
memory of prior notes' descriptions of them.
