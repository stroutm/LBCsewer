import numpy as np
from orifice_testing import get_target_setting

def mbc_noaction(ustream, dstream, setpts, uparam, dparam, n_tanks, setptThres):
    if setptThres == 1:
        p = (sum(uparam*ustream) - sum(dparam*np.maximum(setpts-dstream,np.zeros(len(dstream)))))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) - sum(dparam*(setpts-dstream)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)

    return p, PD, PS

def mbc_noaction_multi(ustream, dstream, setpts, uparam, dparam, n_tanks, setptThres):
    if setptThres == 1:
        p = (sum(uparam*ustream) - dparam[0]*np.maximum(setpts[0]-dstream[0],0.) - dparam[1]*np.maximum(setpts[1]-dstream[1],0.))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) - dparam[0]*(setpts[0]-dstream[0]) - dparam[1]*(setpts[1]-dstream[1]))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)

    return p, PD, PS

def mbc(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, max_flow, max_TSSLoad, units, orifice_diams, shape, ustream_node_depths, dstream_node_depths, uInvert, dInvert, setptThres, objType, ustream_TSSConc):
    if setptThres == 1:
        p = (sum(uparam*ustream) - sum(dparam*np.maximum(setpts-dstream,np.zeros(len(dstream)))))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) - sum(dparam*(setpts-dstream)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        if PD[i] >= p:
            if PS == 0:
                Qi = 0
            else:
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
                    # Weight desired flow by dparam (epsilon) values
                    Qi = (dparam[0]*Qi_flow+dparam[1]*Qi_TSS)/(dparam[0]+dparam[1])

            action[i], note, head = get_target_setting(ustream_node_depths[i],dstream_node_depths[i],Qi,action[i],shape,units,discharge,orifice_diams[i],uInvert[i],dInvert[i])
        else:
            action[i] = 0.0
        if ustream[i] > 0.95:
            action[i] += 0.2
        action[i] = min(action[i],1.0)

    return p, PD, PS, action

def mbc_multi(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, max_flow, max_TSSLoad, units, orifice_diams, shape, ustream_node_depths, dstream_node_depths, uInvert, dInvert, setptThres, objType, ustream_TSSConc):
    if setptThres == 1:
        p = (sum(uparam*ustream) - dparam[0]*np.maximum(setpts[0]-dstream[0],0.) - dparam[1]*np.maximum(setpts[1]-dstream[1],0.))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) - dparam[0]*(setpts[0]-dstream[0]) - dparam[1]*(setpts[1]-dstream[1]))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        if PD[i] >= p:
            if PS == 0:
                Qi = 0
            else:
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
                    # Weight desired flow by dparam (epsilon) values
                    Qi = (dparam[0]*Qi_flow+dparam[1]*Qi_TSS)/(dparam[0]+dparam[1])

            action[i], note, head = get_target_setting(ustream_node_depths[i],dstream_node_depths[i],Qi,action[i],shape,units,discharge,orifice_diams[i],uInvert[i],dInvert[i])
        else:
            action[i] = 0.0
        if ustream[i] > 0.95:
            action[i] += 0.2
        action[i] = min(action[i],1.0)

    return p, PD, PS, action

def mbc_bin(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, setptThres):
    if setptThres == 1:
        p = (sum(uparam*ustream) + sum(dparam*np.maximum(dstream-setpts,np.zeros(len(dstream)))))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) + sum(dparam*(dstream-setpts)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        # Binary option 1
        #if PS == 0:
        #    Qi = 0.0
        #else:
        #    Qi = PD[i]/PS*setpts[0] # setpts[0] assumed to be downstream flow setpoint
        #if ustream[i] == 0:
        #    action[i] = 0.0
        #    action[i+n_tanks] = 1.0
        #else:
        #    h2i = Qi/(discharge*1*np.sqrt(2*9.81*ustream[i]))
        #    action[i] = max(min(h2i/2,1.0),0.0)
        #    if action[i] >= 0.5:
        #        action[i] = 1.0
        #        action[i+n_tanks] = 0.0
        #    else:
        #        action[i] = 0.0
        #        action[i+n_tanks] = 1.0
        #if ustream[i] > 0.95:
        #    action[i] = 1.0
        #    action[i+n_tanks] = 0.0
        # Binary option 2
        if PD[i] >= p:
            action[i] = 1.0 # dam down gate
            action[i+n_tanks] = 0.0 # dam up gate
        else:
            action[i] = 0.0 # dam down gate
            action[i+n_tanks] = 1.0 # dam up gate
        if ustream[i] > 0.95:
            action[i] = 1.0 # dam down gate
            action[i+n_tanks] = 0.0 # dam up gate

    return p, PD, PS, action

def perf(actual, setpt):
    x = actual-setpt
    #x = actual-setpt*np.ones(len(actual))
    value_over = x*(x>0)

    return value_over

def TSScalc(n_tanks, tankDepth, tankDepthPrev, flow, runoff, TSSconcRO, timeStep):
    TSSCT = np.zeros(n_tanks)
    TSSL = np.zeros(n_tanks)
    #for i in range(0,n_tanks):
    #    runoff = runoffs[i]
    #    TSSconcrunoff = 1000
    #    if tankDepth[i] > 0.01:
    #        TSSCT[i] = (timeStep*TSSconcrunoff*runoff/(timeStep*flow[i]+2000*tankDepth[i])) * np.exp(-0.05/((tankDepthPrev[i]+tankDepth[i])/2)*timeStep)
    #    else:
    #        TSSCT[i] = 0.0
    #    TSSL[i] = TSSCT[i] * flow[i]
    if tankDepth > 0.01 and flow > 0.01:
        TSSCT = (timeStep*TSSconcRO*runoff/(timeStep*flow+150*tankDepth)) * np.exp(-0.0068/((tankDepthPrev+tankDepth)/2)*timeStep)
    else:
        TSSCT = 0.0

    return TSSCT
