# Research Drill: Brain-Grounded Continual Self-Improving Concept Encoder (2026-07-04)

**Author:** Research (Director role, this cycle)
**Trigger:** USER strategic question — the brain's concept encoder never stops changing (representational
drift is continuous); should/could our substrate encoder do the same, without breaking stored algebra
(bind/unbind/bundle) or stored atoms? Feeds R3 in the 5x rescue battery
(`notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md`).
**Method:** substrate-KB concept-query attempted first (blocked by a live WinError 1450 filesystem
resource fault — same class of issue already flagged in today's BACKUP doc; not re-litigated here,
proceeded on the substrate atoms already surfaced by the prior brain drill: `T2/complementary_learning_systems`,
`BIO/sparse_coding_neural`, `Self-supervised learning`). 4 parallel Sonnet lit-scan sub-agents (generic
math/neuro terms only, no substrate-specific framing off-platform), then Director synthesis.
**Calibration:** lit-scan penalty applied throughout — P estimates deflated 0.15-0.25 off naive reading;
novel-synthesis P capped at 0.50; hard-fail thresholds given for every claim used to drive a decision.

---

## HEADLINE

**Yes, and we are already 80% of the way there.** The R1 fixed-landmark objective already in flight is
structurally the SAME mechanism the production embedding-compatibility literature uses to let a model
keep improving while old stored vectors stay valid (Shen et al. 2020, "Backward-Compatible Representation
Learning," CVPR Oral — a frozen anchor/classifier pins the new embedding space's frame of reference to the
old one). The brain's version of "stable readout despite drift" is NOT a frozen readout that survives
forever for free — every clean biological/BCI example requires **periodic re-alignment**, not passive
immunity. So the answer to "can our encoder keep improving without breaking stored algebra" is: **yes, via
a frozen/periodically-refreshed landmark anchor — but budget for an explicit compatibility loss and a
re-alignment cadence, don't assume set-once-forever.** This is a **NEXT** item (small, cheap, sequenced
right after R1's base objective clears bar), not a NOW blocker and not a LATER moonshot.

---

## 1. Brain mechanisms — what each buys, what it costs

