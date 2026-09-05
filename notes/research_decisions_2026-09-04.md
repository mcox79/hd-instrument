# Research decisions — 2026-09-04

- Grounded disambiguate-then-bind (sense-discriminative W) brain-fidelity verification:
  `notes/research_grounded_disambiguate_then_bind_2026-09-04.md` — 2/3 mechanism components (encoding
  order; CLS consolidation) already PINNED, built, and NOT the bottleneck; the 3rd (grounding as
  encoding-time resolver) has its closest built analog (P9, ATL hub-and-spoke) already CI-separated
  BELOW the topical floor, and fresh lit-scan finds no support for grounding resolving abstract/regular
  polysemy. Verdict: likely another located negative on the full population (est. a_s 0.22-0.27),
  P_deflated(crosses 0.35)=0.10. Cheap decisive test named (near-zero-cost data re-slice) before any
  full pipeline build; all actionable content is IN the note itself (no companion hand-off file, per the
  no-routing-files override — an erroneously-written hand-off file was retracted in place).
- 2026-09-04: exemplar-based contextual re-representation for subordinate-sense WSD -> notes/research_exemplar_based_contextual_recomputation_wsd_2026-09-04.md (LOCATED NEGATIVE: raw exemplars Zipf-swamp per Blevins-Zettlemoyer 40-62 F1pt rare-sense drop + Reisinger-Mooney multi-prototype beats pure exemplar 0.76 vs 0.60; reinforces existing multi-prototype-W redirect, no new build)
- 2026-09-04: register-general verb-argument attachment mechanism (deep 4-lane lit scan) -> notes/research_register_general_argument_attachment_mechanism_2026-09-04.md — POSITIVE, actionable: human attachment is gated by categorical valency + closed-class scaffold + word-order default (all register-invariant; McRae et al. 1998 fitted weights put structural/frequency-prior ~0.51 vs item-frequency ~0.12), with corpus-like frequency entering only as a small, ONLINE/LOCALLY-re-estimated tie-break (Fine et al. 2013 shows re-calibration within tens of sentences, not a frozen import) — direct mechanistic explanation for why the modern-corpus-trained statistical parser collapses on 19c prose while a human reader does not. 7-stage implementable pipeline spec + 4-condition register-shift cheap decisive test + scrambled-closed-class must-fail control delivered IN the note (no companion hand-off file, per the no-routing-files override). Extends and specializes `research_grammar_construction_resources_for_role_assignment_2026-07-20.md`'s frame-keyed VerbNet/UD stack. P_deflated(7-stage pipeline as built reproduces human-level register-general accuracy)<=0.40 (capped novel synthesis).
