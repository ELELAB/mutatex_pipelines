## Overview

This directory contains a snakemake-based pipeline for peptide mutation scanning runs with `MutateX`[^Tiberti]. This protocol predicts changes of folding free energy upon mutation for each residue of a given list of mutations provided as input. Each residue is mutated to a list of residue types depending on the mutations found in the corresponding input dataset. 

Before running `MutateX`, the pipeline performs a PROCHECK quality assessment on the trimmed structure. The PROCHECK summary is classified as Green, Yellow, or Red. Green structures proceed normally, Yellow structures continue with a warning, and Red structures stop before the MutateX scan.

If the same protein is provided in multiple rows of `models.csv`, corresponding to different trimmed regions or domains, the pipeline also generates an additional aggregated output table. The domain-specific `MutateX` outputs are kept unchanged, and the aggregated tables are written under `mutatex_runs/aggregate/`.

## Description of the directory content:

### {coding_gene} folder

These folders hold per-protein pipeline outputs. Set `pdb_file` in the models CSV to an absolute path or a path relative to the working directory. The workflow copies that file into `structure_selection/{database}/`. Free AFDB rows may leave `pdb_file` blank to download the model.

### Snakefile

The main and example directories contain identical Snakefiles. To run the example elsewhere, copy the whole `example/` directory so its configuration, structures, and helper scripts stay together.

### Table

The `models.csv` file is a comma separated file containing all the information needed to generate a consistent output directory structure, as well as to provide the correct input files to `MutateX` processing tools.

`csv` description:

|Entry|Meaning|Example|
|---|---|---|
|`coding_gene`|Name of the gene coding for the peptide of interest|TP53|
|`prot_id`|Protein identifier|P04637|
|`database`|Structure source (see allowed values below)|PDB|
|`start_res`|First residue to consider during the scan|91|
|`end_res`|Last residue to consider during the scan|289|
|`binding_state`|State or condition of the protein|zn_bound|
|`version`|Source-specific version or template identifier (see below)|2XWR|
|`pdb_file`|Input structure path (required except for free AFDB models)|P04637.pdb|

Both `database` and `version` are required. Use the source labels exactly as shown.

| `database` | Structure source | Required `version` |
|---|---|---|
| `AFDB` | AlphaFold Protein Structure Database | `v3`, `v4`, `v5`, or `v6`, matching the release used |
| `AF2` | Locally generated AlphaFold 2 model | `AF2` |
| `AF3` | AlphaFold 3 model | `AF3` |
| `PDB` | Experimental structure from the Protein Data Bank | A four-character PDB ID, such as `3PTB` |
| `AlphaFill` | Cofactor-bound model prepared using AlphaFill | `v4` for the AlphaFill-provided model, `v6` for a supplied AFDB v6 model, or `AF3` or `AF2` for a supplied AlphaFold model |
| `Mod` | Homology or other template-based model | The template's PDB ID for an experimental template, or `AFDB`, `AF2`, or `AF3` for a predicted template |

PDB IDs are checked for format only. Set `pdb_file` for every `AF2`, `AF3`, `Mod`, `PDB`, and `AlphaFill` row. For an `AFDB` model with a `binding_state` other than `free`, set `pdb_file` to a structure that already contains the cofactors.

The following examples show the source and version fields together with the trimming range. The TP53 and NPLOC4 structure files are bundled in `example/` and referenced by both example CSVs.

| `coding_gene` | `prot_id` | `database` | `start_res` | `end_res` | `version` |
|---|---|---|---:|---:|---|
| APC | P25054 | AF3 | 1 | 5 | AF3 |
| TP53 | P04637 | PDB | 91 | 289 | 2XWR |
| NPLOC4 | Q8TAT6 | Mod | 2 | 608 | AFDB |

