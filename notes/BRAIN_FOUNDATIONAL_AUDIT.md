# BRAIN-FOUNDATIONAL AUDIT — the whole substrate against the brain it reconstructs

**updated: 2026-08-26** · living document, edit in place · **THE single reconciled map of substrate-vs-brain.**
Reconciles the three prior audits onto one list: `ORGAN_MAP.md` (38 organs, per-organ brain-math, 08-22),
`component_brain_fidelity_ledger.md` (14 components, 07-30), `LONG_TERM_PLAN.md` §4 (phases, 08-16). Where
they disagree, this file is the current view and names what went stale.

**Provenance / honesty scope:** the per-organ fidelity verdicts below are carried from `ORGAN_MAP.md` (read in
full 2026-08-26), not independently re-derived this pass; the whole-brain coverage is from a full read of all
155 `hdlab/*.py` docstrings. Treat verdicts as "as-audited," re-verify before acting on any single one. Numbers
are as-quoted from their source cells and do not cross scorers/populations.

---

## 1. THE HEADLINE (plain language)

We mapped 38 "organs" the brain uses to read, mean, remember and reason, plus the systems around them.

- **Only 5 of 38 organs compute the brain's actual equation.** For **12** neuroscience has written down the
  equation, so "build the brain's version" is even a well-posed instruction; for **14** the core operation is a
  mystery *even in neuroscience*, so we are inventing (honestly labelled) — including **our single most central
  operation, binding**. **7 organs don't exist in code at all.**
- **~54% of the code is unreachable** from any live entry point — built-but-unwired islands.
- **Two defects are bigger than any single organ:** (1) **we ask every question of the wrong memory** — the fast
  episodic "sketchpad," never the consolidated long-term store that was written but never read back; (2) a
  **`sign()` quantiser at the end of almost every step** throws away signal strength and keeps only direction,
  which quietly turns the whole system into an averaging machine.
- **The systems we DO build well are lopsided toward reading:** coreference, goals/reward, valence, and
  metacognition are richly built; **Theory of Mind is absent, dedicated meaning-selection (semantic control) is
  thin, and the speaking side is essentially one file.** This substrate is a reader, not a speaker.
- **Corrected this pass:** the 07-30 ledger called coreference and discourse "ABSENT." That is **stale** — both
  are now substantially built. And the meaning step is **no longer "empty" (see §7):** on a fair test it beats
  frequency; it is unwired, not absent.

---

## 2. HOW THIS DOC IS USED (it is a living, shared reference)

- **Every solver brief references this file.** A solver reads the entry for the system it is touching before it
  starts, so it inherits the brain frame and the known deviation instead of re-deriving it.
- **Solvers report deviations/updates they find.** If, during the work, a solver discovers the fidelity verdict
  here is wrong, stale, or incomplete — or finds a new deviation — **that goes in the submission** (a short
  "AUDIT UPDATE" note), and **the strategy session incorporates it here at integration.** The audit improves as
  the work proceeds; it is not frozen.
- **Marking convention:** each entry carries the brain structure, whether the brain's equation is **PINNED**
  (neuroscience fixes it) or **UNPINNED/CONTESTED** (we are inventing — an OUR-INVENTION-UNDER-TEST, not a
  replication), our organ (or ABSENT), a fidelity verdict, and the specific gap/deviation.

---

## 2b. AUDIT UPDATES (from integrated solver work — newest first)

- **2026-08-26 — MEMORY TIER / DEVIATION #2 advanced** (from `no_automatic_reliability_signal_reaches_the_source_oracle`,
  integrated EXCELLENT). A **DG pattern-separation + CA3 completion recollection gate** was built and re-verified:
  recollection now **self-certifies** (top-5% precision 0.938 vs counting 0.533 on the same items) and dual-process
  routing beats the counting floor CI-separated for the first time (0.365 vs UB 0.336), capturing ~half the oracle
  headroom; info-free twin loses, scramble collapses to 0.00. **Effect on this audit:** D1 (DG separation) moves
  from "SAME but orphan" toward a **proven role**; D2 (CA3 completion) gains the **self-certifying confidence** it
  lacked (for this use it no longer just "terminates in sign and buys nothing"). Answers board Q118 — a label-free
  selection signal IS CA3 completion confidence. **NOT closed:** deviation #3's *cortical-consolidated* read — this
  is the *episodic* recollection side. Lever for more = reading VOLUME (coverage), not a better gate. Organ recorded
  as the proven-ready deliberate landing (off the live path).

