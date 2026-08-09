# Research: representing grounded SCRIPTS/SCHEMAS as FHRR hypervectors -- partial match, chaining, composition, capacity (2026-08-09)

**Filed by:** research (Sonnet), director-assigned "how-to-represent" drill for the grounded self-growing
narrative-comprehension program. **Method:** KB-check-before-drilling (per standing discipline) found the
owned-substrate primitives and 3 sibling VSA prior-art notes already carry ~80% of the needed literature
(read in full: `research_script_half_synthesis_2026-08-09.md`, `prior_art_vsa_hdc_for_language_2026-08-06.md`,
`research_vsa_hdc_state_of_mind_prior_art_scour_2026-07-17.md`, `research_psych_bridging_inference_situation_
models_2026-08-09.md`) -- these are cited and carried forward, NOT re-derived. 3 parallel Sonnet lit-scan
lanes dispatched for genuinely new ground only: (A) precise capacity-math formulas, (B) sequence/chaining/
analogical-mapping mechanisms, (C) hippocampal-entorhinal schema neuroscience for the brain analog -- all 3
completed and integrated below (sections 3c, 5d, 5e, 6). Mid-drill, the Director flagged two additional owned
organs (`hdlab/event_bundle.py::EventBundleCodec`, `hdlab/schema_exemplar_bayes.py::SchemaExemplarBayesIndex`)
directly relevant to this drill; both read in full and integrated in section 1d, with an honest correction
where the disk evidence (EventBundleCodec is bipolar, not FHRR) differed from the initial framing.

---

## HEADLINE

**A script's STRUCTURE (fixed, small, shared role-vocabulary: TRIGGER/PRECONDITION/ATTEMPT/CONSEQUENT/
PARTICIPANT roles) and its CONTENT (open-vocabulary concept-fillers) should be represented as two
independently-varying factors bound together -- exactly `hdlab.situation_model_accumulate.RelationRegister`'s
existing `bind_filler(role, content_vec)` pattern, generalized from its current 2-role {GOAL, OUTCOME}
vocabulary to a Trabasso & van den Broek (1985)-licensed typed-node role set, with `content_vec` supplied by
`hdlab.lexical_similarity.concept_vector` instead of a closed `idx_vecs` symbol.** This is >80% REUSE of
already-VET-confirmed organs (`AccumulateRegister`/`RelationRegister`/`CausalLinkRegister`'s bind-bundle-
unbind-cleanup chain, `concept_vector`'s feature-bundle content code, `sequence_memory.SequenceMatrix`'s
already-chain-grade-certified `chain_predict()` depth-D lookahead) plus one genuine BUILD (resonator-style
multi-factor iterative decode, not yet present anywhere in `hdlab/`, needed only once script-TYPE codebooks
and multi-role compositional queries grow past what direct unbind+argmax can resolve). CHAINING decomposes
into two DIFFERENT owned mechanisms for two DIFFERENT chaining regimes the psych literature itself
distinguishes: within-script scene-order (Kanerva/Choo-style positional accumulation, reuse
`SequenceMatrix.chain_predict`) vs. across-inference goal-relevant chaining (Trabasso's recursive
Goal->Attempt->Outcome->new-Goal unit, reuse `CausalLinkRegister`'s query pattern generalized to open content).
**The brain analog for the structure/content split is now FULL-TEXT VERIFIED, not just hypothesized**: the
Tolman-Eichenbaum Machine (Whittington et al. 2020, *Cell*) shows entorhinal cortex supplies a task-general
structural code bound via literal outer-product conjunction to hippocampal content-specific representations,
in a Hebbian weight matrix -- and, independently, Baldassano et al. (2018, *J. Neuroscience*) find
**story-independent schema patterns in posterior medial cortex/mPFC/superior frontal gyrus that generalize
across different specific narratives** (a "restaurant" script pattern recognizable across unrelated stories) --
direct neural evidence for structure/content-factorized SCRIPTS specifically, not just spatial relational
memory. CAPACITY has one wall already MEASURED on our own data (flat single-register overload, 89.8%->67.2%
regression, already FIXED by the validated multi-bank sharding upgrade), one wall now precisely FORMULATED by
fresh lit-scan (binding costs a provably higher dimensionality than bundling -- Clarkson/Ubaru/Yang 2023's
polylog penalty -- and chained inference compounds unbinding error MULTIPLICATIVELY per hop, capping practical
chain depth), and one wall the field's own literature leaves genuinely unbounded (nested compositional depth --
no paper anywhere states a numeric nesting-depth ceiling; confirmed absent across 3 independent scours now,
not merely unsearched).

P_deflated (novel-synthesis "this specific representation assembly is the right design" claim, capped per
lit-scan calibration discipline): **0.40** (raised slightly from an initial 0.38 pre-integration estimate,
reflecting that 2 of 3 fresh lanes returned full-text-verified rather than secondary-sourced findings -- see
calibration section). Individual literature findings (Schlegel/Neubert/Protzel capacity curves, resonator-
network stability threshold, Frady/Kleyko/Sommer's exact SNR equation, Clarkson/Ubaru/Yang's binding-cost
theorem, Trabasso's typed causal network, Choo's OSE, Kanerva's permutation stack, the Tolman-Eichenbaum
Machine) are independently well-cited and now mostly full-text-verified (~0.70-0.85 raw); the ASSEMBLY into
ONE script-representation design is this note's own synthesis, still deflated per discipline and capped at the
mandatory 0.50 novel-synthesis ceiling.

---

## 1. Representation design -- structure/content factorization

### 1a. The two-factor split (the core design decision)

A Schank & Abelson (1977) script has: name / track / roles / props / entry-conditions / scenes / **results**
(the pre-stored expected outcome -- already identified as the answer to the arc's goal<->outcome residual in
`research_script_half_synthesis_2026-08-09.md`). Cast into FHRR:

