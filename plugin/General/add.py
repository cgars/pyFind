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


class Add(FindPlugin):
    """
    This pyFind plugin supports a simple addition operation
    """
    @classmethod
    def find_call(cls):
        return pyfind_add

    @classmethod
    def get_draggable(cls, parent, find_object):
        return AddDrag(parent, pyfind_add, find_object.plugins.General.Add)


class AddDrag(Draggable):
    def __init__(self, parent, this_function, find_function):
        Draggable.__init__(self, parent, this_function, find_function, outputs=['Result'], label='Add')


def pyfind_add(v1, v2):
    """
    Add the two values
    :param v1: Value1
    :param v2: Value2
    :return: The result of adding the two values
    """
    return add(v1, v2)
