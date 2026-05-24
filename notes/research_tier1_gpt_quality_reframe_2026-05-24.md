# Tier-1 reframe — GPT-quality generation with auditable memory

**Filed:** 2026-05-24 by orchestrator (verbatim user delivery; main-thread file action per [[feedback-no-experiment-design-in-prompts]])

**Purpose:** capture the user's substantive analysis of the GPT-quality-generation
KILLER Tier 1 row, which has been carried as "❌ CANNOT" since v1 and as 🟢 PARTIAL
since v3 grounded — the v1 framing was strategy posture wearing capability-claim
clothes, not a substrate-physics ceiling. This file is the canonical reference for
the cap_map row reclassification and the four implementable paths plus one
Research drill.

---

## Key claims

1. **v1 ❌ CANNOT was strategy posture, not capability claim.** The v1 cap_map
   row reads "GPT-quality generation with auditable memory | CANNOT (we're byte
   K-gram, not transformer-quality)" — that is a positioning statement about the
   product framing at the time, not a substrate-physics ceiling test. Nothing in
   the substrate-physics framework (R16 superposition capacity / R23 coding-rate
   bounds / R26 free-probability composition / R29 noise-tolerant readout)
   predicts a hard quality ceiling that GPT-quality generation cannot reach.

2. **v3 grounded shows row at 🟢 PARTIAL not ❌.** The v3 update (2026-05-20)
   already reclassified the row to "🟢 Partial — generation ✅ at byte-K=16;
   quality vs GPT untested." The v1 ❌ entry survives in the cap_map's KILLER
   Tier 1 table by drift / non-update, not by evidence.

3. **Substrate-physics framework does NOT predict a hard quality ceiling.** The
   four load-bearing frameworks (R16/R23/R26/R29) bound capacity, coding rate,
   composition, and readout fidelity — none of them assert a quality ceiling
   below GPT-2-small for an appropriately-scaled substrate generator. The
   question is whether substrate-native generation at scale matches LLM quality
   at matched compute, NOT whether substrate generation is forbidden.

---

## Five paths to resolve the GPT-quality question

### Path 3 — AGS scaling-law extrapolation (HIGHEST per user; CHEAPEST)

**Bet:** L territory (substrate-physics extrapolation).

**What:** measure substrate perplexity at 2-3 (N, K, M) points spanning at
least 1 decade in each axis. Fit AGS-style scaling curve. Extrapolate to
compute-matched GPT-2-small.

**Cost:** cheapest answer in the set. Cycle of CPU runs at multiple (N, K, M)
points, regression fit, extrapolation. No new training infrastructure needed.

**Decision rule (delegated to exp_dev):** exp_dev picks the (N, K, M) grid and
the fit form per [[feedback-no-experiment-design-in-prompts]]. Suggested
discipline: at least 3 points per axis, multi-seed at each, R^2 + extrapolation
CI reported.

**Verdict gates:** exp_dev sets HARD-PASS / HARD-FAIL gates against
compute-matched GPT-2-small extrapolated perplexity.

### Path 1 — Token-level substrate at K=128+ head-to-head vs GPT-2-small

**What:** build substrate generator at K=128 or higher (token-level, not byte
K-gram). Run head-to-head against GPT-2-small on standard eval set.

**Cost:** 2-3 day build + GPU day for the comparison run.

**Status:** substantial build; may need to file as multi-cycle hand-off (user
flagged this in the brief).

**Decision rule:** exp_dev picks the build sequence; suggested discipline:
multi-seed, paired-evaluation (substrate vs GPT-2-small same prompts), perplexity
+ qualitative samples.

### Path 2 — Hybrid substrate + small attention reweighter (kNN-LM-like)

**What:** kNN-LM pattern adapted to substrate — substrate provides the
retrieval-augmented prior, small attention reweighter handles fine-grained
distribution. Substrate-side is the auditable component.

**Cost:** ~week build.