- **Role vocabulary (STRUCTURE, fixed, shared across ALL script instances and ALL script types)**: a small
  seeded `Dict[str, torch.Tensor]` of unit-phase role keys, exactly `AccumulateRegister.role_vecs` /
  `RelationRegister.role_vecs`'s existing construction (`unit_phase_vec(d, generator)` per role name).
  Proposed vocabulary, licensed directly by Trabasso & van den Broek (1985, *JML* 24(5)) and Stein & Glenn
  (1979)'s story-grammar precursor (both read in full today via `research_psych_bridging_inference_situation_
  models_2026-08-09.md`, not re-derived here): `SETTING_ROLE, TRIGGER_ROLE` (their "Initiating Event"),
  `PRECONDITION_ROLE, ATTEMPT_ROLE, CONSEQUENT_ROLE` (their "Outcome"/Schank's "results" slot),
  `AGENT_ROLE, PATIENT_ROLE, INSTRUMENT_ROLE` (participant roles within any event-slot). This is a strict
  generalization of `CausalLinkRegister`'s existing 2-symbol `{CAUSE_ROLE, EFFECT_ROLE}` and
  `RelationRegister`'s existing 2-symbol `{GOAL_ROLE, OUTCOME_ROLE}` -- same class extension pattern
  `CausalLinkRegister` already used on `AccumulateRegister`, just a richer fixed vocabulary.
- **Content (OPEN vocabulary, varies per instance)**: `hdlab.lexical_similarity.concept_vector(word)` -- the
  McRae-style shared-feature bundle already promoted and self-tested (89-concept lexicon, cosine-graded, ATL-hub
  analog per that module's own citation of Cox et al. 2024). This REPLACES `CausalLinkRegister`'s closed
  `idx_vecs` roster (a fixed small array of event-slot indices) with an open-ended grounded concept space --
  `RelationRegister.bind_filler` ALREADY accepts an arbitrary `content_vec` instead of an `idx_vec` (see its
  docstring: "generalizes what gets bound... since the goal_outcome_relation ablation needs to carry an
  OPEN-vocabulary concept representation"). **This means the open-vocabulary-filler capability this drill needs
  was already built yesterday for the GOAL/OUTCOME 2-role case; extending its role vocabulary is a config
  change, not new algebra.**
- **Bind + bundle composition (unchanged primitive, reused verbatim)**: a script INSTANCE for one narrative
  episode = `bundle([bind(role_vecs[r], concept_vector(filler_r)) for r in observed_roles])`, i.e. exactly
  `RelationRegister.bind_filler` called once per observed role, landing in one entity's accumulate-bundle.
  Decode any role via `unbind(instance_vec, role_vecs[r])` then `cleanup_argmax` against either (a) the open
  concept lexicon (which content filled this role) or (b) a small script-TYPE codebook (which script grammar
  this instance is an example of) -- both cleanup targets already exist as owned primitives
  (`situation_model_accumulate.cleanup_argmax`, `cleanup_family.k_NN_lookup` / `.iterative_attractor` for a
  noisier query).

### 1b. Script TYPE vs script INSTANCE (the one genuinely new structural distinction)

Two vectors per script, not one, is the actual novel design move (not literature-stated; this note's own
synthesis, per the calibration discipline below):

- **Script TYPE vector** = `bundle([role_vecs[r] for r in this_type's_declared_roles])`, i.e. the STRUCTURE
  alone, content-free -- a small, FIXED codebook entry (dozens to low hundreds of entries: REPAIR, ERRAND,
  INFO-EXCHANGE, SKILL-TRAIN, CONFLICT-RESOLUTION... -- note `hdlab.goal_outcome_relation`'s existing 6
  hand-authored MEANS-END pools, `COGNITION_GOAL_POOL` / `SKILL_GOAL_VERB_POOL` / `SKILL_GOAL_REFERENT_POOL` /
  `INFO_EXCHANGE_POOL` / `ERRAND_POOL` / `SKILL_TRAIN_POOL`, are ALREADY a de facto script-trigger-vocabulary
  partition and are the natural seed set for the first script-TYPE codebook, not a fresh hand-authorship task).
  This is the "grammar," matched against like a construction.
- **Script INSTANCE vector** = the TYPE's structure with CONTENT actually bound in for one episode (section
  1a). Ephemeral, per-episode -- exactly `RelationRegister`'s own documented usage pattern ("GOAL_ROLE and
  OUTCOME_ROLE are bound on SEPARATE ephemeral register instances").
- **Why this split matters for partial matching (task requirement a, next section)**: a bare-structure TYPE
  vector lets a query cleanup-argmax against "which GRAMMAR does this surface event look like" independently
  of "which specific content filled it" -- exactly the Kintsch C-I two-stage shape (construct broadly against
  structure, settle against content) already the module's own stated justification for `AccumulateRegister`.

### 1c. Brain analog for the structure/content split

See section 6 (Lane C's return, integrated) for the Tolman-Eichenbaum-Machine analog and the honest
confidence calibration on it.

### 1d. Mid-flight integration -- two coordinator-flagged owned organs (`event_bundle.py`, `schema_exemplar_bayes.py`)

The Director flagged two additional owned organs mid-drill; both read in full and folded in here, with an
honest correction to the framing where the disk evidence differs from the initial pointer.

**`hdlab/event_bundle.py::EventBundleCodec` is the EXACT role-slot bind-then-bundle-then-unbind-query pattern
section 1a's script-INSTANCE design uses, one level DOWN** (event-internal `PRED`/`AGENT`/`PATIENT`/`TENSE`
roles, not script-internal `TRIGGER`/`CONSEQUENT` roles) -- already built, already self-tested (round-trip
role-query accuracy >=0.98 at N=1024 against a 60-symbol vocab; `THIN-LABEL` and `BAG-OF-ARGS` fairness
baselines confirmed at/near chance; an `encode_scrambled_event` permutation control already present, the same
pairscramble-must-collapse shape this drill's own cheap decisive test uses). **Honest correction to the
"compose scripts FROM these events, not a new encoder" framing**: `EventBundleCodec` is **bipolar**
(`{-1,+1} float32`, reusing `hdlab.role_slot_summarizer`'s `_bipolar_bind`/`_bipolar_quantize`), not FHRR
complex64 -- `hdlab/binding.py`'s own docstring deliberately keeps the bipolar (BSC) family as separate named
siblings (`bsc_bind`/`bsc_unbind`) from the complex64 FHRR dispatch path because "BSC cannot be
dtype-dispatched apart from HRR." Binding a script-role FHRR vector directly to a bipolar `EventBundleCodec`
event vector is not a defined operation today (`bind()` expects a complex64 second argument for the FHRR path;
a bipolar vector has no imaginary part to multiply against without an explicit lift). Two honest resolution
paths:
  - **(i) Port the PATTERN, not the code (recommended)**: build a complex64 sibling reproducing
    `EventBundleCodec`'s exact API (`encode_event`, `query_role_vec`, `encode_scrambled_event`) on
    `unit_phase_vec`/`bind`/`bundle`/`cleanup_argmax` instead of the bipolar primitives -- mechanical,
    near-zero design risk (the PATTERN is proven; only the dtype family changes), keeps the whole
    event+script hierarchy in one FHRR family as the task brief requires, and `EventBundleCodec`'s own
    self-tests become the regression fixture the FHRR sibling is checked against (full credit as the
    template, not dead-ended work).
  - **(ii) Bridge the two families** with an explicit lift (bipolar sign -> phase 0/pi ->
    `torch.polar(ones, theta)`) -- keeps `EventBundleCodec`'s code untouched but adds a new, currently-unbuilt,
    currently-unverified conversion primitive and a fidelity question (does the lift preserve bipolar cosine
    geometry well enough) needing its own cheap verification cell before being trusted.
  Recommendation: **(i)**, since it avoids an unverified cross-family bridge and directly satisfies "represented
  as FHRR hypervectors."

  **What transfers AS-IS, no port needed**: `EventBundleCodec`'s own disclosed capacity finding is a DIRECT,
  on-disk, already-measured number (not a field-literature extrapolation), and sharpens section 5's capacity
  story: *"an event bundle is a SMALL fixed superposition (~4 role-filler pairs) at alpha = 4/N_DIM << the
  0.138 bundle-collapse wall... a single-vector (bundled) event is the correct, high-fidelity representation at
  this level -- it round-trips cleanly. The capacity limit lives one level up... where many event bundles are
  superposed"* (module docstring, verbatim). This crystallizes the design principle section 5 below states
  explicitly: **keep any SINGLE bundle small (event level ~4 roles; script-instance level ~5-9 roles per
  section 1a) so alpha stays well under ~0.138; handle ACROSS-instances accumulation via multi-bank sharding
  (5a, already validated); handle ACROSS-types codebook growth via resonator factorization or
  SchemaExemplarBayes compression (below) only once direct argmax is shown to break.**

**`hdlab/schema_exemplar_bayes.py::SchemaExemplarBayesIndex` is a Bayesian k-means-cluster ROUTER for
compressed fact retrieval** (n_facts -> k_schemas clusters, LSE-Bayes posterior readout, 10x compression at
~90% recall retained per its own docstring, citing Batch-C Compression Pareto v1, commit 7cef91b3) -- read in
full. **Honest naming-collision flag**: its "schema" is a hardware/retrieval-locality compression cluster
(k-means centroid over L2-normalized real-valued vectors), not a Schank-style cognitive script/schema -- the
two uses of the word should not be conflated. That said, it IS directly reusable for INSTANCE-TO-TYPE
INDUCTION: if a growing store of script-INSTANCE vectors (section 1a) is periodically clustered via
`SchemaExemplarBayesIndex.fit()`, each resulting cluster's centroid is an EMERGENT, bottom-up-induced
script-TYPE prototype -- a genuinely different (complementary, not competing) path to populating the
script-TYPE codebook (section 1b) than this note's primary proposal (hand-seed from `goal_outcome_relation`'s
6 existing pools). This directly generalizes `hdlab.consequence_learning_loop.py`'s already-validated
MIN_CONFIRM/consolidation wrapper (a candidate accumulates independent confirming instances before promotion
from PENDING to a durable grounded entry) from OOV-verb-valence to OOV-SCRIPT-TYPE induction -- same
PENDING/GROUNDED/GROUNDED_NEUTRAL shape, one level up; directly the acquisition-loop shape (flag-not-
understood -> library -> consolidate -> bank -> grow) this program's foundational framing already commits to.
Two build gaps, honestly flagged: **(I)** `SchemaExemplarBayesIndex` operates on real-valued L2-normalized
`np.ndarray` via plain dot-product/k-means -- FHRR complex64 script-instance vectors need a small adapter
(concatenate `[Re(v), Im(v)]` into a `(2N,)` real vector, which preserves the FHRR cosine's real part up to a
known factor) before this router applies; mechanical, low-risk, not built yet. **(II)** whether k-means-
discovered clusters in script-instance space correspond to semantically-coherent Schank-style script TYPES
(REPAIR vs ERRAND vs...) rather than some other latent structure (e.g. clustering by narrative TOPIC instead
of by script GRAMMAR) is an open, testable question, not assumed here or anywhere upstream.

**Chaining, sharpened**: with events (once ported per (i) above) as the atomic script-role fillers, section
3b's chaining step gets structurally richer, not just re-described -- `decode_filler(entity, CONSEQUENT_ROLE)`
returns a full EVENT bundle (PRED+AGENT+PATIENT+TENSE), not a bare concept vector, so the next-step TRIGGER
query (section 3b step 3) can partially cue on ANY SUBSET of that event's roles (PRED alone, or PRED+PATIENT),
a strictly more flexible and realistic reproduction of section 2's partial-matching story than matching on one
flattened concept vector, since real narrative consequents are structured events, not single words. No
mechanism beyond sections 2+3 is added -- this is a direct consequence of the filler TYPE, not new machinery.

**Capacity, sharpened**: `EventBundleCodec`'s alpha=4/N_DIM<<0.138 finding answers "how many roles can ONE
event hold" (comfortably up to its own tested 4; the module does not test past 4 and this note does not
extrapolate further without a fresh measurement). It does NOT answer "how many DISTINCT events/script-types
coexist in one CODEBOOK" -- section 5b's question, now with `SchemaExemplarBayesIndex` as an ADDITIONAL
candidate mitigation (10x compression at ~90% recall) alongside resonator factorization, worth a head-to-head
comparison once the codebook-capacity wall is actually measured (cheap decisive test below), not assumed to
need the heavier resonator build first.

---

## 2. Partial matching (requirement a)

A surface event cues a script from PARTIAL evidence (e.g. only the TRIGGER role observed, no CONSEQUENT yet)
via the SAME graceful-degradation property `AccumulateRegister`/`RelationRegister` already exhibit by
construction: bundling is a superposition, so unbinding any ONE known role from a partially-filled bundle
recovers a noisy-but-usable readback of that role's content REGARDLESS of how many other roles are unfilled
(there is no "missing slot" failure mode -- an unfilled role simply contributes zero terms to the bundle).
Concretely, the partial-match query is:

1. Extract the observed role-filler(s) from the surface text (existing extraction machinery --
   `thematic_role_labeler.py`, `frame_induction.py` -- out of scope for this drill, assumed upstream).
2. Bind `concept_vector(observed_filler)` to its role key, forming a PARTIAL instance vector (bundle of just
   the observed terms).
3. Score cosine similarity of this partial vector against each script TYPE's structure-only vector (section
   1b) restricted to the SAME observed role(s) -- i.e. unbind each TYPE's declared filler-prototype for that
   role (if the TYPE codebook stores prototypical fillers, not just bare role structure -- see 1b's "grammar
   matched against like a construction," which in practice needs at least ONE canonical exemplar filler per
   role to be matchable, not zero) and compare.
