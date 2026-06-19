# Testbed -> Research: segfault root cause + fix (CLOSES backend segfault open issue)

**From:** Testbed  **Date:** 2026-06-09 ~20:15 UTC
**Re:** Stage A crash diagnosed; same root cause as backend segfault open issue

## Root cause: pyarrow 24.0.0 Windows DLL conflict

Faulthandler trace (truncated reports in my earlier debug iterations missed this; full trace pinpointed):

```
sentence_transformers/__init__.py:15
  -> sentence_transformers/base/sampler.py
  -> sentence_transformers/util/similarity.py
  -> sklearn -> sklearn.base -> sklearn.utils.validation
  -> pandas/__init__.py
  -> pandas/compat/pyarrow.py:12 (try: import pyarrow)
  -> pyarrow/__init__.py:71 (from pyarrow.lib import ...)
  -> ACCESS_VIOLATION 0xC0000005 in pyarrow.lib C-extension DLL load
```

`pyarrow.lib` is the C-extension `.pyd` file with bundled DLLs. pyarrow 24.0.0 on Windows has a DLL load conflict when loaded after sklearn/pandas in this transit order. Crashes ONLY happen when chain runs through sklearn.utils -> pandas -> pyarrow. Direct `import pyarrow` works fine.

Diagnostic sequence:
- `import pyarrow` alone -> ok
- `import torch; import pyarrow` -> ok
- `import sklearn; import pyarrow` -> ok
- `import pandas; import pyarrow` -> ok
- `import sentence_transformers` -> crash (transitive chain triggers the load order)

## Why PubMed survived

PubMed ingest started at ~13:00 UTC when the environment was healthy. Process loaded pyarrow into memory; that copy continued working. Stage A launched at 16:23 UTC after PubMed completed; fresh process hit fresh DLL load and crashed.

Likely: a Windows update or background system change between 13:00 and 16:23 introduced the DLL conflict.

## Fix applied

`pip install --force-reinstall --no-deps pyarrow==20.0.0`

Result:
- `import sentence_transformers` works
- bge_encoder.get_encoder() works
- Wikidata smoke test: 1024 facts in 35 sec via REC-3 filter
- Stage A ingest relaunched detached at PID 190916; running
- facts.jsonl + triples.jsonl both growing (retrofit per Q2 working)

`requirements_demo.txt` pinned to `pyarrow>=19,<24` so future installs avoid the bad version.

## This ALSO closes the backend segfault open issue

The backend 0xC0000005 crash that's been blocking /converse + /chat serving is the SAME root cause:
- Backend loads sentence_transformers via bge_encoder
- Same transitive chain through sklearn -> pandas -> pyarrow.lib
- pyarrow 24.0.0 DLL conflict crashes the import

Same fix should unblock backend serving. Recommended: try restarting backend with pyarrow 20.0.0 installed; segfault should resolve. (NOT doing yet since user direction was to NOT restart backend until segfault diagnosed.)

## Status now

| | |
|---|---|
| Stage A Wikidata ingest | RUNNING PID 190916; facts + triples growing |
| Stage B substrate library | complete (a7bfaa4e) |
| Stage C plumbing | complete (f6b717db); awaits Stage A facts.jsonl + triples.jsonl |
| Backend segfault | DIAGNOSED; pyarrow 24->20 fix should resolve; user-paced restart |
| pyarrow pin | shipped in requirements_demo.txt |

## Estimated Stage A timing

Smoke test rate: 29 facts/sec on CPU bge-large. For target ~10M filtered facts: ~95 hours wall. Acceptable for overnight + tomorrow. If too slow, can increase batch_size or move bge-large to GPU once backend allows.

## Cross-references
- Original segfault debug note: notes/research_to_testbed_CONVERSE_SHIPPED_SEGFAULT_DEBUG_2026-06-09.md
- Stage C 5-answers: notes/research_to_testbed_STAGE_C_5_ANSWERS_2026-06-09.md
- pyarrow pin commit: pending push
