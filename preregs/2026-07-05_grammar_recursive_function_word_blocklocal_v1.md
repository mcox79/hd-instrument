# Pre-registration: grammar_recursive_function_word_blocklocal_v1

Anchor: `grammar_recursive_function_word_blocklocal_v1`
Cell: `experiments/exp_grammar_recursive_function_word_blocklocal_v1.py`
Queue: remote_cpu_queue (CPU probe; numpy only; no torch, no GPU, no LLM)
Date: 2026-07-05
Recommended --timeout: 600 (local FULL preview = 4.0s / 3 seeds / 13 grid points; PROT-019 n/a
  no `_n` suffix; PROT-021 n/a timeout < 14400s)

Note (provenance): the substantive pre-registration lives in the cell header + band constants
(the `FLOOR_*`/`GAP_*`/`HF_*`/`CV_MAX` block). This file materializes those bands verbatim so
queue_add can ship + record provenance. All values transcribed off-disk from the cell; nothing added.

## HONEST FRAMING (USER-LOCKED 2026-07-05 -- carry to verdict_msg + verdict-handler)

This is the LAST unbuilt language layer -- the GRAMMAR long pole (research_language_ingest_glassbox_
scoping_2026-07-05.md, Layer C). It is a NARROW, structured, glass-box demonstration that bounded-depth
RECURSIVE constituency (embedded clauses) + closed-class FUNCTION-WORD OPERATORS (determiners,
auxiliaries, prepositions, complementizers) round-trip through the substrate's block/SBC algebra, and
that a flat (bag) / scrambled (structure-destroyed) control provably CANNOT. It is the grammatical-
STRUCTURE primitive. It is NOT a language model, NOT fluent English, NOT raw-text prediction, and NOT
drawn from real language corpora (synthetic clean sparse-bipolar codes; NO KB referent). Stage-3
compositional structure, NOT Stage-4 LM equivalence. Do NOT narrate any pass as "the substrate speaks
English" or "grammar is solved."

## Mechanism (glass-box; block-local sparse SBC; reuses proven decoder + comprehension mechanisms)

- CLAUSE NODE = S=8 typed structural slots: [COMP, DET_S, SUBJ, AUX, VERB, PREP, DET_O, OBJ]. 5 function
  slots covering 4 closed classes (COMP, DET, AUX, PREP) + 3 content slots.
- RECURSION (banded): N=8192 partitioned into LEVELS*S disjoint blocks (bs = N/(LEVELS*S), shrinks with
  depth). A clause at recursion level L occupies band L. An embedded clause (L>=1) is introduced by a
  COMP operator and ATTACHES to a host content slot (SUBJ or OBJ) of its parent (L-1). The encoder is a
  RECURSIVE function over the constituency tree; the same clause template applies at each level.
- FUNCTION WORDS ARE OPERATORS, NOT CONTENT: function slots decode against a SEPARATE closed-class
  codebook partitioned BY TYPE (selectional restriction). The COMP operator's PRESENCE (block energy)
  GATES the recursion -- the complementizer literally decides whether band L is an embedded clause
  (tested via embed_detection; no hallucinated nesting when COMP absent).
- ATTACHMENT (recursion carrier, relational -- a bag cannot fake it): the host is marked by superposing a
  fixed EMBED_HOOK into the host content block (load L=2 with the host noun). Decode attachment = argmax
  over candidate host slots of corr(block, HOOK). A flat bag merges all blocks -> HOOK corr equal across
  candidates -> attachment at chance.

## Arms (PAIRED -- same trees + same codebooks across arms)

- structured      (PRIMARY, mechanism): banded block-local typed-slot encode + recursive/banded decode.
- flat_bag        (negative control, live): ALL slot codes (+hooks) superposed into ONE band -> no
                    positional/level separation -> collapses (proves STRUCTURE, not tokens, is the win).
- scrambled_roles (negative control, live): tokens placed into a random permutation of the (level,slot)
                    -> block address at ENCODE; decode uses the TRUE map -> mis-addressed -> collapses
                    (proves the SPECIFIC structural addressing is load-bearing).

