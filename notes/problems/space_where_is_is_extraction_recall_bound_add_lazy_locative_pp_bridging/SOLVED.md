---
problem: space_where_is_is_extraction_recall_bound_add_lazy_locative_pp_bridging
status: PARTIAL
bar: "PASS = where_is on the MODERN space gold CI-separated over BOTH the current motion-lexicon chain AND the strongest stateless floor (last-mention), with the info-free shuffled-place twin LOSING, motion-event recall materially recovered, and NO precision regression — landed through the LIVE reader (not just the prototype harness). A rigorous located NEGATIVE (the brain's on-demand locative bridging, faithfully built, does not hold end-to-end, with the exact stage that eats the gain named) is a FULL PASS. Report the recall + where_is deltas with CIs + the twin."
result: "where_is exact-node, GP._score-style, paired bootstrap. (1) BRIEF REFUTED: the lazy locative-PP bridge lifts motion-event extraction recall 0.444->0.889 (strict) but moves end where_is only +0.064 on the modern gold (0.319->0.383, n=47, item CI [-0.021,+0.149], NOT CI-separated over the current chain). (2) REAL LEVER (conservative NAMED-GROUND BINDING): where_is MODERN 0.319->0.426 (+0.106, n=47) and REAL 19c LitBank 0.244->0.290 (+0.046, n=606, 24 timelines) -- net-positive and precision-improving on BOTH; beats the last-mention floor CI-separated (+0.277 modern / +0.277 19c) and the shuffled-ground twin CI-separated (+0.255 modern / +0.096 19c); through the LIVE SituationReader.read() stock 0.277->wired 0.404 (+0.128). The gain over the CURRENT chain is NOT CI-separated at the conservative character-timeline unit (modern [-0.021,+0.234]; 19c [-0.077,+0.172]) though it is at the 19c item level (n=606, [+0.015,+0.079])."
floor: "last-mention (strongest stateless): 0.1489 modern (n=47) / 0.0132 19c (n=606). Named-ground binding beats it CI-separated on both. Perfect-extraction CEILING (gold events folded) = 0.7872 modern -- the register/readout headroom."
controls: "shuffled-ground info-free twin (same firing rate, ground nodes permuted) LOSES on both corpora, CI-separated (modern arm 0.426 vs twin 0.170; 19c arm 0.290 vs twin 0.195) -- the ground CONTENT is load-bearing. Perfect-extraction ceiling (0.787) shows the register/readout is not the bottleneck. Precision guardrail: motion-event precision IMPROVES (modern 0.571->0.689; 19c 0.163->0.216), so the gain is not bought with false firing. Aggressive-variant can-fail: the full locative/stative-PP binding + protagonist fallback REGRESSES on real 19c prose (-0.053 to -0.078) -> only the high-precision motion-goal subset is robust (the located wall)."
files_changed: "experiments/exp_space_recall_e2e_ci_v1.py, experiments/exp_space_named_ground_binding_v1.py, experiments/exp_space_ground_binding_litbank_v1.py, experiments/exp_space_ground_binding_live_wire_v1.py, experiments/_diagnose_where_is_errors.py, verification/test_space_ground_binding.py (NO hdlab/ written)"
reverify: ".venv/Scripts/python.exe verification/test_space_ground_binding.py"
---

# Space where_is: the brief's premise is refuted, and the real lever is NAMED-GROUND BINDING

**Bottom line.** The brief said the SPACE dimension's where_is loss is motion-event **extraction recall** and the
fix is a lazy locative-PP bridge (prototyped 0.444->0.889). **The disk refutes the premise:** recovering that
recall moves the end where_is metric only **+0.064** (not CI-separated over the current chain). I located the real
bottleneck — **binding the correct NAMED GROUND to an already-detected motion event** — built the brain-foundational
mechanism for it, and showed a robust, conservative version is **net-positive and precision-improving on both a
modern and a real 19c corpus**, holds **end-to-end through the live reader**, and beats the floor and the
shuffled-ground twin CI-separated. It does **not** CI-separate over the (already decent) current chain at the honest
character-timeline unit, so I am marking this **PARTIAL** rather than claiming the full where_is-vs-current bar —
even though, by the bar's own located-negative clause, the refutation of the brief's mechanism + the named wall is a
pass-grade outcome. **THE DISK OUTRANKS THE BRIEF and it did here.**

