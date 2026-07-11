# The Last Piece — Reasoning vs Frequency, Intuitively (+ courses) — 2026-07-10 (Director)

Written for the USER, no jargon. Enriched by the fairness+mechanism VET (ad72003c) and the crux arc; the deep brain drill (a262f47c) will verify/extend.

## The problem, plainly
We want the system to figure out facts it was never told (real reasoning). Right now it loses to a dumb strategy: "guess whatever answer-type is most common." Beating that is the last piece.

## What we just learned it is NOT (the VET correction)
We thought the reasoner was being FOOLED by popularity. It is NOT -- proven off-disk (its scores barely correlate with how common things are). The real problem is deeper and more interesting:
- The reasoner NARROWS correctly. It reaches the right answer ~42% of the time (better than the dumb guess). That part works.
- But it can't PICK the right one out of the small set it narrowed to. Every clue it has (how well-supported, how many rules point there) applies EQUALLY to the right answer and its near-misses. **Analogy: it narrows a whodunit to 5 suspects who were all at the scene, all had motive, all had opportunity -- and the evidence it holds can't tell them apart.**
- We PROVED the headroom is real: a perfect picker on its own narrowed sets would beat frequency by a wide margin (+0.164). So the answer IS findable -- we just lack the right KIND of evidence to find it. Symbolic path-counting is exhausted.

## How the brain does it (analogies)
1. **It builds a MAP, not a tally.** The brain doesn't count how many paths connect two ideas. It builds a rich geometric "map of meaning" (hippocampal cognitive maps). *You can find a route between two places you've never travelled between, because you understand the city's layout.* New facts fall out of the map's geometry.
2. **Understanding vs familiarity.** Frequency-guessing is RECOGNITION ("this feels common, go with it"). Reasoning is UNDERSTANDING ("given the structure, THIS one fits"). The brain has both and uses the second for genuine inference.
3. **It builds the map in sleep.** Replay/consolidation extracts the PATTERN behind the examples (the gist), turning memorized facts into a generative map that IMPLIES new ones -- it'll even do A->B, B->C, therefore A->C overnight. This "map-builder" is the piece we most lack.
4. **The map is geometric.** Relationships are consistent MOVES/directions in a space (grid-cell-like), so it generalizes to combinations never seen -- a lookup table can't.

## The fingerprint we're missing
The evidence that separates the right answer from its near-misses = the substrate's OWN rich learned sense of what each entity IS -- its geometric position / HD code / type. Our crux experiment already hinted this works: when it used the geometric (HD) signal, it ranked BETTER than symbolic counting. **That is the fix we're now building** -- give the picker a fingerprint (geometry), not just "was near the scene" (path counts).

## How we've tried (honest, short)
- Polished the pieces (codes, encoder, grounding) -- didn't build the map.
- Proved dense knowledge is necessary (a thin graph has nothing to infer from).
- Built a reasoning engine that NARROWS correctly but can't PICK -- because it judged by the wrong kind of evidence (symbolic counts), now proven exhausted.
- Proved the test was partly unfair (popular answers dominate on well-connected things), found the fair arena, and proved the headroom there is real and exploitable -- with richer evidence.

