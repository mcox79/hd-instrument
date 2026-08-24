---
owner_verdict: DONE
---

PROBLEM: the_gate_cannot_measure_its_own_floor
STATUS: SOLVED  (the floor is measured in the gate's own harness, the guard is proven, the past
result is re-graded; the one-line-plus-arm edit to the tool is a PROPOSED diff, out of solver
scope, for the strategy session to land)
LEDGER: python tools/problem_ledger.py --check  ->  SOLVED, malformed/incomplete: 0

WHAT WAS ASKED
We grade "did the system understand this?" against a deliberately dumb spell-checker baseline. That
baseline turned out to be ~78% cheating on words that are merely spelled alike (nation/national). One
of our two graders (tools/per_row_gain_c3_vet_v1.py) owns no spell-checker arm of its own -- it only
ever borrowed the number -- so once the answer key was cleaned it had no honest floor and HONESTLY
REFUSED TO GRADE rather than gate against a number it knew was wrong. Give it the ability to measure
its own floor, prove a guard that refuses if that number ever drifts, and re-grade the past result.
THE TRAP TO AVOID: do not paste the sibling tool's fixed number across -- the two graders build and
score their test items differently, and no number crosses scorers or populations.

WHAT I BUILT (I did NOT edit the tool -- solver scope forbids it; I proved the mechanism and hand back
the exact diff)
  - experiments/exp_per_row_gain_trigram_floor_calibration_v1.py -- measures the floor IN the gate's
    OWN harness. It does not reconstruct the harness; it imports the tool's own _gold and
    build_excitability_E, the same C3 corpus/space/items, the same MS.trigram_matrix, and the same
    bootstrap seed (MASTER_SEED+51). It adds the trigram floor arm, two information-free twins of it,
    the recompute-and-refuse guard, and a leaky-vs-honest re-grade of every arm.
  - verification/test_the_gate_can_measure_its_own_floor.py -- scaffold-free witness, 5/5 PASS, exit 0.

THE HARNESS-IDENTITY CHECK IS THE LOAD-BEARING PART
The brief's whole warning is that a number right in one harness is wrong in another. I did not assume
the two harnesses agree -- I proved it: A1_BASE = 0.04575 and self_retrieval = 0.755853 both reproduce
THIS harness to 1e-9, and n_anchors=5491 / n_items=4000 are identical to the landed run. ONLY because
that identity holds is it legitimate that the floor coincides with the sibling's value. It was
MEASURED here, not pasted; the coincidence is the confirmation, not the shortcut.

