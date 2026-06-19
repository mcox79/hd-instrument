# exp_dev hand-off -- research: statistical_NL_creative_2x

**Filed by:** research sub-agent (Sonnet 4.6)
**Date:** 2026-06-11
**Trigger:** notes/research_drill_statistical_NL_creative_2x_2026-06-11.md
**Cycle context:** User mandate drill on statistical NL fluency + open-ended creative generation.
  PP-331/342/345 validated. Autoregressive generation (wave14d K=16 p1=43.3%) confirmed.
  Zipf load-bearing confirmed. Gap: fluency at LLM grade + open-ended creative production.

---

## Pause state block

Per [[feedback-no-experiment-design-in-prompts]]: this file contains anchor candidates and context
pointers ONLY. Experiment design (HP choices, cell structure, code) is exp_dev's responsibility.
Do not encode experiment design in this file.

---

## What the research found

The fluency and creative generation gaps are engineering gaps, not theoretical ceilings. The substrate
already generates text via autoregressive pool retrieval (wave14d K=16, +15.5pp over Markov baseline).
Ten concrete paths close the gap progressively. The cheapest and most informative paths are:

1. Temperature sampling (PATH 3) -- trivial 1-hour addition, answers Q5, do first
2. Zipf-weighted codebook + 10K trigram N-gram superposition (PATHS 1+2) -- 2 hours CPU, answers Q1/Q4
3. Structured template generation extension of PP-331 (PATH 8) -- 1 hour CPU + human raters, answers Q2

The structured template path (PATH 8) is the highest-confidence route to human-ratable creative text
because it uses validated PP-331 machinery. The Levelt 4-hop chain (PATH 4) is the most informative
single new capability test.

LVH-280 (POS tagger corpus_load_failed) needs a re-run with corpus fix before PP-362 is fully credited.

---

## Anchor candidates (rank-ordered)

### Rank 1: stat_nl_temperature_sampling (Temperature policy, Q5 -- Tier 0/trivial)

- Anchor pointer: stat_nl_temperature_sampling
- Substrate-product reading: adds temperature-controlled diversity to existing autoregressive
  generation. Controllable diversity vs coherence tradeoff. Product: configurable generation mode.
- Tier hint: Tier 0 (trivial extension of existing generation loop; no new mechanism)
- Why-now: The generation loop already exists (wave14d_generation_v2_K16). This is a 10-line change.
  Pre-reg: HARD_PASS if entropy varies >= 1.5 bits across T=0.1 to T=1.0. 1 hour CPU.

### Rank 2: stat_nl_zipf_codebook_ngram (Zipf codebook + 10K trigram store, Q1/Q4 -- Tier 1)

- Anchor pointer: stat_nl_zipf_codebook_ngram
- Substrate-product reading: frequency-weighted atom allocation + 10K trigram superposition.
  Tests whether BLEU-2 >= 0.18 and recall@1 >= 0.80 at N=65536. Links to k3_zipf_falsifier.
- Tier hint: Tier 1 (incremental; builds on existing K=3 generation + Zipf load-bearing result)
- Why-now: k3_zipf_falsifier HARD_FAIL confirmed Zipf is load-bearing. The Zipf codebook is the
  direct next engineering step. N=65536 is needed; local CPU can handle this scale.

### Rank 3: stat_nl_structured_template_creative (PP-331 extension to creative templates, Q2 -- Tier 1)

- Anchor pointer: stat_nl_structured_template_creative
- Substrate-product reading: extend PP-331 6-slot paragraph compose to real KB content as slot fills
  for story/narrative schemas. Human-ratable creative output from substrate-only infrastructure.
  Product: auditable story generation (visible KB provenance per slot).
- Tier hint: Tier 1 (direct extension of PP-331 HARD_PASS machinery; no new mechanism)
- Why-now: PP-331 is 5-seed confirmed (wave1_multiseed_sweep). The slot-fill infra exists.
  Human rating study can be run with 5 raters on 10 generated stories (2-3 hours total).

### Rank 4: stat_nl_levelt_4hop (Levelt 4-hop pipeline, Tier 1)

- Anchor pointer: stat_nl_levelt_4hop
- Substrate-product reading: concept -> lemma -> morphological form -> phonological form as
  4-hop heteroassoc chain. PP-9b validated depth-3 fidelity=0.986. Tests depth-4 extension.
- Tier hint: Tier 1 (one rung beyond validated depth-3 heteroassoc chain)
- Why-now: The depth-3 result is confirmed. Depth-4 is the next rung. Expected fidelity > 0.95
  based on depth-3 result; hard to know without testing. 1 hour CPU.

### Rank 5: pos_tagger_corpus_fix (LVH-280 re-run -- Tier 0 cleanup)

- Anchor pointer: pos_tagger_ptb_corpus_fix
- Substrate-product reading: LVH-280 was filed (cycle 229) because corpus failed to load on local
  runner. exp_dev commit e1c4f831 claims HARD_PASS 0.906. Re-run with corpus load fix to confirm.
  If confirmed: closes LLM-only-for-NL-parsing assumption (new PP row).
- Tier hint: Tier 0 (cleanup re-run; no new code)
- Why-now: LVH-280 is unresolved. The claim is significant (0.906 POS accuracy substrate-only).
  Should be resolved before using PP-362 as a portfolio anchor.

---

## Context pointers (file paths)

- Research note: d:/AI/hd-instrument/notes/research_drill_statistical_NL_creative_2x_2026-06-11.md
- Cap_map generation section: d:/AI/hd-instrument/notes/substrate_capability_map.md (AUTOREGRESSIVE
  GENERATION section, wave14d_generation_v2_K16 row)
- Prior generation result: d:/AI/hd-instrument/data/exp_wave14d_generation_v2_K16/metrics.json
- Zipf falsifier result: substrate_capability_map.md search "k3_zipf_falsifier"
- PP-331 paragraph compose: substrate_capability_map.md search "PP-331"
- PP-342 WUG morphological: substrate_capability_map.md search "PP-342"
- PP-345 translation: substrate_capability_map.md search "PP-345"
- LVH-280 POS tagger: substrate_capability_map.md search "LVH-280"
- PP-9b depth-3 heteroassoc: substrate_capability_map.md search "PP-9b"

---

## Contract section

This handoff provides 5 ranked anchor candidates with substrate-product readings and tier hints.
exp_dev picks order and design based on queue state, runner availability, and its own HP judgment.
Research does not specify cell structure, code, or HP values.

## Autonomy declaration

exp_dev has full autonomy on: which anchors to queue, in what order, with what HP, using what code
structure, on which runner. The anchor names above are suggestions, not mandates. If the queue is
full or a different anchor is more urgent, this handoff can wait.