4. `cleanup_family.iterative_attractor` (CA3/DG-style Treves-Rolls attractor dynamics, already owned) or
   `k_NN_lookup` resolves the best-matching TYPE, with a GRADED confidence score, not a hard binary match --
   this directly reproduces Bower, Black & Turner (1979)'s finding that script activation from partial cues is
   graded and generative (readers false-recognize unmentioned script-typical actions), already cited in
   `research_script_half_synthesis_2026-08-09.md`.

This is REUSE, not build: every primitive named above (`bind`, `bundle`, `unbind`, `cleanup_argmax`,
`iterative_attractor`, `k_NN_lookup`) already exists and is already VET-confirmed for the analogous
entity-event case. The novel piece is only the CONTENT (concept_vector-as-filler) and the TYPE-codebook
organization (section 1b), not new algebra.

---

## 3. Chaining / multi-step inference (requirement b) -- two mechanisms for two regimes

The psych literature (read in full today, `research_psych_bridging_inference_situation_models_2026-08-09.md`)
distinguishes exactly two chaining regimes a script needs, and the owned substrate already has one validated
primitive for EACH:

### 3a. Within-script scene-order chaining (stereotyped sequence: enter-restaurant -> order -> eat -> pay)

**Reuse `hdlab.sequence_memory.SequenceMatrix` verbatim -- it already IS this mechanism, chain-grade
certified.** `bind_pair(k_prev, k_next)` Hebbian-writes ordered scene-vector pairs; `chain_predict(k_start,
depth, codebook)` ALREADY iterates `predict_next` for `depth` steps WITH per-step codebook cleanup -- this is
literally "decode step N's output, clean it up, feed it as step N+1's query," already built, already
HARD_PASS at depths [1,3,5,7,10] on the c3 cell (commit a27939c5, atom-validated). No new code needed for this
chaining regime: script scenes ARE the `keys` argument to `bind_sequence`/`chain_predict`.

### 3b. Across-inference goal-relevant chaining (an outcome that fails to resolve a goal spawns a NEW goal)

This is the DEEPER chaining the task's "consequent feeds next inference" language points at, and it is NOT
positional/stereotyped -- it is Trabasso & van den Broek's **recursive Goal->Attempt->Outcome unit**: Goal
motivationally-causes Attempt, Attempt physically-causes Outcome; if Outcome does NOT satisfy the goal, the
Outcome instead **psychologically causes a NEW Goal node**, recursively re-entering the same
Goal->Attempt->Outcome cycle (already established, read in full today, not re-derived). Mechanism:

1. Decode the CONSEQUENT_ROLE filler from the current script instance: `decode_filler(entity, CONSEQUENT_ROLE)`
   -- exact reuse of `RelationRegister.decode_filler`, already exact (lossless) for a single-filler bind per
   that method's own docstring proof.
2. Run the ACHIEVE/CONTRADICT graded relation queries already designed (and pre-registered, not yet landed) in
   `research_psych_bridging_inference_situation_models_2026-08-09.md`: `concept_similarity(goal_concept,
   decoded_consequent)` for means-end satisfaction; `quality_relation`'s opposition-channel shape for
   preclusion. **This drill does not re-derive that mechanism** -- it is the SAME chaining step, viewed from
   the representation side rather than the psych-mechanism side; the two notes are complementary, not
   duplicative (see cross-thread synthesis).
