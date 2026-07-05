# exp_dev hand-off — research: integration full-stack hard-regime composition

**Filed-by:** research sub-agent, 2026-07-05, per USER's direct 5x-drill angle-3 question ("are the brain
components integrated / does the substrate compose end-to-end at HARD regime, not just easy-regime?").

**Trigger:** `notes/research_integration_full_stack_hard_regime_compose_2026-07-05.md` — the only end-to-end
loop test that has passed (`exp_integration_end_to_end_loop_bridge_v1`) was EASY-REGIME (single-hop,
object-slot-only, symbolic composition). The HARD-regime probe that exists
(`exp_integration_end_to_end_loop_bridge_HARD_v2`) tests only ONE seam (reason->generate, 2 slots) — never a
genuine 4+-subsystem chain (comprehend/role-type -> store+reason(multi-hop) -> control-gate(goal) ->
generate) under hard conditions. The research note re-analyzes HARD_v2's own landed numbers and finds an
accidental, precise, already-answered mechanism question (regenerative-relay cleanup vs analog pass-through
prevents seam-tax compounding at n=1 seam) but explicitly does NOT answer whether this survives a real
multi-subsystem chain, or whether a "confident wrong attractor, no backtrack" failure mode appears only
once subsystems are genuinely composed.

**Pause state:** check `data/orchestrator_paused.flag` at dispatch time. If present, this hand-off still
stands (research dispatches are allowed while paused) — exp_dev should treat the cell as queued-but-gated
until resume.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names the ANCHOR + POINTERS only.
exp_dev designs ALL of: exact trial/seed counts, whether to build the 4-stage or 4-stage-plus-Phase-2-
perceive version first, queue tier, smoke profile, FULL profile, and the exact HARD-PASS/HARD-FAIL/MIDDLE
bands (the research note pre-registers a recommended starting set, not a binding spec).

---

## Anchor candidates (rank-ordered)

