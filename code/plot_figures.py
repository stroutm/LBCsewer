import matplotlib.pyplot as plt
import pickle
import numpy as np

fileNames = ['test_flow_20170504.pkl','test_flow_20170504_some_11.pkl']

n_trunkline = 3
n_ISDs = [1,1,1]
setptMethod = "automatic"
objType = "flow"
# 2: upstream depths; 3: WRRF flow; 4: WRRF TSS load; 5: downstream flows; 6: demands/price; 7: gates
plot = 3
normalize = 0
colors = ['#276278','#167070','#55a6a6','#b5491a','#fe6625','#fe9262','#fb9334','#ffb16c','#414a4f','#006592','#003d59','#167070','#fe6625','#003d59','#66747c']
labels = ['K','J','I','H','G','F','E','D','C','B','A','I-K','D-H','A-C']
max_flow_dstream = np.zeros(n_trunkline)
no_control = 1
control = 1

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 14.0}

plt.rc('font', **font)

# No control
with open('../data/results/no_control/'+fileNames[0]) as f:
      time, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, max_flow_WRRF, max_TSSLoad_WRRF = pickle.load(f)

for q in range(0,n_trunkline):
    max_flow_dstream[q] = max(dstream_flows[:,q])
if no_control == 1:
    if plot == 2:
        for a in range(0,sum(n_ISDs)):
            plt.plot(time,ustream_depths[:,a],
                label = "No control, " + labels[a],
                color = colors[a], linestyle = ':')
    elif plot == 3:
        if normalize == 1:
            plt.plot(time,WRRF_flow/max_flow_WRRF, label = "No control, WRRF flow", color = colors[-1],
                linestyle = ':')
        else:
            plt.plot(time,WRRF_flow, label = "No control, WRRF flow", color = colors[-1],
                    linestyle = ':')
    elif plot == 4:
        if normalize == 1:
            plt.plot(time,WRRF_TSSLoad/max_TSSLoad_WRRF, label = "No control, WRRF TSS Load", color = colors[-1],
                linestyle = ':')
        else:
            plt.plot(time,WRRF_TSSLoad, label = "No control, WRRF TSS Load", color = colors[-1],
                linestyle = ':')
    elif plot == 5:
        for a in range(0,n_trunkline):
            if normalize == 1:
                plt.plot(time,dstream_flows[:,a]/max_flow_dstream[a],
                    label = "No control, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = ':')
            else:
                plt.plot(time,dstream_flows[:,a],
                    label = "No control, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = ':')

# Control
if objType == "both":
    with open('../data/results/control/'+fileNames[1]) as f:
        ISDs, weights, time_state, time_control, ustream_depths, WRRF_flow, setpt_WRRF_flow, setpt_WRRF_TSS, max_flow_WRRF, max_TSSLoad_WRRF, WRRF_TSSLoad, dstream_flows, max_flow_dstream, demands, price, gates = pickle.load(f)
else:
    with open('../data/results/control/'+fileNames[1]) as f:
        ISDs, weights, time_state, time_control, ustream_depths, WRRF_flow, setpt_WRRF_flow, setpt_WRRF_TSS, max_flow_WRRF, max_TSSLoad_WRRF, WRRF_TSSLoad, dstream_flows, setpts_all, max_flow_dstream, demands, price, gates = pickle.load(f)

if control == 1:
    if plot == 2:
        for a in range(0,sum(n_ISDs)):
            plt.plot(time_state,ustream_depths[:,a],
                    label = "MBC, " + labels[a],
                    color = colors[a], linestyle = '-')
    elif plot == 3:
        if normalize == 1:
            plt.plot(time_state,WRRF_flow/max_flow_WRRF, label = "MBC, WRRF flow", color = colors[-1],
                linestyle = '-')
            if setptMethod == "automatic" and objType == "flow":
                plt.plot(time_state,setpt_WRRF_flow*np.ones(len(WRRF_flow)), color = 'k', label = 'Setpoint')
            elif setptMethod == "automatic" and objType == "both":
                plt.plot(time_state,setpt_WRRF_flow*np.ones(len(WRRF_flow)), color = 'k', label = 'Setpoint')
        else:
            plt.plot(time_state,WRRF_flow, label = "MBC, WRRF flow", color = colors[-1],
                linestyle = '-')
            if setptMethod == "automatic" and objType == "flow":
                plt.plot(time_state,max_flow_WRRF*setpt_WRRF_flow*np.ones(len(WRRF_flow)), color = 'k', label = 'Setpoint')
            elif setptMethod == "automatic" and objType == "both":
                plt.plot(time_state,max_flow_WRRF*setpt_WRRF_flow*np.ones(len(WRRF_flow)), color = 'k', label = 'Setpoint')
    elif plot == 4:
        if normalize == 1:
            plt.plot(time_state,WRRF_TSSLoad/max_TSSLoad_WRRF, label = "MBC, WRRF TSS Load", color = colors[-1],
                linestyle = '-')
            if setptMethod == "automatic" and objType == "TSS":
                plt.plot(time_state,setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), color = 'k', label = 'Setpoint')
            elif setptMethod == "automatic" and objType == "both":
                plt.plot(time_state,setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), color = 'k', label = 'Setpoint')
        else:
            plt.plot(time_state,WRRF_TSSLoad, label = "MBC, WRRF TSS Load", color = colors[-1],
                linestyle = '-')
            if setptMethod == "automatic" and objType == "TSS":
                plt.plot(time_state,max_TSSLoad_WRRF*setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), color = 'k', label = 'Setpoint')
            elif setptMethod == "automatic" and objType == "both":
                plt.plot(time_state,max_TSSLoad_WRRF*setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), color = 'k', label = 'Setpoint')
    elif plot == 5:
        for a in range(0,n_trunkline):
            if normalize == 1:
                plt.plot(time_state,dstream_flows[:,a]/max_flow_dstream[a],
                    label = "MBC, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = '-')
                if objType == "flow":
                    plt.plot(time_state,setpts_all[:,a],
                        label = "Setpoint, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = '--')
            else:
                plt.plot(time_state,dstream_flows[:,a],
                    label = "MBC, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = '-')
                #plt.plot(time,max_flow_dstream[a]*dstream_flows[:,a],
                #    label = "MBC, " + labels[a-n_trunkline],
                #    color = colors[a-n_trunkline-1], linestyle = '-')
                if objType == "flow":
                    plt.plot(time_control,max_flow_dstream[a]*setpts_all[:,a],
                        label = "Setpoint, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = '--')
    elif plot == 6:
        for a in range(0,sum(n_ISDs)):
            plt.plot(time_control,demands[:,a],
                label = "Demand, " + labels[a],
                color = colors[a-n_trunkline-1], linestyle = '-')
        for a in range(0,n_trunkline):
            plt.plot(time_control,price[:,a],
                label = "price, " + labels[a-n_trunkline],
                color = colors[a-n_trunkline-1], linestyle = '--')
    elif plot == 7:
        for a in range(0,sum(n_ISDs)):
            plt.plot(time_state,gates[:,a],
                label = "Dam down, " + labels[a],
                color = colors[a], linestyle = '-')

if plot == 1:
    plt.subplot(321)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    plt.rc('font', **font)
    #plt.legend()

    plt.subplot(322)
    if normalize == 1:
        plt.ylim(0,1)
    plt.ylabel('WRRF Flow ($\mathregular{ft^3/s}$)')
    plt.rc('font', **font)
    #plt.legend()

    plt.subplot(323)
    plt.ylabel('WRRF TSS Load ($\mathregular{lb/s}$)')
    plt.rc('font', **font)
    #plt.legend()

    plt.subplot(324)
    plt.ylabel('Branch Flows ($\mathregular{ft^3/s}$)')
    if normalize == 1:
        plt.ylim(0,1)
    plt.rc('font', **font)
    #plt.legend()

    plt.subplot(325)
    plt.ylabel('Gate Opening')
    plt.ylim(0,1)
    plt.rc('font', **font)
    #plt.legend()

    plt.subplot(326)
    plt.ylabel('Price and Demands')
    plt.rc('font', **font)
    #plt.legend()

    plt.show()
elif plot == 2:
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    plt.rc('font', **font)
    plt.show()
elif plot == 3:
    if normalize == 1:
        plt.ylim(0,1)
    plt.ylabel('WRRF Flow ($\mathregular{ft^3/s}$)')
    plt.rc('font', **font)
    plt.show()
elif plot == 4:
    plt.ylabel('WRRF TSS Load ($\mathregular{lb/s}$)')
    plt.rc('font', **font)
    plt.show()
elif plot == 5:
    plt.ylabel('Branch Flows ($\mathregular{ft^3/s}$)')
    if normalize == 1:
        plt.ylim(0,1)
    plt.rc('font', **font)
    plt.show()
elif plot == 6:
    plt.ylabel('Price and Demands')
    plt.rc('font', **font)
    plt.show()
elif plot == 7:
    plt.ylabel('Gate Opening')
    plt.ylim(0,1)
    plt.rc('font', **font)
    plt.show()
