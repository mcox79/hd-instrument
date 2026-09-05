---
problem: wire_the_curated_meaning_foundation_into_a_live_consumer_and_adopt_the_maxsim_usage
status: PARTIAL
bar: "PASS = the curated foundation wired into a LIVE read()-time consumer (the who-did-what/argument path via a MaxSim-usage composed_hub_predictor rebuilt on the curated vectors, and/or the meaning readout stacking store-KEYS + gamma + sense_prior) such that the LIVE consumed metric rises CI-separated over the current live reader, an info-free twin (shuffled-knowledge or verb-shuffled-exemplar) LOSES, and NO other dim regresses (each on its right instrument). Turn it ON if net-positive (no-default-off); keep OFF only with a measured reason. Report CI half-width + null p95; recompute floors per population. A rigorous located NEGATIVE -- the better KB + better usage does not move the live consumer, with the named cause (e.g. the who-did-what live path is parse/attachment-bound, or the meaning readout has no live stage yet and building it is the S2-boundary decision) -- is a FULL PASS."
result: "REROUTED (the brief's two proposals are located negatives; the disk outranks the brief). The curated meaning foundation, wired as taxonomic sense signatures read against context on gold WiC (the board's ONE live meaning-consumed metric, via grounded_semantic_graph.select_sense / PPR), is the FIRST glass-box mechanism to achieve CI-SEPARATED REAL per-context sense discrimination -- it beats its mis-seeded-context twin (WiC dev n=638 +0.0831 CI[+0.038,+0.128]; test n=1400 +0.0929 CI[+0.063,+0.123]; both CI-sep) AND its shuffled-signature info-free twin (+0.0309 CI[+0.019,+0.043] CI-sep), where the live PPR select_sense reader (0.618, real-minus-twin +0.047 NOT-sep) and the gloss/associative baseline (dev +0.0266 NOT-sep) FAIL. Leak-free curated WiC acc = 0.624 (dev) / 0.653 (test) / 0.650 (dev+test), majority floor 0.500. The CURATED KNOWLEDGE is the lever (gloss-only fails the mis-seeded twin on dev; curated crosses it on the SAME split). HONEST NEGATIVES on the upstream levers: the biased-competition diagnostic readout does NOT beat the flat readout on WiC (it is the a_s lever, not the WiC lever); the ATL distinctive-feature/whitening projection HURTS WiC monotonically (as it hurts a_s). The raw-accuracy ceiling (~0.65 leak-free vs 0.80 human) is the CONTEXTUAL INPUT ENCODING (build_sg_lite's invariant-boundary owner decision), NOT sense-signature richness or the readout."
floor: "Majority-class floor 0.500 (balanced WiC). Strongest LIVE-READER floor = the live PPR select_sense reader (landed exp_ppr_spreading_activation_wsd_wic_v1): dev acc 0.618, real-minus-twin +0.047 NOT-sep (the live reader does NOT achieve real per-context discrimination). Leak-free curated dev acc 0.624 is NOT CI-separated above PPR 0.618 on RAW accuracy -- this is the honest PARTIAL bound. The CI-SEPARATED wins are on the DISCRIMINATION MARGIN: curated beats its mis-seeded-context twin +0.083 (dev) / +0.093 (test) CI-sep where PPR does not (+0.047 not-sep), and beats its shuffled-signature info-free twin 0.613 (curated 0.644, +0.031 CI-sep). Gloss-only baseline (the associative floor) FAILS the mis-seeded twin on dev (+0.027 not-sep) -> the CURATED knowledge is the lever."
controls: "(1) mis-seeded-context twin (side-2 sense assigned from a RANDOM other sentence's context) -- the decisive per-context-discrimination control: curated LOSES to nothing / beats it CI-sep on both held-out splits, so the accuracy is genuine context-driven discrimination, not dominant-sense agreement structure (which is what the disk's earlier 'no method beats its twin' negative caught). (2) shuffled-signature info-free twin (curated signatures permuted onto WRONG synsets) LOSES CI-sep (+0.031) -> it is the CORRECT sense<->signature binding, not the machinery. (3) shuffled-diagnosticity twin LOSES (+0.008 CI-sep). (4) LEAK control: the FROZEN asset includes synset.examples() and WiC was built from WordNet/Wiktionary example sentences, so the frozen asset is leak-INFLATED on WiC (0.721 vs the leak-free curated rebuild 0.644) -> the honest WiC number is the leak-free rebuild; the frozen asset's on-WiC number must NOT be quoted. (5) gloss-vs-curated ablation isolates the CURATED KNOWLEDGE as the lever. (6) readout ablation (flat vs diagnostic) and whitening sweep (all-but-the-top k=0..20) both LOCATED-NEGATIVE the a_s-levers on WiC. Each control excludes a distinct rival: agreement-structure / machinery / diagnosticity-shape / examples-leak / knowledge-vs-gloss / readout-vs-input."
files_changed: "experiments/exp_curated_foundation_wic_v1.py (the leak-free curated-foundation WiC channel + all arms/controls), experiments/exp_curated_foundation_wic_whiten_v1.py (the ATL distinctive-feature/whitening upstream-optimization sweep -- located negative), verification/test_curated_foundation_wic.py (scaffold-free witness 5/5), notes/problems/<slug>/RESEARCH_wic_sense_discrimination_neuro.md (4-lit-scan brain-foundational confirmation + the fabricated-citation catch), data/exp_curated_foundation_wic_v1/metrics.json, data/exp_curated_foundation_wic_whiten_v1/metrics.json. NO hdlab/ writes."
reverify: ".venv/Scripts/python.exe verification/test_curated_foundation_wic.py  (5/5)"
---

