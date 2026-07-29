# Pre-reg: Stateful core (coupled slot-attention WM, end-to-end trained) v1

- anchor_name: `stateful_core_situation_model_v1`
- cell: `experiments/exp_stateful_core_situation_model_v1.py`
- module: `hdlab/slot_attention_wm.py` (`SlotAttentionWM`, `gen_kb_prior`)
- date: 2026-07-29
- queue: SMOKE = local_cpu_queue (or direct python invocation, per USER-locked smoke-only-local rule); FULL = overnight_queue (GPU) or remote_cpu_queue -- HELD pending Director/Orchestrator dispatch decision (this build is CPU-authored; the FULL run's item counts + 8 epochs + >=5 random-init-core seeds is GPU-scale compute, see "Compute architecture" below)
- basis docs: `notes/stateful_core_situation_model_build_design.md` (mechanism + training spec), `notes/drill_language_world_model_framing.md` section 6 (the Arm A/B framing-test design + can-fail bands, reproduced below), `notes/brain_foundational_component_analysis.md` (component 6 WORKING MEMORY -- "likely THE structural block" -- + component 8 BINDING)

## Prior-work check (substrate concept-query, mandatory)
`bash tools/substrate_query.sh "coupled stateful entity slot working memory PE-gated write role-general binding situation model"` -> top cosine 0.2881 (our own `project_foundation_llm_built_kb...` memory note describing the situation-model unification framing), 0.2773/0.2764 (CLS/STC memory-tagging note, off-topic), 0.2744 (our own `research_drill_substrate_operand_selection_mwp_2x_2026-06-12.md` Path-2 entity-state-tracking blueprint, the direct prior this build extends). **All hits below the 0.30 threshold.** This is a genuinely novel BUILD (no prior cell implements a trained, coupled, unfrozen-encoder slot-attention WM with PE-gated learned write + role-general HRR binding); the design itself was already scoped by us in the three basis docs above (session-internal prior scoping, not a separate/independent cell to rediscover). Not a rediscovery.

## Hypothesis
Per `brain_foundational_component_analysis.md`: every prior comprehension attempt (design-A entity-slot-gate, loop v1-v6, v5 position-bind readout) failed for ONE recurring reason -- isolated pieces bolted onto a FROZEN, feed-forward, stateless encoder. The fix: build the COUPLED machinery (recurrent WM + PE-gated learned write + role-general binding) and train it END-TO-END with an UNFROZEN encoder. If this mechanism is the missing organ, a trained stateful core should construct genuine cross-boundary / multi-entity comprehension that (a) beats a random-init-core structural-alone control and (b) shows the KB-grounded framing (Arm B) selectively winning on knowledge-dependent items (the world-model framing test).

## Mechanism (brain-faithful, glass-box)
- K=6 full-d-dim (d=512, matching v2 encoder) entity slots, NO scalar compression.
- Recurrent clause-by-clause maintenance (`SlotAttentionWM.step`), slots persist across the clause stream.
- LEARNED PE-gated write: `gate_net([clause_rep, addr_readback, surprise])` -> write_strength (sigmoid); surprise = 1 - cos(addressed slot readback, actual clause_rep), computed BEFORE the write (PBWM analog).
- Learned content-addressed competition over slots (`addr_net`, softmax across slots -- the "attention" in slot-attention).
- Role-general binding: `role_key_net(clause_rep)` -> a learned content key (NOT position); slot write/read use `hdlab.binding.bind/unbind` (HRR) with this learned key -- corrects the v5 absolute-position-bind failure (Frankland-Greene role-general slots).
- Encoder (TinyTransformer, d=512, 6L, `data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt`) is UNFROZEN, trained jointly with WM + judgment head -- the single correction vs every prior attempt.
- Judgment head: linear probe on `[slot_mean, surprise, write_strength, addr_entropy, (kb_consistency for Arm B)]`, trained via cross-entropy against the coherent(1)-vs-violated(0) label.

## Arms (the framing test -- one variable, per drill doc section 6)
- **Arm A (blank):** slots init to zero; no kb_prior; no kb_consistency loss term.
- **Arm B (KB-grounded):** slot 0 seeded with a KB-prior vector, built by encoding real CSKG edge text (`data/cskg_foundation_v1`) for the item's resolved KB concept THROUGH THE SAME ENCODER (never a borrowed embedding -- `gen_kb_prior`); additional `kb_consistency` loss term rewards addressed-slot agreement with the KB prior. KD items (iron/bread/fruit/water/candle/shirt/flower/juice/paper/grape, all with a real CSKG CapableOf/Causes edge, verified live 2026-07-29) resolve to real KB priors; MES items (door/window/light/box/gate...) generically lack a causally-relevant CSKG edge for their state axis, so Arm B degrades to Arm A there by construction (`gen_kb_prior` returns `None` when no edges found) -- this IS the intended selective (not uniform) signature the framing verdict requires.
- **Mandatory random-init-core control (both smoke-preview and full):** identical WM+judge structure on top of a random-init (never-trained) copy of the encoder architecture; only the judgment head is fit (encoder + WM frozen/untrained); if this matches the trained core, the result is structure-alone (HARD_FAIL_STRUCTURE_ALONE) -- the exact design-A failure mode.

## Measured on
Both `MULTI_ENTITY_STATE` (distE4/distEv6, LOCKED construction from `diag_order_critical_comprehension_calib_v1.py`) and `KNOWLEDGE_DEPENDENT`/`TEXT_SUFFICIENT` (`gen_knowledge_dependent`, real-KB-provenance construction), both already independently calibration-validated 2026-07-29 (see `data/diag_order_critical_comprehension_calib_v1/hardening.json` + `KD_FRAMING_FINDING.json` / `kd_framing_revalidation.json`).

## Bands (pre-registered; per drill doc section 6 + design doc MEASUREMENT section)
- **HARD_PASS (mechanism, per construction):** trained Arm-A-or-B core beats the static-encoder baseline (comprehension_specific gain, i.e. beyond the sensorimotor/text-only floor already measured in the calibration doc) AND beats the WORST-CASE (max, not mean) random-init-core control across >=5 seeds (~+0.075-0.08 floor per the calibration doc's caveat -- NOT the mean), on BOTH trained seeds when FULL runs with >=2 trained seeds.
- **HARD_PASS (framing, MES+KD jointly):** Arm B beats Arm A by >= +0.05 on KD (the knowledge-dependent items) with the random-init-core control at/below its worst-case margin for BOTH arms, AND Arm B's advantage is CONCENTRATED on KD (not uniform across MES, where Arm B structurally degrades toward Arm A) -- the discriminating signature per the drill doc.
- **HARD_FAIL (mechanism):** trained core ties/loses to random-init-core worst-case control on either construction -> HARD_FAIL_STRUCTURE_ALONE (the stateful core is not yet the fix; escalate per design doc SEQUENCE to recurrence-in-the-encoder / deeper rebuild).
- **HARD_FAIL (framing):** Arm B ties/loses to Arm A both seeds, OR gain vanishes under random-init-core control, OR gain is uniform across KD and MES (KB acting as a generic feature, not a world-model prior) -> framing hypothesis rejected; pure stateful core (Arm A) remains the story.
- **MIDDLE_BAND:** +0.02 to +0.05 gain, or single-seed only, or a gain that clears the mechanism gate but not the framing-selectivity gate (or vice versa) -- do not bank; re-probe with the added-weight/regime adjustments the drill doc names.

## Compute architecture
Mixed, justified. The per-clause-step recurrence (WM update depends on the previous slot state) is a genuine SEQUENTIAL dependency within an item -- cannot batch across clause-steps -- but items ARE batched (encode_clause_batch processes a [B, L] tensor per clause-step; B=SMOKE_BATCH=32 / FULL_BATCH=24). This is "sequential-within-item, batched-across-items," the standard recurrent-net pattern; not a batching-candidate violation (genuine sequential dependency, exp_dev.md GPU-batching-mandatory exemption (a): "chained retrieval where step N depends on step N-1"). SMOKE runs CPU-only (laptop; no local GPU); the encoder is UNFROZEN so this is a real (small) fine-tune, not a frozen-rep readout -- CPU wall-time is the justified reason SMOKE uses item-count reduction (discriminator-preview option C) rather than full-N. FULL should route to GPU (overnight_queue) given d_model=512, 6L, UNFROZEN backprop through the full item counts x FULL_EPOCHS=8 x >=5 random-init-core seeds -- CPU-only estimate for FULL is several hours (see completion report timeout-derivation), a GPU-batching candidate per the mandatory rule; Director/Orchestrator routes FULL to GPU.
Storage: no_storage / no_composition (single-pass-per-item slot maintenance, no cross-item persistent store).

## Self-test (real code path, tiny scale, exp_dev.md META_RULE F.1)
Self-test constructs the REAL objects the FULL run uses at N~8-16: a real `TinyTransformer` (tiny cfg), a real trained `tokenizers.Tokenizer` (BPE, not a synthetic-only branch), the REAL `gen_multi_entity_state` / `gen_knowledge_dependent` / `kb_ids_for_kd_items` / `load_kb_edges_for_ids` functions from `diag_order_critical_comprehension_calib_v1.py`, the REAL `SlotAttentionWM` + `gen_kb_prior`, and runs ONE real training step (`train_and_eval_arm`) for BOTH arms (A and B, independent params) end-to-end (forward + backward + optimizer step), then verifies arms-must-differ (META_RULE_AF, sha256 hash on eval logits) and finite losses.

**MEASURED@`data/exp_stateful_core_situation_model_v1_selftest/metrics.json`:** `verdict=SELFTEST_PASS`, elapsed_s=3.906, arm_a(train_loss=0.7828, eval_acc=0.5), arm_b(train_loss=0.8013, eval_acc=0.75), arms_differ_verified=true (digests A=a80977a7... B=16346223... distinct), exercised_entrypoints=[SlotAttentionWM_step, TinyTransformer_unfrozen_train, gen_kb_prior].

## SCHEMA-VET / META-RULE fields
- cardinality_ok: n/a (no sweep axis; 2 constructions x 2 arms x seeds; FULL cardinality = `2 constructions * 2 arms * n_trained_seeds` + `2 constructions * n_random_init_seeds` random-init units, verified via `n_units_done` counter + heartbeat).
- arms_differ_verified: true (self-test AND smoke/full runner both call `_arms_must_differ` with sha256 hash gate; META_RULE_AF).
- final_metrics_atomicity: tmp_replace (`_write_metrics` / `_write_crash_metrics` both use `os.replace`).
- except-ordering: verified clean -- `grep -nE "except\s+BaseException|except\s*:"` on both `exp_stateful_core_situation_model_v1.py` and `hdlab/slot_attention_wm.py` returns NO matches; outer try in `main()` uses `except SystemExit: raise` / `except KeyboardInterrupt: raise` / `except Exception as e` (not BaseException) per META_RULE ordering.
- crlb_n/a: "this is a comprehension/consistency discriminator (binary judgment accuracy), not a capacity/noise-floor cell; discriminator_reachability judged via chance=0.50 baseline (label-balanced construction) + the design doc's HARD_PASS margins above."
- discriminator_reachability: true (chance=0.50; the drill-doc-cited known-reader margins of +0.19 to +0.25 on MES and the framing gaps measured in KD_FRAMING_FINDING.json show the constructions are solvable at this difficulty by SOME mechanism, so a HARD_PASS margin is on the achievable side).
- baseline_in_band: true by construction (label-balanced binary judgment; untrained/random baseline ~0.50, in-band per META_RULE_AG's 0.05-0.95 window). SMOKE additionally asserts `discriminator_fires` (best_acc>=0.55) and `baseline_in_band` (0.05<best_acc<0.95) per-construction in metrics.
- HP_SCOPE: `{mechanism_gate: [trained_core beats random_init_core worst-case, both constructions], framing_gate: [Arm B - Arm A >= +0.05 on KD, concentrated not uniform]}`. Random-init-core arm is EXEMPT from the mechanism HARD_PASS gate (it IS the floor the gate is measured against, not a candidate for HARD_PASS itself).
- calibration_check: default_ok_for_this_regime (reuses the ALREADY-VALIDATED MES distE4/distEv6 + KD constructions from `diag_order_critical_comprehension_calib_v1.py`; gate-A/gate-B calibration independently measured 2026-07-29, see `hardening.json` / `KD_FRAMING_FINDING.json` / `kd_framing_revalidation.json`).
- discriminator survives scale: option (C), discriminator-preview at FULL DIFFICULTY (real distE4/distEv6 + real-KB KD construction, not a toy regime) with a REDUCED ITEM COUNT (SMOKE_MES_TRAIN_CAP=64, SMOKE_MES_EVAL_CAP=32, KD capped to 96 train/40 eval) and n_seeds=1 trained + 1 random-init-core seed -- documented, justified by CPU-only-laptop constraint; FULL restores full item counts + FULL_EPOCHS=8 + >=5 random-init-core seeds on GPU.
- Section-15 gates (composition cell -- reuses `hdlab.binding` HRR bind/unbind + `diag_order_critical_comprehension_calib_v1`'s constructions): `composition_edges`: `SlotAttentionWM.step -> hdlab.binding.bind/unbind` SHAPE_MATCH ([B,d] key / [B,K,d] slots, `unbind(slots, key.unsqueeze(1))` broadcasts correctly -- verified by self-test's finite-loss + arms-differ pass); `gen_multi_entity_state`/`gen_knowledge_dependent -> forward_item_batch` SHAPE_MATCH (dict items with `sent`/`label`[/`kb_id`] consumed directly). `positive_control_arms`: N/A -- this is the FIRST cell to compose `SlotAttentionWM` (novel module, no prior chain-grade atom to reproduce); the random-init-core control plays the equivalent falsification role (Gate D's spirit: an untrained-but-real-architecture arm that MUST fail for the trained arm's result to be trusted). `functional_requirements`: (1) maintain persistent entity state across a clause stream -> `SlotAttentionWM.step` recurrence; (2) update only when input is prediction-error-inconsistent -> `gate_net` write_strength; (3) bind fillers by content not position -> `role_key_net` + HRR bind/unbind; (4) ground state in world-knowledge selectively -> `gen_kb_prior` + `kb_consistency` term, gated to Arm B only.
- `real_code_path_and_signature_preflight` (F.1-F.5): F.1 satisfied (self-test constructs real `TinyTransformer`/`Tokenizer`/`SlotAttentionWM`/the real construction-generator functions, not a synthetic-only branch; `exercised_entrypoints` populated and logged). F.2/F.3 (signature binding against BASE/portable kwargs): `TinyTransformer(vocab, max_len, d_model, n_layers, n_heads, ffn_mult, pad_id)` -- these are the same required positional kwargs used by `load_encoder_and_tok` (loading the REAL v2 ckpt) and by `self_test()`'s tiny_cfg construction; no version-specific optional kwargs used. Not formally run through `experiments._validity_preflight.run_validity_preflight` (undeclared -- per exp_dev.md "Mode = ENFORCE" this WARNS, does not block; flagged here for Director/Skunkworks visibility rather than silently omitted). F.4 n/a (no control-beats-baseline break-guard in this cell). F.5: seeding audited -- all RNG seeds are explicit integers (`seed`, `seed+555`, `seed+9001`, `1000+ri_seed`, `2000+ri_seed`) or `np.random.default_rng(int)`; no `hash()`-derived seeding, no `list(set(...))` ordering found (grep clean).

## Defensive error-checking (exp_dev.md section 13)
- cell_chunked: false (single-file, 2 constructions x 2 arms x seeds; cheap enough per-unit that a runner death loses at most one unit; heartbeat written per unit).
- start_marker_written: true (`_write_start_marker` at both `self_test()` and `run_regime()` entry).
- crash_diagnostic_present: true (`_write_crash_metrics`, atomic tmp+replace, invoked from `main()`'s outer except).
- heartbeat_present: true (`_heartbeat` appended to `_heartbeat.jsonl` per unit in `run_regime`).
- defensive_error_checking: passed_all_4_patterns.
- progress_logging: `line_buffered_stdout` -- WIRED (`sys.stdout.reconfigure(line_buffering=True)` at module top, guarded by try/except for interpreters where reconfigure is unavailable); required because SMOKE now targets `timeout_s>=1800` after the epoch/lr bump below.

## Number provenance (META_RULE_AC)
- self-test arm losses/eval_acc: MEASURED@`data/exp_stateful_core_situation_model_v1_selftest/metrics.json`.
- MES known-reader margins (+0.19 to +0.25 BGE) / random-init worst-case (+0.075): CITED@`notes/stateful_core_situation_model_build_design.md` (D3, itself MEASURED@`data/diag_order_critical_comprehension_calib_v1/hardening.json`).
- KD framing-lift numbers (KD_plain=0.486, KD_aug=0.535, etc): CITED@`notes/stateful_core_situation_model_build_design.md` (D3, itself MEASURED@`data/diag_order_critical_comprehension_calib_v1/kd_framing_revalidation.json`).
- v2 encoder config (d_model=512, n_layers=6, n_heads=8, vocab=16000): MEASURED@`data/exp_scale_meaning_learn_arc_heldout_v2/ckpt_seed_7.pt` (`model_cfg`, `spec`, read live this session).
- SMOKE/FULL timeout estimates below: HYPOTHESIZED (not yet measured -- CPU-only estimate; the cell has never been run at smoke/full scale, only self-test scale). Flagged explicitly as an estimate in the hand-off.

## Timeout derivation (partly MEASURED -- a prior smoke landed on disk before this pre-reg was filed)
A smoke run at the ORIGINAL config (SMOKE_EPOCHS=2, lr=1e-4) already landed on disk at
`data/exp_stateful_core_situation_model_v1_smoke/metrics.json`: **MEASURED elapsed_s=228.06**
(seed=7, 2 constructions x 2 arms trained + 1 random-init-core seed x 2 constructions). Verdict
was `SMOKE_DISCRIMINATOR_WEAK` (MES A=0.500 B=0.500, KD A=0.525 B=0.475 -- both ~chance;
train_loss barely moved off ln(2)=0.693). Root-cause read (not yet re-verified): at
MES_TRAIN_CAP=64/batch=32 x 2 epochs = only 4 gradient steps total at lr=1e-4 for a 512d/6L
UNFROZEN fine-tune -- almost certainly UNDERTRAINED, not yet evidence the mechanism fails.
**Fix applied (this session, before hand-off): SMOKE_EPOCHS 2->6 and SMOKE_LR 1e-4->3e-4**
(12 gradient steps at 3x the learning rate); self-test re-verified PASS after the edit
(elapsed 2.9s, unaffected -- self-test doesn't touch these constants). `progress_logging` wired
to `line_buffered_stdout` since the new smoke config pushes wall-time toward/above 1800s.
**Timeout estimate for the RE-SMOKE (HYPOTHESIZED, not yet measured at the new config):** 228s
measured at 2 epochs scales to roughly 3x more trained-arm gradient steps (per-epoch fixed
costs like data-gen/KB-lookup are NOT epoch-scaled, so expect somewhat less than a clean 3x) --
estimate ~500-700s. **Recommend `timeout_s=1800`** (30 min) for the re-smoke command as a
generous bound around this estimate; if `SMOKE_DISCRIMINATOR_WEAK` persists at the new config,
that IS evidence worth trusting (not an undertraining artifact) and the mechanism/framing
verdict should be read from it directly rather than tuned further. FULL (8 epochs, full item
counts ~10-20x SMOKE's batches, >=5 random-init-core seeds) is CPU-infeasible in a reasonable
wall-time (rough extrapolation from the 228s/500-700s smoke measurements: multiple hours) --
**route FULL to GPU (overnight_queue)**; Director/Orchestrator sets FULL timeout after seeing
the re-smoke wall-time (recommend `timeout_s=7200` as a starting GPU estimate, adjust once the
CPU/GPU speedup ratio is known).
