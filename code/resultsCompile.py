import pickle
import numpy as np

# Enter result file information
storm = '201701'
objType = 'flow'
hierarchyOpt = 'NH'
ISD_arrangement = 'A_flood_short'
# Trial number range
noRangeBegin = 1
noRangeEnd = 2
routime_step = 10 # seconds
# Timestep range
timeBegin = 2*24*60*60/routime_step # start 2 days in
if storm == '201701':
    timeEnd = 62*24*60*60/routime_step #365*24*60*60/routime_step #
elif storm == '201806':
    timeEnd = 259200
saveType = "numpy" # "numpy" or "pickle"

dryWeatherFlowMax = 222.3
dryWeatherTSSLoadMax = 2.3165

# Compiles file name for no control results file
if saveType == "pickle":
    fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '.pkl'
elif saveType == "numpy":
    fileName = 'trial2_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '.npy'
    fileName = 'test_' + objType + '_final_short.npy'

# Loads and stores no control results as workspace variables
if saveType == "pickle":
    with open('../data/results/no_control/'+fileName) as f:
      time,ustream_depths,WRRF_flow,WRRF_TSSLoad,dstream_flows,max_flow_WRRF,max_TSSLoad_WRRF = pickle.load(f)
      no_control_res = {'time': time,
                          'ustream_depths': ustream_depths,
                          'WRRF_flow': WRRF_flow,
                          'WRRF_TSSLoad': WRRF_TSSLoad,
                          'dstream_flows': dstream_flows,
                          'max_flow_WRRF': max_flow_WRRF,
                          'max_TSSLoad_WRRF': max_TSSLoad_WRRF
                          }
elif saveType == "numpy":
    no_control_res_load = np.load('../data/results/no_control/' + fileName)
    no_control_res = {'time': no_control_res_load.item().get('time'),
                        'ustream_depths': no_control_res_load.item().get('ustream_depths'),
                        'WRRF_flow': no_control_res_load.item().get('WRRF_flow'),
                        'WRRF_TSSLoad': no_control_res_load.item().get('WRRF_TSSLoad'),
                        'dstream_flows': no_control_res_load.item().get('dstream_flows'),
                        'max_flow_WRRF': no_control_res_load.item().get('max_flow_WRRF'),
                        'max_TSSLoad_WRRF': no_control_res_load.item().get('max_TSSLoad_WRRF'),
                        'flooding':no_control_res_load.item().get('stats')['flooding']
                        }

# Selected no-control results
# Average flow at WRRF for no-control simulation
#FlowBar_NC = np.average(no_control_res['WRRF_flow'][timeBegin:timeEnd])
# Average TSS load at WRRF for no-control simulation
#TSSBar_NC = np.average(no_control_res['WRRF_TSSLoad'][timeBegin:timeEnd])
# Variance of flow at WRRF for no-control simulation
#CHANGE FlowVarArr_NC = np.zeros(timeEnd-timeBegin)
FlowVarArr_NC = np.zeros(timeEnd)
# Variance of TSS load at WRRF for no-control simulation
#CHANGE TSSVarArr_NC = np.zeros(timeEnd-timeBegin)
TSSVarArr_NC = np.zeros(timeEnd)
timeFlooding_NC = 0
tssLCumulative_no_control = 0.

firstDay = timeBegin
lastDay = timeBegin
DW_indices = []
#WW_indices = np.ones(timeEnd-timeBegin)
DW_indices = range(timeBegin,timeEnd)
daily_max_flow_NC = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/(24*60*60/routime_step))))
#for t in range(timeBegin/(24*60*60/routime_step),int(np.floor((float(timeEnd)-float(timeBegin))/(24*60*60/routime_step)))):
for t in range(0,int(np.floor((float(timeEnd)-float(timeBegin))/(24*60*60/routime_step)))):
    firstDay = lastDay
    lastDay += 24*60*60/routime_step
    daily_max_flow_NC[t] = max(no_control_res['WRRF_flow'][firstDay:lastDay]) - dryWeatherFlowMax
    #if abs(daily_max_flow_NC[t]/dryWeatherFlowMax) <= 0.1:
    #    DW_indices.extend(range(firstDay,lastDay))
    if abs(daily_max_flow_NC[t]/dryWeatherFlowMax) > 0.1:
        #WW_indices[t*24*60*60/routime_step:(t+2)*24*60*60/routime_step] = np.zeros(2*24*60*60/routime_step)
        DW_indices[t*24*60*60/routime_step:(t+2)*24*60*60/routime_step] = np.zeros(2*24*60*60/routime_step)
