## Overview

This directory contains a snakemake-based pipeline to analyse the output of peptide stability scans performed with `MutateX`[^Tiberti].

## Description of the directory content:

### {coding_gene} folder

This is an example folder hosting the output of the pipeline. 
The underlying assumption for using the pipeline is that the `stability\_scan` pipeline has been run and the same filetree is produced for `{coding\_gene}/free/stability/mutatex\_runs`.
The pipeline will automatically create a soft link to the input files contained in `{coding\_gene}/free/stability/mutatex\_runs/{database}\_{range}/model\_{version}/saturation` inside the folder `{coding\_gene}/free/stability/mutatex\_analyses/{database}\_{range}/model\_{version}/saturation` in order to run the analysis.


### Snakefile

The `Snakefile` is the pipeline. 

### Table

The `models.csv` file is a comma separated file containing all the information
needed to generate a consistent output directory structure, as well as to
provide the correct input files to `MutateX` processing tools.

`csv` description:

|Entry|Meaning|Example|
|---|---|---|
|`coding_gene`|Name of the gene coding for the peptide of interest|Hspb1|
|`prot_id`|Protein identifier|P14602|
|`method`|Method by whoich the structure was obtained|AF|
|`start_res`|First residue to consider during the analysis|88|
|`end_res`|Last residue to consider during the analysis|177|
|`model`|Protein model type (i.e. exp = experimental structure, model_ = protein structure release from AF Database)|model_v3|

The example file provided was retrieved from AlphaFold Protein Structure Database. The N and C terminal regions were trimmed in order to consider only the higher-confidence and structured portions of the protein.

### Configuration file

The `config.yaml` is the configuration file through which is possible to specify for:

- the `models.csv` file;
- the number of residues to be shown in each plot;
- the labels' font size;
- the energy thresholds to be used when plotting: heatmap, distribution plots (scatterplot, average plot, boxplot and violinplot) and logo plot;
- the folder in which MutateX is installed.


## Requirements

The user must have `Snakemake` [^Mölder2021] and `python` v3.7 or higher installed, togheter with `MutateX`[^Tiberti] and `FoldX`[^Schymkowitz2005].

## Commands to run the pipeline:

`module load python/3.7`
 
`snakemake --cores 4`

It is possible to change the maximum number of processes that each `MutateX` run is allowed to use (default is 1):

`snakemake --cores 4 --set-threads mutatex_scan=4`

The maximum number of processes used by each `MutateX` run cannot exceed the number of provided cores.

### References

[^Tiberti]: MutateX: an automated pipeline for in-silico saturation mutagenesis of protein structures and structural ensembles Matteo Tiberti\*, Thilde Terkelsen, Kristine Degn, Ludovica Beltrame, Tycho Canter Cremers, Isabelle da Piedade, Miriam Di Marco, Emiliano Maiani, Elena Papaleo*, Brief Bioinform. 2022 Mar 22.

[^Schymkowitz2005]: Joost Schymkowitz, Jesper Borg, Francois Stricher, Robby Nys, Frederic Rousseau, Luis Serrano, The FoldX web server: an online force field, Nucleic Acids Research, Volume 33, Issue suppl_2, 1 July 2005, Pages W382–W388.

[^Mölder2021]: Mölder, F., Jablonski, K.P., Letcher, B., Hall, M.B., Tomkins-Tinch, C.H., Sochat, V., Forster, J., Lee, S., Twardziok, S.O., Kanitz, A., Wilm, A., Holtgrewe, M., Rahmann, S., Nahnsen, S., Köster, J., 2021. Sustainable data analysis with Snakemake. F1000Res 10, 33.
