---
problem: add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost
status: SOLVED
bar: "PASS = _FastLabelPlan landed into hdlab/arc_labeler.py, built lazily in label() (mirroring PosTagger._ensure_fast); inference uses the fast path, training stays on the reference; labels are BYTE-IDENTICAL to the stock _predict_label on a held-out doc set (not just witness fixtures), with a measured read-time cut reported; the stock scoring body is retained as a self-checkable reference. A rigorous located NEGATIVE ... is a FULL PASS. Strategy lands the Q111 wire."
result: "Byte-identical labels: 0 mismatches / 22,921 HELD-OUT arcs (4,575 LitBank predicted-heads + 18,346 UD-EWT-test gold-heads); full SituationModel byte-identical across ALL dimensions on 3 held-out docs. Labeler scoring 8.73x faster in-read (14.29s->1.64s median-of-9, ~4.2s/read removed on full LitBank docs). Brain-foundational extension (reuses the LANDED graded_competition organ): graded readout argmax byte-identical (0/18,346 = MAP-optimality, zero consumer regression) AND its normalized entropy flags labeling errors gold-free (AUC 0.930; info-free twin 0.481)."
floor: "The landed reference ArcLabeler._predict_label -- byte-identity measured against it, 0 divergence over 22,921 held-out arcs. For the graded-readout exceed: the info-free twin (shuffled cue validities) AUC 0.481 ~ chance is the floor the entropy signal (AUC 0.930) clears."
controls: "(1) W4 info-free shuffled-weights plan MUST diverge from the real plan -- 10/10 probe arcs differ (byte-identity check is non-vacuous). (2) W3 full-model regression guard: fresh-reader single-read stock-vs-fast SituationModel byte-identical across events/entity_states/causal/typed_causal/coref/coref_xsent/timeline (excludes NO consumer). (3) MAP-optimality byte-identity: argmax(lane)==stock over 18,346 UD arcs, so the graded readout is a strict SUPERSET of the discrete one (regresses nothing). (4) Info-free twin for the entropy signal: shuffled cue validities AUC 0.481 (loses)."
files_changed: "ARC-LABELER (assigned): experiments/exp_arc_labeler_graded_competition_v1.py, exp_arc_labeler_fastpath_landing_v1.py, exp_frontend_chain_signal_loss_v1.py, exp_arc_labeler_joint_clause_competition_v1.py, verification/test_arc_labeler_fastpath_landing.py, test_arc_labeler_graded_competition.py, exp_grounding_whiten_fix_v1.py, exp_meaning_channel_whiten_v1.py. PARSER (owner escalation): experiments/exp_arceager_graded_beam_parser_v1.py, exp_arceager_parser_replacement_v1.py, exp_parser_dominance_breakdown_v1.py, exp_parser_confidence_hybrid_v1.py, verification/test_arceager_parser_replacement.py. SELF-SUPERVISED + MEANING + FULL CHAIN (owner escalation): experiments/exp_predictive_selfsup_parser_v1.py, exp_dmv_selfsup_parser_v1.py, exp_selfsup_parser_semantic_bootstrap_v1.py, exp_selfsup_parser_grounded_selpref_v1.py, exp_grounded_meaning_role_v1.py, exp_selfsup_category_induction_v1.py, exp_full_brain_foundational_chain_v1.py, exp_chain_signal_loss_deep_v1.py. notes/problems/add_the_arc_labeler_fast_scoring_path_the_dominant_remaining_read_cost/SOLVED.md. REUSES exp_arc_labeler_fastpath_v1.py + test_arc_labeler_fastpath.py + hdlab/arceager_parser.py + hdlab/graded_competition.py + hdlab/meaning_foundation.py + hdlab/animacy_lexicon.py; NO hdlab/ writes -- proposed diffs below, strategy lands per Q111"
reverify: ".venv/Scripts/python.exe verification/test_arc_labeler_fastpath_landing.py"
---

# Arc labeler fast scoring path -- SOLVED (byte-identical), plus a brain-foundational extension it unlocks for free

## >>> PARSER-WORK FLAG (owner-requested; READ THIS) -- the escalation exceeded the arc-labeler scope
Beyond the assigned arc-labeler fast path (sections A-C, DONE + land-ready), the owner directed a large
brain-foundational investigation of the reader's PARSER and front-end chain. That work is documented in sections
D-O and is EXPLORATORY, not a landable deliverable -- it should be FILED AS ITS OWN PROBLEM(S) for verification +
landing. Headline parser findings (each with its own section):
  * (C-E) The dominant read-time / accuracy leak is the PARSER, not the labeler. The live reader runs the WEAKER
    of two parsers it already has: switching on the dormant arc-eager (UAS 0.79 -> 0.84, already built) is a
    free, byte-safe win, but only feeds entity_states in the general path -- LOW leverage; the who-did-what path
    already uses arc-eager. (exp_arceager_parser_replacement_v1, exp_parser_dominance_breakdown_v1)
  * (G-N) The parsers are SUPERVISED-trained on gold trees, which is NOT how the brain acquires syntax. I built a
    self-supervised, online, prediction-error-driven, never-frozen structure learner (on hdlab.predictive_coding)
    -- it LEARNS as it reads (control-verified) but caps ~0.42 UAS vs supervised 0.87. Located negatives:
    beam/revision; joint-clause; grounding-on-the-skeleton. Honest: the grand goal (brain-foundational parser
    matching supervised) is NOT achieved; the online learning is not yet stable.
  * (M-O) Traced the loss step-by-step vs the brain (research-backed) and aggressively vetted the grounding
    negative -> ROOT CAUSE = collinear meaning vectors (cosine 0.92); FIX = whiten. Two PROTOTYPE wins from that
    fix: (i) grounded meaning now beats its scrambled control on meaning-sensitive arcs (+0.020, a flip); (ii)
    whitening lifts the LIVE WSD meaning channel a_s +0.018-0.058 (n=2676) -- UNVERIFIED (no twin/significance/
    curated-baseline yet; strategy must confirm before landing).
RECOMMENDATION: accept the ARC-LABELER as done; file two follow-on problems -- "whiten the meaning-channel
embedding" (nearest, testable win) and "self-supervised + grounded front-end parser" (the north-star program).

## What the disk confirms (agrees with the brief)
The mechanism the brief names already exists and is correct. `hdlab/arc_labeler.py::ArcLabeler._predict_label`
is a multiclass averaged perceptron that, for EVERY one of 36 labels, sums `w.get(f + "~" + lab)` over the
arc's ~25 features -- ~900 string-concat dict lookups per arc, and it runs default-on via
`bind_entity_states=True` (situation_reader.py:701) -> `M.extract_entity_states(..., self._es_lab, ...)`. The
`FastLabelPlan` in `experiments/exp_arc_labeler_fastpath_v1.py` precomputes `feat -> [(label_idx, weight)]`
(split each key on the LAST `~`), accumulates present weights into a per-label `lane[]` in FEATURE order, and
argmaxes in LABEL order. The existing witness (`verification/test_arc_labeler_fastpath.py`) passes 3/3.

## (A) The assigned bar -- byte-identical speedup, made LAND-READY

**Byte-identity is now a THEOREM, not a lucky sample** (`test_arc_labeler_fastpath_landing.py` W1). The fast
plan's `rsplit("~", 1)` exactly recovers `(feat, label)` iff no label contains `~`. On the landed asset: 0 of
36 labels contain `~`, and all 348,651 weight keys rsplit to a known label (24 keys have `~` inside the FEATURE
part, which is fine -- the split is on the LAST `~`). Given that, plus (b) `lane[k]` accumulates the SAME
weights in the SAME feature order as stock `_score(feats, label_k)` -> the float sum is bit-identical, and (c)
argmax uses the SAME first-max strict-`>` tie-break in the SAME label order, the output is byte-identical for
ANY weights. This is the labeler analog of the parser fast-path lesson: prove identity at the CONSTRUCTION
level, not by sampling scores.

