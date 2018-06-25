import numpy as np

def GDRSS_build(ISDs):
    state_space = {"depthsN":[],"depthsL":[],"flows":["Trunk02"],"inflows":[]}
    control_points = []
    max_depths = []
    uInvert = []
    dInvert = []
    orifice_diam_all = []
    colors = []
    labels = []

    if 13 in ISDs:
        state_space["depthsN"].append("2355");
        state_space["depthsL"].append("2360");
        state_space["inflows"].append("RC12355");
        control_points.append("ISD013_DOWN");
        max_depths.append(11.5);
        uInvert.append(604.76);
        dInvert.append(604.71);
        orifice_diam_all.append(11.5);
        colors.append('#276278');
        labels.append('K');
    if 12 in ISDs:
        state_space["depthsN"].append("25250");
        state_space["depthsL"].append("2525");
        state_space["inflows"].append("RC12521");
        state_space["inflows"].append("RC12520");
        state_space["inflows"].append("RC12770");
        control_points.append("ISD012_DOWN");
        max_depths.append(10.5);
        uInvert.append(604.56);
        dInvert.append(604.51);
        orifice_diam_all.append(10.5);
        colors.append('#167070');
        labels.append('J');
    if 11 in ISDs:
        state_space["depthsN"].append("2745");
        state_space["depthsL"].append("2765");
        state_space["inflows"].append("RC12350");
        state_space["inflows"].append("RC12345");
        state_space["inflows"].append("RC12315");
        state_space["inflows"].append("RC12765");
        control_points.append("ISD011_DOWN");
        max_depths.append(15.5);
        uInvert.append(580.86);
        dInvert.append(580.81);
        orifice_diam_all.append(15.5);
        colors.append('#55a6a6');
        labels.append('I');
    if 10 in ISDs:
        state_space["depthsN"].append("22201");
        state_space["depthsL"].append("2388");
        state_space["inflows"].append("RC12397");
        state_space["inflows"].append("RC12389");
        control_points.append("ISD010_DOWN");
        max_depths.append(12.25);
        uInvert.append(603.86);
        dInvert.append(603.81);
        orifice_diam_all.append(12.25);
        colors.append('#b5491a');
        labels.append('H');
    if 9 in ISDs:
        state_space["depthsN"].append("2195");
        state_space["depthsL"].append("2201");
        state_space["inflows"].append("RC12201");
        state_space["inflows"].append("RC12200");
        control_points.append("ISD009_DOWN");
        max_depths.append(15.5);
        uInvert.append(591.36);
        dInvert.append(591.31);
        orifice_diam_all.append(15.5);
        colors.append('#fe6625');
        labels.append('G');
    if 8 in ISDs:
        state_space["depthsN"].append("2185");
        state_space["depthsL"].append("21950");
        control_points.append("ISD008_DOWN");
        max_depths.append(15.5);
        uInvert.append(585.26);
        dInvert.append(585.21);
        orifice_diam_all.append(15.5);
        colors.append('#fe9262');
        labels.append('F');
    if 7 in ISDs:
        state_space["depthsN"].append("2170");
        state_space["depthsL"].append("21853");
        control_points.append("ISD007_DOWN");
        max_depths.append(15.5);
        uInvert.append(578.86);
        dInvert.append(578.81);
        orifice_diam_all.append(15.5);
        colors.append('#fb9334');
        labels.append('E');
    if 6 in ISDs:
        state_space["depthsN"].append("2145");
        state_space["depthsL"].append("2160");
        state_space["inflows"].append("RC32160");
        state_space["inflows"].append("RC3214500");
        control_points.append("ISD006_DOWN");
        max_depths.append(15.5);
        uInvert.append(572.46);
        dInvert.append(572.46);
        orifice_diam_all.append(15.5);
        colors.append('#ffb16c');
        labels.append('D');
    if 4 in ISDs:
        state_space["depthsN"].append("1516");
        state_space["depthsL"].append("1535");
        state_space["inflows"].append("RC11570");
        state_space["inflows"].append("RC11571");
        state_space["inflows"].append("RC11550");
        state_space["inflows"].append("RC11545");
        state_space["inflows"].append("RC11535");
        control_points.append("ISD004_DOWN");
        max_depths.append(14.0);
        uInvert.append(587.36);
        dInvert.append(587.31);
        orifice_diam_all.append(14.0);
        colors.append('#414a4f');
        labels.append('C');
    if 3 in ISDs:
        state_space["depthsN"].append("1952");
        state_space["depthsL"].append("RC1951");
        state_space["inflows"].append("RC1951");
        control_points.append("ISD003_DOWN");
        max_depths.append(20.0);
        uInvert.append(586.36);
        dInvert.append(586.31);
        orifice_diam_all.append(9.0);
        colors.append('#006592');
        labels.append('B');
    if 2 in ISDs:
        state_space["depthsN"].append("1504");
        state_space["depthsL"].append("1509");
        state_space["inflows"].append("RC19523");
        control_points.append("ISD002_DOWN");
        max_depths.append(13.45);
        uInvert.append(581.66);
        dInvert.append(581.66);
        orifice_diam_all.append(14.7);
        colors.append('#003d59');
        labels.append('A');

    if 13 in ISDs:
        state_space["depthsN"].append("23554");
        control_points.append("ISD013_UP");
        state_space["inflows"].append("2351");
    if 12 in ISDs:
        state_space["depthsN"].append("25254");
        control_points.append("ISD012_UP");
        state_space["inflows"].append("25251");
    if 11 in ISDs:
        state_space["depthsN"].append("27453");
        control_points.append("ISD011_UP");
        state_space["inflows"].append("27450");
    if 10 in ISDs:
        state_space["depthsN"].append("22204");
        control_points.append("ISD010_UP");
        state_space["inflows"].append("22202");
    if 9 in ISDs:
        state_space["depthsN"].append("21954");
        control_points.append("ISD009_UP");
        state_space["inflows"].append("21950");
    if 8 in ISDs:
        state_space["depthsN"].append("21859");
        control_points.append("ISD008_UP");
        state_space["inflows"].append("21852");
    if 7 in ISDs:
        state_space["depthsN"].append("21703");
        control_points.append("ISD007_UP");
        state_space["inflows"].append("21700");
    if 6 in ISDs:
        state_space["depthsN"].append("21454");
        control_points.append("ISD006_UP");
        state_space["inflows"].append("21450");
    if 4 in ISDs:
        state_space["depthsN"].append("15164");
        control_points.append("ISD004_UP");
        state_space["inflows"].append("1515");
    if 3 in ISDs:
        state_space["depthsN"].append("19523");
        control_points.append("ISD003_UP");
        state_space["inflows"].append("19520");
    if 2 in ISDs:
        state_space["depthsN"].append("15031");
        control_points.append("ISD002_UP");
        state_space["inflows"].append("1503");

    if (13 in ISDs) or (12 in ISDs) or (11 in ISDs):
        state_space["flows"].append("27450");
        colors.append('#167070');
        labels.append('I-K');
    if (10 in ISDs) or (9 in ISDs) or (8 in ISDs) or (7 in ISDs) or (6 in ISDs):
        state_space["flows"].append("21450");
        colors.append('#fe6625');
        labels.append('D-H');
    if (4 in ISDs) or (3 in ISDs) or (2 in ISDs):
        state_space["flows"].append("1503");
        colors.append('#003d59');
        labels.append('A-C'); 

    colors.append('#66747c')

    return state_space, control_points, max_depths, uInvert, dInvert, orifice_diam_all, colors, labels
