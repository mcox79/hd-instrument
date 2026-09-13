

## pasted by the owner 2026-09-12 23:05 (raw; strategy reads this)

SOLUTION SUBMISSION
Original problem: consolidate_the_graded_lexical_semantic_stores_into_one_learned_convergence_hub_with_task_readouts

Docs: notes/problems/consolidate_the_graded_lexical_semantic_stores_into_one_learned_convergence_hub_with_task_readouts/
  -> SOLVED.md, MATH_BF_AUDIT_semantic_hub.md, PROPOSAL_hdlab_semantic_hub.md, DESIGN_semantic_hub_2026-09-13.md
Reverify: .venv/Scripts/python.exe verification/test_semantic_hub_convergence.py   (all checks green)

RESULT (status PARTIAL -- a rigorous located negative, a full-pass outcome per the bar):
Built ONE learned convergence semantic hub (Rogers-McClelland/Jackson) over the graded spokes -- denoising
reconstruct-every-spoke + Ma-Pouget PRECISION-weighted representational-similarity to the gold-free cross-spoke
CONSENSUS (Cox 2024), online/plastic (CLS), mathematically BF end-to-end (glass-box lemmatizer upstream).
- WIN as a REPRESENTATION: the one hub ties/beats EACH of the 5 stores on that store's own best task (incl. the
  DINOv2 visual spoke on concrete nouns) and is the single best representation on MEN relatedness (0.628,
  CI[0.606,0.648]); precision-weighting beats equal-weighting; info-free twin dead everywhere.
- LOCATED NEGATIVE on the live grounding DECISION (coverage-quality MRR@0.5, n=247): hub ALONE trails the landed
  FUSED 0.230 vs 0.295 (CI-sep below); hub AS A 4th POOL ties it (0.301 vs 0.295, CI straddles 0). The hub is
  redundant on the read because it is built from the SAME spokes the fusion reads; the read-time separate-pool
  precision fusion (double dissociation) stays the decision mechanism.

DIRECTION FOR STRATEGY (Q111): land semantic_hub as the ONE consolidated graded-similarity REPRESENTATION and
repoint the relatedness/similarity reads (WSD, typing, bridging, prediction) to it; retire the two islands
(meaning_fusion, composed_hub_predictor); KEEP FusedSenseRanker as-is (measured tie, do not wire the hub in); a
real read-time LIFT needs a NEW modality, not a reorganization of existing spokes; land the glass-box lemmatizer
swap (removes the last WordNet-at-inference rung). Full proposed diff in PROPOSAL_hdlab_semantic_hub.md.

BF: every rung BF/BF_SPIRIT (MATH_BF_AUDIT); the one math infidelity (equal-weight consensus) fixed to Ma-Pouget
inverse-variance; plastic online update path (not a frozen model); no external LLM at inference. NO hdlab written.

ASK: review and set owner_verdict on this problem.
