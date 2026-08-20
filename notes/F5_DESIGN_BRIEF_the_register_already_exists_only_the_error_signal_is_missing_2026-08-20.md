# F5 DESIGN BRIEF -- **THE SITUATION REGISTER ALREADY EXISTS AND IS LIVE. ONLY THE ERROR SIGNAL IS MISSING.**

**⛔ FIRST, A CORRECTION TO WHAT I TOLD THE OWNER ONE TURN AGO.** I said F5 *"is NOT small -- it
depends on F6 (Construction-Integration), also MISSING."* **The prior-work check says otherwise, and
the target is better-posed and smaller than I described.**

## WHAT ALREADY EXISTS (checked, not assumed)

`ORGAN_MAP` **E2 — Situation-model register / event indexing**:

- **`OURS`: `hdlab/situation_model_accumulate.py:84-103`** -- `bound = bind(role_vec, idx_vec[event])`
  bundled into a per-entity register; decode by `unbind` then `cleanup_argmax`. `CausalLinkRegister`
  reuses the identical organ. **`WIRED: YES`** -- and `situation_model_multibank` is live too,
  **one of only four modules the live path gains from a lazy import.**
- **`FIDELITY`: RIGHT-OP-WRONG-PLACE / PARTIAL -- *"has the register, has none of the PE-driven
  segmentation that decides WHEN to write."***
- **`BRAIN'S MATH`: event-indexing with PREDICTION-ERROR-DRIVEN SEGMENTATION** -- a boundary is
  posted when prediction error crosses threshold (Zwaan; **Zacks & Franklin SEM**). *"The register's
  update rule is UNPINNED."*

**➡️ SO F5's MISSING PIECE AND E2's MISSING PIECE ARE THE SAME PIECE. A running situation register
exists and is live; NOTHING COMPUTES PREDICTION ERROR AGAINST IT.** That error is exactly the N400
quantity `‖Δ situation_model‖`. **This is not "build two missing organs". It is "add the error signal
to an organ that already runs".**

## WHAT IS PINNED VS WHAT WOULD BE OUR INVENTION

*The standing rule: invent freely, but never label an invention as pinned. Tonight I already
mislabelled one mechanism as PINNED and had to withdraw it.*

| element | status |
|---|---|
| the REFERENCE POINT: error is against the **current discourse state**, not a fixed template | **PINNED** (Rabovsky/Hansen/McClelland 2018; Kutas & Federmeier 2011) |
| **a boundary is posted when prediction error crosses a threshold** | **PINNED** (Zacks & Franklin SEM) |
| error is **precision-weighted** -- the FORM `precision x error` | **PINNED** |
| the NORM (which `‖·‖`), the UPDATE RULE, the PRECISION ESTIMATOR, the THRESHOLD | **UNPINNED -- ours to choose and sweep** |
| that a *cosine-derived scalar* is an acceptable stand-in for `‖Δ‖` | **OUR INVENTION -- and G2 shows it going wrong** |

## 🔴 THE FAILURE THIS BUILD MUST NOT REPEAT

**`ORGAN_MAP` G2 already tried prediction-error gating and its gate NEVER FIRED** --
`exp_pc1_predictive_coding_residual_gate_v1`, threshold 0.3, **`skip = 0.00`, byte-identical to
ungated.** The recorded cause is **RIGHT-OP-WRONG-METRIC**: the residual is computed on a
**`sign()`-quantised** prediction, so a large graded error and a small one that flips the same bits
are indistinguishable, and no precision term exists.

**MANDATORY, AND IT IS A PRECONDITION NOT A NICETY: the error must be computed on a GRADED
quantity.** *Measured tonight on the read-out carrying the same substitution: signed vs graded
changes the nearest anchor **42.5%** of the time and flips the bank/refuse decision on **7.2%**. The
substitution is not cosmetic in this codebase.*

