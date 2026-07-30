# DIRECTOR POST-COMPACTION BACKUP — FULL STATE (2026-07-30, ~12:00Z)

Self-contained recovery doc. READ THIS FIRST after compaction, then notes/WHERE_WE_ARE_NOW.md (live detail), then MEMORY.md CURRENT FOCUS. First action: heartbeat `date -u +"%Y-%m-%dT%H:%M:%SZ" > d:/AI/hd-instrument/data/heartbeats/research.timestamp`.

## THE GOAL (unchanged)
Glass-box VSA/HDC substrate that genuinely COMPREHENDS, earning meaning the brain's way. Invariants: NO borrowed embeddings/LLM at inference; NO bolt-on reader/parser; from-scratch encoder; supply KNOWLEDGE/STRUCTURE ok, supply MECHANISM = forbidden. USER: align to brain, do the HARD thing not easy paths, don't lose focus, VET positives HARDEST.

## 🎯 THE IMMEDIATE POST-COMPACTION FOCUS (do this)
**Read the result of the read-conditioning fix experiment [agent abd107fa, launched ~11:55Z] — it is THE frontier.** It tests whether the proven WM can learn NL binding once the reps are conditioned (whiten/standardize + aux slot-address loss + warm-start). Metrics land at `data/exp_selective_overwrite_recall_nl_wm_roleseparated_v1*` (or a new dir the agent picks; check its report / disk). Branches:
- **WM_NL_PROVEN_VIA_READ_CONDITIONING** (any fix makes it learn+GENERALIZE, both seeds, random-init still fails) → the FIRST genuine content-gated NL comprehension. VET HARDEST via skunkworks (can-fail clean, generalization, mechanism) before banking. Then elaborate one-variable + harder/online tasks.
- **STILL_CANT_ALL_FIXES** → THEN (and only then) the encoder-objective pivot is EARNED (see below).
If the agent died/hung (check GPU/CPU + .out mtime; latent-PC died silently earlier), re-dispatch it.

## THE ARC (how we got here, so you don't re-litigate)
1. **Comprehension barrier** (open >1wk). We built a coupled stateful core (slot-attention WM + PBWM gating + role-query + bistable EST/SEM segmentation, encoder unfrozen). It would NOT train at MES scale.
2. **4 evidence-driven reversals** (all caught by the TRUSTWORTHY GATE, not cheap probes — probes misled ~3x): (a) "encoder thin" X; (b) "WM collapses" X; (c) "freeze fixes it" X; (d) unfreeze-collapses. RESOLVED: MES is order-critical but RESERVOIR-decodable (random-init whole-sentence attention = 0.80), so MES cannot test LEARNED comprehension; and the clause-split pipeline destroyed cross-clause order.
3. **Reframe (3 lit-scans, design note notes/wm_value_regime_and_contextual_stream_design_2026-07-30.md):** an explicit WM is non-redundant only for ONLINE/content-gating (not short offline). Fix = shared encoder pass → slice by event → sequential content-gated WM. Reservoir-failing task needed to prove the WM.
4. **✅ WM_PROVEN — CONFIRMED (skunkworks a81301a6, commit 88d050955):** the simplest content-gated overwrite WM (EntNet-style) LEARNS + GENERALIZES the "Selective-Overwrite-Recall" reservoir-failing task (eval 0.84 vs 0.05 random-init floor, z~49, both seeds). FIRST VET-confirmed positive. The maintain/update ORGAN works. CAVEAT: init-fragile ~40-50% duds; the proof used a DEGENERATE encoder (clean slot+filler) so it's MECHANISM-only, NOT binding/comprehension.
5. **NL binding arc (the hard part):** rendered the task as natural text (calibrated NL_RESERVOIR_FAILING_VALID, commit 1e1a49e95 — reservoir + pooled readers = chance, oracle = 1.0). Ran the proven WM on our REAL v2 encoder (FROZEN): **2 tests BOTH CANT_LEARN** (pooled f82370cd1, role-separated b3e5c0b7f).
6. **VET SAVED A WRONG PIVOT (skunkworks a1f31e21 = PARTIALLY):** the frozen MLM token reps ARE entangled (cross-leak ~0.99) — BUT "encoder must change" is REFUTED. Held-out-filler slot decode = 1.0; event→query cross-context transfer = 1.0 → the reps CONTAIN a filler-invariant, generalizing slot address; a read-path CAN extract it. REAL BLOCK = the slot signal is in a LOW-VARIANCE SUBSPACE swamped by a large shared component; the WM's raw softmax(x·key) on un-standardized reps is dominated by the shared component → identical address for all queries → STUCK_FLAT = a CONDITIONING/optimization gap, NOT the encoder.

