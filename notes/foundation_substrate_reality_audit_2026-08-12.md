# Foundation substrate reality audit (2026-08-12, Director, audit-only)

All numbers below were measured directly against files on disk / by running code in this
session on `D:/AI/hd-instrument`, branch `dataprep/mcguffey-graded-corpus`. No estimates.

## 1. The real knowledge store

Location: `data/foundation/reading_grounding_v1/` (22 MB). Sibling dirs
`reading_grounding_v1_smoke*`, `*_post_bootstrap_control_copy` are smoke/control copies, not
the live foundation.

Format: a directory snapshot written/read by `hdlab/foundation_persistence.py`
(`save_foundation`/`load_foundation`; `FORMAT_VERSION = 1`):
- `store/store_meta.json`, `store/store_tensors.npz`, `store/store_facts.json` -- an
  `hdlab.hd_fact_store.HDFactStore` (n_dim=2048, seed=1001, `use_index=True`).
- `concept_space.npz` -- an `hdlab.reading_grounding_loop.ConceptSpace` (per-lemma
  quantized context-bundle), **4322 lemmas** measured (`len(npz['lemmas'])`).
- `library_pending.json` / `library_pending_ctx.npz` -- in-progress (not-yet-grounded)
  `hdlab.grounding_acquisition_loop.Library` items, PENDING only.
- `manifest.json` -- growth curve (176 passes) + counters.

Counts, measured directly from `store/store_facts.json` (7966 rows, all `status=ACTIVE`,
no SUPERSEDED/DROPPED/FLAGGED present) and cross-checked against `manifest.json`:
- **n_facts = n_live_facts = 7966**
- relation breakdown: `KNOWN_WORD` = 4422 (word-is-known assertions), `GROUNDED_MEANING`
  = 3544 (word-sense-grounding assertions) -- sums to 7966.
- of the 3544 GROUNDED_MEANING facts: **2328 self-grounded** (subject==object, a root
  anchor / "word means itself") and **1216 cross-grounded** (subject!=object, a genuine
  word->concept claim).
- seed vocabulary (`known_seed` in manifest.json): 878 words.
- pending (not yet grounded): `n_pending_library_items` = 8130 (manifest.json, current).
- `n_occurrences_seen` = 26123 sentence-observations across 176 passes.

Modules that read/write it: `hdlab/hd_fact_store.py` (HDFactStore: store/query/ingest-vet),
`hdlab/reading_grounding_loop.py` (ConceptSpace, Library, process_sentence/checkpoint,
constructs the store), `hdlab/foundation_persistence.py` (save/load, sidecar only -- adds no
methods to the reused classes, verified by reading the file), `hdlab/gap_detector.py`
(novelty gate, read-only consumer of `store.live_facts()`), `hdlab/gap_driven_reader.py`
(self-directed reading prioritization, read-only consumer of `GapDetector`/`store.query`).
Written by: `experiments/exp_reading_grounding_loop_cycle1_v1.py` and
`exp_reading_grounding_loop_cycle2_v1.py` (both call `foundation_persistence.load_store` /
`load_manifest` to resume, `save_foundation` to persist).

## 2. Query interface

**No operator-facing CLI or tool exists.** Grepped `tools/` (no foundation/gap/fact query
script) and the whole repo for `load_foundation(` -- the only call sites are inside
`hdlab/foundation_persistence.py` itself (its own self-tests/`__main__`). The only reachable
interface is the Python API, callable from any script (experiment cells do this; an operator
would have to write one too):

```python
from hdlab.foundation_persistence import load_foundation
state = load_foundation('data/foundation/reading_grounding_v1')
state.store.query('genom', 'GROUNDED_MEANING')
```

Demonstrated live, this session, real output and timing:
- `import hdlab.foundation_persistence` (first-time torch/module import): **12.636 s**
- `load_foundation(...)`: **1.156 s** (7966 facts, use_index=True)
- `store.query('genom', 'GROUNDED_MEANING')` -> `[{'fid': 7958, 'object': 'genom',
  'source': 'reading:bio_new', 'trust': 'TRUST_MID', ...}]`, **47.8 ms** (cold), subsequent
  calls (`dolly`, `mrna`) **7-10 ms**; `nonexistent_word_xyz` -> `[]`, **0.0 ms**.
- Query signature is exact `(subject, relation)` -- not free-text / fuzzy "what do we know
  about X"; the caller must already know the relation name (`KNOWN_WORD` vs
  `GROUNDED_MEANING`).

Finding: a working query path exists but is **reachable only from inside a Python process
that imports the module** -- no CLI, no operator command. This is a finding, not a failure.

## 3. Relation to other stores (measured, not inferred)

- **Grown foundation** (`data/foundation/reading_grounding_v1/`, above) = the actual
  KNOWLEDGE substrate. Current, actively written (2 in-flight agents per manifest growth
  curve through pass 175, 2026-08-12).
- **`hdlab/hd_fact_store.py`** is not a separate store -- it is the storage ENGINE the
  foundation directory persists an instance of. `data/capability_registry.jsonl` row 6
  (`hd_fact_store`) is tagged `wired_prior_to_07-25_audit`, i.e. registered before the
  2026-08-11/12 `gap_detector.py` / `foundation_persistence.py` / `gap_driven_reader.py`
  additions. **None of those three newer modules has a capability_registry entry** (grepped
  all rows for `foundation|gap_detector|hd_fact_store|reading_grounding`, matches are rows
  5-8,15,22,25,56,59,64,104-106; none name gap_detector.py, foundation_persistence.py, or
  gap_driven_reader.py) -- an open WIRE-or-SHELVE gap per this project's own registry
  discipline, not something this audit resolves.
