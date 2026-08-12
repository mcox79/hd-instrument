"""A5-gated SCOPE-CAVEAT amendment (NO TIER CHANGE) to compose-freq routing v5 CG atom.

Trigger: Stage-2 integration (commit 3c4d85aa) surfaced that the certified cell's
control was RAW-HEBBIAN only. That control bundles two effects: the cf-RPE delta-rule
(iterative training, n_steps>0) AND the frequency routing (two kernels W_freq/W_rare +
routed readout). Against a TIGHTER single-kernel delta-rule control (same iterative
training, no routing), routing's genuine contribution is regime-dependent.

VERIFIED OFF-DISK by Skunkworks independent recompute (this session, 2026-07-08):

  (1) Certified cell control setup (experiments/exp_substrate_compose_freq_routing_v5_DEFINITIVE.py
      ARM_CONFIGS): every BASELINE arm has n_steps=0, type=BASELINE (raw Hebbian outer
      product, build_W_hebbian_gpu). Every FREQ arm has n_steps=2000/3000, type=FREQ
      (iterative cf-RPE delta-rule + frequency routing). There is NO single-kernel
      delta-rule control (n_steps>0, no routing). CONFIRMED: the certified +0.148 BPC lift
      (FREQ_DEEPER_N8192 7.1647 vs BASELINE_N8192 7.3124) bundles delta-rule + routing.

  (2) Integration witness (verification/test_compose_freq_routing.py) isolates the tighter
      control (hdlab.compose_freq_routing.build_single_kernel = single-kernel delta-rule,
      SAME iterative training as routed, no frequency gating) and is telemetry-sensitive.
      pytest verification/test_compose_freq_routing.py: 6 passed.

  (3) Independent recompute off the witness builder (2 seeds 7,13; V=200, n_dim=128,
      n_high=15), routed vs single-kernel delta-rule vs raw-Hebbian, BY REGIME:

      HIGH-IN-DEGREE / function-word structure (hi_indeg=40, rare_indeg=1):
        seed7:  heb=7.2430 single_delta=7.1352 routed=7.0178
                routed-vs-single=+0.1174   routed-vs-heb=+0.2253
        seed13: heb=7.2487 single_delta=7.1339 routed=7.0157
                routed-vs-single=+0.1182   routed-vs-heb=+0.2331
        MEAN routed-vs-single=+0.1178   routed-vs-heb=+0.2292
        -> routing GENUINELY adds over the delta-rule (+0.118 BPC, matches the certified
           text8 regime and the lr*rho crosstalk oracle).

      GENERIC / symmetric in-degree (hi_indeg=8, rare_indeg=8):
        seed7:  heb=7.3803 single_delta=7.3146 routed=7.2920  routed-vs-single=+0.0225
        seed13: heb=7.3789 single_delta=7.3119 routed=7.2866  routed-vs-single=+0.0253
        MEAN routed-vs-single=+0.0239 (< 0.05; collapses; witness asserts <0.06)
        -> routing does NOT meaningfully add; the DELTA-RULE (single-vs-heb +0.066) carries
           the lift over raw-Hebbian. Routing advantage collapses (telemetry-sensitive).

FINDING HOLDS. The "routing" attribution in the v5 CG atom is OVER-ATTRIBUTED for generic
regimes: what beats raw-Hebbian there is the cf-RPE delta-rule, not the routing. Routing's
genuine, isolable contribution is confined to the HIGH-IN-DEGREE / function-word regime
(high-frequency targets are successors of many contexts). The certified text8 corpus IS
high-in-degree (natural-language Zipfian function-word structure), so the certified lift is
real and the CG stands for its certified regime.

DISPOSITION: SCOPE-SHARPENING, NOT REFUTATION. Tier stays CHAIN_GRADE_DEFINITIVE.
cert_increment_delta = 0 (no CERT-N change). Amendment record links the original atom;
original NOT superseded, NOT demoted. Symmetric anti-negativity: the CG is preserved (we do
not over-correct downward), the attribution is sharpened (we do not let the bundled control
overstate what routing alone buys).

Discipline invariants (per hdi_skunkworks.md):
  - Atomic tmp-write + os.replace + verify-load on atoms.jsonl AND cert_ledger.jsonl
  - Matching timestamps between atom + ledger entries; verified_off_data=True
  - amendment_record convention (kind='amendment_record', no_tier_change, amends referent)
  - Cross-arc overlap check: substrate_query top hits are lexical concept-nodes
    ('function word' cosine 0.3066, dictionary/wordnet); NO prior EXPERIMENT arc atom at
    cosine>0.30 -> genuine amendment, not a rediscovery.
"""
import json
import os
import time
import pathlib

