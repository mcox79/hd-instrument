# BRAIN-FOUNDATIONAL KNOWLEDGE MAP — causal-testimony foundation

Synthesized from 4 liberal research drills + parent digests (2026-09-09, solver_opus48_causaltestimony). Each finding
tagged PINNED (well-established) / CONTESTED. Citations are for the SOLVED.md HOW-THE-BRAIN section.

## THE SIGNAL CHAIN (final component -> input -> source), mapped
| stage | what | signal type | brain-foundational? |
|---|---|---|---|
| FINAL | `predictive_world_model.causal_antecedent`: argmax_A [surprisal(B\|ctx) - surprisal(B\|ctx\A)] | needs directed cause->effect production strength, difference-from-norm | YES in FORM (Gerstenberg CSM; Trabasso; Hesslow) |
| INPUT | forward model W = P(next event-concept \| recent event-concepts) | ASSOCIATION (verb-concept co-occurrence) | **NO** — rung-1 (Pearl); anti-correlated with cause-selection (Hesslow) |
| SOURCE | delta-rule fit on raw textual ADJACENCY (simplewiki) | co-occurrence counting | **NO** — the defect |
| BRAIN SOURCE | directed causal knowledge; much from CAUSAL-LINGUISTIC TESTIMONY (generics/connectives/counterfactuals) + action-conditioned forward models | directed, interventional, mechanism-level | the target |

