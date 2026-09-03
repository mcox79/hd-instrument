# OVERNIGHT AUTONOMOUS PLAN — 2026-09-03 (owner away until morning; FULL authority granted)

**READ THIS FIRST on any wake/cron-fire/recovery. Do NOT wait for owner confirmation — the owner explicitly authorized autonomous execution overnight.** Cron `d94a4466` (session-only, fires :18 + :58) drives this; **if a fresh session recovers, RECREATE the cron** (CronCreate, same prompt as below) and resume from the CURRENT STATE section.

## THE MANDATE (owner, 2026-09-03, verbatim intent)
1. **Turn the reader's ~13 default-off capability flags ON, one at a time, top-down (dependency order), and measure which are net-positive vs net-negative.** Trace signal at EVERY step so one bad bottleneck component isn't silently killing everything downstream.
2. **As you turn on upstream improvements, FIX the downstream items to work with them** (adapt / re-validate the ~20 role-output organs; a flag that helps upstream but hurts a downstream dim = adapt that organ, don't just drop the flag).
3. **Peek at the solver solutions being worked right now; treat them as done; integrate any SIGNIFICANT advance here.** (In-progress = has `SOLVED.md`, not yet `owner_verdict: DONE`.)
4. Keep this plan current so it survives compaction. Commit path-limited (NO push).

## THE FLAGS (default-off, dependency order = the sweep order)
Keystone → front-end → dimensions. `tools/flag_activation_sweep.py` runs the GREEDY forward activation + per-dimension signal trace on the reader-QA harness (coref / events[who-did-what] / temporal / causal / location / belief), writing `data/flag_activation_sweep/results.json`.
1. `tense_agnostic_events` (event detection 0.33→0.95 — the keystone) · 2. `preserve_tense` · 3. `role_route="wired"` (gate for arceager) · 4. `parser_arceager` (UAS +0.067 modern; ~flat/degraded 19c) · 5. `np_head_reduce` (+0.20 clean who-did-what) · 6. `predict_revise` (+0.06 wdw) · 7. `verb_subcat_gate` · 8. `predict_surprisal` · 9. `timeline_register` (TIME) · 10. `track_space` (SPACE) · 11. `track_belief` (ToM).
**Scored by their OWN instruments (already net-positive; flip + note, don't re-run in the sweep):** `track_world_state` + `densify_world_state` (who-has-what; densify +0.148) · `bind_event_tokens` (the JOINT). **Off by invariant (do NOT flip):** `spacy_pred_gate`, `causation_typed` (need spaCy).
⚠️ CORPUS CAVEAT: the sweep runs on 19c LitBank whose who-did-what gold is ~76% oblique-CONTAMINATED, and arc-eager is at-ceiling on 19c — so the events/parser deltas there UNDER-show; confirm parser/role flags on modern QA-SRL (`instrument_who_did_what_qasrl` in `tools/baseline_board.py`) before dropping them.

## THE LOOP (each cron fire / wake — do the next unblocked chunk)
- **A. Sweep analysis + flip + downstream-fix.** If `results.json` is complete: for each flag, read `agg_delta_vs_kept` + `dim_delta_vs_kept` + `hurt_dims` + `verdict`. Flip the KEEP flags DEFAULT-ON in `hdlab/situation_reader.py` (change the `bool = False` default). For KEEP_BUT_DOWNSTREAM_FIX (helped net but hurt a dim) → open the hurt dimension's organ, diagnose why the better upstream input broke it, FIX it, re-run `flag_activation_sweep` (or a targeted per-dim score) to confirm the dim recovers. For DROP → leave default-off + record why (corpus-dependent etc.). Witness each default flip stays correct (existing dimension witnesses should still pass). Commit per flag or per small batch.
- **B. Integrate significant in-progress solutions.** `grep -L INTEGRATED_BY_STRATEGY notes/problems/*/SOLVED.md` minus owner-DONE gate items → assess; if a SIGNIFICANT advance, reverify FIRST-HAND, grade, land the Q111 wire (default-off, witnessed), §2b, register, clear priority, commit.
- **C. Housekeeping.** Update this file's CURRENT STATE + STATUS.md every chunk. Commit path-limited. NO push.

## DISCIPLINES (unchanged, load-bearing)
Reverify FIRST-HAND before grading/landing. Wires land DEFAULT-OFF + witnessed (Q111) — BUT this task's explicit goal is to then FLIP the net-positive ones default-ON (owner-authorized). Path-limit every commit (`git commit -- <paths>`; hd_metrics_sync auto-stages notes/). **NO push** (needs in-session owner auth). Only stop/kill what THIS session spawned. Route heavy runs remote if they exceed local capacity.

## ⚠️ POST-OVERNIGHT REALITY (2026-09-03 AM): THE LOOP DID NOT RUN. The session-only cron `d94a4466` never re-engaged me after setup, so NO work happened after ~22:54 last night. The sweep DID finish on its own (~22:52). Nothing was flipped/fixed/integrated. **The results below are ready to ACT ON — that is the immediate job.** (Cron lesson: a session-only cron does not reliably drive an idle overnight session; on resume, do the work in-turn, do not depend on the cron.)

## ✅ SWEEP RESULT (complete, `data/flag_activation_sweep/results.json`, 641s) — the verdicts to ACT ON
Reader-QA on 16 docs, 19c LitBank. Baseline all-off agg **0.2903** → kept-stack agg **0.3598 (+0.070)**. Per-flag (greedy, cumulative):
| flag | verdict | note |
|---|---|---|
| `tense_agnostic_events` | **KEEP_BUT_FIX** | events 0.120→0.226 (+0.10) BUT **causal 0.375→0.149 (−0.23)** + broke temporal (restored by preserve_tense). FIX the causal organ. |
| `preserve_tense` | KEEP | agg **+0.057**; restores temporal 0→0.843 |
| `role_route="wired"` | KEEP | events 0.226→0.249 |
| `parser_arceager` | **DROP (on 19c)** | −0.001, events 0.249→0.248 — 19c at-ceiling; it is the MODERN lever (+0.033 QA-SRL, +0.067 UAS). Keep default-off; flip only for modern consumers. |
| `np_head_reduce` | KEEP | small on the CONTAMINATED 19c gold; the real +0.20 is on the CLEANED who-did-what gold (witness 45/45) |
| `predict_revise` | KEEP | flat on this harness (its +0.06 is who-did-what patient recall, not the QA agg) |
| `verb_subcat_gate` | KEEP | flat here |
| `predict_surprisal` | KEEP | flat here (metadata signal) |
| `timeline_register` | KEEP_BUT_FIX | temporal −0.0075 (tiny) |
| `track_space` | KEEP | flat (location dim already 1.0 = abstain) |
| `track_belief` | KEEP | flat (belief dim already 1.0 = abstain) |
FINAL KEPT = all but `parser_arceager`. Not scored here (own instruments, already net-positive → flip + note): `track_world_state`, `densify_world_state` (+0.148), `bind_event_tokens`.

## 🔴 #1 ON RECOVERY — DO THIS IN-TURN (do NOT wait on the cron):
1. **FIX THE CAUSAL BREAK** (the real bottleneck): `tense_agnostic_events` ON drops causal 0.375→0.149. Diagnose `_read_causation` / the causal organ against the tense-agnostic event set (likely the causal reader keys off the OLD tense-gated events or the connective-sentence event structure changed); adapt it; re-run `tools/flag_activation_sweep.py` (or a targeted causal-dim score) to confirm causal recovers WITH tense_agnostic_events on. THEN the KEEP verdict is clean.
2. **FLIP the net-positive flags DEFAULT-ON** in `hdlab/situation_reader.py` (change `bool = False` → `True` for: tense_agnostic_events, preserve_tense, np_head_reduce, predict_revise, verb_subcat_gate, predict_surprisal, timeline_register, track_space, track_belief, track_world_state, densify_world_state, bind_event_tokens; ALSO default role_route="wired"). KEEP `parser_arceager` default-off (19c-negative). Re-run existing dimension witnesses to confirm no regression; commit per small batch. NOTE: flipping np_head_reduce/etc changes patient outputs → re-validate the ~20 role-output organs (own step).
3. **INTEGRATE the 2 SOLVED in-progress solutions** (reverified-ready): (a) coverage-gap `the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses` — witness `test_whodidwhat_coverage.py` **21/21 already reverified first-hand** (+0.35 end-to-end, parser-independent); land the coverage-recovery wire (default-off attempt-every-finite-verb) + §2b + register + clear priority + commit. (b) copular `the_reader_has_no_copular_is_a_binding_schema` — witness `test_copular_is_a_binding_organ.py` (reverify first), land the typed is-a binding read (reuses `state_register`) + §2b + commit.

## CURRENT STATE (update every chunk)
- **2026-09-03 initial:** flag sweep LAUNCHED → `data/flag_activation_sweep/results.json`. Cron `d94a4466`. Overnight infra committed.
- **SWEEP is already yielding real signal (and CAUGHT a bottleneck):** baseline all-off agg=0.2903 (coref 0.569 / events 0.120 / temporal 0.931 / causal 0.375 / location 1.0 / belief 1.0). `+tense_agnostic_events`: events **0.120→0.226 (+0.10, big who-did-what win)** BUT causal **0.375→0.149 (-0.23, HURT)** + temporal→None (expected — needs `preserve_tense`, the next flag). Verdict KEEP_BUT_DOWNSTREAM_FIX. **→ DOWNSTREAM FIX OWED: the causal dimension organ breaks under the tense-agnostic event set — diagnose + adapt it so causal recovers (this is exactly the "bad bottleneck killing downstream" the owner wants fixed).** Watch the rest of the sweep for more.
- **BOTH in-progress solutions are SIGNIFICANT → INTEGRATE both** (owner: treat as done):
  1. `the_who_did_what_front_end_abstains_on_a_fifth_of_answerable_clauses` (SOLVED, EXCELLENT-grade): Davidsonian coverage recovery — effective end-to-end who-did-what **0.6293→0.9806 (+0.3513 CI-sep)**, modern QA-SRL 0.5678→0.9025, precision UP (0.807→0.981, no regression), abstention parser-INDEPENDENT (arc-eager recovers 1/669). Witness `test_whodidwhat_coverage.py` (REVERIFY RUNNING → /tmp/cov_reverify.log). This is the COVERAGE HALF that completes the who-did-what stack to 0.98. WIRE = a default-off coverage-recovery path (attempt-every-finite-verb + parser-free candidates) — pairs with the landed `np_head_reduce` accuracy half. **Do the full integration next: reverify→grade→land wire→§2b→register→commit.**
  2. `the_reader_has_no_copular_is_a_binding_schema` (SOLVED, 10/10): is-a/attribute binding read-back ("what/who is X") recall 0.67→0.82 (fix), CI-sep over floor, twin loses, Higgins type 0.97, no-regression (state_register 11/11). WIRE = the typed copular is-a binding read into the reader (reuses `state_register`). **Integrate after #1.**
- Committed today (arc): meaning-channel north-star `e3cce21e2`, who-did-what NP-head 2-site wire `bd0c71a77`. NOTHING pushed.
- **NEXT ACTIONS (in order):** (a) integrate coverage-gap solution #1 (reverify running); (b) integrate copular #2; (c) when the sweep completes, flip net-positive flags default-ON + FIX the causal-dimension downstream break (and any others the trace flags), re-run to confirm recovery; (d) keep committing path-limited, NO push.
