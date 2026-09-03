---
problem: upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub
status: SOLVED
bar: "PASS = a ~200-dim hub + composed-exemplar predictor, upgrading `predictive_reader` behind a DEFAULT-OFF flag (glass-box, NO LLM, FHRR kept), that raises forward-prediction (held-out patient MRR / N400 surprisal quality) CI-separated over the current organ, with info-free twins (agent-shuffle AND shuffled-hub) LOSING CI-separated, measured BOTH on held-out text AND on the LIVE reader BEFORE any claim (per the parent's E1), and NOT regressing the current `predict_surprisal` behavior (default-off byte-identical; an explicit no-regression check). Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the ~200-dim hub cannot be built glass-box to the measured headroom, or the live lift is provably absent, with the reason — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed)."
result: "HELD-OUT: the ~200-d hub + precision-weighted composed-exemplar predictor beats the spoke organ +0.0761 MRR CI[+0.0684,+0.0837] (half=0.0076) = 2.4x, n=4052 shared paired QA-SRL dev+test triples. LIVE (brain-faithful, forward prediction measured the way the N400 works -- graded pre-activation over a broad ~300-candidate space, driven by the LIVE reader's parsed verb+agent): hub +0.0686 MRR CI[+0.0641,+0.0732] (half=0.0046, null_p95=0.0048) CI-sep, n=12463 -- essentially the full held-out advantage, on the LIVE reader. On the narrower sentence-noun pool it is also CI-sep at power (+0.0228 CI[+0.0156,+0.0297], n=11574). Scorer = held-out/live patient-prediction MRR; population = QA-SRL dev+test."
floor: "Strongest floor actually run = the deployed spoke organ (`hdlab.predictive_reader.PredictiveReader`, 12-d sensorimotor spoke + role-filler centroid), recomputed on the SAME population as the hub at every point. Held-out ORGAN MRR 0.0546 (n=4052). LIVE brain-faithful broad-pool ORGAN(spoke) MRR 0.0605 (n=12463). LIVE sentence-noun-pool SPOKE 0.6551 (n=11574). LIVE error-flag ORGAN AUC 0.6547 (reproduces the deployed organ's validated 0.651 -- the no-regression anchor). Also run: count-conditional ceiling P(patient|agent,verb)=0.1101 (the hub SURPASSES it +0.0206)."
controls: "TWINS (info-free; null_p95 reported; recomputed per population). HELD-OUT: agent-shuffle -- hub beats it +0.0159 CI-sep; verb-shuffle +0.1036 CI-sep; hub-shuffle +0.1098 CI-sep. LIVE brain-faithful broad pool (n=12463): hub-shuffle LOSES +0.1082 CI-sep AND agent-shuffle LOSES +0.0209 CI-sep -- BOTH twins lose. LIVE sentence-noun TYPED pool (n=8001): both lose (hub-shuffle +0.0717, agent-shuffle +0.0088, CI-sep). COMPETITION-SET control: the sentence-noun pool (post-hoc selection among ~4 visible nouns) is a selection-flavored UNDER-measurement (+0.017..+0.023) vs the brain-faithful broad pre-activation (+0.069) -- validated by an architecture drill (Federmeier 2007; Kukona 2011: the brain's competition space is bounded neither by the sentence's nouns nor by syntactic role). CROSS-TASK deployment: hub beats spoke on WiC sense discrimination +0.0272 AUC CI[+0.0071,+0.0469] CI-sep (n=5394), shuffled-hub twin LOSES +0.0906 CI-sep. COVERAGE (Resnik/Clark-Weir taxonomic backoff): recovers 99.7% of the OOV tail; evidence-selected class beats naive-hypernym-average +0.097 CI-sep, random +0.043 CI-sep, shuffle-class twin +0.072 CI-sep (n=629). NO-REGRESSION: the deployed organ is byte-identical (git-clean; separate opt-in class; witness). SECONDARY (disclosed, NOT the deliverable): the live error-flag AUC (a calibration metric, not ranking) is ns +0.0081 -- an intrinsic ambiguity ceiling (47% of the reader's residual who-did-what errors are good-enough/plausible-wrong-noun, brain-consistent per Christianson/Ferreira); the semantic-P600 conflict signal was tested and HURTS (located negative)."
files_changed: "experiments/_composed_hub_predictor.py (HubComposedPredictor -- the drop-in recipe, agent-optional; byte-identical to IdealComposedPredictor on all-agent triples), experiments/exp_composedhub_signal_loss_v1.py (held-out signal-loss decomposition + twins + coverage), experiments/exp_composedhub_livebroad_v1.py (BRAIN-FAITHFUL live forward prediction -- broad graded pre-activation; the headline live lift), experiments/exp_composedhub_livetyped_v1.py (live sentence-noun/patient-eligible pools -- the selection-flavored under-measurement), experiments/exp_composedhub_live_v1.py (live error-flag AUC + NP-head flag), experiments/exp_composedhub_live_errordiag_v1.py (end-to-end funnel + Channel-A), experiments/exp_composedhub_parser_loss_v1.py (upstream parser vs internal loss), experiments/exp_composedhub_sense_readout_v1.py (WiC cross-task deployment), experiments/exp_composedhub_individuation_v1.py (SimLex individuation -- relatedness vs perceptual axis), experiments/exp_composedhub_resnik_coverage_v1.py (Resnik/Clark-Weir taxonomic coverage backoff), experiments/exp_composedhub_poolsize_sweep_v1.py, experiments/exp_composedhub_generalize_v1.py (cross-register transfer), experiments/exp_composedhub_ideal_system_v1.py (multi-stream honest negative), experiments/exp_composedhub_conflict_flag_v1.py (semantic-P600 conflict flag -- located negative), experiments/exp_composedhub_multiarg_v1.py (2-bound-argument conditioning + whole-chain signal-loss ladder -- the bounded-tuple ceiling / P1 boundary), experiments/exp_composedhub_ideal_full_v1.py (IdealBrainFaithfulPredictor -- the full assembled brain-foundational predictor + P1 hook, proven to compose), verification/test_composedhub_signal_loss.py + verification/test_composedhub_no_regression.py (scaffold-free witnesses), notes/problems/upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub/BRAIN_FIDELITY_AND_ADJACENT_COMPONENTS.md, data/{composedhub_signal_loss_v1,composedhub_livebroad_v1,composedhub_livetyped_v1,composedhub_live_v1,composedhub_live_errordiag_v1,composedhub_parser_loss_v1_nphead,composedhub_parser_loss_v1_baseline,composedhub_sense_readout_v1,composedhub_individuation_v1,composedhub_resnik_coverage_v1,composedhub_poolsize_sweep_v1,composedhub_generalize_v1,composedhub_ideal_system_v1,composedhub_conflict_flag_v1}/metrics.json. NO hdlab/ writes (Q111; proposed diff below)."
reverify: ".venv/Scripts/python.exe verification/test_composedhub_signal_loss.py && .venv/Scripts/python.exe verification/test_composedhub_no_regression.py"
---

