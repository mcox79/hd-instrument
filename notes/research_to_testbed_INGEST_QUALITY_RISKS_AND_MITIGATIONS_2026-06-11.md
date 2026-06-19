# Research -> Testbed: ingest quality risks + 8-layer mitigation strategy + NORTH STAR SCALE-INVARIANT

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** User architectural question: garbage ingest + schema drift risks

## Risks acknowledged

| Risk | Manifestation |
|---|---|
| Garbage ingest | Typos + contradictions + deprecated decisions + half-formed routings + speculative content as fact |
| Schema drift | New headers + different field names + evolving conventions break parser silently |
| Net-negative atoms | Wrong descriptions degrade retrieval (Findings 04/05 pattern) |
| Provenance loss | Can't trace if file deleted/renamed |
| Silent breakage | Parser drops atoms without alert |

## 8-layer mitigation (per full-research-ledger drill P5 self-ingest-safety + 7 invariants)

### 1. Quality tiers at ingest
- Tier-A: hand-authored JSONL (full trust; rich-schema)
- Tier-B: parser-validated notes (structured + P_deflated >= 0.30 + Decision section)
- Tier-C: best-effort (flagged for review)
- Reject: parse-failure rate > threshold

### 2. Templates + linting
- TEMPLATES for drills + routings + memory entries
- Pre-commit hook validates structure locally
- Testbed parser includes schema validator server-side
- Templates in templates/research_*_v1.md

### 3. Layer 1 attribution applies to ingest (methodology rule 6 PROT)
- Each new atom's retrieval contribution measured
- Net-negative atoms flagged before commit
- Same mechanism caught algebra-vec NET NEGATIVE Findings 04

### 4. BOCPD drift detection
- Parser success rate monitored over time
- Bayesian change-point detection alerts on note-structure changes
- Catches silent schema drift

### 5. CAS + PROV-O provenance
- Every atom traceable: source-file + content-hash + ingest-timestamp + parser-version
- Wrong atom -> NEW corrected atom; old marked deprecated
- Immutable + versioned

### 6. Adversarial probes (7 invariants drill)
- Synthetic atoms with KNOWN errors injected periodically
- Parser should catch them
- Cross-validation hold-out

### 7. Schema change protocol
- Schema-change-proposal -> Testbed -> parser update + synthetic-note test
- Versioned parser bump
- NO silent schema drift

### 8. Hand-authored JSONL where stakes are highest
- Concept corpus algebra-vec stays hand-authored
- Schools-of-thought ratings stay hand-authored
- Sealed queries stay hand-authored
- Auto-ingest handles BULK low-stakes; expert judgment for critical content

## Implementation in evolve.py

```python
def ingest_note(file_path):
    # 1. Parse with versioned parser
    parser_version = PARSER_V1_3
    parsed = parser.parse(file_path, version=parser_version)

    # 2. Quality tier classification
    tier = classify_quality_tier(parsed)  # A / B / C / Reject

    if tier == "Reject":
        alert_research(file_path, "parse failure or low confidence")
        return None

    # 3. Layer 1 attribution check (methodology rule 6 PROT)
    candidate_atom = build_atom_from_parsed(parsed)
    contribution = measure_retrieval_contribution(candidate_atom)
    if contribution < THRESHOLD:
        flag_for_review(candidate_atom, "net-negative or noise")
        return None

    # 4. CAS + PROV-O metadata
    candidate_atom.provenance = {
        "source_file": file_path,
        "content_hash": cas_hash(file_path),
        "ingest_timestamp": now(),
        "parser_version": parser_version,
        "quality_tier": tier,
    }

    # 5. Write through testbed-only boundary
    return testbed_writer.commit(candidate_atom)
```

## Schema change governance

| Change type | Process |
|---|---|
| New note section | Research files schema-change-proposal; Testbed extends parser; versioned bump |
| Renamed field | Same; old + new field both parseable for transition window |
| Deprecated section | Marked but not removed; parser handles both for backward compat |
| Breaking change | Major version bump; old atoms preserved with parser-version metadata |

## PLUS huge result this turn: NORTH STAR SCALE-INVARIANT

Exp-Dev extended head-to-head to Qwen2.5 0.5B/1.5B/3B:

| Benchmark | Substrate | 0.5B | 1.5B | 3B |
|---|---|---|---|---|
| MAWPS | 0.806 | 0.188 | 0.507 | 0.567 |
| MultiArith | 0.753 | 0.087 | 0.107 | 0.253 |
| SVAMP | 0.297 | 0.163 | 0.413 | 0.433 |
| ASDiv | 0.224 | 0.375 | 0.800 | 0.900 |
| Wins | | 3/4 | 2/4 | 2/4 vs 6x-larger |

Substrate WINS MAWPS + MultiArith at EVERY LLM SIZE. Structured-arithmetic advantage SCALE-INVARIANT not small-model artifact. Beats 6x larger LLM on 2/4 + dominates latency/memory/determinism.

Honest boundary: comprehension-heavy benchmarks where LLM NL fluency wins. Same boundary as CODE synthesis ceiling.

VALIDATES drill 18 substrate-vs-larger-LLM methodology prediction. VALIDATES drill 21 substrate-memory + small-LLM-frontend hybrid commercial framing.

## Cross-references
- Full-research-ledger drill: notes/research_drill_substrate_as_full_research_ledger_2x_2026-06-11.md
- 7 invariants drill: notes/research_drill_7_invariants_empirical_validation_2x_2026-06-11.md
- Auto-ingest architecture: notes/research_to_testbed_AUTO_INGEST_VIA_EVOLVE_PY_NOT_MANUAL_2026-06-11.md
- NORTH STAR SCALE-INVARIANT: notes/exp_dev_to_research_NORTH_STAR_SCALE_INVARIANT_2026-06-11.md

---

**Testbed:** 8-layer mitigation for ingest quality risks (tiers + templates + Layer 1 PROT + BOCPD + CAS+PROV-O + adversarial + schema change protocol + hand-authored JSONL where stakes high). Implementation sketch in evolve.py. PLUS NORTH STAR SCALE-INVARIANT result EMPIRICALLY VALIDATES commercial scale-invariant differentiation across 0.5B / 1.5B / 3B model sizes.
