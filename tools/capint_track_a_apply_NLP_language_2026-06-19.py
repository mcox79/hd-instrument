#!/usr/bin/env python3
"""Cap-int Track-A apply: NLP_language domain (Skunkworks batch-VET'd ACCEPT 2026-06-19).

Adds 19 atoms / 19 capabilities (ALL SINGLETONS; capability-fragmented domain):
- 7 PASS singletons (is_bound=False; WIN-class)
- 8 MIDDLE_BAND singletons (is_bound=True; honest-bounded)
- 4 HARD_FAIL singletons (is_bound=True; honest-negative)

Skunkworks's batch-VET ruling: 'SINGLETONS is the safe default' (the optional
ner_gazetteer mini-cluster pair is the cert-owner's call; defaulting safe
per Skunkworks's note line 7).

Pattern: capint_track_a_apply_math_domain_2026-06-19.py (multi-partition scan).
Discipline: A5-safe metadata-only + SELF-ASSERT 1-canonical/cluster (N/A; all
singletons; just verify no new mis-classification) + Store-LOAD verify +
verdict-faithful per integration-check v1.1 vocab.
"""

import json
import os
from pathlib import Path

ROOT = Path("data/substrate_index")

# 19 SINGLETONS (verdict-faithful is_bound)
SINGLETONS = {
    # PASS (7; WIN-class; is_bound=False)
    "T3/EXP_ner_transition_charngram_noise_crosscut_cpu_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "NER transition + char n-gram noise-crosscut",
        "proven_bound": "NER transition char-ngram noise-crosscut at cert-grade PASS",
    },
    "T3/EXP_pb_kf1_multilang_chain_robustness_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "PB KF1 multi-lang chain robustness",
        "proven_bound": "PB KF1 multilang chain robustness at cert-grade PASS",
    },
    "T3/EXP_pb_multilang_paraphrase_chain_kf1_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "PB multi-lang paraphrase chain KF1",
        "proven_bound": "PB multilang paraphrase chain KF1 at cert-grade PASS",
    },
    "T3/EXP_pos_tagger_multiseed_cpu_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "POS tagger multi-seed",
        "proven_bound": "POS tagger multi-seed at cert-grade PASS",
    },
    "T3/EXP_substrate_crossdomain_transfer_conll2003_ontonotes_ner_cpu_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Substrate cross-domain transfer CoNLL2003->OntoNotes NER",
        "proven_bound": "Substrate cross-domain transfer CoNLL2003->OntoNotes NER at cert-grade PASS",
    },
    "T3/EXP_substrate_extended_context_ceiling_posbind_symw_v1_8192_16384_gpu": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Substrate extended-context ceiling posbind+symW",
        "proven_bound": (
            "Substrate extended-context ceiling posbind+symW at cert-grade PASS "
            "(N=8192/16384 GPU)"
        ),
    },
    "T3/EXP_temporal_contextual_multiseed_cpu_v1": {
        "verdict": "PASS",
        "is_bound": False,
        "capability_name": "Temporal contextual multi-seed",
        "proven_bound": "Temporal contextual multi-seed at cert-grade PASS",
    },
    # MIDDLE_BAND (8; honest-bounded; is_bound=True)
    "T3/EXP_depparse_hashed_multiseed_cpu_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Dependency parse hashed multi-seed bound",
        "proven_bound": "Depparse hashed multi-seed MIDDLE_BAND (honest-bounded)",
    },
    "T3/EXP_ner_feature_ablation_cpu_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "NER feature ablation bound",
        "proven_bound": "NER feature ablation MIDDLE_BAND (honest-bounded; feature-loss bound)",
    },
    "T3/EXP_ner_gazetteer_external_cpu_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "NER gazetteer external bound",
        "proven_bound": "NER gazetteer external MIDDLE_BAND (honest-bounded)",
    },
    "T3/EXP_ner_multiseed_cpu_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "NER multi-seed bound",
        "proven_bound": "NER multi-seed MIDDLE_BAND (honest-bounded; multi-seed variance bound)",
    },
    "T3/EXP_substrate_crossdomain_transfer_sst2_imdb_cpu_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Substrate cross-domain transfer SST2->IMDB bound",
        "proven_bound": (
            "Substrate cross-domain transfer SST2->IMDB MIDDLE_BAND "
            "(honest-bounded; cross-domain sentiment transfer bound)"
        ),
    },
    "T3/EXP_substrate_data_attribution_counterfactual_rpe_v1_n4096": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Substrate data attribution counterfactual RPE bound",
        "proven_bound": "Substrate data attribution counterfactual RPE MIDDLE_BAND (N=4096; honest-bounded)",
    },
    "T3/EXP_substrate_spectral_edge_n_extension_finer_v2_4096_65536_gpu": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Substrate spectral edge N-extension finer bound",
        "proven_bound": (
            "Substrate spectral edge N-extension finer v2 MIDDLE_BAND "
            "(N=4096/65536 GPU; honest-bounded)"
        ),
    },
    "T3/EXP_substrate_stage_a_bio_smoke_iter2_B1_B6_v1": {
        "verdict": "MIDDLE_BAND",
        "is_bound": True,
        "capability_name": "Substrate stage-A bio-smoke iter2 B1-B6 bound",
        "proven_bound": "Substrate stage-A bio-smoke iter2 B1-B6 MIDDLE_BAND (honest-bounded)",
    },
    # HARD_FAIL (4; honest-negative; is_bound=True)
    "T3/EXP_e1_substrate_crf_shared_lib_cpu_v1": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "E1 substrate CRF shared-lib bound",
        "proven_bound": "E1 substrate CRF shared-lib HARD_FAIL (honest-negative bound)",
    },
    "T3/EXP_ner_gazetteer_noise_crosscut_cpu_v1": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "NER gazetteer noise-crosscut bound",
        "proven_bound": (
            "NER gazetteer noise-crosscut HARD_FAIL "
            "(honest-negative; gazetteer + noise interaction breaks NER)"
        ),
    },
    "T3/EXP_substrate_stage_a_bio_b3_b6_ceiling_followup_v1": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "Substrate stage-A bio B3-B6 ceiling follow-up bound",
        "proven_bound": "Substrate stage-A bio B3-B6 ceiling follow-up HARD_FAIL (honest-negative)",
    },
    "T3/EXP_substrate_stage_a_bio_smoke_REVISED_v1": {
        "verdict": "HARD_FAIL",
        "is_bound": True,
        "capability_name": "Substrate stage-A bio-smoke REVISED bound",
        "proven_bound": "Substrate stage-A bio-smoke REVISED HARD_FAIL (honest-negative)",
    },
}


