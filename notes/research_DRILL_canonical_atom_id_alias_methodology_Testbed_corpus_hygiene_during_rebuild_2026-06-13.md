# Research drill: canonical atom-id alias methodology for Testbed corpus hygiene during major re-shard

date: 2026-06-13
topic: variant atom IDs across signals (hungarian_assignment vs hungarian_algorithm; chu_liu_edmonds vs chu_liu_edmonds_algo) artificially deflate cross-signal joins; Testbed needs a canonical-id alias map + normalization pass integrated with current major re-shard
budget: ~30 min, 5 web searches, Sonnet lit-scan tier
calibration: lit-scan deflation 0.15-0.25 applied; novel-synthesis cap 0.50; substrate is uncharted regime so prior work informs but does not govern (per [[feedback-no-experiment-design-in-prompts]] + [[feedback-lit-scan-calibration-penalty]])

## (a) HEADLINE

Three production-standard patterns transfer cleanly to Testbed atom-ID hygiene: (1) **Wikidata-style preferred-label + altLabel pattern** — pick one canonical_atom_id per cluster, store all variants as aliases in a single JSON-Lines alias map (`aliases.jsonl`), use earliest-seen-ID-wins or most-cited-wins canonicalization policy; (2) **two-pass dedupe pipeline = blocking (token-prefix) + matching (Jaro-Winkler ≥ 0.92 OR Levenshtein ≤ 2 on the discriminating suffix)** — the literature is unanimous that blocking is ~10× more important than the matching metric, and for short technical identifiers Jaro-Winkler's prefix-emphasis is the right default; (3) **bidirectional resolve-at-read pattern with versioned alias graph** — readers normalize through `alias_to_canonical(id)` on every load, writes always emit canonical, never delete aliases (immutable). The migration leverages the in-flight major re-shard as the atomic-swap window: build the alias map BEFORE the swap, rewrite atoms+relations to canonical form in the new shard directory, swap via the CURRENT-pointer pattern already drilled (research_DRILL_atomic_write_shard_swap_patterns_2026-06-13). For Testbed: 1 file (`data/atom_aliases.jsonl`), 1 lookup module (`tools/canonical_id.py` with in-memory dict), 1 migration script (`tools/migrate_alias_normalize.py`) — no external library needed (splink/dedupe.io are overkill for ~hundreds-to-low-thousands of atoms; py_stringmatching or rapidfuzz for the matching step only). The "we may be first" caveat applies to integration with the substrate atom-graph specifically; the alias-map mechanics themselves are standard.

## (b) Cheap decisive test

On a scratch copy of the current shard (NOT production):
1. Run `tools/extract_variant_clusters.py` over all atom IDs: tokenize on underscore, group by stem (longest common token sequence ≥ 2 tokens). Manually audit the top-50 clusters for true-aliases vs false-merges. Expect tens-of-units of genuine variant clusters (hungarian_assignment/hungarian_algorithm class; chu_liu_edmonds/chu_liu_edmonds_algo class).
2. For each candidate cluster, apply policy: earliest atom_created_ts wins canonical; tie-break by lexicographic-shortest. Emit `aliases.jsonl` with rows `{"canonical": "hungarian_algorithm", "aliases": ["hungarian_assignment"], "policy": "earliest_ts", "ts_resolved": "..."}`.
3. Dry-run the migration: rewrite atoms + relations to canonical in `data/atoms.shard-N+1/`, count (a) atoms collapsed, (b) relations re-targeted (especially SHARES_MATH and DEPENDS_ON edges where cross-signal joins were artificially deflated), (c) any orphaned references.
4. Cross-signal join lift measurement: run the SHARES_MATH co-occurrence query both pre- and post-normalization on the dry-run shard; expect detectable but bounded lift (the variant pairs are real but few in absolute count).

Total cost: ~2 hours laptop CPU. No GPU. No queue burn.

## (c) Falsifiable predictions

### HARD-PASS thresholds (pattern adoption recommended)

- **HP-1 (clustering precision):** ≥ 90% of auto-clustered variant pairs (Jaro-Winkler ≥ 0.92 on token-stem-match) are TRUE aliases on manual audit of top-50 clusters. False-merge rate ≤ 10%.
- **HP-2 (cross-signal join lift):** SHARES_MATH edge count on the affected variant pairs increases by a factor consistent with the merge ratio (i.e., if 2 IDs merge into 1, their separately-counted SHARES_MATH targets unite — measurable as `unique_targets(canonical) ≥ max(unique_targets(variant_i))` and typically `> sum / 2` indicating prior split).
- **HP-3 (no relation orphaning):** Post-migration, 100% of relations resolve to existing atom IDs (no dangling pointers). Readers using `alias_to_canonical()` resolve any legacy variant query to the canonical without exception.
- **HP-4 (atomic swap clean):** During the shard swap window, zero readers observe a mid-state where some atoms are canonical and others are not (single CURRENT-pointer flip).