For bound states, supply a PDB that already contains the declared cofactors as HETATM records. Trimming retains those cofactor residues even when their residue numbers lie outside the protein range. The workflow stops if fewer cofactor residues than declared are present. The workflow also checks the FoldX repaired PDB and the input to BuildModel for all declared cofactors, including metals and nonmetals such as ATP, ADP, NAD, and FAD. It counts distinct cofactor residues in both ATOM and HETATM records and stops before BuildModel if a declared cofactor is missing. The scan’s `*_foldx_cofactor.log` gives the expected and observed counts and the paths to the repair log and any `Unrecognized_molecules.txt` file.

For zinc, use `ZN` in the PDB residue-name field (columns 18–20). The trimmer looks at this field, so `ZN2` is not counted as zinc. Use `zn_bound` for one zinc or `zn_zn_zn_bound` for three.

### Configuration file

The `config.yaml` is the configuration file through which is possible to specify for:

- the `models.csv` file;
- the environment where pdb-tools is installed;
- the folder in which MutateX is installed;
- the folder where FoldX is installed;
- the FoldX suite;
- the inputs of mutate\_runfile\_.txt;
- the inputs of repair\_runfile\_.txt;
- the list of mutations mutation\_list.txt.
- the MutateX cleaning option
- the environment where PROCHECK is installed.

The MutateX cleaning option is specified with "mutatex.cleaning_depth" and accepts the inputs 'none', 'partial', and 'deep'. If the input is invalid or empty, the workflow stops before execution with an error message.

Both bundled configs set `mutatex.foldx_exe` to `/usr/local/foldx5.1/foldx`. To run with FoldX 5, set `mutatex.foldx_exe` in your working directory’s `config.yaml` to the installed FoldX 5 executable (for example, `/usr/local/foldx5/foldx`) and keep `mutatex.foldx_suite` set to `suite5`.

## Requirements

The user must have `Snakemake` [^Mölder2021] and `python` v3.7 or higher installed, together with `MutateX`[^Tiberti] and `FoldX`[^Schymkowitz2005]. The pipeline also requires `pdb-tools` [^Rodrigues] package and `PROCHECK` installed.

## Commands to run the pipeline:

`module load python/3.10`
 
To preview the example, run this from its working directory:

```bash
snakemake --dry-run --cores 1 all
```

A dry run checks that Snakemake can build the job graph. To check that zinc survives trimming and FoldX repair, run the corresponding jobs.

`snakemake --cores 4`

By default `MutateX` uses all cores assigned to the workflow (`snakemake --cores`) for each MutateX run.
It is possible to change the number of cores used by each `MutateX` run with:

`snakemake --cores 8 --set-threads mutatex_scan=2` 

In any case, the maximum number of processes used by each `MutateX` run cannot exceed the number of provided cores.
In the latter example, the pipeline will still occupy 8 cores, using a maximum of two processes per `MutateX` run.

### References

[^Tiberti]: MutateX: an automated pipeline for in-silico saturation mutagenesis of protein structures and structural ensembles Matteo Tiberti\*, Thilde Terkelsen, Kristine Degn, Ludovica Beltrame, Tycho Canter Cremers, Isabelle da Piedade, Miriam Di Marco, Emiliano Maiani, Elena Papaleo*, Brief Bioinform. 2022 Mar 22.

[^Schymkowitz2005]: Joost Schymkowitz, Jesper Borg, Francois Stricher, Robby Nys, Frederic Rousseau, Luis Serrano, The FoldX web server: an online force field, Nucleic Acids Research, Volume 33, Issue suppl_2, 1 July 2005, Pages W382–W388.

[^Mölder2021]: Mölder, F., Jablonski, K.P., Letcher, B., Hall, M.B., Tomkins-Tinch, C.H., Sochat, V., Forster, J., Lee, S., Twardziok, S.O., Kanitz, A., Wilm, A., Holtgrewe, M., Rahmann, S., Nahnsen, S., Köster, J., 2021. Sustainable data analysis with Snakemake. F1000Res 10, 33.

[^Rodrigues]: Rodrigues JPGLM, Teixeira JMC, Trellet M and Bonvin AMJJ. pdb-tools: a swiss army knife for molecular structures. F1000Research 2018
