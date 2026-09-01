# Brain mechanism of the TEMPORAL-ORDER wall: EPISODIC "when in this story" vs SCHEMATIC "when in this kind of activity"

Research drill for `the_reader_cannot_reason_over_its_own_situation_model_on_real_inference`.
Date 2026-08-31. Author: solver (finer brain-fidelity drill on a wall hit AFTER the experiment).
ONLINE-literature synthesis; calibration penalty applied (every "should" is a DESIGN HYPOTHESIS pending
our own measurement, not an inherited number).

**Scope.** The measured before/after wall on MCScript2 (n=1128): the reasoning MECHANISM carries real
signal (shuffled-timeline twin LOSES CI-separated +0.036; narrated-out-of-order/flashback items recovered
0.74 vs 0.26 surface-text-order) but end-to-end accuracy sits AT the similarity/no-model floor (~0.54;
0.564 text-answerable split; 0.577 with clean retrieval), and improving event RETRIEVAL (coverage
0.55→0.69) left accuracy FLAT. This drill asks the one question that decides the write-up: **is the wall a
KNOWLEDGE gap (missing organ) or a missing-integration/reasoning step (build target inside the reader)?**

**Builds on** `research_inference_over_situation_model_brain_mechanism_2026-08-31.md` (the online/offline
inference split; the RECALL/STEP/KNOWLEDGE three-way attribution; Graesser's 13 classes; cue-based
retrieval; GEK). Does NOT rehash it. This note goes FINER on the TEMPORAL sub-case specifically.

Prior-arc work on script-vs-episodic temporal order: NONE beyond the sibling drill (freshly-opened problem).

---

## Q1 — TWO temporal-order systems in the brain, and how they combine

The brain holds "when" TWICE, in two dissociable systems. This is the load-bearing fact for the whole wall.

**(a) EPISODIC order — "when in THIS specific story" — hippocampal–entorhinal system.**
The order of the events *as narrated in this passage* is carried by the hippocampal–entorhinal sequence
machinery: hippocampal **time cells** that fire at successive moments and tile an interval (MacDonald,
Lepage, Eichenbaum 2011; Pastalkova et al. 2008 sequence cells), a **lateral entorhinal cortex** temporal
signal / sequence-structure code (Tsao et al. 2018 *Nature*; Bright et al. LEC sequence mapping), and
newly-reported human **order-selective cells** that encode ordinal position independent of content or
absolute duration (2025 human intracranial). The hippocampus "associates events in gradually changing
temporal contexts" and *constructs* sequence memories — a content-rich, instance-specific timeline. This is
the register our reader's `timeline_register` already imitates, and it demonstrably WORKS (the +0.036 twin
loss and the flashback recovery are this system succeeding).

**(b) SCHEMATIC/CANONICAL order — "when in this KIND of activity" — mPFC / posterior-medial semantic system.**
The generic canonical order of a stereotyped activity (restaurant: seat → order → check-ID → pour → serve
→ present-check → tip) lives in a SEPARATE system: **medial/ventromedial PFC** plus **posterior medial
cortex** (precuneus, PCC, retrosplenial) and **angular gyrus**. The clean dissociation: **"mPFC confers
ordinality; the hippocampus associates events in gradually changing temporal contexts"** — mPFC carries
abstract/canonical ordinal structure, the hippocampus the specific episodic sequence (Kwok/Macaluso &
related sequence-memory fMRI; Jenkins & Ranganath). The decisive study is **Baldassano, Hasson & Norman
2018 (*J Neurosci* 38(45):9689)**: mPFC + posterior-medial cortex + superior frontal gyrus carry
event-schema patterns that **generalize across stories, subjects and modalities** (audiovisual vs spoken),
are **sensitive to overall SCRIPT STRUCTURE** — **temporally SCRAMBLED events evoke WEAKER schematic
representations** — and an HMM on these patterns decodes restaurant-vs-airport from unlabeled data. That is
the canonical ORDER itself being represented in a semantic (not episodic) store. Schema substrate:
Ghosh & Gilboa 2014 (schema = associative structure abstracted across many episodes); Gilboa & Marlatte
2017 (mPFC schema hub); Tse et al. 2007 *Science* + van Kesteren et al. 2012 (schema-congruent info
consolidates fast into mPFC/neocortex).

