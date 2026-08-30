# LEARNER-ON ROADMAP — the clear path to turning learning-from-reading ON, safely

> **What this is.** The single reference for the North Star the owner set on 2026-08-30: get the
> substrate to *learn from what it reads* — safely — by building ONE connected chain, not scattered
> threads. Every solver and session should build toward the same chain. It is written in plain
> language first, with the evidence (problem slugs + numbers) underneath each claim so it can be
> audited, not taken on faith.
>
> **Companion:** memory `[[learner-on-organizing-frame]]`; the STATUS `POSITION` organizing-frame
> block; `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (per-organ fidelity). This doc is the *plan*; those are
> the *frame* and the *map*.

---

## THE NORTH STAR (plain language)

We want the reader to **get better by reading** — the way a person does — instead of being frozen at
whatever it was shipped with. That is "the learner." We have PROVEN the learner works and we have even
found a SAFE way to let it grow. We are deliberately keeping it **OFF** for one honest reason: the pile
of facts it would grow from is still too messy, and growing on a messy pile multiplies the mess. So
"turn the learner on" really means **"first make the substrate read and keep CLEAN knowledge."**

**The chain, in one line:**

```
  narrative extraction  →  a knowledge base  →  CONSOLIDATION / CLEANUP  →  a clean foundation  →  SAFE GROWTH (learner ON)
        (link 1)              (link 2)                (link 3)                   (link 4)                (link 5)
