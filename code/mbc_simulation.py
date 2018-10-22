import numpy as np
import copy
from mbc_fn import mbc, mbc_multi, mbc_noaction, mbc_noaction_multi, mbc_bin

def simulation_noControl(env, n_trunkline, sysSpecs, timesteps):
    done = False; j = 0
    time = np.zeros((timesteps,1),np.float16)
    ustream_depths = np.zeros((timesteps,len(sysSpecs['ustreamConduits'])),np.float16)
    dstream_flows = np.zeros((timesteps,n_trunkline),np.float16)
    dstream_TSSLoad = np.zeros((timesteps,n_trunkline),np.float16)
    WRRF_flow = np.zeros((timesteps,1),float)
    WRRF_TSS = np.zeros((timesteps,1),float)
    WRRF_TSSLoad = np.zeros((timesteps,1),float)
    while (not done) and (j < timesteps):
        time[j] = j/8640.
        for e in range(0,len(sysSpecs['ustreamConduits'])):
            ustream_depths[j,e] = env.depthL(sysSpecs['ustreamConduits'][e])/sysSpecs['max_depths'][e]
        for e in range(0,len(sysSpecs['branchConduits'])):
            dstream_flows[j,e] = env.flow(sysSpecs['branchConduits'][e])
            dstream_TSSLoad[j,e] = env.flow(sysSpecs['branchConduits'][e])*env.get_pollutant_link(sysSpecs['branchConduits'][e])*0.000062428
        WRRF_flow[j] = env.flow(sysSpecs['WRRFConduit'])
        WRRF_TSS[j] = env.get_pollutant_link(sysSpecs['WRRFConduit'])
        WRRF_TSSLoad[j] = WRRF_flow[j] * WRRF_TSS[j] * 0.000062428
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

def simulation_noControl_old(env, n_trunkline, sysSpecs, timesteps):
    done = False; j = 0
    time = np.empty((0,1), float)
    ustream_depths = np.empty((0,len(sysSpecs['ustreamConduits'])),float)
    dstream_flows = np.empty((0,n_trunkline), float)
    dstream_TSSLoad = np.empty((0,n_trunkline), float)
    WRRF_flow = np.empty((0,1), float)
    WRRF_TSS = np.empty((0,1), float)
    WRRF_TSSLoad = np.empty((0,1), float)
    while not done:
        time = np.vstack((time,j/8640.))
        ustream_depths_tmp = []
        for e in range(0,len(sysSpecs['ustreamConduits'])):
            ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(sysSpecs['ustreamConduits'][e])/sysSpecs['max_depths'][e]))
        ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
        dstream_flows_tmp = []
        dstream_TSSLoad_tmp = []
        for e in range(0,len(sysSpecs['branchConduits'])):
            dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(sysSpecs['branchConduits'][e])))
            dstream_TSSLoad_tmp = np.hstack((dstream_TSSLoad_tmp,env.flow(sysSpecs['branchConduits'][e])*env.get_pollutant_link(sysSpecs['branchConduits'][e])*0.000062428))
        dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
        dstream_TSSLoad = np.vstack((dstream_TSSLoad,dstream_TSSLoad_tmp))
        WRRF_flow = np.vstack((WRRF_flow,env.flow(sysSpecs['WRRFConduit'])))
        WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(sysSpecs['WRRFConduit'])))
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

