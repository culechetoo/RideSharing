import math
import pickle
import time
from itertools import permutations, starmap

import numpy as np
import sortednp as snp
from numpy.linalg import norm

from scipy.spatial.distance import squareform, pdist
import multiprocessing

try:
    cpus = multiprocessing.cpu_count()
except NotImplementedError:
    cpus = 2


def getCosts(iterator, labels):
    labelIter = starmap(lambda i1, i2: (labels[i1], labels[i2]), iterator)
    pool = multiprocessing.Pool(processes=cpus)
    results = np.array(pool.starmap(findDist, labelIter))
    pool.close()
    pool.join()
    return results


# @lru_cache(maxsize=240)
def findDist(label1, label2):
    hubs1 = label1[0]
    hubs2 = label2[0]
    dists1 = label1[1]
    dists2 = label2[1]

    _, (indices1, indices2) = snp.intersect(hubs1, hubs2, indices=True)
    # _, indices1, indices2 = np.intersect1d(hubs1, hubs2, assume_unique=True, return_indices=True)

    dists = dists1[indices1]+dists2[indices2]

    return dists.min()

    # commonHubs = label1.keys() & label2.keys()
    #
    # a = min([label1[hub] + label2[hub] for hub in commonHubs])
    #
    # return a


def getRequestLocation(request, getTarget):
    return request[1] if getTarget else request[0]


def getTotalRequestServeTime(walks, distFunc, targetLocations):
    totalServeTime = 0

    row = 0
    for walk in walks:

        currLocation = walk[0]
        visited = set([])
        runningCost = 0

        col = 1
        for request in walk[1:]:
            runningCost += distFunc(currLocation, request)
            currLocation = request
            if col in targetLocations[row, :]:
                totalServeTime += runningCost
            visited.add(request)
            col += 1

        row += 1

    return totalServeTime


def getRequestGroupWalkCost(requestGroup, car, distFunc):
    walk, cost = naiveInsertion(requestGroup, car, distFunc)
    # if len(requestGroup) == 2:
    #     walk, cost = getPathBruteForce(requestGroup, car, labels)
    #     walk = walk
    # else:
    # walk, cost = getPathNearestNeighbourRequests(requestGroup, car, labels)
    # walk = walk

    return walk, cost


def validateMatching(matching):
    requestIndices = set([])
    prevLen = 0
    cap = 0

    for match in matching:
        requestIndices = requestIndices.union(match[1:])
        if cap == 0:
            cap = len(requestIndices)

        if len(requestIndices) - prevLen != cap:
            return False

        prevLen = len(requestIndices)

    return True


def validateCost(walks, calcedTotalCost, distFunc):

    totalCost = 0

    nWalks, walkLen = walks.shape

    for walk in walks:
        for j in range(walkLen-1):
            totalCost += distFunc(walk[j], walk[j+1])

    return math.isclose(calcedTotalCost, totalCost)


def getMatchingCosts(matching, carLocations, riderSources, riderTargets, labelFile=None, nodeFile=None,
                     calcPath=True, returnOtherCosts=False):
    assert len(matching) == len(carLocations)

    if labelFile is not None:

        labelFile.seek(0)
        labels = pickle.load(labelFile)
        distFunc = lambda i, j: findDist(labels[i], labels[j]) if type(i) == np.int64 else findDist(labels[i[0]], labels[j[0]])

    else:
        assert nodeFile is not None
        nodeFile.seek(0)
        nodes = np.array(list(map(lambda l: list(map(lambda i: float(i), l.split())), nodeFile.readlines()[1:])))
        distFunc = lambda i, j: norm(nodes[i] - nodes[j])

    currTime = time.time()

    nCars = len(carLocations)
    nRiders = len(riderSources)
    carCapacity = nRiders//nCars

    if calcPath:
        dists = []
        allCands = np.zeros((nCars, 2*carCapacity+1))
        for i in range(nCars):
            match = matching[i, :]
            riderIndices = match[1:]
            match = np.concatenate([[carLocations[match[0]]], riderSources[riderIndices], riderTargets[riderIndices]])
            dists.append(squareform(pdist(match.reshape(-1, 1), distFunc)))
            allCands[i, :] = match

        dists = np.array(dists)
        currPaths = np.zeros((nCars, 1), dtype=int)
        walks, costs = linearInsertion(currPaths, carCapacity, dists)
        targetLocations = np.argwhere(walks > carCapacity)[:, 1].reshape(nCars, carCapacity)
        walks[:, 0] = carLocations
        walks[:, 1:] = allCands[np.expand_dims(np.arange(nCars), axis=1), walks[:, 1:]]
    else:
        walks = np.zeros((nCars, 2*carCapacity+1), dtype=int)
        walks[:, 0] = carLocations
        costs = np.zeros(nCars)
        newMatching = []
        for i in range(nCars):
            newMatch = [i]
            for j in range(2*carCapacity):
                ind = int(matching[i, j+1])
                walks[i, j+1] = riderSources[ind] if ind < nRiders else riderTargets[ind-nRiders]
                newMatch.append(ind) if ind < nRiders else None
                costs[i] += distFunc(walks[i, j], walks[i, j+1])

            newMatching.append(newMatch)

        matching = newMatching

    maxCost = costs.max()
    totalCost = costs.sum()

    runTime = time.time() - currTime

    # totalCost = 0.0
    # maxCost = 0.0
    #
    # walks = []
    #
    # for match in matching:
    #
    #     if type(match[0]) == tuple:
    #         riderTuple = match[0]
    #         carIndex = match[1]
    #     else:
    #         riderTuple = match[1]
    #         carIndex = match[0]
    #
    #     car = carLocations[carIndex]
    #     riders = [(riderSources[riderIndex], riderTargets[riderIndex]) for riderIndex in riderTuple]
    #
    #     walk, cost = getRequestGroupWalkCost(riders, car, distFunc)
    #
    #     walks.append(walk)
    #     totalCost += cost
    #     maxCost = max(maxCost, cost)
    #
    # runTime = time.time() - currTime

    # assert math.isclose(totalCost, totalCost2), "%f %f" % (totalCost, totalCost2)
    # assert math.isclose(maxCost, maxCost2), "%f %f" % (maxCost, maxCost2)
    # print(runTime, runTime2)

    assert validateMatching(matching)
    assert validateCost(walks.astype(int), totalCost, distFunc)

    # totalServeTime = getTotalRequestServeTime(walks, distFunc)
    totalServeTime = getTotalRequestServeTime(walks, distFunc, targetLocations)

    # assert math.isclose(totalServeTime, totalServeTime2)

    if returnOtherCosts:
        return (totalCost, maxCost, totalServeTime), runTime
    else:
        return (totalCost), runTime


