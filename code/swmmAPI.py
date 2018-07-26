import math
import pandas as pd
from collections import OrderedDict
from pyswmm import Simulation

# Originally from https://github.com/gregjewi/MBC-env; copied 7/26/2018

def make_sections(inpF,headers):
    with open(inpF) as f:
        contents = f.read()

    sections = {}
    for header in headers:
        sections[header] = contents.find(header)

    sort = sorted(sections.items(), key=lambda x: x[1])

    for i in range(0,len(sort)):
        if i < len(sort)-1:
            a = [sort[i][1],sort[i+1][1]]
        else:
            a = [sort[i][1],len(contents)]

        section_content = contents[a[0]:a[1]]
        h = section_content.split('\n')[0]

        sections[h] = []

        for l in section_content.split('\n'):
            if not l:
                pass
            elif l[0].isalnum():
                sections[h].append(l)
            else:
                pass

    return sections

def prep_dicts(sections):
    conduitDict = make_conduit_dictionary(sections)
    junctionDict = make_junction_dictionary(sections)
    storageDict = make_storage_dictionary(sections)
    subcatchmentDict = make_subcatchment_dictionary(sections)
    outfallDict = make_outfall_dictionary(sections)
    orificeDict = make_orifice_dictionary(sections)
    curvesDict = make_curves_dictionary(sections)
    pumpDict = make_pump_dictionary(sections,curvesDict)
    optionsDict = make_options_dictionary(sections)

    calc_slope(conduitDict,junctionDict,storageDict,0)
    calc_qfull(conduitDict)

    offset = 479.755 # from '29 to Detroit Datum
    datum_conversion(junctionDict,offset)
    datum_conversion(storageDict,offset)
    datum_conversion(outfallDict,offset)

    return conduitDict,junctionDict,storageDict,subcatchmentDict,outfallDict,orificeDict,curvesDict,pumpDict,optionsDict

def make_conduit_dictionary(sections):
    conduitDict = {}
    for l in sections['[CONDUITS]']:
        a = l.split()

        conduitDict[a[0]] = {
            'from_node': a[1],
            'to_node': a[2],
            'length': float(a[3]),
            'roughness': float(a[4]),
            'in_offset': float(a[5]),
            'out_offset': float(a[6]),
            'init_flow': float(a[7]),
            'max_flow': float(a[8]),
        }

    for l in sections['[XSECTIONS]']:
        a = l.split()

        try:
            conduitDict[a[0]]['shape'] = a[1]
            conduitDict[a[0]]['geom1'] = float(a[2])
            conduitDict[a[0]]['geom2'] = float(a[3])
            conduitDict[a[0]]['geom3'] = float(a[4])
            conduitDict[a[0]]['geom4'] = float(a[5])
            conduitDict[a[0]]['barrels'] = int(a[6])
            conduitDict[a[0]]['culvert'] = float(a[7])
        except:
            pass

    return conduitDict

def make_junction_dictionary(sections):
    junctionDict = {}

    for l in sections['[JUNCTIONS]']:
        a = l.split()

        junctionDict[a[0]] = {
            'elevation': float(a[1]),
            'max_depth': float(a[2]),
            'init_depth': float(a[3]),
            'sur_depth': float(a[4]),
            'a_ponded': float(a[5])
        }

    return junctionDict

def make_storage_dictionary(sections):
    storageDict = {}

    for l in sections['[STORAGE]']:
        a = l.split()

        storageDict[a[0]] = {
            'elevation':float(a[1]),
            'max_depth':float(a[2]),
            'init_depth:':float(a[3]),
            'shape':a[4],
            #Curve Name/Params
            #N/A
            #Fevap
            #PSI
            #Ksat
            #IMD
        }

        if a[4] == 'FUNCTIONAL':
            storageDict[a[0]]['A'] = float(a[5])
            storageDict[a[0]]['B'] = float(a[6])
            storageDict[a[0]]['C'] = float(a[7])

    storageDict = calc_storage_vol(storageDict)

    return storageDict

def calc_storage_vol(storageDict):
    for element in storageDict:
        if storageDict[element]['shape'] == 'FUNCTIONAL':
            storageDict[element]['total_storage'] = ( storageDict[element]['A'] * storageDict[element]['max_depth']**(storageDict[element]['B'] + 1) / ( storageDict[element]['B'] + 1 ) ) + ( storageDict[element]['C'] * storageDict[element]['max_depth'] )
        else:
            # do something here to add in storage curves
            pass

    return storageDict

