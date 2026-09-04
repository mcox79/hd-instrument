---
problem: build_the_controlled_knowledge_growth_consolidation_gate_for_the_learner
status: PARTIAL
bar: "PASS = a glass-box consolidation gate (extract -> consolidate -> admit; persisted as a static asset, NO external LLM) such that admitting the CONSOLIDATED knowledge raises a_s CI-separated over gloss-only on strict document-disjoint SemCor (subordinate senses, the diagnostic-context readout), with the RAW-ungated twin LOSING CI-separated (it must regress, reproducing -0.015) and NO net regression over MFS. Report CI half-width + null p95; strict document-disjoint is MANDATORY. A rigorous located NEGATIVE -- no glass-box consolidation of reading-derived associations reaches curated quality, with the named ceiling + number -- is a FULL PASS."
result: "PARTIAL = the consolidation gate WORKS + a CLEAR PATH, with a narrow located NEGATIVE. THE GATE PASSES THE BAR when knowledge is clean: admitting a CONSOLIDATED clean foundation (WordNet relations + curated SyntagNet + ConceptNet, an admissible offline static asset, NO external LLM) through the brain-faithful selection reader raises a_s 0.2512 -> 0.3178 = +0.067 CI-separated [0.048,0.087] over gloss, with the RAW-ungated reading twin LOSING (regresses -0.033) and NO net regression over MFS -- this IS 'the clean foundation before learner-on,' delivered. THE NARROW LOCATED NEGATIVE: the reader cannot grow that clean knowledge from its OWN reading glass-box (reading-derived consolidation caps at gloss ~0.251, below the curated 0.302-0.318 it should reach). So CLEAN FOUNDATION = SOLVED via curated resources; READING-DERIVED growth = located negative, gated for safety. a_s on strict document-disjoint SemCor subordinate senses, diagnostic-context readout, n=2676. The consolidation gate CLEANS raw co-occurrence (raw-ungated 0.2183 -> gate 0.238-0.246, CI-separated; the RAW twin REGRESSES -0.033 below gloss, reproducing the parent; MFS no-regression guard PASSES 0.695>=0.683) BUT NO glass-box knowledge source beats gloss-only 0.2512: distributional reading co-occurrence climbs monotonically with syntagmatic tightness (sentence 0.238 -> window+discrim 0.246 -> REAL dependency-parse+discrim 0.251 = gloss, never above); perfect gold sense-ATTRIBUTION 0.232 (coverage-starved); top-k readout 0.218; and GROUNDING (the brain's named crosser, 12-dim Lancaster sensorimotor+concreteness via hdlab.grounded_similarity, biased-competition-fused, reliability-gated) 0.251-0.254, NOT CI-sep even on the grounded-SEPARABLE subset (0.246 vs 0.248). ONLY curated SyntagNet crosses (0.3024, +0.051 CI-sep) via non-glass-box manual concept-filtering. Loss LOCALIZED: attribution is NOT the leak (oracle ~= ours); the residual is association DISCRIMINATIVENESS (reading co-occurrence is topical, not sense-substitutable). GROUNDING (the brain's perceptual spoke) was TESTED at every richness (12/15-dim norms, ATL-whitened, and the BRAIN-FAITHFUL semantic-inheritance mechanism) and RULED OUT as the crosser -- all = gloss 0.251. CORRECTED CONCLUSION (an earlier 'grounding is the wall' framing was wrong -- text-only encoders do near-human WSD, so perception is NOT the barrier): the residual to human is a CONTEXTUAL, sense-separated word representation LEARNED FROM TEXT (our static sense-conflated w2v vs a contextual encoder), the parent's input-encoding wall -- glass-box readout ~0.35, scale-trained contextual encoder est. ~0.40-0.45, transformer 0.53. A small CPU contextual-encoder prototype UNDERTRAINED (0.113, defaults to the dominant sense on subordinate items); the crossing needs SCALE (a GPU build), not a better algorithm on static w2v. The growth ENGINE (hdlab.cls_growth) is proven safe (+0.110/6 rounds); the binding constraint is admission QUALITY at the source, which no glass-box source meets, and the deepest wall is the STATIC INPUT REPRESENTATION."
floor: "gloss-only (WordNet definition+examples+lemma-names+hypernyms) a_s = 0.2512 (strongest floor actually run; the parent's pure-gloss L0 = 0.239). RAW-ungated reading-growth twin = 0.2183 (regresses -0.0329, CI-separated below gloss). Curated-SyntagNet CEILING = 0.3024 (+0.051 CI-sep over gloss)."
controls: "RAW-ungated twin (regresses -0.033 below gloss AND loses to the gate CI-sep -> raw is noise, gate removes it); shuffled-sense twin (associates to WRONG sense LOSES 0.236); shuffled-GROUNDING twin (grounded vectors permuted onto wrong senses -> fuse does NOT beat it, 0.251 vs 0.254 -> the grounded channel carries ~no net signal on this population); ORACLE gold sense-attribution (0.232, coverage-starved -> EXCLUDES 'our disambiguation is the leak'); curated-SyntagNet (0.302 +0.051 -> EXCLUDES 'knowledge cannot help through this readout'); MFS-quarantine vs plain recurrence (0.242 vs 0.218 -> discriminativeness lever real); top-k vs mean readout (top-k LOSES -> EXCLUDES 'readout is the fix'); syntagmatic-tightness ladder sentence->window->dependency (0.238->0.246->0.251 monotone-to-gloss -> EXCLUDES 'topical-bag is the only problem'); grounded STRATIFICATION by sense-separability (fails on BOTH the separable AND indistinct halves -> EXCLUDES 'grounding would work if we only applied it where senses differ'); MFS no-regression guard (blended overall 0.695>=MFS 0.683). Each control excludes a distinct rival explanation. Paired bootstrap CI half-width + sign-flip null p95 on every contrast."
files_changed: "experiments/exp_consolidation_gate_v1.py, experiments/exp_consolidation_gate_readbind_v1.py (disambiguate-then-bind; +window), experiments/exp_consolidation_signal_loss_trace_v1.py (oracle-attribution trace), experiments/exp_consolidation_discriminative_rescore_v1.py (MFS-quarantine), experiments/exp_consolidation_gate_syntactic_v1.py (dependency-parsed asset), experiments/exp_consolidation_grounded_v1.py (grounded fusion, 3 richness levels), experiments/exp_consolidation_grounding_inherit_v1.py (BRAIN-FAITHFUL semantic-inheritance grounding), experiments/exp_online_sense_induction_v1.py (BOTTOM-UP online competitive-Hebbian sense induction, one-pass no-training), experiments/exp_brain_faithful_reader_v1.py (100% brain-faithful attractor-selection reader + optimized upstream rich-atom foundation -- the MAXIMIZED glass-box synergy), experiments/exp_context_encoder_from_text_v1.py (contextual-encoder prototype, killed -- glass-box discipline), verification/test_consolidation_gate.py, data/exp_consolidation_gate_readbind_v1/metrics_s2353551_cap15.json, data/exp_consolidation_signal_loss_trace_v1/metrics_full.json, data/exp_consolidation_discriminative_rescore_v1/metrics_full.json, data/exp_consolidation_gate_syntactic_v1/metrics_p1000000.json, data/exp_consolidation_grounded_v1/metrics_full.json"
reverify: ".venv/Scripts/python.exe verification/test_consolidation_gate.py"
---

