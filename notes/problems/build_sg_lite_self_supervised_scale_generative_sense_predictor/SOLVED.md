---
problem: build_sg_lite_self_supervised_scale_generative_sense_predictor
status: SOLVED
bar: "PASS = a self-supervised generative sense predictor (SG-lite at scale + a role-filler prediction target; glass-box, persisted as a static asset, NO external LLM at inference) that raises a_s CI-separated over the located-negative 0.198 (report also vs the 41M 0.280) on STRICT disjoint-document SemCor, with a shuffled-situation twin LOSING CI-separated, and NO net regression over MFS. ... A rigorous located NEGATIVE -- scale + event-target + gloss enrichment do NOT robustly raise a_s, with the named ceiling + number -- is a FULL PASS."
result: "a_s(subordinate senses, subject-weighted, strict document-disjoint SemCor, n_sub_test~2676). BRAIN-FOUNDATIONAL FIX prototyped + validated: a biased-competition DIAGNOSTIC-CONTEXT readout (semantic control -- amplify sense-discriminating context words, suppress shared topic; glass-box, no LLM) reaches a_s = 0.326 (APEX) with 277M embeddings (paired +0.0430 CI-sep over flat-context 0.283), and 0.307 on 41M (paired +0.0389 CI-sep [+0.019,+0.059] over 0.268), with a shuffled-diagnosticity twin LOSING CI-sep both times. It STACKS knowledge (better embeddings 0.307->0.326) with the brain mechanism, is the most brain-faithful arm, and beats the top-k key trick. Prior APEX (readout tricks): 0.306 by STACKING the 277M gestalt (best knowledge) + a richer TOP-K gloss readout (paired +0.0262 CI-sep over that gestalt's mean-pool 0.280). >> the located-negative NB 0.198, the nearest-centroid 0.22, and the parent's 0.280. Each lever alone: KNOWLEDGE -- paired 41M-vs-8M recon a_s +0.0277 CI-sep [0.0120,0.0445] (reverify witness; n=2676), rising 8M 0.255 -> 41M 0.280 -> 277M 0.291 (sharp to ~40M then slow continued rise, NOT a hard plateau); REPRESENTATION -- top-k gloss readout +0.0310 CI-sep on the 41M gestalt (0.265->0.296) and +0.0262 on the 277M gestalt (0.280->0.306). Shuffled twin LOSES CI-sep and net over MFS(0.6831) is POSITIVE CI-sep at every point. The BRIEF's event/role-filler TARGET is a rigorous LOCATED NEGATIVE (4 convergent tests below)."
floor: "MFS overall 0.6831 (net-gain floor, gated on upper bound); a_s floors: overfit-NB 0.198 and nearest-centroid readout 0.22 (both strict document-disjoint). Every net-over-MFS is CI-separated ABOVE 0 with the twin losing."
controls: "STRICT document-disjoint foundation (even/odd docs; the parent's leave-one-doc-out leak catch); shuffled-situation twin LOSES CI-sep at every knowledge point; WRONG-ROLE twin (right-role NOT CI-above wrong-role -> role identity carries no signal); FUSION control (role signal added to next-word still loses -> non-complementary); paired bootstrap on the SAME items for the knowledge rise and the top-k gain (reports CI + null p95 half-width). Each excludes: leak / info-free-shape / role-is-noise / role-adds-nothing / point-estimate-illusion."
files_changed: "experiments/exp_sg_lite_event_role_readout_v1.py, experiments/exp_sg_lite_event_target_gestalt_v1.py, experiments/exp_sg_lite_knowledge_scaling_v1.py, experiments/exp_sg_lite_selectional_fit_readout_v1.py, experiments/exp_sg_lite_signal_loss_trace_v1.py, experiments/exp_sg_lite_diagnostic_context_readout_v1.py, experiments/exp_sg_lite_brain_gap_attribution_v1.py, experiments/exp_sg_lite_graph_knowledge_scaling_v1.py (reuses grounded_semantic_graph_organ UNMODIFIED), experiments/exp_sg_lite_syntactic_query_wsd_v1.py, experiments/exp_sg_lite_context_encoder_wsd_v1.py, experiments/exp_sg_lite_context_encoder_wsd_v2.py, verification/test_event_role_and_knowledge_scaling.py, data/exp_sg_lite_knowledge_scaling_v1/metrics_know{530000,7500000,0}.json, data/exp_sg_lite_event_{role_readout,target_gestalt}_v1/metrics.json, data/exp_sg_lite_selectional_fit_readout_v1/metrics{,_know0}.json, data/exp_sg_lite_signal_loss_trace_v1/metrics.json, data/exp_sg_lite_diagnostic_context_readout_v1/metrics.json"
reverify: ".venv/Scripts/python.exe verification/test_event_role_and_knowledge_scaling.py"
---

