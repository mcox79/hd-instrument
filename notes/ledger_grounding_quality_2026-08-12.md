# LEDGER: grounding quality fix (tautology + closed-class refusal, provenance) -- 2026-08-12

Arc: correct the overstated `reading_grounding_v1` foundation ("3544 grounded concepts /
HARD_PASS") by auditing it, then fixing the acquisition loop so a grounding must be an
actual meaning link, not a same-sentence collocate or self-tautology, then re-running and
re-scoring on the same pre-registered rubric. Retroactively written from git history +
notes/grounding_quality_fix_2026-08-12.md; ledger + git log outrank recollection after
compaction.

- bce482b06 -- cycle2 reading-grounding FULL run lands, claimed HARD_PASS, foundation
  185->3544 concepts cumulative. (This is the claim later found overstated -- see next step.)
- 71a84d86f -- `exp_foundation_validation_harness_v1` cell added (3-claim store audit:
  correctness / coherence / can-reason). Built to check the cycle2 claim, not yet run.
- (uncommitted, evidence docs) `notes/landed_vet_foundation_validation_2026-08-12.md` --
  independent audit of the harness run: verdict OVERSTATED. Plumbing proven, meaning not;
  65.7% self-tautologies; 2/4 HARD_PASS band conditions cannot fail by construction.
- (uncommitted, evidence docs) `notes/foundation_grounding_sample_2026-08-12.md` -- direct
  50-pair + 20-pair (cross-only) hand audit quantifying quality: mixed 4%/6%/90%
  (MEANINGFUL/RELATED/NOISE), cross-only 35%/25%/40%.
- 3340df8d5 -- docs: correct the overstated HARD_PASS + 3544-concept claim in the living
  docs; mark stale THE_PLAN items superseded.
- 04b922c0e -- grounding quality fix landed: `hdlab/closed_class_lexicon.py` (new, UD +
  spaCy stop-word closed-class criterion), `hdlab/reading_grounding_loop.py`
  (`canonicalize(eligible=...)`, refusal gate via existing `mdl_gate_fn` hook, provenance +
  refusal ledgers), `hdlab/foundation_persistence.py` (FORMAT_VERSION 2, optional sidecars,
  v1-shape backward compatible). Pre-reg: `preregs/2026-08-12_grounding_quality_fix_v1.md`
  (bands B1-B6, anti-tuning commitment, FROZEN thresholds). Self-tests + verification suite
  green. Smoke gate PASS (discriminator fires: 401 refusals vs 211 groundings).
- (in flight, no commit yet) FULL re-run over the same 5 segments into
  `data/foundation/reading_grounding_v2_qualityfix/` (untracked by design, like all of
  data/foundation/). PID 30104. Log `data/exp_cycle3_full_run.log`. NOT YET SCORED.

- v2 full run completed and scored: B3 fresh 50-pair hand-score 8% MEANINGFUL / 26% RELATED /
  66% NOISE, FAILS the pre-registered <0.15 floor
  (`preregs/2026-08-12_grounding_quality_fix_v1.md:24-26`).
- c628081e5 -- v3 prior-work check + on-disk state verification (query-before-build: 0/107
  registry rows match; not a rediscovery of an owned organ).
- b8b108a1d -- diagnosis: grounding signal is definition-blind (2.2% pair-link vs 58.5%
  definitional evidence present in facts' own evidence sentences); director's premise
  confirmed, more strongly than stated. MEANINGFUL hits are compound terms, not definitions
  (0/32 on the v1 labelled sample).
- 01093ac1f -- fix(2a): `lemma_word` normalizer (WordNet morphy, never-emit-a-non-word
  invariant) migrated into the reading-grounding path; extractor false-positive guards added.
- 58deb570c -- fix(2b): principled low-information PMI gate calibrated off the closed-class
  lexicon (p75=2.10); kills all 20 `X->people` facts, keeps every known-meaningful pair.
- 278a84592 -- step-2: best_cos=0.45 threshold investigated (55% of accepted facts cluster in
  the first 0.05 above floor; median top1-top2 margin 0.0147) and left unchanged -- no
  independent justification to move it.
- 7d937bf6b -- prereg: definitional grounding v3 bands registered BEFORE the run (HARD_PASS
  >=35% MEANINGFUL AND >=200 facts).
- 7f57b5b84 -- exp_definitional_grounding_v3 landed: DEF arm 1751 facts (1749 not produced by
  the distributional path), DIST_LOWINFO control 290 facts; B3 samples written for
  hand-scoring. Cell verdict STRUCTURAL_PASS_PENDING_B3 (not auto-scored).
- 80a4615fa -- step-3 notes: reuse-vs-built ledger, arm sizes, absolute-count caveat.
- (director hand-score, reported in-session, NOT YET persisted to metrics.json or the notes
  doc): DEF arm 38% MEANINGFUL / 18% RELATED / 44% NOISE on 1751 facts; DIST_LOWINFO control
  8%/26%/66%, identical to the DIST_ASIS baseline. Cell verdict on disk is still
  STRUCTURAL_PASS_PENDING_B3 -- treat the 38/18/44 number as unpersisted until it lands.
- 8e364d807 -- wire-reader-to-meaning-organs step 1: islanding premise (a) REFUTED in code and
  on landed v3 data (1751 stored / 1751 live; 288/1316 subjects already multi-sense and
  queryable via FLAGGED-is-ACTIVE). Build halted before wiring superposition.
- 035a3acc5 -- measured random-pick floor for context-conditioned sense selection:
  mean(1/k)=0.4316 over the 288 multi-sense subjects (replacing a hypothesized 1/k).
- 37d10e690 -- (b)/(c) established: FHRR superposition store is an unpromoted exp-local class
  from a HARD_FAILed cell (`exp_bootstrap_fhrr_superposition_fade_v3`, not in hdlab/,
  unregistered); canonicalization organs (lexical_similarity, verb_lexical_similarity) are
  real and HARD_PASS; the 50-pair audit is invariant to storage representation -- STOP before
  build, context-conditioned sense-selection test recommended instead.
- 411d2fb6f -- skunkworks Task B: registered 6 previously-unregistered load-bearing hdlab
  modules (gap_detector, gap_driven_reader, foundation_persistence, closed_class_lexicon =
  WIRE; definitional_extraction, low_information_filter = VET_PENDING pending B3). Registry
  107->113 rows, unregistered hdlab modules 77->71.
- af8e286ae -- skunkworks Task A: reinvention check on `definitional_extraction.py` -- verdict
  DISJOINT/novel, not a rebuild of the "0.90 extractor" (different job). Registry triage of
  the remaining 71 unregistered modules (5 true islands -> SHELVE candidate;
  `lexical_similarity.py`, 23 consumers, flagged as a real unclosed gap).

## NEXT STEP FOR THIS ARC (see notes/STATUS.md for the live pointer)
Context-conditioned sense-selection experiment is in flight (concurrent session), scoring
against the measured 0.4316 random floor on the 288 multi-sense words. Then persist the v3
DEF/DIST_LOWINFO hand-scores to disk and update the cell verdict off
STRUCTURAL_PASS_PENDING_B3.
