---
problem: the_bundle_destroys_meaning_but_replacing_it_hurts
status: SOLVED
bar: "AN EXPLANATION THAT PREDICTS BOTH RESULTS, TESTED ON THE TASK WHERE THE REFUTATIONS LANDED."
result: "Explanation (a)+(c), tested on c3 (WordNet-neighbour hit@1, GP._score_space, n=4000 items over 5491 anchors, 5000x paired bootstrap). Removing the bundle ENTIRELY (RAW_COOC = explicit per-context co-occurrence counts, zero superposition loss) scores 0.0605 and is CI-separated BELOW the spelling floor (delta -0.0262, CI [-0.0377,-0.0147]); no bundling operator and not surprise-weighting (PPMI 0.052-0.055) beats it -> the bundling is NOT the c3 bottleneck. And ~78% of the spelling floor is MORPHOLOGICAL LEAKAGE: strip stem-sharing WordNet gold and the spelling control collapses 0.0867 -> 0.0193 while the unmodified flat bag holds (0.048 -> 0.046) and BEATS it on leakage-free gold (delta +0.0266, CI [+0.0191,+0.0344]). BRAIN-FAITHFUL CAPSTONE (exp_c3_grounded_fusion_v1): fusing the flat bag with the GROUNDED sensorimotor spoke (Lancaster, unclamped; ATL hub-and-spoke) beats EITHER channel alone CI-separated (+0.0355 [+.027,+.044] vs the bag, +0.0163 [+.005,+.028] vs grounded; random(+)grounded control 0.0290 fails); on leakage-free gold it is the BEST arm, 0.0790 vs spelling 0.0193 (+0.0597, CI [+.051,+.069]); and the full hub distributional+grounded+spelling = 0.1125 CLEARS the floor's upper bound (CI_lo 0.1030 > 0.0958). Combine, do not substitute -- confirmed with a grounded spoke, not just the orthographic stand-in."
floor: "A5_STRINGCTRL (character-trigram spelling profile, MS.trigram_matrix) hit@1 0.0867, CI [0.0780,0.0958] -- the strongest no-understanding floor on record (brief's number), reproduced here and shown to be ~78% morphological leakage. Info-free floors also run: RANDOM 0.0085, SHUF_COOC (per-row-shuffled co-occurrence) 0.0177, FUSE_RANDOM_STRING 0.0780."
controls: "RANDOM (dense gaussian, 0.0085) and SHUF_COOC (per-row-independent column-shuffle of the co-occurrence: same shape, destroyed structure, 0.0177) -- both CI-separated below every real arm, EXCLUDING a rank-tie/degenerate-metric artifact. FUSE_RANDOM_STRING 0.0780 < string 0.0867 and FUSE_RANDOM_GROUNDED 0.0290 < grounded 0.0673 -- EXCLUDE the fusion gains being just the string/grounded channel or a fusion artifact. A1_BASE reproduces the landed c3 headline 0.0480 EXACTLY -- EXCLUDES a harness mismatch. Morph-stripped gold (leakage-free) -- EXCLUDES the spelling win being meaning. Cosine-invariance self-test guard -- EXCLUDES a non-null shuffle (a shared permutation leaves cosine invariant and is NOT info-free; the per-row shuffle is)."
files_changed: "experiments/exp_c3_surprise_weighted_vs_bundling_v1.py, experiments/exp_c3_grounded_fusion_v1.py, verification/test_c3_bundling_is_not_the_bottleneck.py, data/exp_c3_surprise_weighted_vs_bundling_v1/metrics.json, data/exp_c3_grounded_fusion_v1/metrics.json, notes/problems/the_bundle_destroys_meaning_but_replacing_it_hurts/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_c3_bundling_is_not_the_bottleneck.py"
---

# SOLVED: the bundling is not the bottleneck; the string floor is mostly morphology; the lever is a grounded spoke

## TLDR (plain language)