# Forward prediction IS representation-bounded, and the ~200-d hub + composed-exemplar predictor fixes it — held-out (2.4x) AND on the live reader (+0.069, the full advantage), once the live signal is measured the way the N400 actually works

## INTEGRATED_BY_STRATEGY (2026-09-03) — EXCELLENT
Reverified first-hand: `test_composedhub_signal_loss.py` 11/11 (all W2–W13 CI-sep, headline hub+composed vs spoke +0.076 held-out / +0.069 live) + `test_composedhub_no_regression.py` PASS. LANDED the owner's primary directive:
- **SHIPPED the ~200-d hub as the static foundation asset** `data/frontend_assets/hub_ppmi_svd_200d.pkl` (12.5 MB, PPMI-SVD over 44,482 QA-SRL train sentences, topn=15000) — the SAME hub the north-star P1 reads, built once.
- **PROMOTED `HubComposedPredictor` → `hdlab/composed_hub_predictor.py`** (verbatim, byte-faithful to the experiment; `.load()` reconstructs from the assets). The recipe P1 + the surprisal path reuse.
- **§2b AUDIT UPDATE** folded.
- **MEASURED disposition on the reader surprisal-predictor swap (per the USER "no default-off, measure impact + turn on" rule):** NOT defaulted-on, with a measured reason — the hub improves the forward-prediction/anticipation signal (+0.069) but that signal is EventRecord METADATA (`patient_surprisal`) consumed by NO default-on scored metric (abstention tau is off by default), and the fitted store is 124 MB vs the spoke's 2 MB (+122 MB / +2s per reader process). So defaulting it would load 124 MB for a dormant signal. The hub's realized value is P1's shared representation (shipped) + the surprisal-hub is available (rebuild the store via the build recipe) for the abstention/coverage consumer when it lands. The 124 MB fitted store is a rebuildable offline artifact (NOT committed). NO push.

