from utils import from_json
from glob import glob

gene_to_length = from_json("hg19_with_GFP/gene_to_length.json")

"""
Read HTSeq-count output files and create a corresponding _fpkm.txt file for each
"""
for fname in glob("output_with_GFP/*.txt"):
    gene_to_count = {}
    total_count = 0
    with open(fname, 'r') as ropen:
        for line in ropen:
            sl = line.strip().split()
            if len(sl) == 0: continue

            gene, count = sl
            if gene not in gene_to_length: continue

            count = int(count)
            gene_to_count[gene] = count
            total_count += count

    output_fname = fname.replace(".txt", "_fpkm.txt")
    with open(output_fname, 'w+') as wopen:
        for gene, count in gene_to_count.items():
            length = gene_to_length[gene]
            fpkm = count / (length / 1e3) / (total_count / 1e6)
            wopen.write(f"{gene} {fpkm}\n")


