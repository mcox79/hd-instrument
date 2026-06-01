# exp_dev hand-off — research: Bet B 4-stage architectural exhaustion

**Filed:** 2026-05-29 by research sub-agent (Opus 4.7 1M, DEEPER drill).

**Trigger:** `notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md` -- 4 training-axis rescues (Phase-D aweight v2 / rehab-epochs v3 / batch128 v1 / multitask diff-corpus v1) all confirmed sub-0.80 retention_A; cap_map v272 Bet B 4-stage row 🟡 PARTIAL; user v273 triage register names Cluster C (C1-C5) as only remaining Tier-1 path; C4 (gamma-1 dual-W CLS) shipped earlier today; remaining C1-C5 plus 3 NEW architectural variants surfaced by this drill.

**Pause state:** check `data/orchestrator_paused.flag` before ship.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHOR POINTERS + WHY-NOW only. exp_dev designs ALL of: N, seed count, threshold bands, queue choice, anchor name (PROT-018 compliant `_n<N>`), `--timeout` value (per PROT-019 formula), smoke profile, FULL profile, smoke-to-FULL gate.

---

## Anchor candidates (rank-ordered by expected-value = P * lift / cost)

### Anchor A1 (TIER 1, top-EV): TP-HDC subspace projection for Bet B 4-stage
- **Anchor pointer:** `notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md` Direction 2 row 1, Prediction P1, top-3 row 1.
- **Substrate-product reading:** Each Phase (A/B/C/D) trains in an orthogonal random projection subspace of the substrate's N hyperspace. Phase A in P_A x N subspace, Phase B in disjoint P_B x N subspace, etc. Retrieval queries the appropriate subspace given task ID. Substrate-compatibility HIGH (preserves HDC binding algebra). Direct lit precedent (arxiv 2004.14252 reported 96.4%-97.1% per-task on Split-MNIST). Predicted ret_A lift: +0.10 to +0.18 over baseline 0.745.
- **Tier hint:** GPU (4-stage chain at N=8192 5-seed FULL).
- **Why now:** Highest substrate-compatibility of all architectural variants surveyed. Single anchor decides whether architectural axis is productive at all. If A1 HARD-PASSes the Cluster-C alternatives (C1/C2/C3/C5) can be deprioritized; if A1 HARD-FAILs the substrate has an additional bottleneck beyond standard VSA CL theory and the architectural rescue chain is in genuine trouble.
- **Falsification:** ret_A < 0.78 at N=8192 5-seed FULL.

### Anchor A2 (TIER 1, cheapest implementation): Pool-retrieval generative replay during Phase D
- **Anchor pointer:** `notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md` Prediction P5, top-3 row 2.
- **Substrate-product reading:** During Phase-D training, sample N_replay items from the substrate's existing pool (retrieved via standard pool-retrieval) and mix them into Phase-D batches. The pool already contains Phase-A/B/C atoms; sampling them at train-time is the substrate-native CLS slow-consolidation analog. Substrate has the plumbing -- no new infrastructure needed. Predicted ret_A lift: +0.08 to +0.15.
- **Tier hint:** GPU (4-stage with mixed batches at N=8192 5-seed) OR cheap CPU smoke first (substrate pool already exists, mixing is trivial).
- **Why now:** **Cheapest substrate-compatible architectural rescue** (~0.5 day script edit). Mechanism-orthogonal to TP-HDC; can be combined. Strong cross-thread with the substrate's 🟢 pool-retrieval row and the McClelland-McNaughton-O'Reilly CLS theory.
- **Falsification:** ret_A < 0.78 at N=8192 5-seed FULL.

### Anchor A3 (TIER 1, leverages MoE 🟢 row): MoE-per-task with DG-gating (HiCL adaptation)
- **Anchor pointer:** `notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md` Direction 4 row 1 (CLS extension), top-3 row 3, Direction 5 row 4 (adjacent method).
- **Substrate-product reading:** Each of 4 phases trains its own MoE expert; retrieval gates via dentate-gyrus-style pattern-separation routing. Substrate's MoE K-scaling already 🟢 demonstrated -- this reuses confirmed infrastructure. Subsumes gamma-2 "Phase-A frozen architecture" (gamma-2 = frozen-Phase-A-expert case of A3). Predicted ret_A lift: +0.07 to +0.13.
- **Tier hint:** GPU (MoE 4-stage chain at N=8192 5-seed).
- **Why now:** Strongest synergy with existing cap_map 🟢 rows (MoE K-scaling). HiCL (arxiv 2508.16651, 2025) reports > 80% on sCIFAR 4-task. Brain-inspired framing maps cleanly to substrate-product narrative per [[feedback-brain-inspired]].
- **Falsification:** ret_A < 0.78 at N=8192 5-seed FULL.

