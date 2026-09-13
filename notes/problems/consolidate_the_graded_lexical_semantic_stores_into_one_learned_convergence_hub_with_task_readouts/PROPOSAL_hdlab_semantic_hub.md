# PROPOSED hdlab CHANGE (Q111 -- strategy lands; solver only proposes)

The mechanism is proven in `experiments/exp_semantic_hub_convergence_v1.py` +
`exp_semantic_hub_live_coverage_v1.py` + `verification/test_semantic_hub_convergence.py`. This is the
exact diff that would land it, and why. NOTHING here is written by the solver into hdlab/.

## New organ: `hdlab/semantic_hub.py` (structure = ATL amodal convergence hub; Cluster 4 representation)
- Holds ONE learned convergence representation over the graded spokes: `h = tanh(W . s + b)`, W learned
  by error-driven CONSOLIDATION (offline) to (a) reconstruct every spoke from every other (denoising, spoke
  dropout) AND (b) match the GOLD-FREE cross-spoke CONSENSUS similarity (Cox 2024 representational-similarity
  learning; convergence principle Rogers-McClelland 2004 / Jackson 2021; reliability Ma-Pouget).
- Frozen asset between consolidations (like PPMI+SVD today): `data/foundation/semantic_hub_v1/hub.pt`
  (encoder weights + spoke_dims + the ordered spoke list). NO gradient training at inference.
- API mirrors the other channels: `hub_vector(word) -> unit np.ndarray or None`; `similarity(a,b)`;
  `covers(word)`. Encoder consumes the SAME spokes the experiments assemble (distributional phi, grounded-
  distinctive, valence, DINOv2 referent, per-lemma w2v aggregate), keyed by lemma.
- Rebuild tool: `tools/build_semantic_hub.py` (== experiments/exp_semantic_hub_convergence_v1.py run_full,
  promoted) so the asset is re-buildable and re-consolidates as the SEQ store grows (CLS slow system).

## Spokes = arms (REUSE, no new stores): distributional_meaning_channel.ppmi_svd (phi), grounded_similarity
   (distinctive), sensorimotor_spoke.referent_vector (DINOv2), valence via affect_lexicon, meaning_foundation
   (per-lemma glass-box aggregate of the synset signatures). KEEP typed_spokes + WordNet definitional bag
   SEPARATE (typed/relational != graded; is-a lever REFUTED).

## Readouts repointed (KEEP the reads; unify only the representation) -- pre-registered, per outcome:
- `reading_grounding_loop.FusedSenseRanker`: ADD a hub channel as a separate pool in the SAME earned-gain
  precision fusion (NOT replace it) IF the live-instrument test shows HUB ties/beats FUSED; else leave FUSED
  and register the hub as an additional graded-similarity channel available to consumers.
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
