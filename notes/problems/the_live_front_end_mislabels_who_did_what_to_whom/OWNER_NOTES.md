---
owner_verdict: DONE
---

=====================================================================================
SOLVER SUBMISSION — the_live_front_end_mislabels_who_did_what_to_whom  (STATUS: PARTIAL)
Session: solver (opus 4.8). hdlab/ UNTOUCHED (proposed diff only; board Q111).
Reverify (scaffold-free, lands nothing):
  .venv/Scripts/python.exe verification/test_frontend_role_who_did_what.py     -> 6/6 PASS
Ledger: python tools/problem_ledger.py --check -> 0 malformed. AWAITING owner_verdict: DONE.
=====================================================================================

THE BAR (from PROBLEM.md §7): the improved front-end must beat (a) the live position baseline AND
(b) the majority floor, CI-separated end-to-end, info-free twin LOSING, per-cue ablation, on BOTH
McGuffey + QA-SRL. Decisive either way (clear the floor -> wire it; tie it -> rigorous negative that
localises the residual).

ONE-LINE VERDICT. The wall is real and a brain-faithful fix recovers most of it (live end-to-end
0.48 -> 0.75, CI-separated over the live baseline). But the fix is NOT the brief's proposed one, and
TWO of the brief's premises are REFUTED on disk. It TIES (does not clear) the agent-saturated
plain-accuracy floor -> the brief's rigorous-negative branch, residual precisely localised.

#####################################################################################
CORE RESULT (5 experiments, 6 scaffold-free witnesses)
#####################################################################################

- THE WALL (reproduced): live positional front-end end-to-end 0.483 [0.410,0.556] on the 57-passage /
  178-query McGuffey entity-role gold, BELOW the trivial "always-agent" majority floor 0.781
  [0.719,0.843]; errors MISASSIGNMENT-dominant (role-label 86 / entity 50 / miss 30) + 104 out-of-scope
  gold roles the agent/patient front-end structurally cannot emit.

- PREMISE 1 REFUTED — "just wire the existing learned organ": naive wiring scores 0.385 end-to-end,
  WORSE than the live baseline. Diagnosed on disk: (i) CandidateGenerator OVER-GENERATES (mean 9.96
  candidate arg-pairs/clause, incl. quote-internal words) -> it labels every nominal, not the core
  mentions; (ii) NO QUOTATIVE CUE -> every `said Fred` labels the speaker PATIENT.

- THE FIX (fair + brain-faithful, passage-level 6-fold CV, held-out): keep the organ's graded
  Competition-Model perceptron, add the two cues the BRAIN uses that it lacked, as graded features:
  core-mention selection + QUOTE EXCLUSION + a SPEECH-VERB/quotative verb-class cue.
  -> AUG = 0.747 [0.680,0.809], hw=0.065, CI-separated over the live positional baseline (0.483).
  Role-balanced (macro) accuracy 0.191 > majority-macro 0.125. Speech cue is the load-bearing lever
  (patient recall 0.14 -> 0.50). Thematic-fit does NOT transfer to archaic McGuffey.
  -> TIES the plain-accuracy majority floor (0.781): the population is 78% "agent" and 16/178 queries
  need roles the organ can't emit, so plain accuracy is near-unbeatable. RIGOROUS-NEGATIVE branch.

- PREMISE 2 REFUTED — "fix the animacy-dominance with thematic-fit": on 32,419 QA-SRL gold-span
  entries, WORD ORDER (+voice) dominates AGENT/PATIENT assignment and resolves the two-animate
  reversible cases (0.918 [0.895,0.940]) where ANIMACY is exactly chance (0.500). Adding THEMATIC-FIT
  is net-negative on every population. Pure thematic-fit (order removed) = 0.585 on two-animate: a REAL
  but LOW-VALIDITY cue (CI excludes chance) utterly DOMINATED by word order. The revalidation's
  "animacy-dominance HARD_FAIL" is partly an artifact of a FIXED positional strawman baseline (0.48);
  a LEARNED order+voice model does 0.93. The organ's real defect is a TRAINING-DISTRIBUTION confound
  (McGuffey-canonical confounds animacy with role), not thematic-fit.

