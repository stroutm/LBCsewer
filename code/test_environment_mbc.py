from environment_mbc import Env
from mbc_fn import mbc, mbc_bin, perf, TSScalc
import matplotlib.pyplot as plt
import numpy as np

results = []
plot = 1
TSS = 0

tank_depths = []
total_flow = []
TSS_load = []
flow_over_cum = []
TSS_over_cum = []

beta = 1.0; epsilons = [0.0]; zetas = [0.0]
setptOutflow = 2.5
setptTSSload = 70

state_space = {"depths":["V-1","V-2","V-3"],
    "flows":["C-7","C-8","C-9"]}
n_tanks = len(state_space['depths'])
control_points = ["R-4","R-5","R-6"]

env = Env("../data/input_files/tanks_TSS_flooding.inp",
    state_space,
    control_points)

max_depths = env.tempo()

done = False; j = 0
while not done:
    j += 1
    state, done = env.step([1.0,1.0,1.0])
    tank_depths.append(state[0][0:n_tanks])
    tot_flow = sum(state[0,n_tanks:2*n_tanks])
    total_flow.append(tot_flow)
    if TSS == 1:
        if j == 1:
            TSSL = TSScalc(n_tanks, tank_depths[-1], 0, state[0][n_tanks:2*n_tanks])
        else:
            TSSL = TSScalc(n_tanks, tank_depths[-1], tank_depths[-2], state[0][n_tanks:2*n_tanks])
        TSS_load.append(sum(TSSL))

        TSS_over = perf(TSS_load,setptTSSload)
    else:
        TSS_over = 0

flow_over = perf(total_flow,setptOutflow)

if plot == 1:
    plt.subplot(231)
    for i in range(0,n_tanks):
        plt.plot(max_depths[i]*np.ones(len(tank_depths)), label = "Setpoint for tank " + str(i+1))
    plt.plot(tank_depths)

    plt.subplot(232)
    plt.plot(setptOutflow*np.ones(len(total_flow)), label = "Setpoint")
    plt.plot(total_flow, label = "No control")

    if TSS == 1:
        plt.subplot(233)
        plt.plot(setptTSSload*np.ones(len(TSS_load)), label = "Setpoint")
        plt.plot(TSS_load, label = "No control")

for epsilon in epsilons:
    for zeta in zetas:
        env.reset()

        tank_depths = []
        price = []
        demand = []
        supply = []
        total_flow = []
        TSS_load = []
        gates = []

        done = False; j = 0
        action = [0.5,0.5,0.5]

        while not done:
            j += 1
            state, done = env.step(action)
            tank_depths.append(state[0][0:n_tanks])
            if TSS == 1:
                if j == 1:
                    TSSL = TSScalc(n_tanks, tank_depths[-1], 0, state[0][n_tanks:2*n_tanks])
                else:
                    TSSL = TSScalc(n_tanks, tank_depths[-1], tank_depths[-2], state[0][n_tanks:2*n_tanks])
                TSS_load.append(sum(TSSL))
            else:
                TSS_load = np.zeros(n_tanks)
                zeta = 0.0

            p, PD, PS, tot_flow, action = mbc(state, TSS_load[-1],
                setptOutflow, setptTSSload, beta, epsilon, zeta, max_depths,
                n_tanks, action)

            gates.append(action[0:n_tanks])
            price.append(p)
            demand.append(PD)
            supply.append(PS)
            total_flow.append(tot_flow)

        if TSS == 1:
            TSS_over = perf(TSS_load,setptTSSload)
        else:
            TSS_over = np.zeros(n_tanks)

        flow_over = perf(total_flow,setptOutflow)
        flow_over_cum.append(sum(flow_over))
        TSS_over_cum.append(sum(TSS_over))

        results.append([epsilon, zeta, sum(flow_over), sum(TSS_over)])

        if plot == 1:
            plt.subplot(231)
            plt.plot(tank_depths)

            plt.subplot(232)
            plt.plot(total_flow, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

            if TSS == 1:
                plt.subplot(233)
                plt.plot(TSS_load, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

            plt.subplot(234)
            plt.plot(price, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

            plt.subplot(235)
            plt.plot(demand, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

            plt.subplot(236)
            plt.plot(gates, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

if plot == 1:
    plt.subplot(231)
    plt.ylabel('Tank Depth')
    plt.legend()

    plt.subplot(232)
    plt.ylabel('Total Outflow')
    plt.legend()

    if TSS == 1:
        plt.subplot(233)
        plt.ylabel('TSS Loading')
        plt.legend()

    plt.subplot(234)
    plt.ylabel('Price')
    plt.legend()

    plt.subplot(235)
    plt.ylabel('Demand')

    plt.subplot(236)
    plt.ylabel('Gate opening')

    plt.show()

np.savetxt("../data/results/res.csv",results,delimiter=',')
