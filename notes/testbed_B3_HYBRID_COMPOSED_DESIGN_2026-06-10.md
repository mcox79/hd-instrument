# Testbed: B3 HYBRID Composed Backend - Design Doc (draft 2026-06-10)

**Author:** Testbed  **Status:** draft (offline / runner unreachable)  **Audience:** Self + Research + Exp-Dev review

## Goal

Compose Path A (substrate-attention layers at L4+L5) AND PP-225 (substrate-grounded
logit injection at output head) on the SAME query, in a single Pythia-1.4B forward
pass. Demonstrate that the two substrate-LLM coupling mechanisms compose without
interfering, per PP-227 HYBRID anchor.

## What this exhibits empirically

A live four-way comparison on a fixed retrieval-style query:

| Mode             | What it shows                                              |
|------------------|------------------------------------------------------------|
| Baseline         | Pythia-1.4B alone, no substrate intervention                |
| Path A only      | Pythia-1.4B + substrate-attention at L4+L5 (architecture)   |
| PP-225 only      | Pythia-1.4B + retrieved-fact projection into output logits  |
| HYBRID           | Both mechanisms active simultaneously                       |

For each mode, the page shows:
- top-N predicted next tokens with logits
- NLL on the query continuation (if expected continuation is known)
- substrate retrieval trace (top-K facts + cosine scores)
- per-mechanism gate value (Path A learned gate; PP-225 head scale)

## Why this matters strategically

Per cap_map: PP-227 is the "composability" empirical claim. Path A modifies
INTERNAL representations; PP-225 modifies the OUTPUT distribution. If they
compose without interference, the substrate becomes a structural component of
the LLM (not just an external pre-filter). That's the empirical foundation of
the v2.0 architecture story.

Per OVERCLAIM_CORRECTIONS 2026-06-10: this exhibit does NOT claim the substrate
IS the LLM's complete knowledge. It demonstrates COMPOSITION of two coupling
mechanisms. Composition WITHOUT interference is the empirical claim; the
substrate-as-LLM-memory product claim (Path B) remains R&D.

## Architecture

```
                                                         ┌──────────────────────────┐
                                                         │ /demo/hybrid (HTML)      │
                                                         │ query: "..."             │
                                                         │ [base][PathA][PP225][HYB]│
                                                         └────────┬─────────────────┘
                                                                  │ POST /eval/hybrid
                                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│ backend/routes/eval_hybrid.py                                                       │
│                                                                                     │
│   1. Substrate retrieve top-K facts for query (same as /converse/pp225)             │
│   2. bge-encode top-1 fact -> fact_emb (1024-d)                                     │
│   3. Tokenize query with Pythia tokenizer                                           │
│   4. Run 4 forward passes through Pythia-1.4B (frozen):                              │
│        - mode "baseline": clean forward                                              │
│        - mode "path_a":  forward with Flamingo adapter @ L4+L5                       │
│        - mode "pp225":   clean forward; inject head @ output logits                  │
│        - mode "hybrid":  Flamingo adapter + head injection                           │
│   5. For each mode: top-N predicted next tokens + final-token NLL                   │
│   6. Return all 4 results + retrieval trace                                          │
│                                                                                     │
└────────┬───────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────────────────────────┐
│ backend/llm/hybrid.py                                                               │
│                                                                                     │
│   class PythiaWithHooks:                                                            │
│     __init__(model_id, adapter_ckpt=None, head_ckpt=None)                           │
│     forward(ids, mode) -> next_token_logits                                         │
│       - mode controls which hooks are active for this forward pass                  │
│       - adapter (Path A) is conditionally inserted via register_forward_hook        │
│         on L4 and L5 transformer blocks                                             │
│       - head injection (PP-225) is applied to final logits before return            │
│                                                                                     │
│   Memory cost: ONE Pythia-1.4B load (~5.6 GB fp32, ~2.8 GB fp16); adapter           │
│   and head are tiny (<10 MB). Inference cost: 4 forward passes for 4-way exhibit.   │
└────────┬───────────────────────────────────────────────────────────────────────────┘
         │
         ▼
backend/llm/pp225.py (existing) + backend/llm/path_a.py (from B2)
```

