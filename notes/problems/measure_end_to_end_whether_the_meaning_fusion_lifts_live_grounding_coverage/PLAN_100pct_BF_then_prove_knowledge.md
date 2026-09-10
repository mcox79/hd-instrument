# PLAN + CRITICAL CONTEXT (cemented 2026-09-10, pre-compaction). SOLVER session.

> **STATUS UPDATE 2026-09-10 (post-compaction, W19): PHASE A IS CLOSED ON THE LIVE LOOP -- and the A1 parser
> swap below is SUPERSEDED.** The sibling solver landed the PARSER-FREE directional-sequential channel (SEQ),
> which removes BOTH NOT_BF atoms (pos_tagger + arceager) -- strictly more BF than swapping to incremental_parser
> (which still needs pos_tagger). Measured on THIS loop (`exp_meaning_fusion_live_coverage_seq_v1.py`, W19): the
> fully-BF parser-free rep BEATS the live incumbent CI-sep, twin losing (GD_SEQ 0.129 vs 0.037, +0.161 CI
> [+0.006,+0.274]); HONEST negative: SEQ does NOT add over the best grounded rep at 34k exposure (increment -0.034,
> not CI-sep) -> EXPOSURE is the lever. So SKIP A1/A2 (parser swap + pos_tagger); the pos_tagger residual is MOOT.
> Ignore Phase A below except as history. GO STRAIGHT TO PHASE B, sharpened: grow SEQ by reading (parser-free =
> cheap) and re-test the GD_SEQ-vs-GD-distinctive live increment turning CI-sep POSITIVE, twin losing. Full detail:
> SOLVED.md "UPDATE 2026-09-10". A3 (word-class routing for the ADJ loss) may still be a small additive BF win.

Slug: measure_end_to_end_whether_the_meaning_fusion_lifts_live_grounding_coverage. Status PARTIAL.
Read this + SOLVED.md (the running record) first after compaction. Witness: `.venv/Scripts/python.exe
verification/test_meaning_fusion_live_coverage.py` (16/16, W1-W18). Bash cwd resets -> prefix `cd /c/AI/hd-
instrument &&`, use `.venv/Scripts/python.exe`, cap OMP/OpenBLAS/MKL/NumExpr=2.

## SCOPE (hard)
Write ONLY experiments/, verification/, this folder. NO hdlab/ (Q111 -- strategy lands the live wire). Never
set owner_verdict. SimLex-999 is the identity gold; NO WordNet in any channel graded on SimLex (circular --
WordNet is a labelled *ceiling reference* only). Every load-bearing claim: info-free twin LOSES + CI on the
loop's own population; grade deflated; keep SOLVED.md ASCII-only + `tools/problem_ledger.py --check` clean;
add every new cell to the witness. If a tool call is denied, STOP and report verbatim.

