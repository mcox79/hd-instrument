"""8 within-family SHARES_MATH bridges per Research DECISION 18 Q4 test +
missing dft_linearity edge for convolution_theorem chain completion.

Per Research PRIORITIES + DECISIONS 17-18 note (2026-06-14):

Testbed work order item 2: dft_linearity_lemma DEPENDS_ON conv-theorem
edge (was missing from convolution_theorem_synthesis dependency chain).

Testbed work order item 3: 8 within-family SHARES_MATH bridges for
DECISION 18 Q4 pre-registered discriminator test:
  4 spectral:    svd <-> singular_value_decomposition <-> spectral_theorem_synthesis <-> eigendecomposition
  4 sequence-dp: dtw <-> edit_distance <-> levenshtein_distance <-> needleman_wunsch

Q4 outcome:
  If >=2 bisim archetype classes emerge at SHARES_MATH=58 -> B confirmed (bridges
    were wrong kind; substrate pivots to within-family discipline)
  Still 0 bisim classes -> A confirmed (adopt connected-component + CHTV-1 gate
    as P3 criterion)
  Exactly 1 class -> MIDDLE-BAND inconclusive

Missing sequence-dp atoms (dtw, levenshtein_distance) authored at T3 with
algebra metadata so they participate in bisim properly.

NO LLM. NO bge.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Atom, AtomKind, Corpus, Tier, RelationType


# 2 missing T3 atoms to author
NEW_ATOMS = [
    {
        "id": "T3/dynamic_time_warping",
        "name": "Dynamic time warping (DTW)",
        "aliases": ("dtw", "DTW", "dynamic_time_warping_distance"),
        "description": (
            "Sequence-alignment distance allowing nonlinear local time warping. "
            "Computes min-cost monotone alignment path between two sequences "
            "of varying length via DP recursion over the (|A|+1) x (|B|+1) "
            "matrix. Member of the sequence-dp distance family alongside "
            "edit_distance, levenshtein, and needleman_wunsch."
        ),
        "depends_on": ("math::T1/sequence", "math::T1/dynamic_programming",),
        "algebra": {
            "about_topic": "dtw",
            "domain": "sequence_alignment",
            "structure": "min_cost_DP_over_pairwise_distance_matrix",
            "role": "operation",
            "signature_output_type": "alignment_path",
            "signature_input_type": "two_sequences_with_local_distance",
            "complexity_class": "O_n_squared_d",
        },
        "serves_capability": ("cap_dtw", "cap_sequence_alignment_distance"),
    },
    {
        "id": "T3/levenshtein_distance",
        "name": "Levenshtein distance",
        "aliases": ("levenshtein", "edit_distance_unit_cost"),
        "description": (
            "Minimum number of single-character edits (insertions, deletions, "
            "substitutions) to transform one sequence into another. Special case "
            "of edit_distance with unit substitution cost. Computed via DP over "
            "the (|A|+1) x (|B|+1) matrix. Member of sequence-dp distance family."
        ),
        "depends_on": ("math::T1/sequence", "math::T1/dynamic_programming"),
        "algebra": {
            "about_topic": "levenshtein",
            "domain": "sequence_alignment",
            "structure": "DP_min_edits_unit_cost",
            "role": "operation",
            "signature_output_type": "scalar_edit_distance",
            "signature_input_type": "two_sequences",
            "complexity_class": "O_n_m",
        },
        "serves_capability": ("cap_levenshtein", "cap_sequence_alignment_distance"),
    },
]


# Within-family SHARES_MATH bridges (symmetric)
# 4 spectral
SPECTRAL_BRIDGES = [
    ("math::T1/SVD", "math::T1/singular_value_decomposition",
     "abbreviation for the same canonical concept"),
    ("math::T1/SVD", "math::T3/spectral_theorem_synthesis",
     "SVD is the spectral theorem applied to non-square operators"),
    ("math::T1/singular_value_decomposition", "math::T3/spectral_theorem_synthesis",
     "SVD generalizes the spectral theorem; same orthonormal-bases structure"),
    ("math::T3/spectral_theorem_synthesis", "math::T1/eigendecomposition",
     "spectral theorem IS eigendecomposition for self-adjoint operators"),
    ("math::T1/SVD", "math::T1/eigendecomposition",
     "SVD reduces to eigendecomposition for square symmetric matrices"),
    ("math::T1/singular_value_decomposition", "math::T1/eigendecomposition",
     "SVD generalizes eigendecomposition to non-square"),
]

# 4 sequence-dp
SEQDP_BRIDGES = [
    ("math::T3/dynamic_time_warping", "math::T3/edit_distance",
     "DTW and edit_distance both compute min-cost DP alignment; DTW allows time warping"),
    ("math::T3/dynamic_time_warping", "math::T3/levenshtein_distance",
     "DTW generalizes Levenshtein from discrete to continuous local cost"),
    ("math::T3/dynamic_time_warping", "math::T3/needleman_wunsch",
     "DTW and Needleman-Wunsch both compute global optimal DP alignment"),
    ("math::T3/edit_distance", "math::T3/levenshtein_distance",
     "Levenshtein is edit_distance with unit substitution cost"),
    ("math::T3/edit_distance", "math::T3/needleman_wunsch",
     "Needleman-Wunsch is sequence-alignment edit_distance with biology-tuned cost"),
    ("math::T3/levenshtein_distance", "math::T3/needleman_wunsch",
     "Needleman-Wunsch and Levenshtein both compute DP min-edits over sequence pairs"),
]


# Missing edge: convolution_theorem_synthesis DEPENDS_ON dft_linearity_lemma
# (per Research item 2: "dft_linearity_lemma -> conv-theorem edge"; the
# DEPENDS_ON should be conv-theorem -> dft_linearity since synthesis USES
# linearity as premise)
MISSING_EDGE = (
    "math::T3/convolution_theorem_synthesis", "math::T3/dft_linearity_lemma",
    "DEPENDS_ON",
    "dft_linearity is a required premise of the convolution theorem derivation; closes the chain"
)


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_atoms = len(ps.all_atoms())
    pre_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"pre-ingest: {pre_atoms} atoms, {pre_rels} relations\n")

    # Step 1: author 2 missing T3 atoms (dtw + levenshtein_distance)
    print("=== STEP 1: author missing T3 sequence-dp atoms ===")
    created = 0
    for spec in NEW_ATOMS:
        qid = f"math::{spec['id']}"
        if ps.has_atom(qid):
            print(f"  EXISTS: {qid}")
            continue
        try:
            meta = {
                "operation_type": "sequence_alignment_distance",
                "substrate_load_bearing": True,
                "batch_origin": "within_family_bridges_q4_test_v1",
                "content_type": "FORMAL_SYSTEMS",
                "rule_link": "DECISION_18_Q4_pre_registered_test",
            }
            atom = Atom(
                id=spec["id"], name=spec["name"], corpus=Corpus.MATH,
                tier=Tier.TIER_3_ALGORITHM, description=spec["description"],
                kind=AtomKind.PRIMITIVE, aliases=spec["aliases"],
                metadata=meta, serves_capability=spec["serves_capability"],
                algebra=spec["algebra"],
            )
            ps.add_atom(atom, source="within_family_bridges_q4_test_v1",
                        note="DECISION 18 Q4 sequence-dp family completion")
            print(f"  CREATED: {qid}")
            created += 1

            # depends_on edges
            for tgt in spec["depends_on"]:
                if not ps.has_atom(tgt):
                    continue
                try:
                    ps.add_relation(qid, RelationType.DEPENDS_ON, tgt,
                                    source="within_family_bridges_q4_test_v1",
                                    note="newly-authored sequence-dp atom dependency")
                except Exception:
                    pass
        except Exception as e:
            print(f"  FAIL: {qid} :: {str(e)[:120]}")

    # Refresh existing edges
    existing = set()
    for src, rel_type, tgt in ps.iter_all_relations():
        existing.add((src, rel_type.name, tgt))

    # Step 2: missing convolution-theorem dependency edge
    print("\n=== STEP 2: missing convolution-theorem chain edge ===")
    src, dst, rel_str, reason = MISSING_EDGE
    key = (src, rel_str, dst)
    if key in existing:
        print(f"  EXISTS: {src} -{rel_str}-> {dst}")
    elif not (ps.has_atom(src) and ps.has_atom(dst)):
        print(f"  ENDPOINT MISSING: {src} or {dst}")
    else:
        try:
            ps.add_relation(src, RelationType[rel_str], dst,
                            source="within_family_bridges_q4_test_v1",
                            note=reason)
            existing.add(key)
            print(f"  ADDED: {src} -{rel_str}-> {dst}")
            print(f"    reason: {reason}")
        except Exception as e:
            print(f"  FAIL: {str(e)[:120]}")

    # Step 3: SHARES_MATH bridges (4 spectral)
    print("\n=== STEP 3: 4 spectral bridges (symmetric SHARES_MATH) ===")
    added_specs = 0
    for left, right, reason in SPECTRAL_BRIDGES:
        if not (ps.has_atom(left) and ps.has_atom(right)):
            print(f"  MISSING: {left} or {right}")
            continue
        for src, tgt in ((left, right), (right, left)):
            key = (src, "SHARES_MATH", tgt)
            if key in existing:
                continue
            try:
                ps.add_relation(src, RelationType.SHARES_MATH, tgt,
                                source="within_family_bridges_q4_test_v1",
                                note=reason)
                existing.add(key)
                added_specs += 1
            except Exception:
                pass
    print(f"  spectral edges added: {added_specs}")

    # Step 4: SHARES_MATH bridges (4 sequence-dp)
    print("\n=== STEP 4: 4 sequence-dp bridges (symmetric SHARES_MATH) ===")
    added_seqdp = 0
    for left, right, reason in SEQDP_BRIDGES:
        if not (ps.has_atom(left) and ps.has_atom(right)):
            print(f"  MISSING: {left} or {right}")
            continue
        for src, tgt in ((left, right), (right, left)):
            key = (src, "SHARES_MATH", tgt)
            if key in existing:
                continue
            try:
                ps.add_relation(src, RelationType.SHARES_MATH, tgt,
                                source="within_family_bridges_q4_test_v1",
                                note=reason)
                existing.add(key)
                added_seqdp += 1
            except Exception:
                pass
    print(f"  sequence-dp edges added: {added_seqdp}")

    post_atoms = len(ps.all_atoms())
    post_rels = sum(1 for _ in ps.iter_all_relations())
    print(f"\n=== WITHIN-FAMILY Q4 BRIDGES v1 SUMMARY ===")
    print(f"atoms: {pre_atoms} -> {post_atoms}  (+{post_atoms - pre_atoms})")
    print(f"relations: {pre_rels} -> {post_rels}  (+{post_rels - pre_rels})")
    print(f"  new T3 atoms: {created}")
    print(f"  spectral SHARES_MATH edges: {added_specs}")
    print(f"  sequence-dp SHARES_MATH edges: {added_seqdp}")
    print(f"  total SHARES_MATH edges added: {added_specs + added_seqdp}")
    print(f"\nDECISION 18 Q4 pre-registered test ready: Exp-Dev re-runs P3-v2.")
    print(f"  Outcome >=2 bisim classes -> B confirmed (within-family pivot)")
    print(f"  Outcome 0 bisim classes -> A confirmed (connected-component + CHTV-1)")
    print(f"  Outcome 1 bisim class -> MIDDLE-BAND inconclusive")


if __name__ == "__main__":
    main()