DW_indices = [x for x in DW_indices if x != 0]
FlowBar_DW_NC = np.average(no_control_res['WRRF_flow'][DW_indices])
TSSBar_DW_NC = np.average(no_control_res['WRRF_TSSLoad'][DW_indices])

# Loop through no-control simulation
for t in range(timeBegin,timeEnd):
    if max(no_control_res['ustream_depths'][t]) == 1.0:
        timeFlooding_NC += 1
    #CHANGE FlowVarArr_NC[t-timeBegin] = (no_control_res['WRRF_flow'][t] - FlowBar_DW_NC)**2
    FlowVarArr_NC[t] = (no_control_res['WRRF_flow'][t] - FlowBar_DW_NC)**2
    #CHANGE TSSVarArr_NC[t-timeBegin] = (no_control_res['WRRF_TSSLoad'][t] - TSSBar_DW_NC)**2
    TSSVarArr_NC[t] = (no_control_res['WRRF_TSSLoad'][t] - TSSBar_DW_NC)**2
    tssLCumulative_no_control += no_control_res['WRRF_TSSLoad'][t] * routime_step
# Finish variance calculation of WRRF flow and TSS load by averaging
# variance arrays
FlowVar_NC = np.average(FlowVarArr_NC[DW_indices])
TSSVar_NC = np.average(TSSVarArr_NC[DW_indices])
'''
import matplotlib.pyplot as plt
plt.figure(1)
plt.subplot(211)
plt.plot(range(timeBegin,timeEnd),FlowVarArr_NC[timeBegin:timeEnd],label='flow, all var')
plt.plot(DW_indices,FlowVarArr_NC[DW_indices],'.')
plt.legend()
plt.subplot(212)
plt.plot(range(timeBegin,timeEnd),TSSVarArr_NC[timeBegin:timeEnd],label='TSS L, all var')
plt.plot(DW_indices,TSSVarArr_NC[DW_indices],'.',label='TSS L, dw var')
plt.legend()
plt.show()
'''
# Initializes summary array for performance metrics of no-control case
summ_NC = np.zeros((1,17),float)

# Compile performance metrics in summary array for no-control simulation
summ_NC[0,0] = 0
summ_NC[0,1] = 0
summ_NC[0,2] = 0
summ_NC[0,3] = 0
summ_NC[0,4] = 0
summ_NC[0,5] = 0
summ_NC[0,6] = 0
summ_NC[0,7] = 0
summ_NC[0,8] = 0
summ_NC[0,9] = 0
summ_NC[0,10] = 0
summ_NC[0,11] = 0
summ_NC[0,12] = 0
summ_NC[0,13] = timeFlooding_NC
summ_NC[0,14] = FlowVar_NC
summ_NC[0,15] = TSSVar_NC
summ_NC[0,16] = no_control_res['flooding']

# Save summary array of no-control performance metrics in a compliation .csv file
saveFileName_NC = '../data/results/no_control/resultSumm_' + storm + '_short.csv'
np.savetxt(saveFileName_NC, summ_NC, delimiter=",")

# Initializes summary array for performance metrics
summ = np.zeros((noRangeEnd-noRangeBegin,17),float)