def simulation_control(env, n_trunkline, n_ISDs, ctrlParams, sysSpecs, weights, orificeDict, maxes, timesteps):
    env.reset()
    done = False; j = 0
    time_state = np.zeros((timesteps,1),np.float16)
    time_control = np.empty((0,1),np.float16)
    ustream_depths = np.zeros((timesteps,len(sysSpecs['ustreamConduits'])),np.float16)
    dstream_flows = np.zeros((timesteps,n_trunkline),np.float16)
    WRRF_flow = np.zeros((timesteps,1),np.float32)
    WRRF_TSS = np.zeros((timesteps,1),np.float32)
    WRRF_TSSLoad = np.zeros((timesteps,1),np.float32)
    action = np.hstack((np.ones(sum(n_ISDs)),np.zeros(sum(n_ISDs))))
    gates = np.zeros((timesteps,2*sum(n_ISDs)),np.float16)

    while (not done) and (j < timesteps):
        if j%sysSpecs['control_step'] != 0:
            if ctrlParams['hierarchy'] == 1:
                time_state[j] = j/8640.
                for m in range(0,len(sysSpecs['control_points'])):
                    action[m] = gateTrans[m,int(j%sysSpecs['control_step'])]
                for b in range(0,sum(n_ISDs)):
                    env.set_gate(sysSpecs['control_points'][b], action[b])
                    env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+b], action[sum(n_ISDs)+b])
                j += 1
                done = env.step()

                for b in range(0,n_ISDs):
                    gates[j-1,b] = env.get_gate(sysSpecs['control_points'][b])

                for e in range(0,len(sysSpecs['ustreamConduits'])):
                    ustream_depths[j-1,e] = env.depthL(sysSpecs['ustreamConduits'][e])/sysSpecs['max_depths'][e]
                for e in range(0,len(sysSpecs['branchConduits'])):
                    dstream_flows[j-1,e] = env.flow(sysSpecs['branchConduits'][e])
                WRRF_flow[j-1] = env.flow(sysSpecs['WRRFConduit'])
                WRRF_TSS[j-1] = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                WRRF_TSSLoad[j-1] = WRRF_flow[j-1] * WRRF_TSS[j-1] * 0.000062428

                for b in range(0,sum(n_ISDs)):
                    env.set_gate(sysSpecs['control_points'][b], actCurr[b])
                    env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+b], actCurr[sum(n_ISDs)+b])                
                
            else:
                time_state[j] = j/8640.
                for m in range(0,len(sysSpecs['control_points'])):
                    action[m] = gateTrans[m,int(j%sysSpecs['control_step'])]
                for e in range(0,sum(n_ISDs)):
                    env.set_gate(sysSpecs['control_points'][e], action[e])
                    env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+e], action[sum(n_ISDs)+e])
                j += 1
                done = env.step()

                for b in range(0,sum(n_ISDs)):
                    gates[j-1,b] = env.get_gate(sysSpecs['control_points'][b])

                for e in range(0,len(sysSpecs['ustreamConduits'])):
                    ustream_depths[j-1,e] = env.depthL(sysSpecs['ustreamConduits'][e])/sysSpecs['max_depths'][e]
                for e in range(0,len(sysSpecs['branchConduits'])):
                    dstream_flows[j-1,e] = env.flow(sysSpecs['branchConduits'][e])
                WRRF_flow[j-1] = env.flow(sysSpecs['WRRFConduit'])
                WRRF_TSS[j-1] = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                WRRF_TSSLoad[j-1] = WRRF_flow[j-1] * WRRF_TSS[j-1] * 0.000062428

                for b in range(0,sum(n_ISDs)):
                    env.set_gate(sysSpecs['control_points'][b], actCurr[b])
                    env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+b], actCurr[sum(n_ISDs)+b])
                
        else:
            time_state[j] = j/8640.
            time_control = np.vstack((time_control,j/8640.))
            j += 1
            done = env.step()
            PDs = np.zeros(sum(n_ISDs),np.float16)
            PSs = np.zeros(n_trunkline,np.float16)
            ps = np.zeros(n_trunkline,np.float16)

            actPrev = copy.deepcopy(action)

            if ctrlParams['hierarchy'] == 1:
                ustream = np.zeros(n_trunkline)
                for b in range(0,n_trunkline):
                    branch_depths = np.zeros((n_ISDs[b],1),float)
                    for e in range(0,n_ISDs[b]):
                        branch_depths[e] = env.depthL(sysSpecs['ustreamConduits'][sum(n_ISDs[0:b])+e])
                    ustream[b] = max(branch_depths/sysSpecs['max_depths'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])])
                if ctrlParams['objType'] == "flow":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    dstream = np.array([WRRF_flow_tmp/maxes['max_flow_WRRF']])
                    dparam = weights['epsilon_flow']
                    setpt = np.array([ctrlParams['setpt_WRRF_flow']])
                elif ctrlParams['objType'] == "TSS":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    WRRF_TSS_tmp = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_TSSLoad_tmp/maxes['max_TSSLoad_WRRF']])
                    dparam = weights['epsilon_TSS']
                    setpt = np.array([ctrlParams['setpt_WRRF_TSS']])
                elif ctrlParams['objType'] == "both":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    WRRF_TSS_tmp = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_flow_tmp/maxes['max_flow_WRRF'], WRRF_TSSLoad_tmp/maxes['max_TSSLoad_WRRF']])
                    dparam = np.array([weights['epsilon_flow'], weights['epsilon_TSS']])
                    setpt = np.array([ctrlParams['setpt_WRRF_flow'], ctrlParams['setpt_WRRF_TSS']])

                uparam = weights['beta']

                orifice_diam = np.ones(n_trunkline)
                if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                    p_b, PD_b, PS_b = mbc_noaction(ustream, dstream, setpt, uparam, dparam, n_trunkline, ctrlParams['setptThres'])
                elif ctrlParams['objType'] == "both":
                    p_b, PD_b, PS_b = mbc_noaction_multi(ustream, dstream, setpt, uparam, dparam, n_trunkline, ctrlParams['setptThres'])
                if PS_b == 0:
                    setpts = np.zeros(n_trunkline)
                else:
                    if ctrlParams['objType'] == "flow":
                        setpts = PD_b/PS_b*ctrlParams['setpt_WRRF_flow']*maxes['max_flow_WRRF']/maxes['max_flow_dstream']
                    elif ctrlParams['objType'] == "TSS":
                        setpts = PD_b/PS_b*ctrlParams['setpt_WRRF_TSS']*maxes['max_TSSLoad_WRRF']/maxes['max_TSSLoad_dstream']
                    elif ctrlParams['objType'] == "both":
                        setpts_flow = PD_b/PS_b*ctrlParams['setpt_WRRF_flow']*maxes['max_flow_WRRF']/maxes['max_flow_dstream']
                        setpts_TSS = PD_b/PS_b*ctrlParams['setpt_WRRF_TSS']*maxes['max_TSSLoad_WRRF']/maxes['max_TSSLoad_dstream']

                for b in range(0,n_trunkline):
                    branch_depths = np.zeros((n_ISDs[b],1),float)
                    ustream_node_depths = np.zeros((n_ISDs[b],1),float)
                    dstream_node_depths = np.zeros((n_ISDs[b],1),float)
                    ustream_node_TSSConc = np.zeros((n_ISDs[b],1),float)
                    for e in range(0,n_ISDs[b]):
                        branch_depths[e] = env.depthL(sysSpecs['ustreamConduits'][sum(n_ISDs[0:b])+e])
                        ustream_node_depths[e] = env.depthN(orificeDict[sysSpecs['control_points'][sum(n_ISDs[0:b])+e]]['from_node'])
                        dstream_node_depths[e] = env.depthN(orificeDict[sysSpecs['control_points'][sum(n_ISDs)+sum(n_ISDs[0:b])+e]]['to_node'])
                        ustream_node_TSSConc[e] = env.get_pollutant_node(orificeDict[sysSpecs['control_points'][sum(n_ISDs[0:b])+e]]['from_node'])
                    ustream = branch_depths/sysSpecs['max_depths'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
                    if ctrlParams['objType'] == "flow":
                        dn_flow_tmp = env.flow(sysSpecs['branchConduits'][b])
                        dstream = np.array([dn_flow_tmp/maxes['max_flow_dstream'][b]])
                        setpt = np.array([setpts[b]])
                    elif ctrlParams['objType'] == "TSS":
                        dn_flow_tmp = env.flow(sysSpecs['branchConduits'][b])
                        dn_TSS_tmp = env.get_pollutant_link(sysSpecs['branchConduits'][b])
                        dn_TSSLoad_tmp = dn_flow_tmp * dn_TSS_tmp * 0.000062428
                        dstream = np.array([dn_TSSLoad_tmp/maxes['max_TSSLoad_dstream'][b]])
                        setpt = np.array([setpts[b]])
                    elif ctrlParams['objType'] == "both":
                        dn_flow_tmp = env.flow(sysSpecs['branchConduits'][b])
                        dn_TSS_tmp = env.get_pollutant_link(sysSpecs['branchConduits'][b])
                        dn_TSSLoad_tmp = dn_flow_tmp * dn_TSS_tmp * 0.000062428
                        dstream = np.array([[dn_flow_tmp/maxes['max_flow_dstream'][b]], [dn_TSSLoad_tmp/maxes['max_TSSLoad_dstream'][b]]])
                        setpt = np.array([[setpts_flow[b]], [setpts_TSS[b]]])

                    uparam = weights['beta']

                    action_sub = np.hstack((np.ones(n_ISDs[b]),np.zeros(n_ISDs[b])))
                    orifice_diam = sysSpecs['orifice_diam_all'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
                    if ctrlParams['contType'] == "binary":
                        p, PD, PS, action_sub = mbc_bin(ustream, dstream, setpt, uparam,
                                            dparam, n_ISDs[b], action_sub, sysSpecs['discharge'], ctrlParams['setptThres'])
                    elif ctrlParams['contType'] == "continuous":
                        if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                            p, PD, PS, action_sub = mbc(ustream, dstream, setpt, uparam,
                                        dparam, n_ISDs[b], action_sub, sysSpecs['discharge'],
                                        maxes['max_flow_dstream'][b], maxes['max_TSSLoad_dstream'][b], sysSpecs['units'], orifice_diam,
                                        sysSpecs['shapes'], ustream_node_depths, dstream_node_depths,
                                        sysSpecs['uInvert'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        sysSpecs['dInvert'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        ctrlParams['setptThres'], ctrlParams['objType'], ustream_node_TSSConc)
                        elif ctrlParams['objType'] == "both":
                            p, PD, PS, action_sub = mbc_multi(ustream, dstream, setpt, uparam,
                                        dparam, n_ISDs[b], action_sub, sysSpecs['discharge'],
                                        maxes['max_flow_dstream'][b], maxes['max_TSSLoad_dstream'][b], sysSpecs['units'], orifice_diam,
                                        sysSpecs['shapes'], ustream_node_depths, dstream_node_depths,
                                        sysSpecs['uInvert'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        sysSpecs['dInvert'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        ctrlParams['setptThres'], ctrlParams['objType'], ustream_node_TSSConc)
                    action[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = action_sub[:len(action_sub)/2]
                    action[sum(n_ISDs[0:b])+sum(n_ISDs):sum(n_ISDs[0:b+1])+sum(n_ISDs)] = action_sub[len(action_sub)/2:]

                    PDs[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = PD
                    PSs[b] = PS
                    ps[b] = p

                    for e in range(0,n_ISDs[b]):
                        env.set_gate(sysSpecs['control_points'][sum(n_ISDs[0:b])+e], action[sum(n_ISDs[0:b])+e])
                        env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+sum(n_ISDs[0:b])+e], action[sum(n_ISDs)+sum(n_ISDs[0:b])+e])

                actCurr = copy.deepcopy(action)

            else:
                storage_depths = np.zeros(sum(n_ISDs),float)
                ustream_node_depths = np.zeros(sum(n_ISDs),float)
                dstream_node_depths = np.zeros(sum(n_ISDs),float)
                ustream_node_TSSConc = np.zeros(sum(n_ISDs),float)
                for b in range(0,sum(n_ISDs)):
                    storage_depths[b] = env.depthL(sysSpecs['ustreamConduits'][b])
                    ustream_node_depths[b] = env.depthN(orificeDict[sysSpecs['control_points'][b]]['from_node'])
                    dstream_node_depths[b] = env.depthN(orificeDict[sysSpecs['control_points'][sum(n_ISDs)+b]]['to_node'])
                    ustream_node_TSSConc[b] = env.get_pollutant_node(orificeDict[sysSpecs['control_points'][b]]['from_node'])
                ustream = storage_depths/sysSpecs['max_depths']
                if ctrlParams['objType'] == "flow":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    dstream = np.array([WRRF_flow_tmp/maxes['max_flow_WRRF']])
                    dparam = weights['epsilon_flow']
                    setpt = np.array([ctrlParams['setpt_WRRF_flow']])
                elif ctrlParams['objType'] == "TSS":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    WRRF_TSS_tmp = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_TSSLoad_tmp/maxes['max_TSSLoad_WRRF']])
                    dparam = weights['epsilon_TSS']
                    setpt = np.array([ctrlParams['setpt_WRRF_TSS']])
                elif ctrlParams['objType'] == "both":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    WRRF_TSS_tmp = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_flow_tmp/maxes['max_flow_WRRF'], WRRF_TSSLoad_tmp/maxes['max_TSSLoad_WRRF']])
                    dparam = np.array([weights['epsilon_flow'], weights['epsilon_TSS']])
                    setpt = np.array([ctrlParams['setpt_WRRF_flow'], ctrlParams['setpt_WRRF_TSS']])

                uparam = weights['beta']

                action_sub = np.hstack((np.ones(sum(n_ISDs)),np.zeros(sum(n_ISDs))))
                orifice_diam = sysSpecs['orifice_diam_all']
                if ctrlParams['contType'] == "binary":
                    p, PD, PS, action_sub = mbc_bin(ustream, dstream, setpt, uparam,
                                        dparam, sum(n_ISDs), action_sub, sysSpecs['discharge'], ctrlParams['setptThres'])
                elif ctrlParams['contType'] == "continuous":
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        p, PD, PS, action_sub = mbc(ustream, dstream, setpt, uparam,
                                    dparam, sum(n_ISDs), action_sub, sysSpecs['discharge'],
                                    maxes['max_flow_WRRF'], maxes['max_TSSLoad_WRRF'], sysSpecs['units'], orifice_diam,
                                    sysSpecs['shapes'], ustream_node_depths, dstream_node_depths,
                                    sysSpecs['uInvert'], sysSpecs['dInvert'],
                                    ctrlParams['setptThres'], ctrlParams['objType'], ustream_node_TSSConc)
                    elif ctrlParams['objType'] == "both":
                        p, PD, PS, action_sub = mbc_multi(ustream, dstream, setpt, uparam,
                                    dparam, sum(n_ISDs), action_sub, sysSpecs['discharge'],
                                    maxes['max_flow_WRRF'], maxes['max_TSSLoad_WRRF'], sysSpecs['units'], orifice_diam,
                                    sysSpecs['shapes'], ustream_node_depths, dstream_node_depths,
                                    sysSpecs['uInvert'], sysSpecs['dInvert'],
                                    ctrlParams['setptThres'], ctrlParams['objType'], ustream_node_TSSConc)
                action[0:sum(n_ISDs)] = action_sub[:len(action_sub)/2]
                action[sum(n_ISDs):2*sum(n_ISDs)] = action_sub[len(action_sub)/2:]

                PDs = PD
                PSs = PS
                ps = p

                for e in range(0,sum(n_ISDs)):
                    env.set_gate(sysSpecs['control_points'][e], action[e])
                    env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+e], action[sum(n_ISDs)+e])

            actCurr = copy.deepcopy(action)

            if sysSpecs['control_step'] > 1:
                action = copy.deepcopy(actPrev)
                gateTrans = np.zeros((len(sysSpecs['control_points']),sysSpecs['control_step']+1))
                for m in range(0,len(sysSpecs['control_points'])):
                    gateTrans[m,:] = np.linspace(actPrev[m],actCurr[m],sysSpecs['control_step']+1)

            for e in range(0,len(sysSpecs['ustreamConduits'])):
                ustream_depths[j-1,e] = env.depthL(sysSpecs['ustreamConduits'][e])/sysSpecs['max_depths'][e]
            for e in range(0,len(sysSpecs['branchConduits'])):
                dstream_flows[j-1,e] = env.flow(sysSpecs['branchConduits'][e])
            WRRF_flow[j-1] = env.flow(sysSpecs['WRRFConduit'])
            WRRF_TSS[j-1] = env.get_pollutant_link(sysSpecs['WRRFConduit'])
            WRRF_TSSLoad[j-1] = WRRF_flow[j-1] * WRRF_TSS[j-1] * 0.000062428
            
            for b in range(0,sum(n_ISDs)):
                gates[j-1,b] = action[b]

            if j == 1:
                price = ps
                demands = PDs
                supply = PSs
                if ctrlParams['hierarchy'] == 1:
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        setpts_all = setpts
                    else:
                        setpts_all = [setpts_flow,setpts_TSS]
                else:
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        setpts_all = np.zeros(n_trunkline)
                    else:
                        setpts_all = np.zeros(2*n_trunkline)
            else:
                price = np.vstack((price,ps))
                demands = np.vstack((demands,PDs))
                supply = np.vstack((supply,PSs))
                if ctrlParams['hierarchy'] == 1:
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        setpts_all = np.vstack((setpts_all,setpts))
                    else:
                        setpts_all = np.vstack((setpts_all,[setpts_flow,setpts_TSS]))
                else:
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        setpts_all = np.vstack((setpts_all,np.zeros(n_trunkline)))
                    else:
                        setpts_all = np.vstack((setpts_all,np.zeros(2*n_trunkline)))

    return time_state, time_control, ustream_depths, dstream_flows, WRRF_flow, WRRF_TSSLoad, price, demands, gates, setpts_all, ctrlParams

