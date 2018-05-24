from environment_mbc import Env
from mbc_fn import mbc, mbc_noaction, mbc_bin, perf, TSScalc
import matplotlib.pyplot as plt
import numpy as np
import pickle

ISDs = [13,12,11,10,9,8,7,6,4,3,2] # ISDs to use for MBC; elements should be from {2,3,4}U{6,...,13}
n_trunkline = 3 # number of main trunkline branches
n_ISDs = [3,5,3] # array with number of ISD along each main trunkline branch
                # (from most upstream trunkline branch to most downstream)

# Weighting parameters
beta = 1.0 # upstream flow
epsilon = 100.0 # downstream flow

# Downstream setpoints
setptMethod = "automatic" # "manual" to use setpts array established below;
                #"automatic" to determine setpoints for each branch using MBC and setpt_WRRF
setptThres = 1 # 1 if not to exceed setpt; 0 if to achieve setpt
setpts = [0.4,0.4,0.4] # same order as branches in n_ISDs
setpt_WRRF = 0.4 # setpoint for flow at WRRF

# Control specifications
contType = "continuous" # "binary" {0,1} or "continuous" [0,1] gate openings
save = 0 # 1 to save results; 0 otherwise
saveNames = ['check']
plot = 1 # 1 to plot results; 0 otherwise
colors = ['#00a650','#008bff','#ff4a00','#ffb502','#9200cc','#b4e300','#ff03a0','#00e3ce','#0011ab','#a40000','#996f3d']
noControl = 0 # 1 to include no control simulation; 0 otherwise
control = 1 # 1 to include control simulation; 0 otherwise

units = "english" # "english" for English units in .inp file; "metric" otherwise
shapes = "rectangular"
max_flow_WRRF = 534.852 # max flow for normalization of most downstream point
max_flow_dstream = [288.145,155.617,198.472]
# all of the max_flows are redefined after no control case if run
routime_step = 10 # routing timestep in seconds
discharge = 0.61 # discharge coefficient of orifices

state_space = {"depthsN":[],"depthsL":[],"flows":["Trunk02"],"inflows":[]}
control_points = []
max_depths = []
uInvert = []
dInvert = []
orifice_diam_all = []

if 13 in ISDs:
    state_space["depthsN"].append("2355"); state_space["depthsL"].append("2360"); control_points.append("ISD013_DOWN"); max_depths.append(11.5); uInvert.append(604.76); dInvert.append(604.71); orifice_diam_all.append(11.5)
if 12 in ISDs:
    state_space["depthsN"].append("25250"); state_space["depthsL"].append("2525"); control_points.append("ISD012_DOWN"); max_depths.append(10.5); uInvert.append(604.56); dInvert.append(604.51); orifice_diam_all.append(10.5)
if 11 in ISDs:
    state_space["depthsN"].append("2745"); state_space["depthsL"].append("2765"); control_points.append("ISD011_DOWN"); max_depths.append(15.5); uInvert.append(580.86); dInvert.append(580.81); orifice_diam_all.append(15.5)
if 10 in ISDs:
    state_space["depthsN"].append("22201"); state_space["depthsL"].append("2388"); control_points.append("ISD010_DOWN"); max_depths.append(12.25); uInvert.append(603.86); dInvert.append(603.81); orifice_diam_all.append(12.25)
if 9 in ISDs:
    state_space["depthsN"].append("2195"); state_space["depthsL"].append("2201"); control_points.append("ISD009_DOWN"); max_depths.append(15.5); uInvert.append(591.36); dInvert.append(591.31); orifice_diam_all.append(15.5)
if 8 in ISDs:
    state_space["depthsN"].append("2185"); state_space["depthsL"].append("21950"); control_points.append("ISD008_DOWN"); max_depths.append(15.5); uInvert.append(585.26); dInvert.append(585.21); orifice_diam_all.append(15.5)
if 7 in ISDs:
    state_space["depthsN"].append("2170"); state_space["depthsL"].append("21853"); control_points.append("ISD007_DOWN"); max_depths.append(15.5); uInvert.append(578.86); dInvert.append(578.81); orifice_diam_all.append(15.5)
if 6 in ISDs:
    state_space["depthsN"].append("2145"); state_space["depthsL"].append("2160"); control_points.append("ISD006_DOWN"); max_depths.append(15.5); uInvert.append(572.46); dInvert.append(572.46); orifice_diam_all.append(15.5)
if 4 in ISDs:
    state_space["depthsN"].append("1516"); state_space["depthsL"].append("1535"); control_points.append("ISD004_DOWN"); max_depths.append(14.0); uInvert.append(587.36); dInvert.append(587.31); orifice_diam_all.append(14.0)
if 3 in ISDs:
    state_space["depthsN"].append("1952"); state_space["depthsL"].append("RC1951"); control_points.append("ISD003_DOWN"); max_depths.append(20.0); uInvert.append(586.36); dInvert.append(586.31); orifice_diam_all.append(9.0)
if 2 in ISDs:
    state_space["depthsN"].append("1504"); state_space["depthsL"].append("1509"); control_points.append("ISD002_DOWN"); max_depths.append(13.45); uInvert.append(581.66); dInvert.append(581.66); orifice_diam_all.append(14.7)

if 13 in ISDs:
    state_space["depthsN"].append("23554"); control_points.append("ISD013_UP")
if 12 in ISDs:
    state_space["depthsN"].append("25254"); control_points.append("ISD012_UP")
if 11 in ISDs:
    state_space["depthsN"].append("27453"); control_points.append("ISD011_UP")
if 10 in ISDs:
    state_space["depthsN"].append("22204"); control_points.append("ISD010_UP")
if 9 in ISDs:
    state_space["depthsN"].append("21954"); control_points.append("ISD009_UP")
