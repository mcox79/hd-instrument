---
priority: 3
review:
review_text:
---

# PROBLEM: every reader consumer gates on a HARD 1-best POS tag, but the tagger's single biggest error class is PROPN↔NOUN (28% of ALL tagger errors, measured UD-EWT gold) — a referential/world-knowledge call surface form cannot make — and it lands squarely in `referent_per_np`'s NP/entity/name detection (a NOUN mistagged PROPN, or vice versa, opens the wrong discourse referent / mis-clusters a name), corrupting who-did-what + coref downstream. The brain does NOT commit to one tag then propagate the error; it keeps a GRADED, ranked-parallel lexical-category belief that top-down evidence (the situation model / coref) re-ranks. The POS-tagger speedup (owner-DONE) made the calibrated forward-backward POSTERIOR (P7's CRF representation) AFFORDABLE — cheaper than the hard 1-best we ship. WIRE the highest-leverage consumer (`referent_per_np` NP-head detection first) to consume the GRADED posterior uncertainty-aware: where P(PROPN) and P(NOUN) are close, let coref/entity evidence pick, instead of a brittle argmax — and MEASURE the who-did-what / coref / entity gain, info-free (shuffled-posterior) twin LOSING. Or a located negative naming why the graded posterior cannot beat the 1-best on the live consumer.

**slug:** `consume_the_graded_pos_posterior_uncertainty_aware_starting_with_referent_np_detection` — **opened:** 2026-09-04 by the strategy session, the explicit follow-on the owner-DONE `optimize_the_pos_tagger_viterbi_inner_loop_the_co_dominant_read_cost` named (the graded decode is now cheaper than the 1-best; the PROPN↔NOUN error is 28% of tagger errors + lands in referent_per_np). **status:** OPEN. Strategy lands any hdlab wire (Q111, witnessed). Glass-box, NO external LLM.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25/26)
> **DO THE RIGHT THING, NOT THE CHEAP THING.** The mission is the most brain-faithful substrate. A located NEGATIVE is a PASS — but only if the brain's actual mechanism, faithfully built, is what failed.

> ## 🧠 BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar — work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN — how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure — do not build the tractable thing and cite neuroscience after.
> 2. **REUSE — does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE — does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly — copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components — that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.

## 1. THE PROBLEM IN PLAIN LANGUAGE
The reader labels each word's part of speech and then treats that label as certain. Its most common mistake is confusing a proper name (PROPN) with a common noun (NOUN) — about a quarter of all its labelling errors — and that exact mistake decides which words the reader treats as characters/entities, so it quietly corrupts "who did what" and "who is who". A real reader doesn't lock in one label and run with it; it holds a couple of ranked possibilities and lets the rest of the sentence and the story so far settle the hard cases. We just made the tagger fast enough that producing those ranked possibilities (a calibrated posterior) is now CHEAPER than the single-guess version we use. The job: feed the ranked possibilities into the entity/name detector so that, when name-vs-noun is a close call, the coreference and entity evidence decides — and show it improves who-did-what / coref.

