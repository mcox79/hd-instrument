---
problem: manner_encoded_harm_needs_an_intensity_read_the_verb_tables_are_silent_on_brutally_and_roughly
status: SOLVED
bar: "Recovers the manner slice (>= 8 of the 15 named verbs) at Connotation-Frames precision >= 0.95 with 0 leaks on P_NEUTRAL_BROAD and the live gold held (>= 35/36), the adverb-in-prose gold CI-separated over the current abstaining read, twin (scrambled intensity norms) losing, knowledge as an offline foundation asset + an online observe path -- OR a numbered located negative naming the missing input."
result: "MANNER-INTENSITY ARM (manner/means/result decomposition of the verb's definition, parsed OFFLINE by the reader's own glass-box stack; sign from the manner's VALENCE, magnitude from the CIRCUMPLEX RADIUS of its core affect or its GROUNDED action strength; operating point tau_intensity=0.40, tau_manner_val=0.10). Named manner verbs reading HARM 9/15 -> 15/15, i.e. ALL SIX of the floor's abstentions recovered (brutalize, manhandle, gore, subjugate, tyrannize, maltreat) with 0 flips to a wrong sign. 46 still-abstaining affecting verbs newly decided at Connotation-Frames precision 6/6 = 1.00 with ZERO wrong signs (the 4 CF-neutral-but-decided all sit at |Effect(o)| = 0.20, inside the gold's own +-0.25 neutral band). 0 leaks on P_NEUTRAL_BROAD (n=36). Whole-arm CF agreement 294/315 = 0.9333 >= floor 288/309 = 0.9320. Live 36-item modern gold 24/24 HARM/HELP held, NEUTRAL items byte-identical to the floor. NEW adverb-in-prose gold (36 declared sentences, an affect-neutral verb + a manner adverb): floor 0.4444 -> 0.6389, delta +0.1944 CI [+0.0833, +0.3056] CI-SEPARATED; the argmax-head read gets only 0.4722, so the win is the GRADED governor posterior. Controls: scrambled-intensity twin 4/6 slice and CF precision 0.875; scrambled-valence twin 2/6 with 3 WRONG HELP and precision 0.5714 over 510 reckless decisions; parse-free twin (the refuted gloss proxy through the identical valuation) 0/6 and 0.8421 over 154 decisions. The 2x2 the brief asked for: with a HIGH-arousal manner the valence sign agrees with the human gold 0.864 (negative) / 0.769 (positive); with a LOW-arousal manner 0.643 / 0.633 -- the intensity gate is what makes the sign trustworthy, and a high-arousal POSITIVE manner reads HELP, not HARM. TWO LEVERS REFUTED-AS-BUILT by the human gold and NOT shipped: promoting the manner above the diffuse word-level norm (CF 0.9333 -> 0.9111) and abstaining on manner-host verbs (0.9014, and a live-gold item)."
floor: "hdlab/force_dynamics_valence.py at HEAD (result state -> word norm -> superordinate consensus): 9/15 named manner verbs HARM and 0/6 of the manner slice (brutalize/manhandle/gore/subjugate/tyrannize/maltreat all abstain, first-hand verified); 695 affecting verbs still abstain; CF whole-arm 288/309 = 0.9320; P_NEUTRAL_BROAD 0 leaks; live 36-item gold 24/24. On the adverb-in-prose gold the floor is not merely silent -- it answers HELP on 'treated the prisoner brutally' (Warriner treat +0.46 is largely the noun 'a treat') and scores 0.4444."
controls: "(1) TWIN, SCRAMBLED INTENSITY (the brief's named control) -- arousal + grounded action strength permuted across words: slice 4/6 (vs 6/6) and CF precision on new decisions 0.875 (vs 1.00). (2) TWIN, SCRAMBLED VALENCE (the sign channel) -- slice 2/6, THREE WRONG HELP verdicts on the slice, 510 decisions at 0.5714 precision, 1 neutral leak: the sign channel is load-bearing and its loss is catastrophic, not quiet. (3) PARSE CONTROL -- the manner filler replaced by the strongest-valence word of the SAME definition (exactly the drilled, refuted parse-free gloss proxy) through the identical intensity/consensus valuation: 0/6 of the slice, 154 decisions at 0.8421. The PARSE is what makes the read work. (4) INDEPENDENT HUMAN GOLD -- Connotation Frames Effect(o) (Rashkin, Singh & Choi ACL 2016), never read at inference: new-decision precision 1.00 with 0 wrong signs, whole-arm 0.9333 >= floor 0.9320. (5) NEUTRAL PRECISION -- 0 leaks on P_NEUTRAL_BROAD; 0 of the 2x2's 437 manner-bearing verbs falls in that population. (6) NO-REGRESS -- live 36-item modern gold 24/24, harm-frame 10/10, social-harm 15/16, non-prevent-help 15/16, all unchanged; 0 of the 15 named verbs flips sign. (7) OPERATING-POINT SWEEP -- tau_intensity 0.35-0.60 x tau_manner_val 0.10-0.30 (18 points): CF precision 1.00 and 0 leaks at 14 of 18 (the four exceptions are all at tau_manner_val >= 0.20); the win is not threshold-brittle. (8) ARGMAX ABLATION on the prose gold: 0.4722 vs the graded read's 0.6389 -- names the graded posterior as the mechanism. (9) INTENSITY-CHANNEL ABLATION: circumplex / arousal / arousal+grounded all hold precision 1.00; grounded-only and valence-only lose the slice (3/6) -- the channel choice is robust, the gate is not."
second_pass: "Supervisor probe 2026-09-13: NO headline number moved. Added the full rung-by-rung signal trace with the exact cue decomposition of the governor loss (locality +0.893 of a +1.161 gap; `constr=none` on both candidates because attachment_arm has no manner-adverbial construction); the per-rung BF table for this signal (the affect lexicon is the one rung that structurally cannot hand down a graded value); the brain-math comparison; and eight mechanistically-understood negatives. Built the CONFIGURATION-CONDITIONED manner-adverbial cue for the governor: UD-EWT advmod 0.5475 -> 0.5475 (zero global cost, vs 0.4932-0.5317 unconditioned) and the target slice posterior 0.4445 -> 0.5332 (+0.0887 CI [-0.1333,+0.3143], n=15, NOT separated) -- and showed that repairing that rung is worth EXACTLY 0.0 to this consumer (prose gold identical on all 36 items), because the graded read had already extracted everything the rung had. Exercised the online observe path on held-out prose (203 observations/4000 lines -> 5 decisions at 4/5, 0 leaks, live gold held). Rejected with counts: Binder as a second gold (434/535 are thing-concepts; 2/46 covered), the POS-conflation lever (treat is 0.000 noun-dominant; removes 11 correct for 4 wrong), the adj.all/adj.pert manner filter, the unconditioned governor boost, and the derivational backoff (inert on every population)."
files_changed: "experiments/exp_manner_intensity_harm_v1.py (the arm, the second-pass levers P1-P12, the NEW adverb-in-prose gold, all controls, the lever ablation, the sweep, self-test); tools/build_manner_intensity_asset.py (NEW offline foundation-asset builder: parses WordNet definitions with hdlab.frontend at BUILD time); data/frontend_assets/manner_intensity_v1.json (the shipped dict: 2,305 verbs, 906 valued filler words, 1,836 affecting-animate senses; COUNTS, so the online observe path writes the same units); data/exp_manner_intensity_harm_v1/metrics.json; notes/problems/<slug>/force_dynamics_valence_patch.diff (the proposed hdlab change -- verified to apply cleanly with `git apply --check` and to reproduce every number above when loaded side-by-side with HEAD). NO hdlab/ writes."
reverify: "OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe tools/build_manner_intensity_asset.py && OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe experiments/exp_manner_intensity_harm_v1.py --self-test && OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 HDLAB_EXP_NAME=manner_intensity_harm_v1 .venv/Scripts/python.exe experiments/exp_manner_intensity_harm_v1.py"
---

