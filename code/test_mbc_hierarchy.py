from environment_mbc import Env
from mbc_fn import mbc, mbc_bin, perf, TSScalc
import matplotlib.pyplot as plt
import numpy as np
import pickle

# Weighting parameters
beta = 1.0 # upstream flow
epsilon = 100.0 # downstream flow

# Downstream setpoints
setptMethod = "automatic" # "manual" to use setpoints established below;
                #"automatic" to determine setpoints for each branch using MBC and setpt_WRRF
setpts = [0.2,0.3,0.2] # same order as branches in n_ISDs
setpt_WRRF = 0.2 # setpoint for flow at WRRF

# Control specifications
contType = "continuous" # "binary" {0,1} or "continuous" [0,1] gate openings
save = 0 # 1 to save results; 0 otherwise
saveNames = ['check']
plot = 1 # 1 to plot results; 0 otherwise
colors = ['#00a650','#008bff','#ff4a00','#ffb502','#9200cc','#b4e300','#ff03a0','#00e3ce','#0011ab','#a40000','#996f3d']
noControl = 1 # 1 to include no control simulation; 0 otherwise
control = 1 # 1 to include control simulation; 0 otherwise

# States to pull from simulation
state_space = {"depthsN":[],
                "depthsL":["2360","2525","2765",
                            "2388","2201","21950","21853","2160",
                            "1535","RC1951","1509"],
                            # depths in conduits upstream of ISDs from
                            # most upstream trunkline branch to most downstream,
                            # from most upstream ISD to most downstream (same
                            # order as control_points)
                "flows":["Trunk02","27450","21450","1503"],
                            # first WRRF influent conduit
                            # then conduits for each trunkline branch from
                            # most upstream to most downstream
                "inflows":[]}
n_trunkline = 3 # number of main trunkline branches
n_ISDs = [3,5,3] # array with number of ISD along each main trunkline branch
                # (from most upstream trunkline branch to most downstream)
control_points = ["ISD013_DOWN","ISD012_DOWN","ISD011_DOWN",
                "ISD010_DOWN","ISD009_DOWN","ISD008_DOWN","ISD007_DOWN","ISD006_DOWN",
                "ISD004_DOWN","ISD003_DOWN","ISD002_DOWN",
                "ISD013_UP","ISD012_UP","ISD011_UP",
                "ISD010_UP","ISD009_UP","ISD008_UP","ISD007_UP","ISD006_UP",
                "ISD004_UP","ISD003_UP","ISD002_UP"]
                # matrix with ISD dam down/up names, from most upstream branch
                # to most downstream, from most upstream ISD to most downstream
max_depths = [11.5,10.5,15.5,
                12.25,15.5,15.5,15.5,15.5,
                14.0,20.0,13.45]
                # upstream tanks/conduits max depths for normalization;
                # should be in same order as "depthsL" in state_space
max_flow_WRRF = 1000 # max flow for normalization of most downstream point
max_flow_dstream = [374,244,412]
routime_step = 10 # routing timestep in seconds
discharge = 1.0 # discharge coefficient of orifices

# Input file, state space, and control points
env = Env("../data/input_files/GDRSS/GDRSS_simple3_ISD_Rework_GJE_edit_SCT_delete234.inp",
        state_space,
        control_points)

if noControl == 1:
    done = False; j = 0
    while not done:
        j += 1
        state, done = env.step(np.hstack((np.ones(sum(n_ISDs)),np.zeros(sum(n_ISDs)))))
        if j == 1:
            ustream_depths = state[0][0:sum(n_ISDs)]/max_depths
            WRRF_flow = state[0][sum(n_ISDs)]/max_flow_WRRF
            dstream_flows = state[0][sum(n_ISDs)+1:sum(n_ISDs)+n_trunkline+1]/max_flow_dstream
        else:
            ustream_depths = np.vstack((ustream_depths,state[0][0:sum(n_ISDs)]/max_depths))
            WRRF_flow = np.vstack((WRRF_flow,state[0][sum(n_ISDs)]/max_flow_WRRF))
            dstream_flows = np.vstack((dstream_flows,state[0][sum(n_ISDs)+1:sum(n_ISDs)+n_trunkline+1]/max_flow_dstream))
    if plot == 1:
        plt.subplot(321)
        for a in range(0,sum(n_ISDs)):
            plt.plot(ustream_depths[:,a],
                        label = "No control, " + control_points[a],
                        color = colors[a], linestyle = '--')

        plt.subplot(322)
        plt.plot(WRRF_flow, label = "No control, WRRF flow", color = colors[0],
                    linestyle = '--')

        plt.subplot(324)
        for a in range(0,n_trunkline):
            plt.plot(dstream_flows[:,a],
                        label = "No control, " + state_space['flows'][a+1],
                        color = colors[a], linestyle = '--')

    print("Done with no control")

