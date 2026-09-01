# STATE + NEXT — recovery anchor (read this FIRST after compaction)

**Problem:** `grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice` (SOLVER).
**Owner directive (current):** "fully answer this problem, with a full solution including a FULL LIFT."
This session BUILT the full-lift mechanism (brain-foundational) on top of the located negative.

Durable partners: `SOLVED.md`, the memory note
`project_consolidation_fail_wall_is_representation_bound_not_durability_2026-08-31.md`,
`verification/test_retrieval_practice_consolidation.py` (witness, now W1-W16),
`RESEARCH_sense_selection_mechanism.md` + `RESEARCH_accumulation_and_cross_situational_learning.md`
(the two brain drills), `WIRE_PROPOSAL_grounded_sense_selection.md` (the exact hdlab diff for strategy).

---
## THE VERDICT (established) + THE FULL LIFT (this session)

**Located negative (prior, decisive, do NOT re-derive):** the 59% CONSOLIDATION_FAIL wall is
representation-bound AT THE SELECTION level. Retrieval practice REFUTED (selection-AUC at chance);
population 92% polysemy/no-anchor/incoherent/proper-noun; the correct anchor is RETRIEVABLE (top-10
~85% under every encoder incl. a full parser) but NOT SELECTABLE by any distributional read-out
(nearest/bg/distilled/supervised all ~0.21-0.24 vs within-set ceiling 1.0).

**THE FULL LIFT (brain-foundational, this session):** a pure GROUNDED sense-selection re-rank over the
distributional shortlist roughly DOUBLES correct sense selection. 2-seed SMOKE, CI-separated both seeds:
- DIST ~0.20-0.28 -> GRD65/CASCADE ~0.35-0.46 (predicted-Binder-65 experiential spoke, morphology-
  extended, distributional-shortlist cascade). ci_CASCADE_MORPH_minus_DIST separated above 0 both seeds.
- Info-free GRD65_SHUF ~= DIST (CI includes 0) -> the lift is REAL grounding.
- Re-FUSING the distributional cue HURTS (FUSE_BOTH < grounded-alone) -> the distributional cue is
  confidently-WRONG for sense (peaky about TOPIC not SENSE); the cascade is grounded-DOMINANT.
- Measured-Binder-535 ~ predicted-Binder on the human-rated slice (0.8-0.9 vs DIST 0.2) -> the lift is
  real experiential grounding, NOT an imputation artifact.

**Brain basis (two research drills, both PINNED):**
1. SELECTION = ATL hub-and-spoke (Lambon Ralph/Patterson/Rogers); reliability-weighted cue combination
   (Ernst-Banks / noisy-channel) == product-of-experts; argmax = settled attractor basin (Rodd 2004);
   two-stage fast distributional shortlist -> slow grounded re-rank = LASS (Barsalou 2008).
