# -------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------
from numpy import *

from pyFind.Find import FindPlugin
from plugin.PyFindGUI.PyFindGUI import Draggable


class DetectSpikes(FindPlugin):
    def __init__(self):
        pass

    @classmethod
    def find_call(cls):
        return detect_spikes

    @classmethod
    def get_draggable(cls, parent, find_object):
        return DetectSpikesDrag(parent, detect_spikes, find_object.spikeTools.DetectSpikes)


class DetectSpikesDrag(Draggable):
    def __init__(self, parent, this_function, find_function):
        Draggable.__init__(self, parent, this_function, find_function,
                           outputs=['op1'], label='Detect Spikes')


def detect_spikes(data_entity,
                  method_number=1,
                  deadtime=0,
                  threshold_factor=5,
                  known_median=20,
                  absolute_flag=1):
    """
    detect_spikes uses the following parameters.

    %%%%% Obligatory Parameters %%%%%

    'data_entity': selected Entities to detect spikes

    %%%%% Optional Parameters %%%%%
    
    'method_number': determines the detection method ,
    Default: methodNumber=1 (The rect. N times median).
    
    'deadTime': time in which no new spike can occur.
    in data units
    Default: deadTime=0;
    
    'threshold_factor': determines the threshold to detect spikes,
    Default: thresholdFactor=5;
    
    GENERAL OPTIONS
       the detection can either be done on absolute or on normal data
       case 1: The rect. N times median
       case 2: The rect. mean +/- SD
       case 3: The mean +/- SD
       case 4: with known median

    based on code by R. Meier Feb 07 meier@biologie.uni-freiburg.de
    """

    data_entity = array(data_entity)

    if absolute_flag:
        # if flag is set, make data absolute
        data_entity = abs(data_entity)

    if method_number == 0:
        # uses method as in Quian Quiroga et al. (2004)
        threshold = threshold_factor * median(abs(data_entity)) / 0.6745

    elif method_number == 1:
        # uses the rectangular N times median to determine the threshold
        threshold = threshold_factor * median(abs(data_entity))

    elif method_number == 2:
        # uses the rectangular mean and standard deviation to determine the
        # threshold
        data_entity = abs(data_entity)
        threshold = mean(data_entity) + threshold_factor * std(data_entity)

    elif method_number == 3:
        # uses the mean and standard deviation to determine the threshold
        threshold = mean(data_entity) + threshold_factor * std(data_entity)

    elif method_number == 4:
        # with known median
        threshold = threshold_factor * known_median

    else:
        errorstr = "Your input for method_number has not been recognised." \
                   + "Your method_number:" + str(method_number) + "\n" + \
                   "Expected input for method_number: integer between 0-4"

        print errorstr
        return 0

    # create list with 1 for every threshold crossing, otherwise 0
    print threshold
    temp = data_entity[:] > threshold

    # temp[1:] - temp[:-1] calculates differences between adjacent
    # elements of temp for every spike position this is 1
    spike_times = nonzero((temp[1:] - temp[:-1]) == 1)[0]

    if deadtime:
        # take spike times with distance to spike time before  > deadtime
        agap = [0]
        agap.extend((nonzero((spike_times[1:] - spike_times[:-1]) >
                             deadtime)[0] + 1))
        return spike_times[agap]
    else:
        return spike_times
