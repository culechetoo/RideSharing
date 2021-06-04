import networkx as nx
from graphLib.graph.BaseGraph import BaseGraph


def nxMatching(graph: BaseGraph, perfect: bool = True, weight: str = "weight", minimum: bool = True):

    assert graph.lib == "networkx"
    graph = graph.getGraph()

    if minimum:
        for _, _, data in graph.edges(data=True):
            data["weight"] = -data["weight"]

    matching = nx.algorithms.max_weight_matching(graph, maxcardinality=perfect, weight=weight)

    return matching