---

## 3. THE SCORECARD (from ORGAN_MAP §1 tally, 38 organs)

| fidelity of our op vs the brain's | count |
|---|---|
| **SAME — our equation IS the brain's** | **5 / 38** |
| RIGHT-OP, WRONG-METRIC | 13 / 38 |
| RIGHT-OP, WRONG-PLACE | 3 / 38 |
| WRONG-OP | 6 / 38 |
| **MISSING entirely** | **7 / 38** |
| UNSCORABLE (brain math UNPINNED) | 4 / 38 |

| how well the brain itself is pinned | count |
|---|---|
| an implementable equation exists in the literature | 12 / 38 |
| form pinned, key function/parameter UNPINNED | 12 / 38 |
| **core operation UNPINNED** | **14 / 38** |

Reachability: **~23 / 38 organs are on the live path (44 of 155 modules)** → ~54% of code unreachable.
Evidence: **10 / 38 organs' only evidence is a self-test PASS** (a construction proof, not a capability).

---

## 4. THE ARCHITECTURE, RECONCILED — every system, its organ, its fidelity

Grouped by the brain's functional tiers. `[P]` = brain equation PINNED, `[U]` = UNPINNED/contested (we invent).

### TIER 1 — PERCEPTION & LEXICAL FORM
- **Visual word form** (VWFA) `[U]` — `vwfa.py`/`char_*`. **RIGHT-OP-WRONG-METRIC:** 1-bit terminal quantiser; trigram order destroyed (position is a hashed atom, not a rotation).
- **Lexical category / POS** (post. temporal) `[U]` — `pos_tagger.py`+`perceptron.py`. **UNSCORABLE** (brain unpinned); own learned perceptron, HARD_PASS 0.906.
- **Dependency / argument-structure parse** (LIFG/pSTS) `[U]` — `arc_parser.py`. **UNSCORABLE**, and a real hole: head/deprel fields are **PLACEHOLDERS at inference** (only form+upos read). *This is the parser the p4 relcl brief is about.*

### TIER 2 — SEMANTIC MEMORY (meaning)
- **Amodal concept hub** (ATL) `[U]` (sub-fact: combination ≈ additive `[P]`) — `lexical_similarity.py`. **WRONG-OP:** unweighted feature overlap is the *inverse* of the brain privileging distinctive features; feature dict hand-built.
- **Per-occurrence pooling** (cortical, divisive normalisation `[P]`) — `grounding_acquisition_loop.py`. **WRONG-OP:** `sign(Σ±1)` where the brain does pooled divisive normalisation; amplifies a noise dim to full weight ~1 in 7.
- **Across-occurrence accumulation** (CLS) `[U]` (weight function) — `reading_grounding_loop.py::observe`. **RIGHT-OP-WRONG-PLACE:** a real graded accumulator, thrown away by `sign()` one line before use (`freeze_graded` default OFF).
- **Representation format** (cortex: graded, low-dim, sparse `[P]`) — 256-dim bipolar default. **WRONG-OP + under-capacity:** dense binary where the brain is graded/sparse; 2,377 concepts in 256 dims; **16× dims buys +0.0843 (largest measured single lever we own).**
- **Sensorimotor spokes** (modality→hub, rule `[U]`) — `grounded_similarity.py`/`sensorimotor_spoke.py`. **RIGHT-OP-WRONG-METRIC + mis-applied:** cosine can't separate synonym from sibling (apple/orange 0.952), capped 0.45 so it never decides; SUPPLY not learning.
- **Semantic comparison** (ATL recurrent settling `[U]`) — `canonicalize_fast`. **RIGHT-OP-WRONG-METRIC:** Hamming between two 256-bit majority patterns ("there is no cosine in the brain").
- **Semantic control** (IFG, multiplicative gain `[P]`; gain function `[U]`) — `context_vector_masked`; dedicated organ is `modern_hopfield_readout.py` (softmax sharpen/blend) + scattered sub-parts. **RIGHT-IDEA-WRONG-ALGEBRA:** context enters *additively*, not as multiplicative gain; the faithful multiplicative version scored WORSE — but that is an estimation-noise result **blocked behind the dense-code defect (B4)**, not evidence against the brain. **Dedicated semantic control is THIN** — a gap.

