import matplotlib.pyplot as plt
import numpy as np

def plot_noControl(n_trunkline, n_ISDs, plotParams, time, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes, timeBegin, timeEnd):
    ## Adds no control case results to plots
    

    # Water depths in conduits upstream of ISDs
    #plt.subplot(151)
    #plt.subplot(131)
    #for a in range(0,sum(n_ISDs)):
    #    plt.plot(time[timeBegin:timeEnd],ustream_depths[timeBegin:timeEnd,a],
    #                label = "No control, " + plotParams['labels'][a],
    #                color = plotParams['colors'][a], linestyle = ':')

    # Flow at downstream WRRF
    #plt.subplot(153)
    plt.subplot(132)
    if plotParams['normalize'] == 1:
        plt.plot(time[timeBegin:timeEnd],WRRF_flow[timeBegin:timeEnd]/maxes['max_flow_WRRF'], label = "No control, WRRF flow",
                color = plotParams['colors'][-1], linestyle = ':')
    else:
        plt.plot(time[timeBegin:timeEnd],WRRF_flow[timeBegin:timeEnd]/35.3147, label = "No control, WRRF flow",
                color = plotParams['colors'][-1], linestyle = ':')
    
    
    # TSS load at downstream WRRF
    #plt.subplot(154)
    plt.subplot(133)
    if plotParams['normalize'] == 1:
        plt.plot(time[timeBegin:timeEnd],WRRF_TSSLoad[timeBegin:timeEnd]/maxes['max_TSSLoad_WRRF'], label = "No control, WRRF TSS Load",
                color = plotParams['colors'][-1], linestyle = ':')
    else:
        plt.plot(time[timeBegin:timeEnd],WRRF_TSSLoad[timeBegin:timeEnd]/2.20462, label = "No control, WRRF TSS Load",
                color = plotParams['colors'][-1], linestyle = ':')

def plot_control(n_trunkline, n_ISDs, ctrlParams, plotParams, time_state, time_control, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes, setpts_all, price, demands, gates, timeBegin, timeEnd):
    ## Adds no control case results to plots

    for a in range(0,sum(n_ISDs)):
        # Water depths in conduits upstream of ISDs (i.e., demanders of capacity)
        #plt.subplot(151)
        plt.subplot(131)
        plt.plot(time_state,ustream_depths[:,a],
                    label = "MBC, " + plotParams['labels'][a],
                    color = plotParams['colors'][a], linestyle = '-')
    '''
    for a in range(0,sum(n_ISDs)):
        plt.subplot(155)
        plt.plot(time_control,demands[:,a], label = "Demand " + plotParams['labels'][a],
                 color = plotParams['colors'][a], linestyle = '-')
    plt.plot(time_control,price, label = "Price",
             color = 'k', linestyle = '-')
    
    for a in range(0,sum(n_ISDs)):
        plt.subplot(152)
        plt.plot(time_state,gates[:,a], label = "Gate actions " + plotParams['labels'][a],
                 color = plotParams['colors'][a], linestyle = '-')
    '''
    # Flow at downstream WRRF (i.e., seller of capacity)
    #plt.subplot(153)
    plt.subplot(132)
    if plotParams['normalize'] == 1:
        plt.plot(time_state,WRRF_flow/maxes['max_flow_WRRF'], label = "MBC, WRRF flow",
                color = plotParams['colors'][-1], linestyle = '-')
        '''
        if ctrlParams['objType'] == "flow":
            plt.plot(time_state,ctrlParams['setpt_WRRF_flow']*np.ones((timeEnd-timeBegin,1)),
                color = 'k', label = 'Setpoint')
        elif ctrlParams['objType'] == "both":
            plt.plot(time_state,ctrlParams['setpt_WRRF_flow']*np.ones((timeEnd-timeBegin,1)),
                color = 'k', label = 'Setpoint')
        '''
    else:
        plt.plot(time_state,WRRF_flow/35.3147, label = "MBC, WRRF flow",
                color = plotParams['colors'][-1], linestyle = '-')
        '''
        if ctrlParams['objType'] == "flow":
            plt.plot(time_state,maxes['max_flow_WRRF']*ctrlParams['setpt_WRRF_flow']*np.ones((timeEnd-timeBegin,1)),
                color = 'k', label = 'Setpoint')
        elif ctrlParams['objType'] == "both":
            plt.plot(time_state,maxes['max_flow_WRRF']*ctrlParams['setpt_WRRF_flow']*np.ones((timeEnd-timeBegin,1)),
                color = 'k', label = 'Setpoint')
        '''

    # TSS load at downstream WRRF (i.e., seller of capacity)
    #plt.subplot(154)
    plt.subplot(133)
    if plotParams['normalize'] == 1:
        plt.plot(time_state,WRRF_TSSLoad/maxes['max_TSSLoad_WRRF'], label = "MBC, WRRF TSS Load",
                color = plotParams['colors'][-1], linestyle = '-')
        '''
        if ctrlParams['objType'] == "TSS":
            plt.plot(time_state,ctrlParams['setpt_WRRF_TSS']*np.ones((timeEnd-timeBegin,1)), label = 'Setpoint',
                    color = 'k')
        elif ctrlParams['objType'] == "both":
            plt.plot(time_state,ctrlParams['setpt_WRRF_TSS']*np.ones((timeEnd-timeBegin,1)), label = 'Setpoint',
                    color = 'k')
        '''
    else:
        plt.plot(time_state,WRRF_TSSLoad/2.20462, label = "MBC, WRRF TSS Load",
                color = plotParams['colors'][-1], linestyle = '-')
        '''
        if ctrlParams['objType'] == "TSS":
            plt.plot(time_state,maxes['max_TSSLoad_WRRF']*ctrlParams['setpt_WRRF_TSS']*np.ones((timeEnd-timeBegin,1)), label = 'Setpoint',
                    color = 'k')
        elif ctrlParams['objType'] == "both":
            plt.plot(time_state,maxes['max_TSSLoad_WRRF']*ctrlParams['setpt_WRRF_TSS']*np.ones((timeEnd-timeBegin,1)), label = 'Setpoint',
                    color = 'k')
        '''

