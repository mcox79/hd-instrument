---
problem: pos_tagger_is_a_notbf_maxmargin_perceptron_not_a_calibrated_graded_category_posterior
status: SOLVED
bar: "Rebuild the tagger's category decision brain-foundationally (a distributional/calibrated GRADED category posterior, not a supervised max-margin hard commit) and recover the who-was-affected POS third CI-separated over the live perceptron floor on modern gold (info-free twin losing, no downstream regress) -- OR a rigorous LOCATED NEGATIVE naming + quantifying why a standalone tagger cannot recover it (numbers; the brain-faithful stronger version actually tested; residual routed). Grade on MODERN gold (UD-EWT; 19c banned)."
result: "RIGOROUS LOCATED NEGATIVE (the bar's explicitly-sanctioned full pass), extending the owner-DONE `upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior` joint-decode negative from the 19c verb-AUROC axis to the WHO-WAS-AFFECTED UNDERGOER metric. On UD-EWT test (n=1500 sents, 627 affecting undergoers): the POS third (full 0.7895 -> gold-POS ceiling 0.8581, +0.0686) is a HARD-COMMIT loss, NOT a standalone-tagger-quality gap -- on the 42 POS-caused undergoer-miss tokens the GOLD category survives in the tagger TOP-2 ~0.80 (perceptron emission 0.81 / CRF marginal 0.79; top-3 0.93 both) but is discarded at the argmax->Viterbi->parse commit (top-1 0.31 / 0.07). NO standalone / frame-local route recovers it (all measured): distributional lexical-category prior override -0.094; DP-head + marginal nominal correction -0.002; joint POS-parse decode driven by the EXISTING arc scorer -0.005 (net-negative at scale). The miss classes are context-ambiguity (PRON->SCONJ 'that' 7, VERB->AUX 'has/have/do' 7, NOUN->VERB 'show/forum/present' 6), NOT OOV a lexical prior fixes. => the who-affected POS third is a JOINT POS-parse decoding loss BOTTLENECKED BY THE ARC SCORER (the parser cluster); the calibrated CRF marginals (top-2 ~0.80 headroom) are the ready interface. Separately: activating the dormant calibrated CRF as the reader's tagger is GLOBALLY no-regress (UPOS 0.94198 -> 0.94402) but a SLIGHT who-affected regress (-0.010), so it is gated (BF-hygiene + interface, not a harm/help win) -- consistent with the prior DONE work's default-off gating."
floor: "Strongest floor actually run = the CURRENT LIVE perceptron tagger, who-was-affected undergoer recall 0.7895 (UD-EWT test n=1500, affecting verbs, on the item's own population). The gold-POS CEILING (what a perfect tagger would give, same population) = 0.8581 -- so the entire standalone-recoverable POS budget is +0.0686, and NO tested standalone route reaches it (best = joint-decode-existing-parser -0.005). Global-UPOS floor = perceptron 0.94198."
controls: "(1) INFO-BEARING-WRONG-ROUTE control: a distributional lexical-category prior (Harris/Mintz neighbour vote from the shipped PPMI-SVD hub) OVERRIDING rare words HURTS who-affected -0.094 -- isolates that the miss classes are context-ambiguity, not OOV (a lexical prior gives the DOMINANT category, which is exactly the wrong tag for that->SCONJ / has->AUX). (2) FRAME-LOCAL control: a generalized DP-head + CRF-marginal nominal correction is negligible (-0.002; too few clean determiner-framed cases). (3) STRONGER-VERSION control (the 'don't declare impossible' discipline): a JOINT POS-parse decode that lets the EXISTING parser's total tree score pick among the CRF-alive top-2 categories recovers -0.005 (net-negative at scale) -- the arc SCORER is the bottleneck, not the tagger. (4) HARD-COMMIT signature (positive control that the headroom is real): gold survives the tagger TOP-2 ~0.80 in BOTH the perceptron emission (0.81) and the CRF marginal (0.79) but is thrown away at argmax (top-1 0.31 / 0.07) -- the loss is the commit, not the score. (5) NO-REGRESS global-UPOS check for the CRF activation: 0.94198 -> 0.94402 (globally better, +0.002). (6) PRIOR-WORK consistency: the owner-DONE calibrated-CRF problem independently found the joint parse-decode a located negative on the 19c verb-AUROC axis (+0.0017) -- this cluster reproduces the same conclusion on the undergoer metric."
files_changed: "experiments/exp_pos_calibrated_tagger_and_hardcommit_v1.py (the consolidated cell: run_activation / run_hardcommit / run_standalone_routes + self_test), verification/test_pos_calibrated_tagger_and_hardcommit.py (6/6 witness). NO hdlab/ writes (Q111 -- the proposed activation diff is in this doc). Reuses hdlab.crf_tagger.GlassBoxCRF, hdlab.graded_parser (tree_score/CLE), hdlab.pos_tagger, hdlab.causation_typing._frontend, experiments.exp_fd_harm_help_signal_trace/role_corpus_validation/arithmetic, experiments.exp_pos_nominal_head_correction (_is_dp_head)."
reverify: ".venv/Scripts/python.exe verification/test_pos_calibrated_tagger_and_hardcommit.py"
---

