# -------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------
import os
import sys
import re
import inspect
import logging
import difflib


class Find(object):
    """
    FIND Base Class
    All Analysis should be done using the FIND object
    """

    def __init__(self, plugin_registry, find_data_class, find_plugin_class,
                 find_history_class, find_event_class):
        """
        :param plugin_registry:
        :type plugin_registry:FindRegistry
        :param find_data_class: Implementation of the FindData Class
        :param find_plugin_class: Implementation of the FindPlugin Class
        :param find_history_class: Implementation of the FindHistory Class
        :return:none
        """
        assert (isinstance(plugin_registry, FindRegistry))
        self.plugin_registry = plugin_registry
        assert issubclass(find_data_class, FindData)
        self.find_data_class = find_data_class
        assert issubclass(find_plugin_class, FindPlugin)
        self.find_plugin_class = find_plugin_class
        assert issubclass(find_history_class, FindHistory)
        self.find_history_class = find_history_class
        assert issubclass(find_event_class, FindEvent)
        self.find_event_class = find_event_class
        self.plugins = plugin_registry.get_plugins(self)
        self.__dict__.update(self.plugins.__dict__)

    def wrap_with_find_data_object(self, func):
        """
        Method that takes care that plugin functionality is decorated in the right way.
        Arguments are searched for FindDataObjects which in turn are transformed into
        normal data types while the history is kept. The function is subsequently called
        and its return wraped with a new FindDataObject with updated history.

        :param: func: The function which is going to be wrapped with Find housekeeping functionality
        :rtype : function
        """

        def _tmp_func(*args, **kwargs):
            _tmp_history = self.find_history_class()
            newargs = []
            newkwargs = {}
            for e in args:
                try:
                    if e.__class__.__name__ == self.find_data_class.__name__:
                        _tmp_history.extend(e.history)
                        newargs.append(e.data)
                    else:
                        newargs.append(e)

                except:
                    pass
            for key, value in kwargs.iteritems():
                try:
                    if value.__class__.__name__ == self.find_data_class.__name__:
                        _tmp_history.extend(value.history)
                        newkwargs[key] = value.data
                    else:
                        newkwargs[key] = value
                except:
                    pass
            _result = self.find_data_class(func(*newargs, **newkwargs))
            _result.history.extend(_tmp_history)
            _result.history.document(self.find_event_class([func, args, kwargs, _result]))
            return _result

        _tmp_func.__doc__ = func.__doc__
        logging.debug('Have wrapped %s and return it as %s' % (func, _tmp_func))
        return _tmp_func


class FindRegistry(object):
    """
    This class is responsible for managing the Find plugins
    """

    def get_plugins(self, find_object):
        """
        This method should return the availible plugins wrapped in a FindPluginContainer
        Each Plugin is either a field in the container or wrapped in another container
        Each plugin must be callable and properly wrapped with Find functionality
        (use wrap_with_find_data_object of the Find object)
        :param find_object: The Find object asking for plugins
        :rtype FindPluginContainer
        """
        pass


class FindPlugin(object):
    """
    FindPlugin class is mainly there to inherit from
    """

    def __init__(self):
        pass

    def find_call(self):
        pass


class FindHistory(list):
    """
    Class to manage history of FindData Objects
    """

    def __init__(self):
        """
        initialize object
        """
        list.__init__(self)

    def document(self, event):
        """
        Document the event event in the history
        """
        self.append(event)

    def __repr__(self):
        return str([e for e in self])


class FindEvent(list):
    """
    FindEvents model one analysis step
    """

    def __init__(self, _input):
        """
        :param _input: A iteratable with four entries [function called, args, kwargs, result]
        :type: list
        :return:none
        """
        list.__init__(self)
        self.extend(_input)


class FindData(object):
    """
    Find internal Data class mainly wrapping other data types and
    annotating them with some history
    """

    def __init__(self, _data):
        self.data = _data
        self.history = FindHistory()

    def __repr__(self):
        return str({'history': self.history})

    def get_sub_result(self, _index):
        _sub_result = FindData(self.data[_index])
        _sub_result.history.document(FindEvent([self.get_sub_result, _index, {}, self]))
        return _sub_result

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        return self.data.__iter__()

    def __getitem__(self, key):
        return self.data.__getitem__(key)


class FindPluginContainer(object):
    def __init__(self):
        pass


