# BRAIN-MECHANISM DRILL — the graded metric + the FHRR Sentence-Gestalt

Read-only literature drill. Date: 2026-09-02. Method: web lit-scan (generic terms), lit-scan
calibration penalty applied (P-estimates deflated; no novel-synthesis P above 0.50).

Anchoring measurement (on-disk, given): exact-patient MRR from agent+verb is near its intrinsic
ceiling — median ~164 effectively-distinct patients per verb in a 300-pool; empirical
count-conditional P(patient|agent,verb) tops out at 0.165 MRR; vector predictor 0.145 already
within 0.02 of that count ceiling. Signal concentrates on high-selectivity verbs. **Exact-match is
saturated; richness has little room THERE.** The two questions below ask (Q1) whether exact-match is
even the right competence, and (Q2) whether a glass-box FHRR Sentence-Gestalt adds signal.

---

## Q1 — THE RIGHT METRIC. Exact-next-word is the WRONG competence; graded thematic-fit IS the brain's.

### Q1a — the brain pre-activates a GRADED distribution, not a unique word. CONFIRMED.

- **Altmann & Kamide (1999)**, visual-world eye-tracking: on hearing a verb (`eat`), listeners
  launch anticipatory saccades to ALL edible objects in the scene, weighted by selectional fit —
  i.e., the verb pre-activates a *set/distribution* of thematically-compatible fillers, not one word.
  The verb restricts the theme space; it does not name the theme.
- **Kutas & Federmeier / Federmeier (2007)** — the N400 is a GRADED index of semantic
  pre-activation. An unexpected-but-plausible word that shares semantic features with the predicted
  continuation shows an ATTENUATED N400 (Federmeier & Kutas 1999; Federmeier et al. 2002): the
  facilitation is a function of *degree* of semantic overlap with the pre-activated distribution, not
  an all-or-none match to one word. "Multiple plausible continuations" are pre-activated in parallel.
- **Metusalem et al. (2012)** — the graded story is EVENT-level, not just word-associate-level. N400
  is smallest for the expected word, LARGEST for an event-UNRELATED implausible word, and
  INTERMEDIATE for an event-RELATED implausible word. The comprehender pre-activates a whole event
  schema; relatedness-to-the-event grades the response. This is the strongest evidence that the brain's
  competence is *graded plausibility over an event model*, not next-word identity.

**Verdict Q1a:** exact-next-word prediction is the WRONG competence to grade a comprehension
substrate on. The brain's measurable competence is a graded pre-activation over thematically/event-
compatible fillers. Our saturated 0.145 MRR is measuring the wrong thing — the ~164-patient fan-out
IS the graded distribution, not noise to be beaten down. (Confidence: HIGH — three independent
paradigms, decades-stable.)

### Q1b — the standard eval + the frequency-controlled 2AFC. CONFIRMED + citation for the freq fix.

**The accepted metric for thematic-fit models is Spearman rank-correlation between model scores and
averaged HUMAN plausibility ratings** on verb–role–filler triples. Standard datasets:
- **McRae et al. (1998)** — agent & patient plausibility ratings (1–7 scale).
- **Padó (2007)** — agent & patient.
- **Ferretti et al. (2001)** — instruments & locations.
- **Vassallo, Chersoni, Santus, Lenci, Blache — DTFit (2018)** — 395 transitive-event sentence
  PAIRS differing only in the patient's typicality; typicality depends on the *whole* <agent,verb,
  patient> triple, not <verb,patient> alone (e.g. "the actor won the AWARD" vs "…the BATTLE";
  "the tailor sewed the DRESS" vs "…the WOUND").

**The typical-vs-atypical 2AFC is the accepted discrimination proxy for the human-norm correlation.**
DTFit / "Did the Cat Drink the Coffee?" (Chersoni et al., *SEM 2021) report BOTH on the SAME items:
(1) Spearman-with-human-ratings, and (2) **binary pairwise accuracy = fraction of pairs where the
model assigns the HIGHER thematic-fit score to the typical patient.** The two track together (SDM:
rho ≈ 0.58–0.65, accuracy ≈ 0.89–0.91; BERT-large: rho ≈ 0.50–0.71, acc ≈ 0.83–0.89) — so the
2AFC IS a validated stand-in when you don't have a full human-rated scale, and it is the exact shape
of the USER's proposed test.

