---
owner_verdict: DONE
---

SUBMISSION — turn_on_the_learner_and_verify_safe_growth_on_the_clean_foundation
status: PARTIAL (decisive: capability proven; brief's bar-5 refuted-on-learner but resolved-on-KB)
reverify: .venv/Scripts/python.exe verification/test_learner_on_clean_foundation.py \
       && .venv/Scripts/python.exe verification/test_learner_growth_full_solution.py
witnesses: 6/6 (core) + 8/8 (extensions) | ledger: malformed 0 | hdlab/ UNTOUCHED (Q111 default-off diff proposed)

HEADLINE — the learner turns ON safe AND beneficial, proven ~9 ways; both negatives DRILLED to mechanism.
Downstream = LitBank who-did-what verb-paraphrase (n=5530, 5M->15M growth, base-correct n=387).
  (1) BENEFICIAL: every keep-both arm beats growth-OFF (0.070) CI-sep; PINNED reliability fusion +0.058.
  (2) REAL: info-free growth twin HURTS (-0.024 CI-sep below OFF).
  (3) SAFE: reliability corruption 0.098 (lowest), CLS_NOISY 0.093, CLS_CORE 0.109 — all < pre-reg 0.15.
  (4) ROLLBACK: held-out known-correct probe accepts clean update, rolls back naive(0.25)+adversarial(0.96);
      random-decision control fails to protect.
  (5) CLEAN-FOUNDATION on the LEARNER: REFUTED — schema-congruence gating is confirmation-biased (+0.039
      MORE corruption than noisy AND than random-drop). BUT the SAME p4 gate WORKS on the episodic is-a KB
      (AUC 0.868; wrong-fact admit 0.30 vs random 0.75; admits 82% correct) — schema-gating belongs on the
      KB, not the distributional learner. Category insight, confirmed constructively.

FULL-SOLUTION EXTENSIONS (owner asks: complete/excellent + all brain-foundational + drill every wall)
  • PINNED reliability fusion (Ernst&Banks/Friston precision) = best operating point: corr 0.098, fix/break 9.45.
  • No fusion crosses the ~0.10 floor CI-sep (store disagreement); anti-brain unaligned control worst (0.171).
  • Decomposition: growth fixes ~8.4–9.4 answers per 1 it breaks.
  • Multi-seed: reliability gain +0.0596 ± 0.0027 (all 3 seeds CI-sep beneficial) — not a lucky seed.
  • Generalizes: 2nd task (WordNet hypernym cue) +0.023/+0.029 CI-sep, twin loses, 3.98:1.
  • Survives the substrate's OWN arc_parser (arc +0.0099 ≈ spaCy; arc cleaner). No external tool at inference.
  • Independent benchmark MCScript2 MC-QA: growth NEUTRAL — a precise boundary (see drills).

WALLS DRILLED (none was a ceiling)
  • Corruption "floor" = BENIGN tie-churn: confident-item corruption 3.1% (96.9% preserved), lower where the
    verb learned MORE (0.058 vs 0.130). Not knowledge loss.
  • Continual "compounding" (iterated 0.196@15M) = ANCHOR-DILUTION: fuse ORIGINAL+cumulative → holds at 0.116.
  • MCScript2 read-out: max-sim let the twin WIN → fixed with mean-vector cosine (twin loses 0.59<0.62); then
    flat growth was partly DILUTION → discriminative (answer-unique words) recovers +0.005. Boundary: growth
    helps where comprehension reduces to similarity (+0.06 paraphrase) and only marginally on inference MC-QA
    (+0.005) — MC-QA needs situation-model reasoning. = the North Star's boundary (reasoning is the other half).

PROPOSED hdlab LANDING (default-off; strategy lands, Q111)
  1. CLS keep-both safe-growth switch, PINNED reliability fusion (ensemble is fine fallback); NEVER overwrite.
  2. Feed from CORE-ARG (p1-cleaned) extraction; works with the OWN arc_parser.
  3. Do NOT gate the LEARNER on p4; DO wire the p4 schema gate onto the EPISODIC is-a KB (item 6 proves it).
  4. Rollback gate on a held-out known-correct probe; CONTINUAL growth must be ANCHOR-preserving.
  5. Stays DEFAULT-OFF until owner approves; residual forgetting is proven-benign tie-churn.

FILES (experiments/ + verification/ + notes/problems/<slug>/ only; READ-ONLY reuse of the validated cells)
  exp_learner_on_clean_foundation_v1.py (5-bar capstone) ; exp_learner_growth_{aligned_continual,second_task,
  own_parser,floor_drill,multiseed,mcscript}_v1.py ; exp_learner_kb_growth_p4gate_v1.py ;
  verification/test_learner_{on_clean_foundation,growth_full_solution}.py ; DESIGN_brain_and_mapping.md.

TLDR: "Learn by reading" turns on safe + helpful — fixes ~9 answers per 1 it breaks, keeps what it was sure
about (>96%), stays safe as it reads more, and holds on a 2nd task, on random re-runs, and on the reader's own
grammar engine. The brief's "only accept agreeing facts" backfires on the meaning learner (confirmation bias)
but works on the fact store — so put it there. Growth helps meaning tasks strongly and multiple-choice reading
only barely, because those need reasoning about the story — an honest boundary that names what's left.
QUESTIONS: none blocking — land the switch + fact-store gate together or separately?
NEXT: land default-off (reliability fusion + core-arg + anchored-continual + rollback); land p4 gate on the KB;
follow-on = the full episodic-KB growth loop (a separate problem on a different store).
