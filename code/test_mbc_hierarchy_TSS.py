from environment_mbc_wq import Env
from mbc_simulation import simulation_noControl, simulation_control
from plot_fn import plot_noControl, plot_control, plot_finish
from GDRSS_fn import GDRSS_build
import numpy as np
import pickle
import matplotlib.pyplot as plt
import swmmAPI as swmm

# Enter 1 to include no control simulation and 0 otherwise
noControl = 0
# Enter 1 to include control simulation and 0 otherwise
control = 1

## Simulation parameters
# Enter ISDs to use for MBC; elements should be from {2,3,4}U{6,...,13}
ISDs = [13,12,11,10,9,8,7,6,4,3,2]; n_ISDs = [3,5,3]
# Enter number of main trunkline branches
n_trunkline = 3

## Weighting parameters
# Enter weighting parameters:
    # beta: upstream flooding
weights = {'beta': 1.0,
    # epsilon_flow: downstream WRRF flow objective
    'epsilon_flow': 1.0,
    # epsilon_TSS: downstream WRRF TSS objective
    'epsilon_TSS': 0.0
    }
eps_flows = [5.]#[1.,2.5,5.,7.5,10.,12.5,15.,17.5,20.]
eps_TSS = [5.]#[1.,2.5,5.,7.5,10.,12.5,15.,17.5,20.]
saveNames = ['trial2_TSS_201701_NH_A_flood_short']
saveNames = ['test_both_final_N100']
saveType = "numpy" # or "pickle"
# Counter for saving results (starts at counter+1)
counter = 0

## Downstream setpoints
    # For setptThres, enter 1 to not exceed setpoint or 0 to achieve setpoint
ctrlParams = {'setptThres': 1,
    # For objType, enter 'flow', 'TSS', or 'both' for downstream objective type;
    # 'both' considers both objectives simulataneously, weighting based on
    # values for epsilon_flow and epsilon_TSS provided above
    'objType': 'both',
    # For setpt_WRRF_flow and setpt_WRRF_TSS, enter downstram flow and TSS
    # setpoints, respectively, normalized to no control simulation results
    'setpt_WRRF_flow': 2.5,
    'setpt_WRRF_TSS': 2.5,
    # For contType, enter 'binary' for {0,1} gate openings or 'continuous' for [0,1]
    'contType': 'continuous',
    # For hierarchy, enter 1 to have separate markets in each branch or 0 to
    # have all control points in the same market
    'hierarchy': 0
    }

## Generate SWMM attributes dictionaries
# List used to find all SWMM attribute types
headers = ['[TITLE]','[OPTIONS]','[EVAPORATION]','[RAINGAGES]','[SUBCATCHMENTS]',
    '[SUBAREAS]','[INFILTRATION]','[JUNCTIONS]','[OUTFALLS]','[STORAGE]',
    '[CONDUITS]','[PUMPS]','[ORIFICES]','[WEIRS]','[XSECTIONS]','[LOSSES]',
    '[CONTROLS]','[INFLOWS]','[DWF]','[HYDROGRAPHS]','[RDII]','[CURVES]',
    '[TIMESERIES]','[PATTERNS]','[REPORT]','[TAGS]','[MAP]','[COORDINATES]',
    '[VERTICES]','[Polygons]','[SYMBOLS]','[PROFILES]']
# Enter .inp file name and location
inpF = "../data/input_files/GDRSS/GDRSS_SCT_simple_ISDs_TSS_inflows_201701_timesteps.inp"
timesteps = 365*24*60*60/10 #62*24*60*60/10
# Sections and dictionaries generated for SWMM attributes;
# used for pulling parameters and states
sections = swmm.make_sections(inpF,headers)
junctionDict = swmm.make_junction_dictionary(sections)
conduitDict = swmm.make_conduit_dictionary(sections)
orificeDict = swmm.make_orifice_dictionary(sections)

# Based on ISDs, pulls states, parameters, and control points
control_points, colors, labels, ustreamConduits, branchConduits, WRRFConduit = GDRSS_build(ISDs)
# Compiles useful .inp file parameters, including:
# invert elevation of node upstream of ISDs (for calculating gate openings)
uInvert = []
# invert elevation of node downstream of ISDs (for calculating gate openings)
dInvert = []
# ISD orifice diameters (for calculating gate openings)
orifice_diam_all = []
# conduit diameters/heights for conduits upstream of ISDs (for normalizing
# water depths)
max_depths = []
for i in range(0,sum(n_ISDs)):
    uInvert = np.hstack((uInvert,junctionDict[orificeDict[control_points[i]]['from_node']]['elevation']))
    dInvert = np.hstack((dInvert,junctionDict[orificeDict[control_points[i]]['to_node']]['elevation']))
    orifice_diam_all = np.hstack((orifice_diam_all,orificeDict[control_points[i]]['geom1']))
    max_depths = np.hstack((max_depths,conduitDict[ustreamConduits[i]]['geom1']))