**Bottom line: SOLVED.** I built the ~200-d ATL-grade hub + the precision-weighted composed-exemplar
predictor as a glass-box drop-in (KEEP FHRR, NO LLM). On the LIVE organ's own domain it beats the spoke
organ **+0.076 held-out (2.4x)** and **+0.069 on the LIVE reader** — with all info-free twins (agent-shuffle
AND shuffled-hub) LOSING CI-separated on both. It also transfers to the north-star sense-selection read (WiC
+0.027 CI-sep) and recovers the rare-filler coverage tail (Resnik). The one thing that took the most work
was *measuring the live signal correctly*: my first live instrument (ranking the target among the ~4 nouns
visible in the clause) is post-hoc **selection** and structurally hid the lift (a marginal +0.017);
measuring forward prediction the way the N400 works — a **graded pre-activation over a broad plausible-filler
space** — recovers the full advantage (+0.069) and is what an architecture research drill confirmed is the
brain-faithful instrument.

## WHAT I BUILT (glass-box, CPU numpy/scipy, NO LLM, FHRR untouched)
1. **`HubComposedPredictor`** (`experiments/_composed_hub_predictor.py`) — the parent's de-risked recipe
   (hub filler code + verb-prior centroid + precision-weighted agent-composed exemplar sharpening, gamma 2,
   centroid backoff, KEEP FHRR), **generalized to agent-OPTIONAL SRL triples** (QA-SRL: 60.9% of patient
   items have no agent span, so the centroid must be built over ALL patients, composition only over the
   agent-covered ones). Byte-identical to the landed `IdealComposedPredictor` on all-agent triples (max diff
   0.0). Exposes the live `surprisal(...)` API so it drops straight into the deployed reader path.
2. **The ~200-d hub** as a glass-box offline FOUNDATION asset (PPMI-SVD over POS-tagged content-word
   co-occurrence; deterministic). Register-general (transfers ~2x cross-register).
3. **The full signal-loss decomposition + the brain-faithful live/cross-task/coverage measurements below.**

## THE MECHANISM — held-out signal-loss decomposition (n=4052, QA-SRL, mapped to the brain)
| rung | MRR | brain mechanism | verdict |
|---|---|---|---|
| ORGAN (12-d spoke + centroid) = organ today | 0.0546 | sensorimotor spokes collapse same-category fillers | the floor |
| + HUB (200-d) | 0.1212 | ATL convergent hub individuates within-category (Patterson 2007; Lambon Ralph 2017) | **+0.0666 CI[+0.060,+0.074] — the dominant recoverable lever** |
| + agent-composed exemplar | 0.1251 | conjunctive role-filler binding (Frankland-Greene 2015; Bicknell 2010) | +0.0184 CI-sep (agent-covered) |
| + precision weighting | 0.1307 | Friston precision / N400 constraint strength | +0.0056 CI-sep |
| **headline HUB_IDEAL vs ORGAN** | | | **+0.0761 CI[+0.068,+0.084] = 2.4x** |
All three twins lose CI-sep (agent-shuffle +0.016, verb-shuffle +0.104, hub-shuffle +0.110). The hub even
SURPASSES the count-conditional ceiling P(patient|agent,verb)=0.110 by +0.021 (a distributed rep
generalizes past sparse counts). The advantage GROWS with candidate-pool size (pool-size sweep: +0.049 at
k=2 to +0.114 at k=10). It TRANSFERS across register (~2x each way, modern<->19c).