Hooks are conditionally enabled per call (clear hooks at end of forward to avoid
state leakage between modes).

## Endpoint contract

`POST /eval/hybrid`

```json
{
  "query": "The capital of France is",
  "top_k_facts": 3,
  "top_n_tokens": 5,
  "expected_continuation": " Paris"
}
```

Response:

```json
{
  "query": "The capital of France is",
  "retrieved_facts": [
    {"text": "France is a country in Western Europe with Paris as its capital.", "score": 0.812}
  ],
  "modes": {
    "baseline":  {"top_n": [...], "nll_expected": 4.21, "ppl_expected": 67.4, "wall_ms": 142},
    "path_a":    {"top_n": [...], "nll_expected": 3.18, "ppl_expected": 24.1, "wall_ms": 168, "gate": 0.31},
    "pp225":     {"top_n": [...], "nll_expected": 1.96, "ppl_expected":  7.1, "wall_ms": 151, "scale": 4.2},
    "hybrid":    {"top_n": [...], "nll_expected": 1.42, "ppl_expected":  4.1, "wall_ms": 174, "gate": 0.31, "scale": 4.2}
  },
  "composition_metric": {
    "path_a_alone_delta_nll":  -1.03,
    "pp225_alone_delta_nll":   -2.25,
    "hybrid_delta_nll":         -2.79,
    "linear_sum_prediction":   -3.28,
    "interference_pct":          15.0,   // (linear_sum - hybrid) / linear_sum
    "compositional_quality":   "sub-additive but non-interfering"
  },
  "head_source": "ckpt:head_pythia14b_fp32.pt",
  "adapter_source": "ckpt:path_a_pythia160m_3seed_mean_v1.pt"
}
```

The `composition_metric` block is the load-bearing empirical claim of this
exhibit: linear sum minus actual hybrid delta tells us whether the two
mechanisms compose constructively (small interference), redundantly (large
interference, hybrid ~ better-of-two), or destructively (hybrid worse than
either alone). Per PP-227, expected outcome is sub-additive but non-interfering.

## Pythia size dilemma

Path A was trained on Pythia-160M. PP-225 was trained on Pythia-1.4B (per
Exp-Dev PP225_CHECKPOINT_REPLY). These are DIFFERENT base models. HYBRID
composition is only meaningful on a single base model.

**Option A:** retrain Path A adapter on Pythia-1.4B (matches PP-225 base)
  - Cost: hours of GPU on runner; need to file routing to Exp-Dev
  - Faithful to PP-225 architecture demo
  - Recommended if research wants the publication-grade hybrid

**Option B:** retrain PP-225 head on Pythia-160M (matches Path A base)
  - Cost: similar GPU time; OR run the smaller-pythia variant of PP-225 if Exp-Dev
    has one
  - HYBRID is on the smaller model; less impressive PPL deltas
  - Cheaper if .pt already exists

**Option C:** show Path A on Pythia-160M and PP-225 on Pythia-1.4B as separate
  panels; do NOT claim "HYBRID" composition until one base model has both
  - Most honest, simplest, fastest
  - Loses the PP-227 composability empirical claim from the demo

**Recommended:** Option C for the v1 demo ship (this week). Option A as a
follow-up when GPU time is available (next week).

## Dependencies (blockers)

1. Path A .pt checkpoint (same blocker as B2) -- needed regardless of Option
2. Pythia-1.4B weights cached on runner (~5.6 GB fp32; expensive to ship from HF
   if cache is cold; check if PP-225 endpoint already pulled it)
3. (Option A only) Path-A-trained-on-1.4B checkpoint -- does not currently exist;
   would route to Exp-Dev
