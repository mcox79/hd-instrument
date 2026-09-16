---
priority: 145
slug: collapse_the_fourteen_drifted_organ_copies_every_experiments_copy_becomes_an_alias_of_its_hdlab_organ_with_equivalence_proven_per_pair_and_the_one_object_witness_as_the_permanent_gate
status: OPEN
review:
review_text:
---

# PROBLEM: 16 organs exist twice on disk (a copy under experiments/ and the organ under hdlab/), 14 of the copies have drifted and none is an alias; 12 were unknown until pri 139's standing witness counted them (the temporal trio 834-891 lines apart, resolved through a consolidation shim; joint_relation_frontend 491). Every cell or witness that imports a copy measures a phantom. Collapse every copy into an alias of its organ, the way pri 137 (space) and pri 139 (belief) did, equivalence proven per pair, the standing one-object witness as the permanent gate, and give the surviving organ its structure name where pri 142's map has one.

**slug:** `collapse_the_fourteen_drifted_organ_copies_every_experiments_copy_becomes_an_alias_of_its_hdlab_organ_with_equivalence_proven_per_pair_and_the_one_object_witness_as_the_permanent_gate`

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25/26; full text in `notes/problems/README.md`, binding here)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING.** **THE OPENING MOVE: how does the BRAIN do THIS?** One structure, many functions (owner 2026-09-11): a second implementation of the same computation is a defect even when it is identical today, because it stops being identical at the next landing (the space copy drifted four landings; the belief copy hid a phantom witness claim).
> **EVERY COMPONENT MUST BE 100% BRAIN-FOUNDATIONAL** -- a copy may still carry a stand-in the organ dropped (the belief copy carried the spaCy branch); the collapse removes it.
> **RENAME AT CONSOLIDATION TIME (owner 2026-09-16):** when a copy collapses into its organ, the organ takes the structure name pri 142's map assigns, via a module alias for the old name (no mass rename; importers keep working; the old name is deprecated in a comment).
> **WALL-PUSH PROTOCOL:** read `notes/WALL_PUSH_PROTOCOL_owner_motivation_messages.md`.
> **YOUR CELL AND WITNESS MUST RUN GREEN ON THE TREE AS LANDED.** Land after pri 137 and 139 (two of the 16 pairs are theirs).

