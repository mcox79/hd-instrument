# Prior-art drill: elegant glass-box mechanisms for the 4 hard-residual DesireDB failure types

**Filed:** 2026-08-08 by research (Sonnet synthesis over 4 parallel Sonnet lit-scan lanes).
**Trigger:** Director-directed focused prior-art drill. REPORT-ONLY — no code touched.
**Scope:** for each of 4 named hard-residual failure types in narrative goal/desire-fulfillment
detection — (a) valence-present-but-misleading, (b) implicit/inferential outcome, (c)
contrast/substitution/expectation-violation, (d) negated/avoidance goals — find the most elegant
known glass-box/structured mechanisms, with real citations, and map them onto our own substrate
primitives (VSA bind-bundle-cleanup, situation-model accumulate/collapse register,
coreference/Centering, goal-typing organ) without an LLM at inference.
**Query-privacy:** all 4 lanes searched only public academic terms (author names, paper titles,
theory names — OCC, RST, PDTB, SDRT, Talmy, etc.). No substrate-internal module names, configs, or
numbers went off-platform.

## HEADLINE

**A single factual correction changes the citation record, and one convergent finding is the
strongest actionable result: the DesireDB paper's own internal ablation shows a single glass-box
discourse-connective feature ("But-Present") alone reaches F1=0.68 — within 0.02 of their full
LSTM black-box best (F1=0.70) — meaning the authors' own data says contrast/concession discourse
structure (failure type (c)) is the single highest-value signal in this exact task, not an
LLM-only-solvable residual.** Second, independently, two separate research threads now converge on
the same citation for a different failure type: Talmy's (1988) Force Dynamics — already
half-wired into our own Channel B per the 2026-08-06 Plot Units comparison — is also this drill's
top-ranked mechanism for failure type (d) (negated/avoidance goals), via Kaup, Lüdtke & Zwaan's
(2006) situation-model account of how negated states get represented as standing slots. Both are
wire-don't-island opportunities against already-partially-built substrate, not new construction
from scratch. Third: for (a) and (b), the field offers deep, well-established, elegant theory
(OCC appraisal 1988; Schank & Abelson scripts 1977; Zwaan & Radvansky situation models 1998;
Trabasso & van den Broek causal networks) but implementing it requires either an ordering/precedence
fix (a, likely cheap) or genuinely new content-authoring (b, the classic 45-year script-knowledge
bottleneck this program has already independently rediscovered twice — see Cross-thread synthesis).

**Correction on record:** the task's framing cited "Rahimtoroghi, Hobbs, Walker" for DesireDB.
Verified via ACL Anthology + arXiv: the actual authors are **Rahimtoroghi, Wu, Wang, Anand &
Walker (2017)**, "Modelling Protagonist Goals and Desires in First-Person Narrative," SIGDIAL 2017
(arXiv:1708.09040, ACL Anthology W17-5543). **Jerry Hobbs is not a co-author.** The dataset is
first-person informal blog narratives (LiveJournal/WordPress/Blogspot), not "short stories."

P_deflated (existence-claim confidence that the mechanisms below are real, correctly cited, and
address the stated failure type): **0.68** (high — 4 independent lit-scan lanes, each citation
WebFetch-verified against a primary or near-primary source; deflated from raw ~0.88 per
lit-scan calibration discipline because several secondary numeric details — exact PDTB-3 sense
hierarchy diffs, Trabasso 1989 page numbers, RST formal constraint text — were verified only via
secondary sourcing, flagged inline below).
P_deflated (the narrower claim that the specific substrate-mapping recommendations below are the
right next build) is **capped at 0.50** per mandatory novel-synthesis ceiling — these are
plausibility reads connecting verified external theory to our own code, not tested claims.

## Per-failure-type mechanism synthesis

### (a) VALENCE-PRESENT-BUT-MISLEADING

