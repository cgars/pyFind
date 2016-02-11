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
import inspect
import logging
import traceback
import threading

from pyFind.Find import FindPlugin


class GUI(FindPlugin):
    """
    Base Class for the GUI
    can be called via Find
    """

    def __init__(self, find_object):
        """
        find_object: The Find Object with which this
        GUI  should controll/work with
        """
        self.find_object = find_object

    def start(self):
        """
        Start the GUI with all availible GUI plugins
        """
        tkinter_root = Tk()
        tkinter_root.wm_title("pyFind")
        m_frame = MainFrame(tkinter_root, self.find_object,
                            width=1900, height=1200)
        logging.debug('Starting the pyFind GUI')
        tkinter_root.mainloop()

    @classmethod
    def find_call(cls):
        """
        Returns a function that returns a GUI Object
        This is needed for the GUI to be callable with
        Find
        """
        return lambda find_object: GUI(find_object)


# Here comes the main functionality
class MainMenue(Menu):
    """
    This is the main manue of the GUI
    It assembles itself mainly by checking the plugin
    Folder for classes returning Draggables
    """

    def __init__(self, parent, find_object, **kwargs):
        """
        parent: The Frame in which the Menue is created
        find_object: The Find Object
        """
        Menu.__init__(self, parent, **kwargs)
        self.parent = parent
        self.add_menue = Menu(self, tearoff=0)
        logging.debug('Will start walking plugins to find Guified Plugins')
        self.__walk_plugins(self, find_object.plugins, find_object)

    def __walk_plugins(self, parent_menu, tree, find_object):
        """
        Walks through the plugin folder and adds the to the path
        For each folder a cascade is created in the main menue
        parent_menue: the menue in which to work
        tree: a tree or subtree as returned by os.walk
        find_object: The Find Object

        """
        if len(tree.nodes) > 0:
            for node in tree.nodes:
                parent_menu.add_cascade(label=node.name,
                                        menu=self.__walk_plugins(Menu(parent_menu, tearoff=0),
                                                                 node,
                                                                 find_object))
        self.add_new_module(self.__check_for_guified_plugins__(tree.leaves), find_object, parent_menu)
        return parent_menu

    def __check_for_guified_plugins__(self, plugins):
        """
        Returns a list of all Find plugins that implement a get_draggable method
        in _files
        """
        guified_plugins = filter(lambda x: hasattr(x[1], 'get_draggable'), plugins)
        logging.debug('%s are plugins providing GUI functionality' % (guified_plugins))
        return guified_plugins

    def add_new_module(self, plugins, find_object, parent_menu):
        """
        Call each plugins[1] get_draggable method and bind the return to a menue
        entry with thge name plugin[0]
        """
        for plugin in plugins:
            logging.debug('Will try to add %s to t %s' % (plugin, parent_menu))
            parent_menu.add_command(label=plugin[0],
                                    command=(lambda worker=plugin[1]:
                                             worker.get_draggable(self.parent, find_object)))
            """
            This is tricky!!!
            As worker would normally point to the last worker only 
            because the menues command statement is only evaluated when called 
            (which is after the for loop), we need to redeclare the worker in 
            its own scope (function). Which we do with:
            def add_worker(worker=worker). 
            Therefore we add a function that adds 
            exactly the worker we really 
            meant
            """


class Result(Frame):
    """
    Results model a Result calculated by a method modelled by
    the Draggable this Result is part of. They form atarting points
    for connections
    Results can be connected to other Draggebles.
    they can also be asked for there value
    """

    def __init__(self, parent, name, output_frame, **kwargs):
        """
        parent:  Parent Draggbble
        name:  string whith the anme of this Result/Output
        position:  relative postion in the draggble
        """
        Frame.__init__(self, output_frame, bg="grey", **kwargs)
        self.name = name
        self.label = Label(self, text=self.name, bg="grey")
        self.label.pack()
        self.icon = FramedIcon(self)
        self.icon.pack(anchor='w')
        self.parent = parent
        self.output_frame = output_frame
        self.pack(side=LEFT, padx=3)
        self.active = False
        self.next = None

    def on_down(self, event):
        """
        If we are not already active, but are connected cut connection
        and make us active. if somneobe alese is active deativate him and activate us
        if we were active deactivate us
        """
        if not self.active:
            if self.next:
                self.next.remove_previous()
            self.icon.config(bg='yellow')
            self.active = True
            if self.parent.parent.active:
                self.parent.parent.active.active = False
                self.parent.parent.active.icon.config(bg='red')
            self.parent.parent.active = self
        else:
            self.icon.config(bg='red')
            self.active = False
            self.parent.parent.active = None
            if self.next:
                self.next.remove_previous()

    def get_result(self):
        """
        Tell the result of our parent give when asked for our name
        """
        return self.parent.get_result(self.name)

    def get_absx(self):
        """
        Return out absolute X Postion
        """
        return self.parent.winfo_x() + self.parent.output_frame.winfo_x() + self.winfo_x() + self.icon.winfo_x()

    def get_absy(self):
        """
        Return out absolute Y Postion
        """
        return self.parent.winfo_y() + self.parent.output_frame.winfo_y() + self.winfo_y() + self.icon.winfo_y()

    def on_move(self):
        """
        If we are moved (normally happend when our parent is moved)
        We have to update the line to our next if such exist
        """
        if self.next:
            self.next.canvas.coords(self.next.arrow,
                                    self.get_absx(), self.get_absy(),
                                    self.next.get_absx(), self.next.get_absy())