## SUBMISSION SUMMARY (read first)

**The brief's two proposals are located negatives, on disk, so I rerouted to the REAL problem underneath
(get the curated foundation onto a LIVE board dimension) and crossed a wall the disk had declared uncrossed.**

**WHY THE BRIEF'S TWO PROPOSALS ARE LOCATED NEGATIVES (disk outranks the brief):**
1. **who-did-what via `composed_hub_predictor` (MaxSim): parse/attachment-bound.** `composed_hub_predictor` is
   FULLY islanded (no live importer in `hdlab/`; `situation_reader` imports none of the meaning-line organs).
   The dormant-organ wire of the verb-role exemplar store was already MEASURED live and REGRESSED PATIENT
   accuracy **-0.1864 CI[-0.280,-0.102]** on modern QA-SRL (commit `bf4258b52`): the current reader (0.644)
   already exceeds the store's best integrated number (0.505), and position log-softmax swamps the exemplar
   margin. The brief's own named cause ("the who-did-what live path is parse/attachment-bound") is correct.
2. **the meaning readout (`diagnostic_context_wsd`): no live read()-time consumer exists** (the
   `reader_meaning_channel` stage; `read()` is sense-blind, one blended vector per lemma). So there is no
   live stage to stack store-KEYS + gamma + sense_prior onto -- yet.

**THE REROUTE (the real problem): the board's ONE live meaning-consumed metric is WiC via
`grounded_semantic_graph.select_sense` (PPR spreading activation).** That is a live read()-time consumer of
sense selection, and the curated foundation is literally a sense-signature store. So I wired the curated
foundation into WiC and measured it.

