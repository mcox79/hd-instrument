---
problem: theory_of_mind_is_proven_only_in_a_synthetic_microworld
status: SOLVED
bar: "De-island the HARD_PASS-but-SYNTHETIC Sally-Anne false-belief organ per its OWN revival criteria: (a) a divergent-belief NARRATIVE task, (b) run on the substrate's own FHRR organs (hdlab.binding + situation_model_accumulate) not hand-rolled numpy, (c) inputs from TEXT not a perfect symbolic codebook. The per-agent belief partition must recover FALSE beliefs and beat the shared-reality floor (which leaks the observer's knowledge to the agent) CI-separated, with an info-free twin LOSING and true-belief controls preventing a trivial always-initial shortcut. Self-scoped pickup of the orphaned ToM island (owner-directed 2026-08-26: pick up a fair-game islanded organ)."
result: "On 26 real-English false-belief passages (28 belief questions; cleanup over a 49-location vocabulary), the per-agent FHRR belief partition run on the substrate's own organs (hdlab.binding.bind/unbind + situation_model_accumulate.cleanup_argmax) scores belief-question accuracy 1.000 [1.000,1.000] -- false-belief 1.00, true-belief 1.00, reality 1.00. With the observation signal EXTRACTED FROM TEXT (a lexical cue extractor at 0.808 accuracy) it still scores 0.821 [0.679,0.964], beating the floor CI-separated; the FULL_TOM(oracle-observation) - FULL_TOM_LIVE gap localises the residual to the observation-cue front-end."
floor: "Strongest floor actually run = ALWAYS_INITIAL (the trivial 'the agent looks where it left the object' rule) belief-acc 0.643 [0.464,0.821] -- FULL_TOM 1.000 CI-separated above it. Also: shared-reality NO_TOM (answer belief from the world state = the deficit) 0.357 [0.179,0.536]; info-free twin (scrambled observation) 0.429 [0.250,0.607]; chance over 49 locations ~0.02; ORACLE 1.000 (upper bound)."
controls: "NO_TOM (shared reality) EXCLUDES 'the task is solvable without a per-agent partition' -- it leaks the observer's knowledge to the agent and fails false-belief (0.10). ALWAYS_INITIAL EXCLUDES 'just answer where it started' -- the true-belief controls (saw / was-told) make it can-fail (0.00 on true-belief). TWIN (observation bit randomised) EXCLUDES 'the partition works from a non-informative signal' -- it loses CI-separated. TRUE-BELIEF CONTROLS (2 saw-the-move + informed 'was told') EXCLUDE 'always-stale' shortcuts and test knows-vs-saw (belief tracks KNOWLEDGE, not vision). REALITY questions EXCLUDE 'the belief partition corrupts world tracking' (reality stays 1.00). FULL_TOM_LIVE (observation read from TEXT) isolates the observation front-end as the only residual. DIVERGENT two-agent items (one false + one true belief in the same scene) require genuinely separate per-agent stores. INTERFERENCE STRESS (compositional location codes, worst |sim| 0.65) EXCLUDES 'the win depends on near-orthogonal codes' -- FULL_TOM holds at 1.000."
files_changed: "experiments/exp_theory_of_mind_realtext_v1.py (new), experiments/data/gold_false_belief_realtext_v1.jsonl + gold_false_belief_realtext_v1b.jsonl (new real-text false-belief gold, 26 items), verification/test_theory_of_mind_realtext.py (new, witness PASS 2/2), data/exp_theory_of_mind_realtext_v1/metrics.json (new). hdlab/ UNTOUCHED (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_theory_of_mind_realtext.py"
---

# Theory of Mind (false belief) validated on REAL TEXT, on the substrate's own organs

## The one-line answer
The substrate's Theory-of-Mind organ was HARD_PASS but only in a synthetic symbolic microworld (islanded,
hand-rolled numpy). I built the missing real-text false-belief gold and ran the per-agent belief-partition
mechanism ON THE SUBSTRATE'S OWN FHRR ORGANS: it solves false belief perfectly on real English narrative
(1.000), CI-separated over the shared-reality floor, the trivial always-initial floor, and an info-free
twin, while keeping true-belief and reality intact. The mechanism is real and portable; the only residual
is reading the observation cue ("did the agent see the move?") from text.

## Why this problem (and how it was picked)
Owner-directed to pick up a fair-game islanded organ. Query-before-build found the two active problems
(predictive-reader, WSD) and confirmed the REAL ToM result (`exp_theory_of_mind_sally_anne_nested_hrr_v1`,
`theory_of_mind_sally_anne_nested_hrr`) is HARD_PASS (Q2 0.806 vs 0.138, oracle 1.0, 5 seeds) but
SYNTHETIC (perfect symbolic codebook), ISLANDED, and hand-rolls bind/unbind in numpy. Its own registry
revival criteria name exactly the gap: a divergent-belief NARRATIVE, run on the substrate's own organs,
with TEXT inputs. (The higher-order recursive line `exp_substrate_higher_order_tom_recursive_v1..v4` is a
DIFFERENT, synthetic, MIDDLE_BAND effort -- this is first-order on real text, additive, not a duplicate.
Note `hdlab/state_of_mind.py` is MISLABELLED: it is coreference, zero belief logic -- the live reader has
no actual belief tracking.)

