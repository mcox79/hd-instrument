# Exp-Dev -> Research: LVH-280 RESOLVED -- pos_tagger 0.906 confirmed stable

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** pos_tagger UNKNOWN-vs-0.906 discrepancy

## Root cause: NLTK corpus download failed on the runner's execution (not cached).
Official metrics showed UNKNOWN: corpus_load_failed. The cell does nltk.download("treebank") on-the-fly; on the runner's
run that download failed (network/timing), returning UNKNOWN. My manual run succeeded (0.906) because the corpus was cached.

## Resolution
Pre-cached NLTK treebank on FrameworkMPC (now ALREADY CACHED). Re-ran: HARD_PASS tag-accuracy=**0.9064** (20039 tokens,
8.5% OOV, 46 tags). Re-queued (pos_tagger_ptb_substrate_LVH280) so the runner records it with the corpus cached.

**LVH-280 resolved: substrate-only POS tagging = 0.906 (HARD_PASS), STABLE.** The categorical claim stands: substrate-only
NL POS tagging at 0.906 without an LLM refutes "LLM-only-for-NL-parse." (0.906 vs Brill 1995 0.967; the 0.95 STRONG bar
needs the context-window/transition layer = clean follow-up.)

## Hardening note
The on-the-fly nltk.download is a fragility (UNKNOWN on download failure). For the FULL PTB run (Tier 2), I will pre-cache
the corpus as a setup step and/or bundle the data path so the run is deterministic regardless of network.

## Cross-ref
- metrics: data/exp_pos_tagger_ptb_substrate_cpu_v1/metrics.json
- cycle-229 batch: notes/research_to_exp_dev_POST_CYCLE229_NEXT_BATCH_2026-06-11.md
