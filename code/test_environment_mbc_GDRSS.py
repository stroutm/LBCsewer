from environment_mbc import Env
from mbc_fn import mbc, mbc_bin, perf, TSScalc
import matplotlib.pyplot as plt
import numpy as np

# Weighting parameters
beta = 1.0 # upstream depth
epsilons = [1.0] # downstream flow
gammas = [0.0] # downstream flow derivative
zetas = [0.0] # downstream TSS loading

# Downstream setpoints
setptFlow = 0.3
setptFlowDeriv = 0.0
setptTSSload = 4.0

# Control specifications
repTot = 1 # only control every repTot steps
contType = "continuous" # "binary" {0,1} or "continuous" [0,1] gate openings
deriv = 0 # 1 to control for flow derivative; 0 otherwise
# TSS not yet established for GDRSS
TSS = 0 # 1 to control for TSS; 0 otherwise

# Plotting specifications
plot = 1 # 1 to plot results; 0 otherwise
linestyles = ['-','-.'] # linestyles for different parameter trials
colors = ['#00a650','#008bff','#ff4a00'] # colors for each upstream asset
noControl = 1 # 1 to include no control simulation; 0 otherwise

# States to pull from simulation (must include upstream and downstream states
# for control objectives)
state_space = {"depthsN":[],
                "depthsL":["1509","RC1954","1520"],
                "flows":["1503"],
                "inflows":[]}
n_tanks = 3 # number of upstream tanks/conduits
control_points = ["ISD002_DOWN","ISD003_DOWN","ISD004_DOWN","ISD002_UP",
                    "ISD003_UP","ISD004_UP"]
max_depths = [13.45,40,14] # upstream tanks/conduits max depths for
                            # normalization
max_flow = 585 # downstream max flow for normalization;
                # 585 peak flow for no control;
                # 1193.0455 as calculated for conduit 1503
routime_step = 10 # routing timestep in seconds

# Input file, state space, and control points
env = Env("../data/input_files/GDRSS/GDRSS_simple3_ISD_Rework_GJE_edit.inp",
    state_space,
    control_points)

ustream_depth_1 = []
ustream_depth_2 = []
ustream_depth_3 = []
dstream_flow = []
TSS_load = []
flow_over_cum = []
TSS_over_cum = []

if noControl == 1:
    done = False; j = 0
    while not done:
        j += 1
        state, done = env.step([1.0,1.0,1.0,0.0,0.0,0.0])
        ustream_depth_1.append(state[0][0]/max_depths[0])
        ustream_depth_2.append(state[0][1]/max_depths[1])
        ustream_depth_3.append(state[0][2]/max_depths[2])
        dstream_flow.append(state[0][n_tanks]/max_flow)
        if TSS == 1:
            if j == 1:
                TSSL = TSScalc(n_tanks, tank_depths[-1], 0,
                                state[0][n_tanks:2*n_tanks],
                                state[0][2*n_tanks:3*n_tanks], routime_step)
            else:
                TSSL = TSScalc(n_tanks, tank_depths[-1], tank_depths[-2],
                                state[0][n_tanks:2*n_tanks],
                                state[0][2*n_tanks:3*n_tanks], routime_step)
            TSS_load.append(sum(TSSL))

            TSS_over = perf(TSS_load,setptTSSload)
        else:
            TSS_over = 0

    flow_over = perf(dstream_flow,setptFlow)

    if plot == 1:
        plt.subplot(321)
        plt.plot(ustream_depth_1, label = "No control, ISD002",
                color = colors[0], linestyle = '--')
        plt.plot(ustream_depth_2, label = "No control, ISD003",
                color = colors[1], linestyle = '--')
        plt.plot(ustream_depth_3, label = "No control, ISD004",
                color = colors[2], linestyle = '--')

        plt.subplot(322)
        plt.plot(dstream_flow, label = "No control", color = colors[0])

        if TSS == 1:
            plt.subplot(323)
            plt.plot(setptTSSload*np.ones(len(TSS_load)), label = "Setpoint")

    print('Done with no control')

