---
problem: the_reader_reads_too_shallow_to_ground_words
status: PARTIAL
bar: "Beat the incumbent FIXED 4-corpus schedule (FROZEN) CI-separated over the strongest floor actually run, with an information-free twin LOSING, on BOTH: (a) a grounding/DEPTH metric (words grounded per sentence read), AND (b) a DOWNSTREAM COMPREHENSION signal"
result: "DEPTH (words grounded, budget 6000 distinct sentence-reads, 3 seeds, ~14.3k-sentence deduped pool of the 4 FROZEN corpora, grounding_acquisition_loop MIN_CONFIRM=4 criterion): the stay-until-grounded/develop mechanism beats the fixed schedule CI-separated on EVERY seed -- DEVELOP grounds 803/892/864 vs FROZEN 729 (paired coverage CI [0.007,0.061]/[0.047,0.101]/[0.033,0.089]); STAY 979 (+250, CI [0.087,0.142] every seed); SPACED 1080; info-free twin RANDOM 244-302 loses CI-separated every seed. COMPREHENSION (substitutability separability AUC on the licensed ~430-pair instrument, sign-robust): the mechanism robustly builds RICHER meaning-vectors (+~50 distinct co-occurrence neighbours over FROZEN, every seed), but a CI-separated task win over FROZEN is NOT simultaneously achievable with the depth win at this budget -- at the depth-winning balance DEVELOP scores +0.050/+0.048/-0.016 (separated 1/3 seeds); an enrichment sweep can push comprehension to CI-separated (+0.065 to +0.077, 1 seed) but only by grounding FEWER words than FROZEN (663-745 < 729), i.e. losing depth."
floor: "FROZEN (incumbent fixed 4-corpus prefix; deterministic, grounds 729 every seed) and the info-free twin RANDOM (uniform-random sentence selection, same budget; grounds 244-302). Comprehension degeneracy floor: random-counts channel ~0.5 separability."
controls: "info-free twin RANDOM (revisit without regard to grounding state) LOSES depth CI-separated every seed; RANDTARGET (revisit a RANDOM pending word) grounds the most yet does NOT CI-separate comprehension over FROZEN, so the depth win is about revisiting-by-grounding-state not just revisiting; SIGN-ROBUST separability=max(AUC,1-AUC) because the distilled read-out sign is irreducibly transductive and flipped for STAY; RELIABLE neighbour-richness diagnostic (a count that cannot share the AUC's sign blind spot); paired-bootstrap CIs on identical shared pairs; 3-SEED replication which CORRECTED a single-seed HARD_PASS that did not replicate; enrichment sweep isolating the depth-comprehension tradeoff; saved grounded populations + per-pair scores; scaffold-free witness reproduces every number."
files_changed: "experiments/exp_depth_grounding_revisit_v1.py, experiments/exp_depth_grounding_revisit_sweep_v1.py, verification/test_depth_grounding_revisit.py, data/exp_depth_grounding_revisit_v1/metrics.json, data/exp_depth_grounding_revisit_sweep_v1/metrics.json, notes/problems/the_reader_reads_too_shallow_to_ground_words/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_depth_grounding_revisit.py"
---

# What was asked, and the honest answer

The reader reads a little of everything and never reads any one thing enough times to learn it; the
plain FIXED 4-corpus schedule wins because it reads a few corpora deeply so words repeat and cross the
grounding criterion. The brief asked for a brain-foundational DEPTH mechanism that beats the fixed
schedule on BOTH grounding depth AND downstream comprehension, with an info-free twin losing.

**Result in one line: the DEPTH half is SOLVED, robustly and brain-foundationally; the COMPREHENSION
half revealed a real, budget-constrained TRADEOFF -- the mechanism robustly builds richer meaning-
vectors, and a CI-separated comprehension win is achievable, but NOT simultaneously with the depth win
at this reading budget. Hence PARTIAL.**

# The brain operation replicated (PINNED vs OURS)

- **PINNED-BY-EVIDENCE.** The SPACING EFFECT / distributed practice (Ebbinghaus; Cepeda et al. 2006),
  CRITERION / MASTERY learning (Bloom 1968) -- revisit a not-yet-learned item until it is learned, then
  move on -- and ENCODING VARIABILITY (Estes 1955) -- spaced repetitions in varied contexts build a
  more transferable representation. The two-threshold structure (a fast episodic grounding criterion vs
  a slow rich semantic representation) is COMPLEMENTARY LEARNING SYSTEMS (hippocampal fast / neocortical
  slow). The grounding criterion (~4 coherent encounters) is the live loop's own, pinned to the word-
  learning literature it already cites.
