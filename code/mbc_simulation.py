import numpy as np
import copy
from mbc_fn import mbc, mbc_multi, mbc_noaction, mbc_noaction_multi, mbc_bin

def simulation_noControl(env, n_trunkline, max_depths, ustreamConduits, branchConduits, WRRFConduit):
    done = False; j = 0
    time = np.empty((0,1), float)
    ustream_depths = np.empty((0,len(ustreamConduits)),float)
    dstream_flows = np.empty((0,n_trunkline), float)
    dstream_TSSLoad = np.empty((0,n_trunkline), float)
    WRRF_flow = np.empty((0,1), float)
    WRRF_TSS = np.empty((0,1), float)
    WRRF_TSSLoad = np.empty((0,1), float)
    while not done:
        time = np.vstack((time,j/8640.))
        ustream_depths_tmp = []
        for e in range(0,len(ustreamConduits)):
            ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(ustreamConduits[e])/max_depths[e]))
        ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
        dstream_flows_tmp = []
        dstream_TSSLoad_tmp = []
        for e in range(0,len(branchConduits)):
            dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(branchConduits[e])))
            dstream_TSSLoad_tmp = np.hstack((dstream_TSSLoad_tmp,env.flow(branchConduits[e])*env.get_pollutant_link(branchConduits[e])*0.000062428))
        dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
        dstream_TSSLoad = np.vstack((dstream_TSSLoad,dstream_TSSLoad_tmp))
        WRRF_flow = np.vstack((WRRF_flow,env.flow(WRRFConduit)))
        WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(WRRFConduit)))
        WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))
        j += 1
        done = env.step()

    max_flow_WRRF = max(WRRF_flow)
    max_flow_dstream = np.zeros(n_trunkline)
    max_TSSLoad_dstream = np.zeros(n_trunkline)
    for e in range(0,n_trunkline):
        max_flow_dstream[e] = max(dstream_flows[:,e])
        max_TSSLoad_dstream[e] = max(dstream_TSSLoad[:,e])
    max_TSSLoad_WRRF = max(WRRF_TSSLoad)

    return time, ustream_depths, dstream_flows, max_flow_dstream, dstream_TSSLoad, max_TSSLoad_dstream, WRRF_flow, max_flow_WRRF, WRRF_TSSLoad, max_TSSLoad_WRRF

