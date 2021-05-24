# TODO
# def getPathNearestNeighbourRequestGroups(requestGroups, sourceLocation, distNorm="l2"):
#     path = []
#
#
#     return path


def getPathNearestNeighbourRequests(requests, sourceLocation, distNorm="l2"):
    path = []
    cost = 0
    inPath = set([])

    remainingRequests = set(requests)

    currLocation = sourceLocation

    while len(path) < 2*len(requests):
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


def getRequestLocation(request, getTarget):

    return request.targetLocation if getTarget else request.sourceLocation
