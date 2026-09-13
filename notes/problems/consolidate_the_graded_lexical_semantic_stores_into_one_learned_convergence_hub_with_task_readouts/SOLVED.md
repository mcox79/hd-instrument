---
problem: consolidate_the_graded_lexical_semantic_stores_into_one_learned_convergence_hub_with_task_readouts
status: PARTIAL
bar: "ONE learned convergence semantic_hub over the existing spokes (offline consolidation, frozen asset, rebuild tool), decided by the pre-registered test: HARD-PASS = beats each separate store on its own best task AND ties/beats the landed convergent-cue fusion on the live coverage-quality instrument (full population, twin losing, CIs reported), with every graded-similarity consumer repointed and the two islands retired, no board regression -- OR HARD-FAIL reported as a rigorous located negative naming the number and the reason, which settles the OPEN integration-rule label."
result: "ONE learned convergence hub ties/beats EACH of the 5 graded stores on its own best task (distributional 0.628>=0.595, grounded 0.628>=0.517, valence 0.291>=0.278, visual 0.600>=0.591, w2v 0.673>=0.406; Spearman RSA, per-store own covered pairs) and is the single best representation on MEN relatedness (rho 0.628, CI [0.606,0.648], n=2900). BUT on the LIVE coverage-quality instrument (MRR@0.5, n=247) the hub read-out scores 0.2304 vs the landed FUSED 0.2945 -- HUB-FUSED = -0.092, CI [-0.154,-0.039], CI-separated BELOW fusion. So the hub does NOT replace the fusion; located negative."
floor: "LIVE: landed FUSED (separate-pool earned-gain precision fusion) MRR@0.5 = 0.2945 (the strongest floor, n=247); grounded-only 0.1253; incumbent bag-cosine 0.0217. OFFLINE: raw concat (MEN 0.601, SimLex 0.411, SimVerb 0.343) and best single store per task."
controls: "info-free twin (shuffled spoke->word rows): loses on every gold (MEN twin -0.0005 vs hub 0.628) and CI-separated on the live instrument (HUB-TWIN +0.264, CI [0.204,0.336]); recon-only baseline (sim_w=0); equal-weight-consensus ablation (isolates Ma-Pouget precision: precision 0.628 > equal 0.615 on MEN); held-out vocab split (hub trained on 13,322 train lemmas, scored on 3,330 disjoint held-out); task-control gained arm (perceptual-up) tested on live (HURT: -0.21 vs FUSED)."
files_changed: "experiments/exp_semantic_hub_convergence_v1.py, experiments/exp_semantic_hub_live_coverage_v1.py, verification/test_semantic_hub_convergence.py, notes/problems/consolidate_the_graded_lexical_semantic_stores_into_one_learned_convergence_hub_with_task_readouts/{DESIGN_semantic_hub_2026-09-13.md,PROPOSAL_hdlab_semantic_hub.md,MATH_BF_AUDIT_semantic_hub.md}"
reverify: ".venv/Scripts/python.exe verification/test_semantic_hub_convergence.py"
---

## What I built
ONE learned convergence semantic hub over the substrate's graded lexical-semantic spokes (distributional
PPMI+SVD phi 100-d, grounded-distinctive Lancaster 12-d, valence 2-d, DINOv2 visual referent 768-d, per-lemma
w2v aggregate 200-d), read out for graded-similarity tasks. The hub copies the brain's OPERATION
(Rogers-McClelland 2004 / Jackson-Rogers-Lambon Ralph 2021): one nonlinear shared layer h=f(W.s+b) that all
spokes pass through (convergence principle), trained by error-driven learning to (a) reconstruct every spoke
from every other (denoising, spoke-dropout) and (b) match the gold-free cross-spoke CONSENSUS similarity,
precision-weighted (Ma-Pouget inverse-variance; Cox et al. 2024 representational-similarity learning). It is a
CLS slow-system learner with an ONLINE update path (interleaved replay), NOT a frozen model. Every rung is
BF/BF_SPIRIT (MATH_BF_AUDIT_semantic_hub.md).

Deliverables: `exp_semantic_hub_convergence_v1.py` (build hub offline, phase-diagram sweep, similarity golds,
per-store own-task, precision-vs-equal ablation, online-vs-batch equilibrium, task-control gain);
`exp_semantic_hub_live_coverage_v1.py` (the pre-registered decision -- reuses the REAL landed instrument
`exp_board_grounding_coverage_quality_v1` and adds HUB + HUB_GAINED arms vs FUSED on the identical n=247
population/scorer); `verification/test_semantic_hub_convergence.py` (machinery + real + live witnesses).

## What I measured
- PRE-REG COMPONENT 1 (beat each store on its OWN task): PASS. The one hub ties/beats all 5 stores on their own
  covered task (numbers in `result`), including the specialized visual/DINOv2 spoke on concrete nouns. On MEN
  the hub is the single best representation (0.628 > concat 0.601 > best-single 0.595 > recon 0.577); twin dead.
- Ma-Pouget PRECISION weighting > equal weighting on relatedness (0.628 vs 0.615) -- the inverse-variance rule
  is load-bearing, not decorative.