## System specifications
sysSpecs = {'uInvert': uInvert,
    'dInvert': dInvert,
    'orifice_diam_all': orifice_diam_all,
    'max_depths': max_depths,
    # For units, enter 'english' for English units in .inp file and 'metric' otherwise
    'units': 'english',
    # For shapes, enter 'rectangular' for rectangular orifices;
    # otherwise, not yet developed
    'shapes': 'rectangular',
    # For routime_step, enter routing timestep in seconds
    'routime_step': 10,
    # For discharge, enter the discharge coefficient of the orifices
    'discharge': 0.61,
    'control_points': control_points,
    'ustreamConduits': ustreamConduits,
    'branchConduits': branchConduits,
    'WRRFConduit': WRRFConduit
    }
# For control_step, enter number of steps between control actions
# (x min) * (60s/min) * (timestep / routime_step)
sysSpecs['control_step'] = 15*60/sysSpecs['routime_step']

# Creates environment for running simulation and getting/setting parameters
# and states
env = Env(inpF)

# Variables in maxes will be calculated using no control simulation results
# if noControl == 1
maxes = {'max_flow_WRRF': 0.,
    'max_flow_dstream': [0., 0., 0.],
    'max_TSSLoad_WRRF': 0.,
    'max_TSSLoad_dstream': [0., 0., 0.]
    }

## Saving and plotting specifications
# Enter 1 to save results and 0 otherwise
save = 1
# Enter filename to save under if save == 1

# For plot, enter 1 to plot results and 0 otherwise
plotParams = {'plot': 0,
    # For colors, provide array of hex colors for each ISD
    'colors': colors,
    # For labels, provide array of strings for each ISD
    'labels': labels,
    # Enter 1 to normalize downstream flows in plots and 0 otherwise
    'normalize': 0
    }

## No control simulation
if noControl == 1:
    # Runs simulation for no control case
    time, ustream_depths, dstream_flows, max_flow_dstream, dstream_TSSLoad, max_TSSLoad_dstream, WRRF_flow, max_flow_WRRF, WRRF_TSSLoad, max_TSSLoad_WRRF, stats = simulation_noControl(env, n_trunkline, sysSpecs, timesteps)

    maxes['max_flow_dstream'] = max_flow_dstream
    maxes['max_TSSLoad_dstream'] = max_TSSLoad_dstream
    maxes['max_flow_WRRF'] = max_flow_WRRF
    maxes['max_TSSLoad_WRRF'] = max_TSSLoad_WRRF

    # Prints cumulative TSS load at WRRF
    print('Sum of WRRF_TSSLoad: ' + '%.2f' % sum(WRRF_TSSLoad))

    if plotParams['plot'] == 1:
        plot_noControl(n_trunkline, n_ISDs, plotParams, time, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes)

    print("Done with no control")

    if save == 1:
        if saveType == "pickle":
            fileName = '../data/results/no_control/' + saveNames[0] + '.pkl'
            with open(fileName,'w') as f:
                pickle.dump([time,ustream_depths,WRRF_flow,WRRF_TSSLoad,dstream_flows,maxes['max_flow_WRRF'],maxes['max_TSSLoad_WRRF']],f)
        elif saveType == "numpy":
            fileName = '../data/results/no_control/' + saveNames[0] + '.npy'
            dict = {'time':time, 'ustream_depths':ustream_depths, 'WRRF_flow':WRRF_flow, 'WRRF_TSSLoad':WRRF_TSSLoad, 'dstream_flows':dstream_flows, 'max_flow_WRRF':maxes['max_flow_WRRF'], 'max_TSSLoad_WRRF':maxes['max_TSSLoad_WRRF'], 'stats':stats}
            np.save(fileName,dict)
        print('No control results saved')
        del dict

maxes['max_flow_WRRF'] = 222.3
maxes['max_TSSLoad_WRRF'] = 2.3165

