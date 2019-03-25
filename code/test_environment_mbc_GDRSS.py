from environment_mbc import Env
from mbc_fn import mbc, mbc_bin, perf, TSScalc
import matplotlib.pyplot as plt
import numpy as np
import pickle
import copy

# Weighting parameters
beta = 1.0 # upstream depth
epsilons = [100.0] # downstream flow
gammas = [0.0] # downstream flow derivative
zetas = [0.0] # downstream TSS loading

# Downstream setpoints
setptFlow = 0.4 # normalized to max_depth
setptFlowDeriv = 0.0
setptTSSload = 0.0

# Control specifications
repTot = 1 # only control every repTot steps
contType = "continuous" # "binary" {0,1} or "continuous" [0,1] gate openings
deriv = 0 # 1 to control for flow derivative; 0 otherwise
# TSS not yet established for GDRSS
TSS = 0 # 1 to control for TSS; 0 otherwise

# Plotting/saving specifications
save = 0 # 1 to save results; 0 otherwise
saveNames = ['iter12_d','iter12_e','iter12_f']
    # first should be no control simulation name (if doing no control simulation);
    # all others should be for control simulations
plot = 1 # 1 to plot results; 0 otherwise
linestyles = ['-','-.'] # linestyles for different parameter trials
colors = ['#00a650','#008bff','#ff4a00','#ffb502','#9200cc','#b4e300','#ff03a0','#00e3ce','#0011ab','#a40000','#bf06b5']
        # colors for each upstream asset
ustream_labels = ['ISD002','ISD003','ISD004']
#ustream_labels = ['ISD006','ISD007','ISD008','ISD009','ISD010']
#ustream_labels = ['ISD011','ISD012','ISD013']
#ustream_labels = ['2','3','4','6','7','8','9','10','11','12','13']
#ustream_labels = ['2','6','11']
noControl = 1 # 1 to include no control simulation; 0 otherwise

# States to pull from simulation (must include upstream and downstream states
# for control objectives)
units = "english" # "english" for English units in .inp file; "metric" otherwise
discharge = 1.0 # discharge coefficient of orifices
state_space = {"depthsN":[],
                "depthsL":["1509","RC1951","1535"],
                #"depthsL":["2160","21853","21950","2201","2388"],
                #"depthsL":["2765","2525","2360"],
                #"depthsL":["1509","RC1951","1535","2160","21853","21950","2201","2388","2765","2525","2360"],
                #"depthsL":["1509","2160","2765"],
                "flows":["1503"],
                #"flows":["21450"],
                #"flows":["27450"],
                #"flows":["Trunk02"],
                "inflows":[]}
n_tanks = len(state_space['depthsL']) # number of upstream tanks/conduits
control_points = ["ISD002_DOWN","ISD003_DOWN","ISD004_DOWN",
                    "ISD002_UP","ISD003_UP","ISD004_UP"]
#control_points = ["ISD006_DOWN","ISD007_DOWN","ISD008_DOWN","ISD009_DOWN","ISD010_DOWN",
#                    "ISD006_UP","ISD007_UP","ISD008_UP","ISD009_UP","ISD010_UP"]
#control_points = ["ISD011_DOWN","ISD012_DOWN","ISD013_DOWN",
#                    "ISD011_UP","ISD012_UP","ISD013_UP"]
#control_points = ["ISD002_DOWN","ISD003_DOWN","ISD004_DOWN","ISD006_DOWN","ISD007_DOWN","ISD008_DOWN","ISD009_DOWN","ISD010_DOWN","ISD011_DOWN","ISD012_DOWN","ISD013_DOWN",
#                    "ISD002_UP","ISD003_UP","ISD004_UP","ISD006_UP","ISD007_UP","ISD008_UP","ISD009_UP","ISD010_UP","ISD011_UP","ISD012_UP","ISD013_UP"]
#control_points = ["ISD002_DOWN","ISD006_DOWN","ISD011_DOWN",
#                    "ISD002_UP","ISD006_UP","ISD011_UP"]
max_depths = [13.45,20.0,14.0]
#max_depths = [15.5,15.5,15.5,15.5,12.25] # upstream tanks/conduits max depths for normalization
#max_depths = [15.5,10.5,11.5]
#max_depths = [13.45,20.0,14.0,15.5,15.5,15.5,15.5,12.25,15.5,10.5,11.5]
orifice_diam = [14.7,9.0,14.0]
#orifice_diam = [15.5,15.5,15.5,15.5,12.25]
#orifice_diam = [15.5,10.5,11.5]
#orifice_diam = [14.7,9.0,14.0,15.5,15.5,15.5,15.5,12.25,15.5,10.5,11.5]
#max_depths = [13.45,15.5,15.5]
max_flow = 198
#max_flow = 247 # downstream max flow for normalization
#max_flow = 373
#max_flow = 1000
routime_step = 10 # routing timestep in seconds

# Input file, state space, and control points
#env = Env("../data/input_files/GDRSS/pyswmm_GDRSS_withISDs_RainEvents_1.inp",
#    state_space,
#    control_points)
env = Env("../data/input_files/GDRSS/GDRSS_simple3_ISD_Rework_GJE_edit_SCT_delete234.inp",
    state_space,
    control_points)

TSS_load = []
flow_over_cum = []
TSS_over_cum = []

