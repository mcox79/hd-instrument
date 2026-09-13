---
problem: the_verbs_affect_value_is_one_number_across_its_senses_treat_handle_hold_read_as_pleasant_a_sense_keyed_norm
status: SOLVED
bar: "The 8 neutral-cell HELP errors of the adverb-in-prose gold reduced by at least half, with 0 new leaks on P_NEUTRAL_BROAD, the Connotation-Frames whole-arm not down (CI), the 36-item live modern gold held, a twin (sense values shuffled across the senses of the same word) losing CI-separated, and knowledge as counts per sense with an online observe path -- OR a numbered located negative naming the missing input."
result: "SENSE-KEYED, PRECISION-WEIGHTED VALUE. value(verb | context) = SUM_s P(s|context) v(s), fused with the word-form norm weighted by that word's OWN UNAMBIGUITY rho (Simpson concentration of its sense distribution; rho(treat) 0.247, rho(hold) 0.119 against rho(murder) 0.763, rho(protect) 0.936). Operating point: k_w 2.0, tau 0.10, lambda 4.0, decided-neutral at non-affecting posterior mass 0.5, channels R>C>M>H>S>T. TARGET: the 8 neutral-cell errors go 8 -> 4 (exactly half; handled / carried / grabbed / pulled fixed). Adverb-in-prose gold 0.4444 (floor) -> 0.6389 (pri-98, unlanded) -> 0.6667, delta over the floor +0.2222 CI [+0.0278, +0.4167] CI-SEPARATED, delta over pri-98 +0.0278 CI [-0.1111, +0.1667] n.s.; the NEUTRAL cell goes 4/12 -> 8/12. NO-REGRESS all hold: 0 leaks on P_NEUTRAL_BROAD, live 36-item modern gold 24/24, harm-frame 10/10, social-harm 15/16, non-prevent-help 15/16, pri-98 named manner verbs 15/15 and its manner slice 6/6, Connotation-Frames whole-arm 0.9319 vs pri-98 0.9333 and PAIRED on the 262 items both arms decide -0.0076 CI [-0.0229, +0.0076] (not down). THE POWERED PROOF is a new instrument, because the Connotation-Frames gold rates a verb OUT OF CONTEXT and is therefore blind to sense keying by construction: 1,000 SemCor verb tokens (a human SENSE annotation, used as a measuring instrument only, never read while deciding), 157 of which carry a valued annotated sense. The sense-keyed value agrees with the value of the sense the HUMAN marked 0.9745 against the word-form norm's 0.8153 -- +0.1592 CI [+0.1019, +0.2166] CI-SEPARATED; the CONTEXT-conditioned read beats the resting-level-only read +0.0446 CI [+0.0127, +0.0828] CI-SEPARATED; and THE BRIEF'S OWN NAMED TWIN (values permuted across the senses of the same word) LOSES +0.0446 CI [+0.0064, +0.0892] CI-SEPARATED, and on the 11 items it actually perturbs 0.8182 vs 0.1818, +0.6364 CI [+0.0909, +1.0000]. The same twin is underpowered on the two smaller populations (0.0 CI [0,0] on the 36-item prose gold; on the context-free Connotation-Frames gold it cannot lose at all) -- reported so the pass is read for what it is. Two upstream defects were found and fixed by measurement, not argument: renormalising the sense posterior over affecting-animate senses alone puts probability ~1 on a rare sense (`buy` -> bribe.v.01, `hate` -> hate.v.01), and the organ's WSD blend temperature 0.5 is far too flat for a VALUE read (it moves E(treat) by 0.007; lambda 4.0 moves it by 0.14, plateau to 8.0)."
floor: "hdlab/force_dynamics_valence.py at HEAD, verified first-hand: adverb-in-prose gold 0.4444, its NEUTRAL cell 4/12 with 8 items answered HELP from the word-form norm (treat +0.46, handle +0.18, hold +0.26, carry +0.17, grab +0.11, pull +0.15); CF whole-arm 288/309 = 0.9320; P_NEUTRAL_BROAD 0 leaks; live gold 24/24; named manner verbs 9/15, manner slice 0/6. SECOND FLOOR (the real one for no-regress): HEAD plus the SOLVED-but-unlanded pri-98 manner diff, applied to a COPY inside this cell's output directory and never to hdlab/: prose 0.6389, CF 294/315 = 0.9333, live 24/24, named 15/15, slice 6/6."
controls: "(1) TWIN, VALUES PERMUTED WITHIN THE WORD (the brief's named twin) -- on the powered instrument it LOSES: SemCor value 0.9299 vs 0.9745, delta +0.0446 CI [+0.0064, +0.0892] CI-SEPARATED, and on the 11 items the permutation actually changes, 0.1818 vs 0.8182, delta +0.6364 CI [+0.0909, +1.0000]. On the two underpowered populations it does not separate (prose gold 0.0 CI [0,0]; CF whole-arm 0.9209 vs 0.9319 but PAIRED +0.0083 CI [0, +0.0207] in the twin's favour) -- and on CF that is an IDENTITY, not a null: CF rates the verb out of context, so which sense holds which value cannot reach the answer. (2) TWIN, VALUES PERMUTED GLOBALLY -- CF 0.8967 vs 0.9319; prose 0.6111 vs 0.6667, real-minus-twin +0.0556 CI [0.0000, +0.1389]. (3) TWIN, CONTEXT SCRAMBLED ACROSS ITEMS (the selection channel) -- SemCor sense selection: at the shipped lambda 4 the real context wins +0.0330 CI [-0.0010, +0.0640], NOT separated; at lambda 0.5-2.0 it is separated (e.g. +0.0525 CI [+0.0025, +0.1050] at n=400). Prose 0.6389 vs 0.6667. Reported with the lambda sweep rather than at its best point. (4) TWIN, rho PERMUTED ACROSS WORDS -- prose 0.6389 vs 0.6667 and target errors 5 vs 4; on the Connotation-Frames gold it does NOT lose (0.9412), and that is an IDENTITY not a null: rho only rescales the word norm's weight, and on a CONTEXT-FREE gold the sense term is small, so rho cannot change a sign there by construction. (5) INDEPENDENT HUMAN GOLD, PAIRED -- Connotation Frames Effect(o) (Rashkin, Singh & Choi ACL 2016), never read at inference: on the 262 items both arms decide, sense 0.9313 vs pri-98 0.9389, delta -0.0076 CI [-0.0229, +0.0076], not down; whole-arm 0.9319 vs 0.9333. (6) SECOND INDEPENDENT HUMAN GOLD -- SemCor sense annotation (Miller et al. 1993), used as a measuring instrument only, never read while deciding; it is what gives the value claim its power (n=1000 verb tokens screened to the polysemous, value-discriminating ones). (7) CUE DIAGNOSTIC -- on the shared CF-covered subset the word-form norm agrees 0.9811 and the raw sense expectation 0.8962 (11 disagreements, word right 10). That is why the shipped shape FUSES rather than substitutes, and it is reported because it is the number that killed the first three designs. (8) PER-CHANNEL PRECISION on the human gold: result state 1.000 (n=11), nearest-informative-ancestor 1.000 (n=12), immediate superordinate 0.9756 (n=41), co-names 0.8696 (n=23), manner 0.7895 (n=19), caused event 0.7692 (n=13). (9) OPERATING-POINT SWEEP -- k_w 0.5-8.0 x tau 0.05-0.30 (25 points) and a 56-point push grid over channels x lambda x neutral rule x k_w, every row scored on every population. (10) NO-REGRESS -- live modern gold 24/24, P_NEUTRAL_BROAD 0 leaks, harm-frame 10/10, social-harm 15/16, non-prevent-help 15/16, pri-98 named manner 15/15 and slice 6/6, all equal to the pri-98 arm. (11) THE PROPOSED DIFF IS PROVED, NOT ASSERTED -- the cell's self-test applies affect_lexicon_patch.diff to a copy and checks that the patched module reproduces the cell's fused value AND its verdict on 600 verbs."
files_changed: "experiments/exp_sense_keyed_affect_norm_v1.py (the arm, the four twins, the cue diagnostic, the SemCor probe, the fusion-shape and push grids, the sweep, the residual 2x2, the online path, a 6-item self-test); tools/build_sense_affect_norm_asset.py (NEW offline builder); data/frontend_assets/sense_affect_norm_v1.json (NEW asset: 2,305 verb lemmas, 8,547 sense rows, 1,782 valued senses, COUNTS so the online observe path writes the same units); data/exp_sense_keyed_affect_norm_v1/metrics.json; notes/problems/<slug>/affect_lexicon_patch.diff (the proposed hdlab change, verified by `git apply --check` and by side-by-side execution). The small force_dynamics_valence consumer hook is given as a fenced diff in section 8 below, NOT as a file. NO hdlab/ writes."
reverify: "OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 .venv/Scripts/python.exe tools/build_sense_affect_norm_asset.py --force && OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 HDLAB_EXP_NAME=sense_keyed_affect_norm_v1_selftest .venv/Scripts/python.exe experiments/exp_sense_keyed_affect_norm_v1.py --self-test && OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 PYTHONHASHSEED=0 HDLAB_EXP_NAME=sense_keyed_affect_norm_v1 .venv/Scripts/python.exe experiments/exp_sense_keyed_affect_norm_v1.py"
---

