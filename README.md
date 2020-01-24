## Load-Balancing Control for Distributed Sewer Assets
### Balancing water quality and flows in combined sewer systems using real-time control
Sara C. Troutman

A new generation of smart and connected stormwater and sewer systems is being enabled by emerging wireless technologies and data algorithms. 
Stormwater and combined sewer systems can be autonomously controlled (gates, valves, pumps) to allocate storage and adapt to changing inputs. 
As a result, there is an opportunity to begin viewing the collection system as an extension of the Water Resource Recovery Facility (WRRF), whereby flows in the collection system are dynamically controlled to benefit downstream treatment. 
The dynamic control of collection system storage will allow peak flows to be minimized and solid loads to the plant to be tuned in response to real-time WRRF states as they relate to treatment operation and performance. 
To that end, this paper presents a formulation of a real-time load-balancing algorithm to control distributed storage assets in the collection system, with objectives of improving flow and water quality dynamics at inflow to a treatment plant. 
We illustrate that this load-balancing approach can successfully attenuate wet-weather peaks and minimize dry-weather oscillations. 
The parameterization of the control algorithm is assessed in the context of competing objectives at the downstream WRRF and broader collection system (e.g. sediment loads, peak flows, flooding, and solids accumulation in the sewer system). 
By applying this control algorithm and analysis to an established case study, we identify a range of parameter values that provide most desirable performance across a number of system-wide objectives. 
Specifically, we discover a band of desirable performance, which not only improves inflow into the WRRF, but simultaneously reduces flooding and sedimentation in the collection system. 

<img src="https://github.com/stroutm/LBCsewer/blob/master/images/LBCsummary.png" alt="LBCsummary" width="500"/>

To use this algorithm, the following will have to be specified beforehand:

| Item | Symbol | Description |
|-----------|:-----------:|-----------|
| A set of sewer assets | ![i\in I](https://latex.codecogs.com/gif.latex?i\in&space;I) | These can include e.g. storage basins with outlet valves and pump stations. |
| States (e.g., water level) | ![S_{i}](https://latex.codecogs.com/gif.latex?S_{i}) | This can be a vector of multiple states for each asset ![i](https://latex.codecogs.com/gif.latex?i). |
| Desired setpoints for each state | ![S_{i}^*](https://latex.codecogs.com/gif.latex?S_{i}^*) | Setpoints must be specified for each state in ![S_{i}](https://latex.codecogs.com/gif.latex?S_{i}). |
| System importance values for each asset ![i](https://latex.codecogs.com/gif.latex?i) | ![\alpha_{i}](https://latex.codecogs.com/gif.latex?\alpha_{i}) | This can be used to specify which assets and states are most important within the system. The size of ![\alpha_{i}](https://latex.codecogs.com/gif.latex?\alpha_{i}) must match ![S_{i}](https://latex.codecogs.com/gif.latex?S_{i}). |
| Instantaneous importance weight | ![\rho](https://latex.codecogs.com/gif.latex?\rho) | This parameter can be tuned to reflect how stressed an asset is at any given point in time. By analogy, ![\rho](https://latex.codecogs.com/gif.latex?\rho) could encapsulate the comfort level of an operator (e.g., release proportional to water level vs. prioritize an asset only if it is close to full). For example, if storage capacity is used as an indicator of importance, with ![\rho=1](https://latex.codecogs.com/gif.latex?\rho=1) the instantaneous importance of the asset increases nearly linearly with water level. With ![\rho=100](https://latex.codecogs.com/gif.latex?\rho=100) the asset would be considered important only if it is close to capacity. |
| A set of assets that are controllable by the operator / system | ![I_{C}](https://latex.codecogs.com/gif.latex?I_{C}) | This algorithm will inform control actions for these assets. |
| A set of assets that will remain uncontrolled or passively controlled | ![I_{U}](https://latex.codecogs.com/gif.latex?I_{U}) | An example of what this set might contain is the downstream WRRF with states pertaining to inflow conditions. |

Then for each time step ![t](https://latex.codecogs.com/gif.latex?t), the following are computed:

| Item | Symbol | Description |
|-----------|:-----------:|-----------|
| Instantaneous importance | ![\gamma_{i}](https://latex.codecogs.com/gif.latex?\gamma_{i}) | This is based on ![S_{i}](https://latex.codecogs.com/gif.latex?S_{i}) and ![\rho](https://latex.codecogs.com/gif.latex?\rho). In general, a higher state (e.g., water level) will result in a higher instantaneous importance. |
| Overall importance | ![\beta_{i}](https://latex.codecogs.com/gif.latex?\beta_{i}) | This is a product of the system importance and instantaneous importance of asset ![i](https://latex.codecogs.com/gif.latex?i). |
| Importance-weighted average | ![\bar{C}](https://latex.codecogs.com/gif.latex?\bar{C}) | This provides a basis for which to compare the relative stress of all assets in the system and is used to determined which assets release water during a particular time step. |
| A set of assets that will release water | ![J](https://latex.codecogs.com/gif.latex?J) | These assets must be controllable (![I_{C}](https://latex.codecogs.com/gif.latex?I_{C})) and have an importance-weighted deviation that is greater than the average: asset ![j](https://latex.codecogs.com/gif.latex?j) such that ![\beta_j(t)\cdot\left(S_j(t)-S_j^*(t)\right)>\bar{C}(t)](https://latex.codecogs.com/gif.latex?\beta_j(t)\cdot\left(S_j(t)-S_j^*(t)\right)>\bar{C}(t)). |
| Relative allotment factor for each asset that will release water | ![R_{j}](https://latex.codecogs.com/gif.latex?R_{j}) | This allotment factor simply assigns the fraction of a downstream asset’s capacity that will be allotted to an upstream asset ![j](https://latex.codecogs.com/gif.latex?j) and is defined as the importance-weighted deviation that is normalized within set ![J](https://latex.codecogs.com/gif.latex?J). |

The relative allotment factor can then be multiplied by available downstream capacity at each time step to determine how much to release from each upstream storage asset.

The algorithm below summarizes this procedure step by step.

<img src="https://github.com/stroutm/LBCsewer/blob/master/images/algorithm.PNG" alt="algorithm" width="350"/>
