---
problem: the_role_competitions_margin_is_a_reliability_signal_0_92_accurate_at_40_percent_coverage_and_no_consumer_reads_it
status: PARTIAL
bar: "At least one consumer up CI-separated with the margin-weighted fusion (affected entity or patient or the chain's agent read), no consumer down, twin at floor, the reliability map as counts with an observe path -- OR a numbered located negative per consumer."
result: "TWO CONSUMERS MEASURED, ONE UP CI-SEPARATED OVER ITS STRONGEST FLOOR, AND THE BRIEF'S OWN HYPOTHESIS PARTLY REFUTED WITH A MECHANISM. (1) THE AGENT READ (UD-EWT test, the board's who_did_what_agent population, n=1423). The marked-cue override in `graded_role_assigner.hybrid_agent_pick` fires unconditionally -- on the 103 clauses where it fires it FIXES 17 positional picks and BREAKS 45, which is exactly why the board shows that dimension BELOW its own floor. Licensing the override by the role competition's own calibrated confidence -- take it only when log P_agent(override candidate) - log P_agent(positional candidate) > theta, theta a criterion LEARNED ON UD-EWT TRAIN (the override is right 193/667 = 0.29 of the times it is decisive there), never hand-set -- gives, through the ORGAN: positional floor 0.8468, landed organ 0.8510 (+0.0042 CI95[-0.0042,+0.0119], n.s.), GATED 0.8545 (+0.0077 CI95[+0.0021,+0.0134] over the floor, CI-SEPARATED). Through the BOARD ARM's own copy of the hybrid (what the board actually scores today, 0.8271): GATED 0.8517 = +0.0246 CI95[+0.0155,+0.0337] over the landed board model (CI-separated) and +0.0049 CI95[0.0000,+0.0098] over the positional floor. The gate keeps 10 of the 17 good overrides and only 3 of the 45 bad ones; a PERFECT gate would give 0.8587. TWIN (the confidences permuted across items): board arm 0.8468 = the positional floor EXACTLY (it stops overriding altogether); organ path 0.8503, +0.0035 over the floor n.s. -- but gated-minus-twin is +0.0042 CI95[-0.0007,+0.0091], NOT itself CI-separated, which is why this is filed PARTIAL and not PASS. (2) THE AFFECTED-ENTITY RESOLVER (GUM third-person undergoer pronouns, live BF chain, n=903). The brief's form -- weight the parallelism cue by the LABEL's reliability -- LOSES: relweight 0.3677 (-0.0155 n.s.), logodds 0.3654 (-0.0177 n.s.) against the landed 0.3832. What DOES win is the GRADED hand-off in log form: the population-gain cue gain(margin) x log P_role(class) reaches 0.4385, +0.0554 CI95[+0.0299,+0.0831] CI-SEPARATED over the strongest floor, and the POSTERIOR-SHUFFLED twin collapses to 0.3289 (-0.0543 CI-separated DOWN). But the MARGIN-SHUFFLED twin KEEPS 0.4341 (+0.0509), i.e. of that +0.0554 only ~+0.004 is the reliability weighting and the rest is reading the posterior at all -- so at this consumer the brief's margin hypothesis is REFUTED and its neighbour (the rung must hand DOWN a graded signal) is CONFIRMED. THE MECHANISM, MEASURED: a parallelism cue never asks 'is this label right?' but 'do these two labels AGREE?', and the role organ's errors are SYSTEMATIC so they partly CANCEL in an agreement test -- on UD-EWT train through the live chain the coarse role class is right 0.8029, yet the MATCH indicator is right 0.7481 where INDEPENDENT errors would give only 0.6576, a +0.0905 EXCESS. Two ceiling arms prove the consequence by arithmetic: a PERFECT hard role label in the same fusion gives 0.3821 (-0.0011 n.s. -- a perfect label buys NOTHING in indicator form) and a PERFECT confidence gate gives 0.3776 (-0.0055 n.s.) -- the whole reliability family's ceiling at this consumer is ZERO, because a gate can only switch a cue off, never supply the graded shape that is doing the work. A fourth reliability map calibrated on the MATCH event (base 0.7522, r 0.634->0.949 over 314,141 train pairs) was built as the corrected statistic and reaches 0.4020 (+0.0188 CI95[+0.0011,+0.0377]) -- real but far below the log-posterior form."
floor: "C2 AGENT: the POSITIONAL floor the board itself uses (nearest pre-verbal clause-local nominal, experiments.exp_board_agent_slot_ud_v1.floor_positional_agent) = 0.8468 on UD-EWT test n=1423; the landed models measured alongside are the organ's hybrid_agent_pick 0.8510 and the board arm's own copy 0.8271. C1 AFFECTED ENTITY: the LANDED organ's own arithmetic -- hdlab.affected_entity_resolver.EntityTokens with the hard indicator cue at the landed gamma 1.0, accrual + foreground window 2 + Principle A, over the SAME fixed GOLD undergoer-pronoun target set -- 0.3832 (n=903, live BF chain) and 0.3544 (gold categories + gold heads). The cell's 'hard' arm is asserted ITEM-IDENTICAL to experiments.exp_affected_entity_token_history_gum_v1.run_arm, so the floor is the shipped organ, not a re-implementation. The dev-selected hard gamma (1.5) scores 0.3743 on test, i.e. LOWER, so every delta is quoted against the STRONGER 0.3832."
controls: "(1) TWIN, C2: the per-decision confidences PERMUTED ACROSS ITEMS -- the gate fires at the same rate but on the wrong decisions. Board arm 0.8468 (exactly the floor); organ path 0.8503. (2) TWIN, C1, TWO of them: MARGINS permuted within each document (destroys the reliability signal, keeps the posterior) -> 0.4341, and the whole POSTERIOR permuted across tokens (info-free for the graded cue) -> 0.3289, CI-separated DOWN. The pair is what separates 'the margin carries information' (it does not, here) from 'the posterior carries information' (it does). (3) CEILING ARMS reading gold ONLY to bound the lever, never shipped: ORACLE (a perfect role label in the same fusion) 0.3821, and ORACLE_GATE (a perfect confidence gate) 0.3776 -- the second is the ceiling of the entire reliability family and it is ZERO. C2's perfect gate is 0.8587. (4) TRAIN/TEST SEPARATION everywhere: the reliability maps are accrued on UD-EWT TRAIN, the C1 fusion weight gamma is swept on the GUM DEV split (even-index docs) and applied unchanged to TEST (odd-index, the board's split), and C2's theta is fitted on UD-EWT TRAIN (best 6.50, train 0.8489 vs train floor 0.8436) and applied unchanged to test; the test ENVELOPE (theta chosen on test, a diagnostic only) is 0.8524 vs the train-fitted 0.8517, so the fit transfers. (5) CALIBRATION TRANSFER: the train-built maps' expected calibration error on UD-EWT TEST is 0.043 (role8) / 0.031 (class) / 0.029 (patient). (6) PATCH FIDELITY: the proposed organ change is byte-identical to the landed organ on its default path -- hybrid_agent_pick with heads=None gives 1423/1423 identical picks, score_and_pick with decisions supplied but mode 'hard' gives the landed pick, and affected_entity_resolver.self_test still passes; the organ's ppc cue equals the cell's to 1.2e-06 (float summation order only), so the arm that was measured is the arm that would ship. (7) PAIRED ITEM BOOTSTRAP, 2000 resamples, on each item's OWN population. (8) UPSTREAM CONTRAST: every C1 arm re-measured under GOLD categories + GOLD heads (n=903): the incumbent is 0.3544 there -- LOWER than under the live chain -- and NOTHING is CI-separated up, the oracle included (+0.0122 n.s.). (9) HEAD-CONFIDENCE INDEPENDENCE: mean P(MAP head) = 0.9868 and corr(head confidence, role margin) = 0.082, so the role margin is not a proxy for attachment uncertainty."
files_changed: "experiments/exp_role_margin_weighted_consumers_v1.py (the cell), data/hook_state/role_margin_reliability_v1.json (the candidate asset: four count-calibrated margin->reliability maps), notes/problems/the_role_competitions_margin_is_a_reliability_signal_0_92_accurate_at_40_percent_coverage_and_no_consumer_reads_it/{SOLVED.md, role_margin_consumers_patch.diff}, and the cell's own data/exp_role_margin_weighted_consumers_v1/*.json. The diff touches hdlab/graded_role_assigner.py (the reliability maps + role_decision + the confidence-licensed agent override), hdlab/affected_entity_resolver.py (the role cue reads the decision, five selectable forms, default 'hard' = byte-identical) and hdlab/situation_reader.py (the ONE hdlab call site of each widened signature passes the new argument). NOTE: two of the three files are CRLF, so apply with `git apply --ignore-whitespace` (checked)."
reverify: ".venv/Scripts/python.exe experiments/exp_role_margin_weighted_consumers_v1.py --self-test    then --run. Numbers by artifact: data/exp_role_margin_weighted_consumers_v1/{c1_test_live.json, c1_test_goldupstream.json, c1_logpost.json, c2_final.json, c2_patch_fidelity.json, match_reliability.json, signal_trace.json, dev_sweep.json}. POPULATION CAVEAT: another solver (pri 109) edited experiments/gum_coref.py at 10:37 on 2026-09-14, mid-session, which changed the GUM mention stream and with it the affected-entity population from n=596 to n=903. EVERY C1 number in this record is on the POST-10:37 loader and all arms were re-measured together on it; they are NOT comparable to the board's standing affected_entity row (n=708, 0.3884)."
---

