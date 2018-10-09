import pickle
import numpy as np

storm = '201701'
objType = 'TSS'
hierarchyOpt = 'NH'
ISD_arrangement = 'A'
noRangeBegin = 1
noRangeEnd = 5
timeBegin = 8640
timeEnd = 3153600 #259200
saveType = "numpy" # "numpy" or "pickle"
#saveFileType = '.svg'
routime_step = 10 # seconds

if saveType == "pickle":
    fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '.pkl'
elif saveType == "numpy":
    fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '.npy'

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

summ = np.zeros((noRangeEnd-noRangeBegin,16),float)

for i in range(noRangeBegin,noRangeEnd):
    print(i)
    if saveType == "pickle":
        fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '_' + "%02d" % (i) + '.pkl'
    elif saveType == "numpy":
        fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISD_arrangement + '_' + "%02d" % (i) + '.npy'

    n_trunkline = 3
    if ISD_arrangement == 'A':
        n_ISDs = [3,5,3]
    else:
        n_ISDs = [1,1,1]

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
                            'WRRF_flow': control_res_load.item().get('WRRF_flow'),
                            'setpt_WRRF_flow': control_res_load.item().get('setpt_WRRF_flow'),
                            'setpt_WRRF_TSS': control_res_load.item().get('setpt_WRRF_TSS'),
                            'max_flow_WRRF': control_res_load.item().get('max_flow_WRRF'),
                            'max_TSSLoad_WRRF': control_res_load.item().get('max_TSSLoad_WRRF'),
                            'WRRF_TSSLoad': control_res_load.item().get('WRRF_TSSLoad'),
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
                            'WRRF_flow': control_res_load.item().get('WRRF_flow'),
                            'setpt_WRRF_flow': control_res_load.item().get('setpt_WRRF_flow'),
                            'setpt_WRRF_TSS': control_res_load.item().get('setpt_WRRF_TSS'),
                            'max_flow_WRRF': control_res_load.item().get('max_flow_WRRF'),
                            'max_TSSLoad_WRRF': control_res_load.item().get('max_TSSLoad_WRRF'),
                            'WRRF_TSSLoad': control_res_load.item().get('WRRF_TSSLoad'),
                            'dstream_flows': control_res_load.item().get('dstream_flows'),
                            'setpts_all': control_res_load.item().get('setpts_all'),
                            'max_flow_dstream': control_res_load.item().get('max_flow_dstream'),
                            'demands': control_res_load.item().get('demands'),
                            'price': control_res_load.item().get('price'),
                            'gates': control_res_load.item().get('gates')
                            }

    # Setpoint adjustment
    control_res['setpt_WRRF_flow'] = 195.6/447.82*control_res['setpt_WRRF_flow']
    control_res['setpt_WRRF_TSS'] = 1.9177/4.8736*control_res['setpt_WRRF_TSS']

    timeOverFlowSetpt = 0
    timeOverTSSLSetpt = 0
    flowOverSetpt = 0
    tssLOverSetpt = 0
    tssLCumulative_no_control = 0
    tssLCumulative_control = 0
    timeFlooding = 0

    FlowBar = np.average(control_res['WRRF_flow'][timeBegin:timeEnd])
    TSSBar = np.average(control_res['WRRF_TSSLoad'][timeBegin:timeEnd])
    FlowVarArr = np.zeros(timeEnd-timeBegin)
    TSSVarArr = np.zeros(timeEnd-timeBegin)

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
    FlowVar = np.average(FlowVarArr)
    TSSVar = np.average(TSSVarArr)
    flowPeakRed = (no_control_res['max_flow_WRRF']-max(control_res['WRRF_flow'])) / no_control_res['max_flow_WRRF']
    tssLPeakRed = (no_control_res['max_TSSLoad_WRRF']-max(control_res['WRRF_TSSLoad'])) / no_control_res['max_TSSLoad_WRRF']
    tssLRemain = max(0,tssLCumulative_no_control - tssLCumulative_control)
    tssLRemainPercent = tssLRemain/tssLCumulative_no_control

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

    saveFileName = '../data/results/control/resultSumm_' + objType + '_' + storm + '.csv'
    np.savetxt(saveFileName, summ, delimiter=",")
