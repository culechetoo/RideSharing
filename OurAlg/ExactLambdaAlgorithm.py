import math
import time
from itertools import combinations
from typing import List, FrozenSet, Tuple

import OurAlg.Utils
from OurAlg.Utils import getDistRequestGroups
from Main.UtilClasses import Rider as Request, Rider, Driver

import networkx as nx

from Main.Utils import getMinWeightPerfectMatching, getBestDriverRequestGroupCost


def initPartition(problemInstance):
    partition = []

    for request in problemInstance.riders:
        partition.append(frozenset({request}))

    return partition


def constructPartitionGraph(partitions: List[FrozenSet[Request]], distNorm="l2"):

    graph = nx.Graph()
    graph.add_nodes_from(range(len(partitions)))

    partitionIndexPairs = combinations(range(len(partitions)), 2)

    edges = []

    for partitionIndex1, partitionIndex2 in partitionIndexPairs:
        partition1 = partitions[partitionIndex1]
        partition2 = partitions[partitionIndex2]

        edgeWeight = getDistRequestGroups(partition1, partition2, distNorm)

        edges.append((partitionIndex1, partitionIndex2, edgeWeight))

    graph.add_weighted_edges_from(edges)

    return graph


def getExactPartition(problemInstance, showRunTime=False):

    partition: List[FrozenSet[Request]] = initPartition(problemInstance)

    i = 0

    while i < math.log2(problemInstance.driverCapacity):
        i += 1
        partition_i: List[FrozenSet[Request]] = []

        currTime = time.time()
        graph_i = constructPartitionGraph(partition, problemInstance.distNorm)
        if showRunTime:
            print("graph constructed in %f" % (time.time()-currTime))

        currTime = time.time()
        matching = getMinWeightPerfectMatching(graph_i)
        if showRunTime:
            print("matching found in %f" % (time.time()-currTime))

        for partitionIndex1, partitionIndex2 in matching:
            partition_i.append(partition[partitionIndex1].union(partition[partitionIndex2]))

        partition = partition_i

    exactPartition = [tuple(requestGroup) for requestGroup in partition]

    return exactPartition


def getDriverGroupGraph(problemInstance, partition: List[Tuple[Rider]]):
    graph = nx.Graph()

    riderGroupBaseIndex = problemInstance.nDrivers

    graph.add_nodes_from(range(problemInstance.nDrivers))
    graph.add_nodes_from(range(riderGroupBaseIndex, riderGroupBaseIndex+len(partition)))

    edges = []

    for driverIndex in range(problemInstance.nDrivers):
        for groupIndex in range(len(partition)):
            driver: Driver = problemInstance.drivers[driverIndex]
            group = partition[groupIndex]

            edgeWeight = getBestDriverRequestGroupCost(driver, group, problemInstance.distNorm)

            edges.append((driverIndex, groupIndex+riderGroupBaseIndex, edgeWeight))

    graph.add_weighted_edges_from(edges)

    return graph


def getDriverGroupMatching(problemInstance, partition):
    graph = getDriverGroupGraph(problemInstance, partition)
    driverGroupMatching = getMinWeightPerfectMatching(graph)

    finalMatching = []

    riderGroupBaseIndex = problemInstance.nDrivers

    for index1, index2 in driverGroupMatching:
        if index1 >= riderGroupBaseIndex:
            groupIndex = index1-riderGroupBaseIndex
            driverIndex = index2
        else:
            groupIndex = index2-riderGroupBaseIndex
            driverIndex = index1

        group = partition[groupIndex]
        driver = problemInstance.drivers[driverIndex]

        finalMatching.append((driver, group))

    return finalMatching


def run(problemInstance, showRunTime=False):

    OurAlg.Utils.mstCache.clear()

    currTime = time.time()

    partition = getExactPartition(problemInstance, showRunTime)
    if showRunTime:
        print("partition found in %f" % (time.time()-currTime))

    driverGroupMatching = getDriverGroupMatching(problemInstance, partition)

    return driverGroupMatching
