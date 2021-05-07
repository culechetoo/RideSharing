from PrevPaper.Algorithm import getRiderMatching
from UtilClasses import Rider, Driver
from Utils import getPathWeight

import networkx as nx


def getDriverRiderBipartiteGraph(problemInstance):
    graph = nx.Graph()
    graph.add_nodes_from(range(problemInstance.nDrivers), bipartite=0)
    graph.add_nodes_from(range(problemInstance.nDrivers, problemInstance.nDrivers+problemInstance.nRiders),
                         bipartite=1)

    driverNodes = {node for node, d in graph.nodes(data=True) if d["bipartite"] == 0}
    riderNodes = {node for node, d in graph.nodes(data=True) if d["bipartite"] == 1}

    for driverNode in driverNodes:
        driver: Driver = problemInstance.drivers[driverNode]
        for riderNode in riderNodes:
            rider: Rider = problemInstance.riders[riderNode-problemInstance.nDrivers]
            graph.add_edge(driverNode, riderNode, weight=getPathWeight([driver.location, rider.sourceLocation],
                                                                       problemInstance.distNorm))

    return graph


def getDriverRiderMatching(problemInstance):
    graph = getDriverRiderBipartiteGraph(problemInstance)
    matching = nx.algorithms.bipartite.minimum_weight_full_matching(graph)

    return matching


def calcDriverRiderMatchingCost(problemInstance, matching):

    matchingCost = 0.0
    for node in matching.keys():
        if node < problemInstance.nDrivers:
            driver: Driver = problemInstance.drivers[node]
            rider: Rider = problemInstance.riders[matching[node]-problemInstance.nDrivers]

            matchingCost += getPathWeight([driver.location, rider.sourceLocation], problemInstance.distNorm)

    return matchingCost


def calcRiderMatchingCost(problemInstance, riderMatching):
    riderMatchingCost = 0.0
    for riderIndexPair in riderMatching:
        rider_i: Rider = problemInstance.riders[riderIndexPair[0]]
        rider_j: Rider = problemInstance.riders[riderIndexPair[1]]

        weightU_ij1 = getPathWeight([rider_i.sourceLocation, rider_j.sourceLocation, rider_i.targetLocation,
                                     rider_j.targetLocation], problemInstance.distNorm)
        weightU_ij2 = getPathWeight([rider_i.sourceLocation, rider_j.sourceLocation, rider_j.targetLocation,
                                     rider_i.targetLocation], problemInstance.distNorm)
        weightU_ij = min(weightU_ij1, weightU_ij2)

        weightU_ji1 = getPathWeight([rider_j.sourceLocation, rider_i.sourceLocation, rider_i.targetLocation,
                                     rider_j.targetLocation], problemInstance.distNorm)
        weightU_ji2 = getPathWeight([rider_j.sourceLocation, rider_i.sourceLocation, rider_j.targetLocation,
                                     rider_i.targetLocation], problemInstance.distNorm)
        weightU_ji = min(weightU_ji1, weightU_ji2)
        riderMatchingCost += min(weightU_ij, weightU_ji)

    return riderMatchingCost


def getLowerBoundCost(problemInstance):
    riderMatching = getRiderMatching(problemInstance)
    riderMatchingCost = calcRiderMatchingCost(problemInstance, riderMatching)

    driverRiderPairMatching = getDriverRiderMatching(problemInstance)
    driverRiderMatchingCost = calcDriverRiderMatchingCost(problemInstance, driverRiderPairMatching)

    return riderMatchingCost+driverRiderMatchingCost
