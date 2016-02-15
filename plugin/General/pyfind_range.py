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


class PyFindRange(FindPlugin):
    """
    The Range plugin returns a range of integers
    """

    def __init__(self):
        pass

    @classmethod
    def find_call(cls):
        return pyfind_range

    @classmethod
    def get_draggable(cls, parent, find_object):
        return PyFindRangeDrag(parent, pyfind_range, find_object.General.PyFindRange)


class PyFindRangeDrag(Draggable):
    def __init__(self, parent, this_function, find_function):
        Draggable.__init__(self, parent, this_function, find_function, outputs=['list'], label='List')
        self.result = find_function()


def pyfind_range(start=1, stop=10):
    """
    Returns a integer range from start to stop
    :param start:
    :param stop:
    :return:
    """
    return range(int(start), int(stop))
