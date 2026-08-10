"""Build the DISTILLED PROCESS-PHYSICS CO-PARTICIPATION KB for the ProPara end-to-end culmination
test (the 07-14 foundation pivot: offline-distilled foundation, glass-box runtime).

LEAK-SAFETY (the crux): every fact here is a GENERAL, TYPE-LEVEL science rule about a PROCESS TYPE
(combustion consumes fuel + oxygen -> produces CO2 + ash + heat), independently verifiable from
world-knowledge, authored WITHOUT reading any TEST gold state grid. Process types were derived from
ProPara TRAIN paragraph topics (rock cycle, water cycle, erosion, sedimentation, fossilization,
photosynthesis, tectonics, oil/coal formation, digestion, electricity generation, sound, neural
signaling, decay, phase change, dissolution, nitrogen/carbon cycle) -- publicly-known middle-school
science, NOT ProPara-specific answers. NO per-paragraph (participant, step, effect) tuples appear.

Schema (matches the loop's typed-fact form): process -> {signature, consumes, produces, moves}.
The cell maps each TEST paragraph to a process by signature-keyword overlap, maps each participant
to a role by lexical overlap with the role lists, then emits (effect, trigger_verb_class) facts:
  consumes -> DESTROY, produces -> CREATE, moves -> MOVE.

Invoke:  python tools/benchmark_trap_check/build_propara_process_physics_kb_v1.py
Output:  data/benchmark_trap_check/propara_process_physics_kb_v1.json
"""
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(REPO_ROOT, "data", "benchmark_trap_check", "propara_process_physics_kb_v1.json")

# GENERAL process-physics facts (hand-authored middle-school science; type-level, not ProPara answers).
# signature = words that identify the process in text; consumes/produces/moves = role keywords.
PROCESSES = {
    "combustion": {
        "signature": ["burn", "burns", "burning", "combust", "fire", "flame", "ignite", "fuel"],
        "consumes": ["fuel", "wood", "oxygen", "coal", "gas", "gasoline", "paper", "oil"],
        "produces": ["ash", "smoke", "carbon", "dioxide", "co2", "heat", "energy", "soot"],
        "moves": ["smoke", "heat"]},
    "photosynthesis": {
        "signature": ["photosynthesis", "chloroplast", "stomate", "stomata", "leaf", "chlorophyll", "sunlight"],
        "consumes": ["carbon", "dioxide", "co2", "water"],
        "produces": ["glucose", "sugar", "oxygen", "starch", "food"],
        "moves": ["water", "light", "sunlight", "sap"]},
    "respiration": {
        "signature": ["respiration", "breathe", "breathing", "lung", "inhale", "exhale", "oxygen"],
        "consumes": ["oxygen", "glucose", "sugar", "food"],
        "produces": ["carbon", "dioxide", "co2", "energy", "water", "atp"],
        "moves": ["air", "oxygen", "blood"]},
    "water_cycle": {
        "signature": ["evaporate", "evaporates", "condense", "condenses", "precipitation", "rain",
                      "cloud", "vapor", "humidity"],
        "consumes": [],
        "produces": ["vapor", "cloud", "rain", "droplet", "snow"],
        "moves": ["water", "vapor", "moisture", "droplet", "rain", "cloud"]},
    "erosion_weathering": {
        "signature": ["erode", "erodes", "erosion", "weather", "weathering", "wear", "break", "wind"],
        "consumes": ["rock", "mountain", "cliff", "stone"],
        "produces": ["sediment", "soil", "silt", "sand", "particle", "gravel"],
        "moves": ["sediment", "rock", "particle", "sand", "soil", "silt"]},
    "sedimentation": {
        "signature": ["sediment", "settle", "settles", "deposit", "deposits", "layer", "gravity", "pile"],
        "consumes": [],
        "produces": ["sediment", "layer", "rock", "sedimentary"],
        "moves": ["sediment", "mud", "silt", "sand", "material"]},
    "fossilization": {
        "signature": ["fossil", "bury", "buried", "buries", "sediment", "bone", "organism", "dead",
                      "million", "years", "remains", "decay"],
        "consumes": ["organism", "plant", "animal", "bone", "tissue", "algae", "plankton", "body", "creature"],
        "produces": ["fossil", "oil", "mineral", "rock", "coal"],
        "moves": ["sediment", "mud"]},
    "igneous_rock_cycle": {
        "signature": ["magma", "lava", "melt", "melts", "cool", "cools", "crystallize", "volcano",
                      "igneous", "erupt", "molten"],
        "consumes": ["magma", "rock", "lava"],
        "produces": ["rock", "crystal", "lava", "stone", "mineral", "igneous"],
        "moves": ["magma", "lava", "rock"]},
    "hydrocarbon_formation": {
        "signature": ["oil", "coal", "petroleum", "pressure", "heat", "organic", "plankton", "peat", "gas"],
        "consumes": ["plant", "plankton", "algae", "organism", "peat", "matter", "bacteria"],
        "produces": ["oil", "coal", "gas", "petroleum", "hydrocarbon"],
        "moves": ["sediment", "oil"]},
    "digestion": {
        "signature": ["digest", "digestion", "stomach", "intestine", "enzyme", "swallow", "food", "eat"],
        "consumes": ["food", "meal", "nutrient"],
        "produces": ["nutrient", "waste", "energy", "feces"],
        "moves": ["food", "nutrient", "waste", "blood"]},
    "nitrogen_cycle": {
        "signature": ["nitrogen", "fix", "fixation", "ammonia", "nitrate", "nitrite", "bacteria"],
        "consumes": ["nitrogen", "ammonia"],
        "produces": ["ammonia", "nitrate", "nitrogen", "protein", "nitrite"],
        "moves": ["nitrogen"]},
    "carbon_cycle": {
        "signature": ["carbon", "atmosphere", "co2", "dioxide"],
        "consumes": ["carbon", "dioxide", "co2"],
        "produces": ["carbon", "oxygen", "carbohydrate"],
        "moves": ["carbon", "co2"]},
    "electricity_generation": {
        "signature": ["generator", "turbine", "electricity", "magnet", "current", "coil", "electron",
                      "wire", "dynamo", "power"],
        "consumes": ["fuel", "motion", "steam"],
        "produces": ["electricity", "current", "electron", "power", "voltage"],
        "moves": ["electron", "water", "magnet", "steam", "current", "energy"]},
    "sound_propagation": {
        "signature": ["sound", "vibrate", "vibration", "hear", "echo", "ear", "acoustic", "noise"],
        "consumes": [],
        "produces": ["sound", "echo", "vibration", "wave"],
        "moves": ["wave", "sound", "vibration"]},
    "neural_signaling": {
        "signature": ["neuron", "brain", "nerve", "synapse", "signal", "impulse", "brainstem", "receptor"],
        "consumes": [],
        "produces": ["signal", "impulse"],
        "moves": ["signal", "impulse", "information", "electron"]},
    "decomposition": {
        "signature": ["decay", "decompose", "rot", "rots", "decomposition", "microbe", "bacteria", "fungi"],
        "consumes": ["organism", "matter", "plant", "animal", "leaf", "corpse", "body"],
        "produces": ["nutrient", "soil", "compost", "humus"],
        "moves": []},
    "phase_change": {
        "signature": ["freeze", "freezes", "melt", "melts", "ice", "solid", "liquid", "boil", "solidify"],
        "consumes": [],
        "produces": ["ice", "water", "steam", "crystal"],
        "moves": ["water", "heat"]},
    "dissolution": {
        "signature": ["dissolve", "dissolves", "solution", "solute", "salt"],
        "consumes": ["salt", "solute", "sugar", "mineral"],
        "produces": ["solution"],
        "moves": ["water", "ion"]},
}

