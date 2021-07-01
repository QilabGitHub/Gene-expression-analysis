#!/bin/bash

#SBATCH --job-name=star_hg19
#SBATCH --mail-user=agchempa@stanford.edu --mail-type=ALL
#SBATCH --time=2:00:00
#SBATCH --mem=40G
#SBATCH --partition=owners
#SBATCH --begin=03:00


cd ..
htseq-count -i gene_id -r name -s no -f bam -q JB10Aligned.sortedByCoord.out.bam hg19refGene.sorted.gtf > test.txt

