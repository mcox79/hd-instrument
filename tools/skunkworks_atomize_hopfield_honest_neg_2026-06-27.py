"""A5-gated atomization: Hopfield family honest-negative + 2 META_RULE_CANDIDATEs.

Created by skunkworks landed-VET 2026-06-27 after verify-off-data on
exp_gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1.

Independent recompute reproduced mean_true_cos=0.17840531468391418 to 8 decimals.
Confirmed: BASELINE_HEBBIAN and HEBBIAN_SLOW arms are mathematically IDENTICAL under
L2-normalized cosine readout (rows differ only by per-class scalar). The arms_range=0.000
finding is GENUINE regime saturation, not a cell bug or measurement artifact.
"""
import json
import os
from pathlib import Path

REPO = Path("d:/AI/hd-instrument")
META_DIR = REPO / "data" / "substrate_index" / "meta"
META_ATOMS = META_DIR / "atoms.jsonl"

# Load existing atom IDs for collision avoidance
existing_ids = set()
with open(META_ATOMS, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            try:
                existing_ids.add(json.loads(line).get("atom_id"))
            except Exception:
                pass
print("Existing meta atoms:", len(existing_ids))

ts = "2026-06-27T22:30:00Z"

finding_atom = {
    "atom_id": "META_FINDING_hopfield_consolidation_family_honest_neg_at_substrate_regime_v1",
    "atom_type": "META_FINDING",
    "corpus": "meta",
    "created_ts": ts,
    "created_by": "skunkworks_landed_vet_2026-06-27",
    "cert_tier": "HONEST_NEGATIVE_VERIFIED",
    "evidence": {
        "cell": "exp_gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1",
        "metrics_path": "data/exp_gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1_smoke/metrics.json",
        "verdict": "HARD_FAIL",
        "verdict_msg": "REGIME_SATURATION: all arms > 0.95 at fair readout; BASE=1.000 HEB=1.000 HOP=1.000 GEN=1.000 | arms_range=0.000",
        "config": "N_DIM=2048 N_CAT=100 N_TRAIN=100 proto_noise=0.60 alpha=0.0488 seed=11",
        "drill_source": "notes/research_drill_2x_hopfield_consolidation_revival_2026-06-27.md",
        "independent_recompute_match": "mean_true_cos=0.17840531468391418 reproduced to 8 decimals",
    },
    "finding": (
        "At the substrate regime (alpha=0.05, N_TRAIN=100 instances per class, proto_noise=0.60), "
        "NREM-style Hopfield replay (stored OR generative) adds ZERO discriminable signal over "
        "simple Hebbian-mean schema construction. All four arms tie at heldout_acc=1.000 when read "
        "via shared fair W-cosine readout. This is NOT a surface-mismatch artifact (the original v2 "
        "bug hypothesis was wrong); it is GENUINE regime saturation: 100 noisy instances per class "
        "at alpha=0.05 already provide enough signal that any hebbian-style W achieves perfect "
        "heldout accuracy, leaving replay nothing to add."
    ),
    "boundary": (
        "Hopfield family is NOT proven impossible substrate-wide. The negative is BOUNDED to "
        "regimes where baseline already saturates. Discriminating regimes would require either "
        "(a) few samples per class (N_TRAIN ~ 1-10) where replay-as-consolidation matters, OR "
        "(b) high catastrophic-interference load (N_CAT >> N_DIM/4) where W capacity is exceeded. "
        "Selective-subset mechanisms (BTSP / STC / engram-dropout / cyclic-eta / memristive / 3-tier-W) "
        "should be the pivot because they have different failure modes (NOT reduces-to-prototype-mean)."
    ),
    "closes": "Hopfield consolidation family at substrate-current-regime",
    "does_not_close": "Hopfield family at sample-scarce or high-load regimes (future scope)",
    "recommendation": "Director decision to NOT ship Hopfield-v3 is CONFIRMED. Pivot to Battery-2 selective-subset mechanisms.",
}

rule_atom = {
    "atom_id": "META_RULE_CANDIDATE_by_construction_arm_equivalence_under_l2_normalized_readout_v1",
    "atom_type": "META_RULE_CANDIDATE",
    "corpus": "meta",
    "created_ts": ts,
    "created_by": "skunkworks_landed_vet_2026-06-27",
    "cert_tier": "METHODOLOGY_DISCIPLINE",
    "rule": (
        "When two arms differ ONLY by a per-row scalar in their W construction "
        "(e.g., W_A[c] = c_scalar * W_B[c]), and the shared readout is L2-row-normalized cosine, "
        "the two arms are MATHEMATICALLY IDENTICAL — their heldout_acc and per-coord cosines MUST "
        "agree to floating-point precision. In the diagnostic, ARM_BASELINE_HEBBIAN (mean) and "
        "ARM_HEBBIAN_SLOW (sum) differ only by per-class N_TRAIN scalar; they reported "
        "mean_true_cos=0.17840531468391418 to ALL 16 decimal places — this is an arithmetic identity, "
        "not evidence."
    ),
    "discipline_directive": (
        "SCHEMA-VET pre-reg check: when two arms exist that differ only by per-row scaling, AND the "
        "readout is L2-normalized, FLAG them as not-independent-evidence. The cell can keep them as "
        "sanity checks but they do NOT contribute discriminator power. For the diagnostic this caused "
        "NO false claim (arms_range=0.000 was correctly noted), but a future cell author could "
        "over-claim 'N arms agree' when in fact 2 of those N arms were structurally identical."
    ),
    "evidence_cell": "exp_gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1",
    "related_to": ["META_RULE_AA_fair_diagnostic_shared_readout", "fix28_per_arm_metrics"],
}

n1_rule_atom = {
    "atom_id": "META_RULE_CANDIDATE_n1_fair_diagnostic_can_close_family_if_discriminator_structural_v1",
    "atom_type": "META_RULE_CANDIDATE",
    "corpus": "meta",
    "created_ts": ts,
    "created_by": "skunkworks_landed_vet_2026-06-27",
    "cert_tier": "METHODOLOGY_DISCIPLINE",
    "rule": (
        "An n=1 seed diagnostic CAN justify closing a mechanism family IF the discriminator is "
        "STRUCTURAL (arms-must-differ-by-X-if-hypothesis-true), not statistical (mean-must-shift-by-Y "
        "across seeds). Structural failure means: even one well-constructed seed produces "
        "arms_range=0.000 when the hypothesis required arms_range >= threshold. Adding more seeds "
        "would not change the structural conclusion because the mechanism is mathematically "
        "degenerate at this regime."
    ),
    "qualification": (
        "This rule applies ONLY when (a) the discriminator is structural (e.g., capacity saturation, "
        "identical-under-normalization, gradient-vanishing), (b) the cell author can articulate WHY "
        "adding seeds would not change the result, and (c) the boundary statement does not "
        "over-generalize beyond the tested regime."
    ),
    "evidence_cell": "exp_gap3_cls_HOPFIELD_v2_surface_mismatch_audit_diagnostic_v1",
    "related_to": ["META_RULE_H_cardinality_ok", "feedback_discriminator_must_survive_scale"],
}

# A5: collision check
for atom in [finding_atom, rule_atom, n1_rule_atom]:
    if atom["atom_id"] in existing_ids:
        print("COLLISION:", atom["atom_id"], "already exists; SKIPPING this atomize")
        raise SystemExit(1)

# Atomic write: read existing, append new, write to tmp, os.replace
tmp_path = META_ATOMS.with_suffix(".jsonl.tmp_skunk_" + str(os.getpid()))
with open(META_ATOMS, "r", encoding="utf-8") as f:
    existing_content = f.read()

with open(tmp_path, "w", encoding="utf-8") as f:
    f.write(existing_content)
    if existing_content and not existing_content.endswith("\n"):
        f.write("\n")
    for atom in [finding_atom, rule_atom, n1_rule_atom]:
        f.write(json.dumps(atom) + "\n")

os.replace(tmp_path, META_ATOMS)

# Verify-load: reload + check atom IDs present
loaded_ids = set()
with open(META_ATOMS, "r", encoding="utf-8") as f:
    for line in f:
        if line.strip():
            try:
                loaded_ids.add(json.loads(line).get("atom_id"))
            except Exception as e:
                print("VERIFY-LOAD FAIL: bad line:", e)
                raise

for atom in [finding_atom, rule_atom, n1_rule_atom]:
    if atom["atom_id"] not in loaded_ids:
        print("VERIFY-LOAD FAIL:", atom["atom_id"], "not present after write")
        raise SystemExit(1)

print("A5 ATOMIZATION SUCCESS:", len(loaded_ids), "atoms in meta corpus (was", len(existing_ids), "; added 3)")
print("Atoms written:")
for atom in [finding_atom, rule_atom, n1_rule_atom]:
    print(" ", atom["atom_id"])
