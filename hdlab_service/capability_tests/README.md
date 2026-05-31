# Pattern B capability tests

Five deterministic tests that exercise the substrate-backed Pattern B
service's capability claims. No LLM API calls; pure substrate-service
behavior validation.

## Run

```
cd hd-instrument
pytest hdlab_service/capability_tests/ -v
```

Each test gets a fresh substrate state (isolated audit log + signing keys
under a temp dir). Tests are independent and can run in any order.

## The 5 capability claims (architecture v1 Tier 2)

These map to the bullet list in
`notes/session_kickoff_testbed_v1.md` Tier 2:

| # | Capability | Test | Pass criterion |
|---|---|---|---|
| 1 | Audit trail completeness across operations | `test_capability_1_audit_trail_completeness` | Every store/edit/delete produced an audit record; chain_ok holds after all operations |
| 2 | Edit-then-query semantics | `test_capability_2_edit_then_query_semantics` | Post-edit retrieval returns the new value; full diff trail recoverable from audit records |
| 3 | Deletion-with-certificate end-to-end | `test_capability_3_deletion_with_certificate` | Cert verifies cryptographically (Ed25519); state hash changed across delete; fact unreachable post-delete |
| 4 | Mid-conversation edit handling | `test_capability_4_mid_conversation_edits` | Interleaved reads see post-edit state; KF-2 edit isolation holds (witness facts untouched) |
| 5 | Multi-hop tool-use coordination | `test_capability_5_multi_hop_coordination` | 3-hop chain (product -> manages-edge -> manager name) returns the correct ground-truth answer |

## Synthetic fact corpus

Tests use `hdlab_service/corpora/synthetic_corpus.py::small_corpus()` for
controlled ground truth: 75 facts encoding 12 people, 3 companies, 6
products with employs / makes / manages / reports_to edges. Seeded RNG
keeps every run identical. Ground-truth dicts are returned alongside the
fact list so tests can ASK substrate questions and check answers without
re-deriving them from the corpus.

The corpus is intentionally domain-neutral. Per the Tier 2 revised goal
("capability-generic first, domain commitment last"), tests validate
substrate properties without implying a specific deployment target
(medical, legal, financial, etc.).

For the LLM-only baseline comparison (Tier 2b), the same corpus renders as
a plain-text dump via `corpus_as_context_string()` -- substrate-backed
vs LLM-only conditions use identical facts, just different delivery
mechanisms.

## What's NOT tested here (deferred to Tier 2b)

- Actual LLM API calls (Claude / GPT) with the substrate tool definitions
- LLM-vs-substrate accuracy comparison
- Token consumption comparison
- Latency end-to-end including LLM round-trip

Tier 2a (this) is "does the substrate deliver the claim?"; Tier 2b is
"does the integrated LLM + substrate flow deliver value over LLM-only?"

## Adding a new capability test

1. Add a test function to `test_capabilities.py` prefixed `test_capability_N_<name>`.
2. Use the `client` fixture for an isolated substrate.
3. Use `small_corpus()` for ground-truth-backed scenarios.
4. Document the capability claim + method + pass criterion in the docstring.
5. Update this README's table.

If the test needs a new server endpoint, prefer adding it to
`hdlab_service/server.py` + a tool definition in
`hdlab_service/tool_definitions.py` rather than working around the public
surface; capability tests should exercise what the LLM is allowed to do.

## Tier 2 progression after these tests pass

With all 5 passing, the substrate side is capability-validated and the
Pattern B integration is ready to be wrapped in an actual LLM tool-use
harness. The remaining Tier 2 work is exposing the synthetic corpus +
substrate service to a real LLM and measuring the LLM's reasoning quality
with vs without substrate tool access. That work lives in `tools/llm/`
once the API creds are wired (separate from Lambda Cloud credentials).
