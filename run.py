import os
import glob
from utils import run_slurm, from_json

output_dir = "output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

genome_dir = "hg19_with_GFP"
genome_fasta = f"{genome_dir}/hg19_with_GFP.fa"
genome_gtf = f"{genome_dir}/hg19_with_GFP.gtf"


def write_fpkm():
    gene_to_length = from_json(f"{genome_dir}/gene_to_length.json")

    for fname in glob(f"{output_dir}/*.txt"):
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


def gene_expression():
    for fname in glob.glob(f"{output_dir}/*.bam"):
        if not os.path.isfile(fname): continue
        file_leaf = fname.split("/")[-1]

        lines = [
            f"cd {output_dir}",
            "htseq-count -i gene_id {} {} -r pos -s no -f bam > {}_hg19.txt".format(file_leaf, genome_gtf, file_leaf.split(".")[0])
        ]
        run_slurm("generate_gene_expression.sh", lines, mem=70, time=60*3, run=True)


def align_reads():
    with open("experiment_overview.csv", 'r') as ropen:
        for idx, line in ropen:
            if idx == 0: continue
            sl = line.strip().split(",")

            name = sl[0]
            read1 = sl[1]
            paired = len(sl) > 2
            if paired: read2 = sl[2]

        lines = [
            "ml biology star",
            f"READ1={read1}",
            f"READ2={read2}" if paired else "",
            f"cd {output_dir}",
            f"STAR --genomeDir {genome_dir} --readFilesIn $READ1 $READ2 --runThreadN 10 --outSAMtype BAM SortedByCoordinate --outFileNamePrefix {output_dir}/{name}  --readFilesCommand gunzip -c"
        ]

        run_slurm("align_reads.sh", lines, mem=50, time=60*5, run=True)


def genome_generate():
    lines = [
        "ml biology star",
        f"cd {output_dir}",
        f"STAR --runMode genomeGenerate --runThreadN 10 --genomeDir {genome_dir} --genomeFastaFiles {genome_fasta} --sjdbGTFfile {genome_gtf} --sjdbOverhang 99"
    ]

    run_slurm("generate_genome.sh", lines, mem=100, time=60*24, run=True)


def main():
    genome_generate()
    align_reads()
    gene_expression()
    write_fpkm()


if __name__=="__main__":
    main()