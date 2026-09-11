# OVERNIGHT PLAN — 2026-09-11 (autonomous, owner-authorized)

**Owner directive (2026-09-11):** *"Create an overnight plan with everything you can be doing to optimize
and set up the substrate for success. You can BF organs yourself, integrate organs, plan, etc. Make it
right, not easy."* + *"turn on your stophook"* (ARMED, unlimited, scoped `auto_d9672062a6`).

**This file is the overnight recovery anchor.** After a compaction, read `notes/STATUS.md` → this file →
resume the top unfinished workstream. The LEDGER + `git log` OUTRANK recollection. Update this file in
place as items land (check the boxes, add the commit hash).

---

## OPERATING RULES (unattended — these are hard constraints, not preferences)
- **RIGHT NOT EASY.** Every landing is the brain's actual mechanism (PINNED, or a defensible computational
  model). A NOT_BF fix must be a genuine PINNED/BF replacement, NEVER a convenient stand-in adopted for a
  metric. A cheap probe may MEASURE, never SET DIRECTION. When a choice is unpinned, mark it OUR-INVENTION
  and say so — do not mislabel.
- **VERIFY EVERYTHING.** No landing without (a) a first-hand witness reproducing the claim and (b) board
  no-regress (self-test at minimum; a full `--run` for anything that could move a scored dim). Deflate
  claims; a construction-proof is not a capability.
- **COMMIT PATH-LIMITED, NOTHING PUSHED.** `git commit -m "..." -- <paths>` only — NEVER `git add -A`,
  never a bare `git commit` after staging (a concurrent fleet session shares the index). Only the
  orchestrator pushes (its lane is auth-gated). Never edit `preregs/**` or `arm_key*` (harness-denied).
