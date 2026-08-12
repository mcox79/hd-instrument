# STATUS

AS OF: 2026-08-12T22:48Z (testbed rewrite) | branch dataprep/mcguffey-graded-corpus | commit
67ffc6998 (local; origin a37b8abeb, 29 commits ahead, not pushed)

Rewritten in place every session; never append -- if it doesn't fit in 6KB, it's an evidence-doc
claim with a pointer, not content that belongs here.

LEDGER: `notes/ledger_grounding_quality_2026-08-12.md` -- STALE (last entry af8e286ae, doesn't
cover v4/v5/PBV/island-harvest/context-v2 below); arc owner should refresh it.

## WHAT IS TRUE NOW (sourced -- follow the pointer, don't trust this summary)
- Definitional v5 term-boundary fix: **HARD_PASS**, 64% MEANINGFUL/12% RELATED/24% NOISE on
  2092 facts vs >=52% bar. Rungs 8->38->40->64; the v4 "ceiling" read was wrong, it was term
  corruption (16.1% of terms), not structural. -> `notes/director_handscore_b3_v5_termboundary_
  2026-08-12.md` (**uncommitted**, `git status` confirms untracked).
- Context-conditioned sense selection v2 (v5 facts): **HARD_FAIL** both indexes -- subject
  0.4809 vs floor 0.4634 (C1 drop 0.010); head_lemma 0.4449 vs floor 0.4401 (C1 drop 0.022). C3
  topic-controlled CI lower bound still below floor despite eased data scarcity. ->
  `notes/context_conditioned_sense_selection_v2_2026-08-12.md`, commit dd58dcf69.
- Brain-fidelity audit Sec G (ab7d8a2cc/a06bb22ae/c6a2e5fd8/82d437be1): reading path had no
  hypothesis object; argmax is already propose-then-verify in shape (director's intersection
  proposal was backwards); definitional parser ruled a WIRING violation (nothing can disconfirm
  banked output), not FORM/function.
- **PBV -- CORRECTION: settled, not in-progress.** Landed-VET REFUTED it, `verdict=HARD_FAIL`
  (commit a28cf3b45). Primary band fails: P1 abandon-on-wrong 0.286 (need >=0.60), P3 separation
  0.071 (need >=0.30); abandonment is an arithmetic function of encounter count, not hypothesis
  correctness (C1 vs C2 Fisher p=1.0). Yield: B replaces 72% of A's output, no correctness gain
  (Mann-Whitney p=0.508). Revision quality (D2) null (mean delta -0.0007, p=0.899). ->
  `notes/landed_vet_pbv_hypothesis_v1_2026-08-12.md`.
- Corpus: **117,642 sentences** (re-summed off 5 `density_report.json`, exact match), 5 OpenStax
  titles, CC BY-NC-SA 4.0 confirmed per-title. Commit 7c26d429c. Density/1000 sent (exact):
  anatomy 105.8, biology 86.9, microbiology 62.6, chemistry 58.6, psychology 30.8 -- gap tracks
  SUBJECT not textbook. **NOT ingested; growth still paused.**
- Island harvest (6d422ec98): MAVEN-ERE precision confirmed 11.49% causal / 8.22% subevent ->
  **DO NOT WIRE**; 3 rows demoted WIRE->SHELVE (`native_vsa_cross_slot_relational_binding`,
  `theory_of_mind_sally_anne_nested_hrr`, `capacity_scaling`). ISLAND census partly an
  instrument artifact (`tools/integration_health.py` missed the dominant bare-import idiom,
  fixed); ISLAND 34->28, TRAPPED_SHARED 22->28. -> `notes/island_harvest_assessment_2026-08-12
  .md`.
- Registry (fresh `--dry-run` this pass): **123 rows** (WIRED 65 / TRAPPED_SHARED 28 / ISLAND
  28 / N_A_SHELVED 2 / UNKNOWN 0); unregistered hdlab modules 71->61. `lexical_similarity.py`'s
  gap (23 consumers) is **already closed**, WIRED.
- **Registry concurrency bug fixed (testbed, this session), commit 67ffc6998.** An agent hit a
  ~1s read-edit-replace lost-update race on `data/capability_registry.jsonl` (the WIRE-or-SHELVE
  gate). Fixed via `RegistryLock`/`registry_transaction`/`append_rows()` in
  `tools/capability_registry_audit.py`, reusing `tools/safe_queue.py`'s lock backend (house
  style) to hold load->mutate->write as one critical section. Witness
  `verification/test_capability_registry_concurrency.py` (2 real OS-process tests) proves the
  safe path never loses a write AND the pre-fix pattern genuinely does (witness can fail).
  `pytest verification/` 269 passed/3 skipped (was 267/3); `--self-test`/`--dry-run` clean; real
  registry byte-unchanged.
- Agent-definition frontmatter claim ("`background`/`isolation` refuted, `model` confirmed"):
  **no on-disk evidence found** (no notes file, no commit touching `.claude/agents/*.md` or
  `AGENT_TEAMS_MIGRATION.md` today). Unverified.

## WHAT IS RUNNING
Nothing experiment-related is live (checked `Get-CimInstance Win32_Process`: only routine infra
-- `director_kb_continuous_ingest.py --once --quiet`, `landing_notifier.py` x2 -- plus this
session's own test workers). PBV smoke FINISHED + landed-VET committed (above).
Context-conditioned sense-selection v2 (prior STATUS said "live") also FINISHED + committed
(dd58dcf69).

## NEXT (ordered)
1. PBV re-run gate if revisited: raise proposer self-consistency (confirm rate 10.1%) first --
   **not** "route through PBV verify" as previously planned; PBV is HARD_FAILed.
2. Induce constructions; syntactic bootstrapping under assessment -- commit 17eeb72e9 (not read
   this pass; concurrent-session-owned, DO NOT TOUCH).
3. Perceptual grounding scoped to concrete vocabulary.
4. Foundation growth stays PAUSED until grounding quality holds (v5 HARD_PASS is a step, not a
   green light; sense selection still HARD_FAILs).
5. Commit today's uncommitted notes (see BLOCKED).

## BLOCKED / DO NOT TOUCH
- `hdlab/reading_grounding_loop.py`, `hdlab/grounding_acquisition_loop.py`,
  `experiments/exp_pbv_hypothesis_v1.py` -- concurrent session.
- `notes/landed_vet_pbv_hypothesis_v1_2026-08-12.md`, any `syntactic_bootstrapping_readiness`
  note -- owned by other agents this pass.
- Untracked-but-live (`git status`), all `notes/*_2026-08-12.md`: `corpus_composition_audit`,
  `director_handscore_b3_{def_vs_control,v4_parsefix,v5_termboundary}`, `foundation_backup` --
  not this role's to commit/edit.
- `data/foundation/reading_grounding_v1` + `v2_qualityfix` (22+23MB), one disk only, not backed
  up (carried over, not re-verified).

## DO NOT REDO
See `notes/director_transition_digest_2026-08-12.md` Sec C. Add: same-sentence cosine as a
grounding-correctness signal; PMI as a meaning-quality ranking; FHRR superposition to move the
50-pair audit (invariant to it); "route through PBV" (HARD_FAILed); flat v3->v4 as a ceiling
(it was term corruption, see v5).
