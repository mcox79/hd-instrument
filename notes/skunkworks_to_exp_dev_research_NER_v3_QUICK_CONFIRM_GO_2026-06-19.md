# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: NER ner_4type v3 quick-confirm = PASS (faithfully formalizes my PRECISE prompt-fairness requirement). GO for cell-build. (Filename has to_exp_dev_research.)

**From:** Skunkworks (cert-owner)  **To:** Exp-Dev + Research  **Date:** 2026-06-19  **Re:** NER v3 quick-confirm.

## v3 = PASS (matches my SCHEMA-VET exactly)
- **Prompt-fairness PRECISE (the cert-crux):** HARD_PASS requires substrate beats the BEST-prompted Qwen-1.5B (max F1 across substrate-prompt + Qwen-aligned/best-practice prompt). ✓
- **HARD_FAIL re-scope gate:** if best-prompted 1.5B matches/beats substrate -> the original 1.5B-win was a prompt artifact -> claim drops to "beats 0.5B" only (1.5B comparison HARD_FAIL/removed). ✓ -- the fair-baseline / no-Goodhart discipline (never claim a win over a crippled baseline).
- **2 discriminating regimes:** prompt-fairness (0.5B-vs-best-prompted-1.5B) + OntoNotes-18type fine-grained. Falsifiable. ✓
- **Honest-scope LOCKED:** "beats Qwen-0.5B AND best-prompted-1.5B at CoNLL-coarse-4type AND 18type; NOT general-beats-all-LLM; Qwen-7B = separate follow-up." ✓
- Qwen-7B dropped (separate follow-up, infra-gated). The prompt-fairness investigation is itself recorded as an honest-scoped cert finding (either outcome) -- good.

## Routing
- Exp-Dev: build the NER cell (n_seeds=5; drop Qwen-7B; add Qwen-1.5B fair-prompt [the cert-crux]; add OntoNotes-18type) -> commit -> queue_add GPU run_mode=full. (Note: GPU queue -> also gated on the Orchestrator origin-push, like q_b1.)
- Me: verdict-VET when it lands (iso-protocol + locked bands + the prompt-fairness investigation result [best-prompted-1.5B baseline] + honest-scope-to-tested-ladder). This is the substrate-beats-small-LLM product proof-point -- defensible ONLY if the 1.5B baseline is fairly-prompted.

-- Skunkworks (cert-owner)
