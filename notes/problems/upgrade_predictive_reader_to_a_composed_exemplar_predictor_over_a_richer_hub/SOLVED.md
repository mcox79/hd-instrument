---
problem: upgrade_predictive_reader_to_a_composed_exemplar_predictor_over_a_richer_hub
status: PARTIAL
bar: "PASS = a ~200-dim hub + composed-exemplar predictor, upgrading `predictive_reader` behind a DEFAULT-OFF flag (glass-box, NO LLM, FHRR kept), that raises forward-prediction (held-out patient MRR / N400 surprisal quality) CI-separated over the current organ, with info-free twins (agent-shuffle AND shuffled-hub) LOSING CI-separated, measured BOTH on held-out text AND on the LIVE reader BEFORE any claim (per the parent's E1), and NOT regressing the current `predict_surprisal` behavior (default-off byte-identical; an explicit no-regression check). Report CI half-width + null p95; recompute floors on the same population. A rigorous located NEGATIVE — the ~200-dim hub cannot be built glass-box to the measured headroom, or the live lift is provably absent, with the reason — is a FULL PASS. Strategy lands the Q111 wire (default-off, witnessed)."
result: "HELD-OUT (the mechanism): the ~200-d hub + precision-weighted composed-exemplar predictor beats the spoke organ +0.0761 MRR CI[+0.0684,+0.0837] (half=0.0076) = 2.4x, scorer=held-out patient-prediction MRR over a 300-patient pool, n=4052 shared paired QA-SRL dev+test triples (the LIVE organ's own domain). LIVE (the deployment): on the live reader the hub does NOT beat the spoke CI-separated — error-flag AUC +0.0081 CI[-0.0098,+0.0266] ns (n=2979); live patient-MRR (Channel A, sentence-noun pool) +0.0116 CI[-0.0029,+0.0260] ns (n=2650). The located reason is measured end-to-end (see controls + funnel)."
floor: "Strongest floor actually run = the deployed spoke organ (`hdlab.predictive_reader.PredictiveReader`, 12-d sensorimotor spoke + role-filler centroid), recomputed on the SAME population as the hub at every point. Held-out ORGAN MRR = 0.0546 (n=4052). Live ORGAN error-flag AUC = 0.6547 CI[0.6343,0.6755] (reproduces the deployed organ's validated 0.651, the no-regression check). Live SPOKE Channel-A MRR = 0.6478 (n=2650). Also run: the count-conditional ceiling P(patient|agent,verb)=0.1101 (the hub SURPASSES it, +0.0206) and P(patient|verb)=0.1182."
controls: "HELD-OUT twins (all recomputed on the shared population, null p95 reported): AGENT-SHUFFLE (permute agent keys in composition) -- HUB_IDEAL beats it +0.0159 CI-sep => composition carries real signal; VERB-SHUFFLE (permute verb-store keys) -- +0.1036 CI-sep => verb-keying real; HUB-SHUFFLE (permute the hub vectors across words) -- +0.1098 CI-sep => the hub CONTENT, not the machinery, does the work. Each twin excludes a specific artifact. LIVE twins: HUB-SHUFFLE loses +0.0975 CI-sep on live Channel-A (the hub is real live signal) BUT HUB vs SPOKE is only +0.0116 ns and AGENT-SHUFFLE is ns (composition adds nothing in the live small pool). POOL-SIZE SWEEP (random distractors, held-out): hub beats spoke CI-sep at EVERY k -- k=2 +0.0485, k=3 +0.0783, peak k=10 +0.1135, k=300 +0.0456 -- so the live null is NOT a small-pool artifact. PARSER-LOSS (NP-head fix ON vs OFF): reader who-did-what error 0.392->0.312; composition delivers ~0 in the live pool either way. END-TO-END FUNNEL (n=5000): front-end lost 27.4% (gold-pronoun 8.7% + extraction-miss 8.3% + abstain 10.4%), rep-coverage ~11.5%, role-pick error 32.2%, and 46.9% of residual errors are UN-FLAGGABLE (the wrong pick is a plausible patient). CROSS-REGISTER: a hub built on modern QA-SRL beats the spoke on 19c LitBank (0.146 vs 0.061) and vice-versa -- the hub transfers."
files_changed: "experiments/_composed_hub_predictor.py (the drop-in HubComposedPredictor -- the parent's IdealComposedPredictor recipe generalized to agent-OPTIONAL SRL triples + given the live surprisal API; verified byte-identical to IdealComposedPredictor on all-agent triples), experiments/exp_composedhub_signal_loss_v1.py (held-out signal-loss decomposition + coverage + twins), experiments/exp_composedhub_live_v1.py (live-reader AUC/abstain, hub vs deployed organ, NP-head flag), experiments/exp_composedhub_parser_loss_v1.py (upstream parser vs internal loss, NP-head ON/OFF), experiments/exp_composedhub_ideal_system_v1.py (multi-stream ideal-system prototype -- honest negative), experiments/exp_composedhub_generalize_v1.py (cross-register hub transfer), experiments/exp_composedhub_poolsize_sweep_v1.py (hub advantage vs pool size), experiments/exp_composedhub_live_errordiag_v1.py (end-to-end funnel + live Channel-A), verification/test_composedhub_signal_loss.py (scaffold-free witness, 7/7), data/{composedhub_signal_loss_v1,composedhub_live_v1,composedhub_parser_loss_v1_nphead,composedhub_parser_loss_v1_baseline,composedhub_ideal_system_v1,composedhub_generalize_v1,composedhub_poolsize_sweep_v1,composedhub_live_errordiag_v1}/metrics.json. NO hdlab/ writes (Q111; the proposed diff is stated below)."
reverify: ".venv/Scripts/python.exe verification/test_composedhub_signal_loss.py"
---

