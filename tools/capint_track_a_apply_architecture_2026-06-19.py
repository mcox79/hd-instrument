#!/usr/bin/env python3
"""Cap-int Track-A apply: architecture domain (Research SPEC #1, 2026-06-19; Director specs / Exp-Dev codes).

33 atoms / 33 capabilities, ALL SINGLETONS (distinct stems; no clusters):
  22 PASS (is_bound=False; WIN) + 5 MIDDLE_BAND (is_bound=True) + 5 HARD_FAIL (is_bound=True)
  + 1 NON_TEST (refuse_gate_nonlinear_readout; capint_verdict=NEUTRAL; is_bound=None).

NEW MANDATORY GUARD (post inst-243 / I1-FAIL lesson; the template LACKED this):
  per-atom pq == CERT_CHAIN_GRADE PRE-CHECK before patching capint_integrated=True. HALT-on-mismatch
  (the enumerator/Store cert-class divergence that put 2 SMOKE atoms in Track-A = I1-FAIL; the fix is to
  verify the Store's provenance_quality is the referent, NOT the enumerator's classification).
+ robust stem->Store-ID resolution (each stem must match EXACTLY ONE atom id; HALT on 0 / >1).
+ A5-safe metadata-only; SELF-ASSERT 1-canonical (N/A singletons); Store-LOAD verify; multi-partition scan.

DRY-RUN default (resolve + pq pre-check + report, NO write). --apply writes (single-writer window;
pre-announce on the bus first). Skunkworks I-checks after. ASCII; no Date.now.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path("data/substrate_index")
DOMAIN = "architecture"

# stems grouped by verdict (Research SPEC #1). is_bound: PASS->False, MIDDLE/HARD_FAIL->True, NON_TEST->None.
PASS_STEMS = [
    "c1_entmax_envelope_sweep", "f8_pinv_padfix_alpha_compound", "i1_bf16_overflow_n65536",
    "kappa3_sensitivity_sweep", "pb_mmr_real_encoder_clustered", "pp48_nkt_depth_5", "pp48_nkt_depth_7",
    "pp55_vsa_binding_n131072", "q_b1_chain_depth_15", "q_b1_chain_depth_20", "q_b1_chain_depth_30",
    "q_b1_chain_depth_40", "sql_hd_aggregation_bound", "substrate_C1_entmax_alpha_readout",
    "substrate_abduction_f1_weakest_signature_kernel_kgram_xor", "substrate_abduction_f1b_confound_break",
    "substrate_arch_ablation_matrix_bigram", "substrate_cognitive_core_architectural_advantage",
    "substrate_minilm_encoder_fidelity", "substrate_position_binding_combined_arch_trigram",
    "t5c_pp225_3seed", "t5c_pp225_pythia14b_fp32proj_3seed",
]
MIDDLE_STEMS = [
    "substrate_tier6_phase_D_4layer_charLM_shakespeare", "combo1_pp48_audit_on_nkt",
    "drosophila_recapture_arch_a", "substrate_drosophila_mb_sparsity_sweep",
    "substrate_kf1_hallucination_order_sensitive_encoder",
]
HARD_FAIL_STEMS = [
    "substrate_trained_mini_lm_readout_fix_nsweep", "combo3_pp51_5method_on_implicit_gram",
    "substrate_autonomous_tier2_mixed_symmetry_link_prediction",
    "substrate_kf1_contradiction_detection_order_sensitive", "substrate_kf1_truthfulqa_style",
]
NON_TEST_STEMS = ["refuse_gate_nonlinear_readout"]

# q_b1_chain_depth_* are N=8192 singletons -> do NOT cluster with the N=16384 cliff bisect atoms (per spec).


def _humanize(stem):
    return stem.replace("_", " ").strip()


def _spec_for(stem, verdict):
    name = _humanize(stem)
    if verdict == "PASS":
        pb = f"{name} at cert-grade PASS"; ib = False
    elif verdict in ("MIDDLE_BAND", "HARD_FAIL"):
        tag = "honest-bounded" if verdict == "MIDDLE_BAND" else "honest-negative bound"
        pb = f"{name} {verdict} ({tag})"; ib = True
    else:  # NON_TEST -> NEUTRAL
        pb = f"{name} (NON_TEST; neutral -- not a WIN/BOUND)"; ib = None
        verdict = "NEUTRAL"
    return {"verdict": verdict, "is_bound": ib, "capability_name": name, "proven_bound": pb}


def build_spec():
    spec = {}
    for stem in PASS_STEMS:
        spec[stem] = _spec_for(stem, "PASS")
    for stem in MIDDLE_STEMS:
        spec[stem] = _spec_for(stem, "MIDDLE_BAND")
    for stem in HARD_FAIL_STEMS:
        spec[stem] = _spec_for(stem, "HARD_FAIL")
    for stem in NON_TEST_STEMS:
        spec[stem] = _spec_for(stem, "NON_TEST")
    return spec


# Explicit exact-ID overrides for substring-ambiguous stems (spec-disambiguated; verify-the-referent).
# q_b1_chain_depth_* -> the N=8192 atoms (spec cross-domain note; the substring also matches _150/_n16384).
# refuse_gate -> substrate_refuse_gate_nonlinear_readout_v1 (spec line 17, the NON_TEST atom).
# The 5 version-choice stems below are LEFT to Research (v1/v2/v3 / CPU/FULL ambiguity = spec-author's call).
OVERRIDE = {
    "q_b1_chain_depth_15": "T3/EXP_q_b1_chain_depth_15_v1_n8192",
    "q_b1_chain_depth_20": "T3/EXP_q_b1_chain_depth_20_v1_n8192",
    "q_b1_chain_depth_30": "T3/EXP_q_b1_chain_depth_30_v1_n8192",
    "q_b1_chain_depth_40": "T3/EXP_q_b1_chain_depth_40_v1_n8192",
    # tier6 + trained_mini_lm: stem doesn't specify version; exactly ONE version is CERT (the other is
    # SMOKE) -> the CERT one IS the capability (Track-A=cert-only). Spec-faithful auto-resolution.
    "substrate_tier6_phase_D_4layer_charLM_shakespeare": "EXP_substrate_tier6_phase_D_4layer_charLM_shakespeare_FULL_v1",
    "substrate_trained_mini_lm_readout_fix_nsweep": "EXP_substrate_trained_mini_lm_readout_fix_nsweep_v2_capped",
    # refuse_gate: spec NAMED substrate_..._v1 which is SMOKE_ONLY (can't Track-A integrate, I1 rule); the
    # only CERT variant has a DIFFERENT name (refuse_gate_nonlinear_readout_v1, no 'substrate') -> NOT a
    # version-pick but a different atom = Research disposition. Left pointing at the spec atom -> HALTs NOT_CERT.
    "refuse_gate_nonlinear_readout": "T3/EXP_substrate_refuse_gate_nonlinear_readout_v1",
    # --- AWAITING Research exact-ID (MULTIPLE CERT versions; do NOT guess which is canonical): ---
    # "kappa3_sensitivity_sweep": "T3/EXP_kappa3_sensitivity_sweep_n16384_v?",
    # "substrate_tier6_phase_D_4layer_charLM_shakespeare": "...CPU_v1_n2048 OR ...FULL_v1",
    # "combo1_pp48_audit_on_nkt": "...v1_n4096 OR ...v2_depth_5_v1",
    # "substrate_trained_mini_lm_readout_fix_nsweep": "...v1 OR ...v2_capped",
    # "combo3_pp51_5method_on_implicit_gram": "...v1_n4096 OR ...v2_cert_fix_n4096",
}


def resolve_and_precheck(ps, spec):
    """Resolve each stem -> exactly-one Store atom id; verify pq==CERT_CHAIN_GRADE. Returns (resolved, problems)."""
    atoms = list(ps.all_atoms())
    by_id = {str(a.id): a for a in atoms}
    resolved = {}   # stem -> atom_id
    problems = []
    for stem, sp in spec.items():
        if stem in OVERRIDE:
            aid = OVERRIDE[stem]
            if aid not in by_id:
                problems.append((stem, "OVERRIDE_ID_NOT_FOUND: %s" % aid, None)); continue
            matches = [aid]
        else:
            matches = [aid for aid in by_id if stem in aid]
        if len(matches) == 0:
            problems.append((stem, "NO_MATCH", None)); continue
        if len(matches) > 1:
            problems.append((stem, "AMBIGUOUS(%d): %s" % (len(matches), matches[:4]), None)); continue
        aid = matches[0]
        pq = (by_id[aid].metadata or {}).get("provenance_quality")
        if pq != "CERT_CHAIN_GRADE":
            problems.append((stem, "NOT_CERT(pq=%s)" % pq, aid)); continue
        resolved[stem] = aid
    return resolved, problems


def build_patches(spec, resolved):
    patches = {}
    for stem, aid in resolved.items():
        sp = spec[stem]
        patches[aid] = {
            "capint_integrated": True,
            "capint_cluster_id": None,
            "capint_cluster_member_role": "singleton",
            "capint_shared_benchmark": None,
            "capint_capability_name": sp["capability_name"],
            "capint_verdict": sp["verdict"],
            "capint_is_bound": sp["is_bound"],
            "capint_proven_bound": sp["proven_bound"],
            "capint_current_best_citation": f"architecture::{aid}",
            "capint_canonical_substring_all": [aid],
            "capint_primary_domain": DOMAIN,
        }
    return patches


def patch_partition(partition_path, patches, applied_ids):
    tmp = partition_path.with_suffix(".jsonl.tmp.%d" % os.getpid())
    n_patched = 0
    with partition_path.open(encoding="utf-8") as src, tmp.open("w", encoding="utf-8") as dst:
        for line in src:
            stripped = line.strip()
            if not stripped:
                dst.write(line); continue
            try:
                atom = json.loads(stripped)
            except json.JSONDecodeError:
                dst.write(line); continue
            aid = atom.get("id")
            if aid in patches and aid not in applied_ids:
                md = atom.get("metadata") or {}
                for k, v in patches[aid].items():
                    md[k] = v
                atom["metadata"] = md
                n_patched += 1
                applied_ids.add(aid)
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
        dst.flush()
        try:
            os.fsync(dst.fileno())
        except OSError:
            pass
    os.replace(tmp, partition_path)
    return n_patched


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply

    sys.path.insert(0, str(Path('.').resolve()))
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(ROOT)
    spec = build_spec()
    print(f"SPEC: {len(spec)} atoms (22 PASS + 5 MIDDLE + 5 HARD_FAIL + 1 NON_TEST), all singletons, domain={DOMAIN}.")

    pre_int = sum(1 for a in ps.all_atoms() if (a.metadata or {}).get("capint_integrated") is True)
    print(f"PRE: capint_integrated={pre_int}")

    # --- MANDATORY per-atom pq pre-check + stem resolution (I1 lesson) ---
    resolved, problems = resolve_and_precheck(ps, spec)
    print(f"\n--- pq PRE-CHECK + stem resolution: {len(resolved)}/{len(spec)} ready ---")
    if problems:
        print(f"HALT: {len(problems)} atoms FAILED pre-check (NOT applying any -- all-or-nothing):")
        for stem, reason, aid in problems:
            print(f"  {stem}: {reason}" + (f"  (id={aid})" if aid else ""))
        print("\n-> Route these to Research for disposition (enumerator/Store mismatch like I1, or stem typo). "
              "Do NOT integrate non-CERT atoms.")
        return 3
    print(f"PASS: all {len(spec)} stems resolved to exactly-one CERT_CHAIN_GRADE atom.")

    patches = build_patches(spec, resolved)
    if not apply:
        print(f"\nDRY-RUN OK -> would integrate {len(patches)} atoms; capint_integrated {pre_int}->{pre_int+len(patches)}.")
        print("Re-run --apply (single-writer window; pre-announce on bus first). Then Skunkworks I-check.")
        return 0

    applied_ids = set()
    total = 0
    for part_dir in sorted(ROOT.iterdir()):
        if not part_dir.is_dir():
            continue
        af = part_dir / "atoms.jsonl"
        if not af.exists():
            continue
        n = patch_partition(af, patches, applied_ids)
        if n:
            print(f"  patched {n} in {part_dir.name}")
        total += n
    if total != len(patches):
        print(f"WARNING: patched {total}/{len(patches)}. Missing: {[a for a in patches if a not in applied_ids]}")
        return 2

    # Store-LOAD verify + count gate
    ps2 = PartitionedStore(ROOT)
    atoms2 = list(ps2.all_atoms())
    post_int = sum(1 for a in atoms2 if (a.metadata or {}).get("capint_integrated") is True)
    arch_atoms = [a for a in atoms2 if (a.metadata or {}).get("capint_primary_domain") == DOMAIN]
    # SELF-ASSERT 1-canonical (singletons -> no canonical clusters introduced)
    bad_canon = [a.id for a in atoms2 if (a.metadata or {}).get("capint_cluster_member_role") == "canonical"
                 and (a.metadata or {}).get("capint_cluster_id") is None]
    gate_ok = (len(atoms2) > 0 and post_int == pre_int + len(patches) and not bad_canon)
    print(f"\nPOST: Store-LOAD OK ({len(atoms2)} atoms) | capint_integrated {pre_int}->{post_int} (+{len(patches)}) "
          f"| architecture cap-int atoms={len(arch_atoms)} | bad_canonicals={len(bad_canon)} | gate {'OK' if gate_ok else 'FAIL'}")
    if not gate_ok:
        print("HARD_FAIL: gate."); return 6
    print(f"\nAPPLY OK: {len(patches)} architecture singletons integrated. Route Skunkworks I-check (integration-check v1.2).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