## A. CAUSAL KNOWLEDGE ACQUISITION FROM TESTIMONY
- **Testimony is a primary route to causal knowledge for UNOBSERVABLE links** (germs cause illness, smoking->cancer):
  Harris & Koenig 2006 (*Child Dev* 77:505); Harris 2012 (*Trusting What You're Told*); Harris/Pasquini/Duke 2006
  (*Dev Sci* 9:76 — children hold germs as real as cats via adult talk). **PINNED directionally**; the exact
  testimony-vs-observation % is **never quantified** (do NOT cite a number). Acceptance is selective/vigilant
  (Koenig & Harris 2005; Sperber et al. 2010 epistemic vigilance) — PINNED.
- **The causal-Bayes-net formalism has NO slot for "A causes B" as a datum** (Gopnik et al. 2004 uses only
  covariation/intervention; Shafto-Goodman pedagogical sampling is over *actions*, self-described as only "beginning to
  be applied to language"). So sentential causal testimony as a knowledge input is an **acknowledged formal GAP** —
  building it is a defensible OUR-INVENTION-UNDER-TEST, not a re-tread. **PINNED (as a gap).**

## B. LINGUISTIC MARKING (the miner SPEC) — see notes/research_causal_marker_mining_spec_2026-09-09.md
Directionality (Sanders-Spooren-Noordman 1992 "Order" primitive; PDTB; Wolff force dynamics):
- BACKWARD / effect-first (subordinate=CAUSE): because, since, as, for, due to, owing to, because of, on account of,
  as a result of, thanks to. (postposed "because" = effect stated first; sentence-initial = cause-then-comma-then-effect.)
- FORWARD / cause-first (clause1=CAUSE): so, therefore, thus, hence, consequently, accordingly, as a result, for this reason.
- CAUSATIVE VERB (SUBJ=cause, OBJ=effect): cause/lead to/result in/produce/trigger/bring about/give rise to/induce.
- COUNTERFACTUAL NECESSITY: "if X hadn't ... Y wouldn't (have)" (Lewis 1973; Halpern-Pearl AC2 but-for; Gerstenberg CSM 2021).
- GENERICS (kind-level causal; Leslie 2007/2008; striking-property subtype fits "smoking causes cancer"): treat as
  AUTHOR-BELIEF, never fact-verify (Cimpian-Erickson 2012).
- FORCE DYNAMICS (Talmy 1988; Wolff 2007): CAUSE / ENABLE / **PREVENT** (result does NOT occur -> EXCLUDE from
  cause->effect-occurs; a real correctness trap) / DESPITE.
- METHOD precedent (reference only): CausalNet (Luo 2016, EPC/CPE + PMI, COPA 70.2%), CausalBank (Li 2020, 314M pairs,
  95% meaningful), PDTB explicit/implicit ~53.5/46.5 (recall ceiling for connective-only).
- FAILURE MODES (guard): cue-only precision 74-85% (15-26% non-causal FPs; Girju/Khoo); since/as polysemy; Sweetser
  epistemic "because" ("he's home because the lights are on" = evidence, not cause); "so that" purposive; "even if"
  concessive DENIES necessity; direction-error rate unmeasured in prior work -> OUR held-out audit is the source.

## C. ASSOCIATION vs CAUSATION (why adjacency is the WRONG signal type) — the strongest support
- **Pearl's ladder + Causal Hierarchy Theorem (Bareinboim et al. 2022):** association-layer data almost never
  determines intervention-layer answers without structural assumptions; adjacency is structurally rung-1. Jin et al.
  2021 (EMNLP): causal direction is NOT recoverable from text surface statistics alone. Asymmetric-stat tricks
  (LiNGAM/ANM, Granger) need linearity/acyclicity/**no latent confound** — false for narrative (topic/schema confounds
  every co-occurring pair). **PINNED.**
- **Forward models are causal precisely where ACTION-CONDITIONED** (Wolpert-Ghahramani-Jordan 1995 motor forward model
  = P(sensation\|do(command)); Rezende et al. 2020: passively-fit transition models are causally incorrect for planning
  unless action is a true intervention). -> explains why the parents' ONE win was the GOAL slice (agent action = the
  intervention). **PINNED.**
- **Hesslow's difference-criterion (1988) — the key CAUTION:** a condition present in BOTH the target and the
  counterfactual/norm case is disqualified as an explainer *regardless of predictive strength* (oxygen predicts fire
  but is never "the cause"). Kahneman-Miller Norm Theory; Hilton-Slugoski Abnormal Conditions; Gerstenberg CSM 2021
  (CSM beats a "features of what actually happened" heuristic). Coherent narrative pushes ALL events' predictability to
  ceiling while ABNORMALITY/NECESSITY varies -> predictability and cause-selection are **actively anti-correlated**.
  **PINNED.** Confirmed on our disk: gold cause has ZERO lexical overlap with the effect on 54-59% of answerable items.
  ARCHITECTURAL COROLLARY: the difference/abnormality layer is EXACTLY the consumer's necessity read (ablation);
  cs_pmi also subtracts the marginal. So the architecture is right in form; only the transition layer's signal is wrong.

## D. ONLINE USE IN COMPREHENSION (per-story application)
- Backward causal-antecedent inference is a **two-stage, coherence-break-gated** process: cheap passive resonance
  always-on; deep backward search only on a discontinuity (van den Broek landscape; Graesser-Singer-Trabasso
  constructionist; McKoon-Ratcliff minimalist). A why-question IS the coherence break -> the trigger is well-defined.
- **Generic->specific binding = soft graded settling**, no formal rule established (Kintsch CI; Zwaan-Radvansky
  event-indexing: causation + protagonist are the dominant dimensions, PINNED; strict 5-dim architecture CONTESTED).
- **Coreference is a SOFT mutually-constraining cue, NOT a hard gate.** -> do NOT hard-gate candidates by coref (matches
  why the parents' hard coref-gating went flat). The forward-model lift signal (soft, graded) is the right shape.
- Next-drill candidate (deferred): ATL/angular-gyrus dual-hub taxonomic-vs-thematic split (Schwartz et al. 2011) to
  separate a causal-knowledge store from the general semantic store.

## E. AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md — the brief mis-cited)
- The brief cites "the 2021 amodal IFG/MTG/mPFC meta-analysis" for causal construction being amodal. **Feng et al.
  2021 (*Front Hum Neurosci* 15:666179) actually found NO overlap between discourse-causal and logical-causal networks
  and argues AGAINST a unified amodal account.** "Embodiment is not the lever" still holds, but via Bedny et al. 2012
  (blind subjects develop normal abstract/causal concepts), NOT Feng. Disk/lit outranks the brief.

## WHEN THIS LEVER FAILS (honest bounds, from the research)
Directed causal testimony ALSO fails when: (1) the link is implicit/unmarked (most narrative causation is not
connective-marked; PDTB ~46% implicit); (2) the everyday link is too OBVIOUS to be testified (Gricean: "people drink
because they are thirsty" is rarely written — the transmission gap is inverted for narrative); (3) the author's stated
cause inherits the norm-theoretic proximate-cause bias (testimony is not ground truth beyond selection); (4)
multi-candidate connectives still need the abnormality computation to resolve WHICH candidate. These are the located-
negative hypotheses the coverage number tests directly.
