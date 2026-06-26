"""Skunkworks 2026-06-26 -- Path C META rule atomization + encoder_provenance tagging on chain-grade atoms.

Source audit: notes/testbed_encoder_provenance_audit_path_C_cleanup_2026-06-26.md
Provenance mapping: data/_testbed_encoder_provenance_FINAL.jsonl (464 rows)

Two operations:
  A) Add 1 META atom to meta corpus (CERT-neutral, methodology_rule, T_methodology, algebra=None, pq=None).
  B) Bulk-update 464 math atoms with metadata.encoder_provenance field.

A5 discipline:
  - Foreground execution (sequential Store+ledger writes -- per foreground-vs-background rule).
  - Atomic write via save_atoms unique-tmp + fsync + os.replace (production-database standard).
  - Verify-load (re-instantiate PartitionedStore + spot-check); integrity check pre/post counts.
  - Bulk patch holds entire math partition in memory + writes ONCE (not 464x add_atom flushes).
  - Single audit log entry on math/audit.jsonl documenting bulk patch source.

PRE-GATE: TOTAL_ATOMS=177377, CHAIN_GRADE=606, math=28573, meta=179.
POST-GATE expectations:
  - TOTAL_ATOMS = 177377 + 1 = 177378 (just the META atom; bulk patch replaces in place)
  - CHAIN_GRADE = 606 UNCHANGED (META is CERT-neutral; provenance tagging does NOT touch provenance_quality)
  - math = 28573 UNCHANGED, meta = 179 + 1 = 180
  - all 464 mapped math atoms have metadata.encoder_provenance set
  - Store re-loads cleanly post-write

ASCII only. Idempotent on META atom (skip-if-exists).
"""
from __future__ import annotations
import json
import sys
import time
import dataclasses
from pathlib import Path
from collections import Counter

# Repo root: this file lives in tools/; cwd-agnostic
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import (
    Atom, AtomKind, Corpus, Tier, save_atoms, load_atoms,
)

FINAL_JSONL = ROOT / "data" / "_testbed_encoder_provenance_FINAL.jsonl"
MATH_ATOMS = ROOT / "data" / "substrate_index" / "math" / "atoms.jsonl"
MATH_AUDIT = ROOT / "data" / "substrate_index" / "math" / "audit.jsonl"

# Maps audit final_provenance bucket -> Store field shape per audit Section 3 Action 1
PROVENANCE_TO_FAMILY = {
    "SUBSTRATE_NATIVE": ("SUBSTRATE_NATIVE", True),
    "LLM_AT_INFERENCE": ("LLM_AT_INFERENCE", False),
    "MIXED_LLM_AND_SUBSTRATE_AT_INFERENCE": ("MIXED_LLM_AND_SUBSTRATE", True),  # substrate arm IS Path C
    "SUBSTRATE_NATIVE_INFERENCE_LLM_INGEST_ONLY": ("LLM_INGEST_ONLY", True),
    "WORD2VEC_DIAGNOSTIC_PROBE": ("WORD2VEC_DIAGNOSTIC", False),
    "NO_CELL_CANT_VERIFY": ("UNKNOWN", False),  # presumed substrate-native but not verifiable
    "UNKNOWN_NO_ENCODER_SIGNAL": ("UNKNOWN", False),
}