def build_patches():
    patches = {}
    for atom_id, spec in SINGLETONS.items():
        qid = f"math::{atom_id}"
        patches[atom_id] = {
            "capint_integrated": True,
            "capint_cluster_id": None,
            "capint_cluster_member_role": "singleton",
            "capint_shared_benchmark": None,
            "capint_capability_name": spec["capability_name"],
            "capint_verdict": spec["verdict"],
            "capint_is_bound": spec["is_bound"],
            "capint_proven_bound": spec["proven_bound"],
            "capint_current_best_citation": qid,
            "capint_canonical_substring_all": [atom_id],
            "capint_primary_domain": "NLP_language",
        }
    return patches


def patch_partition(partition_path, patches, applied_ids):
    tmp = partition_path.with_suffix(".jsonl.tmp")
    n_patched = 0
    n_lines = 0
    with partition_path.open(encoding="utf-8") as src, \
         tmp.open("w", encoding="utf-8") as dst:
        for line in src:
            stripped = line.strip()
            if not stripped:
                dst.write(line)
                continue
            try:
                atom = json.loads(stripped)
            except json.JSONDecodeError:
                dst.write(line)
                continue
            n_lines += 1
            aid = atom.get("id")
            if aid in patches and aid not in applied_ids:
                md = atom.get("metadata") or {}
                for k, v in patches[aid].items():
                    md[k] = v
                atom["metadata"] = md
                for k in list(atom.keys()):
                    if k.startswith("capint_") and k != "metadata":
                        del atom[k]
                n_patched += 1
                applied_ids.add(aid)
            dst.write(json.dumps(atom, ensure_ascii=False) + "\n")
    os.replace(tmp, partition_path)
    return n_patched, n_lines


def main():
    patches = build_patches()
    print(f"Built {len(patches)} patches (19 singletons; all NLP_language domain).")

    applied_ids = set()
    total_patched = 0
    for part_dir in sorted(ROOT.iterdir()):
        if not part_dir.is_dir():
            continue
        atoms_file = part_dir / "atoms.jsonl"
        if not atoms_file.exists():
            continue
        n_patched, n_lines = patch_partition(atoms_file, patches, applied_ids)
        if n_patched > 0:
            print(f"  Patched {n_patched}/{len(patches)} in {part_dir.name} "
                  f"({n_lines} lines scanned).")
        total_patched += n_patched

    print(f"Total patched: {total_patched}/{len(patches)}")

    if total_patched != len(patches):
        print("WARNING: not all patches applied. Missing atom IDs:")
        for pid in patches:
            if pid not in applied_ids:
                print(f"  Missing: {pid}")
        return 2

    # Self-assert 1-canonical (N/A for singletons; just verify no NEW cluster
    # canonicals got mis-mapped)
    print("\n--- SELF-ASSERT: 1 canonical per cluster ---")
    from backend.substrate_index.partition import PartitionedStore
    ps = PartitionedStore(ROOT)
    cluster_canonicals = {}
    for a in ps.all_atoms():
        md = a.metadata or {}
        cid = md.get("capint_cluster_id")
        role = md.get("capint_cluster_member_role")
        if cid and role == "canonical":
            cluster_canonicals.setdefault(cid, []).append(a.id)
    problems = [(cid, m) for cid, m in cluster_canonicals.items() if len(m) != 1]
    if problems:
        print("FAIL: clusters with != 1 canonical:")
        for cid, members in problems:
            print(f"  {cid}: {members}")
        return 3
    else:
        print(f"PASS: all {len(cluster_canonicals)} cap-int clusters have exactly 1 canonical.")

    # Store-LOAD verify
    print("\n--- Store-LOAD verify ---")
    print(f"all_atoms loadable: {len(list(ps.all_atoms()))} atoms.")

    # Show NLP domain final state
    print("\n--- NLP_language cap-int integrated ---")
    nlp_atoms = [a for a in ps.all_atoms()
                 if (a.metadata or {}).get('capint_primary_domain') == 'NLP_language']
    print(f"  Total cap-int NLP_language atoms: {len(nlp_atoms)}")
    pass_n = sum(1 for a in nlp_atoms if (a.metadata or {}).get('capint_verdict') == 'PASS')
    middle_n = sum(1 for a in nlp_atoms if (a.metadata or {}).get('capint_verdict') == 'MIDDLE_BAND')
    fail_n = sum(1 for a in nlp_atoms if (a.metadata or {}).get('capint_verdict') == 'HARD_FAIL')
    print(f"  Verdict distribution: PASS={pass_n}, MIDDLE_BAND={middle_n}, HARD_FAIL={fail_n}")

    print("\nAPPLY + Store-LOAD verify + 1-canonical self-assert COMPLETE.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
