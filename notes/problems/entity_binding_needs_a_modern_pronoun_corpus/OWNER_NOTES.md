---
owner_verdict: DONE
---

═══════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — entity_binding_needs_a_modern_pronoun_corpus   (STATUS: SOLVED)
Session: solver (opus 4.8). hdlab/ UNTOUCHED throughout (proposed diff only; board Q111).
AWAITING owner_verdict: DONE in OWNER_NOTES.md before integration.

REVERIFY (scaffold-free, lands nothing):
  .venv/Scripts/python.exe verification/test_gap_pronoun_binding.py   ->  6/6 PASS
Ledger: python tools/problem_ledger.py --check  ->  malformed/incomplete: 0 (exit 1 = unintegrated, expected).
═══════════════════════════════════════════════════════════════════════════════════════

THE BAR (verbatim, PROBLEM.md §7): "The salience binder must resolve pronouns/anaphora to the correct
entity CI-separated over its UPPER bound vs (a) a string-identity-only baseline and (b) the strongest
simple floor (most-recent-mention), with an info-free twin (shuffled salience / random antecedent)
LOSING CI-separated. Report CI half-width + null p95. Ablate recency vs grammatical-prominence vs
agreement-filter. AND/OR: linking coref threads improves DOWNSTREAM entity prediction over
string-identity CI-separated."