### TIER 3 — COMBINATORICS & STRUCTURE
- **Thematic role assignment** (Competition Model: cue validity `[P]`) — `thematic_role_labeler.py`. **RIGHT-OP-WRONG-METRIC:** raw counts are not cue-validity; cue *cost* absent; animacy-dominant; HARD_FAIL on real text.
- **Role–filler binding** (theta-gamma / conjunctive / tensor-product — **UNPINNED & 3-way CONTESTED** `[U]`) — `binding.py` (FHRR complex-multiply). **UNSCORABLE.** *This is our central operation and it has no settled brain equation to be faithful to — the deepest deviation in the substrate.*
- **Situation-model register / event indexing** (SEM, PE-segmented `[U]`) — `situation_model_accumulate.py`/`_multibank`, `situation_reader.py`. **RIGHT-OP-WRONG-PLACE:** has the register; **missing the prediction-error segmentation that decides WHEN to write.**
- **N400 coherence monitor** (running-model update magnitude; reference `[P]`, norm `[U]`) — **MISSING.** No module computes ‖Δsituation-model‖. A clean Phase-B target.
- **Construction-Integration** (Kintsch `[P]-ish`) — **MISSING.**

### TIER 4 — MEMORY SYSTEMS
- **DG pattern separation** `[U]` (level ~0.2% `[P]`) — `dg_pattern_separation.py`. **SAME** — but orphan (WIRED NO), untested.
- **CA3 completion** (auto-assoc; update rule = our Hopfield import `[U]`) — `cleanup_family.py`/`iterative_attractor.py`. **RIGHT-OP-WRONG-METRIC:** terminates in `sign()`; measured settling buys nothing.
- **Hippocampal one-shot write** (Marr `[P]`; allocation `[U]`) — `hippocampal_encoder.py`. **SAME (write op)** — index/allocation half missing; its 14/14 self-test is a **ceiling, not evidence** (exact cue solved by projection alone).
- **Consolidation / replay** (SWR; selection function `[U]`) — live: `reading_grounding_loop.py::checkpoint`; faithful: `continual.py` (**ISLANDED**). **WRONG-OP-CLASS at the live site:** single averaging op, ungated/un-interleaved/un-budgeted.
- **Working memory** (attractor vs synaptic — CONTESTED `[U]`) — `working_memory.py` **contains no WM (filename trap)**; `slot_attention_wm.py` = learned softmax head. **MISSING / RIGHT-OP-WRONG-METRIC.**
- **Sequence/order** (asymmetric Hebbian `[U]`) — `sequence_memory.py`. **SAME op-class.**
- **Successor representation** (`M=(I−γP)⁻¹` **FULLY PINNED** `[P]`) — `successor_representation.py`. **Faithfully implemented but MEASURED AND LOST** — 0/24 arms clear the bar; **degrades with scale** (its own ladder refutes "scale it up").
- **Cascade synapse** (multi-timescale, **FULLY PINNED** `[P]`) — **MISSING.** PARKED-BY-SCALE (advantage crossover N>~1e6; we run d≤4096, so a null here is the *published prediction*).
- **Synaptic tag & capture** (tag×PRP product `[P]`, but §10.1 says drop from pinned) — `excitability.py`. **RIGHT-OP-WRONG-METRIC:** single EWMA, not a two-factor product; WIRED NO.
- **Theta-gamma ordered buffer** (~7 slots `[P]`; encoding op `[U]`) — `situation_focus.py`. **RIGHT-OP-WRONG-METRIC:** capacity 4 vs ~7; order channel empty (HARD_FAIL).
- **Long-term semantic store** (no single brain analogue `[U]`) — `hd_fact_store.py`. **RIGHT-OP-WRONG-METRIC** ("the fourth prototype operator"); 65.7% of grounded facts are self-referential tautologies.