## 1. What I verified first (the disk outranks the brief)
- Reproduced the brief's prototype: `exp_space_recall_brainfoundational_v1` -> recall 0.444->0.889, where_is
  0.319->0.383 (+0.064), and the twin-separation the brief quoted as **+0.128 is a single high-variance shuffle
  draw** — the honest control is the null distribution, and my measurement gives a far smaller, fragile twin gap
  for the recall bridge.
- Confirmed the LIVE reader runs `mode="prior_ext"` (`hdlab/situation_reader._read_space`), so the prototype's
  "current" baseline (all drill gates: realis/discovery/embedded/caused-motion/stative all ON) **exactly matches
  the live config**. The stative-locative gate, result/telic verbs, and caused-motion routing the research note
  proposed as gates 1–3 are **already built and live** in `experiments/_space_reader.py`. The only genuinely-new
  piece the brief adds is the locative-PP bridge — which I show is not the where_is lever.

## 2. The refutation, measured (`exp_space_recall_e2e_ci_v1.py`)
On the modern gold, the recall bridge lifts extraction recall a lot but end where_is barely moves and is **not**
CI-separated over the current chain (item CI [-0.021,+0.149], timeline CI [-0.049,+0.200]). **Recovering
change-point DETECTION does not recover where_is** — because where_is is bottlenecked on something else.

## 3. Where the where_is signal actually goes (`_diagnose_where_is_errors.py`)
Decomposing every where_is error, cross-referenced with the perfect-extraction CEILING (which the register hits at
**0.787**), and noting coref is **gold** on the modern set (so it is NOT the bottleneck here):

| category | share | meaning |
|---|---|---|
| **SCENE — named place not bound** | **34%** | motion detected, entity present, but where_is returns `<scene>` not the named place ("reached the office"->`<scene>`; "brought him up to a ward"->`<scene>`). The ceiling recovers ALL of these. |
| **WRONG_NODE** | 13% | wrong place bound ("locker" not room, "level" not garage, "floor" not ward). |
| SCORING_ARTIFACT | 13% | ceiling also wrong (start-state `<scene>`, AWAY/None representation) — not addressable by extraction. |
| MISSING | 2% | no location established. |

So ~49% of queries fail on **named-ground binding on already-detected motion**, all recoverable per the ceiling.
Traced to three mechanisms: (1) `route_predicate_arguments` mislabels `goal_belongs_to='theme'` on intransitive
self-motion (head/walk) -> the self-goal is dropped; (2) the goal token resolves to a comma/possessive or the
WRONG nested PP ("a ward on the fourth floor" -> "floor"); (3) a competing same-sentence scene-return ("come in",
"back") clobbers the named arrival.

## 4. The real mechanism, built and measured (`exp_space_named_ground_binding_v1.py`)
**Brain frame (PINNED):** a motion event updates the spatial model to its **Ground** — the reference place the
Figure comes to be at (Talmy 1985 Figure/Ground; Landau & Jackendoff 1993 the "where" object; Zwaan & Radvansky
protagonist-anchored WHERE-state). The reader binds the NAMED ground when the clause offers one and only falls back
to bare presence when it does not. **OUR-INVENTION-UNDER-TEST:** the ground-SELECTION heuristic (dobj vs goal-PP vs
locative-PP; nested-PP compound-HEAD selection; functional-locus typing; named-over-scene preference) — swept, not
adopted from a number.

The pass collects the clause's place-typed grounds (place-typed direct object of a destination verb; head of a
goal-prep PP; head of a locative-prep PP), picks the compound **head** noun (fixing "meeting room"->room), broadens
place-typing with a curated **functional-locus** set (desk/bed/seat/plane/car/gate/ward/... — reference objects a
person occupies that the WordNet location taxonomy misses), rejects `<scene>`/`<away>` sentinel grounds, and binds
arrive(named goal ground) preferring a named ground over a scene-return.

