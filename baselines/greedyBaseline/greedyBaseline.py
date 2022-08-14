from os import remove
from time import time
import gc

import numpy as np

from hra.ExactLambdaAlgorithm import matchingAlgorithm
from hra.cost import linearInsertionRequests, linearInsertion

from graph_tool.all import Graph
from graph_tool.generation import complete_graph


def constructRiderPairGraph(costs):
    nRiders = np.ceil(np.sqrt(2*costs.shape[0]))

    graph = complete_graph(nRiders)
    weightProp = graph.new_ep("int32_t")
    weightProp.a = costs
    return graph, weightProp


def getCarPairs(interRiderDists, showRunTime=False, useMatchingHeuristic=True):

    currTime = time()
    nRiders = interRiderDists.shape[0]//2

    request1, request2 = np.triu_indices(nRiders, 1)

    currPaths1 = np.hstack([request1.reshape(-1, 1), request1.reshape(-1, 1)+nRiders])
    currPaths2 = np.hstack([request2.reshape(-1, 1), request2.reshape(-1, 1)+nRiders])
    requests1 = np.hstack([request2.reshape(-1, 1), request2.reshape(-1, 1)+nRiders])
    requests2 = np.hstack([request1.reshape(-1, 1), request1.reshape(-1, 1)+nRiders])

    _, totalCosts1 = linearInsertionRequests(currPaths1, requests1, interRiderDists)
    _, totalCosts2 = linearInsertionRequests(currPaths2, requests2, interRiderDists)
    totalCosts = np.max(np.concatenate([totalCosts1.reshape(-1, 1), totalCosts2.reshape(-1, 1)], axis=1), axis=1)
    totalCosts = max(totalCosts)-totalCosts+1

    graph, weightProp = constructRiderPairGraph(totalCosts)
    if showRunTime:
        print("graph constructed in %f" % (time()-currTime))

    gc.collect()

    matching = matchingAlgorithm(graph, weightProp, getEdgeProperty=True, useMatchingHeuristic=useMatchingHeuristic)
    matchedCarPairs = np.concatenate([request1[matching], request2[matching]], axis=1)

    return matchedCarPairs


