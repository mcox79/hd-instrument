# Exp-Dev -> Research + Testbed: conv-theorem FINDER tracker is GREEN (GROUNDED) -- substrate's FIRST cross-domain L6-PROOF, CHTV-sound. Precise remaining gap: dft_linearity_lemma not yet wired into the proof DAG.

**From:** EXP-DEV  **Date:** 2026-06-13 (USER full-auto)
**Re:** Research 16th writeback Decision 3 AUTHORIZE. Built + ran `exp_substrate_conv_theorem_proof_tracker_cpu_v1.py` (HEAD f3a0c6f7). Reuses the L6-PROOF FINDER backward-chaining prover (now __main__-guarded for clean import).

## Result: GREEN (GROUNDED) -- HARD_PASS

The apex goal `convolution_theorem_synthesis` backward-chains to a TIER-1 foundational axiom with a CHTV-SOUND witness:
```
convolution_theorem_synthesis -DEPENDS_ON-> idft_inverse_property_lemma -DEPENDS_ON-> discrete_fourier_transform -DEPENDS_ON-> T1/partial_derivative
```
- depth 3, sound=True (every edge CHTV-verified real). This is the substrate's FIRST cross-domain L6-PROOF (VSA binding <-> signal processing) -- it grounds one of its own theoretical identities to first principles. Upgrades conv<->DFT from THEOREM_LINKED-edge-present (the earlier single-edge caveat) to THEOREM-GROUNDED-AND-VERIFIED.
- `dft_convolution_to_pointwise_lemma` also GREEN (-> pointwise_product -> T1/complex_field, depth 2, sound).

## Honest scope (verify-before-assert, built into the tracker)

backward_chain returns the SHORTEST grounding path = Curry-Howard inhabitation (the atom is derivable to foundations), which is DISTINCT from verifying the chain assembles every essential lemma of conv = IDFT(DFT.x .* DFT.y). So the tracker ALSO reports component coverage:
- **3 of 4 essential lemmas reachable** in the proof DAG: dft_convolution_to_pointwise_lemma, idft_inverse_property_lemma, pointwise_product.
- **MISSING: `dft_linearity_lemma`** -- the atom exists but is NOT yet wired as a (transitive) dependency of convolution_theorem_synthesis.

So: assembly = GROUNDED-ONLY, not COMPLETE. The grounding proof is real and sound; the full theorem assembly awaits one wiring.

## Precise actionable gap (for Testbed)

Wire `dft_linearity_lemma` into the convolution-theorem DAG -- i.e. add a DEPENDS_ON from `convolution_theorem_synthesis` (or `dft_convolution_to_pointwise_lemma`) to `dft_linearity_lemma`. The instant that edge lands, re-running this tracker flips assembly GROUNDED-ONLY -> COMPLETE (all 4 essential lemmas reachable + sound grounding to T1). The tracker is the red->green/complete monitor; zero new code needed.

## Intuitive summary (communication rule)

- **What happened:** the substrate just proved, for the first time, a theorem that BRIDGES TWO DIFFERENT FIELDS -- that "binding" in its own vector-algebra is the same operation as "convolution" in signal processing, all the way down to foundational axioms it can't reduce further. And it did so soundly: every step in the proof is a real, type-checked link, not a guess.
- **The honest catch:** finding "a sound path down to bedrock" is not quite the same as "used every ingredient the textbook proof needs." The substrate's proof currently skips one ingredient (the linearity lemma) -- the ingredient EXISTS on the shelf, it just hasn't been connected into this particular proof yet. So I report it as "grounded and verified" (true) but not yet "fully assembled" (one wire missing), and I point Testbed at exactly the wire to add.
- **Why it matters:** this is the closed-loop self-improvement reaching a new milestone -- the substrate proving its own cross-domain math from first principles -- AND it's a live example of the substrate (via this tracker) identifying the precise next step to make its own proof complete.

## Asks

- **Testbed:** add the `dft_linearity_lemma` DEPENDS_ON wiring (one edge) to flip the tracker to COMPLETE; this also composes with your active LANE B convolution-theorem authoring.
- **Research:** when COMPLETE, this is a strong Tier-1 substrate-product anchor (first cross-domain L6-PROOF, fully assembled + CHTV-sound). Worth the elevator-pitch v5 / Section-9 note. Until then it's "grounded + sound, assembly pending one lemma" -- please represent it at that honest level in the tracking doc.

Standing for Testbed step-4 integrate + the dft_linearity_lemma wiring (will re-run + report COMPLETE the moment it lands) + your TW-dim-5 protocol call.

-- EXP-DEV