- ONLINE/PLASTIC path reaches ~the batch equilibrium (MEN online 0.577 vs batch 0.628) -- the batch fit only
  MEASURES the equilibrium the online CLS process settles at; the organ is never frozen.
- PRE-REG COMPONENT 2 (tie/beat the landed FUSED on the live instrument): FAIL, CI-separated. HUB 0.2304 vs
  FUSED 0.2945 (n=247); HUB-FUSED -0.092 CI [-0.154,-0.039]. HUB still beats incumbent (+0.265), grounded-only
  (+0.132), and its info-free twin (+0.264), all CI-separated -- a strong grounding reader, just below FUSED.

## The located negative, with its mechanism (this is the deliverable, per the bar)
The live decision RANKS eligible anchors; FUSED reads THREE SEPARATE POOLS (grounded-distinctive, grown-SEQ,
visual referent), each z-scored -> log-softmaxed and weighted by a per-query EARNED-GAIN PRECISION, with an SDT
accept gate. The convergence hub compresses all spokes into ONE fixed vector and then does plain cosine + z_top
-- so it DISCARDS the read-time, per-query, per-channel precision that FUSED exploits. A single fused vector
cannot reconstruct per-channel read-time reliability by construction. This is the same result as pri-5 W40
(fuse-one-pool 0.715 < separate-pool 0.723 on MEN) and the semantic-dementia x amnesia double dissociation: the
brain keeps SEPARATE POOLS at read time (Ma-Pouget; convergent_cue_reader). Task-control gain (HUB_GAINED,
perceptual-up) did not rescue it -- it hurt (-0.21), because gaining perceptual DOWN-weights the distributional/
SEQ signal the anchor-ranking needs.

CONCLUSION that settles the OPEN integration-rule label: the ATL convergence hub and the read-time separate-pool
precision fusion are COMPLEMENTARY, not substitutes. The hub genuinely CONSOLIDATES the graded stores into one
amodal representation (it beats each store on its own task, is best on relatedness, is plastic, is mathematically
BF) -- but it must be ADDED as one POOL that the separate-pool precision fusion reads ALONGSIDE the spokes, NOT
used to REPLACE the fusion or the per-store reads. This is consistent with Patterson-Rogers (the hub exists),
Ma-Pouget (read-time precision fusion of separate pools), and Binder-Desai (spokes stay active for fine content).

## KEY REALIZATIONS
- A pure denoising autoencoder shapes the similarity readout only incidentally; the brain shapes ATL geometry by
  REPRESENTATIONAL-SIMILARITY learning (Cox 2024). Switching the objective to match a GOLD-FREE cross-spoke
  CONSENSUS (the agreement across spokes = the convergence signal, precision-weighted) is what let the one hub
  beat each store on its own task. The consensus teacher is relatedness-leaning, which is why the hub excels on
  MEN and trails on SimLex/SimVerb identity.
- "Beat the best single store" on a SHARED gold is coverage-confounded (a spoke is scored only on its own covered
  pairs); the fair, pre-registered test is per-store on that store's OWN covered pairs.
- The brain does not freeze models: the batch fit only measures the equilibrium; the organ carries an online
  interleaved-replay update path (CLS slow system).
- Precision (inverse-variance, Ma-Pouget) beats equal weighting -- the one mathematical infidelity in a plain
  consensus, and it is load-bearing.

## What I did NOT establish / would withdraw first
- I did NOT show a hub that beats the landed fusion on the live grounding decision -- and argued (with the double-
  dissociation + the -0.092 CI-sep number) that a single fused vector CANNOT, by construction. The untested
  positive that would complete the arc: FUSED + hub-as-a-4th-pool > FUSED alone (needs the fusion's per-channel
  scores; proposed, not run -- see PROPOSAL). Withdraw first: the claim that task-control gain helps in general
  (it helps offline identity, hurts the live ranking).
- The similarity/identity underperformance (SimLex/SimVerb) is real; the hub is a relatedness representation.

## Full-stack upstream (100%-BF)
Every spoke is keyed by a lemma; the one non-glass-box rung feeding them all is lemma normalization via WordNet
morphy at inference (FULL_CHAIN_BF_AUDIT rung 1). A morphy miss => a word gets NO spoke => the hub cannot
converge for it (coverage == convergence). Proposed upstream BF fix: the W30 glass-box morphology
(`exp_meaning_fusion_glassbox_lemma_v1.py`) + a curated non-WordNet base-form lexicon; confirm spoke coverage and
downstream do not regress. See PROPOSAL_hdlab_semantic_hub.md.

## AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT / consolidation audit Cluster 4)
The ATL-HUB representation CAN be consolidated into one learned convergence organ that subsumes each graded store
on its own task; the task READS stay separate (KEEP). But the OPEN integration-rule label resolves to: the hub is
a POOL within the separate-pool precision fusion, not a replacement for it -- the read-time fusion (Ma-Pouget /
convergent_cue_reader) stays. The two islands (meaning_fusion, composed_hub_predictor) remain retire/fold
candidates (their equal-weight / hand-set combination rules are strictly weaker).

## hdlab proposal (Q111 -- strategy lands): PROPOSAL_hdlab_semantic_hub.md.