REPO = pathlib.Path("d:/AI/hd-instrument")
MATH_ATOMS = REPO / "data/substrate_index/math/atoms.jsonl"
CERT_LEDGER = REPO / "data/substrate_index/meta/cert_ledger.jsonl"

TS_NOW = time.time()
TS_ISO = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(TS_NOW))
DATE = "2026-07-08"
INTEGRATION_COMMIT = "3c4d85aa"
REPO_HEAD_AT_AMEND = "7a32d8f4c"

ORIGINAL_ATOM_ID = "T3/EXP_substrate_compose_freq_routing_v5_DEFINITIVE"
ORIGINAL_ATOM_QUALIFIED = f"math::{ORIGINAL_ATOM_ID}"

AMEND_ID = (
    "T3/NOTE_substrate_compose_freq_routing_v5_DEFINITIVE_SCOPE_CAVEAT_no_tier_change_"
    "ATTRIBUTION_SHARPENED_certified_control_was_RAW_HEBBIAN_n_steps_0_which_BUNDLES_"
    "the_cfRPE_delta_rule_AND_the_frequency_routing_against_a_TIGHTER_single_kernel_delta_"
    "rule_control_same_iterative_training_no_routing_routing_genuine_contribution_is_"
    "REGIME_DEPENDENT_high_in_degree_function_word_regime_routed_beats_single_delta_"
    "plus_0p118_BPC_2seed_matches_lr_rho_crosstalk_oracle_generic_symmetric_in_degree_"
    "routing_gain_collapses_to_plus_0p024_below_0p05_delta_rule_carries_the_lift_over_"
    "hebbian_witness_test_compose_freq_routing_6_passed_telemetry_sensitive_CG_STANDS_"
    "because_certified_text8_regime_IS_high_in_degree_natural_language_function_word_"
    "structure_SCOPE_SHARPENING_not_refutation_no_demote_no_supersede_cert_delta_0_"
    "surfaced_by_stage2_integration_commit_3c4d85aa_2026-07-08"
)