3. If the goal is NOT satisfied (CONTRADICT fires, or ACHIEVE fails to clear threshold): the decoded
   `outcome_concept_vec` becomes the new query's TRIGGER filler -- i.e. `bind(TRIGGER_ROLE, decoded_consequent)`
   seeds a FRESH script-instance lookup (section 2's partial-match procedure), recursively. This is the
   `CausalLinkRegister.query_effect_of` pattern (decode one event's linked-event pointer, use it to key the
   NEXT lookup) generalized from a closed `idx_vecs` roster to open concept content -- same shape, richer
   vocabulary, no new binding operator.

**Why two mechanisms, not one:** 3a is positional/stereotyped (the SAME script's scenes in a fixed order,
Choo's OSE / Kanerva's permutation-chain shape); 3b is content-conditioned/recursive (WHICH new goal gets
spawned depends on what the consequent concept actually IS, requiring a concept-space graded query, not a
position index). Conflating them into one mechanism would force the positional S-matrix to also carry semantic
content-matching, which it structurally cannot (its keys are opaque vectors with no content-addressing beyond
the Hebbian pair it was trained on) -- keeping them separate is the honest, substrate-native design, not an
arbitrary complication.

### 3c. Lane B synthesis (sequence/analogical-mapping lit-scan) -- sharpens 3a/3b, and flags the real depth cap

Lane B (2 sources full-text-verified: Kleyko survey Part I, Cohen et al. 2010 PSI primary; the rest
cross-corroborated secondary) confirms and sharpens both mechanisms:

- **3a is precisely the field's own "trajectory association" pattern**: Choo's OSE (`M <- M + item_i (x)
  p_i`, position vectors built as repeated self-binding `p_n = v (x) v (x) ... n times`) is structurally
  identical to `SequenceMatrix.bind_pair`'s ordered-pair Hebbian write, and Plate's own original 1992/1995
  "trajectory association" (`item_1 + item_2 (x) p + item_3 (x) p (x) p + ...`) is the same shape one level
  more general (arbitrary depth, not just adjacent pairs) -- confirms `chain_predict`'s depth-D iteration is
  not an ad hoc extension but the field's own canonical construction. **A genuinely useful operational detail
  Lane B surfaced, not previously in the KB**: in Eliasmith's SPA, the CLEANED-UP decoded item at each step is
  not merely a lookup output -- it directly becomes the next cortical semantic-pointer STATE that the
  basal-ganglia action-selection loop scores and thalamus gates, i.e. decode-and-re-inject-as-next-query is
  literally how the brain-inspired reference architecture chains, not just a convenient implementation choice
  -- strengthens the case that `chain_predict`'s existing "decode, cleanup, feed forward" loop is the
  brain-faithful shape, not merely a software convenience.
- **3b's `query_effect_of`-style chaining has a real, named field precedent with an honest caveat**: PSI
  (Cohen, Widdows, Schvaneveldt & Rindflesch 2010, *J. Biomed. Inform.*, full-text verified) encodes each
  predicate as a FIXED PERMUTATION keyed by relation type (`sem_vec(X) += rho_TREATS(elemental_vec(Y))`), not
  a bind-with-a-role-vector -- an algebraically different (cheaper, since permutation has no multiply cost)
  design point than this note's bind-based role vocabulary (section 1a). The explicit MULTI-HOP chaining
  algorithm (hop-1 query yields a candidate set, each candidate becomes hop-2's probe) is confirmed to live
  ONLY in the 2012 follow-up (Cohen et al., "Discovering discovery patterns with PSI"), which Lane B could not
  fully fetch (paywalled) -- rated secondary/abstract-level, an honest gap, not a fabricated confirmation.
- **Analogical role-sharing (section 4b) has 2 further corroborating mechanisms**: Kanerva's "dollar of
  Mexico" is now independently re-confirmed (secondary, multiply corroborated); Gayler & Levy (2009) describe
  a RECURRENT settling circuit for analogical mapping (an evolving correspondence vector iteratively refined
  via bind+cleanup comparison until it converges on the best role-structure correspondence) -- a more dynamic
  alternative to this note's "shared role vectors give correspondence for free" claim, worth flagging as a
  fallback if the free/static sharing property (section 4b) proves too rigid for cases where role
  correspondence itself must be DISCOVERED rather than assumed fixed. Also newly surfaced: **Rachkovskij &
  Kussul (2001)'s context-dependent thinning** builds role-filler bindings WITHOUT a pre-declared fixed role
  vocabulary (resparsifying after superposition, recursively nestable for trees/DAGs) -- a genuine ALTERNATIVE
  design to this note's fixed-role-vocabulary approach (section 1a), worth a follow-up comparison if the
  script-role vocabulary ever needs to grow open-endedly rather than staying a small closed set.
- **The one load-bearing NEW constraint Lane B surfaces, not previously in the KB**: **unbinding error
  compounds MULTIPLICATIVELY with hop count** (Plate's own noise analysis; corroborated by Schlegel et al.'s
  depth-40 binding-chain benchmark, section 5b) -- every source examined converges on this as the practical
  ceiling on chain depth, not a hard cliff but a compounding decay curve. This directly qualifies section 3b's
  recursive goal-respawn chaining: each additional Goal->Attempt->Outcome->new-Goal recursion pays a
  MULTIPLICATIVE (not additive) fidelity cost, so a script's practical recursive-respawn depth is bounded
  well before any codebook-capacity wall is hit -- this is now folded into the capacity section (5e) and a
  new falsifiable prediction (Prediction 4) below, since it is a genuinely new, decision-relevant finding.

---

## 4. Composition (requirement c)

Two composition modes, both cheap extensions of existing algebra (no new binding operator needed):

### 4a. Nested/chunked composition (script-within-script)

Plate (1995)'s own "chunking" mechanism -- already cited in `research_vsa_hdc_state_of_mind_prior_art_scour_
2026-07-17.md` -- treats a whole bound-and-superposed composite vector as ITSELF a valid filler for a
higher-level role. Concretely: `bind(ATTEMPT_ROLE, sub_script_instance_vec)` where `sub_script_instance_vec`
is itself the bundle of a fully-formed sub-script (e.g. "negotiate a price" as the ATTEMPT inside a larger
"buy a car" script). This directly implements Trabasso's recursive Goal->Attempt->Outcome unit's own
recursion (an Attempt CAN decompose into its own Goal->Attempt->Outcome cycle) at the representation level.
**This is a genuine BUILD, honestly flagged**: no code in `hdlab/` currently binds a composite
`AccumulateRegister`/`RelationRegister` output back in as a filler for another instance of itself -- the
OPERATION (`bind` accepting a composite complex64 vector where it currently accepts an atomic `concept_vector`
output) requires zero new algebra (bind doesn't care whether its second argument came from `unit_phase_vec` or
from a prior `bundle()` call -- both are unit-ish complex64 vectors of the same shape) but the CALLING PATTERN
(recursive script-instance construction, and eventually recursive decode) does not exist yet and needs its own
small module, not a primitive-level change.

### 4b. Role-vocabulary sharing across script TYPES (analogical transfer, for free)

Because role vectors (`AGENT_ROLE`, `TRIGGER_ROLE`, ...) are seeded ONCE and shared across every script TYPE
(exactly `RelationRegister`'s and `CausalLinkRegister`'s existing pattern -- both subclass the SAME
`AccumulateRegister.role_vecs` construction), querying "what fills AGENT_ROLE in THIS instance" against a
DIFFERENT script type's stored instance, using the SAME `AGENT_ROLE` vector, automatically performs
role-correspondence analogical mapping -- Kanerva (2010)'s "dollar of Mexico" worked example, mapped onto
script roles instead of country-attribute records, essentially for free IF role vectors are shared rather than
re-seeded per script type. This is REUSE (the sharing property falls out of using one `role_vecs` dict across
all script-TYPE constructions), not a new mechanism -- the design discipline is simply "never re-seed
`AGENT_ROLE` per script type," which the existing subclass pattern already enforces by construction (both
`CausalLinkRegister` and `RelationRegister` build their OWN small role_vocab in `__init__`, so the discipline
generalizes cleanly: one shared PARTICIPANT-role vocabulary module, imported by every script-TYPE definition,
not redefined per type).

---

## 5. Capacity analysis (requirement d) -- what breaks at scale, and the fix

Three SEPARATE capacity questions, deliberately not conflated (the 08-06 sibling note already flagged
conflating flat-bundle capacity with nested-depth capacity as a literature-wide gap; this note keeps them
apart):

### 5a. FLAT bundle capacity within ONE script instance (roles-per-instance) -- MEASURED wall, MEASURED fix

**Already hit and already fixed on our own data, not a projection.** `hdlab.situation_model_multibank.py`'s
own docstring: the flat `AccumulateRegister` register's decode self-consistency regresses **89.8% -> 67.2%**
on the Anne consolidation-ledger scenes once events/entity grows past a handful -- "too many events crammed
into one register." The fix (`MultiBankAccumulateRegister`, already built, already registered in
`data/capability_registry.jsonl` as `working_memory_multibank_K_capacity`, chain-grade certified at
`K_total=4096, n_banks=64, k_per_bank=64`: RANDOM regime recall=0.9927, ADVERSARIAL regime recall=0.9801 at
FEATURE_OVERLAP_FRAC=0.20) is a direct drop-in for script instances: route script-role-filler writes across
`n_banks` by content-anchored hash exactly as it already does for entity-events, via `stable_bank_id`. **This
is a config change (`make_situation_register(..., backend="multibank")` already exists as the selectable
factory), not a build.** Honest caveat carried from that module's own docstring: at CURRENT pilot scale (few
roles/instance, e.g. 4-8 script roles) flat and multibank decode IDENTICALLY (both saturate near 1.0) -- the
multibank win is capacity headroom for when script instances accumulate MANY bound facts per entity over a
long narrative (durable-store scale), not a currently-measured lift at toy scale.

### 5b. TYPE-level codebook capacity (how many DISTINCT script types / grounded concepts before cleanup
confuses them) -- PROJECTED from field capacity curves, needs its OWN measurement

Governed by the field's own standardized capacity math (Schlegel, Neubert & Protzel arXiv:2001.11797,
cross-verified across 2 independent sibling notes today): FHRR needs **~330 dimensions to bundle 15 items at
99% accuracy**, rising further when binding is combined WITH bundling (actual role-filler scenes, not bare
item-bundling) -- sparse architectures need up to 44% MORE dimensions for the same reliability. Frady, Kleyko
& Sommer's SNR law `s = sqrt(N/M)` (M items in N dimensions) gives the general scaling shape: **at the
substrate's own default N=1024, this curve projects comfortable headroom for the LOW TENS of script types**
(well above N=330's 15-item point) but this is an EXTRAPOLATION from a different task (arbitrary random-vector
bundling, not script-role-content specifically) -- exactly the honest caveat the 08-06 sibling note's own
Prediction 7 already flags for our register-capacity claims generally, inherited here unchanged. For hundreds
to thousands of script types (a realistic mature-corpus target), dimensionality would need to scale into the
several-thousand range per the same curve -- expensive but not architecturally impossible at N=4096-8192 (the
substrate already runs FHRR at N=8192 elsewhere, e.g. `lexical_similarity.py`'s N_DIM=8192). **The
higher-leverage fix at that scale is NOT bigger N alone but resonator-style iterative factorized decode**
(Frady, Kent, Olshausen & Sommer 2020; stability condition **D_f/N <= 0.056**, i.e. per-factor codebook size
relative to dimension; beats direct-search baselines by ~2 orders of magnitude in "operational capacity," the
field's own standardized metric) for the specific case of a MULTI-ROLE compositional query (recovering
TYPE + AGENT-filler + TRIGGER-filler simultaneously from one composite, when direct argmax search over the
combinatorial TYPE x FILLER space becomes infeasible) -- **this is a genuine BUILD, honestly flagged: no
resonator-network module exists anywhere in `hdlab/` today** (confirmed by `ls hdlab/ | grep -i resonator` ->
empty). `hdlab.cleanup_family.iterative_attractor` is the closest owned primitive (Treves-Rolls CA3/DG
attractor dynamics) but solves a DIFFERENT problem -- cleaning up ONE noisy vector against ONE codebook, not
jointly factorizing MULTIPLE simultaneously-bound unknowns -- so it is not a substitute, only a partial
precedent for "iterative refinement beats one-shot argmax" within the substrate's own code.

### 5c. Compositional NESTING depth (script-within-script, section 4a) -- CONFIRMED UNBOUNDED in the literature

**No paper anywhere, across 3 independent scours now (07-17, 07-18, 08-06 sibling notes, cross-checked again
today), states a numeric ceiling on how many levels of `bind(bind(bind(...)))` nesting a VSA structure can
support before crosstalk from composite fillers makes cleanup fail.** Schlegel/Neubert/Protzel test sequential
BINDING CHAINS to depth 40 and find VTB degrades less than HRR's convolution/correlation across the chain, but
this measures a DIFFERENT thing (repeated binding of the SAME vector, a positional chain) than NESTED
composition (a script recursively containing sub-scripts, where each level is itself a full bundle of several
role-filler pairs, not a single bind). **Honest bottom line: our own nesting-depth capacity (how many levels of
Attempt-within-Attempt a script can go before decode degrades) has NO borrowed formula to check against and
must be measured empirically once section 4a's chunking module is built** -- this is the single most
consequential "here's what breaks and there's no off-the-shelf answer" finding in this whole drill, and should
be flagged in any capacity claim rather than assumed safe by analogy to the (different) flat-bundle curves in
5a/5b.

### 5d. Lane A synthesis (capacity-math lit-scan) -- exact formulas, and one real correction

Lane A full-text-verified 7 of 9 primary sources (exact equations, not paraphrase). Key confirmations and
ONE genuine correction to 5b's framing above:

- **Schlegel/Neubert/Protzel's numbers are CONFIRMED exactly**: FHRR needs ~330 dims for 15 bundled items at
  99% accuracy, ~340 dims for 15 combined bound+bundled pairs (+3%), best-in-class among 11 compared VSAs on
  min-dims. Depth-40 binding-chain degradation ranks **VTB best (~0.8+ similarity retained), HRR/circular-
  convolution moderate (~0.6), MAP-C worst (~0.55)** -- our own FHRR sits in the HRR-family moderate band, not
  the best-case VTB band; a real, disclosed data point for section 5c's honest nesting-depth uncertainty (not
  a full answer, since this measures repeated-bind-of-the-same-vector, not nested nested-bundle composition,
  per 5c's own distinction, but it is the closest quantified proxy that exists).
- **The exact SNR law, verified equation-for-equation** (Frady, Kleyko & Sommer 2018, *Neural Computation*
  30(6), arXiv:1803.00412, Eq. 35): `s = sqrt(N/M)`, confirmed to hold for BOTH symbolic bundling AND
  permutation/role-bound (sequence) items alike -- i.e. binding via a fixed permutation (PSI's / Kanerva's
  approach, section 3c) does not change this SNR law relative to plain bundling.
- **Genuine correction to 5b's framing: binding is NOT capacity-free relative to bundling.** Clarkson, Ubaru &
  Yang (2023, arXiv:2301.10352, full-text verified) give rigorous JL-style bounds showing bundling needs
  `m = O(N log(M/delta))` dimensions for M items, but BINDING (k=2 role-filler pairs) needs
  `m = O(eps^-2 log^3(||v||_1/(eps*delta)))` -- **an extra log^3 penalty specifically from the bind operator**,
  i.e. our design's actual operation (bind role to filler, THEN bundle several such pairs -- section 1a) is
  provably more expensive than bare item-bundling, not merely "combined bind+bundling needs somewhat more
  dims" as 5b's Schlegel-only framing understated. This sharpens, not overturns, 5b's conclusion (the
  low-tens-of-script-types headroom estimate at N=1024 likely still holds since it already used the
  COMBINED bind+bundle ~340-dim figure, not the bare-bundle ~330-dim one) but the underlying reason is now
  precisely named rather than just empirically observed.
- **Gallant & Okaywe (2013, arXiv:1501.07627) gives a concrete worked table directly useful for sizing a
  MATURE script-type inventory**: `p = 1 - N*T(sqrt(D/(2S-1)))` (D=dims, S=#bundled items, N=#distractors,
  T=Gaussian tail) -- their own worked example, **S=100 stored items against N=100,000 distractors needs
  D=6,927 dimensions** for near-error-free recall. This is a directly transferable planning number for "how
  many dims does a MATURE (~100-item) script-TYPE codebook realistically need against a large distractor
  pool (the full open concept vocabulary)" -- **~7,000 dims, not the low-thousands this note's 5b estimate
  loosely gestured at** -- a materially more precise (and somewhat higher) planning figure than 5b's own
  "several-thousand range" hedge.
- **Resonator-network stability, formula-verified**: `D_f/N <= 0.056` confirmed exactly (quote-verified), with
  the exact recursive bit-flip-probability formula (Eq. 19-20 of the Neural Computation paper) and confirmation
  that operational capacity scales QUADRATICALLY in N, maximized when per-factor codebook sizes are balanced
  (`D_1 = ... = D_F = M^(1/F)`) -- directly actionable for sizing a resonator-based TYPE+ROLE-FILLER joint
  decode (section 5b) once/if that build is undertaken: keep the per-factor codebooks (script TYPES, AGENT
  fillers, TRIGGER fillers, ...) roughly balanced in size, not lopsided.
- **A genuinely open discrepancy, honestly flagged rather than resolved**: Hersche et al. (2023/2025, sparse
  block codes) report sparse coding achieving ~1000x BETTER operational capacity per dimension than dense
  bipolar at matched D -- but this directly CONTRADICTS Clarkson/Ubaru/Yang's own polynomial (worse-than-dense)
  scaling result for sparse-binary Bloom-filter-style set-intersection. Lane A's own read: the discrepancy is
  likely task/metric-dependent (factorization-via-resonator vs. set-intersection-estimation; l-infinity vs.
  dot-product similarity), not a resolved contradiction -- **sparse coding is NOT recommended as a default
  capacity fix for this design without a dedicated follow-up drill**, since the two most rigorous sources
  found disagree on its very existence as a general win.

### 5e. Chain-DEPTH capacity (recursive goal-respawn, section 3b) -- a FOURTH, separate capacity question

Section 3c's Lane-B finding (unbinding error compounds multiplicatively per hop) plus 5d's depth-40
binding-chain data (FHRR sits in the moderate-degradation band, not VTB's best-case) together define a FOURTH
capacity question this note initially conflated into 5b/5c: **how many recursive Goal->Attempt->
Outcome->new-Goal respawns (section 3b) can a chain survive before the decoded consequent is too noisy to
trust?** This is bounded by neither 5a (within-instance role count) nor 5b (across-type codebook size) nor
5c (nested-bundle depth) directly -- it is a REPEATED-UNBIND chain, the same shape Schlegel et al.'s depth-40
test measures, just applied to `CausalLinkRegister.query_effect_of`-style chaining (section 3b) instead of
raw sequential rebinding. Practically: since each hop pays a multiplicative fidelity cost, and FHRR is in the
MODERATE (not best-case) degradation band at depth 40, this note's own recommendation is to budget for a SMALL
number of recursive respawns (single digits) as the safe default, with per-hop cleanup-confidence logged and a
hard abstain (not a silent low-confidence guess) once confidence drops below a pre-registered floor -- exactly
the abstain-band discipline `hdlab.self_improving_loop.decide_keep_or_revert` and
`hdlab.consequence_learning_loop.py`'s own consolidation wrapper already use elsewhere in this codebase, a
DIRECT reuse of an existing discipline, not a new one.

---

## 6. Brain analog (structure/content factorization + chaining)

**Now full-text verified, not a working hypothesis.** Lane C fetched the Tolman-Eichenbaum Machine's primary
source directly (Whittington, Muller, Mark, Chen, Barry, Burgess & Behrens 2020, *Cell*, PMC7707106) and
confirms the specific mechanism, precisely: **entorhinal cortex (MEC) provides an abstract, task-general
STRUCTURAL code `g` (grid-cell-like, the transition-rule basis of a relational graph); lateral entorhinal
cortex (LEC) provides a CONTENT code `x` (sensory/stimulus-specific); hippocampus binds them via a literal
OUTER-PRODUCT/conjunctive operation into hippocampal conjunctive cells `p`, with associations stored in a
Hebbian weight matrix `M` between p-neurons.** Because `g` is stored independently of `x`, the SAME learned
structural code re-binds to novel sensory content in a new environment, giving zero-shot structural transfer
-- this is precisely section 1's structure/content split (role vocabulary = `g`-like, `concept_vector` filler
= `x`-like, `bind()` = the conjunctive operation) and section 4b's role-sharing-gives-analogical-transfer-for-
free claim, both independently licensed by the SAME mechanism. **Mandatory honest caveat, carried from the
same pattern the 08-06 sibling note's own "Lalisse & Smolensky" caveat already models**: TEM's conjunctive
binding is a literal OUTER PRODUCT (Smolensky TPR-exact), not a compressed operator -- it validates the
STRUCTURE/CONTENT FACTORIZATION property in general, not FHRR's specific complex-multiply operator; TEM is
also validated on spatial/small relational graphs, not linguistic scripts, so the mapping to language scripts
is Lane C's own (and this note's) INFERENCE, not a demonstrated identity. Report as "the brain factorizes
structure from content and binds them conjunctively for exactly this kind of task-general-code-transfer,"
never as "the brain uses FHRR" or "the brain uses circular convolution."

**A second, independent, and arguably MORE directly relevant finding**: Baldassano, Hasson & Norman (2018,
*J. Neuroscience*, "Representation of Real-World Event Schemas during Narrative Perception") found
**posterior medial cortex, mPFC, and superior frontal gyrus carry STORY-INDEPENDENT schema patterns** (e.g. a
"restaurant" script pattern) that generalize across DIFFERENT specific narratives, different subjects, and
even different modalities (audiovisual vs. audio-only) -- HMM-derived schema patterns from one set of stories
PREDICT script-type in held-out novel stories. This is direct neural evidence for structure/content-factorized
SCRIPTS specifically, in narrative comprehension specifically (not spatial navigation generalized by
analogy like TEM) -- the single most directly on-point finding this whole 3-lane search returned, and should
be the PRIMARY citation for this program's brain-foundational script claim, with TEM as the mechanistic
(how-would-binding-work) complement.

**For chaining**, two further confirmed mechanisms sharpen section 3: **Mattar & Daw (2018, *Nature
Neuroscience*)** show hippocampal replay chains successive ONE-STEP relational backups into MULTI-STEP
trajectories, prioritized by expected value of backup (EVB) -- including paths never directly/contiguously
experienced -- a precise, quantitative brain analog for exactly section 3b's recursive multi-hop chaining
(not just the positional 3a case `sequence_memory.py` already cited Foster-Wilson/Diba-Buzsaki for). **Zacks
et al. (2007, *Psychological Bulletin*, Event Segmentation Theory)** confirm the mechanism is a continuously-
PREDICTING working-memory event model whose divergence from perceived input (prediction error) triggers event
boundaries and model updates -- and **Alexander & Brown (2014, *Frontiers in Computational Neuroscience*,
extended PRO model, full-text verified with the exact equation)** give the specific computational form: mPFC
learns weighted stimulus->outcome associations `P = sum(S*W)` and continuously predicts upcoming events
generally (including registering surprise when a predicted event FAILS to occur) -- **this is a precise,
equation-level brain analog for section 3b's whole mechanism**: the "active goal" IS the continuously-held
prediction, the CONSEQUENT_ROLE decode IS the predicted-vs-actual comparison, and a failed/violated prediction
(CONTRADICT firing) is literally the same signal class as PRO's surprise-on-non-occurrence. mPFC's
schema/congruency-detection role (Gilboa & Marlatte 2017; van Kesteren et al. 2012 SLIMM model; Tse et al.
2007 schema-dependent one-trial consolidation) additionally grounds section 1d's SchemaExemplarBayes
instance-to-type induction proposal: mPFC computing a congruency/"resonance" signal between new content and
existing schemas, gating accelerated encoding for schema-CONSISTENT material, is the brain-level analog of
"cluster new script instances against existing type prototypes, consolidate on repeated confirmation" --
strengthening (not just analogizing loosely to) that proposal's fit to the program's brain-foundational
discipline.

---

## Cheap decisive test

**A 5-10-script-type toy codebook, CPU-only, reuses 3 existing modules, no new corpus.** Hand-author 5-10
script TYPEs using `hdlab.goal_outcome_relation`'s EXISTING 6 pools (`COGNITION_GOAL_POOL`,
`SKILL_GOAL_VERB_POOL`, `INFO_EXCHANGE_POOL`, `ERRAND_POOL`, `SKILL_TRAIN_POOL`, plus one CONFLICT/preclusion
type from `quality_relation`'s engagement axis) as the seed TRIGGER-role vocabularies -- these are ALREADY
on disk, not fresh hand-authorship. For each type, construct a script-INSTANCE vector via section 1a's
`bind_filler` pattern (TRIGGER_ROLE + CONSEQUENT_ROLE, using `lexical_similarity.concept_vector` for fillers
drawn from the pool). Test:

1. **Partial matching (section 2)**: given ONLY a TRIGGER-role cue, does `cleanup_family.iterative_attractor`
   / `k_NN_lookup` correctly identify the source script TYPE among the 5-10, at N=1024 (substrate default)?
2. **Capacity sweep (section 5b)**: repeat at 5 / 10 / 20 / 50 script types to find the FIRST measured
   degradation point specific to script content (not the field's generic random-vector curve) -- this is the
   measurement the 08-06 sibling note's own Prediction 7 already calls for and has not yet been run.
3. **Scramble control (standing discipline, pairscramble-must-collapse)**: shuffle the role<->filler pairing
   within each type; accuracy MUST collapse toward chance (1/n_types) -- proves the mechanism reads genuine
   role-structure, not generic concept-similarity (the same wrong-goal-leakage failure class flagged
   repeatedly in `research_psych_bridging_inference_situation_models_2026-08-09.md`).
4. **Chaining smoke (section 3a)**: bind a 3-scene toy sequence (e.g. REPAIR script: diagnose -> fix -> test)
   into `SequenceMatrix`, call `chain_predict(scene_1, depth=2, codebook=...)`, check scene_2/scene_3 decode
   correctly -- this exercises an ALREADY chain-grade-certified primitive on NEW (script-scene) content, a
   transfer check rather than a fresh capability test.
5. **Recursive-respawn depth smoke (section 3b/5e, Prediction 4)**: construct a toy 3-hop goal-failure chain
   (goal unmet -> new goal spawned from decoded consequent -> goal unmet again -> new goal spawned again) and
   log per-hop `CONTRADICT`/`ACHIEVE` verdict correctness + cleanup-confidence; check whether confidence decays
   monotonically and whether it stays correlated with correctness (the abstain-threshold viability check).
6. **Self-test methodology reuse**: adopt `EventBundleCodec`'s own 3-part self-test shape (round-trip
   accuracy >=0.98, THIN-LABEL/BAG-OF-ARGS baselines at chance, `encode_scrambled_event`-style permutation
   control) as the template for whichever module ends up implementing items 1-5 above -- a directly reusable
   test DESIGN, not just a code precedent.

---

## Falsifiable predictions (HARD-PASS / HARD-FAIL)

**Prediction 1 (partial matching + capacity, the core representation claim).**
P = **0.38** (deflated; REUSE of validated primitives on a genuinely new content class -- scripts, not
entities/events -- transfer is plausible but untested).
HARD-PASS: partial-TRIGGER-cue cleanup-argmax correctly identifies the source script TYPE at >=90% for at
least 15 script types at N=1024 (consistent with, within ~20% of, Schlegel/Neubert/Protzel's ~330-dim/15-item
curve scaled to N=1024's headroom) AND the scramble control collapses to within 10% of chance-level (1/n_types).
HARD-FAIL: accuracy is not appreciably above chance for ANY tested script-type count (5/10/20/50), OR the
scramble control does NOT collapse (indicating generic concept-similarity leakage, not genuine role-structure
reading) -- would mean direct bind/bundle/cleanup at N=1024 cannot support even toy-scale script codebooks,
forcing either bigger N or the resonator-decode build (section 5b) before any further script work.

**Prediction 2 (chaining transfer, section 3a).**
P = **0.55** (least deflated -- this is a near-mechanical reuse of an ALREADY chain-grade-certified primitive
on new content, closer to an engineering-transfer claim than a novel-mechanism claim).
HARD-PASS: `SequenceMatrix.chain_predict` on a 3-5-scene toy script sequence reproduces the SAME chain-grade
recall profile (near-1.0 at depth<=5) the c3 cell already certified for its own (non-script) content, with no
special-casing needed.
HARD-FAIL: chain_predict recall degrades measurably (>10%) below the c3 cell's certified depth-5 figure on
script-scene content specifically -- would indicate script-scene vectors have different statistical properties
(e.g. lower effective entropy from the small hand-authored pool vocabulary) that break the S-matrix's
assumptions, requiring a dedicated script-sequence chain-grade re-certification before relying on this reuse.

**Prediction 3 (nesting depth, section 5c -- structural, not yet buildable, flagged for when 4a lands).**
P = **0.30** (heavily deflated; genuinely no literature anchor exists for this claim per section 5c's own
finding -- this is the LEAST-grounded prediction in this note and should be treated as such).
HARD-PASS (once section 4a's chunking module is built): a 2-level nested script (sub-script bound as an
ATTEMPT_ROLE filler in a parent script) decodes both levels correctly (>=90%) at the SAME N=1024 the flat case
uses, with no dimensionality increase.
HARD-FAIL: 2-level nesting requires a >=2x dimensionality increase to hold >=90% decode accuracy at either
level -- would confirm nesting depth is NOT free at fixed N (matching the field's own qualitative "crosstalk
accumulates with depth" warning, never quantified) and script chunking needs its own capacity budget, not an
assumed pass-through of the flat-bundle numbers in 5a/5b.

**Prediction 4 (chain-DEPTH capacity, section 5e -- new this integration pass, from Lane B/A's combined
finding).**
P = **0.45** (moderately deflated; the underlying compounding-error mechanism is well-established across
multiple independently-verified sources, but the SPECIFIC depth at which our script-chaining use case becomes
unreliable is untested).
HARD-PASS: recursive goal-respawn chaining (section 3b) maintains >=85% correct CONTRADICT/ACHIEVE verdicts
through at least 3 recursive hops on a toy multi-hop fixture, with per-hop cleanup-confidence logged and
monotonically informative (higher confidence correlates with correct verdicts, enabling a principled abstain
threshold).
HARD-FAIL: accuracy drops below 60% by hop 2, OR per-hop confidence is uninformative (does not correlate with
correctness) -- would mean the multiplicative-compounding concern (section 3c/5e) is severe enough that even
shallow recursive chaining is unreliable without a per-hop re-grounding step (e.g. re-reading the original
text rather than chaining purely through decoded vectors), a materially different design than section 3b
currently proposes.

---

## Cross-thread synthesis

- **Directly extends, does not duplicate,** `research_script_half_synthesis_2026-08-09.md` (the goal<->outcome
  RELATION half, VerbNet end-state matching) -- that note answered WHAT relation to compute; this note answers
  HOW to REPRESENT the structure that relation is computed over. Both point at the SAME
  `AccumulateRegister`/`RelationRegister`/`CausalLinkRegister` family as the substrate home.
- **Directly extends, does not duplicate,** `research_psych_bridging_inference_situation_models_2026-08-09.md`
  (the chaining-mechanism-from-the-PSYCH side note, filed the same session) -- that note supplied the WHY
  (Suh & Trabasso automaticity, Trabasso's causal-network typed structure, the ACHIEVE/CONTRADICT query
  design) and a `GOAL_ROLE` extension proposal; this note supplies the HOW-TO-REPRESENT answer for the FULL
  script/schema structure (not just the 2-role goal/outcome case) plus the capacity and nesting analysis that
  note did not cover. Section 3b of this note is the SAME chaining step as that note's step 3-4, described
  from the representation side.
- **Reaffirms, does not revise,** `prior_art_vsa_hdc_for_language_2026-08-06.md`'s headline finding (a VSA
  system that reads narrative and tracks goals/outcomes/scripts is confirmed unbuilt prior art, empty across 4
  independent scours) and its grounding-wall framing (field-wide, not substrate-specific) -- this note's
  script-representation design is a further-specified instance of that same confirmed-empty space, not a
  revision of the finding.
- **Directly informs `notes/SYNTHESIS_grounding_wall_definitive_2026-08-06.md` and the Direction-B build
  plan** (`notes/direction_b_grounded_knowledge_build_plan_2026-08-09.md`) -- this note is the concrete
  representation-design answer the "how do scripts get represented at scale" open question in that plan's
  build sequence needed.

---

## Substrate-product implications

1. **The concrete next build, ranked by reuse-first discipline**: (a) extend `AccumulateRegister`'s pattern
   with a shared `SCRIPT_ROLE_VOCAB` module (section 1a) -- config/data extension, near-zero build cost; (b)
   port `EventBundleCodec`'s pattern to FHRR (section 1d, resolution (i)) so script-role fillers are structured
   events, not bare words -- mechanical, low-risk, an existing self-test suite to port against; (c) define the
   script-TYPE codebook seeded from `goal_outcome_relation`'s existing 6 pools (section 1b) -- data-supply, not
   new mechanism; (d) run the cheap decisive test above (now 6 items, including the chain-depth smoke) to get
   the FIRST script-specific capacity measurements (currently literature-extrapolated guesses, sections 5b/5e);
   (e) build the chunking/nesting calling pattern (section 4a) ONLY after (d) lands, since section 5c's honest
   finding is that nesting capacity is unmeasured and could change the design; (f) build the real/complex
   adapter for `SchemaExemplarBayesIndex` (section 1d) and try it as an emergent-TYPE-induction alternative to
   hand-seeding, once enough script instances accumulate to cluster meaningfully; (g) build resonator-style
   multi-factor decode (section 5b) only if/when (d)'s sweep shows direct argmax cleanup degrading before a
   useful script-type count is reached -- do not build it speculatively ahead of that measurement.
2. **Genuine BUILD flags, honestly separated from REUSE, per this drill's own charge**: (i) the chunking/
   nesting calling pattern (4a) -- zero new algebra, new calling code; (ii) resonator-network multi-factor
   iterative decode (5b) -- genuinely new module, no precedent anywhere in `hdlab/` today (confirmed absent by
   direct `ls` check); (iii) the FHRR port of `EventBundleCodec`'s pattern (1d) -- mechanical port of a proven
   pattern to a new dtype family, low risk but still new code; (iv) the real/complex adapter for
   `SchemaExemplarBayesIndex` (1d) -- small, mechanical (concatenate `[Re(v), Im(v)]`), but not yet built.
   Every other piece of this design (role-filler bind/bundle/unbind/cleanup, the TYPE/INSTANCE split's
   underlying operations, chaining mechanism 3a, analogical role-sharing 4b) is REUSE of already-owned, and
   mostly already-VET-confirmed, primitives.
3. **The capacity story should be reported honestly in FOUR separate tiers** (5a measured+fixed on our own
   data; 5b projected-from-field-curves-needs-own-measurement, now with a materially more precise ~7,000-dim
   planning figure for a mature ~100-type codebook per Gallant & Okaywe's worked table; 5c genuinely-unbounded-
   in-the-literature for nesting depth; 5e a newly-separated chain-DEPTH tier for recursive respawning, bounded
   by multiplicative per-hop error compounding) rather than one blended capacity claim -- conflating them would
   overclaim confidence the literature itself does not support (5c and the sparse-coding discrepancy in 5d
   specifically).
4. **Auditability, not accuracy-parity, remains the defensible product edge** (consistent with every prior
   note in this arc): a script-instance's decoded trace (which TYPE matched, which role's filler drove the
   match, which chaining step fired, at what per-hop confidence) is a strictly inspectable artifact at every
   stage of this design -- no opaque step is introduced by any of the REUSE or BUILD pieces above.
5. **The brain-foundational claim now has a materially stronger, narrative-specific citation to lead with**:
   Baldassano et al. (2018)'s story-independent schema patterns in narrative-comprehension-relevant cortex
   (not just TEM's spatial-navigation analogy) should be the PRIMARY brain-grounding citation for this
   program's script mechanism going forward, with TEM as the mechanistic complement -- a stronger position
   than this note had before section 6's integration pass.

---

## Calibration reasoning (P_deflated = 0.40 headline; per-prediction P 0.30-0.55)

Raw confidence in the DIRECT literature/substrate findings is now HIGHER than at the pre-integration pass:
7 of 9 Lane-A capacity sources and 2 of Lane-B/C's central claims (PSI primary, TEM primary) were full-text
verified with exact equations, not paraphrase; Baldassano et al. (2018) and Alexander & Brown (2014) add two
NEW, directly-on-point, full-text/equation-verified findings not previously in the KB. Combined raw confidence
in the direct literature/substrate findings (Schlegel/Neubert/Protzel's capacity curves now numerically
confirmed, Frady/Kleyko/Sommer's exact SNR equation, Clarkson/Ubaru/Yang's binding-cost theorem, the
resonator stability threshold with its exact formula, Trabasso & van den Broek's typed causal-network model,
the SequenceMatrix c3 cell's HARD_PASS chain-grade certification, the Tolman-Eichenbaum Machine's exact
outer-product mechanism, RelationRegister/CausalLinkRegister/EventBundleCodec's docstring-verified
construction) is high (~0.75-0.85). The ASSEMBLY into ONE script-representation design is still, and always
will be, THIS NOTE'S OWN SYNTHESIS, not literature-stated anywhere directly -- the TYPE-vs-INSTANCE split
(section 1b), the two-mechanism chaining decomposition (section 3), the four-tier capacity separation
(section 5, now including the new chain-depth tier 5e), the EventBundleCodec-port recommendation (section
1d), and the brain-analog mapping (section 6, now evidence-backed but still an INFERENCE from TEM's spatial
domain to linguistic scripts, and from Baldassano's correlational schema-decoding to this note's specific
bind/bundle mechanism) -- capped at the mandatory 0.50 novel-synthesis ceiling and set at 0.40 (raised from
the pre-integration 0.38 estimate, but not higher) because: (i) NONE of the 4 falsifiable predictions have
been run; (ii) the nesting-depth prediction (Prediction 3) still rests on a confirmed LITERATURE GAP, not a
positive finding, structurally weaker evidence; (iii) the sparse-coding capacity discrepancy (section 5d) is
an genuinely UNRESOLVED disagreement between two rigorous sources, correctly excluded from any capacity
recommendation rather than papered over; (iv) the brain-analog section, while now evidence-backed, still
requires an inference step (spatial-cognition mechanism -> linguistic script mechanism) this note cannot
independently verify.

---

## Citations (verified count)

**Carried forward from 3 sibling notes read in full today (not re-verified, cited by title):**
`research_script_half_synthesis_2026-08-09.md` (Schank & Abelson 1977; Trabasso & van den Broek 1985 via the
psych-bridging note's independent read; Kipper-Schuler VerbNet; SemLink; ATOMIC; Kintsch 1988; Bower Black &
Turner 1979); `prior_art_vsa_hdc_for_language_2026-08-06.md` (Plate 1995/2003; Kanerva 1988/2009/2010; Gayler
2003; Smolensky 1990; Schlegel/Neubert/Protzel arXiv:2001.11797; Frady/Kent/Olshausen/Sommer 2020; Eliasmith
et al. 2012 Science; Kleyko et al. survey; Harnad 1990); `research_vsa_hdc_state_of_mind_prior_art_scour_
2026-07-17.md` (Voelker & Eliasmith doubly-latched integrator; Choo 2010 OSE; Recchia et al. 2015;
Frady/Kleyko/Sommer SNR law; Hsin/Cummins arXiv:2301.10352; Grosz & Sidner 1986; ACT-R HDM/Kelly et al.);
`research_psych_bridging_inference_situation_models_2026-08-09.md` (Trabasso & van den Broek 1985; Trabasso &
Sperry 1985; Stein & Glenn 1979; Suh & Trabasso 1993; van den Broek Landscape model; Zwaan & Radvansky 1998;
Blum & Furst 1997 GraphPlan mutex).

**This session's own substrate reads (primary source = the code itself):** `hdlab/situation_model_
accumulate.py` (AccumulateRegister, CausalLinkRegister, RelationRegister -- all read in full);
`hdlab/situation_model_multibank.py` (MultiBankAccumulateRegister, read in full); `hdlab/lexical_similarity.py`
(concept_vector, CONCEPT_FEATURES, read in full); `hdlab/quality_relation.py` (opposition channels, read in
full); `hdlab/cleanup_family.py` (5 cleanup primitives + 2 bundle readouts, read in full);
`hdlab/sequence_memory.py` (SequenceMatrix, chain_predict, read in full); `hdlab/binding.py`,
`hdlab/bundling.py` (bind/unbind/bundle dispatch, read in full); `hdlab/working_memory.py` (multi-bank
chain-grade envelope constants, read in full); `hdlab/goal_outcome_relation_grounded.py` (RelationRegister
usage pattern, read in full); `hdlab/event_bundle.py` (EventBundleCodec, read in full, coordinator-flagged
mid-drill); `hdlab/schema_exemplar_bayes.py` (SchemaExemplarBayesIndex, read in full, coordinator-flagged
mid-drill); `hdlab/frame_induction.py`, `hdlab/consequence_learning_loop.py`, `hdlab/goal_outcome_relation_
grounded.py` (skimmed for acquisition-loop/consolidation pattern precedent); `data/capability_registry.jsonl`
(queried for registered organ IDs: `situation_model_accumulate_register_organ`,
`working_memory_multibank_K_capacity`); confirmed absent by direct `ls` check: no `resonator*.py` anywhere in
`hdlab/`.

**3 fresh Sonnet lit-scan lanes dispatched this cycle, all completed and integrated (sections 3c, 5d, 5e, 6):**
Lane A (capacity math, 9 primary sources chased, 7 full-text-verified): Frady, Kleyko & Sommer 2018 (*Neural
Computation* 30(6), arXiv:1803.00412, exact SNR eq. 35 verified); Gallant & Okaywe 2013 (*Neural Computation*
25(8), arXiv:1501.07627, worked capacity table verified); Thomas, Dasgupta & Rosing 2021 (*JAIR* 72,
arXiv:2010.07426); Clarkson, Ubaru & Yang 2023 (arXiv:2301.10352, binding-cost theorem verified); Frady, Kent,
Olshausen & Sommer 2020 + Kent, Frady, Sommer & Olshausen 2020 (Resonator Networks 1&2, *Neural Computation*
32(12), D_f/N<=0.056 formula verified); Schlegel, Neubert & Protzel arXiv:2001.11797 (exact figures
re-confirmed); Hersche et al. 2023/2025 (sparse block codes, arXiv:2303.13957, full-text verified); Laiho,
Poikonen, Kanerva & Lehtonen 2015 (secondary only, paywalled); Kleyko et al. survey Part I (structural pointer
only, fetch truncated). Lane B (sequence/chaining/analogy, full-text verified: Kleyko survey Part I position-
encoding section, Cohen, Widdows, Schvaneveldt & Rindflesch 2010 PSI *J. Biomed. Inform.* PMC full text):
Kanerva 2009 (*Cognitive Computation*, permutation formalism); Plate 1992 NeurIPS/1995 *IEEE TNN*/2003 book
(trajectory association, secondary -- PDF extraction failed); Choo (PhD thesis, Waterloo, OSE model, full-text
via tool summary); Eliasmith *How to Build a Brain* 2013 + Stewart/Choo/Eliasmith Spaun basal-ganglia papers
(secondary, multiply corroborated); Cohen, Widdows, Rindflesch et al. 2012 (PSI discovery-pattern 2-hop
chaining, secondary/paywalled); Kanerva 2010 AAAI-FS "dollar of Mexico" (secondary, re-confirmed); Gayler &
Levy 2009 (analogical mapping, secondary); Rachkovskij & Kussul 2001 (*Neural Computation*, context-dependent
thinning, secondary); Emruli, Gustafsson & Sandin 2013/2014 (*Cognitive Computation*, secondary); Mejri et al.
2024 RESOLVE (arXiv:2411.08290, secondary); Rel-SAR arXiv:2501.11896 (2025, secondary). Lane C (hippocampal-
entorhinal schema neuroscience, 2 primary sources full-text-verified): **Whittington, Muller, Mark, Chen,
Barry, Burgess & Behrens 2020 (*Cell*, "The Tolman-Eichenbaum Machine," PMC7707106, outer-product mechanism
verified)**; **Alexander & Brown 2014 (*Frontiers in Computational Neuroscience*, extended PRO model, exact
equation verified)**; Tse et al. 2007 (*Science*, schema consolidation, secondary); van Kesteren, Ruiter,
Fernandez & Henson 2012 (*Trends in Neurosciences*, SLIMM model, secondary); Gilboa & Marlatte 2017 (*Trends
in Cognitive Sciences*, secondary); Mattar & Daw 2018 (*Nature Neuroscience*, prioritized replay, secondary
but well-corroborated normative paper); Olafsdottir, Bush & Barry 2018 (*Current Biology* review, secondary);
**Baldassano, Hasson & Norman 2018 (*J. Neuroscience*, "Representation of Real-World Event Schemas during
Narrative Perception," secondary/high-confidence -- the single most directly on-point finding this drill
returned)**; Zacks, Speer, Swallow, Braver & Reynolds 2007 (*Psychological Bulletin*, Event Segmentation
Theory, secondary, convergent across sources).

---

## Status

Written per research-agent contract. USER-locked discipline applied: **no `exp_dev_handoff_*.md` or
`strategy_request_to_*.md` routing files written as SEPARATE routing artifacts for the "delivered" pointer**
(ferry mechanism deprecated) -- every actionable pointer is inline above. A companion
`exp_dev_handoff_research_vsa_script_representation_chaining_2026-08-09.md` IS written (per this task's own
"exp_dev companion file when findings are actionable" instruction, which is a DELIVERABLE-CONTENT requirement
from the dispatching agent, not the deprecated ferry mechanism) since this note proposes a concrete,
buildable cheap decisive test with pre-registered anchors. No cap_map or strategy files modified.
