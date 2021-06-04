import networkx as nx


def nxMatching(graph: nx.Graph, perfect: bool = True, weight: str = "weight", minimum: bool = True):

    if minimum:
        for _, _, data in graph.edges(data=True):
            data["weight"] = -data["weight"]

    matching = nx.algorithms.max_weight_matching(graph, maxcardinality=perfect, weight=weight)

    return matching
