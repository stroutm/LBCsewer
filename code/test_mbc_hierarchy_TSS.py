from environment_mbc_wq import Env
from mbc_fn import mbc, mbc_multi, mbc_noaction, mbc_noaction_multi, mbc_bin, perf
from mbc_simulation import simulation_noControl, simulation_control
from GDRSS_fn import GDRSS_build
import matplotlib.pyplot as plt
import numpy as np
import pickle
import copy
import swmmAPI as swmm

# Generate SWMM attributes dictionaries
headers = ['[TITLE]','[OPTIONS]','[EVAPORATION]','[RAINGAGES]','[SUBCATCHMENTS]',
    '[SUBAREAS]','[INFILTRATION]','[JUNCTIONS]','[OUTFALLS]','[STORAGE]',
    '[CONDUITS]','[PUMPS]','[ORIFICES]','[WEIRS]','[XSECTIONS]','[LOSSES]',
    '[CONTROLS]','[INFLOWS]','[DWF]','[HYDROGRAPHS]','[RDII]','[CURVES]',
    '[TIMESERIES]','[PATTERNS]','[REPORT]','[TAGS]','[MAP]','[COORDINATES]',
    '[VERTICES]','[Polygons]','[SYMBOLS]','[PROFILES]']
inpF = "../data/input_files/GDRSS/GDRSS_SCT_simple_ISDs_TSS_inflows.inp"
sections = swmm.make_sections(inpF,headers)
junctionDict = swmm.make_junction_dictionary(sections)
conduitDict = swmm.make_conduit_dictionary(sections)
orificeDict = swmm.make_orifice_dictionary(sections)

# Enter ISDs to use for MBC; elements should be from {2,3,4}U{6,...,13}
ISDs = [11,6,2]
#ISDs = [13,12,11,10,9,8,7,6,4,3,2]
# Enter number of main trunkline branches
n_trunkline = 3
# Enter array with number of ISDs along each main trunkline branch, from most
# upstream branch to most downstream
n_ISDs = [1,1,1]
# Based on ISDs, pulls states, parameters, and control points
control_points, colors, labels, ustreamConduits, branchConduits, WRRFConduit = GDRSS_build(ISDs)
uInvert = []
dInvert = []
orifice_diam_all = []
max_depths = []
for i in range(0,sum(n_ISDs)):
    uInvert = np.hstack((uInvert,junctionDict[orificeDict[control_points[i]]['from_node']]['elevation']))
    dInvert = np.hstack((dInvert,junctionDict[orificeDict[control_points[i]]['to_node']]['elevation']))
    orifice_diam_all = np.hstack((orifice_diam_all,orificeDict[control_points[i]]['geom1']))
    max_depths = np.hstack((max_depths,conduitDict[ustreamConduits[i]]['geom1']))

# Input file
env = Env(inpF)
# Enter 1 if .inp file has wet weather; 0 otherwise
wetWeather = 1

## Weighting parameters
# Enter upstream flooding weight
beta = 1.0
# Enter downstream objective weights based on objective type
epsilon_flow = 10.0
epsilon_TSS = 1.0

## Downstream setpoints
# Enter either "manual" to use setpts array establish below or "automatic" to
# determine the setpoints for each branch using MBC and setpt_WRRF
setptMethod = "automatic"
# Enter 1 to not exceed setpoint or 0 to achieve setpoint
setptThres = 0
# Enter branch setpoints if chose "manual" for setptMethod;
# list in same order as n_ISDs
setpts = [0.4,0.5,0.3]
# For objType enter "flow", "TSS", or "both" for downstream objective type;
# "both" considers both objectives simulataneously, weighting based on
# values for epsilon_flow and epsilon_TSS provided above;
# for setpt_WRRF enter setpoint to be used if chose "automatic" for setptMethod;
# if objType == "both", enter both setpt_WRRF_flow and setpt_WRRF_TSS values
objType = "both"
setpt_WRRF_flow = 0.8; setpt_WRRF_TSS = 0.8
# Enter "binary" for {0,1} gate openings or "continuous" for [0,1]
contType = "continuous"
# Enter 1 to include no control simulation and 0 otherwise
noControl = 0
# Enter 1 to include control simulation and 0 otherwise
control = 1

