---
owner_verdict: DONE
---

SOLVED (pending your verdict) -- predictive_inference_forward_project_the_next_event_and_state_from_the_situation_model (opus 4.8 solver)

Write-up: notes/problems/predictive_inference_forward_project_the_next_event_and_state_from_the_situation_model/SOLVED.md
Reverify (scaffold-free witness; recomputes headline+floors+twins+selective from source; touches NO landed cell):
  .venv/Scripts/python.exe verification/test_forward_event_projection.py     # 8/8

STATUS: PARTIAL (a rigorous, exhaustively-researched located negative + a real calibrated capability; the bar's
located-negative clause makes SOLVED defensible -- one labelling call is yours, in QUESTIONS).

1. THE CAPABILITY (the brief). Built the forward event/state projector the reader never had -- a glass-box
   generalized-event-knowledge readout over the LIVE situation model. On Story Cloze (MODERN, right-vs-wrong 5th
   sentence; val 1871 + test 1871) it discriminates the coherent continuation 0.592/0.582, CI-SEPARATED over the
   majority/base-rate floor (+0.078/+0.068); the cross-context twin COLLAPSES to chance (0.49) so it truly uses
   the story (not the Story Cloze style artifact); and a calibrated precision (1 - graded_competition entropy)
   earns MONOTONICALLY RISING selective accuracy (0.59->0.65), random-confidence twin flat. Brain-faithful
   (Elman GEK + graded_competition + inverse-entropy precision), NO LLM.

2. CLOSED THE PREDICTIVE-CODING LOOP (highest systemic upgrade). The forward prediction ERROR beats the reader's
   BACKWARD gist for coherence (0.592 vs 0.538) AND is a ~3x better event-BOUNDARY detector (segmentation F1
   0.766-0.806 vs 0.272 matched) -- the error should be taken against the FORWARD prediction (Rao-Ballard/Friston;
   Zacks EST). Reset-vs-reinstate settled empirically: mild reinstatement (lambda~0.3) beats hard reset (Pu 2022).
   Precision-weighting (Friston) tips the artifact-free mechanism to CI-sep over the strongest floor on both splits.

3. THE WALL, RESEARCHED TO THE BOTTOM AND UNDERSTOOD. It does NOT robustly beat a co-occurrence counter. I did not
   accept that as a ceiling: 2 research drills (8 sub-scans) + ~14 built glass-box mechanisms (association, affect,
   contradiction, causal-type, ConceptNet world-knowledge, meaning_foundation, precision-weighting, Kintsch
   CI-settling, a scenario event-SCHEMA foundation slice). ALL plateau. The understood reason: the inference
   ENGINES are built and correct, but they are GATED by the KIND of knowledge net -- ours are associative/
   typicality (wrong kind); the discriminator must be STORY-STATE-SPECIFIC. Proven: schema-typicality alone is
   ANTI-predictive (0.28), and denser extraction (dense-regime test, causal fires 0.74) does NOT help -- so it is
   neither a sparsity nor a mechanism gap. And human-level is reachable WITHOUT a forbidden LLM (SEM decomposition:
   its learned dynamics has no ablation justifying it; Kumar 2023: a glass-box surprise over a FROZEN foundation
   predicts human event boundaries, online-fittable).

4. CAVEAT I CAUGHT ON MYSELF: both benchmarks carry artifacts that reward shallow signals -- Story Cloze's
   ending-style artifact (my negation cue rode it until I ablated it) and MCScript2's typicality artifact (the
   same-scenario distractor is typicality-matched). The real next test needs an artifact-controlled gold.

13 experiment cells + a pinned reproducible gold fetch + an 8/8 scaffold-free witness; controls/twins throughout;
NO hdlab written (Q111); owner_verdict: (blank).

ONE LABELLING CALL FOR YOU (QUESTIONS): I set PARTIAL. SOLVED is defensible (rigorous located negative + the
capability/precision/twin halves pass); PARTIAL is the deflated call (the win is over the frequency floor, not the
strongest associative counter). Content identical either way.

>>> NEXT PROBLEM (the brain-foundational path across the wall; foundation-scale, file as its own north-star):
    build_the_story_state_specific_generative_event_model_over_a_rich_event_schema_knowledge_foundation
    (1) event-schema FOUNDATION: canonical causal/goal-typed script structures per situation (Schank scripts +
    Trabasso causal criteria + Rashkin naive-psychology) -- the clean/typed knowledge north-star, specialized to
    event-schemas, offline static asset. (2) a STORY-STATE-SPECIFIC generative model that instantiates the schema
    with THIS story's entities/state and generates the next event (SEM-style; dynamics ONLINE-fittable per schema,
    NOT a batch-trained/inference-LLM). (3) run the ALREADY-BUILT glass-box engines (CI-settling + causal-necessity
    + inverse-planning, recruited on-demand at the choice per Graesser) over it. Evaluate on an ARTIFACT-CONTROLLED
    forward-continuation gold (a content-blind/typicality baseline must NOT beat it). Do NOT re-file denser
    extraction, ConceptNet world-knowledge, or meaning_foundation-as-coherence-cue (all tested, none is the lever).

    ALSO READY TO LAND NOW (Q111, strategy, verdict-independent-ish): the additive default-off predict_next_event
    readout (lean extraction; 3 live cues: GEK + affect-direction + protagonist-contradiction; precision-weighted;
    1-step directed) + the loop wire redirecting n400_coherence_monitor's error to the forward prediction with
    lambda~0.3 reinstatement. AUDIT UPDATEs for BRAIN_FOUNDATIONAL_AUDIT.md: forward event-level prediction now
    demonstrated; SR-over-events is OUR-INVENTION (a counter); n400 monitor should reinstate (not hard-reset).
