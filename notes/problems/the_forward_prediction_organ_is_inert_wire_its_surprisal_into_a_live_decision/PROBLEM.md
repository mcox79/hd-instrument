---
priority:
review: EXCELLENT
review_text: "Reverified 8/8 first-hand. The forward-prediction organ (predictive_reader, N400 thematic-fit surprisal) is validated LIVE through read() as an error-RISK FLAG + a working ABSTAIN decision, and the ambitious auto-revise decision is a rigorously DECOMPOSED negative. BOTH gates MET with power: INFORMATIVE — live per-argument surprisal predicts the reader's OWN who-did-what errors AUC 0.651 [0.630,0.672] CI-sep, shuffle-surprisal twin p95 0.519 (loses); ACTIONABLE — surprisal-abstain lifts committed accuracy at 80% coverage 0.633 vs random-abstain twin 0.598 (+0.035 [0.022,0.050] CI-sep). GRADED signature (precision-weighted, CI-sep at power) + GENERALIZES to 19c LitBank (AUC 0.624, twin loses — not a modern-vocab artifact). THE WALL decomposed + built-across 7 probes to an evidence-forced terminus: auto-revise fails (−0.002), and the DECISIVE TEST shows the reader's wrong pick is NO more similar to gold than a random competitor (0.221 vs 0.229) → the errors are STRUCTURAL (wrong entity), which is WHY every semantic signal fails; parse-disagreement fails in the opposite direction (silent positional defaults) → the residual is parser-recall-bound (the p2 predictive parser is the sole lever). Brain-led (4 drills): two dissociable streams — the N400 thematic-fit FLAG works; LIFG/P600 structural conflict is the parser's, not a flag's; surprisal is a RISK FLAG not a verdict (parse-as-truth == the info-free null), the brain's action is withhold/re-read not auto-revise (Ferreira/Gibson). 8 controls, every margin with CI half-width + null p95. Exemplary 'diagnose a negative before labeling it' + 'rule out the cheap hypothesis' (richer 1024-d space made it WORSE; the crude count beat the brain-faithful confusability). Modest absolute effect is faithfully what an N400 risk-signal IS. WIRE: the one-line frame_induction.is_passive_real IndexError bug it flagged is FIXED (hdlab); the predict_surprisal flag is QUEUED (needs an offline-fitted predictor asset + an EventRecord schema field — a focused build, precise target in WIRING_MAP). First live node of the prediction-error hierarchy."
---

# PROBLEM: the substrate BUILT the brain's forward-prediction control signal but it is a PURE INERT ISLAND. `hdlab/predictive_reader.py` computes the brain's single best account of the N400 — the verb (+ its thematic role) PRE-ACTIVATES the expected argument's grounded features, and the mismatch against the actual argument is read out as −log P softmax SURPRISAL — and it was VALIDATED on held-out QA-SRL (surprisal beats a reactive baseline +0.199 and an info-free wrong-verb twin +0.095; tracks distributional thematic-fit). BUT it is never called on any live reader path: `situation_reader`/`substrate` do not import it, and the one hdlab file that references it (`incremental_parser`) takes it only as an optional `predictor=None` param that is inert by default (BRAIN_FOUNDATIONAL_AUDIT §2b, 2026-08-31). So the forward half of predictive coding drives NO decision. Meanwhile the brain uses prediction error as its universal control signal (write-to-memory-when-surprised; predict-and-revise reading of a noisy parse), and MULTIPLE just-landed reading dimensions are ceiling'd by exactly the gap this fills: the SPACE dimension proved end-to-end that parse-as-EVIDENCE-fused-with-a-PREDICTION-PRIOR beats parse-as-TRUTH (parse-as-truth sat AT the info-free null; "the fix is the brain's predict-and-revise reading, not a fancier parser"), and causation/role recall hit the same parser-recall wall. Prove the forward-prediction signal, computed LIVE through `SituationReader.read()`, is a real decision-relevant signal — it predicts the reader's OWN comprehension errors CI-separated over chance with a shuffled-surprisal twin LOSING — AND drives ONE brain-faithful downstream decision that measurably improves the reader. If the live signal is too weak to act on, enumerate WHY (which points at the grounded-space / meaning lever). This turns the inert forward predictor into a live control signal — the can-fail FIRST STEP of the prediction-error program.

