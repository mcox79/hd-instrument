# LANDED-VET -- exp_pbv_hypothesis_v1 (SMOKE), 2026-08-12

Auditor: hdi_skunkworks (AUDIT-ONLY; authored nothing under test).
Artifacts: `data/exp_pbv_hypothesis_v1_smoke/{metrics.json,arm_*_detail.json,units.jsonl}`,
log `data/pbv_smoke.log`. Cell `experiments/exp_pbv_hypothesis_v1.py` (31df46c12), prereg
`preregs/2026-08-12_pbv_hypothesis_v1.md` (d4e660550), organs 69bc0223f / 4ce71ceaf.
All numbers below recomputed off the arm detail JSONs with `.venv/Scripts/python.exe`, not read
from `verdict_msg`.

## VERDICT: REFUTED (the build's own primary band). The run is a clean HARD_FAIL.

`metrics.json` carries `"verdict": "HARD_FAIL"`. The log tail the director saw contains only the
SECONDARY block; the primary block is 30 lines above it in the same file.

## 1. PRIMARY BAND -- failed, 2 of 3 bands inside the pre-registered FAIL band

| band | pre-reg edge | FAIL edge | measured | ok |
|---|---|---|---|---|
| P1 C1 abandon (injected WRONG) | >= 0.80 | < 0.60 | **0.285714** (4/14) | NO |
| P2 C2 abandon (injected RIGHT) | <= 0.30 | > 0.50 | 0.214286 (3/14) | yes |
| P3 separation | >= 0.50 | < 0.30 | **0.071428** | NO |

Recomputed from `arm_C*_detail.json -> injection_outcomes.rows`: identical to the reported values.
30 injected per arm, 14 scored, 16 never met a post-injection informative encounter.
Separation = ONE item out of 14 (`neuroscientist`). Fisher exact C1 vs C2 p = 1.0;
C1 95% CI [0.084, 0.581]. There is no signal here in either direction.

## 2. The injection arms -- worse than "the control drifted"

Self-test: injected-wrong 1.0, injected-right 0.0. At corpus scale: 0.286 / 0.214.

Row-by-row the two arms are near-identical. Post-injection informative encounters: C1 sum 50, of
which **50 DISCONFIRM (100%)**; C2 sum 50, of which **46 DISCONFIRM (92%)**. The mechanism's OWN
first proposal is disconfirmed almost as often as a deliberately wrong one. Arm B overall:
7048 DISCONFIRM vs 788 CONFIRM (89.9% disconfirm rate).

Why the rates land where they do: from INJECT_STRENGTH 0.9 with PBV_GAMMA 0.5, abandonment needs
strength <= 0.2, i.e. exactly 3 net disconfirms (0.9 -> .45 -> .225 -> .1125). Rows with >= 3
disconfirms: C1 exactly 4 (= its 4 abandons), C2 exactly 3 (= its 3 abandons). **The abandon rate
is an arithmetic function of how many informative encounters an item got, not of whether the held
hypothesis was right.** That is the analytically-pinned-discriminator failure mode
(2026-07-08 rule), realized.

Downstream effect of injecting 30 hypotheses at 0.9: C1 and C2 bank the SAME 246 lemmas and
differ on 3 objects. The injection barely perturbs the system it is meant to probe.

This is the failure the prereg itself predicted (sec 5.5: many mutually co-occurring anchors ->
per-encounter argmax flips -> thrash) and its named root cause (sec 5.3: the proposer's metric is
distributional relatedness, not reference). Disclosed in advance, then observed.

## 3. Yield: a loss, not a trade -- and it is not 62 concepts

A grounded 305, B grounded 243, but the sets overlap on only **86**. A-only = 219, B-only = 157.
PBV did not decline a 62-item subset; it replaced 72% of the baseline's output.

Independent judge `hdlab.grounded_similarity` (not in the acquisition import closure), scoring
A's OWN object for each lemma:
- kept (A and B both ground): n=86, covered 60, mean 0.1792, median 0.1247
- dropped (A only): n=219, covered 151, mean **0.1911**, median 0.1398
- Mann-Whitney p = 0.508

The dropped set is indistinguishable from the kept set, trending very slightly BETTER. On the 23
shared lemmas where the arms disagree: B better 8, worse 3, tied 2, uncovered 10 (n too small).
B-only additions mean 0.1864 vs all-A 0.1877. **Yield cost bought no measurable correctness.**

## 4. Bands that cannot fail

1. **S2 (median encounters PROPOSE->ABANDON <= 4).** From PBV_INIT_STRENGTH 0.5 with gamma 0.5,
   abandonment occurs after exactly 2 net disconfirms, so the gap has a hard floor of 2 (observed
   min = 2, 950 of 2770 gaps ARE 2). With an 89.9% disconfirm rate the median is pinned at 2-3
   (observed 3.0). S2 measures the author's choice of gamma, not abrupt-vs-smooth switching.
2. **P2 quoted alone.** A mechanism that abandons too LITTLE passes P2 by construction. The prereg
   guarded only the opposite vacuity (abandon-everything passes P1). P3 catches it -- so P2 must
   never be reported without P3, which is precisely how the log tail nearly read.
