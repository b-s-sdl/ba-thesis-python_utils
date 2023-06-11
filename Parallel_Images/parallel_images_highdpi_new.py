import yt
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import mpi4py
from mpi4py import MPI
import os 
import argparse

def run_parallels(basedir:dir, plottype):

    basepath = Path(basedir)
    outpath = basepath / f"Images_{plottype}"

    yt.enable_parallelism()

    ts = yt.load(f"{basedir}/data/id0/*.vtk")
    os.chdir(outpath)

    label_counter = 0

    for i in ts.piter():

        slc = yt.ProjectionPlot(i, "z", ("athena", plottype))
        
        if yt.is_root():
            
            slc.save(mpl_kwargs=dict(dpi=300))

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='parallel_images_highdpi_new.py',
                    description='Creates an image timeseries from a specified directory and outputs into antother specfied Images directory in the same folder')
    parser.add_argument("basedir")
    parser.add_argument("plottype")

    args = parser.parse_args()
    
    comm = mpi4py.MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        if os.path.exists(Path(f"{args.basedir}/Images_{args.plottype}")) != True:
            os.mkdir(f"{args.basedir}/Images_{args.plottype}")
    print(rank)
    MPI.COMM_WORLD.Barrier()
    run_parallels(args.basedir, args.plottype)