if control == 1:
    for q in range(0,len(eps_flows)):
        weights['epsilon_flow'] = eps_flows[q]
        for r in range(0,len(eps_TSS)):
            weights['epsilon_TSS'] = eps_TSS[r]

            counter += 1

            # Runs simulation for MBC case
            time_state, time_control, ustream_depths, dstream_flows, WRRF_flow, WRRF_TSSLoad, price, demands, gates, setpts_all, ctrlParams, stats = simulation_control(env, n_trunkline, n_ISDs, ctrlParams, sysSpecs, weights, orificeDict, maxes, timesteps)

            # Prints cumulative TSS load at WRRF
            print('Sum of WRRF_TSSLoad: ' + '%.2f' % sum(WRRF_TSSLoad))

            if plotParams['plot'] == 1:
                plot_control(n_trunkline, n_ISDs, ctrlParams, plotParams, time_state, time_control, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes, setpts_all, price, demands, gates)

            if ctrlParams['objType'] == "flow":
                print("Done with MBC, Objective: " + ctrlParams['objType'] + ", Setpoint: " + str(ctrlParams['setpt_WRRF_flow']))
            elif ctrlParams['objType'] == "TSS":
                print("Done with MBC, Objective: " + ctrlParams['objType'] + ", Setpoint: " + str(ctrlParams['setpt_WRRF_TSS']))
            elif ctrlParams['objType'] == "both":
                print("Done with MBC, Objective: " + ctrlParams['objType'] + ", Flow setpoint: " + str(ctrlParams['setpt_WRRF_flow']) + ", TSS setpoint: " + str(ctrlParams['setpt_WRRF_TSS']))

            if save == 1:
                if saveType == "pickle":
                    fileName = '../data/results/control/' + saveNames[0] + '_' + '%02d' % (counter) + '.pkl'
                    if ctrlParams['objType'] == "both":
                        with open(fileName,'w') as f:
                            pickle.dump([ISDs,weights,time_state,time_control,ustream_depths,WRRF_flow,ctrlParams['setpt_WRRF_flow'],ctrlParams['setpt_WRRF_TSS'],maxes['max_flow_WRRF'],maxes['max_TSSLoad_WRRF'],WRRF_TSSLoad,dstream_flows,maxes['max_flow_dstream'],demands,price,gates],f)
                    else:
                        with open(fileName,'w') as f:
                            pickle.dump([ISDs,weights,time_state,time_control,ustream_depths,WRRF_flow,ctrlParams['setpt_WRRF_flow'],ctrlParams['setpt_WRRF_TSS'],maxes['max_flow_WRRF'],maxes['max_TSSLoad_WRRF'],WRRF_TSSLoad,dstream_flows,setpts_all,maxes['max_flow_dstream'],demands,price,gates],f)
                elif saveType == "numpy":
                    fileName = '../data/results/control/' + saveNames[0] + '_' + '%02d' % (counter) + '.npy'
                    if ctrlParams['objType'] == "both":
                        dict = {'ISDs':ISDs, 'weights':weights, 'time_state':time_state, 'time_control':time_control, 'ustream_depths':ustream_depths, 'WRRF_flow':WRRF_flow, 'setpt_WRRF_flow':ctrlParams['setpt_WRRF_flow'], 'setpt_WRRF_TSS':ctrlParams['setpt_WRRF_TSS'], 'max_flow_WRRF':maxes['max_flow_WRRF'], 'max_TSSLoad_WRRF':maxes['max_TSSLoad_WRRF'], 'WRRF_TSSLoad':WRRF_TSSLoad, 'dstream_flows':dstream_flows, 'max_flow_dstream':maxes['max_flow_dstream'], 'demands':demands, 'price':price, 'gates':gates, 'stats':stats}
                        np.save(fileName,dict)
                    else:
                        dict = {'ISDs':ISDs, 'weights':weights, 'time_state':time_state, 'time_control':time_control, 'ustream_depths':ustream_depths, 'WRRF_flow':WRRF_flow, 'setpt_WRRF_flow':ctrlParams['setpt_WRRF_flow'], 'setpt_WRRF_TSS':ctrlParams['setpt_WRRF_TSS'], 'max_flow_WRRF':maxes['max_flow_WRRF'], 'max_TSSLoad_WRRF':maxes['max_TSSLoad_WRRF'], 'WRRF_TSSLoad':WRRF_TSSLoad, 'dstream_flows':dstream_flows, 'setpts_all':setpts_all, 'max_flow_dstream':maxes['max_flow_dstream'], 'demands':demands, 'price':price, 'gates':gates, 'stats':stats}
                        np.save(fileName,dict)
                print('Control results saved')
                del dict

if plotParams['plot'] == 1:
    plot_finish(plotParams['normalize'])
    plt.show()
