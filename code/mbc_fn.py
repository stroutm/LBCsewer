import numpy as np
from orifice_testing import get_target_setting_2

def mbc_noaction(ustream, dstream, setpts, uparam, dparam, n_tanks):
    p = (sum(uparam*ustream) + sum(dparam*(dstream-setpts)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)

    return p, PD, PS

def mbc(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge, max_flow, units, orifice_diams, shape, ustream_node_depths, dstream_node_depths, uInvert, dInvert):
    p = (sum(uparam*ustream) + sum(dparam*(dstream-setpts)))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + uparam*ustream[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        if PD[i] >= p:
            if PS == 0:
                Qi = 0
            else:
                Qi = PD[i]/PS*setpts[0]*max_flow # setpts[0] assumed to be downstream flow setpoint

            action[i], note, head = get_target_setting(ustream_node_depths[i],dstream_node_depths[i],Qi,action[i],shape,units,discharge,orifice_diams[i],uInvert[i],dInvert[i])
        else:
            action[i] = 0.0
        if ustream[i] > 0.95:
            action[i] += 0.2
        action[i] = min(action[i],1.0)

    return p, PD, PS, action

def mbc_bin(ustream, dstream, setpts, uparam, dparam, n_tanks, action, discharge):
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

def TSScalc(n_tanks, tankDepth, tankDepthPrev, flow, runoffs, timeStep):
    TSSCT = np.zeros(n_tanks)
    TSSL = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        runoff = runoffs[i]
        TSSconcrunoff = 1000
        if tankDepth[i] > 0.01:
            TSSCT[i] = (timeStep*TSSconcrunoff*runoff/(timeStep*flow[i]+2000*tankDepth[i])) * np.exp(-0.05/((tankDepthPrev[i]+tankDepth[i])/2)*timeStep)
        else:
            TSSCT[i] = 0.0
        TSSL[i] = TSSCT[i] * flow[i]

    return TSSL