### TIER 5 — CONTROL, PREDICTION, METACOGNITION
- **Prediction / predictive coding** (residual precision-weighted `[P]`) — `predictive_coding.py`, `slot_attention_wm.py`. **RIGHT-OP-WRONG-METRIC:** residual computed on a `sign()`-quantised prediction (big & small flips indistinguishable); no precision term; WIRED NO; MIDDLE_BAND. *Encoder objective is also cloze, not forward-PC — see DEVIATIONS.*
- **Attention / information foraging** (MVT leave rule `[P]`) — `information_foraging.py`, `gap_driven_reader.py`, `corpus_registry.py`, `self_manager.py` (ACC/EVC halting), `situation_focus.py`. **The leave-rule exists but "WHAT TO READ NEXT" is effectively MISSING:** readable universe is a hard-coded 4-entry dict vs 36 corpora on disk; downgraded to MIDDLE_BAND (FROZEN beats FORAGE); the organ has never seen real text.
- **Metacognition / familiarity / abstention** (SDT criterion `[U]`) — `gap_detector.py` (**SAME — "the healthiest organ," AUC 1.000**, but its output has nowhere to go because foraging is unbuilt), plus a rich family: `refuse_gate.py`, `conformal.py`, `clarify_gate.py`, `completeness_checker.py`, `reachability_audit.py`, `quality_proxy.py`, `coref_distractor_suppress.py`. **Deviation:** no floor on refusal *correctness*; `state.refusals` written, counted, reloaded, then **never consulted**.
- **Reasoning over knowledge** (constraint satisfaction) — `reasoner.py` (**FAITHFUL, banked**), `multi_hop.py`, `gather_reason.py`, `glass_box_loop.py`, `kg_traversal.py`. Coverage-bound, not mechanism-bound.