def cumargin(a):
    m = np.minimum.accumulate(a, axis=1)
    x = np.repeat(np.arange(a.shape[1])[:, None].T, a.shape[0], axis=0)
    x[:, 1:] *= m[:, :-1] > m[:, 1:]
    np.maximum.accumulate(x, axis=1, out=x)
    return x


def linearInsertionRequests(currPaths, requests, dists):
    nPaths, preLen = currPaths.shape

    pathIndices = np.expand_dims(np.arange(nPaths), axis=1)
    zeroArray = np.expand_dims(np.zeros(nPaths), axis=1)

    sources = requests[:, 0].reshape(-1, 1)
    targets = requests[:, 1].reshape(-1, 1)

    currDists = np.hstack([dists[currPaths[:, :-1], currPaths[:, 1:]], zeroArray])

    prevSourceDist = np.hstack([dists[currPaths, sources]])
    targetNextDist = np.hstack([dists[currPaths[:, 1:], targets], zeroArray])

    # i=j case
    incr = prevSourceDist + targetNextDist + dists[sources, targets] - currDists
    bestIncrIndEq = np.expand_dims(np.argmin(incr, axis=1), axis=1)
    bestIncrEq = incr[pathIndices, bestIncrIndEq]

    # find best i's
    iIncrs = prevSourceDist[:, :-1] + prevSourceDist[:, 1:] - currDists[:, :-1]
    bestIs = cumargin(iIncrs)
    # bestIIncrs = iIncrs[pathIndices, bestIs]

    # find j's and adjust bestIncr
    # jIncrs = targetNextDist[:, :-1] + targetNextDist[:, 1:]
    totalIncrs = iIncrs[pathIndices, bestIs] + targetNextDist[:, :-1] + targetNextDist[:, 1:] - currDists[:, 1:]
    bestIncrIndNe = np.expand_dims(np.argmin(totalIncrs, axis=1), axis=1)
    bestIncrNe = totalIncrs[pathIndices, bestIncrIndNe]

    # find best among both
    eqGr = bestIncrEq < bestIncrNe
    bestInds = np.where(eqGr, np.concatenate([bestIncrIndEq, bestIncrIndEq], axis=1),
                        np.concatenate([bestIs[pathIndices, bestIncrIndNe], bestIncrIndNe + 1], axis=1))
    bestIncrs = np.where(eqGr, bestIncrEq, bestIncrNe)

    # add to path
    currPaths = np.insert(currPaths.flatten(), (bestInds + pathIndices * preLen).flatten() + 1,
                          np.concatenate([sources, targets], axis=1).flatten()).reshape(nPaths, preLen+2)
    totalCost = bestIncrs.squeeze()+currDists.sum(axis=1)

    return currPaths, totalCost