**How the two integrate when you answer "is the check printed before or after the order?" for a familiar
restaurant story.** Complementary-learning-systems division of labour (McClelland, McNaughton & O'Reilly
1995): the **mPFC schema supplies the DEFAULT canonical order** (retrieved by recognising the scenario),
and the **hippocampal episodic trace OVERRIDES the default only where the specific text marks a deviation**
(a flashback/pluperfect). If the passage narrated both events in a clear order you read it off the episodic
timeline; if it did NOT (the usual case — see Q5), the answer comes from the mPFC schema, i.e. from stored
world knowledge, NOT from anything the passage put in the episodic model.

---

## Q2 — THE CRUX: is canonical script ORDER instantiated ONLINE into the situation model, or retrieved OFFLINE at question time?

Decompose into the two things that are genuinely different:

**(a) The EPISODIC order of NARRATED events IS instantiated online.** PINNED. The Event-Indexing Model
(Zwaan, Langston & Graesser 1995) makes TIME one of five dimensions readers continuously monitor; the
Strong Iconicity Assumption (Zwaan 1996) is that readers update the model the instant a temporal shift
appears, and reading slows at time shifts. Default = order-of-mention = order-of-occurrence (temporal
iconicity); an explicit marker (before/after, pluperfect, flashback) triggers a reorder. **Our reader
already implements exactly this and it works** — the flashback split (0.74 vs 0.26) is this online episodic
mechanism recovering true order against surface text order. So for the narrated-order component there is no
gap.

**(b) The GENERIC CANONICAL order of UNMENTIONED / under-determined script relations is NOT laid down as an
episodic timeline — it is applied at retrieval/question time from the semantic schema.** The evidence
converges:
- **Bower, Black & Turner 1979 (*Cog Psych* 11:177).** Canonical order is imposed at **RECALL**: subjects
  RE-ORDER scrambled script sentences toward canonical order in recall, and INTRUDE unstated script actions
  to fill slots. Their script-norming showed people agree on the canonical ORDER of actions — i.e. the
  order is stored in **semantic** memory and is **RECONSTRUCTIVELY** applied, not necessarily bound into
  the episodic trace during reading.
- **Schema ACTIVATION is online, but that is a POINTER, not INSTANTIATION.** Baldassano 2018 (the schema is
  active during perception) and Metusalem et al. 2012 (generalized event knowledge activated
  automatically, event-level, online) show the relevant script is *retrieved and active while reading* —
  but the schema stays in the mPFC/semantic system as a pointer; the full canonical partial order is NOT
  copied into the hippocampal episodic timeline. Activation ≠ the ordered content being present in the
  situation model.
- **Graesser taxonomy (from the sibling drill).** The unmentioned script steps and their order are the
  **subordinate-goal/action** and **instrument** classes — the ELABORATIVE, NOT-drawn-online classes.

**VERDICT on Q2 (the crux):** For canonical event ORDER *specifically*, the relations the passage does not
explicitly narrate are **OFFLINE** — retrieved from the semantic schema at question time, not present in a
text-derived situation model. **A static text-derived situation model structurally cannot contain the
canonical order of events it never narrated.** The solver's negative is CORRECT for the >60% of
temporal questions that need script knowledge (Q5). The ONE nuance that keeps this from being "nothing to
build inside the reader": schema *retrieval* is online, so a faithful reader SHOULD recognise the scenario
and pull the relevant script at read time — that is a thin integration hook, but the thing it pulls (the
canonical orders) is CONTENT the reader does not have. So the dominant missing thing is a KNOWLEDGE STORE,
not a reasoning chain.

