# DESIGN: one learned convergence semantic hub (vATL hub-and-spoke) + task readouts

**Solver:** opus 4.8 · **opened this session:** 2026-09-13 · scope: experiments/, verification/, this folder. NO hdlab writes (Q111).

## The brain operation we copy (from RESEARCH_one_semantic_hub_many_readouts_2026-09-11.md)
- **Hub (Rogers-McClelland 2004; Jackson-Rogers-Lambon Ralph 2021, Nat Hum Behav 5:847-860):**
  `h = f(Σ_i W_i·s_i + b)` -- ONE nonlinear (tanh/sigmoid) shared deep layer that ALL modality spokes pass
  through (convergence principle), trained by ERROR-DRIVEN learning to reconstruct EVERY spoke from EVERY other
  (autoencoder-like co-occurrence reconstruction loss). Plus SPARSE direct shortcut connections (~1-in-24 in the
  winning arch) that bypass the hub for fast shallow associations. Reliability weighting EMERGES (concrete words
  lean on perceptual spokes, abstract on distributional) -- it is NEVER hand-coded (Binder-Desai 2011).
  Result = a graded multidimensional similarity geometry (Cox et al. 2024).
- **Task control (Hoffman-McClelland-Lambon Ralph 2018; Jackson 2021):** `h' = f(W·s + U·c + b)` -- control is an
  additive/amplifying top-down input at the SPOKE/shallow layer (which features reach the hub), NOT a rewrite of the
  deep hub code. => task readouts, not per-task copies of the representation.
- **Consolidation (CLS; McClelland 1995; Kumaran 2016):** slow, interleaved, schema-gated offline folding of
  reading-grown knowledge into the same hub. `dW = eta_slow·Σ_replayed (target_i − f(W·x_i))·x_i^T`, eta_slow<<eta_fast,
  replay mixes new+old. => the hub is a FROZEN asset between consolidations (like PPMI+SVD today); NO training at inference.

## Architecture verdict (BRAIN_STRUCTURE_CONSOLIDATION_AUDIT Cluster 4/12/16)
- CONSOLIDATE the REPRESENTATION into ONE `semantic_hub` organ (the spokes are arms). KEEP the task READS as
  consumers (WSD `underspecified_sense_reader`, predication `copular_binding`, bridging `bridging_inference`,
  entity typing `entity_resolver`->`conceptual_meaning`, prediction `predictive_reader`/`composed_hub_predictor`).
- Fold the two ISLANDS (`meaning_fusion`, `composed_hub_predictor`, 0 importers) into hub readouts or retire.
- Keep TYPED/relational stores SEPARATE (WordNet definitional bag, `typed_spokes`) -- graded ≠ typed; is-a lever REFUTED.

## Spokes to converge (graded-similarity only)
1. `meaning_foundation` -- curated w2v sense signatures (distributional relatedness).
2. `lexical_similarity` -- McRae feature bundles (the GRADED features only, not the WordNet-def cosine).
3. `grounded_similarity`/`sensorimotor_spoke` -- Lancaster 11-d sensorimotor + Brysbaert concreteness.
4. visual referent arm -- DINOv2 multi-exemplar centroid (referent_vectors_multi.npz) from pri-5.
5. grown SEQ store `data/foundation/seq_store_v1` -- directional co-occurrence -> PPMI+SVD (`distributional_meaning_channel.ppmi_svd`).
6. `valence_polarity_channel` -- Warriner valence (Osgood axis).
[APIs to fill from spoke-digest agent.]

## The pre-registered decision (from the brief §6, quoted verbatim into SOLVED.md)
HARD-PASS = the single learned hub beats EACH separate store on that store's OWN best task AND ties-or-beats the
landed convergent-cue fusion (`FusedSenseRanker`, the earned-gain-ratio precision fusion; incumbent 0.382 vs
grounded 0.159 vs incumbent-D 0.027, n=247) on the live coverage-quality instrument (full population), info-free
twin LOSING, CIs reported, no board per-dimension regression (AGG 0.6313 standing; substrate_health gate).
HARD-FAIL = hub underperforms the best single store on its own best task (premature forced convergence).
Prior: a LINEAR one-pool SVD latent (r=64) scored 0.715 vs separate-pool fusion 0.723 on MEN (pri-5 W40) -- a
linear hub does NOT beat precision fusion. The open question is whether the NONLINEAR error-driven convergence hub does.

## Golds / tasks (all MODERN; 19c banned)
- similarity judgement: SimLex-999, SimVerb, MEN (concrete-noun relatedness).
- sense selection: WiC / SCWS (context-modulated).
- grounding: the live coverage-quality instrument (`exp_board_grounding_coverage_quality_v1.py`).
- each spoke's "own best task" = the task where it is the incumbent strongest single channel.

## Phase diagram (owner reminder 2026-09-13 "remember the phase diagram") -- FREE TO SWEEP, a wall at one config = MOVE the point:
hub width (8..256), shortcut sparsity (~1/24 .. dense), spoke dropout rate (= partial-input training = brain's missing-modality
robustness), learning schedule/epochs, nonlinearity (tanh/relu), reconstruction-vs-similarity objective weighting.