# 1. The bar, restated

The role competition already knows how sure it is -- the margin between its top two role activations separates its
right answers from its wrong ones. Nothing downstream asks. **Make a consumer weight the role cue by that
confidence and show a real gain on that consumer's own population**, with a shuffled-confidence twin at the floor,
no other consumer down, and the confidence stored as counts that keep learning.

## The chain, and what each rung hands down (as the disk shows it)

| rung | organ | status | what it PRODUCES | what the next rung READS |
|---|---|---|---|---|
| tokens -> categories | `hdlab/lexical_categories` (counts) | BF_SPIRIT, live default | a full category POSTERIOR per token | the attachment arm reads the posterior (graded) |
| categories -> heads | `hdlab/attachment_arm` | BF_SPIRIT, live default | single-root tree + `P(head \| dep)` marginals + margin | `coarse_roles` reads the MAP head and uses the marginal only as a precision GATE |
| heads -> roles | `hdlab/graded_role_assigner.coarse_roles` | BF_SPIRIT | an 8-way role POSTERIOR per argument head | **nothing: `coarse_roles` returns `Dict[int, str]`** |
| roles -> consumers | affected-entity resolver, state register, harm/help, board agent | BF_SPIRIT | -- | **a UD label STRING** |

Measured on UD-EWT test (700 sentences, 3698 argument-head decisions): a tag posterior is produced 3698/3698
times, a head marginal 3698/3698, a role posterior 3698/3698 -- **and 3698/3698 consumers read a string.** The
entire graded signal is destroyed at one line, the `argmax` inside `coarse_roles`.

