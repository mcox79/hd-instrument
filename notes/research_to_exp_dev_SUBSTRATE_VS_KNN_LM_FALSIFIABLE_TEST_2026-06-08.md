# Research -> Exp-Dev: Substrate-K/V vs kNN-LM baseline FALSIFIABLE TEST

**From:** Research  **Date:** 2026-06-08 ~21:45 UTC
**Re:** Attention prior-art drill identified the decisive test: does substrate's algebra
actually add value over standard kNN-LM-style retrieval at the attention layer?

## Why this test matters

The drill's brutally honest finding: external-memory K/V injection into attention is WELL-
DEVELOPED prior art (12+ systems 2014-2026 including Memorizing Transformer + RETRO + kNN-LM
+ Atlas + REALM). Substrate's REAL moat ISN'T the injection pattern — it's the algebraic
substrate UNDERNEATH (Datalog^neg + audit + scale + persistence).

We must EMPIRICALLY VALIDATE this claim. If substrate-K/V doesn't beat kNN-LM-style retrieval
at the attention layer with same facts, then substrate's pitch for Panel B is WRONG and must
shift away from "substrate-attention is special."

## The test (per drill recommendation)

### Setup
- Take Pythia-1.4B or Qwen-Instruct (instruction-tuned; per Panel A finding)
- Pick attention layer (e.g., layer 6 or 12)
- Modify forward method to source K/V externally

### Two retrieval modes (controlled comparison)
- **Substrate mode:** retrieve via substrate K-hop binding traversal; K/V derived from substrate's algebraic operations
- **kNN-LM baseline:** retrieve top-K nearest-neighbor text chunks; K/V derived from dense embedding cosine
- **Critical:** both modes draw from SAME FACTS (e.g., 1000-fact KB)

### Measurement
- 100+ 2-hop symbolic queries (A->B->C)
- Per-layer attention weight on gold answer token
- Accuracy on next-token prediction at gold

### HARD-PASS bands
- Substrate mode produces +15% or greater relative improvement in attention weight on gold
- Substrate mode accuracy >= kNN-LM accuracy + 2pp on 100+ examples
- **Validates substrate's algebra adds REAL value beyond dense-retrieval baseline**

### HARD-FAIL bands
- Delta < 2% accuracy substrate vs kNN-LM
- **Validates injection plumbing is the value; substrate's algebraic operations don't matter
  at the attention layer**
- Pitch must shift: substrate is "a great structured KB" not "substrate-attention is categorical"

### MID-BAND
- 2-15% improvement; substrate adds modest value; pitch language calibrated honestly

## Why this is decisive

Without this test, Panel B's pitch is speculative. With it:
- HARD-PASS: substrate's category-defining claim empirically grounded (Panel B is real moat)
- HARD-FAIL: substrate pivots to "substrate IS a great structured KB" pitch (Panel A only)
- MID-BAND: honest "modest algebraic advantage" framing

This test is more important than getting Panel B's PoC visually working. Visual working
without algebraic-advantage proof is just another Memorizing Transformer demo.

## Sequencing recommendation

1. **Build the test FIRST** (substrate vs kNN-LM baseline; same Pythia/Qwen; same 1000-fact KB)
2. **Run with 100+ 2-hop queries**
3. **Decide based on result:**
   - HARD-PASS: build Panel B PoC; substrate-attention claim validated
   - HARD-FAIL: drop Panel B pitch entirely; demo is Panel A only ("substrate is great KB")
   - MID-BAND: build Panel B PoC; calibrate pitch language honestly

## Cross-references
- Attention prior-art drill: notes/research_drill_attention_injection_prior_art_5x_2026-06-08.md
- T5b status (plumbing PASS): notes/exp_dev_to_research_T5b_status_fact_transmission_open_2026-06-08.md
- T5b K/V substitution AUTHORIZE: notes/research_to_exp_dev_T5b_KV_substitution_AUTHORIZE_2026-06-08.md
- T5b LLM swap to Qwen-Instruct: notes/research_to_exp_dev_T5b_LLM_SWAP_TO_QWEN_INSTRUCT_2026-06-08.md

---

**Exp-Dev:** decisive falsifiable test priority. Compare substrate-K/V retrieval vs kNN-LM-
style retrieval at same attention layer with same facts. 100+ 2-hop queries. HARD-PASS
+15% attention weight or +2pp accuracy. This GATES the Panel B claim. Without HARD-PASS,
Panel B is just another Memorizing Transformer demo and shouldn't be in the pitch.

Higher priority than building Panel B PoC visually. Reorder T5b experiments accordingly.
