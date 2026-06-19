# exp_dev -> research: CH-P6 substrate-vs-LLM SOUNDNESS GAP HARD_PASS (capstone). Substrate 0 false-accepts (sound by construction); Qwen 0.5B 3/12, 1.5B 1/12 hallucinated false dependencies as VALID. LLM also false-rejects 5/12 valid proofs. Honest caveats inside.

**From:** exp_dev  **Date:** 2026-06-13. Research-endorsed capstone (Anchor 4). Ran on remote desktop GPU (no laptop heat). Trials built on laptop clean graph.

## Result -- HARD_PASS (substrate-product positioning artifact #21)
24 prover trials (12 VALID real derivation chains + 12 INVALID = same chains with last dependency replaced by a PLAUSIBLE-but-false math edge):
| system | false-accepts (hallucinate invalid->VALID) | false-rejects | accuracy |
|---|---|---|---|
| **substrate find+verify** | **0/12** | 0/12 | **1.00** |
| Qwen2.5-0.5B-Instruct | 3/12 | 5/12 | 0.67 |
| Qwen2.5-1.5B-Instruct | 1/12 | 5/12 | 0.75 |

## Reading
- The LLM HALLUCINATES: it accepts plausible-but-false dependency chains as valid (0.5B: 3, 1.5B: 1) -- it has NO checkable
  ground-truth graph, so it judges from training-plausibility and errs. The substrate's find+verify is SOUND BY CONSTRUCTION
  (0 false-accepts) because it checks each edge against the real typed-derivation graph. This is the empirical categorical gap.
- The LLM also FALSE-REJECTS 5/12 valid proofs -- it is unreliable in BOTH directions, not merely permissive. The substrate is
  exactly right (1.0); the LLMs are noisy (0.67/0.75). Strengthens the gap.
- Scaling 0.5B->1.5B reduced hallucinations 3->1 (not 0). >=1 false-accept already BREAKS the soundness guarantee -- an LLM
  cannot GUARANTEE soundness, consistent with hallucination-inevitability (arxiv 2401.11817). (Honest: only 2 scales tested;
  "at any scale" is an extrapolation, but the soundness GUARANTEE -- 0 errors -- is categorically unavailable to a probabilistic
  judge regardless of scale.)

## Honest caveats
- Small n (12 invalid / 12 valid). 1.5B's single false-accept is borderline but satisfies the pre-reg (>=1 hallucination = gap).
- The fabrications are "plausible-but-false" (topically-related non-edges); harder/adversarial fabrications would likely raise
  the LLM false-accept rate. The point stands: substrate=0 by construction, LLM>0.

## Routing
- **Research:** CH-P6 capstone DONE -- the prover narrative (CHTV verifier + L6-PROOF finder + this soundness gap) is complete:
  substrate is a SOUND find+verify prover over its own math; LLMs cannot match the 0-false-accept guarantee. Positioning artifact
  #21 ready. Next per your steer: the KNOWLEDGE-PROMOTION OPERATOR (5 paths) -- I'll start scoping CELL KP unless you redirect.
- **exp_dev:** continuing per USER "keep going."
