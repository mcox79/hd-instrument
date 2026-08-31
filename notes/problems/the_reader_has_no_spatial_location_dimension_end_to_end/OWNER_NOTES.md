---
owner_verdict: DONE
---

════════════════════════════════════════════════════════════════════════════════════════════════════
SOLVER SUBMISSION — the_reader_has_no_spatial_location_dimension_end_to_end          STATUS: SOLVED (WIP → owner DONE)
hdlab/ UNTOUCHED (strategy lands the diff, Q111). Bar MET with power AND the wall crossed brain-faithfully;
the low absolute is bounded to a MEASURED cause (parser recall), every flattering explanation ruled out.
REVERIFY (one command rebuilds reader + gold + both floors + twin-null + distance curve + discriminator +
extension + the modern corpus-age control, all end-to-end through the live read(), FROM SOURCE):
  .venv/Scripts/python.exe verification/test_space_where_is_end_to_end_organ.py   -> ALL 13 CHECKS PASS
  .venv/Scripts/python.exe tools/problem_ledger.py --check                        -> malformed/incomplete: 0
════════════════════════════════════════════════════════════════════════════════════════════════════
ASKED: the reader has WHO/WHAT/WHEN/WHY but not WHERE. The tracking CORE (hdlab/location_register.py, Zwaan &
  Radvansky event-indexing SPACE) is promoted but validated ONLY on abstract motion events + CONSTRUCTION
  templates (exp_location_register_where_is_x_v1 = 1.0 on synthetic sentences via a standalone parser + a
  SUPPLIED alias dict). Drive it END-TO-END through SituationReader.read() from the reader's OWN parse + coref
  on REAL prose, answer "where is X at time T" CI-separated over floors with the info-free twin LOSING and the
  distance signature — or, if extraction is too weak, enumerate WHY (points SPACE at the parser, p2).

BRAIN METHOD (PINNED via 2 dispatched drills, not guessed): the reader's OWN in-substrate parse (pos_tagger +
  arc_parser UAS 0.79 + predicate_argument_frontend goal/source/path/direction — Talmy Source-Path-Goal +
  VerbNet + Goldberg + ATL place-typing) drives the PROMOTED tracker; mover = the coref-resolved AGENT cluster
  (person-gated — goal bias is animacy-modulated, Lakusta&Landau 2012). Drill 1: the brain runs NOISY-CHANNEL
  comprehension — parse as EVIDENCE fused with a situation-model PRIOR (persistence + revise-on-surprise;
  Levy/Gibson; hippocampal pattern-completion, Sinclair 2021), NOT parse-as-truth. NO spaCy/LLM at inference.

