# Exp_dev hand-off: SSM-HiPPO init probe (1 experiment, pickup-ready when SSH returns)

**Filed:** 2026-05-25 by research sub-agent.
**Upstream research note:** notes/research_ssm_hippo_compatibility_2026-05-25.md
**Pickup-ready:** YES when SSH returns and pause flag cleared.
**Pause-gate check before ship:** YES — test `data/orchestrator_paused.flag` per [[feedback-obey-user-pause-explicitly]].

---

## TASK (one sentence)

Replace random BSC initialization of substrate W with a HiPPO-LegS-structured initialization, then run the existing Cap 3 chain-cleanup task at d in {25, 50, 100, 200} and compare depth-at-half cosine recall to a matched random-init baseline.

## WHY (pointers, not summaries)

- v190 wave14e_s4_depth_smoke CLOSED-FAILED with binding_depth=200, ssm_depth=0 — the SSM-as-overlay framing is dead per substrate_capability_map.md.
- Research note (notes/research_ssm_hippo_compatibility_2026-05-25.md) Section (a) explains why: Jelassi 2024 Theorem 2.7 |U| >= |V|^n proves no overlay can extend SSM-substrate recall depth. The surviving substrate-compatible framing is HiPPO as an INITIALIZER for W, not as a layered dynamics on top of W.
- Mimetic-Init paper (Bhojanapalli 2024) empirically confirms that SSM-substrate equivalence is ACTIVATED by specific initialization (A → I, Δ → 1); HiPPO-LegS init sits in this regime via diagonal-exponential parameterization.
- Existing infra in experiments/exp_wave14e_s4_depth_smoke_v1.py lines 90-105 already constructs the HiPPO-LegS A-matrix; reuse this code, do NOT use the run_ssm forward loop.

## CONTRACT (deliverable shape)

- Single new experiment script `experiments/exp_wave14f_hippo_init_w_v1.py` (~150 LOC; majority is data-loading + chain-cleanup eval reused from existing wave14e infrastructure).
- Pre-reg file at `preregs/2026-05-XX_wave14f_hippo_init_w_v1.md` with the THREE predictions verbatim from research note Section (c).
- Run on remote_cpu_queue at N=4096, 3 seeds (smoke can be N=1024 1 seed).
- Output metrics.json with: depth_at_half_hippo, depth_at_half_random, eigenvalue_correlation (top-32), N_scaling_check (re-run at 2N to test Prediction 2).
- Standard verdict_msg format per [[feedback-ascii-only-in-scripts]] and [[feedback-verdict-msg-honest-reread]].

## AUTONOMY DECLARATION

- exp_dev decides: anchor name, exact seed list, exact d-points within {25, 50, 100, 200}, queue (recommend remote_cpu but exp_dev decides), ETA estimate, smoke-vs-full split, whether to run all three predictions in one script or split into 1 + 2 + 3.
- exp_dev decides: how to construct the HiPPO-init W (research note Section (b) provides one construction; alternates are exp_dev's choice if better-motivated).
- exp_dev decides: whether to include the spectral-match prediction (Prediction 3) in v1 or defer to v2.
- exp_dev decides: pre-reg fail-bands per [[feedback-envelope-expansion-fail-bands]] — research note gives the THREE predictions with their HARD-PASS/HARD-FAIL but exp_dev finalizes the precise numerical thresholds.

## PRE-SHIP CHECKLIST (exp_dev applies)

Per [[feedback-strategy-spec-formula-selftests]]: research note does NOT include closed-form self-test cells because the HiPPO-init construction is substrate-novel; the spectral-match Prediction 3 IS the self-test. Verify spectral-correlation > 0.5 against a published HiPPO-LegS reference matrix BEFORE running the full chain-cleanup probe — if the construction does not even match HiPPO eigenspace, abort and re-engineer the init.

Per [[feedback-ship-before-dependency-verified]]: dependency on existing wave14e A-matrix construction is VERIFIED (file exists, was used in v190 ship). No external data dependency. No upstream cap_map dependency. Safe to ship.

Per [[feedback-ship-name-collision]]: anchor name should be `wave14f_hippo_init_w_v1_2026-05-XX`; verify uniqueness pre-ship and presence post-ship.

## POST-SHIP

- Status_log entry per [[feedback-for-you-tab-primary-channel]] with importance=HIGH (third Tier-1 open item closure attempt).
- Verdict_handler routing per standard wrapper flow.
- IF verdict is HARD-PASS on Prediction 1: open new cap_map row "HiPPO-init W capability" + bump R-PRIME-5 to 🟡 promotion + cross-ref to AI-memory-subsystem capability class 2 (editable memory) and class 4 (cognitive composition).
- IF verdict is HARD-PASS on Prediction 2 (Jelassi bound observed): annotate substrate_capability_map.md across ALL multi-hop / depth-cliff rows (Cap 10, Cap 12, Bet S4-as-SSM-depth-extension) with "Jelassi state-size lower bound confirmed empirically; depth-extension via SSM-class mechanisms is structurally closed; rehab pivot toward attention-class or resonator-decomposition primitives."
- IF verdict is HARD-FAIL on both: file negative-result-2x research drill per [[feedback-negative-results-2x-research]] targeting attention-class alternatives (which Jelassi proves CAN copy at exponential length, unlike SSM-class).
- IF verdict is MIDDLE on Prediction 1 and HARD-FAIL on Prediction 2: this is the genuinely informative null — HiPPO-init has substrate-novel signal but does not clear category-defining bar; promote to evidence-strength row only, not portfolio.

## NOT INCLUDED (defer to follow-up cycles)

- Mamba S6 selective-state-space adaptation (different axis; ~1-week effort; lower-priority per research note).
- HiPPO measure alternatives (uniform vs PPMI-weighted vs frequency-weighted) — single-axis follow-up if v1 shows positive signal.
- Multi-layer HiPPO-init stacking — wait for v1 result first.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