# The POS tagger is NOT_BF, but the who-was-affected "POS third" is a HARD-COMMIT loss, not a standalone-tagger gap

**Status: SOLVED as a rigorous LOCATED NEGATIVE (WIP until `owner_verdict: DONE`).** No `hdlab/` file changed
(Q111). Witness `verification/test_pos_calibrated_tagger_and_hardcommit.py` **6/6**.

## FINAL SUMMARY (read this first)

**The plan's Step-A hypothesis was:** a better brain-foundational STANDALONE POS tagger (a distributional
lexical-category posterior, or graded POS marginals instead of hard Viterbi) recovers the ~30 % "POS third" of the
who-was-affected undergoer loss that the harm/help signal-trace measured. **This cluster TESTED that hypothesis
end-to-end and REFUTES it, with the mechanism** — and in doing so confirms + extends the owner-DONE
`upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior` (which found the joint parse-decode a located
negative on a *different* metric, 19c verb-AUROC).

**The three measured facts (UD-EWT test, modern gold; who-was-affected undergoer recall):**

1. **The POS third is a HARD-COMMIT loss, not a tagger-quality gap.** On the 42 tokens whose POS error breaks
   patient-binding, the GOLD category survives in the tagger's **top-2 ~0.80** (perceptron emission 0.81 / CRF
   marginal 0.79; top-3 0.93 both) — but the `argmax → Viterbi → parse` pipeline throws it away (top-1 0.31 / 0.07).
   The headroom is present in BOTH taggers' scores; it is discarded at the hard commit, before the parse can resolve
   the category. This is the brain-foundational signature exactly: the cortex keeps category graded and lets **syntax
   resolve it** (constraint satisfaction); the tag-then-parse pipeline structurally cannot.

2. **The miss classes are CONTEXT-AMBIGUITY, not OOV.** `PRON→SCONJ "that"` (7, relative pronoun vs complementizer —
   needs the relative-clause gap), `VERB→AUX "has/have/do/will"` (7, main vs auxiliary — needs to know a main verb
   follows), `NOUN→VERB "show/forum/present/opening"` (6, conversion — the argument frame disambiguates). The
   disambiguating evidence is the **syntactic structure**, not the word or its distribution.

3. **NO standalone / frame-local route recovers it (all measured vs the 0.7895 floor / 0.8581 gold ceiling):**

   | route | who-affected recall | Δ vs floor | why |
   |---|---|---|---|
   | live perceptron (floor) | 0.7895 | — | — |
   | activate calibrated CRF (Viterbi) | 0.7799 | **−0.010** | globally better (+0.002 UPOS) but a slight who-affected regress |
   | distributional lexical-category prior override | 0.6954 | **−0.094** | gives the DOMINANT category — the wrong tag for that/has |
   | DP-head + marginal nominal correction | 0.7879 | −0.002 | too few clean determiner-framed cases |
   | joint POS-parse decode (EXISTING arc scorer) | 0.7847 | −0.005 | the arc scorer is too weak to exploit the top-2 headroom |
   | **gold POS (ceiling)** | **0.8581** | **+0.069** | only reachable by joint decode with a STRONGER arc scorer |