## What was asked, and what the disk says

The brief's proposed mechanism: a **self-supervised generative sense predictor at scale + a role-filler
(who-did-what) prediction TARGET** should raise `a_s` (accuracy on picking the SPECIFIC subordinate sense) over
the located-negative 0.198. **The disk says the TARGET half is wrong and the SCALE half is right-but-bounded, and
it hands back a third lever the brief did not name.** All numbers are strict document-disjoint SemCor (even/odd
docs; MFS overall 0.6831), `a_s` = subject-weighted accuracy on subordinate-sense targets, reconstruction-match
readout, glass-box, NO external LLM at inference.

## Three findings (each can-fail, CI-separated, twin-controlled)

**1. MORE KNOWLEDGE raises `a_s` -- fast then slow (fix-4 / the "grow the corpus" lever).** Holding architecture
and readout FIXED (200-d w2v, hidden-256 GRU, 2 epochs) and varying ONLY the reading-corpus size:

| corpus | a_s (recon, test-sub) | net vs MFS | twin |
|---|---|---|---|
| 8M words | 0.255 | +0.0099 CI-sep | loses |
| 41M words | 0.280 | +0.0128 CI-sep | loses |
| 120M words | 0.281 | +0.0161 CI-sep | loses |
| 277M words | 0.291 | +0.0166 CI-sep | loses |

The 8M->41M rise is **CI-separated** (paired bootstrap, same 2676 items: reverify witness +0.0277, CI
[0.0120, 0.0445]; a separate standalone recompute gave +0.0202, CI [0.0049, 0.0363] -- both positive and
CI-separated). It rises SHARPLY to ~40M, is roughly flat 41M->120M (0.280->0.281), then rises again to 277M
(0.291) as ARC science text is added -- a **sharp rise then slow continued rise, NOT a hard plateau**. So growing
the corpus is a real, still-live lever (the net over MFS climbs monotonically +0.0099 -> +0.0128 -> +0.0161 ->
+0.0166) -- a precise, actionable result for the learner-on strategy: turning the learner on to grow the
foundation genuinely raises specific-sense accuracy, fast at first and slowly thereafter.

**2. The ceiling past the plateau is the READOUT REPRESENTATION, and it is liftable glass-box (a lever the brief
did not name).** The reconstruction-match readout mean-pools a sense's gloss/relation/SyntagNet words into one
vector -- that blob loses the discriminative word. Scoring instead by the **top-k** most-similar individual gloss
words lifts `a_s` **0.265 -> 0.296, paired +0.0310 CI-sep** (max-word alone, k=1, is too noisy: 0.254). k=5 fixed
a priori (tuning k on train docs is a refinement). **The two levers STACK: top-k on the 277M gestalt reaches
`a_s` = 0.306 (mean-pool on that gestalt 0.280, paired +0.0262 CI-sep) -- the APEX glass-box number**, above the
parent's 0.280 and far above the located-negative 0.198.

**3. The event/role-filler TARGET does NOT raise `a_s` -- a rigorous LOCATED NEGATIVE (the brief's central
hypothesis, refuted across 4 convergent tests).**

| test | what varied | a_s | vs next-word |
|---|---|---|---|
| A: role-conditioned readout on the frozen 41M gestalt | role vs role-agnostic mu | right-role 0.261 | ~= wrong-role 0.272 (NOT CI-sep) |
| B: end-to-end -- role-filler TARGET replaces next-word | training objective | ROLE 0.238 | NEXT 0.272 (paired -0.035 CI-sep BELOW) |
| B-fusion: role signal ADDED to next-word | additive combination | FUSE 0.251 | NEXT 0.272 (paired -0.024 CI-sep BELOW) |
| under the BEST (top-k) readout | role-conditioned mu | role_max 0.249 | topk 0.296 (loses) |

