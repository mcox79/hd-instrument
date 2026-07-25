"""build_arc_science_typed_rules_v1 -- GENERATE a science-precise, self-VETTED typed-rule base for the
verification-by-derivation reasoner (hdlab/reasoner.py).

WHY: off-the-shelf commonsense KBs (ConceptNet/CSKG) + regex text-extraction supplied VACUOUS HUB-BRIDGES
(hub-present = non-discriminative; hub-removed = coverage collapse), not valid directional science rules,
so the reasoner could not fire (connectivity gate RED, COVERAGE_BOUND; atoms 29552-29555, 29559). This is
the PIVOT-authorized replacement supply: LLM-authored (this file), science-precise, self-vetted for
validity + directionality + SELECTIVITY (no mega-hubs).

FORMAT (matched to what the reasoner consumes DIRECTLY):
  DerivationReasoner(rows=[{"relation": R, "arg0": A, "arg1": B}, ...]) with R in LICENSED. The edge is
  DIRECTED arg0 -> arg1. arg0/arg1 are short text labels encoded by SemanticHDEncoder (GloVe+WordNet).
  This bypasses parse_tablestore_typed (which reads WorldTree TSV); the reasoner already accepts rows=.

NODE-MATCH CALIBRATION (the coverage crux): the reasoner maps QUESTION content words to rule-filler nodes
via cos >= tau_unify=0.85 using arc._content_words(text, min_len=4). Consequences the fillers respect:
  (1) fillers use CANONICAL SINGLE WORDS drawn from the ARC-Challenge high-frequency vocabulary (water,
      energy, heat, friction, evaporation, oxygen, sunlight, rotation, ...) so a question word matches at
      cos ~ 1.0. Multi-word fillers dilute the match against single question words and are avoided.
  (2) fillers are >= 4 chars (3-char words like sun/gas/air/ice/day are DROPPED from questions by min_len=4)
      -> use sunlight/solar, vapor/gases, wind/atmosphere, frozen/freezing, daytime/days instead.
  (3) directionality: given(stem) --fwd(<=2)--> meets choice --bwd(<=1)--; rules are authored in the true
      scientific causal/functional direction (process/cause = arg0 upstream, outcome/effect = arg1 down-
      stream), which is where a "what is the effect/result" answer sits. "why/what causes" answers sit
      upstream and are EXPECTEDLY lower-coverage (we do NOT add reverse edges -- that would destroy the
      directional selectivity the SHUFFLE_DIRECTION control exists to prove).

SELECTIVITY DESIGN: the graph is deliberately SPARSE + DIRECTED. Selectivity comes from topology, not from
filler specificity: a chain to the RIGHT answer exists because the specific directed edges connect it;
distractors (same-topic words) are in different components or not downstream. Scientific PRECISION is the
selectivity lever -- e.g. rotation->day but NOT rotation->year (rotation != revolution), so on the classic
"planet rotates faster" question only the "shorter day" answer derives. Multi-hop chains are authored
(rain->runoff->river->ocean ; heat->evaporation->vapor->cloud->rain ; weathering->erosion->sediment) so the
meet-in-middle search produces real >=2-step derivation traces.

SELF-VET (this file, programmatic): (a) every relation is LICENSED; (b) exact-duplicate directed edges
removed; (c) node in/out-degree computed and any node with total degree > HUB_MAX flagged (mega-hub guard);
(d) no self-loops. Per-rule scientific validity is asserted by authorship (each grouped + commented).

Contract: pure-stdlib generator; ASCII-only; deterministic; writes JSON to data/rules/. NOT banked as atoms.
Run: python data/rules/build_arc_science_typed_rules_v1.py
"""
from __future__ import annotations

import os
import json
from collections import defaultdict

LICENSED = ("CAUSE", "IFTHEN", "REQUIRES", "COUPLEDRELATIONSHIP", "SOURCEOF", "USEDFOR")
HUB_MAX = 12  # total (in+out) degree above which a node is flagged as a potential mega-hub

