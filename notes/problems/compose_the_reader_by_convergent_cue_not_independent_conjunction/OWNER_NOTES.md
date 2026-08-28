---
owner_verdict: DONE
---

SUBMISSION — SOLVER RESULT: compose_the_reader_by_convergent_cue_not_independent_conjunction
STATUS: SOLVED | witness 7/7 PASS | ledger malformed:0 | hdlab UNTOUCHED (Q111 — you land) 
INTEGRATE ONLY on owner_verdict: DONE in notes/problems/<slug>/OWNER_NOTES.md.
REVERIFY: .venv/Scripts/python.exe verification/test_convergent_cue_composed_reader.py  (scaffold-free, cached records, fast)

ONE-LINE: Replaced STEP-18's independent post-hoc AND with the brain's actual retrieval rule — CONVERGENT-CUE
pattern completion = the reliability-weighted PRODUCT of the episodic + meaning posteriors (one content-addressable
read jointly driven by both cues). It beats the strongest floor CI-separated, every control passes, and a drill
shows the rule is AT its ceiling — the remaining headroom is the dense episodic store (p2), not the combination.

THE BAR (PROBLEM.md §7): beat the independent-AND (0.119) CI-sep on the SAME harness; mechanism = convergent-cue
(one read, top-down bias) NOT a re-weighted AND; DOUBLE DISSOCIATION preserved (fused-pool refuted); info-free twin
loses; gain LOCALISED to the predicted subset. A root-caused negative is also a PASS.

MECHANISM (all components PINNED): argmax_c [ log softmax(epi_raw/tau_e)(c) + w·log softmax(sem_raw/tau_s)(c) ],
epi = LANDED per-entity FHRR register cleanup scores (bottom-up), sem = conceptual_meaning.similarity(q,c)
(top-down ATL). = CA3 pattern completion (Norman & O'Reilly 2003) + Bayesian cue combination (Ernst-Banks 2002 /
Ma-Pouget PPC 2006). tau = gold-blind cue scales (static); w = reliability ratio CALIBRATED on train, evaluated
strictly HELD-OUT (=12 on the current dense store). Two SEPARATE pools combined at read — never fused.

RESULT (60 docs, n=3681 — the exact STEP-18 population):
  meaning-solo (STRONGEST floor)   0.6998 [0.6791,0.7222]
  CONVERGENT (headline, held-out)  0.7438 [0.7246,0.7626]  → +0.044 CI[0.031,0.058] hw 0.014
  (vs independent-AND 0.1282: +0.6156 ; vs entity-solo 0.1785: +0.5653). Robust across 3 forms
  (log-Bayes 0.744, z-norm-λ 0.750, activation-space top-down reinstatement 0.723).
CONTROLS (each excludes something):
  • shuffled-MEANING twin 0.041 → collapses (gain is top-down semantic, not a free parameter).
  • shuffled-EPISODIC twin 0.667 → FALLS BELOW meaning-solo (−0.033 CI-sep); HEADLINE beats it +0.077 → the win
    over meaning-solo needs the REAL episodic evidence = genuine convergence, not meaning-solo relabeled.
  • FUSED one-undifferentiated-pool 0.360 → loses +0.384; its lesion read 0.134 < separated entity-solo 0.178.
  • DOUBLE DISSOCIATION preserved: lesion meaning → entity-solo 0.178 (spared); lesion entity → meaning-solo 0.700.
  • LOCALISED: keeps 97.6% of meaning-solo-RIGHT, rescues 20.5% of meaning-solo-WRONG.
  • equal-weight product (w=1) 0.639 → BELOW meaning-solo → reliability weighting is load-bearing (Ernst-Banks).

DISK-OUTRANKS-BRIEF (flagged, not silent): the brief's named baseline (independent-AND 0.119/0.128) is a STRAW
floor — LOWER than either system alone (entity 0.178, meaning 0.700). I re-aimed at the true strongest floor
(meaning-solo 0.70) and beat THAT. Do NOT quote the beat over 0.119 as the achievement.

