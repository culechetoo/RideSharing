import networkx as nx

from Main.UtilClasses import Driver
from OurAlg.Utils import getAssignmentCostUnbounded, getRequestGroupWalkCost
import PrevPaper.Algorithm as prevPaper


def checkAdjacency(nodeType1, nodeType2):
    if nodeType1 == "driver":
        if nodeType2 == "riderSource":
            return True
    if nodeType1 == "riderSource":
        return True
    if nodeType1 == "riderTarget":
        if nodeType2 != "driver":
            return True
    return False


def getPathWeight(path, distanceType):
    totalWeight = 0
    for i in range(len(path)-1):
        totalWeight += path[i].getDistance(path[i+1], distanceType)

    return totalWeight


def getMinWeightPerfectMatching(graph):

    for node1, node1, data in graph.edges(data=True):
        data["weight"] = -data["weight"]

    matching = nx.algorithms.max_weight_matching(graph, maxcardinality=True)

    return matching


def getBestDriverRequestGroupCost(driver, requestGroup, distNorm="l2"):

    edgeWeight = 1e9
    for request in requestGroup:
        edgeWeight = min(edgeWeight, request.sourceLocation.getDistance(driver.location, distNorm))

    return edgeWeight


def getMatchingCost(problemInstance, matching):

    if problemInstance.exact:

        totalCost = 0.0

        for match in matching:

            if type(match[0]) == tuple:
                riderTuple = match[0]
                driver: Driver = match[1]
            else:
                riderTuple = match[1]
                driver: Driver = match[0]

            if problemInstance.driverCapacity == 2:
                riderCost = prevPaper.getBestRiderPairCostMax(riderTuple[0], riderTuple[1], problemInstance.distNorm)
            else:
                riderCost = getRequestGroupWalkCost(riderTuple, distNorm=problemInstance.distNorm)
                # riderCost = 2*getOverallMst(riderTuple, problemInstance.distNorm)

            driverCost = getBestDriverRequestGroupCost(driver, riderTuple, problemInstance.distNorm)

            totalCost += riderCost+driverCost

    else:
        totalCost = getAssignmentCostUnbounded(matching, problemInstance.distNorm)

    return totalCost
