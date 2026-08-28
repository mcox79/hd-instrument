---
owner_verdict: DONE
---

SUBMISSION — the_reading_extractor_may_not_beat_a_two_line_rule
Status: SOLVED. Re-verify (scaffold-free, no landed dir touched):
verification/test_reader_vs_twoline_qasrl_power.py (headline), …test_reader_fillergap_reversible_objrel.py (ceiling), …test_reader_cue_retrieval_interference.py (fidelity). All three green.

The literal problem
The pipeline's first stage reads a sentence and works out who did what to whom (which noun is the verb's patient). It scores ~90% on 100 hand-checked items — but a trivial two-line rule (word order + active/passive voice, all the elaborate filters off) reached 0.83 on the same items, and the elaborate reader beat it by only +0.00 to +0.14, a margin that did not exclude zero. So the elaborate "read the text" machinery may be no better than two lines of code. Prove it earns its keep at power, or replace it.

The bar (verbatim)
"On a held-out … role-assignment set LARGER than n=100, floor recomputed on that population: the elaborate reader must beat the two-line rule (word-order + voice, elaborate filters OFF) CI-separated over its UPPER bound, information-free twin LOSING. HOW WE WOULD KNOW IT FAILED, and this is a full PASS for the brief: it ties or loses the two-line rule at power → the elaborate machinery does not earn its keep, and the recommendation is to REPLACE it and redirect the effort to stage 2."

The instrument
QA-SRL v2 gold — real sentences with published correct patient answers — as the controlled-proxy role-assignment set. 17,330 held-out items (dev+test), scored by span-accuracy (a pick is right if its token lies in the gold patient span). The verb index is anchored from gold, so the tagger's verb errors don't confound the one variable: the patient-selection rule. The elaborate reader (the thematic_role_labeler averaged-perceptron cue-integration — the general machinery the brief names) is trained on the QA-SRL train split; every arm gets the same candidate nominals and the same detected voice.

Four answers (all on disk)
1. The brief, answered → REPLACE. At n=17,330:

arm	span-accuracy	vs two-line rule
TWO_LINE_PRECISE (word order + aux+participle voice)	0.795	+0.029 CI[+0.026,+0.032] ABOVE
TWO_LINE (word order + voice) — baseline	0.766	—
ELABORATE (perceptron cue-integration)	0.751	−0.015 CI[−0.019,−0.011] BELOW
ELAB_ORDER_ONLY / ELAB_ANIMACY_ONLY	0.686 / 0.312	diagnostics
ELAB_SCRAMBLE (weights permuted)	0.530	control
TWIN (random nominal, info-free)	0.287	two-line beats it +0.479
The elaborate machinery loses to the two-line rule, CI-separated → a full PASS in the REPLACE direction. It collapses worst on reversible items (0.684 vs 0.800) — the brain-predicted failure of its animacy-leaning cue for word-order-dominant English (MacWhinney, Bates & Kliegl 1984). The best simple reader is word order + a precise voice cue (auxiliary + participle morphology), which fixes the crude detector's false-passive errors ("Mineralogists are scientists who study minerals" — crude rule sees "are," looks backward, picks who; precise rule keeps it active, picks minerals).

