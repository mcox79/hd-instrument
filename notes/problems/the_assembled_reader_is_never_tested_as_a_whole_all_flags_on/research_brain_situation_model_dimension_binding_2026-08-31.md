# Research drill: does the brain build ONE bound situation model indexed on all dimensions, or N independent trackers?

Date: 2026-08-31. Drill for problem `the_assembled_reader_is_never_tested_as_a_whole_all_flags_on`.
Question: our reader re-extracts events separately per dimension (time module re-parses, causation module re-parses...) and combines only at readout. Is a SHARED event/entity representation that every dimension reads+updates the brain's mechanism (PINNED) or OUR-INVENTION?

## VERDICT: SHARED-EVENT-INDEX is PINNED-BY-EVIDENCE. N independent re-extraction pipelines is a KNOWN fidelity gap.

The consensus across psycholinguistics AND systems neuroscience is that comprehension builds ONE integrated, relationally-bound event representation and INDEXES that single event token on all situational dimensions (who/what, when, where, why, intentionality). The dimensions are properties/pointers OF a shared event node, not separate representations that each independently re-derive the events. Re-extracting events per dimension is not even the weakest brain-consistent architecture (parallel monitoring), because in the brain the parallel monitors all point at ONE shared event token, compared against ONE shared prior event.

## The mechanism, layer by layer

1. **Event-indexing model (Zwaan, Langston & Graesser 1995; Zwaan & Radvansky 1998).** THE core claim: events are the focal nodes of the situation model, and a single event node is INDEXED simultaneously on five dimensions (time, space, protagonist, causation, intentionality). Dimensions are indices on a common event representation, not separate models. Empirically: reading time rises monotonically with the NUMBER of dimensions showing a discontinuity — you cannot get a "number-of-dimensions-changed" effect unless all dimensions are attached to the SAME event and compared against the SAME prior event. This is the load-bearing evidence FOR a shared index.

2. **Continuity / "here-and-now" default.** When a dimension is not mentioned, its prior value is CARRIED FORWARD — the situation model PERSISTS across sentences rather than being re-derived from scratch each sentence. This directly contradicts a per-dimension re-extraction architecture: the shared representation is the thing that persists.

3. **Event Segmentation Theory (Zacks, Speer, Swallow, Reynolds 2007).** Boundaries are inferred when prediction breaks down; changes on MULTIPLE dimensions (cause, character, goal, time, object, space) CONVERGE on a single segmentation decision and jointly gate one update. Convergent, cross-dimensional boundary detection = one shared event structure being updated, not N private ones.

4. **Binding substrate = hippocampal/entorhinal relational binding.** The hippocampus binds what-where-when into a single episodic index (index theory; recent sparse "barcode" index models, biorxiv 2024). Relational (vs item) encoding selectively recruits hippocampus. This is the neural realization of "one event token that all dimensions attach to."

5. **SEM — Structured Event Memory (Franklin, Norman, Ranganath, Zacks & Gershman 2020, Psych Review).** Formal generative model: a SINGLE latent event schema generates the structured (multi-role, multi-dimension) scene; a boundary is inferred when a new latent event better explains the input; hippocampus stores the structured event. Dimensions are roles within ONE latent event, inferred jointly — the strongest computational statement that the integration IS the computation.

6. **DMN as the situation-model substrate (Ranganath & Ritchey 2012 PMAT; Yeshurun, Nguyen & Hasson 2021, Nat Rev Neurosci).** The DMN is an active sense-making network that INTEGRATES extrinsic input with intrinsic prior knowledge into ONE context-dependent, evolving situation model over long timescales. Meaning construction = integration, not late fusion of independent streams.

## Honest calibration of the nuance

- SHARED EVENT REPRESENTATION indexed on all dimensions = **PINNED** (central, cross-literature consensus; not novel synthesis).
- FULL online mutual constraint (updating dimension A directly rewrites dimension B mid-sentence) = **PARTIALLY PINNED**. Convergent-boundary + joint-update evidence is strong; some early evidence reads dimension monitoring as roughly ADDITIVE/independent (Zwaan et al. 1995 number-of-dimensions effect). BUT additivity is about UPDATE COST, not about separate representations — even the additive reading requires all dimensions to index the same event token against the same prior. So our silo architecture fails even the MINIMAL pinned version.

## The gap in our reader

Our architecture re-EXTRACTS the event set independently inside each dimension module. The brain extracts ONE event structure (hippocampal relational bind / SEM latent event) and every dimension reads+writes THAT. So the fidelity gap is not merely "we combine late" — it is "we never build the shared event token at all." This is a genuine brain-fidelity DEFECT to build across, not an optimization choice.

## Quotable for SOLVED.md

> The integrated-vs-siloed distinction is brain-foundational, not cosmetic. Across the event-indexing model (Zwaan & Radvansky 1998), Event Segmentation Theory (Zacks et al. 2007), the Structured Event Memory model (Franklin, Norman, Ranganath, Zacks & Gershman 2020), hippocampal-entorhinal relational binding, and the default-mode situation-model literature (Yeshurun, Nguyen & Hasson 2021), the brain builds ONE relationally-bound event representation and indexes that single event token on all situational dimensions (who/what, when, where, why, belief), carrying unmentioned dimensions forward as a persisting shared state. It does not run N pipelines that each re-extract the events from raw text and fuse only at readout. Our current parallel-silo reader — where each dimension re-parses the text and never consults a common event/entity set — is therefore a PINNED brain-fidelity gap: the shared event index is the mechanism, and the integration is the computation, not an efficiency. Testing the assembled reader "all flags on" against a shared event backbone is the brain-faithful configuration; the independent-pass configuration is the ablation.

## Sources
- Zwaan, Langston & Graesser (1995) The Construction of Situation Models in Narrative Comprehension: An Event-Indexing Model — https://journals.sagepub.com/doi/10.1111/j.1467-9280.1995.tb00513.x
- Zwaan & Radvansky (1998) Situation Models in Language Comprehension and Memory — https://sites.ualberta.ca/~dmiall/Cognitive/Readings/Zwaan_Radvansky_1998.pdf
- "Who when where: an experimental test of the event-indexing model" — https://pubmed.ncbi.nlm.nih.gov/15058689/
- Franklin, Norman, Ranganath, Zacks & Gershman (2020) Structured Event Memory (SEM) — https://gershmanlab.com/pubs/Franklin20.pdf ; https://pubmed.ncbi.nlm.nih.gov/32223284/
- Yeshurun, Nguyen & Hasson (2021) The default mode network... construction of meaning — https://pmc.ncbi.nlm.nih.gov/articles/PMC7959111/
- Event Segmentation Theory review / EST (Zacks et al. 2007) — https://pubmed.ncbi.nlm.nih.gov/22468032/
- A Review of Mechanistic Models of Event Comprehension (2024) — https://arxiv.org/pdf/2409.18992
- Hippocampal index / relational binding ("barcodes") — https://www.biorxiv.org/content/10.1101/2024.09.09.612073.full.pdf