2. ACCUMULATION (the problem's literal name) is SECOND-ORDER for THIS population: its precondition
   (coherent within-SENSE repetition) is absent (coherence 0.09-0.13); a per-word running mean = the
   refuted single-average; the brain carries MULTIPLE competing sense-hypotheses for polysemy (CSL:
   single-hypothesis is a monosemous-lab result). Accumulation's honest value = variance-reduction of
   the grounded read, foldable into the selector's reliability weight. So SELECTION-ONLY is the near-
   complete brain-faithful answer here. Missed lever surfaced: MORPHOLOGY as a word-internal spoke
   (brightness<-bright) for the abstract tail -- but only +0.005/+0.023 here because predicted-Binder
   already covers ~86% of the derived tail. Calibration: incidental word-learning is ~15%/exposure
   (Nagy-Anderson), so "doesn't accumulate" on a thin 3000-sent low-coherence corpus is partly EXPECTED.

**Honest bound:** the lift is LARGE (~2x, CI-separated) but not to the within-set ceiling (1.0) -- ~0.45,
not perfect. The residual = harder senses where grounded features don't separate + grounded-read noise.
The supervised CEILING probe (upper bound on extractable grounded signal; NOT a wire) frames it.

---
## WHAT IS BUILT (this session, all on disk)
- `experiments/exp_retrieval_practice_consolidation_v1.py`:
  - `grounded_fusion_probe` (--fusion-probe): THE full-lift mechanism. Selectors DIST/GRD14/GRD65/
    GRD65_MORPH/GRD_BOTH/CASCADE/CASCADE_MORPH/FUSE*/SHUF14/GRD65_SHUF; paired-bootstrap CIs; abstract-
    slice ablation; measured-vs-predicted-Binder anti-artifact cross-check. UNSUPERVISED, wireable.
  - `grounded_supervised_probe` (--grounded-supervised-probe): CEILING yardstick ONLY (trains on gold;
    NOT a wire) + info-free shuffle control.
  - Helpers: `_load_binder65_table`/`_build_binder65_hub` (predicted-Binder-65, 24978 words),
    `_measured_binder_hub` (Binder-535 anti-artifact), `_morph_stem_candidates`/`_build_binder65_hub_morph`
    (morphology backoff), `_cue_reliability` (peakiness), `_cand_z`.
  - `# KB_REFERENT:` lines added (the remote blocker fix); --confirm-all now bundles fusion + ceiling.
- `verification/test_retrieval_practice_consolidation.py`: W15 (grounded re-rank beats DIST CI-separated)
  + W16 (shuffle null + fusion-does-not-beat-grounded). RE-RUN to confirm (was 19/19; now up to ~21).
- `REMOTE_RUN_REQUEST_...md`: RE-DROPPED for `--confirm-all --mode full --seed 0`, KB_REFERENT declared,
  all 8 paths verified present. (spaCy is a false-positive WARN: closed_class_lexicon degrades to its
  frozen snapshot.) Drop a `--seed 1` twin for seed 2.
- `WIRE_PROPOSAL_grounded_sense_selection.md`: the exact additive `canonicalize_grounded` sibling
  (default-off, thresh stays on DIST cosine = no bar relaxation) for strategy to land (Q111).

---
## NEXT (finishing sequence)
1. Confirm `--confirm-all --smoke` bundle runs clean + read the grounded_supervised CEILING number
   (validation was running at compaction: `data/exp_retrieval_practice_consolidation_v1_smoke/`).
2. Re-run the witness -> confirm W15/W16 pass (target all PASS, ledger clean).
3. RECONCILE `SOLVED.md` + the memory note + the AUDIT UPDATE with the FULL-LIFT result (grounded
   re-rank ~doubles selection; the wire; honest ceiling). Keep the located-negative section; ADD the
   full-lift section. Status stays SOLVED; WIP until `owner_verdict: DONE` in OWNER_NOTES.md.
4. Route the FULL 2-seed `--confirm-all` REMOTE (request dropped); watch
   `data/remote_run_request_watcher_log.jsonl` + `data/exp_retrieval_practice_consolidation_v1/confirm_all.json`.
5. END-TO-END (the wire's landing gate, strategy): does CONSOLIDATION_FAIL grounding PRECISION rise
   CI-separated above ~0.30 with `canonicalize_grounded`, 2-seed, info-free twin loses, recall not
   bought by bar-relaxation. Full runs REMOTE.

## HOW TO RUN (exact)
- Self-test: `.venv/Scripts/python.exe experiments/exp_retrieval_practice_consolidation_v1.py --self-test`
- Full-lift mechanism (smoke): `--fusion-probe --smoke --seed {0,1}` -> fusion_probe.json
- Ceiling yardstick: `--grounded-supervised-probe --smoke --seed 0`
- Everything bundled: `--confirm-all --smoke` (or `--mode full`, REMOTE) -> confirm_all.json
- Witness: `.venv/Scripts/python.exe verification/test_retrieval_practice_consolidation.py`

## DISCIPLINES THAT BIT (do not repeat)
- ASCII-ONLY (a Cyrillic suffix slipped into _DERIV_SUFFIXES once -> removed). Verify: no ord>127.
- The read POPULATION is hash-randomized (str-hash) -> smoke MAGNITUDES wobble run-to-run; only
  CI-SEPARATED DIRECTIONS are citeable at smoke; magnitudes come from the full remote run.
- Heavy/long -> REMOTE (remote_cpu_queue, NO torch). Lightweight probes/self-tests inline.
- Match the WordNet criterion exactly (subsumption OR wup>=0.5), scoped to top-K (bit twice earlier).
- SUPERVISED-on-WordNet is a CEILING yardstick, NEVER a wire (grade-by-what-you-ground-by). The wire
  is the UNSUPERVISED grounded cascade.
- Solver scope: MAY write experiments/, verification/, this problem folder. MAY NOT write hdlab/ (Q111).
