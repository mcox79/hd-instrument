# PARSER SERVICE SPEC — what ONE parser must provide to serve ALL brain-foundational consumers

Owner (2026-09-02): *"we need to understand what all the components need, brain-foundationally, so this parser
serves them all. can we determine that precisely?"* **YES — determined precisely below, by reading every
component's solver submission + code and measuring the head-dependence directly.**

## PER-COMPONENT REQUIREMENT (exact parse signal consumed; head-dependence measured, not assumed)
| # | component (brain mechanism) | EXACT parse signal it consumes | head-dependent? | threshold / evidence |
|---|---|---|---|---|
| 1 | **extraction event detector** (neo-Davidsonian event-hood) | **POS only** (UPOS==VERB, tense-agnostic) | NO | recall 0.33→0.95; precision residual wants argument-structure gate (needs heads@higherUAS + a `cop` label) |
| 2 | **graded_role_assigner** (Competition-Model who-did-what) | **POSITION + VOICE**; candidates from POS | **NO — head-independent** (measured: gold-heads don't move it; witness invariant to permuting arcs) | patient organ 0.541/0.411; parse ties the gold parse on who-did-what (−0.005 NS) |
| 3 | **relcl_resolver / predict_revise** (active-filler filler-gap + drop-fill) | **POS + relativizers + VOICE + POSITION** | **NO — takes no heads; the arc parser is HARMFUL here** (0.198 < info-free 0.305) | INC 0.953 vs 0.499; needs the parser to **EXPOSE its DROPS** (leave patient empty), not confabulate |
| 4 | **predicate_argument_frontend** (structure+role pools; PP/oblique roles) | **1-best HEADS — specifically the PP-CHAIN** (ADP→object→verb, `_attaches_to_verb`) + POS + LEMMA + VOICE | **PARTLY — agent/theme head-INDEP (position); PP/spatial roles head-DEP** | **the one measured parse CEILING:** oracle-PP recovers path +0.177, location +0.103, source +0.096 |
| 5 | **verb_subcat** (lexical argument structure) | **LEMMA** (wired gate); graded gate adds POS + patient-index + VOICE | NO (lemma-only) | AUC 0.72→0.777; residual wants PP-attachment (argument vs adjunct) + a `obj`/`obl` label |
| 6 | **predictive_reader** (N400 forward prediction) | **LEMMA + POS + the role-binder's committed event** | NO (event-level) | its own residual = STRUCTURAL parse-coverage failures it cannot flag → "the only lever is a better parser (recall)" |
| 7 | **graded_competition** (maintained distribution) | **abstract cue SUPPORT arrays** the caller builds from heads/order/recency | NO — **builds its own distribution**; MAP theorem ⇒ drop-in on 1-best | needs a per-candidate STRUCTURAL score, NOT a parser posterior; the only usable graded parser output = the per-arc MARGIN (emitted, **unused**) |
| 8 | **world_state_register** (event-indexing situation model) | inherits the reader wire: **LEMMA + AGENT/PATIENT (position) + ARG2 recipient/source (PP-chain)** | PARTLY (ARG2 = PP-chain) | register core parse-independent (1.000); live payoff capped by **COREF**, not attachment |
| 9 | **pos_tagger** | (produces POS — the root, not a consumer) | — | its UPOS accuracy is the universal floor below |

## THE SYNTHESIS — the parser must provide exactly FOUR things, and ONE behavior
**LOAD-BEARING (provide accurately):**
1. **UPOS — the UNIVERSAL floor.** Every component + every upstream extractor keys off it; tagger noise directly
   caps them (relcl real-text precision falls to 0.40 from mistags; 71% of predict_revise's extraction-misses
   are verbs mis-tagged as nouns; the 19c who-did-what verb-ID drop was −0.10). **This is the single biggest
   shared lever.**
2. **VERB LEMMA** — predarg (VerbNet class), world_state (operator), verb_subcat (gate), predictive_reader (key).
3. **VOICE (passive)** — every role component (computed from aux-BE + past-participle over POS, not a label).
4. **1-best PP-CHAIN attachment (ADP→object→verb)** — the SOLE high-precision, parse-quality-sensitive head
   signal, and the ONLY measured parse CEILING (oracle-PP +0.10 to +0.18 on spatial/transfer/recipient roles).
   **This is what a BETTER PARSER actually buys.**

**ONE BEHAVIOR (not accuracy — calibration):**
5. **EXPOSE DROPS, don't confabulate.** relcl/predict_revise need the parser to LEAVE the patient empty when
   uncertain (a coverage drop the drop-fill can then repair) rather than over-commit a wrong bind. This is
   abstention behavior, and it is why the per-arc MARGIN (currently emitted-but-unused) is the right signal to
   wire — as an abstain gate, NOT as an accuracy lever.

**NOT NEEDED (measured, so we stop chasing them):**
- **General head-accuracy for who-did-what (agent/patient)** — POSITION-driven, head-INDEPENDENT. The core
  who-did-what barely moves with parse quality (this is why raising UAS did not lift the patient decision). The
  parser earns its keep on PP-attachment, not on who-did-what heads.
- **Dependency-relation LABELS** — roles come from position + preposition-telicity + verb-class, never a label;
  the arc_labeler's labels are measured HARMFUL for the patient decision. **EXCEPTION (a minority precision
  residual, not a core need):** verb_subcat's argument/adjunct gate and the detector's copular gate WANT `obj`/
  `obl`/`cop` labels — worth a targeted labeler for THOSE gates only, never for role recovery.
- **An n-best / graded parse DISTRIBUTION** — NO component needs one. graded_competition builds its own from
  1-best; predict_revise tested a distribution trigger and it added nothing. The only graded parser output any
  consumer can use is the per-arc MARGIN, and only as an abstain gate (behavior 5).

## THE REFRAME THIS FORCES (and its coherence with the 19c wall)
The parser's brain-foundational value is **NOT "raise who-did-what UAS"** — that is position-driven and
parse-robust. It is: **(a) accurate UPOS, (b) accurate PP-CHAIN attachment, (c) well-calibrated abstention.**
This is COHERENT with the 19c disambiguation: the 19c who-did-what failures were **93% PP-embedding** — i.e. the
19c wall IS the PP-attachment signal (goal is a preposition's object ~9 tokens out). So the single parser lever —
PP-attachment — simultaneously serves predarg's spatial roles, world_state's recipient/source, verb_subcat's
argument/adjunct residual, AND the 19c who-did-what. The rich-structural parser already helps PP-reachability
(70% vs 68%); register-native parse training would raise it further; that is the genuine, multi-consumer,
brain-foundational parser optimization.

## DESIGN TARGET FOR "ONE PARSER THAT SERVES THEM ALL"
A glass-box incremental parser that: (1) emits accurate **UPOS + lemma** (the universal floor — invest here
first, it caps everything and it degrades most on register); (2) is optimized for **PP-CHAIN attachment
accuracy** (the sole high-precision head demand and the sole measured ceiling), NOT global UAS; (3) emits a
**calibrated abstain/drop signal** (expose coverage gaps for drop-fill; the margin, calibrated); (4) OPTIONALLY
supplies `obj`/`obl`/`cop` labels for the two argument-structure precision gates only. It does NOT need general
who-did-what head-accuracy, full dependency labeling, or an n-best distribution. **This is the precise, complete,
brain-foundational service contract.**
