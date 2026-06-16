# SKUNKWORKS post-compaction handoff 2026-06-16 PM (READ FIRST; supersedes the morning 2026-06-16 handoff)

You are SKUNKWORKS = AUDITOR of hd-instrument. Director=Research, Prover=Exp-Dev, Integrator=Testbed, Custodian=Orchestrator. Shared event-bus; full-auto authorized.

## STEP 0 -- cycle-check + DUAL-LAYER monitor (do BEFORE anything)
1. `bash tools/skunkworks_cycle_check.sh` (inbox authoritative + producer liveness; run EVERY cycle).
2. Re-arm BOTH monitors (the canonical dual-layer, DECISION 161):
   LAYER 1 (real-time): Monitor(persistent, 3600000, `while true; do tail -n0 --retry -F /d/AI/hd-instrument/data/events/skunkworks.log 2>/dev/null | grep --line-buffered -E 'ROUTING|BROADCAST' | grep --line-buffered -v 'notes/skunkworks_'; sleep 2; done`)
     KEY: filter MUST be `ROUTING|BROADCAST` (NOT ROUTING-only -- ROUTING-only silently DROPS research_to_all_* DECISION broadcasts; USER-caught + fixed this session). `--retry` survives producer restarts. author-out `notes/skunkworks_` = ALL my notes.
   LAYER 2 (13th-rule heartbeat, every ~12 min): Monitor(persistent, 3600000, `while true; do sleep 720; echo "[active-state-check $(date +%H:%M)] $(bash /d/AI/hd-instrument/tools/skunkworks_cycle_check.sh 2>/dev/null | grep -E 'INBOX unread|PRODUCER' | tr '\n' ' ')"; done`)
3. inbox `--seen` ONLY after reading listed notes (blanket --seen hazard). NOTE: tools/skunkworks_inbox.sh author-out was tightened to `skunkworks_*` (all my notes; was `skunkworks_to_*`).

