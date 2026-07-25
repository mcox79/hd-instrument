# Pre-registration: arc_reasoner_symbolic_tiebreak_v1

**Filed BEFORE the run. Bands + thresholds fixed in advance; reported STRAIGHT, NOT tuned.**

Cell: `experiments/exp_arc_reasoner_symbolic_tiebreak_v1.py`
Reasoner: `hdlab/reasoner.py` (`DerivationReasoner`, new `tiebreak_mode` param)
Config: link_mode=`lemma_syn` (the VET-29568 config), 233 science rules
(`data/rules/arc_science_typed_rules_v1.json`), full held-out ARC-Challenge test.

## Question
On the questions the composed reasoner DERIVES, the decision decomposes (VET 29568):
gold_only (only gold derivable -> ~1.00), TIE (gold AND >=1 distractor both derive ->
thin-cosine tie-break ~chance), dist_only (gold unreachable -> 0.00, coverage/meaning,
DEFERRED). Can the reasoner PICK gold among CO-DERIVABLE candidates on the TIE subset
using SYMBOLIC tie-break signals instead of thin cosine, raising TIE-subset accuracy
above chance -> functional reasoning on the covered subset?

## Mechanism (ONE variable across arms = tie-break METHOD)
`tiebreak_mode="legacy"`  : completeness -> shortest chain -> combiner (thin cosine) -> index.
`tiebreak_mode="symbolic"`: intent-TERMINAL match -> intent-ANY match -> do-calculus-present
-> completeness -> shortest -> combiner -> index. Question-INTENT (asked relation: CAUSE /
REQUIRES / USEDFOR / SOURCEOF / COUPLEDRELATIONSHIP / IFTHEN) parsed from the stem
(`INTENT_PATTERNS`, hand-designed from relation semantics, NOT fit to test labels); a
candidate REACHED BY the asked relation ranks ABOVE one reached by an off-type chain; thin
cosine DEMOTED to last. Rules / graph / search / coverage / CI / do-calculus IDENTICAL across
arms; the derived partition (gold_only/tie/dist_only counts) is byte-identical across modes.

Chance calc FIXED: `chance = mean(1/n_choices)` over the derived subset (NOT the inherited
`1/int(mean(n_choices))` quirk which floored the divisor to 3 -> 0.333).

## Pre-registered bands (5)
1. `tie_subset_rises_ge_0.10`: symbolic TIE-acc - legacy TIE-acc >= +0.10 absolute.
2. `tie_subset_abs_ge_0.42`: symbolic TIE-subset acc >= 0.42 (toward 0.50; strictly > legacy 0.32).
3. `overall_derived_gt_fixed_chance`: symbolic overall derived-acc > fixed chance (~0.25).
4. `gold_only_preserved_ge_0.95` (GUARDRAIL): symbolic gold_only acc >= 0.95 (clean wins untouched).
5. `partition_identical_one_variable`: derived partition counts identical across modes.

## Verdict logic (pre-registered, can-fail)
- GUARDRAIL breach (gold_only < 0.95 OR partition not identical) -> `GUARDRAIL-BREACH` / HARD_FAIL.
- Bands 1+2+3 pass (+ guardrail) -> `TIE-BREAK-WORKS-functional` / PASS (functional reasoning on covered subset).
- TIE rise < +0.03 -> `HONEST-NEG-decision-meaning-bound` / HONEST_NEG (the DECISION among co-derivable
  candidates needs grounded question-relevance meaning; extends the fine-meaning wall from coverage to selection).
- else -> `MIDDLE` / MIDDLE_BAND.

## CAN-FAIL (explicitly pre-registered)
If the symbolic signals cannot lift the ties (TIE rise < +0.03) the tie-break is genuinely
MEANING-BOUND: deciding which valid derivation actually ANSWERS the question needs grounded
question-relevance meaning. HONEST-NEG, cleanly isolated. This confirms grounded meaning is
needed even for the DECISION, not only for coverage.

## Anti-leak / discipline
Held-out ARC-Challenge test; science rules are facts NOT derived from test labels. Intent
patterns are surface question-FORM (relation semantics), designed before the run, not iterated
against accuracy. Deterministic; atomic metrics; start-marker; crash-diag; heartbeat.
Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; VET-PENDING
(skunkworks owns landed-VET); NO atom banking.

## RESULT (MEASURED@data/exp_arc_reasoner_symbolic_tiebreak_v1/metrics.json)
`HONEST-NEG-decision-meaning-bound` / HONEST_NEG, 2/5 bands.
- TIE-subset acc 0.364 -> 0.364 (d=+0.000, n_tie=66); overall derived-acc 0.243 -> 0.243 vs
  fixed chance 0.2498; gold_only 1.000 -> 1.000 (n=26, GUARDRAIL held); dist_only 0.000 (n=114);
  partition identical (one variable clean); 0 tie flips.
- Mechanism diagnostic (tie subset, n=66): intent fires on 13/66; gold's derivation-terminal
  relation aligns with the asked relation on only 4/66; net-zero discrimination. The residual
  tie is a question-relevance MEANING judgment (which valid derivation ANSWERS the question)
  that both thin-cosine and symbolic structure fail. Pre-registered CAN-FAIL outcome.
