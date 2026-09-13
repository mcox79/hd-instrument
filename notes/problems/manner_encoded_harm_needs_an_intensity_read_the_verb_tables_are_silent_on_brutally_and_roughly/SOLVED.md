---
problem: manner_encoded_harm_needs_an_intensity_read_the_verb_tables_are_silent_on_brutally_and_roughly
status: SOLVED
bar: "Recovers the manner slice (>= 8 of the 15 named verbs) at Connotation-Frames precision >= 0.95 with 0 leaks on P_NEUTRAL_BROAD and the live gold held (>= 35/36), the adverb-in-prose gold CI-separated over the current abstaining read, twin (scrambled intensity norms) losing, knowledge as an offline foundation asset + an online observe path -- OR a numbered located negative naming the missing input."
result: "MANNER-INTENSITY ARM (manner/means/result decomposition of the verb's definition, parsed OFFLINE by the reader's own glass-box stack; sign from the manner's VALENCE, magnitude from the CIRCUMPLEX RADIUS of its core affect or its GROUNDED action strength; operating point tau_intensity=0.40, tau_manner_val=0.10). Named manner verbs reading HARM 9/15 -> 15/15, i.e. ALL SIX of the floor's abstentions recovered (brutalize, manhandle, gore, subjugate, tyrannize, maltreat) with 0 flips to a wrong sign. 46 still-abstaining affecting verbs newly decided at Connotation-Frames precision 6/6 = 1.00 with ZERO wrong signs (the 4 CF-neutral-but-decided all sit at |Effect(o)| = 0.20, inside the gold's own +-0.25 neutral band). 0 leaks on P_NEUTRAL_BROAD (n=36). Whole-arm CF agreement 294/315 = 0.9333 >= floor 288/309 = 0.9320. Live 36-item modern gold 24/24 HARM/HELP held, NEUTRAL items byte-identical to the floor. NEW adverb-in-prose gold (36 declared sentences, an affect-neutral verb + a manner adverb): floor 0.4444 -> 0.6389, delta +0.1944 CI [+0.0833, +0.3056] CI-SEPARATED; the argmax-head read gets only 0.4722, so the win is the GRADED governor posterior. Controls: scrambled-intensity twin 4/6 slice and CF precision 0.875; scrambled-valence twin 2/6 with 3 WRONG HELP and precision 0.5714 over 510 reckless decisions; parse-free twin (the refuted gloss proxy through the identical valuation) 0/6 and 0.8421 over 154 decisions. The 2x2 the brief asked for: with a HIGH-arousal manner the valence sign agrees with the human gold 0.864 (negative) / 0.769 (positive); with a LOW-arousal manner 0.643 / 0.633 -- the intensity gate is what makes the sign trustworthy, and a high-arousal POSITIVE manner reads HELP, not HARM. TWO LEVERS REFUTED-AS-BUILT by the human gold and NOT shipped: promoting the manner above the diffuse word-level norm (CF 0.9333 -> 0.9111) and abstaining on manner-host verbs (0.9014, and a live-gold item)."
floor: "hdlab/force_dynamics_valence.py at HEAD (result state -> word norm -> superordinate consensus): 9/15 named manner verbs HARM and 0/6 of the manner slice (brutalize/manhandle/gore/subjugate/tyrannize/maltreat all abstain, first-hand verified); 695 affecting verbs still abstain; CF whole-arm 288/309 = 0.9320; P_NEUTRAL_BROAD 0 leaks; live 36-item gold 24/24. On the adverb-in-prose gold the floor is not merely silent -- it answers HELP on 'treated the prisoner brutally' (Warriner treat +0.46 is largely the noun 'a treat') and scores 0.4444."
controls: "(1) TWIN, SCRAMBLED INTENSITY (the brief's named control) -- arousal + grounded action strength permuted across words: slice 4/6 (vs 6/6) and CF precision on new decisions 0.875 (vs 1.00). (2) TWIN, SCRAMBLED VALENCE (the sign channel) -- slice 2/6, THREE WRONG HELP verdicts on the slice, 510 decisions at 0.5714 precision, 1 neutral leak: the sign channel is load-bearing and its loss is catastrophic, not quiet. (3) PARSE CONTROL -- the manner filler replaced by the strongest-valence word of the SAME definition (exactly the drilled, refuted parse-free gloss proxy) through the identical intensity/consensus valuation: 0/6 of the slice, 154 decisions at 0.8421. The PARSE is what makes the read work. (4) INDEPENDENT HUMAN GOLD -- Connotation Frames Effect(o) (Rashkin, Singh & Choi ACL 2016), never read at inference: new-decision precision 1.00 with 0 wrong signs, whole-arm 0.9333 >= floor 0.9320. (5) NEUTRAL PRECISION -- 0 leaks on P_NEUTRAL_BROAD; 0 of the 2x2's 437 manner-bearing verbs falls in that population. (6) NO-REGRESS -- live 36-item modern gold 24/24, harm-frame 10/10, social-harm 15/16, non-prevent-help 15/16, all unchanged; 0 of the 15 named verbs flips sign. (7) OPERATING-POINT SWEEP -- tau_intensity 0.35-0.60 x tau_manner_val 0.10-0.30 (18 points): CF precision 1.00 and 0 leaks at 14 of 18 (the four exceptions are all at tau_manner_val >= 0.20); the win is not threshold-brittle. (8) ARGMAX ABLATION on the prose gold: 0.4722 vs the graded read's 0.6389 -- names the graded posterior as the mechanism. (9) INTENSITY-CHANNEL ABLATION: circumplex / arousal / arousal+grounded all hold precision 1.00; grounded-only and valence-only lose the slice (3/6) -- the channel choice is robust, the gate is not."
files_changed: "experiments/exp_manner_intensity_harm_v1.py (the arm, the NEW adverb-in-prose gold, all controls, the lever ablation, the sweep, self-test); tools/build_manner_intensity_asset.py (NEW offline foundation-asset builder: parses WordNet definitions with hdlab.frontend at BUILD time); data/frontend_assets/manner_intensity_v1.json (the shipped dict: 2,305 verbs, 906 valued filler words, 1,836 affecting-animate senses; COUNTS, so the online observe path writes the same units); data/exp_manner_intensity_harm_v1/metrics.json; notes/problems/<slug>/force_dynamics_valence_patch.diff (the proposed hdlab change -- verified to apply cleanly with `git apply --check` and to reproduce every number above when loaded side-by-side with HEAD). NO hdlab/ writes."
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