### HARD-FAIL thresholds (pattern rejected, redesign required)

- **HF-1 (over-merging):** > 25% false-merge rate in the top-50 audit (e.g., `softmax_temperature` merged with `softmax` when they should stay distinct). This means Jaro-Winkler ≥ 0.92 threshold is too loose for the substrate's identifier conventions; must raise to ≥ 0.95 or require token-stem-match AS WELL AS character similarity.
- **HF-2 (under-merging):** < 50% recall of known variant clusters from the manual audit list. Means blocking key is too narrow (token-prefix isn't catching e.g. abbreviation patterns); must add a second blocking pass on edit-distance over the full ID.
- **HF-3 (no measurable join lift):** Cross-signal join counts identical pre- and post-normalization. Means either the variants weren't actually splitting joins (skunkworks INV-2a premise was wrong), or the migration didn't actually rewrite the relations. Investigate before claiming the methodology shipped.
- **HF-4 (alias-map cycle):** Any cycle in the alias graph (`alias_to_canonical(canonical_X) → Y` where Y also maps somewhere). Means the canonicalization policy is non-deterministic; must enforce that canonical IDs are never aliases of anything else.

### Calibration notes

- Blocking + Jaro-Winkler matching is STANDARD practice for short identifiers (multiple ontology-alignment surveys, AML name-screening best-practice). P_deflated ~ 0.70 for HP-1 with default threshold.
- Wikidata preferred-label + altLabel pattern is canonical for ontology design and well-documented in skos:prefLabel / skos:altLabel. P_deflated ~ 0.75 for the design pattern.
- Cross-signal join lift (HP-2) is the substrate-specific synthesis — joins-deflated-by-variant-ids is a hypothesis (INV-2a flag) not yet measured; could turn out to be small in absolute terms. P_deflated ~ 0.50 (novel-synthesis cap applied).
- Migration via the in-flight re-shard is operational synthesis with the prior atomic-swap drill; both drills concur on the CURRENT-pointer swap pattern; combined P ~ 0.80.

## (d) Cross-thread synthesis

### Three design patterns + tradeoffs

#### Pattern A: Wikidata preferred-label + altLabel (RECOMMENDED for Testbed)

**Structure.** Single `data/atom_aliases.jsonl`. Each line:
```
{"canonical": "hungarian_algorithm", "aliases": ["hungarian_assignment", "hungarian_assignment_algo"], "policy": "earliest_ts", "resolved_ts": "2026-06-13T...", "audit": "manual:approved"}
```
- One canonical per cluster (skos:prefLabel analog).
- N aliases per canonical (skos:altLabel analog).
- Aliases are NEVER deleted, only the canonical pointer can be re-pointed in a future migration (immutability per HashiCorp Vault identity dedup pattern + ulid-rename pattern).
- Bidirectional: `alias → canonical` is the hot path; `canonical → [aliases]` available for audit / debug.

**Pros.** Standard. Auditable. Idempotent. Matches the substrate's existing JSONL convention. Trivial to load in memory (~hundreds-of-thousands of atoms × few aliases each ≪ 1 GB).
**Cons.** Doesn't natively handle multi-version (e.g., what if hungarian_algorithm itself gets superseded later?). Solution: add `superseded_by` field, never break the alias resolution path.

#### Pattern B: Equivalence-class union-find with canonical pointer

**Structure.** `data/atom_equiv.jsonl` where each row is a node `{"id": "X", "parent": "Y"}` like classic union-find; the root of each tree is the canonical.

**Pros.** Compact for very large alias graphs. Trivial to add new equivalences online (`union(a, b)`).
**Cons.** Resolution requires path-compression at read time (not free); harder to audit (canonical of any ID requires traversal). Overkill for Testbed scale.

#### Pattern C: Versioned alias graph (Pattern A + history)

**Structure.** Same as A but each alias-resolution row carries timestamps + a `version` integer; the alias graph is append-only; lookup picks the latest version.

**Pros.** Full history; can replay corpus state at any prior point. Matches the substrate's append-only spirit.
**Cons.** More complex; over-engineered for the current problem. Reserve for later if substrate ever needs temporal-corpus replay.

**Verdict: Pattern A for now; reserve C extension if temporal-replay becomes a requirement.**

### Specific Testbed recommendation

#### File format
```
# data/atom_aliases.jsonl  -- newline-delimited JSON, atomic write per cluster
{"canonical": "hungarian_algorithm", "aliases": ["hungarian_assignment"], "policy": "earliest_ts", "resolved_ts": "...", "audit": "auto:jw_0.94"}
{"canonical": "chu_liu_edmonds", "aliases": ["chu_liu_edmonds_algo"], "policy": "earliest_ts", "resolved_ts": "...", "audit": "manual:approved"}
```

#### Lookup library: in-house, no external dep
```python
# tools/canonical_id.py
import json
from pathlib import Path
from typing import Dict

_ALIAS_TO_CANONICAL: Dict[str, str] | None = None
_ALIAS_PATH = Path("data/atom_aliases.jsonl")

def _load() -> Dict[str, str]:
    global _ALIAS_TO_CANONICAL
    if _ALIAS_TO_CANONICAL is None:
        m: Dict[str, str] = {}
        if _ALIAS_PATH.exists():
            for line in _ALIAS_PATH.read_text(encoding="utf-8").splitlines():
                if not line.strip(): continue
                row = json.loads(line)
                c = row["canonical"]
                for a in row.get("aliases", []):
                    m[a] = c
                # canonical resolves to itself for idempotency
                m.setdefault(c, c)
        _ALIAS_TO_CANONICAL = m
    return _ALIAS_TO_CANONICAL

def canonical(atom_id: str) -> str:
    """Resolve atom_id to its canonical form. Identity if not aliased."""
    m = _load()
    return m.get(atom_id, atom_id)

def reload() -> None:
    """Drop in-memory cache; next call re-reads from disk."""
    global _ALIAS_TO_CANONICAL
    _ALIAS_TO_CANONICAL = None
```

Why no external dep:
- splink is ~7M-record-scale overkill; Testbed corpus is hundreds-to-low-thousands of atoms.
- dedupe.io requires human training data + supports a different active-learning flow.
- RecordLinkage is research-tier; py_stringmatching / rapidfuzz are libraries we'd pull for the matching step only, not the storage / resolve pattern.

**For the matching step during cluster discovery, use rapidfuzz (a single small library).** rapidfuzz.distance.JaroWinkler.similarity is the right primitive for short technical identifiers. If a dep is undesirable, the Jaro-Winkler implementation is ~30 lines of pure Python.

#### Integration with current re-shard (CURRENT-pointer swap)

The atomic_write_shard_swap drill (notes/research_DRILL_atomic_write_shard_swap_patterns_2026-06-13.md) established the swap pattern. Integration:

1. **Pre-swap:** build `data/atom_aliases.jsonl` in the OLD shard's working directory (it's metadata, not shard data).
2. **In the rebuild writer:** when writing atoms and relations into `data/atoms.shard-N+1/`, pipe every atom_id and every relation endpoint through `canonical(...)`. Atoms that are aliases get collapsed (merge SHARES_MATH targets, sum citation counts where applicable, preserve earliest provenance).
3. **Sentinel:** the new shard manifest carries `alias_map_version=K` so readers know which alias resolution snapshot was applied.
4. **Swap:** CURRENT-pointer flip happens normally; the alias map is ALREADY in place from step 1 so readers see consistent canonical state immediately post-swap.
5. **Post-swap:** readers that resolve a legacy variant query (e.g., a cached probe firing `hungarian_assignment`) hit `canonical()` and route to the merged atom transparently. Nothing breaks.

