# OVERNIGHT PLAN — 2026-09-12 → 13 (owner asleep; autoloop ARMED; owner direction: "make the top of the chain as BF as possible, and fix all downstream 1 at a time")

**Operating rules for every continuation:** SHORT runs (< 10 min) go to RUNNER agents (`hdi_exp_dev`, model haiku); LONG runs (boards, 20-60 min) are launched as ONE chained background Bash job owned by the main session (foreground call -> auto-moved to background -> completion notification) because runner-held long jobs have died repeatedly when the agent's tool call/turn ended (00:18, 00:50 tonight); never poll/wait in the main thread;
commits PATH-LIMITED, never push; never edit `preregs/**` / `arm_key*`; every landed change gets a witness + a ledger line; a
downstream dip after a BF upstream is a CONSUMER TO REPAIR, never a reason to revert the BF rung; one decisive config per run.
Live BF configuration = `HDLAB_TAG_SOURCE=counts` (default) + `HDLAB_HEADS_SOURCE=attachment_arm` (the target default once the
board arms read the reader's parse). Baseline board (perceptron + supervised parser) 0.6395 for reference only.

## Phase 0 — finish the open integrations (owner-DONE)  [status: DONE 23:45]
- [x] pri-13 semantic hub: `hdlab/semantic_hub.py` + asset + `tools/build_semantic_hub_asset.py` + witness 6/6 → commit (+ the
      solver's 3 files routed through get_output_dir), registry BF_SPIRIT, INTEGRATION_LEDGER row (PARTIAL: representation landed,
      read-time fusion kept, readers not repointed), §2b audit note, INTEGRATED mark.
- [x] pri-10 causal store (REFUTED): commit the named files (get_output_dir-routed), INTEGRATION_LEDGER row + manifest (AS-DURABLE-
      NEGATIVE: store as necessity prior; the +0.139 headline = density artifact → retired claim), INTEGRATED mark; follow-on filed:
      `sm.causal_direction` default-off read + `board_causal_direction_dimension` (density-matched twin + reverse control).

## Phase 1 — TOP OF THE CHAIN, BF, one rung at a time
1a TOKENS — enumerate the live tokenizer path (`situation_reader` → regex); confirm no nltk/spaCy; record in SIGNAL_FLOW_MAP §0.
1b CATEGORIES (live organ = `hdlab/lexical_categories`, 0.912):
   - graded hand-off to heads: `attachment_arm.arc_scores_graded(toks, tag_posterior)` = mixture over the top-2 categories of
     uncertain tokens (P(top) < 0.8); measure UAS on UD-EWT test 700: gold / hard-predicted / graded-predicted (runner).
   - route the board arms' PRIVATE taggers (`causation_typing._frontend`, `exp_board_*` `PosTagger.load`) through ONE category
     source (the reader's switch) so the BF tagger reaches every board dimension; A/B.
   - acquisition arm: `LexicalCategories.accrue` over (word, induced class) from the k=68 asset → the organ's counts from READING;
     hand-off test via `build_attachment_validities --categories` (pri-15's solver owns the inventory; this is the organ's arm).
1c HEADS (live organ = `hdlab/attachment_arm`, 0.556; self-grown plausibility): route the who-did-what / coref board arms through
   `situation_reader._cached_parse_heads` (+ head posterior) so `HDLAB_HEADS_SOURCE` reaches them; copular convention in the
   convention layer (AUX → the predicate content word; the state dim residual); rebuild asset; measure per relation.
1d ROLES (BF): re-measure the 596-item decision + role probe on the BF chain; graded hand-off already landed.

## Phase 2 — DOWNSTREAM, one consumer at a time (board A/B after each; runner)
state (0.656 under BF heads; residual = heads) → who_did_what_patient/agent (after 1c routing) → coref/common-noun (if affected by
tags) → affect / causal / temporal arms that read tags → the affected-entity chain (state register, fusion rule).

## Phase 3 — MINE the last 20–30 solved problems for upstream work already proven (owner 23:35)
Scan `notes/problems/*/SOLVED.md` sections "UPSTREAM", "Full-stack upstream", "PROPOSED hdlab", "SUBSTRATE INCORPORATION MANIFEST"
for INCORPORATE items not yet folded (check INTEGRATION_LEDGER + `INTEGRATED_BY_STRATEGY` marks); list them in
`notes/UPSTREAM_FOLD_QUEUE_2026-09-13.md` ranked top-down by chain position; fold the ready ones one at a time with witnesses.

## Phase 4 — bookkeeping at milestones
ledger / STATUS / SCORECARD / BRAIN_MATH_REFERENCE / owner updates (significant only); delta sync to the desktop when the tar stream
finishes (`bash /c/AI/hd-instrument_desktop_2026-09-12/delta_sync.sh` via a runner; verify on the desktop).

## Log (append one line per completed item; newest last)
- 23:40 plan written; board A/B (counts; counts+attarm) running on a runner; transfer ~205/212 GB.
- 23:45 Phase 0 done: pri-13 hub organ landed (PARTIAL; readers not repointed); pri-10 recorded as durable negative (+0.139 retired); both committed.
- 23:05 1b: graded category hand-off landed + measured (gold 0.5562 / hard 0.5340 / graded 0.5379); ONE shared frontend `hdlab/frontend.py` landed and the patient/agent/state/causation arms shimmed onto it (the switches now reach the board); self-test on a runner; post-routing boards queued after the running pair.
- 23:15 transfer stream to the desktop FINISHED (pipe exit 0, 18:03Z->03:27Z = 14:03->23:27 local); delta sync + desktop verify on a runner. Copular clause convention added to the attachment arm (decode-time; witness 15/15); state-dim + per-relation measurement on a runner. Board self-tests PASS under default and fully-BF switches after the shared-frontend routing. Fold queue written (13 items; #4 = unreconciled second heads-rung organ from the pri-2 solver: reading-learned EM scorer + constructions, beats supervised OOD on GUM +0.0235).
- 23:25 1c: copular convention landed (state 0.6587 CI-sep under BF heads); heads-rung reconciliation: the arm subsumes the pri-2 reading-learned scorer; its Hindle-Rooth PP cue FOLDED into the arm ('pp' cue; association grown treebank-free) -- asset rebuild + per-relation on a runner. Board 'counts' (reader-only tagger switch, pre-routing) finished; counts+attarm running.
- 23:35 1b acquisition arm: tools/build_lexical_categories_from_reading.py (category organ counts over the induced classes from raw reading; 20k smoke 0.704 agreement, unknown words handled); 1M-line build + agreement + heads hand-off on a runner. Reader-only tagger board recorded (0.6385; only STATE moved).
- 00:05 1b acquisition arm MEASURED: reading-acquired category organ 0.7242 agreement (closed classes ~0 = pri-15 target); fully reading-learned chain UAS 0.4649 -> 0.4922. Desktop state re-sync verified (26,615 session files). PP-cue rebuild in its last round.
- 00:15 PP cue full rebuild: UAS 0.5583 -> 0.5706, nmod 0.185 -> 0.346 -- asset PROMOTED to live (witness 15/15). Pri-17 effectively delivered through the fold; pri-16 (sibling) remains parked.
- 01:05 post-routing boards C (counts reaching every arm) + D (fully BF chain, PP asset) relaunched as ONE session-owned background job after the runner-held pair died silently; module-import launcher; completion notification expected ~02:15.
- 01:50 FIRST COMPLETE fully-BF board (runner's relaunched B, post-routing): AGG 0.6222; flips = patient 0.729 (-0.09), agent 0.821 (-0.01), state 0.659 (-0.17, CI-sep); coref/wic/salience identical. Phase 2 starts with the PATIENT arm (graded head hand-off into its role read).
- 02:50 Phase 2 #1 (patient arm graded hand-off) = NULL (0.735 hard vs 0.732 graded, n=347): the patient loss is the heads rung's obj attachment (upstream). Next: agent arm once board C separates tagger vs heads; state = heads rung copular predicate.
- 02:55 Phase 2 #2 (agent arm graded category read) WORKS: 0.8209 -> 0.8357 (pre-BF 0.832 recovered). Queued: the same graded candidate read for the patient arm's candidate set and the state holder.
- 03:05 CORRECTION: the runner's boards C (00:08) and D (00:39) were ALIVE all along -- my relaunches reused their log paths and truncated the files, so they looked dead; my duplicate processes were stopped to free the CPU; the originals finish and write the metrics. Rule: never reuse a log path for a relaunch; check `Get-CimInstance Win32_Process` for a live process before declaring a job dead. (The 21:40 graded board WAS genuinely lost -- no process existed.)
- 03:10 Phase 2 #3 (state reader graded read) = NULL (0.7989 -> 0.8016). Phase 2 done for the three flips: agent repaired; patient/state losses are upstream (heads obj; tagger). Waiting on boards C/D (runner originals, ~3 h each under contention).
- 03:30 Heads lever from the object anatomy: ORDER-AWARE semantic bootstrapping (object association after the verb, subject association before it; SUBJ-slot asset grown from the same store) -- teacher now prefers energy<-creating 4.5 vs energy<-wanting -0.3; full rebuild into a separate file running (session job); promote if obj/nsubj rise without UAS loss.
