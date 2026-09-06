---
owner_verdict: DONE
---

SUBMISSION — wire_a_defer_consumer_for_calibrated_confidence_and_realize_precision_weighting
status: SOLVED (WIP until owner_verdict: DONE). Glass-box, NO external LLM at inference OR gold. NO hdlab/ written
(Q111 — strategy lands the wire; proposed diff in SOLVED.md §6). Witness 9/9. My SOLVED.md is well-formed
(ledger: SOLVED, awaiting integration). NOTE the ledger's "malformed: 1" is a DIFFERENT folder
(expand_the_clean_semantic_memory_foundation…, no PROBLEM.md) — not mine, out of my scope.
reverify: .venv/Scripts/python.exe verification/test_defer_consumer_organ.py   # 9/9

THE BAR — MET (positive form). The predecessor PROVED the calibrated confidence's sensitivity by RANKING picks
(a diagnostic); this builds the CONSUMER that ACTS: a DEFER POLICY with a threshold tau chosen on DEV (UD-EWT
train) and applied on TEST (unseen), consuming the FROZEN landed hdlab.parse_confidence calibrator, that CHANGES
the reader's output. Having the reader ABSTAIN below tau lifts accuracy-on-ANSWERED over the BLANKET reader
(commit-on-all) on MODERN gold, CI-separated, random-confidence twin flat:
- who-did-what PATIENT (UD-EWT n=1255): 0.8789 -> 0.9662 @ 66% cov, +0.0873 CI[+0.0710,+0.1044] (twin +0.0053)
- PATIENT (QA-SRL n=8225): 0.2982 -> 0.3543 @ 47% cov, +0.0560 CI[+0.0456,+0.0664] (twin -0.0024)
- obl/spatial ATTACHMENT (UD-EWT n=2294): 0.7581 -> 0.8496 @ 63% cov, +0.0916 CI[+0.0770,+0.1067] (twin -0.0087)

FLIP-ON COST RESOLVED (net-neutral). The ~2 parses/read is removable: fold (heads,conf,marg) into the ONE shared
parse (situation_reader._cached_parse_heads keeps only [0] today, and _cached_parse_conf re-parses the same
sentence) -> removes the duplicate arc-eager parse for FREE (-0.840 ms/read); the inert global-arc_parser a2_marg
cue is droppable (obl AUC 0.7233->0.7181, -0.0052). => the defer path needs ZERO extra parses. Emitting the
confidence is byte-identical to every scored dim (additive) — recommend flipping precision_weight_roles ON after
the fold lands.

TWO LOCATED NEGATIVES, faithfully built + researched to the bottom (each a full-pass form):
(a) FALL-BACK adds nothing (both readers). Patient position fall-back -0.0016 UD / -0.0356 QA (head-independent —
    no better prior); obl locality fall-back nets 0 (dev picks tau=0 — the parser beats locality even on its
    shakiest conf-quartile, 0.5436 vs 0.3537). ABSTAIN is the deployable action, not FALL-BACK.
(b) The UPSTREAM small-beam parse posterior (LOSS 1) does NOT out-calibrate the landed confidence. A FAITHFUL
    small-beam arc-eager decode (same weights/features; log-prob accumulation) read 3 brain-foundational ways
    (agreement / Lewis-Vasishth margin / Hale-2006 entropy) is <= the greedy raw arc conf across k=6/8/16.
    MECHANISM (drilled): gold is in the beam on only 0.492 of the parser's WRONG obl arcs — HALF the errors are
    SEARCH failures (correct analysis fell off the beam = garden-path beam-pruning; Jurafsky 1996), and QBC
    ensemble-agreement over an independent parser is AUC 0.696 ~= raw 0.721 (adds nothing). ROOT CAUSE
    (dispatched research drill, literature-confirmed): the parser is LOCALLY NORMALIZED / greedily trained —
    the LABEL-BIAS pathology (Bottou 1991; Lafferty-McCallum-Pereira 2001; Andor et al. 2016 prove
    globally-normalized > locally-normalized and that BEAM WIDTH does not fix it). Hale/Levy distributions are
    defined over a globally-normalized grammar, so BOTH the theory and the psycholinguistics PREDICT this. The
    beam IS brain-foundational; the wall is the parser's TRAINING. North-star = a globally-normalized scorer with
    EXACT marginals (edge-factored Matrix-Tree; McDonald-Satta 2007 / Koo 2007), a separate problem — NOT an
    inference-time fix.

