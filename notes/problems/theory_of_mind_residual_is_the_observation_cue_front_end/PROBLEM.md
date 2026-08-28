---
priority:
review: EXCELLENT
review_text: "The ToM residual — reading 'did agent A witness the change?' from prose — is SOLVED by a brain-faithful per-agent PERCEPTUAL-ACCESS REGISTRATION LEDGER that replaces the landed lexical keyword extractor. Re-verified 4/4 witnesses FIRST-HAND (ledger 6/6, occlusion 6/6, sequential 4/4, testimony 3/3). Cue accuracy on the corpus-grounded gold: ledger 0.992 [0.980,1.000] vs the LANDED lexical extractor recomputed per-gold 0.500 [0.439,0.561], CI-separated (info-free twin 0.500 loses; majority 0.500); END-TO-END through the landed belief_partition 0.992 vs lexical 0.500 vs oracle 1.000, past the 0.821 residual. Mechanism PINNED (Butterfill&Apperly registration; Zwaan event-indexing SPACE; Talmy PATH-in-the-satellite-not-the-verb; Harris&Koenig testimony): a STICKY per-agent ledger, false belief = the ledger STALE vs reality (maps exactly onto the landed believed_location gate). Deep beyond the bar: per-modality OCCLUSION field (6/6, coarse single-gate fails 2/6), SEQUENTIAL registration (4/4: last-registered, motion-persistence, ignorance≠false-belief, multi-agent divergence), TESTIMONY-with-reliability (3/3: believed-lie→false-matching-lie, distrust→discount), and a DISTANCE experiment PROVING the intact-window spatial-chance is a WINDOWING artifact (full-text spatial route 0.99 at K=0..20 vs a 3-sentence window →0.00). Scrupulously honest scope (two-gold frame-vs-intact split named, intact-scene scarcity + verb-POLYSEMY + coref-cap walls flagged precisely, exact 0.992 gold-quality-bounded ~90% label precision but the 0.98-vs-0.50 gap dwarfs it). hdlab landing QUEUED (careful port — promote perceptual_access + extend belief_partition to a sequence ledger; needs wiring to the coref/situation-model organs to drop the spaCy-parse proxy)."
---