**The robustness split (the located wall).** The full aggressive pass (locative/stative grounds + a
protagonist fallback) helps the clean modern set (+0.170) but **REGRESSES on real 19c prose (-0.053 to -0.078)** —
eager locative-PP binding over-fires on complex real sentences, over-writing correct persistence with spurious
grounds. Only the **conservative** subset (a *genuine motion verb* naming a *goal* ground) is robust:

| corpus | n | current | ARM (conservative) | floor | twin | precision cur->arm |
|---|---|---|---|---|---|---|
| MODERN (coref gold) | 47 | 0.319 | **0.426** (+0.106) | 0.149 | 0.170 | 0.571 -> 0.689 |
| 19c LitBank (real) | 606 | 0.244 | **0.290** (+0.046) | 0.013 | 0.195 | 0.163 -> 0.216 |

- Beats the last-mention floor **CI-separated** on both (+0.277 / +0.277).
- The shuffled-ground **twin LOSES CI-separated** on both (+0.255 / +0.096) — the ground CONTENT carries the signal.
- Precision **improves** on both (no regression).
- Over the current chain: **not CI-separated** at the character-timeline unit (modern [-0.021,+0.234]; 19c
  [-0.077,+0.172]); it IS CI-separated at the 19c item level (n=606, [+0.015,+0.079], anti-conservative).

## 5. Landed through the LIVE reader (`exp_space_ground_binding_live_wire_v1.py`)
Driven end-to-end through `SituationReader(track_space=True).read()` (runtime-patching the one function the diff
touches, since a solver may not write hdlab/): **stock 0.277 -> wired 0.404 (+0.128)**, with 7 named grounds
recovered through the full pipeline that the stock reader returns `<scene>`/`<away>` for (room, desk, garage,
balcony). The diff flows through read() and is faithful.

## 6. THE PROPOSED hdlab/experiments DIFF (Q111 — strategy lands it)
1. Add `ground_bind_events(sents, mentions_by_sent, person_clusters, provider, conservative=True)` (from
   `experiments/exp_space_named_ground_binding_v1.py`) into `experiments/_space_reader.py`.
2. In `extract_events_in_substrate`, add a `ground_bind=False` kwarg; when set, append the conservative
   named-ground events to `events` before returning (using the SAME `parse_provider`).
