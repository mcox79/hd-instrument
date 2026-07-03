# Design arc: substrate open-vocabulary AtomKind + RelationType refactor

**Date filed:** 2026-07-03
**Filer:** hdi_testbed (integrator dispatch during Blocker A/B unblock)
**Composes with:** `[[project_substrate_open_relation_vocabulary_no_closed_enum_USER_2026-07-03]]`,
`[[project_user_strategic_vision_self_improvement_portal_core_mathematics_USER_2026-06-22]]`,
`[[feedback_substrate_knows_almost_nothing_no_general_knowledge_ingest_yet_USER_LOCKED_REPEATED_2026-07-02]]`
**Status:** DESIGN NOTE (not scheduled; awaits strategic slotting)
**Est. scope:** 4-8h implementation + 2-4h migration + verification

---

## Trigger

Two mid-Testbed-cycle discoveries during 2026-07-03 Blocker A/B unblock:

1. **AtomKind closed-enum drift.** Atomize tools have been writing 58 distinct `kind`
   values into `data/substrate_index/**/atoms.jsonl` that are NOT declared in
   `backend/substrate_index/schema.py::AtomKind`. Full census (76 orphan atoms
   across the 58 kinds) at scratchpad `tool-results/bkjviy2jc.txt`. Each surfaces
   as `ValueError` blocking `PartitionedStore.all_atoms()` -> blocks BGE cache
   `retrieve_cache.rebuild_index_cached()` (retrieve_cache.py:56). The codebase
   has ~15 prior "orphan-kind recovery" post-hoc enum adds (established fire-drill
   pattern). Today's dispatch swept 58 more.

2. **RelationType closed-enum default-fallthrough.** `substrate_mapper_to_atom_
   dict_adapter_v1.py` hard-coded `rel_type: "DEPENDS_ON"` for every dep,
   collapsing Wikidata P31/P279/P361 to monotype. The predicate WAS preserved
   in `algebra_dict.predicate` upstream — adapter just ignored it. Cheap fix
   maps three PIDs to existing seed-vocab entries (INSTANCE_OF/IS_A/PART_OF).
   35+ additional Wikidata core properties (P31, P279, P361, P17 country, P625
   coordinates, P527 has_part, ...) are TECH DEBT: baking them into RelationType
   entrenches closed-enum. See `WIKIDATA_PID_TO_REL_TYPE` in the adapter for the
   current 3-entry seed.

3. **(Bonus discovery)** Author-tool drift beyond enums: 98 atoms use `atom_id`
   instead of `id`; 103 missing `name`/`description`; 12 missing `corpus`.
   Testbed added defensive skip-with-count in `load_atoms` today; TECH DEBT.

---

## Design principle (USER 2026-07-03)

Substrate should NEVER refuse to store a triple because its label is not in a
closed vocab. Relation vocabulary should be substrate atoms — a REL_TYPE is
itself a first-class atom (kind=RELATION_TYPE_DEFINITION), referenced by
`Relation.rel_type` as a qualified atom_id. Same principle for AtomKind: kinds
are meta atoms in the META partition (kind=ATOM_KIND_DEFINITION or similar),
referenced by `Atom.kind` as a qualified atom_id.

Brain-analog rationale: hippocampal one-shot novel role-filler binding (per
brain-function-best-in-class reference standard) does not consult a closed
vocab; it binds arbitrary role atoms to arbitrary filler atoms on first
encounter. Closed enums reject on unseen role — brain does not.

---

## Sketch

### Schema changes

```python
# backend/substrate_index/schema.py

# Relation.rel_type becomes str (atom-id reference into meta partition):
@dataclass(frozen=True)
class Relation:
    src_id: str
    tgt_id: str
    rel_type: str  # was RelationType enum; now qualified atom_id (e.g. "meta::rel/instance_of")
    metadata: dict = field(default_factory=dict)

# Atom.kind becomes str (atom-id reference):
@dataclass(frozen=True)
class Atom:
    ...
    kind: str = "meta::kind/primitive"  # was AtomKind enum; qualified atom_id

# Backward-compat readers accept legacy enum-value strings via a registry:
_LEGACY_KIND_ALIASES = {
    "primitive": "meta::kind/primitive",
    "amendment_record": "meta::kind/amendment_record",
    ...  # all 39+58 legacy values
}
_LEGACY_RELTYPE_ALIASES = {
    "DEPENDS_ON": "meta::rel/depends_on",
    "INSTANCE_OF": "meta::rel/instance_of",
    ...
}
```

