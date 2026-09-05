---
owner_verdict: DONE
---

SOLVED (pending your verdict) — improve_the_parser_verb_argument_attachment_for_who_did_what (opus 4.8 solver)

Write-up: notes/problems/improve_the_parser_verb_argument_attachment_for_who_did_what/
  {SOLVED.md, FULL_PARSER_REPLACEMENT_consumer_analysis.md}
  + notes/research_register_general_argument_attachment_mechanism_2026-09-04.md (45-source lit scan)
Reverify (re-runs NO landed cell): .venv/Scripts/python.exe verification/test_valency_labeled_patient.py   # 5/5

WHAT SHIPS (the who-did-what PATIENT reader): read the patient off the parse the brain's way — the LABELED object
relation (obj/nsubj:pass) + correct VOICE remapping + VALENCY-slot binding, net-safe hybrid fallback — replacing
the position-based readout + lossy passive detector. Glass-box, NO LLM, zero tuned parameters.

RESULT (clean UD-EWT gold, the brief's mandated ruler; LitBank OBJECT gold is confounded — not used):
- LIVE arc_parser, patient: deployed structural_patient_pick 0.745 -> improved 0.831, +0.086 CI[0.068,0.104]
  (train +0.098); closes ~52% of the gap to the 0.913 gold-parse ceiling. HEAD-INDEPENDENT (arceager +0.077).
- Levers (ablated): VOICE +0.056 (robust_passive false-fires passive on 9.2% of ACTIVES; precise_passive fixes it),
  LABEL +0.024, valency binding. Info-free twins all LOSE CI-sep (voice +0.197, labels +0.078, heads +0.155).
- REGISTER-GENERAL: 19c clean-DO 0.773 -> 0.870 (+0.097). No-regress through the live reader (16 docs, n_q=2634:
  all 6 QA dims + aggregate 0.0-delta; 2718/8049 patient picks changed; P2 AGENT untouched).
- "Better parser kills a consumer" (owner hint) RESOLVED: under this labeled readout the stronger arceager parser
  is register-SAFE (+0.0045 on 19c, reversing the -0.0017 it causes under the position readout) — flip it ON.

FULL PARSER-REPLACEMENT + IDEAL SOLUTION (owner asks): the parse's value to consumers is the READOUT
(labels+voice+valency+confidence), not head accuracy (head-independent). Two brain signals were computed and
THROWN AWAY: dependency labels (1 of 5 head-consumers read them) and per-arc confidence (0 consumers; arc_parser
margin discriminates a correct obj-arc at AUC 0.81). Built the brain's actual two-tier architecture
(legality-gates-preference, precision-weighted): register-invariant CATEGORICAL BACKBONE (closed-class clause
segmentation + valency projection + word-order/UTAH + voice) GATES the trained parser's PREFERENCE, backbone
fallback. MECHANISM VALIDATED on a Jabberwocky battery (nonce words, pure structure): backbone patient 0.815 /
agent 0.969 — attachment needs NO corpus statistics. GENERALIZES: the ideal reader has the LOWEST cross-register
spread (0.061 across modern/19c/Jabberwocky) of any arm — does not collapse OOD. For the PATIENT the legality gate
is DORMANT (parser picks already legal) so the ideal reduces to the shipped R_final readout; the backbone tier is
ACTIVE for the AGENT (0.969 vs 0.641 positional on embedded clauses).

LOCATED NEGATIVES (fair, mechanism-tested — a full pass per the brief): a better HEAD parser doesn't move
who-did-what (head-independent; 6 engineering variants + delex/register-train/EM all wash out); precision-weighted
selectional RE-ATTACHMENT is null-to-negative and ties its shuffled-verb twin; the space/obl consumer is
head-attachment bound (labeling HURTS it). The residual to the ceiling is genuine parse-HEAD error; the brain's
register-general mechanism is built + validated (Jabberwocky), and its remaining gap on real prose is one NAMED
sub-problem: clause-segmentation precision.

NEXT STEPS for further improvement:
1) LAND the 3 Q111 diffs (precise-voice 1-liner -> labeled+valency structural_patient_pick -> flip parser_arceager).
2) Add a PATIENT-slot QA on clean gold (the live QA is agent-only, so patient gains are invisible end-to-end).
3) THE high-value lever: a more precise register-invariant CLAUSE SEGMENTER — lifts the AGENT backbone from ~0.84
   toward its 0.97 structural ceiling on real prose (the biggest remaining who-did-what gain) and activates the
   ideal reader's legality tier. Owned by the sibling the_agent_tie_wall_is_embedded_clauses... problem; the
   validated categorical backbone + Jabberwocky battery are handed to it as the ready mechanism. NOT a patient lever.

KEY REALIZATIONS: (a) reproduce the deployed baseline then ablate ONE component at a time — the biggest lever was
VOICE (the patient path silently used the lossy detector while the agent path used the precise one), not "parser
quality". (b) "better heads are head-independent" and "the better parser kills a consumer OOD" are the same fact:
the consumer TRUSTED the parse unconditionally — reading the LABELED relation + precision-weighting fixes both.
(c) the brain separates attachment LEGALITY (categorical, register-invariant) from PREFERENCE (corpus-frequency,
online-locally-re-estimated per Fine 2013); a trained parser fuses them into a frozen score, which is exactly why
it collapses OOD and the readout doesn't.

files: experiments/{exp_valency_labeled_patient_v1, exp_valency_labeled_patient_19c_v1, exp_valency_labeled_live_reader_v1,
exp_valency_labeled_patient_reattach_v1, exp_categorical_backbone_parser_v1, exp_ideal_argument_reader_v1}.py +
verification/test_valency_labeled_patient.py (5/5) + data/exp_*/metrics.json. NO hdlab written (Q111 — 3 default-safe
diffs in SOLVED §6). AUDIT UPDATE for BRAIN_FOUNDATIONAL_AUDIT §2b (patient readout PINNED-faithful; per-arc
confidence is a computed-but-unwired brain signal; QA is agent-only). Ledger malformed/incomplete: 0.