> ## BRAIN-FOUNDATIONAL CHECKLIST (in order)
> 1. **OPEN.** Run `verification/test_organ_copies_are_one_object.py` and take its pair table (16 pairs; per pair: alias / drifted / unrelated-looking, the diff line count, the importers). For each drifted pair classify every differing hunk: promotion-only, a landing the organ got and the copy did not, a change the copy got and the organ did not (the dangerous class: measure which side is right).
> 2. **REUSE.** pri 137's alias (`experiments/_space_reader.py` as a `sys.modules` alias; never a star-import), pri 139's alias + identity witness + poisoned-import check + E-check (78 non-belief fields byte-identical), pri 139's classifier for shim-resolved pairs (the temporal trio).
> 3. **GENERALIZE.** One collapse procedure applied 14 times: alias, identity witness, equivalence on >= 9 documents per pair (0 mismatches at the live semantics or each mismatch attributed to a hunk with the organ's answer kept), importers repointed (enumerate), the pair's instruments re-measured on the organ (before = copy, after = organ; a moved number reported with its cause).
> 4. **WALL -> DEEPER.** A pair whose copy is RIGHT where the organ is wrong (a change the copy got) is a located defect in the organ: fix the organ, never keep the copy.
> 5. **OPTIMIZE BY MEASUREMENT.** Read-time and import-time before/after (the copies' importers load two modules today).
> 6. **PERFORMANCE vs THE BRAIN + FULL-STACK UPSTREAM.** The product board byte-identical on every model row after the collapse (the copies are not on the live path; the board proves it).
> 7. **ADJACENT.** pri 142 (the names), 137/139 (the precedents), 143/144 (their members may be among the pairs: consolidate the copy first, then the engine).
> 8. **COMPLETION BAR.** Below.

**(PHASE DIAGRAM.)** Nothing to sweep.

## 1. THE PROBLEM IN PLAIN LANGUAGE

Fourteen parts of the reader exist in two versions: the one the reader runs and an older copy in the experiments folder that the measurements still use. The two have drifted apart, in three cases by more than eight hundred lines. So a measurement can pass on the copy and mean nothing for the product, and a solver can 'improve' a copy the reader never runs. Yesterday two such pairs were collapsed (the map reader and the knowledge reader) with a mechanism that makes the old name a transparent alias of the real part and proves the two give the same answers on a set of documents. Do the same fourteen times, prove it fourteen times, re-run the measurements on the real parts, and keep the counting check that found them as a permanent gate so it cannot happen again.

## 2. WHY THIS ONE

It is the fourth step of the owner's consolidation program (2026-09-16) and the one with the widest blast radius: 14 pairs, 12 unknown until yesterday; two of the pairs already yielded a phantom witness claim and a dead lever. It is mechanical (pri 137 and 139 each took under two hours) and it makes pri 143/144's members single.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)

Not a mechanism brief; the structural rule is the owner's. The alias is OUR-INVENTION for the transition.

## 4. MEASURED vs INFERRED

MEASURED (pri 139, 2026-09-16): 16 pairs, 14 drifted, 0 aliased; the temporal trio (temporal_ordering 891, temporal_order_register 847, temporal_ordering_multiframe 834 differing lines, resolved through `hdlab.temporal_model`'s consolidation shim), joint_relation_frontend 491; the belief pair: 51 lines, one phantom witness claim; the space pair: four landings of drift, a dead lever.

INFERRED (verify): that most hunks are promotion-only or landings the copy missed; that at least one pair carries a change the copy got and the organ did not.

## 5. ALREADY TRIED / DO NOT RE-RUN

- pri 137 and 139: done; reuse their exact mechanism and witnesses.
- A star-import re-creates the defect for monkeypatch-based witnesses (pri 137); never.
- The temporal trio's consolidation (2026-09-11) left shims: resolve the pairs through the shim, not around it.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

1. `.venv/Scripts/python.exe verification/test_organ_copies_are_one_object.py` -- the pair table.
2. `sed -n 1,50p experiments/_space_reader.py experiments/_belief_reader.py` -- the two landed aliases (after pri 137/139 land; else their diffs).
3. `notes/STRUCTURE_MAP_2026-09-16.md` -- the structure names for the surviving organs (pri 142).
4. `grep -rln "experiments\._\|from experiments import _" hdlab experiments verification tools | wc -l` -- the importer population.

## 7. THE BAR (can-fail)

1. **Every pair collapsed**: each `experiments/_X.py` is an alias of `hdlab/X.py` (identity under every import spelling), the standing witness green with 16/16 aliased.
2. **Equivalence proven per pair** on >= 9 documents at the live semantics (0 mismatches, or each mismatch attributed to a hunk and the organ's answer kept; a copy that was right = an organ defect fixed).
3. **Every importer repointed and green** (enumerated per pair); every witness that imported a copy re-run on the organ; every moved number reported with its cause; phantom claims retired by name.
4. **No stand-in survives**: the poisoned-import check passes on each organ's path.
5. **Names**: each surviving organ carries its structure name from the map through a module alias for the old name; no importer breaks.
6. **Product board byte-identical** on every model row; read/import time not up (report).

## 8. FILES AND ENTRY POINTS

- `verification/test_organ_copies_are_one_object.py` (pri 139) -- the pair table and the gate.
- `experiments/_space_reader.py`, `experiments/_belief_reader.py` -- the two landed aliases (the template).
- the 14 pairs as the witness lists them; `hdlab/temporal_model.py` and its three shims.
- `notes/STRUCTURE_MAP_2026-09-16.md` (pri 142).

Write ONLY: `experiments/exp_collapse_organ_copies_v1.py` (NEW cell: per-pair equivalence + before/after on each pair's instruments; `get_output_dir` per Q115; `--self-test`), `notes/problems/<slug>/{SOLVED.md, collapse_copies_patch.diff}` (the 14 aliases, the repointed importers, the module aliases for structure names, the witness re-pins -- as unified diffs; never edit hdlab/ or tracked verification files directly). Cap cores: `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0`; one cell at a time; never a delete command (an alias REPLACES a file's content; nothing is deleted).

## DO NOT QUOTE / DO NOT REDO

- Do not quote any number measured through a copy as the product's number until re-measured on the organ.
- Do not re-derive the alias mechanism; copy pri 137/139's.
- 19c corpora are informational only (owner 2026-09-06).
