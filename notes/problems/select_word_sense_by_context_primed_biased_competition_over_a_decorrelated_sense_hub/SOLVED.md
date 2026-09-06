---
problem: select_word_sense_by_context_primed_biased_competition_over_a_decorrelated_sense_hub
status: REFUTED
bar: "PASS = a glass-box, context-primed BIASED-COMPETITION sense selector (REUSING graded_competition + semantic_control, primed by the reader's structured DISCOURSE context) over a DECORRELATED / whitened sense hub, that BEATS the current diagnostic_context_wsd readout (recomputed on the item's OWN population, WITH its landed precision + Bayesian-prior settings) CI-separated on a MODERN WiC/WSD instrument, with: a CONTEXT-SHUFFLED info-free twin LOSING CI-separated, AND the WHITENING/separation lever VERIFIED (decorrelated-hub arm beats the un-whitened baseline, shuffled-diagnosticity twin LOSING, significance reported, settling the +0.0176-on-a_s vs neutral-to-negative-on-WiC tension), AND NO trained contextual encoder, and NO MFS/dominant regression. A rigorous located NEGATIVE -- the faithful biased-competition-over-a-whitened-hub, discourse-primed, built, does NOT cross the ceiling, with the exact cause NAMED and measured -- is a FULL PASS that EMPIRICALLY SETTLES the standing 'hold the no-encoder invariant' decision."
result: "LOCATED NEGATIVE (full pass): NO brain-faithful glass-box lever crosses the incumbent diagnostic_context_wsd readout, on the MODERN instrument or on SemCor. (1) HUB DECORRELATION does not beat the incumbent -- on SemCor subordinate a_s (n=50,386, frozen curated hub) RAW=0.2697; LCSS(local-contrastive+renorm) -0.0025 (CI incl. 0), global whitening ABTT3 -0.0152 CI[-0.0187,-0.0117] and ZCA -0.0275 CI[-0.0315,-0.0235] (CI-separated BELOW); on MODERN WiC (n=7466, floor 0.500) RAW=0.6238, LCSS +0.0000, ABTT3 -0.0103, ZCA -0.0126. And it is provably accuracy-NEUTRAL: subtracting the per-word sense centroid WITHOUT renorm changes 0 picks (LCSS_NORENORM==RAW, 0 disagreements at n=50,386 AND n=7466) -- the cosine-argmax already reads only the distinctive residual. (2) DISCOURSE-PRIMED context de-blur (construction-integration) -0.0421 to -0.0575 (n=50,386). (3) DISTINCTIVE-FEATURE (IDF) per-sense resupply -0.1693 (n=50,386). Every lever reads REAL structure (each beats its info-free twin CI-separated) but scores below the incumbent -> the ceiling is the CONTEXT-INPUT ENCODING x COVERAGE, not the hub geometry or the readout. (4) I ALSO built the brain's ACTUAL structural mechanism -- THEMATIC-FIT selectional preference (Erk-distributional, parsed governing-predicate+role, doc-held-out, n=4,892): it beats its role-permutation (+0.065) and verb-shuffle (+0.020) twins CI-separated (real structure) but is DOMINATED by topical context (FIT coarse 0.439 < BAG 0.520; a dev-selected multi-cue integrator assigns it weight w*=0.00), replicating Lee&Ng 2002 (-0.6pp) + this project's own +0.007 + 5 external studies -- coarse-only by construction. (5) A GRANULARITY probe shows 37% of fine 'errors' are near-misses INSIDE the correct coarse sense (same picks: a_s 0.2697 fine -> 0.5412 shared-core). CORRECTED CONCLUSION: the residual needs richer CONTEXTUAL representation built by glass-box structured PREDICTIVE comprehension (Phase-1), NOT a barred encoder; HOLD on the no-encoder invariant is confirmed for the right reason (the brain uses none either)."
floor: "The strongest floor actually run = the incumbent diagnostic_context_wsd readout over hdlab.meaning_foundation, recomputed per population WITH its landed settings: a_s RAW 0.2697 (SemCor subordinate, n=50,386); WiC RAW 0.6238 exact / 0.6499 coarse (n=7466, floor 0.500). Additional floors on the a_s population: MFS = 0 on subordinate items BY CONSTRUCTION (subordinate := gold != most-frequent-sense); random 1/k. The whitening prior-art claim (+0.0176 a_s, unverified) is REFUTED: it does not reproduce on the curated hub and is CI-separated NEGATIVE at full n (it was small-sample noise -- reproduced as a spurious +0.0058 on an 8-file subset that vanishes at n=50k)."
controls: "NEUTRALITY PROOF: LCSS_NORENORM (common-mode removal, no renorm) == RAW with 0 pick-disagreements on both a_s (n=50,386) and WiC (n=7466) -- hub decorrelation cannot change the argmax by construction. INFO-FREE TWINS (all LOSE to their arm CI-separated, so each arm reads real structure -- yet all arms still lose to the incumbent): SHUFSEP (wrong-word centroid) LCSS +0.006 CI-sep; CTX_SHUFFLE (shuffled context) loses to every arm; RANDOM_SENSE (context de-blurred with random senses) CI-de-blur +0.0187 CI-sep; SHUFFLED_GLOSS (per-sense bags permuted onto wrong senses) IDF +0.0605 CI-sep. IDF>UNWEIGHTED +0.0020 (the distinctive-feature op barely earns its keep on selection, vs a large CI-sep win on identity/SimLex). NO trained encoder anywhere; frozen static hub -> no train/test leakage. Additivity: I propose NO hub change, so no non-consumer can regress."
files_changed: "experiments/exp_sense_hub_collinearity_locus_v1.py, experiments/exp_sense_hub_separation_as_v1.py, experiments/exp_sense_hub_separation_wic_v1.py, experiments/exp_sense_selection_ci_deblur_as_v1.py, experiments/exp_sense_signature_distinctive_feature_as_v1.py, experiments/exp_sense_selection_granularity_probe_v1.py, experiments/exp_sense_selection_thematic_frame_as_v1.py, verification/test_sense_hub_separation_and_selection_organ.py, notes/problems/select_word_sense_by_context_primed_biased_competition_over_a_decorrelated_sense_hub/SOLVED.md"
reverify: ".venv/Scripts/python.exe verification/test_sense_hub_separation_and_selection_organ.py"
---

