module load procheck
procheck.scr P36896_29-110.pdb A 2.0
check *sum file
python classify_procheck.py -i *sum -o procheck.csv
