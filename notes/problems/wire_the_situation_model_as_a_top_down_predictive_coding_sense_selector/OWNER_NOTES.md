---
owner_verdict: DONE
---

SUBMISSION — wire_the_situation_model_as_a_top_down_predictive_coding_sense_selector

STATUS: PARTIAL — a rigorous, POWERED, multiply-controlled LOCATED NEGATIVE with the failing
component named + quantified (the bar's full-PASS located-negative condition), plus one confirmed
brain-faithful sub-mechanism. Ledger-valid; witness 4/4.
Reverify: .venv/Scripts/python.exe verification/test_topdown_situation_sense_selector.py

RESULT (plain): I built the brain's method for picking a word's RARE meaning — keep the common-meaning
bias, and only override it when a separate, frequency-free structural signal says the common meaning
doesn't fit, using the brain's own inhibition circuit. The override SIGNAL works and is better in its
brain-faithful (directional) form. But it can't win overall, and I found exactly why, with numbers.

POWERED (SemCor, 30 files, n=17,317 items / 5,281 subordinate; bootstrap CIs):
- CONFIRMED brain-faithful (NEW): the DIRECTIONAL predictive-error detector (domI = N400 on the DOMINANT
  reading) AUC 0.6895 > symmetric conflict 0.6652 > bag 0.6407 — all far above the brief's claimed ~0.51
  (the disk corrects the brief: a gold-blind detector clearly exists). Frequency-independent STRUCTURAL
  context beats bag; DISCOURSE aggregation DILUTES (0.61).
- THE WALL is a BASE-RATE see-saw: dominant senses sit at 0.9828 (MFS near-perfect), subordinate is only
  ~30% of items, so any override that touches a dominant item is a near-certain loss. No gated config beats
  the MFS floor: best NET -0.0013, CI[-0.0025,-0.0002] (CI-separated BELOW it).
- DECOMPOSED: net = fired*[p*a_s - (1-p)*c_d], measured p~0.48 (detector precision), a_s~0.33 (override
  accuracy = "which specific rare sense", THE BINDING LIMIT), c_d~0.64 (dominant disruption). Break-even
  needs p*a_s~0.34; we get ~0.16 — must ~2x, and the binding term is a_s = comprehension.
- CONTROLS (all CI-separated): info-free shuffled-structure twin LOSES (+0.0059); error-gate ablation
  REMOVES the gain (net -0.108); subordinate recovery real (+0.0076) bought with dominant loss (-0.0052).
- PROTOTYPED both difference-fixes: detector precision IS cheaply improvable (multi-signal 0.74->0.77);
  override accuracy is NOT a readout fix (sense-signature readout is WORSE) -> a_s is the WORLD-KNOWLEDGE
  SOURCE, not the readout. Detection is buildable; generation (the binding limit) is the North Star.

HONESTY NOTE: a 4f-smoke "Zwaan situation-dimension signature" (recovery larger on event/abstract than
spatial/object) DID NOT REPLICATE at power (n=36 -> 481 reversed it) and is RETRACTED. The powered run
existed to catch exactly this.

WHERE WE DIFFER FROM THE BRAIN (precise): we replicated the DETECTION + INHIBITION + asymmetry half of the
circuit (and improved the detector to its directional/N400 form). What's missing is the GENERATIVE half — a
world-knowledge situation model that predicts the SPECIFIC sense. Detection != generation; generation is
a_s~0.33. Research (24 sources): the human brain is ALSO see-saw-limited (partial genuine difficulty), but
a_s has NO human benchmark (fidelity gap, not proven ceiling); UKB (independent lab) confirms graph-spreading
defaults to frequency.

HOW TO FULLY SOLVE IT — GLASS-BOX, BRAIN-FOUNDATIONAL (NO external LLM at inference):
1. [NORTH STAR] the generative world-knowledge SITUATION/COMPREHENSION model — supplies the sense-SPECIFIC
   top-down prediction; this is the a_s gap and where the gains live.
2. Sense-SPECIFIC continuous representation (meaning_fusion + ultrametric_clustering granularity) so the
   situation can discriminate WHICH rare sense — the representation fork that raises a_s.
3. Richer world-knowledge SOURCE (FrameNet roles / Chambers-Jurafsky script chains / denser thematic KG) so
   the situation INFERS unmentioned concepts (bounded test — selectional-class risks dominance-reinforcement).
4. [cheap de-risk] grounded sensorimotor-simulation override on the concrete-sense subset (spatial/object
   recovered well at power); and MEASURE the human/inter-annotator ceiling to bound the real headroom.

FOR STRATEGY: this problem's approach is near-MAXED and fully drilled — do NOT tune it further. TIER-1 wire
(default-off, witnessed, Q111): the DIRECTIONAL domI detector as semantic_control's frequency-independent
trigger + the MFS-default biased-competition read path — land as an INSTRUMENT, not a default (the override
does not net-gain). The gains are in the North-Star follow-on (a_s = comprehension).

FILES: experiments/exp_topdown_situation_sense_selector_v1.py (organ + sweep + self-test),
  verification/test_topdown_situation_sense_selector.py (witness 4/4),
  notes/problems/<slug>/{SOLVED.md, FINDINGS.md, DESIGN_brain_foundational.md},
  notes/research_subordinate_sense_topdown_predictive_precision_2026-09-02.md.
Reuses UNMODIFIED: hdlab/semantic_control.py (LIFG), the settling/prior/graph from the parent cells, SemCor,
spaCy (LOCAL, cached). AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT §2b included in SOLVED.md.
