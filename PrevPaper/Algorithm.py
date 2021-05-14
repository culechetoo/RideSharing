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
    graph.add_nodes_from(problemInstance.riders)

    riderPairs = combinations(problemInstance.riders, 2)

    for riderPair in riderPairs:

        rider1: Rider = riderPair[0]
        rider2: Rider = riderPair[1]

        edgeWeight = edgeWeightFunction(rider1, rider2, problemInstance.distNorm)
        
        graph.add_edge(rider1, rider2, weight=edgeWeight)

    return graph


def getRiderMatching(problemInstance, edgeWeightFunction):

    graph = generateRiderPairGraph(problemInstance, edgeWeightFunction)
    matching = getMinWeightPerfectMatching(graph)

    return matching


def generateDriverRiderPairGraph(problemInstance, riderMatching):

    graph = nx.Graph()

    graph.add_nodes_from(problemInstance.drivers)
    graph.add_nodes_from(riderMatching)

    for driver in problemInstance.drivers:
        for riderPair in riderMatching:

            rider1: Rider = riderPair[0]
            rider2: Rider = riderPair[1]

            edgeWeight = getBestDriverRequestGroupCost(driver, (rider1, rider2), problemInstance.distNorm)

            graph.add_edge(driver, riderPair, weight=edgeWeight)

    return graph


def getDriverRiderMatching(problemInstance, riderMatching):

    graph = generateDriverRiderPairGraph(problemInstance, riderMatching)
    matching = getMinWeightPerfectMatching(graph)

    return matching


def run(problemInstance):

    riderMatching = getRiderMatching(problemInstance, getBestRiderPairCostMax)
    driverRiderMatching = getDriverRiderMatching(problemInstance, riderMatching)

    return driverRiderMatching
