import networkx as nx


def networkxMatching(graph):

    for _, _, data in graph.edges(data=True):
        data["weight"] = -data["weight"]

    matching = nx.algorithms.max_weight_matching(graph, maxcardinality=True)

    return matching
