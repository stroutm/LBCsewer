import matplotlib.pyplot as plt
import pickle
import numpy as np

fileNames = ['iter04.pkl','iter04_a.pkl','iter04_b.pkl']
# first should be no control; others should be control

colors = ['#00a650','#008bff','#ff4a00','#ffb502','#9200cc'] # colors for each upstream asset

for i in range(0,len(fileNames)-1):
    # No control
    with open('../data/results/no_control/'+fileNames[0]) as f:
        state_space, ustream_depths, dstream_flow = pickle.load(f)

    for a in range(0,len(state_space['depthsL'])):
        plt.figure(i+1)
        plt.subplot(321) # upstream depths
        plt.plot(ustream_depths[:,a],
            label = "No control",
            color = colors[a], linestyle = '--')

    plt.subplot(322) # downstream flows
    plt.plot(dstream_flow, label = "No control", color = colors[0])

    # Control
    with open('../data/results/control/'+fileNames[i+1]) as f:
        beta, epsilon, gamma, zeta, setptFlow, setptFlowDeriv, setptTSSload, repTot, contType, state_space, control_points, max_flow, ustream_depths, dstream_flow, demands, price, gates = pickle.load(f)

    for a in range(0,len(state_space['depthsL'])):
        plt.subplot(321)
        plt.plot(ustream_depths[:,a],
            label = "Market-based control, " + control_points[a],
            color = colors[a], linestyle = '-')

        plt.subplot(324)
        plt.plot(demands[:,a],
            label = "Demand, " + control_points[a],
            color = colors[a], linestyle = '-')

        plt.subplot(326)
        plt.plot(gates[:,a],
            label = "Dam down, " + control_points[a],
            color = colors[a], linestyle = '-')

    plt.subplot(321)
    plt.ylabel('Upstream Normalized Conduit Depth')
    plt.ylim(0,1)
    plt.legend()

    plt.subplot(322)
    plt.plot(dstream_flow, label = "Market-based control",
                color = colors[1], linestyle = '-')
    plt.plot(setptFlow*np.ones(len(dstream_flow)), label = "Setpoint",
                color = 'k')
    plt.ylabel('Downstream Normalized Flow')
    plt.legend()

    plt.subplot(324)
    plt.plot(price, label = "Price", color = 'k',
                linestyle = '-')
    plt.ylabel('Price and Demand')
    plt.legend()

    plt.subplot(326)
    plt.ylabel('Gate opening')
    plt.legend()

plt.show()
