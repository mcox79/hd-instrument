---
problem: consume_the_graded_pos_posterior_uncertainty_aware_starting_with_referent_np_detection
status: PARTIAL
bar: "PASS = an uncertainty-aware consumer (the graded CRF posterior -> referent_per_np NP/name detection, tie-broken by coref/entity evidence; glass-box, NO LLM) that improves the live who-did-what and/or coref_acc CI-separated with a shuffled-posterior twin LOSING and NO regression on confident tags. Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE -- the graded posterior cannot beat the 1-best on the live consumer, with the named cause + number -- is a FULL PASS. Strategy lands the Q111 wire."
result: "LOCATED NEGATIVE (a FULL PASS per the bar), attributed at three levels. (1) referent_per_np: consuming the graded posterior as soft-nominal referent recovery adds +0.0000 to live who-did-what (CLEAN_DO n=149: floor=soft=0.7919; FULL n=1354: 0.2511) -- the shuffled-posterior twin LOSES (-0.0126 CI-sep FULL) so the mechanism is real, but the true posterior changes ZERO picks because introduction is PROPN<->NOUN-INVARIANT (0/3669 head diffs) and coverage is frame-SATURATED (graded adds 0.26% of gold heads over the deployed frame detector). (2) coref/name: UPOS-independent by construction (parse_litbank_conll never reads the tag). (3) the ONE channel PROPN<->NOUN genuinely flips -- ANIMACY -- fed brain-foundationally (name->animate + expected-animacy-under-category-uncertainty) into the Competition-Model role assigner is a genuinely MORE-VALID cue (learned validity 0.511 > floor 0.467 > shuffled-twin 0.296; BEATS the twin CI-sep on the non-canonical slice, +0.0231) yet does NOT CI-separate over the hard 1-best on who-did-what (graded-floor +0.0000 all / +0.0026 n.s. non-canonical, LitBank name-rich n=2957), because English is word-order-DOMINANT (MacWhinney-Bates) so animacy is subordinate, and the CRF posterior is confident (mean top 0.949) so E[animacy]~=hard."
floor: "The DEPLOYED consumers, recomputed per population: (a) landed referent_per_np (base content heads + frame detector) who-did-what CLEAN_DO 0.7919 / FULL 0.2511 (25 LitBank docs); (b) the deployed animacy cue (lookup_animacy on the perceptron 1-best; PROPN->unk) in the landed Competition-Model role assigner, non-canonical role accuracy 0.6012 (science gold, n_test_pre~2000) / 0.0540 (LitBank non-canonical, n=389)."
controls: "SHUFFLED-POSTERIOR TWIN (soft-recovery + graded-animacy both) -- LOSES CI-sep (soft: twin -0.0126 FULL; animacy: graded>twin +0.0037 all / +0.0231 non-canonical CI-sep) -> the effect is the posterior's VALUES, not noise/extra-referents. INTRODUCTION-INVARIANCE (flip every PROPN<->NOUN, 0/3669 head-set diffs) -> excludes the brief's introduction mechanism. FRAME-SATURATION (graded soft adds 0.26% gold-head recall over frame) -> excludes the coverage lever. NO-REGRESS (brain-foundational name->animate animacy: live who-did-what+coref BYTE-IDENTICAL) -> excludes downstream regression. REFIT-PER-VARIANT logistic -> the animacy cue validity is SWEPT not adopted (research: English animacy validity is LOW). One-variable throughout (only the head set / animacy support changes)."
files_changed: "experiments/exp_graded_pos_diagnostic_v1.py, experiments/exp_graded_pos_whodidwhat_v1.py, experiments/exp_graded_animacy_competition_v1.py, experiments/exp_graded_animacy_litbank_v1.py, experiments/exp_whodidwhat_brain_chain_v1.py, experiments/exp_whodidwhat_stage5_thematic_fit_v1.py, experiments/exp_whodidwhat_register_native_store_v1.py, experiments/exp_whodidwhat_thematic_override_v1.py, experiments/exp_whodidwhat_ud_structural_v1.py, verification/test_graded_pos_consumption_located_negative.py, notes/problems/consume_the_graded_pos_posterior_uncertainty_aware_starting_with_referent_np_detection/{SOLVED.md, MECHANISM_DIFF_where_we_lose_signal.md, CHAIN_SIGNAL_LOSS_TRACKER.md}  (NO hdlab/ written -- optional Q111 fidelity diff + Stage-4 live-wire recommendation below)"
reverify: ".venv/Scripts/python.exe verification/test_graded_pos_consumption_located_negative.py"
---

