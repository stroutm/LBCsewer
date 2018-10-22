import matplotlib.pyplot as plt
import numpy as np

def plot_noControl(n_trunkline, n_ISDs, plotParams, time, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes, timeBegin, timeEnd):
    ## Adds no control case results to plots

    # Water depths in conduits upstream of ISDs
    plt.subplot(141)
    for a in range(0,sum(n_ISDs)):
        plt.plot(time[timeBegin:timeEnd],ustream_depths[timeBegin:timeEnd,a],
                    label = "No control, " + plotParams['labels'][a],
                    color = plotParams['colors'][a], linestyle = ':')

    # Flow at downstream WRRF
    plt.subplot(143)
    if plotParams['normalize'] == 1:
        plt.plot(time[timeBegin:timeEnd],WRRF_flow[timeBegin:timeEnd]/maxes['max_flow_WRRF'], label = "No control, WRRF flow",
                color = plotParams['colors'][-1], linestyle = ':')
    else:
        plt.plot(time[timeBegin:timeEnd],WRRF_flow[timeBegin:timeEnd], label = "No control, WRRF flow",
                color = plotParams['colors'][-1], linestyle = ':')

    # TSS load at downstream WRRF
    plt.subplot(144)
    if plotParams['normalize'] == 1:
        plt.plot(time[timeBegin:timeEnd],WRRF_TSSLoad[timeBegin:timeEnd]/maxes['max_TSSLoad_WRRF'], label = "No control, WRRF TSS Load",
                color = plotParams['colors'][-1], linestyle = ':')
    else:
        plt.plot(time[timeBegin:timeEnd],WRRF_TSSLoad[timeBegin:timeEnd], label = "No control, WRRF TSS Load",
                color = plotParams['colors'][-1], linestyle = ':')

    # Flow at downstream point of each branch
    #plt.subplot(235)
    #for a in range(0,n_trunkline):
    #    plt.plot(time,dstream_flows[:,a],
    #                label = "No control, " + plotParams['labels'][a-n_trunkline],
    #                color = plotParams['colors'][a-n_trunkline-1], linestyle = ':')