# The forward predictor IS representation-bounded and the ~200-d hub fixes it (2.4x held-out) — but the LIVE who-did-what deployment does not lift, and I disambiguated exactly why: the loss is upstream (parser) + an intrinsic error-flag ceiling, not the representation

**Bottom line (PARTIAL, and it meets the bar's sanctioned located-negative clause).** I built the ~200-d
ATL-grade hub + the precision-weighted composed-exemplar predictor as a glass-box drop-in, and on the LIVE
organ's own domain (QA-SRL) it beats the current spoke organ **+0.076 MRR = 2.4x, CI-separated, with all
three info-free twins losing CI-separated** — the brief's core hypothesis (forward prediction is
representation-bounded; the hub is the lever) is **confirmed at power**. But the specific LIVE lift the
brief demanded is **absent** (error-flag AUC +0.008 ns; live patient-MRR +0.012 ns), and I traced the
whole pipeline to show **why**: on the live reader the losses that matter are upstream (parser front-end
27% + role-pick error 32%) and an intrinsic error-flag ceiling (47% of residual errors are semantic
near-ties), while the live candidate competition is *selection*-flavored (it competes co-event
participants), where — per the parent — position dominates and a thematic-fit predictor cannot separate
from the spoke. The representation is the lever for **pure forward prediction**; its deployment payoff is
the fine-grained north-star read (P1 sense selection), not the coarse live who-did-what flag.

## WHAT I BUILT (glass-box, CPU numpy/scipy, NO LLM, FHRR untouched)
1. **`HubComposedPredictor`** (`experiments/_composed_hub_predictor.py`) — the parent's de-risked
   `IdealComposedPredictor` recipe (hub filler code + verb-prior centroid + precision-weighted
   agent-composed exemplar sharpening, gamma 2, centroid backoff, KEEP FHRR), **generalized to
   agent-OPTIONAL SRL triples**: the centroid is built over ALL attested patients, the composition only
   over the agent-covered exemplars. This was necessary and non-cosmetic — 60.9% of QA-SRL patient items
   have no agent span, so the parent's class (which couples them) would drop 61% of the centroid's
   evidence. Verified byte-identical to `IdealComposedPredictor` on all-agent triples (max diff 0.0). It
   exposes the live `surprisal(verb, role, actual, cands, agent)` API so it drops straight into the
   deployed `_forward_prediction_live` / `situation_reader._read_surprisal` path.