AMEND_ATOM = {
    "id": AMEND_ID,
    "name": (
        "SCOPE CAVEAT (NO TIER CHANGE) on compose_freq_routing v5 DEFINITIVE CG "
        f"(amends {ORIGINAL_ATOM_QUALIFIED}). The certified lift compared the frequency-"
        "routed arm ONLY against a RAW-HEBBIAN baseline (n_steps=0). That control bundles "
        "TWO effects: the cf-RPE delta-rule (iterative training) AND the frequency routing "
        "(two kernels + routed readout). Against a TIGHTER single-kernel delta-rule control "
        "(same iterative training, no routing), routing's genuine contribution is "
        "REGIME-DEPENDENT. Verified off-disk (Skunkworks recompute off the integration "
        "witness, 2 seeds): in the HIGH-IN-DEGREE / function-word regime (high-freq targets "
        "are successors of many contexts) routed beats single-delta by +0.118 BPC (matches "
        "the lr*rho crosstalk oracle); in a GENERIC / symmetric-in-degree regime the routing "
        "gain collapses to +0.024 BPC (below the 0.05 witness threshold) and the DELTA-RULE, "
        "not the routing, carries the lift over raw-Hebbian. TIER STANDS at "
        "CHAIN_GRADE_DEFINITIVE: the certified text8 corpus IS high-in-degree (natural-"
        "language Zipfian function-word structure), so the certified +0.148 BPC lift is real "
        "in its regime. This is a SCOPE-SHARPENING of the 'routing' attribution, NOT a "
        "refutation. Original atom NOT superseded, NOT demoted; CERT delta = 0. Corroborated "
        "by verification/test_compose_freq_routing.py (6 passed; telemetry-sensitive - the "
        "routing advantage collapses without in-degree asymmetry). Surfaced by Stage-2 "
        f"integration commit {INTEGRATION_COMMIT}."
    ),
    "corpus": "math",
    "tier": "T3",
    "kind": "amendment_record",
    "description": (
        f"OFF-DATA verified {DATE} by Skunkworks independent recompute (NOT from verdict-report):\n\n"
        f"WHAT WAS CHECKED:\n"
        f"  (1) Certified cell control setup read directly from\n"
        f"      experiments/exp_substrate_compose_freq_routing_v5_DEFINITIVE.py ARM_CONFIGS:\n"
        f"      ARM_BASELINE_N8192 n_steps=0 type=BASELINE (raw Hebbian, build_W_hebbian_gpu);\n"
        f"      ARM_BASELINE_N4096 n_steps=0 type=BASELINE; ARM_FREQ_DEEPER_* n_steps=2000/3000\n"
        f"      type=FREQ (iterative cf-RPE delta-rule + frequency routing). NO single-kernel\n"
        f"      delta-rule control exists in the cell. => certified +0.148 BPC lift\n"
        f"      (FREQ_DEEPER_N8192 7.1647 vs BASELINE_N8192 7.3124) BUNDLES delta-rule + routing.\n"
        f"  (2) Integration witness verification/test_compose_freq_routing.py isolates the tight\n"
        f"      control (hdlab.compose_freq_routing.build_single_kernel: single-kernel delta-rule,\n"
        f"      SAME n_steps/lr as routed, no frequency gating). pytest: 6 passed in ~18s.\n"
        f"  (3) Independent recompute off the witness corpus builder (seeds 7,13; V=200 n_dim=128\n"
        f"      n_high=15), routed vs single-delta vs raw-Hebbian, by regime:\n\n"
        f"      HIGH-IN-DEGREE (hi_indeg=40 rare_indeg=1; function-word structure):\n"
        f"        s7:  heb 7.2430 single 7.1352 routed 7.0178 | r-vs-single +0.1174 r-vs-heb +0.2253\n"
        f"        s13: heb 7.2487 single 7.1339 routed 7.0157 | r-vs-single +0.1182 r-vs-heb +0.2331\n"
        f"        MEAN r-vs-single +0.1178  r-vs-heb +0.2292  -> routing GENUINELY adds over delta.\n\n"
        f"      GENERIC / symmetric (hi_indeg=8 rare_indeg=8):\n"
        f"        s7:  heb 7.3803 single 7.3146 routed 7.2920 | r-vs-single +0.0225\n"
        f"        s13: heb 7.3789 single 7.3119 routed 7.2866 | r-vs-single +0.0253\n"
        f"        MEAN r-vs-single +0.0239 (< 0.05; collapses) ; single-vs-heb +0.066\n"
        f"        -> the DELTA-RULE carries the lift over raw-Hebbian; routing does NOT add.\n\n"
        f"ATTRIBUTION CORRECTION (over-attribution surfaced by integration):\n"
        f"  The v5 atom framed the +0.148 BPC as 'frequency-routed learning'. Off-disk, in\n"
        f"  generic/low-in-degree regimes the cf-RPE DELTA-RULE (not the routing) is what beats\n"
        f"  raw-Hebbian. Routing's genuine, isolable contribution is CONFINED to the\n"
        f"  high-in-degree / function-word regime, where high-frequency targets are successors\n"
        f"  of many contexts and a single shared kernel suffers lr*rho crosstalk that dedicated\n"
        f"  frequency-gated kernels remove.\n\n"
        f"WHY TIER STANDS (CHAIN_GRADE_DEFINITIVE, no demote):\n"
        f"  The certified regime is V=4000 text8 natural language. Natural language IS\n"
        f"  high-in-degree by construction (Zipfian function words are successors of very many\n"
        f"  contexts). This is exactly the regime where routing genuinely wins (+0.12 BPC over\n"
        f"  single-delta across seeds in the witness; matches the crosstalk oracle). So the\n"
        f"  certified text8 result held for the RIGHT reason. The CG is preserved.\n\n"
        f"WHAT CHANGES / WHAT REMAINS:\n"
        f"  CHANGES: the SCOPE of the 'routing' attribution. Routing is load-bearing ONLY in\n"
        f"    high-in-degree/function-word regimes; in generic/low-in-degree regimes the\n"
        f"    delta-rule alone matches routed and routing adds nothing beyond noise.\n"
        f"  REMAINS: tier (CHAIN_GRADE_DEFINITIVE), all per-arm numbers, all per-seed lifts,\n"
        f"    the discriminating high-freq/rare-freq telemetry, the sanity rails, the v4\n"
        f"    replication. No metric in the original atom is retracted.\n\n"
        f"CORROBORATING REFERENCE: verification/test_compose_freq_routing.py\n"
        f"  test_routing_beats_both_controls_under_frequency_indegree_asymmetry (routed > single\n"
        f"  by >0.05 AND > Hebbian by >0.12 under asymmetry) and\n"
        f"  test_routing_advantage_collapses_without_indegree_asymmetry (symmetric gain < 0.06;\n"
        f"  asymmetric > 2x symmetric) -> telemetry-sensitive, not by-construction.\n\n"
        f"CROSS-ARC OVERLAP CHECK {DATE}: substrate_query 'compose frequency routing single\n"
        f"  kernel delta rule in-degree function word' -> top hits are lexical concept-nodes\n"
        f"  ('function word' cosine 0.3066 concept/wordnet; 'jam a single frequency' 0.29). NO\n"
        f"  prior EXPERIMENT arc atom at cosine>0.30. Genuine amendment, not a rediscovery.\n\n"
        f"DISPOSITION: SCOPE-SHARPENING amendment. cert_increment_delta=0. Original atom\n"
        f"  {ORIGINAL_ATOM_QUALIFIED} NOT superseded, NOT demoted. Surfaced by Stage-2\n"
        f"  integration commit {INTEGRATION_COMMIT}; repo HEAD at amend {REPO_HEAD_AT_AMEND}.\n"
        f"  Author: hdi_skunkworks landed-VET/cert-integrity audit {DATE}."
    ),
    "metadata": {
        "provenance_quality": "AUDITOR_SCOPE_CAVEAT_NO_TIER_CHANGE",
        "cert_status": "chain_grade_definitive_scope_sharpened",
        "verdict": "SCOPE_CAVEAT_NO_TIER_CHANGE_routing_attribution_over_attributed_certified_control_raw_hebbian_bundles_deltarule_and_routing_tighter_single_kernel_deltarule_control_shows_routing_genuine_add_is_high_in_degree_function_word_regime_only_plus_0p118_BPC_generic_regime_routing_collapses_to_plus_0p024_deltarule_carries_it_CG_stands_certified_text8_is_high_in_degree",
        "amends_atom_referent": ORIGINAL_ATOM_QUALIFIED,
        "amends_atom_short_id": ORIGINAL_ATOM_ID,
        "no_tier_change": True,
        "tier_confirmed": "CHAIN_GRADE_DEFINITIVE",
        "supersedes_atom_id": None,
        "demote": False,
        "amendment_type": "scope_caveat_attribution_sharpening_not_upward_not_downward_tier",
        "surfaced_by_integration_commit": INTEGRATION_COMMIT,
        "repo_head_at_amend": REPO_HEAD_AT_AMEND,
        "verified_off_data_by": "hdi_skunkworks_independent_recompute_2026-07-08",
        "verified_off_data_evidence": (
            "read experiments/exp_substrate_compose_freq_routing_v5_DEFINITIVE.py ARM_CONFIGS "
            "(all BASELINE arms n_steps=0 raw Hebbian; no single-kernel delta control); ran "
            "pytest verification/test_compose_freq_routing.py 6 passed; independent recompute "
            "off witness builder _build_freq_indegree_corpus + _run_arms seeds 7,13 both regimes"
        ),
        "attribution_change": (
            "routing_attribution_scoped_to_high_in_degree_function_word_regime; "
            "in_generic_low_in_degree_regimes_the_cfRPE_delta_rule_not_routing_carries_the_lift"
        ),
        "what_remains_unchanged": (
            "tier_CHAIN_GRADE_DEFINITIVE; all_per_arm_bpc_means; all_5_per_seed_lifts; "
            "discriminating_high_freq_rare_freq_telemetry; sanity_rails; v4_replication; "
            "no_metric_retracted; certified_text8_lift_real_in_its_high_in_degree_regime"
        ),
        "recompute_high_in_degree_regime": {
            "config": "hi_indeg=40 rare_indeg=1 V=200 n_dim=128 n_high=15",
            "seed7": {"heb": 7.2430, "single_delta": 7.1352, "routed": 7.0178,
                       "routed_vs_single": 0.1174, "routed_vs_heb": 0.2253},
            "seed13": {"heb": 7.2487, "single_delta": 7.1339, "routed": 7.0157,
                        "routed_vs_single": 0.1182, "routed_vs_heb": 0.2331},
            "mean_routed_vs_single": 0.1178,
            "mean_routed_vs_heb": 0.2292,
        },
        "recompute_generic_symmetric_regime": {
            "config": "hi_indeg=8 rare_indeg=8 V=200 n_dim=128 n_high=15",
            "seed7": {"heb": 7.3803, "single_delta": 7.3146, "routed": 7.2920,
                       "routed_vs_single": 0.0225},
            "seed13": {"heb": 7.3789, "single_delta": 7.3119, "routed": 7.2866,
                        "routed_vs_single": 0.0253},
            "mean_routed_vs_single": 0.0239,
            "single_vs_heb_carries_lift": True,
            "routing_collapses_below_0p05_threshold": True,
        },
        "witness_reference": "verification/test_compose_freq_routing.py (6 passed; telemetry-sensitive)",
        "witness_pytest_result": "6 passed",
        "corroborating_oracle": "compose_freq_single_kernel_crosstalk (lr*rho); routing sets crosstalk to 0",
        "certified_regime_is_high_in_degree": True,
        "certified_regime_justification": "text8_natural_language_Zipfian_function_words_are_successors_of_many_contexts",
        "cross_arc_overlap_check": "top_hits_lexical_concept_nodes_function_word_cosine_0p3066_no_prior_experiment_arc_atom_above_0p30_genuine_amendment_not_rediscovery",
        "cert_increment_delta": 0,
        "discipline_tags": [
            "verify_off_data_not_reports",
            "symmetric_anti_negativity_no_over_correction_downward",
            "attribution_bundled_control_over_states_single_effect",
            "scope_sharpening_not_refutation",
            "Fix_28_verify_per_arm_mechanism_not_verdict_framing",
        ],
        "ts_atomized": TS_NOW,
        "ts_iso_atomized": TS_ISO,
        "atomized_by": "hdi_skunkworks_amend_compose_freq_routing_v5_scope_caveat_2026-07-08",
        "verified_off_data": True,
    },
}