## Saving and plotting specifications
# Enter 1 to save results and 0 otherwise
save = 0
# Enter filename to save under if save == 1
saveNames = ['both_2018paper']
# Enter 1 to plot results and 0 otherwise
plot = 1
# Enter 1 to normalize downstream flows in plots and 0 otherwise
normalize = 0

# Enter "english" for English units in .inp file and "metric" otherwise
units = "english"
# Enter "rectangular" for rectangular orifices; otherwise is not developed yet
shapes = "rectangular"
if wetWeather == 1:
    # Enter the max flow for normalization of the WRRF flow;
    # if noControl == 1, this will be recalculated using no control flow peak
    max_flow_WRRF = 712.509
    # Enter the max flow for each branch (recalculated if noControl == 1)
    max_flow_dstream = [349.693,190.156,279.428]
    # Enter the max TSS load for WRRF (recalculated if noControl == 1)
    max_TSSLoad_WRRF = 3.533
    # Enter the max TSS load for each (recalculated if noControl == 1)
    max_TSSLoad_dstream = [1.573,0.8788,1.762]
else:
    # Enter the max flow for normalization of the WRRF flow;
    # if noControl == 1, this will be recalculated using no control flow peak
    max_flow_WRRF = 223.275
    # Enter the max flow for each branch (recalculated if noControl == 1)
    max_flow_dstream = [93.7,49.75,75.22]
    # Enter the max TSS load for WRRF (recalculated if noControl == 1)
    max_TSSLoad_WRRF = 2.3675
    # Enter the max TSS load for each (recalculated if noControl == 1)
    max_TSSLoad_dstream = [0.8421,0.5240,1.0090]
# Enter the routing timestep in seconds
routime_step = 10
# Enter number of steps between control actions
# (x min) * (60s/min) * (timestep/10s)
#control_step = 8640 # one action per day (only for visualization)
control_step = int(np.ceil(15.*60./routime_step))
# Enter the discharge coefficient of orifices
discharge = 0.61