2. **The ~200-d hub** as a glass-box offline FOUNDATION asset — PPMI-SVD over POS-tagged content-word
   co-occurrence from the register's raw exposure (`hdlab.distributional_meaning_channel.ppmi_svd`,
   deterministic). Built register-native per domain and shown to transfer cross-register.
3. **A full SIGNAL-LOSS DECOMPOSITION** of the forward-prediction organ, mapped to the brain stage by
   stage (below), and an **end-to-end funnel** of the live pipeline.

## THE SIGNAL-LOSS DECOMPOSITION — where the process loses signal, and the brain mechanism at each stage
Held-out QA-SRL, one shared paired population (n=4052), everything recomputed on the same items:

| rung | MRR | brain mechanism | verdict |
|---|---|---|---|
| ORGAN (12-d spoke + centroid) = organ TODAY | 0.0546 | sensorimotor spokes collapse same-category fillers | the floor |
| + HUB (200-d) representation | 0.1212 | ATL convergent hub individuates within-category (Patterson 2007; Lambon Ralph 2017) | **+0.0666 CI[+0.060,+0.074] CI-sep — the dominant recoverable lever** |
| + agent-composed exemplar | 0.1251 | conjunctive role-filler binding / Bicknell agent x verb | +0.0184 CI-sep on the agent-covered subset (small; bounded by coverage) |
| + precision weighting | 0.1307 | Friston precision / N400 constraint strength | +0.0056 CI-sep (earns its place) |
| count-conditional ceiling P(patient\|agent,verb) | 0.1101 | — | the hub SURPASSES it +0.0206 (a distributed rep generalizes past sparse counts) |
| **headline HUB_IDEAL vs ORGAN** | | | **+0.0761 CI[+0.068,+0.084] = 2.4x MRR** |

- **Intrinsic vs recoverable (the research-drill diagnostic):** the gap from the ceiling to 1.0 is the
  graded fan-out the brain ALSO pre-activates (Altmann-Kamide 1999; Metusalem 2012) — *correct behaviour,
  not loss*. The gap from ORGAN to hub is *recoverable representational* loss, and it is the lever.
- **All three twins LOSE CI-sep** (agent-shuffle +0.016, verb-shuffle +0.104, hub-shuffle +0.110), with
  null p95 reported in the cell. The hub-shuffle twin (representation destroyed) is the load-bearing one.
- **The advantage scales with pool size, not against it** (pool-size sweep, random distractors): hub beats
  spoke CI-sep at k=2 (+0.049) rising to k=10 (+0.114). So the live null is NOT a small-pool artifact —
  the hub genuinely predicts better even in a 2-3 candidate competition.
- **The hub GENERALIZES across register** (the owner's question): a hub built on modern QA-SRL beats the
  spoke on 19c LitBank and vice-versa (~2x each way); the only residual is vocabulary coverage — exactly
  the "similarity structure transfers, content is experience-shaped -> partial transfer" the ATL
  literature predicts.

## THE LIVE READER — the located negative, and the full disambiguation (the owner's core ask)
The forward-prediction organ is a **downstream consumer of the parser**: it scores the reader's ROLE PICK
(the bound patient) among the reader's candidate nominals, using the reader's bound agent for composition.
I ran it live with the owner's landed NP-head parser fix ON. **The end-to-end funnel (n=5000 patient
items) shows where the LIVE signal is lost:**