if noControl == 1:
    done = False; j = 0
    while not done:
        j += 1
        state, done = env.step(np.hstack((np.ones(n_tanks),np.zeros(n_tanks+1))))
        if j == 1:
            ustream_depths = state[0][0:n_tanks]/max_depths
            dstream_flow = state[0][n_tanks]/max_flow
        else:
            ustream_depths = np.vstack((ustream_depths,state[0][0:n_tanks]/max_depths))
            dstream_flow = np.vstack((dstream_flow,state[0][n_tanks]/max_flow))
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
        for a in range(0,n_tanks):
            plt.subplot(321) # upstream depths
            plt.plot(ustream_depths[:,a],
                label = "No control, " + ustream_labels[a],
                color = colors[a], linestyle = '--')

        plt.subplot(322) # downstream flows
        plt.plot(dstream_flow, label = "No control", color = colors[0])

        if TSS == 1:
            plt.subplot(323) # downstream TSS loading
            plt.plot(setptTSSload*np.ones(len(TSS_load)), label = "Setpoint")

    print('Done with no control')

    if save == 1:
        fileName = '../data/results/no_control/' + saveNames[0] + '.pkl'
        with open(fileName,'w') as f:
            pickle.dump([state_space,ustream_depths,dstream_flow],f)
        print('No control results saved')

k = -1
for epsilon in epsilons:
    for zeta in zetas:
        for gamma in gammas:
            k += 1
            env.reset()

            done = False; j = 0
            action = np.hstack((np.ones(n_tanks),np.zeros(n_tanks)))

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
                uparam = beta
                actPrev = copy.deepcopy(action)
                if contType == "binary":
                    p, PD, PS, action = mbc_bin(ustream, dstream, setpts, uparam,
                                                dparam, n_tanks, action, discharge)
                elif contType == "continuous":
                    p, PD, PS, action = mbc(ustream, dstream, setpts, uparam,
                                            dparam, n_tanks, action, discharge, max_flow, units, orifice_diam)
                actCurr = copy.deepcopy(action)
                if repTot > 1:
                    action = copy.deepcopy(actPrev)
                else:
                    action = copy.deepcopy(actCurr)

                if j == 1:
                    ustream_depths = state[0][0:n_tanks]/max_depths
                    dstream_flow = state[0][n_tanks]/max_flow
                    price = p
                    demands = PD
                    supply = PS
                    gates = action
                else:
                    ustream_depths = np.vstack((ustream_depths,state[0][0:n_tanks]/max_depths))
                    dstream_flow = np.vstack((dstream_flow,state[0][n_tanks]/max_flow))
                    price = np.vstack((price,p))
                    demands = np.vstack((demands,PD))
                    supply = np.vstack((supply,PS))
                    gates = np.vstack((gates,action))

                if repTot > 1:
                    # Step without control
                    gateTrans = np.zeros((n_tanks,repTot+1))
                    for m in range(0,n_tanks):
                        gateTrans[m,:] = np.linspace(actPrev[m],actCurr[m],repTot+1)
                    rep = 0
                    while rep < repTot:
                        rep += 1
                        if done == False:
                            state, done = env.step(action)
                            for m in range(0,n_tanks):
                                action[m] = gateTrans[m,rep]
                                action[m+n_tanks] = 1.0 - gateTrans[m,rep]
                            if j == 1:
                                ustream_depths = state[0][0:n_tanks]/max_depths
                                dstream_flow = state[0][n_tanks]/max_flow
                                price = p
                                demands = PD
                                supply = PS
                                gates = action
                            else:
                                ustream_depths = np.vstack((ustream_depths,state[0][0:n_tanks]/max_depths))
                                dstream_flow = np.vstack((dstream_flow,state[0][n_tanks]/max_flow))
                                price = np.vstack((price,p))
                                demands = np.vstack((demands,PD))
                                supply = np.vstack((supply,PS))
                                gates = np.vstack((gates,action))
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
                for a in range(0,n_tanks):
                    plt.subplot(321)
                    plt.plot(ustream_depths[:,a],
                        label = "Market-based control, " + ustream_labels[a],
                        color = colors[a], linestyle = linestyles[k])

                    plt.subplot(324)
                    plt.plot(demands[:,a],
                        label = "Demand, " + ustream_labels[a],
                        color = colors[a], linestyle = linestyles[k])

                    plt.subplot(326)
                    plt.plot(gates[:,a],
                        label = "Dam down, " + ustream_labels[a],
                        color = colors[a], linestyle = linestyles[k])

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

            print('Done with MBC, epsilon = ' + str(epsilon) +
                    ', gamma = ' + str(gamma) + ', zeta = ' + str(zeta))

            if save == 1:
                if noControl == 1:
                    fileName = '../data/results/control/' + saveNames[k+1] + '.pkl'
                else:
                    fileName = '../data/results/control/' + saveNames[k] + '.pkl'
                with open(fileName,'w') as f:
                    pickle.dump([beta,epsilon,gamma,zeta,setptFlow,setptFlowDeriv,
                                setptTSSload,repTot,contType,state_space,control_points,
                                max_flow,ustream_depths,dstream_flow,demands,price,gates],
                                f)
                print('MBC results saved')

if plot == 1:
    plt.subplot(321)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    #plt.gca().set_title('(1)')
    plt.legend()

    plt.subplot(322)
    plt.plot(setptFlow*np.ones(len(dstream_flow)), label = "Setpoint",
            color = 'k')
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
