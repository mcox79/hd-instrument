# Tier Ruling: Consolidation v3 HELDOUT_FIX — HARD_FAIL (mechanism-refuted; Barrier 1 not closed)

Date: 2026-06-25
Cell: `exp_substrate_multihop_consolidation_v3_proper_test_HELDOUT_FIX`
Cert-owner: Skunkworks (audit-only)
Method: independent recompute off `metrics.json` per-seed per-arm; substrate-mine of v1 + v2 priors.

## Tier: HARD_FAIL (mechanism-refuted, NOT sanity-rail-induced)

### Independent recompute confirms reported per-arm numbers exactly

Per-seed HELDOUT_OVERALL (seeds 7 / 17 / 23 / mean):
- NAIVE 2hop: 0.845 / 0.905 / 0.800 / **0.850**
- CONSOL K=1: 0.020 / 0.000 / 0.000 / **0.007**
- CONSOL K=3: 0.120 / 0.100 / 0.100 / **0.107**
- CONSOL K=10: 0.120 / 0.100 / 0.100 / **0.107**
- CONSOL K=50: 0.400 / 0.400 / 0.400 / **0.400**
- HYBRID K=3+cleanup: 0.120 / 0.100 / 0.100 / **0.107**

`consol_held_max - naive = 0.40 - 0.85 = -0.45` → consolidation underperforms naive by 45 pp on heldout. The verdict_msg framing of "no generalization" is correct.

## The smoking gun (Fix #28 — per-arm per-class, not summary)

Per-class HELDOUT broken out reveals the mechanism is not failing randomly — it is failing **deterministically wherever it is applied** (mean across seeds):

| arm | HIGH consolidated? | HIGH held | MID consol? | MID held | LOW consol? | LOW held |
|---|---|---|---|---|---|---|
| K=1 | YES | **0.000** | YES | **0.022** | YES | **0.000** |
| K=3 | YES | **0.000** | YES | **0.022** | NO  | **1.000** |
| K=10 | YES | **0.000** | YES | **0.022** | NO  | **1.000** |
| K=50 | YES | **0.000** | NO  | **1.000** | NO  | **1.000** |

**Pattern (perfect 3/3 seeds across all arms): a class consolidated → ~0% heldout. A class NOT consolidated → 100% heldout (matching the naive 2-hop path).**

The K=50 "highest" 0.40 score is not consolidation working better — it is the average of (1 destroyed HIGH class at 0% × weight 30/50) + (2 untouched naive classes at 100% × weight 20/50) = 0.40. The K=50 arm wins by **doing the consolidation primitive less**.

This makes the consolidation primitive HARD_FAIL not as "didn't help" but as "actively replaces a 100%-correct retrieval path with a near-0% one." Mechanism is refuted, not undersized.

## Concerns addressed

### Concern 1: NAIVE 0.85 ∉ [0.62, 0.68] — does the rail miss invalidate the comparison?

**No.** The NAIVE arm uses a separate single-class chain set (DESIGN_NOTE confirms: "NAIVE arm uses SEPARATE single-class chain set (beta-sweep apples-to-apples regime; W is its own)"). The 0.65 band was calibrated to the v1/beta-sweep regime; v3 changed V_C=600 and predicate structure so 2-hop is genuinely easier in this regime. The naive sanity rail is **mis-calibrated for v3**, not the cell broken. The comparison NAIVE-vs-CONSOL remains valid because both run on the same substrate / N=8192 / V_C=600 — only the chain-class structure differs. Even setting NAIVE arbitrarily to 0.65 in your head, CONSOL_K50=0.40 still underperforms by 25 pp on heldout.

### Concern 2: K_THRESH gating spread = 0.006 — does the second rail miss invalidate?

**No, it confirms the mechanism failure.** The gating rail expected TRAINING spread ≥ 0.10 across K-thresholds. Observed: all K-arms hit 1.000 training because the consolidator memorizes whatever it touches. The non-discrimination on training is what proves K-thresh is doing what it was designed to do (gate which classes get the operator applied) — but the OPERATOR ITSELF then destroys heldout generalization. The rail asked the wrong question; the per-class breakdown answers the right one.

### Concern 3: Is the 0.40 (K=50) vs 0.10 (K=3) "partial signal" meaningful?

**No.** Per the smoking-gun table above, K=50 is mechanically (1 destroyed class + 2 untouched naive paths)/3 ≈ 0.40, and K=3 is (2 destroyed + 1 untouched)/3 ≈ 0.34 weighted as 0.107 by per-class query counts. There is no graded "consolidation improves with higher K" — there is only "fewer classes touched → naive paths survive." 0/3 seeds show any positive consolidation lift on any consolidated class. The "signal" is the absence of consolidation, not its presence.

