---
topic: 19c register-robust argument attachment — brain mechanism + glass-box levers
date: 2026-09-03
---

# HEADLINE

**The on-disk record already answered most of this question three times over, and the answer is NOT "gold/silver
19c parse data" or "delexicalization" or "self-training" — it is (a) the 19c "attachment gap" is 89% NP-head
chunking + copula-as-AUX measurement artifact once the gold is cleaned and powered, not PP-attachment or
selectional-preference failure, and (b) the brain's register-robustness mechanism is Bayesian RE-WEIGHTING of an
already-broad repertoire (Kleinschmidt & Jaeger 2015 "ideal adapter"), fast (Fine, Jaeger, Farmer & Qian 2013:
measurable within ~16-30 exposures) but built on LIFETIME exposure breadth, not new-grammar acquisition — so the
practical lever is composition-fit as a FORWARD-PREDICTION signal (already demonstrated real, +CI-sep) and an
NP-head/case chunker, not parser retraining on 19c gold or silver data.**

If "70% attachment vs 97%" is measured on the same population as our on-disk LB_19c PP-chain-reachability metric
(0.6978 — suspiciously exact match to "70%"), then the disk record directly refutes the premise that closing this
gap via more/better attachment training is high-ROI: PP-attachment is only 8.1% of that population's residual: 65%
of "verb mistagged" failures are copula-as-AUX (CORRECT UPOS scored as wrong by an unrelated gold convention), and
of the true "selection" residual, 76-85% was gold-oblique-contamination — on a CLEANED, POWERED direct-object gold,
linear position alone reaches 91.78%, and the true 8% residual is 89% NP-head chunking (compound-modifier /
genitive-possessive), not semantic or attachment failure at all. **Verify which population your 70%/97% numbers
come from before funding a fix — the fix differs completely depending on which metric it is.**

# Cheap decisive test

