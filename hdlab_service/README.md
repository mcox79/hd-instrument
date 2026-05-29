# hdlab_service: Pattern B FastAPI substrate wrapper

Reference implementation of the Week-1 deliverable from
`notes/pattern_b_integration_demo_executable_spec_v278_2026-05-29.md`.

This service wraps the existing `hdlab/` substrate primitives (no modifications
to substrate code) and exposes them as a FastAPI HTTP/JSON API suitable for
LLM tool-use integration. It also ships:

- A hash-chained append-only audit log
- Ed25519-signed deletion certificates (GDPR Article 17 alignment)
- Anthropic + OpenAI tool-use definitions and a dispatch helper

## Install

```
cd hd-instrument
pip install -r hdlab_service/requirements.txt
```

PyTorch is assumed already installed via the parent `hd-instrument`
environment.

## Environment variables

| Var | Default | Meaning |
|---|---|---|
| `HDLAB_N` | `1024` | Substrate hypervector dimension |
| `HDLAB_M_FRAC` | `0.25` | Reserved (codebook density knob) |
| `HDLAB_CODEBOOK` | `BSC` | One of `BSC`, `Kerdock`, `FHRR`, `HRR` |
| `HDLAB_KEY_DIR` | `hdlab_service/_state/keys` | Where Ed25519 signing keys live |
| `HDLAB_AUDIT_PATH` | `hdlab_service/_state/audit_log.jsonl` | Append-only audit log path |

`BSC` and `Kerdock` are mapped onto the real-valued HRR primitive in this
reference build. `FHRR` selects the complex-valued primitive in
`hdlab/atoms.py`. Internal naming is documented here for engineers; customer-
facing assets do not reference substrate-internal vocabulary.

## Run

```
uvicorn hdlab_service.server:app --reload
```

The service initializes its substrate state on startup (via FastAPI lifespan
handler) and creates the audit log + Ed25519 keypair on first run.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET  | `/health` | Service status, codebook size, audit chain integrity |
| POST | `/store_fact` | Add a (key, value) atom binding |
| POST | `/retrieve_fact` | Closest matching fact + confidence + provenance |
| POST | `/compose_query` | Multi-fact compositional query via binding algebra |
| POST | `/delete_fact` | Erase fact and return signed deletion certificate |
| GET  | `/audit/{record_id}` | Retrieve one audit record |

## Sample requests

```
# health
curl -s http://localhost:8000/health | jq

# store
curl -s -XPOST http://localhost:8000/store_fact \
    -H 'Content-Type: application/json' \
    -d '{"key": "case_smith_v_jones", "value": "The court held for the plaintiff."}'

# retrieve
curl -s -XPOST http://localhost:8000/retrieve_fact \
    -H 'Content-Type: application/json' \
    -d '{"query": "case_smith_v_jones", "min_confidence": 0.5}'

# compositional
curl -s -XPOST http://localhost:8000/compose_query \
    -H 'Content-Type: application/json' \
    -d '{"bindings": [{"role": "case", "filler": "smith_v_jones"}], "min_confidence": 0.1}'

# delete (atom_id obtained from /store_fact response)
curl -s -XPOST http://localhost:8000/delete_fact \
    -H 'Content-Type: application/json' \
    -d '{"atom_id": "atom_<hex>", "requester_id": "admin_42", "legal_basis": "GDPR_ART_17"}'

# audit record lookup
curl -s http://localhost:8000/audit/evt_<hex> | jq
```

## LLM integration - Anthropic Claude

```python
import anthropic
from hdlab_service.tool_definitions import (
    SUBSTRATE_TOOLS_ANTHROPIC,
    tool_call_handler,
)

client = anthropic.Anthropic()

resp = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=1024,
    tools=SUBSTRATE_TOOLS_ANTHROPIC,
    messages=[{"role": "user", "content": "What was the holding in Smith v Jones?"}],
)

# When resp.stop_reason == "tool_use", dispatch each tool_use block:
for block in resp.content:
    if block.type == "tool_use":
        result = tool_call_handler(block.name, block.input)
        # Return result back to the model as a tool_result block...
```

## LLM integration - OpenAI

```python
from openai import OpenAI
from hdlab_service.tool_definitions import (
    SUBSTRATE_TOOLS_OPENAI,
    tool_call_handler,
)

client = OpenAI()

resp = client.chat.completions.create(
    model="gpt-4o",
    tools=SUBSTRATE_TOOLS_OPENAI,
    messages=[{"role": "user", "content": "What was the holding in Smith v Jones?"}],
)

for call in resp.choices[0].message.tool_calls or []:
    import json
    args = json.loads(call.function.arguments)
    result = tool_call_handler(call.function.name, args)
```

## Audit log inspection

The audit log is a JSON-lines file (one record per line):

```
tail -n 5 hdlab_service/_state/audit_log.jsonl | jq .
```

Each record carries `sha256_chain_prev` and `sha256_self`. The chain head
hash is reported in `/health`. To verify chain integrity programmatically:

```python
from hdlab_service.audit_log import AuditLog
log = AuditLog("hdlab_service/_state/audit_log.jsonl")
assert log.verify_chain()
```

## Deletion certificate verification

A certificate returned from `/delete_fact` can be independently verified
given only its embedded `signer_pubkey`:

```python
from hdlab_service.deletion_cert import verify_certificate
import json

cert = json.loads(open("cert.json").read())
assert verify_certificate(cert) is True
```

The certificate format matches Section 5 of the v278 executable spec. GDPR
Article 17 fields (`fact_id`, `deletion_ts`, `state_hash_before`,
`state_hash_after`) are present at the top level for direct compliance
reporting.

## Mapping to existing substrate primitives

| Service feature | Existing primitive | Source |
|---|---|---|
| Fact key/value vectors | `atoms.make_atom_hrr` / `make_atom_fhrr` | `hdlab/atoms.py` |
| (key, value) binding | `binding.bind` | `hdlab/binding.py` |
| Compositional probe matching | `binding.bind` + bundle sum + `atoms.similarity` | `hdlab/binding.py`, `hdlab/atoms.py` |
| Named cleanup | `memory.Codebook` | `hdlab/memory.py` |
| Attention threshold | `modulators.set_attention` | `hdlab/modulators.py` |

The wrapper sets `modulators.attention = 0.0` so the API layer (not the
codebook) decides match/no_match, then re-applies `min_confidence` from the
request. This keeps the substrate primitives unmodified.

## Tests

```
pytest hdlab_service/tests/
```

Tests cover: service startup, all 5 endpoint shapes, store/retrieve
round-trip, Ed25519 deletion cert signing + verification, audit chain
integrity, and tool-definition format.

## Limitations

This is a reference implementation for the Pattern B demo. It is NOT
production-hardened:

- In-memory state only; no DuckDB indexer (spec Section 4 calls for one).
- No Merkle daily-root aggregation yet (spec Section 5).
- No multi-tenancy or auth layer.
- No async write off the critical path; audit fsync on every event.
- Codebook scan is O(N) per query; production deployments need a vector
  index.

Per the spec's Week 2-7 plan, the audit-log DuckDB indexer, Merkle root
chain, and demo UI are added in subsequent weeks. This Week-1 deliverable
exists to unblock the Controller integration (Week 3).
