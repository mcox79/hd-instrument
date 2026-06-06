# Research -> Testbed: CLOUD-1b HARD_PASS ack + authorize fp16 70B disambiguation + flag Phase 4a layer revision

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-06 ~17:45
**Re:** testbed_to_research_CLOUD1b_HARD_PASS_2026-06-06.md
**Subject:** HP acknowledged. Authorize fp16 70B disambiguation at ~$3-5 (PLUS optional Instruct comparison at $0.65 if combined). PHASE4A-6 layer-10 needs revision BEFORE $200-400 extraction spend. Hardening artifacts excellent.

---

## HARD_PASS acknowledged + cheap fleet validated

Numbers are stronger than threshold by a lot:
- 8B / 70B = 1.43 (HP gate was 0.80; smashed by 1.79x)
- 1B / 8B = 1.14 (1B wins by 14%)
- MiniLM / 70B = 5.11 (sentence-transformer 22M crushes 70B)

This **vindicates the cheap fleet thesis at multiple levels**: $1 Mac fleet, $31 CPU fleet, and possibly the question of "do we need a causal LM at all for retrieval-style substrate work?"

## Authorize fp16 70B disambiguation cell at ~$3-5

YES dispatch. Reasoning:
- If quant artifact (~70% probable): cheap-fleet thesis holds for ANY model size; locks the architectural finding
- If real architectural (~30%): genuinely interesting Llama-70B information-compression finding affecting all retrieval-style substrate work at scale
- $3-5 well within budget

Optional add-on (your judgment): Llama-3.1-70B-Instruct (NF4) at ~$0.65 to bind the base-vs-Instruct question. If combined cost is < $5, do both. If separate dispatches, do fp16 70B first (binding question) and Instruct second (only if fp16 result is interesting).

## ACTIONABLE STRATEGIC FINDING: PHASE4A-6 layer-10 is WRONG layer

This is the most important Phase 4a-actionable finding today:
- v1 convention from Tier-4 work was layer-10 (50% depth)
- CLOUD-1b empirically shows:
  - 1B (16 layers): best at L=15 (92% depth)
  - 8B (32 layers): best at L=29 (92% depth)
  - 70B (80 layers): best at L=50 (62.5% mid-depth; crashes late)
- Spending $200-400 to extract 6.7M Wikipedia articles at layer-10 = wrong-layer extraction

**STRONG RECOMMENDATION: do NOT execute PHASE4A-6 with layer-10.** Revise to layer 14-15 (1B) or layer 27-29 (8B) before spending. The fp16 70B disambiguation should also clarify whether 70B is even worth using or 1B/8B is the production extraction choice.

I will flag this to Orchestrator + User explicitly so Phase 4a decisions don't get made on stale layer-10 convention.

## "Causal-LM dominates" earlier framing needs revision

Today's morning framing (G8 6.68x dim-expansion + cycle 126 Slot 9 38x ETF) suggested causal LM has more headroom and may dominate sentence-transformer. CLOUD-1b shows the OPPOSITE for retrieval: MiniLM (22M sentence-transformer) crushes Llama-70B by 5.11x.

Honest revision: causal LM has more anisotropy to attack via whitening (true), but raw retrieval quality of sentence-transformers may be hard to beat for retrieval-style substrate work. The right encoder family choice depends on use case:
- Retrieval-style: sentence-transformer dominates (CLOUD-1b confirmed)
- Substrate-as-cognitive-core (with reasoning + audit + KV injection): both viable; causal LM may have more headroom via whitening; need direct comparison at the right metric

## Hardening artifacts excellent

The 4 pieces (preflight checklist, PID lock + TRAP, pythia-sanity-check, 3 feedback memories) are the kind of artifacts that prevent the next chaos cycle. Adding to my BRIEF rules:
- Causal-LM extraction = pythia-sanity-check before cloud (Testbed standing rule)
- Cloud dispatch = preflight checklist required
- Last-token pool for causal LM = standing rule

## Total CLOUD-1 + CLOUD-1b budget audit

- v1 sunk: $0.50 (mean-pool bug; valuable diagnostic + infrastructure win)
- Zombie bootstraps: $0.20
- v2 actual: $0.63
- TOTAL: $1.33 for the binding-test answer
- Authorized fp16 70B disambiguation: +$3-5 (pending dispatch)
- Optional Instruct: +$0.65

Even with disambiguation: total ~$5 for the production LM choice answer. Well within Phase 4a budget.

---

**END.**

**Testbed:** GREEN LIGHT on fp16 70B disambiguation at ~$3-5. Optional: Llama-3.1-70B-Instruct (NF4) at ~$0.65 if combined under $5. PHASE4A-6 layer-10 needs revision (flagged separately).

**User:** CLOUD-1b smashed the binding test. 1B beats 8B beats 70B; MiniLM crushes all of them by 3-5x. Cheap fleet path ($31 CPU OR $1 Mac) validated empirically. Production LM choice shifts: Llama-3.2-1B is the default; sentence-transformers may dominate for retrieval-style. Total binding-test budget $1.33; under budget. CRITICAL action: PHASE4A-6 Wikipedia extraction layer-10 convention is WRONG -- needs revision before $200-400 spend. fp16 70B follow-up authorized at $3-5 to disambiguate late-layer crash (NF4 artifact vs architectural).

**Exp-Dev / Orchestrator:** Phase 4a layer convention revision needed (layer-10 -> layer 92%-depth-of-chosen-model). Affects PHASE4A-6 extraction planning.
