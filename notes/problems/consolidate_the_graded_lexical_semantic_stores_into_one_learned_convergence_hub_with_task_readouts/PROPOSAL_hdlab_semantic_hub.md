# PROPOSED hdlab CHANGE (Q111 -- strategy lands; solver only proposes)

The mechanism is proven in `experiments/exp_semantic_hub_convergence_v1.py` +
`exp_semantic_hub_live_coverage_v1.py` + `verification/test_semantic_hub_convergence.py`. This is the
exact diff that would land it, and why. NOTHING here is written by the solver into hdlab/.

## New organ: `hdlab/semantic_hub.py` (structure = ATL amodal convergence hub; Cluster 4 representation)
- Holds ONE learned convergence representation over the graded spokes: `h = tanh(W . s + b)`, W learned
  by error-driven CONSOLIDATION (offline) to (a) reconstruct every spoke from every other (denoising, spoke
  dropout) AND (b) match the GOLD-FREE cross-spoke CONSENSUS similarity (Cox 2024 representational-similarity
  learning; convergence principle Rogers-McClelland 2004 / Jackson 2021; reliability Ma-Pouget).
- PLASTIC, NEVER FROZEN (owner 2026-09-13 "the brain doesn't do frozen models"): the organ carries an
  ONLINE observe/update path -- `semantic_hub.online_update(new_obs, replay)` takes SMALL slow-rate
  error-driven steps as the reading loop grows the stores, INTERLEAVING replay of old items (McClelland
  1995 CLS slow system; no catastrophic interference). It is the neocortical slow learner, updated
  continuously, not a one-shot dump. NO gradient training at INFERENCE (updates are the slow/consolidation
  path, not the read path) -- but the weights are never permanently frozen; they keep moving with experience.
- The persisted snapshot `data/foundation/semantic_hub_v1/hub.pt` is a BETWEEN-CONSOLIDATION checkpoint
  (like the current PPMI+SVD asset), NOT a frozen model: it is re-consolidated online as data arrives. The
  120-epoch BATCH fit only MEASURES the equilibrium the online process settles at (verified: a few-pass
  streaming online fit reaches ~the same RSA -- see metrics_full.json online_hub vs consensus_hub).
- API mirrors the other channels: `hub_vector(word) -> unit np.ndarray or None`; `similarity(a,b)`;
  `covers(word)`; `online_update(...)`. Encoder consumes the SAME spokes the experiments assemble
  (distributional phi, grounded-distinctive, valence, DINOv2 referent, per-lemma w2v aggregate), keyed by lemma.
- Rebuild/equilibrium tool: `tools/build_semantic_hub.py` (== exp_semantic_hub_convergence_v1.py run_full,
  promoted) MEASURES the equilibrium; the live organ REACHES it by online_update as the SEQ store grows.

## Spokes = arms (REUSE, no new stores): distributional_meaning_channel.ppmi_svd (phi), grounded_similarity
   (distinctive), sensorimotor_spoke.referent_vector (DINOv2), valence via affect_lexicon, meaning_foundation
   (per-lemma glass-box aggregate of the synset signatures). KEEP typed_spokes + WordNet definitional bag
   SEPARATE (typed/relational != graded; is-a lever REFUTED).

## Readouts repointed (KEEP the reads; unify only the representation) -- pre-registered, per outcome:
- `reading_grounding_loop.FusedSenseRanker`: LEAVE AS-IS. MEASURED: adding the hub as a 4th pool TIES FUSED on
  the live instrument (HUB_PLUS_FUSED 0.3006 vs 0.2945, CI straddles 0) -- the hub is redundant with the fusion's
  pools (same spokes), so it neither helps nor hurts the read-time decision. Do NOT wire it into the ranker; the
  grounding decision stays with the separate-pool precision fusion.
- `underspecified_sense_reader` (WSD), `conceptual_meaning`/`entity_resolver` (typing), `bridging_inference`,
  `copular_binding`: expose `semantic_hub.similarity` as the graded-similarity backend they read (byte-identical
  witness where the read is unchanged; measured where it changes).
- EMBODIED ABSTRACTION (Binder-Desai 2011): the hub sits ATOP the spokes, which STAY ACTIVE for fine-grained
  concrete content -> the deployed readout is hub (+) present high-fidelity spoke (esp. the visual referent on
  concrete nouns, where the specialized spoke is not subsumed by the shared hub). Do NOT drop the referent
  channel from FusedSenseRanker.

## Islands retired/folded: `meaning_fusion.py` (0 importers; equal-weight z-fusion -- strictly weaker than the
   hub + FusedSenseRanker) and `composed_hub_predictor.py`'s hub copy (hand-set lam gate) -> fold their
   PPMI+SVD reading-spoke build into the hub's spoke assembly; retire their combination rules.

## Registry / audit: tag `semantic_hub` BF_SPIRIT (convergence op PINNED Rogers-McClelland; numpy/torch
   denoising-AE + RSL realization is a defensible computational-level model; width/dropout/sim_w SWEPT).
   §2b AUDIT UPDATE: Cluster 4 representation CONSOLIDATED into one organ; reads kept; the OPEN
   integration-rule label on FusedSenseRanker/convergent_cue_reader settled by the pre-registered test.

## UPSTREAM (full-stack, 100%-BF): the one non-glass-box rung feeding ALL spokes is lemma normalization via
   WordNet morphy at inference (`lexical_utils`/`normalize_lemma`; FULL_CHAIN_BF_AUDIT rung 1). A morphy miss
   => a word gets NO spoke => the hub cannot converge for it. Replace with the glass-box morphology
   (W30 prototype `experiments/exp_meaning_fusion_glassbox_lemma_v1.py` + a curated non-WordNet base-form
   lexicon) so the whole chain is glass-box; confirm spoke coverage does not regress and no downstream consumer
   regresses. (Predates this arc; the hub makes it load-bearing because coverage == convergence.)
