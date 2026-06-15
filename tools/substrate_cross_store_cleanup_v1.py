"""DECISION 105c -- cross-store cleanup primitive (reusable). When PartitionedStore.remove_atom deletes atom X, it cascades within-store relations + cross-store relations where X is the SOURCE (src_id = X local id), and pops the _cross_in index. BUT cross-store relations where X is the TARGET are stored in OTHER stores as (local_src, rel_type, X_qualified_id) and DANGLE after the delete (the 101b em_algorithm experience: 5 dangling cross-store edges cleaned manually). This primitive scans ALL partition stores for any relation referencing the deleted atom (in ANY id-form: local / qualified / short -- robust to the 28th-finding namespace fragmentation) as src OR tgt, and removes them via the public Store.remove_relation.

Usage:
  from tools.substrate_cross_store_cleanup_v1 import cross_store_cleanup
  ps.remove_atom(qid)                      # within-store cascade + cross-source + index pop
  cleaned = cross_store_cleanup(ps, qid, execute=True)   # cross-store-target dangling cleanup

Default execute=False = DRY RUN (report dangling, mutate nothing) -- safe for pre-check.
ASCII; `--smoke` runs a mock-based self-test (no real-substrate mutation)."""
from __future__ import annotations
import sys
from pathlib import Path
from typing import List, Tuple
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))


def _idforms(qualified_id: str) -> set:
    """All id-forms a relation tuple might use to reference this atom: qualified, local, short."""
    q = str(qualified_id)
    forms = {q}
    if "::" in q: forms.add(q.split("::", 1)[1])          # corpus::local -> local
    forms.add(q.split("::")[-1].split("/")[-1])           # short (last segment)
    forms.add(q.split("/")[-1])                            # tail
    return {f for f in forms if f}


def find_cross_store_dangling(ps, deleted_qualified_id: str) -> List[Tuple[str, str, str, str]]:
    """Return [(corpus_value, src, rel_type_str, tgt)] for relations in ANY store that still reference
    the deleted atom (any id-form) as src or tgt. Read-only."""
    forms = _idforms(deleted_qualified_id)
    out = []
    for corpus, store in ps._stores.items():
        cv = getattr(corpus, "value", str(corpus))
        for (s, rt, t) in list(store._all_relations):
            if s in forms or t in forms:
                out.append((cv, s, rt, t))
    return out


def cross_store_cleanup(ps, deleted_qualified_id: str, execute: bool = False) -> List[Tuple[str, str, str, str]]:
    """Find (and if execute=True, remove) dangling relations referencing the deleted atom across ALL stores.
    Returns the list of dangling refs found. execute=False is a safe DRY RUN (no mutation)."""
    from backend.substrate_index.schema import RelationType
    dangling = find_cross_store_dangling(ps, deleted_qualified_id)
    if not execute:
        return dangling
    for corpus, store in ps._stores.items():
        cv = getattr(corpus, "value", str(corpus))
        for (cv2, s, rt, t) in [d for d in dangling if d[0] == cv]:
            try:
                store.remove_relation(s, RelationType(rt), t)
            except Exception:
                # fallback: direct discard + flush (per schema-gotcha: some rel_type strings may not map)
                store._all_relations.discard((s, rt, t))
                if hasattr(store, "_flush_relations"):
                    store._flush_relations()
    # drop the cross-store index entry defensively
    try:
        ps._cross_in.pop(deleted_qualified_id, None)
    except Exception:
        pass
    return dangling


# ----------------------------------------------------------------------------- smoke test (mock; no real substrate)
class _MockStore:
    def __init__(self): self._all_relations = set(); self.flushed = False
    def remove_relation(self, s, rt, t):
        self._all_relations.discard((s, getattr(rt, "value", str(rt)), t)); self.flushed = True
    def _flush_relations(self): self.flushed = True


class _MockCorpus:
    def __init__(self, v): self.value = v


class _MockPS:
    def __init__(self, stores): self._stores = stores; self._cross_in = {}


def _smoke():
    # Scenario: atom math::T3/expectation_maximization deleted. A concept-store relation references it as TARGET
    # (concept::cap_x USES math::T3/expectation_maximization) -> stored in concept store as (cap_x, USES, qualified).
    # Also a meta-store relation references it by SHORT form (namespace fragmentation). Both must be found + removed.
    math = _MockStore(); concept = _MockStore(); meta = _MockStore()
    deleted = "math::T3/expectation_maximization"
    concept._all_relations.add(("cap_x", "USES", "math::T3/expectation_maximization"))   # cross-store, qualified target
    concept._all_relations.add(("cap_y", "RELATES", "concept::other"))                    # unrelated, must survive
    meta._all_relations.add(("rule_z", "DEPENDS_ON", "expectation_maximization"))         # short-form ref (fragmentation)
    ps = _MockPS({_MockCorpus("math"): math, _MockCorpus("concept"): concept, _MockCorpus("meta"): meta})

    dry = cross_store_cleanup(ps, deleted, execute=False)
    assert len(dry) == 2, "dry-run should find 2 dangling (qualified + short), found %d: %s" % (len(dry), dry)
    assert all(("expectation_maximization" in d[1] or "expectation_maximization" in d[3]) for d in dry)
    assert concept._all_relations and meta._all_relations  # dry run mutated nothing
    n_before = sum(len(s._all_relations) for s in (math, concept, meta))

    done = cross_store_cleanup(ps, deleted, execute=True)
    assert len(done) == 2
    assert ("cap_x", "USES", "math::T3/expectation_maximization") not in concept._all_relations, "qualified dangling not removed"
    assert ("rule_z", "DEPENDS_ON", "expectation_maximization") not in meta._all_relations, "short dangling not removed"
    assert ("cap_y", "RELATES", "concept::other") in concept._all_relations, "unrelated relation wrongly removed"
    n_after = sum(len(s._all_relations) for s in (math, concept, meta))
    assert n_after == n_before - 2, "expected exactly 2 removed (%d -> %d)" % (n_before, n_after)
    assert concept.flushed and meta.flushed
    print("[smoke] PASS: dry-run found 2 dangling (qualified + short id-forms); execute removed exactly those 2; unrelated preserved; flushed", flush=True)


if __name__ == "__main__":
    if "--smoke" in sys.argv or "--self-test" in sys.argv:
        _smoke()
    else:
        print("cross-store cleanup primitive. import cross_store_cleanup / find_cross_store_dangling. run --smoke to self-test.", flush=True)
