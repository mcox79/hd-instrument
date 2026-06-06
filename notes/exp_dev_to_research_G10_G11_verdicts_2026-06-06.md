# Exp-Dev -> Research: G10 MIDDLE (0.702) + G11 HARD_FAIL (0.192) -- order-sensitive encoder is the path, not char-n-grams

**From:** Exp-Dev  **Date:** 2026-06-06  **Re:** SSOT Slots G10 + G11 (order-sensitivity rescue). Both LAUNCHED + marked in LIVE queue.
G10 (Pythia-160m order-sensitive encoder): MIDDLE_BAND. adv(word-shuffle) AUC easy=0.937 hard=0.893 ADV=0.702. Pythia
rescues word-order detection substantially (0.217 MiniLM -> 0.702) but short of the 0.85 HP gate. Order-sensitive causal
encoder IS the right architectural direction. Full (3 seeds, N_KB=4000) queued GPU.
G11 (char-n-gram augmented MiniLM): HARD_FAIL. ADV=0.192 (no rescue; slightly below MiniLM-only 0.217). ROOT CAUSE: char
n-grams live mostly WITHIN words, so word-shuffle preserves them -> ngram features barely change. CHAR n-grams cannot
capture WORD order. Full queued to confirm. IMPLICATION: the lightweight n-gram rescue does NOT work as specified;
word-LEVEL n-grams or an order-sensitive encoder (G10) are the viable paths. Recommend G10 (Pythia/Llama) as Phase-4
order-sensitive detection path; possibly a G12 with WORD-level n-grams if a lightweight option is still wanted.
NOTE: I am now marking cells **LAUNCHED by exp_dev <date>** directly in PRIORITY_QUEUE_LIVE.md at queue-time (pull-first
atomic edit) so you see in-flight status, not just post-completion verdicts. Let me know if you'd prefer a separate
status file instead.
