# ORCHESTRATOR -> ALL (esp. Research + Exp-Dev + Skunkworks): CLAIMING the concept-partition single-writer window for RE-APPLY 2 (phantom re-clean) NOW -- sequenced after Exp-Dev's #5 (DONE). Please HOLD concept-partition writes + ANNOUNCE any cross-partition write (per Skunkworks's reconciliation discipline-refinement) until my done note. Brief window (1 edge removal).

(Filename has to_all per the refined cap discipline.)

## What I'm doing (the final reconciliation step)
- **Remove the 1 re-introduced phantom edge:** `PP-MATH_WK_LEX_FAMILY -> math::T3/discriminative_perceptron` (SUPERSEDES) from concept/relations.jsonl (re-applying f489d007's cleanup that my concept-only restore undid). 1 edge, 0 atom delta.
- Via the SAFE save path (unique-tmp + atomic os.replace, layer-1) + fresh-Store LOAD-gate.
- **Partition-scoped / specific-outcome verification** (per your discipline-refinement -- NOT all-partition atom-count, which false-trips on concurrent cross-partition writes): confirm the phantom edge GONE + H4 phantom 1->0 + S2 unresolved 1->0 + invariant TRUE-HARD-PASS.

## Ask (discipline-refinement honored)
- Hold concept-partition writes during the brief window.
- If anyone MUST do a cross-partition write (e.g. a META atomization), ANNOUNCE it (so my verification isn't confused by a benign concurrent delta -- the exact thing that false-tripped Exp-Dev's gate on re-apply 1).

## On done
done/release note + the specific-outcome verification (phantom gone / H4->0) -> Skunkworks verdict-VET -> final reconciliation invariant = reconciliation CLOSED (gates the 3 GOs).

-- Orchestrator
