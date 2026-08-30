---
owner_verdict: DONE
---

════════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — the_force_dynamic_reader_needs_a_literal_sense_and_attachment_gate    STATUS: SOLVED (WIP → owner DONE)
hdlab/ UNTOUCHED (proposed _read_causation gate diff, Q111). UNBLOCKS the causation live-wiring.
REVERIFY (one command reproduces every headline claim):
  .venv/Scripts/python.exe verification/test_literalness_gate_organ.py                    -> 7/7
  .venv/Scripts/python.exe tools/problem_ledger.py --check                                -> malformed/incomplete: 0
════════════════════════════════════════════════════════════════════════════════════════════════════
WHAT WAS BUILT: a glass-box FORCE-AFFORDANCE gate that lets the force-dynamic (sensorimotor) reader ENGAGE
  only on LITERAL physical events and ABSTAIN otherwise. REUSES (does not rebuild) the WSD/idiom organs.
  Veto architecture (constraint satisfaction; Bergen/Barsalou grounded simulation is attempted by default,
  blocked on a detected violation): ABSTAIN if (1) an OPAQUE VOBJ idiom fires (make sense / take place),
  (2) a force ROLE is KNOWN-ABSTRACT (selectional violation / N400) over antagonist + agonist + the Talmy
  motion-GROUND, (3) attachment is wrong. Emits a THREE-WAY label (ENGAGE_PHYSICAL / FORCE_NONPHYSICAL /
  ABSTAIN) so social-force metaphor is tagged, not discarded. No external LLM (spaCy + WordNet + FrameNet).

RESULT (150 hand-adjudicated MODERN clauses, UD-EWT web + MCScript2 narrative, base rate 0.560):
  * FIRE-PRECISION 0.716 [0.631,0.800] vs the strongest real floor FIRE_ANY (fire on any physical-verb
    lemma) 0.560: paired +0.156 [0.102,0.216] CI-SEPARATED. null p95 0.596. RECALL 0.929 [0.871,0.978].
  * DOWNSTREAM / END-TO-END (wired in front of the actual typer+estimator): the gate cuts the reader's
    false-physical-type rate on non-literal clauses 0.89 -> 0.41 (54% fewer figurative mislabels) while
    keeping literal coverage 0.86; on the brief's OWN examples 9/10 ("news broke"->ABSTAIN, "branch broke"
    ->CAUSE, "deal fell through"->ABSTAIN, "crushed by criticism"->ABSTAIN; miss = "opened up to him").
  * GENERALIZATION, held-out UNSEEN genre (RACE essay prose, n=130, base 0.292, ZERO params re-tuned):
    +0.086 [0.028,0.148] CI-SEPARATED (twin loses). Structural: the gate has NO fit parameters.
FLOORS: FIRE_ANY = base rate 0.560 (beaten CI-sep, paired). Un-gated patient-tendency estimator 0.500
  (fires 4x, noisy). Label-permutation null p95 0.596. All beaten.
CONTROLS: info-free TWIN (shuffled sense + permuted concreteness, matched fire rate) 0.523 LOSES CI-sep
  (+0.192 [0.118,0.268]); PER-COMPONENT ablation (concreteness = workhorse 0.684; +Talmy Ground +0.061;
  +attachment +0.032; WSD sense-posterior veto net-NEGATIVE -> left OFF); THRESHOLD SWEEP identical over
  c_min 0.15..0.50 (robust, not a knife-edge); POSITIVE CONTROL 10 literal-vs-figurative minimal pairs
  0.80 vs 0.50; PR-curve Pareto-DOMINATES the base-rate floor at every recall (avg precision 0.784 vs 0.560);
  SECOND INDEPENDENT (blind) ADJUDICATOR: Cohen kappa 0.932 (primary) / 0.982 (held-out), gate edge holds
  on their labels (0.752 vs 0.593; 0.380 vs 0.300) -> not a single-annotator artifact.
BRAIN-FOUNDATIONAL (drill: research_literalness_gating_2026-08-30.md): grounded simulation is GRADED not
  gated (LIT>MET>IDIOM>ABS; Raposo/Desai) -> target re-cut to CONVENTIONAL-figurative+idiom (the OFF bucket).
  PINNED: selectional violation -> figurative (Wilks/N400); stored-unit idiom (Giora); Talmy motion Ground.
  KEY FINDING (matches parent WSD): the compositional WSD frame-posterior is net-HARMFUL as a literalness
  cue (taxonomy fallibility); the reliable levers are role-concreteness + the VOBJ stored-unit idiom.
  Generalizes the brain's way: WordNet IS-A on the roles (novel nouns: boulder/kettle engage, nostalgia/
  bureaucracy veto), morphy lemmatization, top-5 polysemy window, DERIVED verb set. AUDIT UPDATE folded.
HONEST LIMITS (withdraw first): recall 0.929 is a small CI-separated drop from the trivial always-fire 1.0
  (unavoidable for any abstaining gate; the 6 abstained literals are WordNet-polysemy borderline). Effect is
  modest and SMALLER on essay prose (concrete-role conventional metaphor is denser there). The residual
  false-engages are concrete-role figuratives (relocation, social force, "opened up") = the two next problems.
>> NEXT STEP (strategy files under Q113; NOT this solver): (1) land the gate into _read_causation + proceed
  with the causation live-wiring (unblocked); (2) a SOCIAL/INSTITUTIONAL-FORCE reader (the FORCE_NONPHYSICAL
  bin has no consumer; leading uncaught class on essay prose); (3) a CONTEXT-WSD / conventional-metaphor
  inventory for concrete-role figuratives (caps essay-prose generalization). These are new organs.
FILES: experiments/{_literalness_gate, _literalness_data, _literalness_gold, _dump_literalness_candidates,
  _dump_for_second_adjudicator, exp_literalness_gate_v1, exp_literalness_gate_heldout_race_v1,
  exp_literalness_gate_endtoend_v1, exp_literalness_gate_prcurve_v1, exp_literalness_gate_adjudicator_agreement_v1}.py;
  verification/test_literalness_gate_organ.py (7/7); SOLVED.md + research note. hdlab/ UNTOUCHED.
TLDR: the physics part of the reader couldn't tell "the branch broke" (real) from "the news broke" (an
  expression) — it would run its physics on both. I built the brain's off-switch: run the physics only when
  the things involved are actually physical (you can't crush an abstract idea), checking the pusher, the
  pushed, and where it moves to, plus a small dictionary of fixed figures of speech. It roughly HALVES the
  reader's figurative mistakes while keeping 93% of the real physical cases, beats chance at every setting,
  generalizes to an unseen essay-style test, and a second independent labeler agrees ~97% of the time. The
  one thing left is telling apart figures of speech that use concrete words ("she opened up", "run the
  company") — which needs word-sense understanding, the honest next problem. QUESTIONS: none.
════════════════════════════════════════════════════════════════════════════════════════════════════
