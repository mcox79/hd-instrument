"""Promote 24 T3 atoms to T2 per Exp-Dev CELL KP P1 frequency-promotion HARD_PASS.

Per research_to_testbed_exp_dev_MASTER_PLAN T1.3:
"Promote 24 T3->T2 candidates per CELL KP P1 verdict; 30 min ingest; KPI 1844 -> 1868 atoms;
substrate retains 0.75+ macro post-promotion"

Mechanism: for each T3 candidate, create a T2/<name> copy with TIER_2_PRIMITIVE tier;
add SUPERSEDES edge from T2 to T3 (per KP semantics: T2 cortical archetype supersedes
T3 specific algorithm). Original T3 atoms remain (for backward compat with existing
references); T2 versions are the new promoted forms.

Source: data/substrate_index/bench_reports/kp_p1_frequency_promotion_candidates.json
"""
from __future__ import annotations
import sys
import json
import dataclasses
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import Tier, RelationType


CANDIDATES_PATH = Path("data/substrate_index/bench_reports/kp_p1_frequency_promotion_candidates.json")


def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    pre_count = len(ps.all_atoms())
    print(f"pre-promotion: {pre_count} atoms\n")

    cand_data = json.loads(CANDIDATES_PATH.read_text(encoding="utf-8"))
    candidates = cand_data["candidates"]
    print(f"loaded {len(candidates)} candidates from KP P1 verdict\n")

    created = 0
    skipped = 0
    failed = 0
    not_found = 0
    edges_added = 0

    for cand in candidates:
        t3_local = cand["atom"]  # "T3/pca_whitening"
        t3_qid = f"math::{t3_local}"
        if not t3_local.startswith("T3/"):
            print(f"  skip (not T3): {t3_local}")
            continue
        name_part = t3_local[len("T3/"):]
        t2_local = f"T2/{name_part}"
        t2_qid = f"math::{t2_local}"

        t3_atom = ps.get_atom(t3_qid)
        if t3_atom is None:
            print(f"  T3 NOT FOUND: {t3_qid}")
            not_found += 1
            continue

        if ps.has_atom(t2_qid):
            print(f"  T2 already exists: {t2_qid}")
            skipped += 1
            # Still try to add SUPERSEDES edge if missing
        else:
            # Create T2/<name> with same fields but tier promoted
            new_meta = dict(t3_atom.metadata or {})
            new_meta["kp_p1_promotion"] = {
                "from": t3_qid,
                "in_degree": cand.get("in_degree"),
                "n_ref_corpora": cand.get("n_ref_corpora"),
                "ref_corpora": cand.get("ref_corpora", []),
                "verdict": "CELL_KP_P1_HARD_PASS_2026-06-13",
            }
            try:
                t2_atom = dataclasses.replace(
                    t3_atom,
                    id=t2_local,
                    tier=Tier.TIER_2_PRIMITIVE,
                    metadata=new_meta,
                )
                ps.add_atom(t2_atom, source="kp_p1_frequency_promotion_t3_to_t2",
                            note=f"promoted from {t3_qid} per CELL KP P1 (in-deg={cand.get('in_degree')}, {cand.get('n_ref_corpora')} corpora)")
                print(f"  PROMOTED: {t3_qid} -> {t2_qid}")
                created += 1
            except Exception as e:
                print(f"  FAIL promote {t3_qid}: {str(e)[:120]}")
                failed += 1
                continue

        # Add SUPERSEDES edge T2 -> T3 (T2 cortical archetype supersedes T3 specific algorithm)
        try:
            ps.add_relation(t2_qid, RelationType.SUPERSEDES, t3_qid,
                            source="kp_p1_frequency_promotion_t3_to_t2",
                            note="T2 cortical archetype supersedes T3 specific algorithm per KP P1 semantics")
            edges_added += 1
        except Exception as e:
            msg = str(e)[:120]
            if "already" in msg.lower() or "exists" in msg.lower() or "duplicate" in msg.lower():
                pass
            else:
                print(f"  edge fail: {t2_qid} SUPERSEDES {t3_qid}: {msg}")

    post_count = len(ps.all_atoms())
    print(f"\n=== SUMMARY ===")
    print(f"pre-promotion: {pre_count} atoms")
    print(f"post-promotion: {post_count} atoms (+{post_count - pre_count})")
    print(f"created: {created}")
    print(f"skipped (T2 already existed): {skipped}")
    print(f"failed: {failed}")
    print(f"T3 not found: {not_found}")
    print(f"SUPERSEDES edges added: {edges_added}")
    print(f"\nPre-reg KPI: 1844 -> 1868 = +24 atoms")
    target_added = 24
    actual_added = post_count - pre_count
    if actual_added == target_added:
        print(f"  EXACT MATCH: +{actual_added} atoms")
    elif actual_added >= target_added * 0.8:
        print(f"  PASS: +{actual_added} >= 80pct of target +{target_added}")
    else:
        print(f"  PARTIAL: +{actual_added} < 80pct of target +{target_added}")


if __name__ == "__main__":
    main()
