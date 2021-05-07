import networkx as nx
from itertools import combinations

from UtilClasses import *
from Utils import getPathWeight, getMinWeightPerfectMatching


def getBestRiderPairCost(rider1: Rider, rider2: Rider, distNorm):
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


def getBestDriverRiderPairCost(driver: Driver, rider1: Rider, rider2: Rider, distNorm):
    weight1 = getPathWeight([driver.location, rider1.sourceLocation], distNorm)
    weight2 = getPathWeight([driver.location, rider2.sourceLocation], distNorm)

    edgeWeight = min(weight1, weight2)

    return edgeWeight


def generateRiderPairGraph(problemInstance):

    graph = nx.Graph()
    graph.add_nodes_from(range(problemInstance.nRiders))

    riderIndexPairs = combinations(range(problemInstance.nRiders), 2)

    for riderIndexPair in riderIndexPairs:

        rider1: Rider = problemInstance.riders[riderIndexPair[0]]
        rider2: Rider = problemInstance.riders[riderIndexPair[1]]

        edgeWeight = getBestRiderPairCost(rider1, rider2, problemInstance.distNorm)
        
        graph.add_edge(riderIndexPair[0], riderIndexPair[1], weight=edgeWeight)

    return graph


def getRiderMatching(problemInstance):

    graph = generateRiderPairGraph(problemInstance)
    matching = getMinWeightPerfectMatching(graph)

    return matching


def generateDriverRiderPairGraph(problemInstance, riderMatching):

    graph = nx.Graph()

    graph.add_nodes_from(range(problemInstance.nDrivers))
    graph.add_nodes_from(riderMatching)

    for driverIndex in range(problemInstance.nDrivers):
        for riderPair in riderMatching:

            driver: Driver = problemInstance.drivers[driverIndex]
            rider1: Rider = problemInstance.riders[riderPair[0]]
            rider2: Rider = problemInstance.riders[riderPair[1]]

            edgeWeight = getBestDriverRiderPairCost(driver, rider1, rider2, problemInstance.distNorm)

            graph.add_edge(driverIndex, riderPair, weight=edgeWeight)

    return graph


def getDriverRiderMatching(problemInstance, riderMatching):

    graph = generateDriverRiderPairGraph(problemInstance, riderMatching)
    matching = getMinWeightPerfectMatching(graph)

    return matching


def run(problemInstance):

    riderMatching = getRiderMatching(problemInstance)
    driverRiderMatching = getDriverRiderMatching(problemInstance, riderMatching)

    return driverRiderMatching


def getMatchingCost(problemInstance, matching):

    totalCost = 0.0

    for match in matching:

        if type(match[0]) == tuple:
            riderTuple = match[0]
            driverIndex = match[1]
        else:
            riderTuple = match[1]
            driverIndex = match[0]

        driver: Driver = problemInstance.drivers[driverIndex]
        rider1: Rider = problemInstance.riders[riderTuple[0]]
        rider2: Rider = problemInstance.riders[riderTuple[1]]

        riderCost = getBestRiderPairCost(rider1, rider2, problemInstance.distNorm)
        driverCost = getBestDriverRiderPairCost(driver, rider1, rider2, problemInstance.distNorm)

        totalCost += riderCost+driverCost

    return totalCost
