## Overview

This directory contains a snakemake-based pipeline for peptide mutation scanning runs with `MutateX`[^Tiberti]. This protocol predicts changes of folding free energy upon mutation for each residue of a given list of mutations provided as input. Each residue is mutated to a list of residue types depending on the mutations found in the corresponding input dataset.

## Description of the directory content:

### {coding_gene} folder

This is an example folder hosting the output of the pipeline. The prerequisite to run the pipeline is to fill the attributes of the template `.csv` file with the instances related to the protein of interest. In case the scan is to be performed on a model from AlphaFold Protein Structure Database, the pipeline will automatically download and prepare the file for the subsequent scan, otherwise, the user is required to provide the input `.pdb` file inside the working directory: `{gene}/structure_selection/{database}`.

### Snakefile

The `Snakefile` is the pipeline. 

### Table

The `models.csv` file is a comma separated file containing all the information needed to generate a consistent output directory structure, as well as to provide the correct input files to `MutateX` processing tools.

`csv` description:

|Entry|Meaning|Example|
|---|---|---|
|`coding_gene`|Name of the gene coding for the peptide of interest|Hspb1|
|`prot_id`|Protein identifier|P14602|
|`database`|Database from which the protein structure was downloaded|AF|
|`start_res`|First residue to consider during the scan|88|
|`end_res`|Last residue to consider during the scan|177|
|`version`|Protein structure release|v3|
|`pdb_file`|PDB namefile (optional)||

The example file provided was retrieved from AlphaFold Protein Structure Database. The N and C terminal regions were trimmed in order to consider only the higher-confidence and structured portions of the protein.

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

## Requirements

The user must have `Snakemake` [^Mölder2021] and `python` v3.7 or higher installed, together with `MutateX`[^Tiberti] and `FoldX`[^Schymkowitz2005]. The pipeline also requires `pdb-tools` [^Rodrigues] package installed.

## Commands to run the pipeline:

`module load python/3.10`
 
`snakemake --cores 4`

By default `MutateX` uses all cores assigned to the workflow (`snakemake --cores`).
It is possible to change the number of cores used by each `MutateX` run with:

`snakemake --cores 8 --set-threads mutatex_scan=2` 

The maximum number of processes used by each `MutateX` run cannot exceed the number of provided cores.

### References

[^Tiberti]: MutateX: an automated pipeline for in-silico saturation mutagenesis of protein structures and structural ensembles Matteo Tiberti\*, Thilde Terkelsen, Kristine Degn, Ludovica Beltrame, Tycho Canter Cremers, Isabelle da Piedade, Miriam Di Marco, Emiliano Maiani, Elena Papaleo*, Brief Bioinform. 2022 Mar 22.

[^Schymkowitz2005]: Joost Schymkowitz, Jesper Borg, Francois Stricher, Robby Nys, Frederic Rousseau, Luis Serrano, The FoldX web server: an online force field, Nucleic Acids Research, Volume 33, Issue suppl_2, 1 July 2005, Pages W382–W388.

[^Mölder2021]: Mölder, F., Jablonski, K.P., Letcher, B., Hall, M.B., Tomkins-Tinch, C.H., Sochat, V., Forster, J., Lee, S., Twardziok, S.O., Kanitz, A., Wilm, A., Holtgrewe, M., Rahmann, S., Nahnsen, S., Köster, J., 2021. Sustainable data analysis with Snakemake. F1000Res 10, 33.

[^Rodrigues]: Rodrigues JPGLM, Teixeira JMC, Trellet M and Bonvin AMJJ. pdb-tools: a swiss army knife for molecular structures. F1000Research 2018
