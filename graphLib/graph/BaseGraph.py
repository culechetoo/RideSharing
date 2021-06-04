from typing import List, Any, Callable


class BaseGraph:

    @property
    def lib(self):
        raise NotImplementedError

    @property
    def graph(self):
        raise NotImplementedError

    @graph.setter
    def graph(self, value):
        raise NotImplementedError

    def getGraph(self):
        raise NotImplementedError

    def addNodes(self, nodes: List[Any]):
        raise NotImplementedError

    def makeCompleteWeightedGraph(self, weightFunc: Callable[[int, int], float], params: bool = False,
                                  partitions: List[List[int]] = None):
        raise NotImplementedError

    def addWeightedEdges(self, edges: List[Any]):
        raise NotImplementedError
