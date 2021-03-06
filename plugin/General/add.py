# -------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------

from Tkinter import *

from numpy import *

from pyFind.Find import FindPlugin
from plugin.PyFindGUI.PyFindGUI import Draggable, MyScale


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
        self.parameter_button.place_forget()
        self.help_button.place_forget()
        self.scale1 = MyScale(self, from_=0, to=2, digits=3, name='scale1',
                              orient=HORIZONTAL, sliderlength=5, tickinterval=0, resolution=0.1,
                              length=50, width=5)
        self.scale1.place(x=30, y=50)
        self.scale2 = MyScale(self, from_=0, to=2, digits=3, name='scale2',
                              orient=HORIZONTAL, sliderlength=5, tickinterval=0, resolution=0.1,
                              length=50, width=5)
        self.scale2.place(x=90, y=50)

    def update(self):
        self.result = self.find_function(float(self.scale1.get_value()) *
                                         self.inputs['v1'].get_result().data,
                                         float(self.scale2.get_value()) *
                                         self.inputs['v2'].get_result().data)
        [e.update() for e in self.next]


def pyfind_add(v1, v2):
    """
    Substract the two values
    :param v1: Value1
    :param v2: Value2
    :return: The result of adding the two values
    """
    return add(v1, v2)
