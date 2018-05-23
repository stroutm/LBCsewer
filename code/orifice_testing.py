import numpy as np

def get_target_setting(ustream_depth,dstream_depth,flow_want,current_setting,shape,units,Cd,orificeDiam,ustreamInvertElev,dstreamInvertElev):
    if units == "english":
        g = 32.2
    else:
        g = 9.81

    ustreamInletOffset = 0.0
    dstreamInletOffset = 0.0

    h1 = ustream_depth + ustreamInvertElev
    h2 = dstream_depth + dstreamInvertElev

    # for a side orifice
    hcrest = ustreamInvertElev + ustreamInletOffset
    hcrown = hcrest + orificeDiam * current_setting
    hmidpt = (hcrest + hcrown) / 2

    # inlet submergence
    if h1 < hcrown:
        f = (h1 - hcrest) / (hcrown - hcrest)
    else:
        f = 1.0

    # head on orifice
    if f < 1.0:
        head = h1 - hcrest
    elif h2 < hmidpt:
        head = h1 - hmidpt
    else:
        head = h1 - h2

    # use calculated head and desired flow to determine gate opening (action)

    # no head at orifice
    if head < 0.1 or f <= 0.0:
        action = 0.0
        note = 1

    elif ustream_depth < dstream_depth:
        action = 0.0
        note = 4

    # weir flow
    elif (f < 1.0 and head > 0.1):
        # similar to orifice case, just with factor of 2/3
        A_open = flow_want / (Cd*np.sqrt(2.0*g*head)*(2.0/3.0))
        if shape == "circular":
            print("Circular doesn't work yet")
            #Aratio = A_open / ( np.pi * orificeDiam**2 / 4.0 )
            #action = -1.1148 * Aratio**3 + 1.6721 * Aratio**2 + 0.4553 * Aratio - 0.0063
            action = 0.0
        else:
            Aratio = A_open / orificeDiam**2
            action = Aratio
        note = 2

    # true orifice flow
    else:
        # since q = Cd * A_open * sqrt( 2 g head )
        A_open = flow_want / Cd / np.sqrt(2*g*head)
        # Aratio = A_open / A_full
        if shape == "circular":
            print("Circular doesn't work yet")
            #Aratio = A_open / ( np.pi * orificeDiam**2 / 4.0 )
            # fitting polynomial to lookup table for circular orifice
            # yratio = y_open / y_full = gate opening = action
            #action = -1.1148 * Aratio**3 + 1.6721 * Aratio**2 + 0.4553 * Aratio - 0.0063
            action = 0.0
        else:
            Aratio = A_open / orificeDiam**2
            # yratio = y_open / y_full = action = Aratio
            action = Aratio
        note = 3

    action = min(max(action,0.0),1.0)

    return action, note, head
