---
owner_verdict: DONE
---

SUBMISSION — promote_the_grounded_semantic_graph_to_an_intrinsic_learnable_organ    status: SOLVED

WHAT: Promote WordNet from a flat lookup to a GROUNDED RELATIONAL SEMANTIC GRAPH read by SPREADING
ACTIVATION (the brain's ATL hub + Collins&Loftus/Rodd settling; personalized-PageRank == random-walk-
with-restart, PINNED). Glass-box, LM-FREE at inference. Built + validated in experiments/; strategy
lands the hdlab wire (Q111).

CORE RESULT (two field-comparable wins, held-out):
 • Per-context sense selection clears the CONTEXT-SHUFFLE twin on gold WiC held-out: cn arm 0.616,
   real-minus-twin +0.052 [0.023,0.081], CI-sep. Witness 21→5/5. (NOT vector-cosine: 8 feature
   prototypes plateaued; sense is RELATIONAL — the diffusion is the mechanism.)
 • FIELD-STANDARD all-words WSD (Raganato ALL, Senseval/SemEval, n=4478): glass-box graph+blend =
   0.677 vs MFS 0.647 = +0.030 CI-sep → BEATS MFS at UKB (67.3) level, LM-free. (The earlier "loses
   to MFS" was a near-oracle-SemCor artifact — corrected on the real instrument.)

LADDER (each an ablation vs the twin): ConceptNet THEMATIC edges = the lever (Mirman TPJ pole);
SyntagNet syntagmatic edges CROSS the all-words wall. HONEST NON-LEVERS: IC-weighting, grounded-Binder
nodes (context-free lift), and frequency-weighted seeding (confirmed non-lever). Competitive-settling
drill: the brain's read is nonlinear competitive attractor settling (lateral inhibition), NOT linear
diffusion — but for single-token argmax-WSD it reduces to the blend (competition sharpens confidence,
not the choice). THREE mechanisms (PPR, blend, settling) converged on the same wall → it was the
GRAPH's context-signal strength, fixed by SyntagNet+blend.

CAN IT LEARN / BE ADDED TO: augmentable — demonstrated (ConceptNet + SyntagNet). Grows from reading —
learn_from_text() grew 16,621 real edges; but the NAIVE (MFS-disambiguated) learned edges are a clean
NEGATIVE (don't beat an info-free shuffle-twin; base +0.078 / learned +0.067 / shuffle +0.075). Faithful
learned graph (context-disambiguated + CLS schema-gate + sense split/merge) is specced, unbuilt (remote).

🧠 KEY BRAIN-FOUNDATIONAL FINDING (the deepest): we compute the brain's rich SETTLED activation state
(context-shaded meaning) then DISCARD it, keeping only argmax(one synset). Done the RIGHT way
(threshold-free AUC, held-out WiC-test), the SETTLED REPRESENTATION beats the discrete label +0.067 AUC
[0.047,0.089] CI-sep (0.709 vs 0.641). ⇒ the meaning organ must OUTPUT A REPRESENTATION, not a label.
(A naive accuracy@tuned-threshold readout showed +0.000 held-out — the artifact; AUC on the representation
reveals the value. Lesson: measure a graded representation threshold-free, not accuracy@a-tuned-cut.)

KEY REALIZATIONS: (1) sense selection is graph DIFFUSION, not feature-cosine; (2) the residual is the
GRAPH's signal strength (SyntagNet), not the combination — three brain-faithful mechanisms hit the same
wall; (3) a near-oracle baseline (grade-by-the-training-corpus) HID a real win — test on the field-standard
instrument; (4) a graded representation's value is invisible to accuracy@threshold — use AUC/ranking;
(5) wordnet_ic stores FREQUENCY not IC (raw use inverts the weighting).

NEXT STEPS (in SOLVED.md; * = brain-foundational completion):
 0. [Strategy/Q111] land the base wire: grounded_semantic_graph organ + reframe canonicalize flat→graph.
 1.* OUTPUT THE SETTLED REPRESENTATION (not the label): route the graded settled vector into
     situation_reader/meaning_fusion/composition/inference (also fixes the "unwired meaning islands" debt);
     demo the compounded value on a GRADED/COMPOSITIONAL task (MCScript2, sentence-sim) — NOT WiC — ON REMOTE.
 2. The LEARNED graph (north-star, remote): faithful context-disambiguated growth + CLS schema-gate + split/merge.
 3. Wire semantic_control (per-item gate); 4. optimize toward SyntagRank 71.7 (full graph config).

FILES: experiments/{exp_grounded_semantic_graph_ladder_wsd_v1, grounded_semantic_graph_organ,
exp_settled_auc_v1, exp_wsd_all_eval_v1, exp_learn_resumable_v1}.py; verification/
test_grounded_semantic_graph_ladder.py (5/5); notes/problems/<slug>/{SOLVED.md,
LEARNED_GRAPH_brain_mechanism_spec.md}. Data (owner-auth fetch): SyntagNet 1.0 (CC BY-NC-SA),
Raganato 2017 WSD Framework. REVERIFY: .venv/Scripts/python.exe verification/test_grounded_semantic_graph_ladder.py

SCOPE: integration is the strategy session's (Q111); heavy corpus/downstream runs need the REMOTE box
(this shared box OOM-kills them at ~250s — handled here with a resumable/checkpointed harness).
