import yt
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import mpi4py
import os 
import argparse


def run_parallels(basedir:dir,outdir:dir, plottype):
    yt.enable_parallelism()

    basepath = Path(basedir)
    outpath = Path(outdir)
    
    ts = yt.load(f"{basedir}/id0/*.vtk")
    os.chdir(outpath)

    label_counter = 0

    for i in ts.piter():

        slc = yt.ProjectionPlot(i, "z", ("athena", plottype))
        
        if yt.is_root():
            
            slc.save(mpl_kwargs=dict(dpi=300))
            

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='Parallel-Images',
                    description='Creates an image timeseries from a specified directory and outputs into antother dir on /ptmp')
    parser.add_argument("basedir")
    parser.add_argument("outdir")
    parser.add_argument("plottype")

    args = parser.parse_args()

    run_parallels(args.basedir, args.outdir, args.plottype)