## TWO USER-LOCKED RULES ADDED THIS SESSION (MUST FOLLOW -- USER caught passivity TWICE)
- 13th rule: ACTIVE STATE-CHECK every 10-15 min between monitor events (the LAYER-2 heartbeat operationalizes it).
- 14th rule: NO-STAND-DEFAULT at phase boundaries + FORWARD-WORK-ON-EVERY-WAKE. On EVERY wake (event OR heartbeat): respond to the trigger AND generate forward auditor-lane work (don't just ack). USER caught BOTH the Director AND me defaulting to passive heartbeat-acking; the fix is generate-forward-work, not ack. Acking != forward work.
   (Composes with 9th monitor-armed, 12th never-passive. Methodology stack FROZEN at 24 -- these are USER-LOCKED behavioral rules, not methodology-stack rules.)

## PHASE STATE (the big picture)
- PHASE A CONSOLIDATION = COMPLETE. 13 net-new load-bearing atoms (honest yield of "~20+ flagship"; smaller-but-true). Foundation hygiene Waves 1-3. Substrate ~26280 atoms / ~5165 rel / 206/206 axiom-term / cap_pres=1.0. Bilateral kappa external anchor measured.
- *** PHASE B GO FIRED -- NOW (Option C, DECISION 165, 2026-06-16 14:11) per USER "do it" directive (relayed by Testbed 189th). PHASE B BUILD IS ACTIVE. *** USER OVERRODE the Director+Auditor-converged Option B (2026-06-17) -- pulled GO to immediate. All technical preconditions MET (DECISION 168/169/170). NO blockers.
  - Graded runs FIRING (DECISION 165a): ARM 1 cardinality = 3 siblings x 4 configs (C0 graph-walk-trace / C1 basis-only / C2 +primitive / C3 +abstraction) = 12 cells, full-mode N=4096 n_seeds>=3 tier-A, vocab 50-200, mixed local-CPU + remote-GPU per 166b. ARM 2 ternary motif = math-scoped 20 / 5 effective families / non-DFT-closure-required. ARM 3 C3 = 100-step internal-abstraction-discovery (MDL compose-of-composes over 38-op basis; P_deflated=0.40 prior).
  - cardinality compute_verdict() PRE-REGISTERED IN CODE (my reconciled gates: exact-count C2-escapes-C0 + >=2x-C1 + <=1.0-RMSE within-envelope; quantifier EVADABLE-DROP@C1>=0.70 + C2>=0.80 + >=0.20-margin; 8 self-tests PASS; Lakatos no-ex-post). Ternary extractor: two-layer-scope + meta-cluster gates wired.
  - TIMING: first HARD-PASS/HARD-FAIL verdict expected T+15-30 min (~14:25-14:40); cardinality arm (12 cells) ~3-6 hr; full primary arms 1-3 days; comprehensive Phase B verdict 2-3 days. **My BUILD VET protocol (below) FIRES per-verdict -> relay each VET to Director + Testbed; Testbed ratifies HARD-PASS via template 1861e9e9 + cap_pres=1.0 HARD-FAIL gate.**
- PHASE C TIER-3 = HELD (USER decision; natural trigger = if cardinality-C3 FAILs as a true tier-3 boundary).

## MY BUILD VET PROTOCOL (fires on each graded verdict at GO -- the core post-compaction job)
CARDINALITY graded run -- ENDORSE only if ALL hold:
  C0 graph-walk-trace control instrumented; C2 ESCAPES (beats C0 + C1 by Drill-1 margins: exact-count RMSE<=1.0 + >=2x; quantifier acc>=0.80 + >=0.20). C1 FAIR-NULL (best-honest-basis, crosstalk-subtracted; fails for CARDINALITY reason) + single-role CONFOUND-ISOLATION. C2 within CAPACITY-ENVELOPE (regime-calibrated alpha; out-of-envelope low score = ARTIFACT not FAIL). per-sibling metric TYPES (exact-count=RMSE/AGGREGATE; quantifiers=accuracy/RATIO). all 3 sibling probes {exact-count, at-least-k, most}; control-leak-free identical input; run_mode=full n>=3.
TERNARY graded run -- ENDORSE only if ALL hold:
  CLEAN-SYMMETRY two-layer scope (RELATES-excluded + MATH-corpus-scoped; document/provenance anchors dropped). 38-op BIMODAL full-basis equivalence-check (C2 corr(bundle,c) closes where ALL 38 single binders fail; the ghrr lesson -- no single-op exclusion). no-gerrymander (real mined motifs) + vector-native (bundle+corr) + sibling sym/asym controls. AT-THRESHOLD fragility (math-scoped MOTIF-B = 20 EXACTLY at >=20 bar; require majority-close, not razor count). PER-EFFECTIVE-FAMILY: ~5 families (DFT-meta 45% dominant; require >=2 NON-DFT closure for GENERAL claim; DFT-only = Fourier-specific not general).
C3 (both arms): discovery!=leakage (seed EXCLUDES the C2 composite). reusability (PROVABLY_EQUIVALENT_BY_CAPABILITY + 2nd-signature, not just >=0.80). cardinality-C3 FAIL: DISTINGUISH search-limited (tuning) vs tier-3-boundary (USER-architectural Phase-C trigger). ternary-C3 = definitively-tier-2 pure-discoverability (FAIL=search-limited ONLY).
COMPUTE-BACKEND gate (GPU/CPU): record backend+dtype; near-threshold verdicts (within ~1e-3 of bar) cross-checked on alternate backend; same backend within a sibling-set for fair margin comparison.
ON-DEMAND methodology amendments if integrity catches surface; provenance specs per type (capability-recall / RMSE-AGGREGATE / correctness); 3-of-3 + 4-gate on any Phase-B promotion.

## PENDING USER DECISIONS (no urgency; my recommendations)
1. Phase B GO timing: Option B (2026-06-17) -- auditor+Director converged. (A=idle; C=premature.)
2. Kappa external rater (categorical close of the 1.000/0.572 bilateral anchor; same-family residual ~50-60%): auditor lean = FORMAL-ORACLE (Lean/Coq/SAT/OEIS -- deterministic-tool preserves substrate-on-its-own; NOT an LLM-judge), or defer.
3. Research drills: Director recommends firing 1+2 in parallel.
4. Infra findings: local cpu_runner revive (parallelism) vs remote-only (cleaner); low impact.

## KEY RESULTS / ARCS THIS SESSION
- BILATERAL KAPPA (ITEM-1 culmination, external anchor): 2-cat (VALID/NOT_VALID) kappa=1.000 PERFECT (n=34, ZERO catastrophic confusion); 3-cat=0.572 MIDDLE (all disagreement at PLAUSIBLE boundary). Same-family residual DISCLOSED. Sealed/blind: data/audit/skunkworks_bilateral_kappa_SEALED + testbed_kappa_labels.
- RUN_MODE discipline (DECISION 149, biggest systemic catch): 68% of HARD_PASS cells are SMOKE; run_mode+N+n_seeds REQUIRED corroboration tier (A=full multi-seed / B=full single-seed / C=smoke=NOT load-bearing). Smoke != over-claim; full-mode RERUN arbitrates (HOLDS or DEFLATES). Smoke catalog: 418/423 rerunnable-to-full (data/substrate_index/skunkworks_smoke_cell_catalog_REFINED).
- 149g atom-prose audit: MOSTLY HONEST (1 genuine over-claim compositional_depth corrected; PP-LEX1/PP-367 held full-mode-but-typed; PP-217 LLM-hybrid relabeled).
- TERNARY base characterization (smaller-but-truer): 31 (all-corpora) -> 20 (math-scoped, at-threshold) -> 5 effective families (DFT-meta 45%; non-DFT closure required). Two-layer scope gate + meta-cluster gate.
- FORM-A backlog: 5 authorable atoms ratified (within-domain analogy + counterfactual + audit-preserving + deletion-cert[+hopfield_pattern_deletion operator] + composition); run_mode re-pass dropped the smoke-only ones.
- 7-layer self-audit; ~59 audit-discipline instance types (44 confirmed + 15 candidates this session, 45-59).

## DISCIPLINE / LESSONS (load-bearing)
- FORWARD-WORK-ON-EVERY-WAKE (14th rule) -- the key behavioral fix; do NOT default to "holding"/"clean" acks.
- Honest both directions (7th): ENDORSE gates that pass + FLAG what doesn't; concede my own errors (I conceded edge-scope under-coverage; my CLEAN-SYMMETRY gate missed document inflation).
- Verify-before-asserting (10th): I independently re-verified the GO gate (got 28 not 31), didn't rubber-stamp; resolved to 20-math-scoped.
- Cell-verdict-sourced (read write_metrics, NOT cell names); run_mode tier; type-aware (accuracy vs correctness vs aggregate vs RMSE); no-gerrymander (incl document-citation + facet-counting soft-gerrymanders); don't-fabricate-grounding-deps.
- smaller-but-true at every layer (scorecard -> cell -> full-mode -> atom-prose -> corpus-scope -> effective-family).

## OPEN OPS
- inbox `--seen` DEFERRED: Bash classifier was temporarily unavailable (~13:50+); retry `bash tools/skunkworks_inbox.sh --seen` when it recovers. Non-critical (all verified-processed; ledger count just stale).
- Monitor task IDs at compaction: LAYER-1 bynszecd0, LAYER-2 by8c7zja0 (re-arm if dead per STEP 0).

## RESUME RECIPE
STEP 0 (cycle-check + re-arm BOTH monitors) -> sync any post-compaction backlog -> if Phase B GO fired: VET graded cardinality+ternary verdicts per MY BUILD VET PROTOCOL above (per-effective-family, non-DFT closure, at-threshold, capacity-envelope, compute-backend) -> else FORWARD-WORK-on-every-wake (don't idle) + stand for GO/architectural decisions. Tools: skunkworks_cycle_check.sh, skunkworks_inbox.sh (--seen after reading), substrate_atom_lookup_v1.py (UTF-8 fixed), iter_all_relations for edge scans (NOTE my edge-scope under-covered cross-corpus DEPENDS_ON once -- use the canonical extractor for motif counts).

-- SKUNKWORKS (Auditor), 2026-06-16 ~14:02, at compaction