if plot == 1:
    plt.subplot(322)
    plt.plot(setptFlow*np.ones(len(dstream_flow)), label = "Setpoint",
            color = 'k')

k = -1
for epsilon in epsilons:
    for zeta in zetas:
        for gamma in gammas:
            k += 1
            env.reset()

            ustream_depth_1 = []; ustream_depth_2 = []; ustream_depth_3 = []
            price = []
            demand_1 = []; demand_2 = []; demand_3 = []; supply = []
            dstream_flow = []; TSS_load = []
            gate_1 = []; gate_2 = []; gate_3 = []

            done = False; j = 0
            action = [1.0,1.0,1.0,0.0,0.0,0.0]

            while not done:
                j += 1
                state, done = env.step(action)
                if TSS == 1:
                    if j == 1:
                        TSSL = TSScalc(n_tanks, tank_depths[-1], 0,
                                        state[0][n_tanks:2*n_tanks],
                                        state[0][2*n_tanks:3*n_tanks], routime_step)
                    else:
                        TSSL = TSScalc(n_tanks, tank_depths[-1], tank_depths[-2],
                                        state[0][n_tanks:2*n_tanks],
                                        state[0][2*n_tanks:3*n_tanks], routime_step)
                    TSS_load.append(sum(TSSL))
                else:
                    TSS_load = np.zeros(n_tanks)
                    zeta = 0.0
                ustream = state[0,0:n_tanks]/max_depths
                if TSS == 0 and deriv == 0:
                    dstream = np.array([state[0,n_tanks]/max_flow])
                    setpts = np.array([setptFlow])
                    dparam = np.array([epsilon])
                elif TSS == 1 and deriv == 0:
                    dstream = np.array([state[0,n_tanks]/max_flow, sum(TSSL)])
                    setpts = np.array([setptFlow, setptTSSload])
                    dparam = np.array([epsilon, zeta])
                elif TSS == 0 and deriv == 1:
                    if j == 1:
                        dstream = np.array([state[0,n_tanks]/max_flow,
                                            state[0,n_tanks]/max_flow])
                    else:
                        dstream = np.array([state[0,n_tanks]/max_flow,
                                            dstream_flow[-1]-state[0,n_tanks]/max_flow])
                    setpts = np.array([setptFlow, setptFlowDeriv])
                    dparam = np.array([epsilon, gamma])
                elif TSS == 1 and deriv == 1:
                    if j == 1:
                        dstream = np.array([state[0,n_tanks]/max_flow,
                                            state[0,n_tanks]/max_flow,
                                            sum(TSSL)])
                    else:
                        dstream = np.array([state[0,n_tanks]/max_flow,
                                            dstream_flow[-1]-state[0,n_tanks]/max_flow,
                                            sum(TSSL)])
                    setpts = np.array([setptFlow, setptFlowDeriv, setptTSSload])
                    dparam = np.array([epsilon, gamma, zeta])
                #dstream = np.array([state[0,n_tanks]/max_flow])
                #setpts = np.array([setptFlow])
                uparam = beta # dparam = np.array([epsilon])
                actPrev = np.zeros(2*n_tanks); actCurr = np.zeros(2*n_tanks)
                actPrev = action[:]
                if contType == "binary":
                    p, PD, PS, action = mbc_bin(ustream, dstream, setpts, uparam,
                                                dparam, n_tanks, action)
                elif contType == "continuous":
                    p, PD, PS, action = mbc(ustream, dstream, setpts, uparam,
                                            dparam, n_tanks, action)
                actCurr = action[:]
                action = actPrev[:]

                gate_1.append(action[0]); gate_2.append(action[1])
                gate_3.append(action[2]); price.append(p)
                demand_1.append(PD[0]); demand_2.append(PD[1])
                demand_3.append(PD[2]); supply.append(PS)
                ustream_depth_1.append(state[0][0]/max_depths[0])
                ustream_depth_2.append(state[0][1]/max_depths[1])
                ustream_depth_3.append(state[0][2]/max_depths[2])
                dstream_flow.append(state[0][n_tanks]/max_flow)

                # Step without control
                gateTrans = np.zeros((n_tanks,repTot+1))
                for m in range(0,n_tanks):
                    gateTrans[m,:] = np.linspace(actPrev[m],actCurr[m],repTot+1)
                rep = 0
                while rep < repTot:
                    rep += 1
                    if done == False:
                        # include something to make sure gate opens if upstream > 0.95
                        state, done = env.step(action)
                        for m in range(0,n_tanks):
                            action[m] = gateTrans[m,rep]
                            action[m+n_tanks] = 1.0 - gateTrans[m,rep]
                        gate_1.append(action[0]); gate_2.append(action[1])
                        gate_3.append(action[2]); price.append(p)
                        demand_1.append(PD[0]); demand_2.append(PD[1])
                        demand_3.append(PD[2]); supply.append(PS)
                        ustream_depth_1.append(state[0][0]/max_depths[0])
                        ustream_depth_2.append(state[0][1]/max_depths[1])
                        ustream_depth_3.append(state[0][2]/max_depths[2])
                        dstream_flow.append(state[0][n_tanks]/max_flow)
                    else:
                        break
                action = actCurr[:]

            if TSS == 1:
                TSS_over = perf(TSS_load,setptTSSload)
            else:
                TSS_over = np.zeros(n_tanks)

            flow_over = perf(dstream_flow,setptFlow)
            flow_over_cum.append(sum(flow_over))
            TSS_over_cum.append(sum(TSS_over))

            if plot == 1:
                plt.subplot(321)
                plt.plot(ustream_depth_1, label = "Market-based control, ISD002",
                            color = colors[0], linestyle = linestyles[k])
                plt.plot(ustream_depth_2, label = "Market-based control, ISD003",
                            color = colors[1], linestyle = linestyles[k])
                plt.plot(ustream_depth_3, label = "Market-based control, ISD004",
                            color = colors[2], linestyle = linestyles[k])

                plt.subplot(322)
                plt.plot(dstream_flow, label = "Market-based control",
                            color = colors[1], linestyle = linestyles[k])

                if TSS == 1:
                    plt.subplot(323)
                    plt.plot(TSS_load, label = "MBC, epsilon = " + str(epsilon) +
                                ", zeta = " + str(zeta) + ", gamma = " + str(gamma))

                plt.subplot(324)
                plt.plot(price, label = "Price", color = 'k',
                            linestyle = linestyles[k])

                plt.subplot(324)
                plt.plot(demand_1, label = "Demand, ISD002", color = colors[0],
                            linestyle = linestyles[k])
                plt.plot(demand_2, label = "Demand, ISD003", color = colors[1],
                            linestyle = linestyles[k])
                plt.plot(demand_3, label = "Demand, ISD004", color = colors[2],
                            linestyle = linestyles[k])

                plt.subplot(326)
                plt.plot(gate_1, label = "Dam down, ISD002", color = colors[0],
                            linestyle = linestyles[k])
                plt.plot(gate_2, label = "Dam down, ISD003", color = colors[1],
                            linestyle = linestyles[k])
                plt.plot(gate_3, label = "Dam down, ISD004", color = colors[2],
                            linestyle = linestyles[k])

            print('Done with MBC, epsilon = ' + str(epsilon) +
                    ', gamma = ' + str(gamma) + ', zeta = ' + str(zeta))

if plot == 1:
    plt.subplot(321)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    #plt.gca().set_title('(1)')
    plt.legend()

    plt.subplot(322)
    plt.ylabel('Downstream Normalized Flow')
    #plt.gca().set_title('(2)')
    plt.legend()

    if TSS == 1:
        plt.subplot(323)
        plt.ylabel('TSS Loading')
        #plt.gca().set_title('(3)')
        plt.legend()

    plt.subplot(324)
    plt.ylabel('Price and Demand')
    #plt.gca().set_title('(3)')
    plt.legend()

    plt.subplot(326)
    plt.ylabel('Gate opening')
    #plt.gca().set_title('(6)')
    plt.legend()

    plt.show()