**Held-out byte-identity on two disjoint populations** (W2): 0 mismatches / 4,575 LitBank arcs via the reader's
live frontend (PREDICTED heads -- the realistic path), and 0 mismatches / 18,346 UD-EWT TEST arcs via gold
heads (a second held-out population the labeler never trained on). 22,921 held-out arcs, zero divergence.

**Full-model regression guard** (W3, the "no downstream consumer regresses" proof): a fresh reader doing ONE
read with the fast labeler patched in at the class level (mirroring the proposed lazy build) yields a
byte-identical `SituationModel` across EVERY value-typed dimension -- events (predicate/agent/patient),
entity_states, causal_links, typed_causal_links, coref_acc, coref_xsent_acc, coref_resolutions, timeline_order
-- on all 3 held-out docs. (Method note: I first had a false FAIL from reading the SAME doc twice on one
stateful reader and from `str()`-ing three closure/object fields whose repr embeds a per-run memory address --
fixed by fresh-reader-single-read and comparing only value-typed content.)

**Measured read-time cut** (`exp_arc_labeler_fastpath_landing_v1.py`, OMP=1, 3 full LitBank docs, median of 9):
- **LABELER-IN-READ (robust): stock 14.289s -> fast 1.637s = 8.73x; ~4.217s/read removed.** This matches the
  prior micro-speedup (9.81x) with the in-read timing wrapper's per-call overhead folded in.