## SOLVED (PARTIAL) -- a rigorous, multi-level LOCATED NEGATIVE + a brain-foundational reframe

**The disk outranks the brief, and it did here.** The brief's stated mechanism -- "a NOUN mistagged PROPN
opens the wrong discourse referent / mis-clusters a name" in `referent_per_np`, corrupting who-did-what +
coref -- is **refuted on disk**. I then pursued the REAL problem underneath (the owner's standing rule) and
found the graded posterior's genuine channel, prototyped it end-to-end with an upstream brain-foundational
fix, and measured that it too does not clear on the live metric -- with the cause named and quantified at
every level. Per the bar, a rigorous located negative is a FULL PASS.

## THE MECHANISM-DIFF (owner follow-up: where EXACTLY do we lose signal vs the brain?)

Full detail in `MECHANISM_DIFF_where_we_lose_signal.md` (brain's 8-stage who-did-what pipeline from
hdi_research, each stage mapped to our organ with its on-disk signal-loss number, mined from 7 landed
signal-loss cells + measured here). The load-bearing conclusions:

- **On canonical prose we ALREADY match the brain** (clean-DO reader 0.97-0.98 ~ human 95-99%; we even beat
  the spaCy competent parser +0.0539 CI-sep). **Gold-POS (-0.046) and gold-parse (-0.051) recover NOTHING** --
  the signal is not lost in tagging or parsing.
- **Half the apparent "0.25-0.44 wall" is the RULER, not the reader:** non-core roles (PP-oblique 49.5% +
  copular 24.6%) a patient-selector shouldn't pick, 26.55% defensible pronoun/coref errors, and 61% gold
  noise on the non-canonical set.
- **The GENUINE gap is the dorsal algorithmic triad -- Stages 4, 6, 7 -- which we lack**, the same machinery
  agrammatic patients lose (chance on reversible, intact on irreversible). Disk-measured: the **voice/word-
  order OVERRIDE cue (Stage 4) is worth +0.4389 on non-canonical** (Competition Model drop-passive ablation,
  CI-sep), and its strong graded form is DEFAULT-OFF; clause segmentation (Stage 6) filler-gap beats the
  landed resolver +0.12; reanalysis (Stage 7) is missing entirely.
- **This EXPLAINS my located negative, precisely:** the graded NOUN/PROPN posterior feeds **Stage 5**
  (animacy/thematic-fit), which the brain research proves is **NEUTRALIZED on exactly the reversible/non-
  canonical items we fail** -- there, only Stage 4 carries signal. I was tuning the wrong stage. The graded
  posterior's REAL contribution to who-did-what is the **VERB axis** (P(VERB) -> participle/verb detection
  for Stage 0/4, landed as P7: 19c dropped-verb recovery 0.582 -> 0.806), NOT the NOUN/PROPN axis this brief
  named.

## What I built (four experiments) + what each established

1. **`exp_graded_pos_diagnostic_v1`** -- WHERE is the leverage? On UD-EWT gold (n=24k tok) + real LitBank:
   - **Introduction is PROPN<->NOUN-INVARIANT.** `referent_per_np._content_head_positions` puts NOUN and
     PROPN in the SAME `NOMINAL` set, so flipping every PROPN<->NOUN in the tagger output leaves the opened-
     referent set IDENTICAL: **0 / 3669 head-set diffs** (721 LitBank sents). The brief's introduction
     mechanism cannot exist.
   - **Coverage is frame-SATURATED.** Perceptron head-recall 0.9615, +frame detector 0.9734; the calibrated
     CRF soft-nominal recovery (P(NOUN)+P(PROPN)>=0.7) adds **32 heads / 5714 = 0.56%** (precision 0.94) --
     a floor the heuristic frame detector already reaches.
   - **The one real channel: ANIMACY.** 267 of 387 UD PROPN<->NOUN swaps flip `lookup_animacy` -- the ONLY
     place the two tags change a reader output (confirmed by a full organ-map: coref/gender never read UPOS).

