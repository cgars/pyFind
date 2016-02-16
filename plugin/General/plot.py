# -------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------
from Tkinter import Label
import pylab

from plugin.PyFindGUI.PyFindGUI import Draggable
from pyFind.Find import FindPlugin


class Plot(FindPlugin):
    """
    A Plugin that can plot iteratables
    """

    @classmethod
    def find_call(cls):
        return plot

    @classmethod
    def get_draggable(cls, parent, find_object):
        return PlotPlotter(parent, plot, find_object.General.Plot)


class PlotPlotter(Draggable):
    """
    A Dragable supporting online plotting
    The plot is iteratively updated once created
    """

    def __init__(self, parent, this_function, find_function):
        Draggable.__init__(self, parent, this_function, find_function)
        self.parameter = []
        self.figure = None
        self.label = Label(self, text="Plot")
        self.label.place(x=50, y=0)

    def on_close(self):
        self.figure = None

    def redraw(self):
        '''
        Draws or redraws a figure
        It must be called from the ui thread (see update below)
        '''
        if not self.figure:
            pylab.ioff()
            self.figure = pylab.figure()
            self.find_function(self.get_result('hallali'))
            self.figure.canvas.mpl_connect('close_event', self.on_close)
            pylab.ion()
            pylab.show()

        else:
            y = self.get_result('hallali')
            pylab.gca().get_lines()[0].set_data(range(len(y)), y)
            pylab.ylim(min(y), max(y))

    def update(self):
        """
        Overides update to ensure that redraw is called from the ui thread.
        We use a small trick here and misues Tkinter after functionality to ensure
        the pylab stuff is done in the ui thread
        """
        self.parent.after(0, self.redraw)
        [e.update() for e in self.next]

    def get_result(self, name):
        return self.inputs['_data'].get_result()


def plot(_data):
    return pylab.plot(_data)
