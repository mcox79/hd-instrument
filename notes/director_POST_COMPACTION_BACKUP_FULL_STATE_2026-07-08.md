# Director BACKUP -- CURRENT STATE 2026-07-08 (clean consolidation; supersedes all earlier dated blocks)

**Read end-to-end; self-contained + current (anachronistic layers removed 2026-07-08 ~22:xxZ). Deep pre-07-08 history: notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-07.md.**

## STEP 0 on pickup (every session)
1. Heartbeat (every turn-end): `date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp`
2. `python tools/inflight_monitor.py` -- monitor CACHE lags ~20min; "empty queue" usually = FINISHED not stalled -> VERIFY OFF-DISK. Sub-agents + VETs are NOT dashboard-visible ("empty dashboard" != idle).
3. Agent stalls are systemic (die on API/socket blips AFTER their work lands): a 0-byte/long-silent agent output = verify off-disk what it produced (cell/notes/metrics/atom usually landed), re-dispatch FRESH only for the missing piece.
4. Bash recursive scans hang on the huge store (178k atoms / 15k notes / 6k exp dirs) -- TARGETED grep only, never a broad crawl.

## WHAT THIS PROJECT IS
hd-instrument: observable VSA/HDC GLASS-BOX substrate. USER goal (locked): a fully-functional glass-box-LLM-capable substrate, every capability inspectable/editable, brain-grounded. **Brain = north-star + existence-proof, NOT a vs-LLM scoreboard** (LLM comparison is a DIAGNOSTIC to find load-bearing weak points). **Deep prize: substrate REASONING OVER ingested knowledge -- glass-box, self-auditing, monitor-not-control.** Stages: 1 foundational (~88%, operational), 2 meta (~85%), 3 capability (~60%, current front), 4 LM-equiv (deferred; gap = generation).
**USER-LOCKED FOUNDATIONAL PRINCIPLE (2026-07-08): the substrate is SELF-CONTAINED and knows nothing but what it is fed; the encoder must CO-EVOLVE with the substrate (learn+improve as it grows) -> NO external model may be bolted into the core.** This is why the encoder must be NATIVE (see barrier #1).

## CURRENT FRONT: the 4 load-bearing barriers (the LLM-diagnostic's weak points), being closed
- **#1 READER (encoder) = THE #1 GAP. Path = NATIVE (USER-locked).** Every downstream stage inherits the reader's quality. The current operational KB reader is lexical `char_trigram_v1` (weak: dogfood MEDIOCRE/BAD -- misses recent+semantic). A far better reader exists (graded-code m=5 closes the retrieval-agreement metric `ret_agree10` 0.19->0.45 cross-seed, joint gate holds) BUT it is BGE-DISTILLED (needs an external BGE text->dense front-end) -> flipping to it violates the self-contained/co-evolving principle. So it is REGISTERED-BUT-OFF (hdlab/gsbc_graded_encoder.py) and we will NOT flip to it. THE NATIVE-PATH QUESTION: does the graded-code resolution trick close ret_agree10 on the NATIVE teacher-free encoder (CG, 06e5a493d), or is native MEANING the limiter (-> strengthen teacher-free semantics first)? THIS is the live headline test.
- **#2 CHAIN DRIFT (compounding error over long reasoning chains).** Fix built = replay-generate-then-select (generate whole candidate paths fwd+reverse, commit the one where directions AGREE = an INFORMATIONALLY-INDEPENDENT check; both prior fixes failed by re-checking a signal against itself). Smoke is N-CONFOUNDED (reverse signal is noise below N=8192) so only the FULL tests it. COIN-FLIP P~0.25-0.30; BOTH outcomes valuable (pass = long chains work; fail = drift bound doubly-confirmed even vs independent correction -> keep chains SHORT, lean on per-hop re-clean / the glass-box loop).
- **#3 CROWDED STORE = SOLVED (both axes).** Hippocampal-indexing + community-routing = wake only the relevant neighborhood. v1 = MEASURED_MECHANISM (decouples crosstalk from TOTAL store size; naive collapses 0.79->0.0 at 58k, routed stays flat 1.0; atom DECOUPLES_CROSSTALK on origin). v2 NESTED community-of-communities closes the per-community-load axis (single-tier collapses 0.99->0.02 under per-community overload, nested stays flat 1.0 both tiers) -- SMOKE HARD_PASS, FULL confirming.
- **GENERATION = the remaining genuinely-OPEN weakness (Stage-4).** Not built. Known: fails by NOISE-COMPOUNDING; fix = SELECTION not denoising (context-gate flattened it ~99.5% but only as RECENCY on a 1st-order corpus; CONTENT-gating on higher-order corpus = the hard open piece). Deep predict-residual FAILED (capped at the ~0.52 concept-recall ceiling) => generation is ENTANGLED with / BOTTLENECKED by the reader (#1) -> its BUILD is sequenced AFTER the native reader. Heavy brain-grounding drill in flight.

## WHAT IS OPERATIONAL NOW (integration phase, all on origin)
USER challenged "certs pushed but is anything INTEGRATED / are we using optimal settings?" -> staged audit (notes/audit_staged_integration_and_optimal_settings_2026-07-08.md): Stage-1 foundation REAL+green, but the gap was INTEGRATION DEBT (4741 exp cells vs ~73 hdlab modules; certs NOT auto-promoted). FIXED bottom-up -- proven mechanisms moved from experiment-cells into the operational hdlab/ library, each ADDITIVE + verification-witnessed + no-regression (verification suite 132 -> 204 tests):
- **Stage-1:** peel/SIC bundled-recovery readout (cleanup_family.BUNDLE_READOUTS); BSC first-class primitive (binding.py).
- **Stage-2:** lock-in amp (lock_in_amp.py); compose-freq routing (compose_freq_routing.py -- CG scope-CAVEAT'd: routing only wins in the high-in-degree regime, delta-rule carries it elsewhere).
- **Stage-3:** retained-trace energy-mode (context_retention.py); CLS discrete-budget consolidation (hippocampal_encoder.py); **the glass-box reasoning loop itself (glass_box_loop.py) + Merkle audit primitives (hdlab had NO hash-chain audit before) + arbitration-margin gate**; BG Go/NoGo action-selection (action_selection.py, MM tier).
- **Self-manager:** adaptive-halting dial (self_manager.py) -- LOCAL, and its independent VET is IN FLIGHT (was wired before VET; see rigor rule).

## DURABLE CERT TALLY (on origin)
- **DEEP PRIZE = CHAIN_GRADE at 80x:** glass-box self-auditing multi-hop reasoning over REAL ConceptNet knowledge, non-ceiling at 48,000 entities (base + SCALE atoms). Scope: real TOPOLOGY with random codes; certifies relational-retrieval + self-audit routing, not semantic-embedding reasoning, not open-domain.
- **CG:** encoder semantic-barrier (semantic-fidelity-bound, not capacity); decouple-store-from-retrieval redirect; peel/SIC readout transfers to real codes (argmax 0.20@J8 -> peel 0.94, the two-head "capacity wall" was a READOUT limit); CLS integrate-without-forgetting; retained-trace non-destructive energy-scaled selective-depth; teacher-free relational encoder.
- **MM:** CA3-completion (n=8 firmed); community-bounded retrieval (total-V scale-invariance); BG Go/NoGo action-selection.
- **Honest negatives (kept as scope-bounds):** peel/SIC does NOT help single-cue NN retrieval (bundle-recovery only); SimGRACE degree-agnostic dead; decouple/peel-SIC does NOT fix ret_agree10 (that gap is quantization RESOLUTION, fixed by graded codes).

## PROCESS RULES (locked -- obey)
- **PROVE -> INDEPENDENT VET -> INTEGRATE.** Never wire a mechanism into hdlab on its own FULL self-verdict + integration witness alone; it must pass the adversarial skunkworks landed-VET FIRST. (Slipped once on the halting dial; VET closing it now.) [[feedback_integrate_only_independently_vetted_mechanisms_vet_before_wiring_USER_2026-07-08]]
- **REASONING PROPORTIONAL to decision difficulty** -- fast/shallow on routine/hold/self-check/obvious turns, deep only on genuine forks/diagnoses/irreversible ops. The cron = spur to MOVEMENT-or-one-line-stop, never a deliberation loop. [[feedback_reasoning_proportional_no_overthink_idle_hold_turns_USER_2026-07-08]]
- **DOGFOOD the substrate API** (director_kb_query) during scours + rate GOOD/MEDIOCRE/BAD, do-both vs grep. [[feedback_dogfood_substrate_api_during_normal_queries_evaluate_performance_USER_2026-07-08]] (Tally this session: mostly MEDIOCRE/BAD -- char_trigram default -- a standing case for the native encoder.)
- **NO-SMOKE honesty:** off-disk tiers, skunkworks-owned; rate GOOD/MEDIOCRE/BAD, default deflated; brain=existence-proof, NEVER frame a baseline as a ceiling.
- **DISCRIMINATOR MUST FIRE at scale** (assert_discriminator_fires): the must-fail control must FAIL at smoke V else the smoke is SATURATION-VACUOUS and the FULL HARD_FAILs. Discriminators must be telemetry-SENSITIVE (perturb-moves-it), not analytically pinned.
- **REMOTE DISPATCH = ORCHESTRATOR** (exp_dev builds+smokes LOCAL, hands the queue_add; orchestrator ships+verifies). No pause flag exists; do NOT write `pause_state: ACTIVE`. queue_add.sh = POSITIONAL args; Pattern-5b now auto-SCPs shared hdlab/ modules to the runner.
- **PUSH PATH:** origin/main push goes through a FRESH orchestrator dispatch (the working authorized path); a SendMessage-resume push gets harness-gated. Push-policy for this session = resume origin syncing (USER full-auto). NEVER git add -A (explicit pathspec; substrate_index partitions are sync-managed, persistence = A5 on-disk write + push).
- **BOTTOM-UP / foundation-first integration** (brain-evolution order), not highest-value-first. BRAIN-GROUND every gap first. SCOUR/grep existing before building. Drill genuine negatives (after skunkworks confirms genuine).
- **Model+effort:** research/drills=Sonnet; exp_dev/skunkworks/orchestrator/testbed=Opus; director=Opus. Effort HIGH / XHIGH headline VETs. NO AskUserQuestion. Keep USER strategic (handle plumbing silently). Never stand -- keep lanes full; cron = move-or-one-line-stop.
- **CRON:** CronCreate job 5aab7891 (:07/:27/:47) -- SESSION-ONLY (survives compaction, NOT session-exit -> re-create if the session restarted). OS watchdog = durable backstop.

## INFRA / HAZARDS
- **SYNC-LAG (SH-9):** remote metrics lag ~20min; force-pull via tools/orchestrator/scp_recover_landing.py; verify off the authoritative runner disk (Fix#28), not queue.json status.
- **Store:** atoms.jsonl / cert_ledger.jsonl are A5-gated; substrate_index partitions gitignored (sync-managed).
- **ERROR-HARDENING live** (from _seed_checkpoint / tools/exp_guard.py): assert_discriminator_fires, timeout floor (encoder V40000 5-seed >=10800s), atomic write_metrics, tri-state scp_recover, heavy-smoke-routes-remote.

## IN FLIGHT NOW (~22:xxZ, full-auto) + NEXT ACTIONS
IN FLIGHT (5): native-reader test (abcd02db) | chain-drift GPU FULL (~70min) | nested-store v2 FULL ship (a6ae6f4e) | halting-dial rigor VET (ac6b7478) | generation heavy-drill (ab807b50).
PENDING SYNC (local): halting dial 982c59a0a (gated on its VET) + self-manager module.
QUEUED (as lanes free, prove->VET->integrate): cross-modal binding integration; other self-manager dials; generation build (post-native-reader).
NEXT ACTIONS on landings: (1) #1 native-reader result -> build-native-encoder-flip vs strengthen-native-semantics-first; (2) #2 GPU verdict -> long-chains vs keep-chains-short; (3) #3 v2 VET+atomize -> #3 fully done; (4) halting-dial VET -> cert-or-pull; (5) generation build after #1 lands. Keep prove->VET->integrate throughout.