def linearInsertion(currPaths, nRequests, dists):
    nPaths, preLen = currPaths.shape
    totalCost = np.zeros((nPaths, 1), dtype=float)

    pathIndices = np.expand_dims(np.arange(nPaths), axis=1)
    zeroArray = np.expand_dims(np.zeros(nPaths), axis=1)

    for i in range(nRequests):

        sources = np.full((nPaths, 1), i + preLen)
        targets = np.full((nPaths, 1), i + preLen + nRequests)

        currDists = np.concatenate([dists[pathIndices, currPaths[:, :-1], currPaths[:, 1:]], zeroArray], axis=1)

        # sourceTargetDist = dists[pathIndices, sources, targets]
        prevSourceDist = dists[pathIndices, currPaths, sources]
        targetNextDist = np.hstack([dists[pathIndices, currPaths[:, 1:], targets], zeroArray])

        # i=j case
        incr = prevSourceDist + targetNextDist + dists[pathIndices, sources, targets] - currDists
        bestIncrIndEq = np.expand_dims(np.argmin(incr, axis=1), axis=1)
        bestIncrEq = incr[pathIndices, bestIncrIndEq]

        if i == 0:
            currPaths = np.concatenate([currPaths, sources, targets], axis=1)
            totalCost += bestIncrEq
            continue

        # find best i's
        iIncrs = prevSourceDist[:, :-1] + prevSourceDist[:, 1:] - currDists[:, :-1]
        bestIs = cumargin(iIncrs)
        # bestIIncrs = iIncrs[pathIndices, bestIs]

        # find j's and adjust bestIncr
        # jIncrs = targetNextDist[:, :-1] + targetNextDist[:, 1:]
        totalIncrs = iIncrs[pathIndices, bestIs] + targetNextDist[:, :-1] + targetNextDist[:, 1:] - currDists[:, 1:]
        bestIncrIndNe = np.expand_dims(np.argmin(totalIncrs, axis=1), axis=1)
        bestIncrNe = totalIncrs[pathIndices, bestIncrIndNe]

        # find best among both
        eqGr = bestIncrEq < bestIncrNe
        bestInds = np.where(eqGr, np.concatenate([bestIncrIndEq, bestIncrIndEq], axis=1),
                            np.concatenate([bestIs[pathIndices, bestIncrIndNe], bestIncrIndNe+1], axis=1))
        bestIncrs = np.where(eqGr, bestIncrEq, bestIncrNe)

        # add to path
        currPaths = np.insert(currPaths.flatten(), (bestInds + pathIndices * (2 * i + preLen)).flatten() + 1,
                              np.concatenate([sources, targets], axis=1).flatten()).reshape((nPaths, 2 * (i + 1) + preLen))
        totalCost += bestIncrs

    return currPaths, totalCost


def getWalkCost(walk, distFunc):
    cost = 0
    for i in range(len(walk) - 1):
        cost += distFunc(walk[i], walk[i + 1])

    return cost


def naiveInsertion(requests, sourceLocation, distFunc):
    walk = [sourceLocation]
    cost = 0

    for request in requests:
        srcIndex = getRequestLocation(request, False)
        tgtIndex = getRequestLocation(request, True)
        minIncr = 1e9
        best_i = 0
        best_j = 0

        for i in range(1, len(walk) + 1):
            incr1 = distFunc(walk[i - 1], srcIndex)
            incr1 += 0 if i == len(walk) else distFunc(srcIndex, walk[i]) - distFunc(walk[i - 1], walk[i])
            for j in range(i + 1, len(walk) + 2):
                prevIndex = srcIndex if j == i + 1 else walk[j - 2]
                incr2 = distFunc(prevIndex, tgtIndex)
                incr2 += 0 if j == len(walk) + 1 else distFunc(tgtIndex, walk[j - 1]) - distFunc(prevIndex, walk[j - 1])

                if incr1 + incr2 < minIncr:
                    minIncr = incr1 + incr2
                    best_i = i
                    best_j = j

        walk = walk[:best_i] + [getRequestLocation(request, False)] + walk[best_i:best_j - 1] + [
            getRequestLocation(request, True)] + walk[best_j - 1:]
        cost += minIncr

    assert len(walk) == 2 * len(requests) + 1

    assert math.isclose(getWalkCost(walk, distFunc), cost)

    return walk, cost


@DeprecationWarning
def getPathBruteForce(requests, sourceLocation, labels):
    assert len(requests) <= 4, "Number of requests is too large"

    requests = list(requests)

    combos = permutations(list(range(len(requests))) + list(range(len(requests))), len(requests) * 2)

    comboCostTuple = (tuple(), 1e9)

    for combo in combos:

        assert len(combo) == len(requests) * 2

        cost = 0
        currLocation = sourceLocation

        inPath = set([])

        for i in combo:
            nextLocation = getRequestLocation(requests[i], i in inPath)
            cost += findDist(labels[currLocation], labels[nextLocation])
            currLocation = nextLocation
            inPath.add(i)

        assert len(inPath) == len(requests)

        if cost < comboCostTuple[1]:
            comboCostTuple = [sourceLocation] + [requests[i] for i in combo], cost

    return comboCostTuple


def getPathNearestNeighbourRequests(requests, sourceLocation, labels):
    path = []
    cost = 0
    inPath = set([])

    remainingRequests = set(requests)

    currLocation = sourceLocation

    while len(path) < 2 * len(requests):
        distArray = [(findDist(labels[currLocation], labels[getRequestLocation(request, request in inPath)]), request)
                     for request in remainingRequests]
        addCost, request = min(distArray, key=lambda obj: obj[0])
        path.append(getRequestLocation(request, request in inPath))
        cost += addCost

        currLocation = getRequestLocation(request, request in inPath)

        if request in inPath:
            remainingRequests.remove(request)
        else:
            inPath.add(request)

    return [sourceLocation] + path, cost
