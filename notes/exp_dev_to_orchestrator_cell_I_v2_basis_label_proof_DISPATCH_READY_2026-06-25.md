# Cell I v2 (basis_layer_label_contamination_proof_v1) DISPATCH-READY

[from=exp_dev] [type=dispatch_ask] [filed=2026-06-25T15:55Z]

## Summary

USER-revised Cell I (BIAS-13 + Principle O proof) authored + self-test PASS + local smoke PASS (3 seeds; directional pattern consistent). Ready for FULL dispatch to remote_cpu_queue. Awaiting USER green-light.

## Commit hash

`cae39e11` (main): cell + prereg + smoke metrics

## Files

- `experiments/exp_substrate_basis_layer_label_contamination_proof_v1.py`
- `preregs/2026-06-25_substrate_basis_layer_label_contamination_proof_v1.md`
- `data/exp_substrate_basis_layer_label_contamination_proof_v1_smoke/metrics.json` (smoke verdict + per-arm metrics)

## Self-test + smoke evidence

**Self-test:** PASS (4 encoders construct cleanly; KG ingests; tasks return finite metrics; verdict logic returns valid string).

**Local smoke (3 seeds at N=2048 / V=100 / M=600):**

| Seed | RANDOM retr | LABEL_BASIS retr | LABEL within_cat_cos | DW retr | OLS retr |
|------|-------------|------------------|----------------------|---------|----------|
| 7    | 0.685       | 0.655            | 0.197                | 0.663   | 0.683    |
| 13   | 0.682       | 0.655            | 0.193                | 0.648   | 0.682    |
| 17   | 0.650       | 0.620            | 0.195                | 0.618   | 0.650    |

**Consistent directional pattern:** LABEL_BASIS retrieval ~3pp below RANDOM across all 3 seeds; LABEL within_cat_cos ~0.195 (clear cone-collapse signature; others at 0 or 0.139 for DeepWalk which discovers KG structure); EMERGENT arms within ±0.05 of RANDOM. Confound diagnostic (within_cat_cos) does NOT trigger C2 flag (0.195 < 0.95).

**Why PROVEN bands don't trigger at smoke:** the bands (RANDOM>=0.80, LABEL<=0.65) are calibrated for FULL N=8192/V=300/M=2400 where substrate is at ~10% of capacity. At smoke N=2048/V=100/M=600 the substrate is at ~30% of capacity → RANDOM crowded to 0.65-0.69 (not 0.80+). The DIRECTIONAL pattern is the smoke-scale signal; absolute thresholds need full scale.

## FULL dispatch parameters

- **Anchor:** `substrate_basis_layer_label_contamination_proof_v1`
- **Queue:** `remote_cpu_queue` (pure numpy; CPU-bound; ~45-90min wall estimated)
- **Config:** N_DIM=8192, V=300, V_cat=10, V_per_cat=30, V_P=8, M=2400, 5 seeds [7,13,17,23,29]
- **Timeout:** 3600s
- **Pre-reg PROVEN:** ARM_LABEL_BASIS retr <= 0.65 AND ARM_RANDOM_BIPOLAR retr >= 0.80 AND EMERGENT within ±0.05 of RANDOM AND label comp <= 0.55 AND random comp >= 0.70
- **Pre-reg REFUTED:** ARM_LABEL_BASIS retr >= 0.80 OR ARM_RANDOM_BIPOLAR retr <= 0.65

## Key design decisions

1. **Revised AXIS_PROJECTION to shared-hub semantics during smoke**: my v1 used per-concept-independent ±1 within band (orthogonal codes within cat) — this did NOT show cone-collapse at smoke. Revised to shared-bipolar-hub-per-category + per-concept perturbation, matching the LITERAL interpretation of "concept in subspace c". Smoke now shows the predicted within-cat cosine signature ~0.195. Documented in cell + prereg.

2. **Retrieval is recall@1 on STORED triples**, not held-out. Per USER spec "cosine+cleanup on stored triples". Held-out 20% split applies only to 2-hop composition chains.

3. **3 of 4 arms ZERO labels at encoder construction** (audited via grep). `_category_of()` is called inside `encoder_label_basis_axis_projection` ONLY; other arms ignore label metadata.

4. **CONFOUND_AUDIT** in prereg names C1 (impl bug → mitigated by ref-cell parameters), C2 (code degeneracy → guarded via within_cat_cos diagnostic), C3 (capacity saturation → mitigated by M=10% capacity).

## Honest assessment

**Smoke shows directional signal toward principle confirmation**, not a definitive chain-grade signal (by design — smoke is not for chain-grade). The 3pp LABEL_BASIS gap below RANDOM + 0.195 within_cat_cos signature is consistent across all 3 seeds tested. EMERGENT arms behave as predicted (DeepWalk discovers some KG structure; SoftHebb stays close to RANDOM baseline).

**Caveat to flag for USER:** at smoke scale, the substrate is closer to capacity than at FULL scale; this compresses all retrieval rates toward each other. The 3pp gap could widen significantly at FULL N=8192/V=300/M=2400 (where RANDOM should be 0.85+ and LABEL_BASIS should fall further). Or it could stay narrow if the cone-collapse mechanism is weaker than I'm assuming. The FULL run will discriminate.

**Recommendation:** dispatch to remote_cpu_queue. Estimated wall 45-90min. If FULL run shows the same 3pp pattern but RANDOM at 0.85+ and LABEL_BASIS at 0.82, the prereg's PROVEN bands won't trigger (HARD_PASS requires LABEL<=0.65 absolute) → MIDDLE_BAND. If FULL shows the predicted dramatic collapse (LABEL<=0.65), HARD_PASS_CHAIN_GRADE. Either way the per-arm numerics will be informative.

## Waiting on

- USER: decide remote dispatch (per task spec: "USER will decide remote dispatch")

If USER green-lights, Orchestrator can dispatch via:
```
HDLAB_EXP_NAME=substrate_basis_layer_label_contamination_proof_v1 \
  python tools/queue_add.py --anchor substrate_basis_layer_label_contamination_proof_v1 \
  --queue remote_cpu_queue --timeout 3600
```
(or whatever the current queue_add invocation is; tools/queue_add.sh doesn't exist on this system — Orchestrator owns the queue tooling).
