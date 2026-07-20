# Platform maturity audit: are the base elements brain-sufficient for chain-grade? (5x drill, 2026-07-20)

## HEADLINE

**NOT mature enough yet -- but not for the reason we might fear.** Capacity is MATURE (more than
brain-sufficient) and the discourse/working-memory layer is already SETTLED (proven two-layer,
brain-consistent). Two base elements are genuinely sub-brain: cleanup/pattern-completion is IMMATURE
(measured as a hard step-function, not the brain's graded attractor completion from partial/noisy cues),
and encoding is PARTIALLY mature (the structure/content split is the right brain-faithful idea and the
algebra is correct, but content vectors are similarity-free by default, so generalization beyond pure
symbol-substitution is not yet available). The single most load-bearing MISSING element is an
**error-driven / predictive-coding correction loop that lets the substrate build and repair its own
compositional model from experience** -- today the "model" is a hand/rule-built extractor (glass-box
parser), already independently proven structurally insufficient for trustworthy multi-hop closure
(0.656 oracle-inflated / defensible ~0.41-0.46, both below the 0.70 floor) with no online mechanism to
notice and fix its own errors. **Minimum brain-faithful build order before the next chain-grade attempt:
(1) attractor-style graded cleanup (cheap, narrow-scope, fixes a clearly-measured immaturity), (2) the
error-driven/predictive correction loop wrapping the extractor (the crux -- hardest, but is what
"flexible/improving not static" structurally requires), (3) similarity-structured content vectors for
fillers (grounded/learned embeddings under the existing content-agnostic bind).** Replay/consolidation and
neuromodulation are refinements layered ON TOP of (2), not prerequisites to it -- deprioritize them until
(2) exists. Bottom line: two of the two negative chain-grade attempts being "construction-determined" is
CONSISTENT WITH (not necessarily caused by) this gap -- we built the mature/easy algebraic parts first, as
the architecture doc itself says, and (2) is exactly the missing piece that would make reasoning
data-earned rather than algebra-free.

---

## Method

Per role contract: dispatched 4 parallel Sonnet lit-scan sub-agents (generic scientific-terms-only queries,
no substrate-novel mechanism names off-platform per [[feedback-query-privacy-decomposition]]), one per base
element cluster (WM capacity/binding; CA3 pattern completion; similarity-structured vs random codes; the
4 remaining "missing element" candidates). Synthesized here (Opus) against on-disk substrate measurements:
`notes/vsa_core_ops_empirical_envelope_bind_bundle_unbind_2026-07-19.md` (measured bind/bundle/unbind/cleanup
envelope), `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-17.md` (state-of-mind two-layer arc,
glass-box extraction closure, structure-content factorization CG-candidate), `notes/substrate_capability_map.md`
(replay-already-validated rows, "no current mechanism" gaps list). Calibration penalty applied throughout
(deflate 0.15-0.25 off raw lit-scan reads; novel-synthesis capped at 0.50).

---

## 1. BINDING + CAPACITY -- verdict: **MATURE** (P_deflated=0.60 that capacity is a non-issue for chain-grade)

**Brain side (lit-scan).** Cowan (2001) ~4-chunk attentional-focus limit; Halford/Wilson/Phillips
Relational Complexity theory converges numerically -- adult relational processing falls apart beyond
**quaternary (4-argument) relations**, i.e. ~4 simultaneously-bound arguments is the parallel ceiling.
Oberauer's binding-interference account: the scarce resource is bindings (item-to-role links), not raw
item slots, and they degrade via cross-item interference in a shared similarity space, not simple
slot-exhaustion. Beyond this small parallel core, the brain goes **beyond ~4-7 via SERIAL CHAINING, not a
bigger simultaneous bind**: hierarchical chunking/recoding (center-embedding empirically caps at 3 nesting
levels even in written language), Ericsson & Kintsch's "long-term working memory" (experts use learned
retrieval-cue structures to access LTM serially through STM cues, not an expanded binding buffer), and
hippocampal-PFC generative replay (2023 Cell; 2026 Nat Neurosci) explicitly chains role-bound objects into
compound structures via SEQUENTIAL replay, not one-shot massive parallel binding. Calibrated confidence in
"small parallel core + always-serial-chaining beyond it" = 0.55-0.60 (the "always serial, never larger
parallel bind" half is the weaker, less-tested half of the claim).

**Substrate side (measured, on disk).** The empirical envelope note gives THREE separately-measured
capacity numbers that must not be conflated: (i) content-blind structural code robust through **m=24**
simultaneous role-filler bindings at N=256, first crosstalk drop at m=32 (`math::MM_role_filler_
factorization_compgen_v1`) -- this sits almost exactly on top of the brain's ~4-24 relational-complexity
band (same-limit convergence, not coincidence); (ii) a real bundled-role-filler ceiling of ~128
bindings/bundle at N=2048 (0.9703 at 128, dropping to 0.5687 at 256); (iii) content-correlation x load
interaction -- at brain-realistic low load (m=3) the code tolerates HIGH real-content correlation (GloVe
corr up to 0.597) with no cost, but at higher load (m=10) high correlation collapses factorization
(F_vocab 0.708->0.008). Reconciliation: **the substrate's usable single-bundle capacity at brain-realistic
loads (m<=24) is MORE than brain-sufficient, with wide headroom.** Multi-hop chaining is ALSO already
measured to work via sharding + discrete list-merge (never a joint vector-op across shards -- that HARD_FAILS
50x below random), i.e. the substrate's own working mechanism for "going beyond one bundle's capacity" is
already the same SERIAL/CHAINED strategy the brain uses, not a different mechanism straining against a wall.

**Verdict: capacity is not the base-element gap.** The two chain-grade construction-determinacy findings
are not explained by capacity being too small or too large; the substrate already operates well inside a
brain-matched capacity band and already chains via discrete serial composition the way the brain does.

---

## 2. CLEANUP / ATTRACTOR MEMORY -- verdict: **IMMATURE** (P_deflated=0.55-0.60 that this gap is load-bearing for reasoning over noisy/incomplete real knowledge)

**Brain side (lit-scan).** CA3 autoassociative attractor dynamics (Marr 1971; McNaughton & Morris 1987;
Rolls 2013) recover a full stored pattern from a PARTIAL or degraded cue never seen exactly as a key, via
convergence into learned basins of attraction shaped by the full statistics of prior experience --
graceful degradation across a CONTINUUM of cue quality (direct in-vivo evidence: Neunuebel & Knierim 2014,
"CA3 Retrieves Coherent Representations from Degraded Input"). This is mechanistically distinct from
exact/near-exact-key lookup, which has no route from a cue sharing only PART of a stored structure to the
full pattern, let alone to combinations never jointly stored. Evidence this is load-bearing for REASONING
(not just episodic recall): hippocampal amnesia impairs relational-memory tasks broadly, including
transitive inference and transverse patterning that require combining across partially-overlapping
experiences (Konkel et al. 2008); associative-inference performance is directly linked to pattern-completion
mechanisms, not a separate reasoning module (Zeithamova/Schlichting/Preston program). Calibrated P=0.72 raw,
deflated to ~0.55-0.60 for the strong claim "a memory system with only exact-key cleanup will structurally
fail at reasoning over incomplete/noisy real-world knowledge, regardless of its other components" (the
lesion evidence is correlational, not a clean single-mechanism ablation).

