# STATE + NEXT — recovery anchor (read this FIRST after compaction)

**Problem:** `grounding_does_not_accumulate_over_repeated_exposures_needs_retrieval_practice` (SOLVER session).
**Owner directive (current):** "fully solve this issue in this solution" — go beyond the located negative +
demonstrated fix and actually CLOSE the gap by building + wiring the grounded sense-selection read-out.

Durable partners to this file: `SOLVED.md` (full writeup, status SOLVED), the memory note
`project_consolidation_fail_wall_is_representation_bound_not_durability_2026-08-31.md` (persists across
sessions), and `verification/test_retrieval_practice_consolidation.py` (the witness).

---
## THE VERDICT (established, decisive, reproducible — do NOT re-derive)

The 59% CONSOLIDATION_FAIL wall is **representation-bound at the SELECTION level**. Chain, all decisive:
1. **Retrieval practice (Mozer Eq7 + PBV) REFUTED** — selection-AUC at chance 0.486/0.503 (2-seed).
2. **Population premise REFUTED** — mean split-half coherence 0.09-0.13; only ~2% coherent-single-sense.
   41% polysemous / 29% no-anchor / 18% incoherent / 11% proper-noun (2-seed).
3. **Sense-splitting (DP-means) NOT robust** — recovery 0.4-4%, seed-unstable.
4. **ORACLE decomposition (2-seed):** a WordNet-correct anchor EXISTS for ~78% (only ~8% coverage-bound).
5. **ENCODER is NOT the wall:** every encoder — hashed bag / PPMI / PPMI+SVD / **full dependency-parse
   syntactic encoder** — retrieves the correct anchor to **median rank ~3, top-10 ~85%**. Refuted the
   "better encoder / p2 parser is the lever" guess head-to-head.
6. **NO distributional read-out SELECTS it:** nearest 0.21, bg-subtract 0.23, distilled-substitutability-axis
   0.24, **supervised CV logistic 0.22 (lift ~0, coefs ~0)** — all vs the top-10 ceiling ~0.87. The signal
   separating correct SENSE (whisky->brandy) from topical ASSOCIATE (whisky->wedding) is genuinely absent
   from distributional co-occurrence.
7. **DEMONSTRATED FIX (positive proof, not elimination):** re-ranking the retrieved top-K by GROUNDED-HUB
   similarity (`hdlab.distributional_meaning_channel.build_grounded_hub` = 11 Lancaster sensorimotor + 3
   Warriner affect dims, the ATL hub-and-spoke vector) SELECTS the correct sense: **rank-1 0.32/0.35 vs
   distributional 0.24/0.27, lift +0.08/+0.07 (both seeds), ~78% grounded coverage.** Grounded features
   carry the sense signal distribution lacks — exactly Phase-1 (sensorimotor spokes -> ATL hub).

**Brain-foundational core:** ATL hub-and-spoke (Lambon Ralph/Patterson/Rogers). Lever = a GROUNDED
sense-selection read-out. Honest bound: the demonstrated lift is PARTIAL (to ~0.33, not ~0.87) and covers
only ~78% (uncovered = abstract words needing affective/linguistic grounding — Barsalou/Vigliocco).

---
## TO FULLY SOLVE (the continuation the owner wants) — concrete plan

**Goal:** push CONSOLIDATION_FAIL sense-selection from ~0.33 toward the ~0.87 top-10 ceiling with a
brain-faithful GROUNDED selector, then WIRE it and measure end-to-end grounding-precision gain (2-seed,
info-free controls, remote for the full runs). Escalation ladder (each is a lightweight probe first):

1. **Richer grounded features — Binder-2016 65-dim experiential.** The demonstrated hub is only 14-dim
   (Lancaster 11 + Warriner 3). Add Binder ratings `data/corpora/binder/binder2016_ratings.csv` (65
   experiential dims: vision, motion, space, emotion, etc.). Build a Binder hub analogously and re-rank.
   Expectation: bigger lift than 14-dim. (Binder covers ~535 words — low coverage, so use it to prove the
   CEILING of grounded selection, then fall back to Lancaster+Warriner + a predictor for coverage.)
2. **LEARNED grounded selector.** Supervised over DISTRIBUTIONAL features gave lift ~0 (signal absent) —
   BUT supervised over GROUNDED features should work (grounded carries signal). Build a logistic / small
   MLP over per-candidate GROUNDED features (grounded-hub cos + Binder cos + the grounded dims themselves),
   optionally + distributional rank as a weak feature; 5-fold CV over HELD-OUT WORDS (labels offline only =
   admissible foundation asset; no external LLM at inference). Target: rank-1 well above 0.33.
   -> add a `grounded_supervised_probe` mirroring `supervised_reranker_probe` but with grounded features.