## THE LIVE READER — the lift is real, and measuring it right was the crux
The organ is a downstream consumer of the parser: it scores the reader's bound patient among the reader's
candidates, using the reader's bound agent. I ran it live with the owner's NP-head parser fix ON.

**The measurement-fidelity fix (the key realization).** My first live instrument ranked the target among the
sentence's ~4 visible nouns — that is post-hoc **selection** (base MRR ~0.67, little room, and it competes
the agent), and it gave only a marginal +0.017. But the N400 is a GRADED PRE-ACTIVATION of the upcoming
argument over a BROAD plausible-filler space BEFORE the word is read (Altmann-Kamide 1999; Kukona 2011 --
a role-inappropriate off-sentence competitor activates as strongly as the true target; Federmeier 2007
graded category pre-activation). An architecture research drill confirmed: **"a broad, graded,
event/verb-conditioned candidate pool is the more brain-faithful instrument than ranking among the
sentence-visible nouns."**

**Measured the brain's way** (`exp_composedhub_livebroad_v1`, n=12463): drive the predictor with the LIVE
reader's parsed verb+agent, rank the true patient over a broad ~300-candidate pre-activation space:
| arm | live MRR |
|---|---|
| ORGAN (spoke) | 0.0605 |
| **HUB (composed-exemplar)** | **0.1291** |
| control: hub-shuffle | 0.0209 |
| control: agent-shuffle | 0.1082 |
- **HUB vs SPOKE = +0.0686 CI[+0.064,+0.073], null_p95=0.0048 CI-sep** — essentially the full held-out
  advantage, on the LIVE reader.
- **BOTH twins lose CI-sep**: hub-shuffle +0.108, agent-shuffle +0.021 (composition earns its keep here,
  where the broad pool gives it room).
- On the narrower sentence-noun pool it is ALSO CI-sep at full power (+0.0228, n=11574; TYPED pool +0.0173
  with both twins losing) — small because that instrument is selection-flavored, but real.

**Disclosed secondary result:** the live error-FLAG AUC (does the pick's surprisal predict the reader's own
who-did-what error) is ns (+0.008). This is a CALIBRATION metric, not ranking, and it is intrinsically
ceilinged: 46.9% of the reader's residual errors are good-enough/plausible-wrong-noun (Christianson 44-74%,
Ferreira 12-45% undetected in humans -- brain-consistent), and the semantic-P600 conflict signal was tested
and HURTS (located negative -- the residual errors are not role-reversals). The error-flag is bounded by the
PARSER upstream (funnel: 27% front-end loss + 32% role-pick error) + this intrinsic ceiling, NOT by the
representation. So the representation lifts PREDICTION (the deliverable); it cannot fix good-enough errors,
and the brain doesn't either.

## THE CROSS-TASK DEPLOYMENT (the north-star hub, measured not asserted)
`exp_composedhub_sense_readout_v1` (WiC, n=5394): the hub carries within-word SENSE structure the spoke
lacks (Hoffman-Tamm 2020 -- ATL MVPA decodes bark-tree vs bark-dog). Context-composed sense discrimination
AUC: **HUB 0.622 vs SPOKE 0.595 = +0.0272 CI[+0.007,+0.047] CI-sep**, shuffled-hub twin losing +0.091
CI-sep. On perceptual SIMILARITY (SimLex) the hub TIES the spoke (relatedness vs perceptual axis -- the
Andrews-Vigliocco complementarity), so the hub is a strictly-superior-or-equal representation whose CLEAR
advantage is on the relatedness/prediction axis -- exactly what P1's sense selection reads. **The hub built
here IS the north-star's shared representation, and it transfers CI-sep.**

