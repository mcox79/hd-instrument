# Testbed: B2 Path A Toggle - Design Doc (draft 2026-06-10)

**Author:** Testbed  **Status:** draft (offline / runner unreachable)  **Audience:** Self + Research + Exp-Dev review

## Goal

Live in-browser toggle exhibit demonstrating the Path A architecture claim from
research_to_testbed_PATH_A_PACKAGE_INTO_DEMO_2026-06-09.md:

> "Substrate-attention measurably improves Pythia-160M perplexity by ~16% (3-seed
> std 0.001). v2.0 substrate-intrinsic architecture is empirically grounded."

User toggles substrate-attention ON/OFF on a fixed evaluation passage. Live PPL
delta renders. This is the architectural-evidence Panel B exhibit.

## Honest scope (per OVERCLAIM_CORRECTIONS 2026-06-10)

This exhibit demonstrates ONLY the architecture-improvement claim. It does NOT:
- Demonstrate v2.0 product (substrate IS the LLM's memory) -- that is Path B R&D
- Claim categorical advantage over LLMs at language modeling
- Claim translation / aesthetics / continual-learning parity (per retractions)

What it DOES demonstrate empirically:
- Substrate-attention layers, gated and trained per the published recipe
  (gate-lr 1e-3 + LayerNorm + warmup/cosine + grad-clip 1.0 + Adam betas 0.9/0.95),
  reduce frozen Pythia-160M's NLL by ~16% on the eval passage
- Reproducible across 3 seeds at std 0.001

## Architecture

```
                                                  ┌─────────────────────────┐
                                                  │  /demo/path_a (HTML)    │
                                                  │  fixed eval passage     │
                                                  │  [ ] substrate-attention│
                                                  │  baseline PPL: 24.3     │
                                                  │  + substrate: 20.4 (-16%)│
                                                  └────────┬────────────────┘
                                                           │ POST /eval/path_a
                                                           ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ backend/routes/eval_path_a.py                                                 │
│                                                                               │
│   1. Tokenize passage with Pythia-160M tokenizer                              │
│   2. Forward pass through Pythia-160M (frozen)                                │
│      - if substrate_attention == True: insert Flamingo-gated cross-attn       │
│        adapter at L4+L5, with substrate hidden states as keys/values          │
│   3. Compute mean per-token NLL across passage                                │
│   4. Return: baseline_nll, substrate_nll, ratio, delta_pct                    │
│                                                                               │
└────────┬─────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│ backend/llm/path_a.py                                                         │
│                                                                               │
│   load_path_a_adapter(ckpt_path) -> FlamingoAdapter (frozen)                  │
│   forward_with_adapter(pythia, ids, adapter, layer_ids=[4, 5])                │
│                                                                               │
│   FlamingoAdapter:                                                            │
│     gated_cross_attn(query=pythia_hidden, key=substrate_kv, value=substrate_kv)│
│     gate is per-layer learned scalar (sigmoid in [0, 1])                      │
└────────┬─────────────────────────────────────────────────────────────────────┘
         │ substrate_kv comes from the in-memory substrate state at query time
         ▼
backend/substrate state (already loaded for /converse etc.)
```

## Dependencies (blockers)

1. **Path A .pt checkpoint** -- 3-seed-mean Pythia-160M Flamingo adapter (L4+L5)
   - Not currently in local repo
   - Most likely lives on runner under data/testbed_pp8_week2/train_v1b_c10/*.pt
     or in lambda_batch_results/pp8_w2_v1b_c10_path_a_paraphrase_h100_2dac0134
     (result_paths_summary.json shows match-count 0; possibly a rsync-back gap)
   - **ACTION:** when runner returns, locate or request .pt + scale config from
     Exp-Dev via testbed_to_exp_dev note
2. **Pythia-160M weights** -- ~330 MB; sufficient to run on runner CPU (no GPU
   required for inference at 1-passage scale)
3. **Substrate hidden states for cross-attention keys/values** -- this is the
   subtle part: Path A used "past-token hidden states" as the substrate
   placeholder during research training. For demo, we must either:
   - **Option A (faithful to training):** use Pythia's own prior-context
     hidden states (the same data used in training). This faithfully
     reproduces the architecture but doesn't actually showcase substrate.
   - **Option B (substrate-grounded):** use real substrate retrieved-fact
     hidden states (bge-encoded facts projected to Pythia hidden dim). This
     deviates from training distribution. NLL will not match the 0.836x.
   - **Recommended:** Option A, with note. Option B is HYBRID territory (B3).

## Endpoint contract

`POST /eval/path_a`

```json
{
  "passage": "...",                  // up to ~512 tokens; default = curated eval passage
  "substrate_attention": true,
  "layers": [4, 5]                   // optional override; default = [4, 5]
}
```

Response:

```json
{
  "n_tokens": 256,
  "baseline_nll": 3.197,
  "substrate_nll": 2.685,
  "ratio": 0.840,
  "delta_pct": -16.0,
  "ppl_baseline": 24.46,
  "ppl_substrate": 14.66,
  "latency_ms_baseline": 412,
  "latency_ms_substrate": 488,
  "head_source": "ckpt:path_a_pythia160m_3seed_mean_v1.pt",
  "notes": "passage NLL averaged per-token; substrate-attention inserted at layers [4, 5]"
}
```

For toggle UX, the page makes TWO calls (one baseline, one substrate) on load
and on passage edit. Both numbers render side-by-side. Per-token NLL is the
honest metric; PPL = exp(NLL) for headline.

## Frontend

`/demo/path_a` HTML page sketch:

```
┌──────────────────────────────────────────────────────────────┐
│ Pythia-160M + substrate-attention (Path A)                  │
│                                                              │
│ Eval passage (editable):                                     │
│ ┌────────────────────────────────────────────────────────┐  │
│ │ [textarea: default curated paragraph; ~256 tokens]     │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                              │
│ ┌─ Baseline ──────────────┐  ┌─ Substrate-attention ─────┐  │
│ │ PPL: 24.46              │  │ PPL: 14.66                 │  │
│ │ NLL/token: 3.197        │  │ NLL/token: 2.685           │  │
│ │ wall: 412 ms            │  │ wall: 488 ms               │  │
│ └─────────────────────────┘  └────────────────────────────┘  │
│                                                              │
│ Delta: -40% PPL (substrate-attention layers at L4+L5)        │
│                                                              │
│ [↻ Re-evaluate]   [📋 Copy reproducibility recipe]            │
│                                                              │
│ Recipe (open-state): gate-lr 1e-3 + LayerNorm + warmup/cosine│
│ + grad-clip 1.0 + Adam betas 0.9/0.95. 3-seed std 0.001.     │
│ Checkpoint: path_a_pythia160m_3seed_mean_v1.pt.              │
└──────────────────────────────────────────────────────────────┘
```

Honesty footer (per OVERCLAIM_CORRECTIONS): "This exhibit demonstrates the
architecture claim only (substrate-attention layers reduce PPL on Pythia-160M).
It does not claim categorical LM parity with frontier LLMs. v2.0 product
(substrate as the LLM's persistent memory) is Path B R&D and is not shown here."

## Implementation plan (~1 day on returned runner)

1. **30 min:** Write `backend/llm/path_a.py` with FlamingoAdapter class +
   `load_path_a_adapter(ckpt_path)` + `forward_with_adapter(...)`.
2. **30 min:** Write `backend/routes/eval_path_a.py` per contract above.
3. **15 min:** Mount router in `backend/main.py`; add `/demo/path_a` HTML page
   (similar pattern to verticals.py).
4. **15 min:** Verify Pythia-160M weights cache loads on runner; cache locally
   if not.
5. **45 min:** Locate Path A .pt checkpoint OR file note to Exp-Dev for one.
6. **30 min:** Smoke test: confirm baseline and substrate calls return; confirm
   delta is approximately -16% on a held-in passage (or document the actual
   delta if eval passage is novel).
7. **15 min:** Add to /demo nav; smoke test in browser.

## Risk and gotchas

- **Latency:** Pythia-160M forward on CPU for 256 tokens is ~400ms. Two calls
  per toggle change = ~800ms. Acceptable for an exhibit but worth a "computing..."
  spinner.
- **Checkpoint shape mismatch:** if Exp-Dev's checkpoint uses different
  hidden_dim / n_heads / gate config than the demo loader expects, load will
  fail. Build the loader to read all config from the .pt's accompanying
  config.json (same pattern as PP-225 head's W + scale fields).
- **Substrate-state vs past-tokens K/V:** must NOT silently substitute one for
  the other. If using past-tokens (Option A, faithful), label exhibit
  "substrate-attention architecture demo." If using real substrate (Option B),
  that's HYBRID and belongs in B3, not B2.
- **Eval passage choice:** must be held-out from Path A training data. Use a
  paragraph not from the C4 training distribution if possible (e.g., a Wikipedia
  paragraph from a freshly-ingested topic in Stage A's wikipedia_full).

## Open questions for Exp-Dev (file as note when runner returns)

1. **Q1:** Path A .pt checkpoint location + state-dict schema?
2. **Q2:** During training, what was the substrate K/V source? (past-token hidden
   states? substrate retrieval? mixed?) Need this to match training distribution
   at inference for the 0.836x ratio to hold.
3. **Q3:** Eval passage used in the published 0.836x metric -- can we reuse it
   as the default demo passage?
4. **Q4:** Recommended cache_dir for Pythia-160M weights on the runner (probably
   the same as PP-225 endpoint's; verify).

## What this does NOT do (and how B3 extends it)

B2 ships the architecture toggle. B3 (HYBRID composed backend) extends it by
running Path A AND PP-225 simultaneously on the same query:
- Path A modifies attention layers L4+L5 with substrate-grounded K/V
- PP-225 projects retrieved-fact embeddings into the final logits
- Both compose; the head's contribution is observable in token rankings
- B3 page shows: baseline | Path A only | PP-225 only | HYBRID, with PPL +
  retrieved-fact attribution traces for each

B3 design doc: testbed_B3_HYBRID_COMPOSED_DESIGN_2026-06-10.md (next).

## Status

- Design: drafted
- Runner: unreachable (~5 hr Tailscale offline)
- Implementation: blocked on (a) runner return, (b) .pt checkpoint location
- Next action on runner return: file Q1-Q4 to Exp-Dev; start step 1-3 in parallel
- Honesty audit: passes OVERCLAIM_CORRECTIONS 2026-06-10 (architecture claim only;
  no LM parity / memory product claim made by this exhibit)