**Substrate side (measured, on disk).** This is the sharpest, most directly falsifiable finding in this
audit: cleanup is independently flagged as **"the WEAKEST leg of the whole noise-tolerance battery"** --
single-observation recovery is perfect (1.0) for sigma in {0...2.0}, then CLIFFS to 0.029 at sigma=3.0 --
"a genuine STEP, not a graceful curve" (`notes/vsa_core_ops_empirical_envelope_bind_bundle_unbind_2026-07-19.md`
Section 3). Every other measured noise axis (MIX partial-slot corruption, WRONG confident-wrong values)
degrades GRACEFULLY with a real HD-over-symbolic advantage (+0.11 to +0.19 depending on regime); cleanup
alone does not. This is an exact structural match to the brain-side gap: our cleanup is closer to a fixed
noise-tolerance-radius lookup than to a CA3-style attractor with basins SHAPED BY EXPERIENCE (no learned
generalization to novel partial-cue combinations was ever built or tested). The one bright spot: modern/
dense (softmax) Hopfield cleanup already measures as HARD_PASS-superior to classical Hopfield (recall=1.000
at load P/N=2.0 where classical is dead), so a graded, higher-capacity attractor primitive is available and
partially validated -- it has just not been wired in as the substrate's actual cleanup path, and no cell
has tested LEARNED (experience-shaped, as opposed to fixed-noise-tolerance) attractor basins.