## THE CORRECTED DIRECTION (post-compaction)
**CHEAP READ-CONDITIONING, not encoder pretraining** (in flight abd107fa): (1) WHITEN/standardize reps (remove dominant shared component) before addressing; (2) AUX slot-supervised address loss (CE address-logits→slot id); (3) WARM-START key from the working logistic slot-probe. The encoder-disentanglement-objective pivot (forward-predictive / binding-consistency; measurable = drive cross-leak DOWN) is the FALLBACK — EARNED only if all 3 read-conditioning fixes fail. Do NOT commit to expensive encoder pretraining until then.

## KEY FILES / COMMITS (all LOCAL, push-free — no origin push without in-session USER auth)
- Proven WM: experiments/exp_selective_overwrite_recall_wm_v1.py (88d050955); calib experiments/exp_selective_overwrite_recall_calib_v1.py (db39c1082).
- NL task VALID: experiments/exp_selective_overwrite_recall_nl_calib_v1.py (1e1a49e95).
- NL WM fails: exp_selective_overwrite_recall_nl_wm_v1.py (f82370cd1), exp_selective_overwrite_recall_nl_wm_roleseparated_v1.py (b3e5c0b7f).
- Design + regime: notes/wm_value_regime_and_contextual_stream_design_2026-07-30.md, notes/encoder_representation_lever_ranking_2026-07-29.md, notes/brain_foundational_component_analysis.md.
- VET recompute script (has the WORKING slot-probe + cross-context tests to reuse for warm-start/aux-loss): scratchpad/vet_rc.py.

## STANDING STATE / DISCIPLINES (load-bearing)
- **VET POSITIVES + PIVOT-DRIVING NEGATIVES HARDEST via skunkworks** — this session it caught 3 mislead-probes AND a wrong expensive encoder pivot. Route decisive Qs through the TRUSTWORTHY GATE / recompute, not cheap probes.
- **ONE VARIABLE at a time** (the whole detour came from stacking 3 WM changes on an underpowered 64-item smoke). Measurement-first: can-fail (random-init MUST fail) before the mechanism.
- **Freeze the (adequate) encoder + train the read/WM** (unfreezing collapsed). The encoder CONTAINS the binding signal; the gap is reading it.
- Push-free scp only; NO origin push w/o in-session auth. Only kill what THIS session spawned. Heartbeat every turn-end.
- **30-min SELF-DRIVE CRON active (33e3a028)** — silent-death sweep + heartbeat + brain-check + advance (SESSION-ONLY, dies on compaction/restart; RE-CREATE it post-compaction if wanted). latent-PC encoder run DIED silently in data-prep (deprioritized; that's why the cron exists).
- IN FLIGHT at compaction: abd107fa (read-conditioning fix — THE frontier). Watchers/other agents from before are stale.

## HONEST SCORECARD
Real, VET-confirmed progress: the WM maintenance/gating ORGAN is PROVEN. The NL binding is NOT yet solved but is precisely diagnosed as a read-CONDITIONING gap (encoder reps contain the signal), with cheap fixes in flight. NOT yet natural-language comprehension. No overclaims. The next result (abd107fa) is the immediate focus.
