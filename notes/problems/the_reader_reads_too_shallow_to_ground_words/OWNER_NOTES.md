---
owner_verdict: DONE
---

SUBMISSION — SOLVER RESULT for problem: the_reader_reads_too_shallow_to_ground_words
STATUS: PARTIAL  (depth half SOLVED robustly + brain-foundationally; comprehension half is a
                  genuine budget-constrained TRADEOFF, not a tuning gap)
LEDGER: `python tools/problem_ledger.py --check` -> OK, malformed/incomplete: 0, awaiting integration.
REVERIFY (scaffold-free, reproduces every number from saved populations; writes to no landed dir):
    .venv/Scripts/python.exe verification/test_depth_grounding_revisit.py

================================================================================
WHAT WAS ASKED
================================================================================
The reader reads a little of everything and never reads any one thing enough times to learn it. A
plain FIXED 4-corpus schedule beats every "smart" reader because it reads a few corpora deeply so
words repeat and cross the grounding criterion. The bar: a brain-foundational DEPTH mechanism that
beats FROZEN CI-separated, with an info-free twin LOSING, on BOTH (a) grounding DEPTH and (b) a
downstream COMPREHENSION signal. Source choice was already refuted 3 ways; this is the depth lever.

================================================================================
KEY REALIZATIONS THAT UNLOCKED THIS (the enabling moves, not just the result)
================================================================================
1. GROUNDING AND COMPREHENSION ARE TWO DIFFERENT DEPTH THRESHOLDS. Grounding ~= 4 coherent encounters
   (a STOP rule). Comprehension ~= a rich, diverse co-occurrence vector (hundreds of neighbours).
   Any arm that stops revisiting at grounding wins depth but not comprehension; the arm that keeps
   developing a word PAST grounding (DEVELOP) is the only one that moves comprehension. This reframe
   drove the whole build.
2. A RELIABLE COUNT CAUGHT A METRIC ARTIFACT THE TASK-AUC COULD NOT. The first comprehension measure
   had only 55 covered instrument pairs; the distilled read-out's transductive sign FLIPPED and every
   arm scored below chance. The neighbour-richness diagnostic (a plain count, which cannot share the
   AUC's sign blind spot) showed the mechanism was actually building RICHER vectors. Fix: score on the
   FULL co-occurrence of everything read (~430 pairs) and use SIGN-ROBUST separability = max(AUC,1-AUC).
3. A SINGLE-SEED HARD_PASS DID NOT REPLICATE. Seed 1 showed DEVELOP clearing comprehension CI-separated;
   3 seeds showed +0.050/+0.048/-0.016. Replication converted a false SOLVED into the honest tradeoff.
   I corrected the cell's verdict logic to require the win on EVERY seed (it had judged on the primary
   seed only) and re-derived the landed verdict to DEPTH_SOLVED_COMPREHENSION_NOT_ROBUST.
4. THE TRADEOFF IS THE ANSWER. "Both at once" fails not from a weak mechanism but because breadth
   (grounding new words) and richness (comprehensible vectors for fewer words) COMPETE for a fixed
   exposure budget under blindness to the eval. The lever for both is READING VOLUME (same conclusion
   the sibling distributional-channel result reached).

================================================================================
THE ARC / WHAT WAS MEASURED (budget 6000 distinct sentence-reads, 3 seeds, ~14.3k-sentence deduped
pool of the 4 FROZEN corpora; grounding_acquisition_loop MIN_CONFIRM=4)
================================================================================
DEPTH (words grounded) — SOLVED, robust EVERY seed:
  FROZEN 729 (deterministic) | STAY 979 (+250, CI [0.087,0.142] every seed) | SPACED 1080
  | DEVELOP 803/892/864 (+74/+163/+135, CI [0.007,0.061]/[0.047,0.101]/[0.033,0.089] — all lo>0)
  | info-free twin RANDOM 244-302 (loses CI-separated every seed).

COMPREHENSION (substitutability separability AUC, licensed instrument, ~430 shared pairs):
  - Reliable, consistent: DEVELOP builds RICHER meaning-vectors, +53/+51/+49 distinct co-occurrence
    neighbours over FROZEN (nearly noiseless across seeds).
  - Noisy task margin: DEVELOP vs FROZEN separability = +0.050/+0.048/-0.016 (CI-separated only 1/3
    seeds). NOT a robust task win at the depth-winning balance.

THE DECISIVE FINDING (enrichment sweep, exp_depth_grounding_revisit_sweep_v1):
  Shifting budget from grounding toward enrichment grows the comprehension margin to CI-separated
  (+0.065 at depth_frac 0.20; +0.077 at depth_frac 0.20 tight-spacing) BUT drops grounding below FROZEN
  (745 -> 695 -> 663 vs 729). NO config clears BOTH. Verdict: SWEEP_NO_CONFIG_CLEARS_BOTH.
  => depth and comprehension TRADE OFF at fixed budget; the resolution is reading volume.

