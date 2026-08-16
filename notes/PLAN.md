# PLAN — the long-horizon plan for the substrate

**LIVING DOCUMENT. Dateless filename on purpose. Edit in place.**
Last substantive rewrite: 2026-08-15 late, at commit `cd8d15cd2`, branch `dataprep/mcguffey-graded-corpus`.
**Dated corrections since, appended not overwritten (every superseded claim is preserved verbatim
with a superseded-by line):** 2026-08-16 — the **CA3 self-contradiction** is resolved in favour of
**building the completer** (section 5 table row + the dated correction under that table), and
**R14 / R15** are added to section 10 with a dated re-earning note on **R12**.

This replaces `notes/PLAN_NEXT_12H.md`, which is now a one-line pointer to here so the recovery
chain does not break. It is written for a session with **no memory of the night that produced it**,
and for an unattended loop that re-reads it on every iteration.

Read order: `notes/STATUS.md` (injected every session by the hook) → **this file** →
`notes/ORGAN_MAP.md` (the per-organ detail) → `notes/RECOVERY_PROGRAM.md` (the triage backlog) →
`notes/STATUS_LESSONS.md` (the never-trim lessons).

---

## 0. HOW TO USE THIS FILE (read this part every iteration)

Each pass, do this and nothing else:

1. **Check what is running.** `python tools/inflight_monitor.py`, and read the
   "WHAT IS RUNNING / BLOCKED" section of `notes/STATUS.md`. Never start work that collides with
   something already in flight.
2. **Pick the LOWEST-NUMBERED item in section 7 that is not DONE and not BLOCKED.** The backlog is
   already sequenced. Do not re-derive the order; do not skip ahead to something that looks easier.
   If the lowest open item is blocked, say so in one line and take the next one.
3. **Before building anything, do the two premise checks in section 10** (rules R11 and R12). They
   are new tonight and they exist because both failed this week.
4. **When an item finishes, edit this file**: mark the item DONE with its commit and its measured
   numbers, or mark it STOPPED with the stop-rule that fired. A backlog item with no recorded
   outcome will be run twice.
5. **Stop the whole loop** if any of these is true — do not continue and do not improvise around it:
   - the instrument for the component you are working on fails its own null or known-answer gates
     (report `INSTRUMENT_STILL_LOOSE`, publish no quality number);
   - a decision in section 9 is required and its recommended default does not apply;
   - you would need to change a pre-registered threshold, a floor definition, or an arm key.

**The one thing that is never allowed**: making a number look better by giving the system a
shortcut that carries no understanding. Spelling is the live example. A spelling channel already
cleared our old ">=10%" gate, which is why that gate was retired. Wiring spelling in would "fix"
the headline and destroy the project. A floor is cleared by understanding, never adopted.

---

## 1. WHAT WE ARE BUILDING, IN PLAIN LANGUAGE

A machine that **reads text and ends up actually knowing what it read**, where every step is
inspectable — no large language model doing the thinking at question time.

We are copying the brain, on purpose, because the brain is the one existing system that does this.
The working method is: for each part, ask *how does the brain do this?* first — before surveying
what tools we happen to have — then build that part as exactly as we can, then measure that part
**on its own** against something that could have beaten it.

Inventing is allowed where the neuroscience does not pin the answer. What is not allowed is
reaching for a convenient available tool *instead of* asking how the brain does it, and what is
absolutely not allowed is presenting an invention as if the brain literature pinned it. Every
design choice in section 5 is tagged **PINNED-BY-EVIDENCE** or **OUR-INVENTION-BEING-TESTED**.

---

## 2. WHERE WE ACTUALLY ARE — MEASURED, NOT REMEMBERED

Every number below was computed off disk. Re-check before quoting; several were wrong at least
once this week.

**The end-to-end read-out loses to a spell-checker.** Asked to name the right word from an
open vocabulary, we get **4.80%** right (CI 4.13–5.48). A channel with **zero** substrate signal —
just three-letter chunks of the spelling — gets **8.70%** (7.83–9.60) on the identical items,
pool and gold. Prefix-only gets 5.88%. The intervals do not overlap.
(`exp_orthographic_floor_vet_v1`, `58a125c88`.)

**We now know which part fails.** Finding the right neighbourhood is fine: the right answer is in
our top 50 **55.65%** of the time versus spelling's **54.55%** — not separable, we are level.
Picking the winner out of that neighbourhood is where we lose: **8.63%** versus spelling's
**15.95%**, and those intervals are separated.

**Tonight's five results, which change what the plan should be:**

1. **Component #1 (word/concept encoding) is no longer unmeasured.** An isolated encoding-quality
   instrument exists and passes its own validity gates: v1 17/17 (`4f6b54852`), v2 21/21
   (`542e1fc0d`). It measures two separate axes — *identity* (is this still the right word?) and
   *structure* (does the geometry carry anything beyond identity?) — each with its own null arm and
   its own known-answer arm, because a random code is near-optimal on identity and at chance on
   structure, so any single blended "quality score" is unfalsifiable.
   Cell: `experiments/exp_encoding_quality_instrument_v2.py`.
   Metrics: `data/exp_encoding_quality_instrument_v2/metrics.json`.

2. **Our live word encoder is a hash of the spelling, and it is the structure-axis null by
   construction.** Six inlined lines inside `hdlab/grounding_acquisition_loop.py::context_vector`:
   sha256 of the word seeds a random ±1 vector at d=256. No training, no corpus, no relation to any
   other word. Measured: spelling-gold lift 0.99, SimLex correlation −0.0019 at d=256. It is not
   *near* the null, it *is* the null. A hash destroys relationships by design, so it is not merely
   meaning-blind — it is spelling-blind too (`cos(water, waters)` and `cos(water, river)` are
   statistically identical). **There is no registry row for it at all.**

3. **"There is nothing there" was a SCOPE OVER-CLOSURE, and this is the biggest correction of the
   night.** Off the live path we have built and never wired:
   - a **learned encoder** trained on **121,082,196 tokens** (from a **237,666,633-token** ARC
     corpus — both counted off disk; the circulating "237.7M-token encoder" attached the corpus
     number to the encoder);
   - **36,810 grounding norms** × 12 dimensions (the circulating "39,707" is the *filename* of the
     Lancaster source CSV, not the usable joined asset), covering **69.0%** of the C3 anchor set;
   - a hand-authored concept lexicon of **359** concepts.
   **All 12 encoder-named modules are absent from the live 40-module import closure**, confirmed by
   running the code and diffing `sys.modules`, not by grep. The plug point exists and is switched
   off: `reading_grounding_loop.process_sentence(encoder=None)` by default.
   **Preliminary on the learned encoder: SimLex 0.189 (CI 0.077–0.295) against a hardened frequency
   floor of 0.080 — a margin of +0.109 whose CI is [−0.026, +0.241] and therefore CROSSES ZERO.**
   Verdict on disk: `NO_ASSET_CLEARS_THE_HARDENED_FLOOR`. Power runs are in flight. This is
   "not established", not "refuted": the point estimate is the largest of the set and the scrambled
   control is negative, which is the right sign, but 322 SimLex pairs cannot separate it.
   The hand lexicon is `NOT_SCORABLE` on this gold (16 usable pairs against a pre-declared floor of
   100) — a coverage fact about the asset, not a failure of it.

4. **SUM versus SIGN is adjudicated** (`cd8d15cd2`, `notes/ORGAN_MAP.md` §9). Two claims that
   looked contradictory both survive, on different axes, and neither may be quoted as an ordering:
   - The **sum** is the dominant loss **only** when you add together **4 or more mutually distinct,
     correlated concept codes** — a flat-store superposition **the live path never performs** (every
     `sum`/`+=`/`bundle` site in both live entry modules was enumerated; none superposes distinct
     concept anchors).
   - The **sign** is the dominant loss **at every site production actually runs**. On the production
     sentence encoder — add 8 word codes, then take the sign — the sum costs 0.074 bits and the sign
     costs 0.218 bits. **The sign costs 3x what the sum costs there.**
   - So ORGAN_MAP's "the defect is one line, not the design" is **superseded in part**: the one line
     is real and worth **+0.0602** on a two-choice test, but ~0 on the open-vocabulary test, and it
     does nothing about the capacity cliff. Our concept codes have a **superposition capacity below
     4** (collision-free: 93.5% of ceiling retained at bundle size 2, 17.3% at 4, 1.4% at 8), while
     our random word codes survive to 8 (98.7%) and beyond.
   - Ordering, at d=256 on the two-choice test, stated so it cannot be misapplied:
     **capacity (+0.0985 for 16x the dimensions) > sign (+0.0585) > divisive normalisation
     (+0.00175, CI includes zero).**
   - **The +0.0602 is a TWO-CHOICE number (chance 0.50, 2-candidate pool, n=4000).** It may not be
     carried to the open-vocabulary scorer, where the same switch measures +0.0015, CI
     [−0.0055, +0.00825], null.

