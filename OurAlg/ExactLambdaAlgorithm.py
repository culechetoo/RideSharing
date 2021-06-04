import math
import time
from typing import List, FrozenSet, Tuple

import OurAlg.Utils
from OurAlg.Utils import getDistRequestGroups
from Main.UtilClasses import Rider as Request, Rider

import graphLib as graphLib

from Main.Utils import getBestDriverRequestGroupCost

graphLibrary = "networkx"


def initPartition(problemInstance):
    partition = []

    for request in problemInstance.riders:
        partition.append(frozenset({request}))

    return partition


def constructPartitionGraph(partitions: List[FrozenSet[Request]], distNorm="l2"):
    graph = graphLib.getGraph(graphLibrary)
    graph.addNodes(range(len(partitions)))

    def edgeWeightFunction(node1: int, node2: int) -> float:
        return getDistRequestGroups(partitions[node1], partitions[node2], distNorm)

    graph.makeCompleteWeightedGraph(edgeWeightFunction)

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
            print("graphLib constructed in %f" % (time.time() - currTime))

        currTime = time.time()
        matchingAlgorithm = graphLib.getMatching(graphLibrary)
        matching = matchingAlgorithm(graph_i)
        if showRunTime:
            print("graphAlg found in %f" % (time.time() - currTime))

        for partitionIndex1, partitionIndex2 in matching:
            partition_i.append(partition[partitionIndex1].union(partition[partitionIndex2]))

        partition = partition_i

    exactPartition = [tuple(requestGroup) for requestGroup in partition]

    return exactPartition


def getDriverGroupGraph(problemInstance, partition: List[Tuple[Rider]]):
    riderGroupBaseIndex = problemInstance.nDrivers
    driverNodes = range(problemInstance.nDrivers)
    riderGroupNodes = range(riderGroupBaseIndex, riderGroupBaseIndex + len(partition))

    graph = graphLib.getGraph(graphLibrary)
    graph.addNodes(driverNodes)
    graph.addNodes(riderGroupNodes)

    def edgeWeightFunction(driverIndex: int, groupIndex: int) -> float:
        return getBestDriverRequestGroupCost(problemInstance.drivers[driverIndex],
                                             partition[groupIndex - riderGroupBaseIndex], problemInstance.distNorm)

    graph.makeCompleteWeightedGraph(edgeWeightFunction, partitions=[driverNodes, riderGroupNodes])

    return graph


def getDriverGroupMatching(problemInstance, partition):
    graph = getDriverGroupGraph(problemInstance, partition)
    matchingAlgorithm = graphLib.getMatching(graphLibrary)
    driverGroupMatching = matchingAlgorithm(graph)

    finalMatching = []

    riderGroupBaseIndex = problemInstance.nDrivers

    for index1, index2 in driverGroupMatching:
        if index1 >= riderGroupBaseIndex:
            groupIndex = index1 - riderGroupBaseIndex
            driverIndex = index2
        else:
            groupIndex = index2 - riderGroupBaseIndex
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
        print("partition found in %f" % (time.time() - currTime))

    driverGroupMatching = getDriverGroupMatching(problemInstance, partition)

    return driverGroupMatching