3. In `read_locations_in_substrate`, default `ground_bind=True` in `prior_ext` mode (the live reader's mode).
4. No change to `hdlab/location_register.py` or `hdlab/situation_reader.py` behavior beyond the events it receives.
   Because coref/precision improve, this is a net-positive additive wire — recommend landing ON (per the
   no-more-default-off discipline), with the equivalence witness `verification/test_space_ground_binding.py`.
**Caveat for the lander:** land ONLY the `conservative=True` path. The full locative/stative + fallback path
regresses on real prose (Section 4) and must NOT be the live default.

## 7. What I did NOT establish / would withdraw first
- **Withdraw first:** the modern +0.106 as a stand-alone claim — n=47 is underpowered and its CI over the current
  chain includes zero. The robust claims are the 19c no-regression + net-positive, the floor/twin separations, and
  the precision improvement.
- I did **not** clear the where_is-vs-current-chain CI bar at the honest (character-timeline) unit on either
  corpus. The current chain is already decent (0.24–0.32 vs a 0.79 ceiling); my lever adds ~5–11 points, real but
  sub-threshold.
- The residual gap to the ceiling (0.79) is locked behind **relevance-gated binding** — the brain fires a locative
  inference on-demand for local coherence (McKoon & Ratcliff 1992), discriminating a location-updating PP from an
  incidental one ("in the bed" vs "the bed by the window"). We bind eagerly on every PP and cannot yet make that
  discrimination without a relevance/coherence-need signal. **This is the named stage that eats the rest of the gain.**
- **Reuse organs (INFERRED in the brief):** on both test corpora coref is gold, so `EntityBinder` was not the
  bottleneck IN THESE TESTS; but the aggressive-variant regression (protagonist fallback binding to a wrong mover)
  shows mover-coref quality WILL matter on a reader with real (non-gold) coref — reuse EntityBinder before enabling
  any aggressive binding. The curated `_FUNCLOC` set covers the world-knowledge places WordNet misses;
  `grounded_semantic_graph` ConceptNet AtLocation is the untested broader replacement (a follow-on).

## KEY REALIZATIONS
- **The diagnosis that names a metric is not the diagnosis that moves it.** "Extraction recall is 0.44" was a
  change-point-DETECTION number; where_is is a node-at-query-time number. Recovering the former (0.44->0.89) barely
  touched the latter (+0.06). The ceiling control (perfect events -> 0.79, our chain -> 0.38 at 0.89 recall) is what
  forced the reframe: the loss is node BINDING, not event detection.
- **The decomposition-against-the-ceiling was the unlock.** Categorizing every error and asking "does the ceiling
  get this right?" separated addressable node-binding losses (49%) from unaddressable scoring artifacts (13%).
- **A win on constructed clean data can be a loss on real prose.** The aggressive binding that gained +0.170 on my
  own modern sentences LOST on real 19c prose; only the high-precision subset generalized. The two-corpus test
  (one I authored, one I did not) is what caught it — a single-corpus result would have been a false SOLVED.
- **The shuffled twin is high-variance; use the distribution, not one draw.** The brief's +0.128 twin gap for the
  recall bridge was one lucky shuffle; the mechanism's real content-dependence is what survives the null.

## AUDIT UPDATE (for `BRAIN_FOUNDATIONAL_AUDIT.md`)
- SPACE extraction front-end (`experiments/_space_reader.decide_motion` / `extract_events_in_substrate`): the
  current verdict frames the where_is cap as extraction RECALL. **Correct it: the where_is cap is NAMED-GROUND
  BINDING (Talmy Figure/Ground), not change-point recall** — measured, with a perfect-extraction ceiling of 0.787
  against a live 0.24–0.38. Add the deviation: ground selection is eager (fires on every place-typed PP) where the
  brain is relevance-gated/on-demand (McKoon & Ratcliff 1992); the eager version over-fires on complex prose, so
  only high-precision motion-goal binding is currently robust.

## TLDR (plain English)
The reader can often tell that a character moved, but it frequently fails to record WHERE they moved to — it knows
"she's somewhere in the scene now" but not "she's in the office." The brief guessed the problem was that the reader
misses too many moves; I checked, and fixing that (catching far more moves) barely helped, because the real problem
is attaching the specific PLACE to the move. I built the fix — when a character goes somewhere, bind the named
place they end up at — and it helps on both modern and old text, never hurts, and gets more of the answers right
about where people are (a character ends up "in the office"/"at her desk"/"in the garage" instead of just
"present"). It runs correctly inside the real reader. It is a genuine improvement but a modest one: the reader was
already fairly good here, and my fix adds a handful of points rather than a decisive jump, so I am calling it a
partial win, not a full solve. The remaining gap needs the reader to judge WHICH place-phrase in a sentence
actually says where someone is — something the brain does by relevance and we cannot yet copy.

## QUESTIONS
None.

## NEXT STEPS
1. **Land the conservative named-ground binding** (Section 6 diff, `conservative=True` ONLY) — net-positive,
   precision-improving, holds live. Do NOT land the aggressive locative/stative + fallback path.
2. **Follow-on, higher value than this was:** relevance-gated / on-demand ground binding — the discrimination
   between a location-updating PP and an incidental one is the stage that eats the remaining 0.4->0.79 headroom.
   This is the real brain mechanism (McKoon & Ratcliff minimalist bridging) and the next problem to file.
3. Before any AGGRESSIVE binding, wire real mover-coref (`EntityBinder`) — the fallback regression shows binding to
   a wrong mover costs more than it buys on real prose.
4. Consider `grounded_semantic_graph` ConceptNet AtLocation to replace the curated `_FUNCLOC` set (broader,
   glass-box place-typing).
5. Fold the AUDIT UPDATE into `BRAIN_FOUNDATIONAL_AUDIT.md` (the SPACE cap is ground-binding, not recall).