2. **`exp_graded_pos_whodidwhat_v1`** -- the brief's literal target, against the STRONGEST floor (landed
   `referent_per_np`, frame ON), through the LIVE default reader, one variable = the head set. **soft-nominal
   recovery adds +0.0000 to who-did-what** (25 docs; CLEAN_DO n=149 floor=soft=0.7919; FULL n=1354=0.2511),
   while the **shuffled-posterior twin LOSES** (-0.0126 CI-sep FULL): the graded signal is *correct* (harmless)
   but adds no value over frame. Located negative #1.

3. **`exp_graded_animacy_competition_v1`** -- the reframe: consume the graded posterior as a
   brain-foundational ANIMACY cue in the landed Competition-Model role assigner (`hdlab.graded_role_assigner`).
   Variants isolate every contribution: `floor` (perceptron 1-best -> lookup_animacy, PROPN->unk) ->
   `crf_hard` (CRF argmax) -> `name_hard` (PROPN -> gazetteer name-animacy) -> `graded`
   (E[animacy | CRF posterior] = P(PROPN)*name + P(NOUN)*wordnet + P(PRON)*pron) -> `twin` (shuffled posterior).
   On the science-text non-canonical gold (n_test_pre~2000): **graded-floor = -0.0020 n.s.**; the name fix is
   negligible (names sparse).

4. **`exp_graded_animacy_litbank_v1`** -- the BEST-CASE population (research caveat: the animacy cue only
   bites off the canonical path, in name-rich prose). 19c LitBank who-did-what, name-bearing + non-canonical
   slices. **graded-floor never CI-separates** (+0.0000 all n=2957 / +0.0026 n.s. non-canonical n=389 /
   +0.0000 name+non-canonical n=172), while **graded BEATS the shuffled twin CI-sep** (+0.0037 all,
   **+0.0231 non-canonical**). Located negative #2 -- with the mechanism proven real.

## WHY it is a negative -- the cause, named and quantified (not "it didn't work")

The brain-foundational graded animacy is a **genuinely more-valid cue** -- the refit logistic gives it
validity **0.511 vs floor 0.467 vs shuffled-twin 0.296**, and it beats the info-free twin CI-separated. The
mechanism is real and correctly built. It does not move who-did-what for three independently measured reasons:
- **English is word-order-DOMINANT** (MacWhinney-Bates, PINNED). Animacy validity (~0.51) is subordinate to
  order/adjacency/voice (1.67 / 2.82 / 3.23), so it rarely flips the argmax. This is the brain's OWN cue-
  validity structure, quantified -- not an implementation ceiling.
- **The CRF posterior is confident** (mean top category 0.949), so E[animacy | posterior] ~= the hard-routed
  value: the graded step is near-idempotent (the research-flagged calibration hinge, verified).
- **The non-canonical residual is UPSTREAM.** LitBank non-canonical role accuracy is ~0.05 for EVERY animacy
  variant -- floored by the reduced-relative / clause-segmentation / verb-subcat gap the
  `graded_role_assigner` docstring itself names as upstream. No animacy cue can lift it.

## The brain-foundational chain (owner directive: EVERY component, self + upstream, brain-foundational)

Researched this session (hdi_research); the chain is **PINNED end-to-end at the operation level**, and every
hard-commit the current pipeline makes is the *less* brain-faithful choice:

| link | verdict | grounding |
|---|---|---|
| graded category maintained + propagated forward (not hard 1-best) | **PINNED** (principle) | Interactive-Activation (McClelland-Rumelhart 1981); Kuperberg-Jaeger 2016; noisy-channel Levy 2008, Gibson 2013 |
| expected animacy = E_P[support] over category uncertainty | **PINNED** (operation) | probabilistic population codes Ma-Beck-Latham-Pouget 2006; Bayesian cue combination Ernst-Banks 2002 |
| a personal NAME denotes an animate person | **PINNED** (ATL person store) | Damasio 1996; Patterson 2007; Bruce-Young 1986; Snowden 2004 -- gazetteer = OUR-INVENTION proxy |
| animacy competes as a validity-weighted cue -> biases agent/patient | **PINNED** (operation) | MacWhinney-Bates 1984; Dowty 1991 proto-roles; Bornkessel-Schlesewsky 2009 -- the English WEIGHT is LOW |

