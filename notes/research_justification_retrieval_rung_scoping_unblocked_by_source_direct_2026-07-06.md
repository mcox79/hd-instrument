# Scoping: justification-retrieval self-audit rung -- UNBLOCKED by source-direct, dispatch-ready

Date: 2026-07-06. Director main-thread scoping (forward work while the control-branching + dup-class self-margin
FULLs VET). The roadmap's next self-audit rung after coverage (roadmap 8b90c6667) was originally gated on "a
gate_claims adoption wave." Source-direct entailment (cert_ledger_source_direct_entailment_v1, MM, 81.3% coverage
canonical) sidesteps that gate -- so justification-retrieval is now buildable on the source-direct backing.

## What the ladder now has
- Tier-1 self-query (MM): can the substrate retrieve/round-trip its own records.
- Tier-2 numeric-entailment (MM) + SOURCE-DIRECT coverage (MM, 0.813): does each cited number actually satisfy its
  cited threshold, checked directly against the citing cell's own metrics.json. MEANINGFUL (24.8x the retrieval ceiling).
- Tier-3 global-consistency (MM clean): whole-ledger cycle/fork/tier-monotonicity structural audit.
So the substrate can now: retrieve its records, verify each numeric claim against its source, and structurally audit
the ledger. The MISSING rung = assemble the JUSTIFICATION: for a given cert claim (an atom's tier/verdict), gather
the CHAIN of backing evidence and check the claim is actually SUPPORTED by it (not just internally numeric-consistent).

## The rung: justification-retrieval + support-check
For a target cert claim C (e.g. "cell X is CHAIN_GRADE" / "metric M >= threshold T"), ASSEMBLE its justification:
1. the citing cell's persisted metrics.json leaves that C depends on (source-direct already resolves these),
2. the pre-registered bands C was gated against (the prereg referent),
3. the firing-control evidence (did the discriminator fire),
and CHECK: do the assembled leaves + bands actually ENTAIL C's verdict? i.e. re-derive the pass/fail from the backing,
and flag any claim whose stated verdict is NOT entailed by its own assembled evidence (an unsupported certification).
This is the natural composition of source-direct (leaf resolution) + Tier-2 entailment (numeric check) + the prereg
bands -- monitor-not-control: it re-derives verdicts from persisted evidence, never edits the ledger.

## Why it's buildable NOW (not gated)
- Source-direct proved the leaves are resolvable (0.813 coverage) and the comparator is exact (op_agreement 1.0).
- The prereg referents exist (preregs/*.md, cited per cell).
- No gate_claims adoption wave needed -- the evidence lives in each cell's metrics.json + prereg, reachable source-direct.

## Honest scope + expected tier
- The support-check is a re-derivation (deterministic given the bands + leaves) -> likely MEASURED_MECHANISM (by-
  construction, monitor-not-control), same tier convention as the rest of the ladder. NOT CG (heuristic band-parsing).
- The REAL payoff is the byproduct: like source-direct surfaced 4 not_holding + 40 unbacked (all artifacts, records
  self-consistent), justification-retrieval would surface any UNSUPPORTED certifications -- claims whose own evidence
  doesn't entail their verdict. If it finds zero genuine ones (expected, given source-direct found records self-
  consistent), that is itself the meaningful positive: the substrate's certifications are backed by their evidence.
- Honest residual to measure: claims whose prereg bands are prose-only / not machine-parseable (the coverage gap).

## Dispatch recipe (ready)
- New cell reusing source-direct's leaf resolution + Tier-2 comparator + a prereg-band parser. Pre-reg: support-recall
  (fraction of claims whose verdict is re-derivable from assembled evidence) + a firing control (scramble the band ->
  support-check must break) + the honest unsupported/unparseable residual. Multi-seed FULL -> remote_cpu_queue.
- FRAMING: monitor-not-control, narrow glass-box, re-encode HELD, NEVER git add -A.
- Dispatch AFTER the current self-margin wave VETs (avoid over-spawn); this is the queued next self-audit build.

## Where it sits
Completes the self-audit ladder from "can I read/verify/structure-check my records" to "are my CERTIFICATIONS actually
supported by their evidence" -- the deepest honest form of the substrate reasoning about its own correctness, still as
narrow glass-box monitor steps (NOT self-modification). Composes with cert_ledger_source_direct_entailment_v1 +
the Tier-1/2/3 ladder + roadmap 8b90c6667.