5. **The shipped store applies NO KEY AT ALL.** Verified by runtime reconstruction: what actually
   accumulates is `acc += symbol_vector(w)`. A role-binding store exists and unbinds cleanly, and
   **nothing calls it** (`reading_grounding_loop.py:436` is the role-bound path and it is
   default-OFF). This is **not a degraded address — it is an absent one**, and the difference
   matters for what we build next.
   **This falsifies a premise a draft spec was already resting on.** `preregs/DRAFT_storage_quality_instrument_v1.md`
   ("key finding 2") assumed contributions were `bind(REL:k, filler)` and therefore that a latent
   address existed and was merely degraded by crosstalk. It does not exist. **That draft must be
   revised before it is built** — see backlog item 3.

6. **A checkpoint-key collision silently no-op'd ~128 full runs** (not 273 — the two circulating
   figures are marginals of different sets whose intersection is 133, of which 5 already have a
   verified full). A full run found the smoke run's checkpoint under the same key and exited having
   computed nothing, or worse, mixed one smoke seed into an otherwise-real full. **Fixed at
   `ee7c42c0f`** in `experiments/_seed_checkpoint.py` (keys now carry a hash of the resolved config;
   mismatch raises). **`tools/exp_checkpoint.py` has the same defect and is UNFIXED** — see backlog
   item 2.

**Two framings that are dead and must not be revived:** "6x its floor", and "5.2pp short of >=10%".
Both come from the retired absolute-number gate.

**What is NOT invalidated:** the growth machinery (no-leak 0, scramble 0.077, round-trip
bit-identical, `ac430868d`). That is a different claim — that grounding tracks real reading context
rather than shuffled context — and a spelling channel cannot touch it.

---

## 3. THE COMPONENT TABLE — what each part is FOR, and whether it does it

The owner's instruction is the shape of this section: *"we need to know what the entire component
is supposed to do, then evaluate each component to see if it's doing what it's supposed to, how
well, and improve it... critical to look at each at a time before testing all together."*

**A component with no isolated instrument is the HIGHEST priority, not the lowest.** You cannot
improve what you cannot measure alone. That is why component #1 got an instrument before anything
was changed, and it is why component #2 gets one next.

| # | component | what it is SUPPOSED to do | can we measure it ALONE? | how well is it doing it |
|---|---|---|---|---|
| 1 | **word / concept encoding** | turn a word into a code that (a) is still identifiably that word and (b) carries its relationships to other words | **YES** — `exp_encoding_quality_instrument_v2`, 21/21 gates | **identity: fine. structure: the live word code is the NULL.** The concept profile has a real spelling/morphology signal (5.75x over null, collision-free) and a semantic signal that is not separated from zero (SimLex 0.1048, CI [−0.006, 0.216]) |
| 2 | **storage** | hold many items so that each can be asked for individually and come back unchanged | **NO — BUILD NEXT.** Draft spec exists; its premise is falsified and must be revised | **unmeasured in isolation.** Known from code: no key is applied at write time |
| 3 | **reading / extraction** | turn a sentence into the facts it states | partial | ~0.22–0.25 precision against independent gold |
| 4 | **retrieval** | given a cue, surface a shortlist containing the right answer | yes | **FINE** — top-50 55.65% vs spelling 54.55%, not separable |
| 5 | **selection** | pick the right one out of the shortlist | yes | **FAILS** — 8.63% vs spelling 15.95%, separated |
| 6 | **foundation (end to end)** | the assembled thing | yes, since `d62acfe58` | **~49% correct** (precision 0.4867, CI 0.408–0.566, vs a frequency floor of 0.22). Not the 95–97% three earlier harness versions claimed |

**Closed this week — do not re-run without a genuinely new mechanism:** graded storage (null);
per-row gain (null, and algebraically so — cosine does not care about positive rescaling);
score-space gain (null); coherence reranking (null, the third floored negative in that family);
capacity across an 8x sweep (flat); the K-sweep (VOID — its own known-answer arm failed all five
seeds at 0.55–0.57 against a 0.70 floor, so its apparent decay is not established).

---

## 4. THE INTEGRATION TABLE — how the parts have to fit together

The owner's second instruction: components **compound**. Measuring each alone is necessary and not
sufficient — you also have to know what each side of a join *assumes* the other provides, because a
defect on one side shows up as a symptom on the other, and you will fix the wrong thing.

**Tonight makes this concrete and it is the clearest example we have.** An encoder that carries no
meaning, and a store that applies no key, are **two independent defects**. Both present downstream
as the *same* symptom: **"selection fails."** If you had only the downstream symptom you would
spend weeks improving the selector, which is measurably not the broken part.

| join | what crosses the boundary | what the LEFT side assumes about the right | what the RIGHT side assumes about the left | how a defect on ONE side shows up on the OTHER |
|---|---|---|---|---|
| **1 → 2** encoding → storage | one vector per word occurrence | that the store will keep this item separable from the others it holds | that codes handed to it are near-orthogonal, so adding them is lossless | **This assumption is currently VIOLATED and measured.** Random word codes survive being added 8-deep (98.7% retained). Structured concept codes do not survive 4-deep (17.3%). So the moment encoding starts carrying meaning, the store starts destroying it — *improving component 1 will make component 2 look worse*, and that is expected, not a regression |
| **2 → 4** storage → retrieval | a set of candidate items for a cue | that the store can be asked for a specific thing | that stored items are addressable, i.e. that asking for A returns A rather than a blend | With **no key at all**, "ask for a facet" is not a degraded operation, it is an unavailable one. Retrieval compensates by scoring everything, which is why retrieval looks *fine* while selection looks broken. **Retrieval's health is partly a symptom of storage's absence of structure, not evidence against it** |
| **4 → 5** retrieval → selection | a shortlist (~50) | that selection can rank within a neighbourhood | that the shortlist actually contains the answer | It does — 55.65% of the time. So selection's failure is **not** a retrieval failure. But a shortlist built from a meaning-free code is a shortlist of *spelling-similar and frequency-similar* words, and no ranker can recover meaning that never entered |
| **3 → 2** extraction → storage | facts (subject, relation, object) | that what is stored is what was extracted | that what arrives is correct | Extraction runs at ~0.22–0.25 precision, so ~3 of 4 stored facts are wrong. **A storage instrument must therefore score "did what went in come back out", NOT "is it true"** — otherwise it measures extraction and reports it as storage |
| **1 → 5** encoding → selection (the long-range one) | the geometry the ranker sorts by | — | that near-neighbours in the code are near-neighbours in meaning | **This is the failure we actually have.** Selection is being asked to sort by meaning using a code with no meaning in it. Every re-weighting intervention on that geometry has measured null (log-IDF null, global z-scoring +0.0018, pool-inverse −0.011, contrast gain −0.0220) — because re-weighting cannot create information the code never had |
| **2 → 6** storage → end-to-end | everything | — | — | The end-to-end 49% and the read-out 4.80% are **joint** numbers. Neither can be attributed to a component. **Stop quoting the headline number as a diagnosis** — the owner has said this directly: *"quoting against the lead number (~4%) isn't that helpful — where is it failing?"* |

**Rule that falls out of this table, and it governs the build order:** fix the components in the
order that makes the *next* component's measurement meaningful. Fixing encoding before storage will
make the store visibly worse, so **the storage instrument must exist before the encoder is
changed** — otherwise the store's degradation will be read as an encoder regression.

---

## 5. BRAIN-FIDELITY LEDGER — which brain part, and are we honest about it

For every component and every planned step: name the **brain structure** (a neural system, not a
cognitive-theory label), say whether we **reuse an organ we already own**, and tag the choice.

- **PINNED-BY-EVIDENCE** — the literature specifies the operation and we are copying it.
- **OUR-INVENTION-BEING-TESTED** — the literature does not pin it; we are proposing the
  highest-probability brain-motivated candidate and testing it. **This is allowed.** Passing it off
  as pinned is not.

**Four anchors that shape every row below:**

- **Word FORM and word MEANING are separate brain systems.** The visual word form area produces a
  *form* code; meaning lives in temporal cortex. **A spelling-derived code is a FORM code, and we
  have been calling it a meaning code.** That single confusion explains why a spell-checker beats
  us and why our concept profile's headline "structure" turned out to be 78% lemma collision.
- **Meaning is distributed across modality spokes, bound by an anterior-temporal hub, with each
  piece keeping its own address.** Evidence for separateness is a double dissociation: hub damage
  degrades meaning across all modalities at once; focal spoke damage produces
  modality-or-category-specific loss with the rest intact. A single blended store predicts only the
  first pattern.
