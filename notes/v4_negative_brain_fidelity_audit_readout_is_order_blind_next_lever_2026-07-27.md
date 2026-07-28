# v4 self-learning loop: clean NEGATIVE — brain-fidelity audit locates the defect (order-blind readout) + sequenced next lever (2026-07-27)

## What landed
`exp_unified_self_learning_loop_v4` FULL, verdict **MIDDLE_BAND** (data/exp_unified_self_learning_loop_v4/metrics.json).
The comprehension-specific test — does reading coherent correct-concept text beat word-scrambled AND wrong-concept reading on LOW-exposure held-out concepts, via our OWN v2 encoder (ckpt_seed_7) + a DG fast-episodic store — **FAILED, fairly.**
- KEY arm MAIN_fast_episodic LOW gain **0.0015**; SCRAMBLED (matched fast-mode) **0.0015** (tie); WRONG_CONCEPT (matched fast-mode) **0.0068** (correct-reading LOSES). `comprehension_specific_gain=false`.
- Controls run in the SAME `fast_episodic` consolidation mode as the KEY arm (ARM_SPECS L137-138) => apples-to-apples => the negative is FAIR, not a mode-mismatch artifact.
- MAIN_plainavg LOW gain 0.0247 (sustained) has NO matched plain-mode scramble/wrong control -> cannot be claimed as comprehension; by the v3 prior (bag-of-words: scrambled gains as much as coherent) it is almost certainly distributional again. Plain final 0.6047 barely exceeds NO_READ 0.6018 (+0.0029).
- DG pattern-sep barely fired: xsim_dense 0.9869 vs sparse 0.9178, ratio **0.9301** (near 1 => keys barely separate).
- Only real signal is negative-side: WRONG final 0.4648, SCRAM 0.5857 fall BELOW NO_READ 0.6018 => incoherent/wrong reading CORRUPTS; coherent stays ~flat. That is interference/corruption-sensitivity, NOT comprehension-driven acquisition.

