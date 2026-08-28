---
problem: no_glass_box_verb_sense_disambiguation
status: PARTIAL
bar: "PASSES only with ALL of: 1. A glass-box sense/frame disambiguator over the dependency parse for AT LEAST the two dominant confusions (motion-vs-transitive-deposit; perception-vs-speech). 2. Beats a most-frequent-sense floor CI-separated on a real WSD gold (recompute the floor on the same population); an info-free twin LOSES CI-separated; report CI half-width + null p95; a positive control the metric can move (a context-flipped minimal pair the disambiguator gets and MFS cannot). 3. Lifts a downstream front-end CI-separated vs the un-disambiguated path. 4. One-screen summary. A rigorous NEGATIVE is a full pass (the downstream lift alone passes)."
result: "BUILT the glass-box event-frame disambiguator (bar 1, met; witness 9/9, minimal-pair positive control 6/6 on the two confusions MFS cannot flip). Bar 2 NOT met: on every real WSD gold it TIES or LOSES to most-frequent-sense -- SemCor coarse event-frame DISAMBIG 0.810 [0.799,0.821] vs MFS 0.811 [0.800,0.822] (n=4544 all-poly) and 0.664 vs 0.667 (n=2159 frame-alt), McNemar n.s.; binary motion confusion DISAMBIG 0.639 vs per-lemma MFS 0.707 (n=191); binary perception/speech 0.802 vs MFS 0.846 (n=162, curated). Bar 3 PARTIAL: gating the ToM ledger's motion decision beats the UN-DISAMBIGUATED ledger (McNemar p=0.039, 10 false departures fixed vs 2 broken, n=191) but the bootstrap CIs overlap and it does not beat the stronger per-lemma MFS."
floor: "STRONGEST floor = per-lemma most-frequent-sense, recomputed per population: coarse-frame 0.811 [0.800,0.822]; binary motion 0.707 [0.644,0.770]; binary perception/speech 0.846 [0.784,0.895]. The un-disambiguated FRONT-END floor (ledger fires motion on every deixis verb string) = 0.586 [0.518,0.654]. DISAMBIG beats the front-end floor (paired-significant) but not the MFS floor."
controls: "INFO-FREE TWIN (shuffled construction->frame map, same conservative gate): ties MFS on coarse-frame (0.810) and on the auto binary pops even BEATS DISAMBIG (0.766 vs 0.707) -> the construction signal is near-worthless vs MFS at aggregate. JOINT-vs-TYPED ablation (co-select noun sense vs type-first): no material difference (0.810 vs 0.811) -> the joint move is not the bottleneck. CONSERVATIVE-DEFER control: bare 'He left.' -> predicts MFS (no over-commitment). CCOMP-complementizer control: 'made him go' (causative) is NOT read as a propositional complement. Positive control: 6/6 context-flipped minimal pairs the MFS floor cannot flip."
files_changed: "experiments/frame_sense_disambiguator.py; experiments/exp_frame_sense_semcor_v1.py; experiments/exp_frame_sense_wic_v1.py; experiments/exp_frame_sense_serves_motion_cue_v1.py; experiments/exp_frame_sense_confusion_pairs_v1.py; verification/test_frame_sense_disambiguator.py; notes/problems/no_glass_box_verb_sense_disambiguation/{BRAIN_MECHANISM_SPEC.md,SOLVED.md,research_brain_foundational_verb_sense_2026-08-28.md}. NO hdlab/ writes (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_frame_sense_disambiguator.py  (-> 9/9; then experiments/exp_frame_sense_semcor_v1.py --mode full -> DISAMBIG ties MFS; experiments/exp_frame_sense_confusion_pairs_v1.py --mode full -> DISAMBIG loses to per-lemma MFS on all four binary pops)"
---

# PARTIAL: a brain-faithful construction disambiguator that helps the front-end but cannot beat most-frequent-sense

## What I built (bar 1, met)

`experiments/frame_sense_disambiguator.py` -- a glass-box verb-sense / **event-FRAME** disambiguator over the
spaCy dependency parse (no LLM at inference), copying the brain's PINNED computation (verified by the 2026-08-28
research drill against MacDonald/Pearlmutter/Seidenberg 1994; McRae/Spivey-Knowlton/Tanenhaus 1998; McClelland
2013): a frequency **prior** (reordered access; Duffy/Morris/Rayner 1988) + a near-categorical argument-structure
**CONSTRUCTION** cue (Goldberg; Levin 1993) + graded **thematic fit**, combined through the substrate's own
`hdlab.graded_competition` (additive activation -> softmax). It resolves the two dominant confusions on
context-flipped minimal pairs (6/6; witness 9/9): "left the ROOM" (motion) vs "left the KEYS" (deposit);
"observed the SWAP" (perception) vs "observed THAT S" (speech). It implements the research's recommendations:
JOINT (verb,noun)-sense co-selection, a homonym/polysemy grain gate, the three missing construction rules
(light-verb, double-object dative, resultative-AP), the "that"-complementizer test (a causative "make him go" is
NOT a propositional complement), and -- brain-faithfully -- a CONSERVATIVE underspecification default (commit off
the prior only when a STRONG construction fires; Frazier & Rayner 1990; Fishbein & Harris 2014).

