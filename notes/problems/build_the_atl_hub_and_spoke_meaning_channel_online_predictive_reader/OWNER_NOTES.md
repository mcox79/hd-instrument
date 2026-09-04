---
owner_verdict: DONE
---

SUBMISSION — build_the_atl_hub_and_spoke_meaning_channel_online_predictive_reader
status: PARTIAL  (WIP until owner_verdict: DONE). Glass-box, NO external LLM/transformer/training at inference.
NO hdlab written (Q111 — strategy lands the wire). Ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_atl_hubspoke_meaning_channel.py   # W1–W8, deterministic (threads=1)
scorer/pop: subject-weighted a_s on strict document-disjoint SemCor SUBORDINATE senses, n=2676, through the wired
hdlab/diagnostic_context_wsd, frozen 200-dim w2v.

RESULT. The brief's grounded ATL hub-and-spoke is a rigorous LOCATED NEGATIVE (a FULL PASS by the bar), PLUS a new
brain-faithful positive, PLUS the full chain assembled and the gap localized:
1. Grounded hub-and-spoke (Binder-65 + Warriner, ATL-whitened, inheritance-propagated) does NOT cross: concat-hub
   0.283 < launch pad 0.313 (CI-sep below). Cause is NOT the brief's premise — grounding DOES separate the senses
   (grounded cos(gold,dominant)=0.222 vs w2v-gloss 0.799; rescues 80% of merged pairs). The bottleneck is query-side
   selection + ~0.48 coverage; the parent already proved the keys are always separable (KEY-unwinnable 0.000).
2. THE LANDABLE WIN: controlled-retrieval PRECISION-weighting (Friston selective gain, gamma>1/top-k on the
   diagnosticity) lifts a_s 0.313 → 0.336, +0.023 CI-sep, info-free twin loses, NO MFS regression. New; neither
   parent found it. Does not reach 0.35.
3. FULL BRAIN-FAITHFUL CHAIN, traced R0→R6 (subordinate a_s): static 0.168 → read-context 0.214 → hub-and-spoke keys
   0.271 → controlled-retrieval 0.340 → consolidated(glass-box) 0.321 → consolidated(gold ceiling) 0.331 →
   +reader-mu 0.341. It climbs correctly, biggest gain = controlled retrieval (+0.069), then STALLS.
4. ENABLER identified (research + chance-controlled re-trace, both cited): CONTEXTUAL per-occurrence RE-REPRESENTATION,
   NOT knowledge. Frozen BERT beats MFS +20 on rare senses zero-knowledge; knowledge without a contextual base
   underperforms; no static-embedding method beats MFS on rare senses anywhere. The static per-token signal is real
   but THIN (+0.047 above chance; the old "cue-in-context 87%" was ~72% combinatorics — corrected).
5. The reader's own `mu` re-representation IS a brain-faithful sense-resolved encoding (raw target 0.201 → mu 0.275;
   +0.006 to the readout; non-leaky twin control) — just weak.

