---
owner_verdict: DONE
---

SOLVED (pending your verdict) -- bridging_inference_infer_the_unstated_link_between_adjacent_sentences (opus 4.8 solver)

Write-up: notes/problems/bridging_inference_infer_the_unstated_link_between_adjacent_sentences/SOLVED.md
Reverify (recomputes every headline from source; runs NO landed cell): .venv/Scripts/python.exe verification/test_bridging_inference.py   # 33/33

STATUS: SOLVED. Build a glass-box construction-integration bridge that infers the UNSTATED coherence link
between adjacent sentences (instrument / causal / referential-part) by semantic relatedness -- the meaning
channel's first live read()-time consumer.

CORE RESULT (the brief's "infer the correct bridge"): meaning-store associative relatedness SELECTS the correct
bridge ANTECEDENT -- which whole a part belongs to, which event an instrument serves -- CI-separated over BOTH a
no-inference floor AND a most-salient-entity floor, with the meaning-SHUFFLED twin collapsing to chance, on the
TWO unclaimed types across TWO independent gold sources (WordNet meronymy + ConceptNet). PART 0.472 / 0.609 vs
floor 0.200 (+0.27 / +0.41); INSTRUMENT (UsedFor) 0.452 vs 0.200 (+0.25); every twin at chance. CAUSAL is REUSED,
not redone -- the force+mental unstated-causal selector is already SOLVED on disk (exp_causal_unified_bridge_
event_type_v1). Located negatives (full controls): relation-TYPE selection is NOT distributional (+0.05 over a
shape twin); a linear relation-offset is a shape artifact.

DEPTH (owner-pushed): (1) MEASURED signal-loss trace, same population -- the dominant loss is the ESTIMATOR
(-0.505 vs a perfect reader), NOT the salience confound (-0.007); gold-ambiguity -0.05; extraction/typing
downstream. (2) Component brain-fidelity audit: NOT 100% -- the two biggest deviations (a STATIC bag-cosine
estimator; a one-step discount standing in for iterative integration) COINCIDE with the biggest signal loss.
(3) Closed those gaps + prototyped ALL optimizations, each with a can-fail floor + info-free twin:
  - Selective/abstaining bridging (graded-competition ENTROPY gate): confident quartile 0.81 vs ~0.52 blanket,
    selective@50 +0.139/+0.158 CI-sep, shuffled-confidence twin FLAT -- the honest abstain, the biggest win.
  - Multi-cue Competition-Model fusion beats the best single cue +0.048..+0.062.
  - Faithful iterative integration (spreading-activation PPR, gold edges HELD OUT) fused with the distributional
    read beats the static estimator +0.036 (PART) / +0.090 (INSTRUMENT).
  - Context-modulation (additive drive) +0.138, twin flat. Coref-resolved referents: a pronoun target is OOV in
    the meaning store -> +0.239 recovery. Structural relation typing 0.790 with the feature-twin AT CHANCE
    (typing is structural, not distributional). Hypernymy densification lifts PART PPR +0.061.
(4) WALL RESEARCHED -> AUDIT CORRECTED: additive beat "multiplicative gain" because semantic control (LIFG/pMTG)
    is BIASED COMPETITION / selection, NOT a scalar gain (TMS disrupts weak-not-strong associations; Reynolds-
    Heeger gain is a visual-attention import). So the additive-drive + softmax-competition form IS the faithful
    one, and the audit's deviation C3 ("additive where control is multiplicative") is REFUTED. Every landed/
    recommended mechanism is now PINNED; the one non-foundational idea (multiplicative gain) was tested, lost,
    and retired with a reason.

12 experiment cells + a 33/33 scaffold-free witness; two independent gold sources per type; controls/twins
throughout; honest located negatives (typing, sense-resolution, end-to-end ~0.50 extraction-bound). NO hdlab
written (Q111). owner_verdict: (blank).

HONEST CAVEATS: the end-to-end (~0.50) is on generated-modern items and is extraction-bounded -- the clean
per-type capability is the load-bearing claim, not a natural-corpus number. Nothing is landed; the additive
sm.bridges wire is proposed in its brain-faithful form (FUSE estimator + additive-context graded_competition +
entropy abstain + coref-resolved referents + structural typer), argued additive/no-regress. One labelling call
for you (SOLVED vs PARTIAL) is flagged in QUESTIONS.

>>> NEXT PROBLEM (highlighted in SOLVED.md; strategy to file + own):
    land_the_additive_sm_bridges_organ_and_wire_the_meaning_channel_live
    Land the ADDITIVE sm.bridges organ (the meaning channel's first live read()-time consumer): FUSE estimator
    (spreading-activation + distributional over the denser graph) + additive-context graded_competition (NOT
    multiplicative gain) + entropy-gated abstain + coref-resolved sm.entities + the structural typer; couple to
    the reader_meaning_channel stage; measure the LIVE board comprehension lift with the twin LOSING and
    no-regress on non-consumers. Do NOT type the bridge from relatedness (measured structural), chase the
    end-to-end 0.50 as a ceiling (extraction-bound), or reintroduce multiplicative gain (refuted).
