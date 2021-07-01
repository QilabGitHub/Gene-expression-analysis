import ujson as json
import os
import glob
import math

YOUR_EMAIL="test@stanford.edu"

def process_path(path):
    return path.strip("/").split("/")


def create_path(path):
    if not os.path.exists(path):
        os.makedirs(path)


def to_json(out_fname, data):
    with open(out_fname, "w") as wopen:
        json.dump(data, wopen, indent=4)


def from_json(fname):
    with open(fname, "r") as ropen:
        data = json.load(ropen)
    return data


def run_slurm(
    output_fname,
    lines,
    time=30,
    mem=8,
    job_name="test",
    run=False,
):
    # A rough conversion of minutes to hours
    hours = math.floor(time / 60)
    hours = str(hours)
    if len(hours) < 2:
        hours = "0" * (2 - len(hours)) + hours
    minutes = str(math.ceil(time % 60))
    minutes = "0" * (2 - len(minutes)) + minutes
    pretty_time = "{}:{}:00".format(hours, minutes)

    with open(output_fname, "w") as wopen:
        wopen.write("#!/bin/bash\n\n")
        wopen.write("#SBATCH --job-name={}\n".format(job_name))
        wopen.write(f"#SBATCH --mail-user={YOUR_EMAIL} --mail-type=ALL\n")
        wopen.write("#SBATCH --partition=owners\n")
        wopen.write("#SBATCH --time={}\n".format(pretty_time))
        wopen.write("#SBATCH --mem={}G\n".format(mem))
        wopen.write("\n")

        for line in lines:
            wopen.write("{}\n".format(line.strip()))

    if run:
        os.system("sbatch {}".format(output_fname))