# Each entry: (RELATION, arg0, arg1). Directed arg0 -> arg1. Grouped by ARC topic; every rule is a
# scientifically valid, specific, directional statement. Fillers chosen from ARC-Challenge vocabulary
# (>=4 chars, canonical single words) to maximize node-match coverage.
RULES = [
    # ============================ FORCES & MOTION ============================
    ("COUPLEDRELATIONSHIP", "force", "acceleration"),   # F=ma: more force -> more acceleration
    ("COUPLEDRELATIONSHIP", "mass", "inertia"),         # more mass -> more inertia
    ("COUPLEDRELATIONSHIP", "speed", "distance"),       # faster -> more distance per time
    ("COUPLEDRELATIONSHIP", "speed", "momentum"),       # faster -> more momentum
    ("COUPLEDRELATIONSHIP", "mass", "momentum"),        # more mass -> more momentum
    ("CAUSE", "friction", "heat"),                      # friction generates heat
    ("CAUSE", "friction", "wear"),                      # friction causes wear
    ("IFTHEN", "friction", "slowing"),                  # friction slows moving objects
    ("CAUSE", "gravity", "weight"),                     # gravity gives weight
    ("CAUSE", "gravity", "falling"),                    # gravity causes objects to fall
    ("CAUSE", "gravity", "orbit"),                      # gravity holds bodies in orbit
    ("CAUSE", "push", "motion"),                        # a push starts motion
    ("CAUSE", "pull", "motion"),                        # a pull starts motion
    ("REQUIRES", "acceleration", "force"),              # changing motion requires a net force
    ("USEDFOR", "lever", "lifting"),                    # simple machines
    ("USEDFOR", "pulley", "lifting"),
    ("USEDFOR", "ramp", "lifting"),                     # inclined plane
    ("USEDFOR", "wheel", "rolling"),
    ("USEDFOR", "magnet", "attraction"),
    ("COUPLEDRELATIONSHIP", "rotation", "daytime"),     # faster rotation -> shorter day (rotation!=revolution)
    ("COUPLEDRELATIONSHIP", "revolution", "year"),      # orbital period sets the year

    # ============================ ENERGY ============================
    ("SOURCEOF", "sunlight", "energy"),
    ("SOURCEOF", "sunlight", "heat"),
    ("SOURCEOF", "food", "energy"),
    ("SOURCEOF", "battery", "energy"),
    ("SOURCEOF", "coal", "energy"),
    ("SOURCEOF", "solar", "electricity"),
    ("SOURCEOF", "wind", "electricity"),
    ("SOURCEOF", "coal", "electricity"),
    ("SOURCEOF", "generator", "electricity"),
    ("COUPLEDRELATIONSHIP", "height", "potential"),     # higher -> more potential energy
    ("COUPLEDRELATIONSHIP", "speed", "kinetic"),        # faster -> more kinetic energy
    ("CAUSE", "motion", "kinetic"),                     # motion is kinetic energy
    ("CAUSE", "falling", "kinetic"),                    # falling converts potential to kinetic
    ("CAUSE", "combustion", "heat"),
    ("CAUSE", "burning", "heat"),
    ("CAUSE", "burning", "light"),
    ("USEDFOR", "food", "energy"),
    ("USEDFOR", "sugar", "energy"),
    ("USEDFOR", "fuel", "energy"),

    # ============================ HEAT / THERMAL ============================
    ("CAUSE", "heat", "expansion"),                     # heating -> expansion
    ("CAUSE", "cooling", "contraction"),
    ("CAUSE", "heat", "melting"),
    ("CAUSE", "heat", "evaporation"),
    ("CAUSE", "cooling", "condensation"),
    ("CAUSE", "cooling", "freezing"),
    ("COUPLEDRELATIONSHIP", "temperature", "evaporation"),  # higher temp -> faster evaporation
    ("COUPLEDRELATIONSHIP", "temperature", "molecules"),    # higher temp -> faster molecular motion
    ("COUPLEDRELATIONSHIP", "temperature", "dissolving"),   # higher temp -> faster dissolving
    ("COUPLEDRELATIONSHIP", "temperature", "reaction"),     # higher temp -> faster reaction
    ("USEDFOR", "insulation", "warmth"),
    ("IFTHEN", "insulation", "warmth"),                 # insulation retains warmth
    ("CAUSE", "conduction", "heat"),                    # heat transfers by conduction
    ("CAUSE", "convection", "heat"),
    ("CAUSE", "radiation", "heat"),

    # ============================ STATES OF MATTER / PHASE CHANGE ============================
    ("CAUSE", "melting", "liquid"),
    ("CAUSE", "freezing", "solid"),
    ("CAUSE", "evaporation", "vapor"),
    ("CAUSE", "boiling", "vapor"),
    ("CAUSE", "condensation", "liquid"),
    ("CAUSE", "sublimation", "vapor"),
    ("IFTHEN", "heating", "melting"),                   # heat a solid -> melts
    ("IFTHEN", "cooling", "freezing"),
    ("CAUSE", "freezing", "expansion"),                 # water expands on freezing (specific!)

    # ============================ WATER CYCLE ============================
    ("CAUSE", "heat", "evaporation"),                   # (chain start; dup-safe, dedup below)
    ("CAUSE", "evaporation", "vapor"),
    ("CAUSE", "cooling", "condensation"),
    ("CAUSE", "condensation", "clouds"),
    ("CAUSE", "clouds", "precipitation"),
    ("SOURCEOF", "precipitation", "rain"),
    ("CAUSE", "precipitation", "rain"),
    ("CAUSE", "rain", "runoff"),
    ("SOURCEOF", "runoff", "river"),
    ("SOURCEOF", "river", "ocean"),
    ("SOURCEOF", "glacier", "river"),

    # ============================ WEATHER / EARTH-SPACE ============================
    ("CAUSE", "heat", "wind"),                          # uneven heating drives wind
    ("CAUSE", "wind", "waves"),
    ("CAUSE", "wind", "erosion"),
    ("CAUSE", "tilt", "seasons"),                       # axial tilt causes seasons
    ("CAUSE", "moon", "tides"),
    ("CAUSE", "gravity", "tides"),
    ("CAUSE", "earthquake", "tsunami"),
    ("CAUSE", "volcano", "lava"),
    ("CAUSE", "volcano", "ash"),
    ("CAUSE", "weathering", "erosion"),
    ("CAUSE", "erosion", "sediment"),
    ("CAUSE", "sediment", "sedimentary"),              # sediment -> sedimentary rock
    ("CAUSE", "pressure", "metamorphic"),              # heat+pressure -> metamorphic rock
    ("CAUSE", "cooling", "igneous"),                   # cooling magma -> igneous rock
    ("SOURCEOF", "magma", "lava"),
    ("CAUSE", "rotation", "daytime"),                  # rotation causes day/night cycle
    ("CAUSE", "orbit", "seasons"),                     # orbit + tilt; specific pairing kept sparse
    ("SOURCEOF", "ocean", "clouds"),                   # oceans are the water source for clouds

    # ============================ LIGHT / OPTICS ============================
    ("CAUSE", "opaque", "shadow"),                     # opaque object blocks light -> shadow
    ("USEDFOR", "mirror", "reflection"),
    ("USEDFOR", "lens", "refraction"),
    ("CAUSE", "refraction", "bending"),                # refraction bends light
    ("CAUSE", "prism", "spectrum"),                    # prism disperses into spectrum
    ("SOURCEOF", "sunlight", "light"),
    ("REQUIRES", "vision", "light"),                   # seeing requires light
    ("REQUIRES", "sight", "light"),
    ("CAUSE", "light", "reflection"),

    # ============================ ELECTRICITY / MAGNETISM ============================
    ("REQUIRES", "current", "circuit"),                # current needs a closed circuit
    ("REQUIRES", "circuit", "conductor"),
    ("USEDFOR", "conductor", "current"),
    ("USEDFOR", "copper", "current"),                  # copper conducts electricity
    ("USEDFOR", "wire", "current"),
    ("IFTHEN", "insulator", "resistance"),             # insulator blocks current
    ("SOURCEOF", "battery", "current"),
    ("CAUSE", "current", "magnetism"),                 # electromagnet
    ("CAUSE", "current", "heat"),                      # resistive heating
    ("CAUSE", "current", "light"),                     # bulb
    ("COUPLEDRELATIONSHIP", "voltage", "current"),     # Ohm's law
    ("CAUSE", "magnet", "force"),
    ("CAUSE", "friction", "static"),                   # friction -> static charge
    ("CAUSE", "static", "attraction"),

    # ============================ MATTER / CHEMISTRY BASICS ============================
    ("CAUSE", "mixing", "mixture"),
    ("CAUSE", "reaction", "product"),                  # chemical reaction -> new substance
    ("CAUSE", "reaction", "heat"),                     # exothermic reaction releases heat
    ("REQUIRES", "burning", "oxygen"),                 # combustion needs oxygen
    ("REQUIRES", "rusting", "oxygen"),
    ("REQUIRES", "rusting", "water"),
    ("CAUSE", "rusting", "corrosion"),
    ("CAUSE", "acid", "corrosion"),
    ("CAUSE", "dissolving", "solution"),               # dissolving -> solution
    ("REQUIRES", "dissolving", "solvent"),
    ("SOURCEOF", "evaporation", "salt"),               # evaporating seawater leaves salt

    # ============================ ECOSYSTEMS / FOOD CHAINS ============================
    ("REQUIRES", "photosynthesis", "sunlight"),
    ("REQUIRES", "photosynthesis", "water"),
    ("REQUIRES", "photosynthesis", "carbon"),          # CO2 (single distinctive word)
    ("CAUSE", "photosynthesis", "oxygen"),             # produces oxygen
    ("CAUSE", "photosynthesis", "sugar"),              # produces glucose/sugar
    ("REQUIRES", "plants", "sunlight"),
    ("REQUIRES", "plants", "water"),
    ("REQUIRES", "plants", "soil"),
    ("SOURCEOF", "plants", "food"),                    # producers
    ("SOURCEOF", "producer", "food"),
    ("REQUIRES", "animals", "food"),
    ("REQUIRES", "animals", "oxygen"),
    ("REQUIRES", "animals", "water"),
    ("REQUIRES", "fish", "water"),
    ("REQUIRES", "life", "water"),
    ("REQUIRES", "growth", "nutrients"),
    ("REQUIRES", "growth", "energy"),
    ("COUPLEDRELATIONSHIP", "predator", "prey"),       # more predators -> fewer prey (coupled)
    ("COUPLEDRELATIONSHIP", "population", "resources"), # more population -> more resource demand
    ("CAUSE", "competition", "extinction"),
    ("CAUSE", "overpopulation", "competition"),
    ("CAUSE", "decomposition", "nutrients"),           # decomposers release nutrients
    ("CAUSE", "decay", "decomposition"),
    ("SOURCEOF", "decomposer", "nutrients"),
    ("CAUSE", "pollution", "harm"),
    ("CAUSE", "drought", "shortage"),                  # drought -> water shortage

    # ============================ LIFE CYCLES / GENETICS / ADAPTATION ============================
    ("CAUSE", "genes", "traits"),                      # genes determine traits
    ("CAUSE", "mutation", "variation"),
    ("CAUSE", "variation", "adaptation"),
    ("COUPLEDRELATIONSHIP", "adaptation", "survival"), # better adaptation -> more survival
    ("USEDFOR", "camouflage", "protection"),
    ("USEDFOR", "camouflage", "hiding"),
    ("USEDFOR", "migration", "survival"),
    ("USEDFOR", "hibernation", "survival"),
    ("CAUSE", "adaptation", "survival"),
    ("SOURCEOF", "parents", "offspring"),              # reproduction
    ("CAUSE", "reproduction", "offspring"),

    # ============================ BODY STRUCTURES / FUNCTION (USEDFOR) ============================
    ("USEDFOR", "roots", "absorption"),                # roots absorb water
    ("USEDFOR", "roots", "water"),
    ("USEDFOR", "leaves", "photosynthesis"),
    ("USEDFOR", "stems", "support"),
    ("USEDFOR", "wings", "flight"),
    ("USEDFOR", "feathers", "flight"),
    ("USEDFOR", "feathers", "warmth"),
    ("USEDFOR", "gills", "breathing"),
    ("USEDFOR", "lungs", "breathing"),
    ("USEDFOR", "heart", "circulation"),
    ("USEDFOR", "muscles", "movement"),
    ("USEDFOR", "bones", "support"),
    ("USEDFOR", "skeleton", "support"),
    ("USEDFOR", "stomach", "digestion"),
    ("USEDFOR", "brain", "control"),

    # ============================ DISEASE / HEALTH ============================
    ("CAUSE", "bacteria", "disease"),
    ("CAUSE", "virus", "disease"),
    ("CAUSE", "parasite", "disease"),
    ("CAUSE", "infection", "disease"),
    ("CAUSE", "disease", "death"),
    ("CAUSE", "exercise", "strength"),
    ("REQUIRES", "survival", "water"),
    ("REQUIRES", "survival", "food"),
    ("REQUIRES", "survival", "oxygen"),

    # ============================ FIRE / COMBUSTION (classic multi-requirement) ============================
    ("REQUIRES", "fire", "oxygen"),
    ("REQUIRES", "fire", "fuel"),
    ("REQUIRES", "fire", "heat"),
    ("CAUSE", "fire", "smoke"),
    ("CAUSE", "fire", "ash"),

    # ============================ ATOMIC / PARTICLE (chemistry) ============================
    ("SOURCEOF", "atoms", "matter"),                   # atoms make up matter
    ("CAUSE", "charge", "attraction"),                 # opposite charges attract
    ("CAUSE", "reaction", "endothermic"),              # reactions can absorb heat
    ("REQUIRES", "endothermic", "heat"),               # endothermic absorbs heat
    ("CAUSE", "exothermic", "heat"),                   # exothermic releases heat
    ("REQUIRES", "combustion", "oxygen"),

    # ============================ EXTINCTION / POPULATION DYNAMICS ============================
    ("CAUSE", "habitat", "survival"),                  # habitat loss threatens survival (habitat->survival)
    ("CAUSE", "predation", "extinction"),
    ("CAUSE", "disease", "extinction"),
    ("CAUSE", "extinction", "loss"),

    # ============================ INFLECTION ALIASES (deterministic node-match hedge) ============================
    # ARC uses singular AND plural; explicit alias nodes match at cos~1.0 (avoids tau=0.85 inflection miss).
    ("REQUIRES", "plant", "sunlight"),
    ("REQUIRES", "plant", "water"),
    ("SOURCEOF", "plant", "food"),
    ("REQUIRES", "animal", "food"),
    ("REQUIRES", "animal", "oxygen"),
    ("USEDFOR", "leaf", "photosynthesis"),
    ("USEDFOR", "root", "water"),
    ("USEDFOR", "wing", "flight"),
    ("USEDFOR", "gill", "breathing"),
    ("USEDFOR", "lung", "breathing"),
    ("USEDFOR", "muscle", "movement"),
    ("USEDFOR", "bone", "support"),
    ("COUPLEDRELATIONSHIP", "temperature", "molecule"),
    ("CAUSE", "wind", "wave"),
    ("SOURCEOF", "sunlight", "energy"),                # dup-safe
    ("CAUSE", "mixing", "mixtures"),
    ("CAUSE", "reaction", "products"),
    ("CAUSE", "genes", "trait"),
    ("CAUSE", "mutation", "variations"),
    ("CAUSE", "decomposition", "nutrient"),
    ("REQUIRES", "growth", "nutrient"),

    # ============================ ENERGY TRANSFORMATION (common ARC frame) ============================
    ("CAUSE", "sunlight", "photosynthesis"),           # light drives photosynthesis
    ("SOURCEOF", "photosynthesis", "sugar"),
    ("SOURCEOF", "photosynthesis", "oxygen"),
    ("CAUSE", "evaporation", "cooling"),               # evaporative cooling
    ("CAUSE", "vibration", "sound"),                   # vibration produces sound
    ("SOURCEOF", "vibration", "sound"),
    ("CAUSE", "sound", "hearing"),
    ("REQUIRES", "hearing", "sound"),
    ("CAUSE", "earthquake", "damage"),
    ("CAUSE", "flooding", "erosion"),
    ("CAUSE", "glacier", "erosion"),
    ("CAUSE", "erosion", "canyon"),                    # rivers/erosion carve canyons
    ("SOURCEOF", "erosion", "sediment"),               # dup-safe
]