## 2. WHY THIS ONE — it is now AFFORDABLE and attacks a measured 28%-of-errors wall
The POS-tagger speedup (owner-DONE, this session) proved the graded ranked-parallel decode (Viterbi 1-best + forward-backward posterior = P7's landed `hdlab/crf_tagger` representation) runs at 0.632s vs the stock hard-1-best 1.099s — the ~5x headroom makes the brain-faithful graded decode cheaper than what we ship. The measured error decomposition (UD-EWT gold, 24,120 tok): 85% of tagger errors touch a content class, PROPN↔NOUN is 28% of ALL errors, and that is precisely the call surface form can't make (it needs referential/world knowledge). It lands in `referent_per_np` (now DEFAULT-ON) — the NP-head/name detection that opens discourse referents + seeds clusters — so a graded, coref-informed resolution is the highest-leverage first consumer.

## 3. HOW THE BRAIN DOES THIS (the opening move)
PINNED: lexical category is a GRADED, calibrated belief maintained in ranked-parallel, resolved by top-down context (Kuperberg-Jaeger 2016; the calibrated CRF posterior = P7; interactive-activation top-down re-ranking — McClelland-Rumelhart). PROPN vs NOUN is a referential distinction the perceptual form underdetermines → it is settled by the discourse/entity model (does this token participate in a coref chain / act as an agent?). OUR-INVENTION-under-test: the exact uncertainty gate (posterior-margin threshold), the coref/entity evidence used to break the tie, the re-rank rule. Sweep, do not adopt. REUSE: `hdlab/crf_tagger.vpost`/`vlogit` (the landed calibrated posterior), `hdlab/referent_per_np.py` (the NP-head/name detection to make uncertainty-aware), the reader's coref/entity model.

## MEASURED vs INFERRED
- **MEASURED (do NOT re-derive):** PROPN↔NOUN = 28% of ALL tagger errors, 85% of errors touch a content class (UD-EWT gold, 24,120 tok, the POS-tagger SOLVED §chain); the calibrated CRF posterior is landed (`hdlab/crf_tagger`, AUROC 0.94) + now affordable (the tagger speedup); `referent_per_np` is DEFAULT-ON and its NP/name detection gates on the hard 1-best UPOS.
- **INFERRED (you must measure):** whether feeding the graded posterior into `referent_per_np` NP-head/name detection (uncertainty-aware: where P(PROPN)≈P(NOUN), let coref/entity evidence decide) improves the live who-did-what / coref_acc / entity metrics CI-separated, with a shuffled-posterior info-free twin LOSING and no regression on the confident-tag majority; the residual + its named cause.

## VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: `python tools/substrate_map.py`, `python tools/reader_capabilities.py`; read the POS-tagger `SOLVED.md` + `BRAIN_FOUNDATIONAL_CHAIN_FINDING.md` (the error decomposition + the graded-decode timing) IN FULL; read `hdlab/crf_tagger.py` (`vpost`/`vlogit`), `hdlab/referent_per_np.py` (`_content_head_positions`/`frame_heads` — where UPOS gates NP/name detection), `hdlab/situation_reader.py` (`_cached_tag`, the coref/entity path).
- Reproduce first-hand: the PROPN↔NOUN error rate on a few docs, and where `referent_per_np` opens a referent off a PROPN vs NOUN call.

## THE BAR (can-fail; CI-separated; the info-free twin must lose)
PASS = an uncertainty-aware consumer (the graded CRF posterior → `referent_per_np` NP/name detection, tie-broken by coref/entity evidence; glass-box, NO LLM) that improves the live who-did-what and/or coref_acc CI-separated with a shuffled-posterior twin LOSING and NO regression on confident tags. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the graded posterior cannot beat the 1-best on the live consumer, with the named cause + number — is a FULL PASS. Strategy lands the Q111 wire.

## ALREADY TRIED / DO NOT REDO
- The tagger CALIBRATION is SOLVED (`upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior`, `hdlab/crf_tagger`) and the tagger SPEED is SOLVED — this is the CONSUMPTION of the graded posterior, a new axis (do not re-derive the posterior).
- The JOINT tag↔parse decode is a LOCATED NEGATIVE (P7) — it regressed without top-down meaning. This is NOT joint decode; it is uncertainty-aware CONSUMPTION by a downstream discourse consumer.
- Do NOT flip the hard 1-best tag globally (that changes every consumer's input — byte-safety); gate the graded consumption at the NP/name decision.

## FILES AND ENTRY POINTS
Build in `experiments/` + `verification/`. REUSE `hdlab/crf_tagger.py`, `hdlab/referent_per_np.py`, `hdlab/situation_reader.py`. Measure on the board's who-did-what + coref arms with `referent_per_np` on. Strategy lands the Q111 wire. Fold an AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.

## DO NOT QUOTE
- Do NOT quote the 28% PROPN↔NOUN as the board gain — it is the error share; report the live who-did-what / coref recovery.
- Do NOT quote a gain without the shuffled-posterior twin losing (else it is the coref evidence alone, not the graded tagger signal).
- Do NOT use an external LLM (the invariant).
