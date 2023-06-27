import yt
from math import sqrt, floor
import cmasher as cmr
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import mpi4py
from mpi4py import MPI
import os 
import argparse
import re

def load_dataset(basedir:dir, periodicity:bool):
    units_override = {"length_unit": (1.0, "cm"),
                      "time_unit": (1.0, "s"),
                      "mass_unit": (1.0, "g")
                      }

    parameters_noPer = {
        "periodicity": (False,False,False)
    }

    parameters_withPer = {
        "periodicity": (False,True,True)
    }
    
    if periodicity == True:
        loadparams = parameters_withPer
    else:
        loadparams = parameters_noPer

    return yt.load(f"{basedir}/data/id0/*.vtk", units_override=units_override, parameters = loadparams)

def add_units_ds(dataset, basedir, r_cloud, drat, T_cloud, M_wind):
    def add_units(ds0, r_cloud, drat, T_cloud, M_wind):
        gamma = 5/3

        v_wind = M_wind * sqrt(drat) * sqrt(gamma*T_cloud)

        t_cc = sqrt(drat) * r_cloud / v_wind

        rho_cloud = drat

        p0 = T_cloud * rho_cloud

        ds0.define_unit("t_cc", t_cc * yt.units.second, tex_repr = r't/t_{\rm cc}')
        ds0.define_unit("r_cl", r_cloud * yt.units.centimetre, tex_repr = r"r/r_{\rm cl}")
        ds0.define_unit("v_wind", v_wind * yt.units.centimetre/yt.units.second, tex_repr = r"v/v_{\rm wind}")
        ds0.define_unit("rho_cl", rho_cloud* yt.units.gram/yt.units.centimetre**3, tex_repr = r"\rho/\rho_{\rm cl}")
        ds0.define_unit("p0", p0* yt.units.dyn/yt.units.centimetre**2, tex_repr = r"p/p_{0}")
        ds0.define_unit("T_cl", T_cloud* yt.units.centimetre*yt.units.dyn/yt.units.gram, tex_repr = r"T/T_{\rm cl}")
        
    add_units(dataset, r_cloud, drat, T_cloud, M_wind)

    def _ath_temperature(field,data):
        return data["pressure"]/data["density"]

    dataset.add_field(
        ("athena", "cloud_temp"),
        units = "T_cl",
        function = _ath_temperature,
        sampling_type = "cell"
    )

def get_inputdata(basedir:dir):
    
    basepath = Path(basedir)
    
    name_pos = re.search(r"\d{4}-\d{2}-\d{2}_", basedir)
    run_specifier = basedir[name_pos.end():]
    filepath = basepath / "inputs" / f"athinput.{run_specifier}"

    with open(filepath, "r") as file:
        data = file.readlines()
            
    for line in data:
        if re.search("r_cloud", line) != None:
            loc = re.search(r"r_cloud\s*=", line)
            r_cloud = float(line[loc.end():loc.end()+8])
        if re.search("drat", line) != None:
            loc = re.search(r"drat\s*=", line)
            drat = float(line[loc.end():loc.end()+8])
        if re.search("T_cloud", line) != None:
            loc = re.search(r"T_cloud\s*=", line)
            T_cloud = float(line[loc.end():loc.end()+8])
        if re.search("M_wind", line) != None:
            loc = re.search(r"M_wind\s*=", line)
            M_wind = float(line[loc.end():loc.end()+8])

    return r_cloud, drat, T_cloud, M_wind

def get_annotate_info(ds, basedir):
    formattime = "{:.2f}".format(ds.current_time)
    #index_hst = int(floor(float(str(formattime).removesuffix(" code_time")))*2-1)
    #if index_hst < 0:
    #    index_hst = 0
    basepath = Path(basedir)
    hstpath = basepath/"data"/"id0"/ "cloud.hst"
    hst_data = np.loadtxt(hstpath)
    current_time = float(str(ds.current_time).removesuffix(" code_time"))
    difference = hst_data[:,0]-current_time
    difference = np.abs(difference)
    index = difference.argmin()

    current_tcc = float(str(ds.current_time.in_units("t_cc")).removesuffix(" t_cc"))

    current_rel_m13 = hst_data[index,11]/hst_data[0,11]
    current_rel_vwind = hst_data[index,28]/hst_data[0,28]
    
    return current_rel_m13, current_rel_vwind, current_tcc

