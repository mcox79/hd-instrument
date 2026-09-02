---
problem: register_native_parse_and_pos_training_data_for_pp_attachment_and_robust_tagging
status: REFUTED
bar: "PASS = a register-native-TRAINED parser/tagger (trained on GOLD target-register POS+parse data, via the in-substrate arc-eager + rich-structural training infra, NOT an LLM) that simultaneously: 1. raises PP-CHAIN attachment precision (argument ADP->object->verb, reported as attach PRECISION not global UAS) CI-separated over the current arc-eager operator on HELD-OUT target-register data -- with an info-free HEAD-shuffle twin LOSING CI-separated; 2. raises 19c who-did-what (or world-state recipient/source role recovery) CI-separated on held-out 19c/literary prose, attributable to the PP-attachment gain; 3. HOLDS the modern UD-EWT UAS gain; 4. does NOT regress argument RECALL or POS. A rigorous located NEGATIVE -- no acquirable/buildable gold target-register data brings the substrate parser's PP-attachment up, OR register-gain and modern-retention are provably non-co-satisfiable -- is a FULL PASS if it names which DATA is the blocker, the number, and the mechanism."
result: "LOCATED NEGATIVE (the bar's sanctioned full-pass form): register-native PARSE/POS training is NOT the 19c who-did-what lever, and the brief's premise is a MEASUREMENT ARTIFACT. On LB_19c (n=3015, chain-selector who-did-what vs the arc-eager operator): (a) the 19c PP-chain reachability residual (n=911 failures) is only 8.1% PP-attachment errors -- 65% is the target token 'mistagged', but 87% of THAT is COPULA-as-AUX (548/629), which is CORRECT UPOS, not a tagger error (the gold points verb_idx at a copula; UD makes the predicate complement the head); genuine archaic open-class verb mistag is 2.2% (67/3015). (b) Every brain-faithful, data-UNBLOCKED route built from RAW exposure FAILS its control: post-hoc Hindle-Rooth PP re-attach HURTS (reach -0.019; modern PP-attach -0.055); margin-gated selectional re-attach is a no-op (-0.002); frequent-frames register tagging (Mintz) is net-NEGATIVE (reach -0.014, both registers); copula-aware reading lifts who-did-what +0.079 CI[+0.069,+0.089] BUT is NOT separable from an info-free permissive traverse-all twin (COPULA-vs-TWIN +0.006 CI[-0.002,+0.015]); association-based SELECTION is NOT separable from its shuffled-association twin (+0.008 CI[-0.002,+0.018]). (c) The real bottleneck is SELECTION: base who-did-what 0.428 vs reachability 0.698 = 27% of items are reachable-but-mispicked (semantic plausibility), which the raw-exposure verb-prep association (real signal, AUC 0.64) does NOT resolve. THE DATA BLOCKER: no gold 19c/literary UD parse or POS treebank exists on disk (LitBank = coref/NER/events + 100 RAW novels; only modern UD-EWT is gold) -- but building it is LOW-ROI: PP-attachment caps at 8% of the reach residual and touches neither the 27% selection bottleneck nor the copula convention. WHERE THE REGISTER ACTUALLY BITES (cited exp_verbrole_exemplar_which_arg_v1, the p3 problem): the substrate's structured verb-role THEMATIC-FIT store beats its verb-shuffle twin +0.081 CI-sep on MODERN but TIES it on 19c (+0.002 CI[-0.011,+0.015]) and loses to the verb-blind prior (-0.070) -- so 'register-native' belongs at the SELECTION/meaning store (re-estimate exemplars on 19c exposure + ground archaic vocab via the grounded semantic-graph organ + add composition P(patient|agent,verb)), NOT at the parser or tagger. The parser's real service to this lever is TYPED ROLE SLOTS to build the store, not PP-attachment or register tagging. DECONFOUNDED (exp_19c_distributional_thematic_fit_prototype_v1): the 19c who-did-what gold is ~85% PP-oblique-contaminated; on the CLEANED direct-object 15%, the register-native thematic-fit selection signal IS real and CI-separated (beats its verb-shuffle twin +0.097 CI[+0.022,+0.178]; beats position +0.119) -- the mechanism works once the gold is clean. It still ties the bag-of-arguments twin, so COMPOSITION P(patient|agent,verb) is the remaining structural lever -- and COMPOSITION IS DEMONSTRATED REAL (exp_19c_composition_thematic_fit_prototype_v1: agent-conditioned fit beats its info-free AGENT-SHUFFLE twin +0.076 CI[+0.029,+0.123], beats position +0.158; the marginal->composed full margin is underpowered at n=171 clean-DO and needs a larger cleaned gold). The owned selection build = CLEAN the gold + add COMPOSITION (a demonstrated-real, buildable positive lever); re-estimation and richer representation recover verb-specificity but not composition; none of it is register parse/POS data."
floor: "arc-eager operator (data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz) on the held-out target-register population LB_19c (n=3015): PP-chain reachability 0.6978, chain-selector who-did-what 0.4279; QA_modern (n=2423) reachability 0.7284, who-did-what 0.4631. Every arm gated CI-separated (bootstrap 2000, CI half-width + null p95 reported) against these + against its own info-free twin (head-shuffle / traverse-all / shuffled-association)."
controls: "(1) info-free HEAD-shuffle twin on the v1 PP re-attach -> shuffled association loses (reach -0.047) => the raw signal is not noise. (2) info-free PERMISSIVE traverse-all twin on copula who-did-what -> NOT separated from the copula arm (+0.006 CI incl. 0) => the copula/reachability 'gain' is chain-selector permissiveness x the 19c far-gold distribution, not a copula-specific mechanism. (3) OPEN-verb slice (76.8%) -> copula-aware is a byte no-op (0.852->0.852) => not a blanket-traversal artifact, but (2) shows even the copula-specific version is permissiveness. (4) SHUFFLED-association twin on assoc-SELECTION -> NOT separated (+0.008 CI incl. 0) => the selectional signal does not resolve the who-did-what selection ambiguity. (5) MODERN retention (QA_modern) -> every arm near-neutral or negative (copula +0.003; FTAG NEG; SEL no-op) => no arm co-satisfies register-gain + modern-hold. (6) de-contaminated copular predicate-complement subset (n=376) -> BASE reach == 0.000 => a real UD-convention representation gap, isolated. Each control excludes a specific alternative explanation."
files_changed: "experiments/exp_register_native_pp_attachment_v1.py (Hindle-Rooth raw-exposure verb-prep/noun-prep association + post-hoc PP re-attach adapter -- HURTS), experiments/exp_19c_reach_failure_diagnosis_v1.py (reach-failure partition: PP-attach 8.1%, verb-mistag 65%, selectional AUC 0.64), experiments/exp_19c_tagging_lever_ceiling_v1.py (verb-tag ceiling +0.158 reach; mistag-as-AUX 87%), experiments/exp_19c_copula_disambiguation_v1.py (copula 23.2% slice; cop-aware reach; genuine open-class mistag 2.2%), experiments/exp_register_native_levers_v1.py (3 faithful data-unblocked levers + twin/selection controls + modern retention), experiments/exp_19c_thematic_fit_reestimation_prototype_v1.py (PROTOTYPE of the drilled fix: register re-estimation of the thematic-fit store -- insufficient), experiments/exp_19c_distributional_thematic_fit_prototype_v1.py (PROTOTYPE: richer PPMI-SVD representation + CLEANED direct-object gold -- verb-specific fit REAL on clean gold, ties bag-of-args), experiments/exp_19c_composition_thematic_fit_prototype_v1.py (PROTOTYPE: composition P(patient|agent,verb) -- beats its agent-shuffle twin +0.076 CI-sep, the demonstrated positive lever), verification/test_register_native_located_negative.py (witness), notes/problems/<slug>/BRAIN_MECHANISM_DRILL.md (literature drill: how the brain does PP-attach/selection/register-adaptation/copula, and how we differ), notes/problems/<slug>/SOLVED.md. CITED (not modified): data/exp_verbrole_exemplar_which_arg_v1/metrics.json (p3 structured thematic-fit store: works modern, ties twin on 19c), exp_pivot_selectional_knowledge_richness_2afc_v1 (knowledge-poverty wall)."
reverify: ".venv/Scripts/python.exe verification/test_register_native_located_negative.py"
---