**Verdict: genuinely IMMATURE, and cheaply fixable.** Swap the cleanup step from exact/near-exact-key
match to a modern-Hopfield-style graded attractor with basins that can be shaped by exposure (not just a
bigger fixed-radius ball) -- this is bounded scope, already has a positive precedent on disk, and directly
targets the one place the substrate diverges structurally (not just quantitatively) from CA3.

---

## 3. ENCODING -- verdict: **PARTIALLY MATURE / borderline IMMATURE** (P_deflated=0.45-0.50 that pure algebraic composition without similarity structure will fail specifically at semantic generalization)

**Brain side (lit-scan).** Cortex encodes concepts as a continuous, metrically-organized similarity space,
not a symbol table: Huth/Nishimoto/Vu/Gallant (2012) map 1,705 categories as smooth shared gradients across
cortex. Grid/place cells are literal metric codes (O'Keefe/Moser), and the SAME metric-coding scheme
repurposes for abstract, non-spatial cognitive maps (Behrens et al. 2018 "What Is a Cognitive Map?";
Whittington et al.'s Tolman-Eichenbaum Machine, 2020) -- this is the mechanism behind interpolation/
extrapolation and structural transfer to novel exemplars, i.e. exactly the "this new thing is LIKE that
known thing" mode of generalization. Analogical mapping is explicitly modeled as similarity-in-relation-space
(Holyoak/Ichien/Lu 2022). Crucially, VSA/HDC/HRR-style random-vector architectures are AGNOSTIC not
ANTI-similarity: they compose correctly whatever content vectors they're handed, but atomic filler symbols
are conventionally assigned deliberately random/dissimilar vectors precisely because no relationship is
assumed -- meaning random-code composition reliably does pure algebraic/combinatorial recombination of
already-known parts, but supplies NO content-level similarity on its own. Hybrid theories (Smolensky
tensor-product binding; Eliasmith's Semantic Pointer Architecture) are exactly this split: content-agnostic
structural binding OVER a similarity-structured content dimension.

**Substrate side.** The already-validated CORE result (`structure-content FACTORIZATION`,
`math::MM_role_filler_factorization_compgen_v1` etc., "STRONG CG-candidate") is precisely the Smolensky/SPA
hybrid architecture: a content-agnostic structural code g (learned, content-blind) bound via native FHRR
over whatever content vectors are supplied -- and it was validated with real GloVe content correlation as
the "content" axis, i.e. the split itself is already brain-faithful and built. The gap is narrower than "no
similarity structure at all": the substrate's bind/bundle primitives don't care whether content is random
or similarity-structured (this was directly tested: factorization holds at LOW load across GloVe
content-correlation 0.015->0.597 with no cost). The real gap is that the substrate's DEFAULT filler
content in most cells to date is either random bipolar codes or supervised/generative content vectors, not
LEARNED similarity-structured (grounded, distributionally-shaped) embeddings as the standing content layer
feeding real-text reasoning. This is a "not yet built as the production content layer" gap, not an
architectural incompatibility -- the hybrid slot for it already exists and is validated.

**Verdict:** the STRUCTURE side is mature (validated, brain-faithful, hybrid-compatible). The CONTENT side
is immature in practice (random/ad-hoc fillers still the default for most cells) but not missing in
principle -- the architecture already has the right slot for similarity-structured content, it just needs
to be populated with a real embedding source (this converges with the earlier "structure-content
factorization" chain-grade candidate and should be read as its natural next step, not a new architectural
requirement).

---

## 4. THE MISSING ELEMENTS -- ranked by necessity for reasoning specifically

Per lit-scan (5 candidates), ranked most->least load-bearing for multi-step reasoning/comprehension (not
episodic memory, not perception):

1. **Error-driven / predictive-coding learning loop -- MISSING, MOST LOAD-BEARING (P_deflated=0.55-0.60 fatal).**
   Predictive coding / free-energy framework (Rao & Ballard; Friston): the brain continuously predicts and
   corrects via prediction error at every level, which is what lets it build/repair a compositional model
   rather than just accumulate co-occurrence statistics (Hebbian/frequency-only association drifts toward
   frequency-dominated, not structurally correct, associations -- exactly the failure mode the lit calls out
   for "correcting the Hebbian mistake" to get compositional generalization). **This is what the substrate
   does not have at all.** The extractor/parser (the "model" reasoning operates over) is a hand-built,
   static, glass-box rule set. It was independently, already, measured and closed as structurally
   insufficient: multi-hop is-a graph closure tops out at 0.656 composed precision (oracle-inflated) /
   ~0.41-0.46 honest, both below the 0.70 trustworthy floor -- "GLASS-BOX NO-LLM EXTRACTION IS STRUCTURALLY
   INSUFFICIENT for trustworthy multi-hop closure," proven oracle-independent. There is no mechanism in the
   current build by which the extractor notices its own errors from downstream reasoning failure and
   corrects itself -- it is exactly the "frequency-count/one-shot" regime the lit-scan contrasts against
   predictive coding. This is separable from capacity/cleanup/encoding: it's an update-RULE gap, not a
   representational-capacity gap.

2. **Discourse-state / working-memory buffer -- NOT missing; already SETTLED and brain-consistent.**
   Zwaan/van-Dijk-Kintsch situation-model theory: comprehension needs a persistent, INDEXED, continuously-
   updated structure (entities/space/time/causation), not just raw capacity -- a distinct representational
   FORMAT requirement, not reducible to WM capacity alone. The substrate already ran this exact question to
   ground empirically (the state-of-mind arc, 5 versions, VET'd each time): the settled architecture is
   TWO-LAYER -- symbolic exact-store wins at working-memory scale (the realistic operating point, robust
   under every fair bit-budget test), HD-bundle superposition wins only at >=8x overload (the durable/
   foundation-memory regime) -- a query-distribution-dependent crossover, not "symbolic always" or "HD
   always." This is the ONE candidate missing-element in the lit-scan list that the substrate has already
   built, drilled 5x, VET'd, and settled. Verdict: MATURE for this element specifically (though its value
   is currently capped by feeding on the same immature extractor from item 1).

3. **Neuromodulation (surprise/reward gating of learning rate) -- MISSING but lower urgency (P_deflated~0.25-0.30 fatal).**
   Dopamine RPE (Schultz) / ACh-NE uncertainty gating (Yu & Dayan): mostly an efficiency/credit-assignment
   layer ON TOP of an error-driven loop, not independently fatal -- collapses substantially into item 1
   (it's the gain-control on the correction signal). Deprioritize until item 1 exists; there is nothing to
   gate yet.

4. **Consolidation / offline replay -- PARTIALLY BUILT, not missing (P_deflated~0.20-0.25 fatal for reasoning specifically, higher ~0.5-0.6 for durable knowledge accumulation).**
   CLS theory / sharp-wave-ripple replay: prevents catastrophic forgetting and extracts cross-episode
   schema, but is a systems-level solution to a DIFFERENT problem (interference over time), not required
   for a single reasoning episode performed in one sitting. The substrate ALREADY HAS a validated version
   of this: "Random replay BWT recovery: +0.66 to +0.73 at K=4" and "Pre-shift neutral replay ... zero
   measurable cost" are both already-validated capability-map rows. What's genuinely absent is full
   sleep-style OFFLINE STRUCTURE-BUILDING/schema-extraction replay (capability-map explicitly lists "Sleep-
   style memory consolidation" as an open, untested question) -- but this is a refinement, not a
   reasoning-blocking gap.

5. **Grounding / sensorimotor referents -- CONTESTED, weakest necessity claim (P_deflated~0.15 fatal).**
   Embodied-cognition claims (Barsalou) are substantially challenged by congenitally-blind cognition studies
   and symbol-ungrounding critiques (Dove 2015) -- structural language, logic, and theory-of-mind reasoning
   develop largely intact without sensorimotor/visual grounding. Some referential grounding likely still
   matters (amodal/relational grounding, not necessarily sensorimotor), but this is NOT the crux. This
   converges with the substrate's own already-closed finding this session that vision is not a grounding
   fix for the reader ("dictionary grounds concrete vocab fine at relational AND perceptual/sensorimotor
   levels") -- independent convergence that sensorimotor grounding specifically is not the bottleneck.

---

## 5. VERDICT

**Is the platform mature enough for chain-grade?** Mostly-no, but narrowly and specifically -- not a
blanket "too immature," and not "task/test-design is the whole story" either. Three of five base
elements check out fine (capacity: mature with brain-matched headroom; discourse/WM buffer: settled,
brain-consistent, already built; replay: partially built, adequate for now). Two do not: cleanup is a
hard step-function where the brain has graded, experience-shaped attractor completion (cheaply fixable --
a validated modern-Hopfield primitive already exists on disk, just not wired in as the default cleanup
path), and the substrate has NO error-driven/predictive-coding loop that lets its compositional model
(the extractor) learn and repair itself from experience -- today that model is a static, hand-built,
already-proven-insufficient rule set. **This second gap is the single most load-bearing missing element.**
It is a sufficient, independent explanation for why every chain-grade attempt to date has either been
construction-determined (the reasoning algebra is free and correct, so any well-formed test of it passes
by construction) or bounded by a frozen ~0.557 extractor with no path to improve except more hand-tuning:
there is no learning loop in the loop.

**Minimum brain-faithful build order (before the next chain-grade attempt):**
1. **Attractor-style graded cleanup** (swap exact/near-exact-key cleanup for a modern-Hopfield-style
   attractor with basins shaped by exposure, not a fixed noise radius). Cheapest, narrowest, has a
   positive precedent already on disk (`T3/EXP_modern_hopfield_beta_capacity_gpu_v1` family). Fixes a
   clean, already-measured immaturity.
2. **The error-driven / predictive correction loop wrapping the extractor** (predict an interpretation,
   compare against a coherence/downstream-success signal, correct the model on the gap -- NOT another
   hand-written rule, and NOT the already-closed scene-coherence-as-training-signal design specifically,
   whose null result (delta=0.000 even at gold-perfect oracle) closed one candidate implementation of this
   idea but did not close the general requirement). This is the crux and the hardest of the three; it is
   what "flexible/improving not static" structurally demands, and its absence is sufficient on its own to
   explain the construction-determined chain-grade results.
3. **Similarity-structured content vectors for fillers** (a learned/grounded embedding source populating
   the CONTENT half of the already-validated structure-content split, replacing ad-hoc/random content
   vectors as the production filler layer). Needed for generalization beyond pure symbol-substitution
   algebra; the architectural slot for this already exists and is validated, it is not populated yet.

Neuromodulation and full offline-consolidation/replay are refinements layered on top of (2) -- do not
build them before (2) exists; there is nothing yet to gate or replay in a structurally new way.

---

## Cheap decisive test

Before any further chain-grade attempt: run a **cleanup-swap smoke** (item 1 above) -- replace the exact-
key cleanup path in the live reasoning-map with the already-validated modern/dense-Hopfield cleanup, re-run
the existing noise-tolerance battery (`exp_read_bridge_noise_tolerance_hd_vs_symbolic_v1`-style cell) at the
same sigma sweep. HARD-PASS = the cleanup curve becomes graceful (no cliff between sigma=2.0 and sigma=3.0,
recovery >0.5 at sigma=3.0 rather than 0.029) with recall parity or better at sigma<2.0. HARD-FAIL = cliff
persists at the same location regardless of cleanup family (would mean the step is a property of the
codebook/dimensionality, not the cleanup rule -- a deeper and more surprising finding). This is cheap
(reuses an existing cell + swaps one component), decisive, and directly tests the ONE clearly-immature
element identified in this audit before any bigger investment in the harder item-2 build.

## Falsifiable predictions

- **HARD-PASS (cleanup, item 1):** modern-Hopfield-style cleanup swap converts the sigma=2.0->3.0 cliff
  into a graceful curve (recovery(sigma=3.0) > 0.3, up from 0.029), with recall at sigma<=2.0 not worse
  than the current exact-key baseline.
- **HARD-FAIL (cleanup, item 1):** recovery(sigma=3.0) stays < 0.10 regardless of cleanup family tested ->
  the step is a codebook/dimensionality property, not fixable by cleanup-rule choice alone; escalate to a
  codebook-redesign question instead.
- **HARD-PASS (item 2, error-driven loop, general form):** ANY implementation of a predict-compare-correct
  loop around the extractor (not necessarily the closed SCV design) produces a measurable, held-out
  precision improvement from raw text with NO gold labels, that (a) is not reproduced by a frozen/no-update
  control, and (b) survives a scrambled/degraded-signal must-fail control (removing the correction target
  should make the learned weight regress). This is the single test that would flip this audit's "MISSING"
  verdict to "built."
- **HARD-FAIL (item 2):** every well-designed correction-signal candidate (coherence, redundancy,
  downstream-task success) produces delta<=0 at gold-perfect oracle quality, mirroring the SCV's exact
  0.000 result -- would indicate the gap is not "which signal" but something deeper about how corrections
  propagate into the current extractor's parameter space, and would need its own dedicated drill.
- **HARD-PASS (item 3, encoding):** swapping ad-hoc/random content vectors for a learned/grounded
  embedding source in the already-validated structure-content split produces measurable generalization to
  semantically-near-but-unseen fillers (not just held-out role-COMBINATIONS of already-known fillers,
  which the current CG-candidate already proves) at 3-seed-stable margin >0.05 over the random-content
  control.
- **HARD-FAIL (item 3):** no generalization gain from similarity-structured content over random content at
  matched held-out-combination performance -> would mean the earlier CA3/similarity-structure literature
  read does not transfer to this substrate's specific binding scheme, a genuinely surprising negative
  worth its own drill.

## Cross-thread synthesis

- Converges with, and gives a mechanistic REASON for, the standing observation that "reading-axis
  STRUCTURAL signals work, SEMANTIC signals fail" (2 CGs vs repeated HARD_FAILs this session,
  [[feedback_reading_axis_structural_signals_work_semantic_fail_2CGs_2026-07-19]]): structural signals are
  things the hand-built parser can already represent and check exactly; semantic/plausibility signals are
  exactly the kind of thing an error-driven predictive loop is supposed to supply, and we don't have one --
  so of course attempts to bolt on a semantic check via cosine/animacy/scene-coherence keep failing to
  TRAIN (the SCV's decisive 0.000-at-gold-oracle result), because there is no general-purpose correction
  mechanism to receive the signal into, only ad-hoc one-off feature designs each time.
- Converges with the glass-box extraction closure (`notes/research_...`/atom acbc6439 family):
  "GLASS-BOX NO-LLM EXTRACTION IS STRUCTURALLY INSUFFICIENT for trustworthy (0.70) multi-hop is-a closure
  -- PROVEN ORACLE-INDEPENDENT." That closure is this audit's item-1 (error-driven loop) gap observed from
  a different angle: a static extractor cannot be patched into trustworthiness by better hand rules alone;
  it needs a correction mechanism, which is the PIVOT's own stated invariant (external tools for the
  FOUNDATION are fine; RUNTIME REASONING stays glass-box) -- meaning item 2's correction loop must itself
  be built glass-box (predict/compare/correct primitives, not an external LLM at inference), which is a
  harder ask than just "get better labels," and is exactly why it is ranked as the crux.
- Converges with the state-of-mind arc's own settled two-layer answer for item 4's "discourse buffer"
  candidate -- this audit independently arrives at the literature's prediction (situation-model = a
  distinct FORMAT requirement, not just capacity) and finds the substrate already built and VET'd exactly
  that architecture, unprompted by this lit-scan. This is a reassuring cross-check: where the substrate HAS
  invested brain-drill-first effort, it lands on the brain-predicted answer.
- Directly informs the strategic fork already on the table in the backup doc (compounding vs more-data vs
  deeper-parser): this audit's ranking says NONE of those three are the highest-leverage move right now --
  the cleanup swap (item 1, cheap) and the correction-loop build (item 2, the actual pivot target) sit
  ABOVE all three, because compounding/more-data/deeper-parser all still terminate in the same static,
  self-uncorrecting extractor.

## Substrate-product implications

A product built on the current base (capacity fine, cleanup brittle, no self-correction) can ship reliably
for tasks that are pure algebra over already-correct extracted structure (exact chained retrieval, auditable
multi-hop lookup on a hand-curated or externally-sourced knowledge graph) -- this is a real, sellable
differentiator (glass-box, auditable, no hallucination by construction) and does not require items 1-2 to
be solved first. It CANNOT yet ship reliably for "reads noisy real text and gets smarter/more accurate the
more it reads" -- that specific promise (the USER's standing "flexible/improving not static" requirement)
structurally depends on item 2, which does not exist yet in any form, closed candidate or otherwise. The
cleanup fix (item 1) is a near-term robustness/reliability upgrade the product can absorb now, cheaply,
without changing the roadmap. The encoding gap (item 3) mainly affects how well the product handles novel
vocabulary/paraphrase at inference (graceful near-miss generalization) versus needing exact vocabulary
match -- a real but secondary limitation, not a blocker for the current "auditable retrieval/reasoning"
positioning.

## Citations (verified count)

34 distinct citations across the 4 parallel sub-agent lit-scans (author/year/venue-traceable, as reported
by each sub-agent; not independently re-fetched by this synthesizing pass -- standard lit-scan provenance,
per [[feedback-lit-scan-calibration-penalty]]):
Cowan 2001; Halford/Wilson/Phillips 1998; Oberauer 2019; Ericsson & Kintsch 1995; Entropy 2020
(center-embedding limits); Cell 2023 (hippocampal-PFC generative replay); Nat Neurosci 2026 (ripple-
coordinated compositional replay); Treisman Feature Integration Theory; Marr 1971; McNaughton & Morris
1987; Rolls 2013 (CA3 quantitative theory); Neunuebel & Knierim 2014; Konkel et al. 2008; Eichenbaum 2004;
Schapiro et al. 2017 (CLS); Kumaran & McClelland (transitive inference); Zeithamova/Schlichting/Preston
2018; developmental-amnesia case study (Hipp 22606); Huth/Nishimoto/Vu/Gallant 2012; Whittington et al.
2020 (Tolman-Eichenbaum Machine); Behrens et al. 2018; Bellmund et al. 2021; Holyoak/Ichien/Lu 2022; HDC/
VSA survey (Kleyko et al.); Crawford & Eliasmith 2016 (SPA); Smolensky 1990 (tensor-product binding);
neuro-symbolic grounding-vs-compositionality (arXiv); Rao & Ballard 1999 / Friston free-energy (predictive
coding); PMC9586412 (error-driven hippocampal correction); PMC 40667278 (interleaved replay prevents
forgetting); Wilson & McNaughton (replay); Zwaan/Langston/Graesser 1995 (event-indexing model); van Dijk &
Kintsch (situation models); Schultz (dopamine RPE); Yu & Dayan (ACh/NE uncertainty); Aston-Jones & Cohen
(LC-NE); Barsalou (perceptual symbol systems); Dove 2015 (symbol-ungrounding critique); PMC11529626 (blind
cognition / ToM without visual grounding).

Plus on-disk substrate evidence (not literature, directly re-read this pass): `notes/vsa_core_ops_empirical_
envelope_bind_bundle_unbind_2026-07-19.md` (full envelope table), `notes/substrate_capability_map.md`
(replay/consolidation rows), `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-17.md` (state-of-mind
arc v1-v5, structure-content factorization CG-candidate, glass-box extraction closure v1-v4).