## Metrics (report SEPARATELY per Fix #28; PAIRED across arms)

terminal_perslot | function_perslot | embed_detection_acc | attachment_acc (chance 1/N_HOST=0.5, PRIMARY
discriminator) | tree_exact (HEADLINE: full bracketed round-trip; chance ~ 0 for controls)

## Pre-registered bands (transcribed verbatim from the cell)

- FLOOR_TREE   = 0.80   HARD_PASS: structured tree_exact at anchor (floor 0.50, band_width 0.50, +5%=0.525;
                         0.80 strictly above -> META_RULE_L satisfied)
- FLOOR_ATTACH = 0.90   HARD_PASS: structured attachment_acc at anchor (chance 0.50)
- FLOOR_TERM   = 0.90   HARD_PASS: structured terminal_perslot at anchor
- GAP_MIN      = 0.35   discriminator: structured attachment_acc - max(control attachment_acc) at anchor
- TREE_GAP_MIN = 0.60   discriminator: structured tree_exact - max(control tree_exact) at anchor
- CTRL_LO/HI   = 0.35/0.65  BIAS gate: control attachment_acc near chance 0.5 at every GATED embed config
- CV_MAX       = 0.15   HARD_PASS: cv of structured tree_exact across seeds at anchor
- HF_TREE      = 0.30   HARD_FAIL: structured tree_exact(anchor) <= this -> mechanism cannot round-trip
- HF_GAP       = 0.15   HARD_FAIL: attachment gap over control below this -> structure not attributable
- ANCHOR = (LEVELS=2, V=256); EASY = (LEVELS=2, V=64)

HARD_PASS: structured round-trips the full bracketed tree at the anchor AND both controls collapse to
chance, cv <= CV_MAX, envelope reaches the anchor.
HARD_FAIL: structured tree_exact(anchor) <= 0.30 OR attachment gap over controls < 0.15.
MIDDLE: structured beats controls but the anchor bar is not met -> report the depth/vocab cliff.

## SCHEMA-VET pre-reg gates

- Compute architecture: (b) sequential-CPU with justification. Per-block matched filter (codebook @ block
  segment) + argmax; per tree trivially cheap; whole FULL grid wall = 4.0s (local, 3 seeds, 13 points).
  Well under the 10s/point batching threshold; cell IS the block-local structural primitive (bit-exact
  numpy reference); no GPU speedup warranted. NumPy-only -> remote_cpu_queue (PROT-020: NOT overnight_queue).
- Storage strategy: SHARDED (block-disjoint per-slot; each structural slot is its own block code; the only
  within-block superposition is host-noun + EMBED_HOOK at load L=2). No bundled-then-composed storage.
- cardinality_ok: EXPECTED_N_UNITS = n_seeds(3) x grid_points(9 gated + 4 boundary = 13) = 39. Verdict
  emits HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if len(per_unit) < 39.
- discriminating_fraction: primary discriminator = attachment_acc; controls sit at chance 0.5 (in the
  [0.35,0.65] band) and structured at ~1.0 at every GATED embed config -> discriminating_fraction = 1.0
  (>= 0.30). The mechanism arm is exact-by-construction on disjoint blocks (see feasibility below); the
  FINDING is the structured-vs-control STRUCTURE discriminator + function-word-operator handling, plus the
  MEASURED recursion-depth capability MAP (boundary points trace the wall). NOT a noisy-channel envelope.
- crlb / capacity feasibility (crlb_n_a declared): block-local per-slot cleanup is exact-by-construction on
  DISJOINT blocks (no cross-slot interference; host block load L<=2). No closed-form argmax-noise floor
  blocks the deliverable. MEASURED architectural wall (seed7, this cell): tree_exact exact (1.000) through
  LEVELS<=6, 0.983 at L8 (bs=128), 0.867 at L10, 0.500 at L12 (bs=85), 0.067 at L16 (bs=64, k=1) -> wall
  at bs<=85 (deeper than any linguistically-meaningful embedding depth). Interpretable: attachment
  (structural link) stays ~1.000 to L12+ while per-slot lexical cleanup (bs-shrink) is the bottleneck.
