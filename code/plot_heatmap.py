import pickle
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from plot_fn import plot_noControl, plot_control, plot_finish
from GDRSS_fn import GDRSS_build
import scipy.io as sio

dataLoad = sio.loadmat('../data/results/control/resultsSumm_201806.mat')
eps_flow = dataLoad['eps_flow'][0]
eps_tss = dataLoad['eps_tss'][0]
flow_var = dataLoad['flow_var']
tss_var = dataLoad['tss_var']
flow_peak = dataLoad['flow_peak']
tss_peak = dataLoad['tss_peak']
flow_peak_red = dataLoad['flow_peak_red']
tss_peak_red = dataLoad['tss_peak_red']
tss_load_remaining = dataLoad['tss_load_remaining']
timeFlood = dataLoad['timeFlood']

#fig1, ax1 = plt.subplots()
#im1 = ax1.imshow(flow_var)

#ax1.set_xticks(np.arange(len(eps_flow))); ax1.set_yticks(np.arange(len(eps_tss)))
#ax1.set_xticklabels(eps_flow); ax1.set_yticklabels(eps_tss)
#ax1.set_xlabel('eps_flow'); ax1.set_ylabel('eps_tss')

#ax1.set_title("Flow Variance")
#fig1.tight_layout()

def heatmap(data, row_labels, col_labels, xLabel, yLabel, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Arguments:
        data       : A 2D numpy array of shape (N,M)
        row_labels : A list or array of length N with the labels
                     for the rows
        col_labels : A list or array of length M with the labels
                     for the columns
    Optional arguments:
        ax         : A matplotlib.axes.Axes instance to which the heatmap
                     is plotted. If not provided, use current axes or
                     create a new one.
        cbar_kw    : A dictionary with arguments to
                     :meth:`matplotlib.Figure.colorbar`.
        cbarlabel  : The label for the colorbar
    All other arguments are directly passed on to the imshow call.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    #cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
    ax.set_title(cbarlabel)

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)

    # Let the horizontal axes labeling appear on top.
    #ax.tick_params(top=True, bottom=False,
    #               labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    #plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
    #         rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar

cmaps = ["viridis","magma","inferno","YlGnBu_r"]
cmapsNo = 2
fig1, ax1 = plt.subplots()
im1, cbar1 = heatmap(flow_var, eps_tss, eps_flow, "eps_flow", "eps_TSS", ax=ax1,
                   cmap=cmaps[cmapsNo], cbarlabel="Flow Variance")
fig2, ax2 = plt.subplots()
im2, cbar2 = heatmap(tss_var, eps_tss, eps_flow, "eps_flow", "eps_TSS", ax=ax2,
                   cmap=cmaps[cmapsNo], cbarlabel="TSS Variance")
fig3, ax3 = plt.subplots()
im3, cbar3 = heatmap(flow_peak, eps_tss, eps_flow, "eps_flow", "eps_TSS", ax=ax3,
                   cmap=cmaps[cmapsNo], cbarlabel="Control/No Control Flow Peak")
fig4, ax4 = plt.subplots()
im4, cbar4 = heatmap(tss_peak, eps_tss, eps_flow, "eps_flow", "eps_TSS", ax=ax4,
                   cmap=cmaps[cmapsNo], cbarlabel="Control/No Control TSS Load Peak")
fig5, ax5 = plt.subplots()
im5, cbar5 = heatmap(tss_load_remaining, eps_tss, eps_flow, "eps_flow", "eps_TSS", ax=ax5,
                   cmap=cmaps[cmapsNo], cbarlabel="Percent of TSS Load Remaining in Sewer")
fig6, ax6 = plt.subplots()
im6, cbar6 = heatmap(timeFlood, eps_tss, eps_flow, "eps_flow", "eps_TSS", ax=ax6,
                   cmap=cmaps[cmapsNo], cbarlabel="Timesteps where a Storage is Full")

fig1.tight_layout()
fig2.tight_layout()
fig3.tight_layout()
fig4.tight_layout()
fig5.tight_layout()
fig6.tight_layout()
plt.show()
