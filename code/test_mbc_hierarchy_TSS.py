from environment_mbc_wq import Env
from mbc_simulation import simulation_noControl, simulation_control
from plot_fn import plot_noControl, plot_control, plot_finish
from GDRSS_fn import GDRSS_build
import numpy as np
import pickle
import swmmAPI as swmm

# Enter 1 to include no control simulation and 0 otherwise
noControl = 1
# Enter 1 to include control simulation and 0 otherwise
control = 1

## Simulation parameters
# Enter ISDs to use for MBC; elements should be from {2,3,4}U{6,...,13}
ISDs = [11,6,2]
#ISDs = [13,12,11,10,9,8,7,6,4,3,2]
# Enter number of main trunkline branches
n_trunkline = 3
# Enter array with number of ISDs along each main trunkline branch, from most
# upstream branch to most downstream
n_ISDs = [1,1,1]

## Weighting parameters
# Enter weighting parameters:
    # beta: upstream flooding
weights = {'beta': 1.0,
    # epsilon_flow: downstream WRRF flow objective
    'epsilon_flow': 10.0,
    # epsilon_TSS: downstream WRRF TSS objective
    'epsilon_TSS': 1.0
    }

## Downstream setpoints
    # For setptThres, enter 1 to not exceed setpoint or 0 to achieve setpoint
ctrlParams = {'setptThres': 0,
    # For objType, enter 'flow', 'TSS', or 'both' for downstream objective type;
    # 'both' considers both objectives simulataneously, weighting based on
    # values for epsilon_flow and epsilon_TSS provided above
    'objType': 'flow',
    # For setpt_WRRF_flow and setpt_WRRF_TSS, enter downstram flow and TSS
    # setpoints, respectively, normalized to no control simulation results
    'setpt_WRRF_flow': 1.0,
    'setpt_WRRF_TSS': 0.8,
    # For contType, enter 'binary' for {0,1} gate openings or 'continuous' for [0,1]
    'contType': 'continuous'
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
inpF = "../data/input_files/GDRSS/GDRSS_SCT_simple_ISDs_TSS_inflows.inp"
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
sysSpecs['control_step'] = int(np.ceil(15.*60./sysSpecs['routime_step']))

# Creates environment for running simulation and getting/setting parameters
# and states
env = Env(inpF)
# Enter 1 if .inp file has wet weather; 0 otherwise;
# only influences max values set below if noControl == 0 for testing storm
wetWeather = 1
# Variables in maxes will be recalculated using no control simulation results
# if noControl == 1
if wetWeather == 1:
    # For max_flow_WRRF, enter no control simulation WRRF flow peak
    maxes = {'max_flow_WRRF': 712.509,
    # For max_flow_dstream, enter no control simulaiton flow peaks for each branch
    'max_flow_dstream': [349.693,190.156,279.428],
    # For max_TSSLoad_WRRF, enter no control simulation WRRF TSS load peak
    'max_TSSLoad_WRRF': 3.533,
    # For max_TSSLoad_dstream, enter no control simulation TSS load peaks for each branch
    'max_TSSLoad_dstream': [1.573,0.8788,1.762]
    }
else:
    maxes = {'max_flow_WRRF': 223.275,
    'max_flow_dstream': [93.7,49.75,75.22],
    'max_TSSLoad_WRRF': 2.3675,
    'max_TSSLoad_dstream': [0.8421,0.5240,1.0090]
    }

## Saving and plotting specifications
# Enter 1 to save results and 0 otherwise
save = 0
# Enter filename to save under if save == 1
saveNames = ['both_2018paper']
# For plot, enter 1 to plot results and 0 otherwise
plotParams = {'plot': 1,
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
    time, ustream_depths, dstream_flows, max_flow_dstream, dstream_TSSLoad, max_TSSLoad_dstream, WRRF_flow, max_flow_WRRF, WRRF_TSSLoad, max_TSSLoad_WRRF = simulation_noControl(env, n_trunkline, sysSpecs)

    maxes = {'max_flow_WRRF': max_flow_WRRF, 'max_flow_dstream': max_flow_dstream,
                'max_TSSLoad_WRRF': max_TSSLoad_WRRF, 'max_TSSLoad_dstream': max_TSSLoad_dstream}

    # Prints cumulative TSS load at WRRF
    print('Sum of WRRF_TSSLoad: ' + '%.2f' % sum(WRRF_TSSLoad))

    if plotParams['plot'] == 1:
        plot_noControl(n_trunkline, n_ISDs, plotParams, time, ustream_depths, WRRF_flow, WRRF_TSSLoad, dstream_flows, maxes)

    print("Done with no control")

    if save == 1:
        fileName = '../data/results/no_control/' + saveNames[0] + '.pkl'
        with open(fileName,'w') as f:
            pickle.dump([time,ustream_depths,WRRF_flow,WRRF_TSSLoad,dstream_flows,maxes['max_flow_WRRF'],maxes['max_TSSLoad_WRRF']],f)
        print('No control results saved')

if control == 1:
    # Runs simulation for MBC case
    time_state, time_control, ustream_depths, dstream_flows, WRRF_flow, WRRF_TSSLoad, price, demands, gates, setpts_all, ctrlParams = simulation_control(env, n_trunkline, n_ISDs, ctrlParams, sysSpecs, weights, orificeDict, maxes)

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
        fileName = '../data/results/control/' + saveNames[0] + '.pkl'
        if ctrlParams['objType'] == "both":
            with open(fileName,'w') as f:
                pickle.dump([time,ustream_depths,WRRF_flow,ctrlParams['setpt_WRRF_flow'],ctrlParams['setpt_WRRF_TSS'],maxes['max_flow_WRRF'],maxes['max_TSSLoad_WRRF'],WRRF_TSSLoad,dstream_flows,maxes['max_flow_dstream'],demands,price,gates],f)
        else:
            with open(fileName,'w') as f:
                pickle.dump([time,ustream_depths,WRRF_flow,ctrlParams['setpt_WRRF_flow'],ctrlParams['setpt_WRRF_TSS'],maxes['max_flow_WRRF'],maxes['max_TSSLoad_WRRF'],WRRF_TSSLoad,dstream_flows,setpts_all,maxes['max_flow_dstream'],demands,price,gates],f)
        print('Control results saved')

if plotParams['plot'] == 1:
    plot_finish(plotParams['normalize'])