So I built the upstream component (brain-foundational animacy: name->animate + expected-animacy-under-
category-uncertainty) that the current organ lacks (`animacy_lexicon`: PROPN -> empty overrides -> "unk" is
NOT brain-foundational -- it discards animacy for every name). The chain is faithful; the downstream *reward*
is ~0 because of the brain's own word-order dominance.

## Owner's three asks -- answered

1. **Prototype this component + the upstream brain-foundational component:** done. Upstream capability = the
   calibrated graded POS posterior (P7). Upstream fix I built = brain-foundational animacy (name->animate via
   the reader's own gazetteer = the "additional NER signal" the animacy docstring asks for; graded routing by
   the posterior). This component = the graded-animacy consumer feeding the Competition Model. Research-
   confirmed brain-foundational at every link.
2. **No downstream consumer of the upstream optimization regresses:** CONFIRMED. Patching animacy to the
   brain-foundational name->animate rule leaves the LIVE reader's who-did-what + coref + entities
   **byte-identical** (witness check 4) -- animacy is not in the primary role path (the primary patient/agent
   are structural: positional + parse-router; animacy enters only PP/goal typing). And the referent_per_np
   soft-recovery leaves the whole read byte-safe by construction.
3. **Should other consumers be revisited to be more brain-foundational, using the new upstream capability?**
   YES, and I evaluated each for fidelity (adjacent-component map below). The highest-value revisit is NOT a
   POS-consumption change -- it is the DOWNSTREAM role residual (verb-subcat supply, incremental clause
   segmentation, coref linking), which is where the who-did-what wall actually sits.

## Adjacent-component brain-fidelity evaluation (seeds the next problems)

- **`animacy_lexicon` (PROPN -> "unk"): NOT brain-foundational.** The brain knows a name is a person (ATL).
  Fix = name->animate via the gazetteer (built here). Fidelity-correct; role-metric no-op TODAY (measured),
  but the RIGHT representation and ready to pay off once the downstream cue-competition is live.
- **`graded_role_assigner` (Competition Model): brain-foundational, but DEFAULT-OFF (island).** It is the
  natural consumer of a graded animacy cue; its own headline gain came from voice/gap, and animacy is a
  low-validity backup -- so a graded-animacy upgrade to it has a low ceiling BY THE ORGAN'S DESIGN.
- **`referent_per_np` frame detector: brain-foundational** (function-word bootstrapping, Abney 1991) -- which
  is exactly WHY the graded category signal is redundant there (a brain-faithful robustness mechanism already
  covers the category-error case).
- **The who-did-what non-canonical wall = UPSTREAM** (reduced-relative structure: verb-subcat frames, clause
  segmentation, coref linking). This is the leverage, and it is owned by the concurrent non-canonical /
  graded-parsing briefs -- I hand it off rather than compete.

## META-finding: the graded posterior's high-leverage axis is VERB, not NOUN/PROPN

The graded POS posterior's proven high-value consumer is **P(VERB) -> `predicate_detector`** (P7, already
landed: 19c dropped-verb recovery 0.582 -> 0.806). The NOUN/PROPN axis this brief targets is **structurally
low-leverage**: introduction is category-robust (frame bootstrapping), coref is tag-independent, and the only
category-discriminating consumer (animacy) is a low-validity cue in word-order-dominant English. That is the
one-line answer to "consume the graded posterior for referent_np": the leverage the tagger-speedup finding
hoped for is not on this axis.

## KEY REALIZATIONS (the enabling moves)

- **Read the consumer before believing the error-share.** "PROPN<->NOUN = 28% of tagger errors" is TRUE and
  IRRELEVANT to referent_per_np: `_content_head_positions` treats NOUN and PROPN identically, so the 28% never
  reaches the referent set. The load-bearing move was mapping *where the tag actually changes an output* (an
  enumeration, not a search) before building -- it collapsed the brief's target to a no-op in one pass.
