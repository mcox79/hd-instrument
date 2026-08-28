# FORWARD WORK — reading + grounding, integrated the way the brain integrates
### Submission-ready package for `aimed_reading_is_built_and_the_reader_never_calls_it`
2026-08-24. Accompanies the SOLVED.md closure. Rewritten after the meaning-integration investigation
(L1-L3) RESOLVED how this substrate should produce meaning. Supersedes the earlier distillation-based
draft (that mechanism was refuted — see below).

---

## 1. What we now KNOW (the resolved mechanism)

**Meaning in this substrate is produced by COMPLEMENTARY INTEGRATION of two spokes:**
- the **reading spoke** — a distributional embedding (PPMI+SVD) the reader builds from co-occurrence.
  On its own, once it has read ~10k sentences, it scores WordSim-353 Spearman **~0.31-0.36**. Reading
  alone makes real word-meaning.
- the **grounded spoke** — the sensorimotor hub (`hdlab/grounded_similarity.py`, 12-dim Lancaster +
  Brysbaert, ~39,707 words). On its own **~0.38-0.41**.
- **integrated by equal-weight z-score fusion** (`z(cos_reading) + z(cos_grounded)`): **~0.45-0.49**,
  which **exceeds BOTH spokes** in all three readers tested. The gain over the stronger spoke is
  CI-separated in 2/3; the info-free (shuffled-grounding) twin loses CI-separated in 3/3.

This is exactly the **hub-and-spoke** prediction (Patterson; Lambon Ralph; Rogers): the semantic hub
integrates modality spokes complementarily, so the integrated representation exceeds any single spoke.

**What was the bug (the earlier "distillation" claim, RETRACTED):** the shipped operator trained the
reading channel to *mimic* the grounded channel (X = phi[a]*phi[b], target = grounded cosine). That
is **substitution** — it discards the reading spoke's own relatedness signal — and it scored *below
raw reading everywhere* (down to −0.24). The smoke that once made distillation look good was a
low-data artifact (the reading spoke had not yet formed). The full run reversed it; integration, not
distillation, is the mechanism.

**Why the SIMPLE operator is the right one (three convergent results):**
- L1: complementary fusion beats both spokes; substitution was the bug. (CI-separated, twin loses.)
- L2: a concreteness-GATED fusion does NOT beat uniform (gating adds nothing over equal-weight).
- L3: a LEARNED hub (CCA/PCA joint) does NOT beat fixed equal-weight fusion (CCA sometimes worse —
  it chases the SHARED subspace and discards the COMPLEMENTARY information that fusion preserves).

Equal-weight complementary fusion is the sufficient, brain-faithful meaning operator at this scale.

---

## 2. PINNED vs OURS
- **PINNED (structure):** meaning = a hub integrating multiple modality spokes; integrated >= either
  spoke (hub-and-spoke). Confirmed by the data.
- **PINNED (learning principle):** the reading spoke is ordinary distributional semantics (Harris;
  Landauer & Dumais) — co-occurrence over enough text yields relatedness.
- **OURS-UNDER-TEST:** that equal-weight z-fusion is the faithful software form of hub integration. It
  is validated as *sufficient* (nothing beat it), not proven *optimal*. A richer teacher or a
  downstream task could still move it.

---

## 3. Forward levers, ordered by what raises meaning most

These RAISE PERFORMANCE; they do not change the resolved mechanism.