# Loops through each trial number
for i in range(noRangeBegin,noRangeEnd):
    print(i)
    # Compiles file name for each control results file
    if saveType == "pickle":
        fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '_' + "%02d" % (i) + '.pkl'
    elif saveType == "numpy":
        fileName = 'trial2_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '_' + "%02d" % (i) + '.npy'
        fileName = 'test_' + objType + '_final_' + "%02d" % (i) + '.npy'

    n_trunkline = 3
    if ISD_arrangement == 'A':
        n_ISDs = [3,5,3]
    else:
        n_ISDs = [1,1,1]

    # Loads and stores control results as workspace variables
    if saveType == "pickle":
        if objType == "both":
            with open('../data/results/control/'+fileName) as f:
                ISDs,weights,time_state,time_control,ustream_depths,WRRF_flow,setpt_WRRF_flow,setpt_WRRF_TSS,max_flow_WRRF,max_TSSLoad_WRRF,WRRF_TSSLoad,dstream_flows,max_flow_dstream,demands,price,gates = pickle.load(f)
            control_res = {'ISDs': ISDs,
                            'weights': weights,
                            'time_state': time_state,
                            'time_control': time_control,
                            'ustream_depths': ustream_depths,
                            'WRRF_flow': WRRF_flow,
                            'setpt_WRRF_flow': setpt_WRRF_flow,
                            'setpt_WRRF_TSS': setpt_WRRF_TSS,
                            'max_flow_WRRF': max_flow_WRRF,
                            'max_TSSLoad_WRRF': max_TSSLoad_WRRF,
                            'WRRF_TSSLoad': WRRF_TSSLoad,
                            'dstream_flows': dstream_flows,
                            'max_flow_dstream': max_flow_dstream,
                            'demands': demands,
                            'price': price,
                            'gates': gates
                            }
        elif objType == "flow" or objType == "TSS":
            with open('../data/results/control/'+fileName) as f:
                ISDs,weights,time_state,time_control,ustream_depths,WRRF_flow,setpt_WRRF_flow,setpt_WRRF_TSS,max_flow_WRRF,max_TSSLoad_WRRF,WRRF_TSSLoad,dstream_flows,setpts_all,max_flow_dstream,demands,price,gates = pickle.load(f)
            control_res = {'ISDs': ISDs,
                            'weights': weights,
                            'time_state': time_state,
                            'time_control': time_control,
                            'ustream_depths': ustream_depths,
                            'WRRF_flow': WRRF_flow,
                            'setpt_WRRF_flow': setpt_WRRF_flow,
                            'setpt_WRRF_TSS': setpt_WRRF_TSS,
                            'max_flow_WRRF': max_flow_WRRF,
                            'max_TSSLoad_WRRF': max_TSSLoad_WRRF,
                            'WRRF_TSSLoad': WRRF_TSSLoad,
                            'dstream_flows': dstream_flows,
                            'setpts_all': setpts_all,
                            'max_flow_dstream': max_flow_dstream,
                            'demands': demands,
                            'price': price,
                            'gates': gates
                            }
    elif saveType == "numpy":
        control_res_load = np.load('../data/results/control/' + fileName)
        if objType == "both":
            control_res = {'ISDs': control_res_load.item().get('ISDs'),
                            'weights': control_res_load.item().get('weights'),
                            'time_state': control_res_load.item().get('time_state'),
                            'time_control': control_res_load.item().get('time_control'),
                            'ustream_depths': control_res_load.item().get('ustream_depths'),
                            'WRRF_flow': np.float32(control_res_load.item().get('WRRF_flow')),
                            'setpt_WRRF_flow': control_res_load.item().get('setpt_WRRF_flow'),
                            'setpt_WRRF_TSS': control_res_load.item().get('setpt_WRRF_TSS'),
                            'max_flow_WRRF': control_res_load.item().get('max_flow_WRRF'),
                            'max_TSSLoad_WRRF': control_res_load.item().get('max_TSSLoad_WRRF'),
                            'WRRF_TSSLoad': np.float32(control_res_load.item().get('WRRF_TSSLoad')),
                            'dstream_flows': control_res_load.item().get('dstream_flows'),
                            'max_flow_dstream': control_res_load.item().get('max_flow_dstream'),
                            'demands': control_res_load.item().get('demands'),
                            'price': control_res_load.item().get('price'),
                            'gates': control_res_load.item().get('gates'),
                            'flooding': control_res_load.item().get('stats')['flooding']
                            }
        elif objType == "flow" or objType == "TSS":
            control_res = {'ISDs': control_res_load.item().get('ISDs'),
                            'weights': control_res_load.item().get('weights'),
                            'time_state': control_res_load.item().get('time_state'),
                            'time_control': control_res_load.item().get('time_control'),
                            'ustream_depths': control_res_load.item().get('ustream_depths'),
                            'WRRF_flow': np.float32(control_res_load.item().get('WRRF_flow')),
                            'setpt_WRRF_flow': control_res_load.item().get('setpt_WRRF_flow'),
                            'setpt_WRRF_TSS': control_res_load.item().get('setpt_WRRF_TSS'),
                            'max_flow_WRRF': control_res_load.item().get('max_flow_WRRF'),
                            'max_TSSLoad_WRRF': control_res_load.item().get('max_TSSLoad_WRRF'),
                            'WRRF_TSSLoad': np.float32(control_res_load.item().get('WRRF_TSSLoad')),
                            'dstream_flows': control_res_load.item().get('dstream_flows'),
                            'setpts_all': control_res_load.item().get('setpts_all'),
                            'max_flow_dstream': control_res_load.item().get('max_flow_dstream'),
                            'demands': control_res_load.item().get('demands'),
                            'price': control_res_load.item().get('price'),
                            'gates': control_res_load.item().get('gates'),
                            'flooding': control_res_load.item().get('stats')['flooding']
                            }

    # Adjusts setpoint to account for delay between upstream and downstream points;
    # These calculations are based on previous simulations where downstream
    # Setpoints are adjusted to account for delay between upstream and downstream;
    # points; setpoints were specified and the actual achieved setpoints were measured;
    # thus, the achieved setpoints are some fraction of the given setpoints which
    # include some notion of upstream/downstream delay without having to explicitly
    # measure the time of concentration for the network
    control_res['setpt_WRRF_flow'] = 195.6/447.82*control_res['setpt_WRRF_flow']
    control_res['setpt_WRRF_TSS'] = 1.9177/4.8736*control_res['setpt_WRRF_TSS']
    
    FlowBar_DW_C = np.average(control_res['WRRF_flow'][DW_indices])
    TSSBar_DW_C = np.average(control_res['WRRF_TSSLoad'][DW_indices])

    ## Initialize performance metrics, described below
    # Number of timesteps over flow setpoint
    timeOverFlowSetpt = 0
    # Number of timesteps over TSS load setpoint
    timeOverTSSLSetpt = 0
    # Cumulative volume over flow setpoint
    flowOverSetpt = 0
    # Cumulative TSS mass over TSS load setpoint
    tssLOverSetpt = 0
    # Cumulative TSS mass received by downstream WRRF for control simulation
    tssLCumulative_control = 0
    # Number of timesteps where at least one storage asset had a normalized
    # depth of 1.0 (full)
    timeFlooding = 0
    # Average flow at WRRF for control simulation
    #FlowBar = np.average(control_res['WRRF_flow'][timeBegin:timeEnd])
    # Average TSS load at WRRF for control simulation
    #TSSBar = np.average(control_res['WRRF_TSSLoad'][timeBegin:timeEnd])
    # Variance of flow at WRRF for control simulation
    #CHANGE FlowVarArr = np.zeros(timeEnd-timeBegin)
    FlowVarArr = np.zeros(timeEnd)
    # Variance of TSS load at WRRF for control simulation
    #CHANGE TSSVarArr = np.zeros(timeEnd-timeBegin)
    TSSVarArr = np.zeros(timeEnd)

    first = 0; last = 0
    # Maximum flow for no control simulation in week-long chunks
    weekly_max_flow_NC = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/(7*24*60*60/routime_step))))
    # Maximum flow for control simulation in week-long chunks
    weekly_max_flow_C = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/(7*24*60*60/routime_step))))
    # Maximum TSS load for no control simulation in week-long chunks
    weekly_max_TSS_NC = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/(7*24*60*60/routime_step))))
    # Maximum TSS load for control simulation in week-long chunks
    weekly_max_TSS_C = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/(7*24*60*60/routime_step))))
    # WRRF flow peak reduction between no control and control simulation
    weekly_flow_peak_red = []
    # WRRF TSS load peak reduction between no control and control simulation
    weekly_TSS_peak_red = []
    # Loop through control simulation in week-long chucks
    for t in range(0,int(np.floor((float(timeEnd)-float(timeBegin))/(7*24*60*60/routime_step)))):
        first = last
        last += 7*24*60*60/routime_step # number of timesteps in a week
        weekly_max_flow_NC[t] = max(no_control_res['WRRF_flow'][first:last]) - dryWeatherFlowMax
        weekly_max_flow_C[t] = max(control_res['WRRF_flow'][first:last]) - dryWeatherFlowMax
        weekly_max_TSS_NC[t] = max(no_control_res['WRRF_TSSLoad'][first:last]) - dryWeatherTSSLoadMax
        weekly_max_TSS_C[t] = max(control_res['WRRF_TSSLoad'][first:last]) - dryWeatherTSSLoadMax
        # Only include no control peaks 10% over dry-weather max to ensure they are wet-weather
        # peaks and not including weeks with only dry weather
        if weekly_max_flow_NC[t] > dryWeatherFlowMax * 0.1:
            weekly_flow_peak_red = np.hstack((weekly_flow_peak_red,(weekly_max_flow_NC[t]-weekly_max_flow_C[t])/weekly_max_flow_NC[t]))
        # Only include no control peaks 10% over dry-weather max to ensure they are wet-weather
        # peaks and not including weeks with only dry weather
        if weekly_max_TSS_NC[t] > dryWeatherTSSLoadMax * 0.1:
            weekly_TSS_peak_red = np.hstack((weekly_TSS_peak_red,(weekly_max_TSS_NC[t]-weekly_max_TSS_C[t])/weekly_max_TSS_NC[t]))
    # Calculate average peak reduction for flow and TSS load
    flowPeakRed = np.average(weekly_flow_peak_red)
    tssLPeakRed = np.average(weekly_TSS_peak_red)
    
    # Loop through control simulation
    for t in range(timeBegin,timeEnd):
        if objType == "flow":
            if control_res['WRRF_flow'][t] > control_res['setpt_WRRF_flow']*no_control_res['max_flow_WRRF']:
                timeOverFlowSetpt += 1
                flowOverSetpt += (control_res['WRRF_flow'][t] - control_res['setpt_WRRF_flow']*no_control_res['max_flow_WRRF']) * routime_step
        elif objType == "TSS":
            if control_res['WRRF_TSSLoad'][t] > control_res['setpt_WRRF_TSS']*no_control_res['max_TSSLoad_WRRF']:
                timeOverTSSLSetpt += 1
                tssLOverSetpt += (control_res['WRRF_TSSLoad'][t] - control_res['setpt_WRRF_TSS']*no_control_res['max_TSSLoad_WRRF']) * routime_step
        elif objType == "both":
            if control_res['WRRF_flow'][t] > control_res['setpt_WRRF_flow']*no_control_res['max_flow_WRRF']:
                timeOverFlowSetpt += 1
                flowOverSetpt += (control_res['WRRF_flow'][t] - control_res['setpt_WRRF_flow']*no_control_res['max_flow_WRRF']) * routime_step
            if control_res['WRRF_TSSLoad'][t] > control_res['setpt_WRRF_TSS']*no_control_res['max_TSSLoad_WRRF']:
                timeOverTSSLSetpt += 1
                tssLOverSetpt += (control_res['WRRF_TSSLoad'][t] - control_res['setpt_WRRF_TSS']*no_control_res['max_TSSLoad_WRRF']) * routime_step
        tssLCumulative_control += control_res['WRRF_TSSLoad'][t] * routime_step
        if max(control_res['ustream_depths'][t]) == 1.0:
            timeFlooding += 1
        #CHANGE FlowVarArr[t-timeBegin] = (control_res['WRRF_flow'][t] - FlowBar_DW_C)**2
        FlowVarArr[t] = (control_res['WRRF_flow'][t] - FlowBar_DW_C)**2
        #CHANGE TSSVarArr[t-timeBegin] = (control_res['WRRF_TSSLoad'][t] - TSSBar_DW_C)**2
        TSSVarArr[t] = (control_res['WRRF_TSSLoad'][t] - TSSBar_DW_C)**2
    # Finish variance calculation of WRRF flow and TSS load by averaging
    # variance arrays
    FlowVar = np.average(FlowVarArr[DW_indices])
    TSSVar = np.average(TSSVarArr[DW_indices])
    # Calculate the TSS mass remaining in the sewer during the control simulation
    # during the course of the simulation; this assumes that no or negligible
    # TSS settled during the no control simulation as it only computes the
    # difference between no control and control
    tssLRemain = max(0,tssLCumulative_no_control - tssLCumulative_control)
    # The TSS mass remaining is normalized to the cumulative TSS mass for the
    # no control simulation
    tssLRemainPercent = tssLRemain/tssLCumulative_no_control
    '''
    plt.figure(1)
    plt.subplot(211)
    plt.plot(range(timeBegin,timeEnd),FlowVarArr[timeBegin:timeEnd],label='flow, all var')
    plt.plot(DW_indices,FlowVarArr[DW_indices],'.',label='flow, dw var')
    plt.legend()
    plt.subplot(212)
    #plt.plot(range(timeBegin,timeEnd),control_res['WRRF_flow'][timeBegin:timeEnd])
    plt.plot(range(timeBegin,timeEnd),TSSVarArr[timeBegin:timeEnd],label='TSS L, all var')
    plt.plot(DW_indices,TSSVarArr[DW_indices],'.',label='TSS L, dw var')
    plt.show()
    '''
    # Compile performance metrics in summary array for each control simulation
    summ[i-noRangeBegin,0] = control_res['weights']['beta']
    summ[i-noRangeBegin,1] = control_res['weights']['epsilon_flow']
    summ[i-noRangeBegin,2] = control_res['weights']['epsilon_TSS']
    summ[i-noRangeBegin,3] = control_res['setpt_WRRF_flow']
    summ[i-noRangeBegin,4] = control_res['setpt_WRRF_TSS']
    summ[i-noRangeBegin,5] = timeOverFlowSetpt
    summ[i-noRangeBegin,6] = timeOverTSSLSetpt
    summ[i-noRangeBegin,7] = flowOverSetpt
    summ[i-noRangeBegin,8] = tssLOverSetpt
    summ[i-noRangeBegin,9] = flowPeakRed
    summ[i-noRangeBegin,10] = tssLPeakRed
    summ[i-noRangeBegin,11] = tssLRemain
    summ[i-noRangeBegin,12] = tssLRemainPercent
    summ[i-noRangeBegin,13] = timeFlooding
    summ[i-noRangeBegin,14] = FlowVar
    summ[i-noRangeBegin,15] = TSSVar
    summ[i-noRangeBegin,16] = control_res['flooding']

    # Save summary array of performance metrics after each control simulation in
    # a compliation .csv file
    saveFileName = '../data/results/control/resultSumm_' + objType + '_' + storm + '_short.csv'
    np.savetxt(saveFileName, summ, delimiter=",")
    
    del control_res_load, control_res, timeOverFlowSetpt, timeOverTSSLSetpt
    del flowOverSetpt, tssLOverSetpt, tssLCumulative_control, timeFlooding
    del FlowVarArr, TSSVarArr, first, last, weekly_max_flow_C, weekly_max_TSS_C
    del flowPeakRed, tssLPeakRed, FlowVar, TSSVar, tssLRemain, tssLRemainPercent