def run_parallels(basedir:dir, field_list, proj_field_list, periodicity:bool):

    basepath = Path(basedir)

    yt.enable_parallelism()
    
    ts = load_dataset(basedir, periodicity)
    r_cloud, drat, T_cloud, M_wind = get_inputdata(basedir)

    for i in ts.piter():
        add_units_ds(i, basedir, r_cloud, drat, T_cloud, M_wind)

        for field in field_list:

            outpath = basepath / f"Images_{field[1]}"/ "raw"
            os.chdir(outpath)
             
            slc = yt.SlicePlot(i, "z", (field[0], field[1]), origin="native")
            
            slc.set_axes_unit("r_cl")
            
            if field[1] == "density":
                slc.set_unit((field[0], field[1]),'rho_cl')
                cmap = cmr.get_sub_cmap('cmr.rainforest', 0.15, .85)
                zmax = 2
                zmin = 2e-2
                
            elif field[1] == "cloud_temp":
                slc.set_unit((field[0], field[1]),'T_cl')
                cmap = cmr.get_sub_cmap('cmr.bubblegum_r', 0.25, 1)
                zmax = 1e0
                zmin = 2e2
                
            elif field[1] == "velocity_x":
                slc.set_unit((field[0], field[1]),'v_wind')
                cmap = cmr.get_sub_cmap('cmr.torch', 0.2, .8)
                zmax =  1.1
                zmin =  0
                
            elif field[1] == "pressure":
                slc.set_unit((field[0], field[1]),'p0')
                cmap = cmr.get_sub_cmap('cmr.viola', 0, 1) #or savanna_r
                zmax = 1e1
                zmin = 1e-1
                
            elif field[1] == "specific_scalar[0]":
                cmap = cmr.get_sub_cmap('cmr.cosmic', 0.3, 1)
                zmax = 1e0
                zmin = 1e-6
            
            slc.set_cmap((field[0], field[1]), cmap)
            slc.set_zlim((field[0], field[1]), zmax, zmin)

            current_rel_m13, current_rel_vwind, current_tcc = get_annotate_info(i, basedir)

            title =  f"$\chi = 100$, $t= {current_tcc:.2f} t_{{\mathrm{{cc}}}}$, $m_{{1/3}} = {current_rel_m13:.2f} m_{{\mathrm{{cl}}}}, v_{{\mathrm{{wind,rel}}}}= {current_rel_vwind:.2f} v_{{\mathrm{{wind,init}}}}$"
            slc.annotate_title(r"{}".format(title))
            
            if yt.is_root():

                slc.save(mpl_kwargs=dict(dpi=300))

        for proj_fields in proj_field_list:
            outpath = basepath / f"Images_{proj_fields[1]}_projection"/ "raw"
            os.chdir(outpath)
             
            slc = yt.ProjectionPlot(i, "z", (proj_fields[0], proj_fields[1]), weight_field = ('gas','density'), origin="native", method = "integrate")
            
            slc.set_axes_unit("r_cl")
            
            if proj_fields[1] == "density":
                slc.set_unit((proj_fields[0], proj_fields[1]),'rho_cl')
                cmap = cmr.get_sub_cmap('cmr.rainforest', 0.15, .85)
                zmax = 1e0
                zmin = 1e-2
                
            elif proj_fields[1] == "cloud_temp":
                slc.set_unit((proj_fields[0], proj_fields[1]),'T_cl')
                cmap = cmr.get_sub_cmap('cmr.bubblegum_r', 0.25, 1)
                zmax = 1e2
                zmin = 5e0
                
            slc.set_cmap((proj_fields[0], proj_fields[1]), cmap)
            slc.set_zlim((proj_fields[0], proj_fields[1]), zmax, zmin)
            
            title =  f"$\chi = 100$, $t= {current_tcc:.2f} t_{{\mathrm{{cc}}}}$, $m_{{1/3}} = {current_rel_m13:.2f} m_{{\mathrm{{cl}}}}, v_{{\mathrm{{wind,rel}}}}= {current_rel_vwind:.2f} v_{{\mathrm{{wind,init}}}}$"
            slc.annotate_title(r"{}".format(title))
            
            if yt.is_root():

                slc.save(mpl_kwargs=dict(dpi=300))
                
if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='parallel_images_highdpi_new.py',
                    description='Creates an image timeseries from a specified directory and outputs into antother specfied Images directory in the same folder')
    parser.add_argument("basedir")
    parser.add_argument("periodicity", default=False)

    args = parser.parse_args()
    
    field_list = [('athena', 'cloud_temp'),('gas','density'),('athena','specific_scalar[0]'),('gas','velocity_x'),('gas','pressure')]
    proj_list = [('athena', 'cloud_temp'),('gas','density')]
    comm = mpi4py.MPI.COMM_WORLD
    rank = comm.Get_rank()
    if rank == 0:
        for field in field_list:
            if os.path.exists(Path(f"{args.basedir}/Images_{field[1]}")) != True:
                os.mkdir(f"{args.basedir}/Images_{field[1]}")
                os.mkdir(f"{args.basedir}/Images_{field[1]}/raw")
        for field in proj_list:
            if os.path.exists(Path(f"{args.basedir}/Images_{field[1]}_projection")) != True:
                os.mkdir(f"{args.basedir}/Images_{field[1]}_projection")
                os.mkdir(f"{args.basedir}/Images_{field[1]}_projection/raw")
                
    MPI.COMM_WORLD.Barrier()
    run_parallels(args.basedir, field_list, proj_list, args.periodicity)