def simulation_control_old(env, n_trunkline, n_ISDs, ctrlParams, sysSpecs, weights, orificeDict, maxes):
    env.reset()
    done = False; j = 0
    time_state = np.empty((0,1), float)
    time_control = np.empty((0,1), float)
    ustream_depths = np.empty((0,len(sysSpecs['ustreamConduits'])),float)
    dstream_flows = np.empty((0,n_trunkline), float)
    WRRF_flow = np.empty((0,1), float)
    WRRF_TSS = np.empty((0,1), float)
    WRRF_TSSLoad = np.empty((0,1), float)
    action = np.hstack((np.ones(sum(n_ISDs)),np.zeros(sum(n_ISDs))))

    while not done:
        if j%sysSpecs['control_step'] != 0:
            if ctrlParams['hierarchy'] == 1:
                time_state = np.vstack((time_state,j/8640.))
                for m in range(0,len(sysSpecs['control_points'])):
                    action[m] = gateTrans[m,int(j%sysSpecs['control_step'])]
                for b in range(0,n_trunkline):
                    for e in range(0,n_ISDs[b]):
                        env.set_gate(sysSpecs['control_points'][sum(n_ISDs[0:b])+e], action[sum(n_ISDs[0:b])+e])
                        env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+sum(n_ISDs[0:b])+e], action[sum(n_ISDs)+sum(n_ISDs[0:b])+e])
                j += 1
                done = env.step()

                gates_tmp = []
                for b in range(0,n_trunkline):
                    for e in range(0,n_ISDs[b]):
                        gates_tmp = np.hstack((gates_tmp,env.get_gate(sysSpecs['control_points'][sum(n_ISDs[0:b])+e])))
                gates_tmp = np.hstack((gates_tmp,np.zeros(sum(n_ISDs))))

                if j == 1:
                    gates = copy.deepcopy(gates_tmp)
                else:
                    gates = np.vstack((gates,gates_tmp))

                ustream_depths_tmp = []
                for e in range(0,len(sysSpecs['ustreamConduits'])):
                    ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(sysSpecs['ustreamConduits'][e])/sysSpecs['max_depths'][e]))
                ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
                dstream_flows_tmp = []
                for e in range(0,len(sysSpecs['branchConduits'])):
                    dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(sysSpecs['branchConduits'][e])))
                dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
                WRRF_flow = np.vstack((WRRF_flow,env.flow(sysSpecs['WRRFConduit'])))
                WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(sysSpecs['WRRFConduit'])))
                WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))

                for b in range(0,n_trunkline):
                    for e in range(0,n_ISDs[b]):
                        env.set_gate(sysSpecs['control_points'][sum(n_ISDs[0:b])+e], actCurr[sum(n_ISDs[0:b])+e])
                        env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+sum(n_ISDs[0:b])+e], actCurr[sum(n_ISDs)+sum(n_ISDs[0:b])+e])

            else:
                time_state = np.vstack((time_state,j/8640.))
                for m in range(0,len(sysSpecs['control_points'])):
                    action[m] = gateTrans[m,int(j%sysSpecs['control_step'])]
                for e in range(0,sum(n_ISDs)):
                    env.set_gate(sysSpecs['control_points'][e], action[e])
                    env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+e], action[sum(n_ISDs)+e])
                j += 1
                done = env.step()

                gates_tmp = []
                for b in range(0,sum(n_ISDs)):
                    gates_tmp = np.hstack((gates_tmp,env.get_gate(sysSpecs['control_points'][e])))
                gates_tmp = np.hstack((gates_tmp,np.zeros(sum(n_ISDs))))

                if j == 1:
                    gates = copy.deepcopy(gates_tmp)
                else:
                    gates = np.vstack((gates,gates_tmp))

                ustream_depths_tmp = []
                for e in range(0,len(sysSpecs['ustreamConduits'])):
                    ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(sysSpecs['ustreamConduits'][e])/sysSpecs['max_depths'][e]))
                ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
                dstream_flows_tmp = []
                for e in range(0,len(sysSpecs['branchConduits'])):
                    dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(sysSpecs['branchConduits'][e])))
                dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
                WRRF_flow = np.vstack((WRRF_flow,env.flow(sysSpecs['WRRFConduit'])))
                WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(sysSpecs['WRRFConduit'])))
                WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))

                for e in range(0,n_trunkline):
                    env.set_gate(sysSpecs['control_points'][e], actCurr[e])
                    env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+e], actCurr[sum(n_ISDs)+e])

        else:
            time_state = np.vstack((time_state,j/8640.))
            time_control = np.vstack((time_control,j/8640.))
            j += 1
            done = env.step()
            PDs = np.zeros(sum(n_ISDs))
            PSs = np.zeros(n_trunkline)
            ps = np.zeros(n_trunkline)

            actPrev = copy.deepcopy(action)

            if ctrlParams['hierarchy'] == 1:
                ustream = np.zeros(n_trunkline)
                for b in range(0,n_trunkline):
                    branch_depths = []
                    for e in range(0,n_ISDs[b]):
                        branch_depths = np.hstack((branch_depths,env.depthL(sysSpecs['ustreamConduits'][sum(n_ISDs[0:b])+e])))
                    ustream[b] = max(branch_depths/sysSpecs['max_depths'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])])
                if ctrlParams['objType'] == "flow":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    dstream = np.array([WRRF_flow_tmp/maxes['max_flow_WRRF']])
                    dparam = weights['epsilon_flow']
                    setpt = np.array([ctrlParams['setpt_WRRF_flow']])
                elif ctrlParams['objType'] == "TSS":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    WRRF_TSS_tmp = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_TSSLoad_tmp/maxes['max_TSSLoad_WRRF']])
                    dparam = weights['epsilon_TSS']
                    setpt = np.array([ctrlParams['setpt_WRRF_TSS']])
                elif ctrlParams['objType'] == "both":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    WRRF_TSS_tmp = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_flow_tmp/maxes['max_flow_WRRF'], WRRF_TSSLoad_tmp/maxes['max_TSSLoad_WRRF']])
                    dparam = np.array([weights['epsilon_flow'], weights['epsilon_TSS']])
                    setpt = np.array([ctrlParams['setpt_WRRF_flow'], ctrlParams['setpt_WRRF_TSS']])

                uparam = weights['beta']

                orifice_diam = np.ones(n_trunkline)
                if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                    p_b, PD_b, PS_b = mbc_noaction(ustream, dstream, setpt, uparam, dparam, n_trunkline, ctrlParams['setptThres'])
                elif ctrlParams['objType'] == "both":
                    p_b, PD_b, PS_b = mbc_noaction_multi(ustream, dstream, setpt, uparam, dparam, n_trunkline, ctrlParams['setptThres'])
                if PS_b == 0:
                    setpts = np.zeros(n_trunkline)
                else:
                    if ctrlParams['objType'] == "flow":
                        setpts = PD_b/PS_b*ctrlParams['setpt_WRRF_flow']*maxes['max_flow_WRRF']/maxes['max_flow_dstream']
                    elif ctrlParams['objType'] == "TSS":
                        setpts = PD_b/PS_b*ctrlParams['setpt_WRRF_TSS']*maxes['max_TSSLoad_WRRF']/maxes['max_TSSLoad_dstream']
                    elif ctrlParams['objType'] == "both":
                        setpts_flow = PD_b/PS_b*ctrlParams['setpt_WRRF_flow']*maxes['max_flow_WRRF']/maxes['max_flow_dstream']
                        setpts_TSS = PD_b/PS_b*ctrlParams['setpt_WRRF_TSS']*maxes['max_TSSLoad_WRRF']/maxes['max_TSSLoad_dstream']

                for b in range(0,n_trunkline):
                    branch_depths = []
                    ustream_node_depths = []
                    dstream_node_depths = []
                    ustream_node_TSSConc = []
                    for e in range(0,n_ISDs[b]):
                        branch_depths = np.hstack((branch_depths,env.depthL(sysSpecs['ustreamConduits'][sum(n_ISDs[0:b])+e])))
                        ustream_node_depths = np.hstack((ustream_node_depths,env.depthN(orificeDict[sysSpecs['control_points'][sum(n_ISDs[0:b])+e]]['from_node'])))
                        dstream_node_depths = np.hstack((dstream_node_depths,env.depthN(orificeDict[sysSpecs['control_points'][sum(n_ISDs)+sum(n_ISDs[0:b])+e]]['to_node'])))
                        ustream_node_TSSConc = np.hstack((ustream_node_TSSConc,env.get_pollutant_node(orificeDict[sysSpecs['control_points'][sum(n_ISDs[0:b])+e]]['from_node'])))
                    ustream = branch_depths/sysSpecs['max_depths'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
                    if ctrlParams['objType'] == "flow":
                        dn_flow_tmp = env.flow(sysSpecs['branchConduits'][b])
                        dstream = np.array([dn_flow_tmp/maxes['max_flow_dstream'][b]])
                        setpt = np.array([setpts[b]])
                    elif ctrlParams['objType'] == "TSS":
                        dn_flow_tmp = env.flow(sysSpecs['branchConduits'][b])
                        dn_TSS_tmp = env.get_pollutant_link(sysSpecs['branchConduits'][b])
                        dn_TSSLoad_tmp = dn_flow_tmp * dn_TSS_tmp * 0.000062428
                        dstream = np.array([dn_TSSLoad_tmp/maxes['max_TSSLoad_dstream'][b]])
                        setpt = np.array([setpts[b]])
                    elif ctrlParams['objType'] == "both":
                        dn_flow_tmp = env.flow(sysSpecs['branchConduits'][b])
                        dn_TSS_tmp = env.get_pollutant_link(sysSpecs['branchConduits'][b])
                        dn_TSSLoad_tmp = dn_flow_tmp * dn_TSS_tmp * 0.000062428
                        dstream = np.array([[dn_flow_tmp/maxes['max_flow_dstream'][b]], [dn_TSSLoad_tmp/maxes['max_TSSLoad_dstream'][b]]])
                        setpt = np.array([[setpts_flow[b]], [setpts_TSS[b]]])

                    uparam = weights['beta']

                    action_sub_down = np.ones(n_ISDs[b])
                    action_sub_up = np.zeros(n_ISDs[b])
                    action_sub = np.hstack((action_sub_down,action_sub_up))
                    orifice_diam = sysSpecs['orifice_diam_all'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])]
                    if ctrlParams['contType'] == "binary":
                        p, PD, PS, action_sub = mbc_bin(ustream, dstream, setpt, uparam,
                                            dparam, n_ISDs[b], action_sub, sysSpecs['discharge'], ctrlParams['setptThres'])
                    elif ctrlParams['contType'] == "continuous":
                        if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                            p, PD, PS, action_sub = mbc(ustream, dstream, setpt, uparam,
                                        dparam, n_ISDs[b], action_sub, sysSpecs['discharge'],
                                        maxes['max_flow_dstream'][b], maxes['max_TSSLoad_dstream'][b], sysSpecs['units'], orifice_diam,
                                        sysSpecs['shapes'], ustream_node_depths, dstream_node_depths,
                                        sysSpecs['uInvert'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        sysSpecs['dInvert'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        ctrlParams['setptThres'], ctrlParams['objType'], ustream_node_TSSConc)
                        elif ctrlParams['objType'] == "both":
                            p, PD, PS, action_sub = mbc_multi(ustream, dstream, setpt, uparam,
                                        dparam, n_ISDs[b], action_sub, sysSpecs['discharge'],
                                        maxes['max_flow_dstream'][b], maxes['max_TSSLoad_dstream'][b], sysSpecs['units'], orifice_diam,
                                        sysSpecs['shapes'], ustream_node_depths, dstream_node_depths,
                                        sysSpecs['uInvert'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        sysSpecs['dInvert'][sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])],
                                        ctrlParams['setptThres'], ctrlParams['objType'], ustream_node_TSSConc)
                    action[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = action_sub[:len(action_sub)/2]
                    action[sum(n_ISDs[0:b])+sum(n_ISDs):sum(n_ISDs[0:b+1])+sum(n_ISDs)] = action_sub[len(action_sub)/2:]

                    PDs[sum(n_ISDs[0:b]):sum(n_ISDs[0:b+1])] = PD
                    PSs[b] = PS
                    ps[b] = p

                    for e in range(0,n_ISDs[b]):
                        env.set_gate(sysSpecs['control_points'][sum(n_ISDs[0:b])+e], action[sum(n_ISDs[0:b])+e])
                        env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+sum(n_ISDs[0:b])+e], action[sum(n_ISDs)+sum(n_ISDs[0:b])+e])

                actCurr = copy.deepcopy(action)

            else:
                storage_depths = []
                ustream_node_depths = []
                dstream_node_depths = []
                ustream_node_TSSConc = []
                for b in range(0,sum(n_ISDs)):
                    storage_depths = np.hstack((storage_depths,env.depthL(sysSpecs['ustreamConduits'][b])))
                    ustream_node_depths = np.hstack((ustream_node_depths,env.depthN(orificeDict[sysSpecs['control_points'][b]]['from_node'])))
                    dstream_node_depths = np.hstack((dstream_node_depths,env.depthN(orificeDict[sysSpecs['control_points'][sum(n_ISDs)+b]]['to_node'])))
                    ustream_node_TSSConc = np.hstack((ustream_node_TSSConc,env.get_pollutant_node(orificeDict[sysSpecs['control_points'][b]]['from_node'])))
                ustream = storage_depths/sysSpecs['max_depths']
                if ctrlParams['objType'] == "flow":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    dstream = np.array([WRRF_flow_tmp/maxes['max_flow_WRRF']])
                    dparam = weights['epsilon_flow']
                    setpt = np.array([ctrlParams['setpt_WRRF_flow']])
                elif ctrlParams['objType'] == "TSS":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    WRRF_TSS_tmp = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_TSSLoad_tmp/maxes['max_TSSLoad_WRRF']])
                    dparam = weights['epsilon_TSS']
                    setpt = np.array([ctrlParams['setpt_WRRF_TSS']])
                elif ctrlParams['objType'] == "both":
                    WRRF_flow_tmp = env.flow(sysSpecs['WRRFConduit'])
                    WRRF_TSS_tmp = env.get_pollutant_link(sysSpecs['WRRFConduit'])
                    WRRF_TSSLoad_tmp = WRRF_flow_tmp * WRRF_TSS_tmp * 0.000062428
                    dstream = np.array([WRRF_flow_tmp/maxes['max_flow_WRRF'], WRRF_TSSLoad_tmp/maxes['max_TSSLoad_WRRF']])
                    dparam = np.array([weights['epsilon_flow'], weights['epsilon_TSS']])
                    setpt = np.array([ctrlParams['setpt_WRRF_flow'], ctrlParams['setpt_WRRF_TSS']])

                uparam = weights['beta']

                action_sub_down = np.ones(sum(n_ISDs))
                action_sub_up = np.zeros(sum(n_ISDs))
                action_sub = np.hstack((action_sub_down,action_sub_up))
                orifice_diam = sysSpecs['orifice_diam_all']
                if ctrlParams['contType'] == "binary":
                    p, PD, PS, action_sub = mbc_bin(ustream, dstream, setpt, uparam,
                                        dparam, sum(n_ISDs), action_sub, sysSpecs['discharge'], ctrlParams['setptThres'])
                elif ctrlParams['contType'] == "continuous":
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        p, PD, PS, action_sub = mbc(ustream, dstream, setpt, uparam,
                                    dparam, sum(n_ISDs), action_sub, sysSpecs['discharge'],
                                    maxes['max_flow_WRRF'], maxes['max_TSSLoad_WRRF'], sysSpecs['units'], orifice_diam,
                                    sysSpecs['shapes'], ustream_node_depths, dstream_node_depths,
                                    sysSpecs['uInvert'], sysSpecs['dInvert'],
                                    ctrlParams['setptThres'], ctrlParams['objType'], ustream_node_TSSConc)
                    elif ctrlParams['objType'] == "both":
                        p, PD, PS, action_sub = mbc_multi(ustream, dstream, setpt, uparam,
                                    dparam, sum(n_ISDs), action_sub, sysSpecs['discharge'],
                                    maxes['max_flow_WRRF'], maxes['max_TSSLoad_WRRF'], sysSpecs['units'], orifice_diam,
                                    sysSpecs['shapes'], ustream_node_depths, dstream_node_depths,
                                    sysSpecs['uInvert'], sysSpecs['dInvert'],
                                    ctrlParams['setptThres'], ctrlParams['objType'], ustream_node_TSSConc)
                action[0:sum(n_ISDs)] = action_sub[:len(action_sub)/2]
                action[sum(n_ISDs):2*sum(n_ISDs)] = action_sub[len(action_sub)/2:]

                PDs = PD
                PSs = PS
                ps = p

                for e in range(0,sum(n_ISDs)):
                    env.set_gate(sysSpecs['control_points'][e], action[e])
                    env.set_gate(sysSpecs['control_points'][sum(n_ISDs)+e], action[sum(n_ISDs)+e])

            actCurr = copy.deepcopy(action)

            if sysSpecs['control_step'] > 1:
                action = copy.deepcopy(actPrev)
                gateTrans = np.zeros((len(sysSpecs['control_points']),sysSpecs['control_step']+1))
                for m in range(0,len(sysSpecs['control_points'])):
                    gateTrans[m,:] = np.linspace(actPrev[m],actCurr[m],sysSpecs['control_step']+1)

            ustream_depths_tmp = []
            for e in range(0,len(sysSpecs['ustreamConduits'])):
                ustream_depths_tmp = np.hstack((ustream_depths_tmp,env.depthL(sysSpecs['ustreamConduits'][e])/sysSpecs['max_depths'][e]))
            ustream_depths = np.vstack((ustream_depths,ustream_depths_tmp))
            dstream_flows_tmp = []
            for e in range(0,len(sysSpecs['branchConduits'])):
                dstream_flows_tmp = np.hstack((dstream_flows_tmp,env.flow(sysSpecs['branchConduits'][e])))
            dstream_flows = np.vstack((dstream_flows,dstream_flows_tmp))
            WRRF_flow = np.vstack((WRRF_flow,env.flow(sysSpecs['WRRFConduit'])))
            WRRF_TSS = np.vstack((WRRF_TSS,env.get_pollutant_link(sysSpecs['WRRFConduit'])))
            WRRF_TSSLoad = np.vstack((WRRF_TSSLoad,WRRF_flow[-1] * WRRF_TSS[-1] * 0.000062428))

            if j == 1:
                price = ps
                demands = PDs
                supply = PSs
                gates = action
                if ctrlParams['hierarchy'] == 1:
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        setpts_all = setpts
                    else:
                        setpts_all = [setpts_flow,setpts_TSS]
                else:
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        setpts_all = np.zeros(n_trunkline)
                    else:
                        setpts_all = np.zeros(2*n_trunkline)
            else:
                price = np.vstack((price,ps))
                demands = np.vstack((demands,PDs))
                supply = np.vstack((supply,PSs))
                gates = np.vstack((gates,action))
                if ctrlParams['hierarchy'] == 1:
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        setpts_all = np.vstack((setpts_all,setpts))
                    else:
                        setpts_all = np.vstack((setpts_all,[setpts_flow,setpts_TSS]))
                else:
                    if (ctrlParams['objType'] == "flow") or (ctrlParams['objType'] == "TSS"):
                        setpts_all = np.vstack((setpts_all,np.zeros(n_trunkline)))
                    else:
                        setpts_all = np.vstack((setpts_all,np.zeros(2*n_trunkline)))

    return time_state, time_control, ustream_depths, dstream_flows, WRRF_flow, WRRF_TSSLoad, price, demands, gates, setpts_all, ctrlParams
