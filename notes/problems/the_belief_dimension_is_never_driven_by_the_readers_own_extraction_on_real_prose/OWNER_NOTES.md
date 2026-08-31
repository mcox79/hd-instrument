---
owner_verdict: DONE
---

SUBMISSION — the_belief_dimension_is_never_driven_by_the_readers_own_extraction_on_real_prose
status: SOLVED (refute-and-rebuild; validated on a powered external benchmark). WIP until owner_verdict: DONE. hdlab/ UNTOUCHED (default-off diff ready in PROPOSED_HDLAB_LANDING.md, Q111).

REVERIFY: .venv/Scripts/python.exe verification/test_belief_at_t_end_to_end_organ.py   (ALL 19 CHECKS PASS)

THE BRIEF WAS REFUTED, THEN REBUILT ON THE BRAIN'S ACTUAL MECHANISM.
The brief drives belief from Sally-Anne OBJECT-MOVE extraction. That source is (a) ~absent from real prose (viability probe: ~1 move/book, 0 objects with >=2 moves / 12 LitBank books, mostly idioms) and (b) the WRONG brain mechanism: a research drill (Koster-Hale 2017/2014; Saxe; Zwaan; Dodell-Feder 2011) shows the mentalizing net holds a CONTENT-GENERAL, SOURCE-TAGGED propositional attitude fed by LANGUAGE ABOUT MINDS. The object-move is a developmental DIAGNOSTIC, not the mechanism (channel-density: narrator-epistemic+testimony 4.2x object-moves). REBUILT: drive the PROMOTED, untouched belief_timeline from the reader's OWN extraction across FOUR channels — narrator-epistemic + testimony (dominant; value read off mental/speech verbs) + perception + INFERENCE — reality separate, ignorance = None.

HEADLINE (INDEPENDENT, POWERED, EXTERNAL, ORGAN-DRIVEN): FANToM info-access ToM (Kim 2023; fetched to data/corpora/fantom/), 253 conversations, 3572 character knows/ignorant judgments. Presence-interval registration drives the ACTUAL belief_timeline organ:
 - reader 0.893 vs strongest floor (assume-knows) 0.665 -> +0.228 [+0.204,+0.253] CI-sep
 - vs shuffled-order twin +0.138 CI-sep AND vs random-presence twin (0.66 base rate) +0.337 CI-sep
 - false-belief: on 1198 IGNORANT characters reader-says-ignorant 0.939 vs beliefless 0.000
 - error drill: 10.7% miss, 4:1 UNDER-attribution (309 testimony/relay FN vs 73 FP) = front-end residual, not the mechanism.
This clears the brief's bar (CI-sep over the strongest floor + twin losing + false-belief) on a REAL, POWERED population.

SUPPORTING (control + LitBank): mechanism (oracle -> belief_timeline) beats the strongest floor CI-sep (+0.303); live gap = 100% extraction; false-belief +0.929; PERSISTENCE signature (last-mention collapses 1.0->0.33->0.0, timeline holds); FLASHBACK (chrono-order via register 1.0 vs narration 0.0); GENERALISES across fact types + all 4 channels; FHRR substrate read-out seed-stable; source-tagging 0.89 + reliability-discounting; two-agent dramatic irony beats the no-asymmetry floor. LitBank real prose (n=6): knowledge-state +0.571 CI-sep, false-belief +0.800 CI-sep (literary exact-VALUE slice stays coverage-bounded — a corpus property, FANToM supplies the powered population).

EVERY GAP ROUTED TO A VETTED ORGAN (one at a time; vetting caught two wrong picks):
 - status change-of-state: NOT intrinsic — the promoted state_register recovers 0.60 > a stronger parser 0.40; WIRED (+ factivity-aware veridicality gate) -> modern status live 1.0.
 - open-ended belief value: distributional_meaning_channel (wrong shape) + conceptual_meaning (too weak) REJECTED; WordNet synonym+entailment (15/17, 0 antonym FPs) WIRED -> paraphrase 0.00->0.50 (deceased->dead, wed->married), antonym-inflation control confirms no loosening.
 - inferred belief: 3-schema edge extractor (EXCLUSION / TRANSITIVE-SPATIAL / MODUS-PONENS) -> belief_timeline.fired_inference_events, WIRED END-TO-END: recall 0.83, all gated controls stay ignorant (evidence-gated; belief never seen nor stated).
 - location object-move: parser-recall wall (spaCy 0.92 > in-substrate 0.75) -> p2 (SPACE + BELIEF converge). flashback chrono -> timeline_register (vetted). coref -> gold coref is the isolation choice.

KEY REALIZATION: the event source was the whole problem, not the organ. Object-moves -> reading the belief VALUE off the narrator's/speaker's words took the dominant channels 0.0->1.0; ignorance = None unlocked the abundant real "did not know" prose; and every gap already had an organ — vetting each in isolation caught two wrong picks before the right one.

HONEST DISPOSITION of the last excellence items: #1 (FANToM through the actual organ + error drill + stronger control) DONE. #2 full-passage own-coref: gold coref is the deliberate isolation choice (reader's own coref is a validated axis) — a clean follow-on, not a defect. #3 larger real-narrative gold: NOT padded with weak items (coverage-bounded corpus property); FANToM supplies the powered real population. Nothing averaged away.

PROPOSED hdlab LANDING (default-off, Q111; PROPOSED_HDLAB_LANDING.md): track_belief on SituationReader -> sm.belief_timeline + believes(A,F,T) + knows(A,F,T); source = 4-channel extractor (belief-assertion PRIMARY, substrate-native) + state_register status + inference extractor; ignorance native; reality separate. Flip on owner approval. Solver did NOT write hdlab.

AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT §2b) in SOLVED: belief event source is NOT object-moves; content-general + source-tagged + 4-channel; status handled by state_register; location extraction = shared parser ceiling (p2).

FILES: experiments/{_belief_reader, belief_at_t_gold, exp_belief_at_t_end_to_end_v1, exp_belief_extraction_drill_v1, exp_belief_fantom_infoaccess_v1, _build_real_belief_gold, _belief_probe_scratch, _belief_channel_probe_scratch}.py ; data/belief_at_t_gold_v1/real.jsonl ; data/corpora/fantom/ ; verification/test_belief_at_t_end_to_end_organ.py ; notes/problems/<slug>/{DESIGN_brain_and_mapping, SOLVED, DATA_REQUEST_fantom, PROPOSED_HDLAB_LANDING}.md
