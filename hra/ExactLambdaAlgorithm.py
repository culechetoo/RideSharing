import math
from math import log2
from os import remove
from time import time

import numpy as np
from h5py import File

from numpy.linalg import norm
from numpy import array, uint32, rint, min, argwhere, max, arange, broadcast_to, newaxis, stack, hstack

from hra.Utils import getDistEvenRequestGroups_v, getDistOddRequestGroups_v

from graph_tool.all import Graph, max_cardinality_matching
from graph_tool.generation import complete_graph


def matchingAlgorithm(graph, weightProp, bipartite=False, useMatchingHeuristic=False, getEdgeProperty=False,
                      partitions=None):

    matching = max_cardinality_matching(graph, weight=weightProp, bipartite=bipartite, heuristic=useMatchingHeuristic,
                                        edges=getEdgeProperty)

    if getEdgeProperty:
        return argwhere(matching.get_array() == 1)

    assert partitions is not None

    partition1 = partitions[0] if len(partitions[0]) <= len(partitions[1]) else partitions[1]

    finalMatching = stack([partition1, matching.a[partition1]], axis=1)

    return finalMatching


def decompose(x):
    powers = []
    i = 1
    while i <= x:
        if i & x:
            powers.append(1)
        else:
            powers.append(0)
        i <<= 1
    return powers


def constructPartitionGraph_v(partition, interSourceDists, interTargetDists):
    weights = getDistEvenRequestGroups_v(partition, interSourceDists, interTargetDists)
    graph = complete_graph(len(partition))
    weightProp = graph.new_ep("int32_t")
    weightProp.a = weights
    return graph, weightProp


def constructBiPartiteGraph_v(requestGroup1, requestGroup2, requestI2, interSourceDists, interTargetDists):

    weights = getDistOddRequestGroups_v(requestGroup1, requestGroup2, requestI2, interSourceDists, interTargetDists)
    graph = Graph(directed=False)
    graph.add_vertex(len(requestGroup1)+len(requestGroup2))
    weightProp = graph.new_ep("int32_t")

    edges = stack([np.repeat(np.arange(len(requestGroup1)), len(requestGroup2)),
                   np.tile(np.arange(len(requestGroup2)), len(requestGroup1))+len(requestGroup1),
                   weights]).T

    graph.add_edge_list(edges, eprops=[weightProp])

    return graph, weightProp


