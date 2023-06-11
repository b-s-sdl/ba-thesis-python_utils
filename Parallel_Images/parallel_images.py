import yt
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import mpi4py
import os 
import argparse

yt.enable_parallelism()

def run_parallels(basedir:dir,outdir:dir, plottype):

    basepath = Path(basedir)
    outpath = Path(outdir)
    ts = yt.load(f"{basedir}/id*/*.vtk")
    os.chdir(outpath)

    label_counter = 0

    for i in ts.piter():

        if label_counter < 10 and label_counter >= 0:
            label = f"000{label_counter}"
        elif label_counter < 100 and label_counter > 9:
            label = f"00{label_counter}"
        elif label_counter < 1000 and label_counter > 99:
            label = f"0{label_counter}"
        elif label_counter < 10000 and label_counter > 999:
            label = f"{label_counter}"

        filename = f"{label}.png"
        slc = yt.ProjectionPlot(i, "z", ("athena", plottype))
        slc.save(name=filename)
        label_counter += 1

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='Parallel-Images',
                    description='Creates an image timeseries from a specified directory and outputs into antother dir on /ptmp')
    parser.add_argument("basedir")
    parser.add_argument("outdir")
    parser.add_argument("plottype")

    args = parser.parse_args()

    run_parallels(args.basedir, args.outdir, args.plottype)