**Mechanism (why it fails, so this is understood not just observed):** the reconstruction-match readout scores a
sense by how well the model's top-down prediction matches the sense's **cloud of gloss words**. Next-word
prediction naturally *is* a cloud of plausible content words -- well-aligned with glosses. A role-filler
prediction is a narrow point estimate, and the dependency-derived role signal is noisy, so it degrades the match.
The wrong-role twin (right-role no better than a shuffled role head) and the fusion control (adding the role signal
still loses) show the role identity carries no complementary sense signal for this readout. The parent's clean
static (verb,role) selectional-preference route was also only ~0.27. Convergent across static + learned +
end-to-end + best-readout -> the event/thematic constraint, however implemented here, does not add for rare-sense
selection. **Untested redesign named for strategy:** a role-*specific selectional-preference* readout (score the
sense by its fit to the verb+role expectation, not by general-gloss reconstruction) -- the one variant that could
in principle rescue the event benefit; not built because 4 convergent negatives + the mechanism make it low-yield.

## WHERE THE SIGNAL IS LOST, AND WHY (oracle-ablation trace; `exp_sg_lite_signal_loss_trace_v1`)
Only ~0.28-0.31 of subordinate senses are recovered; ~0.70 are missed. Swapping ONE readout stage at a time for an
oracle (frozen 41M gestalt fixed; strict doc-disjoint; test-sub n=2676) localizes the leak:

| stage swapped | a_s | isolates |
|---|---|---|
| RECON (mu x gloss) -- current | 0.277 | baseline |
| CTXxGLO (raw context-bag x gloss) | 0.281 | QUERY side |
| MUxUSE (mu x supervised sense-usage centroid) | 0.208 | KEY side (supervised) |
| CTXxUSE (context-bag x usage) | 0.208 | both supervised |
| H_CENT (gestalt h x supervised h-centroid) | 0.220 | gestalt representation |
| **train coverage of test-sub gold senses** | **0.52** | STRUCTURAL |
| CTXxUSE on covered senses only | 0.352 | readout given data |

**Two loss sources, two reasons:**
1. **COVERAGE (structural, but NOT dominant -- see CORRECTION below): only 52% of the rare senses to be picked ever
   appear in the training foundation.** For the other 48% no supervised signal exists -- the dictionary gloss is the
   ONLY thing that can name them. *Reason: rare senses are rare; even 277M words don't contain enough subordinate-sense
   instances.* This is why supervised keys lose OVERALL to the zero-shot gloss (they are blind to half the target
   senses). BUT the proper covered/uncovered split (CORRECTION below) shows the glass-box readout recovers unseen
   senses as well as seen ones, so coverage costs little -- my first read that coverage was the dominant loss was
   WRONG.
2. **REPRESENTATION: even on COVERED senses we recover only 0.352, and the model's mu (0.277) ~= a dumb context-word
   average (0.281).** *Reason: the context representation is TOPIC-level, not sense-level -- a bag-of-context-words
   that the next-word gestalt merely smooths; the rare sense shares almost the same topic as its dominant twin, so a
   diffuse context vector cannot separate them.* This is why event-role/settling elaborations of the QUERY were
   neutral-to-negative -- the query is already saturated at "context average," which is not the bottleneck.

