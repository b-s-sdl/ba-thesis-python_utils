import os
from pathlib import Path
import re

blueprintdir = Path("./blueprints")

with open(f"{blueprintdir}/testslurm", "r") as file:
    data = file.readlines()

newdir = "/u/bseidl/thesis/Python_Utils/Parallel_Imageswdwdwd"
data[25] = f"cd {newdir}\n"

with open("transferslurm", "w") as file:
    file.writelines(data)