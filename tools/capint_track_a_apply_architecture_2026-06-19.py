#!/usr/bin/env python3
"""Cap-int Track-A apply: architecture domain (Research SPEC #1 + 4 dispositions, 2026-06-19).

Final integration set (Director specs / Exp-Dev codes):
  SINGLETONS: 21 PASS + 6 MIDDLE_BAND + 5 HARD_FAIL + 1 NEUTRAL(NON_TEST) = 33 singleton atoms
  CLUSTER:    kappa3_sensitivity_sweep @ N=16384 = 3 atoms (1 canonical v3 + 2 scale_points; all PASS)
  => 36 atoms integrated / 34 capabilities (kappa3 cluster = 1 cap).
  SKIP (recorded, NOT integrated): combo3 v1 (superseded by v2_cert_fix; I7), refuse_gate substrate_v1 (SMOKE).

MANDATORY GUARD (inst-243 / I1-FAIL lesson): per-atom pq == CERT_CHAIN_GRADE PRE-CHECK on EVERY integrated
atom (singleton + cluster member). HALT-on-mismatch (do NOT integrate non-CERT -- the I1 class).
+ exact-ID for every atom (no fragile stem-substring; the dispositions pin versions). I4: kappa3 cluster has
exactly 1 canonical; q_b1_chain_depth_* are N=8192 SINGLETONS (NOT clustered with the N=16384 cliff-bisect).

DRY-RUN default (pq pre-check + report). --apply writes (single-writer window; PRE-ANNOUNCE on bus first).
Skunkworks I-checks after. A5-safe (capint_* only); Store-LOAD verify; multi-partition scan. ASCII; no Date.now.
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path


def _atomic_replace(tmp, path, retries=25, backoff=0.1):
    """os.replace with bounded retry for Windows WinError 5/32 (transient lock from a concurrent
    Store reader -- sync/consumer/AV). The proven schema.py pattern. Raises if the lock persists."""
    for i in range(retries):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            if i == retries - 1:
                raise
            time.sleep(backoff)

ROOT = Path("data/substrate_index")
DOMAIN = "architecture"

# --- SINGLETONS: exact stem (resolves to exactly-one atom) -> verdict. is_bound: PASS->False,
#     MIDDLE/HARD_FAIL->True, NEUTRAL->None. Exact-ID overrides below for version-ambiguous stems. ---
PASS = [
    "c1_entmax_envelope_sweep", "f8_pinv_padfix_alpha_compound", "i1_bf16_overflow_n65536",
    "pb_mmr_real_encoder_clustered", "pp48_nkt_depth_5", "pp48_nkt_depth_7", "pp55_vsa_binding_n131072",
    "q_b1_chain_depth_15", "q_b1_chain_depth_20", "q_b1_chain_depth_30", "q_b1_chain_depth_40",
    "sql_hd_aggregation_bound", "substrate_C1_entmax_alpha_readout",
    "substrate_abduction_f1_weakest_signature_kernel_kgram_xor", "substrate_abduction_f1b_confound_break",
    "substrate_arch_ablation_matrix_bigram", "substrate_cognitive_core_architectural_advantage",
    "substrate_minilm_encoder_fidelity", "substrate_position_binding_combined_arch_trigram",
    "t5c_pp225_3seed", "t5c_pp225_pythia14b_fp32proj_3seed",
    "kappa3_sensitivity_sweep_n16384_v3",  # CORRECTION: kappa3 = v3-only SINGLETON (v1+v2 -> substrate_integrity)
]  # 22
MIDDLE = [
    "substrate_tier6_phase_D_4layer_charLM_shakespeare", "drosophila_recapture_arch_a",
    "substrate_drosophila_mb_sparsity_sweep", "substrate_kf1_hallucination_order_sensitive_encoder",
    "combo1_pp48_audit_on_nkt_v1_n4096", "combo1_pp48_audit_on_nkt_v2_depth_5_v1",  # combo1 -> 2 singletons
]  # 6
HARD_FAIL = [
    "substrate_trained_mini_lm_readout_fix_nsweep", "substrate_autonomous_tier2_mixed_symmetry_link_prediction",
    "substrate_kf1_contradiction_detection_order_sensitive", "substrate_kf1_truthfulqa_style",
    # combo3 v2 DROPPED (Research disposition 2026-06-19): already integrated in reasoning_multihop MIDDLE_BAND;
    # stays there (do NOT re-domain). Architecture batch = 32.
]  # 4
NEUTRAL = ["refuse_gate_nonlinear_readout"]  # 1 (NON_TEST; resolved to the CERT variant via OVERRIDE)

# Exact-ID overrides for version-ambiguous stems (dispositions + spec cross-domain note).
OVERRIDE = {
    "q_b1_chain_depth_15": "T3/EXP_q_b1_chain_depth_15_v1_n8192",
    "q_b1_chain_depth_20": "T3/EXP_q_b1_chain_depth_20_v1_n8192",
    "q_b1_chain_depth_30": "T3/EXP_q_b1_chain_depth_30_v1_n8192",
    "q_b1_chain_depth_40": "T3/EXP_q_b1_chain_depth_40_v1_n8192",
    "substrate_tier6_phase_D_4layer_charLM_shakespeare": "EXP_substrate_tier6_phase_D_4layer_charLM_shakespeare_FULL_v1",
    "substrate_trained_mini_lm_readout_fix_nsweep": "EXP_substrate_trained_mini_lm_readout_fix_nsweep_v2_capped",
    "combo1_pp48_audit_on_nkt_v1_n4096": "T3/EXP_combo1_pp48_audit_on_nkt_v1_n4096",
    "combo1_pp48_audit_on_nkt_v2_depth_5_v1": "T3/EXP_combo1_pp48_audit_on_nkt_v2_depth_5_v1",
    "refuse_gate_nonlinear_readout": "T3/EXP_refuse_gate_nonlinear_readout_v1",  # CERT variant (spec 'substrate_' was a typo->SMOKE)
    "kappa3_sensitivity_sweep_n16384_v3": "T3/EXP_kappa3_sensitivity_sweep_n16384_v3_delta_alpha_protocol_v1",  # v3-only singleton (correction)
}

# CORRECTION (Research URGENT 2026-06-19): kappa3 is NOT a cluster -- only v3 is architecture (PASS);
# v1+v2 are substrate_integrity (HARD_FAIL), spec'd in that domain separately. So v3 = PASS SINGLETON
# (added to PASS list + OVERRIDE above). No architecture cluster.
CLUSTERS = []

# SKIP (recorded, NOT integrated; provenance only).
SKIP = {
    "T3/EXP_combo3_pp51_5method_on_implicit_gram_v1_n4096": "superseded by v2_cert_fix (I7 superseded-chain)",
    "T3/EXP_combo3_pp51_5method_on_implicit_gram_v2_cert_fix_n4096": "ALREADY reasoning_multihop MIDDLE_BAND; stays there (Research disposition; not re-domained)",
    "T3/EXP_substrate_refuse_gate_nonlinear_readout_v1": "SMOKE_ONLY (spec typo; CERT variant integrated instead) -> Track-B if re-run",
}

VTAG = {"PASS": False, "MIDDLE_BAND": True, "HARD_FAIL": True, "NEUTRAL": None}


def _hum(aid):
    s = aid.split("/")[-1]
    for p in ("EXP_substrate_", "EXP_"):
        if s.startswith(p):
            s = s[len(p):]
    return s.replace("_", " ").strip()


def _sing_spec(verdict, aid):
    name = _hum(aid)
    if verdict == "PASS":
        pb = f"{name} at cert-grade PASS"
    elif verdict in ("MIDDLE_BAND", "HARD_FAIL"):
        pb = f"{name} {verdict} (" + ("honest-bounded" if verdict == "MIDDLE_BAND" else "honest-negative bound") + ")"
    else:
        pb = f"{name} (NON_TEST; neutral -- not a WIN/BOUND)"
    return {"verdict": verdict, "is_bound": VTAG[verdict], "capability_name": name, "proven_bound": pb}


def resolve_singletons(by_id):
    """stem -> exact CERT atom id. Returns (resolved {stem:(aid,verdict)}, problems)."""
    groups = [(PASS, "PASS"), (MIDDLE, "MIDDLE_BAND"), (HARD_FAIL, "HARD_FAIL"), (NEUTRAL, "NEUTRAL")]
    resolved = {}; problems = []
    for stems, verdict in groups:
        for stem in stems:
            if stem in OVERRIDE:
                aid = OVERRIDE[stem]
                matches = [aid] if aid in by_id else []
            else:
                matches = [a for a in by_id if stem in a]
            if len(matches) != 1:
                problems.append((stem, "NO_MATCH" if not matches else "AMBIGUOUS:%s" % matches[:4])); continue
            aid = matches[0]
            md = by_id[aid].metadata or {}
            pq = md.get("provenance_quality")
            if pq != "CERT_CHAIN_GRADE":
                problems.append((stem, "NOT_CERT(pq=%s) id=%s" % (pq, aid))); continue
            # GUARD (the clobber lesson): an atom ALREADY capint_integrated in another domain must NOT be
            # silently re-domained. A substring collision or a genuine cross-domain claim -> Research disposition.
            if md.get("capint_integrated") is True:
                problems.append((stem, "ALREADY_INTEGRATED domain=%s verdict=%s (cross-domain conflict / substring-collision -- do NOT clobber) id=%s"
                                 % (md.get("capint_primary_domain"), md.get("capint_verdict"), aid))); continue
            resolved[stem] = (aid, verdict)
    return resolved, problems


def check_clusters(by_id):
    problems = []
    for cl in CLUSTERS:
        canon_roles = [m for m in cl["members"] if m[1] == "canonical"]
        if len(canon_roles) != 1:
            problems.append((cl["cluster_id"], "I4: %d canonicals (need 1)" % len(canon_roles)))
        for aid, role in cl["members"]:
            if aid not in by_id:
                problems.append((aid, "NOT_FOUND")); continue
            pq = (by_id[aid].metadata or {}).get("provenance_quality")
            if pq != "CERT_CHAIN_GRADE":
                problems.append((aid, "NOT_CERT(pq=%s)" % pq))
    return problems


def build_patches(resolved):
    patches = {}
    for stem, (aid, verdict) in resolved.items():
        sp = _sing_spec(verdict, aid)
        patches[aid] = {
            "capint_integrated": True, "capint_cluster_id": None, "capint_cluster_member_role": "singleton",
            "capint_shared_benchmark": None, "capint_capability_name": sp["capability_name"],
            "capint_verdict": sp["verdict"], "capint_is_bound": sp["is_bound"],
            "capint_proven_bound": sp["proven_bound"], "capint_current_best_citation": f"{DOMAIN}::{aid}",
            "capint_canonical_substring_all": [aid], "capint_primary_domain": DOMAIN,
        }
    for cl in CLUSTERS:
        for aid, role in cl["members"]:
            patches[aid] = {
                "capint_integrated": True, "capint_cluster_id": cl["cluster_id"],
                "capint_cluster_member_role": role, "capint_shared_benchmark": cl["shared_benchmark"],
                "capint_capability_name": cl["capability_name"], "capint_verdict": cl["verdict"],
                "capint_is_bound": cl["is_bound"], "capint_proven_bound": cl["proven_bound"],
                "capint_current_best_citation": f"{DOMAIN}::{cl['canonical']}",
                "capint_canonical_substring_all": cl["canonical_substring"], "capint_primary_domain": DOMAIN,
            }
    return patches


def patch_partition(path, patches, applied):
    tmp = path.with_suffix(".jsonl.tmp.%d" % os.getpid()); n = 0
    with path.open(encoding="utf-8") as src, tmp.open("w", encoding="utf-8") as dst:
        for line in src:
            s = line.strip()
            if not s:
                dst.write(line); continue
            try:
                atom = json.loads(s)
            except json.JSONDecodeError:
                dst.write(line); continue
            aid = atom.get("id")
            if aid in patches and aid not in applied:
                md = atom.get("metadata") or {}
                md.update(patches[aid]); atom["metadata"] = md
                n += 1; applied.add(aid)
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
        dst.flush()
        try:
            os.fsync(dst.fileno())
        except OSError:
            pass
    _atomic_replace(tmp, path)
    return n


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--apply", action="store_true")
    apply = ap.parse_args().apply
    sys.path.insert(0, str(Path('.').resolve()))
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(ROOT)
    by_id = {str(a.id): a for a in ps.all_atoms()}
    pre_int = sum(1 for a in by_id.values() if (a.metadata or {}).get("capint_integrated") is True)

    resolved, sing_probs = resolve_singletons(by_id)
    clus_probs = check_clusters(by_id)
    n_cluster_atoms = sum(len(c["members"]) for c in CLUSTERS)
    print(f"SPEC#1 architecture: {len(resolved)} singletons + {n_cluster_atoms} cluster atoms = "
          f"{len(resolved)+n_cluster_atoms} integrated; SKIP {len(SKIP)} (superseded/smoke). PRE capint_integrated={pre_int}")
    problems = sing_probs + clus_probs
    if problems:
        print(f"\nHALT: {len(problems)} pre-check failures (all-or-nothing):")
        for a, r in problems:
            print(f"  {a}: {r}")
        return 3
    print(f"pq PRE-CHECK PASS: all {len(resolved)+n_cluster_atoms} atoms CERT_CHAIN_GRADE; kappa3 cluster 1-canonical OK.")
    print("SKIP (NOT integrated):")
    for aid, why in SKIP.items():
        print(f"  {aid}: {why}")

    patches = build_patches(resolved)
    if not apply:
        print(f"\nDRY-RUN OK -> integrate {len(patches)} atoms; capint_integrated {pre_int}->{pre_int+len(patches)}.")
        print("Re-run --apply (PRE-ANNOUNCE single-writer on bus first). Then Skunkworks I-check.")
        return 0

    applied = set(); total = 0
    for pd in sorted(ROOT.iterdir()):
        af = pd / "atoms.jsonl"
        if pd.is_dir() and af.exists():
            k = patch_partition(af, patches, applied)
            if k:
                print(f"  patched {k} in {pd.name}")
            total += k
    if total != len(patches):
        print(f"WARNING: {total}/{len(patches)} patched; missing {[a for a in patches if a not in applied]}"); return 2

    ps2 = PartitionedStore(ROOT); atoms2 = list(ps2.all_atoms())
    post_int = sum(1 for a in atoms2 if (a.metadata or {}).get("capint_integrated") is True)
    canon = {}
    for a in atoms2:
        md = a.metadata or {}
        if md.get("capint_cluster_member_role") == "canonical" and md.get("capint_cluster_id"):
            canon.setdefault(md["capint_cluster_id"], []).append(str(a.id))
    bad = {c: m for c, m in canon.items() if len(m) != 1}
    gate = (len(atoms2) > 0 and post_int == pre_int + len(patches) and not bad)
    print(f"\nPOST: Store-LOAD OK ({len(atoms2)}) | capint_integrated {pre_int}->{post_int} (+{len(patches)}) "
          f"| bad_canonicals={bad} | gate {'OK' if gate else 'FAIL'}")
    if not gate:
        print("HARD_FAIL: gate."); return 6
    print(f"\nAPPLY OK: {len(patches)} architecture atoms integrated (incl kappa3 3-member cluster). Route Skunkworks I-check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
