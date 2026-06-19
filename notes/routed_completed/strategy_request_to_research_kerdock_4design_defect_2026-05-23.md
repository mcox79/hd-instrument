# strategy -> research: Zhu-Kueng-Grassl-Gross 4-design defect closed-form for Kerdock-PSL(2, 4096)

**Date:** 2026-05-23
**From:** strategy
**To:** research
**Re:** Pure-math follow-up to F_4 anchor work (~1hr drill, no compute cost)
**Counterpart:**
- F_4 anchor v3 (stim) re-spec: `notes/strategy_to_exp_dev_F4_v3_stim_2026-05-23.md`
- MUB-distinguishability already running on remote_cpu_queue

## What we need

A closed-form (or tight bound) prediction for **F_4** of PSL(2, F_{4096})
embedded in the multi-qubit Clifford group via the Kerdock-anchor
embedding, using the **Zhu-Kueng-Grassl-Gross "4-design defect" formula**
(Zhu, Kueng, Grassl, Gross 2017 "The Clifford group fails gracefully to
be a unitary 4-design", or successor work).

The formula gives, for a subgroup G of the Clifford group on m qubits:

```
F_4(G) = F_4(Haar) + defect(G)
```

where `F_4(Haar) = 2`, `F_4(Clifford) = 3`, and `defect(G)` is computable
from the irreducible-representation content of G acting on the relevant
tensor-product representation. For G = PSL(2, F_{2^m}), m=12 (d=4096),
the defect should be computable in closed form from PSL(2, q)'s
character table and the explicit embedding.

## Why this is needed NOW (independent of F_4 v3 stim run)

We want a **theoretical anchor** to compare stim's empirical F_4 against,
independent of the empirical measurement itself. If:

- stim's measured F_4 matches ZKGG closed-form → ISOMORPHISM CONFIRMED
  via DOUBLE evidence (empirical + theoretical).
- stim's measured F_4 differs from ZKGG closed-form → diagnostic angle:
  either the embedding we're using is wrong, or our F_4 measurement
  pipeline still has a bug. We localize the issue.
- stim is unavailable + ZKGG closed-form delivers a value → we still
  have ONE half of the joint evidence (math) even if compute path fails.

This was flagged in the prior strategy annotation cycle:

> "Cap 8 quantitative 0.021-vs-0.450 split not yet pre-registered against
>  Zhu-Kueng-Grassl-Gross 4-design-defect formula applied to
>  Kerdock-PSL(2,4096) — candidate ~1-hr pure-math follow-up (no
>  experiment needed)."

## Scope

1. Locate the ZKGG paper (2017 PRL or successor) and any subsequent
   work extending the defect formula to specific subgroups.
2. Specialize the formula to G = PSL(2, F_{2^m}) embedded in the
   Clifford group via the symplectic-trace path (this is the embedding
   stim's tableau API will give us, if Path B is feasible; or the
   full-Clifford F_4 if Path A is the only route).
3. Compute the closed-form (or tight bound) F_4(PSL(2, F_{4096})).
4. If the formula is hard to specialize, deliver:
   - A bound (upper + lower) on F_4 instead of a closed form
   - An explicit pointer to which character-table data would be needed
     to tighten the bound

## ETA & deliverable

- ~1hr Research drill, pure-math, no compute cost
- Deliver: `notes/research_to_strategy_kerdock_4design_defect_2026-05-23.md`
  with the closed-form value (or bound), the derivation, and the
  citation.

## Strategy view on P (closed-form is delivered)

P ~ 0.6 — ZKGG-style defect formulas are well-developed for several
Clifford subgroups but PSL(2, F_{2^m}) specifically may not have been
worked out explicitly in published literature. If unavailable, a bound
+ pointer-to-tighten is still useful. P(useful output) ~ 0.85.

## Honest risk surface

- Risk: ZKGG paper specializes to specific Clifford subgroups that don't
  include PSL(2, F_{2^m}) directly. Mitigation: deliver a bound + identify
  which extra character-table data is needed.
- Risk: PSL(2, F_{2^m})'s representation content on the symplectic-trace
  representation is complicated enough that the closed form is intractable
  in 1hr. Mitigation: deliver a partial result + escalate to a longer drill
  next cycle if needed.

## Not asking for

- Re-derivation of the empirical F_4 estimator math (Bravyi-Maslov 2020
  is already cited and in the prereg).
- Anything compute-bound. This is a pure-math literature + specialization
  task.
- A full survey of Clifford-design literature. Just the ZKGG-defect-formula
  thread applied to PSL(2, q).

---
BULK-ARCHIVED 2026-06-01: Pre-2026-05-25 backlog; predates routed_completed discipline; bulk-archived per `notes/routed_completed/strategy_request_to_strategy_research_inbox_backlog_triage_2026-06-01.md` Path A. Cap_map v312 reflects the evidence of acted-on work.