- **OWNER-DONE GATE.** Integrate ONLY on `owner_verdict: DONE`. Never front-run a WIP/SOLVED submission
  (owner's vetting). Reverify first-hand before landing; land ALL upstream-chain fixes, accept downstream
  breakage and fix it to receive.
- **CORES CAPPED** on every run: `OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 MKL_NUM_THREADS=4` (+ `PYTHONHASHSEED=0`
  for the board). Heavy/long runs → detached background or remote; the brain does NOT do long offline training.
- **DON'T WEAKEN A GATE.** If blocked on an owner decision, file it on the board (`python tools/board.py ask`)
  with a plain-language recommendation and MOVE ON. Only stop/kill THIS session's own spawns. 19c corpora
  (McGuffey/LitBank) banned for grading — modern gold only.
- **FRONT DOOR each cycle:** `python tools/substrate_health.py` → act on TOP ISSUES worst-first.

---

## WHERE THINGS STAND (as of the plan's writing — verify on disk, do not trust this after edits)
- Health: 83 organs, BF=7 BF_SPIRIT=69 NOT_BF=8. Board aggregate 0.6253 (1.3d old). Gates: 2 FAIL
  (owner-DONE fold-in backlog=2; a BF-ledger tracking gap). Assignable fleet queue: was 1 (coref
  consolidation) → now 3 after tonight's refill so far.
- **8 NOT_BF (the defects):** parser cluster `pos_tagger`/`arc_parser`/`arceager_parser`/`parse_confidence`/
  `arc_labeler` (→ pri-3 PARTIAL, owner-DONE + the reading-learned successors, fleet); `force_dynamics_valence`
  (→ harm_help SOLVED, awaiting owner verdict); `commonnoun_binder` (→ pri-4 owner-DONE, LANDING tonight);
  `scene_segment` (dead/superseded — mine-side to resolve).
- Owner-DONE awaiting fold-in: `the_common_noun_binder...` (pri-4) + `who_was_affected...` (both LANDING tonight).

---

## ✅ PROGRESS (overnight, updated 2026-09-11)
- **WS1a who_was_affected FULLY INTEGRATED (all 3 lands)** — organ `hdlab/affected_entity_resolver.py` (`8acc84ebf`) + **read()-time `sm.affected_entity` dimension** (`c0d612dad`, witness 6/6, board no-regress — re-landed after correcting a degenerate-test misdiagnosis) + `board_affected_entity_dimension` **CI-sep at full power** (n=715; `65e507c86`).
- **WS1b pri-4 INTEGRATED** — full board `--run` confirms `commonnoun_resolution` **0.5818 vs de-leaked floor 0.5156 CI-sep (n=2855)** (`c656ae0c6`).
- **WS2a + WS6a** — BF-ledger gate fixed; fresh authoritative board persisted (aggregate **0.6253**, n=11218, no-regress). **ALL 5 HEALTH GATES GREEN.**
- **WS3a/3b/3c** — queue refilled **+3** (pri-1 generative reranker, pri-8 reading-learned POS induction, pri-9 grounding-quality metric) + brief cert fixed.
- **WS4a** — 8th NOT_BF resolved: `scene_segment` retag NOT_BF→BF_SPIRIT (mis-attributed to dead `detect_scene_boundaries`); **NOT_BF 8→7** (`170e6b047`).
- **WS2c** — Q128 filed (brief-format governance decision). **WS8a** — knowledge assets audited = correctly LATENT (pri-5/pri-1-gated), no wire.
- **REMAINING (measured standing work):** WS7a wiring burn-down (per-island board runs; many islands correctly-off — do measured, one at a time, not churn), WS5a consolidation folds (deep merges are fleet-gated; coref-6→1 flagship posted pri-6).

## 🎯 NEXT MEASURED WORK (scoped for a fresh pickup — instrument-gaps: board-invisible-proven-wins-need-their-own-arm)
Do these ONE at a time, each: build the board arm wrapping the win's OWN experiment (like `board_affected_entity_dimension` wraps `exp_affected_entity_binding_parallelism_gum_v1`) → register in the run harness `new_arms` (its own row, OUT of the headline aggregate, OFF in self-test) → smoke-verify standalone → board self-test no-regress → commit. Full `--run` (or the orchestrator's) confirms the full-power number.
- **`board_causal_sign_dimension`** — ✅ **DONE (`24765b7a6`, built HONESTLY after careful full-scale measurement).** `causal_sign_channel` was board-invisible; the arm wraps `exp_causal_sign_integrated_v1` (byte-faithful to the channel) on the WIQA gated science slice (n=553, 14.2% cov). **KEY HONEST FINDING (measured full-scale — a naive wrap would have been a DEFECT):** the formal sign BEATS the scrambled-sign FALSIFIER CI-sep (+0.067–0.101 by seed; the load-bearing "structure is not chance" result, first sign source to do so — the registered claim holds) BUT does NOT add over the CO-OCCURRENCE baseline CI-sep (+0.01–0.02; on the covered slice raw co-occurrence direction often matches the formal sign). The board row shows this honestly (strongest_floor=cooccur not-sep, twin=falsifier CI-sep). The `formal_couplings` broad model + the general subset DILUTE to a tie — only the gated integrated science slice (14.2%) shows the falsifier win. Original note (superseded): ⚠️ **CAUTION (investigated 2026-09-11, DO NOT naively wrap):** `exp_causal_sign_integrated_v1.run()`'s GENERAL `SIGN_more_vs_less_on_gated_subset` TIES/LOSES the falsifier (smoke n=300, cov 13%: arm 0.516 vs scrambled 0.548, paired −0.032 CI incl 0) — it is DILUTED (promiscuous quantities like water/energy/heat bind the WRONG model, per the experiment's own header). The +0.157 CI-sep is a specific **SCIENCE-SLICE** subset at FULL scale, NOT the general gated subset. So a naive wrap of the integrated run() would ship an arm showing causal_sign LOSING — a measurement DEFECT. FIRST identify the exact science-slice filter/cell that isolates the +0.157 (likely `exp_causal_sign_formal_couplings_wiqa_v1` on its physics/thermo science domain, or a domain filter on the integrated rows), reproduce THAT, and score the LANDED channel (`causal_sign_channel.causal_edge_sign`) on it for a true live==scored arm. FURTHER FINDING (2026-09-11): even the stoichiometry science PoC smoke (n=13 cov) is far too small for CI-sep — the +0.157 needs the FULL cap=6000 run; `formal_couplings_wiqa` "grows the science-slice coverage" so it is the likely source. A full run of it was launched to settle the exact number/slice before building the arm.
- **`board_event_goal_congruence` for `affect_structured_matcher`** — its proven +0.483 lives on the event↔goal-congruence gold, not the OCC arm (INTEGRATION_LEDGER line ~370); check whether the existing `board_event_goal_congruence_dimension` already scores it (may be closed) before building.
- **SpaceEval-precision arm** for the obl-spatial +0.0102 upstream win (line ~181, live≠scored).
- **`board_predictive_causal_necessity_dimension`** already exists (line ~113) — DONE, do not rebuild.

