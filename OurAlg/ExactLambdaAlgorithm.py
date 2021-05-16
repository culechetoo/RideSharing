import math
from itertools import combinations
from typing import List, Tuple

from OurAlg.Utils import mst_st, mst
from Main.UtilClasses import Rider as Request, Rider

import networkx as nx

from Main.Utils import getMinWeightPerfectMatching, getBestDriverRequestGroupCost


def initPartition(problemInstance):
    partition = []

    for request in problemInstance.riders:
        partition.append((request,))

    return partition


def constructPartitionGraph(partitions: List[Tuple[Request]], distNorm="l2"):
    graph = nx.Graph()
    graph.add_nodes_from(partitions)

    partitionPairs = combinations(partitions, 2)

    for partitionPair in partitionPairs:
        partition1 = partitionPair[0]
        partition2 = partitionPair[1]

        edgeWeight = mst_st(partition1 + partition2, distNorm) - mst_st(partition1, distNorm) - \
                     mst_st(partition2, distNorm)

        graph.add_edge(partition1, partition2, weight=edgeWeight)

    return graph


def getExactPartition(problemInstance):
    partitions: List[List[Tuple[Request]]] = [initPartition(problemInstance)]

    i = 0

    while i < math.log2(problemInstance.driverCapacity):
        i += 1
        partition_i: List[Tuple[Request]] = []

        graph_i = constructPartitionGraph(partitions[-1], problemInstance.distNorm)
        matching = getMinWeightPerfectMatching(graph_i)

        for groupPair in matching:
            partition_i.append(groupPair[0] + groupPair[1])

        partitions.append(partition_i)

    return partitions[-1]


def getDriverGroupGraph(problemInstance, partition: List[Tuple[Rider]]):
    graph = nx.Graph()

    graph.add_nodes_from(problemInstance.drivers)
    graph.add_nodes_from(partition)

    for driver in problemInstance.drivers:
        for group in partition:
            edgeWeight = getBestDriverRequestGroupCost(driver, group, problemInstance.distNorm)

            graph.add_edge(driver, group, weight=edgeWeight)

    return graph


def getDriverGroupMatching(problemInstance, partition):
    graph = getDriverGroupGraph(problemInstance, partition)
    driverGroupMatching = getMinWeightPerfectMatching(graph)

    return driverGroupMatching


def run(problemInstance):
    partition = getExactPartition(problemInstance)
    driverGroupMatching = getDriverGroupMatching(problemInstance, partition)

    return driverGroupMatching