def getCarGroupMatching(carPairs, carSourceDists, interRiderDists, useMatchingHeuristic):
    nCars, nRiders = carSourceDists.shape
    nPairs = carPairs.shape[0]
    carCapacity = nRiders//nCars

    unMatchedCars = set(range(nRiders)).difference(carPairs.flatten())
    assert len(unMatchedCars) <= 1

    currPath = np.arange(nCars).reshape(-1, 1)

    for i in range(nPairs//nCars):
        indices1 = np.repeat(np.arange(nCars), carPairs.shape[0]).reshape(-1, 1)
        indices2 = np.tile(np.arange(carPairs.shape[0]), nCars).reshape(-1, 1)
        pathIndices = np.arange(nCars*carPairs.shape[0]).reshape(-1, 1)
        riderIndices = np.concatenate([currPath[indices1, 1:].squeeze(), carPairs[indices2, :].squeeze(),
                                       currPath[indices1, 1:].squeeze()+nRiders, carPairs[indices2, :].squeeze()+nRiders],
                                      axis=1)
        ridersToAdd = riderIndices.shape[1]//2
        riderDists = interRiderDists[riderIndices[:, None].T, riderIndices.T].T
        sourceDists = np.expand_dims(carSourceDists[currPath[indices1, 0], riderIndices[:, :riderIndices.shape[1]//2]], axis=2)
        dists = np.zeros((nCars*carPairs.shape[0], 1+2*ridersToAdd, 1+2*ridersToAdd))
        dists[pathIndices, 0, 1:ridersToAdd+1] = sourceDists.reshape((-1, 1, ridersToAdd))
        dists[pathIndices, 1:ridersToAdd+1, 0] = sourceDists.reshape((-1, 1, ridersToAdd))
        dists[pathIndices, 0, ridersToAdd+1:] = np.NaN
        dists[pathIndices, ridersToAdd+1:, 0] = np.NaN
        dists[pathIndices, np.arange(2*ridersToAdd)+1, 1:] = riderDists

        _, edgeWeights = linearInsertion(np.zeros((nCars*carPairs.shape[0], 1), dtype=int), 2*(i+1), dists)
        edgeWeights = max(edgeWeights)-edgeWeights+1

        edges = np.hstack([indices1, indices2+nCars, np.rint(edgeWeights)]).astype(np.uint32)

        graph = Graph(directed=False)
        graph.add_vertex(nCars+carPairs.shape[0])

        weightProp = graph.new_ep("int32_t")
        graph.add_edge_list(edges, eprops=[weightProp])
        carGroupMatching = matchingAlgorithm(graph, weightProp, bipartite=True, useMatchingHeuristic=useMatchingHeuristic,
                                             partitions=[np.arange(nCars), np.arange(carPairs.shape[0])+nCars])

        requests = carGroupMatching[:, 1]-nCars

        currPath = np.hstack([currPath, carPairs[requests]])
        carPairs = np.delete(carPairs, requests, 0)

    if carCapacity % 2 == 1:
        carPairs = carPairs.flatten()
        if len(unMatchedCars)>0:
            carPairs = np.append(carPairs, unMatchedCars.pop())

        indices1 = np.repeat(np.arange(nCars), carPairs.shape[0]).reshape(-1, 1)
        indices2 = np.tile(np.arange(carPairs.shape[0]), nCars).reshape(-1, 1)
        pathIndices = np.arange(nCars * carPairs.shape[0]).reshape(-1, 1)
        riderIndices = np.concatenate([currPath[indices1, 1:].squeeze(), carPairs[indices2],
                                       currPath[indices1, 1:].squeeze() + nRiders,
                                       carPairs[indices2] + nRiders],
                                      axis=1)
        ridersToAdd = riderIndices.shape[1] // 2
        riderDists = interRiderDists[riderIndices[:, None].T, riderIndices.T].T
        sourceDists = np.expand_dims(
            carSourceDists[currPath[indices1, 0], riderIndices[:, :riderIndices.shape[1] // 2]], axis=2)
        dists = np.zeros((nCars * carPairs.shape[0], 1 + 2 * ridersToAdd, 1 + 2 * ridersToAdd))
        dists[pathIndices, 0, 1:ridersToAdd + 1] = sourceDists.reshape((-1, 1, ridersToAdd))
        dists[pathIndices, 1:ridersToAdd + 1, 0] = sourceDists.reshape((-1, 1, ridersToAdd))
        dists[pathIndices, 0, ridersToAdd + 1:] = np.NaN
        dists[pathIndices, ridersToAdd + 1:, 0] = np.NaN
        dists[pathIndices, np.arange(2 * ridersToAdd) + 1, 1:] = riderDists

        _, edgeWeights = linearInsertion(np.zeros((nCars * carPairs.shape[0], 1), dtype=int), carCapacity, dists)
        edgeWeights = max(edgeWeights) - edgeWeights + 1

        edges = np.hstack([indices1, indices2 + nCars, np.rint(edgeWeights)]).astype(np.uint32)

        graph = Graph(directed=False)
        graph.add_vertex(nCars + carPairs.shape[0])

        weightProp = graph.new_ep("int32_t")
        graph.add_edge_list(edges, eprops=[weightProp])
        carGroupMatching = matchingAlgorithm(graph, weightProp, bipartite=True, useMatchingHeuristic=useMatchingHeuristic,
                                             partitions=[np.arange(nCars), np.arange(carPairs.shape[0]) + nCars])

        requests = (carGroupMatching[:, 1] - nCars).reshape(-1, 1)
        currPath = np.hstack([currPath, carPairs[requests]])

    return currPath


def run(carSourceDists, interRiderDists, showRunTime=False, useMatchingHeuristic=False):
    try:
        remove("mstCache.h5")
    except FileNotFoundError:
        pass

    currTime = time()

    gc.collect()

    nCars, nRiders = carSourceDists.shape
    carCapacity = nRiders//nCars

    assert nRiders == nCars*carCapacity

    carPairs = getCarPairs(interRiderDists, showRunTime, useMatchingHeuristic)
    if showRunTime:
        print("car pairs found in %f" % (time() - currTime))

    carGroupMatching = getCarGroupMatching(carPairs, carSourceDists, interRiderDists, useMatchingHeuristic)

    try:
        remove("mstCache.h5")
    except FileNotFoundError:
        pass

    return carGroupMatching
