---
owner_verdict: DONE
---

SOLVED — the_bundle_destroys_meaning_but_replacing_it_hurts

The answer: The bundling was never the bottleneck on task c3. I built the experiment that removes the bundle entirely — explicit per-word co-occurrence counts, zero superposition loss — and it still loses to a dumb spelling matcher (0.0605 vs 0.0867, CI-separated below). No bundling operator and not surprise-weighting beats the floor. The "62% destroyed" is real but irrelevant here: c3 compares whole-word profiles, it never recovers individual words from the bundle.

Why the spelling floor was misleading: ~78% of the spelling matcher's wins are word-shape relatives (nation/national, volcano/volcanic) that the WordNet gold happens to reward. Strip stem-sharing gold and the spelling matcher collapses (0.0867 → 0.0193) while the unmodified flat bag holds (0.048 → 0.046) and beats it (+0.0266, CI [+.019,+.034]). The "string beats us 2:1" headline does not survive a fair instrument.

The brain-faithful lever (capstone): Fusing the flat bag with the grounded sensorimotor spoke (ATL hub-and-spoke) beats either channel alone, CI-separated (+0.0355 vs the bag, +0.0163 vs grounded); the random⊕grounded control fails (0.029); on the fair gold it is the best arm (0.0790, +0.060 over the floor); and the full distributional+grounded+spelling hub (0.1125) clears the floor's upper bound. Combine, don't substitute — confirmed with a grounded spoke, not the spelling stand-in.

Numbers: WordNet-neighbour hit@1, GP._score_space, n=4,000 items over 5,491 anchors, 5,000× paired bootstrap. Floor: A5_STRINGCTRL (character-trigram spelling) 0.0867, CI [0.078,0.096]. Controls: info-free RANDOM 0.0085 and per-row-shuffled co-occurrence 0.0177 (rank-tie artifact); random⊕grounded and random⊕string (fusion artifact); A1_BASE reproduces the landed 0.0480 headline exactly (harness mismatch); morphology-stripped gold (spelling-as-meaning); cosine-invariance guard. Scaffold-free witness passes 9/9 on an independent corpus.

Recommendation: Keep the flat bundler; retire the "replace the bundle" thread. Wire the measured combine — at read-out, z-score-fuse the distributional cosine with the grounded sensorimotor cosine (this is reader_meaning_channel's missing adapter). Score future c3-style gates against morphology-stripped gold.

Files: experiments/exp_c3_surprise_weighted_vs_bundling_v1.py, experiments/exp_c3_grounded_fusion_v1.py, verification/test_c3_bundling_is_not_the_bottleneck.py, plus the two metrics.json and SOLVED.md.
Reverify: .venv/Scripts/python.exe verification/test_c3_bundling_is_not_the_bottleneck.py