### Registry bootstrap

- Meta partition seeded with atoms for each legacy AtomKind + RelationType value.
- New kinds/reltypes auto-created at write time via
  `Store.ensure_kind(kind_slug)` / `Store.ensure_reltype(rel_slug)`.
- No enum edit ever required to introduce a new label.

### Migration path

1. Add `str`-typed variants alongside enum-typed with dual-read (backward compat).
2. Seed meta partition with legacy atoms (one per current enum value).
3. Sweep-migrate `data/substrate_index/**/atoms.jsonl`: normalize `kind` strings to
   qualified atom_ids; sweep-migrate `Relation` files similarly.
4. Deprecate enum-only path; readers accept both for 1 release; then remove enum.
5. Delete `_load_atoms_skip_count` drift shim once author-tools migrated.

### Author-tool hardening (composes)

Existing 98 `atom_id`-instead-of-`id` + 103 missing-name/description atoms
demonstrate the same "raw-dict at write time" problem. Migration includes:
- `save_atoms` already validates roundtrip via `validate_atom_roundtrip` (2026-06-27
  Skunkworks harden). Enforce all writers through `Store.add_atom()` not raw
  jsonl append.
- Deprecate `_skunkworks_atomize_*.py` raw-dict paths.

---

## Blast radius (est. touch points)

- `backend/substrate_index/schema.py` — the two enum defs + Atom.kind/Relation.rel_type fields
- `backend/substrate_index/store.py`, `partition.py` — reader/writer paths
- `backend/substrate_index/retrieve_cache.py` — BGE cache builders
- 60+ readers across `backend/`, `experiments/`, `tools/` that call
  `AtomKind(...)` / `RelationType(...)` — 4-8h grep+rewrite
- Author-tool sweep (60+ atomize/ratify scripts) — 2-4h re-target through Store API

---

## Sequencing

This is a substrate-schema refactor. Slot when a milestone quiets down:
- NOT during 170K scale re-test (in flight; the sweep-enum-add + adapter fix
  today unblocks it without this arc)
- Composes with the M3 cortex architecture layer (project_M3_cortex_layer_...)
  since cortex may want to introduce new kind literals at learning time

---

## Concrete handoff artifacts (built today)

1. **58-orphan census:**
   `C:\Users\marsh\AppData\Local\Temp\claude\d--AI\02e8b04e-1164-42ee-b96d-ac16726a826a\tool-results\bkjviy2jc.txt`
   (`kind` value + atom count + sample file:line hits)

2. **Adapter cheap fix (uses seed-vocab):**
   `tools/substrate_mapper_to_atom_dict_adapter_v1.py::WIKIDATA_PID_TO_REL_TYPE`
   (3-entry map: P31/P279/P361 -> INSTANCE_OF/IS_A/PART_OF). Full 35-property
   Wikidata core-property expansion requires the open-vocab arc to avoid enum
   entrenchment.

3. **Loader drift shim:**
   `backend/substrate_index/schema.py::load_atoms` skip-with-count for 112 legacy
   raw-dict atoms (98 `atom_id`-not-`id` + 14 missing-critical-field). Diagnostic
   dict `_load_atoms_skip_count` populated. To be removed once open-vocab arc
   migrates + author-tools hardened.

---

## Open questions for USER/Director slotting

- Which comes first: cortex arc + open-vocab together, or open-vocab first as
  substrate-foundation work?
- Does the meta partition ALREADY implicitly hold kind/reltype definitions
  (via METHODOLOGY_RULE atoms), or do we introduce dedicated `RELATION_TYPE_DEFINITION`
  and `ATOM_KIND_DEFINITION` kinds?
- Backward-compat window: is 1-release dual-read acceptable, or migrate atomically?
