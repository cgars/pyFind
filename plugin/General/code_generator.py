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
import tkFileDialog
import re

from numpy import *

from pyFind.Find import FindPlugin
import pyFind.Find
from plugin.PyFindGUI.PyFindGUI import Draggable


class CodeGenerator(FindPlugin):
    """
    This plugin can create valid Python code corresponding to the
    data flow pipeline it terminates. It is only usefull with the GUI
    """

    @classmethod
    def find_call(cls):
        return dummy_func

    @classmethod
    def get_draggable(cls, parent, find_object):
        return CodeGeneratorDrag(parent, None, None)


class CodeGeneratorDrag(Draggable):
    def __init__(self, parent, this_function, find_function):
        Draggable.__init__(self, parent, this_function, find_function, label='CodeGenerator')
        self.parameter_button.destroy()
        self.file_button = Button(self, text="Save as", command=self.get_file)
        self.file_button.place(x=60, y=20)
        self.get_file()
        self.file = False

    def update(self):
        self.get_result(None)
        Draggable.update(self)

    def get_result(self, hallali):
        self.generate_code(self.previous)

    def get_inputs(self):
        return ['previous']

    def get_parameter(self):
        return []

    def get_file(self):
        if isinstance(self._file, file):
            self._file.close()
        self._file = tkFileDialog.asksaveasfile()

    def generate_code(self, previous):
        histories = [pred.get_result(None).history for pred in previous]
        self.find_object_dic = {}
        _script = ''
        for history in histories:
            for counter, _step in enumerate(history):
                _step_name = _step[0].__name__ + str(counter)
                self.find_object_dic[_step_name] = _step

                _code = _step[0].__name__ + '('
                _code = _code + self.__get__arguments__(_step[1])
                _code += self.__get__kwarguments__(_step[2])
                _code += ')'
                _script += '%s = %s\n' % (_step_name, _code)
        _script = self.__check_for_duplicates__(_script)
        self._file.write(_script)
        self._file.flush()

    def __get__arguments__(self, arguments):
        _tmp = ''
        for arg in arguments:
            _tmp = _tmp + '\'' + self.__check_for_find_data__(arg) + '\'' + ','
        return _tmp.rstrip(',')

    def __get__kwarguments__(self, kwarguments):
        _tmp = ''
        if kwarguments is None:
            return ''
        else:
            _tmp += ','
        for _key, _value in kwarguments.iteritems():
            _tmp = _tmp + '%s = \'%s\'' % (_key, self.__check_for_find_data__(_value)) + ','
        return _tmp.rstrip(',')

    def __check_for_find_data__(self, arg):
        if isinstance(arg, pyFind.Find.FindData):
            for _key, _value in self.find_object_dic.iteritems():
                if _value[3] == arg:
                    return _key
        else:
            return str(arg)

    def __check_for_duplicates__(self, _script):
        """
        Checks the script for duplicate occurencces of statements
        deletes them and resets variables accordingly.
        In some sense its a simple version of checking for circles
        in the workflow graph
        """
        _tmp_script = _script.split('\n')

        for _line in _tmp_script:
            try:
                _variable = _line.split('=', 1)[0]
                _argument = _line.split('=', 1)[1]
                _argument = self.escape__chars(_argument)
                _pattern = '^.+=%s' % (_argument)
                _all = re.findall(_pattern, _script, re.MULTILINE)
                for _occurence in _all[1:]:
                    _script = _script.replace(_occurence, '')
                    _script = _script.replace(_occurence.split('=')[0].rstrip(), _variable.rstrip())

            except:
                print  sys.exc_info()[0]
        return _script

    @staticmethod
    def escape__chars(_pattern):
        _pattern = _pattern.replace('.', '\.')
        _pattern = _pattern.replace('(', '\(')
        _pattern = _pattern.replace(')', '\)')

        return _pattern


def dummy_func():
    """
    Will not do anything
    """
    return None