THE NUMBERS (n=4000, the gate's own population, morphology-stripped gold)
  quantity                              value    CI                  width / null
  A6_TRIGRAM_ONLY  (THE FLOOR)          0.0195   [0.01525, 0.024]    half-width 0.004375
  A1_BASE          (the real read-out)  0.04575  [0.0395, 0.05225]   half-width 0.006375
  info-free twin: donor-query          0.008    [0.00525, 0.01075]  null p95 = 0.01025
  info-free twin: row-permuted         0.011    [0.008,   0.01425]  null p95 = 0.01375

THE FLOOR IS A REAL SIGNAL, NOT NOISE. Its lower CI bound (0.01525) sits above both twins' null p95,
and the paired deltas exclude zero: floor - donorq = +0.0115 CI [+0.0063,+0.0168]; floor - rowperm =
+0.0085 CI [+0.0030,+0.0140]. So the gate CAN separate things at this level -- it is a usable floor.

THE RE-GRADE FLIPS THE VERDICT THE LEAKY FLOOR GAVE (both numbers side by side)
                       leaky floor (old)                 honest floor (new)
  floor value          0.0870  CI [0.0783, 0.096]         0.0195  CI [0.01525, 0.024]
                       (unstripped, ~78% leakage)         (morphology-stripped)
  A1_BASE read-out     0.048 -> APPEARS TO LOSE           0.04575 -> BEATS spelling, CI-separated
                       (0.048 < 0.087)                    (ci_lo 0.0395 > 0.024)
For the whole thread the read-out "lost to a spell-checker" (0.048 vs 0.087), and that steered the
project. On a FAIR test it WINS (0.04575 vs 0.0195, CI-separated) -- though it is still a weak reader
in absolute terms (4.6% hit@1). Read it as "beats spelling", not "reads well". THIS DIRECTION WAS
ALREADY REPORTED by the sibling harness (exp_c3_surprise_weighted_vs_bundling_v1 and the existing
witness test_removing_the_bundle_helps...); my contribution is confirming it in THIS gate's harness
with the floor measured here and the gate made honest. Credit, not a new claim.

AND THE MECHANISTIC VERDICT THE TOOL EXISTS FOR IS UNCHANGED: per-row multiplicative gain still adds
nothing -- 5 gain arms bitwise identical to base, 2 dim arms change picks but not accuracy, every
delta-vs-base CI includes zero. The re-grade corrects the FLOOR comparison; it does not resurrect the
gain hypothesis.

THE GUARD, AND ITS POSITIVE CONTROL (I made it fire)
void_plumbing_check recomputes the floor in-harness and refuses (void=True) unless the constant
matches to 1e-9, A1_BASE reproduces the stripped headline, and self-retrieval clears its floor. At
full power: FIRES on the wrong constant 0.0870 (void=True), PASSES on the measured 0.0195 (void=False).

CONTROLS (what each EXCLUDED)
  - donor-query twin 0.008           -> excludes "the floor is target-form noise"
  - row-permuted twin 0.011          -> excludes the same from the other side
  - known-answer self-retrieval 0.756 -> excludes a broken scorer
  - guard positive control            -> excludes a silently-drifted constant
  - harness-identity A1_BASE to 1e-9  -> excludes "measured on a look-alike population"
  - leaky-floor negative control      -> the arm that clears the honest floor does NOT clear the leaky
                                         0.096, so the flip is real, not a metric artifact

BRAIN STRUCTURE (asked in the brief and by the owner): replicating vs substituting
Two things live here on opposite sides of the fidelity line, and conflating them would be inventing
neuroscience for a spreadsheet.
  - The GRADING GATE ITSELF is bookkeeping, NOT a brain mechanism. The brain does not gate its own
    read-outs against a bootstrapped orthographic null. I refused to dress it up. OUR-INVENTION.
  - The DISSOCIATION it encodes IS real: the trigram floor models the orthographic / visual-word-form
    route (form, no meaning); the graded thing is the anterior-temporal-lobe semantic hub read-out of
    a distributed code. That is the dual-route model of reading; surface/deep dyslexia dissociate
    exactly there. Both routes PINNED; our VSA read-out of the semantic route is OUR-INVENTION-UNDER-
    TEST. The morphology we strip (nation/national) is itself a brain fact (morphological
    decomposition), so a form route SHOULD win those without meaning, and stripping them is the
    correct way to isolate the semantic route. PINNED.
  - Honest content: the semantic read-out (0.04575) now beats what the pure form route can do
    (0.0195), CI-separated. Small, but the right direction, and it is Phase-1 (meaning-supply)
    relevant.

PROPOSED DIFF to tools/per_row_gain_c3_vet_v1.py (NOT landed -- three hunks, each mirroring the
already-landed sibling score_space_gain_and_topk_ci_v1.py; full text in SOLVED.md)
  (1) Set the measured constant, replacing lines 73-74:
        ORTHO_BAR = 0.019500 ; ORTHO_BAR_CI = (0.015250, 0.024000)   # measured HERE, licensed by the
        identity check; coincides with the sibling because the population is provably the same.
  (2) Add the A6_TRIGRAM_ONLY floor arm (the tool already imports MS): build
        t_mat, t_cov = MS.trigram_matrix(anchors) once, score sc = t_mat[sel] @ t_mat[pos[L]] per
        item exactly as the sibling does, include it in the bootstrap, keep it OUT of gain_arms.
  (3) Replace the refusal block (lines 266-281) with a guarded gate: void_plumbing (recompute A6,
        require == ORTHO_BAR to 1e-9, require A1_BASE == 0.04575, require self_retrieval >= 0.70;
        refuse if not), then gate gain arms on ci_lo > ORTHO_BAR_CI[1] AND delta>0 AND delta CI
        excludes zero. The delta>0 term is the sibling's 2026-08-24 sign-bug fix: without it a gain
        arm identical to base inherits base's clearance and reads as a pass. Under this harness every
        gain arm is a no-op, so the composite is correctly all-False.

WHAT I DID NOT ESTABLISH / WITHDRAW FIRST
  - I did NOT land the tool edit (out of scope). The tool on disk STILL REFUSES until the strategy
    session applies the diff. Everything it needs is measured and proven here.
  - "The honest floor is a real signal" depends on WHICH info-free twin. Against MY twins it separates
    CI-cleanly; the sibling cell's note reported the stripped string floor OVERLAPPING its twin -- but
    that used a shuffled CO-OCCURRENCE arm as the null (0.0135-0.0213), not the trigram floor's own
    shuffle. Different null, different answer; both defensible. IF CHALLENGED I WITHDRAW "the floor
    carries real orthographic signal" FIRST. The twin-independent, rock-solid facts are (a) the 78%
    collapse 0.087 -> 0.0195 and (b) the read-out clears the honest floor CI-separated.
  - "Re run the past results" scope: the one recorded verdict carrying the leaky bar
    (data/exp_per_row_gain_c3_vet_v1/metrics.json, 2026-08-15, bar 0.087) is re-graded here. I did NOT
    enumerate every downstream doc quoting 0.048/0.087 -- `tools/cite_check.py 0.0870` lists them and
    that sweep is the strategy session's when it lands the fix.

REVERIFY (one command; reproduces the headline from disk, no 45-min re-run, writes nothing)
  .venv/Scripts/python.exe verification/test_the_gate_can_measure_its_own_floor.py
  -> 5/5 PASS, exit 0. The full landed numbers are in
     data/exp_per_row_gain_trigram_floor_calibration_v1/metrics.json (byte-stable); a full re-run is
     `tools/reproduce.py experiments/exp_per_row_gain_trigram_floor_calibration_v1` (~45 min).

FILES
  - experiments/exp_per_row_gain_trigram_floor_calibration_v1.py   (new, measures)
  - verification/test_the_gate_can_measure_its_own_floor.py         (new, witness, WIRED into cert)
  - data/exp_per_row_gain_trigram_floor_calibration_v1/metrics.json (new, landed)
  - notes/problems/the_gate_cannot_measure_its_own_floor/SOLVED.md  (new)
  - PROPOSED-ONLY, not touched: tools/per_row_gain_c3_vet_v1.py

FOR THE STRATEGY SESSION
  1. Re-verify on the artifact (the reverify command above), then land the three-hunk diff and re-run
     the tool (~45 min full); the witness's landed-headline test already asserts A6=0.0195 + guard.
  2. Run cite_check.py 0.0870 and 0.048 to find and re-grade/annotate downstream docs.
  3. Non-blocking judgement call: settle ONE canonical info-free null for the string/trigram floor.
     The trigram arm's own shuffle (donor-query / row-permuted) is the faithful one; the shuffled
     co-occurrence arm answers a different question. Both gates cite a floor, so worth settling once.