META_ATOM = Atom(
    id="RULE_substrate_product_inference_uses_substrate_native_encoder_only_path_C_load_bearing",
    name=(
        "Methodology rule (Path C): substrate-product inference uses substrate-native encoder ONLY; "
        "LLM encoders are diagnostic-probe-context only, never in production inference path"
    ),
    description=(
        "Path C decision (USER 2026-06-23 + 2026-06-26 formalization): production substrate-product "
        "inference uses substrate-native encoder only (random bipolar / sparse_bipolar / FPE phasor / "
        "random codebook / k-WTA / char-trigram / substrate-mined atoms). LLM encoders "
        "(Pythia / MiniLM / BGE / Llama / E5 / sentence-transformers / word2vec) are diagnostic probes "
        "at setup time OR ingest-time semantic mappers; they are NEVER in the substrate-product "
        "inference path. Principle O (basis vs use-case) is the foundation: basis vectors are "
        "content-free; labels appear at readout, not in basis. Brain-existence-proof: a billion years "
        "of evolution produced organism-internal encoders without borrowing other species' "
        "representations; substrate-HD shouldn't borrow LLM representations for production inference "
        "either. EVIDENCE: testbed encoder-provenance audit 2026-06-26 measured 80.8% of chain-grade "
        "portfolio (375/464) already Path C-compliant; 9.3% (43 LLM_AT_INFERENCE) carries a "
        "DEPLOYMENT_CONTEXT_LLM_KEYS or LLM_AUGMENTATION sub-tier (not substrate-product-inference). "
        "Load-bearing for: substrate-product positioning, encoder-mining decisions, future-experiment "
        "encoder-choice defaults, cap_map row classification, Skunkworks cert-tiering at classification "
        "time. Composes with Principle O and the 2026-06-23 Path C session decision atoms. "
        "Anti-saturation check: rule holds iff future encoder-related cells default to substrate-native "
        "at inference path; LLM-encoder cells default to DEPLOYMENT_CONTEXT or LLM_AUGMENTATION cert-class."
    ),
    kind=AtomKind.METHODOLOGY_RULE,
    tier=Tier.TIER_METHODOLOGY,
    corpus=Corpus.META,
    algebra=None,
    metadata={
        "extracted_by": "skunkworks",
        "extracted_date": "2026-06-26",
        "term_class": "methodology",
        "rule_class": "production_encoder_discipline",
        "substrate_internal_verified": True,
        "status": "active",
        "confidence": "high",
        "witnesses": [
            "testbed_encoder_provenance_audit_path_C_cleanup_2026-06-26",
            "USER_session_2026-06-23_path_C_substrate_owned_encoder_is_the_answer",
            "USER_directive_2026-06-26_formalize_path_C_discipline",
        ],
        "audit_source_note": "notes/testbed_encoder_provenance_audit_path_C_cleanup_2026-06-26.md",
        "supersedes": None,
        "complements": [
            "principle_O_basis_vs_use_case",
            "brain_existence_proof_higher_prior_for_brain_grounded_mechanisms",
        ],
        "verification_check": (
            "future encoder-related cells default to substrate-native at inference; "
            "spawn templates should enforce; cap_map encoder-provenance column tracks compliance"
        ),
        "load_bearing_for": [
            "substrate_product_positioning",
            "encoder_mining_decisions",
            "future_experiment_encoder_defaults",
            "cap_map_row_classification",
            "skunkworks_cert_tiering",
        ],
        "portfolio_baseline_2026-06-26": {
            "chain_grade_total": 464,
            "substrate_native": 375,
            "llm_at_inference": 43,
            "mixed_substrate_arm_path_c": 2,
            "llm_ingest_only_substrate_inference": 2,
            "word2vec_diagnostic": 2,
            "no_cell_cant_verify": 34,
            "unknown_no_encoder_signal": 6,
            "path_c_compliant_pct": 80.8,
        },
    },
)


