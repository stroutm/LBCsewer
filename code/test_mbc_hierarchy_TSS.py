from environment_mbc_wq import Env
from mbc_fn import mbc, mbc_multi, mbc_noaction, mbc_noaction_multi, mbc_bin, perf
from GDRSS_fn import GDRSS_build
import matplotlib.pyplot as plt
import numpy as np
import pickle

# Enter ISDs to use for MBC; elements should be from {2,3,4}U{6,...,13}
ISDs = [11,6,2]
#ISDs = [13,12,11,10,9,8,7,6,4,3,2]
# Enter number of main trunkline branches
n_trunkline = 3
# Enter array with number of ISDs along each main trunkline branch, from most
# upstream branch to most downstream
n_ISDs = [1,1,1]
# Based on ISDs, pulls states, parameters, and control points
state_space, control_points, max_depths, uInvert, dInvert, orifice_diam_all, colors, labels = GDRSS_build(ISDs)
# Input file
env = Env("../data/input_files/GDRSS/GDRSS_SCT_simple_ISDs_TSS.inp")

## Weighting parameters
# Enter upstream flooding weight
beta = 1.0
# Enter downstream objective weights based on objective type
epsilon_flow = 10.0
epsilon_TSS = 10.0
#epsilon = 10.0

## Downstream setpoints
# Enter either "manual" to use setpts array establish below or "automatic" to
# determine the setpoints for each branch using MBC and setpt_WRRF
setptMethod = "automatic"
# Enter 1 to not exceed setpoint or 0 to achieve setpoint
setptThres = 0
# Enter branch setpoints if chose "manual" for setptMethod;
# list in same order as n_ISDs
setpts = [0.4,0.5,0.3]
# For objType enter "flow", "TSS", or "both" for downstream objective type;
# "both" considers both objectives simulataneously, weighting based on
# values for epsilon_flow and epsilon_TSS provided above;
# for setpt_WRRF enter setpoint to be used if chose "automatic" for setptMethod;
# if objType == "both", enter both setpt_WRRF_flow and setpt_WRRF_TSS values
#objType = "flow"; setpt_WRRF = 0.4
#objType = "TSS"; setpt_WRRF = 0.2
objType = "both"; setpt_WRRF_flow = 0.4; setpt_WRRF_TSS = 0.2
# Enter "binary" for {0,1} gate openings or "continuous" for [0,1]
contType = "continuous"
# Enter 1 to include no control simulation and 0 otherwise
noControl = 1
# Enter 1 to include control simulation and 0 otherwise
control = 1

## Saving and plotting specifications
# Enter 1 to save results and 0 otherwise
save = 0
# Enter filename to save under if save == 1
saveNames = ['TSS_HIC2018']
# Enter 1 to plot results and 0 otherwise
plot = 1
# Enter 1 to normalize downstream flows in plots and 0 otherwise
normalize = 0

# Enter "english" for English units in .inp file and "metric" otherwise
units = "english"
# Enter "rectangular" for rectangular orifices; otherwise is not developed yet
shapes = "rectangular"
# Enter the max flow for normalization of the WRRF flow;
# if noControl == 1, this will be recalculated using no control flow peak
max_flow_WRRF = 536.684
# Enter the max flow for each branch (recalculated if noControl == 1)
max_flow_dstream = [287.939,154.492,198.450]
# Enter the max TSS load for WRRF (recalculated if noControl == 1)
max_TSSLoad_WRRF = 0.4663
# Enter the max TSS load for each (recalculated if noControl == 1)
max_TSSLoad_dstream = [0.1799,0.1506,0.2338]
# Enter the routing timestep in seconds
routime_step = 10
# Enter the discharge coefficient of orifices
discharge = 0.61

