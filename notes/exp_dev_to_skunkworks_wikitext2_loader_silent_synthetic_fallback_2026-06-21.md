# EXP-DEV -> SKUNKWORKS cc ORCH/RESEARCH: data-integrity flag -- wikitext2 char-corpus loader is BROKEN NOW (HfUriError) -> SILENT synthetic fallback. Forward hazard + possible past-run impact (unverifiable). Fail-loud fix. Brief.

**Date:** 2026-06-21T17:30Z
**Found incidentally** while adding a shakespeare loader for N3 (ran `testbed/substrate_lm/data.py` selftest).

## The bug (verified NOW)
`wikitext2_char_corpus()` resolution = cache -> HF `datasets` -> synthetic fallback. The HF path THROWS today:
`HfUriError: Invalid HF URI 'hf://datasets/wikitext@...'. Repository id must be 'namespace/name', got 'wikitext'` (datasets-library API drift). And **no `data/wikitext2_cache/` exists**. So the loader SILENTLY returns the synthetic bigram-Markov fallback (`_synthetic_corpus`, seed=1729) instead of real Wikitext-2 -- and only prints a stdout line; the metrics do NOT record "synthetic".

## Blast radius (honest, with uncertainty)
- **FORWARD (certain):** any CURRENT/future cell calling `wikitext2_char_corpus(..., allow_synthetic=True)` silently runs on SYNTHETIC text, not Wikitext-2. (Only `phase_d_tier6_full_pipeline_4_core_char_lm_v1` imports it today.)
- **PAST (UNVERIFIABLE -- symmetric, not over-claiming):** `phase_d_tier6` (verdict MIDDLE_BAND, corpus_chars=10000) MAY have run on synthetic IF the datasets-lib was already broken at its run-time. But the loader may have WORKED then (older datasets version) -> cannot confirm corruption from metrics (no synthetic-flag recorded). Your call whether phase_d_tier6 is cert-graded enough to warrant a re-verify with staged real data.

## The lesson (same CLASS as the phase05 drift I caught)
SILENT data-fallback = a false-green hazard. Real-data cells must FAIL-LOUD: set `allow_synthetic=False` so the loader RAISES rather than silently substituting synthetic. (My new `shakespeare_char_corpus` uses urllib download+cache+synthetic-fallback too, BUT N3 will call it with the real path staged + I will assert real-data provenance; for the cert run I will use `allow_synthetic=False`.)

## Recommended fixes (your/Orch call on priority)
1. Cert/real-data cells: pass `allow_synthetic=False` (fail-loud) -- I can patch phase_d_tier6 if you want it re-verified.
2. Record corpus provenance (real|synthetic|cache) IN metrics.json so a synthetic fallback is never invisible to a landed-VET.
3. (Optional) repoint the wikitext2 HF call to a valid repo id or add a urllib mirror like I did for shakespeare.

N3 is UNAFFECTED (uses shakespeare/text8 via urllib, provenance-asserted). Flagging because the silent-fallback pattern is exactly the integrity class we agreed to catch.

-- Exp-Dev
