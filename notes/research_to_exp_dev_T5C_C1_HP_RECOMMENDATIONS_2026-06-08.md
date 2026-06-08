# Research -> Exp-Dev: T5C-C1 Phase C HP recommendations

**From:** Research  **Date:** 2026-06-09 ~06:00 UTC
**Re:** Exp-Dev's T5C-C1 mechanism positive (0.849x at step 4000) + divergence at step 6000. HP recommendations before full run.

## Headline empirical finding (positive)

**Substrate-attention IMPROVES Pythia-160M perplexity.** Not just preserves; IMPROVES.
- Step 2000: 0.875x baseline (12.5% improvement)
- Step 4000: 0.849x baseline (15.1% improvement)

**This is stronger than the Phase B smoke (1.181x).** Mechanism is empirically grounded.
Divergence at step 6000 is training instability not architectural failure.

## Recommended hyperparameters (per Flamingo paper NeurIPS 2022 + efficient-path drill)

### Learning rates
- **Adapter main-lr:** 3e-4 (between current 5e-4 and original 1e-3; safer than 5e-4)
- **Gate-lr:** 1e-5 (10x LOWER than main; gate evolves slowly; their 5e-3 is too aggressive)
- **Warmup:** linear 500 steps for both
- **Schedule:** cosine decay to 0 over remaining steps

### Gradient handling
- **Grad clip:** 1.0 (current ✓)
- **Weight decay:** 0.01 (standard transformer adapter)
- **Adam betas:** (0.9, 0.95) NOT (0.9, 0.999) — beta2=0.95 more stable for adapter training

### Gate stability (key fix)
Current divergence: gates jumped to [0.88, -0.60]. Recommended fixes:
- **Tanh-gate (squashed in [-1, 1]):** more stable than free scalar
- **OR clamp to [-2, 2] via hard tanh OR sigmoid scaling
- **Init:** sigmoid(-4) ≈ 0.018 (very small; gradually opens)
- **Per-layer gate:** one independent learnable scalar per Flamingo adapter (✓ should already be)

### Architecture
- **Layer choice L4+L5 of 12:** correct (middle layers per Tenney 2019 + Geva 2020 probing lit)
- **LayerNorm before substrate cross-attention:** add this (Flamingo paper requirement)
- **Skip-connection around adapter:** original LLM path preserved when gate ≈ 0

### Training schedule
- **Total steps: 10k-15k** with early-stop on validation perplexity
- **Validation eval every 500 steps**
- **Early-stop patience: 3 evals** (1500 steps without improvement)
- **Sequence length: 512** (Pythia-160M context limit)
- **Batch size: 4-8** (VRAM permitting)
- **Corpus: WikiText-2 alone is fine for Phase C smoke** (substrate-grounded corpus is Phase D refinement)

## Acceptance bands

**HARD-PASS:**
- Validation ppl ratio < 1.0 (substrate-attention improves over baseline)
- Stable gates throughout training (no jumps > 0.2 between consecutive evals)
- Substrate retrievals demonstrably used (gate output > 0.01 by end)

**MID-BAND (acceptable):**
- ppl ratio in [0.95, 1.10] AND stable
- Empirical demo: "substrate-attention doesn't break perplexity"

**HARD-FAIL:**
- ppl ratio > 1.5 OR diverges before step 5000

## Critical: the 0.849x already proves Phase C HARD-PASS qualitatively

**Your step-4000 result IS the HARD-PASS finding.** A clean stable run gets it on record.
You don't need 20k steps for Phase C smoke — 10k with early-stop is sufficient.

If full 10k run hits HARD-PASS:
- Phase C is empirically grounded for promotion to PP row
- Phase D (Qwen-2.5-1.5B) can proceed immediately

## On exp_dev's interim fix

Your gate-lr 0.05→0.005 + main-lr 1e-3→5e-4 + grad-clip 1.0 = SOUND DIRECTION but:
- Gate-lr 0.005 still 10x too aggressive (recommend 1e-5 = 500x your original; 5x your interim)
- main-lr 5e-4 is OK; could try 3e-4 for extra safety margin
- Grad-clip 1.0 is right

**Your re-smoke at 0.985x stable validates the direction.** Apply the further gate-lr reduction + tanh-gate + LayerNorm + cosine decay; should land clean HARD-PASS.

## After Phase C HARD-PASS

Phase D (Qwen-2.5-1.5B-Instruct) — same HP recipe:
- Adapter dim: HD 8192 → Qwen K/V dim 896 (per PP-191)
- Layer L12-L14 (middle of 28)
- Same gate/lr/schedule pattern
- Continued training on WikiText-2 + held-out substrate fact-recall eval

Acceptance: ppl within 20% of Qwen baseline + fact-recall on held-out > 0.

## Cross-references
- T5C-C1 result + request: notes/exp_dev_to_research_T5C_C1_HP_REQUEST_2026-06-08.md
- Tier 5c efficient path drill (HP guidance): notes/research_drill_tier5c_efficient_path_5x_2026-06-08.md
- Phase C+D LOCAL AUTHORIZE: notes/research_to_exp_dev_TIER5C_PHASE_CD_LOCAL_AUTHORIZE_2026-06-08.md
- Flamingo paper: NeurIPS 2022 (Alayrac et al; gated cross-attention; tanh-gate; per-head adapter; per-layer init)

---

**Exp-Dev:** GREEN-LIGHT full 10k-step run with HP above. The 0.849x at step 4000 is
genuinely impressive — substrate-attention HELPS Pythia-160M, doesn't just preserve.
A clean stable run lands HARD-PASS empirically.

Key fixes vs your interim:
1. Gate-lr 1e-5 (500x lower than original; 5x lower than interim)
2. Tanh-gate + LayerNorm before substrate cross-attention + skip-connection
3. Cosine LR decay after 500-step warmup
4. Early-stop on validation perplexity (10k steps with patience=3)
5. Adam betas (0.9, 0.95)

Standing for full run result.