LEDGER_ENTRY = {
    "ts": TS_NOW,
    "ts_iso": TS_ISO,
    "op": "cert_scope_caveat_amendment_no_tier_change",
    "atom_id": f"math::{AMEND_ID}",
    "amends_atom_id": ORIGINAL_ATOM_QUALIFIED,
    "corpus": "math",
    "tier": "CHAIN_GRADE_DEFINITIVE",
    "tier_change": False,
    "cert_status": "chain_grade_definitive_scope_sharpened",
    "cert_class": "auditor_scope_caveat_routing_attribution_over_attributed_bundled_raw_hebbian_control",
    "cert_increment_delta": {"CG": 0, "MM": 0, "HF": 0},
    "cert_delta": {"CG": 0, "MM": 0, "HF": 0},
    "cert_delta_note": (
        "SCOPE-SHARPENING amendment, NO CERT-N change. The v5 CG compared routed vs RAW-HEBBIAN "
        "only (n_steps=0), bundling the cf-RPE delta-rule AND the routing. Against a tighter "
        "single-kernel delta-rule control (verified off-disk via integration witness, 2 seeds), "
        "routing's genuine add is high-in-degree/function-word ONLY (+0.118 BPC); in generic/"
        "symmetric regimes routing collapses (+0.024 BPC) and the delta-rule carries the lift. "
        "Tier STANDS CHAIN_GRADE_DEFINITIVE because certified text8 IS high-in-degree. Not a "
        "demote, not a supersede. Symmetric anti-negativity: CG preserved, attribution sharpened."
    ),
    "verified_off_data": True,
    "verification": "arm_config_read + pytest_witness_6_passed + independent_recompute_2seed_both_regimes",
    "cell": "exp_substrate_compose_freq_routing_v5_DEFINITIVE",
    "surfaced_by_integration_commit": INTEGRATION_COMMIT,
    "repo_head_at_amend": REPO_HEAD_AT_AMEND,
    "auditor": "hdi_skunkworks",
    "atomized_by": "hdi_skunkworks_amend_compose_freq_routing_v5_scope_caveat_2026-07-08",
    "supersedes": None,
    "needs_orchestrator_store_sync": True,
    "raw_metrics_paths": [
        "data/exp_substrate_compose_freq_routing_v5_DEFINITIVE/metrics.json",
        "verification/test_compose_freq_routing.py",
    ],
}


