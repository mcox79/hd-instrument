# Research: minimal brain-faithful LEARNED structural-objective fix after causal-objective-alone REFUTED (voice-invariant thematic role) — 2026-07-30

Scope: design-only drill. The prior spec's causal-objective hypothesis
(`brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`) is now
REFUTED BY MEASUREMENT: the new causal + hold-then-revise gate + clause-level head encoder,
trained to 18k lite steps, gives cross-voice agent/patient probe active->passive=0.017,
passive->active=0.000 (INVERTS by position) — statistically indistinguishable from the frozen
bidirectional MLM's 0.18/0.16 Broca's-profile. Raw geometry healthy (std 0.92, near-orthogonal):
this is a CONTENT problem, not a variance/collapse problem. Question: what genuinely different
structural TRAINING signal is minimal, brain-faithful, and self-supervisable from the synthetic
corpus.

Calibration per [[feedback-lit-scan-calibration-penalty]]: P deflated 0.15-0.25, novel-synthesis
capped 0.50, CITED@/REASONED@ tagged, ESTABLISHED/CONTESTED per claim. 4 parallel Sonnet
lit-scans this cycle (generic-terms-only per [[feedback-query-privacy-decomposition]]): structural
probes in causal LMs; contrastive paraphrase-invariance; auxiliary syntactic supervision;
neuroscience of position-invariant role assignment. Field advisor run (materials/inference/etc.
saturated — this drill is out-of-matrix, NL-encoder physics, correctly not scored by the HDC field
map). KB-check carried from dispatch (top cosine 0.29, no prior synthesis on "what structural
objective fixes this after causal-alone failed").

---

## HEADLINE

The causal-alone refutation was PREDICTABLE from the literature, and it pinpoints the fix.
Established ML probing shows a causal next-token objective **does** induce dependency-tree GEOMETRY
in hidden states (Hewitt-Manning 2019; GPT-2 recovers trees ~as well as BERT; Eisape 2022
incremental parse states) — but role information stays **POSITION-ENTANGLED and LEXICALLY SPECIFIC**
(Papadimitriou/Futrell/Mahowald 2022 "BERT doesn't care about word order except when it matters";
Petty/Wilson/Frank 2022 "position-role mappings" share across voice **but break on novel verbs";
Papadimitriou 2021 "Deep Subjecthood" — passive subjects are exactly the collapsing case). A
revision gate revises the PREDICTION; it never revises the GEOMETRY of the role representation, so
nothing in a predictive objective (causal or not, gated or not) applies pressure to make an entity's
representation the SAME across a voice change. Neuroscience names the missing operation precisely:
**role must be licensed at a STRUCTURAL SITE (the gap/head/arc) via morphosyntactic feature-checking,
not at a serial slot** — nominative=actor regardless of position (Bornkessel-Schlesewsky eADM);
role rides the ARC not the SLOT (Gibson DLT); and prediction vs structure-building are DISSOCIABLE
brain signals (Henderson 2016 syntactic surprisal drives LIFG beyond lexical surprisal; Ding 2016
grammar-dependent phrase entrainment). **A prediction objective cannot induce a structure the brain
uses a dissociable, non-predictive operation to compute — you must add a non-predictive structural
training pressure.** TOP RECOMMENDATION: a **token-level, role-DISCRIMINATIVE contrastive objective
across active/passive paraphrase pairs** — pull the same-referent argument's rep together across
voice, push the two arguments apart within a sentence — self-supervisable from the SYNTHETIC corpus
with ZERO external parser (we generate the pairs and know gold alignment), which sidesteps the two
walls that block this in general NLP (parser dependency + the Sachan 2021 silver-parse transfer
collapse). It directly optimizes the measured quantity (position-invariance of role) rather than
bracketing/structure that the encoder already has and that demonstrably does NOT confer voice-invariant
role.

---

## Part 1 — why causal-alone failed (diagnosis, CITED)

1. **Causal objective DOES give tree geometry.** Hewitt & Manning 2019 (NAACL) structural probe:
   a linear map recovers dependency-tree distance/depth from hidden states — ESTABLISHED. GPT-2
   (causal) recovers gold trees nearly as well as same-size BERT (Eisape 2022 Findings-EMNLP,
   incremental parse-state probing; non-linear GPT-2 probe arXiv:2402.16168). So the encoder having
   dependency structure is NOT the gap.
2. **But role is POSITION-ENTANGLED and LEXICALLY SPECIFIC — the actual gap.**
   - Papadimitriou, Futrell & Mahowald 2022 (ACL): grammatical-role classification becomes
     critically position-dependent for non-prototypical sentences ("the onion chopped the chef") —
     role rides position whenever lexical semantics don't disambiguate. ESTABLISHED. This IS our
     0.017/0.000 inversion in a published probe.
   - Petty, Wilson & Frank 2022 (arXiv:2202.03611) "Do Language Models Learn Position-Role
     Mappings?": models share theme/recipient mappings across active/passive **but generalization
     breaks with novel verbs** — lexical specificity, not abstract role. DIRECT precedent that our
     HELDOUT_VERBS bar is the hard part and the likely failure locus.
   - Papadimitriou 2021 (EACL) "Deep Subjecthood": in mBERT, passive subjects are the ambiguous,
     collapsing case. ESTABLISHED.
3. **Prediction != structure (dissociable in the brain).** Henderson et al. 2016 (NeuroImage):
   syntactic surprisal, with lexical surprisal/length/frequency regressed out, still drives left IFG
   + anterior temporal cortex — structural cost is NOT reducible to lexical prediction. Ding et al.
   2016 (Nat Neurosci): cortical phrase/sentence-rate entrainment appears only for listeners who know
   the grammar — internally-constructed hierarchy beyond acoustic/positional cues. Eye-movement
   dissociation (2024/25 preprint): forward reading ~ LM surprisal, rereading/backward saccades index
   structure-building. ESTABLISHED (localization CONTESTED — Matchin-Hickok 2020 place hierarchy in
   posterior temporal, not BA44). **Load-bearing inference (REASONED@):** if the brain computes role
   via an operation dissociable from prediction, then a predictive training objective — however
   staged — is the wrong pressure. This is why the gate did nothing: it acts on prediction error, and
   role-geometry is not what prediction error is about.
4. **Formal-expressivity corroboration (CONTESTED relevance).** Hahn 2020 (TACL) and successors:
   fixed-precision / hard-attention transformers cannot recognize bounded-depth hierarchy (Dyck)
   without positional/architectural aids — an argument that structural competence needs an added bias,
   not more prediction. Relevance is partial (our TinyTransformer has positional embeddings; the issue
   is entanglement, not raw expressivity) — flagged CONTESTED, not load-bearing.
5. **Scale is probably NOT the missing ingredient.** No cited work ties a voice-invariant-role phase
   transition to a small causal LM (grokking/emergent-syntax lit exists but none demonstrate this
   specific escape). Combined with (2)'s structural entanglement finding, "our 18k run was merely
   underpowered" is the LESS likely reading — the entanglement is a property of the objective, not of
   the step count. (Kept as a residual ambiguity in HARD-FAIL interpretation below.)

## Part 2 — the missing brain operation (biology, deeper than the prior spec)

The prior spec cited the staged-ERP models; this cycle names the actual computation. Three candidate
operations, all sharing one property — **they establish a non-adjacent structural link between a
displaced argument and the site where its role is licensed, so role rides the arc, not the slot:**

- **Movement / trace-binding** (Grodzinsky TDH; Chomsky Merge/minimalism). The passive subject is
  interpreted at a GAP it does not linearly occupy; a trace re-links filler -> canonical
  theta-position where the verb assigns role. Position-independent BY CONSTRUCTION. ESTABLISHED as
  theory; CONTESTED as a Broca's/BA44-specific operation vs domain-general WM holding the filler
  across the gap (Fiebach/Friederici; Matchin-Hickok).
- **Dependency-arc construction** (Gibson DLT 2000). The parser builds explicit head-dependent arcs;
  role is carried by the ARC connecting argument to head; arc length (not linear position) predicts
  difficulty. ESTABLISHED behaviorally.
- **Feature-checking / cue-competition** (Bornkessel-Schlesewsky eADM; Alday-Bornkessel computational
  model). Case, animacy, agreement, voice COMPETE to identify the actor verb-independently;
  morphosyntactic case assigns actor regardless of position (nominative = actor even non-initial).
  ESTABLISHED as model; exact cue-hierarchy CONTESTED.

Neural structure-beyond-prediction is established (Ding 2016; Pallier 2011 constituent-size BOLD in
IFG survives with pseudowords; Nelson 2017 intracranial phrase-closure; Zaccarella-Friederici 2015
minimal-Merge localization — the last CONTESTED vs Matchin-Hickok posterior-temporal account). No
binding-by-synchrony claim is load-bearing here (the synchrony-adjacent item, Ding entrainment, is an
established tracking signature whose oscillatory-vs-evoked mechanism is debated — flagged, not used).

**The one-sentence operation the objective lacks:** bind theta-role to a structural site (gap/head/arc)
via morphosyntactic feature-checking, invariant to serial position — an *acquired* competence
(developmental), which is why installing it as a learned training objective (not a hand-coded parser)
is the brain-faithful move.

## Part 3 — ranked structural-objective candidates

Ranked by (i) brain-fidelity, (ii) impl cost on the existing causal `TinyTransformer` cell,
(iii) self-supervisable from the SYNTHETIC corpus (no external parser) vs needs one.
The synthetic corpus is the decisive asset: **we generate active/passive paraphrase pairs with
controlled fillers and KNOW gold role + gold cross-voice alignment for free** — so options that
require a parser/treebank in general NLP become parser-free here, and the Sachan et al. 2021 (EACL)
silver-parse transfer collapse (syntax-augmentation gains vanish without GOLD parses on strong
encoders) does not bite (our labels are gold by construction).

**#1 (PRIMARY) — Token-level role-DISCRIMINATIVE contrastive across active/passive pairs.**
Mechanism (refined from the MEXMA/AMBER word-alignment family, ACL 2025 / Hu 2021, adapted
monolingual): for a generated pair {"the dog chased the cat", "the cat was chased by the dog"},
(a) PULL together the token/span reps of the same-referent argument across the two voices ("dog"_agent
in both); (b) PUSH APART the two different arguments WITHIN each sentence (agent vs patient). InfoNCE
term over the existing token latents.
- Brain-fidelity: HIGH-outcome / MEDIUM-mechanism. Directly implements feature-checking's OUTCOME
  (nominative=actor regardless of position) as a representational constraint; does NOT build the
  explicit arc/gap (mechanism-approximate). An acquired competence — matches the developmental framing.
- Cost: LOW. One InfoNCE loss term; NO architecture change; reuses existing token latents and the
  existing VICReg-style loss plumbing.
- Self-supervisable: YES, parser-free — synthetic generation supplies the pairs and alignment.
- Why #1: it targets the MEASURED quantity (position-invariance of role) directly. Options that induce
  bracketing/structure (below) give the encoder MORE of what it already has (Part 1.1) and which is
  proven NOT to confer voice-invariant role.
- CRITICAL RISK (must design against): the SimCSE collapse — contrastive invariance can be achieved by
  ERASING the who-did-what distinction (invariant but role-blind bag-of-words; documented for
  negation/argument-swap). The role-DISCRIMINATIVE within-sentence negative (b) is the mandatory
  anti-collapse term; it is what distinguishes this from a vanilla paraphrase-contrastive that would
  wash role out (SynCSE/DiffCSE lesson: sentence-level contrast is syntax-blind; token-level +
  discriminative is required).

**#2 (SECONDARY, complementary mechanism-faithful arm) — Dependency-head / argument-role prediction
auxiliary loss (LISA-style).** Supervise a head/attention module to predict each token's syntactic head
/ argument relation (Strubell et al. 2018 LISA: one attention head supervised to the syntactic parent;
+2.5-3.5 SRL F1, largest OOD gains — the one cited signal that injected structure GENERALIZES).
- Brain-fidelity: HIGH-mechanism (explicitly builds the dependency ARC — the actual brain operation).
- Cost: LOW-MED (one supervised head + relation labels, gold in synthetic corpus).
- Self-supervisable: YES here (gold heads from generation); [P] in general NLP.
- Why #2 not #1: LISA/StructBERT induce ARCS/structure, which per Part 1.1 the encoder already partly
  has; the Sachan wall warns structure-injection gains can be treebank-quality artifacts. Value here is
  as the MECHANISM-FAITHFUL control arm — if #1 passes but #2 fails, we learn role-invariance can be
  installed WITHOUT explicit arc-building; if both pass, arc-building is a viable second route. Bundle,
  don't sequence.

**#3 — Structural-probe-AS-a-loss (TreeReg, NAACL 2025).** Convert bracketing decisions into
differentiable orthogonality constraints on hidden states (+9.5 syntactic-generalization). Brain: builds
hierarchical bracketing (Merge). Cost LOW-MED. Self-sup: needs silver/gold trees ([P]; gold in synthetic).
Why #3: same "induces bracketing not role" limitation as #2, newer/single-group (CONTESTED-emerging);
strictly dominated by #2 for our target unless #2's supervised-head proves unstable.

**#4 — Constituency/bracketing self-supervised (ON-LSTM/PRPN/DIORA/StructFormer).** Induce hierarchy
from raw text, parser-free ([SS]). Brain: hierarchy. But induces BRACKETING, explicitly NOT thematic
role; and these are CONTESTED as reliable parsers (init-sensitive). Weakest for OUR specific target;
keep only if a fully-unsupervised route is later required.

**#5 — Agreement / case-marking prediction (Enguehard/Linzen CoNLL 2017).** Predict agreement/case as
[SS]-ish aux task; forces position-independent dependency tracking (Linzen 2016; Ravfogel Basque-case
2018). Brain: feature-checking (HIGH). BUT effect is MODEST in the lit, and English (likely our corpus)
has impoverished case — signal is weak unless we ADD explicit case marking to the synthetic corpus,
which risks changing the task into a trivially-solvable one (construction artifact). Deprioritized;
consider only as a cheap add-on regularizer to #1.

**Verdict:** PRIMARY = #1 (token-level role-discriminative contrastive across voice), because it
uniquely and directly optimizes the measured failure, is parser-free on the synthetic corpus, and is
the cheapest to add. BUNDLE #2 (dependency-head aux) as the mechanism-faithful control in the same
dispatch. #1 is outcome-faithful/mechanism-approximate; #2 is mechanism-faithful; running both isolates
whether voice-invariant role needs the explicit arc or just the representational constraint.

## Cheap decisive test (design-only; exp_dev owns pre-reg)

Smallest experiment that tells us whether #1 moves the cross-voice probe OFF inversion, WITHOUT
being a construction artifact:

- **Corpus (minimal):** N active/patient transitive templates -> generate matched active + passive
  paraphrase pairs with CONTROLLED fillers. Fillers must be varied so referent alignment CANNOT be
  solved by surface string identity alone (vary determiners/adjectives; include a pronominalized
  variant), else the model cheats via lexical match. Reserve a HELD-OUT split of NOVEL verbs AND novel
  filler nouns never seen in any contrastive pair (Petty 2022: this is where lexical-specificity
  breaks — it is the crux, not a nicety).
- **Arms:** (A) causal encoder + #1 contrastive objective; (B) causal encoder + #2 dep-head aux
  (mechanism-faithful control); (C) causal-alone (the already-MEASURED 0.017/0.000 baseline); plus
  standing floors (position-only 0.50, BoW 0.33, shuffled-label ~0.51 — unchanged, encoder-independent).
- **Readout:** the EXISTING `exp_syntactic_role_agent_patient_voice_probe_v1` cell (74d4ea0c1) via the
  ENCODER_ARM path-swap — zero new probe code — closed-form nearest-centroid, both directions, on
  HELD-OUT verbs+fillers.
- **Anti-collapse check (MANDATORY, new):** also report WITHIN-voice agent-vs-patient accuracy on the
  same held-out set. High cross-voice accuracy is only real if within-voice role separation is PRESERVED
  (>= ~0.85). If cross-voice looks high but within-voice separation collapsed toward chance, invariance
  was achieved by ERASURE (SimCSE bag-of-words) — that is a FAIL disguised as a pass.

## Falsifiable predictions (HARD-PASS / HARD-FAIL, pre-registered)

- **HARD-PASS:** active->passive AND passive->active cross-voice nearest-centroid role accuracy
  **>= 0.70 (both directions) on HELD-OUT verbs+fillers**, AND within-voice agent-vs-patient accuracy
  **>= 0.85** on the same held-out set (anti-collapse gate). Ideal target approaches within-voice
  ~0.85-0.90. (Aligns with the existing cell's ROLE_PROBE_PASS_MIN=0.70.)
- **HARD-FAIL:** either cross-voice direction **<= 0.55** on held-out (no better than position-only/
  chance, i.e. still inverted or role-blind), OR improvement appears ONLY on TRAINED verbs/fillers while
  held-out stays <= 0.55 (memorization, the Petty-2022 signature), OR within-voice separation collapses
  below ~0.65 (bag-of-words erasure) even if cross-voice reads high.
- **PARTIAL / MIDDLE (report explicitly, do not force into binary):** held-out cross-voice lands in
  [0.55, 0.70] with within-voice separation preserved — no longer inverted, genuinely reading some
  position-invariant role, but not yet at the bar. This is the program's recurring first-attempt
  objective-lever outcome and is INFORMATIVE (rules the direction in, motivates scale/curriculum).

**Construction-artifact flags (what would make a PASS fake):**
1. Pass on trained verbs/fillers only, held-out fails -> memorization (Petty 2022). The held-out-verb
   split is the ONLY valid pass surface.
2. High cross-voice, collapsed within-voice separation -> bag-of-words erasure (SimCSE). The
   within-voice gate catches it.
3. Referent alignment solvable by surface string identity (same filler tokens in same case) -> the
   contrastive positive is trivial; filler-variation + pronominal variants are mandatory controls.
4. If arm (B) dep-head-aux ALSO passes identically, check the aux labels aren't leaking the answer via
   a degenerate head that just encodes linear position.

## P estimate (deflated)

**P_deflated(HARD-PASS on held-out) = 0.30.** Base REASONED@ ~0.45 (this objective DIRECTLY optimizes
the measured quantity, is parser-free on the synthetic corpus removing the two general-NLP walls, and
maps to an established brain OUTCOME — feature-checking position-invariance) minus 0.15 lit-calibration
penalty. The penalty is moderate not maximal because there IS supporting mechanism precedent
(word-alignment contrastive genuinely aligns same-referent tokens across constructions; token-level +
discriminative demonstrably beats sentence-level), but is not zero because (a) Petty 2022 is a DIRECT
warning that held-out-verb generalization breaks even when role-mapping is present, (b) no published
precedent clears a held-out-verb voice-invariant role probe via contrastive alone, (c) the
construction-artifact surface is large for a contrastive objective on gold synthetic pairs. Below the
0.50 novel-synthesis cap. **MIDDLE/PARTIAL (off-inversion, held-out in [0.55,0.70]) assessed MORE
likely than HARD-PASS, P~0.40** — the more probable and still-valuable outcome (direction confirmed,
scale/curriculum the follow-up). A HARD-FAIL remains genuinely ambiguous between "contrastive-invariance
wrong" and "right direction, insufficient scale/corpus-diversity" (Part 1.5) and must be reported as
such, not as clean refutation.

## Cross-thread synthesis

- Directly answers the REFUTATION of
  `brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`: the causal +
  gate + clause-head design changed the OBJECTIVE's temporal structure but added no NON-PREDICTIVE
  structural pressure; the lit (Henderson 2016 prediction/structure dissociation; Papadimitriou 2022
  position-entanglement) explains why that could not have worked and names the pressure that is missing.
- Supersedes the prior spec's implicit assumption that a predictive objective plus a revision gate is
  sufficient; the gate acts on prediction error, not on role-geometry.
- Reuses the same fair-test cell (74d4ea0c1) and ENCODER_ARM path-swap pattern, and the same
  (seed,arm) checkpoint discipline and OOM-safe latent-only head, verbatim — this is an added LOSS TERM
  on the existing causal cell, not a new model class.
- Complements the binding audit (`brain_fidelity_audit_native_binding_comprehension_2026-07-30.md`):
  that audit flagged READING roles off syntax as the genuine untested gap upstream of binding; this note
  supplies the specific structural training signal for that upstream gap. Contested binding-by-synchrony
  is NOT re-litigated (not load-bearing here).
- Consistent with the standing anti-pattern discipline: the contrastive/aux objectives shape the
  encoder's OWN representations at TRAINING time (acquired competence); inference needs NO parser and NO
  bolt-on reader. Parser-at-train (for #2's gold heads) is distinct from and does not touch the forbidden
  parser-at-inference pattern — and on the synthetic corpus even that is unnecessary (gold by generation).

## Substrate-product implications

Voice-invariant thematic-role reading is the product-relevant line between "the substrate slot-fills
when TOLD who the agent is" and "the substrate figures out who the agent is from grammar alone" — the
difference between a templated-composition demo and a real comprehension capability
(`WHERE_WE_ARE_NOW.md` honest gap). This route keeps the from-scratch, glass-box, no-external-LLM,
no-borrowed-embedding, no-bolt-on-parser invariants: the fix is a native learned training objective on
the encoder's own latents. Even a MIDDLE-band result unblocks the direction; a HARD-PASS would be the
first measured voice-invariant role-reading capability in the substrate.

## Anchor candidates for pickup (ranked; exp_dev owns pre-reg — no inline experiment design)

1. **PRIMARY** — add the token-level role-discriminative contrastive-across-voice loss term (Part 3 #1)
   to the existing causal `exp_encoder_latent_pc_arc_v1` cell; generate the minimal active/passive
   paraphrase-pair corpus with filler-variation + held-out novel-verb/filler split; fair-test via the
   existing `exp_syntactic_role_agent_patient_voice_probe_v1` (74d4ea0c1) ENCODER_ARM path-swap;
   ADD the mandatory within-voice anti-collapse readout. Carry the three death-fixes (data-prep
   single-pass+heartbeat+smoke gate; OOM latent-only tripwire; (seed,arm) checkpointing) verbatim.
   Why now: directly targets the just-measured 0.017/0.000 wall with the cheapest added loss term and
   zero new probe code.
2. **SECONDARY (bundle same dispatch)** — dependency-head/argument-role auxiliary arm (Part 3 #2) as the
   mechanism-faithful control; near-zero marginal cost (same corpus, same (seed,arm) matrix); isolates
   whether voice-invariant role needs explicit arc-building or just the representational constraint.
3. **TERTIARY (only if #1/#2 land PASS/PARTIAL)** — cheap case/agreement aux regularizer (Part 3 #5)
   layered on the winner, and a scale/curriculum follow-up to disambiguate a HARD-FAIL's
   objective-wrong-vs-underpowered ambiguity (Part 1.5).

Context pointers: `experiments/exp_syntactic_role_agent_patient_voice_probe_v1.py` + its metrics.json;
`experiments/exp_encoder_latent_pc_arc_v1.py`;
`notes/brain_syntax_to_role_mechanism_and_forward_predictive_encoder_spec_2026-07-30.md`;
`notes/brain_fidelity_audit_native_binding_comprehension_2026-07-30.md`;
`hdlab/slot_attention_wm.py`; `notes/WHERE_WE_ARE_NOW.md` ("THE ENCODER WALL").

## Citations (verified count)

CITED@ this cycle (4 parallel generic-term lit-scans, query-privacy compliant; all verified against
ACL Anthology / arXiv / journal listings):
Structural-probe/causal-syntax thread — Hewitt & Manning 2019 (NAACL, structural probe); Eisape et al.
2022 (Findings-EMNLP, incremental parse states); GPT-2 non-linear probe (arXiv:2402.16168); Marvin &
Linzen 2018 (EMNLP); Futrell/Wilcox et al. 2019-2020 (structural supervision); Papadimitriou/Futrell/
Mahowald 2022 (ACL, "word order except when it matters"); Petty/Wilson/Frank 2022 (arXiv:2202.03611,
position-role mappings break on novel verbs); Papadimitriou 2021 (EACL, Deep Subjecthood); Hahn 2020
(TACL) + Merrill/Sabharwal formal-expressivity.
Contrastive/invariance thread — Gao/Yao/Chen 2021 (SimCSE, EMNLP); Chuang et al. 2022 (DiffCSE, NAACL);
SynCSE 2025; Gildea & Jurafsky 2002 + He et al. 2019 (SRL); Proietti et al. 2022 (COLING, BERT proto-
roles); Janeiro et al. 2025 (MEXMA, ACL); Hu et al. 2021 (AMBER word alignment); Chi et al. 2021 (NAACL
self-labeled alignment).
Auxiliary-supervision thread — Strubell et al. 2018 (LISA, EMNLP); Wang et al. 2020 (StructBERT, ICLR);
Bai et al. 2021 (Syntax-BERT, ACL); TreeReg 2025 (NAACL, tree regularization); Shen et al. 2018/2019
(PRPN, ON-LSTM); Drozdov et al. 2019 (DIORA); Shen et al. 2021 (StructFormer); Kim et al. 2019 (URNNG);
Enguehard/Goldberg/Linzen 2017 (CoNLL, multi-task agreement); Linzen/Dupoux/Goldberg 2016; Ravfogel et
al. 2018 (case); Sachan et al. 2021 (EACL, skeptical silver-parse transfer wall).
Neuroscience thread — Grodzinsky 2000 (TDH); Gibson 2000 (DLT); Bornkessel-Schlesewsky & Schlesewsky
(eADM) + Alday-Bornkessel computational model; Ding et al. 2016 (Nat Neurosci, entrainment); Pallier et
al. 2011; Nelson et al. 2017; Zaccarella & Friederici 2015 (Merge localization, CONTESTED); Matchin &
Hickok 2020 (posterior-temporal counter, CONTESTED); Henderson et al. 2016 (NeuroImage, syntactic
surprisal dissociation); eye-movement dissociation preprint 2024/25.
**Verified count this cycle: ~40 distinct works across 4 threads.** ESTABLISHED/CONTESTED flagged
per-claim throughout; every Part 3 recommendation tagged CITED@ (underlying finding) or REASONED@
(transfer to this design), with the REASONED@ transfer (contrastive voice-invariance clears a held-out
role probe) explicitly the weakest link and the driver of the P_deflated cap.
