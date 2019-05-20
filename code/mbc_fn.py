import numpy as np
from orifice_testing import get_target_setting

def propRelease(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, max_flow, max_TSSLoad, units, orifice_diams, shape, ustream_node_depths, dstream_node_depths, uInvert, dInvert, setptThres, objType, ustream_TSSConc):
    if setptThres == 1:
        p = (sum(uparam*ustream) - dparam[0]*np.maximum(setpts[0]-dstream[0],0.) - dparam[1]*np.maximum(setpts[1]-dstream[1],0.))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) - dparam[0]*(setpts[0]-dstream[0]) - dparam[1]*(setpts[1]-dstream[1]))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    C = np.zeros(n_tanks)
    uparam = uparam*np.ones(n_tanks)
    for i in range(0,n_tanks):
        if ustream[i] > 0.95:
            uparam[i] = (2+ustream[i])*uparam[i]
        elif ustream[i] > 0.75:
            uparam[i] = (1+ustream[i])*uparam[i]
    for i in range(0,n_tanks):
        C[i] = ustream[i]**2
        PD[i] = max(-p + uparam[i]*ustream[i],0)
    Cbar = sum(C)/n_tanks
    #PS = sum(PD)
    PS = sum(PD[PD>=p])
    for i in range(0,n_tanks):
        if objType == "flow":
            Qi = C[i]/Cbar*setpts[0]*max_flow
        elif objType == "TSS":
            if ustream_TSSConc[i] < 0.01:
                Qi = 0
            else:
                Qi = C[i]/Cbar*setpts[1]*max_TSSLoad/ustream_TSSConc[i]/0.000062428
        elif objType == "both":
            Qi_flow = C[i]/Cbar*setpts[0]*max_flow
            if ustream_TSSConc[i] < 0.01:
                Qi_TSS = 0
            else:
                Qi_TSS = C[i]/Cbar*setpts[1]*max_TSSLoad/ustream_TSSConc[i]/0.000062428
            Qi = (dparam[0]*Qi_flow+dparam[1]*Qi_TSS)/(dparam[0]+dparam[1])

        action[i], note, head = get_target_setting(ustream_node_depths[i],dstream_node_depths[i],Qi,action[i],shape,units,discharge,orifice_diams[i],uInvert[i],dInvert[i])

        #if ustream[i] > 0.95:
        #    action[i] += 0.2
        action[i] = min(action[i],1.0)

    return p, C, Cbar, action

def mbc_noaction(ustream, dstream, setpts, uparam, dparam, n_tanks, setptThres):
    if setptThres == 1:
        p = (sum(uparam*ustream) - sum(dparam*np.maximum(setpts-dstream,np.zeros(len(dstream)))))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) - sum(dparam*(setpts-dstream)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    uparam = uparam*np.ones(n_tanks)
    for i in range(0,n_tanks):
        uparam[i] = uparam[i] * (1+ustream[i])
        #if ustream[i] > 0.95:
        #    uparam[i] = (2+ustream[i])*uparam[i]
        #elif ustream[i] > 0.75:
        #    uparam[i] = (1+ustream[i])*uparam[i]
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam[i]*ustream[i],0)
    #PS = sum(PD)
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
        #if ustream[i] > 0.95:
        #    uparam[i] = (2+ustream[i])*uparam[i]
        #elif ustream[i] > 0.75:
        #    uparam[i] = (1+ustream[i])*uparam[i]
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam[i]*ustream[i],0)
    #PS = sum(PD)
    PS = sum(PD[PD>=p])

    return p, PD, PS

