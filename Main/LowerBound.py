from itertools import combinations
from typing import List

import networkx as nx
from networkx import minimum_spanning_tree

from Main.UtilClasses import Rider, Driver
from Main.Utils import getPathWeight
from PrevPaper.Algorithm import getRiderMatching, getBestRiderPairCostMin


def getMinRequestDriverSetDistance(request: Rider, drivers: List[Driver], distNorm="l2"):

    minDistance = request.sourceLocation.getDistance(drivers[0].location, distNorm)

    for driver in drivers:
        minDistance = request.sourceLocation.getDistance(driver.location, distNorm)

    return minDistance


def createDriverSetRequestGraph(problemInstance):

    graph = nx.Graph()

    graph.add_node("driverSet")

    for request in problemInstance.riders:
        graph.add_node(str(request.sourceLocation))

        edgeWeight = min([request.sourceLocation.getDistance(driver.location, problemInstance.distNorm)
                          for driver in problemInstance.drivers])
        graph.add_edge("driverSet", str(request.sourceLocation), weight=edgeWeight)

        graph.add_node(str(request.targetLocation))

        edgeWeight = min([request.targetLocation.getDistance(driver.location, problemInstance.distNorm)
                          for driver in problemInstance.drivers])
        graph.add_edge("driverSet", str(request.targetLocation), weight=edgeWeight)

        graph.add_edge(str(request.sourceLocation), str(request.targetLocation),
                       weight=request.sourceLocation.getDistance(request.targetLocation, problemInstance.distNorm))

    for requestPair in combinations(problemInstance.riders, 2):

        request1: Rider = requestPair[0]
        request2: Rider = requestPair[1]

        graph.add_edge(str(request1.sourceLocation), str(request2.sourceLocation),
                       weight=request1.sourceLocation.getDistance(request2.sourceLocation, problemInstance.distNorm))

        graph.add_edge(str(request1.sourceLocation), str(request2.targetLocation),
                       weight=request1.sourceLocation.getDistance(request2.targetLocation, problemInstance.distNorm))

        graph.add_edge(str(request2.sourceLocation), str(request1.sourceLocation),
                       weight=request2.sourceLocation.getDistance(request1.sourceLocation, problemInstance.distNorm))

        graph.add_edge(str(request2.sourceLocation), str(request1.targetLocation),
                       weight=request2.sourceLocation.getDistance(request1.targetLocation, problemInstance.distNorm))

    return graph


def entireTreeMethod(problemInstance):

    graph = createDriverSetRequestGraph(problemInstance)
    mst: nx.Graph = minimum_spanning_tree(graph)

    return mst.size(weight="weight")


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
    for riderPair in riderMatching:
        rider_i: Rider = riderPair[0]
        rider_j: Rider = riderPair[1]
        riderMatchingCost += getBestRiderPairCostMin(rider_i, rider_j, problemInstance.distNorm)

    return riderMatchingCost


def getLowerBoundCost(problemInstance):

    lamb = problemInstance.driverCapacity

    if lamb == 2:
        riderMatching = getRiderMatching(problemInstance, getBestRiderPairCostMin)
        riderMatchingCost = calcRiderMatchingCost(problemInstance, riderMatching)

        driverRequestGroupMatching = getDriverRiderMatching(problemInstance)
        driverRequestMatchingCost = calcDriverRiderMatchingCost(problemInstance, driverRequestGroupMatching)

        return riderMatchingCost+driverRequestMatchingCost

    else:
        return entireTreeMethod(problemInstance)