---

## Q3 — Is there a brain-faithful reasoning bridge episodic→script I'm missing, or is the only path a stored/learned canonical-order KB?

**The bridging reasoning mechanism EXISTS, is brain-faithful, and is CHEAP — but it is not the wall.** The
brain bridges a partial stored order to a specific before/after judgment by **transitive inference over
partial orderings**, a well-documented hippocampal/relational-memory function (Dusek & Eichenbaum 1997;
Zeithamova & Preston memory integration; Frontiers 2012 review of hippocampal generalization/inference;
rostrolateral-PFC + hippocampus, Wendelken & Bunge 2010). Directly on temporal order:
**"the hippocampus constructs sequence memories that generalize temporal relations across experiences"**
(bioRxiv 2021) and **"structural knowledge about time patterns, abstracted from different sequences, biases
the construction of specific event times"** (Nat Commun 2022, 13:3646) — literally: a learned canonical
order applied to a specific instance. If the schema stores a partial order, transitive closure yields every
pairwise before/after.

**But transitive inference / schema pattern-completion needs STORED CONTENT to operate over.** Without the
canonical partial order (the KNOWLEDGE), transitivity has nothing to close and pattern-completion has no
pattern. So the reasoning bridge is present and adequate; **the only genuinely missing thing is the stored
(and, per Q4, learnable) canonical-order KNOWLEDGE base.** A cheap transitive-closure reasoner sits on top
of it.

---

## Q4 — ACQUISITION: how canonical script order is LEARNED, and a glass-box no-LLM mechanism (the follow-on)

**Brain evidence: canonical order is learned by extracting the modal/recurring structure across MANY
instances**, driven by prediction error.
- **Reynolds, Zacks & Braver 2007 (*Cog Sci* 31:613).** A computational event-segmentation model: experience
  with recurring patterns lets the system predict within an event, spikes in **prediction error** mark
  boundaries, and the recurring **sequential structure between boundaries is extracted into stable event
  representations** — i.e. schema induction from statistics + prediction error. Event Segmentation Theory
  (Zacks, Speer, Swallow, Reynolds & colleagues 2007).
- **Schema consolidation across repetition** abstracts the invariant order (Tse et al. 2007; Ghosh & Gilboa
  2014); developmental "generalized event representations" are built from repeated experience of the same
  activity (Nelson 1986; Fivush) with the modal order surviving.
- **Hippocampal generalization** of temporal relations across sequences (bioRxiv 2021; Nat Commun 2022) is
  the same computation at the trace level.

This is EXACTLY the North-Star learner move: learn structure by reading many instances.

**Glass-box, no-LLM mechanism sketch (the concrete follow-on organ — a learned canonical-order prior /
"temporal schema" store):**
1. **Segment** each training narrative of a scenario into events (reuse the reader's existing event
   extraction / sentence-gist localization).
2. **Slot-map** each event to a canonical event-type for that scenario by clustering the reader's OWN gist
   embeddings (glass-box; no LLM). Each cluster = a schema slot (e.g. `pour_drink`, `present_check`).