**THE RESULT -- a wall CROSSED.** Every prior glass-box WiC method plateaus ~0.62 but FAILS its mis-seeded twin
(the disk's conclusion: "the accuracy is MFS-agreement structure, NOT real per-context discrimination"):
`exp_glassbox_sense_embeddings_wic_v1` (all real>twin=False), `exp_ppr_spreading_activation_wsd_wic_v1`
(PPR = the live reader, 0.618, real-minus-twin +0.047 NOT-sep). **The curated meaning foundation is the first
to cross it:** it beats its mis-seeded-context twin +0.083 (dev) / +0.093 (test), BOTH CI-separated, and its
shuffled-signature info-free twin +0.031 CI-sep. The CURATED KNOWLEDGE is the lever -- gloss-only FAILS the
twin on the same dev split (+0.027 not-sep) while curated crosses it. This is real per-context sense
discrimination on the one live meaning metric, glass-box, NO LLM.

**WHY IT IS "PARTIAL" AND NOT "SOLVED" (the honest bound):** on RAW aggregate WiC accuracy the curated channel
(~0.65 leak-free) is only marginally above the live PPR reader (~0.62) -- because BOTH also get the easy
dominant-sense / monosemous items right, so the aggregate is diluted by items where context is not the
deciding factor. The CI-separated wins are on the DISCRIMINATION MARGIN (real-vs-twin) and the shuffled-signature
twin, not (cleanly) on raw-accuracy-over-the-live-reader. The raw-accuracy ceiling (~0.65 vs 0.80 human) is the
CONTEXTUAL INPUT ENCODING -- the SAME invariant-boundary owner decision `build_sg_lite` reached on a_s -- not a
knowledge or readout gap.

## EVERY COMPONENT, UPSTREAM AND HERE, EVALUATED FOR BRAIN FOUNDATION (owner's directive)

The owner's directive: overcome the wall by making EVERY component -- this one and every upstream -- brain
foundational, and confirm no downstream consumer regresses. I prototyped the full chain:

| component | brain structure (PINNED / OUR-INVENTION) | on WiC | verdict |
|---|---|---|---|
| **curated sense signatures** (KEY) | ATL amodal hub, taxonomic/feature similarity (Patterson-Nestor-Rogers 2007; Lambon-Ralph 2017) [PINNED structure] | **the lever** -- crosses the discrimination wall CI-sep | KEEP (the win) |
| **biased-competition diagnostic readout** (QUERY) | LIFG/pMTG semantic control; GCM attention weight (Nosofsky 1986), precision-gain (Feldman-Friston 2010) [PINNED components] | DIAG ~= FLAT (d=-0.002) -- **neutral on WiC** (it is the a_s lever) | located negative here |
| **ATL distinctive-feature / whitening** (KEY transform) | ATL privileges DISTINCTIVE features = decorrelation (two-meaning-systems owner-DONE) [PINNED op] | all-but-the-top HURTS monotonically (k0 0.650 -> k20 0.616) | located negative here |
| **contextual input encoder** (QUERY representation) | recompute the token in context (Klepousniotou 2007; Rodd 2002) [PINNED gap] | the raw-accuracy ceiling; NOT built (invariant boundary) | the owner's S2 decision |

**Research-confirmed (4 parallel lit-scans, `RESEARCH_wic_sense_discrimination_neuro.md`), with an honest catch:**
MFS-is-chance-on-WiC is PINNED (Pilehvar-Camacho-Collados 2019 verbatim -- WiC is the regime where the frequency
prior that swamps every other meaning-line result is structurally useless); the diagnosticity weighting has a
formal basis (Nosofsky GCM attention weight); the taxonomic/thematic double dissociation is PINNED (Schwartz
2011 PNAS). **DROPPED as unsupported:** "a definition is worth many contexts (Borman & Lupyan)" -- that citation
is FABRICATED (and it sits in `exp_sense_wall_breakthrough_wic_v1`'s docstring; flagged for correction), and the
one direct definition-vs-context study (Fischer 1994) found the OPPOSITE. So I do NOT claim definitions beat
contexts; the defensible claim is narrower -- RICHER taxonomic sense SIGNATURES make the CONTEXT discriminate.

## DOWNSTREAM NO-REGRESS (owner's directive: confirm no consumer regresses; revisit consumers for brain fidelity)

- **No change to the shared frozen asset is proposed** -- the WiC wire ADDS a read-time consumer that reads the
  raw signatures; it does not modify `meaning_sense_signatures_v1.npz`. So the a_s / `diagnostic_context_wsd`
  consumer (the foundation's validated +0.0755) is UNTOUCHED and cannot regress.
- **The whitening projection WOULD regress a_s** (the foundation MEASURED all-but-the-top hurts a_s 0.319->0.210)
  -- so even had it helped WiC (it did not), it would have to be a per-consumer, task-gated PROJECTION (the
  brain's semantic control; the foundation's own "consumers disagree on the ideal prune -> per-consumer
  projection" next-step), never a shared-asset change. It is a located negative on WiC anyway, so nothing to gate.
- **`composed_hub_predictor` / who-did-what** reads a DIFFERENT asset (`hub_ppmi_svd_200d`) on a DIFFERENT path;
  unaffected. Its own live wire is the separate located negative (`bf4258b52`).
- **Adjacent consumer to revisit (seed for strategy):** the live `select_sense` (PPR) is the ASSOCIATIVE/thematic
  system doing a TAXONOMIC job (sense discrimination) -- the two-meaning-systems mismatch, made concrete on a live
  metric. The brain-foundational upgrade is to add the curated taxonomic-signature channel to `select_sense`
  (blend cos(context, curated-signature) with the PPR activation), which is exactly this problem's wire.

## THE EXACT SIGNAL-LOSS / MECHANISM (why curated crosses where gloss and PPR do not)

Richer, more sense-DISCRIMINATIVE signatures make the sense pick genuinely CONTEXT-DEPENDENT: with curated
signatures the mis-seeded (wrong-context) twin DEGRADES (real-minus-twin +0.08/+0.09), because the correct
context is doing real selection work. Gloss-only and PPR signatures are blurrier / topic-level, so both the real
and the mis-seeded pick collapse to the dominant sense -> the twin does NOT degrade -> no discrimination
(real-minus-twin +0.03/+0.05, not-sep). This is the wall-breakthrough's predicted "knowledge-band needs richer
sense embeddings", now delivered and twin-controlled. The residual (raw ~0.65 vs human 0.80) is the sense-
conflated w2v INPUT (one vector per surface form), the contextual-encoder invariant boundary.

## KEY REALIZATIONS

- **The disk's "no glass-box method beats its WiC twin" was measured on dev ONLY (n=638) and was
  under-powered/under-knowledge'd.** The curated foundation crosses it on that SAME dev split -- the enabling
  move was rebuilding the sense signatures with the CURATED knowledge (relations+SyntagNet+ConceptNet) in the
  OURS w2v space and pairing real-vs-mis-seeded-twin, which turns "does context genuinely decide" into a
  can-fail number. Gloss-only in the same harness FAILS the twin; curated crosses. The knowledge, not the
  harness, is the difference.
- **The a_s lever and the WiC lever are DIFFERENT, and that is a two-systems signature.** Biased competition
  (diagnostic readout) is THE a_s lever (+0.039) and NEUTRAL on WiC; the curated knowledge is THE WiC lever and
  a smaller a_s lever. WiC is discrimination (is the pick context-driven?), a_s is rare-sense selection (which
  specific subordinate sense?). Copying the a_s fix onto WiC (readout, whitening) is a located negative -- a
  concrete instance of "sweep the parameter, do not adopt the number/mechanism from a different problem."
- **A frozen "foundation" can be LEAK-INFLATED on a specific benchmark without being wrong.** The curated
  signatures include `synset.examples()` (legitimate knowledge for general WSD), but WiC was CONSTRUCTED from
  those example sentences, so the frozen asset scores 0.72 on WiC by partial leak; the leak-free rebuild is 0.64.
  You only see it if you rebuild leak-free and compare. Quote the leak-free number.
- **A research drill caught a FABRICATED citation load-bearing in a sibling cell's docstring.** "Borman &
  Lupyan" does not exist; the honest literature (Fischer 1994) runs the other way. The mechanism did not need
  that claim -- but the code repeats it, so it is flagged for correction.

## PROPOSED hdlab CHANGE (strategy lands it, Q111)

The clean, brain-foundational wire (a per-consumer taxonomic-signature channel on the live WiC/select_sense path):

1. **Add a curated-signature sense-identity channel to `hdlab/grounded_semantic_graph.select_sense`** (and
   `select_sense_blended`): for the target's candidate synsets, score `cos(context_query, meaning_foundation
   .sense_signature(syn))` (the FLAT readout is sufficient on WiC; the diagnostic readout is the a_s path, not
   this one), and BLEND it (z-fusion) with the existing PPR activation. Default-OFF flag; witness =
   `test_curated_foundation_wic.py`. This adds the ATL taxonomic system to the reader's currently associative-only
   sense selection.
2. **Do NOT wire the biased-competition readout or the whitening projection into the WiC path** -- both are
   located negatives there (they are the a_s levers).
3. **On the leak:** the live WiC board number must be computed with the leak-free signatures (examples excluded)
   OR the leak flagged; the frozen asset's raw on-WiC number over-reports by ~+0.08.
4. **Correct the fabricated "Borman & Lupyan" citation** in `experiments/exp_sense_wall_breakthrough_wic_v1.py`.

Because the raw-accuracy gain over the live reader is marginal (the discrimination margin is the CI-sep win), this
is a "turn ON for the discrimination capability, measure the live WiC board dim before any capability claim" wire,
per no-default-off -- NOT a raw-accuracy default-on. The raw-accuracy lever past ~0.65 is the contextual encoder
(owner S2 decision).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)

- **MEANING channel / WiC (the one live meaning-consumed metric):** the curated foundation, as a TAXONOMIC
  sense-signature channel, is the first glass-box mechanism to cross the WiC per-context discrimination wall
  (beats mis-seeded + shuffled-signature twins CI-sep) where the live PPR (associative) reader fails. Pins the
  two-meaning-systems deviation on a LIVE metric: `select_sense` is the associative system doing a taxonomic job.
- **The a_s biased-competition readout does NOT transfer to WiC** (neutral); the ATL whitening op HURTS WiC (as
  it hurts a_s). WiC lever = curated knowledge in the mean-pooled signature; a_s lever = the readout. Different
  problems, different levers -- record so neither is copied onto the other.
- **`composed_hub_predictor` remains islanded**; the who-did-what live wire is confirmed parse/position-bound
  (`bf4258b52`), independent of this problem.
- **CODE DEFECT:** `exp_sense_wall_breakthrough_wic_v1` docstring cites a FABRICATED "Borman & Lupyan"; the
  curated signature bags include `synset.examples()` (a WiC-specific leak, not an a_s leak).

## WHAT I DID NOT ESTABLISH, AND WOULD WITHDRAW FIRST IF WRONG

- I did NOT establish that raw WiC accuracy rises CI-separated over the live PPR reader -- the CI-sep wins are on
  the discrimination margin and the info-free twins, not the aggregate. If one claim falls first, it is any
  reading of this as a raw-accuracy-beats-the-live-reader result; it is a per-context-DISCRIMINATION result.
- The "WiC = taxonomic/ATL task" framing is a well-motivated HYPOTHESIS (taxonomic/thematic dissociation +
  homonymy/polysemy processing), NOT a directly-tested routing claim (the research flagged this gap honestly).
- The contextual-input-encoding ceiling (~0.65 -> 0.80) is asserted from `build_sg_lite`'s proven a_s ceiling +
  the input-representation literature, not re-measured end-to-end on WiC here.

## TLDR (plain language)

The reader has a clean, curated dictionary of word-meanings but nothing in the live reader actually uses it, so
its proven benefit reaches no score. The task asked to plug it into the "who did what" part of the reader, but
that part is already limited by grammar-parsing, not by knowledge (a past experiment showed plugging the store in
there makes it WORSE), so that door is closed. I found the door that IS open: the one live test of word-meaning
the reader is scored on is "do these two sentences use this word in the same sense?" -- and I plugged the curated
dictionary in there. For the first time, a glass-box method (no outside AI) genuinely uses the CONTEXT to tell
the senses apart on that test -- proven by a control where feeding it the wrong sentence makes it fail, and a
control where scrambling the dictionary makes it fail. The catch: the overall score only edges up a little,
because both the old and new methods get the easy cases right; the real, measured improvement is that the new
method's correctness is EARNED from context rather than from always guessing the common meaning. Getting the
overall score much higher needs a genuinely context-sensitive re-reading of each word, which is the separate
"do we allow a trained encoder" decision. Along the way a literature check caught a made-up citation the code was
leaning on, and a hidden overlap between our dictionary and this specific test that inflates the number if you
are not careful.

## QUESTIONS

None blocking. One judgment for the owner: this is a real per-context-discrimination win on the live WiC metric,
but NOT a raw-accuracy default-on -- the raw-accuracy lever past ~0.65 is the contextual-encoder S2 decision. I
recommend landing the curated-signature channel default-OFF with the WiC witness as the gate, and treating the
raw-accuracy ceiling as the (separate) contextual-encoder fork.

## NEXT STEPS (ranked, for strategy)

1. **LAND the curated-signature sense-identity channel on `select_sense`/`select_sense_blended`** (default-off,
   `test_curated_foundation_wic.py` the gate; leak-free signatures for the board number). Adds the taxonomic
   system to the reader's associative-only sense selection -- the two-meaning-systems fix on a live metric.
2. **Do NOT wire the diagnostic readout or whitening into the WiC path** (located negatives there); keep the
   diagnostic readout for the a_s path (where it is the lever).
3. **The raw-accuracy ceiling (~0.65 -> 0.80) is the contextual-input-encoding fork** -- the same owner S2
   decision `build_sg_lite` surfaced; not a knowledge or readout lever.
4. **Fix the fabricated "Borman & Lupyan" citation** and note the `synset.examples()` WiC-leak in the curated
   signature build (harmless for a_s, inflating for WiC).
5. **Stratify WiC by homonymy vs polysemy** (the pinned prediction: homonyms easiest, polysemy hardest) to
   target the next knowledge acquisition -- a low-cost follow-on.