def make_subcatchment_dictionary(sections):
    subcatchmentDict = {}

    for l in sections['[SUBCATCHMENTS]']:
        a = l.split()

        subcatchmentDict[a[0]] = {
            'rain_gage': a[1],
            'outlet': a[2],
            'area': float(a[3]),
            'per_imperv': float(a[4]),
            'width': float(a[5]),
            'slope': float(a[6]),
            'curblen': float(a[7])
        }

    return subcatchmentDict

def make_outfall_dictionary(sections):
    outfall = {}

    for l in sections['[OUTFALLS]']:
        a = l.split()
        outfall[a[0]] = {
            'elevation': float(a[1]),
            'type': a[2],
        }

        if a[2] == 'FREE':
            outfall[a[0]]['stage_data'] = 0.0
            outfall[a[0]]['gated'] = a[3]
        else:
            outfall[a[0]]['stage_data'] = float(a[3]),
            outfall[a[0]]['gated'] = a[4]

    return outfall

def make_orifice_dictionary(sections):
    orifice = {}

    for l in sections['[ORIFICES]']:
        a = l.split()
        orifice[a[0]] = {
            'from_node': str(a[1]),
            'to_node': str(a[2]),
            'type':a[3],
            'offset':float(a[4]),
            'Cd':float(a[5]),
            'gated':a[6],
            'close_time':float(a[7])
        }

    for l in sections['[XSECTIONS]']:
        a = l.split()

        try:
            orifice[a[0]]['shape'] = a[1]
            orifice[a[0]]['geom1'] = float(a[2])
            orifice[a[0]]['geom2'] = float(a[3])
            orifice[a[0]]['geom3'] = float(a[4])
            orifice[a[0]]['geom4'] = float(a[5])
            orifice[a[0]]['barrels'] = int(a[6])
            orifice[a[0]]['culvert'] = float(a[7])
        except:
            pass

    return orifice

def make_curves_dictionary(sections):
    curves = {}

    for l in sections['[CURVES]']:
        a = l.split()

        if len(a) == 4:
            curves[a[0]] = {
                'type':a[1],
                'x_val':[a[2]],
                'y_val':[a[3]]
            }

        if len(a) == 3:
            curves[a[0]]['x_val'].append(a[1])
            curves[a[0]]['y_val'].append(a[2])

    return curves

def make_pump_dictionary(sections,curves):
    pump = {}
    for l in sections['[PUMPS]']:
        a = l.split()
        pump[a[0]] = {
            'from_node':a[1],
            'to_node':a[2],
            'pump_curve':a[3],
            'status':a[4],
            'startup':a[5],
            'shutoff':a[6]
        }

    for p in pump:
        pump[p]['curve_info'] = curves[pump[p]['pump_curve']]

    return pump

def make_options_dictionary(sections):
    options = {}

    for l in sections['[OPTIONS]']:
        a = l.split()
        options[a[0]]=a[1]

    step_str = options['ROUTING_STEP'].split(':')
    timestep_sec = float(step_str[0])*60*60 + float(step_str[1])*60 + float(step_str[2])
    options['ROUTING_STEP'] = timestep_sec

    return options

def calc_slope(conduitDict,junctionDict,storageDict,min_slope):
    for item in conduitDict:
        if conduitDict[item]['from_node'] in junctionDict.keys():
            e1 = junctionDict[conduitDict[item]['from_node']]['elevation']+conduitDict[item]['in_offset']
        elif conduitDict[item]['from_node'] in storageDict.keys():
            e1 = storageDict[conduitDict[item]['from_node']]['elevation']+conduitDict[item]['in_offset']
        else:
            e1 = 1

        if conduitDict[item]['to_node'] in junctionDict.keys():
            e2 = junctionDict[conduitDict[item]['to_node']]['elevation']+conduitDict[item]['out_offset']
        elif conduitDict[item]['to_node'] in storageDict.keys():
            e2 = storageDict[conduitDict[item]['to_node']]['elevation']+conduitDict[item]['out_offset']
        else:
            e2 = 1

        if e1==1 or e2==1:
            conduitDict[item]['slope_flag'] = True
        else:
            conduitDict[item]['slope_flag'] = False

        slope = (e1 - e2)/conduitDict[item]['length']

        if slope < min_slope:
            slope = min_slope
            conduitDict[item]['slope_flag'] = True

        conduitDict[item]['slope'] = slope