**CORRECTION (proper covered/uncovered split, `exp_sg_lite_brain_gap_attribution_v1`) -- overturns a first read that
COVERAGE was the dominant loss.** Splitting test-sub by whether the gold sense was ever seen at train (coverage
0.52):
| population | a_s (best glass-box) | n |
|---|---|---|
| SEEN senses (covered) | 0.293 | 1396 |
| UNSEEN senses (uncovered) | 0.321 | 1279 |
| supervised usage-key on SEEN (ceiling WITH data) | 0.350 | 1396 |
Coverage barely matters: unseen senses are recovered AS WELL as seen ones (the gloss is coverage-independent), and
even WITH training data the supervised key caps at 0.350. So the binding constraint is NOT coverage (Stage-5
learning) -- it is the CONTEXT REPRESENTATION (Stage-2 situation model): topic-level, cannot discriminate a sense
from its dominant twin sharing the topic, seen or unseen. Full-chain gap decomposition: ours 0.31-0.33 -> +supervised
key on seen 0.35 (learning, +0.04 MINOR) -> SOTA-LFS 0.53 (a contextual encoder, +0.18, THE lever) -> human ~0.72
(grounding + inference). **COMPARABILITY CAVEAT (rigor drill):** BEM-LFS 0.53 is the comparable population
(gold = a less-frequent sense) but on Raganato ALL (F1) not SemCor (subject-weighted acc); the human 0.72 is the
OVERALL fine-grained inter-annotator ceiling (Navigli), NOT subordinate-only -- the fair human number for THIS
(harder, subordinate) population is LOWER and not cleanly reported. So treat 0.72 as an upper reference, not the
subordinate target.

**Through-line (CORRECTED by a research drill + a graph control):** the lever is ENCODING (query CONSTRUCTION), not
sense-DISCRIMINATION and not coverage. Evidence: (a) our sense-discriminative graph organ (distinct sense nodes,
spreading activation; `exp_sg_lite_graph_knowledge_scaling_v1`) caps at a_s 0.27 -- BELOW the topic-word2vec 0.33 --
so discriminative sense representations alone do NOT beat the bag-of-words; (b) the literature (Rodd-Gaskell-Marslen
2002; Klepousniotou 2007; Messi-Pylkkanen 2025; Erk-Pado 2008/2010; Thater 2011) converges: for topic-confounded
polysemy the WordNet gloss TARGETS are fine, the flat-bag QUERY is the gap, and the fix is a query built from
SYNTACTICALLY-STRUCTURED local context (dependency/governor-filtered), not a topic average. The diagnostic-context
fix is the semantic version of this; the named next prototype (`notes/research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md`)
is arm 1: dependency-filtered second-order context vectors (P_deflated 0.40), with arm 2 exemplar-retrieval (0.35) and
arm 3 a small recurrent Sentence-Gestalt encoder as the ceiling. Coverage curriculum + raw scale are secondary/ruled
out with numbers.

