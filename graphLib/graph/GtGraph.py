from typing import List, Any, Callable

from graphLib.graph.BaseGraph import BaseGraph


class GtGraph(BaseGraph):

    lib = "graph-tool"

    @property
    def _graph(self):
        pass

    def getGraph(self):
        pass

    def addNodes(self, nodes: List[Any]):
        pass

    def makeCompleteWeightedGraph(self, weightFunc: Callable[[int, int], float], params: bool = False,
                                  partitions: List[List[int]] = None):
        if partitions is None:
            partitions = []

    def addWeightedEdges(self, edges: List[Any]):
        pass

    def __init__(self):
        pass
