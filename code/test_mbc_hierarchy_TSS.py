from environment_mbc_wq import Env
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
epsilon = 10.0 # downstream flow

# Downstream setpoints
setptMethod = "automatic" # "manual" to use setpts array established below;
                #"automatic" to determine setpoints for each branch using MBC and setpt_WRRF
setptThres = 0 # 1 if not to exceed setpt; 0 if to achieve setpt
setpts = [0.4,0.5,0.3] # same order as branches in n_ISDs
#objType = "flow"; setpt_WRRF = 0.4 # setpoint for flow at WRRF
objType = "TSS"; setpt_WRRF = 0.1 # setpoint for TSS at WRRF

# Control specifications
contType = "continuous" # "binary" {0,1} or "continuous" [0,1] gate openings
save = 0 # 1 to save results; 0 otherwise
saveNames = ['TSS']
plot = 1 # 1 to plot results; 0 otherwise
normalize = 0 # 1 to normalize downstream flows for plotting; 0 otherwise
#colors = ['#00a650','#008bff','#ff4a00','#ffb502','#9200cc','#b4e300','#ff03a0','#00e3ce','#0011ab','#a40000','#996f3d']
colors = []
labels = []
noControl = 0 # 1 to include no control simulation; 0 otherwise
control = 1 # 1 to include control simulation; 0 otherwise

units = "english" # "english" for English units in .inp file; "metric" otherwise
shapes = "rectangular"
max_flow_WRRF = 534.852 # max flow for normalization of most downstream point
max_flow_dstream = [288.145,155.617,198.472]
max_TSSLoad_WRRF = 0.45
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
    state_space["depthsN"].append("2355"); state_space["depthsL"].append("2360"); control_points.append("ISD013_DOWN"); max_depths.append(11.5); uInvert.append(604.76); dInvert.append(604.71); orifice_diam_all.append(11.5); colors.append('#276278'); labels.append('K'); state_space["inflows"].append("RC12355")
if 12 in ISDs:
    state_space["depthsN"].append("25250"); state_space["depthsL"].append("2525"); control_points.append("ISD012_DOWN"); max_depths.append(10.5); uInvert.append(604.56); dInvert.append(604.51); orifice_diam_all.append(10.5); colors.append('#167070'); labels.append('J'); state_space["inflows"].append("RC12521"); state_space["inflows"].append("RC12520"); state_space["inflows"].append("RC12770")
if 11 in ISDs:
    state_space["depthsN"].append("2745"); state_space["depthsL"].append("2765"); control_points.append("ISD011_DOWN"); max_depths.append(15.5); uInvert.append(580.86); dInvert.append(580.81); orifice_diam_all.append(15.5); colors.append('#55a6a6'); labels.append('I'); state_space["inflows"].append("RC12350"); state_space["inflows"].append("RC12345"); state_space["inflows"].append("RC12315"); state_space["inflows"].append("RC12765")
if 10 in ISDs:
    state_space["depthsN"].append("22201"); state_space["depthsL"].append("2388"); control_points.append("ISD010_DOWN"); max_depths.append(12.25); uInvert.append(603.86); dInvert.append(603.81); orifice_diam_all.append(12.25); colors.append('#b5491a'); labels.append('H'); state_space["inflows"].append("RC12397"); state_space["inflows"].append("RC12389")
if 9 in ISDs:
    state_space["depthsN"].append("2195"); state_space["depthsL"].append("2201"); control_points.append("ISD009_DOWN"); max_depths.append(15.5); uInvert.append(591.36); dInvert.append(591.31); orifice_diam_all.append(15.5); colors.append('#fe6625'); labels.append('G'); state_space["inflows"].append("RC12201"); state_space["inflows"].append("RC12200")
if 8 in ISDs:
    state_space["depthsN"].append("2185"); state_space["depthsL"].append("21950"); control_points.append("ISD008_DOWN"); max_depths.append(15.5); uInvert.append(585.26); dInvert.append(585.21); orifice_diam_all.append(15.5); colors.append('#fe9262'); labels.append('F')