# Reading the FORCE IN THE MANNER: how "treat brutally" reaches a patient's endstate

**Plain-language headline.** Some verbs hurt because of *how* the action is done — to *brutalize* is to treat
someone *brutally*, to *manhandle* is to handle them *roughly*. Until now the reader stayed silent on those
words, because none of its reference books says what state such an action leaves a person in. This work gives
it the missing sense: it takes the verb's own dictionary definition apart **using its own reading machinery**
(its own word-class organ and its own grammar organ, run once offline), pulls out the word that says *how* —
"brutally", "roughly", "in a cruel manner", "by force" — and then judges that word two ways at once: **how
strong a feeling it carries** (that decides whether it counts at all) and **whether that feeling is good or
bad** (that decides which way it points). All six of the named silent verbs now come out as *harm*, and every
one of the forty-six other newly-decided verbs agrees with an independent set of human judgements. The same
read also works on ordinary sentences: "the guard treated the prisoner brutally" used to come out as **help**
(the dictionary rates the plain word "treat" as pleasant); it now comes out as harm, and on a set of thirty-six
such sentences the reader goes from getting sixteen right to twenty-three, a gap wide enough to be real.

---

## 1. THE FLOOR, VERIFIED FIRST-HAND (not taken from the brief)

`hdlab/force_dynamics_valence.py` at HEAD, cascade = result state -> word norm -> superordinate consensus:

| named manner verb | floor | why |
|---|---|---|
| savage victimize oppress maul persecute molest ravage terrorize enslave | **HARM** (9) | result state or affect-laden superordinate |
| **brutalize manhandle gore subjugate tyrannize maltreat** | **abstain** (6) | VerbNet silent, Warriner norm absent/weak, superordinate = *treat* +0.46 / *handle* +0.18 |

695 affecting verbs still abstain. CF whole-arm 288/309 = **0.9320**. P_NEUTRAL_BROAD 0 leaks. Live 36-item
gold 24/24.

**Reading of the bar.** The bar says "recover >= 8 of the 15 named verbs". The floor already decides 9, so I
held myself to the harder reading the brief's own MEASURED section states: recover the **six that actually
abstain**, at CF precision >= 0.95, with no regression anywhere. All six are recovered; the named count goes
9/15 -> **15/15**.

## 2. THE UPSTREAM CHAIN AND ITS BF STATUS, AS THE DISK SHOWS IT

| rung | organ (live) | BF status on disk | what it hands the harm/help read | signal loss found here |
|---|---|---|---|---|
| tokens | `hdlab/frontend.tokenize` | BF (glass-box regex, no nltk) | tokens | none |
| categories | `hdlab/lexical_categories` (`HDLAB_TAG_SOURCE=counts`, LIVE) | BF_SPIRIT (count-based generative model, forward-backward, plastic) | ADV/ADJ/VERB tags | **2/36** prose manner adverbs tagged **NOUN** (*cruelly*, *carelessly*); 1 tagged ADJ (*kindly*) |
| lemma | `hdlab/morphology` (dual route, LIVE) | BF (byte-identical to morphy, frequency race) | verb lemma | none observed here |
| heads | `hdlab/attachment_arm` (`HDLAB_HEADS_SOURCE=attachment_arm`, LIVE default) | BF_SPIRIT (cue competition + semantic bootstrapping + Matrix-Tree) | governor of the patient; **posterior over heads** | **THE BIG ONE: 33/36** clause-final manner adverbs are argmax-attached to the preceding NOUN, mean posterior mass on the verb **0.215** |
| roles | `graded_role_assigner.coarse_roles` | BF_SPIRIT (Competition Model, configuration-conditioned) | patient identity | not exercised (templates are bare SVO) |
| **the reader** | `force_dynamics_valence` | BF_SPIRIT (Wolff force structure x endstate valence x Beavers affectedness) | HARM / HELP / NA / abstain | **the manner slice**: no result state, no superordinate, weak norm |
| supply | Warriner (V/A/D), Lancaster sensorimotor, WordNet, VerbNet | admissible offline foundation | valence, arousal, grounded action strength, definitions, result predicates | *treat* +0.46 is the NOUN sense — a cross-POS conflation |

## 3. THE BRAIN QUESTION, AND THE MECHANISM

**How does a reader know *brutalize* harms when its superordinate *treat* is neutral?**

1. **MANNER/RESULT COMPLEMENTARITY** (Talmy 1985/2000; Levin & Rappaport Hovav 2010 — PINNED lexicalisation
   universal): a verb root lexicalises the MANNER of an action *or* its RESULT, never both. So for a manner verb
   there simply **is no result state to value** — asking the result-state arm for one is asking the wrong
   question. The valuation target is the manner component.
2. **GROUNDED SIMULATION** (Barsalou 1999; Zwaan; Pulvermüller action-word somatotopy — PINNED): comprehending
   "brutally" re-enacts a forceful action on a body. The force magnitude of that simulation is read from the
   sensorimotor spokes (Lancaster haptic / hand-arm / torso / foot-leg strength) and from **core-affect
   activation**.
3. **OUTCOME VALUATION, SIGN AND MAGNITUDE FROM DIFFERENT CHANNELS** (OFC/vmPFC value coding; Barrett/Russell
   core affect — PINNED): `value(patient endstate) = sign(valence(manner)) gated by intensity(manner)`.
4. **INTENSITY IS THE CIRCUMPLEX RADIUS, NOT AROUSAL.** Russell (1980) is pinned that core affect is a 2-D
   valence x arousal space in which the **radius is the intensity** and the angle the quality. An
   **arousal-only** gate is *structurally incapable* of admitting a gentle helping manner — *kind* (arousal
   0.27) and *gentle* (0.27) sit at the calm end by construction while being maximally evaluative. So
   `intensity = max( sqrt(valence^2 + (arousal - A0)_+^2),  grounded action strength )`: the evaluative axis
   carries *kindly*, the grounded axis carries *roughly* (valence only −0.33 but haptic 0.74).
5. **WHERE THE MANNER WORD IS.** In prose: the adverb the reader's own governor binds to the predicate. In a
   lexicalised manner verb: inside the stored concept, recovered by **parsing the verb's WordNet definition with
   the reader's own glass-box stack** — the count-based category organ plus the attachment arm — **offline**, so
   a dict is shipped and nothing external runs at inference. This is exactly the input the previous solver's
   drilled negative named as missing ("gloss-parsing"); it now exists as a BF organ, so the drill's conclusion
   was correct and its blocker is gone.

**The decomposition, as constructions over the reader's own tags and heads** (`tools/build_manner_intensity_asset.py`):

| slot | construction | example |
|---|---|---|
| `ADVMOD` | a **de-adjectival** ADV whose parsed head is the definition's head predicate | brutalize = "treat **brutally**" -> *brutal* |
| `MANNER_PP` | the ADJ inside "in a/an ADJ ... manner\|way\|fashion" | tyrannize = "... in a **cruel** and autocratic manner" |
| `MEANS_PP` | the content word governed by by/with/through under the head predicate | subjugate = "put down by **force**" |
| `RESULT_ADJ` | the ADJ predicated by make/render/leave/cause | brutalize.v.02 = "make **brutal**" |
| `GENUS` | the head predicate of the definition itself | gore = "**wound** by piercing" |

