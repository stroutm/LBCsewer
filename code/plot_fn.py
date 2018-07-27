import matplotlib.pyplot as plt
import numpy as np

def plot_noControl(n_trunkline, n_ISDs, normalize, labels, colors, time, ustream_depths, WRRF_flow, max_flow_WRRF, WRRF_TSSLoad, max_TSSLoad_WRRF, dstream_flows):
    ## Adds no control case results to plots

    # Water depths in conduits upstream of ISDs
    plt.subplot(321)
    for a in range(0,sum(n_ISDs)):
        plt.plot(time,ustream_depths[:,a],
                    label = "No control, " + labels[a],
                    color = colors[a], linestyle = ':')

    # Flow at downstream WRRF
    plt.subplot(322)
    if normalize == 1:
        plt.plot(time,WRRF_flow/max_flow_WRRF, label = "No control, WRRF flow",
                color = colors[-1], linestyle = ':')
    else:
        plt.plot(time,WRRF_flow, label = "No control, WRRF flow",
                color = colors[-1], linestyle = ':')

    # TSS load at downstream WRRF
    plt.subplot(323)
    if normalize == 1:
        plt.plot(time,WRRF_TSSLoad/max_TSSLoad_WRRF, label = "No control, WRRF TSS Load",
                color = colors[-1], linestyle = ':')
    else:
        plt.plot(time,WRRF_TSSLoad, label = "No control, WRRF TSS Load",
                color = colors[-1], linestyle = ':')

    # Flow at downstream point of each branch
    plt.subplot(324)
    for a in range(0,n_trunkline):
        plt.plot(time,dstream_flows[:,a],
                    label = "No control, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = ':')

def plot_control(n_trunkline, n_ISDs, setptMethod, objType, normalize, labels, colors, time_state, time_control, ustream_depths, WRRF_flow, max_flow_WRRF, setpt_WRRF_flow, WRRF_TSSLoad, max_TSSLoad_WRRF, setpt_WRRF_TSS, dstream_flows, max_flow_dstream, setpts_all, price, demands, gates):
    ## Adds no control case results to plots

    for a in range(0,sum(n_ISDs)):
        # Water depths in conduits upstream of ISDs (i.e., demanders of capacity)
        plt.subplot(321)
        plt.plot(time_state,ustream_depths[:,a],
                    label = "MBC, " + labels[a],
                    color = colors[a], linestyle = '-')

        # Gate positions at all controlled ISDs
        plt.subplot(325)
        plt.plot(time_state,gates[:,a],
                    label = "Dam down, " + labels[a],
                    color = colors[a], linestyle = '-')

        # Demands by each upstream storage asset
        plt.subplot(326)
        plt.plot(time_control,demands[:,a],
                    label = "Demand, " + labels[a],
                    color = colors[a-n_trunkline-1], linestyle = '-')

    # Flow at downstream WRRF (i.e., seller of capacity)
    plt.subplot(322)
    if normalize == 1:
        plt.plot(time_state,WRRF_flow/max_flow_WRRF, label = "MBC, WRRF flow",
                color = colors[-1], linestyle = '-')
        if setptMethod == "automatic" and objType == "flow":
            plt.plot(time_state,setpt_WRRF_flow*np.ones(len(WRRF_flow)),
                color = 'k', label = 'Setpoint')
        elif setptMethod == "automatic" and objType == "both":
            plt.plot(time_state,setpt_WRRF_flow*np.ones(len(WRRF_flow)),
                color = 'k', label = 'Setpoint')
    else:
        plt.plot(time_state,WRRF_flow, label = "MBC, WRRF flow",
                color = colors[-1], linestyle = '-')
        if setptMethod == "automatic" and objType == "flow":
            plt.plot(time_state,max_flow_WRRF*setpt_WRRF_flow*np.ones(len(WRRF_flow)),
                color = 'k', label = 'Setpoint')
        elif setptMethod == "automatic" and objType == "both":
            plt.plot(time_state,max_flow_WRRF*setpt_WRRF_flow*np.ones(len(WRRF_flow)),
                color = 'k', label = 'Setpoint')

    # TSS load at downstream WRRF (i.e., seller of capacity)
    plt.subplot(323)
    if normalize == 1:
        plt.plot(time_state,WRRF_TSSLoad/max_TSSLoad_WRRF, label = "MBC, WRRF TSS Load",
                color = colors[-1], linestyle = '-')
        if setptMethod == "automatic" and objType == "TSS":
            plt.plot(time_state,setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), label = 'Setpoint',
                    color = 'k')
        elif setptMethod == "automatic" and objType == "both":
            plt.plot(time_state,setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), label = 'Setpoint',
                    color = 'k')
    else:
        plt.plot(time_state,WRRF_TSSLoad, label = "No control, WRRF TSS Load",
                color = colors[-1], linestyle = '-')
        if setptMethod == "automatic" and objType == "TSS":
            plt.plot(time_state,max_TSSLoad_WRRF*setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), label = 'Setpoint',
                    color = 'k')
        elif setptMethod == "automatic" and objType == "both":
            plt.plot(time_state,max_TSSLoad_WRRF*setpt_WRRF_TSS*np.ones(len(WRRF_TSSLoad)), label = 'Setpoint',
                    color = 'k')

    for a in range(0,n_trunkline):
        # Flow at downstream point of each branch and setpts for each, for
        # either setptMethod == "automatic" or "manual"
        plt.subplot(324)
        if normalize == 1:
            plt.plot(time_state,dstream_flows[:,a]/max_flow_dstream[a],
                    label = "MBC, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = '-')
            if objType == "flow":
                plt.plot(time_control,setpts_all[:,a],
                    label = "Setpoint, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = '--')
        else:
            plt.plot(time_state,dstream_flows[:,a],
                    label = "MBC, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = '-')
            if objType == "flow":
                plt.plot(time_control,max_flow_dstream[a]*setpts_all[:,a],
                    label = "Setpoint, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = '--')

        # Market price for capacity along each branch
        plt.subplot(326)
        plt.plot(time_control,price[:,a],
                    label = "price, " + labels[a-n_trunkline],
                    color = colors[a-n_trunkline-1], linestyle = '--')

def plot_finish(normalize):
    ## Adds labels, limits, etc. to plots and shows plot

    # Water depths in conduits upstream of ISDs
    plt.subplot(321)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    #plt.legend()

    # Flow at downstream WRRF
    plt.subplot(322)
    if normalize == 1:
        plt.ylim(0,1)
    #else:
    #    plt.ylim(0,600)
    plt.ylabel('WRRF Flow ($\mathregular{ft^3/s}$)')
    #plt.legend()

    # TSS load at downstream WRRF
    plt.subplot(323)
    plt.ylabel('WRRF TSS Load ($\mathregular{lb/s}$)')
    #plt.legend()

    # Flow at downstream point of each branch
    plt.subplot(324)
    plt.ylabel('Branch Flows ($\mathregular{ft^3/s}$)')
    if normalize == 1:
        plt.ylim(0,1)

    # Gate positions at all controlled ISDs
    plt.subplot(325)
    plt.ylabel('Gate Opening')
    plt.ylim(0,1)
    #plt.legend()

    # Market price for capacity along each branch and demands by each upstream
    # storage asset
    plt.subplot(326)
    plt.ylabel('Price and Demands')
    #plt.legend()

    plt.show()
