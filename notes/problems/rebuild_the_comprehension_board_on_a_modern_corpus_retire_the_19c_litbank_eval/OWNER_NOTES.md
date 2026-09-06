---
owner_verdict: DONE
---

SUBMISSION — rebuild_the_comprehension_board_on_a_modern_corpus_retire_the_19c_litbank_eval
status: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO external LLM at inference OR in gold construction.
NO hdlab/ written (Q111 — strategy lands the wire; turnkey diff in PROPOSED_HDLAB_LANDING.md). Reader UNCHANGED —
only the corpus + golds change. Witness 12/12. Ledger malformed/incomplete: 0.
reverify: .venv/Scripts/python.exe verification/test_modern_board.py   # 12/12, deterministic, reads metrics.json

THE BAR — MET. A 19c-FREE modern comprehension board (data/situation_model_qa_modern_v1/metrics.json) scoring 7
dimensions on MODERN annotated gold, NO LitBank in the aggregate, per_dimension floor/twin/CI discipline preserved.
Item-weighted 19c-free aggregate model 0.605 vs floor 0.561 (4/7 dims CI-sep over floor). GUM fetch cited
(experiments/fetch_gum_coref_v1.py, pinned V12.1.0 @ 22fdf87). Core bar dims all on modern gold:
- COREF pronoun-pick (GUM, n=3132): 0.4681 vs separate-tracking floor 0.3621, +0.1060 CI[+0.079,+0.133], twin
  0.2034 LOSES.  ✅ EXCEEDS
- STATE (UD-EWT copular, n=378): 0.8333 vs most-recent-noun 0.5714, CI-sep, twin 0.4656 loses.  ✅ EXCEEDS
- WHO-DID-WHAT AGENT (UD-EWT, n=1423): a rigorous LOCATED FINDING (full pass) — see below.
Also modern (folded): PATIENT (UD-EWT 0.8311 vs 0.745 CI-sep), WiC (0.6639 vs 0.6006 CI-sep), COMMON-NOUN (GUM,
located negative 0.4879 vs 0.5412), SALIENCE (GUM).

THE HEADLINE LOCATED FINDING (why the 19c ban matters). The 19c who-did-what AGENT win (Competition-Model role
assigner, 0.041->0.69) is REGISTER-SPECIFIC and does NOT transfer to modern gold. On modern canonical prose the
positional floor is NEAR-CEILING (0.855 UD-EWT / 0.829 GUM discourse n=15738) because gold agent = nsubj ~=
nearest-preverbal-nominal in fixed-word-order English, and word-order is itself a high-validity brain cue. Proved
by testing the STRONGER brain version: full CM 0.758, and the 19c load-bearing lever REVERSES sign on modern
(GUM cm_dense 0.719 > cm_tracked 0.634, vs 19c 0.082 << 0.252 — the tracked-set/DuBois-PAS decouple HURTS on
modern multi-genre prose); a dev re-sweep does not rescue it (0.780 < 0.857). The twin loses throughout (the
assigner carries real signal), and its value SURVIVES on the non-canonical slice (passives). This is the CM
model's OWN prediction (cue validities are register-specific) and a decisive vindication of the 19c ban.

UPSTREAM, ALL THE WAY (every component brain-foundational, research-verified — all PINNED):
#1 UNIFIED DISCOURSE REFERENT (coref) — reused from the sibling SOLVED, EXCEEDS on modern (pronoun +0.106). DRT
   file-change + ACT-R salience + Ariel accessibility.
