# context_vector_signal_v1 -- does the per-encounter context vector carry signal? 2026-08-12

Cell `experiments/exp_context_vector_signal_v1.py`; pre-reg
`preregs/2026-08-12_context_vector_signal_v1.md` (filed BEFORE any run; amendments A1/A2 in its
sec 13, filed after SMOKE and before FULL, both disclosed with the unamended outcome preserved in
metrics as `prereg_literal_primary` / `prereg_literal_secondary`).
Metrics: `data/exp_context_vector_signal_v1/metrics.json` (FULL, run_mode=full, elapsed 216.9s),
`data/exp_context_vector_signal_v1_smoke/metrics.json` (SMOKE).
Author: hdi_exp_dev. MEASUREMENT ONLY -- nothing in `hdlab/reading_grounding_loop.py` or
`hdlab/grounding_acquisition_loop.py` was modified.

Prior-work check (`tools/substrate_query.sh`): top-5 hits all at cosine 0.2793, below the 0.30
threshold. NONE at cosine > 0.30. Genuinely novel, not a rediscovery.

## VERDICT: the director's hypothesis is REFUTED -- the context vector is NOT noise. But its signal is not USABLE by the current read-out, which is where the diagnosis now goes.

## 1. What was verified off disk before designing

* `data/exp_pbv_hypothesis_v1_smoke/metrics.json` carries `"verdict": "HARD_FAIL"`, verdict_msg
  primary bands C1 0.285714 / C2 0.214286 / separation 0.071428. Confirmed.
* `arms.B_PBV.trajectory`: n_disconfirm 7048, n_confirm 788 -> disconfirm share
  7048/7836 = 0.8994. Confirmed. The landed-VET's arithmetic is sound.

## 2. Design

Encounters are the REAL reading loop's OWN, recovered from `state.evidence` + `sentence_pool` and
proven bit-identical to the stored `trace.context_vec` for every one of 8282 encounters
(`trace_alignment_ok`). Five context conditions score the IDENTICAL encounter set through the
UNMODIFIED `canonicalize_fast` against the SAME anchor space (batched argmax verified equal to
`canonicalize_fast` on 200 sampled encounters, 0 mismatches). Two regimes: PER-ENCOUNTER and
TRACE-SUM (`np.sum([t.context_vec for t in item.traces])`, reading_grounding_loop.py:567).

Primary null = SCRAMBLE_SENT: a DIFFERENT encounter's real context window, re-masked. It is the
only geometry-matched null -- the encoder is a permutation-invariant bag-of-content-words bipolar
bundle, so swapping which real sentence supplies the window preserves norm/sparsity/word-frequency
statistics exactly and removes ONLY the lemma<->context association. Empirically vindicated:
SCRAMBLE_SENT reproduces REAL's cosine distribution to 4 decimals (sec 4), which SCRAMBLE_WORD
does not. A within-lemma shuffle would NOT be a valid null (flip rate over a fixed multiset is
near-invariant to ordering, so it could not fail) and was not used.

## 3. PRIMARY -- per-encounter regime (FULL: n=8282 encounters, 4467 lemmas, 898 eligible anchors)

| arm | flip rate | 95% CI (cluster bootstrap over lemmas, 2000x) | modal share | argmax in own window |
|---|---|---|---|---|
| REAL | **0.7830** | [0.7646, 0.8003] | 0.7878 | 0.2871 |
| SCRAMBLE_SENT (primary null) | 0.9984 | [0.9970, 0.9995] | 0.7127 | 0.0050 |
| SCRAMBLE_WORD | 0.9948 | [0.9922, 0.9971] | 0.7136 | 0.0066 |
| LESION_RANDOM (noise ceiling) | 0.9990 | [0.9979, 0.9998] | 0.7125 | 0.0013 |
| LESION_ZERO (**cannot fail**) | 0.0000 | [0, 0] | 1.0000 | 0.0000 |

**D = flip(SCRAMBLE_SENT) - flip(REAL) = +0.2155, 95% CI [+0.1982, +0.2332], 100% of bootstrap
replicates above zero.** Against LESION_RANDOM, D = +0.2160 [+0.1988, +0.2344]. The pre-registered
CONTEXT_CARRIES_SIGNAL band (D >= 0.10, CI excluding 0) is cleared with room to spare, and the
CONTEXT_IS_NOISE band (D < 0.05, CI covering 0) is not remotely approached. Result reproduces at
SMOKE (1/7.5 the corpus): D = +0.2287 [+0.2042, +0.2543].

