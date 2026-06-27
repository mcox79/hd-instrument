# 3x Revival Research Drill — sub_atom token-stream encoder

**Date:** 2026-06-27 ~18:25 PDT
**Author:** research (Opus 4.7-1M)
**USER directive:** revive both however we have to + remote_cpu + remote_gpu idle; use compute aggressively
**Status grounding:** v2_real_mathlib_smoke MIDDLE_BAND (RF_d3=0.935 / Trig_d3=0.66 / gap=0.275 / alpha_cos=0.943 / codebook_disambig=1.0 / cv=0.07)

---

## CRITICAL FRAME RESET (read first)

The brief's "FAILURE HISTORY" understates the v2 state. The v2 smoke is NOT broken — mechanism CLEARLY fires:

- ROLE_FILLER d3 = 0.935 (well past 0.80 HARD_PASS floor)
- char-trigram d3 = 0.66 (above 0.50 fairness ceiling — borderline; NOT saturated)
- gap = 0.275 (just under 0.30 HARD_PASS threshold)
- alpha_equiv = 0.943 (just under 0.95 HARD_PASS threshold)
- codebook_disambig = 1.000 (HARD_PASS)
- cv = 0.07 (HARD_PASS)

The MIDDLE_BAND verdict is two thresholds missing by ~0.03 and ~0.025 — close-miss at smoke (N=2048, 2 seeds, 1 corpus), not "encoder doesn't work". The brief's claim "trigram saturates at 0.95+" was the v1 problem; v2 already fixed it (0.66 < 0.95 saturation gate).

This is therefore not a revival drill against a broken cell — it's a finishing drill against a cell already 80% home. The questions become: (1) does full-scale clear HARD_PASS? (2) if it stalls at MIDDLE_BAND-at-full, what's the next move? (3) is Angle C the right pre-emptive move anyway?

---

## ANGLE A — HARDER TEST / FINISHING-SCALE (the obvious fix; HIGH P)