CONTROLS: majority floor (per population); live positional baseline; info-free twins (role-permuted
0.663; scrambled-centroid; shuffled-validity); naive-wiring negative control 0.385; per-cue ablation
(speech ON/OFF +0.017; thematic-fit ON/OFF net-negative); ANIMACY_ONLY=chance on two-animate; null
p95 reported. Both populations, floors recomputed on each.

#####################################################################################
DEEPENING DRILL (owner's 60-min cron, 4 passes — each deepened OR self-corrected an overclaim)
#####################################################################################
1. Thematic-fit "noise" -> corrected to REAL but low-validity dominated cue (matches Dowty 1991
   indeterminacy prediction + Kako 2006 + Cai/Zhao/Pickering 2022; lit-VET'd).
2. Speech-verb HAND-LIST -> a real SEMANTIC class, derivable from WordNet verb.communication AND
   distributionally LEARNABLE from quote co-occurrence (say: 260/302 uses adjacent to a quote). Also
   found my hand list carried NOISE (go/went/began are not communication verbs).
3. Single-random-draw control was UNDERPOWERED (a lucky draw hit 0.895) -> replaced with a proper NULL
   DISTRIBUTION (40 draws). Honest result: the speech-cue benefit beats the null p95 on the ROLE-
   BALANCED metric (learned 0.215 vs null 0.173) but NOT on agent-saturated plain accuracy.
4. PERCEPTRON vs the brain's DYNAMICS (Spivey-Knowlton normalized recurrence): built + tested. It is
   accuracy-equivalent (0.852) and strictly more brain-faithful as a MECHANISM — but its distinctive
   settling-time DIFFICULTY signal is NOT cleanly validated here (right direction, not CI-separated,
   shuffled-validity twin not defeated). Do NOT claim a clean difficulty signal; validating it needs
   human reading-time data.
=> CONVERGED for natural-corpus role labeling (brain's mechanism identified/replicated/tested);
   remaining gains need new DATA, not new mechanisms.

#####################################################################################
PROPOSED hdlab CHANGE (NOT landed — strategy re-verifies + lands)
#####################################################################################
In hdlab/situation_reader.py + hdlab/thematic_role_labeler.py, behind a default-OFF flag (identical
downstream; only the assigner changes):
1. _pick_role_mentions: add QUOTE EXCLUSION (drop quoted-span nominals; only non-quoted verbs are
   matrix predicates). Biggest single lever.
2. Add a SPEECH-VERB class + quotative frame — DERIVE THE CLASS FROM WordNet verb.communication
   (NOT a hand list; recovers the benefit, drops the hand-list noise); expose as a role_feats cue,
   never a hard override.
3. Wire the learned perceptron over the SELECTED core mentions only (<=2/predicate), not all
   CandidateGenerator candidates. Retrain on a distribution where word order competes with animacy
   (real passages incl. quotative) so it stops being animacy-dominant.
4. Do NOT add a thematic-fit / selectional-preference cue (measured net-negative on McGuffey + 32K
   QA-SRL — English is word-order dominant). Keep the predictive reader's selectional-preference
   machinery for its anticipation/surprisal job.
5. Normalized recurrence is OPTIONAL — adopt only if the settling-based difficulty signal is wired as
   shared infrastructure with the N400 monitor + predictive-reader surprisal.
Expected: live end-to-end 0.48 -> ~0.75 on McGuffey; ~0.93 role labeling on modern prose vs 0.50 floor.
Will NOT clear the agent-saturated plain-accuracy floor on the current gold — honest capability claim
is "recovers the front-end wall + resolves reversible roles via word order," pending a role-balanced
reading gold.

#####################################################################################
AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, thematic-role entry)
#####################################################################################
- WORD ORDER (+verb-class/quotative) dominates English who-did-what: PINNED (MacWhinney/Bates/Kliegl
  1984 cue-validity). Thematic-fit = REAL but LOW-VALIDITY, correctly dominated (Dowty/Kako/Cai) —
  TESTED, not a role-labeling lever for English.
- The organ's "animacy-dominance HARD_FAIL" is partly a fixed-strawman-baseline artifact; the true
  defect is a training-distribution confound.
- Speech-verb cue = a real semantic class, brain-faithfully LEARNABLE from quote co-occurrence (small,
  role-balanced-specific effect, null-controlled). Missing pieces to wire the organ: core-mention
  selection, quote exclusion, speech-verb/quotative frames.
- Cue-integration MECHANISM: normalized-recurrence dynamics (Spivey-Knowlton) is more brain-faithful
  than the perceptron at EQUAL accuracy; its difficulty-signal payoff is unvalidated here. Computational
  model + neural locus (AG thematic role; IFG-vs-temporal primacy) are CONTESTED — honestly labelled
  OUR-INVENTION-UNDER-TEST.

#####################################################################################
PROXIMITY-MACHINERY AUDIT (Q4) + NEXT-PROBLEM RECOMMENDATION
#####################################################################################
- BIGGEST remaining fidelity gap is NOT in the role assigner: the PARSER FRONT-END
  (candidate_generator.py = a UD-EWT statistical POS tagger + arc parser). The brain builds structure
  INCREMENTALLY/predictively, not via a batch dependency parse. RECOMMEND opening its OWN problem
  ("the argument parser is batch/statistical where the brain is incremental/predictive"), composing
  with the predictive-reader + relcl sessions. Highest-value front-end fidelity target.
- Verb FRAME TABLE is hand-authored -> derivable from VerbNet/WordNet or distributional learning
  (as the speech subclass was). Clean fidelity win, SMALL payoff (richer roles are rare in the gold).
- RELCL filler-gap composition UNTESTED — the one construction where word order genuinely fails
  (reversible object-relatives); narrow real accuracy gap, depends on the relcl organ.
- Animacy lexicon / lemmatizer / quote-mask: acceptable stand-ins (quote-mask is CORRECT for reading).

#####################################################################################
FILES
#####################################################################################
experiments/exp_frontend_learned_role_wire_v1.py (naive-wiring negative control);
exp_frontend_role_augmented_cv_v1.py (the fix, CV, per-cue ablation, macro);
exp_frontend_thematic_fit_qasrl_v1.py (word-order-dominance + thematic-fit refutation, +THEMFIT_PURE);
exp_frontend_verbclass_source_v1.py (WordNet + learned speech-verb class, null-controlled);
exp_frontend_normalized_recurrence_v1.py (Q2 mechanism);
verification/test_frontend_role_who_did_what.py (6 witnesses). hdlab/ UNTOUCHED.

TLDR (plain language). The reader's first job — who did what to whom — was badly broken, and we thought
the fix was to switch on a smarter module we'd already built and give it a sense of which nouns do which
actions. Both ideas were wrong when measured: the old module made things worse (it reads the words inside
quotation marks and gets "said Fred" backwards), and the "which nouns fit which actions" idea added no
value. What actually fixes it is simpler and truer to the brain: ignore the words inside quotes, know that
verbs like "said" put the speaker after them, and lean on plain word order — which in English is the
strongest clue by far. That more than doubles the score (48% -> 75%). It still can't beat "just guess the
most common answer" on this test set, because 78% of the answers there are the same role — so we've
recovered the broken step and pinned what's left, but not beaten the trivial guesser on this saturated set.
The deepest remaining brain-fidelity gap is a different component (the sentence parser), which deserves
its own problem.

QUESTIONS: none.

NEXT STEPS: (1) land the proposed diff (quote exclusion + WordNet/learned speech-verb class + core-
mention-selected learned labeling; NO thematic-fit); (2) open a new problem on the incremental/predictive
PARSER front-end (highest-value fidelity target); (3) build a role-BALANCED reading gold so a plain-
accuracy floor-clearing lift is measurable; (4) fix the organ's training-distribution confound
(retrain where word order competes with animacy).
=====================================================================================
