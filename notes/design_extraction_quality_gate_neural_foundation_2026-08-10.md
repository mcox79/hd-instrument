# Design: EXTRACTION-QUALITY GATE -- does the neural extractor produce the RIGHT KIND of data?

Director design note (2026-08-10, USER-approved extraction-as-foundation per 07-14 pivot). GATE before building the full inference pipeline. SHAPE + pointers; exp_dev designs params + picks the runnable stack.

## Why (do it right -- prove the input before trusting the pipeline)
Wall = prose->structure extraction. Audit-confirmed KEY asset: organs hit ORACLE-ceiling (0.93-1.00) on gold structure, collapse ONLY at self-extraction. 07-14 pivot (USER-approved): external vetted extractor = FOUNDATION; glass-box organs+crutch = RUNTIME (no LLM at inference; the extractor produces STRUCTURE, not answers -- charter-clean, like the CSKG crutch + WordNet grounder). BEFORE wiring the pipeline we must PROVE the neural extractor emits the exact structure the organs consume, correctly, with coverage + grounding, and that it CLOSES the oracle->self-extract gap. Garbage structure in = an uninterpretable inference result (can't tell extractor-fault from thesis-fault). This gate de-risks that.

## Target schema = the EXACT organ input contract (read from code, do not improvise)
Per passage produce:
1. EVENTS -- sequence of {PRED (predicate lemma), AGENT (=PropBank ARG0), PATIENT (=ARG1), TENSE} -> hdlab/event_bundle.py EventBundleCodec.encode_event, DEFAULT_ROLES=(PRED,AGENT,PATIENT,TENSE). This IS Semantic Role Labeling output.
2. ENTITIES -- coreference clusters -> canonical entity IDs so AGENT/PATIENT link across events -> hdlab/situation_model_accumulate.py AccumulateRegister.add_event(entity, role, event_idx).
3. CAUSAL/TEMPORAL LINKS -- directed edges between event indices w/ polarity -> hdlab/situation_model_accumulate.py:161 CausalLinkRegister.add_causal_link(cause_idx, effect_idx, polarity). HARDEST; may be partial -- measure its marginal impact separately, do not let it block the SRL+coref core.
4. GROUNDED FILLERS -- fillers -> semantically grounded vectors (REUSE the existing WordNet-Tier2 open-vocab grounder, ~94% coverage). Ungrounded structure was proven WORSE than BoW (E3b) -- grounding is mandatory.

## Extractor stack -- MODERN sources only, INSTALLABILITY-FIRST
Evaluate what actually RUNS in this Windows env AND emits the target schema; verify install + smoke on 5 real sentences BEFORE committing. Candidates (pick best that installs+runs):
- SRL for {PRED,AGENT,PATIENT,TENSE}: a modern PropBank SRL (HF model) OR AMR (amrlib / SPRING / AMRBART) -- AMR IS predicate-argument-role structure + negation/modality in one graph, an attractive single source.
- Coref: fastcoref / spaCy-experimental-coref / Stanza coref.
- Causal/temporal edges: discourse-connective rules + relation classifier, or AMR/UD-derived. Partial OK.
- Grounding: the existing WordNet-Tier2 grounder.
If nothing heavy installs, FALL BACK to spaCy 3.x dependency-parse -> heuristic role mapping (nsubj->AGENT, dobj->PATIENT, root verb->PRED, morphology->TENSE) + REPORT that as the constraint. Report exactly what installed + ran.

## The 5 metrics (the "right kind of data" gate)
1. SHAPE CONFORMANCE -- % extracted events populating >=PRED+AGENT+PATIENT with a well-formed role mapping.
2. CONTENT F1 -- SRL-role F1 + coref F1 vs GOLD (a corpus with gold structure: OntoNotes / CoNLL-2012, or a cell already carrying gold). Are roles/entities actually correct?
3. COVERAGE -- % sentences yielding >=1 well-formed event. MUST beat the E3 failure (67% of PRESENT-tense sentences returned 0 events -- the old organ was LitBank-past-tense-only; a modern SRL must handle all tenses). Report coverage split by tense.
4. GROUNDING -- filler grounding coverage (~0.94 target).
5. DECISIVE -- ORACLE-PARITY. Reuse an existing organ cell that has BOTH an oracle-structure arm AND a self-extracted arm (candidate: exp_wire_coref_accumulate_situation_model, oracle 0.930 -> earned 0.684; or another islanded oracle-vs-earned cell -- pick one you can run). Swap its weak self-extraction for the MODERN external extractor. Measure organ-output-on-EXTRACTED vs organ-output-on-ORACLE. Does modern extraction CLOSE the gap (0.684 -> toward 0.930)? THIS is go/no-go.

## Gate verdict
GO (proceed to full inference test) if: shape-conformance high; content-F1 respectable (SRL >~0.80, coref >~0.70); coverage >~0.85 across ALL tenses; grounding ~0.94; AND oracle-parity gap closes materially (extracted organ-output reaches >~80% of the oracle arm's lift-over-baseline). ELSE: localize the single weakest component (SRL / coref / causal / grounding) + report it as the next target -- do not proceed to the full pipeline on bad structure.

## Guardrails
This is a GATE/MEASUREMENT, not the pipeline build. Modern sources only (USER standing). Branch dataprep/mcguffey-graded-corpus (NOT main/origin). self-test PASS -> installability smoke (5 sentences) -> the parity measurement. Resumable. Targeted commits (git SLOW; never git add -A). VET on disk. Report the 5 metrics + the go/no-go + (if no-go) the weakest component.