# 10 hand-VET'd facts (each is verifiable general science, NOT a ProPara per-instance answer):
HAND_VET = [
    "combustion CONSUMES fuel + oxygen -> PRODUCES CO2 + ash + heat (general chemistry).",
    "photosynthesis CONSUMES CO2 + water -> PRODUCES glucose + oxygen (general biology).",
    "respiration CONSUMES oxygen + glucose -> PRODUCES CO2 + energy + water (general biology).",
    "water cycle MOVES water; evaporation/condensation PRODUCES vapor/cloud/rain (general earth science).",
    "erosion/weathering CONSUMES rock -> PRODUCES + MOVES sediment/soil/silt (general geology).",
    "fossilization CONSUMES buried organisms (plants/plankton) -> PRODUCES fossils/oil/minerals (general geology).",
    "igneous rock cycle: magma/rock melts + cools -> PRODUCES rock/crystal; MOVES magma/lava (general geology).",
    "digestion CONSUMES food -> PRODUCES nutrients + waste; MOVES food/nutrients (general biology).",
    "electricity generation MOVES electrons/magnet -> PRODUCES current/electricity (general physics).",
    "sound propagation MOVES waves -> PRODUCES echoes (general physics).",
]


def main():
    kb = {
        "_meta": {
            "purpose": "distilled process-physics co-participation KB for ProPara end-to-end test",
            "leak_safety": "type-level general science, authored WITHOUT reading TEST gold grids; "
                           "process types derived from TRAIN topics + public middle-school science; "
                           "NO per-paragraph (participant, step, effect) tuples",
            "schema": "process -> {signature, consumes, produces, moves}; "
                      "consumes->DESTROY, produces->CREATE, moves->MOVE",
            "n_processes": len(PROCESSES),
            "hand_vet_general_science": HAND_VET,
        },
        "processes": PROCESSES,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)
    print(f"[done] {len(PROCESSES)} process types -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
