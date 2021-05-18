import itertools
import math
import time
from itertools import combinations
from typing import List, FrozenSet, Set, Tuple

import networkx as nx

import OurAlg.Utils
from Main.UtilClasses import Rider, Driver
from Main.Utils import getMinWeightPerfectMatching
from OurAlg.Utils import getDistRequestGroupSets, mst


def initPartitionSet(problemInstance):
    partitionSetSet = []

    for request in problemInstance.riders:
        partitionSetSet.append(frozenset([frozenset([request])]))

    return partitionSetSet


def constructPartitionSetGraph(partitionSets: List[FrozenSet[FrozenSet[Rider]]], distNorm="l2"):
    graph = nx.Graph()
    graph.add_nodes_from(range(len(partitionSets)))

    partitionSetIndexPairs = combinations(range(len(partitionSets)), 2)

    edges = []
    edgeGroups = {}
    edgeMethods = {}

    for partitionSetIndex1, partitionSetIndex2 in partitionSetIndexPairs:
        partitionSet1 = partitionSets[partitionSetIndex1]
        partitionSet2 = partitionSets[partitionSetIndex2]

        edgeWeight, groups, method = getDistRequestGroupSets(partitionSet1, partitionSet2, distNorm)

        edges.append((partitionSetIndex1, partitionSetIndex2, edgeWeight))
        edgeGroups[(partitionSetIndex1, partitionSetIndex2)] = groups
        edgeMethods[(partitionSetIndex1, partitionSetIndex2)] = method

    graph.add_weighted_edges_from(edges)
    nx.set_edge_attributes(graph, edgeGroups, "groups")
    nx.set_edge_attributes(graph, edgeMethods, "method")

    return graph


def getBoundedPartition(problemInstance):
    partitionSetSets: List[List[FrozenSet[FrozenSet[Rider]]]] = [initPartitionSet(problemInstance)]

    i = 0

    while i < math.log2(problemInstance.driverCapacity):
        i += 1
        partitionSet_i: List[FrozenSet[FrozenSet[Rider]]] = []

        graph_i = constructPartitionSetGraph(partitionSetSets[-1], problemInstance.distNorm)
        matching = getMinWeightPerfectMatching(graph_i)

        for match in matching:

            attr = graph_i.get_edge_data(*match)

            group1 = attr["groups"][0]
            group2 = attr["groups"][1]

            groupSet1: Set[FrozenSet[Rider]] = set(partitionSetSets[-1][match[0]])
            groupSet2: Set[FrozenSet[Rider]] = set(partitionSetSets[-1][match[1]])

            if attr["method"] == "w1":
                if group1 in groupSet1:
                    groupSet1.remove(group1)
                    groupSet2.remove(group2)
                else:
                    groupSet2.remove(group1)
                    groupSet1.remove(group2)

                partitionSet_i.append(frozenset(groupSet1.union(groupSet2).union({group1.union(group2)})))

            elif attr["method"] == "w2":
                partitionSet_i.append(frozenset(groupSet1.union(groupSet2)))

        partitionSetSets.append(partitionSet_i)

    partition = [tuple(requestGroup) for requestGroupSet in partitionSetSets[-1] for requestGroup in requestGroupSet]

    return partition


def getMinSourceDistGroup(group1: Tuple[Rider], group2: Tuple[Rider], distNorm="l2"):

    minDist = 1e9
    minRiderIndex1 = -1
    minRiderIndex2 = -1

    for riderInd1 in range(len(group1)):
        for riderInd2 in range(len(group2)):
            rider1 = group1[riderInd1]
            rider2 = group2[riderInd2]
            dist = rider1.sourceLocation.getDistance(rider2.sourceLocation, distNorm)
            if dist < minDist:
                minDist = dist
                minRiderIndex1 = riderInd1
                minRiderIndex2 = riderInd2

    return minDist, minRiderIndex1, minRiderIndex2


