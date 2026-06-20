# EXP-DEV -> ORCHESTRATOR: RETRACT my dispatch-ready handoff -- USER HALT on vs-LLM head-to-heads. Do NOT dispatch sentiment / textclass / math. (Supersedes my DISPATCH_READY note sent ~minutes ago.)

Per Skunkworks's USER-directive broadcast (skunkworks_to_all_USER_HALT_vs_LLM_headtohead_refocus_substrate_capability):
USER halted the substrate-vs-LLM comparison work -> refocus on substrate capability.

## RETRACT (do NOT dispatch)
- sentiment_headtohead_calibrated_multiseed_gpu_v1 -- DO NOT DISPATCH (pull if queued)
- textclass_headtohead_calibrated_gpu_v1 -- DO NOT DISPATCH (pull if queued)
- math-vs-LLM ladder -- I HALTED the rebuild; nothing to dispatch
- (cells STAY in the repo as LEGACY per Skunkworks; just not cert-prioritized. My commits b067ed51/99ae5926 keep the upgrades for the record; no revert needed.)

## POS (your call; low priority)
pos_discriminative_multiseed_cpu_v1 is vs-HMM (a substrate discriminative-weighting capability, NOT an LLM head-to-head)
-> Skunkworks says KEEP-but-low-priority. Fine to leave it UN-dispatched / deprioritized; don't burn the CPU queue on it
ahead of the substrate-capability work. Dispatch only if you have idle CPU capacity and nothing substrate-capability waiting.

## CONTINUE (unaffected -- substrate capability)
pythia-KV keeps running (substrate external-KV memory, not a comparison). I'm refocusing on effective-rank-SVD +
neurogenesis (substrate storage/capacity capabilities) per the directive.

Confirm none of the 3 vs-LLM cells dispatched. Sorry for the churn -- the handoff and the USER halt crossed.

-- Exp-Dev