RESULT — bar MET end-to-end through the LIVE read(), 14 real LitBank passages, 24 character-timelines, n=606:
  * REGISTER_prior (parse-as-EVIDENCE+prior) where-is 0.177 vs last-mention-location 0.013 (+0.163 CI
    [+0.050,+0.291]) and vs abstain 0.000 (+0.177) — CI-separated over BOTH floors; info-free TWIN NULL (R=25)
    mean 0.068 p95 0.112 LOSES (prior clears p95). PRESENT-IN-SCENE 0.389 vs floor 0.071 (5.5x, the robust
    ToM-consumable query). DISTANCE curve = the Zwaan/Rinck persistence signature: last-mention collapses to
    0.003 at >=11 intervening sentences while the register HOLDS 0.197 (63x).
  * THE PRIOR IS WHAT MAKES IT A TRACKER (drill 1's discriminator, run): parse-as-TRUTH (0.111) sits AT the
    info-free null p95 (0.112) — statistically it isn't using state; the prior clears it. And swapping in a
    STRONGER general parser (spaCy, parse-as-truth) does NOT beat the in-substrate prior on exact-node
    (0.045 vs 0.177) — the lever is the PRIOR, not raw parse quality. → SPACE's ceiling is parser RECALL (p2).

THE WALL — CROSSED brain-faithfully (drill 2 → 3 extensions, can-fail-tested):
  Drill 2 pinned that the brain updates SPACE from the 3 constructions we dropped, gated by VERIDICALITY not
  clause position. Built REGISTER_prior_ext: (1) veridical EMBEDDED-clause routing ("no one saw them ARRIVE at
  the station" → update; "she SAID he had gone" → belief-world, skip — Kuperberg P600); (2) CAUSED-MOTION theme
  relocation ("brought us into the sitting-room" moves the OBJECT; agent co-moves only for accompanied-motion
  verbs — Goldberg); (3) expanded STATIVE locatives (Basic Locative Construction). Result: event-recall
  0.25→0.35, node-recall 0.125→0.20, PRECISION 0.135→0.168 (both up = real recovery), where-is 0.177→0.259,
  beating every floor CI-sep and its OWN null (0.135). (The +0.083 over minimal prior is directional, not
  CI-sep at n=606; the recall/precision lift is the evidence.)

WEAKNESS DRILL — the low 0.26, understood to the mechanism, flattering hypotheses REFUTED:
  * Error composition: FALSE_away 35% + missed-arrival 27% + node-confusion only 12% → the register is wrong
    because it never EXTRACTED the arrival, not because it confuses rooms.
  * REACHABILITY rules out a gold-granularity artifact: 0.260 on reachable gold == 0.259 overall (I checked
    because I hoped otherwise). PERSIST-last-known read-out (brain-faithful) recovers only +0.02 → FALSE_away is
    recall-rooted, not a read-out bug. So the ceiling is genuinely parser recall.
  * ABLATION: caused-motion-theme is LOAD-BEARING (+0.052 alone); embedded-routing HURTS alone (-0.009) but
    earns +0.025 in the full config; stative small. Ship all three; embedded is the one to watch.

CORPUS-AGE CONTROL (the brief's confound, gap FILLED): exp_space_where_is_modern_v1, 8 author-constructed
  modern passages (labeled synthetic; no modern narrative-with-movement corpus on shelf). Extraction recall
  0.444 / precision 0.529 — as good or BETTER than 19c (0.35/0.168): the extraction reads path off age-stable
  PREPOSITIONS, so modern vocabulary does NOT break it. Register 0.277 beats the null + abstain CI-sep,
  directional over last-mention (+0.128, not CI-sep at n=47). VERDICT: the LitBank result is NOT a dated-
  vocabulary artifact.

GOLD RELIABILITY + VET closed: 24-point re-adjudication against the raw text — 0 fabricated/wrong labels,
  ~27% contestable, and the contestable ones (name-generalizations, habitual, inferred) DEFLATE the register,
  not inflate it → the gold is conservative. Drill 2's open VET (is a moved THEME tracked as reliably as a
  self-mover?) CLOSED: 0.67 vs 0.36 — theme caught AT LEAST as reliably (caused-motion is parser-friendly).

CONTROLS: (1) info-free TWIN NULL (R=25, per-entity order destroyed, deterministic crc32) LOSES. (2) ABSTAIN
  floor = 0. (3) DISTANCE curve = persistence signature. (4) spaCy upper-bound (parser-swap doesn't help). (5)
  parse-as-truth-vs-prior discriminator. (6) reachability + persist probes (0.26 is real). (7) modern corpus-age
  control. (8) gold re-adjudication audit. (9) caused-vs-self recall split.

AUDIT UPDATE (fold into BRAIN_FOUNDATIONAL_AUDIT.md §2b): SPACE wired end-to-end + measured on real prose (the
  4th situation-model dimension after entities/time/causation); tracker/categorical-nodes/persistence PINNED
  and confirmed (distance curve). NEW PINNED (built + measured): noisy-channel = parse-as-EVIDENCE+PRIOR, not
  parse-as-truth (truth==null; spaCy doesn't help); embedded SPACE updates gated by VERIDICALITY (Kuperberg);
  caused-motion relocates the THEME (Goldberg); goal-bias is animacy-modulated (Lakusta&Landau 2012). Measured
  deviation: extraction recovers ~25→35% of true motion events on real prose — the SPACE ceiling is the
  LIKELIHOOD (parser) term.

PROPOSED hdlab CHANGE (Q111 — strategy lands): default-off `track_space` flag on SituationReader (byte-identical
  when off, the causation/time pattern) → sm.locations + where_is/present_in_scene; _read_location_register =
  promote experiments/_space_reader.py, DEFAULT to `prior_ext` mode (the best arm) + the persist-last-known
  read-out (+0.02, more brain-faithful); NO spaCy (in-substrate wins). Wire present_in_scene into the ToM
  consumer; update WIRING_MAP DEBT 2.

KEY REALIZATIONS: (1) the reader ALREADY extracts goal/source/path in-substrate (predicate_argument_frontend)
  — the faithful driver, no spaCy needed (and spaCy didn't help). (2) parse-as-truth failing to beat the twin
  null is the tell it isn't using state — only the prior makes ORDER matter. (3) present-in-scene, not exact
  node, is the robust brain-faithful read-out on noisy prose. (4) drill the wall → cross it: veridicality-gating
  let us read embedded clauses without importing reported noise. (5) DECOMPOSE the low number before defending
  or excusing it — the reachability check refuted my own hope that granularity was the cause, which is what made
  "the ceiling is parser recall" trustworthy.

FILES: experiments/{_space_reader,_space_reader_spacy,exp_space_where_is_end_to_end_v1,exp_space_where_is_modern_v1}.py;
  verification/test_space_where_is_end_to_end_organ.py (13/13); data/space_where_is_gold_v1/gold.jsonl (64
  change-points, quote-verified) + data/space_where_is_end_to_end_v1/metrics.json + data/space_where_is_modern_v1/;
  2 research drills. hdlab/ UNTOUCHED.

NEXT (follow-on PROBLEMS, out of solver scope): (1) p2 incremental predictive parser + belief-world channel for
  non-factive reports — the two levers to raise the recall ceiling; (2) the full prior×likelihood SPACE organ +
  per-passage region-containment tree ("is X in the house?"); (3) land the track_space wire + ToM present-in-
  scene. A 30-min deepening cron (ecacabb6) stays live until owner_verdict: DONE.

TLDR: A reader keeps a map of where everyone is; ours was blind to WHERE. I wired the map-keeper to the reader's
  own understanding of each sentence and, on 14 real novels, it answers "where is X" ~14x better than the dumb
  baselines, holds a character's location across long stretches where the baseline drifts away instantly, and a
  scrambled version does far worse. It catches about a third of the moves — the parser drops the hard sentences —
  and I PROVED that's the cause (not a scoring quirk) by ruling out every flattering explanation. I asked how the
  brain copes with a noisy parser (it leans on memory, doesn't trust the parse), built a first version of that
  layer and showed it's what makes the tracker actually track. I taught it three move-types the brain catches and
  we were dropping (getting more right without more wrong), showed a stronger off-the-shelf parser does NOT help
  (so the fix is the brain's predict-and-revise reading, not a fancier parser), confirmed it does NOT get worse on
  modern English, and audited the answer key (no wrong entries; its judgment calls count against us).
  QUESTIONS: none. NEXT: hand to strategy to land the default-off WHERE dimension; the parser and the fuller
  memory layer are the two levers to raise the ceiling, both filed as their own problems.
════════════════════════════════════════════════════════════════════════════════════════════════════