- **Director notes index** (`tools/director_kb_query.py`, `data/substrate_director_kb_v1/`,
  `CharTrigramEncoder`) -- confirmed a DIFFERENT system: queries Director's own notes/
  preregs/atoms.jsonl bookkeeping (`data/substrate_director_kb_v1/{E.pt,R.pt,W.pt,
  atoms.jsonl,entities.jsonl,relations.jsonl}`), not the reading-grown foundation. Bookkeeping,
  not knowledge.
- **`data/substrate_index/`** -- same family as above (atoms.jsonl, benchmark_corpus_*.jsonl,
  canonical_alias_map.jsonl, coevolve*_ACCEPT_edges.jsonl) -- the substrate-KB used by
  `tools/substrate_query.sh`. Bookkeeping/dedup index over prior experiment work, not the
  knowledge foundation.
- **Capability registries** (`data/capability_registry.jsonl`) -- bookkeeping (what's
  wired/shelved), not knowledge content.

So: ONE knowledge substrate exists (`data/foundation/reading_grounding_v1/`, backed by
HDFactStore); everything else found (director KB, substrate_index, capability registry) is
process bookkeeping over experiment/notes history, unrelated in content to what the reading
loop has grounded.

## 4. Speed / dominant cost

Both prior claims checked directly against code + live measurement on the 7966-fact store:

- **GapDetector.refresh()** (rebuild its own content-keyed codebook from
  `store.live_facts()`): measured **0.345 s** at 7966 facts. Cheap; called once per
  `checkpoint()` (i.e. once per pass when something newly grounds), `reading_grounding_loop.py`
  line 304 -- NOT per-word.
- **GapDetector.familiarity()** (one novelty-margin probe): calls
  `hdlab.cleanup_family.iterative_attractor` (`gap_detector.py` line 111), which does a
  softmax-weighted match against the ENTIRE codebook every call, not just at refresh --
  measured **~180 ms/call** at 7966 facts (30-call loop, 5.404 s total). This IS the O(n_facts)
  cost, paid PER CANDIDATE WORD in `process_sentence` (`reading_grounding_loop.py` line 265,
  `if not is_gap(state, lemma): continue`), not amortized by refresh's cache. At ~180 ms/call,
  ~440 candidate probes/chunk reproduces the previously-flagged "~80 s/chunk at ~8k facts" --
  consistent with, not refuted by, this measurement.
- **The O(1) exact-match index**: `HDFactStore._sr_index` (content-hash bucket on the
  (subject,relation) signature, `hd_fact_store.py` lines 124-131, 237-252), gated by
  `use_index` (default `False`, `hd_fact_store.py` line 116). Confirmed **ON** for the live
  foundation store (`store_meta.json`: `"use_index": true`) -- so it is not "switched off" as
  a config flag. But `grep use_index hdlab/reading_grounding_loop.py` and
  `hdlab/gap_detector.py` returns **zero matches** -- neither the reading loop's gate
  (`is_gap`/`GapDetector.familiarity`) nor GapDetector itself ever calls
  `store.query()`/`_sr_index`. `store.query(lemma, 'KNOWN_WORD')` would answer "already
  known" in O(1) (measured 7-10 ms end-to-end incl. cleanup) for any exact re-encounter, but
  the gate path always pays the full attractor scan instead. **Both parts of the prior claim
  verified**: the per-probe scan is genuinely O(n_facts) and dominates chunk time; a working
  O(1) index exists and is enabled on the store, but the gap-detection code path never
  consults it.

## 5. Organized for reuse today?

Attempted end to end, this session: `load_foundation('data/foundation/reading_grounding_v1')`
then `store.query('genom', 'GROUNDED_MEANING')` -- **worked**, returned the grounded fact in
under 50 ms (section 2). So yes, *if* the caller already knows the exact lemma and exact
relation string and is willing to write/run a Python snippet. There is no fuzzy/free-text
"what do we know about X" entrypoint (no encoder-based nearest-lemma search over the store
was found wired to a query function), and no CLI -- an operator today gets an answer only by
authoring a short script against the private Python API, not by running a command.

Separately, `experiments/exp_foundation_validation_harness_v1.py` (commit `71a84d86f`,
pre-reg `preregs/2026-08-12_foundation_validation_harness_v1.md`) ran a 3-claim audit
(correctness / coherence / can-reason via 2-hop chained `store.query()`) against a frozen
snapshot and landed `run_mode=full`, `verdict=HARD_PASS_foundation_validated`
(`verdict_msg`: `claim1=HARD_PASS(gap=0.2533) claim2=HARD_PASS(cohesion=0.4765,contra=0)
claim3=HARD_PASS(mech=1.0,scr=0.0,abl=0.0) smoke_controls_discriminate=True`) -- this is a
landed result on disk, reported here as a fact of what exists, not independently re-verified
by this audit (that re-verification is Director's follow-on work, not part of this report).