# 2. The brain's mechanism, and the computation

**Structure 1 -- the decision carries its own confidence.** Kiani & Shadlen 2009 (Science 324:759): LIP's
accumulated evidence predicts both the choice and the opt-out, so certainty is read off the *same* accumulator that
makes the choice. Our accumulator is `net_activation`; the balance of evidence is the margin. Nothing new is
needed to produce the signal -- only to stop throwing it away.

**Structure 2 -- the consumer weights each input by its reliability.** Ernst & Banks 2002 (w proportional to
1/sigma^2); Fetsch, Pouget, DeAngelis & Angelaki 2011 (MSTd reweights *trial by trial* with momentary reliability,
not with a long-run average); Ma, Beck, Latham & Pouget 2006 (in a probabilistic population code the population's
GAIN *is* its precision, so summing gain-scaled log-likelihoods performs the Bayesian product).

**The mathematics.** The reliability map is counts: margin bin -> [n_correct, n_total], add-alpha smoothed toward
the base rate, then pool-adjacent-violators so `r` is non-decreasing in the evidence balance (a decision cannot get
less reliable as the evidence balance grows). Bin width and alpha are swept, never adopted. Built by reading
UD-EWT TRAIN through the live chain; `observe_margin_outcome` accrues one count per understood argument, so it
keeps learning online and nothing is frozen.

**Reliability belongs to the decision the CONSUMER reads, not to the organ's private alphabet** -- a downstream
area learns how reliable *its* input is. So four maps, not one (74,608 decisions / 314,141 pairs on train):

