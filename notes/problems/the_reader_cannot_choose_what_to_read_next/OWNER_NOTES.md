---
owner_verdict: DONE
---

═══════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — the_reader_cannot_choose_what_to_read_next   (STATUS: SOLVED)
hdlab/ UNTOUCHED (proposed diff only, board Q111). AWAITING owner_verdict: DONE.
REVERIFY: .venv/Scripts/python.exe verification/test_reading_comprehensible_input.py        -> 6/6
          .venv/Scripts/python.exe experiments/run_ci_zpd_parallel.py --budget 6000 --seeds 0,1,2 --jobs 6
                                                    -> data/exp_..._parallel/metrics.json = HARD_PASS
          python tools/problem_ledger.py --check    -> malformed/incomplete: 0
═══════════════════════════════════════════════════════════════════════════════════════════

BAR (PROBLEM.md §7): a brain-faithful reading-foraging policy that BEATS FROZEN and RANDOM CI-separated
on a real downstream metric, info-free twin LOSING CI-separated; break the FROZEN-beats-FORAGE wall on
real text; brain-faithful mechanism; propose the hdlab diff. A rigorous negative is a full pass.

VERDICT: SOLVED — but the BRIEF'S MECHANISM IS REFUTED-ON-DISK and replaced with a MORE brain-faithful one.
- The brief's MVT-forager-on-a-value/gap/learning-progress signal was already built + run (neighbouring
  `aimed_reading...`, REFUTED): it LOSES to the fixed curriculum register-controlled 3/3 seeds, and its
  info-free twin does NOT lose (learning-progress carries no between-source information). WHY (drilled):
  LP is a difference of two noisy estimates, unusable for few-sample between-source selection; fraction-
  known is directly observable. So LP is a within-source LEAVE signal, useless for SELECTION.
- THE BRAIN-FAITHFUL ANSWER = COMPREHENSIBLE INPUT / ZPD (Krashen i+1; Vygotsky; Metcalfe ROPL): read the
  source with the most NEW learnable words in comprehensible context. Register-controlled coverage
  (3000-word probe stratified by FROZEN-reachability, equal-weighted; 6000 sentences x 3 seeds):
  CI 0.081 vs FROZEN 0.031 (delta +0.050, worst-seed +0.044, boot CI [0.041,0.060], all seeds CI>0) and
  vs RANDOM 0.029 (+0.053); info-free twin (shuffled comprehensibility) 0.015 LOSES (+0.067 CI-sep).
  REPLICATED HARD_PASS on the remote machine (independent), all-seed CI-separated, twin loses.

FRONTIER WORK (all measured, brain-drilled):
- ANTI-STARVATION FIX: a higher/adaptive threshold STARVED (a low-vocab reader finds no 85%-known
  sentences). Root cause (Yu&Smith cross-situational learning): binary whole-sentence gate -> GRADED
  PER-WORD partial credit. CI_GRADED cures it (grounds 821-962 vs 50-66) and matches CI_050.
- SELECTION IS CONVERGED: 3 comprehensible-input variants (0.5 / whole-sentence graded / local ±4-word
  window) all TIE at ~0.08 — you cannot out-select a grounding ceiling.
- UNDERPERFORMANCE DECOMPOSED (diagnostic): the reader REACHES 5.2x more target vocab than it GROUNDS
  (0.338 vs 0.064); of words read >=4x, 66% never ground = 59% CONSOLIDATION-depth (>=4 traces, single-
  averaging never grounds -> CLS 2-stage + retrieval-practice, the LEARNER/consolidation problem) + 36%
  abstract-word GATE MISMATCH (single-anchor cos>=0.45 vs ATL many-weak-channel graded FUSION; all
  refused anchors sit at 0.22-0.45, a calibration not a no-meaning gap -> reader_meaning_channel/ATL) +
  4% correct closed-class + 1% extraction. Grounding QUALITY ~35% (WordNet) => the abstract fix must
  RAISE precision (wire meaning_fusion.py + a VAD affect spoke + the built-but-off margin_z_min into
  canonicalize), NOT lower the threshold. Both walls are DOWNSTREAM, not reader-scope; sharp hand-offs.

PROPOSED hdlab DIFF (default-off; strategy re-verifies + lands): (1) wire the enumerable corpus_registry
shelf as the readable universe (replace the 4-entry dict); (2) add a GRADED comprehensible-input source
selector consuming the reader's own known-vocab (no arbitrary threshold, cannot starve; greedy is near-
optimal); (3) keep the within-source MVT leave-rule on grounding-yield. Do NOT land the refuted LP
selector or a separate EVC-halt (redundant per Fromer 2021).

AUDIT UPDATE: "information foraging ... FROZEN beats FORAGE" -> the MVT-forager-with-value/LP signal is
REFUTED for corpus SELECTION; the working mechanism is COMPREHENSIBLE INPUT / ZPD (beats floors CI-sep,
twin loses, replicated). MVT's faithful role is within-source LEAVE only. gap_detector is NOT the corpus-
selection signal (a directly-observable known-fraction is); its home is per-item novelty.

KEY REALIZATIONS: (1) the prior-work check found the brief's mechanism already refuted AND the winning
one already proven+parked; (2) a signal's usable LEVEL matters — LP works within-source (dense), fails
between-source (sparse), while comprehensibility is observable; (3) the starvation wall was a GRANULARITY
+ COMPARATOR bug (whole-sentence binary -> per-word graded; absolute -> relative); (4) pushing selection
three brain-faithful ways and getting a TIE is itself the proof the ceiling is downstream; (5) aggressive
wall-drilling split the 66% loss into two different mechanisms with different fixes — and grounding-
quality (35%) proved the abstract fix is precision-raising fusion, not a cheap threshold move.

FILES: experiments/{exp_reading_comprehensible_input_zpd_v1, run_ci_zpd_parallel,
exp_reading_grounding_depth_diagnostic_v1}.py; verification/test_reading_comprehensible_input.py;
notes/problems/the_reader_cannot_choose_what_to_read_next/{SOLVED.md, prereg_..., REMOTE_RUN_REQUEST_...,
research_finer_comprehensible_input_zpd_...}; notes/{research_comprehensible_input_starvation_mechanism_,
research_atl_grounding_anchor_gate_mechanism_drill_}2026-08-28.md. hdlab/ UNTOUCHED.

TLDR: the reader couldn't choose what to read; the brief's "forage where you're learning fastest" idea was
already tried and loses (that signal is too noisy to compare books). The way that works — how children
learn — is COMPREHENSIBLE INPUT: read where there are the most new words in sentences you mostly already
understand. That reader beats a fixed schedule and random selection ~2.6x on a fair vocabulary test, on
two machines, and a scrambled-signal version fails. Pushing the selector three more brain-faithful ways
didn't move it — because the real limit is downstream: the system reaches 5x more words than it durably
LEARNS. We drilled exactly why (a memory-consolidation gap + an abstract-word meaning gap), and both are
separate problems with concrete brain-faithful fixes. QUESTIONS: none. NEXT: land the default-off hdlab
diff; the two downstream fixes go to the consolidation/learner and meaning-channel/ATL problems.
═══════════════════════════════════════════════════════════════════════════════════════════
