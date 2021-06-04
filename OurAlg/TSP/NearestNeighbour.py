from OurAlg.TSP.Utils import getRequestLocation


def getPathNearestNeighbourRequestGroups(requestGroups, sourceLocation, distNorm="l2"):
    path = []
    cost = 0

    remainingRequestGroups = set(requestGroups)

    currLocation = sourceLocation

    while len(path) < len(requestGroups):
        distArray = [(getPathNearestNeighbourRequests(requestGroup, currLocation, distNorm), requestGroup)
                     for requestGroup in remainingRequestGroups]
        requestGroupWalk, requestGroup = min(distArray, key=lambda obj: obj[0][1])
        path.append(requestGroupWalk[0])
        cost += requestGroupWalk[1]

        currLocation = requestGroupWalk[0][-1].targetLocation

        remainingRequestGroups.remove(requestGroup)

    return path, cost


def getPathNearestNeighbourRequests(requests, sourceLocation, distNorm="l2"):
    path = []
    cost = 0
    inPath = set([])

    remainingRequests = set(requests)

    currLocation = sourceLocation

    while len(path) < 2 * len(requests):
        distArray = [(currLocation.getDistance(getRequestLocation(request, request in inPath), distNorm), request)
                     for request in remainingRequests]
        addCost, request = min(distArray, key=lambda obj: obj[0])
        path.append(request)
        cost += addCost

        currLocation = getRequestLocation(request, request in inPath)

        if request in inPath:
            remainingRequests.remove(request)
        else:
            inPath.add(request)

    return path, cost
