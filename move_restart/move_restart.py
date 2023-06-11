from pathlib import Path
import os, fnmatch
import argparse
from datetime import date
import shutil
import re

def run_collector(rootdir: str, t_lim:str):
    
    rootname = rootdir
    rootdir = Path(rootdir)
    datadir = rootdir / "data" 
    bindir = rootdir / "bin" 
    
    if os.path.exists(bindir/"restart") != True:
        os.mkdir(bindir/"restart")
    
    filelist = []
    
    for subdir,dirs,files in os.walk(datadir, topdown = True):
        movefile = [x for x in files if fnmatch.fnmatch(x, "*.rst")]
        
        moveitem = ''
        
        for item in movefile:
            if moveitem == "":
                moveitem = item
                
            if item > moveitem:
                moveitem = item
                
        if moveitem != "": filelist.append(moveitem)
        
    filelist.sort()
    
    print("[LOG] Collected File List: \n")
    
    for i in filelist:
        print(i)
        pos = re.findall(r"id\d{1,4}", i)

        if pos != []:
            id = pos[0]
        else:
            id = 'id0'    
        
        sourcepath = Path(datadir / id / i)

        os.rename(sourcepath , bindir / "restart"/ i)
    
    name_pos = re.search(r"\d{4}-\d{2}-\d{2}_", rootname)

    run_specifier = rootname[name_pos.end():]
    print(run_specifier)
    inputfile = rootdir / f"slurm/slurm_athena_{run_specifier}"
    with open(inputfile, "r") as file:
        data = file.readlines()
    
    data[2]="#SBATCH -o ../Log/tjob.out.%j\n"
    data[3]="#SBATCH -e ../Log/tjob.err.%j\n"
    data[6]=f"#SBATCH -J rest_{run_specifier}\n"
    data[26]=f"srun ./athena -r ./restart/cloud.*.rst -t 11:55:00 -d ../data time/tlim={t_lim}"
    
    newfile = rootdir / "slurm" / f"slurm_restart_{run_specifier}"
    
    with open(newfile, "w") as file:
        file.writelines(data)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='move_restart',
                    description='Collects all restarts files out of all subdirectorise in a give directory and stores them in to a "restart" folder.')
    parser.add_argument("rootdir")
    parser.add_argument("t_lim")
    
    args = parser.parse_args()
    
    run_collector(args.rootdir, args.t_lim)