def getMinDistGroupDrivers(drivers: List[Driver], group: Tuple[Rider], distNorm="l2"):

    minDist = 1e9
    minDriverIndex = -1
    minRiderIndex = -1

    for riderIndex in range(len(group)):
        for driverIndex in range(len(drivers)):
            driver = drivers[driverIndex]
            rider = group[riderIndex]
            dist = rider.sourceLocation.getDistance(driver.location, distNorm)
            if dist < minDist:
                minDist = dist
                minDriverIndex = driverIndex
                minRiderIndex = rider

    return minDist, minDriverIndex, minRiderIndex


def constructDriverPartitionGraph(problemInstance, partition):

    graph = nx.Graph()

    riderGroupBaseIndex = 1

    graph.add_node(0)
    graph.add_nodes_from(range(riderGroupBaseIndex, riderGroupBaseIndex+len(partition)))

    edges = []
    edgeRiderIndices = {}

    groupIndexPairs = itertools.combinations(range(len(partition)), 2)

    for groupIndex1, groupIndex2 in groupIndexPairs:
        group1 = partition[groupIndex1]
        group2 = partition[groupIndex2]

        edgeWeight, riderIndex1, riderIndex2 = getMinSourceDistGroup(group1, group2, problemInstance.distNorm)

        edges.append((riderGroupBaseIndex+groupIndex1, riderGroupBaseIndex+groupIndex2, edgeWeight))
        edgeRiderIndices[(riderGroupBaseIndex+groupIndex1, riderGroupBaseIndex+groupIndex2)] = (riderIndex1,
                                                                                                riderIndex2)

    graph.add_weighted_edges_from(edges)
    nx.set_edge_attributes(graph, edgeRiderIndices, "riderIndices")

    edges = []
    edgeDriverIndices = {}
    edgeRiderIndices = {}

    for groupIndex in range(len(partition)):
        group = partition[groupIndex]

        edgeWeight, driverIndex, riderIndex = getMinDistGroupDrivers(problemInstance.drivers, group,
                                                                     problemInstance.distNorm)

        edges.append((0, riderGroupBaseIndex+groupIndex, edgeWeight))
        edgeDriverIndices[(0, riderGroupBaseIndex+groupIndex)] = driverIndex
        edgeRiderIndices[(0, riderGroupBaseIndex+groupIndex)] = riderIndex

    graph.add_weighted_edges_from(edges)
    nx.set_edge_attributes(graph, edgeDriverIndices, "driverIndex")
    nx.set_edge_attributes(graph, edgeDriverIndices, "riderIndex")

    return graph


def getDriverRiderGroupForest(problemInstance, partition: List[Tuple[Rider]]):

    graph = constructDriverPartitionGraph(problemInstance, partition)
    driverRiderGroupTree: nx.Graph = mst(graph)

    relabelMapping = {(index+1): partition[index] for index in range(len(partition))}

    neighbours = [data for data in driverRiderGroupTree[0].items()]

    Forest = []
    for partitionIndex, edgeAttributes in neighbours:
        driver = problemInstance.drivers[edgeAttributes["driverIndex"]]
        riderSource = problemInstance.riders[edgeAttributes["riderIndex"]]

        driverRiderGroupTree.remove_edge(0, partitionIndex)
        riderGroupTree: nx.DiGraph = nx.dfs_tree(driverRiderGroupTree, partitionIndex)
        riderGroupTree = nx.relabel_nodes(riderGroupTree, relabelMapping)
        Forest.append((driver, riderGroupTree, riderSource))

    return Forest


def run(problemInstance, showRunTime=False):

    OurAlg.Utils.mstCache.clear()

    currTime = time.time()

    partition = getBoundedPartition(problemInstance)
    if showRunTime:
        print("partition found in %f" % (time.time()-currTime))

    currTime = time.time()

    driverGroupMatching = getDriverRiderGroupForest(problemInstance, partition)
    if showRunTime:
        print("matching found in %f" % (time.time()-currTime))

    return driverGroupMatching