- discriminator survives scale: measured AT full N=8192 in ALL modes (smoke reduces V-grid to 2, seeds to
  1, trials -- never N, never S). Anchor (L2,V256) is IN the smoke grid -> full-N discriminator preview.
- baseline_in_band (META_RULE_AG): flat_bag / scrambled_roles are NEGATIVE CONTROLS expected AT chance on
  STRUCTURE (attachment 0.5, tree_exact ~0) BY CONSTRUCTION -> EXEMPT from the 0.05<baseline<0.95 in-band
  gate (HP_SCOPE); they carry ONLY the near-chance collapse gate (attachment in [0.35,0.65]). The
  structured arm is the finding, not a baseline. (Mechanism saturating at 1.0 with baselines at chance is
  a MAXIMAL discriminator -- the opposite of the AG saturation failure mode.)
- HP_SCOPE: chain-grade HP gates (tree/attach/term floors + gaps + cv + envelope) apply ONLY to structured.
  flat_bag / scrambled_roles carry ONLY the near-chance collapse BIAS gate. Boundary MAP points are ungated
  and EXCLUDED from the control-bias gate (deep-bs control tie-break is high-variance).
- ARMS-MUST-DIFFER (META_RULE_AF): per-unit composite digests AND recovered-structure digests must be
  hash-distinct across all 3 arms (raises AssertionError otherwise). arms_differ_verified: true.
- final_metrics_atomicity: tmp_replace (metrics.json.tmp -> os.replace).
- except SystemExit: raise BEFORE except Exception (grep-gated; no bare except / BaseException).
- defensive_error_checking: start-marker + heartbeat + crash-diagnostic (CELL_CRASHED metrics + traceback)
  + run_mode-assert (written["run_mode"] == mode). cell_chunked: false (single-shot sweep; 3 seeds in one
  cell, wall 4s, no zombie risk at this speed).
- calibration_check: default_ok_for_this_regime (synthetic clean sparse-bipolar codes; F_SPARSE=0.02 and
  block-local geometry match the proven decoder + comprehension cells).
- progress_logging: line_buffered_stdout (sys.stdout.reconfigure(line_buffering=True)); per-unit print +
  _heartbeat.jsonl. timeout_s (600) < 1800 so the 30min+ heartbeat mandate is not triggered.
- functional_requirements (Gate E): (1) recursive/nested structure -> banded block-local levels + recursive
  encoder; (2) function words as structural operators -> closed-class type-partitioned codebook +
  COMP-gated recursion; (3) attachment/bracketing -> EMBED_HOOK relational binding; (4) structure vs tokens
  -> flat_bag + scrambled_roles controls with identical tokens/codebooks.
- positive_control (Gate D): LEVELS=1 (flat clause, no embedding) reproduces the proven block-local decode
  ceiling (tree_exact 1.000) at the test regime -- the recursion axis extends the block-local decoder
  (cited exact_ordered=1.000 to D<=26). Regime-extension audit: synthetic block-local -> synthetic banded
  block-local = SHAPE_MATCH (same sparse-bipolar-code + per-block-argmax primitive, added band/level index).

## Cited baselines (do NOT rerun)

- data/exp_generation_decoder_gsbc_native_blocklocal_v1 (block-local Stage A/B/C; exact_ordered=1.000 to D<=26)
- data/exp_comprehension_envelope_superposition_vocab_v1 (role-typed partition-restricted decode; superposition load)

## Dispatch note

SMOKE ran locally (direct --smoke, HARD_PASS at full N). No local FULL dispatch (USER-LOCKED: SMOKE-only on
local_cpu_queue). FULL is deterministic numpy (no torch/GPU nondeterminism) -> remote canonical run is
bit-identical to the local preview. FULL to be staged by the orchestrator to remote_cpu_queue.