#2 COMPETITION-MODEL ROLE ASSIGNER — feeds BOTH who-did-what(agent) AND coref(entity-KB hard-link). On the coref
   consumer, brain-foundational gold grammatical roles beat the live POSITIONAL proxy +0.084 CI[+0.031,+0.130]
   (matches the sibling's -0.084) — the SAME upstream lifts a second consumer.

THE MECHANISM DRILL (research_agent_walls_mechanism_2026-09-06.md; experiments/_drill_agent_walls.py) — the
unifying "why", to mechanism. The agent competition is PREVERBAL-DOMINATED: P(cm==position) = 0.841 on canonical
/ 0.159 on passives. So cm is CORRELATED with the failing heuristic and on position's FAILURES recovers gold only
0.137 — BELOW random (0.155) and below the scrambled twin (0.169) — that is why the twin "beat" cm. The only
DECORRELATED cue is VOICE, which is why recovery was passive-only. This PROVES cue-reweighting cannot help
(preverbal must be high on canonical, low on failures; only a PARSE knows which regime a clause is in).

BRAIN-FOUNDATIONAL OPTIMIZATIONS + UPGRADES BUILT (all measured net-positive, twin loses, generalize, no-regress):
- byagent-cue COVERAGE fix: the landed cue needs 'by' immediately adjacent, missing multi-word by-phrases ('by US
  troops'); scan-left-for-'by' DOUBLES passive-agent recovery — UD-EWT 0.308->0.522 (+0.214 CI-sep) AND GUM gold
  POS 0.314->0.536 (+0.221 CI-sep). Cross-corpus.
- clause-local VOICE: is_passive_clause was sentence-level (a passive subordinate clause mis-flagged the main
  clause); scoping to the clause span trimmed the canonical cost.
- by-phrase-gated HYBRID (mirrors hybrid_role_patient): word-order default + override only on marked cues; net
  no-regress-to-CI-sep on the full modern set (UD +0.0029 / GUM +0.0095).
- DECORRELATED CONSTRUCTION cues (Goldberg 1995 — the upgrade the mechanism drill predicted): EXISTENTIAL ('there'
  is not an argument -> notional subject) 0.186->0.6535 (+0.467); guarded NP-COORDINATION ('NP1 and NP2 V' ->
  NP1) 0.307->0.5817 (+0.275). Together the FULL who-did-what AGENT set 0.855->0.873 (+0.018 CI[+0.015,+0.021]),
  EXACT zero canonical regress — the first clear full-set margin over position.
- NON-CANONICAL modern instrument (the discriminating gold): hybrid_bothfix 0.3915 vs position 0.2788
  (+0.113 CI-sep), passive-driven; the CM assigner's value lives where structure is non-canonical.

WALLS RESEARCHED TO MECHANISM (located negatives — each saves the next session a re-attempt):
- v3 sharper PP-government detector: passed all 6 hand-probes, REGRESSED at scale (-0.0068) — 74% of its new
  flags were false positives (relative-pronoun subjects; clause-initial pronouns after a fronted adjunct 'As a
  child in the 50's, I…'); a linear left-scan can't separate a within-NP PP-object from a fronted PP-adjunct
  without the attachment structure. Reverted.
- coordination NEUTRAL wall: the naive rule fired on CLAUSE-coordination too (position already right 56%); three
  guards (coordinator immediately joins the NPs; no ', and'; first conjunct not PP-governed) turned it into the
  +0.275 win above.
- pp-suspect WASH: rejecting the PP-object is not finding the subject (cm 0.355 vs floor 0.350; 18% unreachable).
- upstream failure diagnostic (experiments/_diagnose_agent_upstream.py): 70% of position's modern failures are
  UPSTREAM extraction (POS/candidate coverage), heterogeneous, un-recoverable by glass-box cues -> the residual
  agent headroom is the REGISTER-GENERAL PARSE problem (already filed) + Phase-1, NOT a cue fix.

TRANSFERRED-vs-GAP map (bar deliverable b), gaps DIFFERENTIATED by research:
- TRANSFERRED to modern (in the aggregate): coref/salience/common-noun (GUM), agent/patient/state (UD-EWT),
  wic (WiC).
- temporal & causal — PHASE-1-GATED, not corpus-gated: a gold from explicit connectives is circular against a
  connective-detecting reader; the only non-circular order/cause signal is world knowledge (Phase-1). Acquiring
  TimeBank/BECauSE supplies the gold but not the capability.
- goal & affect — CORPUS-ACQUISITION follow-ons (tractable): the registers extract explicit want/feel
  constructions scorable non-circularly on social_iqa / GoEmotions / story-derived gold.

NO DOWNSTREAM REGRESS: reader UNCHANGED (measurement rebuild); the CM agent change is agent-only (patient
byte-identical by construction); construction cues fire only on their constructions (exact zero canonical
regress). The proposed hdlab changes are the board instrument + a register-safe agent guardrail — no reader-
behaviour change is required to PASS.

PROPOSED hdlab LANDING (Q111 — turnkey in PROPOSED_HDLAB_LANDING.md; strategy lands + witnesses):
(0) the 19c-FREE modern board as the reported comprehension board (demote the LitBank aggregate to informational,
    keep temporal/causal/goal/affect as NAMED GAPS). (1) register-safe hybrid_agent_pick on graded_role_assigner
    (word-order default + marked-cue override). (1b) the byagent scan-left-for-'by' coverage fix. (1c) the
    existential + guarded NP-coordination construction cues. All measured net-positive, isolated, byte-identical
    on the untouched cases.

DO NOT LAND / DO NOT QUOTE: the v3 aggressive PP-government detector (regresses); the coordination rule WITHOUT
its three guards (fires on clause-coordination); a cleft agent override (verified NOT an agent lever — the nsubj
is the relativizer); the tracked-set decouple on modern (it reverses sign); a dev-tuned modern weight vector as
if it beat position (0.780 < 0.857); the 19c AGENT 0.69 as a modern result; any LitBank-scored dimension in the
modern aggregate; the item-weighted aggregate as a load-bearing single number (it crosses populations — the
per_dimension rows are load-bearing); a fabricated gold for a NAMED GAP.

FILES (all experiments/ + verification/ + notes/; NO hdlab/): exp_situation_model_qa_modern_v1.py,
exp_board_agent_slot_ud_v1.py, exp_board_agent_gum_v1.py, exp_board_coref_gum_v1.py,
exp_board_agent_noncanonical_v1.py, exp_board_agent_construction_v1.py, _diagnose_agent_upstream.py,
_drill_agent_walls.py; verification/test_modern_board.py (12/12); notes/problems/<slug>/{SOLVED.md,
PROPOSED_HDLAB_LANDING.md, research_modern_board_and_role_assigner_register_2026-09-06.md,
research_agent_walls_mechanism_2026-09-06.md}. REUSES verbatim: exp_unified_referent_gum_v1.py + gum_coref.py +
fetch_gum_coref_v1.py, hdlab.graded_role_assigner (owner-DONE), exp_board_patient_slot_v1 /
exp_situation_model_state_qa_v1 / exp_board_wic_sense_v1.

KEY REALIZATIONS: (1) a register-tuned organ's load-bearing lever can REVERSE sign on a new register — the
tracked-set decouple that carried the 19c AGENT win flips on modern; always re-measure before trusting a
transferred number. (2) "position is a strong floor" was a fact about the register (nsubj ~= preverbal in
canonical English), not a weak instrument — the discriminating signal lives in NON-CANONICAL structure. (3) the
mechanism (preverbal-dominance -> cm correlated with position -> worse than random on failures) is only visible
by PARTITIONING the failures, and it PROVES a cue can only help if DECORRELATED from position — which named the
construction-cue fix that worked. (4) a fix that passes every hand-probe can still regress at scale (v3): measure,
don't trust the probe. (5) the biggest single win was a one-cue COVERAGE bug found by reading the source.

ADJACENT / NEXT PROBLEMS: (1) the register-general incremental parse for subject attachment (the located agent
frontier; a trained parser loses OOD — filed). (2) goal + affect modern golds (corpus-acquisition). (3) the
UPSTREAM POS/candidate extractors (70% of remaining agent failures). (4) temporal + causal are Phase-1-gated.
(5) an existential-'there'-style construction sweep (cleft verified out; diminishing returns).

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md §2b): the comprehension board is now available 19c-FREE (GUM + UD-EWT +
WiC); coref +0.106 / state CI-sep on modern; who-did-what AGENT: the CM win is register-specific (the 19c 0.69
does not transfer; the tracked-set decouple reverses sign), fidelity intact (twin loses; passive win survives;
cross-consumer coref lift +0.084), and now UPGRADED on modern to 0.855->0.873 via decorrelated construction cues;
temporal/causal are Phase-1-gated, goal/affect are corpus-acquisition gaps.

TLDR (plain English): I rebuilt the reader's report card on MODERN writing (a modern annotated collection, GUM,
plus modern sentences), same fair grading, no pre-1923 fiction in the headline. Deciding who a pronoun means and
describing a thing's state clearly beat the simple baselines. The big honest surprise — the whole reason the ban
matters — is "who did what": on the old novels a brain-style method looked great (~69%), but on modern writing a
dumb "the doer is the word before the verb" rule already scores ~85%, and I proved the brain-style method's edge
was specific to old fiction. I then understood exactly WHY (it leans so hard on word-position it copies that
rule's mistakes) and used that to build the fix that works — teaching it specific sentence shapes ("there is/are…"
and "X and Y did…") — lifting the doer score above the dumb rule for the first time (85% -> 87%) with no downside.
I also fixed a real bug (it couldn't read "by US troops" as the doer; doubling its passive score, confirmed on two
corpora), dug every dead end to the bottom, and sorted the four missing skills into two that just need a modern
answer-key (goals, feelings) and two that can't be honestly graded until the system has world-knowledge (time,
cause). Everything has a scrambled-control that loses.

QUESTIONS: none. (One judgement call in SOLVED §8: the single 19c-free aggregate crosses populations, so I treat
the per-skill rows as the load-bearing claims.)

NEXT STEPS: strategy lands the bundle (byagent fix + clause-local voice + hybrid + existential + coordination
cues + the modern board), folds the AUDIT UPDATE, and files the follow-ons (register-general parser; goal/affect
modern golds). The two big frontiers — the parser and the Phase-1 meaning channel — are the real remaining work.
