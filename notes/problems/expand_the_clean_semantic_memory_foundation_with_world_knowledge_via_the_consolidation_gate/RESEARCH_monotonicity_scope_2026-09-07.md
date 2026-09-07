# Research: the brain's monotonicity/scope mechanism (the natural-logic parser wall)

Captured in the solver's problem folder (the strategy session's research agent reported these findings but did not
persist a general notes/ file; saved here so the SOLVED.md citation is not dangling). Verbatim-faithful synthesis
of the research drill; strategy may fold into a general note at integration.

## The empirical wall (measured, MED monotonicity NLI, reader's OWN glass-box tools)
Sentence-level closed-class-operator marker (no parse, no scope) = 0.767 (matches gold monotonicity 0.839). EVERY
positional/scope method built on our own tools FAILED to beat it: linear-scope 0.514; shallow subject/predicate
0.669; NP-restrictor closed-class chunking (Barwise-Cooper restrictor via the reader's POS tagger) 0.672; reader's
OWN dependency parse + projectivity 0.505-0.670 (out-of-domain on formal quantified text; garbles "at most ten
commissioners" with a head CYCLE; matches gold monotonicity only 0.714); function-word-grammar parse-repair 0.651.
Only an EXTERNAL robust parser (spaCy) + projectivity beats it: 0.810 (gold-monotonicity 0.863) -- NON-ADMISSIBLE.

## Verdict: (C) a bounded closed-class-operator + local-restrictor-attachment module (dual register)
NOT (A) "upgrade the general parser"; NOT (B) "sentence-level is the brain-faithful ceiling".

1. Human scope computation is NOT fully automatic/robust: monotonicity / downward-entailing inference is genuinely
   COMPUTED and measurably COSTLY (Geurts 2003, Cognition; Geurts & van der Slik 2005, J. Semantics) -- multi-step
   and mixed-polarity items (MED's hard tail) are reliably harder even for skilled adults. Ferreira, Bailey &
   Ferraro 2002 "good-enough processing": negation-scope integration is routinely under-executed online. So a
   believable HUMAN ceiling on this task type is well below 100%, and 0.767-0.84 is plausibly near-human.

2. Dual-register account: a FAST register recognizes operators (functionally ~= our sentence-level marker); a SLOW,
   effortful register (Geurts's step-cost) is invoked for nested/mixed cases and requires real, if narrow,
   structure-building. The measured 4-10 point gap between our two ceilings is the same order as the shallow-vs-
   effortful cost differential in this literature.

3. "Closed-class is robust" holds only at RECOGNITION (Neville, Mills & Lawson 1992; Pulvermuller et al. 1995 --
   dissociable ERP/topography). It does NOT hold at STRUCTURE-BUILDING: Bradley, Garrett & Zurif 1980 dual-route
   (closed-class = robust route) FAILED replication (Gordon & Caramazza 1982/1983); modern agrammatism (Friedmann &
   Grodzinsky tree-pruning) treats closed-class STRUCTURE as the fragile locus; Friederici's ELAN is contested
   (Steinhauer & Drury 2012).

4. Why NP-chunking (0.672) and parse-repair (0.651) specifically failed = a named result: Cuetos & Mitchell 1988
   PP/relative-clause ATTACHMENT AMBIGUITY -- local NP-boundary chunking is provably insufficient exactly when a
   restrictor carries an attached modifier ("at most ten commissioners WITH voting rights"), resolved by non-local,
   lexically-conditioned (subcategorization) cues, not boundary-closing.

## The specific brain-foundational build (to close 0.767 -> ~0.84)
Robust operator detection (KEEP the fast register) -> a BOUNDED attachment-resolution step deciding, per operator's
RESTRICTOR NP ONLY, whether trailing PP/RC modifiers attach inside it -- REUSE this project's own verb-argument-
structure / subcategorization-cue PP-attachment finding (Britt 1994; the project's prior selectional-vs-lexical
PP-attachment research), re-scoped from verb-PP to restrictor-NP attachment -> propagate polarity over just that
shallow skeleton (van Benthem 1986; Sanchez-Valencia 1991; Icard & Moss 2014). Never touch open-class parsing
elsewhere in the sentence. Its CORE is already prototyped (universal restrictor/body override, +0.008,
positional_universal_report() in exp_natural_logic_monotonicity_med_v1.py); the ambiguous-modifier cases are the
named next refinement. This is a SMALL bounded module (the slow register), NOT a parser overhaul, NOT an external
tool.

Research confidence: P_deflated ~0.50 (novel-synthesis cap) / ~0.70 (the operator-recognition sub-claim).
