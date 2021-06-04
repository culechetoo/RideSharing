import itertools

from OurAlg.tsp.Utils import getRequestLocation


def getPathBruteForce(requests, sourceLocation, distNorm="l2"):

    assert len(requests) <= 4, "Number of requests is too large"

    requests = list(requests)

    combos = itertools.permutations(list(range(len(requests)))+list(range(len(requests))), len(requests)*2)

    comboCostTuple = (tuple(), 1e9)

    for combo in combos:

        assert len(combo) == len(requests)*2

        cost = 0
        currLocation = sourceLocation

        inPath = set([])

        for i in combo:
            nextLocation = getRequestLocation(requests[i], i in inPath)
            cost += currLocation.getDistance(nextLocation, distNorm)
            currLocation = nextLocation
            inPath.add(i)

        assert len(inPath) == len(requests)

        if cost < comboCostTuple[1]:
            comboCostTuple = [requests[i] for i in combo], cost

    return comboCostTuple