Our reader mashes a sentence's meaningful words into one shared code. A separate measurement said
that mashing destroys most of a word's distinguishing meaning, so replacing the mash looked like the
obvious fix -- yet two attempts to replace it made a real task worse. **I built the experiment that
un-mashes it completely and re-ran the task. Un-mashing changes almost nothing: it still loses to a
dumb spelling matcher.** So the mashing was never what was costing us on this task.

**Then I found what the spelling matcher was really doing.** The task grades an answer "right" if it
is a dictionary-relative of the word (a synonym or a category). About 78% of the spelling matcher's
wins were *word-shape* relatives -- "nation/national", "volcano/volcanic" -- which spelling finds for
free and which are not evidence of meaning. When I remove those shape-based answers and ask only for
relatives that do NOT look like the word, **the spelling matcher collapses and our meaning code --
including the plain mashed one -- beats it.** The headline "plain string-matching beats our whole
system 2:1" does not survive that check; most of it was the task rewarding spelling.

**And the real lever is to COMBINE, not replace:** our meaning code plus the spelling signal beats
either alone. That matches how the brain's meaning hub works -- it fuses channels rather than
swapping one for another.

## What I built

`experiments/exp_c3_surprise_weighted_vs_bundling_v1.py` runs, on the SAME task c3 the two
refutations landed on (same corpus, buckets, items, gold set and scorer, imported directly from the
landed harness), a head-to-head of ten arms, all scored hit@1 by the identical read-out
(`GP._score_space`) with a 5000x paired bootstrap, on TWO populations:

- the FULL landed gold set (4000 items, 5491 anchors), and
- a MORPHOLOGY-STRIPPED gold set (every WordNet gold member that shares a stem/form with the query
  removed, so a spelling signal cannot win by shape).

Task c3, precisely: a lemma L's accumulated distributional profile is used to rank all other anchors
by cosine; hit@1 = the top-ranked anchor is in `gold_meaning_set(L)` (WordNet synonyms + hypernyms +
sisters + hyponyms, L and its close variants excluded). It is profile->WordNet-neighbour retrieval
among 5491 words.

The arms, and why each exists:
- **A1_BASE** -- the flat bag (hdlab `context_vector_masked`, unmodified). Integrity: reproduces the
  landed headline `0.0480` to the bit.
- **A5_STRINGCTRL** -- character-trigram spelling profile. THE FLOOR (landed `0.0870`).
- **RAW_COOC** -- explicit per-context co-occurrence counts over the same masked context and the same
  profile sentences. This is *the flat bag with the superposition removed* -- the 256-dim hash
  projection and the additive bundling both gone, replaced by an interpretable count vector. It is
  the direct test of "does un-bundling help".
- **PPMI_RAW / PPMI_SMOOTH** -- surprise-weighting of those counts (PPMI; alpha=1.0 and the
  Levy&Goldberg alpha=0.75 context-smoothing control). The biggest known lever on a count model, and
  brain-motivated (N400 as a lexical prediction-error signal; Rabovsky et al. 2018).
- **RANDOM, SHUF_COOC** -- info-free twins (dense gaussian; per-row-shuffled co-occurrence). Must lose.
- **FUSE_PPMI_STRING, FUSE_BASE_STRING, FUSE_RANDOM_STRING** -- z-score fusion of a distributional arm
  with the string arm, plus the random(+)string artifact control.

A second cell, `experiments/exp_c3_grounded_fusion_v1.py`, runs the brain-faithful capstone (see the
capstone section below): flat bag fused with the grounded sensorimotor spoke on the same c3.

A scaffold-free witness, `verification/test_c3_bundling_is_not_the_bottleneck.py`, recomputes a
modest independent version (2442 anchors, fresh corpus draw) and asserts every load-bearing direction
-- bundling-removed still loses to spelling, spelling is leakage, the brain-faithful combine beats the
flat bag and beats spelling on leakage-free gold, info-free controls lose, and the shuffle-null guard.
It passes all of them.

