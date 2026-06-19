# Research request — Path 5 Bayes-optimal lower bound on substrate generation (GPT-quality reframe)

**Filed:** 2026-05-24 by orchestrator (inline-via-main-thread per orchestrator post-compaction brief Section 2 Agent dispatch unavailable in sub-agent context)

**WHAT** — derive a Bayes-optimal lower bound on substrate-native generation
perplexity from the R16 superposition capacity / R23 coding-rate bounds / R26
free-probability composition frameworks. If the bound is at or below GPT-quality
perplexity at matched compute, the GPT-quality capability question reduces to an
engineering problem, not a substrate-physics ceiling. This is the theoretical
companion to the empirical Paths 3 + 1.

**WHY (pointers, not summaries)**

- Reframe note: `notes/research_tier1_gpt_quality_reframe_2026-05-24.md` (read this first)
- R16 superposition capacity framework: search recent research_*.md notes for
  R16 derivation + Frady-Sommer sparse-vector capacity reframing (v2 cap_map
  update has the pointer)
- R23 coding-rate bound framework: search research_*.md for R23 + coding-theory
  drills
- R26 free-probability composition framework: search research_*.md for R26 +
  free-cumulants / mingo-speicher
- R29 noise-tolerant readout: companion framework; supplementary
- Compute-matched GPT-2-small reference: 124M params; standard byte/token
  corpus perplexity numbers
- AGS scaling form: companion to Path 3 (exp_dev) — Path 5 is the theoretical
  ceiling, Path 3 is the empirical extrapolation; they should agree
- Pause flag: ACTIVE (no pause) — confirmed at orchestrator cycle 16:20

**CONTRACT** — deliverable shape

- A short research note (~1500-3000 words) at
  `notes/research_path5_bayes_lower_bound_<date>.md` deriving:
  1. Bayes-optimal lower bound on per-token NLL / perplexity from R16 capacity
  2. Tighter bound (if applicable) from R23 coding-rate
  3. Composition adjustment (additive or otherwise) from R26
  4. Comparison: bound vs GPT-2-small published perplexity at matched compute
  5. Decisive prediction: which framework (capacity / rate / composition) binds
     first, and at what (N, K, M) regime the bound becomes non-trivial
- Cite literature for each framework — audit that the derivation matches the
  cited paper, not just the framework name (per [[feedback-verify-implementations]])
- Identify what empirical observation would falsify each step of the
  derivation (per [[feedback-lit-scan-calibration-penalty]])
- Identify research-field adjacencies that should be drilled if Path 5 returns
  a tight bound that conflicts with Paths 3/1 empirics (per Research field
  advisor heuristic — see `tools/orchestrator/research_field_advisor.py`)

**AUTONOMY DECLARATION** — you decide:
- Exact derivation strategy (replica method / Gaussian-process kernel / direct
  combinatorial / convex-analytic / etc.)
- Which sub-framework binds first (capacity / rate / composition) and how to
  argue for it
- What counts as "compute-matched" GPT-2-small (params / FLOPs / tokens / etc.)
- Which adjacencies to flag for follow-up drills
- Whether to include the R29 readout-side bound or defer
- Whether the bound is information-theoretic (data-processing inequality
  side) or operational (achievable-rate side)

**Discipline pointers** (citations only — no verbatim re-statement):
- Per [[feedback-no-experiment-design-in-prompts]]: this prompt declares autonomy
- Per [[feedback-verify-implementations]]: derivation must match cited papers
- Per [[feedback-lit-scan-calibration-penalty]]: deflate confidence on novel
  synthesis claims; substrate is in uncharted regime
- Per project_research_playbook item 5 (verify-lit) + item 6 (distillation)
- Per [[feedback-for-you-tab-primary-channel]]: status_log entry on delivery
  with plain_language + importance HIGH (this is a load-bearing theoretical
  result)
- Per [[feedback-subagent-model-optimization]]: this is theoretical synthesis —
  appropriate for Sonnet-default if Research /loop runs Sonnet; orchestrator
  defers model choice to Research role policy
- Per Research-cycle PROT-003: file slash-command body content if not already
  set up; cycle on /research-cycle

**Return format**: filed note + one-line summary of the bound (number + which
framework binds) for main thread to status_log.
