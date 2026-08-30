# Research drill: how the brain answers a comprehension question over a situation model (2026-08-30)

Literature drill (hdi_research, saturated across 6 questions) for
`the_reader_cannot_answer_a_question_over_its_situation_model`. Full brief + synthesis in the task
transcript; this note is the durable, citable digest folded into SOLVED.md.

## Prior-work check
`experiment_index`: broad prior work on `situation` (48 landed), `comprehension` (41), `router` (60),
`readout` (193), but **ZERO** cells on `question-answering` / `QUD`. The QA-over-model interface is a
genuine gap in the arc -- nothing to re-derive or credit.

## The four load-bearing verdicts

**(a) Question -> dimension routing = PARTIALLY PINNED.**
- PINNED: dimension->subsystem specialization is real -- PPA/parahippocampal+retrosplenial = SPACE
  (Epstein & Kanwisher); hippocampal/entorhinal TIME CELLS = temporal order (Eichenbaum 2014 Nat Rev
  Neurosci 15:732; Umbach 2020 PNAS 117:28463); pSTS = agents/who-did-what (Isik 2017 PNAS 114:E9145);
  mPFC+hippocampus = causal (Radvansky & Zacks 2014 Event Cognition); rTPJ+mPFC = ToM/who-believes
  (Saxe & Kanwisher 2003). The five Zwaan indices are separately maintained + updated (Zwaan &
  Radvansky 1998 Psych Bull 123:162; "who/when/where" test, Mem&Cog).
- OUR-INVENTION: a DISCRETE router/switch. The subsystems run IN PARALLEL, bound into ONE situation
  model (PM/DMN + hippocampus: Ranganath & Ritchey 2012 Nat Rev Neurosci 13:713; Baldassano 2017
  Neuron 95:709, PMID 28772125). The "routing" that happens is a GRADED CUE-BASED RACE
  (Lewis & Vasishth 2005 Cog Sci 29:375; McElree 2000): a cue spreads activation, matching items race
  to threshold, most-activated wins. "There is no router; there is a cue and a race."
  -> FAITHFUL FORM = soft, parallel, threshold-gated cue-based dimension-scoring (multi-dimensional
  answers allowed), NOT a 1-of-N keyword switch.

**(b) Read-off-model vs re-read = STRONGLY PINNED (the floor is correct).**
Kintsch's three levels -- surface / textbase / situation model (Kintsch 1988 Psych Rev 95:163; van Dijk
& Kintsch 1983). The signature is a DISSOCIATION: helping textbase memory can hurt situation-model
measures. Whole question classes are UNANSWERABLE from the textbase / word-overlap and are answered
from the maintained model: bridging inferences (McKoon & Ratcliff 1992 Psych Rev 99:440, PMID 1502273),
causal-antecedent / goal / global-coherence (Graesser Singer & Trabasso 1994 Psych Rev 101:371, PMID
7938337), the spatial-distance effect (Rinck & Bower 1995/2000, PMID 11219959), temporal-order retrieval
tracking model-time not text-position (Radvansky Zwaan Federico & Franklin 1998 JEP:LMC), anaphor
resolved from the model's focus-of-attention (Garrod & Sanford). -> "answer from the maintained model,
not by re-reading" is the brain-faithful claim, and word-overlap is the correct FLOOR.

**(c) Generalization target = paraphrase-invariant QUD, NOT keywords.**
A question's meaning IS the set of its possible answers -- a partition over possibilities (Groenendijk &
Stokhof 1984; Roberts 2012 [1996] Semantics & Pragmatics 5:1, the Question Under Discussion). Paraphrases
induce the SAME partition / QUD ("where did she go" == "which room did she end up in"). The brain keys on
answerhood conditions, so comprehension is paraphrase-robust. A keyword router (before/after->temporal,
caused->causal, "refer to"->coref) keys on exactly the surface level the brain abstracts away, and breaks
on "earlier that day" (temporal, no before/after), "on account of" (causal, no caused), "who is she"
(coref, no "refer to"). -> FAITHFUL = a question-type/QUD representation over relational cues, not fixed
phrasings. THIS IS THE KEY FIDELITY AXIS and must be MEASURED (paraphrase robustness).

**(d) Abstain = threshold + feeling-of-knowing gate; never-tracked != tracked-but-absent.**
Cue-based retrieval fails explicitly when nothing crosses threshold (Lewis & Vasishth 2005; ACT-R
declarative retrieval). Whether to infer / keep searching / give up is a metacognitive monitor -- FOK
from accessibility + cue-familiarity (Koriat 1993 Psych Rev 100:609). Distinguish (i) tracked-but-absent
(dimension live, text silent) from (ii) never-tracked (organ not wired into the live model at all) --
the latter has no content to pattern-complete from -> HARD abstain, never confabulate. SQuAD 2.0
(Rajpurkar Jia & Liang 2018 ACL) confirms abstention is the hard, first-class capability, not a fallback.
Our SPACE/ToM/entity-state organs are the NEVER-TRACKED case (islands) -> hard abstain until wired.

## Reference architecture (cite in SOLVED.md)
- **SEM -- Structured Event Memory (Franklin, Norman, Ranganath, Zacks & Gershman 2020, Psych Rev
  127:327, PMID 32223284):** the neuro-symbolic brain model of the situation-model store -- structured
  symbolic scenes in a vector space, role-filler binding, schema learning, and reconstruction-based
  readout (infers missing fillers from schema). This is the brain-grounded architecture for the
  router+readout; content-addressable reconstruction, not silo lookup. (Also validates the codebase's
  standing FHRR/role-filler choice.)
- **Lewis & Vasishth (2005):** the retrieval MECHANISM (cue-based, activation, threshold, race) -- and
  the SAME mechanism the codebase's graded coref binder already implements.
- **QUALM (Lehnert 1978)** + **QUEST (Graesser & Franklin 1990):** the historical glass-box precedents --
  question-TYPE (13 conceptual categories) selects a retrieval strategy over a structured story model;
  answers read off the memory representation, not re-read. Right idea, brittle hand-coded matching, no
  graded retrieval or paraphrase generalization.

## The five fidelity fixes applied to the build
1. Hard keyword router -> SOFT PARALLEL cue-based dimension-scoring, threshold-gated (biggest gap).
2. Surface keywords -> relational-cue / QUD-type features (paraphrase-robust); MEASURE paraphrase
   robustness as a first-class result.
3. Per-dimension silos -> readout inherits the reader's own content-addressable coref (the graded
   binder) so "which she" uses the bound model; the dimension emerges from cue-match strength.
4. Abstain-by-silence -> explicit threshold + never-tracked vs tracked-but-absent; SPACE/ToM/state
   are never-tracked -> hard abstain.
5. Keep abstain-unless-marked-inferred (SEM-style schema reconstruction is where confabulation lives;
   defer it, note as a future capability).

## Follow-on drill (2x discipline, if the router lift is load-bearing)
Least-pinned link = the mechanism that forms a paraphrase-invariant question/QUD representation
(fix #2). If paraphrase robustness becomes the headline, drill that specifically.
