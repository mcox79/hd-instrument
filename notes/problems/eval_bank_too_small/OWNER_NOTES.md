---
owner_verdict: DONE
---

eval_bank_too_small — COMPLETE. Built a new goal-outcome test bank (goal_bearing_modern_eval_v2): 166 questions, 124 scored — 3.4× the old bank, and unlike the old one both cheats are dead: a passage-length ruler and a "not"-counter now score at chance instead of the 81% they used to fake. Every passage is verbatim real book text (machine-checked against the source), and every answer was set by reading-comprehension judgment only, never by the system under test. Fairness reported honestly (guessing the protagonist still scores ~0.76; 9 questions beat every shortcut). Scope: this delivers a trustworthy measuring instrument only — it does not itself make the system better at the task; the brain-foundational fix that uses this bank (Phase B) is authorized and now unblocked. Files: experiments/data/goal_bearing_modern_eval_v2.jsonl (+ baselines); solution logged in notes/problems/eval_bank_too_small/SOLVED.md.