```

The owner's key insight (which strategy had under-weighted): **the reasoning/narrative work and the
learner-foundation work are the SAME chain.** The situation model the reader builds (who did what, to
whom, where, when, why, who-believes-what) *is* a small structured knowledge base. So making the reader
extract narrative accurately IS cleaning the foundation. They are not competing priorities.

---

## THE CHAIN, LINK BY LINK — what is PROVEN, what is the residual

### Link 5 — SAFE GROWTH (the learner itself): PROVEN, and a SAFE mechanism is already validated.
Plain: *learning from reading works, and we know a safe way to switch it on — we just haven't wired
that safe switch in yet.*

- **Worth continuing at all — YES, decisively** (`does_learning_from_reading_deserve_to_continue`,
  SOLVED). The learned distributional arm clears the strongest floors CI-separated by 15–40× on
  SimLex/SimVerb/WordSim, and the curve is **still climbing at the corpus ceiling** — the route is
  corpus-limited, not exhausted.
- **The brain-faithful lever is CONTEXT SHAPE, not the update rule**
  (`optimize_and_validate_the_learner_before_it_grows_the_foundation`, "PARTIAL" but decisive). A
  dependency-typed (grammatical-relation) distributional learner beats the ±2-window baseline
  CI-separated on SimLex (+0.060) and SimVerb (+0.034), ~2.5× more data-efficient. (The update-rule
  question is settled by argument: SGNS ≡ shifted-PPMI, CBOW ≡ counting — online ≡ batch here.)
- **It is SAFE to grow — behind the right mechanism.** Growing meaning by reading 5M→15M tokens lifts
  downstream LitBank who-did-what **0.071→0.149 (+0.078 CI-sep)**, and it is *real learned structure*
  (info-free growth controls fall below baseline). A NAIVE overwrite corrupts **~25.6%** of
  previously-correct answers — but that was a **MISSING-MECHANISM artifact, not a ceiling**: a
  CLS-faithful **keep-both-stores ensemble** cuts corruption to **7.85% (−0.177 vs naive)** while
  keeping 71% of the gain; a rate-limited gradual blend (α=0.25) keeps 84% of the gain at 18.5%
  corruption. Accuracy saturates while corruption climbs monotonically toward the naive value — the
  textbook CLS signature (slow, replay-preserving integration beats wholesale overwrite).
- **⚠️ OWED LANDING (Q111 candidate — VERIFY BEFORE CLAIMING):** that SOLVED landed **NO hdlab/
  change** — the CLS keep-both-stores growth mechanism (default-OFF) is *described* for the strategy
  session to land. This is a concrete owed strategy landing. **Before treating it as owed, CHECK hdlab
  for an existing growth-ensemble / keep-both-stores module** (the duplicate-landing lesson). If
  absent, this is the cleanest single step that moves "safe switch validated" → "safe switch wired,
  default-off."

### Link 4 — CLEAN FOUNDATION (extraction quality): THE REAL UPSTREAM BOTTLENECK.
Plain: *the messy pile is the actual blocker, and it is where the current top-priority work aims.*

- The foundation the learner would grow on is still too noisy (most auto-extracted facts are low-value).
  Two independent lower-links point their residual squarely HERE:
  - the learner is "corpus-limited, still climbing" — it wants **more and cleaner** text, not a better
    rule;
  - the consolidation read's residual is "the **CONTENT/CODE** is the residual wall" (see Link 3), i.e.
    what got written, not how it is read.
- **This is exactly what the OWNER-PRIORITY p1 problem targets:**
  `the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text` — migrate the reader eval
  off 200-year-old McGuffey onto modern annotated text (on the shelf: LitBank CoNLL, UD-EWT,
  RACE/MCScript/OneStop) and re-validate the organs. Cleaner, modern extraction targets = a cleaner
  foundation. **Corpus, not mechanism.**

### Link 3 — CONSOLIDATION / CLEANUP: the read-path defect is REAL; the residual is CONTENT, not the read metric.
Plain: *the "clean-up" organ runs but its cleaned output is currently ignored; fixing the plumbing is
proven-not-enough — the deeper issue is the quality of what gets stored.*

- The organ RUNS (episodic→semantic pass; `cortical_recall` / `cleanup_family` / `schema_exemplar_bayes`)
  but the cleaned cortical store was **written-but-never-read** — the live read-out hit the EPISODIC store.
- **The read-path defect is genuinely real** (`the_consolidated_cortical_store_is_written_but_never_read`,
  PARTIAL): the brain-faithful cortical read BEATS the live episodic path CI-separated (0.484 vs 0.064) —
  it beats the *wrong memory* — and the consolidation ablation bites. **BUT** it does **not** clear the
  first-order counting floor, and on the decisive unseen-co-occurrence regime it sits at/below its
  info-free twin. Verdict in the solver's own words: *"the consolidated CONTENT/CODE is the residual
  wall."*
- **⛔ ANTI-RE-TREAD (verified 2026-08-30):** the tempting next step — "wire the built
  `distributional_meaning_channel` (distilled substitutability) into the cortical read and measure" —
  is a **re-tread of an integrated REFUTATION.** `teach_the_self_built_space_instead_of_concatenating_it`
  (owner-DONE, REFUTED = full PASS) proved that teaching the self-built space with the grounded/distilled
  direction does NOT rescue unseen-context **retrieval** — it HURTS, monotonically, across 3 mechanisms
  at full power. Substitutability ≠ retrieval; **no number crosses tasks.** `cortical_recall.py`
  correctly does not consult it, and `distributional_meaning_channel` is already wired where it belongs
  (`meaning_fusion` + `reading_grounding_loop` — the meaning read-out). **Do NOT package a
  "wire the distilled space into the cortical read" problem.**
- **What the consolidation residual actually is:** the CONTENT that gets consolidated (Link 4) and the
  scale of reading, not the read-out metric. That is why the critical path routes THROUGH Link 4, not
  through a new consolidation-read cell.

### Links 1–2 — NARRATIVE EXTRACTION → KNOWLEDGE BASE: heavily built; residual is coref.
Plain: *the reader already extracts the who/what/where/when/why reasonably; its biggest remaining error
is figuring out which "she/he/they" points at whom.*

- All 5 Zwaan situation-model dimensions have organs (SPACE, TIME, CAUSATION, ENTITIES+state, GOALS/ToM).
- The **assembly milestone** (STRONG, integrated): the live reader beats its positional self on
  who-did-what end-to-end (0.551→0.798), the dominant lever being quotative inversion ("said Fred"→Fred
  = agent, +0.253, now landed in the shared router).
- **Residual = coreference on anti-typical/topic-shift cases** — measured (twice, convergently) to be a
  **discourse-focus / syntactic-binder** problem, NOT a world-knowledge/KB problem (a commonsense KB is
  DEAD there, ~2–3%). This is packaged as **p3 `the_coref_residual_needs_a_discourse_focus_stack`** (a
  Grosz-Sidner focus stack).

---

## THE CRITICAL PATH TO LEARNER-ON (in order)

1. **Clean the extraction foundation (Link 4 — the real bottleneck).** Ship p1 corpus-migration
   (McGuffey→modern) and keep improving narrative-extraction accuracy (coref residual, p3). Every
   accuracy gain here is a cleaner foundation. *This is the top priority and it is already in the queue.*
2. **Land the safe-growth switch (Link 5 — owed, default-off).** Verify no existing hdlab keep-both-stores
   growth module; if absent, land the CLS keep-both-stores growth mechanism as a **default-OFF** hdlab
   diff, witnessed. This makes the validated safe switch real without turning it on.
3. **Prove the foundation is clean ENOUGH, then flip growth ON behind the safety gate.** Only once the
   foundation is measurably clean do we run the safety-gate test live and enable growth — never on hope.

Note the ordering: **we do NOT chase a better learner or a better consolidation read next.** Both are
proven; both are bottlenecked upstream. The leverage is in Link 4.

---

## THE SAFETY GATE (the "responsible" pillar — non-negotiable)

Learner growth stays **OFF** until BOTH:
- **the foundation is proven CLEAN** (extraction quality measured, not assumed), AND
- **growth is proven SAFE on the day** via the validated mechanism: **keep-both-stores** (hippocampal +
  cortical ensemble) or rate-limited gradual integration, with a **regression-checked rollback** and an
  **info-free growth control** that must NOT help (ideally hurt).

Flip on **EVIDENCE, never hope.** The corruption rate (with CI) is reported every time; a naive-overwrite
growth is barred (it is the 25.6%-corruption path).

---

## HOW THE CURRENT QUEUE MAPS TO THE CHAIN

| Queue item | Priority | Chain link it serves |
|---|---|---|
| `the_reader_eval_is_scored_on_200_year_old_mcguffey_migrate_to_modern_text` | **p1 (owner)** | Link 4 — clean foundation (modern extraction targets) |
| `the_coref_residual_needs_a_discourse_focus_stack` | p3 | Links 1–2 — extraction accuracy (coref residual) |
| `the_reader_cannot_answer_a_question_over_its_situation_model` | p5 | Links 1–2 — the comprehension→reasoning capstone (proves the KB is queryable) |
| 3 WIP awaiting owner review (belief-timeline p4, patient-tendency p7, causal-network p8) | — | Links 1–2 — extend the situation-model organs |

Every current item feeds Links 1–4. The safe-growth landing (Link 5, step 2) is strategy's own owed work,
not a solver brief.

---

## WHAT NOT TO DO (anti-re-tread ledger)

- **Do NOT** wire the distilled `distributional_meaning_channel` into the cortical/consolidation read —
  refuted by `teach_the_self_built_space` (substitutability ≠ retrieval).
- **Do NOT** hand a solver a "make the consolidation read beat counting" brief framed as a read-metric
  problem — the residual is CONTENT/scale (Link 4), and the read-metric route is heavily worked with
  integrated negatives.
- **Do NOT** turn growth on with a naive overwrite — it corrupts ~25.6% of correct answers; the
  keep-both-stores mechanism is the only sanctioned path.
- **Do NOT** treat "the learner is off" as a learner problem — it is a foundation-quality gate.

---

## HONEST OPEN QUESTIONS / RISKS

- **How do we MEASURE "clean enough"?** We do not yet have a single agreed foundation-cleanliness metric
  that says "the foundation is now clean enough to grow on." Defining that gate is itself a genuine,
  un-worked piece of work (candidate future problem — verify it is not already covered before packaging).
- **The safe-growth landing is a THIN, foundational change** — land it default-off and carefully; the
  keep-both-stores gain is real but the mechanism touches the store.
- **Modern-corpus annotation is imperfect** — LitBank is 19c (newer + annotated, not truly 21c); role gold
  on truly-modern narrative is scarcer, so p1 picks per available gold. This narrows but does not fully
  retire the corpus-age confound; quantify the per-organ delta.

---

## TLDR / QUESTIONS / NEXT STEPS

**TLDR (plain English):** We want the reader to get smarter by reading, and we have proven it can — we
even found a safe way to switch it on without it forgetting things (keep the old memory alongside the new
one, which cuts the "forgetting" from about a quarter of answers down to under a tenth). We are keeping it
off on purpose because the facts it would learn from are still too messy. So the real job right now is to
clean up what the reader extracts — which is exactly what our current top-priority work (moving off the
200-year-old text onto modern text, and fixing which "she/he" points at whom) already does. Then we wire
in the safe switch (off by default), prove the facts are clean enough, and only then turn learning on. One
thing I checked and want to flag: an "obvious next step" I had written down — plugging our new meaning
tool into the memory-cleanup organ — turns out to have already been tested and shown NOT to work, so we
will not spend effort on it.

**QUESTIONS:** None — the direction and priorities are clear from the owner's 08-30 discussion; this
roadmap records them.

**NEXT STEPS:**
1. Keep the queue aimed at Link 4 (p1 corpus-migration is top; p3 coref residual next).
2. Verify hdlab has no existing keep-both-stores growth module; if absent, land the CLS safe-growth
   mechanism default-OFF (strategy's owed Q111 landing).
3. Later, define a foundation-cleanliness measurement — the gate that decides when growth may flip on.