## No control simulation
if noControl == 1:
    done = False; j = 0
    time = np.empty((0,1), float)
    ustream_depths = np.empty((0,len(state_space["depthsL"])), float)
    dstream_flows = np.empty((0,n_trunkline), float)
    dstream_TSSLoad = np.empty((0,n_trunkline), float)
    WRRF_flow = np.empty((0,1), float)
    WRRF_TSS = np.empty((0,1), float)
    WRRF_TSSLoad = np.empty((0,1), float)
    while not done:
        time = np.vstack((time,j/8640.))
        ustream_depths_tmp = []
        for e in range(0,len(state_space["depthsL"])):
            ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(state_space["depthsL"][e])/max_depths[e]))
        ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
        dstream_flows_tmp = []
        dstream_TSSLoad_tmp = []
        for e in range(1,len(state_space["flows"])):
            dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(state_space["flows"][e])))
            dstream_TSSLoad_tmp = np.hstack((dstream_TSSLoad_tmp,env.flow(state_space["flows"][e])*env.get_pollutant_link(state_space["flows"][e])*0.000062428))
        dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
        dstream_TSSLoad = np.vstack((dstream_TSSLoad,dstream_TSSLoad_tmp))
        WRRF_flow = np.vstack((WRRF_flow,env.flow(state_space["flows"][0])))
        WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(state_space["flows"][0])))
        WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))
        j += 1
        done = env.step()

    max_flow_WRRF = max(WRRF_flow)
    max_flow_dstream = np.zeros(n_trunkline)
    for e in range(0,n_trunkline):
        max_flow_dstream[e] = max(dstream_flows[:,e])
        max_TSSLoad_dstream[e] = max(dstream_TSSLoad[:,e])
    max_TSSLoad_WRRF = max(WRRF_TSSLoad)
    #if normalize == 1:
    #    WRRF_flow = WRRF_flow/max_flow_WRRF
    #    WRRF_TSSLoad = WRRF_TSSLoad/max_TSSLoad_WRRF

    print('Sum of WRRF_TSSLoad: ' + '%.2f' % sum(WRRF_TSSLoad))

    if plot == 1:
        plt.subplot(321)
        for a in range(0,sum(n_ISDs)):
            plt.plot(time,ustream_depths[:,a],
                        label = "No control, " + labels[a],
                        color = colors[a], linestyle = ':')

        plt.subplot(322)
        if normalize == 1:
            plt.plot(time,WRRF_flow/max_flow_WRRF, label = "No control, WRRF flow",
                    color = colors[-1], linestyle = ':')
        else:
            plt.plot(time,WRRF_flow, label = "No control, WRRF flow",
                    color = colors[-1], linestyle = ':')

        plt.subplot(323)
        if normalize == 1:
            plt.plot(time,WRRF_TSSLoad/max_TSSLoad_WRRF, label = "No control, WRRF TSS Load",
                    color = colors[-1], linestyle = ':')
        else:
            plt.plot(time,WRRF_TSSLoad, label = "No control, WRRF TSS Load",
                    color = colors[-1], linestyle = ':')

        plt.subplot(324)
        for a in range(0,n_trunkline):
            plt.plot(time,dstream_flows[:,a],
                        label = "No control, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = ':')

    print("Done with no control")

    if save == 1:
        fileName = '../data/results/no_control/' + saveNames[0] + '.pkl'
        with open(fileName,'w') as f:
            pickle.dump([time,ustream_depths,WRRF_flow,WRRF_TSSLoad,dstream_flows],f)
        print('No control results saved')

if control == 1:
    env.reset()
    done = False; j = 0
    time = np.empty((0,1), float)
    ustream_depths = np.empty((0,len(state_space["depthsL"])), float)
    dstream_flows = np.empty((0,n_trunkline), float)
    WRRF_flow = np.empty((0,1), float)
    WRRF_TSS = np.empty((0,1), float)
    WRRF_TSSLoad = np.empty((0,1), float)
    action = np.hstack((np.ones(sum(n_ISDs)),np.zeros(sum(n_ISDs))))

    while not done:
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
                dparam = epsilon_flow
                setpt = np.array([setpt_WRRF])
            elif objType == "TSS":
                WRRF_flow_tmp = env.flow(state_space["flows"][0])
                WRRF_TSS_tmp = env.get_pollutant_link(state_space["flows"][0])
                WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                dstream = np.array([WRRF_TSSLoad_tmp/max_TSSLoad_WRRF])
                dparam = epsilon_TSS
                setpt = np.array([setpt_WRRF])
            elif objType == "both":
                WRRF_flow_tmp = env.flow(state_space["flows"][0])
                WRRF_TSS_tmp = env.get_pollutant_link(state_space["flows"][0])
                WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                dstream = np.array([WRRF_flow_tmp/max_flow_WRRF, WRRF_TSSLoad_tmp/max_TSSLoad_WRRF])
                dparam = np.array([epsilon_flow, epsilon_TSS])
                setpt = np.array([setpt_WRRF_flow, setpt_WRRF_TSS])

            uparam = beta
            #dparam = epsilon
            orifice_diam = np.ones(n_trunkline)
            #p_b, PD_b, PS_b = mbc_noaction(ustream, dstream, setpt, uparam, dparam, n_trunkline, setptThres)
            if (objType == "flow") or (objType == "TSS"):
                p_b, PD_b, PS_b = mbc_noaction(ustream, dstream, setpt, uparam, dparam, n_trunkline, setptThres)
            elif objType == "both":
                p_b, PD_b, PS_b = mbc_noaction_multi(ustream, dstream, setpt, uparam, dparam, n_trunkline, setptThres)
            if PS_b == 0:
                setpts = np.zeros(n_trunkline)
            else:
                if objType == "flow":
                    setpts = PD_b/PS_b*setpt_WRRF*max_flow_WRRF/max_flow_dstream
                elif objType == "TSS":
                    setpts = PD_b/PS_b*setpt_WRRF*max_TSSLoad_WRRF/max_TSSLoad_dstream
                elif objType == "both":
                    setpts_flow = PD_b/PS_b*setpt_WRRF_flow*max_flow_WRRF/max_flow_dstream
                    setpts_TSS = PD_b/PS_b*setpt_WRRF_TSS*max_TSSLoad_WRRF/max_TSSLoad_dstream

        for b in range(0,n_trunkline):
            branch_depths = []
            ustream_node_depths = []
            dstream_node_depths = []
            ustream_node_TSSConc = []
            for e in range(0,n_ISDs[b]):
                branch_depths = np.hstack((branch_depths,env.depthL(state_space["depthsL"][sum(n_ISDs[0:b])+e])))
                ustream_node_depths = np.hstack((ustream_node_depths,env.depthN(state_space["depthsN"][sum(n_ISDs[0:b])+e])))
                dstream_node_depths = np.hstack((dstream_node_depths,env.depthN(state_space["depthsN"][sum(n_ISDs)+sum(n_ISDs[0:b])+e])))
                ustream_node_TSSConc = np.hstack((ustream_node_TSSConc,env.get_pollutant_node(state_space["depthsN"][e])))
            ustream = branch_depths/max_depths[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
            if objType == "flow":
                dn_flow_tmp = env.flow(state_space["flows"][b+1])
                dstream = np.array([dn_flow_tmp/max_flow_dstream[b]])
                setpt = np.array([setpts[b]])
            elif objType == "TSS":
                dn_flow_tmp = env.flow(state_space["flows"][b+1])
                dn_TSS_tmp = env.get_pollutant_link(state_space["flows"][b+1])
                dn_TSSLoad_tmp = dn_flow_tmp * dn_TSS_tmp * 0.000062428
                dstream = np.array([dn_TSSLoad_tmp/max_TSSLoad_dstream[b]])
                setpt = np.array([setpts[b]])
            elif objType == "both":
                dn_flow_tmp = env.flow(state_space["flows"][b+1])
                dn_TSS_tmp = env.get_pollutant_link(state_space["flows"][b+1])
                dn_TSSLoad_tmp = dn_flow_tmp * dn_TSS_tmp * 0.000062428
                dstream = np.array([[dn_flow_tmp/max_flow_dstream[b]], [dn_TSSLoad_tmp/max_TSSLoad_dstream[b]]])
                setpt = np.array([[setpts_flow[b]], [setpts_TSS[b]]])

            uparam = beta
            #dparam = epsilon

            action_sub_down = np.ones(n_ISDs[b])
            action_sub_up = np.zeros(n_ISDs[b])
            action_sub = np.hstack((action_sub_down,action_sub_up))
            orifice_diam = orifice_diam_all[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
            if contType == "binary":
                p, PD, PS, action_sub = mbc_bin(ustream, dstream, setpt, uparam,
                                            dparam, n_ISDs[b], action_sub, discharge, setptThres)
            elif contType == "continuous":
                if (objType == "flow") or (objType == "TSS"):
                    p, PD, PS, action_sub = mbc(ustream, dstream, setpt, uparam,
                                        dparam, n_ISDs[b], action_sub, discharge,
                                        max_flow_dstream[b], max_TSSLoad_dstream[b], units, orifice_diam,
                                        shapes, ustream_node_depths, dstream_node_depths,
                                        uInvert[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        dInvert[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        setptThres, objType, ustream_node_TSSConc)
                elif objType == "both":
                    p, PD, PS, action_sub = mbc_multi(ustream, dstream, setpt, uparam,
                                        dparam, n_ISDs[b], action_sub, discharge,
                                        max_flow_dstream[b], max_TSSLoad_dstream[b], units, orifice_diam,
                                        shapes, ustream_node_depths, dstream_node_depths,
                                        uInvert[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        dInvert[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        setptThres, objType, ustream_node_TSSConc)
            action[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = action_sub[:len(action_sub)/2]
            action[sum(n_ISDs[0:b])+sum(n_ISDs):sum(n_ISDs[0:b+1])+sum(n_ISDs)] = action_sub[len(action_sub)/2:]
            PDs[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = PD
            PSs[b] = PS
            ps[b] = p

            for e in range(0,n_ISDs[b]):
                env.set_gate(control_points[sum(n_ISDs[0:b])+e], action[sum(n_ISDs[0:b])+e])
                env.set_gate(control_points[sum(n_ISDs)+sum(n_ISDs[0:b])+e], action[sum(n_ISDs)+sum(n_ISDs[0:b])+e])

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

        if j == 1:
            price = ps
            demands = PDs
            supply = PSs
            gates = action
            if (objType == "flow") or (objType == "TSS"):
                setpts_all = setpts
        else:
            price = np.vstack((price,ps))
            demands = np.vstack((demands,PDs))
            supply = np.vstack((supply,PSs))
            gates = np.vstack((gates,action))
            if (objType == "flow") or (objType == "TSS"):
                setpts_all = np.vstack((setpts_all,setpts))

    print('Sum of WRRF_TSSLoad: ' + '%.2f' % sum(WRRF_TSSLoad))

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
            plt.plot(time,WRRF_flow/max_flow_WRRF, label = "MBC, WRRF flow",
                    color = colors[-1], linestyle = '-')
            if setptMethod == "automatic" and objType == "flow":
                plt.plot(time,setpt_WRRF*np.ones(len(WRRF_flow)),
                    color = 'k', label = 'Setpoint')
            elif setptMethod == "automatic" and objType == "flow":
                plt.plot(time,setpt_WRRF_flow*np.ones(len(WRRF_flow)),
                    color = 'k', label = 'Setpoint')
        else:
            plt.plot(time,WRRF_flow, label = "MBC, WRRF flow",
                    color = colors[-1], linestyle = '-')
            if setptMethod == "automatic" and objType == "flow":
                plt.plot(time,max_flow_WRRF*setpt_WRRF*np.ones(len(WRRF_flow)),
                    color = 'k', label = 'Setpoint')
            elif setptMethod == "automatic" and objType == "both":
                plt.plot(time,max_flow_WRRF*setpt_WRRF_flow*np.ones(len(WRRF_flow)),
                    color = 'k', label = 'Setpoint')

        plt.subplot(323)
        if normalize == 1:
            plt.plot(time,WRRF_TSSLoad/max_TSSLoad_WRRF, label = "MBC, WRRF TSS Load",
                    color = colors[-1], linestyle = '-')
            if setptMethod == "automatic" and objType == "TSS":
                plt.plot(time,setpt_WRRF*np.ones(len(WRRF_TSSLoad)), label = 'Setpoint',
                        color = 'k')
            elif setptMethod == "automatic" and objType == "both":
                plt.plot(time,setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), label = 'Setpoint',
                        color = 'k')
        else:
            plt.plot(time,WRRF_TSSLoad, label = "No control, WRRF TSS Load",
                    color = colors[-1], linestyle = '-')
            if setptMethod == "automatic" and objType == "TSS":
                plt.plot(time,max_TSSLoad_WRRF*setpt_WRRF*np.ones(len(WRRF_TSSLoad)), label = 'Setpoint',
                        color = 'k')
            elif setptMethod == "automatic" and objType == "both":
                plt.plot(time,max_TSSLoad_WRRF*setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), label = 'Setpoint',
                        color = 'k')

        for a in range(0,n_trunkline):
            plt.subplot(324)
            if normalize == 1:
                plt.plot(time,dstream_flows[:,a]/max_flow_dstream[a],
                        label = "MBC, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = '-')
                if objType == "flow":
                    plt.plot(time,setpts_all[:,a],
                        label = "Setpoint, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = '--')
            else:
                plt.plot(time,dstream_flows[:,a],
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
            pickle.dump([time,ustream_depths,WRRF_flow,setpt_WRRF,max_flow_WRRF,WRRF_TSSLoad,dstream_flows,setpts_all,max_flow_dstream,demands,price,gates],f)
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