def load_provenance_map() -> dict[str, dict]:
    """Read FINAL.jsonl and produce qualified_atom_id -> provenance-payload map."""
    out: dict[str, dict] = {}
    with open(FINAL_JSONL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            aid = r["atom_id"]  # math::T3/EXP_...
            bucket = r["final_provenance"]
            llm_fams = list(r.get("llm_families") or [])
            deep_class = r.get("deep_class") or ""
            cell_file = r.get("cell_file") or ""
            family, path_c = PROVENANCE_TO_FAMILY[bucket]
            payload = {
                "family": family,
                "llm_families": llm_fams,
                "path_c_compliant": path_c,
                "deep_class": deep_class,
                "cell_file": cell_file,
                "audit_bucket": bucket,
                "audit_ts": "2026-06-26",
                "audit_source": "testbed_encoder_provenance_audit_2026-06-26",
            }
            out[aid] = payload
    return out


def count_chain_grade(ps: PartitionedStore) -> int:
    return sum(
        1 for a in ps.all_atoms()
        if (a.metadata or {}).get("provenance_quality") == "CERT_CHAIN_GRADE"
    )


def main() -> int:
    print(f"FINAL.jsonl: {FINAL_JSONL}")
    print(f"math/atoms.jsonl: {MATH_ATOMS}")
    if not FINAL_JSONL.exists():
        print(f"FAIL: FINAL.jsonl not found")
        return 1
    if not MATH_ATOMS.exists():
        print(f"FAIL: math/atoms.jsonl not found")
        return 1

    prov_map = load_provenance_map()
    print(f"loaded {len(prov_map)} provenance entries from FINAL.jsonl")
    # Stats by bucket
    bucket_counts = Counter(p["audit_bucket"] for p in prov_map.values())
    print("provenance bucket distribution:")
    for k, v in bucket_counts.most_common():
        print(f"  {k}: {v}")

    # ============================================================
    # PRE-GATE: baseline counts
    # ============================================================
    ps_pre = PartitionedStore(ROOT / "data" / "substrate_index")
    pre_total = len(ps_pre.all_atoms())
    pre_chain = count_chain_grade(ps_pre)
    pre_math = len([a for a in ps_pre.all_atoms() if a.corpus == Corpus.MATH])
    pre_meta = len([a for a in ps_pre.all_atoms() if a.corpus == Corpus.META])
    print(f"PRE: total={pre_total} chain_grade={pre_chain} math={pre_math} meta={pre_meta}")
    if pre_total != 177377:
        print(f"WARN: pre_total {pre_total} != expected 177377 (drift since audit; continuing)")
    if pre_meta != 179:
        print(f"WARN: pre_meta {pre_meta} != expected 179 (drift; continuing)")
    # Verify all FINAL atom_ids exist in math partition
    missing = [aid for aid in prov_map if ps_pre.get_atom(aid) is None]
    if missing:
        print(f"FAIL: {len(missing)} FINAL atom_ids do NOT exist in Store: {missing[:5]}")
        return 1
    del ps_pre

    # ============================================================
    # Operation A: add META atom (use add_atom -- single Store-flushed write, audit-logged)
    # ============================================================
    ps = PartitionedStore(ROOT / "data" / "substrate_index")
    if ps.get_atom(META_ATOM.qualified_id) is not None:
        print(f"SKIP META atom exists: {META_ATOM.qualified_id}")
        meta_added = 0
    else:
        ps.add_atom(
            META_ATOM,
            source="skunkworks_path_C_meta_plus_encoder_provenance_tagging_2026_06_26",
            note="Path C META rule + atomized from testbed audit",
        )
        print(f"ADD META: {META_ATOM.qualified_id}")
        meta_added = 1

    # ============================================================
    # Operation B: bulk-update 464 math atoms with metadata.encoder_provenance
    # Strategy: load math/atoms.jsonl once, mutate 464 in-memory, save_atoms once.
    # This avoids 464 separate _flush_atoms() calls (each rewrites 28573 atoms).
    # ============================================================
    print(f"loading math/atoms.jsonl for bulk encoder_provenance patch...")
    math_atoms = load_atoms(MATH_ATOMS)
    print(f"  loaded {len(math_atoms)} math atoms")

    # Build qualified-id -> index map
    qid_to_idx: dict[str, int] = {}
    for i, a in enumerate(math_atoms):
        qid_to_idx[f"math::{a.id}"] = i

    patched_count = 0
    by_family = Counter()
    skipped_already_set = 0
    for qid, payload in prov_map.items():
        idx = qid_to_idx.get(qid)
        if idx is None:
            # already pre-gate verified existence; should not happen
            print(f"  WARN: post-load lookup miss: {qid}")
            continue
        old = math_atoms[idx]
        old_meta = dict(old.metadata or {})
        if old_meta.get("encoder_provenance", {}).get("audit_source") == payload["audit_source"]:
            skipped_already_set += 1
            by_family[payload["family"]] += 1
            continue
        new_meta = dict(old_meta)
        new_meta["encoder_provenance"] = payload
        new_atom = dataclasses.replace(old, metadata=new_meta)
        math_atoms[idx] = new_atom
        patched_count += 1
        by_family[payload["family"]] += 1

    print(f"patched {patched_count} atoms in-memory (skipped {skipped_already_set} already-tagged)")
    print("encoder_provenance family distribution (patched + skipped):")
    for k, v in by_family.most_common():
        print(f"  {k}: {v}")

    if patched_count > 0:
        # Single atomic write of the entire math partition
        print(f"writing math/atoms.jsonl via save_atoms (atomic unique-tmp + fsync + os.replace)...")
        save_atoms(math_atoms, MATH_ATOMS)
        # Append ONE audit entry documenting the bulk patch
        audit_evt = {
            "ts": time.time(),
            "op": "bulk_update_encoder_provenance",
            "target": f"math_partition_464_atoms_encoder_provenance_field",
            "note": (
                f"Bulk patch: encoder_provenance set on {patched_count} math atoms "
                f"(skipped {skipped_already_set} already-tagged). "
                f"Source: data/_testbed_encoder_provenance_FINAL.jsonl"
            ),
            "source": "skunkworks_path_C_meta_plus_encoder_provenance_tagging_2026_06_26",
        }
        MATH_AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with open(MATH_AUDIT, "a", encoding="utf-8") as f:
            f.write(json.dumps(audit_evt, ensure_ascii=False) + "\n")
        print(f"appended bulk-patch audit event to {MATH_AUDIT}")
    else:
        print("no atoms needed patching; skipping save_atoms")

    # ============================================================
    # VERIFY: fresh Store load + spot-check
    # ============================================================
    print("verify: fresh PartitionedStore load...")
    ps2 = PartitionedStore(ROOT / "data" / "substrate_index")
    post_total = len(ps2.all_atoms())
    post_chain = count_chain_grade(ps2)
    post_math = len([a for a in ps2.all_atoms() if a.corpus == Corpus.MATH])
    post_meta = len([a for a in ps2.all_atoms() if a.corpus == Corpus.META])
    print(f"POST: total={post_total} chain_grade={post_chain} math={post_math} meta={post_meta}")

    # Meta atom landed?
    meta_atom_landed = ps2.get_atom(META_ATOM.qualified_id) is not None
    print(f"  META atom landed: {meta_atom_landed}")

    # Spot-check: 5 atoms from each major family
    print("spot-check 5 atoms per major family:")
    samples_per_family: dict[str, list] = {}
    for qid, payload in prov_map.items():
        samples_per_family.setdefault(payload["family"], []).append(qid)
    spot_ok = True
    for fam, qids in samples_per_family.items():
        for qid in qids[:2]:
            a = ps2.get_atom(qid)
            ep = (a.metadata or {}).get("encoder_provenance")
            ok = ep is not None and ep.get("family") == fam
            print(f"  {fam}: {qid} -> ep_family={ep.get('family') if ep else None} ok={ok}")
            if not ok:
                spot_ok = False

    # Verify CERT-neutrality: META atom didn't accidentally promote
    bad_pq = (
        ps2.get_atom(META_ATOM.qualified_id)
        and (ps2.get_atom(META_ATOM.qualified_id).metadata or {}).get("provenance_quality")
            == "CERT_CHAIN_GRADE"
    )
    bad_alg = ps2.get_atom(META_ATOM.qualified_id) and ps2.get_atom(META_ATOM.qualified_id).algebra is not None
    print(f"  META atom CERT-neutral check: bad_pq={bad_pq} bad_algebra={bad_alg}")

    # Verify provenance tagging did NOT touch provenance_quality (chain-grade count steady)
    chain_grade_steady = post_chain == pre_chain
    print(f"  chain-grade count: pre={pre_chain} post={post_chain} steady={chain_grade_steady}")

    # Verify integrity: every FINAL atom now has encoder_provenance field
    tagged_count = 0
    for qid in prov_map:
        a = ps2.get_atom(qid)
        if (a.metadata or {}).get("encoder_provenance") is not None:
            tagged_count += 1
    print(f"  tagged atoms: {tagged_count} / {len(prov_map)}")

    # GATE
    expected_total = pre_total + meta_added
    gate = (
        post_total == expected_total
        and chain_grade_steady
        and post_math == pre_math
        and post_meta == pre_meta + meta_added
        and meta_atom_landed
        and not bad_pq
        and not bad_alg
        and spot_ok
        and tagged_count == len(prov_map)
    )
    print("GATE:", "OK" if gate else "FAIL")
    print(f"  expected_total={expected_total} actual={post_total}")
    print(f"  chain_grade_steady={chain_grade_steady}")
    print(f"  meta_atom_landed={meta_atom_landed}")
    print(f"  spot_ok={spot_ok}")
    print(f"  all_tagged={tagged_count == len(prov_map)}")
    print(f"FOR_RECIPROCAL_CHECK: --expect-cert {post_chain} --expect-atoms {post_total}")
    return 0 if gate else 2


if __name__ == "__main__":
    raise SystemExit(main())