**AND THE DIAGNOSTIC THAT WOULD HAVE CAUGHT G2 IN MINUTES, WHICH THIS BUILD MUST PRINT BEFORE ANY
VERDICT IS READ:**
1. **the DISTRIBUTION of the error signal** -- how many distinct values does it actually take?
2. **the FIRING RATE at the chosen threshold** -- `skip` must not be 0.00 or 1.00.
3. **a POSITIVE CONTROL** -- an input that MUST produce a large error (a deliberate anomaly) and one
   that must not. *G2 shipped without one and a dead gate looked like a null result.*

## WHAT WOULD MAKE IT A REAL RESULT RATHER THAN A DEMO

- **A CAN-FAIL DISCRIMINATOR ON A HELD-OUT TASK**, scored against the strongest floor actually RUN
  on the same population -- not against chance. *E2's own evidence line shows why: maintenance
  0.4625 / coref 0.5825 / overwrite 0.4508 look strong against **chance 0.05** and are recorded as
  **LOCALIZED_WALL, "floored and failing"** against a **ref_span ceiling of 0.98**.*
- **SEEDS, AND `tools/replication_gate.py` ON THE RESULT.** Tonight a single-seed win was withdrawn
  on its second seed; the gate exists to make that automatic.
- **AN INFORMATION-FREE VERSION OF THE WINNING ARM** -- if a random error signal segments as well,
  the mechanism is not the cause.

## ⚖️ THE HONEST CASE *AGAINST* DOING THIS

**It does not obviously fix the thing four routes identified.** The bottleneck is that **nothing
reads the banked meanings**. A coherence monitor gives the system a *use* for its situation
register -- which is the selection loop philosophy demands -- **but the banked GROUNDED_MEANING facts
still sit outside that loop unless they are wired into the prediction.** *If this is built and the
meanings are still not consumed, the gap survives the build.* **That connection must be part of the
design, not an afterthought.**

**Also: `PHASE-B NOTE` in `ORGAN_MAP` records that the human baseline here is weak -- 40-50% of
subjects miss a controlled semantic anomaly (Moses illusion).** An always-on engineered check can
**structurally beat** the brain here. *That is an opportunity, and it is also a warning: beating a
40% human baseline is not evidence of comprehension.*

## TLDR

Last turn I told you the missing piece was big, because it needed a second component we do not have.
**I checked, and I was wrong in a useful direction.**

That second component — the running mental picture of what the text is about — **already exists in
our system and is running right now.** What is missing is only the part that notices when a new
sentence does not fit the picture. So the job is smaller and much better defined than I said: **add
the surprise signal to a machine that already keeps the picture.**

There is one trap, and we have already fallen into it once. A previous attempt at a surprise signal
threw away *how big* the surprise was and kept only its direction — and consequently never triggered,
not once. **So the first requirement is that the signal keeps its size**, and the build must print
how often it fires before anyone reads its result.

**And the honest argument against doing it at all:** the deep problem is that nothing in the system
ever reads the meanings it writes down. Giving it a sense of surprise about *sentences* does not
automatically make it consult its *word meanings*. If we build this and that connection is not made
deliberately, the original problem survives untouched.

## QUESTIONS

None. This is a design brief for a decision already taken, not a new fork.

## NEXT STEPS

1. **This is cell-authoring work** (`experiments/*.py`, smoke-gated) -- a different job from the
   main thread, and deliberately not started here.
2. **Whoever picks it up: read `ORGAN_MAP` E2 and F5 and G2 together.** The register, the missing
   error signal, and the recorded reason the last attempt died are three entries in one file.
3. **Design the meaning-consumption link IN**, or the build will not touch the bottleneck.

---

## ✅ THE MEANING-CONSUMPTION LINK IS **ARCHITECTURALLY AVAILABLE TODAY** -- AND ALREADY EXERCISED

The brief above ends by warning that this build will not touch the bottleneck unless banked meanings
are wired into the prediction. **That connection point exists, is live, and is already used.**

`hdlab/situation_model_accumulate.py:301`:

```
def bind_filler(self, entity, role, content_vec)   # bind a role to an ARBITRARY content vector
def decode_filler(self, entity, role)              # unbind it back out
```

