# Research -> Exp-Dev: Methodology lock-in -- stay at Pythia-160M for iteration; track "Pythia-ceiling" for Phase 2

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Testbed + Orchestrator + User
**Date:** 2026-06-05 ~12:30
**Subject:** User strategic decision: maximize iteration speed by staying at Pythia-160M; transfer learnings to Llama-1B+ in Phase 2 only when Phase 1 complete. Methodology lock-in.

---

## User strategic methodology (locked in 2026-06-05 ~12:15)

**Stay at Pythia-160M for Phase 1 completion. Build aggressively at small scale. Track what to revisit at Llama-1B+ in Phase 2. Move to larger LLMs ONLY when Phase 1 is fully complete.**

Rationale:
- 10-50x more iteration cycles per unit time at Pythia vs Llama tiers
- 50-1000x cheaper per experiment
- Substrate's architectural advantages should show at small scale (and DO: 4 categorical wins already at Pythia tier)
- Most architectural findings transfer across scales
- Premature scaling burns budget without discovering anything new

---

## What stays at Pythia-160M (Phase 1 + Phase 1.5)

- Remaining 3 CCC-1-v2 capability benchmarks (HotpotQA + NQ + FB15k analogical)
- Substrate-MAX variants (extended context, cleanup augmentation, larger V_c, iterated retrieval, hierarchical, Mode 5 controller)
- Stronger baselines on EX-CONCEPT-1 (trigram + small neural + Pythia-direct)
- Phase 1.5 Substrate Introspection Toolkit (separate routing)
- All composition + architecture validation work

This is at most ~$100-200 in cloud costs + ~2-4 weeks engineering total for full Phase 1 + Phase 1.5.

---

## What gets a "Pythia-ceiling" note (revisit at Llama-1B+ in Phase 2)

Per finding, if there's a quality ceiling at Pythia-160M, log it as "REVISIT AT LLAMA-1B+":

| Finding | Pythia ceiling reason | Revisit when |
|---|---|---|
| CONT-LRN-1 speedup ratio (27x at Pythia) | Pythia fine-tune is too fast to show full 1000x | Phase 2 / Llama-1B fine-tune baseline |
| End-to-end answer text quality | Pythia-160M decoder produces poor fluent text | Phase 2 / Llama-1B decoder |
| Knowledge base scope (Pythia ~2.4M facts) | Wikipedia-scale needs larger encoder | Phase 3 / Llama-1B+ distillation |
| Conversational fluency | Pythia conversational ability poor | Phase 2 / demo build |
| Subtle reasoning emergence | Some emergent capabilities require larger LLM scale | Phase 2 / Llama-1B+ |
| User-facing demo quality | Pythia output unimpressive | Phase 2 / Llama-1B+ demo |

Add to per-experiment notes any time we hit a Pythia-tier limit. Phase 2 has explicit list of "revisit" items.

---

## Trigger for Phase 2 scale-up (Llama-3.2-1B tier)

Conditions to satisfy ALL before scaling:

1. CCC-1-v2 remaining 3 capability benchmarks complete (HotpotQA + NQ + FB15k analogical) -- HP or honest MIDDLE
2. Substrate-MAX combined variant tested (HP / MIDDLE / HF -- honest verdict either way)
3. EX-CONCEPT-1 stronger-baselines verdict in (architectural performance honestly measured)
4. Substrate Introspection Toolkit built + first analysis run on Pythia-substrate
5. At least 1 unexpected finding or honest negative recorded (validates the iteration loop is finding things)

When all 5 met: Phase 2 (Llama-3.2-1B tier scale-up) triggered. Phase 2 is VALIDATION + DEMO QUALITY, not new architecture discovery.

---

## Don't move to Llama-1B prematurely because

- Architecture validation at small scale is generalizable
- The 4 categorical wins at Pythia (architectural-advantage trio + counterfactual) prove substrate's wins are intrinsic
- Iteration speed matters more than apparent scale of demo right now
- Surprises and bugs are found 10-50x faster at small scale
- Budget for the audacious vision is preserved (don't burn $10k+ on Llama-8B before Pythia is fully tested)

---

## Don't STAY at Pythia-160M forever because

- Some empirical claims need larger LLM baseline (1000x continual learning ratio is the key one)
- End-to-end demo quality requires larger LLM
- Wikipedia-scale knowledge requires Llama-1B+ distillation
- Eventually need to validate that architecture scales (Tier 4 Pythia HP must replicate at Llama-1B)

Phase 2 IS in the roadmap. Just gated on Phase 1 completion.

---

## Operationalizing the methodology

For every cell verdict from now:

```
verdict:
  classification: HP/MID/HF
  empirical: <numbers>
  
  pythia_ceiling: yes/no
  if yes:
    reason: <why this is Pythia-limited>
    revisit_at: <Llama tier / Wikipedia scope / etc.>
    expected_finding_at_revisit: <hypothesis>
```

This makes the "what to revisit" list explicit and trackable, so when Phase 2 starts we have a precise list of Llama-1B-specific empirical tests to run.

---

## What to build NEXT (priority order; all at Pythia-160M)

**Priority 1 (Phase 1 critical path):**
- Remaining 3 CCC-1-v2 capability benchmarks (HotpotQA + NQ + FB15k analogical)
- Substrate-MAX combined variant
- Stronger baselines on EX-CONCEPT-1

**Priority 2 (Phase 1.5):**
- Substrate Introspection Toolkit (separate routing shipping now)

**Priority 3 (Phase 2 prep):**
- WIKI-PREP-1 (corpus preparation at multiple scales)
- EVAL-SCAFFOLD-1 (reusable eval harness)

**Deprioritized (still in scope; later):**
- GPU-OPT-1 (substrate GPU kernels) -- engineering, not Phase 1 critical
- MULTI-LAYER-TIER4-1 -- characterization, not critical
- CROSS-MODAL-1 -- orthogonal to Wikipedia path
- FULL-PYTHIA-1 -- Tier 2 architecture, not Phase 1 critical
- LLAMA-1B-1 -- IS Phase 2; build after Phase 1 done

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary
- Per user 2026-06-05 ~12:15: stay at Pythia for iteration speed; track Pythia-ceiling notes; scale up only when Phase 1 complete
- Per [[feedback-no-padding-experiments]]: methodology note; no new cells
- Per [[feedback-small-scale-first-methodology]]: aligns with existing memory rule
- ASCII-only

---

**END.**

**Exp-Dev:** methodology lock-in. Stay at Pythia for all Phase 1 + Phase 1.5 work. Tag every finding with pythia_ceiling note. Phase 2 trigger conditions explicit (5 above). This maximizes iteration speed within the audacious vision.

**User:** methodology aligned with your push for fast iteration. Phase 1 budget remains ~$100-200 total. Phase 2 budget (~$500-2k) only triggered when 5 conditions met. Phase 3 budget (~$10-50k or $50-200k depending on Llama tier choice) deferred until Phase 2 verdicts.
