# THE KNOWLEDGE LEVER — WHERE, WHAT KIND, and THE LEARNER DECISION (consolidated 2026-09-04)

*Owner asked (2026-09-04): "Many solutions, MANY, pointed to more knowledge as a key. Consolidate all of
that — understand WHERE and WHAT KIND of knowledge is key. One grown corpus, or different stores? And the
learner: dedicated ingest + freeze, keep it on, or what?" This note answers all three from the measured
record (53 SOLVED files touch the theme; the load-bearing numbers are cited).*

---
## THE ONE-SENTENCE ANSWER
The recurring lever is NOT "more facts" — it is **CLEAN, TYPED, CORRECTLY-RESOLVED** knowledge; RAW reading-
growth measurably REGRESSES, and the biggest proven win is a **curated, offline-built, FROZEN foundation**
admitted through the (already-built) consolidation gate — build that first; the online learner is the *second*
layer, not the first move.

---
## 1. WHERE knowledge is the lever (by capability, with the measured kind)

| capability | what kind of knowledge | measured status |
|---|---|---|
| **Word-sense selection (the meaning channel / WSD)** | a broad-coverage **sense-discriminative W** (which context words indicate THIS sense over its competitors) | oracle-W → a_s 0.995; real curated foundation 0.251→0.318 (+0.067 CI-sep). The lever is COVERAGE + correct resolution, NOT more static facts. |
| **Parsing / PP-attachment / who-did-what** | **syntactically-TYPED selectional preference** — (verb, role, arg) + (head, grammatical-function, object) | growing a TYPED grounding lexicon lifts PP-attachment 0.587→0.639, MONOTONIC + unsaturated (P8). The generic topical hub does NOT help. |
| **Thematic roles (agent/patient)** | verb-frame / valency + **animacy** | the Competition-Model + structure-first patient already consume verb-frame + animacy; the residual is parse quality + coref, not more facts |
| **Goals / affect** | supplied static lexicons (verb subcat frames, Warriner valence, psych-verb frames) | these WORK and are already shipped as offline foundation assets — the model for "clean curated knowledge helps" |
| **Rare-sense meaning (the deepest wall)** | NOT knowledge — the FROZEN sense-conflated INPUT REPRESENTATION | needs contextual re-representation (a contextual encoder at scale ≈0.40–0.53 = the INVARIANT BOUNDARY) OR a lifetime of rare-sense EXPERIENCE (Zipf-thin). |

**Pattern:** every "more knowledge" finding resolves to one of two TYPED stores — (a) a **sense-discriminative
W** for meaning, (b) **typed selectional preference** for parsing/roles — plus the curated lexical backbone
(WordNet/SyntagNet/ConceptNet) that already exists. They are different *indexes* on the same acquisition.

## 2. WHAT KIND — the three things the data says, sharply
1. **CURATED, CLEAN, STRUCTURED knowledge WORKS** and is largely already available. Admitting a consolidated
   clean foundation (WordNet relations + curated SyntagNet + ConceptNet — an admissible offline static asset,
   NO LLM) through the brain-faithful reader raises a_s **0.251→0.318 (+0.067 CI-sep)** — "the clean
   foundation before learner-on," delivered (consolidation-gate SOLVED, 14/14).
2. **RAW reading-derived growth REGRESSES.** Reading co-occurrence is TOPICAL, not sense-substitutable; the
   raw-ungated twin LOSES (−0.033 below gloss). "To build the W that disambiguates you must first
   disambiguate" — a circularity broken only by grounding-anchored propose-and-verify (resolve the
   confident/concrete cases first, iterate). This is why the learner cannot just be switched on.
3. **GROUNDING (perception) is RULED OUT as the crosser** at every accessible richness (12–65-dim norms,
   ATL-whitened, semantic-inheritance) — all = gloss 0.251. The deepest residual is the static input
   representation, NOT missing perceptual facts.

## 3. ONE CORPUS or DIFFERENT STORES? → ONE acquisition pipeline, TYPED stores
- The **clean foundation is ONE offline-built asset** (curated resources + the consolidation gate) and is the
  biggest, cheapest, already-proven win — build + freeze it once.
- The two learned TYPED stores (sense-discriminative W; typed selectional preference) serve different
  decisions but are built by the SAME pipeline (a large modern reading corpus, correctly-resolved via
  grounding-anchored propose-and-verify, admitted through the SAME consolidation gate). So: **one corpus + one
  gate → several typed stores, indexed by the decision they serve.** Not one blob, not N unrelated corpora.

## 4. THE LEARNER — the recommendation (grounded, brain-faithful, invariant-safe)
State on disk: the reading learner (`hdlab/cls_growth`) is PROVEN-SAFE (+0.110 / 6 rounds) but DEFAULT-OFF,
because RAW admission regresses; the consolidation gate (`hdlab/consolidation_gate.py`) is BUILT as the
admission guard. So the pieces exist; the question is the regime.

**Recommended sequence (NOT "just turn it on," NOT "batch-train a model"):**
1. **FIRST — build + FREEZE the clean CURATED foundation** (WordNet/SyntagNet/ConceptNet + typed selectional
   preference), offline, through the consolidation gate. This is ADMISSIBLE (a static offline-built foundation
   asset — owner rule 2026-08-16), already PROVEN (+0.067), and is the measured "clean foundation before
   learner-on." **This is the biggest immediate win and it is NOT model-training** — it is assembling a
   structured, verified store. Verify → freeze → ship.
2. **THEN — online grow-experience ON TOP**, via grounding-anchored PROPOSE-AND-VERIFY (the filed north-star
   `grow_broad_coverage_correctly_resolved_rare_sense_experience...`): resolve confident/concrete cases first,
   admit ONLY clean growth through the gate + cls_growth, iterate over a large corpus. This is the brain's
   online acquisition (one-pass, no batch training) — it addresses the Zipf-thin rare-sense EXPERIENCE the
   frozen curated foundation can't cover. Keep it ON only if it MEASURABLY beats the frozen foundation
   (inductive-only + MFS-guard + shuffled-twin controls — two false PASSes were caught only by those).
3. **DO NOT** turn on the raw reading learner (regresses); **DO NOT** batch-train a contextual encoder unless
   the owner relaxes the no-transformer invariant (the open P9 decision — that buys ≈0.53 on rare senses).

**"Dedicated ingest + freeze?" → YES, for the curated foundation (step 1) — admissible, proven, do it first.
"Keep it on?" → only the propose-and-verify online layer (step 2), and only if it beats the frozen foundation.**

## 5. THE ONE OWNER DECISION THAT GATES THE CEILING
The rare-sense ceiling is ~0.34 glass-box vs ~0.53 with a scale-trained contextual encoder (the invariant
boundary). **HOLD the invariant** → the coverage/learner-on route above (steps 1–2), ceiling grown by
experience. **RELAX it once** → one offline contextual-sense asset reaches ~0.53. Recommendation: HOLD and
pursue steps 1–2 first (they are cheap, proven, and brain-faithful); revisit the relax only if the
experience route plateaus below target.

## 6. CONCRETE NEXT MOVES (verdict-independent, ready to assign)
- **A dedicated problem: "build + freeze the clean curated knowledge foundation"** (WordNet+SyntagNet+ConceptNet
  + typed selectional preference through the consolidation gate; verify +0.067 reproduces; freeze; wire as the
  reader's default meaning foundation). *This is the step-1 win and is not yet a filed problem — file it.*
- The filed `grow_broad_coverage_correctly_resolved_rare_sense_experience...` (priority 5) IS step 2.
- The typed selectional-preference store is the shared lever under the filed parser problems (2/3/6).
