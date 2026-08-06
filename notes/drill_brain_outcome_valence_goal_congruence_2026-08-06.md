# Research drill: brain-faithful outcome-valence via goal-congruence (2026-08-06)

FORMALIZE-BEFORE-BUILDING drill, triggered by the deep VET's outcome-valence flag
(`notes/deep_vet_comprehension_organ_vs_brain_2026-08-05.md`, "NEXT-CAPABILITY PREP"). 3 parallel
Sonnet lit-scan sub-agents (appraisal theory; ACC/OFC/predictive-coding neuroscience; narrative
psycholinguistics), generic-terms-only per query-privacy. Opus/director synthesis below. Calibration
penalty applied per [[feedback-lit-scan-calibration-penalty]].

## HEADLINE

The brain computes outcome valence as a **goal-congruence comparison between a goal-specified desired
state and the actual outcome state on the SAME affected referent** — not as an intrinsic property of
the outcome word/event. This is convergent across three independent literatures (appraisal theory,
ACC/OFC neuroscience, narrative-comprehension psycholinguistics), though the *neural implementation*
of the comparison (signed prediction-error vs. state-representation shift vs. unsigned salience) is
genuinely contested. Our current `hdlab/goal_typing.py:84-87` lexicon (`V2_OUTCOME_UNMET`/`_MET` by
set membership) computes something else entirely — a goal-INDEPENDENT intrinsic-word-valence signal —
which the appraisal literature explicitly treats as a SEPARATE, dissociable computation from
goal-conduciveness (Kreibig/Aue/Scherer autonomic dissociation, cited below). The buildable fix
reuses three ALREADY-PROVEN substrate primitives (theme-binding, purpose-infinitival/desiderative
construction detection, per-sentence event extraction) plus one small SUPPLY (a hand-authored
result-verb-class register, same pattern as the desiderative/aspectual partition that cleanly fixed
t03/t12, commit `5da76bf34`). Predictive-coding's residual math is NOT the literal reuse (wrong metric
for a discrete class-match decision, same ruling as `frame_induction.py:27` for role decisions) but
ITS ORDER/SHAPE (predict-the-goal-implied-state, then compare to observed) is exactly the computation
being proposed — see verdict at the end.

## Cheap decisive test

Build the 10-item flip-pair bank specified below (all sentences hand-authored, ASCII, reuses the
`V2_OUTCOME_UNMET`/`V2_OUTCOME_MET` word inventory so the comparison is apples-to-apples against the
mechanism being replaced) and run BOTH the current lexicon and the proposed goal-congruence mechanism
against it. This is a ~1-day build (mostly composition of existing organs + one small verb-class
register) and a same-day measurement — no GPU, no training, pure glass-box logic. Full spec in
"THE CAN-FAIL TEST DESIGN" below.

## Falsifiable predictions

**HARD-PASS** (all must hold):
- Goal-congruence mechanism accuracy on the 8 core+entity-binding flip items (A/B/C/D) >= 0.875 (7/8).
- Lexicon baseline accuracy on the SAME 8 items <= 0.625 (near its constructed ~50% chance rate).
- Mechanism beats lexicon by >= 0.25 absolute on the flip set.
- Scramble control (shuffle goal-clause <-> outcome-clause pairing across items) collapses mechanism
  accuracy to within 0.15 of the item-set base rate (proves the signal is goal-CONTENT-driven, not a
  second hidden lexicon).
- Item H (theme-mismatch precision guard) abstains (no false MET/UNMET) across all seeds.
- Item G (positive control, non-flip) stays correct — no regression on today's easy cases.