#### Migration path (one-shot, idempotent)

```
tools/migrate_alias_normalize.py:
  Stage 1 (DISCOVERY): scan old shard atom IDs; produce clusters via blocking (token-stem-match) + matching (rapidfuzz JaroWinkler >= 0.92); write candidate_clusters.jsonl
  Stage 2 (AUDIT): emit top-50 clusters with stem + members + scores to stdout for manual review; allow manual override file manual_overrides.jsonl (force-merge, force-split)
  Stage 3 (RESOLVE): apply policy (earliest_ts wins; lex-shortest tiebreak); write data/atom_aliases.jsonl atomically
  Stage 4 (REWRITE): during the next shard rebuild pass, route every atom + relation endpoint through canonical(); collapse and merge; emit data/atoms.shard-N+1/
  Stage 5 (VERIFY): post-swap, run cross-signal join sanity (HP-2); compare atom-count, relation-count pre/post; log to data/orchestrator_status_log.jsonl
```

Idempotency: re-running migrate on an already-normalized shard is a no-op (canonical of canonical is itself).

### How prior literature informs this without governing

- Entity resolution surveys (Christen 2012; Papadakis 2019 blocking survey; arxiv 2008.04443 "Almost All of ER") give us the canonical pipeline shape (preprocess → block → match → cluster → canonicalize). The substrate inherits structure, not the specific tooling.
- Wikidata's preferred-label / altLabel + skos:prefLabel / skos:altLabel is the design pattern. We inherit the schema vocabulary, not the SPARQL endpoint.
- Jaro-Winkler is favored over Levenshtein here because variant identifiers tend to share prefixes (hungarian_*, chu_liu_*). Prefix-emphasis matches our identifier morphology.
- splink / dedupe.io demonstrate the production scale matters for tool choice. We're 4 orders of magnitude smaller, so we use lighter-weight pattern.
- Wellcome catalogue-pipeline (creating canonical identifiers) demonstrates the bulk-rewrite-during-pipeline-rebuild pattern fits naturally with a shard swap.
- Substrate-specific synthesis (novel-synthesis cap 0.50): the integration with SHARES_MATH cross-signal join lift quantification is OURS to measure; no published prior couples canonical-id hygiene to a substrate-graph join metric in this form.

