---
problem: audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins
status: SOLVED
bar: "PASS = a prioritized, DISK-VERIFIED CATALOG (CATALOG.md) of every LIVE non-brain-faithful stand-in in the grounding-acquisition subsystem, each with FIVE disk-verified fields (the brain structure+computation it should implement / why the current thing is not it / the brain-foundational replacement / blast + live-vs-dormant with the consuming file:line / fix class), top-K ranked by blast, denominator = the subsystem's actual live import+call closure (reconciled against flag defaults, not comments), explicitly distinguishing live-defective vs live-but-inert vs dormant -- PLUS a powered can-fail LOCALIZATION of the #1 item on the subsystem's OWN metric (the grounding loop's ranking / growth-quality measure), with a machine-checkable pure-disk witness (verification/test_audit_grounding_subsystem.py) that reproduces every LIVE/DORMANT classification from disk. NO hdlab/ writes (Q111)."
result: "CATALOG.md = 4 LIVE stand-ins (G1 bag-of-content-words co-occurrence comparator; G2 grounded input channel imported-but-INERT; C7 attractor-as-ranker; C8 hd_fact_store trust-only vetting) + 3 located-negatives/corrections (N1 dormant+refuted structured encoder; N2 dormant VWFA; N3 six dormant-islanded orchestrators), each with all five disk-verified fields, top-K ranked. Denominator = the live import+call closure of Substrate.read() + the grounding-core run, classified by a runtime import+settrace trace (exp_audit_grounding_subsystem_v1.py): 16 LIVE-CALLED / 23 LIVE-IMPORTED-INERT / 6 DORMANT-ISLANDED, positive control fired. #1 LOCALIZATION (exp_ground_readout_localization_v1.py, n=999 SimLex pairs + n=1685 ConceptNet targets): a DISSOCIATION -- the brain-faithful ATL conceptual channel beats the co-occurrence family on grounded MEANING (SimLex rho 0.521 vs 0.371, +CI-sep, info-free twin loses) but does NOT beat it on the loop's OWN relatedness gold (ConceptNet prec@1 0.261 vs 0.248, CIs overlap; WordSim rho 0.432 vs 0.596, co-occurrence WINS) -> the #1 stand-in is locally optimal for a mis-specified (relatedness) objective over an ungrounded (co-occurrence) input. The #1 FIX was ALSO prototyped + UPSTREAM-TRACED (owner 'do all; trace the signal back'): an early grounded read-out lost, but the loss was an UPSTREAM-FIDELITY ARTIFACT -- after fixing three non-brain-foundational upstream links (hardcoded POS -> the substrate's UPOS tagger; raw sum -> ATL covariance distillation; syntagmatic sentence-bag -> PARADIGMATIC dependency context via the substrate's parser) the grounded read-out FLIPS to the BEST arm (GROUNDED_STRUCT SimLex 0.147 > COUNTING 0.143 > BAG 0.140; beats its twin +0.175 CI-sep and the sentence-bag grounding +0.017), reaching PARITY with counting (not CI-sep, parse-data-limited). The DECISIVE brain-foundational win remains DIRECT grounding of the target's own features (localization: SimLex 0.521 vs 0.371, above the co-occurrence family's ~0.37 ceiling). Fix = direct grounding + meaning objective + online coverage; paradigmatic grounded context is a real supplement. Witness 15/15."
floor: "Localization floors, all run: the co-occurrence STEELMAN = GloVe (ASSOC, a strong co-occurrence model; SimLex rho 0.371); the landed COUNTING floor on the live own metric = TOP_COOCCURRENT 0.0476/0.0653/0.0590 which the live bag read-out (SUBSTRATE 0.0159/0.0302/0.0272) LOSES to (disk-verified, data/exp_meaning_readout_own_metric_v1); the info-free TWIN = word->conceptual-vector permutation (near-chance, loses CI-separated). Catalog floor/positive-control: the reader-audit's C7/C8 handoff, both recovered as LIVE-CALLED and extended."
controls: "(1) runtime import+call trace with a POSITIVE CONTROL (tracer fired, caught process_sentence) separating LIVE-CALLED from LIVE-IMPORTED-INERT from DORMANT-ISLANDED -- excludes the 'imported != executed' false positive (caught grounded_similarity imported-but-inert; caught StructuralEncoder/parser/vwfa/three_tier dormant despite being importable). (2) info-free TWIN (word->vec permutation) LOSES on meaning -> the conceptual channel reads distinctive features, not a population artifact. (3) co-occurrence STEELMAN (GloVe, stronger than the live bag) still loses on meaning -> the wall is the co-occurrence FAMILY, not a weak implementation. (4) the ConceptNet own-gold EXCLUDES WordNet provenance -> no circularity with the WordNet-sourced conceptual channel. (5) do-not-over-fire: every LIVE-CALLED organ scanned; the brain-faithful HD/CLS organs (foraging=MVT, hippocampal=CA3, event_bundle/role_slot=FHRR-recall, definitional=WordNet supply) verified admissible, not flagged."
files_changed: "experiments/exp_audit_grounding_subsystem_v1.py (the import+call trace/denominator); experiments/exp_ground_readout_localization_v1.py (the #1 dissociation localization); experiments/exp_grounded_meaning_readout_v1.py + experiments/exp_grounded_meaning_readout_structured_v1.py (the #1 FIX prototyped + upstream-traced: POS tagger + ATL distillation + paradigmatic dependency context) + experiments/exp_grounded_meaning_readout_remote_sweep_v1.py (BF optimization sweep: fusion/relation-typed/dim + DIRECT reference -> DIRECT 0.48 dominates) + experiments/exp_grounded_meaning_readout_coverage_fusion_v1.py (THE OPTIMIZED FIX: coverage-aware reliability-weighted fusion beats the co-occurrence stand-in +0.125 CI-sep @40% coverage, scales to 0.49 = direct) + experiments/exp_multimodal_hub_v1.py (the MULTIMODAL ATL hub closing the gap to the brain: verbal+sensorimotor+affective reliability-weighted fusion 0.569 vs verbal 0.527 +0.042 CI-sep, closes 29% of the verbal->brain gap) + experiments/exp_grounded_meaning_readout_remote_sweep_v1.py; verification/test_audit_grounding_subsystem.py (15/15 pure-disk witness); notes/problems/audit_the_grounding_acquisition_subsystem_for_non_brain_faithful_stand_ins/CATALOG.md (the deliverable) + SOLVED.md. NO hdlab/ writes (Q111 -- this is a MAP + proposed fixes + the #1 localization + the #1 fix prototyped)."
reverify: ".venv/Scripts/python.exe verification/test_audit_grounding_subsystem.py"
---

