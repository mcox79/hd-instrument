# Brain mechanism of PRECISE EVENT ALIGNMENT: telling one specific event apart from SIMILAR events in the same script

Research drill for `the_reader_cannot_reason_over_its_own_situation_model_on_real_inference`.
Date 2026-09-01. Author: SOLVER (finer brain-fidelity drill on the RE-LOCALIZED wall).
ONLINE-literature synthesis; **lit-scan calibration penalty applied** — every "should" is a DESIGN
HYPOTHESIS pending our own measurement, not an inherited number.

---

## The wall this drill answers (RE-LOCALIZED — a different wall from the two sibling temporal drills)

The two Aug-31 drills concluded the before/after wall was a **KNOWLEDGE gap** (a missing canonical-order
store; >60% of MCScript2 WHEN questions "need script knowledge"). The new **empirical error-localization
drill has REFUTED the strong form of that framing** and moved the diagnosis one layer finer:

- The answers' events are **NARRATED IN THE PASSAGE for ~90–98%** of the n≈301 held-out symmetric
  before/after questions → this is **NOT** a commonsense-knowledge-not-in-text gap. The content is present.
- Yet neither this passage's own event order (semantic-aligned episodic = **0.547**) NOR a learned
  cross-narrative canonical script order (`transitive_ordering`, semantic-aligned = **0.593**) reliably gives
  gold; both cap ~0.55–0.59 over a ~0.52 floor. The order SIGNAL is real (learned schema beats its
  shuffled-order twin CI-sep, and beats the single passage's order — cross-narrative denoising helps).
- **THE BOTTLENECK IS EVENT-ALIGNMENT PRECISION.** Mapping a PARAPHRASED question/candidate event ("get out
  of the shower", "watch the wire push the candy") to the RIGHT specific event among a script's several
  SIMILAR events. The current aligner is a **coarse 12-d grounded sensorimotor cosine**, which cannot
  disambiguate which of several near-synonymous / near-cooccurring events is meant, so before/after is read
  off the **WRONG event pair ~40% of the time**.

So this is a **similarity-KERNEL / representation problem**, not a missing-store problem. The reconciliation
with the sibling drills: the canonical order IS learnable and mostly present once events are aligned by
meaning; what was mislabeled "missing knowledge" is largely **mis-alignment of the cue to the event that
carries the knowledge**. This drill asks: how does the brain achieve precise event identity, and which
glass-box representation converts the 0.59 near-positive into a clean CI-separated positive.

**Prior-arc work on precise event alignment / pattern separation of events: NONE** beyond the two sibling
temporal drills (this is the finer, third drill). The `content_addressable_retrieval` and
`bound_event_backbone` organs already exist and are the composition candidates (read below).

---

## Q1 — How the brain identifies/aligns a SPECIFIC event from a paraphrased cue, distinct from SIMILAR events

**The load-bearing fact: the brain has a DEDICATED circuit whose only job is to keep SIMILAR experiences
from colliding — hippocampal PATTERN SEPARATION, in the dentate gyrus (DG) → CA3. This is exactly the
operation our coarse cosine LACKS.** PINNED.

**(a) DG/CA3 pattern separation = orthogonalizing similar inputs into non-overlapping codes.**
Pattern separation is "a neural operation supporting mnemonic discrimination of highly similar memories by
**orthogonalizing** neural inputs into nonoverlapping representations" — and it is **favored precisely when
inputs are highly similar** (Yassa & Stark 2011; Bakker, Kirwan, Miller & Stark 2008 *Science* — high-fidelity
CA3/DG signal that treats highly similar inputs as distinct; Leutgeb et al. 2007 *Science* — DG remaps to
small input changes while CA3 pattern-completes). Human DG volume predicts behavioral mnemonic-discrimination
accuracy; damage to human DG impairs discrimination of complex NOVEL, overlapping objects (Sci Reports 2017;
ScienceDirect 2022). **This is the missing ingredient stated in brain terms: the brain does NOT rely on a
smooth similarity metric to tell "get IN" from "get OUT of the shower"; it EXPANDS overlapping inputs into a
sparse, high-dimensional CONJUNCTIVE code where they no longer overlap.** Our 12-d cosine is the opposite: a
smooth, LOW-dimensional, holistic kernel that maximizes collapse.

**(b) The decisive new result — pattern separation happens BY MEANING, not just by perceptual features.**
The single most on-point citation: **"The human hippocampus can pattern separate memories by MEANING"**
(PNAS 2026, `10.1073/pnas.2603114123`). The hippocampus orthogonalizes memories that are close in **semantic
content**, not merely in surface/perceptual form. This is exactly our regime: the events collide because they
are close in MEANING (near-synonymous predicates, near-cooccurring in the same script), and the brain has a
mechanism that separates them at the level of meaning. Our coarse cosine has no such mechanism — it is the
raw semantic-similarity space with no separation stage on top.

**(c) The complementary hub: ATL/AG graded semantic coding + relational conjunction.** The anterior temporal
lobe is a transmodal semantic hub encoding a **graded, multidimensional** concept space at multiple
granularities (Lambon Ralph hub-and-spokes; biorxiv 2022 graded ATL space). For EVENTS specifically, the
**angular gyrus and ventral ATL encode event-concept similarity** (RSA; left vATL events>objects F(42)=5.1,
p=.03; right AG F(42)=10.95, p=.002; PMC10839851) — BUT that study modelled events **HOLISTICALLY with
word2vec** ("treating events holistically rather than decomposing them into argument structures"), which is
**precisely the failure mode of our coarse cosine**: a holistic whole-event vector does not individuate
similar events. The individuation comes from **conjunctive/relational coding** — left vATL's stronger
connectivity to posterior MTG (which "codes causal relations between objects") during event processing, and
the hippocampal **conjunctive/relational binding** literature (O'Reilly & Rudy 2001 "Conjunctive
Representations…"; Konkel & Cohen 2009 — relational vs conjunctive binding dissociate; the hippocampus binds
"arbitrary relations among constituent elements" while maintaining the ability to "discriminate the unique
aspect of each event").

**PINNED answer to Q1:** precise event identity is **a CONJUNCTION of (predicate × its arguments × context),
pattern-SEPARATED so near-neighbors do not collide — NOT a predicate/whole-event similarity.** Two operations
are needed and they are complementary: (i) a **graded semantic input** (ATL/EC) so a PARAPHRASE still lands
near its target (pattern COMPLETION from a partial cue, CA3), and (ii) a **conjunctive expansion / separation**
(DG→CA3) so two events that share a verb but differ in one argument become non-overlapping. Our cosine has (i)
in impoverished 12-d form and entirely LACKS (ii). **The wall is exactly where the brain's pattern-separation
stage sits and where our metric collapses.**

---

## Q2 — Event individuation is driven by the BOUND ARGUMENTS and relational context, not the verb alone

Strong, convergent PINNED evidence that arguments/particles/context — not the predicate — individuate events:

- **Thematic uniqueness (Carlson 1998, "Thematic Roles and the Individuation of Events").** Thematic roles are
  RELATIONS between an entity and an event; "principles of individuation including thematic uniqueness mean
  events take only singular values" — i.e. an event is individuated by its role-bound participants, not by the
  predicate type. Two "get" events are DIFFERENT events because their PATH/PATIENT arguments differ.
- **Event segmentation is triggered by a CHANGE IN ANY situational dimension — character, object, goal, space,
  time — not by the verb.** Event-Indexing Model (Zwaan, Langston & Graesser 1995): five dimensions
  (space/time/goals/actions/characters) are continuously monitored; a change in ANY ONE triggers a new event
  index (Zacks & Swallow; Kurby & Zacks). "All readers tracked the character dimension." This is direct
  cognitive evidence that WHO and WHAT (arguments) individuate an event boundary — the same argument change
  that our verb-dominated cosine ignores is what the brain uses to split events.
- **Predicate-argument structure is the semantic unit, and "not directly discernible from syntax/verb alone."**
  Thematic-role databases (PropBank, FrameNet) codify the roles arguments take; thematic-fit work models the
  compatibility of a (predicate, argument, role) TRIPLE, not the verb alone (arXiv 2410.15173). "Events and
  their participants require additional semantic analysis beyond just the verb."
- **SEM (Franklin, Norman, Ranganath, Zacks & Gershman 2020, *Psych Review*) — the canonical computational
  model, and OUR pinned FHRR basis.** SEM is a neuro-symbolic generative model over **structured symbolic
  scenes embedded in a vector space**; events are **role-filler bound** structures; the model "infers missing
  fillers in their appropriate ROLES from co-occurrence statistics" and generalizes across event types via a
  shared representational space. This is the exact object our `bound_event_backbone` builds (FHRR bound token
  over {AGENT, PATIENT, PRED, TENSE}) — and SEM's whole point is that event identity lives in the ROLE-FILLER
  CONJUNCTION.

**PINNED answer to Q2:** align on the **FULL bound token — predicate + AGENT + PATIENT + PATH/PARTICLE +
manner/context — NOT verb+object.** The specific failures cited ("get OUT of the shower" vs "get IN"; "watch
the wire PUSH the candy") are precisely PATH/PARTICLE and PATIENT/relational-argument distinctions; a verb(+one
object) aligner is structurally blind to them. The 12-d coarse vector has no dedicated slots for path/particle
or for the second argument of an embedded predicate — so it cannot carry the very features that individuate.

---

## Q3 — Is `bound_event_backbone` the brain-faithful fix, or is a DG pattern-separation step the missing ingredient? (They are the SAME operation — but each existing organ is HALF of it)

I read both candidate organs' actual code. The decisive finding: **neither organ ALONE solves the wall, and
each fails for a DIFFERENT half of the pattern-separation-by-meaning operation.**

**`bound_event_backbone` (read: `hdlab/bound_event_backbone.py`)** builds ONE FHRR bound token per event over
{AGENT, PATIENT, PRED, TENSE}; `resolve()` scores by FHRR cleanup ≈ **number of shared EXACT (role,filler)
terms**. This is a genuine CONJUNCTIVE role-filler code (the Q2 structure) — BUT its fillers are
`sym(s) = unit_phase_vec seeded by sha256(s)`, i.e. **exact-hash ORTHOGONAL symbols**. Consequence:
- It has **maximal pattern SEPARATION** — "get in" and "get out" are orthogonal, never collide. Good.
- But it has **ZERO within-slot generalization** — the PARAPHRASE "exit" vs "get out of" are ALSO orthogonal,
  so a paraphrased cue scores ~0 against its true event. This is the **DG with no graded EC→CA3 input**:
  perfectly separated, cannot pattern-COMPLETE from a fuzzy cue. It would fail our wall from the opposite side
  (the sibling SOLVED.md already found symbol/lexical alignment TIES the twin at 0.48–0.49).

**`content_addressable_retrieval` (read: `hdlab/content_addressable_retrieval.py`)** scores by the **ADDITIVE
sum** of per-feature graded similarities (Lewis & Vasishth; ACT-R). Its fillers CAN be graded semantic codes:
- It has **within-slot generalization** — a paraphrase matches. Good.
- But its own docstring is explicit: **"it does NOT and SHOULD NOT confer immunity to similarity interference:
  with genuinely similar competitors, additive is fooled too — that is the FAN EFFECT."** Because the score is
  a SUM, a shared high-weight verb DOMINATES and the several similar events tie — exactly our ~40% mis-alignment.
  This is the **smooth additive kernel with no separation stage**.

**So the two organs bracket the answer: `bound_event_backbone` = conjunctive structure + NO graded semantics
(over-separated); `content_addressable_retrieval` = graded semantics + additive combination (under-separated).
The brain's DG-pattern-separation-by-meaning is the operation that sits BETWEEN them, and neither organ is it
yet.** The missing ingredient is a **CONJUNCTIVE combination of GRADED per-role semantic similarities** — a
soft-AND, not a sum, over role-bound graded fillers — plus (optionally) a DG-style high-dimensional sparse
expansion to escape the 12-d collapse. That is a small, buildable modification that COMPOSES the two organs
rather than a new mechanism.

**Why the combination rule (product/soft-AND vs sum) is the crux, and is brain-faithful:** DG pattern
separation makes overlapping inputs non-overlapping — the computational signature of a **conjunction** (all
roles must match) rather than a **disjunction/sum** (any strong role suffices). With a soft-AND, a mismatch on
the PATH role ("out" vs "in") multiplicatively drags the whole alignment score down for the wrong candidate,
so the correct "get OUT" separates from "get IN" even though they share predicate+patient — while a graded
per-role kernel keeps "exit"≈"get out" matchable WITHIN the path/predicate slots. This gives BOTH properties
the wall needs. (`content_addressable_retrieval`'s own note that a multiplicative composite "orthogonalises the
whole match when ONE feature is wrong" is the SAME mechanism — that "collapse" is a BUG for partial cues but a
FEATURE for separating similar competitors; the fix is a soft/temperature-controlled AND that separates
competitors without killing genuine paraphrases, tuned by one sweepable knob.)

---

## Q4 — HONEST CEILING: how much of the residual is fixable alignment vs an irreducible floor

**There IS an irreducible floor, but the literature + the new empirical localization say it is a MINORITY of
the residual; most of the ~40% mis-alignment is fixable.** Evidence for each source of irreducibility:

- **Some before/after pairs are genuinely UNDER-DETERMINED in the episode.** Temporal order in a situation
  model is "inferred from sometimes UNDERSPECIFIED linguistic information" (Dixon 2019, *Discourse Processes*,
  "Distraction and Temporal Order in Narrative Situation Models"); "causal relationships do NOT suffice to
  determine the order of events" and the model must carry separate order information. When two events co-occur
  or are unordered in the actual episode, no situation model — brain or ours — recovers a unique gold order.
- **Eventuality-type / state-before-event DEFAULTS are genuine commonsense, not text.** Marx & Wittenberg 2024
  (*Glossa Psycholinguistics*, N=930, preregistered): readers systematically order **states before events**
  and **longer states before shorter**, "regardless of sentence order." A residual slice of before/after is
  answered by these commonsense defaults (a stative "the shower was running" precedes the eventive "she got
  out") — genuinely outside a text-derived episodic model.
- **Discourse order ≠ chronology.** Where narration departs from chronology (flashback, pluperfect), order must
  be reconstructed; the sibling drill already showed our episodic reader RECOVERS these (0.74 vs 0.26) — so this
  slice is largely a SOLVED sub-case, not the ceiling.
- **Humans answer at 97.4% (MCScript2) because the mPFC/PMC schema supplies the canonical order for free**
  (Baldassano, Hasson & Norman 2018; "mPFC confers ordinality"). Humans are NOT reading it off the episode —
  they retrieve a schema default. That is the ceiling that a learned canonical-order prior (already built,
  underpowered) is meant to reach, and the new empirical result shows that prior IS a real signal (0.593,
  beats shuffled twin CI-sep) once events are aligned by meaning.

**Honest split (DESIGN ESTIMATE, calibration-penalized — to be MEASURED, not asserted):** the new
error-localization drill's own numbers are the strongest evidence — events narrated 90–98%, order signal real
(twin loses CI-sep), and the residual concentrated in mis-alignment (~40% wrong pair). I estimate **the
alignment-precision component is the DOMINANT and fixable majority (order of ~25–35 of the ~40 lost points),
with an irreducible floor of roughly ~10–20% of items** (genuinely-unordered pairs + state-before-event
commonsense defaults + benchmark annotation noise). This predicts the fix should lift accuracy from ~0.59
toward ~0.70–0.80, NOT to ~0.97 — a clean CI-separated positive over the ~0.52–0.55 floors is reachable, a
human-level ceiling is not. **This is falsifiable:** if a precise conjunctive aligner does NOT beat the coarse
cosine on a direct alignment-accuracy probe (below), the wall is not alignment and this estimate is wrong.

---

## Q5 — VERDICT + the single highest-leverage glass-box build

### VERDICT: **(a) — richer CONJUNCTIVE / bound event codes for alignment is the fix.**
Specifically: **a grounded conjunctive event code with a soft-AND (multiplicative) per-role semantic kernel,
built by MARRYING the two existing organs** — `bound_event_backbone`'s role-filler CONJUNCTION structure +
`content_addressable_retrieval`'s GRADED per-role matching + distributional/grounded meaning fillers — with the
combination rule changed from ADDITIVE to soft-AND, and (optionally) a DG-style sparse high-dim expansion to
escape the 12-d collapse. This is option (a), and it is the brain's DG-pattern-separation-BY-MEANING operation
(PNAS 2026) rendered glass-box. It is NOT a still-different mechanism (b), and it is NOT largely an intrinsic
ceiling (c) — the ceiling is real but a minority (Q4).

### The single build to run first (concrete, glass-box, no LLM at inference)

**`grounded_conjunctive_event_aligner`** — replaces ONLY the aligner's similarity kernel; everything downstream
(the validated `transitive_ordering` read-out, the episodic-override, the shuffled-order twin) is UNCHANGED.

1. **Represent every event** (each script/passage event AND each question/candidate event) as a set of
   per-ROLE **graded** fillers, NOT a 12-d holistic vector and NOT exact-hash symbols:
   `{PRED: v, AGENT: v, PATIENT: v, PATH/PARTICLE: v, MANNER/CTX: v}`, where each `v` is a
   **distributional/grounded meaning vector** (reuse `distributional_meaning_channel` + the grounded codes that
   already lifted the sibling result to 0.593). Crucially ADD the **PATH/PARTICLE** and the **second/embedded
   argument** as first-class roles — these are the individuating features the 12-d cosine lacks (Q2).
2. **Alignment score = soft-AND over shared roles**, not the additive sum:
   `score(cue, ev) = Π over roles r present in both of  sim(cue_r, ev_r) ** w_r`  (a geometric mean / product;
   drop a role missing from either side so it stays partial-cue robust). The PRODUCT enforces that ALL roles
   agree — a path mismatch ("out" vs "in") multiplicatively suppresses the wrong candidate (DG-style
   separation), while graded `sim` keeps "exit"≈"get out" within a slot (CA3-style completion).
3. **(Optional, if step 2 under-separates) DG sparse expansion:** expand the concatenated per-role graded code
   into a high-dimensional sparse conjunctive code via random projection + k-WTA (reuse
   `hippocampal_encoder`'s DG stage) and match there — the literal DG operation, escaping the 12-d capacity
   collapse. Match on the expanded code; the multiplicative kernel of step 2 is the transparent first cut.
4. **One sweepable OUR-INVENTION knob — the separation SHARPNESS** (the temperature/exponent on per-role `sim`,
   or the k-WTA sparsity). Too soft → reverts to the additive fan-effect collapse; too sharp → reverts to
   `bound_event_backbone`'s orthogonal brittleness (kills paraphrases). Sweep to the point that separates
   similar events without killing genuine paraphrases. This is the sole tuned parameter; it is NOT copied from
   biology (0.2% DG sparsity is a constraint we do not share — sweep it, do not adopt it).

### The DECISIVE go/no-go controls (build these into the cell)
- **Direct alignment-precision probe (the discriminator that isolates THIS wall):** on paraphrased cues with
  KNOWN gold events, measure top-1 alignment accuracy among the script's SIMILAR distractors for three kernels
  — (i) coarse 12-d cosine [baseline], (ii) additive graded [`content_addressable_retrieval`], (iii)
  conjunctive soft-AND graded [the build]. **PASS predicts (iii) >> (i) and (iii) > (ii), CI-separated.** If
  not, the wall is not alignment (Q4 estimate falsified) — a clean can-fail.
- **Role-scramble info-free twin:** bind AGENT-filler to the PATIENT role etc. If alignment precision drops
  CI-sep, the role STRUCTURE (conjunction) is load-bearing, not merely "more features."
- **End-to-end bar:** the shuffled-ORDER twin must still LOSE CI-sep (order signal preserved), AND the model
  must now **CI-separate over the similarity floor** (the positive the sibling near-miss did not reach), with a
  graceful multi-hop degradation.

### PINNED vs OUR-INVENTION (this drill)
- **PINNED:** DG/CA3 pattern separation orthogonalizes SIMILAR inputs, favored when inputs are similar, and
  operates BY MEANING (Bakker 2008; Yassa & Stark 2011; PNAS 2026). Event identity is a role-filler CONJUNCTION
  individuated by its ARGUMENTS/particles, not the verb (Carlson 1998; Zwaan Event-Indexing; SEM/Franklin 2020;
  PropBank/thematic-fit). ATL/AG code events but holistic word2vec does NOT individuate — decomposition into
  predicate+arguments does. Separation (DG) + graded completion (CA3/ATL) are complementary and BOTH required.
- **OUR-INVENTION-UNDER-TEST:** the soft-AND combination rule and its sharpness knob; the specific role set
  (adding PATH/PARTICLE + second argument); the DG expansion dim + k-WTA sparsity; the per-role weights `w_r`.
  All sweepable; none is copied from a biological constant.

---

## Key citations
- Bakker A., Kirwan C.B., Miller M. & Stark C.E.L. (2008). Pattern separation in the human hippocampal CA3 and dentate gyrus. *Science* 319:1640–1642.
- Yassa M.A. & Stark C.E.L. (2011). Pattern separation in the hippocampus. *Trends in Neurosciences* 34:515–525.
- Leutgeb J.K., Leutgeb S., Moser M-B. & Moser E.I. (2007). Pattern separation in the dentate gyrus and CA3 of the hippocampus. *Science* 315:961–966.
- **[the money citation]** The human hippocampus can pattern separate memories by MEANING (2026). *PNAS* 10.1073/pnas.2603114123.
- O'Reilly R.C. & Rudy J.W. (2001). Conjunctive representations in learning and memory: principles of cortical and hippocampal function. *Psychological Review* 108:311–345.
- Konkel A. & Cohen N.J. (2009). Relational memory and the hippocampus: representations and methods. *Frontiers in Neuroscience* 3:166. (Relational vs conjunctive binding dissociate.)
- Carlson G.N. (1998). Thematic roles and the individuation of events. In *Events and Grammar* (Springer). (Thematic uniqueness → arguments individuate events.)
- Zwaan R.A., Langston M.C. & Graesser A.C. (1995). The construction of situation models: an event-indexing model. *Psychological Science* 6:292–297. (5 dimensions; change in any triggers a new event.)
- Franklin N.T., Norman K.A., Ranganath C., Zacks J.M. & Gershman S.J. (2020). Structured Event Memory: a neuro-symbolic model of event cognition. *Psychological Review* 127:327–361. (Role-filler bound events; infers missing fillers per role; OUR pinned FHRR basis.)
- Anterior-temporal / angular-gyrus event vs object concepts (2024). *PMC10839851*. (AG/vATL code event similarity; word2vec HOLISTIC → does NOT individuate similar events.)
- Baldassano C., Hasson U. & Norman K.A. (2018). Real-world event schemas during narrative perception. *J Neurosci* 38(45):9689. ("mPFC confers ordinality"; humans' schema default.)
- Dixon P. & Bortolussi M. (2019). Distraction and temporal order in narrative situation models. *Discourse Processes* 56:5-6. (Order from underspecified info; causality ≠ order.)
- Marx E. & Wittenberg E. (2024). Eventuality type predicts temporal order inferences in discourse comprehension. *Glossa Psycholinguistics* (N=930). (States-before-events default = genuine commonsense floor.)
- Lewis R.L. & Vasishth S. (2005). An activation-based model of sentence processing as skilled memory retrieval. *Cognitive Science* 29:375–419. (Additive cue-based retrieval; the fan effect our aligner must overcome.)

---

## TLDR (plain English)
Our reader keeps failing "did X happen before or after Y" questions, and we now know exactly why: it is NOT
that the story hides the answer (the events ARE in the text 90–98% of the time), and it is NOT that the
reasoning is broken. It is that the reader **matches the question's wording to the WRONG event**. A question
says "get out of the shower"; the story has several similar moments ("get in", "wash", "get out", "dry off"),
and the reader's crude 12-number "meaning fingerprint" is too blurry to tell them apart, so it grabs the wrong
one about 40% of the time and then reads off the wrong order. The brain has a dedicated part (in the memory
system, the dentate gyrus) whose ONLY job is to keep similar experiences from blurring together — and a 2026
study shows it does this **by meaning**, exactly our problem. It works by identifying an event not by its verb
but by the WHOLE package — who did what to whom, and crucially the little words like "in" vs "out" — and by
requiring **all** of those to match (an AND), not just the verb. We already have the two half-solutions in our
toolbox: one part builds the "whole package" but is too strict to recognise reworded events; the other
recognises rewording but is too loose and gets fooled by similar events. The fix is to **combine them**: build
each event as its full who-did-what-with-which-particle package, made of soft "meaning" pieces so rewording
still matches, but require ALL the pieces to agree so similar events separate. This is a small build on top of
what exists, and it should turn the current near-miss (~59%) into a clear win over the baselines — though not
to human level, because a genuine slice (~10–20%) of these questions is truly commonsense or genuinely
unordered and no amount of better matching will recover it.

## QUESTIONS
None for the owner. One DESIGN choice is the solver's to make (not a question): build the direct
alignment-precision probe FIRST as a cheap can-fail discriminator (it isolates the wall in one cell before the
full end-to-end build) — recommended.

## NEXT STEPS
1. Build `grounded_conjunctive_event_aligner` as a proposed diff (compose `bound_event_backbone`'s role-filler
   conjunction + `content_addressable_retrieval`'s graded matching + `distributional_meaning_channel` fillers;
   change ADDITIVE→soft-AND; add PATH/PARTICLE + 2nd-argument roles). Do NOT land it until it clears the bar.
2. Run the direct alignment-precision probe first (coarse cosine vs additive vs soft-AND conjunctive on
   paraphrased-cue → gold-event among similar distractors) — the cheap can-fail that isolates this wall.
3. If (2) passes, wire the new kernel into the aligner and re-run the end-to-end before/after bar: shuffled-
   ORDER twin must still lose CI-sep, and the model must now CI-separate over the similarity floor.
4. Propose the AUDIT UPDATE: the before/after wall was RE-LOCALIZED from "missing canonical-order KNOWLEDGE"
   to "event-ALIGNMENT PRECISION" — a coarse holistic cosine with no pattern-separation stage; the brain-
   faithful fix is DG-pattern-separation-by-meaning = a grounded CONJUNCTIVE (soft-AND) role-filler event code.