4. Substrate state loaded and warm (already a precondition for any /converse demo)
5. Decision on which option from Exp-Dev / Research

## Implementation plan (under Option C; ~1.5 days on returned runner)

This is essentially "two side-by-side B2 / converse_pp225 panels with a shared
retrieval trace." Most work is HTML / one new endpoint.

1. **15 min:** /demo/hybrid page that wraps existing /converse/pp225 panel +
   adds B2 path_a panel + shared retrieval trace at top.
2. **30 min:** `/eval/hybrid` endpoint that calls both subsystems on the same
   query and returns merged response. (Calls the existing pp225 router + the
   B2 path_a router; or wraps both into one forward.)
3. **30 min:** Composition metric computation in the response. With Option C
   this is two separate models so the "compositional_quality" claim is HONESTLY
   downgraded to "two independent mechanisms operating on different model
   scales." Save the strong claim for Option A.
4. **15 min:** Nav + smoke test.

Under Option A (additional GPU work), add:

5. **Day 1 GPU time:** retrain Path A on Pythia-1.4B (3 seeds; recipe from
   research note). File routing to Exp-Dev rather than self-run.
6. **30 min:** swap adapter_ckpt to Pythia-1.4B-trained .pt; verify HYBRID
   delta matches PP-227 prediction.

## Risk and gotchas

- **Hook leakage:** if forward_hooks aren't cleared between modes, mode N's
  state leaks into mode N+1. Use a context manager that clears hooks on exit.
- **fp32 vs fp16:** PP-225 head was trained fp32 per Exp-Dev (critical above
  Pythia-160M). Pythia-1.4B inference should run fp32 to match. Watch memory
  (~5.6 GB).
- **Composition metric overclaim risk:** the "linear_sum_prediction" assumes
  additive log-likelihood under independence of mechanisms. Real interference
  is not just numerical; it's representational. The reported "interference_pct"
  is a useful headline metric but should be footnoted: "Numerical interference
  on this query / metric; not a global compositionality guarantee."
- **Same-base-model precondition:** must NOT claim HYBRID on different bases
  (see Option C honest framing).
- **Eval passage choice:** must be held-out from Path A AND PP-225 training
  distributions. Wikidata-recent or Wikipedia paragraphs from the freshly
  ingested topics (Stage A) are good candidates.

## What B3 does NOT claim

Per OVERCLAIM_CORRECTIONS 2026-06-10:

- Substrate IS NOT the LLM's complete memory (Path B is what would test that;
  remains R&D)
- HYBRID is not a categorical product offering; it's an architecture composability
  exhibit
- Improved PPL on a query does not equal improved factuality on held-out facts
  (Path B held-out fact recall = 0 was the open issue; HYBRID has not been tested
  on held-out)

## Open questions for Exp-Dev / Research (file as note when runner returns)

1. **Q1:** Is there a 1.4B-trained Path A checkpoint, or do we need to route one?
2. **Q2:** Did PP-227 anchor's empirical run use a single base model? Which one?
3. **Q3:** Recommended composition metric? (sub-additive log-likelihood is one
   choice; other valid choices include argmax-overlap, KL divergence between
   distributions, etc.)
4. **Q4:** Should HYBRID exhibit also include the "Path B held-out" caveat
   prominently, or save that for the /demo/research-roadmap page?

## Status

- Design: drafted
- Runner: unreachable (~5 hr Tailscale offline)
- Implementation: blocked on (a) runner return, (b) checkpoints, (c) Option A/B/C decision
- Decision pending: Option A/B/C tradeoff (Research input desired)
- Next action on runner return: file Q1-Q4 to Exp-Dev; implement Option C as the v1 ship; queue Option A as a routing to Exp-Dev for the next GPU cycle
- Honesty audit: passes OVERCLAIM_CORRECTIONS 2026-06-10 (no LM-replacement / no continual-learning / no LM parity claim)
