# Forward-predictive objective from maintained WM state — design (2026-07-29)

Scope: DESIGN ONLY. Answers the remaining "forward-predictive" leg of the founding
diagnosis (encoder is feedforward+bidirectional+stateless where the brain is
recurrent+forward-predictive+stateful). Builds directly on
`notes/brain_fidelity_audit_as_built_stateful_core_2026-07-29.md` section A (gap: our
`surprise` is a retrieval/familiarity match, not a generative prediction) and reuses the
already-built primitives in `hdlab/slot_attention_wm.py` (per-slot PBWM gate, post
audit-C fix) + `experiments/exp_stateful_core_situation_model_v1.py` (training loop).
No experiment cell or module is edited by this note. Calibration per
[[feedback-lit-scan-calibration-penalty]]: CITED@ vs REASONED@ tagged per claim;
novel-synthesis claims capped/deflated.

---

## 1. Biology

CITED@Rao&Ballard1999 / CITED@Friston2005 (hierarchical predictive coding): at every
level of cortex, a *generative* top-down signal proposes what the next input should look
like, BEFORE it arrives, from the current internal (recurrent, persistent) state alone;
the residual (prediction error) is computed at the input level and propagates both as the
training signal (synaptic update) and as the gating/attention signal (which units get
"believed"/passed forward). CITED@Rabovsky2018 (N400 as PE over an integrated situation
model, not a lexical-surprisal signal) — the violation is measured against a *maintained*
representation of the unfolding situation, not the raw token stream. CITED@Zwaan et al.
1995/1998 — updating cost is highest exactly at discontinuities, i.e. where a genuine
prior expectation was wrong, not where the current input merely differs from stored gist.

The critical biological property our current `surprise_k` (audit-A) lacks: the brain's PE
is computed between an **actively generated candidate representation of what comes next**
and the evidence — it is anticipatory. Our current signal (`1 - cos(unbind(slot_k, key),
clause_rep)`, `slot_attention_wm.py:117-119`) compares the SAME clause's own bound content
against itself after decoding — it is a consistency/familiarity check on the CURRENT
clause, not a guess about a FUTURE one. Both are legitimate PC-family quantities (Rao-
Ballard use both within-level consistency and across-level anticipation), but only the
anticipatory kind lets the maintained state's *forward validity* be scored — the piece
that is missing.

## 2. Concrete mechanism (reuses our primitives)

**What is predicted:** the pooled latent of the NEXT clause, `clause_rep_{t}`, computed
through OUR OWN encoder (`model.pooled`, same call as `encode_clause_batch` already uses)
— never a borrowed embedding, honoring the standing invariant. This keeps the target
in the same representational space slots already bind into (audit-B/C already operate in
this space), so no new representation format is introduced.

**From what — a slot-set predictor head, not a mean-pool (do not reintroduce audit-C's
bug):**

```
class ForwardPredictor(nn.Module):
    def __init__(self, d_model, hidden, seed):
        self.pred_query = nn.Parameter(torch.randn(d_model) * 0.05)  # learned, content-free
        self.attn_net = _mlp(2 * d_model, hidden, 1, seed_gen)       # same family as addr_net
        self.predict_mlp = _mlp(d_model, hidden, d_model, seed_gen)

    def forward(self, slots):                       # slots: [B, K, d]  (state BEFORE clause t)
        B, K, d = slots.shape
        q = self.pred_query.expand(B, K, d)
        attn_logits = self.attn_net(torch.cat([q, slots], dim=-1)).squeeze(-1)   # [B, K]
        attn_w = torch.softmax(attn_logits, dim=-1)
        ctx = (attn_w.unsqueeze(-1) * slots).sum(dim=1)                          # [B, d]
        return F.normalize(self.predict_mlp(ctx), dim=-1)                       # predicted_latent_t [B, d]
```

