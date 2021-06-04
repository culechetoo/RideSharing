import itertools
from typing import List, FrozenSet, Tuple

import networkx as nx
from networkx import minimum_spanning_tree

from Main.UtilClasses import Rider as Request, Location, Rider
from OurAlg.TSP.NearestNeighbour import getPathNearestNeighbourRequests

from OurAlg.TSP.BruteForce import getPathBruteForce

mstCache = {}


def getOverallMstRequestTuple(requestTuple, distNorm="l2"):
    x = []
    y = []

    for request in requestTuple:
        x.append(request.sourceLocation.x)
        x.append(request.targetLocation.x)
        y.append(request.sourceLocation.y)
        y.append(request.targetLocation.y)

    graph = constructCompleteGraph(x, y, distNorm)

    return mst(graph).size(weight="weight")


def mst_st(requestGroup, distNorm="l2"):

    return mst_s(requestGroup, distNorm)+mst_t(requestGroup, distNorm)


def mst_s(requestGroup: FrozenSet[Request], distNorm="l2"):

    if len(requestGroup) == 1:
        return 0
    if len(requestGroup) == 2:
        request1, request2 = requestGroup
        return request1.sourceLocation.getDistance(request2.sourceLocation, distNorm)

    x: List[float] = []
    y: List[float] = []

    for request in requestGroup:
        x.append(request.sourceLocation.x)
        y.append(request.sourceLocation.y)

    graph = constructCompleteGraph(x, y, distNorm)

    return mst(graph).size(weight="weight")


def mst_t(requestGroup: FrozenSet[Request], distNorm="l2"):

    if len(requestGroup) == 1:
        return 0
    if len(requestGroup) == 2:
        request1, request2 = requestGroup
        return request1.targetLocation.getDistance(request2.targetLocation, distNorm)

    x: List[float] = []
    y: List[float] = []

    for request in requestGroup:
        x.append(request.targetLocation.x)
        y.append(request.targetLocation.y)

    graph = constructCompleteGraph(x, y, distNorm)

    return mst(graph).size(weight="weight")


def constructCompleteGraph(x, y, distNorm="l2"):

    graph = nx.Graph()
    graph.add_nodes_from(range(len(x)))

    indexPairs = itertools.combinations(range(len(x)), 2)

    edges = []

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

        edges.append((index1, index2, dist))

    graph.add_weighted_edges_from(edges)

    return graph


def mst(graph):
    mstGraph = minimum_spanning_tree(graph)

    return mstGraph


def getDistRequestGroups(requestGroup1: FrozenSet[Request], requestGroup2: FrozenSet[Request], distNorm="l2"):

    union = requestGroup1.union(requestGroup2)

    if requestGroup1 not in mstCache:
        mstCache[requestGroup1] = mst_st(requestGroup1, distNorm)
    if requestGroup2 not in mstCache:
        mstCache[requestGroup2] = mst_st(requestGroup2, distNorm)
    if union not in mstCache:
        mstCache[union] = mst_st(union, distNorm)

    dist = mstCache[union] - mstCache[requestGroup1] - mstCache[requestGroup2]

    del mstCache[requestGroup2]
    del mstCache[requestGroup1]

    return dist


def getDistRequestGroupSets(requestGroupSet1, requestGroupSet2, distNorm="l2"):
    edgeWeight = 1e9
    groups = ()
    method = ""

    for requestGroup1 in requestGroupSet1:
        for requestGroup2 in requestGroupSet2:
            w1 = getDistRequestGroups(requestGroup1, requestGroup2, distNorm)
            w2 = w_2(requestGroup1, requestGroup2, distNorm)

            if w2 < edgeWeight:
                groups = (requestGroup1, requestGroup2)
                edgeWeight = w2
                method = "w2"
            if w1 <= edgeWeight:
                groups = (requestGroup1, requestGroup2)
                edgeWeight = w1
                method = "w1"

    return edgeWeight, groups, method


def w_2(requestGroup1, requestGroup2, distNorm="l2"):
    minVal1 = 1e9

    for request in requestGroup1:
        minVal1 = min(minVal1, request.sourceLocation.getDistance(request.targetLocation, distNorm))

    minVal2 = 1e9
    for request in requestGroup2:
        minVal2 = min(minVal2, request.sourceLocation.getDistance(request.targetLocation, distNorm))

    return minVal1+minVal2


def getRequestGroupWalkCost(requestGroup, driver, distNorm="l2"):

    # cost = 2 * mst_st(requestGroup, distNorm) + getMinDistSt(requestGroup, distNorm)
    if len(requestGroup) == 2:
        walk, cost = getPathBruteForce(requestGroup, driver.location, distNorm)
    else:
        walk, cost = getPathNearestNeighbourRequests(requestGroup, driver.location, distNorm)

    return [driver]+walk, cost


def getBoundedAssignmentWalks(driverGroupMatching, distNorm="l2"):

    driverRequests = {}

    for driver, riderGroupTree, _ in driverGroupMatching:
        if driver not in driverRequests:
            driverRequests[driver] = []
        for requestGroup in riderGroupTree.nodes:
            driverRequests[driver].extend(requestGroup)

    walks = []
    costs = []

    for driver, requestGroup in driverRequests.items():

        walk, driverGroupCost = getRequestGroupWalkCost(requestGroup, driver, distNorm)[1]
        costs.append(driverGroupCost)
        walk.append(walks)

    return walks, costs


def getMinDistSt(riderTuple: Tuple[Rider], distNorm):

    minDist = riderTuple[0].sourceLocation.getDistance(riderTuple[0].targetLocation, distNorm)

    for riderIndex1 in range(len(riderTuple)):
        for riderIndex2 in range(len(riderTuple)):
            minDist = min(minDist, riderTuple[riderIndex1].sourceLocation.getDistance(
                riderTuple[riderIndex2].targetLocation, distNorm))

    return minDist