ONE-LINE VERDICT. The bar is MET, and the mechanism is now genuinely brain-faithful: I (1) put a modern
human-labeled pronoun corpus on disk and showed a salience binder beats the named floors CI-separated
with the info-free twin losing; (2) found via five brain-fidelity drills that the ALGORITHM should be
ACT-R base-level activation (the brain's declarative-memory equation), which beats the live organ's
salience formula by +21 points on running narrative; (3) returned a rigorous NEGATIVE on the
implicit-causality lever; (4) closed the downstream clause with an honest both-sided result.

#####################################################################################
1. THE BAR TASK — salience binder on GAP (Wikipedia, same-gender ambiguous pronouns)
#####################################################################################
Corpus: GAP (Webster et al. 2018), 4,454 human-labeled instances. Same-gender candidates by
construction => agreement filter is INERT => the corpus isolates pure salience (the PINNED claim).
Parsed with spaCy dependency parse only (NOT a coref model; gold is human => no circularity).

GAP test, n=1773 resolvable, 2-way A/B, chance 0.5:
  RANDOM 0.504 | STRING_IDENTITY 0.508 | RECENCY/most-recent 0.514 (AT CHANCE) | FREQUENCY 0.539
  | PARALLELISM 0.616 | GRAMMATICAL prominence 0.694 | SALIENCE_PRIOR (binder) 0.699 [0.677,0.719]
  | SALIENCE_SHUF twin 0.490 (null p95 upper 0.513)
- Bar (a): binder > string-identity +0.191 CI-separated.  MET.
- Bar (b): binder > most-recent-mention +0.184 CI-separated.  MET.
- Info-free twin LOSES: SALIENCE_over_twin +0.181 [0.151, 0.210] ABOVE (hw 0.020).  MET.
- ABLATION (leave-one-cue-out marginal): role +0.0344 CI-separated (LOAD-BEARING); first-mention +0.016
  (not sep); parallelism +0.009 (subsumed by role); RECENCY +0.0000 (INERT); frequency +0.0000 (inert);
  agreement inert BY CONSTRUCTION. => salience = grammatical prominence; recency is at chance (Ariel).

#####################################################################################
2. THE DEEPER, MORE BRAIN-FAITHFUL MECHANISM — ACT-R base-level activation (LitBank)
#####################################################################################
Fidelity drill (notes/research_pronoun_activation_dynamics_2026-08-27.md): iterative SETTLING is
REFUTED for the pick (3 converging sources: Li et al. 2020 fMRI/MEG one-shot best-fit; Chow/Lewis/
Phillips 2014; on-disk LV05 HARD_FAIL). The one faithful FORM fix: the live organ's salience =
count + beta*exp(-lambda*dist) provably (T2c) can never let recency overturn a 1-mention count lead.
The brain's actual equation is a real trade-off:  B_i = ln( sum_k w_role(k) * dt_k^(-d) ).
GAP snippets are too short to test it (why the GAP ablation found recency at +0.0000). Acquired LitBank
(100 novel excerpts, CC-BY; 9,128 pronoun instances) -- running narrative.

Held-out (test half, n=3654, ~24-way choice, chance 0.042; decay d*=2.0 chosen on train half):
  RANDOM 0.045 | ROLE_ALONE 0.228 (COLLAPSES) | FREQUENCY 0.614 | ACTR_NO_DECAY 0.611
  | CURRENT_FORMULA 0.623 | MOST_RECENT 0.658 | ACTR_DECAY 0.837 [0.825, 0.849]
- ACT-R > live organ formula +0.213 (hw 0.017) | > pure recency +0.178 | > no-decay twin +0.226. All CI-sep.
- REGIME FLIP (Competition Model, the unifying insight): grammatical role DOMINATES on GAP (short,
  2-way) but COLLAPSES on running narrative (0.228 -- everyone's been a subject); recency is inert on
  GAP but dominant on LitBank. The ONE ACT-R scalar wins in BOTH regimes -- that is what marks it as the
  brain-faithful mechanism, not a corpus-specific cue.

#####################################################################################
3. RIGOROUS NEGATIVE — implicit-causality / coherence likelihood does NOT lift GAP
#####################################################################################
Built the PINNED prior x likelihood second stage (Kehler & Rohde 2013) from the Ferstl (2011) 305-verb
human IC-norm lexicon. On GAP test: IC fires on only ~15% of instances; adding it is negligible on the
full set (test +0.006, dev -0.008 -- FLIPS SIGN, so it does not replicate); where it fires it does NOT
beat its own lexicon-scramble twin CI-separated. Localized: GAP's residual to human ~96.6% is genuine
world knowledge (neural systems reach ~92% only via massive pretraining, unavailable to a glass-box
no-LLM substrate), and even the brain's residual is a hippocampal ACTIVATION bias (Dijksterhuis et al.
2024, Science: a pronoun reinstates the more-activated concept cell). NOT a binding lever on Wikipedia
prose; reserve for connective-dense narrative.

#####################################################################################
4. DOWNSTREAM (bar's AND/OR) — honest both-sided, on LitBank (all 100 docs, B-cubed vs gold)
#####################################################################################
- On PRONOUN mentions (B-cubed recall): string-identity 0.095 -> ACT-R binder 0.472, +0.377
  CI-separated [0.352, 0.402]. LARGE -- string-identity orphans every pronoun; the binder recovers ~40%
  of the tracking recall it throws away.
- On the WHOLE mention set (B-cubed F1): 0.495 -> 0.506, +0.011 NOT separated [-0.002, 0.025]. MODEST --
  pronouns are a minority (names dominate, threaded identically), and wrong links cost precision.
=> marginal value of real coref over exact-match: LARGE for pronouns, MODEST whole-document. The caveat
travels.

#####################################################################################
PROPOSED hdlab CHANGE (NOT landed -- strategy re-verifies + lands)
#####################################################################################
In hdlab/coreference_resolver.py + the hdlab/state_of_mind salience formula it imports:
1. REPLACE the pronoun-branch salience score with ACT-R base-level activation
   B_i = ln(sum_k w_role(k) * dt_k^-d)  (dt = sentence-distance; w_role = existing role weights; d ~1.5-2.0).
   Drop-in for salience(); unifies grammatical prominence + recency + frequency; +0.213 over the live
   formula on running narrative. Highest-value change.
2. Do NOT build iterative settling/attractor for the antecedent PICK (refuted, 3 sources) -- standing constraint.
3. Keep the agreement filter as a DISTINCT, LOGGED stage (log "0 eliminated by agreement" so a
   same-gender test can't conflate "did nothing" with "broken").
4. Do NOT add an IC/coherence likelihood for binding on Wikipedia-style prose (measured null).
5. Do NOT use content/cue-based retrieval as the pronoun pick (LV05 HARD_FAIL -0.1348; Jaeger/Engelmann/
   Vasishth 2017: interference signature absent for this dependency). Content retrieval is the PREDICTION channel.
Design note (for land-time, not a blocker): the FHRR-native readout -- activation = magnitude of an
unnormalized, decaying situation-model register (concept-cell-like: identity=direction, activation=
magnitude) -- computes ~the same scalar; adopt it as the register architecture if convenient, it won't
change accuracy.

#####################################################################################
AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, coreference/binding entry)
#####################################################################################
- Reference resolution is SALIENCE-driven; salience = ACT-R base-level ACTIVATION unifying grammatical
  prominence + recency + frequency, and which component dominates is DISCOURSE-STRUCTURE-DEPENDENT
  (Competition Model): role dominates GAP (short 2-way), recency/accumulation dominates LitBank (long
  many-way). B=ln(sum_k w_role*dt^-d) wins both; beats the organ's count+exp formula +0.213. PINNED; d swept.
- Iterative SETTLING/attractor dynamics REFUTED for the pick (Li 2020; Chow/Lewis/Phillips 2014; on-disk
  LV05). Fast, one-shot; only the score's FORM is the lever.
- IC/coherence likelihood: TESTED, null on GAP (~15% coverage, non-replicating, doesn't beat scramble).
- LV05 cue-based activation for antecedent CHOICE: REFUTED (Jaeger/Engelmann/Vasishth 2017 + on-disk).
- New anchors to cite: Dijksterhuis et al. 2024 Science (hippocampal reinstatement = activation bias);
  Lewis & Vasishth 2005 (ACT-R base-level); Kehler & Rohde 2013 (Bayesian prior x likelihood); Ariel
  (recency weakest). Full drills: notes/research_pronoun_anaphora_brain_computation_2026-08-27.md,
  notes/research_pronoun_residual_worldknowledge_brain_drill_2026-08-27.md,
  notes/research_ic_coherence_gap_pronoun_2026-08-27.md,
  notes/research_pronoun_activation_dynamics_2026-08-27.md (written by research helpers this session).

FILES: experiments/exp_gap_features_v1.py, exp_gap_salience_binder_v1.py, exp_gap_salience_prior_v2.py,
exp_gap_ic_coherence_v3.py, exp_litbank_activation_binder_v1.py, exp_litbank_chain_quality_v1.py;
verification/test_gap_pronoun_binding.py (6 witnesses); notes/problems/entity_binding_needs_a_modern_
pronoun_corpus/SOLVED.md; foundation assets: data/gap_coreference/, data/ic_norms/ferstl2011.xlsx,
data/litbank/. hdlab/ UNTOUCHED.

WHAT I'D WITHDRAW FIRST IF WRONG: the within-entity timestamp-shuffle twin is a WEAK control (+0.011;
it preserves each entity's recency profile) -- the load-bearing info-free control is the NO-DECAY twin
(ACT-R > no-decay +0.226). First-mention's marginal value on GAP is not CI-separated. The IC null is
GAP-specific (Wikipedia prose), not a claim IC is useless for binding in connective-dense narrative.
d*=2.0 sits at a plateau (1.5-2.0); the win over the organ formula holds across the whole sweep.

TLDR. The reader's "who does he/she refer to?" step now has real tests on real pronouns. A salience
resolver picks the right person ~70% of the time on hard same-gender Wikipedia cases (vs 50% guessing;
"nearest name" is no better than a coin flip there), and a scrambled version collapses to chance --
driven by grammatical role, NOT recency, which corrects a backwards default in the live reader. Pushing
on brain-faithfulness, the bigger finding is about the FORMULA: the reader scores how "present" each
character is with math that can never let "mentioned more recently" out-vote "mentioned more often" --
backwards from human memory. Swapping in the brain's actual memory-strength equation (fades with time,
builds with each mention, weighted by subjecthood) jumps accuracy from 62% to 84% on full novel excerpts,
and unifies two regimes that each break the single-cue methods. On the payoff: correct pronoun threading
is a big win on the pronouns themselves (recovering 40% of tracking the old method drops) but a modest
one document-wide (pronouns are a minority). The remaining gap to human 96% is world knowledge a
glass-box system without a big language model doesn't have.

QUESTIONS: none.

NEXT STEPS: (1) land the ACT-R activation formula (drop-in salience replacement; +21 pts on running
narrative); do NOT build settling. (2) wire it into the situation-model prediction channel and measure
end-to-end grounded prediction (needs hdlab; LitBank now provides the running-narrative substrate). (3)
do NOT pursue IC for binding on Wikipedia prose. (4) optional: FHRR-native register-magnitude activation
readout, after the base version lands.
═══════════════════════════════════════════════════════════════════════════════════════