def getExactPartition_v(interSourceDists, interTargetDists, carCapacity, showRunTime=False, useMatchingHeuristic=True):
    nRiders = interSourceDists.shape[0]

    partition = np.fromiter(range(nRiders), dtype=int)

    partitions = [partition]

    i = 0

    leastLog = math.floor(log2(carCapacity))

    while i < leastLog:
        i += 1

        currTime = time()

        graph_i, weightProp = constructPartitionGraph_v(partition, interSourceDists, interTargetDists)

        if showRunTime:
            print("graph constructed in %f" % (time() - currTime))

        currTime = time()
        # pool = multiprocessing.Pool(processes=1)
        # matching = pool.apply_async(matchingAlgorithm, (graph_i, useMatchingHeuristic, True)).get()
        # pool.close()
        # pool.join()
        partition = matchingAlgorithm(graph_i, weightProp, False, useMatchingHeuristic, True)

        partitions.append(partition)

        if showRunTime:
            print("matching done in %f" % (time() - currTime))

        del graph_i, weightProp

    mstCacheFile = File("mstCacheEven.h5", 'r')
    mstCache = mstCacheFile["mstCache%d" % leastLog][:]
    mstCacheFile.close()

    if 2**leastLog != carCapacity:

        powers2 = decompose(carCapacity)

        remCapacity = carCapacity-2**leastLog
        nRemRiders = nRiders*remCapacity//carCapacity
        groupIndices = np.argsort(mstCache[partition], axis=0)
        bestGroupIndices = partition[groupIndices[:groupIndices.shape[0]-nRemRiders//(2**leastLog)]].squeeze()
        remGroupIndices = groupIndices[groupIndices.shape[0]-nRemRiders//(2**leastLog):].squeeze()

        i = leastLog-1

        prevGroupIndices = partition[remGroupIndices].squeeze()
        while i >= 0:

            prevGroupIndices = partitions[i][np.stack(np.triu_indices(len(partitions[i]), 1), 1)][prevGroupIndices].squeeze().flatten()

            if powers2[i] == 1:

                graph, weightProp = constructBiPartiteGraph_v(bestGroupIndices, prevGroupIndices, i, interSourceDists,
                                                              interTargetDists)
                matching = matchingAlgorithm(graph, weightProp, bipartite=True, useMatchingHeuristic=useMatchingHeuristic,
                                             partitions=[np.arange(len(bestGroupIndices)),
                                                         np.arange(len(prevGroupIndices)) + len(bestGroupIndices)])

                matching[:, 1] -= len(bestGroupIndices)
                bestGroupIndices = matching[:, 0]*len(prevGroupIndices)+matching[:, 1]
                prevGroupIndices = np.delete(prevGroupIndices, matching[:, 1])

            i -= 1

        partition = bestGroupIndices

        mstCacheFile = File("mstCacheOdd.h5", 'r')
        requestGroupSet = mstCacheFile["requestGroupSet"][:]
        mstCacheFile.close()

    else:
        mstCacheFile = File("mstCacheEven.h5", 'r')
        requestGroupSet = mstCacheFile["requestGroupSet%d" % leastLog][:]
        mstCacheFile.close()

    exactPartition = array(
        [(requestGroupSet[requestGroupSetIndex].tolist()) for requestGroupSetIndex in partition.squeeze()])

    return exactPartition


def getBestCarRequestGroupCost(carLocation, requestGroup, riderSources):
    requestLocations = riderSources[requestGroup, :]
    dists = norm(carLocation - requestLocations, axis=1)
    val = rint(min(dists))

    return val


def getCarGroupGraph(carSourceDists, partition):
    nCars = carSourceDists.shape[0]
    carCapacity = partition.shape[1]

    riderGroupBaseIndex = nCars
    carNodes = arange(nCars)
    riderGroupNodes = arange(riderGroupBaseIndex, riderGroupBaseIndex + len(partition))

    graph = Graph(directed=False)
    graph.add_vertex(nCars + len(partition))

    edges = stack([broadcast_to(carNodes[:, newaxis], (nCars, *carNodes.shape)).reshape(-1),
                   broadcast_to(riderGroupNodes, (nCars, *riderGroupNodes.shape)).reshape(-1),
                   rint(carSourceDists[broadcast_to(carNodes[:, newaxis], (nCars, *carNodes.shape)).reshape(-1, 1),
                                       broadcast_to(partition, (nCars, *partition.shape))
                                       .reshape(nCars * nCars, carCapacity)]
                        .min(axis=1))]).T

    edges[:, 2] = max(edges[:, 2]) - edges[:, 2] + 1
    edges = edges.astype(uint32)

    weightProp = graph.new_ep("int32_t")
    graph.add_edge_list(edges, eprops=[weightProp])

    return graph, weightProp


def getCarGroupMatching(carSourceDists, partition, useMatchingHeuristic=False):
    nCars = carSourceDists.shape[0]

    graph, weightProp = getCarGroupGraph(carSourceDists, partition)
    carGroupMatching = matchingAlgorithm(graph, weightProp, bipartite=True, useMatchingHeuristic=useMatchingHeuristic,
                                         partitions=[np.arange(nCars), np.arange(len(partition))+nCars])

    finalMatching = hstack([carGroupMatching[:, 0].reshape(-1, 1), partition[carGroupMatching[:, 1] - nCars]])

    return finalMatching


def run(carSourceDists, interRiderDists, interTargetDists, showRunTime=False, useMatchingHeuristic=False):
    try:
        remove("mstCacheEven.h5")
        remove("mstCacheOdd.h5")
    except FileNotFoundError:
        pass

    currTime = time()

    carCapacity = interRiderDists.shape[0] // carSourceDists.shape[0]

    partition = getExactPartition_v(interRiderDists, interTargetDists, carCapacity, showRunTime)
    if showRunTime:
        print("partition found in %f" % (time() - currTime))

    carGroupMatching = getCarGroupMatching(carSourceDists, partition, useMatchingHeuristic)

    try:
        remove("mstCacheEven.h5")
        remove("mstCacheOdd.h5")
    except FileNotFoundError:
        pass

    return carGroupMatching