3. **integrity `arms_must_differ_ok`.** It compares the injection TABLE (30/30 objects differ,
   verified), not arm behavior; it passes while C1 and C2 ground an identical lemma set.
4. **"arm A within +/-2% of the v5-comparable re-run"** (prereg sec 4, a refuse-the-verdict gate)
   was never computed -- `exp_definitional_grounding_v5` has only a `full` run, so no smoke-scale
   comparator exists. A gate that is never evaluated cannot fail.
5. S3 (yield >= 0.25x A) is genuinely failable but so loose a 4x yield collapse would pass it.

Genuinely can-fail and doing work: P1, P3, S1, D2, and the C2 control itself (it DID move).

## 5. Revision quality -- the cell measures it, and it is a clean null

D2 recomputed independently:
- all revised, n=995: better 367 / worse 359 / tied 269, mean delta **-0.000722**, median 0.0,
  95% CI [-0.0161, +0.0146], Wilcoxon p = 0.899, sign-test p = 0.795.
- BANKED-only (what prereg D2 actually specifies), n=38: better 15 / worse 14 / tied 9,
  mean -0.0019, Wilcoxon p = 1.0, sign-test p = 1.0.

Implementation deviation (minor, disclosed here): `revision_quality()` falls back to
`rev["final_obj"]` for unbanked lemmas, so it scored 995 revisions rather than the banked subset
the prereg names. Both slices give the same null.

S1's 31.7% is therefore 31.7% of revisions that, judged by an independent concrete-word norm, are
as likely to be worse as better. The judge is concrete-biased and 367 pairs were uncovered, so
this is weak evidence against quality, not proof of randomness -- but there is zero evidence FOR
quality, and the prereg pre-committed to D2 carrying no verdict either way.

## 6. Context-insensitivity (audit Section G) -- ruling STANDS, its REASONING is challenged

The prohibition holds: this cell measures no sense-selection metric, and nothing here may be
quoted against the C1 swap-drop 0.0100.

But the stated reason ("a missing-hypothesis gap does not predict context-insensitivity") is
weakened by the new data. The swap-drop was measured on `canonicalize` over `np.sum(all traces)`.
This run shows the SAME function, called per-encounter on a single context vector, changes its
argmax on ~90% of informative encounters. Extreme context-insensitivity after summing, extreme
output volatility before it, same argmax and same metric -> the collapse, not the argmax, is a
live candidate cause. Unproven: the volatility may be noise rather than sense-sensitivity.

Discriminator that settles it (one arm, cheap, can fail): scramble the within-encounter context
words and re-measure the per-encounter flip rate. Unchanged flip rate => noise, G stands
unamended. Materially lower flip rate => the context signal is real and the sum is destroying it.

## 7. Is the FULL run warranted? NO.

More data moves the primary band the WRONG way. Abandonment triggers at 3 net disconfirms and the
disconfirm rate is ~90% for right and wrong hypotheses alike, so as encounters per item grow both
arms converge on 1.0. Already visible in the >= 3-informative subset: C1 4/4 abandoned, C2 3/4.
FULL (no per-segment limit, 200 injection targets) buys statistical power for a contrast whose
expected value is shrinking toward zero.

Re-run gate, in order: (a) raise proposer self-consistency -- the confirm rate must move well
above the observed 788/7836 = 0.101 before ANY injection discriminator can separate; (b) then a
smoke whose C1/C2 discriminator actually fires. The prereg's own smoke gate ("a smoke that cannot
fire the discriminator is not a gate") is unmet.

If the director overrides for the yield/quality numbers only, the command is exactly:

    cd d:/AI/hd-instrument && .venv/Scripts/python.exe experiments/exp_pbv_hypothesis_v1.py --mode full --arm all

(smoke wall clock 921 s over 4 arms; full drops the 1500-sentence/segment cap.) Not run by this
role.

## Integrity gates actually evaluated

cardinality_ok true (4/4 arms), segments_ok true (5/5 segments x 1500 sentences each arm),
no_tautology_facts true, no_closed_class_objects true, no_leak_ok true (0 violations any arm) --
all re-verified off the detail files. Judge independence confirmed by import closure.
Per-arm seeds differ (3001/3002/3003/3004) although the cell's header comment claims C1/C2 are
"byte-identical (same seeds)"; the seed reaches only `HDFactStore`, and `ConceptSpace` /
`canonicalize` are seed-free, so the comparison is not confounded -- but there is exactly one
seed's worth of evidence and no variance estimate anywhere in this cell.

## Disposition

HARD_FAIL, substantive (HF_STRUCTURAL_BOUND, not test-design failure): the positive control
direction is intact (the machinery does abandon, 2770 times, and the self-test discriminator
fires on a 2-anchor fixture), so the corpus-scale null is a property of the proposer, not of a
broken harness. WIRE STATUS stays VET_PENDING; no promotion. Revival criterion = the confirm-rate
gate in sec 7.
