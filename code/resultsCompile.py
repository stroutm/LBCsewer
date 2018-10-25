import pickle
import numpy as np

# Enter result file information
storm = '201806'
objType = 'both'
hierarchyOpt = 'NH'
ISD_arrangement = 'A'
# Trial number range
noRangeBegin = 1
noRangeEnd = 101
# Timestep range (note, 1 sample every 10 seconds)
timeBegin = 8640
if storm == '201701':
    timeEnd = 3153600
elif storm == '201806':
    timeEnd = 259200
saveType = "pickle" # "numpy" or "pickle"
routime_step = 10 # seconds

# Compiles file name for no control results file
if saveType == "pickle":
    fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '.pkl'
elif saveType == "numpy":
    fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '.npy'

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
                        'max_TSSLoad_WRRF': no_control_res_load.item().get('max_TSSLoad_WRRF')
                        }

# Initializes summary array for performance metrics
summ = np.zeros((noRangeEnd-noRangeBegin,16),float)

# Loops through each trial number
for i in range(noRangeBegin,noRangeEnd):
    print(i)
    # Compiles file name for each control results file
    if saveType == "pickle":
        fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '_' + "%02d" % (i) + '.pkl'
    elif saveType == "numpy":
        fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '_' + "%02d" % (i) + '.npy'

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
                            'gates': control_res_load.item().get('gates')
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
                            'gates': control_res_load.item().get('gates')
                            }

    # Adjusts setpoint to account for delay between upstream and downstream
    # Numbers based on simulations
    control_res['setpt_WRRF_flow'] = 195.6/447.82*control_res['setpt_WRRF_flow']
    control_res['setpt_WRRF_TSS'] = 1.9177/4.8736*control_res['setpt_WRRF_TSS']

    ## Initialize performance metrics, described below
    # Number of timesteps over flow setpoint
    timeOverFlowSetpt = 0
    # Number of timesteps over TSS load setpoint
    timeOverTSSLSetpt = 0
    # Cumulative volume over flow setpoint
    flowOverSetpt = 0
    # Cumulative TSS mass over TSS load setpoint
    tssLOverSetpt = 0
    # Cumulative TSS mass received by downstream WRRF for no control simulation
    tssLCumulative_no_control = 0
    # Cumulative TSS mass received by downstream WRRF for control simulation
    tssLCumulative_control = 0
    # Number of timesteps where at least one storage asset had a normalized
    # depth of 1.0 (full)
    timeFlooding = 0
    # Average flow at WRRF for control simulation
    FlowBar = np.average(control_res['WRRF_flow'][timeBegin:timeEnd])
    # Average TSS load at WRRF for control simulation
    TSSBar = np.average(control_res['WRRF_TSSLoad'][timeBegin:timeEnd])
    # Variance of flow at WRRF for control simulation
    FlowVarArr = np.zeros(timeEnd-timeBegin)
    # Variance of TSS load at WRRF for control simulation
    TSSVarArr = np.zeros(timeEnd-timeBegin)

    first = 0; last = 0
    # Maximum flow for no control simulation in week-long chunks
    weekly_max_flow_NC = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/24/60/60*10/7)))
    # Maximum flow for control simulation in week-long chunks
    weekly_max_flow_C = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/24/60/60*10/7)))
    # Maximum TSS load for no control simulation in week-long chunks
    weekly_max_TSS_NC = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/24/60/60*10/7)))
    # Maximum TSS load for control simulation in week-long chunks
    weekly_max_TSS_C = np.zeros(int(np.floor((float(timeEnd)-float(timeBegin))/24/60/60*10/7)))
    # WRRF flow peak reduction between no control and control simulation
    weekly_flow_peak_red = []
    # WRRF TSS load peak reduction between no control and control simulation
    weekly_TSS_peak_red = []
    # Loop through control simulation in week-long chucks
    for t in range(0,int(np.floor((float(timeEnd)-float(timeBegin))/24/60/60*10/7))):
        first = last
        last += 8640*7 # number of timesteps in a week
        weekly_max_flow_NC[t] = max(no_control_res['WRRF_flow'][first:last])
        weekly_max_flow_C[t] = max(control_res['WRRF_flow'][first:last])
        weekly_max_TSS_NC[t] = max(no_control_res['WRRF_TSSLoad'][first:last])
        weekly_max_TSS_C[t] = max(control_res['WRRF_TSSLoad'][first:last])
        # Only include no control peaks over 250 to ensure they are wet-weather
        # peaks and not including weeks with only dry weather
        if weekly_max_flow_NC[t] > 250.0:
            weekly_flow_peak_red = np.hstack((weekly_flow_peak_red,(weekly_max_flow_NC[t]-weekly_max_flow_C[t])/weekly_max_flow_NC[t]))
        # Only include no control peaks over 2.4 to ensure they are wet-weather
        # peaks and not including weeks with only dry weather
        if weekly_max_TSS_NC[t] > 2.4:
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
        tssLCumulative_no_control += no_control_res['WRRF_TSSLoad'][t] * routime_step
        tssLCumulative_control += control_res['WRRF_TSSLoad'][t] * routime_step
        if max(control_res['ustream_depths'][t]) == 1.0:
            timeFlooding += 1
        FlowVarArr[t-timeBegin] = (control_res['WRRF_flow'][t] - FlowBar)**2
        TSSVarArr[t-timeBegin] = (control_res['WRRF_TSSLoad'][t] - TSSBar)**2
    # Finish variance calculation of WRRF flow and TSS load by averaging
    # variance arrays
    FlowVar = np.average(FlowVarArr)
    TSSVar = np.average(TSSVarArr)
    # Calculate the TSS mass remaining in the sewer during the control simulation
    # during the course of the simulation; this assumes that no or negligible
    # TSS settled during the no control simulation as it only computes the
    # difference between no control and control
    tssLRemain = max(0,tssLCumulative_no_control - tssLCumulative_control)
    # The TSS mass remaining is normalized to the cumulative TSS mass for the
    # no control simulation
    tssLRemainPercent = tssLRemain/tssLCumulative_no_control

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

    # Save summary array of performance metrics after each control simulation in
    # a compliation .csv file
    saveFileName = '../data/results/control/resultSumm_' + objType + '_' + storm + '.csv'
    np.savetxt(saveFileName, summ, delimiter=",")
