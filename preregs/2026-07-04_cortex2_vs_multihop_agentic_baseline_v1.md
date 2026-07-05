# Pre-reg: cortex2_vs_multihop_agentic_baseline_v1 (2026-07-04) -- GO/NO-GO

Skunkworks named the decisive weakness: the cortex's chain-completeness win (1.0 vs 0.51) was
"cannot-fake" ONLY vs a SINGLE-SHOT retrieve-then-read black-box. This cell runs the cortex head-to-head
vs a STRONGER MULTI-HOP / AGENTIC baseline that CAN retrieve-about-the-intermediate (cite fact2) and CAN
bolt on a verification retrieval. CPU-local, NO re-encode. Sharded FHRR KG over FB15k-237.

## Arms (same KG)
- CORTEX (glass-box, single-pass): per-hop unbind+cleanup; answer=path argmax; provenance=causal path;
  confidence=min hop cleanup-cosine -- ALL from ONE mechanism (2 cleanups).
- MHM (multi-hop agentic, STRONG): explores top-K intermediates, cites fact1+fact2, bolts on an extrinsic
  verification retrieval (+1 op). Uses the same sharded cleanup as confidence. Fair strong competitor.
- NAIVE_FLAT (multi-hop over MONOLITHIC index): the naive RAG WITHOUT the transparent sharded mechanism;
  present to test whether competent multi-hop REQUIRES the glass-box mechanism.

## Three go/no-go questions
1. Does the chain-completeness advantage SURVIVE vs multi-hop or collapse to parity?
2. Does per-hop confidence-refuse still beat the multi-hop baseline's refuse on near-miss?
3. Is there ANY axis where the glass-box (intrinsic, single-pass) beats a multi-hop agentic RAG that
   bolts on extrinsic verification?

## Pre-registered bands
- CONTINUE_STANDALONE_DIFFERENTIATOR: >=1 of {completeness, near-miss refuse, faithfulness} survives
  (cortex - mhm > 0.05 parity tolerance).
- PIVOT_INTERPRETABLE_MEMORY_INDEX: all three reach PARITY -> not a standalone reasoning moat; surviving
  cannot-fake value = interpretable-memory-index (competent multi-hop needs the transparent mechanism;
  faithfulness/auditability come free; single-pass efficiency).

## RESULT (FULL, 3 seeds, VE=6014; MEASURED@data/exp_cortex2_vs_multihop_agentic_baseline_v1/metrics.json)
- verdict: PIVOT_INTERPRETABLE_MEMORY_INDEX.
- Q1 completeness: cortex 1.000 vs mhm 0.958 -> PARITY (survives=False). Multi-hop names fact2 too.
- Q2 near-miss refuse: cortex 1.000 vs mhm 1.000 -> PARITY. Multi-hop detects the missing final edge
  via its 2nd retrieval.
- Faithfulness: cortex 0.850 vs mhm 0.866 -> PARITY (mhm marginally higher). Competent multi-hop
  mechanical retrieval is EQUALLY ablation-faithful.
- Recall: cortex 0.958, mhm 1.000 (agentic top-K exploration is genuinely competitive/stronger),
  naive_flat 0.014 -> naive monolithic COLLAPSES: competent multi-hop REQUIRES the transparent sharded
  mechanism.
- Q3 efficiency: cortex 2.0 ops vs mhm 4.4 ops -> single-pass edge (answer+provenance+confidence from
  ONE mechanism; the agentic baseline pays extra retrieval + a bolt-on verification pass).

## Honest interpretation (CONTINUE vs PIVOT)
The standalone-reasoning-differentiator thesis FAILS: a competent multi-hop agentic baseline reaches
parity on completeness + near-miss refuse + faithfulness (and beats cortex on recall via exploration).
The v1 "cannot-fake completeness" edge was an artifact of the single-shot straw-baseline. The cannot-fake
value that SURVIVES is the INTERPRETABLE-MEMORY-INDEX: (a) in this substrate a competent multi-hop
retriever MUST use the transparent sharded per-hop mechanism (naive monolithic collapses to 0.014), so
mechanical faithfulness + auditability come FOR FREE with competent KG-multi-hop -- they are a property
of the substrate, not a reasoning moat; (b) the glass-box is single-pass (2 ops vs 4.4) -- it does not
bolt on an extrinsic verifier. Net: PIVOT the thesis from "standalone reasoning differentiator" to
"interpretable / auditable memory index with a structural faithfulness guarantee + single-pass audit."
NOTE (scope): the faithfulness-GUARANTEE vs an actual LLM reader (whose answer is not mechanically bound
to retrieved chunks) is asserted, not measured here -- it requires a real LLM reader arm. That is the
crisp remaining CONTINUE thread if the memory-index framing needs a differentiator vs LLM-RAG.

## Discipline
cardinality_ok true (3 seeds); arms_differ_verified true; tmp_replace atomic; except SystemExit: raise
before except Exception; start_marker + crash-diag; line_buffered_stdout. CPU-local foreground (189s).
