from environment_mbc import Env
from mbc_fn import mbc
import matplotlib.pyplot as plt

record1 = []
record2 = []
price = []
demand = []
supply = []
total_flow1 = []
total_flow2 = []
gates = []

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
    state, done = env.step([1.0,1.0,1.0])
    record1.append(state[0])
    tot_flow = sum(state[0,n_tanks:2*n_tanks])
    total_flow1.append(tot_flow)

print("Done")
env.reset()

done = False
action = [0.5,0.5,0.5]
beta = 1.0; epsilon = 7.0
setptOutflow = 2.5
while not done:
    state, done = env.step(action)
    record2.append(state[0])

    p, PD, PS, tot_flow, action = mbc(state,
        setptOutflow, beta, epsilon, max_depths,
        n_tanks, action)

    gates.append(action[0:n_tanks])
    price.append(p)
    demand.append(PD)
    supply.append(PS)
    total_flow2.append(tot_flow)

plt.subplot(1,3,1)
plt.plot(record1)
plt.subplot(1,3,2)
plt.plot(record2)
plt.subplot(1,3,3)
plt.plot(total_flow1)
plt.plot(total_flow2)
plt.show()