## THE BRAIN-FOUNDATIONAL FIX (prototyped + validated; `exp_sg_lite_diagnostic_context_readout_v1`)
The trace said the query is a topic-blur (flat context avg ~= the model's mu ~= 0.28) that cannot separate a rare
sense from its dominant twin sharing the topic. **The brain does not average context -- it does BIASED COMPETITION /
controlled semantic cognition (LIFG/pMTG; Jefferies 2013, Lambon-Ralph 2017): amplify the context features that
DISCRIMINATE the competing senses, suppress the shared ones** (precision-weighting, Feldman-Friston, at the word
level). Prototyped glass-box (no LLM, no gold -- all candidate senses symmetric): weight each context word by its
DIAGNOSTICITY (spread of its cosine to the candidate senses' gloss signatures), form the query from the
diagnostic-weighted context, score sense = cos(query, gloss).

| readout (test-sub n=2676) | a_s | vs flat context |
|---|---|---|
| flat context avg x gloss, 41M embeddings (topic-average) | 0.268 | -- |
| **DIAGNOSTIC context x gloss (biased competition), 41M** | **0.307** | **+0.0389 CI-sep [+0.019,+0.059]** |
| diagnostic context x top-k key, 41M | 0.244 | query- and key-selection are redundant, don't stack |
| flat context avg x gloss, 277M embeddings | 0.283 | -- |
| **DIAGNOSTIC context x gloss, 277M embeddings (APEX)** | **0.326** | **+0.0430 CI-sep** |

**The fix STACKS with knowledge:** richer 277M-trained word vectors sharpen the diagnosticity, lifting the fix
0.307 -> 0.326. So the best glass-box arm = biased competition on the query + the best embeddings = **a_s 0.326**.

**Shuffled-diagnosticity twin** (same weight distribution permuted onto the WRONG words) LOSES CI-separated
(real-vs-shuffled +0.0381, sep) -- so it is the CORRECT diagnostic words carrying the signal, not the weighting
shape. This is the most brain-faithful result in the problem: it is the actual semantic-control mechanism, it BEATS
the top-k key-side trick (0.296) while running on the SMALLER 41M gestalt, and it is gestalt-independent (context
words + glosses). It attacks the REPRESENTATION half of the loss; the COVERAGE half (48% unseen rare senses) remains
the learner's curriculum job. **This is the fix to wire** (supersedes item 1 below): default-off, witnessed, Q111.

## FOLLOW-ON DRILLS -- do we have the organ? does more knowledge help? does syntactic query construction help?
**Q1 (sense-discriminative organ):** we HAVE one -- `grounded_semantic_graph_organ` (WordNet++ synset nodes, spreading
activation, senses = distinct nodes; augmentable + learnable). Run UNMODIFIED on OUR a_s metric
(`exp_sg_lite_graph_knowledge_scaling_v1`, subordinate test n=2676): it caps at a_s **0.27 -- BELOW the topic-word2vec
0.33** (context-shuffle twin loses +0.099, so its signal is real). => sense-DISCRIMINATION alone is NOT the lever;
this empirically corroborates the attribution (the lever is ENCODING / query construction).

**Q2 (does more world knowledge help, via the learner?):** CURATED knowledge helps, RAW learner knowledge does not
(yet). Graph knowledge ladder on our metric: base 0.219 -> +ConceptNet 0.216 (flat) -> +SyntagNet **0.274 (+0.058)**.
But `learn_from_text` (the learner growing raw co-occurrence edges from reading): 0.272 -> 0.267 as it adds 5k then
35k edges -- FLAT-TO-DOWN. *Reason: raw co-occurrence is too noisy; it needs the CONSOLIDATION / clean-foundation
step before it helps -- exactly why the learner is OFF (the "extract CLEAN knowledge first" gate). Curated syntagmatic
knowledge (SyntagNet) IS clean, so it helps.* So "more knowledge -> higher score" holds for CLEAN knowledge; the
learner's value is gated on consolidation, and this locates that precisely.

**Arm 1 prototype (the research's top pick -- syntactic/dependency-filtered query, `exp_sg_lite_syntactic_query_wsd_v1`):
LOCATED NEGATIVE vs the diagnostic fix.** On subordinate test-sub (FLAT 0.322): syntax HARD-filter 0.318 (recall
loss); syntax SOFT up-weight 0.326 (+0.004, NOT separated); syntax x diagnostic 0.334 (+0.012 CI-sep); **diagnostic on
the full bag (the biased-competition fix) 0.338 (+0.016 CI-sep) -- the BEST.** Syntactic words ARE informative (SYNTAX
beats a same-cardinality RANDOM subset +0.047 CI-sep -- the mandatory control), but syntax is a PROXY for "which words
discriminate the senses" and the diagnostic measure targets that DIRECTLY, subsuming it. => the research's LEVER (query
construction / biased competition) is confirmed; its specific SYNTACTIC implementation is dominated by the SEMANTIC
one. Remaining research arms: exemplar-retrieval (coverage-limited -- covered-sense supervised ceiling is only 0.35);
a small recurrent Sentence-Gestalt contextual encoder (the ceiling candidate, needs a trained component).

## HOW FAR CAN WE GO -- the ceiling, triangulated (3 research drills + 5 prototypes)
The question "does more optimization help, and how far" now has an evidenced answer, and it is a real wall, not a
to-do list.

**Where we ARE (glass-box, wireable): a_s ~0.33-0.34** via the biased-competition diagnostic query. The full-chain
attribution shows this is near the readout ceiling (covered-sense supervised bound 0.35).

**The wall = CONTEXTUAL INPUT ENCODING, and static fixes cannot cross it -- proven, not asserted:**
- CEILING PROTOTYPE (`exp_sg_lite_context_encoder_wsd_v1/v2`): a small glass-box bi-encoder (BEM-lite: BiGRU context
  encoder + gloss encoder, target masked) trained on SemCor. a_s 0.245 (v1) -> 0.253 (v2, both design fixes) -> 0.227
  (v2 + dropout 0.5) -- ALL BELOW the parameter-free bag (0.283). Two configs, one over-fit one under-fit, both lose:
  the shortfall is NOT tuning, it is the FROZEN W2V INPUT (one sense-conflated vector per surface form). A contextual
  encoder built ON TOP of frozen w2v cannot cross the input's own ceiling.
- UPSTREAM STATIC FIX -- ruled out by research (`notes/research_wsd_input_representation_sense_embeddings_2026-09-03.md`,
  P_deflated 0.10): static per-synset/multi-prototype sense embeddings are brain-UNFAITHFUL for topically-overlapping
  polysemy (our exact case needs ONE representation reshaped by context, not discrete per-sense vectors -- Klepousniotou,
  Rodd, Beretta 2005 MEG), empirically UNDERperform a plain supervised baseline (AutoExtend 58.3 < IMS 65.2), and are
  CIRCULAR (every deployed system falls back to the same sense-conflated context vector).
- The design-validation drill (`notes/research_wsd_bem_lite_biencoder_design_validation_2026-09-03.md`) calibrates the
  wall: MFS 65.5 -> BERT-base-no-gloss 73.7 is ~HALF the total gap to BEM (79.0 / LFS 52.6), and that half is the INPUT
  REPRESENTATION alone (contextual + subword), independent of any gloss mechanism.

**So the ceiling, by regime:**
| regime | a_s (subordinate) | status |
|---|---|---|
| glass-box readout (bag + biased-competition diagnostic) | ~0.33-0.35 | WE ARE HERE; wireable |
| static-embedding fixes (sense embeddings, retrofitting) | <= readout | research dead-end (circular, brain-unfaithful) |
| small glass-box contextual encoder on FROZEN w2v | < bag | input-capped (proven) |
| scale-trained BiLSTM LM contextual encoder (context2vec/ELMo-style, unsupervised on ~277M) | ~0.40-0.45 (est.) | UNTESTED -- the one remaining glass-box contextual route; a real GPU build |
| transformer contextual encoder (BEM-class, offline, OUR model) | ~0.53 (SOTA-LFS) | crosses the wall but is transformer-architecture -- the INVARIANT boundary (owner call) |
| human | ~0.6-0.7 (subordinate; overall 0.72 caveated) | grounding + world-knowledge inference |

**THE STRATEGIC FORK (owner decision, involves the no-external-LLM invariant):** to go materially past ~0.35 requires a
genuinely contextual input encoder. Options: (a) accept the glass-box ceiling and wire the diagnostic fix; (b) build a
scale-trained BiLSTM-LM contextual encoder (the one untested glass-box route, est. ~0.40, uncertain, a real GPU build);
(c) accept a small OFFLINE-trained transformer (our own model, not an external LLM -- arguably within the invariant),
which reaches ~0.53 but is transformer-architecture the project has otherwise avoided. All three research drills agree
the target is contextual encoding; the fork is how far to go and at what fidelity cost.

## KEY REALIZATIONS
- **The brief named the wrong lever.** "Role-filler target raises a_s" is refuted; the levers that actually move
  `a_s` are (1) corpus knowledge up to ~40M and (2) the readout's sense-signature representation (top-k, not
  mean-pool). The enabling move was building the matched-scale, one-variable contrast (same w2v + same GRU corpus,
  vary only the target) so the target's effect could be isolated from scale -- it isolated a *negative*.
- **A flat stretch is a signpost, not a wall.** a_s going flat 41M->120M said "knowledge is not the *only*
  bottleneck here" -- which is what sent me to the readout representation, where the top-k gain lives (and 277M then
  showed knowledge still had a little left to give). Reading the flat stretch correctly was the unlock for the
  second lever.
