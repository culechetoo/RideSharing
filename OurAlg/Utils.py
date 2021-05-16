import itertools
from typing import List

import networkx as nx
from networkx import minimum_spanning_tree

from Main.UtilClasses import Rider as Request, Location


def getOverallMst(requestTuple, distNorm="l2"):
    x = []
    y = []

    for request in requestTuple:
        x.append(request.sourceLocation.x)
        x.append(request.targetLocation.x)
        y.append(request.sourceLocation.y)
        y.append(request.targetLocation.y)

    return mst(x, y, distNorm)


def mst_st(requestGroup, distNorm="l2"):

    return mst_s(requestGroup, distNorm)+mst_t(requestGroup, distNorm)


def mst_s(requestGroup: List[Request], distNorm="l2"):

    x: List[float] = []
    y: List[float] = []

    for request in requestGroup:
        x.append(request.sourceLocation.x)
        y.append(request.sourceLocation.y)

    return mst(x, y, distNorm)


def mst_t(requestGroup, distNorm="l2"):

    x: List[float] = []
    y: List[float] = []

    for request in requestGroup:
        x.append(request.targetLocation.x)
        y.append(request.targetLocation.y)

    return mst(x, y, distNorm)


def constructCompleteGraph(x, y, distNorm="l2"):

    graph = nx.Graph()
    graph.add_nodes_from(range(len(x)))

    indexPairs = itertools.combinations(range(len(x)), 2)

    for indexPair in indexPairs:

        index1 = indexPair[0]
        index2 = indexPair[1]

        x1 = x[index1]
        y1 = y[index1]
        x2 = x[index2]
        y2 = y[index2]

        location1 = Location(x1, y1)
        location2 = Location(x2, y2)

        dist = location1.getDistance(location2, distNorm)

        graph.add_edge(index1, index2, weight=dist)

    return graph


def mst(x, y, distNorm="l2"):

    graph = constructCompleteGraph(x, y, distNorm)
    mstGraph = minimum_spanning_tree(graph)

    return mstGraph.size(weight="weight")