## What I built
1. **The missing real-text false-belief gold** (`gold_false_belief_realtext_v1{,b}.jsonl`, 26 passages / 28
   belief Qs): real-English Sally-Anne narratives -- an agent forms a belief, the world changes in their
   absence (moved by a person, an animal, or the wind; or the agent asleep), and questions probe the
   agent's BELIEF vs REALITY. Deliberately balanced with **true-belief controls** (the agent SAW the move,
   or was TOLD) and **divergent two-agent** items (one false + one true belief in one scene). The controls
   make the task can-fail: "always answer where it started" scores only 0.64.
2. **The end-to-end measurement** (`exp_theory_of_mind_realtext_v1.py`): per-agent belief banks built with
   the substrate's OWN organs -- `hdlab.binding.bind/unbind` + `situation_model_accumulate.cleanup_argmax`
   over a 49-location vocabulary, codes seeded from the TEXT surface forms (not a perfect codebook). An
   agent who did not observe a move keeps the OLD binding (stale = false belief); observers/informed agents
   and the world bank update. Arms: NO_TOM (shared reality), FULL_TOM (oracle observation), FULL_TOM_LIVE
   (observation read from text), TWIN (scrambled observation), ORACLE, ALWAYS_INITIAL.

## What I measured
FULL_TOM belief-acc **1.000** (false-belief 1.00, true-belief 1.00, reality 1.00) vs floors NO_TOM 0.357 /
ALWAYS_INITIAL 0.643 / TWIN 0.429 -- CI-separated over all three. **FULL_TOM_LIVE** (observation extracted
from text at 0.808 accuracy) **0.821 [0.679,0.964]**, still beating the floor CI-separated. All 7 pre-stated
gates pass. Brain frame: false belief is the canonical ToM test (Wimmer & Perner 1983; Baron-Cohen/Leslie/
Frith 1985); the mentalizing network (TPJ/mPFC; Saxe & Kanwisher 2003) keeps belief representations SEPARATE
from the observer's own knowledge -- which is exactly what the per-agent partition does and the NO_TOM floor
(which leaks reality to the agent) fails to do.

## What I did NOT establish (and would withdraw first)
- **The observation front-end is not solved.** FULL_TOM uses the gold's observation field; FULL_TOM_LIVE's
  lexical extractor is 0.808, dropping end-to-end to 0.821. Reading "did the agent witness the change?" from
  arbitrary prose is the real residual (and the same front-end-is-the-wall theme as the wire-organs problem).
- **The gold is AUTHORED, not corpus-mined.** It is natural-English TEXT (not a symbolic codebook, satisfying
  the revival criterion), but I wrote it; the answers are unambiguous by construction. First thing I'd
  withdraw if wrong: any claim of *corpus* generality -- a follow-on should mine/verify real story passages.
- **First-order only.** Higher-order ("A thinks B thinks") is the separate recursive line (MIDDLE_BAND); not
  claimed here.
- (RESOLVED, was a caveat) Location-interference stress: rebuilding location codes COMPOSITIONALLY so
  similar phrases share components (worst pairwise |sim| 0.65 vs ~0 orthogonal) leaves FULL_TOM at 1.000 and
  NO_TOM at 0.357 -- the single-binding-per-object belief store is robust to location interference, not
  reliant on near-orthogonal codes. (An 8th gate, `full_tom_robust_to_location_interference`, now guards this.)

## KEY REALIZATIONS
- **The recurring bottleneck across every fair-game organ is real-text GOLD, not another mechanism.** Foraging,
  ToM -- each was validated-but-synthetic and blocked from real-text measurement by missing gold. The
  highest-leverage move was to BUILD the gold; the mechanism then validated immediately. This is the
  wire-organs problem's lesson one level down.
- **Belief tracks KNOWLEDGE, not vision.** The first run scored true-belief 0.67 because FULL_TOM gated on
  "saw the move"; the informed-true-belief control ("was told") forced the correct signal = "knows" (saw OR
  informed). The can-fail control named the fix.
- **Power is a first-class control.** At 11 belief questions the mechanism was already at 1.00 but could not
  CI-separate from the floors; expanding the gold to 28 was what turned a visible effect into a gated result.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
- **Theory of Mind is no longer synthetic-only.** The false-belief per-agent-partition mechanism is validated
  on REAL TEXT on the substrate's own organs (`hdlab.binding`), belief-acc 1.000 over a 0.643 trivial floor,
  twin losing. The `theory_of_mind_sally_anne_nested_hrr` island's revival criteria (a)+(b)+(c) are MET for
  first-order belief. The live reader still has NO belief tracking (`hdlab/state_of_mind.py` is coref,
  mislabelled). Deviation: the situation model is single-perspective; a faithful reader needs per-agent
  belief partitions (Saxe TPJ). Residual = the observation-cue front-end (consistent with the front-end being
  the binding constraint found in `wire_the_validated_organs...`).

