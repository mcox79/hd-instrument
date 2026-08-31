# Research drill 4 (2026-08-31): the brain mechanism of candidate competition in who-did-what

Dispatched (hdi_research) after the two-factor-flag test found: non-canonicity FAILS as a structural
signal (AUC 0.487 ~chance) but CANDIDATE COMPETITION works (AUC 0.666; flags the low-surprisal errors
surprisal misses, +0.15 gap; combined flag 0.683->0.692 directional). Goal: understand the mechanism +
find the MOST brain-faithful competition signal (raw count is crude).

## Findings

**Q1 -- Competition is a DISTINCT brain machine from thematic-fit (validates the two-signal flag).**
Thompson-Schill 1997 (PNAS): LIFG = SELECTION-AMONG-COMPETING-REPRESENTATIONS, separable from meaning
access. Novick & Trueswell 2005: LIFG = cognitive control / conflict resolution, a layer ON TOP of
plausibility. The distinct error TYPE = the semantic P600 / role-reversal (Kuperberg 2007; van Herten &
Kolk 2005; Ferreira 2003 good-enough): LOW-surprisal, WRONG-argument = our missed-error quadrant. Two
dissociable streams: N400 = thematic fit (our surprisal flag); P600/LIFG = competition/control (misses).

**Q2 -- The brain's competition cost is CONFUSABILITY (similarity), NOT raw count.** Lewis & Vasishth
2005: cue-based retrieval; interference is SIMILARITY-based (cue/feature overlap); count enters only as
the degenerate "fan" term (uniform confusability). Van Dyke & McElree 2006: interference at RETRIEVAL,
driven by CUE-OVERLOAD (which competitors match, not how many). Jager/Engelmann/Vasishth 2017 (meta,
110 comps): confusability graded + structured. Wagers/Lau/Phillips 2009: agreement ATTRACTION = confident
misretrieval of a partially-matching LURE = the mechanistic model for our low-surprisal semantic-illusion
errors (facilitatory interference = high-confidence wrong answer = what surprisal cannot flag). So raw
count is a CRUDE PROXY for competitor confusability.

**Q3 -- Interference, not capacity.** Retrieval is direct-access (~1 item in focal attention, McElree
2001); errors are cue-confusability-driven, not capacity-slot-search. Van Dyke & Johns 2012: capacity/
decay accounts untenable; interference determines difficulty. Cowan-4 = OUTER ENVELOPE / interaction
gate, not the driver. Raw count conflates capacity-load + fan -> crude (AUC 0.67).

## THE BRAIN-FAITHFUL SIGNAL TO BUILD (ranked)
1. **(c) cue-weighted competitor CONFUSABILITY of the CHOSEN argument -- BUILD THIS.** = posterior-mass-
   weighted cosine similarity (grounded space) between the chosen argument and the OTHER candidates:
   "how much probability sits on meaning-similar near-twins of the one I picked." The fan term done RIGHT
   (weighted by similarity, not counted). We have the ingredient the models had to ASSUME: a grounded
   meaning space. Define vs the CHOSEN argument (attraction/illusion account -> predicts the reader's error).
2. (b) softmax ENTROPY -- graded, distribution-aware, but blind to WHICH competitors are confusable. Free
   companion feature (from the existing softmax).
3. (a) raw COUNT -- degenerate uniform-fan case; least faithful; keep as baseline-to-beat.
4. (d) full ACT-R cue-based-retrieval score -- most faithful in principle but drags in unshared params
   (base-level decay, cue weights, noise, F, threshold); later upgrade only if (c)'s residual demands it.

## HONEST DEFLATION + THE RIGHT EVALUATION (drill's own steer)
Direction (similarity not count) + distinctness (separate stream) = HIGH confidence. Whether confusability
BEATS count (already AUC 0.67) on THIS substrate = novel synthesis, P~0.45-0.50 (they correlate; count may
absorb much variance). => BUILD it, but GATE acceptance on a HEAD-TO-HEAD (confusability vs entropy vs
count, each as a complement to surprisal) evaluated SPECIFICALLY on the LOW-SURPRISAL error subset (the
semantic-illusion quadrant), with the CI-separation bar + null p95 -- NOT pooled AUC (a directional
0.68->0.69, as count already shows, would not clear the margin). Test the Cowan-4 x confusability interaction.

Key sources: Thompson-Schill 1997 (PNAS); Novick & Trueswell 2005 (CABN); Kuperberg 2007; van Herten &
Kolk 2005; Ferreira 2003; Lewis & Vasishth 2005; Van Dyke & McElree 2006; Jager/Engelmann/Vasishth 2017;
Wagers/Lau/Phillips 2009; McElree 2001; Cowan 2001; Van Dyke & Johns 2012; Hale 2006 (entropy reduction).