**Status:** not in the current dispatch set; reserved for follow-up.

### Path 4 — Per-document substrate (strategic reframe)

**What:** substrate as document-grounded generator with audit/edit, NOT a
general-purpose generator competing with GPT-quality.

**Cost:** strategic positioning, not experimental — frames substrate's
auditable-memory advantage as the product wedge, sidestepping the "match
GPT-quality" question.

**Status:** strategic hedge if Paths 1/3 fail to deliver clear PASS.

### Path 5 — Bayes-optimal lower bound via R16 + R23 + R26 frameworks

**What:** derive Bayes-optimal lower bound on substrate-native generation
perplexity from R16 superposition capacity + R23 coding-rate bounds + R26
free-probability composition. If the Bayes-optimal bound is at or below
GPT-quality perplexity at matched compute, the capability question reduces to
engineering not physics.

**Cost:** ~week Research drill.

---

## User recommendation (sequencing)

1. **Path 3 FIRST** — cheapest answer; AGS scaling-law extrapolation tells us
   whether we are even in the right scaling envelope before paying for a
   token-level build.
2. **Path 1 in parallel** — substantial build, may stretch across cycles, but
   the head-to-head is the load-bearing test for the capability claim.
3. **Path 4 as strategic hedge** — if Paths 1/3 don't clear the bar, substrate
   pivots to per-document generation positioning.
4. **Path 5 as Research drill** — runs alongside Paths 1/3 to bound the
   theoretical ceiling and identify which framework (capacity / rate /
   composition) binds first.

---

## Cap_map row reclassification

The cap_map KILLER Tier 1 row at line 122 of `notes/substrate_capability_map.md`:

```
| **GPT-quality generation with auditable memory** | CANNOT (we're byte K-gram, not transformer-quality) | ...
```

should move to:

```
| **GPT-quality generation with auditable memory** | 🟢 PARTIAL — substrate-physics framework (R16/R23/R26/R29) does NOT predict hard quality ceiling; v3 grounded reading already at 🟢 Partial; v1 CANNOT was strategy posture not capability claim; 5 paths filed (Paths 1/3/5 dispatched 2026-05-24) | ...
```

Reclassification rationale: v1 ❌ CANNOT was filed as positioning, not as a
falsified-capability closure. The honest read of the substrate-physics
framework is 🟢 PARTIAL — generation primitive confirmed at byte-K=16; quality
bar untested; substrate-physics frameworks do not forbid GPT-quality;
extrapolation + head-to-head are the load-bearing tests filed under Paths 3 + 1
respectively.

This is a row reclassification NOT a portfolio promotion. It does NOT add a
demonstrated capability to the 12-row demonstrated portfolio; it removes a
spurious ❌ CANNOT closure that was never evidence-grounded.

---

## Dispatch routing (filed 2026-05-24)

| Path | Routing | Hand-off file |
|---|---|---|
| Path 3 (AGS scaling-law extrapolation) | exp_dev inline | `notes/exp_dev_handoff_path3_ags_scaling_2026-05-24.md` |
| Path 1 (token-level substrate K=128+ vs GPT-2-small) | exp_dev inline (multi-cycle) | `notes/exp_dev_handoff_path1_token_substrate_2026-05-24.md` |
| Path 5 (Bayes-optimal lower bound) | Research inline | `notes/research_request_path5_bayes_lower_bound_2026-05-24.md` |
| Path 4 (per-document substrate) | strategic hedge — no dispatch this cycle | (deferred; Strategy considers after Paths 1/3 land) |
| Path 2 (hybrid kNN-LM-like) | reserved for follow-up | (no dispatch this cycle) |

Per [[feedback-no-experiment-design-in-prompts]]: each hand-off contains task
statement + pointers to context + deliverable shape + autonomy declaration. No
sweep grids, no thresholds, no numerical bounds in the prompts. exp_dev / Research
pick parameters.