## FULL-STACK UPSTREAM (owner instruction this session + brief FULL-STACK-UPSTREAM directive)
End component = the hub (100% BF: Rogers-McClelland convergence operation). Trace the inputs' signal up the chain:
- Every spoke is keyed by a LEMMA. Rung 1 of the live chain (FULL_CHAIN_BF_AUDIT) normalizes lemmas with **WordNet
  morphy at runtime** -- BF in computation (morphological decomposition, Rastle-Davis) but an EXTERNAL TOOL AT
  INFERENCE, NOT glass-box. This is the deepest residual, pipeline-wide, and it is the ONE non-BF-in-implementation
  rung feeding ALL spokes: a morphy miss => a word gets NO spoke => the hub cannot converge for it (signal lost on
  the inputs, exactly where the owner says to look). W30 glass-box-morphology prototype exists (pri-5 ARC_SUMMARY #2).
- PLAN: prototype a glass-box morphology (irregular table + productive suffix rules + a curated non-WordNet base-form
  lexicon) as the upstream BF replacement; measure that it recovers >= morphy's lemma coverage on the spoke vocab
  (so hub coverage does not regress) and that NO downstream consumer regresses. This makes the whole chain glass-box.

## GENERALIZATION (owner question 2026-09-13 "does this generalize?") -- tested 3 ways, not single-task
The point of one hub is that it generalizes; a hub that wins one task is not the brain's hub. Tests:
1. ACROSS TASKS: the SAME frozen hub, read by task-specific readouts, must serve similarity (MEN/SimLex/SimVerb),
   sense selection (WiC), AND the live coverage-quality MRR -- never retuned per task. (== the pre-registered bar.)
2. ACROSS WORDS/COVERAGE: spoke-dropout = train to impute a missing spoke from the others => generalizes to
   partial-coverage words (most words = distributional only); CLS consolidation folds reading-grown words in.
3. HELD-OUT (not memorizing): train the hub on a TRAIN vocab split, score similarity on HELD-OUT word pairs
   (words unseen in training); info-free twin LOSING + bootstrap CIs throughout. Golds are never in training
   (unsupervised reconstruction), so there is no gold leakage by construction.

## FINDINGS LOG (running; numbers are quick 40-epoch passes unless marked FULL)
- MACHINERY (synthetic, 3 regimes): convergence hub recovers shared latent (RSA CI>0), info-free twin
  COLLAPSES (rho ~0), phase-diagram sensible (tight bottleneck wins; shortcuts bypass hub -> hurt readout).
  Recon hub beats singles in symmetric regime, beats CONCAT in the sparse/low-coverage regime (imputation
  niche == the real-data regime). Consensus hub (recon + sim-to-consensus) > recon hub.
- BRAIN-FAITHFUL UPGRADE (owner "how does the brain do this?"): pure reconstruction shapes the similarity
  geometry only incidentally -> hub stuck between concat and singles. FIX = representational-similarity
  learning (Cox et al. 2024) with a GOLD-FREE cross-spoke-CONSENSUS teacher (two concepts are similar to the
  degree many spokes agree = the convergence principle + Ma-Pouget reliability). ConsensusHub implements this.
- REAL DATA (quick 40-epoch, hub_width 48): per-store OWN-TASK (fair, same covered pairs):
  distributional hub 0.608>=0.595 TIE/BEAT; grounded 0.608>=0.517; valence 0.399>=0.278; w2v 0.632>=0.406;
  VISUAL 0.566 < spoke 0.591 (n=384) -- the ONE store the hub-alone does not subsume, on concrete nouns.
  Consensus HELPS relatedness (MEN all 0.608 vs recon 0.593) but HURTS similarity (SimLex/SimVerb) vs recon
  (consensus is a relatedness-leaning teacher). Twin dead on every gold.
- INTERPRETATION (pending FULL-trained confirmation): the visual/DINOv2 spoke is a specialized high-fidelity
  perceptual channel at 7.5% coverage; the shared hub rarely sees it in training and slightly dilutes it on
  its home turf. BRAIN-FAITHFUL reading (Binder-Desai 2011 "embodied abstraction"): the ATL hub sits ATOP
  modality spokes that STAY ACTIVE for fine-grained concrete content -- the full concept = hub + currently-
  active spokes, NOT hub replacing the spoke. So the faithful deployed readout is hub (+) present-spoke
  (exactly what FusedSenseRanker does with its referent channel), and the hub need not beat the visual spoke
  on concrete nouns to be the right consolidation of the BROAD graded stores.
- LEVERS if visual gap is robust after FULL training: (a) precision-weight the consensus (visual reliability
  = exemplar count / inverse dispersion; Ma-Pouget); (b) lower spoke-dropout for rare high-reliability spokes
  or oversample words carrying them; (c) sweep sim_w (recon<->consensus tradeoff: consensus favors MEN, recon
  favors SimLex) -- report the frontier, do not adopt a single number.

## Deliverables
1. `experiments/exp_semantic_hub_convergence_v1.py` -- build the nonlinear convergence hub offline over the spokes
   (numpy/glass-box; NO pretrained embedding as the hub; NO torch unless justified/GPU-queued), sweep the phase-diagram
   knobs, run the pre-registered test with info-free twin + bootstrap CIs. Own data dir only.
2. `experiments/exp_glassbox_morphology_v1.py` -- the upstream BF lemmatizer prototype + coverage/no-regress check.
3. `verification/test_semantic_hub_convergence.py` -- scaffold-free witnesses (assert each load-bearing claim).
4. `SOLVED.md` -- the pre-registered block + prose + KEY REALIZATIONS + the proposed hdlab diff (Q111) + AUDIT UPDATE.
