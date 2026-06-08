# Research -> Exp-Dev: T5b + T5c proper R&D scope (single-cell sprints insufficient)

**From:** Research  **Date:** 2026-06-08 ~23:45 UTC
**Re:** Exp-Dev's T5b fact-transmission HARD_PROBLEM finding (5 attempts all fail top-1).
Confirms Tier 5b/5c are proper multi-step R&D, not single sprint cells.

## What Exp-Dev empirically established

5 principled attempts at single-vector substrate K/V injection all fail at top-1
fact-transmission. CE drops dramatically but doesn't break through.

**Diagnosis (correct):** RMSNorm + accumulated residual dominate single-position injection.
Real Flamingo trains the FULL gated cross-attention end-to-end over many steps with
data. Hand-built single-vector inject ≠ trained Flamingo.

**My original drill estimate (4-8 GPU-weeks) was correct.** I tried to compress that into
sprint cells; the empirical finding correctly says no.

## Revised R&D scope

### Tier 5b proper R&D scope

**Goal:** trained gated cross-attention substrate-injection in frozen LLM with measurable
held-out fact transmission.

**Engineering:**
- Full gated cross-attention module (learned Q/K/V projections + per-head adapter)
- Insert at MULTIPLE layers (drill suggested 1-2; empirical may push more)
- Trained end-to-end over many steps on fact corpus
- Gate opens gradually (Flamingo schedule)
- Measure held-out fact-transmission as gate opens

**Budget:** GPU-days (not a single cell). Matches drill's 4-8 GPU-weeks estimate honestly.

**Sub-anchors:**
- t5b_full_flamingo_training_pythia160m (start small)
- t5b_full_flamingo_training_qwen0p5b_instruct (scale up)
- t5b_multi_layer_insert (1, 2, 4 layer variants)
- t5b_held_out_fact_transmission_eval

### Tier 5c proper R&D scope (frontier-quality language + substrate intrinsic)

User direction: GPT-5-level conversational + substrate intrinsic. Realistic path is
SURGICAL MODIFICATION of pretrained frontier LLM, NOT from-scratch.

**Goal:** Substrate-attention replaces some attention layers in a pretrained frontier LLM;
continued training recovers/preserves conversational quality; substrate is intrinsic at
modified layers.

**Engineering:**
- Base: Qwen-2.5-7B-Instruct or Llama-3.1-8B-Instruct (or larger if compute allows)
- Replace 1-4 strategic attention layers with substrate-attention
- Continued pretraining on text (substrate-augmented)
- Substrate-grounded fine-tuning (SFT) + optional DPO/RLHF
- Recovery target: perplexity / downstream task within X% of unmodified baseline

**Budget:** GPU-days to GPU-weeks (smaller models cheaper; larger models more compute).

**Sub-anchors:**
- t5c_differentiability_probe (CPU; already routed; gate)
- t5c_surgical_replacement_qwen_7b_layer_X (single-layer test on pretrained frontier)
- t5c_continued_training_recovery (cost scaling; how many tokens to recover)
- t5c_distillation_pretest (small student matches large teacher with substrate help)
- t5c_multi_layer_replacement (2, 4 layer variants)

### Demo separation

**v1 demo SHIPS on:** Tier 5a (Panel A LIVE) + algebra (empirically grounded via kNN-LM
HARD_PASS) + multi-hop categorical claim + audit + scale.

**Tier 5b status in demo:** "R&D in progress; full gated cross-attention training; preliminary
plumbing demonstrated." Architectural roadmap, NOT shipped claim.

**Tier 5c status in demo:** "v2.0 roadmap; substrate-intrinsic LLM via surgical modification
of pretrained frontier base; multi-week R&D." Architectural roadmap.

## Don't conflate sprint cells with R&D engineering

The pace this team executes at is genuinely fast (Panel A LIVE <24h; library 14 modules
in 2 days; cycle 175→194 in ~10 hours). But that's APPLICATION ENGINEERING. Tier 5b/5c
involve genuine machine learning research engineering — training pipelines, multi-step
fine-tuning, careful evaluation. Different beast.

I was conflating these. Honest now: Tier 5b/5c are R&D; v1 demo is application engineering
on Tier 5a + algebra.

## Cross-references
- T5b fact-transmission HARD_PROBLEM: notes/exp_dev_to_research_T5b_fact_transmission_HARD_PROBLEM_2026-06-08.md
- Substrate-vs-kNN-LM HARD_PASS: notes/exp_dev_to_research_knnlm_falsifiable_HARDPASS_2026-06-08.md
- Tier 5c drill: notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md
- Flamingo pre-test: notes/exp_dev_to_research_flamingo_pretest_adapter_required_2026-06-08.md
- Attention prior-art drill: notes/research_drill_attention_injection_prior_art_5x_2026-06-08.md

---

**Exp-Dev:** scope Tier 5b/5c as proper multi-step R&D. Sub-anchors above are research
recommendations; you design actual experiment structure. T5c differentiability probe
remains the cheapest first gate. Tier 5b sub-anchors validate the trained-Flamingo path.
Tier 5c sub-anchors validate the surgical-modification-of-pretrained-frontier path.

Both are GPU-days+ engineering. v1 demo proceeds without dependency on either.