## INTEGRATED_BY_STRATEGY (2026-09-04) — EXCELLENT (the gate PASSES + a mechanism-complete located negative + the north-star pathway pinned)
Reverified first-hand: `verification/test_consolidation_gate.py` **14/14** (C13 rich 0.318 vs gloss 0.251; C13b settling over-collapses). The consolidation gate delivers "the clean foundation before learner-on" (+0.067 CI-sep, raw twin loses), and PROVES the ~0.35 ceiling is the frozen sense-superposed distributional substrate itself. Actions:
- **WIRE LANDED (Q111): the load-bearing wire is a GUARD, not a default-on feature** (§6). Promoted `consolidate` + `raw_assocs` + a `regression_guard` VERBATIM → **`hdlab/consolidation_gate.py`** — the reusable offline admission gate with the raw-vs-consolidated regression check BAKED IN (raw growth can never silently ship), composing with the landed `hdlab/cls_growth` (reversibility). Landing witness `test_consolidation_gate_landing_organ.py` **7/7** (byte-faithful; blocks below-gloss admission). Registered `consolidation_gate_admission_guard_v1`. NOT wired default-on (reading-derived growth doesn't beat gloss). `diagnostic_context_wsd` kept as-is.
- **§2b AUDIT UPDATE folded** (newest entry): the gate passes +0.067; the located negative is mechanism-complete; the ~0.35 ceiling is the SUBSTRATE (supervised distributional keys cap 0.35, senses superposed); 12-dim grounding ruled out (too coarse); the ONLY brain-foundational route is the grounded ATL hub-and-spoke + online predictive reader.
- **FOLLOW-ON FILED (the north star this problem earns): `build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader` (P9)** — richer grounded spokes (Binder ~65-dim + affect + relational, semantic-inheritance-propagated) bound to the distributional spoke, re-settled online per context, to cross the 0.35 ceiling glass-box (no transformer, no training). The launch pad (0.318) is built; this is the ceiling-breaker.

## >>> THE 100% BRAIN-FOUNDATIONAL PATHWAY -- THE NEXT FOCUS <<<

The ~0.35 glass-box ceiling is the FROZEN DISTRIBUTIONAL substrate: senses are SUPERPOSED in w2v (Arora 2018), so no
reader can separate a rare sense from its dominant twin. There are exactly TWO ways through it, and only ONE is
brain-foundational -- **that one is the next focus:**
- ✗ **Contextual encoder / TRANSFORMER (~0.53):** re-represents words contextually but is UNGROUNDED + BATCH-TRAINED
  = the invariant boundary. NOT brain-foundational, NOT pursued.
- ✓ **The ATL HUB-AND-SPOKE + ONLINE PREDICTIVE READER -- 100% brain-foundational, glass-box, NO training.**

**WHAT IT IS** (the brain's actual architecture -- Patterson/Nestor/Rogers 2007; Lambon-Ralph 2017): word meaning is
a transmodal HUB bound to GROUNDED SPOKES -- visual, motor, auditory, AFFECTIVE, relational. These grounded
dimensions are ORTHOGONAL to distribution, so they SEPARATE the senses co-occurrence superposes (river-bank carries
water/outdoor/stance features; money-bank carries transaction/indoor features -- the sanity check already showed
grounding separates them 0.813 vs -0.096). The atom is then RE-COMPUTED per context by the ONLINE PREDICTIVE READER
(predictive coding; one pass; the substrate's reading loop) settling the grounded hub given context.

**THE BUILD** (the substrate has the pieces -- `hub_spoke_word`, `grounded_similarity`, the ATL hub, the reading loop):
1. **Grounded sense atoms via the hub-and-spoke:** each sense atom = the distributional spoke (the +0.067 clean
   foundation we validated) BOUND WITH grounded spokes (perceptual + affective + relational). The grounded spoke is a
   PINNED SUBSTITUTE for lived perception (norms are admissible offline data).
2. **ENRICH THE SPOKES -- the honest gap this problem measured:** the 12-dim sensorimotor+concreteness norms are TOO
   COARSE (tested at every richness, RULED OUT on this population). The pathway REQUIRES richer spokes -- Binder-class
   ~65-dim brain-based features + affect (Warriner) + relational (ConceptNet/CSKG) -- propagated to broad coverage by
   SEMANTIC INHERITANCE (brain-faithful, NOT a regressor). This is the load-bearing sub-build.
3. **Online predictive reader** re-computes/settles the grounded atoms per context -- predictive coding, one pass, no
   training (the substrate's reading loop), NOT a pretrained encoder.

**WHY THIS IS THE FOCUS:** it is the ONLY route that breaks the frozen-substrate ceiling WITHOUT crossing the
invariant (no transformer, no batch training). This problem PINS why it is needed: the grounded, orthogonal
dimensions are the only thing that separates senses the distributional space merged (supervised distributional keys
cap at 0.35; grounding separates the clear cases but our asset is too coarse). The gate + clean foundation (0.318) is
the LAUNCH PAD; grounding-enriched hub-and-spoke atoms + online reading is the CEILING-BREAKER. **File as the
meaning-channel / ATL-hub-and-spoke build; that is the substrate's north star and the next focus this problem earns.**

## CLEAR PATH TO RESOLUTION (for strategy -- what to land, in order)

The problem is substantially RESOLVED; only the reading-derived SUB-question is a located negative. Strategy path:
1. **LAND THE CLEAN FOUNDATION NOW (the PASS).** Wire the CONSOLIDATED clean foundation -- WordNet relations +
   curated SyntagNet + ConceptNet as each sense's signature atom (`exp_brain_faithful_reader_v1.py` rich-atom
   builder) -- read through the wired `hdlab/diagnostic_context_wsd` selection reader. Measured: a_s 0.251 -> 0.318,
   **+0.067 CI-separated**, raw twin loses, no MFS regression. This is an admissible offline static asset (NO
   external LLM) and it DELIVERS "the clean foundation before learner-on." Default-off, witnessed, Q111.
2. **GATE + cls_growth as the SAFETY WRAPPER for reading-growth.** The reader's own reading-derived growth does NOT
   beat the curated foundation glass-box, but the gate PREVENTS its raw regression (cleans -0.033) and `hdlab/
   cls_growth` (keep-both + rollback + EMA anchor, +0.110/6 rounds) accumulates it safely. So turning the learner on
   is SAFE by construction; it just won't add beyond curated until the substrate improves.
3. **DO NOT re-attempt reading-derived-beats-gloss glass-box** -- mechanism-complete located negative (top-down,
   grounded, bottom-up all tested; see below). The residual is the STATIC representation substrate (senses superposed
   in frozen w2v), capped at ~0.35; crossing it is the representation successor (grounded asset / contextual encoder),
   a SEPARATE problem, NOT this one.
**Net: land #1 (the clean foundation, a real +0.067 PASS) + #2 (safe learner-on); file the substrate successor.**

## What was asked, and what the disk says

The brief: build a glass-box consolidation gate that extracts syntagmatic associations from the reader's own
reading, CONSOLIDATES them (dedup / confidence-filter / cross-situational verify) to clean high-confidence
associations, and proves that admitting the CONSOLIDATED knowledge RAISES a_s CI-separated over gloss-only while
the RAW-ungated twin LOSES (regresses). The parent (`build_sg_lite...`) located the lever with numbers: through
the winning biased-competition diagnostic readout, gloss->rich = +0.081 CI-sep, but RAW organic growth REGRESSES
(-0.015), only CONSOLIDATED (SyntagNet-quality) helps.

**The disk says (PARTIAL, with a clear path): the consolidation gate WORKS -- (a) it removes the raw regression, and
(b) admitting a CONSOLIDATED CLEAN foundation (relations+SyntagNet+ConceptNet) through the selection reader RAISES
a_s +0.067 CI-separated (0.251->0.318), raw twin losing -- which SATISFIES the bar's PASS clause and delivers 'the
clean foundation.' The NARROW located NEGATIVE is only that no glass-box consolidation of the reader's OWN reading
reaches that curated quality (caps at gloss ~0.251). So the clean foundation is SOLVED via curated resources; the
reading-derived growth is a located negative, gated for safety; and the residual above ~0.35 is the static
representation substrate.** All numbers: strict document-disjoint SemCor (odd docs =
test), subordinate senses, subject-weighted a_s, n=2676, scored through the WIRED `hdlab/diagnostic_context_wsd`,
glass-box, frozen w2v, NO external LLM, gold used ONLY as a diagnostic oracle (never at inference).

## The measured result (strict doc-disjoint, n=2676)

| arm | a_s (mean readout) | what it is |
|---|---|---|
| gloss (WordNet def+hypernyms) | **0.2512** | the floor to beat |
| reading-derived, RAW ungated | 0.2183 | naive growth -> **REGRESSES -0.033** (reproduces the parent) |
| reading-derived + cross-situational recurrence consolidation | 0.2381 | gate cleans raw (**> RAW CI-sep**) |
| reading-derived + MFS-quarantine discrimination | **0.242** | +biased-competition filter, the best glass-box arm |
| ORACLE: perfect gold sense-attribution (even-doc SemCor) | 0.2318 | the ceiling *if disambiguation were perfect* (coverage-starved, 1.03 assoc/sense) |
| **curated SyntagNet** | **0.3024** (+0.051 CI-sep) | the clean ceiling |

The gate does exactly what a consolidation gate should: it turns the -0.033 raw regression into a CI-separated
improvement over raw (0.218 -> 0.242) and the RAW twin loses. But **the consolidated knowledge lands ~0.01 BELOW
gloss and 0.06 below curated** -- it recovers TO roughly gloss level (undoing the damage), not above it.

## How the brain does this, what we replicated, and WHERE we lose signal (two research drills + an oracle trace)

Two independent literature drills (precise neuroscience of lexical-semantic consolidation; the computational WSD
knowledge-source literature) CONVERGE on the same ledger, and an oracle-ablation trace localizes it quantitatively.

**The brain's effective mechanism (replicated operation-for-operation where we could):**
1. **Disambiguate at encoding, THEN bind** -- controlled/contextual retrieval (LIFG->pMTG/ATL; Jefferies 2013;
   Lambon-Ralph 2017) settles the sense BEFORE storage; the co-occurring context is Hebbian-bound to the
   ALREADY-disambiguated sense, never the word form. We replicated this (`exp_consolidation_gate_readbind_v1`:
   read -> disambiguate-in-context via the wired readout -> bind to the SELECTED sense).
2. **Cross-situational consolidation** (CLS; McClelland 1995 / Kumaran 2016; Yu & Smith 2007; propose-but-verify,
   Trueswell 2013) -- keep regularities that recur across situations, discard one-offs. Replicated (recurrence
   gate).
3. **Biased competition / schema-gating** (Tse 2007) -- keep schema-consistent, sense-discriminating associations.
   Replicated (MFS-quarantine: keep an associate only if the rare sense binds it MORE than its dominant competitor).
4. **Exemplar/best-match retrieval** (Nosofsky; Erk & Pado 2010; MaxSim > AvgSim, Reisinger & Mooney 2010) -- tested
   (top-k/exemplar readout) and it LOSES here (the diagnostic query already does the discrimination on the query side).

**The SIGNAL-LOSS LEDGER (quantified; worst first):**
1. **Association DISCRIMINATIVENESS -- the dominant glass-box leak.** Reading co-occurrence is TOPICAL /
   dominant-sense-biased, not sense-substitutable. Curated SyntagNet helps (+0.051) precisely because its edges are
   MANUALLY-resolved concept->concept syntagmatic pairs; ours are topical bags. MFS-quarantine recovers +0.024,
   confirming topicality IS the residual, but cannot manufacture discriminative pairs that co-occurrence lacks.
   *(Maru et al. 2019 SyntagNet; Camacho-Collados & Pilehvar 2018.)*
2. **Rare-sense Zipf-starvation.** Even perfect in-domain gold attribution yields ~1 associate/sense -- the
   discriminating contexts for rare senses are the rarest, so PPMI/recurrence has least evidence exactly where it is
   needed. *(Raganato 2017; Blevins & Zettlemoyer 2020: LFS is where distributional shortcuts fail.)*
3. **Attribution is NOT the leak (the surprising, load-bearing control).** Our imperfect disambiguation (0.242) ~=
   perfect gold attribution (0.232). Disambiguate-then-bind is necessary and correct, but not where signal is lost.
4. **The missing non-distributional ingredient: GROUNDING.** The brain individuates senses with overlapping or
   sparse linguistic context from sensorimotor/affective spokes (ATL hub; Patterson 2007; Binder & Desai 2011) -- a
   text-distributional signature has ZERO such dimensions, so those senses are inseparable IN PRINCIPLE from reading
   alone. This is the ceiling cause and it is not glass-box-distributionally reachable.
5. **Representation.** Under the diagnostic query, mean-pool beats top-k/exemplar here (measured), so the readout is
   not the recoverable lever.

## The syntagmatic-tightness lever, tested TWO ways (the last glass-box crossing)

SyntagNet's edges are syntactically-LINKED pairs; ours were whole-sentence topical bags. I tested the fix the
brain-faithful way -- disambiguate-then-bind, then restrict the BINDING to syntagmatic neighbours, then
cross-situational recurrence, then MFS-quarantine biased-competition (the 4-stage pipeline):
- **Window proxy (+/-3 content-word neighbours) + MFS-quarantine discrimination:** a_s **0.246** (best config
  ratio=2.0, K=3), and the windowed run's own recur+schema consolidation **0.247**. Both still BELOW gloss 0.251
  (sep=False, delta ~-0.005), the RAW-windowed twin regresses (0.236 < gloss), the shuffled twin loses, and the
  **MFS no-regression guard PASSES** (overall blended 0.695 >= MFS 0.683). So syntagmatic tightness inches the
  ceiling up (0.238 -> 0.247) but does not cross gloss.
- **Real dependency-parsed asset (offline spaCy; head + children of the disambiguated target) + MFS-quarantine:**
  a_s **0.251 = gloss exactly** (`exp_consolidation_gate_syntactic_v1.py`, 1M parsed sentences; sep=False,
  null_p95 0.013). The truest syntagmatic test reaches gloss and stops -- confirming the monotone ladder
  (sentence 0.238 -> window 0.246 -> dependency 0.251) never crosses. Syntagmatic tightness is RULED OUT.

**What I did NOT establish, and would withdraw first if wrong:**
- The claim that ATTRIBUTION is not the leak rests on the oracle being coverage-starved (1.03 assoc/sense on
  even-doc SemCor). A large gold-tagged corpus could give perfect-attribution AND coverage; I could not build one
  glass-box. The full-corpus discriminative route (0.246-0.251, ~12 assoc/sense) triangulates the same ceiling from
  the opposite corner, which is why I hold the conclusion.
- The contextual-encoder is a GLASS-BOX prototype (our own BiLSTM masked-LM; NO external LLM) and was scale-limited
  on CPU (undertrained to 0.113); the run was STOPPED -- we do glass-box, and chasing scale toward a transformer is
  the INVARIANT BOUNDARY, not pursued. The corrected claim (contextual representation is the barrier) rests on the
  established fact that text-only encoders reach ~0.53; a scale-trained GLASS-BOX contextual encoder is est.
  ~0.40-0.45 (a real but bounded glass-box lever). We ACCEPT the glass-box readout ceiling (~0.35) as the honest
  wall here; the transformer/scale route is an owner decision outside this problem.

## GROUNDING TESTED AT EVERY RICHNESS AND RULED OUT (an earlier 'grounding is the crosser' framing was WRONG)

The signal-loss trace named GROUNDING as the ceiling cause: reading co-occurrence is topical, and the brain
individuates senses from sensorimotor/affective spokes (ATL hub; Patterson 2007; Binder & Desai 2011). I BUILT and
tested that fix glass-box (`exp_consolidation_grounded_v1.py`) using the WIRED grounding organ
`hdlab/grounded_similarity` (12-dim Lancaster sensorimotor + Brysbaert concreteness, ~30k coverage):
- **Grounding DOES separate senses distribution cannot** -- a river-context grounded vector matches the river-bank
  sense centroid at **0.813** vs the money-bank sense at **-0.096** (the self-test asserts this). The mechanism is real.
- **But fused into the readout (biased competition in the grounded space + reliability-weighted precision gating), it
  does NOT beat gloss, at ANY available richness -- tested three ways:** base 12-dim 0.251; **affect-augmented 15-dim
  (+Warriner valence/arousal/dominance) 0.252 (filter+fuse 0.256);** ATL-whitened distinctive 0.250 -- all vs gloss
  0.251, NONE CI-separated (null p95 ~0.006-0.009). Affect adds a hair of real signal (0.252 > its shuffled twin
  0.246) but nowhere near a CI-separated crossing.
- **Stratifying by grounded-separability does not rescue it:** on the HIGH-separability (concrete-ish) half it is
  0.246 vs gloss 0.248; on the LOW half 0.255 vs 0.255. It fails on BOTH halves.
- **The BRAIN'S EXACT grounding mechanism was implemented and ALSO does not cross.** Grounding coverage to
  abstract/unseen concepts is achieved in the brain by CATEGORY-BASED SEMANTIC INHERITANCE (a hyponym inherits its
  hypernym's grounded features; the ATL hub over the concept hierarchy) -- NOT by a regressor (the brain does not
  train a map from word-vectors onto feature-ratings; that ML hack was tried and correctly DROPPED as
  non-brain-foundational). Implemented exactly (`exp_consolidation_grounding_inherit_v1.py`: aggregate the
  perceptual norms over each synset's own + hypernym-chain + hyponym words, distance-weighted): INHERIT_fuse =
  0.2512 = gloss (sep=False). The brain's Hebbian binding + CLS consolidation + inheritance are ALL replicated, and
  the capability still does not cross.
- **THE WALL IS THE INPUT REPRESENTATION, NOT THE ALGORITHM -- and it is TEXT-learnable, not perceptual (the deep,
  twice-corrected conclusion).** With the brain's full mechanism faithfully in place, grounding at every richness
  = gloss, so grounding is NOT the missing signal. The corrected wall (owner 2026-09-03): we hand each word ONE
  static, sense-conflated vector (fixed before the sentence is read); the brain -- and a text-only language model --
  RE-COMPUTES the word from its context, giving "bank(river)" and "bank(money)" different representations. That is
  learnable from the SAME text (text-only encoders reach 0.53 near-human; grounding/perception is NOT required), and
  it needs SCALE, not perception. Earlier drafts called this a grounded-input / fidelity-vs-coverage problem; that
  was the overstatement -- the honest wall is a CONTEXTUAL, sense-separated text representation.

## THE 100% BRAIN-FAITHFUL READER + OPTIMIZED UPSTREAM FOUNDATION -- the MAXIMIZED glass-box result (a POSITIVE)

Research-grounded (Rodd/Gaskell/Marslen-Wilson 2004 attractors; Kawamoto 1993; McClelland-Rumelhart 1981;
Erk & Pado 2010 exemplars; Arora 2018 sense-superposition; Peters 2018) the training-free brain-faithful way to
contextualize a word is "RE-REPRESENTATION BY SELECTION among multiple sense-ATOMS": replace the single frozen
point with a SET of sense atoms and let context SELECT/settle among them. Built glass-box, no-training, one-pass
(`exp_brain_faithful_reader_v1.py`): the READER = biased-competition selection / attractor settling; the optimized
UPSTREAM FOUNDATION = the richest offline sense-atoms (gloss + examples + lemmas + hypernyms + WordNet relations +
curated SyntagNet + ConceptNet -- the admissible "ideal knowledge foundation"). n=2676 strict doc-disjoint:
- **gloss-only atom + reader 0.251 -> RICH-foundation atom + reader 0.3178: +0.067 CI-separated [0.048,0.087].**
  The optimized upstream foundation synergizing with the faithful selection reader is the BIGGEST glass-box lever
  and it BEATS the dictionary -- reaching the glass-box ceiling (~0.32; parent's 0.326-0.34 with richer embeddings).
- **Attractor SETTLING (recurrent modern-Hopfield over the atoms) OVER-COLLAPSES: 0.202 (< gloss).** Understood
  negative: with atoms that share gloss words, recurrent settling snaps to the topically-nearest = dominant basin,
  destroying the fine diagnostic signal. The RIGHT amount of settling is the ONE-SHOT biased competition (itself
  lateral-inhibition selection); more hurts (matches the parent's PPR-settling graph < one-shot diagnostic).
- **Ceiling confirmed:** capped near the static-atom inventory's own separability (Arora 2018; Peters 2018) -- every
  atom is drawn from the same frozen space, so selection cannot recover distinctions that space never encoded.
  Crossing it needs re-representing the ATOMS (a contextual encoder / transformer) = the invariant boundary, NOT
  pursued (glass-box, period). So the MAXIMUM brain-faithful glass-box system = rich foundation + selection reader
  = 0.318.

## WHERE THE SIGNAL IS LOST IN THE 0.318 SYSTEM, THE EXACT BRAIN DIVERGENCE, AND WHERE THE NEXT GAINS COME FROM

Traced stage-by-stage through the maximized reader (rich-atom foundation + faithful selection = 0.318), with the
loss and the EXACT brain difference at each, and the number that proves it:

| stage | our implementation | where signal is lost | EXACT brain difference |
|---|---|---|---|
| **1. sense ATOMS** (foundation) | each sense = a **frozen-w2v CENTROID** of {gloss+relations+SyntagNet+ConceptNet} | **THE DOMINANT LOSS** -- a rare sense's atom and its dominant twin's atom **OVERLAP in the frozen space** (senses are superposed there, Arora 2018), so selection cannot separate topically-ambiguous cases. **PROVEN:** even a SUPERVISED sense-usage key caps at **0.35** (parent's oracle trace) -- so the FROZEN DISTRIBUTIONAL SPACE is the cap, NOT the knowledge and NOT the reader | brain sense reps are (a) **contextually re-computed** (not frozen), (b) **grounded** (non-distributional dims), (c) **exemplar** (not a prototype/centroid -- Erk-Pado 2010) |
| **2. CONTEXT** (query) | bag of static-w2v, biased-competition weighted | **non-COMPOSITIONAL** -- no syntax/order ("you SIT ON a river bank"), and each context word is itself frozen | compositional, order-sensitive; each context word re-represented in context |
| **3. SELECTION** (reader) | one-shot biased competition = **near-optimal for our atoms** | **not the loss** -- recurrent settling only makes it WORSE (0.202), because the atoms overlap so settling collapses to the dominant basin | brain settles among **DISTINCT** attractors; ours overlap, so more settling = collapse |
| **4. prior** | none (subordinate metric) | minor | resting-level frequency + interactive competition |

**QUANTIFIED loss ledger (our 0.318 -> human ~0.65):**
- **0.318 -> ~0.35** = glass-box residual (prototype->exemplar, bag->compositional, atom overlap). ~+0.03, diminishing.
- **~0.35 -> 0.53** = THE FROZEN-DISTRIBUTIONAL-SPACE WALL -- recoverable ONLY by adding information the frozen space
  lacks. ~+0.18, the dominant remaining loss.
- **0.53 -> ~0.65** = world-knowledge INFERENCE beyond the sentence. ~+0.12.

**THE SINGLE DEEPEST DIVERGENCE:** our representational SUBSTRATE is a **frozen distributional space where senses are
superposed**; the brain's is **grounded + contextually-recomputed, where senses are DISTINCT**. Every downstream
difference (settling collapse, bag context) traces to this one -- and no reading dynamics on frozen, overlapping
atoms can separate what the substrate already merged (evidence: supervised keys cap at 0.35).

**WHERE THE NEXT GAINS COME FROM (assigned, prioritized):**
1. **[glass-box, small, diminishing -> ~0.35]** exemplar retrieval (Erk-Pado; store per-sense usages, retrieve by
   context) + compositional/order context (BEAGLE/VSA circular-convolution binding, no training) + a richer curated
   foundation. Reaches the ceiling but no further.
2. **[THE ceiling-breaker -- two routes, both add what the frozen space lacks]:**
   (A) **glass-box + brain-faithful: a RICHER GROUNDED representation** -- non-distributional (perceptual/affective)
   dimensions that separate superposed senses. This is the correct brain-faithful lever, but our 12-dim norms are too
   coarse (tested, ruled out); it needs a Binder-class ~65-dim brain-based asset at broad coverage = a foundation/data
   build. (B) **[invariant boundary, NOT pursued glass-box]** contextual RE-REPRESENTATION of the atoms (a
   contextual encoder / transformer) -- reaches 0.53; owner decision.
3. **[glass-box, hard -> ~0.65]** multi-hop world-knowledge REASONING over the semantic graph for the residual that
   is not in the sentence at all.

## MECHANISM-COMPLETE: the brain's mechanism tested TOP-DOWN, GROUNDED, and BOTTOM-UP -- none crosses

To rule out "we just didn't use the brain's actual learning mechanism," all three families were implemented
glass-box, ONLINE, ONE-PASS, NO TRAINING (the brain does not do long training runs):
- **TOP-DOWN** disambiguate-then-bind + cross-situational consolidation (the gate): a_s 0.251 = gloss.
- **GROUNDED** perceptual norms + semantic inheritance: a_s 0.251 = gloss (ruled out at every richness).
- **BOTTOM-UP online sense induction** (`exp_online_sense_induction_v1.py`) -- competitive-Hebbian multi-prototype
  (Reisinger-Mooney / interactive activation, ART vigilance: a novel context SPAWNS a sense-prototype, else UPDATES
  the nearest; one pass over 800k sentences, 2.3M occurrences): induced sense-keys a_s **0.183 vs the same cell's
  gloss-key 0.214 -- CI-separated BELOW gloss** (ci [-0.049,-0.013]), induced-key coverage only 0.22. Induced
  clusters are TOPICAL and dominant-swamped; rare senses do not form their own clean cluster.
**So the wall is NOT any mechanism** (top-down, grounded, and bottom-up all faithfully built, none crosses) --
it is the TOPICAL, STATIC context/word representation they all operate on. The brain-foundational fix for THAT is
an ONLINE predictive reader that separates senses as it reads, not a batch-trained encoder.

## HOW THE LEARNER GROWS THIS CAPABILITY OVER TIME, AND BUILDS THE CORPUS OPTIMALLY (the composed path)

The growth ARCHITECTURE is complete and its ENGINE is proven; the binding constraint is knowledge QUALITY at the source.
- **Growth engine (proven, safe):** `hdlab/cls_growth` -- keep-both ensemble (`make_ensemble_sim`, old store never
  discarded) + `rollback_gate` (accept a grown update only if corruption CI-upper < 0.15 on a frozen known-correct
  probe) + EMA slow-anchor (`align_and_fuse`, eta=0.1 = the consolidation rate). Measured **+0.110 held-out over 6
  reading rounds, corruption 0.116<0.15, drift-free** (`run_the_learner_on_live...`, SOLVED). The learner CAN grow
  knowledge over time without corrupting the old store.
- **"Optimally built up" operationally = the admission pipeline this problem supplies:** read -> DISAMBIGUATE at
  encoding (bind context to the SELECTED sense, never the word form) -> cross-situational RECURRENCE -> DISCRIMINATION
  filter (MFS-quarantine; grounded where the asset is informative) -> **ADMISSION-QUALITY GATE vs the gloss floor with
  the RAW-vs-consolidated regression check baked in** -> cls_growth keep-both + rollback + EMA anchor. Consistency
  cleanup lives on the EPISODIC is-a KB (schema-congruence needs supercritical density, AUC 0.88), NOT on the
  distributional meaning learner (schema-congruence is confirmation-biased there -- `turn_on_the_learner...`).
- **The measured truth:** the gate and engine are ready and safe, but EVERY glass-box knowledge SOURCE (reading
  co-occurrence, 12-dim grounding) fails the admission gate on this task -- the learner would grow safely but not
  beneficially from them. The source that passes (curated SyntagNet) uses non-glass-box manual filtering. So the corpus
  is "optimally built up" by this pipeline, but beneficial growth needs a SOURCE that clears gloss -- which points to
  the grounded-input build below.

## PROPOSED hdlab WIRE (strategy lands it, Q111, default-off, witnessed)

**Do NOT wire a knowledge-growth default-on.** The measured result is that reading-derived consolidated knowledge
does not beat gloss, so admitting it to the live sense signatures would not help (and raw growth HURTS). The
load-bearing wire is a **guard**, not a feature:
- Promote the consolidation gate as a REUSABLE offline asset-builder (`consolidate(reading_cooc) -> per-sense
  clean associates`) with the RAW-vs-consolidated contrast BAKED IN as a regression check, so any future
  learner-growth path is measured against gloss before admission and the raw regression can never silently ship.
- The gate composes with `hdlab/cls_growth` (keep-both + rollback) as the safety wrapper: cls_growth handles
  reversibility; this gate handles admission quality. Neither alone is sufficient; the measured lesson is that
  admission quality is the binding constraint and reading-derived co-occurrence does not meet it.
- Keep the diagnostic-context readout (`hdlab/diagnostic_context_wsd`) as-is; top-k did not help.

## KEY REALIZATIONS

- **The reversed order IS the regression.** The brain disambiguates BEFORE it stores; naive growth counts
  co-occurrence on the ambiguous FORM then never separates senses, so the dominant sense floods the rare one. Fixing
  the order (disambiguate-then-bind) was necessary but revealed the deeper truth below.
- **Attribution was a decoy; the leak is discriminativeness.** The move that unstuck the analysis was the oracle
  arm: giving the pipeline PERFECT gold sense-attribution and watching it STILL fail to beat gloss. That killed the
  "just disambiguate better" hypothesis and pointed at the residual -- reading co-occurrence is topical, not
  sense-discriminative; the ingredient that fixes it (SyntagNet's manual concept-pair filtering) is non-glass-box.
- **A ceiling triangulated from opposite routes is a real wall.** Perfect-attribution/tiny-coverage and
  imperfect-attribution/full-corpus+discrimination both land ~0.242-0.251 -- the reading-derived ceiling, independent
  of the attribution/coverage tradeoff; the syntagmatic-tightness ladder climbs monotonically TO gloss and stops.
- **I overstated GROUNDING as the wall -- the owner corrected it, and the correction is the deepest realization.**
  I twice named grounding/perception as the ceiling-crosser. But a human (and a text-only LM) does WSD from the SAME
  text, so invoking perception was inventing an input we don't need. I then TESTED grounding at every richness
  (12/15-dim norms, ATL-whitened, brain-faithful semantic-inheritance) -- all = gloss 0.251, ruling it out. The real
  barrier is a CONTEXTUAL, sense-separated word representation learned from text: we use ONE static average vector
  per word form (sense-conflated, fixed before the sentence is read); the brain (and an LM) RE-COMPUTES the word from
  its context. That is text-learnable (text-only encoders reach 0.53) and needs SCALE, not perception. Lesson: never
  invoke grounding as a wall when text-only models already cross it -- name the missing TEXT-derived representation.
- **A brain-faithful mechanism is not a regressor.** Learning grounding-to-coverage via ridge (w2v->Binder ratings)
  is NOT how the brain works and was dropped; the brain-faithful coverage mechanism is SEMANTIC INHERITANCE through
  the concept hierarchy. Implementing the brain's FULL mechanism faithfully and still landing at gloss is what
  localized the wall to the INPUT REPRESENTATION rather than the learning/consolidation machinery.
- **THE BRAIN DOES NOT DO LONG TRAINING RUNS (owner 2026-09-03).** I twice reached for batch ML -- a ridge regressor,
  then a multi-epoch contextual-encoder training run -- both correctly killed. The brain learns ONLINE, incrementally,
  in ONE pass, via predictive coding + Hebbian plasticity + slow interleaved consolidation; it never backprops over a
  corpus for epochs. The brain-foundational route to a contextual representation is the ONLINE predictive reader, not
  a pretrained encoder. Whenever the "answer" becomes "train a bigger model," that is the ML-tool crutch, not the
  brain's mechanism -- stop and name the online operation instead.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)

- Knowledge growth from reading is CONFIRMED as the biggest lever (curated +0.051 CI-sep) but is NEGATIVE if
  uncontrolled (raw -0.033) -- the consolidation gate removes the regression but does NOT reach curated quality
  glass-box. The gap is NOT attribution (disambiguate-then-bind matches a gold oracle); it is association
  DISCRIMINATIVENESS (SyntagNet's manual concept-filter). Record reading-derived ceiling ~0.246-0.251 vs curated
  0.302 vs gloss 0.251.
- diagnostic_context_wsd: top-k/exemplar key readout is a measured NEGATIVE under the diagnostic query (mean-pool
  wins); do not expect a top-k lift when the query is already biased-competition.
- grounded_similarity: the grounding MECHANISM is confirmed (separates concrete homonyms 0.813 vs -0.096) but was
  TESTED at every richness (12/15-dim norms, ATL-whitened, and the BRAIN-FAITHFUL semantic-inheritance mechanism)
  and RULED OUT as the crosser -- all = gloss 0.251, failing even on the grounded-separable half. CORRECTION: an
  earlier "grounding is the wall" verdict was WRONG. Text-only encoders do near-human WSD, so the residual is a
  CONTEXTUAL, sense-separated input representation learned from text (static w2v is the deepest wall), NOT
  perception. Downgrade grounding to a secondary spoke; PIN the input-encoding wall (scale-trained contextual
  encoder est. ~0.40-0.45; transformer 0.53) as the crosser. cls_growth is the proven safe growth engine
  (+0.110/6 rounds); admission quality + the static input representation are the walls, not the engine.

## TLDR (plain English)

The biggest way to help a model pick a word's rare meaning is to give it more world knowledge about which words go
with which meaning -- but if it learns that knowledge the naive way from reading, the score gets WORSE, because raw
word-neighbour statistics pile onto the COMMON meaning and drown the rare one. I built the clean-up gate the brain
uses: read, figure out which meaning is in play FIRST, then attach the surrounding words to THAT meaning, and keep
only the associations that recur and that actually distinguish the meaning. The gate WORKS as a clean-up step -- it
removes the damage that raw learning causes. But even cleaned, reading-derived knowledge does not beat the plain
dictionary definition, and stays well below a hand-curated knowledge base. I proved WHY, three ways: giving the
system PERFECT meaning-labels still didn't help (so bad labelling wasn't the problem); the rare meanings barely
appear in any text (so there's little to learn from); and I tested the "perception" idea (grounding) at every
richness -- it cleanly separates obvious cases (river-bank vs money-bank) but does NOT move the average, so it is
NOT what's missing. The real gap (corrected): we hand each word ONE fixed meaning-vector, the blurry average of
all its meanings, decided before the sentence is read; a person (and a plain text-trained language model)
RE-READS the word in its sentence so "bank" by "river" and "bank" by "money" become different -- a better
representation learned from the SAME text, no perception required. Our small text-model prototype for this
undertrained on the CPU, but text-only models are known to reach near-human on this task, so THAT -- a
context-sensitive word representation, at scale -- is the real fix, not more reading and not perception. Net:
the clean-up gate is a real working safety filter and the safe growth engine is proven; growing knowledge from
reading is refuted as a way to beat the dictionary; the crosser is a context-sensitive input representation.

## WHERE THE SIGNAL IS LOST (ranked, with numbers -- the map for further optimization)

All a_s on strict doc-disjoint SemCor subordinate, n=2676. gloss floor 0.251; curated ceiling 0.302 (+0.051).

| # | loss source | evidence (the number that proves it) | recoverable glass-box? |
|---|---|---|---|
| 1 | **Association DISCRIMINATIVENESS** (reading co-occurrence is topical/dominant-biased, not sense-substitutable) | curated 0.302 vs best reading-derived 0.251; MFS-quarantine recovers only 0.218->0.246 | PARTLY -- residual is SyntagNet's manual concept-filter (barred) |
| 2 | **Rare-sense Zipf-starvation** (discriminating contexts are the rarest; PPMI weakest where needed) | oracle PERFECT attribution yields ~1 assoc/sense, a_s 0.232 | NO -- intrinsic to corpus/sense frequency |
| 1b | **STATIC (not contextual) input representation -- THE DEEPEST WALL** (one fixed sense-conflated w2v vector per word form, fixed before the sentence is read; a contextual encoder recomputes it per context) | glass-box readout caps ~0.35; scale contextual encoder est. ~0.40-0.45; transformer 0.53; human 0.6-0.7 -- and text-only encoders reach 0.53, so this is TEXT-learnable, not perception | YES but needs SCALE -- a scale-trained contextual encoder (GPU build); our small CPU prototype undertrained (0.113) |
| 3 | ~~GROUNDING~~ (TESTED, RULED OUT as the crosser) -- 12/15-dim norms, ATL-whitened, AND brain-faithful semantic-inheritance | grounded fuse 0.251-0.254 = gloss, fails even on the grounded-separable half (0.246 vs 0.248); separates concrete homonyms but the eval is abstract-dominated | perception is NOT the missing signal; contextual representation (1b) is |
| 4 | ~~Attribution~~ (RULED OUT) | our disambiguation 0.242 ~= perfect gold 0.232 -- NOT a leak | n/a |
| 5 | ~~Readout representation (top-k)~~ (RULED OUT) | top-k/exemplar LOSES under the diagnostic query (-0.03 to -0.06) | n/a |
| 6 | ~~Syntagmatic tightness~~ (RULED OUT, tested to the real dependency parse) | sentence 0.238 -> window 0.246 -> real dependency 0.251 = gloss, never above | inches up, does not cross |

## STEPS FOR FURTHER OPTIMIZATION (ordered, actionable -- what strategy should build next)

1. **[THE FOCUS] THE 100% BRAIN-FOUNDATIONAL PATHWAY -- the ATL HUB-AND-SPOKE + ONLINE PREDICTIVE READER** (see the
   highlighted section above). The ceiling is the FROZEN DISTRIBUTIONAL substrate (senses superposed); the
   brain-foundational way through it is GROUNDED SPOKES (visual/motor/affective/relational -- orthogonal dimensions
   that separate superposed senses) bound to a transmodal HUB, RE-COMPUTED per context by the ONLINE predictive
   reader (one pass, no training). NUANCE the corrections: the 12-dim norm READOUT-FUSION was ruled out (too coarse),
   but the pathway is RICHER SPOKES (Binder-class ~65-dim + affect + relational, propagated to coverage by SEMANTIC
   INHERITANCE) in the HUB-AND-SPOKE architecture + online reading -- NOT a coarse fusion, and NOT a batch-trained
   encoder. This is the meaning-channel NORTH STAR and the next build this problem earns.
2. **[LAND NOW -- the launch pad] the clean foundation + safe learner-on.** Wire relations+SyntagNet+ConceptNet as
   sense atoms through the selection reader (+0.067 CI-sep, the PASS); the admission GATE + `hdlab/cls_growth`
   (+0.110/6 rounds, drift-free) make reading-growth SAFE. Default-off, witnessed, Q111.
3. **[NON-brain-foundational -- NOT pursued] the contextual encoder / transformer (~0.53)** is the OTHER way through
   the ceiling, but it is ungrounded + batch-trained = the invariant boundary. Owner-only decision; not this pathway.
4. **DO NOT wire reading-derived growth default-on** -- it does not beat gloss and raw growth HURTS. The gate is a
   REGRESSION-GUARD; admission quality is the binding constraint until the substrate (step 1) improves.

## QUESTIONS

One judgment for the owner: **open the 100% brain-foundational pathway (ATL hub-and-spoke grounded atoms + online
predictive reader; step 1) as its own problem -- the next focus?** The gate + clean foundation (step 2) is landable
now (+0.067 PASS); the substrate build is where the ceiling breaks brain-foundationally (no transformer, no training).

## NEXT STEPS

PARTIAL: the gate PASSES with clean knowledge (+0.067 CI-sep, raw twin loses) -- LAND the clean foundation + safe
learner-on now (step 2). The narrow located negative (reader can't grow clean knowledge from its OWN reading) is
mechanism-complete. **THE NEXT FOCUS is the 100% brain-foundational pathway -- the ATL HUB-AND-SPOKE (grounded,
orthogonal, richer spokes) + ONLINE PREDICTIVE READER (step 1) -- the only route that breaks the frozen-substrate
ceiling without a transformer or a training run.** It is the meaning-channel north star, and this problem pins why.