## (e) Substrate-product implications

- Closes a corpus-hygiene gap that artificially deflates SHARES_MATH cross-signal joins (skunkworks INV-2a). Magnitude unknown but bounded; the cheap decisive test measures it directly.
- Adds a structural artifact (`atom_aliases.jsonl` + `canonical()` resolver) that is visible, auditable, and substrate-load-bearing — supports the architecture-axis story without burning queue cycles.
- Idempotent migration path means we can ship the alias-map TODAY (Stage 1-3 measurement-only, no canonical rewrite), gather data, then commit Stage 4 (rewrite) during the next planned re-shard cycle. Decouples the discovery from the destructive write.
- Reusable for future variant clusters (the substrate's atom-naming conventions will evolve; the alias map is the standing mechanism).
- Substrate-product positioning: this is the kind of plumbing LLMs cannot do for themselves — they have no addressable atomic-id namespace, no canonical-form policy, no auditable alias graph. The substrate explicitly maintains the namespace it computes over. (LLM categorical-gap story extension.)
- Honest framing: the alias-map mechanics are standard production patterns from KB / ontology / record-linkage literature. The integration with the substrate's atom-graph and the SHARES_MATH cross-signal join lift measurement are the substrate-specific synthesis where we may be first. Prior work informs; does not govern.

## (f) Citations (verified count: 5 web searches, ~25 sources reviewed; high-confidence anchors listed)

- arxiv 1905.06167 — "A Survey of Blocking and Filtering Techniques for Entity Resolution" (Papadakis et al.) — blocking is 10× more important than matching
- arxiv 2008.04443 — "(Almost) All of Entity Resolution" (Binette & Steorts) — canonical four-stage pipeline (block, match, cluster, canonicalize)
- arxiv 2504.04266 — "BlockingPy: approximate nearest neighbours for blocking" (2024) — modern embedding-based blocking; not needed for our scale but informs upgrade path
- Wikidata Help:Label (wikidata.org) — preferred-label / altLabel design pattern; "the most common name is picked for the label while the other ones are listed as aliases"
- Wellcome Collection catalogue-pipeline docs — "Creating canonical identifiers" — bulk pipeline canonicalization pattern
- HashiCorp Vault identity dedup docs — different-case entity alias resolution pattern; earliest-ID-wins as canonical
- robinlinacre.com — Splink benchmarks (deduplicating 7M records in 2 min) — establishes that for our 4-OOM-smaller scale, an in-house Pattern A solution is appropriate
- recordlinkage.readthedocs.io — RecordLinkage docs — research-tier; cited to contextualize against splink/dedupe.io
- A Comparative Analysis of Fuzzy String Matching Algorithms for Content-Based Ontology Alignment (Springer 2024) — Jaro-Winkler prefix-emphasis for ontology terms
- Flagright AML-screening guide — Jaro-Winkler for fast individual-name screening; Levenshtein for longer business entities (informs threshold choice)

Verified anchor count: 10.
