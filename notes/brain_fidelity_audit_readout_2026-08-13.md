# Brain-fidelity element audit -- word-meaning read-out (2026-08-13)

Trigger: blind hand-score of GROUNDED_MEANING read-out, 3 MEANINGFUL / 19 RELATED / 78 NOISE
(`notes/director_handscore_readout_v1_2026-08-13.md`). Failures are topical co-occurrence
(`whisky->wedding`, `aphotic->marry`, `confidence->talking`, `banana->people`,
`checklist->joe`). Per standing discipline: a wall triggers a brain-fidelity element audit,
not a workaround.

Files read (READ ONLY, not modified): `hdlab/reading_grounding_loop.py` (full, 1687 lines),
`hdlab/grounding_acquisition_loop.py` (lines 1-430), `hdlab/gap_detector.py`,
`hdlab/coreference_resolver.py`, `hdlab/cleanup_family.py`, `data/capability_registry.jsonl`.

## 1. The pipeline off disk

1. **Candidate context representation.** `context_vector(window_text)`
   (`hdlab/grounding_acquisition_loop.py:117-134`): tokenize to content words
   (`content_words`, same file `:106-114`, stopword-filtered, len>2), for each word draw a
   `hashlib.sha256`-seeded fixed bipolar vector, sum, `sign()`. This is a **Kanerva
   random-indexing / BEAGLE-style bag-of-content-words bundle** -- explicitly named as such in
   the docstring. It carries no grammar, no roles, no word order, only "which other words were
   nearby."
2. **Per-word running profile.** `ConceptSpace.observe` / `seed_from_bundle`
   (`hdlab/reading_grounding_loop.py:227-236`) accumulates a raw sum of `context_vector`s per
   lemma; `ConceptSpace.bundle` (`:259-263`) returns `sign(sum)`. This is the anchor pool.
3. **Meaning selection metric.** `canonicalize` (`:406-445`) and its vectorized twin
   `canonicalize_fast` (`:448-510`): cosine (`_cos`, `:399-403`) between the target's bundled
   context sum and every *eligible* anchor's bundle, **argmax**, admit iff
   `best_cos >= SENSE_MATCH_THRESH=0.45` (`:108`). No-match returns the lemma itself (refused
   downstream as `TAUTOLOGY_NO_ANCHOR`, `:875-930`).
4. **Gate / admission.** `_make_grounding_gate` / `_make_pbv_grounding_gate`
   (`:882-1003`) refuse self-tautology and closed-class objects (`hdlab/closed_class_lexicon`),
   otherwise the accepted "meaning" **is exactly the nearest-anchor-by-cosine-of-bag-of-words**.
5. **Storage.** `checkpoint` (`:1024-1122`) writes `(lemma, GROUNDED_MEANING, canon_obj)` into
   `HDFactStore` (`state.store.store(...)`, `:1075`). `HDFactStore` here is a passive ledger for
   an already-decided answer, not a retrieval mechanism that participates in the decision.
6. **PBV wrapper (2026-08-12 addition).** `make_pbv_fns` (`:525-700`) builds
   `propose_fn`/`verify_fn` from `_encounter_best` (`:643-647`), which is **`canonicalize_fast`
   again**, called per-encounter instead of once on a summed trace. `propose_fn` (`:684-688`)
   returns the cosine-argmax winner; `verify_fn` (`:690-694`) returns
   `encounter_best == hypothesis.obj`, i.e. it re-runs the identical cosine argmax on a fresh
   encounter and checks equality with the standing hypothesis. `Library.flag`
   (`hdlab/grounding_acquisition_loop.py:236-321`) then applies Bush-Mosteller strength update
   (`pbv_update_strength`, `:218-226`) and abandon-and-repropose (`:306-321`) on top of that
   verdict.
7. **Read-out stability fixes (F1/F3, default OFF).** `ReadoutConfig` (`:321-379`) replaces the
   magnitude test with a field-relative z-score of the *same cosine array* (`_readout_statistic`,
   `:382-396`); `ConceptSpace.freeze()`/`FrozenAnchorSpace` (`:271-319`) snapshot the anchor
   matrix so encounters compare against a stable field. Both operate strictly *inside* the same
   cosine-of-bag-of-words space; neither changes what the decision variable is.

## 2. Is the meaning selected by similarity in a co-occurrence-derived space? YES.

