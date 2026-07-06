# Director BACKUP -- CURRENT STATE 2026-07-06 (clean; supersedes 2026-07-05)

**Read end-to-end first. Self-contained. Supersedes director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md (which holds the detailed blow-by-blow if you need it).**

## STEP 0 on pickup
`date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp` (every turn-end).
Then `python tools/inflight_monitor.py`.

## WHAT THIS PROJECT IS
hd-instrument: an observable VSA/HDC "glass-box" substrate. USER goal (locked): build a fully-functional glass-box-LLM-capable substrate -- every capability inspectable/editable, brain-grounded. Brain = north-star + existence-proof. NOT a vs-LLM comparison. The DEEP prize (USER north-star): the substrate REASONING ABOUT ITSELF (self-improvement / core-mathematics), pursued as NARROW glass-box monitor steps -- NOT full autonomous self-improvement.

## USER-LOCKED (obey; violating these is the main failure mode)
- **NO AskUserQuestion tool** (it blocks all progress until USER returns). Decide + state in prose + keep moving.
- **re-encode HELD** (do NOT trigger a BGE re-encode of the substrate).
- **SMOKE-only-local; canonical FULL via remote queue** (orchestrator owns push + queue_add). GPU FULL once/stage on the HOME GPU (overnight_queue), not cloud.
- **NEVER git add -A** (canonical Store is in the repo) -- explicit pathspec only.
- **Agent-spawn operating model**: main thread = judgment/routing/verification; sub-agents (hdi_exp_dev / hdi_skunkworks AUDIT-ONLY / hdi_orchestrator / hdi_testbed) do the work. Default run_in_background.
- **No-smoke**: rate GOOD/MEDIOCRE/BAD honestly; skunkworks (cert-owner) sets tiers off-disk. exact-by-construction -> MEASURED_MECHANISM, NOT CHAIN_GRADE -- BUT a parameter-free exact DERIVATION that clears the bar with firing controls -> CG.
- **Fix#28**: verify OFF-DISK before claiming, incl. AGENT-reported numbers. RECURRING DIRECTOR SLIP THIS SESSION (~5x): I propagated agents' PRE-FLIGHT / OTHER-CELL numbers as if in the TARGET cell's own persisted metrics -- ALWAYS verify what is PERSISTED in THE cell before routing/claiming.
- **Framing**: layer-demos (morphology / re-emission / arithmetic / self-query / self-margin) are NARROW glass-box steps -- NOT fluent-language, NOT self-improvement. Self-check = monitor-not-control (writes only its own metrics, never edits the ledger/code).
- **Research every negative** for mechanism + direction (paid off 2x this session: waypoint HARD_FAIL -> compounding-error diagnosis; drills that decided DON'T-build). Skunkworks non-positives; drill 2x/5x if load-bearing.
- Intuitive summaries at END (no jargon; importance/implications/progress/position).

## THE ONE BLOCKER (surfaced to USER; needs USER auth)
**Deploy the fixed `tools/queue_add.py` to the remote** (`marsh@home:C:/dev/hd-instrument/tools/queue_add.py`). The remote working tree is 4425-commit drifted + SCP-only (doesn't pull origin), so its `queue_add.py` runs the STALE referent-gate. This BLOCKS every cell that declares a `cert_ledger` KB_REFERENT -- i.e. the whole record-based self-reasoning ladder. The SCP-deploy is harness-DENIED in auto mode (Modify Shared Remote Resource); orchestrator did NOT bypass it (no --allow-missing-referent). **This one file-push is the SOLE lever that reopens the highest-value work.** PARKED FULLs waiting on it: cert_ledger_self_query (Tier-1), cert_ledger_numeric_entailment (Tier-2), cert_ledger_global_consistency (Tier-3), hard-comprehension. Their SMOKES already prove the capabilities; the FULLs are canonical confirmation.

## FINAL CAPABILITY MAP (session 2026-07-05/06, all honestly tiered off-disk by skunkworks)
- **LANGUAGE**: all 4 glass-box layers built + ASSEMBLED end-to-end (lexicon reused; MORPHOLOGY CG; SYNTAX proven; GRAMMAR MM function-words+recursion; 4-LAYER ASSEMBLY MM -- SVO round-trips, deliberately-malformed English = structure-not-language, "substrate knows nothing" held).
- **MATH**: arithmetic set COMPLETE (add/subtract/compare/multiply, all MM by-construction; multiply PRIME_NOT_REQUIRED honest finding; exact-equality + numeric-threshold-entailment primitives).
- **SELF-REASONING (the north-star, strongest thread) -- 4 forms, 2 at CHAIN_GRADE**:
  - Tier-2 numeric-entailment over its own ledger (MM, smoke, delta0 pending deploy).
  - Tier-3 structural-audit of its own ledger (cycles/forks/tier-monotonicity, MM, smoke, delta0, Goodhart-avoided).
  - decode-margin (own MATH): v1 empirical sigma^2 scaling (MM) -> v2 EXACT parameter-free order-statistic (CHAIN_GRADE -- predicts its own RNS decode-collapse boundary to ~1%).
  - FHRR bundle-capacity exact-margin (CHAIN_GRADE, 5-seed -- predicts its own bundle capacity K_crit exactly).
  => the substrate EXACTLY self-predicts its own reliability for its 2 ORTHOGONAL-family codebooks (monitor-not-control).
- **CONTROL**: depth SOLVED given a decomposition (hierarchical options, MM); autonomous self-decomposition works to entropy~8 (MM, depth-bounded).
- **INTEGRATION**: composes with REAL parts (full-fidelity 4-stage, CG); grounded re-emission (CG).
- **PERCEPTION/MEMORY**: encoder graded-code retrieval (MM, distill-from-BGE pragmatic); memory dense-Hopfield->1M + bundle law solid.

## CERT TALLY (this session, skunkworks-authoritative): 24 live atoms, ~19 commits. CG +6 / MM +11 (9 count toward CERT-N; 2 ledger-audit smokes delta0) / HARD_FAIL +2 / META +4 (neutral). CERT-N +15.

## BOUNDS honestly established (NOT failures -- thoroughly tested limits)
- Generalization = one-to-many entropy ceiling (all levers falsified; Hits@k neighborhood is the achievable form).
- Autonomous deep-decomposition = compounding-error bound (discovery+rescue both HARD_FAIL at the deepest corner; coarse-to-fine/cerebellum FALSIFIED for it; DAgger = out-of-scope next lever). KEY META: a small N-limited smoke directional-lift with NS sign_p can REVERSE at the canonical FULL (rescue smoke +0.112 -> FULL +0.004) -- canon decisive, don't call a small NS smoke lift a "lower bound".
- Closed-form SELF-MARGIN boundary: works for ORTHOGONAL-family codebooks (RNS/FHRR, roots-of-unity/near-independent -> CG) but the SEMANTIC/heterogeneous families RESIST (GSBC ~0.5-correlated; encoder Gram is a clean POWER LAW not bulk+spike so RMT is the wrong tool). Thoroughly tested across all 5 codebook families.
- THREADS CLOSED: thalamic-router SHELVED (drill-decided, RC2 CRT-fragility + RC3 prior 0.20); waypoint/cerebellum bounded.

## BANKED META-RULES (memory + this session)
- CROSS-CELL LAW (memory-banked, reference_crt_residue_helps_clean_encoding...): CRT/residue decomposition HELPS clean exact encoding, HURTS noisy associative readout.
- exact-by-construction -> MM; parameter-free exact DERIVATION with firing controls -> CG.
- symmetric-verify: correct UP (discovery HARD_FAIL->MM) AND deflate DOWN (by-construction), AND decline your OWN proposed promotions when not earned (bundle re-VET no-promote).
- a CG self-prediction of a quantity does NOT auto-promote earlier looser measurements of it.

## NON-PARKED HIGH-VALUE WORK = GENUINELY, THOROUGHLY EXHAUSTED
The self-margin arc is definitively closed (2 CGs + full 5-family boundary). Brain-components (CLS/neuromodulation/cortical-microcircuit) lack a real consumer (avoid the thalamic force-build mistake -- need a drill proving a consumer first). Generalization closed. So the remaining non-parked candidates are all MARGINAL (testbed quarantine the 86 id-less atoms.jsonl lines -- data-hygiene, no corruption) or SPECULATIVE (Glauber dynamics on codeword space; encoder RMT rejected). Do NOT manufacture busy-work against the deploy bottleneck. **LATE UPDATE (09:55Z): ONE more genuine non-parked direction found (pushed back on 'exhausted' + it paid off) -- the exact self-margin machinery EXTENDS from CODEBOOK-margins to a HEADLINE CAPABILITY: REASONING-DEPTH. Drill verified (vs landed data, zero new trials) that reasoning-depth collapse is the same order-statistic/collision family; a CAPTURE partial-credit order-statistic closes the reasoning-depth cell's 2.02x under-prediction to ~0.98x unbiased -> a 3rd self-margin CG-candidate + PROMOTES the reasoning-depth MIDDLE_BAND. Cell exp_reasoning_depth_exact_order_statistic_self_margin_v1 building (multi-seed >=5). So the self-margin machinery generalizes CODEBOOK-margins -> CAPABILITY-margins (the substrate predicting how deep it can REASON). This is a live sub-thread: after it lands+VETs, next-drill candidates are free-prob F4 (tier-1, 100% yield, under-drilled) or coding-theory BCH -- possibly MORE capability-level self-margins remain. Re-assess 'exhausted' after this lands.** **FRONTIER MAPPED (capability-self-margin meta-drill, notes/research_capability_self_margin_frontier_map_2026-07-06): 5/9 capability-collapses are collision/order-statistic SELF-PREDICTABLE (RNS CG + FHRR CG done; reasoning-depth FULL running->VET; generation mechanistically covered; COMPREHENSION order-recovery = top NEW pick, BUILDING a2b7b49), 1/9 HARDER (control branching-depth chain, needs a horizon-dependent SNR derivation first, P0.35), 3/9 honest ACCEPT-boundaries for distinct reasons (encoder power-law / generalization entropy-ceiling / autonomous-decomp Ross-Bagnell compounding). => the self-margin generalization is a SYSTEMATIC capability-frontier (the substrate predicting its own reliability across its CAPABILITIES, monitor-not-control) -- NOT a narrow codebook trick, and honestly BOUNDED (3 resist). Live sub-thread order: comprehension (building) -> if it lands, control_branching_depth (needs horizon-SNR drill first). NOT exhausted -- this is the deploy-INDEPENDENT north-star continuation.**

## NEXT-SESSION FIRST ACTIONS (priority order)
1. **MEMORY.md compaction** (deferred all session; 20.6KB -> under 17.1KB; STEP-0-safe at fresh context: keep the READ-FIRST banner + all FOUNDATIONAL ANCHORS + USER-LOCKED lines + the CROSS-CELL LAW; merge/drop stale; one line per entry).
2. **IF the deploy is done** -> re-dispatch the 4 parked FULLs (self-query/Tier-2/Tier-3/hard-comp) + build the next ledger-ladder rungs (roadmap 8b90c6667: coverage-gap is ready-to-build reusing refuse_gate_calibrate; then justification-retrieval which needs a gate_claims adoption-wave; then methodology-audit).
3. **ELSE (deploy still pending)** -> the highest-value non-parked options are all lower-confidence: (a) a drill proving a real CONSUMER for a missing brain-component before building it; (b) language-agreement/multi-clause (dispatchable, lower-value); (c) the Glauber speculative route. Prefer preparatory drills over marginal builds; surface the deploy bottleneck to USER again.
4. Testbed: quarantine/schema-normalize the 86 id-less lines in data/substrate_index/math/atoms.jsonl (id-indexers should guard for missing id meanwhile).

## INFRA/HAZARDS
- Cron 3f99d7f4 (:07/:27/:47) = the director cadence heartbeat. Landing-notifier armed.
- The cron's item-4 "encoder->0.85 / NCE-off lever" pointer is STALE (superseded weeks ago; encoder is a distill-from-BGE MM). Real primary = the north-star self-reasoning. (Testbed should update the cron text.)
- queue_add PROT-022 local pre-flight probe FIXED (19bbdf75d: was POSIX test-f on a Windows cmd.exe remote + short timeout; now PowerShell Test-Path + 3-retry) -- but the REMOTE copy is stale (see THE ONE BLOCKER).
- Detailed session history: notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md.
