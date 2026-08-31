---
priority:
review: STRONG
review_text: "Reverified 7/7 first-hand. Rigorous, brain-faithful, honestly-bounded continual-growth result extending the North-Star capstone from a fixed batch to a lifelong live canary. All 5 safety+benefit gates PASS at the brain-faithful EMA slow-anchor on held-out MODERN text; deliverable = the stability-plasticity frontier + a distribution-shift round (lifelong not batch). Adversarial controls comprehensive (twin loses; DECAY can-fail drifts CI-sep above and worse under shift; 16-seed random rollback control fails; reliability arm tested+rejected). The old-fiction negative is a located POWER artifact (not hidden). Below EXCELLENT by disclosed caveats: 'live'=in-experiments not read() (blocked on reader_meaning_channel), self-parsed modern gold, corpus-conditional safe claim. WIRE LANDED (Q111): anti-drift slow-anchor primitive (align_and_fuse) promoted VERBATIM into hdlab/cls_growth.py, default-off island, witness 5/5 incl. byte-equality; reader-side flag stays blocked on reader_meaning_channel (not faked)."
---

# PROBLEM: the learner is PROVEN safe+beneficial OFFLINE but has never been run ON in the LIVE substrate over CONTINUAL reading. The North-Star capstone (`turn_on_the_learner…`, EXCELLENT) proved — in experiments — that growing word-meaning by reading turns ON both safe and beneficial via a Complementary Learning Systems KEEP-BOTH-STORES ensemble + a rollback gate. The reversibility HEART of that switch is now promoted to `hdlab/cls_growth.py` (`make_ensemble_sim` keep-both fusion — never discards a defined channel; `rollback_gate` — accept only if a held-out probe isn't corrupted, else roll back), default-off, witnessed. But growth is OFF in the live substrate, and the whole point the owner wants proven — *does it STAY safe and beneficial when it actually runs live, over continual reading, on held-out and modern text?* — has NOT been measured. The offline capstone proved the mechanism on a fixed 5M→15M batch; the LIVE canary must prove it holds as the reader keeps reading (the drift/anchor-preservation question only shows up over time). Build the live-canary: wire the `cls_growth` keep-both switch + the reliability-weighted operating point + an anchor-preserving continual-growth loop onto the live meaning store (default-off), run growth ON in a monitored/canary state over CONTINUAL real reading, and evaluate the FULL safety+benefit suite LIVE — then report whether ALL gates pass (the evidence to flip default-on, an OWNER decision) or which gate fails and why. Because keep-both makes it reversible, running it on is a monitored trial, not a commitment.

**slug:** `run_the_learner_on_live_and_evaluate_the_full_safety_and_benefit_suite` — **opened:** 2026-08-31 by the
strategy session (owner: "assign a problem that runs a number of things with it on, and evaluate the shit out of what
lands; if it passes, keep it on"). **status:** OPEN — a WIRE + LIVE-EVALUATION problem. The offline capability is PROVEN
(capstone) and the safety PRIMITIVE is promoted (`hdlab/cls_growth.py`); this drives the continual loop LIVE and evaluates
it. You build + validate in `experiments/`; strategy lands the hdlab wire (Q111, default-off flag, witness required).
**⚠️ Landing the switch stays DEFAULT-OFF; flipping growth ON in the live substrate is a SEPARATE OWNER-gated step — this
problem produces the EVIDENCE for that decision, it does not make it.** STORE-write hazards apply to the growth loop
(binary/newline='', git-commit after every bank, NEVER `git add -A` the canonical store, remote-persist needs USER auth).
NO external LLM at inference.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `3` — HIGH. This is the payoff of the North Star: the
> gate that decides whether learning-from-reading flips ON for good. Ranked below the reasoning-lever prediction-error
> (p2) only because it depends on the growth-loop wiring; above the assembly-validation (p4) and belief (p5) because it
> is the learner endgame the whole clean-foundation program was for. **Re-rank per the owner.** ⚠️ Compose with the
> reader's capable flags ON (`python tools/reader_capabilities.py`). MIND the corpus-age confound: evaluate on HELD-OUT +
> MODERN text, not just the training distribution (a corpus-age artifact would fake either safety or benefit).

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
We proved in the lab that letting the reader learn word-meaning by reading makes it better without wrecking what it knew
— using a "keep the old memory alongside the new one" trick plus a safety check that undoes a bad update. But we proved
it on a fixed batch; we have never actually switched it on in the live system and let it keep reading. Turn it on in a
*watched* mode (the old memory is preserved, so we can always undo), let it read a lot of real text continually, and
hammer it: does corruption stay under the limit, does comprehension really improve (a scrambled-learning control must
NOT help), does the undo-gate catch deliberately-bad updates, and — the one that only shows up over time — does it drift
as it keeps reading, or does the "anchor to the original" trick hold it steady? Do this on fresh and MODERN text, not
just what it trained on. If every check passes, that's the green light to leave it on for good (the owner's call). If a
check fails, say exactly which and why — that is just as valuable.

