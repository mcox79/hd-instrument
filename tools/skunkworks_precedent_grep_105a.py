"""SKUNKWORKS DECISION 105a -- precedent-grep gate for the 3 needs_review candidates.
Question (Director ruling): does the substrate maintain OTHER (base, base_atom) or
operator/process pairs as DISTINCT atoms with DIFFERENT relations (= architectural
operator/sub_op layering)? If NO precedent -> default MERGE. If YES -> layering is
architectural; the 3 stay distinct.
Read-only. NO LLM. ASCII only.
"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.substrate_index.partition import PartitionedStore
from backend.substrate_index.schema import RelationType

REL_SET = [RelationType.DEPENDS_ON, RelationType.USES, RelationType.INSTANCE_OF,
           RelationType.SPECIALIZES, RelationType.DUAL, RelationType.RELATES]

def base_of(aid):
    # short name after last '/'
    return aid.split("/")[-1]

def outset(ps, qid):
    s = {}
    for rt in REL_SET:
        try:
            ns = ps.out_neighbors(qid, rt) or set()
            for n in ns:
                s.setdefault(rt.name, set()).add(n)
        except Exception:
            pass
    return s

def main():
    ps = PartitionedStore(Path("data/substrate_index"))
    all_atoms = list(ps.all_atoms())
    by_base = {}
    kinds = {}
    for a in all_atoms:
        b = base_of(a.id)
        by_base.setdefault(b, []).append(a)
        k = a.kind.value if hasattr(a.kind, "value") else str(a.kind)
        kinds[k] = kinds.get(k, 0) + 1

    print("=== kind distribution across substrate ===")
    for k, c in sorted(kinds.items(), key=lambda x: -x[1]):
        print(f"  {k}: {c}")

    # 1) all atoms whose short-name ends in _atom, and whether a non-_atom counterpart exists
    print("\n=== (A) atoms with short-name ending in '_atom' + counterpart check ===")
    atom_suffixed = sorted([base_of(a.id) for a in all_atoms if base_of(a.id).endswith("_atom")])
    atom_suffixed = sorted(set(atom_suffixed))
    print(f"count of distinct '_atom'-suffixed short-names: {len(atom_suffixed)}")
    distinct_layering = []
    dup_2cycle = []
    no_counterpart = []
    for b in atom_suffixed:
        base = b[:-5]  # strip _atom
        # find counterpart short-name == base in any tier/corpus
        suffixed_atoms = [a for a in all_atoms if base_of(a.id) == b]
        base_atoms = [a for a in all_atoms if base_of(a.id) == base]
        if not base_atoms:
            no_counterpart.append(b)
            continue
        # examine relation between the suffixed and base atom (pick T3 if multiple)
        sa = suffixed_atoms[0]
        ba = base_atoms[0]
        sa_out = outset(ps, sa.qualified_id)
        ba_out = outset(ps, ba.qualified_id)
        sa_to_ba = any(ba.qualified_id in v for v in sa_out.values())
        ba_to_sa = any(sa.qualified_id in v for v in ba_out.values())
        sa_kind = sa.kind.value if hasattr(sa.kind, "value") else str(sa.kind)
        ba_kind = ba.kind.value if hasattr(ba.kind, "value") else str(ba.kind)
        # distinct relations beyond the mutual link?
        sa_others = sorted({n for v in sa_out.values() for n in v} - {ba.qualified_id})
        ba_others = sorted({n for v in ba_out.values() for n in v} - {sa.qualified_id})
        rel = f"sa->ba={sa_to_ba} ba->sa={ba_to_sa}"
        cyc = sa_to_ba and ba_to_sa
        record = (b, base, sa.qualified_id, ba.qualified_id, sa_kind, ba_kind, rel,
                  len(sa_others), len(ba_others), cyc, sa.description[:60] if sa.description else "",
                  ba.description[:60] if ba.description else "")
        if cyc:
            dup_2cycle.append(record)
        else:
            distinct_layering.append(record)

    print(f"\n  -- pairs forming a MUTUAL 2-CYCLE (duplicate signature): {len(dup_2cycle)}")
    for r in dup_2cycle:
        print(f"    {r[2]} <-> {r[3]} | kinds={r[4]}/{r[5]} | {r[6]} | descSame? sa='{r[10]}' ba='{r[11]}'")
    print(f"\n  -- pairs NOT a 2-cycle (candidate DISTINCT layering): {len(distinct_layering)}")
    for r in distinct_layering:
        print(f"    {r[2]} & {r[3]} | kinds={r[4]}/{r[5]} | {r[6]} | sa_other_edges={r[7]} ba_other_edges={r[8]}")
    print(f"\n  -- '_atom'-suffixed with NO non-suffixed counterpart: {len(no_counterpart)}")
    for b in no_counterpart[:40]:
        print(f"    {b}")

    # 2) operator/process pairs: X_decoder vs X_decoding, X_er vs X_ing (heuristic)
    print("\n=== (B) operator-object vs process pairs (decoder/decoding style) ===")
    shortnames = set(by_base.keys())
    pairs = []
    for sn in sorted(shortnames):
        # decoder/decoding
        if sn.endswith("_decoder"):
            stem = sn[:-len("_decoder")]
            alt = stem + "_decoding"
            if alt in shortnames:
                pairs.append((sn, alt))
        if sn.endswith("er") and (sn[:-2] + "ing") in shortnames:
            pairs.append((sn, sn[:-2] + "ing"))
    pairs = sorted(set(pairs))
    print(f"candidate object/process pairs: {len(pairs)}")
    for a, b in pairs:
        print(f"    {a} / {b}")

if __name__ == "__main__":
    main()