Every step that decides *what a word means* -- proposal (`canonicalize`/`canonicalize_fast`),
informativeness gating (`PBV_INFORMATIVE_MIN` via the same call), verification
(`verify_fn` calling the same call again), and final admission (`_make_pbv_grounding_gate`) --
routes through one function, `canonicalize_fast`, whose decision variable is cosine similarity
between two bags-of-nearby-content-words. The PBV machinery (propose/verify/abandon/strength)
wraps this metric in literature-shaped control flow but never substitutes an independent
evidence channel for the verify step: propose and verify are the *same statistic* computed
twice. A systematic bias in that statistic (thematic/co-occurrence proximity, not synonymy or
definitional identity) cannot be self-corrected by re-measuring itself.

## 3. Per-element table

| Element | Our SHAPE / POSITION / METRIC | Brain's SHAPE / POSITION / METRIC | Divergence | Severity |
|---|---|---|---|---|
| Meaning candidate space | Bag-of-nearby-content-words bipolar bundle (`context_vector`); position: computed once per sentence occurrence, pooled into `ConceptSpace`; metric: raw co-occurrence, no roles/order | ATL hub integrates convergent **multimodal features** (perceptual, motor, linguistic) from spoke regions into a graded, modality-invariant conceptual space (Patterson et al. 2007 *Nat Rev Neurosci*; Lambon Ralph et al. 2017 *Nat Rev Neurosci*) -- similarity is feature/property-based, not word-adjacency-based | Ours has no spoke/feature layer at all; "similarity" = context overlap, which brain research explicitly does NOT equate with conceptual similarity | **CRITICAL** |
| Meaning selection metric | `argmax(cosine(target_bundle, anchor_bundle))` (`canonicalize_fast`) sitting exactly at the decision point | The brain never selects a referent by nearest-neighbor distance in a global distributional space; hub integration + relational/referential binding constrain the choice long before any similarity computation, and similarity there is over converged conceptual features, not text co-occurrence | A similarity-proxy sits where the brain reasons (hub integration + relational constraint satisfaction) -- textbook instance of the standing "similarity-proxy where the brain reasons = architectural fault" rule | **CRITICAL** |
| Relational/referential binding | Absent as a proposal mechanism. `HDFactStore` triples are written only AFTER cosine argmax decides the object (`checkpoint:1075`); the fact store never participates in proposing candidates | Hippocampus supports rapid, one/few-shot **relational binding** of a novel word to a specific referent/event via pattern separation + completion over structured (role-bound) codes, not accumulated averages (Warren et al. 2014's schema-coherence guard is itself modeled on this) | We have the right organ (`HDFactStore` (s,r,o) triples + `gap_detector.ca3_match_score` CA3/CA1 attractor, `hdlab/gap_detector.py:~94-118`) but use it only as a passive ledger, never as the retrieval/proposal substrate | **HIGH** |
| Sensorimotor grounding | None wired into this loop. `context_vector` reads only text tokens; no perceptual/action feature channel found in `reading_grounding_loop.py` or `grounding_acquisition_loop.py` | Perceptual/motor simulation contributes grounded features to concepts (Barsalou 1999 *perceptual symbol systems*; norms e.g. Lancaster/Brysbaert) | Spokes are entirely absent -- the "hub" (ConceptSpace) has nothing but more text to converge over, so it cannot help but reduce to co-occurrence | **HIGH** (structural absence, not a tuning gap) |
| Propose-then-verify control flow (SHAPE) | `Hypothesis` (one carried hypothesis, no runner-up score, Bush-Mosteller strength, abandon-and-repropose in one act) -- `grounding_acquisition_loop.py:162-227,236-340` | Medina 2011 *PNAS*; Trueswell et al. 2013 *Cog Psych* "Propose but Verify"; Woodard et al. 2016; Stevens et al. 2017 "Pursuit" -- exactly this shape (single hypothesis, abrupt abandon, persisting strength) | SHAPE and POSITION (online, per-encounter) genuinely match the literature -- this is a real fidelity win, not a proxy | **none (correct)** |
| Propose-then-verify evidence channel (INDEPENDENCE) | `verify_fn` re-runs `canonicalize_fast` on a fresh encounter and checks equality with the standing hypothesis (`reading_grounding_loop.py:690-694`) -- verification uses the SAME metric as proposal | In the human experiments, verification is against an independent referent/scene/discourse cue -- a channel that can disagree with the proposal mechanism and therefore actually correct it | Verify is not an independent check; it is the proposal metric asking itself the same question twice, so PBV's abandon-and-repropose machinery cannot escape a systematic bias in the underlying metric | **CRITICAL** (this is why PBV wiring does not fix the topical-relatedness failure even where it is wired in) |
| Read-out stability fixes (F1 z-gate, F3 freeze) | Operate strictly inside the cosine-of-bag-of-words space: they change WHICH scores are compared or WHEN the field is snapshotted, not WHAT is compared (`ReadoutConfig`, `ConceptSpace.freeze`) | N/A -- stability of an argmax is not a brain construct; the brain's analogue would be attractor convergence stability, downstream of a correctly-shaped comparator | Confirms the MEMORY-recorded finding: read-out stability and meaning quality are decoupled. F1/F3 make the WRONG argmax more repeatable, not more correct | **MEDIUM** (already flagged, reconfirmed by this audit) |

## 4. The decisive question

**Does the brain ever select a word's meaning by nearest-neighbor in a distributional
(co-occurrence) space? No.** The literature converges on two things a nearest-neighbor
co-occurrence readout cannot do: (a) integrate convergent, feature-based, modality-spanning
information into a single conceptual similarity space (ATL hub-and-spoke), and (b) verify a
proposed meaning against an evidence channel independent of the proposal itself
(propose-but-verify). Both are exactly the ingredients missing from `canonicalize_fast`.

**The one structural change:** stop letting `canonicalize_fast`'s cosine-of-bag-of-words be
the function that both PROPOSES and VERIFIES a meaning. Concretely: (1) make meaning candidates
**structured relational facts** about the word (the predicate-argument roles/relations it
participates in, extractable via `thematic_role_labeler` / the definitional-extraction
pipeline) rather than raw co-occurring-word bundles, stored and retrieved through
`HDFactStore`'s (s,r,o) shape; (2) replace the plain cosine argmax comparator with
`gap_detector`'s CA3/CA1 attractor match (`ca3_match_score`) or `cleanup_family`'s structured
cleanup primitives operating over that **relational codebook**, which is a genuinely different
SHAPE (bound-role cleanup, not bag-of-words similarity) even though it is still ultimately a
margin/cosine computation under the hood -- the point is WHAT is being compared, not whether a
dot product is involved; (3) source the PBV `verify_fn`'s evidence from a channel that is NOT
`canonicalize_fast` -- e.g., `coreference_resolver`'s Centering/Cb-style relational,
constraint-based referent selection (grammatical role, recency, gender/number compatibility,
Principle B; `hdlab/coreference_resolver.py:200-429`) as the model for "propose/confirm a
specific referent from structural constraints," not vector similarity. This is a genuinely
non-proxy SHAPE already built and validated in this codebase for a cognate problem
(referent selection), which is exactly the kind of adjacent organ the standing "reuse, don't
build a parallel organ" rule points at.

## 5. Literature -- specific failure shape (generic-term web search, deflated per calibration
discipline; P estimates below are capped at 0.50 for anything synthesized rather than directly
sourced)

