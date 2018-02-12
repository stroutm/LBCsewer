from environment_mbc import Env
import matplotlib.pyplot as plt
import numpy as np


def mbc(state, setptOutflow, beta, epsilon):
    tot_flow = sum(state[0,3:6])
    p = (sum(beta*state[0,0:3]/max_depths)
        + epsilon*(tot_flow-setptOutflow))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + beta*state[0,i]/max_depths[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        if PS == 0:
            Qi = 0
        else:
            Qi = PD[i]/PS*setptOutflow
        if state[0,i] == 0:
            act[i] = 0.5
        else:
            h2i = Qi/(0.61*1*np.sqrt(2*9.81*state[0,i]))
            act[i] = max(min(h2i/2,1.0),0.0)
        if state[0,i]/max_depths[i] > 0.9:
            act[i] = 1

    return p, PD, PS, tot_flow, act

record1 = []
record2 = []
price = []
demand = []
supply = []
total_flow1 = []
total_flow2 = []
gate = []

state_space = {"depths":["V-1","V-2","V-3"],
    "flows":["C-7","C-8","C-9"]}
n_tanks = len(state_space['depths'])
max_depths = [7.0,6.0,6.5]
control_points = ["R-4","R-5","R-6"]

env = Env("../data/input_files/tanks_TSS_flooding.inp",
    state_space,
    control_points)

done = False
while not done:
    state, _, done = env.step(np.ones(n_tanks))
    record1.append(state[0])
    tot_flow = sum(state[0,n_tanks:2*n_tanks])
    total_flow1.append(tot_flow)

print("Done")
env.reset()

done = False
act = 0.5*np.ones(len(control_points))
beta = 1.0; epsilon = 7.0
setptOutflow = 2.5
while not done:
    state, _, done = env.step(act)
    record2.append(state[0])

    p, PD, PS, tot_flow, act = mbc(state,setptOutflow, beta, epsilon)

    price.append(p)
    demand.append(PD)
    supply.append(PS)
    total_flow2.append(tot_flow)
    gate.append(act)

plt.subplot(1,3,1)
plt.plot(record1)
plt.subplot(1,3,2)
plt.plot(record2)
plt.subplot(1,3,3)
plt.plot(total_flow1)
plt.plot(total_flow2)
plt.show()
