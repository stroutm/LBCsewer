import numpy as np

def GDRSS_build(ISDs):
    control_points = []
    colors = []
    labels = []
    ustreamConduits = []
    branchConduits = []
    WRRFConduit = "Trunk02"

    if 13 in ISDs:
        control_points.append("ISD013_DOWN");
        colors.append('#276278');
        labels.append('K');
        ustreamConduits.append('2360');
    if 12 in ISDs:
        control_points.append("ISD012_DOWN");
        colors.append('#167070');
        labels.append('J');
        ustreamConduits.append('2525');
    if 11 in ISDs:
        control_points.append("ISD011_DOWN");
        colors.append('#55a6a6');
        labels.append('I');
        ustreamConduits.append('2765');
    if 10 in ISDs:
        control_points.append("ISD010_DOWN");
        colors.append('#b5491a');
        labels.append('H');
        ustreamConduits.append('2388');
    if 9 in ISDs:
        control_points.append("ISD009_DOWN");
        colors.append('#fe6625');
        labels.append('G');
        ustreamConduits.append('2201');
    if 8 in ISDs:
        control_points.append("ISD008_DOWN");
        colors.append('#fe9262');
        labels.append('F');
        ustreamConduits.append('21950');
    if 7 in ISDs:
        control_points.append("ISD007_DOWN");
        colors.append('#fb9334');
        labels.append('E');
        ustreamConduits.append('21853');
    if 6 in ISDs:
        control_points.append("ISD006_DOWN");
        colors.append('#ffb16c');
        labels.append('D');
        ustreamConduits.append('2160');
    if 4 in ISDs:
        control_points.append("ISD004_DOWN");
        colors.append('#414a4f');
        labels.append('C');
        ustreamConduits.append('1535');
    if 3 in ISDs:
        control_points.append("ISD003_DOWN");
        colors.append('#006592');
        labels.append('B');
        ustreamConduits.append('RC1951');
    if 2 in ISDs:
        control_points.append("ISD002_DOWN");
        colors.append('#003d59');
        labels.append('A');
        ustreamConduits.append('1509');

    if 13 in ISDs:
        control_points.append("ISD013_UP");
    if 12 in ISDs:
        control_points.append("ISD012_UP");
    if 11 in ISDs:
        control_points.append("ISD011_UP");
    if 10 in ISDs:
        control_points.append("ISD010_UP");
    if 9 in ISDs:
        control_points.append("ISD009_UP");
    if 8 in ISDs:
        control_points.append("ISD008_UP");
    if 7 in ISDs:
        control_points.append("ISD007_UP");
    if 6 in ISDs:
        control_points.append("ISD006_UP");
    if 4 in ISDs:
        control_points.append("ISD004_UP");
    if 3 in ISDs:
        control_points.append("ISD003_UP");
    if 2 in ISDs:
        control_points.append("ISD002_UP");

    if (13 in ISDs) or (12 in ISDs) or (11 in ISDs):
        colors.append('#167070');
        labels.append('I-K');
        branchConduits.append('27450');
    if (10 in ISDs) or (9 in ISDs) or (8 in ISDs) or (7 in ISDs) or (6 in ISDs):
        colors.append('#fe6625');
        labels.append('D-H');
        branchConduits.append('21450');
    if (4 in ISDs) or (3 in ISDs) or (2 in ISDs):
        colors.append('#003d59');
        labels.append('A-C');
        branchConduits.append('1503');

    colors.append('#66747c')

    return control_points, colors, labels, ustreamConduits, branchConduits, WRRFConduit
