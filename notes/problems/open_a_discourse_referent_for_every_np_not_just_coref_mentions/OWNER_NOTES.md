---
owner_verdict: DONE
---

SUBMISSION — open_a_discourse_referent_for_every_np_not_just_coref_mentions

STATUS: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO LLM at inference. NO hdlab/ written (Q111 — proposed
wire only; proved via a runtime monkeypatch of the live reader's mention source). Reverify:
  .venv/Scripts/python.exe verification/test_referent_per_np_organ.py        # 10/10, all from source

CORE (bar met, witnessed). Open a discourse referent for EVERY content-noun-head NP (Kamp/Heim DRT) and demote
coreference to a downstream LINKING pass. Measured through the actual live SituationReader().read() (only the mention
SOURCE swapped), scorer pick==gold, abstention=wrong, 25 real LitBank docs:
  - honest cleaned-DO instrument (n=149): coref-column deployment floor 0.4698 -> referent-per-NP 0.8054,
    +0.3356 CI[+0.262,+0.416], over null. FULL noisy population (n=1354): +0.0473 CI[+0.023,+0.070].
  - info-free twin (matched-count random-position referents) LOSES (+0.47/+0.12 CI-sep) AND actively HURTS vs coref
    (-0.13/-0.07): the RIGHT complete NP set helps, RANDOM candidates steal picks.
  - NO regression: referent-per-NP reproduces the noun-supplied eval accuracy exactly (rnp==supplied, delta ~0).
  - DESIGN: referent-per-NP as the SOLE source (0.805) beats the additive union (0.403) — REPLACE, don't ADD (DRT order).
  - WHO-HAS-WHAT: OBJECT/theme candidate coverage +0.1151 (the inanimate "what" coref's entity-typing misses).
  - GENERALIZATION: introduction is register-INVARIANT (0.983 modern / 0.978 19c) where the coref linker is OOD on 19c
    (0.818) — register-sensitivity lives in the linker, exactly as DRT predicts.

MEASURED BRAIN COMPARISON (spaCy = competent-reader REFERENCE-ONLY; per-stage signal-loss waterfall, product=end).
  chain: ORACLE 1.000 -> S1 SOURCE -> S2 EVENT(verb-ID) -> S3 SELECTION -> END.
  coref (deployed): S1 0.839 -> S2 0.968 -> S3 0.545 => 0.443   (loses at BOTH source -0.16 AND selection -0.37)
  rnp   (this fix): S1 0.987 -> S2 0.966 -> S3 0.845 => 0.805   (source nearly closed; a COMPLETE set also REPAIRS
                                                                 selection — coref gaps had corrupted the pick)
  performance vs a brain: rnp 0.805 = 95% of the competent reader (0.846); the IDEAL composition (referent-per-NP +
  the parent's validated structural-DO/Competition-Model selector) reaches 0.873 (>= competent); shuffled-CANDIDATE
  twin collapses to 0.235 (+0.638 CI-sep).

PROTOTYPED SELECTION IMPROVEMENT (S3, the biggest remaining loss). Diagnosed the residual: 84% of errors are multi-DO
competition. A Goldberg construction-aware selector (double-object -> recipient; naming/object-complement -> complement)
lifts 0.873 -> 0.913 (+0.040 CI[+0.013,+0.074] CI-sep; +0.146 CI-sep on the multi-DO subset), info-free twin loses.
KEY FINDING: a distributional selectional-preference re-rank adds only +0.007 n.s. OVER the constructions (beats its
own shuffled twin +0.067 CI-sep) — so on canonical multi-DO the "fit" the brain uses is CONSTRUCTIONAL, not lexical
co-occurrence, reconciling the fit-dominant literature with the parent's fenced grounded-fit negative.

WHERE WE LOSE SIGNAL -> FURTHER IMPROVEMENT (ranked by the measured loss; READY vs GATED):
  0. LAND THE SOURCE WIRE (this bar): referent_per_np replaces the coref-column source in read(); ship the
     determiner/name FRAME detector on the holder/name path (not as extra patient candidates). +0.336 CI-sep. READY.
  1. LAND THE SELECTOR: the parent's ideal_pick + the PROTOTYPED construction-aware improvement (0.805->0.913). READY.
  2. MEANING-FIT selector for genuine ambiguity (the residual to oracle). GATED on the meaning channel (filed).
  3. REGISTER-NATIVE POS/NER: close the 19c introduction cap (POS noun recall 0.914; frame recovers ~20% ->0.931). FILED.
  4. NOISY-CHANNEL joint POS override for free-text verb-ID (S2). AVAILABLE (parent).

HONEST BOUNDS: no hdlab landed (mechanism proved via monkeypatch; strategy lands Q111). FULL absolute numbers are on a
known-noisy gold (~76% oblique-contaminated) — I lead with cleaned-DO. Modern SOURCE end-to-end delta is INFERRED (no
modern gold-coref corpus on disk); the direct evidence is register-invariant introduction coverage + the parent's
modern selection recovery. The discrete referent structure is a defensible OUR-INVENTION (no dedicated neural
file-opener is attested); the DRT introduction operation itself is PINNED.

FILES. experiments/: exp_referent_per_np_{end_to_end, holder_and_generalization, frame_detection, signal_loss_waterfall,
ideal_composition, selection_improvement}_v1.py. verification/: test_referent_per_np_organ.py (10/10). notes/problems/
<slug>/: SOLVED.md + research_discourse_referents + IDEAL_who_did_what_composition + selection_improvement_construction_aware.
REUSED read-only: exp_whodidwhat_referent_per_np_prototype_v1, exp_whodidwhat_ideal_brain_foundational_v1,
hdlab/situation_reader.py, hdlab/coref.py.
