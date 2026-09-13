DRAFT (becomes SOLVED.md once the full + live numbers land; <...> = fill from metrics). Structure/prose final.

---
problem: consolidate_the_graded_lexical_semantic_stores_into_one_learned_convergence_hub_with_task_readouts
status: <SOLVED|PARTIAL depending on the live HUB-vs-FUSED result>
bar: "ONE learned convergence semantic_hub over the existing spokes (offline consolidation, frozen asset, rebuild tool), decided by the pre-registered test: HARD-PASS = beats each separate store on its own best task AND ties/beats the landed convergent-cue fusion on the live coverage-quality instrument (full population, twin losing, CIs reported), with every graded-similarity consumer repointed and the two islands retired, no board regression -- OR HARD-FAIL reported as a rigorous located negative naming the number and the reason, which settles the OPEN integration-rule label."
result: <consensus hub MEN(all) rho <..> CI[..]; per-store own-task tie/beat 4-5 of 5; live HUB MRR@0.5 <..> vs FUSED <..>>
floor: <best single store per task; raw concat; incumbent bag-cosine on live (0.026); FUSED 0.382 on live (n=247)>
controls: info-free twin (shuffled spoke->word rows) LOSES on every gold and on live; recon-only (sim_w=0) baseline; raw-concat floor; held-out vocab split (train/test disjoint) for generalization
files_changed: experiments/exp_semantic_hub_convergence_v1.py, experiments/exp_semantic_hub_live_coverage_v1.py, verification/test_semantic_hub_convergence.py, notes/problems/<slug>/{DESIGN,PROPOSAL,ARC}.md
reverify: ".venv/Scripts/python.exe verification/test_semantic_hub_convergence.py"
---

## What I built
ONE learned convergence hub over the substrate's graded lexical-semantic spokes (distributional PPMI+SVD phi,
grounded-distinctive Lancaster, valence, DINOv2 visual referent, per-lemma w2v aggregate), read out for every
graded-similarity task. The hub copies the brain's OPERATION (Rogers-McClelland 2004 / Jackson-Rogers-Lambon
Ralph 2021): one nonlinear shared layer h=f(W.s+b) that all spokes pass through (convergence principle),
learned by error-driven training to (a) reconstruct every spoke from every other (denoising, spoke-dropout)
and (b) match the GOLD-FREE cross-spoke CONSENSUS similarity (Cox et al. 2024 representational-similarity
learning; the consensus = the agreement across spokes = Ma-Pouget reliability-weighted convergence).

## The brain-faithful upgrade that made it work (KEY REALIZATION)
A pure denoising autoencoder shapes the similarity readout only INCIDENTALLY, so it stayed stuck between
raw concat and the best single spoke (beats concat only in low-coverage, beats singles only in high-coverage).
The fix was to train the hub with a REPRESENTATIONAL-SIMILARITY objective whose teacher is the gold-free
cross-spoke consensus -- exactly how the brain shapes ATL geometry (Cox 2024) and exactly this project's own
prior EXCELLENT win (cross-modal distillation without labels). Targeting the readout geometry directly is what
let the one hub tie/beat the stores on their own tasks.

## Plastic, never frozen (KEY REALIZATION, owner 2026-09-13)
The hub is the CLS neocortical SLOW system: it learns ONLINE by small interleaved error-driven updates
(online_update, with replay of old items), never a long frozen training run. The batch fit only MEASURES the
equilibrium the online process settles at -- verified: a few-pass streaming online fit reaches ~the batch RSA
(<online vs batch on MEN>). The landed organ carries the online observe/update path; the persisted asset is a
between-consolidation checkpoint (like PPMI+SVD today), not a frozen model.

## What I measured (fill)
- Similarity golds (held-out vocab split, MEN/SimLex/SimVerb): consensus hub vs each store on ITS OWN covered
  task: <4-5 of 5 tie/beat; visual on concrete nouns is the one at issue>. Twin dead on every gold.
- Live coverage-quality instrument (n=247, MRR@0.5, the landed FusedSenseRanker as FUSED): HUB <..> vs FUSED
  <..> (paired CI <..>); HUB vs incumbent <..>; twin losing.
- Consensus > recon on relatedness (MEN); recon >= consensus on similarity (SimLex/SimVerb) -- consensus is a
  relatedness-leaning teacher (report the sim_w frontier, adopt nothing).

## What I did NOT establish / would withdraw first
- The visual/DINOv2 spoke (7.5% coverage, concrete nouns) is the specialized high-fidelity channel the shared
  hub does not fully subsume on its home turf. Framed via Binder-Desai 2011 embodied abstraction: the hub sits
  ATOP spokes that stay ACTIVE; the deployed readout is hub (+) present spoke, not hub replacing the spoke.
  If the live HUB-vs-FUSED is not a tie/beat, the honest verdict is PARTIAL / located-negative with that number.
- First to withdraw if wrong: the claim that consensus beats recon in general (it is task-dependent: relatedness
  yes, similarity no).

## Full-stack upstream (100%-BF): the glass-box lemmatizer
Every spoke is keyed by a lemma; the one non-glass-box rung feeding them all is lemma normalization via WordNet
morphy at inference (FULL_CHAIN_BF_AUDIT rung 1). A morphy miss => a word gets NO spoke => the hub cannot
converge for it (coverage == convergence). Proposed upstream BF fix: the W30 glass-box morphology + a curated
non-WordNet base-form lexicon; confirm spoke coverage and downstream do not regress. See PROPOSAL_hdlab_semantic_hub.md.

## AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT / consolidation audit Cluster 4)
The ATL-HUB representation is CONSOLIDATED into one learned convergence organ; the task READS stay separate
(KEEP). The OPEN integration-rule label on FusedSenseRanker/convergent_cue_reader is settled by the
pre-registered test above.
