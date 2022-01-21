## Overview

This directory contains a snakemake-based pipeline for peptide mutation scanning runs with `MutateX`[^Tiberti].
This protocol predicts changes of folding free energy upon mutation for each residue of a given list of mutations provided as input. 
Each residue is mutated to a list of residue types depending on the mutations found in the corresponding input dataset.

## Description of the directory content:

### Snakefile

The `Snakefile` is the pipeline. 

### Table

The `models.csv` file is a comma separated file containing all the information
needed to generate a consistent output directory structure, as well as to
provide the correct input pdbs to `MutateX`.

`csv` description:

|Entry|Meaning|Example|
|---|---|---|
|`protein_name`|Name of the protein chain|lc3b|
|`mathod`|Method by which the structures were generated|xray|
|`PDB`|PDB ID of original complex|1V49|
|`aa_protein`|First-last sequence residue numbers corresponding to the residues in the FASTA sequence of the protein|1-120|
|`chain`|Chain identifier of the protein|a|
|`restraints`|Restraints applied to the generation of the pdb structure (if any)|blind|
|`model_name`|Name of the structure model that was used as a starting structure for final model generation|model0|
|`scan`|Type of scanning to be performed with mutatex|cancermuts|
|`pdb_file`|Name of the pdb file to be provided in input|lc3b.pdb|

N.B., The `restraints`, `model_name` and `scan` columns can be left empty if needed.

Additionally, the pipeline requires one csv file per row of the `models.csv` file, named: 

`{protein_name}{chain}.csv`

These files contain the mutations that we are interested investigating, one per row. One is consistent with the output of the cancermuts software, and contains the following columns that are used by the pipeline:

|Column|Meaning|Example|
|---|---|---|
|`Position`|1-numbered position of the mutation site in the primary Uniprot main sequence|R|
|`WT residue`|Single-letter residue type in the canonical wild-type sequence (as per Position)|A|
|`Position`|Single-letter residue type of the mutant variant|94|

The other supported format is a csv file with a `Mutation` column. It will report (i) the amino acid WT in single letter, (ii) the position in the sequence and (iii) the mutation in single letter. The three notations listed above can be preceded from a prefix "p".

|Column|Meaning|Example|
|---|---|---|
|`Mutation`| "prefix""amino_acid""position""new_amino_acid"|pR54S|
 
### Configuration file

The `config.yaml` is the configuration file through which is possible to specify for:

- the `models.csv` file;
- the path containing the input pdb files;
- the path containing the input csv files;
- the `skip-repair` option, to skip (`True`) or not (`False`) the repair phase;
- the `FoldX`[^Schymkowitz2005] executable location;
- the contents of the `mutate_runfile.txt` file;
- the contents of the `repair_runfile.txt` file;
- the contents of the `interface_runfile.txt` file. 

## Requirements

The user must have `Snakemake` [^Mölder2021] and `python` v3.7 or higher installed, togheter with `MutateX`[^Tiberti] and `FoldX`[^Schymkowitz2005].

## Commands to run the pipeline:

`module load python/3.7`
 
`snakemake --cores 4`

It is possible to change the maximum number of processes that each `MutateX` run is allowed to use (default is 1):

`snakemake --cores 4 --set-threads mutatex_scan=4`

The maximum number of processes used by each `MutateX` run cannot exceed the number of provided cores.


### References

[^Tiberti]: MutateX: an automated pipeline for in-silico saturation mutagenesis of protein structures and structural ensembles Matteo Tiberti, Thilde Terkelsen, Tycho Canter Cremers, Miriam Di Marco, Isabelle da Piedade, Emiliano Maiani, Elena Papaleo, submitted to biorxiv.

[^Sali1993]: A. Sali & T.L. Blundell. Comparative protein modelling by satisfaction of spatial restraints. J. Mol. Biol. 234, 779-815, 1993.

[^Schymkowitz2005]: Joost Schymkowitz, Jesper Borg, Francois Stricher, Robby Nys, Frederic Rousseau, Luis Serrano, The FoldX web server: an online force field, Nucleic Acids Research, Volume 33, Issue suppl_2, 1 July 2005, Pages W382–W388.

[^Mölder2021]: Mölder, F., Jablonski, K.P., Letcher, B., Hall, M.B., Tomkins-Tinch, C.H., Sochat, V., Forster, J., Lee, S., Twardziok, S.O., Kanitz, A., Wilm, A., Holtgrewe, M., Rahmann, S., Nahnsen, S., Köster, J., 2021. Sustainable data analysis with Snakemake. F1000Res 10, 33.

