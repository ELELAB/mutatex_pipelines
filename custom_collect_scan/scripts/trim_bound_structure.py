"""Trim a bound PDB while retaining the cofactors declared in binding_state."""

import argparse
from collections import Counter, defaultdict
from pathlib import Path


# PDB Chemical Component Dictionary identifiers that differ from the CSV labels.
COMPONENT_IDS = {"nadh": "NAI", "fadh": "FDA", "fe3": "FE"}
RESIDUE_RECORDS = {"ATOM", "HETATM", "ANISOU", "TER"}


def trim_bound_structure(source, destination, start, end, binding_state):
    expected = Counter(binding_state[:-len("_bound")].split("_"))
    component_to_label = {
        COMPONENT_IDS.get(label, label.upper()): label for label in expected
    }
    model = 0
    protein_models = set()
    cofactors = defaultdict(set)
    retained = []

    for line in source.read_text().splitlines(keepends=True):
        record = line[:6].strip()
        if record == "MODEL":
            model += 1
        if record not in RESIDUE_RECORDS:
            retained.append(line)
            continue

        in_range = start <= int(line[22:26]) <= end
        if record == "ATOM" and in_range:
            protein_models.add(model)
        label = component_to_label.get(line[17:20].strip())
        if record == "HETATM" and label is not None:
            # Chain, residue number, and insertion code identify one ligand
            # residue, even if it has many atoms or alternate locations.
            cofactors[model, label].add(line[21:27])
            retained.append(line)
        elif in_range or (record == "ANISOU" and label is not None):
            retained.append(line)

    if not protein_models:
        raise ValueError(f"{source}: no protein ATOM records in residues {start}–{end}")

    for model in sorted(protein_models):
        for label, required in expected.items():
            found = len(cofactors[model, label])
            if found < required:
                raise ValueError(
                    f"{source}: {binding_state} requires {required} {label} residues "
                    f"but found {found} in model {model or 1}"
                )
    destination.write_text("".join(retained))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    parser.add_argument("start", type=int)
    parser.add_argument("end", type=int)
    parser.add_argument("binding_state")
    args = parser.parse_args()
    try:
        trim_bound_structure(args.source, args.destination, args.start, args.end, args.binding_state)
    except ValueError as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