**The pseudo-disambiguation task** is the older/classic 2AFC for selectional preference (Rooth et
al. 1999; Erk 2007; Padó, Padó & Erk 2007; Van de Cruys 2014): score the attested (S,V,O) above a
corrupted (S,V,O′) with a foil object O′.

**FREQUENCY CONTROL — the load-bearing citation the USER needs: Chambers & Jurafsky (2010),
"Improving the Use of Pseudo-Words for Evaluating Selectional Preferences."** Their point is exactly
the confound the USER wants to remove: a *randomly* chosen foil is a trivially-winnable frequency
contrast (a model can prefer the true word by raw frequency, learning nothing semantic). **Their fix
(quote): "For each target word, we randomly selected a foil from among the candidate words that
appeared in the same frequency bin as the target word."** Frequency-binned foil selection makes the
2AFC a valid test of *semantic* compatibility. NOTE: DTFit itself does **not** frequency-match its
foils — so the USER's frequency-controlled 2AFC is a genuine methodological improvement over DTFit,
grounded in Chambers & Jurafsky 2010.

**Verdict Q1b:** YES — frequency-controlled 2AFC (true patient vs frequency-matched, verb-plausible-
but-context-atypical foil) is the accepted proxy for human thematic-fit norms. Cite DTFit
(Vassallo/Chersoni 2018) + Chersoni *SEM 2021 for the typical/atypical 2AFC; Chambers & Jurafsky
2010 for the frequency-binned foil. (Confidence: HIGH.)

### Q1c — does representational RICHNESS earn its keep on the graded metric (that exact-match hides)?

**YES on the graded metric — but the lever is a richer STORE / event-knowledge structure, NOT a
fancier model.** Two findings, held in tension:

- **Structured Distributional Model (SDM; Chersoni, Santus, Pannitto, Lenci, Blache, Huang 2019,
  *Nat. Lang. Eng.*)** — augmenting a compositional DSM with an explicit event-knowledge graph
  (roles + typical co-participants as distributional vectors) "constantly improves performance" on
  DTFit across embedding types, matching/beating BERT-large and RoBERTa-large (rho ≈ 0.58–0.65, 2AFC
  ≈ 0.89–0.91). Structure that encodes *which participants co-occur in an event* is what pays off —
  precisely the multi-participant signal that exact-single-patient MRR cannot reward.
- **CAVEAT — Kelly, Ghaffari et al. "Where's the Learning…" (2022, arXiv:2208.04749):** on the same
  thematic-fit datasets (Padó, McRae, Ferretti, Bicknell), *random* embeddings tuned during training
  nearly match GloVe; frozen pretrained beats frozen random. Headline: "much of the learning is
  captured in the word embeddings," not the architecture. So the richness that helps is
  representational (a good distributional space / event-knowledge graph), not a deep learned net.

**Verdict Q1c:** graded plausibility IS where a richer stream earns its keep (SDM shows a
count/prototype + event-knowledge structure lifts DTFit rho and 2AFC accuracy far above chance where
exact-match saturates) — and the lever is a richer STORE (event-knowledge composition, better
distributional codebook), which the project's "offline-built FOUNDATION is admissible" charter
already blesses. Deflated read: the gain is real but modest and store-driven, not architecture-driven.
(Confidence: MEDIUM-HIGH; P(a frequency-controlled 2AFC shows a richer store beating agent+verb
alone) ≈ 0.45 — capped per lit-scan penalty; it depends on whether the richer store carries
*additional-participant* signal, see Q2c.)

---

## Q2 — THE FAITHFUL SENTENCE-GESTALT as a glass-box FHRR stream (no trained net, no LLM).

### Q2a — what the Sentence Gestalt IS, how a role's filler is READ OUT, and the faithfulness verdict.

**What it is (St. John & McClelland 1990; Rabovsky/Hansen/McClelland 2018; Venhuizen et al. 2019):**
the Sentence Gestalt is a single distributed vector — a *situation/event* representation — updated
INCREMENTALLY per word by a recurrent UPDATE network (SRN: gestalt(t) = f(word(t), gestalt(t-1))).
It is not a bag of role-bindings; it is a learned compression of "the event described so far."