## STATE (measured, witnessed -- verify on disk, don't trust recall)
- The fully-BF sense-assignment decision = GROUNDED-DISTINCTIVE ATL representation (FIX #3/#5, no bag/no
  parser) (+) DEPENDENCY-PPMI PROPERTY-SVD is-a channel (paradigmatic; Levy-Goldberg + Rogers-McClelland) +
  SELF-CALIBRATING SDT accept criterion on the z_top standout (FIX #7). It BEATS the distributional incumbent
  CI-separated (+0.158 MRR@0.5) and grounded (+0.055) on the live 556-word anchor-pool decision.
- vs BRAIN (AUF-MRR, oracle=1.0): incumbent 0.037 (~4%) -> grounded 0.198 -> grounded-distinctive 0.232 ->
  grounded(+)is-a ~0.27 (~27%, BEST landable) -> WordNet-supplied is-a ceiling 0.650 (~65%, circular) ->
  reader ~1.0. We moved ~4% -> ~27% fully BF.
- SIGNAL-LOSS TRACE (W16, identity=SimLex rho): bag -0.02 (PRIMARY LOSS: unordered pooling = first-order
  syntagmatic/relatedness, not paradigmatic identity) -> grounded 0.22 (recovers from perception; residual
  sibling confound) -> distinctive 0.27 -> is-a 0.23 -> WordNet ceiling 0.50 (id>>rel = clean identity).
  Per-POS: NOUN 0.315, VERB 0.255, ADJ 0.099 (adjective loss -> word-class routing).
- BF CONFIRMED at every COMPUTATION rung (math+citation, W16 table): lemmatize (Rastle-Davis), random proj
  (JL/Marr), superposition, z-score/whiten (Carandini-Heeger / Patterson-Nestor-Rogers), PPMI (rectified
  MI/Hebbian, Levy-Goldberg), property-SVD (Saxe-McClelland-Ganguli PROVE GD learns these modes), role-filler
  binding (circular convolution, FHRR/HRR PINNED), cosine readout (Georgopoulos), softmax (Gibbs), fusion
  (Bayes cue integ, Ma/Pouget), SDT accept (Yonelinas + Bruce-Young).
- TWO NON-BF ATOMS remain: (1) the unordered POOLING -- but the BF fix (role-binding / paradigmatic-is-a)
  REPLACES it; (2) the SYNTACTIC-ROLE SOURCE: the working is-a PPMI-SVD draws roles from arc-eager
  (`hdlab.arceager_parser`, NOT_BF); the BF replacement is `hdlab.incremental_parser` (BF_SPIRIT, verified to
  supply SUBJ/OBJ frames), whose own upstream is the UPOS tagger `hdlab.pos_tagger` (confirm/replace).
- MEASURED NEGATIVES (do NOT redo blindly): separate-pools vs feature-fusion (null; joint property-SVD is
  correct); genus-centroid differentia (neutral even with the grown REAL read genus); SVD-densification of
  sparse PPMI (hurts -- smooths distinctive contexts); RAW grow-by-reading to 800k simplewiki sents (coverage
  0.17->0.58 but quality flat -> raw regresses); CLEAN-isa confirmation gate (removes noise-harm but coverage
  collapses to ~1% -> clean+coverage not both from reading); role-filler BINDING positional & syntactic
  (directionally right but data-hungry/noise-limited -> PPMI-SVD is the low-variance estimator of the same
  paradigmatic signal). matched-count online correct-coverage vs incumbent = directional not CI-sep (judge
  noise). Corpora on disk: simplewiki_clean_v1.txt (2.3M sents) + ~12 OpenStax textbooks (definition-dense).

## THE PLAN (owner-proposed 2026-09-10; I AGREE, with the order justified)
Two phases. Do PHASE A first: the owner's principle is that a BF component that "isn't working" almost always
has a non-BF UPSTREAM; and you cannot cleanly PROVE knowledge is the lever while a non-BF atom (the parser)
confounds the channel carrying it. So make the chain 100% BF, THEN prove knowledge moves the needle.

PHASE A -- ENSURE 100% CHAIN MATHEMATICAL BF (mostly solver scope):
  A1. Swap the is-a channel's syntactic-role source arc-eager (NOT_BF) -> incremental_parser (BF_SPIRIT).
      Re-measure the dependency-PPMI property-SVD is-a channel with the BF role source: does removing the last
      non-BF atom preserve/raise identity rho 0.23 (twin losing)? Confirm the whole is-a chain is now BF.
  A2. Confirm/replace the UPOS tagger (`hdlab.pos_tagger`) BF status (it feeds the parser). If NOT_BF, name the
      BF replacement or mark it the deepest residual. Goal: EVERY component from text->decision 100% math-BF.
  A3. Wire the WORD-CLASS-ROUTED read-out for the adjective loss (ADJ rho 0.099, 3x weaker; all gradable):
      route gradable adjectives -> scalar-magnitude op (`hdlab.scalar_adjective_operation`), else -> the
      identity representation, via the validated `hdlab.meaning_operation_router`. Measure the lift (bounded:
      adjectives ~12% of pairs). This is a validated-organ WIRING, fully BF.

PHASE B -- BUILD + PROVE KNOWLEDGE MOVES THE NEEDLE (north-star + solver-prototypable):
  The dominant lever is CLEAN is-a KNOWLEDGE (WordNet lever 27%->65%, +0.488 CI-sep; but that is circular +
  supplied). RAW reading does NOT supply it (measured). So build the CLEAN knowledge brain-foundationally and
  PROVE it, with the KNOWLEDGE-SHUFFLED info-free twin LOSING:
  B1. Prototype the online CLEAN-knowledge mechanism (north-star curated-foundation-first + propose-verify-
      RESOLVE): the consolidation-gate / MINERVA-2 idea, but the CLEAN-vs-raw test showed confirmation trades
      coverage. Try: cross-SOURCE agreement (read edges confirmed across INDEPENDENT documents), sense-
      RESOLUTION, and/or a curated NON-circular is-a foundation asset (admissible offline asset; NOT WordNet
      if graded on SimLex -- use a held-out is-a gold or a different ontology, and grade on SimLex).
  B2. PROVE it on the LIVE loop's coverage-QUALITY: the clean-knowledge is-a channel, fused with grounded,
      lifts the anchor-pool decision CI-separated over grounded, with the KNOWLEDGE-SHUFFLED twin LOSING (the
      control that isolates KNOWLEDGE from mechanism), and shows the vs-brain ladder climbing 27% -> toward 65%.
  B3. The actual LIVE landable win = strategy lands the fully-BF decision into `canonicalize` (Q111) + adds a
      correct-coverage metric to the loop (the count is quality-blind). Solver hands the wire spec + the proof.

## AGREEMENT (my read)
YES. The chain is BF at every computation; the ONLY non-BF atom left in the working channel is the parser ->
Phase A closes it (incremental_parser). And knowledge IS the dominant lever (shown), but must be PROVEN
brain-foundationally with the knowledge-shuffled twin losing, from a CLEAN non-circular source (curated
foundation and/or online propose-verify-resolve) -- Phase B. Order = A then B, because a non-BF parser could
confound the knowledge test and the owner's rule is fix-upstream-BF-first. This closes the problem to a
fully-complete, exceptional, 100%-BF solution whose remaining distance to the brain is proven-to-be knowledge.
