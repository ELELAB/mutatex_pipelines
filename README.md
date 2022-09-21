# mutatex_pipelines

## Overview

This repository contains three Snakemake-based pipelines for peptide mutation scanning runs and processing with `MutateX`[^Tiberti]. 

The first pipeline `custom_scan` includes two protocols:

- The protocol `custom_scan/stability_scan` predicts changes of folding free energy upon mutation for each residue of a given list of mutations provided as input. Each residue is mutated to a list of residue types depending on the mutations found in the corresponding input dataset.

- The protocol `custom_scan/stability_binding_scan` predicts changes of folding and binding free energy upon mutation for each residue of a given list of mutations provided as input. Each residue is mutated to a list of residue types depending on the mutations found in the corresponding input dataset.

The second pipeline `custom_collect_scan` behaves as `custom_scan/stability_scan`, but the user is not required to provide the input PDBs, instead the pipeline will automatically retrieve the structures from AlphaFold Protein Structure Database, if present, trim them based on user input and run the analysis.

The third pipeline `custom_analysis` visualizes the output of MutateX stability scans by running MutateX's plotting tools. These include the generation of: heatmaps, boxplots, scatter plots, average plots, violin plots, logo plots, density plots and output tables (.xlsx and .csv formats).

### References

[^Tiberti]: Tiberti, Terkelsen, T., Cremers, T. C., Di Marco, M., da Piedade, I., Maiani, E., & Papaleo, E. (2019). MutateX: an automated pipeline for in-silico saturation mutagenesis of protein structures and structural ensembles. https://doi.org/10.1101/824938