**Honest verdict: Leg 3 (learn-from-reading) remains OPEN. v4 is a clean fair negative on comprehension-specific gain. Not banked.** (Independent skunkworks landed-VET in flight to confirm no hidden per-arm/slice signal + confirm the corruption signal isn't a fast-store-overwrite artifact.)

## Brain-fidelity element audit (per USER 07-25 discipline: score EACH element brain-vs-us)
| Element | Brain | Us (v1-v4) | Verdict |
|---|---|---|---|
| 1. Sentence -> meaning (READOUT) | order-sensitive, role-bound proposition (who-did-what-to-what) | `TinyTransformer.pooled` = **mean over token hiddens** = bag-of-contextualized-tokens; then mean over mentions; then fast-read weighted-mean | **THE DEFECT** |
| 2. Write/bind | binds a structured relational fact (litmus-[turns_red_in]-acid), sparse pattern-separated | binds/averages a POOLED centroid (or a pooled trace into a DG key) | wrong content written |
| 3. Consolidate (sleep) | replay proposition, schema-gated integration | sleep fires, consolidates the pooled trace (plumbing OK) | garbage-in |
| 4. Measure | can it USE the fact (answer/infer) | relational-AUC placement + spec_fact probe (spec_fact lacks a clean no-read baseline) | partially right |

## The located defect (mechanistic, not just asserted)
`TinyTransformer.pooled` (exp_scale_..._v2.py L659-665): `summed=(h*keep).sum(dim=1); rep=summed/cnt` -> **mean-pool over token positions.** A word-scrambled sentence has the IDENTICAL token set; self-attention + position embeddings perturb each token hidden, but the MEAN over the window is largely preserved => pooled(coherent) ~= pooled(scrambled). The encoder was MLM-pretrained (order-sensitive signal) but **we discard order at readout.** This compounds through two more mean-pools (over mentions L755; over traces in fast-read L286).

This is NOT a bolt-on-reader problem (invariant: no situation_reader/spaCy). It is OUR OWN encoder's readout, which we own and can change.

## SKUNKWORKS VET (landed, CONFIRMS clean-negative; attribution = MEASURED_MECHANISM not universal-negative)
Independent recompute off metrics.json. Adds three things beyond the Director's read:
- **spec_fact HAS a no-read baseline** (NO_READ/READ_NO_SLEEP LOW 0.6105 / HIGH 0.6773). Reading raises LOW (0.6105->0.6686) but LOWERS HIGH (0.6773->0.6091); coherent-over-scrambled = 0.34sigma, over-no_read = 1.12sigma (within noise), REVERSES at HIGH. Scrambled itself lifts +0.041 over no-read => the lift is concept-PRESENCE, not comprehension. spec_fact does NOT prove acquisition. (Corrects my earlier "spec_fact lacks a baseline".)
- **comprehension_gap (MAIN_fast - SCRAMBLED, LOW) is CONSTANT from cycle0** (0.0177 @ cycle0 == 0.0177 @ final; no upward accumulation). A comprehension effect must GROW with accumulated reading; flat-from-start => immediate corruption-of-incoherent, NOT coherent-teaches. Stronger than the level-comparison.
- **Q4 = a SECOND candidate defect (mention-space collapse):** DIFFERENT concepts' DENSE mention-encodings sit at **0.987 cosine** (near-degenerate); DG expansion only -> 0.918. The fast store is fed near-collapsed keys => cannot retrieve concept-specifically. VET names this a strong candidate PRIMARY cause of the null. Readout-over-noread margin also GROWS with exposure (LOW +0.0015 < HIGH +0.0184 < ALL +0.0302) -- backwards for "teaches new low-exposure." On ALL slice scrambled +0.0305 ~= coherent +0.0302 (v3 distributional result reproduced).

## TWO candidate defects (both readout/representation-level, both plausibly cheap)
- **(A) order-blind READOUT (within-concept):** mean-pool over tokens => pooled(coherent) ~= pooled(scrambled) (identical token set). My hypothesis.
- **(B) cross-concept anisotropic COLLAPSE (between-concept):** raw mention-reps at 0.987 cross-concept cosine (VET Q4). LIKELY an anisotropy artifact -- the scale-eval (29591) that BEAT grounding used z-avg / standardization (mu-subtract + L2); but the fast-store read (_fast_episodic_read / _sparse_keys) consumes RAW reps, so it operates in the collapsed cone where DG can't separate. Candidate cheap fix: common-mode/anisotropy removal (center+standardize) BEFORE the fast-store key projection, matching what the eval does.
H (to measure, NOT assert): (A) and/or (B) cause the null. v4 is CONSISTENT but does not isolate them. The v3-drill over-read once each direction; do not repeat it. **STEP 0 measures BOTH: coherent-vs-scrambled cosine = (A); coherent-vs-wrong cosine = (B) [wrong = a different concept]; + does centering drop the cross-concept cosine.**

## NEXT LEVER — sequenced, brain-faithful, own-mechanism, can-fail
**STEP 0 (cheap decisive diagnostic — a probe, NOT a full cell):** on the v2 encoder over a sample of held-concept mentions, measure cos(pooled(coherent), pooled(scrambled)) and cos(pooled(coherent), pooled(wrong)). Predict coherent~=scrambled (cos near 1) => readout order-blind, H confirmed. In the SAME probe, test an ALTERNATIVE order-sensitive readout on the SAME frozen encoder (candidates below) and show it separates coherent from scrambled. Decision gate: if the alt readout separates coherent<->scrambled while mean-pool does not, the fix is "change the readout" (high confidence, cheap). If mean-pool ALSO separates them, H is wrong and the defect is downstream (metric/store) -> re-diagnose.

### STEP 0 RESULT (LANDED 07-27, hypothesis CONFIRMED) — data/probe_v4_readout_order_sensitivity_v1.json
Frozen ckpt_seed_7, 40 held concepts, 120 (coherent, scrambled, wrong) triplets. Self-tests passed (scramble preserves multiset+changes order 120/120; wrong=derangement).

| readout | coh-vs-scram | coh-vs-wrong RAW | coh-vs-wrong CENTERED |
|---|---|---|---|
| MEAN_POOL (current) | **0.9944** | 0.9444 | -0.0645 |
| BIND_HRR_position (**v5 pick**) | **0.7304** | **0.4848** | -0.0258 |
| LAST_TOKEN | 0.8428 | 0.8624 | -0.0307 |
| MAX_POOL | 0.9754 | 0.9261 | -0.0323 |
| CONCAT_FIRST_8 | 0.7399 | 0.6994 | 0.0123 |

- **(A) CONFIRMED order-blind:** mean-pool coh-vs-scram 0.9944 ~= 1.0; MAX_POOL 0.9754 too => it's the POOLING permutation-invariance, not the mean operator.
- **(B) CONFIRMED = anisotropy (cheap), NOT encoder incapacity:** raw cross-concept 0.9444 -> -0.0645 after mean-centering. Encoder CAN discriminate concepts; the fast-store write path just never removed the common mode. Reuse existing `LOOP2._apply_common_mode`.
- **v5 readout pick = BIND_HRR_position** (hdlab.binding.bind, fixed per-position role ⊗ token-hidden, summed over non-pad): wins BOTH axes at once (lowest coh-vs-scram 0.7304 AND lowest coh-vs-wrong-raw 0.4848). Own-mechanism, no bolt-on reader.
- **CAVEAT (do NOT over-read):** this is REPRESENTATION separation, NECESSARY but not SUFFICIENT for comprehension-LEARNING GAIN. 0.7304 is MODEST order-separation (bind still sums over shared tokens). v5 FULL comprehension test settles it; VET the positive HARDEST.

### v5 FULL RESULT (LANDED 07-28 ~00:30Z) = MIDDLE_BAND — mechanism progress, NOT a pass (VET'd honest)
data/exp_unified_self_learning_loop_v5/metrics.json (elapsed 935s single-seed-7).
- **Readout works at scale (confirmed on REAL ckpt):** coh~scram 0.7719, coh~wrong 0.5018, order_sensitive_fires=TRUE, discriminative_fires=TRUE. The order-blindness IS removed.
- **Direction flipped correct vs v4:** FAST_LOW gain 0.0051 (POSITIVE; v4 was 0.0015) BEATS scrambled 0.0001 AND wrong-concept 0.0036 => comprehension_specific_gain flipped FALSE(v4)->TRUE(v5).
- **BUT NOT learning-from-reading (why MIDDLE_BAND is correct+honest):** (1) magnitude 0.0051 is FAR below the +0.02 acquisition bar => low_sustained=FALSE, teaches_new=FALSE. (2) The margins the TRUE flags ride on (fast-vs-wrong = 0.0015) are within noise (LOW_nq=172) — do NOT over-read the boolean. (3) contrast=FALSE: HIGH gain 0.0341 >> LOW gain 0.0051 — reading helps ALREADY-KNOWN concepts far more than NEW ones = distributional ACCUMULATION, not novelty-driven comprehension (the v3 story at aggregate, with only a whisker of comprehension-ordering at LOW). (4) low_retention=FALSE.
- **CONCLUSION:** order-blindness was A blocker (now removed, direction corrected) but NOT the whole gap. Remaining: reading barely moves the metric (0.005) + what moves favors known-not-new. Deeper fixes needed: metric may under-see comprehension (D), consolidation still averages (C), or need the learned extraction head (B/v6). NOT banked.

**STEP 1 (v5 — STEP 0 confirmed H): structure-sensitive readout via our OWN encoder, no bolt-on reader.**
- (a) substrate-NATIVE bind readout: bind position/role ⊗ token-hidden and sum via HRR/FHRR (the substrate's core primitive) -> order-sensitive by construction; pure own-mechanism. Cheapest.
- (b) small learned attention/readout head emitting a (relation,object)-structured rep, self-taught from the foundation's own 1.24M typed edges (foundation = supervision; brain-faithful self-teacher = the R3/R4 move applied to comprehension).
- Start (a). One variable: readout = mean-pool vs bind, holding encoder+store+measurement fixed. Re-run the SAME v4 comprehension test. HARD-PASS = coherent LOW gain beats BOTH matched-mode scrambled AND wrong-concept.

**STEP 2 (v6): learned extraction head self-taught from foundation edges — the general own-comprehension mechanism.** Consolidate the BOUND proposition (not a centroid); add a spec_fact probe WITH a no-read baseline so acquisition is provable.

## Discipline notes
- v4 negative is FAIR + mechanistically diagnosed -> not defeatist: the brain does this, the gap is LOCATED (order-blind readout), the fix is our own readout. Iterate.
- Route-by-flavor: this is a MISSING PRIMITIVE (rep can't express a structured proposition from text) -> BUILD the primitive (bind readout) by hand first, THEN hand rule-learning to the loop (learned extraction head).
- Do NOT assert H as confirmed until STEP 0 measures it. Do NOT bank v4. VET the STEP-1 positive HARDEST (active-control GAIN not level).
