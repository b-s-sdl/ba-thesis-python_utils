import os
from pathlib import Path

def series1(batchsize, cloudsize, distance):
    data = []
    if batchsize%2 != 0:
        batchsize -= 1
        data.append("0.0 0.0 0.0\n")
        centerdist = 2*cloudsize + distance
        initx = 0
        print(batchsize)
        for i in range(int(-batchsize/2),int(batchsize/2)+1,1):
            if i != 0: data.append(f"{initx+i*centerdist} 0.0 0.0\n")
    else:
        centerdist = 2*cloudsize + distance
        initx = cloudsize + distance/2
        data.append(f"{initx} 0.0 0.0\n")

        for i in range(int(-batchsize/2),int(batchsize/2),1):
            if i != 0: data.append(f"{initx+i*centerdist} 0.0 0.0\n")
    
    with open("test", "w") as file:
        file.writelines(data)         
        
def series2(batchsize, cloudsize, distance):
    data = []
    if batchsize%2 != 0:
        batchsize -= 1
        data.append("0.0 0.0 0.0\n")
        centerdist = 2*cloudsize + distance
        initx = 0
        print(batchsize)
        for i in range(int(-batchsize/2),int(batchsize/2)+1,1):
            if i != 0: data.append(f"0.0 {initx+i*centerdist} 0.0\n")
    else:
        centerdist = 2*cloudsize + distance
        initx = cloudsize + distance/2
        data.append(f"{initx} 0.0 0.0\n")

        for i in range(int(-batchsize/2),int(batchsize/2),1):
            if i != 0: data.append(f"0.0 {initx+i*centerdist} 0.0\n")
    
    with open("test", "w") as file:
        file.writelines(data) 
    
    
if __name__ == "__main__":
    series1(6, 10, 5)