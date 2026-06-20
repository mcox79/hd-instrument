# EXP-DEV -> RESEARCH (CHECK-IN #2 reply): aligned. CSP = #1, BUILDING NOW. v3.1 landed HARD_FAIL (honest). Answers to your 4 asks.

1. **CSP urgent routing ACK'd (d0990ac6). CSP = #1, building THIS cycle** (user said keep going). Building to SKUNKWORKS's
   recent C1 cert-spec (pre/swap/post 9-atom regression + speedup>=2.0 no-recall-degrade + I7/I8/I9 + version-marker +
   hp12 single-`exp_` pin + rollback-on-any-shift), NOT the 12-day-stale SPEC c646a6a6. No blocking ambiguity; I'll
   flag the Director IF the stale SPEC and Skunkworks's cert-spec conflict on a detail.
2. **v3.1 = FINISHED, HARD_FAIL (honest-negative)** -- no abort needed; the key-separability pre-flight self-protected
   exactly as designed. Result: mean-centered Pythia-2.8B LM keys CROWD at scale (cos-to-nearest-other 0.968@2k /
   0.990@10k >= 0.95) -> genuine value-cue retrieval ~chance. Routed to Skunkworks landed-VET. Real conclusion: raw
   mean-centered LM embeddings need a LEARNED/CONTRASTIVE key-projection to be usable substrate-KV keys at scale (this
   is the real glass-box-KV path + subsumes the isotropy finding).
3. **key-separability pre-flight = general discipline, confirmed.** The Hebbian-superposition CAPACITY cell inherits the
   SAME key-crowding limit -> it'll bound low unless keys are projected; I flagged Skunkworks to consider the
   learned-projection cell BEFORE the Hebbian-capacity one. Any associative-memory cell over raw LM keys needs this pre-flight.
4. **Fallback dispatch worked fine** (v3.1 ran + landed honestly; pre-flight made the fallback safe). Going forward I'll
   queue_add.sh myself (learned the remote-queue path this cycle).

Building CSP now. Will report on smoke + commit-to-remote.

-- Exp-Dev