## What I measured (FULL, n=4000, 5491 anchors, 5000x paired bootstrap)

| arm | hit@1 | 95% CI | gold-in-top50 | median rank | rank-1 conversion | paired delta vs A5_STRINGCTRL |
|---|---|---|---|---|---|---|
| A1_BASE (flat bag) | 0.0480 | [.0413,.0548] | 0.5565 | 37 | 0.086 | -0.0387 [-.050,-.028] **below** |
| **RAW_COOC (un-bundled)** | 0.0605 | [.0530,.0680] | 0.6285 | 26 | 0.096 | **-0.0262 [-.038,-.015] below** |
| PPMI_RAW | 0.0520 | [.0450,.0592] | 0.6183 | 30 | 0.084 | -0.0347 below |
| PPMI_SMOOTH | 0.0550 | [.0478,.0625] | 0.6273 | 28 | 0.088 | -0.0317 below |
| A5_STRINGCTRL (spelling) | 0.0867 | [.0780,.0958] | 0.5455 | 37 | **0.159** | -- (floor) |
| RANDOM | 0.0085 | [.0057,.0115] | 0.3033 | 136 | 0.028 | -0.0782 below (info-free) |
| SHUF_COOC | 0.0177 | [.0138,.0220] | 0.4153 | 77 | 0.043 | -0.0690 below (info-free) |
| FUSE_RANDOM_STRING | 0.0780 | [.0698,.0865] | -- | -- | -- | -0.0087 below (control) |
| FUSE_PPMI_STRING | 0.0943 | [.0853,.1035] | -- | -- | -- | +0.0075 [-.002,+.017] n.s. |
| **FUSE_BASE_STRING** | 0.1027 | [.0935,.1123] | -- | -- | -- | **+0.0160 [+.009,+.023] above** |

Morphology-stripped gold (n=3988; the leakage-free instrument):

| arm | hit@1 FULL | hit@1 STRIP | paired delta vs A5 on STRIP |
|---|---|---|---|
| A5_STRINGCTRL | 0.0867 | **0.0193** | -- (floor collapsed) |
| A1_BASE (flat bag) | 0.0480 | 0.0459 | **+0.0266 [+.0191,+.0344] above** |
| RAW_COOC | 0.0605 | 0.0582 | **+0.0389 [+.0306,+.0471] above** |
| PPMI_SMOOTH | 0.0550 | 0.0532 | +0.0339 [+.0258,+.0419] above |

k distribution of the population used: content-lemmas per profile sentence mean **11.4**, median 11,
p75 14 (n=153,352 profile sentences). Note this is HIGHER than the brief's k=6 -- c3's corpus is
textbook-register, so the superposition is even denser than the brief's example, which only sharpens
the conclusion below.

## The explanation that predicts BOTH landed results (the deliverable)

Task c3's usable distributional signal is COARSE RECALL -- getting a WordNet neighbour into the top
~50 out of 5491 -- and that recall is maximised by LINEAR ADDITIVE co-occurrence. The scarce, hard
part is RANK-1 CONVERSION: turning "in the top 50" into "first". The two facts the brief could not
reconcile fall straight out of that:

1. **Why replacing the bundle HURTS** (predicts `STRUCTURE_HURTS`, `CONJUNCTIVE_HURTS`). The
   conjunctive and structured codes make similarity superlinear / relation-bound, which DEGRADES
   coarse recall -- the landed cells show it directly (gold-in-top50 0.56 -> 0.42-0.47; self-retrieval
   0.79 -> 0.66-0.70). My arms show linear additive co-occurrence is at the top of coarse recall
   (RAW_COOC gold-in-top50 0.63, the best of any distributional arm), so any fancier operator throws
   coarse recall away without touching the rank-1 bottleneck. **"The blending IS the feature" -- the
   brief's resolution (a) -- is correct, but specifically it is the feature for COARSE RECALL.** And
   the 62% figure measures recovering INDIVIDUAL word identities out of a superposition; c3 never
   queries that -- it compares AGGREGATE profiles -- so the 62% is orthogonal to the task. The
   cleanest proof: **RAW_COOC removes the superposition entirely (explicit counts, zero bundling
   loss) and gains only +0.0125 -- still CI-separated below the spelling floor.** Un-bundling does not
   rescue c3, so the bundling was never the c3 cost.

