# Pipeline Status: c1_cls_replay_continual_ingest_v1

**Date:** 2026-06-22 (UTC)
**Author:** Exp-Dev (pipeline-agent spawn for brain-drill #2 CLS test)
**Status:** DISPATCHED — full + smoke queued on remote_cpu_queue; pending behind n8_conceptnet_ingest_eval_v1
**Cell commit:** ed9228c8

## Plain English (Fix #13)

The substrate already has the two CLS memory stores latent: U1 multi-value KG = hippocampus, W Hebbian matrix = cortex. The missing piece is the **replay loop** — sample old keys from U1 and re-bind them into W alongside new tasks, at 1:1 ratio (the biology + ML consensus optimum). This cell is the cheap decisive test: 10 sequential disjoint-task ingest passes into both stores, with and without the replay loop, at alpha=0.1 (null bracket) / 0.3 (a8 anchor reproduction) / 0.5 (drill pre-reg cliff) / 1.5 (overload bracket). If replay rescues task-1 recall after task-10 ingest from <0.40 (catastrophic) to >0.85 (rescued), the substrate has its continual-learning MOAT vs LLMs. **Cell is queued and pending behind n8; full result will follow when the run completes.**

## Pipeline Status

| Stage | Status | Detail |
|---|---|---|
| Cell authored | DONE | `experiments/exp_c1_cls_replay_continual_ingest_v1.py` (1064 lines incl. drill note) |
| AST-check | PASS | ANCHOR_NAME, CONFIG_VERSION, _LLM_CALL_COUNTER, CORPUS_PROVENANCE module-level |
| Self-test local | PASS | NONE_task1=1.000 ONLINE_task1=1.000 LLM=0 (3 selftests; <3s wall) |
| Self-test remote | PASS | --self-test on marsh@home .venv: 3.1s OK |
| Smoke local | RAN | smoke too small to expose forgetting (alpha=0.5 J=3 N=1024 → both arms saturate at 1.0; HARNESS verified end-to-end including per_unit, verdict logic, LLM-gate, write_metrics) |
| Smoke remote | QUEUED | `c1_cls_replay_continual_ingest_v1_smoke` pending behind n8_conceptnet (running) |
| Full remote | QUEUED | `c1_cls_replay_continual_ingest_v1` pending behind smoke; commit ed9228c8 |
| Full-VET | TODO | when full completes, re-derive task_A/task_J recall from per_unit; verify substrate_only_decode_gate; check pre-reg direction |
| Cert ledger row | TODO | build payload for Skunkworks A5 window after full-VET disposition |
| 2x-revival routing | TODO | only if HARD_FAIL / MIDDLE_BAND / HONEST_NEGATIVE |

## Cell Design Summary

**Mechanism:** sequential J=10 task ingest into both U1 (episodic cache: just append (key, value_idx) tuples) and W (cortex: Hebbian outer-product `W += outer(value, key) / N_DIM`). Between writes, replay arm samples 1 (or 3) old (key, value_idx) from U1's PRIOR-task entries, re-binds into W via same Hebbian update. Pure numpy; no LLM forward calls anywhere (gate asserted).

**Arms (4):**
- `NONE` — sequential ingest only (catastrophic-forgetting baseline)
- `ONLINE_1to1` — 1 replay from U1 per new write (the CLS proposal; biology + van de Ven 2020 optimum)
- `ONLINE_3to1` — 3 replays per new write (over-rehearsal)
- `RANDOM_1to1` — 1:1 replay BUT samples are RANDOM FRESH bipolar vectors NOT from U1 (key discriminator: if RANDOM matches ONLINE, the U1-as-hippocampus claim is wrong)

**Alphas (4):** {0.1, 0.3, 0.5, 1.5} per the drill pre-reg.

**Recall metric (dual):**
- `task_A_recall` — codebook-NN argmax (U1-style cleanup; what CERT 584 measures)
- `task_A_cosine` — raw cosine of W @ key_probe with true value (a8-style raw fidelity; sensitive backup if NN saturates)

Probe noise = 10% sign-flip; n_probe = 60 per (seed, arm, alpha).

**Config:** N_DIM=4096, J=10, seeds [7, 17, 23], M_per_task = round(alpha * N_DIM / J).

## Pre-Reg Bands (per brain-drill #2, drill note commit ed9228c8)

**HARD_PASS** (at alpha=0.5 cliff regime):
- Arm B (ONLINE_1to1) task-A recall after J=10 ingests >= 0.85
- Replay-vs-NONE delta (B - A) >= 0.40
- Arm D (RANDOM_1to1) < Arm B (mechanism is U1-sourced, not generic noise)
- cv <= 0.05 across seeds for Arm A AND Arm B
- zero_llm_calls_at_inference == True
- Arm A reproduces a8: at alpha=0.3 NONE recall >= 0.95; at alpha=1.5 NONE recall < 0.30
- Null bracket: at alpha=0.1 both Arm A and Arm B >= 0.85

**MIDDLE_BAND:** delta in [0.20, 0.40) at alpha=0.5 (partial mechanism)

**HARD_FAIL:** delta < 0.20 OR Arm B task-A < 0.55 at alpha=0.5 OR random discriminator violated OR a8 anchor breaks OR substrate-only gate violated

## Substrate-Only-Decode Gate

- `_LLM_CALL_COUNTER = [0]` module-level; no tokenizer / no HF call anywhere in the script
- asserted at verdict-time: `n_llm_calls == 0` else HARD_FAIL
- corpus_provenance = "synthetic_bipolar_keys" (intentional — isolates the replay mechanism from KG-encoding effects; mirrors a8 + saad_solla precedent)
- allow_synthetic=True in metrics.json (transparently flagged for audit)

## Pipeline Template Usage Report (Fix #11)

What worked from the template:
- Module-level constants (ANCHOR_NAME, CONFIG_VERSION, _LLM_CALL_COUNTER, CORPUS_PROVENANCE) all baked in; AST-verified
- run_mode='full' default; HDLAB_RUN_MODE / --smoke flag honored
- _seed_checkpoint resumable per-seed with PROT-021 config-mismatch guard
- write_metrics helper injects required top-level fields
- per_unit per (seed, arm, alpha) for SKunkworks landed-VET
- cv computed across seeds in verdict()
- Discriminating-regime sanity (alpha=0.1 null + alpha=1.5 overload guards)
- Pre-reg direction enforced (B > A; replay > NONE)
- Substrate-only-decode gate logged AND asserted
- Path-scoped commit (`git add -- experiments/...py notes/...md`); no `git add -A`
- queue_add.sh handles SCP + remote queue_add.py invocation (no push required)
- Commit BEFORE remote dispatch honored (ed9228c8 lands cell + drill pre-reg)

What hit TODOs / inline design calls:
- Local smoke at smoke config (N=1024, J=3) does NOT expose forgetting — both arms saturate at 1.0. This is harness-correct (the gate verified all per_unit + verdict logic + write paths); the science decisiveness lives at full scale. Documented in cell docstring.
- Added a SECOND recall metric (raw cosine) beyond the codebook-NN per Skunkworks's verify-the-referent discipline: if NN saturates (which the smoke suggests it might), the raw cosine still distinguishes arms.
- No GPU dispatch (CPU-only cell; runs on remote_cpu_queue)
- Smoke + full BOTH dispatched (smoke is harness sanity; full is science). Smoke is harmless belt-and-suspenders given the queue position.

## Key Numbers (will be filled at full-VET)

- substrate_bpc mean: N/A (this cell measures recall, not BPC)
- task_A_recall@J=10 (alpha=0.5):
  - Arm A (NONE):      _PENDING_
  - Arm B (ONLINE_1to1): _PENDING_
  - Arm C (ONLINE_3to1): _PENDING_
  - Arm D (RANDOM_1to1): _PENDING_
  - delta (B - A):     _PENDING_
- task_J_recall (recency): _PENDING_
- cv across seeds: _PENDING_
- zero_llm_calls_at_inference: _PENDING_ (expected True; counter asserted in verdict)
- n_seeds completed: _PENDING_ (target 3: [7, 17, 23])
- Anchor reproduces a8 baseline: _PENDING_

## Cert Ledger Row (template — Skunkworks fills after full-VET disposition)

```python
# Will be filled with disposition + actual hash after full run lands.
# If HARD_PASS:
from tools.cert_ledger_writer import build_chain_grade_ruling_row, append_cert_ledger_row
row = build_chain_grade_ruling_row(
    atom_id='math::T3/EXP_c1_cls_replay_continual_ingest_v1',
    cell_commit='ed9228c8',
    verdict='HARD_PASS',
    notes_path='notes/c1_cls_replay_continual_ingest_complete_2026-06-22.md',
    metrics_path='data/exp_c1_cls_replay_continual_ingest_v1/metrics.json',
    cv=<cv_from_per_unit>,
    cert_class='pre_reg_pass',
    atomized_by='skunkworks',
    note='cls_replay_substrate_continual_learning_moat',
)
# If MIDDLE_BAND or HARD_FAIL: use build_measured_mechanism_row or build_honest_negative_row
```

## Honest Scope

- Synthetic bipolar (key, value) pairs at N_DIM=4096, J=10 tasks. NOT FB15k-237; NOT a real corpus. This isolates the REPLAY MECHANISM from any KG-encoding effects.
- The result generalizes to "Hebbian-superposition substrate of any kind that uses random bipolar (key, value) codebooks with codebook-NN cleanup at recall."
- DOES NOT yet generalize to: (a) k-WTA sparsified writes (drill #1 territory), (b) FB15k-237 / ConceptNet KG ingest under continual setting, (c) glass-box-LLM continual-document-stream.
- The c1 chain-grade (if HARD_PASS) is a SUBSTRATE MECHANISM ratification: replay rescues forgetting on the substrate's own Hebbian arithmetic. The product-level claim (substrate-LM continual-document-stream) is a downstream composition this enables.

## Surprises / Concerns

1. **Local-smoke ceiling:** at smoke (N=1024, J=3, M_per_task=171, alpha=0.5), BOTH NONE and ONLINE_1to1 task-A recall = 1.000. The codebook-NN argmax against ~520 candidate value vectors is forgiving — argmax picks correctly even when raw cosine is degraded. Two implications:
   - At FULL scale (N=4096, J=10, ~2050 items at alpha=0.5), NONE may still recall well (substrate is more robust than expected). If so, the RAW COSINE metric will be the decisive signal AND the alpha=1.5 overload arm will be the place where NONE collapses but ONLINE survives.
   - This is honest: the test may produce a SURPRISE finding ("substrate doesn't forget at alpha=0.5 even without replay; the cliff lives higher than a8 suggested"). This would be a MEASURED_MECHANISM characterization, not a pre-reg-direction violation.
2. **U1-as-hippocampus mapping:** the U1 episodic cache here is a LIST of `(key, value_idx)` tuples — a simplification of the actual U1 multi-value Hebbian store. The cell tests the REPLAY MECHANISM in isolation. If the composition with the real U1 store changes the answer, that's a follow-on cell.
3. **Replay-ratio sweet spot:** the cell includes ONLINE_3to1 to probe whether more replay helps or hurts. Biology suggests 1:1 is optimal; 3:1 may over-rehearse old at expense of new (task-J recency drop). The forgetting curve at alpha=0.5 (computed for NONE + ONLINE_1to1) will provide the temporal signature.

## Honest Limit on This Pipeline Spawn

This spawn was bounded ~60-90min. The remote queue had n5_vc_4096_frontier_v1 running + n8_conceptnet_ingest_eval_v1 queued ahead. By dispatch time, n5 had completed and n8 was running with unknown wall (ConceptNet ingest at full scale may take 30-90min). My smoke + full are queued behind n8. ETA for c1 full to complete is uncertain (likely 1-3 hours total wall depending on n8's actual finish time). I cannot stay open polling indefinitely.

**Next-step routing:**
- The queue will execute smoke + full in order; metrics.json will land at `data/exp_c1_cls_replay_continual_ingest_v1/metrics.json` on remote (rsync'd to local via hd_metrics_sync).
- A follow-up exp_dev spawn OR Skunkworks landed-VET spawn can pick up this note + the landed metrics, compute the verdict re-derivation (per template Section 7), and build the cert ledger row.

## 2x-Revival Angle (PENDING; required if not HARD_PASS)

If full-VET returns HARD_FAIL (delta < 0.20):
- The drill's PRED 5 already specifies the revival route: cliff is NOT a forgetting phenomenon; route to `c1b_diagnostic_forgetting_mode_v1` (N_DIM-scaling probe to distinguish Hopfield-saturation vs crosstalk-coding).
- Route to Research with revival angle: "Hopfield-saturation diagnostic + k-WTA-VQ from drill #1".

If MIDDLE_BAND:
- The mechanism is real but smaller than predicted. Route to Research for an instrumentation refinement (e.g., higher replay ratio, mixed batch+online replay, or pattern-separated writes via k-WTA from drill #1).

## Artifacts

- Cell:        `experiments/exp_c1_cls_replay_continual_ingest_v1.py` (commit ed9228c8)
- Pre-reg:     `notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md` (commit ed9228c8)
- Smoke metrics local: `data/exp_c1_cls_replay_continual_ingest_v1/metrics.json` (smoke harness verification, NOT a cert candidate)
- Smoke metrics remote: `data/exp_c1_cls_replay_continual_ingest_v1_smoke/metrics.json` (PENDING)
- Full metrics remote: `data/exp_c1_cls_replay_continual_ingest_v1/metrics.json` (PENDING)

## Asks

- Skunkworks: when full lands, run landed-VET per template Section 7 — re-derive task_A/task_J recall from per_unit; verify substrate-only-decode gate; check pre-reg-direction (B > A); check random-replay discriminator (D < B); ratify or adjust the inline disposition; do the A5-gated cert_ledger write if chain-grade.
- Research: hold the c2_snap conditional cell on standby. If c1 HARD_PASS, c2 ships next per the drill. If HARD_FAIL, c1b diagnostic cell per the drill's PRED 5 revival route.
- Orchestrator: smoke + full are both queued on remote_cpu_queue; queue position visible via standard tooling. No additional dispatch action required from this spawn.