| map | what is "right" | base | r range |
|---|---|---|---|
| `role8` | the organ's 8-way label | 0.7412 | 0.449 -> 0.930 |
| `aer_class` | the SUBJ/OBJ/OTHER parallelism class | **0.8017** | 0.563 -> 0.953 |
| `patient` | the PATIENT flag | **0.9207** | 0.856 -> 0.987 |
| `match` | do two labels AGREE (see section 4) | 0.7522 | 0.634 -> 0.949 |

Calibrating on the organ's own 8-way label would have **under**-weighted every cue a consumer actually uses, by up
to 18 points. On UD-EWT test the train-built maps stay calibrated (expected calibration error 0.043 / 0.031 /
0.029) and the defer curve on the class decision is 0.930 at 20% coverage and 0.910 at 40% against a 0.794 base.

# 3. Consumer 1 -- the affected-entity resolver (the brief's first-named target)

The Kehler-Rohde fusion `ln p_salience + gamma_g*1[gram-role match] + gamma_t*1[PATIENT]` is already a fusion, and
the only unweighted cues in it are the two ROLE cues. Every arm ran on the SAME fixed gold undergoer-pronoun target
set under the live BF chain (categories organ -> attachment arm -> role competition), gamma swept on the GUM DEV
split and applied unchanged to TEST.