The **de-adjectival test** on ADVMOD (WordNet pertainym, else -ly stripping with a lexical check = Taft 1979
affix-strip-plus-check, PINNED) is what keeps verb particles out of the manner slot: "put **down** by force"
does not contribute *down* (Warriner −0.45) as a manner.

## 4. WHAT I MEASURED (shipped operating point: residual-only, tau_int 0.40, tau_val 0.10)

- **Named slice:** 9/15 -> **15/15 HARM**; all six abstentions recovered; **0 flips to a wrong sign**.
- **New residual decisions:** 46 (of 695 abstaining), CF precision **6/6 = 1.00**, **0 wrong signs**; the four
  CF-neutral-but-decided (*freeze, modify, sell, switch*) all sit at |Effect(o)| = 0.20, inside the gold's own
  ±0.25 neutral band.
- **Neutral precision:** P_NEUTRAL_BROAD **0 leaks** (floor 0).
- **Whole-arm independent human gold:** **294/315 = 0.9333** ≥ floor 288/309 = 0.9320 — no regression, a small gain.
- **No-regress:** live 36-item modern gold 24/24; harm-frame 10/10; social-harm 15/16; non-prevent-help 15/16;
  the gold's NEUTRAL items decide byte-identically to the floor.
- **THE 2x2 THE BRIEF ASKED FOR** (ungated, over every verb with a manner filler; sign = the filler's valence):

  | | CF sign agreement | n verbs | in P_NEUTRAL_BROAD |
  |---|---|---|---|
  | **high arousal, negative manner** | **0.864** (22 covered) | 96 | 0 |
  | **high arousal, positive manner** | **0.769** (13 covered) | 54 | 0 |
  | low arousal, negative manner | 0.643 (14 covered) | 100 | 0 |
  | low arousal, positive manner | 0.633 (49 covered) | 187 | 0 |

  Read it two ways. (a) The **intensity gate earns its keep**: a manner's valence sign is trustworthy (0.86/0.77)
  exactly when the manner is affectively intense, and near a coin-flip (0.64/0.63) when it is not. (b) The **sign
  comes from valence, not arousal**: the high-arousal POSITIVE cell reads HELP at 0.769, it is not swept into HARM.
- **Slot ablation** (each slot alone, residual read): MEANS_PP 32 decisions at 1.00, RESULT_ADJ 10 at 1.00,
  ADVMOD 7 (recovers 3 of the slice), MANNER_PP 1 slice verb. **Raw GENUS as just another valence slot is the
  refuted parse-free read reappearing** — 154 decisions at 0.875 with **1 neutral leak**; it is *not* shipped in
  that form (see §5).
- **Operating-point sweep** (18 points, tau_int 0.35–0.60 x tau_val 0.10–0.30): CF precision **1.00 with 0 leaks
  at 14 of 18**; the four exceptions are all at tau_val ≥ 0.20 (0.80–0.83). Decided count 49 -> 15 across the
  grid. Not threshold-brittle; the operating point is free to move per organ.
- **Intensity-channel ablation:** circumplex 5 slice / 43 decided / 1.00 / prose 0.639; arousal 5 / 40 / 1.00 /
  0.639; arousal+grounded 5 / 35 / 1.00 / **0.667**; grounded-only 3 / 26; valence-only 3 / 33. The channel
  choice is robust within noise (arousal+grounded differs from circumplex by ONE prose item); circumplex ships
  because it decides most at the same precision and is the pinned geometry.

## 5. THE QUALITY PUSH — four levers built, TWO REFUTED BY THE HUMAN GOLD

| lever | what it does | shipped? | measured cost/benefit |
|---|---|---|---|
| **L1 manner-first** | manner outranks the diffuse word-level norm (the "obviously right" ordering: Warriner rates *treat* +0.46 largely as the NOUN) | **NO — REFUTED-AS-BUILT** | CF whole-arm **0.9333 -> 0.9111** (7 decisions flipped wrong) |
| **L2 manner-host abstain** | a verb with an OPEN MANNER SLOT (*treat*, *handle*, *hold* — derived from the asset, no list) is underspecified for the patient's outcome without a manner, so the word norm must not decide it | **NO — REFUTED-AS-BUILT** | CF **0.9014**, live gold 24 -> **23**; it removes mostly *correct* decisions |
| **L3 genus-by-cascade** | the definition's genus verb valued by the organ's OWN result-state read, under (a) genus-must-name-a-result-state and (b) full cross-sense UNANIMITY | **YES** | recovers **gore** (genus *wound* −0.77, where troponymy gives +0.19); slice 5 -> 6, named 14 -> 15, CF unchanged 0.9333, precision stays 1.00, 0 leaks |
| **L4 morphological reanalysis** | a -ly word with an adjective pertainym IS a manner adverb even when the category organ tags it NOUN (words-and-rules conflict-triggered repair) | **YES** | prose 0.6111 -> **0.6389**, nothing else moves |

L3 needed **two** restrictions before it stopped being the refuted gloss read, each found by a failure:
*visit* = "**pay** a brief visit" inherited *pay* +0.42 and produced exactly 1 neutral leak (fixed by requiring
the genus to name a **result state**); *spur* = "**give** heart or courage to" beside "**strike** with a spur"
produced this arm's only wrong sign against the human gold (fixed by requiring **unanimity** — a sense whose
genus is silent is *missing evidence*, not agreement).

**That L1 and L2 fail is the most useful thing in this write-up.** Both are the reading a linguist would defend
on principle; the independent human gold says no. The shape that survives is the strictly **additive,
residual-only** one — the same shape the landed superordinate arm has.

## 6. THE ADVERB IN RUNNING PROSE — the new gold, and the graded hand-off

**The gold (declared here, `ADVERB_PROSE_GOLD`, n=36):** "<A> <agent> <verb> the <patient> <adverb> ." with an
affect-neutral manner-host verb; 12 harm-manner / 12 help-manner / 12 neutral-manner. The verbs are **shared
across the three cells** so the verb itself carries no information — an arm that ignores the adverb cannot beat
chance-by-verb. Adverbs were chosen before any measurement and not filtered by norm coverage.

| arm | accuracy (± bootstrap CI half-width) |
|---|---|
| floor (`force_dynamics_valence` at HEAD) | **0.4444** ± 0.1667 |
| manner read, **argmax** governor head | 0.4722 ± 0.1667 |
| manner read, **graded** governor posterior | **0.6389** ± 0.1528 |
| **delta (graded − floor), paired bootstrap** | **+0.1944, CI [+0.0833, +0.3056] — CI-SEPARATED** |

Per cell: HARM 2 -> **8** / 12, HELP 10 -> 11 / 12, NEUTRAL 4 -> 4 / 12.

