"""Guard MutateX's FoldX calls against loss of a declared metal during RepairPDB."""

import os
import shutil
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

from trim_bound_structure import COMPONENT_IDS


METALS = {"zn", "mg", "ca", "mn", "fe2", "fe3"}
REPAIR_LOG = "FoldXrun.log"
REPAIR_ERRORS = "Unrecognized_molecules.txt"


def missing_metals(pdb, expected):
    component_labels = {COMPONENT_IDS.get(label, label.upper()): label for label in expected}
    residues = defaultdict(set)
    with pdb.open() as handle:
        for line in handle:
            if line.startswith(("ATOM  ", "HETATM")):
                label = component_labels.get(line[17:20].strip())
                if label is not None:
                    residues[label].add(line[21:27])
    return [
        f"{label}: expected {count}, found {len(residues[label])}"
        for label, count in sorted(expected.items())
        if len(residues[label]) < count
    ]


def report_failure(pdb, repair_dir, problems, diagnostic_log):
    # Keep diagnostics outside the scan output directory, which Snakemake may
    # remove after a failed job.
    saved_dir = diagnostic_log.parent / f"{diagnostic_log.stem}_files" / repair_dir.name
    saved_dir.mkdir(parents=True, exist_ok=True)
    messages = [f"FoldX metal validation failed for {pdb}: {'; '.join(problems)}."]
    for name, label in [(REPAIR_LOG, "Repair log"), (REPAIR_ERRORS, "Repair error file")]:
        source = repair_dir / name
        if source.is_file():
            target = saved_dir / name
            shutil.copyfile(source, target)
            messages.append(f"{label}: {target}")
        else:
            messages.append(f"{label}: {source} (not generated)")
    message = "\n".join(messages)
    with diagnostic_log.open("a") as handle:
        handle.write(message + "\n")
    print(message, file=sys.stderr)


def validate_pdb(pdb, repair_dir, expected, diagnostic_log):
    problems = missing_metals(pdb, expected) if pdb.is_file() else ["repaired PDB is missing"]
    if problems:
        report_failure(pdb, repair_dir, problems, diagnostic_log)
    return not problems


def run_foldx(arguments):
    binary = os.environ["MUTATEX_REAL_FOLDX"]
    state = os.environ["MUTATEX_BINDING_STATE"]
    expected = Counter(label for label in state[:-len("_bound")].split("_") if label in METALS)
    if not expected:
        return subprocess.run([binary, *arguments]).returncode

    # MutateX uses this exact invocation for FoldX Suite 4 and 5.
    if len(arguments) != 2 or arguments[0] != "-f":
        raise ValueError("Expected MutateX to invoke FoldX with -f <runfile>")
    config = {}
    for line in Path(arguments[1]).read_text().splitlines():
        key, separator, value = line.partition("=")
        if separator:
            config[key.strip().lower()] = value.strip()
    command = config["command"].lower()
    if command not in {"repairpdb", "buildmodel"}:
        return subprocess.run([binary, *arguments]).returncode

    scan_dir = Path(os.environ["MUTATEX_SCAN_DIR"])
    diagnostic_log = Path(os.environ["MUTATEX_METAL_DIAGNOSTIC_LOG"])
    pdb_dir = Path(config.get("pdb-dir", "."))
    pdbs = [pdb_dir / name.strip() for name in config["pdb"].split(",") if name.strip()]
    if not pdbs:
        raise ValueError(f"No pdb inputs in {arguments[1]}")

    if command == "repairpdb":
        result = subprocess.run([binary, *arguments])
        if result.returncode:
            return result.returncode
        output_dir = Path(config.get("output-dir", ".")).resolve()
        checks = [
            validate_pdb(output_dir / f"{pdb.stem}_Repair.pdb", Path.cwd(), expected, diagnostic_log)
            for pdb in pdbs
        ]
        return 0 if all(checks) else 1

    # MutateX can reuse a repaired structure from an earlier run. Check the
    # actual BuildModel input even when no RepairPDB process was launched.
    checks = []
    for pdb in pdbs:
        repaired = pdb.resolve()
        repair_dir = repaired.parent
        if repair_dir.parent != scan_dir / "repair":
            matches = list((scan_dir / "repair").glob(f"*/{pdb.name}"))
            if len(matches) == 1:
                repair_dir = matches[0].parent
        checks.append(validate_pdb(repaired, repair_dir, expected, diagnostic_log))
    if not all(checks):
        return 1
    return subprocess.run([binary, *arguments]).returncode


if __name__ == "__main__":
    try:
        sys.exit(run_foldx(sys.argv[1:]))
    except (KeyError, OSError, ValueError) as error:
        sys.exit(f"FoldX metal validation could not complete: {error}")