if control == 1:
    env.reset()
    done = False; j = 0
    action = np.hstack((np.ones(sum(n_ISDs)),np.zeros(sum(n_ISDs))))

    while not done:
        j += 1
        state, done = env.step(action)
        PDs = np.zeros(sum(n_ISDs))
        PSs = np.zeros(n_trunkline)
        ps = np.zeros(n_trunkline)

        if setptMethod == "automatic":
            ustream = state[0,-n_trunkline:]/max_flow_dstream
            dstream = np.array([state[0,-n_trunkline-1]/max_flow_WRRF])
            setpt = np.array([setpt_WRRF])
            uparam = beta
            dparam = epsilon
            act_b = np.zeros(n_trunkline)
            p_b, PD_b, PS_b, act_b = mbc(ustream, dstream, setpt, uparam,
                                    dparam, n_trunkline, act_b, discharge, max_flow_WRRF)
            if PS_b == 0:
                setpts = np.zeros(n_trunkline)
            else:
                setpts = PD_b/PS_b*setpt_WRRF*max_flow_WRRF/max_flow_dstream

        for b in range(0,n_trunkline):
            ustream = state[0,sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]/max_depths[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
            dstream = np.array([state[0,-n_trunkline+b]/max_flow_dstream[b]])
            setpt = np.array([setpts[b]])
            uparam = beta
            dparam = epsilon
            action_sub_down = np.ones(n_ISDs[b])
            action_sub_up = np.zeros(n_ISDs[b])
            action_sub = np.hstack((action_sub_down,action_sub_up))
            if contType == "binary":
                p, PD, PS, action_sub = mbc_bin(ustream, dstream, setpt, uparam,
                                            dparam, n_ISDs[b], action_sub, discharge)
            elif contType == "continuous":
                p, PD, PS, action_sub = mbc(ustream, dstream, setpt, uparam,
                                        dparam, n_ISDs[b], action_sub, discharge, max_flow_dstream[b])
            action[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = action_sub[:len(action_sub)/2]
            action[sum(n_ISDs[0:b])+sum(n_ISDs):sum(n_ISDs[0:b+1])+sum(n_ISDs)] = action_sub[len(action_sub)/2:]
            PDs[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = PD
            PSs[b] = PS
            ps[b] = p

        if j == 1:
            ustream_depths = state[0][0:sum(n_ISDs)]/max_depths
            WRRF_flow = state[0][sum(n_ISDs)]/max_flow_WRRF
            dstream_flows = state[0][sum(n_ISDs)+1:sum(n_ISDs)+n_trunkline+1]/max_flow_dstream
            price = ps
            demands = PDs
            supply = PSs
            gates = action
            setpts_all = setpts
        else:
            ustream_depths = np.vstack((ustream_depths,state[0][0:sum(n_ISDs)]/max_depths))
            WRRF_flow = np.vstack((WRRF_flow,state[0][sum(n_ISDs)]/max_flow_WRRF))
            dstream_flows = np.vstack((dstream_flows,state[0][sum(n_ISDs)+1:sum(n_ISDs)+n_trunkline+1]/max_flow_dstream))
            price = np.vstack((price,ps))
            demands = np.vstack((demands,PDs))
            supply = np.vstack((supply,PSs))
            gates = np.vstack((gates,action))
            setpts_all = np.vstack((setpts_all,setpts))

    if plot == 1:
        for a in range(0,sum(n_ISDs)):
            plt.subplot(321)
            plt.plot(ustream_depths[:,a],
                        label = "MBC, " + control_points[a],
                        color = colors[a], linestyle = '-')

            plt.subplot(325)
            plt.plot(gates[:,a],
                        label = "Dam down, " + control_points[a],
                        color = colors[a], linestyle = '-')

            plt.subplot(326)
            plt.plot(demands[:,a],
                        label = "Demand, " + control_points[a],
                        color = colors[a], linestyle = '-')

        plt.subplot(322)
        plt.plot(WRRF_flow, label = "MBC, WRRF flow", color = colors[0],
                    linestyle = '-')

        for a in range(0,n_trunkline):
            plt.subplot(324)
            plt.plot(dstream_flows[:,a],
                        label = "MBC, " + state_space['flows'][a+1],
                        color = colors[a], linestyle = '-')

            plt.subplot(326)
            plt.plot(price[:,a],
                        label = "price, " + state_space['flows'][a+1],
                        color = colors[a], linestyle = '--')

    print("Done with MBC")

if plot == 1:
    plt.subplot(321)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.legend()

    plt.subplot(322)
    if setptMethod == "automatic":
        plt.plot(setpt_WRRF*np.ones(len(WRRF_flow)), color = 'k', label = 'Setpoint')
    plt.ylabel('WRRF Normalized Flow')
    plt.legend()

    plt.subplot(324)
    for q in range(0,n_trunkline):
        plt.plot(setpts_all[:,q],
                    label = "Setpoint, " + state_space['flows'][q+1],
                    color = colors[q], linestyle = ':')
    plt.ylabel('Normalized Trunkline Flows')
    plt.legend()

    plt.subplot(325)
    plt.ylabel('Gate Opening')
    plt.legend()

    plt.subplot(326)
    plt.ylabel('Price and Demands')
    plt.legend()

    plt.show()