| Mechanism | Citation | Core idea | Confidence |
|---|---|---|---|
| OCC cognitive-structure-of-emotions | Ortony, Clore & Collins (1988), *The Cognitive Structure of Emotions*, Cambridge UP | Emotions are appraisals of events relative to an agent's own goals/standards/attitudes, not free-floating word valence; formally separates "fortune-of-others" appraisal (bystander reacting to someone else's event) from "well-being" appraisal (agent reacting to own goal-relevant event) — the exact structural distinction a bag-of-sentiment-words approach collapses | HIGH (verified) |
| Scherer Component Process Model | Scherer (2001), in *Appraisal Processes in Emotion*, Oxford UP | Appraisal decomposed into sequential checks incl. explicit "goal conduciveness" (does this event help/harm THIS goal) as a scored dimension distinct from raw valence | HIGH (verified) |
| Lehnert Plot Units | Lehnert (1981), *Cognitive Science* 5(4), 293-331 | +/- affect states are goal-relative by construction, per-character track (already compared against our organs 2026-08-06) | HIGH (already verified in-project) |
| Hofmann, Troiano, Sassenberg & Klinger, appraisal-dimension emotion corpus | *COLING* 2020 | Modern, structured (non-black-box-only) operationalization: annotates goal-relevance/goal-conduciveness as an explicit intermediate layer for emotion classification, i.e. exactly the "appraisal-not-word-valence" pipeline stage failure (a) needs | HIGH (verified) |
| Elliott, Affective Reasoner | PhD thesis, Northwestern, 1992 | Symbolic rule-based OCC implementation, per-agent goal-relative emotion computation — a working glass-box precedent for the whole approach | HIGH (verified) |

**Substrate mapping:** per the 2026-08-06 Plot Units comparison note (item 2, verdict ADAPT), our
`goal_congruence_appraisal_type`'s Channel-B force-dynamics branch ALREADY computes a goal-relative
(not raw-lexicon) congruence read — it is simply unwired into `GoalOutcomeRegister`/
`select_outcome_owner`'s main decision path. The OCC/Scherer literature gives the theoretical
license this fix needs: the fallback ordering should PREFER the goal-relative congruence channel
over the raw opinion-lexicon valence channel whenever the former has a decision, not run them as
co-equal signals or let raw valence override. This reframes failure (a) as most likely a
**precedence/wiring bug against an already-correct primitive**, not a missing mechanism — the
cheapest of the four to test (see Cheap decisive test below).

### (b) IMPLICIT / INFERENTIAL outcome