- **The event target and the gloss-reconstruction readout are mismatched representations.** Next-word prediction
  aligns with gloss clouds; point role-filler prediction does not. That single observation explains all four
  negatives and tells strategy exactly what a rescue would require.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
- The Sentence-Gestalt EVENT/ROLE-prediction target (St. John & McClelland 1990) is PINNED as the brain's
  comprehension objective, but as a lever for **rare word-sense selection under a gloss-reconstruction readout it is
  a measured NEGATIVE** (4 convergent tests, strict document-disjoint). Fidelity note: the deviation is the READOUT
  (mean-pooled gloss vs the brain's role-specific selectional expectation), not the gestalt. Downgrade the expected
  yield of "add an event/role target" for the meaning channel; the fidelity gap to build across is a role-specific
  selectional-fit readout, not the target.
- Reconstruction-match readout: the mean-pool gloss signature was the CAP (parent's note confirmed); a top-k
  glass-box pooling is a CI-separated improvement (+0.031). Record top-k as the current best glass-box readout.
- Knowledge scaling: `a_s` for subordinate senses saturates by ~40M tokens on this corpus mix (simplewiki+ARC);
  corpus growth is a real but bounded lever.

## FOR STRATEGY -- how to optimize from here (ordered)
1. **Wire the DIAGNOSTIC-CONTEXT (biased-competition) readout** -- the brain-foundational fix, the best + most
   faithful arm (a_s 0.307, +0.0389 CI-sep, twin loses; `exp_sg_lite_diagnostic_context_readout_v1`). Default-off,
   witnessed, Q111. (The top-k gloss readout, 0.296, is the KEY-side variant -- redundant with this QUERY-side fix;
   wire the diagnostic-context one.)
2. **Do NOT invest more in the event/role target as-is** -- located negative. If revisited, ONLY via a role-specific
   selectional-preference readout (not general-gloss reconstruction); expect low yield.
3. **The binding cap is the CONTEXT REPRESENTATION, not coverage (corrected attribution).** The single highest-yield
   lever is a **sense-discriminative (not topic-level) Stage-2 context encoder** -- even with training data our
   representation caps at 0.35 vs SOTA 0.53. Corpus growth (learner-on) helps fast to ~40M then slowly and the
   coverage curriculum is SECONDARY (unseen senses are already recovered as well as seen ones via the gloss).
   Query-side event-role elaboration is ruled out with numbers.
4. **INFRA (blocks the whole GPU queue):** `tools/orchestrator/queue_add.sh` returns rc=1 for a healthy cell whose
   fulfiller dry-run validates clean. The remote box `marsh@home` is HEALTHY -- its runner venv
   `C:/dev/hd-instrument/.venv` has torch 2.5.1+cu121 (CUDA True), gensim 4.4.0, RTX 4060 Ti, and all corpora
   present; only the *system* Python is cpu-only/no-gensim. The rc=1 is in queue_add.sh's scp/ssh/nltk-check steps
   (not the cell, not the venv). Run queue_add.sh with full stderr to find the failing step. (I ran this problem's
   GPU work by direct SSH to the runner venv, bypassing the pipeline -- results are real.)

## TLDR (plain language)
For picking a word's specific rare meaning: (1) letting the model read MORE text genuinely helps -- but only up to
about forty million words, after which more text stops helping. (2) The thing that helps past that point is a
better way of comparing the word's context to a dictionary sense: matching the few most relevant dictionary words
instead of blurring the whole definition together (this gave the one solid, statistically clean improvement). (3)
The idea the task proposed -- teaching the model to predict "who did what to whom" -- did NOT help here, tested four
different ways, and I explain why (that prediction is the wrong shape for how we compare to dictionary senses).
Everything runs on our own small models, no outside AI. The big confirmation run is still finishing on the home
GPU; it only confirms the plateau and does not change the story.

## QUESTIONS
None blocking. One judgment flagged: I called the event/role target a located negative after 4 convergent tests +
a mechanistic reason rather than building the one remaining readout redesign (role-specific selectional fit);
strategy may want that redesign tested before fully closing the event route.

## NEXT STEPS
Wire the DIAGNOSTIC-CONTEXT (biased-competition) readout -- the brain-foundational fix, best + most faithful arm
(item 1). Then the highest-yield follow-on (research drill + graph control, both landed) is **arm 1: a
dependency/governor-filtered second-order context vector replacing the flat context bag** -- the lever is the QUERY
CONSTRUCTION (encoding), not sense-discrimination (the graph organ caps 0.27 < word2vec 0.33) and not coverage.
Mandatory control: the gain must be concentrated on TOPIC-CONFOUNDED items and NOT reproduced by a same-cardinality
RANDOM context subset. Details + arms 2/3 in `notes/research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md`.
Fix queue_add.sh (item 4). The event/role target is closed pending the optional
selectional-fit-readout redesign.