**How a role's filler is read out — the PROBE / QUERY network (this is the load-bearing detail):**
readout is NOT unbinding. A separate trained QUERY network takes the gestalt + a probe (a role unit,
e.g. `patient`, OR a filler) and is trained to emit the other half of the role/filler pair. Crucially
the query net was trained to answer comprehension questions about the event — so it does
**probabilistic inference**: it can instantiate roles that were NEVER lexically given (elaborate an
implied instrument), disambiguate a vague word, and fill an unseen role from event statistics
("the pitcher threw the ___" → BALL, even though ball was never in the input). The readout's power is
in the LEARNED weights of the query net, not in retrieving stored bindings.

**Is a static FHRR superposition of (role⊗filler) bindings a faithful glass-box approximation, or a
caricature? — HONEST VERDICT: it is faithful for READBACK of ALREADY-SEEN roles, and a CARICATURE
for PREDICTING an UNSEEN role's filler (which is exactly the patient-prediction use-case).** Why:
- A static bundle `SG = Σ role_i ⊗ filler_i` is an addressable memory. Unbinding a role that WAS
  filled (`SG ⊗ agent_role⁻¹ ≈ agent_filler + noise`) faithfully recovers it — this part is a clean
  glass-box model of the "query an observed role" function.
- But to predict the PATIENT before the patient word arrives, there is **no `patient_role ⊗ patient`
  term in the bundle to unbind** — the patient hasn't been seen. `SG ⊗ patient_role⁻¹` returns NOISE.
  The trained SG produces a patient expectation via *learned event statistics* (agent×verb → likely
  patient), which the static bundle simply does not contain. To make the FHRR version predict, you
  must ADD a schema term (a precomputed `(verb,patient_role) → typical-patient prototype`), i.e. bake
  in the inference the trained net learned. That schema term is a *distributional/thematic-fit
  prototype* — the SAME thing a distributional hub already is.
