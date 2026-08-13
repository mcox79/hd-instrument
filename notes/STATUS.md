# STATUS

AS OF: 2026-08-12T~23:59Z (refresh #2) | branch dataprep/mcguffey-graded-corpus | commit
46c32d960 (local; origin a37b8abeb, 43 ahead, not pushed)

Rewritten in place every session; never append -- if it doesn't fit in 6KB, it's an evidence-doc
claim with a pointer. LEDGER: `notes/ledger_grounding_quality_2026-08-12.md`, refreshed this pass.

## WHAT IS TRUE NOW (sourced -- follow the pointer, don't trust this summary)
- **Infra, tonight** (CLAUDE.md "Agent-teams / frontmatter findings"): `background:`
  frontmatter key INVALID -- fails the WHOLE definition to load (all 5 `hdi_*` vanished,
  returned when removed), corrects prior "no effect" claim. `model`/`tools` valid. `hdi_*`
  needs client env `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, restored in
  `~/.claude/settings.json` tonight, needs client restart. Effort = env
  `CLAUDE_CODE_EFFORT_LEVEL=high`, not settings.json `effortLevel: xhigh` (inactive).
  Backgrounding never the blocker, see `notes/director_delegation_audit_2026-08-12.md`.
- **Read-out fix landed-VET** (`notes/landed_vet_readout_fix_v1_2026-08-12.md`, 8de3a9a20):
  OVERSTATED headline. F3 (frozen anchor space) CONFIRMED stronger than claimed (-0.168 at
  matched retention, moves `flip_all` -0.0603) -> WIRE default-OFF. F2 (freq-corrected pool)
  REFUTED as retention artifact (+0.032 HURTS GROWING) -> SHELVED. F1 (z-gate): stability
  selector only, never informativeness (AUC 0.5067). Best config F1+F3, GROWING 0.3602,
  **no quality claim licensed, flip stability only**. WIRED default-OFF additive
  (192521a7f/8e6c574c5/7a708eff3, latter closes an F3 memory leak).
- **Context vector is NOT noise:** flip 0.7830 vs scramble 0.9984, D=+0.2155 (79c7521cd,
  59479cf82). Defect is downstream in the READ-OUT -- why the arc above exists.
- Delegation audit `notes/director_delegation_audit_2026-08-12.md` (untracked): blocking fixed
  only after 4th protocol edit (~4.5h); verbosity trended worse (4.8x).
- Definitional v5 term-boundary fix: **HARD_PASS**, 64% MEANINGFUL/12% RELATED/24% NOISE on
  2092 facts vs >=52% bar (8->38->40->64; v4 "ceiling" was term corruption not structural) ->
  `notes/director_handscore_b3_v5_termboundary_2026-08-12.md` (untracked).
- Context-conditioned sense selection v2: **HARD_FAIL** both indexes (0.4809 vs floor 0.4634;
  0.4449 vs floor 0.4401) -> dd58dcf69.
- **PBV: settled HARD_FAIL.** P1 0.286 (need >=0.60), P3 0.071 (need >=0.30) ->
  `notes/landed_vet_pbv_hypothesis_v1_2026-08-12.md`, a28cf3b45.
- Foundation-validation: **OVERSTATED**, plumbing proven/meaning not -- 65.7% self-tautologies
  `(X,GROUNDED_MEANING,X)` -> `notes/landed_vet_foundation_validation_2026-08-12.md`, 3340df8d5.
- Corpus: 117,642 sentences, 5 OpenStax titles, CC BY-NC-SA 4.0, 7c26d429c. **NOT ingested;
  growth still paused.**
- Registry: 123 rows (WIRED 65/SHARED 28/ISLAND 28/SHELVED 2), concurrency race fixed
  67ffc6998. `pytest verification/` 269/3.

## WHAT IS RUNNING -- TOP OPEN ITEM
**Nothing live** (`Get-Process`: only pre-existing python/pythonw/claude PIDs, none tied to this
cell). 4th detached `claude -p` attempt left `data/cli_agent_quality.log` (4433B) + `.err` (0B),
**produced no experiment** -- `exp_grounding_quality_readout_v1.py` still absent on disk. Log's
diagnosis: every Write/Edit failed, no settings file grants Write/Edit
(`.claude/settings.local.json` confirmed 0 such rules) and the session was headless -- 4th
non-completion, 1st with a root cause. Reusable pre-flight it verified: corpus loader 34169
sentences/5 segments match prereg, F1 threshold `g_match=3.542496` reproduces, S5 ref 0.100561
reproduces, wall-time margin wide (4.56x a 220.8s/7500-sentence smoke), S7 memory not a
knife-edge (CTX_D=256 not 2048, worst case 0.4-0.9GB vs 4GB cap), `reading_grounding_loop.py`
untouched. **Fixing the Write/Edit grant is a precondition for attempt 5.** Prereg sound
(`preregs/2026-08-12_grounding_quality_readout_v1.md`, 192521a7f): 2 arms x 5 segments,
HARD_PASS delta>=+0.20 & F1F3>=0.25, NULL |delta|<0.08 acceptable, S1-S8 gates, timeout_s 21600.

## NEXT (ordered)
1. Grant Write/Edit in settings (blocked attempt 4) then author + detach-dispatch
   `exp_grounding_quality_readout_v1.py` -> two UNSCORED 50-row samples (PBV_BASE, PBV_F1F3).
2. Director hand-scores both vs the 64% v5 rubric (CEILING REF ONLY, prereg refuses scoring
   against it; real comparator is v2 DIST's 8%).
3. Growth stays PAUSED regardless of this cell's outcome until grounding quality holds.
4. Noun-only structural gap (0 verb defs in 2092 facts, all 5 patterns NP-headed) -- unscheduled.
5. Syntactic bootstrapping note (17eeb72e9) -- concurrent-session-owned, do not touch.

## DO NOT REDO (unmissable -- do not re-propose)
- Intersection-over-argmax: refuted, argmax already propose-then-verify shaped.
- The "40% ceiling": was term corruption, now 64% (v5 term-boundary fix).
- Syntactic bootstrapping as a *next step*: no verbs in extracted data (0/2092), blocked on the
  noun-only extractor gap, not ready to build on.
- F2 (frequency-corrected pool): refuted as a retention artifact, SHELVED; revival needs a
  retention-matched arm >=0.05 residual, none measured.
- Same-sentence cosine / PMI as grounding-quality signals; FHRR superposition to move the
  50-pair audit (invariant to storage rep); "route through PBV" (HARD_FAILed).
- `isolation:` agent frontmatter key -- tested, ignored. `background:` -- WORSE than ignored,
  fails the whole definition to load (see infra bullet above); still never add either.
- Scoring the quality-readout cell against v5's 64% -- refused in its own prereg; comparator 8%.

## BLOCKED / DO NOT TOUCH
- `hdlab/reading_grounding_loop.py`, `hdlab/grounding_acquisition_loop.py`,
  `experiments/exp_pbv_hypothesis_v1.py` -- concurrent session (verify before edit).
- Untracked notes owned by others, `notes/*_2026-08-12.md`: `corpus_composition_audit`,
  `director_delegation_audit`, `director_handscore_b3_{def_vs_control,v4_parsefix,v5_termboundary}`,
  `foundation_backup` -- not this role's to commit.
- `data/foundation/reading_grounding_v1`+`v2_qualityfix` (22+23MB), one disk only, no backup.