class FramedIcon(Frame):
    def __init__(self, parent):
        """

        """
        Frame.__init__(self, parent, bg="red", width=10, height=10)
        self.bind("<Button-1>", self.on_down)
        self.parent = parent

    def on_down(self, event):
        """
        if we have no connection yet and there is someone
        waiting for a connection partner, connect us to him
        if we are already connected break connection
        """
        self.parent.on_down(event)


class Input(Frame):
    """
    Input Objects model End points of connections. They can be asked for
    results, do draw and update lines
    """

    def __init__(self, parent, name, input_frame, **kwargs):
        """
        parent  Parent draggbble
        name  string whith the anme of this input
        position  relative postion in the draggble
        """
        Frame.__init__(self, input_frame, bg="grey", **kwargs)
        self.icon = FramedIcon(self)
        self.icon.pack(anchor='w')
        self.parent = parent
        self.pack(side=LEFT, padx=3)
        self.name = name
        #        self.absx = int(self.place_info()['x'])
        #        self.absy = int(self.place_info()['y'])
        #        self.bind("<Button-1>", self.on_down)
        self.previous = None
        self.canvas = self.parent.parent.canvas
        self.label = Label(self, text=self.name, bg="grey")
        self.label.pack()

    def on_down(self, event):
        """
        if we have no connection yet and there is someone
        waiting for a connection partner, connect us to him
        if we are already connected break connection
        """
        if not self.previous and self.parent.parent.active:
            self.add_previous(self.parent.parent.active)
        elif self.previous:
            self.remove_previous()

    def add_previous(self, previous):
        """
        Connect us to previous. And draw a line marking this event on the
        canvas. Update our parent Draggable
        """
        self.icon.config(bg='green')
        self.previous = previous
        self.parent.parent.active = False
        self.previous.active = False
        self.previous.icon.config(bg='green')
        self.previous.next = self
        self.arrow = self.canvas.create_line(self.previous.get_absx(),
                                             self.previous.get_absy(),
                                             self.get_absx(), self.get_absy())
        self.parent.add_previous(previous.parent)
        try:
            self.parent.update()
        except AttributeError:
            logging.error(traceback.format_exc())

    def remove_previous(self):
        """
        Delete our connection and delete the corresponding line
        """
        self.icon.config(bg='red')
        self.parent.remove_previous(self.previous.parent)
        self.previous.next = None
        self.previous.icon.config(bg='red')
        self.previous = None
        self.canvas.delete(self.arrow)

    def get_absx(self):
        """
        Return out absolute X Postion
        """
        return self.winfo_x() + self.parent.winfo_x()

    def get_absy(self):
        """
        Return out absolute Y Postion
        """
        return self.winfo_y() + self.parent.winfo_y()

    def on_move(self):
        """
        If we are moved (normally happend when our parent is moved)
        We have to update the line to our previous if such exist
        """
        if self.previous:
            self.canvas.coords(self.arrow,
                               self.previous.get_absx(),
                               self.previous.get_absy(),
                               self.get_absx(), self.get_absy())

    def get_result(self):
        """
        If we are asked for a Result we ask our previous
        """
        if self.previous:
            return self.previous.get_result()