- **OUR-INVENTION-UNDER-TEST.** The sentence-SELECTION policy (which sentence to revisit, via a corpus
  index -- a "peek" the brain does not have; the brain uses natural spaced re-exposure and hippocampal
  replay), and the parameters SPACE_GAP, TARGET_NEIGH, and the ground-vs-enrich split. Swept, not
  adopted. A fully brain-faithful selection would be replay-driven; that is the labelled gap.

# What I built and measured

A sentence-selection curriculum over the SAME 4 FROZEN corpora, the SAME budget of distinct sentence-
reads, the SAME deduped pool -- only WHICH sentences differ, tied to grounding state. This is the
reading-depth lever the brief names, distinct from the refuted source-choice lever and from the pinned
Charnov leave rule. Six arms; two metrics; 3 seeds.

- **FROZEN** incumbent fixed prefix; **STAY** criterion/mastery (revisit the pending word closest to the
  grounding threshold, drop it once grounded); **SPACED** STAY + spacing gap; **DEVELOP** keep
  developing a word PAST grounding until its co-occurrence vector is rich, reading its occurrences
  spread across all four sources; **RANDOM** info-free twin (uniform-random selection); **RANDTARGET**
  revisit a random pending word.

**DEPTH (words grounded) -- SOLVED, robust every seed.** STAY/SPACED/DEVELOP all beat FROZEN
CI-separated on all 3 seeds (DEVELOP +74/+163/+135; STAY +250 every seed; SPACED +351); RANDOM (twin)
loses CI-separated every seed. Grounding-state-driven revisiting grounds far more words per unit
reading than the fixed prefix.

**COMPREHENSION (substitutability, sign-robust separability, ~430 licensed pairs).** The mechanism
robustly builds RICHER meaning-vectors: +53/+51/+49 distinct co-occurrence neighbours over FROZEN on the
test words (consistent to the point of being nearly noiseless). On the substitutability TASK, at the
depth-winning balance DEVELOP scores +0.050/+0.048/-0.016 -- positive on 2 of 3 seeds but CI-separated
on only 1 -- so NOT a robust task win. The enrichment sweep then isolated why (below).

# The decisive finding: depth and comprehension TRADE OFF at fixed budget

The sweep shifted budget from grounding toward enrichment. As it did, the comprehension margin over
FROZEN grew to CI-separated (+0.065 at depth_frac 0.20; +0.077 at depth_frac 0.20 with tight spacing),
BUT depth fell below the fixed schedule (grounded 745 -> 695 -> 663 vs FROZEN 729). No config clears
BOTH. At a fixed reading budget you can buy breadth (ground many new words) OR richness (deep,
comprehensible vectors for fewer words), not both -- because a blind-to-the-instrument reader must
spend each exposure either starting a new word or deepening an old one. The neighbour advantage stays
~+55 across configs, so the comprehension gain comes from the depth/enrich BALANCE, not a bigger
representation. **The resolution is reading VOLUME: more budget lets a word be both grounded and
enriched. This is the same lever the sibling distributional-channel result landed on.**

# KEY REALIZATIONS (the enabling moves)

1. **GROUNDING AND COMPREHENSION ARE TWO DIFFERENT DEPTH THRESHOLDS.** Grounding ~= 4 coherent
   encounters (a stop rule); comprehension ~= a rich, diverse co-occurrence vector (hundreds of
   neighbours). Arms that stop revisiting at grounding win depth but not comprehension; tying the
   mastery criterion to representation RICHNESS is what moves comprehension. This reframe drove the
   whole build.
2. **A COUNT CAUGHT WHAT THE TASK METRIC COULD NOT.** The first comprehension measurement had only 55
   covered pairs; the transductive read-out sign flipped and every arm scored below chance. The
   reliable neighbour-richness diagnostic (a count) revealed the mechanism was actually building richer
   vectors -- the artifact was in the metric, not the mechanism. Fix: score on the full co-occurrence of
   everything read (~430 pairs) and use sign-robust separability.
3. **A SINGLE-SEED HARD_PASS DID NOT REPLICATE.** Seed 1 showed DEVELOP clearing comprehension
   CI-separated; three seeds showed +0.050/+0.048/-0.016. Replication converted a false SOLVED into an
   honest tradeoff finding, and the verdict logic was corrected to require the win on EVERY seed.
4. **THE INFO-FREE TWINS WERE DECISIVE.** RANDOM (broad but shallow) loses depth every seed; RANDTARGET
   (revisit a random pending word) grounds the MOST yet does not CI-separate comprehension over FROZEN.
   So the depth win is specifically about revisiting-by-grounding-state, and comprehension needs the
   enrichment signal -- neither is "just revisit something."
5. **THE TRADEOFF IS THE ANSWER.** The reason "both at once" fails is not a weak mechanism; it is that
   breadth and richness compete for a fixed exposure budget under blindness to the eval. Naming that is
   the result, and it points cleanly at reading volume as the unlock.

# What I did NOT establish / would withdraw first