2. But the two-line rule is NOT the ceiling. The QA-SRL win is on canonical-heavy text. The brain recruits its dorsal stream (Broca's BA44 + arcuate fasciculus) for reversible non-canonical clauses — object-relatives and clefts, where the patient is a fronted antecedent reached by a filler-gap/movement dependency, not by linear position (Friederici 2011; Grodzinsky & Santi 2008; Caramazza & Zurif 1976). On a controlled reversible set (gold by construction) and on real QA-SRL object-relatives:

construction	two-line	filler-gap (ORACLE parse)	filler-gap (REAL arc parser)
synthetic object-relative (n=1500)	0.001	1.000	0.224 (+0.223 ABOVE)
synthetic object-cleft (n=1500)	0.003	1.000	0.186 (+0.183 ABOVE)
real QA-SRL object-relative-like (n=1711)	0.080	—	0.294 (+0.214 ABOVE)
canonical / passive	1.000	1.000	0.95 / 1.00
On the fronted regime the two-line rule is below the info-free twin — it systematically anti-picks. The brain's filler-gap operation with a correct parse resolves it perfectly; even our weak parser beats the two-line rule there, CI-separated, on synthetic and real text. Honest cost: applied ungated with the UAS-0.79 parser, the filler-gap arm is net-negative overall (−0.107) because the parser false-fires the relative-clause rules on canonical sentences. So the real frontier is a stronger relative-clause parser + a construction gate — a missing primitive to BUILD, not a ceiling. This is the honest hole in "two lines beat the machinery": true on the easy regime, the opposite on the hard one.

3. Brain-fidelity: my mechanisms are OVER-ACCURATE. A deeper adversarial drill found "point to the antecedent" is not how the brain resolves the dependency — the brain does cue-based memory retrieval at the gap (Lewis & Vasishth 2005; Van Dyke & McElree 2006) and therefore suffers similarity-based interference (Gordon, Hendrick & Johnson 2001). A structural pointer is immune → more accurate than humans, the tell of a convenient substitute. Tested on the Gordon design (similar vs dissimilar intervening noun, n=2000/cell):

mechanism	similar	dissimilar	similarity effect (dis−sim)
structural point-to-antecedent	1.000	1.000	+0.000 FLAT (over-accurate)
cue-based retrieval (ACT-R-style, cue-overload)	0.71–0.90	0.91–0.96	+0.05…+0.20 CI-separated ABOVE (temp sweep)
twin (control)	0.46	0.46	+0.000 (no artifact)
The cue-based mechanism reproduces the human interference signature robustly across a temperature sweep; the structural one does not. The faithful copy of the computation is content-addressable retrieval with cue-overload, not structural pointing.

4. Fidelity verdict table. positional/NVN = PINNED; aux+participle voice = DEFENSIBLE-REDUCTION; voice-flip = OVER-SIMPLIFICATION (brain often fails to flip — Ferreira 2003); point-to-antecedent = OVER-SIMPLIFICATION (Gordon 2001); dual-route hard if/else = OVER-SIMPLIFICATION (routes run parallel and compete); cue-based retrieval = PINNED as the faithful mechanism (tested).

Controls (each excludes something)
Info-free twin loses to two-line on natural text (0.287 vs 0.766) but beats it on the fronted regime → localizes the failure, excludes "the two-line rule always works."
ELAB_SCRAMBLE (0.530 vs 0.751): the learned weights carry real signal → the elaborate reader had a fair, trained shot and still lost.
ELAB_ANIMACY_ONLY ≈ twin (0.312) vs ELAB_ORDER_ONLY (0.686) → the reader's usable cue is word order; animacy is the wrong English cue.
Oracle vs real parse (1.000 vs ~0.25 on the fronted regime) → the mechanism is right; the shortfall is parser quality, not a ceiling.
Cue-retrieval vs structural on the Gordon manipulation (drop vs flat, 3 temperatures) → excludes "structural pointing computes the way the brain does."
The engineering-vs-fidelity fork (owner's call)
The meaning pipeline wants maximally accurate patient selection — and for that the structural mechanisms are better precisely because they're over-accurate (they don't make the human errors). The brain-faithful mechanism (cue-based retrieval) is less accurate by design. So "most brain-faithful" and "most accurate for extraction" point in different directions on the hard regime. My recommendation: for extraction, adopt the structural filler-gap resolver and invest in a stronger parser; keep the cue-retrieval result as the faithful model of comprehension, relevant only if the goal becomes modeling human reading.

Proposed hdlab change — NOT landed (Q111; strategy lands it)
Replace the perceptron cue-integration for PATIENT with word order + precise voice (aux+participle) in situation_reader._pick_role_mentions (~4 lines); do not weight animacy as an English role cue.
Add a filler-gap resolver for relative clauses, GATED on confident relative-clause detection; keep it off on the live path until the gate is reliable (its ungated form is net-negative).
Invest in a stronger relative-clause parser — the measured ceiling — and redirect freed effort to stage 2 (meaning).
Key realizations (the enabling moves)
The voice signal was a trap that flipped the headline — QA-SRL's isPassive is the question's voice, not the clause's; detecting voice from the sentence (the rule's real job) flipped "elaborate wins" to "two-line wins."
"Replace it" was the halfway point — testing the regime the brain's dorsal parser exists for showed the story inverts there; the aggregate win hid it.
Oracle-vs-real parse turned a null into a diagnosis — "nothing beats two-line on the hard cell" was a weak-parser artifact, not a ceiling.
Over-accuracy is a fidelity failure, not a success — a mechanism that never makes the human error isn't a copy of the human computation; building the Gordon test is what converted "we cite neuroscience" into "we test the brain's computation."
Most-faithful and most-accurate can diverge — naming that fork is itself the finding.
What I did NOT establish / would withdraw first
I diagnosed but did not build the stronger parser (a separate organ effort). I did not run the fate-verb extract_facts_strict at power (specialised; the prior n=100 SOLVED decomposed its 0.90). The Ferreira voice-route fidelity probe needs a reliable plausibility resource the repo lacks — I declined to run a rigged version.
Withdraw first: the +0.214 real-QA-SRL filler-gap gain (its stratum is object-relative-like, structurally detected). I would defend last the headline (elaborate loses, CI-separated, twin loses everywhere) and the fidelity finding (structural flat, cue-retrieval drops, across a temperature sweep) — both witness-reproduced.
Reproduction
Experiments: experiments/exp_reader_vs_twoline_qasrl_power_v1.py, …_fillergap_reversible_objrel_v1.py, …_cue_retrieval_interference_v1.py (each self-test + smoke gated, ASCII, CPU, no network).
Witnesses: the three verification/test_reader_*.py above.
Data: data/exp_reader_vs_twoline_qasrl_power_v1/ (+ _detail_sample.json), …_fillergap_reversible_objrel_v1/, …_cue_retrieval_interference_v1/.
Closure: notes/problems/the_reading_extractor_may_not_beat_a_two_line_rule/SOLVED.md; problem_ledger.py --check → malformed/incomplete: 0 (awaiting strategy integration). Follow-up brief for the parser build: …/PROPOSED_FOLLOWUP_role_assignment_untested_where_the_brain_needs_syntax.md.
TLDR
The pipeline's first step works out who did what to whom. We suspected its fancy version was no better than a dumb two-line rule (word order, flipped for "was X-ed"). On 17,330 real sentences the dumb rule doesn't just tie — it beats the fancy version, so retire the fancy machinery for ordinary sentences. But that's only true for easy sentences. On genuinely hard ones — "the banker that the lawyer chased," where you must hold the first noun in mind and connect it across the sentence, exactly what the brain switches on a special circuit for — the two-line rule is worse than guessing, and the brain's real trick (reach back and grab the noun the clause is about) gets them right. Our software can't do that reliably yet because our grammar-parser is too weak — so the real job is a better parser, not a fancier guesser. And deeper: the brain's "reach back and grab" isn't perfect — it's a memory lookup a similar nearby word can hijack, which is why people misread those sentences too. We built that faithful version and it makes the same mistakes humans do, where our clean version doesn't — a reminder that copying the brain sometimes means copying its errors, and that "most accurate" and "most brain-like" aren't always the same choice.

Questions
None. (One decision flagged for you: on the hard regime, optimize for extraction accuracy via a stronger parser, or for fidelity via cue-based retrieval. My recommendation: the former.)

Next steps
Land the precise-voice patient selector; retire the perceptron cue-integration for PATIENT.
Build a stronger relative-clause / filler-gap parser + a construction gate — the measured ceiling and the real brain-foundational headroom (brief drafted).
Redirect the freed effort to stage 2 (meaning) — the named Phase-1 bottleneck.
(Optional fidelity) if modeling human comprehension becomes a goal, adopt cue-based retrieval and validate against the Gordon and Ferreira human data.
