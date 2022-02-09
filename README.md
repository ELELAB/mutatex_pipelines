# mutatex_pipelines

## Overview

This directory contains Snakemake-based pipelines for peptide mutation scanning runs with `MutateX`[^Tiberti]. 

The protocol `custom_scan/stability_scan` predicts changes of folding free energy upon mutation for each residue of a given list of mutations provided as input. Each residue is mutated to a list of residue types depending on the mutations found in the corresponding input dataset.

The protocol `custom_scan/stability_binding_scan` predicts changes of folding and binding free energy upon mutation for each residue of a given list of mutations provided as input. Each residue is mutated to a list of residue types depending on the mutations found in the corresponding input dataset.

### References

[^Tiberti]: Tiberti, Terkelsen, T., Cremers, T. C., Di Marco, M., da Piedade, I., Maiani, E., & Papaleo, E. (2019). MutateX: an automated pipeline for in-silico saturation mutagenesis of protein structures and structural ensembles. https://doi.org/10.1101/824938
