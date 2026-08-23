# THE SHELVE HALF OF THE DURABILITY GATE IS HOLLOW: 24 OF 42 SAY NOTHING AT ALL

**2026-08-23, strategy session.** Found by following one row rather than by auditing the registry --
a shelved 11x result whose entry explained WHY it was shelved and never said what would bring it
back. The question was whether that is one row or the norm.

---

## 1. THE RULE, AND THE MEASUREMENT

**CLAUDE.md, verbatim:** *"WIRE (promote to `hdlab/`, register in the registry, target + step noted)
or **SHELVE (explicit revival criteria)** -- nothing stays in limbo."*

`data/capability_registry.jsonl`, 212 rows:

| `gate_decision` | count |
|---|---|
| `WIRE` | 124 |
| **`SHELVE`** | **42** |
| `ALREADY_WIRED` / `WIRED` | 27 |
| everything else | 19 |

**OF THE 42 SHELVES:**

| | count | share |
|---|---|---|
| 🔻 **`gate_decision_target` COMPLETELY EMPTY** | **24** | **57%** |
| carries some text but **no forward-looking language** | 13 | 31% |
| ✅ names a condition that would bring it back | **5** | **12%** |

🚨 **THE 57% NEEDS NO DETECTOR AND CARRIES NO INTERPRETATION: the field is empty.** Twenty-four
capabilities are recorded as deliberately shelved with **nothing whatsoever** about what would revive
them.

*(The 31% is keyword-based and therefore soft -- it distinguishes forward-looking phrasing from
explanatory phrasing, and could miss a criterion worded unusually. **Detector controlled both ways:**
three revival-shaped probes match, three explanation-shaped probes do not. Median target length among
rows that have text is 176 characters, so these are notes, not stubs.)*

---

## 2. WHY THIS IS THE GATE FAILING RATHER THAN PAPERWORK MISSING

**A shelve is supposed to be a DECISION WITH A TRIGGER.** Its whole function is that a capability
which is good but not yet useful can be set down and *found again by the condition that makes it
useful*. Without the trigger, a shelve is indistinguishable from abandonment -- and worse, it LOOKS
like the gate was satisfied, because the row carries a `gate_decision`.

**THIS PROJECT HAS ALREADY PAID FOR EXACTLY THIS.** The row that started this audit says so in its
own words: *"registered by director 2026-08-21, **after the owner had to recall this work from memory
twice** because the registry-first check returns nothing for it."* An 11x lift on the hard population
was recovered by human memory, not by the mechanism built to prevent that.

**AND THE SHELVED SET IS NOT JUNK.** It includes `hdlab_encoder_cluster_vwfa_ppmi_composed_v3`,
`binder_direct_supply_grounding`, `entity_slot_gate_cross_boundary_v1`, `reasoner_composed_entry_arc_program`,
`coherence_selector_text_transfer` -- **organs on the goal-bearing line, set down with no stated way
back.**

---

## 3. THE SPLIT THAT MAKES THIS ACTIONABLE

**These are two different jobs and conflating them is why nothing has been done:**

- 🔧 **FORWARD (cheap, mechanical, mine):** `capability_registry_audit.py` should FLAG a `SHELVE` row
  whose `gate_decision_target` is empty. **A gate that accepts a blank field is not enforcing its own
  rule**, and this is the repo's standing escalation -- *when a caution written as prose is violated,
  move it into the code path where the unsafe usage is unrepresentable*.
- 🧠 **RETROACTIVE (24 judgements, NOT mechanical):** each empty row needs someone who knows that
  capability to say what would revive it. **This cannot be batch-filled** -- a generated placeholder
  would satisfy the check while making the situation worse, because it would look answered.

⚠️ **I AM NOT DOING THE RETROACTIVE HALF IN THIS SESSION AND WILL NOT FAKE IT.** Writing 24 plausible
revival criteria without knowing the capabilities is precisely the failure this note is about.

---

## 4. WHAT MAY AND MAY NOT BE QUOTED

- ✅ **MAY: 24 of 42 SHELVE rows have an empty `gate_decision_target`.** Directly read from the file.
- ✅ **MAY: 5 of 42 name a revival condition** by keyword detection with controls both ways.
- 🚫 **MAY NOT: "37 of 42 shelves are abandoned."** 13 of those carry real explanatory text and some
  may encode a criterion the keyword test cannot see. **The unambiguous number is 24.**
- 🚫 **MAY NOT:** any claim that the shelved capabilities are weak. **The gate decision says nothing
  about quality** -- the row that started this shelved an 11x result explicitly *"NOT because it is
  weak"*.

---

## TLDR

We have a rule that when a piece of work is good but not yet needed, you put it on the shelf **and
write down what would bring it back**. Otherwise "shelved" just means "lost politely."

I checked all forty-two shelved items. **Twenty-four have nothing written at all** — not a vague
note, an empty field. Only five say what would revive them.

This is not a filing complaint. The shelf includes real components on the main line of work, and we
have already paid for it once: a result that was eleven times better on the hardest cases had to be
remembered by you, personally, twice, because searching the register found nothing.

There are two fixes and they are different jobs. The mechanical one is mine and it is small — the
audit that checks this register should refuse to accept a blank field. The other is twenty-four
individual judgements about what each component would need to come back, and that needs someone who
knows each one. **I am not going to invent them, because a plausible-sounding placeholder would pass
the check and make things worse.**

## QUESTIONS

None. `Q115` and `Q116` remain open.

## NEXT STEPS

1. **Make `capability_registry_audit.py` flag an empty `gate_decision_target` on a `SHELVE` row.**
   Cheap, mine, prevents the next one.
2. **The 24 existing blanks need per-capability judgement** -- a candidate for the problems list, but
   only if someone will actually do the thinking rather than fill the field.
3. *The detector's soft 31% could be tightened, but the unambiguous 57% is already enough to act on.*