## WORKSTREAM 1 — CLOSE THE OWNER-DONE INTEGRATION BACKLOG  *(the FAILING gate; #1 blocking; do FIRST)*
### 1a. `who_was_affected...forward_salience_prior` (owner-DONE, reverified 10/10)
- [x] Land 1/3: promote the BF resolver → `hdlab/affected_entity_resolver.py`; experiment imports it (witness 4/4 = the organ). Registry +1. `8acc84ebf`.
- [ ] Land 2/3: additive `sm.who_was_affected` / `sm.affected_entity` dimension via a new `_read_affected_entity` in `situation_reader` — resolve pronoun undergoers to the salient discourse entity over the LIVE mentions + parse, using the organ. Default-on, BYTE-IDENTICAL off (pure add, like `_read_senses`/`_read_bridges`). Witness: byte-identical off vs on + the live path reproduces the deployment win. CAPABILITY_FLAGS + `__init__` flag.
- [ ] Land 3/3: `board_affected_entity_dimension()` reusing the experiment cell (the scored proof; the win is board-invisible today). Full board no-regress.
- [ ] Docs: §2b durable entry (the two-half machine now has its FORWARD-half grammatical-likelihood organ landed; the ~40% residual → the generative reranker pri-1), BF ledger row, INTEGRATION_LEDGER row, mark PROBLEM.md `status: INTEGRATED` + INTEGRATED_BY_STRATEGY marker. Commit path-limited.