## PROPOSED hdlab CHANGE (NOT landed -- strategy re-verifies + lands, Q111)
1. Promote the belief-partition mechanism to a real organ: extend the situation model with PER-AGENT belief
   banks + a knowledge-gate (an agent's bank updates on a move only if the agent observed OR was informed),
   built on `hdlab.binding` + `situation_model_multibank` (the mechanism already uses the substrate's organs;
   this is a small extension, not a rebuild -- unlike the hand-rolled numpy cell). Default-off flag.
2. The load-bearing residual is an OBSERVATION-CUE extractor (did agent A witness event E?) from text -- file
   as the follow-on; it is the same front-end class as the verb-argument role assigner and belongs with the
   reader front-end work, not the ToM organ.
3. Do NOT wire `hdlab/state_of_mind.py` as ToM (it is coreference; keep the mislabel note).

## TLDR
Our "does the character know the world changed?" ability had only ever been shown in a toy world with perfect
symbols. I wrote a small set of real English stories where someone believes something that's no longer true
(a marble moved while they were out), with trick controls so the system can't cheat, and ran our real
memory machinery on them. It gets false belief exactly right (100%) and clearly beats "assume everyone knows
the truth" and "assume they look where they left it." The one thing still hard is reading from the text
whether the character actually saw the change -- the same first-read weakness we keep finding.

## QUESTIONS
None.

## NEXT STEPS
1. Land the per-agent belief-partition organ (default-off) on `hdlab.binding` + `situation_model_multibank`.
2. Build the observation-cue extractor (did agent A witness event E?) -- route with the reader front-end work.
3. Follow-on: corpus-mine + verify real story passages with false belief (beyond authored gold); test
   interference among similar locations; then higher-order ToM on real text (the recursive line is
   MIDDLE_BAND synthetic).

---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-28 (strategy session; grade EXCELLENT; owner authorized integration in-session)
> (Self-scoped pickup: this problem has only a SOLVED.md — no PROBLEM.md — so the review is recorded here.)
> **Re-verified FIRST-HAND** (`verification/test_theory_of_mind_realtext.py`, 2/2 PASS — ran it myself): FULL_TOM belief-acc
> 1.000 [1.000,1.000] > NO_TOM 0.357, ALWAYS_INITIAL 0.643, TWIN 0.536; false-belief solved 20/20.
> **Argument audit:** the per-agent belief partition (an agent who did not observe keeps the STALE binding) runs on the
> substrate's OWN organs (hdlab.binding + cleanup_argmax), NOT hand-rolled numpy — de-islanding the synthetic HARD_PASS onto
> REAL English narrative (revival criteria a/b/c MET). Controls are strong and complete: the shared-reality floor LEAKS the
> observer's knowledge and fails false-belief (0.10); true-belief controls (saw/informed) make it can-fail and prove belief
> tracks KNOWLEDGE not vision; the info-free scrambled-observation twin loses; reality stays 1.00 (no corruption); an
> interference-stress gate holds at 1.000 under non-orthogonal compositional codes. Brain-faithful (TPJ/mPFC mentalizing keeps
> belief separate from the observer's knowledge — exactly the partition; the floor that fails is the one that leaks).
> **HONEST SCOPE (the solver's own deflations, upheld — this is why it grades excellent-FOR-ITS-CLAIM, not overclaimed):**
> the gold is AUTHORED real-English narrative (satisfies "text, not a codebook" but is NOT corpus-mined → a mechanism
> demonstration, not a corpus-generality claim); the perfect 1.000 uses ORACLE observation, and the true end-to-end with the
> observation read FROM TEXT is 0.821 (the residual localises to the observation-cue front-end — the same "front-end is the
> wall" theme); first-order belief only. None of these is overclaimed; the follow-ons are named.
> **hdlab LANDED (Q111):** `hdlab/belief_partition.py` (`BeliefPartition` + the `believed_location` knowledge-gate; ports the
> mechanism VERBATIM on the substrate's organs; the observation flag is an INPUT — the text extractor stays a separate
> follow-on). Witness `verification/test_belief_partition_organ.py` PASS first-hand (false 5/5, true 5/5, divergence,
> random-observation twin 0.49 loses, glass-box). Registered `belief_partition_v1` (BUILT/ISLAND, default-safe). AUDIT UPDATE
> folded (§2b). **FOLLOW-ONS (not blocking): the observation-cue extractor (route with the reader front-end work); corpus-mined
> false-belief gold; higher-order ToM.** The live reader still has NO belief tracking (state_of_mind.py is coref, mislabelled).

INTEGRATED_BY_STRATEGY: 2026-08-28 (grade EXCELLENT, owner-authorized in-session). Re-verified FIRST-HAND (2/2 PASS). Landed
hdlab/belief_partition.py + witness test_belief_partition_organ.py (PASS) + registered belief_partition_v1. AUDIT UPDATE folded.
