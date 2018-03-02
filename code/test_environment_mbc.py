from environment_mbc import Env
from mbc_fn import mbc, mbc_bin, perf
import matplotlib.pyplot as plt
import numpy as np

results = []
plot = 1
TSS = 0

record1 = []
tanks1 = []
total_flow1 = []
TSSload = []
flow_over_cum = []
TSS_over_cum = []

beta = 1.0; epsilons = [0.0]; zetas = [0.0]
setptOutflow = 2.5
setptTSSload = 70

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
    tot_flow = sum(state[0,n_tanks:2*n_tanks])
    total_flow1.append(tot_flow)
    TSSCT = [0.0,0.0,0.0]
    TSSL = [0.0,0.0,0.0]
    if TSS == 1:
        for i in range(0,n_tanks):
            runoff = 10
            TSSconcrunoff = 1000
            if tanks1[-1][i] > 0.01:
                TSSCT[i] = (30*TSSconcrunoff*runoff/(30*state[0][n_tanks+i]+2000*tanks1[-1][i])) * np.exp(-0.05/((tanks1[-2][i]+tanks1[-1][i])/2)*30)
            else:
                TSSCT[i] = 0.0
            TSSL[i] = TSSCT[i] * state[0][n_tanks+i]
        TSSload.append(sum(TSSL))

        TSS_over = perf(TSSload,setptTSSload)
    else:
        TSS_over = 0

flow_over = perf(total_flow1,setptOutflow)

if plot == 1:
    plt.subplot(231)
    for i in range(0,n_tanks):
        plt.plot(max_depths[i]*np.ones(len(tanks1)), label = "Setpoint for tank " + str(i+1))
    plt.plot(tanks1)

    plt.subplot(232)
    plt.plot(setptOutflow*np.ones(len(total_flow1)), label = "Setpoint")
    plt.plot(total_flow1, label = "No control")

    if TSS == 1:
        plt.subplot(233)
        plt.plot(setptTSSload*np.ones(len(TSSload)), label = "Setpoint")
        plt.plot(TSSload, label = "No control")

for epsilon in epsilons:
    for zeta in zetas:
        env.reset()

        record2 = []
        tanks2 = []
        price = []
        demand = []
        supply = []
        total_flow2 = []
        TSSload = []
        gates = []

        done = False
        action = [0.5,0.5,0.5]

        while not done:
            state, done = env.step(action)
            record2.append(state[0])
            tanks2.append(state[0][0:n_tanks])
            TSSCT = [0.0,0.0,0.0]
            TSSL = [0.0,0.0,0.0]
            if TSS == 1:
                for i in range(0,n_tanks):
                    runoff = 10
                    TSSconcrunoff = 1000
                    if tanks2[-1][i] > 0.01:
                        TSSCT[i] = (30*TSSconcrunoff*runoff/(30*state[0][n_tanks+i]+2000*tanks2[-1][i])) * np.exp(-0.05/((tanks2[-2][i]+tanks2[-1][i])/2)*30)
                    else:
                        TSSCT[i] = 0.0
                    TSSL[i] = TSSCT[i] * state[0][n_tanks+i]
                TSSload.append(sum(TSSL))
            else:
                TSSload = np.zeros(n_tanks)
                zeta = 0.0

            p, PD, PS, tot_flow, action = mbc(state, TSSload[-1],
                setptOutflow, setptTSSload, beta, epsilon, zeta, max_depths,
                n_tanks, action)

            gates.append(action[0:n_tanks])
            price.append(p)
            demand.append(PD)
            supply.append(PS)
            total_flow2.append(tot_flow)

        if TSS == 1:
            TSS_over = perf(TSSload,setptTSSload)
        else:
            TSS_over = np.zeros(n_tanks)

        flow_over = perf(total_flow2,setptOutflow)
        flow_over_cum.append(sum(flow_over))
        TSS_over_cum.append(sum(TSS_over))

        results.append([epsilon, zeta, sum(flow_over), sum(TSS_over)])
        #print("MB control (epsilon = " + str(epsilon) + ", zeta = " + str(zeta) + ") flow/TSS over: "
        #    + str(sum(flow_over)) + ", " + str(sum(TSS_over)))

        if plot == 1:
            plt.subplot(231)
            plt.plot(tanks2)

            plt.subplot(232)
            plt.plot(total_flow2, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

            if TSS == 1:
                plt.subplot(233)
                plt.plot(TSSload, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

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