if 7 in ISDs:
    state_space["depthsN"].append("2170"); state_space["depthsL"].append("21853"); control_points.append("ISD007_DOWN"); max_depths.append(15.5); uInvert.append(578.86); dInvert.append(578.81); orifice_diam_all.append(15.5); colors.append('#fb9334'); labels.append('E')
if 6 in ISDs:
    state_space["depthsN"].append("2145"); state_space["depthsL"].append("2160"); control_points.append("ISD006_DOWN"); max_depths.append(15.5); uInvert.append(572.46); dInvert.append(572.46); orifice_diam_all.append(15.5); colors.append('#ffb16c'); labels.append('D'); state_space["inflows"].append("RC32160"); state_space["inflows"].append("RC3214500")
if 4 in ISDs:
    state_space["depthsN"].append("1516"); state_space["depthsL"].append("1535"); control_points.append("ISD004_DOWN"); max_depths.append(14.0); uInvert.append(587.36); dInvert.append(587.31); orifice_diam_all.append(14.0); colors.append('#414a4f'); labels.append('C'); state_space["inflows"].append("RC11570"); state_space["inflows"].append("RC11571"); state_space["inflows"].append("RC11550"); state_space["inflows"].append("RC11545"); state_space["inflows"].append("RC11535")
if 3 in ISDs:
    state_space["depthsN"].append("1952"); state_space["depthsL"].append("RC1951"); control_points.append("ISD003_DOWN"); max_depths.append(20.0); uInvert.append(586.36); dInvert.append(586.31); orifice_diam_all.append(9.0); colors.append('#006592'); labels.append('B'); state_space["inflows"].append("RC1951")
if 2 in ISDs:
    state_space["depthsN"].append("1504"); state_space["depthsL"].append("1509"); control_points.append("ISD002_DOWN"); max_depths.append(13.45); uInvert.append(581.66); dInvert.append(581.66); orifice_diam_all.append(14.7); colors.append('#003d59'); labels.append('A'); state_space["inflows"].append("RC19523")

if 13 in ISDs:
    state_space["depthsN"].append("23554"); control_points.append("ISD013_UP"); state_space["inflows"].append("2351")
if 12 in ISDs:
    state_space["depthsN"].append("25254"); control_points.append("ISD012_UP"); state_space["inflows"].append("25251")
if 11 in ISDs:
    state_space["depthsN"].append("27453"); control_points.append("ISD011_UP"); state_space["inflows"].append("27450")
if 10 in ISDs:
    state_space["depthsN"].append("22204"); control_points.append("ISD010_UP"); state_space["inflows"].append("22202")
if 9 in ISDs:
    state_space["depthsN"].append("21954"); control_points.append("ISD009_UP"); state_space["inflows"].append("21950")
if 8 in ISDs:
    state_space["depthsN"].append("21859"); control_points.append("ISD008_UP"); state_space["inflows"].append("21852")
if 7 in ISDs:
    state_space["depthsN"].append("21703"); control_points.append("ISD007_UP"); state_space["inflows"].append("21700")
if 6 in ISDs:
    state_space["depthsN"].append("21454"); control_points.append("ISD006_UP"); state_space["inflows"].append("21450")
if 4 in ISDs:
    state_space["depthsN"].append("15164"); control_points.append("ISD004_UP"); state_space["inflows"].append("1515")
if 3 in ISDs:
    state_space["depthsN"].append("19523"); control_points.append("ISD003_UP"); state_space["inflows"].append("19520")
if 2 in ISDs:
    state_space["depthsN"].append("15031"); control_points.append("ISD002_UP"); state_space["inflows"].append("1503")

if (13 in ISDs) or (12 in ISDs) or (11 in ISDs):
    state_space["flows"].append("27450"); colors.append('#167070'); labels.append('I-K')
