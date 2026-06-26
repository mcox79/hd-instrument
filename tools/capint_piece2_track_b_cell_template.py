#!/usr/bin/env python3
"""Cap-int Piece 2: Track-B pull-up cell-build TEMPLATE.

Pattern for re-running a non-cert experiment to cert-grade rigor.

PROTOCOL (per cap-int spec + the 5 binding rigor rules):

1. INPUT (from Track-B queue):
   - original_atom_id: the MIDDLE_BAND / MEASURED_MECHANISM / smoke EXP atom
   - cert_gap_diagnostic: list of what's missing for cert-grade (from enumerator)
   - capability_candidate: which capability this re-run would integrate into
   - proven_bound_hypothesis: the honest-scoped bound being tested

2. CERT-GAP CLOSE (the re-run cell):
   - PRE-REGISTERED BANDS (HARD_PASS / MIDDLE_BAND / HARD_FAIL) -- committed
     to git BEFORE dispatch (per pre-dispatch 7-checklist)
   - n_seeds >= 5 (per substrate convention; more if variance high)
   - HELD-OUT TEST (no leakage) -- the actual held-out set spec
   - DISCRIMINATING-REGIME guard (Skunkworks AUDIT_degenerate_regime_*; ensure
     the test can fail honestly, not trivially pass)
   - run_mode=full (NOT smoke; the run_mode=smoke false-green tell-tale was the
     7-checklist's load-bearing catch)
   - commit_hash + substrate_id_hash RECORDED at run-time (per A2 v6 lesson
     about corpus-provenance; substrate_id_hash a HARDENING item per Skunkworks)
   - 6th-checklist: checkpoint + resume + kill-restart-test (if runtime > ~10min
     OR N>1 units; mandatory)
   - GPU exercise check (per 7th-checklist USER-caught 2026-06-18; cell must
     EXERCISE GPU OR route to cpu_queue)
   - GATE-0 self-check (producer-attest + consumer-enforce per cert-architecture)

3. ATOMIZE (the verdict-driven atom add):
   - kind: experiment_record
   - tier + pq: BANDS-DRIVEN (HARD_PASS -> CERT_CHAIN_GRADE; MIDDLE -> MIDDLE_BAND;
     HARD_FAIL -> HARD_FAIL_no_cert; the cert-engine assigns)
   - metadata.key_metrics: structured {metric_name -> value} (NOT description hints)
   - metadata.prereg_bands: from the committed pre-reg
   - metadata.cell_commit: git commit hash at run-time
   - metadata.substrate_id_hash: hash of the bge_atom_set used (per A2 v6 lesson)
   - metadata.discrimination_self_check: {pass: bool, details: ...}
   - metadata.gate0_self_check: {pass: bool, n_cells, elapsed, ...}
   - metadata.a2_set_validity_vet: if A2-family
   - metadata.verdict: PASS / MIDDLE_BAND / HARD_FAIL
   - cross-refs: composes_with the original_atom_id (the pull-up record)

4. VERDICT VET (Skunkworks lane):
   - Verify key_metrics MATCH headlines (verify-the-referent at data layer)
   - Verify discrimination non-degenerate (real classes; spread; not bar-as-perf)
   - Verify run integrity (run_mode=full; metrics_source=measured; gate0_pass)
   - Verify A2-set-validity if A2-family
   - Verify band MET (per pre-reg)
   - Verify cell_commit + substrate_id_hash present
   - Verdict: CERT_CHAIN_GRADE / MIDDLE_BAND / HARD_FAIL_no_cert
   - If PASS at CERT_CHAIN_GRADE -> integrate via Track A (capability metadata
     -> current_best = this EXP atom)
   - If MIDDLE / FAIL -> honest-stays-below-cert (the truth-test working)

5. ROUTING:
   - Cell-build (this template): Director-side (you).
   - Pre-dispatch SCHEMA-VET (7-checklist + atom-add-mechanism + bands-pre-reg
     + 6th-checklist if long): Skunkworks.
   - Dispatch: Orchestrator.
   - Verdict atomize: Exp-Dev (proven pattern; new atom-add).
   - Verdict VET (band check + integrate or honest-down): Skunkworks.

TEMPLATE: this file is a PATTERN, not a runnable cell. Each Track-B cell-build
copies/adapts it for the specific original_atom_id + cert_gap_diagnostic.

PRIORITY ORDER (from Piece-1 enumerator):
- 5 MEASURED_MECHANISM (closest-to-cert; minimal-gap pull-ups; ~1h each)
- 541 MIDDLE_BAND (re-run with stricter bands / held-out / discriminating-regime)
- 475 HARD_FAIL (honest-negatives; many will stay below cert; some have fixable
  gaps like wrong-bands or degenerate-regime)
- 1148 PASS-but-non-cert (likely smoke or pre-cert-arc; need 7-checklist
  conformance + structured metrics + pre-reg bands)
- ~981 other (varies)

DOMAIN-VALUE-first per USER default: reasoning_multihop first, then
cognitive_capacity, then retrieval, then NLP_language + math + architecture +
refuse_gate (with closest-to-cert tiebreaker within domain).

ENCODER DISCIPLINE (Path C; META_substrate_product_inference_uses_substrate_native_encoder_only):
- DEFAULT encoder for substrate-product inference = substrate-native (random sparse-bipolar
  codebook, FPE phasor, random codebook, k-WTA, char-trigram). NEVER labels-at-basis.
- LLM encoders (Pythia, MiniLM, BGE, Llama, word2vec, sentence-transformers, etc.) are
  DIAGNOSTIC PROBES ONLY at setup time and MUST NOT sit in the substrate-product
  inference path.
- Track-B pull-up cells inherit the encoder family of the ORIGINAL_ATOM_ID; if the
  original used an LLM encoder, the pull-up must EITHER stay scoped as
  DEPLOYMENT_CONTEXT / LLM_AUGMENTATION (subordinate cert-tier) OR commission a
  parallel substrate-native re-validation cell (cf. testbed encoder-provenance audit
  2026-06-26 Section 2B).
- Set ENCODER_PROVENANCE constant below; emit in metrics; default = SUBSTRATE_NATIVE.
"""