| Mechanism | Citation | Core idea | Confidence |
|---|---|---|---|
| Schank & Abelson scripts | *Scripts, Plans, Goals, and Understanding* (1977), Lawrence Erlbaum | Stereotyped event sequences (e.g. RACE) let a reader fill in unstated goal-relevant outcomes from world knowledge — the original, canonical account of exactly "crossed the finish line first" -> "won" | HIGH (verified) |
| Zwaan & Radvansky, event-indexing situation models | *Psychological Bulletin* 123(2), 1998, 162-185 | Readers track protagonist/time/space/causation/**intentionality** dimensions; formalizes what a reader must maintain to link a later event to an earlier unstated goal | HIGH (verified) |
| Trabasso & van den Broek, causal network model | Trabasso & Sperry (1985), *J. Memory & Language*; Trabasso, van den Broek & Suh (1989), *Discourse Processes* | Explicit clause-category causal chain: Setting -> Event -> Internal Response -> **Goal** -> Attempt -> **Outcome**, linked by physical/motivational/psychological causal links | HIGH on the model; MED on exact 1989 cite (page numbers not independently pinned — [UNVERIFIED] on that detail only) |
| Graesser, Singer & Trabasso, constructionist inference theory | *Psychological Review* 101(3), 1994, 371-395 (title corrected from task framing: "Constructing Inferences During Narrative Text Comprehension") | Predicts WHEN readers generate script-based implicit-outcome inferences during reading (goal-relevance, coherence-building, explanation-seeking triggers) | HIGH (verified, title corrected) |
| Cardona-Rivera et al., symbolic plan recognition | AIIDE 2015 workshop (Joint Workshop on Intelligent Narrative Technologies & Social Believability in Games), pp. 16-22 | Modern (2015), still-symbolic (non-neural) plan recognition inferring character goal states in interactive narrative | HIGH (verified) |

**Substrate mapping:** this failure type needs actual world/script content, not just architecture.
The natural VSA-native realization: bind script-role vectors (e.g. `RACE ⊗ WIN-CONDITION`) and store
script-effect templates as codebook/cleanup-memory atoms; an event's parsed predicate structure
("cross" + "finish-line" + ordinal=1) is compared via cleanup-similarity against stored
script-effect templates, and on a match the goal-typing organ substitutes the inferred abstract
outcome (WON) before `congruence_decision` runs. **This is the same mechanism CLASS already
identified and partially adopted 2026-08-07** (Resnik selectional-association / VerbNet-Levin
verb-class backoff for OOV goal-verbs) generalized from verb-typing to event-outcome-typing — not
a new architecture, an extension of an existing pattern. The bottleneck is content-authoring
(which scripts, how many, how they're sourced), which is exactly the field's own 45-year-old
open problem (see Cross-thread synthesis) — this is the least cheap of the four to build.

### (c) CONTRAST / SUBSTITUTION / EXPECTATION-VIOLATION

| Mechanism | Citation | Core idea | Confidence |
|---|---|---|---|
| RST Concession/Antithesis | Mann & Thompson (1988), *Text* 8(3), 213-281 | Concession is formally defined as "denial of expectation" — a satellite clause sets up an expectation, the nucleus denies it; directly matches "wanted X, but got Y" | HIGH (verified); sub-relation formal constraint wording verified via secondary source, not primary text — flag MED on exact wording |
| PDTB-2/PDTB-3 Comparison.Contrast / Comparison.Concession | Prasad et al. (2008), LREC (ACL W17-5543... [PDTB-2, LREC 2008, L08-1093]); Webber, Prasad, Lee & Joshi (2019), PDTB-3 Annotation Manual, LDC2019T05 | Closed-class connective-sense taxonomy directly lexicalized around "but/yet/instead/however" (Comparison.Contrast, Comparison.Concession, Expansion.Substitution senses) | HIGH on existence/venue; MED on exact PDTB-2-vs-3 sense-inventory diff ([UNVERIFIED] pending manual read) |
| SDRT — Asher & Lascarides | *Logics of Conversation* (2003), Cambridge UP, ISBN 0521650585 | Formal, glass-box **defeasible (non-monotonic) logic** over discourse relations (Contrast, Result, Narration...), governed by Maximize Discourse Coherence: default axioms (e.g. "wanting X defeasibly implies getting X") that get DEFEATED by an explicit Contrast-marked clause and world knowledge. Confirmed: "but" is treated as normally REQUIRED for a Contrast/denial-of-expectation reading | HIGH (verified) — **the single most theoretically elegant match found in this drill**: it's not just a connective-lexicon detector, it's a formal account of exactly the override logic the failure type needs |
| Wilensky PAM / Meta-Planning; Schank TOPs/XPs; SWALE | Wilensky (1978 PhD thesis; 1981 *Cognitive Science* 5(3) "Meta-Planning"); Schank (1982, *Dynamic Memory*); Kass, Leake & Owens (1986), in Schank (ed.) *Explanation Patterns* | Plan-level analog: detects a plan failed and a substitute plan executed instead; TOPs/XPs classify WHICH kind of substitution (side-effect vs. adjacent-goal vs. total failure) | HIGH (verified) |
| Cheong & Young; Bae & Young — computational surprise/suspense | Cheong & Young (2006), *AAAI-06*; Bae & Young (2008), *ICIDS*; Bae & Young (2014) "Prevoyant" | Plan-based (STRIPS/HTN, non-neural) models of reader-expectation as a projected plan trace, surprise = measurable deviation | HIGH (verified) |

**Substrate mapping — highest-priority recommendation of this whole drill.** DesireDB's own
ablation (But-Present alone, F1=0.68) says a closed-class connective detector is nearly as good as
their full model. Wire a PDTB-style connective-sense feature (a small closed lexicon: but, yet,
instead, however, only to -> Contrast/Concession/Substitution senses) as a **third channel**
alongside the existing valence + action-recurrence channels, combined via **SDRT's defeasible
default-then-override logic specifically** (not another OR'd flag): default assumption "stated
goal -> fulfilled" is defeated when a Contrast/Concession-sense connective attaches structurally to
the goal clause. This is cheap (closed lexicon, no parser needed for explicit connectives),
theoretically well-founded (SDRT), and empirically pre-validated by the source dataset's own
ablation — the strongest single next-build candidate in this note.

### (d) NEGATED / AVOIDANCE goals

| Mechanism | Citation | Core idea | Confidence |
|---|---|---|---|
| Talmy Force Dynamics | Talmy (1988), *Cognitive Science* 12(1), 49-100 | Agonist/Antagonist force opposition; an avoidance goal = Agonist exerting force to keep a state at rest, later-stated outcome = Antagonist force overcoming that resistance — gives a principled polarity-inverted representation distinct from a negated approach-goal | HIGH (verified) — **already partially wired in our own Channel B per the 2026-08-06 Plot Units note** |
| Kaup, Lüdtke & Zwaan | *Journal of Pragmatics* 38(7), 2006, 1033-1050 | Experiential-simulation account: readers of a negated sentence first simulate the negated state, then suppress/replace it — motivates representing "never wanted to hear X" as a standing negative-expectation SLOT at goal-registration time, not a transient negation flag | HIGH (verified) |
| Elliot & Covington; Higgins Regulatory Focus | Elliot & Covington (2001), *Educational Psychology Review* 13, 73-92; Higgins (1997), *American Psychologist* 52, 1280-1300 | Approach/avoidance and promotion/prevention focus are argued as structurally DISTINCT goal types (not sign-flipped versions of one type), with distinct success/failure signatures — prevention-focus "failure" = the bad thing occurring, not merely a gain's absence | HIGH (verified) — theoretical warrant for a distinct `AVOID` goal-type class |
| *SEM 2012 shared task; BioScope | Morante & Blanco (2012), *SEM 2012, ACL S12-1035; Vincze et al. (2008), *BMC Bioinformatics* 9(S11):S9 | Glass-box cue/scope negation resolvers — useful for parsing the negation AT the goal clause itself, but local-scope only; does not itself bridge to a later affirmative-polarity outcome sentence | HIGH (verified); scoped as a sub-component only |

**Substrate mapping:** four concrete, small changes, in the SDRT/Talmy spirit of wiring existing
primitives rather than building new ones: (1) goal-typing organ tags AVOID-class goals as a
distinct type at extraction (theoretical warrant: Higgins/Elliot), not merely a negation bit on an
ACHIEVE goal; (2) the situation-model accumulate register instantiates the avoided content as a
standing tracked slot at goal-registration time (Kaup et al.); (3) `congruence_decision`'s
occurrence-gate, when checking an AVOID-typed goal, uses INVERTED polarity (recurrence of the
avoided content = failure, absence = success); (4) the already-existing Channel-B force-dynamics
agonist-realized/blocked primitive (Talmy) becomes the actual congruence computation for AVOID
goals specifically, since force-dynamics maps naturally onto "did the antagonist force overcome
the agonist's resistance." Per lane D's search: **no existing computational system was found that
solves this avoidance-polarity-to-affirmative-outcome matching problem** (checked directly against
both DesireDB and Chaturvedi & Goldwasser 2016 abstracts) — this is confirmed novel synthesis of
existing theory pieces, capped at P=0.50.

## DesireDB paper's own best model + follow-ups + public benchmarks

**Corrected citation:** Rahimtoroghi, Wu, Wang, Anand & Walker (2017), "Modelling Protagonist Goals
and Desires in First-Person Narrative," SIGDIAL 2017 (arXiv:1708.09040, ACL W17-5543). ~3,680
desire statements over ~3,500 first-person blog narratives; labels fulfilled (53%) / unfulfilled
(31%) / unknown (14%) / no-agreement (2%). **Best model: Skip-Thought LSTM encoder + full feature
set (Desire, Discourse, Connotation-Lexicon, Sentiment-Flow), F1 = 0.70**; logistic regression +
full features, F1 = 0.66; **single discourse feature "But-Present" alone, F1 = 0.68** — the
paper's own headline finding is that discourse markers are the single best predictor, nearly
matching the full black-box model. (Confidence: headline F1=0.70 verified across multiple sources;
the per-model/per-feature breakdown came from an AI-summarized document fetch, treated as
high-but-not-primary-source confidence.)

**Follow-ups:** searched the ~20-paper citation graph (Semantic Scholar). **No paper was found that
reuses the DesireDB corpus/task and reports beating F1=0.70.** Citing work builds adjacent
resources instead: SAGA (Vallurupalli, Erk & Ferraro, Findings of ACL 2024, goal-applicability
annotation), CoRE (Vallurupalli & Ferraro, Findings of ACL 2025, condition-based outcome-variance
reasoning), Vijayaraghavan & Roy (WWW 2021, motives/emotions from personal narratives), an
entity-based narrative-graph mental-state paper (NAACL 2021). A related but earlier (not
follow-up) predecessor: Chaturvedi, Goldwasser & Daumé III, "Ask, and Shall You Receive?
Understanding Desire Fulfillment in Natural Language Text," AAAI 2016 (a different desire-
fulfillment dataset, predates DesireDB by a year). This negative claim ("nothing has beaten it")
is search-based, not exhaustive — flagged accordingly.

**Public narrative-outcome benchmarks relevant to (b)/(c):** ROCStories / Story Cloze (Mostafazadeh
et al., NAACL 2016) — re-verified, plus the well-known style-only-shortcut finding (Schwartz et al.,
LSDSem 2017, 75.2% using only ending-style features + LM scores, ignoring story context; Cai et al.,
ACL 2017, confirms near-parity 72.5% ending-only vs 74.7% context-aware) — an important
methodological warning for any future goal/outcome benchmark we might construct: guard against a
model solving fulfillment classification from ending-style alone. Also verified: GLUCOSE (causal
commonsense mini-theories, EMNLP 2020), TellMeWhy (Lal et al., Findings ACL-IJCNLP 2021), Story
Commonsense (Rashkin et al., ACL 2018, character motivation/emotion chains), Sharma et al. (ACL
2018, debiased/adversarial Story Cloze — top models drop sharply), ATOMIC/COMET (Sap et al. 2019 /
Bosselut et al. 2019, flagged non-glass-box), HellaSwag (Zellers et al., ACL 2019). **No standalone
public benchmark specifically for narrative contrast/expectation-violation ("but/instead"-style)
was found** — flagged as a possible gap, not strong evidence of true absence.

## Cheap decisive test

Two-stage test, cheapest-first, targeting the highest-ranked mechanism (c):

**Stage 1 (calibration, ~1 hr):** implement a minimal closed-class connective detector (but, yet,
instead, however, only to) scoped to the goal clause / its immediate discourse continuation, run
IN ISOLATION as a standalone decision rule (mirroring DesireDB's own "But-Present" ablation) on our
existing DesireDB-derived test split. This replicates a published number on our own harness before
any new mechanism is trusted.

**Stage 2 (the real test):** wire the connective channel as a third input to the existing
valence + action-recurrence combination, using SDRT-style default-then-override precedence (not an
OR'd flag), and re-run the full macro-F1 eval.

## Falsifiable predictions

**HARD-PASS (Stage 1):** the isolated connective-alone rule scores macro-F1 in the 0.55-0.72 range
on our test split — i.e., is in the neighborhood of the paper's own reported 0.68, confirming the
signal transfers from DesireDB's blog-narrative register to whatever corpus we're currently
evaluating on.

**HARD-FAIL (Stage 1):** macro-F1 < 0.45 in isolation — signals a register mismatch (DesireDB's
informal first-person blog narratives vs. our own eval corpus) serious enough that the published
number should not be trusted as a prior for Stage 2.

**HARD-PASS (Stage 2):** adding the connective channel lifts the combined system's macro-F1
measurably above the current ~0.62 plateau (e.g. to >=0.65), AND a majority of newly-corrected
items are specifically failure-type-(c) contrast/substitution cases (not accidental correction of
unrelated items via a different pathway).

**HARD-FAIL (Stage 2):** no macro-F1 lift above 0.62, OR the lift is real but concentrated in
failure types (a)/(b)/(d) rather than (c) — meaning the mechanism is helping for reasons other than
the theorized SDRT-override pathway, which would need separate investigation before trusting the
mechanism's interpretation.

## Cross-thread synthesis

- **Directly extends `notes/research_plot_units_comparison_adoption_2026-08-06.md`.** That note's
  item-2 ADAPT verdict (Talmy force-dynamics primitive exists in Channel B, unwired into the main
  goal/outcome decision path) is corroborated independently here from BOTH sides: it is this drill's
  top mechanism for failure (d), and the appraisal-goal-conduciveness literature for failure (a)
  gives the same "wire an existing correct primitive into the main path" diagnosis for a second,
  separate failure type. Two independent failure types, same underlying fix pattern
  (precedence/wiring, not new construction).
- **Extends `notes/prior_art_modern_neurosymbolic_narrative_2026-08-06.md`.** That note flagged
  PDTB-3 `Contingency.Purpose`/RST PURPOSE-vs-RESULT as a candidate external-validation schema for
  the goal/outcome distinction generally. This drill adds the COUNTERPART label set — PDTB
  Comparison.Contrast/Concession and RST Concession/Antithesis — completing the discourse-relation
  picture: Purpose/Result validates the base mechanism, Contrast/Concession is the override signal
  for failure type (c) specifically.
- **Extends `notes/research_context_conditioned_grounding_and_extraction_2026-08-07.md`.** The
  VerbNet/Levin verb-class backoff table adopted there for OOV goal-verb coverage is the SAME
  mechanism class this drill recommends for failure (b) (script-effect lookup for implicit
  outcomes) — both are "closed-class linguistic-resource backoff table, no training corpus,
  additive to existing architecture" — reinforcing that pattern as the substrate's general answer
  to coverage/knowledge gaps, not a one-off.
- **IMPORTANT CAVEAT against the 2026-08-08 reckoning** (per MEMORY.md CURRENT FOCUS): the corrected
  held-out run found the congruence mechanism firing on only 2/80 items — a coverage crisis, not a
  discrimination-accuracy problem. All four mechanisms in this note address DISCRIMINATION on cases
  where a channel already fires and gets the hard case wrong; none of them fix a mechanism that
  isn't firing at all. **Before investing build time in any of the four recommendations above,
  confirm whether the current dominant bottleneck is still coverage** (in which case the
  2026-08-07 VerbNet/Levin backoff work is higher-leverage and should ship first) **or has shifted
  to discrimination-accuracy on cases that do fire** (in which case this note's (c) recommendation
  is the next build). This is a strategic read, not a tested claim — flagged per the "caveat
  interpretation, not just verdicts" discipline.

## Substrate-product implications

Never framed as publication value — product-relevant only. The single most concrete, de-risked,
cheap next action is the (c) discourse-connective channel: it is pre-validated by the source
dataset's own published ablation (a glass-box feature nearly matching a black-box LSTM), requires
no new content-authoring (closed lexicon), and has a clean formal combination rule (SDRT default-
then-override) rather than an ad-hoc OR. The (d) avoidance-goal wiring is the second most concrete
action because it reuses an already-half-built primitive (Talmy force-dynamics in Channel B) rather
than requiring new code, and is theoretically motivated by TWO independent, well-established
literatures (force-dynamics AND regulatory-focus psychology) converging on the same design. The (a)
fix may be the cheapest of all if it turns out to be purely a precedence bug (worth a same-day code
read to check before scheduling any build). The (b) mechanism is real and elegant but structurally
the most expensive — it requires new script/effect content, the same open bottleneck this program
has independently rediscovered multiple times (2026-08-06, 2026-08-07 notes) — and should be
sequenced last, or folded into whatever future cycle tackles the broader knowledge-content-authoring
problem rather than treated as a quick win.

## Recommended next mechanism to build (ranked by elegance x fit-to-substrate)

1. **(c) PDTB/SDRT discourse-connective defeasible-override channel.** Cheapest, most empirically
   pre-validated (DesireDB's own ablation), cleanest formal combination logic, directly testable via
   the cheap decisive test above. P_deflated=0.45 (novel-synthesis cap applies; the underlying cited
   mechanisms are HIGH confidence, the specific wiring recommendation is a plausibility read).
2. **(d) AVOID-goal typing + Talmy force-dynamics wire-in.** Reuses an existing half-built primitive;
   two independent, well-established literatures converge on the same design. P_deflated=0.40
   (slightly lower than (c) — four coordinated code changes needed vs. one for (c), more surface
   area for the recommendation to be wrong about).
3. **(a) OCC/appraisal precedence-ordering fix.** Possibly the cheapest of all IF it is a pure
   precedence bug (needs a same-day code-read to confirm before ranking it above (c)/(d) with
   confidence) — ranked 3rd here because that confirmation hasn't happened yet, not because the
   fix itself is expensive. P_deflated=0.35 (real uncertainty on whether it's a wiring fix or needs
   new logic; genuinely bimodal until the code-read happens).
4. **(b) Script-effect lookup / world-knowledge backoff table.** Most elegant theory of the four
   (Schank/Abelson, Zwaan, Trabasso are canonical), but most expensive to build (new content-
   authoring, the field's known 45-year bottleneck) and lowest near-term ROI given the open coverage
   question flagged above. P_deflated=0.30, same mechanism CLASS as the already-adopted
   VerbNet/Levin backoff (2026-08-07) so worth sequencing alongside that work rather than as a
   standalone build.

## Citations (verified count)

**~45 distinct real citations verified via WebSearch/WebFetch across 4 parallel lit-scan lanes**
(deduplicated across lanes; several sources — Lehnert 1981, Rahimtoroghi et al. 2017, Talmy 1988 —
were independently rediscovered by multiple lanes, reinforcing confidence). One significant factual
correction made to the task's own framing (DesireDB co-authorship — Hobbs is not a co-author).
Confidence is HIGH on essentially all author/year/venue bibliographic facts (checked against ACL
Anthology, arXiv, publisher pages, or Semantic Scholar); several fine-grained secondary details
(exact PDTB-3 sense-hierarchy diff, RST formal constraint wording, Trabasso 1989 page numbers, exact
per-model DesireDB feature-ablation breakdown beyond the two headline numbers) are flagged inline
as MED confidence / [UNVERIFIED], sourced from secondary summaries rather than primary-text
re-derivation within this session's time budget.
