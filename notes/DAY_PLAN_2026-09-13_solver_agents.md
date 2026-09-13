# DAY PLAN 2026-09-13 (afternoon -> overnight): SOLVER SESSIONS AS AGENTS -- test, gate, then run the program

**Owner direction (14:15 local):** "prepare a full day plan, including testing and, if successful, continuing to implement these
opus 4.8 solver sessions as agents, and then start implementing." Autoloop ARMED (unlimited). Times below are by `date` (local).
The model: the Agent tool offers `opus` (the current Opus) with no 4.8 pin -- reported as such everywhere.

## What stays true all day (standing rules)
Integrate only on the owner's DONE (Q filed below asks whether agent-produced solutions may be integrated on strategy's first-hand
reverify instead); commit path-limited, never push; cap cores on every run; never edit preregs/** or arm_key*; every component
100% brain-foundational (off-the-shelf tool at inference = defect); organs plastic, never frozen; params swept, never adopted;
surgical edits; plain-language owner updates only for significant items; waiting is delegated to haiku runners, never the main
thread; at most TWO opus solver agents at once (the usage cap and the laptop's cores) plus one haiku runner for boards.

## PHASE A -- 14:15-16:00: the PILOT runs (started 14:15)
RUNNING: `solver-pri97` (main assertion = cue knowledge in the attachment arm) and `solver-pri98` (manner-encoded harm = intensity
read in force_dynamics_valence), opus agents, each with the brief verbatim + the six mandatory phases (read / build+measure /
status probe / quality push / verdict check with "path A" on PARTIAL / finalize with SOLVED.md + patch .diff). Also running:
`board-final3-runner` (the final board with pri 93/15 landed; the earlier run died with its stopped watcher).
Strategy (me) during A: supervise only -- on a completion notice read the report; if it stopped before phase 6, SendMessage the
next phase verbatim (one nudge); if PARTIAL, send "what would it take to make this fully solved -- pick path A and try it once";
log every nudge with a timestamp in `notes/SOLVER_AGENT_PILOT_2026-09-13.md`. Record the final board when it lands (ledger,
scorecard, STATUS, BOARD_TREND). Then the light desktop shipment (`resync_light.sh` on a haiku runner).

## PHASE B -- on each pilot completion: THE TEST (pass/fail, written to the pilot log)
A pilot session PASSES if ALL hold:
1. **Reached phase 6, then completed PHASE 7 (the owner's understanding + improvement probe, ALWAYS sent) with <= 2 further nudges** (the owner's sessions needed ~8 messages each, 5 of 33 judgment calls).
2. **Rubric met by its own report:** witness green; information-free twin loses CI-separated; the bar's primary metric up
   CI-separated on the item's own population (or a NUMBERED located negative naming the missing input); named no-regress
   populations hold; knowledge in counts/assets with an online observe path; SOLVED.md in the schema; a patch .diff, no hdlab edit.
3. **First-hand reverify by strategy:** re-run its experiment's reverify/self-test path under capped cores; the headline numbers
   reproduce within the CI; the patch applies cleanly to the current hdlab file.
4. **No rule violation:** files written only where the brief allows; no push; no preregs/arm_key touch; no off-the-shelf tool at
   inference; no retired figure quoted.
5. **Cost:** wall time and tool-call count recorded; PASS needs wall time <= the comparable owner-run session (coordination 2 h,
   object slot 3.3 h; the 12-14 h ones ran unattended overnight).
Quality is graded on the same axes as `notes/SOLVER_SESSIONS_EVALUATION_2026-09-13.md` (twins, paired CIs, independent human
golds, refuted levers counted, honest caveats). The verdict for the PROGRAM: **2/2 PASS = continue at full rate; 1/2 = continue with
the failure's cause fixed in the kick-off prompt first; 0/2 = stop, report, and return to owner-run hand-outs.**

## PHASE C -- if successful (16:00 onward): THE SOLVER-AGENT PROGRAM
**Mechanics landed today (strategy work, see "implementing now"):** `tools/solver_agent_prompt.py <slug>` emits the identical
kick-off prompt (brief path + hard rules + six phases) for every launch; `data/hook_state/assigned_problems.json` marks agent-taken
problems so the hand-out tab shows them as taken; `notes/SOLVER_AGENT_PILOT_2026-09-13.md` is the measurement log (one row per
session: start, end, nudges, tool calls, verdict, reverify, integrated).
**Queue (one organ per concurrent agent; no diff collision):**
1. **pri 94** PP attachment (obl/nmod seesaw) -- attachment_arm; start ONLY after pri 97's patch is landed (same file).
2. **pri 96** far coordination needs the meaning channel -- attachment_arm + meaning channel; after 94 or paired with a non-arm item.
3. **NEW brief (strategy writes during C): embedded and copular SUBJECTS at the labels rung** (the role competition loses nsubj under
   ccomp/xcomp and in copular clauses; the plan's "governor residuals = labels rung" item) -- graded_role_assigner.
4. **pri 99 (WRITTEN 14:50): unseen words read by form and position (names vs common nouns)** -- was: unknown-word coverage of the category organ (0.752 on unseen words; the reading-acquired inventory covers only
   what 1M lines showed; the brain generalises by form) -- lexical_categories + induced_categories.
5. **NEW brief: the nmod give-back after the teacher v2 promotion** (0.311 -> 0.358 with meaning cues; still the weakest
   comprehension-relevant nominal relation) -- may fold into pri 94.
Each completion -> strategy reverifies first-hand -> presents in the tab -> integrates top-down on DONE (or on reverify if Q answered
yes) with a board A/B per integration, ledger row, scorecard line, INTEGRATED mark, owner update if significant.
**Strategy's own chain work in the gaps** (never idle while agents run): the math-BF top-down pass items still open -- the heads
rung's live-chain number under the organ's own tags (0.598) vs gold tags (0.6125): trace the 1.5-point tag loss per relation;
the typed-SP / GEK stores' consumers after the re-key; BRAIN_MATH_REFERENCE rows for today's landings (incremental governor, lag-2
categories, collision rule, perceived-heads validities).

## PHASE D -- evening (20:00 onward) and overnight
Keep two agents running from the queue; after each integration wave run `resync_light.sh`; before any compaction write the memory
handoff (`project_live_chain_organs_and_switches_2026-09-13.md` update + the pilot verdict as its own memory) and the STATUS block.
Owner check-ins expected: DONE marks in the tab; Q on the integration gate; whether 94/96 stay owner hand-outs (default below).

## Decisions filed / defaults taken
- DEFAULT: pri 94 and 96 move to the agent queue (the owner's "continuing to implement these solver sessions as agents"); they stay
  visible in the tab until an agent takes them, then are marked taken. If the owner starts one first, the agent is not launched.
- Q filed on the board: may agent-produced solutions be integrated on strategy's first-hand reverify (with a board A/B) instead of
  waiting for DONE? Recommendation: keep DONE for the two pilot sessions, then allow reverify-gated integration to remove the human
  bottleneck, with every integration still presented in the tab and reversible (assets kept at data/hook_state/*_prev).

## Log (appended through the day)
- 14:15 pilot launched (pri 97, pri 98; opus agents); board_final3 launched (haiku runner).
- 14:24 gap work: tag->head loss attributed (VERB-as-AUX = 58% of the 1.56-point loss); building the frequent-frame cue in the category organ.
- 14:38 final board 0.6352 recorded; 14:41 light shipment done; 14:35 frame cue blanket form refuted, chunk form drafted (run DENIED -> parked); 14:50 pri 99 brief written (unknown words).
- 15:15 PILOT SESSION 1 DONE (pri 98): 57 min, 0 nudges, SOLVED by report; reverify runner launched; patch `git apply --check` clean (5 hunks, additive; switches HDLAB_FDV_MANNER_READ / HDLAB_FDV_MANNER_PROSE both default on; new asset manner_intensity_v1.json). INTEGRATION PLAN on DONE: (1) apply the diff; (2) rebuild the asset; (3) witnesses: verification/test_fd_upstream_joins_landing.py (22/22), test_fd_result_state_arm.py, test_board_state_closure_and_affect_harm_help.py (17/17); (4) the live 36-item gold (experiments/exp_fd_harm_help_live_modern_v1.py) and the real-prose affected-entity probe (standing 0.393) with RUNG 5 on vs off -- the board has no affect dimension, so these two are the no-regress check; (5) ledger row + scorecard line + INTEGRATED mark + brain-math row (manner/result complementarity; circumplex radius); (6) file the 'treat' cross-sense conflation as a brief (sense-keyed affect norm). Kick-off prompt amended (denied step not to be done another way).
- 15:22 session 1 PASS (reverified); pri 99 launched (slot 2); pri 97 still running (72 min).
- 15:51 weighted role table: subjects recovered (matrix nsubj 0.714 -> 0.776 live; 0.748 -> 0.830 gold heads), objects kept; board A/B running.
- 15:55 owner correction: phase 7 probe is mandatory for every session; sent to pri 98; pilot row reopened.
- 16:03 owner mandates (signal-loss trace / upstream BF per signal / brain math per chain / negatives understood / why the wins won) sent to 97, 98, 99; baked into kick-off phases 3, 5, 6.
- 17:17 all three pilot sessions CLOSED (97 SOLVED, 98 SOLVED, 99 PARTIAL-by-bar); briefs 101-104 written; slots: pri 100 (17:14) + pri 103 (17:17) running; 94/96/101/102/104 wait for pending patches to land (DONE gate).