1. **`exp_integration_full_stack_hard_regime_v1`** (TOP PRIORITY — the decisive integration test the USER
   asked for directly)
   - Anchor pointer: `notes/research_integration_full_stack_hard_regime_compose_2026-07-05.md`, section
     "Cheap decisive test."
   - Substrate-product reading: this is THE test of whether "8 capabilities individually proven" adds up to
     an actually-integrated substrate at hard regime, or whether composition-specific failure modes (seam
     tax, capacity-collision, confident-wrong-attractor cascade) appear only once 4+ real subsystems are
     chained together. A HARD_PASS here is the strongest possible evidence for the glass-box-substrate
     product thesis (composable, inspectable, auditable at every hand-off). A HARD_FAIL where
     `compounding_ratio[REGEN] < 0.50` despite each pairwise seam individually working would be the single
     most important negative result of the whole brain-component-driven-development thrust: it would mean
     pairwise regenerative relay is necessary-but-NOT-sufficient and motivate building a sustained
     cross-stage working-memory/thalamic buffer as the next brain-component (currently MISSING/DEFERRED per
     the brain-component inventory).
   - Stages (4 subsystems, ALL already independently proven, reused as-is — no new mechanism):
     (1) COMPREHEND = `exp_comprehension_envelope_superposition_vocab_v1`'s content-conditioned role-typing,
     operating point D=6/V=500 (MEASURED@same cell: order_content_exact=1.000, parse_holds=true here).
     (2) STORE+REASON = `exp_integration_end_to_end_loop_bridge_HARD_v2`'s hard regime (V=4096, hops=3,
     D_store=10, hub-cluster) + `hdlab.binding` HRR bind/unbind, but consuming COMPREHEND's typed output
     instead of ground-truth slot labels.
     (3) CONTROL-GATE = `exp_pfc_gate_cfrpe_trained_v2`'s RPE-trained Go/NoGo gate at its proven FAIR
     operating point (V1200/depth-4: GONOGO=0.653, ORACLE=0.962).
     (4) GENERATE = the HARD_v2 / `exp_generation_decoder_roundtrip_v1` bipolar-BSC decoder.
   - The primary experimental axis is ARMS, not stages: REGEN (snap inter-stage signal to nearest known
     codeword at every hand-off — the "thalamic relay") vs ANALOG (raw continuous pass-through at every
     hand-off, mirroring `cotrained_linear`'s already-observed collapse) vs STAGE-ORACLE (isolate each
     stage's own ceiling with ground-truth input, to compute `product_of_stages` — the naive-independence
     prediction the real chain is compared against).
   - Tier hint: CPU-only, no GPU needed — reuses 4 already-built primitives, comparable build/run cost to
     `exp_integration_end_to_end_loop_bridge_HARD_v2` (a cell that already shipped this session, few-hours
     dev + minutes-to-low-hours CPU wall time).
   - Why now: every component this cell needs already exists and is independently proven; the marginal cost
     is wiring, not new mechanism. The research note found the "does a relay prevent compounding" mechanism
     question already has a precise partial answer from landed data (re-analysis of HARD_v2's own two arms:
     0.939x0.861=0.808 ~= observed 0.806; 0.467x0.228=0.106 ~= observed 0.10 — near-perfect per-slot
     independence at n=1 seam) — so re-testing that mechanism in isolation is low-value. The genuinely open,
     literature-confirmed-as-unstudied question (2 of 3 independent lit-scans found NO published benchmark
     of chaining 3+ cleanup/attractor stages in series) is whether it holds at 4+ real subsystems. That is
     exactly what this cell tests, and it is cheap.
   - Recommended bands (exp_dev may adjust — see research note for full derivation):
     WIRING gate: full-oracle chain (every stage ground-truth) >= 0.85.
     BROKEN_CEIL: identity-severed discriminator <= ~0.05.
     HARD_PASS: `full_chain_end2end[REGEN] >= 0.35` AND `compounding_ratio[REGEN] >= 0.70` AND REGEN beats
     ANALOG by >= 0.20 absolute AND cross-seed cv < 0.15.
     HARD_FAIL: `full_chain_end2end[REGEN] < 0.25` despite `compounding_ratio[REGEN] < 0.50` (i.e. the
     relay fix itself still compounds worse than naive independence predicts).
     MIDDLE_BAND: `full_chain_end2end[REGEN]` in [0.25,0.35) OR `compounding_ratio` in [0.50,0.70) OR
     REGEN-ANALOG margin present but < 0.20.
   - Also instrument `wrong_attractor_rate[REGEN]` (glass-box-logged: fraction of trials where an
     intermediate cleanup step commits to a WRONG codeword with high internal margin/confidence) — this is
     a trust/auditability metric, not just a research curiosity; flag it as a standing quantity worth
     keeping even if the cell HARD_PASSes on the primary bands.
   - P_deflated = 0.45 for HARD_PASS (novel-synthesis-capped; naive per-stage product estimate is
     ~0.48-0.56 — comprehend ~0.86-1.0 x reason-per-slot ~0.86-0.94 x gate-GO ~0.65 x generate-given-clean
     ~1.0 — deflated per lit-scan calibration discipline because the product assumes independence, which is
     exactly the assumption under test).