2. **Why the spelling control BEATS the flat bag** (predicts `A5_STRINGCTRL 0.0870 > 0.0480`). Not
   because spelling carries more meaning. Measured: **~78% of the spelling control's hit@1 is
   morphological leakage** -- WordNet gold neighbours that share a stem with the query (nation/
   national), which trigram overlap finds for free. Strip them and the spelling control collapses
   0.0867 -> 0.0193, while the flat bag barely moves (0.0480 -> 0.0459) and BEATS it on the
   leakage-free gold. The residual spelling edge is a SHARP rank-1 signal (its conversion 0.159 vs the
   distributional 0.084-0.096) in a distributional space that is flat at the top. This is my own
   logged discipline paying off -- "a benchmark selected by a resource cannot fairly score that
   resource": c3's gold IS WordNet, and a WordNet-adjacent spelling instrument is doubly circular.

**So the bundling / representation question is NOT the bottleneck** (the brief's outcome (c), which it
called "the most valuable outcome"): no bundling operator and not surprise-weighting beats the
spelling floor on the FULL gold. What actually moves the number is (i) fixing the instrument (on
leakage-free gold the plain flat bag already wins) and (ii) COMBINING channels -- flat bag (+) string
beats string alone CI-separated, while random (+) string does not. **Combine, do not substitute.**

### Which of the brief's pre-registered outcomes fired
- **(a) fired** -- the linear blending IS the feature for coarse recall; it explains why the two
  replacements hurt. This alone closes the brief as UNDERSTOOD (a PASS).
- **(c) fired** -- nothing you can do to the bundle (re-operator, re-weight, un-bundle) beats the
  spelling floor on the landed gold; the representation is not the bottleneck.
- **(b) did NOT fire for a pure representation** -- no re-bundled/re-weighted arm beats both the flat
  bag and the spelling control. It fired only for a channel COMBINATION (fusion), which is a
  different claim.
- **(d) did NOT fire** -- I can tell what c3 needs; I also found a real, quantified DEFECT in the
  instrument (morphological leakage in the gold), which is better than "cannot tell".

## The brain-faithful combine (capstone: `exp_c3_grounded_fusion_v1`)

The v1 "combine" result fused the flat bag with SPELLING -- a form channel, not brain-faithful. The
capstone runs the actual anterior-temporal hub-and-spoke: fuse the flat bag (the distributional
channel) with the GROUNDED SENSORIMOTOR SPOKE (Lancaster norms, 11 dims, measured UNCLAMPED per the
`reader_meaning_channel` discipline; anchor coverage 0.81, item coverage 0.86), same c3 items / gold /
scorer, 5000x paired bootstrap.

| arm | hit@1 FULL | 95% CI | hit@1 leakage-free gold |
|---|---|---|---|
| A5_STRINGCTRL (spelling floor) | 0.0867 | [.0780,.0958] | 0.0193 (collapses) |
| A1_BASE (flat bag) | 0.0480 | [.0413,.0548] | 0.0459 |
| GROUNDED spoke alone | 0.0673 | [.0592,.0752] | 0.0607 |
| **FUSE_BASE_GROUNDED (flat bag (+) grounded)** | 0.0835 | [.0750,.0920] | **0.0790** |
| FUSE_RANDOM_GROUNDED (control) | 0.0290 | [.0240,.0343] | 0.0291 |
| **FUSE_BASE_GROUNDED_STRING (full hub)** | **0.1125** | [.1030,.1222] | 0.0431 |

Three things, all CI-backed:

