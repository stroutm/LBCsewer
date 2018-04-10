from environment_mbc import Env
from mbc_fn import mbc, mbc_bin, perf, TSScalc
import matplotlib.pyplot as plt
import numpy as np

plot = 1
TSS = 0

#ustream_depths = []
ustream_depth_1 = []
ustream_depth_2 = []
ustream_depth_3 = []
dstream_flow = []
TSS_load = []
flow_over_cum = []
TSS_over_cum = []

beta = 1.0; epsilons = [1.0]; zetas = [0.0]#; gammas = [0.0,1.0]
linestyles = ['-','-.']
setptFlow = 0.4 #150.0
setptTSSload = 4.0
#setptFlowDeriv = 0.0
repTot = 1000 # only control every *repTot* steps

state_space = {"depthsN":[],
                "depthsL":["1509","RC1954","1520"],
                "flows":["1503"],
                "inflows":[]}
n_tanks = 3
control_points = ["ISD002_DOWN","ISD003_DOWN","ISD004_DOWN","ISD002_UP","ISD003_UP","ISD004_UP"]

env = Env("../data/input_files/GDRSS/GDRSS_simple3_ISD_Rework_GJE_edit.inp",
    state_space,
    control_points)

max_depths = [13.45,40,14]
max_flow = 585 #1193.0455 # as calculated for conduit 1503
routime_step = 900 # 15 min

done = False; j = 0
while not done:
    j += 1
    state, done = env.step([1.0,1.0,1.0,0.0,0.0,0.0])
    #ustream_depths.append(state[0][0:n_tanks]/max_depths)#ustream_depths.append(state[0][0:n_tanks])
    ustream_depth_1.append(state[0][0]/max_depths[0])
    ustream_depth_2.append(state[0][1]/max_depths[1])
    ustream_depth_3.append(state[0][2]/max_depths[2])
    dstream_flow.append(state[0][n_tanks]/max_flow)
    if TSS == 1:
        if j == 1:
            TSSL = TSScalc(n_tanks, tank_depths[-1], 0, state[0][n_tanks:2*n_tanks], state[0][2*n_tanks:3*n_tanks], routime_step)
        else:
            TSSL = TSScalc(n_tanks, tank_depths[-1], tank_depths[-2], state[0][n_tanks:2*n_tanks], state[0][2*n_tanks:3*n_tanks], routime_step)
        TSS_load.append(sum(TSSL))

        TSS_over = perf(TSS_load,setptTSSload)
    else:
        TSS_over = 0

flow_over = perf(dstream_flow,setptFlow)

if plot == 1:
    plt.subplot(321)
    #for i in range(0,n_tanks):
    #    plt.plot(max_depths[i]*np.ones(len(ustream_depths)), label = "Setpoint for tank " + str(i+1))
    #plt.plot(ustream_depths, label = "No control")
    plt.plot(ustream_depth_1, label = "No control, ISD002", color = '#00a650', linestyle = '--')
    plt.plot(ustream_depth_2, label = "No control, ISD003", color = '#008bff', linestyle = '--')
    plt.plot(ustream_depth_3, label = "No control, ISD004", color = '#ff4a00', linestyle = '--')

    plt.subplot(322)
    plt.plot(setptFlow*np.ones(len(dstream_flow)), label = "Setpoint", color = 'k')#plt.plot(setptFlow*np.ones(len(dstream_flow)), label = "Setpoint")
    plt.plot(dstream_flow, label = "No control", color = '#00a650')

    if TSS == 1:
        plt.subplot(323)
        plt.plot(setptTSSload*np.ones(len(TSS_load)), label = "Setpoint")

print('Done with no control')

