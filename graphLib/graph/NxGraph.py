import itertools
from typing import List, Any, Callable

from graphLib.graph.BaseGraph import BaseGraph

import networkx as nx


class NxGraph(BaseGraph):

    def __init__(self):
        self._graph = nx.Graph()
        self._lib = "networkx"

    @property
    def graph(self):
        return self._graph

    @property
    def lib(self):
        return self._lib

    def getGraph(self):
        return self.graph

    def addNodes(self, nodes: List[Any]):
        self.graph.add_nodes_from(nodes)

    def addWeightedEdges(self, edges: List[Any]):
        self.graph.add_weighted_edges_from(edges)

    def makeCompleteWeightedGraph(self, weightFunc: Callable[[int, int], float], params: bool = False,
                                  partitions: List[List[int]] = None):
        if partitions is None:
            nodes = self.graph.nodes
            edges = [(node1, node2, weightFunc(node1, node2)) for node1, node2 in itertools.combinations(nodes, 2)
                     if node1 != node2]
            self.addWeightedEdges(edges)
        else:
            assert max([max(partition) for partition in partitions]) < len(self.graph.nodes)
            edges = [(node1, node2, weightFunc(node1, node2)) for partition1, partition2 in
                     itertools.combinations(partitions, 2) for node1, node2 in
                     itertools.product(partition1, partition2) if node1 != node2]
            self.addWeightedEdges(edges)