- **Association vs. similarity is a named, well-documented distributional-semantics failure
  mode.** Search on "distributional semantics topical relatedness vs synonymy critique" and
  "distributional embeddings hypernymy association vs similarity" both surfaced the same
  finding independently: co-occurrence-trained vectors "capture more semantic association than
  semantic similarity" and cannot by themselves distinguish synonymy/hypernymy from antonymy,
  meronymy, or broad thematic relatedness (car-driver, hot-cold, cat-dog all score similarly
  under cosine). This is precisely the `whisky->wedding` failure shape. P(this is the correct
  causal diagnosis for our failure) ~0.45 (deflated from what would otherwise read as ~0.7;
  the mechanism match is exact, deflation is because I have not run a matched ablation proving
  it, only code-path + literature correspondence).
- **ATL hub-and-spoke (Patterson, Nestor & Rogers 2007, *Nature Reviews Neuroscience*, "Where
  do you know what you know?"; extended by Lambon Ralph and colleagues, e.g. 2017 review)**:
  conceptual similarity is computed over convergent multimodal FEATURES, not raw co-occurrence.
  Well-established, high confidence this is the standard model (P~0.6, capped per novel-synthesis
  rule since I am mapping it onto our architecture, not citing a paper that makes this mapping).
- **Trueswell, Medina, Hafri & Gleitman 2013, *Cognitive Psychology*, "Propose but verify: Fast
  mapping meets cross-situational word learning"** (Medina et al. 2011 *PNAS* is the companion
  eye-tracking paper): single-hypothesis, abrupt-switching, propose-then-verify word learning.
  Directly cited already in our own code comments, confirmed present via search. High confidence
  this literature exists and matches our SHAPE claim (P~0.55, capped).