- **A twin that LOSES while the arm ties the floor is the signature of a correct-but-subordinate cue**, not a
  broken one. graded > twin CI-sep AND graded = floor together say: the mechanism works, the brain just
  weights it low here. Reporting the learned validity (0.511 > 0.467 > 0.296) turned "no gain" into a
  quantified brain-mechanism statement.
- **Calibration is the graded step's hinge.** Mean top posterior 0.949 => E[feature | posterior] ~= hard =>
  the graded blend can only pay where the tagger is genuinely uncertain, which is rare. Verified, not assumed.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md)

- `animacy_lexicon`: flag as **NOT brain-foundational for proper names** (PROPN -> "unk"); the brain-faithful
  representation is name->animate-person (ATL person store). A safe, gazetteer-gated fix exists (built here),
  role-metric-neutral today.
- Record the **graded-consumption principle** as PINNED (propagate the category posterior forward; compute
  downstream features as expectations under category uncertainty) but note its NOUN/PROPN payoff is capped by
  English word-order dominance -- the high-value axis is VERB (P7), already landed.

## PROPOSED hdlab CHANGE (optional; strategy lands, Q111) -- FIDELITY, not a who-did-what win

Make `animacy_lexicon.lookup_animacy` brain-foundational for names: when the (graded or hard) category belief
says PROPN and the surface token is a gazetteer first-name, return `{"animacy":"animate","category":"person"}`
instead of "unk". Optionally route it as the expected animacy under the CRF posterior (body:
`exp_graded_animacy_competition_v1._animacy_column(variant="graded")`). **This is a correctness/fidelity fix,
default-safe (witness check 4: live reader byte-identical), NOT a role-metric gain** -- land it because it is
the right representation and unblocks any future consumer that needs name-animacy, not because it moves a
number today. Do NOT wire graded soft-nominal into referent_per_np (measured +0.0000 over frame).

## What I would withdraw first if wrong

The claim that the animacy channel is "low-value because English is word-order-dominant" rests on the natural-
corpus population. If a downstream consumer with a HIGH animacy-validity task existed (e.g. cue-CONFLICT /
implausible-patient comprehension, where animacy is the deciding cue), the graded animacy could clear there --
I did not build that engineered population (it risks being a construction proof). What STANDS regardless: the
referent_per_np introduction-invariance (0/3669) and frame-saturation (0.26%) -- those are structural, not
population-dependent.

---
### TLDR (plain English)
The reader guesses each word's grammatical type once and commits. We now have a cheaper, calibrated way to keep
several ranked guesses. The brief bet that feeding those ranked guesses into the part that decides which words
are people/things would fix "who did what to whom." I checked on disk first and found the bet can't pay off the
way the brief said: the name-vs-common-noun mix-up (the tagger's biggest error) never changes which things the
reader tracks -- it treats names and common nouns the same there -- and the name/character grouping never even
looks at the grammar tag. The one place the mix-up matters is deciding if a word is a living thing, which the
current code throws away for every name. I built the brain-faithful fix (a name is a person, so it's alive) and
fed the ranked guesses into the reader's "who's the agent" competition. It IS a better signal (it beats a
scrambled version), but it barely changes the answer -- because in English, word ORDER does almost all the work
of deciding who did what, so "is it alive" is a tie-breaker that rarely gets to break a tie. Every piece is now
brain-faithful; the honest finding is that this particular lever is small, and the real bottleneck for hard
sentences is further downstream (untangling clause structure), not the grammar-tag step.

### QUESTIONS
None. (The negative is rigorous and multiply-attributed; the constructive animacy fix is measured byte-safe.)

### NEXT STEPS
1. **Optional:** land the brain-foundational name->animate animacy fix (fidelity, default-safe, no-op measured)
   -- the right representation, ready for a future high-animacy consumer.
2. **Do NOT** file more graded-POS-posterior consumers on the NOUN/PROPN axis -- it is structurally
   low-leverage (this result). The graded posterior's high-value axis (VERB -> predicate_detector) is already
   landed (P7).
3. **The real who-did-what wall is downstream:** reduced-relative structure (verb-subcat supply, incremental
   clause segmentation, coref linking) -- already owned by the concurrent non-canonical / graded-parsing
   briefs. Point the graded_role_assigner (Competition Model, currently default-OFF island) work there; a
   graded-animacy upgrade to it has a low ceiling by the organ's own cue-validity design.