# Template constants -- each cell-build sets these
ORIGINAL_ATOM_ID = "<set per pull-up; from Piece-1 Track-B queue>"
CERT_GAP_DIAGNOSTIC = [
    # "structured_key_metrics: absent",
    # "pre-registered_bands: absent",
    # "n_seeds_recorded: absent",
    # ...
]
CAPABILITY_CANDIDATE = "<set per pull-up; the capability this would integrate into>"
PROVEN_BOUND_HYPOTHESIS = "<set per pull-up; the honest-scoped bound to test>"

# Pre-registered bands (COMMIT TO GIT BEFORE DISPATCH; per 7-checklist)
PREREG_BANDS = {
    # Example structure (tune per metric):
    # "HARD_PASS": {"AUROC": 0.90, "f1": 0.80, "recall_at_k": 0.85},
    # "MIDDLE_BAND": {"AUROC": 0.70},
    # "HARD_FAIL": {"AUROC": 0.55},  # explicit below-band threshold
}

N_SEEDS = 5  # >= 5 per substrate convention
RUN_MODE_DEFAULT = "full"  # NEVER smoke for a cert-grade cell

# Encoder provenance: default substrate-native. If using LLM-derived features at
# inference, set to one of: DEPLOYMENT_CONTEXT_LLM_KEYS | DEPLOYMENT_CONTEXT_LLM_RESIDUALS
# | LLM_AUGMENTATION | LLM_DIAGNOSTIC_PROBE | MIXED_LLM_AND_SUBSTRATE |
# LLM_INGEST_ONLY_SUBSTRATE_AT_INFERENCE -- and document the justification in the
# cell docstring per the Path C discipline (testbed encoder-provenance audit 2026-06-26).
ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"


def hypothesis_card():
    """Required: state the hypothesis + pre-registered bands.
    Per cap-int cert-emphasis: the headline must EQUAL the proven-bound.
    """
    return {
        "original_atom_id": ORIGINAL_ATOM_ID,
        "capability": CAPABILITY_CANDIDATE,
        "proven_bound_hypothesis": PROVEN_BOUND_HYPOTHESIS,
        "headline_equals_bound_self_check": True,  # cert-emphasis discipline
        "prereg_bands": PREREG_BANDS,
        "n_seeds": N_SEEDS,
        "run_mode": RUN_MODE_DEFAULT,
        "cert_gap_close": CERT_GAP_DIAGNOSTIC,
    }