def simulation_control(env, control_points, n_trunkline, n_ISDs, control_step, setptMethod, setptThres, contType, objType, units, shapes, discharge, uInvert, dInvert, beta, epsilon_flow, epsilon_TSS, setpt_WRRF_flow, setpt_WRRF_TSS, orificeDict, orifice_diam_all, max_depths, ustreamConduits, branchConduits, WRRFConduit, max_flow_dstream, max_TSSLoad_dstream, max_flow_WRRF, max_TSSLoad_WRRF):
    env.reset()
    done = False; j = 0
    time_state = np.empty((0,1), float)
    time_control = np.empty((0,1), float)
    ustream_depths = np.empty((0,len(ustreamConduits)),float)
    dstream_flows = np.empty((0,n_trunkline), float)
    WRRF_flow = np.empty((0,1), float)
    WRRF_TSS = np.empty((0,1), float)
    WRRF_TSSLoad = np.empty((0,1), float)
    action = np.hstack((np.ones(sum(n_ISDs)),np.zeros(sum(n_ISDs))))

    while not done:
        if j%control_step != 0:
            time_state = np.vstack((time_state,j/8640.))
            for m in range(0,len(control_points)):
                action[m] = gateTrans[m,int(j%control_step)]
            for b in range(0,n_trunkline):
                for e in range(0,n_ISDs[b]):
                    env.set_gate(control_points[sum(n_ISDs[0:b])+e], action[sum(n_ISDs[0:b])+e])
                    env.set_gate(control_points[sum(n_ISDs)+sum(n_ISDs[0:b])+e], action[sum(n_ISDs)+sum(n_ISDs[0:b])+e])
            j += 1
            done = env.step()

            gates_tmp = []
            for b in range(0,n_trunkline):
                for e in range(0,n_ISDs[b]):
                    gates_tmp = np.hstack((gates_tmp,env.get_gate(control_points[sum(n_ISDs[0:b])+e])))
            gates_tmp = np.hstack((gates_tmp,np.zeros(sum(n_ISDs))))

            if j == 1:
                gates = copy.deepcopy(gates_tmp)
            else:
                gates = np.vstack((gates,gates_tmp))

            ustream_depths_tmp = []
            for e in range(0,len(ustreamConduits)):
                ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(ustreamConduits[e])/max_depths[e]))
            ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
            dstream_flows_tmp = []
            for e in range(0,len(branchConduits)):
                dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(branchConduits[e])))
            dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
            WRRF_flow = np.vstack((WRRF_flow,env.flow(WRRFConduit)))
            WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(WRRFConduit)))
            WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))

            for b in range(0,n_trunkline):
                for e in range(0,n_ISDs[b]):
                    env.set_gate(control_points[sum(n_ISDs[0:b])+e], actCurr[sum(n_ISDs[0:b])+e])
                    env.set_gate(control_points[sum(n_ISDs)+sum(n_ISDs[0:b])+e], actCurr[sum(n_ISDs)+sum(n_ISDs[0:b])+e])
        else:
            time_state = np.vstack((time_state,j/8640.))
            time_control = np.vstack((time_control,j/8640.))
            j += 1
            done = env.step()
            PDs = np.zeros(sum(n_ISDs))
            PSs = np.zeros(n_trunkline)
            ps = np.zeros(n_trunkline)

            actPrev = copy.deepcopy(action)

            if setptMethod == "automatic":
                ustream = np.zeros(n_trunkline)
                for b in range(0,n_trunkline):
                    branch_depths = []
                    for e in range(0,n_ISDs[b]):
                        branch_depths = np.hstack((branch_depths,env.depthL(ustreamConduits[sum(n_ISDs[0:b])+e])))
                    ustream[b] = max(branch_depths/max_depths[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])])
                if objType == "flow":
                    WRRF_flow_tmp = env.flow(WRRFConduit)
                    dstream = np.array([WRRF_flow_tmp/max_flow_WRRF])
                    dparam = epsilon_flow
                    setpt = np.array([setpt_WRRF_flow])
                elif objType == "TSS":
                    WRRF_flow_tmp = env.flow(WRRFConduit)
                    WRRF_TSS_tmp = env.get_pollutant_link(WRRFConduit)
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_TSSLoad_tmp/max_TSSLoad_WRRF])
                    dparam = epsilon_TSS
                    setpt = np.array([setpt_WRRF_TSS])
                elif objType == "both":
                    WRRF_flow_tmp = env.flow(WRRFConduit)
                    WRRF_TSS_tmp = env.get_pollutant_link(WRRFConduit)
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_flow_tmp/max_flow_WRRF, WRRF_TSSLoad_tmp/max_TSSLoad_WRRF])
                    dparam = np.array([epsilon_flow, epsilon_TSS])
                    setpt = np.array([setpt_WRRF_flow, setpt_WRRF_TSS])

                uparam = beta

                orifice_diam = np.ones(n_trunkline)
                if (objType == "flow") or (objType == "TSS"):
                    p_b, PD_b, PS_b = mbc_noaction(ustream, dstream, setpt, uparam, dparam, n_trunkline, setptThres)
                elif objType == "both":
                    p_b, PD_b, PS_b = mbc_noaction_multi(ustream, dstream, setpt, uparam, dparam, n_trunkline, setptThres)
                if PS_b == 0:
                    setpts = np.zeros(n_trunkline)
                else:
                    if objType == "flow":
                        setpts = PD_b/PS_b*setpt_WRRF_flow*max_flow_WRRF/max_flow_dstream
                    elif objType == "TSS":
                        setpts = PD_b/PS_b*setpt_WRRF_TSS*max_TSSLoad_WRRF/max_TSSLoad_dstream
                    elif objType == "both":
                        setpts_flow = PD_b/PS_b*setpt_WRRF_flow*max_flow_WRRF/max_flow_dstream
                        setpts_TSS = PD_b/PS_b*setpt_WRRF_TSS*max_TSSLoad_WRRF/max_TSSLoad_dstream

            for b in range(0,n_trunkline):
                branch_depths = []
                ustream_node_depths = []
                dstream_node_depths = []
                ustream_node_TSSConc = []
                for e in range(0,n_ISDs[b]):
                    branch_depths = np.hstack((branch_depths,env.depthL(ustreamConduits[sum(n_ISDs[0:b])+e])))
                    ustream_node_depths = np.hstack((ustream_node_depths,env.depthN(orificeDict[control_points[sum(n_ISDs[0:b])+e]]['from_node'])))
                    dstream_node_depths = np.hstack((dstream_node_depths,env.depthN(orificeDict[control_points[sum(n_ISDs)+sum(n_ISDs[0:b])+e]]['to_node'])))
                    ustream_node_TSSConc = np.hstack((ustream_node_TSSConc,env.get_pollutant_node(orificeDict[control_points[sum(n_ISDs[0:b])+e]]['from_node'])))
                ustream = branch_depths/max_depths[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
                if objType == "flow":
                    dn_flow_tmp = env.flow(branchConduits[b])
                    dstream = np.array([dn_flow_tmp/max_flow_dstream[b]])
                    setpt = np.array([setpts[b]])
                elif objType == "TSS":
                    dn_flow_tmp = env.flow(branchConduits[b])
                    dn_TSS_tmp = env.get_pollutant_link(branchConduits[b])
                    dn_TSSLoad_tmp = dn_flow_tmp * dn_TSS_tmp * 0.000062428
                    dstream = np.array([dn_TSSLoad_tmp/max_TSSLoad_dstream[b]])
                    setpt = np.array([setpts[b]])
                elif objType == "both":
                    dn_flow_tmp = env.flow(branchConduits[b])
                    dn_TSS_tmp = env.get_pollutant_link(branchConduits[b])
                    dn_TSSLoad_tmp = dn_flow_tmp * dn_TSS_tmp * 0.000062428
                    dstream = np.array([[dn_flow_tmp/max_flow_dstream[b]], [dn_TSSLoad_tmp/max_TSSLoad_dstream[b]]])
                    setpt = np.array([[setpts_flow[b]], [setpts_TSS[b]]])

                uparam = beta

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

            actCurr = copy.deepcopy(action)
            action = copy.deepcopy(actPrev)

            if control_step > 1:
                gateTrans = np.zeros((len(control_points),control_step+1))
                for m in range(0,len(control_points)):
                    gateTrans[m,:] = np.linspace(actPrev[m],actCurr[m],control_step+1)

            ustream_depths_tmp = []
            for e in range(0,len(ustreamConduits)):
                ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(ustreamConduits[e])/max_depths[e]))
            ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
            dstream_flows_tmp = []
            for e in range(0,len(branchConduits)):
                dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(branchConduits[e])))
            dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
            WRRF_flow = np.vstack((WRRF_flow,env.flow(WRRFConduit)))
            WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(WRRFConduit)))
            WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))

            if j == 1:
                price = ps
                demands = PDs
                supply = PSs
                gates = action
                if (objType == "flow") or (objType == "TSS"):
                    setpts_all = setpts
                else:
                    setpts_all = [setpts_flow,setpts_TSS]
            else:
                price = np.vstack((price,ps))
                demands = np.vstack((demands,PDs))
                supply = np.vstack((supply,PSs))
                gates = np.vstack((gates,action))
                if (objType == "flow") or (objType == "TSS"):
                    setpts_all = np.vstack((setpts_all,setpts))
                else:
                    setpts_all = np.vstack((setpts_all,[setpts_flow,setpts_TSS]))

    return time_state, time_control, ustream_depths, dstream_flows, WRRF_flow, WRRF_TSSLoad, price, demands, gates, setpts_all, setpt_WRRF_flow, setpt_WRRF_TSS
