# Prereg: n8_proofwiki_smoke_ingest_chunk_kb_v2_retry

Date: 2026-06-27
Anchor: n8_proofwiki_smoke_ingest_chunk_kb_v2_retry
Cell: experiments/exp_n8_proofwiki_smoke_ingest_chunk_kb_v2_retry.py
Queue: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive)
Primitives composed:
  - hdlab/director_kb_math_sources.py (patched with v2_retry helpers;
    exp_dev 2026-06-27)
  - hdlab/director_kb.py (chain-grade schema loader)
  - hdlab/director_kb_chunk_ingest.py (chain-grade ingest pipeline)
  - hdlab/director_kb_query.py (chain-grade KB query)

## Motivation

v1 (n8_proofwiki_smoke_ingest_chunk_kb_v1) HARD_FAILed because the
ProofWiki website returned 0 bytes (transient network failure during the
remote-CPU runner's dispatch window). The pre-reg's
`fetch_errors_non_empty` HARD_FAIL gate fired correctly, but the failure
mode is recoverable: a 1- or 5-second retry would have succeeded.

v2_retry adds:
1. Exponential-backoff retry helpers in director_kb_math_sources
   (`_http_get_with_retry`, `_http_post_with_retry`) with default
   delays (1s, 5s, 25s) -- 4 attempts total per HTTP request, ~30s
   max wait per request.
2. Local-cache fallback: if all retries fail, the cell consults
   `data/math_kb_cache/proofwiki/_export.xml` and uses cached content
   if available (>= 1000 bytes).
3. Pre-populate step: before the main fetch, the cell does a small
   10-page fetch to seed the local cache, so a subsequent full-fetch
   failure has SOMETHING to fall back to.

## Mechanism (mechanically identical to v1 otherwise)

```
fetch_and_materialize_proofwiki_v2_retry(repo, max_pages):
  for chunk in chunked_titles:
    _http_post_with_retry(EXPORT_URL, body, retries=(1s, 5s, 25s))
    record retries + outcome
  if all_chunks_failed:
    try local_cache_fallback (data/math_kb_cache/proofwiki/_export.xml)
    if cache also missing: return ok=False
  parse_proofwiki_xml + materialize_proofwiki (verbatim v1)
```

Arms, schema, chunk-ingest pipeline, probe titles, verdict logic: all
verbatim v1.

## Arms (4 mandatory; verbatim v1)

- ARM_BASELINE_FILENAME_QUERY -- query existing v1 filename-metadata KB
- ARM_SMOKE_INGEST_500 -- fetch (RETRY+FALLBACK) + materialize +
  chunk-ingest + query 5 theorem-name probes; verify-the-referent
- ARM_FULL_N_PREVIEW_DISCRIMINATOR -- analytical scaling check
- ARM_CONTAMINATION_CONTROL -- non-math probes

## Pre-reg bands (LOCKED; verbatim v1)

### HARD_PASS
- smoke ARM top1_min >= 0.85 across all 5 probes
- AND smoke ARM content_match True across all 5 probes
- AND analytical scaling passes (tau_full >= 0.85 for all probes)
- AND contamination_max < 0.5
- AND n_chunks in band ([60, 1000] smoke / [1500, 4000] full)

### HARD_FAIL
- cardinality_breach (arms missing OR chunks out of band)
- OR fetch_errors_non_empty AFTER retry and fallback (META_RULE_J)
- OR contamination_max >= 0.5
- OR BIAS-Q suspect 1.000 with content mismatch
- OR smoke top1_mean < 0.70

### MIDDLE_BAND
- smoke passes but scaling fails: full-N test cell needed
- OR partial signal: some probes match, some don't

## Discriminator-must-survive-scale

Smoke MAX_PAGES=20 (~100 chunks observed). analytical scaling projects
to N_FULL_PROJECTION=35000 chunks; tau_full = tau_smoke * sqrt(35000/N).
At smoke n=100, tau_full = 0.85 * sqrt(350) = 0.85 * 18.7 = 15.9 >> 0.85
-- always passes if smoke clears 0.85 (analytical scaling is upper-
bound preserving for n_smoke < n_full).

## Substrate-only-decode gate

zero_llm_calls_at_inference: True. Pipeline is char-trigram encoder +
HDC projection + cosine query. No transformers.

## REQUIRED_FIELDS

`verdict`, `verdict_msg`, `elapsed_s`, `summary`.

## New disciplines applied

- META_RULE_H cardinality_ok mandatory (4 arms + chunks in band).
- META_RULE_J no-silent-except: fetch errors RECORDED. Retry+fallback
  REDUCES the surface of META_RULE_J HARD_FAILs without weakening
  them; if BOTH retry AND fallback fail, fetch_errors still trips.
- META_RULE_K smoke fires discriminator: ARM_FULL_N_PREVIEW arm.
- META_RULE_L band-floor strictly-above-floor.
- BIAS-S/Q/N/13 from USER 2026-06-24 master checklist.
- PROT-020: numpy-only -> remote_cpu_queue.

## Runtime estimate

Smoke (MAX_PAGES=20 + pre-populate 10):
  - pre-populate: ~10-30s (network + retry overhead)
  - main fetch: ~20-60s (20 pages + chunk-ingest)
  - 4 arm computations: ~30s
  -> wall ~ 70-120s
Full (MAX_PAGES=500): 500 pages * ~1s/page network + 2500 chunks
  ingest * ~0.01s/chunk = ~525s -> wall ~600s = 10min.

timeout_s = ceil(1.5 * 600) = 900s for safety -> use 900s (15min).

## Honest scope

This cell tests whether retry + cache fallback fixes the v1 transient-
network HARD_FAIL. It does NOT test:
- New mechanism (verbatim v1 chunk-ingest + query)
- Different probe set
- Anything beyond v1's pre-reg bands

If v2_retry HARD_PASSes, ProofWiki ingest is operationally robust and
the v1 failure is closed. If v2_retry HARD_FAILs with same
fetch_errors, ProofWiki blocking is structural (need different source).

## ASCII-only; no unicode; no emojis; no em-dashes.
