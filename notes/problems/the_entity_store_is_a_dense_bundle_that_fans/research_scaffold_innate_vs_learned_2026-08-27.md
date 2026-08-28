# Drill: is a LEARNED structural scaffold brain-foundational? (before building TEM)

Third drill (owner: "Is the learned scaffold brain foundational? do a research drill if necessary").
Dispatched via `research`. Full synthesis persisted here. Tags PINNED / OUR-INVENTION / PLAUSIBLE-BUT-UNTESTED.
ASCII only. (Agent also wrote a longer copy under notes/ + a status_log entry.)

## HEADLINE

A learned structural scaffold is brain-foundational in its TARGET (TEM's factorized, reusable, ACTION-DRIVEN
g/x split) but NOT in its TRAINING MECHANISM (backprop-through-time). Build a PATH-INTEGRATING action-driven
scaffold (zero training) + a LOCAL-RULE successor-representation predictive layer; do NOT build a backprop TEM.

## Q1 -- INNATE vs LEARNED scaffold: PINNED innate/pre-structured
- Grid/head-direction attractor architecture is substantially PRE-STRUCTURED, not learned from scratch. HD
  coherence near-adult from earliest testable age; grid regularity matures abruptly (P16-P24); a 2026 preprint
  reports toroidal grid-attractor TOPOLOGY by P10 before eye/ear-opening (PLAUSIBLE-BUT-UNTESTED, unreplicated).
  Deprivation delays but does not prevent; "preconfigured but experientially calibrated" (Ulsaker-Janke et al.
  2023 PNAS, PINNED). => a HAND-DESIGNED fixed scaffold is MORE faithful than a backprop-trained one.

## Q2 -- TEM's learning rule: PINNED implausible
- TEM (Whittington & Behrens 2020, Cell) trains structural weights by BACKPROP-THROUGH-TIME and its own text
  says "not a biophysically realistic model" (limits its Hebbian-plausibility claim to the fast memory matrix M
  only). Tang, Barron & Bogacz 2024: TEM "trained by BPTT, a learning rule unlikely to be employed by the
  brain." Weight-transport (Lillicrap et al. 2020) + BPTT temporal-credit-assignment (Bellec et al. 2020).
  => the REPRESENTATION is brain-like; the brain does NOT learn it this way.

## Q3 -- what is learned, by what rule: PINNED none is gradient descent
- (a) scaffold CONNECTIVITY = innate attractor; (b) fast content<->scaffold BINDING = one-shot HEBBIAN
  (Nakazawa; Marr; McNaughton-Morris); (c) slow TRANSITION/SCHEMA structure = replay/consolidation (Gilboa &
  Marlatte 2017). None is backprop.

## Q4 -- PATH INTEGRATION is the core: PINNED
- Grid cells PATH-INTEGRATE: g_t = f(g_{t-1}, velocity/ACTION), NO time input (Burak & Fiete 2009; McNaughton
  et al. 2006 Nat Rev Neurosci; Sreenivasan & Fiete 2011). Buys route/order-invariance, multi-scale redundant
  precision, cross-context REUSABILITY (Behrens 2018), and NON-SPATIAL relational generalization (Constantinescu,
  O'Reilly & Behrens 2016 Science -- grid-like fMRI in a purely CONCEPTUAL task). An open-loop CTX(t)=f(t)
  cannot reach any of these IN PRINCIPLE, regardless of tuning. => our clock is the fixed-tick special case
  CTX_t = CTX_0 * A^t; the faithful scaffold uses an ACTION-dependent update CTX_t = CTX_{t-1} * A(a_t).

## Q5 -- bio-plausible LEARNED structure (no backprop): PINNED
- Grid structure is Hebbian/PCA-learnable (Dordek et al. 2016 eLife). The SUCCESSOR REPRESENTATION (a
  predictive map) is TD/eligibility-trace learnable by an explicit LOCAL rule (Fang, Aronov, Abbott &
  Mackevicius 2023 eLife; Stachenfeld et al. 2017 Nat Neurosci = SR as the hippocampal predictive map),
  including over a purely TEMPORAL sequence -- no backprop. => the genuinely "learned" brain-foundational layer
  is a SR predictive map learned by a local TD rule, generalizing our schema-gist EMA into a next-event predictor.

## BOTTOM LINE (ranked, concrete)
1. (tied) PATH-INTEGRATING action-driven scaffold: CTX_t = f(CTX_{t-1}, a_t), a_t = the transition/event type,
   replacing CTX(t)=f(t). ZERO training. Buys structural transfer/reuse the open-loop clock cannot.
2. LOCAL-rule SUCCESSOR-REPRESENTATION predictive layer (TD/Hebbian), generalizing schema-gist into a next-event
   predictor. The bio-plausible "learning".
3. Backprop TEM -- DO NOT BUILD. Only value = existence-proof of the representational target if (1)+(2) still
   lack cross-entity generalization.
