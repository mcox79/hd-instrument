# DISAMBIGUATION FINDINGS — where the who-did-what signal is actually lost, and why the brief's route is dead

Cell: `experiments/exp_parser_gap_decomp_v1.py` (metrics `data/exp_parser_gap_decomp_v1/metrics.json`).
Reverify diagnostic: `.venv/Scripts/python.exe experiments/exp_parser_gap_decomp_v1.py --pops qa`.

## 1. THE DISK REFUTES THE BRIEF'S HEADLINE ROUTE (global structured-perceptron training)
- `data/exp_depparse_global_beam_earlyupdate_cpu_v1/metrics.json` = **HARD_FAIL**: GLOBAL beam + early-update
  UAS **0.809 vs LOCAL greedy 0.8109 (−0.0019)**. The earned bound printed in that cell: *"search does not help
  this feature set; the saturation is deeper than decode."* So the brief's INFERRED lever — "close the
  arc→spaCy UAS gap via the in-substrate arc-eager + GLOBAL-training infra" — is **already refuted on disk**.
  The ~0.81 in-substrate UAS ceiling is a REPRESENTATION/FEATURE gap the available glass-box search infra
  cannot cross. **The disk outranks the brief (README rule 1).**
- So a pure "raise UAS to spaCy's ~0.90 and let it transfer" is NOT available through the sanctioned route.

## 2. UAS LADDER on UD-EWT test (n=24120 arcs)
| parser | UAS gold-POS | UAS pred-POS (deployment) |
|---|---|---|
| **arc-eager transition (dynamic oracle)** | — | **0.8109 (dev, cited)** = best in-substrate |
| hashed (arc-factored) | 0.7907 | 0.7608 |
| **richfeat (arc-factored) — THE LIVE FRONTEND ASSET** | 0.7750 | **0.7440** |
| mst_retrain | 0.7385 | 0.7117 |
- The LIVE frontend loads `richfeat` (0.744 pred-POS) — yet `hashed` (0.761) is BETTER on test. A free swap.
- The POS tagger costs ~3 UAS points (gold-POS − pred-POS ≈ 0.031).
- **spaCy UAS-vs-UD-gold is NOT measurable here** (0.5697 is an annotation-SCHEME mismatch: en_core_web_sm is
  OntoNotes/CLEAR-style, not UD — do NOT quote it as spaCy being weak). The fair cross-parser comparison is the
  who-did-what task below, where spaCy wins.

## 3. WHO-DID-WHAT GAP DECOMPOSITION (QA-SRL science, FULL n=2423) — the crux
Same role-recovery rule swapped between LABELED (dobj/nsubjpass) and LABEL-FREE (head-attachment + POS + voice
+ position). A0=position floor; A5=gold-attach oracle.
| arm | FULL acc | HARD acc (n=1296) |
|---|---|---|
| A0 POS (position floor) | 0.3743 | 0.2708 |
| A1 FE_LABELED (= parent 0.515) | 0.5147 | 0.4529 |
| **A2 FE_LABELFREE** (frontend heads, NO labels) | **0.5444** | **0.5247** |
| A3 SP_LABELFREE (spaCy heads, NO labels) | 0.5724 | 0.5602 |
| A4 SP_LABELED (= parent 0.588) | 0.5877 | 0.5448 |
| A5 GOLD_ATTACH (oracle) | 0.9909 | 0.9907 |

Decomposition of the +0.073 total (paired bootstrap, 2000):
| component | Δ (FULL) | CI | reading |
|---|---|---|---|
| TOTAL gap (A4−A1) | **+0.0730** | [+0.060,+0.086] | frontend-labeled → spaCy-labeled |
| HEAD-ATTACH (A3−A2) | **+0.0281** | [+0.013,+0.043] | pure attachment quality (labels off both) |
| **FE labeler (A1−A2)** | **−0.0297** | [−0.041,−0.019], frac≤0=1.0 | **the arc_labeler is HARMFUL — label-free beats it** |
| SP labeler (A4−A3) | +0.0153 | [+0.007,+0.024] | spaCy's labels help (on FULL) |
| FE struct (A1−A0) | +0.1403 | [+0.126,+0.154] | even a weak parse beats position by +0.14 |

## 4. THE TWO LEVERS THIS EXPOSES (both deployable; both brain-faithful)
1. **DROP THE LABELER — recover roles LABEL-FREE (head-attachment + voice + position).** On the SAME live
   frontend heads this is **0.515 → 0.544 (+0.030 CI-sep)** on FULL and **0.453 → 0.525 (+0.072)** on HARD;
   spaCy's own labels even HURT on HARD (A4 0.545 < A3 0.560). This is the single biggest deployable who-did-
   what lever and needs NO retraining. It is exactly what CONSUMER_FIDELITY_MAP predicted: the brain binds
   THEMATIC roles (agent/patient) from structure + voice, not linguists' grammatical-relation LABELS
   (dobj/nsubj); `arc_labeler` is a LOW-fidelity OUR-INVENTION and here it is provably dead weight → actively
   harmful. **The disk confirmed the brain-foundational analysis before any build.**
2. **BETTER HEAD-ATTACHMENT (+0.028 headroom).** The available in-substrate gain is the **arc-eager incremental
   parser (0.81)** over the live arc-factored richfeat (0.744) — the brain-faithful INCREMENTAL shape
   (Now-or-Never) the audit named as the fix to arc_parser's two weaknesses (batch + UAS cap). Promote it to a
   loadable `parse()` operator emitting a CALIBRATED distribution (its uncalibrated margins today don't serve
   graded_competition/N7). The residual to spaCy is the representation/domain saturation §1 proved un-crossable
   by the sanctioned search infra → located negative + follow-on (GOLD target-domain parse data, not
   self-training which is refuted).

## 5. WHY THIS IS THE RIGHT (BRAIN-FAITHFUL) SOLUTION, NOT A UAS ARMS RACE
English who-did-what is word-order-DOMINANT (Competition Model, Bates & MacWhinney) — position floor already
0.374, and even an ORACLE object-decision only adds ~+0.028 on canonical (lineage). The parse matters on the
NON-CANONICAL / cross-domain slice. So the faithful shape is **position-dominant + cue-OVERRIDE with a
maintained distribution + drop-fill**, with the parse as ONE cue — NOT a super-accurate 1-best tree. That
shape also serves every consumer (calibrated distribution → graded_competition; incremental heads → the
builder; voice/position → the role binder; drop-fill → recall) and is robust across register where a sharper
modern 1-best parser is a NET LOSS on 19c. The build implements this; the multi-objective eval measures it
against the bar with twin/floor controls.