3. **Observe** each narrative's within-passage pairwise order relations between the slots that co-occur
   (read straight off the reader's episodic timeline — reliable for narrated order per Q2a).
4. **Aggregate** across many narratives: for every ordered slot-pair (A,B) tally P(A before B); take the
   MODAL direction as the canonical relation and keep the vote margin as a **confidence**. Result = a
   learned canonical PARTIAL ORDER per scenario.
5. **Transitive closure** over the high-confidence edges → a full canonical before/after prior (Q3's cheap
   reasoner).
6. **At question time on a single passage:** recognise the scenario (schema retrieval), map the two queried
   events to slots, answer before/after from the learned canonical order — but let the passage's OWN
   episodic timeline OVERRIDE the canonical default wherever the text explicitly marks a non-canonical order
   (the reader's existing flashback mechanism). Report the confidence; abstain / fall back to the episodic
   read when the margin is low.

This copies the COMPUTATION (statistical schema induction + prediction-error-gated structure extraction +
transitive generalization) faithfully; the update rule (majority-vote vs an EM/prediction-error refinement)
is the sweepable OUR-INVENTION parameter. It answers before/after when the single passage under-determines
the order — precisely the wall.

---

## Q5 — Validate/refute "MCScript2 before/after is script-order-dominated" — CONFIRMED with the dataset's own numbers

MCScript2.0 (Ostermann, Roth & Pinkal 2019, *SEM 2019* / arXiv:1905.09531; MCScript 1.0 Ostermann et al.
2018, arXiv:1803.05223):
- **Question mix (validated set):** 50% **script-based** (9,935), 40% **text-based** (7,908), 8%
  text-or-script (1,978) — a deliberate jump from ~27% script-based in MCScript 1.0.
- **Collection forced offline knowledge:** target sentences were selected then **HIDDEN** during answer
  collection, so the answer "would have to be inferred from common sense," not retrieved from the text.
- **TEMPORAL specifically (the decisive number):** **"WHEN" questions are the second-largest type and
  require script knowledge in MORE THAN 60% of cases**, and **"events are usually referred to only once in
  a text."** So the single passage structurally under-determines before/after for most temporal items — you
  cannot re-derive order from a passage that mentions each event once.
- **Humans 97.4% vs best model 72% (67% on script-based).** Humans answer trivially because their mPFC
  schema supplies the canonical order for free.

This is a direct, quantitative confirmation of the solver's interpretation: **most MCScript2 before/after
answers are dominated by commonsense script-order that (i) is not recoverable from the single passage's
narrated events and (ii) a text-derived situation model structurally cannot contain.** Graesser class: the
narrated-order component is the ONLINE bridging class (which the reader already handles — the flashback
win); the under-determined canonical-order component is the ELABORATIVE/subordinate-goal OFFLINE class.

This also explains every measured null cleanly: retrieval-coverage 0.55→0.69 leaving accuracy FLAT (the
missing thing was never in the text to retrieve); text-answerable split still at the 0.564 similarity floor
(even "text" items lean on canonical order + a similarity floor already captures the surface-order cases);
0.577 ceiling with clean retrieval (retrieval is not the binding constraint).

---

## PINNED vs OUR-INVENTION-UNDER-TEST (temporal sub-case)

**PINNED (brain-constrained; replicate the operation):**
- TWO temporal-order systems: episodic instance timeline = hippocampal–entorhinal (time cells / LEC /
  order-selective cells); canonical/ordinal schematic order = mPFC + posterior-medial cortex (Baldassano
  2018; "mPFC confers ordinality"). Integrated by CLS: schema default + episodic override.
- Narrated-event order is instantiated ONLINE (Event-Indexing / Strong Iconicity); canonical order of
  unmentioned relations is retrieved/reconstructed OFFLINE from the semantic schema (Bower Black & Turner
  1979; schema activation ≠ instantiation).
- The bridge from a stored partial order to a specific before/after = transitive inference over partial
  orderings (hippocampal relational memory; "structural knowledge abstracted across sequences biases
  specific event-time construction," Nat Commun 2022).
- Canonical order is LEARNED by prediction-error-gated statistical schema induction across many instances
  (Reynolds, Zacks & Braver 2007; Event Segmentation Theory).

**OUR-INVENTION-UNDER-TEST (sweep; keep glass-box, NO external LLM):**
- The slot-mapping (gist clustering granularity), the confidence/vote-margin threshold, the
  update rule (majority-vote vs EM/prediction-error), the transitive-closure conflict-resolution, and the
  schema-default-vs-episodic-override arbitration policy. All sweepable; none is the wall.

---

## VERDICT — KNOWLEDGE gap (missing organ), not a reasoning-step or retrieval failure

**This wall is a KNOWLEDGE gap: a missing organ — a stored/learned canonical script-order prior (a
glass-box "temporal schema" / GEK store) — NOT a missing reasoning step or retrieval failure inside the
reader.** Four independent lines converge:
1. **The reasoning step is intact** — the shuffled-timeline twin loses CI-separated and the flashback split
   is recovered (0.74 vs 0.26). The order-reasoning mechanism carries real signal where the content exists.
2. **Retrieval is not the binding wall** — coverage 0.55→0.69 left accuracy flat; clean retrieval caps at
   0.577.
3. **The content is structurally absent** — >60% of temporal questions need script knowledge and events are
   mentioned once, so the canonical order is not in a text-derived model by construction.
4. **The brain supplies it from a SEPARATE system** — mPFC/posterior-medial semantic schema, retrieved at
   question time, not the episodic hippocampal timeline the reader models.

**One honest qualifier (do not overstate):** it is not a PURE knowledge gap with zero build inside the
reader. There is a THIN integration hook — recognise the scenario at read time (schema retrieval is online)
and route the retrieved canonical order into the answer read-out, with the episodic timeline overriding the
canonical default where the text marks a deviation. But that hook is trivial once the store exists; the
DOMINANT missing thing is the KNOWLEDGE (the canonical orders), which is a NEW ORGAN, and it is LEARNABLE by
reading many instances (Q4) — which makes it a first-class North-Star learner target, not a dead end.

This refines the sibling drill's prediction (commonsense split = KNOWLEDGE gap, points at a glass-box GEK
store) into a concrete, temporal-specific, buildable organ: a learned canonical-order prior + a
transitive-closure reasoner + a schema-vs-episodic override.

---

## Proposed AUDIT UPDATE for `notes/BRAIN_FOUNDATIONAL_AUDIT.md §2b` (NOT applied here — surfaced for strategy to land)
> **Temporal order is held by TWO dissociable brain systems, and our reader models only one.** Episodic
> "when in this story" = hippocampal–entorhinal (time cells / LEC / order-selective cells) — this is what
> `timeline_register` imitates, and it works. Canonical "when in this kind of activity" = mPFC +
> posterior-medial cortex semantic schema ("mPFC confers ordinality"; Baldassano 2018) — **UNBUILT**. The
> before/after wall on MCScript2 is a KNOWLEDGE gap = the missing mPFC-schema canonical-order store, not a
> reasoning/retrieval failure. Follow-on: a glass-box learned canonical-order prior (statistical schema
> induction across narratives; Reynolds/Zacks/Braver 2007) + transitive-closure reasoner + schema-default /
> episodic-override arbitration.

---

## Key citations
- MacDonald C.J., Lepage K.Q., Eden U.T. & Eichenbaum H. (2011). Hippocampal "time cells" bridge the gap in memory for discontiguous events. *Neuron* 71:737-749.
- Tsao A., Sugar J., Lu L., Wang C., Knierim J.J., Moser M-B. & Moser E.I. (2018). Integrating time from experience in the lateral entorhinal cortex. *Nature* 561:57-62.
- Zwaan R.A., Langston M.C. & Graesser A.C. (1995). The construction of situation models in narrative comprehension: an event-indexing model. *Psychological Science* 6:292-297.
- Zwaan R.A. (1996). Processing narrative time shifts. *JEP:LMC* 22:1196-1207. (Strong Iconicity.)
- Bower G.H., Black J.B. & Turner T.J. (1979). Scripts in memory for text. *Cognitive Psychology* 11:177-220. (Reordering-to-canonical + gap-filling at recall.)
- Baldassano C., Hasson U. & Norman K.A. (2018). Representation of real-world event schemas during narrative perception. *Journal of Neuroscience* 38(45):9689-9699. (mPFC/PMC canonical schema, generalizes across story/modality, scrambling weakens it.)
- Ghosh V.E. & Gilboa A. (2014). What is a memory schema? A historical perspective on current neuroscience literature. *Neuropsychologia* 53:104-114.
- Gilboa A. & Marlatte H. (2017). Neurobiology of schemas and schema-mediated memory. *Trends in Cognitive Sciences* 21:618-631.
- Tse D. et al. (2007). Schemas and memory consolidation. *Science* 316:76-82. van Kesteren M.T.R. et al. (2012). How schema and novelty augment memory formation. *TICS* 16:211-218.
- Reynolds J.R., Zacks J.M. & Braver T.S. (2007). A computational model of event segmentation from perceptual prediction. *Cognitive Science* 31:613-643. (Prediction-error schema learning.)
- Dusek J.A. & Eichenbaum H. (1997). The hippocampus and memory for orderly stimulus relations. *PNAS* 94:7109-7114. (Transitive inference.) + Nat Commun 13:3646 (2022): structural time-knowledge abstracted across sequences biases specific event-time construction.
- Ostermann S., Roth M. & Pinkal M. (2019). MCScript2.0. *SEM 2019* / arXiv:1905.09531. (50% script-based; WHEN questions >60% need script knowledge; events mentioned once; humans 97.4% vs model 72%.)
- McClelland J.L., McNaughton B.L. & O'Reilly R.C. (1995). Why there are complementary learning systems. *Psychological Review* 102:419-457. (CLS: schema default + episodic specifics.)

---

## TLDR (plain English)
The brain stores "when" twice: a memory of the exact order things happened in THIS story (a hippocampal
"tape"), and separate general knowledge of the usual order of steps in THIS KIND of activity — e.g. in a
restaurant you order before the bill is printed (a front-of-brain "script"). Our reader builds the first
tape faithfully and it works: when a story is told out of order it correctly untangles it. But most
before/after questions in this test are answered from the SECOND kind of knowledge — the usual order of a
familiar activity — which the test deliberately never states in the passage (each event is mentioned once,
and more than 60% of "when" questions need this outside knowledge; people score 97% because they just know
it). Our reader has no store of "usual order of things," so it cannot answer these, and no amount of better
reading or better reasoning fixes that — there is nothing in the passage to reason over. So the wall is a
MISSING PIECE OF KNOWLEDGE, not a broken reasoning or reading step. The good news: this knowledge is exactly
the kind you can LEARN by reading many stories about the same activity and noticing the usual order — which
is the whole point of our learn-by-reading direction.

## QUESTIONS
None for the owner. One open DESIGN choice (solver's call, not a question): build the learned canonical-order
store as the immediate follow-on, or first ship the honest KNOWLEDGE-gap negative on this problem and open
the store as its own problem. Recommendation: ship the negative here (it is a rigorous PASS — the brain's
actual mechanism, faithfully built, hit a content wall the text cannot supply), and open the learned
canonical-order prior as the follow-on build, because it is a self-contained new organ AND a North-Star
learner target.

## NEXT STEPS
1. Write up THIS wall as a rigorous negative = KNOWLEDGE gap: the reader models the episodic timeline
   (hippocampal) but not the canonical/schematic order (mPFC), and MCScript2 before/after is dominated by
   the latter (dataset's own numbers: WHEN questions >60% script-knowledge, events mentioned once).
2. Attribute the residual per the sibling drill's table: confirm the text-answerable temporal items are
   RECALL/STEP-clean (the flashback recovery says the STEP is fine) and the misses concentrate on the
   script-knowledge items (KNOWLEDGE).
3. Open the follow-on organ: a glass-box learned canonical-order prior (Q4 sketch) — statistical schema
   induction across many scenario narratives + transitive closure + schema-default/episodic-override — and
   test it can answer before/after when the single passage under-determines the order, info-free (scrambled
   canonical prior) twin LOSING.
4. Land the proposed AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md §2b` (two temporal-order systems; we
   model only the episodic one).