def mbc(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, max_flow, max_TSSLoad, units, orifice_diams, shape, ustream_node_depths, dstream_node_depths, uInvert, dInvert, setptThres, objType, ustream_TSSConc):
    alpha = uparam*np.ones(n_tanks)
    beta = np.zeros(n_tanks)
    betamax = 2
    N = 1 #TESTING
    #ORIGINAL.0 uparam = uparam*np.ones(n_tanks)
    for i in range(0,n_tanks):
        #ORINGAL.1 beta[i] = alpha[i] * (1+ustream[i])
        #beta[i] = alpha[i]*ustream[i] #TESTING1
        beta[i] = alpha[i]*(np.exp(N*ustream[i])-1)/(np.exp(N)-1) #TESTING2
        #ORIGINAL.0 uparam[i] = uparam[i] * (1+ustream[i])
    if setptThres == 1:
        Cbar = (sum(beta*ustream) - sum(dparam*np.maximum(setpts-dstream,np.zeros(len(dstream)))))/(1 + n_tanks)
        #ORIGINAL.0 p = (sum(uparam*ustream) - sum(dparam*np.maximum(setpts-dstream,np.zeros(len(dstream)))))/(1 + n_tanks)
    else:
        Cbar = (sum(beta*ustream) - sum(dparam*(setpts-dstream)))/(1 + n_tanks)
        #ORIGINAL.0 p = (sum(uparam*ustream) - sum(dparam*(setpts-dstream)))/(1 + n_tanks)
    releaseCrit = np.zeros(n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        #ORIGINAL.1 releaseCrit[i] = max(beta[i]/betamax*ustream[i],0.)
        releaseCrit[i] = (np.exp(N*ustream[i])-1)/(np.exp(N)-1) #TESTING1
        PD[i] = max(beta[i]*ustream[i]-Cbar,0.)
        #ORIGINAL.0 PD[i] = max(-p + uparam[i]*ustream[i],0.)
        #PD[i] = ustream[i]-Cbar #TESTING2
        PD[i] = max(beta[i]*ustream[i]-Cbar,0.) #TESTING2.2
        #PD[i] = beta[i] #TESTING2.3
        #PD[i] = beta[i]*ustream[i] #TESTING2.4
    PS = sum(PD[releaseCrit>=Cbar])
    PS = sum(PD) #TESTING2
    #ORIGINAL.0 PS = sum(PD[PD>=p])
    for i in range(0,n_tanks):
        #TESTING2
        if objType == "flow":
            Qi = PD[i]/PS*setpts[0]*max_flow # setpts[0] assumed to be downstream flow setpoint
        elif objType == "TSS":
            if ustream_TSSConc[i] < 0.01:
                Qi = 0
                #ADDED TO CHECK
                print('i = ' + str(i))
                print(ustream_TSSConc[i])
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
        '''
        if releaseCrit[i] >= Cbar:
        #ORIGINAL.0 if PD[i] >= p:
            if PS == 0:
                Qi = 0
            else:
                if objType == "flow":
                    Qi = PD[i]/PS*setpts[0]*max_flow # setpts[0] assumed to be downstream flow setpoint
                elif objType == "TSS":
                    if ustream_TSSConc[i] < 0.01:
                        Qi = 0
                        #ADDED TO CHECK
                        print('i = ' + str(i))
                        print(ustream_TSSConc[i])
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
        else:
            action[i] = 0.0
        '''
        action[i] = min(action[i],1.0)

    return Cbar, PD, PS, action

def mbc_multi(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, max_flow, max_TSSLoad, units, orifice_diams, shape, ustream_node_depths, dstream_node_depths, uInvert, dInvert, setptThres, objType, ustream_TSSConc):
    alpha = uparam*np.ones(n_tanks)
    beta = np.zeros(n_tanks)
    betamax = 2
    N = 1 #TESTING
    #ORIGINAL.0 uparam = uparam*np.ones(n_tanks)
    for i in range(0,n_tanks):
        #ORIGINAL.1 beta[i] = alpha[i] * (1+ustream[i])
        #beta[i] = alpha[i]*ustream[i] #TESTING1
        beta[i] = alpha[i]*(np.exp(N*ustream[i])-1)/(np.exp(N)-1) #TESTING2
        #ORIGINAL.0 uparam[i] = uparam[i] * (1+ustream[i])
    if setptThres == 1:
        Cbar = (sum(beta*ustream) - dparam[0]*np.maximum(setpts[0]-dstream[0],0.) - dparam[1]*np.maximum(setpts[1]-dstream[1],0.))/(1 + n_tanks)
        #ORIGINAL.0 p = (sum(uparam*ustream) - dparam[0]*np.maximum(setpts[0]-dstream[0],0.) - dparam[1]*np.maximum(setpts[1]-dstream[1],0.))/(1 + n_tanks)
    else:
        Cbar = (sum(beta*ustream) - dparam[0]*(setpts[0]-dstream[0]) - dparam[1]*(setpts[1]-dstream[1]))/(1 + n_tanks)
        #ORIGINAL.0 p = (sum(uparam*ustream) - dparam[0]*(setpts[0]-dstream[0]) - dparam[1]*(setpts[1]-dstream[1]))/(1 + n_tanks)
    releaseCrit = np.zeros(n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        #ORIGINAL.1 releaseCrit[i] = max(beta[i]/betamax*ustream[i],0.)
        releaseCrit[i] = (np.exp(N*ustream[i])-1)/(np.exp(N)-1) #TESTING1
        PD[i] = max(beta[i]*ustream[i]-Cbar,0.)
        #ORIGINAL.0 PD[i] = max(-p + uparam[i]*ustream[i],0.)
        PD[i] = max(beta[i]*ustream[i]-Cbar,0.) #TESTING2.2
    PS = sum(PD[releaseCrit>=Cbar])
    PS = sum(PD) #TESTING2
    #ORIGINAL.0 PS = sum(PD[PD>=p])
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
        '''
        if releaseCrit[i] >= Cbar:
        #ORIGINAL.0 if PD[i] >= p:
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
        '''
        #if ustream[i] > 0.95:
        #    action[i] += 0.2
        action[i] = min(action[i],1.0)

    return Cbar, PD, PS, action

def mbc_bin(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, setptThres):
    if setptThres == 1:
        p = (sum(uparam*ustream) + sum(dparam*np.maximum(dstream-setpts,np.zeros(len(dstream)))))/(1 + n_tanks)
    else:
        p = (sum(uparam*ustream) + sum(dparam*(dstream-setpts)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    uparam = uparam*np.ones(n_tanks)
    for i in range(0,n_tanks):
        uparam[i] = uparam[i] * (1+ustream[i])
        #if ustream[i] > 0.95:
        #    uparam[i] = (2+ustream[i])*uparam[i]
        #elif ustream[i] > 0.75:
        #    uparam[i] = (1+ustream[i])*uparam[i]
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam[i]*ustream[i],0)
    #PS = sum(PD)
    PS = sum(PD[PD>=p])
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