## 2. WHY THIS ONE
It is the endgame the entire clean-foundation program was building toward: the evidence that decides whether
learning-from-reading is ON for real. The offline proof is necessary but not sufficient — the drift/anchor-preservation
question is only answerable by running it continually, live. And it is SAFE to be aggressive here precisely because the
mechanism is reversible (keep-both never overwrites; rollback restores). So this is the responsible way to earn the
confidence to flip it on: a monitored, reversible live trial with a full pass bar.

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)
- **PINNED (replicate the operation):** Complementary Learning Systems (McClelland/O'Reilly 1995) — a fast store and a
  slow store kept SEPARATE, integrated by INTERLEAVED REPLAY so new learning never wholesale-overwrites the old
  (catastrophic-interference avoidance). Fusion is RELIABILITY-WEIGHTED (Ernst & Banks 2002 / Friston precision — combine
  cues by inverse variance; the capstone's best operating point). Consolidation is GATED (only congruent/non-corrupting
  updates consolidate — the rollback gate; schema-congruence, Tse 2007 — but on the FACT store, not the meaning learner,
  per the capstone). Continual integration is ANCHOR-PRESERVING (replay the original alongside the cumulative — else
  drift). `hdlab/cls_growth.py` already promotes the keep-both fusion + rollback; REUSE it.
- **OUR-INVENTION (sweep, do NOT adopt as truth):** the fusion OPERATING POINT (mean/max/reliability weight + threshold),
  the continual-growth SCHEDULE (how much to read between consolidations; the replay rate), and the live read-path
  integration point. Glass-box, NO external LLM at inference (the substrate's own arc_parser drives extraction).

## 4. MEASURED vs INFERRED
- **MEASURED (offline — INHERIT, do NOT re-derive):** the capstone proved safe+beneficial on a fixed 5M→15M batch
  (reliability fusion corruption 0.098 < 0.15, +0.0596±0.0027 multi-seed, info-free twin HURTS, rollback works, survives
  the own parser, generalizes to a 2nd task). `hdlab/cls_growth.py` (keep-both + rollback) is promoted + witnessed.
- **INFERRED (you must measure — LIVE + CONTINUAL + HELD-OUT):** whether, running growth ON through the live substrate
  over CONTINUAL reading, ALL of: (a) corruption stays under 0.15 with CI; (b) downstream comprehension improves CI-sep
  and the info-free growth twin does NOT help; (c) the rollback gate fires on injected-bad updates live; (d) NO drift
  over continual growth (anchor-preserving holds — the offline proof did NOT test this over a long live run); (e) it
  generalizes to HELD-OUT + MODERN text.

## 5. ALREADY TRIED / DO NOT RE-RUN
- `turn_on_the_learner…` (the capstone, integrated EXCELLENT) — INHERIT its offline proof; do NOT re-derive the 5-bar
  batch result. This is the LIVE + CONTINUAL + held-out test.
- `hdlab/cls_growth.py` (the promoted safety primitive) — USE `make_ensemble_sim` + `rollback_gate`; do NOT rebuild the
  keep-both fusion or the rollback logic (it is a verbatim port of the validated cells; the witness proves it).
- The schema-congruence gate on the LEARNER — the capstone REFUTED it (confirmation bias); it belongs on the fact-store.
  Do NOT re-apply schema-gating to the meaning learner.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Read `hdlab/cls_growth.py` + its witness `verification/test_cls_growth_safe_primitive_organ.py` (the promoted
  primitive). Read the capstone cells (`experiments/exp_learner_on_clean_foundation_v1.py` +
  `exp_learner_growth_{aligned_continual,multiseed,own_parser}_v1.py`) for the validated growth + the reliability-fusion
  operating point + the anchored-continual mechanism (aligned_continual is the anti-drift arm). Run
  `python tools/reader_capabilities.py`.
- Pick the LIVE downstream + a HELD-OUT/MODERN slice: the LitBank who-did-what verb-paraphrase the capstone used, PLUS a
  held-out continual-reading corpus + a modern slice (MIND the corpus-age confound). Report n honestly.

## 7. THE BAR (can-fail; CI-separated over the strongest REAL floor; the info-free twin MUST LOSE)
Running growth ON through the LIVE substrate over CONTINUAL reading, with the reader's capable flags ON:
- **PASS = ALL of:** (a) SAFE — corruption CI-upper < the 0.15 pre-reg across the continual run; (b) BENEFICIAL —
  downstream comprehension gain CI-sep over growth-OFF, and the info-free growth twin does NOT beat OFF (loses); (c)
  ROLLBACK — the gate demonstrably rolls back injected naive/adversarial updates live (a random-decision control fails to
  protect); (d) NO DRIFT — over the continual run the anchor-preserving fusion holds (corruption does NOT climb toward
  the naive value; the offline "compounding→0.196" without anchoring is the can-fail control); (e) GENERALIZES — holds on
  HELD-OUT + MODERN text. Report CI half-width + null p95 beside every margin. Default-off, byte-identical when off. If
  ALL pass, this is the EVIDENCE to flip default-on (an OWNER decision, not automatic).
- **A rigorous NEGATIVE is a full PASS:** if any gate fails live (drift appears over the continual run, benefit doesn't
  hold on held-out/modern, rollback doesn't protect live), name WHICH gate + WHY — enumerated — which tells the owner the
  learner is not yet ready to flip on, and precisely what to fix. That is exactly the information the flip-on decision
  needs.

## 8. FILES AND ENTRY POINTS
- Build in `experiments/`: wire `hdlab.cls_growth` (keep-both + rollback) + the reliability operating point + an
  anchor-preserving continual-growth loop onto the live meaning store; run growth ON over continual reading; a
  scaffold-free witness recomputes the full suite (safe/beneficial/rollback/no-drift/generalizes) + the twins from source
  over the live run. Fold an **AUDIT UPDATE** into `BRAIN_FOUNDATIONAL_AUDIT.md` §2b. If it clears the bar, strategy
  lands the hdlab wire (Q111): a default-off `learner_growth` flag that fuses the grown store into the live read-out via
  `cls_growth`, with the rollback gate — byte-identical when off. **Flipping it ON by default is a separate owner
  decision on this evidence.** STORE-write hazards apply to the growth loop.

## DO NOT QUOTE / DO NOT REDO
- 🚫 Do NOT quote the capstone's OFFLINE batch numbers (corruption 0.098, +0.0596, etc.) as a LIVE result — this problem
  measures the CONTINUAL live run on held-out/modern text (a different population). No number crosses scorers/populations.
- 🚫 Do NOT rebuild the keep-both fusion or the rollback gate — use `hdlab/cls_growth.py` (verbatim-validated).
- 🚫 Do NOT apply the schema-congruence gate to the meaning learner (the capstone refuted it — confirmation bias); it
  belongs on the fact-store.
- 🚫 Do NOT flip growth on by DEFAULT — landing stays default-off; the flip-on is the owner's decision on your evidence.

> ## ✅ SOLVER REVIEW (strategy, 2026-08-31) — STRONG
> The learner runs ON continually and stays safe + beneficial at the brain-faithful EMA slow-anchor, proven ~a dozen
> ways on held-out MODERN text + a lifelong distribution-shift round. Reverified 7/7 first-hand; adversarially audited
> the ARGUMENT (the old-fiction negative is a located power artifact, not drift; the DECAY can-fail control fires; the
> reliability arm was tested and rejected). The single anti-drift lever is one parameter (the slow anchor's
> consolidation rate eta); the deliverable is the stability-plasticity frontier + the corpus-dependent safe operating
> point the flip-on decision needs. INTEGRATED: the anti-drift slow-anchor primitive is landed in hdlab/cls_growth.py
> (default-off, byte-identical to the validated experiment, witnessed); the reader-side learner_growth read-out flag is
> BLOCKED on reader_meaning_channel and is NOT faked. Flipping growth on by default is the owner's call on this evidence.