FURTHER-OPTIMISATION DRILL (owner "keep pushing"): the RULE is AT CEILING — convergent 0.744 is only +0.006 below
the argmax-union oracle 0.750 (NOT_SEP); an explicit per-query precision-weighted form HURTS (0.677) → the log-Bayes
product already does optimal per-observation weighting. On the hard subset convergent (0.205) EXCEEDS the episodic
argmax rate (0.167) by integrating GRADED evidence = the pattern-completion signature. The gain rises monotonically
with episodic reliability (quartiles +0.00/+0.01/+0.05/+0.12) → validates the weighting AND the compounding
prediction: p2's sparse store raises episodic reliability → the gain grows. WALL = the dense episodic store, NOT the rule.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT §2b): the "composition-by-independent-conjunction" deviation is now TESTED +
RESOLVED at the READ side (convergent-cue validated, fused refuted, dissociation preserved). New PINNED/INVENTED line:
combination rule (product of posteriors) = PINNED; the reliability weight being CALIBRATED (not emergent, because our
two cue codes aren't one PPC population) = OUR-INVENTION-UNDER-TEST. Forward hook: convergent + p2 should compound.

PROPOSED hdlab (you land; I did NOT write hdlab/):
  1. New hdlab/convergent_cue_reader.py: argmax_c [ log softmax(cleanup_scores/tau_e) + w·log softmax(sem/tau_s) ]
     over the LANDED situation_model_accumulate decode + conceptual_meaning.similarity. tau_e/tau_s/w = OFFLINE
     static assets (admissible); graceful degradation free (no register → meaning-solo; no cue → entity-solo).
  2. Wire it in for STEP-18's independent-AND composition; keep the two organs + their SEPARATE stores unchanged
     (the dissociation gate forbids fusing them).
  3. Re-run + re-calibrate w on p2's sparse DG+CA3 store when it lands (one backend swap; predicted w→1, bigger gain).
  4. Do NOT: fuse into one pool (loses + kills the dissociation); use the equal-weight product (below meaning-solo);
     build the REMERGE recurrent loop for this co-referential task (single-shot is the settled state).

DO NOT QUOTE: the beat over 0.119 as the headline (it's a straw floor — the claim is the CI-sep beat over
meaning-solo 0.70 + controls); the absolute convergent number as a general capability (WordNet-paraphrase
circularity in the absolute, identical across arms so the delta is clean); "reliability weighting is emergent" (it's
CALIBRATED here — heterogeneous cue codes).

FILES: experiments/exp_convergent_cue_composed_reader_v1.py (deployable); exp_convergent_cue_probe_v1.py;
exp_convergent_cue_reliability_drill_v1.py; verification/test_convergent_cue_composed_reader.py;
notes/problems/<slug>/SOLVED.md; data/exp_convergent_cue_composed_reader_v1/{metrics.json,records_60.json,run60.log}.
NO hdlab/.

TLDR (plain language): To answer "what did she chase?" the reader must track who "she" is (memory) AND know the
paraphrase (meaning). The old way ran the two separately and demanded both be right — which scores worse than either
alone. The brain feeds both clues into ONE memory lookup where the meaning clue steers the memory read, each clue
counting more when it's more reliable. I built exactly that: it beats the best single skill (~70%→~74%, a real
CI-separated gain), and every check that it's the RIGHT mechanism passes (scramble the meaning clue → collapses;
scramble the memory clue → the extra gain vanishes; merge the two memories into one pool → worse and loses graceful
failure). A drill proved the combination rule is already at its ceiling; the modest size is because the memory store
it reads is still the weak "dense" one — the same mechanism should gain MORE once the sharper "sparse" store (p2) lands.

QUESTIONS: none blocking. One judgment call made visible: I re-aimed the bar from the brief's straw baseline (0.13)
to the true strongest floor (meaning-solo 0.70) and beat that.
NEXT STEPS: (1) land convergent_cue_reader in place of the AND; (2) re-run + re-calibrate w on p2's sparse store;
(3) a non-WordNet paraphrase gold to remove the mild circularity from the absolute numbers.
