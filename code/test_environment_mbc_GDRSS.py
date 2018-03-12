from environment_mbc import Env
from mbc_fn import mbc, mbc_bin, perf, TSScalc
import matplotlib.pyplot as plt
import numpy as np

results = []
plot = 1
TSS = 0

ustream_depths = []
dstream_flow = []
TSS_load = []
flow_over_cum = []
TSS_over_cum = []

beta = 1.0; epsilons = [0.0]; zetas = [0.0]
setptDstream = 300.0
setptTSSload = 4.0

state_space = {"depthsN":[],
                "depthsL":["1509","RC1954","1520"],
                "flows":["1503"],
                "inflows":[]}
n_tanks = 3
control_points = ["ISD002_DOWN","ISD003_DOWN","ISD004_DOWN","ISD002_UP","ISD003_UP","ISD004_UP"]

env = Env("../data/input_files/GDRSS/GDRSS_simple3_ISD_Rework_GJE.inp",
    state_space,
    control_points)

max_depths = [13.45,40.0,14.0]
routime_step = 900

done = False; j = 0
while not done:
    j += 1
    state, done = env.step([1.0,1.0,1.0,0.0,0.0,0.0])
    ustream_depths.append(state[0][0:n_tanks])
    dstream_flow.append(state[0][-1])
    if TSS == 1:
        if j == 1:
            TSSL = TSScalc(n_tanks, tank_depths[-1], 0, state[0][n_tanks:2*n_tanks], state[0][2*n_tanks:3*n_tanks], routime_step)
        else:
            TSSL = TSScalc(n_tanks, tank_depths[-1], tank_depths[-2], state[0][n_tanks:2*n_tanks], state[0][2*n_tanks:3*n_tanks], routime_step)
        TSS_load.append(sum(TSSL))

        TSS_over = perf(TSS_load,setptTSSload)
    else:
        TSS_over = 0

flow_over = perf(dstream_flow,setptDstream)

if plot == 1:
    plt.subplot(231)
    for i in range(0,n_tanks):
        plt.plot(max_depths[i]*np.ones(len(ustream_depths)), label = "Setpoint for tank " + str(i+1))
    plt.plot(ustream_depths)

    plt.subplot(232)
    plt.plot(setptDstream*np.ones(len(dstream_flow)), label = "Setpoint")
    plt.plot(dstream_flow, label = "No control")

    if TSS == 1:
        plt.subplot(233)
        plt.plot(setptTSSload*np.ones(len(TSS_load)), label = "Setpoint")
        plt.plot(TSS_load, label = "No control")

print('Done with no control')

for epsilon in epsilons:
    for zeta in zetas:
        env.reset()

        ustream_depths = []
        price = []
        demand = []
        supply = []
        dstream_flow = []
        TSS_load = []
        gates = []

        done = False; j = 0
        action = [0.5,0.5,0.5,0.0,0.0,0.0]

        while not done:
            j += 1
            state, done = env.step(action)
            ustream_depths.append(state[0][0:n_tanks])
            if TSS == 1:
                if j == 1:
                    TSSL = TSScalc(n_tanks, tank_depths[-1], 0, state[0][n_tanks:2*n_tanks], state[0][2*n_tanks:3*n_tanks], routime_step)
                else:
                    TSSL = TSScalc(n_tanks, tank_depths[-1], tank_depths[-2], state[0][n_tanks:2*n_tanks], state[0][2*n_tanks:3*n_tanks], routime_step)
                TSS_load.append(sum(TSSL))
            else:
                TSS_load = np.zeros(n_tanks)
                zeta = 0.0

            ustream = state[0,0:n_tanks]/max_depths
            dstream = np.array([state[0,-1]])
            setpts = np.array([setptDstream, setptTSSload])
            uparam = beta
            dparam = np.array([epsilon, zeta])
            p, PD, PS, action = mbc(ustream, dstream, setpts, uparam, dparam, n_tanks)

            gates.append(action[0:n_tanks])
            price.append(p)
            demand.append(PD)
            supply.append(PS)
            dstream_flow.append(state[0][-1])

        if TSS == 1:
            TSS_over = perf(TSS_load,setptTSSload)
        else:
            TSS_over = np.zeros(n_tanks)

        flow_over = perf(dstream_flow,setptDstream)
        flow_over_cum.append(sum(flow_over))
        TSS_over_cum.append(sum(TSS_over))

        results.append([epsilon, zeta, sum(flow_over), sum(TSS_over)])

        if plot == 1:
            plt.subplot(231)
            plt.plot(ustream_depths)

            plt.subplot(232)
            plt.plot(dstream_flow, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

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
    plt.ylabel('Upstream Conduit Depth')
    plt.legend()

    plt.subplot(232)
    plt.ylabel('Downstream Flow')
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