## What I measured (bars 2 and 3)

Across **five** real evaluations the construction cue **ties or loses to most-frequent-sense (MFS)**:
- **SemCor coarse event-frame** (n=4544 all-poly, 2159 frame-alt; human sense tags): DISAMBIG **ties** MFS
  (0.810 vs 0.811; 0.664 vs 0.667; McNemar n.s.). It DEFERS -- it does not hurt.
- **WiC same-sense** (human-judged, balanced ~0.5 floor, verb subset): DISAMBIG ties the majority-class floor;
  frame-equality predicts human same-sense at only 0.68 precision vs a 0.61 base rate.
- **Binary motion confusion** (n=191 SemCor deixis verbs): DISAMBIG 0.639 < per-lemma MFS 0.707.
- **Binary perception/speech confusion** (n=162 curated exemplars): DISAMBIG 0.802 < per-lemma MFS 0.846.
- **Downstream ToM motion cue** (bar 3): gating the ledger's motion decision beats the **un-disambiguated ledger**
  (McNemar p=0.039; fixes 10 false departures like "left a note", breaks 2) -- but the bootstrap CIs overlap and
  it never beats the stronger per-lemma MFS.

The **info-free twin** ties MFS everywhere and on the auto populations even BEATS DISAMBIG -- direct evidence the
construction signal carries almost nothing over MFS in aggregate.

## Why -- the finding (this is the deliverable)

**Two orthogonal reasons the standard WSD golds cannot show the mechanism, and one reason the mechanism is
capped -- all brain-grounded:**

1. **TAXONOMY MISMATCH (SemCor).** WordNet's lexname is a lexicographer's *semantic-field* taxonomy that FIGHTS
   the event-frame taxonomy: "leave behind" (deposit) is tagged `verb.cognition`, "time passed" (elapse) is
   `verb.motion`, "put" is `verb.contact`. So a construction/event-frame disambiguator cannot beat a lexname MFS
   -- and the diagnostic subpopulation (where the cue is confident) is where it is MOST "wrong" vs lexname,
   because that is exactly where event-frame != lexname. **This is why the prior `entity_typing` selectional
   SemCor test nulled (+0.001).**
2. **GRAIN MISMATCH (WiC).** WiC's sense distinctions are finer than / orthogonal to the coarse event-frame, so
   frame-equality is a noisy same-sense predictor.
3. **MFS IS THE WALL + the residual is WORLD KNOWLEDGE (fundamental).** Verb-sense in real text is dominated by
   a heavily skewed frequency prior; per-lemma MFS is 0.71-0.91 and captures most of the signal. The
   construction cue is genuinely **low-coverage** (a diagnostic construction is present in a minority of
   instances) and the dominant non-literal uses -- "pass a law", "come to a decision", "go bad", "make sense" --
   are **idiomatic/abstract**, where the construction is absent or actively MISLEADING (an idiomatic "come to X"
   mimics a motion Goal-PP). The research flagged these as the permanent world-knowledge / idiom ceiling. The
   brain crosses it with full lexical-semantic + world + discourse knowledge; a glass-box construction cue over
   the parse structurally cannot, and the no-LLM-at-inference invariant precludes sourcing that knowledge.

**The reframe:** a front-end verb-sense disambiguator should be evaluated on the DOWNSTREAM TASK, not a WSD
benchmark -- because the benchmarks' sense grain is not the event-frame grain the front-ends consume. On the
downstream (bar 3) the mechanism DOES help (it removes real false departures), just not enough to clear MFS.

## What I did NOT establish / would withdraw first

- I did **not** beat MFS CI-separated on any WSD gold (bar 2 is a NEGATIVE). Withdraw first if wrong: the claim
  that the SemCor result is a *taxonomy* mismatch rather than a mechanism failure -- it is supported by the
  minimal-pair control (the mechanism gives the correct EVENT frame) + the diagnostic-subpop-is-most-wrong
  signature, but a construction-labeled real gold (not built) would settle it.
- The bar-3 lift is **paired-significant but not bootstrap-CI-separated** on n=191; I did not build a
  literary-domain hand-verified gold (where clean "left a note"/"returned a reply" may separate it, though the
  motion-skew of narrative may also shrink the headroom). I refuse to over-state it as a clean lift.

## KEY REALIZATIONS (the enabling moves)