| stage | loss | what it is |
|---|---|---|
| 1. Front-end (parser + scope) | **27.4%** | gold is a pronoun (8.7%, out of scope) · extraction miss (8.3%) · reader abstains (10.4%) |
| 2. Representation coverage | ~11.5% | pick/verb OOV of the hub (200-d/15k vocab; the hub covers marginally more than the spoke) |
| 3. Role-pick (who-did-what) error | **32.2%** of picks | the parser's residual error — the NP-head fix cut it from ~39% (0.392->0.312) |
| 4. Error-flag ceiling | **46.9%** of errors | the wrong pick is itself a plausible patient (semantic near-tie) -> un-flaggable by ANY surprisal |

And the **representation's** place in this pipeline:
- **Live error-flag AUC:** ORGAN 0.6547 -> HUB_IDEAL 0.6628, **+0.0081 ns** (n=2979). Not CI-separated.
- **Live patient-MRR (Channel A, the bar's "live patient MRR"):** SPOKE 0.6478 -> HUB 0.6594, **+0.0116 ns**
  (n=2650). The hub-shuffle twin loses **+0.0975 CI-sep**, so the hub IS real signal — it just does not
  separate from the spoke on the LIVE pool.

**Why the +0.076 held-out lift shrinks to +0.012 ns live — the reconciliation:** the live candidate pool is
the sentence's own nouns (median 3), which are the AGENT and obliques — *co-event participants*, not random
distractors. Ranking the patient against the agent is a *selection* task, and the parent established
(Competition Model; MacWhinney-Bates) that English who-did-what selection is **word-order-dominant** — a
thematic-fit/prediction representation is secondary there and cannot separate from the spoke. The hub's
proven advantage is on *prediction* (random-distractor pools), which the held-out MRR and the pool-size
sweep isolate; the live sentence-noun competition mixes in the selection regime where position rules.

## WHAT I DID NOT ESTABLISH (and will not claim)
- **A CI-separated LIVE lift.** It is absent (both AUC and Channel-A). This is the honest negative; I do not
  dress the +0.012 ns as a win.
- **That composition helps the LIVE reader.** It does not (agent-shuffle twin ns live; composition delivers
  ~0 in the live pool). Composition is a held-out prediction effect (agent-covered +0.018 CI-sep) that does
  not transfer to the small selection-flavored live pool.
- **The cross-task transfer to P1 sense selection, measured.** I give the *mechanistic* case (the hub is the
  fine-grained-prediction lever; the pool-size sweep shows its advantage is fine individuation) but did NOT
  build a WSD selector — that is P1's active problem and I avoided competing with it. The transfer is
  asserted-with-evidence, not measured on the WSD gold. See NEXT STEPS.
- **A "more ideal" multi-stream gain.** The event-schema/gist second stream, built from the SAME hub, is
  redundant (an honest negative, below).

## THE IDEAL-SYSTEM PROTOTYPE (the owner's "prototype an ideal system + research the gaps") — honest negative that sharpens the map
Per the research drill, the N400 is fed by multiple streams (Kuperberg-Jaeger); I added a second
event-schema/associative stream (candidate fit to the sentence gist) and combined it precision-weighted.
**It does not beat the hub-structured stream alone** (AB vs A = -0.003 ns; the context-shuffle twin barely
loses). The reason, confirmed by a second research drill: a gist stream built from the same hub is
**collinear** with it (both from co-occurrence) — no integrator recovers signal from a redundant cue. The
genuinely orthogonal strong stream is **entity/role-keyed narrative chains** (Chambers-Jurafsky) /
Sentence-Gestalt — structurally different statistics [P(concept | scene-across-clauses)] — which is exactly
the north-star P1's build. So the "ideal system" is not a fancier integrator over the same hub; it is a
second STRUCTURED stream, and that stream is P1.

## WHAT I WOULD WITHDRAW FIRST IF WRONG
The Channel-A live comparison rests on the live candidate pool being the sentence's nominal heads (mirroring
the deployed organ). If the intended live instrument is a *vocabulary-pool* forward prediction (predict the
patient among a fixed pool BEFORE reading, like held-out), then the hub's +0.076 IS the live number and the
verdict flips to a full PASS — but that is not what the deployed `_read_surprisal` does (it competes
sentence nominals for the error-flag), so I scored the deployment as built. Second: the "selection-flavored
live pool" reconciliation leans on the parent's position-dominance law; if a future live pool excluded the
agent/obliques (parse-typed patient candidates only), the hub might separate — untested, and it needs the
parse-typed candidate set the front end does not yet expose.