class Draggable(Frame):
    """
    Base class for most workers as it provides drag and drop functionality.

    """

    def __init__(self, parent, this_function, find_function, position=(0, 0), outputs=[],
                 label=None, **kwargs):
        """
        parent  the widget on which this Draggable is placed
        position  starting position of this draggable
        this_function FIND function bound to this draggable
        outputs same as inputs but with outputs
        """
        Frame.__init__(self, parent, width=200, height=100, bg='grey', **kwargs)
        self.place(x=position[0], y=position[1])
        self.parent = parent
        self.absx = int(self.place_info()['x'])
        self.absy = int(self.place_info()['y'])
        self.this_function = this_function
        self.input_frame = Frame(self, bg='grey')
        self.input_frame.place(x=0, y=0)
        self.inputs = self.add_inputs(self.get_inputs())
        self.default_outputs = outputs
        self.output_frame = Frame(self, bg='grey')
        self.output_frame.place(x=0, y=70)
        self.outputs = self.add_outputs(self.get_outputs())
        self.bind("<Button-1>", self.on_down)
        self.bind("<B1-Motion>", self.on_move)
        self.next = []
        self.previous = []
        if label is not None:
            self.label = Label(self, text=label)
            self.label.place(x=50, y=30)
        self.parameter_button = Button(self, text="Parameter", command=self.open_params, font=('Arial', 6))
        self.parameter_button.place(x=70, y=50)
        self.help_button = Button(self, text="Help", command=self.help, font=('Arial', 6))
        self.help_button.place(x=30, y=50)
        self.parameters = []
        self.param_frame = ParameterFrame(self.parent, self, width=300,
                                          height=600)
        for parameter in self.get_parameter():
            self.parameters.append(parameter)
        self.find_function = find_function
        self.help_message = HelpMessage(parent, this_function)

    def on_down(self, event):
        """
        On mouse down track the relative postion of the courcer at movenment
        start
        """
        self.offset_x = event.x
        self.offset_y = event.y

    def on_move(self, event):
        """
        Move the draagable to the correct new postion
        inform all inputs and output objects of the position change and let
        them update line positions
        """
        new_x = self.absx + event.x - self.offset_x
        new_y = self.absy + event.y - self.offset_y
        self.place(x=new_x, y=new_y)
        self.absx = int(self.place_info()['x'])
        self.absy = int(self.place_info()['y'])
        [e.on_move() for e in self.inputs.itervalues()]
        [e.on_move() for e in self.outputs.itervalues()]

    def add_previous(self, previous):
        """
        Add a connection to an previous item
        """
        self.previous.append(previous)
        previous.add_next(self)

    def remove_previous(self, previous):
        """
        Cut a connection to an previous item
        """
        previous.remove_next(self)

    def add_next(self, _next):
        """
        add a connection to a next item
        """
        self.next.append(_next)

    def remove_next(self, _next):
        """
        remove a connection to a next item
        """
        self.next.remove(_next)

    def open_params(self):
        self.param_frame.reload()
        self.param_frame.place(x=self.absx + 10, y=self.absy + 10)

    def add_inputs(self, inputs):
        """
        inputs : list of strings defining inputs
        Paints Inputs as defined in input and returns a
        Dictionary of inputs
        """
        return dict(zip(inputs, [Input(self, e, self.input_frame) for e in inputs]))

    def clear_inputs(self):
        """
        Removes All Input Objects attached to this Draggable
        """
        for _Input in self.inputs.itervalues():
            if _Input.previous:
                _Input.remove_previous()
            _Input.pack_forget()

    def clear_outputs(self):
        """
        Removes All Input Objects attached to this Draggable
        """
        for _output in self.outputs.itervalues():
            if _output.next:
                _output.next.remove_previous()
            _output.pack_forget()

    def get_inputs(self):
        """
        Returns a List of Strings
        Every String will is the name of an input to the
        callable modelled by this draggable
        to self.Overide to change default behaviour
        """
        if inspect.getargspec(self.this_function)[3] is None:
            return inspect.getargspec(self.this_function)[0]
        else:
            return inspect.getargspec(self.this_function)[0][:-len(inspect.getargspec(self.this_function)[3])]

    def get_parameter(self):
        """
        Return a list of Parameter Objects
        Overide to change default behaviour
        """
        _tmp_list = []
        arguments = inspect.getargspec(self.this_function)
        if arguments[3]:
            for parameter, value in zip(arguments[0][-len(arguments[3]):], arguments[3]):
                _tmp_list.append(PvPParameter(self, parameter, value))

        return _tmp_list

    def get_result(self, _name):
        """
        Overide to change functionality
        Default: Assemble all default inputs to form args
                 all parameters to form kwargs and add inputified
                 parameters too.
                 pass all this into the find_function and return the
                 result
        """
        if len(self.outputs) > 1:
            return self.result.get_sub_result(self.default_outputs.index(_name))
        else:
            return self.result

    def update(self):
        """
        This is called whenever one partner upstream changes or is updated
        Do not Overide this method overide the async part instead (see below)
        """
        if self.all_inputs_set():
            threading.Thread(target=self.async_update).start()

    def async_update(self):
        """
        Part of an update that will be run in a seperate thread
        """
        self.config(bg="cyan")
        arguments = inspect.getargspec(self.this_function)
        if arguments[3] is None:
            args = arguments[0]
            args = [self.inputs[key].get_result() for key in args]
            self.result = self.find_function(*args)
        else:
            args = arguments[0][:-len(arguments[3])]  # !!All arguments without value are non keyword!!
            kwargs = arguments[0][-len(arguments[3]):]
            args = [self.inputs[key].get_result() for key in args]
            kwargs = dict(zip([param.name for param in self.parameters],
                              [param.get_value() for param in self.parameters]))
            for param, name in self.inputs.iteritems():
                if arguments[0][-len(arguments[3]):].count(
                        name) > 0:  # If this parameter is not in the nonkeys it must be
                    # a kwarg
                    kwargs[name] = param.get_result()
            self.result = self.find_function(*args, **kwargs)
        self.config(bg="grey")
        [e.update() for e in self.next]

    def help(self):
        """
        Place the docstring provided by this Draggable onto
        the screen
        """
        self.help_message.place(x=self.absx + 10, y=self.absy + 10)

    def add_outputs(self, outputs):
        """
        outputs : list of strings defining inputs
        Paints Outputs as defined in input and returns a
        Dictionary of Outputs
        """
        return dict(zip(outputs, [Result(self, e, self.output_frame) for e in outputs]))

    def get_outputs(self):
        """
        Return the default outputs
        """
        return self.default_outputs

    def all_inputs_set(self):
        """
        Checks whether all inputs have been set correctly
        """
        _is_set = True
        for _input in self.inputs.itervalues():
            if not _input.previous:
                _is_set = False
        return _is_set