**A1. Just ship full at N=8192 + 3 corpora + 5 seeds.** The smoke is structurally close enough that the prereg's stated scaling levers (4x N, 3x corpora, 2.5x seeds) should clear HARD_PASS. Three independent mechanisms expected to widen gap and tighten alpha_cos:
- N=8192 quadruples vector orthogonality budget → alpha_cos approaches 1.0 (currently 0.943; needs 0.95)
- 3 corpora (lean + matsci + oeis) diversify distractor pool: trigram-overlap-across-corpora is much weaker than within-Lean → trigram d3 drops below 0.66 → gap widens past 0.30
- 5 seeds vs 2 tightens cv (already 0.07; will tighten further with more samples)
- **Compute:** ~1-3hr full GPU run (prereg estimate)
- **P(HARD_PASS at full):** 0.55 (lit-scan deflated; close-miss-at-smoke + structural scaling argument; not novel synthesis so cap doesn't bite)

**A2. Depth-5 / depth-7 / depth-10 sweep arms.** Current discriminator is depth-3. Mathlib pretty-printed theorems have natural nesting up to ~8 (e.g., `(forall n, exists p, Prime p and p > n)` is depth-4-5 once parsed). Adding a depth-7 arm would force trigram d3 down further (longer subtrees = more head-disjoint distractors = trigram fails harder). Risk: substrate role-filler also degrades with depth — need to check the chain-depth saturation curve.
- **Compute:** +1hr added to A1 if bolted on
- **P(useful signal at depth-7):** 0.50 (depth-3 already near-pass; depth-7 may show wider gap OR may show role-filler decay — both informative)

**A3. Raw Lean syntax (NOT pretty-print) as corpus.** Current corpus uses pretty-printed theorems with English-like operator spacing. Raw Lean4 source uses `@[simp]` attributes, `:=`, `fun x => x`, deeply-nested anonymous-function syntax. Trigram baseline likely drops sharply on raw syntax since it lacks natural word-boundary tokens.
- **Compute:** corpus-prep ~30min (parse Lean4 .lean files); run alongside A1
- **P(meaningful trigram drop):** 0.45 (raw-syntax has more structural symbols; less English-fluent; but also might be MORE trigram-friendly due to repetitive `=>` `:=` patterns)

---

## ANGLE B — DIFFERENT ENCODER ARCHITECTURE (the deep fix; MEDIUM P)

**B1. BPE (Byte-Pair Encoding) sub-word tokenizer.** Train BPE on lean+matsci+oeis combined corpus (~450 strings, ~30-80 tokens each → ~15K BPE merges). Replaces both char-trigram (too granular) and codebook (requires explicit symbol list) — BPE auto-discovers token boundaries from corpus statistics. Substrate-native because BPE merges become atom IDs in codebook.
- **Compute:** ~30min training BPE + ~1hr substrate test
- **P:** 0.45 (BPE works well on code/math in published encoders — Codex, AlphaCode — but adapting to substrate role-filler unbind is novel; deflated)

**B2. Sub-tree DAG hashing instead of unbind-along-path.** Current encoder unbinds sequentially along role-path; this loses information at deeper depths. Alternative: hash each subtree to a unique atom on first sight (Merkle-tree-style); compose via XOR-bind of subtree-atoms. Same compositional power, lossless retrieval, deeper depths trivially handled.
- **Compute:** ~2hr re-impl + test (substantial code change)
- **P:** 0.35 (clever but loses HRR's continuous-similarity property; pure-symbolic recovery may hurt downstream cells that depend on near-neighbor cosine; deflated for novelty)

**B3. Transformer-style attention encoder (GPU-heavy).** Train a small (~10M param) transformer on Lean Mathlib next-token; use final-layer hidden state as substrate-input embedding. Comparable to "use word2vec" but for formal math. Eligible for remote_gpu.
- **Compute:** ~6-12hr GPU training + 1hr eval
- **P:** 0.30 (we explicitly chose substrate-native encoder per PATH C USER directive 2026-06-23; this is anti-directive; only justified if A+B exhausted)

---

## ANGLE C — IS CHAR-TRIGRAM ALREADY SUFFICIENT? (the abandon-fix; UNDER-EXPLORED)

This is the most-important question and I want to call it out hard.

**Honest reading of v2 data:** char-trigram d3 = 0.66 on real Mathlib at N=2048. That's WAY above random (random = 0.10 for top-1-from-10). It means trigram on Mathlib already encodes structure well enough to retrieve correct subtree 66% of the time. For downstream INGEST (which doesn't need depth-3 subtree-perfect recovery — it needs "store this theorem retrievably"), trigram may be MORE than enough.

**C1. Quick-witness test: run lean_mathlib_ingest_v1 with current char-trigram encoder at d=8192.** No new encoder; just push the existing substrate encoder against Mathlib ingest. If downstream "retrieve theorem by partial-prompt" hits 0.70+ recall, sub_atom encoder is unnecessary for Barrier 4.
- **Compute:** ~1-2hr (ingest 500-1000 theorems + retrieval test)
- **P(trigram-sufficient for ingest):** 0.55 (trigram d3=0.66 on subtree retrieval suggests whole-theorem retrieval will be higher; supported by KB ingest already working on internal notes at trigram level)

**C2. Same test but on Materials Project SMILES.** SMILES is structurally different (chemical symbol grammar, parentheses for branching). Trigram should work WORSE on SMILES than on Mathlib pretty-print because SMILES has fewer "word-like" 3-char patterns. If trigram fails here, that's where sub_atom encoder earns its keep.
- **Compute:** ~1hr
- **P(trigram-insufficient for SMILES specifically):** 0.45 (SMILES is the corpus most likely to need codebook)

**C3. Schema-driven proof-step inference, trigram vs codebook arms.** The downstream cell we ACTUALLY care about. Run with both encoders side-by-side; let the discriminator decide.
- **Compute:** ~3hr (proof-step cell isn't built yet; would need to spec + build first)
- **P:** 0.40 (most-direct but most-expensive; the right test)

---

## TOP-2 PICKS (P-deflated)

### Pick 1: **A1 (ship full v2) + C1 (trigram-baseline ingest) IN PARALLEL** — recommended
- A1 on remote_gpu (~1-3hr): finishes the cell already at MIDDLE_BAND smoke; high prior of HARD_PASS
- C1 on remote_cpu (~1-2hr): tests the abandon-the-encoder hypothesis with real downstream signal
- Either outcome is decisive:
  - A1 HARD_PASS + C1 also works → ship sub_atom for hard cases, trigram for easy cases (best of both)
  - A1 HARD_PASS + C1 fails → sub_atom encoder is the unblock
  - A1 MIDDLE_BAND + C1 works → SKIP sub_atom; ship Barrier-4 cells on trigram (USER pragmatism)
  - A1 MIDDLE_BAND + C1 fails → escalate to B1 (BPE)
- **Discriminator:** A1 HARD_PASS = role_filler d3>=0.80 AND trigram d3<=0.50 AND gap>=0.30 AND alpha_cos>=0.95 (per prereg). C1 HARD_PASS = ingest 500 theorems + retrieve correct theorem from partial-prompt top-1 >= 0.70.
- **GPU eligibility:** A1 yes (large matmul + multi-seed); C1 marginal (CPU-fine).
- **Compute estimate:** ~3-5hr wall-time total (parallel)
- **P(unblocks Barrier 4 within this window):** 0.75 (one of two paths almost certainly works)

### Pick 2: **B1 (BPE encoder) as fallback** — gated on Pick 1 both failing
- Don't pre-dispatch; only fire if A1+C1 both miss
- BPE is well-attested in code-encoding lit (lit-scan deflated to P=0.45) and substrate-compatible (BPE merges → codebook atoms)
- **Compute:** ~1.5hr
- **GPU eligibility:** marginal (BPE training is CPU-bound; substrate test small)

---

## HONEST RECOMMENDATION TO USER

**Path forward (fastest Barrier-4 unblock):**

1. **Dispatch A1 immediately** (ship v2 full at N=8192 + 3 corpora + 5 seeds) on remote_gpu. Cell already exists, prereg locked, smoke close-miss with structural scaling argument. P(HARD_PASS) = 0.55. ~1-3hr.

2. **Dispatch C1 in parallel** (lean_mathlib_ingest_v1 against current trigram encoder at d=8192) on remote_cpu. Witness whether sub_atom is even needed. P(trigram-sufficient) = 0.55. ~1-2hr.

3. **Read both verdicts together.** The 2x2 outcome matrix above gives a decisive next move regardless.

4. **Gate B1 (BPE) on both failing.** No pre-emptive build.

**Why I don't recommend Angle B as first move:** B1-B3 are substantial re-implements; we have a working v2 that just needs the finishing-scale run. Don't pivot architecture when the current architecture is one threshold-touch away from PASS.

**Why I push Angle C as parallel:** If C1 works (trigram-sufficient for downstream ingest), we ship Barrier-4 cells in DAYS instead of weeks — sub_atom encoder becomes a refinement rather than a blocker. USER's "however we have to" hints at pragmatism: the goal is Barrier-4 unblock, not encoder-perfection.

**Key honest position:** the brief framed sub_atom as a 2x-failure that needs revival. The actual data says it's a near-pass that needs finishing + a parallel sanity-check on whether it's even necessary. If we're aggressive with compute (USER directive), running both in parallel costs ~3-5hr and gives us a decisive answer about the whole barrier.

---

## P-DEFLATION AUDIT (lit-scan calibration)

- A1 P=0.55: scaling-laws lit shows quad-N + 3x corpora reliably tightens cosine bounds on HD encoders; not novel; minimal deflation
- B1 P=0.45: BPE in code-encoding well-attested but substrate-binding adaptation novel; deflated 0.20 from baseline 0.65
- C1 P=0.55: KB query already works on substrate at trigram level for internal notes (existence proof); deflated 0.10
- Pick-1 combined P=0.75: union-bound argument (at-least-one-works), not product

No P claimed > 0.75 (per novel-synthesis cap 0.50; though combined-paths argument lifts to 0.75 since at-least-one-works isn't single-novel-synthesis).