def calc_qfull(conduitDict):
    for item in conduitDict:
        if conduitDict[item]['shape'] == 'CIRCULAR':
            # compute Qfull as pipe full manning equation
            conduitDict[item]['q_full'] = (conduitDict[item]['geom1']**(8/3)*conduitDict[item]['slope']**(1/2))/(4**(5/3)*conduitDict[item]['roughness'])*math.pi
        elif conduitDict[item]['shape'] == 'RECT_CLOSED':
            # Compute q_full as manning equation of pipe with manning eq with depth as 0.95
            conduitDict[item]['q_full'] = (1.49/conduitDict[item]['roughness']) * (0.95 * conduitDict[item]['geom1'] * conduitDict[item]['geom2']) * (conduitDict[item]['geom2'] * 0.95 * conduitDict[item]['geom1'] / (conduitDict[item]['geom2'] + 2 * 0.95 * conduitDict[item]['geom1']))**(2/3)
        else:
            conduitDict[item]['q_full'] = 1;

def change_elev(swmm_nodes,nodeD,storD,outD):
    for n in swmm_nodes:
        try:
            #print(swmm_nodes[n.nodeid].invert_elevation)
            swmm_nodes[n.nodeid].invert_elevation = nodeD[n.nodeid]['elev_detroit']
            #print(swmm_nodes[n.nodeid].invert_elevation)
        except:
            try:
                swmm_nodes[n.nodeid].invert_elevation = storD[n.nodeid]['elev_detroit']
                #print('beech')
            except:
                try:
                    swmm_nodes[n.nodeid].invert_elevation = outD[nodeid]['elev_detroit']
                    #print('grab em')
                except:
                    print("Error in Datum Change for "+n.nodeid)
                    pass

def datum_conversion(withElev,offset):
    for point in withElev:
        withElev[point]['elev_detroit'] = withElev[point]['elevation'] - offset

def orifice_xsect_grab(controlDict,orifices):
    # Add items from orifices dictionary to the control dict
    for i in controlDict:
        try:
            controlDict[i].update(orifices[i])
        except:
            pass

def pump_curve_grab(controlDict, pumps):
    # Add information to controlDict with pump curve info.
    for i in controlDict:
        try:
            controlDict[i].update(pumps[i])
        except:
            pass

def return_inputs(filename,handle):
    #
    df = pd.read_csv(filename,index_col='name')
    df.index = df.index.map(str)
    df_dict = df.to_dict(into=OrderedDict,orient='index')

    for i in df_dict:
        if handle == 'control':
            df_dict[i]['actionTS'] = []
            df_dict[i]['q_goal'] = 1.0
        elif handle == 'upstream':
            df_dict[i]['ts'] = []
            df_dict[i]['PD'] = []
        elif handle == 'downstream':
            df_dict[i]['ts_flow'] = []
            df_dict[i]['ts_depth'] = []
        elif handle == 'performance':
            df_dict[i]['ts_flow'] = []
            df_dict[i]['ts_depth'] = []
        else:
            pass

    return df_dict

def get_depth(elements,conduitDict,storageDict):
    for element in elements:
        if elements[element]['type'] == 'link':
            elements[element]['max_depth'] = conduitDict[element]['geom1']
        elif elements[element]['type'] == 'storage':
            elements[element]['max_depth'] = storageDict[element]['max_depth']
        else:
            pass

def get_q_full_and_other(elements,conduits,storages):
    for element in elements:
        if elements[element]['type'] == 'link':
            elements[element]['max_flow'] = conduits[element]['q_full']
        elif elements[element]['type'] == 'storage':
            elements[element]['total_storage'] = storages[element]['total_storage']
        else:
            pass

def performance_elements(elements,conduits,nodes,storages,subcatchments,outfalls,orifices):
    for element in elements:
        if elements[element]['type'] == 'outfall':
            elements[element]['elevation'] = outfalls[element]['elevation']
            elements[element]['elev_detroit'] = outfalls[element]['elev_detroit']
        elif elements[element]['type'] == 'link':
            elements[element]['max_depth'] = conduits[element]['geom1']
        elif elements[element]['type'] == 'storage':
            elements[element]['max_depth'] = storages[element]['max_depth']
        elif elements[element]['type'] == 'orifice':
            elements[element]['max_depth'] = orifices[element]['geom1']
        else:
            pass
