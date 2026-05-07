#!/usr/bin/env python3
import re
import argparse
import csv
from pathlib import Path
from collections import Counter

# icons for display
ICONS = {
    "Green": "🟢",
    "Yellow": "🟡",
    "Red": "🔴"
}

def safe_float(value, default, missing_flags):
    if value is None:
        missing_flags.append(True)
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        missing_flags.append(True)
        return default

def safe_int(value, default, missing_flags):
    if value is None:
        missing_flags.append(True)
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        missing_flags.append(True)
        return default

def classify_metrics(core, allow, disall, bad_contacts, cis, nres, mode="exp"):
    """Classify model quality according to mode (exp vs af), ignoring bond lengths/angles and G-factor."""

    core_allow = core + allow
    bc_per100 = (bad_contacts / nres) * 100 if nres > 0 else bad_contacts

    if mode == "exp":
        # Experimental structure thresholds (stricter)
        if (core >= 75 and core_allow >= 95 and disall <= 0.5 and 
            bc_per100 <= 2 and cis <= 0.01 * nres):
            return "Green"
        elif (core >= 65 and core_allow >= 90 and disall <= 2 and 
              bc_per100 <= 5 and cis <= 0.05 * nres):
            return "Yellow"
        else:
            return "Red"

    elif mode == "af":
        # AlphaFold/homology thresholds (looser)
        if (core >= 70 and core_allow >= 90 and disall <= 5 and 
            bc_per100 <= 5):
            return "Green"
        elif (core >= 60 and core_allow >= 85 and disall <= 10 and 
              bc_per100 <= 10):
            return "Yellow"
        else:
            return "Red"

    else:
        raise ValueError(f"Unknown mode: {mode}")

def parse_procheck_summary(file_path, mode):
    text = Path(file_path).read_text()
    missing_flags = []

    res_match = re.search(r"(\d+)\s+residues", text)
    nres = safe_int(res_match.group(1) if res_match else None, 0, missing_flags)

    rama_match = re.search(
        r"Ramachandran plot:\s+([\d.]+)% core\s+([\d.]+)% allow\s+([\d.]+)% gener\s+([\d.]+)% disall",
        text
    )
    core = safe_float(rama_match.group(1) if rama_match else None, 0, missing_flags)
    allow = safe_float(rama_match.group(2) if rama_match else None, 0, missing_flags)
    gener = safe_float(rama_match.group(3) if rama_match else None, 0, missing_flags)
    disall = safe_float(rama_match.group(4) if rama_match else None, 100, missing_flags)

    bad_match = re.search(r"Bad contacts:\s+(\d+)", text)
    bad_contacts = safe_int(bad_match.group(1) if bad_match else None, 0, missing_flags)

    cis_match = re.search(r"(\d+)\s+cis-peptides", text)
    cis = safe_int(cis_match.group(1) if cis_match else None, 0, missing_flags)

    classification = classify_metrics(core, allow, disall, bad_contacts, cis, nres, mode=mode)
    missing_values = "Yes" if missing_flags else "No"

    return {
        "File": Path(file_path).name,
        "Residues": nres,
        "Core%": core,
        "Allow%": allow,
        "Generous%": gener,
        "Disallowed%": disall,
        "BadContacts": bad_contacts,
        "BadContacts_per100": round((bad_contacts/nres)*100, 2) if nres > 0 else bad_contacts,
        "CisPeptides": cis,
        "Classification": classification,
        "MissingValues": missing_values
    }

def main():
    parser = argparse.ArgumentParser(description="Classify PROCHECK summary outputs into Green/Yellow/Red")
    parser.add_argument("-i", "--inputs", nargs="+", required=True, help="Input PROCHECK summary files")
    parser.add_argument("-o", "--output", required=True, help="Output CSV file")
    parser.add_argument("--mode", choices=["exp", "af"], default="exp",
                        help="Classification mode: exp (experimental, strict) or af (AlphaFold/homology, loose). Default=exp")
    args = parser.parse_args()

    results = []
    for f in args.inputs:
        try:
            parsed = parse_procheck_summary(f, args.mode)
            results.append(parsed)
            icon = ICONS.get(parsed['Classification'], "")
            warn = " ⚠️ Missing values filled" if parsed["MissingValues"] == "Yes" else ""
            print(f"{icon} {parsed['File']}: {parsed['Classification']} "
                  f"(Core={parsed['Core%']}%, Allowed={parsed['Allow%']}%, "
                  f"Disallowed={parsed['Disallowed%']}%, BadContacts/100={parsed['BadContacts_per100']}){warn}")
        except Exception as e:
            print(f"⚠️ Error parsing {f}: {e}")

    # Count classification categories
    counts = Counter(r["Classification"] for r in results)
    summary_str = f"{ICONS['Green']} Green={counts.get('Green',0)}, " \
                  f"{ICONS['Yellow']} Yellow={counts.get('Yellow',0)}, " \
                  f"{ICONS['Red']} Red={counts.get('Red',0)}"
    print(f"\n📊 Summary: {summary_str}")

    summary_row = {
        "File": "SUMMARY",
        "Residues": "",
        "Core%": "",
        "Allow%": "",
        "Generous%": "",
        "Disallowed%": "",
        "BadContacts": "",
        "BadContacts_per100": "",
        "CisPeptides": "",
        "Classification": summary_str,
        "MissingValues": ""
    }
    results.append(summary_row)

    with open(args.output, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

if __name__ == "__main__":
    main()

