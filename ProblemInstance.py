from typing import List

import networkx as nx

from InputGenerator import UniformRandomGenerator, GaussianRandomGenerator
from UtilClasses import Driver, Rider, GraphNode
from Utils import getPathWeight


class ProblemInstance:
    graphDim: (int, int)
    nDrivers: int
    nRiders: int
    drivers: List[Driver]
    riders: List[Rider]
    distNorm: str
    inputPrecision: int
    driverCapacity: int

    def __init__(self, graph_dim: (int, int), n_drivers: int, n_riders: int, driverCapacity: int, distNorm: str = "l2",
                 inputPrecision: int = 0):
        self.graphDim = graph_dim
        self.nDrivers = n_drivers
        self.nRiders = n_riders
        self.drivers = []
        self.riders = []
        self.distNorm = distNorm
        self.driverCapacity = driverCapacity
        self.inputPrecision = inputPrecision

    def generateParams(self, generatorType: str, generatorArgs: dict = None):
        if generatorType == "uniform":
            UniformRandomGenerator.uniformGeneration(self, self.driverCapacity, self.inputPrecision)

        elif generatorType == "gaussian":
            GaussianRandomGenerator.gaussianMixtureGeneration(self, generatorArgs, self.driverCapacity,
                                                              self.inputPrecision)

    def getMatchingCost(self, matching):

        cost = 0.0
        for match in matching:

            if type(match[0]) == tuple:
                riderTuple = match[0]
                driverIndex = match[1]
            else:
                riderTuple = match[1]
                driverIndex = match[0]

            driver: Driver = self.drivers[driverIndex]
            rider1: Rider = self.riders[riderTuple[0]]
            rider2: Rider = self.riders[riderTuple[1]]

            costPick1FirstDrop1First = getPathWeight([driver.location, rider1.sourceLocation, rider2.sourceLocation,
                                                     rider1.targetLocation, rider2.targetLocation], self.distNorm)
            costPick1FirstDrop2First = getPathWeight([driver.location, rider1.sourceLocation, rider2.sourceLocation,
                                                      rider2.targetLocation, rider1.targetLocation], self.distNorm)
            costPick2FirstDrop1First = getPathWeight([driver.location, rider2.sourceLocation, rider1.sourceLocation,
                                                      rider1.targetLocation, rider2.targetLocation], self.distNorm)
            costPick2FirstDrop2First = getPathWeight([driver.location, rider2.sourceLocation, rider1.sourceLocation,
                                                      rider2.targetLocation, rider1.targetLocation], self.distNorm)

            cost += min([costPick1FirstDrop1First, costPick1FirstDrop2First, costPick2FirstDrop1First,
                         costPick2FirstDrop2First])

        return cost

    def generateGraph(self):
        G = nx.Graph()
        driverNodes = []
        riderSourceNodes = []
        riderTargetNodes = []

        for driver in self.drivers:
            driverNode = GraphNode(driver.index, driver.location, "driver")
            driverNodes.append(driverNode)
            G.add_node(driverNode)

        for rider in self.riders:
            riderSourceNode = GraphNode(rider.index, rider.sourceLocation, "riderSource")
            riderSourceNodes.append(riderSourceNode)
            G.add_node(riderSourceNode)
            riderTargetNode = GraphNode(rider.index, rider.targetLocation, "riderTarget")
            riderTargetNodes.append(riderTargetNode)
            G.add_node(riderTargetNode)

        for driverNode in driverNodes:
            for riderSourceNode in riderSourceNodes:
                G.add_edge(driverNode, riderSourceNode, weight=driverNode.location.getDistance(
                                                                           riderSourceNode.location,
                                                                           self.distNorm))
        for riderSourceNode in riderSourceNodes:
            for riderNode in riderSourceNodes + riderTargetNodes:
                if riderSourceNode != riderNode and not G.has_edge(riderSourceNode, riderNode):
                    G.add_edge(riderSourceNodes, riderNode, weight=riderSourceNode.location.getDistance(
                                                                               riderNode.location,
                                                                               self.distNorm))

        return G
