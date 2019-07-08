import numpy as np
from orifice_testing import get_target_setting

def mbc_noaction(ustream, dstream, setpts, uparam, dparam, n_tanks, setptThres):
    if setptThres == 1:
        p = (sum(uparam*ustream) - sum(dparam*np.maximum(setpts-dstream,np.zeros(len(dstream)))))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) - sum(dparam*(setpts-dstream)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    uparam = uparam*np.ones(n_tanks)
    for i in range(0,n_tanks):
        uparam[i] = uparam[i] * (1+ustream[i])
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam[i]*ustream[i],0)
    PS = sum(PD[PD>=p])

    return p, PD, PS

def mbc_noaction_multi(ustream, dstream, setpts, uparam, dparam, n_tanks, setptThres):
    if setptThres == 1:
        p = (sum(uparam*ustream) - dparam[0]*np.maximum(setpts[0]-dstream[0],0.) - dparam[1]*np.maximum(setpts[1]-dstream[1],0.))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) - dparam[0]*(setpts[0]-dstream[0]) - dparam[1]*(setpts[1]-dstream[1]))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    uparam = uparam*np.ones(n_tanks)
    for i in range(0,n_tanks):
        uparam[i] = uparam[i] * (1+ustream[i])
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam[i]*ustream[i],0)
    PS = sum(PD[PD>=p])

    return p, PD, PS

def mbc(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, max_flow, max_TSSLoad, units, orifice_diams, shape, ustream_node_depths, dstream_node_depths, uInvert, dInvert, setptThres, objType, ustream_TSSConc):
    alpha = uparam*np.ones(n_tanks)
    beta = np.zeros(n_tanks)
    N = 100
    for i in range(0,n_tanks):
        beta[i] = alpha[i]*(np.exp(N*ustream[i])-1)/(np.exp(N)-1)
    if setptThres == 1:
        Cbar = (sum(beta*ustream) - sum(dparam*np.maximum(setpts-dstream,np.zeros(len(dstream)))))/(1 + n_tanks)
    else:
        Cbar = (sum(beta*ustream) - sum(dparam*(setpts-dstream)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(beta[i]*ustream[i]-Cbar,0.)
    PS = sum(PD)
    for i in range(0,n_tanks):
        if objType == "flow":
            Qi = PD[i]/PS*setpts[0]*max_flow # setpts[0] assumed to be downstream flow setpoint
        elif objType == "TSS":
            if ustream_TSSConc[i] < 0.01:
                Qi = 0
            else:
                Qi = PD[i]/PS*setpts[0]*max_TSSLoad/ustream_TSSConc[i]/0.000062428
        elif objType == "both":
            Qi_flow = PD[i]/PS*setpts[0]*max_flow
            if ustream_TSSConc[i] < 0.01:
                Qi_TSS = 0
            else:
                Qi_TSS = PD[i]/PS*setpts[1]*max_TSSLoad/ustream_TSSConc[i]/0.000062428
            Qi = (dparam[0]*Qi_flow+dparam[1]*Qi_TSS)/(dparam[0]+dparam[1])

        action[i], note, head = get_target_setting(ustream_node_depths[i],dstream_node_depths[i],Qi,action[i],shape,units,discharge,orifice_diams[i],uInvert[i],dInvert[i])
        action[i] = min(action[i],1.0)

    return Cbar, PD, PS, action

def mbc_multi(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, max_flow, max_TSSLoad, units, orifice_diams, shape, ustream_node_depths, dstream_node_depths, uInvert, dInvert, setptThres, objType, ustream_TSSConc):
    alpha = uparam*np.ones(n_tanks)
    beta = np.zeros(n_tanks)
    N = 100
    for i in range(0,n_tanks):
        beta[i] = alpha[i]*(np.exp(N*ustream[i])-1)/(np.exp(N)-1)
    if setptThres == 1:
        Cbar = (sum(beta*ustream) - dparam[0]*np.maximum(setpts[0]-dstream[0],0.) - dparam[1]*np.maximum(setpts[1]-dstream[1],0.))/(1 + n_tanks)
    else:
        Cbar = (sum(beta*ustream) - dparam[0]*(setpts[0]-dstream[0]) - dparam[1]*(setpts[1]-dstream[1]))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(beta[i]*ustream[i]-Cbar,0.)
    PS = sum(PD)
    for i in range(0,n_tanks):
        if objType == "both":
            Qi_flow = PD[i]/PS*setpts[0]*max_flow
            if ustream_TSSConc[i] < 0.01:
                Qi_TSS = 0
            else:
                Qi_TSS = PD[i]/PS*setpts[1]*max_TSSLoad/ustream_TSSConc[i]/0.000062428
            # Weight desired flow by dparam (epsilon) values
            Qi = (dparam[0]*Qi_flow+dparam[1]*Qi_TSS)/(dparam[0]+dparam[1])

        action[i], note, head = get_target_setting(ustream_node_depths[i],dstream_node_depths[i],Qi,action[i],shape,units,discharge,orifice_diams[i],uInvert[i],dInvert[i])
        action[i] = min(action[i],1.0)

    return Cbar, PD, PS, action