### Anchor A4 (TIER 2, backup): GPM / null-space W update
- **Anchor pointer:** `notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md` Prediction P2, comparison table row 3.
- **Substrate-product reading:** Phase-B/C/D W updates projected onto null-space of Phase-A subspace. Substrate-native operation (orthogonal W projection). GPM literature (arxiv 2103.09762) reports 86-89% on 5-task Split-CIFAR-100. Predicted ret_A lift: +0.07 to +0.12.
- **Tier hint:** GPU.
- **Why now:** Mechanism-orthogonal to A1/A2/A3. Run as backup if top-3 underperform.
- **Falsification:** ret_A < 0.77.

### Anchor A5 (TIER 2, theoretical extension): Cascade-synapse K=3 W extension
- **Anchor pointer:** `notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md` Prediction P3, comparison table row 4, Direction 1 (theoretical anchor).
- **Substrate-product reading:** Promote substrate W from K=1 (bipolar) to K=3 metaplastic states per cell. Theory predicts power-law forgetting (Fusi-Drew-Abbott 2005 Neuron). Substrate extension non-trivial; argmax read must work over 3-state W. Predicted ret_A lift: +0.04 to +0.10.
- **Tier hint:** GPU (substrate change + 4-stage chain).
- **Why now:** Only variant with formal theoretical anchor for the 0.80 ceiling lift. Higher engineering cost than A1-A4; deprioritize relative to those but keep as Tier-2 backup if top-3 fall MIDDLE-BAND.
- **Falsification:** ret_A < 0.77.

### Anchor A6 (TIER 2, info-theory only): Free-prob multi-phase joint-spectrum prediction
- **Anchor pointer:** `notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md` Next-drill candidate.
- **Substrate-product reading:** Theoretical ex-ante prediction: given Phase-A spectrum + Phase-B spectrum + Phase-C spectrum, predict ret_A using free-probability R-transform / S-transform convolution of W spectra. Informational; could pre-screen architectural variants BEFORE running them.
- **Tier hint:** local CPU (theory + ~30 min CPU verification).
- **Why now:** Cheapest possible drill (~1 day theory); gives ex-ante substrate-native prediction for ALL anchor outcomes. Per research_field_advisor.py F4 free cumulants is top-5 next-drill (tier-1 fruit-bearing field). Not a Bet-B-clearing anchor but informs anchor design.

---

## Stretch candidates (if exp_dev has bandwidth)

### Anchor A7 (cluster combination): TP-HDC + pool-retrieval generative replay (A1 + A2 combined)
The three top-3 mechanisms (A1/A2/A3) are mechanism-orthogonal; combining gives the natural Tier-1-clearing anchor. Predicted ret_A under (A1 + A2): 0.83-0.90. Cost: ~1.5 days (A1 + A2 design); ~4h GPU. Run if A1 and A2 INDIVIDUALLY clear MIDDLE_BAND but neither HARD-PASSes alone -- combined might push over 0.85.

### Anchor A8 (gamma-2 / C2 cleanup): Phase-A frozen architecture (Cluster C original)
User-named gamma-2 from v273 Cluster C. Trivial implementation (freeze W after Phase A; Phase B/C/D learn in remaining W cells). Substrate-compatibility HIGH. Predicted ret_A ~ 1.0 (Phase A perfect) but at cost of ret_B/C/D. Run as a sanity check on the architectural axis -- if even frozen Phase A doesn't clear 0.80 at ret_A, something is fundamentally wrong with the 4-stage probe instrumentation.

### Anchor A9 (gamma-3 / extension): Hierarchical W architecture
User-named gamma-3 from v273 Cluster C. Multi-tier W matrix (fast-tier + slow-tier with consolidation between). Substrate-compatibility MEDIUM (needs new infrastructure). Cost: ~2 days. Run after top-3 (A1/A2/A3) verdicts land.