- **SPARSE, not dense. CONJUNCTIONS, not features. RARE features outweigh common ones.**
- **We store a dense sum.** Summing is precisely the operation that destroys addresses.

| component / step | brain structure | reuse an organ we own? | choice tag |
|---|---|---|---|
| 1. word form | visual word form area — position-tolerant letter-feature detectors, open-bigram coding | `hdlab/char_trigram_encoder.py`, `hdlab/vwfa.py`, `hdlab/char_positional_encoder.py` — all built, none on the live path | n-gram coding **PINNED-BY-EVIDENCE**; the 1-bit terminal quantiser **is not the brain's and is ours** |
| 1. word meaning | anterior temporal hub + modality spokes | learned encoder (unwired), grounding norms (unwired), hand lexicon (unwired) | that meaning is hub+spokes: **PINNED-BY-EVIDENCE**. That a trained transformer is an acceptable stand-in for a spoke: **OUR-INVENTION-BEING-TESTED**, and see decision D3 |
| 1. combining one encounter | cortical pooling — graded rate code, then divisive normalisation with a pool-shared denominator | live path does `sign()` of a sum, d=256 | graded pooling **PINNED-BY-EVIDENCE**. **Divisive normalisation is measured NULL for us (+0.00175, CI includes zero) and the reason is mathematical: cosine is invariant to a scalar denominator.** Do not re-propose it |
| 1. combining many encounters | slow replay-driven cortical consolidation into graded weights; a feature's fate is distinctiveness × correlational strength | `ConceptSpace.observe` builds a genuine graded accumulator, then throws it away with `sign()` one line before use | the graded accumulator **PINNED-BY-EVIDENCE**. **The distinctiveness WEIGHT FUNCTION is UNPINNED** — our one instantiation (log-IDF) was refuted by recompute in both of its mechanistic claims |
| 2. storage / addressing | hippocampal index — a sparse *pointer* into distributed cortical activity, not the content itself; dentate gyrus separates similar patterns before storage | `hdlab/dg_pattern_separation.py` (zero importers), `hdlab/hippocampal_encoder.py` (not wired), `hdlab/hd_fact_store.py` (per-fact, not superposed) | "each piece keeps its own address" **PINNED-BY-EVIDENCE**. **Implementing "ask for one facet" as unbind-by-role-key is OUR-INVENTION-BEING-TESTED** — we are not claiming the brain does circular convolution |
| 2. avoiding interference | complementary learning systems; sparse conjunctive coding in perirhinal cortex | `exp_interference_avoidance_conjunctive_vs_additive_v1` (conjunctive 1.000 vs additive 0.273 — the additive arm *is* our geometry) | that overlapping representations interfere more in an additive store: **PINNED-BY-EVIDENCE**. **The perirhinal feature-ambiguity attribution is CONTESTED** (real failed replications) and the conjunction operator is UNPINNED — ours to choose, and we must say so |
| 4. retrieval | cue-driven cortical reinstatement | live | **OUR-INVENTION-BEING-TESTED** (cosine over a stacked matrix). "There is no cosine anywhere in the brain" — the honest brain analogue is a recurrent settling trajectory, whose metric is UNPINNED |
| 5. selection | basal-ganglia Go/NoGo disinhibition; graded competition implemented *by* the normalisation pool, not by a hard argmax | live path uses `argmax` | **For a two-choice accuracy metric, argmax is the deterministic limit of a softmax and cannot change the expected score.** Low priority *by the brain's own metric*. **PINNED-BY-EVIDENCE that this is not our bottleneck** |
| — settling / pattern completion | **CA3 recurrent collaterals — the COMPLETER.** The brain never retrieves with an exact key; it completes a stored pattern from a PARTIAL CUE. Separation (dentate gyrus) and completion (CA3) are a **MATCHED PAIR** | `cleanup_family`, `iterative_attractor` (both live, both terminate in `sign()`); `hdlab/dg_pattern_separation.py` (the separating half, **zero importers**) | **IN SCOPE AND BEING BUILT (2026-08-16, owner direction).** We built separators with no completer, which is why conjunction failed. Read the dated correction directly under this table before acting on this row. **SUPERSEDED 2026-08-16 — the prior recommendation, preserved verbatim so the reversal is auditable:** *"EXPLICIT NEGATIVE RECOMMENDATION — do NOT build. Distinctive features are weakly correlated with a concept's other features, and attractor settling is driven by correlational structure, so completion makes near-neighbour discrimination worse. Three cells already floor it: lift +0.005, +0.003, and one HARD_FAIL at −0.020."* superseded-by: the 2026-08-16 correction note below this table, and R13 in section 10 |
| — foraging (what to read next) | UNPINNED as an equation; functionally, the system that notices what it does not know | `gap_driven_reader.rank_material()` already HARD_PASS; the "shelf" of corpora does not exist | function parity only, **OUR-INVENTION-BEING-TESTED**, and the writeup must say so |

### DATED CORRECTION 2026-08-16 — THE CA3 CONTRADICTION IS RESOLVED IN FAVOUR OF BUILDING IT

**The defect being fixed.** This file contradicted itself in a way that would have mis-routed
dispatch. The settling / pattern-completion row of the table above said **do NOT build CA3**.
Rule **R13** in section 10 says conjunction **is not testable until CA3 completion sits in front of
it**. Both cannot guide the same decision, and an agent taking the lowest-numbered open item would
have hit one or the other depending on which it read first. Flagged by the cell author who ran the
hub-and-spoke full cell (`.claude/scan-out/wall1-hubspoke-full.json`,
`A_LIVE_TENSION_IN_OUR_OWN_DOCUMENTS_recorded_not_resolved`), who correctly declined to adjudicate
it and escalated instead.

**The resolution, and it is the owner's, not an agent's.** *CA3 completion is IN SCOPE and is being
built.* The reasoning is brain-fidelity, not performance: **the brain never retrieves with an exact
key — it completes from a partial cue**, and **dentate-gyrus separation and CA3 completion are a
matched pair**. We built the separating half and never built the completing half, and that is why
conjunction failed. A conjunctive code measured with no completer in front of it is being asked to
do its partner organ's job.

**The prior negative is NOT demoted — it is re-scoped, and it stands as measured.** All three cells
were re-checked on disk today before this correction was written (right file / right version at
HEAD / `.venv` / right metric / right arm):

- `data/exp_att1_iterative_attractor_cleanup_v1/metrics.json` — `run_mode=full`, `MIDDLE_BAND`,
  best lift over argmax **+0.005**, basin ratio 1.00x, cv 0.935.
- `data/exp_cleanup_graded_attractor_vs_argmax_v1/metrics.json` — `STEP_IS_CODEBOOK_SNR_WALL_NOT_CLEANUP_RULE`,
  modern_hopfield **0.360** vs argmax **0.357** at the cliff, max|gap| 0.008.
- `data/exp_att1_iterative_attractor_v2_low_storage_ratio_krotov_v1/metrics.json` — `run_mode=full`,
  **HARD_FAIL**, lift **−0.020**.