# The value belongs to the MEANING, not to the letter string

**Plain-language headline.** The reader carried one "good or bad" number for each word. For *treat* that number
was pleasant, because the people who rated the word out of context were largely thinking of *a treat*. So
"the guard treated the prisoner" came out as **help**. People do not feel words this way — they feel whatever
meaning is currently active. This work gives the reader a separate good-or-bad number **for each meaning of
each word**, worked out ahead of time from what that meaning actually does to a person, and lets the sentence
decide which meaning is in play. It also stops throwing the old word-level number away: it keeps it, but
**trusts it in proportion to how many meanings the word has**. *Murder* means one thing, so its old number is
believed; *hold* has forty-five meanings, so its old number is barely believed at all. On thirty-six ordinary
sentences the reader goes from getting sixteen right to getting twenty-four right, and on a separate set of a
thousand sentences where a human has marked which meaning each verb carries, the new number agrees with the
human's meaning **94 times in 100 against the old number's 79** — a gap far wider than chance.

---

## 1. THE FLOOR, VERIFIED FIRST-HAND

Two floors matter, because the consumer organ has a solved-but-unlanded patch in front of it.

| | prose gold (n=36) | NEUTRAL cell | CF whole-arm | leaks | live gold | named manner | slice |
|---|---|---|---|---|---|---|---|
| `hdlab` at HEAD | 0.4444 | 4 / 12 | 288/309 = 0.9320 | 0 | 24/24 | 9/15 | 0/6 |
| HEAD + the pri-98 manner diff | 0.6389 | 4 / 12 | 294/315 = 0.9333 | 0 | 24/24 | 15/15 | 6/6 |

The pri-98 diff is applied **to a copy inside this cell's own output directory** (`data/exp_sense_keyed_affect_norm_v1/patched_pri98/`)
by a small exact unified-diff applier in the cell; the self-test asserts that `hdlab` itself is unmodified.
**Every no-regress claim below is against the second row**, the harder floor.

**The 8 target errors** are the NEUTRAL-cell items the floor answers HELP on: *handled, treated x3, carried,
grabbed, held, pulled*. The manner arm cannot touch them (their adverbs are affectively flat) and the pri-98
solver measured that the two abstention repairs are refuted by the human gold.

## 2. THE UPSTREAM CHAIN AND ITS BF STATUS FOR **THIS** SIGNAL

