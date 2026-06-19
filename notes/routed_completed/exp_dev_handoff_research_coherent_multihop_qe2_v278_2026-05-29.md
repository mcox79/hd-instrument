# exp_dev hand-off — research: coherent multi-hop (QE-2) v278

**Filed:** 2026-05-29 by research sub-agent. Trigger: research delivery `notes/research_coherent_multihop_qe2_v278_2026-05-29.md`. Strategic input from user (quantum-inspired two-layer / D-Wave-analog framing) maps to QE-2 (coherent multi-hop) at user-stated P=40-55%, deflated to P_smoke=0.40 per [[feedback-lit-scan-calibration-penalty]].

**Pause state:** check `data/orchestrator_paused.flag` before shipping. If paused, file as design-only.

**Per [[feedback-no-experiment-design-in-prompts]]**: this hand-off names ANCHORS + WHY + CONTRACT + AUTONOMY only. exp_dev designs ALL of: exact N, M, K, seed count, threshold band numerical bounds, queue choice (Tier A/B/C), final anchor name (PROT-018 _n<N> suffix), per-experiment timeout, smoke profile, FULL profile, and pre-reg envelope-fail-bands.

---

## Strategic context (one paragraph)

Substrate's multi-hop cliff at d=25-50 has been the most persistent capability limitation; 5 prior chained-cleanup mechanism diagnoses returned at 80% refutation rate. User's quantum-inspired strategic input identifies the failure mechanism PHYSICALLY: per-hop argmax destroys the information the next hop needs. Coherent multi-hop sidesteps this by propagating the full retrieval distribution (or top-K soft mixture) through multi-step W operations, with argmax only at the final readout. This is the architectural inversion of chained cleanup, not a tweak of it. Research note section (b)-(c)-(d) derives why this should escape per-hop information loss, and section (e) addresses argmax-bottleneck reassertion at the final readout. v276 4-witness argmax-bottleneck pattern (Agent 5 + Agent 3) provides the theoretical motivation; v272 KF-4/KF-5 joint rescue is the single-step analog of this multi-step rescue.

---

## Anchor candidates (rank-ordered)

### Anchor 1 — Option 1 top-K soft mixture coherent multi-hop smoke (RECOMMENDED FIRST SHIP)

- **Anchor pointer**: research note section (g) substrate-specific pseudocode + section (i) falsifiable predictions table
- **Substrate-product reading**: highest-EV anchor in current pipeline; closes substrate's biggest competitive weakness (multi-hop cliff) if HARD-PASS. Per project_substrate_killer_features_2026-05-26 this enables the compositionality-audit product feature.
- **Tier hint**: Tier A LAPTOP CPU smoke (~1 hr); cheap pre-condition for the GPU FULL.
- **Why now**: research note section (j) recommends immediate smoke; user-stated 40-55% P_success; substrate-product implications binary on this result.
- **Falsification envelope** (research note section i): pre-register hard-pass at d=50 acc>=0.65, hard-fail at d=50 acc<=0.35. exp_dev tunes exact numerical thresholds per envelope-fail-bands.
- **Substrate primitive**: uses existing `W @ x` (Hebbian) + `codebook @ s` + standard pytorch topk/softmax. NO new substrate code needed beyond a ~30-line wrapper function.
- **Per-experiment timeout**: per [[feedback-per-experiment-timeout-required]] exp_dev computes from smoke wall_s and scaling factor.

### Anchor 2 — Option 1 FULL coherent multi-hop production confirmation (GATED on Anchor 1 HARD-PASS)

- **Anchor pointer**: research note section (i) FULL test table; section (g) implementation
- **Substrate-product reading**: PROT-018 production-N N=8192 5-seed multi-cell sweep; HARD-PASS triggers cap_map row update from 🔬 to 🟡/🟢.
- **Tier hint**: Tier C GPU FULL (~2 GPU days estimated; exp_dev confirms ETA from smoke wall_s).
- **Why now**: gated on smoke pass; not pre-shipped. Per [[feedback-no-padding-experiments]] don't queue this until smoke result.
- **Falsification envelope**: research note section (i) FULL table; exp_dev pre-registers (K_mix, beta) grid endpoints and threshold formula per envelope-fail-bands.

### Anchor 3 — Option 3 spectral propagation DIAGNOSTIC (GATED on Anchor 1 HARD-FAIL or MIDDLE-BAND)

