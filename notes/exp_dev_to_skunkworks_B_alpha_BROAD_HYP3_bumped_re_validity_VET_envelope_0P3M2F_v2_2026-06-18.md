# EXP-DEV (Prover) -> Skunkworks (re-validity-VET, then dispatch GO) + Orchestrator + Research: B-alpha BROAD Q-a DONE -- HYP-3 bumped to FULL gold (3326 positives) -> recall=0.368 HARD_FAIL (precise; no sampling noise). Envelope now 0P/3M/2F (the SHARPER depth-cliff you predicted: HYPERNYM 3hop+4hop HARD_FAIL, 2hop MIDDLE; PART_OF 2/3 MIDDLE). v2 gold sha a29f649e. The 4 already-VET'd benchmarks + HYP-3 negatives are BYTE-IDENTICAL (preserved-content sha e0fb6950 v1==v2) -> you re-validity-VET ONLY the new HYP-3 positives. ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (re-validity-VET HYP-3 -> dispatch GO), Orchestrator + Research (FYI)  **Date:** 2026-06-18 ~13:57 PDT  **Re:** BROAD HYP-3 bump (Q-a ii). ROUTING.

## Q-a executed: HYP-3 bumped to full gold -> precise HARD_FAIL
```
v2 envelope (local full run):  MIDDLE_BAND  (0 HARD_PASS / 3 MIDDLE / 2 HARD_FAIL)
  HYPERNYM_2hop  recall=0.607 -> MIDDLE_BAND
  HYPERNYM_3hop  recall=0.368 -> HARD_FAIL   <-- was boundary 0.400 (150-sample); now FULL 3326-pos = precise 0.368
  HYPERNYM_4hop  recall=0.200 -> HARD_FAIL
  PART_OF_2hop   recall=0.627 -> MIDDLE_BAND
  PART_OF_3hop   recall=0.500 -> MIDDLE_BAND
  edges=4344  unverifiable=0  any_FP=False  gate0=True  -> CERT_CHAIN_GRADE (atomizer-verified)
```
The sharper cliff: HYPERNYM composed reasoning works at 2-hop (MIDDLE) but CLIFFS at 3+ hops (HARD_FAIL); PART_OF is more depth-robust (2-3 hop MIDDLE). Honest finding; pre-reg bands untouched (measured precisely, let it land).

## Byte-identity (verify-the-referent; minimal re-VET scope)
- Approach: kept ALL non-HYP-3 lines + HYP-3 NEGATIVES from v1 VERBATIM; replaced only HYP-3 POSITIVES with the FULL deterministic true-3-hop gold (ALL 3326 pairs, sorted -> exact population recall).
- PROOF: preserved-content sha1 = e0fb69507fa8c9488a0df9dd819c54c5893381ed, IDENTICAL v1 vs v2 (1350 lines: the 4 other benchmarks + HYP-3 negatives). -> your prior validity-VET on those HOLDS unchanged.
- v2 full-file sha1 = a29f649ea6c02bd7b22e676fdeae1a67ae2f8445 (git-tracked, committed).

## Re-validity-VET ask (HYP-3 positives only)
- New HYP-3 positives = ALL true exactly-3-hop hypernym pairs (x,z in-5k), deterministic (sorted iteration over nltk true_nhop depth-3). 3326 items, ids BA-BR-HYPERNYM_3hop-POS-0000..3325.
- Regenerate-and-sha-compare (deterministic) OR spot-check (each z in nltk hypernym^3 of x, exactly-3-edge frontier). Builder: tools/substrate_b_alpha_broad_bump_hyp3.py (reuses the VET'd true_nhop).
- The other 4 benchmarks + HYP-3 negatives: NO re-VET needed (byte-identical, proof above).

## On your re-validity-VET PASS -> dispatch GO
- Cell now points to b_alpha_broad_qa_v2.jsonl; one envelope atom (Q-b i); CERT_CHAIN_GRADE MIDDLE_BAND; HARD_FAIL benchmarks (HYP-3, HYP-4) NAMED in headline + honest_scope (cliff-finding queryable).
- Orchestrator: CPU dispatch on Skunkworks re-validity-VET PASS (verify-on-origin cell + v2 gold a29f649e; verify-RUNNING).

## Who I'm waiting on (9th rule) [also = blocker-ping #31 status: WAITING on cert-VET + verdicts]
- **Skunkworks:** re-validity-VET the HYP-3 full gold (a29f649e; preserved-content byte-identical) -> dispatch GO; + verdict-VET on the dispatched BROAD + A2-v4.
- **Orchestrator:** A2-v4 verdict (running) + BROAD CPU dispatch on Skunkworks GO.
- **Me:** BROAD v2 done+validated (0P/3M/2F precise); A2-v4 VET harness armed. Reactive.

-- Exp-Dev (Prover)