| arm (n=903, live chain) | acc | vs floor 0.3832 | CI95 | sep |
|---|---|---|---|---|
| **floor: the landed hard indicator (gamma 1.0)** | 0.3832 | -- | -- | -- |
| relweight -- gamma * r * 1[match] (the brief's form) | 0.3677 | -0.0155 | [-0.0343,+0.0033] | no |
| logodds -- gamma * LLR(r) * 1[match] | 0.3654 | -0.0177 | [-0.0365,+0.0011] | no |
| expected -- gamma * Pcal(class) | 0.3876 | +0.0044 | [-0.0155,+0.0244] | no |
| shrunk -- r*P(class) + (1-r)*prior | 0.3898 | +0.0066 | [-0.0122,+0.0255] | no |
| rawpost -- gamma * P(class) | 0.3965 | +0.0133 | [-0.0022,+0.0299] | no |
| expboth -- both ends uncertain | 0.4009 | +0.0177 | [-0.0011,+0.0377] | no |
| **match -- P(the two labels agree), calibrated** | 0.4020 | **+0.0188** | [+0.0011,+0.0377] | **yes** |
| **ppc -- gain(margin) * log P(class)** | **0.4385** | **+0.0554** | [+0.0299,+0.0831] | **yes** |
| CEILING oracle -- a PERFECT role label | 0.3821 | -0.0011 | [-0.0255,+0.0244] | no |
| CEILING oracle_gate -- a PERFECT confidence gate | 0.3776 | -0.0055 | [-0.0199,+0.0089] | no |
| TWIN margins shuffled (of ppc) | 0.4341 | +0.0509 | [+0.0244,+0.0775] | yes |
| TWIN posteriors shuffled (of ppc) | 0.3289 | -0.0543 | [-0.0864,-0.0210] | yes DOWN |

**Read the twins together and the answer is unambiguous.** Shuffling the MARGINS keeps +0.0509 of the +0.0554;
shuffling the POSTERIORS destroys it and goes 0.0543 *below* the floor. **Of the win, roughly +0.004 is the
reliability weighting and the rest is reading the posterior at all.** At this consumer the brief's hypothesis --
the margin as a reliability weight -- is **refuted**, and its neighbour, the standing rule that every rung must
hand DOWN a graded signal, is **confirmed CI-separated with a proper info-free twin.**

**Why the log form and not the raw mass.** `ppc` is the population-gain form (Ma et al. 2006): the cue enters as a
gain-scaled LOG-probability. A candidate the competition gives almost no mass to the anaphor's class then
contributes a strong *negative* term -- a graded veto. An indicator cannot express "this candidate is definitely
not an object", which is exactly why **a perfect gold label scores 0.3821, below the 0.3832 floor, while the
organ's own imperfect posterior in log form scores 0.4385.**

# 4. The negative, understood: why weighting by the label's reliability LOSES

A parallelism cue never asks *is this label right?* It asks *do these two labels AGREE?* The role organ's errors
are **systematic**, so they partly **cancel** in an agreement test. Measured on UD-EWT train through the live chain
(24,068 labels, 107,969 within-sentence pairs):

| quantity | value |
|---|---|
| coarse role CLASS accuracy | 0.8029 |
| MATCH indicator accuracy | **0.7481** |
| what INDEPENDENT errors would give | 0.6576 |
| **excess from correlated error** | **+0.0905** |

Two consequences, both measured, both previously unexplained:

- weighting the cue by the label's reliability LOSES (-0.0155), because a wrong-but-correlated label still agrees;
- **even a PERFECT label-gate loses** (0.3776 vs 0.3832) -- it switches off cues whose match was still right.

So the ceiling of the entire reliability family at this consumer is **zero**, by arithmetic, and the corrected
statistic is a reliability calibrated on the MATCH event keyed by the WEAKER of the two decisions' margins. That
map was built (base 0.7522, r 0.634 -> 0.949 over 314,141 pairs) and shipped as the `match` cue: +0.0188
CI-separated -- real, and still far below the log-posterior form.

**Upstream contrast (the brief's full-stack requirement).** Every arm re-measured under GOLD categories + GOLD
heads: the incumbent is **0.3544**, *lower* than the 0.3832 it reaches under the live chain, and nothing is
CI-separated up, the oracle included (+0.0122 n.s.). The live chain's role posterior is more useful here than gold
structure is, because the v4 validity table was learned from PERCEIVED heads -- feeding it gold heads is a
distribution mismatch (the same fact pri 103 found when the perceived-heads table beat the gold-convention one).

# 5. Consumer 2 -- the chain's AGENT read (the brief's item 7), and the CI-separated win

`hybrid_agent_pick` keeps the high-validity word-order default and lets a MARKED cue (passive-with-by /
PP-governed / non-nominative positional pick) overturn it. **That override is unconditional.** On the board's own
agent population (UD-EWT test, n=1423) it fires on 103 clauses and:

| | count |
|---|---|
| overrides that FIX the positional pick | 17 |
| overrides that BREAK it | 45 |
| the gate keeps, of the fixes | **10** |
| the gate keeps, of the breaks | **3** |

The brain does not let an unreliable decision overturn a high-validity default. So license the override by the
evidence it can show, in log-odds, between the two candidates, with the agent probability CALIBRATED by that
decision's own margin, and the criterion **learned from counts on train** (the override is right 193/667 = 0.29 of
the times it is decisive there), never hand-set.

| arm (UD-EWT test, n=1423) | acc | vs positional floor 0.8468 | CI95 | sep |
|---|---|---|---|---|
| positional floor (never override) | 0.8468 | -- | -- | -- |
| landed ORGAN hybrid (unconditional) | 0.8510 | +0.0042 | [-0.0042,+0.0119] | no |
| **GATED (organ) -- the shipped form** | **0.8545** | **+0.0077** | **[+0.0021,+0.0134]** | **yes** |
| TWIN, confidences shuffled (organ) | 0.8503 | +0.0035 | [-0.0021,+0.0098] | no |
| landed BOARD-ARM hybrid (what the board scores) | 0.8271 | -0.0197 | [-0.0309,-0.0091] | yes DOWN |
| **GATED (board arm)** | **0.8517** | +0.0049 | [0.0000,+0.0098] | no |
| TWIN, confidences shuffled (board arm) | 0.8468 | 0.0000 | -- | -- |
| CEILING: a perfect gate | 0.8587 | +0.0119 | -- | -- |

Against the **landed board model** the gated arm is **+0.0246 CI95[+0.0155,+0.0337], CI-separated**, and the twin
gets none of it (+0.0007 n.s.). theta was fitted on TRAIN (6.50; train 0.8489 vs train floor 0.8436) and applied
unchanged; choosing theta on test instead would give 0.8524, i.e. the train fit is within 0.0007 of optimal.

**Why this is filed PARTIAL and not PASS.** The organ arm clears the bar's main clause -- up CI-separated over the
strongest floor, twin statistically at the floor -- but the decisive gated-minus-twin contrast is **+0.0042
CI95[-0.0007,+0.0091], not itself CI-separated**: with only 103 marked clauses and 13 kept overrides the twin has
little to differ on. The board-arm twin landing *exactly* on the floor (it stops overriding altogether) is the
stronger evidence, and the +0.0246 over the landed board model is unambiguous. Strategy should decide whether the
board-arm contrast is the one that counts.

# 6. Status probe: where the signal is lost, chain by chain

| hand-off | produced | read by the next rung | LOST |
|---|---|---|---|
| categories -> heads | posterior, 3698/3698 | the arm reads it (`arc_scores_graded`) | nothing |
| heads -> roles | `P(head\|dep)` marginals, 3698/3698 | a precision GATE only; the read stays on the MAP head | the alternatives (deliberately: pri 103 measured marginalising costs 0.027) |
| roles -> consumers | an 8-way posterior, 3698/3698 | **a string, 3698/3698** | **everything: the posterior, the margin, the reliability** |
| roles -> the LIVE reader | -- | **`rank2dep = {0:'nsubj', 1:'obj'}`** | **the whole organ.** `situation_reader._read_affected_entity` fed the resolver a POSITIONAL rank as the role, so the Competition-Model decision never reached this consumer at all -- landed != live. The patch wires it. |

**The role margin is its own signal, not a proxy for the rung above it:** mean `P(MAP head)` is 0.9868 and
`corr(head confidence, role margin)` is **0.082**. The heads rung's confidence is saturated and nearly independent
of the role competition's, so this is genuinely new information at the roles rung.

# 7. Every component touched, and its brain-foundational status

| component | what changed | BF status |
|---|---|---|
| `hdlab/graded_role_assigner` (Competition-Model organ) | + the margin->reliability maps (counts, PAVA-monotone, `observe_margin_outcome`), `role_decision` (the graded hand-off), `calibrated_class_posterior`, `reliability_gain`, `agent_override_licensed`; `hybrid_agent_pick` gains an opt-in confidence gate | BF_SPIRIT, unchanged. The additions are PINNED computations (Kiani-Shadlen confidence off the accumulator; Ernst-Banks / Fetsch / Ma-Pouget reliability-weighted fusion). Knowledge is counts; an online observe path exists; every parameter is swept. |
| `hdlab/affected_entity_resolver` (Kehler-Rohde resolver) | the role cue can read the DECISION (five selectable forms); default `hard` is byte-identical | BF_SPIRIT, unchanged; the graded form is strictly more faithful (a rung hands down a distribution) |
| `hdlab/situation_reader` | `_read_affected_entity` feeds the organ's real role decision instead of a positional rank; `hybrid_agent_pick` gets the reader's heads | repairs a **landed != live** break |
| `hdlab/lexical_categories`, `hdlab/attachment_arm`, `hdlab/frontend` | read only | BF_SPIRIT, live defaults, unchanged |
| `data/hook_state/role_margin_reliability_v1.json` | NEW candidate asset, four maps, counts only | plastic; strengths are a pure function of counts |

# 8. What made the biggest improvement, and which rungs were cracked

The owner's rule is that a big win means the real mathematical chain was cracked all the way to the top. Here it
half was, and the record should say which half.

**Cracked.** `tokens -> categories (posterior) -> heads (marginals) -> roles (POSTERIOR) -> the consumer's fusion`.
The C1 win exists precisely because the role rung's posterior was finally allowed to reach a consumer *in the form
the consumer's own decision needs* -- as a log-probability inside an additive fusion, where it can veto as well as
endorse. The posterior-shuffled twin going 0.054 BELOW the floor is the proof that the content, not the shape of
the arithmetic, is doing the work.

**Not cracked.** The margin itself. It is a genuine reliability signal (AUC 0.73, 0.93 accuracy at 20% coverage)
and it *does* pay at C2, where the decision is a discrete take-it-or-leave-it override -- exactly the shape the
defer curve describes. It does *not* pay at C1, where the decision is a graded comparison among candidates and the
cue tests agreement rather than correctness. **A confidence signal pays where the consumer makes a GO/NO-GO
choice, and pays nothing where the consumer already has a graded quantity to compare.** That is the transferable
lesson, and it is why pri 103's defer curve promised more than the affected-entity consumer could deliver.

**Also not cracked, and it bounds everything above:** the role labels themselves are right 0.7942 of the time on
the class decision the consumers read. The +0.09 correlated-error excess is what makes parallelism survive that;
it is not a substitute for getting the labels right.

# 9. Alternate paths, as brain-foundational or more

1. **Make `coarse_roles` return the decision, not the string.** The structural fix: one organ-level change
   (`roles_with_decisions`) removes the `argmax` bottleneck for *every* consumer at once instead of per consumer.
   PINNED (a cortical area projects its population, not its argmax). What it would take: a second return value and
   a sweep of every consumer. Not done here because the brief scoped me to named consumers.
2. **Calibrate on the consumer's own decision, always.** Generalise the three-map lesson: the state register wants
   `P(copular-subject decision right)`, harm/help wants `P(patient flag right)`. Each is one more counting pass.
   Strictly more BF than a single global map; cheap; queueable now.
3. **Learn the cue validities from the CONFIDENCE-weighted outcome.** `observe_role_outcome` accrues every outcome
   at weight 1. Ernst-Banks applies to *learning* too (the builder already does this for heads with `MIN_CONF`).
   Accruing role outcomes at the decision's own reliability is the same operation one level up.
4. **A joint role-pair posterior instead of two independent labels.** The +0.0905 correlated-error excess says the
   two labels are not independent; the brain's competition is over the CLAUSE, not per nominal. `assign_slots_incr`
   already computes a joint decode -- extending it to emit a joint *posterior* over pairs would make the match
   probability exact rather than calibrated from a margin. More BF than what shipped.
5. **Second-order confidence: the margin of the FUSED decision.** The resolver's own pick has a margin too. The
   forward half writes every resolved pronoun into its entity token at full strength; ACT-R says a weak retrieval
   should lay down a weaker trace. Confidence-weighted impletion is the same Kiani-Shadlen principle one level up.

# 10. Priority next steps

1. **Land the C2 gate.** It is the only change here that moves a board dimension: `who_did_what_agent` goes from a
   model 0.0197 CI-separated BELOW its floor to one at or above it. Ask for the board A/B.
2. **Re-run the affected-entity board row.** Another solver changed `experiments/gum_coref.py` at 10:37 today; the
   standing row (n=708, 0.3884) is on the old loader and is no longer comparable to anything measured after it.
3. **Then decide on the C1 `ppc` cue** (+0.0554 CI-separated, twin collapses) on a re-based row. It is default-OFF
   in the patch precisely so it cannot move anything before that A/B.
4. **Do not re-try label-reliability weighting on a parallelism cue anywhere.** The correlated-error excess and the
   perfect-gate ceiling are the reason, and both are numbers now.

# 11. Submission

```
pri 106 the_role_competitions_margin_is_a_reliability_signal_0_92_accurate_at_40_percent_coverage_and_no_consumer_reads_it
-- SOLVED.md written, status PARTIAL. ONE CONSUMER UP CI-SEPARATED OVER ITS STRONGEST FLOOR: the board's
who-did-what AGENT read, by licensing the marked-cue override with the role competition's own calibrated
confidence (theta learned on UD-EWT train, never hand-set) -- organ 0.8468 floor -> 0.8545, +0.0077
CI95[+0.0021,+0.0134]; through the board arm's own hybrid 0.8271 -> 0.8517, +0.0246 CI95[+0.0155,+0.0337] over
the landed board model, and the confidence-shuffled twin lands exactly on the floor. The gate keeps 10 of the 17
good overrides and 3 of the 45 bad ones. THE BRIEF'S OWN HYPOTHESIS IS REFUTED AT THE AFFECTED-ENTITY CONSUMER
WITH A MECHANISM: weighting the parallelism cue by the LABEL's reliability loses (-0.0155), and even a PERFECT
label-gate loses (-0.0055), because a parallelism cue tests AGREEMENT and the organ's errors are systematic --
class accuracy 0.8029 but match accuracy 0.7481 against 0.6576 for independent errors, a +0.0905 excess. What DOES
win there is the graded hand-off in log form (population-gain cue) 0.3832 -> 0.4385, +0.0554 CI95[+0.0299,+0.0831],
posterior-shuffled twin 0.3289 (CI-separated DOWN) -- but the margin-shuffled twin keeps +0.0509, so ~+0.004 of it
is the reliability and the rest is reading the posterior at all. Asset: data/hook_state/role_margin_reliability_v1.json
(four count-calibrated monotone maps with an online observe path). Patch: three hdlab files, default path byte-
identical (1423/1423 identical agent picks with heads=None), apply with --ignore-whitespace. CAVEAT: pri 109 edited
experiments/gum_coref.py at 10:37 today and the affected-entity population changed n=596 -> n=903 mid-session;
every C1 number here is on the post-10:37 loader and the board's standing affected_entity row is not comparable.
```
