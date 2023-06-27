from pathlib import Path
import os 
import argparse
from datetime import date
import shutil
import raster_geometry as rg
import numpy as np
import matplotlib.pyplot as plt

def centerpos_series1(batchsize, cloudsize, distance):
    data = []
    if batchsize%2 != 0:
        batchsize -= 1
        data.append("0.0 0.0 0.0\n")
        centerdist = 2*cloudsize + distance
        initx = 0
        for i in range(int(-batchsize/2),int(batchsize/2)+1,1):
            if i != 0 and i != batchsize/2: data.append(f"{initx+i*centerdist} 0.0 0.0\n")
            elif i == batchsize/2: data.append(f"{initx+i*centerdist} 0.0 0.0")

    else:
        centerdist = 2*cloudsize + distance
        initx = cloudsize + distance/2
        data.append(f"{initx} 0.0 0.0\n")

        for i in range(int(-batchsize/2),int(batchsize/2),1):
            if i != 0 and i != batchsize/2 -1: data.append(f"{initx+i*centerdist} 0.0 0.0\n")
            elif i == batchsize/2 -1: data.append(f"{initx+i*centerdist} 0.0 0.0")
    
    with open(f"./temp/centerpos_series1_temp", "w") as file:
        file.writelines(data)         
        
def centerpos_series2(batchsize, cloudsize, distance):
    data = []
    if batchsize%2 != 0:
        batchsize -= 1
        data.append("0.0 0.0 0.0\n")
        centerdist = 2*cloudsize + distance
        initx = 0
        print(batchsize)
        for i in range(int(-batchsize/2),int(batchsize/2)+1,1):
            if i != 0  and i != batchsize/2: data.append(f"0.0 {initx+i*centerdist} 0.0\n")
            elif i == batchsize/2: data.append(f"0.0 {initx+i*centerdist} 0.0")

    else:
        centerdist = 2*cloudsize + distance
        initx = cloudsize + distance/2
        data.append(f"0.0 {initx} 0.0\n")

        for i in range(int(-batchsize/2),int(batchsize/2),1):
            if i != 0 and i != batchsize/2 -1: data.append(f"0.0 {initx+i*centerdist} 0.0\n")
            elif i == batchsize/2 -1: data.append(f"0.0 {initx+i*centerdist} 0.0")

    with open(f"./temp/centerpos_series2_temp", "w") as file:
        file.writelines(data) 
        
        
def centerpos_series3(outdir, batchsize, distance, a, b, c):
    plt.rcParams["figure.figsize"] = (10,10)
    
    size = 20

    ellipsoid = rg.ellipsoid(size,[a,b,c])
    unique, counts = np.unique(ellipsoid, return_counts=True)

    x,y,z = ellipsoid.nonzero()
    np.random.seed(2)
    random_points = np.random.choice(len(x), batchsize, replace=False)
    
    xran_plot = []
    yran_plot = []
    zran_plot = []

    for i in random_points:
        xran_plot.append(x[i])
        yran_plot.append(y[i])
        zran_plot.append(z[i])

    xran_plot = distance * np.array(xran_plot)-size*distance/2
    yran_plot = distance * np.array(yran_plot)-size*distance/2
    zran_plot = distance * np.array(zran_plot)-size*distance/2
    
    data = []
    
    for count, value in enumerate(xran_plot):
        data.append(f"{value:.2f} {yran_plot[count]:.2f} {zran_plot[count]:.2f}\n")
    data[-1] = data[-1].removesuffix("\n")

    with open(f"./temp/centerpos_series3_temp", "w") as file:
        file.writelines(data) 
    
    ax = plt.figure().add_subplot(projection='3d')
    ax.scatter(xran_plot, yran_plot, zran_plot, label='Points of array')
    ax.set_xlim(-size*distance/2,size*distance/2)
    ax.set_ylim(-size*distance/2,size*distance/2)
    ax.set_zlim(-size*distance/2,size*distance/2)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.view_init(elev=130, azim=-0, roll=90)
    ax.set_title(f"ellipse params in x:{a} y:{b} z:{c}")
    ax.legend()
    
    figpath = outdir / "3d_plot.png"
    plt.savefig(figpath, dpi=300)
 