**It is not hypothetical.** `hdlab/goal_outcome_relation_grounded.py` binds **word vectors** as
fillers in four places (`:144`, `:311`, `:314`, `:414`), with a verification witness in
`verification/test_three_tier_loop_e2e.py:98`. The module's own docstring says why the API exists:
*"since the goal_outcome_relation ablation needs to carry an **OPEN-vocabulary** [content]"*.

**➡️ SO A TERM'S BANKED MEANING CAN BE BOUND INTO THE RUNNING REGISTER AS A FILLER, WHICH PUTS IT
INSIDE THE PREDICTION AND THEREFORE INSIDE THE ERROR SIGNAL.** *That is the selection loop the
philosophy demands and the read-back gap lacks -- and it needs no new machinery, only wiring.*
**A wrong meaning would then produce a wrong prediction, an error, and pressure to revise.**

### ⚠️ AND THE CONSTRAINT, WHICH IS IN THE SAME DOCSTRING AND IS A REAL DESIGN LIMIT

> *"`unbind(bind(v,r),r) = v * r * conj(r) = v`, since `|r| = 1`, so `decode_filler` after
> **exactly one** `bind_filler` call on that role is a **lossless passthrough**, not noise."*

**LOSSLESS FOR ONE FILLER PER ROLE. Bundle several meanings onto the same role and the decode
becomes noisy** -- the ordinary superposition-capacity limit. **So the design cannot simply pour
every banked meaning into one register slot.** *It needs either one role per meaning-slot, or an
explicit capacity budget with the crosstalk measured -- and "measure the crosstalk before trusting
the decode" is exactly the check this codebase has skipped before.*

**➡️ THE BRIEF'S OPEN QUESTION IS THEREFORE ANSWERED: the link is available, it is tested, and its
capacity limit is documented. It should be designed in from the start rather than bolted on.**

### ⛔ AND THE CAPACITY CONSTRAINT I JUST IMPOSED IS **ALREADY SOLVED BY THE DEFAULT** -- MEASURED, IN A LANDED CELL

I was about to measure the crosstalk. **I read the constructor first, and it had already been
done -- better than I would have done it.** `make_situation_register`'s docstring records
`exp_situation_model_multibank_capacity_v1`, sweeping `n_events` in {64, 96, 128, 192, 256}:

| backend | decode self-consistency across the sweep |
|---|---|
| **`multibank_8`** -- and it is **the DEFAULT** | **[1.0000, 0.9992]** -- holds **>=0.999 at 256 events/entity** |
| flat register | [0.9781, **0.6547**] -- degrades badly under load |

*"Strictly >= flat at every swept load ... there is no regime in the measured sweep where flat beats
multibank_8, so multibank is a safe default, not a scale-vs-small-scale tradeoff."*

**➡️ SO "ONE ROLE PER MEANING-SLOT, OR MEASURE THE CROSSTALK" IS AN OVER-CONSTRAINT I IMPOSED ONE
TURN AGO ON STALE INFORMATION.** The lossless-for-one-filler caveat is real for the **flat**
register; **the shipped default holds 256 events per entity at >=0.999.** *The design can bundle
many meanings per entity.*

**AND THE DOCSTRING'S OWN HONEST SCOPE MATTERS TOO:** *"at current pilot scale (bundle-load ~2)
multibank and flat decode IDENTICALLY ... Switching the default is NOT claimed to lift current
comprehension accuracy; it is capacity-headroom future-proofing."* **So capacity is not currently a
binding constraint at all -- neither backend is under stress at present loads.**

**🔑 FIFTH TIME TONIGHT THE ANSWER WAS ALREADY IN AN ARTIFACT -- AND THE FIRST TIME I CAUGHT IT
BEFORE SPENDING THE COMPUTE.** *The previous four were found after the fact: two unscored audit
samples, a cell's own floor_note, a balance table nobody read. This one was caught by reading the
constructor docstring before writing the diagnostic. That is the habit working prospectively rather
than as an autopsy.*