- **Anchor pointer**: research note section (c) Option 3 implementation + section (d) eigenvalue-degeneracy connection to Entry 152
- **Substrate-product reading**: diagnostic to identify whether eigenvalue near-degeneracy mechanism (Entry 152 Agent G) is the dominant failure mode. If alpha vector measurably drifts within degenerate signal subspace, the mechanism is identified and the multi-hop row can close red with confidence per [[feedback-rehabilitation-after-rejection]].
- **Tier hint**: Tier A LAPTOP CPU diagnostic (~30 min); diagnostic-only, no production claim.
- **Why now**: gated on Anchor 1 outcome. Only ship if Anchor 1 fails or borders.
- **Falsification envelope**: not a hard-pass/hard-fail anchor; observational. Pre-register: top-r=64 alpha vector drift magnitude post-d=50 in measurement-bounds [0.0, 1.0]; report empirically.

---

## Context pointers (file paths, NOT summaries)

- This research note: `notes/research_coherent_multihop_qe2_v278_2026-05-29.md`
- v276 surge synthesis (argmax-bottleneck 4-witness pattern + Sagawa-Ueda + Bet B convergence): `notes/research_surge_synthesis_v276_2026-05-29.md`
- Entry 155 cluster-trapping framework: `notes/research_multihop_mechanism_4th_attempt_ADDENDUM_2026-05-22.md`
- Entry 152 eigenvalue near-degeneracy diagnosis (Agent G + H): `notes/research_multihop_chain_rehabilitation_N65536_2026-05-22.md`
- Entry 156 retraction framework (8-constraint 11/11 fit): `notes/research_multihop_mechanism_5th_attempt_2026-05-22.md`
- Substrate killer-features priority: `notes/project_substrate_killer_features_2026-05-26.md`
- Existing repo primitives: `hdlab/hebbian.py` (W), `hdlab/codebook.py`, existing chained-cleanup baseline scripts (exp_dev locates via decision-log grep per [[feedback-poll-closed-session-logs]]).

---

## Contract (what's locked vs free)

**Locked**:
- Anchor 1 is a TOP-K SOFT-MIXTURE coherent multi-hop variant (Option 1 in research note). Not Option 2 or Option 3 — those are gated diagnostics.
- Pre-arg argmax happens ONCE at final depth d only. NO per-hop argmax.
- Smoke at N=4096 K_codewords=100; FULL at N=8192 5-seed PROT-018 production.
- Falsification thresholds from research note section (i) HARD-PASS / HARD-FAIL / MIDDLE-BAND tables are pre-registered targets; exp_dev fine-tunes exact bound values per envelope-fail-bands but cannot soften the ranges (e.g., HARD-PASS at d=50 cannot be set below 0.55).
- ASCII-only print/verdict_msg per [[feedback-ascii-only-in-scripts]].
- PROT-018 anchor-name `_n<N>` suffix required.

**Free (exp_dev autonomy)**:
- Exact (K_mix, beta) grid for smoke and FULL.
- Exact depth sweep points (e.g., {1, 5, 10, 25, 50, 100} or different choice).
- Seed count (smoke = 3 per research note suggestion, FULL = 5 per PROT-018).
- Smoke wall-time and FULL wall-time computation, per-experiment timeout formula.
- Queue choice (likely Tier A laptop CPU for smoke; Tier C GPU for FULL).
- Smoke + verify_remote pattern per exp_dev contract.
- Decision on whether Anchor 1 smoke needs replication seed (3 vs 5 seeds at smoke level).
- Naming: exp_dev's final PROT-018-compliant anchor name (suggested patterns in research note section j).

---

## Autonomy declaration

Per [[feedback-no-experiment-design-in-prompts]] checklist item 7:

This hand-off contains NO:
- specific anchor names (only suggested name patterns)
- numerical sweep grids beyond depth endpoint suggestions ({1..100} is endpoint, not grid)
- threshold formulas (HARD-PASS values are research-note-derived, exp_dev confirms)
- HF1/HF2/HF3 numerical bounds (research note provides ranges, exp_dev sets exact values)
- queue choice (tier hints only; exp_dev confirms per Tier A/B/C policy)
- pre-committed cap_map decisions (cap_map update gated on verdict, decided by verdict_handler not by this hand-off)

exp_dev applies its full envelope-fail-bands discipline, smoke-then-FULL pattern, per-experiment timeout formula, smoke gate, and post-ship REMOTE VERIFY per `agents/exp_dev.md`.

---

## Status_log + commit

Research sub-agent has logged `research_delivery` status_log entry referencing this hand-off path. Main thread should commit + push the research note and this hand-off as part of the standard post-research commit, then dispatch exp_dev via the `exp_dev` skill with this hand-off path as the routing input.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