Before funding ANY of the four candidate levers: re-run the existing `exp_19c_reach_failure_diagnosis_v1.py` /
`exp_19c_composed_cleaned_gold_v1.py` witnesses (`verification/test_register_native_located_negative.py`,
`verification/test_19c_composed_cleaned_gold.py`) and diff their population definition against whatever produced
the "70% attachment / 97% competent-reader" numbers in the brief. If they are the SAME population (LB_19c
who-did-what / PP-reachability), the located-negative chain below applies directly and no new experiment is
needed — route to the already-filed follow-ons. If they are a DIFFERENT population (e.g. raw UAS on a disjoint 19c
sentence sample, not gated through the who-did-what task), run one new cheap decisive test: the residual-taxonomy
script (`exp_19c_whodidwhat_residual_taxonomy_v1.py`'s method) applied to the NEW population — partition the ~30-pt
gap into {NP-head/chunking, copula/predication-convention, genuine PP-attachment, genuine selection, tagger error}
BEFORE choosing a lever. This single triage run (re-usable code, ~1hr) prevents funding a 19c-gold-acquisition or
distillation project that (per the disk record) would only move ~8% of a residual that may not even be the
dominant bucket.

# 1. THE BRAIN MECHANISM (PINNED vs SPECULATIVE)

**PINNED — register robustness is Bayesian re-weighting over an already-broad repertoire, not new-grammar
learning.** Kleinschmidt & Jaeger (2015, *Psych. Review* 122(2):148-203) "ideal adapter": comprehension = inference
over which of several previously-encountered generative distributions is currently active ("recognize the
familiar, generalize to the similar, adapt to the novel"); true from-scratch learning is reserved for genuinely
novel input. This is the theoretical scaffold for everything below.

**PINNED — the re-weighting is FAST and error-driven, on the order of a few dozen exposures, not extended
retraining.** Fine, Jaeger, Farmer & Qian (2013, *PLoS ONE* 8(10):e77661): a measurable adaptation shift after
~16 exposures to a critical structure (Block 1 of their design), strengthening further through ~26 exposures
(Block 3). Fine & Jaeger (2016, *JEP:LMC* 42(9):1362-1376): priming/adaptation is CUMULATIVE at the abstract
structural level (equal magnitude with or without lexical/verb overlap) and update size scales with prediction
error (rarer/more-surprising structures produce larger updates) — i.e. genuinely error-driven, a single sentence
is already one increment. **Caveat (still PINNED but with real uncertainty on magnitude):** Harrington Stack,
James & Watson (2018, *Memory & Cognition*) failed to replicate the original RC-ambiguity effect at N=423 powered
to the original effect size; follow-up work (Prasad & Linzen 2021; Yan & Jaeger 2020; a 2023 review titled
"Syntactic Adaptation: A Robust Phenomenon with Open Questions") finds construction-dependent, generally smaller
effects than 2013. Treat the MECHANISM (fast, error-driven, cumulative re-weighting) as pinned; treat any specific
EFFECT SIZE as uncertain.

**PINNED — constraint-based lexicalist integration, not a staged pipeline.** MacDonald, Pearlmutter & Seidenberg
(1994): parallel, probabilistic, competition-based integration of syntactic frame + morphology + semantic/
thematic fit at the decision point, no separate purely-structural stage. Trueswell & Tanenhaus; the substrate's
own prior BRAIN_MECHANISM_DRILL (notes/problems/register_native_parse_and_pos_training_data.../
BRAIN_MECHANISM_DRILL.md) independently reaches the same synthesis citing Levy 2008 / Gibson 2013 noisy-channel
co-inference and Christiansen & Chater 2016 (Now-or-Never, incremental bounded-buffer processing).

**PINNED — selectional preference is real but a MARGINAL (verb→class) signal is provably insufficient for
argument SELECTION; you need the CONJUNCTION.** Resnik (1996) selectional preference (S(v)=KL(P(class|v)‖P(class)))
generalizes co-occurrence over a taxonomy (WordNet) so rare/unseen nouns inherit class-level preference — this is
learnable from raw parsed exposure, no gold labels. But Bicknell, Elman, Hare, McRae & Kutas (2010) is the
decisive discriminating result: patient plausibility depends on the CONJUNCTION agent×verb ("the journalist
checked the spelling" fast vs "the mechanic checked the spelling" slow) — the marginal P(patient|verb) is
IDENTICAL in both, so a marginal/bag-of-arguments model is provably blind to the effect. Chersoni, Santus, Lenci &
Blache (2017) confirm on distributional models: role-STRUCTURED + composed models score ~72% on these items vs
~58% (≈chance) for bag-of-arguments. McRae, Spivey-Knowlton & Tanenhaus (1998) thematic fit; Metusalem et al.
(2012, N400/ERP) show the driver is EVENT-level, not pairwise lexical association. Frankland & Greene (2015):
separate neural populations for agent vs patient — a positive prediction for JOINT/conjunctive event binding over
flat co-occurrence.

**PINNED — for ENGLISH specifically, word order dominates the who-did-what decision itself; thematic fit/
selectional preference is a PREDICTION cue, not usually a SELECTION cue.** Bates & MacWhinney Competition Model;
MacWhinney, Bates & Kliegl (1984): when word order conflicts with animacy/plausibility, English speakers follow
ORDER (unlike morphologically-rich languages, which follow case/agreement). This is corroborated hard by our own
on-disk re-measurement (below): on canonical 19c/modern active-voice direct objects, linear position alone
resolves ~92% of cases, and the Bicknell/Chersoni composition effect is measurable on the held-out forward-
PREDICTION task (does the model anticipate the right patient) but NOT on the SELECTION task when order already
disambiguates — i.e. selection and prediction are dissociable and the literature (Altmann & Kamide 1999
anticipatory eye movements) puts thematic fit on the prediction/pre-activation side.

**SPECULATIVE / not directly evidenced in this scan:** the precise minimum EXPOSURE VOLUME (sentence count) needed
for register adaptation specifically to 200-year-old WORD-ORDER divergence (as opposed to the RC-ambiguity
paradigm tested); no paper in this scan tested syntactic adaptation to genuinely archaic (not just
domain-shifted-modern) word order.

# 2. EXPOSURE/DATA EFFECT vs ARCHITECTURE EFFECT

**Both, but the literature (and Kleinschmidt & Jaeger's framework specifically) says they are not separable —
they are the SAME mechanism applied at two timescales.** Lifetime exposure builds the REPERTOIRE of distributions
("recognize the familiar, generalize to the similar" — this is why an adult skilled reader treats 19c prose as
"a somewhat unusual member of an already-known family," not an alien grammar); fast in-context re-weighting
(Fine-Jaeger, ~16-30 exposures) does recognition-and-mixture-reweighting AMONG already-known distributions. The
architecture that MAKES fast adaptation possible (Bayesian mixture over a repertoire, error-driven update) is
itself something that must be built from broad prior exposure — so "architecture vs data" is a false dichotomy in
the human case: it is an architecture (belief-updating over a mixture model) that is trained by broad data
(lifetime reading) and then generalizes fast at inference (within a session) because the target register is
usually "similar enough" to something in the repertoire already. **No paper in this scan quantifies the relative
% contribution of repertoire-breadth vs in-context reweighting** — flagged as open, consistent with the lit-scan
calibration penalty (deflate any specific split estimate).

**For a glass-box parser, this maps directly onto a design choice:** don't try to make the base parser "know
archaic word order" from scratch (that requires either genuinely broad lifetime-scale exposure — i.e., a large,
representative pretraining corpus we don't have gold for — or an architecture that treats new registers as
mixtures of known ones). The tractable glass-box analog of "recognize the familiar, generalize to the similar" is
a STRUCTURED FALLBACK / MIXTURE-OF-CUES system (position cue + parse cue + selectional cue, reliability-weighted)
rather than a single retrained end-to-end parser — which is exactly the architecture our own on-disk work already
converged on independently (`convergent_cue_reader`, precision-weighted noisy-channel integration, reaching 68%
of chance→human on who-did-what by COMPOSING existing cues, not by retraining the parser).

# 3. GLASS-BOX ML ANALOGS, RANKED WITH PITFALLS

**(1) Silver-data distillation from a strong offline teacher on 19c raw text — MODERATE evidence it helps ONLY
for lexical/topical/noise domain gaps, WEAK-TO-NEGATIVE evidence for genuine syntactic/word-order gaps.**
McClosky, Charniak & Johnson (2006, NAACL/ACL) is the landmark positive result (self-training a
parser+reranker on unlabeled WSJ-ADJACENT news text: Brown-corpus F1 85.2%→87.8%, matching an in-domain-trained
model) — but note the target domain (Brown fiction) is NOT syntactically alien to WSJ, and gains shrank sharply on
the MORE syntactically-distant Switchboard corpus (only 12% error reduction vs 28% on Brown) — **evidence gains
degrade specifically as syntactic distance grows, which is exactly our regime.** No paper in this scan (searched
"diachronic parsing," "historical treebank adaptation," "distillation under domain shift") found a study
distilling a modern teacher onto genuinely archaic word order. The mechanistic risk, supported by domain-shift-KD
theory/vision literature (Berezovskiy & Morozov 2023, ICCV workshop: KD student degrades in proportion to
teacher-target divergence) and by direct analogy to Zeman & Resnik (2008) — where self-training ON TOP of a
cross-lingual (partly word-order-differing) delexicalized parser actively HURT (F dropped) — is: **a frozen
teacher that was never exposed to archaic word order has no mechanism to emit correct silver labels for it; the
student most likely learns the teacher's confidently-wrong modern-word-order attachment preferences AS IF they
were archaic-domain truth.** This is a THEORETICAL/analogical risk, not directly measured for this exact scenario
— deflate confidence accordingly. **Directly corroborating this on OUR data:** the disk record already ran the
closest available real-world analog (a gold-quality-matched register-native marginal store on a genuinely disjoint
19c-like corpus) and found the naive/marginal signal TIES its shuffled-domain twin — the "same architecture,
better-matched data" lever alone did not separate.

**(2) Self-training on the parser's own output over 19c raw text — REFUTED on our own data, and the literature
explains the mechanism.** Already tested and REFUTED on-disk ("Self-training for register/19c adaptation" —
stalls, model's own modern-biased parses reinforce the error; cited across 3 separate owner-DONE problems). The
lit-scan explains WHY: pseudo-labels are generated under the SOURCE model's decision boundary; when errors are
topical they wash out under reranking/agreement filters (McClosky's reranker; Wagner & Foster 2021 tri-training),
but when errors are SYSTEMATIC (a fixed modern-word-order attachment bias), all resampled/bootstrapped copies of
the same architecture share the same bias, so confidence/agreement heuristics confidently select the WRONG
structure and reinforce it. Zeman & Resnik (2008) show this failure directly: self-training on top of a
partly-word-order-mismatched delexicalized parser dropped F from 66.4 to 57.4. **Do not re-open.**

**(3) Delexicalized transfer — WRONG TOOL for a word-order-driven gap by construction.** Zeman & Resnik (2008)
and McDonald, Petrov & Hall (2011) show delexicalization transfers well ACROSS RELATED LANGUAGES specifically
because it strips lexical cues while KEEPING structural/POS-order cues — and McDonald et al. state explicitly the
method works "because... there is some regularity in how syntax is expressed" across their source/target pair
(shared SVO order). Ahmad et al. (2019, NAACL, arXiv:1811.00570) is the clean confirmation: transfer-performance
gap correlates with word-order distance at r≈0.90 across 30 languages — order-sensitive architectures degrade
sharply as word-order distance grows. **This is exactly backwards for our problem:** our gap (per the brief's own
framing) IS the word-order divergence; delexicalization removes lexical cues, which were never the problem
(vocabulary already matches ~90%), and keeps the exact structural/order-mapping that is broken. **Do not pursue.**

**(4) Hindle-Rooth-style selectional-preference PP-attachment correction — REAL signal (~78-80% standalone
accuracy per Hindle & Rooth 1993, CL 19(1):103-120), but LOW ceiling and ALREADY TESTED NEGATIVE as a post-hoc
corrector on our exact task.** Known limits from the lit-scan: needs substantial same-register data to estimate
associations reliably (Collins & Brooks 1995: accuracy drops 84.5%→81.6% just from discarding rare
co-occurrences); multiple distinct estimators cluster at ~81-88% on the same 4-tuple features — a representational
plateau, not a data-quantity problem; post-hoc correction on top of an already-decent parser IS a documented viable
pattern in one instance (Foth & Menzel 2006, reduces parse errors 14%), but **our own on-disk cell already ran
exactly this (`exp_register_native_pp_attachment_v1.py`, raw-19c-exposure Hindle-Rooth verb-prep/noun-prep
association, post-hoc re-attachment): it HURTS (reach −0.019, modern PP-attach −0.055) — it overturns cases the
parser already had right; margin-gated (only intervene when parser is uncertain) is a no-op (−0.002).** And
per the disk's diagnosis, PP-attachment is only 8.1% of the 19c residual anyway, so even a perfect fix caps low.
**Do not re-open the post-hoc-corrector form; the marginal/bag-of-arguments form of this same idea (verb-prep
selectional association used for SELECTION, not attachment) is real signal (AUC 0.64-0.88) but provably
insufficient alone (Bicknell/Chersoni) — needs the conjunctive/composed upgrade, which is lever (5) below.**

**(5) [Not in the brief's 4, but the one demonstrated-real, still-open lever] Composition
`P(patient|agent,verb)` as a FORWARD-PREDICTION signal + NP-head/case structural chunking.** Already
demonstrated real and CI-separated on our own 19c data, twice, on the correct instrument: composition beats its
agent-shuffle twin +0.040 CI[+0.033,+0.047] and the marginal +0.032 CI[+0.024,+0.040] on held-out forward
prediction (MRR, n=4000) — NOT on selection, where it ties (Bicknell's effect is a prediction/N400 phenomenon,
consistent with the psycholinguistics). Separately, the actual residual on CLEAN 19c who-did-what (8% of items,
after position resolves 92%) is 89% NP-head chunking (compound-modifier / genitive-possessive head selection,
+0.043 CI-sep when fixed) — a constituency/chunking build, not a semantic or attachment fix. Both are
FOUNDATION-IS-FREE offline builds from the 11M-word raw 19c corpus already in hand, no gold parse/POS treebank
needed, no LLM.

# 4. RECOMMENDED LEVER — ranked

**Given we have 11M words of raw 19c text, can build any static offline asset, but must be glass-box/LLM-free at
inference, and the brain's actual mechanism is fast Bayesian re-weighting over a mixture of KNOWN cues (not
retraining a monolithic parser): the single most brain-faithful AND practical lever is NOT any of the brief's
four candidates as originally framed — it is upgrading the EXISTING reliability-weighted cue-mixture (already
built and wired: `convergent_cue_reader` / `graded_role_assigner`) with (a) the demonstrated-real composition
signal routed to the FORWARD-PREDICTION path, and (b) an NP-head/morphological-case structural chunker — rather
than funding parser retraining (silver, gold, or self-trained) on the attachment/word-order axis at all.**

Ranked:
1. **NP-head + morphological-case structural chunker** (build once, offline, from raw 19c + WordNet/rule
   patterns; register-INDEPENDENT and CASE is BETTER preserved in 19c than modern English) — HIGHEST expected
   effect (+0.043 CI-sep already demonstrated → 0.961 on the residual it targets), LOWEST pitfall (it's a
   constituency-parsing fix, brain-faithful as the Right-Hand Head Rule / genitive-DP-head operation, orthogonal
   to the register-adaptation question entirely). **Pitfall: scope-limited — it fixes the 8% structural residual
   on CLEAN canonical data, not a broader "attachment" problem if the brief's 70/97 numbers are measuring
   something else. Verify the population first (the cheap decisive test above).**
2. **Composition-as-forward-prediction upgrade to `predictive_reader`** (agent-composed exemplar over a
   register-native ~200-d PPMI-SVD hub instead of the current 12-d sensorimotor centroid) — already de-risked,
   +0.083 CI-sep / 2.3x MRR over the current organ, built from raw 19c exposure, no gold. Brain-faithful
   (Bicknell/Chersoni mechanism, on the correct prediction instrument). **Pitfall: this raises anticipation/
   surprisal quality, not the who-did-what SELECTION number directly — don't oversell it as an "attachment" fix.**
3. **Reliability-weighted cue integration, extended with a genuine parser-confidence signal for 19c** (the
   `attach_conf`/`graded_competition` margin, currently emitted but unused, calibrated so the system AUTOMATICALLY
   down-weights the parser when it detects 19c-style low confidence and defers to position/selectional cues) —
   brain-faithful (Ernst & Banks 2002 precision-weighted cue combination; Levy/Gibson noisy-channel), cheap
   (wiring, not new training), moderate expected effect (the existing hard 2-parser-agreement proxy already added
   +0.006-0.10 CI-sep). **Pitfall: it's an integration fix, not a capability fix — it can't create signal the
   underlying cues don't have; only helps where SOME cue is still informative.**
4. **Silver-data distillation from a strong offline teacher, run on the 11M-word 19c corpus** — worth a SMALL,
   bounded pilot only if the cheap decisive test above shows the population is NOT dominated by NP-head/copula
   artifacts (i.e., there is a genuine, large, structural-attachment-specific residual the above three don't
   touch). Expected effect: LOW-TO-MODERATE per the lit-scan (works for lexical/topical gaps, degrades sharply
   with syntactic distance — Switchboard evidence), with the DOMINANT PITFALL being teacher-error propagation: any
   modern-trained teacher's confident, systematically-wrong attachment decisions on archaic word order become
   silver "gold," and — per the disk's own already-run marginal-domain-match experiment — a same-architecture,
   better-matched-corpus lever alone already TIED its shuffled-domain twin, suggesting the ceiling here is low.
   **If pursued: gate it on a HELD-OUT population disjoint from any 19c text used to validate levers 1-3, require
   an info-free teacher-noise twin (teacher run on SCRAMBLED-order 19c text) to lose CI-separated, and cap
   expected gain at the Switchboard-analog ~12% relative error reduction, not the Brown-analog ~28%.**
5. **Self-training on the parser's own 19c output — DO NOT PURSUE.** Already refuted on this exact substrate
   (3 independent problems); the lit-scan (Zeman & Resnik 2008; the pseudo-label-under-source-decision-boundary
   mechanism) explains why it cannot work when the error is systematic/word-order-driven rather than topical.
6. **Delexicalized transfer parsing — DO NOT PURSUE.** Wrong tool by construction (McDonald/Petrov/Hall 2011;
   Ahmad et al. 2019): it strips the cue (lexical) that isn't broken and keeps the cue (structural/POS-order
   mapping) that is.
7. **Hindle-Rooth post-hoc PP-attachment correction — DO NOT RE-OPEN.** Already empirically tested on this exact
   corpus and HURTS (−0.019 to −0.055); low ceiling even if it worked (8.1% of residual).

**HARD-PASS threshold for lever 4 (the only untested candidate) if pursued:** silver-trained arm beats the
current arc-eager operator on held-out 19c attachment/who-did-what, CI-separated, with an info-free
scrambled-teacher twin losing CI-separated, AND holds modern UD-EWT retention (no regression) — matching the
existing bar already written into `register_native_parse_and_pos_training_data_for_pp_attachment_and_robust_
tagging/PROBLEM.md`. **HARD-FAIL:** ties or loses to levers 1-3 already built, OR the info-free scrambled-teacher
twin does not lose CI-separated (indicating any apparent gain is domain-match/coverage, not attachment quality).

# Cross-thread synthesis

Three consecutive owner-DONE problems on this substrate (`register_native_parse_and_pos_training_data_for_pp_
attachment_and_robust_tagging`, `the_extraction_front_end_parser_is_the_cross_task_bottleneck...`,
`the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold`) already built and empirically
tested nearly every mechanism this brief asks about, on raw 19c LitBank exposure, glass-box, no gold parse/POS
treebank, no LLM — and found: PP-attachment = 8.1% of the 19c who-did-what residual; the "verb-ID collapse" that
looked like a tagging problem is 87% copula-as-AUX (correct); self-training refuted; post-hoc Hindle-Rooth
re-attachment hurts; marginal domain-matched re-estimation ties its twin; the "27% selection gap" was ~76-85%
gold contamination; on cleaned, powered data linear position gets 91.78% and the true residual (8%) is 89%
NP-head chunking; agent-composition is real but only on the forward-prediction instrument, not selection. Two
follow-on problems encoding exactly levers (1) and (2) above are ALREADY FILED on disk
(`the_who_did_what_selection_residual_is_structural_np_head_chunking_and_case_not_meaning`,
`upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub`) — check their current status
before dispatching new build work; they may already be solved or in progress.

# Substrate-product implications

In plain terms: the machine's "does it understand who did what in old writing" problem looked, at first glance,
like "it can't figure out which words go together" (an attachment/grammar problem) — and the natural fix people
reach for is "train it more on old writing." We already tried that path three times and it does not work, because
the real problem turned out to be much narrower and different: (1) about a tenth of the errors are a genuine
small grammar-chunking mistake (picking the wrong word inside a two-word phrase, like grabbing "trade" instead of
"van" in "trade delivery van"), fixable with a small rule-based fix, not more training; (2) most of what looked
like a tagging failure on old-style helper-verbs ("is," "was," "were") was actually being scored wrong, not
computed wrong; (3) the "meaning/plausibility" fix that sounds appealing (teach it what typically goes with what)
turns out to help the machine's ANTICIPATION of what's coming next, not its decision about what's already there.
Fixing this the expensive way (hand-building an old-English training set, or running a bigger AI parser
offline and training on its guesses) would cost real engineering time and, per the literature, is likely to just
copy that bigger AI's OWN mistakes about old word order onto our system, since it was never trained on
old-fashioned sentences either. The cheap, already-proven fixes cost far less and are already half-built.

# QUESTIONS

None blocking. One clarification requested of the coordinator: confirm whether "70% attachment / 97% competent
reader" is measured on the LB_19c PP-chain-reachability population (0.6978, matching "70%" closely) or a different
population — this determines whether the located-negative chain above applies directly or whether a fresh
triage run is needed first (the cheap decisive test).

# NEXT STEPS

1. Run the cheap decisive test (population match check) before funding anything.
2. Check current status of the two already-filed follow-on problems (NP-head/case chunker; predictive_reader hub
   upgrade) — likely already in progress or solved; do not re-derive.
3. If a genuine, large, structural-attachment-specific residual remains after (1) and (2), consider a SMALL bounded
   silver-data distillation pilot with the HARD-PASS/HARD-FAIL gate above — not a first move.
4. Do not fund: gold-19c-treebank acquisition, self-training, delexicalized transfer, or post-hoc Hindle-Rooth
   PP re-attachment — all already refuted or theoretically ruled out for this specific gap shape.

# Citations (verified count)

Primary sources cited above, with confidence: **21 high-confidence** (Kleinschmidt & Jaeger 2015; Fine, Jaeger,
Farmer & Qian 2013; Fine & Jaeger 2016; MacDonald, Pearlmutter & Seidenberg 1994; Resnik 1996; Bicknell et al.
2010; Chersoni et al. 2017; McRae, Spivey-Knowlton & Tanenhaus 1998; Metusalem et al. 2012; Frankland & Greene
2015; MacWhinney, Bates & Kliegl 1984; Altmann & Kamide 1999; Hindle & Rooth 1993; Collins & Brooks 1995; McClosky,
Charniak & Johnson 2006; Zeman & Resnik 2008; McDonald, Petrov & Hall 2011; Ahmad et al. 2019; Harrington Stack,
James & Watson 2018; Levy 2008; Christiansen & Chater 2016), **6 medium-confidence / number-unverified-this-pass**
(Wagner & Foster 2021; Sagae 2010; Foth & Menzel 2006; Kamide 2012 — corrected title; Berezovskiy & Morozov 2023;
Rotman & Reichart 2019), **2 low-confidence / flagged** (a 2026 arXiv self-training denoising-vs-forgetting paper,
venue unconfirmed; an OpenReview cross-domain-KD theory paper, authorship unconfirmed). Per
[[feedback-lit-scan-calibration-penalty]]: P estimates in this note are deflated 0.20 from lit-scan face value;
novel-synthesis claims (the exposure/architecture inseparability argument in §2; the "two follow-ons already solve
this" claim in Cross-thread synthesis) are capped at P=0.50 pending direct verification of those problems' current
SOLVED status.