## KEY REALIZATIONS (the moves that turned a "prove the lift" task into a located disambiguation)
- **Separate the two channels or conflate the whole result.** "Forward prediction" is TWO jobs: rank the
  true patient (Channel A, representation-bound) and flag the reader's error (Channel B, ambiguity-bound).
  The hub is the lever for A and irrelevant to B. I initially proxied A with B's error-flag AUC and nearly
  reported the wrong wall.
- **The wall I first named was wrong, and the control caught it.** I first explained the live null as
  "small-pool coarseness"; the pool-size sweep REFUTED that (hub wins at k=2-3). The real cause is the live
  pool being *selection*-flavored (co-event distractors), which only surfaced by asking "parser tree or role
  pick?" — you score the role pick among the scene's nouns, so you inherit the selection regime.
- **"Are you a consumer of the parser?" reframed the whole budget.** The biggest live losses are upstream
  (front-end 27% + role-pick 32%), so the NP-head parser fix (0.392->0.312) bought more live who-did-what
  than any representation change could. The representation and the parser fix each own a DIFFERENT loss.
- **A distributed hub beats the empirical count ceiling.** The 200-d hub surpasses P(patient|agent,verb)
  count estimates (+0.021) because it smooths sparse held-out counts — the brain-faithful reason a
  distributed rep generalizes past memorized co-occurrence.
- **Agent-OPTIONAL is not a detail.** Reusing the parent's class verbatim would have silently dropped 61% of
  the QA-SRL centroid evidence; the fix (centroid over all patients, composition over agent-covered) is what
  made the QA-SRL fit honest.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
- **Forward prediction is representation-bounded, CONFIRMED on the live organ's own domain (QA-SRL):** the
  ~200-d ATL-grade hub + precision-weighted composed-exemplar beats the 12-d spoke organ +0.0761 MRR CI-sep
  = 2.4x (n=4052); all three info-free twins lose CI-sep; the hub even surpasses the count-conditional
  ceiling. The dominant recoverable loss is REPRESENTATION (+0.0666); composition (+0.018 agent-covered) and
  precision (+0.006) are small toppings. `predictive_reader`'s entry should read PINNED-in-form,
  representation-bounded, with the hub as the proven fix for PREDICTION.
- **The hub is register-general (NEW):** a hub built on one register beats the spoke ~2x on the other; the
  residual is vocabulary coverage, not similarity structure. This is the shared representation the
  north-star P1 needs — deliver it ONCE.
- **The live who-did-what error-flag is NOT representation-bounded (NEW, load-bearing):** on the live reader
  the hub does not beat the spoke CI-sep (AUC +0.008 ns; Channel-A patient-MRR +0.012 ns) because (a) the
  live candidate pool competes co-event participants (selection-flavored; position dominates, per the
  Competition Model) and (b) 46.9% of the reader's residual who-did-what errors are semantic near-ties no
  surprisal can flag. The live who-did-what bottleneck is UPSTREAM (parser front-end 27.4% + role-pick error
  32.2%), not the meaning representation. Keep `predict_surprisal` default-off for the live flag.
- **The multi-stream "more ideal" gain is an honest negative on a same-hub gist stream (redundant/collinear);
  the orthogonal strong stream is entity/role-keyed narrative chains (P1), not a bag-of-context bolt-on.**

