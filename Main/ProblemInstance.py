from typing import List

# import networkx as nx

from InputGenerator import UniformRandomGenerator, GaussianRandomGenerator
from Main.UtilClasses import Driver, Rider


class ProblemInstance:
    graphDim: (int, int)
    nDrivers: int
    nRiders: int
    drivers: List[Driver]
    riders: List[Rider]
    distNorm: str
    inputPrecision: int
    driverCapacity: int
    generatorType: str
    generatorArgs: dict

    def __init__(self, graph_dim: (int, int), n_drivers: int, n_riders: int, driverCapacity: int,
                 distNorm: str = "l2", inputPrecision: int = 2):
        self.graphDim = graph_dim
        self.nDrivers = n_drivers
        self.nRiders = n_riders
        self.drivers = []
        self.riders = []
        self.distNorm = distNorm
        self.driverCapacity = driverCapacity
        self.inputPrecision = inputPrecision

    def generateParams(self, generatorType: str, generatorArgs: dict = None):
        self.generatorType = generatorType
        self.generatorArgs = generatorArgs

        if generatorType == "uniform":
            UniformRandomGenerator.uniformGeneration(self, self.driverCapacity, self.inputPrecision)

        elif generatorType == "gaussian":
            GaussianRandomGenerator.gaussianMixtureGeneration(self, generatorArgs, self.driverCapacity,
                                                              self.inputPrecision)

    def getConfigString(self):

        print("Graph Dimensions: %d| nDrivers: %d| Driver Capacity: %d| Generator Type: %d| "
              "Generator Args"+str(self.generatorArgs) % (self.graphDim, self.nDrivers, self.nRiders,
                                                          self.generatorType))

    # def generateGraph(self):
    #     G = nx.Graph()
    #     driverNodes = []
    #     riderSourceNodes = []
    #     riderTargetNodes = []
    #
    #     for driver in self.drivers:
    #         driverNode = GraphNode(driver.index, driver.location, "driver")
    #         driverNodes.append(driverNode)
    #         G.add_node(driverNode)
    #
    #     for rider in self.riders:
    #         riderSourceNode = GraphNode(rider.index, rider.sourceLocation, "riderSource")
    #         riderSourceNodes.append(riderSourceNode)
    #         G.add_node(riderSourceNode)
    #         riderTargetNode = GraphNode(rider.index, rider.targetLocation, "riderTarget")
    #         riderTargetNodes.append(riderTargetNode)
    #         G.add_node(riderTargetNode)
    #
    #     for driverNode in driverNodes:
    #         for riderSourceNode in riderSourceNodes:
    #             G.add_edge(driverNode, riderSourceNode, weight=driverNode.location.getDistance(
    #                                                                        riderSourceNode.location,
    #                                                                        self.distNorm))
    #     for riderSourceNode in riderSourceNodes:
    #         for riderNode in riderSourceNodes + riderTargetNodes:
    #             if riderSourceNode != riderNode and not G.has_edge(riderSourceNode, riderNode):
    #                 G.add_edge(riderSourceNodes, riderNode, weight=riderSourceNode.location.getDistance(
    #                                                                            riderNode.location,
    #                                                                            self.distNorm))
    #
    #     return G