>>> THE GAP (where to improve), stated plainly <<<
NOT the readout (near-optimal, +0.069, landable). NOT the keys/knowledge (knowledge hurts inductively 0.261<0.34).
NOT a static extractor (signal thin, near-ceiling extracted). THE GAP = the CONSOLIDATION-OF-EXPERIENCE stage cannot
build a strong representation for RARE senses, because they are Zipf-thin (~1–2 instances). On the chain the climb
stalls exactly here: glass-box consolidation HURTS rare senses (worse than a shuffled twin — mis-resolution binds the
dominant sense's associates onto the rare one), and EVEN A PERFECT resolver doesn't help rare senses (too few
instances) though it helps well-attested ones (+0.034 all-population). Ceiling ~0.34; the 0.34→~0.53 gap is
broad-coverage correctly-resolved rare-sense EXPERIENCE — not a better encoder, readout, or more knowledge.

CONTROLS (each excluded a distinct rival; two caught FALSE PASSes):
- shuffled-grounding / shuffled-diagnosticity / shuffled-W twins (all lose CI-sep on the arms that carry signal).
- MFS no-regression guard: caught the anti-dominant "0.382" as a PRIOR SHIFT (helps subordinate only by hurting dominant).
- strict INDUCTIVE (train-only) W: caught the knowledge-integration "0.360" as TRANSDUCTIVE LEAKAGE (clean 0.261).
- chance-control on ORACLE_single (real gold +0.15 over random; ~72% was combinatorics).
- oracle decomposition + gold-resolution ceiling (localizes the loss to consolidation/coverage, not readout/keys).

FILES: experiments/exp_atl_hubspoke_{grounded_separability, query_side_readout, grounded_disambiguate_then_bind,
discourse_situation_prior, ideal_full_chain, contextual_recompute, joint_ppr_recompute, ppr_signal_loss,
actr_ideal_chain, multicue_integration, signal_loss_ladder, controlled_retrieval[_gated], knowledge_integration,
signal_trace_v2, context2vec_aligned, full_chain_signal_trace}_v1.py ; verification/test_atl_hubspoke_meaning_channel.py
(W1–W8); notes/research_{grounded_disambiguate_then_bind, exemplar_based_contextual_recomputation_wsd,
lfs_rare_sense_enabler_knowledge_vs_context}_2026-09-04.md ; AUDIT UPDATE folded for BRAIN_FOUNDATIONAL_AUDIT §2b.

FOR STRATEGY (Q111): LAND the precision-weighting readout refinement — add a gamma/top-k precision-sharpening
parameter to hdlab/diagnostic_context_wsd (default gamma=1 = byte-identical), +0.023 CI-sep, twin-losing, no MFS
regression, stacks with any future knowledge. DO NOT wire the grounded hub into the keys (measured null), DO NOT grow
reading-derived W default-on (glass-box consolidation regresses the consumer set), DO NOT chase a general trained
encoder (not brain-foundational; scale-bound 0.192→0.207).

NEXT PROBLEM (this problem earns it): GROW BROAD-COVERAGE, CORRECTLY-RESOLVED RARE-SENSE EXPERIENCE (the learner-on /
consolidation north star) — the only lever that thickens the rare-sense signal without crossing the invariant.
Mechanism: grounding-anchored PROPOSE-AND-VERIFY BOOTSTRAPPING (Trueswell 2013) — resolve confident/concrete cases
first, bind, let the growing store resolve harder cases, iterated ONLINE over a large corpus; admit only through the
owner-DONE consolidation_gate + cls_growth. Acceptance test (proven here): recover the rare-sense gain as coverage
grows WITHOUT dominant regression, with a strict INDUCTIVE train-only W + shuffled twin (two false PASSes this
session were caught only by those controls).

DO NOT QUOTE: the knowledge-integration "0.360" or anti-dominant "0.382" (both artifacts, refuted by controls); the
0.53/0.65 transformer/human numbers as achievable glass-box.

TLDR (plain English): We built the meaning-hub the brain's way, end to end, and the score climbs — read the sentence,
build rich meaning-keys, then use the brain's "focus on the one telling word" step — up to about 0.34, with that
focusing step the biggest single win (and it's landable). Then it stops, at the stage where the reader should learn
from experience which words signal a rare meaning. It stalls there for one measured reason: rare meanings barely
occur, so there's almost nothing to learn from — and guessing the meaning to learn from makes it worse than random;
even handing it perfect answers doesn't help the rare cases (too few examples) though it helps common ones. The thing
that actually cracks rare meanings is re-computing each word in its sentence, which needs either a big pretrained
model (the line we won't cross) or a lifetime of rare-sense reading. So the chain is right, the gap is pinpointed —
lack of rare-sense experience to consolidate — and the next problem should grow that experience safely over time.

QUESTIONS: one, and it's the owner's — hold the no-transformer invariant and accept the ~0.34 glass-box ceiling on
rare senses (the brain-faithful chain is proven complete and correct to there), or relax it for one offline
contextual-sense asset to reach ~0.53? Recommendation: hold the invariant; pursue the coverage/learner-on route.

NEXT STEPS: (1) land precision-weighting (the +0.023 readout win). (2) open the next problem = broad-coverage
correctly-resolved rare-sense experience via grounding-anchored bootstrapping + the consolidation gate. (3) do not
reinvest in grounding, static knowledge, or a general trained encoder — all measured negatives here.
