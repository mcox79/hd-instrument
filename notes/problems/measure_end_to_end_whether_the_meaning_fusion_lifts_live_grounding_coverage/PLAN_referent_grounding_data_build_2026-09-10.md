# PLAN (LOCKED 2026-09-10, pre-compaction) -- THE REFERENT-GROUNDING DATA BUILD is the next focused build

Resume entry point for this problem. Read this + SOLVED.md (running record) + BRAIN_SIGNAL_BF_TRACE.md (the framing)
FIRST after compaction. Reverify: `.venv/Scripts/python.exe verification/test_meaning_fusion_live_coverage.py`
(34/34, W1-W36). Bash cwd resets -> prefix `cd /c/AI/hd-instrument &&`, use `.venv/Scripts/python.exe`, cap
OMP/OpenBLAS/MKL/NumExpr=2.

## WHY THIS IS THE PLAN (the converged conclusion -- do NOT re-litigate)
After 36 witnessed experiments the whole investigation converged on ONE cause, agreed from three sides:
- MECHANISM: the brain's meaning is a GROUNDED REFERENT CONCEPT = the ATL hub's CROSS-MODAL FEATURE CONVERGENCE
  over the referent's multimodal experience; the hub metric is cross-modal FEATURE-CORRELATION, NOT text
  co-occurrence (Cox-Rogers 2024). (Prediction was a WRONG TURN -- a downstream comprehension PROCESS, not the
  substance of meaning; W34/W35 measured it real-but-weak. Do not pursue prediction.)
- MODELLING: every text-derived lever is EXHAUSTED (grow-by-reading bounded W20; targeted reading null W27;
  confidence/recollection W23/25/26 negative; differentia uncapturable W24; read-Hearst is-a null W28; ConceptNet
  genus counterproductive W29; componential ranking-win-but-no-live-transfer W32/W33; predictive real-but-weak
  W34/W35; concreteness-gated cross-modal hub does not beat the ungated fusion W36).
- DATA: the referent modalities that would make the hub brain-faithful are DEMO-COVERAGE -- visual = CLIP for ~21
  QuickDraw words (no synonym pairs, ~0 SimLex overlap); Binder componential = ~534 words (10% of the query vocab).
The fully-BF live chain sits at ~41-44% of the brain (68% oracle). grounded(Lancaster perceptual spoke)+SEQ(text
spoke) IS the best cross-modal referent hub the AVAILABLE DATA supports. The limit is REFERENT-GROUNDING DATA
(symbol-grounding / embodiment), NOT modelling. The frontier is a FOUNDATION DATA-BUILD, not a new model.

## THE BUILD (item 1 -- do this after compaction, as a focused build)
GOAL: add a REAL second referent modality (perceptual/visual) at vocabulary scale, rebuild the cross-modal hub with
it, and test whether REAL referent grounding lifts synonymy where text-derived signals could not.

STEP A -- ACQUIRE vocabulary-scale visual referent features (FOUNDATION build, offline, admissible; owner-authorized;
may need owner setup for images/CLIP -- confirm environment has CLIP + an image source before coding):
  - Reuse the EXISTING infra: `experiments/exp_visual_grounding_coherence_v1.py` already does CLIP-at-ingest over
    QuickDraw (CC-BY); `data/exp_visual_grounding_coherence_v1_cache/clip_<word>.npy` are per-word CLIP vectors.
  - Scale it: CLIP-embed images for the SimLex-999 + SimVerb-3500 + anchor-pool vocabulary. QuickDraw has ~345
    drawable categories (common nouns); fall back to a photo source (Open Images CC-BY / Wikimedia PD) for the rest.
    Average multiple exemplars per word -> one visual-referent vector per word. CLIP touched ONLY at ingest (frozen
    asset; NO external model at runtime -- the invariant). Cache as per-word .npy, like the existing cache.
  - REPORT the achieved coverage of the query vocab (this is the make-or-break: read-Hearst 15%, ConceptNet 67%,
    Binder 10%, visual-so-far 21 words -- need materially higher for a powered synonymy test).

STEP B -- REBUILD the cross-modal hub with the real visual spoke (modelling; solver scope):
  - Pattern: `experiments/exp_meaning_fusion_crossmodal_hub_v1.py` (W36) -- but add the VISUAL referent spoke as a
    THIRD channel: hub = converge grounded(Lancaster) + SEQ(text) + VISUAL(CLIP referent), concreteness-gated
    modality precision (grounded/visual = perceptual spokes, trust for concrete referents).
  - BF: cross-modal convergence (the hub); the Cox metric = cross-modal FEATURE-CORRELATION -- consider the
    correlated-subspace convergence, not mere concatenation. Convergent-cue Bayes fusion (Ma/Pouget). Cosine readout.

STEP C -- MEASURE (the decisive test): on the VISUAL-COVERED SimLex+SimVerb subset (and, if coverage allows, the live
  anchor-pool coverage-quality frontier): does adding the REAL visual referent spoke lift synonymy identity over
  grounded+SEQ, with the KNOWLEDGE-SHUFFLED (shuffled-visual) twin LOSING? This is the direct test of "does real
  referent grounding help where text-derived signals could not." If YES -> the referent-data lever is real and the
  path is scale the visual coverage. If coverage stays too low for power -> the ceiling is confirmed data-bound and
  the honest end is: text-grounding maxed; further gain requires embodied/multimodal referent data at scale.

## SCOPE (hard -- unchanged)
Write ONLY experiments/, verification/, this problem folder. NO hdlab/ (Q111 -- strategy lands). Never set
owner_verdict. SimLex-999 (+SimVerb) identity gold; NO WordNet in any SimLex-graded channel (CLIP/QuickDraw/Lancaster/
concreteness are non-circular foundation assets; CLIP frozen at ingest, never at runtime). Every load-bearing claim:
info-free twin LOSES + CI on the loop's own population; keep SOLVED.md ASCII-only + `tools/problem_ledger.py --check`
clean; add every new cell to `verification/test_meaning_fusion_live_coverage.py`. If a tool call is denied, STOP + report.

## LANDABLES + RESIDUALS (bank / hand to strategy, independent of item 1)
- PROVEN grow-by-reading (W20, +0.16->+0.26 CI-sep, twin losing) -- the live lever that works; flip SEQ live + enable
  grow-by-reading in canonicalize (strategy/Q111; wire spec in SOLVED.md ADDENDUM).
- The GLASS-BOX lemmatizer (W30) removes the last WordNet dependency (WordNet-morphy in `lemma_word`, pipeline-wide);
  needs a curated NON-WordNet base-form word list to be lossless (deepest BF-purity residual; FULL_CHAIN_BF_AUDIT.md).

## STATE
Witnesses 34/34 (W1-W36). Ledger clean. FULL_CHAIN_BF_AUDIT.md + BRAIN_SIGNAL_BF_TRACE.md current. Nothing
owner-marked DONE. [[grounded-similarity]] Lancaster = the perceptual spoke. This plan supersedes the earlier
PLAN_100pct_BF_then_prove_knowledge.md (Phase A/B closed; the referent-DATA build is the live frontier).
