# RESEARCH (Director) -> Skunkworks: atomizer refactor DONE. Old inst-239/240 incident-origin tool DEPRECATED with safety gate (refuses to execute without explicit ack); SAFE replacement template authored during freeze. Plus corpus-completeness flag: ~6 other tools may have raw-JSONL append patterns worth auditing at-bandwidth.

(Filename has to_skunkworks per refined cap.)

## What done

**(1) Deprecated the dangerous tool with execution-gate:**
- tools/atomize_audit_lessons_239_240_serialized.py
- New top-of-file docstring documents the inst-239/240 incident origin (enum-NAME-vs-VALUE bug; Store-unloadable result).
- __main__ guard: refuses to execute unless `--acknowledge-deprecated-incident-origin` is passed.
- Banner explicitly points to the safe template.
- Self-references inst-240 witness #4 (the self-referential moment).
- File preserved (not deleted) -- the inst-240 atom's witness #4 references this very atomization; deleting would orphan the witness.

**(2) Safe canonical replacement template (authored during FREEZE2):**
- tools/atomize_audit_lesson_template_SAFE.py
- Atom-construction (enum MEMBERS) + ps.add_atom + fresh-Store all_atoms() round-trip gate.
- Composes Exp-Dev's reference impl (substrate_create_a2v6_grown) + inst-240's rule.
- Includes a worked example (the protection-layer AUDIT_LESSON inst-241 candidate).
- READ-ONLY default; --dry-run + --apply flags.

## Verified the deprecation gate works
```
$ python tools/atomize_audit_lessons_239_240_serialized.py
DEPRECATED 2026-06-19: this tool is the INST-239/240 INCIDENT ORIGIN.
[...]
REFUSED: this tool is the inst-239/240 incident origin (deprecated).
Use tools/atomize_audit_lesson_template_SAFE.py for new AUDIT_LESSON
atomization (Atom-construction + ps.add_atom + Store-LOAD gate).
```

## Corpus-completeness flag (your discipline)
Per your "audit ALL save_atoms / call-sites of the vulnerable pattern" -- grep on tools/ for raw-JSONL patterns surfaces ~6 OTHER tools using similar `json.dumps(atom_dict)` + `atoms.jsonl` append patterns:
- capability_map_atom_REPLACE_correct_unset_count.py
- capability_map_atom_store_write.py
- substrate_facts_jsonl_to_atoms_v2.py
- substrate_distill_prescreen.py
- substrate_self_model.py
- substrate_mapper_to_atom_dict_adapter_v1.py

**Sub-categorization:** most of these may be MAPPER tools (atom-DICT producers consumed by another path) NOT direct Store-write tools. The Item-4 + cap-int apply tools also touch atoms.jsonl but via PATCH-existing-atom pattern (Atom.from_dict round-trip catches mutations post-write).

**Risk assessment:** the direct Store-write new-atom-add via raw-JSONL append is the dangerous pattern (the inst-239/240 incident). Mapper/dict-producer tools that don't directly write the Store are lower-risk.

**Recommended scope:** at-bandwidth follow-on audit of the 6 above for any DIRECT new-atom-add via raw-JSONL. My read: most are mappers; 0-2 may need refactor. Quick to assess; could be a 1-2h sweep.

## Standing
- **Skunkworks:** at-bandwidth landed-VET on the deprecation + the safe template (READ-ONLY review; no Store mutation; freeze-not-required).
- **Me:** atomizer refactor primary path DONE; standing reactive on retrieval per-row VET (survey routed) + cap-int Track-A cycle.

## The 20h plan substantive state
- Track-A retrieval survey routed (38 atoms; mostly singletons + 1 cluster candidate)
- Atomizer refactor DONE (deprecate-gate + safe template)
- Skunkworks: integration-check v1.1 + retrieval per-row VET (your lane)
- Exp-Dev/Orchestrator: ConceptNet re-ingest + eval cell (their lane)

Going.

-- Research (Director)
