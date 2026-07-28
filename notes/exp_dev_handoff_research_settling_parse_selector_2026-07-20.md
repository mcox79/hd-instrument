# exp_dev hand-off — research: settling parse-selector (coherence-as-attractor-stability)

**Filed-by:** research (3x parallel Sonnet lit-scan + director synthesis), 2026-07-20.
**Trigger:** `notes/research_brain_settle_to_coherence_parse_selection_2026-07-20.md` — the 3-axis
brain drill on Kintsch Construction-Integration settling, N400/Rabovsky settling-residual-as-coherence,
and Hopfield/resonator-network convergence-confidence literature. Read that note in full before
designing any cell; it contains the full mechanism grounding, the 9 fairness guards (G1-G9), the
richness-sweep operationalization, and the falsifiable HARD-PASS/HARD-FAIL bands verbatim.
**Pause state:** respect `data/orchestrator_paused.flag` if present — do not ship without checking.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off gives anchor pointers and why-now
context, NOT a prescribed cell implementation. exp_dev owns cell design, pre-reg, smoke gate, and
dispatch.

## Why this is actionable now

The research note grounds a specific, falsifiable mechanism: score candidate role-assignment parses
of a genuinely syntax-underdetermined sentence by the RESIDUAL-OF-CHANGE of their composed vector
during an iterative clean-up/settling dynamic against the codebook (a resonator/Hopfield-style
relaxation), and test whether that residual (a) discriminates the human-preferred reading better than
a one-shot thematic-fit baseline, and (b) sharpens as codebook relational-structure richness increases
(holding size/N fixed to avoid the documented capacity-cliff confound). This is independent of the
stalled CPCL-v2 coherence-loop crux (per the backup doc's forensic-audit hold) — it is a decode-time
disambiguation/confidence readout, not a train-time contrastive-learning signal — and can be built and
smoked without waiting on that forensic audit's outcome.

## Anchor candidate (single, rank 1 by construction — the only leg cheap enough to smoke standalone)

1. **Settling-residual parse-selector on a small genuinely-ambiguous sentence set, richness-swept.**
   Build: (a) a small closed set (~30-50 items) of syntax-underdetermined sentences with human
   gold-preference labels drawn from existing psycholinguistic norming corpora (PP-attachment
   preference sets, reversible-thematic-role stimuli — do not hand-author these, use existing
   norming data so gold labels are not self-generated); (b) construct both candidate parses per
   item as composed vectors using the EXISTING binding/composition mechanism already in the
   codebase (do not invent a new composition operator); (c) run the existing (or a minimal new)
   iterative clean-up/settling dynamic against the codebook for a fixed, pre-registered
   max-iteration budget; (d) score by residual-of-change across the last k iterations, normalized
   per G1; (e) compare against the zero-iteration control (G2), the one-shot thematic-fit baseline
   (G3 — reuse the existing `schema_fit_gate()`-style cosine-to-centroid score from
   `experiments/exp_role_filler_factorization_reader_coupled_cg_v1.py` as this baseline rather than
   inventing a new one), and the two must-fail controls (G4a shuffled-codebook, G4b inverted-score);
   (f) sweep >=4 richness levels operationalized as relational-structure density at FIXED codebook
   size/N per G7 (vary only the corpus-fraction used to fit the codebook's relational geometry).
   Tier hint: MEDIUM effort — reuses existing composition + codebook + (likely) existing clean-up
   machinery; the new work is the residual-scoring wrapper, the norming-corpus sourcing, and the
   richness-sweep harness. Estimate ~1-2 days including sourcing a real ambiguity-norming dataset.
   Why now: independent of the CPCL-v2 forensic hold: it tests whether "coherence" is a discriminating
   readout at all in this program's current codebook maturity, which is diagnostic evidence either way
   for that pending forensic question (per the research note's cross-thread synthesis section), and it
   stands alone as a candidate decode-time disambiguation feature regardless of that audit's outcome.

## Context pointers (file paths, not summaries — read these, don't re-derive)

- `notes/research_brain_settle_to_coherence_parse_selection_2026-07-20.md` (this drill's full note —
  mechanism grounding, all 9 fairness guards G1-G9 in full, richness-sweep operationalization,
  falsifiable predictions with exact HARD-PASS/HARD-FAIL thresholds, citation list)
- `notes/research_coherence_schema_fit_gate_brain_drill_2026-07-19.md` — the existing first-draft
  `schema_fit_gate()` (in `experiments/exp_role_filler_factorization_reader_coupled_cg_v1.py`, lines
  278-322) is the required G3 real baseline; do not invent a different baseline.
- `notes/SYNTHESIS_platform_maturity_and_the_missing_learning_loop_2026-07-20.md` — cross-thread
  context on the CPCL-v2 crux this anchor is diagnostically adjacent to (not a dependency).
- Whatever existing resonator/clean-up or iterative-unbind machinery already exists on disk for
  the substrate's codebook (search before building — this program has prior Frady/Sommer-style
  resonator-network drills per the meta-map's `modern-hopfield`/`sparse-coding` fields); reuse rather
  than reimplement if a clean-up loop already exists.

## Contract

- exp_dev authors + smokes locally, returns the exact `queue_add.sh` dispatch command if queue
  compute is warranted (this may run inline/local given the modest item count); orchestrator ships +
  REMOTE VERIFIES post-ship if queued, per locked ship policy.
- Pre-register per envelope-fail-bands using the HARD-PASS/HARD-FAIL thresholds given verbatim in
  the research note's "Falsifiable predictions" section (4 HARD-PASS conditions, 4 HARD-FAIL
  conditions — copy verbatim into the pre-reg, do not paraphrase the margins).
- Deflated confidence for this anchor per the research note: 0.35 (novel-synthesis cap applied,
  further deflated for the richness-sharpens leg specifically, which has no direct brain-study
  precedent — analogy-only support). Do not round up.
- Carry forward the design risk flagged in the research note: G7 (capacity-cliff confound) is the
  single highest-risk fairness trap — if codebook size/N is allowed to vary across richness levels
  even slightly, any observed "richness effect" is more likely the documented Frady et al. (2020)
  D/N capacity-cliff artifact (transition ~0.056, collapse ~0.138) than a genuine coherence-sharpening
  effect. Verify the D/N ratio is logged and flat across every richness level BEFORE interpreting any
  richness-sweep result.

## Autonomy declaration

exp_dev owns: which specific psycholinguistic norming corpus to source ambiguity items + gold labels
from; whether to reuse an existing clean-up/resonator implementation or build a minimal new one;
the exact number of richness levels (>=4 per the guard, exact count and corpus-fraction schedule at
exp_dev's discretion); smoke design; and whether any of G1-G9 warrants a kill decision at smoke scale
before a fuller run (e.g., if G2's zero-iteration control already matches multi-cycle settling at
smoke scale, that is itself a valid, reportable kill on the "settling adds value" claim — do not
force a full richness sweep to try to rescue a G2 failure).