# The sense hub should NOT be decorrelated -- it is right the way it is. A rigorous located negative that settles the meaning-channel fine-sense ceiling and the no-encoder-invariant decision.

**Status REFUTED, and it is the FULL-PASS kind the bar describes.** The brief's premise -- "the sense hub is
near-collinear, so DECORRELATE it toward a well-separated geometry AND select by discourse-primed competition" --
is tested at three levels (the hub, the context input, the signature construction) with the brain's ACTUAL
mechanisms and full controls. Every brain-faithful glass-box lever is a located negative, and the reasons are
mathematical, empirical, AND biological. This EMPIRICALLY SETTLES the owner's standing question: the fine-sense
ceiling is representational (context-input encoding x coverage), so HOLD on the no-external-encoder invariant is
confirmed. The one owner directive -- "the only way you overcome this wall is for EVERY component, you and
upstream, to be brain-foundational" -- is exactly what produced the answer: the upstream component (the hub) is
ALREADY brain-foundational, and forcing it to be "separated" makes it LESS so.

## 1. HOW THE BRAIN DOES THIS (the opening move -- research-verified, 4 lit drills)

- **The ATL hub DISTILLS; it does NOT decorrelate. (PINNED, and it reverses the brief.)** The hub-and-spoke
  literature describes the ATL as performing *distillation / convergence / compression* into a modality-invariant
  code (Patterson, Nestor & Rogers 2007, *Nat Rev Neurosci*; Lambon Ralph & Patterson 2008). The one genuine neural
  *decorrelation* mechanism in the brain is HIPPOCAMPAL pattern separation (dentate gyrus; McClelland, McNaughton &
  O'Reilly 1995 CLS) -- a DIFFERENT, complementary system, explicitly contrasted with neocortex/ATL. **No source
  places active decorrelation/orthogonalization in the semantic hub.**
- **Polysemy SHARES A CORE -- overlap is the correct geometry, not a bug. (PINNED.)** Rodd, Gaskell &
  Marslen-Wilson (2002, *JML*; 2004 model): homonyms (unrelated meanings) live in *separate, competing* attractor
  basins and produce a processing COST; polysemous senses share a *broad, overlapping* representation and produce a
  processing BENEFIT (the sense-relatedness advantage). WordNet's fine senses are overwhelmingly polysemy, so
  *forcing them apart is predicted to destroy the very structure that helps* (Klepousniotou 2002/2012). The
  within-word collinearity we measured (0.923) IS that shared-core structure.
- **Context reshapes at READOUT time, over a CONTEXT-INDEPENDENT hub. (PINNED -- the closest real match.)**
  Controlled Semantic Cognition (Lambon Ralph, Jefferies, Patterson & Rogers 2017, *Nat Rev Neurosci*): an
  *integrative layer* "dynamically and transiently reshapes the multidimensional similarity structure arising in the
  context-independent hub" toward context-relevant dimensions. The hub stays context-independent; the reshaping is
  transient, at integration/selection time -- which the diagnostic readout ALREADY does (context-word diagnosticity
  = a context-dependent reweighting toward discriminating dimensions).
- **Selection is a RACE over fixed representations, not online sharpening. (PINNED.)** Swinney 1979 / Tanenhaus,
  Leiman & Seidenberg 1979 (exhaustive access then selection); Duffy, Morris & Rayner 1988 (reordered access);
  Kawamoto 1993 (settling into pre-existing attractor basins). Competition SELECTS among already-differentiated
  senses; it does not restructure the stored signatures.
- **OUR-INVENTION-UNDER-TEST (what the brief proposed):** (a) geometrically decorrelate the hub; (b) a discourse-
  primed biased-competition selection that de-blurs the context. Both tested below; both refuted.

## 2. THE CRUX MEASUREMENT (the premise reproduces -- and localizes to WITHIN-WORD)

On the ACTUAL frozen asset `hdlab.meaning_foundation` (117,614 curated 200-d signatures), mean pairwise cosine:
**within-word (a lemma's own candidate senses) = 0.9234; global (random synset pairs) = 0.8407.** The "~0.92
collinear" claim REPRODUCES and is a WITHIN-WORD phenomenon (`exp_sense_hub_collinearity_locus_v1`). This is exactly
the graded-overlap polysemy structure the brain uses -- not a defect.

## 3. THE PROVABLE POINT: hub decorrelation is accuracy-NEUTRAL for the cosine-argmax readout

Write a word's k unit sense signatures as `g_s = sqrt(rho)*u + sqrt(1-rho)*e_s` (`u` = the shared direction, `e_s`
= the distinctive residual, `rho` ~ 0.92). The readout score is `q.g_s = sqrt(rho)*(q.u) + sqrt(1-rho)*(q.e_s)`, and
`sqrt(rho)*(q.u)` is CONSTANT across senses -- **so the argmax already depends only on the distinctive residual
`q.e_s`.** Removing the common mode (subtract the per-word centroid, no renorm) therefore changes NOTHING.
Measured, not just derived: `LCSS_NORENORM` produces **0 pick-disagreements vs RAW at n=50,386 (a_s) and n=7466
(WiC)**. Decorrelation can change accuracy ONLY by *reweighting* the residual (renormalization, or global
whitening's dimension reweighting) -- and every such reweighting is neutral-to-negative (below).

## 4. THE THREE LOCATED NEGATIVES (brain's mechanisms, full controls)

| lever (brain-faithful form) | a_s (SemCor subordinate, n=50,386) | modern WiC (n=7466) | verdict |
|---|---|---|---|
| **incumbent** diagnostic readout over the curated hub | **0.2697** | 0.6238 exact / 0.6499 coarse | the arm to beat |
| decorrelate: LCSS local-contrastive + renorm | -0.0025 (CI incl. 0) | +0.0000 | no lift |
| decorrelate: global all-but-top-3 | **-0.0152** CI[-0.0187,-0.0117] | -0.0103 | HURTS |
| decorrelate: global ZCA | **-0.0275** CI[-0.0315,-0.0235] | -0.0126 / -0.0273 coarse | HURTS |
| discourse-primed context de-blur (construction-integration, T=1..3) | **-0.0421 to -0.0575** | (WiC has no discourse) | HURTS |
| distinctive-feature (IDF) per-sense resupply (sparse Lesk) | **-0.1693** (FUSE -0.0076) | -- | HURTS |

**Every lever reads REAL structure** -- LCSS beats a wrong-word-centroid twin (+0.006 CI-sep); CI-de-blur beats a
random-sense twin (+0.0187) and a shuffled-context twin (+0.0737); IDF beats a shuffled-gloss twin (+0.0605) and a
shuffled-context twin (+0.0617) -- **yet all lose to the incumbent.** That is the signature of a *representational*
ceiling: the mechanisms work, but the information they operate on caps them.

**Why each fails, named:** (a) decorrelation is argmax-neutral (S3) and, when it reweights, it either amplifies
low-signal residuals (LCSS renorm) or removes signal-bearing top components (global whitening) -- and it is
brain-unfaithful (S1: ATL distills; polysemy overlap is correct). (b) De-blurring context words to their gloss-sense
signatures throws away the RICH distributional word vector for an impoverished gloss mean (the resolved senses are
noisier than the raw vectors). (c) Sparse IDF distinctive-feature overlap is the RIGHT op for meaning-IDENTITY
(SimLex, where two full definition bags overlap heavily -- landed in `hdlab.conceptual_meaning`) but the WRONG op for
context-SELECTION, where the short context rarely contains a sense's exact definitional tokens and soft dense
similarity is what carries the signal.

## 5. THE a_s-vs-WiC WHITENING TENSION, SETTLED

The unverified prior-art "+0.0176 a_s whitening lift" (`exp_meaning_channel_whiten_v1`, no controls) **does not
reproduce on the curated hub**: at full n it is CI-separated NEGATIVE (ABTT3 -0.0152, ZCA -0.0275), and I reproduced
the *spurious positive* itself as a +0.0058 fluctuation on an 8-file subset that vanishes at n=50k -- i.e. the
original number was small-sample noise on the gestalt space, without the shuffled-diagnosticity twin or significance
the DO-NOT-QUOTE list demanded. On modern WiC, separation is neutral (LCSS) to negative (whitening), consistent with
the on-disk `exp_curated_foundation_wic_whiten_v1` neutral result AND with the fact that on WiC DIAG~=FLAT (the
coarse identity task has no within-word fine-selection headroom for separation to touch). **Both instruments agree:
separation is task-inappropriate.**

## 6. UPSTREAM + DOWNSTREAM (the owner's directive, discharged)

- **Upstream component (the hub) prototyped three ways, all brain-faithful, all refuted as optimizations** ->
  the correct action is to CHANGE NOTHING about the hub. Its graded-overlap geometry IS the brain-foundational one.
- **Downstream consumers of the hub, enumerated on disk:** the ONLY read-time consumer of `hdlab.meaning_foundation`
  is the `diagnostic_context_wsd` readout (it takes signatures as input); `consolidation_gate` only references it in
  a docstring; `grounded_semantic_graph.select_sense` is a SEPARATE associative PPR reader that does not touch the
  dense hub. Because I propose NO hub change, **there is zero regression surface.**
- **Should the other consumer be revisited to be more brain-foundational?** Yes -- but not via separation. The live
  reader's `select_sense` (PPR spreading activation) is the weaker path; the board already shows the curated hub +
  diagnostic readout beats it +0.0633 CI-sep on WiC. The pending WIN is the WIRE (route read-time `select_sense`
  through the diagnostic readout over the curated hub), and it needs NO decorrelation. That is a meaning-channel
  integration item (Q111), not this problem.

## 7. PROPOSED hdlab CHANGE (strategy lands it, Q111 -- I did NOT write hdlab/)

1. **Do NOT decorrelate / whiten `hdlab.meaning_foundation`** (nor add a whitening step to `diagnostic_context_wsd`):
   provably argmax-neutral for the common mode, CI-separated NEGATIVE for whitening, on modern gold, and
   brain-unfaithful. Remove "decorrelate the sense hub" from the meaning-channel lever list.
2. **Do NOT add a construction-integration context de-blur or a sparse-IDF sense-signature swap** to the selection
   path: both score below the incumbent (the gloss/IDF supply is impoverished vs the dense w2v context for selection).
3. **The forward action is the WIRE, unchanged:** route the read-time meaning stage through `diagnostic_context_wsd`
   over the curated `meaning_foundation` hub WITH its landed precision (`gamma`/`topk`) + Bayesian log-prior
   (`sense_prior`/`prior_weight`) + `semantic_control` conflict-gated suppression (the landed subordinate-case lift
   +0.007..0.033). Keep `conceptual_meaning`'s IDF distinctive-feature channel for meaning-IDENTITY (its validated
   job), demand-ROUTED (not fused) with the associative channel.

## 8. KEY REALIZATIONS (the enabling moves)

- **The one-line control that ended the separation debate: subtract the per-word centroid WITHOUT renormalizing.**
  It produces 0 pick-changes, which PROVES the cosine-argmax readout is already invariant to the collinear common
  mode -- so "decorrelate the hub" cannot help by removing collinearity; only a reweighting could, and every
  reweighting hurt. This turned a fuzzy "does whitening help?" into a theorem plus a measurement.
- **Recomputing the premise on the REAL asset localized it:** 0.923 is a WITHIN-WORD number (a word's own senses),
  not a global one -- and the research says that within-word overlap is the brain's polysemy structure, not a defect.
- **Reproducing the prior-art positive as small-sample noise:** the +0.0176 whitening "lift" reappears as +0.0058 on
  8 files and inverts to CI-sep NEGATIVE at n=50k. The DO-NOT-QUOTE flag was right; the number was an artifact.
- **The research REVERSED the brief.** Four lit drills converged: the ATL distills (doesn't decorrelate); CSC reshapes
  at readout over a context-INDEPENDENT hub; the N400/SG model is feature-agnostic and overlap-based; decorrelation is
  a hippocampal (episodic), not semantic-hub, operation. Being forced to check "is the UPSTREAM component actually
  brain-foundational?" is what revealed the hub was already right.
- **"Reads real structure but loses to the incumbent" is the fingerprint of a representational ceiling** -- every
  refuted lever beats its own info-free twin, so the failure is not machinery; it is the sense-conflated context input.

## 9. AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, meaning channel / section 2b)

- **Sense-hub decorrelation is NOT a meaning-channel lever -- remove it.** It is (a) provably argmax-neutral for the
  cosine-argmax readout (common-mode removal = 0 pick-changes at n=50,386 and n=7466), (b) CI-separated NEGATIVE when
  it reweights (global whitening) on modern WiC AND SemCor a_s, and (c) brain-unfaithful: the ATL DISTILLS/converges
  (Patterson-Nestor-Rogers 2007); decorrelation is a HIPPOCAMPAL operation (CLS 1995); polysemy's shared-core overlap
  is the correct geometry (Rodd 2002), so separation misrepresents it. The unverified +0.0176 a_s whitening figure is
  RETRACTED (small-sample noise; CI-sep negative at full n).
- **The context-appropriate reshaping is a READOUT-time, context-independent-hub operation (CSC 2017).** The landed
  `diagnostic_context_wsd` diagnosticity already implements the transient reshaping; the hub is correctly
  context-independent. Do NOT move the reshaping into the stored representation.
- **The fine-sense ceiling (a_s ~0.27-0.33; WiC ~0.62) is confirmed CONTEXT-INPUT-ENCODING x COVERAGE bound.** The
  brain's glass-box selection mechanisms (biased competition, reordered access, semantic control, precision-weighting)
  are landed/brain-complete; neither separation, nor construction-integration context de-blur, nor distinctive-feature
  resupply crosses it. HOLD on the no-external-encoder invariant is EMPIRICALLY CONFIRMED.

## 10b. HOW THE BRAIN ACTUALLY DOES IT WITHOUT A TRAINED ENCODER (owner question -- and a correction to my framing)

**My "the ceiling requires a trained encoder, which is barred" was TOO STRONG.** The brain resolves word sense
WITHOUT a black-box encoder -- so the true wall is not the invariant. The brain's mechanism is a glass-box,
STRUCTURED, PREDICTIVE, INCREMENTAL comprehension process, not a scan of co-occurring words (which is all our
readout does):
1. **Incremental structure, not a bag (Kintsch 1988 construction-integration).** It parses and builds a running
   situation model (entities/events/roles); the disambiguating "context" is that STRUCTURE, not word co-occurrence.
2. **The thematic frame is a hard constraint (selectional preference).** The sense is pinned by the word's ARGUMENT
   SLOT + GOVERNING PREDICATE: "deposit [money] at the bank" (verb+theme -> financial) vs "sat on the grassy bank"
   (locative predicate + modifier -> land). A bag discards which word governs the target and in what role.
3. **Top-down prediction (Federmeier & Kutas 1999; predictive coding).** The situation model PRE-ACTIVATES the
   fitting sense before/as the word arrives; reordered access + semantic control (both LANDED) then let the predicted
   subordinate sense beat the frequency-dominant one.
4. **Coarser granularity than WordNet (Rodd 2002).** The brain holds polysemy as a graded shared core and does not
   hair-split. MEASURED (`exp_sense_selection_granularity_probe_v1`, n=50,386): the SAME incumbent picks score
   a_s 0.2697 at FINE (exact synset) but **0.5412 at the brain's shared-core granularity (supersense)** -- 37% of
   the "errors" are fine near-misses INSIDE the correct coarse sense. The brain "solves" a third of the ceiling by
   simply not making the distinction we force.

**So the corrected conclusion:** crossing the fine-sense ceiling needs CONTEXTUALIZED word meaning, which the brain
produces by glass-box structured/predictive comprehension over slowly-offline-learned representations -- NOT a
transformer. My located negatives all live INSIDE the bag-of-context paradigm (decorrelate the hub, resupply the
signatures, de-blur context words); they correctly fail because none of them add the missing STRUCTURE. The forward
lever is meaning-selection as a downstream READ of the TOP-DOWN situation model + the parsed thematic frame, at
shared-core granularity -- which is the project's Phase-1 comprehension program, NOT a hub/readout fix. The
no-external-LLM-at-inference invariant stays correct; but "the ceiling is unreachable without a barred encoder" is
withdrawn.

## 10c. I BUILT THE BRAIN'S STRUCTURAL MECHANISM (thematic-fit selectional preference) AND DRILLED IT -- it is REAL but topical-context-DOMINATED, exactly as the literature predicts

Per the owner's directive to build the brain's actual mechanism and drill every wall, I built a THEMATIC-FRAME sense
selector (`exp_sense_selection_thematic_frame_as_v1`): parse the sentence (spaCy, a glass-box syntactic frame -- NOT
an LLM), find the target NOUN's governing predicate + syntactic role, build ERK-DISTRIBUTIONAL selectional-preference
profiles (count-weighted typical-filler centroid per (verb, role), doc-held-out, GOLD-BLIND), and select the sense
whose `meaning_foundation` signature best fits the (verb, role) profile. Research-grounded by a dedicated drill
(McRae-Spivey-Knowlton-Tanenhaus 1998; Ferretti-McRae-Hatherell 2001; Resnik 1996; Erk 2007 / Erk-Pado-Pado 2010;
Baroni-Lenci 2010; Lenci 2011; Metusalem 2012; Palmer-Dang-Fellbaum 2007; Lee & Ng 2002).

**RESULT (SemCor subordinate NOUN, doc-held-out, n=4,892):** thematic-fit reads REAL structure -- it beats BOTH
info-free twins CI-separated (role-permutation +0.065, verb-shuffle +0.020) -- but it is DOMINATED by topical
context: FIT a_s 0.234 fine / 0.439 coarse vs the incumbent BAG 0.346 / 0.520. A dev-selected brain-faithful
multi-cue integrator (McRae 1998 constraint integration, weight chosen on train) assigns thematic-fit weight
**w\*=0.00** -- given the choice it IGNORES the structural cue, because the topical bag already subsumes its coarse
signal. Complementarity is tiny (fit on the bag's WRONG items 0.189 vs chance 0.168). No bucket reverses it: not the
coarse-separable bucket, not the strongly-selecting-verb bucket (Resnik's cherry-pick), not their intersection.

**This is not a build failure -- it is the information-theoretic ceiling the field agrees on.** Lee & Ng (2002)'s
controlled ablation lost 0.6pp removing syntactic/selectional features from a strong SENSEVAL-2 classifier -- a
near-exact match to this project's own +0.007 and to my w\*=0.00. McCarthy & Carroll (2003): selectional preference
is BEATEN by MFS on fine senses and fails to beat random on the non-dominant subset. Navigli (2009): "selectional
restrictions have not been found to perform as well as Lesk-based methods or MFS." Fine polysemy shares a coarse
selectional class by construction, and selectional preference is a coarse-class-level signal -- it cannot see below
a class it cannot see. **The brain's structural cue is REAL, coarse-only, and here it is redundant with topical
context. The residual routes to richer CONTEXTUAL representation (Phase-1 structured comprehension), not more
structure** -- the research's own bottom line, now empirically confirmed on this substrate.

## 10. WHAT I DID NOT ESTABLISH (withdraw first if wrong)

- **All numbers are on SemCor (subordinate a_s, mid-20c, informational) and WiC (modern, the headline).** I did not
  acquire a modern fine-grained all-words WSD set (Raganato/SemEval-2015); the *readout-invariance proof* is
  instrument-independent, but a modern fine-WSD confirmation of the empirical negatives is an optional add (Next Steps).
- **I did not test a homonymy-only separation.** Rodd predicts separation is appropriate for *homonyms* (genuinely
  unrelated meanings); WordNet fine senses are mostly polysemy, so the aggregate negative is expected, but a
  homonym-routed separation could help on that small subset (named as an adjacent probe, not claimed here).
- **The discourse lever was tested in its WITHIN-CONTEXT construction-integration form**, the evidence-backed one
  (Kintsch 1988; the multi-sentence "one sense per discourse" claim is weak at fine senses -- Krovetz 1998 -- and
  contested -- Binder 2003). I did not build a full structured situation-model prior; the prior topical-discourse
  negative plus this CI negative make that low-expected-value, but it is not exhaustively closed.
- **The incumbent I beat-tested against is the diagnostic readout with default settings.** Its landed
  precision/Bayesian-prior/semantic-control settings only RAISE the floor, so they strengthen the negative, not weaken it.

## TLDR

Words have several meanings; ours are stored as fixed "meaning fingerprints." The brief's idea was that the
fingerprints for one word look too alike (they do -- 92% similar), so we should pull them apart and then let context
pick the right one. I tested that idea the brain's way and it does not work -- and I found out exactly why, three
different ways. First, a short proof: the way we score meanings already ignores the part that all a word's senses
share, so "pulling them apart" changes literally nothing (I confirmed it changes 0 of 50,000 decisions). Second,
when a separation method DOES change decisions, it makes them WORSE on both modern and older test sets. Third, the
brain research says the brief had it backwards: the brain does NOT pull related meanings apart -- keeping them
overlapping is exactly what lets it read fast; the "pull apart" machinery lives in a different brain system
(memory), not the meaning hub. I also tried two deeper brain-faithful fixes (rebuild the context out of resolved
meanings; rebuild the fingerprints to emphasize distinctive words) and both were worse too -- though all of them
clearly used real information (they beat scrambled versions of themselves), they just can't beat what we already
have. The bottom line: the meaning hub is already built the right (brain) way; the real limit is that each context
word is stored as one blurry vector, and the only thing that fixes THAT is a trained language model -- which we have
deliberately banned. So the honest, decision-settling answer is: keep the ban; the wall here is the representation,
not the method, and the upstream component was right all along.

## QUESTIONS

None blocking. One judgement call: I filed **REFUTED** because the brief's specific mechanism (decorrelate the hub +
discourse-primed selection crosses the ceiling) is refuted with the exact cause named and measured -- which the bar
defines as a FULL PASS that settles the no-encoder-invariant decision. If you would prefer this labelled PARTIAL to
signal the constructive half (the hub needs no change; wire the existing stack), say so and I will relabel.

## NEXT STEPS

1. **Land nothing on the hub.** Keep `meaning_foundation` as-is; do NOT add whitening/decorrelation to
   `diagnostic_context_wsd`. Update `BRAIN_FOUNDATIONAL_AUDIT.md` per section 9.
2. **Proceed with the meaning WIRE (Q111), unchanged by this result:** route read-time `select_sense` through the
   curated hub + diagnostic readout + landed precision/Bayesian-prior/semantic-control. This is the standing positive;
   it needs no separation.
3. **Optional modern-fine-WSD confirmation:** acquire Raganato/SemEval-2015 (pre-authorized, `data/corpora/`) and
   re-run the incumbent-vs-separation contrast for a third, modern, fine-grained instrument. The readout-invariance
   proof already generalizes; this is belt-and-suspenders.
4. **Adjacent probe (small, Rodd-grounded):** a homonym-ONLY separation (route by WordNet unrelatedness) -- separation
   is predicted appropriate for genuine homonyms; likely a small subset, but the one place decorrelation could earn
   its keep.
5. **The real forward lever is richer CONTEXTUAL representation built the brain's way -- glass-box structured
   PREDICTIVE comprehension, NOT a trained encoder (corrected).** The brain resolves sense by (i) the parsed
   thematic frame [built + drilled here: real but topical-context-dominated, coarse-only]; (ii) top-down PREDICTION
   from an incremental situation model (Kintsch 1988; Metusalem 2012 -- event knowledge pre-activates the fitting
   sense, and the effect COLLAPSES when the discourse is removed, its own falsification control); (iii) at COARSE
   shared-core granularity. Concretely mapped as Phase-1 comprehension components, each with the research's
   falsification recipe: (a) **score/measure sense at SHARED-CORE granularity** -- immediately recovers 0.27->0.54
   here, the cheapest brain-faithful gain; (b) **multiplicative (bind, not bundle) joint-role conditioning** (Lenci
   2011 ECU: PRODUCT 84% > SUM ~chance on Bicknell 2010) -- a clean bind-vs-bundle test on this substrate; (c) an
   **additive discourse-event prior** from the tracked situation model (Metusalem), which must collapse to ~0 in
   isolation or it is leaking local information. These are the top-down comprehension program, NOT a hub/readout fix.
   The no-external-LLM-at-inference invariant HOLDS -- for the right reason (the brain uses none either), not because
   the ceiling needs one.
