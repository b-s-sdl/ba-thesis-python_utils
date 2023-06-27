from pathlib import Path
import os 
import argparse
from datetime import date
import shutil
import raster_geometry as rg
import numpy as np
import matplotlib.pyplot as plt
import re

def recreate_slurm(rundir: str):
    
    name_pos = re.search(r"\d{4}-\d{2}-\d{2}_", rundir)
    run_specifier = rundir[name_pos.end():]
    rundate = rundir[int(name_pos.start()):int(name_pos.end())-1]

    outdir = Path(f"/ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}")
    
    with open("./blueprints/slurm_images_blueprint", "r") as file:
        data = file.readlines()
        data[6] = f"#SBATCH -J img_{run_specifier}\n"
        data[28] = f"srun python parallel_images_multiSeries.py /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier} False\n"
        data[34] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_density/raw\n"
        data[36] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_dens.mp4\n"
        data[38] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_cloud_temp/raw\n"
        data[40] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_temp.mp4\n"
        data[42] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_pressure/raw\n"
        data[44] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_press.mp4\n"
        data[46] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_specific_scalar[0]/raw\n"
        data[48] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_scalar.mp4\n"
        data[50] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_velocity_x/raw\n"
        data[52] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_velo.mp4\n"
        data[54] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_density_projection/raw\n"
        data[56] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_dens_projection.mp4\n"
        data[58] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_cloud_temp_projection/raw\n"
        data[60] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_temp_projetion.mp4\n"

        with open("./temp/slurm_images_blueprint", "w") as tempfile:
            tempfile.writelines(data)
    
        shutil.copy('./temp/slurm_images_blueprint', outdir / f'slurm/slurm_new_images_{run_specifier}')

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(prog='setup_run',
                    description='Recreates a suitable images generation script for runs that have been executed before current version existed.')
    parser.add_argument("rootdir")
    args = parser.parse_args()
    
    recreate_slurm(args.rootdir)