def build():
    seen = set()
    rows = []
    dropped_dupes = 0
    self_loops = 0
    bad_rel = 0
    for rel, a, b in RULES:
        if rel not in LICENSED:
            bad_rel += 1
            raise ValueError(f"unlicensed relation {rel} in ({a},{b})")
        a = a.strip().lower()
        b = b.strip().lower()
        if a == b:
            self_loops += 1
            continue
        key = (rel, a, b)
        if key in seen:
            dropped_dupes += 1
            continue
        seen.add(key)
        rows.append({"relation": rel, "arg0": a, "arg1": b})

    # degree / hub audit
    out_deg = defaultdict(int)
    in_deg = defaultdict(int)
    per_rel = defaultdict(int)
    for r in rows:
        out_deg[r["arg0"]] += 1
        in_deg[r["arg1"]] += 1
        per_rel[r["relation"]] += 1
    nodes = set(out_deg) | set(in_deg)
    tot_deg = {n: out_deg[n] + in_deg[n] for n in nodes}
    hubs = sorted([(n, d) for n, d in tot_deg.items() if d > HUB_MAX], key=lambda t: -t[1])
    top_deg = sorted(tot_deg.items(), key=lambda t: -t[1])[:15]

    meta = {
        "n_rules": len(rows),
        "n_nodes": len(nodes),
        "per_relation": dict(sorted(per_rel.items())),
        "dropped_exact_dupes": dropped_dupes,
        "self_loops_dropped": self_loops,
        "hub_max_threshold": HUB_MAX,
        "flagged_hubs_over_threshold": hubs,   # SELECTIVITY guard: should be empty or tiny
        "top15_degree_nodes": top_deg,
        "licensed": list(LICENSED),
        "format": "list[{relation, arg0, arg1}] -> DerivationReasoner(rows=...); directed arg0->arg1",
        "provenance": "LLM-authored science-precise supply; replaces vacuous ConceptNet/CSKG hub-bridges",
    }
    return rows, meta


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    rows, meta = build()
    out = {"meta": meta, "rules": rows}
    path = os.path.join(here, "arc_science_typed_rules_v1.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(out, f, indent=2)
    os.replace(tmp, path)
    print(f"wrote {len(rows)} rules to {path}")
    print(f"per_relation = {meta['per_relation']}")
    print(f"n_nodes = {meta['n_nodes']}; flagged_hubs(>{meta['hub_max_threshold']}) = {meta['flagged_hubs_over_threshold']}")
    print(f"top-degree nodes = {meta['top15_degree_nodes']}")