if 8 in ISDs:
    state_space["depthsN"].append("21859"); control_points.append("ISD008_UP")
if 7 in ISDs:
    state_space["depthsN"].append("21703"); control_points.append("ISD007_UP")
if 6 in ISDs:
    state_space["depthsN"].append("21454"); control_points.append("ISD006_UP")
if 4 in ISDs:
    state_space["depthsN"].append("15164"); control_points.append("ISD004_UP")
if 3 in ISDs:
    state_space["depthsN"].append("19523"); control_points.append("ISD003_UP")
if 2 in ISDs:
    state_space["depthsN"].append("15031"); control_points.append("ISD002_UP")

if (13 in ISDs) or (12 in ISDs) or (11 in ISDs):
    state_space["flows"].append("27450")
if (10 in ISDs) or (9 in ISDs) or (8 in ISDs) or (7 in ISDs) or (6 in ISDs):
    state_space["flows"].append("21450")
if (4 in ISDs) or (3 in ISDs) or (2 in ISDs):
    state_space["flows"].append("1503")

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
            ustream_depths = state[0][2*sum(n_ISDs):3*sum(n_ISDs)]/max_depths
            WRRF_flow = state[0][3*sum(n_ISDs)]
            dstream_flows = state[0][-1*n_trunkline:]
        else:
            ustream_depths = np.vstack((ustream_depths,state[0][2*sum(n_ISDs):3*sum(n_ISDs)]/max_depths))
            WRRF_flow = np.vstack((WRRF_flow,state[0][3*sum(n_ISDs)]))
            dstream_flows = np.vstack((dstream_flows,state[0][-1*n_trunkline:]))

    max_flow_WRRF = max(WRRF_flow)
    WRRF_flow = WRRF_flow/max_flow_WRRF
    for q in range(0,n_trunkline):
        max_flow_dstream[q] = max(dstream_flows[:,q])
        dstream_flows[:,q] = dstream_flows[:,q]/max_flow_dstream[q]

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
            ustream = state[0,-n_trunkline:]/max_flow_dstream # dstream flows at branch/trunkline
            dstream = np.array([state[0,-n_trunkline-1]/max_flow_WRRF]) # WRRF flow
            setpt = np.array([setpt_WRRF])
            uparam = beta
            dparam = epsilon
            orifice_diam = np.ones(n_trunkline)
            p_b, PD_b, PS_b = mbc_noaction(ustream, dstream, setpt, uparam, dparam, n_trunkline, setptThres)
            if PS_b == 0:
                setpts = np.zeros(n_trunkline)
            else:
                setpts = PD_b/PS_b*setpt_WRRF*max_flow_WRRF/max_flow_dstream
                #setpts = PD_b/PS_b*min(setpt_WRRF,dstream[0])*max_flow_WRRF/max_flow_dstream

        for b in range(0,n_trunkline):
            ustream = state[0,2*sum(n_ISDs)+sum(n_ISDs[0:b]):2*sum(n_ISDs)+sum(n_ISDs[0:b+1])]/max_depths[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
            dstream = np.array([state[0,-n_trunkline+b]/max_flow_dstream[b]])
            ustream_node_depths = state[0,sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
            dstream_node_depths = state[0,sum(n_ISDs)+sum(n_ISDs[0:b]):sum(n_ISDs)+sum(n_ISDs[0:b+1])]
            setpt = np.array([setpts[b]])
            uparam = beta
            dparam = epsilon
            action_sub_down = np.ones(n_ISDs[b])
            action_sub_up = np.zeros(n_ISDs[b])
            action_sub = np.hstack((action_sub_down,action_sub_up))
            orifice_diam = orifice_diam_all[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
            if contType == "binary":
                p, PD, PS, action_sub = mbc_bin(ustream, dstream, setpt, uparam,
                                            dparam, n_ISDs[b], action_sub, discharge, setptThres)
            elif contType == "continuous":
                p, PD, PS, action_sub = mbc(ustream, dstream, setpt, uparam,
                                        dparam, n_ISDs[b], action_sub, discharge,
                                        max_flow_dstream[b], units, orifice_diam,
                                        shapes, ustream_node_depths, dstream_node_depths,
                                        uInvert[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        dInvert[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        setptThres)
            action[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = action_sub[:len(action_sub)/2]
            action[sum(n_ISDs[0:b])+sum(n_ISDs):sum(n_ISDs[0:b+1])+sum(n_ISDs)] = action_sub[len(action_sub)/2:]
            PDs[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = PD
            PSs[b] = PS
            ps[b] = p

        if j == 1:
            ustream_depths = state[0][2*sum(n_ISDs):3*sum(n_ISDs)]/max_depths
            WRRF_flow = state[0][3*sum(n_ISDs)]/max_flow_WRRF
            dstream_flows = state[0][-1*n_trunkline:]/max_flow_dstream
            price = ps
            demands = PDs
            supply = PSs
            gates = action
            setpts_all = setpts
        else:
            ustream_depths = np.vstack((ustream_depths,state[0][2*sum(n_ISDs):3*sum(n_ISDs)]/max_depths))
            WRRF_flow = np.vstack((WRRF_flow,state[0][3*sum(n_ISDs)]/max_flow_WRRF))
            dstream_flows = np.vstack((dstream_flows,state[0][-1*n_trunkline:]/max_flow_dstream))
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
            plt.plot(setpts_all[:,a],
                        label = "Setpoint, " + state_space['flows'][a+1],
                        color = colors[a], linestyle = ':')

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
    plt.ylabel('Normalized Trunkline Flows')
    plt.legend()

    plt.subplot(325)
    plt.ylabel('Gate Opening')
    plt.legend()

    plt.subplot(326)
    plt.ylabel('Price and Demands')
    plt.legend()

    plt.show()
