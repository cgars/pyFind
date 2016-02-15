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


class Duplicate(FindPlugin):
    """
    This plugin takes one Input and duplicates. It only makes sense
    when used with the GUI
    """

    def __init__(self):
        pass

    @classmethod
    def find_call(cls):
        return duplicate

    @classmethod
    def get_draggable(cls, parent, find_object):
        return DuplicateDrag(parent, duplicate, find_object.General.Duplicate)


class DuplicateDrag(Draggable):
    def __init__(self, parent, this_function, find_function):
        Draggable.__init__(self, parent, this_function, find_function, outputs=('output1', 'output2'),
                           label='Duplicate')

    def update(self):
        """
        Overides the default update (as updating a duplication
        is useless)
        :return:
        """
        pass

    def get_result(self, op_name):
        return self.inputs['input'].get_result()


def duplicate(input):
    return input
