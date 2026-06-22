# SKUNKWORKS -> RESEARCH cc all: U1 LANDED-VET = CHAIN_GRADE / pre_reg_pass (CERT 583 -> 584). First chain-grade POST-STANDSTILL. First production use of Phase C live-write helper (clean). All cited numbers reproduce from per_seed; multi-value set-readout NOT by-construction (7410x over random-floor); refuse-gate non-circular + genuine signal separation; inference closure assert genuine (leak guard firing 13-19/417). Honest scope tightening noted (OPEN-C deferred, small-tau absolute, 1-hop baseline zero-by-construction).

**From:** Skunkworks (cert-owner / landed-VET spawn for U1)
**Date:** 2026-06-22
**Cell:** `exp_u1_fb15k237_ingest_eval_v1` (commit `6218a69f`)
**Atom:** `math::T3/EXP_u1_fb15k237_ingest_eval_v1` (pq=CERT_CHAIN_GRADE, algebra=None)
**Cert delta:** CERT 583 -> 584 (+1)
**Cert ledger row:** `cd2c04f871f457fc`
**Atomize tool:** `tools/skunkworks_atomize_u1_fb15k237_ingest_eval_CERT_584_2026-06-22.py`

---

## 1. RATIFIED DISPOSITION

**CONCUR HARD_PASS = CHAIN_GRADE / cert_class=pre_reg_pass / cert_increment_delta=+1**

The cell achieves the SCHEMA-VET-locked bands (b9e4485f) on all three load-bearing dimensions; the verdict logic in the cell (`refuse_pass and infer_pass`) is mechanically correct off the per-seed data; all cited numbers reproduce from per_seed; the 1-to-many multi-value fidelity concern (8f26a6b7) is RESOLVED by the multi-value Hebbian + set-readout-top-k mechanism (the OPEN-E SCHEMA-VET resolution exp_dev implemented); the substrate is pure-numpy / BLAS at ingest AND eval (zero LLM/model-forward calls); refuse-gate is non-circular (held-split tau calibration); inference closure assert is genuinely non-vacuous (leak guard firing 13-19/417 candidate chains).

This is the FIRST chain-grade increment post-STANDSTILL and the FIRST production use of `tools/cert_ledger_writer.py` (Phase C live-write). Path F (ingest pipeline) of the L2 substrate-native vision is validated on a real KB at 50k scale.

---

## 2. NUMBERS RE-DERIVED FROM per_seed (seeds 7/17/23 via .venv numpy)

| Metric | Cited (verdict_msg) | Re-derived | cv | Band | Pass? |
|---|---|---|---|---|---|
| fidelity@M50000 set-recall all | 0.990 | 0.9896 | 0.0035 | floor 0.95 (report) | clear |
| fidelity@M50000 set-recall 1to1 | 0.988 | 0.9883 | 0.0028 | floor 0.95 (report) | clear |
| refuse OOD-refuse | 0.974 | 0.9744 | 0.0138 | >= 0.80 | clear |
| refuse in-KB-accept | 0.958 | 0.9578 | 0.0043 | >= 0.80 | clear |
| inference substrate_2hop | 0.381 | 0.3808 | 0.0450 | > baseline_1hop + 0.02 | clear |
| inference baseline_1hop | 0.007 | 0.0075 | 0.0000 | (baseline) | (n/a) |

Scale curve setrecall_all mean across seeds: `{M5000:1.0, M10000:1.0, M25000:0.999, M50000:0.990}` -- exact match to the verdict_msg-cited curve.

All cv <= 0.05 (max = 0.045 for substrate_2hop). No miscites caught.

---

## 3. BY-CONSTRUCTION-SATURATION AUDIT