- HARD-FAIL threshold for the association-vs-similarity diagnosis, were it tested directly: if a
  matched ablation that swaps `canonicalize`'s comparator for a relational-fact-based comparator
  (Sec. 4) does NOT reduce topical-neighbor errors (e.g., `whisky->wedding`-class errors) on a
  held-out hand-score relative to the current cosine-argmax baseline, the association-vs-
  similarity diagnosis is refuted as the dominant cause and the search must look elsewhere
  (e.g., corpus composition, extraction noise).

## 6. Owned capabilities that are NOT similarity proxies (registry query)

`data/capability_registry.jsonl` (123 rows, READ ONLY): `hd_fact_store` is registered and
`WIRED` (`status: wired_prior_to_07-25_audit`, used by 15+ experiments,
`current_best_for: "fact retrieval reaching the ARC frontier"`). `coreference_resolver`,
`gap_detector`, and `cleanup_family` did **not** surface in `--serves` queries for "word meaning
disambiguation" / "relational binding antecedent retrieval" (0/123 matches for both), and a
direct id-grep across those three plus `hd_fact_store`/`thematic_role_labeler`/`fhrr` found only
`hd_fact_store`. This means the registry likely does not have entries for
`coreference_resolver` / `gap_detector` / `cleanup_family` at all -- consistent with the
already-logged registry-leaky finding (`feedback_tighten_capability_registry_version_control_
audit_found_leaky_2026-08-11`). These three modules exist on disk, are non-trivial and
purpose-built for exactly the non-proxy mechanisms named in Sec. 4 (relational referent
selection, structured attractor cleanup over bound codes), but are currently **invisible to
query-before-build** discipline. Recommend a registry-audit pass add all three before any build
against this finding starts, so the reuse doesn't get re-discovered by hand a second time.

## 7. What I could NOT verify

- Which mode (`pbv=False` plain `canonicalize` vs `pbv=True` PBV path; `readout=None` legacy vs
  `operating_readout()` F1/F3) produced the specific 3/19/78 hand-scored run referenced in the
  trigger. The finding in Sec. 2-3 (verify uses the same metric as propose) applies whenever PBV
  is active; if the hand-scored run used the plain (non-PBV) `checkpoint(pbv=False)` path, the
  PBV-specific "verify is not independent" divergence did not fire in that particular run and
  the CRITICAL item most directly explaining the observed data is simply "meaning selection IS
  cosine-of-bag-of-words argmax" (Sec. 2), not the PBV-verify item.
  Concurrent agents own `experiments/exp_grounding_text_vs_mechanism/` and the harness that
  produced the hand-score; I did not read that harness (out of this audit's read set / risk of
  colliding with `quality_readout`/`readout_sheet`/`readout_verdict` agents active this session).
- Whether Lancaster/Brysbaert sensorimotor norms (referenced in the task prompt as "already on
  disk") are wired into ANY hdlab module. I did not find them imported in
  `reading_grounding_loop.py` or `grounding_acquisition_loop.py`, but I did not exhaustively grep
  the full `hdlab/` tree for them, so "wired nowhere" is an inference from two files, not a
  verified absence.
- Whether `gap_detector.ca3_match_score`'s codebook, in current production use, is built over
  genuinely STRUCTURED (role-bound) facts or over comparably flat bundles -- I read its
  docstring and margin computation but not the codebook-construction call sites outside this
  file's own imports, so "the right SHAPE already exists" (Sec. 3/4) is a claim about the
  primitive's design, not a verified claim about what codebook it is fed in the reading-loop's
  own current wiring (which, per Sec. 1 point 5, does not feed it word-meaning candidates at
  all today).
- I did not run any code or experiment; this is a static code-and-literature audit only, per the
  read-mostly / no-code-modification constraint on this task.