3. **OOV coverage for the ~22% uncovered abstract words.** A learned grounded-feature PREDICTOR exists:
   `data/exp_selpref_unseen_lowdata_v1/_ckpt_full/artifact_BINDER65_PREDICT.npz` (predicts Binder-65 from
   distributional input). Use it to impute grounded features for words absent from the norms, extending
   selection to the full population. Check whether predicted-grounded still beats distributional.
4. **WIRE it — the proposed hdlab change (Q111, strategy lands).** The fix is a GROUNDED sense-selection
   read-out over `reading_grounding_loop.canonicalize`'s candidate set: instead of nearest-eligible-anchor
   by distributional cosine, retrieve the top-K distributionally then SELECT by grounded-hub similarity.
   Site: `hdlab/reading_grounding_loop.py::canonicalize` (+ `checkpoint`'s use of it). Default-off flag.
5. **END-TO-END measurement (the real solve criterion).** Wire the grounded selector into the grounding
   read-out and measure CONSOLIDATION_FAIL grounding PRECISION (WordNet-correct rate) end-to-end: does it
   rise from the ~0.30 distributional ceiling toward the grounded ceiling, CI-separated over (a) the
   distributional read-out and (b) an info-free twin (shuffled grounded features / random norms)? 2-seed;
   full runs REMOTE (remote_cpu_queue). THAT is "fully solved": a grounded read-out that measurably grounds
   more of these words correctly, wired (proposed), witnessed.

**Success bar for the full solve:** grounded (richer + learned) sense-selection lifts CONSOLIDATION_FAIL
grounding precision CI-separated above the distributional ceiling (~0.30), 2-seed, info-free twin loses,
with a default-off `canonicalize` grounded-selection wire proposed + a witness check.

---
## HOW TO RUN (exact commands; cell = experiments/exp_retrieval_practice_consolidation_v1.py)

- Self-test: `.venv/Scripts/python.exe experiments/exp_retrieval_practice_consolidation_v1.py --self-test`
- The demonstrated fix (grounded re-rank): `--grounded-probe --smoke --seed {0,1}` -> grounded_probe.json
- Read-out ladder + oracle + supervised, all at once: `--confirm-all --smoke` -> confirm_all.json
- Witness (recomputes everything incl. W14 grounded fix):
  `.venv/Scripts/python.exe verification/test_retrieval_practice_consolidation.py`
- Full-scale confirmation is REMOTE: `REMOTE_RUN_REQUEST_exp_retrieval_practice_consolidation_v1.md` is
  DROPPED (queue remote_cpu_queue, args `--confirm-all --mode full`); watch
  `data/remote_run_request_watcher_log.jsonl` + `data/exp_retrieval_practice_consolidation_v1/confirm_all.json`.

Key functions in the cell: `capture(route_b=True)`, `oracle_anchor_ceiling`, `encoder_diagnostic`
(has `readout_reranking_on_phi`), `supervised_reranker_probe`, `grounded_reranker_probe`,
`readout_reranker_probe`, `sense_splitting_probe`, `distributional_representation_probe`. Reuse
`_correct_anchor_set`/`_syn_closure` for WordNet correctness (ALWAYS subsumption OR wup>=0.5 — dropping wup
gave invalid collapsed numbers TWICE). Grounded assets: `hdlab.distributional_meaning_channel.build_grounded_hub`,
`hub_sim`; norms in `data/grounding_testbed/` (Lancaster, Warriner) + `data/corpora/binder/binder2016_ratings.csv`.

---
## DISCIPLINES THAT BIT (do not repeat)
- **Heavy/long runs go REMOTE (marsh@home, remote_cpu_queue — NO torch here).** Lightweight probes/self-tests
  inline. The local box was thrashed by stale process pileup; clean up with a cmdline-matched kill of
  `*exp_retrieval_practice*` only (this session's), NEVER other sessions' pythons.
- **Match the established WordNet criterion exactly** (subsumption OR wup>=0.5), scope wup to top-K for speed.
- **Believe multi-seed over smoke** (sense-splitting looked good at smoke, failed at full 2-seed).
- **Rate-independent selection-AUC** defeats the unmatched-twin trap.
- Solver scope: MAY write experiments/, verification/, this problem folder. MAY NOT write hdlab/ (Q111 —
  strategy lands the wire), preregs/**, arm_key*. WIP until `owner_verdict: DONE` in OWNER_NOTES.md.

## STATE OF RUNS (at compaction)
- Local: all probe json on disk (smoke + core 2-seed). No heavy run should be left running locally.
- Remote: REMOTE_RUN_REQUEST dropped (full --confirm-all, seed 0). Second-seed = drop a `--seed 1` twin.
- Witness: 18/18 confirmed earlier; W14 (grounded fix) added -> re-running to confirm 19/19.