DENSITY-PHASE ROBUSTNESS (owner's phase-diagram lever — turned an observation into a proof). Stratifying real obl
arcs by competition density, the abstain gain SCALES with density: +0.0599 (sparse <=2 sites) / +0.1030 (mid) /
+0.1251 (dense >=5), confidence AUC stable (~0.73), twins flat. A SYNTHETIC controllable-density sweep (real
parser, glass-box templates, NO LLM) shows the calibrated confidence DECREASES monotonically as density rises into
the denser-than-corpus regime (0.828 D=1 -> 0.747 D=8). Defer earns its keep most exactly where competition is
densest (where the locally-normalized parser is weakest).

TWO FURTHER BRAIN-FOUNDATIONAL UPGRADES + EFFICIENCIES (this round; each a full-data CI-sep positive, no new walls):
- AGENT defer-consumer (completes who-did-what + an EFFICIENCY). The agent is read by the Competition-Model
  competition (maintains the distribution), so its reliability is the MARGIN (AUC 0.760) — abstain on the RAW
  margin, NO calibration logistic: UD 0.7367 -> 0.8238 (+0.0872 CI-sep) / QA 0.4346 -> 0.4981 (+0.0635 CI-sep),
  twin flat. Efficiency: the competition reader gets a usable reliability for free; the parse-arc readers need the
  logistic.
- JOINT-EVENT precision propagation (the reasoning substrate). Friston precision PROPAGATES: combine each role's
  P(correct) into a per-EVENT confidence. On whole-event-correct (n=662, blanket 0.680), the PRINCIPLED product
  P(agent)*P(patient) predicts AUC 0.821 — beating agent-only 0.752 / patient-only 0.642 and MATCHING a learned
  combiner 0.822. Event-level defer lifts whole-event reliability 0.680 -> 0.807 (+0.1270 CI[+0.1006,+0.1537]),
  twin flat. This realizes the brief's "every fact the reasoning reasons from carries a reliability it can defer on."

EFFICIENCIES (all measured): (E1) fold removes the duplicate parse -0.840 ms/read; (E2) drop the inert obl a2_marg
(net-zero 2nd parser, -0.0052 AUC); (E3) agent defer needs no calibration (raw margin); (E4) event combiner needs
no learned model (product matches the logistic).

CONTROLS: (1) random-confidence TWIN at matched coverage flat/loses on every arm; (2) tau chosen on DEV, applied
on unseen TEST (deployed policy, not in-sample ranking); (3) fall-back attribution (parse beats prior even on the
shaky quartile); (4) upstream attribution (0.492 gold-in-beam-when-wrong + QBC~=raw); (5) additive/no-regress
(defer(None)=False, tau=-inf == blanket byte-identical); (6) density-phase scaling; twin flat on the agent + joint
arms.

PROPOSED hdlab LANDING (Q111 — strategy applies + witnesses; SOLVED.md §6): (1) cache (heads,conf,marg) once in
_cached_parse_heads + read _cached_parse_conf from it (the -0.84ms fold); drop the obl a2_marg cue. (2) build the
ABSTAIN defer-consumer on the head-driven readout keyed on precision_weight_tau (abstain below tau; do NOT
fall-back). (3) flip precision_weight_roles default-ON (net-neutral). (4) add the AGENT defer (cheap raw-margin
threshold — no calibration). (5) put a per-EVENT joint confidence = P(agent)*P(patient) on the EventRecord so the
reasoning phase defers on whole events.

DO NOT: wire the RAW arc margin FOR THE PATIENT (weak; the AGENT raw margin IS strong — use it); wire the
small-beam posterior (located negative — label bias); use FALL-BACK for any defer (adds nothing — ABSTAIN);
re-attach the parse; quote a fall-back absolute-accuracy gain (there is none); quote the predecessor's RANKING
selective@50 numbers as this problem's result (this is a DEPLOYED-tau defer policy); put a LitBank/19c dim in a
headline.

HIGH-PRIORITY NEXT STEPS: (1) LAND the fold + abstain defer-consumer (patient/obl/agent) + FLIP
precision_weight_roles ON — this is the flip-on the problem was opened for, and it is now net-neutral cost.
(2) Put the per-EVENT joint confidence (product of role precisions) on the EventRecord — the direct bridge to the
reasoning phase. (3) Add a MODERN selective-reliability board arm (the board scores blanket accuracy on 19c gold,
so this live defer gain is board-invisible until it gets its own arm). (4) FILE the globally-normalized parser
(exact Matrix-Tree marginals) — the north-star for the ~half of parser errors that are search failures.

FILES (all experiments/ + verification/ + notes/; NO hdlab/): exp_defer_consumer_v1.py,
exp_defer_upstream_smallbeam_v1.py, exp_defer_readcost_v1.py, exp_defer_density_sweep_v1.py, exp_defer_agent_v1.py,
exp_defer_joint_event_v1.py; verification/test_defer_consumer_organ.py (9/9); notes/problems/<slug>/SOLVED.md.
REUSES: hdlab.parse_confidence (the FROZEN landed calibrator + defer), hdlab.graded_role_assigner +
graded_competition (agent margin), hdlab.predicate_argument_frontend.structural_patient_pick, arceager_parser,
and the predecessor's exp_precwt_live_* cells.

KEY REALIZATIONS: (1) a DEPLOYED policy (fixed dev-tau, changes output) is a different deliverable from a ranking
diagnostic. (2) the fall-back negative and the upstream negative are the SAME wall — no good alternative to fall
back to; the one that would beat the parse on its shaky arcs is the parse's own 2nd alternative, which a greedy
parser can't expose. (3) gold-in-beam-when-wrong = 0.492 BOUNDS the whole upstream lever: half the errors are
search failures no reweighting can reach -> the fix is a better MODEL, not a better decoder. (4) the biggest
flip-on blocker was a one-line caching bug (conf/marg computed then thrown away). (5) a controllable phase
parameter turns an observation into a proof — the defer gain RISES with density exactly as precision-weighting
predicts. (6) precision PROPAGATES: the principled product-of-role-precisions matches a learned event combiner —
the brain's rule is optimal, no model needed.

AUDIT UPDATE (BRAIN_FOUNDATIONAL_AUDIT.md §2b, parse_confidence / precision-weighting): the flip-on follow-on is
realized (prototyped) — an ABSTAIN defer-consumer lifts live selective reliability on modern gold (deployed tau,
twin flat); flip-on cost RESOLVED (fold -> net-zero extra parse); the small-beam posterior is a LOCATED NEGATIVE
(label bias — needs a globally-normalized parser, sharpening the predecessor's "needs a small-beam parser");
FALL-BACK confirmed as the expected negative (ABSTAIN is the robust action); the AGENT defer needs no calibration;
and precision PROPAGATES (per-event product-of-precisions = the reasoning substrate). Recommend flipping ON.

TLDR (plain English): the reader now ACTS on its own certainty — below a fixed bar (set once on practice text) it
holds back instead of asserting a coin-flip, and on modern writing that takes who-was-acted-on from ~88 to ~97
right-in-100, where-things-attach from ~76 to ~85, and who-did-the-action from ~74 to ~82 — a scrambled
fake-certainty control does none of it. Turning it on is now free (one parse, not two). The holding-back helps most
when the sentence is crowded. Two honest dead-ends chased to the bottom: falling back to a simpler guess adds
nothing, and rebuilding the grammar engine's certainty by keeping several analyses fails because it was trained to
make one greedy choice (the fix is a differently-built engine, filed separately). And the bigger new win: a whole
fact is only as trustworthy as its shakiest part, so multiplying the per-part certainties gives a per-fact
certainty as good as a trained model — which is exactly what the reasoning stage has to stand on.

QUESTIONS: none. (One judgment call: graded SOLVED on the positive deployed-defer result; the fall-back and beam
negatives are full-pass secondary findings.)