2. **Phase-2 extension: swap ground-truth BGE rows for the live graded-GSBC encoder (v11/v12) as a genuine
   5th PERCEIVE stage** (follow-up, not blocking #1)
   - Anchor pointer: same research note, "Stages" section, Phase-2 note.
   - Substrate-product reading: completes the full perceive->comprehend->reason->control->generate loop with
     no ground-truth stand-ins anywhere. Should only be attempted after #1's 4-stage result is in hand, since
     perception's own retrieval-agreement gap (ret_agree10, already tracked separately) would otherwise
     confound the integration-specific question this cell is designed to isolate.
   - Tier hint: CPU-plausible if the v11/v12 checkpoint is already loadable from disk; no new training.

---

## Context pointers (pointers, not summaries)

- `notes/research_integration_full_stack_hard_regime_compose_2026-07-05.md` — this cycle's full spec,
  derivation of the pre-registered bands, and the 3 lit-scan syntheses (read this first, in full).
- `notes/research_integration_end_to_end_substrate_loop_2026-07-05.md` — prior same-day research note this
  drill extends (original 4-hand-off interface map + first thalamic-relay literature citations).
- `data/exp_integration_end_to_end_loop_bridge_v1/metrics.json` — EASY-regime FULL, HARD_PASS (both
  cotrained_linear and naive_symbolic hit 1.000 — the scope limitation this new cell is designed to move
  past).
- `data/exp_integration_end_to_end_loop_bridge_HARD_v2/metrics.json` — HARD-regime FULL, HARD_FAIL (VET-
  scoped as glass-box-positive: "composition is effectively symbolic"). Contains the per-slot accuracies
  this hand-off's naive-product re-analysis is built from (`regimes.hard.obj_acc`, `regimes.hard.subj_acc`).
- `data/exp_comprehension_envelope_superposition_vocab_v1/metrics.json` — comprehension's role-typing
  envelope grid (`grid.D6_V500`, `grid.D8_V500`); confirms the D6/V500 operating point recommended above sits
  inside the proven envelope (parse_holds=true), not past the D8/V250+ cliff.
- `data/exp_pfc_gate_cfrpe_trained_v2/metrics.json` — control-gate's proven FAIR operating point
  (V1200_d4/V2400_d4) and its depth-degradation curve (closure 0.661@d4 -> 0.075@d6) — the reason the new
  cell should NOT push reasoning hops past what the gate itself has been proven at, or the two subsystems'
  individual weaknesses could be conflated with a genuine composition failure.
- `experiments/exp_integration_end_to_end_loop_bridge_HARD_v2.py` — source scaffold to extend (reuse its
  hard-regime config, HRR primitives, decoder, and META_RULE discipline: arms_differ_verified, atomic
  metrics write, baseline_in_band, discriminator-survives-scale).
- `experiments/exp_comprehension_envelope_superposition_vocab_v1.py`,
  `experiments/exp_pfc_gate_cfrpe_trained_v2.py` — the two subsystems not yet wired into any integration
  cell; their exported scoring functions are what stage (1) and (3) above call.
- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-07-05.md` — INTEGRATION + CONTROL scoreboard rows
  (context for why these particular 4 subsystems and operating points were chosen).
- Pause state line: check `data/orchestrator_paused.flag` at dispatch time.

---

## Contract

- Pre-reg per [[feedback-envelope-expansion-fail-bands]]: HARD-PASS + HARD-FAIL bands BEFORE smoke (starting
  bands recommended above; exp_dev owns final numbers).
- Smoke gate exercises the SAME code path as FULL per [[feedback-smoke-code-path-must-exercise-same-branches]]
  — difficulty axes (V, hops, D_store, hub_cluster, comprehension D/V, gate depth) held at FULL in smoke per
  the HARD_v2 precedent; smoke reduces only trials/seeds.
- arms_differ_verified (META_RULE_AF): REGEN vs ANALOG intermediate representations must be hash-distinct;
  broken-identity discriminator recovery must differ from both.
- baseline_in_band (META_RULE_AG): verify the control-gate's ADD-baseline and comprehension's occupancy-
  baseline land in their already-established chance bands at the chosen operating points before trusting any
  chain-level discriminator (both have known floored-baseline failure modes documented in their own cells —
  do not re-trip the same test-design bug that produced control-gate v1's false HARD_FAIL).
- Self-test per [[feedback-formula-selftests]].
- Multi-seed FULL on smoke clearance (3 seeds minimum, matching the convention of all 4 source cells).
- Queue routing per Tier A/B/C in `agents/exp_dev.md` Section 0 (CPU-tier expected).
- Ship via `bash tools/orchestrator/queue_add.sh <queue> <name> <script> <prereg> <timeout>`.
- POST-SHIP REMOTE VERIFY via queue_add.sh exit code.
- status_log entry with `plain_language` + `importance`.

## Autonomy declaration

exp_dev decides ALL of: exact trial counts, whether to ship the 4-stage or defer to the 5-stage
(Phase-2-perceive) version, queue tier, ETA, smoke profile, FULL profile, and final HARD-PASS/HARD-FAIL/
MIDDLE bands (the research note's bands are a starting recommendation, not binding). If exp_dev's own
pre-flight re-read of the 4 source cells' metrics.json files finds the operating points recommended above
no longer sit inside each subsystem's proven envelope (e.g. if a subsequent cell has moved the comprehension
or control-gate envelope), that independent verification supersedes this hand-off's specific numbers — the
STRUCTURE (4 subsystems, REGEN/ANALOG/ORACLE arms, compounding_ratio + wrong_attractor_rate metrics) is the
load-bearing part of this hand-off, not the specific D/V/depth values.