### TIER 6 — AFFECT · GOALS · SOCIAL (BUILT, BUT LARGELY OUTSIDE THE FIDELITY AUDIT)
> These systems have real organs but are **NOT in the ORGAN_MAP's 38** — so their brain-fidelity has **never been
> scored.** That is itself a finding: the fidelity audit stops at the reading/memory pipeline.
- **Affect / valence / appraisal** (amygdala, vmPFC) — **richly built, UN-AUDITED:** `context_grounded_valence.py`, `consequence_learning_loop.py`, `wordnet_polarity_propagation.py`, `word_learning_tool.py`, `word_acquisition_loop.py`, `idiom_grounding.py`. *p3 (`propagate_along_the_relation`) lives here.*
- **Goals / reward / motivation** (BG, OFC) — **richly built:** `goal_typing.py`, `goal_owner_select.py`, `goal_achievement.py`, `goal_outcome_relation(_grounded).py`, `outcome_event_extraction.py`, `parse_goal_extraction.py`, `action_selection.py` (**BG Go/NoGo + TD, SAME op-class**), `successor_representation.py`, `self_manager.py` (DA vigor). *p1's convergent line (`organ_abstains`) lives here.*
- **Theory of mind / mentalizing** (TPJ, mPFC) — **ABSENT.** `state_of_mind.py` is explicitly *not* ToM (it's a coref tracker); the only false-belief (Sally-Anne, nested-HRR) work sits in `experiments/` and **was never promoted to `hdlab/`.** Clean gap + clean build target.

### TIER 7 — LEARNING & OUTPUT
- **Cortical learning rule** (lexical-semantic acquisition **UNPINNED, deliberately** `[U]`) — `learner/core.py`. **WRONG-OP:** MDL is model-selection, not a synaptic update rule; **the loop was never measured as a learner.**
- **Read→extract→consolidate loop** — PARTIAL (CLS shape right; the "what to extract from reading" step unsolved).
- **Language production / generation** (Levelt staged; lemma/lexeme split `[P]`) — **THIN, essentially ABSENT:** only `generation.py` (S-matrix + Langevin + cleanup). `substrate.py` production slots are EMPTY. The expressive side does not exist as an organ.

### COREFERENCE / ENTITY TRACKING — (spans tiers; the 07-30 "ABSENT" is corrected)
Heavily built: `coref.py`, `coreference_resolver.py`, `coref_distractor_suppress.py`, `bundle_focus_coref.py`,
`event_centrality_coref.py`, `scene_segment.py`, `state_of_mind.py`, `entity_slot_gate.py`, `slot_attention_wm.py`,
`situation_reader.py`, `event_bundle.py`. **RIGHT-OP-WRONG-METRIC:** invented arithmetic (`count + β·exp(−λΔ)`)
over a pinned *ordering*; **mentions are SUPPLIED (gold), so it does not transfer to raw prose**; margin over the
strong floor NOT CI-separated at n=57. *Competitive antecedent resolution among 2+ plausible referents remains the
real open case.*

### DISCOURSE / BRIDGING — (also corrected from "ABSENT")
Exists as *relation* inference (`situation_model_accumulate` CausalLinkRegister, `goal_outcome_relation*`,
`gather_reason`, `multi_hop`). **Explicit causal/elaborative bridging of the UNSTATED** (Graesser) is still
thin/UNPINNED and, structurally, "IS coreference in disguise → must reuse the coref organ."

---

## 5. THE LARGE-SCALE DEVIATIONS (we do it, not the brain's way)

1. **MOST OF THE ARCHITECTURE IS INVENTION, NOT REPLICATION** — 14/38 core operations UNPINNED, 4 UNSCORABLE,
   only 5 SAME. Including **the central binding operation (3-way contested)**. Honestly labelled, but it means
   "brain-faithful" is *undefined* for a large fraction of the substrate; those parts are bets, and should be
   named as bets.
2. **THE `sign()` QUANTISER EVERYWHERE** (34 sites / 12 modules) → the system becomes a prototype/averaging
   machine (`sign(shared+distinctive)=sign(shared)`). **The SUM it sits on is faithful (additive combination);
   only the terminal normaliser is not.** Graded flags exist **default-OFF** (`freeze_graded`, `graded_query`).
   *Caveat: "one-line fix" is half-right — removing it buys +0.0602 on 2AFC but ~null on open-vocab hit@1.*
3. **WE QUERY THE WRONG MEMORY** — retrieval answers out of the fast episodic (hippocampal) codes and **never
   reads the consolidated cortical store** (ablating consolidation moved the read-out by 0.0000). The standing
   "memorises but does not transfer" negative is the *signature of hippocampus-only retrieval* — a **MISSING
   cortical-read organ**, not a representational ceiling.
4. **DENSE where the brain is SPARSE + GRADED** (B4) — the largest measured single lever we own (16× dims).
5. **ONE STORE DOING TWO JOBS** — fast hippocampal binding and slow cortical consolidation are conflated; the
   faithful consolidation engine (`continual.py`) is **islanded**.
6. **ADDITIVE where control is MULTIPLICATIVE** (IFG gain, C3); **CLOZE where learning is FORWARD-PREDICTIVE**
   (encoder objective is bidirectional MLM, not prediction-error).
7. **~54% OF THE CODE IS UNREACHABLE** — built-but-unwired islands; several *faithful* organs (DG separation,
   cascade-adjacent, `continual.py`) sit unwired.

---

## 6. THE LARGE-SCALE GAPS (absent or thin systems)

- **7 organs MISSING outright**, the load-bearing ones being: the **cortical-read organ** (fixes deviation #3),
  the **N400 coherence monitor**, **Construction-Integration**, **corpus-selection foraging** ("what to read
  next"), the **cascade synapse** (parked-by-scale), and **discourse bridging of the unstated**.
- **Theory of Mind — ABSENT** (mechanism exists in `experiments/`, never promoted).
- **Dedicated semantic control — THIN** (one primitive + scattered sub-parts).
- **Language production — THIN** (one file; the expressive half of a brain is missing).
- **Scope gap in the audit itself:** affect, goals/reward, and metacognition are **built but never fidelity-scored**
  against the brain — likely deviations are hiding there, unmeasured.

---

## 7. THE MEANING RE-FRAME (2026-08-26 — updates the plan's foundational premise)

`LONG_TERM_PLAN.md` is built on "meaning is absent / you cannot route meaning that was never supplied / every
downstream fix is a better filing system for empty folders," and every phase is gated **supply-before-architecture**.

**This session weakened that premise.** On a **frequency-controlled (fair) metric**, the grounded meaning signal
**beats the strongest frequency floor CI-separated** (0.741 vs 0.558; info-free twins lose) — the old "counting
beats us" was measured on a metric that was secretly scoring frequency. **So meaning is present-but-unwired and
context-free, not empty.** The block has moved from "there is nothing to route" to "route it, and condition it on
context" (the p1 build). The plan's Phase-1 "supply more norms" lever is also downgraded (projecting the norms we
have covers the gap). **Reconcile the plan's §3 diagnosis with this before quoting it.**

---

## 8. LEVERAGE RANKING — and how it reshuffles the queue

The current problem queue (p1–p4) captures **only one** of the top brain-fidelity levers. The biggest
cross-cutting deviations are **not queued.** Candidates, ranked by leverage (blast radius × tractability):

1. **The `sign()` → graded path (deviation #2).** One cross-cutting change flips the whole substrate off
   "averaging machine." Graded flags already exist default-OFF; the work is proving graded wins downstream and
   flipping them. *Half-fix caveat noted — pair with B4.* **Not queued → package.**
2. **The missing cortical-read organ (deviation #3).** Could flip the programme's standing "memorises-not-transfers"
   negative by reading the store we already write. **Not queued → package.**
3. **Meaning wiring + context-conditioning — p1, ALREADY QUEUED.** The fair-metric win made it actionable.
4. **Dense → sparse+graded code (B4, deviation #4).** Largest measured single lever (16× dims = +0.0843).
   **Not queued → package (couples with #1).**
5. **The binding operator (E1) — our central op is unpinned/contested.** Deserves a deliberate "which brain
   binding theory, tested to converge" program rather than continued reliance on an unexamined default.
   **Not queued → package.**
6. **Fidelity-audit the affect / goals / metacognition systems** — built but never scored against the brain.
7. **Promote Theory of Mind** from `experiments/` into a real organ.
8. p2 (reliability signal), p3 (valence propagation), p4 (relcl parser) — the existing queue, unchanged.

**Recommendation:** the next problems to package are #1 (`sign→graded`) and #2 (cortical-read), because they are
cross-cutting, tractable (flags/organs partly exist), and outrank most of the current queue on blast radius. Do
NOT flood — package them as the current builds converge.

---

## 9. OPEN RECONCILIATION ITEMS (to close in later passes)
- Re-verify the ORGAN_MAP verdicts that are load-bearing here against HEAD (esp. B4's +0.0843, the `sign()`
  2AFC/hit@1 split, the retrieval-order 0.0000 ablation).
- Fold the affect/goals/metacognition organs into a fidelity table (currently un-scored).
- Reconcile `LONG_TERM_PLAN.md` §3 with the §7 re-frame in the plan file itself.
