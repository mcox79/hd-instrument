---
owner_verdict: DONE
---

SUBMISSION — precision_weight_the_head_driven_readers_on_calibrated_parse_confidence
status: SOLVED (WIP until owner_verdict: DONE)

WHAT THE BRIEF ASKED: the parser emits a per-arc confidence that ZERO live consumers read; wire
a calibrated version into the head-driven readers (who-did-what / obl / space) so each TRUSTS its
confident arcs and DEFERS on shaky ones — delivering comprehension RELIABILITY, not higher UAS.

RESULT — POSITIVE, CI-separated, twin-controlled, on TWO modern golds, THREE live readers:
  • who-did-what PATIENT (deployed structural_patient_pick, off the substrate's own arc-eager parse):
    selective@50 0.8789→0.9745 (+0.0956 CI[+0.078,+0.114]) UD-EWT n=1255; 0.2982→0.3414 (+0.0432
    CI[+0.033,+0.053]) QA-SRL n=8225. Random twin FLAT.
  • obl/spatial ATTACHMENT (which predicate an oblique attaches to = who-is-where):
    0.7581→0.8919 (+0.1338 CI[+0.117,+0.151]) UD-EWT obl/nmod n=2294. Twin FLAT.
  • who-did-what AGENT (read by the Competition-Model competition, so weighted by its MARGIN not a
    parse arc): 0.7367→0.8864 (+0.1497 CI[+0.129,+0.174]) UD-EWT; 0.4346→0.5559 (+0.1213) QA-SRL. Twin FLAT.
  All clear null-p95 by 5–13×. Additive (parse heads unchanged) → no non-consumer regresses.

UPSTREAM COMPONENT (fully prototyped, proven to EXCEL): the RAW emitted arc conf is near-useless
(AUC 0.615 UD / 0.500 QA — confirms the settled "confidence-weighting is weak" negative). The
CALIBRATED confidence (glass-box logistic = graded_competition.net_activation + softmax = the pinned
McClelland-2013 posterior, learned Bates-MacWhinney cue validities) is AUC 0.858; the parse-only
version (no reader-branch feature) is 0.777 and still lifts +0.0765 CI-sep → the parser's own graded
confidence is load-bearing. ANSWER to the brief's open Q: ONE reliability signal PER READER, keyed to
how it reads its role (parse-arc conf for patient/obl; competition margin for agent) — not one universal.

BRAIN-FOUNDATIONAL (research-verified, honestly labeled): precision-weighting + graded confidence are
PINNED as decision-level computations (Ernst&Banks 2002; Kepecs 2008; Kiani&Shadlen 2009; Friston 2010)
and distribution-over-parses is PINNED (Hale/Levy/Jurafsky). Applying confidence to gate the THEMATIC-ROLE
readout is OUR-INVENTION-UNDER-TEST (a-priori P~0.30, tested nowhere) — empirically UPHELD here, twins flat.
Strict CALIBRATION is NOT a brain property (hard-easy effect) → we measure SENSITIVITY (AUC/risk-coverage),
the brain-robust quantity. Brain/SOTA anchor: AUC 0.84 sits INSIDE biological decision-confidence (0.7–0.9)
and at/above trained selective-prediction SOTA (0.80–0.85) — glass-box, no trained encoder.

DEEPENING (signal-loss ladder, oracle ceiling, recapture, fidelity map):
  • Where signal is lost: parser's raw conf captures 23% of the oracle sensitivity, entropy adds ~10pts,
    cue-validity integration reaches 68%; ~32% (UD)/~76% (QA) is unreachable by any glass-box cue.
  • RECAPTURE PROTOTYPE (located negative): a richer greedy-parser posterior (+0.2pt, redundant) and a
    static animacy proto-role cue (near-chance) do NOT recapture the losses → they are STRUCTURAL.
  • EXACTLY where we differ from the brain (cited): LOSS 1 = greedy max-margin scalar vs the brain's
    competition-among-co-active-alternatives (Hale 2006; Lewis&Vasishth 2005) → requires a small-beam
    graded parser (P=0.65). LOSS 2 = static binary animacy vs graded verb-specific thematic FIT (McRae
    1998; Kim&Osterhout 2005 semantic-P600 = the "confidently wrong though structure is clean" case) →
    requires a real thematic-fit channel (P=0.72). Both a MISSING REPRESENTATIONAL CLASS, not a feature.
  • On-disk proof: the AGENT's competition margin is a STRONG raw signal (AUC 0.76) vs the patient's
    greedy-parser arc conf (0.50–0.62) — same move, two reliability strengths = Loss 1 made concrete.

PROPOSED hdlab WIRE (Q111 — strategy lands; ADDITIVE, opt-in, default-safe): cache (heads, conf, marg)
from the already-computed shared parse; add hdlab/parse_confidence.py (frozen glass-box calibration =
net_activation+softmax, per-reader cue sets); opt-in precision_weight_roles flag; readers attach conf(arc)
and defer below threshold. DO edit NO parse head; do NOT wire the raw patient margin (use calibrated);
the agent margin can be used raw. Default (no gating) byte-identical.

NEXT MOVES (priority): ① LAND the additive wire (safe, default-off→flip-on after live-board no-regress).
② add a MODERN who-did-what/obl reliability board arm (this live gain is board-invisible — 19c gold +
blanket-scored). ③ the two upstream organs hold the un-captured reliability: a small-beam distributional
parser + a graded thematic-fit channel (each PINNED, each a filed follow-on, neither a bolt-on).
DON'T: wire the raw patient margin; recapture via bolt-on cues (structural); chase UAS.

FILES: experiments/exp_precwt_live_whodidwhat_v1.py, exp_precwt_live_obl_space_v1.py,
  exp_precwt_live_agent_v1.py, exp_precwt_signal_loss_and_fidelity_v1.py, exp_precwt_recapture_v1.py;
  verification/test_precwt_live_readers_organ.py (6/6);
  notes/problems/<slug>/SOLVED.md. NO hdlab/ written (Q111). Glass-box, no LLM.
REVERIFY: .venv/Scripts/python.exe verification/test_precwt_live_readers_organ.py   (ALL CHECKS PASS 6/6)
AUDIT UPDATE folded into SOLVED.md §9 (BRAIN_FOUNDATIONAL_AUDIT.md §2b: parser / graded competition).