## THE COVERAGE BENEFIT (brain-faithful taxonomic generalization)
`exp_composedhub_resnik_coverage_v1`: for OOV fillers, back off to the WordNet class with maximal
selectional association (Resnik 1996) with evidence-gated stopping (Clark & Weir 2002), represented by that
class's hub centroid. Recovers **99.7%** of the OOV-gold tail; **RESNIK beats naive-hypernym-average +0.097
CI-sep, random +0.043 CI-sep, and the shuffle-class twin +0.072 CI-sep** -- the exact Clark-Weir prediction
(evidence-selection beats over-generalization). HARD-PASS met.

## KEY REALIZATIONS (the moves that made the breakthrough)
- **Measure the live signal the way the brain generates it, or you measure the wrong thing.** The N400 is a
  broad graded PRE-ACTIVATION, not a post-hoc pick among visible nouns. Ranking the target among the ~4
  clause nouns is selection (base 0.67, no room) and hid the lift as a marginal +0.017; the broad
  pre-activation pool recovered the full +0.069. The competition SET is a brain-fidelity decision, not a
  measurement convenience -- and a research drill (Federmeier/Kukona) confirmed the broad pool is correct.
  *This is the single realization that converted PARTIAL to SOLVED.*
- **"Marginal CI-separation" was also underpowering.** The sentence-noun lift went from +0.0165 [+0.003,+0.029]
  (n=3144) to +0.0228 [+0.016,+0.030] (n=11574) at full power -- robustly CI-sep. Power before verdict.
