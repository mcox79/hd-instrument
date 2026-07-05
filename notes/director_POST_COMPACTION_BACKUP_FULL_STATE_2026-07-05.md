# Director BACKUP -- CURRENT STATE 2026-07-05 (clean; supersedes 2026-07-04)

**Read end-to-end first. Self-contained. Supersedes director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-04.md.**

## STEP 0 on pickup
`date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp` (every turn-end).
Then `python tools/inflight_monitor.py`. Companion doc = `notes/integrated_short_term_spec_sheet_5x_drills_what_we_want_how_brain_does_it_2026-07-05.md` (per-goal specs + VET-results + LATEST-LANDINGS).

## WHAT THIS SESSION DID (2026-07-05)
USER goal (locked): build a **fully-functional glass-box-LLM-capable substrate** (perception, memory, reasoning, generation, generalization, comprehension, control -- all inspectable, brain-grounded). NOT vs-LLM.
Arc: 5x-drilled every short-term goal -> built + independently VET'd a first cell of each capability -> iterated on the hard ones -> tested end-to-end composition -> opened comprehension + control -> USER added the BRAIN-COMPONENT thrust.

## HONEST AUDIT-SCOPED SCOREBOARD (no smoke -- the audits trimmed several of my over-claims; lead with these)
- **PERCEPTION**: done-mediocre (GSBC_EXPAND2X). Teacher-dependence NOT a proven wall.
- **MEMORY**: SOLID. dense-Hopfield recall->1M (CHAIN_GRADE); bundle ~200 items/N8192 (MM, linear-memory law ~40 floats/item); hubs deg5-7 via protected/permutation-index binding (MM); deg8+ via redundancy banks 0.40->0.99 (HARD_PASS smoke, FULL deferred -- 1.3GB BGE cache local-only).
- **REASONING**: **CHAIN_GRADE** (VET-confirmed). Regenerative digital-repeater cleanup ~0.70 depth-5, ~9-10 usable hops, faith 1.0. NOTE: the earlier "modest 0.26" was a chain-key-COLLISION artifact (all 3 witnesses mis-diagnosed; collision-corrected v2 = strong). Next lever: iterative/resonator per-hop cleanup (deeper).
- **GENERATION**: **CHAIN_GRADE** (VET-confirmed). Block-local native-GSBC decoder round-trips real fillers exact-ordered ~1.0 to D=26/V<=1024 (canonical cliff 0.856 @V8192/D26). Grid-cell modular coding. Next lever: RNS/CRT sub-blocks (higher vocab).
- **INTEGRATION (goal-level: does it COMPOSE)**: **HARD_PASS at FULL (LANDED 2026-07-05, verified off-disk)**. Full loop perceive->store->reason->bridge->generate = 1.000 exact-ordered, glass-box; controls fire (broken-reasoning=0.000, naive-randproj-bridge=0.000, discriminator gap 1.000). Co-trained linear bridge closes the cross-algebra+dim reason->generate seam (bridge MANDATORY). CAVEAT: easy regime (D=3 single-hop); hard-regime stress (high-deg hubs, multi-hop) staged. VET IN FLIGHT (af274c4) -- saturation scrutiny on the 1.000 + the near-chance correlation_cone 0.51-0.52.
- **COMPREHENSION**: real, HOLDS at HARD regime (smoke). frame-classify-then-decode; content-conditioned role-typing (selectional-restriction) recovers ORDER where occupancy is provably blind (1.0 vs 0.20), survives superposition (0.80), holds at scale (0.70). NOTE: the FIRST cell's 1.0 was trivial-by-construction (set-identity); the HARD cell redeemed it. FULL shipping.
- **FRONTIER / GENERALIZATION (the prize, still open)**: MEASURED_MECHANISM, NARROW. Content-conditioned bilinear (RESCAL-class) moved inductive relational transfer OFF ZERO where averaging (TransE-class) = shuffle-invariant 0. BUT crosses the 0.2075 bar ONLY at V=100 (1/56 configs); systematic scaling plateaus ~0.11; collapses at V>=300. Diagnosis = one-to-many ENTROPY CEILING, not under-param. Fix candidates: (a) richer JOINTLY-TRAINED content (BLP/SimKGC), (b) CLS slow-consolidation (brain-component route).
- **CONTROL**: **HARD_FAIL at FULL (LANDED 2026-07-05, verified off-disk)**. goal-conditioned additive/WM gate: combined_lift=0.044, add_lift=0.068, ORACLE=0.994, **headroom=0.642**, cv=0.061, 5 seeds -> additivity FAILS, static gate near its ceiling. BUT op-selection router proven (cortex_attention_binding_router_v2 HARD_PASS). FIX IN FLIGHT (top brain-component build, a16c02f): exp_pfc_gate_cfrpe_trained_v1 -- replace static additive bias with a Go/NoGo gate TRAINED by the cfrpe RPE signal (the missing training half of the BG gate; PBWM/Frank). HARD-PASS if it closes >=25% of the 0.642 headroom.

**Key meta-finding:** >=4 brain components are EMPIRICALLY REQUIRED for higher function (ablation-style): hippo-index for hubs, regen-cleanup for reasoning-depth, grid-modular for generation, TEM content-conditioning for generalization. Not decoration -- measured requirements.