================================================================================
CONTROLS (what each excluded)
================================================================================
- INFO-FREE TWIN RANDOM (revisit without regard to grounding state): loses depth CI-separated every
  seed -> the grounding-state signal carries real depth information.
- RANDTARGET (revisit a RANDOM pending word): grounds the MOST yet does NOT CI-separate comprehension
  over FROZEN -> the depth win is revisiting-BY-grounding-state, and comprehension needs the enrichment
  signal, not "revisit something."
- SIGN-ROBUST separability = max(AUC,1-AUC): the distilled sign is irreducibly transductive and FLIPPED
  for STAY (raw AUC 0.206 = the sign-inverted image); separability removes that fragility. Degeneracy
  floor (random counts) ~0.5.
- Neighbour-richness diagnostic: a count that cannot share the AUC's sign blind spot.
- 3-SEED replication (corrected a single-seed HARD_PASS); paired-bootstrap CIs on identical shared
  pairs; saved grounded populations + per-pair scores; scaffold-free witness reproduces every number.

================================================================================
CAVEATS / WHAT I DID NOT ESTABLISH (withdraw first if wrong)
================================================================================
- A SIMULTANEOUS depth+comprehension win over FROZEN at budget 6000 — withdraw first; the sweep shows
  it is not achievable at this budget. Robust: the depth win, and the richer representation.
- The comprehension-task win is single-seed where it separates (+0.065/+0.077) and was not 3-seed
  confirmed, because comprehension-winning configs already LOSE depth (can't clear the bar).
- Comprehension is measured on the FULL co-occurrence of what was read; the live ConceptSpace ROUTE B
  store tracks only seed-known + grounded words (~55 instrument pairs, too few to score live).
- The sentence-SELECTION policy is an INVENTION, not the brain's: a global corpus "peek", where the
  brain would use replay / natural re-exposure. Core operations (spacing, criterion/mastery, encoding
  variability, CLS two-threshold) ARE pinned; the selection is the labelled fidelity gap.

================================================================================
PROPOSED hdlab CHANGES (NOT landed — strategy session owns integration, board Q111)
================================================================================
1. substrate.read(): add a grounding-state selection hook — when a pending word is within one coherent
   encounter of the criterion (or an under-developed word is below a richness criterion), read its next
   (spread) occurrence instead of the next rotated sentence; keep the pinned Charnov leave rule. This
   is the robust DEPTH win, ready to wire.
2. Make track_context_counts accumulate co-occurrence for ALL content lemmas read (not just seed-known
   + grounded), so distributional_meaning_channel has coverage to score comprehension live.
3. Do NOT expect a simultaneous comprehension gain at a small budget — it trades against depth. The
   comprehension payoff needs reading VOLUME.

================================================================================
FILES
================================================================================
experiments/exp_depth_grounding_revisit_v1.py         (6-arm cell: FROZEN/STAY/SPACED/RANDOM/RANDTARGET/DEVELOP)
experiments/exp_depth_grounding_revisit_sweep_v1.py   (enrichment sweep — the tradeoff isolation)
verification/test_depth_grounding_revisit.py          (scaffold-free witness; REVERIFY)
data/exp_depth_grounding_revisit_v1/metrics.json      (3-seed; verdict corrected to cross-seed)
data/exp_depth_grounding_revisit_sweep_v1/metrics.json(SWEEP_NO_CONFIG_CLEARS_BOTH)
notes/problems/the_reader_reads_too_shallow_to_ground_words/SOLVED.md

================================================================================
FOR THE STRATEGY SESSION
================================================================================
1. Re-verify: .venv/Scripts/python.exe verification/test_depth_grounding_revisit.py
2. Land the depth mechanism (change 1) — the robust, ready-to-wire win — plus full co-occurrence
   tracking (change 2) so comprehension is measurable live.
3. For a robust comprehension win, raise the reading budget rather than retune the split; the tradeoff,
   not the mechanism, is the constraint. The representation improvement (+~50 neighbours) is robust.

================================================================================
PLAIN-LANGUAGE TLDR
================================================================================
Making the reader go back and re-read words it hasn't learned yet — spaced out, across varied sources —
lets it learn far more words for the same amount of reading (roughly 10-48% more), and a "re-read at
random" version does much worse, so the choosing genuinely matters. That half is solid and repeats
every time. On understanding (telling true synonyms from mere associates), deeper reading reliably
builds richer word-meanings, and if we push the reader to keep developing words instead of grounding
new ones it does win the understanding test — but then it learns fewer new words than the plain list.
So at a fixed amount of reading you can have breadth OR depth-of-meaning, not both; the way to get both
is to read more. Depth is solved; understanding is a genuine second axis that trades against it.