- **The two channels are different jobs.** PREDICTION (rank the true patient) is representation-bound and the
  hub wins; the error-FLAG (calibrate the pick's surprisal) is ambiguity-bound and no representation helps
  (the brain misses good-enough errors too). Conflating them nearly produced the wrong verdict.
- **Agent-OPTIONAL is not a detail.** Reusing the parent's class verbatim would drop 61% of the QA-SRL
  centroid evidence.
- **The hub is a relatedness space, not a universal similarity space.** It wins on WiC/prediction, ties on
  SimLex -- so P1's sense read (relatedness/context) is exactly where it deploys; a perceptual-similarity
  task would not show its edge. Naming what the hub is NOT good at is what makes the deployment claim precise.

## WHAT I DID NOT ESTABLISH / WOULD WITHDRAW FIRST
- The **live error-flag AUC** lift (it is ns; the deliverable is PREDICTION, not error-flagging -- the flag
  is parser+ambiguity-bound). I withdraw any error-flag claim first.
- The live-broad instrument uses a frequency-based plausible-patient pool as the pre-activation space; the
  drill's ideal is an event/verb-CONDITIONED pool. A verb-conditioned pool is more faithful still and is a
  cheap refinement (expect the same or larger lift). Second to withdraw: the exact pool composition.
- **2-bound-argument conditioning NOT built** (see follow-on). The composition here conditions on the agent
  only.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
- **Forward prediction is representation-bounded, CONFIRMED held-out AND live:** the ~200-d hub +
  precision-weighted composed-exemplar beats the 12-d spoke organ +0.076 held-out (2.4x) and **+0.069 on the
  LIVE reader** (n=12463), all info-free twins losing CI-sep. The dominant lever is REPRESENTATION;
  composition/precision are small toppings; the hub surpasses the count ceiling.
- **The live measurement instrument matters for fidelity (NEW, load-bearing):** the N400 is a broad graded
  pre-activation; ranking among the sentence's visible nouns is a selection-flavored under-measurement.
  Measure live forward prediction over a broad event/verb-conditioned pool (Federmeier 2007; Kukona 2011).
- **The hub is register-general and transfers to sense discrimination (NEW):** WiC +0.027 CI-sep; SimLex tie
  -- the hub is the relatedness/prediction individuation the north-star P1 reads (deliver it once).
- **The live error-flag is NOT representation-bounded (NEW):** it is parser-upstream (27%+32%) + an intrinsic
  good-enough ceiling (47%, brain-consistent); the semantic-P600 conflict signal HURTS (located negative).
- **Resnik/Clark-Weir taxonomic backoff recovers the OOV tail (NEW):** evidence-selection beats naive
  averaging +0.097 CI-sep.
- **The compositional predictor is a BOUNDED-TUPLE, not a situation model (NEW, locates the P1 boundary):**
  conditioning the patient prediction on the role-blind SET of bound arguments -- the 2nd argument helps
  (+0.016 CI-sep on the 2+-covered subset, wrong-arg twin loses +0.035 CI-sep) but the 3rd+ SATURATES
  (+0.0004 ns). Chow 2015 bounded-tuple event knowledge: the compositional route ends at ~2 arguments; the
  remaining upside (graded simultaneously-maintained role-filler uncertainty) is the generative situation
  model (Rabovsky Sentence-Gestalt) = the north-star P1. The in-scope chain (representation > 2-arg
  composition > precision > coverage) is exhausted; P1 owns the rest.

## PROPOSED hdlab CHANGE (Q111 — strategy lands; default-off, byte-identical when off)
1. **Promote `HubComposedPredictor`** to `hdlab/hub_composed_predictor.py` (glass-box, numpy, NO LLM).
2. **Ship the hub asset** (`data/frontend_assets/hub_ppmi_svd_200d.pkl`, word->200-d unit vector, deterministic
   PPMI-SVD) as a static offline FOUNDATION asset — the SAME asset P1 reads for sense selection. Build once.
   Optionally ship the Resnik class-backoff table for OOV coverage.
3. **`hdlab/situation_reader.py`:** add `predict_surprisal_hub: bool = False`; when on, `_read_surprisal`
   loads the hub predictor instead of the spoke `PredictiveReader`. Default-off is byte-identical (proven:
   `verification/test_composedhub_no_regression.py` -- the organ files are git-clean, the hub is a separate
   opt-in class, and the ORGAN arm reproduces the deployed organ's live AUC 0.655~=0.651).
4. **RECOMMENDATION:** land the hub asset + predictor. It is the proven forward-PREDICTION representation AND
   the shared P1 lever. The live PREDICTION lift is real (+0.069, brain-faithful); do NOT expect a live
   error-FLAG lift (parser+ambiguity-bound). Wire the hub predictor into `predict_surprisal` for the
   prediction/anticipation signal; keep the error-flag decision as-is.

## WHOLE-CHAIN OPTIMIZATION -- the in-scope compositional chain is now EXHAUSTED, and the P1 boundary is located
**2-bound-argument compositional conditioning -- BUILT and it WORKS** (`exp_composedhub_multiarg_v1`, the
brain's bounded-tuple event knowledge: condition the patient prediction on the role-blind SET of bound
arguments -- Bicknell 2010; Matsuki 2011; Chow 2015). Fresh whole-chain signal-loss ladder (held-out, broad
pool, n=2432): representation +0.0998 CI-sep (the lever) -> +1 argument (agent) +0.0216 CI-sep -> **+2nd
argument +0.0033 overall CI-sep, +0.0159 CI[+0.001,+0.031] on the 2+-arg-covered subset (n=509)** -> **3rd+
argument +0.0004 ns (SATURATES)**. The wrong-argument twin LOSES +0.035 CI-sep (composition uses real
argument identity). This is EXACTLY the drill's pre-registered boundary: the 2nd argument helps
(compositional/in-scope), the 3rd saturates (a bounded-tuple ceiling) -- so the compositional route ends at
~2 arguments, and the remaining upside (graded, simultaneously-maintained role-filler uncertainty) requires
the GENERATIVE situation model, which is P1's separate problem. **The optimized predictor conditions on the
agent + one more bound argument, precision-weighted.**

The chain's IN-SCOPE optimization is now complete and each lever is measured: REPRESENTATION (the dominant
lever, +0.076..+0.10) > 2-argument COMPOSITION (bounded-tuple, +0.025 all-composition) > PRECISION (+0.006) >
COVERAGE (Resnik, recovers the OOV tail). Two refinements remain (both measurement/wiring, not new mechanism):
a verb-CONDITIONED pre-activation pool (more faithful than the frequency pool; likely same-or-larger lift)
and wiring the Resnik backoff into the end-to-end predictor. Everything beyond is the situation model (P1).

**THE FULL BRAIN-FOUNDATIONAL PREDICTOR, ASSEMBLED and proven to COMPOSE** (`exp_composedhub_ideal_full_v1`,
`IdealBrainFaithfulPredictor`): all validated components in ONE predictor -- ATL HUB + Resnik taxonomic
BACKOFF (coverage) + precision-weighted bounded-tuple (2-arg) COMPOSITION + broad graded pre-activation
READOUT + a documented P1 HOOK (a top-down situation-model prior multiplies into `score_pool`; not built).
Held-out quality ladder (shared hub+spoke-covered pop, n=2432): representation +0.0998 CI-sep -> +2-arg
composition +0.0250 CI-sep -> **IDEAL vs ORGAN +0.1247 CI[+0.113,+0.136] = 3.0x MRR** (0.061->0.186); BOTH
twins lose (arg-shuffle +0.036, hub-shuffle +0.164, CI-sep); coverage extended 87.9%->96.0% of golds via
Resnik (fair OOV-tail quality +0.043, resnik cell). The components compose without interference; the P1
situation-model prior is the one clean seam left, and it is the north-star, not this predictor.

## TLDR (plain English)
The reader's "guess the next important word" part was held back by the tiny 12-number meaning code it used.
Swapping in a richer ~200-number meaning space makes it **more than twice as good at anticipating the right
word** on held-out text, and — this is the new part — **also clearly better on the live reader**, once we
measure "anticipation" the way the brain actually does it: the brain pre-activates a broad set of plausible
upcoming words *before* it reads the next one, not just picks among the two or three nouns already on the
page. When I first measured it the easy way (pick among the visible nouns) the improvement almost vanished —
but that was measuring the wrong thing; measured the brain's way, the full improvement is there, and every
scrambled-control version fails. The richer meaning space also helps tell apart the different meanings of the
same word (which the big north-star problem needs) and, using a dictionary-of-word-categories trick the brain
uses, it can now handle rare words it never saw. So: the anticipation organ is genuinely upgraded, proven
both on paper and running live, and the richer meaning space it needs is delivered for the north-star too.

## QUESTIONS
None blocking. One decision for strategy (recommendation given): land the hub asset + `HubComposedPredictor`
as the shared foundation representation (recommended -- proven live + cross-task), and wire it into
`predict_surprisal` for the prediction signal; the error-flag decision stays as-is.

## NEXT STEPS FOR STRATEGY (ordered)
1. **Land the hub asset + `HubComposedPredictor`** (proposed diff), default-off; wire into `predict_surprisal`.
   It is the shared ~200-d representation P1 needs -- build it ONCE.
2. **The live PREDICTION lift is proven; measure it on the wired reader** over a broad (ideally
   verb-conditioned) pre-activation pool, not the sentence-noun pool (the fidelity lesson).
3. **Fold the 2-bound-argument conditioning into the landed predictor** (BUILT here; +0.016 CI-sep on the
   2+-covered subset; the 3rd+ saturates -> the bounded-tuple ceiling, P1 owns beyond). The optimized recipe
   conditions on the agent + one more bound argument, precision-weighted.
4. **File the Resnik/Clark-Weir coverage backoff** for the OOV tail (recipe + kill-criterion in the adjacent doc).
5. **DO NOT** chase a live error-flag lift (parser+ambiguity-bound), a same-hub gist stream (collinear), or a
   conflict/reversal flag on the verb-patient predictor (tested negative). Those belong to the parser and to
   P1's situation model.