def create_rundir(run_specifier: str, series: int, batchsize: int, cloudsize: int, distance: int, a:int, b:int, c:int):
    
    today = date.today()
    rundate = today.strftime("%Y-%m-%d")
    outdir = Path(f"/ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}")

    os.mkdir(outdir)
    os.mkdir(outdir / 'data')
    os.mkdir(outdir / 'setuprun')
    os.mkdir(outdir / 'bin')
    os.mkdir(outdir / 'slurm')
    os.mkdir(outdir / 'Log')
    os.mkdir(outdir / 'ImLog')
    os.mkdir(outdir / 'inputs')
    
    with open("./blueprints/athinput.blueprint", "r") as file:
        data = file.readlines()
        data[64] = f"centerpos       = centerpos_{run_specifier}\n"

        if series == 3:
            data[33] = "Nx1             = 1000\n"
            data[34] = "Nx2             = 480\n"
            data[35] = "Nx3             = 480\n"
            data[42] = "x1max           = 475\n"
            data[43] = "x1min           = -150\n"
            data[44] = "x2max           = 150\n"
            data[45] = "x2min           = -150\n"
            data[46] = "x3max           = 150\n"
            data[47] = "x3min           = -150\n"

        with open("./temp/athinput.tempfile", "w") as tempfile:
            tempfile.writelines(data)
    
    shutil.copy("./temp/athinput.tempfile", outdir / f'inputs/athinput.{run_specifier}')
    
    shutil.copy(Path('../../athena-maxbg-bsdl-fork/bin/athena'), outdir / 'bin')

    with open("./blueprints/slurm_athena_blueprint", "r") as file:
        data = file.readlines()
        data[6] = f"#SBATCH -J {run_specifier}\n"
        data[25] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/bin\n"
        data[26] = f"srun ./athena -i ../inputs/athinput.{run_specifier} -t 11:55:00 -d ../data\n"
        with open("./temp/slurm_athena_blueprint.tempfile", "w") as tempfile:
            tempfile.writelines(data)
            
    shutil.copy('./temp/slurm_athena_blueprint.tempfile', outdir / f'slurm/slurm_athena_{run_specifier}')
    
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
        data[54] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_density_projection/raw"
        data[56] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_dens_projection.mp4\n"
        data[58] = f"cd /ptmp/mpa/bseidl/Simulation-Runs/{rundate}_{run_specifier}/Images_cloud_temp_projection/raw"
        data[60] = f"ffmpeg -framerate 10 -pattern_type glob -i '*.png' -c:v libx264 -pix_fmt yuv420p -vf \"scale=trunc(iw/2)*2:trunc(ih/2)*2\" -f mp4 ../{run_specifier}_temp_projetion.mp4\n"

        with open("./temp/slurm_images_blueprint", "w") as tempfile:
            tempfile.writelines(data)
            
    shutil.copy('./temp/slurm_images_blueprint', outdir / f'slurm/slurm_images_{run_specifier}')
    
    if series == 0:
        shutil.copy("./blueprints/centerpos_blueprint", outdir / f'bin/centerpos_default_{run_specifier}')
        
    elif series == 1:
        centerpos_series1(int(batchsize), int(cloudsize), int(distance))
        shutil.copy("./temp/centerpos_series1_temp", outdir / f'bin/centerpos_{run_specifier}')
        
    elif series == 2:
        centerpos_series2(batchsize, cloudsize, distance)
        shutil.copy("./temp/centerpos_series2_temp", outdir / f'bin/centerpos_{run_specifier}')

    elif series == 3:
        centerpos_series3(outdir, batchsize, distance, a, b, c)
        shutil.copy("./temp/centerpos_series3_temp", outdir / f'bin/centerpos_{run_specifier}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='setup_run',
                    description='Creates a new folder in ptmp, moves the necessary binary file, creates athinput from a template, and creates the folders for a data dump.')
    parser.add_argument("run_specifier")
    parser.add_argument("series", default= 0)
    parser.add_argument("cloudsize", default=5)
    parser.add_argument("batchsize", default=1)
    parser.add_argument("distance", default= 0)
    parser.add_argument("a", default= 2)
    parser.add_argument("b", default= 2)
    parser.add_argument("c", default= 2)


    args = parser.parse_args()
    
    create_rundir(args.run_specifier, int(args.series),int(args.batchsize),int(args.cloudsize),int(args.distance),int(args.a),int(args.b),int(args.c))