def plot_control(n_trunkline, n_ISDs, ctrlParams, plotParams, time_state, time_control, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes, setpts_all, price, demands, gates, timeBegin, timeEnd):
    ## Adds no control case results to plots

    for a in range(0,sum(n_ISDs)):
        # Water depths in conduits upstream of ISDs (i.e., demanders of capacity)
        plt.subplot(141)
        plt.plot(time_state[timeBegin:timeEnd],ustream_depths[timeBegin:timeEnd,a],
                    label = "MBC, " + plotParams['labels'][a],
                    color = plotParams['colors'][a], linestyle = '-')

        # Gate positions at all controlled ISDs
        #plt.subplot(222)
        #plt.plot(time_state[timeBegin:timeEnd],gates[timeBegin:timeEnd,a],
        #            label = "Dam down, " + plotParams['labels'][a],
        #            color = plotParams['colors'][a], linestyle = '-')

        # Demands by each upstream storage asset
        #plt.subplot(236)
        #plt.plot(time_control,demands[:,a],
        #            label = "Demand, " + plotParams['labels'][a],
        #            color = plotParams['colors'][a-n_trunkline-1], linestyle = '-')

    # Flow at downstream WRRF (i.e., seller of capacity)
    plt.subplot(143)
    if plotParams['normalize'] == 1:
        plt.plot(time_state[timeBegin:timeEnd],WRRF_flow[timeBegin:timeEnd]/maxes['max_flow_WRRF'], label = "MBC, WRRF flow",
                color = plotParams['colors'][-1], linestyle = '-')
        if ctrlParams['objType'] == "flow":
            plt.plot(time_state[timeBegin:timeEnd],ctrlParams['setpt_WRRF_flow']*np.ones(timeEnd-timeBegin),
                color = 'k', label = 'Setpoint')
        elif ctrlParams['objType'] == "both":
            plt.plot(time_state[timeBegin:timeEnd],ctrlParams['setpt_WRRF_flow']*np.ones(timeEnd-timeBegin),
                color = 'k', label = 'Setpoint')
    else:
        plt.plot(time_state[timeBegin:timeEnd],WRRF_flow[timeBegin:timeEnd], label = "MBC, WRRF flow",
                color = plotParams['colors'][-1], linestyle = '-')
        if ctrlParams['objType'] == "flow":
            plt.plot(time_state[timeBegin:timeEnd],maxes['max_flow_WRRF']*ctrlParams['setpt_WRRF_flow']*np.ones(timeEnd-timeBegin),
                color = 'k', label = 'Setpoint')
        elif ctrlParams['objType'] == "both":
            plt.plot(time_state[timeBegin:timeEnd],maxes['max_flow_WRRF']*ctrlParams['setpt_WRRF_flow']*np.ones(timeEnd-timeBegin),
                color = 'k', label = 'Setpoint')

    # TSS load at downstream WRRF (i.e., seller of capacity)
    plt.subplot(144)
    if plotParams['normalize'] == 1:
        plt.plot(time_state[timeBegin:timeEnd],WRRF_TSSLoad[timeBegin:timeEnd]/maxes['max_TSSLoad_WRRF'], label = "MBC, WRRF TSS Load",
                color = plotParams['colors'][-1], linestyle = '-')
        if ctrlParams['objType'] == "TSS":
            plt.plot(time_state[timeBegin:timeEnd],ctrlParams['setpt_WRRF_TSS']*np.ones(timeEnd-timeBegin), label = 'Setpoint',
                    color = 'k')
        elif ctrlParams['objType'] == "both":
            plt.plot(time_state[timeBegin:timeEnd],ctrlParams['setpt_WRRF_TSS']*np.ones(timeEnd-timeBegin), label = 'Setpoint',
                    color = 'k')
    else:
        plt.plot(time_state[timeBegin:timeEnd],WRRF_TSSLoad[timeBegin:timeEnd], label = "No control, WRRF TSS Load",
                color = plotParams['colors'][-1], linestyle = '-')
        if ctrlParams['objType'] == "TSS":
            plt.plot(time_state[timeBegin:timeEnd],maxes['max_TSSLoad_WRRF']*ctrlParams['setpt_WRRF_TSS']*np.ones(timeEnd-timeBegin), label = 'Setpoint',
                    color = 'k')
        elif ctrlParams['objType'] == "both":
            plt.plot(time_state[timeBegin:timeEnd],maxes['max_TSSLoad_WRRF']*ctrlParams['setpt_WRRF_TSS']*np.ones(timeEnd-timeBegin), label = 'Setpoint',
                    color = 'k')

    #for a in range(0,n_trunkline):
        # Flow at downstream point of each branch and setpts for each
        #plt.subplot(235)
        #if plotParams['normalize'] == 1:
        #    plt.plot(time_state,dstream_flows[:,a]/maxes['max_flow_dstream'][a],
        #            label = "MBC, " + plotParams['labels'][a-n_trunkline],
        #            color = plotParams['colors'][a-n_trunkline-1], linestyle = '-')
        #    if ctrlParams['objType'] == "flow":
        #        plt.plot(time_control,setpts_all[:,a],
        #            label = "Setpoint, " + plotParams['labels'][a-n_trunkline],
        #            color = plotParams['colors'][a-n_trunkline-1], linestyle = '--')
        #else:
        #    plt.plot(time_state,dstream_flows[:,a],
        #            label = "MBC, " + plotParams['labels'][a-n_trunkline],
        #            color = plotParams['colors'][a-n_trunkline-1], linestyle = '-')
        #    if ctrlParams['objType'] == "flow":
        #        plt.plot(time_control,maxes['max_flow_dstream'][a]*setpts_all[:,a],
        #            label = "Setpoint, " + plotParams['labels'][a-n_trunkline],
        #            color = plotParams['colors'][a-n_trunkline-1], linestyle = '--')

        # Market price for capacity along each branch
        #if ctrlParams['hierarchy'] == 1:
            #plt.subplot(236)
            #plt.plot(time_control,price[:,a],
            #        label = "price, " + plotParams['labels'][a-n_trunkline],
            #        color = plotParams['colors'][a-n_trunkline-1], linestyle = '--')

    #if ctrlParams['hierarchy'] == 0:
        #plt.subplot(236)
        #plt.plot(time_control,price,
        #            label = "price", color = 'k', linestyle = '--')

def plot_finish(normalize):
    ## Adds labels, limits, etc. to plots and shows plot

    # Water depths in conduits upstream of ISDs
    plt.subplot(141)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    plt.xlim(0,30)
    #plt.legend()

    # Flow at downstream WRRF
    plt.subplot(143)
    if normalize == 1:
        plt.ylim(0,1)
    #else:
    #    plt.ylim(0,600)
    plt.ylabel('WRRF Flow ($\mathregular{ft^3/s}$)')
    plt.xlim(0,30)
    #plt.legend()

    # TSS load at downstream WRRF
    plt.subplot(144)
    plt.ylabel('WRRF TSS Load ($\mathregular{lb/s}$)')
    plt.xlim(0,30)
    #plt.legend()

    # Flow at downstream point of each branch
    #plt.subplot(235)
    #plt.ylabel('Branch Flows ($\mathregular{ft^3/s}$)')
    #if normalize == 1:
    #    plt.ylim(0,1)
    #plt.legend()

    # Gate positions at all controlled ISDs
    #plt.subplot(222)
    #plt.ylabel('Gate Opening')
    #plt.ylim(0,1)
    #plt.legend()
    plt.subplot(142)
    plt.ylabel('Precipitation')
    plt.xlim(0,30)

    # Market price for capacity along each branch and demands by each upstream
    # storage asset
    #plt.subplot(236)
    #plt.ylabel('Price and Demands')
    #plt.legend()

    #plt.show()