## What we need
1. RICH / GEOMETRIC evidence for the picker (the substrate's learned sense of each entity), to separate the answer from its near-misses. [building now]
2. A genuinely COMPOSITIONAL corpus where a map CAN be built (facts derivable from facts). Our synthetic test proved this is possible (0.86 headroom vs FB15k's ~0). [surveying now]
3. A MAP-BUILDER: a "sleep/replay" that extracts relational structure into a geometric generalizing code. The brain's actual solution; the deepest missing piece. [next]

## Courses (plotted, ranked)
- **A -- Geometric picker (now, cheap):** rank the narrowed candidates by the substrate's HD/geometric signal (+ type), exploiting the proven +0.164 headroom. If it beats frequency on the fair arena = the FIRST real reasoning win. P ~0.4 (headroom is proven; question is whether our current HD codes are discriminative enough). Risk: codes not yet sharp enough -> needs the map-builder (C).
- **B -- Compositional corpus (durable):** find/build a corpus where relations are genuinely derivable (survey running). Reasoning only has room where a map can exist. P high that a better corpus exists; it's the durable escape from the frequency wall.
- **C -- The map-builder (deepest, highest ceiling):** a replay/consolidation mechanism that extracts relational structure into a geometric code so new facts fall out of the geometry -- the brain's real answer, and what would make the picker (A) sharp. Hardest; biggest payoff.
- **They compose** into the brain's stack: a good corpus (B) + a map-builder (C) + a geometric picker (A).

## Deep brain drill result (a262f47c, landed) -- the mechanistic core + a near-term gift
notes/research_brain_beats_frequency_relational_inference_deep_drill_2026-07-10.md.
- **The brain beats frequency ARCHITECTURALLY, not by smarter weighting.** Two pieces: (1) it runs on a factorized GEOMETRIC MAP (Tolman-Eichenbaum) built OFFLINE by replay -- and that map demonstrably generates shortcuts through places never travelled (inference falling out of geometry); (2) it CAPS frequency: familiarity supplies only a BOUNDED starting-nudge (DDM starting-point) while STRUCTURAL evidence gets UNCAPPED drift -- so frequency literally cannot outvote structure. Our system has the opposite (frequency competes equally and wins). Design fix: cap the frequency prior, let structural/type evidence dominate. [folded into the Course-A build]
- **Highest-P near-term lever = RELATION-TYPE CONSISTENCY (drill course D, P=0.30-0.35 -- above HD codes).** Rank a candidate by whether its TYPE fits the relation ("capital_of" expects a country). This is exactly the non-symbolic discriminator the VET proved we need. [folded into Course A as TYPE_RANK, first-class]
- Course C (map-builder) caveat: must first confront the on-substrate stage3_hrr_involutive HARD_FAIL (a prior HD-binding limit) before a TEM-style replay map-builder is buildable.
- P ranges (deflated): type-consistency 0.30-0.35, map-builder 0.20-0.25 (highest ceiling), corpus 0.15-0.20.

## Immediate
Course A = the geometric picker, now ENRICHED with type-consistency (drill's highest-P feature) + the frequency-cap architecture -- building. B (corpus survey) booked to remote (4hr). C (replay map-builder) = deepest, next design after A shows how far current geometry reaches AND the stage3_hrr HARD_FAIL is addressed.

## RESOLUTION (2026-07-10/11 overnight -- the arc converged)
1. **COURSE A / ranker line = CLOSED.** FULL HARD_FAIL 3-seed, VET-confirmed (a165be25): HD+type+freq-cap structural ranker does NOT beat frequency on FB15k fair stratum; 2 independent fair HARD_FAILs exhaust the substrate's glass-box unsupervised ranker classes; the +0.164 headroom is real but UNREALIZABLE on FB15k. Ranker was never the lever.
2. **COURSE B / CORPUS FOUND + VERIFIED GENUINE = CSKG (HIGH confidence, VET a46eadfa).** Complete 7-corpus survey: CSKG fair-headroom 0.332 (WINNER, ~10x FB15k), and it HOLDS at high-degree (L2-only 0.226 at pop 0.412) where FB15k collapses (0.028) and where WN18RR was exposed as 91% inverse-lookup ARTIFACT. Decisive discriminator = decompose reach-ceiling by pattern kind (L2 genuine 2-hop composition vs L1I inverse vs alias) + leak fraction; CSKG L2 genuine (2886 patterns, sym-leak 5.1%), survives the degree/pop control. CRITICAL NUANCE: headroom = OPPORTUNITY (a perfect reasoner's ceiling), NOT demonstrated substrate reasoning -- CSKG is the corpus where reasoning CAN win; Course C must show the substrate DOES.
3. **COURSE C / MAP-BUILDER = the mechanism to realize CSKG's opportunity.** Design (ac375037): stage3_hrr prereq is a FIXABLE method limit (not a wall); fix = phase-rotation binding (RotatE-equiv) + continuous SSP/FPE encoding + replay-consolidation. Cheap operator-fix (SSP_FRACTIONAL, P~0.40) building now on a synthetic compositional testbed (a3546a17) -- prove the operator generalizes BEFORE scaling to CSKG.

**THE CONVERGENCE / NEXT MOVE:** operator-fix (synthetic) -> if passes, build the map-builder ON CSKG -> measure whether the substrate REALIZES CSKG's proven 0.28 reasoning opportunity, beating frequency. First time all 3 pieces (verified compositional corpus + fixable map-builder + geometric readout) line up on the RIGHT knowledge. Pending: orchestrator sync of the CSKG-genuine MM + Course-A HF + META atoms.