---

## Context pointers (pointers, not summaries)

- `notes/research_bet_b_4stage_architectural_exhaustion_2026-05-29.md` -- THIS drill; full quantitative comparison table + decision rationale.
- `notes/substrate_capability_map.md` -- v272 Bet B 4-stage row 🟡 PARTIAL; v273 ANNOTATION-ONLY user triage register names Cluster C; v270 4-axis rescue exhaustion documented.
- `notes/strategy_request_to_exp_dev_4stage_script_path_hygiene_2026-05-27.md` -- prior 4-stage routing context.
- `notes/wave14b_continual_learning_design.md` -- original 4-stage CL design.
- Anchor v189: `data/exp_wave14_betB_4stage_continual_v1` -- baseline ret_A=0.740.
- Anchor v239: `data/exp_bet_b_n8192_4stage_v2` -- N=8192 5-seed FULL ret_A=0.745.
- Anchor C4 / gamma-1 shipped earlier today: `data/exp_bet_b_cls_dual_w_smoke*` (find latest mtime).
- Pause state line: check `data/orchestrator_paused.flag`.
- Bridge state for queue depth: `python tools/orchestrator/state_check.py`.

---

## Contract section

- Pre-reg per `[[feedback-envelope-expansion-fail-bands]]`: each anchor must register HARD-PASS / HARD-FAIL / MIDDLE-BAND bands BEFORE smoke (already pre-registered in the research note for A1-A5; exp_dev may tighten).
- Smoke gate before FULL ship per [[feedback-strategy-spec-formula-selftests]].
- PROT-018 anchor-name `_n<N>` binding contract for all anchors.
- PROT-019 `--timeout` formula: `timeout = ceil(1.5 * smoke_wall_s * (FULL_N / smoke_N)^exp * (FULL_seeds / smoke_seeds))` with exp default 1.5.
- 6GB OOM ceiling pre-check per Section 3j of post-compaction brief.
- Import-chain coverage in smoke per Section 3k.
- ASCII-only in scripts per [[feedback-ascii-only-in-scripts]].
- REMOTE VERIFY each anchor post-ship.
- Self-test gate per `[[feedback-strategy-spec-formula-selftests]]`.

---

## Autonomy declaration

exp_dev decides:
- Which subset of A1-A9 to ship in this cycle (recommend top-3 = A1 + A2 + A3 if GPU bandwidth permits; otherwise A2 first as cheapest decisive).
- N, seed count per anchor (recommend N=8192 5-seed FULL to match v239 corroboration scale, but smoke first).
- Threshold bands (research note provides HARD-PASS / MIDDLE-BAND / HARD-FAIL recommendations -- exp_dev may tighten).
- Queue choice (Tier A/B/C per `agents/exp_dev.md` Section 0).
- Anchor name (PROT-018 compliant `_n<N>` suffix).
- `--timeout` value (per PROT-019 formula).
- Smoke profile + FULL profile.
- Smoke-to-FULL gate (pre-registered HARD-PASS gate).

Orchestrator does NOT specify numerical parameters per [[feedback-no-experiment-design-in-prompts]].

---

## Pre-registered closure trigger (HARD-FAIL coordination)

If A1 (TP-HDC) AND A2 (pool-retrieval generative replay) AND A3 (MoE-per-task) ALL HARD-FAIL at N=8192 5-seed FULL (ret_A < 0.77 for A1/A2; ret_A < 0.78 for A3), then formal Bet B 4-stage Tier-1 RESCUE EXHAUSTED status. At that point cap_map row stays 🟡 PARTIAL but Tier-1 0.80 bar is honestly closed; re-frame product narrative around observed ret_A=0.745 / ret_B=0.86 / ret_C=0.81 at product-bar 0.70.

If at least 1 of A1/A2/A3 HARD-PASSes: row promotes to 🟢 with Tier-1 demonstrated; killer-feature "true continual learning at production scale" gets concrete anchor.

If all 3 land MIDDLE-BAND: ship A4 (GPM) + A5 (cascade-K=3) + A7 (A1+A2 combined) as second wave.

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