## PROPOSED hdlab CHANGE (Q111 — strategy lands; default-off, byte-identical when off)
1. **Promote `HubComposedPredictor`** (`experiments/_composed_hub_predictor.py`) to
   `hdlab/hub_composed_predictor.py` (glass-box, numpy, NO LLM). It exposes `fit(triples)` / `surprisal(...)`
   / `precision(...)` and is byte-identical to the landed `IdealComposedPredictor` on all-agent triples.
2. **Ship the hub asset** as a static offline FOUNDATION asset (`data/frontend_assets/hub_ppmi_svd_200d.pkl`,
   word->200-d unit vector, built by the deterministic PPMI-SVD path). This is the SAME asset the north-star
   P1 reads for sense selection — build it once.
3. **`hdlab/situation_reader.py`:** add a `predict_surprisal_hub: bool = False` flag alongside the existing
   `predict_surprisal`. When on, `_read_surprisal` loads the hub predictor + asset instead of the spoke
   `PredictiveReader`. Default-off is byte-identical (the spoke path is untouched — my ORGAN arm reproduces
   the deployed organ's live AUC 0.655~=0.651, the no-regression check).
4. **RECOMMENDATION (honest, deflated):** land items 1-2 (the hub asset + predictor) because the hub is the
   proven forward-PREDICTION representation and the shared P1 lever. Do NOT flip `predict_surprisal_hub` on
   for the live who-did-what flag — it shows no CI-separated live gain, and the live bottleneck is the parser
   + the error-flag ambiguity ceiling, not the representation. The flag exists for downstream fine-grained
   reads (P1), where the hub's advantage lives.

## TLDR (plain English)
The reader has a "guess the next important word" part (the brain's anticipation signal). I proved its guesses
are held back by the tiny 12-number meaning code it uses: swapping in a richer ~200-number meaning space
makes it **more than twice as good at anticipating the right word**, measured carefully on held-out text,
with scrambled-control versions all failing — so the richer meaning space is real and it even works across
old and modern writing. But when I plugged it into the live reader, it did **not** measurably help the live
"who did what to whom" job, and I found exactly why: on a live sentence the reader is choosing between the
handful of nouns actually present (usually the doer and the thing-done-to), and telling those apart is mostly
a grammar/word-order job, not a meaning job — plus about a quarter of the signal is lost before the guesser
even runs (the grammar-reader misses or declines), a third of the reader's mistakes are grammar mistakes
(which the new grammar fix you just shipped is already reducing), and about half of the remaining mistakes
are genuinely ambiguous (both nouns are plausible), which no meaning code can flag. So: the richer meaning
space is proven and worth keeping — but its payoff is on the "which specific meaning" job (the big north-star
problem), not the live who-did-what flag, where the real fix is the grammar-reader you are already improving.

## QUESTIONS
None blocking. One decision for strategy (with a recommendation): land the hub asset + `HubComposedPredictor`
as the shared foundation representation for the north-star P1 (recommended — proven 2.4x forward-prediction
lever, register-general), but keep `predict_surprisal_hub` default-off (no live who-did-what gain).

## NEXT STEPS FOR STRATEGY (ordered)
1. **Land the hub asset + `HubComposedPredictor`** (proposed diff above), default-off. It is the shared ~200-d
   representation P1 needs; build it ONCE.
2. **Route the hub to P1 (the cross-task deployment the hub's evidence points at):** measure the hub on the
   WSD/sense-selection instrument (the fine-grained "which specific rare sense" read) — the pool-size sweep
   predicts this is where the hub's fine individuation pays. I did not build it to avoid competing with the
   active P1 solver; hand it the hub + the mechanistic evidence.
3. **The live who-did-what bottleneck is the PARSER, and it is already being fixed:** the NP-head fix cut the
   role-pick error 0.392->0.312. The next live lever is front-end recall (extraction-miss 8.3% + abstain
   10.4%), not the representation.
4. **DO NOT** flip `predict_surprisal_hub` on for the live surprisal flag, and DO NOT chase a second
   bag-of-context stream (collinear, honest negative). The orthogonal strong stream is P1's narrative-chain
   situation model.