**THE UPSTREAM LOSS, COUNTED (the brief asked for exactly this).** The live governor argmax-attaches the
clause-final manner adverb to **the preceding NOUN in 33 of 36 sentences** (adverb→verb 3/36); mean posterior
mass on the verb **0.215**. An adverb is not a manner modifier of a common noun. But the attachment arm **keeps
the alternatives alive** (MacDonald 1994, and the arm's own Matrix-Tree marginals), so the consumer reads
`P(head = the predicate | this adverb)` instead of the argmax — and that is the whole mechanism: the argmax read
gains **+0.028** over the floor (n.s.), the graded read **+0.194** (CI-separated). *A downstream consumer
repaired to receive the graded signal, rather than the point estimate, is what converts this rung.*

**Where the remaining 13 prose errors are, with counts:** **8** are NEUTRAL-cell items where the **floor**
already answers HELP from the sense-conflating word norm (*treat/handle/carry/grab/hold/pull* all rate positive
in Warriner); the manner read correctly declines to fire (those adverbs are affectively flat) but cannot repair
someone else's error — and the repair I built for it (**L2**) was rejected by the human gold. **1** is a
categories-rung tag error L4 does not reach (*carelessly* -> NOUN, and *careless* is below the valence floor).
**4** are norm-coverage gaps (*contemptuously*, *patiently*, *violently* under a non-affecting *push*).

## 7. PLASTIC, NEVER FROZEN

The asset stores **counts**, not scores: `evidence[verb] = [[synset, slot, filler, count], ...]`, and the
strengths are one pure function of those counts (count-weighted mean valence per sense, then cross-sense
consensus). `observe_manner(verb, filler, slot)` writes into the **same table in the same units** — verified:
`manner_state_value("greet")` is `None` before and `-0.4825` after one observation of *greet* + *brutal*. The
online path is not a second mechanism bolted on; it is how the offline build itself accrues, so a reader that
meets "handled her roughly" in prose learns the same thing the definition taught.

## 8. THE PROPOSED hdlab CHANGE (a proposed diff, per Q111 — strategy lands it)

`notes/problems/<slug>/force_dynamics_valence_patch.diff`, **verified**: `git apply --check` passes, and the
patched file loaded side-by-side with HEAD reproduces every number (named 9 -> 15, slice 0 -> 6, leaks 0, live
gold 24/24, CF 0.9320 -> 0.9333). All additive:

1. New constants `MANNER_READ`, `MANNER_ASSET`, `TAU_INTENSITY=0.40`, `TAU_MANNER_VAL=0.10`, `A0=0.40`,
   `K_AROUSAL`, `K_GROUNDED`, `MANNER_SLOTS`, plus `manner_table()`, `observe_manner()`, `manner_intensity()`,
   `manner_state_value/sign()`, `genus_state_sign()`.
2. `endstate_valence_sign`: **step 4** (the manner) and **step 5** (the definition's genus) after the
   superordinate step, before the abstain.
3. `is_affecting`: a final **guarded** branch (f) — the same decomposition admits the event that signs it,
   never overriding the subject-experiencer exclusion or the non-affecting-dominant guard.
4. `_parse_out()` (the reader's governor **with its marginals kept**) + `_adverb_stem()` + `prose_manner_value()`.
5. `force_dynamics_event_type`: **RUNG 5 manner-in-prose** — precision-weighted fusion, gated behind
   `HDLAB_FDV_MANNER_PROSE`, that yields to a result state and outranks the word-level norm for THIS event.

New asset required: `data/frontend_assets/manner_intensity_v1.json` (rebuild with
`tools/build_manner_intensity_asset.py`, ~10 s). BF status stays `BF_SPIRIT`.

**Withdraw first if wrong:** the RUNG 5 prose fusion. It is the only rung that changes an *existing* live-path
decision (the verb-level arm is residual-only and cannot). Its no-regress evidence is that the 36-item live gold
contains no manner adverbs, so the read is identity there — that is an argument from the gold's composition, not
from a real-prose board run, which a solver cannot execute.

## 9. COMPONENTS TOUCHED OR CREATED, AND THEIR BF STATUS

**CREATED**

| file | role | BF status |
|---|---|---|
| `tools/build_manner_intensity_asset.py` | offline decomposition of WordNet definitions into manner/means/result/genus slots **using the reader's own stack** | **BF_SPIRIT** — Talmy/L&RH manner-result decomposition (PINNED) realised over our own BF category+heads organs; slot constructions are OUR-INVENTION, measured per slot |
| `data/frontend_assets/manner_intensity_v1.json` | 2,305 verbs, 906 valued fillers, 1,836 senses; **counts** | admissible offline foundation SUPPLY + an online `observe_manner` path |
| `experiments/exp_manner_intensity_harm_v1.py` | the arm, the new prose gold, 3 twins, lever ablation, sweep, 2x2, self-test | **BF_SPIRIT** — circumplex-radius intensity (Russell, PINNED) x valence sign (OFC/vmPFC, PINNED); thresholds swept |

**INTERACTED WITH (read-only)**

| organ | how used | BF status |
|---|---|---|
| `hdlab/force_dynamics_valence.py` | the cascade extended (proposed diff only) | **BF_SPIRIT** |
| `hdlab/frontend.py` (Tagger/Parser) | the definition parse at BUILD time; the governor + **marginals** at read time | **BF_SPIRIT** (routes to `lexical_categories` + `attachment_arm`) |
| `hdlab/lexical_categories.py` | categories for the definition and the sentence | **BF_SPIRIT** — located loss: 2/36 prose manner adverbs tagged NOUN |
| `hdlab/attachment_arm.py` | the governor and its posterior | **BF_SPIRIT** — located loss: 33/36 manner adverbs argmax-attached to a NOUN, mass 0.215 on the verb |
| `hdlab/affect_lexicon.py` | valence + arousal (Warriner) | **BF_SPIRIT** — located defect: `treat` +0.46 is a cross-POS/sense conflation |
| `hdlab/morphology.py` | verb lemmas | **BF** |
| WordNet (pertainyms, definitions, frames), Lancaster sensorimotor norms, Warriner V/A/D | offline supply, build time only | admissible foundation |
| Connotation Frames Effect(o) | independent eval gold, never at inference | admissible offline eval SUPPLY |

## 10. KEY REALIZATIONS

- **The missing input the previous drill named was the PARSE, and it now exists.** The three refuted parse-free
  proxies failed because they could not tell WHICH word of a definition is the manner. Running the same
  valuation over the parsed manner slot instead of the strongest gloss word takes 154 decisions at 0.84 with a
  neutral leak to 46 decisions at 1.00 with none. The parse-free twin is the cleanest control in this file.
- **The intensity read is real but it is a GATE, not the signal.** The 2x2 makes this precise: the manner's
  valence sign agrees with humans 0.86/0.77 when the manner is intense and 0.64/0.63 when it is not. Scrambling
  the intensity norms costs 2 of the 6 slice verbs and 0.125 of precision; scrambling the *valence* norms is
  catastrophic (510 reckless decisions at 0.57, three wrong HELP verdicts on the slice). Sign channel and
  magnitude channel do genuinely different jobs, exactly as the brief predicted.
- **An arousal-only intensity read is STRUCTURALLY CAPPED.** Gentle helping manners (*kindly*, *gently*,
  *tenderly*) live at the calm end of the circumplex by construction. Whoever reaches for "arousal = intensity"
  gets a harm-only detector. The pinned geometry (radius, not axis) is what makes the read two-sided.
- **The obvious reorderings were wrong and the human gold caught them.** L1 and L2 are the moves I would have
  shipped on argument alone; both cost real accuracy. The additive residual-only shape won.
- **A downstream consumer can convert an upstream rung by reading its GRADED output.** The governor gets the
  manner adverb's head wrong 33 times out of 36 — and the manner read still wins CI-separated, purely by reading
  the posterior instead of the argmax (argmax +0.028 n.s. vs graded +0.194 CI-sep). "Repair the consumer to
  receive the graded signal" is not a consolation prize here; it is the mechanism.

## 11. WHAT I DID **NOT** ESTABLISH

- **No real-prose board number.** The prose gold is 36 constructed sentences (declared, verb-balanced), not a
  corpus. The `affected_entity` / `affect_harm_help` real-prose numbers under RUNG 5 need a board run, which is
  out of a solver's scope.
- **The CF precision of 1.00 rests on 6 CF-covered items** out of 46 new decisions. The other 40 have no
  independent gold; I report zero wrong signs *among the covered*, and that the 4 CF-neutral decisions all sit
  inside the gold's own neutral band. This is the same coverage limit the previous solver recorded.
- **I did not fix the word-norm conflation** (`treat` +0.46). I built the repair (L2), measured it, and the
  human gold rejected it. The correct fix is a **sense-level** verb norm, not an abstention rule — see next steps.
- **The `MEANS_PP` slot is doing more work than the pure manner slots** (32 of the 43 manner-only decisions). It
  is a means/instrument, not strictly a manner; the Talmy story covers it (both are the non-result half of the
  event template) but it is a broader claim than "manner intensity".

## 12. PRIORITY NEXT STEPS (ranked)

1. **Land the diff top-down and run the board.** Verb-level rungs (steps 4/5 + the `is_affecting` branch) are
   zero-risk-by-construction (residual-only, verified 24/24 + 0 leaks). RUNG 5 prose fusion is the one that
   needs the real-prose `affected_entity` / `affect_harm_help` numbers.
2. **UPSTREAM, and it is not this organ's to fix: an ADV's governor is a predicate.** The attachment arm
   argmax-attaches 33/36 clause-final manner adverbs to a noun. A category-conditioned arc constraint (or simply
   suppressing ADV→common-noun arcs before the Matrix-Tree) is the Competition Model's own within-configuration
   contrast and should lift `advmod` for every consumer, not just this one. **Filed for the attachment_arm
   brief; deliberately not attempted here** (a concurrent solver owns that organ).
3. **The sense-level verb norm.** `treat` +0.46, `handle` +0.18, `hold` +0.26 are the NOUN/other-sense readings
   leaking into a verb decision, and they cost 8 of the 13 remaining prose errors. The organ already has
   `context_sense_sign` (PPR spreading activation); the missing piece is a **sense-keyed affect norm** rather
   than a word-keyed one. That is a foundation-asset build, and it is the largest single remaining error class
   in this problem.
4. **Grow the manner table by reading.** `observe_manner` exists and is verified; nothing currently calls it.
   Wiring it into the reader's event loop would let manner knowledge accrue from prose the way the brief's
   plasticity rule intends.
5. **Extend the decomposition to adjectival and nominal manner** ("gave him a *brutal* beating", "with great
   *cruelty*") — the same slots, different constructions.

## 13. TLDR

The harm in *brutalize* is in the word *brutally*, and the reader could not find that word. It can now: the
verb's definition is decomposed into manner / means / result / genus slots **by the reader's own category and
attachment organs, offline**, and the manner is valued the way the brain values an outcome — **sign from
valence, magnitude from the circumplex radius of its core affect or the grounded force of the action it
evokes**. All six named silent verbs recovered (named manner verbs 9/15 -> 15/15), 46 residual verbs newly
decided at **1.00** precision against an independent human gold with **zero** wrong signs and **zero** neutral
leaks, whole-arm human-gold agreement up 0.9320 -> 0.9333, live gold untouched. In running prose the same read
turns "treated the prisoner brutally" from **HELP** into **HARM** and lifts a declared 36-sentence gold
**0.444 -> 0.639, +0.194 CI [+0.083, +0.306]** — achieved by reading the governor's **graded posterior**, because
its argmax puts the manner adverb on the wrong word 33 times out of 36. Two "obviously right" levers were built
and **refuted by the human gold**, and are documented as such.

## 14. QUESTIONS (for the owner / strategy)

- Land RUNG 5 (the prose manner fusion) with the verb-level rungs, or land the verb-level rungs first and hold
  RUNG 5 for a board run? It is the only rung that can change an existing live decision; my recommendation is to
  land it behind `HDLAB_FDV_MANNER_PROSE=1` **and** run the board in the same pass, since holding it means the
  adverb-in-prose win never reaches a consumer. **Risk of my own recommendation:** the 36-item live gold cannot
  detect a prose-fusion regression (it contains no adverbs), so the board is the only real check.
- The `treat` +0.46 cross-sense conflation now blocks three separate things (this problem's neutral cell, the
  earlier `throttle`/`batter` cases, RUNG 3's sense-in-context). Is a **sense-keyed affect norm** worth its own
  brief, above the remaining manner work?


---
---

# SECOND PASS — the supervisor probe (2026-09-13): understanding, the signal trace, and seven levers

**Headline of this pass, stated without padding: NOT ONE HEADLINE NUMBER MOVED.** The pass produced
understanding, eight mechanistically-understood negatives, two corrections to claims I made in the first
report, one measured upstream specification for another organ — and a demonstration that that upstream repair
is worth **exactly 0.0** to this consumer. That last result is the most valuable thing in it.

## 15. BEFORE / AFTER (first final report vs now)

| measure | after pass 1 | after pass 2 | change |
|---|---|---|---|
| named manner verbs HARM | 15 / 15 | **15 / 15** | — |
| manner slice recovered | 6 / 6 | **6 / 6** | — |
| new residual decisions | 46 | **46** | — |
| CF precision on new decisions | 6/6 = 1.00 | **6/6 = 1.00** | — |
| CF whole-arm agreement | 294/315 = 0.9333 | **294/315 = 0.9333** | — |
| leaks on `P_NEUTRAL_BROAD` | 0 | **0** | — |
| live 36-item modern gold | 24 / 24 | **24 / 24** | — |
| adverb-in-prose gold | 0.6389 (+0.1944 CI [+0.0833,+0.3056]) | **0.6389 (unchanged)** | — |
| **NEW: second human gold (Binder)** | not attempted | **REJECTED with counts** (434/535 entries are `thing` concepts; 2/46 new decisions covered) | new |
| **NEW: UD-EWT advmod, live arm** | assumed broken from 3/36 | **0.5475 over 442 — the arm is NOT broadly broken** | corrected |
| **NEW: the construction's real frequency** | unknown | **15 / 442 advmod = 3.4%** | new |
| **NEW: governor cue, unconditioned** | proposed | **REFUTED: advmod 0.5475 → 0.4932–0.5317** | new |
| **NEW: governor cue, CONFIGURATION-CONDITIONED** | — | **advmod 0.5475 → 0.5475 (zero cost), slice posterior 0.4445 → 0.5332** | new |
| **NEW: downstream value of repairing the governor** | assumed large | **0.0 — prose gold identical, every item** | corrected |
| **NEW: online observe path, exercised** | never called | **203 observations / 4000 lines → 5 new decisions at 4/5, no regression** | new |
| levers built and measured | 4 (2 shipped, 2 refuted) | **11 (2 shipped, 9 refuted or inert)** | +7 |

## 16. THE SIGNAL-LOSS TRACE, RUNG BY RUNG, WITH COUNTS

**The signal:** *the manner's affect, reaching the patient's endstate.* Measured on the 36-sentence gold
(`signal_trace()` in the cell; per-item rows in `metrics.json`).

| # | rung / organ | what it PRODUCES | what my read TAKES | measured LOSS |
|---|---|---|---|---|
| 1 | **categories** `lexical_categories` | a point tag **and** a graded posterior | the point tag, then repairs it morphologically | **4 / 36** manner adverbs mis-tagged (*cruelly*, *carelessly* → NOUN; *kindly* → ADJ). L4 recovers them; worth **+1** item |
| 2 | **governor** `attachment_arm` | a single-root MAP tree (point) **and** Matrix-Tree marginals (graded) | **the marginals** | argmax on the verb **3/36**; mass on the verb **0.215** (templates) / **0.4445** (the real UD-EWT instance of this construction, n=15). Taking the point estimate would lose the whole read; taking the posterior loses **nothing** |
| 3 | **morphology** `morphology` / pertainym + strip-and-check | adverb → adjective stem | the stem | **1 / 36** (*sideways*, correctly — it is not de-adjectival) |
| 4 | **affect lexicon** `affect_lexicon` (Warriner) | **one scalar per WORD FORM**, no sense index, no variance | valence (sign) + arousal (magnitude) | **3 / 36** stems uncovered (*contemptuous*, *sudden*, *sideways*); **6 / 24** signed items fail the gate; **0 / 12** neutral items pass (correct). And on the VERB side the same conflation costs **8 of the 13** remaining prose errors |
| 5 | **roles** `graded_role_assigner` | the patient, with cue strengths learned from the organ's own perceived heads | not exercised (bare-SVO templates; animacy from WordNet) | **untested here — named as a gap** |
| 6 | **the fusion** (mine) | HARM / HELP / abstain | result state > manner > word norm | ordinal precedence, not variance-weighted (no cue carries a variance) |

### 16b. WHY the governor rates ADV→NOUN above ADV→VERB — the exact cue decomposition

Averaged over the 36 items, score(NOUN) − score(VERB) = **+1.161**:

| cue | Δ (noun − verb) | what it is |
|---|---|---|
| **locality** | **+0.893** | `L1` (adjacent, head-left) is worth **+1.314** in the `NOUN>ADV:L` configuration; `L3-4` is worth **+0.218** in `VERB>ADV:L`. **77% of the whole gap.** |
| frame | +0.146 | the `VERB>ADV:L` frame cue is itself **−0.141** — the learned verb frames never saw a manner adverbial |
| plaus | +0.059 | fires only for nominal dependents |
| config | +0.040 | even the configuration prior favours the noun (`NOUN>ADV:L` 0.943 vs `VERB>ADV:L` 0.754) |
| **constr** | **+0.024**, and `constr=none` **on both candidates** | **the smoking gun.** `attachment_arm.CONSTRUCTIONS = {verbarg, coord, npmod, clausal, fw}` contains **no manner-adverbial schema**, so the arm's strongest cue channel contributes **zero** to the correct arc — while in the one row where a construction does fire (`cruelly` mis-tagged NOUN → `constr=verbarg`) it is worth **+1.081** and the verb wins |
| boundary / agree / form | 0.000 | inactive in this configuration |

*A side-effect worth recording: the categories-rung error **compensates** for the missing construction —
`cruelly` tagged NOUN gets `constr=verbarg` (+1.081) and lands on the verb with mass 1.00, while correctly
tagged `brutally` lands on the noun with 0.86. Two defects cancelling is not a working chain.*

## 17. PER-RUNG BF STATUS **FOR THIS SIGNAL** (graded, point, or conflated?)

| rung | BF status of the computation | does it hand DOWN the graded signal this read needs? |
|---|---|---|
| categories | **BF_SPIRIT** — count-based generative model, forward-backward posterior, plastic (PINNED: Bayesian cue integration, graded belief) | **YES, and it is available** (`tag_with_posterior`) — but my read consumes the point tag and repairs it. *My* shortcoming, not the organ's |
| governor | **BF_SPIRIT** — cue competition (MacDonald 1994) with exact single-root Matrix-Tree marginals (PINNED: keep-alternatives-alive) | **YES** — and taking it is the entire prose win. The gap is an incomplete construction inventory, not a non-graded hand-off |
| morphology | **BF** — Rastle & Davis / Taft strip-and-check, dual route (PINNED) | yes (categorical by nature) |
| **affect lexicon** | **BF_SPIRIT as a SUPPLY**, but **NOT graded and NOT sense-keyed** | **NO.** One scalar per word form, no sense index, **no variance**. This is the one rung that structurally cannot hand down what a precision-weighted fusion needs |
| roles | BF_SPIRIT — Competition Model, validities from perceived heads | untested for this signal |
| result-state arm | BF_SPIRIT — VerbNet sense-keyed states + the innate nociceptive sign (PINNED) | yes, and it is correctly given precedence |

**The one structurally non-BF rung for this signal is the affect lexicon.** Everything else either already hands
down a graded signal or is categorical by nature.

## 18. THE BRAIN'S MATHEMATICS ALONG THIS CHAIN vs WHAT IS BUILT

| computation | the brain's math (status) | what is built | the difference, measured |
|---|---|---|---|
| **adverb attachment** | cue competition: arc score = Σ contrasts within a configuration, alternatives kept as a posterior (MacDonald-Pearlmutter-Seidenberg 1994; Lewis & Vasishth 2005 retrieval; Hale/Levy surprisal) — **PINNED**; item-based constructions as cue coalitions (Tomasello 2003; Goldberg) | exactly that, minus one construction | the missing manner-adverbial schema hands **+1.161 log-odds** to the wrong candidate; `constr` contributes 0 where it is worth +1.081 when present |
| **manner/result lexicalisation** | a verb root lexicalises manner XOR result (Talmy 1985/2000; Levin & Rappaport Hovav 2010) — **PINNED** | the decomposition is the mechanism | none — this is the rung that was cracked |
| **core affect** | 2-D valence × arousal circumplex; **radius = intensity, angle = quality** (Russell 1980; Barrett) — **PINNED** | intensity = the radius, sign = the valence axis | replicated. Measured payoff: sign agreement 0.864/0.769 at high arousal vs 0.643/0.633 at low |
| **outcome valuation** | OFC/vmPFC value over the simulated result state; nociception innate — **PINNED** | Warriner ratings as a proxy for the valuation | **a human rating is not a simulation.** The value is looked up, not computed from a grounded re-enactment. See ALTERNATE PATH 2 |
| **affect retrieval by sense in context** | the settled sense vector determines the meaning retrieved (Rodd; PPR spreading activation) — **PINNED/MODEL** | `context_sense_sign` exists and is live (residual-only) | **measured this pass: it does not discriminate.** `treat` → sign **+1 in all six** of its contexts (brutally, cruelly, kindly, routinely, privately, impersonally). The *selection* is the weak half, not the keying |
| **precision-weighted fusion** | w ∝ 1/σ² (Ernst & Banks 2002; Ma & Pouget) — **PINNED** | an **ordinal precedence** (result state > manner > word norm) | no cue carries a variance, so a true reliability weighting is not computable. The ordinal order is the degenerate case — and pass 1's L1 got the order **backwards**, which the human gold caught |

## 19. EVERY NEGATIVE, UNDERSTOOD MECHANISTICALLY, WITH NUMBERS

1. **L1 (manner above the word norm) — CF 0.9333 → 0.9111.** 7 of 315 decisions flip wrong. *Mechanism:* it
   only changes verbs where a manner AND a word norm both exist and **disagree** — and for those the manner
   filler is usually a `MEANS_PP` or a genus-adjacent word describing the **instrument**, not the outcome
   (*administer, court, hang, load*). The word norm, where it fires, is a **0.93-accurate** cue; the manner is
   0.86/0.77 at high arousal and **0.64 at low**. So the precedence must follow the precision — and I had it
   backwards. This is the Ernst-Banks rule applied honestly rather than rhetorically.
2. **L2 (abstain on manner-host verbs) — CF 0.9014, live gold 24 → 23.** 21 decisions removed, ~all correct.
   *Mechanism:* the host set is derived by counting *which verbs are described with a manner*, and the most
   frequently manner-described verbs are the most affect-laden ones — **beat (22), hit (19), treat (16),
   kill (8), injure (6), attack (5)**. A co-occurrence count named the wrong class: "often described with a
   manner" ≠ "underspecified without a manner".
3. **The arousal-only gate — slice 5/6 instead of 6/6.** *Mechanism, structural not statistical:* calm positive
   manners sit at the low-arousal pole **by construction** — *kind* 0.274, *gentle* 0.271, *tender* 0.278,
   against a gate at 0.40, while *brutal* 0.516 and *rough* 0.554 pass. An arousal gate is a **harm-only
   detector**. (It scores the same 0.6389 on the prose gold only because that gold's HELP cell is already
   carried 10/12 by the floor — a coverage artefact, not evidence for arousal.)
4. **The parse-free twin's 0.8421 over 154 decisions — why so far above chance?** *Mechanism:* for verbs whose
   definitions are affect-saturated (*torture: subject to torture*) the strongest-valence word **is** the
   outcome, so the proxy is a lower-precision, 3×-recall estimator, not an information-free one. But on the
   manner slice specifically the strongest word is the **genus** (*treat*, *handle*), which is why it recovers
   **0 of 6**. **The parse buys the slice, not the average** — precisely the shape of the original drilled
   negative, now explained.
5. **The POS-conflation lever (P2) — REFUTED, and my diagnosis in pass 1 was WRONG.** SemCor noun fractions:
   **treat 0.000**, handle 0.059, hold 0.025, grab 0.000, carry 0.006 (only *wound* 0.828 and *place* 0.527 are
   noun-dominant). So `treat` +0.46 is **not** a cross-POS artefact — it is a **within-verb sense** conflation.
   Withholding the norm for noun-dominant strings removes **11 correct decisions for 4 wrong** ones; the
   apparent precision gain (0.9333 → 0.9400) is **pure coverage shrinkage** — on the shared 300 items both arms
   score identically. A count of decisions removed is not a quality gain.
6. **Binder as a second human gold — REJECTED.** 434 of 535 entries are `thing` concepts; the 113 overlapping
   strings are noun homographs (*cabbage −2.23, monkey +1.22, submarine +0.96, soldier +0.97*) rated as
   **concepts**, not as verb outcomes. It covers **2 of the 46** new decisions. The 0.8378 → 0.8421 it reports
   is not evidence about a verb read. (NRC EmoLex is on disk and also inadmissible: an *association* lexicon,
   already documented as over-firing in `hdlab/affect_lexicon.py`.)
7. **The descriptive-vs-relational adjective filter — REJECTED BEFORE BUILDING.** Levi (1978) / WordNet
   `adj.all` vs `adj.pert`, checked on 43 stems: *mental, verbal, legal, visual, national* carry `adj.all` too,
   and *most, complete, probable, usual, real* are pure `adj.all`. The distinction does not separate manner
   from degree at all.
8. **The unconditioned governor boost — REFUTED: advmod 0.5475 → 0.4932–0.5317, UAS 0.6125 → 0.6092–0.6115.**
   *Mechanism, now exact:* it fires on all **442** UD-EWT advmod tokens to help the **15** that are this
   construction. The arm's own discipline is that every strength is a contrast **within a configuration**;
   a global additive bonus violates it. The scrambled-target twin is flat (advmod 0.5452), confirming the
   damage is the boost's breadth, not noise.
9. **The online path on encyclopedic prose — mechanically fine, materially empty.** 4000 Simple-Wikipedia lines
   → 203 observations, 117 verbs, **0 verbs gained a manner decision**, 5 new decisions at **4/5** correct, CF
   0.9333 → 0.9313 with 0 leaks and the live gold held. The accrued fillers are dominated by **degree and
   sentential** adverbs (*mostly, completely, publicly*), which the read's own gate then discards. A
   WordNet-manner-gloss filter drops 135 of 203 and changes the outcome by **−0.0005** — the gate was already
   doing the filtering.

## 20. WHAT WAS BUILT AND KEPT IN THIS PASS

**One thing, and it is not shippable from this brief:** the **configuration-conditioned manner-adverbial
construction cue** for `attachment_arm`.

| arm | UD-EWT advmod (n=442) | UAS (9534 tok) | the target slice (n=15) | mean posterior on the gold verb |
|---|---|---|---|---|
| live | 0.5475 | 0.6125 | 7/15 = 0.4667 | 0.4445 |
| unconditioned boost γ4 | **0.5000** | 0.6102 | 8/15 | 0.5256 |
| **conditioned γ4** | **0.5475** | **0.6125** | **8/15 = 0.5333** | **0.5256** |
| **conditioned γ8** | **0.5475** | 0.6124 | **8/15** | **0.5332** |
| scrambled-target twin γ4 | 0.5452 | 0.6128 | — | — |

**Zero global cost, +0.089 posterior mass on the target slice** — but the paired bootstrap over n=15 gives
**+0.0887 CI [−0.1333, +0.3143], NOT CI-separated.** It is underpowered, and I say so rather than claim it.

**AND THE RESULT THAT MATTERS MOST IN THIS PASS: repairing that rung is worth 0.0 to this consumer.** With the
conditioned cue on, the manner adverb's posterior mass on the verb goes from 0.215 to **0.9409** on the prose
gold — and the harm/help accuracy is **0.6389, identical on every one of the 36 items** (Δ = 0.0, CI [0,0]).
*The graded read had already extracted everything the rung had.* The mass-weighted mean's **sign** does not
change when the mass rises, because the qualifying adverb is unique in the clause. So: **do not queue the
manner-construction cue on this consumer's behalf.** It should be queued for the consumers that read the
**point tree** (roles, labels) — and this measurement tells that brief what to expect and what not to.

**Built, measured, and NOT shipped because it is inert:** the derivational backoff (*contemptuous → contempt*,
−0.445). It recovers 1 of 3 uncovered stems and changes **nothing** on any population (CF 0.9333, leaks 0,
slice 6, prose 0.6389 — byte-identical with and without). It fails to convert its one target item by 0.005
(the communication-verb admissibility gate needs |value| ≥ 0.45 and *contempt* is −0.445); moving that
threshold to catch one item of my own gold would be fitting, so I did not. An unmeasurable change does not ship.

## 21. THE SLOT × AROUSAL TABLE (where the low-arousal weakness actually lives)

CF sign agreement of the best filler per verb, split by slot and by arousal:

| slot | high arousal | low arousal |
|---|---|---|
| `ADVMOD` | 5/6 = **0.833** | 10/24 = **0.417** |
| `MANNER_PP` | 0/1 | 4/4 = 1.000 |
| `MEANS_PP` | 19/22 = **0.864** | 22/34 = **0.647** |
| `RESULT_ADJ` | 6/7 = 0.857 | 9/9 = **1.000** |

Two readings. (a) The low-arousal weakness is in **ADVMOD and MEANS_PP**, not everywhere: `RESULT_ADJ` is
**1.000 at low arousal**, because a *result state* is evaluative whether or not it is arousing — which is
exactly the theory (the circumplex radius matters for a manner; a result state is valued directly). (b)
`MEANS_PP` carries 32 of the 43 manner-only decisions, so the arm leans on the slot that is a **means**, not
strictly a manner. A slot-specific gate for `MEANS_PP` was built and swept (τ 0.40–0.70); it changes the slice
and the decision count but the harness admitted verbs it should not (31 leaks) — **the harness is defective,
the finding is not established, and I am recording it as not-established rather than as a result.**

## 22. WHAT LET THIS PROBLEM YIELD SO MUCH SIGNAL — the chain, rung by rung

The owner's expectation is that a large yield means the mathematical brain-foundational chain was cracked to
the top. That is what happened here, and this is the chain:

| rung | the brain's computation | the math replicated | was the graded signal kept? |
|---|---|---|---|
| **1. what to value** | manner/result complementarity (Talmy; Levin & Rappaport Hovav) — **PINNED** | a manner verb has no result state, so the manner IS the valuation target | n/a — this is the framing that made the rest possible |
| **2. where the manner is** | the lexical concept's decomposition | the definition parsed into manner/means/result/genus **by the reader's own category and attachment organs**, offline | **yes** — the parse is what the parse-free twin (0/6 on the slice) lacks |
| **3. the word form → the concept** | morpho-orthographic decomposition, dual route (Rastle & Davis; Taft; Pinker-Ullman) — **PINNED** | pertainym, else -ly strip + lexical check | categorical; 35/36 |
| **4. how strong, how good** | core affect as a 2-D circumplex, radius = intensity, angle = quality (Russell) — **PINNED** | intensity = the radius (or the grounded action strength); sign = the valence axis | **yes** — both are continuous, and the 2×2 (0.864/0.769 vs 0.643/0.633) is the proof they do different jobs |
| **5. trusting it** | cross-sense consensus (the discipline that rescued the superordinate read) | value per sense, sign only under agreement | **yes** — abstention is graded evidence, not failure |
| **6. binding it to the event** | cue competition keeping the alternatives alive (MacDonald 1994; Matrix-Tree) — **PINNED** | the consumer reads **P(head = predicate \| adverb)**, not the argmax | **YES — and this is the single largest win in the whole problem.** argmax read +0.028 n.s.; graded read **+0.194 CI-separated** |
| **7. combining the cues** | precision-weighted fusion (Ernst & Banks) — **PINNED** | ordinal precedence result > manner > norm | **NO** — degenerate, because no cue carries a variance |

**Where the chain was NOT cracked, and it shows:**

- **Rung 7 (fusion) is ordinal, not variance-weighted** — no cue supplies a σ. Pass 1's L1 got the order
  backwards precisely because ordering by argument rather than by measured reliability is guesswork; the
  human gold had to supply what the missing variances should have.
- **The affect lexicon (rung 4's supply) is a point value per word form** — no sense, no variance, no
  posterior. It is the only rung in the chain that structurally cannot hand down a graded signal, and it is
  where the remaining 8 of 13 prose errors live.
- **Roles were never exercised** — the templates are bare SVO, so the patient is given. On real prose this rung
  is live and untested for this signal.

**The honest summary of the yield:** the biggest single gain (+0.194 CI-separated) came not from new knowledge
but from **reading a graded signal that was already there and being thrown away**; the second (6/6 of the
slice) came from **using our own BF organs on the foundation's own definitions**, so nothing external entered
at any point. Both are chain properties, not cleverness — which is the owner's point.

## 23. THE LOCATED LIMIT — three independent routes to the same target, all measured, all failing differently

The 8 remaining prose errors are all the same shape: *"A guard treated the prisoner routinely"* → the floor
answers **HELP** because Warriner rates `treat` +0.46, and the manner read correctly declines to fire because
*routinely* is affectively flat. Three routes to fixing that, each built and measured this pass:

| route | result | why it failed, mechanically |
|---|---|---|
| **withhold the norm for manner-host verbs** (L2) | CF 0.9014, live gold 23 | the host set is the *most affect-laden* verbs (beat 22, hit 19, kill 8) |
| **withhold the norm for noun-dominant strings** (P2) | 11 correct removed for 4 wrong | `treat` is **0.000** noun-dominant — the conflation is not cross-POS |
| **read the sense in context** (the organ's live PPR reader) | `treat` → **+1 in all six contexts** | the *selection* is context-blind here, not the keying |

**What is actually missing, named precisely:** an affect value for the verb's outcome **conditioned on whether
the manner slot is filled** — P(outcome | verb, manner present/absent). Not a word norm, not a sense norm: a
**construction-conditioned** one. Nothing on disk supplies it; it has to be counted from the reader's own
parsed events, which makes it a **generative-world-model** requirement (pri-1), not a lexicon lookup.

## 24. ALTERNATE PATHS — other ways to do this read, as or more brain-foundational

| # | brain structure & computation | the math | what it would take | why not now |
|---|---|---|---|---|
| **AP1** | **Acquire the manner lexicon by READING** rather than from definitions (Hebbian association over exposure; the project's own reading-acquisition arm) | count (verb, manner) co-occurrence; strengths = the same pure function of counts | ~1M lines of **modern narrative/interpersonal** prose + the reader's governor; the same battery | **measured:** 4000 lines of Simple-Wikipedia yield 5 decisions at 4/5. Encyclopedic prose has almost no interpersonal manner. The path is right; the corpus is wrong, and 19c narrative is banned for grading (admissible only as foundation supply) |
| **AP2** | **Value the manner by SIMULATION, not by lookup** (Barsalou; Pulvermüller somatotopy; OFC valuation over a re-enacted action) — **strictly more BF than a Warriner rating** | a grounded vector for the manner + a learned map to an aversive/appetitive readout anchored on innate nociception | perceptual grounding for manner *adjectives* (the DINOv2/THINGS route the project used for nouns) | that grounding does not exist for adjectives on disk. **This is the honest "more brain-foundational" replacement for the whole valuation channel** and should be queued as such |
| **AP3** | **Read the manner from the ARGUMENT-STRUCTURE CONSTRUCTION** (Goldberg; Tomasello) rather than the lexical entry: `V NP ADV` *means* "affect NP in manner ADV" | the value composes from the construction; the verb contributes the frame | an induced constructional inventory | induced constructions were **REFUTED-AS-BUILT** in the heads rung; my slot detectors are a hand-authored approximation of exactly this |
| **AP4** | **Make the affect lexicon sense-keyed and graded** (settled-vector semantics; Rodd) — the missing variance for rung 7 | label propagation / PPR of the word norms over WordNet++ → a valence **and a variance** per synset | a foundation-asset build inside `affect_lexicon` | out of this brief's file scope, and measured this pass: the *selection* is the weak half (`treat` → +1 in all six contexts), so keying alone will not convert it |
| **AP5** | **Learn the outcome distribution generatively** — P(outcome \| verb, manner-slot filled) from the reader's own parsed events | generalized event knowledge counted over parsed events | the generative world model (pri-1) | this is the named located limit of §23; it belongs to pri-1, not here |
| **AP6** | **Dominance/potency as the third Osgood axis** for intensity | radius in the full E-P-A space rather than E-A | nothing — the norms are already loaded | checked: Warriner dominance tracks **valence** (kind 7.62 vs cruel 4.78), not force. It would double-count the sign channel. Not built |

## 25. ARE THE OPPORTUNITIES EXHAUSTED?

**Within this brief's scope and file permissions: essentially yes, and here is the accounting.** Eleven levers
built or checked; two shipped in pass 1; nine refuted, inert, or out of scope, each with a number and a
mechanism. The three routes to the largest remaining error class (§23) are all measured and all fail for
distinct, understood reasons, and the thing that would fix it is a **construction-conditioned outcome
distribution** that requires the generative world model.

**Not exhausted, and honestly outside what a solver session can close here:**
1. **AP2 (simulated rather than looked-up valuation)** — strictly more brain-foundational than what I shipped,
   and blocked only by missing perceptual grounding for adjectives.
2. **AP1 at scale** — the acquisition path is proven to work mechanically and starved of the right corpus.
3. **The real-prose board number** — the only measurement that can falsify the RUNG 5 prose fusion, and a
   solver cannot run it.
4. **Roles** — never exercised for this signal.

I am not claiming exhaustion beyond that, and I would not want the four items above read as closed.