**slug:** `the_forward_prediction_organ_is_inert_wire_its_surprisal_into_a_live_decision` — **opened:** 2026-08-31 by
the strategy session (BRAIN_FOUNDATIONAL_AUDIT §2b heartbeat scan: predictive_reader is PINNED + held-out-validated but
a PURE INERT ISLAND; the SPACE integration independently confirmed the noisy-channel prior is the parser-recall
ceiling-lever). **status:** OPEN — a WIRE + MEASUREMENT problem (the organ is built + validated in isolation; this
computes it LIVE, proves it is decision-relevant, and drives ONE decision). You build + validate in `experiments/`;
strategy lands the hdlab wire (Q111, default-off flag, witness required). NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2` — HIGH, below only the learner capstone (p1).
> This is the can-fail FIRST STEP of the prediction-error direction — the substrate's single biggest built-but-inert
> fidelity gap (the brain's universal control signal is built at 4 levels; 3 are inert islands, the 1 wired node
> [`gap_detector`] does not demonstrably fire a decision). It is ALSO the CONVERGENT ceiling-lever: SPACE, causation,
> and roles are all ceiling'd by parser recall, and the brain's fix is predict-and-revise, which this signal supplies.
> And one slice (`gap_detector`, the memory-novelty write-gate) is on the LEARNER's critical path (the "notice you were
> surprised → learn this" gate). Scoped DELIBERATELY to ONE decision + a positive control — NOT the whole 4-level
> hierarchy (that is the follow-on program). **Re-rank per the owner.** ⚠️ Compose with the reader's capable flags ON
> (`python tools/reader_capabilities.py`); measure against the correct reader state, not the artificially-weak default.

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing — owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** — the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau — it is the FIRST thing you do.
>
> **🚀 YOU ARE ENABLED — AND EXPECTED — TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **⛔ "CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **🔁 THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) — RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one — and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps — AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) — that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When you read, your brain constantly guesses the next word's meaning before it arrives, and it pays special attention
exactly when the guess is wrong — that surprise is the signal it uses to update its memory and to re-read a confusing
sentence. We BUILT that guessing machine, showed it works on real data, and then left it switched off: nothing in the
live reader ever actually computes the surprise or uses it for anything. Turn it on: compute the surprise as the reader
reads real stories, show that the surprise reliably flags the places the reader gets "who did what" wrong (a scrambled
version of the surprise must NOT flag them), and then use it for ONE concrete thing — e.g. "when the reader is very
surprised, trust it less / hold the answer" — and show that makes the reader measurably better. If the surprise signal
turns out too weak to act on, say exactly why (that points at how coarse our meaning representation is).

## 2. WHY THIS ONE
It is the substrate's biggest built-but-unplugged brain mechanism, and it is the convergent fix for a wall three
different reading dimensions just hit. The brain runs on prediction error — it is how it decides what to store, where to
segment events, and when to re-read. We have the forward-prediction piece built and validated but completely inert. And
the recent SPACE work proved, end-to-end, that leaning on a prediction PRIOR (not trusting the raw parse) is what makes
the reader actually track state — the exact thing this organ supplies. Proving the live signal is real and actionable is
the responsible, bounded first step before committing to the full multi-level prediction-error program.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate the operation):** forward prediction / pre-activation of the expected argument's MEANING features
  (Altmann & Kamide 1999; McRae et al. 1998 thematic fit) — predict features, NOT the word-form (Nieuwland 2018). The
  ERROR is the signal: surprisal = −log P under softmax competition (Hale 2001; Levy 2008; Michaelov 2024 — LM surprisal
  is the best single account of the N400). Prediction error DRIVES memory encoding (hippocampal write-on-surprise; the
  CA1 novelty/gap comparator) and RE-READING (predict-and-revise noisy-channel comprehension — Levy/Gibson; confirmed
  live by the SPACE dimension: parse-as-evidence+prior > parse-as-truth). Precision-weighting: a sharp verb makes a
  high-confidence prediction that should be trusted more (Friston constraint strength).
- **OUR-INVENTION (sweep, do NOT adopt as truth):** the specific downstream decision the surprisal gates (the
  write/abstain/revision THRESHOLD), the softmax temperature, and exactly how live surprisal is computed on the reader's
  own event/argument stream. The grounded space is the feature basis (its coarseness is a known ceiling — measure it).

## 4. MEASURED vs INFERRED
- **MEASURED:** `predictive_reader` is validated IN ISOLATION on held-out QA-SRL (surprisal beats reactive +0.199, an
  info-free wrong-verb twin +0.095; thematic-fit Spearman 0.239; reversible-role AUC 0.619) — INHERIT this, do NOT
  re-derive it. It is a PURE INERT ISLAND (never computed on a live reader path). SPACE independently MEASURED that the
  prediction prior is the ceiling-lever (parse-as-truth == the info-free null; a stronger general parser does not help).
- **INFERRED (you must measure):** whether the forward-prediction signal, computed LIVE on the reader's OWN stream, (a)
  is decision-relevant — predicts the reader's own who-did-what/comprehension errors CI-separated over chance, shuffled-
  surprisal twin LOSING; and (b) can drive ONE brain-faithful decision that improves a downstream metric CI-separated,
  info-free twin losing — or is too weak (grounded-space ceiling), enumerated.

## 5. ALREADY TRIED / DO NOT RE-RUN
- `the_reader_is_feed_forward_where_the_brain_is_predictive` (integrated EXCELLENT — built predictive_reader) — INHERIT
  its isolation result; this is the LIVE-wiring + decision test, not a re-derivation of the organ.
- `wire_the_incremental_parser_as_the_reader_extraction_front_end` (integrated — the parser-as-role-candidate-source is a
  proven NEGATIVE/fidelity error). This is about the PREDICTION SIGNAL driving a decision, NOT re-restricting the role
  binder to a parser's candidate set. Do NOT re-wire the parser as the role source.
- `gap_detector` (CA1 novelty comparator) is WIRED but ablation-AMBIGUOUS (turning it off moved no counter). If your
  decision is a write-gate, READ its state and compose — do not build a second novelty signal blind to it.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Run `python tools/reader_capabilities.py` (the flag/default manifest). Read `hdlab/predictive_reader.py` (fit/predict/
  surprisal/precision), its witness `verification/test_predictive_reader_organ.py`, and the BRAIN_FOUNDATIONAL_AUDIT §2b
  2026-08-31 predictive_reader entry. CONFIRM on disk it is not called on any live path (grep situation_reader/substrate).
- Read how SPACE used the noisy-channel prior (`experiments/_space_reader.py`) — the same predict-and-revise pattern, live.
- Pick the error gold on the reader's OWN output: the who-did-what / role gold already used by the role work (LitBank +
  QA-SRL), scored through the live `read()`. MIND the corpus-age confound (add a modern slice if reachable).

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
On real narrative through the LIVE `SituationReader.read()`, with the reader's capable flags ON:
- **PASS = BOTH gates.** (1) INFORMATIVE: live per-argument surprisal predicts the reader's OWN comprehension errors
  (who-did-what wrong) CI-separated over chance (AUC/point-biserial lower bound > 0.5), and a SHUFFLED-surprisal twin
  (same values permuted across arguments) LOSES CI-separated. (2) ACTIONABLE: gating ONE brain-faithful decision by the
  signal — surprisal-abstain (hold the highest-surprisal answers) OR surprisal-weighted predict-and-revise — beats the
  un-gated reader on a downstream comprehension metric CI-separated, with the info-free (random same-rate) twin NOT
  helping. Report CI half-width + null p95 beside every margin; precision-weight as the graded brain signature.
- **A rigorous NEGATIVE is a full PASS:** if the live signal is too weak to drive a decision (informative but not
  actionable, or ceiling'd), enumerate WHY — is it the grounded-space coarseness (the known ceiling), the isolation
  effect being modest, or the decision choice? Name it; that points the prediction-error program at the meaning/grounding
  lever or a different decision, and tells the owner the forward signal alone is not yet a live controller.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/`: compose `predictive_reader` (fit on QA-SRL triples via its `extract_triples`, then
  `surprisal`) over the reader's OWN event/argument stream produced by `SituationReader.read()`; score the INFORMATIVE
  gate (surprisal vs the reader's role errors) + the ACTIONABLE gate (one gated decision) + both twins from source. A
  scaffold-free witness recomputes every headline through the live read(). Fold an **AUDIT UPDATE** into
  `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. If it clears the bar, strategy lands the hdlab wire (Q111): a default-off flag on
  `SituationReader` that computes the surprisal signal and applies the one validated decision (byte-identical when off).
  This is the first live node of the prediction-error hierarchy.

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote `predictive_reader`'s ISOLATION numbers (QA-SRL +0.199 etc.) as a LIVE result — they are the inherited
  isolation baseline; this problem measures the signal computed through the live reader (a different population). No
  number crosses scorers/populations.
- 🚫 Do NOT re-wire the incremental parser as the role candidate source (a proven fidelity-error NEGATIVE) — this is the
  prediction SIGNAL driving a decision, not the parser's candidate set.
- 🚫 Do NOT build the whole 4-level prediction-error hierarchy — this is ONE decision + a positive control, deliberately.
  The other levels (n400_coherence_monitor / slot_attention_wm / gap_detector) are the follow-on program.

> ## ✅ SOLVER REVIEW (strategy, 2026-08-31) — EXCELLENT
> The forward-prediction organ (N400 thematic-fit surprisal) is validated LIVE through read() as an error-RISK FLAG (AUC
> 0.651 CI-sep over chance, shuffle twin loses) + a working ABSTAIN decision (+0.035 committed-accuracy CI-sep), generalizing
> to 19c narrative (AUC 0.624). The ambitious auto-revise decision is a rigorously DECOMPOSED negative: the decisive test
> shows the reader's wrong pick is no more similar to gold than a random competitor (0.221 vs 0.229) → the errors are
> STRUCTURAL (wrong entity), which is WHY every semantic/plausibility signal fails; the residual is parser-recall-bound (→
> the predictive parser, the named next lever). Brain-led via 4 drills (two dissociable streams: N400 thematic flag works,
> LIFG/P600 structural conflict is the parser's; surprisal is a risk flag not a verdict). Reverified 8/8 first-hand; 8
> controls with CI + null p95 on every margin. INTEGRATED: the one-line hdlab bug it flagged (frame_induction.is_passive_real
> IndexError) is FIXED; the predict_surprisal read-out flag is QUEUED (WIRING_MAP — needs an offline-fitted predictor asset +
> an additive EventRecord surprisal field; the first live node of the prediction-error hierarchy). Do NOT wire auto-revision
> (it fails). Flip-on default-off.
