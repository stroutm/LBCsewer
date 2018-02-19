from environment_mbc import Env
from mbc_fn import mbc, perf
import matplotlib.pyplot as plt
import numpy as np

record1 = []
tanks1 = []
total_flow1 = []
flow_over_cum = []

beta = 1.0; epsilons = [0.0, 1.0, 10.0]
setptOutflow = 2.0

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
    tanks1.append(state[0][0:n_tanks])
    tot_flow = sum(state[0,n_tanks:-1])
    total_flow1.append(tot_flow)

flow_over = perf(total_flow1,setptOutflow)

plt.subplot(231)
for i in range(0,n_tanks):
    plt.plot(max_depths[i]*np.ones(len(tanks1)), label = "Setpoint for tank " + str(i+1))
plt.plot(tanks1)

plt.subplot(232)
plt.plot(setptOutflow*np.ones(len(total_flow1)), label = "Setpoint")
plt.plot(total_flow1, label = "No control")

print("No control flow over: " + str(sum(flow_over)))

for epsilon in epsilons:
    env.reset()

    record2 = []
    tanks2 = []
    price = []
    demand = []
    supply = []
    total_flow2 = []
    gates = []

    done = False
    action = [0.5,0.5,0.5]

    while not done:
        state, done = env.step(action)
        record2.append(state[0])
        tanks2.append(state[0][0:n_tanks])

        p, PD, PS, tot_flow, action = mbc(state,
            setptOutflow, beta, epsilon, max_depths,
            n_tanks, action)

        gates.append(action[0:n_tanks])
        price.append(p)
        demand.append(PD)
        supply.append(PS)
        total_flow2.append(tot_flow)

    flow_over = perf(total_flow2, setptOutflow)
    flow_over_cum.append(sum(flow_over))

    print("MB control (epsilon = " + str(epsilon) + ") flow over: "
        + str(sum(flow_over)))

    plt.subplot(231)
    plt.plot(tanks2)

    plt.subplot(232)
    plt.plot(total_flow2, label = "MBC, epsilon = " + str(epsilon))

    plt.subplot(234)
    plt.plot(price, label = "MBC, epsilon = " + str(epsilon))

    plt.subplot(235)
    plt.plot(demand, label = "MBC, epsilon = " + str(epsilon))

    plt.subplot(236)
    plt.plot(gates, label = "MBC, epsilon = " + str(epsilon))

plt.subplot(231)
plt.ylabel('Tank Depth')
plt.legend()

plt.subplot(232)
plt.ylabel('Total Outflow')
plt.legend()

plt.subplot(233)
plt.plot(epsilons,flow_over_cum)
plt.xlabel('Epsilon')
plt.ylabel('Total Outflow over Setpoint')

plt.subplot(234)
plt.ylabel('Price')
plt.legend()

plt.subplot(235)
plt.ylabel('Demand')
plt.legend()

plt.subplot(236)
plt.ylabel('Gate opening')
plt.legend()

plt.show()