**=> LOCATED NEGATIVE, well-attributed:** the who-was-affected POS third is a **JOINT POS-parse decoding loss
bottlenecked by the arc SCORER (the parser cluster, Step B)**, NOT a standalone-tagger gap. Standalone Step A is
**exhausted** — the stronger brain-faithful version (joint decode) was actually tested and is scorer-bound, so this
is not a premature "impossible." The calibrated CRF marginals (top-2 ~0.80 headroom, proper probabilities) are the
**ready interface** for the parser cluster's joint decode.

## THE ONE CLEAN POSITIVE (BF hygiene, gated — NOT a who-affected win)
The reader tags with the NOT_BF max-margin perceptron while a calibrated glass-box CRF
(`hdlab/crf_tagger.py`, likelihood-trained, pure-numpy forward-backward marginals — landed by the prior DONE problem)
sits **DORMANT: zero live consumers** (verified — the reader loads the perceptron in `causation_typing._frontend`;
`predicate_detector` still uses the perceptron `verb_margin`, never the CRF `vlogit`). The CRF is **globally more
accurate** (UPOS 0.94198 → 0.94402) and **calibrated** (a graded category posterior — the BF representation, vs the
perceptron's over-sure max-margin). BUT activating it as the tagger is a **slight who-affected regress (−0.010)**, so
per **no-more-default-off / measure-impact-and-turn-on** it must NOT be flipped standalone now — it is gated on the
parser cluster becoming a joint consumer of its marginals (consistent with the prior DONE work, which already left the
CRF default-off pending a live consumer). This is a BF-hygiene + interface action, not a harm/help extraction win, and
is reported as exactly that.

## WHAT WAS BUILT / MEASURED
- `experiments/exp_pos_calibrated_tagger_and_hardcommit_v1.py` — one consolidated cell:
  - `run_activation` — perceptron vs CRF-Viterbi vs CRF-max-marginal on global UPOS + who-was-affected + gold ceiling.
  - `run_hardcommit` — on the POS-caused undergoer-miss tokens, gold-in-top-k for BOTH the perceptron emission and the
    CRF marginal (the hard-commit signature) + the miss-class histogram.
  - `run_standalone_routes` — the distributional-prior override, the DP-head+marginal correction, and the joint
    POS-parse decode (existing arc scorer), each vs the floor + gold ceiling.
  - `self_test` — asserts CRF global no-regress; the hard-commit signature (top-2 ≫ top-1, both taggers); the located
    negative (distributional ≤ 0, joint-decode < gold-ceiling gap).
- Witness `verification/test_pos_calibrated_tagger_and_hardcommit.py` **6/6**.

## PRIOR-WORK CHECK (mandatory; done)
`upgrade_the_pos_tagger_to_a_calibrated_joint_decoded_posterior` is **owner_verdict: DONE**. It built the calibrated
CRF, found the joint parse-decode a located negative on the **19c verb-AUROC** axis (structure adds +0.0017 over the
calibrated posterior), and left the CRF **default-off / gated on a live consumer**. This cluster does **not**
re-discover any of that — it **extends** the joint-decode located-negative to the **who-was-affected undergoer**
metric and the **general tag set**, adds the **top-2 ~0.80 hard-commit headroom** quantification, and measures the
**harm/help-extraction standalone routes** (distributional prior / DP-head) that were not tested there. The two
results are mutually consistent: the calibrated posterior captures the local category signal; structure — as currently
scored — adds little; the lever is a stronger joint decoder (the parser).

## PROPOSED hdlab DIFF (Q111 — strategy lands; GATED)
- **`hdlab/causation_typing._frontend` (+ any reader POS load):** OPTION to source POS from
  `hdlab.crf_tagger.GlassBoxCRF` (argmax `.tag()`) instead of the perceptron, AND expose `.marginals()` as a
  parser-facing graded-category interface. **Do NOT flip standalone** (who-affected −0.010); land it TOGETHER with the
  parser cluster's joint decode that consumes the marginals, then measure the joint who-affected number. Until then,
  the perceptron stays the live tagger (it is marginally better on the who-affected slice).
- **No change to `hdlab/pos_tagger.py`** beyond its standing NOT_BF flag — the fully-BF standalone tagger is not the
  lever here (measured), so rebuilding it in isolation is de-prioritized in favour of the parser joint decode.

## SUBSTRATE INCORPORATION MANIFEST
- **INCORPORATE-AS-DURABLE-NEGATIVE:** the who-was-affected POS third is a HARD-COMMIT / joint-POS-parse loss bottlenecked
  by the arc scorer, NOT a standalone-tagger gap (gold survives tagger top-2 ~0.80, discarded at argmax; every standalone
  route ≤ +0.003 / negative). This RE-DIRECTS the parser cluster (Step B) and de-prioritises a from-scratch BF tagger.
  Witness `test_pos_calibrated_tagger_and_hardcommit.py` (6/6) gates it.
- **INCORPORATE (gated, ready interface):** the dormant calibrated CRF (`crf_tagger.GlassBoxCRF`) as the reader's tagger
  + its marginals as the parser-facing graded-category interface — land WITH the parser joint decode (not standalone;
  who-affected −0.010 alone).
- **DO-NOT-INCORPORATE:** the distributional lexical-category prior override (a control showing the miss classes are
  context-ambiguity, not OOV — it HURTS, −0.094); the standalone CRF swap as a who-affected win (it is a slight regress).

## TLDR (plain language)
The reading system decides each word's part of speech with an older, over-confident method, and I was asked to see
whether replacing it with a more brain-like method would fix a class of mistakes where the system loses track of *who
was affected* in a sentence. I measured carefully and found something more useful than a quick swap: for the exact
words that cause these mistakes (like "that", "has", "show"), the tagger actually still has the correct answer as its
close-second guess about 80 % of the time — it just throws that away when it locks in a single choice *before* it works
out the sentence structure. The brain doesn't do that; it keeps the options open and lets the sentence structure settle
the choice. I tried every way to fix this at the tagging step alone — a more brain-like distributional method, a
grammar-frame rule, and even letting the existing parser re-pick the word type — and none of them recovered the loss
(one made it clearly worse). The reason is that these words can only be resolved by the full sentence structure, and the
part of the system that builds that structure isn't strong enough yet. So the honest result is: this is **not** a
tagging problem to fix here — it's a job for the sentence-structure component, and I've handed it a precise target and
the ready "keep-the-options-open" signal it needs. I also confirmed a better, already-built tagger is sitting unused,
but switching to it would slightly hurt this particular measure, so it should be turned on together with the
sentence-structure fix, not before.

## QUESTIONS
None — the hypothesis was tested end-to-end and refuted with mechanism, the residual is named + quantified + routed to
the parser cluster, and the finding is consistent with prior owner-DONE work. (SOLVED.md is WIP until `owner_verdict:
DONE`.)

## NEXT STEPS
1. **Parser cluster (Step B) — the real lever:** build a stronger arc scorer and a JOINT POS-parse decoder that consumes
   the calibrated CRF marginals (top-2 ~0.80 headroom), targeting the who-was-affected undergoer recall toward the 0.8581
   gold-POS ceiling. Same scoreboard (`exp_fd_harm_help_signal_trace_v1` / `exp_pos_calibrated_tagger_and_hardcommit_v1`).
2. **Land the CRF activation + marginal interface TOGETHER with that joint decode** (not standalone), then re-measure the
   joint who-affected number and the global no-regress across the reader's board.
3. Harm/help stays SOLVED — this cluster does not reopen it.