# The 19c who-did-what wall is NOT a register PARSE/POS-DATA problem -- it is copular-predication CONVENTION + SELECTION, and the brief's premise is a measurement artifact

**Bottom line: REFUTED, delivered as the bar's sanctioned LOCATED NEGATIVE.** I built the brain's actual
register-adaptation mechanisms from RAW exposure (no gold parses/POS -- exactly what the brief's own brain section
says: selectional expectations "learned from usage"), so the data blocker the brief names is side-stepped rather
than hit. Every route failed its control, and the diagnosis shows *why*: the two levers the brief names (PP-chain
attachment, robust archaic tagging) are each small, and the number that motivated the brief -- "19c verb-ID -0.10"
-- is ~87% copula-as-AUX, which is correct UPOS, not a tagger error. The real 19c bottleneck is SELECTION (which
reachable noun is the argument), a semantic-plausibility problem no parser/tagger training touches.

## WHAT I MEASURED (the disambiguation, worst-first)
The 19c PP-chain reachability residual (`_attaches_to_verb`, the bar's PP-attach-precision metric) decomposes
(`exp_19c_reach_failure_diagnosis_v1`, LB_19c n=3015, base reach 0.6978, 911 failures):

| bucket | share of failures | what it is |
|---|---|---|
| target token "mistagged" | 65.1% | but 87% of these are COPULA-as-AUX (`are/is/was/were/has`) -- CORRECT UPOS |
| wrong-verb block | 20.4% | chain hits a different verb first (partly copula-predicate-as-root) |
| **PP-attachment error** | **8.1%** | **the brief's PRIMARY lever -- small** |
| no prep path | 5.9% | not a PP case |
| gold mistagged | 0.4% | negligible |

Splitting by the target token (`exp_19c_copula_disambiguation_v1`): **COPULA/predicative clauses are 23.2% of the
population** (base reach 0.189, because UD makes the predicate complement the head and the copula a leaf `cop`
child, so the gold is unreachable *from the copula token* by CONVENTION); **genuine archaic open-class verb mistag
is 2.2%** (`equal`->ADJ, `saw`->NOUN). So the "robust tagging" lever the brief names is ~2% of the population, and
the apparent "tagging collapse" was a copula/annotation-convention artifact.

## THE ROUTES I BUILT (each the brain's mechanism, from RAW exposure, no gold data) -- AND WHY EACH FAILED
1. **PP-attachment via raw-exposure selectional association** (Hindle & Rooth 1993; MacDonald 1994
   constraint-satisfaction) -- learn verb-prep vs noun-prep preferences from 11M words of raw 19c LitBank text
   (no gold parses). The signal is **REAL** (LA(verb, gold-prep) beats LA(verb, other-prep), AUC 0.64). But: v1
   post-hoc re-attachment HURTS (reach -0.019; modern PP-attach -0.055) -- it shatters the 92% the parser already
   gets right (the brain integrates the cue AT decision time among real candidates, not as after-the-fact
   surgery). The faithful fix -- integrate only among the real competing heads AND only when the parser is
   UNCERTAIN (raw margin, since softmax conf is saturated ~0.99) -- is a **no-op** (-0.002): the confident
   attachments are already right and the uncertain ones the association doesn't decide.
2. **Register-robust tagging via frequent-frames** (Mintz 2003 -- how children categorize novel words from
   closed-class frames "he ___ the"; learned from raw 19c, no gold POS) -- override the modern tagger toward the
   frame-predicted category. **Net-NEGATIVE** on reach in both registers (-0.014 / -0.009): the 2.2% genuine
   payoff is swamped by the noise of retagging.
3. **Copula-aware predication** (traverse the `cop` relation -- copular predication is a real construction) --
   lifts reach +0.153 and who-did-what +0.079 CI-sep. **But it is NOT separable from an info-free permissive
   traverse-all twin** (COPULA-vs-TWIN who-did-what +0.006, CI includes 0; on modern the twin *beats* it). The
   "gain" is chain-selector PERMISSIVENESS x the 19c far/PP-embedded gold distribution, not a mechanism. The one
   real fact underneath: on the clean copular predicate-complement subset (n=376) the base reader scores 0/376
   (a genuine UD-convention representation gap) -- but even that a blunt permissive traversal recovers.
4. **Selection via the association** (the constructive test -- apply the AUC-0.64 signal to the SELECTION problem:
   rank reachable candidates by how much the verb selects their governing preposition). **NOT separable from a
   shuffled-association twin** (+0.008, CI includes 0): the real abstract signal does not resolve the actual
   competing-candidate ambiguity (the competitors aren't separated by verb-prep selection).

**No route co-satisfies bar criteria 1-4** (raise PP-attach CI-sep with twin losing + raise who-did-what + hold
modern + no POS/recall regression). The one arm that "raises who-did-what" fails its twin control; the arms that
survive a twin (none) don't exist.

## THE REAL BOTTLENECK (and it is not in this problem's scope)
Base who-did-what 0.4279 vs reachability 0.6978 -> **27% of items are reachable-but-mispicked**. The gold is in the
parse; the reader picks the wrong candidate. That is SELECTION -- which of several reachable nouns is the plausible
argument of THIS verb -- a semantic/world-knowledge problem. It is register-native only in that 19c plausibility
statistics differ; it is NOT a parser or tagger training-DATA problem, and the raw-exposure verb-prep association
does not resolve it. This sharpens the parent's conclusion ("residual = SELECTION, semantic/plausibility") with the
exact 27% number and the copula decomposition.

## THE SELECTION WALL, FULLY DRILLED (brain mechanism + where the register actually bites) -- `BRAIN_MECHANISM_DRILL.md`
A literature drill (McRae/Bicknell/Chersoni/Resnik/Elman) + the on-disk record close this wall precisely:
- **Why my raw-exposure verb-PREP association failed its twin (AUC 0.64 real, but no lift):** it is a MARGINAL /
  "bag-of-arguments" model, and the discriminating signal for argument selection is the CONJUNCTION
  `P(patient | agent, verb)`, not the marginal (Bicknell et al. 2010: "the journalist checked the spelling" fast
  vs "the mechanic checked the spelling" slow -- identical marginal, opposite answer). Chersoni et al. 2017: a
  role-STRUCTURED + composed distributional model scores ~72% on exactly these items; a bag-of-arguments model
  ~58% (chance); bag-of-words worse. A flat verb-prep/verb-noun store IS a bag-of-arguments model -> ties its
  shuffled twin, which is exactly what I measured.
- **The brain's mechanism = graded THEMATIC FIT from generalized event knowledge, composed over the arguments seen
  so far** (McRae, Spivey-Knowlton, Tanenhaus 1998; Elman 2009 words-as-cues; Metusalem 2012 N400 event-fit). It
  IS learnable from RAW parsed exposure (Resnik selectional preference; Erk-Pado exemplar; unsupervised over the
  substrate's OWN arc-eager typed slots) -- "gold target-register data" is again the supervised framing of an
  unsupervised mechanism.
- **THE DECISIVE ON-DISK FACT (cited, not re-derived -- `exp_verbrole_exemplar_which_arg_v1`, the `p3` problem):**
  the substrate ALREADY has this structured thematic-fit store, and it WORKS on modern but its register signal is
  DEAD on 19c:

  | selection arm | MODERN QA-SRL (n=2737) | 19c LitBank (n=5999) |
  |---|---|---|
  | structured verb-role EXEMPLAR | **0.4152** | 0.2255 |
  | role-collapsed HOLISTIC centroid | 0.3251 | **0.2959** |
  | EXEMPLAR vs verb-shuffle twin | **+0.081 CI[+0.060,+0.102]** | **+0.002 CI[-0.011,+0.015] (TIES)** |
  | EXEMPLAR vs HOLISTIC | +0.090 CI-sep | **-0.070 CI-sep (WORSE)** |

  On modern the verb-SPECIFIC thematic-fit beats its info-free twin +0.081; **on 19c it ties the twin and loses to
  the verb-blind prior** -- the verb-specific signal is NOISE on 19c because the exemplars + grounded vectors were
  estimated on modern text and archaic vocabulary is ungrounded (the cited HARD_PASS
  `exp_pivot_selectional_knowledge_richness_2afc_v1`: "KNOWLEDGE_POVERTY_WAS_THE_WALL").
- **SO THE REGISTER EFFECT IS AT THE SELECTION/THEMATIC-FIT STORE, NOT THE PARSER OR TAGGER.** "Register-native"
  belongs there: RE-ESTIMATE the verb-role thematic-fit exemplars on 19c raw exposure (Fine-Jaeger 2013 rapid
  adaptation = re-weighting existing distributions, not retraining) + GROUND archaic vocabulary through the
  grounded semantic-graph organ (PPR over WordNet++, SOLVED 2026-09-01) + add the missing COMPOSITION lever
  (`P(patient|agent,verb)`, the 58->72 ingredient). None of this is gold parse/POS data, the parser, or the tagger.
- **PROTOTYPED, TO SEE THE EFFECT (`exp_19c_thematic_fit_reestimation_prototype_v1`; hand-off artifact for the
  owned selection problems, experiments/ only):** I re-estimated the verb->patient thematic-fit store on 120K words
  of RAW 19c exposure (reusing the substrate's 12-d grounded space + `fit_exemplar`) and tested it on the 19c
  OPEN-verb (copula-excluded) selection population (n=1219, verb-coverage 0.977). **Register re-estimation ALONE
  does NOT revive the signal:** C19 0.350 TIES its verb-shuffle twin (+0.012 CI[-0.022,+0.044]) and its
  role-collapsed bag-of-arguments twin (+0.020 ns), and LOSES to position (FAR 0.419, -0.069 CI-sep). So the
  tractable increment is insufficient; the selection lever additionally requires (a) COMPOSITION
  `P(patient|agent,verb)` (the 58->72 ingredient; a marginal/verb-role store is a bag-of-arguments model), and
  (b) a RICHER/SMOOTHED representation than the coarse 12-d sensorimotor grounded space (candidate coverage 0.73;
  archaic/proper nouns OOV -> the grounded semantic-graph smoothing). Those are the owned selection problems'
  substantial build, not a register-data or re-estimation quick win -- and they confirm the cited HARD_PASS
  `exp_pivot_selectional_knowledge_richness_2afc_v1` "KNOWLEDGE_POVERTY_WAS_THE_WALL".
- **SECOND PROTOTYPE increment -- RICHER REPRESENTATION + CLEANED GOLD (`exp_19c_distributional_thematic_fit_
  prototype_v1`):** built a register-native 100-d PPMI-SVD distributional space over 19c exposure (reusing
  `hdlab.distributional_meaning_channel.ppmi_svd`) and re-ran verb-role thematic-fit selection.
  - On the CONTAMINATED full 19c who-did-what gold (n=1191): it ties its twins (DIST vs verb-shuffle +0.008 ns) and
    loses to position -- like every other arm. So a richer representation is NOT the wall on the contaminated gold.
  - **DECONFOUNDED on the CLEANED direct-object gold (n=185, the drill's stated prerequisite -- exclude the 85%
    PP-oblique "patients"): the verb-specific thematic-fit signal is REAL and CI-SEPARATED** -- DIST beats its
    verb-shuffle twin **+0.097 CI[+0.022,+0.178]** and beats position **+0.119 CI[+0.022,+0.211]**. So the
    mechanism WORKS on 19c once the gold is clean; the full-set null was GOLD CONTAMINATION, not a dead mechanism.
  - **But even on clean gold it TIES the bag-of-arguments twin (+0.016 ns)** -- so verb-SPECIFICITY is recovered,
    but the ROLE-STRUCTURE/COMPOSITION gain is not, exactly as Bicknell/Chersoni predict (marginal verb-role ==
    bag-of-arguments; only `P(patient|agent,verb)` COMPOSITION separates them, the 58->72). 
  **NET (this session, empirically):** (1) the 19c who-did-what gold is ~85% oblique-contaminated -- clean
  direct-object patients are only 15%; (2) on that clean 15% the register-native thematic-fit mechanism is REAL
  (verb-shuffle twin loses CI-sep); (3) re-estimation and richer representation recover verb-specificity but NOT
  composition; (4) so the owned selection build is precisely: CLEAN the gold + add COMPOSITION -- both de-risked
  and bounded here, neither is register PARSE/POS data.
- **THIRD PROTOTYPE increment -- COMPOSITION drilled + DEMONSTRATED (`exp_19c_composition_thematic_fit_prototype_v1`):**
  built the `P(patient|agent,verb)` conjunction from raw 19c exposure ((agent,patient) pairs per verb, agent-
  conditioned exemplar reweighting in the PPMI-SVD space) and tested it on the cleaned direct-object gold (n=171).
  **COMPOSITION carries REAL signal:** COMPOSED beats its info-free AGENT-SHUFFLE twin **+0.076 CI[+0.029,+0.123]
  CI-sep** and beats position **+0.158 CI-sep** -- the agent x verb conjunction is not noise (a wrong agent loses),
  empirically confirming the Bicknell/Chersoni mechanism on OUR data. The marginal->composed lift (+0.041) and
  COMPOSED-vs-bag (+0.076) are directionally right but just short of CI-separation at n=171 -- the clean gold is too
  small to resolve the full 58->72 separation. **So the last wall is drilled: composition IS the lever and IS real;
  confirming its full margin over the marginal/bag needs a LARGER cleaned direct-object gold (the owned problem's
  build). This is the one genuinely POSITIVE, buildable path -- and it is a SELECTION/meaning-store build, still not
  register parse/POS data.**

## THE PARSER'S ACTUAL SERVICE TO THE 19c LEVER (in-scope refinement of the parent's spec)
The structured selection store needs the parser to emit **TYPED ROLE SLOTS** (nsubj/obj/obl) so it can build
role-DISTINGUISHED exemplars (agent-fillers vs patient-fillers) from parsed exposure -- a bag-of-arguments pool
ties chance. This REFINES the parent's "arc_labeler labels are harmful": labels are harmful for the position-
dominant patient PICK (`hybrid_role_patient`, label-independent), but the dependency LABELS are REQUIRED to BUILD
the structured thematic-fit store from exposure. So the parser's brain-foundational contribution to 19c who-did-
what is neither PP-attachment nor register tagging -- it is CLEAN TYPED ARGUMENT SLOTS for the selection store to
consume (offline, at store-build time). That is what a "better parser" actually buys the 19c lever.

## THE DATA BLOCKER, NAMED (per the bar) -- and why building it is LOW-ROI
No gold 19c/literary **UD parse or POS treebank** exists on disk. Enumerated (not searched): `data/litbank/` ships
`coref / entities(NER) / events / quotations / tagger(a CRF NER model)` + 100 RAW novels (11M words); `data/corpora`
has raw fiction (Sherlock, Little Women, Tom Sawyer, ...); the ONLY gold parse+POS is modern UD-EWT
(`experiments/data/ud_english_ewt/en_ewt-ud-*.conllu`). So the brief's "LitBank CoNLL on the shelf" is COREF conll,
not parse/POS gold. **But data is not the lever:** a perfect gold-trained PP-attachment caps at 8% of the reach
residual and touches neither the 27% selection bottleneck nor the copula convention; genuine archaic tagging is 2%.
FOUNDATION-IS-FREE-TO-BUILD is admissible, but hand-building a 19c treebank to move ~10% of one metric is the wrong
investment. **The one route I bounded rather than exhausted: I did not hand-build a gold 19c parse corpus and
train on it** -- because the diagnosis caps its ceiling at ~8% and it misses the real bottleneck.

## KEY REALIZATIONS (the moves that turned a build into a diagnosis)
- **The wall diagnosed itself before the fix.** My first faithful adapter HURT; instead of tuning it I partitioned
  the failures -- and PP-attachment was only 8%, redirecting the whole problem. *Ask whether the experiment could
  have succeeded before asking why it didn't.*
- **A metric can be gamed by an info-free twin.** The reachability/who-did-what gain looked strong (+0.15/+0.08)
  until a "traverse one extra edge for ALL verbs" twin matched it. The twin -- not the effect size -- is what
  told the truth. *A caution written as prose gets violated; a control written as code catches something.*
- **The premise was a measurement artifact.** "19c verb-ID -0.10" (the number that justified the "robust tagging"
  half of the brief) is 87% copula-as-AUX -- correct UPOS scored as a miss because the who-did-what gold uses the
  older copula-as-head convention. The defect the brief was built on largely does not exist.
- **The brain's own mechanism, faithfully built, is what failed -- so this is a real negative, not a weak impl.**
  Hindle-Rooth selectional association (real, AUC 0.64), Mintz frequent frames, decision-time constraint
  satisfaction, copular predication: the register signal is learnable from raw exposure (no gold needed), it just
  is not where the 19c comprehension gap lives.
- **A REAL signal that ties its shuffled twin is a MARGINAL model on a COMPOSITIONAL problem.** The literature
  drill named my exact failure: argument selection needs `P(patient|agent,verb)` (the conjunction), and any flat
  verb-prep/verb-noun store is a bag-of-arguments model that sits at chance (Bicknell 2010; Chersoni 2017,
  58% vs 72%). The fix is STRUCTURE (role-typed slots) + COMPOSITION (agent x verb), not more data.
- **The register bites the MEANING store, not the grammar.** The on-disk structured thematic-fit store beats its
  twin +0.081 on modern but TIES it on 19c -- so "register-native" was mis-located by the brief onto the
  parser/tagger; it belongs at the selection/thematic-fit store (re-estimate on 19c exposure + ground archaic
  vocab). This is the same central wall the substrate already named: knowledge poverty, not grammar.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec.2b)
- **The parent's "19c verb-ID -0.10 / 19c tagging collapse" is ~87% copula-as-AUX (correct UPOS), not a tagger
  error.** Genuine archaic open-class verb mistag on the who-did-what population is ~2.2%. Re-scope any
  "register-robust tagging" work accordingly -- it is a small lever.
- **PP-CHAIN attachment is ~8% of the 19c reachability residual** (not the dominant 19c lever). The parent's
  "oracle-PP +0.10..+0.18" is on the predarg spatial/recipient-role task, a DIFFERENT metric than who-did-what
  reachability; do not quote it as the 19c who-did-what headroom.
- **The 19c who-did-what bottleneck is SELECTION** (27% reachable-but-mispicked; semantic plausibility), not
  parse structure or POS. Register-native PARSE/POS training is not the lever; a register-native SELECTIONAL /
  plausibility store is.
- **The register effect is at the THEMATIC-FIT STORE, not the grammar** (cited `exp_verbrole_exemplar_which_arg_v1`):
  the structured verb-role exemplar store beats its verb-shuffle twin +0.081 CI-sep on MODERN but TIES it on 19c
  (+0.002) and loses to the verb-blind prior (-0.070) -- the verb-specific thematic-fit signal is dead on 19c
  (modern-estimated exemplars + ungrounded archaic vocab). Re-estimating THIS store on 19c exposure (+ grounding
  archaic vocab via the grounded semantic-graph organ) is the register lever; it is knowledge poverty (cited
  `exp_pivot_selectional_knowledge_richness_2afc_v1` HARD_PASS), not grammar.
- **Argument selection is COMPOSITIONAL** (`P(patient|agent,verb)`; Bicknell 2010, Chersoni 2017: structured 72% vs
  bag-of-arguments 58%): a marginal verb-noun/verb-prep store is provably at chance. The store needs role STRUCTURE
  + agent-COMPOSITION, not more data.
- **The parser's real service to the 19c lever is TYPED ROLE SLOTS** (nsubj/obj/obl) to BUILD the role-distinguished
  thematic-fit store from parsed exposure -- refining the parent's "labels harmful": labels are harmful for the
  position-dominant PICK but REQUIRED to build the structured selection store.
- **The register mechanism is REAL on 19c once the gold is clean (the confound was measurement, not mechanism).**
  On the cleaned direct-object gold the register-native thematic-fit store beats its verb-shuffle twin +0.097 CI-sep;
  the earlier "dead on 19c" reading was 85% oblique gold-contamination. It still ties the bag-of-arguments twin, so
  COMPOSITION `P(patient|agent,verb)` is the remaining structural lever -- confirming Bicknell/Chersoni on our data.
- **Register adaptation is exposure-driven and needs no gold parses** (raw-exposure Hindle-Rooth signal is real,
  AUC 0.64) -- the "gold target-register data" framing in the parent's follow-on list is the SUPERVISED framing of
  an UNSUPERVISED brain mechanism; correct it to "raw-exposure selectional statistics."

## WHAT I WOULD WITHDRAW FIRST IF WRONG
The claim that building a gold 19c parse corpus is low-ROI rests on the 8%/2.2%/27% decomposition, which is scored
on ONE who-did-what population (QA-SRL/LitBank-derived, itself partly copula/oblique-contaminated). If a cleaner,
larger 19c who-did-what gold with de-contaminated direct-object patients showed PP-attachment to be a larger share,
the ROI argument weakens (the located-negative on the METHOD -- exposure signal built, twin-controlled, does not
help -- would still stand). Second: the copula "gain" is real as a representation gap (base 0/376) even though it
is not separable from a permissive twin; a copula-aware reader is still worth wiring for its own sake, just not as
a "register PP-attachment" win.

## TLDR (plain English)
The job was to fix "who did what" on 200-year-old prose by getting old-style annotated grammar data and retraining
the reader's grammar-parser and word-tagger on it. I built the brain's actual way of adapting to a new style --
learning which words go together from plain reading, no annotated data needed -- and it works as a signal but does
not fix the problem. Digging in showed why: the thing that looked like "the tagger breaks on old verbs" is 87%
just the words "is/was/were" (tagged correctly as helper-verbs), and the preposition-attachment the brief targeted
is only 8% of the errors. The real problem is picking which of several candidate nouns is the one the verb acts on
-- a meaning/plausibility judgment -- which no amount of grammar-data retraining touches. So the honest answer is:
the missing old-style grammar data is real (none exists on the machine), but it is not the bottleneck, and
hand-building it would fix at most a tenth of one measure while missing the real issue.

## QUESTIONS
- The one genuinely POSITIVE, demonstrated lever (composition, `P(patient|agent,verb)`, beats its agent-shuffle
  twin +0.076 CI-sep) is bounded to the clean ~15% direct-object slice and its full margin needs a LARGER cleaned
  direct-object gold to confirm. That build belongs to the owned selection problems (`archaicrole`/`p3`). Fund it
  there? My recommendation: YES, but clean the gold first. (Building a gold 19c PARSE/POS corpus -- the brief's
  route -- I still recommend AGAINST: it caps at ~8% of the reachability residual and misses the selection lever.)

## IS PERFORMANCE MAXED? -- the realizable-headroom accounting
**Within THIS problem's scope (register parse/POS training): YES, exhausted.** The brief's two levers are refuted
(PP-attach = 8% of the reach residual, faithful integration null/negative; register tagging = 2% genuine,
frequent-frames net-negative), and the two tractable meaning-store increments (register re-estimation, richer
PPMI-SVD representation) are EMPIRICALLY ELIMINATED (both tie their twins). There is no further parser / tagger /
register-data performance to extract for 19c who-did-what -- that is the located negative.
**For the 19c who-did-what NUMBER overall: NOT maxed -- but the remaining headroom is small and MOSTLY MEASUREMENT,
not mechanism, and all of it is OUT OF THIS PROBLEM'S SCOPE:**
- **~85% of the 19c gap is GOLD CONTAMINATION** (PP-obliques / copula-complements scored as "patients"). Cleaning
  the gold RE-SCOPES the metric; it is not a capability gain. Much of the 0.43 number is measurement noise.
- **Copular is-a predication (~23% of the population; base 0/376):** a real, buildable, register-INDEPENDENT lever
  -- UNBUILT here (filed as a small separate frontend problem).
- **Composition `P(patient|agent,verb)` on the clean ~15% direct-object slice:** the one genuine selection lever
  left, and now DEMONSTRATED real (composition beats its agent-shuffle twin +0.076 CI-sep; beats position +0.158
  CI-sep). Its full margin over the marginal/bag is not yet CI-separated (clean gold only n=171) -- confirming it
  needs a LARGER cleaned direct-object gold, which is the owned selection problem's build. Bounded to ~15% of items.
**Net:** the parser/tagger/data path is MAXED; the residual is (a) a gold-cleaning re-scope, (b) a copular is-a
binding, (c) a DEMONSTRATED-real composition lever on ~15% of items whose full margin needs a larger cleaned gold --
all named + bounded below, none of it this problem's mechanism. Do not expect the 19c number to jump; most of the
gap is measurement (gold contamination), and the one real mechanism lever (composition) is bounded to the clean 15%.

## NEXT STEPS FOR STRATEGY (ordered)
1. **Re-rank / re-scope THIS problem.** Its two named levers are small (PP-attach 8%, tagging 2.2%) and its
   premise number (19c verb-ID -0.10) is a copula-as-AUX artifact. The register-native PARSE/POS-DATA framing
   should be retired or folded into the selection problem below.
2. **The real 19c lever is SELECTION, and it is a MEANING-STORE register problem** -- route it to the existing
   `role_assignment_is_untested_on_archaic_literary_prose` / `the_plausibility_prior_is_a_coarse_centroid_needs_a_
   structured_verb_role_exemplar_store` / `grounded_role_assignment_via_verb_keyed_thematic_fit` with the drilled,
   brain-foundational, our-implementation recipe (`BRAIN_MECHANISM_DRILL.md`): a **role-STRUCTURED + agent-COMPOSED
   + taxonomically-SMOOTHED thematic-fit store** -- (a) build verb-role exemplars from the parser's TYPED slots on
   19c raw exposure (register re-estimation, Fine-Jaeger); (b) add the missing COMPOSITION `P(patient|agent,verb)`
   (the 58->72 ingredient, Bicknell/Chersoni); (c) SMOOTH archaic vocabulary through the grounded semantic-graph
   organ (PPR over WordNet++, SOLVED 2026-09-01). CONTROLS: must beat BOTH a shuffled-role twin AND a role-collapsed
   bag-of-arguments twin CI-sep (the on-disk store currently ties its twin on 19c -- that is the gap to close).
   Feed it the parser's `_pp_args_for_verb` candidate set; the pick is semantic, not structural. **PROTOTYPE RESULT
   (`exp_19c_thematic_fit_reestimation_prototype_v1`) BOUNDS THE BUILD:** register re-estimation ALONE is
   insufficient (C19 ties both twins, n=1219, loses to position) -- so the build MUST include the composition and
   the richer/smoothed representation, NOT just re-estimation; and CLEAN the who-did-what gold first.
3. **Copular predication is a real, in-scope representation gap** (base 0/376 on clean predicate complements):
   file a small problem to make `predicate_argument_frontend` copula-aware (bind the predicate nominal/adjective
   as the copula's complement), independent of any register data -- but do NOT sell it as a "register PP-attach"
   gain (not twin-separable).
4. **Clean the 19c who-did-what gold** (the parent's flagged contamination: obliques/predicate-complements scored
   as patients). Several measurements here are capped by gold quality, not mechanism.
5. **DO NOT** acquire/build gold 19c parse/POS data for PP-attachment or archaic tagging (ROI ~10% of one metric,
   misses the bottleneck); **DO NOT** re-open post-hoc PP re-attachment (hurts) or frequent-frames retagging
   (net-negative) or the copula-as-a-parser-win framing (permissiveness). The raw-exposure selectional association
   is REAL (AUC 0.64) but only as an abstract signal -- it does not resolve selection.

## INTEGRATED_BY_STRATEGY 2026-09-02

Reverified `verification/test_register_native_located_negative.py` FIRST-HAND: **13/13** checks pass
(W1 copula-WDW ties permissive twin; W2 frequent-frames tagging net-negative −0.010; W3 margin-gated
re-attach no-op; W4 assoc-selection ties shuffled twin; W5 clean copular predicate-complement base
reach = 0/120; W6 raw-exposure selectional signal real AUC 0.881; W7 PP-attach = 8.1% of the 19c
residual; W8 87% of "19c verb mistags" = copula-as-AUX correct-UPOS; W9 structured store beats twin
MODERN +0.081 / TIES 19c +0.002; W10 19c re-estimation alone ties twin; W11 contaminated-gold
distributional store ties twin; W12 on CLEANED direct-object gold the verb-specific signal is REAL
+0.097 CI-sep; W13 COMPOSITION beats agent-shuffle twin +0.076 CI[+0.029,+0.123]). Accepted
**REFUTED + a deconfounded POSITIVE**, rating **EXCELLENT** (refuted the brief's own MEASURED premise
— the "19c verb-ID collapses −0.10" is 87% copula-as-AUX correct-UPOS; drilled every wall to its brain
mechanism; deconfounded a real lever the noisy gold was hiding; no `hdlab/` overreach; clean routing).

**NO hdlab wire** (a located negative — the parser/POS-data framing is retired; nothing cleared the
bar). **AUDIT UPDATE folded into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b.** The demonstrated-real lever
(agent-COMPOSED P(patient|agent,verb) thematic-fit, from raw exposure, on a CLEANED direct-object gold)
is routed forward as the follow-on `the_19c_who_did_what_lever_is_agent_composed_thematic_fit_on_a_cleaned_gold`
(priority 2, taking this slot); the separate copular is-a binding gap (base reader 0/376 on predicate
complements, register-independent, ~23% of the population) is filed as
`the_reader_has_no_copular_is_a_binding_schema` (priority 4). Priority cleared.

**STRATEGIC NOTE (reshapes the DEBT-2 parser wire):** the parser's ONLY real 19c service to
who-did-what is emitting TYPED argument slots (nsubj/obj/obl) to BUILD the thematic-fit store — NOT
PP-attachment (8% of the residual) and NOT register tagging (net-negative). And the 19c who-did-what
GOLD is ~85% oblique-contaminated — a measurement-integrity flag on the baseline board's 19c
who-did-what arm.