1. **Hub-and-spoke fusion beats EITHER channel alone (the pinned Andrews-2009 prediction), on c3.**
   FUSE_BASE_GROUNDED beats the flat bag by +0.0355 [+.027,+.044] AND grounded alone by +0.0163
   [+.005,+.028], both CI-separated; the random(+)grounded control (0.0290) fails. Fusing a
   distributional channel with a grounded spoke is more than either -- exactly the hub prediction, and
   it is the FIRST arm in this whole thread that improves on the flat bag for a MEANING reason rather
   than a form one.
2. **On the FAIR (leakage-free) instrument the brain-faithful combine is the BEST arm** -- 0.0790,
   beating the spelling floor by +0.0597 [+.051,+.069], beating the flat bag and grounded alone, and
   beating the full hub (0.0431) because once spelling cannot leak it is pure noise and drags the
   fusion down. So the right combine is distributional + grounded, and adding spelling only helps on
   the leaky raw gold.
3. **On the raw (leaky) gold, the full hub distributional+grounded+spelling clears the floor's UPPER
   bound** (0.1125, CI_lo 0.1030 > the floor's CI_hi 0.0958) -- the only arm that does. The
   distributional + grounded pair alone TIES the leaky floor (0.0835 vs 0.0867, not separated),
   because the raw gold hands spelling ~78% free leakage; strip that and the combine wins outright.

So the resolution is not "replace the bundle" and not "re-weight the bundle" -- it is **keep the
bundle and ADD a grounded spoke**, which is what the brain does. That also matches the strategy
session's own finding 1 on the sibling brief ("use it AS WELL, not instead").

## Brain fidelity (labelled, per standing discipline)
- **PINNED-AS-PRINCIPLE:** surprise/prediction-error-gated encoding (N400; Rabovsky 2018; predictive
  coding). An anterior-temporal hub that COMBINES a distributional channel with complementary spokes,
  fusion beating either alone (Patterson 2007; Lambon Ralph 2017; Andrews 2009). The "combine, don't
  substitute" result is consistent with this and with the strategy session's own finding 1.
- **OUR-INVENTION-UNDER-TEST:** the PPMI formula as the surprise proxy (and it did NOT help rank-1
  here -- PPMI - RAW = -0.0055, n.s. -- so this instance is unfalsified-but-unsupported, not a win);
  and the z-score fusion RULE (the brain's hub is a nonlinear learning stage, not a fixed algebra).
  The v1 fusion partner was ORTHOGRAPHY, a FORM channel, so `FUSE_BASE_STRING` demonstrated only the
  COMBINE PRINCIPLE. The capstone (`exp_c3_grounded_fusion_v1`) replaces it with the GROUNDED
  sensorimotor spoke and confirms the brain-faithful version: fusion beats either channel alone,
  CI-separated. The grounded VECTOR (11 sensorimotor dims) is our engineering choice; the hub-and-
  spoke ARCHITECTURE it instantiates is the pinned part.

## What this implies for hdlab/ (proposed, NOT landed -- strategy session owns the substrate)
1. **Do not spend effort replacing the flat bundler to fix c3.** The evidence is that the additive
   bundle is near-optimal for the coarse-recall part and that un-bundling buys ~nothing. The two
   default-off replacements (`perirhinal_conjunctive.py`, the structured encoder) should stay off for
   this purpose.
2. **The lever is a read-out-time COMBINE with the GROUNDED spoke, not a new bundler.** Measured:
   flat bag (+) grounded sensorimotor beats either alone CI-separated and is the best arm on
   leakage-free gold (+0.0597 over the floor). This is exactly `reader_meaning_channel`'s adapter
   ("read() never consults the meaning asset") -- so the wiring is: at read-out, z-score-fuse the
   distributional cosine with the grounded cosine, use the grounded spoke where covered (0.81 of
   anchors) and fall back to the bag where not. This DOVETAILS with that brief rather than competing.
3. **Fix the instrument before trusting the floor.** Any future c3-style gate should score against a
   morphology-stripped gold (or report both), because the raw WordNet gold rewards spelling. The
   "spelling beats the system 2:1" number (brief section 3, its biggest) does not survive that fix.

## What I did NOT establish, and what I would withdraw first
- **Withdraw first:** the orthographic-fusion claims (`FUSE_BASE_STRING`, full hub). They rely on the
  raw WordNet gold, whose ~78% spelling leakage is exactly what makes a form channel look useful; on
  the fair gold spelling is noise and the full hub DROPS to 0.0431. The load-bearing, brain-faithful
  results are (i) flat bag beats spelling on leakage-free gold (+0.0266 [+.019,+.034]) and (ii) flat
  bag (+) grounded beats either channel alone CI-separated and is the best arm on fair gold
  (+0.0597 [+.051,+.069]). Lean on those, not on anything involving the spelling channel.
- Absolute hit@1 is low for EVERY arm (0.02-0.11 among 5491) -- c3 is WordNet taxonomic *similarity*,
  the axis co-occurrence is structurally weakest at (Hill 2015). Even the leakage-free "combine wins"
  is on a stingy instrument; this shows the grounded spoke is the missing lever on c3, not that the
  absolute number is good.
- Surprise-weighting (PPMI) was my hypothesised lever and it is REFUTED on c3: it improves coarse
  recall but not rank-1, and does not beat the floor. The grounded-spoke fusion IS now tested (and
  wins); a learned (SVD / contextual) reweighting and a LEARNED (vs z-score) hub rule remain open.
- I did not re-run the two landed FULL cells (that would re-date landed records; README forbids it). I
  relied on their on-disk metrics.json plus my own reproduction of A1_BASE=0.0480 and A5=0.0867 as the
  integrity link.

## Reproduce
- Headline (scaffold-free, ~4 min): `.venv/Scripts/python.exe verification/test_c3_bundling_is_not_the_bottleneck.py`
  -- asserts, at an independent smaller scale, all of: bundling-removed still loses to spelling; the
  spelling floor is morphological leakage; the brain-faithful combine beats the flat bag and beats the
  spelling floor on leakage-free gold; info-free controls lose; the shuffle bug guard.
- Full numbers/CIs: `data/exp_c3_surprise_weighted_vs_bundling_v1/metrics.json` (bundling/leakage,
  ~62 min) and `data/exp_c3_grounded_fusion_v1/metrics.json` (grounded capstone, ~31 min). Re-run via
  `tools/reproduce.py <cell>`, NOT a bare in-place re-run (README hazard).

## TLDR / QUESTIONS / NEXT STEPS
**TLDR:** Un-mashing the sentence code does not help the task -- it still loses to a spelling matcher,
so the mashing was never the problem. And most of the spelling matcher's win was the task rewarding
word-shape, not meaning; remove that and our plain code beats it. What DOES help is adding the brain's
other meaning channel -- the grounded "what it feels/looks/sounds like" knowledge -- ALONGSIDE the
mashed code: the two together beat either one alone, and on the fair test they beat the spelling
matcher outright. Keep the code, add the grounded channel, don't replace anything.

**QUESTIONS:** None. (The board is empty and the brief asked for none.)

**NEXT STEPS (for the strategy session, not me):**
1. Re-score any c3-style gate against morphology-stripped gold, or report both -- the raw WordNet gold
   rewards spelling and the "2:1" floor is ~78% leakage.
2. **Wire the measured combine:** at read-out, z-score-fuse the distributional cosine with the grounded
   sensorimotor cosine (grounded spoke where covered, bag elsewhere). This is exactly
   `reader_meaning_channel`'s missing adapter; the capstone shows it beats either channel alone and
   beats the floor on fair gold. A learned hub rule (vs z-score) is the obvious follow-on.
3. Keep the flat bundler; retire the "replace the bundle" thread for c3.