if (10 in ISDs) or (9 in ISDs) or (8 in ISDs) or (7 in ISDs) or (6 in ISDs):
    state_space["flows"].append("21450"); colors.append('#fe6625'); labels.append('D-H')
if (4 in ISDs) or (3 in ISDs) or (2 in ISDs):
    state_space["flows"].append("1503"); colors.append('#003d59'); labels.append('A-C')

colors.append('#66747c')

# Input file
env = Env("../data/input_files/GDRSS/GDRSS_SCT_simple_ISDs_TSS.inp")

if noControl == 1:
    done = False; j = 0
    ustream_depths = []
    dstream_flows = []
    while not done:
        if j == 0:
            time = j/8640.
        else:
            time = np.vstack((time,j/8640.))
        j += 1
        done = env.step()

        if j == 1:
            for e in range(0,len(state_space["depthsL"])):
                ustream_depths = np.hstack((ustream_depths,env.depthL(state_space["depthsL"][e])/max_depths[e]))
            for e in range(1,len(state_space["flows"])):
                dstream_flows = np.hstack((dstream_flows,env.flow(state_space["flows"][e])))
            WRRF_flow = env.flow(state_space["flows"][0])
            WRRF_TSS = env.get_pollutant_link(state_space["flows"][0])
            WRRF_TSSLoad = WRRF_flow * WRRF_TSS * 0.000062428

        else:
            ustream_depths_tmp = []
            for e in range(0,len(state_space["depthsL"])):
                ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(state_space["depthsL"][e])/max_depths[e]))
            ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
            dstream_flows_tmp = []
            for e in range(1,len(state_space["flows"])):
                dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(state_space["flows"][e])))
            dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
            WRRF_flow = np.vstack((WRRF_flow,env.flow(state_space["flows"][0])))
            WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(state_space["flows"][0])))
            WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))

    max_flow_WRRF = max(WRRF_flow)
    max_TSSLoad_WRRF = max(WRRF_TSSLoad)
    if normalize == 1:
        WRRF_flow = WRRF_flow/max_flow_WRRF
        WRRF_TSSLoad = WRRF_TSSLoad/max_TSSLoad_WRRF

    if plot == 1:
        plt.subplot(321)
        for a in range(0,sum(n_ISDs)):
            plt.plot(time,ustream_depths[:,a],
                        label = "No control, " + labels[a],
                        color = colors[a], linestyle = ':')

        plt.subplot(322)
        plt.plot(time,WRRF_flow, label = "No control, WRRF flow", color = colors[-1],
                    linestyle = ':')

        plt.subplot(323)
        plt.plot(time,WRRF_TSSLoad, label = "No control, WRRF TSS Load", color = colors[-1],
                    linestyle = ':')

        plt.subplot(324)
        for a in range(0,n_trunkline):
            plt.plot(time,dstream_flows[:,a],
                        label = "No control, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = ':')

    print("Done with no control")

    if save == 1:
        fileName = '../data/results/no_control/' + saveNames[0] + '.pkl'
        with open(fileName,'w') as f:
            pickle.dump([time,ustream_depths,WRRF_flow,TSSWRRFLoad_all,dstream_flows],f)
        print('No control results saved')
        print(done)

if control == 1:
    env.reset()
    done = False; j = 0
    ustream_depths = []
    dstream_flows = []
    action = np.hstack((np.ones(sum(n_ISDs)),np.zeros(sum(n_ISDs))))

    while not done:
        if j == 0:
            time = j/8640.
        else:
            time = np.vstack((time,j/8640.))
        j += 1
        done = env.step()
        PDs = np.zeros(sum(n_ISDs))
        PSs = np.zeros(n_trunkline)
        ps = np.zeros(n_trunkline)

        if setptMethod == "automatic":
            ustream = np.zeros(n_trunkline)
            for b in range(0,n_trunkline):
                branch_depths = []
                for e in range(0,n_ISDs[b]):
                    branch_depths = np.hstack((branch_depths,env.depthL(state_space["depthsL"][sum(n_ISDs[0:b])+e])))
                ustream[b] = max(branch_depths/max_depths[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])])
            if objType == "flow":
                WRRF_flow_tmp = env.flow(state_space["flows"][0])
                dstream = np.array([WRRF_flow_tmp/max_flow_WRRF])
            elif objType == "TSS":
                WRRF_flow_tmp = env.flow(state_space["flows"][0])
                WRRF_TSS_tmp = env.get_pollutant_link(state_space["flows"][0])
                WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                dstream = np.array([WRRF_TSSLoad_tmp/max_TSSLoad_WRRF])

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
            branch_depths = []
            for e in range(0,n_ISDs[b]):
                branch_depths = np.hstack((branch_depths,env.depthL(state_space["depthsL"][sum(n_ISDs[0:b])+e])))
            ustream = branch_depths/max_depths[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
            if objType == "flow":
                dn_flow_tmp = env.flow(state_space["flows"][b+1])
                dstream = np.array([WRRF_flow_tmp/max_flow_WRRF])
            elif objType == "TSS":
                WRRF_flow_tmp = env.flow(state_space["flows"][b+1])
                WRRF_TSS_tmp = env.get_pollutant_link(state_space["flows"][b+1])
                WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                dstream = np.array([WRRF_TSSLoad_tmp/max_TSSLoad_WRRF])
            ustream_node_depths = []
            dstream_node_depths = []
            for e in range(0,n_ISDs[b]):
                ustream_node_depths = np.hstack((ustream_node_depths,env.depthN(state_space["depthsN"][sum(n_ISDs[0:b])+e])))
                dstream_node_depths = np.hstack((dstream_node_depths,env.depthN(state_space["depthsN"][sum(n_ISDs)+sum(n_ISDs[0:b])+e])))
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

            for e in range(0,n_ISDs[b]):
                env.set_gate(control_points[sum(n_ISDs[0:b])+e], action[sum(n_ISDs[0:b])+e])
                env.set_gate(control_points[sum(n_ISDs)+sum(n_ISDs[0:b])+e], action[sum(n_ISDs)+sum(n_ISDs[0:b])+e])

        if j == 1:
            for e in range(0,len(state_space["depthsL"])):
                ustream_depths = np.hstack((ustream_depths,env.depthL(state_space["depthsL"][e])/max_depths[e]))
            for e in range(1,len(state_space["flows"])):
                dstream_flows = np.hstack((dstream_flows,env.flow(state_space["flows"][e])))
            WRRF_flow = env.flow(state_space["flows"][0])
            WRRF_TSS = env.get_pollutant_link(state_space["flows"][0])
            WRRF_TSSLoad = WRRF_flow * WRRF_TSS * 0.000062428
            price = ps
            demands = PDs
            supply = PSs
            gates = action
            setpts_all = setpts
        else:
            ustream_depths_tmp = []
            for e in range(0,len(state_space["depthsL"])):
                ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(state_space["depthsL"][e])/max_depths[e]))
            ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
            dstream_flows_tmp = []
            for e in range(1,len(state_space["flows"])):
                dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(state_space["flows"][e])))
            dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
            WRRF_flow = np.vstack((WRRF_flow,env.flow(state_space["flows"][0])))
            WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(state_space["flows"][0])))
            WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))
            price = np.vstack((price,ps))
            demands = np.vstack((demands,PDs))
            supply = np.vstack((supply,PSs))
            gates = np.vstack((gates,action))
            setpts_all = np.vstack((setpts_all,setpts))

    if plot == 1:
        for a in range(0,sum(n_ISDs)):
            plt.subplot(321)
            plt.plot(time,ustream_depths[:,a],
                        label = "MBC, " + labels[a],
                        color = colors[a], linestyle = '-')

            plt.subplot(325)
            plt.plot(time,gates[:,a],
                        label = "Dam down, " + labels[a],
                        color = colors[a], linestyle = '-')

            plt.subplot(326)
            plt.plot(time,demands[:,a],
                        label = "Demand, " + labels[a],
                        color = colors[a-n_trunkline-1], linestyle = '-')

        plt.subplot(322)
        if normalize == 1:
            plt.plot(time,WRRF_flow/max_flow_WRRF, label = "MBC, WRRF flow", color = colors[-1],
                    linestyle = '-')
            if setptMethod == "automatic" and objType == "flow":
                plt.plot(time,setpt_WRRF*np.ones(len(WRRF_flow)), color = 'k', label = 'Setpoint')
        else:
            plt.plot(time,WRRF_flow, label = "MBC, WRRF flow", color = colors[-1],
                    linestyle = '-')
            if setptMethod == "automatic" and objType == "flow":
                plt.plot(time,max_flow_WRRF*setpt_WRRF*np.ones(len(WRRF_flow)), color = 'k', label = 'Setpoint')

        plt.subplot(323)
        if normalize == 1:
            plt.plot(time,WRRF_TSSLoad/max_TSSLoad_WRRF, label = "MBC, WRRF TSS Load", color = colors[-1],
                    linestyle = '-')
        else:
            plt.plot(time,WRRF_TSSLoad, label = "No control, WRRF TSS Load", color = colors[-1],
                    linestyle = '-')
        if setptMethod == "automatic" and objType == "TSS":
            plt.plot(time,setpt_WRRF*np.ones(len(WRRF_TSSLoad)), color = 'k', label = 'Setpoint')

        for a in range(0,n_trunkline):
            plt.subplot(324)
            if normalize == 1:
                plt.plot(time,dstream_flows[:,a],
                        label = "MBC, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = '-')
                if objType == "flow":
                    plt.plot(time,setpts_all[:,a],
                            label = "Setpoint, " + labels[a-n_trunkline],
                            color = colors[a-n_trunkline-1], linestyle = '--')
            else:
                plt.plot(time,max_flow_dstream[a]*dstream_flows[:,a],
                        label = "MBC, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = '-')
                if objType == "flow":
                    plt.plot(time,max_flow_dstream[a]*setpts_all[:,a],
                            label = "Setpoint, " + labels[a-n_trunkline],
                            color = colors[a-n_trunkline-1], linestyle = '--')

            plt.subplot(326)
            plt.plot(time,price[:,a],
                        label = "price, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = '--')

    print("Done with MBC")
    if save == 1:
        fileName = '../data/results/control/' + saveNames[0] + '.pkl'
        with open(fileName,'w') as f:
            pickle.dump([time,ustream_depths,WRRF_flow,setpt_WRRF,max_flow_WRRF,TSSWRRFLoad_all,dstream_flows,setpts_all,max_flow_dstream,demands,price,gates],f)
        print('Control results saved')

if plot == 1:
    plt.subplot(321)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    #plt.legend()

    plt.subplot(322)
    if normalize == 1:
        plt.ylim(0,1)
    #else:
    #    plt.ylim(0,600)
    plt.ylabel('WRRF Flow ($\mathregular{ft^3/s}$)')
    #plt.legend()

    plt.subplot(323)
    plt.ylabel('WRRF TSS Load ($\mathregular{lb/s}$)')
    #plt.legend()

    plt.subplot(324)
    plt.ylabel('Branch Flows ($\mathregular{ft^3/s}$)')
    if normalize == 1:
        plt.ylim(0,1)
    #else:
    #    plt.ylim(0,300)
    #plt.legend()

    plt.subplot(325)
    plt.ylabel('Gate Opening')
    plt.ylim(0,1)
    #plt.legend()

    plt.subplot(326)
    plt.ylabel('Price and Demands')
    #plt.legend()

    plt.show()