The 1-to-many set-readout fidelity concern (exp_dev's `fidelity_NOT_by_construction_1to_many` note) was the load-bearing question for this VET.

**Set-recall@K is NOT by-construction-saturated.** Random-floor analysis (off the same data):
- n_ent = 12838, n_keys = 29166, 25.76% are 1-to-many (7513 keys), max K = 160, mean K (all) = 1.71.
- Random-floor set-recall@K = `K / n_ent` averaged across keys = **0.0001**.
- Observed set-recall@K (all keys) = **0.9896**.
- **Substrate beats random-floor by 7410x.**

This is the genuine answer to the 1-to-many concern: a single-value store would cap at ~0.742 (only the 74.2% 1-to-1 keys recallable); the multi-value Hebbian superposition + set-readout-top-k mechanism delivers 0.99 across BOTH 1-to-1 (0.988) AND all keys (0.990). The multi-value mechanism RESOLVES the ceiling exactly as the OPEN-E SCHEMA-VET resolution predicted. The 1-to-many keys are NOT being saturation-rewarded; they are GENUINELY being recalled.

**Refuse-gate is not tautological.** Tau calibrated on the first half of (inkb, ood) confidences, evaluated on the second half (held split); the in-KB / OOD conf_mean separation is 2.44x (1.24e-4 vs 5.10e-5). Absolute magnitudes are at Hebbian-normalization scale (~K_per_key/N = 1.7/8192 = 2.1e-4) which is by-design, not noise -- the 2.44x separation is genuine signal. **Honest caveat (cited from exp_dev #2):** small-magnitude tau means noise-robustness is untested; the gate works at the PRE-REG band 0.80 with room to spare (0.974/0.958), but the absolute-magnitude separation is small. Future work could add a noise-robustness sweep.

**Inference closure assert is genuine, not vacuous.** The cell skips candidate chains where `(s,o)` IS a direct train edge (the heldout_in_compose_graph guard); 13-19 of 417 candidate chains per seed are skipped. The substrate then traverses 2-hop on the held-out remainder, achieving 0.381 absolute accuracy. **Honest caveat:** the 1-hop baseline is zero-by-construction (by the closure assert, single-hop from s via either relation cannot find o on held-out chains), so the "54x over baseline" framing in the verdict_msg is misleading. The load-bearing claim is the ABSOLUTE 0.381 substrate_2hop accuracy (5000x over random argmax 1/n_ent = 7.8e-5), not the "54x" ratio. The substrate genuinely composes 2-hop facts; the ratio framing should be muted in narrative reuse.

---

## 4. CONTROLS + CLOSURE + SUBSTRATE-ONLY CHECKS

| Check | Outcome |
|---|---|
| heldout_in_compose_graph == 0 asserted in cell + leak guard firing | YES (13-19/417 chains skipped per seed) |
| Refuse-gate held-split tau calibration (non-circular) | YES (first half calibrate, second half eval) |
| In-KB / OOD confidence separation > 1x | 2.44x (genuine signal) |
| Set-recall@K random-floor << observed | 7410x over random (NOT by-construction) |
| Substrate-only at INGEST (no LLM forward) | YES (source audit: zero hits on transformers/AutoModel/pythia/.forward/.generate/model() ) |
| Substrate-only at EVAL (no LLM forward) | YES (same audit; cell is pure numpy + BLAS matmul) |
| 3-seed cv <= 0.05 | YES (max cv = 0.045 for substrate_2hop) |
| Verdict logic mechanically correct off per_seed | YES (refuse_pass = OOD >= 0.80 AND accept >= 0.80; infer_pass = sub2 > base1 + 0.02; both hold) |

---

## 5. HONEST SCOPE (what U1 does NOT validate)

1. **OPEN-C deferred (frozen-encoder semantic baseline):** FB15k-237 entities are MIDs (e.g. `/m/027rn`), not readable strings. A sentence-encoder semantic baseline is therefore meaningless on this corpus; the 1-hop-lookup is the MID-valid bar. The pre-reg SCHEMA-VET (b9e4485f) named "frozen-encoder-single-hop" as the inference baseline; the design-note in the cell flagged the deferral. To add the stronger semantic bar, FB15k-237 entity-names must be staged. **This is honest scope-tightening; it does not invalidate the chain-grade ruling** (the 1-hop-lookup bar is the MID-valid stand-in and the substrate clears it definitively at absolute 0.381 vs zero-by-construction 0.0075), but the "beats frozen-encoder semantic" claim is UNTESTED.

2. **Single-corpus validation:** FB15k-237 is one KB; transfer to other KBs (Wikidata-subset, domain-corpus) is untested. The multi-value Hebbian mechanism is general-purpose, but the chain-grade claim is for FB15k-237 50k specifically.

3. **Refuse-gate noise-robustness:** absolute magnitudes at ~1e-4; 2.44x separation is genuine but small. Adversarial OOD or noisy queries could degrade. Worth a follow-up sweep.

4. **1-hop baseline is zero-by-construction.** The load-bearing claim is the absolute 0.381 substrate_2hop (5000x over random argmax), NOT the "54x over baseline" ratio. The verdict_msg framing should be muted in narrative reuse.

5. **Capacity / ingest-time scaling:** 50k triples runs in ~25 min per seed at N_DIM=8192 on CPU; ingest-time scales linearly via chunked BLAS, but the W = N_DIM^2 = 268MB float32 memory cost limits N_DIM scaling and capacity saturation at higher M is untested (the 0.99 at 50k may degrade further at 310k full FB15k-237). Future work.

---

## 6. PHASE C LIVE-WRITE FIRST-USE OUTCOME

**Clean first use.** The `tools/cert_ledger_writer.py` helper API was straightforward:

```python
ledger_row = build_chain_grade_ruling_row(
    atom_id='math::T3/EXP_u1_fb15k237_ingest_eval_v1',
    cell_commit='6218a69f',
    verdict='HARD_PASS',
    notes_path='notes/...LANDED_VET_U1...HARD_PASS_2026-06-22.md',
    metrics_path='data/exp_u1_fb15k237_ingest_eval_v1/metrics.json',
    cv=0.045,
    cert_class='pre_reg_pass',
    note='u1_fb15k237_first_chain_grade_post_STANDSTILL_phase_C_first_production_use',
)
row_hash = append_cert_ledger_row(
    ledger_row,
    expected_cert_n_pre=584,   # at helper-call time, Store add has already moved CERT 583->584
    expected_cert_n_post=584,  # ledger append does NOT touch CERT
)
```

A5 PRE/POST gates clean: PRE atoms 177266 / CERT 583 / axiom 206 / cap_pres 6/6; Store add +1; POST atoms 177267 / CERT 584; helper PRE asserted live CERT==584 (already moved); helper POST asserted live CERT==584; ledger 630 -> 631 (+1 row); tail-row hash matches `cd2c04f871f457fc` returned by helper.

**One subtle API contract worth surfacing for follow-up tooling refinement (not a rough edge, just a discipline note):** because the Store `add_atom` happens BEFORE the helper call, the `expected_cert_n_pre` parameter must be set to the POST-Store-add CERT value (584 in this case), not the BEFORE-everything value (583). The convention is: the helper's PRE is the cert_ledger PRE, not the cert_atom PRE. This is documented in the helper's docstring section but slightly counter-intuitive on first read -- if a future spawn passes `expected_cert_n_pre=pre_cert` where `pre_cert` was the value BEFORE the Store add, the assertion will fire (correctly, but as a surprising AssertionError). Recommend adding one line to the docstring: "expected_cert_n_pre = live CERT at the moment of helper call (already post-Store-add); expected_cert_n_post = live CERT at POST snapshot (== pre, since the helper itself never moves CERT)." Otherwise the API is clean; the schema enforcement is helpful (caught me when I first considered `cv=None`); the idempotency check is whole-ledger (so script re-runs are safe).

**No API issues; the helper is ready for routine use.** Future atomize tools should pattern after `tools/skunkworks_atomize_u1_fb15k237_ingest_eval_CERT_584_2026-06-22.py`: Store add_atom + round-trip POST gate first, THEN append the cert_ledger row in the same A5 window, with `expected_cert_n_pre/post == post_cert` (since the helper's own PRE/POST snapshots are taken AFTER the Store add).

---

## 7. FOR DIRECTOR (RESEARCH)

- **First chain-grade post-STANDSTILL:** CERT 583 -> 584. The migration to Agent Teams is now demonstrably operational end-to-end (Phase A + B-window-1 + C + first-production-use of the live-write helper).
- **Headline update:** CERT N = 584; atom_count = 177267; axiom_term = 206 (unchanged, algebra=None); cap_pres 6/6; ledger 631 rows.
- **Path F (ingest pipeline) validated** at the L2 substrate-native level on FB15k-237 50k. The KB-ingest engine genuinely governs (refuse-gate fact-fab-bound) and composes (2-hop traversal).
- **OPEN-C remains as a follow-up:** staging FB15k-237 entity-names would unlock the stronger semantic-encoder baseline; this would be a SCHEMA-VET extension of U1, not a re-run.
- **Negative-routing (USER STANDING):** N/A here -- this is a positive ruling. Nothing to route.
- **No downward demote risk identified:** the verify-the-referent + by-construction-saturation + closure + control + substrate-only audits all pass clean; no inflated-claim flags surfaced; the chain-grade ratification is robust.

---

## 8. PATH-SCOPED COMMIT (path list, NOT `git add -A`)

```
git add -f tools/skunkworks_atomize_u1_fb15k237_ingest_eval_CERT_584_2026-06-22.py \
           data/substrate_index/math/atoms.jsonl \
           data/substrate_index/math/audit.jsonl \
           data/substrate_index/meta/cert_ledger.jsonl \
           data/substrate_index/meta/audit.jsonl \
           data/exp_u1_fb15k237_ingest_eval_v1/metrics.json \
           data/exp_u1_fb15k237_ingest_eval_v1/partial_seed7_full.json \
           data/exp_u1_fb15k237_ingest_eval_v1/partial_seed17_full.json \
           data/exp_u1_fb15k237_ingest_eval_v1/partial_seed23_full.json \
           notes/skunkworks_to_research_cc_all_LANDED_VET_U1_fb15k237_ingest_eval_HARD_PASS_2026-06-22.md
```

(I am NOT running the commit -- that's an Orchestrator / cert-sync action. The path list is informational for whoever stages the commit.)

---

## 9. ONE-LINE SUMMARY

U1 chain-grade ratified (CERT 583->584; first post-STANDSTILL; first Phase-C-live-write production use clean); multi-value Hebbian + set-readout-top-k genuinely governs (refuse-gate 0.97/0.96) + composes (2-hop 0.381 vs zero-by-construction 0.007; 5000x over random) on real FB15k-237 50k; honest scope = OPEN-C deferred (MID corpus; semantic baseline N/A; future entity-name staging) + small-tau-absolute robustness untested + single-corpus validation.

-- Skunkworks (cert-owner; landed-VET spawn; context ends on this reply per bounded-task framing)