> ## ✅ SOLVER REVIEW — INTEGRATED 2026-08-28 (strategy session; grade EXCELLENT)
> **Re-verified FIRST-HAND** — all 4 witnesses ran + PASS (suspected my own checker, ran them):
> `test_perceptual_access_ledger.py` **6/6**, `test_perceptual_field_occlusion.py` **6/6**,
> `test_sequential_registration.py` **4/4**, `test_testimony_reliability.py` **3/3**.
> **Result (bar MET, and exceeded):** the observation-cue front-end is a per-agent **perceptual-access registration
> ledger** (`observed = RULE0 explicit-narrator-statement, else RULE1 co-present-&-in-perceptual-field, OR RULE2
> informed`). Cue accuracy on the CORPUS-GROUNDED gold: **ledger 0.992 [0.980,1.000] vs the LANDED lexical extractor
> 0.500 [0.439,0.561]** (CI-separated by ~0.44), over majority 0.500 and the info-free twin 0.500 (both lose);
> HELD-OUT 0.985 on 5 unseen phrasing draws (n=1230) rules out overfit. **END-TO-END through the LANDED
> `belief_partition`: ledger 0.992 vs lexical 0.500 vs oracle 1.000 — past the 0.821 in-situ residual.**
> **Argument audit (not just arithmetic):** the lexical baseline is the *landed* extractor recomputed per-gold — it
> collapses 0.808 (its own authored phrasings) → 0.500 (chance) on diverse real corpus prose, which **is** the
> residual the brief targets. Per-class dissociation localizes the entire win to NOT-OBSERVED classes (depart 1.000,
> occlude 0.980 vs lexical 0.000) → it genuinely READS the cue, not a relabeled prior. The intact-window spatial
> chance (0.52) is **proven a WINDOWING artifact**, not a mechanism failure, by the distance experiment (the
> full-text spatial route holds 0.99 across K=0..20 filler sentences; a 3-sentence window collapses to 0.00) —
> validating Zwaan's incremental-situation-model claim. The solver is scrupulously honest: two complementary golds
> (frame-gold isolates the SPATIAL mechanism; intact-gold gives realism where the win is RULE 0's explicit-marker
> coverage), and it explicitly **bars** quoting the intact 0.930 as a spatial-inference result. Beyond the bar it
> built + witnessed a per-modality OCCLUSION field (the FANToM/Ullman wall — vision needs light+LOS+not-closed-opaque
> +attending+awake, audition penetrates dark but needs sound, touch needs contact; 6/6 where a coarse gate fails
> 2/6), SEQUENTIAL registration over event chains (last-registered-not-final; motion-persistence; ignorance=None as a
> first-class state ≠ false belief; multi-agent divergence — 4/4), and TESTIMONY with reliability (believed-lie →
> false belief matching the lie; distrusted source discounted — 3/3). The sequence exposed + fixed two real bugs a
> single move hides (occlusion window read one sentence PAST the event; RULE 0 leaked a move-1 marker onto move 2 —
> markers are EVENT-LOCAL). **Brain-fidelity:** the whole mechanism is PINNED (Butterfill & Apperly 2013 registration;
> Zwaan & Radvansky event-indexing SPACE; Talmy 1985 PATH-in-the-satellite; Harris & Koenig 2006 testimony) — "PATH
> lives in the satellite not the verb" avoids the verb-whitelist trap the brain doesn't have, and "false belief = the
> ledger being stale" maps exactly onto the landed `believed_location(observed, initial, final)` gate.
> **Honest deflations preserved:** intact false-belief SCENES are too sparse to mine at scale (verb POLYSEMY + idiom
> bound automatic mining — named precisely, the deliverable for bar #4); label precision ~90%; coref is a simple
> proxy (multi-character prose is coref-capped ~0.65); first-order belief only; the exact 0.992 is gold-quality-bounded.
> **AUDIT UPDATE folded (§2b).**
> **hdlab landing QUEUED (Q111 — a careful multi-module port, NOT this commit; proven-ready, witnesses are the gates):**
> promote `experiments/perceptual_access_ledger.py` → `hdlab/perceptual_access.py` (default-off island like
> `belief_partition`); wire `observed()` → `belief_partition.form_belief(...)` **over the FULL running situation model,
> not windows**; extend `belief_partition` from the binary gate to a SEQUENCE registration ledger + IGNORANCE(None) +
> asserted-location testimony. **⚠️ Landing prerequisite:** the module currently uses an internal **spaCy parse proxy**
> for mention/event localisation — promoting it as-is would give hdlab a spaCy dependency (the exact remote-unsafe
> pattern just fixed in `closed_class_lexicon`). So the landing should CONSUME the substrate's coref / situation-model
> organs (the solver's own recommendation) rather than re-parsing — which is why it is a careful port, not a drop-in.
> **Adjacent gaps the solver surfaced (candidate future briefs, ranked): (1) NO SPACE dimension in the situation
> model — a genuinely MISSING, high-leverage organ (per-entity location-over-time register); (2) coref ~0.65 on real
> narrative; (3) verb-sense/POLYSEMY glass-box WSD; (4) object-state-change event extraction; (5) wire
> belief_partition into the live reader + add belief-questions to the reading task (strategy's VALUE-gating adjacency).**

# PROBLEM: theory-of-mind's belief mechanism is LANDED and perfect with oracle observation (1.000), but the end-to-end drops to 0.821 because reading "did this character WITNESS the change?" from prose is unsolved — build the brain-faithful observation-cue front-end (perceptual access / "seeing = knowing"), validate it beats the lexical baseline CI-separated on a CORPUS-mined false-belief gold, twin losing

**slug:** `theory_of_mind_residual_is_the_observation_cue_front_end` — **opened:** 2026-08-28 by the strategy session (owner
MUSED a dedicated ToM re-eval after p1 landed). **status:** OPEN — a MECHANISM + DATA problem. You build + validate in
`experiments/`; strategy lands any hdlab change (Q111). Builds on the LANDED `hdlab/belief_partition.py`.

> **PRIORITY NOTE (the call is the strategy session's):** filed at `5`, below the learner (p2) + foraging (p3) + the
> phase-diagram (p4). This STRENGTHENS an already-integrated result (theory-of-mind), so it is a refinement, not a new
> capability — but it targets the one measured residual (the observation front-end) + the honest corpus-generality gap. Re-rank per the owner.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

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
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill — do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across — never a ceiling.
> Each fire: implement → test (can-fail, strongest real floor, info-free twin LOSING) → iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS — but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **📖 REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch (Theory of Mind / mentalizing; the
> front-end); inherit its PINNED/INVENTED verdicts; put a short **AUDIT UPDATE** in your submission.

## 1. THE PROBLEM IN PLAIN LANGUAGE

We just landed a real Theory-of-Mind ability: the reader tracks what each character BELIEVES separately from what's actually
true, and gets false-belief questions perfect (100%) — WHEN it's told who saw what. But reading "**did this character
actually WITNESS the change?**" from ordinary prose is unsolved: a crude keyword matcher gets it right only ~81% of the
time, which drags the whole ability down from 100% to 82%. And the test stories were hand-written by the solver, so we
haven't shown it works on REAL story passages. Build the brain's way of deciding "did the character see it?" — perceptual
access, the "seeing-leads-to-knowing" principle young children use — and prove it on real, corpus-mined false-belief passages.

## 2. WHY THIS ONE

It is the ONE measured residual of an otherwise-perfect, already-landed organ (`hdlab/belief_partition.py`), and it closes
the honest corpus-generality gap the solver flagged. It is also the SAME front-end class we keep hitting ("the front-end is
the binding constraint") — reading a specific relation (here: did agent A perceive event E?) from arbitrary text — so a win
here generalises the front-end story. It does NOT re-open the belief mechanism (that is solved + landed).

## 3. HOW THE BRAIN DOES THIS (frame — PINNED vs OUR-INVENTION)

- **PINNED — perceptual access → knowledge ("seeing is knowing").** Children track knowledge via PERCEPTUAL ACCESS: an
  agent knows a fact iff it perceived (or was informed of) it (the developmental ToM literature; the false-belief task
  turns on exactly this). The observation cue = "was agent A perceptually present / informed at the moment of the change?".
  This is the input the landed `belief_partition` gate consumes (`believed_location(observed, initial, final)`).
- **PINNED — it is a discourse/situation-model inference, not a keyword.** "While she was out", "he had gone to the field",
  "asleep", "watched from the doorway", "was told" — the cue is carried by PRESENCE / ABSENCE / INFORMED state in the
  event structure, which is exactly what the situation model + coreference + the entity register already track (agent
  location vs event location over time). Build the observation cue AS a read of the situation model, not a regex.
- **OUR-INVENTION-UNDER-TEST:** the exact extractor. The landed lexical version (0.808) is the STAND-IN to beat. COPY the
  computation (perceptual-access inference over the event/entity structure), SWEEP the parameters.

## 4. MEASURED vs INFERRED
- **MEASURED (the integrated ToM work, `hdlab/belief_partition.py`):** with ORACLE observation, belief-acc 1.000; with the
  lexical text extractor (0.808 cue accuracy), end-to-end 0.821 — the FULL_TOM(oracle) − LIVE gap localises the residual to
  the observation cue. The belief mechanism, controls, and dissociations are DONE (do not redo).
- **INFERRED (to test):** a brain-faithful observation-cue extractor (perceptual-access inference over the situation/entity
  structure) beats the 0.808 lexical baseline CI-sep AND lifts end-to-end toward the oracle 1.000, on a CORPUS-mined (not
  authored) false-belief gold. UNPROVEN — could be null (a valid PASS: the residual is elsewhere / the cue is genuinely hard).

## 5. ALREADY TRIED / DO NOT RE-RUN
- The per-agent belief partition IS solved + LANDED (`belief_partition.py`) — build the observation FRONT-END that feeds it,
  do NOT rebuild the belief mechanism, the controls, or the dissociations.
- The lexical extractor (0.808) is the BASELINE to beat, not a result to reproduce.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- Reverify the belief organ: `.venv/Scripts/python.exe verification/test_belief_partition_organ.py` (+ the integration
  witness `verification/test_theory_of_mind_realtext.py`).
- Read `hdlab/belief_partition.py` (the gate consuming `observed`) + `experiments/exp_theory_of_mind_realtext_v1.py`
  (`extract_observed_from_text`, the 0.808 lexical baseline) + the situation/entity organs (`situation_model_accumulate`,
  `salience_binder`, coref) you should read the cue FROM.
- Read `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (the ToM entry) — the residual is named there.

## 7. THE BAR
PASSES only with ALL of:
1. **The observation-cue extractor beats the 0.808 lexical baseline CI-separated** on cue accuracy (did agent A witness
   event E?), on a **CORPUS-mined false-belief gold** (real story passages, not authored) — recompute the strongest real
   floor; info-free twin (shuffled presence/absence signal) LOSES CI-sep; report CI half-width + null p95.
2. **Lifts the END-TO-END belief accuracy** (feeding the LANDED `belief_partition`) toward the oracle 1.000, CI-separated
   over the lexical-cue end-to-end 0.821 — the whole point is the composed lift, not the cue in isolation.
3. **Brain-faithful mechanism:** the cue is a PERCEPTUAL-ACCESS inference read from the event/entity/situation structure
   (presence/absence/informed at the moment of change), NOT a keyword list. State the operation. COPY the computation, SWEEP params.
4. **A corpus-mined false-belief gold exists + is verified** (the honest corpus-generality gap): real passages where an agent
   holds a belief the world has since falsified, with the observation state derivable from the text; report how it was mined + verified.
A rigorous NEGATIVE (a faithfully-built perceptual-access extractor does NOT beat the lexical baseline on real corpus text) is
a FULL PASS — localising why (the cue needs coref the reader lacks / the corpus is too sparse / it needs the incremental parser).

## 8. FILES AND ENTRY POINTS
- Organ + baseline: `hdlab/belief_partition.py`, `experiments/exp_theory_of_mind_realtext_v1.py` (`extract_observed_from_text`).
- Read the cue FROM: `hdlab/situation_model_accumulate.py`, `hdlab/salience_binder.py`, the coref organs.
- Gold source: mine real false-belief passages (LitBank / Gutenberg narrative; the situation-model corpora on disk).
- **Route heavy corpus-scale runs to the REMOTE GPU box** (`tools/queue_add.py`).
- Audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (ToM).

## DO NOT QUOTE / DO NOT REDO
The belief mechanism (1.000 with oracle observation), its controls, and its dissociations are DONE + LANDED — do not redo
them. The lexical extractor (0.808) is the BASELINE. Strategy owns the hdlab landing — you propose the diff (the observation
front-end + a corpus gold), you do not write `hdlab/`.