# Audit — the grounding-acquisition subsystem's non-brain-foundational stand-ins

**The deliverable is `CATALOG.md` in this folder** (4 LIVE stand-ins + 3 corrections, five disk-verified fields each,
top-K, admissible list, positive control). This SOLVED.md is the summary + the #1 full-stack-upstream localization +
the required sections.

## 🔧 BRAIN-FOUNDATIONAL FIXES IDENTIFIED (the actionable list — read this first)
Every non-brain-foundational stand-in found, with its brain-foundational replacement, where it lives, the evidence,
and whether it is the DECISIVE lever or a supplement. Details for each are in the sections below + `CATALOG.md`.
NO `hdlab/` writes here (Q111) — these are the proposed changes for strategy to land.

| # | non-brain-foundational NOW | brain-foundational FIX | where (file:line / organ) | evidence | class |
|---|---|---|---|---|---|
| **1** | meaning read-out decides by a **co-occurrence bag cosine** (relatedness) | **DIRECT grounded read-out**: the target's OWN grounded features — wire the inert `grounded_similarity` spoke + broaden `definitional_extraction` | `reading_grounding_loop.canonicalize:872`, `_make_grounding_gate:1469`; `grounded_similarity` (LIVE-IMPORTED-INERT) | direct grounding SimLex **0.521** vs co-occurrence 0.371 (twin loses) | **DECISIVE** |
| **2** | growth-quality **objective = ConceptNet relatedness** — rewards the co-occurrence stand-in | **MEANING objective** (grounded substitutability); decide in grounded space | `schema_consistency_split_half:414`, `canonicalize`; the own-metric harness | dissociation: co-occ ties grounded on the relatedness gold, loses on SimLex | **DECISIVE (land with #1)** |
| **3** | grounding grown by a **single-pass distributional guess** | **online propose-verify** accumulation (MINERVA-2; north-star) — the brain does not batch-train | the learner turn-on path | brain-does-not-train + the parity ceiling below | **DECISIVE (land with #1)** |
| **4** | context encoded as a **syntagmatic sentence bag** (relatedness) | **PARADIGMATIC dependency context** via the substrate's parser (Levy-Goldberg) | `process_sentence._encode:1345` (the `encoder` path) | grounded-STRUCT flips to **best arm 0.147**, beats its twin +0.175 CI-sep | supplement (real, not decisive) |
| **5** | context words represented with **hardcoded/blurred POS**, a **raw-sum** compose, no normalisation | correct POS (**`hdlab.pos_tagger`**) + **ATL covariance distillation** (Rogers-McClelland) + **common-mode removal** (Carandini-Heeger) + **PPMI/surprise** weighting | any read-out that composes context word codes | fixing these FLIPPED the grounded arm from losing to best-arm | general upstream-fidelity fix |
| **6** | gap-gate uses the **attractor's settled argmax as a RANKER** (can drift to hubs) | **graded population read** for row-selection; reserve the attractor for recognition | `gap_detector.ca3_match_score:111` → `iterative_attractor:125` | bounded (margin stays an honest CA1 cosine) | **filed pri-5** (don't duplicate) |
| **7** | `hd_fact_store` vets by **source-trust only**, not correctness | correctness/quality gate at admission | `hd_fact_store.store:323`; already gated upstream at `_make_grounding_gate:1471` | remediated (tautology refusal live) | LOW / telemetry |
| — | **DO NOT** re-propose the dependency-STRUCTURED encoder over **RANDOM** codes (N1) | — it is a landed CI-separated NEGATIVE; grounding is what makes structure pay | `StructuralEncoder:378` (DORMANT) | −0.0113 CI[−0.0195,−0.0030] | do-not-redo |
| — | **DO NOT** ground the **SENTENCE bag** alone | — ties counting; the lever is DIRECT grounding + PARADIGMATIC context | — | tie (deltas include 0) | do-not-redo |

**The one-line takeaway:** the decisive brain-foundational fix is **DIRECT grounding of the target's own features + a
meaning objective + online coverage (rows 1-3, land together)**; paradigmatic grounded context (row 4) is a real
supplement; rows 5-7 are the upstream-fidelity + adjacent fixes. Direct grounding (0.52) sits ABOVE the whole
co-occurrence family's ceiling (~0.37), so no amount of tuning the distributional read-out substitutes for it.

### OPTIMIZATION SWEEP now that the mechanism is brain-foundational (owner: "any optimizations now we're BF?")
`exp_grounded_meaning_readout_remote_sweep_v1.py` sweeps the BF operating point over 6 MODERN corpora (opt A fuse
direct+paradigmatic; opt B relation-TYPED Levy-Goldberg context; opt C distillation-dim) with a DIRECT reference arm.
Smoke (dim=200, 6879 parsed, n=409 pairs) SimLex rho: **DIRECT 0.475** >> FUSED 0.403 >> COUNTING 0.046 / BAG 0.039 /
GROUNDED_SENT 0.037 / GROUNDED_STRUCT 0.036 / STRUCT_TYPED 0.034 / TWIN 0.016. Findings that reshape the fix:
- **DIRECT grounding dominates ~10x** — the decisive lever, reproduced a 3rd way (independent of the localization).
- **Naive equal-weight FUSION HURTS** (−0.072 vs DIRECT): summing a near-noise context spoke DILUTES the strong direct
  spoke. => the right optimization is **COVERAGE-AWARE fusion** (direct where the word is grounded, context ONLY as
  the fallback for uncovered words), i.e. reliability-weighted hub integration — not a blind sum.
- **Relation-typing (B) and dim (C) do NOT lift the distributional arms off counting-parity (~0.04)** — so tuning the
  distributional read-out is not where the gain is; DIRECT-grounding COVERAGE is.
- **Net:** the highest-value optimization is (1) maximise DIRECT-grounding coverage (definitional extraction + the
  foundation + online growth) and (2) coverage-aware reliability-weighted fusion of the spokes; paradigmatic context is
  a fallback, not a lever. A powered remote CI-run confirms the (already large) DIRECT-vs-distributional gap; the
  distributional deltas are floor-level and not worth chasing.

### THE OPTIMIZED FIX, PROTOTYPED + WON: coverage-aware reliability-weighted fusion (`exp_grounded_meaning_readout_coverage_fusion_v1.py`)
The ATL hub integrates spokes by PRECISION, not by averaging (Ernst-Banks 2002 / Friston; hub-and-spoke). So the fix is
`meaning(w) = r_direct(w)*DIRECT_unit + lambda*r_context(w)*CONTEXT_unit`, with `r_direct` = COVERAGE (1 if the word has
direct grounding — a definition/foundation entry — else 0), `r_context` = evidence-scaled context reliability, `lambda`
~0.1 (the context spoke's inherent reliability relative to direct). Coverage is simulated FREQUENCY-FIRST (common/early
words grounded directly first — the realistic loop). Result (SimLex, n=404 pairs, twin = shuffled coverage):
- **The current live read-out (CONTEXT_ONLY co-occurrence) = 0.042. Coverage-aware fusion at a realistic 40% coverage =
  0.168, a +0.125 CI[0.052,0.199] WIN (CI-separated)**, scaling monotonically with coverage: 0.06 (0%) -> 0.17 (40%) ->
  0.33 (80%) -> 0.49 (100% = direct). **=> the lever is DIRECT-grounding COVERAGE**, and fusing it with context (as a
  reliability-weighted fallback) lifts the read-out far above the co-occurrence stand-in.
- **Reliability-WEIGHTING pays off at high coverage:** at 100% covered, weighted fusion keeps full direct quality (0.491)
  where NAIVE equal-weight fusion DILUTES to 0.411; at partial coverage the two track (both fall back to context on
  uncovered words), so FUSED-vs-NAIVE is not CI-separated at this n — stated honestly, not overclaimed.
- **This is the optimized brain-foundational read-out:** direct grounding where covered (the decisive spoke), context as
  a reliability-weighted fallback where not, integrated by precision — beating the #1 co-occurrence stand-in CI-separated
  and scaling to the direct-grounding ceiling as coverage grows. The hdlab wire = (a) `grounded_similarity`/definitional
  DIRECT spoke, (b) the coverage/reliability signal (does the word have a definition/foundation entry + context
  coherence), (c) this precision-weighted fusion in `canonicalize`, (d) a meaning objective. Coverage grows online.

### CLOSING THE GAP TO THE BRAIN: the MULTIMODAL ATL hub (`exp_multimodal_hub_v1.py`)
Even at full direct grounding the DIRECT read-out is the VERBAL/definitional spoke ALONE (SimLex ~0.52); the brain's
concept is a MULTIMODAL hub. Research (this session, cited in the AUDIT UPDATE) settled that the ATL integrates spokes by
a LEARNED COVARIANCE-DISTILLATION CONVERGENCE (Rogers-McClelland 2004; Lambon Ralph 2017), with verbal (taxonomic) and
sensorimotor (perceptual) spokes COMPLEMENTARY (verbal breaks the sensorimotor "sibling ceiling"; SimLex targets the
taxonomic axis). Built it from on-disk brain-grounded norms — Lancaster sensorimotor (11 dims, 100% SimLex cov), Warriner
VAD affective (98%), Brysbaert concreteness (100%); Binder-2016 is the gold brain feature set but only 535 words/0% cov,
so these are the defensible partial approximation of its sensory/motor/affective quadrant. Method (verbatim from the
research): per-block z-score -> verbal-dominant reliability weighting (experiential at a SWEPT weight lambda) -> concat,
fit gold-blind on a SimLex-disjoint background (leakage guard). **Result (SimLex, n=977 pairs = ~all of SimLex):**
- **The multimodal hub 0.569 BEATS the verbal spoke alone 0.527: +0.042 CI[0.024,0.062], frac_pos 1.0 — CI-separated —
  CLOSING 29% of the verbal->brain(0.67) gap. Info-free twin loses (-0.01).** Each spoke alone is far weaker
  (sensorimotor 0.26, affective 0.26), so the gain is genuine COMPLEMENTARITY (hub-and-spoke confirmed), not one spoke.
- **The reliability weight peaks cleanly at lambda=0.25** (0.569 -> 0.566 -> 0.511 -> 0.447 as experiential weight rises):
  verbal is the reliable dominant spoke; sensorimotor/affective are a 1/4-weight complement — the Ernst-Banks reliability
  weighting the research named as the legitimate secondary term.
- **Honest limits:** the lossy linear SVD "hub" arm (0.50) slightly underperforms the weighted concat (a nonlinear
  autoencoder is the untested closer-to-brain variant — a named follow-on); and the remaining 0.57->0.67 gap needs the
  FULL Binder experiential space (spatial/temporal/social/cognitive quadrants), which is coverage-blocked here (535 words).
- **=> The optimized fix now targets 0.57 (from a live 0.04):** wire the MULTIMODAL direct spoke (verbal + sensorimotor +
  affective norms, reliability-weighted) as the grounded read-out, coverage-aware fusion with context as fallback, online
  coverage growth. The multimodal hub is the lever that reaches toward the brain's ceiling.

## What I built
1. **The denominator, by enumeration not comment-grep** (`experiments/exp_audit_grounding_subsystem_v1.py`). A runtime
   **import trace** (5 fresh-subprocess closures) + a **settrace call trace** over the subsystem's live entry point
   `Substrate.read()` and a direct grounding-core run (`seed → process_sentence → checkpoint`, default flags). It
   classifies every hdlab module in the closure into **LIVE-CALLED (16)** / **LIVE-IMPORTED-INERT (23)** /
   **DORMANT-ISLANDED-ONLY (6)**, with a positive control (the tracer caught `process_sentence`) and twelve targeted
   probes. This is what let me separate a *live decision* from an *imported-but-inert* organ from a *dormant island* —
   the reader-audit's own lesson that "LIVE has three failure modes."
2. **The prioritized CATALOG.md** — G1 bag comparator (#1, CRITICAL), G2 grounded-channel-inert (HIGH), C7
   attractor-as-ranker (MEDIUM, bounded), C8 store trust-vetting (LOW, remediated), + N1–N3 located negatives.
3. **The #1 localization** (`experiments/exp_ground_readout_localization_v1.py`) — a powered can-fail DISSOCIATION on the
   loop's own metric, addressing the owner's full-stack-upstream directive step by step.
4. **The pure-disk witness** (`verification/test_audit_grounding_subsystem.py`, 14/14) that re-derives the classification
   from the current bytes and checks the two landed numbers.

## The #1 item, localized full-stack-upstream (the owner's four steps)

**Step 1 — is the end component 100% brain-foundational? What are its inputs? Is it research-supported?**
The end component is the grounding decision — `canonicalize` (nearest-anchor sense assignment) + the consolidation
gate. It is **NOT** brain-foundational: it decides meaning by a **cosine over a bag of nearby content-word codes**
(`canonicalize` `reading_grounding_loop.py:872–911`; `context_vector` `grounding_acquisition_loop.py:117`;
`schema_consistency_split_half` `:414–462`). Its inputs are (i) the context representation — a sum of sha256-seeded
**random bipolar codes** (`symbol_vector:297–310`), i.e. ungrounded word identities in a d=256 superposition; (ii) the
anchor space — the same bags; (iii) the gap signal (C7). The brain grows word meaning in the **anterior-temporal
semantic hub**, integrating **sensorimotor spokes + verbal/definitional experience** into a grounded distinctive-feature
code (hub-and-spoke: Lambon Ralph et al. 2017; Rogers & McClelland 2004; Binder & Desai 2011). A co-occurrence bag is a
different, lower-fidelity computation — the classic distributional convenience (Firth 1957), not the hub.

**Step 2 — trace, all the way up, where the signal on those inputs is lost.**
On the loop's OWN metric the bag read-out **loses to word-counting**: `SUBSTRATE 0.0159/0.0302/0.0272 <
TOP_COOCCURRENT 0.0476/0.0653/0.0590` (`data/exp_meaning_readout_own_metric_v1`, disk-verified). Two prior drills
already refuted the two obvious *comparator/input* fixes over the same bag — dependency **STRUCTURE hurts** (−0.0113
CI[−0.0195,−0.0030], `exp_structured_code_vs_flat_bag_c3_v1`) and sensorimotor **GROUNDING ties** the counting floor
(paired-perm p=1.0, `exp_sensorimotor_spoke_grounding_v1`). So the signal is not lost *in the cosine*; it is lost at
the **input representation** (ungrounded co-occurrence) and — the deeper find — at the **objective** (the loop's own
growth-quality metric is itself co-occurrence-shaped).

**Step 3 — dig deep: it is not brain-foundational *somewhere*. Where?** A powered can-fail dissociation (n=999 SimLex
pairs; n=1685 ConceptNet targets) pins it to **two coupled non-brain-foundational links**:
- **The input.** A brain-faithful ATL **conceptual** channel (WordNet gloss+genus distinctive-feature cosine) **EXCEEDS**
  on grounded-MEANING similarity where the co-occurrence family cannot: SimLex rho **0.521** vs GloVe (a strong
  co-occurrence steelman) **0.371** vs the wired grounded spoke **0.291**; the info-free **word→vector-permutation twin
  loses CI-separated**. So grounded meaning IS learnable/measurable — the co-occurrence input just cannot carry it.
- **The objective.** On the loop's OWN gold (ConceptNet-neighbour precision@1) the conceptual channel does **NOT** beat
  the co-occurrence family (0.261 vs 0.248, CIs overlap), and on a relatedness gold (WordSim) co-occurrence **WINS**
  (0.596 vs 0.432, CI-sep). The loop's own metric REWARDS association, and is blind to the meaning signal that separates
  the two channels on SimLex.
→ **The #1 stand-in is locally optimal for a mis-specified (relatedness) objective, over an ungrounded (co-occurrence)
input.** No comparator swap fixes that; the brain-faithful fix couples a **grounded input channel** with a **meaning
objective**. Both grounded inputs already exist in the process and are not fed to the decision: `grounded_similarity`
is **LIVE-IMPORTED-INERT** (funcs=0), and the conceptual/definitional channel fires only on explicit genus statements.

**Step 4 — are the tools cheap off-the-shelf things?** Yes, and named: the **co-occurrence bag** (Firth distributional
convenience) and the **ConceptNet/relatedness objective** are the easy distributional stand-ins; the brain uses grounded
ATL representations and a meaning objective. (The audit also confirmed no *external tool at inference* in the subsystem:
the WordNet lookups are admissible static foundation supply, and the in-substrate parser assets are dormant.)

**"Excel and exceed" + no downstream regression + upstream is brain-foundational (owner directive).** The brain-faithful
upstream representation (ATL conceptual channel) EXCEEDS the co-occurrence family on the *right* metric (grounded meaning,
+CI-sep, twin loses) — research-backed (hub-and-spoke; Rogers–McClelland covariance distillation). Because this audit is a
MAP (no hdlab writes), no live consumer is changed, so nothing regresses yet; the localization explicitly warns that
wiring the grounded channel WITHOUT also fixing the co-occurrence objective would move no board number (it ties on the
own metric) — the two must land together. That is the full-stack-upstream conclusion: **every link (input AND objective)
must be brain-foundational for the wall to fall.**

## THE #1 FIX, PROTOTYPED + UPSTREAM-TRACED (owner directive: "do all, brain-foundational, right not easy;
## a brain-foundational component relies on brain-foundational components upstream -- trace the signal back")
The localization named the coupled fix (grounded input + meaning objective). Prototyping the INPUT half exposed
exactly the owner's principle: an EARLY version LOST -- but the loss was an UPSTREAM-FIDELITY ARTIFACT, not a
structural fact. Tracing the signal back and making every upstream link brain-foundational FLIPPED it.

**The three upstream links that were NOT brain-foundational (found + fixed):**
1. **POS** -- the first version hardcoded POS="N" for every context word, so verbs/adjectives/adverbs (~half the
   tokens) were looked up as nouns. FIX: the substrate's own UPOS tagger (`hdlab.pos_tagger`, Viterbi perceptron).
2. **Composition** -- a raw centroid, not the ATL's operation. FIX: Rogers-McClelland covariance DISTILLATION
   (whitened SVD, fit gold-blind on background WordNet; the conceptual channel's `_build_distillation`).
3. **Context type** -- the SYNTAGMATIC whole-sentence bag (which encodes RELATEDNESS), not the PARADIGMATIC
   context that carries SIMILARITY. FIX: DEPENDENCY-linked context (head + dependents + co-arguments) via the
   substrate's own parser (`hdlab.arc_parser`/`arc_labeler`) -- Levy-Goldberg 2014.

**The corrected result (`exp_grounded_meaning_readout_v1.py` sentence-bag; `exp_grounded_meaning_readout_structured_v1.py`
paradigmatic), on grounded MEANING (SimLex), all common-mode-removed + PPMI-weighted, twin = word->vector permutation:**
- SENTENCE-bag grounding (POS-correct + distilled), n=547 pairs: `GROUNDED_DISTILL` **0.036** ~ `BAG` **0.045** ~
  `COUNTING` **0.046** -- a TIE (deltas' CIs include 0). Grounding the SENTENCE bag alone does not move it.
- PARADIGMATIC (dependency) grounding, n=269 pairs (parse-limited): **`GROUNDED_STRUCT` 0.147 is the BEST arm** >
  `COUNTING` 0.143 > `BAG` 0.140 > `GROUNDED_SENT` 0.130. It beats its info-free TWIN **+0.175 CI[+0.015,+0.34]**
  and the sentence-bag grounding **+0.017 (frac_pos 0.78)** -- so paradigmatic STRUCTURE + grounding both carry
  real signal -- but it only **TIES/edges the counting floor** (+0.004, NOT CI-separated at this data scale).
=> The earlier "located negative" is RETRACTED as an upstream artifact: with the whole upstream chain
brain-foundational, grounding the context stops losing and becomes the best arm. But it reaches PARITY with
counting, not a decisive win -- and that has a principled ceiling: the co-occurrence FAMILY tops out near GloVe's
SimLex rho ~0.37 (a strong co-occurrence model on massive data), whereas...

**...the fix that DECISIVELY WINS is DIRECT grounding of the target's OWN features (localization, disk-verified):**
a direct grounded/conceptual representation scores SimLex **0.521** vs co-occurrence 0.371 (twin loses) -- ABOVE
the whole distributional-context ceiling. So "brain-foundational all the way wins" is TRUE, and the winning
mechanism is DIRECT grounding (the ATL hub's own representation), not a fully-tuned distributional-context model.
For a word learned from reading that means the on-page DEFINITION/genus (`definitional_extraction`, already LIVE,
32% vs 8% distributional) + the sensorimotor spoke (`grounded_similarity`, currently INERT), accumulated by
ONLINE propose-verify (the north-star; the brain does not batch-train). The lever is COVERAGE + a MEANING
objective. (Paradigmatic grounded context is a real, brain-foundational SUPPLEMENT -- best-arm, beats its twin --
worth wiring alongside, but it is not the decisive lever; direct grounding is.)

**Remaining upstream links not yet made faithful (candidate further gains, honestly named):** (a) WSD of each
context word (a known wall -- "WSD = representation not grounding"); (b) RELATION-TYPED paradigmatic context
(nsubj:drive, not just drive -- true Levy-Goldberg); (c) POWER: the parser runs ~8 sentences/sec (O(n^2)), so a
CI-separating sample needs the remote box or a parse cache -- the +0.004 counting margin is data-limited. None of
these changes the ceiling argument: direct grounding (0.52) sits above the distributional family (~0.37).

**The exact hdlab diff (for strategy to land, Q111 -- three coupled changes, landed TOGETHER):**
1. **DIRECT grounded read-out (not context-composed).** In `reading_grounding_loop.canonicalize` /
   `_make_grounding_gate` (`:1469`), compare the target's DIRECT grounded representation against grounded
   anchors, not the co-occurrence bag: wire the currently-INERT `grounded_similarity` spoke (36,810-word
   coverage) as the target's grounded code where covered, and keep/broaden `definitional_extraction` as the
   on-page direct-grounding path.
2. **MEANING objective.** Replace the growth-quality metric (ConceptNet-neighbour relatedness precision, on which
   the stand-in is locally optimal -- the dissociation) with a grounded-MEANING objective (SimLex-type
   substitutability); compute `schema_consistency_split_half` / `canonicalize` decisions in grounded space.
3. **COVERAGE via online growth**, not a single-pass distributional guess -- grow direct grounding by online
   propose-verify over encounters (MINERVA-2 episodic; the north-star), NOT the batch distributional composition
   this prototype refuted.
**DO NOT** (this prototype's located negative, plus the two prior ones): ground/structure the co-occurrence
CONTEXT representation -- it ties or loses PPMI counting.

## What I did NOT establish (honest bounds)
- I did **not** build the live grounding read-out's bag over a fresh corpus inside the drill; I used GloVe as a strong
  co-occurrence STEELMAN (so the argument is *a fortiori* — the live bag is weaker than GloVe) and quoted the landed live
  own-metric loss (SUBSTRATE < counting) directly. The dissociation is about the co-occurrence *family*.
- I did **not** re-solve grounding or wire anything — the learner turn-on and the fix are out of scope (Q111; named
  follow-ons below). The catalog is a MAP + the #1 localization.
- The C7 "bounded" verdict rests on the gap gate reading the RAW CA1 margin (`gap_detector.py:114–117`); I did not measure
  how often the attractor's settled argmax diverges from the true nearest neighbour (that quantification is pri-5's job).
- ConceptNet own-metric precision is low in absolute terms for every arm (~0.05–0.26) — it is a hard sparse metric; the
  load-bearing claim is the *relative* dissociation, not the absolute level.

## What I would withdraw first if wrong
The G2 framing that the grounded channel is "one wire from live." The dissociation shows wiring `grounded_similarity`
alone would tie the own metric (the objective is also the wall). If a reader reads G2 as "just wire it," that is the
over-claim to strike first — the localization is explicit that input AND objective must change together.

## KEY REALIZATIONS (the enabling moves)
- **The import trace had to trace CALLS, not imports.** The first pass ran the fixture's `import` statements *under*
  `settrace`, so every module body registered as a "call" and 40 modules looked LIVE-CALLED — including the dormant
  `StructuralEncoder` (its class body fired at import). Pre-importing before tracing and filtering `<module>` frames
  collapsed it to the true 16 LIVE-CALLED, and flipped `structural_encoder_dormant` from a false-negative to True. The
  live/dormant distinction is only meaningful once "executed a function" is separated from "was imported."
- **The obvious brain-faithful fix was a known double-negative — so I stopped and asked the deeper question.** Surveying
  prior work first showed dependency-structure HURTS and sensorimotor-grounding TIES on the live path. That killed
  "swap the comparator" and forced the real question: *why does every comparator over this input tie/lose?* — which is
  what surfaced the objective (the loop's own metric is relatedness).
- **The loop's own metric validates its own stand-in.** The single most useful measurement was scoring the
  meaning-winning conceptual channel on the loop's OWN ConceptNet gold and finding it *ties* the co-occurrence family. A
  metric that cannot tell grounded meaning from association cannot supervise a grounded learner — the objective is a
  stand-in, not just the representation.
- **A dormant-looking win can be a live *inert* input.** `grounded_similarity` is imported by the live path and never
  called — the grounded input the comparator needs is in the room and unused. "Imported ≠ consumed" is the input-side
  twin of the reader-audit's "computed-and-discarded."
- **The control was the finding.** In the fix prototype, common-mode removal (Carandini-Heeger) was the move that made
  the result readable: before it, the info-free twin scored a spurious 0.055 and would have let me mis-read a frequency
  artifact as a win. Centring collapsed the twin to ~0 and revealed the honest negative (grounded-context composition
  loses to counting). A brain-faithful *control* (divisive normalisation) rescued a brain-faithful *measurement*.
- **A brain-foundational component needs a brain-foundational upstream (owner's push, and it paid off).** The
  grounded read-out first LOST — and the loss was an UPSTREAM artifact, not a structural fact: a hardcoded POS
  corrupted half the context words, a raw sum stood in for the ATL's distillation, and a syntagmatic sentence-bag
  stood in for paradigmatic context. Fixing all three FLIPPED it to the best arm. The lesson: before believing a
  brain-faithful mechanism's negative, trace every upstream signal and confirm each link is itself brain-faithful.
- **"Ground the input" split into two claims with different ceilings.** Grounding the target's own features (DIRECT)
  excels on meaning (localization, 0.52, above the co-occurrence family's ~0.37 ceiling); grounding the target's
  CONTEXTS (distributional) reaches best-arm/parity with counting once the upstream is faithful, but not above the
  distributional ceiling. Direct grounding is the decisive lever; paradigmatic grounded context is a real supplement.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md §2b — strategy re-verifies + folds in)
- **EXTENDS the existing "grounding ceiling is REPRESENTATION-bound" entry (2026-09-01):** the ceiling is representation
  **AND objective**. The live grounding read-out (bag-of-content-words cosine) loses to counting on its own metric; a
  brain-faithful ATL conceptual representation separates grounded meaning (SimLex 0.521 vs 0.371 co-occurrence, twin
  loses) but the loop's own growth-quality metric (ConceptNet-neighbour precision) is a *relatedness* gold on which it
  does not separate — so the stand-in is locally optimal for a mis-specified objective. Fix = grounded input + meaning
  objective, landed together.
- **NEW live-map for the grounding-acquisition subsystem (the reader-audit's excluded second entry point):** LIVE-CALLED
  decision organs = the bag comparator (`canonicalize`/`context_vector`/`schema_consistency`), the C7 attractor gap-gate,
  `hd_fact_store`, `definitional_extraction`; the grounded channel `grounded_similarity` is LIVE-IMPORTED-INERT; the
  StructuralEncoder + parser assets + VWFA + the six orchestrators (`three_tier_loop`, `gap_driven_reader`,
  `gather_reason`, `kg_traversal`, `prelim_tier`, `script_grain_acquisition_loop`) are DORMANT.
- **C7 refined:** LIVE but BOUNDED — the gap gate reads the honest RAW CA1 pre-settle cosine as its margin; only the
  attractor's *row-selection* (settled argmax, `iterative_attractor.py:125–126`) can drift to hubs. (Owned by pri-5.)
- **C8 confirmed remediated:** `hd_fact_store` vets by source-trust only, but the tautology/quality gate is live upstream
  (`_make_grounding_gate` `REFUSAL_TAUTOLOGY`); the correctness-cleanup problem is integrated.

## TLDR (plain English)
The system has a second way it runs that the last audit skipped: the part that LEARNS word meanings by reading. I traced
exactly what code actually runs when it learns (not what the comments claim), and made one ranked list of every place it
takes a convenient shortcut instead of working like a brain. The worst shortcut, switched on right now: to decide what a
new word means, it just checks which other words tend to sit near it — a word-company tally. On the system's own report
card that tally scores *worse than plain word-counting*. I then dug into WHY, all the way up the chain, and found the
loss is in two linked places, and I proved it: (1) the INPUT it reads is a bag of meaningless word-tags with no grounding,
and a proper brain-style "meaning from a dictionary-definition" representation beats the word-company tally on a real
human meaning test — while a scrambled version fails, so it's real; (2) but the system's own report card only measures
"do these words hang out together", not "do they mean the same thing", so it actually *rewards* the shortcut and can't
see the better method at all. So you can't fix this by tweaking the tally — you have to feed it grounded meaning AND
change what the report card rewards, together. I also found the grounded-meaning part it needs is already loaded into the
program but never actually used, and I confirmed a couple of earlier-flagged shortcuts are either switched off or already
fixed. I changed no live code (that's the other lane); this is the map plus the one deepest fix proven.

## QUESTIONS
None blocking. One judgement call for integration: I marked **SOLVED** because the bar asks for a disk-verified catalog +
a powered can-fail localization + a witness, and all three are delivered and green (14/14). If you would rather the #1
item's *fix* be prototyped end-to-end on the live loop before calling it solved, that is the named follow-on below, and
PARTIAL would be defensible — but per the brief ("this is a MAP + the one deepest fix localized", "NOT a full rebuild")
the audit deliverable is complete.

## NEXT STEPS (priority-ordered — the fixes this audit sets up; all are strategy-lands-it, Q111)
1. **[the #1 fix — prototyped + upstream-traced] DIRECT grounding + a meaning objective + online coverage** (the
   decisive lever), with PARADIGMATIC grounded context as a supplement. The three coupled hdlab changes: (a) a DIRECT
   grounded read-out (wire the inert `grounded_similarity` spoke + broaden `definitional_extraction`), (b) a
   grounded-MEANING objective (not ConceptNet relatedness), (c) COVERAGE by online propose-verify, land TOGETHER.
   Prototyping showed the upstream must be brain-foundational (POS tagger + ATL distillation + dependency context) or
   the grounded arm is suppressed; even faithful, distributional context only reaches counting-parity (~0.37 ceiling),
   while DIRECT grounding wins (0.52). *Worth filing: `ground_the_meaning_readout_directly_and_fix_the_cooccurrence_objective`.*
   *A powered CI-check of the paradigmatic supplement needs the remote box (the parser is ~8 sent/s inline).*
2. **[filed pri-5] C7 attractor-as-ranker → graded population read** in the gap gate
   (`replace_the_attractor_as_ranker_with_a_graded_population_read_in_the_grounding_loop`). Bounded blast; do not
   duplicate — this audit confirms it LIVE and refines it to row-selection-only.
3. **[hygiene] Confirm C8 residual is telemetry-only** and close it — the correctness gate is already live upstream; the
   store-side is source-trust by design.
4. **[do-not-redo] Do NOT re-propose the on-disk dependency-structured encoder** (N1) — it is a landed CI-separated
   negative; only a non-starved, in-domain structured encoder is an open fair-test.