This mirrors `addr_net`'s per-slot-scored-then-softmax pattern (a precedent already
audited as brain-faithful in shape) instead of `slots.mean(dim=1)` — the exact
anti-pattern audit-C just removed from addressing. `pred_query` stands in for "what the
situation model currently expects to attend to when guessing forward," analogous to a
top-down prediction unit in PC hierarchies (CITED@Friston2005, generative model issues a
query independent of the as-yet-unseen input).

**Timing (anticipatory, not post-hoc):** call `predicted_latent_t = predictor(slots)`
using `slots` **before** `wm.step` runs for clause t (i.e. the pre-update state from
clause t-1's write). Then encode clause t via the encoder to get `clause_rep_t` (as today).
Score `PE_pred_t = 1 - cos(predicted_latent_t, stopgrad(clause_rep_t))`. This slots
directly into `forward_item_batch`'s existing per-clause loop
(`exp_stateful_core_situation_model_v1.py:363-366`) as one extra call before
`encode_clause_batch`/`wm.step`, and the existing `run_clause_stream` per-step feats dict
gains a `pe_pred` key for free (also partially addresses audit-E's discarded-trajectory
gap, since a per-step list already exists and is simply currently unused by
`forward_item_batch`).

## 3. Collapse avoidance

The classic JEPA failure (CITED@LeCun2022, CITED@Assran2023 V-JEPA) is representation
collapse: the predictor learns a trivial constant, driving PE to ~0 with zero information.
Two guards, layered cheap-to-expensive:

1. **Stop-gradient asymmetry, SimSiam-style (CITED@Chen&He2021 "Exploring Simple Siamese
   Representation Learning"):** `clause_rep_t` is detached before the cosine term
   (`stopgrad(clause_rep_t)`); the predictor MLP exists ONLY on the `slots -> predicted`
   branch, not mirrored on the target branch. SimSiam's result (no negative pairs, no
   momentum/EMA target network, collapse avoided purely by architectural asymmetry +
   stop-grad) is the cheapest applicable guard and requires no second encoder copy — a
   real cost saving given our encoder is already being fine-tuned jointly every step (an
   EMA shadow copy would mean carrying/updating a full second copy of a growing encoder).
   Recommend this as PRIMARY.
2. **Variance backstop on `predicted_latent`, VICReg-style (CITED@Bardes2022), narrowly
   scoped:** a hinge term `mean(relu(1 - std(predicted_latent, dim=0)))` computed
   per-batch across the d dimensions of `predicted_latent` only — NOT re-attempting R4's
   full VICReg-to-KB-graph pastiche. Distinguish explicitly from R4's failure: R4 applied
   VICReg as part of an alignment loss to a STATIC external target (KB-graph relational-
   InfoNCE) — the collapse-adjacent risk there was entangled with aligning to a fixed
   symbolic structure. Here the variance term guards only the predictor's own output
   distribution against a trivial-constant solution; there is no static external target
   anywhere in this design (the target `clause_rep_t` is produced by the SAME stream,
   changes every clause and every item — this is the structural difference from every
   prior static-target-alignment failure, see section 6).

If (1) alone proves insufficient at smoke (predictor variance collapses despite falling
PE_pred loss), escalate to a true EMA target encoder (Polyak-averaged copy of `model`,
stop-grad through it) as the JEPA-proper fallback — flagged as the build's single highest
design risk (section 8), not built preemptively.

## 4. Encoder recommendation

**Keep the MLM-bidirectional encoder; add the predictive head on top of clause-level
pooled output.** Do not build a causal/forward encoder variant now.

Justification: the anticipation this design adds operates at the SITUATION-MODEL
level — predicting which upcoming CLAUSE's gist follows, given the accumulated slot
state — not at the sub-clause/token level. CITED@Rao&Ballard1999's hierarchy explicitly
allows different levels to integrate over different windows: a lower level can form a
locally-integrated (here: bidirectional-within-clause) representation while a HIGHER level
still issues a genuine anticipatory prediction over the coarser unit that lower level
produces. Our `clause_rep` is exactly such a lower-level integrated unit; making the
higher (slot/situation) level anticipatory over that unit is a legitimate partial
implementation of the hierarchy, not a violation of it. REASONED@, moderate confidence
(P~0.40, deflated): this is a plausible reading, not a settled equivalence — if capability
gains don't materialize (section 6 HARD_FAIL), a causal/forward encoder is the next
escalation, but it is expensive (retrains the shared encoder's attention pattern, touches
every other consumer of `clause_rep`) and the prior forced-causal attempt (v5, causal-LM
full-vocab CE) failed for OOM + stateless reasons unrelated to whether within-clause
attention was causal — so that prior failure does not license concluding causal encoding
itself is bad, only that full-vocab next-token CE was bad. Keep this escalation path
explicit but deferred.

## 5. OOM-free confirmation (v5-class failure structurally absent)

`predicted_latent_t` and `clause_rep_t` are both `[B, d_model]` (d_model is the
substrate's fixed vector width, e.g. 256-1024 in current configs — at least an order of
magnitude below the ~16k tokenizer vocab that caused v5's OOM). The loss term
(`1 - cos(...)`, or MSE) is computed once per clause-step over a `[B, d]` pair; no
`[B, L, vocab]` logits tensor is ever materialized anywhere in this path — v5's failure
mode required a full per-position, per-vocab-entry score tensor from a causal-LM head,
which this design has no analog of (there is no vocab-sized output anywhere; the only
head is `predict_mlp: d -> d`). The OOM class is categorically absent, not merely
smaller.

## 6. Measurement + can-fail bands

**Training signal (diagnostic, not the capability test):** `PE_pred` trajectory across
epochs should trend down; `std(predicted_latent, dim=0)` must stay above a floor
(recommend 0.10 in the L2-normalized latent space) throughout training — a falling
`PE_pred` with collapsing variance is flagged as COLLAPSE, not success (see HARD_FAIL
below).

**One-variable ablation:** `Core` = per-slot-gated WM (post audit-C fix, once re-smoked)
exactly as currently specified, both arms (A blank / B KB), vs `Core+ForwardPred` = same
core with (a) the predictor head added, (b) `PE_pred` folded into the gate
(`gate_net` input becomes `[clause_b, slots, surprise_k, PE_pred_broadcast]`, i.e. a
GLOBAL situational-PE alongside the existing per-slot LOCAL retrieval-PE — this is
genuinely hierarchical PC, not a redundant duplicate signal: `surprise_k` = "does this
slot's own stored content match," `PE_pred` = "did the situation model anticipate the
next clause at all," matching Rao-Ballard's multiple simultaneous PE levels), and (c) a
new loss term `lambda_fwd * PE_pred[coh].mean()` (coherent-items-only, mirroring the
existing `pe_term` policy at
`exp_stateful_core_situation_model_v1.py:407` — training the predictor only on NORMAL
continuations preserves the discriminative gap on incoherent items that the judge reads).
Start `lambda_fwd` at ~0.1x `lambda_pe` to avoid destabilizing the already-fragile joint
optimization (grad-clip already present per the module's own note on an 18x grad-norm
spike). Same seeds (>=2), same random-init-core control, both KB arms preserved.

- **HARD_PASS:** `Core+ForwardPred` improves MES `eval_acc` by >=+0.10 absolute over
  `Core`-only AND clears the random-init-core control by >=+0.05 absolute, in >=1 of 2
  seeds with the other seed at least non-negative in direction; OR (independently) the KD
  Arm-B-vs-A delta flips from the current negative/flat (-0.125) to >=+0.05 positive in
  BOTH seeds (direct evidence the forward-predictive signal lets the KB prior actually get
  USED rather than diluted/gamed, addressing audit-D). Predictor variance floor
  (std>=0.10) must hold in the PASS run — a pass with collapsed variance does not count.
- **HARD_FAIL:** `Core+ForwardPred` ties BOTH `Core`-only AND random-init-core (all three
  within +/-0.03 on MES `eval_acc`) — the same training-invariant/no-effect signature
  audit-C's mean-pool bug produced; report as FAIL-BY-NO-EFFECT. Separately, if
  `predicted_latent` variance collapses below floor while `PE_pred` loss still falls,
  report as FAIL-BY-COLLAPSE (distinct diagnosis — escalate to EMA target per section 3,
  do not conclude the mechanism class is wrong).

## 7. Build-order recommendation

**AFTER the per-slot-gating (audit-C) re-smoke, not before.** One-variable discipline: if
the re-smoke of the per-slot PBWM gate does not itself clear the random-init-core control,
adding a second new mechanism (forward-predictive coupling) on top of a still-broken core
confounds attribution — a HARD_PASS or HARD_FAIL on `Core+ForwardPred` would be
uninterpretable (can't tell whether the forward-predictive term helped/hurt, or whether
`Core` itself was still the limiting factor). Sequence: (1) re-smoke audit-C's per-slot
gate fix alone, confirm it clears random-init-core on MES; (2) only then dispatch this
design as the next `hdi_exp_dev` build, ablating against that now-functioning `Core`.

## 8. Single highest-risk design decision

**Whether stop-gradient-only (SimSiam-style, no EMA target network) is sufficient to
prevent collapse in THIS setting.** SimSiam's no-collapse result was empirically
established at large-batch, many-thousand-step image-pretraining scale; our regime (tens
to low-thousands of items, small batches, a few hundred steps, and — unlike SimSiam — a
jointly fine-tuned rather than frozen/from-scratch encoder feeding both branches) is far
outside where that empirical guarantee was demonstrated. REASONED@, deflated, P~0.35 that
stop-grad-alone suffices unmodified at this scale. If smoke shows collapse, the fallback
(EMA target encoder, section 3) is a real additional build cost (a maintained second
encoder copy) that should be pre-registered as a contingency budget line, not discovered
mid-build.

---

## Citations (CITED@ = literature-verified in prior session docs; carried, not re-searched this cycle)
- Rao & Ballard (1999) / Friston (2005) — hierarchical predictive coding, generative
  top-down prediction, multi-level PE — carried CITED@ from
  `brain_foundational_component_analysis.md` row 1 and the 07-29 audit note.
- Rabovsky, Hansen & McClelland (2018, *Nat Hum Behav*) — N400 as PE over an integrated
  situation model — carried CITED@ from `drill_language_world_model_framing.md`.
- Zwaan, Langston & Graesser (1995); Zwaan & Radvansky (1998) — updating cost at
  discontinuities — carried CITED@ from `drill_language_world_model_framing.md`.
- LeCun (2022 position paper) / Assran et al. (2023, I-JEPA/V-JEPA) — predict in latent
  space, not pixel/token space — carried CITED@ from
  `notes/research_drill_embodied_revival_3x_2026-06-10.md` (chunk049/053).
- Chen & He (2021, CVPR, "Exploring Simple Siamese Representation Learning," SimSiam) —
  stop-gradient + predictor-asymmetry prevents collapse without negative pairs or a
  momentum/EMA target — NEW this cycle, generic-term verified (architecture widely
  reported; not substrate-specific), P_deflated per lit-scan-calibration-penalty applies
  to its transfer to our small-scale jointly-trained setting (section 8).
- Bardes, Ponce & LeCun (2022, ICLR, VICReg) — variance-covariance regularization against
  collapse — carried CITED@ from R3/R4 session history; narrowed application justified in
  section 3 (distinguished from R4's static-KB-graph-alignment failure mode).
- REASONED@ (code-level, this note): all mechanism/wiring claims about
  `hdlab/slot_attention_wm.py` and `experiments/exp_stateful_core_situation_model_v1.py`
  are from direct line-cited reading, not hypothesized.

Verified citation count this cycle: 7 anchors (6 carried CITED@ from prior-verified
session docs + 1 new generic-term-verified this cycle: SimSiam). No external search was
run for the already-well-established JEPA/Rao-Ballard/Rabovsky/VICReg anchors (carried
per KB-check discipline, avoiding redundant re-scan of settled citations); SimSiam was the
one genuinely new element this cycle and is a standard, non-substrate-specific
architecture claim.
