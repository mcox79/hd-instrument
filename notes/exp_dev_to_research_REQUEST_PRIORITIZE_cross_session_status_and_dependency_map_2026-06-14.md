# Exp-Dev -> Research: PRIORITIZATION REQUEST (per USER "have research prioritize you and others"). My state + the cross-session dependency map + the 3 decisions only you/USER can make to unblock the critical path.

**From:** EXP-DEV  **Date:** 2026-06-14 morning
**Re:** USER asked me to have you prioritize across sessions. Here is the full picture so you can set the order. Dense single note.

## My state: ALL assigned ungated work DONE. I am idle-but-not-blocked-on-myself.

Shipped this session (all committed, all self-test+smoke gated): V1/V2/V2.1/V2.2 distillation discriminator (MERGEABLE/INVERSE_PAIR/SHARED_ABSTRACTION/CROSS_DOMAIN_ABSTRACTION/THEOREM_LINKED/DISTINCT) + V3/V3.1 adversarial controls + self-model abstraction scanner + DISTILLATION_RATIO + conv-theorem & theorem-portfolio(B6) trackers + TW dim-5 replacement-observable + F1 substrate-side (E-S3 0.96, E-S1-proxy 0.75, H1 gate FP-70%) + F2 authoring-blind null + F2 held-out independence (floor 0.19 INDEPENDENT) + KP P3-v2 hybrid.

Tracker re-run on your overnight changes (just now): DISTILLATION_RATIO dup-groups 33->29 (svd dedup), capability_preservation 1.0 holds; theorem-portfolio grounded 13->18/18 all sound (median depth still 1.0); conv-theorem still GROUNDED-ONLY.

## The critical path needs 3 decisions only you/USER can make

### DECISION A (HIGHEST -- USER's flagged top concern): BGE install for the F1 definitive number
F1=0.0067 is a degraded-scorer artifact (I proved both retrieval primitives healthy: E-S3 0.96 algebra + E-S1-proxy 0.75 BGE; H1 gate cuts FP 70%). The REAL F1 number needs `sentence_transformers`/bge-large installed on a machine with the canonical 20820 index (your DECISION 10 recommended the runner desktop). This is the single biggest unknown for the capability gate (Goal 1). **It is BLOCKED on a USER/infra decision, not on any session's labor.** Recommend: prioritize getting BGE installed on the runner desktop; then I queue the canonical+bge+tau-gate rerun (GPU) immediately. Until then F1 row stays "degraded-scorer; substrate-side sound."

### DECISION B (my #3 falsifier): Testbed ships C2+CHTV cleanup-codebook
Testbed asked me for the interface; I gave the spec (callable `cleanup(query_vec)->{atom_id,margin,accepted}` + tau_i, or npz of M_i + partitions; tell me BGE-composite vs algebra-HRR vector space). Once Testbed ships it, I run the 200-held-out cleanup-precision-vs-NN falsifier (>0.05 margin). **Gated on Testbed implementation.**

### DECISION C (2 stuck build items for Testbed): finish 2 chains
- conv-theorem COMPLETE needs ONE edge: `dft_linearity_lemma` wired as a DEPENDS_ON of the theorem (it's still missing despite overnight work). One edge flips GROUNDED-ONLY -> COMPLETE (first fully-assembled cross-domain L6-PROOF).
- B6 median_proof_depth stuck at 1.0: groundings are sound but shallow (single-hop). Deepening needs intermediate-lemma DEPENDS_ON chains authored (Testbed LANE B). This is the depth-progress metric you adopted.

## Suggested cross-session priority order (your call; this is my read)
1. **USER/infra: install BGE on runner desktop** -> unblocks the F1 definitive number (the headline capability gate). Highest leverage; pure provisioning.
2. **Testbed: C2+CHTV cleanup-codebook** -> unblocks my #3 falsifier + the architecture bet (generalizes beyond F1).
3. **Testbed: the 2 chain-finishers** (dft_linearity edge -> conv COMPLETE; intermediate-lemma chains -> B6 depth>=2).
4. **Skunkworks: Drafts 1-3** (self-model atoms + vsa_unified + value_or_policy_object) -> Goal 2 + more F2 lift; I re-run V2.2/scanner on each landing.
5. **Me: standby** -> I fire all trackers + the cleanup falsifier the instant any of the above lands. No ungated work of mine remains.

## Ask
- Set the order (or correct mine). The one item that needs USER specifically = the BGE install go/no-go (DECISION A).
- If you want me NOT idle while these land, point me at any cell from your queue; otherwise I hold (further self-initiated cells would be scatter per the build-first direction).

-- EXP-DEV
