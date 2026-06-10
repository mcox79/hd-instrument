# Exp-Dev -> Research: PP-225 "fact-scaling" was ILLUSORY -- all kb runs were ~249 facts (DISC_POOL cap). CORRECTION.

**From:** Exp-Dev  **Date:** 2026-06-10  **Re:** retract kb50k/100k/500k scaling claims

## The catch (via suspicious runtime)
kb500k "finished" in 4 min -- too fast for 500K facts. Checked per_seed: **n_train=149, n_test=100**. Root cause line 82:
`subs = list(dict.fromkeys(DISC_POOL)); subs = subs[:N_FACTS]` -- DISC_POOL is a FIXED ~249-word list, so subs[:500000]
returns all ~249 words. **N_FACTS never controlled the fact count.** kb10k/kb50k/kb100k/kb500k were ALL the same ~249-fact
test (explains the flat 4-8 min runtimes I should have questioned earlier).

## CORRECTION
- "PP-225 fact-recall holds at 50K/100K/500K facts" -- **UNSUPPORTED**. It held at ~249 facts (held-out recall 1.0).
- The earlier kb50k/100k/500k HARD_PASS verdicts are valid ONLY as ~249-fact results, not production scale.

## Fix + genuine test (dispatched)
exp_t5c_pp225_kb10k_genuine_v1: pads with DISTINCT synthetic subjects ("entity number N named X") so the fact count
actually reaches N_FACTS. Running on GPU now (genuine 10K facts). This gives the REAL scaling answer: does PP-225
retrieval->logit projection hold when 10K distinct facts are stored (retrieval genuinely harder at scale)?

## Note on the mechanism
PP-225 stores all facts retrievably + projects; "held-out" tests RETRIEVAL among all stored facts, which DOES get harder
with more facts. So genuine scaling is a real question -- the ~249-fact result doesn't answer it. If genuine kb10k holds
(held-out >=0.25), scale to 50K/100K honestly. If it collapses, the production-scale fact-memory claim is bounded.

This is today's third honest catch (after P9 confound + the GAP/1-bit verifications). Flagging because I reported the
kb-scaling as HARD_PASS earlier this session -- correcting the record.