Argmax IDENTITY agreement, chance-corrected (Cohen-kappa style; raw agreement alone is
uninterpretable at 898 anchors):

| pair | raw | chance | kappa |
|---|---|---|---|
| REAL vs SCRAMBLE_SENT | 0.0022 | 0.0021 | **+0.0001** |
| REAL vs SCRAMBLE_WORD | 0.0053 | 0.0018 | +0.0035 |
| REAL vs LESION_RANDOM | 0.0006 | 0.0011 | -0.0005 |

REAL and the null pick essentially never the same anchor. So the flip-rate gap is not an artifact
of the arms sharing choices -- they are genuinely different read-outs, and REAL's is the stable one.

## 4. The sharpest finding: the COSINE MAGNITUDE carries ZERO signal

| arm | informative rate (cos >= 0.30) | sense-match rate (cos >= 0.45) | mean best cos |
|---|---|---|---|
| REAL | 0.416687 | 0.107221 | 0.311340 |
| SCRAMBLE_SENT | 0.416807 | 0.107221 | 0.311326 |
| SCRAMBLE_WORD | 0.194035 | 0.007003 | 0.250701 |
| LESION_RANDOM | 0.000725 | 0.000000 | 0.190207 |

REAL and SCRAMBLE_SENT are **identical to four decimal places on all three**. A context window
belonging to a completely different lemma clears `PBV_INFORMATIVE_MIN`=0.30 and
`SENSE_MATCH_THRESH`=0.45 at exactly the same rate as the true one.

This is load-bearing for PBV. `make_pbv_fns` uses the cosine to decide whether an encounter is
INFORMATIVE at all, and that gate is provably blind to whether the context is the lemma's own.
ALL the lemma-specific information lives in argmax IDENTITY; NONE of it lives in the score.
LESION_RANDOM's 0.190 mean matches the THEORETICAL max-of-898 draws at cosine SD = 1/sqrt(256) =
0.0625 (~3.0 SD), so the geometry is behaving as expected and the harness is sound.

## 5. SECONDARY -- trace-sum regime, and it does NOT collapse the way the VET proposed

| arm | summed sense-match rate | mean best cos | top-1 anchor share |
|---|---|---|---|
| REAL | 0.2216 | 0.3540 | 0.1119 |
| SCRAMBLE_SENT | 0.2854 | 0.3654 | 0.1854 |
| LESION_RANDOM | 0.0936 | 0.2544 | 0.1169 |

REAL vs SCRAMBLE_SENT trace-sum argmax agreement: raw 0.0663, kappa 0.0446 -- the summed answer
still DEPENDS on which contexts went in, so it is **not** a single generic attractor. Prefix-sum
flip rate (argmax of the running sum as traces accumulate): REAL **0.7148** [0.6952, 0.7343] vs
SCRAMBLE_SENT **0.9413** [0.9271, 0.9536]. Summing therefore HELPS slightly (0.7830 -> 0.7148) and
widens the real-vs-null gap (D_prefix = +0.2265).

Verdict TRACE_SUM_ALIVE. **The trace-sum collapse is not the root cause.** The per-encounter
separation the VET hypothesised was being destroyed by the sum is in fact largely preserved by it.

But one number in that table is a genuine pathology and should not be smoothed over:
`trace_sum_separation = -0.0638`. Summing a lemma's OWN contexts yields a vector that clears
SENSE_MATCH_THRESH **less** often (0.2216) than summing UNRELATED contexts (0.2854), and the
scrambled sums concentrate harder on a single anchor (top-1 share 0.1854 vs 0.1119). Reading:
the anchors are themselves accumulated context sums, so the anchor pool is biased toward the
corpus FREQUENCY BACKBONE; a scrambled sum regresses toward that backbone and therefore matches
it well, while a genuinely lemma-specific sum points somewhere no anchor lives. The read-out
rewards genericity and penalises specificity. That is an architecture-level defect in the
comparison pool, not in the context vector.

## 6. A THIRD cause the framing did not name: ANCHOR-SPACE GROWTH

Re-scoring each encounter against the ConceptSpace snapshot from its OWN curriculum segment
(5 snapshots at FULL) instead of the final space:

| arm | fixed final space | segment-snapshot space |
|---|---|---|
| REAL | 0.7830 | **0.8569** [0.8431, 0.8706] |
| SCRAMBLE_SENT | 0.9984 | 0.9990 |