### 1b. `the_common_noun_binder...typed_coref` (pri-4, owner-DONE — CORE + bridges + board-sync already landed)
- [ ] Full-board `--run` (detached, core-capped) to verify **0.5818** on `board_commonnoun_resolution_dimension` (the capped self-test dim didn't visibly move — likely a different/underpowered dim vs the full n=2855).
- [ ] Live-consumer faithfulness witness: live `_resolve_commonnouns` == `resolve_param` on GUM (proves the board copy ≡ the live path).
- [ ] Board-floor honesty: adopt the de-leaked **0.5254**, retire the 0.5412 redaction see-through leak in the board's `common_noun` floor.
- [ ] Optional: `boundary_nphead` raw-text head + Nref cheap wire (measure first; skip if inert on the gold board).
- [ ] Mark `status: INTEGRATED` + marker + INTEGRATION_LEDGER. Commit path-limited.

## WORKSTREAM 2 — SUBSTRATE HYGIENE / GATE FIXES  *(fast; keeps the derived views honest)*
- [ ] 2a. Fix gate #2: add `wire_the_context_gated_sense_read` to `notes/BF_COMPONENT_UPDATE_LEDGER.md` (it carries BF-bearing updates; the health gate flags it MISSING).
- [x] 2b. Brief-cert conformance: the 3 fleet-authored briefs lacked the 8 guard sections (cert was RED, blocking all `notes/problems/` commits). Appended faithful guard blocks → cert 8/8 green. `52331d95e`.
- [ ] 2c. Governance note for the owner (board or COMMENTARY): fleet-authored briefs use a different heading format than the 8-section strategy template the cert enforces → propose either a fleet brief template or a cert that scopes section-enforcement to OPEN (assignable) briefs. Do NOT unilaterally weaken the cert; file the decision.
- [ ] 2d. Re-run `substrate_health.py` after each workstream; drive TOP ISSUES to zero.

## WORKSTREAM 3 — FINISH THE QUEUE REFILL  *(fleet un-idle; owner: "refill that queue")*
- [x] 3a. pri-1 `generative_entity_state_reranks_which_entity_is_the_affected_undergoer` (the north-star convergent lever; who_was_affected BUILD 5 + type_generalized #1). `52331d95e`.
- [x] 3b. pri-8 `reading_learned_pos_category_induction_from_prediction_not_a_supervised_tagger` (the "gating link"; distinct from the in-review pos_tagger/arc-scorer). `8c78886b2`.
- [ ] 3c. pri-9 `grounding_coverage_quality_metric` — an independent-gold correct-LINK quality metric for the grounding loop (measure_end_to_end #2: `n_grounded` count can't show a quality gain). Dedup vs the eval-bank folders.
- [ ] 3d. If the fleet drains these: post `per_spoke_reliability_weighted_meaning_fusion` (survey #7, Ernst-Banks so the fused ATL hub beats grounded-alone) + `coref_ambiguity_abstain_wire` (survey #8, cheap standalone). Dedup-verify each first. HOLD `joint_pos_parse_graded_decode` + `eisner_2nd_order_em` (overlap the in-review parser submissions — post only after the owner verdicts those).

## WORKSTREAM 4 — BF THE SUBSTRATE MYSELF  *(the SPINE — "right not easy"; every component 100% BF)*
- [ ] 4a. `scene_segment` (NOT_BF, "dead/superseded or no mapped problem"): enumerate its live consumers (grep `situation_reader` + all of `hdlab`). If genuinely dead → prune the organ + its registry row (dormant ORGANS are never pruned, but a dead VERSION is; verify it's not a dormant-but-valid dimension first). If live → BF it (name the brain structure) or file a fleet problem. Resolve the 8th NOT_BF one way or the other.
- [ ] 4b. Fresh BF audit sweep: confirm ZERO BF_UNVERIFIED remain; spot-check that each BF_SPIRIT organ's `__bf_note__` still matches its code (the "verify before recommending" discipline). Any drift → correct in place (tag + registry + `__bf_corrections__` together).
- [ ] 4c. The remaining NOT_BF are fleet-gated (parser cluster pri-3; force_dynamics pri-7; commonnoun pri-4) — do NOT front-run; ensure each is tracked in the BF ledger with its resolving problem. If any is a SMALL fitted stand-in with a clear PINNED replacement I can land without a research problem, land it (measure no-regress).

## WORKSTREAM 5 — AGGREGATE BF: CONSOLIDATION  *(anti-fragmentation; one structure = one organ)*
- [x] Flagship posted: `consolidate_the_six_coreference_organs...` (pri-6, fleet).
- [ ] 5a. Trivial mine-side folds from `BRAIN_STRUCTURE_CONSOLIDATION_AUDIT.md` where byte-identical + net-neutral (e.g. `sensorimotor_spoke`). Prove byte-identical before + after; commit path-limited. Do NOT attempt the deep merges mine-side (those are fleet problems).
- [ ] 5b. Stagger the remaining deep merges as fleet problems ONLY if the queue thins (temporal 6→?, thematic split, force) — each dedup'd + cert 8/8. Don't over-post.

## WORKSTREAM 6 — BOARD / INSTRUMENT HEALTH  *(measurement hygiene)*
- [ ] 6a. After WS1 lands, run ONE fresh full board `--run` (detached, core-capped, `PYTHONHASHSEED=0`) → a current authoritative aggregate + trend point (the on-disk one is 1.3d old and predates tonight's landings). Persist `metrics.json`; update the health view.
- [ ] 6b. `board_affected_entity_dimension` (WS1a-3/3) makes the who_was_affected win scored, not latent — the "a board-invisible proven win needs its own instrument-arm" discipline.

## WORKSTREAM 7 — WIRING BURN-DOWN  *(dormant → live; no-more-default-off)*
- [ ] 7a. `python tools/wiring_debt.py` → the top default-off islands. For each, MEASURE live board impact; TURN ON if net-positive (impact-analyse + flip; a break = a subpar downstream to fix on its own gold, not a reason to keep it off). OFF only for a genuine INVARIANT. One at a time, gate on net-positive + no-regress, commit path-limited. Log anything left off + why (no silent caps).

## WORKSTREAM 8 — KNOWLEDGE ASSETS LIVE  *(landed ≠ live)*
- [ ] 8a. Audit `notes/KNOWLEDGE_ASSET_REGISTER.md` for LATENT assets whose live consumer is NOW live (e.g. after WS1/WS7 flips). Wire the ones that are ready; keep correctly-latent ones latent (verify, don't mislabel). Grep `situation_reader` for a REAL live consumer before calling anything done-live.

---

## EXECUTION ORDER (the autoloop walks this top-down; blocking-first)
1. **WS1a** (who_was_affected land 2/3, 3/3, docs) — highest leverage owner-DONE, the new solution, in flight.
2. **WS1b** (pri-4 finishing) — kick the full board `--run` early (it doubles as WS6a); do the faithfulness witness + floor honesty while it runs.
3. **WS2a/2c** (gate #2 fix + governance note) — fast, clears a health gate.
4. **WS3c/3d** (finish the queue refill) — keep the fleet fed.
5. **WS4a** (scene_segment — resolve the 8th NOT_BF mine-side) — the "right not easy" BF spine.
6. **WS7a** (wiring burn-down, one island at a time) + **WS8a** (knowledge-asset live audit) — deeper optimization.
7. **WS5a** (trivial consolidation folds) — aggregate BF where safe.
8. Re-run `substrate_health.py`; if all gates green + queue healthy + board fresh, do the next-worst TOP ISSUE.

## WHAT NOT TO DO OVERNIGHT (guardrails)
- Do NOT push anything. Do NOT front-run a WIP/SOLVED submission (owner-DONE only). Do NOT weaken any gate
  (cert/BF/board/health) — file the decision instead. Do NOT `git add -A` or bare-commit. Do NOT edit
  `preregs/**`/`arm_key*`. Do NOT adopt a convenient stand-in for a NOT_BF organ to move a number. Do NOT
  do a long offline training run. Do NOT grade on 19c. Do NOT start a big new build the plan doesn't name —
  if a genuinely new high-leverage direction appears, file it as a fleet problem and note it here.