## IN FLIGHT (as of ~16:30Z 2026-07-05; check inflight_monitor + task notifications)
- **a16c02f (hdi_exp_dev)**: authoring + SMOKE `exp_pfc_gate_cfrpe_trained_v1` -- the TOP brain-component build (Go/NoGo gate trained by cfrpe RPE; targets CONTROL HARD_FAIL, 0.642 headroom). Spec = brain-component drill Section 4. SMOKE-local then stage FULL for orchestrator.
- **a79824 (research)**: generalization reframe drill -- mechanism of the one-to-many ceiling (fan-out vs conditional-entropy) + design the RANK/SET (Hits@k/MRR) reframe cell spec. Genuinely-new leverage (NOT re-litigating CLS-dual-store, flagged weak/mixed).
- **af274c4 (hdi_skunkworks)**: landed-VET of integration FULL (HARD_PASS, saturation scrutiny) + control FULL (HARD_FAIL, confirm headroom).
- PRIOR in-flight all LANDED (prize=HARD_FAIL confirmed; integration=HARD_PASS; control=HARD_FAIL; hard-comprehension FULL still blocked on PROT-022).

## NEXT-SESSION FIRST ACTIONS
1. **PRIZE RESULT IN (2026-07-05 ~15:40Z): richer-content = HARD_FAIL_ONE_TO_MANY_CEILING_GENUINE** (data/exp_schema_relation_richer_content_vscan_v1/metrics.json). Jointly-trained content does NOT beat frozen at V>=300 (joint-minus-frozen=0.002<0.02); discriminators fired -> the one-to-many entropy ceiling is GENUINE for single-answer relational transfer on thin generic-sentence content. So broad generalization is NOT won via richer content. => NEXT ROUTES (this is THE open problem): (a) CLS slow-consolidation (brain-component route -- DIFFERENT mechanism: offline replay abstracts schemas, not content-richness); (b) REFRAME the task -- one-to-many means single-answer transfer is ill-posed; try RANK/SET prediction (Hits@k over the plausible-object set) instead of exact-single-object, which may be the honest correct metric. Route this decisive negative to a 5x-drill (important-negative). Needs Skunkworks landed-VET of the HARD_FAIL + the ceiling claim.
   **STATUS 2026-07-05 ~16:30Z: BOTH routes now IN FLIGHT.** Reframe-to-rank/set drill dispatched (research a79824, designing the Hits@k/MRR cell + fan-out-vs-entropy mechanism). On landing: ship the reframe cell if bands are falsifiable. NOTE the brain-component drill flagged CLS-dual-store as weak/mixed (3 cells run) -> reframe is the new leverage, not another CLS cell.
2. **TOP brain-component build FIRED (a16c02f, hdi_exp_dev): `exp_pfc_gate_cfrpe_trained_v1`** -- Go/NoGo gate trained by cfrpe RPE (drill ranked #1+#2; NOT CLS). Targets CONTROL HARD_FAIL (0.642 headroom). On SMOKE-clear: orchestrator fires the canonical FULL. This is the "missing training half of the BG gate" thesis (PBWM/Frank): static additive bias was near ceiling; RPE-trained Go/NoGo should close >=25% of headroom (HARD-PASS) or prove the weakness is architectural (HARD-FAIL <=0.05 lift).
3. VET IN FLIGHT (hdi_skunkworks af274c4): integration HARD_PASS (saturation scrutiny -- the 1.0 + near-chance correlation_cone 0.51) + control HARD_FAIL confirm. Hard-comprehension FULL still BLOCKED on PROT-022 (one-line testbed fix, see HAZARDS).
4. Continue: fire staged brain-component builds; iterate the open capabilities (generalization broad, control strong, integration hard-regime).

## PRINCIPLES BANKED THIS SESSION (memory files + MEMORY.md)
- **no-smoke** (rate good/mediocre/bad, deflate OUR claims) -- caught ~4 over-claims via VETs this session (comprehension-trivial, prize-narrow, reasoning-mis-diagnosed, generation-rounded).
- **prior-work-informs-NOT-constrains** (scour to not rediscover, but test brain-aligned OR high-prob-superior new mechanisms).
- **research-every-finding (middle/negative) for MECHANISM + ENVELOPE-PUSH** (a tier is not the finding; a negative is a mechanism-clue + a direction).
- **BRAIN-COMPONENT-DRIVEN development** (USER standing thrust: inventory->required->multiples->build-missing). [[project_brain_component_driven_development_thrust...]].
- honest capability framings [[reference_honest_capability_framings_generation_frame_known_memory_linear_memory_law_2026-07-05]].

## DISCIPLINE / HAZARDS (obey)
- Verify off-disk before claiming (Fix#28); the audits scoped down several headlines -- LEAD with VET-surviving scoped numbers.
- Canonical run = remote queue; SMOKE-only-local; GPU FULL via orchestrator; SCP untracked caches explicitly.
- **GIT-INDEX RACE** flagged: running many concurrent agents caused a pathspec-less commit to sweep a concurrent agent's staged Store atoms (no data loss). Mitigation: `git commit <explicit-pathspec>`, avoid `git add -A`, tighten concurrency. I over-extended (5-6 concurrent) -- be more measured.
- Re-encode of substrate HELD (not needed; not fired).
- **INFRA BUG (blocks referent-declaring remote cells; one-line fix):** PROT-022 gate in `tools/queue_add.py` (~line 425-440, `check_declared_referents`) does an ssh-to-SELF loopback when `HDLAB_QUEUE_ADD_ON_REMOTE=1` (remote can't ssh itself -> false "referent MISSING"). FIX: when on-remote, check LOCAL filesystem `(REPO/ref).exists()` not ssh. Blocked the HARD-COMPREHENSION FULL (frame_order_recovery_hard_comprehension_v1) -- smoke is banked + commit c44332fee pushed; re-dispatch after the testbed fix (never queued, no --allow-duplicate needed). Route to hdi_testbed.
- Deferred tidy: director_plan.json refresh (stale pre-reframe C0-C6); capability_scorecard revision; a97751df light-VET; auto-refill daemon needs USER elevated cmd; n11 teacher-free revival; memory deg8+ canonical FULL (data-locality); push accumulated commits (durability sweep ad38e6 ran).