### LEVER 1 (primary) — a stronger grounded spoke: CSKG as the teacher  [L4 DONE]
**RESULT (2026-08-24, `exp_reader_meaning_teacher_optimization_v1`, landed-VET CONFIRMED: numbers
clean, recompute exact, no leak, twin loses; synergy framing REFUTED by the cell's own arms):** a CSKG word
embedding (4.63M English edges, PPMI+SVD k=200, 100% benchmark coverage) lifts WordSim from ~0.47
(norm-hub fusion) to **~0.65** in all three readers (CI-separated +0.16-0.20), SimLex ~0.15 -> ~0.30;
twin loses, positive control passes, tuning cross-validated (no leak). **So the 12-dim hub WAS the
bottleneck on the absolute number — optimization ceiling ~0.66 WordSim / ~0.40 SimLex.**
- **CAVEAT (load-bearing):** CSKG **replaces** rather than **complements**. Cross-validated tuning
  zeros the norm-hub weight and keeps reading low; `FUSION_CSKG ~= CSKG alone`, and `FUSION_CSKG >
  FUSION_3WAY` (adding the thin hub dilutes). CSKG is a relatedness/linguistic graph scored on a
  relatedness benchmark (0.65 is the known ConceptNet regime) — arguably a better *distributional*
  channel, not a distinct *sensorimotor* modality. Reading becomes ~redundant given CSKG (a static
  rich foundation subsumes the runtime reading channel). **This is a foundation-quality win, NOT a
  demonstration of multi-modal spoke synergy — the genuine hub-and-spoke result stays Section 1 (L1).**
- **Genuine frontier (Lever 1b):** test a truly SENSORIMOTOR richer teacher (full Lancaster norms) —
  does a richer PERCEPTUAL spoke ADD on top of CSKG? That, not the CSKG lift, tests hub-and-spoke
  synergy without the relatedness-overlap confound.

### LEVER 2 — wire the two spokes into the LIVE reader  [the PRIORITY-2 problem]
Today the reading spoke and the grounded spoke are SEPARATE at the live path
(`the_live_meaning_organ_has_no_distributional_channel_to_be_taught_by`).
- **Build:** a separable co-occurrence store accumulated during `substrate.read()` (the reading
  spoke), fused with `grounded_similarity` at query time by equal-weight z-fusion.
- **Now well-motivated:** the store's raw channel IS meaning (0.34); fusing it with grounding gives
  0.45+. Promote `exp_reader_meaning_integration_diag_v1`'s path into the live reader.

### LEVER 3 — raise the reading spoke via DEPTH (spacing / stay-until-grounded)
Deeper reading builds a better distributional spoke (and grounds more words — the coverage result).
Stay-until-grounded and spaced repetition (Ebbinghaus; Leitner, both pinned) improve the reading
spoke's quality, which lifts the fusion.

### LEVER 4 — confirm on the right yardsticks  [L5]
Re-score the winning fusion on **SimLex-999** (similarity) and a **downstream comprehension task**
(context-conditioned sense selection), each with a POSITIVE CONTROL that the metric detects meaning in
a known-good embedding before trusting any negative. Report per-word-class breakdowns (the concrete/
abstract localization was suggestive but underpowered at n=30-36 abstract pairs — needs a bigger
benchmark to resolve).

### LEVER 5 (hygiene, not a lever) — wire the forager into `substrate.read()`
Land the corpus chooser as correctness (the organ's output is currently discarded), NOT as a
performance win — this brief's measurements say it does not move coverage; depth does.

---

## 4. Risks / twins (every lever)
- **Lever 1 fails if** CSKG embeddings do not beat the norm hub CI-separated in fusion (then the norm
  hub was not the bottleneck). Twin: shuffled graph must lose.
- **Any lever's info-free twin** (shuffled grounding/graph, massed instead of spaced) reproducing the
  gain means it is an artifact — the standing rule that killed four single-seed wins in one session.
- **Do not re-claim concrete-localization** without a larger concreteness-labeled benchmark; current
  evidence is underpowered and reversed for one reader.

---

## TLDR (plain language)
We cracked why reading + grounded knowledge combined into something *worse* than either alone: we had
been forcing the reading side to imitate the grounding side, which throws away what reading knows.
Combine them the way the brain's semantic hub does — let each contribute what it uniquely knows — and
the result beats both (agreement with human word ratings rises from ~0.34 reading-alone and ~0.40
grounding-alone to ~0.47 combined), and a scrambled-grounding control fails, proving the gain is real.
We tried two fancier combination methods (weight by how concrete a word is; learn the combination) and
neither beat the simple equal mix — so the simple, faithful method is the answer. Forward: give it a
much bigger teacher (a 1.2-million-fact knowledge graph we own but never use), wire both channels into
the live reader, and confirm on a comprehension task.

## QUESTIONS
None. One decision for the owner: whether to invest the CSKG-teacher build now (Lever 1, the biggest
absolute lever, ~a few hours to build graph embeddings) or bank the resolved mechanism first.

## NEXT STEPS
1. Bank the resolution: the meaning mechanism is complementary fusion of reading + grounded spokes
   (not distillation). Recorded here + in INTEGRATION_INVESTIGATION_PLAN.md.
2. Lever 1 (CSKG teacher) is the highest-value next experiment; the 30-min cron will drive it unless
   redirected.
3. Lever 2 (wire both spokes into the live reader) is the standing PRIORITY-2 problem, now motivated.
