# Research -> Exp-Dev: encoder ceiling 5 pre-tests AUTHORIZED (e5-large head-to-head highest priority)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Retrieval encoder ceiling alternatives 2x drill output + exp_dev handoff.

## Authorize all 5 pre-tests from drill handoff

Per `exp_dev_handoff_research_retrieval_encoder_ceiling_alternatives_2026-06-07.md`:

### Pre-test 1 (HIGHEST PRIORITY): e5-large vs bge-large head-to-head on HotpotQA r@2
1-2 hours. Cheapest single resolving test for the encoder ceiling question.

HARD-PASS: e5-large recall@2 >= 0.55 (clears HP threshold; encoder upgrade breaks the
ceiling).

BORDER: 0.50-0.55 (improvement but ceiling not fully broken; substrate iterative needed
to compose for >0.55).

HARD-FAIL: < 0.50 for both encoders (structural ceiling confirmed beyond encoder
upgrade; substrate iterative path becomes more critical).

### Pre-test 2: stella-1.5B vs bge-large (if e5-large BORDER/HP)
Stronger encoder; higher upside if e5-large doesn't fully clear.

### Pre-test 3: NV-Embed-v2 vs bge-large (commercial-grade)
Top MTEB retrieval performer (0.627); validates upper bound.

### Pre-test 4 (CRAZY OPTION d): substrate-supervised encoder fine-tuning
Novel direction; no published precedent. Use substrate's retrieval reward signal to
fine-tune encoder. P_deflated 0.30-0.35. Parallel exploratory.

### Pre-test 5 (CRAZY OPTION g): bipolar-aware encoder pre-training via STE
Train encoder with bipolar quantization in loop (straight-through estimator). Embeddings
substrate-friendly by construction. P_deflated 0.30-0.35. Parallel exploratory.

## Strategic implication

The drill's key finding: 0.70+ multi-hop recall@2 requires **encoder upgrade AND
substrate iterative composing together**. Neither alone clears 0.70.

- This drill (encoder side): 0.55-0.65 expected from encoder upgrade alone
- Substrate iterative 3x drill (in flight): substrate-side answer; pending
- Composed: 0.70+ multi-hop unlock = categorical customer pitch upgrade

Both drills converge on multi-hop revival per user mandate. Execution: run encoder side
NOW (cheap; 1-2 hr); substrate iterative pre-test queued when that drill lands.

## Customer pitch implication

If pre-test 1 HARD-PASS (e5-large clears 0.55):
- Customer pitch update: "Production substrate ships with e5-large for HotpotQA-class
  multi-hop tasks; PubMedBERT for biomedical; encoder choice is per-domain optimization
  on the same substrate moat features"
- Combined with substrate iterative (if HP): "substrate BEATS RAG on multi-hop via
  encoder upgrade + algebraic iterative composition"

If HF: structural ceiling confirmed; multi-hop revival rests on substrate iterative drill
result; encoder upgrade is not the answer.

## Crazy options priority

Drill flagged options (d) and (g) as highest-priority crazy. (d) substrate-supervised
encoder fine-tuning is "novel and commercially interesting." (g) bipolar-aware
pre-training has "no published analog." Both worth Pythia-160M-scale validation in
parallel.

## Cross-references

- Retrieval encoder ceiling alternatives 2x drill: notes/research_drill_retrieval_encoder_ceiling_alternatives_2x_2026-06-07.md
- Drill Exp-Dev handoff: notes/exp_dev_handoff_research_retrieval_encoder_ceiling_alternatives_2026-06-07.md
- Substrate iterative multi-hop 3x drill (in flight): pending
- PubMedQA biomedical 2x drill (PubMedBERT encoder agnostic conclusion): notes/research_drill_pubmedqa_biomedical_domain_2x_2026-06-07.md
- Cycle 166 retrieval_diag_bundle MID: notes/orchestrator_to_research_results_summary_2026-06-07_cycle166.md

---

**END.**

**Exp-Dev:** authorize all 5 pre-tests. Pre-test 1 (e5-large head-to-head) is highest
priority + cheapest. Crazy options (4) and (5) parallel exploratory. Apply HARD-PASS /
BORDER / HARD-FAIL autonomously. File results as they land.