**HARD-FAIL** (any triggers):
- Mechanism accuracy on the flip set < 0.625 (no better than the lexicon it's replacing).
- Mechanism-vs-lexicon delta < 0.15 (not a real improvement).
- Scramble does NOT collapse (mechanism is secretly still keying off the outcome word alone, not the
  goal — the exact failure mode this whole drill exists to catch).
- Item H fires a false verdict at any rate (over-generalizes theme-binding).

N=10 is small; convention is MIDDLE_BAND unless HARD-PASS clears decisively, with a follow-up
expanded 20-30 item bank (mirrors how the 48-item fair goal-owner instrument grew from a smaller
pilot) before production promotion.

---

## 1. BRAIN MECHANISM (SHAPE / POSITION / METRIC)

| System | SHAPE (representation + operation) | POSITION (pipeline stage) | METRIC (what's compared) | Confidence |
|---|---|---|---|---|
| Appraisal — Scherer's Component Process Model (CPM), goal/need-conduciveness check | goal/need state (desired situation) vs. encountered/actual stimulus situation; match/mismatch scaled by goal importance | a Stimulus Evaluation Check in the Implication-Assessment stage — AFTER relevance detection, BEFORE coping-potential; kept **structurally separate** from the "discrepancy-from-expectation" check and from "intrinsic pleasantness" | match vs. mismatch of the encountered situation against the goal-specified desired situation — NOT a property of the stimulus word (Scherer 2001; Kreibig, Gendolla & Scherer 2012, *Biol. Psychology*, autonomic dissociation of goal-conduciveness from intrinsic pleasantness) | HIGH (0.75) |
| Appraisal — Roseman / Lazarus goal-relative valence | goal/motive representation (a desire predicate over a state) vs. the event's effect on that state; for these theorists there is **no event-intrinsic valence term at all** | core relational theme computation, downstream of event perception | motive-consistent vs. motive-inconsistent — formalized as boolean entailment in the OCC-logic tradition (Adam, Herzig & Longin 2009) or a signed utility differential in EMA (Gratch & Marsella 2004/2009) | HIGH (0.75) |
| ACC/dACC outcome monitoring (FRN/ERN, reward-prediction-error) | outcome-identity ensemble representation that **shifts** from expected-outcome coding to actual-outcome coding on mismatch (Hyman, Holroyd & Seamans 2017, *Neuron*) | post-outcome, ~FRN latency (~250-300ms after feedback) | **CONTESTED**: classic signed reward-PE (Holroyd & Coles 2002) vs. unsigned salience/surprise (Talmi et al. 2013; Alexander & Brown 2011 PRO model; Heilbronner & Hayden 2011). The state-representation-SHIFT finding is the least contested piece and is the strongest direct evidence the compared object is a rich STATE, not a scalar. | MEDIUM (0.5, genuinely split literature — flag as contested, do not overclaim "signed PE" as settled) |
| OFC / vmPFC goal-value, expected-outcome representation | a "cognitive map of task space" — rich state/identity representation of the EXPECTED outcome, held BEFORE the outcome is observed (Wilson, Takahashi, Schoenbaum & Niv 2014; Schuck et al. 2016, human fMRI); Schoenbaum-line work shows OFC predicts specific outcome IDENTITY (not just scalar value) | pre-outcome / anticipatory; the actual comparison against realized outcome happens partly DOWNSTREAM (ACC, dopamine identity-PE) | expected outcome IDENTITY/state vs. realized identity/state; scalar value (Padoa-Schioppa & Assad 2006) is real and coexists but looks like a DERIVED readout, not the comparison primitive | MEDIUM (0.55 — partly cross-paper synthesis, not one paper's stated thesis) |
| Predictive coding / forward models (Friston active inference; Rao & Ballard 1999; Wolpert-Kawato motor forward models) | goal = prior/preferred belief over a future state; forward model predicts the consequent state; **residual = prediction error** | predict BEFORE observe; hierarchical; well-established at low-level sensorimotor, THEORETICALLY generalized to goal-outcome (Joffily & Coricelli 2013 formalize emotional valence as the rate-of-change of free-energy/prediction-error) | expected (goal-implied) state vs. observed state; residual sign/magnitude = the congruence signal. Empirically THIN specifically for narrative/goal-outcome tracking — the strongest empirical extensions are at the lexical/semantic level (N400-as-prediction-error), not "did the protagonist's goal succeed" | MEDIUM-LOW (0.45 — mostly theoretical extension at the goal-outcome grain; flag as inference, not settled empirical finding) |
| Narrative comprehension — Trabasso & van den Broek causal-network theory; Zwaan/Langston/Graesser Event-Indexing Model | Goal is a causal-network node; an Outcome node either causally TERMINATES the goal episode (satisfaction — no further motivated Attempt needed) or EXTENDS/REINSTATES it (failure — motivates a new subgoal). "Intentionality" (goal-relatedness) is one of 5 tracked situation-model dimensions (Zwaan, Langston & Graesser 1995) | online, clause-by-clause causal-link construction + situation-model updating; reading-time signature at dimension shifts | the Outcome's STRUCTURAL ROLE relative to the Goal in the causal network (chain-closing vs. chain-extending), NOT outcome-word polarity. Direct RT evidence goal-status is tracked/updated online: Lutz & Radvansky 1997 (goal-probe RTs differ for completed vs. failed vs. neutral goals) | HIGH (0.7) |

**Direct answer to the pre-registered question ("is outcome-valence a prediction-error between a
goal-set expected outcome-state and the actual outcome-state, and is the compared 'state' an
OBJECT-state")**: partially yes, with caveats. The cleanest DIRECT formalization found is Houlihan,
Kleiman-Weiner, Hewitt, Tenenbaum & Saxe (2023, *Phil. Trans. R. Soc. A*), who define
**Prediction Error = Achieved Utility − Expected Utility** per goal-relevant dimension — an explicit
computed discrepancy, not a lookup. CPM (Scherer) treats "discrepancy from expectation" as a
DIFFERENT, SEPARATE check from goal-conduciveness itself — worth respecting in the build (don't
conflate "was this surprising" with "does this help the goal"; our target is goal-conduciveness).
On the object-state question: convergent (not single-paper-stated) support from the OFC
cognitive-map literature (Wilson et al. 2014; Schuck et al. 2016) plus the ACC ensemble
state-representation-SHIFT finding (Hyman et al. 2017) — the compared substrate looks like a rich
STATE/IDENTITY representation of the affected object, with scalar reward value as a derived
readout, not the primitive. This directly supports representing goal-desired-state and
outcome-actual-state as (theme, verb/result-class) pairs on a shared object referent, rather than
as a valence scalar.

## 2. WHY THE LEXICON IS WRONG (the can-fail principle)

**The construction where a goal-independent word-lexicon MUST fail**: any pair of sentences sharing
an outcome CLAUSE (same event word, same object) where the antecedent GOAL differs such that the
SAME outcome event is desired in one context and undesired in the other.

> "Tom wanted to mend the boat before the tide came in. The boat sank." -> **UNMET** (repair goal
> blocked)
> "Tom wanted the boat to sink so he could collect the insurance money. The boat sank." -> **MET**
> (the goal WAS the sinking)

`hdlab/goal_typing.py:84-86` puts "sank"/"sink" unconditionally in `V2_OUTCOME_UNMET` — it scores
the second sentence UNMET, which is wrong; the outcome is exactly what the protagonist wanted.

**Is this a real, established brain phenomenon, not an artifact of a contrived example?**
Three independent lines of evidence say yes:

1. **Appraisal theory explicitly dissociates goal-conduciveness from intrinsic (word/event) valence
   as two different computations.** Moors, Ellsworth, Scherer & Frijda (2013, *Emotion Review*)
   document the field split: Frijda/Scherer/Smith&Ellsworth keep BOTH an intrinsic-pleasantness check
   AND a goal-conduciveness check; Lazarus (1991) and Roseman (1984/1996) go further and hold that
   valence has NO event-intrinsic component at all — it is entirely goal/motive-relative. Kreibig,
   Gendolla & Scherer (2012) show these two checks have DIFFERENT autonomic signatures (cardiac vs.
   electrodermal) — i.e. the brain is doing measurably different work for "is this word/event bad" vs.
   "does this event block my goal." Our lexicon, at best, approximates the intrinsic-pleasantness
   axis; Zwaan/Trabasso's OUTCOME_MET/UNMET dimension targets the goal-conduciveness axis. These are
   not the same computation, and only one of them is goal-relative-correct.
2. **Roseman's "motive-consistent/motive-inconsistent" appraisal is the textbook goal-relative-valence
   case**: the identical event (e.g. a relationship ending) is appraised as motive-consistent (positive)
   or motive-inconsistent (negative) purely as a function of the person's active motive regarding that
   relationship (Roseman, Antoniou & Jose 1996, *Cognition & Emotion*).
3. **Narrative-comprehension psycholinguistics shows the SAME critical sentence produces different
   comprehension signatures depending on earlier-established context**, the closest directly-verified
   analog being Albrecht & O'Brien (1993, *JEP:LMC*) — an identical target sentence is read faster or
   slower purely as a function of an earlier trait/plan-establishing sentence (their design is
   trait-consistency rather than literally goal-outcome, but it is the strongest same-critical-sentence
   design located and generalizes directly: readers do NOT process an outcome sentence in a
   context-free, lexically-fixed way). Suh & Trabasso (1993, *JML*) ran a directly goal-relevant
   consistent/inconsistent-action design (goal established, later action tested for
   consistency/inconsistency, converging discourse-analysis + think-aloud + recognition-priming
   evidence), though primary-source effect sizes were not independently re-verified in this scan —
   flagged. **Gap honestly noted**: no ERP (N400) study was located that manipulates the GOAL while
   holding the exact OUTCOME sentence wording fixed — the ERP-level confirmation of this specific
   effect appears to be an open literature gap, not a refutation. The RT/priming evidence base above
   is the strongest currently available.

Net: the goal-dependent-valence phenomenon is well-established at the appraisal-theory and
motive-consistency level (high confidence), and consistent with (though not yet ERP-confirmed for
the identical-outcome-sentence case in) narrative-comprehension psycholinguistics (medium confidence,
honest gap flagged).

## 3. BUILDABLE MECHANISM (glass-box, own-vs-build)

**Design**: extract the goal's DESIRED-STATE as a `(theme, result_verb_class)` pair and the outcome's
ACTUAL-STATE as a `(theme, result_verb_class)` pair on the SAME referent, then:
- `theme_desired & theme_actual` empty -> **ABSTAIN/NA** (no congruence relation; the outcome isn't
  about the goal's object — precision guard, matches the aspectual-precision-probe convention already
  used for the desiderative partition).
- same theme, same/entailing verb class -> **MET**.
- same theme, opposed verb class -> **UNMET**.

### What we already own (reuse unmodified)

| Piece | Source (production) | Role in this build |
|---|---|---|
| Theme extraction / shared-referent binding | `hdlab/goal_owner_select.py::clause_theme` / `_theme_tokens` / `entity_goal_themes` (48/48 HARD_PASS on the fair instrument's multi-goal tie-break, commit `6961f5b49`) | gives `theme_desired` and `theme_actual` — head nouns of determiner-led NPs, already proven to correctly bind "boat" across a goal clause and an outcome clause |
| Desiderative / purpose-infinitival construction detection | `hdlab/goal_typing.py::action_frame_feats`, `DESIDERATIVE_PASS`, `ASPECTUAL_STOP` (18/18 + 10/10 clean HARD_PASS, commit `5da76bf34`) | locates the embedded VP in "X wanted/hoped [NP] to VP" or "X wanted to VP [NP]" so the desired-state verb+theme can be pulled out of the GOAL clause, not just detected as present/absent |
| Verb lemmatization | `hdlab/thematic_role_labeler.py::lemma_verb` | normalizes tense so "sink"(goal) and "sank"(outcome) compare as the same lemma |
| Per-sentence event extraction | `hdlab/situation_reader.py::EventRecord` (predicate, agent, patient) | gives the outcome clause's `(verb_lemma, patient)` "for free" — already extracted for every sentence in production |
| Predictive-coding SHAPE (not the literal metric) | `hdlab/predictive_coding.py` (`predict` -> `residual` -> `gated_write`, currently islanded) | the ORDER of this computation — predict the goal-implied state BEFORE observing the outcome, then compare — is exactly the pattern being proposed. The literal numeric residual (bipolar FHRR cosine-mismatch) is the WRONG METRIC for a discrete class-match decision, same ruling `frame_induction.py:27` already made for discrete role decisions. Reuse the SHAPE as a design pattern; do not wire the literal residual math into this discrete comparison. |

### What must be built (new, small)

1. **`RESULT_VERB_CLASS` register** — a small hand-authored, innate-core physical/social result-state
   verb typology, same SUPPLY pattern (not induce) as `DESIDERATIVE_PASS`/`ASPECTUAL_STOP` that
   cleanly fixed t03/t12. E.g. `REPAIR_PRESERVE = {mend, fix, repair, save, rescue, protect, build,
   restore}` opposed to `DAMAGE_LOSE = {sink, break, fall, collapse, lose, fail, destroy, damage,
   wreck, crash, drown, flood}`; `ARRIVE_SUCCEED = {reach, escape, arrive, win, succeed}` opposed to
   `FAIL_LOSE = {lose, fail, miss}`. This is a defensible small SUPPLY (analogous scope to the
   desiderative-verb class), grounded in Levin's (1993) verb-class typology / Beavers' scalar
   change-of-state / result-state literature (not independently re-verified in this lit-scan pass —
   flagged as a follow-up citation check, the mechanism does not depend on the exact citation).
2. **Goal-desired-state extractor** — given a sentence where the desiderative/purpose-infinitival
   detector fires, pull `(clause_theme(embedded_VP_clause), lemma_verb(embedded_verb))` as the
   desired state. New, small, pure composition of the two reused detectors above.
3. **Congruence function** — the 3-way match/opposed/abstain logic above. New, ~20 lines.

**Routing per the USER error-flavor rule**: this is (1) *used-ability-wrong* for the existing lexicon
(retire it as a fallback-only default, not the primary signal) plus (3) *missing-fact* SUPPLY for the
verb-class register (small, hand-authored, same class of fix as the desiderative partition) — NOT
missing-LEARNING (no induction needed yet; a future OOV-verb-class induction is a legitimate v2
extension, analogous to the still-open desiderative-vs-aspectual OOV induction noted in the deep VET).

**Verdict on predictive-coding-residual, precisely**: **right SHAPE, wrong METRIC.** The
predict-before-observe, gate-on-mismatch ORDER is exactly the computation the appraisal + forward-model
literature converges on. But `hdlab/predictive_coding.py`'s literal implementation is a continuous
bipolar-vector cosine-mismatch over an associative memory — appropriate for continuous salience/surprise
signals, not for a discrete goal-verb-class-vs-outcome-verb-class match decision. Build the discrete
congruence function directly (item 3 above); treat predictive_coding as the validated DESIGN PATTERN
this composition follows, not a literal dependency — consistent with the standing ruling in
`frame_induction.py:27` for the sibling discrete-role-decision case.

## 4. THE CAN-FAIL TEST DESIGN

10-item hand-authored bank, ASCII, ready to build as `experiments/data/outcome_valence_congruence_v1.jsonl`.
Outcome words are drawn directly from the CURRENT `V2_OUTCOME_UNMET`/`V2_OUTCOME_MET` sets so the
comparison against the lexicon being replaced is apples-to-apples.

**Core flip pairs (A/B/C) — DAMAGE/LOSE-class outcome word, UNMET(default) vs MET(goal-desired):**

| id | text | gold | lexicon predicts | why lexicon is wrong (when it is) |
|---|---|---|---|---|
| A-unmet | "Tom wanted to mend the boat before the tide came in. The boat sank." | UNMET | UNMET | (control — lexicon happens to agree here) |
| A-met | "Tom wanted the boat to sink so he could collect the insurance money. The boat sank." | MET | UNMET | "sank" is always UNMET in the lexicon regardless of whose goal it serves |
| B-unmet | "Nora wanted to save the old oak tree from the storm. The tree fell." | UNMET | UNMET | (control) |
| B-met | "Nora wanted the old oak tree to fall so she could clear the lot for a shed. The tree fell." | MET | UNMET | same failure mode, "fell" |
| C-unmet | "Kate wanted to win the chess tournament. Kate lost the final match." | UNMET | UNMET | (control) |
| C-met | "Kate wanted her rival to lose the final match. Kate's rival lost the final match." | MET | UNMET | same failure mode, "lost" |

**Entity-binding stress pair (D) — MET-class outcome word, tests theme/referent binding not just
verb polarity (the outcome's referent must match the goal's referent, not just the verb class):**

| id | text | gold | lexicon predicts | why lexicon is wrong |
|---|---|---|---|---|
| D-met | "Owen wanted to win the race. Owen won the race." | MET | MET | (control) |
| D-unmet | "Owen wanted his sister to win the race. Owen's rival won the race." | UNMET | MET | "won" is always MET in the lexicon regardless of WHO won — the outcome's actual referent (rival) doesn't match the goal's desired referent (sister) |

**Precision guard (H) — theme mismatch, must abstain, not hallucinate a verdict:**

| id | text | gold | why it matters |
|---|---|---|---|
| H-abstain | "Derek wanted to fix his bicycle before the race. The library closed early." | NA/ABSTAIN | outcome doesn't concern the goal's theme (bicycle) at all; the mechanism must not force a MET/UNMET call |

**Positive control (G) — non-flip, easy case, no regression:**

| id | text | gold | why it matters |
|---|---|---|---|
| G-control | "Sara wanted to reach the summit by noon. Sara reached the summit." | MET | both lexicon and mechanism should agree; regression guard |

**Controls**:
- **SCRAMBLE**: shuffle which outcome sentence pairs with which goal sentence across the 10 items
  (same convention as `exp_c5_multigoal_content_coherence_tiebreak_v1.py`'s flip-control) — mechanism
  accuracy must collapse toward the item-set's marginal MET/UNMET base rate.
- **LEXICON baseline**: current `V2_OUTCOME_UNMET`/`V2_OUTCOME_MET` set-membership check on the
  outcome sentence alone (the mechanism being replaced) — by construction ~50% on the flip pairs.
- **MAJORITY-CLASS baseline**: predict the more-frequent gold label across the 10-item set.
- **Known v1 scope limit (not tested here, flag for v2)**: negated/prevent-goals ("wanted to PREVENT
  X from winning", "wanted X to NOT VP") require negation-scope handling over the desired-VP, a
  genuinely separate mechanism from verb-class polarity matching. Excluded from v1 to keep the
  discriminator clean; do not conflate a v1 pass with negation-robustness.

## Cross-thread synthesis

This drill directly continues the deep VET's "6 slight differences" table (`notes/deep_vet_
comprehension_organ_vs_brain_2026-08-05.md`, row 6, predictive coding) and its "NEXT-CAPABILITY PREP"
outcome-valence flag, which had already correctly ruled OUT the appraisal-sim
(`exp_grounded_appraisal_sim_earned_v1.py`) as a drop-in reuse (it VALUES a hand-mapped congruence
input, doesn't COMPUTE congruence from goal+outcome) and correctly flagged predictive-coding as a
candidate needing verification. This drill supplies that verification: predictive-coding's SHAPE is
right, its literal metric is wrong, and the actual reuse path runs through the ALREADY-PROVEN
goal-owner organ's theme-binding and construction-detection machinery (LANDED-3 through LANDED-6 in
the deep VET), not through predictive_coding or the appraisal-sim directly. This also converges with
the deep VET's META-PATTERN 1 (severed top-down loop): goal-congruence outcome valence is, in the
brain's own architecture, computed by comparing an EXPECTED state (goal-set, top-down) against an
OBSERVED state — exactly the recurrent/predictive loop the deep VET found missing across all 4
components. Building this the goal-congruence way (rather than patching the lexicon) is simultaneously
the outcome-valence fix AND one more concrete instance of wiring the predict-then-observe loop the
deep VET calls for structurally, without literally forcing predictive_coding's numeric residual where
it doesn't fit (same discipline already applied to frame/role decisions).

## Substrate-product implications

- **Immediate build target** (not gated on anything else landing first): a new experiment cell,
  e.g. `experiments/exp_outcome_valence_goal_congruence_v1.py`, implementing the congruence function
  + `RESULT_VERB_CLASS` register + the 10-item bank above, following the exact wire-don't-island
  promotion convention `hdlab/goal_typing.py`'s own docstring documents (byte-identical-copy
  promotion after HARD-PASS + certification).
- **Backward compatibility**: on today's ~62-item fair goal-owner instrument (which does not contain
  goal-dependent flips), the ABSTAIN-to-lexicon-fallback path preserves current behavior exactly —
  this is a strict capability ADD, not a risk to the 48/48 goal-owner milestone already landed.
- **Downstream consumer**: once HARD-PASS, this becomes the outcome-valence half of the
  `GoalOutcomeRegister` the deep VET's row #1 (persistent per-protagonist state) needs — outcome
  valence stops being a per-clause lexicon lookup and becomes a genuine goal-relative READOUT,
  closing one more of the deep VET's 6 gaps.
- **Do not overclaim**: this fixes the MET/UNMET *polarity* computation. It does NOT fix
  negation-scope (v2), does not address the still-open OOV verb-class induction (missing-LEARNING,
  a legitimate future extension), and does not by itself close the event-extraction precision gap
  (deep VET row #4) — outcome-valence and event-extraction are independent caps.

## Citations (verified count)

**Directly verified (fetched primary/secondary text, high confidence in the specific claim
attributed)**: Houlihan et al. 2023 (PMC full text, PE=AU-EU formula); Holroyd & Coles 2002; Talmi
et al. 2013 (jneurosci.org); Hauser et al. (PMC4033096); Heilbronner & Hayden 2011 (jneurosci.org);
Alexander & Brown 2011 (nature.com); Hyman, Holroyd & Seamans 2017 (cell.com/neuron); Padoa-Schioppa
& Assad 2006 (pubmed); Wilson, Takahashi, Schoenbaum & Niv 2014 (princeton.edu PDF); Schuck et al.
2016 (PDF); Joffily & Coricelli 2013 (PLoS Comp Biol); Moors, Ellsworth, Scherer & Frijda 2013
(*Emotion Review*, field-split claim); Zwaan, Langston & Graesser 1995 (*Psych Science*); Lutz &
Radvansky 1997 (*JML*); Albrecht & O'Brien 1993 (*JEP:LMC*). **Count: 15.**

**Secondary-source paraphrase / not independently verified verbatim (flagged inline above, treat
as directionally trustworthy but not quote-precise)**: Scherer 2001 CPM chapter; Kreibig, Gendolla
& Scherer 2012; Gratch & Marsella EMA papers (2004/2009); Adam, Herzig & Longin 2009 OCC
formalization; Dias, Mascarenhas & Paiva 2014 FAtiMA; Becker-Asano & Wachsmuth WASABI; Roseman,
Antoniou & Jose 1996; Lazarus 1991; Trabasso, van den Broek & Suh 1989; Trabasso & van den Broek
1985; Suh & Trabasso 1993 (design confirmed, effect sizes not independently re-verified); Levin
1993 verb-class typology (not directly searched this pass, cited from prior knowledge — flag for a
follow-up confirmation pass if the verb-class register's provenance needs a hard citation).
**Count: 12.**

**Genuine literature gaps found (not evidence of absence, evidence of a search miss or a real open
question)**: no ERP/N400 study located that manipulates the GOAL while holding the OUTCOME sentence
wording fixed (closest available: Albrecht & O'Brien 1993, trait-consistency not literally
goal-outcome); no direct narrative-comprehension-literature critique of lexicon-based sentiment vs.
goal-relative valence (closest adjacent: general lexicon-sentiment context-dependence critiques,
Taboada et al. 2011, and the NLP-side "SAGA" goal-applicability framework, arXiv:2408.05793).

**P_deflated for "the buildable mechanism as specified passes its own HARD-PASS test"**: raw estimate
~0.70 (composition of three already-proven substrate primitives + one small SUPPLY register, same
structural pattern as the desiderative/aspectual partition's clean 18/18+10/10 HARD_PASS). Deflated
per [[feedback-lit-scan-calibration-penalty]] by 0.20 for uncharted-regime risk (first time this
exact composition has been tried in this substrate) -> **0.50**, which also matches the novel-synthesis
P cap, so the cap is not binding beyond the deflation already applied. Confidence in the underlying
BRAIN-MECHANISM claims (goal-congruence as a genuine, dissociable, comparison-not-lookup computation)
is HIGH (0.7-0.75); confidence in the SPECIFIC neural implementation (signed-PE vs. state-shift vs.
unsigned-salience) is explicitly LOW-MEDIUM and flagged as contested throughout — do not build any
downstream claim that leans on "ACC computes a signed reward-prediction-error" as settled fact.