What those three measured is **settling as a re-ranker bolted onto an argmax read-out**, scored by
lift-over-argmax and basin ratio. What R13 asks for is **completion standing between a partial cue
and a conjunctive or addressed code**. Those are different questions, and generalising the first
into "CA3 is closed" is the narrow-failure-to-impossible fault (`notes/STATUS_LESSONS.md`, and the
owner's standing directive of 2026-08-11). Two further facts make the re-scoping concrete rather
than convenient: `notes/ORGAN_MAP.md` §D2 records that **every one of our completion
implementations terminates in `sign()`**, and tonight measured that **the terminal sign is free at
an exact key and expensive under a partial cue** (new rule R14 below) — so the three cells may have
been scoring a crippled completer at the one operating point where its defect is invisible.

**What the new evidence adds, stated without overselling it.** `data/exp_hub_spoke_partial_cue_curve_v1/metrics.json`
(`run_mode=full`, verdict `ADDRESSING_HOLDS_UNDER_PARTIAL_CUE`, instrument validity 8/8, recomputed
off disk for this correction) measures how far each operator degrades **before** a completer would
have to do any work. At 50% cue overlap, item identification: **CONJUNCTIVE 0.4850** against
**FLAT 0.9564** and **ADDRESSED 0.9668**; the paired conjunctive-vs-flat delta at 20% overlap is
**−0.0247, CI [−0.0371, −0.0127]**, CI-separated below, while addressing's is **−0.0007,
CI [−0.0160, +0.0147]**, a tie. So the conjunctive operator's damage starts well before the cue is
badly degraded — which is the measurement the R13 argument needed, and it is what makes the missing
completer a *build target* rather than an assertion. **This licenses no meaning claim**: that cell
is a construction proof on synthetic and norm-derived codes, its own headline gate `G1` FAILED, and
nothing in it touches the 4.80% read-out.

**Sequencing is the Director's call, not this correction's.** No backlog item was created or
renumbered here (this note was written by the audit role, which does not author or dispatch cells).
The storage instrument, ITEM 1, still blocks the architecture items, and a completer has to be
measured on an instrument before it can be believed.

**A note we keep getting wrong, so it is written here.** `hdlab/working_memory.py` contains no
working memory — 116 lines of guard functions and constants. Auditing by filename will mislead you.
The real mechanisms are `slot_attention_wm.py` and `situation_model_accumulate.py`.

---

## 6. WHERE WORK RUNS — the runners, and which one each job goes to

The owner has reminded us a **remote GPU machine exists**. Heavy sweeps must not sit on the local
CPU. Enumerated from `tools/remote_launchers/*.bat`, `tools/remote_sync.sh` and
`tools/runner_status.py`.

| runner id | machine | queue directory | hardware | what belongs here |
|---|---|---|---|---|
| `cpu_runner_local` | **this** box, `D:/AI/hd-instrument` | `data/local_cpu_queue` | local CPU | smokes, self-tests, instrument validity passes, anything under ~5 minutes. `exp_dev` may run this queue directly |
| `cpu_runner_0` | **remote**, `marsh@home`, `C:\dev\hd-instrument` | `data/remote_cpu_queue` | 10 of 12 logical cores (affinity `3FF`), below-normal priority, idle-exit 240 min | long numpy/BLAS sweeps, multi-seed CPU cells, the 128 re-runs. **This is where "it's only CPU but it takes hours" goes — not the local box** |
| `gpu_runner_0` | **remote**, same `marsh@home` box | `data/overnight_queue` | RTX 4060 Ti (Ada Lovelace, 8 GB VRAM), `HDLAB_GPU_MEMORY_FRACTION=0.9` | anything with torch training or large matmuls: encoder training/eval, big-`d` capacity sweeps, transformer read-outs |

**VRAM is 8 GB and the fraction cap is 0.9.** A cell that needs more than ~7 GB does not belong on
`gpu_runner_0`; shrink the batch or route it to `cpu_runner_0` and accept the wall time.

### The dispatch path — LOCKED SHIP POLICY, do not shortcut it

1. **`exp_dev` authors the cell and smokes it LOCALLY**, then **RETURNS the exact `queue_add`
   command**. It does not ship remote.
   `python tools/queue_add.py <queue_name> <entry_name> <script_path> --prereg preregs/<file>.md --timeout <seconds>`
   `--timeout` is required (no silent default). Anchors named `_n>=4096` require `--timeout >= 3600`.
   The gate refuses a script that lacks `--self-test` or `--smoke`, or that does not write
   `data/exp_<HDLAB_EXP_NAME>/metrics.json` with `verdict`, `verdict_msg`, `elapsed_s`, `summary`.
2. **The orchestrator ships remote and owns post-ship verify.** After pushing any commit the remote
   runners need: `bash tools/remote_sync.sh` (it resets the remote worktree to `origin/main` and
   preserves any divergence on a timestamped branch).
3. **Verify the landing before believing it**: `python tools/verify_landing.py <anchor>`. Exit 0
   only. A `status=completed` in a queue file is **not** evidence a full run finished.
4. **If verify says the metrics file is missing but the remote shows a terminal state**, that is the
   sync-cadence gap, not a failure:
   `python tools/orchestrator/scp_recover_landing.py --verify-after <anchor>`. Only after *that*
   also fails may a landing be called missing.
5. **Liveness truth signal for a remote run** = the in-progress checkpoint file's modification time
   advancing **and** `nvidia-smi` utilisation, **never** the training heartbeat, whose cadence is
   coarse enough to have produced three false stall alarms.

### Per-item routing for everything in section 7

| backlog item | runner | why |
|---|---|---|
| 1 storage instrument (build + smoke) | `cpu_runner_local` | seconds to low minutes at d=256; must be iterated interactively |
| 1b storage instrument (full) | `cpu_runner_0` | 10 arms × 5 seeds × M up to 4096 × T up to 256; hours, and it must not block the local box |
| 2 `tools/exp_checkpoint.py` fix | `cpu_runner_local` | a self-test, not an experiment |
| 3 revise the storage draft spec | none — desk work | |
| 4 spokes-vs-flat-sum | `cpu_runner_0` | CPU-bound superposition sweeps, many arms |
| 5 learned-encoder power run | **`gpu_runner_0`** | torch forward passes over a 27M-parameter encoder across a larger pair population |
| 6 norms as a spoke | `cpu_runner_0` | 12-dim, trivially cheap, but multi-seed |
| 7 capacity (d=1024 on the live path) | **`gpu_runner_0`** | rebuilding every anchor store at 4x d; this is the memory-heaviest job in the plan |
| 8 conjunctive coding | `cpu_runner_0` | |
| 9 sparse coding level | `cpu_runner_0` | |
| 10 rare-feature weighting | `cpu_runner_0` | |
| 11 real-query sign arm | `cpu_runner_local` then `cpu_runner_0` | smoke local, full remote |
| 12 the 128 re-runs | `cpu_runner_0` (waves 0–2) | the original cells were CPU cells; a few `_gpu_` named ones go to `gpu_runner_0` |
| 13 foraging shelf | `cpu_runner_local` | it is a call site and a registry, not a sweep |

---

## 7. THE SEQUENCED BACKLOG

Format for every item: **the question** → **the can-fail design** → **the floor it must clear** →
**the stop-if**. The floor is always *a CI-separated margin over the strongest of
{orthographic, frequency, scramble} on the identical scorer, n, pool and gold* — **never a bare
number**. If an item does not name its floor, it is not ready to run.

Items are ordered. Do the lowest open one.

---

### ITEM 1 — BUILD THE STORAGE INSTRUMENT (component #2). *Blocks 4, 6, 7, 8, 9, 10.*

- **Question.** If you put many things in the store and then ask for one of them, do you get *that
  one*, or a blend of everything? And at what load does it start to fail?
- **Can-fail design.** Draft exists at `preregs/DRAFT_storage_quality_instrument_v1.md` — **read
  item 3 first, its central premise is falsified.** Four measures: fidelity at load; interference
  onset; **addressability** (ask for one facet of an item, score whether you get *that* facet rather
  than a different facet **of the same item** — the candidate pool is the item's own other facets,
  which is what makes a blended sum score at chance and an addressed store score at 1.0 on the
  identical scorer); crosstalk between feature-sharing items.
  The single-number discriminator is **key sensitivity** = score with the true key minus score with
  a shuffled key. A store with no address is insensitive to which key you present.
  Ten arms including an oracle dictionary, a slotted "spokes" reference, the live flat store, the
  other (fact) store scored separately and never merged into an "our store" claim, a null-content
  arm, a null-key arm, a scramble floor, an orthographic floor and a frequency floor.
  **Isolation from encoding**: every headline number is a *retention ratio* against the same arm's
  own single-item score, chance-corrected first, so a bad encoder cancels out of numerator and
  denominator. **The gold is what was WRITTEN, not what is TRUE** — truth is component #3.
- **Floor.** Addressability, CI-separated above `max(scramble, orthographic, frequency)` on the
  identical scorer/n/pool/gold, **and** key sensitivity ≥ 0.15 with CI excluding 0.
- **Instrument gates that must pass before any quality number is published**: oracle ≥ 0.99;
  slotted ≥ 0.95 at maximum load; null-content within chance + 0.05 with CI covering chance;
  `tools/saturation_negative_control.py` shows every measure declines monotonically as noise is
  added (**a metric that cannot go down is not a measurement**); and both floors land at chance ±
  0.05 on the addressability measure — **a floor beating chance there means the design leaks**
  (almost certainly the within-item gold fillers are not frequency-matched), and the fix is the
  construction, not the number.
- **Stop-if.** Any validity gate fails → report `INSTRUMENT_STILL_LOOSE`, publish no quality
  number, stop. Precedent: three versions of the foundation validator scored a random decoy at
  0.76 where it should have been near zero, and every number they produced was void.
- **Known risks, pre-declared so a later change is visible:** 4 facets gives a chance level of 0.25,
  which is high — if the spread is small, raise it to 8 **before** the run; d=256 is very small for
  superposed facet retrieval, so a d=1024 sentinel arm exists specifically so that a null at 256 is
  not misread as an architecture verdict when it is a dimensionality one.

---

### ITEM 2 — FIX `tools/exp_checkpoint.py`. *Independent. Small. Do it early.*

- **Question.** Can a full run still silently reload a smoke run's result?
- **Why it is here.** `experiments/_seed_checkpoint.py` was fixed at `ee7c42c0f`.
  **`tools/exp_checkpoint.py` has the same defect in a worse form and is the module `CLAUDE.md`
  makes MANDATORY for any cell looping over more than one (arm, seed) unit.** `unit_key(*parts)` is
  caller-composed with no config discriminator, and `completed_units(output_dir)` has **no
  config-check parameter at all** — there is no opt-in guard to forget, because none exists.
  Reproduced: record a unit at N=1024 in smoke mode, then a full at N=16384 computes the key
  `armA|17`, finds it, and reuses the smoke result.
- **Can-fail design.** Additive only: a config-fingerprint variant of `unit_key`, plus a
  `completed_units_checked(output_dir, config)` that **raises** on a recorded-config mismatch,
  leaving the four existing functions byte-identical. A regression self-test that **reproduces the
  collision on the old path and proves it is gone on the new one**.
- **Floor.** Not applicable — this is a self-test, not a measurement. The gate is the regression
  test failing before the fix and passing after.
- **Stop-if.** A cell is actively running that imports it → wait. Editing a module a live run
  imports is exactly the hazard.
- **Note for whoever does this.** The 38 experiment files importing `_seed_checkpoint` still use the
  old seed-only contract; they now get a warning, not protection. **Migrating them is the real
  remaining work** and is a separate, larger item.

---

### ITEM 3 — REVISE THE STORAGE DRAFT SPEC AGAINST WHAT THE CODE ACTUALLY DOES. *Desk work. Blocks item 1.*

- **Question.** Does the store apply a key at write time — yes or no?
- **Why.** The draft assumed contributions were `bind(REL:k, filler)` and concluded the flat sum has
  a *latent* address degraded by crosstalk, "not structurally incapable of facet retrieval". Runtime
  reconstruction shows what actually accumulates is `acc += symbol_vector(w)` — **no key**. The
  role-binding path exists, unbinds cleanly, and nothing calls it.
- **What changes.** The instrument's `A2_LIVE_FLAT` arm must be split into **two** arms: the live
  no-key store, and the built-but-uncalled role-binding store. Key sensitivity on the no-key arm is
  ~0 **by construction**, so it is not a finding — it is a positive control that the instrument is
  reading the right thing. The *interesting* measurement moves to the role-bound arm: it has a key,
  so how much address survives at live load?
- **Floor / stop-if.** Same as item 1; this item only changes the arm definitions.
- **This is the concrete instance of new rule R12** (section 10): a spec's premise gets verified by
  runtime reconstruction before anything is built on it.

---

### ITEM 4 — SPOKES VERSUS ONE FLAT SUM. *After 1 and 3. The architecture question.*

- **Question.** If you give the same content several separately-addressed stores instead of one
  blended one, does the store become askable?
- **Brain claim being tested.** Hub-and-spoke with each piece keeping its own address:
  **PINNED-BY-EVIDENCE** as architecture. The implementation as unbind-by-role-key:
  **OUR-INVENTION-BEING-TESTED**.
- **Can-fail design.** On the *unchanged* storage instrument, add a small set of property-typed
  stores as one arm against today's single flat sum as another. Identical items, identical queries,
  identical gold. One variable: how many stores and whether they are separately addressed.
- **Floor.** CI-separated above `max(scramble, orthographic, frequency)` on the identical scorer,
  **and** CI-separated above the flat-sum arm, **and** key sensitivity ≥ 0.15.
- **Stop-if.** **If the slotted reference arm also scores low, the instrument or the hypothesis is
  wrong** — addressing is then not the lever and the plan reorganises around selection. If every
  candidate ties the flat sum, same conclusion. Say so; do not keep proposing variants.

---

### ITEM 5 — GIVE THE LEARNED ENCODER ENOUGH STATISTICAL POWER TO ANSWER. *Independent. GPU.*

- **Question.** Is the learned encoder's +0.109 margin over the hardened frequency floor real, or is
  322 SimLex pairs simply too few to tell?
- **Why it matters.** This decides whether we own a meaning source at all. The current answer is
  "not established", which is not the same as "no".
- **Can-fail design.** Same instrument, same floors, **more pairs**: extend the item population
  beyond the 322 SimLex pairs the instrument's frequency-ranked vocabulary happens to cover.
  Keep the random-initialised twin arm (same architecture, same tokenizer, untrained weights — it
  has TIED the learned encoder before), the row-permuted scramble twin, and the
  concreteness-controlled partial correlation (a concreteness confound has inflated a
  learned-encoder result before: a gap of 1.6022 collapsing to 0.0406 took 0.71/0.75 down to
  0.59/0.46).
- **Floor.** CI-separated margin over `max(hardened frequency, orthographic, scramble)`, paired
  bootstrap over the identical pairs. The hardened frequency floor is currently **0.0797**
  (channel `FREQ_MIN`, the strongest of four seed-free frequency channels).
- **Stop-if.** With adequate power, the margin's CI still includes zero → the learned encoder is
  **not** a meaning source we can use, and item 6 becomes the meaning candidate. Record it as a
  measured null, not a defeat.
- **Honest labelling requirement.** A larger item population is a **different population**. Its
  numbers are not instrument numbers and must be labelled so in their own metrics file. Do not quote
  them as the like-for-like result.

---

### ITEM 6 — THE GROUNDING NORMS AS A REAL SPOKE, NOT AS A FILTER. *After 1. Independent of 5.*

- **Question.** The norms are sensorimotor ratings — exactly the shape of a modality spoke. They
  have only ever been tried as a similarity *filter*, capped at 0.45 so they structurally cannot
  cross the 0.50 decision threshold, and shelved. **Do they work as a separately addressed spoke?**
- **Brain claim.** Modality-specific cortex feeding the hub: **PINNED-BY-EVIDENCE**. Two hard
  results bound the design and must be respected: a sensory-independent code for object colour
  exists in blind and sighted alike, so a spoke is not the only route to that knowledge; and
  text-only channels recover non-sensorimotor meaning well, sensory poorly, **motor minimally**.
- **Can-fail design.** Norms as one addressed store among several, on the item-1 instrument, at the
  norms' native 12 dimensions with all floors re-run at 12 dimensions and **no comparison made
  across dimensionality blocks**.
- **Floor.** The measured Lancaster random-word-pair floor. Be aware raw cosine on these norms
  **cannot separate a synonym from a sibling** by the module's own numbers: sofa/couch 0.968,
  happy/joyful 0.962, apple/orange 0.952, dog/cat 0.932. A design that needs that separation will
  fail, and should.
- **Stop-if.** Scores on the floor as it did as a filter (0.8071 versus a 0.8060 random floor) →
  the norms are not a usable spoke for this task. Do not revive a third time without a new mechanism.

---

### ITEM 7 — CAPACITY ON THE LIVE PATH. *After 1. GPU. Largest measured lever we own.*

- **Question.** Sixteen times the dimensions bought **+0.0843** at probe scale — more than any
  mechanism change this programme has produced. Does it survive on the real, full anchor population?
- **Can-fail design.** Held-out near-neighbour two-choice **on the live path, not on a probe** —
  full anchor set (2,377+ concepts, not the probe's 400), graded field and graded query, at d=1024,
  with d=4096 as a labelled diagnostic carrying no verdict weight, against the live d=256 baseline
  of 0.6395.
- **Floor.** In-cell scrambled-context floor (must land 0.49–0.51; prior cells give 0.4975 / 0.5065
  / 0.49775 / 0.5095), frequency baseline 0.4800, chance 0.50. **MANDATORY: report the
  between-projection-draw standard deviation next to the CI (0.0090 at d=256).** Item bootstraps are
  blind to shared-randomness variance, and every cell built on a random projection must report it.
- **Stop-if.** The gain does not survive the full population, or memory/latency at d=4096 make it
  unusable as a default → "capacity is a probe result, not a live capability."
- **Honest caveat to write into the report up front.** At probe scale this is already measured
  (0.7030 sign at d=1024; 0.78225 graded at d=4096). **This is a WIRE-IT test, not a discovery.**
  Do not report a re-measurement of a known effect as a new finding. And **0.7495 is the d=1024
  graded arm — it is not the live path**; the live path moved 0.6395 → 0.6980.
- **BLOCKED PENDING OWNER AUTHORISATION** (decision D1): raising d rewrites every persisted anchor
  store, and a concurrent session is live.

---

### ITEM 8 — CONJUNCTIONS INSTEAD OF FEATURES. *After 4.*

- **Question.** The brain codes conjunctions of features, not features. We add features. A floored
  result already exists: conjunctive 1.000 versus additive 0.273 at M=256, and **the additive arm is
  our geometry**. Does conjunctive coding survive on real text rather than a synthetic world?
- **Can-fail design.** Conjunctive versus additive coding of the same real extracted content, on the
  item-1 instrument, with the **disjoint-feature must-fail control** reused wholesale from
  `exp_interference_avoidance_conjunctive_vs_additive_v1`: in a regime where items share no
  features, every arm must show |slope| ≤ 0.05. If the disjoint regime also shows a slope, the
  effect is a confound and the measure is not reporting crosstalk.
- **Floor.** The additive arm at matched dimensionality, plus scramble, orthographic and frequency.
- **Stop-if.** Conjunctive ties additive on real content → the synthetic win does not transfer; say
  so plainly. **Do not attribute the design to perirhinal feature-ambiguity** — that literature is
  contested with real failed replications, and the conjunction operator is unpinned and ours.

---

### ITEM 9 — SPARSE INSTEAD OF DENSE. *After 4.*

- **Question.** Cortical and medial-temporal codes are sparse; ours is dense. Sparse coding level in
  the medial temporal lobe is **pinned**: about 0.2% of neurons per percept, each neuron responding
  to 50–150 concepts. Does a code at that sparsity address better than a dense one?
- **Reuse.** `hdlab/dg_pattern_separation.py` — random expansion, keep top-k, normalise. That is
  **the brain's operation, in the right order, at roughly the right sparsity**, and it has **zero
  importers**. This is a wire-and-measure job, not a build job.
- **Careful, this is a documented trap.** ~0.2% sparse coding is the **medial temporal** regime. The
  semantic hub is **dense and graded** — first ~4 group principal components define the shared
  space, about two-thirds of temporal-pole electrodes active per exemplar. **Conflating the two
  systems is the trap.** So: sparse for the *index*, dense for the *hub*, and say which you are
  building.
- **Floor.** Same instrument, same floors. Plus the dense arm at matched dimensionality.
- **Stop-if.** Sparse ties dense on addressability → sparsity is not the lever here.

---

### ITEM 10 — RARE FEATURES OUTWEIGHING COMMON ONES. *After 9. Lowest confidence in this group.*

- **Question.** The brain privileges distinctive (few-concept) features; our hub weights a tag
  shared by 8 concepts exactly as much as one shared by 1.
- **Why it is last and why it is honest to say so.** The weight function is **UNPINNED** — nothing
  in the literature says by how much a rare feature is up-weighted — and our one instantiation
  (log-IDF) was **refuted by recompute in both of its mechanistic claims**: near-cancellation is 4.3x
  *rarer* under weighting, and the per-component step *transmits more* of the perturbation than
  whole-vector normalisation. The real cause was diagnosed: a mean of 2.91 features per concept and a
  weight range spanning only 2.34x cannot restructure a cosine.
  **Refuting the normaliser does not revive the route.** Four separate re-weighting interventions
  have measured null or harmful. **That is an estimation-noise statement, and it points at capacity
  (item 7), not at weighting.**
- **Only run this after item 7 lands.** With 70 observations per concept in a 256-dimensional random
  projection, the dimensions with the largest differences are disproportionately the worst-estimated
  — so any per-dimension reweighting is measuring noise. If item 7 gives us a dimensionality where
  estimation is not the limiter, this becomes a fair test. Until then it is not.
- **Stop-if.** Null at the new dimensionality → the route is closed, with a fifth floored negative.

---

### ITEM 11 — THE MISSING ARM THAT WOULD PUT BOTH SIGN CLAIMS IN ONE CELL. *Independent. Cheap.*

- **Question.** The sign was measured under **isotropic Gaussian noise**, where magnitude is pure
  liability and the sign therefore *helps*. Production queries are **real held-out sentences**. What
  does the post-sum sign cost under a real-query model?
- **Can-fail design.** One additional arm inside the encoding instrument whose probe is a held-out
  sentence rather than isotropic noise. Everything else identical.
- **Floor.** Not a floor question — this is an instrument-completeness question. The gate is that
  the arm reproduces the published numbers under the noise model and then reports the real-query
  number alongside it.
- **Stop-if.** Nothing to stop; this closes a named open question rather than testing a hypothesis.
- **Named as an open question, not run, by the audit that found it.** It is a cell author's job.

---

### ITEM 12 — THE 128 RE-RUNNABLE CELLS. *Background work. See section 8.*

---

### ITEM 13 — THE SHELF: LET THE SYSTEM CHOOSE WHAT TO READ NEXT. *Independent of everything above.*

- **Question.** The organ that decides what to read next **does not exist**, which is why the system
  cannot notice what it does not know. The loop reads the same 4 segments forever, producing a
  64.5% biology skew.
- **Reuse.** `gap_driven_reader.rank_material()` is already HARD_PASS. What is missing is (a) a
  registry enumerating `data/corpora/` — *the shelf*, roughly 15 lines, which exists nowhere; (b) a
  call site pointing `rank_material()` at that registry instead of a synthetic dictionary; (c) a
  driver of roughly 60–100 lines.
- **Can-fail design.** Seed the loop with the current foundation. Let it choose its next corpus from
  the 36 available for N cycles. Measure the share of newly-grounded terms that are **everyday,
  non-biology** vocabulary.
- **Floor — two arms, both must be beaten.** Random corpus choice over the same 36 (**if gap-ranked
  selection cannot beat a coin flip, the organ adds nothing, and this is the arm that kills it**),
  and the frozen 4-entry schedule that produced the skew. Report per-arm CIs and the seed count.
- **Stop-if.** Ties random → the ranking adds nothing; keep the shelf, drop the ranker.
- **Honest caveat.** The brain equation here is **UNPINNED**, so this reaches *function* parity, not
  *equation* parity. State that in the writeup.
- **Why it is worth doing even though it is last:** nothing downstream can be tested on genuinely
  new material until it exists, and the "we simply have not read enough" hypothesis has never been
  given a fair test.

---

## 8. THE 128 RE-RUNNABLE CELLS — cheapest-correct order

Ordering principle: **value first, then cost inside each value band.** Tier is the value axis
(MEDIUM = still on a live path; ARCHIVE = superseded). Declared N is the cost axis and drives
runtime superlinearly. Re-running an ARCHIVE N=16384 cell before a MEDIUM N=4096 cell spends the
most compute on the least-wanted answer.

**Precondition, and it is not optional.** Re-run **only** after migrating the affected cell to the
config-aware checkpoint API, **or** into a fresh output directory. Re-running on the old contract
into a directory that still holds the smoke partial reproduces the same corruption — it now raises
rather than silently succeeding, which means you get a failed run instead of a wrong number, but it
is still a wasted run.

**Route: `cpu_runner_0` (remote CPU) for waves 0–2**, except the two `_gpu_` named modern-Hopfield
cells in wave 2, which go to `gpu_runner_0`.

### WAVE 0 — 3 MEDIUM cells. Do these first regardless of cost.

| # | anchor | declared N | actually ran at | banked verdict |
|---|---|---|---|---|
| 1 | `exp_kf45_pre_argmax_joint_probe_v1_n4096` | 4096 | 1024 | PASS |
| 2 | `exp_reasoning_storage_4way_cleanup_v1_n16384` | 16384 | 512 | PASS |
| 3 | `exp_reasoning_storage_4way_cleanup_v3_hadamard_hopid_v1_n16384` | 16384 | 512 | PASS |

All three are banked **PASS** at a scale they never reached. Those three PASS verdicts are the only
results at stake at this point in the queue.

### WAVE 1 — 19 LOW cells at N=4096.

`exp_alpha1_cleanup_sweep_n4096` · `exp_axis3_triplepoint_v1_n4096` ·
`exp_bid_order_parameter_v6_n4096` · `exp_bid_order_parameter_v7_n4096_bsc` ·
`exp_cross_shard_correlation_k10_v1_n4096` · `exp_kf4_drift_detect_v4_n4096` ·
`exp_kf5_phase_v1_n4096` · `exp_lyapunov_v1_n4096` ·
`exp_maes_netocny_frenesy_positivity_v1_n4096` · `exp_multi_hop_higher_m_stress_v1_n4096` ·
`exp_pb1_susceptibility_v2_n4096` · `exp_pb2_corr_len_v4_n4096` · `exp_phase_region_cd_v1_n4096` ·
`exp_region_c_kf1_n4096_beta64_mfrac4` · `exp_sagawa_ueda_mutual_info_jarzynski_v1_n4096` ·
`exp_superposition_single_hop_decomp_v1_n4096` · `exp_t1_beta_fine_v2_n4096` ·
`exp_t1_m_sweep_v1_n4096` · `exp_tensor_binding_two_shard_v1_n4096`

### WAVE 2 — 8 LOW cells at N ≥ 8192.

At N=8192: `exp_bid_m_normalized_v5_n8192` · `exp_hatano_sasa_v3_n8192_multiseed` ·
`exp_kf2_be1_retrieval_acc_n8192` · `exp_modern_hopfield_ceiling_probe_gpu_v1_n8192` (**GPU**) ·
`exp_modern_hopfield_replication_gpu_v1_n8192` (**GPU**).
At N=16384: `exp_modern_hopfield_cpu_backup_extended_v1_n16384` ·
`exp_modern_hopfield_cpu_extended_v9_n16384` · `exp_n_scaling_chunked_codebook_v4_n16384`.

### THE REMAINING 98 — ARCHIVE tier. **STOP HERE AND ASK.**

After wave 0 there are 3 results at stake; after wave 2, 30. The remaining 98 are ARCHIVE-tier
(77 at N ≤ 4096, 21 at N ≥ 8192). **Do not default into 98 re-runs.** This is decision D5 in
section 9; the recommended default is **do not re-run them**, and record that as the decision.

### What this population is NOT

- **It is 128, not 273.** The two circulating figures are marginals of different sets: 187 runs have
  elapsed time under 1 second and 179 have a declared N disagreeing with the N actually run; their
  intersection is 133, of which 5 already have a verified full.
- **A further 138 runs have no full and no positive evidence of the collision** — 95 of them carry
  no declared-versus-actual N record at all. Most are plausibly genuine smoke-only runs never
  dispatched as a full. **They are not established as victims and must not be re-run on that basis.**
- **The owner's directive "there is always a full if it's graded hard pass — you just need to find
  it" does not hold for this cohort, and the reason is mechanical, not a failed search.** Of 274
  atoms enumerated: **8** have a verified full of the same experiment, 29 have a non-smoke sibling
  somewhere in the family (candidates, not recoveries — the sibling was not checked for testing the
  same hypothesis), 208 are genuinely smoke-only, and 29 are ambiguous. For the affected anchors the
  full was dispatched and silently no-op'd, so **there is no full on disk to find. They need
  re-running, not finding.**
- **One "recovery" is a reversal, not a rescue.** `exp_chunked_codebook_n16384_v6_smoketest` was
  banked HARD_PASS at N=1024 with one seed; its own full at N=16384 with 3 seeds is
  **HARD_FAIL** (out of memory at M ≥ 2048, 9 of 9 cells). Expect more of these.
- **What the search did not cover, stated so nobody re-reads it as exhaustive:** no remote queue or
  SSH host was queried, so a full that ran remotely and was never pulled back is invisible; git
  history was not searched for deleted-then-recommitted metrics; non-`metrics.json` result formats
  were not treated as full-run evidence.

---

## 9. DECISIONS FOR THE OWNER

Each has a **recommended default**, so silence is safe — if no answer comes, the default is what
happens, and the loop records that it took the default.

> A separate agent is building `notes/BOARD.md` and `tools/board.py`. **Do not create or edit
> those files from here.** This list lives in the plan only.

**D1 — Raise the working dimensionality from 256 to 1024 on the live path?**
Sixteen times the dimensions bought +0.0843 at probe scale, the largest lever measured. It rewrites
every persisted anchor store, and a concurrent session is live.
**Recommended default: HOLD.** Do it only when no concurrent session is running and a backup of the
persisted stores exists. It is item 7 and it is worth doing; it is not worth doing unsafely.

**D2 — Do we wire a learned transformer encoder into the representation at all?**
It is 27,172,864 parameters, 6 layers, trained from scratch **by this project** on ARC text with our
own 16k tokenizer. No external model is contacted at any point. Its codes are computed once, offline,
into a static table. It is not an external LLM. **But it is an opaque learned function**, and if the
glass-box requirement is read as "no opaque learned function anywhere in the representation", it is
disqualified on policy, not on score. **That is a policy call for the owner, not a measurement.**
**Recommended default: MEASURE IT, DO NOT WIRE IT.** Finish item 5 and get a real number. Wiring is
a separate decision after a verdict.

**D3 — If the learned encoder does clear the floor, does it count as a "spoke"?**
It is trained on text, and the literature is explicit that text-only channels recover
non-sensorimotor meaning well, sensory poorly, motor minimally. Calling it a spoke would be a
fidelity claim we cannot support.
**Recommended default: call it a text-derived meaning source, not a spoke.** Tag every use
**OUR-INVENTION-BEING-TESTED**.

**D4 — Migrate the 38 experiment files still on the old checkpoint contract?**
They now get a warning, not protection. This is the real remaining work behind item 2 and it is
mechanical, bulk, and low-judgement.
**Recommended default: migrate only the cells that are actually re-dispatched**, at the moment they
are re-dispatched, rather than a big-bang migration.

**D5 — Re-run the 98 ARCHIVE-tier collision-affected cells?**
Lowest value at highest cost. 21 of them are at N ≥ 8192.
**Recommended default: NO.** Mark them collision-affected in place so nobody quotes them, and stop
after wave 2.

**D6 — Merge this branch to `origin/main`?**
`dataprep/mcguffey-graded-corpus` has been the working branch for days.
**Recommended default: HOLD.** Merge needs explicit authorisation; nothing in this plan requires it.

**D7 — Is "growth" still paused?**
It is, and this plan does not unpause it. Growth is not invalidated — the no-leak and scramble
results stand — but nothing here depends on running it.
**Recommended default: stays paused** until component #2 has an instrument.

---

## 10. STANDING RULES — earned the hard way

R1–R12 carry forward. **R13 is new (2026-08-16) and is a standing owner directive, not a
session finding. R14 and R15 are new (2026-08-16), each earned by an incident on the same night
and each citing it inline. R12 carries a dated re-earning note; it was NOT duplicated as a new
rule, because two rules for one discipline drift apart and then contradict each other — which is
the exact defect the CA3 correction in section 5 had to repair.**

1. **A gate is a CI-separated margin above the strongest no-understanding floor** —
   `max(orthographic, frequency, scramble)` — on the identical scorer, n, pool and gold. **Never a
   bare absolute number.** This cost us the whole ">=10%" criterion, which a spelling channel
   cleared. The baseline must be **standalone**: an arm that adds a shortcut *on top of* the system
   under test is a decomposition, not a floor.
2. **A floor and a known-answer arm fail independently.** A floor says whether the **effect** is
   real. A known-answer arm says whether the **instrument** is. Run both, every time.
3. **A gain measured on one scorer may not be carried to another.** A two-choice gain (chance 0.50)
   was quoted onto an open-vocabulary pool where the same manipulation is null.
4. **Detectors fire on honesty.** Cells that explicitly disclose their own scope get flagged for
   naming the thing they said they did not test. 49 flagged candidates across three passes, 49 false
   positives. Hand-adjudicate any large flag class before believing it.
5. **Silent joins fabricate both green and red.** A dropped id prefix produced a false clean bill on
   314 atoms, and separately a false "1,113 missing" that was really 32. Assert and count joined rows.
6. **Enumerate, never search, for absence claims.** State **how** you enumerated. Search by shape,
   not by keyword — the verdict vocabulary drifted from 13 strings in June to 444 in July.
7. **No demotion without a fresh on-disk re-check.** A negative about someone else's landed result
   is itself a claim and gets the same scrutiny as a positive. Keep **EXISTS**, **IS-REACHED** and
   **IS-GOOD** as three separate questions.
8. **Overnight autonomy is authorised in principle, but any non-stopping loop needs a harness-level
   deny rule on `preregs/` and arm-key files.** An agent that cannot stop will eventually try to
   adjust the bands.
9. **Wiring is decided by RUNTIME, never by grep.** Lazy imports inside function bodies are
   invisible to grep; a string constant and a comment both read *as* imports. Import the code and
   inspect `sys.modules`.
10. **Enumerate from the filesystem, then reconcile to the registry — never the reverse.** The
    registry is wrong in both directions and has no row at all for the thing that encodes every word
    in production.
11. **NEW — an over-scoped claim must state its AXIS.** "Sign destroys zero" was true at one site,
    at one noise level, and by construction for half the arms — and its own cell's next row
    contradicted it. The rule: any headline of the form "X destroys / preserves / dominates" must
    carry, in the same sentence, **which operation, at which site, under which query model, at which
    scale**. A claim without an axis is not a finding, it is a slogan waiting to be misapplied.
12. **NEW — a spec's premise gets verified by RUNTIME RECONSTRUCTION before anything is built on
    it.** A storage instrument was designed on the premise that the store applies a role key. It
    does not. The premise came from reading a code path that exists and is never called. **Before
    building on "the code does X", run the code and reconstruct X from what it actually produces.**
    Cost of not doing it: a whole instrument design measuring the wrong arm.
    *RE-EARNED AND CONFIRMED 2026-08-16, with the incident named precisely so the rule is
    recognisable next time:* `preregs/DRAFT_storage_quality_instrument_v1.md` "key finding 2" was
    written against **"the store keeps a smeared key"** — a latent address degraded by crosstalk.
    Runtime reconstruction shows what actually accumulates is `acc += symbol_vector(w)`: **the store
    keeps no key at all.** The difference is not a detail. A smeared key makes "recover the address"
    the measurement; an absent key makes key sensitivity ~0 **by construction**, so that arm is a
    positive control and not a finding, and the real measurement moves to the built-but-uncalled
    role-binding path (`hdlab/reading_grounding_loop.py:436`, default-OFF). Backlog item 3 exists
    solely to repair that spec. **This was deliberately NOT filed as a new rule R16** — it is the
    same rule, re-earned, and splitting one discipline across two numbered rules is how the CA3
    contradiction in section 5 came to exist.
13. **NEW — every component names WHICH BRAIN STRUCTURE, and every shelve reason is BRAIN-framed,
    never performance-framed.** The question is not "did we consider the brain?" — it is **"which
    brain structure, and are we replicating it or substituting something convenient?"** The default
    opening move on any component is *how does the brain do this*, **before** surveying available
    tools, before measuring, before optimising what we already have. For each component state: (a)
    the **brain structure** — a neural system (CA3, dentate gyrus, perirhinal cortex, DMN), not a
    cognitive-theory label ("working memory" and "attention" are labels); (b) whether it **reuses an
    organ we already own** — the brain reuses circuits, so a parallel build is both unfaithful and
    islanding; (c) each design choice marked **PINNED-BY-EVIDENCE** or **OUR-INVENTION-BEING-TESTED**
    — invention is authorised, presenting invention as pinned is not; (d) any **shelve or revival
    criterion in brain terms**.
    *The incident:* `hdlab/perirhinal_conjunctive.py` was shelved with the revival criterion
    **"exact-key retrieval only"** — a performance-engineering framing in a project whose whole
    thesis is brain fidelity. The brain never retrieves with an exact key; it **completes from a
    partial cue**. The brain-framed criterion is that conjunction is not testable until **pattern
    completion (CA3)** sits in front of it, because **separation (DG) and completion (CA3) are a
    matched pair**. The wrong frame would have shelved a correct component for the wrong reason and
    **hidden the actual missing organ**. That is the cost: a wrong frame closes a live research
    direction. Owner, 2026-08-15: *"we need to be doing brain foundational things - not maximizing
    performance in single areas"*; *"the way we lose is by trying fancy available tools."*
    *Enforced by construction, not by this paragraph:* `tools/dispatch_batch.py` folds the block
    into every composed brief, and `tools/capability_registry_audit.py` requires `brain_structure` +
    `fidelity_basis` on registry rows going forward (pre-existing rows are reported as a backlog and
    **never auto-filled** — a fabricated brain justification is worse than a missing one).
    *Contradiction closed 2026-08-16:* this rule used to sit in the same document as an explicit
    "do NOT build CA3" recommendation in section 5. Resolved in favour of **building the completer**
    — see the dated correction under the section 5 table.
14. **NEW — a claim measured at the EXACT-KEY operating point does not transfer to the PARTIAL-CUE
    regime, and the partial-cue regime is the real one.** The brain never presents a stored key back
    to itself; every real query is a new, partly-overlapping encounter. So a measurement taken with
    the query set equal to the stored item is a *best case*, not a *typical case*, and a cost that
    is invisible there can be large one step away from it.
    *The incident, both halves measured the same night on the same object:* with an **exact key**,
    `data/exp_hub_spoke_word_representation_v1/metrics.json` gate G5 reports the terminal `sign()`
    costing **exactly 0.000 bits** at bundle sizes 2 and 3 — the sizes this architecture actually
    uses — which reads as "the sign is free here". With a **partial cue**,
    `data/exp_hub_spoke_partial_cue_curve_v1/metrics.json` reports item identification of
    **0.9668 unsigned versus 0.7018 signed at 50% overlap** (0.0322 vs 0.0153 at 20%), and the
    signed arm's paired delta against the flat bag is **−0.2546, CI [−0.2848, −0.2243]** at 50% and
    **−0.0176, CI [−0.0309, −0.0046]** at 20% — CI-separated below at both. Recomputed off disk,
    3-seed mean at d=256, for this rule. **The live read-out does `sign()` of a sum and always
    queries with a never-seen context**, so this is a measured cost sitting on the live path that
    the exact-key number would have told you was zero.
    *How to apply it:* before quoting any "X costs nothing / X is free", state the query model in
    the same sentence (this is R11's axis requirement, and this is the case that shows why the
    **query model** is the axis that gets dropped most often). Where the claim is load-bearing, run
    the partial-cue arm; it is usually one extra loop over a degradation fraction, not a new cell.
15. **NEW — a smoke's HAND-COMPUTED gate verdict is not a gate. Only the cell's own gate code, run
    at full, decides.** A hand-computed verdict is an argument about what the gate would say, made
    by the party who wants it to pass, using numbers it selected itself. It is not evidence, and it
    must never appear in a report in the grammatical form of a result.
    *The incident:* the hub-and-spoke smoke report recorded **"G1 would pass"**. At full, the cell's
    own `evaluate()` returned **G1 = FAIL**, with no threshold touched
    (`data/exp_hub_spoke_word_representation_v1/metrics.json`, `verdict: PARTIAL`). The hand
    computation had silently used a max-floor CI upper of **0.2583**, i.e. it dropped `F_SCRAMBLE`
    from the pre-registered floor set. Recomputed off disk today, per arm at d=256: **F_SCRAMBLE
    facet recovery 1.0000, CI [1.0000, 1.0000]** — bit-for-bit the treatment arm's own score, and
    `N_NULLCONTENT` scores 1.0000 there too. So the pre-registered gate is unpassable as written,
    and the automated path had never run at smoke at all (it produced NaNs from a `load_units` bug).
    The full run was the **first** evaluation of that gate by code.
    *Two things this rule does NOT say.* It does not say the floor set was right — `F_SCRAMBLE` is a
    floor on the MEANING axis and not on the facet axis, which is a real design defect, recorded as
    prereg amendment A4. It says the place to fix that is **a dated prereg amendment BEFORE the
    run**, never a hand adjustment after it. And it does not say the substantive reading must be
    withheld: report it **beside** the failing gate, never **instead of** it, which is what that
    cell did.

**Two disciplines that are not rules but are how we work:**
- **Plain language.** The owner has said twice that jargon makes these documents unusable to them.
  Write "the right answer is in our top 50", not "recall@50".
- **Deflate claims, not ambition.** Rate results GOOD / MEDIOCRE / BAD honestly and deflate the
  claim, never the goal. A miss is never a ceiling until the test was fair *and* the thing tested was
  what the brain actually does.

---

## 11. HOUSEKEEPING

**Do not touch, currently:**
- `data/exp_coref_margin_gated_cleanup_local_window_break050_v1*` — a live agent owns it.
- `data/exp_structured_comparator_v1/probes/` and `CLAUDE.md` — concurrent writers; never stage.
- `data/foundation/reading_grounding_v1` and `v2_qualityfix` (22 + 23 MB) — **no backup**; the 37 MB
  snapshot is gitignored and not on the remote (reproducible from code plus corpora, but not cheaply).
- `notes/BOARD.md` and `tools/board.py` — another agent is building them.
- `preregs/` arm-key files and `experiments/**` — only `exp_dev` authors those.

**Provenance debt to clear** (a durable document citing a scratch script makes that script no longer
throwaway, and `scratch/` gets wiped):
`scratch/posthoc_collision.py`, `scratch/posthoc_ci.py`, `scratch/probe_live_encoder.py`,
`scratch/probe_all_entrypoints.py`, `scratch/enum_meaning_assets.py`,
`scratch/enum_encoder_assets2.py`, `scratch/probe_learned_assets.py`,
`scratch/probe_wired_runtime.py`, `scratch/count_arc_tokens.py`.
Promote to `tools/` or re-derive their numbers. (`tools/audit_sum_vs_sign_probe.py` and
`audit_sum_vs_sign_probe2.py` were already promoted this way and re-run bit-identically.)

**Known instrument defect, disclosed and deliberately not fixed** (fixing it after seeing the data
would be tuning): the encoding instrument's stage chain is a branching graph, not a chain — the
bundle stage takes the graded codes, not the signed ones. Numerically immaterial; the **label** is
what invites misreading. Fix it in v3, before the chain is used for anything new.

**Delegation.** Batch 4 agents per message, hard ceiling 5. Every brief carries: no-spawn, the
disclosure rule verbatim, the fragment-report convention (`.claude/scan-out/<name>.json`, return ONE
line), and the do-not-touch list. `tools/dispatch_batch.py` composes these automatically.

**The disclosure rule, verbatim, for every brief:**

> If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.

And give the reason, so the agent does not negotiate with itself: **a dropped precondition
invalidates the declared gate even when the result may be fine.** Note also that a denial reading
*"The user doesn't want to take this action right now"* is **ambiguous** — it is emitted both for a
real rejection and for an ESC interrupt that tore down every in-flight call at once. Only
*"Permission to use ... has been denied"* means a rule fired. Report and stop either way; do not
write a prohibition into a downstream brief on the strength of the ambiguous string.
