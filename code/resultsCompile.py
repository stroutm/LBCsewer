import pickle
import numpy as np

objType = 'flow'
storm = '20170504'
ISDscen = 'A'
routime_step = 10 # seconds

fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISDscen + '.pkl'

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

n = 10
summ = np.zeros((n,11),float)

for i in range(1,n+1):
    fileName = 'trial_' + objType + '_' + storm + '_NH_' + ISDscen + '_' + "%02d" % (i+30) + '.pkl'

    n_trunkline = 3
    if ISDscen == 'all':
        n_ISDs = [3,5,3]
    elif ISDscen == 'some':
        n_ISDs = [1,1,1]

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

    timeOverFlowSetpt = 0
    timeOverTSSLSetpt = 0
    flowOverSetpt = 0
    tssLOverSetpt = 0
    tssLCumulative_no_control = 0
    tssLCumulative_control = 0
    timeFlooding = 0

    for t in range(0,len(no_control_res['time'])):
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
    flowPeakRed = (no_control_res['max_flow_WRRF']-max(control_res['WRRF_flow'])) / no_control_res['max_flow_WRRF']
    tssLPeakRed = (no_control_res['max_TSSLoad_WRRF']-max(control_res['WRRF_TSSLoad'])) / no_control_res['max_TSSLoad_WRRF']
    tssLRemain = max(0,tssLCumulative_no_control - tssLCumulative_control)
    tssLRemainPercent = tssLRemain/tssLCumulative_no_control

    summ[i-1,0] = weights['epsilon_flow']/weights['beta']
    summ[i-1,1] = setpt_WRRF_flow
    summ[i-1,2] = timeOverFlowSetpt
    summ[i-1,3] = timeOverTSSLSetpt
    summ[i-1,4] = flowOverSetpt
    summ[i-1,5] = tssLOverSetpt
    summ[i-1,6] = flowPeakRed
    summ[i-1,7] = tssLPeakRed
    summ[i-1,8] = tssLRemain
    summ[i-1,9] = tssLRemainPercent
    summ[i-1,10] = timeFlooding

np.savetxt("foo.csv", summ, delimiter=",")
