# exp_dev N3 text8 ingest-cert pre-reg pointer (2026-06-22)

**Anchor:** `n3_text8_ingest_cert_v1`
**Canonical prereg:** `preregs/2026-06-22_n3_text8_ingest_cert_v1.md` (queue_add gate file)
**Cell:** `experiments/exp_n3_text8_ingest_cert_v1.py` (selftest 8/8 PASS; smoke ~0.8s wall locally on cached text8)
**Queue:** `remote_cpu_queue` (smoke entry first; full pending Director smoke-green poll)

## Decision summary (matches the canonical prereg)

- Substrate-LM plugged in: `SubstrateCharLM` (CHAR-level, the text8 grain). N1 v3.1 is TOKEN-level; architecture-AGNOSTIC eval ruling means N3 grades whichever substrate-LM is plugged in. A separate token-level text8 cell could be authored as v2 if Research/Skunkworks rules the token grain primary.
- Bands: absolute-floor (Skunkworks N3 cert-bands + parent prompt):
  - HARD_PASS: substrate_bpc <= 1.90 (beats 5-gram-KN) AND cv <= 0.05 AND gain_vs_ceiling >= 0.05 AND zero LLM calls AND corpus real
  - MIDDLE_BAND: 1.90 < substrate_bpc <= 3.00 (between 5-gram-KN and bigram)
  - HARD_FAIL: > 3.00 OR LLM call OR synthetic-fallback OR primitive collapse
- 4 instrumentation requirements baked (per_unit + cv + zero_llm_calls_LOGGED + bigram-ceiling VQ-floor analog).
- All 7 fixes from parent prompt absorbed (CORPUS_PROVENANCE_REAL asserted + LOGGED; substrate-only code-trace; zero-D-overlap fallback; pre-reg direction-correct; CONFIG_VERSION coverage; per-seed runtime; NO background bash watcher).

## Dispatch state at note-write time

- Self-test PASS (T1-T8) on .venv
- Local smoke arm measured 0.8s wall (10k chars / N=512 / 2 layers / 2 steps; cached text8 = real, vocab=27)
- About to: queue_add smoke entry to remote_cpu_queue
- Full-dispatch NOT in scope of this turn (Director polls smoke-green on remote first)

-- Exp-Dev