k = -1
for epsilon in epsilons:
    for zeta in zetas:
        #for gamma in gammas:
        k += 1
        env.reset()

        #ustream_depths = []
        ustream_depth_1 = []
        ustream_depth_2 = []
        ustream_depth_3 = []
        price = []
        #demand = []
        demand_1 = []
        demand_2 = []
        demand_3 = []
        supply = []
        dstream_flow = []
        TSS_load = []
        #gates = []
        gate_1 = []
        gate_2 = []
        gate_3 = []

        done = False; j = 0
        action = [1.0,1.0,1.0,0.0,0.0,0.0]

        while not done:
            j += 1
            state, done = env.step(action)
            #ustream_depths append here
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
            dstream = np.array([state[0,n_tanks]/max_flow])
            #if j == 1:
            #    dstream = np.array([state[0,n_tanks]/max_flow, state[0,n_tanks]/max_flow])
            #else:
            #    dstream = np.array([state[0,n_tanks]/max_flow, dstream_flow[-1]-state[0,n_tanks]/max_flow])
            setpts = np.array([setptFlow])
            #setpts = np.array([setptFlow, setptFlowDeriv])#setpts = np.array([setptFlow, setptTSSload])
            uparam = beta
            dparam = np.array([epsilon])
            #dparam = np.array([epsilon, gamma])#dparam = np.array([epsilon, zeta])
            actPrev = np.zeros(2*n_tanks)
            actCurr = np.zeros(2*n_tanks)
            for m in range(0,n_tanks):
                if action[m] == 1.0:
                    actPrev[m] = 1.0
                    actPrev[m+n_tanks] = 0.0
                elif action [m] == 0.0:
                    actPrev[m] = 0.0
                    actPrev[m+n_tanks] = 1.0
            p, PD, PS, action = mbc_bin(ustream, dstream, setpts, uparam, dparam, n_tanks, action)
            for m in range(0,n_tanks):
                if action[m] == 1.0:
                    actCurr[m] = 1.0
                    actCurr[m+n_tanks] = 0.0
                elif action [m] == 0.0:
                    actCurr[m] = 0.0
                    actCurr[m+n_tanks] = 1.0
            for m in range(0,n_tanks):
                if actCurr[m] - actPrev[m] > 0.5: #if actPrev[m] == 0.0 and actCurr[m] == 1.0:
                    action[m] = 0.0; action[m+n_tanks] = 1.0
                elif actPrev[m] - actCurr[m] > 0.5:
                    action[m] = 1.0; action[m+n_tanks] = 0.0

                #gates.append(action[0:n_tanks])
            gate_1.append(action[0]); gate_2.append(action[1]); gate_3.append(action[2]); price.append(p)
                #demand.append(PD)
            demand_1.append(PD[0]); demand_2.append(PD[1]); demand_3.append(PD[2]); supply.append(PS)
                #ustream_depths.append(state[0][0:n_tanks]/max_depths)#ustream_depths.append(state[0][0:n_tanks])
            ustream_depth_1.append(state[0][0]/max_depths[0]); ustream_depth_2.append(state[0][1]/max_depths[1]); ustream_depth_3.append(state[0][2]/max_depths[2]); dstream_flow.append(state[0][n_tanks]/max_flow)

            # step w/o control
            gateTrans = np.linspace(0.0,1.0,repTot+1)
            rep = 0
            while rep < repTot:
                rep += 1
                if done == False:
                    # include something to make sure gate opens if upstream > 0.95
                    state, done = env.step(action)
                    for m in range(0,n_tanks):
                        if actCurr[m] - actPrev[m] > 0.5:
                            action[m] = gateTrans[rep]; action[m+n_tanks] = 1-gateTrans[rep]
                        elif actPrev[m] - actCurr[m] > 0.5:
                            action[m] = 1-gateTrans[rep]; action[m+n_tanks] = gateTrans[rep]
                    gate_1.append(action[0]); gate_2.append(action[1]); gate_3.append(action[2]); price.append(p); demand_1.append(PD[0]); demand_2.append(PD[1]); demand_3.append(PD[2]); supply.append(PS); ustream_depth_1.append(state[0][0]/max_depths[0]); ustream_depth_2.append(state[0][1]/max_depths[1]); ustream_depth_3.append(state[0][2]/max_depths[2]); dstream_flow.append(state[0][n_tanks]/max_flow)
                else:
                    break
            action = actCurr

        if TSS == 1:
            TSS_over = perf(TSS_load,setptTSSload)
        else:
            TSS_over = np.zeros(n_tanks)

        flow_over = perf(dstream_flow,setptFlow)
        flow_over_cum.append(sum(flow_over))
        TSS_over_cum.append(sum(TSS_over))

        if plot == 1:
            plt.subplot(321)
            #plt.plot(ustream_depths, label = "Market-based control")#plt.plot(ustream_depths, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))
            plt.plot(ustream_depth_1, label = "Market-based control, ISD002", color = '#00a650', linestyle = linestyles[k])
            plt.plot(ustream_depth_2, label = "Market-based control, ISD003", color = '#008bff', linestyle = linestyles[k])
            plt.plot(ustream_depth_3, label = "Market-based control, ISD004", color = '#ff4a00', linestyle = linestyles[k])

            plt.subplot(322)
            plt.plot(dstream_flow, label = "Market-based control", color = '#008bff', linestyle = linestyles[k])#plt.plot(dstream_flow, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

            if TSS == 1:
                plt.subplot(323)
                plt.plot(TSS_load, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta) + ", gamma = " + str(gamma))

            plt.subplot(324)
            plt.plot(price, label = "Price", color = 'k', linestyle = linestyles[k])#plt.plot(price, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))

            plt.subplot(324)
            #plt.plot(demand, label = "Market-based control")#plt.plot(demand, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))
            plt.plot(demand_1, label = "Demand, ISD002", color = '#00a650', linestyle = linestyles[k])
            plt.plot(demand_2, label = "Demand, ISD003", color = '#008bff', linestyle = linestyles[k])
            plt.plot(demand_3, label = "Demand, ISD004", color = '#ff4a00', linestyle = linestyles[k])

            plt.subplot(326)
            #plt.plot(gates, label = "Market-based control")#plt.plot(gates, label = "MBC, epsilon = " + str(epsilon) + ", zeta = " + str(zeta))
            plt.plot(gate_1, label = "Dam down, ISD002", color = '#00a650', linestyle = linestyles[k])
            plt.plot(gate_2, label = "Dam down, ISD003", color = '#008bff', linestyle = linestyles[k])
            plt.plot(gate_3, label = "Dam down, ISD004", color = '#ff4a00', linestyle = linestyles[k])

        print('Done with MBC, epsilon = ' + str(epsilon) + ', zeta = ' + str(zeta))
        #print('Done with MBC, epsilon = ' + str(epsilon) + ', zeta = ' + str(zeta) + ", gamma = " + str(gamma))

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

    #plt.subplot(224)
    #plt.ylabel('Price')
    #plt.gca().set_title('(4)')
    #plt.legend()

    plt.subplot(324)
    plt.ylabel('Price and Demand')
    #plt.gca().set_title('(3)')
    plt.legend()

    plt.subplot(326)
    plt.ylabel('Gate opening')
    #plt.gca().set_title('(6)')
    plt.legend()

    plt.show()