## No control simulation
if noControl == 1:
    time, ustream_depths, dstream_flows, max_flow_dstream, dstream_TSSLoad, max_TSSLoad_dstream, WRRF_flow, max_flow_WRRF, WRRF_TSSLoad, max_TSSLoad_WRRF = simulation_noControl(env, n_trunkline, max_depths, ustreamConduits, branchConduits, WRRFConduit)

    print('Sum of WRRF_TSSLoad: ' + '%.2f' % sum(WRRF_TSSLoad))

    if plot == 1:
        plt.subplot(321)
        for a in range(0,sum(n_ISDs)):
            plt.plot(time,ustream_depths[:,a],
                        label = "No control, " + labels[a],
                        color = colors[a], linestyle = ':')

        plt.subplot(322)
        if normalize == 1:
            plt.plot(time,WRRF_flow/max_flow_WRRF, label = "No control, WRRF flow",
                    color = colors[-1], linestyle = ':')
        else:
            plt.plot(time,WRRF_flow, label = "No control, WRRF flow",
                    color = colors[-1], linestyle = ':')

        plt.subplot(323)
        if normalize == 1:
            plt.plot(time,WRRF_TSSLoad/max_TSSLoad_WRRF, label = "No control, WRRF TSS Load",
                    color = colors[-1], linestyle = ':')
        else:
            plt.plot(time,WRRF_TSSLoad, label = "No control, WRRF TSS Load",
                    color = colors[-1], linestyle = ':')

        plt.subplot(324)
        for a in range(0,n_trunkline):
            plt.plot(time,dstream_flows[:,a],
                        label = "No control, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = ':')

    print("Done with no control")

    if save == 1:
        fileName = '../data/results/no_control/' + saveNames[0] + '.pkl'
        with open(fileName,'w') as f:
            pickle.dump([time,ustream_depths,WRRF_flow,WRRF_TSSLoad,dstream_flows,max_flow_WRRF,max_TSSLoad_WRRF],f)
        print('No control results saved')

if control == 1:
    time_state, time_control, ustream_depths, dstream_flows, WRRF_flow, WRRF_TSSLoad, price, demands, gates, setpts_all, setpt_WRRF_flow, setpt_WRRF_TSS = simulation_control(env, control_points, n_trunkline, n_ISDs, control_step, setptMethod, setptThres, contType, objType, units, shapes, discharge, uInvert, dInvert, beta, epsilon_flow, epsilon_TSS, setpt_WRRF_flow, setpt_WRRF_TSS, orificeDict, orifice_diam_all, max_depths, ustreamConduits, branchConduits, WRRFConduit, max_flow_dstream, max_TSSLoad_dstream, max_flow_WRRF, max_TSSLoad_WRRF)

    print('Sum of WRRF_TSSLoad: ' + '%.2f' % sum(WRRF_TSSLoad))

    if plot == 1:
        for a in range(0,sum(n_ISDs)):
            plt.subplot(321)
            plt.plot(time_state,ustream_depths[:,a],
                        label = "MBC, " + labels[a],
                        color = colors[a], linestyle = '-')

            plt.subplot(325)
            plt.plot(time_state,gates[:,a],
                        label = "Dam down, " + labels[a],
                        color = colors[a], linestyle = '-')

            plt.subplot(326)
            plt.plot(time_control,demands[:,a],
                        label = "Demand, " + labels[a],
                        color = colors[a-n_trunkline-1], linestyle = '-')

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

            plt.subplot(326)
            plt.plot(time_control,price[:,a],
                        label = "price, " + labels[a-n_trunkline],
                        color = colors[a-n_trunkline-1], linestyle = '--')

    if objType == "flow":
        print("Done with MBC, Objective: " + objType + ", Setpoint: " + str(setpt_WRRF_flow))
    elif objType == "TSS":
        print("Done with MBC, Objective: " + objType + ", Setpoint: " + str(setpt_WRRF_TSS))
    elif objType == "both":
        print("Done with MBC, Objective: " + objType + ", Flow setpoint: " + str(setpt_WRRF_flow) + ", TSS setpoint: " + str(setpt_WRRF_TSS))

    if save == 1:
        fileName = '../data/results/control/' + saveNames[0] + '.pkl'
        if objType == "both":
            with open(fileName,'w') as f:
                pickle.dump([time,ustream_depths,WRRF_flow,setpt_WRRF_flow,setpt_WRRF_TSS,max_flow_WRRF,max_TSSLoad_WRRF,WRRF_TSSLoad,dstream_flows,max_flow_dstream,demands,price,gates],f)
        else:
            with open(fileName,'w') as f:
                pickle.dump([time,ustream_depths,WRRF_flow,setpt_WRRF_flow,setpt_WRRF_TSS,max_flow_WRRF,max_TSSLoad_WRRF,WRRF_TSSLoad,dstream_flows,setpts_all,max_flow_dstream,demands,price,gates],f)
        print('Control results saved')

if plot == 1:
    plt.subplot(321)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    #plt.legend()

    plt.subplot(322)
    if normalize == 1:
        plt.ylim(0,1)
    #else:
    #    plt.ylim(0,600)
    plt.ylabel('WRRF Flow ($\mathregular{ft^3/s}$)')
    #plt.legend()

    plt.subplot(323)
    plt.ylabel('WRRF TSS Load ($\mathregular{lb/s}$)')
    #plt.legend()

    plt.subplot(324)
    plt.ylabel('Branch Flows ($\mathregular{ft^3/s}$)')
    if normalize == 1:
        plt.ylim(0,1)
    #else:
    #    plt.ylim(0,300)
    #plt.legend()

    plt.subplot(325)
    plt.ylabel('Gate Opening')
    plt.ylim(0,1)
    #plt.legend()

    plt.subplot(326)
    plt.ylabel('Price and Demands')
    #plt.legend()

    plt.show()