1. **The gold's taxonomy was fighting the mechanism.** The decisive move was reading WordNet's lexnames for the
   target verbs and seeing "leave behind"=cognition, "elapse"=motion -- proving SemCor-lexname is the wrong
   instrument for an event-frame disambiguator, and explaining a prior landed null.
2. **A general construction cue applied to every verb HURTS** (measured: -0.03 on SemCor); the fix was
   VERB-SENSITIVITY -- fire the cue only for the confusion a verb actually participates in -- plus a CONSERVATIVE
   underspecification default. That turned "actively worse than MFS" into "ties MFS (defers)".
3. **The info-free twin tying/beating the real cue is the honest verdict**, not a bug: it says the construction
   carries almost nothing over MFS in aggregate, because MFS already captures the dominant-sense skew.
4. **A pronoun object is the coreference seam** -- typing "it/him/them" guesses a referent; not typing it
   (deferring) removed a measured real-prose error class ("observed it" -> perception, not communication).
5. **MFS is not a floor to be embarrassed by -- it is the finding.** The brain's advantage over MFS here is
   world knowledge, which the invariant precludes; naming that precisely is worth more than a fragile win.

## AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md)

The **verb-polysemy** wall (named in the ToM entry / audit) now has a measured verdict: a glass-box
argument-structure **construction** cue is brain-faithful and correct on diagnostic constructions but **does not
beat most-frequent-sense** on real WSD, because (a) WordNet-lexname and WiC sense grains are not the event-frame
grain, and (b) the residual is world knowledge precluded by the no-LLM invariant. New PINNED/INVENTED note: the
reordered-access + construction + thematic-fit + graded-competition model is the mainstream account (PINNED,
research-verified); the additive->softmax combination is "structurally isomorphic to, not proven equal to" a
Bayesian posterior (McClelland 2013 needs calibrated log-likelihoods + conditional independence, which our
construction/fit cues violate). Recommendation: do NOT wire this as a WSD organ; its only measured value is as a
CONSERVATIVE front-end gate that removes false departures/false-speech reads (paired-significant, not
CI-separated).

## Proposed hdlab change (strategy lands; I did not write hdlab/)

Do NOT promote a WSD organ. IF a front-end gate is wanted: expose
`experiments/frame_sense_disambiguator.py:strong_construction` + `disambiguate_token(conservative=True)` as an
optional, default-OFF gate that `perceptual_access_ledger._motion_signal` consults to SUPPRESS a departure read
when the realized frame is clearly non-motion ("left a note", "returned a reply"). It is precision-oriented and
paired-significant over the current always-fire behaviour; it is NOT a capability win and must be measured on the
live reader before any claim. Keep the no-LLM invariant.

## Adjacent bottlenecks (mapped follow-ons, not silent gaps)

- **Coreference (~0.65)** -- typing pronoun/anaphoric objects needs it; it also resolves the ambiguous
  caused-motion "to X" head. The dominant real-narrative cap; owned by the coref brief.
- **A world-knowledge / idiom source under the invariant** -- the true ceiling here ("pass a law", "go bad").
  Open problem: is there a glass-box, offline-built idiom/collocation asset (a static FOUNDATION) that flags
  non-compositional uses without an LLM at inference?
- **A construction-labeled real gold** (event-frame, not lexname) + a **literary-domain downstream gold** --
  would let bar 2/3 be scored on the mechanism's own taxonomy and its own domain.

## TLDR / QUESTIONS / NEXT STEPS

**TLDR (plain language):** The same word means different things -- "she left the room" (walked out) vs "she left
a note" (put it down). I built a glass-box reader that tells these apart from sentence grammar the way the brain
does, and it is right on clean textbook examples. But on real text it cannot beat the dumb rule "always guess the
word's most common meaning" -- because that common-meaning rule is already right most of the time, the grammar
clue is only present in a minority of sentences, and the hard cases ("pass a law", "go bad") need real-world
knowledge the brain has and our no-outside-AI rule forbids us from using. It DOES measurably fix a real bug in
the mind-reading module (it stops "she left a note" being misread as "she left the room" -- 10 such errors fixed,
2 introduced), but the improvement is small and not statistically clean. So: a faithful mechanism, a real but
small front-end fix, and a clear finding about why the standard tests can't score it.

**QUESTIONS:** none blocking. One judgement call for the owner: whether to invest in a hand-built world-knowledge
/ idiom asset (the true ceiling) or accept the front-end gate as-is.

**NEXT STEPS:** (1) land the optional default-off front-end gate (strategy, if wanted) and measure it on the live
reader; (2) build a construction-labeled + literary-domain gold to score the mechanism on its own taxonomy/domain;
(3) route pronoun/anaphoric objects to coreference; (4) open the "glass-box idiom/world-knowledge foundation"
question -- that, not a better construction cue, is what would let us beat MFS.
