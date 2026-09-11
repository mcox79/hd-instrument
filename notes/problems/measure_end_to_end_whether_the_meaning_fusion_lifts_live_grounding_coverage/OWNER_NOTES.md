---
owner_verdict: DONE
---

SOLUTION SUBMISSION
Original problem name: measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage

Docs: notes/problems/measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage/
  → SOLVED.md (W37–W40), ARC_SUMMARY_referent_grounding_2026-09-11.md, DESIGN_visual_referent_hub_2026-09-10.md
Reverify: .venv/Scripts/python.exe verification/test_meaning_fusion_live_coverage.py   (37/37)

RESULT: A real, NON-text visual referent modality (DINOv2 over THINGS photos, frozen at ingest) adds
meaning-similarity signal that text+sensorimotor miss — perceptual (THINGS-behavior +0.027 R²) and,
once denoised by ~14-exemplar volume, SEMANTIC (MEN, 391 pairs, +0.086 R² unique, CI-separated,
shuffled-visual twin losing, seed-stable). The recovery-gated per-concept precision (convergent-cue)
fusion makes the FUSED hub beat its best single channel (0.72 vs 0.64, CI-sep) and cannot dilute by
construction. All three optional extensions exhausted with MEASURED reasons: hub shared-latent =
fuse-one-pool anti-pattern (loses 0.715 vs 0.723); coverage-fill = uncovered words are non-objects;
sound spoke = data-blocked (ESC-50 grounds ~25 concepts / 1 MEN pair, no instruments).

BF: every rung BF/BF_SPIRIT; NO NOT_BF atom added. Fusion = the brain's convergent-cue (separate
pools, precision-weighted; Ma-Pouget/Ernst-Banks; semantic-dementia×amnesia double dissociation).
Frozen transducers at ingest only, no runtime model; golds non-circular. Deepest residual is
pre-existing: WordNet-morphy lemmatizer needs a glass-box replacement (W30). NO hdlab written (Q111).

ASK: review and set owner_verdict on problem
"measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage". On DONE, apply the
SUBSTRATE INCORPORATION MANIFEST (SOLVED W37–W40): incorporate the multi-exemplar denoised centroid +
convergent-cue precision fusion; bank the three durable-negatives (fuse-one-pool hub, object
coverage-fill, ESC-50 sound spoke). Deprioritize those; a broad-AudioSet sound spoke is the only
unbuilt path (niche modality).