Anchor-space growth contributes ~+0.074 of additional instability, and PBV ran against a space
that grew at every encounter -- finer-grained still. Reconciliation with the measured PBV
disconfirm rate: 0.783 (context-vector-intrinsic) + ~0.074 (space growth) + residual live-space
drift lands right on arm B's 0.8994. **The ~90% disconfirm rate is fully accounted for without
needing the context vector to be noise.** D under the snapshot space is still +0.142, above the
pre-registered 0.10 signal band, so the finding survives the more realistic regime.

## 7. Positive control and scope

`REAL informative_rate` = 0.416687 vs arm B's MEASURED `informative_encounter_rate` 0.393912
(`data/exp_pbv_hypothesis_v1_smoke/metrics.json:arms.B_PBV.trajectory`): deviation 0.0228, inside
the pre-registered 0.10 tolerance. The regimes match on the load-bearing quantity.

**Scope caveat, stated plainly.** This cell runs the arm-A (non-PBV, `revive_terminal=False`)
reading path, so its encounter population is 8282 encounters / 4467 lemmas against arm B's 31045 /
6925 -- arm B keeps terminal items accumulating traces, this one does not. Same organs, same
corpus, same 7500-sentence stream, same 1500/segment cap. The context-vector construction and the
`canonicalize_fast` read-out are byte-identical between them, and the positive control above
confirms the regimes agree; but the encounter POPULATION differs and no claim here is a direct
re-measurement of arm B's own encounters.

## 8. Controls that cannot fail -- declared

`LESION_ZERO` is pinned at flip rate 0.0000 and informative rate 0.0000 by construction (a
zero-norm probe makes `canonicalize_fast` self-return). It is a harness sanity check with NO
verdict weight; the inferential lesion is `LESION_RANDOM`, which can and does move. Everything
else (SCRAMBLE_SENT, SCRAMBLE_WORD, LESION_RANDOM, both D bands, both trace-sum bands) can fail.

Two pre-registered bands were found MIS-SPECIFIED at smoke and amended before FULL, both
disclosed in prereg sec 13 with the unamended outcomes preserved in metrics: (A1) the ceiling
guard fired on the null arm alone, so it could only ever suppress a positive and never rescue a
null -- and its stated premise ("no room for REAL to be more stable") was directly falsified by
the data; amended to require BOTH arms pinned. (A2) TRACE_SUM_ALIVE was written backwards (high
real-vs-scramble agreement is the DEAD signature, not the alive one), making ALIVE unreachable;
amended to input-dependence plus separation. A1 moves the verdict TOWARD refuting the director,
i.e. away from the answer the task leaned toward; it is recorded so that can be audited.

## 9. What this means -- honestly, in both directions

**BAD news for the one-root-cause story.** The three walls do NOT collapse into "the context
vector is noise". It is not noise; D = +0.2155 with a CI nowhere near zero, replicated at two
scales, against three independent nulls.

**But the director's operational instinct is still half right.** REAL's flip rate is 0.7830 --
the argmax changes on 78% of consecutive encounters (86% under the live-ish space). A
propose-then-verify mechanism whose verifier is `encounter_best == hypothesis.obj` cannot function
on a read-out that unstable, no matter how real the underlying signal is. PBV was built
correctly; it was handed a read-out with a genuine signal buried under an argmax over ~900
near-tied anchors at d=256 where the cosine noise SD is 0.0625.

**Where the diagnosis should go next** (all three are read-out defects, not encoder defects):
1. **The informativeness gate is blind.** Sec 4: cosine magnitude is identical for real and
   scrambled context. Gating on `cos >= 0.30` filters nothing lemma-specific. A margin-based
   gate (top-1 minus top-2, or a per-lemma z-score against that lemma's own anchor-score
   distribution) is the obvious replacement and is cheap to test.
2. **The comparison pool rewards genericity.** Sec 5's negative separation: anchors are
   frequency-backbone-biased, so specific vectors score worse than generic ones. Frequency-
   correcting the anchor pool (or comparing against a lemma-conditioned rather than global pool)
   is a structural fix.
3. **Anchor-space growth adds ~0.074 instability** (sec 6) and is straightforward to remove by
   freezing or versioning the comparison pool within a verification episode.

Only item 3 was named in any prior framing. Items 1 and 2 are new and are, on this evidence, the
larger share of the problem.

## 10. Wire status

`MEASUREMENT_ONLY_NO_WIRE`. Nothing here is a capability to promote; it is a diagnosis of an
existing one. No registry entry claimed.