## Substrate-mine context (v1 → v2 → v3)

- **v1 (`exp_substrate_multihop_consolidation_memory_v1`)**: HARD_PASS at CONS_IMMEDIATE=1.000 but with HOP2_ORACLE_LOW rail miss. The 1.000 was perfect-by-construction (the consolidator was queried on data it had just stored; this is closure on training distribution, not generalization).
- **v2 (`exp_substrate_multihop_consolidation_v2_proper_test`)**: MIDDLE_BAND_HELDOUT with `nan` heldout because `make_two_hop_chains` exhausted `V_C` before generating heldout (DESIGN_NOTE bug acknowledgment).
- **v3 (this cell)**: heldout finally measured cleanly → 0.107 best. **Trajectory: v1 perfect-by-construction → v2 unmeasurable → v3 clean refutation.**

This is not "third re-author keeps mis-matching the rail" — it is "third attempt finally measures the right thing and the answer is that the primitive doesn't generalize." v1's HARD_PASS was a by-construction-saturation false signal (substrate priority feedback 2026-06-22: "default classification = MM not chain-grade; let cert-owner tier UP"). v3 is the honest counterfactual.

## Atomization decision: YES — file as HARD_FAIL with informative-negative framing

File one experiment_record atom in `math` corpus with these load-bearing fields:

- `anchor`: substrate_multihop_consolidation_v3_proper_test_heldout_fix
- `verdict`: HARD_FAIL
- `tier`: T2 (clean negative; multi-seed; held-out generalization measured; per-class mechanism diagnosis)
- `provenance_quality`: CERT_CHAIN_GRADE (full mode, 3 seeds, partial checkpoints present)
- `era`: SUBSTRATE_BUILD
- `relevance_tier`: HIGH (this is a Barrier 1 closer; the negative is load-bearing for L2-vision pivot)
- `headline`: "HARD_FAIL: consolidation primitive destroys heldout generalization wherever applied (per-class: consolidated → 0%, unconsolidated → 100%); 0/3 seeds show positive lift; K=50 'win' is arithmetic of fewer-classes-touched. Multi-hop continual-learning via this consolidation operator REFUTED at apples-to-apples regime."

Also file one META atom in `meta` corpus capturing the discriminator that worked:

- `name`: `per_class_consolidation_breakdown_discriminator`
- `description`: "When testing a memory-consolidation primitive with class-gated application (K-threshold), the AGGREGATE heldout score is uninterpretable without per-class breakdown showing consolidated-vs-not. v3 consolidation HARD_FAIL was only diagnosable from per-class: consolidated → 0%, unconsolidated → naive baseline. Aggregate hides the mechanism."

## Implications (audit-only — Director decides)

1. **Do not re-dispatch v4 without a mechanism revision.** The primitive as currently coded (consolidator stores compound predicate; query routes to compound) fails to factor 2-hop chains in a way that survives s-disjoint heldout. A v4 cell that just tunes K-thresh or V_P is forbidden by Fix #26 (recent HARD_FAIL re-dispatch).

2. **Barrier 1 (multi-hop continual-learning) remains OPEN.** Route to Research for revival-angle drill (per USER STANDING rule): the negative is informative — the substrate CAN do 2-hop naive at 0.85; the failure is the consolidator-as-replacement-path. Revival candidates: consolidator-as-AUGMENTATION (keep naive path; add consolidated path; ensemble), or consolidator with explicit s-generalization training (currently the consolidator binds to specific s instances it has seen).

3. **Naive sanity rail needs regime-aware re-calibration.** Pre-reg the v4 sanity rail to v3's measured 0.85 ± noise band, not v1's 0.65. The rail-miss here is a methodology debt, not a substrate finding.

4. **Cert N**: +1 HARD_FAIL atom (counts toward CERT N as proven negative). Update `cert_ledger.jsonl`. No CERT subtraction.

## Verdict summary

- Tier: **HARD_FAIL** — mechanism refuted, not sanity-rail-induced. The per-class smoking-gun rules out "rail miss invalidates comparison" and rules out "by-construction-saturation hiding a real signal."
- Atomization: YES, math corpus experiment_record + meta corpus discriminator atom.
- Discipline: this is the right call EVEN IF it removes a desired Barrier 1 closer. Symmetric anti-negativity: honest downward correction at same rigor as upward (USER 2026-06-17).
