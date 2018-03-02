import numpy as np

def mbc(state, TSSload, setptOutflow, setptTSSload, beta, epsilon, zeta, max_depths, n_tanks, action):
    tot_flow = sum(state[0,n_tanks:2*n_tanks])
    p = (sum(beta*state[0,0:n_tanks]/max_depths)
        + epsilon*(tot_flow-setptOutflow) + zeta*(TSSload-setptTSSload))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + beta*state[0,i]/max_depths[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        if PS == 0:
            Qi = 0
        else:
            Qi = PD[i]/PS*setptOutflow
        if state[0,i] == 0:
            action[i] = 0.5
        else:
            h2i = Qi/(0.61*1*np.sqrt(2*9.81*state[0,i]))
            action[i] = max(min(h2i/2,1.0),0.0)
        if state[0,i]/max_depths[i] > 0.95:
            action[i] = 1.0

    return p, PD, PS, tot_flow, action

def mbc_bin(state, TSSload, setptOutflow, setptTSSload, beta, epsilon, zeta, max_depths, n_tanks, action):
    tot_flow = sum(state[0,n_tanks:2*n_tanks])
    p = (sum(beta*state[0,0:n_tanks]/max_depths)
        + epsilon*(tot_flow-setptOutflow) + zeta*(TSSload-setptTSSload))/(1 + n_tanks)
    PD = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        PD[i] = max(-p + beta*state[0,i]/max_depths[i],0)
    PS = sum(PD)
    for i in range(0,n_tanks):
        # Binary option 1
        #if PS == 0:
        #    Qi = 0.0
        #else:
        #    Qi = PD[i]/PS*setptOutflow
        #if state[0,i] == 0:
        #    action[i] = 0.0
        #else:
        #    h2i = Qi/(0.61*1*np.sqrt(2*9.81*state[0,i]))
        #    action[i] = max(min(h2i/2,1.0),0.0)
        #    if action[i] >= 0.5:
        #        action[i] = 1.0
        #    else:
        #        action[i] = 0.0
        #if state[0,i]/max_depths[i] > 0.95:
        #    action[i] = 1.0
        # Binary option 2
        if PD[i] >= p:
            action[i] = 1
        else:
            action[i] = 0 # 0.1424 is area equivalent to 80% filled from bottom
        if state[0,i]/max_depths[i] > 0.95:
            action[i] = 1

    return p, PD, PS, tot_flow, action

def perf(actual, setpt):
    x = actual-setpt*np.ones(len(actual))
    value_over = x*(x>0)

    return value_over

def TSScalc(n_tanks, tankDepth, tankDepthPrev, flow):
    TSSCT = np.zeros(n_tanks)
    TSSL = np.zeros(n_tanks)
    for i in range(0,n_tanks):
        runoff = 10
        TSSconcrunoff = 1000
        if tankDepth[i] > 0.01:
            TSSCT[i] = (30*TSSconcrunoff*runoff/(30*flow[i]+2000*tankDepth[i])) * np.exp(-0.05/((tankDepthPrev[i]+tankDepth[i])/2)*30)
        else:
            TSSCT[i] = 0.0
        TSSL[i] = TSSCT[i] * flow[i]

    return TSSL
