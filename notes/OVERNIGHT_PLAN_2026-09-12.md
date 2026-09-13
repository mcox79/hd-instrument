# OVERNIGHT PLAN — 2026-09-12 → 13 (owner asleep; autoloop ARMED; owner direction: "make the top of the chain as BF as possible, and fix all downstream 1 at a time")

**Operating rules for every continuation:** runs go to RUNNER agents (`hdi_exp_dev`, model haiku; never wait in the main thread);
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
- 00:15 1b: graded category hand-off landed + measured (gold 0.5562 / hard 0.5340 / graded 0.5379); ONE shared frontend `hdlab/frontend.py` landed and the patient/agent/state/causation arms shimmed onto it (the switches now reach the board); self-test on a runner; post-routing boards queued after the running pair.
- 00:30 transfer stream to the desktop FINISHED (pipe exit 0, 18:03->03:27Z); delta sync + desktop verify on a runner. Copular clause convention added to the attachment arm (decode-time; witness 15/15); state-dim + per-relation measurement on a runner. Board self-tests PASS under default and fully-BF switches after the shared-frontend routing. Fold queue written (13 items; #4 = unreconciled second heads-rung organ from the pri-2 solver: reading-learned EM scorer + constructions, beats supervised OOD on GUM +0.0235).
- 00:55 1c: copular convention landed (state 0.6587 CI-sep under BF heads); heads-rung reconciliation: the arm subsumes the pri-2 reading-learned scorer; its Hindle-Rooth PP cue FOLDED into the arm ('pp' cue; association grown treebank-free) -- asset rebuild + per-relation on a runner. Board 'counts' (reader-only tagger switch, pre-routing) finished; counts+attarm running.
