# -------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
# -------------------------------------------------------------------------------
from scipy.cluster.vq import kmeans2, whiten
from scipy.signal import resample

from numpy import *

from plugin.PyFindGUI.PyFindGUI import Draggable
from pyFind.Find import FindPlugin


class SortSpikes(FindPlugin):
    def __init__(self):
        pass

    @classmethod
    def find_call(cls):
        return sort_spikes

    @classmethod
    def get_draggable(cls, parent, find_object):
        return SpikeSortDrag(parent, sort_spikes, find_object.spikeTools.SortSpikes)


class SpikeSortDrag(Draggable):
    def __init__(self, parent, this_function, find_function):
        Draggable.__init__(self, parent, this_function, find_function,
                           outputs=['op1'], label='Spike Sorting')


def sort_spikes(samples, n_clusters=5, reduction_method=0):
    """Performs spike sorting on Segment Data.
    dimension reduction with
    resampling (reduction_method == 0)
    or feature extraction (reduction_method == 1)
    clustering with kmeans
    performs pca for analysis

    n_clusters: number of clusters to sort spikes into with kmeans
    """
    samples = array(samples)

    if reduction_method:
        # feature extraction: get extreme value and integral
        maxima = []
        # get maximum value of each sample
        # abs(samples).argmax(axis=1) gets index of the extreme
        # value of each sample
        abs_samples = abs(samples)
        for i1, i2 in enumerate(abs_samples.argmax(axis=1)):
            maxima.append(samples[i1][i2])
        integral = sum(abs_samples, 1)
        reduced_data = array(zip(maxima, integral))
    else:
        # resampling:
        reduced_data = []
        for sample in samples:
            if sample.shape[0] > 44:
                reduced_data.append(resample(sample, 44))
            else:
                reduced_data.append(sample)

    # Clustering with kmeans
    # kmeans
    cluster_id = kmeans2(whiten(reduced_data), n_clusters)[1]
    clusters = []
    for _number in range(n_clusters):
        clusters.append(filter(lambda x: x[1] == _number, zip(samples, cluster_id)))

    return [[item[0] for item in cluster] for cluster in clusters]
