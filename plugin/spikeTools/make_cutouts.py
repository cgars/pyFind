# -------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------

from pyFind.Find import FindPlugin
from plugin.PyFindGUI.PyFindGUI import Draggable


class MakeCutouts(FindPlugin):
    def __init__(self):
        pass

    @classmethod
    def find_call(cls):
        return make_cutouts

    @classmethod
    def get_draggable(cls, parent, find_object):
        return MakeCutoutsDrag(parent, make_cutouts, find_object.spikeTools.MakeCutouts)


class MakeCutoutsDrag(Draggable):
    def __init__(self, parent, this_function, find_function):
        Draggable.__init__(self, parent, this_function, find_function, outputs=['op1'], label='Make Cutouts')


def make_cutouts(data_entity, times, cut_before=10, cut_after=10):
    """
    Generates cutout window for given times from data_entity.
    
    GENERAL OPTIONS
        define the extent of the cutout window ('cutBefore' to 'cutAfter')
        Default: cut_before = 10;
        Default: cut_after = 10;
    """
    samples = []
    for time in times:
        samples.append(data_entity[time - cut_before:time + cut_after + 1])

    return samples
