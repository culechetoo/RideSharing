import networkx as nx
from itertools import combinations

from Main.UtilClasses import *
from Main.Utils import getPathWeight, getMinWeightPerfectMatching, getBestDriverRequestGroupCost


def getBestRiderPairCostMax(rider1: Rider, rider2: Rider, distNorm):
    weightU_ij1 = getPathWeight([rider1.sourceLocation, rider2.sourceLocation, rider1.targetLocation,
                                 rider2.targetLocation], distNorm)
    weightU_ij2 = getPathWeight([rider1.sourceLocation, rider2.sourceLocation, rider2.targetLocation,
                                 rider1.targetLocation], distNorm)
    weightU_ij = min(weightU_ij1, weightU_ij2)

    weightU_ji1 = getPathWeight([rider2.sourceLocation, rider1.sourceLocation, rider1.targetLocation,
                                 rider2.targetLocation], distNorm)
    weightU_ji2 = getPathWeight([rider2.sourceLocation, rider1.sourceLocation, rider2.targetLocation,
                                 rider1.targetLocation], distNorm)
    weightU_ji = min(weightU_ji1, weightU_ji2)

    edgeWeight = max(weightU_ij, weightU_ji)
    
    return edgeWeight


def getBestRiderPairCostMin(rider1: Rider, rider2: Rider, distNorm):
    weightU_ij1 = getPathWeight([rider1.sourceLocation, rider2.sourceLocation, rider1.targetLocation,
                                 rider2.targetLocation], distNorm)
    weightU_ij2 = getPathWeight([rider1.sourceLocation, rider2.sourceLocation, rider2.targetLocation,
                                 rider1.targetLocation], distNorm)
    weightU_ij = min(weightU_ij1, weightU_ij2)

    weightU_ji1 = getPathWeight([rider2.sourceLocation, rider1.sourceLocation, rider1.targetLocation,
                                 rider2.targetLocation], distNorm)
    weightU_ji2 = getPathWeight([rider2.sourceLocation, rider1.sourceLocation, rider2.targetLocation,
                                 rider1.targetLocation], distNorm)
    weightU_ji = min(weightU_ji1, weightU_ji2)

    edgeWeight = min(weightU_ij, weightU_ji)

    return edgeWeight


def generateRiderPairGraph(problemInstance, edgeWeightFunction):

    graph = nx.Graph()
    graph.add_nodes_from(range(problemInstance.nRiders))

    riderIndexPairs = combinations(range(problemInstance.nRiders), 2)

    edges = []

    for riderIndex1, riderIndex2 in riderIndexPairs:

        rider1: Rider = problemInstance.riders[riderIndex1]
        rider2: Rider = problemInstance.riders[riderIndex2]

        edgeWeight = edgeWeightFunction(rider1, rider2, problemInstance.distNorm)
        
        edges.append((riderIndex1, riderIndex2, edgeWeight))

    graph.add_weighted_edges_from(edges)

    return graph


def getRiderMatching(problemInstance, edgeWeightFunction):

    graph = generateRiderPairGraph(problemInstance, edgeWeightFunction)
    matching = getMinWeightPerfectMatching(graph)

    finalMatching = []

    for riderIndex1, riderIndex2 in matching:

        rider1 = problemInstance.riders[riderIndex1]
        rider2 = problemInstance.riders[riderIndex2]

        finalMatching.append((rider1, rider2))

    return finalMatching


def generateDriverRiderPairGraph(problemInstance, riderMatching):

    graph = nx.Graph()

    graphRiderIndexBase = problemInstance.nDrivers

    graph.add_nodes_from(range(problemInstance.nDrivers))
    graph.add_nodes_from(range(graphRiderIndexBase, graphRiderIndexBase+len(riderMatching)))

    edges = []

    for driverIndex in range(problemInstance.nDrivers):
        driver: Driver = problemInstance.drivers[driverIndex]

        for riderMatchingIndex in range(len(riderMatching)):

            rider1, rider2 = riderMatching[riderMatchingIndex]

            edgeWeight = getBestDriverRequestGroupCost(driver, (rider1, rider2), problemInstance.distNorm)

            edges.append((driverIndex, riderMatchingIndex+graphRiderIndexBase, edgeWeight))

    graph.add_weighted_edges_from(edges)

    return graph


def getDriverRiderMatching(problemInstance, riderMatching):

    graph = generateDriverRiderPairGraph(problemInstance, riderMatching)
    matching = getMinWeightPerfectMatching(graph)

    finalMatching = []

    graphRiderIndexBase = problemInstance.nDrivers

    for index1, index2 in matching:
        if index1 >= graphRiderIndexBase:
            riderMatchingIndex = index1 - graphRiderIndexBase
            driverIndex = index2
        else:
            riderMatchingIndex = index2 - graphRiderIndexBase
            driverIndex = index1

        driver = problemInstance.drivers[driverIndex]
        rider1, rider2 = riderMatching[riderMatchingIndex]

        finalMatching.append((driver, (rider1, rider2)))

    return finalMatching


def run(problemInstance):

    riderMatching = getRiderMatching(problemInstance, getBestRiderPairCostMax)
    driverRiderMatching = getDriverRiderMatching(problemInstance, riderMatching)

    return driverRiderMatching