class FindMetaDataDict(dict):
    """Provides a dictionary that performs fuzzy lookup"""

    def __init__(self, items=None, cutoff=.6, **kwargs):
        """Construct a new FuzzyDict instance

            items is an dictionary to copy items from (optional)
            cutoff is the match ratio below which matches should not be considered
            cutoff needs to be a float between 0 and 1 (where zero is no match
            and 1 is a perfect match)"""
        super(FindMetaDataDict, self).__init__(**kwargs)
        if items:
            self.update(items)
        self.cutoff = cutoff

    def _search(self, lookfor, stop_on_first=False):
        """Returns the value whose key best matches lookfor

        if stop_on_first is True then the method returns as soon
        as it finds the first item
        """

        # if the item is in the dictionary then just return it
        if self._dict_contains(lookfor):
            return True, lookfor, self._dict_getitem(lookfor), 1

        # set up the fuzzy matching tool
        ratio_calc = difflib.SequenceMatcher()
        ratio_calc.set_seq1(lookfor)

        # test each key in the dictionary
        best_ratio = 0
        best_match = None
        best_key = None
        for key in self:

            # if the current key is not a string
            # then we just skip it
            try:
                # set up the SequenceMatcher with other text
                ratio_calc.set_seq2(key)
            except TypeError:
                continue

            # we get an error here if the item to look for is not a
            # string - if it cannot be fuzzy matched and we are here
            # this it is defintely not in the dictionary
            try:
                # calculate the match value
                ratio = ratio_calc.ratio()
            except TypeError:
                break

            # if this is the best ratio so far - save it and the value
            if ratio > best_ratio:
                best_ratio = ratio
                best_key = key
                best_match = self._dict_getitem(key)

            if stop_on_first and ratio >= self.cutoff:
                break

        return (
            best_ratio >= self.cutoff,
            best_key,
            best_match,
            best_ratio)

    def __contains__(self, item):
        """Overides Dictionary __contains__ to use fuzzy matching"""
        if self._search(item, True)[0]:
            return True
        else:
            return False

    def __getitem__(self, lookfor):
        """Overides Dictionary __getitem__ to use fuzzy matching"""
        matched, key, item, ratio = self._search(lookfor)

        if not matched:
            raise KeyError(
                "'%s'. closest match: '%s' with ratio %.3f" %
                (str(lookfor), str(key), ratio))

        return item


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


class TreeWalkRegistry(FindRegistry):
    """

    """

    def __init__(self, pluginpath):
        assert isinstance(pluginpath, str)
        self.pluginpath = pluginpath

    def get_plugins(self, find_obj):
        """

        :type self: TreeWalkRegistry
        :type self: Find
        """
        base_path = os.getcwd()
        logging.debug('Will now start walking %s' % self.pluginpath)
        self.plugins = self.__walk_plugins__(FindPluginContainer(), [(e, i, j) for e, i, j in os.walk(
            self.pluginpath)], find_obj)
        os.chdir(base_path)
        return self.plugins

    def __walk_plugins__(self, parent, tree, find_obj):
        """
        Recursivly walk through the plugin directory and its subfolders and add
        valid plugins in a Treelike Fashion
        :rtype : object
        """
        parent = FindPluginContainer()
        if len(tree[0][1]) > 0:
            for _subfolder in tree[0][1]:
                sys.path.append(os.path.join(tree[0][0], _subfolder))
                logging.debug('Added %s to the path' % os.path.join(tree[0][0],
                                                                    _subfolder))
                _node_name = tree[0][0].rpartition(os.sep)[2]
                _tmp = FindPluginContainer()
                _subtree = self.__walk_plugins__(_tmp, [(e, i, j) for e, i, j
                                                        in os.walk(tree[0][0] + '/' + _subfolder)], find_obj)
                parent.__dict__[_subfolder] = _subtree
                logging.debug('Have added %s with name %s as a child to %s' % (
                    _subtree, _subfolder, parent))
        TreeWalkRegistry.__add_plugins__(parent, TreeWalkRegistry.__check_for_plugins__(tree[0][2], find_obj), find_obj)
        return parent

    @staticmethod
    def __add_plugins__(parent, plugins, find_obj):
        """
        Check whether plugins contains a class inhereting from FindPlugin
        if so wrap some documenting and FindData stuff around it and add
        the resulting Function Object as Attribute to the parentObject
        """
        for plugin in plugins:
            _tmp_func = find_obj.wrap_with_find_data_object(plugin[1].find_call())
            _name = plugin[0]
            parent.__dict__[_name] = _tmp_func
            logging.debug('Have added %s with name %s as a child to %s' % (_tmp_func, _name, parent))

    @staticmethod
    def __check_for_plugins__(_files, find_obj):
        """
        returns a list of all valid plugins in _files
        """
        _plugin_files = filter(lambda x: re.search('.+py$', x) is not None, _files)
        _plugins = []
        for plugin in _plugin_files:
            _plugins.extend(
                filter(lambda x: issubclass(x[1], find_obj.find_plugin_class)
                                 and not x[1].__name__ == find_obj.find_plugin_class.__name__,
                       inspect.getmembers(
                           __import__(plugin.split('.')[0]),
                           inspect.isclass))
            )
        logging.debug('Will now add plugins %s' % _plugins)
        return _plugins


h = NullHandler()
# logging.getLogger("foo").addHandler(h)