| Mechanism | What it buys | Cost / condition | Confidence |
|---|---|---|---|
| **Representational drift + "stable" readout** (piriform odor code, hippocampal CA1, posterior parietal cortex, V1) | Demonstrates biological systems tolerate continuous upstream change | The "stability" is **not free**. Piriform: linear decoder trained on day-1 activity falls to chance by ~day 32 (Schoonover, Ohashi, Axel & Fink, *Nature* 2021) — daily re-exposure slows drift, disuse re-accelerates it. CA1: only ~15-25% of place cells overlap across sessions weeks apart (Ziv et al. *Nat Neurosci* 2013), yet population decoding of position holds because the **decoder is re-fit**, not static. PPC: 60-80% of tuned neurons change tuning within 2-30 days (Driscoll et al. *Cell* 2017) yet task decoding survives (Rule/Loback *eLife* 2020) — again only under a decoder that keeps pace. | High for the drift measurements (flagship, replicated). Moderate-low for "stability is free" — every quantified failure case in this literature is exactly a **static decoder** hitting a drifted code. |
| **Stable low-dim manifold, drifting high-dim periphery** | The single best-supported compensation mechanism. Individual neurons turn over but low-dimensional population dynamics stay stable (Gallego, Perich, Miller et al. *Nat Neurosci* 2020, tracked 2 years, motor/premotor cortex); a BCI decoder recovers control after abrupt instability by **realigning to the intrinsic manifold** (Degenhart, Bishop, Yu et al. *Nat Biomed Eng* 2020) | Requires an explicit, periodic **realignment step** — this is the closest brain/BCI analog to "re-run a compatibility pass." Not passive. | Moderate-high, cross-lab replicated in the motor system; less direct evidence in piriform/hippocampus specifically. |
| **CLS two-speed (fast hippocampal / slow cortical) + sleep replay as offline self-distillation** | Lets a system absorb new specifics fast (hippocampus) without corrupting the generalizing slow model (cortex) every step; replay batches the consolidation into an offline phase (McClelland/McNaughton/O'Reilly 1995; Kumaran/Hassabis/McClelland 2016 update; formalized as generative replay by Shin et al. 2017, and as internally-generated "brain-inspired replay" by van de Ven, Siegelmann & Tolias 2020, *Nat Commun* — closest to a true no-external-label self-distillation loop). A 2026 preprint (Fountas et al., arXiv:2603.04688) explicitly casts consolidation as knowledge distillation where a noisy internal "teacher" trains a generalizing "student." | Needs TWO subsystems + a mechanism to synthesize/replay training signal; the synthesized signal has to be rich enough to be worth distilling from. **This is a genuinely un-tested computational analogy in real neurons** — confidence is theoretical/proposed, not measured. | Moderate for the CLS architecture itself (well-established framework); LOW/speculative for the literal "replay = distillation loss" claim — small-model demonstrations only. |
| **Neuromodulatory gating of plasticity** (ACh encoding-vs-retrieval switch, Hasselmo 1999 and lineage; theta-phase variant, Douchamps et al. 2013) | A cheap scalar signal that switches the whole circuit between "write" (encoding, plasticity high, recurrent retrieval suppressed) and "read" (retrieval/consolidation, recurrent circuit favored) — i.e., a plasticity ON/OFF gate keyed to internal state, not continuous free-running update. | Needs a reliable internal signal for "which mode am I in." No modern DL paper found that reimplements this as a literal learning-rate gate faithfully (conceptually parallel meta-learned/context-gated plasticity work exists but rarely cites this lineage). | Moderate for the biological mechanism; low for a ready-made computational template to lift directly. |
| **Sparse coding as interference control** | Reduces catastrophic interference essentially "for free" once the code is already sparse — Bricken et al. 2023 (ICLR), "Sparse Distributed Memory is a Continual Learner," shows a sparse-coding MLP continual-learns strongly **with zero replay**. Classical connectionist evidence (Chappell & Humphreys 1994; French 1991/1999) is consistent. | Nothing extra to buy — we are already heading to ~2% sparse for other reasons (goal 3). This mechanism comes along for free if the sparsifier itself is healthy. | High for the ML result; moderate-low for the causal in-vivo claim (indirect: sparse DG firing + pattern-separation behavior, not a direct drift-forgetting measurement). |

**Net read on Part 1:** the brain's "self-improving encoder" is real, but it is not a frozen-readout-survives-
forever story — it is a **periodically-realigned, offline-consolidated, gated** story. That reframes the
USER's question precisely: we are not choosing between "static encoder" and "encoder that drifts freely
forever," we are choosing a **re-alignment cadence** and a **gate for when learning is allowed to touch the
stored frame**.

---

## 2. ML analogs + anti-forgetting safeguards — cost vs. fixed-downstream-code preservation

| Method | Cost | Preserves a FIXED downstream code (old stored vectors stay valid)? |
|---|---|---|
| **EMA / mean-teacher self-distillation** (Tarvainen & Valpola 2017; BYOL, Grill et al. 2020; DINO, Caron et al. 2021) | Cheap — one extra forward pass + a parameter copy, no stored data. Prevents *collapse*, not forgetting per se; recent work (Shenfeld et al. 2026, arXiv:2601.19897; "Elastic Mean-Teacher Distillation") uses it explicitly to smooth the post-update "stability gap" in continual settings. | **No, not by itself.** It damps drift *rate*, it does not pin the embedding space to an old reference frame. Usually paired with something else. |
| **Experience replay / rehearsal** (Dark Experience Replay, Buzzega et al. 2020; iCaRL, Rebuffi et al. 2017) | Moderate — buffer storage scales with size; strongest general anti-forgetting result in the literature, beats regularization especially in hard (class-incremental) regimes. | **No, not directly.** It protects the model from forgetting old *tasks/classes*; it does not guarantee the embedding *geometry* stays compatible with a previously-built external index. Different problem than ours. |
| **Regularization (EWC, Kirkpatrick et al. 2017; Synaptic Intelligence, Zenke et al. 2017)** | Cheap compute, no buffer. But degrades sharply beyond ~10-15 sequential tasks (accumulated quadratic-penalty conflicts); protects **raw weight values**, not the function/representation the weights compute. | **No.** Explicitly the wrong tool for us — it doesn't touch the actual output-geometry compatibility question at all. |
| **Anchor-based / backward-compatible representation learning** (Shen, Xiong, Xia & Soatto 2020, CVPR Oral, "Towards Backward-Compatible Representation Learning" / Positive-Congruent Training; Forward-Compatible Training, Ramanujan et al. 2022; Hot-Refresh, arXiv:2201.09724; Query Drift Compensation, arXiv:2506.00037) | Moderate-heavy — requires a frozen anchor (their case: old classifier head), a compatibility-data subset, and an added influence-loss term during retraining. Empirical accuracy cost ~3% vs. unconstrained retraining (a real, quantified tax). | **YES — this is the only family that gives a direct guarantee.** Mechanism: freeze the old model's classifier/reference frame; force the NEW embedding network to still score correctly against that frozen frame via an added loss term. This geometrically pins the new space's frame of reference to the old one, so a database indexed under the old model stays retrievable without re-encoding. |

**This is the load-bearing citation for Part 3.** The anchor-based family is not a novel idea we would be
inventing — it is a solved production problem (face-recognition / retrieval-system embedding upgrades) with
a name, a known cost (~3% accuracy tax), and known failure conditions (below).

---

## 3. THE ANCHOR IDEA — assessed against our system (load-bearing question)

**Can a frozen/slow-moving landmark frame serve as the "stable readout"?** Yes — this is precisely what R1
is already doing (`experiments/exp_encoder_migration_step1b_v3_global_objective_landmark_rkd_concept_encoder_v1_core.py`):
anchor every concept to a fixed ~4-8k landmark frame each step. Structurally this **is** the Shen et al.
2020 mechanism (frozen anchor + compatibility loss against it), just currently pointed at fixing the
in-batch-coverage problem (R1's primary purpose) rather than explicitly at cross-version compatibility. The
two purposes are not in tension — the same mechanism buys both if we use it deliberately for both.

**Conditions that must hold** (read directly off the BCT literature's own stated failure modes, mapped onto
our system):

1. **The landmark set itself must not be drifting.** Shen's anchor is the *frozen old classifier*, never
   retrained. Ours must be an equivalently frozen reference — a fixed sample of teacher (BGE) embeddings
   works today (external, genuinely frozen); if we ever anchor to our OWN prior student checkpoint instead
   of the external teacher, that anchor is itself a moving target unless explicitly frozen and versioned.
   Recursive self-anchoring without freezing is exactly how drift compounds uncorrected.
2. **The comparison operator used at read-time must not change concurrently with the encoder.** Shen found
   that changing classifier *type* (e.g. softmax to cosine-margin) or adding nonlinearities destroyed
   compatibility even with the anchor loss in place. Our analog: cosine similarity is the operator used
   throughout retrieval/algebra; if that ever changes in the same cycle as an encoder retrain, the anchor
   trick will not save it.
3. **Dimensionality / block structure (N, K) must stay fixed.** No anchor loss rescues a change in N or K —
   that is a structural break, not a compatibility-loss problem, and is out of scope for this mechanism
   entirely.
4. **Compatibility is only guaranteed NEAR the anchors.** The influence loss constrains geometry local to
   the landmark set; concepts far from any landmark are less constrained (matches the Nystrom/landmark
   spectral-decay risk already flagged in the prior distillation-methods drill — teacher spectral decay, not
   L/N ratio, is the risk). This is a coverage question, not a correctness question — argues for periodically
   checking landmark coverage as the KB grows, not a fixed landmark set forever.
5. **There is a real accuracy tax (~3% empirically, Shen 2020).** A compatibility constraint trades off
   against how far the *next* training pass could otherwise improve. Given R1 is currently below its own
   pre-registered pass floor (DENSE 0.521 vs target ~0.8, MID scale), **adding a compatibility loss NOW,
   before the base objective clears bar, is premature** — it would tax an already-struggling number. Sequence
   it AFTER R1 (or its successor fix) reaches its target, not concurrently.

**What breaks it, restated as a checklist:** (a) changing N/K, (b) changing the retrieval comparison
operator at the same time as retraining, (c) anchoring to an unfrozen/recursive self-reference, (d) treating
"landmark set" as permanent rather than periodically re-verified for coverage as the KB grows, (e) adding
the compatibility constraint before the base objective itself is solved.

**Re-alignment cadence — the honest answer from the brain literature:** none of the clean biological/BCI
examples show a frozen anchor surviving indefinitely without intervention; they show **periodic
realignment** (Gallego/Degenhart: recalibrate the manifold-to-decoder mapping when instability is detected,
not continuously). The practical translation for us: treat every deliberate encoder retrain (new KB growth
milestone, new architecture tweak) as a realignment event with its own before/after compatibility check —
not a "set the landmark once at genesis and never touch it" assumption.

**A genuinely useful compositional finding:** this dovetails with the USER's runtime phase-diagram
regime-switching directive. If the substrate can occupy different operating regimes per-operation
(semantic-optimal for retrieval vs. composition-optimal for algebra), then a **regime transition is itself a
natural, controlled point to run the realignment/compatibility check** — the substrate-native analog of a
sleep/consolidation window, rather than something that must happen invisibly online. This relaxes the
requirement from "never let anything drift, ever" to "re-anchor deliberately at regime-transition
boundaries," which is both cheaper and better-grounded in how the brain actually does it (offline,
batched consolidation — not continuous online correction).

---

## 4. Gating conditions — does controlled continual EMA refinement sidestep R3's corpus wall?

**Short answer: yes, definitionally — but the literature does not show that EMA/online refinement is
*better* than periodic batch re-distillation at our current scale; it shows the wall is specific to
REMOVING the teacher, not to how you use it.**

- R3 (teacher-free self-distillation) needs ~60-250x more corpus density than we have (1.6 → ~100-400
  atoms/entity per the prior drill). That wall exists because pure self-supervised/EMA methods need to
  bootstrap semantics from the data itself with no external signal.
- A **controlled continual-refinement scheme that keeps BGE as the external teacher**, updating online/EMA
  rather than in one static batch pass, is NOT the same regime as R3 — it never removes the teacher, so it
  does not need to clear R3's density wall at all. This is close to definitional rather than a new empirical
  finding, so we do not need to deflate it as heavily as a genuinely novel claim, but flag it as a structural
  inference from the diagnosis, not a directly-cited number.
- The supporting literature is directional but thin: "Adapt Your Teacher" (Goswami et al. 2024, WACV) shows
  a **continuously-adapted external teacher signal outperforms a stale/frozen self-teacher under data
  scarcity** — consistent with "keep the teacher present" being the right sequencing call. "Online
  Distillation with Continual Learning for Cyclic Domain Shifts" (Roy et al. 2023) demonstrates the exact
  pattern (a slow-but-accurate teacher continuously supervising an incrementally-updated student) but does
  not quantify a data-density benefit over static batch distillation. **No paper directly sweeps
  per-instance density for EMA-with-teacher-present vs. static-batch-with-teacher-present** — this specific
  comparison is unaddressed in the literature; treat the "online is meaningfully better than periodic batch
  at our scale" claim as **speculative, P_deflated 0.25**, not established.

**Sequencing — doable today vs. waits:**

| Doable now (teacher present, current corpus) | Waits (needs corpus growth) |
|---|---|
| R1 landmark-distillation itself (already running) | R3/R4: true self-teacher, EMA over the substrate's OWN relational/gloss experience — gated at the 60-250x density wall, unchanged by this drill |
| Periodic *batch* re-distillation as the KB grows (re-run R1-style training on a cadence, e.g. tied to KB-growth milestones or regime-transition points) | An always-on *online/incremental* EMA refinement loop layered on top of BGE distillation — the literature does not show this buys enough over periodic batch re-runs to justify its added engineering complexity at current scale |
| A BCT-style compatibility-loss add-on to each periodic re-distillation pass, once R1's base objective clears bar (Part 3) | — |

**Net:** the corpus gate is real and unaffected by choosing EMA vs. batch cadence — it only matters if/when
we drop BGE (R3/R4). Until then, "continual improvement" for us means **periodic, deliberate, compatibility-
checked batch re-distillation**, not a continuously-updating online student. This is cheaper, better matches
the brain's actual offline-consolidation pattern (not continuous online drift), and avoids taking on EMA's
implementation cost for a benefit the literature does not currently support at our scale.

---

## Cheap decisive test (pre-registered)

**We already have the data for this, for free — no new training required.**

The R1 MID run recorded a dense-spearman trajectory across checkpoints (300-step intervals) as part of its
own quick-eval logging, and the backup doc records the peak-then-degrade signature (0.740@step1200 →
0.716@step1500 → 0.521@step1800 full-eval). This is, structurally, the SAME measurement class as the
piriform "day 1 vs day 32" drift-decoding-cliff: does a fixed reference (an earlier checkpoint, standing in
for "already-stored atoms") stay retrievable against a later, improved checkpoint ("the current encoder")?

**Test:** using the ALREADY-SAVED R1 checkpoints (e.g. step1200 as `v_old` / stand-in for stored atoms, and
the final/step1800 checkpoint as `v_new` / current encoder), encode a held concept set with `v_old` and
freeze those vectors (the pretend index). Encode QUERIES for the same concepts with `v_new`. Measure
cross-checkpoint retrieval accuracy / cosine-spearman against those frozen `v_old` vectors, and compare to
same-checkpoint (`v_new`-vs-`v_new`) retrieval on an identical held set. Cost: one extra eval pass reusing
existing checkpoints — no new training, no GPU time.

**Also run on BOTH the DENSE and BLOCK_K128 codes.** Hard-argmax discretization can amplify small
continuous-geometry drift into large discrete-winner flips (a block's chosen active dimension can flip
between checkpoints even when the underlying dense score barely moved) — this is the same
argmax-readout-degeneracy theme the phase-diagram program already found causes phantom effects elsewhere
(mechanism-cross-term family demoted 4/4 as argmax-degenerate artifacts). If BLOCK shows materially worse
cross-checkpoint compatibility than DENSE, that is itself informative: discretization is a compatibility risk
multiplier, independent of the semantic-quality question R1 is already solving.

### Falsifiable predictions

- **HARD-PASS (defer compatibility work to NEXT, not urgent):** cross-checkpoint retrieval stays at or above
  ~90% of same-checkpoint retrieval accuracy/spearman across the tested checkpoint range, on BOTH DENSE and
  BLOCK codes. Drift within a single training run is mild; a BCT-style compatibility loss is a NEXT-priority
  refinement, not a blocker.
- **HARD-FAIL (pull compatibility work forward to NOW, before any periodic re-training cadence is adopted):**
  cross-checkpoint retrieval drops below ~50% of same-checkpoint retrieval on either code — i.e., the
  piriform chance-level-by-day-32 signature reproduces WITHIN a single ~1800-step training run. If this
  fires, do not adopt any periodic re-distillation cadence without a compatibility loss from the first cycle.
- **MIDDLE BAND (50-90%):** proceeds as the NEXT-priority item as scoped in Part 3/5 — real but not urgent;
  matches the default recommendation below.

---

## 5. Recommendation: NOW / NEXT / LATER

- **NOW: nothing new to build.** R1 (running) already IS the mechanism this drill validates — a fixed
  landmark/anchor frame supervising the map globally is structurally identical to the production
  backward-compatible-embedding technique. No architecture change is required to act on this drill; the
  finding is confirmatory of the current direction, not a redirect.
- **NEXT (small, cheap, sequenced right after R1's DENSE-recovery number lands):**
  1. Run the **cheap decisive test above** (free — reuses existing checkpoints) to get a direct read on
     within-run drift severity before committing to a cadence.
  2. Once R1 (or its successor fix) clears its base-objective target (~0.8 DENSE), add an explicit
     **compatibility-loss smoke test**: freeze a held set of atoms encoded under the CURRENT (R1) encoder
     version, train a next-version candidate WITH an added BCT-style compatibility term against that frozen
     set, and measure cross-version retrieval accuracy vs. a candidate trained WITHOUT the term. This is the
     single smallest concrete first experiment — reuses the R1 training loop, adds one loss term and one
     eval, no new infrastructure.
  3. Treat every future deliberate encoder retrain as a scheduled "realignment event" (ideally aligned to a
     regime-transition boundary per the phase-diagram directive) with a before/after compatibility check,
     rather than assuming a landmark set set once at genesis survives indefinitely.
- **LATER (gated, unchanged by this drill):** R3/R4 — wean off the external BGE teacher entirely once the
  KB clears the 60-250x density milestone. When that happens, apply the SAME anchor discipline recursively:
  the self-teacher's own periodic "landmark snapshot" becomes the frozen reference for the next self-
  distillation generation — this is the encoder-level analog of CLS's requirement that *something* stays
  slow and stable even when both teacher and student are internal.

**Top failure mode to guard:** representational-drift-breaks-stored-traces — a future retrain (new
landmark set, architecture tweak, or KB-growth-triggered re-run) silently shifts the student's mapping
enough that OLD stored HD vectors no longer sit correctly relative to NEW queries/algebra, even though the
encoder's own semantic quality improved in isolation. This is exactly Shen et al.'s baseline failure case
(new model good on its own metric, bad against the old gallery) and exactly the piriform/motor-cortex
drift-cliff under a static decoder. Guard: never promote a new encoder version into production without
either (a) full re-encoding of all stored atoms, or (b) a passed compatibility check (per the falsifiable
predictions above) run BEFORE promotion.

---

## Cross-thread synthesis

- **Extends, does not overturn, the prior brain drill** (`research_drill_brain_grounded_concept_encoding_how_does_brain_do_it_2026-07-04.md`): that drill established the brain has no external teacher and forms geometry before sparsifying (D1/R2); this drill adds the missing piece — HOW the brain's internally-refining representation stays USABLE downstream despite continuously changing (periodic realignment, not passive stability), which is the direct answer to the NEW question asked here.
- **Confirms, rather than adds risk to, the R1 fix in flight**: R1's fixed-landmark objective (`notes/encoder_rescue_plan_converged_diagnosis_2026-07-04.md`) is independently validated by an entirely different literature (production embedding-compatibility engineering, not neuroscience) — two disparate fields converge on the same mechanism (frozen-anchor supervision), which raises confidence in R1's structural soundness beyond what either literature alone would support.
- **Reinforces D1-now/R3-later sequencing** from the teacher-free-viability 2x drill (`research_drill_teacher_free_semantic_bootstrapping_from_sparse_kb_2026-07-04.md`): this drill independently arrives at the same NOW/LATER split via a different angle (data-density requirements of EMA self-distillation specifically), and clarifies that the corpus wall is intrinsic to dropping the teacher, not to online-vs-batch cadence choices made while the teacher is still present.
- **Ties into the phase-diagram program's argmax-readout-degeneracy finding**: the same discretization brittleness that caused the mechanism-cross-term family to be demoted 4/4 as measurement artifacts is flagged here as a plausible compatibility-risk multiplier for the BLOCK sparse code specifically — worth testing empirically (part of the cheap decisive test) rather than assuming.
- **Composes with the runtime phase-diagram regime-switching directive**: regime transitions are proposed here as the natural, controlled point to run realignment/compatibility checks — turning an otherwise-continuous drift-management burden into a discrete, scheduled event, matching the brain's offline-consolidation pattern rather than requiring continuous online correction.

---

## Substrate-product implications

Framed as capability, not publication: a concept encoder that can keep improving over time WITHOUT forcing
a costly full re-index of everything already stored is a genuine differentiator against conventional
embedding-based systems, where "upgrade the embedding model" conventionally means "re-encode the entire
database" (an expensive, often-skipped maintenance burden in production retrieval/search systems — exactly
the problem the backward-compatible-training literature exists to solve). If our substrate solves this
natively via the landmark-anchor mechanism plus a fixed comparison operator and stable algebra, that is a
marketable, structural property: **"the encoder gets better; your stored knowledge does not need to be
rebuilt."** This composes directly with the self-improvement-portal / core-mathematics strategic vision and
gives the cortex-layer roadmap item a concrete, already-in-hand mechanism (periodic realignment at
regime-transition boundaries) rather than an open research question.

---

## Citations (verified count)

**~45 distinct works surfaced** across 4 parallel Sonnet lit-scan sub-agents (each fetched/read web sources
directly; citations were NOT independently re-fetched by the synthesizing agent — apply the standing
lit-scan calibration discipline). Load-bearing citations used to drive the Part 3/5 recommendation:
Schoonover/Ohashi/Axel/Fink *Nature* 2021 (piriform drift); Gallego/Perich/Miller et al. *Nat Neurosci* 2020
+ Degenhart/Bishop/Yu et al. *Nat Biomed Eng* 2020 (stable-manifold + realignment, the strongest brain/BCI
mechanism); McClelland/McNaughton/O'Reilly 1995 + Kumaran/Hassabis/McClelland 2016 (CLS); Shen/Xiong/Xia/
Soatto 2020 CVPR (Backward-Compatible Representation Learning — THE load-bearing ML citation for Part 3);
Bricken et al. 2023 ICLR (sparse coding as free interference control); Goswami et al. 2024 WACV + Roy et al.
2023 (teacher-present continual/online distillation, Part 4). Full per-topic citation lists are embedded in
Parts 1-4 above (author/year/venue given inline for every claim).

---

## Intuitive summary (USER universal rule)

Short version: the brain never freezes its idea of what a concept means — it keeps refining it your whole
life. But here is the part that matters for us: the brain's "stable memory despite a changing map" trick is
not magic and it is not free. Every clean example (smell recognition, place memory, motor skill) shows the
same pattern: the detailed neural pattern keeps drifting, but something downstream periodically RE-ALIGNS
itself to the new pattern — usually during an offline period like sleep. A memory that is never re-aligned
against a drifting map does go stale; that has been measured directly (smell recognition drops to chance
after about a month if you stop checking in on it).

That reframes our question in a useful way. We are not choosing between "encoder frozen forever" and
"encoder that drifts and breaks everything" — we are choosing how often to deliberately re-anchor. And it
turns out the fix already in flight for the encoder (anchoring every concept to a fixed reference frame so
the training signal reaches the whole map, not just nearby neighbors) is, structurally, the exact same trick
a completely different field independently invented to solve "how do I upgrade my search engine's embedding
model without having to re-index everything" — freeze an old reference point, force the new model to stay
consistent with it. Two unrelated fields landing on the same mechanism is a good sign it is the right one.

So the practical answer: we do not need to build anything new right now. Once the current fix lands its
target number, the next small step is to add one extra loss term that keeps new training passes honest
against a frozen sample of what is already stored, and to treat every future deliberate encoder update as a
scheduled "re-anchor" moment rather than something we hope just works. The corpus-size wall that blocks
fully weaning off the outside teacher is unaffected by any of this — that wall is about removing the
teacher entirely, which is a separate, later decision, gated on the substrate's own knowledge base growing
much richer than it is today. Position: this is good, low-risk, confirmatory news — the direction already
chosen is validated from two independent angles, the next step is cheap and already scoped, and the
one thing to actively guard against (a future retrain silently invalidating old stored knowledge) now has a
named test with a hard-fail threshold, so it cannot happen silently.