- WHOLE-READ (CI-separated on these docs): stock 26.56s [24.46-28.29] -> fast 13.28s [12.49-14.91], ~4.43s/read
  -- i.e. the labeler is ~54% of a full-length-doc read, so the fast path roughly HALVES total read time here.
  This magnitude is doc-length-dependent (the prior solver's 6-doc mixed median was 0.87s / 13.9%); the
  doc-independent robust claim is the 8.7-9.8x labeler speedup, byte-identical.

**Info-free control** (W4): a weights-shuffled plan diverges from the real plan (10/10 probe arcs) -- the
identity check has teeth.

## (B) Brain-foundational -- the SAME refactor unlocks a graded, brain-faithful readout, at zero cost

The owner's directive: every component, mine and upstream, must be brain-foundational. So I asked what the
labeler COMPUTES, not just how fast it runs. A parallel research drill (below) answered it, and it re-frames
the fast path as more than a speedup.

**The operation is already brain-faithful; the readout is not.** `lane[k] = sum over the arc's features of
weight(feature, label_k)` is EXACTLY `net_activation` in the LANDED `hdlab/graded_competition.py`: additive cue
integration `A_i = sum_c w_c * support_c(i)` (Lewis-Vasishth), the pinned Competition-Model / FLMP operation
(MacWhinney, Bates & Kliegl 1984; McClelland 2013: softmax over additive net IS the Bayesian posterior). The
perceptron feature-weights ARE learned cue validities. **What is NOT brain-faithful is the HARD ARGMAX**: the
brain maintains the graded distribution and collapses to a single winner only when a task presses (Hale 2001 /
Levy 2008 distribution-over-parses; Kiani & Shadlen 2009 graded posterior + Usher-McClelland 2001 threshold;
the loser's activation persists and affects later processing, Christianson 2001). The stock `_predict_label`
computes `lane[]` implicitly and THROWS AWAY everything but the max.

**The fast-path refactor MATERIALIZES `lane[]`.** So the byte-identical speedup is ALSO the enabling substrate
for the brain-faithful graded readout -- the same move. And it lets the LABELER feed the SAME gold-free
difficulty currency (normalized entropy) that the landed `discrete_where_the_brain_is_graded` organ already
wires for the parser/role pools. I did NOT build a new organ; I REUSE `graded_competition.softmax`.

Measured on held-out UD-EWT test (`exp_arc_labeler_graded_competition_v1.py`, gold heads+UPOS isolate the
labeler; label accuracy 0.941):
- **argmax(lane) == stock `_predict_label`: 0 mismatches / 18,346 arcs.** By MAP-optimality (normalization is
  rank-inert) the graded readout is a strict SUPERSET of the discrete one -- wiring it regresses NO consumer.
- **The normalized entropy flags labeling ERRORS gold-free:** entropy(wrong) - entropy(right) = +0.0209,
  95% CI [+0.0180, +0.0237] (CI-separated); **AUC(entropy -> error) = 0.930**; the parameter-free
  top1-top2 margin gives AUC 0.934. **Info-free twin (shuffled cue validities): AUC 0.481 -- LOSES.**

This is the "excel and exceed", stated honestly: **+9.8x speed, +fidelity (graded posterior vs hard argmax --
the brain's readout), + a calibrated gold-free uncertainty signal (AUC 0.93) the argmax structurally cannot
express -- with ZERO change to any output.** It is NOT a label-accuracy jump: by MAP-optimality the graded
distribution cannot beat its own argmax on gold accuracy (its value is the DISTRIBUTION/uncertainty). This is
the same finding the parser/role graded organ reached (there AUC 0.646); the labeler's confidence is far
sharper (AUC 0.93) because its per-arc decision, given correct structure, is usually unambiguous.

## (C) Upstream + downstream (the owner's chain question)

**The front-end scoring chain is ONE brain operation implemented three times:** POS-tagger emission (sum
feature-weights per tag -> Viterbi), arc-parser arc score (sum feature-weights per head-dependent pair ->
argmax head), arc-labeler label score (sum feature-weights per label -> argmax). All three are linear cue
integration -> competition, and all three now have byte-identical fast paths (tagger `_FastEmissionPlan` and
parser `FeatCache`/CRC IDs are already LANDED; the labeler is this problem). Each fast path materializes its
per-candidate activation, so `graded_competition` composes with all three.

**No downstream consumer regresses from the upstream optimization.** W3 runs the reader THROUGH the live fast
tagger + fast parser + (patched) fast labeler and gets a byte-identical SituationModel across all dimensions.
The labeler's only live consumer is `M.extract_entity_states` (copular is-a/attribute binding, via
`bind_entity_states`, default-on) plus `hdlab/copular_binding.py` and `hdlab/predicate_argument_frontend.py`;
all read only the argmax label, which is byte-identical. The tagger/parser fast paths were witnessed
byte-identical at their own integrations; the chain is transparent.

**Should the consumers be revisited to consume the newly-materialized graded signal? Yes -- mapped, not built
(they belong to solvers already on them; see ADJACENT).** The entity_states/copular binder and the who-did-what
role readout currently gate on a hard 1-best label; where the labeler's entropy is high (genuine competition),
a graded consumer could defer or let discourse evidence re-rank -- exactly the pattern
`consume_the_graded_pos_posterior_uncertainty_aware...` is landing for the POS tagger, now available from the
labeler too.

## (D) EXACT signal-loss accounting over the ENTIRE chain (owner's question, MEASURED)
`exp_frontend_chain_signal_loss_v1.py`, held-out UD-EWT test (2,061 sents, 24,120 tokens), ORACLE-SUBSTITUTION
ladder (feed each stage gold vs predicted inputs -> each stage's loss is isolated and attributed):

| stage | measured | signal lost | attributed to |
|---|---|---|---|
| Tagger  | POS accuracy 0.9443 | -5.6% of tags | itself |
| Parser  | UAS 0.7907 (gold POS) -> 0.7608 (pred POS) | -20.9% of heads in isolation; tagger propagation -3.0 UAS | PARSER dominant; tagger secondary |
| Labeler | A gold-struct 0.9422 -> C(pred POS) 0.9082 -> B(pred heads) 0.8439 -> D live 0.8210 | intrinsic -5.8%; tagger->features -3.4; PARSER->labeler -9.8 | parser head-errors are 3x the tagger's cost to labeling |
| End-to-end | LAS (head AND label correct) 0.7175 | -- | compounded |

**Who-did-what signal specifically:** core-role (nsubj/obj/iobj/nsubj:pass/obl:agent) accuracy is 0.9293 in
isolation but 0.8166 live; the catastrophic losses are the PASSIVE role markers -- **obl:agent LAS 0.0588,
nsubj:pass 0.402** -- because the parser fails to attach the passive "by"-agent, so the labeler never sees the
arc. This IS the non-canonical / who-did-what wall the front-end problems target. Downstream of LAS the
who-did-what TASK sits lower still (audit: 0.48 flat -> 0.74 with a brain-faithful front-end) due to
consumer-side losses (referent linking / coref / NP-head chunking -- other problems).

**The decisive, honest finding:** the LABELER (this problem's component) is the STRONGEST link -- 5.8% intrinsic
loss, the most brain-faithful of the three at the operation level. **The dominant leak is UPSTREAM: the parser**
(loses ~21% of heads even with gold tags; its head-errors cost the labeler 3x what the tagger does). The
owner's premise -- every component AND upstream must be brain-foundational -- is now QUANTIFIED: the biggest
brain-fidelity payoff is the PARSER, not the labeler.

### Per-stage brain-diff (EXACTLY where each stage departs from the brain)
| stage | our operation | brain's operation (PINNED) | the specific deviation | measured cost |
|---|---|---|---|---|
| Tagger  | emission = sum feature-weights per tag; Viterbi (global DP); hard 1-best | incremental + graded lexical-category belief, top-down re-ranked (cohort; McClelland-Kawamoto) | batch global decode + hard 1-best (PROPN<->NOUN, 28% of tag errors, propagates) | 5.6% tags; -3.0 parser UAS; -3.4 labeler |
| Parser  | O(n^2) all-pairs arc scores; greedy argmax head + cycle-break; batch | incremental structure-building with graded parallel constraint satisfaction + working-memory retrieval (Lewis-Vasishth 2005; Hale/Levy) | non-incremental + hard argmax + NO structural competition | UAS 0.79 -> the DOMINANT leak; -9.8 to labeler |
| Labeler | sum feature-weights per label; per-arc HARD ARGMAX; arcs INDEPENDENT | additive cue integration (Competition Model / FLMP) -> graded normalized competition; whole-clause settling with one-role-per-clause competition (McClelland-Kawamoto 1986; Theta-Criterion; LFG Uniqueness) | (1) hard argmax readout [CLOSED here: graded readout, AUC 0.93, byte-safe]; (2) per-arc INDEPENDENCE [OPEN: no joint decode] | intrinsic 5.8% (strongest link) |

Gap (1) is closed at the labeler (the graded readout, section B). Gap (2) -- per-arc independence and
non-incrementality -- is UNCLOSED and is the deeper structural gap; combined with the parser's dominance it is
where the chain's remaining signal is lost. It is owned by the in-flight incremental-parser / who-did-what /
joint-decode problems (Q113); the concrete brain-faithful target is shared-head joint decoding (CRF / bipartite
matching over each predicate's arcs) with one-role-per-clause competition.

## (F) IS THE ARC-EAGER PARSER IDEAL? Is it better than the batch parser in EVERY way? -- NO to both (MEASURED)
`exp_parser_dominance_breakdown_v1.py`, held-out UD-EWT test (2,061 sents, 24,120 arcs, live pred-POS).

**Not ideal.** Overall UAS 0.8053 (live) / 0.842 (gold POS) -- it still gets ~1 head in 5 wrong (gap to the 1.0
ceiling = 0.195), well below neural-parser SOTA (~0.92 on UD-EWT). It is greedy with NO revision (beam+revision
is a located negative on this greedy-trained model, section E). So "ideal" it is not; it is the best AVAILABLE
and more brain-foundational than the batch parser (incremental + working-memory buffer).

**NOT strictly better than the batch parser.** It wins massively where it matters most -- long-range attachment
(distance 6-10: +0.15, 11+: +0.18) and left-headed arcs (+0.076), which drives the +0.045 overall -- but it
LOSES on four relations:
| relation | batch | arc-eager | delta | note |
|---|---|---|---|---|
| obl:agent | 0.824 | 0.676 | -0.147 | the PASSIVE "by"-agent -- the who-did-what-critical relation (n=34) |
| appos | 0.507 | 0.472 | -0.035 | apposition |
| det | 0.942 | 0.923 | -0.019 | determiners -- VERY frequent (n=1785) |
| amod | 0.838 | 0.836 | -0.002 | negligible |

So a wholesale kill-and-replace trades a passive-agent + determiner REGRESSION for a large long-range gain.

**Headroom of combining (oracle-union): 0.854** (+0.049 over arc-eager). The two parsers' errors are
COMPLEMENTARY (arc-eager uniquely right on 9.3% of arcs, batch uniquely right on 4.9%; agreement 80.8%). So a
confidence-gated hybrid (run both routes, arbitrate by reliability -- itself the Competition Model applied to
PARSING routes) is a real path, but its CEILING (0.854) is still not ideal.

**What an actually-ideal parser needs -- and the critical caveat.** Reaching ~0.92 needs a model trained with a
global/graded objective (dynamic-oracle + beam/globally-normalized training, i.e. train FOR revision), which is
a real BUILD, not a reuse. BUT: the `improve_the_parser_verb_argument_attachment` problem recorded that a
modern-trained parser LOSES out-of-distribution on 19c literature (the reader's actual corpus). So "ideal for
this reader" is NOT "max UAS on UD-EWT" -- it is REGISTER-GENERAL. The glass-box perceptron arc-eager is more
register-robust than a neural SOTA parser would be. The honest ideal target: a register-general parser trained
with a graded/revision objective, evaluated on BOTH UD-EWT and 19c, that also fixes arc-eager's obl:agent/det
pockets -- none of which is achieved by reusing what is on disk today.

**Bottom line for the owner's question:** arc-eager is the better DEFAULT and a genuine brain-foundational
improvement, but it is neither ideal nor strictly dominant. A confidence-gated hybrid reaches 0.854; true ideal
needs a register-general graded-with-revision retrain (with the 19c-OOD guard), which is out of a reuse-only,
byte-safe scope and should be its own build problem.

## (G) THE TRULY BRAIN-FOUNDATIONAL PARSER: why it is TRAINED, and a self-supervised implementation (owner escalation)
Owner challenge: "why is it trained? does the brain use a trained parser?" Both live parsers (batch + arc-eager)
are SUPERVISED-trained on gold UD trees. The brain does NOT learn syntax from gold trees (there are none in a
child's input); it learns SELF-SUPERVISED from PREDICTION (research drill, notes/research_self_supervised_
predictive_parser_2026-09-02.md: Saffran/Aslin/Newport 1996; Tomasello 2003; Rao-Ballard 1999; Hale/Levy; and
Fedorenko 2020 / Schrimpf 2021 -- no separate "parser" module, structure is emergent from a predictive model
integrated with meaning).

TASK 1 -- confidence-gated HYBRID of the two parsers = LOCATED NEGATIVE (exp_parser_confidence_hybrid_v1).
No confidence rule beats arc-eager (best hybrid 0.8053 = arc-eager; z-conf 0.796 HURTS; reliability-calibrated
0.8046 ties). The per-attachment confidences are not reliably complementary. AND the framing was wrong: an
ensemble of two separately-trained parsers arbitrated post-hoc is NOT the Competition Model (which integrates
CUES within ONE process) -- it is an engineering combiner. Oracle-union ceiling 0.854 exists but is unreachable
by confidence -> the answer is one better model (task 2), not a combiner.

TASK 2 -- self-supervised predictive parser, IMPLEMENTED (exp_predictive_selfsup_parser_v1 + exp_dmv_selfsup_
parser_v1). A naive predictive-PMI "attach to your best predictor" inducer FAILS (0.22-0.28, BELOW the adjacency
floor 0.30) -- because self-supervised prediction ALONE converges on a linear-order shortcut (Yedetore 2023).
The research's prescription (generative model + UNIVERSAL STRUCTURAL PRIOR + EM + graded inference) built as a
glass-box DMV (Klein-Manning 2004) + universal head->dep POS prior (Naseem 2010) + hard-EM + projective Eisner
INDUCES REAL STRUCTURE with NO gold trees: UAS 0.385-0.398 vs adjacency floor ~0.30 (+0.08-0.09), Eisner
self-test passes, and the ablation proves BOTH ingredients load-bearing (no-prior EM-only 0.35-0.37; prior-only
no-EM 0.32-0.35). HONEST: my reduced DMV plateaus ~0.38-0.40 (no valence/stop model, POS-only, no lexicalization);
a fully-tuned self-supervised DMV reaches ~0.55-0.65 (Spitkovsky; Naseem); BOTH are far below the supervised 0.84.

WHAT THIS ESTABLISHES.
  * The brain-faithful ACQUISITION signal (self-supervised prediction + universal structural bias) is REAL and
    buildable glass-box, and induces genuine dependency structure with zero gold trees.
  * It trades accuracy (~0.38-0.65 vs 0.84). Supervised-on-gold-trees is a SHORTCUT that wins on limited data by
    injecting structure the learner cannot yet discover. Its cost is register-OOD (a modern-trained parser loses
    on 19c -- measured by improve_the_parser); the self-supervised learner needs NO gold trees so it trains on
    19c+modern directly, sidestepping OOD.
  * PINNED (research): self-supervised prediction ALONE is a FLOOR, not a ceiling. The brain's ceiling comes from
    SEMANTIC/GROUNDED bootstrapping (Pinker/Gleitman) and there is NO separate parser module -- structure is
    emergent from a predictive generative model INTEGRATED WITH MEANING. So the truly ideal parser is inseparable
    from the situation/meaning model -- the project's grounding thesis. A parser optimized in isolation cannot be
    ideal.
  * UPSTREAM (owner "upstream as well if needed"): the POS tagger is ALSO gold-trained; the DMV leans on gold
    POS. A FULLY self-supervised chain induces categories too (distributional clustering, Saffran 1996; frequent
    frames, Mintz 2003) -- the next upstream step, flagged not closed.

RECOMMENDATION (philosophy fork -- owner's call): (a) ship the supervised arc-eager as a best-performing offline
FOUNDATION asset (admissible; keep the runtime inference brain-faithful/graded) as the interim; (b) pursue the
self-supervised + MEANING-bootstrapped predictive parser as the north-star research program that closes the gap
the brain's way and is register-general. I lean (b) north-star / (a) interim. This whole parser arc merits its
own problem folder; it exceeded the arc-labeler scope on owner instruction and is recorded here for handoff.

## (H) THE 100% BRAIN-FOUNDATIONAL CHAIN: exactly what is incorrect, signal loss traced, and the correction
Owner: "do the right thing; implement the 100% brain-foundational chain; identify exactly what is incorrect;
trace signal loss every step; get it correct." Uses the live substrate's new curated knowledge foundation
(hdlab.meaning_foundation, 117,614 WordNet-synset meaning signatures).

### SIGNAL LOSS, every step (measured)
| step | our impl | brain-faithful? | measured |
|---|---|---|---|
| categories (POS) | supervised UPOS Viterbi | NO (brain: self-sup distributional clustering) | 0.944 acc; 5.6% loss |
| structure (heads) | supervised gold-tree parser | NO (brain: self-sup predictive + graded) | UAS 0.79 -- DOMINANT leak; obl:agent collapses |
| relations (labels) | supervised perceptron, hard argmax | PARTLY (graded readout closed here) | 0.94 given gold structure; LAS 0.72 live |
| roles/meaning | rule + competition | the real locus of MEANING (below) | who-did-what gated by structure (0.48->0.74) |

### EXACTLY WHAT IS INCORRECT (three findings, each controlled)
1. **The whole chain is SUPERVISED** (gold trees + gold tags). The brain learns syntax SELF-SUPERVISED from
   prediction (no gold trees exist in the input). FIX validated: DMV + universal structural prior + hard-EM +
   Eisner INDUCES real structure with NO gold trees (UAS 0.38-0.45 vs adjacency 0.30; prior +0.03 and EM +0.05
   both load-bearing by ablation). Honest trade: ~0.4 (my reduced DMV) / ~0.6 (tuned literature) vs 0.84
   supervised -- the price of gold-tree-free + register-generality.
2. **MEANING does NOT build the attachment SKELETON.** THREE controlled located negatives: lexical-PMI selpref
   (0.25, HURTS), animacy directional bonus (+0.02 = its scrambled control), grounded distributional selpref
   from the curated foundation (+0.063 UAS but the scrambled-meaning + shuffled-prototype controls lift +0.057-
   +0.061 -- grounded meaning adds only +0.002 over its controls). The "lift" was a verb->nominal STRUCTURAL
   bias, not meaning. The skeleton is a distributional/syntactic problem; I mis-targeted meaning at it.
3. **MEANING is a SUBORDINATE cue on AGGREGATE English, but CARRIES ROLE exactly where structure fails.** On all
   UD-EWT test transitive clauses, POSITION predicts the agent at 0.961 (English SVO word-order cue validity is
   ~96%; animacy 0.950 real vs 0.886 scrambled = real-but-subordinate; grounded 0.778). BUT on NON-CANONICAL
   (passive) clauses, where position MISLEADS: positional 0.00, animacy 0.07, **grounded meaning 0.43**. So
   meaning's brain-foundational locus is ROLE assignment WHERE SYNTACTIC CUES ARE ABSENT/MISLEADING (Competition
   Model: when the word-order cue is invalid, the semantic cue decides), NOT the skeleton and NOT the aggregate.

### THE CORRECTION (the 100% brain-foundational architecture, blueprint + validated pieces)
Separate the two jobs the brain separates: (i) the STRUCTURE skeleton is induced SELF-SUPERVISED from prediction/
distribution (DMV+prior+EM validated; the graded-competition engine does incremental inference); (ii) grounded
MEANING (curated foundation) is a CUE in the SAME graded competition that decides ROLE when the structural cue
is weak/misleading (non-canonical, passives, ambiguous attachment) -- validated: grounded meaning 0.43 vs
positional 0.00 where syntax fails. Upstream: the POS tagger is also gold-trained; a fully self-supervised chain
induces categories too (distributional clustering; Saffran 1996 / Mintz 2003) -- flagged, next.

### KEY CAVEAT (fair test): the reader's REAL corpus is 19c literature, which has MANY MORE non-canonical
constructions than modern rigid-SVO UD-EWT. Word-order cue validity is LOWER on 19c prose, so meaning's role
contribution (measured 0.43-vs-0.00 on the rare UD-EWT passives) is LARGER on the actual reading corpus than
these UD numbers show. This aligns with the substrate's own findings (animacy correct-but-subordinate; the
who-did-what residual is structural NP/case; WSD wall is contextual-rep not grounding) -- and with the audit's
"front-end is the binding constraint." The dominant lever is the self-supervised STRUCTURE learner; meaning is
the subordinate role-decider for the non-canonical tail (which 19c has in abundance).

### HONEST STATE. I identified exactly what is incorrect (supervised acquisition; meaning mis-targeted at
skeleton/aggregate), traced the loss (structure/parser is the leak; meaning's locus is non-canonical role), and
got the ARCHITECTURE correct with controlled evidence for each piece. I did NOT build the full end-to-end
integrated self-supervised+grounded chain (a multi-week research program). Each component's brain-faithful
mechanism is prototyped + measured; the integration is the specified program.

## (I) FULLY BRAIN-FOUNDATIONAL PROTOTYPES FOR EVERY STAGE + END-TO-END (owner: "for all")
A self-supervised, glass-box (no LLM, no gold tags/trees) replacement or modification prototyped for EACH stage,
assembled and measured end-to-end (exp_selfsup_category_induction_v1 + exp_full_brain_foundational_chain_v1):

| stage | brain-foundational prototype | mechanism (PINNED) | measured |
|---|---|---|---|
| CATEGORIES | self-sup distributional clustering (PPMI ctx -> SVD -> k-means) | Harris 1954 / Saffran 1996 / Mintz 2003 | many-to-one 0.547 vs 0.427 random (reduced; lit ~0.70) |
| STRUCTURE | self-sup DMV + universal prior + hard-EM + Eisner | Klein-Manning 2004 / Naseem 2010; prediction=Levy/Hale | 0.38-0.45 standalone (gold cats); prior+EM ablation-confirmed |
| RELATIONS | graded competition readout (softmax over lane) | McClelland 2013 FLMP posterior | argmax byte-identical; entropy->error AUC 0.93 |
| ROLE | Competition Model: position + GROUNDED meaning cue | MacWhinney; Pinker/Gleitman semantic bootstrapping | grounded 0.43 vs positional 0.00 on non-canonical |

END-TO-END (UD-EWT test, maxlen<=12): supervised REF (gold POS -> arc-eager) 0.874; self-sup STRUCTURE on gold
cats 0.295 (cost of self-sup structure ~0.58 in this harness / ~0.43 with the standalone DMV's fuller prior);
+ self-sup CATEGORIES 0.203 (cost of self-sup categories ~0.09); FULLY self-supervised (no gold anywhere) 0.178.

HONEST VERDICT. Every stage now has a working brain-foundational prototype and they compose end-to-end -- but
the fully self-supervised chain reaches ~0.18-0.29 UAS vs the supervised 0.874: a LARGE compounding trade,
dominated by the self-supervised STRUCTURE learner (self-sup categories add only ~0.09 more). This is the honest
state of from-scratch self-supervised parsing on a limited offline corpus. The brain closes this gap with
massive GROUNDED MULTIMODAL experience over years (which we cannot replicate offline), NOT with a different
learning signal -- so the MECHANISMS are brain-faithful (validated) while the DATA/GROUNDING scale is the gap.
Meaning's role contribution (the one place grounding clearly helps) is concentrated in the non-canonical tail,
which the reader's REAL 19c corpus has far more of than modern UD-EWT (the fair-test caveat, still open).

IMPLICATION (do the right thing): the supervised parser is best treated as an offline FOUNDATION asset (proven
0.84, admissible) with brain-faithful RUNTIME (graded/incremental); the self-supervised chain is the north-star
research program whose bottleneck is GROUNDED EXPERIENCE scale, not the mechanism. The single highest-leverage
brain-foundational build remains the STRUCTURE learner (the dominant leak and the dominant self-sup cost),
grounded by meaning for the non-canonical tail, evaluated on 19c text.

## (J) DEEP EVALUATION vs the brain + best alternative; WHERE signal is lost; brain-fidelity of the top rungs
`exp_chain_signal_loss_deep_v1.py` (UD-EWT test, maxlen<=12, n=1304). LADDER (UAS): brain/human-IAA ~0.955
(cited); neural biaffine SOTA ~0.957 (Dozat-Manning 2017, cited); OUR supervised arc-eager 0.874; OUR self-sup
DMV 0.409. Gaps: brain->SOTA ~0.00 (SOTA has MATCHED human accuracy -- by a non-brain route: gold-tree
supervision + transformer); SOTA->ours -0.083 (representation gap); supervised->self-sup -0.465 (grounding/impl).

WHERE the self-sup chain loses (by relation, arcs_lost): punct 660, nsubj 335, case 292, aux 228 (dmv 0.013!),
root 227, obj 203, compound 191 (0.044), cop 191 (0.000!), nmod 191, obl 185. By distance: 3-5 loses 1242 (the
mid-range core-arg band), 2 loses 1036, 1 loses 864. The loss is CONCENTRATED and STRUCTURAL, not uniform.

DEEP brain-fidelity of the highest-loss rungs:
  RUNG 1 supervised->self-sup (-0.465, biggest). NOT a mechanism-fidelity flaw -- the brain IS self-supervised at
  0.955. Decomposes into: (a) REDUCED IMPLEMENTATION -- the near-total aux(0.01)/cop(0.00)/compound(0.04)
  collapse is exactly what the full DMV's VALENCE/stop model + lexicalization handle, which my prototype omits
  (fixable in-mechanism); (b) GROUNDING -- nsubj(0.32)/obj(0.27) core-arg discrimination needs meaning+agreement
  (role probe: grounded 0.43 vs positional 0.00 on non-canonical); (c) grounded-experience SCALE. Verdict: the
  self-supervised MECHANISM is brain-faithful; we are reduced + starved, not un-brain-like.
  RUNG 2 SOTA->ours supervised (-0.083). A GENUINE brain-fidelity gap: our parser uses SPARSE HASHED SYMBOLIC
  features; the brain (and SOTA) use DISTRIBUTED CONTEXTUAL representations. The brain-faithful fix = feed the
  parser the substrate's OWN distributed meaning vectors (meaning_foundation / distributional_meaning_channel,
  present but unused by the parser) -- glass-box, NO LLM. The most tractable clearly-brain-foundational upgrade.
  RUNG 3 the LIVE WIRING. The reader runs the weaker BATCH parser (0.79), not the dormant arc-eager (0.87) whose
  incremental working-memory decode recovers long-range (+0.15) -- a fidelity+wiring loss; and obl:agent needs
  meaning the role stage does not supply.

RANKED brain-foundational fixes (measured loss x fidelity): (1) DISTRIBUTED REPRESENTATIONS into the parser (the
one clear fidelity gap, -0.083, tractable, glass-box); (2) COMPLETE THE DMV MECHANISM (valence + lexicalization
-- fixes the aux/cop/compound collapse); (3) WIRE GROUNDED MEANING into role competition (validated non-
canonical); (4) FLIP the dormant arc-eager live (+0.05 free) + graded/incremental runtime. All on 19c text.

## (K) THE BRAIN-FOUNDATIONAL STRUCTURE LEARNER, BUILT: online, prediction-error-driven, never frozen
`exp_online_predictive_structure_learner_v1.py`, built ON hdlab.predictive_coding (the substrate's own
Friston/Rao-Ballard organ). This is "how the brain does it, exactly": NOT a trained-then-frozen model, but a
system that reads left-to-right, predicts, and updates itself from its own prediction error, continuously,
consolidating -- no answer key, no batch training, never frozen.

MECHANISM (each piece reuses / copies the brain's): distributed bipolar code per word-type; an associative
memory W (predictive_coding) predicts a head's dependents; read incrementally; attach by GLOBAL settling to a
coherent parse (graded competition); then a PREDICTION-ERROR-GATED Hebbian write (predictive_coding.
proportional_gate + gated_write: W += surprise * outer(dep, head)) -- big surprise, big update; consolidate
fast->slow (EMA, the cortical trace). Seeded with an INNATE universal structural bias (Naseem 2010).

RESULT -- it LEARNS AS IT READS (UD-EWT test, no gold trees, never frozen):
  innate bias, 0 read (settle) 0.3902  ->  0.4433 (peak, 500 sents)  ->  0.4270 (final)  = +0.037-0.053 learned.
  CONTROL no-learning (W frozen at the innate bias): 0.3902 (flat -- confirms the rise is real learning).
  CONTROL no innate bias, then learned: 0.2747 (the innate structural bias is LOAD-BEARING -- like the brain's).
It matches the batch self-supervised DMV (0.38-0.45) but done the brain's way (online, never frozen).

KEY REALIZATION (the fix that made it work): my first update rule learned from its OWN GREEDY guesses and
REINFORCED ITS OWN MISTAKES -- accuracy DROPPED below the innate bias (0.368 -> 0.262). The brain-foundational
fix: SETTLE on a coherent whole-sentence parse BEFORE learning from it (an online version of a careful
expectation step), which flipped learning from degrading to improving. Self-training on a weak greedy decode
amplifies error; settling first does not.

HONEST LIMITS: absolute accuracy ~0.44 is far below the supervised parser (0.84) -- it is category-level, learns
from limited text, and lacks the grounding + experience-scale the brain has (the measured gap in J). And there
is mild drift after the early peak (0.4433 -> 0.4270) -- the online writes slowly over-consolidate; a lower
learning rate / stronger slow-store stabilization (the brain's consolidation) is the next lever. But the
brain-foundational MECHANISM is now BUILT and VALIDATED: it learns structure by predicting text, online, never
frozen, reusing the substrate's predictive-coding organ.

## (L) ROBUST IN-PLACE EVALUATION of the online learner in the LIVE reader (exp_online_learner_inplace_eval_v1)
1. UAS on held-out UD-EWT: live-batch 0.822 | arc-eager 0.869 | ONLINE-LEARNER 0.423. It is ~HALF the accuracy
   of the live parsers -- too weak to deploy.
2. IN-PLACE (live SituationReader, 3 real 19c LitBank docs; swap the general front-end parser to the online
   learner): coref_acc UNCHANGED (0.579/0.835/0.025), events UNCHANGED (245/337/331), causal UNCHANGED -- because
   those run off the ROLE-path (arc-eager, default-on) or don't read these heads. ONLY entity_states regressed
   (44->27, 52->37, 34->19, ~-40% of copular bindings). So the general front-end parser's blast radius is SMALL
   (it feeds ~only entity_states); the HIGH-leverage parser is the role-path arc-eager, already the better one.
3. ADAPTATION: after reading 80 19c sentences online, modern UAS 0.4226 -> 0.4216 (-0.001) = STABLE, no
   catastrophic forgetting (consolidation works -- the stability half of stability/plasticity). The PLASTICITY
   half (does it improve ON 19c) is UNMEASURED here: no 19c gold trees exist, and only 80 sentences were read.

RECOMMENDATION + downstream implications (honest): the online learner REPLACES NOTHING today -- at 0.42 UAS it
would regress entity_states ~40% and anything else on its heads. When strengthened to >=0.82 it would replace
the general FRONT-END parser (the batch parser feeding the labeler/entity_states) -- but that is LOW-leverage
(only entity_states depends on it). The high-leverage parser (events/who-did-what) is the role-path arc-eager,
already at 0.87. So: (a) do NOT swap the online learner in now; (b) its unique value is adaptation + never-frozen
+ no-answer-key + STABLE (measured); (c) the strengthening path is grounding + steadier consolidation + richer
features toward 0.82; (d) MEANWHILE the free, safe win is flipping the dormant arc-eager (0.87) to also serve the
general front-end (fixes the batch parser's 0.82 for entity_states, byte-safe, already built). The online learner
is the north-star acquisition mechanism (proven to learn, stable); it is not yet a drop-in.

## (M) MINUTE STEP-BY-STEP: where our online learner loses signal vs the brain (measured + research-grounded)
Measured decomposition (exp_accuracy_loss_ladder_v1, SAME Eisner decode, only the knowledge source changes):
self-sup POS-only 0.41 -> SUPERVISED POS-only 0.60 (+0.20 = NO ANSWER KEY) -> rich lexical supervised 0.87
(+0.27 = words + valence + features) -> brain/SOTA 0.95 (+0.08 = distributed representation). Now WHERE each
gap comes from, per pipeline step, vs the brain's actual mechanism:

STEP 1 -- WORD REPRESENTATION. Ours: word -> POS tag -> random code (keep ~18 category labels, discard which
word). Brain: distributed learned meaning+form code, and VERB-SPECIFIC argument structure stored per word
(Tomasello verb-islands; MacDonald lexicalist) [PINNED]. LOST: all lexical + argument-structure signal -- most
of the +0.27 model/lexical gap; the brain reads structure off verb-specific expectations POS cannot see.
QUANTIFIED (research): PP-attachment structure-only baseline 59% -> +lexical/valence 82-84% -> human lexical
ceiling 88% (Collins&Brooks 1995; Ratnaparkhi 1994) = ~22-25 points from valence/selectional info. REFINEMENT
(shapes the fix): it is the CLASS/subcategorization level that matters, NOT word-pair memorization -- Klein&
Manning 2003 (unlexicalized+subcat 86.4% ~= lexicalized SOTA), Gildea 2001 (bilexical worth only ~0.5F), Resnik
1996, Zapirain 2013 (+17% error reduction). THIS is why our raw word-pair PMI HURT and why the lever is
CLASS-based selectional preference (generalizable) -- exactly what GROUNDED MEANING supplies. Non-local: cue-based
retrieval + interference (Lewis-Vasishth 2005; Linzen 2016 agreement error 7->33->70% at 0->1->4 attractors) --
our first-order-ish associative W lacks it.

STEP 2 -- THE CUE. Ours: ONE cue (category->category association). Brain: ~6 cues in a graded competition --
word order, verb argument structure, selectional fit (meaning), animacy, agreement, prosody (Competition Model,
MacWhinney; syntactic bootstrapping, Gleitman/Fisher) [PINNED]. LOST: five of six cues, strongest = meaning +
valence.

STEP 3 -- THE SUPERVISION SIGNAL (the biggest). Ours: learn from our OWN best-guess parse (self-training) nudged
by prediction error -- NO external check, so it can only reinforce its own guesses (it plateaus; pre-settle-fix
it amplified error). Brain: PROPOSE-BUT-VERIFY (Trueswell/Medina/Gleitman 2013) -- propose one parse, VERIFY
against MEANING/the situation (win-stay/lose-shift); error = grounded coherence, neurally a prediction-error/P600
(Fitz & Chang 2019) [PINNED]. LOST: THE ANSWER KEY ITSELF. The brain's answer key IS meaning/the world (semantic
bootstrapping, Pinker 1984); we removed the answer key and put NOTHING (no grounding) in its place -> the +0.20
"no answer key" gap is almost entirely THIS. It is a missing SIGNAL, not mainly a data limit.

STEP 4 -- COMMIT. Ours: global settle (Eisner) = brain-like constraint-satisfaction settling. LITTLE loss (the
greedy->settle fix already recovered ~+0.06 and stopped error-amplification).

STEP 5 -- DATA (quantity AND quality). Ours: ~3-6k sentences (~50-100k words) of ADULT text. Child: tens of
millions of GROUNDED words (Hart & Risley 1995 ~30M by age 3; revised to ~4M typical by Gilkerson 2017 LENA), and
that input is EASIER -- formulaic/frequency-skewed frames (Cameron-Faulkner 2003) and "optimized for syntax-free
semantic inference" (Sci. Reports 2021: CDS redundancy lets local co-occurrence recover verb causativity WITHOUT
syntax). So we are ~100-1000x under the child on QUANTITY and on QUALITY (grounded+formulaic vs raw adult text).
Grounding still dominates (propose-but-verify is near one-shot).

STEP 6 -- PROSODY (a signal a TEXT reader structurally lacks). PINNED: infants use speech rhythm/pausing/pitch
for phrase+clause BOUNDARIES (6-9mo) and coarse HEAD-DIRECTION typology (3mo, Christophe 2003; Bion 2013).
A text-only reader has NO analog (punctuation is a sparse, weak, late substitute). Genuine additional loss -- but
COARSE (boundaries + word-order typology), NOT fine dependency attachment; and prosody needs function words for
labeling. So it is a real but bounded text-reader deficit, not the main lever (which remains grounded meaning).

RESEARCH CONFIRMATION (lit-scan): Step 3 is PINNED -- Brown & Hanlon 1970 + Marcus 1993: children get NO reliable
EXPLICIT grammatical answer key; parental correction tracks TRUTH/MEANING, not grammar -> the brain's answer key
IS meaning. Grounded-meaning-as-supervision is PINNED (Yu & Smith 2007 cross-situational; Tanenhaus 1995
visual-world; and DIRECTLY: Alishahi & Stevenson 2008 -- a model that learns argument structure from utterance-
MEANING pairs with NO gold trees, the precedent for the build). Self-training error-amplification is PINNED
(Arazo 2020 confirmation bias; Blum & Mitchell 1998 co-training: a self-referential loop needs an INDEPENDENT
second view to break it -- grounded meaning IS that second view). Predictive coding is grounded against real
input (Rao-Ballard 1999; Friston 2010). TWO HONEST CAVEATS (synthesis inferences, NOT citable claims): (i)
framing grounded meaning as a "different-kind-of answer key" is our synthesis; (ii) "grounded prediction error
avoids self-training collapse" is well-motivated by combining the ML + neuro literatures but NO paper states it
directly. The mechanism pieces are pinned; the exact bridge is ours-under-test.

VERDICT (owner's "we should NOT be losing that accuracy" -- CORRECT): most of 0.42->0.87 is signal we DISCARDED,
not a fundamental limit. Single highest-leverage missing signal = GROUNDED MEANING as the verification/
supervision signal: it (a) replaces the missing answer key (Step 3, +0.20) by correcting the parse against
meaning, and (b) supplies the selectional/valence cue (Steps 1-2, much of +0.27). Down-payment already measured:
grounded meaning picks the agent 43% where word-order gets 0% on non-canonical clauses. Genuine residual limit is
small (~0.08 representation + some data-scale). FIX brain-foundationally: make supervision GROUNDED (meaning-
verified propose-but-verify) and LEXICAL/valence-aware -- NOT add an answer key, NOT mainly add data.

## (N) IMPLEMENTED ALL IMPROVEMENTS + RETESTED -- HONEST NEGATIVE (exp_grounded_online_learner_v1)
Built the fully brain-foundational learner integrating EVERY research-identified improvement: online PE-gated
Hebbian (predictive_coding) + CLASS-based grounded selectional cue (meaning_foundation) + grounded propose-but-
verify + global-settle + consolidation + innate bias + never frozen. Retested at scale with CONTROLS (plain-
ungrounded; scrambled-meaning).

RESULT (UD-EWT test, maxlen<=10, 2 passes): aggregate UAS plain 0.395 -> grounded 0.422 -> SCRAMBLED-meaning
0.448 (scrambled BEATS grounded). Hard arcs (obl:agent/obl/nmod/iobj) plain 0.158 -> grounded 0.196 ->
SCRAMBLED 0.215 (scrambled BEATS grounded again). Learning curve DRIFTS DOWN (hard 0.25 -> 0.20 as it reads).
An early tiny-smoke result (real meaning +0.057 over scrambled on hard arcs) DID NOT REPLICATE at scale -- I
withdraw it (adversarial control beat the hopeful reading).

HONEST VERDICT: implementing all improvements did NOT recover the 0.42->0.87 accuracy, and the CONTROLS show why
the grounding did not help: on the attachment SKELETON (UAS), grounded meaning does not beat a structural-bias
(scrambled) control -- for the 4th time across independent experiments. This is consistent, not a fluke: MEANING'S
REAL CONTRIBUTION IS ROLE ASSIGNMENT (agent/patient given structure -- measured 0.43 vs 0.00 on non-canonical),
NOT the attachment skeleton that UAS scores. Two further honest reasons the text-only recovery fails: (a)
propose-but-verify needs a genuinely EXTERNAL corrector (the world/situation); a text-only MEANING-VECTOR cue is
NOT independent of the parse (Blum&Mitchell 1998 -- a self-referential loop needs an independent second view), so
it cannot supply the missing +0.20 "answer key" or break the self-training drift; (b) the online learning is not
yet STABLE (drifts down; stability/plasticity/consolidation unsolved). So the earlier projection that grounding
would recover +0.20/+0.22 is CORRECTED: not from a text-only cue. The genuine path (all evidence converges):
ground the parser in the reader's actual SITUATION/MEANING model (an external corrector), applied to ROLE, not a
meaning-vector cue on the skeleton -- a major integration, beyond a text-only parser. Architecture is 100%
brain-foundational in MECHANISM; the accuracy is NOT recovered from text alone, and the controls are what prove it.

## (O) VETTED THE NEGATIVE -> ROOT CAUSE + FIX, VERIFIED ON BOTH THE PARSER AND THE LIVE MEANING CHANNEL
Aggressive vet of the grounding negative (exp_vet_why_grounding_failed_v1): ROOT CAUSE = the meaning vectors were
NEAR-COLLINEAR (mean pairwise cosine of noun vectors = 0.9221) -- a dominant common component swamped them, so
cosine could not discriminate words (true object no more similar to the verb than random sentence nouns: gap
+0.0042; cue-alone head-pick at chance; real ~= scrambled because both were noise). This is a known averaged-
embedding degeneracy (Arora et al. 2017 "all-but-the-top"); the brain's representations are discriminative /
contrast-normalized. THE DEVIATION: we fed raw un-normalized averaged embeddings, not a discriminative rep.

FIX = whiten (subtract global mean + project out top-D principal components, renormalize). VERIFIED:
  * At the cue level (exp_grounding_whiten_fix_v1): diffuseness 0.9221 -> 0.0156; true-obj discriminativeness
    +0.0042 -> +0.0534 (13x); role real-vs-scrambled +0.017 -> +0.046.
  * END-TO-END in the grounded online learner (exp_grounded_online_learner_v1 --whiten): on the meaning-sensitive
    HARD arcs, real grounded meaning now BEATS its scrambled control +0.0198 (grounded 0.225 vs scrambled 0.205)
    -- a FLIP from pre-whitening (scrambled beat grounded, 0.215 vs 0.196) -- AND the learning is now STABLE (no
    drift). Aggregate still washes (word-order dominates the skeleton; meaning's locus is the hard/non-canonical
    fraction, as diagnosed). Modest (+0.020) but REAL and control-verified.
  * IN THE LIVE MEANING CHANNEL (exp_meaning_channel_whiten_v1, reusing the a_s harness, n=2676): whitening the
    WSD embedding lifts subordinate-sense accuracy DIAGCTX 0.3114 -> 0.3290 (+0.0176), FLATCTX +0.025, DIAG+TOPK
    +0.058 -- a genuine improvement to the shipped meaning instrument from the SAME fix. (Prototype: strategy
    should re-run the shuffled-diagnosticity twin + significance + vs the curated-foundation baseline before
    landing.)

VERDICT (owner's "the brain can do it, so once we get it right we can too" -- CORRECT): the negative was OUR
degenerate representation, not a limit of grounding. Fixing it (contrast normalization) flips the parser-
grounding control result and independently lifts the live meaning channel. Two brain-foundational wins from one
diagnosis. The parser lift stays modest because meaning's job is ROLE/non-canonical, not the word-order skeleton.

## Proposed hdlab/ diff (strategy lands, Q111)
Add `_FastLabelPlan` to `hdlab/arc_labeler.py` (the class body of `experiments/exp_arc_labeler_fastpath_v1.py::
FastLabelPlan`, verbatim). Add `ArcLabeler._ensure_fast(self)` that lazily builds `self._fast_plan =
_FastLabelPlan(self.weights, self.labels)` (mirroring `PosTagger._ensure_fast`). Route `label()` (and any
inference caller) through `self._ensure_fast(); return self._fast_plan.predict(feats)` per arc; KEEP
`_predict_label` and `_score` UNCHANGED as the training path and the self-checkable reference. Default-ON
(the witness is the gate). OPTIONAL brain-foundational add (separate, verdict-independent): expose
`predict_graded(feats) -> graded_competition.graded_pick(lane)` so the labeler can publish its label posterior
+ normalized entropy into the shared difficulty currency; this is byte-safe (argmax unchanged) and default-off
until a consumer is wired.

## KEY REALIZATIONS
1. **Prove byte-identity at the CONSTRUCTION level.** The guarantee is a theorem the moment you check that no
   label contains the `~` separator (so the split is exact) -- not a property you can only sample. Sampling
   22,921 arcs then confirms it, but the theorem is what makes it unconditional in the weights.
2. **The speedup and the fidelity upgrade are the SAME refactor.** The hard argmax computes `lane[]` and
   discards it. The fast path's whole point is to build `lane[]` efficiently -- which is exactly the graded
   competition activation the brain keeps. Optimizing for speed HANDED US the brain-faithful readout for free.
3. **A "byte-identical speedup" can still be a fidelity move if you look at what it materializes.** The brief
   framed this as pure hygiene; the disk says the labeler already computes the pinned Competition-Model
   operation and only its READOUT (argmax vs posterior) is the deviation -- so the fast path is the cheapest
   possible path to closing gap (1).
4. **Measurement traps I hit and fixed:** reading the same doc twice on one stateful reader (state accumulates)
   and `str()`-ing closure/object fields whose repr embeds a memory address both produced FALSE regressions;
   the honest guard is fresh-reader-single-read + value-typed-content-only.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, strategy folds in)
The arc labeler (`hdlab/arc_labeler.py`) computes the PINNED brain operation for grammatical-relation assignment
(linear cue integration = Competition Model / FLMP, McClelland 2013) but reads out a HARD ARGMAX where the brain
maintains a graded normalized posterior (Hale/Levy; Kiani-Shadlen; the loser persists, Christianson 2001). The
byte-identical fast path materializes the per-label activation `lane[]`, so `graded_competition` now applies to
the labeler at zero cost: argmax byte-identical (MAP-optimality), and the label entropy is a validated gold-free
error signal (AUC 0.930 vs info-free twin 0.481) -- the same difficulty currency the parser/role pools already
publish. Perf (byte-identical, not a fidelity change): labeler scoring 8.7-9.8x, ~4.2s/read on full LitBank
docs (~54% of a long-doc read). Remaining fidelity gap (deeper, NOT closed here, owned by other solvers):
per-arc INDEPENDENT labeling -- no shared-head/one-role-per-clause competition (Theta-Criterion; LFG
Uniqueness; McClelland-Kawamoto 1986 whole-clause settling) and no incrementality.

## ADJACENT COMPONENTS (seeds; evaluated for brain-fidelity, deferred to their owners)
1. **Per-arc INDEPENDENCE is the real remaining fidelity gap (OUR-INVENTION placeholder, not the brain's
   mechanism).** The brain assigns roles by whole-clause interactive-activation settling with within-role
   lateral inhibition + cross-role excitation (McClelland-Kawamoto 1986), enforcing one-subject/one-object
   uniqueness (Chomsky Theta-Criterion; Bresnan LFG). Our labeler classifies each arc independently. Concrete
   brain-faithful build target (from the research drill): structured/joint decoding with shared-head
   constraints -- CRF-style joint labeling or bipartite matching over the arcs of each predicate. This overlaps
   `improve_the_parser_verb_argument_attachment_for_who_did_what` / `the_argument_parser_is_batch_where_the_
   brain_is_incremental` / `no_shared_shallow_predicate_argument_front_end` -- NOT started here (Q113).
2. **The entity_states / copular binder and the who-did-what readout should consume the graded label posterior
   + entropy**, not the hard 1-best -- the labeler can now publish both for free. Belongs with
   `consume_the_graded_pos_posterior_uncertainty_aware...` (POS analog already in flight).
3. **The softmax `gain` is OUR-INVENTION-UNDER-TEST** (a precision term; `graded_competition` says reuse the
   predictive-reader precision-weighting, not a fixed 2.0). The parameter-free top1-top2 margin (AUC 0.934)
   sidesteps it; a gain sweep is the follow-up if the entropy magnitude (not just its ranking) is wired.

## What I did NOT establish
- A label-ACCURACY improvement. There is none by design (MAP-optimality: graded argmax == discrete argmax
  exactly, byte-identical). The exceed is speed + graded fidelity + a calibrated uncertainty signal, at zero
  output change -- NOT a point-estimate gain. Anyone wanting a who-did-what accuracy jump must close gap (1)
  (joint/incremental decoding), which is out of this scope.
- The whole-read cut as a doc-independent number. It is ~54% on these three full-length docs but shrinks on
  shorter docs; the robust claim is the 8.7-9.8x labeler speedup, not a fixed whole-read percentage.
- I did not LAND anything in hdlab/ (Q111 -- proposed diff above; strategy lands + re-verifies).

## What I would withdraw first if wrong
The **whole-read ~50% cut** -- it is doc-length-dependent and the affect/parser notes both warn whole-read
wall-clock is doc-noisy (my min/max are CI-separated on these 3 docs, but I would not generalize the
percentage). I would fall back to the 8.7-9.8x labeler-in-read speedup and the ~4.2s/read directly-removed,
which do not depend on doc mix. The byte-identity (theorem + 22,921 held-out arcs + full-model W3) and the
graded AUC 0.930-vs-0.481 results are robust and would stand.

## TLDR (plain language)
Every time the reader parses a sentence it labels each grammatical link, and it was doing that the slow way:
for each link it tried all 36 possible labels and rebuilt ~900 little text lookups. I confirmed a
already-built faster method gives the EXACT same labels -- provably, not just usually: 22,921 links from books
and a held-out test set, zero differences, and the whole downstream reading (who did what, causes, coreference,
timeline) comes out identical. On full-length books it roughly halves the reading time. Then, prompted to make
sure the piece is brain-like, I found something better than a speedup: the fast method internally computes,
for free, a full "how strongly does each label fit" score -- which is exactly how the brain represents a
grammatical decision (a graded competition, not a hard pick). Reusing an existing brain-model piece we already
built, this gives a reliable "the reader is unsure here" signal (it flags its own mistakes 93 times out of 100,
versus 48 for a scrambled control) at no cost and without changing a single answer. So: same answers, about
twice as fast on long texts, and a brain-faithful confidence signal we did not have before.

## QUESTIONS
None blocking. One decision for strategy at land time: wire the OPTIONAL `predict_graded` publisher now
(byte-safe, default-off) or defer it to whichever consumer-side problem picks up the graded label posterior.
I recommend adding the publisher (it is byte-safe and makes the signal available) but leaving it default-off.

## NEXT STEPS
1. Strategy lands the Q111 diff: `_FastLabelPlan` + `_ensure_fast` in `hdlab/arc_labeler.py`, `label()` routes
   through it, `_predict_label`/`_score` kept as training path + reference. Reverify
   `verification/test_arc_labeler_fastpath_landing.py` (5/5).
2. Optionally land the byte-safe `predict_graded` publisher (default-off) so the labeler's posterior + entropy
   feed the shared difficulty currency.
3. The deeper fidelity gap -- per-arc independence / joint-incremental role decoding -- is the next real lever
   and is already owned by the who-did-what / incremental-parser problems; feed them the concrete target
   (shared-head joint decoding + one-role-per-clause competition, McClelland-Kawamoto 1986).
