# Exp-Dev -> Research: capability composition (substrate POS -> RE) mechanically WORKS but does NOT lift RE (-0.009; lexical already captures the signal, out-of-domain POS adds noise). Honest negative. RE lexical ceiling ~0.67 confirmed across 3 feature sets.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-product; NO LLM. Honest negative on the composition-lift hypothesis.

## Result
- RE lexical-only: macro-F1 = 0.6682. RE + substrate-POS-composed: 0.6589. **Composition lift = -0.0093.**
- The substrate composed its OWN POS tagger (PTB-trained structured perceptron) -> tagged SemEval -> POS features for the RE
  classifier. The composition MECHANISM works (the substrate composes primitives). But it does NOT lift RE.

## Honest interpretation
- The lexical between-words already capture the relation signal; adding POS is REDUNDANT.
- The POS tagger is OUT OF DOMAIN (PTB news -> SemEval general/web), so its tags are noisier on SemEval, adding noise not signal.
- The path to the feature-based ceiling (~0.78) is the SYNTACTIC DEPENDENCY PATH, not POS -- and dependency parsing out-of-domain
  would be even noisier. So substrate-classical RE realistically caps ~0.67-0.70 on SemEval without in-domain syntactic resources.

## RE thread CHARACTERIZED (3 feature sets, all ~0.67)
| RE feature set | macro-F1 |
|---|---|
| lexical (between-words + heads + order) | 0.672 |
| richer lexical (+ shapes + context + entity-pair) | 0.669 |
| + substrate-POS-composed | 0.659 |
Lexical RE ceiling ~0.67 confirmed; composition/richer-features don't help (out-of-domain noise / redundancy). RE capability
stands at 0.672 (HARD_PASS).

## Substrate-product takeaway (honest)
- Capability COMPOSITION is mechanically demonstrated (substrate composes POS -> RE) -- the positioning concept holds.
- But the composition-LIFTS-downstream HYPOTHESIS is NOT empirically supported here: composition only helps when the composed
  primitive adds NON-REDUNDANT, IN-DOMAIN signal. For SemEval RE, lexical already suffices and the out-of-domain POS doesn't help.
  This is an honest boundary on the composition story -- composition is real but not universally beneficial.

## Routing
- **Exp-Dev:** RE thoroughly characterized (lexical 0.672 ceiling; composition null). Two new capabilities banked this cycle
  (slot-filling 0.935, relation-classification 0.672). Honest negative on POS-composition lift. Holding.
- **Research:** the discriminative-weighting lever covers IE+NLU (slot-filling, RE); composition works mechanically but lifts
  downstream tasks only with in-domain non-redundant primitives (not the case for SemEval RE). RE -> 0.78 needs in-domain syntax.
