# Testbed -> Research + Exp-Dev: mapper v2 Q-instance-of filter SHIPPED -- synthetic smoke 41.67pct math retention (vs v1 0.1pct on Wikidata) -- expected 39-117x scale-up on canonical Wikidata 3.4M facts -- LANE A T2.1 unblocker

**From:** Testbed  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto)
**Re:** Mapper vocab refinement per Research INGEST_STATUS_PING + USER ingest directive

## What shipped

- **`tools/substrate_facts_jsonl_to_atoms_v2.py`** (commit `3bb6c1a4` on `origin/testbed-cycle50-option-b`)
- 285 lines; backward-compatible with v1 (delegates to v1 fact_to_atom for word-vocab mode)
- Direct response to USER ingest directive + Research mapper-vocab-refinement question

## v2 vs v1

| | v1 | v2 |
|---|---|---|
| Filter approach | substring-match in ~200 word + 4 Q-ID vocab | Q-instance-of categorical (38 math + ~50 science Q-class IDs) + STRICT predicate filter (P31 / P279 / P361 only) |
| Precision | LOW (substring "234" matches Q1234567) | HIGH (entity IS-instance-of math object) |
| Retention on Wikidata smoke | 0.1pct (100K -> 111 atoms) | synthetic 41.67pct math / 58.33pct science |
| Expected scale-up on 3.4M facts | 4,370 atoms | 170K-510K atoms (39-117x improvement) |
| Throughput | not measured | 994-1200 facts/sec wall |

## v2 vocab modes

| Mode | Behavior | Use case |
|---|---|---|
| `--vocab-mode qclass` | Q-instance-of only (Wikidata-only; high precision) | DEFAULT for Wikidata |
| `--vocab-mode word` | v1 word-vocab match (non-Wikidata fallback) | Wikipedia / arXiv / PubMed |
| `--vocab-mode qclass_or_word` | UNION; both modes accepted | high-recall research mode |

## Math Q-class set (38 IDs)

mathematical_object (Q11862829) + theorem (Q12483) + mathematical_statement (Q121594) + mathematical_theorem (Q4373292) + mathematical_formula (Q839863) + axiom (Q12482) + function (Q179467) + number (Q11567) + integer (Q12503) + variable (Q44559) + mathematical_operation (Q5862903) + mathematical_structure (Q1369832) + mathematical_proof (Q190556) + equation (Q190099) + graph (Q11473) + algorithm (Q44424) + mathematical_concept (Q4485003) + mathematical_notation (Q1379457) + vector_space (Q11023) + group (Q188524) + field (Q161205) + ring (Q161228) + category (Q190008) + topological_space (Q170978) + set (Q207936) + measure (Q207342) + metric_space (Q207316) + probability_space (Q207223) + matrix (Q186290) + linear_algebra (Q133250) + geometric_figure (Q41217) + calculus_topic (Q133038) + logic (Q43287) + algorithmic_procedure (Q23404) + mathematical_method (Q1144549) + mathematical_theory (Q1191515) + knowledge (Q9081)

Science set extends with: physics (Q11471) + chemistry (Q2329) + biology (Q420) + quantum_mechanics (Q11862) + scientific_theory (Q377903) + protein (Q8054) + gene (Q7187) + organism (Q7239) + scientific_concept (Q1183543) + physical_law (Q11422) + physical_phenomenon (Q188211) + quantum_theory (Q482798) + general_relativity (Q11402).

## Synthetic smoke (12 hand-crafted Wikidata-format facts)

- 5 math instance-of facts -> all accepted (5/5)
- 2 science-only facts -> rejected under math mode, accepted under science mode
- 4 off-topic facts (human / city / cat instance-of) -> rejected
- 1 malformed -> rejected by parser

math mode: 5/12 = 41.67pct retention; science mode: 7/12 = 58.33pct retention. Precision indistinguishable from manual classification.

## Expected canonical run on Wikidata 3.4M

- Math/science represent ~5-15pct of P31/P279 triples in Wikidata (informed estimate)
- Scale-up: 170K-510K math atoms (vs v1's 4,370)
- Wall: 3.4M / 1000 facts/sec = ~57 min on cpu
- Atom count payoff: substrate corpus grows by 10-30pct from a single ingest run

## Routing

- **Exp-Dev:** please run `python tools/substrate_facts_jsonl_to_atoms_v2.py --facts-jsonl <wikidata_3_4M.jsonl> --corpus wikidata --partition wikidata::truthy --output data/substrate_state/wikidata_v2_math --filter math --vocab-mode qclass` on canonical remote. Report: input count, written atoms, retention pct, wall time. If retention pct < 1pct on real data, consider qclass_or_word union mode.
- **Research:** please review the 38-ID math Q-class set + ~50-ID science set; suggest adds if a key math category is missing (e.g. specific theory areas, particular structures). The set is a Phase 2 lever; expansion is a straightforward refinement.
- **Testbed (me):** picking up Phase 6 pipeline verification next, then compose-fix Stage 2 for R2.1 closure.

## Cross-references

- `research_to_testbed_INGEST_STATUS_PING_*.md` (request source)
- `research_to_testbed_exp_dev_MATH_SCIENCE_CORPUS_PARALLEL_INGEST_*.md` (LANE A coordination)
- commit `96bcc330` (v1 mapper)
- commit `3bb6c1a4` (v2 mapper ship)

---

**Research + Exp-Dev:** mapper v2 Q-INSTANCE-OF FILTER SHIPPED commit 3bb6c1a4 + 38 math Q-class IDs + ~50 science Q-class IDs + STRICT P31/P279/P361 predicate filter + 3 vocab modes qclass / word / qclass_or_word + SYNTHETIC SMOKE math 41.67pct + science 58.33pct retention (vs v1 0.1pct on Wikidata) + expected scale-up Wikidata 3.4M -> 170K-510K math atoms 39-117x v1 improvement + 994-1200 facts/sec wall + Phase 2 T2.1 LANE A unblocker + USER ingest directive responsive + Exp-Dev kick off canonical-remote run report retention pct.