class ParameterFrame(Frame):
    """
    Class modelling a Frame were parameters are presentet
    to the users and can be changed
    """

    def __init__(self, parent, draggable, **kwargs):
        """
        parent: the Main Frame
        draggabe: the Draggable object to which this parameter belongs
        """
        Frame.__init__(self, parent, bd=1, relief='raised', **kwargs)
        self.draggable = draggable
        self.parameters = []
        self.close_button = Button(self, text="Close", command=self.hide_me, height=1)
        self.close_button.grid()
        self.parent = parent

    def reload(self):
        """
        check draggable parameters and add them
        """
        for parameter in self.draggable.parameters:
            if self.parameters.count(parameter) == 0:
                self.parameters.append(parameter)
                parameter.grid()

    def hide_me(self):
        """
        Hides this ParameterFrame
        """
        self.place_forget()
        self.draggable.update()


class PvPParameter(Frame):
    """
    This class models a Parameter value pair
    The parameter is called lable and its value can be set
    via an input field
    """

    def __init__(self, parent, label, default_value, **kwargs):
        Frame.__init__(self, parent.param_frame, **kwargs)
        self.draggable = parent
        self.label = Label(self, text=label)
        self.name = label
        self.label.grid(column=0, row=0)
        self.value = Entry(self, width=5)
        self.value.insert(0, default_value)
        self.value.grid(column=1, row=0)
        self.make_input = Button(self, text='ToInput', command=self.inputify)
        self.make_input.grid(column=2, row=0)

    def inputify(self):
        """
        This method is called when the user wants to move
        this PVP to the list of Input Objects of the Draggable
        we belong to
        """
        self.draggable.clear_inputs()
        _inputs = self.draggable.get_inputs()
        _inputs.append(self.name)
        self.draggable.inputs = self.draggable.add_inputs(_inputs)
        self.draggable.parameters.remove(self)

    def get_value(self):
        """
        Return the value currently set
        """
        return self.type_conversion(self.value.get())

    def type_conversion(self, value):
        """
        called to convert the paremter value (string) into deired type
        default = float
        Overide to change behaviour
        """
        return float(value)


class HelpMessage(Frame):
    """
    This Class prsents Help Information to the user
    """

    def __init__(self, parent, this_function):
        Frame.__init__(self, parent, relief='raised', bg='white')
        self.message = Message(self, text=this_function.__doc__, bg='white')
        self.message.pack()
        self.close_button = Button(self, text="Close", command=self.hide_me, height=1)
        self.close_button.pack()

    def hide_me(self):
        """
        Hides this help message
        """
        self.place_forget()


class Parameter:
    def __init__(self, name, _min=None, _max=None, values=None, default=None, position=(0, 0), **kwargs):
        if _min:
            self.name = name
            self._min = _min
            self.max = _max
            self.default = default
        else:
            self.values = values
            self.name = name
            self.default = default
        self.position = position


class MyScale(Scale, Parameter):
    def __init__(self, parent, **kwargs):
        Scale.__init__(self, parent, **kwargs)
        Parameter.__init__(self, **kwargs)
        self.parent = parent
        self.bind("<ButtonRelease-1>", self.update)
        self.bind("<B1-Motion>", self.update)
        self.set(1)

    def get_value(self):
        return self.get()

    def update(self, event):
        self.parent.update()


class MainFrame(Canvas):
    """
    This is the main frame of the GUI. its basically a canvas on which certain
    objects draw lines.Additionally it holds the main menue

    """

    def __init__(self, parent, find_object, **kwargs):
        """
        find_object The Find Object
        """
        Canvas.__init__(self, parent, **kwargs)
        self.canvas = self
        menu = MainMenue(self, find_object)
        parent.config(menu=menu)
        self.active = None
        self.pack()