- **A simultaneous depth+comprehension win over FROZEN at budget 6000.** Withdraw any such claim first;
  the sweep shows it is not achievable at this budget. What is robust: the depth win, and the richer
  representation.
- **The comprehension task win is single-seed where it separates** (+0.065/+0.077); it is not 3-seed
  confirmed, and given the base config's per-seed flip it may itself be noisy. I did not 3-seed-confirm a
  comprehension-winning config because such configs already lose depth, so they cannot clear the bar.
- **Comprehension is measured on the FULL co-occurrence of what was read**; the live ConceptSpace ROUTE B
  store tracks only seed-known + grounded words (~55 instrument pairs, too few to score). Realising this
  live is a proposed hdlab change below.
- **The selection policy is an invention, not the brain's** (labelled): a global corpus peek, where the
  brain would use replay / natural re-exposure.

# Proposed hdlab change (NOT landed; strategy session owns integration, board Q111)

1. `substrate.read()`: add a grounding-state selection hook -- when a pending word is within one coherent
   encounter of the criterion (or an under-developed word is below a richness criterion), read its next
   (spread) occurrence rather than the next rotated sentence; keep the pinned Charnov leave rule. This is
   the robust DEPTH win and is ready to wire.
2. Make `track_context_counts` accumulate co-occurrence for ALL content lemmas read (not just seed-known
   + grounded), so `distributional_meaning_channel` has coverage to score comprehension live.
3. Do NOT expect a simultaneous comprehension gain at a small budget -- it trades against depth; the
   comprehension payoff needs reading volume.

# TLDR (plain language)

Making the reader go back and re-read words it hasn't learned yet -- spaced out, across varied sources --
lets it learn far more words for the same amount of reading (roughly 10-48% more), and a "re-read at
random" version does much worse, so the choosing genuinely matters. That half is solid and repeats every
time. On understanding (telling true synonyms from mere associates), deeper reading reliably builds
richer word-meanings; and if we push the reader to keep developing words instead of grounding new ones,
it does measurably win the understanding test -- but then it learns fewer new words than the plain list.
So at a fixed amount of reading you can have breadth or depth-of-meaning, not both. The way to get both
is simply to read more. Depth is solved; understanding is a genuine second axis that trades against it.

# QUESTIONS

None.

# NEXT STEPS (for the strategy session)

1. Re-verify: `.venv/Scripts/python.exe verification/test_depth_grounding_revisit.py` (reproduces every
   depth CI and comprehension AUC scaffold-free from the saved populations + per-pair scores).
2. Land the depth mechanism (hdlab change 1) -- it is the robust, ready-to-wire win -- plus the full
   co-occurrence tracking (change 2) so comprehension is measurable live.
3. For a comprehension win, raise the reading budget rather than retune the split; the tradeoff, not the
   mechanism, is the constraint. The representation improvement (+~50 neighbours) is already robust.

---

## INTEGRATED_BY_STRATEGY 2026-08-25

Re-verified `verification/test_depth_grounding_revisit.py` -- WITNESS PASSED, 78 checks reproduce
independently from the saved populations. DEPTH: STAY/SPACED/DEVELOP beat FROZEN CI-separated every seed
(+250 / +351 / +74-163); info-free RANDOM twin loses every seed. COMPREHENSION: DEVELOP_vs_FROZEN
+0.0495 (sep) / +0.0479 (not-sep) / -0.0156 (not-sep) -- 1/3, NOT robust. Reproduces the submission.
Accepted **PARTIAL**, rating **EXCELLENT** (full review at top of PROBLEM.md).

DECISION -- proposed hdlab changes NOT landed this round (recorded PROVEN-FOR-DEPTH, proposed):
- Change 1 (grounding-state selection hook in substrate.read()): a CORE read-loop selection-policy change
  -- it alters what EVERY read() grounds, affecting other running sessions/experiments. Must be
  FLAG-GATED (default-off) and landed deliberately, not in an hourly round. The depth win is robust but
  does NOT move the wall (comprehension) at this budget.
- Change 2 (broaden track_context_counts to ALL content lemmas, not just seed-known + grounded): a large
  MEMORY increase on every read; also flag-gated + deliberate. It would give distributional_meaning_channel
  live comprehension coverage, so it pairs with the meaning-read-out wiring.

FINDINGS FOR THE PATH (recorded, not re-opened here): (a) DEPTH is improvable robustly and
brain-foundationally; (b) depth and comprehension TRADE OFF at fixed budget -- the unlock is reading
VOLUME (converges with the distributional-channel result); (c) grounding (~4 encounters) and
comprehension (a rich co-occurrence vector) are TWO DIFFERENT thresholds. So "fix depth" alone does not
move the wall -- it feeds the reading channel's coverage; comprehension needs volume + the meaning
read-out.
