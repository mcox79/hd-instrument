"""
A5-gated patch: 6 poison atoms with invalid AtomKind values.

Director-authorized 2026-06-28: invalid `kind` strings break PartitionedStore.all_atoms()
load. Patch each by mapping to valid AtomKind enum value, preserving original string
in metadata.cert_class (already mirrored there in all 6 cases).

Patches:
  math line 28688 substrate_property_characterization -> capability_map (AGG chain-grade)
  math line 28689 dispatch_infrastructure_failure     -> experiment_record (seed-7 HF dispatch)
  math line 28690 dispatch_infrastructure_failure     -> experiment_record (seed-13 HF dispatch)
  math line 28691 dispatch_infrastructure_failure     -> experiment_record (seed-19 HF dispatch)
  math line 28692 test_design_failure_dispatch_infra  -> experiment_record (CROSS-SEED AGG HF)
  meta line 248   meta_observation                    -> audit_lesson  (instrumentation observation)

cert_class on each atom already preserves the original semantic descriptor; no metadata move
required. We only mutate the top-level `kind` field.

A5 protocol per file:
  1. PRE-snapshot: count lines, integrity-check JSON parse all lines, capture target line obj
  2. Mutate target line's kind in-memory
  3. Atomic write tmp -> os.replace
  4. POST-verify: reload, count delta = 0, integrity-check all lines, target kind verified,
     PartitionedStore.all_atoms() loads clean.
"""
import json
import os
from pathlib import Path

ROOT = Path("d:/AI/hd-instrument")

PATCHES = [
    # (partition, line_no_1indexed, old_kind, new_kind, atom_id_prefix_for_assert)
    ("math", 28688, "substrate_property_characterization", "capability_map",
     "T3/EXP_substrate_cross_modal_binding_visual_auditory_v1_CROSS_SEED_AGG"),
    ("math", 28689, "dispatch_infrastructure_failure", "experiment_record",
     "T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_7"),
    ("math", 28690, "dispatch_infrastructure_failure", "experiment_record",
     "T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_13"),
    ("math", 28691, "dispatch_infrastructure_failure", "experiment_record",
     "T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_seed_19"),
    ("math", 28692, "test_design_failure_dispatch_infra", "experiment_record",
     "T3/EXP_substrate_pattern_completion_corruption_cliff_v2p2_dense_cliff_grid_CROSS_SEED_AGG"),
    ("meta", 248, "meta_observation", "audit_lesson",
     "META_OBS_replay_cost_dominates_compute_at_N_replay_50_cortex_hippo_handoff"),
]


def patch_partition(partition: str, edits: list):
    """edits = list of (line_no, old_kind, new_kind, id_prefix)"""
    p = ROOT / f"data/substrate_index/{partition}/atoms.jsonl"
    assert p.exists(), f"missing: {p}"

    with open(p, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    pre_count = len(lines)
    print(f"[A5 {partition}] PRE count: {pre_count}")

    # PRE integrity-check all lines
    for i, ln in enumerate(lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"PRE integrity fail {partition} line {i+1}: {e}")
    print(f"[A5 {partition}] PRE all {pre_count} lines parse OK")

    # Mutate target lines
    any_mutation = False
    for line_no, old_kind, new_kind, id_prefix in edits:
        idx = line_no - 1
        obj = json.loads(lines[idx])
        current_kind = obj.get("kind")
        if current_kind == new_kind:
            print(f"[A5 {partition}] line {line_no}: ALREADY PATCHED (kind={new_kind!r}) - skipping")
            assert obj.get("id", "").startswith(id_prefix), f"line {line_no}: id prefix mismatch even though already patched"
            continue
        assert current_kind == old_kind, f"line {line_no}: expected old_kind={old_kind!r} got {current_kind!r}"
        assert obj.get("id", "").startswith(id_prefix), f"line {line_no}: id prefix mismatch: {obj.get('id','')[:80]}"
        # Preserve original kind string as kind_legacy_poison metadata for cert-trail
        md = obj.setdefault("metadata", {})
        existing_cc = md.get("cert_class")
        md["kind_legacy_poison"] = old_kind
        md["kind_patched_by"] = "skunkworks_patch_poison_atomkinds_2026-06-28"
        md["kind_patched_date"] = "2026-06-28"
        if existing_cc != old_kind:
            print(f"[A5 {partition}] line {line_no}: NOTE cert_class={existing_cc!r} != old_kind={old_kind!r} (preserved both: cert_class stays, kind_legacy_poison records old kind)")
        obj["kind"] = new_kind
        lines[idx] = json.dumps(obj, ensure_ascii=True)
        any_mutation = True
        print(f"[A5 {partition}] line {line_no}: kind {old_kind!r} -> {new_kind!r} (cert_class preserved)")

    if not any_mutation:
        print(f"[A5 {partition}] no mutations needed; skipping write")
        return

    # Atomic write
    out_text = "\n".join(lines) + "\n"
    tmp = p.with_suffix(p.suffix + ".tmp_a5_patch")
    with open(tmp, "w", encoding="utf-8") as f:
        f.write(out_text)
        f.flush()
        os.fsync(f.fileno())
    os.replace(str(tmp), str(p))
    print(f"[A5 {partition}] atomic-write OK")

    # POST verify
    with open(p, "r", encoding="utf-8") as f:
        post_lines = f.read().splitlines()
    post_count = len(post_lines)
    assert post_count == pre_count, f"count drift: {pre_count} -> {post_count}"
    for i, ln in enumerate(post_lines):
        if not ln.strip():
            continue
        try:
            json.loads(ln)
        except Exception as e:
            raise RuntimeError(f"POST integrity fail {partition} line {i+1}: {e}")
    # Verify all patched lines
    for line_no, old_kind, new_kind, id_prefix in edits:
        obj = json.loads(post_lines[line_no - 1])
        assert obj.get("kind") == new_kind, f"POST line {line_no}: kind {obj.get('kind')!r} != {new_kind!r}"
        assert obj.get("id", "").startswith(id_prefix)
    print(f"[A5 {partition}] POST verify OK: count={post_count}, all patched kinds confirmed")


def main():
    print("=" * 70)
    print("A5 PATCH 6 POISON ATOMS (Director-authorized 2026-06-28)")
    print("=" * 70)

    by_partition = {}
    for partition, line_no, old_kind, new_kind, id_prefix in PATCHES:
        by_partition.setdefault(partition, []).append((line_no, old_kind, new_kind, id_prefix))

    for partition, edits in by_partition.items():
        patch_partition(partition, edits)

    print()
    print("=" * 70)
    print("FINAL: PartitionedStore.all_atoms() load test")
    print("=" * 70)
    from backend.substrate_index.partition import PartitionedStore
    S = PartitionedStore(Path("d:/AI/hd-instrument/data/substrate_index"))
    atoms = list(S.all_atoms())
    print(f"CLEAN LOAD - atoms: {len(atoms)}")
    print("DONE")


if __name__ == "__main__":
    main()