def atomic_append_jsonl(path: pathlib.Path, records: list) -> tuple:
    """Atomic tmp-write + os.replace + verify-load. Returns (lines_before, lines_after)."""
    lines_before = 0
    if path.exists():
        with path.open("r", encoding="utf-8") as f:
            lines_before = sum(1 for _ in f)

    tmp_path = path.with_suffix(path.suffix + ".tmp")
    existing_content = b""
    if path.exists():
        existing_content = path.read_bytes()
    if existing_content and not existing_content.endswith(b"\n"):
        existing_content += b"\n"
    new_lines = b""
    for rec in records:
        new_lines += (json.dumps(rec, ensure_ascii=False) + "\n").encode("utf-8")
    tmp_path.write_bytes(existing_content + new_lines)

    # verify-load the tmp before replace
    with tmp_path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Corrupt JSON at line {i+1} in {tmp_path}: {e}")

    os.replace(tmp_path, path)

    lines_after = 0
    with path.open("r", encoding="utf-8") as f:
        lines_after = sum(1 for _ in f)
    return lines_before, lines_after


def main():
    # integrity precheck: original atom must exist exactly once and be CG
    found = 0
    for line in MATH_ATOMS.open("r", encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            a = json.loads(line)
        except json.JSONDecodeError:
            continue
        if a.get("id") == ORIGINAL_ATOM_ID:
            found += 1
    if found != 1:
        raise RuntimeError(f"Expected exactly 1 original atom {ORIGINAL_ATOM_ID}, found {found}")
    print(f"integrity precheck: original atom present ({found}) -> OK")

    mb, ma = atomic_append_jsonl(MATH_ATOMS, [AMEND_ATOM])
    print(f"math/atoms.jsonl: {mb} -> {ma} (+{ma - mb})")

    lb, la = atomic_append_jsonl(CERT_LEDGER, [LEDGER_ENTRY])
    print(f"meta/cert_ledger.jsonl: {lb} -> {la} (+{la - lb})")

    # verify-load both back and confirm the amendment atom is retrievable + tier confirm
    def load_last(path):
        rec = None
        for line in path.open("r", encoding="utf-8"):
            line = line.strip()
            if line:
                rec = json.loads(line)
        return rec
    a_last = load_last(MATH_ATOMS)
    l_last = load_last(CERT_LEDGER)
    assert a_last["id"] == AMEND_ID, "amendment atom not last line of atoms.jsonl"
    assert a_last["metadata"]["amends_atom_referent"] == ORIGINAL_ATOM_QUALIFIED
    assert a_last["metadata"]["no_tier_change"] is True
    assert a_last["metadata"]["cert_increment_delta"] == 0
    assert l_last["atom_id"] == f"math::{AMEND_ID}"
    assert l_last["tier_change"] is False
    print("\nverify-load OK: amendment atom + ledger entry retrievable")
    print(f"  amends: {ORIGINAL_ATOM_QUALIFIED}")
    print(f"  tier confirmed: CHAIN_GRADE_DEFINITIVE (no change)")
    print(f"  cert_increment_delta: 0")
    print(f"  ts_iso: {TS_ISO}")


if __name__ == "__main__":
    main()