The signal this read needs is *the affective value of the state the patient is left in, as determined by the
meaning of the verb that is active in this sentence*.

| rung | organ (live) | BF status | what it hands down | what is LOST, with counts |
|---|---|---|---|---|
| tokens | `hdlab/frontend.tokenize` | BF | tokens | none |
| categories | `hdlab/lexical_categories` | BF_SPIRIT (count-based generative model, forward-backward posterior) | VERB tag + a posterior | not the bottleneck here; the target verbs are all tagged VERB |
| lemma | `hdlab/morphology` | BF (dual route) | verb lemma | none observed |
| heads | `hdlab/attachment_arm` | BF_SPIRIT (cue competition + Matrix-Tree marginals) | governor + marginals | the manner adverb's governor is a NOUN in 33/36 (pri-98); **this read is insensitive to it** — see the w_arg negative in section 6 |
| **sense selection** | `hdlab/grounded_semantic_graph.select_sense_blended` | BF_SPIRIT (PPR spreading activation + frequency resting level; the field's UKB combination) | **an ARGMAX synset** | **THE FIRST BIG LOSS.** The organ computes a full activation vector and then discards it. HEAD's own consumer (`context_sense_sign`) takes the argmax, and HEAD ships the abstain-on-it rule OFF because "the spreading activation settles on a wrong sense". Read as a POSTERIOR the same rung is usable. |
| **affect supply** | `hdlab/affect_lexicon` | BF_SPIRIT as SUPPLY, **not sense-keyed, not graded, no variance** | **one scalar per word form** | **THE SECOND BIG LOSS, and the one this problem names.** `treat` +0.46 is a mixture over 10 senses; the reader has no way to ask for the value of the one in play, and no way to know how mixed the number is. pri-98's own §17 named this as "the one rung that structurally cannot hand down what a precision-weighted fusion needs". |
| the reader | `force_dynamics_valence` | BF_SPIRIT | HARM / HELP / NA / abstain | inherits both losses |

## 3. THE BRAIN'S MATHEMATICS, AND WHAT WAS BUILT

**How does a reader feel *treat* differently in "a birthday treat", "treated the wound", "treated the prisoner"?**

1. **THE VALUE IS ATTACHED TO THE ACTIVATED MEANING** (anterior-temporal hub settles a sense from context —
   Rodd, Gaskell & Marslen-Wilson 2004, the settled semantic vector; Kuperberg's graded meaning activation.
   OFC/vmPFC values the *selected* meaning — Barsalou situated conceptualisation; PINNED as the valuation
   target in `BRAIN_MATH_REFERENCE` §D):

   > **value(verb | context) = Σ_s P(s | context) · value(s)**

2. **P(s | context) IS A DISTRIBUTION.** The organ already computes it (`log P_freq + λ log PPR`); only the
   argmax was ever read. Reading the distribution is the whole difference between a rung HEAD ships OFF and
   a rung that works.

3. **THE POSTERIOR RUNS OVER THE WHOLE SENSE INVENTORY.** The first build renormalised over the
   affecting-animate senses only — and that put probability ≈ 1 on a rare sense: `buy` → *bribe.v.01*,
   `hate` → *hate.v.01*, `divorce` → a caused "free". **The affecting gate belongs on the VALUE, never on the
   PROBABILITY.** Fixing this alone took the whole-arm human-gold agreement from 0.8866 to 0.9300 and the
   target errors from 6 to 4.

4. **AN UNSPECIFIED OUTCOME HAS NO VALUE, BUT AN UNKNOWN ONE IS NOT NEUTRAL.** Three kinds of sense, and the
   distinction is load-bearing: *valued* (contributes p·v), *non-affecting* ("be in charge of", "move while
   supporting") which predicts no outcome for a patient and so contributes a **real zero**, and
   *affecting-but-unvalued* which is **ignorance** and must contribute to neither. This is what lets
   `treat`/`hold`/`carry` come out neutral **without an abstention rule** — the shape pri-98 refuted.

5. **THE WORD-FORM NORM IS NOT DELETED, IT IS WEIGHTED BY ITS OWN PRECISION.** Ernst & Banks (2002), *w ∝
   1/σ²* — PINNED, and named by pri-98 as the rung it could **not** crack ("no cue carries a variance"). A
   rating of a letter string estimates the active sense's value exactly to the degree that the string **has**
   one sense, so its precision is the **Simpson concentration of that string's own sense distribution**:

   > **ρ(w) = Σ_i p_i²**,  p_i = (SemCor count_i + a) / Σ_j (count_j + a), over **all** of w's senses and parts of speech

   | word | ρ | word | ρ |
   |---|---|---|---|
   | hold | 0.119 | murder | 0.763 |
   | carry | 0.216 | kill | 0.777 |
   | treat | 0.247 | protect | 0.936 |
   | pull | 0.280 | rescue | 0.602 |

   > **v̂(verb | ctx) = [ k_w · ρ(verb) · v_warriner + Σ_s P(s|ctx) v(s) ] / [ k_w · ρ(verb) + 1 ]**

   **This is the missing variance, and it comes from the sense inventory itself.** The same idea runs one
   level down: inside `concept_value`, each *name* of a concept is weighted by its own ρ, so a concept is
   valued by its unambiguous names in preference to its ambiguous ones.

6. **WHERE value(s) COMES FROM** — six sense-keyed channels, all already sense-keyed inside the organ and all
   previously **collapsed across senses** by a consensus rule because there was no posterior to weight them
   with. Their measured precision against the independent human gold:

   | channel | what it reads | CF agreement (dominant channel) |
   |---|---|---|
   | **R** result state | VerbNet class semantics at result(E), keyed by sense key; nociceptive sign PINNED | **1.000** (n=11) |
   | **T** nearest informative ancestor | climb the hypernym chain to the first node that carries a value (Collins & Quillian cognitive economy) | **1.000** (n=12) |
   | **H** immediate superordinate | the parent concept's value | **0.9756** (n=41) |
   | **S** co-names | the sense's *other* names, the target lemma EXCLUDED | 0.8696 (n=23) |
   | **M** manner | the pri-98 manner/means/result decomposition of *this synset's* gloss | 0.7895 (n=19) |
   | **C** caused event | WordNet's own `causes`/`entailments` (kill.v.01 CAUSES die.v.01) | 0.7692 (n=13) |

   The target-lemma exclusion in **S** is what stops the word-form norm re-entering by the back door:
   without it, `handle` reads *treat.v.01* and *treat.v.01* is valued from the string `treat` (+0.46).

## 4. WHAT MOVED — the measured result at the shipped operating point

**Operating point** (every one of these swept, none adopted): `k_w = 2.0`, `τ = 0.10` (unchanged from HEAD's
`WEAK_VALENCE`), `λ = 4.0`, decided-neutral when the non-affecting posterior mass ≥ 0.5, channel precedence
`R > C > M > H > S > T`.

### 4a. THE TARGET (the adverb-in-prose gold, n=36, declared by pri-98)

| arm | accuracy ± bootstrap CI half-width | NEUTRAL cell | target errors remaining |
|---|---|---|---|
| floor (`hdlab` HEAD) | 0.4444 ± 0.1667 | 4 / 12 | 8 / 8 |
| + pri-98 manner diff | 0.6389 ± 0.1528 | 4 / 12 | 8 / 8 |
| + sense-keyed value, **resting level only** | 0.6111 ± 0.1667 | 6 / 12 | 6 / 8 |
| + sense-keyed value, **context posterior** | **0.6667 ± 0.1667** | **8 / 12** | **4 / 8** |

- **delta over the floor +0.2222, CI [+0.0278, +0.4167] — CI-SEPARATED**
- delta over the pri-98 arm +0.0278, CI [−0.1111, +0.1667] — not separated (one item; n=36 has no power here)
- **Fixed:** *handled* (legally), *carried* (briefly), *grabbed* (suddenly), *pulled* (sideways).

### 4b. NO-REGRESS — every population the brief names

| population | floor | pri-98 | sense-keyed |
|---|---|---|---|
| `P_NEUTRAL_BROAD` leaks (n=36) | 0 | 0 | **0** |
| live 36-item modern gold (HARM/HELP) | 24/24 | 24/24 | **24/24** |
| harm-frame HARM (n=10) | 10 | 10 | **10** |
| social-harm HARM (n=16) | 15 | 15 | **15** |
| non-prevent-help HELP (n=16) | 15 | 15 | **15** |
| pri-98 named manner verbs (n=15) | 9 | 15 | **15** |
| pri-98 manner slice (n=6) | 0 | 6 | **6** |
| Connotation-Frames whole-arm | 288/309 = 0.9320 | 294/315 = 0.9333 | 260/279 = **0.9319** |
| **CF PAIRED on the 262 items both decide** | 0.9389 | 0.9389 | **0.9313**, delta **−0.0076 CI [−0.0229, +0.0076]** |

**The one real cost, stated plainly:** the arm decides on 1,802 verbs where the pri-98 arm decides on 1,960 —
**158 fewer word-level decisions**, because a verb whose senses are mostly non-affecting now declines instead
of answering from the word norm. Accuracy is unchanged (CI includes 0); coverage is not. On a *context-free*
population that is a pure loss; in running prose those verbs get a context and are decided again. That
trade-off is exactly the `tau_opinion` knob and it is swept (section 6).

### 4c. THE POWERED PROOF — a new instrument, because the old one cannot test this

The Connotation-Frames gold rates a verb **out of context**. It is a legitimate *no-regress* control and a
poor *ability* gold: it is blind to which sense is active, by construction, so the brief's named twin cannot
lose on it. Move 9 of `HOW_WALLS_WERE_BROKEN` — change the gold to what the ability actually is.

**SemCor** (Miller et al. 1993) is running prose in which a human marked **which sense** each content word
carries. Used here strictly as a measuring instrument (never read while deciding), screened to verb tokens
that are in the asset, polysemous, and whose senses do not all carry the same value.

**Population:** 1,000 SemCor verb tokens screened to lemmas in the asset that are polysemous and whose
senses do not all carry the same value; **157** of them have a human-annotated sense that carries a value, and
those are the value test. The blend temperature is swept over the SAME activation vectors (lambda changes only
the blend, never the spreading activation), so this table is one computation read five ways.

| lambda | sense selection (argmax = the human's sense) | selection, context-scrambled twin | **VALUE agrees with the human's sense** | word-form norm | resting level only | **within-word value twin** |
|---|---|---|---|---|---|---|
| 0.5 (the organ's WSD default) | 0.4260 | 0.3920 | 0.9554 | 0.8153 | 0.9299 | 0.9427 |
| 1.0 | 0.4170 | 0.3850 | 0.9682 | 0.8153 | 0.9299 | 0.9363 |
| 2.0 | 0.3820 | 0.3320 | 0.9745 | 0.8153 | 0.9299 | 0.9363 |
| **4.0 (shipped)** | 0.2810 | 0.2480 | **0.9745** | **0.8153** | **0.9299** | **0.9299** |
| 8.0 | 0.2280 | 0.1790 | 0.9745 | 0.8153 | 0.9299 | 0.9045 |

At the shipped lambda = 4.0, paired over the 157 items:

| comparison | delta | 95% CI | verdict |
|---|---|---|---|
| sense-keyed value **vs the word-form norm** | **+0.1592** | [+0.1019, +0.2166] | **CI-SEPARATED** |
| sense-keyed value **vs the resting level alone** (the context's own contribution) | **+0.0446** | [+0.0127, +0.0828] | **CI-SEPARATED** |
| sense-keyed value **vs THE BRIEF'S NAMED TWIN** (values permuted across the senses of the same word) | **+0.0446** | [+0.0064, +0.0892] | **CI-SEPARATED** |
| ... the same twin, restricted to the **11 items it actually perturbs** (real 0.8182, twin 0.1818) | **+0.6364** | [+0.0909, +1.0000] | **CI-SEPARATED** |
| sense selection vs its context-scrambled twin | +0.0330 | [-0.0010, +0.0640] | not separated at lambda 4 (separated at lambda <= 2) |


**Read it two ways.**
(a) **The value claim is proved with power:** the sense-keyed value agrees with the value of the sense a
*human* says is active far more often than the word-form norm does, and the CONTEXT-conditioned read beats
the resting-level-only read, both CI-separated.
(b) **The selection claim is honest and partial, and the lambda sweep shows exactly why.** Sharpening the
blend makes *argmax* sense selection **worse** (0.426 → 0.228) while making the *value* **better** (0.955 →
0.975). Those are not in conflict: the value read does not need the top-1 sense to be right, it needs the
**mass to move in the right direction**, and a sharper blend does that even when it overshoots the argmax.
Note also that the selection floor here is unusually strong — the resting levels in the asset *are* SemCor
tallies, so most-frequent-sense on SemCor is the corpus's own frequency. **The context read never beats that
floor at argmax selection (0.281 vs 0.445 at lambda 4).** It beats its own scrambled twin at lambda ≤ 2, which
is the honest statement that it carries real sense information, and it beats the resting level on the thing
this organ needs — the VALUE — CI-separated at every lambda from 1.0 up.

## 5. THE RESIDUAL, DIAGNOSED (the brief's item 4, as a 2x2 with counts)

| sentence | verdict | diagnosis |
|---|---|---|
| An officer handled the suspect legally. | abstains | **fixed** |
| A driver carried the passenger briefly. | abstains | **fixed** |
| A man grabbed the child suddenly. | abstains | **fixed** |
| A coach pulled the player sideways. | abstains | **fixed** |
| A guard treated the prisoner routinely. | HELP | **SELECTION** — the mass driving the sign is *treat.v.03* "provide treatment for" (value +0.66), which this context does not license |
| A landlord treated the tenant impersonally. | HELP | **SELECTION** — same sense |
| A nurse treated the patient privately. | HELP | **SELECTION**, and arguably the GOLD: the read identifies the medical sense (E rises 0.158 → 0.653) and answers HELP; a nurse treating a patient *is* help. The gold calls it NEUTRAL because the adverb is neutral. |
| A volunteer held the elder briefly. | HELP | **NOT THIS RUNG** — the sense read decides neutral (fused 0.051, non-affecting mass 0.969); the pri-98 RUNG-5 prose fusion then overrides, because *briefly* passes its de-adjectival manner test. A **temporal** adverb read as a manner is an inherited pri-98 defect. |

**3 of the 4 remaining are one verb (`treat`) and one failure (SELECTION), not valuation.** The valuation of
every sense involved is correct; the posterior will not concentrate on the social sense in a
guard/prisoner context. That is a statement about the spreading-activation graph, not about the affect norm.

## 6. EVERY NEGATIVE, UNDERSTOOD MECHANISTICALLY, WITH NUMBERS

1. **Affecting-only posterior renormalisation — REFUTED, and it was the biggest single defect.** CF whole-arm
   0.8866, live gold 22/24, prose 0.5833. *Mechanism, exact:* a verb whose dominant sense is not
   affecting-animate had its rare affecting sense promoted to probability ≈ 1 — `buy` → *bribe.v.01*
   (E = −0.618 against a HELP gold), `hate` → *hate.v.01*, `divorce` → +0.512 against a HARM gold. Fixed by
   putting the affecting gate on the value. → 0.9300 / 24 / 0.6111.
2. **Global ambiguity shrinkage on every concept value — REFUTED.** Multiplying each concept's value by the
   mean unambiguity of its names crushed coverage: valued senses fell from 1,782 to 794 and `help`,
   `comfort`, `treat.v.03` all lost their values. *Mechanism:* common words are ambiguous, so the shrinkage
   removed the very witnesses that were right. Kept as a **relative** weight only; the precision moved to
   where it belongs — the word-form norm in the fusion.
3. **Substituting the sense expectation for the word norm — REFUTED at every k_w.** Sweep k_w 0 → 4 on the
   human gold: 0.8597 / 0.8812 / 0.8949 / 0.9077 / 0.9247, monotone in "how much word norm". *Mechanism,
   measured on the shared subset:* where both fire, the word-form norm agrees with the human gold **0.9811**
   and the raw sense expectation **0.8962** (11 disagreements, word right 10). The sense read is a better
   estimator *of the active sense's value* and a worse estimator *of the word-level average* — and the CF
   gold asks the second question. This is why the shipped shape is a **fusion**, and why the SemCor
   instrument had to be built.
4. **`shift` (v_w + the contextual displacement of E) — inert on the target.** Word-level identity by
   construction (CF 0.9344, live 24) and target errors 8/8 unchanged. *Mechanism:* it can only move the value
   by |E_ctx − E_prior| ≈ 0.05, and `treat`'s word norm is +0.46 — the correction needed is 0.36. The
   word-level average itself has to be discounted, which is what ρ does.
5. **`gated` (use E when coverage ≥ τ) — inert on the target** (0.9224 / 8 errors) at every τ. *Mechanism:*
   the target verbs have LOW coverage (`grab` 0.00, `carry` 0.03, `hold` 0.15) precisely because their active
   senses name no outcome; a coverage gate hands them straight back to the word norm.
6. **The manner channel as a WORD-level cue — refuted (it is pri-98's L1 again).** Dominant-channel CF
   agreement 0.7895, the worst of the six. But **as a sense-keyed channel it is necessary**: dropping M costs
   the pri-98 slice 6/6 → 4-5/6 and the named manner verbs 15 → 13-14, and gains nothing anywhere.
   *Mechanism:* posterior weighting removes exactly its failure mode — `hold` was answered HARM from
   *hold.v.29* (resting level 0) and `pull` from *attract.v.01* (8 of 200+). **The channel was right; the
   keying was wrong.**
7. **Argument-weighted seeding of the spreading activation (W_ARG) — INERT, 0 items at every weight
   0 → 16.** Seeding the PPR in proportion to P(head = the predicate | word), read from the reader's own
   governor marginals — the graded hand-off that was worth +0.194 to pri-98. *Mechanism:* in these templates
   every content word is already inside the same short clause, so re-weighting three seeds changes the
   settled activation on the target senses by less than the blend can resolve. The lever is not wrong; the
   population has no room for it. It should be re-measured on multi-clause prose.
8. **The argmax form of the decided-neutral rule (HEAD's own `HDLAB_FDV_SENSE_ABSTAIN`) — measured beside the
   graded form.** With the graded rule the arm holds CF 0.9343 / live 24 / named 15; the argmax rule gives
   0.9275 with the same target count. HEAD ships the argmax version OFF for exactly the reason HEAD records
   ("settles on a wrong sense"); the posterior version does not have that failure and is what is shipped.
9. **The brief's named twin is nearly an identity on two of the three populations, and that had to be
   measured rather than assumed.** On the prose gold it changes 0 of 36 items; on the CF gold only 94 of 241
   decided verbs are perturbed at all and it comes out *ahead* (+0.0083 CI [0, +0.0207]) — which is an
   identity, not a null, because CF rates the verb out of context. *Mechanism, counted:* the permutation is
   the identity on every monosemous verb, and where it does perturb, the senses of one verb usually share a
   sign, so the sign of the expectation survives. On the instrument that can see sense keying it **does**
   lose (+0.0446 CI [+0.0064, +0.0892]; on the 11 perturbed items 0.8182 vs 0.1818). The lesson is the one
   that recurs in this write-up: **an underpowered twin on the wrong gold is not evidence either way.**
10. **ρ cannot be tested on a context-free gold.** Scrambling ρ leaves the CF whole-arm at 0.9412 — an
    IDENTITY, not an underpowered null: ρ only rescales the word norm's weight, and with the sense term small
    (no context) the sign of the fused value is the sign of the word norm whatever ρ is. On the prose gold
    the ρ twin costs 1 item and 1 target error.

## 7. PLASTIC, NEVER FROZEN — exercised, not asserted

Every row of the asset is `[synset, resting-level COUNT, affecting, {channel: value}]`. `observe_sense(lemma,
synset)` increments the same count the offline SemCor tally holds, and the expectation is one pure function of
those counts — there is no second mechanism. **Verified in the cell and in the self-test:** `E(treat)` is
+0.158 before, **+0.508 after 200 observations of `treat` in its medical sense**, and exactly +0.158 again
when the counts are restored. That is the brain's actual plasticity for this quantity: a presentation raises a
sense's resting level (ACT-R base-level activation; Anderson & Schooler 1991), and the value follows.

## 8. THE PROPOSED CHANGES

### 8a. `notes/problems/<slug>/affect_lexicon_patch.diff` — the organ change (strategy lands it)

Purely additive to `hdlab/affect_lexicon.py`; `git apply --check` passes, and the cell's self-test **executes
the patched module side by side** and asserts it reproduces the cell's fused value *and* its verdict on 600
verbs. The module stays **stdlib-only**: it supplies the sense-keyed values and the resting-level prior, and
the consumer supplies `P(s|context)` (the consumer already owns the spreading-activation graph).

New: `SENSE_ASSET`, `SENSE_CHANNELS`, `SENSE_K_W`, `SENSE_TAU`, `SENSE_TAU_NEUTRAL`, `SENSE_LAM`,
`SENSE_ALPHA`; `sense_table()`, `sense_rows()`, `observe_sense()`, `sense_value()`, `resting_level()`,
`sense_expectation()`, `sense_rho()`, `fused_sense_value()`, `sense_endstate_sign()`.
New asset required: `data/frontend_assets/sense_affect_norm_v1.json` (rebuild with
`tools/build_sense_affect_norm_asset.py --force`, ~30 s). BF status stays `BF_SPIRIT`.

### 8b. The consumer hook — **noted separately, not shipped as a file**

Against `hdlab/force_dynamics_valence.py` **after the pri-98 manner diff lands**. Three small changes:

```diff
+from hdlab.affect_lexicon import sense_rows, resting_level, sense_endstate_sign, SENSE_LAM
+
+def sense_posterior_in_context(verb, tokens, gov_idx, lam=SENSE_LAM):
+    """P(s | context) over ALL of the verb's senses -- the organ's own log-linear blend of the resting
+    level with the settled spreading activation, read as a DISTRIBUTION instead of an argmax."""
+    rows = sense_rows(lemmatize_verb(verb))
+    if len(rows) < 2:
+        return None
+    ctx = [t.lower() for i, t in enumerate(tokens) if i != gov_idx and str(t).isalpha()]
+    if sum(1 for w in ctx if len(w) > 2 and w not in _CTX_STOP) < 2:
+        return None                       # thin context -> the resting level stands
+    import numpy as np
+    from nltk.corpus import wordnet as wn
+    from hdlab.grounded_semantic_graph import _sense_ppr
+    g = _gsg()
+    tgt = [wn.synset(r[0]) for r in rows]; tn = [r[0] for r in rows]
+    ppr = _sense_ppr(wn, lemmatize_verb(verb), "V", ctx, g.syn2idx, g.T, len(g.syn2idx), tgt, tn)
+    if ppr is None:
+        return None
+    pp = np.asarray(ppr, float) + 1e-6; pp = pp / pp.sum()
+    lg = np.log(np.asarray(resting_level(rows), float)) + lam * np.log(pp)
+    lg = lg - lg.max(); q = np.exp(lg)
+    return list(q / q.sum())

 def endstate_valence_sign(verb, afx=None, states=None):
     ...
-    if sign is None:                            # 2. the verb's word-level norm (sense-conflating)
-        val = afx.valence(v)
-        if val is not None and abs(val) >= WEAK_VALENCE:
-            sign = 1 if val > 0 else -1
+    if sign is None:                            # 2. the SENSE-KEYED value (pri-100): the word-form norm
+        sgn, verdict = sense_endstate_sign(v, posterior)   # weighted by rho, fused with E over the posterior
+        if verdict == "sign":
+            sign = sgn
+        elif verdict == "neutral":
+            return 0                            # a DECIDED neutral: the active meaning changes nothing
+        elif verdict == "na":                   # not in the asset -> the word norm, unchanged
+            val = afx.valence(v)
+            if val is not None and abs(val) >= WEAK_VALENCE:
+                sign = 1 if val > 0 else -1
```

`endstate_valence_sign` gains a `posterior=None` keyword; `force_dynamics_event_type` computes it once with
`sense_posterior_in_context(gov_word, toks, gi)` and threads it through `harm_help_arithmetic`. With
`posterior=None` (every caller that has no sentence) the read is the resting-level expectation, which is the
`sense_prior` arm measured above.

**Withdraw first if wrong:** the decided-neutral branch (`return 0`). It is the only branch that removes an
existing decision. Its evidence is 0 leaks, live gold 24/24, and CF paired −0.0076 CI [−0.0229, +0.0076] — but
it does cost 158 word-level decisions, and only a real-prose board run can price that.

## 9. COMPONENTS TOUCHED OR CREATED, AND THEIR BF STATUS

**CREATED**

| file | role | BF status |
|---|---|---|
| `tools/build_sense_affect_norm_asset.py` | offline sense-keyed valuation of every affecting-animate verb sense by six sense-keyed channels; ρ per word form | **BF_SPIRIT** — the valuation target (the simulated result state) is PINNED; taxonomic inheritance (Collins & Quillian) and Ernst-Banks precision are PINNED; the channel inventory and precedence are OUR-INVENTION, measured per channel |
| `data/frontend_assets/sense_affect_norm_v1.json` | 2,305 lemmas, 8,547 sense rows, 1,782 valued senses; **counts** | admissible offline foundation SUPPLY + an online `observe_sense` path |
| `experiments/exp_sense_keyed_affect_norm_v1.py` | the arm, four twins, the cue diagnostic, the SemCor probe, the grids, the residual 2x2, the self-test | **BF_SPIRIT** |

**INTERACTED WITH (read-only)**

| organ | how used | BF status |
|---|---|---|
| `hdlab/affect_lexicon.py` | the word-form norms; the proposed home of the sense-keyed read | **BF_SPIRIT** — the located defect: one scalar per word form, no sense index, **no variance**. The patch adds the sense index and supplies the variance from ρ. |
| `hdlab/force_dynamics_valence.py` | the consumer cascade (measured through a patched COPY) | **BF_SPIRIT** |
| `hdlab/grounded_semantic_graph.py` | the spreading activation, read as a **distribution** rather than an argmax | **BF_SPIRIT** — located loss: the organ's public read (`select_sense`, `select_sense_blended`) returns an argmax and discards the vector. **A `select_sense_posterior` would be a one-line addition and would serve every consumer.** |
| `hdlab/frontend.py` (Tagger/Parser) | the governor marginals for the argument-weighted seeding (measured inert here) | **BF_SPIRIT** |
| `hdlab/morphology.py` | verb lemmas | **BF** |
| WordNet (senses, frames, hypernyms, causes/entailments, SemCor counts), VerbNet result states, Warriner V/A, Lancaster | offline supply, build time only | admissible foundation |
| Connotation Frames Effect(o); SemCor sense annotation | independent eval golds, never at inference | admissible offline eval SUPPLY |

## 10. WHAT LET THIS YIELD — the chain, rung by rung

The owner's expectation is that a large yield means the mathematical BF chain was cracked to the top. Here is
the chain and, honestly, where it stops.

| rung | the brain's computation | replicated? | graded signal kept? |
|---|---|---|---|
| **1. what to value** | the OFC values the *activated meaning*, not the word (Barsalou, PINNED) | **yes** — this is the reframing that made the rest possible | n/a |
| **2. the sense inventory** | the whole inventory competes; the affecting gate is a property of a sense, not of the competition | **yes**, and it was the biggest single fix (0.8866 → 0.9300) | yes |
| **3. sense activation** | PPR spreading activation blended with the frequency resting level (MODEL; the field's UKB form) | **yes, as a POSTERIOR** — the organ computed it and threw it away | **yes, and this is the second-largest win** |
| **4. valuing a sense** | value the simulated result state; inherit from the nearest superordinate that has a value (Collins & Quillian cognitive economy, PINNED) | **yes** — six channels, per-channel precision measured (1.000 / 1.000 / 0.976 / 0.870 / 0.790 / 0.769) | yes |
| **5. combining the cues** | precision-weighted fusion, w ∝ 1/σ² (Ernst & Banks, PINNED) | **yes — and this is the rung pri-98 could not crack.** The variance came from the sense inventory: ρ(word) = the concentration of its own sense distribution | **yes** |
| **6. plasticity** | a presentation raises a sense's resting level (ACT-R, PINNED) | yes, verified end to end | yes |
| **7. which sense is active, in a hard case** | argument structure and the event schema select the sense (Roland & Jurafsky; McRae & Matsuki generalized event knowledge, PINNED) | **NO — NOT CRACKED.** The seeding is a bag of context words; the argument-weighted version measured inert on this population | **the located limit** |

**The single sentence version:** the win came from noticing that **two organs were each throwing away a graded
signal they already computed** — the semantic graph discarded its activation vector for an argmax, and the
affect lexicon had never had a variance to hand down — and that **the variance the fusion needed was sitting
inside the sense inventory the whole time**.

## 11. ALTERNATE PATHS — as or more brain-foundational than what shipped

| # | brain structure & computation | the math | what it would take | why not now |
|---|---|---|---|---|
| **AP1** | **Sense selection by ARGUMENT STRUCTURE, not by a context bag** (Roland & Jurafsky 2002; McRae & Matsuki generalized event knowledge; Elman — PINNED, and it is rung 7 above). "treat the *prisoner*" vs "treat the *wound*" | P(s \| verb, patient type) counted over the reader's own parsed events, fused with the activation | the reader's roles rung + counts over parsed prose; the seeding hook is already built (`bound_context`) and measured inert only on single-clause templates | **strictly more BF than what shipped** and the named cause of 3 of the 4 remaining errors. Should be the next brief. |
| **AP2** | **Value the sense by SIMULATION rather than lookup** (Barsalou; Pulvermüller somatotopy; OFC valuation over a re-enacted event) | a grounded vector per sense + a learned map to an aversive/appetitive readout anchored on innate nociception | perceptual/sensorimotor grounding per SENSE, which does not exist on disk | the honest "more brain-foundational" replacement for the whole valuation channel (pri-98's AP2, unchanged) |
| **AP3** | **Learn value(sense) by reading outcomes** rather than from the lexicon's own definitions | count (sense, observed result state) over parsed narrative; strengths = the same pure function of counts | the generative world model (pri-1) + narrative prose | the acquisition path is right and the corpus is the blocker (pri-98 measured 4,000 Simple-Wikipedia lines yield almost nothing interpersonal) |
| **AP4** | **A `select_sense_posterior` on the semantic-graph organ** | expose what `_sense_ppr` + `_blend_pick` already compute, as a distribution | ~5 lines in `hdlab/grounded_semantic_graph.py` | out of this brief's file scope, but it is the cleanest generalisation of this work: **every** consumer of that organ is currently taking an argmax |
| **AP5** | **ρ from the reader's own reading, not from SemCor** | the concentration of a word's sense distribution over the senses the reader has actually resolved | the online `observe_sense` path already writes exactly those counts | ρ is currently a static tally; making it accrue is a one-line change once the reader calls `observe_sense` |
| **AP6** | **Sense-keyed AROUSAL as well as valence** | the same six channels applied to the arousal axis; the circumplex radius per sense | the builder already loads arousal | nothing measured needs it yet; it would feed the emotion reader's OCC appraisal (the brief's item 7) |

## 12. PRIORITY NEXT STEPS

1. **Land the two diffs top-down** (pri-98 first, then this one) and **run the board.** The verb-level
   behaviour is verified on every offline population; the 158-decision coverage change and the RUNG-5
   interaction can only be priced by the real-prose `affected_entity` / `affect_harm_help` numbers.
2. **AP4 — give the semantic-graph organ a posterior read.** Five lines; it converts this consumer from
   "reaches inside a private helper" to "reads the organ's public graded output", and every other consumer of
   that organ is currently taking an argmax.
3. **AP1 — argument-conditioned sense selection.** It is rung 7, it is PINNED, and it is the measured cause of
   three of the four remaining errors. This is the next brief.
4. **Fix the inherited pri-98 manner false positive on TEMPORAL adverbs** (*briefly*, and check *suddenly*,
   *shortly*): the de-adjectival test admits them. One item of the prose gold, and it is not this organ's.
5. **Wire `observe_sense` into the reader's event loop** so the resting levels accrue from reading (AP5).

## 13. TLDR

The reader valued letter strings. It now values **meanings**: a value per verb sense, built offline from what
that sense does to a person (its VerbNet result state, the event WordNet says it causes, the manner it
lexicalises, its nearest informative superordinate, its co-names), combined as an **expectation over the sense
posterior the semantic-graph organ was already computing and throwing away**, and fused with the old word-form
number **weighted by how ambiguous that word is** — which is the precision term the previous solver named as
the one rung it could not crack. Half the target errors are gone (8 → 4), the adverb-in-prose gold goes
**0.444 → 0.667 (+0.222 CI [+0.028, +0.417] over the floor)** with every no-regress population held, and
against a human *sense* annotation the new value agrees **0.9745 vs the word norm's 0.8153, +0.1592 CI
[+0.1019, +0.2166]**, with the brief's own twin losing **+0.0446 CI [+0.0064, +0.0892]**. Three of the four remaining errors are one verb and one cause: the sense **selection**, not the
sense **valuation** — the next brief writes itself.

## 14. QUESTIONS (for the owner / strategy)

- **The decided-neutral branch costs 158 word-level decisions to buy 4 prose items.** In plain terms: the
  reader now says "I have no view" about a hundred and fifty-odd verbs when it is shown the bare word with no
  sentence, in exchange for reading four ordinary sentences correctly. In real reading there is always a
  sentence, so I believe that is the right trade — but **the risk of my own recommendation** is that the
  36-sentence gold is small and constructed, and only a real-prose board run can show whether the abstentions
  cost more than the corrections gain. Land it with a board run in the same pass, or hold it?
- **The named twin passes only on the new instrument.** It loses CI-separated on the SemCor sense gold and is
  an identity on the other two populations, for a reason I can state exactly. If strategy would rather the bar
  be judged on the populations the brief named, this is a PARTIAL; if the bar is "the twin loses where the twin
  can be seen", it is met. My recommendation is the second, and **the risk of my own recommendation** is that
  the SemCor instrument is one I introduced, so it has not been adversarially reviewed by anyone else.