def plot_finish(normalize, timeBegin, timeEnd, routime_step):
    ## Adds labels, limits, etc. to plots and shows plot

    # Water depths in conduits upstream of ISDs
    #plt.subplot(151)
    plt.subplot(131)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    #plt.xlim(0,(timeEnd-timeBegin)/(24*60*60/routime_step))
    plt.xlim(timeBegin/(24*60*60/routime_step),timeEnd/(24*60*60/routime_step))
    plt.xlabel('Time (days)')
    #plt.legend()

    # Flow at downstream WRRF
    #plt.subplot(153)
    plt.subplot(132)
    plt.ylim(0,25)
    plt.ylabel('WRRF Flow ($\mathregular{m^3/s}$)')
    #plt.xlim(0,(timeEnd-timeBegin)/(24*60*60/routime_step))
    plt.xlim(timeBegin/(24*60*60/routime_step),timeEnd/(24*60*60/routime_step))
    plt.xlabel('Time (days)')
    #plt.legend()

    # TSS load at downstream WRRF
    #plt.subplot(154)
    plt.subplot(133)
    plt.ylabel('WRRF TSS Load ($\mathregular{kg/s}$)')
    plt.ylim(0,3.5)
    #plt.xlim(0,(timeEnd-timeBegin)/(24*60*60/routime_step))
    plt.xlim(timeBegin/(24*60*60/routime_step),timeEnd/(24*60*60/routime_step))
    plt.xlabel('Time (days)')
    #plt.legend()
    '''
    # Gate positions at all controlled ISDs
    plt.subplot(152)
    plt.ylabel('Gate actions')
    #plt.xlim(0,(timeEnd-timeBegin)/(24*60*60/routime_step))
    plt.xlim(timeBegin/(24*60*60/routime_step),timeEnd/(24*60*60/routime_step))
    plt.xlabel('Time (days)')
    plt.ylim(0,1)
    
    plt.subplot(155)
    plt.ylabel('Demands and price')
    #plt.xlim(0,(timeEnd-timeBegin)/(24*60*60/routime_step))
    plt.xlim(timeBegin/(24*60*60/routime_step),timeEnd/(24*60*60/routime_step))
    plt.xlabel('Time (days)')
    '''