import networkx as nx


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

    graphCopy = graph.copy()

    for node1, node1, data in graphCopy.edges(data=True):
        data["weight"] = -data["weight"]

    matching = nx.algorithms.max_weight_matching(graphCopy, maxcardinality=True)
    return matching