- CogNeuro corroboration (LibreTexts / O'Reilly-Munakata CCN; Rabovsky 2018): the SG's signature
  behaviours — instantiate implied roles, disambiguate, graded update = N400 semantic prediction
  error — all live in the LEARNED recurrent update + query weights. A no-training static superposition
  reproduces none of them.

**Verdict Q2a:** a no-training static FHRR bundle is a FAITHFUL model of the SG's *role-addressing /
retrieval* competence and a CARICATURE of its *predictive/inferential* competence. For patient
prediction specifically, the faithful-looking unbind is vacuous — the predictive content must be
supplied as a precomputed schema/prototype (an offline FOUNDATION asset, which is admissible), at
which point it is a structured distributional model, not a dynamic gestalt. (Confidence: HIGH on the
mechanism; this is the crux.)

### Q2b — the exact FHRR ops for combining bound roles into a patient expectation.

FHRR = each dimension is a unit-magnitude complex phasor (angle ∈ (0,2π]). Ops (Plate; Schlegel/
Neubert/Protzel 2021 "A comparison of VSA"; Kleyko survey ACM CSUR 2022):

- **Atoms / codebook:** each role symbol (`AGENT_ROLE`, `VERB`, `PATIENT_ROLE`, `INSTR_ROLE`, …) and
  each filler concept = a random phasor vector, unit magnitude per component. Keep them in a codebook
  (the cleanup memory).
- **bind(a,b)** = elementwise complex multiplication = per-component PHASE ADDITION. `c = a ⊙ b`.
  (In real-valued HRR this is circular convolution; FHRR is its clean frequency-domain form with
  EXACT unbinding up to quantization noise — prefer FHRR for exactly this reason.)
- **unbind(c,a)** = bind with the INVERSE of a = elementwise multiply by complex CONJUGATE = phase
  SUBTRACTION. `b̂ = c ⊙ conj(a)`. For unit phasors the conjugate IS the exact inverse (no
  pseudo-inverse noise, unlike real HRR).
- **bundle/superpose(x1..xn)** = elementwise complex ADDITION, then project each component back to
  the unit circle (renormalize phase). This is lossy; unbind recovers a filler + a noise term whose
  variance grows with the number of superposed bindings.
- **cleanup** = nearest neighbour (max cosine) in the filler codebook.

**Compositional patient-expectation for a partial event {agent, verb, (obliques)}:**
```
SG  = normalize(  AGENT_ROLE ⊙ agent
                + VERB_ROLE  ⊙ verb          # or use verb as the event/context vector
                + INSTR_ROLE ⊙ instrument    # only if an oblique is actually present
                + ... )                      # one term PER already-seen role
pred_patient_raw = SG ⊙ conj(PATIENT_ROLE)   # unbind the patient role
scores = cos(pred_patient_raw, codebook)     # cleanup → ranked candidates
```
The 2AFC score for a candidate patient `p`: `cos(pred_patient_raw, p)` (or, symmetrically,
`cos(SG, PATIENT_ROLE ⊙ p)`), compared for typical vs frequency-matched foil.

**The catch (ties to Q2a):** in this bundle there is NO patient term, so `SG ⊙ conj(PATIENT_ROLE)`
is pure noise unless you inject a learned/precomputed schema term. The faithful predictive version is:
`SG_pred = SG + (VERB ⊙ AGENT ⊙ PATIENT_ROLE ⊙ patient_prototype[verb,agent])` — i.e. add an
offline-built event-schema prototype. Without that term, the ops above are correct but return noise
for the patient.

### Q2c — COMPLEMENTARY or REDUNDANT with the distributional hub? HONEST: redundant on single {agent,verb}.

The hub already conditions patient on {agent, verb}. What can an FHRR SG add BEYOND agent+verb?
- **On a SINGLE canonical sentence where only {agent, verb} are available: NOTHING.** The SG bundle
  contains only `AGENT_ROLE⊙agent + VERB⊙verb`; unbinding the patient role returns noise; the only
  way to get a patient expectation is a `(verb[,agent]) → patient` schema, which is *definitionally
  the same conditioning the hub performs*. The SG is REDUNDANT here. Its "situation vector" has no
  additional participants, no discourse referents, no prior-clause event schema to carry independent
  signal. (This is the honest answer the USER asked for — do not oversell.)
- **The SG earns independent signal ONLY when the input carries MORE than {agent, verb}:**
  (1) additional overt participants/obliques (instrument, location, recipient) — DTFit's variable-
  length tuples are built exactly to require this multi-argument composition;
  (2) MULTI-CLAUSE / discourse context — prior-sentence referents and an accumulated event schema
  (the Metusalem event-level pre-activation; Venhuizen 2019 discourse-updated gestalt) give the
  superposition terms the hub's single-triple conditioning never sees.

**Verdict Q2c:** on single {agent, verb} items the no-training FHRR SG is REDUNDANT with agent-
composition (both collapse to a verb[,agent]→patient prototype). It becomes potentially COMPLEMENTARY
only with ≥1 additional bound role or with cross-clause discourse. **Recommendation: do NOT build/
test the FHRR SG on single-sentence patient prediction — it cannot beat the hub there by construction.
Either (a) test it on MULTI-participant tuples (≥ agent+verb+instrument/location) and multi-clause/
discourse items where extra role-bindings and referents give it independent terms, or (b) drop the
"dynamic gestalt" framing and just build the offline event-knowledge prototype store (the SDM lever
from Q1c), which is the part that actually moves the graded metric.** (Confidence: HIGH on the
redundancy-on-single-sentences claim — it is a structural, not empirical, result.)

---

## BOTTOM LINE (the recipe)

**(1) The metric to implement — frequency-controlled graded 2AFC, and it IS an accepted human-norm proxy.**
- Build items: for each event with gold patient `p*`, pick a foil `p−` that is (a) plausible for the
  VERB alone but atypical for THIS <agent,verb> context (forces composition, per DTFit design), and
  (b) drawn from the SAME corpus-frequency bin as `p*` (Chambers & Jurafsky 2010 — removes the
  frequency confound that raw MRR-on-a-300-pool cannot).
- Score: model plausibility(agent,verb,p*) vs plausibility(agent,verb,p−) = cos(pred, cand) or the
  hub's conditional P. Report **pairwise 2AFC accuracy** (fraction p* > p−) AND, where a rated scale
  exists (McRae/Padó/DTFit), **Spearman rho** to human ratings. The 2AFC↔rho tracking in DTFit /
  Chersoni *SEM 2021 validates the 2AFC as the proxy. This metric has real headroom where exact-match
  MRR is saturated at ~0.145.
- Cite: Vassallo/Chersoni DTFit 2018; Chersoni et al. *SEM 2021 (typical/atypical 2AFC + rho);
  McRae 1998 / Padó 2007 (norms); Chambers & Jurafsky 2010 (frequency-binned foil).

**(2) Glass-box FHRR Sentence-Gestalt — faithful or caricature, the ops, and the honest verdict.**
- FAITHFUL for reading back roles that WERE filled (addressable memory); CARICATURE for predicting an
  UNSEEN patient — the trained SG's predictive power lives in learned event statistics, and a static
  bundle has no patient term to unbind (returns noise). Making it predict requires injecting a
  precomputed event-schema prototype — at which point it IS a structured distributional model, not a
  dynamic gestalt.
- Exact ops (FHRR, unit phasors): bind = elementwise complex mult (phase add); unbind = mult by
  complex conjugate (phase subtract, EXACT for unit phasors — the reason to use FHRR over real HRR);
  bundle = complex add + renormalize to unit circle; cleanup = nearest in codebook.
  `SG = normalize(Σ role_i ⊙ filler_i)`; `pred = SG ⊙ conj(PATIENT_ROLE)`; `score = cos(pred, cand)`.
- HONEST verdict on added signal: **REDUNDANT with agent-composition on single {agent,verb}
  sentences** (both reduce to a verb[,agent]→patient prototype; the SG has no extra terms). It adds
  signal ONLY with ≥1 additional overt participant (instrument/location/recipient — DTFit variable-
  length tuples) or MULTI-CLAUSE/discourse context (prior referents + accumulated event schema).
- **Directive:** if the target is single canonical sentences, do NOT build the FHRR SG — build the
  offline event-knowledge PROTOTYPE store (SDM-style, Q1c) instead; that is the store-richness lever
  that moves the graded 2AFC. Reserve the FHRR SG for multi-participant / multi-clause items, and
  test complementarity THERE.

---

## Sources
- Altmann & Kamide (1999), *Cognition* — anticipatory eye movements, verb selectional restriction.
- Federmeier (2007) / Federmeier & Kutas (1999) — graded N400 semantic pre-activation.
- Metusalem et al. (2012), *JML* — event-level graded N400 (related vs unrelated implausible).
- McRae et al. (1998); Padó (2007); Ferretti et al. (2001) — thematic-fit human-rating norms.
- Vassallo, Chersoni, Santus, Lenci, Blache (2018) — DTFit dataset (typical/atypical patient pairs).
- Chersoni et al. (2021 *SEM), "Did the Cat Drink the Coffee?" — DTFit 2AFC accuracy + rho; SDM/BERT/RoBERTa numbers. https://aclanthology.org/2021.starsem-1.1.pdf
- Chambers & Jurafsky (2010) — frequency-binned foil for pseudo-word selectional-pref eval. https://web.stanford.edu/~jurafsky/chambers-acl2010-pseudowords.pdf
- Santus, Chersoni, Lenci, Blache (2017), "Measuring Thematic Fit with Distributional Feature Overlap." https://aclanthology.org/D17-1068/
- Chersoni et al. (2019), "A Structured Distributional Model of Sentence Meaning and Processing," *Nat. Lang. Eng.* https://arxiv.org/abs/1906.07280
- Kelly, Ghaffari et al. (2022), "Where's the Learning in Representation Learning for Compositional Semantics and the Case of Thematic Fit." https://arxiv.org/abs/2208.04749
- St. John & McClelland (1990), *AI J.* — Sentence Gestalt model. https://cseweb.ucsd.edu//~gary/PAPER-SUGGESTIONS/stjohn-mclelland-aij-1990.pdf
- Rabovsky, Hansen & McClelland (2018), *Nat. Hum. Behav.* — SG semantic update = N400.
- Brouwer, Crocker, Venhuizen & Hoeks (2017), *Cognitive Science* — Retrieval-Integration N400/P600. https://onlinelibrary.wiley.com/doi/10.1111/cogs.12461
- Venhuizen et al. (2019) — SG surprisal / semantic update, discourse-updated gestalt.
- O'Reilly & Munakata, *Computational Cognitive Neuroscience* 3e, §9.6 Sentence Gestalt (probe/query net).
- Schlegel, Neubert & Protzel (2021), "A comparison of VSAs"; Kleyko et al. (2022), ACM CSUR HDC/VSA survey — FHRR ops.