def gate_0_self_check(n_cells_run, elapsed, run_mode):
    """Producer-attest: was this a real run, not smoke?
    Tell-tale: smoke runs finish in seconds; full runs take time.
    """
    is_smoke = (run_mode == "smoke" or elapsed < 1.0 or n_cells_run < 5)
    return {
        "pass": not is_smoke,
        "is_smoke": is_smoke,
        "n_cells": n_cells_run,
        "elapsed": elapsed,
        "run_mode": run_mode,
    }


def discrimination_self_check(predictions, labels):
    """Self-check: discriminating-regime non-degenerate.
    Both classes present? Spread? Not bar-as-perf?
    """
    n_pos = sum(1 for l in labels if l == 1)
    n_neg = sum(1 for l in labels if l == 0)
    if n_pos == 0 or n_neg == 0:
        return {"discriminates": False, "reason": "single-class"}
    pred_spread = max(predictions) - min(predictions)
    if pred_spread < 0.05:
        return {"discriminates": False, "reason": "no-spread"}
    return {
        "discriminates": True,
        "n_pos": n_pos,
        "n_neg": n_neg,
        "pred_spread": pred_spread,
    }


def record_provenance():
    """Required per A2 v6 lesson: cell_commit + substrate_id_hash.
    Run BEFORE the experiment so the corpus is git-pinned at run-time.
    """
    import subprocess
    cell_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"]).decode().strip()
    # substrate_id_hash: hash of the bge_atom_set used; cell-specific
    substrate_id_hash = "<compute per cell; cache-content-hash>"
    return {"cell_commit": cell_commit,
            "substrate_id_hash": substrate_id_hash}


def checkpoint_step(state, step_idx, total_steps):
    """6th-checklist: checkpoint + resume + kill-restart-test.
    Required if runtime > ~10min OR N>1 units.
    """
    import json as _json
    from pathlib import Path as _Path
    checkpoint_path = _Path(f"data/checkpoints/cell_{ORIGINAL_ATOM_ID}/step_{step_idx}.json")
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    with checkpoint_path.open("w") as f:
        _json.dump({"step_idx": step_idx, "total_steps": total_steps,
                    "state": state}, f)


def resume_from_checkpoint():
    """Resume from last completed checkpoint. Returns (step_idx, state) or
    (0, None) if no checkpoint."""
    from pathlib import Path as _Path
    import json as _json
    checkpoint_dir = _Path(f"data/checkpoints/cell_{ORIGINAL_ATOM_ID}")
    if not checkpoint_dir.exists():
        return (0, None)
    checkpoints = sorted(checkpoint_dir.glob("step_*.json"),
                         key=lambda p: int(p.stem.split("_")[1]))
    if not checkpoints:
        return (0, None)
    with checkpoints[-1].open() as f:
        data = _json.load(f)
    return (data["step_idx"] + 1, data["state"])


def emit_verdict_atom(verdict, key_metrics, gate0, discrimination,
                      provenance, n_seeds):
    """Emit the verdict EXPERIMENT_RECORD per the cap-int discipline."""
    return {
        "kind": "experiment_record",
        "id": f"EXP_pullup_{ORIGINAL_ATOM_ID}_v1",
        "name": f"Pull-up re-run of {ORIGINAL_ATOM_ID} (Track-B)",
        "description": f"Cap-int Track-B pull-up. "
                       f"Proven-bound hypothesis: {PROVEN_BOUND_HYPOTHESIS}. "
                       f"Verdict: {verdict}.",
        "metadata": {
            "verdict": verdict,
            "key_metrics": key_metrics,
            "prereg_bands": PREREG_BANDS,
            "cell_commit": provenance["cell_commit"],
            "substrate_id_hash": provenance["substrate_id_hash"],
            "gate0_self_check": gate0,
            "discrimination_self_check": discrimination,
            "n_seeds": n_seeds,
            "run_mode": RUN_MODE_DEFAULT,
            "metrics_source": "measured",
            "encoder_provenance": ENCODER_PROVENANCE,
            "capint_track_b_pull_up": True,
            "original_experiment": ORIGINAL_ATOM_ID,
            "capability_candidate": CAPABILITY_CANDIDATE,
            "composes_with": [ORIGINAL_ATOM_ID],
        },
    }


# This template is a PATTERN. Actual cells are AUTHORED per Track-B row at
# pull-up time; the template's helpers are imported/adapted.

if __name__ == "__main__":
    print(__doc__)
    print()
    print("Hypothesis card (template; fill in per pull-up):")
    import json
    print(json.dumps(hypothesis_card(), indent=2, default=str))
